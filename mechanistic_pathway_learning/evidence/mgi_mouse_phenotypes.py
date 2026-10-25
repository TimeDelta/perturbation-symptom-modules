"""MGI's genotype-phenotype annotations as two mouse report sources, MGI-literature and MGI-screen (decision 9.93).

Why. IMPC was the only non-human source on the label side, so in the calibrated reliability regression
(evidence/calibrated_reliability.py) the column species:mouse equalled source:IMPC-knockout and a species effect could
not be told from a pipeline effect. MGI curates mouse phenotypes from two other kinds of origin: the published
literature, and direct loads from industrial knockout and mutagenesis screens. Each becomes a source of its own, so
species, source and source x direction can be estimated apart. The owner, 24 October 2026, on that proposal: "sure.
implement it". Every row is class animal: a soft prior entering training only through --soft-prior-reports, never a
label (9.48, 9.50; the owner: "Leave it in since the negatives aren't labels").

The files (MGI reports, https://www.informatics.jax.org/downloads/reports/, pinned by SHA-256 in
scripts/fetch_raw_sources.sh): MGI_PhenoGenoMP.rpt, one row per (genotype, MP term, reference) with the allelic
composition, the allele symbols, the genetic background, the MP id, the PubMed id (empty for a direct load), the
markers and the genotype id; MGI_PhenotypicAllele.rpt, one row per allele with its type and attributes ("Allele
Attribute"); and the MP ontology (MPheno_OBO.ontology, the same file as the mammalian-phenotype-ontology release
v2026-09-23). Licence: "MGI data and annotations are licensed under a Creative Commons Attribution 4.0 International
License (CC-BY)" (https://www.informatics.jax.org/mgihome/other/copyright.shtml, read 24 October 2026).

Which rows. A genotype is read when every allele in it other than the wild type belongs to one marker (so a double
mutant, a transgene at another locus or a recombinase driver is left out) and the marker maps to one human gene by
HGNC's MGI ids, one to one, as for IMPC.
  - MGI-literature: rows with a PubMed id whose alleles are none of them a consortium allele (a superscript naming
    IMPC, KOMP, EUCOMM, EUCOMMtools or NCOM; CONSORTIUM_PATTERN), so a published paper on an IMPC line does not
    repeat IMPC.
  - MGI-screen: rows without a PubMed id whose alleles all come from one of the loads of configs/mgi_screen_loads.csv
    (Lexicon, Deltagen, the Beutler lab's Mutagenetix ENU screen, the JAX Neuroscience Mutagenesis Facility), matched
    by the allele's laboratory code in its superscript and, where the config gives one, by the producer in the
    allele's name.
  - Every other row is counted and not read: consortium alleles (IMPC's own source), other direct loads, rows with a
    PubMed id and a consortium allele.

Mapping. An MP term maps through configs/impc_symptom_crosswalk_fine.csv (the crosswalk IMPC reads, with its validity
classes) and so does each of its is_a descendants, except those configs/mgi_mp_descendant_exclusions.csv lists. Why
descendants: MGI's curators annotate to the most specific term, so "impaired spatial working memory" (MP:0014370) is
an annotation the crosswalk's "abnormal spatial working memory" covers by definition, while IMPC's pipeline asserts a
fixed set of terms and is read on the exact ones. The exclusions are the descendants that state the opposite
direction (enhanced spatial working memory under abnormal spatial working memory) or a response to a challenge
rather than the baseline readout (hyperactivity elicited by ethanol or by feed restriction, handling-induced
hyperactivity and nervousness, compensatory feeding after a fast).

MP:0002169, "no abnormal phenotype detected". It is a statement about the whole genotype on whatever was examined,
not about a test, so by default it is no absence for any symptom: it is written to a table of its own
(normal_genotypes) and counted. With count_normal_as_absence (the builder's --count-no-abnormal-phenotype-as-absence)
it becomes one absence per read symptom (relation induces) for the genotype, unless the genotype also carries a call
among that symptom's terms, and those rows carry whole_genotype_normal True so a reader can tell them apart.

Allele direction (the keying of the v5 tables under --allele-perturbations, decision 9.54): from MGI's allele
attributes.
  - loss of function: Null/knockout, Hypomorph, Knockdown and Dominant negative (a dominant-negative product lowers
    the activity of the wild-type product, the reading 9.54 gave Gene2Phenotype's category); keyed to the gene, seeded
    -1.
  - gain of function: Constitutively active; keyed "<gene>|gain_of_function", seeded +1, as a hypermorph is.
  - both kinds on one allele, or on the alleles of one genotype: a conflict, not read.
  - untyped: an allele whose attributes are empty, "Not Specified" or "Not Applicable" (most ENU alleles), and a gene
    trap whose only other attributes are those of a tool (a reporter in the trap cassette); keyed to the gene as 9.54 keys an untyped human association, which "keeps the default, marked untyped",
    and carried with allele_direction "untyped"; include_untyped=False (--exclude-untyped-alleles) leaves them out.
  - not read: allele type Transgenic (a transgene inserted at the locus usually expresses another gene's product,
    often a mutant human one, so its phenotype is not the gene's; MGI_PhenotypicAllele.rpt names Tg(Prnp-SNCA*A53T)
    under 2310039L15Rik), an allele whose only functional attributes are Inserted expressed sequence, Humanized
    sequence, Modified isoform(s), Modified regulatory region or Altered localization (a stated change of the product
    that is neither a loss nor a gain), No functional change (a floxed allele before recombination), and tool alleles
    (Recombinase, Transactivator, Reporter or Epitope tag alone).
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from mechanistic_pathway_learning.evidence.evidence_reports import REPORT_COLUMNS
from mechanistic_pathway_learning.evidence.impc_knockout_phenotypes import VALIDITY_READ_BY_DEFAULT, VALIDITY_RUBRIC, CrosswalkRow

LITERATURE_SOURCE = "MGI-literature"
SCREEN_SOURCE = "MGI-screen"
EVIDENCE_CLASS = "animal"
NO_ABNORMAL_PHENOTYPE = "MP:0002169"
DEFAULT_SCREEN_LOADS_PATH = Path("configs/mgi_screen_loads.csv")
DEFAULT_DESCENDANT_EXCLUSIONS_PATH = Path("configs/mgi_mp_descendant_exclusions.csv")
CONSORTIUM_PATTERN = re.compile(r"\((?:IMPC|KOMP|EUCOMM|EUCOMMtools|NCOM)\)")
GENOTYPE_COLUMNS = ("allelic_composition", "allele_symbols", "genetic_background", "mp_term_id", "pubmed_id", "marker_ids", "genotype_id")
LOSS_ATTRIBUTES = frozenset({"Null/knockout", "Hypomorph", "Knockdown", "Dominant negative"})
GAIN_ATTRIBUTES = frozenset({"Constitutively active"})
SILENT_ATTRIBUTES = frozenset({"", "Not Specified", "Not Applicable"})
UNREAD_CHANGE_ATTRIBUTES = frozenset({"Inserted expressed sequence", "Humanized sequence", "Modified isoform(s)", "Modified regulatory region", "Altered localization"})
TOOL_ATTRIBUTES = frozenset({"Recombinase", "Transactivator", "Reporter", "Epitope tag", "Conditional ready", "RMCE-ready", "Inducible", "Endonuclease",
                             "Transposase", "Transposon concatemer", "Lineage barcode", "Inducible degradation"})
EXTRA_COLUMNS = ("rubric_cross_species", "rubric_proxy_validity", "allele_direction", "mgi_genotype_id", "mgi_allele_ids", "mgi_origin", "whole_genotype_normal")


@dataclass(frozen=True)
class MgiAllele:
    allele_id: str
    symbol: str
    name: str
    allele_type: str
    attributes: frozenset
    marker_id: str


@dataclass(frozen=True)
class ScreenLoad:
    load: str
    superscript_pattern: re.Pattern
    name_contains: str


def read_mp_ontology(path: Path) -> tuple[dict[str, str], dict[str, set[str]]]:
    """MP term id -> name, and term id -> its direct is_a children, from an OBO file; obsolete terms are left out."""
    names: dict[str, str] = {}
    parents: dict[str, set[str]] = defaultdict(set)
    obsolete: set[str] = set()
    current = None
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line.startswith("["):
                current = None
            elif line.startswith("id: MP:"):
                current = line[4:].strip()
            elif current and line.startswith("name: "):
                names[current] = line[6:].strip()
            elif current and line.startswith("is_a: "):
                parents[current].add(line[6:].split("!")[0].strip())
            elif current and line.strip() == "is_obsolete: true":
                obsolete.add(current)
    children: dict[str, set[str]] = defaultdict(set)
    for child, parent_set in parents.items():
        if child in obsolete:
            continue
        for parent in parent_set:
            children[parent].add(child)
    return {term: name for term, name in names.items() if term not in obsolete}, children


def descendants(term: str, children: dict[str, set[str]]) -> set[str]:
    """The term and every term below it by is_a."""
    found, stack = {term}, [term]
    while stack:
        for child in children.get(stack.pop(), ()):
            if child not in found:
                found.add(child)
                stack.append(child)
    return found


def read_descendant_exclusions(path: Path = DEFAULT_DESCENDANT_EXCLUSIONS_PATH) -> dict[str, str]:
    """MP term id -> why it is not read through its ancestor's crosswalk row."""
    with open(path, newline="", encoding="utf-8") as handle:
        return {row["mp_term_id"].strip(): row["reason"] for row in csv.DictReader(handle)}


def crosswalk_term_map(crosswalk: list[CrosswalkRow], validities: tuple[str, ...], children: dict[str, set[str]], exclusions: dict[str, str]
                       ) -> tuple[dict[str, list[tuple[CrosswalkRow, str]]], dict[str, set[str]]]:
    """(term -> [(crosswalk row, the crosswalk term it was reached from)] for the rows read, symptom -> every term of the
    symptom over all rows, which blocks an absence). A listed exclusion is not reached through a descendant walk, and
    nothing below it is either."""
    def walk(term: str) -> set[str]:
        found, stack = {term}, [term]
        while stack:
            for child in children.get(stack.pop(), ()):
                if child not in found and child not in exclusions:
                    found.add(child)
                    stack.append(child)
        return found

    term_map: dict[str, list[tuple[CrosswalkRow, str]]] = defaultdict(list)
    terms_of_symptom: dict[str, set[str]] = defaultdict(set)
    for row in crosswalk:
        for crosswalk_term in row.mp_term_ids:
            reached = walk(crosswalk_term)
            terms_of_symptom[row.symptom].update(reached)
            if row.validity in validities:
                for term in reached:
                    term_map[term].append((row, crosswalk_term))
    return term_map, terms_of_symptom


def read_alleles(path: Path) -> dict[str, MgiAllele | None]:
    """Allele symbol -> MgiAllele from MGI_PhenotypicAllele.rpt; a symbol on two rows with different types, attributes
    or markers maps to None (ambiguous)."""
    alleles: dict[str, MgiAllele | None] = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                continue
            allele = MgiAllele(fields[0], fields[1], fields[2], fields[3], frozenset(attribute.strip() for attribute in fields[4].split("|")), fields[6])
            if fields[1] in alleles and alleles[fields[1]] is not None and (alleles[fields[1]].allele_type, alleles[fields[1]].attributes, alleles[fields[1]].marker_id) != (allele.allele_type, allele.attributes, allele.marker_id):
                alleles[fields[1]] = None
            elif fields[1] not in alleles:
                alleles[fields[1]] = allele
    return alleles


def read_screen_loads(path: Path = DEFAULT_SCREEN_LOADS_PATH) -> list[ScreenLoad]:
    with open(path, newline="", encoding="utf-8") as handle:
        return [ScreenLoad(row["load"].strip(), re.compile(row["superscript_pattern"].strip()), row.get("allele_name_contains", "").strip()) for row in csv.DictReader(handle)]


def superscript(symbol: str) -> str:
    """The part of an allele symbol inside <>: Rb1<tm1Tyj> -> tm1Tyj; empty for a symbol without one."""
    match = re.search(r"<(.*)>", symbol)
    return match.group(1) if match else ""


def is_wild_type(symbol: str) -> bool:
    return superscript(symbol) == "+"


def allele_direction(allele: MgiAllele) -> tuple[str | None, str]:
    """(loss_of_function, gain_of_function or untyped; or None) and the reason, from the allele's type and attributes
    (module docstring)."""
    if allele.allele_type == "Transgenic":
        return None, "transgenic"
    attributes = set(allele.attributes)
    loss, gain = attributes & LOSS_ATTRIBUTES, attributes & GAIN_ATTRIBUTES
    if loss and gain:
        return None, "loss and gain attributes"
    if loss:
        return "loss_of_function", "attribute"
    if gain:
        return "gain_of_function", "attribute"
    if "No functional change" in attributes:
        return None, "no functional change"
    if attributes & UNREAD_CHANGE_ATTRIBUTES:
        return None, "a change of the product that is neither loss nor gain"
    if attributes - SILENT_ATTRIBUTES - TOOL_ATTRIBUTES:
        return None, "unlisted attribute"
    if attributes & TOOL_ATTRIBUTES and allele.allele_type != "Gene trapped":
        return None, "a tool allele"
    return "untyped", "no functional attribute"


def zygosity(allelic_composition: str) -> str:
    """homozygous, heterozygous (one wild-type allele), hemizygous (an allele against Y or a deletion) or compound."""
    parts = [part.strip() for part in allelic_composition.split("/")]
    if len(parts) == 1:
        return "hemizygous"
    if any(is_wild_type(part) for part in parts):
        return "heterozygous"
    if any(part.endswith("<Y>") or part == "Y" for part in parts):
        return "hemizygous"
    return "homozygous" if len(set(parts)) == 1 else "compound heterozygous"


def read_genotype_annotations(path: Path) -> Iterator[dict]:
    """MGI_PhenoGenoMP.rpt rows as dicts of GENOTYPE_COLUMNS."""
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= len(GENOTYPE_COLUMNS):
                yield dict(zip(GENOTYPE_COLUMNS, fields[: len(GENOTYPE_COLUMNS)]))


def origin_of(allele_symbols: list[str], alleles: dict[str, MgiAllele | None], pubmed_id: str, loads: list[ScreenLoad]) -> tuple[str, str]:
    """(literature, screen, consortium, consortium_in_literature or other_direct_load; the load's name for a screen)."""
    consortium = any(CONSORTIUM_PATTERN.search(superscript(symbol)) for symbol in allele_symbols)
    if pubmed_id:
        return ("consortium_in_literature", "") if consortium else ("literature", "")
    if consortium:
        return "consortium", ""
    matched = set()
    for symbol in allele_symbols:
        allele = alleles.get(symbol)
        found = [load.load for load in loads if load.superscript_pattern.search(superscript(symbol))
                 and (not load.name_contains or (allele is not None and load.name_contains.lower() in allele.name.lower()))]
        if len(found) != 1:
            return "other_direct_load", ""
        matched.add(found[0])
    return ("screen", matched.pop()) if len(matched) == 1 else ("other_direct_load", "")


def report_row(source: str, perturbation_id: str, node_id: str, sign: float, symptom: str, relation: str, validity: str) -> dict:
    row = {column: "" for column in REPORT_COLUMNS}
    row.update({
        "perturbation_id": perturbation_id, "perturbation_type": "gene", "perturbation_label": perturbation_id, "symptom": symptom, "relation": relation,
        "evidence_class": EVIDENCE_CLASS, "source": source, "frequency": None, "frequency_denominator": None, "placebo_flag": False, "onset": None, "sex": None,
        "pubmed_reference_count": 0, "rubric_frequency_known": 0.0, "rubric_evidence_code_pcs": 0.0, "rubric_evidence_code_tas": 0.0, "rubric_evidence_code_iea": 0.0,
        "rubric_placebo_controlled": 0.0, "rubric_curated_synopsis": 0.0, "rubric_log_sample_size": 0.0, "association_type": "", "rubric_causal_association": 0.0,
        "perturbation_nodes": json.dumps([[node_id, sign, 1.0]]), "rubric_cross_species": 1.0, "rubric_proxy_validity": VALIDITY_RUBRIC.get(validity, 0.0),
        "whole_genotype_normal": False,
    })
    return row


def build_reports(genotype_rows: Iterable[dict], alleles: dict[str, MgiAllele | None], mouse_to_human: dict[str, str], node_of_symbol: dict[str, str],
                  crosswalk: list[CrosswalkRow], children: dict[str, set[str]], exclusions: dict[str, str], term_names: dict[str, str], loads: list[ScreenLoad],
                  origin_wanted: str, validities: tuple[str, ...] = VALIDITY_READ_BY_DEFAULT, count_normal_as_absence: bool = False,
                  include_untyped: bool = True, release_label: str = "", release_date: str = "") -> tuple[list[dict], list[dict], dict]:
    """(report rows, the genotypes annotated MP:0002169, counts) for origin_wanted "literature" or "screen"."""
    if origin_wanted not in ("literature", "screen"):
        raise ValueError(f"origin_wanted must be literature or screen, not {origin_wanted!r}")
    source = LITERATURE_SOURCE if origin_wanted == "literature" else SCREEN_SOURCE
    term_map, terms_of_symptom = crosswalk_term_map(crosswalk, validities, children, exclusions)
    absence_rows = [row for row in crosswalk if row.validity in validities and row.relation == "induces"]
    counts: dict = defaultdict(int)
    genotypes: dict[str, dict] = {}
    for annotation in genotype_rows:
        counts["annotation_rows"] += 1
        symbols = [symbol.strip() for symbol in annotation["allele_symbols"].split("|") if symbol.strip()]
        origin, load = origin_of(symbols, alleles, annotation["pubmed_id"].strip(), loads)
        counts[f"origin:{origin}"] += 1
        if origin != origin_wanted:
            continue
        markers = [marker.strip() for marker in annotation["marker_ids"].split("|") if marker.strip()]
        mutant = [symbol for symbol in symbols if not is_wild_type(symbol)]
        resolved = [alleles.get(symbol) for symbol in mutant]
        if len(markers) != 1 or not mutant or any(allele is None or allele.marker_id != markers[0] for allele in resolved):
            counts["not_one_gene_or_allele_unresolved"] += 1
            continue
        directions = set()
        reason = ""
        for allele in resolved:
            direction, why = allele_direction(allele)
            if direction is None:
                reason = why
                break
            directions.add(direction)
        if reason:
            counts[f"allele_not_read:{reason}"] += 1
            continue
        typed = directions - {"untyped"}
        if len(typed) > 1:
            counts["allele_not_read:alleles of the genotype disagree"] += 1
            continue
        direction = typed.pop() if typed else "untyped"
        if direction == "untyped" and not include_untyped:
            counts["allele_not_read:untyped, left out"] += 1
            continue
        human = mouse_to_human.get(markers[0])
        if human is None:
            counts["no_one_to_one_human_gene"] += 1
            continue
        node = node_of_symbol.get(human)
        if node is None:
            counts["human_gene_not_in_graph"] += 1
            continue
        record = genotypes.setdefault(annotation["genotype_id"], {"human": human, "node": node, "direction": direction, "terms": defaultdict(set), "annotation": annotation,
                                                                   "allele_ids": ";".join(sorted(allele.allele_id for allele in resolved)), "load": load})
        record["terms"][annotation["mp_term_id"]].add(annotation["pubmed_id"].strip())

    rows: list[dict] = []
    normal_genotypes: list[dict] = []
    for genotype_id, record in sorted(genotypes.items()):
        perturbation_id = record["human"] if record["direction"] != "gain_of_function" else f"{record['human']}|gain_of_function"
        sign = 1.0 if record["direction"] == "gain_of_function" else -1.0
        annotation = record["annotation"]
        state = zygosity(annotation["allelic_composition"])
        described = (f"mouse {annotation['allelic_composition']} ({state}; {annotation['genetic_background']}); allele {record['direction'].replace('_', ' ')} by MGI's "
                     f"attributes; human orthologue {record['human']} by HGNC" + (f"; load {record['load']}" if record["load"] else ""))
        extra = {"allele_direction": record["direction"], "mgi_genotype_id": genotype_id, "mgi_allele_ids": record["allele_ids"], "mgi_origin": record["load"] or origin_wanted}
        called_symptoms = set()
        for term, pubmed_ids in sorted(record["terms"].items()):
            for crosswalk_row, crosswalk_term in term_map.get(term, []):
                called_symptoms.add(crosswalk_row.symptom)
                for pubmed_id in sorted(pubmed_ids):
                    row = report_row(source, perturbation_id, record["node"], sign, crosswalk_row.symptom, crosswalk_row.relation, crosswalk_row.validity)
                    row.update(extra)
                    row.update({
                        "report_id": f"{source}|{perturbation_id}|{term}|{crosswalk_row.symptom}|{crosswalk_row.relation}|{genotype_id}|{pubmed_id}",
                        "report_value": 1, "source_record_id": genotype_id, "source_record_label": annotation["allelic_composition"], "source_term_id": term,
                        "source_term_label": term_names.get(term, ""), "evidence_code": f"mgi_{origin_wanted}_call",
                        "references": f"PMID:{pubmed_id}" if pubmed_id else f"MGI {release_label}".strip(), "pubmed_reference_count": 1 if pubmed_id else 0,
                        "evidence_date": release_date, "evidence_date_source": "release",
                        "model_description": described + ("" if term == crosswalk_term else f"; {term} read through its ancestor {crosswalk_term}"),
                        "limitations": (f"cross-species: a mouse {term_names.get(term, term)} read as {crosswalk_row.symptom} with {crosswalk_row.validity} validity "
                                        f"({crosswalk_row.note}); " + ("a published mouse line, often made because the gene was already tied to the phenotype"
                                                                       if origin_wanted == "literature" else "a screen without a published paper; the test battery is the producer's")),
                    })
                    rows.append(row)
                    counts["calls"] += 1
        if NO_ABNORMAL_PHENOTYPE in record["terms"]:
            normal_genotypes.append({"perturbation_id": perturbation_id, "mgi_genotype_id": genotype_id, "allelic_composition": annotation["allelic_composition"],
                                     "allele_direction": record["direction"], "pubmed_ids": ";".join(sorted(record["terms"][NO_ABNORMAL_PHENOTYPE])), "load": record["load"]})
            counts["genotypes_with_no_abnormal_phenotype"] += 1
            if count_normal_as_absence:
                for crosswalk_row in absence_rows:
                    if record["terms"].keys() & terms_of_symptom[crosswalk_row.symptom] or crosswalk_row.symptom in called_symptoms:
                        counts["absences_blocked_by_a_call"] += 1
                        continue
                    pubmed_ids = sorted(record["terms"][NO_ABNORMAL_PHENOTYPE])
                    row = report_row(source, perturbation_id, record["node"], sign, crosswalk_row.symptom, crosswalk_row.relation, crosswalk_row.validity)
                    row.update(extra)
                    row.update({
                        "report_id": f"{source}|{perturbation_id}|{NO_ABNORMAL_PHENOTYPE}|{crosswalk_row.symptom}|absent|{genotype_id}",
                        "report_value": 0, "source_record_id": genotype_id, "source_record_label": annotation["allelic_composition"], "source_term_id": NO_ABNORMAL_PHENOTYPE,
                        "source_term_label": "no abnormal phenotype detected", "evidence_code": f"mgi_{origin_wanted}_no_abnormal_phenotype",
                        "references": f"PMID:{pubmed_ids[0]}" if pubmed_ids and pubmed_ids[0] else f"MGI {release_label}".strip(),
                        "evidence_date": release_date, "evidence_date_source": "release", "whole_genotype_normal": True, "model_description": described,
                        "limitations": (f"cross-species: a genotype found normal on whatever its examiners tested, read as an absence of {crosswalk_row.symptom}; "
                                        "the tests behind it are not stated, so this is not an absence at a known test's power"),
                    })
                    rows.append(row)
                    counts["absences_from_no_abnormal_phenotype"] += 1
    counts["genotypes_read"] = len(genotypes)
    counts["human_genes_with_calls"] = len({row["perturbation_id"] for row in rows if row["report_value"] == 1})
    return rows, normal_genotypes, dict(counts)
