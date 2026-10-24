"""HuRI's tested space as positive and negative observations on the graph's binds edges (decision 9.91).

HuRI (Luck et al. 2020, doi 10.1038/s41586-020-2188-x) screened every pair of a fixed gene set, Space III, nine times
with three yeast two-hybrid versions, so a pair inside that set is tested: detected or not. A binds edge between two
tested proteins is a positive when HuRI detected the pair and a negative when it did not. HuRI states direct binding
only, so nothing here speaks to activates, inhibits or regulation edges. The likelihood ratios are in
configs/edge_negative_likelihood_ratios.csv (graph/edge_negative_evidence.py quotes their sources).

The tested set. Space III is the 17,408 genes of human ORFeome v9.1. Its list is in the paper's supplementary table and
in horfdb; on 22 October 2026 nature.com answered the shell reader with a check that the visitor is human,
static-content.springer.com disallows every path to automated readers in its robots file, and horfdb.dfci.harvard.edu
served a certificate that does not verify, so the list was not read (docs/data_sources.md). In its place the tested set
is the genes with at least one HuRI interaction (8,275 proteins in the paper): each of them was in Space III, so every
pair of two of them was tested in all nine screens. It is a subset of Space III, biased toward proteins that work in
the assay, so the published sensitivity, which is for Space III as a whole, understates the sensitivity on it and the
negative ratio is nearer 1 than it would be. `space_iii_genes` takes the list when the owner supplies it.

Counted once. OmniPath imports HuRI (resource "HuRI"). A binds edge whose own resources include HuRI, or whose PubMed ids
include HuRI's paper, already carries the detection as one of its records, so its positive observation is recorded
(huri_status "detected_already_a_record") and not counted again.

The measurement of decision 9.91 (resource_precision): for each OmniPath resource that supplies binds edges, the fraction
of its pairs inside the tested set that HuRI detected, against the same fraction for a positive reference set (Lit-BM)
and for random pairs of the tested set, read as Venkatesan et al. 2009 (doi 10.1038/nmeth.1280) read their MAPPIT
retests: precision = (f - f_random) / (f_reference - f_random).
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.graph.edge_evidence import resources_of, split_pubmed_ids, symbol_of

BINDS_RELATION = "binds"
HURI_RESOURCES = frozenset({"HuRI"})
HURI_PUBMED_ID = "32296183"  # Luck et al. 2020
# the CCSB-DFCI screens' papers: HuRI (Luck 2020), HI-II-14 (Rolland 2014), H-I-05 (Rual 2005), Yu-11 (Yu 2011), Venkatesan-09, Yang-16
CCSB_SCREEN_PUBMED_IDS = frozenset({"32296183", "25416956", "16189514", "21516116", "19060904", "26871637"})
REFERENCE_RESOURCES_EXCLUDED = frozenset({"HuRI", "Lit-BM-17", "Lit-BM"})  # OmniPath imports both; scoring them against HuRI is circular
DEFAULT_HURI = Path("data/raw/huri/HuRI.tsv")
DEFAULT_LIT_BM = Path("data/raw/huri/Lit-BM.tsv")
DEFAULT_HGNC = Path("data/raw/hgnc/hgnc_complete_set.txt")
STATUSES = ("detected", "detected_already_a_record", "tested_not_detected", "outside_tested_space", "not_binds")


def read_ensembl_pairs(path: Path) -> list[tuple[str, str]]:
    """The two Ensembl gene ids of each row of an interactome-atlas table (HuRI.tsv, Lit-BM.tsv: two tab-separated ids)."""
    pairs = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            parts = line.strip().split("\t")
            if len(parts) >= 2 and parts[0].startswith("ENSG") and parts[1].startswith("ENSG"):
                pairs.append((parts[0].split(".")[0], parts[1].split(".")[0]))
    return pairs


def symbol_of_ensembl_gene(hgnc_path: Path) -> dict[str, str]:
    """Ensembl gene id -> approved HGNC symbol, from HGNC's complete set."""
    mapping = {}
    with open(hgnc_path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            ensembl = (row.get("ensembl_gene_id") or "").strip()
            if ensembl and row.get("symbol"):
                mapping[ensembl] = row["symbol"].strip()
    return mapping


def symbol_pairs(ensembl_pairs: list[tuple[str, str]], symbol_of_ensembl: dict[str, str]) -> tuple[set[frozenset[str]], dict]:
    """The pairs as unordered gene symbol pairs (a self-pair is a one-member set), with how many ids had no symbol."""
    pairs, unmapped = set(), set()
    for first, second in ensembl_pairs:
        symbols = [symbol_of_ensembl.get(first), symbol_of_ensembl.get(second)]
        unmapped.update(identifier for identifier, symbol in zip((first, second), symbols) if symbol is None)
        if None not in symbols:
            pairs.add(frozenset(symbols))
    return pairs, {"rows": len(ensembl_pairs), "pairs": len(pairs), "ensembl_ids_without_a_symbol": len(unmapped)}


def tested_genes(huri_pairs: set[frozenset[str]], space_iii_genes: set[str] | None = None) -> set[str]:
    """Space III when its gene list is given; else the genes HuRI detected an interaction for, a subset of it."""
    if space_iii_genes:
        return set(space_iii_genes)
    return {gene for pair in huri_pairs for gene in pair}


def huri_edge_columns(evidence: pd.DataFrame, huri_pairs: set[frozenset[str]], tested: set[str]) -> pd.DataFrame:
    """Per row of the edge evidence table (which carries source_id, target_id, relation_type and, when built, resources
    and pubmed_ids): huri_negative, huri_positive and huri_status."""
    resources = evidence["resources"] if "resources" in evidence.columns else pd.Series("", index=evidence.index)
    pubmed = evidence["pubmed_ids"] if "pubmed_ids" in evidence.columns else pd.Series("", index=evidence.index)
    negative, positive, status = [], [], []
    for source, target, relation, stated_by, identifiers in zip(evidence["source_id"], evidence["target_id"], evidence["relation_type"], resources, pubmed):
        if str(relation) != BINDS_RELATION:
            negative.append(0), positive.append(0), status.append("not_binds")
            continue
        first, second = symbol_of(source), symbol_of(target)
        if first not in tested or second not in tested:
            negative.append(0), positive.append(0), status.append("outside_tested_space")
            continue
        if frozenset((first, second)) in huri_pairs:
            own_record = bool(resources_of(stated_by) & HURI_RESOURCES) or HURI_PUBMED_ID in split_pubmed_ids(identifiers)
            negative.append(0), positive.append(0 if own_record else 1), status.append("detected_already_a_record" if own_record else "detected")
        else:
            negative.append(1), positive.append(0), status.append("tested_not_detected")
    return pd.DataFrame({"huri_negative": np.array(negative, dtype=np.int64), "huri_positive": np.array(positive, dtype=np.int64),
                         "huri_status": status}, index=evidence.index)


def wilson_interval(successes: int, trials: int, z: float = 1.959964) -> tuple[float, float]:
    """The 95% Wilson score interval of a proportion."""
    if trials == 0:
        return (math.nan, math.nan)
    proportion = successes / trials
    centre = (proportion + z * z / (2 * trials)) / (1 + z * z / trials)
    half = z * math.sqrt(proportion * (1 - proportion) / trials + z * z / (4 * trials * trials)) / (1 + z * z / trials)
    return (max(0.0, centre - half), min(1.0, centre + half))


def detection_rate(pairs: set[frozenset[str]], huri_pairs: set[frozenset[str]], tested: set[str]) -> dict:
    """Of the distinct pairs of two different tested genes, how many HuRI detected, with the 95% Wilson interval."""
    inside = [pair for pair in pairs if len(pair) == 2 and pair <= tested]
    detected = sum(pair in huri_pairs for pair in inside)
    low, high = wilson_interval(detected, len(inside))
    return {"pairs_inside_tested_space": len(inside), "detected": detected, "rate": detected / len(inside) if inside else math.nan,
            "rate_95_interval": [low, high]}


def random_pair_rate(huri_pairs: set[frozenset[str]], tested: set[str]) -> dict:
    """The detection rate of a uniformly random pair of two different tested genes, exactly: HuRI's pairs of two
    different tested genes over every such pair (the expectation of Venkatesan's random reference set, without its
    sampling error)."""
    detected = sum(1 for pair in huri_pairs if len(pair) == 2 and pair <= tested)
    possible = len(tested) * (len(tested) - 1) // 2
    return {"tested_genes": len(tested), "possible_pairs": possible, "detected": detected, "rate": detected / possible if possible else math.nan}


def precision_from_rates(rate: float, reference_rate: float, random_rate: float) -> float:
    """(f - f_random) / (f_reference - f_random), the reading of Venkatesan et al. 2009."""
    return (rate - random_rate) / (reference_rate - random_rate)


def graph_binds_pairs(evidence: pd.DataFrame, family: str = "signalling") -> set[frozenset[str]]:
    """The unordered symbol pairs of the graph's binds edges of the family."""
    selected = (evidence["relation_type"].astype(str) == BINDS_RELATION) & (evidence["family"].astype(str) == family)
    return {frozenset((symbol_of(source), symbol_of(target))) for source, target in zip(evidence.loc[selected, "source_id"], evidence.loc[selected, "target_id"])}


def resource_pairs(omnipath: pd.DataFrame, graph_pairs: set[frozenset[str]], screen_pubmed_ids: frozenset[str] = CCSB_SCREEN_PUBMED_IDS) -> dict[str, set[frozenset[str]]]:
    """Per OmniPath resource, the graph's binds pairs it states (raw rows expanded to complex members as the build
    expands them). A resource is not credited with a pair for which every reference it gives is a CCSB screen paper:
    IntAct, for one, deposits HuRI's pairs under HuRI's paper, and scoring HuRI's own pairs against HuRI is circular.
    A resource that gives no reference for the pair is credited."""
    from mechanistic_pathway_learning.graph.edge_evidence import members

    by_resource: dict[str, set[frozenset[str]]] = defaultdict(set)
    for source_cell, target_cell, sources_cell, references_cell in zip(omnipath["source_genesymbol"], omnipath["target_genesymbol"], omnipath["sources"],
                                                                       omnipath["references"]):
        pairs = {frozenset((source, target)) for source in members(source_cell) for target in members(target_cell)} & graph_pairs
        if not pairs:
            continue
        references: dict[str, set[str]] = defaultdict(set)
        for reference in str(references_cell).split(";") if isinstance(references_cell, str) else []:
            if ":" in reference:
                resource, identifier = reference.split(":", 1)
                references[resource.strip()].add(identifier.strip())
        for resource in resources_of(sources_cell):
            cited = references.get(resource, set())
            if cited and cited <= screen_pubmed_ids:
                continue
            by_resource[resource] |= pairs
    return dict(by_resource)


def resource_precision(by_resource: dict[str, set[frozenset[str]]], graph_pairs: set[frozenset[str]], huri_pairs: set[frozenset[str]],
                       lit_bm_pairs: set[frozenset[str]], tested: set[str], excluded: frozenset[str] = REFERENCE_RESOURCES_EXCLUDED) -> dict:
    """The measurement of decision 9.91: per resource supplying binds edges (HuRI and Lit-BM left out), its detection
    rate in the tested space and its precision against Lit-BM and random pairs, with the interval of the rate carried
    through the same formula."""
    reference = detection_rate(lit_bm_pairs, huri_pairs, tested)
    random = random_pair_rate(huri_pairs, tested)
    results = {}
    for resource, pairs in sorted(by_resource.items()):
        if resource in excluded:
            continue
        rate = detection_rate(pairs, huri_pairs, tested)
        low, high = rate["rate_95_interval"]
        results[resource] = {**rate, "binds_pairs": len(pairs),
                             "precision": precision_from_rates(rate["rate"], reference["rate"], random["rate"]) if rate["pairs_inside_tested_space"] else math.nan,
                             "precision_95_interval": [precision_from_rates(low, reference["rate"], random["rate"]),
                                                       precision_from_rates(high, reference["rate"], random["rate"])]}
    return {"reference_lit_bm": reference, "random_pairs": random, "all_graph_binds_pairs": detection_rate(graph_pairs, huri_pairs, tested),
            "excluded_resources": sorted(excluded), "by_resource": results}
