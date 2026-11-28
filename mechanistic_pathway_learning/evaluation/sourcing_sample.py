"""The sourcing sample of decision 9.134, as amendment item 38 (g) draws it: labelled development cells per research
stratum, era and type, which the (g) pass reads to check what a count and a date mean (built 28 November 2026; nothing
has been drawn with it).

**Status: an unreviewed draft** (written 28 November 2026, not yet reviewed by the owner). It encodes readings of (g)
and 9.134 the owner has not confirmed, and the definitions neither settles are the required arguments listed below.
Nothing here has been run on real data: no real held-out set has been read with it and no sample has been drawn.

What is ruled.

- Decision 9.134 (the owner, 20 November 2026: "Ok. Add that version as a required step eventually"): "fix the
  held-out split first and permanently, then draw any sourcing sample at random from the training portion alone",
  because the reverse order "lets the held-out set decide what gets sourced". Its status: "the order is ruled; the rule
  binds from the draw of 1.1 and is owed a place in the sourcing scripts". So a sample is drawn only against a
  held-out set already drawn, which held_out_perturbation_ids refuses unless it was drawn on the evidence table and
  label selection the sample is drawn on, and only from the cells of perturbations outside it. Beyond the strata and
  eras, which are cut over the whole table before the draw as (d) and (g) register them, nothing of a held-out cell
  (its label, count, year or stratum) enters which cells are drawn.
- Item 38 (g) (the owner, 23 November 2026: "20 per stratum is fine, classes and limit ok"): "20 labelled cells per
  research stratum, per era and per type, drawn by a seeded rule from development perturbations only after the
  held-out set is fixed (decision 9.134), are read by the pass; where a stratum holds fewer than 20 labelled
  development cells, all of them are read and the number is reported."

What it reuses rather than restates. The strata and the eras are the per-cell assignment that
experiments/write_research_strata_and_eras.py writes before the draw (research_strata_and_eras.read_cells, with the
readings and orders of research_strata_and_eras.READING_COLUMNS), and draw_sourcing_sample_from_files checks that
assignment against the SHA-256 its record holds. A cell is a perturbation against a scored symptom of that assignment,
a labelled cell is one of its kept positives (``kept_positive``; a pair a label selection set aside is "no labelled
pair", as that module reads it), and a cell's type is its ``perturbation_type``. The held-out set is read in the format
experiments/draw_lockbox.py writes (configs/lockbox_v2.json), which experiments/draw_held_out_set.py also writes:
``evidence_records_sha256``, ``label_selection_sha256`` and ``perturbation_ids``.

What follows from (g) and is therefore not a choice here, each stated so that it can be corrected:

- SAMPLE_SIZE_PER_STRATUM is 20, and a quota cell with 20 candidates or fewer has all of them drawn, its number
  reported.
- A cell is a candidate only when it has a counted record (``record_count`` above zero): "For each cell the earliest
  counted record is read", and "A cell is **none** when no record counts", so a none cell (and a cell with no record
  in a lower third) has nothing to read. Such labelled development cells are counted in their quota cell, as
  without_a_counted_record, and not drawn. A cell left out of the strata as not searched
  (research_strata_and_eras.NOT_IN_THE_READING) is in no stratum, so in no quota cell; it is counted by type.
- Within a quota cell the candidates are put in order by perturbation_id and symptom, and the sample is the first
  SAMPLE_SIZE_PER_STRATUM of numpy.random.Generator.permutation over them, the idiom experiments/draw_lockbox.py
  orders its groups by, so that one seed gives one sample.

What it leaves to the caller, because neither (g) nor 9.134 settles it, each a required argument with no default:

- **The seed**, a whole number, 0 or more.
- **The quota unit** (QUOTA_UNITS), what "per research stratum, per era and per type" counts its 20 in. ``crossed``:
  one quota cell per type, stratum and era together. ``apart``: one quota cell per type and stratum and another per
  type and era, drawn separately, so that a cell can be drawn in both (it is read once; the record counts the distinct
  cells). (g) reports the reading "per stratum and per era", which either fits.
- **The stratum reading** (STRATUM_READINGS): the registered strata (``research_stratum``) or the two-stratum form
  reported beside them (``none_against_any``).
- **The era reading** (ERA_READINGS): the thirds of the first-record year (``first_record_era_thirds``) or the two-way
  cut at the end of 2015 (``first_record_era_two_way``). The registered gene date's era
  (``registered_date_era_two_way``) is not offered, since in item 38 (d) "the first-record date is the one the eras
  below are cut on", and it is the date the read record gives.
- **The order of draws** (DRAW_ORDERS). ``one_generator_in_quota_order``: one generator,
  numpy.random.default_rng(seed), over the quota cells in their reporting order (types sorted; within a type, for
  ``crossed`` the strata in their reading's order and within each the eras in theirs, for ``apart`` the stratum quota
  cells and then the era quota cells, each in its reading's order), a quota cell without a candidate drawing nothing.
  ``one_generator_per_quota_cell``: each quota cell its own generator, seeded by the seed and the quota cell's name,
  so that no quota cell's sample depends on which other quota cells exist or how many candidates they hold.

experiments/draw_sourcing_sample.py is the command that runs it on files. Item 37's sourcing draws no sample (9.134:
"that item's own sourcing is exhaustive and draws no sample"), so nothing there calls this.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.evaluation.research_strata_and_eras import (
    NOT_IN_THE_READING, READING_COLUMNS, UNLABELLED_CELL, file_sha256, read_cells)

SAMPLE_SIZE_PER_STRATUM = 20  # item 38 (g): "20 labelled cells per research stratum, per era and per type"
QUOTA_UNITS = ("crossed", "apart")
STRATUM_READINGS = tuple(name for name, (kind, _) in READING_COLUMNS.items() if kind == "cells")
ERA_READINGS = ("first_record_era_thirds", "first_record_era_two_way")
DRAW_ORDERS = ("one_generator_in_quota_order", "one_generator_per_quota_cell")
CELL_COLUMNS_READ = ("perturbation_id", "symptom", "perturbation_type", "kept_positive", "record_count", "earliest_record_year")


def held_out_perturbation_ids(held_out: dict, evidence_records_sha256: str, label_selection_sha256: str | None,
                              perturbation_ids_of_the_table) -> set[str]:
    """The perturbation ids of a held-out set already drawn, refused unless it records the evidence table and label
    selection it was drawn on and they are the ones given (the sample's), and unless every id it names is a perturbation
    of the table and some perturbation of the table is outside it.

    held_out is the parsed file (experiments/draw_lockbox.py's format). Where experiment_data.read_lockbox checks the
    evidence table only when the lockbox records it, this refuses a held-out set that does not, since the check is
    the point."""
    if not isinstance(held_out, dict):
        raise ValueError("the held-out set is not a JSON object in experiments/draw_lockbox.py's format")
    if not held_out.get("evidence_records_sha256"):
        raise ValueError("the held-out set records no evidence_records_sha256, so it cannot be checked against the evidence "
                         "table the sample is drawn on (decision 9.134: the held-out split is fixed first)")
    if "label_selection_sha256" not in held_out:
        raise ValueError("the held-out set records no label_selection_sha256, so it cannot be checked against the label "
                         "selection the sample is drawn on")
    if held_out["evidence_records_sha256"] != evidence_records_sha256:
        raise ValueError(f"the held-out set was drawn on evidence {str(held_out['evidence_records_sha256'])[:12]}, not on the "
                         f"evidence the sample is drawn on ({str(evidence_records_sha256)[:12]})")
    if held_out["label_selection_sha256"] != label_selection_sha256:
        raise ValueError(f"the held-out set was drawn on label selection {str(held_out['label_selection_sha256'])[:12]}, not on "
                         f"the one the sample is drawn on ({str(label_selection_sha256)[:12]})")
    perturbation_ids = held_out.get("perturbation_ids")
    if not isinstance(perturbation_ids, list) or not perturbation_ids:
        raise ValueError("the held-out set names no perturbation_ids; a sample is drawn only once the held-out split is fixed")
    if not all(isinstance(perturbation_id, str) for perturbation_id in perturbation_ids):
        raise ValueError("the held-out set's perturbation_ids are not all strings")
    if len(set(perturbation_ids)) != len(perturbation_ids):
        raise ValueError("the held-out set names a perturbation twice")
    held_out_ids, of_the_table = set(perturbation_ids), set(map(str, perturbation_ids_of_the_table))
    unknown = sorted(held_out_ids - of_the_table)
    if unknown:
        raise ValueError(f"the held-out set names {len(unknown)} perturbations the table does not hold, e.g. {unknown[:3]}: was it "
                         "drawn on another table?")
    if of_the_table <= held_out_ids:
        raise ValueError("the held-out set holds every perturbation of the table, so there is no training portion to draw from")
    return held_out_ids


def _validated_choices(seed, quota_unit: str, stratum_reading: str, era_reading: str, draw_order: str) -> int:
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError(f"the seed must be a whole number, 0 or more, not {seed!r}")
    for name, value, allowed in (("quota_unit", quota_unit, QUOTA_UNITS), ("stratum_reading", stratum_reading, STRATUM_READINGS),
                                 ("era_reading", era_reading, ERA_READINGS), ("draw_order", draw_order, DRAW_ORDERS)):
        if value not in allowed:
            raise ValueError(f"{name} must be one of {allowed}, not {value!r}")
    return int(seed)


def _quota_generator(seed: int, quota_cell: str) -> np.random.Generator:
    """The generator of one quota cell under one_generator_per_quota_cell: seeded by the seed and the quota cell's name."""
    name_key = int.from_bytes(hashlib.sha256(quota_cell.encode()).digest()[:8], "big")
    return np.random.default_rng([seed, name_key])


def draw_sourcing_sample(cells: pd.DataFrame, held_out: dict, *, evidence_records_sha256: str, label_selection_sha256: str | None,
                         seed: int, quota_unit: str, stratum_reading: str, era_reading: str, draw_order: str) -> tuple[pd.DataFrame, dict]:
    """The sample, one row per cell drawn into a quota cell, and its record.

    cells is the per-cell assignment of research_strata_and_eras (assign_strata_and_eras, or read_cells of the file
    experiments/write_research_strata_and_eras.py wrote), made on the evidence table and label selection whose SHA-256
    are given; held_out is the parsed held-out set, checked against them by held_out_perturbation_ids. Every other
    argument is one of the open definitions of the module docstring. A sample row names its quota cell, its stratum
    and era, its count and earliest year, and its draw_position (0 for the first the generator put in order)."""
    seed = _validated_choices(seed, quota_unit, stratum_reading, era_reading, draw_order)
    missing = [column for column in (*CELL_COLUMNS_READ, stratum_reading, era_reading) if column not in cells.columns]
    if missing:
        raise ValueError(f"the cells lack {missing}; they are research_strata_and_eras's per-cell assignment")
    if cells.duplicated(["perturbation_id", "symptom"]).any():
        raise ValueError("the cells repeat a cell")
    held_out_ids = held_out_perturbation_ids(held_out, evidence_records_sha256, label_selection_sha256, cells.perturbation_id)
    in_training = ~cells.perturbation_id.astype(str).isin(held_out_ids)
    labelled_development = cells[in_training & cells.kept_positive.astype(bool)]
    left_out = labelled_development[stratum_reading].astype(str) == NOT_IN_THE_READING
    in_strata = labelled_development[~left_out].copy()
    stratum_order, era_order = READING_COLUMNS[stratum_reading][1], READING_COLUMNS[era_reading][1]
    unknown_strata = sorted(set(in_strata[stratum_reading].astype(str)) - set(stratum_order))
    unknown_eras = sorted(set(in_strata[era_reading].astype(str)) - set(era_order))  # a kept positive is never UNLABELLED_CELL
    if unknown_strata or unknown_eras:
        raise ValueError(f"labelled cells carry strata {unknown_strata} or eras {unknown_eras} that research_strata_and_eras does not "
                         f"give under {stratum_reading} and {era_reading} (an era of {UNLABELLED_CELL!r} is not a kept positive's)")
    in_strata["has_a_counted_record"] = in_strata.record_count.fillna(0).astype(int) > 0
    families = [(stratum_reading, era_reading)] if quota_unit == "crossed" else [(stratum_reading,), (era_reading,)]
    rank = {stratum_reading: {value: position for position, value in enumerate(stratum_order)},
            era_reading: {value: position for position, value in enumerate(era_order)}}
    quota_cells = []  # (perturbation type, family position, ranks, key) in reporting order
    for perturbation_type in sorted(set(in_strata.perturbation_type.astype(str))):
        of_type = in_strata[in_strata.perturbation_type.astype(str) == perturbation_type]
        for family_position, family in enumerate(families):
            for values, members in of_type.groupby([of_type[column].astype(str) for column in family], sort=False):
                values = values if isinstance(values, tuple) else (values,)
                ranks = tuple(rank[column][value] for column, value in zip(family, values))
                quota_cells.append(((perturbation_type, family_position, ranks), dict(zip(family, values)), members))
    quota_cells.sort(key=lambda entry: entry[0])
    generator = np.random.default_rng(seed) if draw_order == "one_generator_in_quota_order" else None
    rows, quota_records = [], []
    for (perturbation_type, _, _), values, members in quota_cells:
        name = " | ".join([perturbation_type] + [f"{column}={value}" for column, value in values.items()])
        candidates = members[members.has_a_counted_record].sort_values(["perturbation_id", "symptom"], kind="stable")
        drawn = candidates.iloc[0:0]
        if len(candidates):
            order = (generator if generator is not None else _quota_generator(seed, name)).permutation(len(candidates))
            drawn = candidates.iloc[order[:SAMPLE_SIZE_PER_STRATUM]]
        for position, (_, cell) in enumerate(drawn.iterrows()):
            rows.append({"quota_cell": name, "perturbation_id": cell.perturbation_id, "symptom": cell.symptom,
                         "perturbation_type": perturbation_type, "stratum": cell[stratum_reading], "era": cell[era_reading],
                         "record_count": int(cell.record_count), "earliest_record_year": int(cell.earliest_record_year),
                         "draw_position": position})
        quota_records.append({"quota_cell": name, "perturbation_type": perturbation_type, **values,
                              "labelled_development_cells": int(len(members)),
                              "without_a_counted_record": int((~members.has_a_counted_record).sum()),
                              "candidates": int(len(candidates)), "drawn": int(len(drawn)),
                              "all_candidates_drawn": bool(len(drawn) == len(candidates))})
    sample = pd.DataFrame(rows, columns=["quota_cell", "perturbation_id", "symptom", "perturbation_type", "stratum", "era",
                                         "record_count", "earliest_record_year", "draw_position"])
    if sample.perturbation_id.isin(held_out_ids).any():  # impossible by construction; checked because it is the rule
        raise AssertionError("a held-out perturbation was drawn into the sourcing sample")
    record = {
        "what": "the sourcing sample of amendment item 38 (g), drawn from the training portion after the held-out split "
                "was fixed (decision 9.134)",
        "rule": {"sample_size_per_stratum": SAMPLE_SIZE_PER_STRATUM, "seed": seed, "quota_unit": quota_unit,
                 "stratum_reading": stratum_reading, "era_reading": era_reading, "draw_order": draw_order,
                 "candidates": "kept positives of perturbations outside the held-out set with a counted record, in the "
                               "order of perturbation_id and symptom, the sample being the first "
                               f"{SAMPLE_SIZE_PER_STRATUM} of numpy.random.Generator.permutation over them"},
        "held_out_set": {"num_perturbations": len(held_out_ids), "evidence_records_sha256": evidence_records_sha256,
                         "label_selection_sha256": label_selection_sha256},
        "num_development_perturbations": int(cells.loc[in_training, "perturbation_id"].nunique()),
        "labelled_development_cells_left_out_as_not_searched": {
            str(name): int(count) for name, count in labelled_development[left_out].perturbation_type.astype(str).value_counts().sort_index().items()},
        "quota_cells": quota_records,
        "num_rows_drawn": int(len(sample)),
        "num_distinct_cells_to_read": int(len(sample.drop_duplicates(["perturbation_id", "symptom"]))),
    }
    return sample, record


def draw_sourcing_sample_from_files(held_out_path: Path, strata_record_path: Path, cells_path: Path, *, evidence_records_sha256: str,
                                    label_selection_sha256: str | None, seed: int, quota_unit: str, stratum_reading: str,
                                    era_reading: str, draw_order: str) -> tuple[pd.DataFrame, dict]:
    """draw_sourcing_sample on the files: the held-out set, the record experiments/write_research_strata_and_eras.py
    wrote and the cells file it names. Refuses a cells file whose SHA-256 is not the record's, a record (or its
    sha256sum sidecar, when there is one) that does not agree with itself, and a record made on another evidence table
    or label selection than the ones given. The sample's record names every file read with its SHA-256."""
    strata_record_path, cells_path, held_out_path = Path(strata_record_path), Path(cells_path), Path(held_out_path)
    record_sha256 = file_sha256(strata_record_path)
    sidecar = Path(f"{strata_record_path}.sha256")
    if sidecar.exists() and sidecar.read_text().split()[0] != record_sha256:
        raise ValueError(f"{strata_record_path} is not the record its sidecar {sidecar.name} names; it was changed after it was written")
    strata_record = json.loads(strata_record_path.read_text())
    cells_sha256 = file_sha256(cells_path)
    if strata_record.get("cells_sha256") != cells_sha256:
        raise ValueError(f"{cells_path} is not the cells file {strata_record_path} records (cells_sha256)")
    for key, value, what in (("evidence_records_sha256", evidence_records_sha256, "evidence table"),
                             ("label_selection_sha256", label_selection_sha256, "label selection")):
        if strata_record.get(key) != value:
            raise ValueError(f"the strata of {strata_record_path} were written on another {what} ({key}) than the one the sample is drawn on")
    held_out = json.loads(held_out_path.read_text())
    sample, record = draw_sourcing_sample(read_cells(cells_path), held_out, evidence_records_sha256=evidence_records_sha256,
                                          label_selection_sha256=label_selection_sha256, seed=seed, quota_unit=quota_unit,
                                          stratum_reading=stratum_reading, era_reading=era_reading, draw_order=draw_order)
    record["inputs"] = {"held_out_set": str(held_out_path), "held_out_set_sha256": file_sha256(held_out_path),
                        "strata_record": str(strata_record_path), "strata_record_sha256": record_sha256,
                        "cells": str(cells_path), "cells_sha256": cells_sha256}
    return sample, record
