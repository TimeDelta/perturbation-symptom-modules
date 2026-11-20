"""configs/chembl_parent_corrections.csv and the reader that applies it (map_drug_targets_to_graph_nodes.read_pubchem_to_chembl).

The ChEMBL_37 cache map data/raw/chembl/pubchem_to_chembl_with_parents.json holds, for some PubChem ids, no ChEMBL id
or only a form other than the parent that carries the drug's mechanisms and activity records; a refetch writes the same
map, so the parents are added where it is read. The unit tests run on small fixtures. The two guard tests read the
pinned ChEMBL_37 cache and the OnSIDES bridge, which are gitignored raw downloads, and skip when they are absent:
every correction names a parent the pinned release holds, and no drug whose OnSIDES-bridge parent carries a pinned
mechanism target is left without one by the corrected map.
"""
import csv
import json
from pathlib import Path

import pandas as pd
import pytest

from mechanistic_pathway_learning.evidence.assemble_evidence_table import bridge_chembl_parents_by_sider_cid
from mechanistic_pathway_learning.graph.chembl_activity_negatives import compound_ids_of_nodes, read_pubchem_mapping
from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import (
    CHEMBL_PARENT_CORRECTIONS_PATH,
    corrected_pubchem_to_chembl,
    drug_targets_for_pubchem_cid,
    load_chembl_caches,
    mechanism_targets,
    read_chembl_parent_corrections,
    read_pubchem_to_chembl,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHEMBL_DIRECTORY = REPOSITORY_ROOT / "data/raw/chembl"
ONSIDES_BRIDGE = REPOSITORY_ROOT / "data/raw/onsides/v3.1.1/ingredient_identifier_bridge.json"
IDENTITY_OVERRIDES = REPOSITORY_ROOT / "configs/perturbation_identity_overrides.csv"
SIDER_DIRECTORY = REPOSITORY_ROOT / "data/raw/sider_4.1"
TABLE_COLUMNS = ["pubchem_cid", "drug", "cache_chembl_ids", "correct_parent_chembl_id", "chembl_release", "sources", "note"]


def write_corrections(path: Path, rows: list[dict]) -> Path:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TABLE_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in TABLE_COLUMNS})
    return path


def write_chembl_directory(directory: Path, release: str | None = "ChEMBL_37") -> Path:
    """A cache in which CID 100 maps to a dead registration (CHEMBL1, no mechanism) whose parent CHEMBL2 carries the
    mechanism, CID 200 maps to nothing, and CID 300 maps to a salt that carries a mechanism of its own."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "pubchem_to_chembl_with_parents.json").write_text(json.dumps({"100": ["CHEMBL1"], "200": [], "300": ["CHEMBL30"]}))
    mechanisms = [
        {"molecule_chembl_id": "CHEMBL2", "parent_molecule_chembl_id": "CHEMBL2", "target_chembl_id": "CHEMBL_T1", "action_type": "ANTAGONIST"},
        {"molecule_chembl_id": "CHEMBL4", "parent_molecule_chembl_id": "CHEMBL4", "target_chembl_id": "CHEMBL_T2", "action_type": "INHIBITOR"},
        {"molecule_chembl_id": "CHEMBL30", "parent_molecule_chembl_id": "CHEMBL31", "target_chembl_id": "CHEMBL_T1", "action_type": "AGONIST"},
    ]
    (directory / "mechanisms.json").write_text(json.dumps(mechanisms))
    targets = {"CHEMBL_T1": {"pref_name": "Receptor 1", "target_type": "SINGLE PROTEIN", "organism": "Homo sapiens", "gene_symbols": ["RCP1"], "accessions": ["P00001"]},
               "CHEMBL_T2": {"pref_name": "Enzyme 2", "target_type": "SINGLE PROTEIN", "organism": "Homo sapiens", "gene_symbols": ["ENZ2"], "accessions": ["P00002"]}}
    (directory / "targets.json").write_text(json.dumps(targets))
    if release is not None:
        (directory / "chembl_release.json").write_text(json.dumps({"chembl_db_version": release, "chembl_release_date": "2026-05-01"}))
    return directory


FIXTURE_ROWS = [
    {"pubchem_cid": "100", "drug": "drug one", "cache_chembl_ids": "CHEMBL1", "correct_parent_chembl_id": "CHEMBL2", "chembl_release": "ChEMBL_37", "sources": "fixture"},
    {"pubchem_cid": "200", "drug": "drug two", "cache_chembl_ids": "", "correct_parent_chembl_id": "CHEMBL4", "chembl_release": "ChEMBL_37", "sources": "fixture"},
    {"pubchem_cid": "200", "drug": "drug two", "cache_chembl_ids": "", "correct_parent_chembl_id": "CHEMBL4", "chembl_release": "ChEMBL_37", "sources": "fixture, repeated"},
    {"pubchem_cid": "0400", "drug": "drug four", "cache_chembl_ids": "", "correct_parent_chembl_id": "CHEMBL5", "chembl_release": "ChEMBL_37", "sources": "fixture"},
]


def test_the_union_keeps_the_cache_ids_and_adds_each_parent_once():
    cache = {"100": ["CHEMBL1"], "200": [], "300": ["CHEMBL30"]}
    corrected = corrected_pubchem_to_chembl(cache, {"100": ["CHEMBL2", "CHEMBL1"], "200": ["CHEMBL4"], "400": ["CHEMBL5"]})
    assert corrected == {"100": ["CHEMBL1", "CHEMBL2"], "200": ["CHEMBL4"], "300": ["CHEMBL30"], "400": ["CHEMBL5"]}
    assert cache == {"100": ["CHEMBL1"], "200": [], "300": ["CHEMBL30"]}, "the cache map is not changed in place"


def test_the_table_reader_keys_by_cache_cid_and_drops_repeats(tmp_path):
    corrections, releases = read_chembl_parent_corrections(write_corrections(tmp_path / "corrections.csv", FIXTURE_ROWS))
    assert corrections == {"100": ["CHEMBL2"], "200": ["CHEMBL4"], "400": ["CHEMBL5"]}
    assert releases == {"ChEMBL_37"}
    assert read_chembl_parent_corrections(tmp_path / "absent.csv") == ({}, set())
    assert read_chembl_parent_corrections(None) == ({}, set())


def test_the_map_is_read_with_the_corrections_and_as_fetched_without_them(tmp_path):
    directory = write_chembl_directory(tmp_path / "chembl")
    corrections = write_corrections(tmp_path / "corrections.csv", FIXTURE_ROWS)
    mapping_path = directory / "pubchem_to_chembl_with_parents.json"
    assert read_pubchem_to_chembl(mapping_path, corrections) == {"100": ["CHEMBL1", "CHEMBL2"], "200": ["CHEMBL4"], "300": ["CHEMBL30"], "400": ["CHEMBL5"]}
    assert read_pubchem_to_chembl(mapping_path, None) == {"100": ["CHEMBL1"], "200": [], "300": ["CHEMBL30"]}


def test_a_table_verified_on_another_release_is_refused(tmp_path):
    corrections = write_corrections(tmp_path / "corrections.csv", FIXTURE_ROWS)
    newer = write_chembl_directory(tmp_path / "chembl_38", release="ChEMBL_38")
    with pytest.raises(ValueError, match="re-verify"):
        read_pubchem_to_chembl(newer / "pubchem_to_chembl_with_parents.json", corrections)
    unnamed = write_chembl_directory(tmp_path / "chembl_unnamed", release=None)
    assert read_pubchem_to_chembl(unnamed / "pubchem_to_chembl_with_parents.json", corrections)["100"] == ["CHEMBL1", "CHEMBL2"]


def test_the_mechanism_route_reaches_the_parent_without_the_bridge(tmp_path):
    directory = write_chembl_directory(tmp_path / "chembl")
    corrections = write_corrections(tmp_path / "corrections.csv", FIXTURE_ROWS)
    as_fetched = load_chembl_caches(directory, corrections_path=None)
    corrected = load_chembl_caches(directory, corrections_path=corrections)
    assert drug_targets_for_pubchem_cid(100, as_fetched) == [] and drug_targets_for_pubchem_cid(200, as_fetched) == []
    assert [(target.target_chembl_id, target.sign) for target in drug_targets_for_pubchem_cid(100, corrected)] == [("CHEMBL_T1", -1.0)]
    assert [target.gene_symbols for target in drug_targets_for_pubchem_cid(200, corrected)] == [["ENZ2"]]
    assert [target.action_type for target in drug_targets_for_pubchem_cid(300, corrected)] == ["AGONIST"], "a CID the table does not list is unchanged"


def test_the_activity_route_reads_the_same_corrected_map(tmp_path):
    directory = write_chembl_directory(tmp_path / "chembl")
    corrections = write_corrections(tmp_path / "corrections.csv", FIXTURE_ROWS)
    mapping = read_pubchem_mapping(directory / "pubchem_to_chembl_with_parents.json", corrections)
    assert mapping == load_chembl_caches(directory, corrections_path=corrections).pubchem_to_chembl
    nodes = pd.DataFrame({"node_id": ["DRUG:CID100000100", "DRUG:CID100000200"], "node_type": ["drug", "drug"]})
    assert compound_ids_of_nodes(nodes, {}, {}, mapping) == {"DRUG:CID100000100": {"CHEMBL1", "CHEMBL2"}, "DRUG:CID100000200": {"CHEMBL4"}}
    assert read_pubchem_mapping(tmp_path / "absent.json", corrections) == {}


def test_every_row_of_the_table_names_its_parent_release_and_sources():
    with open(CHEMBL_PARENT_CORRECTIONS_PATH, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == TABLE_COLUMNS
        rows = list(reader)
    assert rows
    pairs = [(row["pubchem_cid"], row["correct_parent_chembl_id"]) for row in rows]
    assert len(pairs) == len(set(pairs)), "a CID and parent are listed once"
    for row in rows:
        assert row["pubchem_cid"].isdigit() and str(int(row["pubchem_cid"])) == row["pubchem_cid"], row
        assert row["correct_parent_chembl_id"].startswith("CHEMBL") and row["correct_parent_chembl_id"][6:].isdigit(), row
        assert row["correct_parent_chembl_id"] not in row["cache_chembl_ids"].split(";"), f"CID {row['pubchem_cid']}: the parent is already in the cache"
        assert row["chembl_release"] and row["sources"].strip() and row["drug"].strip(), row


pinned_chembl = pytest.mark.skipif(not (CHEMBL_DIRECTORY / "mechanisms.json").exists() or not (CHEMBL_DIRECTORY / "chembl_release.json").exists(),
                                   reason="the pinned ChEMBL_37 cache (data/raw/chembl/) is written by experiments/fetch_chembl_drug_targets.py and is not present")


@pinned_chembl
def test_every_correction_points_at_a_mechanism_parent_of_the_pinned_release():
    """A correction that names an id absent from the pinned data corrects nothing."""
    release = json.loads((CHEMBL_DIRECTORY / "chembl_release.json").read_text())["chembl_db_version"]
    corrections, releases = read_chembl_parent_corrections(CHEMBL_PARENT_CORRECTIONS_PATH)
    assert releases == {release}, f"the table was verified on {sorted(releases)}, the pinned cache is {release}"
    caches = load_chembl_caches(CHEMBL_DIRECTORY)
    absent = sorted((cid, parent) for cid, parents in corrections.items() for parent in parents if parent not in caches.mechanisms_by_molecule)
    assert not absent, f"corrections naming no mechanism molecule or parent of pinned {release}: {absent}"


@pinned_chembl
@pytest.mark.skipif(not ONSIDES_BRIDGE.exists(), reason="the OnSIDES identifier bridge, the independent witness of a drug's parent, is not present "
                                                         "(experiments/fetch_onsides_identifier_bridge.py)")
def test_no_drug_whose_bridge_parent_has_a_mechanism_is_left_without_one():
    """For every SIDER CID whose OnSIDES-bridge parent carries a pinned mechanism with a target, the corrected map
    yields a mechanism target by itself, without the bridge fallback; otherwise the cache holds a non-parent form the
    table does not cover. (A mechanism row without a target, which some ChEMBL_37 parents carry alone, is no witness.)"""
    caches = load_chembl_caches(CHEMBL_DIRECTORY)
    bridge = bridge_chembl_parents_by_sider_cid(ONSIDES_BRIDGE, IDENTITY_OVERRIDES, SIDER_DIRECTORY if SIDER_DIRECTORY.exists() else None)
    offenders = []
    for cid, parents in sorted(bridge.items()):
        witnesses = [parent for parent in parents if mechanism_targets([parent], caches.mechanisms_by_molecule, caches.targets, human_only=False)]
        if not witnesses:
            continue
        chembl_ids = caches.pubchem_to_chembl.get(str(cid), [])
        if not mechanism_targets(chembl_ids, caches.mechanisms_by_molecule, caches.targets, human_only=False):
            offenders.append((cid, chembl_ids, witnesses))
    assert not offenders, ("cache ids with a missing parent that configs/chembl_parent_corrections.csv does not supply:\n"
                           + "\n".join(f"  CID {cid}: corrected map {ids}, bridge parent {witnesses}" for cid, ids, witnesses in offenders[:50]))
