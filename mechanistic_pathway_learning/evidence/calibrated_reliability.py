"""A feature-dependent reliability model calibrated on held-out labels (decision 9.59, the owner, 16 October 2026).

What it estimates. For a soft-evidence pair (evidence/soft_priors.py: one row per perturbation, symptom, class and
direction, with its sources and its deduplicated record count), the probability that the pair is a label-grade
statement, read off the pairs the fit trains on: a logistic regression of the label outcome (1 where the training
fold's label table holds the pair as a positive, 0 where it does not) on the row's features. Its prediction replaces
the fixed prior probability of configs/soft_prior_tiers.csv; the tier's unit strength and the tempered count still
set how hard the prior pulls, so the regression says what to believe and the tiers say how much.

Features. The evidence class, the direction, each source present, the logarithm of the record count, the species the
evidence was measured in (a property of the source, SPECIES_OF_SOURCE: mouse for the four mouse sources, human
otherwise; a primate or other source takes its own level when one enters), the perturbation type, and the
perturbation's literature popularity (log of its distinct PubMed references in the literature table, 0 without one).

What the owner asked about species (decision 9.56, 16 October 2026), as written: "wouldn't all non-human evidence need
to be fit separately so species isn't one of the fit features ... Even primate research I would think should have its
negative evidence weighted differently though". That asks for a separate fit per non-human species, or at least for a
non-human source's absences to be weighted apart from its calls. Until 24 October 2026 this docstring said species was
a feature "as the owner asked", which is the opposite of what 9.56 records; the form below is the partial-pooling
answer to the second half of the question, and the separate fit per species stays the owner's to choose (9.93).

The species, source and direction terms (decision 9.93, 24 October 2026). While IMPC was the only mouse source, the
column species:mouse equalled source:IMPC-knockout, so a species effect could not be told from a pipeline effect. When
the pairs carry two or more sources of one non-human species (hierarchical_sources), the regression takes the
partially pooled form:
  - species:<species>, the main effect shared by every source of that species, at the base penalty;
  - species_direction:<species>:negative, the species' absences against its calls, at the base penalty;
  - source:<source> for each non-human source, now its deviation from its species, and
    source_direction:<source>:negative, the deviation of its absences, both shrunk toward 0 by an L2 penalty
    source_deviation_penalty times the base one (SOURCE_DEVIATION_PENALTY, the trainer's
    --soft-prior-calibration-source-deviation-penalty).
Without the extra shrinkage the deviations and the species column are collinear (species:mouse is the sum of the mouse
sources' indicators on pairs with one mouse source), and the split between them would be set by the base penalty
alone. The penalty is applied by dividing each deviation column by sqrt(source_deviation_penalty) before the fit and
the fitted weight by the same factor after it, which is the same optimum as a per-coefficient penalty because
sklearn's L2 term is 0.5 w^T w. Why 10: with REGULARISATION_C 1 the deviations then carry a Gaussian prior with
standard deviation 1/sqrt(10), about 0.32 on the log-odds, so a mouse source is expected to differ from the other
mouse sources by a factor of about 1.4 in the odds unless its own cells say more; it is a numerical choice, not a
physiological one, and the measurement record (docs/mouse_sources_measured_v5.md) gives the coefficients at 1, 10 and
100. With one source per species the columns are those of the form before 9.93, so a run whose reports hold IMPC as
the only mouse source fits the model it fitted before, bit for bit (tested).

A symptom with no label positives. A cell on a symptom that has no label positive on the fit rows of its perturbation
kind (gene or drug) trains the regression toward 0 because the label table cannot state a positive there, not because
the evidence is wrong: on v5 psychomotor_retardation has no gene label at all, because the human crosswalk maps it to
no HPO term (docs/symptom_crosswalk_fine.csv, "HPO retired Psychomotor retardation (HP:0025356) into Global
developmental delay"), so its 5,143 IMPC cells cannot be calibrated. fit_calibration reports such symptoms, with their
cells by source, in Calibration.symptoms_without_label_positives; exclude_symptoms_without_label_positives (off by
default, so the fit is the one before 9.93) leaves their cells out of the fit, and the prediction is still written on
them.

The comparison's own statistic (decision 9.48, option 3: "Carrying stat to calibrated proper is the way"). Where a
pair's evidence carries one (evidence/soft_priors.py keeps the most informative comparison's), four more features:
statistic:logit_excess, the log-odds of its posterior probability that the drug raises the event rate, clipped to
+-LOGIT_CLIP and divided by it, so it lies in [-1, 1]; its square, statistic:logit_excess_squared, because the label
rate need not rise monotonically with the statistic (on the development pairs of v5, 17 October 2026, FAERS pairs
whose posterior put the excess below 0.025 were label positives more often than pairs with an inconclusive posterior:
docs/open_decisions.md, 9.48); statistic:log_information, the logarithm of one plus its information; and
statistic:present. A pair without a statistic takes 0 in all four, so the indicator carries the difference. The
regression then says what each level of the statistic is worth on the training-fold labels, which is the calibration
the decision asked for. When no pair carries a statistic the columns are not made, so a run on tables built before
the statistics fits the model it fitted before.

Popularity. It is a feature so that the volume of reports on a well-studied perturbation is attributed to reporting
propensity rather than to truth (the SAR reading of positive-only sources, docs/soft_priors.md); the prediction is
read with popularity set to its median over the training rows, so the prior carries the report-type effect and not
the popularity effect. The raw prediction is kept beside it in the summary for the reader.

Where it fits. On the perturbations of the rows a fit trains on, never on the lockbox and never on a held-out fold;
the trainer passes those rows (--soft-prior-probability calibrated). Below MINIMUM_CALIBRATION_CASES positives or
negatives among them the tiers are kept and the summary says why.

What it is not. Not Dawid-Skene: there is no latent truth and no conditional-independence assumption; the target is
the label table, with its own ascertainment, which is why the popularity term exists and why the arm is read against
the permuted prior (docs/soft_priors.md, section 3).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# every label-side source measured in another species; the three after IMPC were added by decision 9.93
SPECIES_OF_SOURCE = {"IMPC-knockout": "mouse", "MGI-literature": "mouse", "MGI-screen": "mouse", "SFARI-mouse-models": "mouse"}
LOGIT_CLIP = 10.0
DEFAULT_SPECIES = "human"
MINIMUM_CALIBRATION_CASES = 20
REGULARISATION_C = 1.0
# the L2 strength on a non-human source's deviation from its species, as a multiple of the base strength (9.93)
SOURCE_DEVIATION_PENALTY = 10.0


@dataclass
class Calibration:
    features: list[str]
    coefficients: dict[str, float]
    intercept: float
    training_rows: int
    training_positives: int
    median_log_popularity: float
    predicted_by_class_and_direction: dict[str, float]
    raw_predicted_by_class_and_direction: dict[str, float]
    kept_tiers: bool
    reason: str = ""
    # the deviation columns of the partially pooled form and the penalty multiple each was fitted under (9.93); empty
    # in the form before it
    penalty_multiples: dict[str, float] = field(default_factory=dict)
    # symptom -> what the fit had on a symptom with no label positive on the fit rows of its cells' perturbation kind
    symptoms_without_label_positives: dict[str, dict] = field(default_factory=dict)
    excluded_symptoms_without_label_positives: bool = False


def species_of_sources(sources: str) -> str:
    """The species of a pair's evidence: the first non-human species among its sources, else human."""
    for source in str(sources).split(";"):
        species = SPECIES_OF_SOURCE.get(source.strip())
        if species:
            return species
    return DEFAULT_SPECIES


def feature_frame(pairs: pd.DataFrame, perturbation_types: dict[str, str], log_popularity: dict[str, float]) -> pd.DataFrame:
    """One row per resolved pair, with the columns named in the module docstring; categorical levels are one-hot
    columns named level:value, every source its own column source:name."""
    frame = pd.DataFrame(index=pairs.index)
    for level in sorted(set(pairs.evidence_class)):
        frame[f"class:{level}"] = (pairs.evidence_class == level).astype(float)
    frame["direction:positive"] = (pairs.direction == "positive").astype(float)
    sources = sorted({source for cell in pairs.sources for source in str(cell).split(";") if source})
    for source in sources:
        frame[f"source:{source}"] = pairs.sources.map(lambda cell: float(source in str(cell).split(";")))
    frame["log_records"] = np.log1p(pairs.n_distinct.astype(float))
    species = pairs.sources.map(species_of_sources)
    for level in sorted(set(species) - {DEFAULT_SPECIES}):
        frame[f"species:{level}"] = (species == level).astype(float)
    kinds = pairs.perturbation_id.map(lambda identifier: perturbation_types.get(identifier, ""))
    frame["perturbation:drug"] = (kinds == "drug").astype(float)
    frame["log_popularity"] = pairs.perturbation_id.map(lambda identifier: float(log_popularity.get(identifier, 0.0)))
    if "statistic_probability_of_excess" in pairs.columns and pd.to_numeric(pairs.statistic_probability_of_excess, errors="coerce").notna().any():
        probability = pd.to_numeric(pairs.statistic_probability_of_excess, errors="coerce")
        information = pd.to_numeric(pairs.get("statistic_information", pd.Series(np.nan, index=pairs.index)), errors="coerce")
        present = probability.notna() & information.notna()
        clipped = probability.clip(1e-12, 1.0 - 1e-12)
        scaled = np.clip(np.log(clipped / (1.0 - clipped)), -LOGIT_CLIP, LOGIT_CLIP) / LOGIT_CLIP
        frame["statistic:logit_excess"] = np.where(present, scaled, 0.0)
        frame["statistic:logit_excess_squared"] = np.where(present, scaled ** 2, 0.0)
        frame["statistic:log_information"] = np.where(present, np.log1p(information.clip(lower=0.0)), 0.0)
        frame["statistic:present"] = present.astype(float)
    pooled = hierarchical_sources(sources)
    if pooled:
        negative = (pairs.direction == "negative").astype(float)
        for level in sorted({SPECIES_OF_SOURCE[source] for source in pooled}):
            column = (species == level).astype(float) * negative
            if column.any():
                frame[f"species_direction:{level}:negative"] = column
        for source in pooled:
            column = frame[f"source:{source}"] * negative
            if column.any():
                frame[f"source_direction:{source}:negative"] = column
    return frame


def hierarchical_sources(sources) -> list[str]:
    """The non-human sources that take the partially pooled form: all of them, once some species has two or more
    sources among the pairs (decision 9.93); none otherwise, so a table whose only mouse source is IMPC keeps the
    columns it had before."""
    non_human = sorted({source for source in sources if source in SPECIES_OF_SOURCE})
    by_species: dict[str, int] = {}
    for source in non_human:
        by_species[SPECIES_OF_SOURCE[source]] = by_species.get(SPECIES_OF_SOURCE[source], 0) + 1
    return non_human if any(count >= 2 for count in by_species.values()) else []


def deviation_columns(feature_names: list[str]) -> list[str]:
    """The columns shrunk toward 0 by the source-deviation penalty: a pooled non-human source's indicator and its
    absence term."""
    pooled = hierarchical_sources([name.split(":", 1)[1] for name in feature_names if name.startswith("source:")])
    return [name for name in feature_names
            if (name.startswith("source:") and name.split(":", 1)[1] in pooled)
            or (name.startswith("source_direction:") and name.split(":")[1] in pooled)]


def cell_table(pairs: pd.DataFrame, features: pd.DataFrame, perturbation_ids: list[str], symptoms: list[str]) -> pd.DataFrame:
    """The resolved pairs that fall inside a data set's perturbation and symptom universe, with their row and column and
    their features; the rows are what the calibration fits on and what it predicts for."""
    row_of = {identifier: index for index, identifier in enumerate(perturbation_ids)}
    column_of = {symptom: index for index, symptom in enumerate(symptoms)}
    rows = pairs.perturbation_id.map(row_of)
    columns = pairs.symptom.map(column_of)
    inside = rows.notna() & columns.notna()
    table = features[inside].copy()
    table.insert(0, "column", columns[inside].astype(int).to_numpy())
    table.insert(0, "row", rows[inside].astype(int).to_numpy())
    table["evidence_class"] = pairs.evidence_class[inside].to_numpy()
    table["direction"] = pairs.direction[inside].to_numpy()
    return table.reset_index(drop=True)


def permute_cell_rows(cells: pd.DataFrame, source_row: np.ndarray) -> pd.DataFrame:
    """After --permute-labels moved row source_row[i] to position i, a prior cell on the old row r sits at the position
    whose source is r."""
    position_of_source = np.argsort(np.asarray(source_row))
    moved = cells.copy()
    moved["row"] = position_of_source[moved.row.to_numpy()]
    return moved


FEATURE_COLUMNS_EXCLUDED = ("row", "column", "evidence_class", "direction")


def symptoms_without_label_positives(cells: pd.DataFrame, outcomes: np.ndarray, labelled: np.ndarray, in_fit: np.ndarray, usable: np.ndarray,
                                     symptom_names: list[str] | None, row_is_drug: np.ndarray | None) -> dict[str, dict]:
    """The symptoms among the usable cells with no label positive on the fit rows of the cells' perturbation kind,
    with the cells and their sources. Without row_is_drug every fit row counts as the same kind."""
    report: dict[str, dict] = {}
    if not usable.any():
        return report
    rows, columns = cells.row.to_numpy(), cells.column.to_numpy()
    cell_is_drug = cells["perturbation:drug"].to_numpy() > 0 if "perturbation:drug" in cells.columns else np.zeros(len(cells), dtype=bool)
    kind_of_row = np.zeros(outcomes.shape[0], dtype=bool) if row_is_drug is None else np.asarray(row_is_drug, dtype=bool)
    source_columns = [name for name in cells.columns if name.startswith("source:")]
    for column in sorted(set(columns[usable].tolist())):
        for is_drug in ((False, True) if row_is_drug is not None else (False,)):
            selected = usable & (columns == column) & ((cell_is_drug == is_drug) if row_is_drug is not None else True)
            if not selected.any():
                continue
            rows_of_kind = in_fit & ((kind_of_row == is_drug) if row_is_drug is not None else True)
            positives = int(((outcomes[rows_of_kind, column] > 0) & labelled[rows_of_kind, column]).sum())
            if positives:
                continue
            name = symptom_names[column] if symptom_names is not None else str(column)
            entry = report.setdefault(name, {"column": int(column), "cells": 0, "cells_by_source": {}, "kinds": []})
            entry["cells"] += int(selected.sum())
            entry["kinds"].append("all" if row_is_drug is None else ("drug" if is_drug else "gene"))
            for source_column in source_columns:
                count = int((cells[source_column].to_numpy()[selected] > 0).sum())
                if count:
                    entry["cells_by_source"][source_column.split(":", 1)[1]] = entry["cells_by_source"].get(source_column.split(":", 1)[1], 0) + count
    return report


def fit_calibration(cells: pd.DataFrame, outcomes: np.ndarray, label_mask: np.ndarray | None, fit_rows: np.ndarray,
                    minimum_cases: int = MINIMUM_CALIBRATION_CASES, regularisation_c: float = REGULARISATION_C,
                    source_deviation_penalty: float = SOURCE_DEVIATION_PENALTY, symptom_names: list[str] | None = None,
                    row_is_drug: np.ndarray | None = None, exclude_symptoms_without_label_positives: bool = False) -> Calibration:
    """The regression on the prior cells whose row the fit trains on and whose label the table states: the target is 1
    where the cell is a label positive, 0 where it is labelled and not positive (a pair the selection set aside is
    not a statement and is left out). Returns a Calibration that keeps the tiers when either side has fewer than
    minimum_cases cells.

    The symptoms with no label positive on the fit rows of their cells' kind are reported in
    symptoms_without_label_positives, and their cells leave the fit only under
    exclude_symptoms_without_label_positives. In the partially pooled form (hierarchical_sources) the deviation
    columns are fitted at source_deviation_penalty times the base L2 strength."""
    feature_names = [column for column in cells.columns if column not in FEATURE_COLUMNS_EXCLUDED]
    in_fit = np.zeros(outcomes.shape[0], dtype=bool)
    in_fit[np.asarray(fit_rows, dtype=int)] = True
    labelled = np.ones(outcomes.shape, dtype=bool) if label_mask is None else np.asarray(label_mask, dtype=bool)
    rows, columns = cells.row.to_numpy(), cells.column.to_numpy()
    usable = in_fit[rows] & labelled[rows, columns]
    without_positives = symptoms_without_label_positives(cells, outcomes, labelled, in_fit, usable, symptom_names, row_is_drug)
    if exclude_symptoms_without_label_positives and without_positives:
        cell_is_drug = cells["perturbation:drug"].to_numpy() > 0 if "perturbation:drug" in cells.columns else np.zeros(len(cells), dtype=bool)
        for entry in without_positives.values():
            for kind in entry["kinds"]:
                kind_mask = np.ones(len(cells), dtype=bool) if kind == "all" else (cell_is_drug == (kind == "drug"))
                usable = usable & ~((columns == entry["column"]) & kind_mask)
    targets = (outcomes[rows, columns] > 0).astype(int)
    training = cells[usable]
    training_targets = targets[usable]
    positives, negatives = int(training_targets.sum()), int((1 - training_targets).sum())
    median_log_popularity = float(np.median(training.log_popularity)) if len(training) else 0.0
    if positives < minimum_cases or negatives < minimum_cases:
        return Calibration(feature_names, {}, 0.0, int(len(training)), positives, median_log_popularity, {}, {}, True,
                           f"{positives} positive and {negatives} negative calibration cells on the fit rows; at least {minimum_cases} of each are needed",
                           symptoms_without_label_positives=without_positives, excluded_symptoms_without_label_positives=exclude_symptoms_without_label_positives)
    from sklearn.linear_model import LogisticRegression

    deviations = deviation_columns(feature_names)
    design = training[feature_names].to_numpy(dtype=float)
    scale = np.ones(len(feature_names))
    if deviations:  # the partially pooled form; before 9.93 there are none and the design is passed as it was
        for name in deviations:
            scale[feature_names.index(name)] = 1.0 / np.sqrt(source_deviation_penalty)
        design = design * scale
    model = LogisticRegression(C=regularisation_c, max_iter=2000)
    model.fit(design, training_targets)
    weights = model.coef_[0] * scale if deviations else model.coef_[0]
    coefficients = {name: float(value) for name, value in zip(feature_names, weights)}
    calibration = Calibration(feature_names, coefficients, float(model.intercept_[0]), int(len(training)), positives, median_log_popularity, {}, {}, False,
                              penalty_multiples={name: float(source_deviation_penalty) for name in deviations},
                              symptoms_without_label_positives=without_positives, excluded_symptoms_without_label_positives=exclude_symptoms_without_label_positives)
    predicted = predict(calibration, cells, at_median_popularity=True)
    raw = predict(calibration, cells, at_median_popularity=False)
    groups = cells.evidence_class.astype(str) + ":" + cells.direction.astype(str)
    calibration.predicted_by_class_and_direction = {str(group): float(np.mean(predicted[groups == group])) for group in sorted(set(groups))}
    calibration.raw_predicted_by_class_and_direction = {str(group): float(np.mean(raw[groups == group])) for group in sorted(set(groups))}
    return calibration


def predict(calibration: Calibration, cells: pd.DataFrame, at_median_popularity: bool = True) -> np.ndarray:
    """The regression's probability per cell; with at_median_popularity the popularity feature is held at the
    training median so the prior carries the report-type effect and not the popularity effect."""
    features = cells[calibration.features].to_numpy(dtype=float)
    if at_median_popularity and "log_popularity" in calibration.features:
        features = features.copy()
        features[:, calibration.features.index("log_popularity")] = calibration.median_log_popularity
    logits = calibration.intercept + features @ np.array([calibration.coefficients[name] for name in calibration.features])
    return 1.0 / (1.0 + np.exp(-np.clip(logits, -30.0, 30.0)))


def calibrated_probability_matrix(calibration: Calibration, cells: pd.DataFrame, tier_probability: np.ndarray) -> np.ndarray:
    """The prior-probability matrix with the regression's prediction written on every prior cell; the tiers' matrix is
    returned unchanged when the calibration kept the tiers."""
    if calibration.kept_tiers:
        return tier_probability
    probability = np.array(tier_probability, copy=True)
    probability[cells.row.to_numpy(), cells.column.to_numpy()] = predict(calibration, cells, at_median_popularity=True)
    return probability


def summarise_calibration(calibration: Calibration) -> dict:
    return {"kept_tiers": calibration.kept_tiers, "reason": calibration.reason, "training_cells": calibration.training_rows,
            "training_positives": calibration.training_positives, "median_log_popularity": calibration.median_log_popularity,
            "intercept": calibration.intercept, "coefficients": calibration.coefficients,
            "mean_prediction_at_median_popularity": calibration.predicted_by_class_and_direction,
            "mean_prediction_raw": calibration.raw_predicted_by_class_and_direction,
            "penalty_multiples": calibration.penalty_multiples, "symptoms_without_label_positives": calibration.symptoms_without_label_positives,
            "excluded_symptoms_without_label_positives": calibration.excluded_symptoms_without_label_positives}

