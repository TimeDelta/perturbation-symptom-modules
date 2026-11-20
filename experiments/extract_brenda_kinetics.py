"""Pull BRENDA's kinetic constants into one table, for amendment item 37's sourced headroom of the enzyme rows.

Why. The item 37 rulings draft (docs/item37_rulings_draft_2026-11-13.md, section 12) records "BRENDA's full kinetics are
fetched. The owner: "16. fetch", so the enzyme rows are not left on the fallback". The headroom of a saturable step is
(maximum - rest) / rest, which for a Michaelis-Menten step needs its Km or its kcat (decision 9.81, the addition of 6
November 2026: "Km is in the BRENDA release the project already holds, and the human subset drops it on purpose").
The committed subset `data/brenda/brenda_2026_1_human_regulation_subset.json.gz` holds the six regulation fields of
experiments/extract_brenda_enzyme_regulation.py and no kinetic field, so this reads the release itself.

Input. BRENDA's JSON release as BRENDA serves it: the `.tar.gz` archive, read as a stream so the 709,658,292-byte JSON
of release 2026.1 is never unpacked to disk; or the JSON, plain or gzip-compressed. The download page
(brenda-enzymes.org/download.php) serves it to a form on which the downloader actively accepts the licence, which is the
owner's to do (decision 9.88), so this script fetches nothing. The release's format is BRENDA's JSON schema 2.0.0
(brenda-enzymes.org/schemas/2.0.0/enzyme.schema.json, read 20 November 2026 with experiments/read_public_page.py,
sha256 20ec78df8ebd5bb6...): each kinetic field is a list of numeric_dataset records, `value` a string, with
`proteins`, `references` and `comment`, and the schema gives each field's unit. In release 2026.1 a value reads
"<number> {<compound>}" (the Ki and IC50 records of the committed subset, e.g. "1.7 {ethanol}"), the compound being the
substrate for km_value, turnover_number and kcat_km_value and the inhibitor for ki_value and ic50_value; a record whose
value is not one number reads "-999 {more}" there (beside the comment "inhibition kinetics"), and is kept as
`unspecified`.

Output. One row per (record, protein entry of the organisms asked for, accession): the EC number, the field and its
unit as the schema gives it, the value as written and parsed (a number, a range "low-high", -999, or unparsed, kept
either way), the compound, the protein entry's accession and organism, the record's comment whole (it carries the
conditions: pH, temperature, mutant or wild type, isozyme), and the PubMed ids of the references it cites. Nothing is
filtered on the comment and no value is chosen among several: which Km stands for a reaction, at which conditions, is
the sourcing pass's to decide, not this table's.

What it leaves to the caller, because no ruling settles it: **--organisms**, required with no default: "human" keeps
the protein entries whose organism names Homo sapiens, as the regulation extraction does; "all" keeps every organism,
for a fallback across species, which the rulings do not settle. The licence of release 2026.1 is recorded in
docs/data_sources.md (CC BY 4.0); its check for these fields is a Fable step and is not made here.

Usage:
  python experiments/extract_brenda_kinetics.py brenda_2026_1.json.tar.gz --organisms human --output <table>.csv.gz
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import csv
import gzip
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path

import ijson

# field -> unit, from the descriptions of brenda-enzymes.org/schemas/2.0.0/enzyme.schema.json (read 20 November 2026)
KINETIC_FIELDS_AND_UNITS = {
    "km_value": "mM",
    "turnover_number": "1/s",
    "kcat_km_value": "1/(mM*s)",
    "specific_activity": "umol/min/mg",
    "ki_value": "mM",
    "ic50_value": "mM",
}
ORGANISM_SCOPES = ("human", "all")
HUMAN = "homo sapiens"
UNSPECIFIED_VALUE = -999.0  # BRENDA's "-999 {more}", a record whose value is not one number (module docstring)
NUMBER = r"[0-9]+(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?"
VALUE_PATTERN = re.compile(rf"^\s*(?P<low>-?{NUMBER})(?:\s*-\s*(?P<high>{NUMBER}))?\s*(?:\{{(?P<compound>.*)\}})?\s*$", re.DOTALL)
OUTPUT_COLUMNS = ("ec_number", "field", "unit", "value_text", "value_kind", "value_low", "value_high", "compound", "uniprot_accession",
                  "protein_index", "organism", "comment", "reference_pmids", "reference_count")


def parsed_value(text: str) -> dict:
    """value_kind (number, range, unspecified or unparsed), value_low, value_high and compound of a value string."""
    match = VALUE_PATTERN.match(str(text))
    if match is None:
        braces = re.search(r"\{(.*)\}", str(text), re.DOTALL)
        return {"value_kind": "unparsed", "value_low": "", "value_high": "", "compound": braces.group(1).strip() if braces else ""}
    low, high = float(match.group("low")), match.group("high")
    compound = (match.group("compound") or "").strip()
    if low == UNSPECIFIED_VALUE and high is None:
        return {"value_kind": "unspecified", "value_low": "", "value_high": "", "compound": compound}
    if high is None:
        return {"value_kind": "number", "value_low": low, "value_high": low, "compound": compound}
    high = float(high)
    if high < low:
        return {"value_kind": "unparsed", "value_low": "", "value_high": "", "compound": compound}
    return {"value_kind": "range", "value_low": low, "value_high": high, "compound": compound}


def protein_entries_in_scope(enzyme_record: dict, organisms: str) -> dict[str, tuple[list[str], str]]:
    """{protein index: (accessions, [''] for an entry without one; organism)} of the entries the scope keeps."""
    if organisms not in ORGANISM_SCOPES:
        raise ValueError(f"organisms is one of {ORGANISM_SCOPES}, not {organisms!r}")
    kept: dict[str, tuple[list[str], str]] = {}
    for protein_index, entry in (enzyme_record.get("protein") or {}).items():
        if not isinstance(entry, dict):
            continue
        organism = str(entry.get("organism", ""))
        if organisms == "human" and HUMAN not in organism.lower():
            continue
        accessions = [str(accession) for accession in entry.get("accessions") or [] if str(accession).strip()] or [""]
        kept[str(protein_index)] = (accessions, organism)
    return kept


def kinetic_rows(ec_number: str, enzyme_record: dict, organisms: str):
    """The rows of one EC entry (module docstring, Output)."""
    entries = protein_entries_in_scope(enzyme_record, organisms)
    if not entries:
        return
    references = enzyme_record.get("reference") or {}
    for field_name, unit in KINETIC_FIELDS_AND_UNITS.items():
        for record in enzyme_record.get(field_name) or []:
            value_text = str(record.get("value", "")).strip()
            reference_ids = [str(reference) for reference in record.get("references") or []]
            pmids = sorted({str(references[reference]["pmid"]) for reference in reference_ids
                            if isinstance(references.get(reference), dict) and references[reference].get("pmid")}, key=int)
            parsed = parsed_value(value_text)
            for protein_index in (str(index) for index in record.get("proteins") or []):
                if protein_index not in entries:
                    continue
                accessions, organism = entries[protein_index]
                for accession in accessions:
                    yield {"ec_number": ec_number, "field": field_name, "unit": unit, "value_text": value_text, **parsed,
                           "uniprot_accession": accession, "protein_index": protein_index, "organism": organism,
                           "comment": str(record.get("comment", "")), "reference_pmids": ";".join(pmids), "reference_count": len(reference_ids)}


@contextlib.contextmanager
def release_stream(path: Path):
    """The release's JSON as a binary stream: from a .tar.gz archive holding one .json member, read without unpacking
    it to disk, or from a .json or .json.gz file."""
    path = Path(path)
    if path.name.endswith((".tar.gz", ".tgz")):
        with tarfile.open(path, "r:gz") as archive:
            members = [member for member in archive.getmembers() if member.isfile() and member.name.endswith(".json")]
            if len(members) != 1:
                raise ValueError(f"{path} holds {len(members)} JSON members, not one: {[member.name for member in members]}")
            handle = archive.extractfile(members[0])
            yield io.BufferedReader(handle)
    elif path.name.endswith(".gz"):
        with gzip.open(path, "rb") as handle:
            yield handle
    else:
        with open(path, "rb") as handle:
            yield handle


def release_header(path: Path) -> dict:
    """The release's top-level `release` and `version` strings, which precede `data` in BRENDA's file."""
    header: dict = {}
    with release_stream(path) as handle:
        for prefix, event, value in ijson.parse(handle):
            if prefix in ("release", "version") and event == "string":
                header[prefix] = value
            if prefix == "data" and event == "start_map":
                break
    return header


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def extract(release: Path, organisms: str, output: Path) -> dict:
    """Write the table (gzip-compressed when output ends .gz) and return the summary."""
    counts: collections.Counter = collections.Counter()
    entries_with_rows = 0
    opener = gzip.open if str(output).endswith(".gz") else open
    with release_stream(release) as handle, opener(output, "wt", newline="", encoding="utf-8") as table:
        writer = csv.DictWriter(table, fieldnames=list(OUTPUT_COLUMNS), lineterminator="\n")
        writer.writeheader()
        for ec_number, enzyme_record in ijson.kvitems(handle, "data"):
            wrote = False
            for row in kinetic_rows(ec_number, enzyme_record, organisms):
                writer.writerow(row)
                counts[(row["field"], row["value_kind"])] += 1
                wrote = True
            entries_with_rows += wrote
    header = release_header(release)
    return {"release_path": str(release), "release_sha256": sha256_of(release), "brenda_release": header.get("release"),
            "brenda_file_version": header.get("version"), "organisms": organisms,
            "output": str(output), "ec_entries_with_rows": entries_with_rows,
            "rows_by_field_and_kind": {f"{field}: {kind}": count for (field, kind), count in sorted(counts.items())}}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("release", type=Path, help="BRENDA's JSON release: the .tar.gz archive, or the JSON plain or gzip-compressed")
    parser.add_argument("--organisms", choices=ORGANISM_SCOPES, required=True, help="human or all (module docstring); no default")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    print(json.dumps(extract(arguments.release, arguments.organisms, arguments.output), indent=1))


if __name__ == "__main__":
    main()
