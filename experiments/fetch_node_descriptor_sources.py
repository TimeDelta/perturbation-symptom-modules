"""Fetch and pin the sources of the fixed node descriptors and of the HPO laboratory-abnormality labels
(design section 5.2, node descriptors; section 4, auxiliary labels).

Files, each written to data/raw/<source>/ with a <file>.pin.json beside it (URL, bytes, SHA-256, Last-Modified or
release header, fetch time); a file already present with a pin is not fetched again unless --refresh is given:
  - uniprot/uniprot_human_reviewed.tsv.gz: the reviewed human proteome from the UniProt REST stream (accession,
    primary gene name, HGNC, EC numbers, subcellular location, Pfam, length, sequence); sequences feed the ESM-2
    embeddings, the annotations the reduced-rank regression that reduces them;
  - gene_ontology/goa_human.gaf.gz and gene_ontology/go-basic.obo: GO annotations with evidence codes (phenotype-derived
    codes are dropped downstream) and the ontology to propagate them to ancestor terms;
  - hpo/hp-base.owl: the HPO release whose logical definitions name the ChEBI entity and the direction of each
    laboratory abnormality (hp.obo carries none), pinned to the release of data/raw/hpo/hp.obo;
  - chebi/chebi_core.obo.gz: ChEBI with its conjugate acid and base relations, to bridge the neutral forms HPO names
    and the charged forms Human-GEM uses.
Raw files are never committed (data/raw is gitignored); the pins are recorded in docs/data_sources.md.

A UniProt stream that answers 503 is retried at the interval UniProt names, and if it stays unavailable the same query is
read through UniProt's paged search instead, page by page along its Link headers, and checked against the
X-Total-Results header before it is kept (`retrieve_uniprot`). This is the same query and release by another documented
route; the pin records which route served the file. Added 4 November 2026, when the stream answered "503 Streaming
temporarily unavailable" (from UniProt's own cache server, with Retry-After 5) for minutes at a time and stopped the
rebuild at this step. experiments/fetch_plasma_binder_annotations.py and fetch_organelle_channel_annotations.py fetch
through `download_and_pin` too and take the same fallback. The other sources of this script are retried the same
way on a 503 or 429 (`open_with_retries`) and have no second route.

Usage:
  python experiments/fetch_node_descriptor_sources.py [--refresh]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from mechanistic_pathway_learning.evidence.cached_http import USER_AGENT

HPO_RELEASE = "v2026-09-01"  # the release of data/raw/hpo/hp.obo (data-version hp/releases/2026-09-01)
UNIPROT_FIELDS = "accession,gene_primary,xref_hgnc,ec,cc_subcellular_location,xref_pfam,length,sequence"
SOURCES = [
    ("uniprot", "uniprot_human_reviewed.tsv.gz",
     f"https://rest.uniprot.org/uniprotkb/stream?query=(organism_id:9606)%20AND%20(reviewed:true)&fields={UNIPROT_FIELDS}&format=tsv&compressed=true"),
    ("gene_ontology", "goa_human.gaf.gz", "https://current.geneontology.org/annotations/goa_human.gaf.gz"),
    ("gene_ontology", "go-basic.obo", "https://current.geneontology.org/ontology/go-basic.obo"),
    ("hpo", "hp-base.owl", f"https://github.com/obophenotype/human-phenotype-ontology/releases/download/{HPO_RELEASE}/hp-base.owl"),
    ("chebi", "chebi_core.obo.gz", "https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_core.obo.gz"),
]
PINNED_HEADERS = ("last-modified", "content-length", "x-uniprot-release", "x-uniprot-release-date", "x-total-results", "etag")


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


UNIPROT_STREAM_PREFIX = "https://rest.uniprot.org/uniprotkb/stream?"
UNIPROT_SEARCH_PREFIX = "https://rest.uniprot.org/uniprotkb/search?"
UNIPROT_PAGE_SIZE = 500  # the largest page UniProt's search endpoint serves
UNAVAILABLE_ATTEMPTS = 4  # tries of one request before it counts as unavailable
LONGEST_RETRY_WAIT_SECONDS = 60
NEXT_PAGE_LINK = re.compile(r'<([^>]+)>;\s*rel="next"')


def open_with_retries(url: str, attempts: int = UNAVAILABLE_ATTEMPTS):
    """urlopen, retrying a 503 or 429 at the interval its Retry-After names (at least 5 s, at most a minute); the last
    such error is raised when every attempt answered it, and any other error at once."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        try:
            return urllib.request.urlopen(request, timeout=300)
        except urllib.error.HTTPError as error:
            if error.code not in (429, 503) or attempt == attempts:
                raise
            retry_after = error.headers.get("Retry-After", "") if error.headers else ""
            wait = int(retry_after) if retry_after.isdigit() else 5
            time.sleep(min(max(wait, 5), LONGEST_RETRY_WAIT_SECONDS))
    raise AssertionError("unreachable")


def paged_search_url(stream_url: str) -> tuple[str, bool]:
    """(the search URL for the same query, whether the stream URL asked for a gzip-compressed answer). The pages are
    read uncompressed and compressed here, so the file on disk has the form the stream would have given."""
    parameters = urllib.parse.parse_qsl(stream_url[len(UNIPROT_STREAM_PREFIX):], keep_blank_values=True)
    compressed = any(key == "compressed" and value == "true" for key, value in parameters)
    kept = [(key, value) for key, value in parameters if key not in ("compressed", "size")] + [("size", str(UNIPROT_PAGE_SIZE))]
    return UNIPROT_SEARCH_PREFIX + urllib.parse.urlencode(kept, safe="(),:"), compressed


def retrieve_uniprot(stream_url: str, partial_path: Path) -> tuple[dict, dict]:
    """Write the answer to a UniProt stream URL to partial_path. Returns (the response headers to pin, the route that
    served it). The stream is tried first; if it stays unavailable, the paged search is read instead and its rows are
    counted against X-Total-Results, so a short read is an error rather than a smaller file."""
    try:
        with open_with_retries(stream_url) as response, open(partial_path, "wb") as handle:
            headers = {key.lower(): value for key, value in response.headers.items()}
            shutil.copyfileobj(response, handle, length=1 << 20)
        return headers, {"retrieved_by": "stream"}
    except urllib.error.HTTPError as error:
        if error.code not in (429, 503):
            raise
    search_url, compressed = paged_search_url(stream_url)
    first_headers: dict = {}
    header_line = None
    rows = pages = 0
    opener = gzip.open if compressed else open
    with opener(partial_path, "wt", encoding="utf-8") as handle:
        next_url = search_url
        while next_url:
            with open_with_retries(next_url) as response:
                page_headers = {key.lower(): value for key, value in response.headers.items()}
                lines = response.read().decode("utf-8").splitlines()
            pages += 1
            first_headers = first_headers or page_headers
            if lines:
                if header_line is None:
                    header_line = lines[0]
                    handle.write(header_line + "\n")
                body = lines[1:] if lines[0] == header_line else lines
                handle.writelines(line + "\n" for line in body)
                rows += len(body)
            link = NEXT_PAGE_LINK.search(page_headers.get("link", ""))
            next_url = link.group(1) if link else None
    expected = first_headers.get("x-total-results")
    if expected is not None and int(expected) != rows:
        raise RuntimeError(f"UniProt paged search gave {rows} rows where X-Total-Results says {expected}: {search_url}")
    return first_headers, {"retrieved_by": "paged search, because the stream answered 503 or 429 on every attempt",
                           "retrieval_url": search_url, "pages": pages, "rows": rows}


def download_and_pin(raw_root: Path, source: str, file_name: str, url: str, refresh: bool) -> dict:
    directory = raw_root / source
    directory.mkdir(parents=True, exist_ok=True)
    target_path, pin_path = directory / file_name, directory / f"{file_name}.pin.json"
    if target_path.exists() and pin_path.exists() and not refresh:
        return json.loads(pin_path.read_text())
    partial_path = directory / f"{file_name}.part"
    route: dict = {}
    if url.startswith(UNIPROT_STREAM_PREFIX):
        headers, route = retrieve_uniprot(url, partial_path)
    else:
        with open_with_retries(url) as response, open(partial_path, "wb") as handle:
            headers = {key.lower(): value for key, value in response.headers.items()}
            shutil.copyfileobj(response, handle, length=1 << 20)
    partial_path.replace(target_path)
    pin = {"url": url, "file": str(target_path), "bytes": target_path.stat().st_size, "sha256": sha256_of_file(target_path),
           "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **route,
           **{header.replace("-", "_"): headers[header] for header in PINNED_HEADERS if header in headers}}
    pin_path.write_text(json.dumps(pin, indent=2) + "\n")
    return pin


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--refresh", action="store_true", help="fetch again even when a pinned file is present")
    arguments = parser.parse_args()
    for source, file_name, url in SOURCES:
        pin = download_and_pin(arguments.raw_root, source, file_name, url, arguments.refresh)
        print(f"{source}/{file_name}: {pin['bytes']:,} bytes, sha256 {pin['sha256'][:12]}, "
              f"{pin.get('last_modified') or pin.get('x_uniprot_release') or 'no release header'}")


if __name__ == "__main__":
    main()
