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

from pathlib import Path  # noqa: E402

from mechanistic_pathway_learning.graph.peripheral_cell_classes import (  # noqa: E402
    EXPRESSION_ATLAS_ADULT_BRAIN_COLUMNS, add_peripheral_classes, expression_atlas_profiles, gtex_profiles, hpa_brain_pseudobulk,
    peripheral_class_table, scaled_to_ncpm)


def write_peripheral_sources(directory: Path) -> tuple[Path, Path]:
    """A GTEx GCT with two brain tissues and the three peripheral tissues, and an Expression Atlas table with the pineal and
    the adult brain columns. The brain columns of each source sit at twice the HPA pseudobulk, so the scale factor is 2."""
    genes = [f"G{index}" for index in range(1, 13)]
    gtex_header = ["Name", "Description", "Brain_Cortex", "Brain_Hypothalamus", "Thyroid", "Pancreas_Islets", "Pituitary", "Liver"]
    gtex_rows = [[f"ENSG{index:011d}.1", gene, str(20.0 * index), str(20.0 * index), "0" if gene != "G1" else "600", "0" if gene != "G2" else "40",
                  "0" if gene != "G3" else "8", "5"] for index, gene in enumerate(genes, start=1)]
    gct = directory / "gtex.gct"
    gct.write_text("#1.2\n12\t6\n" + "\n".join("\t".join(row) for row in [gtex_header, *gtex_rows]) + "\n")
    atlas_header = ["Gene ID", "Gene Name", "adult, pineal body", *EXPRESSION_ATLAS_ADULT_BRAIN_COLUMNS]
    atlas_rows = []
    for index, gene in enumerate(genes[:11], start=1):  # G12 is absent from the atlas
        pineal = "" if gene != "G4" else "300"  # a blank cell is 0
        atlas_rows.append([f"ENSG{index:011d}", gene, pineal, *[str(20.0 * index)] * len(EXPRESSION_ATLAS_ADULT_BRAIN_COLUMNS)])
    atlas = directory / "atlas.tsv"
    atlas.write_text("# Expression Atlas\n# Query: all\n" + "\n".join("\t".join(row) for row in [atlas_header, *atlas_rows]) + "\n")
    return gct, atlas


def hpa_table() -> pd.DataFrame:
    index = pd.Index([f"ENSG{index:011d}" for index in range(1, 13)], name="ensembl_gene_id")
    values = [10.0 * index for index in range(1, 13)]
    return pd.DataFrame({"class_neuron": values, "class_glia": values}, index=index)


def test_the_sources_are_read_per_class_and_a_blank_atlas_cell_is_zero(tmp_path: Path):
    gct, atlas = write_peripheral_sources(tmp_path)
    gtex, gtex_brain = gtex_profiles(gct)
    assert list(gtex.columns) == ["thyroid", "pancreatic_islet", "pituitary"] and gtex.loc["ENSG00000000001", "thyroid"] == 600.0
    assert gtex_brain.loc["ENSG00000000002"] == 40.0, "the mean over the Brain_ tissues, the liver left out"
    pineal, atlas_brain = expression_atlas_profiles(atlas)
    assert list(pineal.columns) == ["pineal"] and pineal.loc["ENSG00000000004", "pineal"] == 300.0 and pineal.loc["ENSG00000000001", "pineal"] == 0.0
    assert "ENSG00000000012" not in pineal.index and atlas_brain.loc["ENSG00000000003"] == 60.0


def test_a_source_is_placed_on_the_ncpm_scale_by_its_own_brain_samples(tmp_path: Path):
    gct, _ = write_peripheral_sources(tmp_path)
    gtex, gtex_brain = gtex_profiles(gct)
    scaled, factor = scaled_to_ncpm(gtex, gtex_brain, hpa_brain_pseudobulk(hpa_table()))
    assert np.isclose(factor, 2.0), "the source's brain profile is twice the HPA pseudobulk on every gene"
    assert np.isclose(scaled.loc["ENSG00000000001", "thyroid"], 300.0)


def test_the_peripheral_classes_join_the_brain_table_over_its_own_genes(tmp_path: Path):
    gct, atlas = write_peripheral_sources(tmp_path)
    table, summary = add_peripheral_classes(hpa_table(), gct, atlas)
    assert list(table.columns) == ["class_neuron", "class_glia", "class_thyroid", "class_pancreatic_islet", "class_pituitary", "class_pineal"]
    assert len(table) == 12, "a gene the brain table lacks is not added"
    assert np.isclose(table.loc["ENSG00000000004", "class_pineal"], 150.0) and np.isnan(table.loc["ENSG00000000012", "class_pineal"]), "G12 is unknown to the atlas"
    assert summary["classes"] == ["thyroid", "pancreatic_islet", "pituitary", "pineal"] and np.isclose(summary["scale_factor_source_units_per_ncpm"]["gtex"], 2.0)
    without_pineal, summary_without = add_peripheral_classes(hpa_table(), gct, tmp_path / "absent.tsv")
    assert "class_pineal" not in without_pineal.columns and summary_without["expression_atlas_fantom5"] is None
    assert peripheral_class_table(hpa_table(), None, None)[0].empty


def test_a_tissue_specific_factor_weighs_near_one_in_its_organ_and_zero_in_the_brain(tmp_path: Path):
    gct, atlas = write_peripheral_sources(tmp_path)
    brain = hpa_table()
    brain.loc["ENSG00000000001", ["class_neuron", "class_glia"]] = 0.0  # G1: silent in the brain, 600 TPM in the thyroid
    table, _ = add_peripheral_classes(brain, gct, atlas)
    table.columns = [column.removeprefix("class_") for column in table.columns]
    weights = relative_expression_weights(table)
    assert weights.loc["ENSG00000000001", "thyroid"] > 0.99 and weights.loc["ENSG00000000001", "neuron"] == 0.0
    assert weights.loc["ENSG00000000004", "pineal"] > 0.7 and weights.loc["ENSG00000000004", "thyroid"] == 0.0
    nodes = pd.DataFrame({"node_id": ["GENE:G1", "GENE:G12"], "node_type": ["gene", "gene"], "ensembl_gene_id": ["ENSG00000000001", "ENSG00000000012"],
                          "gene_symbol": ["G1", "G12"], "gene_reaction_rule": [None, None], "compartment": [None, None]})
    node_weights = node_cell_class_weights(nodes, table)
    assert node_weights.loc["GENE:G12", "pineal"] == 1.0, "unknown to the atlas: nothing is known, so nothing is blocked"
    assert node_weights.loc["GENE:G1", "thyroid"] > 0.99 and node_weights.loc["GENE:G1", "pineal"] == 0.0
