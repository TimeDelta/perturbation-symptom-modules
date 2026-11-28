"""Tests added on 28 November 2026 to kill mutants of mechanistic_pathway_learning/evaluation/leakage_only_adversary.py
that tests/test_leakage_only_adversary.py and the tests reading the adversary let survive (hand-made mutation testing;
the mutants and which test kills each were listed in the working report of the session of 28 November 2026, which is outside the repository). Each test checks what a docstring or
comment of the module says the code does. Synthetic graphs only."""
import numpy as np
import pytest

from mechanistic_pathway_learning.evaluation.leakage_only_adversary import (
    BASE_RATE_PRIOR_STRENGTH,
    LeakageOnlyAdversary,
    channel_breakdown,
    neighbours_through_the_channels,
    reached_node_neighbours,
    reached_nodes_of_perturbations,
    registered_channel_list,
    seed_nodes_of_perturbations,
    validated_type_pairs,
)
from tests.test_leakage_only_adversary import EDGE_SOURCE, EDGE_TARGET, IDS, NODES, SEEDS, TYPES_OF_ID, reached

# ---------------------------------------------------------------- seeds and walks


def test_a_seed_index_outside_the_node_list_seeds_no_node():
    """seed_nodes_of_perturbations: "perturbation id -> the node ids it seeds"; an index before the first node or past
    the last one names no node."""
    assert seed_nodes_of_perturbations(["p"], [[-1, 0, 2]], ["A", "B"]) == {"p": frozenset({"A"})}


def test_a_walk_starts_from_the_seeds_inside_the_node_list_only():
    """reached_nodes_of_perturbations: the reached set is that of the seeds, and an index outside the node list is
    no seed (as seed_nodes_of_perturbations reads it)."""
    with_strays = reached_nodes_of_perturbations(["p"], [[0, len(NODES), -1]], NODES, EDGE_SOURCE, EDGE_TARGET, 1)
    assert with_strays == {"p": frozenset({"GENE:A", "PROTEIN:A"})}


def test_true_is_not_a_number_of_hops():
    """reached_nodes_of_perturbations: "maximum_hops must be a whole number of steps"."""
    with pytest.raises(ValueError, match="whole number of steps"):
        reached(True)


def test_a_type_pair_with_an_empty_type_is_refused():
    """validated_type_pairs: the pairs must each name a held-out type and a training type."""
    for pairs in ([("", "gene")], [("gene", "")]):
        with pytest.raises(ValueError, match="at least one"):
            validated_type_pairs(pairs)


# ---------------------------------------------------------------- the reached-node channel's neighbours


def test_only_the_covered_type_pairs_enter_and_a_held_out_perturbation_with_none_left_has_no_entry():
    """reached_node_neighbours counts "the pairs whose (held-out type, training type) reached_node_type_pairs covers".
    gA (a gene) and d3 (a drug) both reach PROTEIN:A at k = 1, but (gene, drug) is not covered here although gene is a
    covered held-out type and drug a covered training type."""
    covered = [("gene", "gene"), ("drug", "drug")]
    assert reached_node_neighbours(["gA"], ["gB", "d3"], reached(1), TYPES_OF_ID, covered) == {}
    assert reached_node_neighbours(["gA"], ["gB", "d3"], reached(1), TYPES_OF_ID, covered + [("gene", "drug")]) == {"gA": {"d3": 1}}


def test_reached_nodes_without_their_types_and_pairs_are_refused():
    """neighbours_through_the_channels: "the reached-node channel needs perturbation_types_of_id and
    reached_node_type_pairs"."""
    seeds = seed_nodes_of_perturbations(IDS, SEEDS, NODES)
    with pytest.raises(ValueError, match="needs perturbation_types_of_id and reached_node_type_pairs"):
        neighbours_through_the_channels(["d2"], ["gB"], seeds, reached(1))
    with pytest.raises(ValueError, match="needs perturbation_types_of_id and reached_node_type_pairs"):
        neighbours_through_the_channels(["d2"], ["gB"], seeds, reached(1), TYPES_OF_ID)


def test_the_breakdown_counts_held_out_perturbations_and_pairs_apart():
    """channel_breakdown: held_out_with_a_leaked_neighbour counts held-out perturbations, the other keys count pairs."""
    breakdown = channel_breakdown({"d2": {"gA": 1, "gB": 2, "d3": 1}}, TYPES_OF_ID)
    assert breakdown == {"held_out_with_a_leaked_neighbour": 1, "pairs_through_a_training_drug": 1,
                         "pairs_through_a_training_gene": 2, "pairs_through_another_type": 0}


# ---------------------------------------------------------------- the adversary

TRAINING = ["t1", "t2"]
OUTCOMES = np.array([[1.0, 0.0], [0.0, 1.0]])  # base rate 0.5 for each symptom


def test_the_pooling_rule_is_checked_and_defaults_to_the_shrunk_mean():
    """POOLING_RULES: "The default shrinks the neighbour mean towards the training base rate"."""
    assert LeakageOnlyAdversary().pooling_rule == "base_rate_shrunk_mean"
    with pytest.raises(ValueError, match="pooling_rule must be one of"):
        LeakageOnlyAdversary("median")


def test_one_neighbour_sharing_one_node_moves_the_score_halfway_to_its_label():
    """BASE_RATE_PRIOR_STRENGTH: "one neighbour sharing one node moves the score halfway from the base rate to that
    neighbour's label"."""
    assert BASE_RATE_PRIOR_STRENGTH == 1.0
    adversary = LeakageOnlyAdversary().fit(TRAINING, OUTCOMES)
    assert adversary.predict(["h"], {"h": {"t1": 1}}) == pytest.approx(np.array([[0.75, 0.25]]))


def test_the_shrunk_mean_weighs_each_neighbour_by_its_shared_nodes_against_the_prior():
    """The shrunk mean: (sum of shared-node weight x label + prior strength x base rate) / (total weight + prior
    strength), "the weight of evidence behind it"."""
    adversary = LeakageOnlyAdversary("base_rate_shrunk_mean", base_rate_prior_strength=3.0).fit(TRAINING, OUTCOMES)
    expected = (2 * OUTCOMES[0] + 1 * OUTCOMES[1] + 3.0 * np.array([0.5, 0.5])) / (2 + 1 + 3.0)
    assert adversary.predict(["h"], {"h": {"t1": 2, "t2": 1}}) == pytest.approx(expected[None, :])


def test_the_weighted_mean_and_the_nearest_neighbour_read_the_shared_node_counts():
    """shared_node_weighted_mean weighs each neighbour by its shared nodes; nearest_neighbour_maximum takes the labels
    of the neighbour sharing the most."""
    neighbours = {"h": {"t1": 1, "t2": 3}}
    weighted = LeakageOnlyAdversary("shared_node_weighted_mean").fit(TRAINING, OUTCOMES).predict(["h"], neighbours)
    assert weighted == pytest.approx(np.array([[0.25, 0.75]]))
    nearest = LeakageOnlyAdversary("nearest_neighbour_maximum").fit(TRAINING, OUTCOMES).predict(["h"], neighbours)
    assert nearest == pytest.approx(OUTCOMES[1][None, :])


def test_a_label_mask_limits_the_base_rate_and_the_looked_up_labels_to_the_labelled_pairs():
    """fit: "with a label mask the base rate and the looked-up labels both run over the labelled pairs only"."""
    outcomes = np.array([[1.0, 1.0], [1.0, 0.0], [0.0, 0.0]])
    label_mask = np.array([[True, False], [True, True], [False, True]])
    adversary = LeakageOnlyAdversary("shared_node_weighted_mean").fit(["t1", "t2", "t3"], outcomes, label_mask)
    assert adversary.symptom_base_rate == pytest.approx([1.0, 0.0])  # 2 of 2 labelled, 0 of 2 labelled
    assert adversary.predict(["h"], {"h": {"t1": 1}}) == pytest.approx(np.array([[1.0, 0.0]]))  # t1's set-aside positive is not looked up


def test_predict_before_fit_is_refused_and_an_unknown_neighbour_is_no_lookup():
    """predict: "fit before predict"; a held-out perturbation with no leaked training neighbour "takes the training
    base rate", and a neighbour that is no training perturbation is not one."""
    with pytest.raises(RuntimeError, match="fit before predict"):
        LeakageOnlyAdversary().predict(["h"], {})
    adversary = LeakageOnlyAdversary().fit(TRAINING, OUTCOMES)
    assert adversary.predict(["h"], {"h": {"not_in_training": 4}}) == pytest.approx(np.array([[0.5, 0.5]]))


def test_an_edge_set_without_the_number_of_hops_is_refused():
    """registered_channel_list: "reached_node_hops None is the reached-node channel switched off", and "reached_node_type_pairs
    and reach_edge_set describe the reached-node channel; pass reached_node_hops with them"."""
    with pytest.raises(ValueError, match="pass reached_node_hops with them"):
        registered_channel_list(None, None, "stored")
