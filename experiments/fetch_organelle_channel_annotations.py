"""Fetch and pin the UniProt annotations of the organelle counter-ion and release channels the curated calcium-store
reactions rest on (decision 9.75).

One file, data/raw/uniprot/uniprot_organelle_channels.tsv.gz, with a <file>.pin.json beside it: the reviewed human
entries of the channel genes with their catalytic activity (cc_catalytic_activity, whose transport reactions are Rhea
reactions written "ion(in) = ion(out)" with an evidence code each), their Rhea identifiers, their subcellular location
and their primary gene name. Rhea gives a transport reaction no direction and no compartment: its "(in)" and "(out)"
are "nominal cellular compartments" under "the side convention of NC-IUBMB" (Alcantara et al. 2012, doi
10.1093/nar/gkr1126), so which membrane a reaction crosses is read from the entry's subcellular location, and the
direction a curated reaction is written in is the physiological one stated in experiments/build_neuronal_graph_variant.py.

The query names the genes rather than a keyword, so the pinned file is exactly the set the build reads and a later
UniProt release cannot silently widen it. Raw files are never committed (data/raw is gitignored); the pin is recorded
in docs/data_sources.md.

Usage:
  python experiments/fetch_organelle_channel_annotations.py [--refresh]
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
from pathlib import Path
from urllib.parse import quote

import pandas as pd

from experiments.fetch_node_descriptor_sources import download_and_pin

# TMEM38A and TMEM38B are TRIC-A and TRIC-B, the K+ counter-ion channels of the SR and ER; TMEM175 the lysosomal K+
# channel; MCOLN1 to MCOLN3 the mucolipins, the endolysosomal Ca2+ release channels (TRPML1 to TRPML3).
ORGANELLE_CHANNEL_GENES = ("TMEM38A", "TMEM38B", "TMEM175", "MCOLN1", "MCOLN2", "MCOLN3")
UNIPROT_FIELDS = "accession,gene_primary,protein_name,cc_catalytic_activity,rhea,cc_subcellular_location"
DEFAULT_PINNED_PATH = Path("data/raw/uniprot/uniprot_organelle_channels.tsv.gz")
REACTION_PATTERN = re.compile(r"Reaction=([^;]+);.*?Xref=(Rhea:RHEA:\d+)[^;]*;.*?Evidence=\{([^}]*)\}", re.DOTALL)


def organelle_channel_query(genes=ORGANELLE_CHANNEL_GENES) -> str:
    """The UniProt query string: the reviewed human entries whose gene name is one of the channels."""
    return f"(organism_id:9606) AND (reviewed:true) AND ({' OR '.join(f'gene_exact:{gene}' for gene in genes)})"


def transport_reactions(pinned_path: Path = DEFAULT_PINNED_PATH) -> pd.DataFrame:
    """One row per catalytic activity of the pinned entries: gene, accession, reaction, Rhea id, evidence codes and
    the entry's subcellular location text."""
    with gzip.open(pinned_path, "rt", encoding="utf-8") as handle:
        table = pd.read_csv(handle, sep="\t", dtype=str, keep_default_na=False)
    rows = []
    for entry in table.itertuples(index=False):
        activities = [part for part in str(entry[3]).split("CATALYTIC ACTIVITY: ") if part.strip()]
        for activity in activities:
            match = REACTION_PATTERN.search(activity)
            if match is None:
                continue
            evidence_codes = sorted({code.strip().split("|")[0] for code in match.group(3).split(",")})
            rows.append({"gene": entry[1], "accession": entry[0], "reaction": match.group(1).strip(), "rhea": match.group(2).replace("Rhea:", ""),
                         "evidence": ";".join(evidence_codes), "subcellular_location": entry[5]})
    return pd.DataFrame(rows, columns=["gene", "accession", "reaction", "rhea", "evidence", "subcellular_location"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--refresh", action="store_true", help="fetch again even when a pinned file is present")
    arguments = parser.parse_args()
    url = (f"https://rest.uniprot.org/uniprotkb/stream?query={quote(organelle_channel_query())}"
           f"&fields={UNIPROT_FIELDS}&format=tsv&compressed=true")
    pin = download_and_pin(arguments.raw_root, "uniprot", DEFAULT_PINNED_PATH.name, url, arguments.refresh)
    print(json.dumps({key: value for key, value in pin.items() if key != "url"}, indent=2))
    print(f"genes asked for: {len(ORGANELLE_CHANNEL_GENES)} ({', '.join(ORGANELLE_CHANNEL_GENES)})")
    reactions = transport_reactions(arguments.raw_root / "uniprot" / DEFAULT_PINNED_PATH.name)
    print(reactions[["gene", "accession", "reaction", "rhea", "evidence"]].to_string(index=False))


if __name__ == "__main__":
    main()
