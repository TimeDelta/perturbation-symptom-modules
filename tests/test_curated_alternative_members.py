"""Curated alternative members (decision 9.68 (a), the owner on 20 October 2026: VAMP1 beside VAMP2):
graph/curated_mechanisms.py add_alternative_members, docs/curated_alternative_members.csv, and the "or" the pair
gets in the complex gate of graph/brain_expression_weights.py."""
from pathlib import Path

import pandas as pd
import pytest

from mechanistic_pathway_learning.graph.brain_expression_weights import complex_limiting_member_expression, node_cell_class_weights
from mechanistic_pathway_learning.graph.curated_mechanisms import (ALTERNATIVE_EVIDENCE_PREFIX, ALTERNATIVE_REQUIRED_COLUMNS,
                                                                   DEFAULT_ALTERNATIVE_MEMBERS_PATH, add_alternative_members,
                                                                   alternative_member_groups, alternative_share, pubmed_ids_of,
                                                                   read_alternative_members)
from mechanistic_pathway_learning.graph.edge_evidence import CURATED_PMID, family_of

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = REPOSITORY_ROOT / DEFAULT_ALTERNATIVE_MEMBERS_PATH


def vesicle_graph():
    """A primary in two entities beside a partner, its alternative in none, and an entity the primary is not in."""
    nodes = pd.DataFrame({"node_id": ["GENE:PRIMARY", "GENE:ALTERNATIVE", "GENE:PARTNER", "RCTE_1", "RCTE_2", "RCTE_3", "RCT_RELEASE"],
                          "node_type": ["gene", "gene", "gene", "protein_entity", "protein_entity", "protein_entity", "reaction"],
                          "gene_symbol": ["PRIMARY", "ALTERNATIVE", "PARTNER", None, None, None, None],
                          "ensembl_gene_id": ["ENSG_PRIMARY", "ENSG_ALTERNATIVE", "ENSG_PARTNER", None, None, None, None],
                          "gene_reaction_rule": [None] * 7,
                          "degree": [2, 0, 3, 2, 2, 1, 1]})
    edges = pd.DataFrame({"source_id": ["GENE:PRIMARY", "GENE:PARTNER", "GENE:PRIMARY", "GENE:PARTNER", "GENE:PARTNER", "RCTE_1"],
                          "target_id": ["RCTE_1", "RCTE_1", "RCTE_2", "RCTE_2", "RCTE_3", "RCT_RELEASE"],
                          "relation_type": ["member_of", "member_of", "member_of", "member_of", "member_of", "catalyzed_by"],
                          "sign": [1.0] * 6, "evidence_source": ["Reactome entity member"] * 5 + ["Reactome regulator"],
                          "weight": [1.0] * 6})
    relations = ["member_of", "catalyzed_by"]
    expression = pd.DataFrame({"gene_symbol": ["PRIMARY", "ALTERNATIVE", "PARTNER"], "brain_median_tpm_mean": [300.0, 100.0, 50.0]})
    return nodes, edges, relations, expression


def table_of(**row):
    defaults = {"alternative_id": "GENE:ALTERNATIVE", "primary_id": "GENE:PRIMARY", "decision": "9.68", "share_basis": "gtex_brain_median_tpm_mean",
                "pmids": "111111;222222", "quotes": "\"a quote\" (PMID 111111)", "reading": "why"}
    return pd.DataFrame([{**defaults, **row}], columns=list(ALTERNATIVE_REQUIRED_COLUMNS))


def test_the_alternative_joins_every_entity_of_the_primary_and_splits_its_weight():
    nodes, edges, relations, expression = vesicle_graph()
    new_nodes, new_edges, new_relations, summary = add_alternative_members(nodes, edges, relations, table_of(), expression)
    weight_of = {(source, target): weight for source, target, weight in zip(new_edges.source_id, new_edges.target_id, new_edges.weight)}
    assert summary["edges_added"] == 2 and summary["rows"][0]["entities_joined"] == ["RCTE_1", "RCTE_2"]
    assert summary["rows"][0]["share_of_alternative"] == pytest.approx(0.25)
    for entity in ("RCTE_1", "RCTE_2"):
        assert weight_of[("GENE:ALTERNATIVE", entity)] == pytest.approx(0.25)
        assert weight_of[("GENE:PRIMARY", entity)] == pytest.approx(0.75)
        assert weight_of[("GENE:PARTNER", entity)] == 1.0, "another member's weight must not move"
    assert ("GENE:ALTERNATIVE", "RCTE_3") not in weight_of, "an entity the primary is not in is left alone"
    assert new_relations == relations
    assert new_edges.dtypes.to_dict() == edges.dtypes.to_dict()
    assert dict(zip(new_nodes.node_id, new_nodes.degree))["GENE:ALTERNATIVE"] == 2


def test_every_entity_keeps_its_summed_incoming_weight_so_no_divisor_changes():
    """Under item 28's total_in_degree divisor (decision 4.11: the divisor sums the weights) the other members' shares
    are then exactly what they were."""
    nodes, edges, relations, expression = vesicle_graph()
    _, new_edges, _, _ = add_alternative_members(nodes, edges, relations, table_of(), expression)
    assert new_edges.groupby("target_id").weight.sum().to_dict() == pytest.approx(edges.groupby("target_id").weight.sum().to_dict())


def test_the_edge_evidence_reads_the_new_edges_as_curated_with_their_pubmed_ids():
    nodes, edges, relations, expression = vesicle_graph()
    _, new_edges, _, _ = add_alternative_members(nodes, edges, relations, table_of(), expression)
    evidence = new_edges.evidence_source.iloc[-1]
    assert evidence.startswith(ALTERNATIVE_EVIDENCE_PREFIX) and "decision 9.68" in evidence
    assert CURATED_PMID.findall(evidence) == ["111111", "222222"]
    assert family_of(evidence) == "curated"
    unchanged = new_edges.iloc[:len(edges)]
    assert list(unchanged.evidence_source) == list(edges.evidence_source), "the primary's edges keep their imported evidence"


def test_an_entity_already_holding_the_alternative_is_left_as_it_is_and_reported():
    nodes, edges, relations, expression = vesicle_graph()
    edges = pd.concat([edges, pd.DataFrame([{"source_id": "GENE:ALTERNATIVE", "target_id": "RCTE_2", "relation_type": "member_of", "sign": 1.0,
                                             "evidence_source": "Reactome entity member", "weight": 1.0}])], ignore_index=True)
    _, new_edges, _, summary = add_alternative_members(nodes, edges, relations, table_of(), expression)
    assert summary["rows"][0]["entities_already_holding_the_alternative"] == ["RCTE_2"]
    weight_of = {(source, target): weight for source, target, weight in zip(new_edges.source_id, new_edges.target_id, new_edges.weight)}
    assert weight_of[("GENE:PRIMARY", "RCTE_2")] == 1.0 and weight_of[("GENE:ALTERNATIVE", "RCTE_2")] == 1.0


def test_a_missing_weight_counts_as_one_before_it_is_split():
    nodes, edges, relations, expression = vesicle_graph()
    edges["weight"] = float("nan")
    _, new_edges, _, _ = add_alternative_members(nodes, edges, relations, table_of(), expression)
    weight_of = {(source, target): weight for source, target, weight in zip(new_edges.source_id, new_edges.target_id, new_edges.weight)}
    assert weight_of[("GENE:PRIMARY", "RCTE_1")] == pytest.approx(0.75)


@pytest.mark.parametrize("row, expected", [
    ({"alternative_id": "GENE:NOT_THERE"}, "is not a node of the graph"),
    ({"primary_id": "RCTE_1"}, "must be a gene"),
    ({"alternative_id": "GENE:PRIMARY"}, "its own alternative"),
    ({"share_basis": "a guess"}, "share basis"),
    ({"pmids": ""}, "no PubMed id"),
    ({"quotes": " "}, "no quote"),
])
def test_a_row_that_cannot_be_added_as_written_raises(row, expected):
    nodes, edges, relations, expression = vesicle_graph()
    with pytest.raises(ValueError, match=expected):
        add_alternative_members(nodes, edges, relations, table_of(**row), expression)


def test_a_gene_without_expression_cannot_be_given_a_share():
    _, _, _, expression = vesicle_graph()
    with pytest.raises(ValueError, match="no row in the brain expression table"):
        alternative_share("MISSING", "PRIMARY", expression)


def test_the_pair_is_one_member_of_the_complex_gate_taking_the_larger_expression():
    """Without the "or" the scarce alternative would set the gate in every class where it is scarcer than the
    primary, which shuts the primary's routes too (the reason the pair is a disjunction)."""
    nodes, edges, relations, expression = vesicle_graph()
    _, new_edges, _, _ = add_alternative_members(nodes, edges, relations, table_of(), expression)
    class_expression = pd.DataFrame({"forebrain": [500.0, 5.0, 200.0], "motor": [20.0, 400.0, 200.0]},
                                    index=pd.Index(["ENSG_PRIMARY", "ENSG_ALTERNATIVE", "ENSG_PARTNER"], name="ensembl_gene_id"))
    groups = alternative_member_groups(table_of())
    plain = complex_limiting_member_expression(nodes, new_edges, class_expression)
    with_pair = complex_limiting_member_expression(nodes, new_edges, class_expression, alternative_groups=groups)
    assert plain.loc["RCTE_1", "forebrain"] == 5.0 and plain.loc["RCTE_1", "motor"] == 20.0
    assert with_pair.loc["RCTE_1", "forebrain"] == 200.0, "the primary carries the forebrain, the partner limits"
    assert with_pair.loc["RCTE_1", "motor"] == 200.0, "the alternative carries the motor class, the partner limits"
    before = complex_limiting_member_expression(nodes, edges, class_expression)
    assert with_pair.loc["RCTE_1", "forebrain"] == before.loc["RCTE_1", "forebrain"], "where the primary dominates the gate is unchanged"
    assert with_pair.loc["RCTE_3"].tolist() == before.loc["RCTE_3"].tolist(), "an entity without the pair is untouched"
    weights = node_cell_class_weights(nodes, class_expression, member_edges=new_edges, alternative_groups=groups, include_all_cells_class=False)
    assert weights.loc["RCTE_1", "motor"] == pytest.approx(200.0 / 201.0)


def test_groups_collect_every_alternative_of_one_primary():
    table = pd.concat([table_of(), table_of(alternative_id="GENE:THIRD")], ignore_index=True)
    assert alternative_member_groups(table) == [frozenset({"GENE:PRIMARY", "GENE:ALTERNATIVE", "GENE:THIRD"})]


def test_the_shares_keep_the_other_members_shares_in_the_linear_response_adjacency():
    torch = pytest.importorskip("torch")
    from mechanistic_pathway_learning.models.linear_response_encoder import LinearResponseEncoder
    nodes, edges, relations, expression = vesicle_graph()
    _, new_edges, _, _ = add_alternative_members(nodes, edges, relations, table_of(), expression)
    index_of = {node: position for position, node in enumerate(nodes.node_id)}

    def values_into(edge_table, entity):
        adjacency, _ = LinearResponseEncoder.signed_stacked_adjacency(
            num_graph_nodes=len(nodes), relation_types=relations,
            edge_source=torch.tensor(edge_table.source_id.map(index_of).to_numpy()), edge_target=torch.tensor(edge_table.target_id.map(index_of).to_numpy()),
            edge_relation=torch.tensor(edge_table.relation_type.map(relations.index).to_numpy()), edge_sign=torch.tensor(edge_table.sign.to_numpy(), dtype=torch.float32),
            normalisation="total_in_degree", edge_weight=torch.tensor(edge_table.weight.to_numpy(), dtype=torch.float32))
        # rows are relation * N + target and columns are sources, so the relations stack along the first axis
        dense = adjacency.to_dense().reshape(-1, len(nodes), len(nodes)).sum(dim=0)
        return {node: float(dense[index_of[entity], index_of[node]]) for node in ("GENE:PRIMARY", "GENE:ALTERNATIVE", "GENE:PARTNER")}

    before, after = values_into(edges, "RCTE_1"), values_into(new_edges, "RCTE_1")
    assert after["GENE:PARTNER"] == pytest.approx(before["GENE:PARTNER"]) == pytest.approx(0.5)
    assert after["GENE:PRIMARY"] + after["GENE:ALTERNATIVE"] == pytest.approx(before["GENE:PRIMARY"])
    assert after["GENE:ALTERNATIVE"] == pytest.approx(0.125)


def test_the_table_names_vamp1_for_vamp2_with_papers_that_were_read():
    table = read_alternative_members(TABLE_PATH)
    assert list(zip(table.alternative_id, table.primary_id)) == [("GENE:VAMP1", "GENE:VAMP2")]
    row = table.iloc[0]
    pmids = pubmed_ids_of(row.pmids)
    assert pmids == ["24944211", "11691998", "28253535"]
    assert all(f"PMID {pmid}" in row.quotes for pmid in pmids), "every PubMed id is quoted"
    assert len(row.dois.split(";")) == len(pmids)
    assert row.decision == "9.68" and row.share_basis == "gtex_brain_median_tpm_mean"
