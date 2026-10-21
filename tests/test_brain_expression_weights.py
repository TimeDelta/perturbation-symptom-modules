"""Tests for the per-node cell-class weights of the cell-class propagation channels."""
import numpy as np
import pandas as pd

import pytest

from mechanistic_pathway_learning.graph.brain_expression_weights import (ALL_CELLS_CLASS, complex_limiting_member_expression,
                                                                         extracellular_pool_nodes, node_cell_class_weights,
                                                                         relative_expression_weights)


def test_relative_weight_is_expression_over_the_top_class_plus_the_detection_threshold():
    table = pd.DataFrame({"neuron": [388.0, 2.0, 112.0], "glia": [6.0, 2.0, 5606.0]}, index=["TH", "FLAT", "MBP"])
    weights = relative_expression_weights(table)
    assert np.isclose(weights.loc["TH", "neuron"], 388 / 389)
    assert np.isclose(weights.loc["FLAT", "glia"], 2 / 3)
    assert weights.loc["MBP", "neuron"] < 0.03


def test_nodes_without_expression_get_one_and_reactions_follow_their_rule():
    nodes = pd.DataFrame({
        "node_id": ["g1", "g2", "r1", "r2", "m1", "m2"],
        "node_type": ["gene", "gene", "reaction", "reaction", "metabolite", "metabolite"],
        "ensembl_gene_id": ["E1", "E9", None, None, None, None],
        "gene_symbol": ["A", "Z", None, None, None, None],
        "gene_reaction_rule": [None, None, "E1 and E2", "", None, None],
        "compartment": [None, None, None, None, "c", "e"],
    })
    expression = pd.DataFrame({"neuron": [10.0, 1.0], "glia": [0.0, 9.0]}, index=pd.Index(["E1", "E2"], name="ensembl_gene_id"))
    weights = node_cell_class_weights(nodes, expression)
    assert np.isclose(weights.loc["g1", "neuron"], 10 / 11) and weights.loc["g1", "glia"] == 0.0
    assert (weights.loc["g2"] == 1.0).all()  # not in the table
    assert np.isclose(weights.loc["r1", "neuron"], 1 / 2) and weights.loc["r1", "glia"] == 0.0  # min(10, 1) = 1 and min(0, 9) = 0
    assert (weights.loc[["r2", "m1", "m2"]] == 1.0).all().all()  # no rule, metabolites
    assert (weights[ALL_CELLS_CLASS] == 1.0).all()
    assert extracellular_pool_nodes(nodes).tolist() == [False, False, False, False, False, True]


# --- Decision 4.2: a protein complex takes its limiting member's expression, per class ---

def complex_fixture() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Two subunits with opposite class specificities, a complex of them, and a complex with no expressed member."""
    nodes = pd.DataFrame({
        "node_id": ["gene:ABUNDANT", "gene:SCARCE", "gene:UNKNOWN", "complex:BOTH", "complex:UNKNOWN_ONLY",
                    "reaction:DOWNSTREAM"],
        "node_type": ["gene", "gene", "gene", "protein_entity", "protein_entity", "reaction"],
        "ensembl_gene_id": ["ABUNDANT", "SCARCE", None, None, None, None],
        "gene_symbol": ["ABUNDANT", "SCARCE", "UNKNOWN", None, None, None],
        "gene_reaction_rule": [None, None, None, None, None, ""],
    })
    edges = pd.DataFrame({
        "source_id": ["gene:ABUNDANT", "gene:SCARCE", "gene:UNKNOWN", "complex:BOTH"],
        "target_id": ["complex:BOTH", "complex:BOTH", "complex:UNKNOWN_ONLY", "reaction:DOWNSTREAM"],
        "relation_type": ["member_of", "member_of", "member_of", "catalyzed_by"],
    })
    class_expression = pd.DataFrame({"neuron": [1000.0, 10.0], "astrocyte": [10.0, 1000.0]},
                                    index=pd.Index(["ABUNDANT", "SCARCE"], name="ensembl_gene_id"))
    return nodes, edges, class_expression


def test_a_complex_takes_the_minimum_raw_expression_of_its_members_per_class():
    nodes, edges, class_expression = complex_fixture()
    limiting = complex_limiting_member_expression(nodes, edges, class_expression)
    assert list(limiting.index) == ["complex:BOTH"], "a complex with no expressed member must be absent, not zero"
    assert limiting.loc["complex:BOTH", "neuron"] == pytest.approx(10.0)
    assert limiting.loc["complex:BOTH", "astrocyte"] == pytest.approx(10.0)


def test_the_limiting_member_is_chosen_within_each_class_and_can_differ_between_them():
    """"per type": the scarce subunit in the neuron column is not the scarce one in the astrocyte column."""
    nodes, edges, class_expression = complex_fixture()
    limiting = complex_limiting_member_expression(nodes, edges, class_expression)
    assert limiting.loc["complex:BOTH", "neuron"] == class_expression.loc["SCARCE", "neuron"]
    assert limiting.loc["complex:BOTH", "astrocyte"] == class_expression.loc["ABUNDANT", "astrocyte"]


def test_the_minimum_is_on_raw_expression_and_not_on_the_members_relative_weights():
    """The registered order. Taking it the other way round drives a complex of differently specific subunits
    towards zero in every class, which is what docs/complex_limiting_member_weight.md measures."""
    nodes, edges, class_expression = complex_fixture()
    registered = relative_expression_weights(
        complex_limiting_member_expression(nodes, edges, class_expression))
    member_weights = relative_expression_weights(class_expression)
    the_other_order = member_weights.min(axis=0)
    assert registered.loc["complex:BOTH"].max() == pytest.approx(10.0 / 11.0)
    assert the_other_order.max() < 0.02
    assert registered.loc["complex:BOTH"].max() > 20 * the_other_order.max()


def test_a_complex_with_no_expressed_member_keeps_weight_one_in_every_class():
    nodes, edges, class_expression = complex_fixture()
    weights = node_cell_class_weights(nodes, class_expression, member_edges=edges)
    assert (weights.loc["complex:UNKNOWN_ONLY", ["neuron", "astrocyte"]] == 1.0).all()


def test_omitting_the_member_edges_leaves_every_complex_flat():
    """The behaviour before decision 4.2, kept available so the change can be measured against it."""
    nodes, edges, class_expression = complex_fixture()
    without = node_cell_class_weights(nodes, class_expression)
    with_members = node_cell_class_weights(nodes, class_expression, member_edges=edges)
    assert (without.loc["complex:BOTH", ["neuron", "astrocyte"]] == 1.0).all()
    assert (with_members.loc["complex:BOTH", ["neuron", "astrocyte"]] < 1.0).all()
    for gene in ("gene:ABUNDANT", "gene:SCARCE", "gene:UNKNOWN"):
        assert without.loc[gene].equals(with_members.loc[gene]), "gene weights must not move"


# --- Decision 4.2b: the rewiring control recomputes the complex gate from the rewired membership ---

def test_the_rewired_gate_follows_the_rewired_membership():
    """The point of 4.2b: a complex's gate must come from whichever genes the rewired graph says belong to it."""
    from mechanistic_pathway_learning.graph.rewired_expression_features import rewired_complex_cell_class_weights
    nodes, edges, class_expression = complex_fixture()
    node_index = {node_id: position for position, node_id in enumerate(nodes.node_id)}
    # the real membership: ABUNDANT and SCARCE both in complex:BOTH
    real = np.array([[node_index["gene:ABUNDANT"], node_index["gene:SCARCE"]],
                     [node_index["complex:BOTH"], node_index["complex:BOTH"]]])
    # a rewiring that moves SCARCE out, leaving the complex with the abundant subunit only
    rewired = np.array([[node_index["gene:ABUNDANT"], node_index["gene:SCARCE"]],
                        [node_index["complex:BOTH"], node_index["complex:UNKNOWN_ONLY"]]])
    membership = np.array([True, True])
    before, _ = rewired_complex_cell_class_weights(nodes, real, membership, class_expression,
                                                   include_all_cells_class=False)
    after, counts = rewired_complex_cell_class_weights(nodes, rewired, membership, class_expression,
                                                       include_all_cells_class=False)
    assert before.loc["complex:BOTH", "neuron"] == pytest.approx(10.0 / 11.0), "min of the two subunits"
    assert after.loc["complex:BOTH", "neuron"] == pytest.approx(1000.0 / 1001.0), "the abundant subunit alone"
    assert counts["member_of_edges_rewired"] == 2


def test_every_complex_gets_a_row_so_a_real_gate_cannot_survive_the_rewiring():
    """A complex whose rewired members carry no expression must fall back to 1, not keep its real gate."""
    from mechanistic_pathway_learning.graph.rewired_expression_features import rewired_complex_cell_class_weights
    nodes, edges, class_expression = complex_fixture()
    node_index = {node_id: position for position, node_id in enumerate(nodes.node_id)}
    # the rewiring gives complex:BOTH only the gene with no expression
    rewired = np.array([[node_index["gene:UNKNOWN"]], [node_index["complex:BOTH"]]])
    weights, counts = rewired_complex_cell_class_weights(nodes, rewired, np.array([True]), class_expression,
                                                         include_all_cells_class=False)
    assert set(weights.index) == {"complex:BOTH", "complex:UNKNOWN_ONLY"}, "every complex needs a row"
    assert (weights.loc["complex:BOTH"] == 1.0).all()
    assert counts["complexes_with_a_rewired_gate"] == 0
    assert counts["complexes_left_flat_by_the_rewiring"] == 2


def test_the_rewired_gate_carries_the_all_cells_column_when_the_stored_table_does():
    from mechanistic_pathway_learning.graph.rewired_expression_features import rewired_complex_cell_class_weights
    nodes, edges, class_expression = complex_fixture()
    node_index = {node_id: position for position, node_id in enumerate(nodes.node_id)}
    rewired = np.array([[node_index["gene:ABUNDANT"]], [node_index["complex:BOTH"]]])
    weights, _ = rewired_complex_cell_class_weights(nodes, rewired, np.array([True]), class_expression,
                                                     include_all_cells_class=True)
    assert ALL_CELLS_CLASS in weights.columns
    assert (weights[ALL_CELLS_CLASS] == 1.0).all()


# --- Decision 9.76: peripheral endocrine classes beside the brain classes ---

import gzip  # noqa: E402
from pathlib import Path  # noqa: E402

from mechanistic_pathway_learning.graph.peripheral_cell_classes import (  # noqa: E402
    GEO_PINEAL_ANNOTATION_FILE, GEO_PINEAL_COUNTS_FILE, GEO_PINEAL_SAMPLES, add_peripheral_classes, geo_pineal_profile, gtex_profiles,
    hpa_brain_pseudobulk, peripheral_class_table, scaled_to_ncpm)


def write_peripheral_sources(directory: Path) -> tuple[Path, Path]:
    """A GTEx GCT with two brain tissues and the three peripheral tissues, and a GEO directory with raw counts and an
    annotation table. The GTEx brain columns sit at twice the HPA pseudobulk, so its scale factor is 2; the pineal counts
    are laid out so that each gene's mean CPM is twice the HPA pseudobulk too, except G4 (pineal-specific) and G1 (silent)."""
    genes = [f"G{index}" for index in range(1, 13)]
    gtex_header = ["Name", "Description", "Brain_Cortex", "Brain_Hypothalamus", "Thyroid", "Pancreas_Islets", "Pituitary", "Liver"]
    gtex_rows = [[f"ENSG{index:011d}.1", gene, str(20.0 * index), str(20.0 * index), "0" if gene != "G1" else "600", "0" if gene != "G2" else "40",
                  "0" if gene != "G3" else "8", "5"] for index, gene in enumerate(genes, start=1)]
    gct = directory / "gtex.gct"
    gct.write_text("#1.2\n12\t6\n" + "\n".join("\t".join(row) for row in [gtex_header, *gtex_rows]) + "\n")
    geo = directory / "GSE100472"
    geo.mkdir()
    # GeneIDs 1..11 map to G1..G11 (G12 has no Ensembl id and is dropped); GeneID 99 shares G4's Ensembl id with smaller counts
    count_rows = [["GeneID", *GEO_PINEAL_SAMPLES]]
    for index in range(1, 13):
        value = 0 if index == 1 else (3000 if index == 4 else 20 * index)
        count_rows.append([str(index), *[str(value)] * 6])
    count_rows.append(["99", *["1"] * 6])
    with gzip.open(geo / GEO_PINEAL_COUNTS_FILE, "wt") as handle:
        handle.write("\n".join("\t".join(row) for row in count_rows) + "\n")
    annotation_rows = [["GeneID", "Symbol", "GeneType", "EnsemblGeneID"]]
    for index in range(1, 13):
        annotation_rows.append([str(index), genes[index - 1], "protein-coding", f"ENSG{index:011d}" if index != 12 else ""])
    annotation_rows.append(["99", "G4-copy", "protein-coding", "ENSG00000000004"])
    with gzip.open(geo / GEO_PINEAL_ANNOTATION_FILE, "wt") as handle:
        handle.write("\n".join("\t".join(row) for row in annotation_rows) + "\n")
    return gct, geo


def hpa_table() -> pd.DataFrame:
    index = pd.Index([f"ENSG{index:011d}" for index in range(1, 13)], name="ensembl_gene_id")
    values = [10.0 * index for index in range(1, 13)]
    return pd.DataFrame({"class_neuron": values, "class_glia": values}, index=index)


def test_the_gtex_tissues_are_read_per_class(tmp_path: Path):
    gct, _ = write_peripheral_sources(tmp_path)
    gtex, gtex_brain = gtex_profiles(gct)
    assert list(gtex.columns) == ["thyroid", "pancreatic_islet", "pituitary"] and gtex.loc["ENSG00000000001", "thyroid"] == 600.0
    assert gtex_brain.loc["ENSG00000000002"] == 40.0, "the mean over the Brain_ tissues, the liver left out"


def test_the_geo_pineal_profile_is_mean_cpm_keyed_by_ensembl_id(tmp_path: Path):
    _, geo = write_peripheral_sources(tmp_path)
    profile = geo_pineal_profile(geo)
    column_sum = sum(20 * index for index in range(2, 13)) - 80 + 3000 + 1  # G1 at 0, G4 at 3000 instead of 80, G12 counted though dropped, GeneID 99 at 1
    assert list(profile.columns) == ["pineal"] and profile.loc["ENSG00000000004", "pineal"] == pytest.approx(3000 / column_sum * 1e6)
    assert profile.loc["ENSG00000000001", "pineal"] == 0.0, "a silent gene is 0, not missing"
    assert "ENSG00000000012" not in profile.index, "a GeneID without an Ensembl id is dropped"
    assert len(profile) == 11, "two GeneIDs sharing an Ensembl id give one row, the larger"
    with pytest.raises(ValueError, match="GSM2684714"):
        with gzip.open(geo / GEO_PINEAL_COUNTS_FILE, "wt") as handle:
            handle.write("GeneID\tOTHER\n1\t5\n")
        geo_pineal_profile(geo)


def test_a_source_is_placed_on_the_ncpm_scale_by_its_own_brain_samples(tmp_path: Path):
    gct, _ = write_peripheral_sources(tmp_path)
    gtex, gtex_brain = gtex_profiles(gct)
    scaled, factor = scaled_to_ncpm(gtex, gtex_brain, hpa_brain_pseudobulk(hpa_table()))
    assert np.isclose(factor, 2.0), "the source's brain profile is twice the HPA pseudobulk on every gene"
    assert np.isclose(scaled.loc["ENSG00000000001", "thyroid"], 300.0)


def test_the_peripheral_classes_join_the_brain_table_over_its_own_genes(tmp_path: Path):
    gct, geo = write_peripheral_sources(tmp_path)
    table, summary = add_peripheral_classes(hpa_table(), gct, geo)
    assert list(table.columns) == ["class_neuron", "class_glia", "class_thyroid", "class_pancreatic_islet", "class_pituitary", "class_pineal"]
    assert len(table) == 12, "a gene the brain table lacks is not added"
    assert np.isnan(table.loc["ENSG00000000012", "class_pineal"]), "G12 is unknown to the pineal source"
    assert table.loc["ENSG00000000004", "class_pineal"] > table.loc["ENSG00000000004", "class_neuron"]
    assert summary["classes"] == ["thyroid", "pancreatic_islet", "pituitary", "pineal"] and np.isclose(summary["scale_factor_source_units_per_ncpm"]["gtex"], 2.0)
    assert summary["scale_factor_source_units_per_ncpm"]["geo_pineal"] > 0, "estimated from the pineal profile itself: the series has no brain sample"
    without_pineal, summary_without = add_peripheral_classes(hpa_table(), gct, tmp_path / "absent")
    assert "class_pineal" not in without_pineal.columns and summary_without["geo_pineal"] is None
    assert peripheral_class_table(hpa_table(), None, None)[0].empty


def test_a_tissue_specific_factor_weighs_near_one_in_its_organ_and_zero_in_the_brain(tmp_path: Path):
    gct, geo = write_peripheral_sources(tmp_path)
    brain = hpa_table()
    brain.loc["ENSG00000000001", ["class_neuron", "class_glia"]] = 0.0  # G1: silent in the brain and the pineal, 600 TPM in the thyroid
    table, _ = add_peripheral_classes(brain, gct, geo)
    table.columns = [column.removeprefix("class_") for column in table.columns]
    weights = relative_expression_weights(table)
    assert weights.loc["ENSG00000000001", "thyroid"] > 0.99 and weights.loc["ENSG00000000001", "neuron"] == 0.0 and weights.loc["ENSG00000000001", "pineal"] == 0.0
    assert weights.loc["ENSG00000000004", "pineal"] > 0.9 and weights.loc["ENSG00000000004", "thyroid"] == 0.0
    nodes = pd.DataFrame({"node_id": ["GENE:G1", "GENE:G12"], "node_type": ["gene", "gene"], "ensembl_gene_id": ["ENSG00000000001", "ENSG00000000012"],
                          "gene_symbol": ["G1", "G12"], "gene_reaction_rule": [None, None], "compartment": [None, None]})
    node_weights = node_cell_class_weights(nodes, table)
    assert node_weights.loc["GENE:G12", "pineal"] == 1.0, "unknown to the pineal source: nothing is known, so nothing is blocked"
    assert node_weights.loc["GENE:G1", "thyroid"] > 0.99 and node_weights.loc["GENE:G1", "pineal"] == 0.0


# --- Decision 9.76 (21 October 2026): a class from one cluster of the adult human brain atlas ---

def write_cluster_aggregate(path: Path) -> None:
    """A loom-shaped HDF5 file: mean UMI per nucleus for six genes in three clusters (ids 10, 398 and 399), with the
    attributes the reader uses; G5 appears twice (two accessions of one gene) and G6 is absent from the HPA table."""
    import h5py

    genes = ["G1", "G2", "G3", "G4", "G5", "G5", "G6"]
    accessions = ["ENSG00000000001.5", "ENSG00000000002.1", "ENSG00000000003.2", "ENSG00000000004.9", "ENSG00000000005.1", "ENSG00000000005.2", "ENSG00000000099.1"]
    matrix = np.array([[10.0, 1.0, 1.0], [20.0, 2.0, 2.0], [30.0, 3.0, 3.0], [0.0, 40.0, 4.0], [1.0, 2.0, 5.0], [0.5, 1.0, 6.0], [1.0, 1.0, 7.0]])
    with h5py.File(path, "w") as handle:
        handle.create_dataset("matrix", data=matrix)
        handle.create_dataset("row_attrs/Gene", data=np.array(genes, dtype="S"))
        handle.create_dataset("row_attrs/Accession", data=np.array(accessions, dtype="S"))
        handle.create_dataset("col_attrs/Clusters", data=np.array([10, 398, 399]))
        handle.create_dataset("col_attrs/NCells", data=np.array([1000, 100, 300]))


def test_the_cluster_aggregate_is_read_as_pseudobulk_cpm_per_class(tmp_path: Path):
    from mechanistic_pathway_learning.graph.siletti_cluster_classes import add_atlas_cluster_classes, cluster_class_profiles, read_cluster_aggregate

    loom = tmp_path / "agg.loom"
    write_cluster_aggregate(loom)
    mean_umi, nuclei = read_cluster_aggregate(loom)
    assert list(mean_umi.columns) == [10, 398, 399] and nuclei.to_dict() == {10: 1000, 398: 100, 399: 300}
    assert mean_umi.loc["ENSG00000000005", 398] == 2.0, "a gene with two accessions keeps its largest row"
    profiles, nuclei_of_class = cluster_class_profiles(loom, {"noradrenergic_neuron": (398,), "pooled": (398, 399)})
    column_sum_398 = 1.0 + 2.0 + 3.0 + 40.0 + 2.0 + 1.0
    assert profiles.loc["ENSG00000000004", "noradrenergic_neuron"] == pytest.approx(40.0 / column_sum_398 * 1e6)
    pooled_g4 = (40.0 * 100 + 4.0 * 300) / 400  # the mean per nucleus weighted by nucleus count
    pooled_sum = sum((mean_umi.loc[gene, 398] * 100 + mean_umi.loc[gene, 399] * 300) / 400 for gene in mean_umi.index)
    assert profiles.loc["ENSG00000000004", "pooled"] == pytest.approx(pooled_g4 / pooled_sum * 1e6) and nuclei_of_class == {"noradrenergic_neuron": 100, "pooled": 400}
    with pytest.raises(ValueError, match="cluster 7"):
        cluster_class_profiles(loom, {"missing": (7,)})
    brain = pd.DataFrame({"class_neuron": [100.0, 200.0, 300.0, 1.0, 20.0], "class_glia": [100.0, 200.0, 300.0, 1.0, 20.0]},
                         index=pd.Index([f"ENSG{index:011d}" for index in range(1, 6)], name="ensembl_gene_id"))
    table, summary = add_atlas_cluster_classes(brain, loom)
    assert list(table.columns) == ["class_neuron", "class_glia", "class_noradrenergic_neuron"] and len(table) == 5, "joined over the brain table's genes; G6 is not added"
    assert summary["classes"] == ["noradrenergic_neuron"] and summary["nuclei"] == {"noradrenergic_neuron": 100} and summary["scale_factor_source_units_per_ncpm"]["noradrenergic_neuron"] > 0
    assert table["class_noradrenergic_neuron"].idxmax() == "ENSG00000000004", "the cluster's marker is the class's top gene"
    weights = relative_expression_weights(table.rename(columns=lambda column: column.removeprefix("class_")))
    assert weights.loc["ENSG00000000004", "noradrenergic_neuron"] > 0.95 and weights.loc["ENSG00000000004", "neuron"] < 0.01
    same, summary_without = add_atlas_cluster_classes(brain, tmp_path / "absent.loom")
    assert list(same.columns) == ["class_neuron", "class_glia"] and summary_without["siletti_aggregate"] is None and summary_without["classes"] == []


def test_the_scale_reference_is_the_brain_classes_whatever_the_table_already_carries(tmp_path: Path):
    """The reference must not drift as classes are joined on: a table with the peripheral and atlas classes gives the same
    pseudobulk as the HPA table alone."""
    gct, geo = write_peripheral_sources(tmp_path)
    brain = hpa_table()
    with_peripheral, _ = add_peripheral_classes(brain, gct, geo)
    with_peripheral["class_noradrenergic_neuron"] = 1e6
    assert hpa_brain_pseudobulk(with_peripheral, excluded_classes=("noradrenergic_neuron",)).equals(hpa_brain_pseudobulk(brain))
    assert not hpa_brain_pseudobulk(with_peripheral).equals(hpa_brain_pseudobulk(brain)), "an unnamed extra class would move it"
