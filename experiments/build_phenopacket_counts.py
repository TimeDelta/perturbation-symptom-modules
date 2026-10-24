"""Count, per (perturbation, symptom), the Phenopacket Store individuals observed with the symptom (k) and assessed for
it (n), by the rules of mechanistic_pathway_learning/evidence/phenopacket_store.py (decision 9.92).

Inputs: the pinned release archive (data/raw/phenopacket_store/all_phenopackets.zip, release 0.1.27; scripts/
fetch_raw_sources.sh), hp.obo for the is_a closure and the replaced terms, HGNC for the approved symbols, the graph's
gene nodes, a symptom crosswalk (coarse for the v0.4 tables, fine for v5) and configs/symptom_minimum_assessment_age.csv.
With --key allele (the v5 tables) the gene's perturbation is the allele its disease's mechanism names, read from
Orphadata products 6 and 1, Gene2Phenotype, configs/allele_mechanism_adjudications.csv and configs/neomorphic_alleles.csv,
as the assembler's --allele-perturbations does; with --key gene (v0.4) every individual keys the gene.

Outputs (--output-dir):
  phenopacket_individual_status.parquet  one row per (individual, construct) the individual says anything about
  phenopacket_pair_counts.parquet        one row per (perturbation, symptom): k, n and every status counted
  phenopacket_summary.json               who was left out and why, statements by symptom, the pins

Usage:
  python experiments/build_phenopacket_counts.py --key gene --crosswalk docs/symptom_crosswalk.csv \
      --graph-dir data/releases/v0.4/graph_full --output-dir data/processed/phenopacket_store_v04
  python experiments/build_phenopacket_counts.py --key allele --crosswalk docs/symptom_crosswalk_fine.csv \
      --graph-dir data/processed/graph_full --output-dir data/processed/phenopacket_store_v5
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.evidence.load_monogenic_phenotype_annotations import load_hpo_is_a_parents_from_obo
from mechanistic_pathway_learning.evidence.phenopacket_store import (
    DEFAULT_EXCLUSION_RULE,
    DEFAULT_MINIMUM_AGE_TABLE,
    DEFAULT_PHENOPACKET_ARCHIVE,
    EXCLUSION_RULES,
    INDIVIDUALS_ASSESSED_COLUMN,
    INDIVIDUALS_OBSERVED_COLUMN,
    OBSERVED,
    STATUSES,
    allele_keys,
    gene_resolver,
    individual_status_table,
    load_hpo_term_replacements,
    pair_counts,
    read_constructs,
    read_minimum_ages,
    read_phenopackets,
)

RELEASE = "0.1.27"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--archive", type=Path, default=DEFAULT_PHENOPACKET_ARCHIVE)
    parser.add_argument("--hpo-obo", type=Path, default=Path("data/raw/hpo/hp.obo"))
    parser.add_argument("--hgnc", type=Path, default=Path("data/raw/hgnc/hgnc_complete_set.txt"))
    parser.add_argument("--graph-dir", type=Path, required=True, help="the graph whose gene nodes the perturbations must be")
    parser.add_argument("--crosswalk", type=Path, default=Path("docs/symptom_crosswalk_fine.csv"))
    parser.add_argument("--minimum-ages", type=Path, default=DEFAULT_MINIMUM_AGE_TABLE)
    parser.add_argument("--key", choices=("allele", "gene"), default="allele", help="allele for the v5 tables (decision 9.54), gene for v0.4")
    parser.add_argument("--exclusion-rule", choices=sorted(EXCLUSION_RULES), default=DEFAULT_EXCLUSION_RULE)
    parser.add_argument("--orphadata-product6", type=Path, default=Path("data/raw/orphadata/en_product6.xml"))
    parser.add_argument("--orphadata-product1", type=Path, default=Path("data/raw/orphadata/en_product1.xml"))
    parser.add_argument("--gene2phenotype", type=Path, default=Path("data/raw/gene2phenotype/G2P_all_panels.csv"))
    parser.add_argument("--mechanism-adjudications", type=Path, default=Path("configs/allele_mechanism_adjudications.csv"))
    parser.add_argument("--neomorphic-alleles", type=Path, default=Path("configs/neomorphic_alleles.csv"))
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args()

    parents = load_hpo_is_a_parents_from_obo(arguments.hpo_obo)
    constructs = read_constructs(arguments.crosswalk, parents)
    minimum_ages = read_minimum_ages(arguments.minimum_ages)
    nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet", columns=["node_type", "gene_symbol"])
    graph_symbols = set(nodes[nodes.node_type == "gene"].gene_symbol.dropna().astype(str))
    resolver = gene_resolver(arguments.hgnc, graph_symbols)
    individuals = list(read_phenopackets(arguments.archive))
    keys = None
    if arguments.key == "allele":
        pairs = set()
        for individual in individuals:
            for hgnc_id, symbol in individual.genes:
                gene = resolver.resolve(hgnc_id, symbol)
                if gene:
                    pairs.add((gene, individual.disease_id))
        keys = allele_keys(pairs, arguments.orphadata_product6, arguments.orphadata_product1,
                           arguments.gene2phenotype if arguments.gene2phenotype.exists() else None,
                           arguments.mechanism_adjudications, arguments.neomorphic_alleles)
    statuses, counts = individual_status_table(individuals, constructs, parents, minimum_ages, resolver, load_hpo_term_replacements(arguments.hpo_obo), keys)
    pairs_table = pair_counts(statuses, arguments.key, arguments.exclusion_rule)
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    statuses.to_parquet(arguments.output_dir / "phenopacket_individual_status.parquet", index=False)
    pairs_table.to_parquet(arguments.output_dir / "phenopacket_pair_counts.parquet", index=False)
    absent = statuses[statuses.status.isin(EXCLUSION_RULES[arguments.exclusion_rule])]
    summary = {
        "source": "Phenopacket Store", "release": RELEASE, "archive": str(arguments.archive), "archive_sha256": sha256_of(arguments.archive),
        "hpo_obo_sha256": sha256_of(arguments.hpo_obo), "crosswalk": str(arguments.crosswalk), "minimum_ages": str(arguments.minimum_ages),
        "minimum_ages_sha256": sha256_of(arguments.minimum_ages), "key": arguments.key, "exclusion_rule": arguments.exclusion_rule,
        "graph_dir": str(arguments.graph_dir), **counts,
        "individuals_with_a_statement_on_the_symptom_set": int(statuses.phenopacket_id.nunique()),
        "genes_with_a_statement": int(statuses.gene.nunique()),
        "statements_by_status": {status: int((statuses.status == status).sum()) for status in STATUSES},
        "observed_statements_by_symptom": statuses[statuses.status == OBSERVED].groupby("symptom").size().to_dict(),
        "assessed_absent_statements_by_symptom": absent.groupby("symptom").size().to_dict(),
        "individuals_with_an_age": int(statuses.drop_duplicates("phenopacket_id").age_years.notna().sum()),
        "pairs": len(pairs_table), "pairs_with_an_assessed_individual": int((pairs_table[INDIVIDUALS_ASSESSED_COLUMN] > 0).sum()),
        "pairs_with_observed_and_assessed_absent": int(((pairs_table[INDIVIDUALS_OBSERVED_COLUMN] > 0)
                                                        & (pairs_table[INDIVIDUALS_ASSESSED_COLUMN] > pairs_table[INDIVIDUALS_OBSERVED_COLUMN])).sum()),
        "pairs_with_assessed_absent_only": int(((pairs_table[INDIVIDUALS_OBSERVED_COLUMN] == 0) & (pairs_table[INDIVIDUALS_ASSESSED_COLUMN] > 0)).sum()),
        "pairs_with_assessed_absent_only_and_a_carved_out_observation": int(((pairs_table[INDIVIDUALS_OBSERVED_COLUMN] == 0) & (pairs_table[INDIVIDUALS_ASSESSED_COLUMN] > 0)
                                                                            & (pairs_table.individuals_observed_in_carved_out_descendant > 0)).sum()),
    }
    if arguments.key == "allele":
        summary["allele_classes_of_individuals"] = statuses.drop_duplicates("phenopacket_id").allele_class.value_counts().to_dict()
    (arguments.output_dir / "phenopacket_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
