"""IntAct's curated negative interactions as an anchor set for the graph's protein edges.

What it is. IntAct records, beside its interactions, the pairs curators found reported as *not* interacting
(intact_negative.txt, PSI-MITAB 2.7). They are the one curated statement of "these two proteins do not bind" the
project has, and the report of 15 October 2026 on evidence priors names such a set as what the reliability of an
edge source cannot be estimated without: every edge source asserts presences only, so its specificity is
unidentifiable until something asserts an absence. The set is small (908 human pairs on 14 January 2026), so what it
supports is an audit figure per source, an upper bound on how often a source asserts a pair curators recorded as
non-interacting, and not a per-edge weight.

An isoform's absence is not the gene's (decision 9.88, 22 October 2026). 763 of the 983 records of the 14 January 2026
file come from one splice-isoform study (Yang et al. 2016, Cell 164:805, doi 10.1016/j.cell.2016.01.029, abstract
read in PubMed: "The majority of isoform pairs share less than 50% of their interactions"), and IntAct's curation
manual (section 4.6.9, as a research pass of 22 October 2026 quoted it) accepts an isoform negative only "provided there
is complementary positive interaction data for other isoform/s". So a record on
one isoform says that the gene pair does interact, through another isoform. Each end of a record is therefore kept as
IntAct names it and classed against UniProt's reviewed human proteome (data/raw/uniprot/uniprot_human_reviewed.tsv.gz,
which experiments/fetch_node_descriptor_sources.py downloads): `canonical`, a reviewed accession with no suffix, which
UniProt displays with the canonical isoform's sequence; `isoform`, an accession with an isoform suffix (Q07817-2,
including -1, since a curator who names isoform 1 is contrasting it with another); `chain`, a processed chain
(P01189-PRO_0000024969); `unreviewed`, an accession outside the reviewed proteome (an unreviewed entry such as the
IRAK4 entry F8VVZ1, one of the ORFeome isoform entries A0A0S2Z... or a retired accession). Only a record between two
canonical entries is a negative between whole proteins, and only such a record counts against a gene pair of the
graph. Both textbook cases this module flagged before, BCL2L1 isoform Q07817-2 with BAD and IRAK4 entry F8VVZ1 with
MYD88, are isoform records of that study.

Licence: IntAct is an EMBL-EBI resource; the EMBL-EBI terms of use (read 15 October 2026) impose no restriction
beyond the data owner's, and the IntAct data are released under CC BY 4.0 according to the resource's own
statements, which this session could not read from the script-rendered legal page; the licence is unverified, and
neither the release directory nor its README states one (read 22 October 2026).
"""
from __future__ import annotations

import csv
import gzip
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

HUMAN_TAXID = "taxid:9606"
GENE_NAME = re.compile(r"uniprotkb:([^|()]+)\(gene name\)")
# A UniProtKB identifier as PSI-MITAB writes it: the accession in UniProt's format, then an isoform suffix (-2), a
# processed chain (-PRO_0000024969) or nothing. Anchored at both ends, so a longer token is not read as an accession.
UNIPROTKB_IDENTIFIER = re.compile(r"^uniprotkb:((?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2}))(?:-(\d+)|-(PRO_\d+))?$")
DEFAULT_REVIEWED_PROTEOME = Path("data/raw/uniprot/uniprot_human_reviewed.tsv.gz")
CANONICAL, ISOFORM, CHAIN, UNREVIEWED = "canonical", "isoform", "chain", "unreviewed"


@dataclass(frozen=True)
class NegativePair:
    """One human-human record. An accession is kept as IntAct names it, isoform suffix included; a gene is UniProt's
    primary gene name for a canonical entry and IntAct's gene-name alias otherwise."""
    accession_a: str
    accession_b: str
    gene_a: str | None
    gene_b: str | None
    interaction_type: str
    detection_method: str
    publications: str
    entry_kind_a: str = CANONICAL
    entry_kind_b: str = CANONICAL

    @property
    def between_whole_proteins(self) -> bool:
        """True when both ends are canonical entries, the only records that count against a gene pair (decision 9.88)."""
        return self.entry_kind_a == CANONICAL and self.entry_kind_b == CANONICAL


def read_reviewed_proteome(path: Path = DEFAULT_REVIEWED_PROTEOME) -> dict[str, str]:
    """UniProt's reviewed human proteome as {accession: primary gene name} ('' for an entry with no gene name)."""
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return {row["Entry"].strip(): (row.get("Gene Names (primary)") or "").strip() for row in csv.DictReader(handle, delimiter="\t")}


def classify_identifier(identifier_field: str, gene_of_reviewed_accession: dict[str, str]) -> tuple[str, str, str] | None:
    """(accession as IntAct names it, entry kind, UniProt gene of a canonical entry or '') for the UniProtKB identifier of
    an interactor column; None when the interactor is not named by a UniProtKB identifier (an IntAct-only molecule)."""
    for part in identifier_field.split("|"):
        match = UNIPROTKB_IDENTIFIER.match(part.strip())
        if not match:
            continue
        accession, isoform_number, chain = match.groups()
        if isoform_number:
            return f"{accession}-{isoform_number}", ISOFORM, ""
        if chain:
            return f"{accession}-{chain}", CHAIN, ""
        if accession in gene_of_reviewed_accession:
            return accession, CANONICAL, gene_of_reviewed_accession[accession]
        return accession, UNREVIEWED, ""
    return None


def read_human_negative_pairs(path: Path, gene_of_reviewed_accession: dict[str, str]) -> list[NegativePair]:
    """Every human-human row whose two interactors are UniProtKB entries, each end classed against the reviewed proteome
    (read_reviewed_proteome). Without the proteome a plain accession cannot be told from an unreviewed entry, so the
    argument is required."""
    if not gene_of_reviewed_accession:
        raise ValueError("the reviewed UniProt proteome is empty: an accession cannot be classed as canonical without it")
    pairs = []
    with open(path, encoding="utf-8", newline="") as negative_file:
        reader = csv.reader(negative_file, delimiter="\t")
        header = next(reader)
        column = {name.lstrip("#"): index for index, name in enumerate(header)}
        for row in reader:
            if HUMAN_TAXID not in row[column["Taxid interactor A"]] or HUMAN_TAXID not in row[column["Taxid interactor B"]]:
                continue
            end_a = classify_identifier(row[column["ID(s) interactor A"]], gene_of_reviewed_accession)
            end_b = classify_identifier(row[column["ID(s) interactor B"]], gene_of_reviewed_accession)
            if end_a is None or end_b is None:
                continue
            alias_a = GENE_NAME.search(row[column["Alias(es) interactor A"]])
            alias_b = GENE_NAME.search(row[column["Alias(es) interactor B"]])
            gene_a = end_a[2] or (alias_a.group(1) if alias_a else None)
            gene_b = end_b[2] or (alias_b.group(1) if alias_b else None)
            pairs.append(NegativePair(end_a[0], end_b[0], gene_a, gene_b, row[column["Interaction type(s)"]], row[column["Interaction detection method(s)"]],
                                      row[column["Publication Identifier(s)"]], end_a[1], end_b[1]))
    return pairs


def gene_pairs_between_whole_proteins(pairs: list[NegativePair]) -> set[frozenset[str]]:
    """The gene pairs a negative between two canonical entries names, the only ones that contest a graph edge."""
    return {frozenset((pair.gene_a, pair.gene_b)) for pair in pairs if pair.between_whole_proteins and pair.gene_a and pair.gene_b}


def symbol_of_node(nodes: pd.DataFrame) -> dict[str, str]:
    """node id -> gene symbol for gene and protein nodes (a protein node's symbol is its gene's)."""
    symbols = {}
    for row in nodes.itertuples(index=False):
        symbol = getattr(row, "gene_symbol", None)
        if isinstance(symbol, str) and symbol and getattr(row, "node_type", "") in ("gene", "protein"):
            symbols[str(row.node_id)] = symbol
    return symbols


def contradicted_edges(pairs: list[NegativePair], edges: pd.DataFrame, nodes: pd.DataFrame) -> pd.DataFrame:
    """The graph edges whose two ends are a pair curators recorded as non-interacting between whole proteins (two
    canonical entries), in either direction, with the pair's provenance. A record on an isoform, a chain or an
    unreviewed entry contests nothing (decision 9.88)."""
    negative_by_symbols: dict[frozenset[str], NegativePair] = {}
    for pair in pairs:
        if pair.between_whole_proteins and pair.gene_a and pair.gene_b:
            negative_by_symbols[frozenset((pair.gene_a, pair.gene_b))] = pair
    symbols = symbol_of_node(nodes)
    rows = []
    for edge in edges.itertuples(index=False):
        symbol_a, symbol_b = symbols.get(str(edge.source_id)), symbols.get(str(edge.target_id))
        if not symbol_a or not symbol_b or symbol_a == symbol_b:
            continue
        pair = negative_by_symbols.get(frozenset((symbol_a, symbol_b)))
        if pair is None:
            continue
        rows.append({"source_id": edge.source_id, "target_id": edge.target_id, "relation_type": getattr(edge, "relation_type", ""),
                     "sign": getattr(edge, "sign", None), "evidence_source": getattr(edge, "evidence_source", ""),
                     "intact_accession_a": pair.accession_a, "intact_accession_b": pair.accession_b, "intact_interaction_type": pair.interaction_type,
                     "intact_detection_method": pair.detection_method, "intact_publications": pair.publications})
    return pd.DataFrame(rows, columns=["source_id", "target_id", "relation_type", "sign", "evidence_source", "intact_accession_a", "intact_accession_b",
                                       "intact_interaction_type", "intact_detection_method", "intact_publications"])


def audit(pairs: list[NegativePair], edges: pd.DataFrame, nodes: pd.DataFrame) -> dict:
    """Per edge source: how many of its protein-protein edges fall on a pair curators recorded as non-interacting
    between whole proteins, against how many of its edges join two proteins those records name at all (the exposure),
    so a source is judged on the pairs the anchor set can speak to. The records set aside, on an isoform, a chain or an
    unreviewed entry, are counted by the kinds of their two ends (decision 9.88)."""
    whole = [pair for pair in pairs if pair.between_whole_proteins]
    named = {gene for pair in whole for gene in (pair.gene_a, pair.gene_b) if gene}
    symbols = symbol_of_node(nodes)
    exposed: Counter = Counter()
    for edge in edges.itertuples(index=False):
        symbol_a, symbol_b = symbols.get(str(edge.source_id)), symbols.get(str(edge.target_id))
        if symbol_a and symbol_b and symbol_a != symbol_b and symbol_a in named and symbol_b in named:
            exposed[str(getattr(edge, "evidence_source", ""))] += 1
    contradicted = contradicted_edges(pairs, edges, nodes)
    by_source: dict[str, dict] = defaultdict(lambda: {"edges_on_named_proteins": 0, "edges_on_a_negative_pair": 0})
    for source, count in exposed.items():
        by_source[source]["edges_on_named_proteins"] = count
    for source, count in Counter(contradicted.evidence_source.astype(str)).items():
        by_source[source]["edges_on_a_negative_pair"] = int(count)
    set_aside = Counter("+".join(sorted((pair.entry_kind_a, pair.entry_kind_b))) for pair in pairs if not pair.between_whole_proteins)
    gene_pairs = gene_pairs_between_whole_proteins(pairs)
    return {"human_negative_records": len(pairs), "records_between_whole_proteins": len(whole),
            "records_set_aside_by_entry_kinds": dict(set_aside.most_common()),
            "gene_pairs_between_whole_proteins": sum(1 for pair in gene_pairs if len(pair) == 2),
            "proteins_named": len(named), "edges_on_a_negative_pair": int(len(contradicted)), "by_source": dict(sorted(by_source.items())),
            "contradicted": contradicted.to_dict("records")}


def write_audit(path: Path, result: dict) -> None:
    path.write_text(json.dumps(result, indent=1, default=str) + "\n", encoding="utf-8")
