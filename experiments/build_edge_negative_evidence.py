"""Add the negative edge observations of decision 9.91 to a graph's edge evidence table.

experiments/build_edge_evidence.py adds the same columns when it builds the table and the sources' files are present;
this script adds them to a table built without them, or refreshes them, leaving every other column as it is. It refuses
a table that does not hold the graph's edges row for row. Columns of a source whose files are absent are not written
(graph/edge_negative_sources.py), so the trainer refuses that source rather than reading it as observing nothing.

It writes <graph-dir>/edge_negative_evidence_summary.json: per source the files read with their SHA-256 or why the source
is absent, the observations by family and relation, and, for the balance the owner asked for, each edge family's
positive evidence (its edges with records and its records, as the table counts them) beside the negative and positive
observations of every source; and how far the observations would move the gated edges' priors under the tiers at
strength 1 (graph/edge_negative_evidence.py).

Usage:
  python experiments/build_edge_negative_evidence.py --graph-dir data/processed/graph_full_neuronal_split_binders_drugs_v5
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.graph.edge_evidence import DEFAULT_TIERS_PATH, curated_edge_labels, edge_priors, read_edge_tiers
from mechanistic_pathway_learning.graph.edge_negative_evidence import (
    DEFAULT_LIKELIHOOD_RATIOS_PATH,
    SOURCES,
    apply_likelihood_ratios,
    log_likelihood_ratio,
    read_likelihood_ratios,
)
from mechanistic_pathway_learning.graph.edge_negative_sources import NegativeEvidencePaths, assemble_negative_evidence

EDGE_EVIDENCE_FILE = "edge_evidence.parquet"
SUMMARY_FILE = "edge_negative_evidence_summary.json"


def source_columns(columns) -> list[str]:
    return [column for column in columns if any(str(column).startswith(f"{source}_") for source in SOURCES)]


def family_balance(evidence: pd.DataFrame) -> dict:
    """Per edge family: its edges, the edges with at least one positive record and the records (the table's own
    count), beside each present source's edges with negative and with positive observations."""
    balance = {}
    for family, group in evidence.groupby("family"):
        entry = {"edges": int(len(group)), "edges_with_records": int((group["records"] > 0).sum()), "records": int(group["records"].sum())}
        for source in SOURCES:
            if f"{source}_negative" in group.columns:
                entry[f"{source}_negative_edges"] = int((group[f"{source}_negative"] > 0).sum())
                entry[f"{source}_positive_edges"] = int((group[f"{source}_positive"] > 0).sum())
        balance[str(family)] = entry
    return balance


def prior_shift(evidence: pd.DataFrame, tiers_path: Path, ratios_path: Path) -> dict:
    """At strength 1 under the tier table: per present source, how many gated edges its observations move and the mean
    prior before and after on those edges; and how many edge labels (decision 9.63 (b)) carry an observation, which the
    trainer does not move."""
    gated, probability, _ = edge_priors(evidence, read_edge_tiers(tiers_path))
    ratios = read_likelihood_ratios(ratios_path)
    labels = curated_edge_labels(evidence) if "human_records" in evidence.columns else np.zeros(len(evidence), dtype=bool)
    shifts = {}
    for source in SOURCES:
        if f"{source}_negative" not in evidence.columns:
            continue
        log_ratio, contributions = log_likelihood_ratio(evidence, ratios, (source,))
        moved = gated & ~labels & (log_ratio != 0)
        after = apply_likelihood_ratios(probability, gated & ~labels, log_ratio)
        observed = (evidence[f"{source}_negative"] > 0) | (evidence[f"{source}_positive"] > 0)
        shifts[source] = {"contributions": contributions, "gated_edges_moved": int(moved.sum()),
                          "mean_prior_before": float(np.mean(probability[moved])) if moved.any() else None,
                          "mean_prior_after": float(np.mean(after[moved])) if moved.any() else None,
                          "moved_down": int((moved & (log_ratio < 0)).sum()), "moved_up": int((moved & (log_ratio > 0)).sum()),
                          "labels_with_an_observation": int((labels & observed.to_numpy()).sum()),
                          "ungated_edges_with_an_observation": int((~gated & observed.to_numpy()).sum())}
    return shifts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--sources", nargs="+", choices=SOURCES, default=list(SOURCES))
    parser.add_argument("--tiers", type=Path, default=DEFAULT_TIERS_PATH)
    parser.add_argument("--likelihood-ratios", type=Path, default=DEFAULT_LIKELIHOOD_RATIOS_PATH)
    defaults = NegativeEvidencePaths()
    for name, value in vars(defaults).items():
        if name != "sources":
            parser.add_argument(f"--{name.replace('_', '-')}", type=Path, default=value)
    arguments = parser.parse_args()
    paths = NegativeEvidencePaths(**{name: getattr(arguments, name) for name in vars(defaults) if name != "sources"}, sources=tuple(arguments.sources))
    evidence_path = arguments.graph_dir / EDGE_EVIDENCE_FILE
    edges = pd.read_parquet(arguments.graph_dir / "edges.parquet")
    nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet")
    evidence = pd.read_parquet(evidence_path)
    endpoints = ["source_id", "target_id", "relation_type"]
    if len(evidence) != len(edges) or not all(np.array_equal(evidence[column].to_numpy(dtype=object), edges[column].to_numpy(dtype=object)) for column in endpoints):
        raise SystemExit(f"{evidence_path} does not hold {arguments.graph_dir}/edges.parquet row for row; rebuild it with experiments/build_edge_evidence.py first")
    evidence = evidence.drop(columns=[column for column in source_columns(evidence.columns) if column.split("_")[0] in {s.split("_")[0] for s in arguments.sources}])
    columns, summary = assemble_negative_evidence(evidence, edges, nodes, paths)
    evidence = pd.concat([evidence, columns], axis=1)
    evidence.to_parquet(evidence_path, index=False)
    summary.update({"graph_dir": str(arguments.graph_dir), "edges_sha256": hashlib.sha256((arguments.graph_dir / "edges.parquet").read_bytes()).hexdigest(),
                    "edge_evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(), "family_balance": family_balance(evidence),
                    "likelihood_ratios": str(arguments.likelihood_ratios), "tiers": str(arguments.tiers),
                    "prior_shift_at_strength_1": prior_shift(evidence, arguments.tiers, arguments.likelihood_ratios)})
    (arguments.graph_dir / SUMMARY_FILE).write_text(json.dumps(summary, indent=1, default=str) + "\n", encoding="utf-8")
    for source, record in summary["sources"].items():
        if "absent" in record:
            print(f"  {source:11s} absent: {record['absent']}")
            continue
        counts = summary["counts"].get(source, {})
        print(f"  {source:11s} {counts.get('negative', {}).get('edges', 0):7,} edges with a negative observation, {counts.get('positive', {}).get('edges', 0):7,} with a positive")
    print(f"wrote {evidence_path} and {arguments.graph_dir / SUMMARY_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
