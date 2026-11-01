"""The human subset of BRENDA's JSON release (experiments/make_brenda_human_subset.py) gives the extraction
(experiments/extract_brenda_enzyme_regulation.py) the rows the whole release gives, and the extraction reads it
gzip-compressed. On release 2026.1 the two output files were compared by SHA-256 on 1 November 2026
(docs/data_sources.md); this test holds the same property on a small release built here."""
from __future__ import annotations

import gzip
import json
import subprocess
import sys
from pathlib import Path

from experiments.make_brenda_human_subset import human_regulation_subset_of_enzyme, write_human_regulation_subset

REPOSITORY = Path(__file__).resolve().parents[1]


def enzyme_with_human_and_rat_entries() -> dict:
    return {"id": "2.7.1.2", "recommended_name": "glucokinase", "km_value": [{"value": "0.1", "proteins": ["1"]}],
            "protein": {"1": {"id": "1", "organism": "Homo sapiens", "accessions": ["P35557"], "references": ["1"]},
                        "2": {"id": "2", "organism": "Rattus norvegicus", "accessions": ["P17712"], "references": ["2"]},
                        "3": {"id": "3", "organism": "Homo sapiens", "references": ["3"]}},
            "inhibitor": [
                {"value": "palmitoyl-CoA", "proteins": ["1", "2"], "references": ["4"]},
                {"value": "D-glucose 6-phosphate", "proteins": ["1", "2"], "references": ["5"],
                 "comment": "not inhibited by D-glucose 6-phosphate, a long note that runs well past the three hundred characters the "
                            "extraction keeps of a comment, so that the subset can be seen to keep the whole of it: " + "x" * 300},
                {"value": "trehalose 6-phosphate", "proteins": ["2"], "references": ["6"], "comment": "70% inhibition"}],
            "activating_compound": [{"value": "sorbitol 6-phosphate", "proteins": ["3"], "references": ["7"], "comment": "no effect"}],
            "cofactor": [{"value": "ATP", "proteins": ["2"], "references": ["8"]}],
            "reference": {str(number): {"id": str(number), "title": f"paper {number}", "pmid": 1000 + number} for number in range(1, 10)}}


def enzyme_of_rat_only() -> dict:
    return {"id": "1.1.1.1", "protein": {"1": {"id": "1", "organism": "Rattus norvegicus", "accessions": ["P06757"]}},
            "inhibitor": [{"value": "pyrazole", "proteins": ["1"], "references": ["1"]}],
            "reference": {"1": {"id": "1", "title": "rat paper"}}}


def test_the_subset_keeps_the_human_entries_and_every_record_that_names_one():
    subset = human_regulation_subset_of_enzyme(enzyme_with_human_and_rat_entries())
    assert set(subset["protein"]) == {"1", "3"}  # the rat entry is left out
    assert [record["value"] for record in subset["inhibitor"]] == ["palmitoyl-CoA", "D-glucose 6-phosphate"]
    assert subset["inhibitor"][1]["proteins"] == ["1", "2"]  # a record is kept whole, rat index and all
    assert len(subset["inhibitor"][1]["comment"]) > 300  # and its comment is not cut
    assert "cofactor" not in subset  # the one cofactor record names the rat entry only
    assert "km_value" not in subset  # a field the extraction does not read
    assert set(subset["reference"]) == {"1", "3", "4", "5", "7"}  # cited by the human entries and the kept records
    assert subset["recommended_name"] == "glucokinase"


def test_an_enzyme_with_no_human_entry_is_left_out():
    assert human_regulation_subset_of_enzyme(enzyme_of_rat_only()) is None


def test_the_extraction_gives_the_same_rows_from_the_gzip_subset_as_from_the_whole_release(tmp_path):
    whole_release = tmp_path / "brenda.json"
    whole_release.write_text(json.dumps({"release": "test", "version": "1",
                                         "data": {"1.1.1.1": enzyme_of_rat_only(), "2.7.1.2": enzyme_with_human_and_rat_entries()}}))
    subset_path = tmp_path / "subset.json.gz"
    counts = write_human_regulation_subset(whole_release, subset_path)
    assert counts == {"enzyme_entries_read": 2, "enzyme_entries_with_a_human_protein_entry": 1, "release": "test", "version": "1"}
    with gzip.open(subset_path, "rt", encoding="utf-8") as subset_handle:
        subset_release = json.load(subset_handle)
    assert list(subset_release["data"]) == ["2.7.1.2"] and subset_release["release"] == "test"

    outputs = {}
    for name, release_path in (("whole", whole_release), ("subset", subset_path)):
        outputs[name] = tmp_path / f"rows_{name}.csv"
        subprocess.run([sys.executable, "experiments/extract_brenda_enzyme_regulation.py", str(release_path), "--output", str(outputs[name])],
                       cwd=REPOSITORY, env={"PYTHONPATH": str(REPOSITORY), "PATH": ""}, check=True, capture_output=True)
    whole_rows = outputs["whole"].read_bytes()
    assert whole_rows == outputs["subset"].read_bytes()
    assert b"palmitoyl-CoA" in whole_rows and b"sorbitol 6-phosphate" in whole_rows and b"pyrazole" not in whole_rows
