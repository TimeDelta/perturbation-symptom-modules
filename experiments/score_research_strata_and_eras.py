"""Score amendment item 38's two descriptive readings on the held-out set: (g), by how many records name a pair, and
(d), by when the pair was first recorded (docs/preregistration.md, item 38 (d) and (g); the owner, 23 November 2026).

Both are descriptive. Neither enters H1, H2 or P1, spends alpha, or has an interval compared with a level, so this
script reports intervals and no p-value. Because each reading is a model-minus-baseline difference on the held-out
set, which is scored once, it refuses to run until experiments/score_confirmatory.py has scored that set (its SCORED
marker and lockbox_scores.json in --confirmatory-output-dir, for the same lockbox file), and it is reported beside
that scoring, in the section labelled descriptive.

Inputs:
- the eras and strata experiments/write_research_strata_and_eras.py wrote before the draw (--strata-record and
  --strata-cells), and the search table of (g) they were written from (--search-table). Before reading a stratum the
  script checks the cells file against the record's SHA-256, the search table, graph, evidence table and label selection
  against the hashes the record holds, and recomputes the assignment from the search table and the data, refusing if
  any cell's stratum differs ("The cuts are not moved after the draw"). The recomputation refuses, as the writing
  did, while any cell is unexplained;
- the tested model's lockbox runs on the real labels (<run-root>/<model>_<group-by>_confirmatory/lockbox_seed<k>),
  accepted by score_confirmatory.read_model_run under the same checks the confirmatory scorer applies, and the
  baselines of run_baselines.py --score-lockbox (<baseline-root>/seed<k>/predictions_lockbox_<name>.npy), for the same
  seeds. A missing or refused run stops the script.

Readings, each per perturbation type (genes and drugs apart, the main reading), and for (g) pooled beside them:
- research_stratum: the stratum of the form the type took (tertiles, or none, fewer and more);
- none_against_any: the two-stratum form, "reported beside it always";
- first_record_era_thirds and first_record_era_two_way (types apart only; (d) registers no pooled reading): the eras
  of the first-record date, as thirds and at the end of 2015, each with the undated positives as a stratum of their own;
- registered_date_era_two_way (genes only): the same two-way cut under the registered gene date, "The gene reading is
  given under both dates".
The pooled research_stratum reading is given only when both types took the same form; otherwise the output says why.

Inside each stratum: a stratum of a research reading holds its own cells, positive and unlabelled; an era holds its
positives, scored against every unlabelled cell of the reading ("Each era's positives are scored against the same
unlabelled cells of the held-out set"). The registered macro AUPRC (score_confirmatory.macro_auprc) over the symptoms
with at least MINIMUM_POSITIVES_TO_SCORE of the stratum's positives among the held-out cells, and the registered micro
AUPRC (score_confirmatory.micro_auprc) over the symptoms with that many of the stratum's positives in the whole data:
the registered rules, each applied within the stratum ("minimum_positives_to_score applied within the stratum"). Both
symptom lists are written out, "because the strata will not share one list". For the tested model and every
baseline, per seed and as the seed mean; the best baseline of the stratum, per macro and micro, "the one with the
highest seed-mean score in that stratum, chosen without reference to any model"; the seed mean of the model minus that
baseline; its 95 per cent interval from the paired bootstrap over the leakage groups of the held-out rows of the
reading's perturbations (score_confirmatory.bootstrap_rows, unit group: the same resampled rows for the model and the
baseline, every seed and every stratum), the 2.5 and 97.5 percentiles of the resampled differences; and the number of
held-out cells and positives. AUPRC values are not compared between strata or eras, since they move with the number
of positives: only the difference inside each is read.

Usage, from the repository root, after experiments/score_confirmatory.py:
  PYTHONPATH=. python experiments/score_research_strata_and_eras.py --search-table <search output> \\
      --strata-record <record.json> --strata-cells <cells.csv>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_confirmatory import (BASELINES, MINIMUM_POSITIVES_TO_SCORE, bootstrap_rows, chosen_models, expected_run_arguments,  # noqa: E402
                                macro_auprc, micro_auprc, read_model_run)
from write_research_strata_and_eras import input_hashes  # noqa: E402

from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data, read_lockbox  # noqa: E402
from mechanistic_pathway_learning.evaluation.research_strata_and_eras import (  # noqa: E402
    NOT_IN_THE_READING, READING_COLUMNS, REGISTERED_DATE_TYPE, UNLABELLED_CELL, assign_strata_and_eras, file_sha256, read_cell_search_table,
    read_cells, same_assignment, scored_cells_from_experiment_data)

POOLED_SCOPE = "pooled"
POOLED_READINGS = ("research_stratum", "none_against_any")  # (g): "the pooled reading is given beside it"; (d) is read per type
REGISTERED_DATE_READING = "registered_date_era_two_way"
METRICS = ("macro", "micro")


def cell_label_arrays(cells, perturbation_ids: list[str], symptoms: list[str]) -> dict[str, np.ndarray]:
    """Each reading's stratum per cell as a [num_perturbations, num_symptoms] array, NOT_IN_THE_READING where the cells
    file holds no stratum (a symptom the table does not score among them)."""
    row_of = {perturbation_id: row for row, perturbation_id in enumerate(perturbation_ids)}
    column_of = {symptom: column for column, symptom in enumerate(symptoms)}
    rows = cells.perturbation_id.map(row_of)
    columns = cells.symptom.map(column_of)
    if rows.isna().any() or columns.isna().any():
        raise ValueError("the cells file names perturbations or symptoms the data does not hold")
    arrays = {}
    for reading in READING_COLUMNS:
        labels = np.full((len(perturbation_ids), len(symptoms)), NOT_IN_THE_READING, dtype=object)
        labels[rows.to_numpy(dtype=int), columns.to_numpy(dtype=int)] = cells[reading].fillna(NOT_IN_THE_READING).to_numpy(dtype=object)
        arrays[reading] = labels
    return arrays


def stratum_masks(labels: np.ndarray, reading: str, label_mask: np.ndarray) -> dict[str, np.ndarray]:
    """The cells each stratum of a reading scores, over the rows given, in the reading's order: a research stratum its
    own cells; an era its positives and every unlabelled cell of the reading. A stratum no cell of the rows holds is
    left out."""
    kind, order = READING_COLUMNS[reading]
    unlabelled = labels == UNLABELLED_CELL
    masks = {}
    for stratum in order:
        holds = labels == stratum
        if holds.any():
            masks[stratum] = label_mask & (holds | unlabelled) if kind == "positives" else label_mask & holds
    return masks


def best_of(seed_means: dict[str, float]) -> str | None:
    """The baseline with the highest seed-mean score, among those with a defined one; None when none has."""
    defined = {name: value for name, value in seed_means.items() if np.isfinite(value)}
    return max(defined, key=defined.get) if defined else None


def interval(values: list[float]) -> dict:
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)]
    return {"lower_95": float(np.quantile(finite, 0.025)) if finite.size else float("nan"),
            "upper_95": float(np.quantile(finite, 0.975)) if finite.size else float("nan"), "num_resamples_defined": int(finite.size)}


def descriptive_readings(outcomes: np.ndarray, label_mask: np.ndarray, held_out: np.ndarray, perturbation_types: list[str], group_ids: list[str],
                         symptoms: list[str], cell_labels: dict[str, np.ndarray], model_predictions: dict[str, dict[int, np.ndarray]],
                         baseline_predictions: dict[str, dict[int, np.ndarray]], seeds: list[int], num_bootstrap: int, bootstrap_seed: int,
                         minimum_positives_to_score: int, pooled_research_stratum_defined: bool) -> dict:
    """Every reading per scope (each perturbation type, and pooled for (g)), stratum and metric, as the module docstring
    states. outcomes, label_mask and cell_labels cover every perturbation; held_out marks the held-out rows, and every
    prediction array holds those rows, in data order, by every symptom."""
    held_out_rows = np.flatnonzero(held_out)
    types = np.asarray(perturbation_types, dtype=object)
    groups = np.asarray(group_ids, dtype=object)
    positive = np.asarray(outcomes) > 0
    label_mask = np.asarray(label_mask, dtype=bool)
    scopes = {name: types == name for name in sorted(set(types.tolist()))}
    scopes[POOLED_SCOPE] = np.ones(len(types), dtype=bool)
    result = {}
    for scope_index, (scope, of_scope) in enumerate(scopes.items()):
        if scope == POOLED_SCOPE:
            readings = [reading for reading in POOLED_READINGS if reading != "research_stratum" or pooled_research_stratum_defined]
        else:
            readings = [reading for reading in READING_COLUMNS if reading != REGISTERED_DATE_READING or scope == REGISTERED_DATE_TYPE]
        scope_rows = np.flatnonzero(of_scope)
        scope_positions = np.flatnonzero(of_scope[held_out_rows])  # within the held-out arrays
        held_rows = held_out_rows[scope_positions]
        outcomes_held = np.asarray(outcomes, dtype=float)[held_rows]
        group_of_position = groups[held_rows]
        members_of_group = [np.flatnonzero(group_of_position == group) for group in sorted(set(group_of_position.tolist()))]
        predictions = {("model", name): {seed: by_seed[seed][scope_positions] for seed in seeds} for name, by_seed in model_predictions.items()}
        predictions.update({("baseline", name): {seed: by_seed[seed][scope_positions] for seed in seeds} for name, by_seed in baseline_predictions.items()})

        strata = []  # (reading, stratum, held-out mask, macro columns, micro columns)
        entries: dict[str, dict] = {}
        for reading in readings:
            entries[reading] = {}
            whole_masks = stratum_masks(cell_labels[reading][scope_rows], reading, label_mask[scope_rows])
            held_masks = stratum_masks(cell_labels[reading][held_rows], reading, label_mask[held_rows])
            for stratum, whole_mask in whole_masks.items():
                held_mask = held_masks.get(stratum, np.zeros_like(outcomes_held, dtype=bool))
                held_positives = (positive[held_rows] & held_mask).sum(axis=0)
                whole_positives = (positive[scope_rows] & whole_mask).sum(axis=0)
                macro_columns = [column for column in range(len(symptoms)) if held_positives[column] >= minimum_positives_to_score]
                micro_columns = [column for column in range(len(symptoms)) if whole_positives[column] >= minimum_positives_to_score]
                strata.append((reading, stratum, held_mask, macro_columns, micro_columns))
                entries[reading][stratum] = {
                    "held_out_cells": int(held_mask.sum()), "held_out_positives": int((positive[held_rows] & held_mask).sum()),
                    "macro_symptoms": [symptoms[column] for column in macro_columns], "micro_symptoms": [symptoms[column] for column in micro_columns],
                    "held_out_positives_per_macro_symptom": {symptoms[column]: int(held_positives[column]) for column in macro_columns}}

        def scores_on(index: np.ndarray, which: list[tuple[str, str]]) -> dict:
            """Per predictor, seed and stratum, the macro and micro AUPRC on the held-out positions index of the scope."""
            labels = outcomes_held[index]
            chosen_masks = [held_mask[index] for _, _, held_mask, _, _ in strata]
            values = {}
            for key in which:
                values[key] = {}
                for seed in seeds:
                    chosen = predictions[key][seed][index]
                    values[key][seed] = [(macro_auprc(chosen, labels, mask, macro_columns), micro_auprc(chosen, labels, mask, micro_columns))
                                         for mask, (_, _, _, macro_columns, micro_columns) in zip(chosen_masks, strata)]
            return values

        observed = scores_on(np.arange(len(scope_positions)), list(predictions))
        best = []  # per stratum, per metric, the best baseline's key
        for position, (reading, stratum, _, _, _) in enumerate(strata):
            entry = entries[reading][stratum]
            seed_means = {key: [float(np.mean([observed[key][seed][position][metric] for seed in seeds])) for metric in range(len(METRICS))] for key in predictions}
            entry["model_scores"] = {name: {metric: seed_means[("model", name)][index] for index, metric in enumerate(METRICS)}
                                     | {"per_seed": {str(seed): dict(zip(METRICS, observed[("model", name)][seed][position])) for seed in seeds}}
                                     for name in model_predictions}
            entry["baseline_scores"] = {name: {metric: seed_means[("baseline", name)][index] for index, metric in enumerate(METRICS)}
                                        | {"per_seed": {str(seed): dict(zip(METRICS, observed[("baseline", name)][seed][position])) for seed in seeds}}
                                        for name in baseline_predictions}
            chosen = {metric: best_of({name: seed_means[("baseline", name)][index] for name in baseline_predictions}) for index, metric in enumerate(METRICS)}
            entry["best_baseline"] = chosen
            best.append(chosen)
            entry["differences"] = {name: {metric: {"difference": float(np.mean([observed[("model", name)][seed][position][index]
                                                                                 - observed[("baseline", chosen[metric])][seed][position][index] for seed in seeds]))
                                                    if chosen[metric] is not None else float("nan")}
                                           for index, metric in enumerate(METRICS)} for name in model_predictions}

        resampled = {name: [[[] for _ in METRICS] for _ in strata] for name in model_predictions}
        if strata and len(scope_positions):
            needed = [("model", name) for name in model_predictions] + sorted({("baseline", chosen[metric]) for chosen in best for metric in METRICS
                                                                               if chosen[metric] is not None})
            generator = np.random.default_rng(bootstrap_seed + scope_index)
            for _ in range(num_bootstrap):
                values = scores_on(bootstrap_rows("group", members_of_group, len(scope_positions), generator), needed)
                for name in model_predictions:
                    for position, chosen in enumerate(best):
                        for index, metric in enumerate(METRICS):
                            resampled[name][position][index].append(
                                float(np.mean([values[("model", name)][seed][position][index] - values[("baseline", chosen[metric])][seed][position][index]
                                               for seed in seeds])) if chosen[metric] is not None else float("nan"))
        for position, (reading, stratum, _, _, _) in enumerate(strata):
            for name in model_predictions:
                for index, metric in enumerate(METRICS):
                    entries[reading][stratum]["differences"][name][metric].update(interval(resampled[name][position][index]))
        result[scope] = {"held_out_perturbations": int(len(scope_positions)), "held_out_leakage_groups": len(members_of_group), "readings": entries}
        if scope == POOLED_SCOPE and not pooled_research_stratum_defined:
            result[scope]["research_stratum_not_pooled"] = "the types took different forms of strata, so their research strata do not pool"
    return result


def markdown_lines(result: dict, models: list[str], header: list[str]) -> list[str]:
    lines = header[:]
    for scope, scope_entry in result.items():
        for reading, by_stratum in scope_entry["readings"].items():
            lines += ["", f"## {scope}, {reading} ({scope_entry['held_out_perturbations']} held-out perturbations, "
                          f"{scope_entry['held_out_leakage_groups']} leakage groups)", "",
                      "| stratum | held-out cells | held-out positives | macro symptoms | micro symptoms | model | macro: best baseline, model minus it [95%] | micro: best baseline, model minus it [95%] |",
                      "|---|---|---|---|---|---|---|---|"]
            for stratum, entry in by_stratum.items():
                for model in models:
                    cells = []
                    for metric in METRICS:
                        difference = entry["differences"][model][metric]
                        cells.append(f"{entry['best_baseline'][metric]}, {difference['difference']:+.3f} [{difference['lower_95']:+.3f}, {difference['upper_95']:+.3f}]")
                    lines.append(f"| {stratum} | {entry['held_out_cells']} | {entry['held_out_positives']} | {len(entry['macro_symptoms'])} | "
                                 f"{len(entry['micro_symptoms'])} | {model} | " + " | ".join(cells) + " |")
        if "research_stratum_not_pooled" in scope_entry:
            lines += ["", f"{scope}: research_stratum not given: {scope_entry['research_stratum_not_pooled']}."]
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, default=Path("data/processed/graph_full_neuronal"))
    parser.add_argument("--evidence-dir", type=Path, default=Path("data/processed/evidence_full_v2"))
    parser.add_argument("--label-selection", type=Path, default=Path("data/processed/label_selection/better_v2_full_v2.parquet"))
    parser.add_argument("--group-by", default="disease_cluster_and_targets")
    parser.add_argument("--lockbox", type=Path, default=Path("configs/lockbox_v2.json"))
    parser.add_argument("--run-root", type=Path, default=Path("runs/full"), help="holds <model>_<group-by>_confirmatory for every model")
    parser.add_argument("--models", nargs="*", default=None, help="the tested models; default: the configurations chosen in --head-choice")
    parser.add_argument("--head-choice", type=Path, default=Path("configs/head_choice.json"))
    parser.add_argument("--baseline-root", type=Path, default=Path("runs/full/lockbox_v2_baselines"), help="holds seed<k> from run_baselines.py --score-lockbox --seed <k>")
    parser.add_argument("--baselines", nargs="*", default=list(BASELINES))
    parser.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2, 3, 4])
    parser.add_argument("--num-bootstrap", type=int, default=4000, help="resamples of the paired bootstrap (registered rule num_bootstrap)")
    parser.add_argument("--bootstrap-seed", type=int, default=20261008, help="the confirmatory scorer's; each scope draws from this plus its position")
    parser.add_argument("--search-table", type=Path, required=True)
    parser.add_argument("--strata-record", type=Path, required=True, help="experiments/write_research_strata_and_eras.py --output-record")
    parser.add_argument("--strata-cells", type=Path, required=True, help="experiments/write_research_strata_and_eras.py --output-cells")
    parser.add_argument("--confirmatory-output-dir", type=Path, default=Path("runs/confirmatory"), help="where experiments/score_confirmatory.py wrote SCORED")
    parser.add_argument("--output", type=Path, default=Path("runs/confirmatory/research_strata_and_eras.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("runs/confirmatory/research_strata_and_eras.md"))
    parser.add_argument("--allow-runs-without-refit", action="store_true", help="smoke tests on runs trained before 8 October 2026 only, as in score_confirmatory.py")
    arguments = parser.parse_args()

    lockbox_sha256 = file_sha256(arguments.lockbox)
    scores_path = arguments.confirmatory_output_dir / "lockbox_scores.json"
    if not (arguments.confirmatory_output_dir / "SCORED").exists() or not scores_path.exists():
        raise SystemExit(f"not run: experiments/score_confirmatory.py has not scored the held-out set into {arguments.confirmatory_output_dir}; "
                         "these readings are reported beside that scoring, not before it")
    if json.loads(scores_path.read_text()).get("lockbox_sha256") != lockbox_sha256:
        raise SystemExit(f"{scores_path} scored another lockbox file than {arguments.lockbox}")
    if arguments.models is None:
        arguments.models = chosen_models(arguments.head_choice, arguments.lockbox)
    label_selection = None if str(arguments.label_selection) in ("", "none") else arguments.label_selection

    record = json.loads(arguments.strata_record.read_text())
    sidecar = Path(f"{arguments.strata_record}.sha256")
    if sidecar.exists() and sidecar.read_text().split()[0] != file_sha256(arguments.strata_record):
        raise SystemExit(f"{arguments.strata_record} is not the file {sidecar} hashed")
    if file_sha256(arguments.strata_cells) != record["cells_sha256"]:
        raise SystemExit(f"{arguments.strata_cells} is not the cells file {arguments.strata_record} hashed")
    hashes = input_hashes(arguments.graph_dir, arguments.evidence_dir, label_selection, arguments.search_table)
    differing = sorted(key for key, value in hashes.items() if record.get(key) != value)
    if differing:
        raise SystemExit(f"the strata were written on other files than those scored now: {differing}")
    data = load_experiment_data(arguments.graph_dir, arguments.evidence_dir, group_by=arguments.group_by, label_selection=label_selection)
    recomputed, _ = assign_strata_and_eras(read_cell_search_table(arguments.search_table), scored_cells_from_experiment_data(data, MINIMUM_POSITIVES_TO_SCORE))
    committed = read_cells(arguments.strata_cells)
    moved = same_assignment(recomputed, committed)
    if moved:
        raise SystemExit(f"the committed strata differ from those the search table and the data give, in {moved}: the cuts are not moved after the draw")
    cell_labels = cell_label_arrays(committed, data.perturbation_ids, data.symptoms)

    in_lockbox = read_lockbox(arguments.lockbox, data, arguments.group_by, arguments.evidence_dir)
    rows = np.flatnonzero(in_lockbox)
    lockbox_ids = [data.perturbation_ids[i] for i in rows]
    selection_sha256 = file_sha256(label_selection) if label_selection else None
    label_mask = data.label_mask if data.label_mask is not None else np.ones_like(data.outcomes, dtype=bool)

    baseline_predictions = {name: {} for name in arguments.baselines}
    for seed in arguments.seeds:
        directory = arguments.baseline_root / f"seed{seed}"
        if json.loads((directory / "perturbation_ids.json").read_text()) != data.perturbation_ids:
            raise SystemExit(f"{directory} holds other perturbations")
        baseline_lockbox = (json.loads((directory / "results.json").read_text()).get("lockbox") or {}).get("path")
        if baseline_lockbox is None or Path(baseline_lockbox) != arguments.lockbox:
            raise SystemExit(f"{directory} scored lockbox {baseline_lockbox}, not {arguments.lockbox}")
        for name in arguments.baselines:
            baseline_predictions[name][seed] = np.load(directory / f"predictions_lockbox_{name}.npy")[rows]

    graph_and_evidence_hashes = {"graph_files_sha256": hashes["graph_files_sha256"], "evidence_records_sha256": hashes["evidence_records_sha256"]}
    model_predictions, refused = {}, []
    for model in arguments.models:
        configuration_arguments = expected_run_arguments(model, 0, arguments.group_by, arguments.lockbox)
        run_hashes = {**graph_and_evidence_hashes,
                      "node_descriptors_sha256": file_sha256(configuration_arguments["node_descriptors"]) if configuration_arguments.get("node_descriptors") else None,
                      "cell_class_weights_sha256": file_sha256(configuration_arguments["cell_class_weights"]) if configuration_arguments.get("cell_class_weights") else None}
        model_predictions[model] = {}
        for seed in arguments.seeds:
            split_directory = arguments.run_root / f"{model}_{arguments.group_by}_confirmatory" / f"lockbox_seed{seed}"
            predictions, reason = read_model_run(split_directory, lockbox_ids, lockbox_sha256, selection_sha256, "real",
                                                 require_refit=not arguments.allow_runs_without_refit, symptoms=data.symptoms,
                                                 expected_arguments=expected_run_arguments(model, seed, arguments.group_by, arguments.lockbox),
                                                 input_hashes=run_hashes)
            if predictions is None:
                refused.append(f"{split_directory}: {reason}")
            else:
                model_predictions[model][seed] = predictions
    if refused:
        raise SystemExit("not scored: runs missing or refused:\n" + "\n".join(refused))

    result = descriptive_readings(data.outcomes, label_mask, in_lockbox, data.perturbation_types, data.group_ids, data.symptoms, cell_labels,
                                  model_predictions, baseline_predictions, arguments.seeds, arguments.num_bootstrap, arguments.bootstrap_seed,
                                  MINIMUM_POSITIVES_TO_SCORE, bool(record["pooled_research_stratum"]["defined"]))
    output = {"scored_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "lockbox": str(arguments.lockbox), "lockbox_sha256": lockbox_sha256,
              "strata_record": str(arguments.strata_record), "strata_record_sha256": file_sha256(arguments.strata_record),
              "models": arguments.models, "baselines": arguments.baselines, "seeds": arguments.seeds, "num_bootstrap": arguments.num_bootstrap,
              "bootstrap_unit": "group", "minimum_positives_to_score": MINIMUM_POSITIVES_TO_SCORE, "scopes": result}
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(output, indent=1) + "\n")
    header = ["# Item 38 (d) and (g): descriptive readings by research stratum and era (generated by experiments/score_research_strata_and_eras.py)", "",
              f"Descriptive: in neither H1, H2 nor P1, no alpha spent, no interval compared with a level. Held-out set {arguments.lockbox} "
              f"(SHA-256 {lockbox_sha256[:12]}); strata {arguments.strata_record} (SHA-256 {output['strata_record_sha256'][:12]}); seeds {arguments.seeds}; "
              f"{arguments.num_bootstrap} paired bootstrap resamples over leakage groups. Each cell: the best baseline of the stratum (highest seed-mean "
              "score there, chosen without reference to any model) and the seed-mean model minus it, with the 2.5 and 97.5 percentiles of its bootstrap "
              "distribution. AUPRC values are not compared between strata or eras."]
    arguments.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    arguments.markdown_output.write_text("\n".join(markdown_lines(result, arguments.models, header)) + "\n")
    print(arguments.markdown_output.read_text())


if __name__ == "__main__":
    main()
