"""Tests: the merge of an endogenous drug onto its own compound (graph/drug_entry_nodes.py, "The merge"; item 37
rulings draft, section 17 P1, section 18 P1.1, P1.2 and P7, section 19 P1.1a and P1.1b, section 22: "P1.1a happens
inside the merge step, so every endogenous drug is handled by one code path and the build stays reproducible").

A listed compound whose drug's own mechanism moves (configs/drugs_acting_as_graph_compounds.csv,
moves_mechanism_to_compound_edges; melatonin) is seeded on its compound by the evidence build, gets no drug node, and
at the merge the compound's own edges to its mechanism's targets take the mechanism's sign. Only listed compounds move,
a compound with no edge to a target is refused (P1.1b), and the compound's nodes keep their type (P1.2 and P7)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from experiments.build_drug_entry_node_variant import compound_mechanisms_of_graph, edge_rows_changed
from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data
from mechanistic_pathway_learning.graph.drug_entry_nodes import (
    DRUG_ENTRY_FILE,
    DRUG_MECHANISM_RELATION,
    DRUG_NODE_TYPE,
    MERGED_SIGN_EVIDENCE,
    add_drug_entry_nodes,
    drug_node_id,
)
from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import (
    EXOGENOUS_SUPPLY,
    GRAPH_COMPOUND_TARGET_PREFIX,
    ChemblCaches,
    DrugTarget,
    check_graph_compounds_have_no_mechanism,
    compound_mechanism_targets,
    graph_compound_targets,
    mechanisms_by_parent_and_molecule,
    read_compounds_moving_their_mechanism,
)
from tests.test_drug_entry_nodes import evidence_row, write_graph

RELATIONS = ["binds", "activates", "inhibits", "encodes", DRUG_MECHANISM_RELATION]
SMALL_MOLECULE = "OmniPath small_molecule_protein"
MEL, TRP = frozenset({"MEL"}), frozenset({"TRP"})
GRAPH_COMPOUNDS = [TRP, MEL]
AGONISM = {MEL: [("PROTEIN:R1", 1.0), ("PROTEIN:R2", 1.0)]}
SEEDS = {
    "CID_mel": ("melatonin", [("MELc", 1.0, 0.5), ("MELe", 1.0, 0.5)]),  # seeded on its compound, as the evidence build now seeds it
    "CID_trp": ("tryptophan", [("TRPc", 1.0, 1.0)]),  # a graph compound whose listing moves no mechanism
    "CID_ram": ("ramelteon", [("PROTEIN:R1", 1.0, 0.5), ("PROTEIN:R2", 1.0, 0.5)]),  # a drug with a node of its own on the same receptors
}


def toy_graph() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Two receptors, an enzyme and a binding partner as gene and protein nodes; melatonin in two compartments, with
    unsigned receptor edges from its extracellular node and a signed enzyme edge from its cytosolic one; tryptophan with
    an unsigned edge to the first receptor."""
    node_ids = ["GENE:R1", "GENE:R2", "GENE:E", "PROTEIN:R1", "PROTEIN:R2", "PROTEIN:E", "PROTEIN:X", "MELc", "MELe", "TRPc"]
    nodes = pd.DataFrame({
        "node_id": node_ids,
        "node_type": ["gene"] * 3 + ["protein"] * 4 + ["metabolite"] * 3,
        "display_name": node_ids,
        "compartment": [None] * 7 + ["c", "e", "c"],
        "base_metabolite_id": [None] * 7 + ["MEL", "MEL", "TRP"],
        "gene_symbol": ["R1", "R2", "E", "R1", "R2", "E", "X", None, None, None],
        "degree": [1, 1, 1, 4, 2, 2, 1, 1, 2, 1]})
    edges = pd.DataFrame({
        "source_id": ["GENE:R1", "GENE:R2", "GENE:E", "MELe", "MELe", "MELc", "TRPc", "PROTEIN:X"],
        "target_id": ["PROTEIN:R1", "PROTEIN:R2", "PROTEIN:E", "PROTEIN:R1", "PROTEIN:R2", "PROTEIN:E", "PROTEIN:R1", "PROTEIN:R1"],
        "relation_type": ["encodes", "encodes", "encodes", "binds", "binds", "inhibits", "binds", "binds"],
        "sign": [1.0, 1.0, 1.0, 0.0, 0.0, -1.0, 0.0, 0.0],
        "evidence_source": ["gene_protein_split"] * 3 + [SMALL_MOLECULE, SMALL_MOLECULE, "BRENDA toy", SMALL_MOLECULE, "OmniPath"]})
    return nodes, edges


def merged(seeds=None, compound_mechanisms=AGONISM):
    nodes, edges = toy_graph()
    return (nodes, edges, *add_drug_entry_nodes(nodes, edges, RELATIONS, SEEDS if seeds is None else seeds, GRAPH_COMPOUNDS,
                                                compound_mechanisms=compound_mechanisms))


def edge_of(edges: pd.DataFrame, source: str, target: str) -> pd.DataFrame:
    return edges[(edges.source_id == source) & (edges.target_id == target)]


def test_the_merge_signs_the_compound_s_receptor_edges_and_gives_the_drug_no_node() -> None:
    nodes, edges, new_nodes, new_edges, relations, entry_table, summary = merged()
    # the merged node: no drug node for melatonin, and its compound's nodes keep their type (P1.2 and P7: no drug flag)
    assert drug_node_id("CID_mel") not in set(new_nodes.node_id)
    assert list(new_nodes.node_id[len(nodes):]) == [drug_node_id("CID_ram")] and set(new_nodes.node_type[len(nodes):]) == {DRUG_NODE_TYPE}
    pd.testing.assert_frame_equal(new_nodes.iloc[: len(nodes)].reset_index(drop=True), nodes)  # node types and degrees as they were
    assert dict(zip(new_nodes.node_id, new_nodes.node_type))["MELe"] == "metabolite"
    assert summary["drugs_attached_to_a_graph_compound"] == ["CID_mel", "CID_trp"]
    assert summary["drugs_whose_mechanism_moved_onto_their_compound"] == ["CID_mel"]
    # the receptor edges: the agonist sign under activates, the sourced evidence first and the merge's note after it
    for receptor in ("PROTEIN:R1", "PROTEIN:R2"):
        row = edge_of(new_edges, "MELe", receptor)
        assert list(zip(row.relation_type, row.sign)) == [("activates", 1.0)]
        assert row.evidence_source.iloc[0].startswith(SMALL_MOLECULE) and MERGED_SIGN_EVIDENCE in row.evidence_source.iloc[0] and "CID_mel" in row.evidence_source.iloc[0]
    # nothing else changed: the two rows, in relation, sign and evidence only
    assert edge_rows_changed(edges, new_edges) == ([3, 4], ["relation_type", "sign", "evidence_source"])
    assert sorted(record["edge_row"] for record in summary["compound_edges_signed_at_the_merge"]) == [3, 4]
    assert {(record["relation_before"], record["sign_before"]) for record in summary["compound_edges_signed_at_the_merge"]} == {("binds", 0.0)}
    assert summary["existing_rows_unchanged"] is False and summary["compound_edges_already_carrying_the_mechanism_sign"] == []
    assert relations == RELATIONS  # activates was already a relation; no carrier, so no sequesters
    # ramelteon is built as before: a node with its targets edges, and the entry table holds it alone
    assert sorted(zip(entry_table.perturbation_id, entry_table.target_node_id)) == [("CID_ram", "PROTEIN:R1"), ("CID_ram", "PROTEIN:R2")]
    added = new_edges.iloc[len(edges):]
    assert set(added.relation_type) == {DRUG_MECHANISM_RELATION} and set(added.source_id) == {drug_node_id("CID_ram")}


def test_only_listed_compounds_move() -> None:
    nodes, edges, _, unmerged_edges, _, _, summary = merged(compound_mechanisms=None)
    pd.testing.assert_frame_equal(unmerged_edges.iloc[: len(edges)].reset_index(drop=True), edges)  # the build it always was
    assert summary["existing_rows_unchanged"] is True and "compound_edges_signed_at_the_merge" not in summary
    assert summary["drugs_attached_to_a_graph_compound"] == ["CID_mel", "CID_trp"]  # still merged, but its receptor edges stay unsigned
    # tryptophan's own unsigned edge to the receptor and another protein's binds row are not touched by melatonin's merge
    _, _, _, new_edges, _, _, _ = merged()
    for source in ("TRPc", "PROTEIN:X"):
        assert list(zip(edge_of(new_edges, source, "PROTEIN:R1").relation_type, edge_of(new_edges, source, "PROTEIN:R1").sign)) == [("binds", 0.0)]
    # a moving compound that no perturbation attaches to signs nothing
    without_melatonin = {key: value for key, value in SEEDS.items() if key != "CID_mel"}
    _, edges, _, new_edges, _, _, summary = merged(seeds=without_melatonin)
    pd.testing.assert_frame_equal(new_edges.iloc[: len(edges)].reset_index(drop=True), edges)
    assert "drugs_whose_mechanism_moved_onto_their_compound" not in summary
    # melatonin seeded on its receptors, as an evidence table built before its listing moved it, keeps a drug node
    on_receptors = {"CID_mel": ("melatonin", [("PROTEIN:R1", 1.0, 0.5), ("PROTEIN:R2", 1.0, 0.5)])}
    _, edges, new_nodes, new_edges, _, _, summary = merged(seeds=on_receptors)
    assert drug_node_id("CID_mel") in set(new_nodes.node_id) and summary["drugs_attached_to_a_graph_compound"] == []
    pd.testing.assert_frame_equal(new_edges.iloc[: len(edges)].reset_index(drop=True), edges)


def test_an_antagonist_and_a_partial_agonist_move_their_own_signs_and_an_agreeing_signed_edge_is_kept() -> None:
    _, _, _, new_edges, _, _, _ = merged(compound_mechanisms={MEL: [("PROTEIN:R1", -1.0), ("PROTEIN:R2", 0.5)]})
    assert list(zip(edge_of(new_edges, "MELe", "PROTEIN:R1").relation_type, edge_of(new_edges, "MELe", "PROTEIN:R1").sign)) == [("inhibits", -1.0)]
    assert list(zip(edge_of(new_edges, "MELe", "PROTEIN:R2").relation_type, edge_of(new_edges, "MELe", "PROTEIN:R2").sign)) == [("activates", 0.5)]
    _, edges, _, new_edges, _, _, summary = merged(compound_mechanisms={MEL: [("PROTEIN:E", -1.0)]})  # the inhibits row already points that way
    pd.testing.assert_frame_equal(new_edges.iloc[: len(edges)].reset_index(drop=True), edges)
    assert summary["existing_rows_unchanged"] is True and summary["compound_edges_signed_at_the_merge"] == []
    assert [(record["source_id"], record["target_id"]) for record in summary["compound_edges_already_carrying_the_mechanism_sign"]] == [("MELc", "PROTEIN:E")]


def test_the_merge_refuses_what_it_would_lose_or_contradict() -> None:
    with pytest.raises(ValueError, match="P1.1b"):  # brexanolone's and oxybate's case: no receptor edge on the compound
        merged(seeds={"CID_trp": SEEDS["CID_trp"]}, compound_mechanisms={TRP: [("PROTEIN:R2", 1.0)]})
    with pytest.raises(ValueError, match="P1.1b"):  # one target of two without an edge loses part of the mechanism
        merged(compound_mechanisms={MEL: [("PROTEIN:R1", 1.0), ("PROTEIN:X", 1.0)]})
    with pytest.raises(ValueError, match="disagrees"):  # the compound's sourced inhibition against an agonist mechanism
        merged(compound_mechanisms={MEL: [("PROTEIN:E", 1.0)]})
    with pytest.raises(ValueError, match="no direction"):
        merged(compound_mechanisms={MEL: [("PROTEIN:R1", 0.0)]})
    with pytest.raises(ValueError, match="not graph compounds"):
        merged(compound_mechanisms={frozenset({"OTHER"}): [("PROTEIN:R1", 1.0)]})
    nodes, edges = toy_graph()
    with pytest.raises(ValueError, match="no activates relation"):
        add_drug_entry_nodes(nodes, edges, [relation for relation in RELATIONS if relation != "activates"], SEEDS, GRAPH_COMPOUNDS, compound_mechanisms=AGONISM)
    duplicated = pd.concat([edges, edges.iloc[[3]].assign(relation_type="activates", sign=1.0)], ignore_index=True)  # a signed copy beside the binds row
    with pytest.raises(ValueError, match="two edges of one relation"):
        add_drug_entry_nodes(nodes, duplicated, RELATIONS, SEEDS, GRAPH_COMPOUNDS, compound_mechanisms=AGONISM)


def test_both_arms_of_the_ablation_read_the_signed_edges(tmp_path: Path) -> None:
    """The ablation arm (drug_entry "targets") drops the entry nodes but keeps the compound edges the merge signed, since
    it too seeds melatonin on its compound; against the source graph it differs in those two edges only."""
    nodes, edges, new_nodes, new_edges, relations, entry_table, _ = merged()
    write_graph(tmp_path / "source", nodes, edges, RELATIONS)
    write_graph(tmp_path / "drugs", new_nodes, new_edges, relations, entry_table)
    assert (tmp_path / "drugs" / DRUG_ENTRY_FILE).exists()
    evidence_directory = tmp_path / "evidence"
    evidence_directory.mkdir()
    rows = [evidence_row(perturbation, "drug", perturbation, [list(triple) for triple in triples]) for perturbation, (_, triples) in SEEDS.items()]
    rows.append(evidence_row("knockout_R1", "gene", "cluster:R1", [["GENE:R1", -1.0, 1.0]]))
    pd.DataFrame(rows).to_parquet(evidence_directory / "evidence_records.parquet", index=False)
    source = load_experiment_data(tmp_path / "source", evidence_directory)
    arms = {mode: load_experiment_data(tmp_path / "drugs", evidence_directory, drug_entry=mode) for mode in ("targets", "nodes")}
    for mode, data in arms.items():
        pairs = {(data.node_ids[source_index], data.node_ids[target_index]): (data.relation_types[relation], sign)
                 for source_index, target_index, relation, sign in zip(data.edge_source, data.edge_target, data.edge_relation, data.edge_sign)}
        assert pairs[("MELe", "PROTEIN:R1")] == ("activates", 1.0) and pairs[("MELe", "PROTEIN:R2")] == ("activates", 1.0), mode
        seeds = dict(zip(data.perturbation_ids, ([data.node_ids[index] for index in indices] for indices in data.perturbation_seeds)))
        assert seeds["CID_mel"] == ["MELc", "MELe"], mode  # the endogenous drug enters on its compound in both arms
    targets_arm = arms["targets"]
    assert targets_arm.node_ids == source.node_ids
    np.testing.assert_array_equal(targets_arm.edge_source, source.edge_source)
    differs = (np.asarray(targets_arm.edge_relation) != np.asarray(source.edge_relation)) | (np.asarray(targets_arm.edge_sign) != np.asarray(source.edge_sign))
    assert sorted((source.node_ids[source.edge_source[index]], source.node_ids[source.edge_target[index]]) for index in np.flatnonzero(differs)) == [
        ("MELe", "PROTEIN:R1"), ("MELe", "PROTEIN:R2")]


def test_the_variant_build_places_a_moving_mechanism_as_the_drug_s_seeds_were_placed() -> None:
    nodes, _ = toy_graph()
    protein_of_gene = {"GENE:R1": ["PROTEIN:R1"], "GENE:R2": ["PROTEIN:R2"], "GENE:E": ["PROTEIN:E"]}
    mechanisms = mechanisms_by_parent_and_molecule([
        {"molecule_chembl_id": "CHEMBL_MEL", "parent_molecule_chembl_id": "CHEMBL_MEL", "target_chembl_id": "CHEMBL_FAMILY", "action_type": "AGONIST", "mec_id": 1}])
    targets = {"CHEMBL_FAMILY": {"organism": "Homo sapiens", "gene_symbols": ["R1", "R2"], "target_type": "PROTEIN FAMILY", "pref_name": "toy receptors"}}
    caches = ChemblCaches({}, mechanisms, targets, action_resolutions={})
    assert compound_mechanisms_of_graph({MEL: ["CHEMBL_MEL"]}, caches, nodes, protein_of_gene) == AGONISM
    assert compound_mechanisms_of_graph({MEL: ["CHEMBL_MEL"]}, caches, nodes, {}) == {MEL: [("GENE:R1", 1.0), ("GENE:R2", 1.0)]}  # a merged graph
    with pytest.raises(ValueError, match="has a mechanism target"):
        compound_mechanisms_of_graph({MEL: ["CHEMBL_NONE"]}, caches, nodes, protein_of_gene)
    elsewhere = ChemblCaches({}, mechanisms, {"CHEMBL_FAMILY": targets["CHEMBL_FAMILY"] | {"gene_symbols": ["ABSENT"]}}, action_resolutions={})
    with pytest.raises(ValueError, match="is a node of this graph"):
        compound_mechanisms_of_graph({MEL: ["CHEMBL_MEL"]}, elsewhere, nodes, protein_of_gene)
    # a target whose rows disagree on the action is withheld, and a withheld sign cannot move
    conflicting = mechanisms_by_parent_and_molecule([
        {"molecule_chembl_id": "CHEMBL_MEL", "parent_molecule_chembl_id": "CHEMBL_MEL", "target_chembl_id": "CHEMBL_FAMILY", "action_type": action, "mec_id": number}
        for number, action in ((1, "AGONIST"), (2, "PARTIAL AGONIST"))])
    with pytest.raises(ValueError, match="curate it first"):
        compound_mechanism_targets({MEL: ["CHEMBL_MEL"]}, ChemblCaches({}, conflicting, targets, action_resolutions={}))


def listing(tmp_path: Path, rows: list[dict], with_column: bool = True) -> Path:
    path = tmp_path / "drugs_acting_as_graph_compounds.csv"
    columns = ["drug_name", "pubchem_cid", "chembl_ids", "base_metabolite_ids"] + (["moves_mechanism_to_compound_edges"] if with_column else []) + ["note"]
    pd.DataFrame([{column: row.get(column, "") for column in columns} for row in rows], columns=columns).to_csv(path, index=False)
    return path


def test_the_listing_column_names_the_compounds_whose_mechanism_moves(tmp_path: Path) -> None:
    rows = [{"drug_name": "tryptophan", "chembl_ids": "CHEMBL_TRP", "base_metabolite_ids": "TRP", "moves_mechanism_to_compound_edges": "false"},
            {"drug_name": "melatonin", "chembl_ids": "CHEMBL_MEL", "base_metabolite_ids": "MEL", "moves_mechanism_to_compound_edges": "true"},
            {"drug_name": "blank", "chembl_ids": "CHEMBL_BLANK", "base_metabolite_ids": "BLANK"}]
    assert read_compounds_moving_their_mechanism(listing(tmp_path, rows)) == {MEL: ["CHEMBL_MEL"]}
    assert read_compounds_moving_their_mechanism(listing(tmp_path, rows, with_column=False)) == {}  # a table written before the column moves none
    assert read_compounds_moving_their_mechanism(tmp_path / "absent.csv") == {}
    with pytest.raises(ValueError, match="expected true, false or blank"):
        read_compounds_moving_their_mechanism(listing(tmp_path, [rows[1] | {"moves_mechanism_to_compound_edges": "yes"}]))


def test_the_guard_admits_a_mechanism_only_where_the_listing_moves_it() -> None:
    by_chembl_id = {"CHEMBL_TRP": ["TRP"], "CHEMBL_MEL": ["MEL"]}
    mechanisms = mechanisms_by_parent_and_molecule([
        {"molecule_chembl_id": "CHEMBL_MEL", "parent_molecule_chembl_id": "CHEMBL_MEL", "target_chembl_id": "CHEMBL_FAMILY", "action_type": "AGONIST", "mec_id": 1}])
    check_graph_compounds_have_no_mechanism(by_chembl_id, mechanisms, exclusions=(), moving_compounds=[MEL])
    with pytest.raises(ValueError, match="carry a mechanism: \\['CHEMBL_MEL'\\]"):  # not moving: the rule for a graph compound with a mechanism holds
        check_graph_compounds_have_no_mechanism(by_chembl_id, mechanisms, exclusions=())
    with pytest.raises(ValueError, match="none of whose ChEMBL forms carries one"):  # a row that moves a mechanism no form carries
        check_graph_compounds_have_no_mechanism(by_chembl_id, mechanisms, exclusions=(), moving_compounds=[MEL, TRP])


def test_a_moving_drug_is_seeded_on_its_compound_in_place_of_its_chembl_targets() -> None:
    agonism = [DrugTarget("CHEMBL_FAMILY", "AGONIST", ["R1", "R2"], "PROTEIN FAMILY")]
    by_chembl_id = {"CHEMBL_TRP": ["TRP"], "CHEMBL_MEL": ["MEL"]}
    seeded = graph_compound_targets(agonism, None, ["CHEMBL_MEL"], {}, by_chembl_id, moving_compounds=[MEL])
    assert [(target.target_chembl_id, target.action_type, target.sign) for target in seeded] == [(GRAPH_COMPOUND_TARGET_PREFIX + "MEL", EXOGENOUS_SUPPLY, 1.0)]
    assert graph_compound_targets(agonism, None, ["CHEMBL_MEL"], {}, by_chembl_id) == agonism  # not moving: its ChEMBL targets, as before
    assert graph_compound_targets(agonism, None, ["CHEMBL_OTHER"], {}, by_chembl_id, moving_compounds=[MEL]) == agonism  # not listed
    assert [target.target_chembl_id for target in graph_compound_targets([], None, ["CHEMBL_TRP"], {}, by_chembl_id, moving_compounds=[MEL])] == [
        GRAPH_COMPOUND_TARGET_PREFIX + "TRP"]  # a listed compound without a mechanism, as tryptophan and levodopa


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LISTING = REPOSITORY_ROOT / "configs" / "drugs_acting_as_graph_compounds.csv"
CHEMBL_DIRECTORY = REPOSITORY_ROOT / "data" / "raw" / "chembl"
SOURCE_GRAPH = REPOSITORY_ROOT / "data" / "processed" / "graph_full_neuronal_split_binders"  # the source graph of the v5 drug-entry variant
MELATONIN, LEVODOPA = "CID100000896", "RXCUI:6375"  # their perturbation ids (configs/centrally_acting_drugs.csv)
MELATONIN_COMPOUND = frozenset({"MAM02460"})
pinned_chembl = pytest.mark.skipif(not (CHEMBL_DIRECTORY / "mechanisms.json").exists() or not (CHEMBL_DIRECTORY / "targets.json").exists(),
                                   reason="the pinned ChEMBL caches are not present (experiments/fetch_chembl_drug_targets.py)")


@pinned_chembl
def test_on_the_pinned_cache_the_committed_listing_moves_melatonin_s_agonism_and_nothing_else() -> None:
    """Item 37 rulings draft, section 19, P1.1a: "Melatonin's compound-node receptor edges take the agonist sign before
    the merge"; the listing moves melatonin's one mechanism row and no other row's."""
    from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import (
        drug_targets_for_pubchem_cid, load_chembl_caches, load_drugs_acting_as_graph_compounds)

    moving = read_compounds_moving_their_mechanism(LISTING)
    assert moving == {MELATONIN_COMPOUND: ["CHEMBL45"]}
    caches = load_chembl_caches(CHEMBL_DIRECTORY)
    by_pubchem_cid, by_chembl_id = load_drugs_acting_as_graph_compounds(LISTING)
    assert by_chembl_id["CHEMBL45"] == ["MAM02460"] and 896 not in by_pubchem_cid
    check_graph_compounds_have_no_mechanism(by_chembl_id, caches.mechanisms_by_molecule, moving_compounds=moving)
    with pytest.raises(ValueError, match=r"carry a mechanism: \['CHEMBL45'\]"):  # without the column melatonin would be refused, and only melatonin
        check_graph_compounds_have_no_mechanism(by_chembl_id, caches.mechanisms_by_molecule)
    moved = compound_mechanism_targets(moving, caches)
    assert [(target.target_chembl_id, target.action_type, sorted(target.gene_symbols), target.sign) for target in moved[MELATONIN_COMPOUND]] == [
        ("CHEMBL2094268", "AGONIST", ["MTNR1A", "MTNR1B"], 1.0)]
    # the SIDER route (CID 896, which the pinned map gives as CHEMBL45) and the OnSIDES route (the parent alone) both seed the compound
    found = drug_targets_for_pubchem_cid(896, caches)
    assert [target.target_chembl_id for target in found] == ["CHEMBL2094268"]
    for pubchem_cid, chembl_ids in ((896, caches.pubchem_to_chembl["896"]), (None, ["CHEMBL45"])):
        seeded = graph_compound_targets(found, pubchem_cid, chembl_ids, by_pubchem_cid, by_chembl_id, moving)
        assert [(target.target_chembl_id, target.action_type) for target in seeded] == [(GRAPH_COMPOUND_TARGET_PREFIX + "MAM02460", EXOGENOUS_SUPPLY)]


@pinned_chembl
def test_on_the_pinned_cache_levodopa_stays_the_plain_graph_compound_of_daeff3b6() -> None:
    """Levodopa's case (item 37 rulings draft, section 16, item 28) is unchanged by the moving column: its DRD3 row is
    removed, not moved, and it is seeded on MAM02354 through the graph-compound fallback as before."""
    from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import (
        load_chembl_caches, load_drugs_acting_as_graph_compounds, mechanism_targets)

    moving = read_compounds_moving_their_mechanism(LISTING)
    assert frozenset({"MAM02354"}) not in moving and frozenset({"MAM03089"}) not in moving
    caches = load_chembl_caches(CHEMBL_DIRECTORY)
    by_pubchem_cid, by_chembl_id = load_drugs_acting_as_graph_compounds(LISTING)
    kept = mechanism_targets(["CHEMBL1009"], caches.mechanisms_by_molecule, caches.targets)
    assert kept == []
    seeded = graph_compound_targets(kept, None, ["CHEMBL1009"], by_pubchem_cid, by_chembl_id, moving)
    assert [(target.target_chembl_id, target.sign) for target in seeded] == [(GRAPH_COMPOUND_TARGET_PREFIX + "MAM02354", 1.0)]
    with pytest.raises(ValueError, match="CHEMBL1009"):  # with the removal undone the guard still refuses levodopa: its row moves nothing
        check_graph_compounds_have_no_mechanism(by_chembl_id, caches.mechanisms_by_molecule, exclusions=(), moving_compounds=moving)


@pinned_chembl
@pytest.mark.skipif(not (SOURCE_GRAPH / "edges.parquet").exists(), reason="the v5 source graph is not built (scripts/rebuild_data_layer.sh)")
def test_on_the_v5_source_graph_the_merge_signs_melatonin_s_two_receptor_edges_and_no_other_row() -> None:
    """On graph_full_neuronal_split_binders (the source of graph_full_neuronal_split_binders_drugs_v5, files of the v5
    build): MAM02460e binds PROTEIN:MTNR1A and PROTEIN:MTNR1B at sign 0 (OmniPath small_molecule_protein); the merge
    makes both activates at the agonist's +1, and levodopa, merged in the same build, changes nothing."""
    from experiments.build_drug_entry_node_variant import graph_compound_base_ids
    from mechanistic_pathway_learning.evaluation.experiment_data import read_protein_of_gene
    from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import load_chembl_caches

    nodes, edges = pd.read_parquet(SOURCE_GRAPH / "nodes.parquet"), pd.read_parquet(SOURCE_GRAPH / "edges.parquet")
    relation_types = json.loads((SOURCE_GRAPH / "relation_types.json").read_text())
    mechanisms = compound_mechanisms_of_graph(read_compounds_moving_their_mechanism(LISTING), load_chembl_caches(CHEMBL_DIRECTORY), nodes,
                                              read_protein_of_gene(SOURCE_GRAPH))
    assert mechanisms == {MELATONIN_COMPOUND: [("PROTEIN:MTNR1A", 1.0), ("PROTEIN:MTNR1B", 1.0)]}
    compound_nodes = {base: sorted(nodes.node_id[nodes.base_metabolite_id == base]) for base in ("MAM02460", "MAM02354")}
    assert compound_nodes["MAM02460"] == ["MAM02460c", "MAM02460e"]
    seeds = {MELATONIN: ("melatonin", [(node, 1.0, 0.5) for node in compound_nodes["MAM02460"]]),
             LEVODOPA: ("levodopa", [(node, 1.0, 1.0 / len(compound_nodes["MAM02354"])) for node in compound_nodes["MAM02354"]])}
    new_nodes, new_edges, new_relations, entry_table, summary = add_drug_entry_nodes(
        nodes, edges, relation_types, seeds, graph_compound_base_ids(LISTING), compound_mechanisms=mechanisms)
    assert len(new_nodes) == len(nodes) and len(new_edges) == len(edges) and new_relations == relation_types and entry_table.empty
    assert summary["drugs_attached_to_a_graph_compound"] == sorted([MELATONIN, LEVODOPA]) and summary["drugs_whose_mechanism_moved_onto_their_compound"] == [MELATONIN]
    rows, columns = edge_rows_changed(edges, new_edges)
    assert columns == ["relation_type", "sign", "evidence_source"]
    changed = new_edges.iloc[rows]
    assert sorted(zip(changed.source_id, changed.target_id, changed.relation_type, changed.sign)) == [
        ("MAM02460e", "PROTEIN:MTNR1A", "activates", 1.0), ("MAM02460e", "PROTEIN:MTNR1B", "activates", 1.0)]
    before = edges.iloc[rows]
    assert set(zip(before.relation_type, before.sign, before.evidence_source)) == {("binds", 0.0, SMALL_MOLECULE)}
    assert sorted(record["edge_row"] for record in summary["compound_edges_signed_at_the_merge"]) == rows
