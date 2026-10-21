"""Tests for the entmax weighting of the cross-relation mixture (linear_response_encoder.entmax) and its annealing to
sparsemax in the trainer (experiments/run_main_model.py, apply_entmax_schedule): entmax is sparsemax exactly at
exponent 2 and tends to softmax as the exponent falls to 1, its hand-written backward pass is the exact Jacobian, it
keeps a gradient on a statistic sparsemax has dropped, and an annealed run keeps only a model trained at sparsemax."""
from argparse import Namespace

import pytest
import torch

from experiments.run_main_model import apply_entmax_schedule, refuse_an_entmax_setting_that_cannot_act
from mechanistic_pathway_learning.models.linear_response_encoder import (
    DEFAULT_MIXTURE_ENTMAX_EXPONENT,
    MIXTURE_EXPONENT_SPARSEMAX,
    MIXTURE_STATISTICS,
    CrossRelationAggregator,
    entmax,
    entmax_exponent_for_epoch,
    project_onto_simplex,
)
from tests.test_edge_priors_in_the_trainer import run_trainer
from tests.test_soft_priors_in_the_trainer import write_toy_dataset


def random_logits(seed: int = 0) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    return torch.randn(3, len(MIXTURE_STATISTICS), 4, generator=generator, dtype=torch.float64)


def test_entmax_at_exponent_two_is_sparsemax_exactly():
    logits = random_logits()
    assert torch.allclose(entmax(logits, MIXTURE_EXPONENT_SPARSEMAX, dim=1), project_onto_simplex(logits, dim=1), atol=1e-12)


def test_entmax_approaches_softmax_as_the_exponent_falls_towards_one():
    logits = random_logits()
    distances_from_softmax = [float((entmax(logits, exponent, dim=1) - torch.softmax(logits, dim=1)).abs().max())
                              for exponent in (1.5, 1.1, 1.05, 1.02)]
    assert distances_from_softmax == sorted(distances_from_softmax, reverse=True), distances_from_softmax
    assert distances_from_softmax[-1] < 0.02


@pytest.mark.parametrize("exponent", [1.2, 1.5, 1.9, 2.0])
def test_entmax_weights_lie_on_the_simplex_and_its_backward_pass_is_the_exact_jacobian(exponent):
    logits = random_logits()
    weights = entmax(logits, exponent, dim=1)
    assert (weights >= 0).all() and torch.allclose(weights.sum(dim=1), torch.ones(3, 4, dtype=torch.float64))
    leaf = logits.clone().requires_grad_(True)
    assert torch.autograd.gradcheck(lambda logit: entmax(logit, exponent, dim=1), (leaf,), eps=1e-6, atol=1e-5)


def test_entmax_keeps_a_statistic_and_its_gradient_that_sparsemax_drops():
    """The reason entmax is offered: a statistic outside sparsemax's support has exactly zero weight and zero gradient,
    so it can never come back; at a lower exponent the same logits keep it inside the support."""
    logits = torch.tensor([[1.0, 0.2, 0.0]], dtype=torch.float64)
    assert float(project_onto_simplex(logits, dim=1)[0, 2]) == 0.0
    leaf = logits.clone().requires_grad_(True)
    weights = entmax(leaf, 1.5, dim=1)
    assert float(weights[0, 2].detach()) > 0.0
    weights[0, 2].backward()
    assert float(leaf.grad[0, 2]) > 0.0


@pytest.mark.parametrize("exponent", [1.1, 1.5, 2.0])
def test_the_entmax_warm_start_puts_the_requested_weight_on_the_mean(exponent):
    requested_mean_weight = 0.9
    aggregator = CrossRelationAggregator(num_node_types=2, propagation_channels=3, weighting="entmax",
                                         initial_mean_weight=requested_mean_weight, entmax_exponent=exponent)
    weight = aggregator.simplex_weight()
    mean_position = MIXTURE_STATISTICS.index("mean")
    assert torch.allclose(weight[:, mean_position, :], torch.full_like(weight[:, mean_position, :], requested_mean_weight), atol=1e-6)


def test_entmax_exponents_outside_the_open_closed_interval_are_refused():
    with pytest.raises(ValueError, match="entmax"):
        CrossRelationAggregator(num_node_types=1, propagation_channels=1, weighting="entmax", entmax_exponent=1.0)
    with pytest.raises(ValueError, match="entmax"):
        CrossRelationAggregator(num_node_types=1, propagation_channels=1, weighting="entmax", entmax_exponent=2.5)
    with pytest.raises(ValueError, match="only the entmax weighting"):
        CrossRelationAggregator(num_node_types=1, propagation_channels=1, weighting="sparsemax").set_entmax_exponent(1.5)


def test_the_anneal_starts_at_the_given_exponent_and_reaches_sparsemax_exactly_at_its_last_epoch():
    assert [entmax_exponent_for_epoch(1.5, 4, epoch) for epoch in range(6)] == [1.5, 1.625, 1.75, 1.875, 2.0, 2.0]
    assert [entmax_exponent_for_epoch(1.3, 0, epoch) for epoch in range(3)] == [1.3, 1.3, 1.3]


def trainer_arguments(**overrides) -> Namespace:
    values = {"encoder": "linear_response", "cross_relation_aggregator": "softmax_mixture", "mixture_weighting": "entmax",
              "mixture_entmax_exponent": DEFAULT_MIXTURE_ENTMAX_EXPONENT, "mixture_entmax_anneal_epochs": 0, "max_epochs": 10}
    return Namespace(**{**values, **overrides})


def test_entmax_options_that_would_do_nothing_are_refused():
    with pytest.raises(ValueError, match="act only with"):
        refuse_an_entmax_setting_that_cannot_act(trainer_arguments(mixture_weighting="sparsemax", mixture_entmax_anneal_epochs=3))
    with pytest.raises(ValueError, match="act only with"):
        refuse_an_entmax_setting_that_cannot_act(trainer_arguments(cross_relation_aggregator="mean", mixture_entmax_exponent=1.2))
    with pytest.raises(ValueError, match="must be below --max-epochs"):
        refuse_an_entmax_setting_that_cannot_act(trainer_arguments(mixture_entmax_anneal_epochs=10))
    refuse_an_entmax_setting_that_cannot_act(trainer_arguments(mixture_entmax_anneal_epochs=9))
    refuse_an_entmax_setting_that_cannot_act(trainer_arguments(mixture_weighting="sparsemax"))  # defaults left alone pass


def test_the_schedule_is_applied_to_an_entmax_mixture_and_skipped_elsewhere():
    class EncoderWithMixture(torch.nn.Module):
        def __init__(self, weighting):
            super().__init__()
            self.cross_relation_mixture = CrossRelationAggregator(num_node_types=1, propagation_channels=1, weighting=weighting)
    entmax_encoder = EncoderWithMixture("entmax")
    assert apply_entmax_schedule(entmax_encoder, trainer_arguments(mixture_entmax_anneal_epochs=2), epoch=1) == 1.75
    assert entmax_encoder.cross_relation_mixture.entmax_exponent == 1.75
    assert apply_entmax_schedule(EncoderWithMixture("sparsemax"), trainer_arguments(), epoch=1) is None
    assert apply_entmax_schedule(torch.nn.Linear(1, 1), trainer_arguments(), epoch=1) is None


def test_end_to_end_an_annealed_run_records_the_exponent_and_keeps_only_a_sparsemax_epoch(tmp_path):
    paths = write_toy_dataset(tmp_path)
    run = run_trainer(paths, tmp_path / "annealed", "--encoder", "linear_response", "--cross-relation-aggregator", "softmax_mixture",
                      "--mixture-weighting", "entmax", "--mixture-entmax-exponent", "1.5", "--mixture-entmax-anneal-epochs", "2",
                      "--max-epochs", "4")
    history = run["results"]["history"]
    assert [entry["mixture_entmax_exponent"] for entry in history] == [1.5, 1.75, 2.0, 2.0]
    assert [entry.get("selection_paused_while_annealing", False) for entry in history] == [True, True, False, False]
    assert run["results"]["best_epoch"] >= 2, "an epoch trained below sparsemax was kept"
