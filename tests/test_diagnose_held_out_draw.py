"""experiments/diagnose_held_out_draw.py: label-free diagnostics of the held-out draw under the rule as it stands and the
draft options of 28 November 2026. Every number is checked on small synthetic fixtures, worked out by hand in the
comments; the loader is checked to read no symptom label (by the columns it asks for, and by running on a table that
holds none) and to give the inputs experiment_data.load_experiment_data gives."""
import dataclasses
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mechanistic_pathway_learning.evaluation.experiment_data import GROUPING_COLUMNS, load_experiment_data
from mechanistic_pathway_learning.evaluation.target_held_out_split import HeldOutDrawOptions
from tests.test_gene_protein_split import RELATIONS, split_toy_graph, write_graph

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import diagnose_held_out_draw  # noqa: E402
from diagnose_held_out_draw import (  # noqa: E402
    DRAW_INPUT_COLUMNS, ROW_FILTER_COLUMNS, RULES, DrawInputs, diagnose, gene_side_overlap, jaccard_index,
    load_draw_inputs)

# ---------------------------------------------------------------- a hand-checkable fixture
#
# A split graph. Five drugs d0..d4, drug di seeding protein PROTEIN:i alone. Five clusters cluster_0..cluster_4 of four
# genes each, gene gi_0 encoding PROTEIN:i and gi_1..gi_3 encoding nothing, and one cluster_big of six genes encoding
# nothing: 26 gene-side perturbations in six groups, the largest cluster_big (6 of 26). Each drug is its own group.
#
# At fraction 0.2 the drug side holds one target, the first of the seed's order (one drug in five is 0.2 exactly; two
# would be 0.4), so i* below is that target's index. Under the rule as it stands, 5 grouped folds: cluster_big (6)
# goes to fold 0, the five clusters to folds 1, 2, 3, 4 and 1, the drugs to folds 2, 3, 4, 2, 3, so fold 0 holds
# cluster_big alone under every seed. Under M2 the side is the first group of the seed's order alone (4/26 or 6/26 is
# nearer 0.2 than any two groups). Under M1 with M2 cluster_i* is forced (4/26 < 0.2) and nothing is added.

NUM_GENE_SIDE = 26


def hand_fixture() -> DrawInputs:
    protein_nodes = [f"PROTEIN:{index}" for index in range(5)]
    gene_names = [f"g{index}_{member}" for index in range(5) for member in range(4)] + [f"big_{member}" for member in range(6)]
    node_ids = protein_nodes + [f"GENE:{name}" for name in gene_names]
    node_index = {name: position for position, name in enumerate(node_ids)}
    perturbation_ids = [f"d{index}" for index in range(5)] + gene_names
    perturbation_types = ["drug"] * 5 + ["gene"] * len(gene_names)
    seeds = [np.array([index]) for index in range(5)] + [np.array([node_index[f"GENE:{name}"]]) for name in gene_names]
    group_ids = [f"drug_group_{index}" for index in range(5)] + [f"cluster_{index}" for index in range(5) for _ in range(4)] + ["cluster_big"] * 6
    return DrawInputs(perturbation_ids=perturbation_ids, perturbation_types=perturbation_types, perturbation_seeds=seeds,
                      node_ids=node_ids, group_ids=group_ids,
                      proteins_encoded_by_gene={f"GENE:g{index}_0": {f"PROTEIN:{index}"} for index in range(5)},
                      columns_read={})


def first_of_order(items, seed):
    order = sorted(items)
    random.Random(seed).shuffle(order)
    return order[0]


def held_target_index(seed) -> str:
    return first_of_order([f"PROTEIN:{index}" for index in range(5)], seed).removeprefix("PROTEIN:")


SEEDS = list(range(12))


def test_the_population_block():
    population = diagnose(hand_fixture(), [0], 0.2)["population"]
    assert population == {"perturbations": 31, "drugs": 5, "gene_side_perturbations": 26, "gene_side_groups": 6,
                          "largest_group": "cluster_big", "largest_group_size": 6, "largest_group_share": 6 / 26,
                          "groups_tied_for_largest": 1, "split_graph": True, "genes_encoding_a_protein_node": 5,
                          "most_shared_target": {"target": "PROTEIN:0", "drugs": 1, "share_of_drugs": 0.2,
                                                 "above_twice_the_fraction": False}}


def test_every_number_under_the_rule_as_it_stands():
    result = diagnose(hand_fixture(), SEEDS, 0.2)["rules"]["rule_as_it_stands"]
    for seed in SEEDS:
        assert result["seeds"][str(seed)] == {
            "drug_side_size": 1, "held_out_targets": 1,
            "gene_side_size": 6, "gene_side_share_of_gene_side_perturbations": 6 / 26, "gene_side_groups": 1,
            "largest_group_size": 6, "largest_group_share": 6 / 26, "largest_group_members_on_the_gene_side": 6,
            "largest_group_wholly_on_the_gene_side": True,
            "held_out_targets_whose_gene_perturbation_trains": 1,  # g{i*}_0 encodes the held-out protein and trains
            "m1_forced_groups": 0, "m1_forced_gene_side_size": 0, "m1_forced_share_of_the_gene_side": 0.0,
            "m1_forced_groups_pass_the_fraction": False, "m1_overshoot": 0.0,
            "groups_with_members_on_both_sides": 0}, seed
    overlap = result["gene_side_jaccard_across_seeds"]
    assert overlap["the_same_gene_side_under_every_seed"] and overlap["minimum"] == overlap["maximum"] == 1.0
    assert len(overlap["pairs"]) == len(SEEDS) * (len(SEEDS) - 1) // 2


def test_every_number_under_the_identity_option_alone():
    result = diagnose(hand_fixture(), SEEDS, 0.2)["rules"]["identity_option_alone"]
    for seed in SEEDS:
        numbers = result["seeds"][str(seed)]
        assert numbers["gene_side_size"] == 7 and numbers["gene_side_share_of_gene_side_perturbations"] == 7 / 26
        assert numbers["gene_side_groups"] == 2  # cluster_big, and g{i*}_0's cluster
        assert numbers["held_out_targets_whose_gene_perturbation_trains"] == 0
        assert numbers["groups_with_members_on_both_sides"] == 1  # g{i*}_0 out, its three cluster mates in training
        assert numbers["largest_group_wholly_on_the_gene_side"] and numbers["m1_forced_groups"] == 0


def test_every_number_under_m2():
    result = diagnose(hand_fixture(), SEEDS, 0.2)["rules"]["m2_seeded_group_prefix"]
    gene_sides = {}
    for seed in SEEDS:
        numbers = result["seeds"][str(seed)]
        first_group = first_of_order([f"cluster_{index}" for index in range(5)] + ["cluster_big"], seed)
        size = 6 if first_group == "cluster_big" else 4
        assert numbers["gene_side_size"] == size and numbers["gene_side_share_of_gene_side_perturbations"] == size / 26
        assert numbers["gene_side_groups"] == 1 and numbers["groups_with_members_on_both_sides"] == 0
        assert numbers["largest_group_members_on_the_gene_side"] == (6 if first_group == "cluster_big" else 0)
        assert numbers["largest_group_wholly_on_the_gene_side"] == (first_group == "cluster_big")
        assert numbers["held_out_targets_whose_gene_perturbation_trains"] == int(first_group != f"cluster_{held_target_index(seed)}")
        gene_sides[seed] = first_group
    pairs = {(first, second): value for first, second, value in result["gene_side_jaccard_across_seeds"]["pairs"]}
    for (first, second), value in pairs.items():
        assert value == (1.0 if gene_sides[first] == gene_sides[second] else 0.0)  # whole groups: the same or disjoint
    assert not result["gene_side_jaccard_across_seeds"]["the_same_gene_side_under_every_seed"]


def test_every_number_under_m1_with_m2():
    result = diagnose(hand_fixture(), SEEDS, 0.2)["rules"]["m1_with_m2"]
    for seed in SEEDS:
        numbers = result["seeds"][str(seed)]
        assert numbers["drug_side_size"] == 1 and numbers["held_out_targets"] == 1
        assert numbers["m1_forced_groups"] == 1 and numbers["m1_forced_gene_side_size"] == 4
        assert numbers["m1_forced_share_of_the_gene_side"] == 4 / 26
        assert not numbers["m1_forced_groups_pass_the_fraction"] and numbers["m1_overshoot"] == 0.0
        assert numbers["gene_side_size"] == 4 and numbers["gene_side_groups"] == 1  # the forced cluster, nothing added
        assert numbers["held_out_targets_whose_gene_perturbation_trains"] == 0
        assert numbers["largest_group_members_on_the_gene_side"] == 0 and not numbers["largest_group_wholly_on_the_gene_side"]
        assert numbers["groups_with_members_on_both_sides"] == 0


def test_m1s_overshoot_when_the_forced_group_alone_passes_the_fraction():
    # at 0.15 one target is still held (0.2 is nearer 0.15 than 0 or 0.4), and 4/26 = 0.1538 passes 0.15
    result = diagnose(hand_fixture(), SEEDS, 0.15)["rules"]["m1_with_m2"]
    for seed in SEEDS:
        numbers = result["seeds"][str(seed)]
        assert numbers["m1_forced_groups_pass_the_fraction"] and numbers["m1_overshoot"] == pytest.approx(4 / 26 - 0.15)
        assert numbers["gene_side_size"] == 4


def test_the_most_shared_target_above_twice_the_fraction_empties_the_drug_side_when_it_comes_first():
    """Four of five drugs hold PROTEIN:0 (0.8 > 0.4): a seed whose order starts with it draws no drug, since the empty
    prefix (0.2 from 0.2) is nearer than 0.8 and adding PROTEIN:1 gives 1.0."""
    inputs = hand_fixture()
    seeds = [np.array([0])] * 4 + [np.array([1])] + list(inputs.perturbation_seeds[5:])
    inputs = dataclasses.replace(inputs, perturbation_seeds=seeds)
    result = diagnose(inputs, SEEDS, 0.2)
    assert result["population"]["most_shared_target"] == {"target": "PROTEIN:0", "drugs": 4, "share_of_drugs": 0.8,
                                                          "above_twice_the_fraction": True}
    for seed in SEEDS:
        starts_with_the_shared_target = first_of_order(["PROTEIN:0", "PROTEIN:1"], seed) == "PROTEIN:0"
        assert (result["rules"]["rule_as_it_stands"]["seeds"][str(seed)]["drug_side_size"] == 0) == starts_with_the_shared_target


def test_the_jaccard_index():
    assert jaccard_index({"a", "b"}, {"b", "c"}) == 1 / 3 and jaccard_index(set(), set()) == 1.0
    overlap = gene_side_overlap({0: {"a"}, 1: {"a"}, 2: {"b"}})
    assert overlap["pairs"] == [[0, 1, 1.0], [0, 2, 0.0], [1, 2, 0.0]]
    assert overlap["minimum"] == 0.0 and overlap["maximum"] == 1.0 and overlap["mean"] == pytest.approx(1 / 3)
    assert not overlap["the_same_gene_side_under_every_seed"]


def test_the_rules_are_the_four_asked_for():
    assert RULES["rule_as_it_stands"] == HeldOutDrawOptions()
    assert RULES["m2_seeded_group_prefix"] == HeldOutDrawOptions(gene_side_rule="seeded_group_prefix")
    assert RULES["m1_with_m2"] == HeldOutDrawOptions(True, True, "seeded_group_prefix")
    assert RULES["identity_option_alone"] == HeldOutDrawOptions(hold_out_genes_encoding_held_out_targets=True)


# ---------------------------------------------------------------- the loader reads no label


def evidence_row(perturbation, kind, cluster, seeds, symptom="anxiety", relation="induces", grade="A", positive_reports=1):
    return {"perturbation_id": perturbation, "perturbation_type": kind, "perturbation_label": perturbation, "group_id": perturbation,
            "disease_cluster_id": cluster, "symptom": symptom, "relation": relation, "evidence_class": "monogenic", "grade": grade,
            "weight": 1.0, "label_frequency": None, "in_metabolic_layer": True, "evidence_date": None,
            "positive_report_count": positive_reports, "perturbation_nodes": json.dumps(seeds)}


def write_fixture_tables(tmp_path: Path) -> tuple[Path, Path, Path]:
    """The split toy graph of tests/test_gene_protein_split.py and its merged twin, and an evidence table with rows the
    loader's filters drop: knockout_C has only a grade C row, knockout_TF only a relieves row and drug_none only a row
    without a positive report."""
    nodes, edges, assignment, split_nodes, split_edges, relations, _ = split_toy_graph()
    write_graph(tmp_path / "merged", nodes, edges, RELATIONS)
    write_graph(tmp_path / "split", split_nodes, split_edges, relations, assignment)
    evidence_directory = tmp_path / "evidence"
    evidence_directory.mkdir()
    pd.DataFrame([evidence_row("knockout_D", "gene", "cluster:D", [["GENE:D", -1.0, 1.0]]),
                  evidence_row("knockout_D", "gene", "cluster:D", [["GENE:D", -1.0, 1.0]], symptom="fatigue", grade="B"),
                  evidence_row("knockout_M", "gene", "cluster:M", [["GENE:M", -1.0, 1.0]]),
                  evidence_row("knockout_B", "gene", "cluster:D", [["GENE:B", -1.0, 1.0]]),
                  evidence_row("knockout_C", "gene", "cluster:C", [["GENE:C", -1.0, 1.0]], grade="C"),
                  evidence_row("knockout_TF", "gene", "cluster:TF", [["GENE:TF", -1.0, 1.0]], relation="relieves"),
                  evidence_row("drug_BC", "drug", "drug_BC", [["GENE:B", -1.0, 0.5], ["GENE:C", -1.0, 0.5], ["GENE:D", -1.0, 0.5]]),
                  evidence_row("drug_M", "drug", "drug_M", [["GENE:M", 1.0, 1.0]]),
                  evidence_row("drug_none", "drug", "drug_none", [["GENE:TF", 1.0, 1.0]], positive_reports=0)]
                 ).to_parquet(evidence_directory / "evidence_records.parquet", index=False)
    return tmp_path / "merged", tmp_path / "split", evidence_directory


@pytest.mark.parametrize("group_by", sorted(GROUPING_COLUMNS))
def test_the_label_free_loader_gives_the_inputs_the_experiment_loader_gives(tmp_path, group_by):
    merged, split, evidence = write_fixture_tables(tmp_path)
    for graph in (merged, split):
        inputs = load_draw_inputs(graph, evidence, group_by)
        data = load_experiment_data(graph, evidence, group_by=group_by)
        assert inputs.perturbation_ids == list(data.perturbation_ids) == ["drug_BC", "drug_M", "knockout_B", "knockout_D", "knockout_M"]
        assert inputs.perturbation_types == list(data.perturbation_types)
        assert inputs.node_ids == list(data.node_ids)
        assert [seed.tolist() for seed in inputs.perturbation_seeds] == [seed.tolist() for seed in data.perturbation_seeds]
        assert inputs.group_ids == [str(group) for group in data.group_ids]
    split_inputs = load_draw_inputs(split, evidence, group_by)
    assert split_inputs.proteins_encoded_by_gene["GENE:M"] == {"PROTEIN:M:PM1", "PROTEIN:M:PM2"}  # both, drug target or not
    assert load_draw_inputs(merged, evidence, group_by).proteins_encoded_by_gene == {}


def test_the_loader_asks_for_no_label_column(tmp_path, monkeypatch):
    _, split, evidence = write_fixture_tables(tmp_path)
    requested = []
    read_parquet = pd.read_parquet

    def recording_read_parquet(path, *arguments, **keywords):
        requested.append((Path(path).name, keywords.get("columns")))
        return read_parquet(path, *arguments, **keywords)

    monkeypatch.setattr(diagnose_held_out_draw.pd, "read_parquet", recording_read_parquet)
    inputs = load_draw_inputs(split, evidence, "disease_cluster_and_targets")
    evidence_requests = [columns for name, columns in requested if name == "evidence_records.parquet"]
    assert len(evidence_requests) == 1 and evidence_requests[0] is not None
    allowed = set(DRAW_INPUT_COLUMNS) | set(ROW_FILTER_COLUMNS) | {"disease_cluster_id", "perturbation_parts"}
    assert set(evidence_requests[0]) <= allowed
    assert not {"symptom", "weight", "label_frequency", "evidence_date", "perturbation_label"} & set(evidence_requests[0])
    assert all(columns is not None for name, columns in requested if name == "nodes.parquet")
    assert inputs.columns_read["evidence_records.parquet"] == evidence_requests[0]


def test_the_loader_runs_on_a_table_that_holds_no_label(tmp_path):
    merged, split, evidence = write_fixture_tables(tmp_path)
    table = pd.read_parquet(evidence / "evidence_records.parquet")
    expected = load_draw_inputs(split, evidence, "disease_cluster")
    stripped = tmp_path / "stripped"
    stripped.mkdir()
    table[list(DRAW_INPUT_COLUMNS) + ["disease_cluster_id"] + list(ROW_FILTER_COLUMNS)].to_parquet(stripped / "evidence_records.parquet", index=False)
    inputs = load_draw_inputs(split, stripped, "disease_cluster")
    assert inputs.perturbation_ids == expected.perturbation_ids and inputs.group_ids == expected.group_ids
    assert [seed.tolist() for seed in inputs.perturbation_seeds] == [seed.tolist() for seed in expected.perturbation_seeds]


def test_the_draw_inputs_have_no_field_for_a_label():
    names = {field.name for field in dataclasses.fields(DrawInputs)}
    assert names == {"perturbation_ids", "perturbation_types", "perturbation_seeds", "node_ids", "group_ids",
                     "proteins_encoded_by_gene", "columns_read"}


def test_the_script_writes_every_grouping_with_its_provenance(tmp_path, monkeypatch):
    _, split, evidence = write_fixture_tables(tmp_path)
    output = tmp_path / "out" / "diagnostics.json"
    monkeypatch.setattr(sys, "argv", ["diagnose_held_out_draw.py", "--graph-dir", str(split), "--evidence-dir", str(evidence),
                                      "--group-by", "disease_cluster", "gene", "--seeds", "0", "1", "2",
                                      "--provenance", "fixture graph, measured in a test", "--output", str(output)])
    diagnose_held_out_draw.main()
    record = json.loads(output.read_text())
    assert record["provenance"] == "fixture graph, measured in a test" and record["seeds"] == [0, 1, 2]
    assert set(record["groupings"]) == {"disease_cluster", "gene"}
    assert set(record["groupings"]["gene"]["rules"]) == set(RULES)
    assert set(record["groupings"]["gene"]["rules"]["m1_with_m2"]["seeds"]) == {"0", "1", "2"}
    assert record["groupings"]["gene"]["population"]["split_graph"] is True
