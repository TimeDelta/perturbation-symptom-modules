"""Fetch the ChEMBL activity records for the compound-to-protein pairs a graph's edges name (decision 9.91).

For every edge of the compound-to-protein relations (graph/chembl_activity_negatives.py: CHEMBL_RELATIONS) whose source
maps to ChEMBL compounds and whose target maps to ChEMBL single-protein targets, the ChEMBL web service's activity
resource is asked for the records of that parent compound on those targets. The service is ChEMBL's own programmatic
interface; the SQLite dump of the release (chembl_37_sqlite.tar.gz on the EBI FTP) is several gigabytes compressed and
was not needed for a few thousand pairs. Every response is appended to a parquet cache, so a second graph or a rerun
asks only for the compounds not yet asked; the pin beside it (edge_activities.pin.json) records the release the
service reported, the time and the pairs asked.

Usage:
  python experiments/fetch_chembl_edge_activities.py --graph-dir data/processed/graph_full_neuronal_split_binders_drugs_v5
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.chembl_activity_negatives import (
    ACTIVITY_FIELDS,
    DEFAULT_ACTIVITIES,
    DEFAULT_CHEBI_MAPPING,
    DEFAULT_METABOLITES,
    DEFAULT_PUBCHEM_MAPPING,
    DEFAULT_TARGET_MAPPING,
    candidate_pairs,
    chebi_of_base,
    compound_ids_of_nodes,
    read_chebi_mapping,
    read_pubchem_mapping,
    read_target_mapping,
    target_ids_of_nodes,
)
from mechanistic_pathway_learning.graph.negatome_negatives import accession_symbols

SERVICE = "https://www.ebi.ac.uk/chembl/api/data"
TARGETS_PER_REQUEST = 40
PAGE_SIZE = 1000
SECONDS_BETWEEN_REQUESTS = 0.3
USER_AGENT = "mechanistic-pathway-learning/0.1 (research; ChEMBL activity records for graph edges)"


def get_json(url: str, attempts: int = 4) -> dict:
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as error:  # a transient failure of the service; the last one is raised
            if attempt == attempts - 1:
                raise
            print(f"retrying after {error}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("unreachable")


def activities_of(compound: str, targets: list[str]) -> list[dict]:
    """Every activity record of the parent compound on the targets, page by page."""
    rows = []
    for start in range(0, len(targets), TARGETS_PER_REQUEST):
        chunk = targets[start:start + TARGETS_PER_REQUEST]
        offset = 0
        while True:
            query = {"parent_molecule_chembl_id": compound, "target_chembl_id__in": ",".join(chunk), "limit": PAGE_SIZE, "offset": offset,
                     "only": ",".join(ACTIVITY_FIELDS)}
            page = get_json(f"{SERVICE}/activity.json?{urllib.parse.urlencode(query)}")
            rows.extend({field: record.get(field) for field in ACTIVITY_FIELDS} for record in page.get("activities", []))
            time.sleep(SECONDS_BETWEEN_REQUESTS)
            if not (page.get("page_meta") or {}).get("next"):
                break
            offset += PAGE_SIZE
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, action="append", required=True, help="repeat for several graphs")
    parser.add_argument("--output", type=Path, default=DEFAULT_ACTIVITIES)
    parser.add_argument("--target-mapping", type=Path, default=DEFAULT_TARGET_MAPPING)
    parser.add_argument("--chebi-mapping", type=Path, default=DEFAULT_CHEBI_MAPPING)
    parser.add_argument("--pubchem-mapping", type=Path, default=DEFAULT_PUBCHEM_MAPPING)
    parser.add_argument("--metabolites", type=Path, default=DEFAULT_METABOLITES)
    parser.add_argument("--hgnc", type=Path, default=Path("data/raw/hgnc/hgnc_complete_set.txt"))
    arguments = parser.parse_args()
    status = get_json(f"{SERVICE}/status.json")
    targets_of_accession = read_target_mapping(arguments.target_mapping)
    chembl_of_chebi = read_chebi_mapping(arguments.chebi_mapping)
    chembl_of_pubchem = read_pubchem_mapping(arguments.pubchem_mapping)
    human_gem_chebi = chebi_of_base(pd.read_csv(arguments.metabolites, sep="\t", usecols=["metsNoComp", "metChEBIID"]) if arguments.metabolites.is_file() else None)
    accessions_of_symbol: dict[str, set[str]] = {}
    for accession, symbol in accession_symbols(arguments.hgnc).items():
        accessions_of_symbol.setdefault(symbol, set()).add(accession)
    wanted: dict[str, set[str]] = {}
    for graph_dir in arguments.graph_dir:
        nodes = pd.read_parquet(graph_dir / "nodes.parquet")
        edges = pd.read_parquet(graph_dir / "edges.parquet", columns=["source_id", "target_id", "relation_type"])
        compounds = compound_ids_of_nodes(nodes, human_gem_chebi, chembl_of_chebi, chembl_of_pubchem)
        targets = target_ids_of_nodes(nodes, targets_of_accession, accessions_of_symbol)
        for compound, found in candidate_pairs(edges, compounds, targets).items():
            wanted.setdefault(compound, set()).update(found)
        print(f"{graph_dir}: {len(compounds):,} compound nodes and {len(targets):,} protein or gene nodes map to ChEMBL")
    cached = pd.read_parquet(arguments.output) if arguments.output.is_file() else pd.DataFrame(columns=list(ACTIVITY_FIELDS))
    pin_path = arguments.output.with_suffix(".pin.json")
    pin = json.loads(pin_path.read_text(encoding="utf-8")) if pin_path.is_file() else {"queries": {}}
    asked = {compound: set(targets) for compound, targets in pin["queries"].items()}
    new_rows = []
    to_ask = {compound: sorted(found - asked.get(compound, set())) for compound, found in sorted(wanted.items())}
    to_ask = {compound: found for compound, found in to_ask.items() if found}
    print(f"{len(wanted):,} compounds with edges to mapped targets; {len(to_ask):,} still to ask ({sum(map(len, to_ask.values())):,} pairs)")
    for number, (compound, found) in enumerate(to_ask.items(), start=1):
        new_rows.extend(activities_of(compound, found))
        asked.setdefault(compound, set()).update(found)
        if number % 50 == 0 or number == len(to_ask):
            print(f"  {number:,} of {len(to_ask):,} compounds, {len(new_rows):,} records so far")
    table = pd.concat([cached, pd.DataFrame(new_rows, columns=list(ACTIVITY_FIELDS))], ignore_index=True).drop_duplicates("activity_id") if new_rows else cached
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    table.astype({field: "string" for field in ACTIVITY_FIELDS}).to_parquet(arguments.output, index=False)
    pin.update({"service": SERVICE, "release": status.get("chembl_db_version"), "release_date": status.get("chembl_release_date"),
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "records": int(len(table)),
                "sha256": hashlib.sha256(arguments.output.read_bytes()).hexdigest(),
                "queries": {compound: sorted(targets) for compound, targets in sorted(asked.items())}})
    pin_path.write_text(json.dumps(pin, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {arguments.output}: {len(table):,} records over {table.parent_molecule_chembl_id.nunique() if len(table) else 0:,} parent compounds; release {pin['release']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
