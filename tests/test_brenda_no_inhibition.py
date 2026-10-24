"""Decision 9.88: a BRENDA note of no inhibition is a negative observation, not an `inhibits` edge
(experiments/extract_brenda_enzyme_regulation.py), and the mapping keeps such observations out of the edge table
(experiments/map_brenda_regulation_to_graph.py). The clause patterns are audited in tests/test_regex_audit.py."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from experiments.extract_brenda_enzyme_regulation import NO_INHIBITION_RELATION, notes_by_protein, regulation_rows, relation_of_notes
from experiments.map_brenda_regulation_to_graph import overlap_with_inhibits, pair_changes, pairs_of

REPOSITORY = Path(__file__).resolve().parents[1]


def test_a_comment_is_split_into_the_notes_of_each_protein_entry():
    comment = "#1,4# not inhibited <12>; #5# 50% inhibition at 1 mM <13,14>"
    assert notes_by_protein(comment, ["1", "4", "5"]) == {"1": ["not inhibited"], "4": ["not inhibited"], "5": ["50% inhibition at 1 mM"]}


def test_a_comment_without_markers_is_one_note_on_every_protein_of_the_record():
    assert notes_by_protein("not inhibited by ATP <3>", ["2", "7"]) == {"2": ["not inhibited by ATP"], "7": ["not inhibited by ATP"]}
    assert notes_by_protein("", ["2"]) == {} and notes_by_protein(None, ["2"]) == {}


@pytest.mark.parametrize("notes, expected_relation", [
    ([], "inhibits"),  # listed as an inhibitor with no note: as before
    (["competitive to MgATP2-, inhibition is partially relieved by phosphate"], "inhibits"),  # EC 2.7.1.1, human
    (["not inhibited by D-glucose 6-phosphate"], NO_INHIBITION_RELATION),  # EC 2.7.1.1
    (["D-glucose 6-phosphate has no effect"], NO_INHIBITION_RELATION),  # EC 2.7.1.1
    (["no inhibition of V62L, V62M, V62Q, V62F, V62K"], None),  # a mutant only: no human edge either way
    (["enzymes from rat brain and bovine heart are not inhibited by palmitoyl-CoA"], None),  # another organism
    (["no inhibition of hexokinase 2"], None),  # an isozyme
    # EC 2.7.1.1, human glucokinase and its regulatory protein: the wild type is inhibited, the mutants are not
    (["wild type enzyme and mutant enzymes V62A, V62T, and V62E are significantly inhibited (80% enzyme activity remaining), "
      "no inhibition of V62L, V62M, V62Q, V62F, V62K"], "inhibits"),
    (["no inhibition at 1 mM, 50% inhibition at 10 mM"], "inhibits"),  # concentration dependence
    (["mutant D209A is inhibited, no inhibition of the wild-type enzyme"], NO_INHIBITION_RELATION),
    (["noncompetitive, no effect on Km"], "inhibits"),  # a kinetic note, not an absence
])
def test_the_relation_of_an_inhibitor_entry_follows_its_notes(notes, expected_relation):
    relation, note_class = relation_of_notes(notes, "D-glucose 6-phosphate")
    assert relation == expected_relation, (notes, relation, note_class)


def enzyme_with_a_human_and_a_rat_entry() -> dict:
    return {"protein": {"1": {"id": "1", "organism": "Homo sapiens", "accessions": ["P35557"]},
                        "2": {"id": "2", "organism": "Rattus norvegicus", "accessions": ["P17712"]}},
            "inhibitor": [
                {"value": "palmitoyl-CoA", "proteins": ["1", "2"], "references": ["3", "4"]},
                {"value": "D-glucose 6-phosphate", "proteins": ["1", "2"], "references": ["5", "6"],
                 "comment": "#1# not inhibited by D-glucose 6-phosphate <5>; #2# 40% inhibition at 2 mM <6>"},
                {"value": "D-fructose 1-phosphate", "proteins": ["1"], "references": ["7"], "comment": "#1# no inhibition of mutant V62L <7>"},
                {"value": "trehalose 6-phosphate", "proteins": ["2"], "references": ["8"], "comment": "#2# 70% inhibition <8>"},
                {"value": "more", "proteins": ["1"], "references": ["9"], "comment": "#1# not inhibited by D-fructose <9>"}],
            "activating_compound": [{"value": "sorbitol 6-phosphate", "proteins": ["1"], "references": ["10"]}]}


def test_the_human_entry_takes_its_own_note_and_the_rat_entry_none():
    rows = list(regulation_rows("2.7.1.2", enzyme_with_a_human_and_a_rat_entry()))
    by_ligand = {(row["ligand_name"], row["uniprot_accession"]): row for row in rows}
    assert by_ligand[("palmitoyl-CoA", "P35557")]["relation_type"] == "inhibits" and by_ligand[("palmitoyl-CoA", "P35557")]["sign"] == -1.0
    # the human entry's note says not inhibited; the rat entry's 40% does not reach it
    negative = by_ligand[("D-glucose 6-phosphate", "P35557")]
    assert negative["relation_type"] == NO_INHIBITION_RELATION and negative["sign"] == 0.0
    assert negative["brenda_comment"] == "not inhibited by D-glucose 6-phosphate"
    assert ("D-fructose 1-phosphate", "P35557") not in by_ligand  # a mutant's absence: no row either way
    assert not any(row["uniprot_accession"] == "P17712" for row in rows)  # the rat entry, left out by its organism
    assert ("more", "P35557") not in by_ligand
    assert by_ligand[("sorbitol 6-phosphate", "P35557")]["relation_type"] == "activates"


def test_the_extraction_writes_the_note_class_and_counts_it(tmp_path):
    brenda_json = tmp_path / "brenda.json"
    brenda_json.write_text(json.dumps({"release": "test", "data": {"2.7.1.2": enzyme_with_a_human_and_a_rat_entry()}}))
    output = tmp_path / "records.csv"
    completed = subprocess.run([sys.executable, "experiments/extract_brenda_enzyme_regulation.py", str(brenda_json), "--output", str(output)],
                               cwd=REPOSITORY, capture_output=True, text=True, env={"PYTHONPATH": str(REPOSITORY), "PATH": ""}, check=True)
    summary = json.loads(completed.stdout)
    assert summary["counts_by_relation"] == {"inhibits": 1, NO_INHIBITION_RELATION: 1, "activates": 1}
    assert summary["note_classes"]["inhibitor: no row (no inhibition, mutant)"] == 1
    assert summary["note_classes"]["comments of an inhibition field entry with protein markers"] == 3
    with open(output, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert {row["note_class"] for row in rows} == {"no note of absence", "no inhibition of this enzyme", ""}


def mapped_rows(relations: list[tuple[str, str, str, float]]) -> pd.DataFrame:
    return pd.DataFrame([{"base_metabolite_id": metabolite, "uniprot_accession": accession, "relation_type": relation, "sign": sign, "ec_number": "2.7.1.2",
                          "brenda_field": "inhibitor", "ligand_name": metabolite, "enzyme_route": "accession stated by BRENDA", "brenda_reference_count": 1}
                         for metabolite, accession, relation, sign in relations])


def test_negative_observations_stay_apart_from_the_edges_and_are_counted_where_they_meet_one():
    mapped = mapped_rows([("MAM01", "P35557", "inhibits", -1.0), ("MAM01", "P35557", NO_INHIBITION_RELATION, 0.0), ("MAM02", "P35557", NO_INHIBITION_RELATION, 0.0)])
    negative = mapped.relation_type == NO_INHIBITION_RELATION
    pairs, no_inhibition = pairs_of(mapped[~negative]), pairs_of(mapped[negative])
    assert set(pairs.relation_type) == {"inhibits"} and len(no_inhibition) == 2
    assert overlap_with_inhibits(no_inhibition, pairs) == 1
    assert pairs_of(mapped.iloc[0:0]).empty


def test_the_comparison_counts_the_pairs_each_relation_lost_and_gained():
    before = pairs_of(mapped_rows([("MAM01", "P35557", "inhibits", -1.0), ("MAM02", "P35557", "inhibits", -1.0), ("MAM03", "P35557", "activates", 1.0)]))
    after = pairs_of(mapped_rows([("MAM01", "P35557", "inhibits", -1.0), ("MAM03", "P35557", "activates", 1.0)]))
    assert pair_changes(before, after) == {"activates": {"before": 1, "after": 1, "lost": 0, "gained": 0},
                                           "inhibits": {"before": 2, "after": 1, "lost": 1, "gained": 0}}
