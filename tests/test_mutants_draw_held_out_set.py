"""Tests added on 28 November 2026 to kill mutants of experiments/draw_held_out_set.py that tests/test_leakage_ceiling.py
lets survive (hand-made mutation testing; the mutants and which test kills each are listed in the session's report).
Each test checks what the script's docstrings say it does; its open definitions stay required arguments. Synthetic data
only: nothing here draws a held-out set from a real graph."""
import dataclasses
import json
import sys
from pathlib import Path

import numpy as np
import pytest

from mechanistic_pathway_learning.data_release import sha256_of_file
from mechanistic_pathway_learning.evaluation.leakage_only_adversary import (
    reach_edges, reached_nodes_of_perturbations, registered_channel_list, seen_reached_node_share, seen_target_share)
from mechanistic_pathway_learning.evaluation.target_held_out_split import targets_of_drugs, two_sided_held_out_perturbations
from tests.test_leakage_ceiling import DIGESTS, calibration_record
from tests.test_measure_leakage_only_adversary import synthetic_data, write_graph_directory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import draw_held_out_set as draw_script  # noqa: E402
from measure_leakage_only_adversary import graph_file_sha256  # noqa: E402


def held_out_and_training(data, seed):
    held_out_ids, held_out_targets = two_sided_held_out_perturbations(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds,
                                                                      data.node_ids, data.group_ids, seed)
    return held_out_ids, held_out_targets, [identifier for identifier in data.perturbation_ids if identifier not in held_out_ids]


def test_a_draw_checked_against_no_calibration_is_refused():
    """ceilings_of_calibrations: "the draw is checked against at least one calibration"."""
    with pytest.raises(ValueError, match="at least one calibration"):
        draw_script.ceilings_of_calibrations([], "disease_cluster", DIGESTS)


def test_a_seed_any_calibration_scored_as_a_pseudo_draw_is_refused():
    """The docstring: "A seed that was also a calibration pseudo-draw is refused", whichever calibration scored it."""
    channels = registered_channel_list(1, [("drug", "gene")], "stored")
    calibrations = [calibration_record(ceiling=2.0, channels=channels, pseudo_draw_seeds=range(5)),
                    calibration_record("seen_reached_node_share", ceiling=2.0, channels=channels, pseudo_draw_seeds=range(100, 105))]
    with pytest.raises(ValueError, match="were calibration pseudo-draws"):
        draw_script.draw_held_out_set(synthetic_data(), [102], calibrations, "disease_cluster", DIGESTS)


def a_graph_where_the_walk_length_and_the_edge_set_matter():
    """synthetic_data's perturbations on another graph: gene i (i < 9) encodes protein i, protein t leads to gene t + 9,
    and the proteins are currency nodes, so walks of one and two steps differ and so do the two edge sets."""
    data = synthetic_data()
    num_targets = 9
    targets = np.arange(num_targets)
    is_currency = np.array([name.startswith("PROTEIN:") for name in data.node_ids])
    return dataclasses.replace(data, edge_source=np.concatenate([num_targets + targets, targets]),
                               edge_target=np.concatenate([targets, num_targets + num_targets + targets]),
                               edge_relation=np.zeros(2 * num_targets, dtype=int), is_currency=is_currency)


def reached_share(data, seed, hops, edge_set, pairs):
    held_out_ids, _, training_ids = held_out_and_training(data, seed)
    source, target = reach_edges(data.edge_source, data.edge_target, data.is_currency, edge_set)
    reached = reached_nodes_of_perturbations(data.perturbation_ids, data.perturbation_seeds, data.node_ids, source, target, hops)
    return seen_reached_node_share(reached, sorted(held_out_ids), training_ids, dict(zip(data.perturbation_ids, data.perturbation_types)), pairs)


@pytest.mark.parametrize("hops, edge_set", [(1, "stored"), (1, "stored_without_currency_out_edges"), (2, "stored")])
def test_the_reached_statistic_is_computed_on_the_calibrated_channel_against_the_training_portion(hops, edge_set):
    """The docstring: each draw's label-free statistics are compared with the ceilings, computed with the channels the
    calibrations were measured with; seen_reached_node_share is over the held-out and the training perturbations."""
    data = a_graph_where_the_walk_length_and_the_edge_set_matter()
    pairs = [("drug", "gene")]
    channel_settings = [(1, "stored"), (1, "stored_without_currency_out_edges"), (2, "stored")]
    # a draw on which the three channels give three different statistics
    seed, others = next((candidate, shares) for candidate in range(100, 200)
                        for shares in [{setting: reached_share(data, candidate, *setting, pairs) for setting in channel_settings}]
                        if len(set(shares.values())) == 3)
    channels = registered_channel_list(hops, pairs, edge_set)
    calibrations = [calibration_record("seen_reached_node_share", ceiling=2.0, channels=channels)]
    record = draw_script.draw_held_out_set(data, [seed], calibrations, "disease_cluster", DIGESTS)
    assert record["accepted_seed"] == seed
    assert record["examined_seeds"][0]["statistics"]["seen_reached_node_share"] == pytest.approx(others[(hops, edge_set)])


def test_the_record_counts_the_held_out_set_as_the_docstring_lists(monkeypatch):
    """What it records: the held-out targets, the perturbations and the kept positives inside and outside the set (a
    pair set aside by the label mask is no kept positive), the symptoms with at least MINIMUM_POSITIVES_TO_SCORE kept
    positives inside it, and "the leakage groups of --group-by that hold perturbations on both sides"."""
    data = synthetic_data()
    generator = np.random.default_rng(7)
    label_mask = generator.random(data.outcomes.shape) < 0.6
    group_ids = [f"cluster_{index % 14}" if kind == "drug" else group for index, (kind, group) in enumerate(zip(data.perturbation_types, data.group_ids))]
    data = dataclasses.replace(data, label_mask=label_mask, group_ids=group_ids)
    ids, kinds = np.array(data.perturbation_ids), np.array(data.perturbation_types)
    kept = data.outcomes * label_mask
    seed = next(candidate for candidate in range(100, 140)
                if len({group for group, inside in zip(group_ids, np.isin(ids, list(held_out_and_training(data, candidate)[0]))) if inside}
                       & {group for group, inside in zip(group_ids, np.isin(ids, list(held_out_and_training(data, candidate)[0]))) if not inside}) > 0)
    held_out_ids, held_out_targets, _ = held_out_and_training(data, seed)
    inside = np.isin(ids, sorted(held_out_ids))
    is_drug = kinds == "drug"
    positives = {symptom: int(kept[inside, column].sum()) for column, symptom in enumerate(data.symptoms)}
    smallest_counted = min(count for count in positives.values() if count > 0)
    monkeypatch.setattr(draw_script, "MINIMUM_POSITIVES_TO_SCORE", smallest_counted)
    record = draw_script.draw_held_out_set(data, [seed], [calibration_record(ceiling=2.0)], "disease_cluster", DIGESTS)
    assert record["accepted_seed"] == seed
    groups_inside = {group for group, held in zip(group_ids, inside) if held}
    groups_outside = {group for group, held in zip(group_ids, inside) if not held}
    assert record["held_out_targets"] == sorted(held_out_targets) and record["held_out_targets"]
    assert (record["num_genes"], record["num_drugs"]) == (int((inside & ~is_drug).sum()), int((inside & is_drug).sum()))
    assert record["num_drugs_with_a_kept_positive"] == int((kept[inside & is_drug].sum(axis=1) > 0).sum())
    assert (record["kept_positive_pairs"], record["kept_positive_pairs_development"]) == (int(kept[inside].sum()), int(kept[~inside].sum()))
    assert record["kept_positives_by_symptom"] == positives
    assert record["symptoms_in_the_macro_average"] == sorted(symptom for symptom, count in positives.items() if count >= smallest_counted)
    assert record["leakage_groups_with_members_on_both_sides"] == len(groups_inside & groups_outside) > 0


def test_the_target_statistic_of_a_draw_is_over_its_held_out_drugs():
    """The docstring: "Each draw's label-free statistics are computed, reading no label, and compared with the ceilings";
    seen_target_share is "over the held-out drugs, the share of their mechanism targets that a training drug also has".
    (Added by the checker of 28 November 2026: a mutant computing it over the training portion survived.)"""
    data = synthetic_data()
    targets = targets_of_drugs(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids)
    seed = next(candidate for candidate in range(100, 140)
                if seen_target_share(targets, held_out_and_training(data, candidate)[0]) != seen_target_share(targets, held_out_and_training(data, candidate)[2]))
    held_out_ids, _, _ = held_out_and_training(data, seed)
    record = draw_script.draw_held_out_set(data, [seed], [calibration_record(ceiling=2.0)], "disease_cluster", DIGESTS)
    assert record["examined_seeds"][0]["statistics"] == {"seen_target_share": pytest.approx(seen_target_share(targets, held_out_ids))}


def test_the_record_counts_the_held_out_and_the_development_perturbations_as_draw_lockbox_does():
    """The held-out set is written in experiments/draw_lockbox.py's format (sourcing_sample's docstring: "the format
    experiments/draw_lockbox.py writes (configs/lockbox_v2.json), which experiments/draw_held_out_set.py also writes"),
    where num_perturbations counts the held-out set and num_development_perturbations the rest. (Added by the checker
    of 28 November 2026: a mutant swapping the two survived, since the existing test checks only their sum.)"""
    data = synthetic_data()
    held_out_ids, _, training_ids = held_out_and_training(data, 100)
    assert len(held_out_ids) != len(training_ids)
    record = draw_script.draw_held_out_set(data, [100], [calibration_record(ceiling=2.0)], "disease_cluster", DIGESTS)
    assert record["perturbation_ids"] == sorted(held_out_ids)
    assert (record["num_perturbations"], record["num_development_perturbations"]) == (len(held_out_ids), len(training_ids))


# ---------------------------------------------------------------- the command


def command_inputs(directory: Path, ceiling: float, monkeypatch) -> dict:
    graph = write_graph_directory(directory / "graph")
    evidence = directory / "evidence"
    evidence.mkdir()
    (evidence / "evidence_records.parquet").write_bytes(b"evidence")
    selection = directory / "selection.parquet"
    selection.write_bytes(b"selection")
    digests = {"graph_file_sha256": graph_file_sha256(graph), "evidence_records_sha256": sha256_of_file(evidence / "evidence_records.parquet"),
               "label_selection_sha256": sha256_of_file(selection)}
    calibration = directory / "calibration.json"
    calibration.write_text(json.dumps({**calibration_record(ceiling=ceiling), **digests}))
    seed_order = directory / "seed_order.json"
    seed_order.write_text(json.dumps([100, 101]))
    data = synthetic_data()
    monkeypatch.setattr(draw_script, "load_experiment_data", lambda *arguments, **keywords: data)
    monkeypatch.setattr(draw_script, "reactome_release_of_graph", lambda graph_directory: {"reactome_release": "98", "lineage": []})
    output = directory / "out" / "held_out.json"
    monkeypatch.setattr(sys, "argv", ["draw_held_out_set.py", "--graph-dir", str(graph), "--evidence-dir", str(evidence),
                                      "--label-selection", str(selection), "--group-by", "disease_cluster", "--seed-order", str(seed_order),
                                      "--calibration", str(calibration), "--output", str(output)])
    return {"output": output, "seed_order": seed_order, "calibration": calibration}


def test_the_command_writes_the_accepted_draw_once_with_the_files_it_was_drawn_from(tmp_path, monkeypatch):
    """The docstring: "The output is never overwritten", and the record holds "the seed order and its SHA-256", each
    calibration with its SHA-256 and ceiling, and the Reactome release."""
    paths = command_inputs(tmp_path, 2.0, monkeypatch)
    draw_script.main()
    record = json.loads(paths["output"].read_text())
    assert record["accepted_seed"] == 100 and record["seed_order_sha256"] == sha256_of_file(paths["seed_order"])
    assert record["calibrations"] == [{"path": str(paths["calibration"]), "sha256": sha256_of_file(paths["calibration"]),
                                       "statistic": "seen_target_share", "ceiling": 2.0}]
    assert record["reactome_release"] == {"reactome_release": "98", "lineage": []}
    written = paths["output"].read_text()
    with pytest.raises(SystemExit, match="is drawn once and is not overwritten"):
        draw_script.main()
    assert paths["output"].read_text() == written


def test_the_command_writes_nothing_when_no_seed_passes(tmp_path, monkeypatch):
    """The docstring: "If none passes, nothing is written and the examined seeds are printed for the owner"."""
    paths = command_inputs(tmp_path, -1.0, monkeypatch)
    with pytest.raises(SystemExit, match="no seed of the order passes every ceiling"):
        draw_script.main()
    assert not paths["output"].exists()
