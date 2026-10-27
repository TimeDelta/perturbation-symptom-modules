"""Guards on docs/open_decisions.md.

Row 9.100 lost eight characters between commits on 26 October 2026, while it was being authored and rewrapped as a
single 11,744-character line: six inside words ("different", "et al.", "under", "project", "a step down", "errors
not corrected") and two bold markers. Asked whether to restructure the log out of its table, the owner chose a
guard and an editing practice instead (27 October 2026). These tests are that guard.
"""
from __future__ import annotations

import re

import pytest

from mechanistic_pathway_learning import documentation
from mechanistic_pathway_learning.documentation import (
    REPOSITORY_ROOT,
    closed_decision_ids,
    decision_ids_in_log,
    decision_ids_owing_nothing,
    refuse_on_shallow_history,
)

LOG_PATH = REPOSITORY_ROOT / "docs" / "open_decisions.md"

# The longest line the log holds on 27 October 2026 is 18,153 characters. This ceiling is a ratchet and not a
# target: the longer a row grows the likelier an edit drops characters from it unnoticed, which is what happened to
# 9.100. Raising it is a decision to take knowingly.
LINE_LENGTH_CEILING = 19_000

# A code span becomes one placeholder character rather than nothing. Stripping it to nothing was a bug in this
# counter on 27 October 2026: a bold run ending in a code span, "**Built as <code>** with", collapsed to "as ** with",
# a space-flanked marker the operator rule below then discarded, which made five rows dense with code spans look
# unpaired when none of them was damaged.
INLINE_CODE = re.compile(r"`[^`]*`")
# "min(n, 2) ** 0.5" in row 9.50 is arithmetic, not emphasis. Markdown emphasis never carries a space on the inside
# of its markers, so a space on both sides means an operator.
EXPONENT_OPERATOR = re.compile(r"\s\*\*\s")
ROW = re.compile(r"^\|\s*(~~)?(?P<id>\d+\.\d+[a-z]?)(~~)?\s*\|")


def emphasis_marker_count(line: str) -> int:
    return EXPONENT_OPERATOR.sub(" ", INLINE_CODE.sub("x", line)).count("**")


def decision_rows() -> list[tuple[int, str, str]]:
    rows = []
    for number, line in enumerate(LOG_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        match = ROW.match(line)
        if match:
            rows.append((number, match.group("id"), line))
    return rows


def test_the_log_still_presents_rows_to_check():
    """A guard that silently finds nothing to guard is no guard; this fails if the format moves under it."""
    assert len(decision_rows()) > 100


def test_no_decision_row_has_an_unmatched_emphasis_marker():
    """Strict, with no baseline. Five rows were held as one until 27 October 2026, when the counter above was
    corrected and all five turned out to pair; no row in the log carries an unmatched marker."""
    unmatched = sorted({identifier for _, identifier, line in decision_rows() if emphasis_marker_count(line) % 2})
    assert not unmatched, (
        "a lost '**' is exactly the two-character loss that damaged row 9.100, and it renders the rest of the row "
        f"bold. Rows with an odd number of markers: {unmatched}"
    )


def test_the_counter_keeps_a_bold_run_that_ends_in_a_code_span():
    """The bug that made five undamaged rows look unpaired: the code span was stripped to nothing, leaving a
    space-flanked marker that the arithmetic rule then discarded."""
    assert emphasis_marker_count("| 9.16 | **Built as `models/forward_cone_divisor.py`** with both kept. |") == 2
    assert emphasis_marker_count("| 9.50 | a weight (strength x min(n, 2) ** 0.5) decides it |") == 0


def test_no_line_is_longer_than_the_recorded_ceiling():
    lengths = {number: len(line) for number, line in enumerate(LOG_PATH.read_text(encoding="utf-8").splitlines(), start=1)}
    too_long = {number: length for number, length in lengths.items() if length > LINE_LENGTH_CEILING}
    assert not too_long, f"lines past the {LINE_LENGTH_CEILING}-character ceiling (line: length): {too_long}"


SUBSECTION_FORM = """## Section nine

### 9.200

**nothing owed**, kept as a record.

### ~~9.201~~

Closed on a date.

### 9.202

Something the owner still owes a ruling on.
"""

TABLE_FORM = """| id | what | status |
| --- | --- | --- |
| 9.200 | what | **nothing owed**, kept as a record. |
| ~~9.201~~ | what | Closed on a date. |
| 9.202 | what | Something the owner still owes a ruling on. |
"""


def test_the_parsers_read_the_subsection_form_as_well_as_the_table_form():
    """So the log can be restructured out of its table later without touching these parsers or the pages."""
    assert decision_ids_in_log(SUBSECTION_FORM) == ["9.200", "9.201", "9.202"]
    assert decision_ids_in_log(TABLE_FORM) == ["9.200", "9.201", "9.202"]
    assert closed_decision_ids(SUBSECTION_FORM) == closed_decision_ids(TABLE_FORM) == {"9.201"}
    assert decision_ids_owing_nothing(SUBSECTION_FORM) == decision_ids_owing_nothing(TABLE_FORM) == {"9.200"}


def test_a_closed_subsection_is_not_counted_as_owing_nothing():
    assert decision_ids_owing_nothing("### ~~9.300~~\n\n**nothing owed** and closed.\n") == set()


def test_the_generators_refuse_a_shallow_clone_and_name_the_fix(monkeypatch):
    monkeypatch.setattr(documentation, "repository_is_shallow", lambda root=REPOSITORY_ROOT: True)
    with pytest.raises(SystemExit) as refusal:
        refuse_on_shallow_history("experiments/generate_status.py")
    assert "shallow" in str(refusal.value) and "--depth" in str(refusal.value)
    assert refuse_on_shallow_history("experiments/generate_status.py", allow_shallow=True) is None
