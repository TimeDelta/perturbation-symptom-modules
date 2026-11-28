"""The eras and research strata of amendment item 38's two descriptive readings (docs/preregistration.md, item 38 (d)
and (g); the owner, 23 November 2026), computed from the per-cell search table of (g).

(g) reads the held-out difference between the tested model and the best baseline inside strata of how many records
name a pair; (d) reads it by when the pair was first recorded. Both are descriptive: neither enters H1, H2 or P1,
spends alpha, or compares an interval with a level. Both rest on the exhaustive search of (g), a research pass on
Fable that counts, for every cell (every perturbation of the evidence table against every scored symptom construct,
labelled or not, held out or not), the PubMed records and admitted preprints whose title or abstract names both, and
keeps the year of the earliest. That search runs after the evidence table is rebuilt and before the draw of decision
1.1, and its output, with the boundaries this module derives from it, is hashed and committed before the draw.
experiments/write_research_strata_and_eras.py writes them; experiments/score_research_strata_and_eras.py reads them
beside the confirmatory scoring.

**The input schema is an assumption of this module**, written on 27 November 2026 before the search exists, which the
(g) pass may revise; a revision changes CELL_SEARCH_TABLE_COLUMNS, read_cell_search_table and
validated_cell_search_table, and nothing downstream of them.
One row per cell, as parquet or CSV:

- ``perturbation_id`` (string): the perturbation as the evidence table's ``perturbation_id`` holds it.
- ``symptom`` (string): the symptom as the evidence table's ``symptom`` column holds it.
- ``search_status``: ``searched``, or ``not_searched`` for a cell whose request still failed after it was repeated
  (item 38 (g), "Being exhaustive").
- ``record_count`` (integer, 0 or more): the records counted for the cell under (g)'s rule; empty when not searched.
  Never 0 for a cell that was not searched: "the cell is recorded as not searched with the reason, never as zero".
- ``earliest_record_year`` (integer): the publication year of the earliest counted record, from PubMed's metadata or
  Europe PMC's preprint record; present exactly when ``record_count`` is 1 or more.
- ``not_searched_reason`` (string): why a cell was not searched; empty for a searched cell. A cell that was not
  searched and carries no reason is unexplained, and so is a cell of the scored table that has no row at all.

Other columns (the query string, the identifier of the earliest record, whether it has an abstract, the times of the
requests) are allowed and not read here.

**The rules, as registered.**

- *Strata* (g): "Genes and drugs are binned apart, each over its own cells. Within a type: if no more than a third of
  its cells are **none**, three equal-count strata (tertiles), ties kept together in the lower stratum; otherwise
  **none**, and the remaining cells split at their median count into **fewer** (at or below it) and **more** (above
  it)." "The two-stratum form, none against any, is reported beside it always." "Every cell is binned by its own
  count, positive or unlabelled", so no label enters a stratum.
- *Eras* (d): "Within a type the eras are the thirds of the first-record year over that type's dated labelled pairs
  in the whole table, ties kept in the earlier third", and "Each type is also reported two-way at the end of 2015".
  "Only a labelled pair is read by its date": an era holds its positives, which are "scored against the same
  unlabelled cells of the held-out set". "A cell with no record is a stratum of its own and is never dropped": among
  positives that stratum is **undated**, the **none** stratum of (g).
- *The registered gene date* (d): "The gene reading is given under both dates". The second date is the ``time_split``
  pair date of configs/evaluation.yaml (``publication_of_cited_reference_else_biocuration``), which the evidence table
  carries as ``evidence_date`` and load_experiment_data as ``evidence_dates``; it is read at the 2015 cut, the one cut
  the registration makes "common to both types and to the registered gene date", since the thirds are cut on the
  first-record date. A gene positive without that date is **undated** under it.

**Where the registration leaves a detail to the code, it is read here as follows**, each stated so that it can be
corrected:

1. *Thirds* (eras and tertiles alike). The sorted values are cut by position as
   mechanistic_pathway_learning/evaluation/measurement_coverage_strata.py cuts its bins (position i of n is in group
   i * 3 // n, so with n not a multiple of three the earlier groups take the extra values); the boundary of a group
   is the value at its last position, and every value equal to a boundary goes to the lower group, which is the
   registered tie rule. Ties can therefore leave a group empty; it is reported empty, not refilled.
2. *The median* of the nonzero counts is numpy's (the mean of the two middle counts for an even number).
3. *A cell that was not searched, with its reason*, is left out of every reading here and named in the record by
   type and reason, as the registration does for "A construct with no searchable term"; it is not binned, is not in
   the denominator of the share of none, and its positives are in no era. It has no count, so it cannot be "binned by
   its own count", and it is not **none**, which is a count of zero. The registered gene date reading leaves out the
   same cells, so the gene reading under both dates is read on the same cells.
4. *A pair a label selection set aside* (label_mask False, neither positive nor negative) is a cell of the table, so
   it is binned by its count like every cell; it is in no era, being no labelled pair, and it is scored in no stratum.
5. *A perturbation type other than gene and drug* (a combination) is binned apart, as a type of its own; the
   registration names genes and drugs only.

Not computed here: the share of counted records without an abstract and the share that are preprints (left open as
`[P 23]`), the text-mined literature count kept beside the search's count, and the seeded sample of 20 labelled
development cells per stratum that the (g) pass reads after the held-out set is fixed, which
mechanistic_pathway_learning/evaluation/sourcing_sample.py draws from the assignment written here (built 28 November
2026, an unreviewed draft).
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

SEARCHED, NOT_SEARCHED = "searched", "not_searched"
CELL_SEARCH_TABLE_COLUMNS = ("perturbation_id", "symptom", "search_status", "record_count", "earliest_record_year", "not_searched_reason")

# The two-way era cut: the end of 2015, configs/evaluation.yaml's splits.time_split.monogenic_cutoff, which no code
# reads (tests/test_research_strata_and_eras.py asserts the two agree), and experiments/run_baselines.py's
# --time-split-cutoff default.
TWO_WAY_ERA_CUT = date(2015, 12, 31)

TERTILE_FORM, NONE_FEWER_MORE_FORM = "tertiles", "none_fewer_more"
LOWER_THIRD, MIDDLE_THIRD, UPPER_THIRD = "lower_third", "middle_third", "upper_third"
NONE_STRATUM, FEWER_STRATUM, MORE_STRATUM, ANY_STRATUM = "none", "fewer", "more", "any"
FIRST_THIRD, SECOND_THIRD, LAST_THIRD = "first_third", "second_third", "last_third"
THROUGH_CUT, AFTER_CUT = f"through_{TWO_WAY_ERA_CUT.year}", f"from_{TWO_WAY_ERA_CUT.year + 1}"
UNDATED = "undated"
UNLABELLED_CELL = "unlabelled"  # in an era column: a cell of the reading that is not a kept positive and was not set aside, scored against every era's positives
NOT_IN_THE_READING = ""  # a cell left out (not searched), set aside by a label selection, or of a type a reading omits

# The per-cell columns write_research_strata_and_eras writes, with the order their strata are reported in. A "cells"
# reading's stratum holds its own cells, positive and unlabelled; a "positives" reading's stratum holds its positives,
# scored against every unlabelled cell of the reading (item 38 (d): "Each era's positives are scored against the same
# unlabelled cells of the held-out set").
READING_COLUMNS = {
    "research_stratum": ("cells", (LOWER_THIRD, MIDDLE_THIRD, UPPER_THIRD, NONE_STRATUM, FEWER_STRATUM, MORE_STRATUM)),
    "none_against_any": ("cells", (NONE_STRATUM, ANY_STRATUM)),
    "first_record_era_thirds": ("positives", (FIRST_THIRD, SECOND_THIRD, LAST_THIRD, UNDATED)),
    "first_record_era_two_way": ("positives", (THROUGH_CUT, AFTER_CUT, UNDATED)),
    "registered_date_era_two_way": ("positives", (THROUGH_CUT, AFTER_CUT, UNDATED)),
}
REGISTERED_DATE_TYPE = "gene"  # the registered gene date is read for genes only


class UnexplainedUnsearchedCells(ValueError):
    """A cell of the scored table was not searched and no reason says why (item 38 (g): "the reading is not run while
    any remain unexplained")."""


def read_cell_search_table(path: Path) -> pd.DataFrame:
    """The search table of (g), checked against the schema above; parquet or CSV by suffix."""
    path = Path(path)
    table = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, dtype={"perturbation_id": str, "symptom": str,
                                                                                               "search_status": str, "not_searched_reason": str},
                                                                                  keep_default_na=False, na_values={"record_count": [""], "earliest_record_year": [""]})
    return validated_cell_search_table(table, str(path))


def validated_cell_search_table(table: pd.DataFrame, source: str = "the search table") -> pd.DataFrame:
    """The table with record_count and earliest_record_year as nullable integers and not_searched_reason as a string,
    refused when a column is missing, a cell appears twice, or a row contradicts the schema. An unexplained cell is not
    refused here but by refuse_unexplained_unsearched_cells, which also sees the cells that have no row."""
    missing = [column for column in CELL_SEARCH_TABLE_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"{source} lacks {missing}; the schema is the one mechanistic_pathway_learning/evaluation/research_strata_and_eras.py states")
    table = table.copy()
    table["perturbation_id"] = table.perturbation_id.astype(str)
    table["symptom"] = table.symptom.astype(str)
    table["search_status"] = table.search_status.astype(str)
    table["not_searched_reason"] = table.not_searched_reason.fillna("").astype(str).str.strip()
    problems = []
    for column in ("record_count", "earliest_record_year"):
        values = pd.to_numeric(table[column], errors="coerce")
        not_whole = values.notna() & (values != np.floor(values.fillna(0)))
        if not_whole.any() or (table[column].notna() & values.isna()).any():
            problems.append(f"{column} holds a value that is not a whole number")
        table[column] = values.round().astype("Int64")
    duplicated = table.duplicated(["perturbation_id", "symptom"], keep=False)
    if duplicated.any():
        problems.append(f"{int(duplicated.sum())} rows repeat a cell, e.g. {table.loc[duplicated, ['perturbation_id', 'symptom']].iloc[0].tolist()}")
    unknown_status = ~table.search_status.isin([SEARCHED, NOT_SEARCHED])
    if unknown_status.any():
        problems.append(f"search_status holds {sorted(set(table.search_status[unknown_status]))}, not {SEARCHED} or {NOT_SEARCHED}")
    searched, not_searched = table.search_status == SEARCHED, table.search_status == NOT_SEARCHED
    counted = searched & table.record_count.notna()
    checks = {
        "a searched cell without a record_count": searched & table.record_count.isna(),
        "a negative record_count": counted & (table.record_count.fillna(0) < 0),
        "a searched cell with records but no earliest_record_year": counted & (table.record_count.fillna(0) > 0) & table.earliest_record_year.isna(),
        "a searched cell with no record but an earliest_record_year": counted & (table.record_count.fillna(0) == 0) & table.earliest_record_year.notna(),
        "a searched cell with a not_searched_reason": searched & (table.not_searched_reason != ""),
        "a cell not searched but given a record_count (never as zero)": not_searched & table.record_count.notna(),
        "a cell not searched but given an earliest_record_year": not_searched & table.earliest_record_year.notna(),
    }
    problems += [f"{int(rows.sum())} rows hold {what}" for what, rows in checks.items() if rows.any()]
    if problems:
        raise ValueError(f"{source} does not follow the schema: " + "; ".join(problems))
    return table.reset_index(drop=True)


def refuse_unexplained_unsearched_cells(search_table: pd.DataFrame, scored_cells: pd.DataFrame) -> None:
    """Raise UnexplainedUnsearchedCells while any cell of scored_cells has no row in search_table, or has a row marked
    not searched with no reason. A row naming a perturbation or symptom that scored_cells does not hold at all (a search
    run on another evidence table) is refused too, with a ValueError."""
    keys = ["perturbation_id", "symptom"]
    joined = scored_cells[keys].merge(search_table[keys + ["search_status", "not_searched_reason"]], on=keys, how="left", indicator=True)
    without_a_row = joined._merge == "left_only"
    without_a_reason = (joined.search_status == NOT_SEARCHED) & (joined.not_searched_reason.fillna("") == "")
    foreign_perturbations = sorted(set(search_table.perturbation_id) - set(scored_cells.perturbation_id))
    foreign_symptoms = sorted(set(search_table.symptom) - set(scored_cells.symptom))
    if foreign_perturbations or foreign_symptoms:
        raise ValueError(f"the search table names perturbations ({foreign_perturbations[:5]}, {len(foreign_perturbations)} in all) or symptoms "
                         f"({foreign_symptoms[:5]}, {len(foreign_symptoms)} in all) that the scored table does not hold: was it searched on another evidence table?")
    if without_a_row.any() or without_a_reason.any():
        examples = joined.loc[without_a_row | without_a_reason, keys].head(5).values.tolist()
        raise UnexplainedUnsearchedCells(
            f"not run: {int(without_a_row.sum())} cells of the scored table have no row in the search table and {int(without_a_reason.sum())} are marked "
            f"not searched with no reason (e.g. {examples}); item 38 (g): \"the reading is not run while any remain unexplained\"")


def equal_count_third_boundaries(values: np.ndarray) -> tuple[float, float] | None:
    """The boundaries of three equal-count groups of values, ties kept in the lower group: the value at the last
    position of the first group and at the last position of the second, positions cut as
    measurement_coverage_strata.py cuts its bins (position i of n in group i * 3 // n). None for no values."""
    ordered = np.sort(np.asarray(values, dtype=float), kind="stable")
    if not len(ordered):
        return None
    group_of_position = np.arange(len(ordered)) * 3 // len(ordered)
    return float(ordered[np.flatnonzero(group_of_position <= 0)[-1]]), float(ordered[np.flatnonzero(group_of_position <= 1)[-1]])


def thirds_of(values: np.ndarray, boundaries: tuple[float, float], labels: tuple[str, str, str]) -> np.ndarray:
    """The label of each value against the two boundaries; a value equal to a boundary takes the lower label."""
    values = np.asarray(values, dtype=float)
    first_boundary, second_boundary = boundaries
    return np.where(values <= first_boundary, labels[0], np.where(values <= second_boundary, labels[1], labels[2])).astype(object)


def research_strata_of_one_type(record_counts: np.ndarray) -> tuple[np.ndarray, dict]:
    """The research stratum of each cell of one type, by (g)'s rule, and the form and boundaries it gave."""
    counts = np.asarray(record_counts, dtype=float)
    num_cells, num_none = len(counts), int((counts == 0).sum())
    summary = {"num_cells": num_cells, "num_none_cells": num_none, "none_share": num_none / num_cells if num_cells else None}
    if not num_cells:  # every cell of the type left out
        return np.array([], dtype=object), {**summary, "form": None, "boundaries": None}
    if 3 * num_none <= num_cells:  # "no more than a third of its cells are none"
        boundaries = equal_count_third_boundaries(counts)
        strata = thirds_of(counts, boundaries, (LOWER_THIRD, MIDDLE_THIRD, UPPER_THIRD))
        summary.update(form=TERTILE_FORM, boundaries={"largest_count_in_the_lower_third": boundaries[0], "largest_count_in_the_middle_third": boundaries[1]})
    else:
        nonzero = counts[counts > 0]
        median = float(np.median(nonzero)) if len(nonzero) else None
        strata = np.where(counts == 0, NONE_STRATUM, np.where(counts <= (median if median is not None else np.inf), FEWER_STRATUM, MORE_STRATUM)).astype(object)
        summary.update(form=NONE_FEWER_MORE_FORM, boundaries={"median_count_of_the_cells_with_a_record": median})
    return strata, summary


def first_record_eras_of_one_type(earliest_years: np.ndarray, kept_positive: np.ndarray, record_counts: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict]:
    """The era of each cell of one type under the first-record date, as thirds and as the two-way cut, and the boundary
    years. A kept positive with a record takes its era, one with no record is undated, and every other cell is
    unlabelled (scored against each era's positives); the caller marks the cells set aside by a label selection."""
    kept_positive = np.asarray(kept_positive, dtype=bool)
    counts = np.asarray(record_counts, dtype=float)
    years = np.asarray(earliest_years, dtype=float)
    dated = kept_positive & (counts > 0)
    boundaries = equal_count_third_boundaries(years[dated])
    thirds = np.full(len(years), UNLABELLED_CELL, dtype=object)
    two_way = np.full(len(years), UNLABELLED_CELL, dtype=object)
    if boundaries is not None:
        thirds[dated] = thirds_of(years[dated], boundaries, (FIRST_THIRD, SECOND_THIRD, LAST_THIRD))
    two_way[dated] = np.where(years[dated] <= TWO_WAY_ERA_CUT.year, THROUGH_CUT, AFTER_CUT)
    undated = kept_positive & (counts == 0)
    thirds[undated], two_way[undated] = UNDATED, UNDATED
    summary = {"num_dated_kept_positives": int(dated.sum()), "num_undated_kept_positives": int(undated.sum()),
               "boundary_years": None if boundaries is None else {"last_year_of_the_first_third": int(boundaries[0]),
                                                                  "last_year_of_the_second_third": int(boundaries[1])},
               "two_way_cut": TWO_WAY_ERA_CUT.isoformat()}
    return thirds, two_way, summary


def registered_date_eras(registered_date_ordinals: np.ndarray, kept_positive: np.ndarray) -> np.ndarray:
    """The two-way era of each cell under the registered gene date (a proleptic Gregorian ordinal, 0 when undated)."""
    ordinals = np.asarray(registered_date_ordinals, dtype=np.int64)
    kept_positive = np.asarray(kept_positive, dtype=bool)
    eras = np.full(len(ordinals), UNLABELLED_CELL, dtype=object)
    eras[kept_positive & (ordinals > 0)] = np.where(ordinals[kept_positive & (ordinals > 0)] <= TWO_WAY_ERA_CUT.toordinal(), THROUGH_CUT, AFTER_CUT)
    eras[kept_positive & (ordinals <= 0)] = UNDATED
    return eras


SCORED_CELL_COLUMNS = ("perturbation_id", "symptom", "perturbation_type", "kept_positive", "set_aside_by_label_selection", "registered_date_ordinal")


def scored_cells_from_experiment_data(data, minimum_positives_to_score: int) -> pd.DataFrame:
    """Every cell of the scored table: each perturbation of the data against each symptom with at least
    minimum_positives_to_score kept positives in the whole data (the registered micro set of
    experiments/score_confirmatory.py), with its type, whether it is a kept positive, whether a label selection set it
    aside, and the registered gene date of the evidence table (0 when undated)."""
    label_mask = np.ones_like(data.outcomes, dtype=bool) if data.label_mask is None else np.asarray(data.label_mask, dtype=bool)
    kept = (data.outcomes > 0) & label_mask
    scored_columns = [column for column in range(len(data.symptoms)) if kept[:, column].sum() >= minimum_positives_to_score]
    num_perturbations = len(data.perturbation_ids)
    rows = np.repeat(np.arange(num_perturbations), len(scored_columns))
    columns = np.tile(np.array(scored_columns, dtype=int), num_perturbations)
    dates = np.zeros_like(data.outcomes, dtype=np.int64) if data.evidence_dates is None else np.asarray(data.evidence_dates, dtype=np.int64)
    return pd.DataFrame({"perturbation_id": np.array(data.perturbation_ids, dtype=object)[rows],
                         "symptom": np.array(data.symptoms, dtype=object)[columns],
                         "perturbation_type": np.array(data.perturbation_types, dtype=object)[rows],
                         "kept_positive": kept[rows, columns], "set_aside_by_label_selection": ~label_mask[rows, columns],
                         "registered_date_ordinal": dates[rows, columns]})


def stratum_counts(labels: np.ndarray, kept_positive: np.ndarray, order: tuple[str, ...]) -> dict:
    labels = np.asarray(labels, dtype=object)
    return {"cells": {label: int((labels == label).sum()) for label in order if (labels == label).any()},
            "kept_positives": {label: int(((labels == label) & kept_positive).sum()) for label in order if (labels == label).any()}}


def assign_strata_and_eras(search_table: pd.DataFrame, scored_cells: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """One row per cell of scored_cells with its research stratum, its none-against-any stratum and its era under each
    date, and the record of the rule each type took and the boundaries it gave. Refuses while any cell is unexplained.

    search_table is validated_cell_search_table's; scored_cells has SCORED_CELL_COLUMNS (scored_cells_from_experiment_data).
    Search rows of symptoms the scored table does not score are left out and counted; a row of a perturbation it does
    not hold is refused."""
    missing = [column for column in SCORED_CELL_COLUMNS if column not in scored_cells.columns]
    if missing:
        raise ValueError(f"the scored cells lack {missing}")
    keys = ["perturbation_id", "symptom"]
    scored_symptoms = set(scored_cells.symptom)
    in_scored_table = search_table.symptom.isin(scored_symptoms)  # a row of a perturbation the table lacks is refused below
    refuse_unexplained_unsearched_cells(search_table[in_scored_table], scored_cells)
    cells = scored_cells.merge(search_table.loc[in_scored_table, keys + ["search_status", "record_count", "earliest_record_year", "not_searched_reason"]],
                               on=keys, how="left", validate="one_to_one")
    cells = cells.sort_values(keys, kind="stable").reset_index(drop=True)
    left_out = (cells.search_status == NOT_SEARCHED).to_numpy()
    cells["left_out_reason"] = np.where(left_out, cells.not_searched_reason.fillna(""), "")
    for column in READING_COLUMNS:
        cells[column] = NOT_IN_THE_READING
    record = {"scored_symptoms": sorted(scored_symptoms), "num_scored_cells": int(len(cells)),
              "search_rows_of_symptoms_the_table_does_not_score": int((~in_scored_table).sum()), "types": {}}
    set_aside = cells.set_aside_by_label_selection.to_numpy(dtype=bool)
    kept_positive = cells.kept_positive.to_numpy(dtype=bool)
    for perturbation_type in sorted(set(cells.perturbation_type)):
        of_type = (cells.perturbation_type == perturbation_type).to_numpy()
        in_reading = of_type & ~left_out
        positions = np.flatnonzero(in_reading)
        counts = cells.record_count.to_numpy(dtype=float, na_value=np.nan)[positions]
        years = cells.earliest_record_year.to_numpy(dtype=float, na_value=np.nan)[positions]
        strata, strata_summary = research_strata_of_one_type(counts)
        none_against_any = np.where(counts == 0, NONE_STRATUM, ANY_STRATUM).astype(object)
        thirds, two_way, era_summary = first_record_eras_of_one_type(years, kept_positive[positions], counts)
        cells.loc[positions, "research_stratum"] = strata
        cells.loc[positions, "none_against_any"] = none_against_any
        scored_positions = positions[~set_aside[positions]]
        in_scored = ~set_aside[positions]
        cells.loc[scored_positions, "first_record_era_thirds"] = thirds[in_scored]
        cells.loc[scored_positions, "first_record_era_two_way"] = two_way[in_scored]
        entry = {
            "research_strata": {**strata_summary, **stratum_counts(strata, kept_positive[positions], READING_COLUMNS["research_stratum"][1])},
            "none_against_any": stratum_counts(none_against_any, kept_positive[positions], READING_COLUMNS["none_against_any"][1]),
            "first_record_eras": {**era_summary,
                                  "kept_positives_per_era_thirds": stratum_counts(thirds, kept_positive[positions], READING_COLUMNS["first_record_era_thirds"][1])["kept_positives"],
                                  "kept_positives_per_era_two_way": stratum_counts(two_way, kept_positive[positions], READING_COLUMNS["first_record_era_two_way"][1])["kept_positives"]},
            "left_out_not_searched": {"cells": int((of_type & left_out).sum()), "kept_positives": int((of_type & left_out & kept_positive).sum()),
                                      "cells_by_reason": {reason: int(count) for reason, count in
                                                          cells.loc[of_type & left_out, "left_out_reason"].value_counts().sort_index().items()}},
        }
        if perturbation_type == REGISTERED_DATE_TYPE:
            registered = registered_date_eras(cells.registered_date_ordinal.to_numpy()[positions], kept_positive[positions])
            cells.loc[scored_positions, "registered_date_era_two_way"] = registered[in_scored]
            entry["registered_date_two_way"] = {"date": "configs/evaluation.yaml splits.time_split.pair_date (the evidence table's evidence_date)",
                                                "two_way_cut": TWO_WAY_ERA_CUT.isoformat(),
                                                "kept_positives_per_era": stratum_counts(registered, kept_positive[positions], READING_COLUMNS["registered_date_era_two_way"][1])["kept_positives"]}
        record["types"][perturbation_type] = entry
    forms = {name: entry["research_strata"]["form"] for name, entry in record["types"].items() if entry["research_strata"]["form"] is not None}
    # (g): "the pooled reading is given beside it". Each type is binned on its own cuts, so the pooled reading pools the
    # strata of the same name, which exist in both types only when both took the same form.
    if not forms:
        record["pooled_research_stratum"] = {"defined": False, "reason": "no type has a cell in the reading"}
    elif len(set(forms.values())) == 1:
        record["pooled_research_stratum"] = {"defined": True, "form": next(iter(forms.values()))}
    else:
        record["pooled_research_stratum"] = {"defined": False, "reason": "the types took different forms (" + ", ".join(f"{name} {form}" for name, form in forms.items())
                                             + "), so their research strata do not pool; none against any pools whatever the forms"}
    output_columns = list(SCORED_CELL_COLUMNS) + ["record_count", "earliest_record_year", "left_out_reason"] + list(READING_COLUMNS)
    return cells[output_columns], record


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_cells(cells: pd.DataFrame, path: Path) -> str:
    """Write the per-cell assignment as CSV (text, so that a commit shows what changed) and return its SHA-256."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cells.to_csv(path, index=False, lineterminator="\n")
    return file_sha256(path)


def read_cells(path: Path) -> pd.DataFrame:
    """The per-cell assignment write_cells wrote, with its column types restored."""
    cells = pd.read_csv(path, dtype={column: str for column in ("perturbation_id", "symptom", "perturbation_type", "left_out_reason", *READING_COLUMNS)},
                        keep_default_na=False, na_values={"record_count": [""], "earliest_record_year": [""]})
    for column in ("record_count", "earliest_record_year"):
        cells[column] = pd.to_numeric(cells[column]).astype("Int64")
    for column in ("kept_positive", "set_aside_by_label_selection"):
        cells[column] = cells[column].astype(str).map({"True": True, "False": False}).astype(bool)
    cells["registered_date_ordinal"] = cells.registered_date_ordinal.astype(np.int64)
    return cells


def write_record(record: dict, path: Path) -> str:
    """Write the boundary record as JSON with a sha256sum-format sidecar (<path>.sha256) and return its SHA-256."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    digest = file_sha256(path)
    Path(f"{path}.sha256").write_text(f"{digest}  {path.name}\n")
    return digest


def same_assignment(recomputed: pd.DataFrame, committed: pd.DataFrame) -> list[str]:
    """The columns in which two assignments differ (empty when they agree cell for cell), for a scorer that checks the
    committed cuts were not moved."""
    keys = ["perturbation_id", "symptom"]
    if len(recomputed) != len(committed) or not recomputed[keys].reset_index(drop=True).equals(committed[keys].reset_index(drop=True)):
        return ["the cells themselves"]
    differing = []
    for column in recomputed.columns:
        left, right = recomputed[column].reset_index(drop=True), committed[column].reset_index(drop=True)
        if column in ("record_count", "earliest_record_year"):
            same = left.astype("Int64").fillna(-1).astype(np.int64).equals(right.astype("Int64").fillna(-1).astype(np.int64))
        else:
            same = left.astype(str).equals(right.astype(str))
        if not same:
            differing.append(column)
    return differing
