"""Fit decision 9.35's curve on development pseudo-draws and invert it at one standard error (built 27 November 2026,
not run).

**Status: an unreviewed draft** (written 27 November 2026 and pushed the same day at the owner's request, "Just merge
and push everything. I'll review it later"; until then it was held on a local branch for the owner to read first). It
encodes readings of 9.35 the owner has not confirmed, its open definitions are listed in the message of the commit that
added it, and one known defect is not fixed: ceilings_of_calibrations (experiments/draw_held_out_set.py) applies a
least-squares ceiling extrapolated beyond every pseudo-draw (statistic_ceiling's within_observed_range is False) as it
applies one inside them. A second defect this paragraph named on 27 November 2026 was fixed on 28 November 2026, and
the fix is as unreviewed as the rest: reactome_release_of_graph (evaluation/leakage_ceiling.py) read the release only
from a summary in the graph's own directory, which graph_full_neuronal (neuronal_variant_summary.json) alone holds, so
on the registered chain it raised and the draw could not run; it now follows the source graph each derived graph's own
summary records, checking every link, back to the summary that holds the release. Nothing here has been run on real
data and no held-out set has been drawn with it.

What it does. It reads the pseudo-draw records experiments/measure_leakage_only_adversary.py wrote (each draw's
label-free statistics and the adversary's advantage over each baseline), fits the advantage against one label-free
statistic, and inverts the fit at one standard error of the test's own reading, giving the value of that statistic a
real draw must stay below (evaluation/leakage_ceiling.py). experiments/draw_held_out_set.py reads the file this writes.

What is ruled and built in: the curve is fitted on development-set pseudo-draws, so no lockbox label is read; the
threshold is one standard error of the test's own reading; both are on the graph the draw is made on (decision 9.35,
24 November 2026: "Use 1.a but not on current graph. On graph at time of draw, right?"). So this refuses a measurement
whose graph files, evidence table or label selection differ from the ones named here, which are the draw's. Decision
9.36 puts the k = 2 reached-node channel into the adversary, with k as a sensitivity sweep; which channels the
measurement scored is copied into the output from the measurement, which recorded them.

What it leaves to the caller, because no ruling settles it, each a required argument with no default:

- **--statistic**, the label-free statistic the advantage is fitted against: seen_target_share (the drug side of the
  shared seed node channel, the statistic 9.35 proposed) or seen_reached_node_share (the reached-node channel's, a
  candidate built as seen_target_share is). Only statistics that read no label are offered, since the draw has to
  compute the same one on the real draw without opening it. Fitting each and checking the draw against both is done
  by running this once per statistic and passing both files to the draw.
- **--advantage**, which reading the advantage is: macro or micro, over which baseline (popularity, degree_popularity,
  type_popularity), on every held-out row or within the drug or gene stratum, written as the measurement's key
  ([drug_stratum_|gene_stratum_](macro|micro)_advantage_over_<baseline>).
- **--one-standard-error**, the number the curve is inverted at, and **--standard-error-source**, a sentence saying
  where that number was read (which reading, on which graph and date, at which level), recorded beside it.
- **--curve-form** (leakage_ceiling.CURVE_FORMS).
- **--pooling-rule**, whose draws are fitted: the measurement holds one set per pooling rule, and the
  adversary is meant to be the strongest lookup, which is a reading across them and not a choice made here.
- **--num-pseudo-draws**, checked against the measurement, so the count is stated by the caller and not inherited
  from the measurement script's default.

The draw's options (--hold-out-genes-encoding-held-out-targets, --hold-out-whole-groups-of-those-genes, --gene-side-rule;
target_held_out_split.HeldOutDrawOptions, built 28 November 2026 and not ruled) are off by default. They state the rule
the measurement's pseudo-draws were drawn by, a measurement drawn by another is refused (one without a record of them
was drawn by the rule as it stands), and the calibration records them when one is on, so that
experiments/draw_held_out_set.py, which takes the same flags, refuses a ceiling fitted on another rule.

It writes one JSON file and refuses to overwrite one.

Usage, from the repository root:
  PYTHONPATH=. python experiments/calibrate_leakage_ceiling.py --measurement <measurement.json> \\
      --graph-dir <the draw's graph> --evidence-dir <evidence> --label-selection <selection.parquet> \\
      --pooling-rule base_rate_shrunk_mean --statistic seen_target_share \\
      --advantage drug_stratum_macro_advantage_over_type_popularity --one-standard-error <number> \\
      --standard-error-source "<where the number was read>" --curve-form least_squares_line \\
      --num-pseudo-draws <n> --output <calibration.json>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mechanistic_pathway_learning.data_release import sha256_of_file  # noqa: E402
from mechanistic_pathway_learning.evaluation.leakage_ceiling import CURVE_FORMS, fit_advantage_curve, statistic_ceiling  # noqa: E402
from mechanistic_pathway_learning.evaluation.leakage_only_adversary import POOLING_RULES  # noqa: E402
from mechanistic_pathway_learning.evaluation.target_held_out_split import HeldOutDrawOptions  # noqa: E402
from measure_leakage_only_adversary import (  # noqa: E402
    DRAW_OPTIONS_KEY, add_held_out_draw_option_arguments, graph_file_sha256, held_out_draw_options_from_arguments)

LABEL_FREE_STATISTICS = ("seen_target_share", "seen_reached_node_share")
ADVANTAGE_KEY = re.compile(r"^(drug_stratum_|gene_stratum_)?(macro|micro)_advantage_over_(popularity|degree_popularity|type_popularity)$")


def calibrate(measurement: dict, pooling_rule: str, statistic: str, advantage: str, one_standard_error: float,
              curve_form: str, num_pseudo_draws: int, draw_options: HeldOutDrawOptions | None = None) -> dict:
    """The fit and its inversion from a measurement's records, with the points used and the draws left out.
    draw_options are the draw's options the caller states (None: the rule as it stands); a measurement whose
    pseudo-draws were drawn by other options is refused."""
    draw_options = draw_options or HeldOutDrawOptions()
    measured_options = HeldOutDrawOptions.from_record(measurement.get(DRAW_OPTIONS_KEY))
    if measured_options != draw_options:
        raise ValueError(f"the measurement's pseudo-draws were drawn with the draw options {measured_options.as_record()}, "
                         f"not the {draw_options.as_record()} stated; the calibration and the draw use one rule")
    if statistic not in LABEL_FREE_STATISTICS:
        raise ValueError(f"statistic must be one of {LABEL_FREE_STATISTICS}, the label-free ones, not {statistic!r}")
    if not ADVANTAGE_KEY.match(advantage):
        raise ValueError(f"advantage must be a key of the form {ADVANTAGE_KEY.pattern}, not {advantage!r}")
    if measurement.get("num_draws") != num_pseudo_draws:
        raise ValueError(f"the measurement holds {measurement.get('num_draws')} pseudo-draws, not the {num_pseudo_draws} stated")
    if pooling_rule not in measurement.get("pooling_rules", {}):
        raise ValueError(f"the measurement has no draws for pooling rule {pooling_rule!r}")
    channel_names = [channel["channel"] for channel in measurement["channels"]["scored"]]
    if statistic == "seen_reached_node_share" and "reached_node" not in channel_names:
        raise ValueError("seen_reached_node_share needs a measurement made with the reached-node channel on")
    points, left_out = [], []
    for draw in measurement["pooling_rules"][pooling_rule]["draws"]:
        seed = draw.get("draw_seed")
        if not draw.get("usable"):
            left_out.append({"draw_seed": seed, "reason": "the draw held out no row or trained on none"})
        elif statistic not in draw or advantage not in draw:
            left_out.append({"draw_seed": seed, "reason": f"the draw records no {statistic if statistic not in draw else advantage}"})
        elif not (np.isfinite(draw[statistic]) and np.isfinite(draw[advantage])):
            left_out.append({"draw_seed": seed, "reason": "a value is not finite"})
        else:
            points.append({"draw_seed": seed, "statistic": float(draw[statistic]), "advantage": float(draw[advantage])})
    curve = fit_advantage_curve([point["statistic"] for point in points], [point["advantage"] for point in points], curve_form)
    record = {"pooling_rule": pooling_rule, "statistic": statistic, "advantage": advantage,
              "one_standard_error": float(one_standard_error), "curve": curve,
              "ceiling": statistic_ceiling(curve, one_standard_error), "points": points, "pseudo_draws_left_out": left_out,
              "pseudo_draw_seeds": measurement.get("pseudo_draw_seeds", list(range(num_pseudo_draws))),
              "channels": measurement["channels"], "group_by": measurement.get("group_by"),
              "lockbox_excluded": measurement.get("lockbox_excluded")}
    if not draw_options.is_default():  # recorded only when an option is on, as the measurement records them
        record[DRAW_OPTIONS_KEY] = draw_options.as_record()
    return record


def refuse_another_graph(measurement: dict, graph_directory: Path, evidence_directory: Path, label_selection: Path) -> None:
    """Decision 9.35: the curve is fitted on the graph the draw is made on. A measurement made before it recorded its
    inputs' digests (before 27 November 2026) cannot show which graph it was on, so it is refused too."""
    expected = {"graph_file_sha256": graph_file_sha256(graph_directory),
                "evidence_records_sha256": sha256_of_file(Path(evidence_directory) / "evidence_records.parquet"),
                "label_selection_sha256": sha256_of_file(label_selection)}
    for key, value in expected.items():
        if measurement.get(key) is None:
            raise ValueError(f"the measurement records no {key}, so it cannot show it was made on {graph_directory}")
        if measurement[key] != value:
            raise ValueError(f"the measurement's {key} differs from that of the inputs named here; decision 9.35 fits the "
                             "curve on the graph the draw is made on")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--measurement", type=Path, required=True, help="the JSON experiments/measure_leakage_only_adversary.py wrote")
    parser.add_argument("--graph-dir", type=Path, required=True, help="the graph the draw is made on")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--label-selection", type=Path, required=True)
    parser.add_argument("--pooling-rule", choices=list(POOLING_RULES), required=True)
    parser.add_argument("--statistic", choices=list(LABEL_FREE_STATISTICS), required=True)
    parser.add_argument("--advantage", required=True, help=f"a measurement key matching {ADVANTAGE_KEY.pattern}")
    parser.add_argument("--one-standard-error", type=float, required=True)
    parser.add_argument("--standard-error-source", required=True,
                        help="where the standard error was read: which reading, on which graph and date, at which level")
    parser.add_argument("--curve-form", choices=list(CURVE_FORMS), required=True)
    parser.add_argument("--num-pseudo-draws", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    add_held_out_draw_option_arguments(parser)
    arguments = parser.parse_args()
    draw_options = held_out_draw_options_from_arguments(parser, arguments)
    if arguments.output.exists():
        raise SystemExit(f"{arguments.output} exists; a calibration is written once, so name another path")
    if not arguments.standard_error_source.strip():
        raise SystemExit("--standard-error-source is empty")
    measurement = json.loads(arguments.measurement.read_text())
    refuse_another_graph(measurement, arguments.graph_dir, arguments.evidence_dir, arguments.label_selection)
    record = {"made_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "measurement": str(arguments.measurement), "measurement_sha256": sha256_of_file(arguments.measurement),
              "graph_dir": str(arguments.graph_dir), "graph_file_sha256": measurement["graph_file_sha256"],
              "evidence_dir": str(arguments.evidence_dir), "evidence_records_sha256": measurement["evidence_records_sha256"],
              "label_selection": str(arguments.label_selection), "label_selection_sha256": measurement["label_selection_sha256"],
              "standard_error_source": arguments.standard_error_source}
    record.update(calibrate(measurement, arguments.pooling_rule, arguments.statistic, arguments.advantage,
                            arguments.one_standard_error, arguments.curve_form, arguments.num_pseudo_draws, draw_options))
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with open(arguments.output, "x") as handle:
        handle.write(json.dumps(record, indent=1) + "\n")
    print(json.dumps({key: record[key] for key in ("statistic", "advantage", "one_standard_error", "curve", "ceiling")}, indent=1))


if __name__ == "__main__":
    main()
