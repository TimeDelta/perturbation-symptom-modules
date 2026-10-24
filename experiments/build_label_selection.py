"""Write the "better (not more)" label selection: which positive pairs train and score, and which are set aside.

The rule was fixed on 7 October 2026, before any full-graph model was scored, from evidence properties only (never
from a model's predictions), and is recorded in docs/preregistration.md:

  - gene pairs (grade A, HPO): kept when the frequency is at least 0.30, the lower bound of the HPO qualifier
    "frequent" (30 to 79 percent), so "frequent", "very frequent", "obligate" and counted frequencies of 30 percent or
    more are kept; "occasional", "very rare", counted frequencies below 30 percent and pairs with no frequency are set
    aside;
  - drug pairs (grade B, SIDER and OnSIDES labels): kept when the label frequency is at least 1 percent (the CIOMS
    "common" band) or when both SIDER and OnSIDES list the pair (two independent label extractions); the rest,
    mostly label statements with no frequency, are set aside.

A pair set aside is masked, not relabelled: it stays a positive in the outcome matrix and load_experiment_data's
label_mask removes it from the loss and from every metric, so it is neither a positive nor a negative. A
perturbation whose every positive is set aside still contributes its unlabelled pairs, as any perturbation does.

--mask-grades C (better_v2, the user's decision of 8 October 2026) also masks the pairs whose only evidence is of those
grades (grade C: a human association, not a label). Without it such a pair is a negative in scoring and a weak
negative in training. Each gets a row with keep False and masks_a_negative True, which load_experiment_data reads as
"neither positive nor negative"; a pair that also has grade A or B evidence is a positive and gets no such row.

--mask-never-above-placebo (the user's decision of 10 October 2026, docs/label_source_review.md section 5) sets aside a
drug pair the rule above would keep when SIDER gives a drug arm and a placebo arm for it in the same label and in no
such label is the event more frequent on the drug (mechanistic_pathway_learning/evidence/placebo_arm_comparison.py). The
pair is masked like any other pair set aside. A pair with no placebo arm in SIDER is not judged, and OnSIDES gives no
frequencies, so a drug known to OnSIDES alone is never judged.

--never-above-placebo-as-negative (an option built on 11 October 2026 after the user asked "Why would working no better
than the placebo not be counted as evidence against a label?") judges the same pairs and relabels them: the row gets
keep False and counts_as_negative True, and load_experiment_data turns the pair into a negative, with the weight of any
other negative in training and counted as a negative in scoring. The reasoning: an unlabelled pair is already treated
as a negative on no evidence at all, so a pair with a controlled comparison that shows no excess should not count for
less. Its limits: SIDER gives no arm sizes, so "not above placebo" is read from percentages alone, and several of the
pairs are the symptom of the condition the drug treats. The two flags exclude each other.

Evidenced negatives from individually assessed human perturbations and from placebo-controlled trials (decision 9.92,
22 October 2026; the owner: negatives are "as important as positives here for fitting the priors to the truth"). Each
is off by default, so a selection written without these flags is the one the rule above writes; switching one on is
the owner's call. They differ in kind from the absences of decision 9.48, which stay soft classes:

--phenopacket-counts PATH (experiments/build_phenopacket_counts.py, keyed as the evidence table keys genes) writes k
observed and n assessed (phenopacket_individuals_observed, phenopacket_individuals_assessed) beside every gene pair
it covers. With --phenopacket-exclusions-as-negative, a pair with assessed individuals, none observed, none observed in
a carved-out descendant of the construct, and no positive record of any grade in the evidence table gets a row with
counts_as_negative True and evidenced_negative_source "Phenopacket-Store", which the loader reads as an evidenced
negative on an otherwise unlabelled pair (mechanistic_pathway_learning/evidence/phenopacket_store.py states when an
exclusion counts). With --phenopacket-frequency, a gene pair HPO gives no frequency takes k/n as its frequency and
goes through the 0.30 rule, as HPO's own counted frequencies do.

--statin-trial-negatives-as-negative reads the curated table (--statin-trial-negatives, configs/
statin_trial_negatives.csv: the Cholesterol Treatment Trialists' meta-analysis of 19 double-blind statin-placebo
trials, Lancet 2026, PMID 41655587) and makes each of its (statin, symptom) pairs an evidenced negative: a positive is
relabelled as --never-above-placebo-as-negative relabels one, and an unlabelled pair gets a row as above. The trials
used six statins; a statin of the table that none of them used enters only with --admit-class-extrapolation.

Usage:
  python experiments/build_label_selection.py --evidence-dir data/processed/evidence_full \
      --output data/processed/label_selection/better_v1_full.parquet
  python experiments/build_label_selection.py --evidence-dir data/processed/evidence_full_v2 --mask-grades C \
      --output data/processed/label_selection/better_v2_full_v2.parquet
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.evaluation.experiment_data import DEFAULT_LABEL_GRADES
from mechanistic_pathway_learning.evidence.load_drug_label_events import load_sider_frequency_rows, read_preferred_term_to_target_symptom
from mechanistic_pathway_learning.evidence.phenopacket_store import INDIVIDUALS_ASSESSED_COLUMN, INDIVIDUALS_OBSERVED_COLUMN, clean_negative_pairs
from mechanistic_pathway_learning.evidence.placebo_arm_comparison import PlaceboArmComparison, compare_drug_arm_with_placebo_arm

GENE_MINIMUM_FREQUENCY = 0.30
DRUG_MINIMUM_FREQUENCY = 0.01
NEVER_ABOVE_PLACEBO_REASON = "drug pair never more frequent on the drug than on placebo"
COUNTED_AS_NEGATIVE = ", counted as a negative"
EVIDENCED_NEGATIVE_SOURCE_COLUMN = "evidenced_negative_source"
PHENOPACKET_SOURCE = "Phenopacket-Store"
STATIN_TRIALS_SOURCE = "CTT-statin-placebo-trials-2026"
DEFAULT_STATIN_TRIAL_NEGATIVES = Path("configs/statin_trial_negatives.csv")
# the per-pair columns the loader turns into matrices (evaluation/experiment_data.py), for the positive-unlabelled
# likelihood to read as a propensity (k of n) or a power (participants and interval)
PHENOPACKET_COUNT_COLUMNS = (INDIVIDUALS_OBSERVED_COLUMN, INDIVIDUALS_ASSESSED_COLUMN)
META_ANALYSIS_COLUMNS = ("meta_analysis_participants", "meta_analysis_rate_ratio", "meta_analysis_rate_ratio_lower_95", "meta_analysis_rate_ratio_upper_95")


def select_pairs(records: pd.DataFrame, placebo_arm_comparisons: Mapping[tuple[str, str], PlaceboArmComparison] | None = None,
                 never_above_placebo_as_negative: bool = False) -> pd.DataFrame:
    """One row per positive (perturbation_id, symptom) with keep and the reason.

    placebo_arm_comparisons, keyed by (perturbation_id, symptom), sets aside the drug pairs the frequency rule would
    keep whose comparison is never_above_placebo; None leaves the rule as it was registered. With
    never_above_placebo_as_negative those pairs get counts_as_negative True as well (and every other row False), which
    the loader reads as "a negative", where a pair set aside is neither a positive nor a negative."""
    positives = records[(records.relation == "induces") & records.grade.isin(DEFAULT_LABEL_GRADES)]
    if "positive_report_count" in positives.columns:
        positives = positives[positives.positive_report_count > 0]
    rows = []
    for (perturbation_id, symptom), group in positives.groupby(["perturbation_id", "symptom"], sort=True):
        perturbation_type = group.perturbation_type.iloc[0]
        counts_as_negative = False
        frequency = pd.to_numeric(group.label_frequency, errors="coerce").max()
        sources = ";".join(group.source.astype(str))
        if perturbation_type == "gene":
            if pd.isna(frequency):
                keep, reason = False, "gene pair with no frequency"
            elif frequency >= GENE_MINIMUM_FREQUENCY:
                keep, reason = True, f"gene pair, frequency {frequency:.2f} at least {GENE_MINIMUM_FREQUENCY}"
            else:
                keep, reason = False, f"gene pair, frequency {frequency:.2f} below {GENE_MINIMUM_FREQUENCY}"
        else:
            both_sources = "OnSIDES-label" in sources and "SIDER-label" in sources
            if not pd.isna(frequency) and frequency >= DRUG_MINIMUM_FREQUENCY:
                keep, reason = True, f"drug pair, frequency {frequency:.3f} at least {DRUG_MINIMUM_FREQUENCY}"
            elif both_sources:
                keep, reason = True, "drug pair listed by both SIDER and OnSIDES"
            elif pd.isna(frequency):
                keep, reason = False, "drug pair with no frequency, one label source"
            else:
                keep, reason = False, f"drug pair, frequency {frequency:.3f} below {DRUG_MINIMUM_FREQUENCY}, one label source"
            comparison = (placebo_arm_comparisons or {}).get((perturbation_id, symptom))
            if keep and comparison is not None and comparison.never_above_placebo:
                keep, counts_as_negative = False, never_above_placebo_as_negative
                reason = f"{NEVER_ABOVE_PLACEBO_REASON}{COUNTED_AS_NEGATIVE if counts_as_negative else ''} ({comparison.entries_with_both_arms} label entries with both arms)"
        rows.append({"perturbation_id": perturbation_id, "symptom": symptom, "perturbation_type": perturbation_type,
                     "label_frequency": frequency, "keep": keep, "reason": reason} | ({"counts_as_negative": counts_as_negative} if never_above_placebo_as_negative else {}))
    return pd.DataFrame(rows)


def masked_negative_pairs(records: pd.DataFrame, mask_grades: list[str]) -> pd.DataFrame:
    """One row (keep False, masks_a_negative True) per (perturbation_id, symptom) with evidence of mask_grades and none of
    the label grades, so that the pair is neither a positive nor a negative."""
    claims = records[records.relation == "induces"]
    if "positive_report_count" in claims.columns:
        claims = claims[claims.positive_report_count > 0]
    labelled = set(zip(*[claims[claims.grade.isin(DEFAULT_LABEL_GRADES)][column] for column in ("perturbation_id", "symptom")]))
    rows = []
    for (perturbation_id, symptom), group in claims[claims.grade.isin(mask_grades)].groupby(["perturbation_id", "symptom"], sort=True):
        if (perturbation_id, symptom) in labelled:
            continue
        rows.append({"perturbation_id": perturbation_id, "symptom": symptom, "perturbation_type": group.perturbation_type.iloc[0],
                     "label_frequency": float("nan"), "keep": False, "reason": f"grade {'/'.join(sorted(group.grade.unique()))} pair only, masked",
                     "masks_a_negative": True})
    return pd.DataFrame(rows, columns=["perturbation_id", "symptom", "perturbation_type", "label_frequency", "keep", "reason", "masks_a_negative"])


def boolean_column(selection: pd.DataFrame, column: str) -> pd.Series:
    """A flag column of a selection as booleans, False where a row of another kind carries none or the column is absent."""
    if column not in selection.columns:
        return pd.Series(False, index=selection.index)
    return selection[column].astype("boolean").fillna(False).astype(bool)


def positive_pairs_of_any_grade(records: pd.DataFrame) -> set[tuple[str, str]]:
    """Every (perturbation_id, symptom) with a positive claim of any grade: a pair an evidenced negative must not land on
    unless it says so (the curated trial negatives relabel label positives; Phenopacket exclusions never do)."""
    claims = records[records.relation == "induces"]
    if "positive_report_count" in claims.columns:
        claims = claims[claims.positive_report_count > 0]
    return set(zip(claims.perturbation_id, claims.symptom))


def with_phenopacket_counts(selection: pd.DataFrame, counts: pd.DataFrame) -> pd.DataFrame:
    """k and n beside each row the counts cover (NaN elsewhere); nothing else changes."""
    columns = ["perturbation_id", "symptom", *PHENOPACKET_COUNT_COLUMNS]
    merged = selection.drop(columns=[column for column in PHENOPACKET_COUNT_COLUMNS if column in selection.columns]).merge(
        counts[columns], on=["perturbation_id", "symptom"], how="left")
    for column in PHENOPACKET_COUNT_COLUMNS:
        merged[column] = merged[column].astype("float64")
    return merged


def apply_phenopacket_frequency(selection: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Use (b) of decision 9.92: a gene pair HPO gives no frequency takes k/n as its frequency and the registered 0.30
    rule decides it, as HPO's counted frequencies ("3/7") are decided. Pairs with an HPO frequency keep it."""
    selection = selection.copy()
    # a relabelled pair, or a grade-C-only pair the selection masks
    not_a_positive = boolean_column(selection, "counts_as_negative") | boolean_column(selection, "masks_a_negative")
    is_candidate = ((selection.perturbation_type == "gene") & selection.label_frequency.isna()
                    & (selection[INDIVIDUALS_ASSESSED_COLUMN].fillna(0) > 0) & ~not_a_positive)
    became_kept, stayed_set_aside = 0, 0
    for index in selection.index[is_candidate]:
        frequency = float(selection.at[index, INDIVIDUALS_OBSERVED_COLUMN]) / float(selection.at[index, INDIVIDUALS_ASSESSED_COLUMN])
        keep = frequency >= GENE_MINIMUM_FREQUENCY
        selection.at[index, "label_frequency"] = frequency
        selection.at[index, "keep"] = keep
        selection.at[index, "reason"] = (f"gene pair, Phenopacket Store frequency {int(selection.at[index, INDIVIDUALS_OBSERVED_COLUMN])} of "
                                         f"{int(selection.at[index, INDIVIDUALS_ASSESSED_COLUMN])} = {frequency:.2f} "
                                         f"{'at least' if keep else 'below'} {GENE_MINIMUM_FREQUENCY}")
        became_kept += keep
        stayed_set_aside += not keep
    return selection, {"gene_pairs_without_an_hpo_frequency_given_one": int(is_candidate.sum()), "of_them_kept": int(became_kept), "of_them_set_aside": int(stayed_set_aside)}


def phenopacket_negative_rows(counts: pd.DataFrame, records: pd.DataFrame) -> pd.DataFrame:
    """Use (a) of decision 9.92: one counts_as_negative row per clean pair (phenopacket_store.clean_negative_pairs)."""
    clean = clean_negative_pairs(counts, positive_pairs_of_any_grade(records))
    rows = [{"perturbation_id": row.perturbation_id, "symptom": row.symptom, "perturbation_type": "gene", "label_frequency": float("nan"), "keep": False,
             "reason": (f"Phenopacket Store: 0 of {int(getattr(row, INDIVIDUALS_ASSESSED_COLUMN))} assessed individuals observed "
                        f"({int(row.individuals_absent_root_exclusion)} with the construct's own term excluded), no positive record; counted as a negative"),
             "counts_as_negative": True, EVIDENCED_NEGATIVE_SOURCE_COLUMN: PHENOPACKET_SOURCE,
             INDIVIDUALS_OBSERVED_COLUMN: float(getattr(row, INDIVIDUALS_OBSERVED_COLUMN)), INDIVIDUALS_ASSESSED_COLUMN: float(getattr(row, INDIVIDUALS_ASSESSED_COLUMN))}
            for row in clean.itertuples(index=False)]
    return pd.DataFrame(rows, columns=["perturbation_id", "symptom", "perturbation_type", "label_frequency", "keep", "reason", "counts_as_negative",
                                       EVIDENCED_NEGATIVE_SOURCE_COLUMN, *PHENOPACKET_COUNT_COLUMNS])


def read_statin_trial_negatives(path: Path, admit_class_extrapolation: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(rows entered, rows left out because the trials did not use that statin and extrapolation is not admitted)."""
    table = pd.read_csv(path, dtype={"pmid": str})
    in_the_trials = table.in_the_trials.astype(str).str.lower() == "true"
    if admit_class_extrapolation:
        return table.reset_index(drop=True), table.iloc[0:0]
    return table[in_the_trials].reset_index(drop=True), table[~in_the_trials].reset_index(drop=True)


def apply_statin_trial_negatives(selection: pd.DataFrame, table: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Each (statin, symptom) of table becomes an evidenced negative: its positive row, when there is one, is relabelled
    (keep False, counts_as_negative True); a masked grade-C-only row gives way to it; otherwise a row is added."""
    selection = selection.copy()
    if "counts_as_negative" not in selection.columns:
        selection["counts_as_negative"] = False
    for column in META_ANALYSIS_COLUMNS:
        if column not in selection.columns:
            selection[column] = float("nan")
    if EVIDENCED_NEGATIVE_SOURCE_COLUMN not in selection.columns:
        selection[EVIDENCED_NEGATIVE_SOURCE_COLUMN] = ""
    masks = boolean_column(selection, "masks_a_negative")
    relabelled, replaced_a_mask, added, contradicted = [], [], [], []
    new_rows = []
    for row in table.itertuples(index=False):
        values = {"meta_analysis_participants": float(row.participants), "meta_analysis_rate_ratio": float(row.rate_ratio),
                  "meta_analysis_rate_ratio_lower_95": float(row.rate_ratio_lower_95), "meta_analysis_rate_ratio_upper_95": float(row.rate_ratio_upper_95)}
        reason = (f"{row.drug}: statin against placebo, {row.trials} double-blind trials, {row.participants:,} participants, {row.outcome} RR {row.rate_ratio:.2f} "
                  f"({row.rate_ratio_lower_95:.2f} to {row.rate_ratio_upper_95:.2f}), PMID {row.pmid}"
                  + ("" if str(row.in_the_trials).lower() == "true" else ", applied by class extrapolation") + "; counted as a negative")
        matches = selection.index[(selection.perturbation_id == row.perturbation_id) & (selection.symptom == row.symptom)]
        positive = [index for index in matches if not masks[index]]
        if positive:
            index = positive[0]
            contradicted.append(f"{row.drug} {row.symptom} ({selection.at[index, 'reason']})")
            selection.loc[index, ["keep", "counts_as_negative", "reason", EVIDENCED_NEGATIVE_SOURCE_COLUMN]] = [False, True, reason, STATIN_TRIALS_SOURCE]
            for column, value in values.items():
                selection.at[index, column] = value
            relabelled.append(f"{row.drug} {row.symptom}")
            continue
        if len(matches):
            replaced_a_mask.append(f"{row.drug} {row.symptom}")
            selection = selection.drop(index=matches)
        added.append(f"{row.drug} {row.symptom}")
        new_rows.append({"perturbation_id": row.perturbation_id, "symptom": row.symptom, "perturbation_type": "drug", "label_frequency": float("nan"),
                         "keep": False, "reason": reason, "counts_as_negative": True, EVIDENCED_NEGATIVE_SOURCE_COLUMN: STATIN_TRIALS_SOURCE, **values})
    if new_rows:
        selection = pd.concat([selection, pd.DataFrame(new_rows)], ignore_index=True)
    return selection.reset_index(drop=True), {"pairs_in_table": len(table), "label_positives_relabelled": relabelled, "grade_c_masks_replaced": replaced_a_mask,
                                              "rows_added_for_unlabelled_pairs": added, "contradicted_positives_with_their_reason": contradicted}


def with_evidenced_negative_sources(selection: pd.DataFrame, records: pd.DataFrame, arguments: argparse.Namespace) -> tuple[pd.DataFrame, dict]:
    """The decision 9.92 sources applied to a selection under their flags; (the selection unchanged, {}) under none."""
    if arguments.phenopacket_counts is None and not arguments.statin_trial_negatives_as_negative:
        return selection, {}
    summary: dict = {}
    if arguments.phenopacket_counts is not None:
        counts = pd.read_parquet(arguments.phenopacket_counts)
        gene_perturbations = set(records[records.perturbation_type == "gene"].perturbation_id)
        selection = with_phenopacket_counts(selection, counts)
        masked = boolean_column(selection, "masks_a_negative")
        positive_gene_pairs = selection[(selection.perturbation_type == "gene") & ~masked]
        covered = positive_gene_pairs[positive_gene_pairs[INDIVIDUALS_ASSESSED_COLUMN].fillna(0) > 0]
        summary["phenopacket"] = {
            "counts": str(arguments.phenopacket_counts), "counts_sha256": hashlib.sha256(Path(arguments.phenopacket_counts).read_bytes()).hexdigest(),
            "pairs_in_counts": len(counts), "pairs_with_an_assessed_individual": int((counts[INDIVIDUALS_ASSESSED_COLUMN] > 0).sum()),
            "count_perturbations_in_this_evidence_table": int(counts.perturbation_id.isin(gene_perturbations).sum()),
            "positive_gene_pairs": len(positive_gene_pairs),
            "positive_gene_pairs_given_k_of_n": int(len(covered)),
            "positive_gene_pairs_given_k_of_n_by_symptom": covered.groupby("symptom").size().to_dict(),
        }
        if not summary["phenopacket"]["count_perturbations_in_this_evidence_table"]:
            raise SystemExit(f"no perturbation of {arguments.phenopacket_counts} is a gene perturbation of {arguments.evidence_dir}: keyed the other way (--key allele or gene)?")
        if arguments.phenopacket_frequency:
            selection, summary["phenopacket"]["frequency"] = apply_phenopacket_frequency(selection)
        if arguments.phenopacket_exclusions_as_negative:
            negatives = phenopacket_negative_rows(counts, records)
            positive_pairs = positive_pairs_of_any_grade(records)
            absent_only = counts[(counts[INDIVIDUALS_OBSERVED_COLUMN] == 0) & (counts[INDIVIDUALS_ASSESSED_COLUMN] > 0)]
            contradicted = absent_only[[pair in positive_pairs for pair in zip(absent_only.perturbation_id, absent_only.symptom)]]
            if "counts_as_negative" not in selection.columns:
                selection = selection.assign(counts_as_negative=False)
            if "masks_a_negative" in selection.columns:
                negatives = negatives.assign(masks_a_negative=False)
            selection = pd.concat([selection, negatives], ignore_index=True)
            summary["phenopacket"]["exclusions_as_negative"] = {
                "pairs_with_assessed_absent_only": len(absent_only),
                "of_them_with_a_carved_out_observation": int((absent_only.individuals_observed_in_carved_out_descendant > 0).sum()),
                "of_them_contradicting_a_positive_record": len(contradicted),
                "contradicted_pairs": [f"{row.perturbation_id} {row.symptom} (0 of {int(getattr(row, INDIVIDUALS_ASSESSED_COLUMN))})" for row in contradicted.itertuples(index=False)],
                "evidenced_negatives": len(negatives), "evidenced_negatives_by_symptom": negatives.groupby("symptom").size().to_dict(),
                "evidenced_negatives_with_five_or_more_assessed": int((negatives[INDIVIDUALS_ASSESSED_COLUMN] >= 5).sum()),
                "evidenced_negatives_whose_perturbation_is_in_this_table": int(negatives.perturbation_id.isin(gene_perturbations).sum()),
                "pairs": [f"{row.perturbation_id} {row.symptom} (0 of {int(getattr(row, INDIVIDUALS_ASSESSED_COLUMN))})" for row in negatives.itertuples(index=False)],
            }
    if arguments.statin_trial_negatives_as_negative:
        table, left_out = read_statin_trial_negatives(arguments.statin_trial_negatives, arguments.admit_class_extrapolation)
        perturbations = set(records.perturbation_id)
        selection, statin_summary = apply_statin_trial_negatives(selection, table)
        summary["statin_trials"] = {"table": str(arguments.statin_trial_negatives), "table_sha256": hashlib.sha256(Path(arguments.statin_trial_negatives).read_bytes()).hexdigest(),
                                    "admit_class_extrapolation": bool(arguments.admit_class_extrapolation),
                                    "pairs_left_out_as_extrapolation": [f"{row.drug} {row.symptom}" for row in left_out.itertuples(index=False)],
                                    "pairs_whose_drug_is_in_this_table": int(table.perturbation_id.isin(perturbations).sum()), **statin_summary}
    for column in ("counts_as_negative", "masks_a_negative"):  # rows of other kinds carry no value: False
        if column in selection.columns:
            selection[column] = boolean_column(selection, column)
    if EVIDENCED_NEGATIVE_SOURCE_COLUMN in selection.columns:
        selection[EVIDENCED_NEGATIVE_SOURCE_COLUMN] = selection[EVIDENCED_NEGATIVE_SOURCE_COLUMN].fillna("").astype(str)
    return selection, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--evidence-dir", type=Path, default=Path("data/processed/evidence_full"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/label_selection/better_v1_full.parquet"))
    parser.add_argument("--mask-grades", nargs="*", default=[], help="also mask the pairs whose only evidence is of these grades (C for better_v2)")
    parser.add_argument("--mask-never-above-placebo", action="store_true",
                        help="set aside the kept drug pairs that no SIDER label with both arms lists as more frequent on the drug than on placebo")
    parser.add_argument("--never-above-placebo-as-negative", action="store_true",
                        help="relabel those pairs as negatives in place of setting them aside (excludes --mask-never-above-placebo)")
    parser.add_argument("--sider-dir", type=Path, default=Path("data/raw/sider_4.1"), help="SIDER 4.1 tables, read under either placebo flag")
    parser.add_argument("--crosswalk", type=Path, default=Path("docs/symptom_crosswalk.csv"), help="preferred term to target symptom, read under either placebo flag")
    parser.add_argument("--phenopacket-counts", type=Path, default=None,
                        help="phenopacket_pair_counts.parquet (experiments/build_phenopacket_counts.py, keyed as this evidence table keys genes): k and n beside each pair it covers")
    parser.add_argument("--phenopacket-exclusions-as-negative", action="store_true",
                        help="decision 9.92 (a): a pair with assessed individuals, none observed and no positive record becomes an evidenced negative")
    parser.add_argument("--phenopacket-frequency", action="store_true",
                        help="decision 9.92 (b): a gene pair HPO gives no frequency takes k/n and the 0.30 rule decides it")
    parser.add_argument("--statin-trial-negatives-as-negative", action="store_true",
                        help="decision 9.92: the curated statin-placebo meta-analysis negatives become evidenced negatives")
    parser.add_argument("--statin-trial-negatives", type=Path, default=DEFAULT_STATIN_TRIAL_NEGATIVES)
    parser.add_argument("--admit-class-extrapolation", action="store_true",
                        help="also enter the statins of the table that none of the trials used (pitavastatin, cerivastatin)")
    arguments = parser.parse_args()
    if (arguments.phenopacket_exclusions_as_negative or arguments.phenopacket_frequency) and arguments.phenopacket_counts is None:
        raise SystemExit("--phenopacket-exclusions-as-negative and --phenopacket-frequency read --phenopacket-counts")
    if arguments.admit_class_extrapolation and not arguments.statin_trial_negatives_as_negative:
        raise SystemExit("--admit-class-extrapolation qualifies --statin-trial-negatives-as-negative")
    if arguments.mask_never_above_placebo and arguments.never_above_placebo_as_negative:
        raise SystemExit("--mask-never-above-placebo and --never-above-placebo-as-negative exclude each other: a pair is set aside or it is a negative")
    if set(arguments.mask_grades) & set(DEFAULT_LABEL_GRADES):
        raise SystemExit(f"--mask-grades {arguments.mask_grades} names a label grade")
    if arguments.output.exists():
        raise SystemExit(f"{arguments.output} exists; a selection is written once (jobs and the lockbox record its hash)")
    records = pd.read_parquet(arguments.evidence_dir / "evidence_records.parquet")
    placebo_arm_comparisons = None
    if arguments.mask_never_above_placebo or arguments.never_above_placebo_as_negative:
        placebo_arm_comparisons = compare_drug_arm_with_placebo_arm(load_sider_frequency_rows(arguments.sider_dir), read_preferred_term_to_target_symptom(arguments.crosswalk))
    positive_selection = select_pairs(records, placebo_arm_comparisons, arguments.never_above_placebo_as_negative)
    masked_negatives = masked_negative_pairs(records, arguments.mask_grades) if arguments.mask_grades else None
    if masked_negatives is not None and arguments.never_above_placebo_as_negative:
        masked_negatives = masked_negatives.assign(counts_as_negative=False)
    selection = positive_selection if masked_negatives is None else pd.concat([positive_selection.assign(masks_a_negative=False), masked_negatives], ignore_index=True)
    selection, evidenced_negative_summary = with_evidenced_negative_sources(selection, records, arguments)
    if evidenced_negative_summary:  # a positive relabelled or given a Phenopacket frequency is read from the selection as written
        positive_keys = set(zip(positive_selection.perturbation_id, positive_selection.symptom))
        positive_selection = selection[[pair in positive_keys for pair in zip(selection.perturbation_id, selection.symptom)]]
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    selection.to_parquet(arguments.output, index=False)
    kept = positive_selection[positive_selection.keep]
    summary = {
        "output": str(arguments.output), "evidence_dir": str(arguments.evidence_dir),
        "gene_minimum_frequency": GENE_MINIMUM_FREQUENCY, "drug_minimum_frequency": DRUG_MINIMUM_FREQUENCY,
        "positive_pairs": len(positive_selection), "kept_pairs": len(kept), "set_aside_pairs": int((~positive_selection.keep).sum()),
        "kept_by_type": kept.groupby("perturbation_type").size().to_dict(),
        "perturbations_with_a_kept_positive_by_type": kept.groupby("perturbation_type").perturbation_id.nunique().to_dict(),
        "kept_by_symptom": kept.groupby("symptom").size().to_dict(),
        "all_by_symptom": positive_selection.groupby("symptom").size().to_dict(),
        "set_aside_reasons": positive_selection[~positive_selection.keep].reason.str.replace(r"[0-9.]+ below", "x below", regex=True).value_counts().to_dict(),
    }
    if placebo_arm_comparisons is not None:  # recorded only when set, so a selection written without it has the summary it always had
        drug_pairs = positive_selection[positive_selection.perturbation_type == "drug"]
        judged = [placebo_arm_comparisons.get(pair) for pair in zip(drug_pairs.perturbation_id, drug_pairs.symptom)]
        set_aside_for_placebo = drug_pairs[drug_pairs.reason.str.startswith(NEVER_ABOVE_PLACEBO_REASON)]
        summary["never_above_placebo_as_negative" if arguments.never_above_placebo_as_negative else "mask_never_above_placebo"] = {
            "drug_pairs_with_a_label_entry_giving_both_arms": sum(comparison is not None for comparison in judged),
            "of_them_never_above_placebo": sum(comparison is not None and comparison.never_above_placebo for comparison in judged),
            "kept_pairs_set_aside": len(set_aside_for_placebo),
            "kept_pairs_set_aside_by_symptom": set_aside_for_placebo.groupby("symptom").size().to_dict(),
        }
    if masked_negatives is not None:
        summary["mask_grades"] = sorted(arguments.mask_grades)
        summary["masked_negative_pairs"] = len(masked_negatives)
        summary["masked_negative_pairs_by_type"] = masked_negatives.groupby("perturbation_type").size().to_dict()
        summary["masked_negative_pairs_by_symptom"] = masked_negatives.groupby("symptom").size().to_dict()
    if evidenced_negative_summary:  # recorded only when a decision 9.92 flag is set
        summary["evidenced_negative_sources"] = evidenced_negative_summary
    arguments.output.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
