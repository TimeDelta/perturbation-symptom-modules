"""The leakage-only adversary of decision 9.35 and the reached-node channel decision 9.36 added to it (ruled 24 November
2026: "the k=2 reached-node channel enters the adversary of 9.35, with k as a sensitivity sweep"). Synthetic graphs
only."""
import numpy as np
import pytest

from mechanistic_pathway_learning.evaluation.leakage_only_adversary import (
    LeakageOnlyAdversary,
    channel_breakdown,
    leaked_neighbours,
    neighbours_through_the_channels,
    reach_edges,
    reached_node_neighbours,
    reached_nodes_of_perturbations,
    registered_channel_list,
    seed_nodes_of_perturbations,
    seen_reached_node_share,
    seen_target_share,
    validated_type_pairs,
)

# A split graph in miniature: each gene seeds its GENE node and reaches its PROTEIN node in one step; proteins A and B
# both catalyse RXN:1, protein C catalyses RXN:2; both reactions make ATP (a currency node), and ATP feeds RXN:3.
NODES = ["GENE:A", "GENE:B", "GENE:C", "PROTEIN:A", "PROTEIN:B", "PROTEIN:C", "RXN:1", "RXN:2", "MET:ATP", "RXN:3"]
EDGE_SOURCE = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8])
EDGE_TARGET = np.array([3, 4, 5, 6, 6, 7, 8, 8, 9])
IS_CURRENCY = np.array([name == "MET:ATP" for name in NODES])
IDS = ["gA", "gB", "gC", "d1", "d2", "d3"]
KINDS = ["gene", "gene", "gene", "drug", "drug", "drug"]
SEEDS = [[0], [1], [2], [3], [4], [3]]  # d1 and d3 share PROTEIN:A; d2 targets PROTEIN:B
TYPES_OF_ID = dict(zip(IDS, KINDS))


def reached(maximum_hops, edge_set="stored"):
    source, target = reach_edges(EDGE_SOURCE, EDGE_TARGET, IS_CURRENCY, edge_set)
    return reached_nodes_of_perturbations(IDS, SEEDS, NODES, source, target, maximum_hops)


def test_k_counts_steps_from_the_seeds_as_the_9_36_measurement_did():
    """At k = 1 a gene reaches only its own protein; at k = 2 the reaction that protein catalyses (9.36: "At k=1 a gene
    reaches only its own protein")."""
    assert reached(0)["gA"] == frozenset({"GENE:A"})
    assert reached(1)["gA"] == frozenset({"GENE:A", "PROTEIN:A"})
    assert reached(2)["gA"] == frozenset({"GENE:A", "PROTEIN:A", "RXN:1"})
    with pytest.raises(ValueError):
        reached(-1)
    with pytest.raises(ValueError):
        reached(1.5)


def test_k0_is_the_shared_seed_node_channel():
    assert reached(0) == seed_nodes_of_perturbations(IDS, SEEDS, NODES)
    every_pair = [(left, right) for left in ("gene", "drug") for right in ("gene", "drug")]
    seeds = seed_nodes_of_perturbations(IDS, SEEDS, NODES)
    held_out, training = ["gA", "d1", "d2"], ["gB", "gC", "d3"]
    assert neighbours_through_the_channels(held_out, training, seeds, reached(0), TYPES_OF_ID, every_pair) == leaked_neighbours(held_out, training, seeds)


def test_two_genes_share_nothing_at_k1_and_their_reaction_at_k2():
    held_out, training = ["gA"], ["gB", "gC"]
    assert reached_node_neighbours(held_out, training, reached(1), TYPES_OF_ID, [("gene", "gene")]) == {}
    assert reached_node_neighbours(held_out, training, reached(2), TYPES_OF_ID, [("gene", "gene")]) == {"gA": {"gB": 1}}
    # gC's reaction is not gA's, so gC enters only once both walks reach the ATP the two reactions make
    assert reached_node_neighbours(held_out, training, reached(3), TYPES_OF_ID, [("gene", "gene")]) == {"gA": {"gB": 2, "gC": 1}}


def test_the_channel_off_is_the_shared_seed_node_channel_exactly():
    """Without the reached-node arguments nothing changes, so run_baselines.py --with-leakage-lookup and every
    measurement before 27 November 2026 are reproduced."""
    seeds = seed_nodes_of_perturbations(IDS, SEEDS, NODES)
    held_out, training = ["gA", "d1", "d2"], ["gB", "gC", "d3"]
    off = neighbours_through_the_channels(held_out, training, seeds)
    assert off == leaked_neighbours(held_out, training, seeds) == {"d1": {"d3": 1}}
    outcomes = np.array([[1, 0], [0, 1], [1, 1], [0, 0], [1, 0], [1, 1]], dtype=float)
    training_rows = [IDS.index(identifier) for identifier in training]
    adversary = LeakageOnlyAdversary().fit(training, outcomes[training_rows])
    assert np.array_equal(adversary.predict(held_out, off), adversary.predict(held_out, leaked_neighbours(held_out, training, seeds)))
    with pytest.raises(ValueError):
        neighbours_through_the_channels(held_out, training, seeds, reached_node_type_pairs=[("gene", "gene")])


def test_the_type_pairs_decide_which_pairs_enter():
    """9.36 is of the gene side and no ruling says whether drugs enter, so the covered pairs are the caller's."""
    seeds = seed_nodes_of_perturbations(IDS, SEEDS, NODES)
    gene_side_only = neighbours_through_the_channels(["d2"], ["gA", "gB"], seeds, reached(1), TYPES_OF_ID, [("gene", "gene")])
    assert gene_side_only == {}
    # a held-out drug and the training gene of its own target: the shared seed node channel cannot see the pair, since
    # the drug seeds PROTEIN:B and the gene GENE:B, but the gene's one step reaches PROTEIN:B
    drug_with_gene = neighbours_through_the_channels(["d2"], ["gA", "gB"], seeds, reached(1), TYPES_OF_ID, [("drug", "gene")])
    assert drug_with_gene == {"d2": {"gB": 1}}
    breakdown = channel_breakdown(drug_with_gene, TYPES_OF_ID)
    assert breakdown["pairs_through_a_training_gene"] == 1 and breakdown["pairs_through_a_training_drug"] == 0
    with pytest.raises(ValueError):
        validated_type_pairs([])


def test_a_shared_seed_node_is_counted_once_when_both_channels_hold_the_pair():
    """d1 and d3 share PROTEIN:A (one seed node) and, at k = 1, PROTEIN:A and RXN:1 (two reached nodes): the weight is
    the reached count, 2, and not the sum, 3."""
    seeds = seed_nodes_of_perturbations(IDS, SEEDS, NODES)
    combined = neighbours_through_the_channels(["d1"], ["d3"], seeds, reached(1), TYPES_OF_ID, [("drug", "drug")])
    assert leaked_neighbours(["d1"], ["d3"], seeds) == {"d1": {"d3": 1}}
    assert combined == {"d1": {"d3": 2}}


def test_the_currency_edge_set_stops_a_walk_at_atp():
    # at four steps gA's walk passes through ATP to RXN:3 on the stored edges, and stops at ATP without its out-edges
    assert "RXN:3" in reached(4, "stored")["gA"]
    assert "RXN:3" not in reached(4, "stored_without_currency_out_edges")["gA"]
    assert "MET:ATP" in reached(4, "stored_without_currency_out_edges")["gA"]
    with pytest.raises(ValueError):
        reach_edges(EDGE_SOURCE, EDGE_TARGET, IS_CURRENCY, "every_edge")


def test_the_label_free_reached_share_pools_over_the_held_out_nodes():
    # at k = 2: gA reaches GENE:A, PROTEIN:A and RXN:1, of which gB (training) also reaches RXN:1: 1 of 3
    share = seen_reached_node_share(reached(2), ["gA"], ["gB", "gC"], TYPES_OF_ID, [("gene", "gene")])
    assert share == pytest.approx(1 / 3)
    # a held-out type no pair covers contributes nothing
    assert np.isnan(seen_reached_node_share(reached(2), ["d1"], ["gB"], TYPES_OF_ID, [("gene", "gene")]))
    # the drug-side statistic is the one it is built after, and reads targets only
    targets = {"d1": {"PROTEIN:A"}, "d2": {"PROTEIN:B"}, "d3": {"PROTEIN:A"}}
    assert seen_target_share(targets, ["d1"]) == 1.0 and seen_target_share(targets, ["d2"]) == 0.0


def test_the_registered_channel_list_names_what_is_and_is_not_scored():
    off = registered_channel_list()
    assert [channel["channel"] for channel in off["scored"]] == ["shared_seed_node"]
    assert any("disclosed limitation" in text for text in off["not_scored"])
    on = registered_channel_list(2, [("gene", "gene")], "stored")
    reached_channel = on["scored"][1]
    assert reached_channel["maximum_hops"] == 2 and reached_channel["covers"] == [{"held_out_type": "gene", "training_type": "gene"}]
    assert any("longer than 2 steps" in text for text in on["not_scored"])
    with pytest.raises(ValueError):
        registered_channel_list(None, [("gene", "gene")], None)
    with pytest.raises(ValueError):
        registered_channel_list(2, [("gene", "gene")], None)


def test_the_nearest_neighbour_tie_goes_to_the_lowest_training_row_whatever_the_order_of_the_neighbour_map():
    """Two training perturbations share one node each with the held-out one, so they tie. The copied labels are those
    of the neighbour that came first in the ids given to fit, in either order of the neighbour map."""
    training_ids, training_outcomes = ["train_a", "train_b", "train_c"], np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    adversary = LeakageOnlyAdversary("nearest_neighbour_maximum").fit(training_ids, training_outcomes)
    for neighbour_map in ({"held_out": {"train_a": 1, "train_b": 1}}, {"held_out": {"train_b": 1, "train_a": 1}}):
        assert adversary.predict(["held_out"], neighbour_map).tolist() == [[1.0, 0.0]]
    # a larger weight still wins over a lower training row
    assert adversary.predict(["held_out"], {"held_out": {"train_a": 1, "train_c": 2}}).tolist() == [[1.0, 1.0]]


NEAREST_NEIGHBOUR_IN_ONE_PROCESS = """
import json
import numpy as np
from mechanistic_pathway_learning.evaluation.leakage_only_adversary import (LeakageOnlyAdversary, leaked_neighbours,
                                                                             neighbours_through_the_channels)
training_ids, training_outcomes = ["train_a", "train_b"], np.array([[1.0, 0.0], [0.0, 1.0]])
adversary = LeakageOnlyAdversary("nearest_neighbour_maximum").fit(training_ids, training_outcomes)
# shared seed node channel: the held-out drug targets X and Y, each training drug one of them
seed_nodes = {"held_out": frozenset({"protein:X", "protein:Y"}), "train_a": frozenset({"protein:X"}), "train_b": frozenset({"protein:Y"})}
seed_channel = adversary.predict(["held_out"], leaked_neighbours(["held_out"], training_ids, seed_nodes))
# reached-node channel: the held-out gene's walk reaches two reactions, each training gene's walk one of them
gene_seeds = {"held_out": frozenset({"gene:H"}), "train_a": frozenset({"gene:A"}), "train_b": frozenset({"gene:B"})}
reached = {"held_out": frozenset({"gene:H", "reaction:R1", "reaction:R2"}), "train_a": frozenset({"gene:A", "reaction:R1"}),
           "train_b": frozenset({"gene:B", "reaction:R2"})}
reached_channel = adversary.predict(["held_out"], neighbours_through_the_channels(
    ["held_out"], training_ids, gene_seeds, reached, {identifier: "gene" for identifier in reached}, [("gene", "gene")]))
print(json.dumps({"seed_channel": seed_channel.tolist(), "reached_channel": reached_channel.tolist()}))
"""


def test_the_nearest_neighbour_scores_do_not_depend_on_the_process_string_hashing():
    """The neighbour map is built by iterating frozensets of node-id strings, whose order Python randomises per process
    (PYTHONHASHSEED). Until 28 November 2026 nearest_neighbour_maximum took the first maximum in that order, so on
    this interpreter hash seeds 0 to 3 copied different neighbours on both channels. Each hash seed runs in its own
    process, all at once."""
    import json
    import os
    import subprocess
    import sys
    from pathlib import Path
    repository_root = str(Path(__file__).resolve().parents[1])
    processes = {hash_seed: subprocess.Popen([sys.executable, "-c", NEAREST_NEIGHBOUR_IN_ONE_PROCESS], cwd=repository_root,
                                             env={**os.environ, "PYTHONHASHSEED": str(hash_seed), "PYTHONPATH": repository_root},
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                 for hash_seed in range(4)}
    scores_of_hash_seed = {}
    for hash_seed, process in processes.items():
        standard_output, standard_error = process.communicate(timeout=300)
        assert process.returncode == 0, standard_error
        scores_of_hash_seed[hash_seed] = json.loads(standard_output)
    assert all(scores == {"seed_channel": [[1.0, 0.0]], "reached_channel": [[1.0, 0.0]]} for scores in scores_of_hash_seed.values()), scores_of_hash_seed
