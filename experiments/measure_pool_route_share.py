"""What enters VM_c on a build, by route: the pool edges' share of the weight, for amendment item 37's limits (an
engineering measurement, read-only on a graph directory).

Why. Decision 9.129's addition of 12 November 2026 measured, on a dry-run build at commit `22e7e6e9` (the neuronal
variant from `data/processed/graph_full_manganese` of 4 November 2026, written to a scratch directory), "59 edges into
`VM_c`: 56 conductance edges weighing 685.2 mV and the pool edges 2.296 mV, so the pool route is 0.33 per cent of what
enters `VM_c`". Item 37 states its limit with that figure and is to remeasure it on its own build; the 12 November
figure stays the record of the build it was taken on (CLAUDE.md, "A measurement carries the graph it was taken on").
This script takes that figure on any build: every edge into VM_c, grouped by its relation and by what its source is
(a neuronal ion pool, a node whose id starts NEURON_; a reaction, which is how a conductive pore's conductance edge
enters; anything else), with the count and the stored weights summed, and the pools' share of the total weight.

What it does not take. The same addition gives a second set of figures, "per single-ion pore the pool route reaches
`VM_c` at 1.5e-4, 3.3e-4 and 9.1e-3 of the direct edge for sodium, potassium and chloride". The record does not say
how they were computed: under which normalisation the pool's inputs were averaged (item 28's total in-degree or the
registered forward_cone, whose divisor depends on the perturbation's cone), and which statistic was taken over the
pores of one ion. A remeasurement by another method would not be comparable, so this script stops at them, and the
method is a question for the owner.

Usage:
  PYTHONPATH=. python experiments/measure_pool_route_share.py --graph-dir <build directory> --output <path outside data/>
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd

from experiments.measure_saturation_counts import refuse_output_under_data, sha256_of

MEMBRANE_POTENTIAL_NODE = "VM_c"
NEURONAL_POOL_PREFIX = "NEURON_"
REACTION_NODE_TYPE = "reaction"


def source_kind(source_id: str, node_type: str | None) -> str:
    """A neuronal ion pool, a reaction (a conductive pore's conductance edge), or another node."""
    if str(source_id).startswith(NEURONAL_POOL_PREFIX):
        return "neuronal_pool"
    if node_type == REACTION_NODE_TYPE:
        return "reaction"
    return "other"


def inputs_of_membrane_potential(edges: pd.DataFrame, nodes: pd.DataFrame) -> dict:
    """The edges into VM_c by relation and source kind, with their weights, and the pools' share of the total weight.

    edges needs source_id, target_id and relation_type, and weight where the build stores one (each edge counts 1
    without it, which the result says); nodes needs node_id and node_type."""
    into = edges[edges.target_id == MEMBRANE_POTENTIAL_NODE].copy()
    weighted = "weight" in into.columns
    into["weight"] = into.weight.astype(float) if weighted else 1.0
    type_of = dict(zip(nodes.node_id, nodes.node_type))
    into["source_kind"] = [source_kind(source, type_of.get(source)) for source in into.source_id]
    total = float(into.weight.sum())
    groups = into.groupby(["relation_type", "source_kind"], sort=True).weight.agg(["count", "sum"]).reset_index()
    pools = into[into.source_kind == "neuronal_pool"]
    return {"edges_into_VM_c": int(len(into)), "weights_stored": weighted, "total_weight": total,
            "by_relation_and_source": [{"relation_type": row.relation_type, "source_kind": row.source_kind, "edges": int(row["count"]),
                                        "weight": float(row["sum"])} for _, row in groups.iterrows()],
            "pool_edges": {source: float(weight) for source, weight in sorted(zip(pools.source_id, pools.weight))},
            "pool_weight": float(pools.weight.sum()),
            "pool_share_of_total_weight": float(pools.weight.sum() / total) if total else None,
            "conductance_edges_from_reactions": int((into.source_kind == "reaction").sum()),
            "conductance_weight_from_reactions": float(into.weight[into.source_kind == "reaction"].sum())}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    refuse_output_under_data(arguments.output)
    edges = pd.read_parquet(arguments.graph_dir / "edges.parquet")
    nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet", columns=["node_id", "node_type"])
    record = {"what": "the edges into VM_c and the pool edges' share of their weight (experiments/measure_pool_route_share.py)",
              "date": time.strftime("%Y-%m-%d"), "graph_dir": str(arguments.graph_dir),
              "inputs_sha256": {str(path): sha256_of(path) for path in (arguments.graph_dir / "edges.parquet", arguments.graph_dir / "nodes.parquet")},
              **inputs_of_membrane_potential(edges, nodes),
              "not_taken": "the per-single-ion-pore ratios of decision 9.129's addition of 12 November 2026; their method is not recorded (module docstring)"}
    arguments.output.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({key: record[key] for key in ("date", "graph_dir", "edges_into_VM_c", "total_weight", "pool_weight", "pool_share_of_total_weight")}, indent=1))


if __name__ == "__main__":
    main()
