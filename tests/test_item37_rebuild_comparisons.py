"""Two read-only measurements owed by amendment item 37 once its builds run, on small synthetic graphs: what enters
VM_c by route (experiments/measure_pool_route_share.py, decision 9.129's figure of 12 November 2026) and the
before-and-after counts of the expression rebuild (experiments/compare_expression_rebuild.py, item 37 rulings draft,
section 8 (c))."""
from __future__ import annotations

import json

import pandas as pd
import pytest

from experiments.compare_expression_rebuild import compare, flag_changes, pores_and_catalysts, target_site_changes
from experiments.measure_pool_route_share import inputs_of_membrane_potential, main as pool_route_main


def membrane_graph() -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = pd.DataFrame({"node_id": ["VM_c", "NEURON_MAM02519c", "NEURON_MAM02200c", "MAR_NAV", "MAR_KIR", "GENE:X"],
                          "node_type": ["membrane_potential", "metabolite", "metabolite", "reaction", "reaction", "gene"]})
    edges = pd.DataFrame({"source_id": ["NEURON_MAM02519c", "NEURON_MAM02200c", "MAR_NAV", "MAR_KIR", "GENE:X", "VM_c"],
                          "target_id": ["VM_c", "VM_c", "VM_c", "VM_c", "VM_c", "MAR_NAV"],
                          "relation_type": ["driving_force", "driving_force", "driving_force", "driving_force", "activates", "voltage_gates"],
                          "weight": [1.306, 0.094, 300.0, 385.2, 2.0, 1.0]})
    return edges, nodes


def test_the_pool_share_is_the_pool_edges_weight_over_all_weight_entering_vm_c():
    edges, nodes = membrane_graph()
    result = inputs_of_membrane_potential(edges, nodes)
    assert result["edges_into_VM_c"] == 5 and result["weights_stored"]
    assert result["pool_weight"] == pytest.approx(1.4) and result["total_weight"] == pytest.approx(688.6)
    assert result["pool_share_of_total_weight"] == pytest.approx(1.4 / 688.6)
    assert result["conductance_edges_from_reactions"] == 2 and result["conductance_weight_from_reactions"] == pytest.approx(685.2)
    kinds = {(row["relation_type"], row["source_kind"]): row["edges"] for row in result["by_relation_and_source"]}
    assert kinds == {("activates", "other"): 1, ("driving_force", "neuronal_pool"): 2, ("driving_force", "reaction"): 2}
    unweighted = inputs_of_membrane_potential(edges.drop(columns="weight"), nodes)
    assert not unweighted["weights_stored"] and unweighted["pool_share_of_total_weight"] == pytest.approx(2 / 5)


def test_the_pool_route_script_writes_its_record_outside_data(tmp_path):
    edges, nodes = membrane_graph()
    graph = tmp_path / "graph"
    graph.mkdir()
    edges.to_parquet(graph / "edges.parquet")
    nodes.to_parquet(graph / "nodes.parquet")
    output = tmp_path / "pool_route.json"
    pool_route_main(["--graph-dir", str(graph), "--output", str(output)])
    record = json.loads(output.read_text())
    assert record["pool_share_of_total_weight"] == pytest.approx(1.4 / 688.6) and len(record["inputs_sha256"]) == 2
    assert "not recorded" in record["not_taken"]


def nodes_table(flags: dict[str, object], extra: list[tuple[str, str, str]] = ()) -> pd.DataFrame:
    rows = [(f"GENE:{symbol}", "gene", symbol, flag) for symbol, flag in flags.items()]
    rows += [(node_id, node_type, symbol, False) for node_id, node_type, symbol in extra]
    return pd.DataFrame(rows, columns=["node_id", "node_type", "gene_symbol", "brain_expressed"])


def test_a_gene_flag_change_is_counted_in_each_direction_with_unknown_read_as_not_expressed():
    before = nodes_table({"A": False, "B": True, "C": None, "D": None, "E": True})
    after = nodes_table({"A": True, "B": False, "C": True, "D": False, "F": True})
    result = flag_changes(before, after)
    assert result["turned_expressed"] == ["GENE:A", "GENE:C"] and result["turned_not_expressed"] == ["GENE:B"]
    assert result["unknown_became_known"] == ["GENE:C", "GENE:D"]  # D unknown then not expressed: known, no flag change
    assert result["genes_only_before"] == 1 and result["genes_only_after"] == 1


def test_pores_are_reactions_with_an_edge_into_vm_c_and_catalysts_the_sources_of_catalysis():
    edges, nodes = membrane_graph()
    edges = pd.concat([edges, pd.DataFrame({"source_id": ["PROTEIN:SCN1A"], "target_id": ["MAR_NAV"], "relation_type": ["catalyzed_by"], "weight": [1.0]})])
    pores, catalysts, into = pores_and_catalysts(edges, nodes)
    assert pores == {"MAR_NAV", "MAR_KIR"} and catalysts == {"PROTEIN:SCN1A"}
    assert into == {"activates from gene": 1, "driving_force from metabolite": 2, "driving_force from reaction": 2}


def test_a_build_whose_conductance_edges_come_from_the_pools_is_not_recorded_as_a_build_with_no_edge():
    """graph_full_neuronal_split_binders_drugs_v5 has 0 pores by this rule: its 6 edges into VM_c are driving_force
    from metabolite pool nodes, which the breakdown says and the pore count alone would not."""
    edges, nodes = membrane_graph()
    pools_only = edges[~edges.source_id.isin(["MAR_NAV", "MAR_KIR"])]
    pores, _, into = pores_and_catalysts(pools_only, nodes)
    assert pores == set() and into == {"activates from gene": 1, "driving_force from metabolite": 2}


def test_a_target_moves_from_plasma_to_brain_when_its_gene_turns_brain_expressed():
    entries = pd.DataFrame({"perturbation_id": ["D1", "D1", "D2"], "target_node_id": ["PROTEIN:SLC6A4", "PROTEIN:HTR2A", "PROTEIN:HTR2A"]})
    symbols = {"PROTEIN:SLC6A4": "SLC6A4", "PROTEIN:HTR2A": "HTR2A"}
    result = target_site_changes(entries, entries, symbols, symbols, brain_genes_before={"HTR2A"}, brain_genes_after={"SLC6A4"})
    assert result["plasma_to_brain"] == [["D1", "PROTEIN:SLC6A4", "SLC6A4"]]
    assert result["brain_to_plasma"] == [["D1", "PROTEIN:HTR2A", "HTR2A"], ["D2", "PROTEIN:HTR2A", "HTR2A"]]
    assert result["counts"] == {"plasma_to_brain_pairs": 1, "plasma_to_brain_targets": 1, "plasma_to_brain_drugs": 1,
                                "brain_to_plasma_pairs": 2, "brain_to_plasma_drugs": 2}


def test_the_comparison_of_two_builds_reads_their_tables(tmp_path):
    for name, flags in (("before", {"SLC6A4": False, "KCNK1": None}), ("after", {"SLC6A4": True, "KCNK1": True})):
        directory = tmp_path / name
        directory.mkdir()
        nodes = pd.concat([nodes_table(flags, [("PROTEIN:SLC6A4", "protein", "SLC6A4"), ("PROTEIN:KCNK1", "protein", "KCNK1"),
                                               ("MAR_K", "reaction", None), ("VM_c", "membrane_potential", None)])])
        edges = pd.DataFrame({"source_id": ["PROTEIN:KCNK1", "MAR_K"] if name == "after" else ["MAR_K"],
                              "target_id": ["MAR_K", "VM_c"] if name == "after" else ["VM_c"],
                              "relation_type": ["catalyzed_by", "driving_force"] if name == "after" else ["driving_force"]})
        nodes.to_parquet(directory / "nodes.parquet")
        edges.to_parquet(directory / "edges.parquet")
        pd.DataFrame({"perturbation_id": ["CID1"], "drug_node_id": ["DRUG:CID1"], "target_node_id": ["PROTEIN:SLC6A4"], "sign": [-1.0],
                      "magnitude": [1.0]}).to_parquet(directory / "drug_entry_nodes.parquet")
    result = compare(tmp_path / "before", tmp_path / "after")
    assert result["genes_whose_flag_changes"]["counts"] == {"turned_expressed": 2, "turned_not_expressed": 0, "unknown_became_known": 1}
    assert result["catalysts"]["added"] == ["PROTEIN:KCNK1"] and result["pores"]["before"] == result["pores"]["after"] == 1
    assert result["drug_target_sites"]["plasma_to_brain"] == [["CID1", "PROTEIN:SLC6A4", "SLC6A4"]]
    assert result["edges_into_membrane_potential"] == {"before": {"driving_force from reaction": 1}, "after": {"driving_force from reaction": 1}}


def test_a_catalyst_with_no_gene_symbol_is_counted_apart_from_the_flag_changes_it_cannot_show(tmp_path):
    """A protein_entity catalyst (a complex) has no gene_symbol, and the flag-change rule matches a catalyst by its
    own symbol, so 316 of the 12 November build's 3,181 catalysts can never be reported; the record says how many."""
    for name, flags in (("before", {"KCNK1": False}), ("after", {"KCNK1": True})):
        directory = tmp_path / name
        directory.mkdir()
        nodes_table(flags, [("PROTEIN:KCNK1", "protein", "KCNK1"), ("COMPLEX:1", "protein_entity", None),
                            ("MAR_K", "reaction", None), ("VM_c", "membrane_potential", None)]).to_parquet(directory / "nodes.parquet")
        pd.DataFrame({"source_id": ["PROTEIN:KCNK1", "COMPLEX:1", "MAR_K"], "target_id": ["MAR_K", "MAR_K", "VM_c"],
                      "relation_type": ["catalyzed_by", "catalyzed_by", "driving_force"]}).to_parquet(directory / "edges.parquet")
    result = compare(tmp_path / "before", tmp_path / "after")
    assert result["catalysts_whose_gene_flag_changes"] == ["PROTEIN:KCNK1"]
    assert result["catalysts_a_flag_change_cannot_reach"] == {"count": 1, "by_node_type": {"protein_entity": 1}, "catalysts": ["COMPLEX:1"]}
    assert result["drug_target_sites"].startswith("not compared")
