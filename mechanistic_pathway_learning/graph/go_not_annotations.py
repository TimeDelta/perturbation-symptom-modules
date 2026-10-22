"""Gene Ontology NOT-qualified molecular functions as negative observations on the graph's edges (decision 9.91).

What GO says a NOT means (geneontology.github.io/docs/go-annotations/, read 22 October 2026): "NOT statements are only
used when a user might expect that the gene product would have a specific biological property", "The NOT modifier is
not used for negative or inconclusive experimental results", "Negative, or NOT annotations propagate down to more
specific child terms", and "Both positive and NOT statements can be used between a single gene product and a GO term
when there are unresolved conflicting experimental findings in the literature".

The rules. configs/go_not_edge_rules.csv names the molecular functions whose absence rules out an edge type, and how:
  out_of_protein  every edge of the relation out of the annotated protein (no DNA-binding transcription factor activity
                  rules out its regulation edges; no G protein-coupled receptor activity its edges into a G alpha
                  subunit; no kinase activity its phosphorylation edges, of which the graph has none);
  partner         the binds edge between the protein and the partner the annotation names in its With/From column (NOT
                  protein binding, or a narrower binding term, with that partner);
  catalysis       its catalyzed_by edges: all of them, into non-transport reactions, for NOT catalytic activity; for a
                  narrower activity, those into reactions whose every EC number (Human-GEM's SBML annotation) falls
                  under the NOT term or a term below it; for NOT transporter activity, those into transport reactions.
A NOT on the rule's term or on a term above it (through is_a) applies the rule, since a NOT propagates down. A NOT whose
gene also carries a positive annotation to the same term or a term below it is the unresolved conflict GO describes and
is counted in the summary and not as an observation. Independent observations are distinct (term, reference) pairs.

No likelihood ratio. No published measurement of how often a NOT annotation is wrong was found (decision 9.91), so
configs/edge_negative_likelihood_ratios.csv leaves the row blank and the observations move no prior; they are recorded
and counted for the owner. GO states no positive edge observations in this sense: a positive function says what a
protein can do, not which edge it has, so go_not_positive is always 0.
"""
from __future__ import annotations

import csv
import gzip
import re
import xml.etree.ElementTree as ElementTree
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.graph.edge_evidence import accession_of, symbol_of

DEFAULT_RULES = Path("configs/go_not_edge_rules.csv")
DEFAULT_GAF = Path("data/raw/gene_ontology/goa_human.gaf.gz")
DEFAULT_OBO = Path("data/raw/gene_ontology/go-basic.obo")
DEFAULT_SBML = Path("data/raw/Human-GEM/model/Human-GEM.xml")
G_ALPHA_GENE_SYMBOLS = frozenset({"GNAS", "GNAL", "GNAI1", "GNAI2", "GNAI3", "GNAO1", "GNAZ", "GNAQ", "GNA11", "GNA12", "GNA13", "GNA14", "GNA15",
                                  "GNAT1", "GNAT2", "GNAT3"})  # the whole families (decision 9.86 (2)), so a filter gap does not hide an edge
CATALYTIC_ACTIVITY = "GO:0003824"
EC_REFERENCE = re.compile(r"ec-code/([0-9]+\.[0-9-]+\.[0-9-]+\.[0-9n-]+)")
RULE_KINDS = ("out_of_protein", "partner", "catalysis")


@dataclass(frozen=True)
class NotRule:
    go_id: str
    go_name: str
    kind: str
    relations: frozenset[str]
    target_filter: str


@dataclass(frozen=True)
class NotAnnotation:
    accession: str
    symbol: str
    go_id: str
    reference: str
    evidence_code: str
    partners: tuple[str, ...]


def read_rules(path: Path = DEFAULT_RULES) -> list[NotRule]:
    rules = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["rule"] not in RULE_KINDS:
                raise ValueError(f"{path}: unknown rule {row['rule']!r}")
            rules.append(NotRule(row["go_id"].strip(), row["go_name"].strip(), row["rule"].strip(),
                                 frozenset(part.strip() for part in row["relation_type"].split(";") if part.strip()), row.get("target_filter", "").strip()))
    return rules


def read_is_a_and_ec(obo_path: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """(GO term -> its is_a parents, GO term -> its EC cross-references) from go-basic.obo."""
    parents: dict[str, set[str]] = defaultdict(set)
    ec_numbers: dict[str, set[str]] = defaultdict(set)
    current = None
    with open(obo_path, encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line in ("[Term]", "[Typedef]"):
                current = None
            elif line.startswith("id: GO:"):
                current = line[4:14]
            elif current is None:
                continue
            elif line.startswith("is_a: GO:"):
                parents[current].add(line[6:16])
            elif line.startswith("xref: EC:"):
                ec_numbers[current].add(line[len("xref: EC:"):].split()[0])
    return dict(parents), dict(ec_numbers)


def closure(term: str, links: dict[str, set[str]]) -> set[str]:
    """The term and every term reachable from it through the links."""
    seen, stack = {term}, [term]
    while stack:
        for following in links.get(stack.pop(), ()):
            if following not in seen:
                seen.add(following)
                stack.append(following)
    return seen


def children_of(parents: dict[str, set[str]]) -> dict[str, set[str]]:
    children: dict[str, set[str]] = defaultdict(set)
    for child, found in parents.items():
        for parent in found:
            children[parent].add(child)
    return dict(children)


def read_gaf_molecular_functions(gaf_path: Path) -> tuple[list[NotAnnotation], dict[str, set[str]], dict[tuple[str, str], set[str]]]:
    """(the NOT molecular-function annotations, gene accession -> its positive molecular-function terms, (accession,
    term) -> the partners of its positive annotations)."""
    opener = gzip.open if str(gaf_path).endswith(".gz") else open
    negatives, positive_terms, positive_partners = [], defaultdict(set), defaultdict(set)
    with opener(gaf_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("!"):
                continue
            columns = line.rstrip("\n").split("\t")
            if len(columns) < 15 or columns[8] != "F":
                continue
            partners = tuple(sorted({part.split(":", 1)[1].split("-")[0] for part in re.split(r"[|,]", columns[7]) if part.startswith("UniProtKB:")}))
            if "NOT" in columns[3].split("|"):
                negatives.append(NotAnnotation(columns[1], columns[2], columns[4], columns[5], columns[6], partners))
            else:
                positive_terms[columns[1]].add(columns[4])
                for partner in partners:
                    positive_partners[(columns[1], columns[4])].add(partner)
    return negatives, dict(positive_terms), dict(positive_partners)


def reaction_ec_numbers(sbml_path: Path) -> dict[str, set[str]]:
    """Reaction node id (MAR03905) -> the EC numbers its SBML annotation lists."""
    ec_numbers: dict[str, set[str]] = {}
    current = None
    for event, element in ElementTree.iterparse(str(sbml_path), events=("start", "end")):
        tag = element.tag.rsplit("}", 1)[-1]
        if event == "start" and tag == "reaction":
            current = str(element.get("id", ""))
            current = current[2:] if current.startswith("R_") else current
        elif event == "end" and current and tag == "li":
            match = EC_REFERENCE.search(element.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource", "") or "")
            if match:
                ec_numbers.setdefault(current, set()).add(match.group(1))
        elif event == "end" and tag == "reaction":
            current = None
            element.clear()
    return ec_numbers


def go_not_edge_columns(evidence: pd.DataFrame, nodes: pd.DataFrame, rules: list[NotRule], negatives: list[NotAnnotation],
                        positive_terms: dict[str, set[str]], positive_partners: dict[tuple[str, str], set[str]],
                        parents: dict[str, set[str]], ec_of_term: dict[str, set[str]], ec_of_reaction: dict[str, set[str]],
                        symbol_of_accession: dict[str, str]) -> tuple[pd.DataFrame, dict]:
    """Per row of the edge evidence table: go_not_negative (distinct term and reference pairs ruling the edge out),
    go_not_positive (always 0) and go_not_terms; with a summary per rule, the conflicted annotations counted there."""
    children = children_of(parents)
    descendants = lambda term: closure(term, children)  # noqa: E731 - a short local reader
    ancestors_of_rule = {rule.go_id: closure(rule.go_id, parents) for rule in rules}
    transport = set(nodes.node_id[nodes["is_transport"].map(lambda value: bool(value) if pd.notna(value) else False).astype(bool)]) \
        if "is_transport" in nodes.columns else set()
    reaction_nodes = set(nodes.node_id[nodes.node_type == "reaction"]) if "node_type" in nodes.columns else set()
    # (rule, annotation) -> what it rules out: a relation set out of the protein, a partner, or reactions
    ruled_out_of: dict[str, list[tuple[NotRule, NotAnnotation, set[str] | None]]] = defaultdict(list)  # protein symbol -> rules
    per_rule = {rule.go_id: {"annotations": 0, "conflicted": 0} for rule in rules}
    conflicted_by_symbol: dict[str, int] = defaultdict(int)
    for annotation in negatives:
        below = descendants(annotation.go_id)
        positive = positive_terms.get(annotation.accession, set())
        for rule in rules:
            applies_fully = annotation.go_id in ancestors_of_rule[rule.go_id]
            narrower_catalysis = rule.kind == "catalysis" and rule.go_id == CATALYTIC_ACTIVITY and not applies_fully and rule.go_id in closure(annotation.go_id, parents)
            narrower_binding = rule.kind == "partner" and not applies_fully and rule.go_id in closure(annotation.go_id, parents)
            if not (applies_fully or narrower_catalysis or narrower_binding):
                continue
            if rule.kind == "partner":
                if not annotation.partners:
                    continue
                conflict = any(partner in positive_partners.get((annotation.accession, term), set()) for term in below for partner in annotation.partners)
            else:
                conflict = bool(positive & below)
            per_rule[rule.go_id]["annotations"] += 1
            if conflict:
                per_rule[rule.go_id]["conflicted"] += 1
                conflicted_by_symbol[annotation.symbol] += 1
                continue
            reactions = None
            if narrower_catalysis:
                ec_numbers = set().union(*(ec_of_term.get(term, set()) for term in below))
                reactions = {reaction for reaction, found in ec_of_reaction.items() if found and found <= ec_numbers}
            ruled_out_of[annotation.symbol].append((rule, annotation, reactions))
    counts, terms = [], []
    for source, target, relation in zip(evidence["source_id"], evidence["target_id"], evidence["relation_type"]):
        source_symbol, relation = symbol_of(source), str(relation)
        found: set[tuple[str, str]] = set()
        for rule, annotation, reactions in ruled_out_of.get(source_symbol, ()):
            if relation not in rule.relations:
                continue
            accession = accession_of(source)
            if accession and accession != annotation.accession:
                continue
            if rule.kind == "out_of_protein":
                if rule.target_filter == "g_alpha" and symbol_of(target) not in G_ALPHA_GENE_SYMBOLS:
                    continue
            elif rule.kind == "partner":
                partner_symbols = {symbol_of_accession.get(partner, partner) for partner in annotation.partners}
                if symbol_of(target) not in partner_symbols and (accession_of(target) or "") not in annotation.partners:
                    continue
            elif rule.kind == "catalysis":
                if str(target) not in reaction_nodes:
                    continue
                if reactions is not None:
                    if str(target) not in reactions:
                        continue
                elif rule.target_filter == "transport" and str(target) not in transport:
                    continue
                elif rule.target_filter == "non_transport" and str(target) in transport:
                    continue
            found.add((annotation.go_id, annotation.reference))
        # a partner annotation on the target's side rules out the same undirected binding
        if relation == "binds":
            for rule, annotation, _ in ruled_out_of.get(symbol_of(target), ()):
                if rule.kind == "partner" and relation in rule.relations:
                    partner_symbols = {symbol_of_accession.get(partner, partner) for partner in annotation.partners}
                    if source_symbol in partner_symbols:
                        found.add((annotation.go_id, annotation.reference))
        counts.append(len(found))
        terms.append(";".join(sorted({term for term, _ in found})))
    table = pd.DataFrame({"go_not_negative": np.array(counts, dtype=np.int64), "go_not_positive": np.zeros(len(evidence), dtype=np.int64),
                          "go_not_terms": terms}, index=evidence.index)
    summary = {"not_molecular_function_annotations": len(negatives), "by_rule": per_rule, "genes_with_a_conflicted_not": len(conflicted_by_symbol),
               "relations_named_by_rules_absent_from_the_graph": sorted({relation for rule in rules for relation in rule.relations}
                                                                         - set(evidence["relation_type"].astype(str)))}
    return table, summary
