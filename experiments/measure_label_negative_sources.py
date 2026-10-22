"""Measure the three label-negative sources of decision 9.92 against an evidence table and its registered label selection,
and write the generated record docs/label_negative_sources_measured.md.

  1. Phenopacket Store (experiments/build_phenopacket_counts.py output): observed and excluded statements on the symptom
     set, the pairs, the evidenced negatives of use (a) under each exclusion rule, the contradictions with current
     positives, and the positive gene pairs that gain k of n under use (b).
  2. ClinicalTrials.gov trial arms, rebuilt from the fetcher's per-drug cache with this branch's code, which reads each
     term's assessment type: the absence reports before and after the systematic-assessment filter, and decision 9.48's
     development-label check (absences that are label positives) split by assessment type. Only the cache is read; this
     script sends no request (the site's robots file disallows /api/ for every reader; see decision 9.92).
  3. The curated statin-placebo negatives (configs/statin_trial_negatives.csv): which statins are in the table, and
     whether a pair contradicts a current positive.

Usage:
  python experiments/measure_label_negative_sources.py --evidence-dir data/processed/evidence_full_v5 \
      --label-selection data/processed/label_selection/better_v2_full_v5.parquet \
      --phenopacket-dir data/processed/phenopacket_store_v5 --trial-cache-dir data/raw/clinicaltrials \
      --crosswalk docs/symptom_crosswalk_fine.csv
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from experiments.build_label_selection import (
    boolean_column,
    phenopacket_negative_rows,
    positive_pairs_of_any_grade,
    read_statin_trial_negatives,
)
from mechanistic_pathway_learning.documentation import provenance_stamp
from mechanistic_pathway_learning.evidence.clinical_trial_adverse_events import (
    NON_SYSTEMATIC_ASSESSMENT,
    SYSTEMATIC_ASSESSMENT,
    build_comparisons,
    build_reports,
    perturbations_from_reports,
    read_lowest_level_to_preferred_term,
)
from mechanistic_pathway_learning.evidence.load_drug_label_events import read_preferred_term_to_target_symptom
from mechanistic_pathway_learning.evidence.phenopacket_store import (
    EXCLUSION_RULES,
    INDIVIDUALS_ASSESSED_COLUMN,
    INDIVIDUALS_OBSERVED_COLUMN,
    OBSERVED,
    pair_counts,
)

GENERATOR = "experiments/measure_label_negative_sources.py"


def kept_positive_pairs(selection_path: Path | None) -> set[tuple[str, str]]:
    if selection_path is None or not Path(selection_path).exists():
        return set()
    selection = pd.read_parquet(selection_path)
    kept = selection[selection.keep.astype(bool) & ~boolean_column(selection, "masks_a_negative")]
    return set(zip(kept.perturbation_id, kept.symptom))


def measure_phenopackets(directory: Path, records: pd.DataFrame, kept: set[tuple[str, str]]) -> dict:
    statuses = pd.read_parquet(directory / "phenopacket_individual_status.parquet")
    summary = json.loads((directory / "phenopacket_summary.json").read_text())
    key = summary["key"]
    any_grade = positive_pairs_of_any_grade(records)
    claims = records[(records.relation == "induces") & records.grade.isin(["A", "B"])]
    if "positive_report_count" in claims.columns:
        claims = claims[claims.positive_report_count > 0]
    label_positive = set(zip(claims.perturbation_id, claims.symptom))
    loaded_perturbations = set(claims.perturbation_id)  # the loader's perturbation set under the default label grades
    result = {"release": summary["release"], "key": key, "crosswalk": summary["crosswalk"], "phenopackets": summary["phenopackets"],
              "individuals_on_graph_genes": summary["individuals_on_graph_genes"], "left_out_gene_not_in_graph": summary["left_out_gene_not_in_graph"],
              "left_out_structural_variant_without_gene": summary["left_out_structural_variant_without_gene"],
              "statements_by_status": statuses.status.value_counts().to_dict(),
              "observed_statements": int((statuses.status == OBSERVED).sum()),
              "individuals_with_a_statement": int(statuses.phenopacket_id.nunique()), "rules": {}}
    for rule, counted in EXCLUSION_RULES.items():
        counts = pair_counts(statuses, key, rule)
        negatives = phenopacket_negative_rows(counts, records)
        absent_only = counts[(counts[INDIVIDUALS_OBSERVED_COLUMN] == 0) & (counts[INDIVIDUALS_ASSESSED_COLUMN] > 0)]
        contradicted_any = [pair for pair in zip(absent_only.perturbation_id, absent_only.symptom) if pair in any_grade]
        contradicted_label = [pair for pair in contradicted_any if pair in label_positive]
        contradicted_kept = [pair for pair in contradicted_any if pair in kept]
        is_label_positive = pd.Series([pair in label_positive for pair in zip(counts.perturbation_id, counts.symptom)], index=counts.index, dtype=bool)
        covered_positives = counts[is_label_positive & (counts[INDIVIDUALS_ASSESSED_COLUMN] > 0)]
        with_some_absent = covered_positives[covered_positives[INDIVIDUALS_ASSESSED_COLUMN] > covered_positives[INDIVIDUALS_OBSERVED_COLUMN]]
        result["rules"][rule] = {
            "excluded_statements_counted": int(statuses.status.isin(counted).sum()),
            "pairs_with_an_assessed_individual": int((counts[INDIVIDUALS_ASSESSED_COLUMN] > 0).sum()),
            "pairs_with_observed_and_absent": int(((counts[INDIVIDUALS_OBSERVED_COLUMN] > 0) & (counts[INDIVIDUALS_ASSESSED_COLUMN] > counts[INDIVIDUALS_OBSERVED_COLUMN])).sum()),
            "pairs_with_absent_only": len(absent_only),
            "absent_only_with_a_carved_out_observation": int((absent_only.individuals_observed_in_carved_out_descendant > 0).sum()),
            "absent_only_contradicting_a_positive_of_any_grade": [f"{p} {s}" for p, s in contradicted_any],
            "absent_only_contradicting_a_label_positive": [f"{p} {s}" for p, s in contradicted_label],
            "absent_only_contradicting_a_kept_positive": [f"{p} {s}" for p, s in contradicted_kept],
            "evidenced_negatives": len(negatives),
            "evidenced_negatives_with_five_or_more_assessed": int((negatives[INDIVIDUALS_ASSESSED_COLUMN] >= 5).sum()),
            "evidenced_negatives_the_loader_places": int(negatives.perturbation_id.isin(loaded_perturbations).sum()),
            "evidenced_negatives_by_symptom": negatives.groupby("symptom").size().to_dict(),
            "evidenced_negative_pairs": [f"{row.perturbation_id} {row.symptom} (0 of {int(getattr(row, INDIVIDUALS_ASSESSED_COLUMN))})" for row in negatives.itertuples(index=False)],
            "label_positive_pairs_given_k_of_n": len(covered_positives),
            "label_positive_pairs_with_an_assessed_absent_individual": len(with_some_absent),
            "label_positive_pairs_given_k_of_n_by_symptom": covered_positives.groupby("symptom").size().to_dict(),
        }
    return result


def read_cached_studies(cache_directory: Path, label: str) -> list[dict] | None:
    path = cache_directory / f"{label.replace('/', '_')}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))["studies"]


def measure_trial_arms(cache_directory: Path, evidence_directory: Path, crosswalk: Path, sider_directory: Path, kept: set[tuple[str, str]],
                       lockbox_perturbations: set[str]) -> dict:
    perturbations = perturbations_from_reports(evidence_directory / "evidence_reports.parquet")
    terms = read_preferred_term_to_target_symptom(crosswalk)
    lowest = read_lowest_level_to_preferred_term(sider_directory)
    assessment_of_terms: Counter = Counter()
    default_rows, filtered_rows, comparisons, missing = [], [], [], []
    for label in sorted(perturbations):
        studies = read_cached_studies(cache_directory, label)
        if studies is None:
            missing.append(label)
            continue
        others = set(perturbations) - {label}
        for study in studies:
            module = study.get("resultsSection", {}).get("adverseEventsModule", {})
            for key in ("otherEvents", "seriousEvents"):
                for event in module.get(key, []) or []:
                    assessment_of_terms[str(event.get("assessmentType") or "unstated")] += 1
        rows, _ = build_reports(studies, label, perturbations[label], terms, lowest, other_study_drugs=others)
        default_rows += rows
        rows, _ = build_reports(studies, label, perturbations[label], terms, lowest, other_study_drugs=others, absence_requires_systematic_assessment=True)
        filtered_rows += rows
        comparisons += build_comparisons(studies, label, perturbations[label], terms, lowest, other_study_drugs=others)
    reports, filtered = pd.DataFrame(default_rows), pd.DataFrame(filtered_rows)
    result = {"drugs": len(perturbations), "drugs_without_a_cache_file": missing, "event_terms_by_assessment_type": dict(assessment_of_terms)}
    if reports.empty:
        return result
    absences, filtered_absences = reports[reports.report_value == 0], filtered[filtered.report_value == 0]
    result.update({
        "positive_reports": int((reports.report_value == 1).sum()), "absence_reports_before_filter": len(absences), "absence_reports_after_filter": len(filtered_absences),
        "absence_reports_by_assessment_type": absences.assessment_type.replace("", "unstated").value_counts().to_dict(),
        "absence_reports_with_a_systematically_assessed_symptom": int(absences.symptom_systematically_assessed.sum()),
        "absence_reports_by_symptom_before": absences.groupby("symptom").size().to_dict(),
        "absence_reports_by_symptom_after": filtered_absences.groupby("symptom").size().to_dict(),
        "positive_reports_by_assessment_type": reports[reports.report_value == 1].assessment_type.replace("", "unstated").value_counts().to_dict(),
    })
    # decision 9.48's development-label check: drug pairs outside the lockboxes; a pair is an absence when its reports
    # hold an absence and no excess (the rule's verdict); its label status is a kept pair of the registered selection
    development = reports[~reports.perturbation_id.isin(lockbox_perturbations)]
    pairs = development.groupby(["perturbation_id", "symptom"])
    verdicts = pairs.report_value.agg(["min", "max"]).reset_index()
    systematic = pairs.symptom_systematically_assessed.any().reset_index(name="systematic")
    verdicts = verdicts.merge(systematic, on=["perturbation_id", "symptom"])
    verdicts["label_positive"] = [pair in kept for pair in zip(verdicts.perturbation_id, verdicts.symptom)]
    absent = verdicts[verdicts["max"] == 0]

    def share(frame: pd.DataFrame) -> dict:
        return {"pairs": len(frame), "label_positive": int(frame.label_positive.sum()),
                "percent": round(100.0 * frame.label_positive.mean(), 1) if len(frame) else None}

    all_comparison_pairs = pd.DataFrame(comparisons)
    if not all_comparison_pairs.empty:
        all_comparison_pairs = all_comparison_pairs[~all_comparison_pairs.perturbation_id.isin(lockbox_perturbations)].drop_duplicates(["perturbation_id", "symptom"])
        all_comparison_pairs["label_positive"] = [pair in kept for pair in zip(all_comparison_pairs.perturbation_id, all_comparison_pairs.symptom)]
    result["development_label_check"] = {
        "all_trial_pairs": share(all_comparison_pairs) if not all_comparison_pairs.empty else None,
        "pairs_with_a_report": share(verdicts),
        "absence_pairs": share(absent),
        "absence_pairs_systematically_assessed": share(absent[absent.systematic]),
        "absence_pairs_not_systematically_assessed": share(absent[~absent.systematic]),
    }
    return result


def measure_statins(table_path: Path, records: pd.DataFrame, kept: set[tuple[str, str]]) -> dict:
    table, _ = read_statin_trial_negatives(table_path, admit_class_extrapolation=True)
    perturbations = set(records.perturbation_id)
    any_grade = positive_pairs_of_any_grade(records)
    rows = []
    for row in table.itertuples(index=False):
        pair = (row.perturbation_id, row.symptom)
        rows.append({"drug": row.drug, "symptom": row.symptom, "in_the_trials": str(row.in_the_trials).lower() == "true",
                     "drug_in_the_table": row.perturbation_id in perturbations, "positive_of_any_grade": pair in any_grade, "kept_positive": pair in kept})
    frame = pd.DataFrame(rows)
    in_table = frame[frame.drug_in_the_table]
    return {"pairs_in_table": len(frame), "statins_in_table": sorted(frame.drug.unique()),
            "statins_used_by_the_trials": sorted(frame[frame.in_the_trials].drug.unique()),
            "statins_in_the_evidence_table": sorted(in_table.drug.unique()),
            "pairs_whose_statin_is_in_the_evidence_table": len(in_table),
            "of_them_contradicting_a_positive_of_any_grade": [f"{row.drug} {row.symptom}" for row in in_table[in_table.positive_of_any_grade].itertuples()],
            "of_them_contradicting_a_kept_positive": [f"{row.drug} {row.symptom}" for row in in_table[in_table.kept_positive].itertuples()],
            "evidenced_negatives_entering_this_table_without_extrapolation": int(in_table.in_the_trials.sum()),
            "evidenced_negatives_entering_this_table_with_extrapolation": len(in_table)}


def markdown(result: dict, inputs: list[str]) -> str:
    lines = ["# Label-negative sources measured (generated by experiments/measure_label_negative_sources.py — do not edit by hand)", "",
             provenance_stamp(GENERATOR, inputs), "",
             "Decision 9.92. Every number below is read from the inputs in the stamp; the rules behind them are in "
             "`mechanistic_pathway_learning/evidence/phenopacket_store.py`, `mechanistic_pathway_learning/evidence/clinical_trial_adverse_events.py` "
             "and `experiments/build_label_selection.py`. Nothing here is registered: each source enters a label selection only under its own flag.", ""]
    phenopackets = result.get("phenopackets")
    if phenopackets:
        lines += ["## 1. Phenopacket Store", "",
                  f"Release {phenopackets['release']}, keyed by {phenopackets['key']}, crosswalk `{phenopackets['crosswalk']}`: "
                  f"{phenopackets['phenopackets']:,} phenopackets, {phenopackets['individuals_on_graph_genes']:,} on graph genes "
                  f"({phenopackets['left_out_gene_not_in_graph']:,} on genes outside the graph, {phenopackets['left_out_structural_variant_without_gene']} structural "
                  f"variants without a gene), {phenopackets['individuals_with_a_statement']:,} with a statement on the symptom set; "
                  f"{phenopackets['observed_statements']:,} observed statements.", "",
                  "| status | individual-construct statements |", "| --- | --- |"]
        lines += [f"| {status} | {count:,} |" for status, count in phenopackets["statements_by_status"].items()]
        lines += ["", "| exclusion rule | excluded statements counted | assessed pairs | observed and absent | absent only | of them with a carved-out observation | "
                  "contradicting a positive (any grade) | evidenced negatives | with n of 5 or more | placed by the loader | label positives given k of n |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for rule, row in phenopackets["rules"].items():
            lines.append(f"| {rule} | {row['excluded_statements_counted']:,} | {row['pairs_with_an_assessed_individual']} | {row['pairs_with_observed_and_absent']} | "
                         f"{row['pairs_with_absent_only']} | {row['absent_only_with_a_carved_out_observation']} | {len(row['absent_only_contradicting_a_positive_of_any_grade'])} | "
                         f"{row['evidenced_negatives']} | {row['evidenced_negatives_with_five_or_more_assessed']} | {row['evidenced_negatives_the_loader_places']} | "
                         f"{row['label_positive_pairs_given_k_of_n']} |")
        for rule, row in phenopackets["rules"].items():
            lines += ["", f"Under `{rule}`: evidenced negatives by symptom {json.dumps(row['evidenced_negatives_by_symptom'])}; "
                          f"label positives given k of n by symptom {json.dumps(row['label_positive_pairs_given_k_of_n_by_symptom'])}; "
                          f"absent-only pairs that contradict a positive: {', '.join(row['absent_only_contradicting_a_positive_of_any_grade']) or 'none'}."]
            if row["evidenced_negative_pairs"]:
                lines += ["", "Pairs: " + "; ".join(row["evidenced_negative_pairs"]) + "."]
        lines.append("")
    trials = result.get("trial_arms")
    if not trials:
        lines += ["## 2. ClinicalTrials.gov trial arms by assessment type", "",
                  "Not measured in this run: no trial cache was given (`--trial-cache-dir`, the fetcher's per-drug cache; this script sends no request).", ""]
    else:
        lines += ["## 2. ClinicalTrials.gov trial arms by assessment type", ""]
        if "absence_reports_before_filter" not in trials:
            lines += [f"No cached study was found for any of the {trials['drugs']} drugs; nothing is measured.", ""]
        else:
            check = trials["development_label_check"]
            lines += [f"{trials['drugs']} drugs; {len(trials['drugs_without_a_cache_file'])} without a cache file. Event terms by assessment type: "
                      f"{json.dumps(trials['event_terms_by_assessment_type'])}. Absence reports: **{trials['absence_reports_before_filter']:,} before** the "
                      f"systematic-assessment filter and **{trials['absence_reports_after_filter']:,} after** it; by the term's own type "
                      f"{json.dumps(trials['absence_reports_by_assessment_type'])}. Positive reports {trials['positive_reports']:,}, by type "
                      f"{json.dumps(trials['positive_reports_by_assessment_type'])}.", "",
                      "| symptom | absences before | after |", "| --- | --- | --- |"]
            for symptom, before in sorted(trials["absence_reports_by_symptom_before"].items()):
                lines.append(f"| {symptom} | {before} | {trials['absence_reports_by_symptom_after'].get(symptom, 0)} |")
            lines += ["", "Decision 9.48's development-label check (drugs outside both lockboxes; a label positive is a kept pair of the registered selection):", "",
                      "| pairs | number | label positives | percent |", "| --- | --- | --- | --- |"]
            for name, value in check.items():
                if value:
                    lines.append(f"| {name.replace('_', ' ')} | {value['pairs']} | {value['label_positive']} | {value['percent']} |")
            lines.append("")
    statins = result.get("statins")
    if statins:
        lines += ["## 3. Statin-placebo meta-analysis negatives", "",
                  f"{statins['pairs_in_table']} curated pairs over {', '.join(statins['statins_in_table'])}; the trials used "
                  f"{', '.join(statins['statins_used_by_the_trials'])} (and fluvastatin, which the drug set does not hold). Statins in this evidence table: "
                  f"{', '.join(statins['statins_in_the_evidence_table']) or 'none'}. Pairs that would enter it: {statins['evidenced_negatives_entering_this_table_without_extrapolation']} "
                  f"without class extrapolation, {statins['evidenced_negatives_entering_this_table_with_extrapolation']} with it. Contradicting a positive of any grade: "
                  f"{', '.join(statins['of_them_contradicting_a_positive_of_any_grade']) or 'none'}; a kept positive: {', '.join(statins['of_them_contradicting_a_kept_positive']) or 'none'}.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--label-selection", type=Path, default=None, help="the registered selection whose kept pairs are the label positives")
    parser.add_argument("--phenopacket-dir", type=Path, default=None)
    parser.add_argument("--statin-trial-negatives", type=Path, default=Path("configs/statin_trial_negatives.csv"))
    parser.add_argument("--trial-cache-dir", type=Path, default=None, help="the fetcher's per-drug cache; read only, no request is sent")
    parser.add_argument("--crosswalk", type=Path, default=Path("docs/symptom_crosswalk_fine.csv"))
    parser.add_argument("--sider-dir", type=Path, default=Path("data/raw/sider_4.1"))
    parser.add_argument("--lockbox", type=Path, nargs="*", default=[Path("configs/lockbox_v1.json"), Path("configs/lockbox_v2.json")])
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--markdown-output", type=Path, default=Path("docs/label_negative_sources_measured.md"))
    arguments = parser.parse_args()
    records = pd.read_parquet(arguments.evidence_dir / "evidence_records.parquet")
    kept = kept_positive_pairs(arguments.label_selection)
    lockbox_perturbations = set().union(*(json.loads(Path(path).read_text())["perturbation_ids"] for path in arguments.lockbox)) if arguments.lockbox else set()
    result: dict = {"evidence_dir": str(arguments.evidence_dir), "label_selection": str(arguments.label_selection), "kept_positive_pairs": len(kept)}
    inputs = [str(arguments.evidence_dir), str(arguments.label_selection), str(arguments.statin_trial_negatives)]
    if arguments.phenopacket_dir is not None:
        result["phenopackets"] = measure_phenopackets(arguments.phenopacket_dir, records, kept)
        inputs.append(str(arguments.phenopacket_dir))
    if arguments.trial_cache_dir is not None:
        result["trial_arms"] = measure_trial_arms(arguments.trial_cache_dir, arguments.evidence_dir, arguments.crosswalk, arguments.sider_dir, kept, lockbox_perturbations)
        inputs.append(f"{arguments.trial_cache_dir} (cache only)")
    result["statins"] = measure_statins(arguments.statin_trial_negatives, records, kept)
    if arguments.output_json is not None:
        arguments.output_json.parent.mkdir(parents=True, exist_ok=True)
        arguments.output_json.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    arguments.markdown_output.write_text(markdown(result, inputs) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "phenopackets"}, indent=1))


if __name__ == "__main__":
    main()
