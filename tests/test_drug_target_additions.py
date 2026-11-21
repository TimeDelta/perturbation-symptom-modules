"""Ruled additions of drug targets (configs/drug_target_additions.csv; map_drug_targets_to_graph_nodes, "A ruled
addition"): a target a ruling adds to a drug whose ChEMBL mechanism rows do not name it, the twin of a ruled removal.
The first rows are cocaine's three monoamine transporters (item 37 rulings draft, section 17, P4, and section 19)."""
from __future__ import annotations

import csv
import json

import pytest

from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import (
    DRUG_TARGET_ADDITION_COLUMNS,
    DRUG_TARGET_ADDITIONS_PATH,
    DrugTargetAddition,
    DrugTargetExclusion,
    GraphNodeLookup,
    check_graph_compounds_have_no_mechanism,
    has_dominant_target,
    mechanism_targets,
    mechanisms_by_parent_and_molecule,
    read_drug_target_additions,
)

SODIUM_FAMILY = "CHEMBL2331043"
SODIUM_MEMBERS = ["SCN10A", "SCN11A", "SCN1A", "SCN2A", "SCN3A", "SCN4A", "SCN5A", "SCN7A", "SCN8A", "SCN9A"]
TARGETS = {
    SODIUM_FAMILY: {"organism": "Homo sapiens", "gene_symbols": SODIUM_MEMBERS, "target_type": "PROTEIN FAMILY", "pref_name": "Sodium channel alpha subunit"},
    "CHEMBL_DAT": {"organism": "Homo sapiens", "gene_symbols": ["SLC6A3"], "target_type": "SINGLE PROTEIN", "pref_name": "toy dopamine transporter"},
    "CHEMBL_SERT": {"organism": "Homo sapiens", "gene_symbols": ["SLC6A4"], "target_type": "SINGLE PROTEIN", "pref_name": "toy serotonin transporter"},
    "CHEMBL_PAIR": {"organism": "Homo sapiens", "gene_symbols": ["GENE1", "GENE2", "GENE3"], "target_type": "PROTEIN COMPLEX", "pref_name": "toy complex"},
    "CHEMBL_RAT": {"organism": "Rattus norvegicus", "gene_symbols": ["Slc6a3"], "target_type": "SINGLE PROTEIN", "pref_name": "toy rat transporter"},
}
MECHANISMS = [
    {"molecule_chembl_id": "CHEMBL_DRUG_SALT", "parent_molecule_chembl_id": "CHEMBL_DRUG", "target_chembl_id": SODIUM_FAMILY, "action_type": "BLOCKER", "mec_id": 1},
    {"molecule_chembl_id": "CHEMBL_COMPOUND", "parent_molecule_chembl_id": "CHEMBL_COMPOUND", "target_chembl_id": "CHEMBL_SERT", "action_type": "INHIBITOR", "mec_id": 2},
]
BY_MOLECULE = mechanisms_by_parent_and_molecule(MECHANISMS)


def addition(drug="CHEMBL_DRUG", target="CHEMBL_DAT", gene="SLC6A3", action="INHIBITOR", affinity=0.23, measure="Ki") -> DrugTargetAddition:
    return DrugTargetAddition(drug, target, gene, action, "a ruling", "a source", affinity, measure)


def write_additions(path, rows) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(DRUG_TARGET_ADDITION_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


def row(**changes) -> dict:
    values = {"drug_chembl_id": "CHEMBL_DRUG", "target_chembl_id": "CHEMBL_DAT", "gene_symbol": "SLC6A3", "action_type": "inhibitor",
              "affinity_um": "0.23", "affinity_measure": "Ki", "ruling": "r", "sources": "s", "note": ""}
    values.update(changes)
    return values


def test_an_addition_is_appended_after_the_chembl_targets_and_matches_through_the_salt_or_the_parent():
    for drug_ids in (["CHEMBL_DRUG"], ["CHEMBL_DRUG_SALT"]):
        kept = mechanism_targets(drug_ids, BY_MOLECULE, TARGETS, exclusions=(), additions=(addition(),))
        assert [target.target_chembl_id for target in kept] == [SODIUM_FAMILY, "CHEMBL_DAT"]
        added = kept[1]
        assert added.gene_symbols == ["SLC6A3"] and added.action_type == "INHIBITOR" and added.sign == -1.0
        assert added.target_type == "SINGLE PROTEIN" and added.pref_name == "toy dopamine transporter"
    # another drug is untouched, and without the table the drug keeps what ChEMBL gives
    assert [target.target_chembl_id for target in mechanism_targets(["CHEMBL_COMPOUND"], BY_MOLECULE, TARGETS, exclusions=(), additions=(addition(),))] == ["CHEMBL_SERT"]
    assert [target.target_chembl_id for target in mechanism_targets(["CHEMBL_DRUG"], BY_MOLECULE, TARGETS, exclusions=(), additions=())] == [SODIUM_FAMILY]


def test_an_added_target_is_seeded_at_magnitude_one_with_its_sign_and_counts_as_a_target():
    kept = mechanism_targets(["CHEMBL_DRUG"], BY_MOLECULE, TARGETS, exclusions=(), additions=(addition(),))
    lookup = GraphNodeLookup({gene: f"PROTEIN:{gene}" for gene in SODIUM_MEMBERS + ["SLC6A3"]}, {}, {})
    triples = {node: (sign, magnitude) for node, sign, magnitude in lookup.perturbation_nodes(kept)}
    assert triples["PROTEIN:SLC6A3"] == (-1.0, 1.0)
    assert triples["PROTEIN:SCN1A"] == (-1.0, pytest.approx(0.1))
    assert has_dominant_target(kept, max_targets=0) and not has_dominant_target(kept, max_targets=1)


def test_a_drug_with_no_mechanism_row_takes_its_addition_alone():
    kept = mechanism_targets(["CHEMBL_NO_ROWS"], BY_MOLECULE, TARGETS, exclusions=(), additions=(addition(drug="CHEMBL_NO_ROWS"),))
    assert [target.target_chembl_id for target in kept] == ["CHEMBL_DAT"]


def test_rows_of_one_target_are_one_target_over_their_genes_in_file_order():
    rows = (addition(target="CHEMBL_PAIR", gene="GENE3", action="ANTAGONIST"), addition(target="CHEMBL_PAIR", gene="GENE1", action="ANTAGONIST"))
    kept = mechanism_targets(["CHEMBL_DRUG"], BY_MOLECULE, TARGETS, exclusions=(), additions=rows)
    assert [(target.target_chembl_id, target.gene_symbols) for target in kept[1:]] == [("CHEMBL_PAIR", ["GENE3", "GENE1"])]


def test_an_addition_of_a_target_the_chembl_rows_name_already_is_refused_kept_or_removed():
    with pytest.raises(ValueError, match="name already"):
        mechanism_targets(["CHEMBL_COMPOUND"], BY_MOLECULE, TARGETS, exclusions=(), additions=(addition(drug="CHEMBL_COMPOUND", target="CHEMBL_SERT", gene="SLC6A4"),))
    removed = (DrugTargetExclusion("CHEMBL_COMPOUND", "CHEMBL_SERT", "", "a ruling", "a source"),)
    with pytest.raises(ValueError, match="name already"):
        mechanism_targets(["CHEMBL_COMPOUND"], BY_MOLECULE, TARGETS, exclusions=removed, additions=(addition(drug="CHEMBL_COMPOUND", target="CHEMBL_SERT", gene="SLC6A4"),))


def test_an_addition_its_own_exclusions_remove_is_refused():
    for exclusion in (DrugTargetExclusion("CHEMBL_DRUG", "CHEMBL_DAT", "", "r", "s"), DrugTargetExclusion("", "CHEMBL_DAT", "SLC6A3", "r", "s")):
        with pytest.raises(ValueError, match="added and removed"):
            mechanism_targets(["CHEMBL_DRUG"], BY_MOLECULE, TARGETS, exclusions=(exclusion,), additions=(addition(),))


@pytest.mark.parametrize("bad, message", [
    (addition(target="CHEMBL_ABSENT"), "holds no record"),
    (addition(target="CHEMBL_RAT", gene="Slc6a3"), "not Homo sapiens"),
    (addition(gene="SLC6A4"), "lists"),
])
def test_an_addition_that_cannot_stand_is_refused_rather_than_dropped(bad, message):
    with pytest.raises(ValueError, match=message):
        mechanism_targets(["CHEMBL_DRUG"], BY_MOLECULE, TARGETS, exclusions=(), additions=(bad,))


def test_the_graph_compound_guard_counts_an_addition_as_a_mechanism():
    compounds = {"CHEMBL_GRAPH_COMPOUND": ["MAM00001"]}
    check_graph_compounds_have_no_mechanism(compounds, BY_MOLECULE, exclusions=(), additions=())
    with pytest.raises(ValueError, match="CHEMBL_GRAPH_COMPOUND"):
        check_graph_compounds_have_no_mechanism(compounds, BY_MOLECULE, exclusions=(), additions=(addition(drug="CHEMBL_GRAPH_COMPOUND"),))


@pytest.mark.parametrize("changes, message", [
    ({"drug_chembl_id": ""}, "the drug, the target and the gene"),
    ({"target_chembl_id": ""}, "the drug, the target and the gene"),
    ({"gene_symbol": ""}, "the drug, the target and the gene"),
    ({"action_type": "BLOCKS"}, "not an action type"),
    ({"ruling": ""}, "its ruling and its sources"),
    ({"sources": ""}, "its ruling and its sources"),
    ({"affinity_um": ""}, "with its quantity type"),
    ({"affinity_measure": ""}, "with its quantity type"),
    ({"affinity_um": "-0.2"}, "not a positive number"),
    ({"affinity_um": "0"}, "not a positive number"),
    ({"affinity_um": "about 0.2"}, "not a positive number"),
    ({"affinity_um": "inf"}, "not a positive number"),
    ({"affinity_measure": "pKi"}, "is not one of"),
])
def test_the_reader_refuses_a_row_without_what_it_must_name(tmp_path, changes, message):
    path = tmp_path / "additions.csv"
    write_additions(path, [row(**changes)])
    with pytest.raises(ValueError, match=message):
        read_drug_target_additions(path)


def test_the_reader_takes_a_row_without_an_affinity_and_upper_cases_the_action(tmp_path):
    path = tmp_path / "additions.csv"
    write_additions(path, [row(affinity_um="", affinity_measure="")])
    (read,) = read_drug_target_additions(path)
    assert read.affinity_um is None and read.affinity_measure is None and read.action_type == "INHIBITOR" and read.sign == -1.0


def test_the_reader_refuses_a_row_given_twice_two_actions_for_one_target_and_other_columns(tmp_path):
    path = tmp_path / "additions.csv"
    write_additions(path, [row(), row()])
    with pytest.raises(ValueError, match="twice"):
        read_drug_target_additions(path)
    write_additions(path, [row(target_chembl_id="CHEMBL_PAIR", gene_symbol="GENE1"),
                           row(target_chembl_id="CHEMBL_PAIR", gene_symbol="GENE2", action_type="AGONIST")])
    with pytest.raises(ValueError, match="the actions"):
        read_drug_target_additions(path)
    path.write_text("drug,target\nA,B\n")
    with pytest.raises(ValueError, match="columns"):
        read_drug_target_additions(path)
    assert read_drug_target_additions(tmp_path / "absent.csv") == ()


def test_two_ids_of_one_drug_cannot_smuggle_a_second_action_or_a_repeated_gene_past_the_reader(tmp_path):
    """The reader compares rows by their drug_chembl_id string, so rows keyed by a salt and by its parent look like two
    drugs to it; added_targets, which holds every id of the one drug, refuses the pair rather than letting rows[0] win
    (the action) or the gene be seeded twice at half the magnitude."""
    path = tmp_path / "additions.csv"
    write_additions(path, [row(drug_chembl_id="CHEMBL_DRUG"), row(drug_chembl_id="CHEMBL_DRUG_SALT", action_type="agonist")])
    rows = read_drug_target_additions(path)
    assert [(read.drug_chembl_id, read.action_type) for read in rows] == [("CHEMBL_DRUG", "INHIBITOR"), ("CHEMBL_DRUG_SALT", "AGONIST")]
    for drug_ids in (["CHEMBL_DRUG"], ["CHEMBL_DRUG_SALT"]):
        with pytest.raises(ValueError, match="one drug, one target, one action"):
            mechanism_targets(drug_ids, BY_MOLECULE, TARGETS, exclusions=(), additions=rows)
    same_action = (addition(drug="CHEMBL_DRUG"), addition(drug="CHEMBL_DRUG_SALT"))
    with pytest.raises(ValueError, match="name \\['SLC6A3'\\] twice"):
        mechanism_targets(["CHEMBL_DRUG"], BY_MOLECULE, TARGETS, exclusions=(), additions=same_action)
    two_genes = (addition(drug="CHEMBL_DRUG", target="CHEMBL_PAIR", gene="GENE1"), addition(drug="CHEMBL_DRUG_SALT", target="CHEMBL_PAIR", gene="GENE2"))
    kept = mechanism_targets(["CHEMBL_DRUG"], BY_MOLECULE, TARGETS, exclusions=(), additions=two_genes)
    assert [(target.target_chembl_id, target.gene_symbols) for target in kept[1:]] == [("CHEMBL_PAIR", ["GENE1", "GENE2"])]


COCAINE = "CHEMBL370805"
# item 37 rulings draft, section 19: "SLC6A3 0.23, SLC6A4 0.74 and SLC6A2 0.48 micromolar, all inhibition so sign -1"
RULED_COCAINE_ROWS = {("CHEMBL238", "SLC6A3"): 0.23, ("CHEMBL228", "SLC6A4"): 0.74, ("CHEMBL222", "SLC6A2"): 0.48}


def test_the_committed_table_holds_cocaines_three_transporters_as_ruled():
    """Item 37 rulings draft, section 19: "Cocaine's three transporter targets are curated (P4) [...] each on ChEMBL
    binding records and Han and Gu 2006", the dopamine transporter with GtoPdb and Miller 2001 as a third source."""
    additions = read_drug_target_additions(DRUG_TARGET_ADDITIONS_PATH)
    cocaine = {(row.target_chembl_id, row.gene_symbol): row for row in additions if row.drug_chembl_id == COCAINE}
    assert {key: row.affinity_um for key, row in cocaine.items()} == RULED_COCAINE_ROWS
    for row in cocaine.values():
        assert row.sign == -1.0 and row.affinity_measure == "Ki"
        assert "PMID 16515684" in row.sources and "ChEMBL binding records" in row.sources  # two sources per curated row
        assert "omission, not a contradiction" in row.note
    assert "PMID 11223167" in cocaine[("CHEMBL238", "SLC6A3")].sources and "GtoPdb ligand 2286" in cocaine[("CHEMBL238", "SLC6A3")].sources


CHEMBL_DIRECTORY = DRUG_TARGET_ADDITIONS_PATH.parents[1] / "data/raw/chembl"
pinned_chembl = pytest.mark.skipif(not (CHEMBL_DIRECTORY / "mechanisms.json").exists() or not (CHEMBL_DIRECTORY / "targets.json").exists(),
                                   reason="the pinned ChEMBL caches are not present (experiments/fetch_chembl_drug_targets.py)")


@pinned_chembl
def test_on_the_pinned_cache_cocaine_carries_its_sodium_channel_family_and_the_three_transporters():
    """The SIDER route of cocaine (CID 2826) goes through mechanism_targets, so the committed additions reach it; the
    sodium-channel family keeps its nine voltage-gated members (SCN7A removed by configs/drug_target_exclusions.csv)
    until the family row's own resolution is built. That resolution is the rulings draft's P8, which takes its form
    from P5, and P5's class-level annotation became one yes-or-no gate per Nav subtype in the addition of 20 November
    2026; whether cocaine is one of the "similar cases" that gate covers is not settled, so the form is left open here.
    """
    from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import drug_targets_for_pubchem_cid, load_chembl_caches

    caches = load_chembl_caches(CHEMBL_DIRECTORY)
    assert COCAINE in caches.pubchem_to_chembl.get("2826", [])
    kept = drug_targets_for_pubchem_cid(2826, caches)
    by_target = {target.target_chembl_id: target for target in kept}
    assert set(by_target) == {SODIUM_FAMILY, "CHEMBL238", "CHEMBL228", "CHEMBL222"}
    assert {(target_id, tuple(by_target[target_id].gene_symbols)) for target_id, _ in RULED_COCAINE_ROWS} == {(target_id, (gene,)) for target_id, gene in RULED_COCAINE_ROWS}
    assert all(by_target[target_id].sign == -1.0 for target_id, _ in RULED_COCAINE_ROWS)
    assert "SCN7A" not in by_target[SODIUM_FAMILY].gene_symbols and len(by_target[SODIUM_FAMILY].gene_symbols) == 9
    # without the table cocaine carries the family alone, as every build until 20 November 2026 did
    before = mechanism_targets(caches.pubchem_to_chembl["2826"], caches.mechanisms_by_molecule, caches.targets, additions=())
    assert [target.target_chembl_id for target in before] == [SODIUM_FAMILY]
    # so the version-1 dominant-target rule no longer admits cocaine: experiments/run_phase1_counts.py keeps that rule
    # at its default of one target, and its E2 counts were recorded when cocaine passed (that script's docstring)
    assert has_dominant_target(before) and not has_dominant_target(kept)


@pinned_chembl
def test_on_the_pinned_cache_no_addition_names_a_target_its_drug_has_a_chembl_mechanism_row_for():
    """Every committed addition stands on the pinned cache: each drug's mechanism targets are computed with the table,
    which refuses an addition its ChEMBL rows or exclusions contradict, or whose target or gene the cache lacks."""
    targets = json.loads((CHEMBL_DIRECTORY / "targets.json").read_text())
    mechanisms = mechanisms_by_parent_and_molecule(json.loads((CHEMBL_DIRECTORY / "mechanisms.json").read_text()))
    for drug_chembl_id in sorted({row.drug_chembl_id for row in read_drug_target_additions(DRUG_TARGET_ADDITIONS_PATH)}):
        added = {row.target_chembl_id for row in read_drug_target_additions(DRUG_TARGET_ADDITIONS_PATH) if row.drug_chembl_id == drug_chembl_id}
        assert added <= {target.target_chembl_id for target in mechanism_targets([drug_chembl_id], mechanisms, targets)}
