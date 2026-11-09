"""The curated label route of decision 9.117 group (ii), ruled by the owner on 9 November 2026."""
import csv
from pathlib import Path

import pytest

from mechanistic_pathway_learning.evidence.curated_label_events import (
    CURATED_LABEL_EVENTS_PATH,
    curated_label_reports,
    read_curated_label_events,
)

COLUMNS = ("perturbation_id", "drug", "source", "label_address", "label_version", "effective_date", "read_on",
           "section", "term_as_printed", "meddra_preferred_term", "target_symptom", "relation", "frequency",
           "placebo_frequency", "second_source", "second_source_agrees", "note")


def write_rows(path: Path, rows: list[dict]) -> Path:
    with open(path, "w", encoding="utf-8", newline="") as events_file:
        writer = csv.DictWriter(events_file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows({column: row.get(column, "") for column in COLUMNS} for row in rows)
    return path


def row(**overrides) -> dict:
    base = {"perturbation_id": "CID1", "drug": "d", "source": "DailyMed SPL (X)", "label_address": "https://example/x",
            "section": "6.1", "term_as_printed": "Somnolence", "target_symptom": "somnolence_or_hypersomnia",
            "relation": "induces", "frequency": "", "placebo_frequency": ""}
    return {**base, **overrides}


def test_a_row_with_both_arms_is_placebo_controlled_and_one_without_is_label_text(tmp_path: Path) -> None:
    rows = read_curated_label_events(write_rows(tmp_path / "events.csv", [
        row(frequency="10.9%", placebo_frequency="4.2%"), row(frequency="21"), row(),
        row(relation="relieves", frequency="30%", placebo_frequency="10%"),
    ]))
    reports = curated_label_reports(rows, {"CID1": '[["GENE:X", -1.0, 1.0]]'})
    assert [report.evidence_code for report in reports] == ["placebo_controlled_frequency", "frequency", "label_text", "label_text"]
    assert [report.frequency for report in reports] == [pytest.approx(0.109), pytest.approx(0.21), None, None]
    assert [report.placebo_flag for report in reports] == [True, False, False, False]
    assert reports[3].source == "curated-label-indication" and reports[0].source == "curated-label"
    assert "no numeric placebo arm" in reports[1].limitations and "no numeric placebo arm" not in reports[0].limitations
    assert all("curated by hand" in report.limitations for report in reports)


def test_a_drug_with_no_graph_nodes_is_dropped(tmp_path: Path) -> None:
    """Tianeptine's rows fall out this way: no source files a mechanism target for it, only a measured affinity."""
    rows = read_curated_label_events(write_rows(tmp_path / "events.csv", [row(), row(perturbation_id="CID2")]))
    assert [report.perturbation_id for report in curated_label_reports(rows, {"CID1": '[["GENE:X", -1.0, 1.0]]'})] == ["CID1"]


def test_a_row_citing_the_uk_emc_or_leaving_a_field_empty_is_refused(tmp_path: Path) -> None:
    """The eMC's terms forbid loading its text into a database (docs/label_source_review.md)."""
    with pytest.raises(ValueError, match="forbid database use"):
        read_curated_label_events(write_rows(tmp_path / "a.csv", [row(source="UK eMC SmPC (Depixol)")]))
    with pytest.raises(ValueError, match="leaves"):
        read_curated_label_events(write_rows(tmp_path / "b.csv", [row(target_symptom="")]))
    with pytest.raises(ValueError, match="relation"):
        read_curated_label_events(write_rows(tmp_path / "c.csv", [row(relation="causes")]))


def test_the_committed_rows_are_well_formed_and_cite_no_forbidden_source() -> None:
    rows = read_curated_label_events(CURATED_LABEL_EVENTS_PATH)
    assert len(rows) == 76
    assert sorted({r["drug"] for r in rows}) == ["brexanolone", "levomilnacipran", "sertindole", "tianeptine", "viloxazine", "zuranolone"]
    assert "flupentixol" not in {r["drug"] for r in rows}  # it enters by OnSIDES as "flupenthixol" (decision 9.121 A5)
    assert all(r["label_address"].startswith("http") for r in rows)
    assert sum(1 for r in rows if r["placebo_frequency"].strip()) == 42
