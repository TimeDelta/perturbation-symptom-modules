"""Fetch, for every PubMed id the project holds, the DOI and PMC id that name the same work, from two services
(the owner, 9 November 2026: "just make it so that it tries to convert whichever id exists to all other types and
check each list for duplicates").

What this is for. `mechanistic_pathway_learning/evidence/record_identifiers.py` collapses a reference list to the
distinct works it names, so that one paper cited under two identifier types counts once. It needs a crosswalk, and
this builds it. Without one the module finds same-identifier repeats only.

Why two services, and why both answers are kept. The project's convention for a bibliography entry is "every field
read from the paper's PubMed record and confirmed against Europe PMC" (CLAUDE.md, "Papers are added to
docs/references.bib"), and the two do not agree on coverage: for PMID 1279089, PubMed's own esummary returns no DOI
while Europe PMC returns 10.1016/s0022-2275(20)40768-0 (both read 9 November 2026). So each service's answer is
stored in its own column and a disagreement is left unresolved rather than settled, as the curation rule requires
("a disagreement between sources is recorded beside the row, not settled silently").

The route, and one route that does not work. NCBI's ID Converter
(pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/) covers only articles deposited in PMC: it answers "Identifier
not found in PMC" for PMID 5057882, 1279089 and 3942763 (read 9 November 2026), so it is not used. E-utilities
esummary carries the DOI in its `articleids` array for all of PubMed and is used instead.

NCBI E-utilities, licence and limits verified 9 November 2026. NCBI's "Website and Data Usage Policies and
Disclaimers" (www.ncbi.nlm.nih.gov/home/about/policies/): "Make no more than 3 requests every 1 second. Use the URL
parameter email, and tool for distributed software, so that we can track your project and contact you if there is a
problem." and "Run retrieval scripts on weekends or between 9 pm and 5 am Eastern Time weekdays for any series of
more than 100 requests." Redistribution is permitted under NLM's Terms and Conditions
(www.nlm.nih.gov/databases/download/terms_and_conditions.html, last reviewed 21 May 2019), which the PubMed User
Guide links as "the terms and conditions for data users": acknowledge NLM with "Courtesy of the U.S. National Library
of Medicine", do not imply endorsement, and "Users who republish or redistribute the data ... agree to: maintain the
most current version of all distributed data, or make known in a clear and conspicuous manner that the
products/services/applications do not reflect the most current/accurate data available from NLM." NLM "does not claim
the copyright on the abstracts in PubMed"; no page states in terms that identifier metadata is public domain, and the
only field the policy singles out for third-party rights is the abstract, which this script does not read. The 500-id
ceiling is stated by the API itself, not by a readable page: a POST of 600 ids answers "Too many UIDs in request.
Maximum number of UIDs is 500 for JSON format output." and a GET of 600 answers HTTP 414 (both observed 9 November
2026). The Bookshelf chapters that state the guidelines (NBK25497, NBK25499) sat behind a check that the visitor is
human and were not read.

Europe PMC, licence and limits verified 9 November 2026. Read on `www.ebi.ac.uk`, whose robots file permits the REST
path with crawl-delay 10. **The europepmc.org website is not read by this project**: its robots file disallows
ClaudeBot, anthropic-ai and Claude-Web, and carries content signals addressed to AI systems
("search=yes,ai-train=no,use=reference"), which were reported to the owner, who ruled on 9 November 2026 that using
the API host instead is right ("switching hosts sounds fine to me"). The consortium's own paper, "Europe PMC in 2023"
(Nucleic Acids Research 2024, PMC10767826, CC BY 4.0), states: "Europe PMC APIs and bulk downloads are freely
available ... Content is distributed under the EMBL-EBI Terms of Use available at
(https://www.ebi.ac.uk/about/terms-of-use)." Those Terms of Use (last revised 14 October 2026): "EMBL-EBI itself
places no additional restrictions on the use or redistribution of the data available via its Data Resources and Tools
other than those provided by the original data owners", with attribution "expected ... in accordance with good
scientific practice". So the binding restrictions on these identifiers are NLM's, above. No terms page or API
document states a rate limit; Europe PMC staff state one in the Europe PMC Developer Forum on EBI's own domain ("we
can't increase the current rate limit of 10 requests per second (or 500 per minute)", 1 October 2024), which is a
weaker citation than a terms page, so this script paces well under it. No API key and no registration are needed.

Two measured limits that shape the batch sizes. A 200-id `EXT_ID:x OR EXT_ID:y` query is served; 500 ids answers HTTP
414 (9 November 2026). And a 200-id query returned 208 records, because `EXT_ID` matches more than one record for some
ids, so this script keeps only the record whose own `pmid` field equals the id asked for. Taking the first record per
query would write a DOI belonging to a different work.

Usage:
  PYTHONPATH=. python experiments/fetch_record_identifier_crosswalk.py --limit 2000
  PYTHONPATH=. python experiments/fetch_record_identifier_crosswalk.py              # every id the project holds
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from mechanistic_pathway_learning.evidence.record_identifiers import CROSSWALK_PATH, normalise_doi, normalise_pmc_id
from mechanistic_pathway_learning.graph.edge_evidence import TEXT_MINED_REFERENCE_RESOURCES, pmids_of

PUBMED_SUMMARY_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EUROPEPMC_SEARCH_API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
# Stated by the API itself: a POST of 600 ids is refused with "Maximum number of UIDs is 500 for JSON format output".
PUBMED_BATCH_SIZE = 500
# Measured: 200 ids in one EXT_ID query is served, 500 answers HTTP 414 (9 November 2026).
EUROPEPMC_BATCH_SIZE = 200
# NCBI asks for no more than 3 requests a second without an API key; Europe PMC staff state 10 a second. One request
# of each per cycle with this pause stays well under both.
PAUSE_SECONDS = 1.0
# NCBI asks that "any series of more than 100 requests" run at a weekend or between 9 pm and 5 am Eastern.
NCBI_OFF_PEAK_REQUEST_THRESHOLD = 100
NCBI_OFF_PEAK_ZONE = ZoneInfo("America/New_York")
TOOL_NAME = "perturbation-symptom-modules"
USER_AGENT = f"{TOOL_NAME} (research; https://github.com/TimeDelta/perturbation-symptom-modules)"
CROSSWALK_COLUMNS = ("pubmed_id", "pubmed_service_doi", "europepmc_doi", "pmc_id",
                     "found_in_pubmed", "found_in_europepmc", "retrieved_at")
DEFAULT_HUMAN_GEM_YAML = Path("data/raw/Human-GEM/model/Human-GEM.yml")
DEFAULT_OMNIPATH = Path("data/raw/omnipath/omnipath_interactions.tsv")
DEFAULT_COLLECTRI = Path("data/raw/omnipath/collectri_interactions.tsv")
HUMAN_GEM_REFERENCES_LINE = re.compile(r"^    - references: (.*)$", re.M)
HUMAN_GEM_PUBMED_ID = re.compile(r"(?:PMID|PubMed):(\d+)")


def human_gem_pubmed_ids(yaml_path: Path) -> set[str]:
    """Every PubMed id Human-GEM's reaction references name. Release 2.0.1 writes nine of them as "PubMed:" rather
    than "PMID:", and some tokens are an empty "PMID:", which yields nothing."""
    if not yaml_path.exists():
        return set()
    text = yaml_path.read_text(encoding="utf-8")
    identifiers: set[str] = set()
    for line in HUMAN_GEM_REFERENCES_LINE.findall(text):
        identifiers |= set(HUMAN_GEM_PUBMED_ID.findall(line))
    return identifiers


def interaction_pubmed_ids(omnipath_path: Path, collectri_path: Path) -> set[str]:
    """Every PubMed id an OmniPath or CollecTRI row names, the text-mined resource included: the crosswalk is about
    identifying works, so an id is wanted whatever tier its edge ends up in."""
    identifiers: set[str] = set()
    for path in (omnipath_path, collectri_path):
        if not path.exists():
            continue
        for references in pd.read_csv(path, sep="\t", usecols=["references"], low_memory=False).references:
            kept, excluded = pmids_of(references, TEXT_MINED_REFERENCE_RESOURCES)
            identifiers |= kept | excluded
    return identifiers


def fetch_pubmed_identifiers(pubmed_ids: list[str]) -> dict[str, dict]:
    """{pubmed id: {"doi": ..., "pmc": ...}} from esummary's articleids, for the ids it holds.

    Sent as a POST because a GET of 600 ids answers HTTP 414; `tool` and `email` are the parameters NCBI's policy asks
    distributed software to send, and the owner's address is not used (CLAUDE.md: nothing of the owner's goes into a
    request), so `tool` alone identifies this script.
    """
    body = urllib.parse.urlencode({"db": "pubmed", "retmode": "json", "tool": TOOL_NAME,
                                   "id": ",".join(pubmed_ids)}).encode("ascii")
    request = urllib.request.Request(PUBMED_SUMMARY_API, data=body, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
    result = payload.get("result", {})
    identifiers: dict[str, dict] = {}
    for pubmed_id in result.get("uids", []):
        record = result.get(pubmed_id, {})
        by_type = {entry.get("idtype"): entry.get("value") for entry in record.get("articleids", [])}
        identifiers[str(pubmed_id)] = {"doi": by_type.get("doi") or "", "pmc": by_type.get("pmc") or ""}
    return identifiers


def fetch_europepmc_identifiers(pubmed_ids: list[str]) -> dict[str, dict]:
    """{pubmed id: {"doi": ..., "pmc": ...}} from Europe PMC, keeping only the record whose own pmid is the id asked
    for: a 200-id query returned 208 records, so the extras belong to other works."""
    query = " OR ".join(f"EXT_ID:{pubmed_id}" for pubmed_id in pubmed_ids)
    parameters = urllib.parse.urlencode({"query": query, "format": "json", "resultType": "core",
                                         "pageSize": str(max(len(pubmed_ids) * 2, 25))})
    request = urllib.request.Request(f"{EUROPEPMC_SEARCH_API}?{parameters}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
    asked_for = set(pubmed_ids)
    identifiers: dict[str, dict] = {}
    for record in payload.get("resultList", {}).get("result", []):
        pubmed_id = str(record.get("pmid") or "")
        if pubmed_id in asked_for:
            identifiers[pubmed_id] = {"doi": record.get("doi") or "", "pmc": record.get("pmcid") or ""}
    return identifiers


def with_retries(fetch, batch: list[str], label: str) -> dict[str, dict] | None:
    """Three attempts with a widening pause; None leaves the batch for the next run, as the iCite fetch does."""
    for attempt in range(3):
        try:
            return fetch(batch)
        except Exception as error:
            print(f"{label}: {error}; attempt {attempt + 1}", file=sys.stderr, flush=True)
            time.sleep(10 * (attempt + 1))
    return None


def ncbi_off_peak_now(moment: datetime | None = None) -> bool:
    """True when NCBI's window for a series of more than 100 requests is open: a weekend, or 9 pm to 5 am Eastern."""
    eastern = (moment or datetime.now(timezone.utc)).astimezone(NCBI_OFF_PEAK_ZONE)
    return eastern.weekday() >= 5 or eastern.hour >= 21 or eastern.hour < 5


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--human-gem", type=Path, default=DEFAULT_HUMAN_GEM_YAML)
    parser.add_argument("--omnipath", type=Path, default=DEFAULT_OMNIPATH)
    parser.add_argument("--collectri", type=Path, default=DEFAULT_COLLECTRI)
    parser.add_argument("--cache", type=Path, default=CROSSWALK_PATH)
    parser.add_argument("--limit", type=int, default=None, help="ask for at most this many missing ids")
    parser.add_argument("--pause", type=float, default=PAUSE_SECONDS)
    parser.add_argument("--human-gem-only", action="store_true",
                        help="only the ids Human-GEM's reaction references name, which is a short enough series to "
                             "run outside NCBI's off-peak window")
    parser.add_argument("--ignore-off-peak", action="store_true",
                        help="run a series of more than 100 requests outside NCBI's stated window anyway")
    arguments = parser.parse_args()

    wanted = human_gem_pubmed_ids(arguments.human_gem)
    if not arguments.human_gem_only:
        wanted |= interaction_pubmed_ids(arguments.omnipath, arguments.collectri)
    ordered = sorted(wanted, key=int)
    cached = pd.read_parquet(arguments.cache) if arguments.cache.exists() else pd.DataFrame(columns=list(CROSSWALK_COLUMNS))
    have = set(cached.pubmed_id.astype(str)) if len(cached) else set()
    missing = [pubmed_id for pubmed_id in ordered if pubmed_id not in have]
    if arguments.limit is not None:
        missing = missing[: arguments.limit]
    requests_needed = -(-len(missing) // PUBMED_BATCH_SIZE) + -(-len(missing) // EUROPEPMC_BATCH_SIZE)
    print(f"{len(ordered):,} PubMed ids held; {len(have):,} already in the crosswalk; asking for {len(missing):,} "
          f"in about {requests_needed:,} requests", flush=True)
    if requests_needed > NCBI_OFF_PEAK_REQUEST_THRESHOLD and not ncbi_off_peak_now() and not arguments.ignore_off_peak:
        print(f"NCBI asks that a series of more than {NCBI_OFF_PEAK_REQUEST_THRESHOLD} requests run at a weekend or "
              f"between 9 pm and 5 am Eastern; it is "
              f"{datetime.now(timezone.utc).astimezone(NCBI_OFF_PEAK_ZONE).strftime('%a %H:%M')} Eastern. Use "
              f"--limit, --human-gem-only, or --ignore-off-peak to override.", file=sys.stderr, flush=True)
        return 2
    if not missing:
        return 0

    arguments.cache.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    skipped = 0
    pubmed_answers: dict[str, dict] = {}
    europepmc_answers: dict[str, dict] = {}
    for start in range(0, len(missing), PUBMED_BATCH_SIZE):
        batch = missing[start : start + PUBMED_BATCH_SIZE]
        answered = with_retries(fetch_pubmed_identifiers, batch, f"esummary batch at {start}")
        if answered is None:
            skipped += len(batch)
            continue
        pubmed_answers.update(answered)
        for inner in range(0, len(batch), EUROPEPMC_BATCH_SIZE):
            smaller = batch[inner : inner + EUROPEPMC_BATCH_SIZE]
            answered = with_retries(fetch_europepmc_identifiers, smaller, f"Europe PMC batch at {start + inner}")
            if answered is not None:
                europepmc_answers.update(answered)
            time.sleep(arguments.pause)
        retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for pubmed_id in batch:
            from_pubmed = pubmed_answers.get(pubmed_id)
            from_europepmc = europepmc_answers.get(pubmed_id)
            pmc_id = (from_pubmed or {}).get("pmc") or (from_europepmc or {}).get("pmc") or ""
            rows.append({
                "pubmed_id": pubmed_id,
                "pubmed_service_doi": normalise_doi((from_pubmed or {}).get("doi", "")),
                "europepmc_doi": normalise_doi((from_europepmc or {}).get("doi", "")),
                "pmc_id": normalise_pmc_id(pmc_id) if pmc_id else "",
                "found_in_pubmed": from_pubmed is not None,
                "found_in_europepmc": from_europepmc is not None,
                "retrieved_at": retrieved_at,
            })
        table = pd.concat([cached, pd.DataFrame(rows)], ignore_index=True) if len(cached) else pd.DataFrame(rows)
        table["pubmed_id"] = table.pubmed_id.astype(str)
        table.to_parquet(arguments.cache, index=False)  # written as it goes, so a stopped run keeps what it read
        disagreements = int(((table.pubmed_service_doi != "") & (table.europepmc_doi != "")
                             & (table.pubmed_service_doi != table.europepmc_doi)).sum())
        with_a_doi = int(((table.pubmed_service_doi != "") | (table.europepmc_doi != "")).sum())
        print(f"{start + len(batch):,}/{len(missing):,} asked; {with_a_doi:,} of {len(table):,} have a DOI; "
              f"{disagreements:,} where the two services disagree", flush=True)
        time.sleep(arguments.pause)
    if skipped:
        print(f"{skipped:,} ids were not read after three attempts; run again to ask for them", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
