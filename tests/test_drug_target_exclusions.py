"""Ruled removals of drug targets (configs/drug_target_exclusions.csv; map_drug_targets_to_graph_nodes, "A ruled
removal"): a member gene leaving a family target for every drug, or a whole target leaving one drug."""
from __future__ import annotations

import csv

import pytest

from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import (
    DRUG_TARGET_EXCLUSION_COLUMNS,
    DRUG_TARGET_EXCLUSIONS_PATH,
    DrugTargetExclusion,
    GraphNodeLookup,
    check_graph_compounds_have_no_mechanism,
    mechanism_targets,
    mechanisms_by_parent_and_molecule,
    read_drug_target_exclusions,
)

SODIUM_FAMILY = "CHEMBL2331043"
SODIUM_MEMBERS = ["SCN10A", "SCN11A", "SCN1A", "SCN2A", "SCN3A", "SCN4A", "SCN5A", "SCN7A", "SCN8A", "SCN9A"]
TARGETS = {
    SODIUM_FAMILY: {"organism": "Homo sapiens", "gene_symbols": SODIUM_MEMBERS, "target_type": "PROTEIN FAMILY", "pref_name": "Sodium channel alpha subunit"},
    "CHEMBL_GABAA": {"organism": "Homo sapiens", "gene_symbols": ["GABRA1", "GABRB2", "GABRG2"], "target_type": "PROTEIN COMPLEX GROUP", "pref_name": "toy GABA-A"},
    "CHEMBL_NMDA": {"organism": "Homo sapiens", "gene_symbols": ["GRIN1", "GRIN2A"], "target_type": "PROTEIN COMPLEX GROUP", "pref_name": "toy NMDA"},
    "CHEMBL_ONE": {"organism": "Homo sapiens", "gene_symbols": ["SCN7A"], "target_type": "SINGLE PROTEIN", "pref_name": "toy single member"},
}
MECHANISMS = [
    {"molecule_chembl_id": "CHEMBL_DRUG_A", "parent_molecule_chembl_id": "CHEMBL_DRUG_A", "target_chembl_id": SODIUM_FAMILY, "action_type": "BLOCKER", "mec_id": 1},
    {"molecule_chembl_id": "CHEMBL_DRUG_B_SALT", "parent_molecule_chembl_id": "CHEMBL_DRUG_B", "target_chembl_id": "CHEMBL_GABAA", "action_type": "POSITIVE MODULATOR", "mec_id": 2},
    {"molecule_chembl_id": "CHEMBL_DRUG_B_SALT", "parent_molecule_chembl_id": "CHEMBL_DRUG_B", "target_chembl_id": "CHEMBL_NMDA", "action_type": "ANTAGONIST", "mec_id": 3},
    {"molecule_chembl_id": "CHEMBL_DRUG_C", "parent_molecule_chembl_id": "CHEMBL_DRUG_C", "target_chembl_id": "CHEMBL_ONE", "action_type": "AGONIST", "mec_id": 4},
]
BY_MOLECULE = mechanisms_by_parent_and_molecule(MECHANISMS)


def exclusion(drug="", target=SODIUM_FAMILY, gene="", ruling="a ruling", sources="a source") -> DrugTargetExclusion:
    return DrugTargetExclusion(drug, target, gene, ruling, sources)


def write_exclusions(path, rows) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(DRUG_TARGET_EXCLUSION_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


def test_a_member_removed_for_every_drug_leaves_the_family_and_the_magnitude_is_spread_over_the_rest():
    kept = mechanism_targets(["CHEMBL_DRUG_A"], BY_MOLECULE, TARGETS, exclusions=(exclusion(gene="SCN7A"),))
    assert [target.target_chembl_id for target in kept] == [SODIUM_FAMILY]
    assert "SCN7A" not in kept[0].gene_symbols and len(kept[0].gene_symbols) == 9
    lookup = GraphNodeLookup({gene: f"PROTEIN:{gene}" for gene in SODIUM_MEMBERS}, {}, {})
    triples = lookup.perturbation_nodes(kept)
    assert "PROTEIN:SCN7A" not in {node for node, _, _ in triples}
    assert all(magnitude == pytest.approx(1 / 9) for _, _, magnitude in triples) and all(sign == -1.0 for _, sign, _ in triples)
    # without the table the family is spread over all ten, as every build before 20 November 2026 did
    assert len(mechanism_targets(["CHEMBL_DRUG_A"], BY_MOLECULE, TARGETS, exclusions=())[0].gene_symbols) == 10


def test_a_target_removed_whole_for_one_drug_goes_for_that_drug_alone_and_matches_through_the_salt_or_the_parent():
    for drug_ids in (["CHEMBL_DRUG_B"], ["CHEMBL_DRUG_B_SALT"]):
        kept = mechanism_targets(drug_ids, BY_MOLECULE, TARGETS, exclusions=(exclusion(drug="CHEMBL_DRUG_B", target="CHEMBL_GABAA"),))
        assert [target.target_chembl_id for target in kept] == ["CHEMBL_NMDA"]
    other_drug = mechanism_targets(["CHEMBL_DRUG_B"], BY_MOLECULE, TARGETS, exclusions=(exclusion(drug="CHEMBL_OTHER", target="CHEMBL_GABAA"),))
    assert sorted(target.target_chembl_id for target in other_drug) == ["CHEMBL_GABAA", "CHEMBL_NMDA"]


def test_a_target_whose_every_member_is_removed_is_dropped():
    assert mechanism_targets(["CHEMBL_DRUG_C"], BY_MOLECULE, TARGETS, exclusions=(exclusion(target="CHEMBL_ONE", gene="SCN7A"),)) == []


def test_a_compound_whose_every_mechanism_is_removed_carries_none_for_the_graph_compound_guard():
    compounds = {"CHEMBL_DRUG_C": ["MAM00001"]}
    with pytest.raises(ValueError):
        check_graph_compounds_have_no_mechanism(compounds, BY_MOLECULE, exclusions=())
    check_graph_compounds_have_no_mechanism(compounds, BY_MOLECULE, exclusions=(exclusion(drug="CHEMBL_DRUG_C", target="CHEMBL_ONE"),))
    # a member removal does not remove the row, so the guard still refuses
    with pytest.raises(ValueError):
        check_graph_compounds_have_no_mechanism(compounds, BY_MOLECULE, exclusions=(exclusion(target="CHEMBL_ONE", gene="SCN7A"),))


@pytest.mark.parametrize("row, message", [
    ({"drug_chembl_id": "", "target_chembl_id": "", "gene_symbol": "SCN7A", "ruling": "r", "sources": "s", "note": ""}, "names the target"),
    ({"drug_chembl_id": "", "target_chembl_id": SODIUM_FAMILY, "gene_symbol": "", "ruling": "r", "sources": "s", "note": ""}, "a drug, a member gene or both"),
    ({"drug_chembl_id": "", "target_chembl_id": SODIUM_FAMILY, "gene_symbol": "SCN7A", "ruling": "", "sources": "s", "note": ""}, "its ruling and its sources"),
    ({"drug_chembl_id": "", "target_chembl_id": SODIUM_FAMILY, "gene_symbol": "SCN7A", "ruling": "r", "sources": "", "note": ""}, "its ruling and its sources"),
])
def test_the_reader_refuses_a_row_without_its_target_scope_ruling_or_sources(tmp_path, row, message):
    path = tmp_path / "exclusions.csv"
    write_exclusions(path, [row])
    with pytest.raises(ValueError, match=message):
        read_drug_target_exclusions(path)


def test_the_reader_refuses_a_row_given_twice_and_other_columns(tmp_path):
    path = tmp_path / "exclusions.csv"
    row = {"drug_chembl_id": "", "target_chembl_id": SODIUM_FAMILY, "gene_symbol": "SCN7A", "ruling": "r", "sources": "s", "note": ""}
    write_exclusions(path, [row, row])
    with pytest.raises(ValueError, match="twice"):
        read_drug_target_exclusions(path)
    path.write_text("drug,target\nA,B\n")
    with pytest.raises(ValueError, match="columns"):
        read_drug_target_exclusions(path)
    assert read_drug_target_exclusions(tmp_path / "absent.csv") == ()


def test_the_committed_table_reads_and_removes_scn7a_from_the_sodium_channel_family_for_every_drug():
    """Item 37 rulings draft, section 16, item 25: "The SCN7A edge is removed for all 26 drugs that carry it"."""
    exclusions = read_drug_target_exclusions(DRUG_TARGET_EXCLUSIONS_PATH)
    assert any((row.drug_chembl_id, row.target_chembl_id, row.gene_symbol) == ("", SODIUM_FAMILY, "SCN7A") for row in exclusions)
    kept = mechanism_targets(["CHEMBL_DRUG_A"], BY_MOLECULE, TARGETS)  # the default reads the committed table
    assert "SCN7A" not in kept[0].gene_symbols


CHEMBL_DIRECTORY = DRUG_TARGET_EXCLUSIONS_PATH.parents[1] / "data/raw/chembl"
pinned_chembl = pytest.mark.skipif(not (CHEMBL_DIRECTORY / "mechanisms.json").exists() or not (CHEMBL_DIRECTORY / "targets.json").exists(),
                                   reason="the pinned ChEMBL caches are not present (experiments/fetch_chembl_drug_targets.py)")


@pinned_chembl
def test_on_the_pinned_cache_acamprosate_keeps_its_nmda_row_and_loses_the_gaba_a_complex():
    """Item 37 rulings draft, section 14: "remove acamprosate edges" (its 13 GABA-A edges, a sourced negative)."""
    from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import load_chembl_caches

    caches = load_chembl_caches(CHEMBL_DIRECTORY)
    chembl_ids = caches.pubchem_to_chembl.get("71158", [])  # acamprosate, CID 71158
    kept = mechanism_targets(chembl_ids, caches.mechanisms_by_molecule, caches.targets)
    assert {target.target_chembl_id for target in kept} == {"CHEMBL2094124"}
    before = mechanism_targets(chembl_ids, caches.mechanisms_by_molecule, caches.targets, exclusions=())
    assert {target.target_chembl_id for target in before} == {"CHEMBL2094124", "CHEMBL2093872"}


@pinned_chembl
def test_on_the_pinned_cache_scn7a_sits_in_one_target_only():
    """The SCN7A row removes the member from CHEMBL2331043 alone, which holds for every drug only while no other target
    of the pinned cache lists SCN7A (ChEMBL's single-protein target for Nax, CHEMBL3585, carries no mechanism)."""
    import json

    targets = json.loads((CHEMBL_DIRECTORY / "targets.json").read_text())
    assert [target_id for target_id, record in targets.items() if "SCN7A" in (record.get("gene_symbols") or [])] == [SODIUM_FAMILY]
