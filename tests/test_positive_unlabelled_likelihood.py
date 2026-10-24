"""The labels' positive-unlabelled likelihood (decision 9.90; models/positive_unlabelled_likelihood.py): the plain binary
cross-entropy at full propensity and no false reports, finite and correctly signed gradients, a cheap unlabelled pair
at a small propensity, the module-size criterion on the counted-once code lengths, every pair weighing 1 in the trainer
with the edge priors' W equal to the number of counted pairs, and the weighted loss untouched while the flag is off."""
from __future__ import annotations

import json
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from experiments.run_main_model import (
    LABEL_LIKELIHOOD_SETTINGS,
    VALUES_BEFORE_THE_V4_DEFAULTS,
    build_argument_parser,
    configuration_fingerprint,
    label_likelihood_labels,
    loss_pair_weights,
    refuse_what_the_likelihood_does_not_define,
    weighted_constant_optimum,
)
from mechanistic_pathway_learning.models.minimum_description_length_selection import (
    CandidateDescriptionLength,
    candidate_description_length,
    data_cost_nats,
    select_minimum_description_length,
)
from mechanistic_pathway_learning.models.positive_unlabelled_likelihood import (
    LabellingPropensity,
    assessment_power_matrix,
    constant_optimum,
    derived_propensity,
    labelled_shares_by_type,
    pair_code_lengths,
    popularity_of_perturbations,
    positive_unlabelled_binary_cross_entropy,
)
from mechanistic_pathway_learning.models.soft_constraint_losses import evidence_weighted_binary_cross_entropy
from tests.test_edge_priors_in_the_trainer import write_edge_evidence
from tests.test_soft_priors_in_the_trainer import write_toy_dataset

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def kinds(num_pairs: int = 9) -> tuple[torch.Tensor, torch.Tensor]:
    """A third of the pairs labelled positive, a third evidenced negatives, a third unlabelled."""
    positive = torch.tensor([float(index % 3 == 0) for index in range(num_pairs)])
    negative = torch.tensor([float(index % 3 == 1) for index in range(num_pairs)])
    return positive, negative


def scalar(value: float) -> torch.Tensor:
    return torch.tensor(value, dtype=torch.float32)


@pytest.mark.parametrize("in_log_space", [False, True])
def test_at_full_propensity_and_no_false_reports_it_is_the_plain_unweighted_cross_entropy(in_log_space):
    probability = torch.linspace(0.02, 0.97, 9)
    positive, negative = kinds()
    log_parts = {"log_probability": torch.log(probability), "log_complement": torch.log1p(-probability)} if in_log_space else {}
    likelihood = positive_unlabelled_binary_cross_entropy(probability, positive, negative, torch.ones(9), scalar(1.0), scalar(0.0), torch.ones(9), **log_parts)
    plain = torch.nn.functional.binary_cross_entropy(probability, positive)  # an evidenced negative at power 1 is an ordinary negative
    assert likelihood.item() == pytest.approx(plain.item(), rel=1e-6)
    # and the per-pair lengths are the per-pair cross-entropies, unlabelled pairs included
    lengths = pair_code_lengths(probability, positive, torch.zeros(9), scalar(1.0), scalar(0.0), torch.zeros(9), **log_parts)
    assert torch.allclose(lengths, torch.nn.functional.binary_cross_entropy(probability, positive, reduction="none"), rtol=1e-6)


@pytest.mark.parametrize("in_log_space", [False, True])
@pytest.mark.parametrize("false_report_rate", [0.0, 0.03])
def test_gradients_are_finite_and_a_label_pulls_up_while_silence_and_an_assessed_absence_push_down(in_log_space, false_report_rate):
    probability = torch.tensor([1e-7, 1e-4, 0.01, 0.3, 0.7, 0.99, 1.0 - 1e-6], dtype=torch.float32)
    for kind in ("positive", "unlabelled", "negative"):
        logit = torch.logit(probability.clamp(1e-7, 1 - 1e-7)).double().float().requires_grad_(True)
        slope = torch.zeros((), requires_grad=True)
        f = torch.sigmoid(logit)
        propensity = torch.sigmoid(torch.logit(scalar(0.2)) + slope * torch.linspace(-1, 1, len(f)))
        log_parts = {"log_probability": torch.nn.functional.logsigmoid(logit), "log_complement": torch.nn.functional.logsigmoid(-logit)} if in_log_space else {}
        ones, zeros = torch.ones_like(f), torch.zeros_like(f)
        length = pair_code_lengths(f, ones if kind == "positive" else zeros, ones if kind == "negative" else zeros, propensity, scalar(false_report_rate),
                                   torch.full_like(f, 0.9), **log_parts)
        length.sum().backward()
        assert torch.isfinite(length).all() and torch.isfinite(logit.grad).all() and torch.isfinite(slope.grad), kind
        inside = (f > 2e-6) & (f < 1 - 2e-6)  # beyond the clamp the plain path has no gradient, as the weighted loss has none
        if in_log_space:
            inside = torch.ones_like(inside)
        if kind == "positive":
            assert (logit.grad[inside] < 0).all(), "descending the loss raises f for a labelled pair"
        else:
            assert (logit.grad[inside] > 0).all(), f"descending the loss lowers f for an {kind} pair"


def test_an_unlabelled_pair_costs_little_at_a_small_propensity_and_its_cost_is_bounded():
    probability = torch.tensor([0.0, 0.5, 0.999999])
    unlabelled = torch.zeros(3)
    for propensity in (0.01, 0.05, 0.2):
        lengths = pair_code_lengths(probability, unlabelled, unlabelled, scalar(propensity), scalar(0.0), unlabelled)
        assert (lengths <= -np.log1p(-propensity) + 1e-6).all(), "never more than -log(1 - pi), however sure the model is of the link"
    small = pair_code_lengths(probability, unlabelled, unlabelled, scalar(0.01), scalar(0.0), unlabelled)
    assert small.max().item() < 0.0101
    weighted = evidence_weighted_binary_cross_entropy(torch.tensor([0.999999]), torch.zeros(1), torch.tensor([0.2]))
    assert weighted.item() > 2.0, "the weighted negative grows without bound as f approaches 1"


def test_the_channel_is_e_f_plus_b_times_one_minus_f_and_the_false_report_rate_bounds_a_label():
    probability = torch.tensor([1e-6, 0.1, 0.6])
    propensity, rate = 0.3, 0.02
    efficiency = rate + (1 - rate) * propensity  # e = P(labelled | real)
    positive = pair_code_lengths(probability, torch.ones(3), torch.zeros(3), scalar(propensity), scalar(rate), torch.zeros(3))
    assert torch.allclose(positive, -torch.log(efficiency * probability + rate * (1 - probability)), rtol=1e-5)
    assert positive.max().item() <= -np.log(rate) + 1e-6
    unlabelled = pair_code_lengths(probability, torch.zeros(3), torch.zeros(3), scalar(propensity), scalar(rate), torch.zeros(3))
    assert torch.allclose(torch.exp(-positive) + torch.exp(-unlabelled), torch.ones(3), atol=1e-6), "labelled and unlabelled are the two outcomes"


def test_the_constant_optimum_is_the_share_labelled_over_the_propensity():
    labelled = np.zeros((50, 2))
    labelled[:5, 0] = 1  # r = 0.1
    labelled[:15, 1] = 1  # r = 0.3, above the propensity: f stops at 1
    optimum = constant_optimum(labelled, np.zeros_like(labelled), np.ones_like(labelled), np.full((50, 1), 0.2), np.zeros((50, 1)), np.zeros_like(labelled))
    assert optimum[0] == pytest.approx(0.5, abs=1e-6) and optimum[1] == pytest.approx(1.0, abs=1e-5)
    # with an evidenced negative and a false-report rate the root is still the minimum of the summed code length
    negative = np.zeros((50, 2))
    negative[40:45] = 1
    grid = np.linspace(0.001, 0.999, 999)
    lengths = [pair_code_lengths(torch.full((50, 2), float(f)), torch.as_tensor(labelled), torch.as_tensor(negative), torch.full((50, 1), 0.2),
                                 torch.full((50, 1), 0.01), torch.full((50, 2), 0.6)).sum(dim=0).numpy() for f in grid]
    found = constant_optimum(labelled, negative, np.ones_like(labelled), np.full((50, 1), 0.2), np.full((50, 1), 0.01), np.full((50, 2), 0.6))
    assert found[0] == pytest.approx(grid[np.argmin([length[0] for length in lengths])], abs=2e-3)


def test_the_module_size_criterion_counts_each_label_once():
    """Design section 5.5 as amended by decision 9.90: the data cost is the summed counted-once code length, so a
    candidate's total moves with the likelihood and a set-aside pair adds nothing."""
    probability = torch.tensor([[0.9, 0.2, 0.6], [0.1, 0.05, 0.3]])
    positive = torch.tensor([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    weights = np.array([[1.0, 1.0, 0.0], [1.0, 1.0, 1.0]])  # one pair set aside
    lengths = pair_code_lengths(probability, positive, torch.zeros_like(positive), scalar(0.2), scalar(0.0), torch.zeros_like(positive)).numpy()
    expected = -(np.log(0.2 * 0.9) + np.log1p(-0.2 * 0.2) + np.log1p(-0.2 * 0.1) + np.log1p(-0.2 * 0.05) + np.log(0.2 * 0.3))
    assert data_cost_nats(lengths, weights) == pytest.approx(expected, rel=1e-5)
    candidate = candidate_description_length(4, 10.0, lengths, weights)
    assert candidate.total_nats == pytest.approx(10.0 + expected, rel=1e-6)
    # the weighted negative log-likelihood would count each silence at 0.2 and each label at its evidence weight
    weighted_lengths = torch.nn.functional.binary_cross_entropy(probability, positive, reduction="none").numpy()
    weighted_weights = np.where(positive.numpy() > 0, 0.6, 0.2) * (weights > 0)
    assert data_cost_nats(weighted_lengths, weighted_weights) != pytest.approx(candidate.data_cost_nats)
    smaller_model = CandidateDescriptionLength(2, 10.0 + expected - 1.0, 0.0)
    assert select_minimum_description_length([candidate, smaller_model]) is smaller_model
    with pytest.raises(ValueError, match="infinite"):
        data_cost_nats(np.array([np.inf, 1.0]), np.array([1.0, 1.0]))


def small_data(with_negatives: bool = True) -> Namespace:
    generator = np.random.default_rng(3)
    outcomes = (generator.random((10, 4)) < 0.3).astype(float)
    evidenced = (generator.random(outcomes.shape) < 0.2) & (outcomes == 0)
    return Namespace(outcomes=outcomes, weights=np.where(outcomes > 0, generator.uniform(0.15, 1.0, outcomes.shape), 0.0),
                     perturbation_types=["drug"] * 6 + ["gene"] * 4, perturbation_ids=[f"P{index}" for index in range(10)],
                     evidenced_negative=evidenced if with_negatives else None, placebo_negative_weight_matrix=None, symptoms=list("abcd"))


def likelihood_arguments(**changes) -> Namespace:
    arguments = build_argument_parser().parse_args(["--graph-dir", "g", "--evidence-dir", "e", "--label-likelihood", "positive_unlabelled",
                                                    "--no-equal-drug-shares"])
    for name, value in changes.items():
        setattr(arguments, name, value)
    return arguments


def test_every_counted_pair_weighs_one_and_the_drug_shares_keep_the_count():
    data = small_data()
    label_mask = np.ones_like(data.outcomes, dtype=bool)
    label_mask[0, 0] = False
    counted = loss_pair_weights(data, label_mask, likelihood_arguments(), np.arange(8))
    assert np.array_equal(counted, label_mask.astype(float)), "no evidence weight, no 0.2, no placebo weight: one observation each"
    shared = loss_pair_weights(data, label_mask, likelihood_arguments(equal_drug_shares=True), np.arange(8))
    assert shared[np.arange(8)].sum() == pytest.approx(counted[np.arange(8)].sum()), "the shares move weight between drugs and keep W = N"
    assert np.array_equal(shared[6:], counted[6:]), "gene rows are left as they are"


def test_the_power_of_an_evidenced_negative_comes_from_the_source_then_the_placebo_file_then_the_default():
    evidenced = np.array([[True, True, True, False]])
    stated = np.array([[0.95, np.nan, np.nan, 0.5]])
    placebo = np.array([[0.3, 0.4, np.nan, np.nan]])
    power, counts = assessment_power_matrix(evidenced, stated, placebo, 0.5)
    assert power.tolist() == [[0.95, 0.4, 0.5, 0.0]]
    assert counts == {"stated_by_the_source": 1, "placebo_weight_file": 1, "default": 1}
    with pytest.raises(ValueError, match="power"):
        assessment_power_matrix(evidenced, np.array([[1.5, np.nan, np.nan, np.nan]]), None, 0.5)


def test_the_labels_read_a_power_matrix_a_parallel_source_writes_beside_the_evidenced_negatives():
    data = small_data()
    rows, columns = np.nonzero(data.evidenced_negative)
    data.evidenced_negative_power = np.full(data.outcomes.shape, np.nan)
    data.evidenced_negative_power[rows[0], columns[0]] = 0.97  # k observed of n assessed, from a source of its own
    labels, _, summary = label_likelihood_labels(data, None, likelihood_arguments(), np.arange(10))
    assert labels.assessment_power[rows[0], columns[0]].item() == pytest.approx(0.97)
    assert summary["evidenced_negative_power"]["stated_by_the_source"] == 1
    assert summary["evidenced_negative_power"]["default"] == len(rows) - 1
    groups = summary["groups_on_the_fit_rows"]
    assert groups["evidenced_negative"]["pairs"] == len(rows) and groups["total_weight"]["counted_once"] == data.outcomes.size
    assert label_likelihood_labels(data, None, likelihood_arguments(label_likelihood="weighted"), np.arange(10)) == (None, None, None)


def test_the_propensity_has_one_learned_slope_on_popularity_and_none_without_it():
    reports = pd.DataFrame({"perturbation_id": ["G1", "G1", "G2", "D1", "G3"], "pmid": ["1", "2", "3", "4", None],
                            "evidence_class": ["literature"] * 4 + ["literature"]})
    popularity = popularity_of_perturbations(["G1", "G2|gain", "D1+G9", "G4"], reports, slot_ids=["G1", "G2|gain", "D1", "G4"])
    assert popularity.tolist() == [2.0, 1.0, 1.0, 0.0], "an allele takes its gene's papers and a combination its drug's"
    anchors = np.array([0.3, 0.3, 0.7, 0.3])  # a drug row and three gene rows
    propensity = LabellingPropensity(anchors, np.log1p(popularity), centre=float(np.median(np.log1p(popularity))))
    assert sum(parameter.numel() for parameter in propensity.parameters()) == 1
    assert torch.allclose(propensity(np.arange(4)), torch.as_tensor(anchors, dtype=torch.float32)[:, None]), "the slope starts at 0: the fit starts at pi_0"
    with torch.no_grad():
        propensity.popularity_slope.fill_(1.0)
    moved = propensity(np.arange(4))[:, 0]
    assert moved[0] > 0.3 and moved[3] < 0.3, "a more popular perturbation is labelled more often at a positive slope"
    assert sum(parameter.numel() for parameter in LabellingPropensity(anchors).parameters()) == 0
    with pytest.raises(ValueError, match="propensity"):
        LabellingPropensity(np.array([0.2, 1.0]))


def test_the_derived_propensity_is_above_every_labelled_share_and_keeps_every_cells_weighted_optimum():
    outcomes = np.zeros((10, 3))
    outcomes[:7, 0] = 1  # the drugs' most-labelled symptom: 7 of 8 rows
    outcomes[:2, 1] = 1
    outcomes[8:, 2] = [1, 0]  # the genes: one of two
    types = ["drug"] * 8 + ["gene"] * 2
    shares = labelled_shares_by_type(outcomes, None, types, np.arange(10))
    assert np.allclose(shares["drug"], [7 / 8, 2 / 8, 0.0]) and np.allclose(shares["gene"], [0.0, 0.0, 0.5])
    by_cell = derived_propensity(shares, 0.2)
    assert all((by_cell[kind] > shares[kind]).all() for kind in by_cell), "no propensity below a labelled share can produce it"
    assert by_cell["drug"][2] == pytest.approx(0.2), "rare labels: the registered negative weight"
    for column in range(2):  # every drug cell keeps the registered weighted optimum r / (r + w (1 - r)), below 1
        share = shares["drug"][column]
        optimum = constant_optimum(outcomes[:8, column:column + 1], np.zeros((8, 1)), np.ones((8, 1)), np.full((8, 1), by_cell["drug"][column]),
                                   np.zeros((8, 1)), np.zeros((8, 1)))
        assert optimum[0] == pytest.approx(share / (share + 0.2 * (1 - share)), abs=1e-6)
    by_type = derived_propensity(shares, 0.2, by_symptom=False)
    assert np.allclose(by_type["drug"], 0.2 + 0.8 * 7 / 8) and np.allclose(by_type["gene"], 0.2 + 0.8 * 0.5), "one value per type, set by its top symptom"


def test_the_start_is_the_counted_once_optimum_under_the_likelihood():
    data = small_data(with_negatives=False)
    arguments = likelihood_arguments(start_at_weighted_optimum=True, head="noisy_or", labelling_propensity=0.6)
    labels, _, _ = label_likelihood_labels(data, None, arguments, np.arange(10))
    start = weighted_constant_optimum(data, np.arange(10), None, arguments, labels)
    share = data.outcomes.mean(axis=0)
    assert np.allclose(start, share / 0.6, atol=1e-5)


def test_the_flag_and_its_settings_stay_out_of_the_fingerprint_while_it_is_off():
    data = Namespace(outcomes=np.zeros((2, 2)), weights=np.zeros((2, 2)), edge_source=np.array([0]), edge_target=np.array([1]), edge_relation=np.array([0]),
                     perturbation_seeds=[np.array([0]), np.array([1])], perturbation_signs=[np.array([-1.0])] * 2, perturbation_magnitudes=[np.array([1.0])] * 2)
    off = configuration_fingerprint(build_argument_parser().parse_args(["--graph-dir", "g", "--evidence-dir", "e", "--label-likelihood", "weighted",
                                                                         "--labelling-propensity", "0.4"]), data, None)
    assert not any(key.split(":", 1)[1] in LABEL_LIKELIHOOD_SETTINGS | {"label_likelihood"} for key in off if key.startswith("argument:"))
    on = configuration_fingerprint(likelihood_arguments(), data, None)
    assert on["argument:label_likelihood"] == "positive_unlabelled" and on["argument:labelling_propensity"] == "derived"
    assert VALUES_BEFORE_THE_V4_DEFAULTS["label_likelihood"] == "weighted"


def test_what_the_likelihood_does_not_define_is_refused():
    with pytest.raises(ValueError, match="soft prior"):
        refuse_what_the_likelihood_does_not_define(likelihood_arguments(soft_prior_strength=1.0))
    with pytest.raises(ValueError, match="frequency"):
        refuse_what_the_likelihood_does_not_define(likelihood_arguments(positive_target_from_frequency=True))
    with pytest.raises(ValueError, match="TYPE=RATE"):
        refuse_what_the_likelihood_does_not_define(likelihood_arguments(false_report_rate=["drug"]))
    with pytest.raises(ValueError, match="false-report rate"):
        refuse_what_the_likelihood_does_not_define(likelihood_arguments(false_report_rate=["drug=1.0"]))
    refuse_what_the_likelihood_does_not_define(likelihood_arguments(label_likelihood="weighted", soft_prior_strength=1.0))  # the weighted loss is untouched


def run_trainer(paths: dict[str, Path], run_directory: Path, *extra: str) -> dict:
    command = [sys.executable, "experiments/run_main_model.py", "--graph-dir", str(paths["graph"]), "--evidence-dir", str(paths["evidence"]), "--run-dir", str(run_directory),
               "--encoder", "linear_response", "--normalisation", "total_in_degree", "--max-epochs", "2", "--num-bootstrap", "3", "--refit-on-validation",
               "--validation-fraction", "0.3", "--no-keep-large-groups-in-training", "--fold", "0", "--seed", "0", "--batch-size", "8",
               "--placebo-negative-weights-file", str(paths["placebo"]), "--group-by", "disease_cluster", "--label-selection", str(paths["selection"]), *extra]
    completed = subprocess.run(command, cwd=REPOSITORY_ROOT, capture_output=True, text=True, env={"PYTHONPATH": ".", "PATH": "/usr/bin:/bin:/usr/local/bin", "OMP_NUM_THREADS": "1"})
    assert completed.returncode == 0, completed.stderr[-3000:]
    split_directory = next(path for path in run_directory.iterdir() if path.is_dir())
    return {"directory": split_directory, "results": json.loads((split_directory / "results.json").read_text()),
            "predictions": np.load(split_directory / "test_predictions.npy")}


def toy_with_evidenced_negatives(root: Path) -> dict[str, Path]:
    """The toy data set of the soft-prior tests with every ninth kept positive relabelled as a never-above-placebo
    negative, and a placebo weight file naming half of them."""
    paths = write_toy_dataset(root)
    write_edge_evidence(paths["graph"])
    selection = pd.read_parquet(paths["selection"])
    relabelled = selection.index[selection.keep & ~selection.masks_a_negative][::9]
    selection["counts_as_negative"] = False
    selection.loc[relabelled, ["keep", "counts_as_negative"]] = [False, True]
    selection.to_parquet(paths["selection"], index=False)
    paths["placebo"] = root / "placebo.csv"
    pd.DataFrame({"perturbation_id": selection.perturbation_id[relabelled[::2]], "symptom": selection.symptom[relabelled[::2]], "weight": 0.37}).to_csv(paths["placebo"], index=False)
    return paths


def test_end_to_end_off_is_the_weighted_run_and_on_it_trains_counts_each_pair_once_and_records_its_description_length(tmp_path):
    paths = toy_with_evidenced_negatives(tmp_path)
    plain = run_trainer(paths, tmp_path / "plain", "--label-likelihood", "weighted")
    off = run_trainer(paths, tmp_path / "off", "--label-likelihood", "weighted", "--labelling-propensity", "0.4", "--false-report-rate", "gene=0.3",
                      "--propensity-popularity-reports", str(paths["reports"]))
    assert np.array_equal(plain["predictions"], off["predictions"]), "the likelihood's settings do nothing while it is off"
    assert plain["results"]["configuration_fingerprint"] == off["results"]["configuration_fingerprint"]
    assert "label_likelihood" not in plain["results"] and plain["results"]["arguments"]["label_likelihood"] == "weighted"

    on = run_trainer(paths, tmp_path / "on", "--label-likelihood", "positive_unlabelled", "--propensity-popularity-reports", str(paths["reports"]),
                     "--false-report-rate", "gene=0.01", "--edge-prior-strength", "1.0", "--edge-gate-kind", "soft", "--edge-gate-learning-rate", "0.05")
    record = on["results"]["label_likelihood"]
    assert np.isfinite(on["predictions"]).all() and not np.array_equal(on["predictions"], plain["predictions"])
    assert all(np.isfinite(entry["train_loss"]) and np.isfinite(entry["validation_loss"]) for entry in on["results"]["history"])
    assert record["evidenced_negative_power"]["placebo_weight_file"] > 0 and record["evidenced_negative_power"]["default"] > 0
    assert record["false_report_rate_by_type"] == {"gene": 0.01}
    assert record["propensity"]["learned_parameters"] == 1 and record["propensity"]["popularity_slope"] != 0.0, "the slope trains with the model"
    anchor = record["propensity_anchor"]
    assert anchor["at_the_median_popularity_by_type"]["gene"]["max"] > anchor["largest_labelled_share_by_type"]["gene"]["share"] > 0.2, \
        "the toy's labelled shares are above 0.2, which a propensity of 0.2 could not produce"
    groups = record["groups_on_the_fit_rows"]
    assert {groups[kind]["counted_once_weight"] for kind in ("labelled_positive", "unlabelled", "evidenced_negative")} \
        == {float(groups[kind]["pairs"]) for kind in ("labelled_positive", "unlabelled", "evidenced_negative")}
    # W, the edge priors' divisor, is the number of counted pairs on the fit rows: the data and the prior are both in nats per pair
    assert on["results"]["edge_priors"]["penalty_denominator"]["fit"] == pytest.approx(groups["total_weight"]["counted_once"])
    description = record["description_length"]
    assert description["total_nats"] == pytest.approx(description["model_cost_nats"] + description["data_cost_nats"], abs=2e-3)
    assert description["summed_pair_weight"] == description["counted_pairs"] and description["data_cost_nats"] > 0
    assert len(on["results"]["configuration_fingerprint"]["file:propensity_popularity_reports"]) == 64
