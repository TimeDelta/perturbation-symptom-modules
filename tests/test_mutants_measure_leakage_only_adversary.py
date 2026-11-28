"""Tests added on 28 November 2026 to kill mutants of experiments/measure_leakage_only_adversary.py, in
registered_two_sided_draw, one_draw and main's pseudo-draw loop, that tests/test_measure_leakage_only_adversary.py and
tests/test_leakage_ceiling.py let survive (hand-made mutation testing; the mutants and which test kills each are listed
in the session's report). Each test checks what the script's docstrings say it does. The test of the development rows,
added with the fix of _restrict on the same day, was found by reading the code rather than by a surviving mutant; the
tests after it were added by the checker of that branch, for mutants of its own that every earlier test let survive,
and they reach summarise as well. Synthetic data only: nothing here reads a real graph."""
import dataclasses
import json
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pytest

import experiments.measure_leakage_only_adversary as measurement
from mechanistic_pathway_learning.evaluation.experiment_data import PER_PERTURBATION_ARRAYS, PER_PERTURBATION_LISTS
from mechanistic_pathway_learning.evaluation.leakage_only_adversary import (
    POOLING_RULES, LeakageOnlyAdversary, neighbours_through_the_channels, reached_nodes_of_perturbations, seed_nodes_of_perturbations,
    seen_reached_node_share, seen_target_share)
from mechanistic_pathway_learning.evaluation.ranking_and_calibration_metrics import (
    macro_statistic, paired_bootstrap_macro_difference, paired_bootstrap_micro_difference)
from mechanistic_pathway_learning.evaluation.target_held_out_split import targets_of_drugs
from mechanistic_pathway_learning.models.baselines.popularity_baseline import PopularityBaseline
from tests.test_measure_leakage_only_adversary import synthetic_data, write_graph_directory

DRUG_GENE = [("drug", "gene")]


# ---------------------------------------------------------------- one pseudo-draw


@pytest.mark.parametrize("which", ["everything", "nothing"])
def test_a_draw_that_holds_out_nothing_or_trains_on_nothing_is_not_usable(monkeypatch, which):
    """experiments/calibrate_leakage_ceiling.py reads an unusable draw as one that "held out no row or trained on none",
    and summarise averages "over the usable draws"."""
    data = synthetic_data()
    held_out = set(data.perturbation_ids) if which == "everything" else set()
    monkeypatch.setattr(measurement, "registered_two_sided_draw", lambda data, draw_seed: (held_out, set()))
    assert measurement.one_draw(data, 100, "base_rate_shrunk_mean", 10) == {"draw_seed": 100, "usable": False}


def test_the_standard_error_is_the_95_percent_half_width_over_1_96():
    """STANDARD_ERRORS_IN_A_95_PERCENT_HALF_WIDTH: "a 95 percent bootstrap interval is about this many standard errors
    wide on each side", used "to turn the interval the registered machinery returns into the standard error"."""
    assert measurement.STANDARD_ERRORS_IN_A_95_PERCENT_HALF_WIDTH == pytest.approx(NormalDist().inv_cdf(0.975), abs=1e-6)
    draw = measurement.one_draw(synthetic_data(), 100, "base_rate_shrunk_mean", 50)
    checked = 0
    for key, value in draw.items():
        if "_interval_over_" in key:
            lower, upper = value
            if np.isfinite(lower) and np.isfinite(upper):  # a stratum with no symptom to score reads NaN
                assert draw[key.replace("_interval_over_", "_standard_error_over_")] == pytest.approx((upper - lower) / 2 / 1.959964)
                checked += 1
    assert checked >= 6 and any(draw[key] > 0 for key in draw if "_standard_error_over_" in key)


def test_a_draw_records_what_its_own_held_out_set_and_training_set_give():
    """one_draw: the held-out set "as the registration actually draws it" (registered_two_sided_draw), the adversary
    fitted on the training labels and scoring the held-out rows through the channels given, and the label-free
    statistics of that split."""
    data = synthetic_data()
    seed = 100
    held_out_ids, _ = measurement.registered_two_sided_draw(data, seed)
    held_out = [identifier for identifier in data.perturbation_ids if identifier in held_out_ids]
    training = [identifier for identifier in data.perturbation_ids if identifier not in held_out_ids]
    held_rows = [data.perturbation_ids.index(identifier) for identifier in held_out]
    training_rows = [data.perturbation_ids.index(identifier) for identifier in training]
    types_of = dict(zip(data.perturbation_ids, data.perturbation_types))
    reached = reached_nodes_of_perturbations(data.perturbation_ids, data.perturbation_seeds, data.node_ids, data.edge_source, data.edge_target, 1)
    neighbours = neighbours_through_the_channels(held_out, training, seed_nodes_of_perturbations(data.perturbation_ids, data.perturbation_seeds,
                                                                                                data.node_ids), reached, types_of, DRUG_GENE)
    assert neighbours
    adversary = LeakageOnlyAdversary("base_rate_shrunk_mean").fit(training, data.outcomes[training_rows], data.label_mask[training_rows])
    macro = macro_statistic()
    expected_macro = float(macro(adversary.predict(held_out, neighbours), data.outcomes[held_rows], data.label_mask[held_rows]))
    assert expected_macro != pytest.approx(float(macro(adversary.predict(held_out, {}), data.outcomes[held_rows], data.label_mask[held_rows])))

    draw = measurement.one_draw(data, seed, "base_rate_shrunk_mean", 10, reached, DRUG_GENE)
    assert draw["adversary_macro_auprc"] == pytest.approx(expected_macro)
    assert (draw["held_out_drugs"], draw["held_out_genes"]) == (sum(types_of[identifier] == "drug" for identifier in held_out),
                                                                sum(types_of[identifier] != "drug" for identifier in held_out))
    assert draw["held_out_drugs"] > 0 and draw["held_out_genes"] > 0
    targets = targets_of_drugs(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids)
    assert draw["seen_target_share"] == pytest.approx(seen_target_share(targets, held_out))
    assert draw["seen_target_share"] != pytest.approx(seen_target_share(targets, training))
    assert draw["seen_reached_node_share"] == pytest.approx(seen_reached_node_share(reached, held_out, training, types_of, DRUG_GENE))


# ---------------------------------------------------------------- the pseudo-draw loop of main


def run_main(monkeypatch, directory: Path, *extra: str, data=None, num_bootstrap="5", recorder=None):
    graph = directory / "graph"
    if not graph.exists():
        write_graph_directory(graph)
        (directory / "evidence").mkdir()
        (directory / "evidence" / "evidence_records.parquet").write_bytes(b"evidence")
        (directory / "selection.parquet").write_bytes(b"selection")
    data = synthetic_data() if data is None else data
    monkeypatch.setattr(measurement, "load_experiment_data", lambda *arguments, **keywords: data)
    if recorder is not None:
        original = measurement.one_draw

        def recording(data, draw_seed, *arguments):
            recorder.append((draw_seed, list(data.perturbation_ids)))
            return original(data, draw_seed, *arguments)

        monkeypatch.setattr(measurement, "one_draw", recording)
    monkeypatch.setattr(sys, "argv", ["measure_leakage_only_adversary.py", "--graph-dir", str(graph), "--evidence-dir", str(directory / "evidence"),
                                      "--label-selection", str(directory / "selection.parquet"), "--group-by", "disease_cluster",
                                      "--num-draws", "3", "--num-bootstrap", num_bootstrap,
                                      "--pooling-rules", "base_rate_shrunk_mean", "shared_node_weighted_mean",
                                      "--checkpoint-dir", str(directory / "draws"), *extra])
    measurement.main()


def outputs(directory: Path, name="k0") -> list[str]:
    return ["--json-output", str(directory / f"{name}.json"), "--markdown-output", str(directory / f"{name}.md")]


def test_the_pseudo_draws_are_seeds_0_to_n_minus_1_checkpointed_per_pooling_rule_and_resumed(tmp_path, monkeypatch):
    """The docstring: "The pseudo-draw seeds are 0 to --num-draws - 1"; --checkpoint-dir holds "one JSON per (pooling
    rule, draw). A draw already written here is skipped, so a run stopped by the background time limit resumes where
    it left off instead of starting over"."""
    seen = []
    run_main(monkeypatch, tmp_path, *outputs(tmp_path), recorder=seen)
    results = json.loads((tmp_path / "k0.json").read_text())
    assert results["pseudo_draw_seeds"] == [0, 1, 2] and [seed for seed, _ in seen] == [0, 1, 2, 0, 1, 2]
    for pooling_rule in ("base_rate_shrunk_mean", "shared_node_weighted_mean"):
        draws = results["pooling_rules"][pooling_rule]["draws"]
        assert [draw["draw_seed"] for draw in draws] == [0, 1, 2] and {draw["pooling_rule"] for draw in draws} == {pooling_rule}
        for seed, draw in enumerate(draws):
            assert json.loads((tmp_path / "draws" / f"{pooling_rule}_draw_{seed:03d}.json").read_text()) == draw
    checkpoint = tmp_path / "draws" / "shared_node_weighted_mean_draw_001.json"
    resumed = {**json.loads(checkpoint.read_text()), "seen_target_share": 0.123456}
    checkpoint.write_text(json.dumps(resumed))
    seen.clear()
    run_main(monkeypatch, tmp_path, *outputs(tmp_path, "again"), recorder=seen)
    assert seen == []  # every draw was checkpointed, so none is computed again
    again = json.loads((tmp_path / "again.json").read_text())
    assert again["pooling_rules"]["shared_node_weighted_mean"]["draws"][1] == resumed


def test_a_checkpoint_directory_of_another_bootstrap_count_or_other_channels_is_refused(tmp_path, monkeypatch):
    """checkpoint_inputs.json records "the inputs its draws were computed on (... the bootstrap count, the excluded
    lockbox and the channel list)", and a run whose inputs differ "refuses to resume from it"."""
    run_main(monkeypatch, tmp_path, *outputs(tmp_path))
    with pytest.raises(SystemExit, match="num_bootstrap differ"):
        run_main(monkeypatch, tmp_path, *outputs(tmp_path, "other_bootstrap"), num_bootstrap="6")
    with pytest.raises(SystemExit, match="channels differ"):
        run_main(monkeypatch, tmp_path, "--reached-node-hops", "0", "--reached-node-type-pairs", "gene:gene", "--reached-node-edges", "stored",
                 *outputs(tmp_path, "reached"))


def test_the_lockbox_perturbations_are_left_out_of_every_pseudo_draw(tmp_path, monkeypatch):
    """--lockbox: "a drawn lockbox whose perturbations are excluded, so the calibration reads development rows only"."""
    lockbox = tmp_path / "lockbox.json"
    lockbox.write_text(json.dumps({"perturbation_ids": ["d0", "g0", "g1"]}))
    seen = []
    run_main(monkeypatch, tmp_path, "--lockbox", str(lockbox), *outputs(tmp_path), recorder=seen)
    assert seen and all(not {"d0", "g0", "g1"} & set(perturbation_ids) for _, perturbation_ids in seen)
    assert all(len(perturbation_ids) == len(synthetic_data().perturbation_ids) - 3 for _, perturbation_ids in seen)
    results = json.loads((tmp_path / "k0.json").read_text())
    assert results["excluded_lockbox_perturbations"] == 3 and results["lockbox_excluded"] == str(lockbox)


# ---------------------------------------------------------------- the development rows


def test_leaving_out_the_lockbox_cuts_every_per_perturbation_field_to_the_rows_kept():
    """_restrict: "A copy of the experiment data holding only the given perturbation rows". Until 28 November 2026 it
    sliced a list of its own, which left in_metabolic_layer and five other per-perturbation fields at their full length
    while outcomes was cut; experiment_data.PER_PERTURBATION_LISTS and PER_PERTURBATION_ARRAYS name every such field."""
    data = synthetic_data()
    number_of_perturbations, number_of_symptoms = data.outcomes.shape
    seed_parts = [np.zeros(len(seed), dtype=int) for seed in data.perturbation_seeds]
    data = dataclasses.replace(
        data, in_metabolic_layer=np.arange(number_of_perturbations) % 2 == 0,
        masked_for_soft_evidence=np.arange(number_of_perturbations * number_of_symptoms).reshape(data.outcomes.shape) % 3 == 0,
        evidenced_negative_power=np.arange(number_of_perturbations * number_of_symptoms, dtype=float).reshape(data.outcomes.shape),
        perturbation_target_seeds=[seed + 100 for seed in data.perturbation_seeds],
        perturbation_parts=[[f"part of {identifier}"] for identifier in data.perturbation_ids], perturbation_seed_parts=seed_parts)
    kept_rows = [row for row in range(number_of_perturbations) if row % 3 != 1]
    restricted = measurement._restrict(data, kept_rows)
    for name in PER_PERTURBATION_LISTS + ("perturbation_target_seeds", "perturbation_parts", "perturbation_seed_parts"):
        kept_values, expected_values = getattr(restricted, name), [getattr(data, name)[row] for row in kept_rows]
        assert len(kept_values) == len(kept_rows), name
        for kept_value, expected_value in zip(kept_values, expected_values):
            np.testing.assert_array_equal(kept_value, expected_value)
    for name in PER_PERTURBATION_ARRAYS:
        if getattr(data, name) is None:
            assert getattr(restricted, name) is None, name
        else:
            np.testing.assert_array_equal(getattr(restricted, name), np.asarray(getattr(data, name))[kept_rows], err_msg=name)
    assert restricted.node_ids == data.node_ids and restricted.edge_source is data.edge_source


# ---------------------------------------------------------------- added by the checker of the same day
# Mutants written by the checker (not among the 306 of the report) that every test above let survive: the adversary
# scored with the default pooling rule whatever rule was asked for, the micro reading stored from the macro one, type
# popularity read as plain popularity, degree-scaled popularity given other rows' degrees, and a summary over the
# unusable draws as well.


def held_out_and_training_rows(data, seed):
    held_out_ids, _ = measurement.registered_two_sided_draw(data, seed)
    held_out = [identifier for identifier in data.perturbation_ids if identifier in held_out_ids]
    training = [identifier for identifier in data.perturbation_ids if identifier not in held_out_ids]
    return (held_out, training, np.array([data.perturbation_ids.index(identifier) for identifier in held_out]),
            np.array([data.perturbation_ids.index(identifier) for identifier in training]))


def data_with_degrees_and_type_rates():
    """synthetic_data with seed degrees that differ between perturbations and drugs positive more often than genes, so
    that popularity, degree-scaled popularity and type popularity order the held-out rows three different ways."""
    data = synthetic_data()
    generator = np.random.default_rng(11)
    is_drug = np.array([kind == "drug" for kind in data.perturbation_types])
    outcomes = (generator.random(data.outcomes.shape) < np.where(is_drug, 0.6, 0.25)[:, None]).astype(float)
    return dataclasses.replace(data, node_degree=np.arange(1.0, len(data.node_ids) + 1.0), outcomes=outcomes, weights=outcomes)


@pytest.mark.parametrize("pooling_rule", POOLING_RULES)
def test_a_draw_scores_the_adversary_with_the_pooling_rule_it_is_given(pooling_rule):
    """one_draw takes the pooling rule, main writes one set of draws per --pooling-rules entry, and
    experiments/calibrate_leakage_ceiling.py fits the draws of the --pooling-rule it is given, "the adversary is meant
    to be the strongest lookup, which is a reading across them": so a rule's draws are that rule's adversary."""
    data = data_with_degrees_and_type_rates()
    seed = 100
    held_out, training, held_rows, training_rows = held_out_and_training_rows(data, seed)
    neighbours = neighbours_through_the_channels(held_out, training, seed_nodes_of_perturbations(data.perturbation_ids, data.perturbation_seeds,
                                                                                                data.node_ids))
    macro = macro_statistic()

    def macro_auprc_of(rule):
        adversary = LeakageOnlyAdversary(rule).fit(training, data.outcomes[training_rows], data.label_mask[training_rows])
        return float(macro(adversary.predict(held_out, neighbours), data.outcomes[held_rows], data.label_mask[held_rows]))

    by_rule = {rule: macro_auprc_of(rule) for rule in POOLING_RULES}
    assert len({round(value, 12) for value in by_rule.values()}) == len(POOLING_RULES)  # the three rules part on this draw
    draw = measurement.one_draw(data, seed, pooling_rule, 5)
    assert draw["pooling_rule"] == pooling_rule and draw["adversary_macro_auprc"] == pytest.approx(by_rule[pooling_rule])


def test_each_advantage_is_the_adversary_against_that_baseline_on_the_held_out_rows():
    """The module docstring: the adversary's "advantage over each registered baseline is read in macro and micro AUPRC
    with the paired bootstrap"; one_draw: over "popularity, degree-scaled popularity and type popularity", type
    popularity being fitted on the training rows of each held-out row's own type (the comparator the pooled reading
    needs) and degree-scaled popularity scaling each held-out row by its own seed degree."""
    data = data_with_degrees_and_type_rates()
    seed = 100
    held_out, training, held_rows, training_rows = held_out_and_training_rows(data, seed)
    neighbours = neighbours_through_the_channels(held_out, training, seed_nodes_of_perturbations(data.perturbation_ids, data.perturbation_seeds,
                                                                                                data.node_ids))
    adversary_scores = LeakageOnlyAdversary().fit(training, data.outcomes[training_rows], data.label_mask[training_rows]).predict(held_out, neighbours)
    outcomes_held, mask_held = data.outcomes[held_rows], data.label_mask[held_rows]
    outcomes_training, mask_training = data.outcomes[training_rows], data.label_mask[training_rows]

    def seed_degrees(rows):
        return np.array([float(data.node_degree[data.perturbation_seeds[row]].sum()) for row in rows])

    kinds_training, kinds_held = np.array(data.perturbation_types)[training_rows], np.array(data.perturbation_types)[held_rows]
    type_scores = np.zeros(outcomes_held.shape)
    for kind in set(kinds_held.tolist()):
        fitted = PopularityBaseline().fit(outcomes_training[kinds_training == kind], None, mask_training[kinds_training == kind])
        type_scores[kinds_held == kind] = fitted.predict(int((kinds_held == kind).sum()))
    baselines = {"popularity": PopularityBaseline().fit(outcomes_training, None, mask_training).predict(len(held_rows)),
                 "degree_popularity": PopularityBaseline(scale_by_degree=True).fit(outcomes_training, seed_degrees(training_rows), mask_training)
                 .predict(len(held_rows), seed_degrees(held_rows)),
                 "type_popularity": type_scores}

    draw = measurement.one_draw(data, seed, "base_rate_shrunk_mean", 5)
    for name, baseline_scores in baselines.items():
        expected_macro = paired_bootstrap_macro_difference(adversary_scores, baseline_scores, outcomes_held, num_bootstrap=1, mask=mask_held)
        expected_micro = paired_bootstrap_micro_difference(adversary_scores, baseline_scores, outcomes_held, num_bootstrap=1, mask=mask_held)
        assert draw[f"macro_advantage_over_{name}"] == pytest.approx(expected_macro["difference"]), name
        assert draw[f"micro_advantage_over_{name}"] == pytest.approx(expected_micro["difference"]), name
    # the readings differ here, so a draw that read one baseline or one metric in place of another fails above
    assert len({round(draw[f"{metric}_advantage_over_{name}"], 12) for name in baselines for metric in ("macro", "micro")}) == 6


def test_the_summary_is_over_the_usable_draws_only():
    """summarise: "Means and ranges over the usable draws, per reading"."""
    draws = [{"draw_seed": 0, "usable": False},
             {"draw_seed": 1, "usable": True, "seen_target_share": 0.25},
             {"draw_seed": 2, "usable": True, "seen_target_share": 0.75}]
    summary = measurement.summarise(draws)
    assert summary["usable_draws"] == 2
    assert summary["seen_target_share"] == {"mean": 0.5, "minimum": 0.25, "maximum": 0.75, "draws": 2}
