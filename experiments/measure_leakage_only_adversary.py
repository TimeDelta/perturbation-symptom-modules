"""What can a predictor earn from the open leakage channels alone, under the item 25 split? (Decision 9.35.)

What it is for now. Decision 9.35 was ruled on 24 November 2026 (the owner: "Use 1.a but not on current graph. On graph
at time of draw, right?"): the adversary's advantage must stay below one standard error of the test's own reading, with
the curve fitted on development-set pseudo-draws on the graph the draw is made on. The pseudo-draw records this script
writes are what experiments/calibrate_leakage_ceiling.py fits that curve on. Until 24 November 2026 the script measured
a control and set no threshold, on the owner's words of 14 October 2026: "build the adversary. it's a good control", and
then "you can remove the leakage ceiling construction since that adversary is being used instead"; the ruling of 24
November sets a ceiling built from this adversary, checked at the draw.

What it does. Over --num-draws pseudo-draws of the item 25 rule on the development data, each draw gives a held-out set
and a training set. The adversary is fitted on the training labels and scores the held-out rows from the training
perturbations that reach them through the channels it is given, nothing else: the shared seed node channel always, and
the reached-node channel of decision 9.36 when --reached-node-hops is given (off by default, so a run without it is the
run of 14 October 2026). Its advantage over each registered baseline is read in macro and micro AUPRC with the paired
bootstrap of design section 7, so the number is comparable with the measured precision of the readings. Until 27
November 2026 this docstring also said it was comparable "with H1's 0.05 requirement"; that floor was removed on 15
October 2026. Each draw also records its label-free statistics: seen_target_share always, and seen_reached_node_share
with the reached-node channel on.

The reached-node channel. With --reached-node-hops K the adversary also counts as a neighbour a training perturbation
whose forward walk of at most K steps reaches a node the held-out perturbation's walk reaches, over the (held-out type,
training type) pairs of --reached-node-type-pairs and the edges of --reached-node-edges, both required with it because
no ruling settles them (9.36 measured the gene side on every stored edge). k is a sensitivity sweep (9.36), so the
script is run once per K. A run with the channel on must name its own --checkpoint-dir, --json-output and
--markdown-output, so it can neither resume from the shared seed node run's checkpoints nor overwrite
docs/generated/leakage_only_adversary.json and .md, the record of 14 October 2026 on
graph_full_neuronal_split_binders_drugs_v4_enzymes.

What a checkpoint directory holds. A checkpointed draw is named by its pooling rule and seed only, so the directory also
holds checkpoint_inputs.json, the inputs its draws were computed on (the graph, evidence and label selection digests,
the grouping, the bootstrap count, the excluded lockbox and the channel list). A run whose inputs differ from those, or
that finds draws without that file (a directory written before 27 November 2026), refuses to resume from it, since its
output would record this run's digests over draws made on other inputs, which is what
experiments/calibrate_leakage_ceiling.py checks the graph by.

The draw's options. --hold-out-genes-encoding-held-out-targets, --hold-out-whole-groups-of-those-genes and
--gene-side-rule are the opt-in options of target_held_out_split.HeldOutDrawOptions (built 28 November 2026 from
docs/drafts/held_out_draw_methods_2026-11-28.md, M1 and M2; none is ruled), off by default, so a run without them is the
run it was before. A run with any of them on records them in its output (held_out_draw_options), must name its own
--checkpoint-dir, --json-output and --markdown-output as a reached-node run does, and is what
experiments/calibrate_leakage_ceiling.py and experiments/draw_held_out_set.py check their own options against, so the
pseudo-draws and the draw use one rule.

Why pseudo-draws and not the real one. The adversary needs the held-out labels to be *scored*, which the lockbox
forbids before `runs/confirmatory/SCORED` exists. Development pseudo-draws under the same rule need no lockbox label, so
this runs before the draw. The pseudo-draw seeds are 0 to --num-draws - 1; experiments/draw_held_out_set.py refuses a
real seed order that repeats one, since a pseudo-draw at the real draw's seed scores the very rows the draw holds out.

Usage:
  python experiments/measure_leakage_only_adversary.py --num-draws 20
  python experiments/measure_leakage_only_adversary.py --num-draws 20 --reached-node-hops 2 \\
      --reached-node-type-pairs gene:gene --reached-node-edges stored --checkpoint-dir <dir> \\
      --json-output <path> --markdown-output <path>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from mechanistic_pathway_learning.data_release import sha256_of_file
from mechanistic_pathway_learning.evaluation.experiment_data import (
    GENE_TO_PROTEIN_FILE, load_experiment_data, read_proteins_encoded_by_gene, restrict_to_perturbations)
from mechanistic_pathway_learning.evaluation.leakage_only_adversary import (
    LeakageOnlyAdversary, POOLING_RULES, REACH_EDGE_SETS, channel_breakdown, neighbours_through_the_channels,
    reach_edges, reached_nodes_of_perturbations, registered_channel_list, seed_nodes_of_perturbations,
    seen_reached_node_share, seen_target_share)
from mechanistic_pathway_learning.evaluation.ranking_and_calibration_metrics import (
    macro_statistic, micro_auprc, paired_bootstrap_macro_difference, paired_bootstrap_micro_difference)
from mechanistic_pathway_learning.evaluation.target_held_out_split import (
    GENE_SIDE_RULES, HeldOutDrawOptions, targets_of_drugs, two_sided_held_out_perturbations)
from mechanistic_pathway_learning.graph.drug_entry_nodes import DRUG_ENTRY_FILE
from mechanistic_pathway_learning.models.baselines.popularity_baseline import PopularityBaseline

# a 95 percent bootstrap interval is about this many standard errors wide on each side, used only to turn the interval
# the registered machinery returns into the standard error the readings are compared against
STANDARD_ERRORS_IN_A_95_PERCENT_HALF_WIDTH = 1.959964
# The files of a graph directory that load_experiment_data reads, so their SHA-256 values say which graph a measurement
# was made on. The two optional ones are hashed when present.
GRAPH_FILES_READ = ("nodes.parquet", "edges.parquet", "relation_types.json")
OPTIONAL_GRAPH_FILES_READ = (GENE_TO_PROTEIN_FILE, DRUG_ENTRY_FILE)


def graph_file_sha256(graph_directory: Path) -> dict[str, str]:
    """file name -> SHA-256 for the files of the graph directory load_experiment_data reads (GRAPH_FILES_READ, and
    OPTIONAL_GRAPH_FILES_READ when present): what says which graph the pseudo-draws were made on, since decision 9.35
    fits its curve on the graph the draw is made on. experiments/calibrate_leakage_ceiling.py and
    experiments/draw_held_out_set.py check the graph by it."""
    directory = Path(graph_directory)
    digests = {}
    for name in GRAPH_FILES_READ:
        path = directory / name
        if not path.is_file():
            raise FileNotFoundError(f"{path} is missing; a graph directory holds {', '.join(GRAPH_FILES_READ)}")
        digests[name] = sha256_of_file(path)
    for name in OPTIONAL_GRAPH_FILES_READ:
        if (directory / name).is_file():
            digests[name] = sha256_of_file(directory / name)
    return digests


def registered_two_sided_draw(data, draw_seed: int, draw_options: HeldOutDrawOptions | None = None,
                              proteins_encoded_by_gene=None) -> tuple[set[str], set[str]]:
    """The held-out set as the registration actually draws it: **each side at its own registered fraction** (item 25,
    "the genes by the registered disease-cluster grouping and the drugs by the rule below, one seventh of each rather
    than one seventh of the whole").

    Corrected 14 October 2026 after the owner asked "i thought gene perturbations were also being included in the
    lockbox draw ...". They are, and an earlier version of this script drew the drug side only: `held_out_perturbations`
    pulls a gene in only when its own node is a held-out drug **target**, and on a gene/protein-split graph a gene
    node is a drug target only for a target gene the split gave no protein node; every pseudo-draw held out 39, 22 or
    30 drugs and **zero** genes. Since 1,414 of the 1,636 perturbations are genes, the adversary was being scored on 2
    percent of the row mix it will meet.

    Since 27 November 2026 the draw itself is target_held_out_split.two_sided_held_out_perturbations, which
    experiments/draw_held_out_set.py draws by too (since 28 November 2026 through two_sided_held_out_draw, which
    returns the same draw with what the options did); this keeps the name the script has always used. With draw_options (and
    proteins_encoded_by_gene for the identity option) it draws by the opt-in options of 28 November 2026 instead, which
    no ruling registers; without them it draws the registered rule as before.
    """
    return two_sided_held_out_perturbations(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds,
                                            data.node_ids, data.group_ids, draw_seed, options=draw_options,
                                            proteins_encoded_by_gene=proteins_encoded_by_gene)


def one_draw(data, draw_seed: int, pooling_rule: str, num_bootstrap: int, reached_nodes_of_perturbation=None,
             reached_node_type_pairs=None, draw_options: HeldOutDrawOptions | None = None,
             proteins_encoded_by_gene=None) -> dict:
    """One pseudo-draw: the adversary's advantage over popularity, degree-scaled popularity and type popularity, the
    channel counts and the label-free statistics. Without reached_nodes_of_perturbation the adversary has the shared
    seed node channel alone, as in every run before 27 November 2026. draw_options are passed to
    registered_two_sided_draw (off by default)."""
    held_out_ids, held_out_targets = registered_two_sided_draw(data, draw_seed, draw_options, proteins_encoded_by_gene)
    held_out_rows = np.array([index for index, perturbation_id in enumerate(data.perturbation_ids) if str(perturbation_id) in held_out_ids], dtype=int)
    training_rows = np.array([index for index, perturbation_id in enumerate(data.perturbation_ids) if str(perturbation_id) not in held_out_ids], dtype=int)
    if held_out_rows.size == 0 or training_rows.size == 0:
        return {"draw_seed": draw_seed, "usable": False}

    held_out_identifiers = [str(data.perturbation_ids[row]) for row in held_out_rows]
    training_identifiers = [str(data.perturbation_ids[row]) for row in training_rows]
    label_mask = data.label_mask if data.label_mask is not None else np.ones(data.outcomes.shape, dtype=bool)

    seed_nodes_of_perturbation = seed_nodes_of_perturbations(data.perturbation_ids, data.perturbation_seeds, data.node_ids)
    perturbation_types_of_id = {str(perturbation_id): kind for perturbation_id, kind in zip(data.perturbation_ids, data.perturbation_types)}
    neighbours = neighbours_through_the_channels(
        held_out_identifiers, training_identifiers, seed_nodes_of_perturbation, reached_nodes_of_perturbation,
        perturbation_types_of_id, reached_node_type_pairs)

    adversary = LeakageOnlyAdversary(pooling_rule).fit(training_identifiers, data.outcomes[training_rows], label_mask[training_rows])
    adversary_scores = adversary.predict(held_out_identifiers, neighbours)

    held_out_outcomes, held_out_mask = data.outcomes[held_out_rows], label_mask[held_out_rows]
    held_out_degrees = np.array([float(data.node_degree[data.perturbation_seeds[row]].sum()) for row in held_out_rows])
    training_degrees = np.array([float(data.node_degree[data.perturbation_seeds[row]].sum()) for row in training_rows])

    macro_average = macro_statistic()
    result = {"draw_seed": draw_seed, "usable": True, "pooling_rule": pooling_rule,
              "held_out_perturbations": int(held_out_rows.size), "held_out_targets": int(len(held_out_targets)),
              "held_out_drugs": int(sum(1 for row in held_out_rows if data.perturbation_types[row] == "drug")),
              "held_out_genes": int(sum(1 for row in held_out_rows if data.perturbation_types[row] != "drug")),
              "seen_target_share": seen_target_share(
                  targets_of_drugs(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids), held_out_identifiers),
              "adversary_macro_auprc": float(macro_average(adversary_scores, held_out_outcomes, held_out_mask)),
              "adversary_micro_auprc": float(micro_auprc(adversary_scores, held_out_outcomes, held_out_mask))}
    if reached_nodes_of_perturbation is not None:
        result["seen_reached_node_share"] = seen_reached_node_share(
            reached_nodes_of_perturbation, held_out_identifiers, training_identifiers, perturbation_types_of_id,
            reached_node_type_pairs)
    result.update(channel_breakdown(neighbours, perturbation_types_of_id))

    # The drug stratum, approved by the owner 14 October 2026 ("1. yes"). The whole-lockbox reading is diluted: in the
    # shared seed node run of 14 October 2026 (graph_full_neuronal_split_binders_drugs_v4_enzymes) a draw held out about
    # 170 genes to 22-39 drugs, no gene shared a seed node with anything, and the adversary fell back to the base rate
    # on every gene row, so its whole-lockbox macro and micro sat almost on top of popularity whatever the drug side was
    # doing. That channel exists only among drugs, so its bound has force only where it is read. With the reached-node
    # channel on, gene rows can have neighbours, and the gene stratum is read the same way.
    held_out_is_a_drug = np.array([data.perturbation_types[row] == "drug" for row in held_out_rows], dtype=bool)
    strata = {"all_held_out": np.ones(len(held_out_rows), dtype=bool), "drug_stratum": held_out_is_a_drug,
              "gene_stratum": ~held_out_is_a_drug}

    # type_popularity is the comparator the pooled reading needs, and reading against popularity alone was a defect.
    # Popularity gives every row the same score for a symptom, so it cannot order a drug above a gene. In the first
    # stratum run of 14 October 2026 the adversary had the shared seed node channel alone and its score differed from
    # the base rate on drug rows only, so it ordered drugs first, and with the drug base rate well above the gene one
    # that earned a large AUPRC gain for KNOWING WHICH PERTURBATIONS ARE DRUGS rather than for any lookup. Against
    # popularity the pooled macro advantage came out at +0.139, above the drug stratum's own +0.041, which is the
    # signature of that contamination (the graph is not recorded beside those two numbers; the script's default that
    # day was graph_full_neuronal_split_binders_drugs_v4_enzymes). Within the drug stratum every row is a drug, so there
    # type_popularity and popularity coincide and the stratum numbers were never affected. With the reached-node channel
    # on, gene rows can have neighbours too, so their scores can differ from the base rate as well.
    training_kinds = np.asarray([data.perturbation_types[row] for row in training_rows])
    held_out_kinds = np.asarray([data.perturbation_types[row] for row in held_out_rows])

    for baseline_name, scale_by_degree in (("popularity", False), ("degree_popularity", True), ("type_popularity", False)):
        if baseline_name == "type_popularity":
            baseline_scores = np.zeros((len(held_out_rows), data.outcomes.shape[1]))
            for kind in np.unique(held_out_kinds):
                of_this_kind_in_training = training_kinds == kind
                if not of_this_kind_in_training.any():
                    of_this_kind_in_training = np.ones(len(training_rows), dtype=bool)
                fitted_on_kind = PopularityBaseline().fit(
                    data.outcomes[training_rows][of_this_kind_in_training], None,
                    label_mask[training_rows][of_this_kind_in_training])
                baseline_scores[held_out_kinds == kind] = fitted_on_kind.predict(int((held_out_kinds == kind).sum()))
        else:
            baseline = PopularityBaseline(scale_by_degree=scale_by_degree).fit(
                data.outcomes[training_rows], training_degrees, label_mask[training_rows])
            baseline_scores = baseline.predict(len(held_out_rows), held_out_degrees)
        for stratum_name, in_stratum in strata.items():
            if in_stratum.sum() < 2:
                continue
            prefix = "" if stratum_name == "all_held_out" else f"{stratum_name}_"
            macro = paired_bootstrap_macro_difference(adversary_scores[in_stratum], baseline_scores[in_stratum],
                                                      held_out_outcomes[in_stratum], num_bootstrap=num_bootstrap,
                                                      random_seed=draw_seed, mask=held_out_mask[in_stratum])
            micro = paired_bootstrap_micro_difference(adversary_scores[in_stratum], baseline_scores[in_stratum],
                                                      held_out_outcomes[in_stratum], num_bootstrap=num_bootstrap,
                                                      random_seed=draw_seed, mask=held_out_mask[in_stratum])
            for reading_name, reading in (("macro", macro), ("micro", micro)):
                half_width = (reading["upper"] - reading["lower"]) / 2.0
                result[f"{prefix}{reading_name}_advantage_over_{baseline_name}"] = reading["difference"]
                result[f"{prefix}{reading_name}_interval_over_{baseline_name}"] = [reading["lower"], reading["upper"]]
                result[f"{prefix}{reading_name}_standard_error_over_{baseline_name}"] = half_width / STANDARD_ERRORS_IN_A_95_PERCENT_HALF_WIDTH
    return result


def summarise(draws: list[dict]) -> dict:
    """Means and ranges over the usable draws, per reading."""
    usable = [draw for draw in draws if draw.get("usable")]
    summary = {"usable_draws": len(usable)}
    if not usable:
        return summary
    for key in sorted(usable[0]):
        values = [draw[key] for draw in usable if isinstance(draw.get(key), (int, float)) and not isinstance(draw.get(key), bool)]
        if len(values) == len(usable) and values:
            finite = [value for value in values if np.isfinite(value)]
            if finite:
                summary[key] = {"mean": float(np.mean(finite)), "minimum": float(np.min(finite)), "maximum": float(np.max(finite)),
                                "draws": len(finite)}
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, default=Path("data/processed/graph_full_neuronal_split_binders_drugs_v4_enzymes"))
    parser.add_argument("--evidence-dir", type=Path, default=Path("data/processed/evidence_full_v4"))
    parser.add_argument("--label-selection", type=Path, default=Path("data/processed/label_selection/better_v2_full_v4.parquet"))
    parser.add_argument("--group-by", default="disease_cluster_and_targets")
    parser.add_argument("--num-draws", type=int, default=20)
    parser.add_argument("--pooling-rules", nargs="+", default=list(POOLING_RULES), choices=list(POOLING_RULES),
                        help="which pooling rules to measure; the default measures all of them, which is the cross "
                             "product this script is slowest on")
    parser.add_argument("--checkpoint-dir", type=Path, default=None,
                        help="one JSON per (pooling rule, draw). A draw already written here is skipped, so a run "
                             "stopped by the background time limit resumes where it left off instead of starting over; "
                             "a directory whose checkpoint_inputs.json names other inputs, or that holds draws without "
                             "one, is refused. Defaults to runs/leakage_only_adversary_draws for the shared seed node run; "
                             "required with --reached-node-hops")
    parser.add_argument("--num-bootstrap", type=int, default=1000)
    parser.add_argument("--lockbox", type=Path, default=None,
                        help="a drawn lockbox whose perturbations are excluded, so the calibration reads development rows only")
    parser.add_argument("--reached-node-hops", type=int, default=None,
                        help="switch on the reached-node channel of decision 9.36 with walks of at most this many steps "
                             "(off by default; 0 reproduces the shared seed node channel). Needs --reached-node-type-pairs "
                             "and --reached-node-edges")
    parser.add_argument("--reached-node-type-pairs", nargs="+", default=None, metavar="HELD_OUT_TYPE:TRAINING_TYPE",
                        help="the (held-out type, training type) pairs the reached-node channel covers, e.g. gene:gene; "
                             "required with --reached-node-hops, since no ruling says whether drugs enter it")
    parser.add_argument("--reached-node-edges", choices=list(REACH_EDGE_SETS), default=None,
                        help="the edges the reached-node walk follows (leakage_only_adversary.REACH_EDGE_SETS); required "
                             "with --reached-node-hops")
    parser.add_argument("--json-output", type=Path, default=None,
                        help="defaults to docs/generated/leakage_only_adversary.json for the shared seed node run; "
                             "required with --reached-node-hops")
    parser.add_argument("--markdown-output", type=Path, default=None,
                        help="defaults to docs/generated/leakage_only_adversary.md for the shared seed node run; "
                             "required with --reached-node-hops")
    add_held_out_draw_option_arguments(parser)
    arguments = parser.parse_args()
    draw_options = held_out_draw_options_from_arguments(parser, arguments)
    refuse_shared_run_paths_for_draw_options(parser, arguments, draw_options)
    reached_node_type_pairs = resolve_channel_arguments(parser, arguments)

    data = load_experiment_data(arguments.graph_dir, arguments.evidence_dir, group_by=arguments.group_by,
                               label_selection=arguments.label_selection)
    excluded_lockbox_perturbations = set()
    if arguments.lockbox is not None:
        excluded_lockbox_perturbations = {str(perturbation_id) for perturbation_id in json.loads(arguments.lockbox.read_text())["perturbation_ids"]}
        keep = [index for index, perturbation_id in enumerate(data.perturbation_ids) if str(perturbation_id) not in excluded_lockbox_perturbations]
        data = _restrict(data, keep)
    reached_nodes_of_perturbation = None
    if arguments.reached_node_hops is not None:
        walk_source, walk_target = reach_edges(data.edge_source, data.edge_target, data.is_currency, arguments.reached_node_edges)
        reached_nodes_of_perturbation = reached_nodes_of_perturbations(
            data.perturbation_ids, data.perturbation_seeds, data.node_ids, walk_source, walk_target, arguments.reached_node_hops)
    proteins_encoded_by_gene = (read_proteins_encoded_by_gene(arguments.graph_dir)
                                if draw_options.hold_out_genes_encoding_held_out_targets else None)

    results = {"pooling_rules": {}, "excluded_lockbox_perturbations": len(excluded_lockbox_perturbations),
               "evidence_dir": str(arguments.evidence_dir), "graph_dir": str(arguments.graph_dir),
               "label_selection": str(arguments.label_selection), "num_draws": arguments.num_draws,
               "pseudo_draw_seeds": list(range(arguments.num_draws)), "group_by": arguments.group_by,
               "num_bootstrap": arguments.num_bootstrap,
               "lockbox_excluded": None if arguments.lockbox is None else str(arguments.lockbox),
               "channels": registered_channel_list(arguments.reached_node_hops, reached_node_type_pairs, arguments.reached_node_edges),
               "graph_file_sha256": graph_file_sha256(arguments.graph_dir),
               "evidence_records_sha256": sha256_of_file(arguments.evidence_dir / "evidence_records.parquet"),
               "label_selection_sha256": sha256_of_file(arguments.label_selection)}
    if not draw_options.is_default():  # recorded only when an option is on, so a run without them writes what it wrote
        results[DRAW_OPTIONS_KEY] = draw_options.as_record()
    claim_checkpoint_directory(arguments.checkpoint_dir, {key: results[key] for key in CHECKPOINT_INPUT_KEYS
                                                          if key != DRAW_OPTIONS_KEY or key in results})
    completed_draws = 0
    for pooling_rule in arguments.pooling_rules:
        draws = []
        for draw_seed in range(arguments.num_draws):
            checkpoint_path = arguments.checkpoint_dir / f"{pooling_rule}_draw_{draw_seed:03d}.json"
            if checkpoint_path.exists():
                draws.append(json.loads(checkpoint_path.read_text()))
                continue
            draw = one_draw(data, draw_seed, pooling_rule, arguments.num_bootstrap, reached_nodes_of_perturbation,
                            reached_node_type_pairs, draw_options, proteins_encoded_by_gene)
            checkpoint_path.write_text(json.dumps(draw, indent=1) + "\n")
            draws.append(draw)
            completed_draws += 1
            print(f"  {pooling_rule} draw {draw_seed} done and checkpointed", flush=True)
        results["pooling_rules"][pooling_rule] = {"draws": draws, "summary": summarise(draws)}
        print(pooling_rule, json.dumps(results["pooling_rules"][pooling_rule]["summary"], indent=1), flush=True)
    print(f"draws computed this invocation: {completed_draws}; re-run to continue if the run was cut short")

    arguments.json_output.parent.mkdir(parents=True, exist_ok=True)
    arguments.json_output.write_text(json.dumps(results, indent=1) + "\n")
    arguments.markdown_output.write_text(_markdown(results, arguments) + "\n")
    print(f"wrote {arguments.json_output} and {arguments.markdown_output}")


SHARED_SEED_NODE_RUN_DEFAULTS = {"checkpoint_dir": Path("runs/leakage_only_adversary_draws"),
                                 "json_output": Path("docs/generated/leakage_only_adversary.json"),
                                 "markdown_output": Path("docs/generated/leakage_only_adversary.md")}
# What a checkpointed draw depends on besides its pooling rule and seed, which name its file. DRAW_OPTIONS_KEY is in
# a run's inputs only when one of the draw's options is on, so a directory written before 28 November 2026 still
# serves a run without them and refuses a run with them.
CHECKPOINT_INPUTS_FILE = "checkpoint_inputs.json"
DRAW_OPTIONS_KEY = "held_out_draw_options"
CHECKPOINT_INPUT_KEYS = ("graph_file_sha256", "evidence_records_sha256", "label_selection_sha256", "group_by",
                         "num_bootstrap", "lockbox_excluded", "excluded_lockbox_perturbations", "channels",
                         DRAW_OPTIONS_KEY)


def add_held_out_draw_option_arguments(parser) -> None:
    """The three flags of target_held_out_split.HeldOutDrawOptions, off by default. experiments/calibrate_leakage_ceiling.py
    and experiments/draw_held_out_set.py add the same flags, so a measurement, its calibration and the draw state one rule."""
    parser.add_argument("--hold-out-genes-encoding-held-out-targets", action="store_true",
                        help="draft option, not ruled: also hold out a gene perturbation whose gene encodes a held-out "
                             "target protein (gene_to_protein.parquet; changes nothing on a merged graph)")
    parser.add_argument("--hold-out-whole-groups-of-those-genes", action="store_true",
                        help="draft option M1, not ruled: hold out the whole leakage group of each gene perturbation held "
                             "out with a held-out target, counted first on the gene side; needs the option above")
    parser.add_argument("--gene-side-rule", choices=list(GENE_SIDE_RULES), default="fold_zero",
                        help="fold_zero (the rule as it stands) or seeded_group_prefix (draft option M2, not ruled)")


def held_out_draw_options_from_arguments(parser, arguments) -> HeldOutDrawOptions:
    """The options the three flags of add_held_out_draw_option_arguments name; a combination they refuse is a usage error."""
    try:
        return HeldOutDrawOptions(hold_out_genes_encoding_held_out_targets=arguments.hold_out_genes_encoding_held_out_targets,
                                  hold_out_whole_groups_of_those_genes=arguments.hold_out_whole_groups_of_those_genes,
                                  gene_side_rule=arguments.gene_side_rule)
    except ValueError as error:
        parser.error(str(error))


def refuse_shared_run_paths_for_draw_options(parser, arguments, draw_options: HeldOutDrawOptions) -> None:
    """A run with a draw option on must name its own checkpoint directory and outputs, as a reached-node run must, so it
    neither resumes from the shared seed node run's checkpoints nor overwrites the committed record of 14 October 2026."""
    if draw_options.is_default():
        return
    missing = [f"--{name.replace('_', '-')}" for name in SHARED_SEED_NODE_RUN_DEFAULTS if getattr(arguments, name) is None]
    if missing:
        parser.error(f"a run with a draw option on must name {', '.join(missing)}")
    for name, default in SHARED_SEED_NODE_RUN_DEFAULTS.items():
        if Path(getattr(arguments, name)).resolve() == default.resolve():
            parser.error(f"--{name.replace('_', '-')} {default} belongs to the shared seed node run; name another path")


def claim_checkpoint_directory(checkpoint_dir: Path, inputs: dict) -> None:
    """Make checkpoint_dir the store of draws computed on inputs, or refuse it.

    A directory whose CHECKPOINT_INPUTS_FILE records other inputs is refused, and so is one holding draws with no such
    file, since resuming from either would write this run's digests over draws made on other inputs. An empty
    directory, or a new one, has the file written."""
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    inputs_path = checkpoint_dir / CHECKPOINT_INPUTS_FILE
    inputs = json.loads(json.dumps(inputs))  # compared as it will read back
    if inputs_path.exists():
        recorded = json.loads(inputs_path.read_text())
        differing = sorted(key for key in set(recorded) | set(inputs) if recorded.get(key) != inputs.get(key))
        if differing:
            raise SystemExit(f"{checkpoint_dir} holds draws computed on other inputs ({', '.join(differing)} differ); "
                             "name another --checkpoint-dir")
        return
    if any(checkpoint_dir.glob("*_draw_*.json")):
        raise SystemExit(f"{checkpoint_dir} holds draws with no {CHECKPOINT_INPUTS_FILE}, so which inputs they were computed "
                         "on is unknown; name another --checkpoint-dir")
    inputs_path.write_text(json.dumps(inputs, indent=1, sort_keys=True) + "\n")


def parse_type_pairs(texts) -> list[tuple[str, str]]:
    """["gene:gene", "drug:gene"] -> [("gene", "gene"), ("drug", "gene")], held-out type first."""
    pairs = []
    for text in texts:
        held_out_type, separator, training_type = str(text).partition(":")
        if not separator or not held_out_type or not training_type or ":" in training_type:
            raise ValueError(f"a reached-node type pair is HELD_OUT_TYPE:TRAINING_TYPE, not {text!r}")
        pairs.append((held_out_type, training_type))
    return pairs


def resolve_channel_arguments(parser, arguments) -> list[tuple[str, str]] | None:
    """The reached-node type pairs, after checking the channel's arguments come together, and the output defaults.

    The shared seed node run keeps the paths it always had. A reached-node run must name its own, so it cannot resume
    from the other run's checkpoints (which are named by pooling rule and seed only) or overwrite the committed
    record of 14 October 2026."""
    channel_arguments = (arguments.reached_node_type_pairs, arguments.reached_node_edges)
    if arguments.reached_node_hops is None:
        if any(value is not None for value in channel_arguments):
            parser.error("--reached-node-type-pairs and --reached-node-edges need --reached-node-hops")
        for name, default in SHARED_SEED_NODE_RUN_DEFAULTS.items():
            if getattr(arguments, name) is None:
                setattr(arguments, name, default)
        return None
    if arguments.reached_node_hops < 0:
        parser.error("--reached-node-hops is a number of steps, 0 or more")
    if any(value is None for value in channel_arguments):
        parser.error("--reached-node-hops needs --reached-node-type-pairs and --reached-node-edges, which have no default")
    missing = [f"--{name.replace('_', '-')}" for name in SHARED_SEED_NODE_RUN_DEFAULTS if getattr(arguments, name) is None]
    if missing:
        parser.error(f"a run with the reached-node channel must name {', '.join(missing)}")
    for name, default in SHARED_SEED_NODE_RUN_DEFAULTS.items():
        if Path(getattr(arguments, name)).resolve() == default.resolve():
            parser.error(f"--{name.replace('_', '-')} {default} belongs to the shared seed node run; name another path")
    try:
        return parse_type_pairs(arguments.reached_node_type_pairs)
    except ValueError as error:
        parser.error(str(error))


def _restrict(data, keep: list[int]):
    """A copy of the experiment data holding only the given perturbation rows, by
    experiment_data.restrict_to_perturbations, which slices every per-perturbation field. Until 28 November 2026 this
    sliced a list of its own, which left in_metabolic_layer, masked_for_soft_evidence, evidenced_negative_power,
    perturbation_target_seeds, perturbation_parts and perturbation_seed_parts at their full length; one_draw reads none
    of them (nor label_selection_summary, to which restrict_to_perturbations adds the counts after the restriction), so
    the change gives every measurement the numbers it gave before."""
    kept_perturbation_mask = np.zeros(len(data.perturbation_ids), dtype=bool)
    kept_perturbation_mask[np.asarray(keep, dtype=int)] = True
    return restrict_to_perturbations(data, kept_perturbation_mask)


def _markdown(results: dict, arguments) -> str:
    """The page. Without the reached-node channel and the draw's options it writes the page of 14 October 2026 word for
    word (a draw option on adds one paragraph naming it, _draw_options_lines), which is what
    docs/generated/leakage_only_adversary.md holds; that page's comparison with "H1's registered requirement of a 0.05
    macro and micro difference" and its account of route transfer as "the hypothesis under test rather than a leak" are
    history (the floor was removed on 15 October 2026, and decision 9.36 put sharing within k hops into the adversary on
    24 November 2026), kept so the generator still writes the record it generated. A run with the reached-node channel
    writes the current account instead."""
    if arguments.reached_node_hops is not None:
        return _markdown_with_the_reached_node_channel(results, arguments)
    lines = ["# The leakage-only adversary (generated by experiments/measure_leakage_only_adversary.py)", "",
             f"Evidence {arguments.evidence_dir}, label selection {arguments.label_selection}, graph {arguments.graph_dir}; "
             f"{arguments.num_draws} pseudo-draws of the item 25 rule at the registered held-out fraction, "
             f"{arguments.num_bootstrap} bootstrap resamples per reading.", "", *_draw_options_lines(results),
             "The adversary knows two things: which training perturbations share a seed node with the held-out "
             "perturbation, and the training labels. No edge, no propagation, no descriptor. It is handed the leaked "
             "labels directly, so its advantage is an upper bound on what any model could take from this channel by "
             "lookup. A held-out perturbation with no leaked neighbour takes the training base rate, which keeps the "
             "advantage a measure of the leak rather than a mixture of a leak and a handicap.", "",
             "Read against H1's registered requirement of a 0.05 macro and micro difference, and against the measured "
             "precision of the readings (paired-bootstrap 95 percent half-widths of 0.019 to 0.063 macro and 0.018 to "
             "0.041 micro, growing by about 1.4 at Holm's smallest level).", ""]
    lines += _summary_tables(results)
    lines += ["## The channel this does not cover", "",
              "Two perturbations sharing a seed node perturb the same node, so a label transfers by identity and a "
              "lookup substitutes for mechanism: that is the channel measured here. Two perturbations whose seeds sit "
              "in one pathway are the hypothesis under test rather than a leak, so transfer along a route is not "
              "measured and must not be: bounding it would bound the study's own subject. A channel outside both "
              "descriptions is a disclosed limitation."]
    return "\n".join(lines)


def _draw_options_lines(results: dict) -> list[str]:
    """A paragraph naming the draw's options when one is on; nothing otherwise, so the page of a run without them is
    unchanged."""
    if DRAW_OPTIONS_KEY not in results:
        return []
    options = ", ".join(f"{name} {value}" for name, value in results[DRAW_OPTIONS_KEY].items())
    return [f"The draw used the draft options of 28 November 2026, which no ruling registers ({options}; "
            "target_held_out_split.HeldOutDrawOptions), so these are not pseudo-draws of the registered rule.", ""]


def _summary_tables(results: dict) -> list[str]:
    lines = []
    for pooling_rule, block in results["pooling_rules"].items():
        summary = block["summary"]
        lines += [f"## {pooling_rule}", "", f"Usable draws: {summary.get('usable_draws', 0)}.", "",
                  "| reading | mean | minimum | maximum |", "|---|---|---|---|"]
        for key in sorted(summary):
            value = summary[key]
            if isinstance(value, dict):
                lines.append(f"| {key.replace('_', ' ')} | {value['mean']:.4f} | {value['minimum']:.4f} | {value['maximum']:.4f} |")
        lines.append("")
    return lines


def _markdown_with_the_reached_node_channel(results: dict, arguments) -> str:
    channels = results["channels"]
    reached = next(channel for channel in channels["scored"] if channel["channel"] == "reached_node")
    pairs = ", ".join(f"{pair['held_out_type']} held out with {pair['training_type']} in training" for pair in reached["covers"])
    lines = ["# The leakage-only adversary with the reached-node channel (generated by experiments/measure_leakage_only_adversary.py)", "",
             f"Evidence {arguments.evidence_dir}, label selection {arguments.label_selection}, graph {arguments.graph_dir}; "
             f"{arguments.num_draws} pseudo-draws of the item 25 rule at the registered held-out fraction, "
             f"{arguments.num_bootstrap} bootstrap resamples per reading.", "", *_draw_options_lines(results),
             "The adversary knows two things: which training perturbations reach the held-out perturbation through the "
             "channels below, and the training labels. No edge weight or sign, no propagation, no descriptor. It is "
             "handed the leaked labels directly, so its advantage is an upper bound on what any model could take from "
             "these channels by lookup. A held-out perturbation with no neighbour takes the training base rate.", "",
             f"Channels scored: a shared seed node, for every pair; and a node reached by both walks of at most "
             f"{reached['maximum_hops']} steps over the edges '{reached['reach_edge_set']}' (decision 9.36), for {pairs}. "
             "Decision 9.35 (ruled 24 November 2026) reads the advantage against one standard error of the test's own "
             "reading, on the graph the draw is made on; this page measures and sets no ceiling, which "
             "experiments/calibrate_leakage_ceiling.py fits from these draws.", ""]
    lines += _summary_tables(results)
    lines += ["## The channels this does not cover", ""] + [f"- {text}" for text in channels["not_scored"]]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
