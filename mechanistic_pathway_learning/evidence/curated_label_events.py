"""Label events curated by hand from a medicines agency, for drugs neither SIDER 4.1 nor OnSIDES v3.1.1 holds
(decision 9.117 group (ii); the owner, 9 November 2026: "Rule on 9.117 group (ii): build the curated label route").

Why the route exists. A drug becomes a perturbation only by carrying a label one of the two pinned sources holds, so a
drug approved after SIDER's 2015 extraction and absent from OnSIDES has no way in however well its pharmacology is
known: valbenazine, viloxazine, zuranolone, brexanolone, tianeptine, sertindole and levomilnacipran were all out for
that reason alone. This module reads rows a Fable pass curated from the agencies' own labels and turns them into
evidence reports in the schema of evidence/evidence_reports.py, so they join the table beside the SIDER and OnSIDES
slices rather than replacing either.

What the rows are, and what they are not. Each row is one statement of one label: the drug, the agency and the label's
address and version, the section, the term as the label prints it, the MedDRA preferred term where the curator could
give one, the fine construct it maps to, the relation, and the frequency in the drug arm and the placebo arm where the
label tabulates them. A row is not a reading of the drug's pharmacology and carries no target: the targets come from
configs/curated_drug_targets.csv and the additions table, as for any other drug.

The limits this route carries, and why the source string says so on every report:
  - **The rows were read once, by one pass, and not by the agencies' own extraction.** SIDER's and OnSIDES's rows come
    from pipelines applied uniformly to thousands of labels; these come from a curator reading a handful. The reading
    is recorded with its address, version and date so it can be checked, and a second agency was sought for each drug.
  - **The drugs are not a sample.** They are the drugs that happened to fall out of both pinned sources, which is a
    function of approval date rather than of pharmacology, so this slice is biased towards recent approvals.
  - **A frequency without a placebo arm cannot be judged** (decision 9.124), and 34 of the 76 committed rows have none.
  - **The UK eMC's terms forbid loading its text into a database**, so no row may cite it; the reader refuses one that
    does. Flupentixol's rows, which rested on it, are not here for a second reason: decision 9.121 A5 found OnSIDES
    holds it as "flupenthixol", so it enters by the ordinary route and curating it would double-count its labels.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

from mechanistic_pathway_learning.evidence.evidence_reports import EvidenceReport, limitations_text

CURATED_LABEL_EVENTS_PATH = Path("configs/curated_label_events.csv")
CURATED_LABEL_SOURCE = "curated-label"
CURATED_INDICATION_SOURCE = "curated-label-indication"
FORBIDDEN_SOURCE_MARKERS = ("eMC", "medicines.org.uk")  # its terms forbid database use (docs/label_source_review.md)
REQUIRED_COLUMNS = ("perturbation_id", "drug", "source", "label_address", "section", "term_as_printed",
                    "target_symptom", "relation", "frequency", "placebo_frequency")


def _fraction(text: str) -> float | None:
    """A percentage as the label prints it ("10.9%", "3") as a fraction, or None when the cell is empty or not a number."""
    cleaned = str(text).strip().rstrip("%").strip()
    if not cleaned:
        return None
    try:
        value = float(cleaned)
    except ValueError:
        return None
    return value / 100.0 if 0.0 <= value <= 100.0 else None


def read_curated_label_events(path: Path = CURATED_LABEL_EVENTS_PATH) -> list[dict]:
    """The rows of configs/curated_label_events.csv, checked. Every row must name its perturbation, its agency source,
    the label's address, the section, the term, a target symptom and a relation; a row citing a source whose terms
    forbid database use is refused, as is an unknown relation."""
    rows: list[dict] = []
    with open(path, encoding="utf-8", newline="") as events_file:
        for row in csv.DictReader(events_file):
            missing = [column for column in REQUIRED_COLUMNS if not str(row.get(column, "")).strip()
                       and column not in ("frequency", "placebo_frequency")]
            if missing:
                raise ValueError(f"{path}: a row of {row.get('drug')!r} leaves {missing} empty")
            if row["relation"] not in ("induces", "relieves"):
                raise ValueError(f"{path}: {row['drug']} carries the relation {row['relation']!r}")
            if any(marker in row["source"] for marker in FORBIDDEN_SOURCE_MARKERS):
                raise ValueError(f"{path}: {row['drug']} cites {row['source']!r}, whose terms forbid database use")
            rows.append(row)
    return rows


def curated_label_reports(rows: list[dict], perturbation_nodes_by_id: dict[str, str]) -> list[EvidenceReport]:
    """One report per curated row whose perturbation has graph nodes; a row whose drug has none is dropped, as a SIDER
    drug with no mapped target is.

    A row with a numeric frequency in both arms is evidence_code placebo_controlled_frequency and carries the drug
    arm's frequency, as the SIDER route does; a row with the drug arm alone is frequency; a row with neither is
    label_text. An indication row is label_text, whatever its frequency.
    """
    reports: list[EvidenceReport] = []
    for ordinal, row in enumerate(rows):
        perturbation_nodes = perturbation_nodes_by_id.get(row["perturbation_id"])
        if not perturbation_nodes:
            continue
        drug_arm, placebo_arm = _fraction(row["frequency"]), _fraction(row["placebo_frequency"])
        relieves = row["relation"] == "relieves"
        if relieves or drug_arm is None:
            evidence_code, frequency = "label_text", None
        elif placebo_arm is None:
            evidence_code, frequency = "frequency", drug_arm
        else:
            evidence_code, frequency = "placebo_controlled_frequency", drug_arm
        placebo_controlled = evidence_code == "placebo_controlled_frequency"
        source = CURATED_INDICATION_SOURCE if relieves else CURATED_LABEL_SOURCE
        report = EvidenceReport(
            report_id=f"{source}|{row['perturbation_id']}|{row['label_address']}|{row['target_symptom']}|{ordinal}",
            perturbation_id=row["perturbation_id"], perturbation_type="drug", perturbation_label=row["drug"],
            symptom=row["target_symptom"], relation=row["relation"], evidence_class="pharmacological", source=source,
            report_value=1, source_record_id=row["label_address"], source_record_label=row["source"],
            source_term_id=str(row.get("meddra_preferred_term", "")), source_term_label=row["term_as_printed"],
            evidence_code=evidence_code,
            model_description=f"human; drug label curated by hand from {row['source']}; section {row['section']}",
            frequency=frequency, frequency_denominator=None, placebo_flag=placebo_controlled,
            onset=None, sex=None, references="", pubmed_reference_count=0,
            evidence_date=str(row.get("effective_date", "")) or None,
            rubric_log_sample_size=0.0, rubric_frequency_known=1.0 if frequency is not None else 0.0,
            rubric_evidence_code_pcs=0.0, rubric_evidence_code_tas=0.0, rubric_evidence_code_iea=0.0,
            rubric_placebo_controlled=1.0 if placebo_controlled else 0.0, rubric_curated_synopsis=0.0,
            perturbation_nodes=perturbation_nodes,
        )
        report.limitations = "; ".join(filter(None, [
            limitations_text(report),
            "curated by hand from one agency's label, not by the pipeline that reads SIDER and OnSIDES",
            "" if placebo_controlled else "no numeric placebo arm, so the drug arm cannot be judged against one (decision 9.124)",
            "" if str(row.get("second_source_agrees", "")).strip().lower() in ("true", "yes", "agrees") else "no second agency confirms this row",
        ]))
        reports.append(report)
    return reports
