"""BRENDA's kinetic constants (experiments/extract_brenda_kinetics.py), on a small release written in the layout of
BRENDA's JSON schema 2.0.0: a value "<number> {<compound>}", -999 where the number is in the comment."""
from __future__ import annotations

import csv
import gzip
import io
import json
import tarfile

import pytest

from experiments.extract_brenda_kinetics import (
    KINETIC_FIELDS_AND_UNITS,
    OUTPUT_COLUMNS,
    extract,
    kinetic_rows,
    parsed_value,
    protein_entries_in_scope,
)


def enzyme() -> dict:
    return {"id": "2.7.1.1", "recommended_name": "hexokinase",
            "protein": {"1": {"id": "1", "organism": "Homo sapiens", "source": "uniprot", "accessions": ["P19367"], "references": ["1"]},
                        "2": {"id": "2", "organism": "Rattus norvegicus", "accessions": ["P05708"], "references": ["2"]},
                        "3": {"id": "3", "organism": "Homo sapiens", "references": ["1"]}},
            "km_value": [{"value": "0.03 {D-glucose}", "proteins": ["1", "2"], "references": ["1", "2"], "comment": "pH 7.5, 30°C, wild-type enzyme"},
                         {"value": "0.1-0.5 {ATP}", "proteins": ["3"], "references": ["1"], "comment": "isozyme HK2"},
                         {"value": "-999 {more}", "proteins": ["1"], "references": ["1"], "comment": "kinetics for several substrates"}],
            "turnover_number": [{"value": "62 {D-glucose}", "proteins": ["2"], "references": ["2"], "comment": ""}],
            "specific_activity": [{"value": "1.5", "proteins": ["1"], "references": ["1"], "comment": "purified"}],
            "ki_value": [{"value": "0.0047 {glucose 6-phosphate}", "proteins": ["1"], "references": ["1"], "comment": "versus ATP"}],
            "inhibitor": [{"value": "glucose 6-phosphate", "proteins": ["1"], "references": ["1"], "comment": ""}],
            "reference": {"1": {"id": "1", "title": "human paper", "pmid": 1000}, "2": {"id": "2", "title": "rat paper", "pmid": 2000}}}


def release() -> dict:
    return {"release": "2026.1", "version": "1", "data": {"2.7.1.1": enzyme(),
                                                         "1.1.1.1": {"id": "1.1.1.1", "protein": {"1": {"id": "1", "organism": "Rattus norvegicus"}},
                                                                     "km_value": [{"value": "1 {ethanol}", "proteins": ["1"], "references": ["1"]}]}}}


def test_a_value_is_parsed_into_its_number_or_range_and_its_compound_and_kept_as_written():
    assert parsed_value("0.03 {D-glucose}") == {"value_kind": "number", "value_low": 0.03, "value_high": 0.03, "compound": "D-glucose"}
    assert parsed_value("0.1-0.5 {ATP}") == {"value_kind": "range", "value_low": 0.1, "value_high": 0.5, "compound": "ATP"}
    assert parsed_value("-999 {more}")["value_kind"] == "unspecified"
    assert parsed_value("1.5") == {"value_kind": "number", "value_low": 1.5, "value_high": 1.5, "compound": ""}
    assert parsed_value("2e-3 {NADH}")["value_low"] == pytest.approx(0.002)
    assert parsed_value("about 3 {NAD+}") == {"value_kind": "unparsed", "value_low": "", "value_high": "", "compound": "NAD+"}
    assert parsed_value("0.5-0.1 {ATP}")["value_kind"] == "unparsed"  # a range written backwards is not read as one


def test_the_human_scope_keeps_the_human_entries_and_one_without_an_accession():
    entries = protein_entries_in_scope(enzyme(), "human")
    assert entries == {"1": (["P19367"], "Homo sapiens"), "3": ([""], "Homo sapiens")}
    assert set(protein_entries_in_scope(enzyme(), "all")) == {"1", "2", "3"}
    with pytest.raises(ValueError):
        protein_entries_in_scope(enzyme(), "mammals")


def test_the_rows_of_an_entry_carry_the_unit_the_comment_whole_and_the_cited_pubmed_ids():
    rows = list(kinetic_rows("2.7.1.1", enzyme(), "human"))
    assert sorted((row["field"], row["value_text"], row["uniprot_accession"]) for row in rows) == [
        ("ki_value", "0.0047 {glucose 6-phosphate}", "P19367"), ("km_value", "-999 {more}", "P19367"),
        ("km_value", "0.03 {D-glucose}", "P19367"), ("km_value", "0.1-0.5 {ATP}", ""), ("specific_activity", "1.5", "P19367")]
    km = next(row for row in rows if row["value_text"] == "0.03 {D-glucose}")
    assert km["unit"] == "mM" and km["comment"] == "pH 7.5, 30°C, wild-type enzyme" and km["organism"] == "Homo sapiens"
    assert km["reference_pmids"] == "1000;2000" and km["reference_count"] == 2  # the record's references, the rat one among them
    assert all(set(row) == set(OUTPUT_COLUMNS) for row in rows)
    assert "inhibitor" not in {row["field"] for row in rows}  # the regulation fields stay with extract_brenda_enzyme_regulation.py
    every = list(kinetic_rows("2.7.1.1", enzyme(), "all"))
    assert ("turnover_number", "P05708") in {(row["field"], row["uniprot_accession"]) for row in every}


@pytest.mark.parametrize("form", ["tar.gz", "json.gz", "json"])
def test_the_release_is_read_as_an_archive_or_a_json_and_gives_the_same_table(tmp_path, form):
    text = json.dumps(release()).encode()
    path = tmp_path / f"brenda_test.{form}"
    if form == "tar.gz":
        with tarfile.open(path, "w:gz") as archive:
            info = tarfile.TarInfo("brenda_2026_1.json")
            info.size = len(text)
            archive.addfile(info, io.BytesIO(text))
    elif form == "json.gz":
        path.write_bytes(gzip.compress(text))
    else:
        path.write_bytes(text)
    output = tmp_path / "kinetics.csv.gz"
    summary = extract(path, "human", output)
    assert summary["release_path"] == str(path) and summary["brenda_release"] == "2026.1" and len(summary["release_sha256"]) == 64
    assert summary["ec_entries_with_rows"] == 1 and summary["organisms"] == "human"
    assert summary["rows_by_field_and_kind"] == {"ki_value: number": 1, "km_value: number": 1, "km_value: range": 1, "km_value: unspecified": 1,
                                                 "specific_activity: number": 1}
    with gzip.open(output, "rt", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 5 and tuple(rows[0]) == OUTPUT_COLUMNS


def test_an_archive_with_no_or_two_json_members_is_refused(tmp_path):
    path = tmp_path / "two.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        for name in ("a.json", "b.json"):
            info = tarfile.TarInfo(name)
            info.size = 2
            archive.addfile(info, io.BytesIO(b"{}"))
    with pytest.raises(ValueError, match="2 JSON members"):
        extract(path, "human", tmp_path / "out.csv")


def test_every_kinetic_field_names_the_unit_the_schema_gives():
    assert KINETIC_FIELDS_AND_UNITS == {"km_value": "mM", "turnover_number": "1/s", "kcat_km_value": "1/(mM*s)",
                                        "specific_activity": "umol/min/mg", "ki_value": "mM", "ic50_value": "mM"}
