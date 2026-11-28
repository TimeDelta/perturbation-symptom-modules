"""The leakage-only adversary: a predictor given the leaked labels and nothing else (decision 9.35).

Why it exists. The owner, 14 October 2026: "instead of doing the final approval on leakage after the draw, let's just
set an upper bound on the acceptable leakage. how can i do that in a non-arbitrary way?" A ceiling stated in counts of
overlapping targets is not checkable against anything, because nothing says what a count is worth. A ceiling stated in
the units of the test is: it asks how much of the registered reading a predictor could earn **by lookup alone**. The
ruling of 24 November 2026 (decision 9.35, the owner: "Use 1.a but not on current graph. On graph at time of draw,
right?") is that this advantage must stay below one standard error of the test's own reading, on the graph the draw is
made on, with the curve that turns it into a label-free ceiling fitted on development-set pseudo-draws
(`evaluation/leakage_ceiling.py`). Registering that rule is an amendment item owed before the draw. Until 27 November
2026 this docstring also compared the advantage with "the 0.05 difference H1 already requires"; that floor was removed
on 15 October 2026, so the comparison is history.

What the adversary is allowed to know. Exactly two things: which training perturbations reach the held-out
perturbation through the channels it is given, and the training labels. No edge weight or sign, no propagation, no
descriptor. It is handed the leaked labels directly, so **its advantage is an upper bound on what any model could
extract from those channels by lookup**, which is the property that makes it usable as a ceiling.

The channels.

- **Shared seed node** (`leaked_neighbours`), always scored and the only channel
  `experiments/run_baselines.py --with-leakage-lookup` uses. Two perturbations sharing a seed node perturb the **same
  node**, so a label transfers between them by identity and a lookup substitutes for mechanism. That is leakage.
- **Reached node within k hops** (`reached_nodes_of_perturbations`, `reached_node_neighbours`), off unless asked for.
  Two perturbations whose forward walks of at most k steps over the graph's edges reach a common node (decision 9.36,
  ruled 24 November 2026: "the k=2 reached-node channel enters the adversary of 9.35, with k as a sensitivity sweep";
  the owner: "2 accepted. Draw depends on graph. Oh well on the genes"). Two genes whose products enter one complex or
  reaction are near-substitutes and the label transfers close to by identity, which is the same test that makes
  drug-to-drug target sharing leakage (9.36). At k = 0 the reached set is the seed set, so the channel is the shared
  seed node channel. Which (held-out type, training type) pairs it covers is a parameter with no default: 9.36's
  measurement and heading are of the gene side, and no ruling says whether a drug enters it. Which edges the walk
  follows is a parameter with no default too (`REACH_EDGE_SETS`).

Until 27 November 2026 this docstring said that transfer along a route is "the hypothesis rather than a leak", that
scoring it "would bound the study's own subject" and that "only the shared-node channel is measured"; decision 9.36
overtook that for sharing within k hops. Sharing reached only by a longer walk is still not scored, and
`registered_channel_list` names it, so that a channel found later is a disclosed limitation and not grounds for a
redraw (9.35).

What item 25 closes and what it leaves open. `target_held_out_split` holds out every drug sharing a held-out target, so
none reaches training. It holds out the gene perturbation of a held-out target only when that perturbation seeds the
target's own node, which is so on a merged graph and not on a gene/protein-split graph, where a drug seeds protein
nodes and the gene perturbation its gene node: there the default leaves the gene perturbation of a held-out protein
target in training, and only the opt-in `HeldOutDrawOptions.hold_out_genes_encoding_held_out_targets` (built 28
November 2026, not ruled) holds it out, matching the gene to the protein it encodes. Until 28 November 2026 this
paragraph said that gene perturbation is held out on every graph. It does **not** hold out the gene perturbations
of a held-out drug's **other** targets, nor the drugs that share those: a drug with three targets of which one is held
out keeps two mechanisms in training, which the registration states as the price of keeping the label exact. So this
channel is open by design and the adversary is what measures its worth. `channel_breakdown` reports the two sides
separately rather than asserting either is empty. On a gene/protein-split graph a drug seeds PROTEIN nodes and a gene
perturbation seeds its GENE node, so the shared seed node channel cannot see a drug paired with the gene of one of its
other targets (no pair came through a training gene in any of the 20 pseudo-draws of decision 9.35b, measured on 14
October 2026 on graph_full_neuronal_split_binders_drugs_v4_enzymes, docs/generated/leakage_only_adversary.md); the
reached-node channel at k of 1 or more sees that pair when the pair (drug, gene) is covered, since the gene's walk
reaches its protein in one step.
"""
from __future__ import annotations

import numpy as np
import torch

from mechanistic_pathway_learning.models.forward_cone_divisor import forward_reachable_nodes

# How a neighbour's labels are pooled. The strongest of the three is the bound, since the adversary is meant to be the
# best lookup available rather than a particular one. The default shrinks the neighbour mean towards the training base
# rate by the weight of evidence behind it, which matters more than it sounds: a raw neighbour mean over one or two
# neighbours is near-binary, and a near-binary score ranks badly whatever information it holds, so an unshrunk
# adversary understates the leak through its score scale rather than through the channel. A shrunk score is also
# continuous with the fallback, since a perturbation with no neighbour lands on the base rate exactly.
# nearest_neighbour_maximum copies the labels of the neighbour sharing the most nodes; neighbours tied on that count go
# to the one first in the ids given to fit, so the copy does not depend on the order of the neighbour map, which
# follows the iteration of frozensets of node-id strings and so changes from one process to the next (PYTHONHASHSEED).
# Until 28 November 2026 a tie went to the first in that order.
POOLING_RULES = ("base_rate_shrunk_mean", "shared_node_weighted_mean", "nearest_neighbour_maximum")
# weight given to the base rate in the shrunk mean, in units of one shared node: one neighbour sharing one node moves
# the score halfway from the base rate to that neighbour's label. A node shared through the reached-node channel counts
# as one shared node like a seed node does.
BASE_RATE_PRIOR_STRENGTH = 1.0
# The edges a reached-node walk may follow, chosen by the caller because no ruling settles it. "stored" walks every
# stored edge, as experiments/measure_gene_hop_grouping.py did for decision 9.36's counts. "stored_without_currency_out_edges"
# leaves out the outgoing edges of currency nodes (ExperimentData.is_currency), as the linear-response encoder does,
# so a walk does not pass through ATP or water to every reaction that uses them. Two walks from gene seeds of at most
# two steps (gene, protein, then the reactions and complexes the protein enters) differ between the two only where a
# currency node lies within one step of a seed; they part at larger k.
REACH_EDGE_SETS = ("stored", "stored_without_currency_out_edges")


def seed_nodes_of_perturbations(perturbation_ids, perturbation_seeds, node_ids) -> dict[str, frozenset[str]]:
    """perturbation id -> the node ids it seeds, for every perturbation regardless of type."""
    names = list(node_ids)
    return {str(perturbation_id): frozenset(names[int(index)] for index in seeds if 0 <= int(index) < len(names))
            for perturbation_id, seeds in zip(perturbation_ids, perturbation_seeds)}


def leaked_neighbours(held_out_ids, training_ids, seed_nodes_of_perturbation) -> dict[str, dict[str, int]]:
    """held-out perturbation id -> {training perturbation id: how many seed nodes they share}, shared nodes only.

    A held-out perturbation with no entry has no lookup available and the adversary falls back to the training base
    rate for it, which is what keeps the adversary from scoring *below* popularity on those rows and so keeps its
    advantage an upper bound rather than a mixture of a leak and a handicap.

    Given reached-node sets instead of seed-node sets (reached_nodes_of_perturbations) it counts shared reached nodes,
    which is how reached_node_neighbours uses it.
    """
    training_by_node: dict[str, list[str]] = {}
    for training_id in training_ids:
        for node in seed_nodes_of_perturbation.get(str(training_id), ()):
            training_by_node.setdefault(node, []).append(str(training_id))
    neighbours: dict[str, dict[str, int]] = {}
    for held_out_id in held_out_ids:
        shared_node_count: dict[str, int] = {}
        for node in seed_nodes_of_perturbation.get(str(held_out_id), ()):
            for training_id in training_by_node.get(node, ()):
                shared_node_count[training_id] = shared_node_count.get(training_id, 0) + 1
        if shared_node_count:
            neighbours[str(held_out_id)] = shared_node_count
    return neighbours


def validated_type_pairs(reached_node_type_pairs) -> frozenset[tuple[str, str]]:
    """The (held-out type, training type) pairs the reached-node channel covers, as a set. Refuses an empty set, since
    a channel switched on over no pair would read as on while scoring nothing."""
    pairs = frozenset((str(held_out_type), str(training_type)) for held_out_type, training_type in reached_node_type_pairs)
    if not pairs or any(not held_out_type or not training_type for held_out_type, training_type in pairs):
        raise ValueError(f"reached_node_type_pairs must name at least one (held-out type, training type) pair, not {reached_node_type_pairs!r}")
    return pairs


def reach_edges(edge_source, edge_target, is_currency, reach_edge_set: str) -> tuple[np.ndarray, np.ndarray]:
    """The (source, target) edge arrays a reached-node walk follows, by REACH_EDGE_SETS. There is no default."""
    source, target = np.asarray(edge_source, dtype=np.int64), np.asarray(edge_target, dtype=np.int64)
    if reach_edge_set == "stored":
        return source, target
    if reach_edge_set == "stored_without_currency_out_edges":
        keep = ~np.asarray(is_currency, dtype=bool)[source]
        return source[keep], target[keep]
    raise ValueError(f"reach_edge_set must be one of {REACH_EDGE_SETS}, not {reach_edge_set!r}")


def reached_nodes_of_perturbations(perturbation_ids, perturbation_seeds, node_ids, edge_source, edge_target,
                                   maximum_hops: int) -> dict[str, frozenset[str]]:
    """perturbation id -> the node ids its seeds reach in at most maximum_hops forward steps, the seeds included.

    The walk is forward_reachable_nodes (models/forward_cone_divisor.py), the one experiments/measure_gene_hop_grouping.py
    measured decision 9.36 with, so k means what it meant there: at k = 1 a gene on a split graph reaches its own
    protein, at k = 2 the reactions and complexes that protein enters. maximum_hops = 0 gives the seed set itself,
    handled here because forward_reachable_nodes takes one step before it checks maximum_steps. The reach does not
    depend on the split, so a caller computes it once per graph and reuses it for every draw.
    """
    if isinstance(maximum_hops, bool) or int(maximum_hops) != maximum_hops or maximum_hops < 0:
        raise ValueError(f"maximum_hops must be a whole number of steps, 0 or more, not {maximum_hops!r}")
    if maximum_hops == 0:
        return seed_nodes_of_perturbations(perturbation_ids, perturbation_seeds, node_ids)
    names = list(node_ids)
    source = torch.as_tensor(np.asarray(edge_source, dtype=np.int64), dtype=torch.long)
    target = torch.as_tensor(np.asarray(edge_target, dtype=np.int64), dtype=torch.long)
    reached_of_seed_set: dict[frozenset[int], frozenset[str]] = {}
    reached_of_perturbation: dict[str, frozenset[str]] = {}
    for perturbation_id, seeds in zip(perturbation_ids, perturbation_seeds):
        seed_set = frozenset(int(index) for index in seeds if 0 <= int(index) < len(names))
        if seed_set not in reached_of_seed_set:
            if seed_set:
                reached = forward_reachable_nodes(source, target, torch.as_tensor(sorted(seed_set), dtype=torch.long),
                                                  len(names), maximum_steps=int(maximum_hops))
                reached_of_seed_set[seed_set] = frozenset(names[index] for index in torch.nonzero(reached).reshape(-1).tolist())
            else:
                reached_of_seed_set[seed_set] = frozenset()
        reached_of_perturbation[str(perturbation_id)] = reached_of_seed_set[seed_set]
    return reached_of_perturbation


def reached_node_neighbours(held_out_ids, training_ids, reached_nodes_of_perturbation, perturbation_types_of_id: dict[str, str],
                            reached_node_type_pairs) -> dict[str, dict[str, int]]:
    """held-out perturbation id -> {training perturbation id: how many reached nodes they share}, over the pairs whose
    (held-out type, training type) reached_node_type_pairs covers (decision 9.36's channel)."""
    covered = validated_type_pairs(reached_node_type_pairs)
    held_out_types = {held_out_type for held_out_type, _ in covered}
    training_types = {training_type for _, training_type in covered}
    eligible_held_out = [str(held_out_id) for held_out_id in held_out_ids if perturbation_types_of_id.get(str(held_out_id)) in held_out_types]
    eligible_training = [str(training_id) for training_id in training_ids if perturbation_types_of_id.get(str(training_id)) in training_types]
    neighbours: dict[str, dict[str, int]] = {}
    for held_out_id, shared_node_count in leaked_neighbours(eligible_held_out, eligible_training, reached_nodes_of_perturbation).items():
        held_out_type = perturbation_types_of_id[held_out_id]
        kept = {training_id: count for training_id, count in shared_node_count.items()
                if (held_out_type, perturbation_types_of_id[training_id]) in covered}
        if kept:
            neighbours[held_out_id] = kept
    return neighbours


def neighbours_through_the_channels(held_out_ids, training_ids, seed_nodes_of_perturbation, reached_nodes_of_perturbation=None,
                                    perturbation_types_of_id: dict[str, str] | None = None,
                                    reached_node_type_pairs=None) -> dict[str, dict[str, int]]:
    """The adversary's neighbours over every channel it is given: the shared seed node channel always, and the
    reached-node channel when reached_nodes_of_perturbation is passed, with the type pairs it covers.

    Without the reached-node arguments this is leaked_neighbours exactly, so every run made before the channel existed
    is unchanged. With them, a covered pair's weight is its count of shared reached nodes. A reached set holds the
    perturbation's own seeds, so that count already counts every seed node the pair shares; the larger of the two
    counts is taken rather than their sum, which would count a shared seed node twice.
    """
    shared_seed_node = leaked_neighbours(held_out_ids, training_ids, seed_nodes_of_perturbation)
    if reached_nodes_of_perturbation is None:
        if reached_node_type_pairs is not None:
            raise ValueError("reached_node_type_pairs was given without reached_nodes_of_perturbation")
        return shared_seed_node
    if perturbation_types_of_id is None or reached_node_type_pairs is None:
        raise ValueError("the reached-node channel needs perturbation_types_of_id and reached_node_type_pairs")
    combined = {held_out_id: dict(shared_node_count) for held_out_id, shared_node_count in shared_seed_node.items()}
    reached = reached_node_neighbours(held_out_ids, training_ids, reached_nodes_of_perturbation, perturbation_types_of_id,
                                      reached_node_type_pairs)
    for held_out_id, shared_node_count in reached.items():
        row = combined.setdefault(held_out_id, {})
        for training_id, count in shared_node_count.items():
            row[training_id] = max(row.get(training_id, 0), count)
    return combined


def seen_reached_node_share(reached_nodes_of_perturbation, held_out_ids, training_ids, perturbation_types_of_id: dict[str, str],
                            reached_node_type_pairs) -> float:
    """A label-free statistic of the reached-node channel, built as seen_target_share is: over the held-out
    perturbations of a covered held-out type, the share of the nodes they reach that a training perturbation of a type
    paired with theirs also reaches. NaN when no held-out perturbation is of a covered type or none reaches a node.

    It is one candidate. Which label-free statistic, or which set of them, the draw is checked against once this
    channel enters the adversary is not ruled, so experiments/calibrate_leakage_ceiling.py takes it as a required
    argument.
    """
    covered = validated_type_pairs(reached_node_type_pairs)
    nodes_reached_by_training_type: dict[str, set[str]] = {}
    for training_id in training_ids:
        kind = perturbation_types_of_id.get(str(training_id), "")
        nodes_reached_by_training_type.setdefault(kind, set()).update(reached_nodes_of_perturbation.get(str(training_id), ()))
    seen, total = 0, 0
    for held_out_id in held_out_ids:
        kind = perturbation_types_of_id.get(str(held_out_id), "")
        partner_types = {training_type for held_out_type, training_type in covered if held_out_type == kind}
        if not partner_types:
            continue
        reached_by_partners: set[str] = set()
        for training_type in partner_types:
            reached_by_partners |= nodes_reached_by_training_type.get(training_type, set())
        own = reached_nodes_of_perturbation.get(str(held_out_id), frozenset())
        seen += len(own & reached_by_partners)
        total += len(own)
    return float(seen) / total if total else float("nan")


def registered_channel_list(reached_node_hops: int | None = None, reached_node_type_pairs=None,
                            reach_edge_set: str | None = None) -> dict:
    """The channels the adversary scores and the ones it does not, as a lockbox record names them (decision 9.35:
    "The channel list is registered, and a channel found later is a disclosed limitation, not grounds for a redraw").
    reached_node_hops None is the reached-node channel switched off."""
    scored = [{"channel": "shared_seed_node", "covers": "every pair of perturbations",
               "definition": "a training perturbation seeding a node the held-out perturbation seeds"}]
    if reached_node_hops is None:
        if reached_node_type_pairs is not None or reach_edge_set is not None:
            raise ValueError("reached_node_type_pairs and reach_edge_set describe the reached-node channel; pass reached_node_hops with them")
        not_scored = ["a node reached from both perturbations' seeds by a forward walk, beyond the shared seed nodes "
                      "(the reached-node channel of decision 9.36, switched off here)"]
    else:
        if reach_edge_set not in REACH_EDGE_SETS:
            raise ValueError(f"reach_edge_set must be one of {REACH_EDGE_SETS}, not {reach_edge_set!r}")
        pairs = sorted(validated_type_pairs(reached_node_type_pairs))
        scored.append({"channel": "reached_node", "maximum_hops": int(reached_node_hops), "reach_edge_set": reach_edge_set,
                       "covers": [{"held_out_type": held_out_type, "training_type": training_type} for held_out_type, training_type in pairs],
                       "definition": f"a training perturbation whose forward walk of at most {int(reached_node_hops)} steps reaches a node "
                                     "the held-out perturbation's walk of the same length reaches"})
        not_scored = [f"a node reached from both perturbations' seeds only by a walk longer than {int(reached_node_hops)} steps",
                      "a node reached by both perturbations of a (held-out type, training type) pair the reached-node channel does not cover"]
    not_scored.append("any channel not listed here, which is a disclosed limitation and not grounds for a redraw (decision 9.35)")
    return {"scored": scored, "not_scored": not_scored}


def channel_breakdown(neighbours, perturbation_types_of_id: dict[str, str]) -> dict[str, int]:
    """Which side of the open channel each leaked pair comes through, so the registered channel list is counted rather
    than asserted: a training **drug** sharing a target, or the training **gene** perturbation of one of those targets.
    It counts the neighbour map it is given, so with the reached-node channel in that map a training gene paired with
    a held-out gene through a reached node is counted under pairs_through_a_training_gene too."""
    counts = {"held_out_with_a_leaked_neighbour": len(neighbours), "pairs_through_a_training_drug": 0,
              "pairs_through_a_training_gene": 0, "pairs_through_another_type": 0}
    for shared_node_count in neighbours.values():
        for training_id in shared_node_count:
            kind = perturbation_types_of_id.get(training_id, "")
            key = {"drug": "pairs_through_a_training_drug", "gene": "pairs_through_a_training_gene"}.get(kind, "pairs_through_another_type")
            counts[key] += 1
    return counts


class LeakageOnlyAdversary:
    """Predicts a held-out perturbation's symptoms from the labels of its neighbours: the training perturbations the
    neighbour map passed to predict names (leaked_neighbours, the shared seed node channel, or
    neighbours_through_the_channels, which adds the reached-node channel of decision 9.36).

    Exposes fit/predict like the baselines of `models/baselines`, so the same reading scores it: the advantage it earns
    over the same baseline, in the same macro and micro AUPRC, is the leakage expressed in the units of the test.
    """

    def __init__(self, pooling_rule: str = "base_rate_shrunk_mean", base_rate_prior_strength: float = BASE_RATE_PRIOR_STRENGTH) -> None:
        if pooling_rule not in POOLING_RULES:
            raise ValueError(f"pooling_rule must be one of {POOLING_RULES}, not {pooling_rule!r}")
        self.pooling_rule = pooling_rule
        self.base_rate_prior_strength = float(base_rate_prior_strength)
        self.symptom_base_rate: np.ndarray | None = None
        self.training_kept_positive: np.ndarray | None = None
        self.training_row_of_id: dict[str, int] = {}

    def fit(self, training_ids, training_outcomes: np.ndarray, training_label_mask: np.ndarray | None = None) -> "LeakageOnlyAdversary":
        """training_outcomes [num_training, num_symptoms] in {0, 1}; with a label mask the base rate and the looked-up
        labels both run over the labelled pairs only, as in the trainer's loss and in PopularityBaseline."""
        labelled = np.ones(training_outcomes.shape, dtype=bool) if training_label_mask is None else np.asarray(training_label_mask, dtype=bool)
        self.training_kept_positive = np.asarray(training_outcomes, dtype=float) * labelled
        self.symptom_base_rate = self.training_kept_positive.sum(axis=0) / np.maximum(labelled.sum(axis=0), 1)
        self.training_row_of_id = {str(training_id): row for row, training_id in enumerate(training_ids)}
        return self

    def predict(self, held_out_ids, neighbours: dict[str, dict[str, int]]) -> np.ndarray:
        """[num_held_out, num_symptoms]. A held-out perturbation with no leaked neighbour takes the training base rate.

        Under nearest_neighbour_maximum, neighbours tied on the largest weight go to the lowest training row (the order
        of the ids given to fit), so the score does not depend on the order of the neighbour map."""
        if self.symptom_base_rate is None or self.training_kept_positive is None:
            raise RuntimeError("fit before predict")
        scores = np.tile(self.symptom_base_rate, (len(held_out_ids), 1))
        for row, held_out_id in enumerate(held_out_ids):
            shared_node_count = neighbours.get(str(held_out_id))
            if not shared_node_count:
                continue
            rows_of_neighbours, weights = [], []
            for training_id, shared in shared_node_count.items():
                training_row = self.training_row_of_id.get(training_id)
                if training_row is not None:
                    rows_of_neighbours.append(training_row)
                    weights.append(float(shared))
            if not rows_of_neighbours:
                continue
            neighbour_labels = self.training_kept_positive[rows_of_neighbours]
            weight_vector = np.asarray(weights, dtype=float)
            if self.pooling_rule == "nearest_neighbour_maximum":
                largest_weight = max(weights)
                lowest_training_row_with_the_largest_weight = min(
                    training_row for training_row, weight in zip(rows_of_neighbours, weights) if weight == largest_weight)
                scores[row] = self.training_kept_positive[lowest_training_row_with_the_largest_weight]
            elif self.pooling_rule == "shared_node_weighted_mean":
                scores[row] = (neighbour_labels * weight_vector[:, None]).sum(axis=0) / weight_vector.sum()
            else:  # base_rate_shrunk_mean
                looked_up = (neighbour_labels * weight_vector[:, None]).sum(axis=0)
                total_weight = weight_vector.sum() + self.base_rate_prior_strength
                scores[row] = (looked_up + self.base_rate_prior_strength * self.symptom_base_rate) / total_weight
        return scores


def seen_target_share(targets_of_drug: dict[str, set[str]], held_out_ids) -> float:
    """A label-free statistic of the shared seed node channel on the drug side: over the held-out drugs, the share of
    their mechanism targets that a training drug also has. Decision 9.35 proposed fitting the adversary's advantage
    against it.

    It reads no label, so it can be computed on the real draw without opening the lockbox, which is what lets a ceiling
    calibrated on development pseudo-draws be applied to the draw that counts. With the reached-node channel of 9.36 in
    the adversary, whether the draw is checked against this statistic, against seen_reached_node_share or against both
    is not ruled, and experiments/calibrate_leakage_ceiling.py takes it as a required argument.
    """
    held = {str(held_out_id) for held_out_id in held_out_ids}
    trained_targets = {target for drug, own in targets_of_drug.items() if drug not in held for target in own}
    seen, total = 0, 0
    for drug, own in targets_of_drug.items():
        if drug in held:
            seen += len(own & trained_targets)
            total += len(own)
    return float(seen) / total if total else float("nan")
