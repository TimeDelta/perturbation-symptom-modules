"""Cut BRENDA's JSON release down to what the human regulation extraction reads, so the release can travel.

The whole release 2026.1 JSON is 709,658,292 bytes unpacked, and a session on a small environment cannot hold it
(the owner, 1 November 2026). `experiments/extract_brenda_enzyme_regulation.py` reads only part of it: per EC entry,
the protein table, to find the human protein entries, and the six regulation fields of
`REGULATION_FIELDS_AND_RELATIONS`. A record of a field reaches a row only through a human protein index it names.
So this script keeps, in the same layout (top-level `release`, `version` and `data` keyed by EC number):

  every EC entry that has at least one human protein entry (`human_accessions_of_protein_entry`'s test: the
  organism contains "homo sapiens"), with its `id` and `recommended_name`;
  its `protein` table reduced to the human entries;
  every record of the six regulation fields that names at least one of those human entries, kept whole, so its
  comment is not cut (the extraction cuts the comment it writes to 300 characters) and the notes of other protein
  entries stay readable beside the human ones;
  the `reference` entries those records and human protein entries cite, so a reading of a note can find its paper.

The extraction's rows from the subset are the rows from the whole release; the test of that is
`tests/test_brenda_human_subset.py`, and the run of 1 November 2026 compared the two output files by SHA-256 (the
record is `docs/data_sources.md`). Two counts of the extraction's printed summary do change, because they count
entries that make no row: `enzyme_entries_seen` counts EC entries, and the note class "comments of an inhibition
field entry without protein markers" counts every commented record.

BRENDA is CC BY 4.0 (`docs/data_sources.md`), so the subset may be redistributed with attribution.

Usage:
  python experiments/make_brenda_human_subset.py brenda_2026_1.json --output data/brenda/brenda_2026_1_human_regulation_subset.json.gz
"""
import argparse
import gzip
import json
from pathlib import Path

import ijson

from experiments.extract_brenda_enzyme_regulation import REGULATION_FIELDS_AND_RELATIONS

KEPT_ENTRY_DESCRIPTORS = ("id", "recommended_name")


def is_human_protein_entry(protein_entry) -> bool:
    return isinstance(protein_entry, dict) and "homo sapiens" in str(protein_entry.get("organism", "")).lower()


def human_regulation_subset_of_enzyme(enzyme_record: dict) -> dict | None:
    """The part of one EC entry the extraction reads, or None when the entry has no human protein entry."""
    human_protein_entries = {str(protein_index): protein_entry
                             for protein_index, protein_entry in (enzyme_record.get("protein") or {}).items()
                             if is_human_protein_entry(protein_entry)}
    if not human_protein_entries:
        return None
    subset_record = {descriptor: enzyme_record[descriptor] for descriptor in KEPT_ENTRY_DESCRIPTORS if descriptor in enzyme_record}
    subset_record["protein"] = human_protein_entries
    cited_reference_ids = {str(reference_id) for protein_entry in human_protein_entries.values()
                           for reference_id in protein_entry.get("references") or []}
    for field_name in REGULATION_FIELDS_AND_RELATIONS:
        records_naming_a_human_protein = [field_record for field_record in enzyme_record.get(field_name) or []
                                          if any(str(protein_index) in human_protein_entries
                                                 for protein_index in field_record.get("proteins") or [])]
        if records_naming_a_human_protein:
            subset_record[field_name] = records_naming_a_human_protein
            cited_reference_ids.update(str(reference_id) for field_record in records_naming_a_human_protein
                                       for reference_id in field_record.get("references") or [])
    all_references = enzyme_record.get("reference") or {}
    subset_record["reference"] = {reference_id: all_references[reference_id]
                                  for reference_id in sorted(cited_reference_ids, key=lambda value: (len(value), value))
                                  if reference_id in all_references}
    return subset_record


def write_human_regulation_subset(brenda_json_path: Path, output_path: Path) -> dict:
    """Stream the release and write the subset as gzip-compressed JSON; returns counts for the record."""
    enzyme_entries_read = 0
    enzyme_entries_kept = 0
    with open(brenda_json_path, "rb") as release_handle:
        release_header = {key: value for key, value in ijson.kvitems(release_handle, "") if key in ("release", "version")}
    opener = gzip.open if output_path.suffix == ".gz" else open
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(brenda_json_path, "rb") as release_handle, opener(output_path, "wt", encoding="utf-8") as output_handle:
        output_handle.write("{")
        for header_key, header_value in release_header.items():
            output_handle.write(f"{json.dumps(header_key)}: {json.dumps(header_value, ensure_ascii=False)}, ")
        output_handle.write('"data": {')
        for ec_number, enzyme_record in ijson.kvitems(release_handle, "data", use_float=True):
            enzyme_entries_read += 1
            subset_record = human_regulation_subset_of_enzyme(enzyme_record)
            if subset_record is None:
                continue
            separator = ", " if enzyme_entries_kept else ""
            output_handle.write(f"{separator}{json.dumps(ec_number)}: {json.dumps(subset_record, ensure_ascii=False)}")
            enzyme_entries_kept += 1
        output_handle.write("}}\n")
    return {"enzyme_entries_read": enzyme_entries_read, "enzyme_entries_with_a_human_protein_entry": enzyme_entries_kept,
            "release": release_header.get("release"), "version": release_header.get("version")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("brenda_json", type=Path, help="the whole BRENDA JSON release, unpacked")
    parser.add_argument("--output", type=Path, required=True, help="the subset; gzip-compressed when the name ends in .gz")
    arguments = parser.parse_args()
    print(json.dumps(write_human_regulation_subset(arguments.brenda_json, arguments.output), indent=1))


if __name__ == "__main__":
    main()
