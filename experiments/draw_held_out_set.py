"""Draw the held-out set by item 25's target partition under decision 9.35's leakage ceiling (built 27 November 2026;
nothing has been drawn with it).

**Status: an unreviewed draft** (written 27 November 2026 and pushed the same day at the owner's request, "Just merge
and push everything. I'll review it later"; until then it was held on a local branch for the owner to read first). It
encodes readings of 9.35 the owner has not confirmed, its open definitions are listed in the message of the commit that
added it, and one known defect is not fixed: ceilings_of_calibrations applies a least-squares ceiling extrapolated
beyond every pseudo-draw (statistic_ceiling's within_observed_range is False) as it applies one inside them. A second
defect this paragraph named on 27 November 2026 was fixed on 28 November 2026, and the fix is as unreviewed as the
rest: reactome_release_of_graph read the release only from a summary in the graph's own directory, which
graph_full_neuronal (neuronal_variant_summary.json) alone holds, so on the registered chain it raised and the draw
could not run; it now follows the source graph each derived graph's own summary records, checking every link, back to
the summary that holds the release. Nothing here has been run on real data and no held-out set has been drawn with it.

The draw is made only on the owner's go-ahead (decision 1.1: "Don't finalize the lockbox until I've given the go
ahead"), after the Human-GEM update of decision 9.151 and on the graph built from it, and after the amendment item that
registers 9.35's rule. experiments/draw_lockbox.py stays as the record of the earlier group draws (configs/lockbox_v1.json
and configs/lockbox_v2.json); this script does not replace what those files are.

The rule, as ruled (decision 9.35, 24 November 2026: "Use 1.a but not on current graph. On graph at time of draw,
right?"; decision 9.36, the same day: "2 accepted. Draw depends on graph. Oh well on the genes"):

- Each seed of --seed-order, a file fixed in advance, draws the held-out set by item 25 with each side at its
  registered fraction (target_held_out_split.two_sided_held_out_perturbations).
- Each draw's label-free statistics are computed, reading no label, and compared with the ceilings of the --calibration
  files (experiments/calibrate_leakage_ceiling.py). A draw passes when every statistic is below its ceiling.
- The first draw that passes is accepted and no later seed is examined. If none passes, nothing is written and the
  examined seeds are printed for the owner.
- The channel list is recorded with the draw; a channel found later is a disclosed limitation, not grounds for a redraw.
- Every ceiling must have been fitted on this graph, evidence table and label selection (9.35: "on the graph the draw
  is made on and not on any graph before it"), with the same leakage grouping for the gene side and with the same
  channels in every calibration given.
- A seed that was also a calibration pseudo-draw is refused: that pseudo-draw scored the adversary on the very rows
  the real draw would hold out, which 9.35's "so no lockbox label is read" rules out.
- The output is never overwritten; there is no option to.

What it records (one JSON file): the perturbation ids and the fields experiments/score_confirmatory.py and
experiment_data.read_lockbox read (label_selection_sha256, evidence_records_sha256, group_by,
symptoms_in_the_macro_average), the rule, the seed order and its SHA-256, every seed examined with its statistics, the
accepted seed, the held-out targets, the channel list, each calibration with its SHA-256 and ceiling, the SHA-256 of
the graph files read, and the Reactome release with the lineage it was read through (reactome_release_of_graph,
which follows the source each derived graph's summary records back to the neuronal variant's summary; decision 9.111:
the release in use is pinned when the lockbox is drawn). It also counts the leakage groups of --group-by that hold
perturbations on both sides: item 25 holds a drug out by its targets, so such a group can exist, and read_lockbox
refuses a lockbox that has one.
How the runs that read the lockbox treat that is not settled here.

What it leaves to the caller, each a required argument with no default: the inputs (--graph-dir, --evidence-dir,
--label-selection), --group-by, --seed-order, --calibration (which ceilings the draw is checked against) and --output.
No ruling settles the inputs, the seed order or the calibrations, which is why they have no default. --group-by is the
grouping of the gene side, and must be the one the calibration's pseudo-draws used. The registration of 9 October 2026
keeps disease_cluster_and_targets for the confirmatory reading (docs/preregistration.md: "`group_by` therefore stays
`disease_cluster_and_targets` for the confirmatory reading", with the family grouping a development sensitivity
reading). docs/drafts/held_out_draw_methods_2026-11-28.md (M1, not ruled) proposes disease_cluster for this draw,
because under item 25 disease_cluster_and_targets also joins drugs that share a target, so a group can land on both
sides, which read_lockbox refuses. So this script, itself an unreviewed draft, takes the grouping from the caller rather than
defaulting to either. Until 28 November 2026 this paragraph said no ruling settles the grouping.

The draw's options (--hold-out-genes-encoding-held-out-targets, --hold-out-whole-groups-of-those-genes, --gene-side-rule;
target_held_out_split.HeldOutDrawOptions, built 28 November 2026 from that draft's M1 and M2, none ruled) are off by
default, so a draw without them is the draw described above. Every calibration given must record the same options
(experiments/calibrate_leakage_ceiling.py takes the same flags), so the pseudo-draws and the draw use one rule.

Usage, from the repository root (only on the owner's go-ahead):
  PYTHONPATH=. python experiments/draw_held_out_set.py --graph-dir <graph> --evidence-dir <evidence> \\
      --label-selection <selection.parquet> --group-by <grouping> --seed-order <seeds.json> \\
      --calibration <calibration.json> [<calibration.json> ...] --output <lockbox.json>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mechanistic_pathway_learning.data_release import sha256_of_file  # noqa: E402
from mechanistic_pathway_learning.evaluation.experiment_data import (  # noqa: E402
    GROUPING_COLUMNS, load_experiment_data, read_proteins_encoded_by_gene)
from mechanistic_pathway_learning.evaluation.leakage_ceiling import (  # noqa: E402
    first_passing_seed, reactome_release_of_graph, validated_seed_order)
from mechanistic_pathway_learning.evaluation.leakage_only_adversary import (  # noqa: E402
    reach_edges, reached_nodes_of_perturbations, seen_reached_node_share, seen_target_share)
from mechanistic_pathway_learning.evaluation.target_held_out_split import (  # noqa: E402
    REGISTERED_HELD_OUT_FRACTION, HeldOutDrawOptions, targets_of_drugs, two_sided_held_out_perturbations)
from measure_leakage_only_adversary import (  # noqa: E402
    DRAW_OPTIONS_KEY, add_held_out_draw_option_arguments, graph_file_sha256, held_out_draw_options_from_arguments)
from score_confirmatory import MINIMUM_POSITIVES_TO_SCORE  # noqa: E402


def ceilings_of_calibrations(calibrations: list[dict], group_by: str, input_digests: dict,
                             draw_options: HeldOutDrawOptions | None = None) -> tuple[dict[str, float], dict]:
    """statistic -> ceiling over the calibrations, and the channel list they share, after refusing any calibration
    made on other inputs, with another grouping or other draw options (None: the rule as it stands), without a finite
    ceiling, or with channels the others do not share."""
    if not calibrations:
        raise ValueError("the draw is checked against at least one calibration")
    draw_options = draw_options or HeldOutDrawOptions()
    ceilings: dict[str, float] = {}
    channels = calibrations[0]["channels"]
    for calibration in calibrations:
        for key, value in input_digests.items():
            if calibration.get(key) != value:
                raise ValueError(f"a calibration's {key} differs from the draw's inputs; decision 9.35 fits the curve on the graph the draw is made on")
        if calibration.get("group_by") != group_by:
            raise ValueError(f"a calibration's pseudo-draws grouped the gene side by {calibration.get('group_by')!r}, not {group_by!r}")
        calibrated_options = HeldOutDrawOptions.from_record(calibration.get(DRAW_OPTIONS_KEY))
        if calibrated_options != draw_options:
            raise ValueError(f"a calibration's pseudo-draws were drawn with the draw options {calibrated_options.as_record()}, "
                             f"not {draw_options.as_record()}; the pseudo-draws and the draw use one rule")
        if calibration["channels"] != channels:
            raise ValueError("the calibrations were measured with different channels; the draw computes its statistics with one set")
        ceiling = calibration["ceiling"]
        if ceiling.get("ceiling") is None:
            raise ValueError(f"the calibration of {calibration['statistic']} gives no ceiling ({ceiling.get('status')}); what that means for the draw is the owner's")
        if calibration["statistic"] in ceilings:
            raise ValueError(f"two calibrations give a ceiling for {calibration['statistic']}")
        ceilings[calibration["statistic"]] = float(ceiling["ceiling"])
    return ceilings, channels


def reached_node_channel(channels: dict) -> dict | None:
    """The reached-node channel's entry of a channel list, or None when it was off."""
    return next((channel for channel in channels["scored"] if channel["channel"] == "reached_node"), None)


def draw_held_out_set(data, seed_order, calibrations: list[dict], group_by: str, input_digests: dict,
                      draw_options: HeldOutDrawOptions | None = None, proteins_encoded_by_gene=None) -> dict:
    """The examination of the seed order and, when a seed passes, the held-out set it draws. Reads no label until a
    seed is accepted; then it counts the kept positives inside the held-out set, as experiments/draw_lockbox.py did,
    which fixes the symptoms of the macro average before anything is scored. draw_options (and
    proteins_encoded_by_gene for the identity option) are the draft options of the module docstring, off by default."""
    draw_options = draw_options or HeldOutDrawOptions()
    ceilings, channels = ceilings_of_calibrations(calibrations, group_by, input_digests, draw_options)
    seeds = validated_seed_order(seed_order)
    pseudo_draw_seeds = {int(seed) for calibration in calibrations for seed in calibration["pseudo_draw_seeds"]}
    repeated = sorted(set(seeds) & pseudo_draw_seeds)
    if repeated:
        raise ValueError(f"seeds {repeated[:5]} were calibration pseudo-draws, whose adversary scored the rows the real draw would hold out")
    perturbation_ids = [str(perturbation_id) for perturbation_id in data.perturbation_ids]
    perturbation_types_of_id = dict(zip(perturbation_ids, data.perturbation_types))
    targets_of_drug = targets_of_drugs(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids)
    reached_channel = reached_node_channel(channels)
    reached_nodes_of_perturbation, covered_type_pairs = None, None
    if "seen_reached_node_share" in ceilings:
        if reached_channel is None:
            raise ValueError("a ceiling on seen_reached_node_share needs calibrations measured with the reached-node channel on")
        covered_type_pairs = [(pair["held_out_type"], pair["training_type"]) for pair in reached_channel["covers"]]
        walk_source, walk_target = reach_edges(data.edge_source, data.edge_target, data.is_currency, reached_channel["reach_edge_set"])
        reached_nodes_of_perturbation = reached_nodes_of_perturbations(
            data.perturbation_ids, data.perturbation_seeds, data.node_ids, walk_source, walk_target, reached_channel["maximum_hops"])
    held_out_of_seed: dict[int, tuple[set[str], set[str]]] = {}

    def statistics_of_seed(seed: int) -> dict[str, float]:
        held_out_ids, held_out_targets = two_sided_held_out_perturbations(
            data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids, data.group_ids, seed,
            options=draw_options, proteins_encoded_by_gene=proteins_encoded_by_gene)
        held_out_of_seed[seed] = (held_out_ids, held_out_targets)
        training_ids = [perturbation_id for perturbation_id in perturbation_ids if perturbation_id not in held_out_ids]
        statistics = {}
        if "seen_target_share" in ceilings:
            statistics["seen_target_share"] = seen_target_share(targets_of_drug, held_out_ids)
        if "seen_reached_node_share" in ceilings:
            statistics["seen_reached_node_share"] = seen_reached_node_share(
                reached_nodes_of_perturbation, sorted(held_out_ids), training_ids, perturbation_types_of_id, covered_type_pairs)
        return statistics

    examination = first_passing_seed(seeds, statistics_of_seed, ceilings)
    record = {"rule": {"split": "item 25: drugs by the target partition, the rest by fold 0 of the grouped folds, each "
                                "side at the registered fraction (target_held_out_split.two_sided_held_out_perturbations)",
                       "held_out_fraction": REGISTERED_HELD_OUT_FRACTION, "group_by": group_by,
                       "acceptance": "the first seed of the order whose label-free statistics are all below their "
                                     "ceilings; no later seed is examined (decision 9.35)"},
              "group_by": group_by, "seed_order": seeds, "accepted_seed": examination["accepted_seed"],
              "examined_seeds": examination["examined"], "ceilings": ceilings, "channels": channels}
    if not draw_options.is_default():  # recorded only when an option is on, so a draw without them records what it did
        record["rule"]["split"] += ("; changed by the draft options of 28 November 2026 that held_out_draw_options "
                                    "names, which no ruling registers (target_held_out_split.HeldOutDrawOptions)")
        record["rule"][DRAW_OPTIONS_KEY] = record[DRAW_OPTIONS_KEY] = draw_options.as_record()
    if examination["accepted_seed"] is None:
        return record
    held_out_ids, held_out_targets = held_out_of_seed[examination["accepted_seed"]]
    in_held_out = np.array([perturbation_id in held_out_ids for perturbation_id in perturbation_ids])
    is_drug = np.array([kind == "drug" for kind in data.perturbation_types])
    label_mask = data.label_mask if data.label_mask is not None else np.ones(data.outcomes.shape, dtype=bool)
    kept = data.outcomes * label_mask
    positives_by_symptom = {symptom: int(kept[in_held_out, column].sum()) for column, symptom in enumerate(data.symptoms)}
    groups_inside = {group for group, inside in zip(data.group_ids, in_held_out) if inside}
    groups_outside = {group for group, inside in zip(data.group_ids, in_held_out) if not inside}
    record.update({
        "held_out_targets": sorted(held_out_targets),
        "num_perturbations": int(in_held_out.sum()), "num_development_perturbations": int((~in_held_out).sum()),
        "num_genes": int((in_held_out & ~is_drug).sum()), "num_drugs": int((in_held_out & is_drug).sum()),
        "num_drugs_with_a_kept_positive": int((kept[in_held_out & is_drug].sum(axis=1) > 0).sum()),
        "kept_positive_pairs": int(kept[in_held_out].sum()), "kept_positive_pairs_development": int(kept[~in_held_out].sum()),
        "kept_positives_by_symptom": positives_by_symptom,
        "symptoms_in_the_macro_average": sorted(symptom for symptom, count in positives_by_symptom.items() if count >= MINIMUM_POSITIVES_TO_SCORE),
        "leakage_groups_with_members_on_both_sides": len(groups_inside & groups_outside),
        "perturbation_ids": sorted(held_out_ids),
    })
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--label-selection", type=Path, required=True)
    parser.add_argument("--group-by", choices=sorted(GROUPING_COLUMNS), required=True,
                        help="the leakage grouping of the gene side; must be the one the calibration's pseudo-draws used")
    parser.add_argument("--seed-order", type=Path, required=True, help="a JSON list of whole-number seeds, fixed in advance")
    parser.add_argument("--calibration", type=Path, nargs="+", required=True,
                        help="files written by experiments/calibrate_leakage_ceiling.py; a draw passes when it is below every ceiling")
    parser.add_argument("--output", type=Path, required=True, help="the held-out set's record; refused if it exists")
    add_held_out_draw_option_arguments(parser)
    arguments = parser.parse_args()
    draw_options = held_out_draw_options_from_arguments(parser, arguments)
    if arguments.output.exists():
        raise SystemExit(f"{arguments.output} exists; a held-out set is drawn once and is not overwritten")
    seed_order = json.loads(arguments.seed_order.read_text())
    calibrations = [json.loads(path.read_text()) for path in arguments.calibration]
    input_digests = {"graph_file_sha256": graph_file_sha256(arguments.graph_dir),
                     "evidence_records_sha256": sha256_of_file(arguments.evidence_dir / "evidence_records.parquet"),
                     "label_selection_sha256": sha256_of_file(arguments.label_selection)}
    reactome_release = reactome_release_of_graph(arguments.graph_dir)
    data = load_experiment_data(arguments.graph_dir, arguments.evidence_dir, group_by=arguments.group_by,
                               label_selection=arguments.label_selection)
    proteins_encoded_by_gene = (read_proteins_encoded_by_gene(arguments.graph_dir)
                                if draw_options.hold_out_genes_encoding_held_out_targets else None)
    record = draw_held_out_set(data, seed_order, calibrations, arguments.group_by, input_digests, draw_options,
                               proteins_encoded_by_gene)
    if record["accepted_seed"] is None:
        print(json.dumps({key: record[key] for key in ("seed_order", "examined_seeds", "ceilings")}, indent=1))
        raise SystemExit("no seed of the order passes every ceiling; nothing was written, and what follows is the owner's")
    record = {"drawn_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **record,
              "seed_order_file": str(arguments.seed_order), "seed_order_sha256": sha256_of_file(arguments.seed_order),
              "calibrations": [{"path": str(path), "sha256": sha256_of_file(path), "statistic": calibration["statistic"],
                                "ceiling": calibration["ceiling"]["ceiling"]} for path, calibration in zip(arguments.calibration, calibrations)],
              "graph_dir": str(arguments.graph_dir), "reactome_release": reactome_release,
              "evidence_dir": str(arguments.evidence_dir), "label_selection": str(arguments.label_selection), **input_digests}
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with open(arguments.output, "x") as handle:
        handle.write(json.dumps(record, indent=1) + "\n")
    print(json.dumps({key: value for key, value in record.items() if key not in ("perturbation_ids", "examined_seeds", "kept_positives_by_symptom")}, indent=1))


if __name__ == "__main__":
    main()
