"""The before-and-after counts of the expression rebuild, from two graph directories (an engineering comparison,
read-only on both).

Why. The item 37 rulings draft, section 8 (c), ruled on 16 November 2026: expression values are attached after the
last build stage that adds gene nodes, built in one rebuild with section 7's region rule, and "the before-and-after
counts (genes whose flag changes, pores and catalysts, drug targets moving from a plasma to a brain site) shown to the
owner once the rebuild has run". This script takes those counts from the build before and the build after:

- **Genes whose flag changes.** `brain_expressed` per gene node, matched by node id, an unknown flag read as not
  expressed, since "Every step that gates on `brain_expressed` reads unknown as not expressed" (the same section):
  how many turn expressed and how many turn not expressed, how many unknowns became known, and the nodes present in
  one build only, counted apart.
- **Pores and catalysts.** The pores of each build, a reaction with an edge into VM_c (a conductive pore's
  conductance edge), and the catalysts, the sources of `catalyzed_by` edges, with those added and removed, and the
  catalysts whose gene's flag changes. The edges into VM_c are also counted by their source's node type, because a
  build whose conductance edges come from the neuronal pools rather than from reactions has no pores by this rule and
  would otherwise be recorded as a build with none: on graph_full_neuronal_split_binders_drugs_v5 (12 November 2026)
  all 6 edges into VM_c are `driving_force` from metabolite pool nodes, so its pore count is 0. The catalysts a flag
  change cannot reach are counted apart: the rule matches a catalyst by its own gene_symbol, and 316 of that build's
  3,181 catalysts are `protein_entity` nodes (complexes) with no symbol, so no flag change is ever reported for them.
- **Drug targets moving from a plasma to a brain site.** A drug's mechanism target (the target_node_id of
  `drug_entry_nodes.parquet`) is at a brain site when its gene symbol is brain-expressed and at a plasma site
  otherwise, the site rule of experiments/measure_target_occupancy.py (brain_expressed_genes), which reads the flag
  by symbol, so a protein node takes its gene's: the targets that move in each direction, and the drugs that hold one.

The lists are given in full beside the counts, sorted, so the owner can read which genes, pores, catalysts and drugs
moved.

Usage:
  PYTHONPATH=. python experiments/compare_expression_rebuild.py --before <graph directory> --after <graph directory> \\
      --output <path outside data/>
"""
from __future__ import annotations

import argparse
import collections
import json
import time
from pathlib import Path

import pandas as pd

from experiments.measure_saturation_counts import refuse_output_under_data, sha256_of
from experiments.measure_target_occupancy import brain_expressed_genes

MEMBRANE_POTENTIAL_NODE = "VM_c"
CATALYSIS_RELATION = "catalyzed_by"
DRUG_ENTRY_FILE = "drug_entry_nodes.parquet"


def flag_changes(before: pd.DataFrame, after: pd.DataFrame) -> dict:
    """Gene nodes whose brain_expressed flag changes between two nodes tables (module docstring), unknown read as False."""
    def flags(nodes: pd.DataFrame) -> pd.DataFrame:
        genes = nodes[nodes.node_type == "gene"].set_index("node_id")
        known = genes.brain_expressed.notna()
        return pd.DataFrame({"expressed": genes.brain_expressed.where(known, False).astype(bool), "known": known})

    old, new = flags(before), flags(after)
    common = old.index.intersection(new.index)
    turned_on = sorted(common[(~old.expressed[common]) & new.expressed[common]])
    turned_off = sorted(common[old.expressed[common] & (~new.expressed[common])])
    became_known = sorted(common[(~old.known[common]) & new.known[common]])
    return {"genes_in_both": int(len(common)), "turned_expressed": turned_on, "turned_not_expressed": turned_off,
            "unknown_became_known": became_known, "counts": {"turned_expressed": len(turned_on), "turned_not_expressed": len(turned_off),
                                                              "unknown_became_known": len(became_known)},
            "genes_only_before": int(len(old.index.difference(new.index))), "genes_only_after": int(len(new.index.difference(old.index)))}


def pores_and_catalysts(edges: pd.DataFrame, nodes: pd.DataFrame) -> tuple[set[str], set[str], dict[str, int]]:
    """(pores: reactions with an edge into VM_c, catalysts: sources of catalyzed_by edges, the edges into VM_c by
    "<relation> from <source node type>") of one build.

    The third tells a build with no pore from a build whose conductance edges enter VM_c from somewhere else (module
    docstring, "Pores and catalysts")."""
    type_of = dict(zip(nodes.node_id, nodes.node_type))
    into = edges[edges.target_id == MEMBRANE_POTENTIAL_NODE]
    pores = {source for source in into.source_id if type_of.get(source) == "reaction"}
    catalysts = set(edges.source_id[edges.relation_type == CATALYSIS_RELATION])
    by_source = collections.Counter(f"{relation} from {type_of.get(source)}" for source, relation in zip(into.source_id, into.relation_type))
    return pores, catalysts, dict(sorted(by_source.items()))


def set_change(before: set[str], after: set[str]) -> dict:
    added, removed = sorted(after - before), sorted(before - after)
    return {"before": len(before), "after": len(after), "added": added, "removed": removed, "added_count": len(added), "removed_count": len(removed)}


def target_site_changes(entries_before: pd.DataFrame, entries_after: pd.DataFrame, symbol_before: dict, symbol_after: dict,
                        brain_genes_before: set[str], brain_genes_after: set[str]) -> dict:
    """The (drug, target) pairs of both builds whose site moves between plasma and brain, by the site rule."""
    def pairs(entries: pd.DataFrame, symbol_of: dict) -> dict[tuple[str, str], str]:
        return {(drug, target): symbol_of.get(target, "") for drug, target in zip(entries.perturbation_id, entries.target_node_id)}

    old, new = pairs(entries_before, symbol_before), pairs(entries_after, symbol_after)
    to_brain, to_plasma = [], []
    for pair in sorted(set(old) & set(new)):
        was_brain, is_brain = old[pair] in brain_genes_before, new[pair] in brain_genes_after
        if not was_brain and is_brain:
            to_brain.append([*pair, new[pair]])
        elif was_brain and not is_brain:
            to_plasma.append([*pair, new[pair]])
    return {"pairs_in_both": len(set(old) & set(new)), "pairs_only_before": len(set(old) - set(new)), "pairs_only_after": len(set(new) - set(old)),
            "plasma_to_brain": to_brain, "brain_to_plasma": to_plasma,
            "counts": {"plasma_to_brain_pairs": len(to_brain), "plasma_to_brain_targets": len({target for _, target, _ in to_brain}),
                       "plasma_to_brain_drugs": len({drug for drug, _, _ in to_brain}), "brain_to_plasma_pairs": len(to_plasma),
                       "brain_to_plasma_drugs": len({drug for drug, _, _ in to_plasma})}}


def compare(before: Path, after: Path) -> dict:
    nodes_before = pd.read_parquet(before / "nodes.parquet", columns=["node_id", "node_type", "gene_symbol", "brain_expressed"])
    nodes_after = pd.read_parquet(after / "nodes.parquet", columns=["node_id", "node_type", "gene_symbol", "brain_expressed"])
    edges_before = pd.read_parquet(before / "edges.parquet", columns=["source_id", "target_id", "relation_type"])
    edges_after = pd.read_parquet(after / "edges.parquet", columns=["source_id", "target_id", "relation_type"])
    pores_before, catalysts_before, into_before = pores_and_catalysts(edges_before, nodes_before)
    pores_after, catalysts_after, into_after = pores_and_catalysts(edges_after, nodes_after)
    flags = flag_changes(nodes_before, nodes_after)
    symbol_after = dict(zip(nodes_after.node_id, nodes_after.gene_symbol))
    gene_of_symbol_changed = {symbol_after.get(node) for node in flags["turned_expressed"] + flags["turned_not_expressed"]}
    gene_of_symbol_changed = {symbol for symbol in gene_of_symbol_changed if isinstance(symbol, str) and symbol}
    type_after = dict(zip(nodes_after.node_id, nodes_after.node_type))
    without_symbol = sorted(catalyst for catalyst in catalysts_before & catalysts_after
                            if not isinstance(symbol_after.get(catalyst), str) or not symbol_after.get(catalyst))
    record = {"genes_whose_flag_changes": flags, "pores": set_change(pores_before, pores_after), "catalysts": set_change(catalysts_before, catalysts_after),
              "edges_into_membrane_potential": {"before": into_before, "after": into_after},
              "catalysts_whose_gene_flag_changes": sorted(catalyst for catalyst in catalysts_before & catalysts_after
                                                          if symbol_after.get(catalyst) in gene_of_symbol_changed),
              # the rule above matches a catalyst by its own gene_symbol, so a catalyst without one is outside it
              "catalysts_a_flag_change_cannot_reach": {"count": len(without_symbol),
                                                       "by_node_type": dict(sorted(collections.Counter(type_after.get(catalyst) for catalyst in without_symbol).items())),
                                                       "catalysts": without_symbol}}
    if (before / DRUG_ENTRY_FILE).exists() and (after / DRUG_ENTRY_FILE).exists():
        record["drug_target_sites"] = target_site_changes(
            pd.read_parquet(before / DRUG_ENTRY_FILE), pd.read_parquet(after / DRUG_ENTRY_FILE),
            dict(zip(nodes_before.node_id, nodes_before.gene_symbol)), symbol_after, brain_expressed_genes(before), brain_expressed_genes(after))
    else:
        record["drug_target_sites"] = f"not compared: {DRUG_ENTRY_FILE} is missing from one of the builds"
    return record


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--before", type=Path, required=True, help="the graph directory built before the expression rebuild")
    parser.add_argument("--after", type=Path, required=True, help="the graph directory the expression rebuild wrote")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    refuse_output_under_data(arguments.output)
    record = {"what": "the before-and-after counts of the expression rebuild (experiments/compare_expression_rebuild.py)", "date": time.strftime("%Y-%m-%d"),
              "before": str(arguments.before), "after": str(arguments.after),
              "inputs_sha256": {str(path): sha256_of(path) for directory in (arguments.before, arguments.after)
                                for path in sorted(directory.glob("*.parquet")) if path.name in ("nodes.parquet", "edges.parquet", DRUG_ENTRY_FILE)},
              **compare(arguments.before, arguments.after)}
    arguments.output.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    sites = record["drug_target_sites"]
    print(json.dumps({"genes": record["genes_whose_flag_changes"]["counts"], "pores": {k: record["pores"][k] for k in ("before", "after", "added_count", "removed_count")},
                      "catalysts": {k: record["catalysts"][k] for k in ("before", "after", "added_count", "removed_count")},
                      "drug_target_sites": sites["counts"] if isinstance(sites, dict) else sites}, indent=1))


if __name__ == "__main__":
    main()
