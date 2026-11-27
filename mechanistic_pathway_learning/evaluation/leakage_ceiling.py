"""The leakage ceiling of decision 9.35 and the draw it gates: fit, invert, and accept the first passing seed.

**Status: an unreviewed draft** (written 27 November 2026 and pushed the same day at the owner's request, "Just merge
and push everything. I'll review it later"; until then it was held on a local branch for the owner to read first). It
encodes readings of 9.35 the owner has not confirmed, its open definitions are listed in the message of the commit that
added it, and two known defects are not fixed: reactome_release_of_graph reads the release from
graph_full_neuronal/neuronal_variant_summary.json, which no graph derived from that one carries, so on the registered
chain it raises and the draw cannot run; and ceilings_of_calibrations applies a least-squares ceiling extrapolated
beyond every pseudo-draw (statistic_ceiling's within_observed_range is False) as it applies one inside them. Nothing
here has been run on real data and no held-out set has been drawn with it.

What is ruled (decision 9.35, 24 November 2026; the owner: "Use 1.a but not on current graph. On graph at time of draw,
right?"). A leakage-only adversary (`evaluation/leakage_only_adversary.py`) predicts each held-out symptom from the
labels of training perturbations reachable through the registered channels only, and its advantage must stay below one
standard error of the test's own reading. Both are computed on the graph the draw is made on and on no graph before it.
The curve is fitted on development-set pseudo-draws, so no lockbox label is read, and it is inverted at the
one-standard-error threshold to give the value of a label-free statistic the real draw is checked against. The first
draw that passes is accepted, with the seed order fixed in advance; the channel list is registered; the
200-pseudo-draw median fallback is not taken. Decision 9.36 adds the k = 2 reached-node channel to the adversary, with
k as a sensitivity sweep. Registering the rule is an amendment item owed before the draw, so nothing here is
registered: it is the machinery that amendment would name. Which graph a calibration or a draw was made on is
checked by experiments/measure_leakage_only_adversary.graph_file_sha256, the digests the measurement records.

What it leaves to the caller, because no ruling settles it, each a required argument with no default:

- **The curve form** (`CURVE_FORMS`): a least-squares line, or an isotonic (non-decreasing) fit.
- **The one standard error** the curve is inverted at, a number. Which reading it is the standard error of (macro or
  micro, over which baseline, whether Holm's level widens it) is not ruled.
- **Which label-free statistics** the draw is checked against, and so how the shared seed node channel and the
  reached-node channel meet in the check. Here each statistic carries a ceiling of its own and a draw passes when it is
  below every ceiling it is given; a single statistic combining the channels is not built, since none is defined.
- **The pseudo-draws** (their number and seeds) and **the seed order** of the real draw.

What follows from the ruling and is therefore not a choice here:

- A draw passes when its statistic is strictly below the ceiling, since the advantage must stay *below* one standard
  error and the ceiling is where the fitted advantage reaches it.
- Seeds are examined in the order given and the examination stops at the first pass, so no later seed is looked at;
  that is what keeps the ceiling from becoming the leakage-minimising search 9.35 warns against.
- A fit that gives no finite ceiling (a line that does not rise with the statistic, an isotonic fit that never reaches
  the threshold over the observed range or already exceeds it at the smallest statistic) is reported as such and not
  turned into a ceiling, because what it means for the draw is the owner's.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

CURVE_FORMS = ("least_squares_line", "isotonic_increasing")


def _finite_pairs(label_free_statistics, advantages) -> tuple[np.ndarray, np.ndarray]:
    statistics = np.asarray(label_free_statistics, dtype=float)
    advantage_values = np.asarray(advantages, dtype=float)
    if statistics.shape != advantage_values.shape or statistics.ndim != 1:
        raise ValueError("label_free_statistics and advantages must be one value per pseudo-draw, the same number of each")
    finite = np.isfinite(statistics) & np.isfinite(advantage_values)
    return statistics[finite], advantage_values[finite]


def fit_advantage_curve(label_free_statistics, advantages, curve_form: str) -> dict:
    """The adversary's advantage per pseudo-draw fitted against the label-free statistic of the same draw.

    Pseudo-draws where either value is not finite are left out and counted. At least two distinct statistic values are
    needed, since neither form can be fitted to one."""
    if curve_form not in CURVE_FORMS:
        raise ValueError(f"curve_form must be one of {CURVE_FORMS}, not {curve_form!r}")
    statistics, advantage_values = _finite_pairs(label_free_statistics, advantages)
    if len(np.unique(statistics)) < 2:
        raise ValueError("the curve needs pseudo-draws at two or more distinct values of the label-free statistic")
    curve = {"curve_form": curve_form, "pseudo_draws_fitted": int(statistics.size),
             "pseudo_draws_left_out_as_not_finite": int(np.asarray(label_free_statistics).size - statistics.size),
             "observed_statistic_range": [float(statistics.min()), float(statistics.max())]}
    if curve_form == "least_squares_line":
        slope, intercept = np.polyfit(statistics, advantage_values, 1)
        curve.update(slope=float(slope), intercept=float(intercept))
        return curve
    from sklearn.isotonic import IsotonicRegression
    fitted = IsotonicRegression(increasing=True).fit(statistics, advantage_values)
    curve.update(knot_statistics=[float(value) for value in fitted.X_thresholds_],
                 knot_advantages=[float(value) for value in fitted.y_thresholds_])
    return curve


def statistic_ceiling(curve: dict, one_standard_error: float) -> dict:
    """The value of the label-free statistic at which the fitted advantage reaches one_standard_error.

    Returns {"ceiling": float or None, "status": ..., "within_observed_range": bool or None}. A line is inverted where
    it crosses the threshold, inside or outside the observed range (the flag says which). An isotonic fit is inverted
    by linear interpolation between its knots and only inside the observed range, since it says nothing beyond it."""
    threshold = float(one_standard_error)
    if not np.isfinite(threshold) or threshold <= 0:
        raise ValueError(f"one_standard_error must be a positive number, not {one_standard_error!r}")
    lowest, highest = curve["observed_statistic_range"]
    if curve["curve_form"] == "least_squares_line":
        if curve["slope"] <= 0:
            return {"ceiling": None, "within_observed_range": None,
                    "status": "the fitted advantage does not rise with the statistic, so the line gives no ceiling"}
        ceiling = (threshold - curve["intercept"]) / curve["slope"]
        return {"ceiling": float(ceiling), "within_observed_range": bool(lowest <= ceiling <= highest), "status": "ceiling"}
    if curve["curve_form"] == "isotonic_increasing":
        knot_statistics = np.asarray(curve["knot_statistics"], dtype=float)
        knot_advantages = np.asarray(curve["knot_advantages"], dtype=float)
        if knot_advantages[0] >= threshold:
            return {"ceiling": None, "within_observed_range": None,
                    "status": "the fitted advantage already reaches one standard error at the smallest statistic observed"}
        if knot_advantages[-1] < threshold:
            return {"ceiling": None, "within_observed_range": None,
                    "status": "the fitted advantage stays below one standard error over the whole observed range, "
                              "which gives no ceiling without extrapolating"}
        first_at_or_above = int(np.argmax(knot_advantages >= threshold))
        left_statistic, right_statistic = knot_statistics[first_at_or_above - 1], knot_statistics[first_at_or_above]
        left_advantage, right_advantage = knot_advantages[first_at_or_above - 1], knot_advantages[first_at_or_above]
        ceiling = left_statistic + (threshold - left_advantage) * (right_statistic - left_statistic) / (right_advantage - left_advantage)
        return {"ceiling": float(ceiling), "within_observed_range": True, "status": "ceiling"}
    raise ValueError(f"unknown curve_form {curve['curve_form']!r}")


def draw_passes(statistics_of_draw: dict[str, float], ceilings: dict[str, float]) -> tuple[bool, list[str]]:
    """(passes, why not): a draw passes when every statistic named in ceilings is finite and strictly below its
    ceiling. An empty ceilings is refused, since a check against nothing would pass every draw."""
    if not ceilings:
        raise ValueError("a draw is checked against at least one ceiling")
    reasons = []
    for statistic_name, ceiling in sorted(ceilings.items()):
        value = statistics_of_draw.get(statistic_name)
        if value is None or not np.isfinite(value):
            reasons.append(f"{statistic_name} is not a finite number ({value!r})")
        elif not value < ceiling:
            reasons.append(f"{statistic_name} {value:.6g} is not below its ceiling {ceiling:.6g}")
    return not reasons, reasons


def validated_seed_order(seed_order) -> list[int]:
    """The real draw's seed order as a list of whole numbers, refusing an empty order and a repeated seed (a repeat
    would examine one draw twice and make the order mean something other than what was fixed)."""
    seeds = list(seed_order)
    if not seeds:
        raise ValueError("the seed order is empty")
    if any(isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) for seed in seeds):
        raise ValueError("every seed in the order must be a whole number")
    seeds = [int(seed) for seed in seeds]
    if len(set(seeds)) != len(seeds):
        raise ValueError("the seed order repeats a seed")
    return seeds


def first_passing_seed(seed_order, statistics_of_seed, ceilings: dict[str, float]) -> dict:
    """Examine the seeds in the order given and stop at the first whose draw passes (decision 9.35: "The first draw
    that passes is accepted, with the seed order fixed in advance").

    statistics_of_seed(seed) returns the label-free statistics of that seed's draw. Returns {"accepted_seed": seed or
    None, "examined": [{"seed", "statistics", "passed", "reasons"} in order]}; no seed after the accepted one is
    examined."""
    examined = []
    for seed in validated_seed_order(seed_order):
        statistics = {name: float(value) for name, value in statistics_of_seed(seed).items()}
        passed, reasons = draw_passes(statistics, ceilings)
        examined.append({"seed": seed, "statistics": statistics, "passed": passed, "reasons": reasons})
        if passed:
            return {"accepted_seed": seed, "examined": examined}
    return {"accepted_seed": None, "examined": examined}


def reactome_release_of_graph(graph_directory: Path) -> dict:
    """The Reactome release the graph was built from, read from its summary (decision 9.111: when the lockbox is
    drawn the release in use is pinned, "read from the registered graph's summary").

    experiments/build_neuronal_graph_variant.py writes it as reactome_pathways.reactome_release in
    neuronal_variant_summary.json; any JSON summary directly in the directory carrying that key is read. Refuses a
    directory where none does, and one where two summaries name different releases, rather than guess."""
    directory = Path(graph_directory)
    release_of_summary: dict[str, str] = {}
    for path in sorted(directory.glob("*.json")):
        try:
            summary = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        pathways = summary.get("reactome_pathways") if isinstance(summary, dict) else None
        if isinstance(pathways, dict) and pathways.get("reactome_release") is not None:
            release_of_summary[path.name] = str(pathways["reactome_release"])
    if not release_of_summary:
        raise ValueError(f"no summary in {directory} records reactome_pathways.reactome_release; decision 9.111 needs the "
                         "release the graph was built from, read from the graph's summary")
    releases = set(release_of_summary.values())
    if len(releases) != 1:
        raise ValueError(f"the summaries in {directory} name different Reactome releases: {release_of_summary}")
    return {"reactome_release": releases.pop(), "read_from": sorted(release_of_summary)}
