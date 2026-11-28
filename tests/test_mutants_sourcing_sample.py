"""Tests added on 28 November 2026 to kill mutants of mechanistic_pathway_learning/evaluation/sourcing_sample.py that
tests/test_sourcing_sample.py lets survive (hand-made mutation testing; the mutants and which test kills each are listed
in the working report of the session of 28 November 2026, which is outside the repository). Each test checks what the module docstring says the code does; the open definitions stay
arguments. Synthetic tables only: no real held-out set is read and nothing real is drawn."""
from __future__ import annotations

import itertools

import numpy as np
import pytest

from mechanistic_pathway_learning.evaluation.research_strata_and_eras import READING_COLUMNS, file_sha256
from mechanistic_pathway_learning.evaluation.sourcing_sample import (
    DRAW_ORDERS, QUOTA_UNITS, SAMPLE_SIZE_PER_STRATUM, _quota_generator, draw_sourcing_sample_from_files, held_out_perturbation_ids)
from tests.test_sourcing_sample import CHOICES, EVIDENCE, SELECTION, draw, held_out_set, synthetic_cells, write_inputs

REGISTERED_SAMPLE_SIZE = 20  # item 38 (g): "20 labelled cells per research stratum, per era and per type"


@pytest.fixture(scope="module")
def cells():
    return synthetic_cells()


def test_the_sample_size_is_item_38_gs_twenty():
    assert SAMPLE_SIZE_PER_STRATUM == REGISTERED_SAMPLE_SIZE


def the_rule_as_the_docstring_states_it(cells, held_out, seed, quota_unit, stratum_reading, era_reading, draw_order):
    """The quota cells in reporting order and the rows drawn, written out from the module docstring alone: candidates
    are the kept positives of perturbations outside the held-out set, in a stratum, with a counted record; quota cells
    are reported with the types sorted and, within a type, for crossed the strata in their reading's order and within
    each the eras in theirs, for apart the stratum quota cells and then the era quota cells; within a quota cell the
    candidates are ordered by perturbation_id and symptom and the sample is the first 20 of
    Generator.permutation over them, the generator being numpy.random.default_rng(seed) shared in quota order, or the
    quota cell's own (_quota_generator); a quota cell without a candidate draws nothing."""
    labelled_development = cells[~cells.perturbation_id.isin(held_out["perturbation_ids"]) & cells.kept_positive.astype(bool)
                                 & (cells[stratum_reading] != "")]
    families = [(stratum_reading, era_reading)] if quota_unit == "crossed" else [(stratum_reading,), (era_reading,)]
    order_of_reading = {stratum_reading: READING_COLUMNS[stratum_reading][1], era_reading: READING_COLUMNS[era_reading][1]}
    shared_generator = np.random.default_rng(seed) if draw_order == "one_generator_in_quota_order" else None
    quota_names, drawn_rows = [], []
    for perturbation_type in sorted(set(labelled_development.perturbation_type)):
        of_type = labelled_development[labelled_development.perturbation_type == perturbation_type]
        for family in families:
            for values in itertools.product(*(order_of_reading[column] for column in family)):
                members = of_type
                for column, value in zip(family, values):
                    members = members[members[column] == value]
                if members.empty:
                    continue
                name = " | ".join([perturbation_type] + [f"{column}={value}" for column, value in zip(family, values)])
                quota_names.append(name)
                candidates = members[members.record_count.fillna(0) > 0].sort_values(["perturbation_id", "symptom"])
                if candidates.empty:
                    continue
                generator = shared_generator if shared_generator is not None else _quota_generator(seed, name)
                for position, row in enumerate(generator.permutation(len(candidates))[:REGISTERED_SAMPLE_SIZE]):
                    drawn_rows.append((name, candidates.perturbation_id.iloc[row], candidates.symptom.iloc[row], position))
    return quota_names, drawn_rows


@pytest.mark.parametrize("quota_unit", QUOTA_UNITS)
@pytest.mark.parametrize("draw_order", DRAW_ORDERS)
@pytest.mark.parametrize("readings", [("research_stratum", "first_record_era_thirds"), ("none_against_any", "first_record_era_two_way")])
def test_the_sample_is_the_rule_the_docstring_states(cells, quota_unit, draw_order, readings):
    stratum_reading, era_reading = readings
    held_out = held_out_set(cells)
    sample, record = draw(cells, held_out, seed=0, quota_unit=quota_unit, draw_order=draw_order,
                          stratum_reading=stratum_reading, era_reading=era_reading)  # seed 0 is "a whole number, 0 or more"
    quota_names, drawn_rows = the_rule_as_the_docstring_states_it(cells, held_out, 0, quota_unit, stratum_reading, era_reading, draw_order)
    assert [quota["quota_cell"] for quota in record["quota_cells"]] == quota_names
    assert list(zip(sample.quota_cell, sample.perturbation_id, sample.symptom, sample.draw_position)) == drawn_rows
    assert record["held_out_set"]["num_perturbations"] == len(held_out["perturbation_ids"])


def test_a_numpy_integer_seed_draws_what_the_same_whole_number_draws(cells):
    first, _ = draw(cells, seed=np.int64(5))
    second, _ = draw(cells, seed=5)
    assert first.equals(second)


def test_a_held_out_set_that_is_not_an_object_or_records_an_empty_digest_is_refused(cells):
    """held_out_perturbation_ids: refused unless it "records the evidence table and label selection it was drawn on";
    held_out is "the parsed file (experiments/draw_lockbox.py's format)", an object whose perturbation_ids is a list."""
    table = set(cells.perturbation_id)
    good = held_out_set(cells)
    with pytest.raises(ValueError, match="not a JSON object"):
        held_out_perturbation_ids([good], EVIDENCE, SELECTION, table)
    with pytest.raises(ValueError, match="records no evidence_records_sha256"):
        held_out_perturbation_ids({**good, "evidence_records_sha256": ""}, EVIDENCE, SELECTION, table)
    with pytest.raises(ValueError, match="names no perturbation_ids"):
        held_out_perturbation_ids({**good, "perturbation_ids": {identifier: True for identifier in good["perturbation_ids"]}},
                                  EVIDENCE, SELECTION, table)


def test_a_strata_record_without_a_sidecar_is_read_and_named_by_its_digest(tmp_path, cells):
    """draw_sourcing_sample_from_files checks the sidecar "when there is one", and "The sample's record names every
    file read with its SHA-256"."""
    inputs = write_inputs(tmp_path, cells)
    (tmp_path / "strata_record.json.sha256").unlink()
    digests = {key: inputs[key] for key in ("evidence_records_sha256", "label_selection_sha256")}
    _, record = draw_sourcing_sample_from_files(inputs["held_out"], inputs["record"], inputs["cells"], **digests, **CHOICES)
    assert record["inputs"] == {"held_out_set": str(inputs["held_out"]), "held_out_set_sha256": file_sha256(inputs["held_out"]),
                                "strata_record": str(inputs["record"]), "strata_record_sha256": file_sha256(inputs["record"]),
                                "cells": str(inputs["cells"]), "cells_sha256": file_sha256(inputs["cells"])}


def test_each_sample_row_names_the_drawn_cells_own_stratum_era_count_and_year(cells):
    """draw_sourcing_sample: "A sample row names its quota cell, its stratum and era, its count and earliest year".
    (Added by the checker of 28 November 2026: a mutant writing the year into record_count survived.)"""
    sample, _ = draw(cells)
    assert len(sample)
    joined = sample.merge(cells, on=["perturbation_id", "symptom"], suffixes=("", "_of_the_cell"), validate="many_to_one")
    assert (joined.record_count == joined.record_count_of_the_cell.astype(int)).all()
    assert (joined.earliest_record_year == joined.earliest_record_year_of_the_cell.astype(int)).all()
    assert (joined.stratum == joined[CHOICES["stratum_reading"]]).all() and (joined.era == joined[CHOICES["era_reading"]]).all()
    assert (joined.perturbation_type == joined.perturbation_type_of_the_cell).all()
