"""Fetch SFARI Gene's mouse-model pages and pin what was read (decision 9.93; evidence/sfari_mouse_models.py reads them).

SFARI Gene publishes its animal-model module as web pages, one per gene and species, and a gene list as CSV; it has no
versioned download of the phenotypic profiles. Every request goes through experiments/read_public_page.py, so the
site's robots file is read first, a disallowed page is left unread and a check that the visitor is human is reported
as a refusal. Each page is saved with its address, time and SHA-256 (the reader's record beside it), and
data/raw/sfari/manifest.tsv pins the set: gene, address, SHA-256, saved file, whether it was read and why not. The
release SFARI names on its pages ("Latest Release: 2026 Q2" on 24 October 2026) is recorded in manifest.json; a later
fetch that finds another release says so, since the pages move with each release.

Writes, under --output-dir (data/raw/sfari): animal_genes.csv (the gene list), pages/ (the reader's files),
manifest.tsv and manifest.json. Resumable: a gene the manifest holds as read, with its file present and its SHA-256
unchanged, is not requested again.

--import-directory takes pages an earlier pass saved with experiments/read_public_page.py (each page with the
reader's .json record beside it), checks each file against the SHA-256 the record states, and pins them as if fetched,
without a request; a page whose digest does not match is not imported.

Terms: "All data on SFARI Gene are derived from sources that are in the public domain, and we encourage users to
include such data in their publications, with appropriate citation of the primary data source, the SFARI Gene
website, and relevant publications describing SFARI Gene" (https://gene.sfari.org/terms-and-privacy/, read 24 October
2026); no licence is named.

Usage:
  PYTHONPATH=. python experiments/fetch_sfari_mouse_models.py
  PYTHONPATH=. python experiments/fetch_sfari_mouse_models.py --genes SHANK3 CNTNAP2
  PYTHONPATH=. python experiments/fetch_sfari_mouse_models.py --import-directory <a directory of pages read earlier>
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

GENE_LIST_ADDRESS = "https://gene.sfari.org//wp-content/themes/sfari-gene/utilities/download-csv.php?api-endpoint=animal-genes"
PAGE_ADDRESS = "https://gene.sfari.org/database/animal-models/genetic-animal-models/{gene}/Mus+musculus"
EXPECTED_RELEASE = "2026 Q2"
MANIFEST_COLUMNS = ("gene", "address", "read", "sha256", "saved_as", "reason")
READER_PATH = Path(__file__).resolve().parent / "read_public_page.py"


def page_reader_module():
    specification = importlib.util.spec_from_file_location("read_public_page", READER_PATH)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def page_address(gene: str) -> str:
    return PAGE_ADDRESS.format(gene=urllib.parse.quote(gene, safe=""))


def gene_of_address(address: str) -> str | None:
    match = re.search(r"genetic-animal-models/([^/]+)/Mus\+musculus", address)
    return urllib.parse.unquote(match.group(1)) if match else None


def release_of_page(page_html: str) -> str:
    match = re.search(r"Latest Release:\s*([^<]+)", page_html)
    return match.group(1).strip() if match else ""


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_manifest(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    with open(path, newline="", encoding="utf-8") as handle:
        return {row["gene"]: row for row in csv.DictReader(handle, delimiter="\t")}


def write_manifest(path: Path, entries: dict[str, dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS, delimiter="\t")
        writer.writeheader()
        for gene in sorted(entries):
            writer.writerow({column: entries[gene].get(column, "") for column in MANIFEST_COLUMNS})


def pinned_entry_is_current(entry: dict | None, output_dir: Path) -> bool:
    if not entry or entry.get("read") != "True":
        return False
    saved = output_dir / entry["saved_as"]
    return saved.is_file() and file_sha256(saved) == entry["sha256"]


def import_pages(import_directory: Path, pages_dir: Path) -> dict[str, dict]:
    """Pages saved earlier by the page reader, checked against their records' SHA-256 and copied into pages_dir."""
    entries: dict[str, dict] = {}
    for record_path in sorted(Path(import_directory).glob("*.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        gene = gene_of_address(record.get("address", ""))
        page_path = record_path.with_suffix("")
        if gene is None or not record.get("read") or not page_path.is_file():
            continue
        digest = file_sha256(page_path)
        if digest != record.get("sha256"):
            entries[gene] = {"gene": gene, "address": record["address"], "read": "False", "sha256": digest, "saved_as": "",
                             "reason": f"imported file's SHA-256 {digest} differs from its record's {record.get('sha256')}"}
            continue
        pages_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(page_path, pages_dir / page_path.name)
        shutil.copyfile(record_path, pages_dir / record_path.name)
        entries[gene] = {"gene": gene, "address": record["address"], "read": "True", "sha256": digest, "saved_as": f"pages/{page_path.name}",
                         "reason": f"imported from a page read {record.get('requested_at', '')} by experiments/read_public_page.py"}
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw/sfari"))
    parser.add_argument("--genes", nargs="*", default=None, help="these genes only (default: every gene of SFARI's animal-model gene list)")
    parser.add_argument("--import-directory", type=Path, default=None)
    parser.add_argument("--refresh", action="store_true", help="request every page again, even one the manifest pins")
    arguments = parser.parse_args()

    output_dir = arguments.output_dir
    pages_dir = output_dir / "pages"
    manifest_path = output_dir / "manifest.tsv"
    entries = read_manifest(manifest_path)
    if arguments.import_directory is not None:
        imported = import_pages(arguments.import_directory, pages_dir)
        entries.update(imported)
        write_manifest(manifest_path, entries)
        print(f"imported {sum(entry['read'] == 'True' for entry in imported.values())} pages, {sum(entry['read'] != 'True' for entry in imported.values())} refused; {manifest_path}")
    else:
        reader = page_reader_module().PublicPageReader(pages_dir)
        genes = arguments.genes
        if genes is None:
            record = reader.read(GENE_LIST_ADDRESS)
            record.pop("text", None)
            if not record["read"]:
                print(f"the gene list was not read: {record.get('reason')}", file=sys.stderr)
                return 1
            output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(record["saved_as"], output_dir / "animal_genes.csv")
            with open(output_dir / "animal_genes.csv", newline="", encoding="utf-8") as handle:
                genes = [row["gene-symbol"].strip() for row in csv.DictReader(handle) if row.get("gene-symbol", "").strip()]
        refused = 0
        for gene in genes:
            if not arguments.refresh and pinned_entry_is_current(entries.get(gene), output_dir):
                continue
            record = reader.read(page_address(gene))
            record.pop("text", None)
            if record["read"]:
                entries[gene] = {"gene": gene, "address": record["address"], "read": "True", "sha256": record["sha256"],
                                 "saved_as": str(Path(record["saved_as"]).relative_to(output_dir)), "reason": ""}
            else:
                refused += 1
                entries[gene] = {"gene": gene, "address": record["address"], "read": "False", "sha256": "", "saved_as": "", "reason": record.get("reason", "")}
            print(json.dumps({key: value for key, value in record.items() if key != "saved_as"}), flush=True)
            write_manifest(manifest_path, entries)
        print(f"{len(genes)} genes, {refused} pages not read; {manifest_path}")
    releases = sorted({release_of_page((output_dir / entry["saved_as"]).read_text(encoding="utf-8", errors="replace"))
                       for entry in entries.values() if entry.get("read") == "True" and (output_dir / entry["saved_as"]).is_file()})
    (output_dir / "manifest.json").write_text(json.dumps({"releases_named_on_the_pages": releases, "expected_release": EXPECTED_RELEASE,
                                                          "pages_read": sum(entry.get("read") == "True" for entry in entries.values()),
                                                          "pages_not_read": sorted(gene for gene, entry in entries.items() if entry.get("read") != "True"),
                                                          "manifest_sha256": file_sha256(manifest_path) if manifest_path.is_file() else None}, indent=1) + "\n", encoding="utf-8")
    if releases != [EXPECTED_RELEASE]:
        print(f"the pages name the release(s) {releases}, not {EXPECTED_RELEASE}: the pin moved", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
