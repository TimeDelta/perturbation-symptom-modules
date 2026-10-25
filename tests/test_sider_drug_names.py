"""SIDER names that are truncations or codes are corrected in one place (evidence/sider_drug_names.py, decision 9.93)."""
from __future__ import annotations

from mechanistic_pathway_learning.evidence.sider_drug_names import corrected_drug_names, read_corrections, readable_drug_name


def test_vortioxetine_is_named_and_not_lu() -> None:
    assert readable_drug_name("CID109966051", "Lu") == "vortioxetine"


def test_a_name_not_listed_is_kept() -> None:
    assert readable_drug_name("CID100002771", "citalopram") == "citalopram"


def test_a_correction_applies_only_to_the_name_it_was_written_against() -> None:
    # a later SIDER release that names the drug properly keeps its own name
    assert readable_drug_name("CID109966051", "vortioxetine hydrobromide") == "vortioxetine hydrobromide"


def test_every_correction_is_a_lowercase_name_and_differs_from_sider() -> None:
    corrections = read_corrections()
    assert len(corrections) >= 20
    for stitch_flat_id, (sider_name, corrected) in corrections.items():
        assert stitch_flat_id.startswith("CID1")
        assert corrected == corrected.lower() and corrected != sider_name and len(corrected) > 4


def test_the_mapping_helper_applies_the_corrections() -> None:
    assert corrected_drug_names({"CID109966051": "Lu", "CID100002771": "citalopram"}) == {"CID109966051": "vortioxetine", "CID100002771": "citalopram"}
