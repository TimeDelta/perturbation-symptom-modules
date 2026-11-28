"""Tests added on 28 November 2026 to kill mutants of mechanistic_pathway_learning/evaluation/research_strata_and_eras.py
that tests/test_research_strata_and_eras.py lets survive (hand-made mutation testing; the mutants and which test kills
each are listed in the session's report). Each test checks the schema or a rule the module docstring states. Synthetic
tables only."""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from mechanistic_pathway_learning.evaluation.research_strata_and_eras import (
    UNLABELLED_CELL, UnexplainedUnsearchedCells, first_record_eras_of_one_type, refuse_unexplained_unsearched_cells, registered_date_eras,
    validated_cell_search_table)
from tests.test_research_strata_and_eras import scored_cell, search_row


@pytest.mark.parametrize("message, row", [
    ("a searched cell without a record_count", search_row("g1", "anxiety", None)),
    ("not a whole number", search_row("g1", "anxiety", "many", 1990)),
    ("a cell not searched but given an earliest_record_year", search_row("g1", "anxiety", None, 1990, status="not_searched", reason="timeout")),
])
def test_the_schema_refuses_what_it_states_a_row_cannot_hold(message, row):
    """The schema: record_count is "integer, 0 or more ... empty when not searched", and earliest_record_year is
    "present exactly when record_count is 1 or more"."""
    with pytest.raises(ValueError, match=message):
        validated_cell_search_table(pd.DataFrame([row]))


def test_a_reason_of_blanks_is_no_reason():
    """not_searched_reason is "empty for a searched cell", and "A cell that was not searched and carries no reason is
    unexplained": a reason of blanks gives no reason either way."""
    table = validated_cell_search_table(pd.DataFrame([search_row("g1", "anxiety", 2, 2001, reason="   "),
                                                      search_row("g1", "fatigue", None, status="not_searched", reason="  ")]))
    assert table.not_searched_reason.tolist() == ["", ""]
    scored = pd.DataFrame([scored_cell("g1", "anxiety", "gene"), scored_cell("g1", "fatigue", "gene")])
    with pytest.raises(UnexplainedUnsearchedCells, match="1 are marked not searched with no reason"):
        refuse_unexplained_unsearched_cells(table, scored)


def test_a_search_row_of_a_symptom_the_scored_table_does_not_hold_is_refused():
    """refuse_unexplained_unsearched_cells: "A row naming a perturbation or symptom that scored_cells does not hold at
    all (a search run on another evidence table) is refused too"."""
    scored = pd.DataFrame([scored_cell("g1", "anxiety", "gene")])
    search = validated_cell_search_table(pd.DataFrame([search_row("g1", "anxiety", 1, 2001), search_row("g1", "tremor", 1, 2001)]))
    with pytest.raises(ValueError, match="another evidence table"):
        refuse_unexplained_unsearched_cells(search, scored)


def test_a_first_record_in_2015_is_through_the_end_of_2015():
    """Eras (d): "Each type is also reported two-way at the end of 2015" (TWO_WAY_ERA_CUT, 31 December 2015)."""
    _, two_way, _ = first_record_eras_of_one_type(np.array([2015.0, 2016.0]), np.array([True, True]), np.array([1.0, 1.0]))
    assert two_way.tolist() == ["through_2015", "from_2016"]


def test_an_unlabelled_cell_without_a_registered_date_stays_unlabelled():
    """registered_date_eras: "A gene positive without that date is undated under it"; a cell that is no positive is
    unlabelled whatever its date."""
    ordinals = np.array([0, 0, date(2016, 1, 1).toordinal()])
    assert registered_date_eras(ordinals, np.array([True, False, False])).tolist() == ["undated", UNLABELLED_CELL, UNLABELLED_CELL]
