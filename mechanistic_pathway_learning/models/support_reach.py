"""How many perturbation sources can move each node, and the module-support rule that reads it.

A node's reach is the number of distinct seed nodes from which a route can reach it: the seeds of the perturbations
counted (each perturbation's own seed nodes, so a gene's loss and its gain share one source), walking the edges the
linear-response encoder propagates along. Those are the encoder's bottleneck edges (LinearResponseEncoder
.bottleneck_edge_source and _target), which it takes from the stacked adjacency it propagates on, with the derived
reverse relations (depletes_substrate, product_opposes) in it and the edges out of non-propagating nodes left out, and
with the drug mechanism edges appended. Under cell-class weights a route may also only pass through nodes some class
expresses, as the limiting-step rule requires (walkable_adjacency). Reachability ignores signs, gains, the in-degree
divisor and edge gates, so it is an upper bound on the nodes a field can carry a nonzero change to: a rule that excludes
by it excludes no more than any measure of reach that read those would.

The rule (experiments/run_main_model.py --module-support-minimum-reach; amendment item 39 registers it at 2 for the
tested model, the linear-response encoder with the noisy-OR head, and the trainer resolves its default to 2 there and to
0, which leaves it off, for every other encoder and head): a node fewer than
that many sources can reach is never module support. At 2 it excludes every node one source or none can reach. A node
only one perturbation source can move cannot take part in convergence, so it cannot serve the equifinality hypothesis,
and a module holding it reads the identity of that perturbation as a lookup entry; a node no source can reach carries no
field and only adds a gate. The owner, 22 November 2026, on the version that excludes only a perturbed gene with no
incoming edge: "So limit it to only allowing incorporation of nodes with no incoming edges if it isn't also a
perturbation source"; and, offered the general version beside it and the dominance diagnostic: "yes build both and draft
the amendment". From 22 to 24 November 2026 the rule was built and off by default, waiting for its amendment; it was
registered as amendment item 39 and switched on for the tested model on 24 November 2026 (the owner: "I already told you
twice not for 9.150 to do it before the draw"), so every run before that date was made without it. The reason given
above names the equifinality hypothesis, which item 38 made descriptive on 23 November 2026; the rule does not depend on
it, since a module holding such a node reads which perturbation was applied and not a mechanism two share.

The sources counted are the training rows only (the trainer passes train_indices, and the refit its refit rows), as the
leaks are initialised from them: under --score-lockbox the data still hold the lockbox perturbations, and a reach that
counted them would let lockbox membership shape the model before the lockbox is scored.
"""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import scipy.sparse as sparse
from scipy.sparse.csgraph import breadth_first_order


def walkable_adjacency(num_nodes: int, walked_edge_source: np.ndarray, walked_edge_target: np.ndarray,
                       node_carries_class_weight: np.ndarray, entry_node_mask: np.ndarray) -> sparse.csr_matrix:
    """The edges a route can take: walked by the bottleneck, both ends with a class weight above 0 in some class, and
    not into an entry node, since an entry node is present only in the perturbation that seeds it."""
    route_can_take_edge = (node_carries_class_weight[walked_edge_source] & node_carries_class_weight[walked_edge_target]
                           & ~entry_node_mask[walked_edge_target])
    return sparse.csr_matrix((np.ones(int(route_can_take_edge.sum()), dtype=np.int8),
                              (walked_edge_source[route_can_take_edge], walked_edge_target[route_can_take_edge])),
                             shape=(num_nodes, num_nodes))


def encoder_walkable_adjacency(encoder, num_nodes: int) -> tuple[sparse.csr_matrix, np.ndarray]:
    """The walkable adjacency of a linear-response encoder and which nodes carry a class weight (every node, for an
    encoder without cell-class weights)."""
    if getattr(encoder, "bottleneck_edge_source", None) is None:
        raise ValueError("the reach is read from the linear-response encoder's walked edges, which this encoder does not have")
    class_weight = getattr(encoder, "cell_class_node_weight", None)
    node_carries_class_weight = (np.ones(num_nodes, dtype=bool) if class_weight is None
                                 else (class_weight.max(dim=1).values > 0).cpu().numpy())
    entry_mask = getattr(encoder, "entry_node_mask", None)
    entry_node_mask = np.zeros(num_nodes, dtype=bool) if entry_mask is None else entry_mask.cpu().numpy().astype(bool)
    adjacency = walkable_adjacency(num_nodes, encoder.bottleneck_edge_source.cpu().numpy(), encoder.bottleneck_edge_target.cpu().numpy(),
                                   node_carries_class_weight, entry_node_mask)
    return adjacency, node_carries_class_weight


def distinct_seed_nodes(perturbation_seeds: Iterable[Iterable[int]]) -> list[int]:
    """Every node at least one of the perturbations seeds, once, in order."""
    return sorted({int(node) for seeds in perturbation_seeds for node in seeds})


def source_reach(adjacency: sparse.csr_matrix, seed_nodes: Iterable[int], node_carries_class_weight: np.ndarray) -> np.ndarray:
    """For every node, how many of seed_nodes a route can reach it from, the seed itself included; a seed without a
    class weight starts no route, because the recurrence starts it at its class weight."""
    reach = np.zeros(adjacency.shape[0], dtype=np.int64)
    for seed_node in seed_nodes:
        if node_carries_class_weight[seed_node]:
            reach[breadth_first_order(adjacency, int(seed_node), directed=True, return_predecessors=False)] += 1
    return reach


def nodes_below_minimum_reach(encoder, num_nodes: int, perturbation_seeds: list[Iterable[int]], minimum_reach: int,
                              entry_node_mask: np.ndarray | None = None) -> tuple[np.ndarray, dict]:
    """The nodes fewer than minimum_reach of the perturbations' seed nodes can reach, as a boolean mask, and a summary
    of what the rule removes. Entry nodes are left out of the mask and of the counts, since every module excludes them
    already (HardConcreteNodeGate's excluded_node_mask)."""
    if minimum_reach < 1:
        raise ValueError("a minimum reach below 1 excludes nothing; the rule is off at 0, which callers check before calling")
    adjacency, node_carries_class_weight = encoder_walkable_adjacency(encoder, num_nodes)
    seed_nodes = distinct_seed_nodes(perturbation_seeds)
    reach = source_reach(adjacency, seed_nodes, node_carries_class_weight)
    is_entry_node = np.zeros(num_nodes, dtype=bool) if entry_node_mask is None else np.asarray(entry_node_mask, dtype=bool)
    below = (reach < minimum_reach) & ~is_entry_node
    eligible = ~is_entry_node
    summary = {
        "minimum_reach": int(minimum_reach),
        "perturbations_counted": int(len(perturbation_seeds)),
        "seed_nodes": int(len(seed_nodes)),
        "seed_nodes_starting_a_route": int(node_carries_class_weight[seed_nodes].sum()) if seed_nodes else 0,
        "nodes_eligible_before": int(eligible.sum()),
        "nodes_excluded": int(below.sum()),
        "nodes_with_reach_0": int(((reach == 0) & eligible).sum()),
        "nodes_with_reach_1": int(((reach == 1) & eligible).sum()),
        "nodes_with_reach_2_to_5": int(((reach >= 2) & (reach <= 5) & eligible).sum()),
    }
    return below, summary
