"""The study sheet's diagrams stay current with the decisions and code they depict (the owner, 5 November 2026).

The guard of experiments/check_study_sheet_diagrams.py: a commit that changes a decision row or a code file a diagram
depicts fails here until the diagram is checked and stamped again with
`PYTHONPATH=. python experiments/check_study_sheet_diagrams.py --stamp <widget id>`.
"""
from __future__ import annotations

import pytest

from experiments import check_study_sheet_diagrams as diagrams

REGISTRY = diagrams.read_registry()


def test_the_registry_is_well_formed():
    assert not diagrams.registry_problems(REGISTRY)


@pytest.mark.parametrize("widget_id", sorted(REGISTRY["diagrams"]))
def test_the_diagram_was_checked_against_what_it_depicts_now(widget_id):
    entry = REGISTRY["diagrams"][widget_id]
    stale = diagrams.stale_items(entry)
    assert not stale, (f"study-sheet diagram {widget_id} ({entry.get('title', '')}) was checked before these changed: {stale}. "
                       "Check it in the doc, correct it there if it is wrong, then run "
                       f"PYTHONPATH=. python experiments/check_study_sheet_diagrams.py --stamp {widget_id}")


def test_a_pair_is_one_built_and_one_decided_diagram():
    registry = {"diagrams": {"a": {"state": "built", "partner": "b"}, "b": {"state": "built", "partner": "a"}}}
    assert any("one built and one decided" in problem for problem in diagrams.registry_problems(registry))


def test_a_diagram_showing_both_states_needs_no_partner():
    registry = {"diagrams": {"a": {"state": "built_and_decided"}}}
    assert not diagrams.registry_problems(registry)


def test_a_changed_decision_row_makes_its_diagram_stale(tmp_path, monkeypatch):
    log = tmp_path / "open_decisions.md"
    log.write_text("| 9.1 | first text | open |\n", encoding="utf-8")
    monkeypatch.setattr(diagrams, "DECISION_LOG_PATH", log)
    entry = {"depicts": {"decisions": ["9.1"]}}
    entry["fingerprints"] = diagrams.current_fingerprints(entry["depicts"])
    assert not diagrams.stale_items(entry)
    log.write_text("| 9.1 | first text **Added:** more | open |\n", encoding="utf-8")
    assert diagrams.stale_items(entry) == ["decision:9.1"]


def test_a_struck_row_is_still_found(tmp_path, monkeypatch):
    log = tmp_path / "open_decisions.md"
    log.write_text("| ~~9.2~~ | closed text | closed |\n", encoding="utf-8")
    monkeypatch.setattr(diagrams, "DECISION_LOG_PATH", log)
    assert diagrams.decision_row_text("9.2").startswith("| ~~9.2~~")
