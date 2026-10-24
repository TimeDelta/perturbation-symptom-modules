"""SFARI Gene's mouse models as a mouse report source, SFARI-mouse-models (decision 9.93, 24 October 2026).

What the source is. SFARI Gene's animal-model module curates, per gene, each published mouse model and its phenotypic
profile: one row per test, with the category, the entity measured, the value change ("Increased", "Decreased", "No
change", "Not reported", and for rescue experiments "Restored", "Refractory" and the like), the experimental paradigm,
the age at testing and the paper. Unlike MGI's annotations it records the tests that found nothing, so a "No change"
row is a measured absence for its test's construct, as an IMPC procedure without a call is. The owner, 24 October
2026, on adding it with MGI as mouse sources of their own: "sure. implement it". Class animal: a soft prior through
--soft-prior-reports only, never a label (9.48, 9.50).

Pages. experiments/fetch_sfari_mouse_models.py reads https://gene.sfari.org/database/animal-models/
genetic-animal-models/<GENE>/Mus+musculus for every gene of the module's gene list through
experiments/read_public_page.py (robots rules and checks that the visitor is human respected) and pins each page by
SHA-256 in data/raw/sfari/manifest.tsv. parse_page reads a page into its model blocks and their rows.

Terms: "All data on SFARI Gene are derived from sources that are in the public domain, and we encourage users to
include such data in their publications, with appropriate citation of the primary data source, the SFARI Gene
website, and relevant publications describing SFARI Gene" (https://gene.sfari.org/terms-and-privacy/, read 24 October
2026). No licence is named; nothing in the terms bans this use.

Rows read.
  - Models: Model Type "Genetic", "Genetic LOF" or "Genetic GOF" (READ_MODEL_TYPES). Rescue models (RESCUE-Genetic,
    -Pharmaceutical, -Behavioral, -Dietary, -Microbiome, -Procedural, -Transplantation), "Pharmaceutical
    intervention", "Multifactorial", "Transgenerational" and "Genetic; Induced" describe a treated or combined
    animal, not the mutation alone, and are dropped and counted.
  - Changes: "Increased" and "Decreased" are calls with a direction; "No change" is an absence for the construct of
    its test, unless the same model has a call for that symptom on another test (as IMPC sets aside a negative where
    the line has a hit); "Not reported" means untested and is not read. "Abnormal" has no direction and is not read. The rescue
    and treatment outcomes ("Restored", "Refractory", "Ameliorated", "No adverse effect", "Side effect", "Sustained
    effect", "No sustained effect"; RESCUE_CHANGES) are dropped and counted wherever they appear.
  - Allele direction: from the model's allele type through configs/sfari_allele_classes.csv (one row per label SFARI
    uses, lowercased, each with its class and why); a "Genetic LOF" or "Genetic GOF" model type that disagrees with
    its allele class is a conflict and not read. Loss of function is keyed to the gene (seeded -1), gain of function to
    "<gene>|gain_of_function" (+1), untyped to the gene and marked untyped, as for MGI (evidence/mgi_mouse_phenotypes.py).
    Conditional, region-restricted (knockdown) and multi-gene models are not read, because the graph's perturbation is
    a whole-body change of one gene.
  - Genes: SFARI names models by the human gene symbol; the gene is read when HGNC gives it one MGI id and that MGI id
    one human gene (the one-to-one rule of IMPC).

Mapping. configs/sfari_symptom_crosswalk.csv maps (category, entity, paradigms) to a symptom with a validity class in
the IMPC crosswalk's style: which change is a call for which relation, whether a "No change" is read as an absence,
and why. A construct with no defensible mouse proxy (configs/impc_symptom_crosswalk_fine.csv names them: psychosis is
endophenotype only; suicidality, abnormal dreams and emotional lability have none) has no row that reads it. An absence
is read only where the test measures the whole mouse construct the row maps (open-field locomotion for hyperactivity),
not where one narrow test stands for a broad construct (one memory test for cognitive_impairment), which is the lesson
of decision 9.85: a narrow absence read as the absence of a whole construct made 8 of 21 contradictions there.
"""
from __future__ import annotations

import csv
import html
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from mechanistic_pathway_learning.evidence.evidence_reports import REPORT_COLUMNS
from mechanistic_pathway_learning.evidence.impc_knockout_phenotypes import VALIDITY_READ_BY_DEFAULT, VALIDITY_RUBRIC

SOURCE_NAME = "SFARI-mouse-models"
EVIDENCE_CLASS = "animal"
DEFAULT_CROSSWALK_PATH = Path("configs/sfari_symptom_crosswalk.csv")
DEFAULT_ALLELE_CLASSES_PATH = Path("configs/sfari_allele_classes.csv")
READ_MODEL_TYPES = frozenset({"genetic", "genetic lof", "genetic gof"})
MODEL_TYPE_DIRECTION = {"genetic lof": "loss_of_function", "genetic gof": "gain_of_function"}
CALL_CHANGES = frozenset({"increased", "decreased"})
ABSENCE_CHANGE = "no change"
UNTESTED_CHANGES = frozenset({"not reported", "", "na", "-"})
RESCUE_CHANGES = frozenset({"restored", "refractory", "ameliorated", "no adverse effect", "side effect", "sustained effect", "no sustained effect"})
ALLELE_CLASSES = ("loss_of_function", "gain_of_function", "untyped", "not_read")
EXTRA_COLUMNS = ("rubric_cross_species", "rubric_proxy_validity", "allele_direction", "sfari_model", "sfari_allele_type", "sfari_genotype", "sfari_paradigm")


@dataclass(frozen=True)
class SfariCrosswalkRow:
    category: str
    entity: str
    entity_match: str  # exact or prefix (the entity or any "entity: sub-entity")
    paradigms: tuple[str, ...]  # lowercased; empty means any paradigm
    increased: str  # the relation an "Increased" is a call for: induces, relieves or empty (not read)
    decreased: str
    absence_read: bool
    target_symptom: str
    validity: str
    note: str


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(text))).strip().lower()


def read_crosswalk(path: Path = DEFAULT_CROSSWALK_PATH) -> list[SfariCrosswalkRow]:
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            match = row["entity_match"].strip()
            if match not in ("exact", "prefix"):
                raise ValueError(f"{path}: entity_match {match!r} is not exact or prefix")
            for column in ("increased", "decreased"):
                if row[column].strip() not in ("induces", "relieves", ""):
                    raise ValueError(f"{path}: {column} {row[column]!r} is not induces, relieves or empty")
            rows.append(SfariCrosswalkRow(normalise(row["category"]), normalise(row["entity"]), match,
                                          tuple(normalise(paradigm) for paradigm in row["paradigms"].split(";") if paradigm.strip()),
                                          row["increased"].strip(), row["decreased"].strip(), row["absence_read"].strip() == "yes",
                                          row["target_symptom"].strip(), row["validity"].strip(), row.get("note", "")))
    return rows


def read_allele_classes(path: Path = DEFAULT_ALLELE_CLASSES_PATH) -> dict[str, str]:
    classes = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["allele_class"].strip() not in ALLELE_CLASSES:
                raise ValueError(f"{path}: allele_class {row['allele_class']!r} is not one of {ALLELE_CLASSES}")
            classes[normalise(row["sfari_allele_type"])] = row["allele_class"].strip()
    return classes


def cell_text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def parse_page(page_html: str) -> list[dict]:
    """The model blocks of one SFARI mouse-model page: each {model, model_type, genotype, allele_type, rows}, a row
    {category, entity, change, paradigm, age, pmid}."""
    models = []
    blocks = page_html.split('<div class="data-block">')[1:]
    for block in blocks:
        title = re.search(r'<span class="data-block__title">([^<]*)', block)

        def field(label: str) -> str:
            match = re.search(re.escape(label) + r':\s*<span class="data-block__value">([^<]*)', block)
            return cell_text(match.group(1)) if match else ""

        rows = []
        for row_html in re.findall(r'<tr class="table__row">(.*?)</tr>', block, flags=re.S):
            cells = [cell_text(cell) for cell in re.findall(r'<td class="table__cell">(.*?)</td>', row_html, flags=re.S)]
            if len(cells) < 6:
                continue
            pmid = re.search(r"pubmed/(\d+)", row_html)
            rows.append({"category": cells[0], "entity": cells[1], "change": cells[2], "paradigm": cells[3], "age": cells[4], "pmid": pmid.group(1) if pmid else ""})
        models.append({"model": cell_text(title.group(1)) if title else "", "model_type": field("Model Type"), "genotype": field("Model Genotype"),
                       "allele_type": field("Allele Type"), "background": field("Genetic Background"), "rows": rows})
    return models


def matching_rows(crosswalk: list[SfariCrosswalkRow], category: str, entity: str, paradigm: str) -> list[SfariCrosswalkRow]:
    category, entity, paradigm = normalise(category), normalise(entity), normalise(paradigm)
    found = []
    for row in crosswalk:
        if row.category != category:
            continue
        if row.entity_match == "exact" and entity != row.entity:
            continue
        if row.entity_match == "prefix" and not (entity == row.entity or entity.startswith(row.entity + ":")):
            continue
        if row.paradigms and paradigm not in row.paradigms:
            continue
        found.append(row)
    return found


GENOTYPES_NOT_READ = frozenset({"wildtype", "wild type", "wild-type", "chimeric", "multifactorial"})


def multi_gene_model(model: dict) -> bool:
    """A double mutant or a model of two genes, which SFARI lists on each gene's page."""
    text = normalise(model["allele_type"] + " " + model["genotype"])
    return ";" in model["allele_type"] or "double" in text or bool(re.search(r"\([a-z0-9]+\),", text))


def genotype_not_read(model: dict) -> str:
    """Why a model's genotype is not read: a wild-type, chimeric or multifactorial animal, or a floxed allele with a
    recombinase (a conditional model whose allele type does not say so); empty when it is read."""
    genotype = normalise(model["genotype"])
    if genotype in GENOTYPES_NOT_READ:
        return f"genotype {genotype}"
    if "cre" in re.split(r"[^a-z]+", genotype) or "flox" in genotype:
        return "genotype with a recombinase"
    return ""


def report_row(perturbation_id: str, node_id: str, sign: float, symptom: str, relation: str, validity: str) -> dict:
    row = {column: "" for column in REPORT_COLUMNS}
    row.update({
        "perturbation_id": perturbation_id, "perturbation_type": "gene", "perturbation_label": perturbation_id, "symptom": symptom, "relation": relation,
        "evidence_class": EVIDENCE_CLASS, "source": SOURCE_NAME, "frequency": None, "frequency_denominator": None, "placebo_flag": False, "onset": None, "sex": None,
        "pubmed_reference_count": 0, "rubric_frequency_known": 0.0, "rubric_evidence_code_pcs": 0.0, "rubric_evidence_code_tas": 0.0, "rubric_evidence_code_iea": 0.0,
        "rubric_placebo_controlled": 0.0, "rubric_curated_synopsis": 0.0, "rubric_log_sample_size": 0.0, "association_type": "", "rubric_causal_association": 0.0,
        "perturbation_nodes": json.dumps([[node_id, sign, 1.0]]), "rubric_cross_species": 1.0, "rubric_proxy_validity": VALIDITY_RUBRIC.get(validity, 0.0),
    })
    return row


def build_reports(pages: dict[str, str], human_genes_one_to_one: set[str], node_of_symbol: dict[str, str], crosswalk: list[SfariCrosswalkRow],
                  allele_classes: dict[str, str], validities: tuple[str, ...] = VALIDITY_READ_BY_DEFAULT, include_untyped: bool = True,
                  release_label: str = "") -> tuple[list[dict], dict]:
    """(report rows, counts) from {gene symbol: page HTML}. A gene outside human_genes_one_to_one (the human genes with
    a one-to-one MGI orthologue by HGNC) or without a graph node gives nothing and is counted."""
    counts: dict = defaultdict(int)
    rows: list[dict] = []
    for gene, page_html in sorted(pages.items()):
        models = parse_page(page_html)
        counts["models"] += len(models)
        if gene not in human_genes_one_to_one:
            counts["genes_without_a_one_to_one_mouse_orthologue"] += 1
            continue
        node = node_of_symbol.get(gene)
        if node is None:
            counts["genes_not_in_graph"] += 1
            continue
        for model_index, model in enumerate(models):
            model_type = normalise(model["model_type"])
            if model_type not in READ_MODEL_TYPES:
                counts[f"model_not_read:{model_type or 'no model type'}"] += 1
                counts["rows_in_models_not_read"] += len(model["rows"])
                continue
            if multi_gene_model(model):
                counts["model_not_read:more than one gene"] += 1
                counts["rows_in_models_not_read"] += len(model["rows"])
                continue
            if genotype_not_read(model):
                counts[f"model_not_read:{genotype_not_read(model)}"] += 1
                counts["rows_in_models_not_read"] += len(model["rows"])
                continue
            allele_class = allele_classes.get(normalise(model["allele_type"]))
            if allele_class is None:
                counts[f"model_not_read:allele type not in the allele classes ({normalise(model['allele_type'])})"] += 1
                counts["rows_in_models_not_read"] += len(model["rows"])
                continue
            stated = MODEL_TYPE_DIRECTION.get(model_type)
            if stated and allele_class in ("loss_of_function", "gain_of_function") and stated != allele_class:
                counts["model_not_read:model type and allele type disagree"] += 1
                continue
            direction = stated if stated and allele_class == "untyped" else allele_class
            if direction == "not_read" or (direction == "untyped" and not include_untyped):
                counts[f"model_not_read:allele class {direction}"] += 1
                counts["rows_in_models_not_read"] += len(model["rows"])
                continue
            counts["models_read"] += 1
            perturbation_id = gene if direction != "gain_of_function" else f"{gene}|gain_of_function"
            sign = 1.0 if direction == "gain_of_function" else -1.0
            model_name = model["model"] or f"{gene} model {model_index + 1}"
            called = set()  # a symptom this model has a call for, in any relation: its absences on other tests are not read
            for test in model["rows"]:
                if normalise(test["change"]) in CALL_CHANGES:
                    called.update(row.target_symptom for row in matching_rows(crosswalk, test["category"], test["entity"], test["paradigm"])
                                  if (row.increased if normalise(test["change"]) == "increased" else row.decreased))
            for test_index, test in enumerate(model["rows"]):
                change = normalise(test["change"])
                if change in RESCUE_CHANGES:
                    counts[f"row_dropped:{change}"] += 1
                    continue
                if change in UNTESTED_CHANGES:
                    counts["row_untested"] += 1
                    continue
                if change not in CALL_CHANGES and change != ABSENCE_CHANGE:
                    counts[f"row_not_read:{change}"] += 1
                    continue
                for crosswalk_row in matching_rows(crosswalk, test["category"], test["entity"], test["paradigm"]):
                    if crosswalk_row.validity not in validities:
                        continue
                    if change == ABSENCE_CHANGE:
                        if not crosswalk_row.absence_read:
                            counts["absences_not_read_for_a_narrow_test"] += 1
                            continue
                        if crosswalk_row.target_symptom in called:
                            counts["absences_blocked_by_a_call_of_the_model"] += 1
                            continue
                        relation, value = "induces", 0
                    else:
                        relation, value = (crosswalk_row.increased if change == "increased" else crosswalk_row.decreased), 1
                        if not relation:
                            continue
                    row = report_row(perturbation_id, node, sign, crosswalk_row.target_symptom, relation, crosswalk_row.validity)
                    row.update({
                        "report_id": f"{SOURCE_NAME}|{perturbation_id}|{model_name}|{test_index}|{crosswalk_row.target_symptom}|{relation if value else 'absent'}",
                        "report_value": value, "source_record_id": f"{model_name}|{test['pmid']}", "source_record_label": model_name,
                        "source_term_id": f"{test['category']}|{test['entity']}", "source_term_label": f"{test['entity']}: {test['change']} ({test['paradigm']})",
                        "evidence_code": "sfari_call" if value else "sfari_no_change", "references": f"PMID:{test['pmid']}" if test["pmid"] else f"SFARI Gene {release_label}".strip(),
                        "pubmed_reference_count": 1 if test["pmid"] else 0, "evidence_date_source": "release",
                        "model_description": (f"mouse model {model_name} ({model['allele_type']}; {model['genotype']}; {model['background']}); {test['entity']} {test['change'].lower()} "
                                              f"in the {test['paradigm']} at {test['age']}; allele {direction.replace('_', ' ')}; human gene {gene}, one to one by HGNC"),
                        "limitations": (f"cross-species: a mouse {test['entity']} read as {crosswalk_row.target_symptom} with {crosswalk_row.validity} validity ({crosswalk_row.note}); "
                                        + ("an absence on one published test, at a power the page does not state" if not value else
                                           "a published model of a gene SFARI lists for autism, so the genes were chosen for a phenotype")),
                        "allele_direction": direction, "sfari_model": model_name, "sfari_allele_type": model["allele_type"], "sfari_genotype": model["genotype"],
                        "sfari_paradigm": test["paradigm"],
                    })
                    rows.append(row)
                    counts["calls" if value else "absences"] += 1
    return rows, dict(counts)
