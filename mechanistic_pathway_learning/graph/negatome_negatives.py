"""Negatome 2.0's non-interacting protein pairs as negative observations on the graph's protein edges (decision 9.91).

Negatome 2.0 (Blohm et al. 2014, doi 10.1093/nar/gkt1079) holds mammalian protein pairs reported not to interact: a
manual set curated from the literature, guided by text mining and verified by hand ("Manual and Manual-stringent datasets
contain 2171 and 1991 pairs"), and a set derived from protein structures, chains of one PDB biological unit more than
8 A apart ("PDB dataset and its stringent version contain 4397 and 4161 pairs"). The stringent subsets leave out the
pairs IntAct records as interacting. A structure-derived pair belongs to one complex and is not in direct contact, so it
says no direct binding, not no association.

What is read. Each Negatome file holds one pair per line, the two UniProt accessions first; whatever follows (PubMed
ids, PDB ids, methods) is kept as provenance. A file's set is read from its name: manual, pdb or combined, and stringent
or not. A pair counts one observation per independent set holding it, manual and pdb, so a pair in both counts two;
a stringent subset is part of its set and adds nothing, and the combined set is the union of the two.

Which edges. Every graph edge whose two ends are the two proteins, in either direction, carries the observation
(negatome_negative, negatome_sets); the likelihood ratio applies to binds edges alone (configs/
edge_negative_likelihood_ratios.csv), since an activation or an inhibition can run through intermediates, and
the count on other relations is reported. Negatome states no positives.

Retrieval. The 2.0 files are served from the provider's host, which on 22 October 2026 was unreachable from this
machine (docs/data_sources.md lists the routes tried); `read_negatome` reads the files from data/raw/negatome/ when they
are there.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.graph.edge_evidence import UNIPROT_ACCESSION, accession_of, symbol_of

DEFAULT_NEGATOME_DIRECTORY = Path("data/raw/negatome")
BASE_SETS = ("manual", "pdb")
TOKEN = re.compile(r"[\s,;|]+")


def set_of_file(path: Path) -> tuple[str, bool] | None:
    """(base set, stringent) from a Negatome file name: manual.txt, manual_stringent.txt, pdb.txt, combined_stringent.txt
    and the like; None for a file that is not a protein pair set (the PFAM domain sets)."""
    name = path.stem.lower()
    if "pfam" in name or "domain" in name:
        return None
    stringent = "stringent" in name
    for base in ("manual", "pdb", "combined"):
        if base in name:
            return base, stringent
    return None


def read_negatome_file(path: Path) -> dict[frozenset[str], str]:
    """{unordered accession pair: the rest of its first line} for every line whose first two tokens are UniProt
    accessions (isoform suffixes dropped)."""
    pairs = {}
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            tokens = [token for token in TOKEN.split(line.strip()) if token]
            if len(tokens) < 2 or not (UNIPROT_ACCESSION.match(tokens[0]) and UNIPROT_ACCESSION.match(tokens[1])):
                continue
            first, second = tokens[0].split("-")[0], tokens[1].split("-")[0]
            if first != second:
                pairs.setdefault(frozenset((first, second)), " ".join(tokens[2:]))
    return pairs


def read_negatome(directory: Path = DEFAULT_NEGATOME_DIRECTORY) -> dict[frozenset[str], set[str]]:
    """{accession pair: the independent base sets holding it (manual, pdb)} over every pair file in the directory. The
    combined files add the base sets of their pairs only where no base file holds the pair, since their lines do not say
    which set a pair came from."""
    held: dict[frozenset[str], set[str]] = defaultdict(set)
    combined: set[frozenset[str]] = set()
    for path in sorted(Path(directory).glob("*.txt")):
        kind = set_of_file(path)
        if kind is None:
            continue
        base, _ = kind
        pairs = read_negatome_file(path)
        if base == "combined":
            combined |= set(pairs)
        else:
            for pair in pairs:
                held[pair].add(base)
    for pair in combined - set(held):
        held[pair].add("combined")
    return dict(held)


def accession_symbols(hgnc_path: Path) -> dict[str, str]:
    """UniProt accession -> HGNC symbol, from HGNC's complete set (its uniprot_ids column), for gene nodes, which carry
    no accession."""
    mapping = {}
    with open(hgnc_path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            for accession in (row.get("uniprot_ids") or "").replace('"', "").split("|"):
                if accession.strip():
                    mapping.setdefault(accession.strip(), row["symbol"].strip())
    return mapping


def negatome_edge_columns(evidence: pd.DataFrame, negatome: dict[frozenset[str], set[str]], symbol_of_accession: dict[str, str]) -> pd.DataFrame:
    """Per row of the edge evidence table: negatome_negative (the independent sets holding the pair, counting "combined"
    as one), negatome_positive (always 0) and negatome_sets. An end is matched by its accession when it is a protein
    node that names one, and by its gene symbol otherwise."""
    by_symbols: dict[frozenset[str], set[str]] = defaultdict(set)
    for pair, sets in negatome.items():
        symbols = [symbol_of_accession.get(accession) for accession in pair]
        if None not in symbols and symbols[0] != symbols[1]:
            by_symbols[frozenset(symbols)] |= sets
    counts, labels = [], []
    for source, target in zip(evidence["source_id"], evidence["target_id"]):
        sets: set[str] = set()
        accessions = (accession_of(source), accession_of(target))
        if None not in accessions and accessions[0] != accessions[1]:
            sets |= negatome.get(frozenset(accessions), set())
        symbols = (symbol_of(source), symbol_of(target))
        if symbols[0] != symbols[1]:
            sets |= by_symbols.get(frozenset(symbols), set())
        counts.append(len(sets & set(BASE_SETS)) or (1 if sets else 0))
        labels.append(";".join(sorted(sets)))
    return pd.DataFrame({"negatome_negative": np.array(counts, dtype=np.int64), "negatome_positive": np.zeros(len(evidence), dtype=np.int64),
                         "negatome_sets": labels}, index=evidence.index)
