"""The leakage ceiling of decision 9.35 and the draw it gates: fit, invert, and accept the first passing seed.

**Status: an unreviewed draft** (written 27 November 2026 and pushed the same day at the owner's request, "Just merge
and push everything. I'll review it later"; until then it was held on a local branch for the owner to read first). It
encodes readings of 9.35 the owner has not confirmed, its open definitions are listed in the message of the commit that
added it, and one known defect is not fixed: ceilings_of_calibrations (experiments/draw_held_out_set.py) applies a
least-squares ceiling extrapolated beyond every pseudo-draw (statistic_ceiling's within_observed_range is False) as it
applies one inside them. A second defect this paragraph named on 27 November 2026 was fixed on 28 November 2026, and
the fix is as unreviewed as the rest: reactome_release_of_graph read the release only from a summary in the graph's own
directory, which graph_full_neuronal (neuronal_variant_summary.json) alone holds, so on the registered chain it raised
and the draw could not run; it now follows the source graph each derived graph's own summary records, checking every
link, back to the summary that holds the release. Nothing here has been run on real data and no held-out set has been
drawn with it.

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


# The summaries the graph builders of the registered chain write (scripts/rebuild_data_layer.sh: graph_full_neuronal,
# its gene and protein split, the plasma binders on either, and the drug entry variants on the split's binders), by
# file name. Only the neuronal variant's records the Reactome release. Each other one records the graph it was built
# from under source_key, as the path its builder was given, which is relative to the repository root the scripts are
# run from. A summary is a directory's own when what it records of its builder's output matches the directory's graph
# files: that tells it from the copies of the source's summaries that experiments/build_drug_entry_node_variant.py
# makes (it copies every file of the source it does not rewrite), whose record of their output describes the source.
# The link to the source is checked by what the summary records of the builder's input: digests for the drug entry
# variant, row counts for the split and the binders, whose builders record no digest of their input.
# tests/test_leakage_ceiling.py checks that each builder named here still writes the summary file and the keys read.
REACTOME_RELEASE_SUMMARY = "neuronal_variant_summary.json"
GRAPH_BUILD_SUMMARIES = {
    REACTOME_RELEASE_SUMMARY: {"builder": "experiments/build_neuronal_graph_variant.py", "source_key": None},
    "split_summary.json": {"builder": "experiments/build_gene_protein_split.py", "source_key": "graph_dir"},
    "plasma_binder_summary.json": {"builder": "experiments/build_plasma_binder_variant.py", "source_key": "source_graph"},
    "drug_entry_summary.json": {"builder": "experiments/build_drug_entry_node_variant.py", "source_key": "source_graph"},
}


def _row_count(path: Path) -> int:
    import pyarrow.parquet as parquet_module

    return int(parquet_module.read_metadata(path).num_rows)


def _value_counts(path: Path, column: str) -> dict[str, int]:
    import pandas as pd

    return {str(value): int(count) for value, count in pd.read_parquet(path, columns=[column])[column].value_counts().items() if count}


def _mismatches(summary: dict, from_the_files: dict) -> list[str]:
    """One sentence per key whose recorded value differs from what the files give, or that the summary does not record.
    A recorded count per type or relation is compared without its zero entries, which a categorical column's
    value_counts gives and the files do not."""
    problems = []
    for key, value in from_the_files.items():
        recorded = summary.get(key)
        if isinstance(value, dict) and isinstance(recorded, dict):
            recorded = {str(name): count for name, count in recorded.items() if count}
        if key not in summary:
            problems.append(f"it records no {key}")
        elif recorded != value:
            problems.append(f"its {key} is {summary[key]!r} where the files give {value!r}")
    return problems


def _own_output_mismatches(summary_name: str, summary: dict, directory: Path) -> list[str]:
    """Empty when what the summary records of its builder's output matches the graph files of directory."""
    from mechanistic_pathway_learning.data_release import sha256_of_file

    nodes, edges = directory / "nodes.parquet", directory / "edges.parquet"
    if summary_name == REACTOME_RELEASE_SUMMARY:
        from_the_files = {"nodes_by_type": _value_counts(nodes, "node_type"), "edges_by_relation": _value_counts(edges, "relation_type")}
    elif summary_name == "split_summary.json":
        from_the_files = {"nodes_after": _row_count(nodes), "edges_after": _row_count(edges),
                          "edges_per_relation": _value_counts(edges, "relation_type")}
    elif summary_name == "plasma_binder_summary.json":
        from_the_files = {"nodes": _row_count(nodes), "edges_after": _row_count(edges)}
    else:
        from_the_files = {"nodes_sha256": sha256_of_file(nodes), "edges_sha256": sha256_of_file(edges)}
    return _mismatches(summary, from_the_files)


def _source_link_mismatches(summary_name: str, summary: dict, source: Path) -> tuple[str, list[str]]:
    """How the link from a derived graph to its recorded source is checked, and what fails the check (empty when the
    source holds the graph the summary says its builder read)."""
    from mechanistic_pathway_learning.data_release import sha256_of_file

    nodes, edges = source / "nodes.parquet", source / "edges.parquet"
    if summary_name == "drug_entry_summary.json":
        return ("the SHA-256 of the source's nodes.parquet and edges.parquet",
                _mismatches(summary, {"source_nodes_sha256": sha256_of_file(nodes), "source_edges_sha256": sha256_of_file(edges)}))
    if summary_name == "split_summary.json":
        return ("the source's row counts of nodes, edges and gene nodes (the split's builder records no digest of its input)",
                _mismatches(summary, {"nodes_before": _row_count(nodes), "edges_before": _row_count(edges),
                                      "gene_nodes": _value_counts(nodes, "node_type").get("gene", 0)}))
    return ("the source's row counts of nodes and edges (the binders' builder records no digest of its input and adds no node)",
            _mismatches(summary, {"nodes": _row_count(nodes), "edges_before": _row_count(edges)}))


def _own_summary(directory: Path) -> tuple[str, dict]:
    """The one summary of GRAPH_BUILD_SUMMARIES that is directory's own, refusing a directory with none or several."""
    for required in ("nodes.parquet", "edges.parquet"):
        if not (directory / required).is_file():
            raise ValueError(f"{directory} holds no {required}, so it is not a graph directory")
    own, not_own = [], []
    for name in GRAPH_BUILD_SUMMARIES:
        path = directory / name
        if not path.is_file():
            continue
        try:
            summary = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            not_own.append(f"{name} is not JSON ({error})")
            continue
        if not isinstance(summary, dict):
            not_own.append(f"{name} is not a JSON object")
            continue
        problems = _own_output_mismatches(name, summary, directory)
        if problems:
            not_own.append(f"{name} does not describe this directory's graph files ({'; '.join(problems)})")
        else:
            own.append((name, summary))
    if not own:
        raise ValueError(f"the lineage of {directory} is not recorded: no summary there that a builder of the registered chain "
                         f"writes ({', '.join(GRAPH_BUILD_SUMMARIES)}) describes its graph files"
                         + (f"; {'; '.join(not_own)}" if not_own else ""))
    if len(own) > 1:
        raise ValueError(f"the lineage of {directory} is ambiguous: {' and '.join(name for name, _ in own)} each describe its "
                         "graph files, so which build wrote them is not recorded")
    return own[0]


def reactome_release_of_graph(graph_directory: Path, relative_to: Path | None = None) -> dict:
    """The Reactome release the graph was built from (decision 9.111: when the lockbox is drawn the release in use is
    pinned, "read from the registered graph's summary").

    experiments/build_neuronal_graph_variant.py records it as reactome_pathways.reactome_release in
    neuronal_variant_summary.json, and no graph built from that one carries the file. So the release is read by
    following the graph's lineage (GRAPH_BUILD_SUMMARIES): the directory's own summary names the graph it was built
    from, the link is checked by what that summary records of its input, and so on back to the neuronal variant's
    summary. A recorded path that is relative is resolved against relative_to, by default the working directory: the
    builders record the path they were given, from the repository root they are run from, and the draw is run from it
    too.

    Refuses, rather than guess: a directory with no own summary or with several; a recorded source that is missing;
    one that no longer matches what the summary recorded of it (rebuilt since); a lineage that returns to a graph
    already visited; and a neuronal summary that records no release.

    Returns {"reactome_release": the release as a string, "read_from": the path of the summary that records it,
    "lineage": one entry per link followed, from the graph given back to the neuronal variant, each naming the graph,
    its own summary, that summary's builder, the source as recorded and as resolved, and what the link was checked
    by}; the lineage is empty when the graph given is the neuronal variant itself."""
    base = Path.cwd() if relative_to is None else Path(relative_to)
    directory = Path(graph_directory)
    lineage: list[dict] = []
    visited: set[Path] = set()
    while True:
        visited.add(directory.resolve())
        name, summary = _own_summary(directory)
        source_key = GRAPH_BUILD_SUMMARIES[name]["source_key"]
        if source_key is None:
            pathways = summary.get("reactome_pathways")
            release = pathways.get("reactome_release") if isinstance(pathways, dict) else None
            if release is None:
                raise ValueError(f"{directory / name} records no reactome_pathways.reactome_release; decision 9.111 needs the "
                                 "release the graph was built from, read from the graph's summary")
            return {"reactome_release": str(release), "read_from": str(directory / name), "lineage": lineage}
        recorded = summary.get(source_key)
        if not isinstance(recorded, str) or not recorded:
            raise ValueError(f"the lineage of {directory} is not recorded: {name} names no graph it was built from ({source_key})")
        source = Path(recorded) if Path(recorded).is_absolute() else base / recorded
        if source.resolve() in visited:
            raise ValueError(f"the lineage of {graph_directory} returns to {source}, a graph already visited")
        for required in ("nodes.parquet", "edges.parquet"):
            if not (source / required).is_file():
                raise ValueError(f"{directory / name} records its source graph as {recorded!r}, and {source} holds no {required}; "
                                 "the lineage cannot be followed")
        checked_by, problems = _source_link_mismatches(name, summary, source)
        if problems:
            raise ValueError(f"{source} is not the graph {directory} was built from, by {checked_by} as {name} records them "
                             f"(was it rebuilt since?): {'; '.join(problems)}")
        lineage.append({"graph_dir": str(directory), "summary": name, "builder": GRAPH_BUILD_SUMMARIES[name]["builder"],
                        "source_recorded_as": recorded, "source_graph_dir": str(source), "link_checked_by": checked_by})
        directory = source
