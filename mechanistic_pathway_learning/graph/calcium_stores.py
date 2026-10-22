"""Store content as a driving force on release, read after the fixed point (decision 9.75; the owner, 20 October 2026:
"please implement that").

What the graph has. The organelle calcium stores are pools (reactome_import.ORGANELLE_CALCIUM_STORES): a non-currency
node per store that the release channels draw on through substrate_of and the pumps refill through product_of. So the
first-order effect of store content on release is already propagated: a depleted store sends less to its release
reactions by mass action, as any substrate does.

What a linear propagation cannot carry. The unit current of a release channel "is defined by luminal [Ca2+],
permeable ion composition and concentration, and pore selectivity and conductance" (Gillespie and Fill 2008, PMID
18621826): the flux is the number of open channels times the driving force, a product of two quantities the
perturbation can move at once. Linearised about rest that product is two additive terms, which the propagation has,
plus their interaction, which it does not: a perturbation that opens the channel does less when the store it draws on
is depleted, and more when it is overfilled. This module supplies that interaction the way graph/compartment_ph.py
supplies the pH ceiling, as a multiplier applied after the propagation has settled:

    w_store(release reaction) = max(0, 1 + sensitivity * store deviation)

with one learned sensitivity per store, calibrated as the pH sensitivity is (linear_response_encoder.
calibrate_calcium_store_sensitivity). The weight is linear in the deviation, not a bell curve: a store has no optimum
the way an enzyme has a pH optimum, and release rises with luminal calcium until the store is empty, which is the
floor at 0. It multiplies the release reactions of the store only, the reactions that consume the store pool, and not
the pumps that fill it or anything else in the compartment. A weight does not propagate, so the store does not become
a hub, and the fixed point is reached before it is applied, so the contraction is untouched. What it costs is the same
as the pH weight: positive homogeneity of degree one, since the weight reads the deviation's size, and the exact
antisymmetry of a gain and a loss of function at the release reactions, since 1 + s and 1 - s are not negatives.

The honest limit, stated: with the store pool propagating, this multiplier is the second-order term, and whether it
is worth its parameters is a measurement for the owner, not a claim of this module.
"""
from __future__ import annotations

import numpy as np

STORE_DISPLAY_NAME_MARK = "(neuronal store,"
SUBSTRATE_RELATION = "substrate_of"


def store_pool_indices(node_ids, node_display_names) -> list[int]:
    """The indices of the store pool nodes, in node order: the pools reactome_import builds with "neuronal store" in
    their display name."""
    return [index for index, name in enumerate(node_display_names) if STORE_DISPLAY_NAME_MARK in str(name)]


def release_reactions_of_stores(store_indices: list[int], num_nodes: int, edge_source, edge_target, edge_relation, relation_types) -> np.ndarray:
    """[N] the position in store_indices of the store each node draws on through substrate_of, -1 for every other node.
    A reaction that consumed two stores (none does) would take the last one in edge order."""
    store_position = {node_index: position for position, node_index in enumerate(store_indices)}
    store_of_node = np.full(num_nodes, -1, dtype=np.int64)
    if not store_position or SUBSTRATE_RELATION not in relation_types:
        return store_of_node
    substrate_relation = relation_types.index(SUBSTRATE_RELATION)
    for source, target, relation in zip(np.asarray(edge_source), np.asarray(edge_target), np.asarray(edge_relation)):
        if int(relation) == substrate_relation and int(source) in store_position:
            store_of_node[int(target)] = store_position[int(source)]
    return store_of_node


def calcium_store_inputs(data) -> dict:
    """The encoder keywords for the store driving-force weight, or {} when the graph holds no store pool."""
    names = getattr(data, "node_display_name", None)
    if names is None:
        return {}
    stores = store_pool_indices(data.node_ids, names)
    if not stores:
        return {}
    return {"store_names": [str(data.node_ids[index]) for index in stores],
            "store_pool_node_index": np.asarray(stores, dtype=np.int64),
            "store_of_node": release_reactions_of_stores(stores, len(data.node_ids), data.edge_source, data.edge_target, data.edge_relation, data.relation_types)}
