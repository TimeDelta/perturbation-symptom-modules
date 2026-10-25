"""Minimum description length selection of the module count (design section 5.5).

Total code length for a fitted model = model cost + data cost, where the model
cost is node_cost * active support nodes + link_cost * nonzero links (from
NoisyOrPathwayModuleHead.description_length_penalty) and the data cost is the
code length of the labels of the training observations. Candidate values
of K are trained separately and the smallest total wins. Costs are in nats when
the likelihood is in nats; a node cost of log2(num_graph_nodes) bits is the
natural choice (the cost of naming a node), converted to nats.

The data cost counts each label once (decision 9.90, the owner, 22 October 2026: "each label should only be counted
once in the MDL calculation"): under run_main_model.py --label-likelihood positive_unlabelled it is the sum over the
counted pairs of their code lengths under the positive-unlabelled likelihood
(models/positive_unlabelled_likelihood.py), in nats. The design named "the weighted negative log-likelihood of the
observations" before that decision; data_cost_nats computes it too, for --label-likelihood weighted, where a pair
counts as many times as its loss weight and the total is therefore not a code length.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class CandidateDescriptionLength:
    num_pathway_modules: int
    model_cost_nats: float
    data_cost_nats: float

    @property
    def total_nats(self) -> float:
        return self.model_cost_nats + self.data_cost_nats


def node_naming_cost_nats(num_graph_nodes: int) -> float:
    return math.log(num_graph_nodes)


def data_cost_nats(per_pair_code_length: np.ndarray, pair_weight: np.ndarray) -> float:
    """sum w L over the pairs. Under counted-once coding w is 1 on every counted pair and 0 on a pair the label
    selection set aside, so the sum is the labels' code length; under the weighted likelihood w is the loss weight.
    Under --equal-drug-shares w is the rescaled count, whose sum over the fitted rows is still the number of counted
    pairs, so the data cost stays in nats per pair while each drug's pairs share one drug's worth of it."""
    lengths = np.asarray(per_pair_code_length, dtype=float)
    weights = np.asarray(pair_weight, dtype=float)
    if lengths.shape != weights.shape:
        raise ValueError(f"{lengths.shape} code lengths against {weights.shape} weights")
    counted = weights > 0
    if not np.isfinite(lengths[counted]).all():
        raise ValueError("a counted pair has an infinite code length")
    return float((lengths[counted] * weights[counted]).sum())


def candidate_description_length(num_pathway_modules: int, model_cost_nats: float, per_pair_code_length: np.ndarray,
                                 pair_weight: np.ndarray) -> CandidateDescriptionLength:
    """The candidate of one fitted module count: its model cost and the data cost of its fit's code lengths."""
    return CandidateDescriptionLength(num_pathway_modules, float(model_cost_nats), data_cost_nats(per_pair_code_length, pair_weight))


def select_minimum_description_length(candidates: list[CandidateDescriptionLength]) -> CandidateDescriptionLength:
    if not candidates:
        raise ValueError("no candidates")
    return min(candidates, key=lambda candidate: candidate.total_nats)
