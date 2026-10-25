"""Fetch ChEMBL's in vivo behavioural assays in Rattus norvegicus that the rat drug source reads (decision 9.94).

The source is `ChEMBL-rat-in-vivo` (evidence/rat_drug_behaviour.py): drug-produced catalepsy in rats, read as
parkinsonism. This script asks ChEMBL's web service (the provider's programmatic service, www.ebi.ac.uk/chembl/api)
for every assay of assay organism Rattus norvegicus whose description names catalepsy, then for the activities of
those assays, and saves every page through experiments/read_public_page.py, so the robots rules of www.ebi.ac.uk are
read first and each page is kept with its address, time and SHA-256. data/raw/chembl_rat_behaviour/manifest.json
lists the pages read and the ChEMBL release the service reported. ChEMBL's licence: "The ChEMBL data is made available
on a Creative Commons Attribution-Share Alike 3.0 Unported License" (docs/data_sources.md).

Usage:
  PYTHONPATH=. python experiments/fetch_chembl_rat_behaviour.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path

SERVICE = "https://www.ebi.ac.uk/chembl/api/data"
ASSAY_QUERY = {"assay_organism": "Rattus norvegicus", "description__icontains": "catalep", "limit": "1000"}
ASSAYS_PER_ACTIVITY_REQUEST = 25
READER_PATH = Path(__file__).resolve().parent / "read_public_page.py"


def reader_module():
    specification = importlib.util.spec_from_file_location("read_public_page", READER_PATH)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def read_json(reader, address: str, pages: list[dict]) -> dict:
    record = reader.read(address)
    text = record.pop("text", None)
    pages.append({key: value for key, value in record.items()})
    if not record["read"]:
        raise SystemExit(f"{address}: {record.get('reason')}")
    return json.loads(Path(record["saved_as"]).read_text(encoding="utf-8") if text is None else text)


def all_pages(reader, path: str, query: dict, key: str, pages: list[dict]) -> list[dict]:
    items, address = [], f"{SERVICE}/{path}?{urllib.parse.urlencode(query)}"
    while address:
        page = read_json(reader, address, pages)
        items.extend(page[key])
        following = page["page_meta"].get("next")
        address = f"https://www.ebi.ac.uk{following}" if following else None
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw/chembl_rat_behaviour"))
    arguments = parser.parse_args()
    reader = reader_module().PublicPageReader(arguments.output_dir / "pages")
    pages: list[dict] = []
    assays = all_pages(reader, "assay.json", ASSAY_QUERY, "assays", pages)
    activities = []
    identifiers = sorted({assay["assay_chembl_id"] for assay in assays})
    for start in range(0, len(identifiers), ASSAYS_PER_ACTIVITY_REQUEST):
        batch = identifiers[start:start + ASSAYS_PER_ACTIVITY_REQUEST]
        activities += all_pages(reader, "activity.json", {"assay_chembl_id__in": ",".join(batch), "limit": "1000"}, "activities", pages)
    status = read_json(reader, f"{SERVICE}/status.json", pages)
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    (arguments.output_dir / "assays.json").write_text(json.dumps(assays, indent=0) + "\n", encoding="utf-8")
    (arguments.output_dir / "activities.json").write_text(json.dumps(activities, indent=0) + "\n", encoding="utf-8")
    (arguments.output_dir / "manifest.json").write_text(json.dumps({"chembl_release": status.get("chembl_db_version"), "release_date": status.get("chembl_release_date"),
                                                                    "assay_query": ASSAY_QUERY, "assays": len(assays), "activities": len(activities),
                                                                    "pages": pages}, indent=1) + "\n", encoding="utf-8")
    print(f"{len(assays)} assays and {len(activities)} activities from {status.get('chembl_db_version')}; {arguments.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
