"""The forward-cone normalisations of the linear-response encoder (decision 9.16; the owner, 20 October 2026:
"can you please implement that").

forward_cone divides each message by the weights entering its destination from inside the seed's own forward cone,
per seed; forward_cone_union does it once per perturbation over the union of its seeds' cones. Both start from the
total_in_degree adjacency and rescale its rows, so on a graph where every seed reaches every node they must give
total_in_degree's response exactly, and on a graph with dead edges they must give the response of the graph with the
dead edges deleted.
"""
import pytest
import torch

from mechanistic_pathway_learning.models.linear_response_encoder import CONE_NORMALISATIONS, LinearResponseEncoder


def build_encoder(edges, num_nodes, normalisation, relation_types=("activates",), steps=40, **keywords) -> LinearResponseEncoder:
    """edges: (source, target, relation, sign). A fixed step count, so two encoders that should agree run the same
    rounds; the gains are the first parameters drawn, so one seed gives every encoder here the same gains."""
    relation_types = list(relation_types)
    torch.manual_seed(0)
    return LinearResponseEncoder(
        num_nodes, relation_types,
        edge_source=torch.tensor([edge[0] for edge in edges]), edge_target=torch.tensor([edge[1] for edge in edges]),
        edge_relation=torch.tensor([relation_types.index(edge[2]) for edge in edges]), edge_sign=torch.tensor([float(edge[3]) for edge in edges]),
        node_features=torch.eye(num_nodes), node_state_dim=2, num_propagation_steps=steps, fixed_point_tolerance=None,
        propagation_channels=2, normalisation=normalisation, **keywords)


def seeded(nodes, signs=None):
    signs = signs or [1.0] * len(nodes)
    return torch.tensor([nodes]), torch.tensor([[[sign, 1.0] for sign in signs]])


# a ring 0 -> 1 -> 2 -> 3 -> 0 with two chords, so every node reaches every node and no edge is ever dead
RING_WITH_CHORDS = [(0, 1, "activates", 1), (1, 2, "activates", -1), (2, 3, "activates", 1), (3, 0, "activates", 1),
                    (0, 2, "activates", 1), (3, 1, "activates", -1)]


@pytest.mark.parametrize("normalisation", CONE_NORMALISATIONS)
def test_where_every_seed_reaches_every_node_the_cone_divisor_is_total_in_degree(normalisation):
    reference = build_encoder(RING_WITH_CHORDS, 4, "total_in_degree")
    cone = build_encoder(RING_WITH_CHORDS, 4, normalisation)
    with torch.no_grad():
        expected = reference.response(*seeded([0, 2], [1.0, -0.5]))
        observed = cone.response(*seeded([0, 2], [1.0, -0.5]))
    assert torch.allclose(observed, expected, atol=1e-6)


# the chain 0 -> 1 -> 2 -> 3, each chain node also fed by two distractor nodes nothing reaches (4 to 9)
CHAIN = [(0, 1, "activates", 1), (1, 2, "activates", 1), (2, 3, "activates", 1)]
DISTRACTORS = [(4, 1, "activates", 1), (5, 1, "activates", 1), (6, 2, "activates", 1), (7, 2, "activates", 1),
               (8, 3, "activates", 1), (9, 3, "activates", 1)]


@pytest.mark.parametrize("normalisation", CONE_NORMALISATIONS)
def test_a_dead_edge_no_longer_divides_the_live_message(normalisation):
    """With the distractors, total_in_degree divides every step by three; the cone divisor gives what the chain alone
    gives under total_in_degree, which is the response of the graph with the dead edges deleted."""
    chain_alone = build_encoder(CHAIN, 10, "total_in_degree")
    diluted = build_encoder(CHAIN + DISTRACTORS, 10, "total_in_degree")
    cone = build_encoder(CHAIN + DISTRACTORS, 10, normalisation)
    with torch.no_grad():
        expected = chain_alone.response(*seeded([0]))
        observed = cone.response(*seeded([0]))
        attenuated = diluted.response(*seeded([0]))
    assert torch.allclose(observed, expected, atol=1e-6)
    assert float(observed[0, 3].abs().sum()) > 5 * float(attenuated[0, 3].abs().sum()), "the distractors attenuate total_in_degree"


# two seeds whose cones are disjoint until they meet at node 2, then 2 -> 3
TWO_CONES = [(0, 2, "activates", 1), (1, 2, "activates", 1), (2, 3, "activates", 1)]


def test_per_seed_is_the_sum_of_the_seeds_alone_and_the_union_is_not():
    per_seed = build_encoder(TWO_CONES, 4, "forward_cone")
    union = build_encoder(TWO_CONES, 4, "forward_cone_union")
    with torch.no_grad():
        both = per_seed.response(*seeded([0, 1]))
        first_alone = per_seed.response(*seeded([0]))
        second_alone = per_seed.response(*seeded([1]))
        both_by_union = union.response(*seeded([0, 1]))
    assert torch.allclose(both, first_alone + second_alone, atol=1e-6), "the columns are summed exactly"
    # per seed, node 2 takes each seed's message whole; under the union it divides each by both edges
    assert float(both[0, 2].abs().sum()) > 1.5 * float(both_by_union[0, 2].abs().sum())


def test_a_padded_batch_and_an_empty_perturbation_give_the_reference_response():
    """Padding (-1) makes no column, and a perturbation with no valid seed has no column and a zero response."""
    reference = build_encoder(RING_WITH_CHORDS, 4, "total_in_degree")
    cone = build_encoder(RING_WITH_CHORDS, 4, "forward_cone")
    index = torch.tensor([[0, -1], [-1, -1], [1, 3]])
    sign_and_magnitude = torch.tensor([[[1.0, 1.0], [1.0, 1.0]], [[1.0, 1.0], [1.0, 1.0]], [[-1.0, 0.5], [1.0, 2.0]]])
    with torch.no_grad():
        expected = reference.response(index, sign_and_magnitude)
        observed = cone.response(index, sign_and_magnitude)
    assert torch.count_nonzero(observed[1]) == 0
    assert torch.allclose(observed, expected, atol=1e-6)


def test_the_entries_that_carry_sum_to_at_most_one_in_every_row():
    """The contraction bound on the states the loop visits: per column, the rescaled entries whose source is inside
    the cone sum to at most one in absolute value at every destination."""
    cone = build_encoder(CHAIN + DISTRACTORS + [(3, 1, "activates", -1)], 10, "forward_cone")
    reached = cone.cone_reach([((0,), ())])
    ratio = cone.cone_row_ratio(reached)[:, 0, 0]  # [K]
    compressed = cone.compressed_adjacency.coalesce()
    row, source = compressed.indices()
    carried = compressed.values().abs() * ratio[row] * reached[source, 0].to(torch.float32)
    row_sums = torch.zeros(compressed.shape[0]).index_add(0, row, carried)
    assert float(row_sums.max()) <= 1.0 + 1e-6, row_sums.tolist()


ENTRY_RELATIONS = ["activates", "targets", "sequesters"]


def entry_graph_encoder(normalisation="forward_cone"):
    """Gene 0 activates carrier 1, which sequesters drug 2; drug 2 targets 3 and drug 4 targets 5. Drugs 2 and 4 are
    entry nodes, present only where seeded, and their mechanism edges are their only way out."""
    edges = [(0, 1, "activates", 1), (1, 2, "sequesters", -1), (2, 3, "targets", 1), (4, 5, "targets", 1)]
    entry_node_mask = torch.tensor([False, False, True, False, True, False])
    return build_encoder(edges, 6, normalisation, relation_types=ENTRY_RELATIONS, entry_node_mask=entry_node_mask,
                         entry_relation_names=("targets",))


def test_an_unseeded_drug_node_is_absent_from_the_walk_and_a_seeded_one_sends_its_mechanism_edges():
    cone = entry_graph_encoder()
    gene_alone = cone.cone_reach([((0,), ())])[:, 0]
    assert gene_alone.tolist() == [True, True, False, False, False, False], "drug 2 is absent, so its target is not reached"
    drug_seeded = cone.cone_reach([((2,), (2,))])[:, 0]
    assert drug_seeded.tolist() == [False, False, True, True, False, False], "the mechanism edge carries the drug to its target"
    gene_with_the_drug_present = cone.cone_reach([((0,), (2,))])[:, 0]
    assert gene_with_the_drug_present[3], "with the drug in the perturbation, the gene's signal reaches it and through it the target"


def test_the_cone_response_with_entry_nodes_matches_total_in_degree_where_nothing_is_dead():
    """No destination here has an entering edge from outside the seed's cone, so the two must agree."""
    reference = entry_graph_encoder("total_in_degree")
    cone = entry_graph_encoder("forward_cone")
    with torch.no_grad():
        expected = reference.response(*seeded([2]))
        observed = cone.response(*seeded([2]))
    assert torch.count_nonzero(observed[0, 3]) > 0
    assert torch.allclose(observed, expected, atol=1e-6)


def test_the_cone_cache_is_filled_once_and_can_be_turned_off():
    cached = build_encoder(CHAIN + DISTRACTORS, 10, "forward_cone")
    with torch.no_grad():
        cached.response(*seeded([0]))
        cached.response(*seeded([0]))
    assert list(cached.cone_reach_cache) == [((0,), ())]
    uncached = build_encoder(CHAIN + DISTRACTORS, 10, "forward_cone", cache_cone_reach=False)
    with torch.no_grad():
        uncached.response(*seeded([0]))
    assert uncached.cone_reach_cache == {}


@pytest.mark.parametrize("normalisation", CONE_NORMALISATIONS)
def test_the_cone_normalisations_refuse_what_they_are_not_built_for(normalisation):
    with pytest.raises(ValueError, match="softmax_mixture"):
        build_encoder(CHAIN, 4, normalisation, cross_relation_aggregator="softmax_mixture")
    with pytest.raises(ValueError, match="edge gates"):
        build_encoder(CHAIN, 4, normalisation, edge_gates=object())  # refused before the layout is read
