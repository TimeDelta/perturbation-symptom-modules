"""ChEMBL action conflicts (the owner's ruling of 20 November 2026: "always flag for curation instead").

When one drug's mechanism rows give one target more than one action type, mechanism_targets chooses none: a row of
configs/chembl_action_conflict_resolutions.csv decides it, and without one the target is withheld and reported.
"""
from __future__ import annotations

import csv

import pandas as pd
import pytest

from mechanistic_pathway_learning.evidence.assemble_evidence_table import sider_drug_targets
from mechanistic_pathway_learning.evidence.load_onsides_label_events import ACTION_CONFLICT_REASON, qualify_ingredient
from mechanistic_pathway_learning.evidence.onsides_identifier_bridge import IngredientBridge
from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import (
    ACTION_CONFLICT_RESOLUTION_COLUMNS,
    ACTION_CONFLICTS_REPORT_COLUMNS,
    CHEMBL_ACTION_CONFLICT_RESOLUTIONS_PATH,
    ChemblCaches,
    DrugTarget,
    action_conflict_report_rows,
    has_dominant_target,
    mechanism_targets,
    mechanisms_by_parent_and_molecule,
    read_action_conflict_resolutions,
    withheld_count,
    write_action_conflicts_report,
)

# Toy rows shaped like varenicline's in ChEMBL_37: a salt form's AGONIST row and the parent's PARTIAL AGONIST row on
# one receptor target, and a second target both rows agree on.
MECHANISMS = [
    {"molecule_chembl_id": "CHEMBL9001", "parent_molecule_chembl_id": "CHEMBL900", "target_chembl_id": "CHEMBL_T1", "action_type": "AGONIST", "mec_id": 1},
    {"molecule_chembl_id": "CHEMBL900", "parent_molecule_chembl_id": "CHEMBL900", "target_chembl_id": "CHEMBL_T1", "action_type": "PARTIAL AGONIST", "mec_id": 2},
    {"molecule_chembl_id": "CHEMBL900", "parent_molecule_chembl_id": "CHEMBL900", "target_chembl_id": "CHEMBL_T2", "action_type": "INHIBITOR", "mec_id": 3},
    {"molecule_chembl_id": "CHEMBL9001", "parent_molecule_chembl_id": "CHEMBL900", "target_chembl_id": "CHEMBL_T2", "action_type": "inhibitor", "mec_id": 4},
]
TARGETS = {
    "CHEMBL_T1": {"organism": "Homo sapiens", "gene_symbols": ["CHRNA4", "CHRNB2"], "target_type": "PROTEIN COMPLEX", "pref_name": "toy receptor"},
    "CHEMBL_T2": {"organism": "Homo sapiens", "gene_symbols": ["SLC6A4"], "target_type": "SINGLE PROTEIN", "pref_name": "toy transporter"},
}


def write_resolutions(path, rows) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ACTION_CONFLICT_RESOLUTION_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


def test_a_conflict_without_a_resolution_is_withheld_and_reported() -> None:
    conflicts: list = []
    kept = mechanism_targets(["CHEMBL900"], mechanisms_by_parent_and_molecule(MECHANISMS), TARGETS, action_resolutions={}, conflicts=conflicts)
    assert [(target.target_chembl_id, target.sign) for target in kept] == [("CHEMBL_T2", -1.0)]  # case alone is no conflict
    conflict, = conflicts
    assert conflict.target_chembl_id == "CHEMBL_T1" and conflict.withheld and conflict.resolved_action is None
    assert conflict.action_types == ("AGONIST", "PARTIAL AGONIST") and conflict.gene_symbols == ("CHRNA4", "CHRNB2")
    assert conflict.mechanism_rows == ("CHEMBL9001:AGONIST:1", "CHEMBL900:PARTIAL AGONIST:2")
    assert withheld_count(conflicts) == 1
    row, = action_conflict_report_rows("CID1", "toy drug", "SIDER CID 1", conflicts)
    assert row["status"] == "withheld" and row["target_chembl_id"] == "CHEMBL_T1" and set(row) == set(ACTION_CONFLICTS_REPORT_COLUMNS)


def test_a_withheld_target_counts_against_the_single_target_rule() -> None:
    kept = [DrugTarget("CHEMBL_T2", "INHIBITOR", ["SLC6A4"])]
    assert has_dominant_target(kept, 1) and not has_dominant_target(kept, 1, withheld_targets=1)  # two targets, one withheld: not single
    assert has_dominant_target(kept, None, withheld_targets=1)  # the cap lifted, the kept target enters
    assert not has_dominant_target([], None, withheld_targets=1)  # a drug needs a kept target


def test_a_resolution_row_sets_the_action(tmp_path) -> None:
    path = tmp_path / "resolutions.csv"
    write_resolutions(path, [{"drug_chembl_id": "CHEMBL900", "target_chembl_id": "CHEMBL_T1", "chosen_action": "partial agonist",
                              "sources": "toy source one; toy source two", "note": "toy"}])
    resolutions = read_action_conflict_resolutions(path)
    conflicts: list = []
    kept = mechanism_targets(["CHEMBL900"], mechanisms_by_parent_and_molecule(MECHANISMS), TARGETS, action_resolutions=resolutions, conflicts=conflicts)
    assert {target.target_chembl_id: (target.action_type, target.sign) for target in kept} == {"CHEMBL_T1": ("PARTIAL AGONIST", 0.5), "CHEMBL_T2": ("inhibitor", -1.0)}
    conflict, = conflicts
    assert not conflict.withheld and conflict.resolved_action == "PARTIAL AGONIST" and conflict.resolution_drug_chembl_id == "CHEMBL900"
    assert withheld_count(conflicts) == 0
    assert action_conflict_report_rows("CID1", "toy drug", "SIDER CID 1", conflicts)[0]["status"] == "resolved"


def test_rows_that_agree_are_unchanged_and_report_nothing() -> None:
    agreeing = [mechanism for mechanism in MECHANISMS if mechanism["target_chembl_id"] == "CHEMBL_T2"]
    conflicts: list = []
    kept = mechanism_targets(["CHEMBL900", "CHEMBL9001"], mechanisms_by_parent_and_molecule(agreeing), TARGETS, action_resolutions={}, conflicts=conflicts)
    assert len(kept) == 1 and kept[0].target_chembl_id == "CHEMBL_T2" and kept[0].gene_symbols == ["SLC6A4"]
    assert conflicts == []
    one_row = [MECHANISMS[1]]  # one row reached through the salt and the parent keys is one row, not two
    assert [target.action_type for target in mechanism_targets(["CHEMBL900", "CHEMBL9001"], mechanisms_by_parent_and_molecule(one_row), TARGETS,
                                                               action_resolutions={}, conflicts=conflicts)] == ["PARTIAL AGONIST"]
    assert conflicts == []


def test_a_withheld_target_keeps_the_sider_drug_from_the_fallbacks() -> None:
    caches = ChemblCaches({"1": ["CHEMBL900"]}, mechanisms_by_parent_and_molecule(MECHANISMS[:2]), TARGETS, action_resolutions={})
    other_parent = mechanisms_by_parent_and_molecule([{"molecule_chembl_id": "CHEMBL777", "parent_molecule_chembl_id": "CHEMBL777", "target_chembl_id": "CHEMBL_T2",
                                                       "action_type": "INHIBITOR", "mec_id": 9}])
    caches.mechanisms_by_molecule.update(other_parent)
    conflicts: list = []
    assert sider_drug_targets(1, caches, {1: ["CHEMBL777"]}, {1: ["toy_metabolite"]}, {}, conflicts) == []  # neither the bridge parent nor the graph compound
    assert withheld_count(conflicts) == 1
    no_conflict = ChemblCaches({"1": ["CHEMBL555"]}, caches.mechanisms_by_molecule, TARGETS, action_resolutions={})
    assert [target.target_chembl_id for target in sider_drug_targets(1, no_conflict, {1: ["CHEMBL777"]}, {}, {})] == ["CHEMBL_T2"]  # the fallback as before


def test_an_ingredient_left_without_a_target_fails_for_the_conflict() -> None:
    bridge = IngredientBridge("591622", "toy ingredient", "RXCUI", "unii_unichem", chembl_parent="CHEMBL900", atc_codes_rxnav=["N07BA03"], perturbation_id="CID1")
    curated = {"CID1": [DrugTarget("CURATED:CHRNA4", "AGONIST", ["CHRNA4"])]}
    qualification = qualify_ingredient(bridge, mechanisms_by_parent_and_molecule(MECHANISMS[:2]), TARGETS, max_drug_targets=None,
                                       curated_targets_by_perturbation=curated, action_resolutions={})
    assert not qualification.qualifies and qualification.reason == ACTION_CONFLICT_REASON
    assert qualification.drug_targets == [] and qualification.target_source == "ChEMBL"  # the curated fallback is for a drug ChEMBL gives no target
    assert [conflict.target_chembl_id for conflict in qualification.action_conflicts] == ["CHEMBL_T1"]


def test_the_report_is_written_once_per_row_and_with_a_header_when_empty(tmp_path) -> None:
    conflicts: list = []
    mechanism_targets(["CHEMBL900"], mechanisms_by_parent_and_molecule(MECHANISMS), TARGETS, action_resolutions={}, conflicts=conflicts)
    rows = action_conflict_report_rows("CID1", "toy drug", "SIDER CID 1", conflicts)
    write_action_conflicts_report(rows + rows, tmp_path / "conflicts.csv")
    written = pd.read_csv(tmp_path / "conflicts.csv")
    assert list(written.columns) == list(ACTION_CONFLICTS_REPORT_COLUMNS) and len(written) == 1
    write_action_conflicts_report([], tmp_path / "empty.csv")
    assert list(pd.read_csv(tmp_path / "empty.csv").columns) == list(ACTION_CONFLICTS_REPORT_COLUMNS)


def test_the_resolution_table_refuses_rows_it_cannot_apply(tmp_path) -> None:
    good = {"drug_chembl_id": "CHEMBL900", "target_chembl_id": "CHEMBL_T1", "chosen_action": "AGONIST", "sources": "toy", "note": ""}
    for bad, message in (({**good, "chosen_action": "SOMETHING"}, "not an action type"), ({**good, "sources": ""}, "names its sources"),
                         ({**good, "drug_chembl_id": ""}, "needs both")):
        write_resolutions(tmp_path / "bad.csv", [bad])
        with pytest.raises(ValueError, match=message):
            read_action_conflict_resolutions(tmp_path / "bad.csv")
    write_resolutions(tmp_path / "twice.csv", [good, good])
    with pytest.raises(ValueError, match="resolved twice"):
        read_action_conflict_resolutions(tmp_path / "twice.csv")
    (tmp_path / "columns.csv").write_text("drug,target\n", encoding="utf-8")
    with pytest.raises(ValueError, match="columns"):
        read_action_conflict_resolutions(tmp_path / "columns.csv")


def test_the_repository_table_reads_and_is_the_default() -> None:
    resolutions = read_action_conflict_resolutions(CHEMBL_ACTION_CONFLICT_RESOLUTIONS_PATH)
    conflicts: list = []
    kept = mechanism_targets(["CHEMBL900"], mechanisms_by_parent_and_molecule(MECHANISMS), TARGETS, conflicts=conflicts)  # None reads the table
    assert {target.target_chembl_id for target in kept} == {"CHEMBL_T2"} | {key[1] for key in resolutions if key[0] == "CHEMBL900"}
    assert len(conflicts) == 1
