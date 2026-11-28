"""Drawing the held-out set by holding out mechanism targets (preregistration amendment item 25, 13 October 2026).

The rule, and what is principled about it. A drug is held out **whole** when any of its mechanism targets is in the
held-out target partition, because the claim under test is about mechanism and not about drug identity, and this is
what puts a mechanism the model never trained on into every held-out drug. The owner, 13 October 2026: "NOT splitting
on drug itself but splitting on each target individually"; and of the drug split it replaces, "i have to just accept
that there will be some leakage" - which this is what avoids.

Why the drug split could not stand, measured over 200 draws: 84.4 percent of held-out drugs had **every** target
already present in a training drug, because the drugs genuinely share mechanisms, and grouping hard enough to remove
that gives one block holding 90 percent of them.

What is a convention, said plainly rather than dressed up (the owner: "that's not principled; it's just pushing the
arbitrariness further down the chain"). The **size** of the held-out set is a convention. Inside a one-shot lockbox
design nothing can make it otherwise; only cross-validation removes the choice, and leave-one-target-out, which has no
convention in it at all, costs 192 folds against the registered 60 runs for the same split quality. One seventh is
legitimate because it was fixed long before this rule existed, not because it is derived.

The gene perturbation of a held-out target. A gene perturbation is held out with a held-out target when one of the
nodes it seeds **is** that target. On a merged graph a drug and the loss of function of its target gene seed the same
gene node, so the gene perturbation is held out with the target (and its disease cluster is not); otherwise the model
learns what that node does from the gene and is credited for it on the drug, which is the leak
`merge_drugs_with_their_targets` was written to stop. On a gene/protein split graph (docs/gene_protein_split.md) the
default rule does **not** do this: a drug seeds its targets' protein nodes and a gene perturbation seeds its gene node,
so no seed matches, and the gene perturbation of a held-out protein target stays in training unless the gene side's
own rule happens to draw it (channel 2 of docs/drafts/held_out_draw_methods_2026-11-28.md, section 2). The one
exception is a target gene the split gave no protein node: a drug still seeds that gene node
(experiment_data.drug_seeds_on_proteins), so its gene perturbation is matched and held out as on a merged graph. Until
28 November 2026 this docstring said the gene perturbation of a held-out target "goes with it" without that
qualification, and decision 9.35's decision cell still counts it as closed.

Options (HeldOutDrawOptions; built 28 November 2026 from that draft's M1 and M2; **none is ruled**, and each default is
the rule as it stands, so a caller that passes none draws exactly what it drew before):

- hold_out_genes_encoding_held_out_targets: channel 2 closed by identity on a split graph. A gene perturbation is also
  held out when the gene node it seeds encodes a held-out target protein, read from the graph's gene_to_protein.parquet
  (experiment_data.read_proteins_encoded_by_gene), not from a walk.
- hold_out_whole_groups_of_those_genes: M1's closure. Each gene perturbation held out with a held-out target takes the
  rest of its leakage group with it, counted first on the gene side; the gene side's rule then fills the side up to the
  fraction. When those forced groups alone pass the fraction, the side stops at them and the overshoot is recorded,
  and the seed is not refused.
- gene_side_rule: "fold_zero", the rule as it stands (fold 0 of the grouped folds), or "seeded_group_prefix", M2: the
  gene side's whole groups in the seed's order, kept to the prefix whose share of the genes is nearest the fraction,
  which is the rule held_out_targets applies to targets (its edge rule is in seeded_group_prefix).
"""
from __future__ import annotations

import dataclasses
import math
import random
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from mechanistic_pathway_learning.evaluation.perturbation_wise_and_pathway_wise_splits import assign_grouped_folds

REGISTERED_HELD_OUT_FRACTION = 1 / 7
# a draw stops growing once it is this far past the registered fraction, since no later prefix can be nearer
STOP_SEARCHING_PAST = 0.05
# The gene side's rules: fold 0 of the grouped folds (the rule as it stands) and M2's seeded prefix of whole groups.
GENE_SIDE_RULES = ("fold_zero", "seeded_group_prefix")


@dataclass(frozen=True)
class HeldOutDrawOptions:
    """The opt-in options of the held-out draw (the module docstring says what each does). Built 28 November 2026 from
    docs/drafts/held_out_draw_methods_2026-11-28.md; none is ruled. HeldOutDrawOptions() is the rule as it stands."""

    hold_out_genes_encoding_held_out_targets: bool = False
    hold_out_whole_groups_of_those_genes: bool = False
    gene_side_rule: str = "fold_zero"

    def __post_init__(self) -> None:
        if self.gene_side_rule not in GENE_SIDE_RULES:
            raise ValueError(f"gene_side_rule must be one of {GENE_SIDE_RULES}, not {self.gene_side_rule!r}")
        if self.hold_out_whole_groups_of_those_genes and not self.hold_out_genes_encoding_held_out_targets:
            raise ValueError("M1's closure holds out the groups of the gene perturbations held out with a held-out target, "
                             "so it needs hold_out_genes_encoding_held_out_targets, without which a split graph matches none")

    def is_default(self) -> bool:
        return self == HeldOutDrawOptions()

    def as_record(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_record(cls, record: dict | None) -> "HeldOutDrawOptions":
        """The options a record names. A record without them (None) was drawn by the rule as it stands, which is what
        every record written before 28 November 2026 drew."""
        return cls() if record is None else cls(**record)


@dataclass(frozen=True)
class TwoSidedDraw:
    """One draw of two_sided_held_out_draw, with what the options did."""

    held_out_ids: set[str]
    held_out_target_ids: set[str]
    # the perturbations that are not drugs held out because a node they seed is, or (with the identity option) the gene
    # they seed encodes, a held-out target
    held_with_their_targets_ids: set[str]
    # M1: the groups of those, and every perturbation that is not a drug in them; all empty without the closure
    forced_group_ids: set[str]
    forced_gene_side_ids: set[str]
    forced_share_of_the_gene_side: float  # forced_gene_side_ids over every perturbation that is not a drug
    forced_groups_pass_the_fraction: bool
    overshoot: float  # forced_share_of_the_gene_side - held_out_fraction when the forced groups pass it, else 0.0


def targets_of_drugs(perturbation_ids, perturbation_types, perturbation_seeds, node_ids) -> dict[str, set[str]]:
    """perturbation id -> the node ids it seeds, for the drug perturbations only."""
    names = list(node_ids)
    return {str(perturbation_id): {names[int(seed)] for seed in seeds if 0 <= int(seed) < len(names)}
            for perturbation_id, kind, seeds in zip(perturbation_ids, perturbation_types, perturbation_seeds)
            if kind == "drug"}


def held_out_targets(targets_of_drug: dict[str, set[str]], seed: int,
                     held_out_fraction: float = REGISTERED_HELD_OUT_FRACTION) -> set[str]:
    """The held-out target partition: targets in the seed's order, kept to the prefix whose held-out share of drugs
    lands nearest the registered fraction.

    The count of targets is a consequence of that fraction and of how promiscuous the drugs happen to be, so it moves
    on its own when a rebuild changes the target sets. Which targets, and in which order, is the seed's alone.

    When the first target in the order is held by more than twice the fraction of the drugs, the empty prefix is nearer
    the fraction than any other and the partition comes back empty (docs/drafts/held_out_draw_methods_2026-11-28.md,
    section M2). No rule for that case is registered and none is built here."""
    drugs = sorted(targets_of_drug)
    if not drugs:
        return set()
    every_target = sorted({target for own in targets_of_drug.values() for target in own})
    order = list(every_target)
    random.Random(seed).shuffle(order)
    held, best_gap, best = set(), abs(0.0 - held_out_fraction), set()
    for target in order:
        held = held | {target}
        share = sum(1 for drug in drugs if targets_of_drug[drug] & held) / len(drugs)
        gap = abs(share - held_out_fraction)
        if gap < best_gap:
            best_gap, best = gap, set(held)
        elif share > held_out_fraction + STOP_SEARCHING_PAST:
            break  # no longer prefix can be nearer, since the share only grows
    return best


def held_out_perturbations(perturbation_ids, perturbation_types, perturbation_seeds, node_ids, seed: int,
                           held_out_fraction: float = REGISTERED_HELD_OUT_FRACTION,
                           gene_node_of_perturbation: dict[str, str] | None = None,
                           proteins_encoded_by_gene: Mapping[str, Iterable[str]] | None = None) -> tuple[set[str], set[str]]:
    """(the held-out perturbation ids, the held-out target node ids).

    A drug is held out when any of its targets is. A perturbation that is not a drug is held out when a node it seeds is
    a held-out target, so the model cannot learn that node's effect from the gene and be credited for it on the drug.
    That match is by node identity, so it holds the gene perturbation out on a merged graph, where a drug and the loss
    of its target gene seed one gene node, and not on a gene/protein split graph, where the drug seeds protein nodes and
    the gene perturbation its gene node; there it stays in training (the module docstring has the one exception).

    gene_node_of_perturbation adds one node per perturbation to what it is matched by. A gene node id is never a protein
    node id, so on a split graph it changes nothing, and no caller passes it (28 November 2026).

    proteins_encoded_by_gene (gene node id -> the protein node ids it encodes; experiment_data.read_proteins_encoded_by_gene)
    is the identity option: a perturbation that is not a drug is also held out when a gene node it seeds encodes a
    held-out target. None, the default, is the rule as it stands; on a merged graph the map is empty and changes nothing."""
    targets_of_drug = targets_of_drugs(perturbation_ids, perturbation_types, perturbation_seeds, node_ids)
    held_targets = held_out_targets(targets_of_drug, seed, held_out_fraction)
    held = {drug for drug, own in targets_of_drug.items() if own & held_targets}
    names = list(node_ids)
    for perturbation_id, kind, seeds in zip(perturbation_ids, perturbation_types, perturbation_seeds):
        if kind == "drug":
            continue
        own = {names[int(index)] for index in seeds if 0 <= int(index) < len(names)}
        if gene_node_of_perturbation and str(perturbation_id) in gene_node_of_perturbation:
            own = own | {gene_node_of_perturbation[str(perturbation_id)]}
        if proteins_encoded_by_gene is not None:
            own = own | {protein for node in own for protein in proteins_encoded_by_gene.get(node, ())}
        if own & held_targets:
            held.add(str(perturbation_id))
    return held, held_targets


def seeded_group_prefix(gene_side_count_of_group: Mapping[str, int], seed: int, held_out_fraction: float,
                        num_gene_side_perturbations: int, forced_count: int = 0) -> list[str]:
    """M2: the gene side's groups in the seed's order, kept to the prefix whose share of the gene side, counted after
    the forced_count perturbations M1 already put there, is nearest held_out_fraction. gene_side_count_of_group holds
    each candidate group's count of perturbations that are not drugs (a forced group is not a candidate).

    This is held_out_targets' rule with groups in place of targets, and with one edge rule of its own (built 28 November
    2026, **not ruled**): the side is never empty while a group can be held out. As held_out_targets is written, when the
    first unit in the order alone holds more than twice the fraction the empty prefix is nearer the fraction than any
    other, the side comes back empty, its statistic is not a finite number, and draw_passes refuses the seed: the seed
    would fail on a property of the split and not of its leakage. So the empty prefix is a candidate only when M1 has
    forced perturbations onto the side; otherwise the nearest non-empty prefix is kept, which in that case is the first
    group alone, and the side overshoots the fraction by that group. A tie keeps the shorter prefix, as held_out_targets
    does."""
    if num_gene_side_perturbations <= 0:
        return []
    order = sorted(gene_side_count_of_group)
    random.Random(seed).shuffle(order)
    count_so_far = forced_count
    best_prefix_length = 0 if forced_count else None
    best_gap = abs(forced_count / num_gene_side_perturbations - held_out_fraction) if forced_count else math.inf
    for prefix_length, group in enumerate(order, start=1):
        count_so_far += gene_side_count_of_group[group]
        share = count_so_far / num_gene_side_perturbations
        gap = abs(share - held_out_fraction)
        if gap < best_gap:
            best_gap, best_prefix_length = gap, prefix_length
        elif share > held_out_fraction + STOP_SEARCHING_PAST:
            break  # no longer prefix can be nearer, since the share only grows
    return order[:best_prefix_length or 0]


def two_sided_held_out_draw(perturbation_ids, perturbation_types, perturbation_seeds, node_ids, group_ids, seed: int,
                            held_out_fraction: float = REGISTERED_HELD_OUT_FRACTION,
                            options: HeldOutDrawOptions | None = None,
                            proteins_encoded_by_gene: Mapping[str, Iterable[str]] | None = None) -> TwoSidedDraw:
    """two_sided_held_out_perturbations with what the options did: the perturbations held out with their targets, M1's
    forced groups and their overshoot. With options None or HeldOutDrawOptions() it draws exactly what
    two_sided_held_out_perturbations drew before the options existed (tests/test_target_held_out_split.py holds a copy
    of that code and checks it). proteins_encoded_by_gene is required with hold_out_genes_encoding_held_out_targets; on
    a merged graph it is the empty map.

    The gene side is every perturbation that is not a drug. Under M1's closure a forced group's drugs stay where the
    drug side's target rule puts them, since the drug side is that rule's alone; a group holds drugs only under a
    grouping that joins them to genes (disease_cluster_and_targets)."""
    options = options or HeldOutDrawOptions()
    if options.hold_out_genes_encoding_held_out_targets and proteins_encoded_by_gene is None:
        raise ValueError("the identity option needs proteins_encoded_by_gene (experiment_data.read_proteins_encoded_by_gene; "
                         "the empty map on a merged graph)")
    held_out_ids, held_out_target_ids = held_out_perturbations(
        perturbation_ids, perturbation_types, perturbation_seeds, node_ids, seed, held_out_fraction,
        proteins_encoded_by_gene=proteins_encoded_by_gene if options.hold_out_genes_encoding_held_out_targets else None)
    type_of = {str(perturbation_id): kind for perturbation_id, kind in zip(perturbation_ids, perturbation_types)}
    group_of = {str(perturbation_id): group for perturbation_id, group in zip(perturbation_ids, group_ids)}
    gene_side_ids = [str(perturbation_id) for perturbation_id, kind in zip(perturbation_ids, perturbation_types) if kind != "drug"]
    held_with_their_targets_ids = {perturbation_id for perturbation_id in held_out_ids if type_of[perturbation_id] != "drug"}

    forced_group_ids: set[str] = set()
    if options.hold_out_whole_groups_of_those_genes:
        forced_group_ids = {group_of[perturbation_id] for perturbation_id in held_with_their_targets_ids}
    forced_gene_side_ids = {perturbation_id for perturbation_id in gene_side_ids if group_of[perturbation_id] in forced_group_ids}
    forced_share = len(forced_gene_side_ids) / len(gene_side_ids) if gene_side_ids else 0.0
    forced_groups_pass_the_fraction = bool(forced_group_ids) and forced_share > held_out_fraction
    overshoot = forced_share - held_out_fraction if forced_groups_pass_the_fraction else 0.0

    if forced_groups_pass_the_fraction:
        held_out_ids |= forced_gene_side_ids  # the side stops at the forced groups; the seed is not refused
    elif options.gene_side_rule == "fold_zero":
        # The rule as it stands; with M1's closure the forced groups are placed in fold 0 before the balance starts.
        num_grouped_folds = int(round(1 / held_out_fraction))
        fold_of_perturbation = assign_grouped_folds(perturbation_ids, group_ids, num_grouped_folds, seed,
                                                    groups_placed_in_fold_zero=forced_group_ids)
        for perturbation_id, kind in zip(perturbation_ids, perturbation_types):
            if kind != "drug" and fold_of_perturbation[perturbation_id] == 0:
                held_out_ids.add(str(perturbation_id))
    else:
        candidate_count_of_group = Counter(group_of[perturbation_id] for perturbation_id in gene_side_ids
                                           if group_of[perturbation_id] not in forced_group_ids)
        prefix_groups = set(seeded_group_prefix(candidate_count_of_group, seed, held_out_fraction, len(gene_side_ids),
                                                forced_count=len(forced_gene_side_ids)))
        held_out_ids |= forced_gene_side_ids
        held_out_ids |= {perturbation_id for perturbation_id in gene_side_ids if group_of[perturbation_id] in prefix_groups}
    return TwoSidedDraw(held_out_ids=held_out_ids, held_out_target_ids=held_out_target_ids,
                        held_with_their_targets_ids=held_with_their_targets_ids, forced_group_ids=forced_group_ids,
                        forced_gene_side_ids=forced_gene_side_ids, forced_share_of_the_gene_side=forced_share,
                        forced_groups_pass_the_fraction=forced_groups_pass_the_fraction, overshoot=overshoot)


def two_sided_held_out_perturbations(perturbation_ids, perturbation_types, perturbation_seeds, node_ids, group_ids,
                                     seed: int, held_out_fraction: float = REGISTERED_HELD_OUT_FRACTION,
                                     options: HeldOutDrawOptions | None = None,
                                     proteins_encoded_by_gene: Mapping[str, Iterable[str]] | None = None) -> tuple[set[str], set[str]]:
    """(the held-out perturbation ids, the held-out target node ids) with **each side at its own registered fraction**
    (item 25: "the genes by the registered disease-cluster grouping and the drugs by the rule below, one seventh of
    each rather than one seventh of the whole").

    The drug side is held_out_perturbations: every drug with a held-out target, and every perturbation that is not a
    drug whose own seed node is a held-out target, which on a split graph is almost none (its docstring says why). The
    gene side, every perturbation that is not a drug, is fold 0 of round(1 / held_out_fraction) grouped folds of
    group_ids (assign_grouped_folds with the same seed), so no leakage group of the grouping the caller loaded is split
    within that side; a drug held out by its targets can still share a group with a gene in training, which is item
    25's rule and not a defect of it. Moved here on 27 November 2026 from experiments/measure_leakage_only_adversary.py
    (registered_two_sided_draw, which now calls it), so the measurement and experiments/draw_held_out_set.py draw by
    one implementation.

    options and proteins_encoded_by_gene are the opt-in options of the module docstring, off by default, under which
    this returns what it returned before they existed; two_sided_held_out_draw returns the same draw with what the
    options did (M1's forced groups and overshoot).
    """
    draw = two_sided_held_out_draw(perturbation_ids, perturbation_types, perturbation_seeds, node_ids, group_ids, seed,
                                   held_out_fraction, options, proteins_encoded_by_gene)
    return draw.held_out_ids, draw.held_out_target_ids


def mechanisms_never_trained(targets_of_drug: dict[str, set[str]], held: set[str]) -> dict[str, set[str]]:
    """Per held-out drug, the targets no training drug has: what the unseen-mechanism stratum of item 25c is scored on.

    Under this rule every held-out drug has at least one, by construction. A drug for which it is **all** of them is in
    the stratum; the rest have part of their mechanism in training, which the registration states as the price of
    keeping the label exact."""
    trained_targets = {target for drug, own in targets_of_drug.items() if drug not in held for target in own}
    return {drug: targets_of_drug[drug] - trained_targets for drug in held if drug in targets_of_drug}
