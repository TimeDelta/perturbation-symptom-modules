"""Split the carrier `product_of` edges (the encoder's `coproduct_of`) into regeneration and de novo synthesis.

Why the split matters. `mechanistic_pathway_learning/graph/cofactor_edges.py` marks an edge as a carrier edge when
the metabolite's name is on the carrier list, which keys on the metabolite's identity and not on what the reaction
does to the moiety's total. Two physically opposite processes therefore share one relation and so one learned gain:

  regeneration  the reaction also CONSUMES a metabolite of the same moiety family, so it redistributes material
                within a conserved total and the total does not move (buffered; the behaviour the low carrier gain
                exists to produce, so that a PAH loss leaving tetrahydrobiopterin unconsumed does not raise dopamine)
  de novo       it does not, so the moiety's total increases (drainable; the behaviour a synthesis defect needs, so
                that a GCH1 loss lowers tetrahydrobiopterin)

The test used here is the one that decides whether the edge moves the total, and it is this script's definition
rather than the repository's: a family is a set of names from the carrier list that are interconvertible forms of one
moiety (FAMILIES below), and an edge is regeneration when its reaction consumes any metabolite of its product's
family. Transport counts as regeneration, which is right (a transport reaction moves one form between compartments);
exchange and demand reactions also count as regeneration, which is an artefact of them being boundary pseudo-
reactions rather than physiology, and the printed table names the subsystem so they can be told apart. Edges marked
only by the recurring-substrate-product-pair clause have no family here and are counted apart; a recurring pair is a
redistribution by construction, so they belong with regeneration.

Usage (from the checkout's root):

    PYTHONPATH=. python experiments/measure_coproduct_de_novo_split.py [--graph data/releases/v0.4/graph]

Prints the counts, the split by family, and every carrier edge into a chosen family (--family, default biopterin).
Reads a graph directory holding nodes.parquet, edges.parquet and relation_types.json; changes nothing.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.graph.cofactor_edges import cofactor_edge_mask

# Interconvertible forms of one moiety, from DEFAULT_CARRIER_METABOLITE_NAMES. Plain THF is absent from the carrier
# list although every substituted folate and dihydrofolate is on it, so the folate moiety is split across carrier and
# main treatment at THF; it is left out here too, so that this script reports the list as it stands.
FAMILIES: dict[str, tuple[str, ...]] = {
    "biopterin": ("tetrahydrobiopterin", "dihydrobiopterin", "quinonoid dihydrobiopterin",
                  "4alpha-hydroxytetrahydrobiopterin", "o2-4a-cyclic-tetrahydrobiopterin"),
    "quinone": ("ubiquinone", "ubiquinol"),
    "cytochrome": ("ferricytochrome c", "ferrocytochrome c", "ferricytochrome b5", "ferrocytochrome b5"),
    "thioredoxin": ("thioredoxin", "oxidized thioredoxin", "mitothioredoxin", "mitooxidized thioredoxin"),
    "ferredoxin": ("oxidized ferredoxin", "reduced ferredoxin", "oxidized adrenal ferredoxin",
                   "reduced adrenal ferredoxin"),
    "ascorbate": ("ascorbate", "monodehydroascorbate", "dehydroascorbic acid"),
    "lipoamide": ("lipoamide", "dihydrolipoamide"),
    "acyl carrier": ("[acp]", "acyl carrier protein"),
    "vitamin B6": ("pyridoxal-phosphate", "pyridoxamine-phosphate"),
    "folate": ("5,10-methylene-thf", "5-methyl-thf", "10-formyl-thf", "5,10-methenyl-thf", "5-formyl-thf",
               "5-formiminotetrahydrofolate", "dihydrofolate"),
}
PAIR_CLAUSE = "pair clause (no named family)"


def load_graph(directory: Path):
    nodes = pd.read_parquet(directory / "nodes.parquet")
    edges = pd.read_parquet(directory / "edges.parquet")
    relation_types = json.loads((directory / "relation_types.json").read_text())
    position = {node_id: index for index, node_id in enumerate(nodes.node_id)}
    source = edges.source_id.map(position).to_numpy()
    target = edges.target_id.map(position).to_numpy()
    relation = edges.relation_type.map(relation_types.index).to_numpy()
    return nodes, relation_types, source, target, relation


def classify(nodes, relation_types, source, target, relation, carrier_rule: str = "all") -> pd.DataFrame:
    """One row per carrier product_of edge, with the family of its product and whether it is de novo."""
    mask = cofactor_edge_mask(source, target, relation, relation_types, nodes.base_metabolite_id.to_numpy(),
                              nodes.display_name.to_numpy(), nodes.is_currency.to_numpy(), carrier_rule=carrier_rule)
    family_of_name = {name: family for family, names in FAMILIES.items() for name in names}
    lowered = np.array([str(name).lower() for name in nodes.display_name])
    family = np.array([family_of_name.get(name, "") for name in lowered], dtype=object)

    substrate_relation = relation_types.index("substrate_of")
    product_relation = relation_types.index("product_of")
    # every family a reaction consumes, whether or not that edge was marked a carrier edge: the moiety's total is
    # what decides, so a consumed form counts even where the rule treated it as a main substrate
    consumed: dict[int, set] = defaultdict(set)
    for edge in np.where(relation == substrate_relation)[0]:
        if family[source[edge]]:
            consumed[int(target[edge])].add(family[source[edge]])

    rows = []
    for edge in np.where(mask & (relation == product_relation))[0]:
        reaction, metabolite = int(source[edge]), int(target[edge])
        this_family = family[metabolite]
        kind = (PAIR_CLAUSE if not this_family
                else "regeneration" if this_family in consumed.get(reaction, set()) else "de novo")
        rows.append({"kind": kind, "family": this_family or "-", "reaction": nodes.node_id.iloc[reaction],
                     "metabolite": nodes.display_name.iloc[metabolite],
                     "gene_reaction_rule": nodes.gene_reaction_rule.iloc[reaction],
                     "subsystem": nodes.subsystem.iloc[reaction]})
    return pd.DataFrame(rows)


def gene_symbols(rule, symbol_of: dict[str, str]) -> str:
    """The gene_reaction_rule's Ensembl identifiers as symbols; the rules carry identifiers, not symbols."""
    if not isinstance(rule, str):
        return ""
    return " ".join(sorted({symbol_of.get(found, found) for found in re.findall(r"ENSG\d+", rule)}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph", type=Path, default=Path("data/releases/v0.4/graph"))
    parser.add_argument("--carrier-rule", default="all")
    parser.add_argument("--family", default="biopterin", help="the family whose edges are listed one by one")
    arguments = parser.parse_args()

    nodes, relation_types, source, target, relation = load_graph(arguments.graph)
    table = classify(nodes, relation_types, source, target, relation, arguments.carrier_rule)
    print(f"graph {arguments.graph}, carrier_rule {arguments.carrier_rule}: "
          f"{len(table)} carrier product_of (coproduct_of) edges\n")
    print(table.kind.value_counts().to_string(), "\n")
    print(pd.crosstab(table.family, table.kind).to_string(), "\n")

    symbol_of = {str(identifier): str(symbol) for identifier, symbol in zip(nodes.ensembl_gene_id, nodes.gene_symbol)
                 if isinstance(identifier, str) and identifier}
    chosen = table[table.family == arguments.family].copy()
    if len(chosen):
        chosen["genes"] = [gene_symbols(rule, symbol_of) for rule in chosen.gene_reaction_rule]
        print(f"every carrier product_of edge into the {arguments.family} family:")
        for _, row in chosen.sort_values(["kind", "reaction"]).iterrows():
            print(f"  {row.kind:13s} {row.metabolite:34s} <- {row.reaction:12s} "
                  f"[{row.genes or 'no gene rule'}] {row.subsystem}")


if __name__ == "__main__":
    main()
