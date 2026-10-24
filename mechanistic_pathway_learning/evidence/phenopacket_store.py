"""Case-level phenotypes of Phenopacket Store as counts per (perturbation, symptom): k individuals observed of n assessed.

Why this source (decision 9.92). Every other monogenic source here is a disease-level annotation: HPO says a disease
has a feature, sometimes with a frequency, and says nothing about the individuals who were examined and did not have
it. Phenopacket Store (Danis et al. 2025, HGG Advances, doi 10.1016/j.xhgg.2024.100371; BSD-3-Clause) records each
published individual with a causal variant, and each phenotypic feature as observed or as `excluded: true`, of
which the GA4GH Phenopacket schema says "it is only required in cases to indicate that the phenotype was looked for,
but found to be absent" (phenopacket-schema.readthedocs.io, version 2.0.0, PhenotypicFeature, read 22 October 2026).
An exclusion is an individually assessed human genetic perturbation without the feature, which is a different kind
of statement from the absences decision 9.48 kept as soft classes (a placebo arm, a spontaneous-report count, a
mouse line).

The perturbation an individual belongs to. The causal gene of the individual's interpretation, mapped through HGNC to
the approved symbol and kept only when that symbol is a graph gene. With `allele` keying (the v5 tables, decision
9.54) the gene's perturbation is the allele its disease's mechanism names (allele_mechanisms.allele_of): a loss of
function or an untyped disease keys the gene, a gain of function keys "<gene>|gain_of_function" or the curated
neomorph, exactly as the assembler keys the HPO annotations of the same disease. With `gene` keying (the v0.4
tables) every individual keys the gene. An individual whose interpretation names variants in more than one gene, or a
structural variant with no single gene, is not a single-gene perturbation and is left out (counted).

When an exclusion counts against a construct (the crosswalk granularity finding of 21 October 2026, pull request
#12). The crosswalk takes a construct as the descendants of its root HPO terms minus the carved-out subtrees, so a
narrow NOT read as an absence of the construct would negate the whole construct on the strength of one narrow term.
An individual counts as assessed and without construct C when either
  (1) root exclusion: the individual has each root of C excluded, that is, the curator named the construct's own
      term (the crosswalk's root) as looked for and absent; or
  (2) study-complete: the construct terms observed in any individual of the same study (PubMed id) and gene form a
      non-empty set, and the individual has every one of them excluded (the term or an ancestor of it), so the study
      looked for each form of C that the genotype shows and this individual had none.
A narrow exclusion that meets neither is counted as `narrow_exclusion_not_counted` and enters nothing. Rule (2) can
add an assessed individual only to a pair that has an observed individual in that study, so it never makes a pair
without observations: a pair with exclusions only rests on rule (1) alone.

Broader exclusions are counted apart (`absent_ancestor_exclusion`) and enter n only under the exclusion rule
"root_or_ancestor_or_study_complete". Under the HPO's annotation propagation rule an excluded ancestor of every root
excludes the construct, but curators record broad exclusions from summary statements: on Phenopacket Store 0.1.27,
"Atypical behavior" excluded in 80 individuals would exclude decreased libido, increased appetite and five other
constructs at once, and "Abnormality of the genital system" (a normal genital examination) reaches decreased libido
through HPO's second parent of that term. "Sleep disturbance" excluded (359 individuals) is the one broad exclusion
that reads as a look for the construct; it is counted only under the broader rule all the same, since the rule is
written once for every construct.

A further guard (the U2AF2 and CHD8 artefacts of the research pass of 22 October 2026). An observed term that lies
under a root of C but inside a carved-out subtree (Attention deficit hyperactivity disorder under Hyperactivity, which
the crosswalk scores as a diagnosis rather than a symptom) is not an observation of C, but under the propagation rule
it implies a root of C is present. Such individuals are counted as `observed_in_carved_out_descendant`, enter neither
k nor n, and make the pair ineligible as an evidenced negative.

Age (the owner, 22 October 2026: the age distribution is fine "as long as the results aren't specifically
toddlers"). No individual is excluded by age. An exclusion counts only if the individual was old enough for the
symptom to be assessable: at least the construct's minimum age in configs/symptom_minimum_assessment_age.csv (its
sources are quoted there; the table is the owner's to confirm). The age is the age at last encounter; failing it, the
latest onset among the individual's features (a lower bound, since an onset precedes the last encounter); an HPO
onset class is read at the lower bound of its definition. An exclusion with no age, or below the minimum, is counted
under `exclusion_age_unknown` or `exclusion_below_minimum_age` and enters nothing. Observations are counted at any
age: a feature seen is seen.
"""
from __future__ import annotations

import csv
import json
import re
import zipfile
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

SOURCE_NAME = "Phenopacket-Store"
DEFAULT_PHENOPACKET_ARCHIVE = Path("data/raw/phenopacket_store/all_phenopackets.zip")
DEFAULT_MINIMUM_AGE_TABLE = Path("configs/symptom_minimum_assessment_age.csv")
DAYS_PER_YEAR = 365.25

# The lower bound of each HPO onset class, in years, as hp.obo (release 2026-09-01) defines it; an age stated only as
# one of these classes is read at its lower bound, which can only under-state the age and so never admits an exclusion
# the true age would refuse.
ONSET_CLASS_LOWER_BOUND_YEARS = {
    "HP:0030674": 0.0,  # Antenatal onset: "Onset prior to birth."
    "HP:0011460": 0.0,  # Embryonal onset
    "HP:0011461": 0.0,  # Fetal onset
    "HP:0034199": 0.0, "HP:0034198": 0.0, "HP:0034197": 0.0,  # first, second and third trimester onsets
    "HP:0003577": 0.0,  # Congenital onset: "A phenotypic abnormality that is present at birth."
    "HP:0003623": 0.0,  # Neonatal onset: "within the first 28 days of life"
    "HP:0003593": 28 / DAYS_PER_YEAR,  # Infantile onset: "between 28 days to one year of life"
    "HP:0410280": 28 / DAYS_PER_YEAR,  # Pediatric onset: "before the age of 16 years, but excluding neonatal or congenital onset"
    "HP:0011463": 1.0,  # Childhood onset: "between 1 and 5 years"
    "HP:0003621": 5.0,  # Juvenile onset: "between the age of 5 and 15 years"
    "HP:0003581": 16.0,  # Adult onset: "at the age of 16 years or later"
    "HP:0011462": 16.0,  # Young adult onset: "between 16 and 40 years"
    "HP:0025708": 16.0, "HP:0025709": 19.0, "HP:0025710": 25.0,  # early, intermediate and late young adult onset
    "HP:0003596": 40.0,  # Middle age onset: "at the age of 40 to 60 years"
    "HP:0003584": 60.0,  # Late onset: "after the age of 60 years"
}

# Status of one (individual, construct); the counts per pair are built from these.
OBSERVED = "observed"
ABSENT_ROOT_EXCLUSION = "absent_root_exclusion"
ABSENT_STUDY_COMPLETE = "absent_study_complete"
ABSENT_ANCESTOR_EXCLUSION = "absent_ancestor_exclusion"
NARROW_EXCLUSION_NOT_COUNTED = "narrow_exclusion_not_counted"
OBSERVED_IN_CARVED_OUT_DESCENDANT = "observed_in_carved_out_descendant"
EXCLUSION_BELOW_MINIMUM_AGE = "exclusion_below_minimum_age"
EXCLUSION_AGE_UNKNOWN = "exclusion_age_unknown"
STATUSES = (OBSERVED, ABSENT_ROOT_EXCLUSION, ABSENT_STUDY_COMPLETE, ABSENT_ANCESTOR_EXCLUSION, NARROW_EXCLUSION_NOT_COUNTED,
            OBSERVED_IN_CARVED_OUT_DESCENDANT, EXCLUSION_BELOW_MINIMUM_AGE, EXCLUSION_AGE_UNKNOWN)
# which absent statuses enter n under each exclusion rule; the default is rules (1) and (2) of the module docstring
EXCLUSION_RULES = {
    "root": (ABSENT_ROOT_EXCLUSION,),
    "root_or_study_complete": (ABSENT_ROOT_EXCLUSION, ABSENT_STUDY_COMPLETE),
    "root_or_ancestor_or_study_complete": (ABSENT_ROOT_EXCLUSION, ABSENT_STUDY_COMPLETE, ABSENT_ANCESTOR_EXCLUSION),
}
DEFAULT_EXCLUSION_RULE = "root_or_study_complete"
ASSESSED_ABSENT = EXCLUSION_RULES[DEFAULT_EXCLUSION_RULE]

# The per-pair columns the label selection and the loader read (decision 9.92), with obvious names for the
# positive-unlabelled likelihood to read as a propensity or a power.
INDIVIDUALS_OBSERVED_COLUMN = "phenopacket_individuals_observed"
INDIVIDUALS_ASSESSED_COLUMN = "phenopacket_individuals_assessed"


def parse_iso8601_duration_years(text: str | None) -> float | None:
    """Years in an ISO 8601 duration of the forms Phenopacket Store uses (P3Y2M, P10Y, P2M14D, P6W, P0D)."""
    if not text:
        return None
    match = re.fullmatch(r"P(?:(\d+(?:\.\d+)?)Y)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)W)?(?:(\d+(?:\.\d+)?)D)?(?:T.*)?", text.strip())
    if not match or not any(match.groups()):
        return None
    years, months, weeks, days = (float(part) if part else 0.0 for part in match.groups())
    return years + months / 12.0 + (weeks * 7.0 + days) / DAYS_PER_YEAR


def years_of_time_element(element: Mapping | None) -> float | None:
    """A phenopacket TimeElement as years of age: an ISO 8601 age, a gestational age (before birth, so 0) or an HPO
    onset class at its lower bound; None for anything else (a timestamp, an interval, an unknown class)."""
    if not element:
        return None
    if "age" in element:
        return parse_iso8601_duration_years((element.get("age") or {}).get("iso8601duration"))
    if "gestationalAge" in element:
        return 0.0
    if "ontologyClass" in element:
        return ONSET_CLASS_LOWER_BOUND_YEARS.get((element.get("ontologyClass") or {}).get("id"))
    if "ageRange" in element:
        return parse_iso8601_duration_years(((element.get("ageRange") or {}).get("start") or {}).get("iso8601duration"))
    return None


@dataclass
class Individual:
    phenopacket_id: str
    study: str  # the PubMed id of the publication the individual was curated from ("" when none is stated)
    cohort: str  # the store's folder (one per gene, or a named cohort)
    genes: tuple[tuple[str, str], ...]  # (HGNC id, symbol as the phenopacket gives it) of each causal or contributory variant's gene
    structural_variant_without_gene: bool
    disease_id: str
    age_years: float | None
    age_basis: str  # "last encounter", "latest feature onset" or ""
    observed_terms: frozenset[str]
    excluded_terms: frozenset[str]


def study_of(phenopacket: Mapping) -> str:
    for reference in (phenopacket.get("metaData") or {}).get("externalReferences") or []:
        identifier = str(reference.get("id", ""))
        if identifier.startswith("PMID:"):
            return identifier
    match = re.match(r"PMID_(\d+)", str(phenopacket.get("id", "")))
    return f"PMID:{match.group(1)}" if match else ""


def individual_of(phenopacket: Mapping, cohort: str) -> Individual:
    observed, excluded = set(), set()
    latest_onset = None
    for feature in phenopacket.get("phenotypicFeatures") or []:
        term = (feature.get("type") or {}).get("id")
        if not term:
            continue
        (excluded if feature.get("excluded") else observed).add(term)
        onset = years_of_time_element(feature.get("onset"))
        if onset is not None and not feature.get("excluded"):
            latest_onset = onset if latest_onset is None else max(latest_onset, onset)
    subject = phenopacket.get("subject") or {}
    age, basis = years_of_time_element(subject.get("timeAtLastEncounter")), "last encounter"
    if age is None and latest_onset is not None:
        age, basis = latest_onset, "latest feature onset"
    elif age is None:
        basis = ""
    genes, structural_without_gene, disease = [], False, ""
    for interpretation in phenopacket.get("interpretations") or []:
        diagnosis = interpretation.get("diagnosis") or {}
        disease = disease or (diagnosis.get("disease") or {}).get("id", "")
        for genomic in diagnosis.get("genomicInterpretations") or []:
            if genomic.get("interpretationStatus") not in (None, "CAUSATIVE", "CONTRIBUTORY"):  # not REJECTED, CANDIDATE or UNKNOWN_STATUS
                continue
            descriptor = (genomic.get("variantInterpretation") or {}).get("variationDescriptor") or {}
            context = descriptor.get("geneContext") or genomic.get("gene")
            if context:
                genes.append((str(context.get("valueId", "")), str(context.get("symbol", ""))))
            else:
                structural_without_gene = True
    if not disease:
        disease = next(((entry.get("term") or {}).get("id", "") for entry in phenopacket.get("diseases") or [] if not entry.get("excluded")), "")
    return Individual(str(phenopacket.get("id", "")), study_of(phenopacket), cohort, tuple(dict.fromkeys(genes)), structural_without_gene, disease,
                      age, basis, frozenset(observed), frozenset(excluded))


def read_phenopackets(archive_path: Path) -> Iterator[Individual]:
    """Every phenopacket of a release archive (all_phenopackets.zip), read in place without extracting it."""
    with zipfile.ZipFile(archive_path) as archive:
        for name in sorted(archive.namelist()):
            if not name.endswith(".json"):
                continue
            parts = name.split("/")
            cohort = parts[-2] if len(parts) >= 2 else ""
            phenopacket = json.loads(archive.read(name))
            if "phenotypicFeatures" not in phenopacket and "subject" not in phenopacket:
                continue
            yield individual_of(phenopacket, cohort)


def load_hpo_term_replacements(obo_path: Path) -> dict[str, str]:
    """Alternative and obsolete HPO ids -> the current id: alt_id lines, and replaced_by on an obsolete term. A
    phenopacket curated against an older release may use either."""
    replacements: dict[str, str] = {}
    current, obsolete, replaced_by, alternatives = None, False, None, []

    def close() -> None:
        if current is None:
            return
        for alternative in alternatives:
            replacements[alternative] = current
        if obsolete and replaced_by:
            replacements[current] = replaced_by

    with open(obo_path, encoding="utf-8") as obo_file:
        for raw_line in obo_file:
            line = raw_line.strip()
            if line.startswith("["):
                close()
                current, obsolete, replaced_by, alternatives = None, False, None, []
            elif line.startswith("id: HP:"):
                current = line[len("id: "):]
            elif line.startswith("alt_id: HP:"):
                alternatives.append(line[len("alt_id: "):])
            elif line == "is_obsolete: true":
                obsolete = True
            elif line.startswith("replaced_by: HP:"):
                replaced_by = line[len("replaced_by: "):]
    close()
    return replacements


def ancestors_with_self(term: str, parents_by_term: Mapping[str, set[str]], cache: dict[str, frozenset[str]]) -> frozenset[str]:
    if term in cache:
        return cache[term]
    collected, frontier = {term}, [term]
    while frontier:
        current = frontier.pop()
        for parent in parents_by_term.get(current, ()):
            if parent not in collected:
                collected.add(parent)
                frontier.append(parent)
    cache[term] = frozenset(collected)
    return cache[term]


@dataclass(frozen=True)
class Construct:
    symptom: str
    roots: frozenset[str]
    terms: frozenset[str]  # the crosswalked terms: descendants of the roots minus the carved-out subtrees
    carved_out: frozenset[str]  # descendants of a root inside a carved-out subtree


def read_constructs(crosswalk_path: Path, parents_by_term: Mapping[str, set[str]]) -> list[Construct]:
    """One Construct per crosswalk row with HPO roots (coarse or fine crosswalk alike)."""
    from mechanistic_pathway_learning.evidence.load_monogenic_phenotype_annotations import descendants_of, read_crosswalk_hpo_terms

    constructs = []
    for symptom, (roots, carved) in read_crosswalk_hpo_terms(crosswalk_path).items():
        if not roots:
            continue
        under_roots = set().union(*(descendants_of(root, parents_by_term) for root in roots))
        carved_terms = set().union(*(descendants_of(term, parents_by_term) for term in carved)) if carved else set()
        constructs.append(Construct(symptom, frozenset(roots), frozenset(under_roots - carved_terms), frozenset(under_roots & carved_terms)))
    return constructs


def read_minimum_ages(path: Path = DEFAULT_MINIMUM_AGE_TABLE) -> dict[str, float]:
    with open(path, encoding="utf-8") as table:
        return {row["target_symptom"]: float(row["minimum_age_years"]) for row in csv.DictReader(table)}


@dataclass
class GeneResolver:
    """Phenopacket gene -> the approved HGNC symbol when it is a graph gene, else None."""
    symbol_of_hgnc_id: Mapping[str, str]
    symbol_of_previous_symbol: Mapping[str, str]
    graph_symbols: frozenset[str]

    def resolve(self, hgnc_id: str, symbol: str) -> str | None:
        approved = self.symbol_of_hgnc_id.get(hgnc_id) or (symbol if symbol in self.graph_symbols else self.symbol_of_previous_symbol.get(symbol, symbol))
        return approved if approved in self.graph_symbols else None


def gene_resolver(hgnc_path: Path, graph_symbols: Iterable[str]) -> GeneResolver:
    hgnc = pd.read_csv(hgnc_path, sep="\t", usecols=["hgnc_id", "symbol", "prev_symbol", "status"], dtype=str).fillna("")
    hgnc = hgnc[hgnc.status == "Approved"]
    previous: dict[str, str] = {}
    counts: dict[str, int] = defaultdict(int)
    for row in hgnc.itertuples(index=False):
        for old in filter(None, (part.strip() for part in row.prev_symbol.split("|"))):
            previous[old] = row.symbol
            counts[old] += 1
    previous = {old: new for old, new in previous.items() if counts[old] == 1}  # an ambiguous previous symbol maps to nothing
    return GeneResolver(dict(zip(hgnc.hgnc_id, hgnc.symbol)), previous, frozenset(graph_symbols))


def individual_statuses(individual: Individual, constructs: Iterable[Construct], parents_by_term: Mapping[str, set[str]],
                        minimum_age_years: Mapping[str, float], study_observed_terms: Mapping[str, frozenset[str]],
                        ancestor_cache: dict[str, frozenset[str]]) -> dict[str, str]:
    """Construct symptom -> status for the constructs this individual says anything about (STATUSES)."""
    statuses: dict[str, str] = {}
    for construct in constructs:
        if any(term in construct.terms for term in individual.observed_terms):
            statuses[construct.symptom] = OBSERVED
            continue
        if any(term in construct.carved_out for term in individual.observed_terms):
            statuses[construct.symptom] = OBSERVED_IN_CARVED_OUT_DESCENDANT
            continue
        # an excluded term speaks about the construct when it lies in it or above one of its roots
        relevant = [term for term in individual.excluded_terms
                    if term in construct.terms or any(term in ancestors_with_self(root, parents_by_term, ancestor_cache) for root in construct.roots)]
        if not relevant:
            continue
        excluded_set = set(individual.excluded_terms)
        root_exclusion = construct.roots <= excluded_set
        ancestor_exclusion = all(ancestors_with_self(root, parents_by_term, ancestor_cache) & excluded_set for root in construct.roots)
        seen_in_study = study_observed_terms.get(construct.symptom, frozenset())
        study_complete = bool(seen_in_study) and all(ancestors_with_self(term, parents_by_term, ancestor_cache) & excluded_set for term in seen_in_study)
        if not (root_exclusion or ancestor_exclusion or study_complete):
            statuses[construct.symptom] = NARROW_EXCLUSION_NOT_COUNTED
            continue
        minimum = minimum_age_years.get(construct.symptom)
        if minimum is None:
            raise KeyError(f"{construct.symptom} has no row in the minimum-age table")
        if individual.age_years is None:
            statuses[construct.symptom] = EXCLUSION_AGE_UNKNOWN
        elif individual.age_years < minimum:
            statuses[construct.symptom] = EXCLUSION_BELOW_MINIMUM_AGE
        else:  # the narrowest rule that admits it, so each broader rule admits everything the narrower ones do
            statuses[construct.symptom] = ABSENT_ROOT_EXCLUSION if root_exclusion else (ABSENT_STUDY_COMPLETE if study_complete else ABSENT_ANCESTOR_EXCLUSION)
    return statuses


@dataclass
class AlleleKeys:
    """(gene, disease) -> (perturbation id, allele class, basis), from allele_mechanisms; empty means gene keying."""
    keys: Mapping[tuple[str, str], tuple[str, str, str]] = field(default_factory=dict)

    def key(self, gene: str, disease: str) -> tuple[str, str, str]:
        return self.keys.get((gene, disease), (gene, "untyped", "untyped"))


def allele_keys(pairs: Iterable[tuple[str, str]], orphadata_product6: Path, orphadata_product1: Path, gene2phenotype: Path | None,
                adjudications: Path | None, neomorphic_alleles: Path | None) -> AlleleKeys:
    """The allele each (gene, disease) of the phenopackets belongs to, by the assembler's own rule (decision 9.54)."""
    from mechanistic_pathway_learning.evidence.allele_mechanisms import (
        allele_of, apply_adjudications, disease_mechanisms, first_source_unless_absent, gene2phenotype_mechanisms,
        load_gene2phenotype, load_orphanet_omim_mappings, read_mechanism_adjudications, read_neomorphic_alleles)
    from mechanistic_pathway_learning.evidence.gene_disease_association_types import load_orphanet_association_types

    pairs = set(pairs)
    mappings = load_orphanet_omim_mappings(orphadata_product1)
    mechanisms = disease_mechanisms(load_orphanet_association_types(orphadata_product6), mappings, pairs)
    if gene2phenotype is not None:
        records, _ = load_gene2phenotype(gene2phenotype)
        mechanisms = first_source_unless_absent(mechanisms, gene2phenotype_mechanisms(records, mappings, pairs), pairs)
    if adjudications is not None:
        mechanisms = apply_adjudications(mechanisms, read_mechanism_adjudications(adjudications))
    neomorphs = read_neomorphic_alleles(neomorphic_alleles) if neomorphic_alleles is not None else {}
    keys = {}
    for gene, disease in pairs:
        mechanism = mechanisms[(gene, disease)]
        allele = allele_of(gene, mechanism, neomorphs)
        keys[(gene, disease)] = (allele.perturbation_id, allele.allele_class, mechanism.basis)
    return AlleleKeys(keys)


INDIVIDUAL_STATUS_COLUMNS = ("phenopacket_id", "study", "cohort", "gene", "disease_id", "allele_perturbation_id", "allele_class", "allele_mechanism_basis",
                             "age_years", "age_basis", "symptom", "status")


def individual_status_table(individuals: Iterable[Individual], constructs: list[Construct], parents_by_term: Mapping[str, set[str]],
                            minimum_age_years: Mapping[str, float], resolver: GeneResolver, replacements: Mapping[str, str],
                            keys: AlleleKeys | None = None) -> tuple[pd.DataFrame, dict]:
    """One row per (individual, construct) the individual says anything about, and counts of who was left out and why.

    Two passes: the first resolves genes and terms and collects, per (study, gene, construct), the construct terms
    observed in the study (rule 2 of the module docstring); the second gives each individual its status."""
    counts = {"phenopackets": 0, "left_out_no_gene": 0, "left_out_several_genes": 0, "left_out_structural_variant_without_gene": 0,
              "left_out_gene_not_in_graph": 0, "individuals_on_graph_genes": 0}
    kept: list[tuple[Individual, str]] = []
    for individual in individuals:
        counts["phenopackets"] += 1
        if individual.structural_variant_without_gene and not individual.genes:
            counts["left_out_structural_variant_without_gene"] += 1
            continue
        if not individual.genes:
            counts["left_out_no_gene"] += 1
            continue
        resolved = {resolver.resolve(hgnc_id, symbol) or f"?{symbol}" for hgnc_id, symbol in individual.genes}
        if len(resolved) > 1:
            counts["left_out_several_genes"] += 1
            continue
        gene = resolved.pop()
        if gene.startswith("?"):
            counts["left_out_gene_not_in_graph"] += 1
            continue
        individual.observed_terms = frozenset(replacements.get(term, term) for term in individual.observed_terms)
        individual.excluded_terms = frozenset(replacements.get(term, term) for term in individual.excluded_terms)
        kept.append((individual, gene))
    counts["individuals_on_graph_genes"] = len(kept)
    study_observed: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for individual, gene in kept:
        for construct in constructs:
            seen = individual.observed_terms & construct.terms
            if seen:
                study_observed[(individual.study or individual.cohort, gene)][construct.symptom] |= seen
    ancestor_cache: dict[str, frozenset[str]] = {}
    rows = []
    keys = keys or AlleleKeys()
    for individual, gene in kept:
        study_terms = {symptom: frozenset(terms) for symptom, terms in study_observed.get((individual.study or individual.cohort, gene), {}).items()}
        statuses = individual_statuses(individual, constructs, parents_by_term, minimum_age_years, study_terms, ancestor_cache)
        allele_id, allele_class, basis = keys.key(gene, individual.disease_id)
        for symptom, status in statuses.items():
            rows.append((individual.phenopacket_id, individual.study, individual.cohort, gene, individual.disease_id, allele_id, allele_class, basis,
                         individual.age_years, individual.age_basis, symptom, status))
    return pd.DataFrame(rows, columns=list(INDIVIDUAL_STATUS_COLUMNS)), counts


PAIR_COUNT_COLUMNS = ("perturbation_id", "gene", "symptom", INDIVIDUALS_OBSERVED_COLUMN, INDIVIDUALS_ASSESSED_COLUMN, "individuals_absent_root_exclusion",
                      "individuals_absent_study_complete", "individuals_absent_ancestor_exclusion", "individuals_narrow_exclusion_not_counted",
                      "individuals_observed_in_carved_out_descendant", "individuals_exclusion_below_minimum_age", "individuals_exclusion_age_unknown",
                      "studies", "exclusion_rule")


def pair_counts(statuses: pd.DataFrame, key: str = "allele", exclusion_rule: str = DEFAULT_EXCLUSION_RULE) -> pd.DataFrame:
    """Per (perturbation, symptom): k observed and n assessed (k plus those assessed and absent under exclusion_rule),
    with every status counted beside them. key "allele" uses allele_perturbation_id (v5), "gene" the gene (v0.4)."""
    if key not in ("allele", "gene"):
        raise ValueError(f"key must be allele or gene, not {key!r}")
    if exclusion_rule not in EXCLUSION_RULES:
        raise ValueError(f"exclusion_rule must be one of {sorted(EXCLUSION_RULES)}")
    counted = EXCLUSION_RULES[exclusion_rule]
    column = "allele_perturbation_id" if key == "allele" else "gene"
    rows = []
    for (perturbation_id, symptom), group in statuses.groupby([column, "symptom"], sort=True):
        by_status = group.status.value_counts().to_dict()
        observed = int(by_status.get(OBSERVED, 0))
        absent = sum(int(by_status.get(status, 0)) for status in counted)
        rows.append((perturbation_id, group.gene.iloc[0], symptom, observed, observed + absent, int(by_status.get(ABSENT_ROOT_EXCLUSION, 0)),
                     int(by_status.get(ABSENT_STUDY_COMPLETE, 0)), int(by_status.get(ABSENT_ANCESTOR_EXCLUSION, 0)),
                     int(by_status.get(NARROW_EXCLUSION_NOT_COUNTED, 0)), int(by_status.get(OBSERVED_IN_CARVED_OUT_DESCENDANT, 0)),
                     int(by_status.get(EXCLUSION_BELOW_MINIMUM_AGE, 0)), int(by_status.get(EXCLUSION_AGE_UNKNOWN, 0)),
                     ";".join(sorted(set(group.study.astype(str)) - {""})), exclusion_rule))
    return pd.DataFrame(rows, columns=list(PAIR_COUNT_COLUMNS))


def clean_negative_pairs(counts: pd.DataFrame, positive_pairs: set[tuple[str, str]]) -> pd.DataFrame:
    """Use (a): pairs with assessed individuals, none observed, none observed in a carved-out descendant, and no
    current positive. Returns the rows of counts that qualify."""
    eligible = ((counts[INDIVIDUALS_OBSERVED_COLUMN] == 0) & (counts[INDIVIDUALS_ASSESSED_COLUMN] > 0)
                & (counts.individuals_observed_in_carved_out_descendant == 0))
    without_positive = [(perturbation_id, symptom) not in positive_pairs for perturbation_id, symptom in zip(counts.perturbation_id, counts.symptom)]
    return counts[eligible & pd.Series(without_positive, index=counts.index)]
