"""The labels' positive-unlabelled likelihood: every pair counted once, at its code length (decision 9.90).

The owner, 22 October 2026: "labeled / unlabeled costs formulation accepted. same fix for module size cost is also
fine ... silence change folding into the same likelihood change is fine", and "each label should only be counted once
in the MDL calculation". This replaces the weighted cross-entropy of soft_constraint_losses (a positive at its evidence
weight, an unlabelled pair at --negative-weight, an evidenced negative at its placebo weight) with the likelihood of a
labelling process, behind run_main_model.py --label-likelihood positive_unlabelled.

Notation. f is the head's probability that the link is real (the noisy-OR P). A real link is labelled with
probability e and a link that is not real is labelled with probability b, the false-report rate of the row's evidence
class, so P(labelled positive) = e f + b (1 - f). Writing e = b + (1 - b) pi turns this into the noisy-OR of a
false-report leak and the propensity-scaled link, P(labelled positive) = 1 - (1 - b)(1 - pi f), which keeps e above b
for every pi in (0, 1), so a label always argues for the link. Per pair, in nats:

    labelled positive     L = -log(b + (1 - b) pi f)
    unlabelled pair       L = -log(1 - b) - log(1 - pi f)
    evidenced negative    L = -log(1 - a f)

where a is the power of the assessment that found the pair absent (the probability that it would have found a real
link). At pi = 1, b = 0 and a = 1 this is the plain binary cross-entropy -[y log f + (1 - y) log(1 - f)].

What the old weights become. At small f the gradient of the unlabelled term is pi / (1 - pi f), close to pi, and that
of the weighted negative was w / (1 - f), close to w (w = --negative-weight, 0.2), so the weighted loss is this
likelihood at pi = w in the limit of rare labels. What changes is the rest: the cost of an unlabelled pair is bounded
by -log(1 - b) - log(1 - pi), where the weighted negative grew without bound as f approached 1, so silence never forces
a link to zero; f is the probability that the link is real, and pi f the probability that it is labelled; and a label
is one observation whatever its grade.

The propensity (Bekker, Robberechts and Davis 2019, arXiv 1809.03207: "the propensity score needs to depend on fewer
attributes than the final classifier"). pi(x, s) = sigmoid(logit(pi_0(t, s)) + c (z(x) - z_0)), t the perturbation's
type and s the symptom, z its log(1 + literature popularity) (distinct PubMed ids in a literature report table, the
feature decision 9.59 gives its calibrated reliability) and z_0 the median of z over the rows the fit trains on.
pi_0(t, s), the propensity of the cell at the median popularity, is fixed; the one slope c is learned jointly with f.
Without a literature table c is absent and pi is constant within a cell, the selected-completely-at-random assumption
(Elkan and Noto 2008, KDD: "c = p(s = 1|y = 1) is the constant probability that a positive example is labeled") applied
per cell.

Why pi_0 is fixed and not learned. For the rare links that make up most pairs, f is close to the leak plus the summed
links times activations, so multiplying pi by a constant and dividing every leak and link of a symptom by it leaves
pi f unchanged: an intercept of pi is not identified against the head's own scale above the bound below, and a
learned one would sit wherever its start put it. The popularity slope is identified because popularity is not an input
of f: the field is computed from the graph alone. A learned perturbation-type offset is left out for the same reason:
the field can tell a drug from a gene (they enter at different nodes), so a type offset of pi and a type effect in f
trade against each other.

What the data do fix is a lower bound. P(labelled) = pi f <= pi, so no propensity below the labelled share r of a cell
can produce that share, and a constant propensity below it drives f to 1 for every pair of the cell, where the
noisy-OR has no gradient left. On the v5 tables the labelled share reaches 0.68 for intellectual disability among the
genes (the next gene symptom is at 0.17) and 0.87 for somnolence among the drugs, so pi = 0.2 is not available for
those cells. The default (--labelling-propensity derived) is pi_0(t, s) = w + (1 - w) r(t, s), w = --negative-weight
and r(t, s) the labelled share of the cell's counted pairs on the fit rows: the propensity at which every cell keeps
the constant optimum of the registered weighted loss, since r / (w + (1 - w) r) = r / (r + w (1 - r)). It is above
every share, so no cell starts saturated, and it is w where labels are rare, so the registered balance of labels and
silence is kept to first order wherever it was set. It reads label completeness as varying with the symptom, as the
gene table's ascertainment on intellectual disability says it does. --labelling-propensity derived_by_type takes
pi_0(t) = w + (1 - w) max_s r(t, s) instead, one propensity per type (selected completely at random within a type),
which on v5 puts every gene symptom at 0.75 because of intellectual disability alone. Above the bound the choice is
the owner's.

The false-report rate b is 0 unless set per perturbation type (decision 9.90 gives the reasons). The power a of an
evidenced negative is read from a per-pair matrix, ExperimentData.evidenced_negative_power, with a constant fallback.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor, nn

from mechanistic_pathway_learning.models.soft_constraint_losses import PROBABILITY_EPSILON

LABEL_LIKELIHOODS: tuple[str, ...] = ("weighted", "positive_unlabelled")
DERIVED_PROPENSITY = "derived"  # --labelling-propensity: pi_0(t, s) = w + (1 - w) r(t, s) (module docstring)
DERIVED_PROPENSITY_BY_TYPE = "derived_by_type"  # pi_0(t) = w + (1 - w) max_s r(t, s)


def log_one_minus_scaled(scale: Tensor, probability: Tensor, log_probability: Tensor | None = None,
                         log_complement: Tensor | None = None) -> Tensor:
    """log(1 - s f) for s in [0, 1]. Given the head's log f and log(1 - f), it is computed exactly as
    log((1 - f) + (1 - s) f), so s = 1 gives log(1 - f) itself; otherwise f is clamped to [1e-6, 1 - 1e-6] as the
    weighted cross-entropy clamps it."""
    if log_probability is not None and log_complement is not None:
        return torch.logaddexp(log_complement, torch.log1p(-scale) + log_probability)
    return torch.log1p(-scale * probability.clamp(PROBABILITY_EPSILON, 1.0 - PROBABILITY_EPSILON))


def log_labelled_probability(propensity: Tensor, false_report_rate: Tensor, probability: Tensor,
                             log_probability: Tensor | None = None) -> Tensor:
    """log(b + (1 - b) pi f): exact from the head's log f when it is given, else from f clamped to [1e-6, 1 - 1e-6]."""
    if log_probability is not None:
        return torch.logaddexp(torch.log(false_report_rate), torch.log1p(-false_report_rate) + torch.log(propensity) + log_probability)
    clamped = probability.clamp(PROBABILITY_EPSILON, 1.0 - PROBABILITY_EPSILON)
    return torch.log(false_report_rate + (1.0 - false_report_rate) * propensity * clamped)


def pair_code_lengths(probability: Tensor, labelled_positive: Tensor, evidenced_negative: Tensor, propensity: Tensor,
                      false_report_rate: Tensor, assessment_power: Tensor, log_probability: Tensor | None = None,
                      log_complement: Tensor | None = None) -> Tensor:
    """The code length in nats of each pair's label (module docstring); every argument broadcasts to probability's
    shape. labelled_positive and evidenced_negative are 1.0 or 0.0 and never both 1; a pair with neither is unlabelled.
    The three terms are computed for every pair and selected by multiplication, so a pair of one kind takes no gradient
    from the formulas of the other two."""
    labelled_positive = labelled_positive.to(probability.dtype)
    evidenced_negative = evidenced_negative.to(probability.dtype)
    unlabelled = 1.0 - labelled_positive - evidenced_negative
    positive_term = log_labelled_probability(propensity, false_report_rate, probability, log_probability)
    unlabelled_term = torch.log1p(-false_report_rate) + log_one_minus_scaled(propensity, probability, log_probability, log_complement)
    negative_term = log_one_minus_scaled(assessment_power, probability, log_probability, log_complement)
    return -(labelled_positive * positive_term + unlabelled * unlabelled_term + evidenced_negative * negative_term)


def positive_unlabelled_binary_cross_entropy(probability: Tensor, labelled_positive: Tensor, evidenced_negative: Tensor, pair_weight: Tensor,
                                             propensity: Tensor, false_report_rate: Tensor, assessment_power: Tensor,
                                             log_probability: Tensor | None = None, log_complement: Tensor | None = None) -> Tensor:
    """The mean code length over the counted pairs of a batch: sum w L / sum w, w 1 on a counted pair and 0 on one the
    label selection set aside (or the equal drug shares' rescaled count). Its sum over a fit, times the fit's sum of w,
    is the labels' code length in nats."""
    lengths = pair_code_lengths(probability, labelled_positive, evidenced_negative, propensity, false_report_rate, assessment_power,
                                log_probability, log_complement)
    return (lengths * pair_weight).sum() / pair_weight.sum().clamp_min(PROBABILITY_EPSILON)


def popularity_of_perturbations(perturbation_ids: list[str], literature_reports, slot_ids=None) -> np.ndarray:
    """Distinct PubMed ids per perturbation in a literature report table (the count soft_priors.literature_popularity
    takes). A row is looked up under its slot id when one is given (a combination under its drug), and an allele
    ("GENE|allele") that the table does not name takes its gene's count, since a statement names a gene."""
    if literature_reports is None or literature_reports.empty or "pmid" not in literature_reports.columns:
        return np.zeros(len(perturbation_ids))
    literature = literature_reports
    if "evidence_class" in literature.columns:
        literature = literature[literature.evidence_class == "literature"]
    counts = literature.dropna(subset=["pmid"]).groupby("perturbation_id").pmid.nunique()
    lookup_ids = list(perturbation_ids) if slot_ids is None else [str(slot) for slot in slot_ids]
    popularity = []
    for identifier in lookup_ids:
        count = counts.get(identifier)
        if count is None and "|" in identifier:
            count = counts.get(identifier.split("|", 1)[0])
        popularity.append(float(count or 0))
    return np.asarray(popularity, dtype=float)


def labelled_shares_by_type(outcomes: np.ndarray, label_mask: np.ndarray | None, perturbation_types: list[str],
                            fit_rows: np.ndarray) -> dict[str, np.ndarray]:
    """Per perturbation type t, r(t, s) for every symptom s: the share of the type's counted pairs of the symptom on the
    fit rows that are labelled positive, the bound no propensity of that cell may be below. 0 where a cell has no
    counted pair on the fit rows."""
    rows = np.asarray(fit_rows, dtype=int)
    counted = np.ones_like(outcomes, dtype=bool) if label_mask is None else np.asarray(label_mask, dtype=bool)
    positive = (np.asarray(outcomes) > 0) & counted
    types = np.asarray(perturbation_types, dtype=object)
    shares = {}
    for kind in sorted(set(types.tolist())):
        of_kind = rows[types[rows] == kind]
        pairs = counted[of_kind].sum(axis=0)
        shares[kind] = np.divide(positive[of_kind].sum(axis=0), pairs, out=np.zeros(pairs.shape, dtype=float), where=pairs > 0)
    return shares


def derived_propensity(shares_by_type: dict[str, np.ndarray], negative_weight: float, by_symptom: bool = True) -> dict[str, np.ndarray]:
    """pi_0 = w + (1 - w) r (module docstring), w the registered negative weight: per type and symptom, r = r(t, s), so
    that every cell keeps the constant optimum of the weighted loss; or per type, r = max_s r(t, s), so that only the
    type's most-labelled symptom keeps it. Above every share it covers, and held below 1 - 1e-6."""
    if not 0.0 < negative_weight < 1.0:
        raise ValueError(f"the derived propensity needs a negative weight in (0, 1), not {negative_weight}")
    anchors = {}
    for kind, shares in shares_by_type.items():
        shares = np.asarray(shares, dtype=float)
        bound = shares if by_symptom else np.full(shares.shape, shares.max() if len(shares) else 0.0)
        anchors[kind] = np.minimum(negative_weight + (1.0 - negative_weight) * bound, 1.0 - PROBABILITY_EPSILON)
    return anchors


class LabellingPropensity(nn.Module):
    """pi(x, s) = sigmoid(logit(pi_0(t, s)) + c (z(x) - z_0)) (module docstring): pi_0 fixed per row and symptom (or per
    row, one column), one learned slope c on the centred log popularity when one is given, none otherwise. c starts at
    0, so every fit starts at the fixed propensities and moves from them only as far as the labels ask."""

    def __init__(self, anchor: np.ndarray, log_popularity: np.ndarray | None = None, centre: float = 0.0):
        super().__init__()
        anchor = np.asarray(anchor, dtype=float)
        if anchor.ndim == 1:
            anchor = anchor[:, None]
        if not ((anchor > 0.0) & (anchor < 1.0)).all():
            raise ValueError(f"a labelling propensity at the median popularity lies in (0, 1); given {sorted(set(anchor.ravel().tolist()))[:5]}")
        self.register_buffer("anchor_logit", torch.as_tensor(np.log(anchor) - np.log1p(-anchor), dtype=torch.float32))
        if log_popularity is None:
            self.register_buffer("centred_log_popularity", torch.zeros(len(anchor)))
            self.popularity_slope = None
        else:
            self.register_buffer("centred_log_popularity", torch.as_tensor(np.asarray(log_popularity, dtype=np.float32) - np.float32(centre)))
            self.popularity_slope = nn.Parameter(torch.zeros(()))
        self.centre = float(centre)

    def forward(self, rows) -> Tensor:
        """pi for the given perturbation rows, [len(rows), S] or [len(rows), 1] (one value for every symptom), so that it
        broadcasts over the symptoms; held inside [1e-6, 1 - 1e-6] so that log(1 - pi f) and its gradient stay finite."""
        rows = torch.as_tensor(np.asarray(rows), dtype=torch.long, device=self.anchor_logit.device)
        logit = self.anchor_logit[rows]
        if self.popularity_slope is not None:
            logit = logit + self.popularity_slope * self.centred_log_popularity[rows][:, None]
        return torch.sigmoid(logit).clamp(PROBABILITY_EPSILON, 1.0 - PROBABILITY_EPSILON)

    def summary(self) -> dict:
        slope = None if self.popularity_slope is None else float(self.popularity_slope.detach())
        values = self(np.arange(len(self.centred_log_popularity))).detach().cpu().numpy()
        return {"popularity_slope": slope, "median_log_popularity": self.centre,
                "learned_parameters": int(sum(parameter.numel() for parameter in self.parameters())),
                "propensity_range": [float(values.min()), float(values.max())] if len(values) else None}


@dataclass
class PositiveUnlabelledLabels:
    """What the likelihood reads per pair, over every perturbation of the data set: the labelled positives, the
    evidenced negatives, the power a of each evidenced negative's assessment and the false-report rate b of each row's
    evidence class, as tensors, with the propensity module. Built once per run (run_main_model.label_likelihood_labels)."""

    labelled_positive: Tensor  # [P, S] 1.0 where a counted pair is a labelled positive
    evidenced_negative: Tensor  # [P, S] 1.0 where a pair was assessed and found absent
    assessment_power: Tensor  # [P, S] a; read only where evidenced_negative is 1
    false_report_rate: Tensor  # [P, 1] b of the row's evidence class
    propensity: LabellingPropensity

    def inputs(self, rows, device, detach_propensity: bool = False) -> dict:
        rows_tensor = torch.as_tensor(np.asarray(rows), dtype=torch.long)
        propensity = self.propensity(rows)
        if detach_propensity:
            propensity = propensity.detach()
        return {"labelled_positive": self.labelled_positive[rows_tensor].to(device), "evidenced_negative": self.evidenced_negative[rows_tensor].to(device),
                "propensity": propensity.to(device), "false_report_rate": self.false_report_rate[rows_tensor].to(device),
                "assessment_power": self.assessment_power[rows_tensor].to(device)}

    def loss(self, probability: Tensor, rows, pair_weight: Tensor, log_probability: Tensor | None = None, log_complement: Tensor | None = None,
             detach_propensity: bool = False) -> Tensor:
        return positive_unlabelled_binary_cross_entropy(probability, pair_weight=pair_weight, log_probability=log_probability, log_complement=log_complement,
                                                        **self.inputs(rows, probability.device, detach_propensity))

    def code_lengths(self, probability: Tensor, rows, log_probability: Tensor | None = None, log_complement: Tensor | None = None) -> Tensor:
        return pair_code_lengths(probability, log_probability=log_probability, log_complement=log_complement,
                                 **self.inputs(rows, probability.device, detach_propensity=True))


def assessment_power_matrix(evidenced_negative: np.ndarray, stated_power: np.ndarray | None, placebo_weights: np.ndarray | None,
                            default_power: float) -> tuple[np.ndarray, dict]:
    """The power a per pair, read on the evidenced negatives: a source's own per-pair power where it states one
    (ExperimentData.evidenced_negative_power, NaN elsewhere), else amendment item 3's n_effective / (n_effective + 214.39)
    from the placebo weight file, else the default. Returns the matrix (0 off the evidenced negatives) and how many
    evidenced negatives took each source. A power outside [0, 1] is refused."""
    evidenced_negative = np.asarray(evidenced_negative, dtype=bool)
    if not 0.0 <= default_power <= 1.0:
        raise ValueError(f"an assessment's power lies in [0, 1], not {default_power}")
    power = np.full(evidenced_negative.shape, np.nan)
    counts = {"stated_by_the_source": 0, "placebo_weight_file": 0, "default": 0}
    for name, matrix in (("stated_by_the_source", stated_power), ("placebo_weight_file", placebo_weights)):
        if matrix is None:
            continue
        matrix = np.asarray(matrix, dtype=float)
        outside = np.isfinite(matrix) & ((matrix < 0.0) | (matrix > 1.0))
        if outside.any():
            raise ValueError(f"a power of {matrix[outside][0]} ({name}); an assessment's power lies in [0, 1]")
        fills = evidenced_negative & np.isnan(power) & np.isfinite(matrix)
        power[fills] = matrix[fills]
        counts[name] = int(fills.sum())
    defaults = evidenced_negative & np.isnan(power)
    power[defaults] = default_power
    counts["default"] = int(defaults.sum())
    return np.where(evidenced_negative, power, 0.0), counts


def false_report_rates(perturbation_types: list[str], rates_by_type: dict[str, float]) -> np.ndarray:
    """b per row, [P, 1]: the rate of the row's perturbation type, 0 for a type not named."""
    for kind, rate in rates_by_type.items():
        if not 0.0 <= rate < 1.0:
            raise ValueError(f"the false-report rate of {kind} is {rate}; it lies in [0, 1)")
    return np.array([[float(rates_by_type.get(kind, 0.0))] for kind in perturbation_types], dtype=np.float32)


def constant_optimum(labelled_positive: np.ndarray, evidenced_negative: np.ndarray, pair_weight: np.ndarray, propensity: np.ndarray,
                     false_report_rate: np.ndarray, assessment_power: np.ndarray, iterations: int = 80) -> np.ndarray:
    """Per symptom, the constant f that minimises sum w L over the given rows: the counted-once counterpart of
    run_main_model.weighted_constant_optimum. The sum is convex in f (each term is -log of a function linear in f), so
    its derivative

        sum_pos -w (1 - b) pi / (b + (1 - b) pi f) + sum_unl w pi / (1 - pi f) + sum_neg w a / (1 - a f)

    rises with f and the root is found by bisection on [1e-6, 1 - 1e-6]; at b = 0, a constant pi and no evidenced
    negative it is f = r / pi, r the weighted share of positives, capped below 1. Arrays are [rows, S], propensity and
    false_report_rate [rows, 1]."""
    positive = np.asarray(labelled_positive, dtype=float) * pair_weight
    negative = np.asarray(evidenced_negative, dtype=float) * pair_weight
    unlabelled = (1.0 - np.asarray(labelled_positive, dtype=float) - np.asarray(evidenced_negative, dtype=float)) * pair_weight
    pi = np.broadcast_to(np.asarray(propensity, dtype=float), positive.shape)
    b = np.broadcast_to(np.asarray(false_report_rate, dtype=float), positive.shape)
    a = np.asarray(assessment_power, dtype=float)

    def derivative(f: np.ndarray) -> np.ndarray:
        return (-(positive * (1.0 - b) * pi / (b + (1.0 - b) * pi * f)).sum(axis=0) + (unlabelled * pi / (1.0 - pi * f)).sum(axis=0)
                + (negative * a / np.maximum(1.0 - a * f, PROBABILITY_EPSILON)).sum(axis=0))

    low = np.full(positive.shape[1], PROBABILITY_EPSILON)
    high = np.full(positive.shape[1], 1.0 - PROBABILITY_EPSILON)
    for _ in range(iterations):
        middle = (low + high) / 2.0
        rising = derivative(middle[None, :]) > 0
        high = np.where(rising, middle, high)
        low = np.where(rising, low, middle)
    return (low + high) / 2.0


def group_weights(outcomes: np.ndarray, label_mask: np.ndarray | None, evidenced_negative: np.ndarray | None, weighted_pair_weights: np.ndarray,
                  counted_pair_weights: np.ndarray, rows: np.ndarray, propensity_by_row: np.ndarray | float) -> dict:
    """The three groups of pairs over the given rows, each with its count and its summed weight under the weighted loss
    and under counted-once coding, and the first-order weight an unlabelled pair carries under the likelihood (pi at
    small f, averaged over the group's pairs). The shares are each group's part of the total weight."""
    rows = np.asarray(rows, dtype=int)
    counted = np.ones_like(outcomes, dtype=bool) if label_mask is None else np.asarray(label_mask, dtype=bool)
    positive = (np.asarray(outcomes) > 0) & counted
    negative = np.zeros_like(positive) if evidenced_negative is None else (np.asarray(evidenced_negative, dtype=bool) & ~positive & counted)
    unlabelled = counted & ~positive & ~negative
    groups = {"labelled_positive": positive, "unlabelled": unlabelled, "evidenced_negative": negative}
    summary = {}
    totals = {"weighted": float(weighted_pair_weights[rows].sum()), "counted_once": float(counted_pair_weights[rows].sum())}
    for name, mask in groups.items():
        selected = mask[rows]
        weighted = float(weighted_pair_weights[rows][selected].sum())
        counted_once = float(counted_pair_weights[rows][selected].sum())
        summary[name] = {"pairs": int(selected.sum()), "weighted_loss_weight": round(weighted, 3), "counted_once_weight": round(counted_once, 3),
                         "weighted_share": round(weighted / totals["weighted"], 4) if totals["weighted"] else None,
                         "counted_once_share": round(counted_once / totals["counted_once"], 4) if totals["counted_once"] else None}
    propensity = np.asarray(propensity_by_row, dtype=float)
    propensity = np.broadcast_to(propensity[:, None] if propensity.ndim == 1 else propensity, np.asarray(outcomes).shape)[rows]
    silent = unlabelled[rows]
    summary["unlabelled"]["first_order_weight_per_pair_under_the_likelihood"] = round(float(propensity[silent].mean()), 4) if silent.any() else None
    summary["total_weight"] = {key: round(value, 3) for key, value in totals.items()}
    return summary
