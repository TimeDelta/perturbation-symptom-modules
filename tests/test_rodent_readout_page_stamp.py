"""experiments/map_rodent_readout_human_evidence.py writes its page under a provenance stamp naming the committed files it
reads, checked with the page redirected to a temporary directory and nothing in the repository rewritten."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from mechanistic_pathway_learning.documentation import REPOSITORY_ROOT, parse_stamp

sys.path.insert(0, str(REPOSITORY_ROOT / "experiments"))
import map_rodent_readout_human_evidence as rodent_generator  # noqa: E402


def test_the_stamp_names_the_committed_inputs_or_the_pubmed_file_it_was_given():
    committed = rodent_generator.page_stamp(None)
    for input_path in ("docs/generated/rodent_readout_human_evidence.json", "docs/generated/rodent_readout_human_evidence_references.json",
                       "docs/generated/rodent_readout_human_evidence_checks.json", "experiments/scope_open_targets_symptom_labels.py"):
        assert input_path in committed, input_path
    rechecked = rodent_generator.page_stamp(Path("pubmed_records.json"))
    assert "pubmed_records.json" in rechecked and "rodent_readout_human_evidence_checks.json" not in rechecked


def test_the_page_carries_the_stamp_under_its_title(tmp_path, monkeypatch):
    redirected_page = tmp_path / "rodent_readout_human_evidence.md"
    monkeypatch.setattr(rodent_generator, "DOCUMENT_FILE", redirected_page)
    evidence = json.loads(rodent_generator.EVIDENCE_FILE.read_text())
    reference_records = json.loads(rodent_generator.REFERENCE_FILE.read_text())
    patterns, animal_readout_pattern, species_ambiguous_pattern = rodent_generator.symptom_patterns()
    checks = rodent_generator.check_references(evidence["claims"], reference_records, None)  # reads the committed checks, writes nothing
    rows = rodent_generator.claim_rows(evidence["claims"], patterns)
    stamp = rodent_generator.page_stamp(None)
    rodent_generator.write_document(evidence, rows, checks, reference_records, animal_readout_pattern, species_ambiguous_pattern, stamp)
    lines = redirected_page.read_text().splitlines()
    assert lines[0] == "# Human evidence for the rodent-only target safety claims" and lines[2] == stamp
    assert parse_stamp("\n".join(lines))["generator"] == "experiments/map_rodent_readout_human_evidence.py"
