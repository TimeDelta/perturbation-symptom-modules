"""Whether the cAMP response of a receptor coupled to both Gs and Gi/o follows its primary transducer or the number of
genes in each G-alpha family (decision 9.77).

Every admitted coupling (configs/admitted_receptor_g_alpha_coupling.csv, decision 9.23) is expanded from a family to
its member genes, and each adenylyl cyclase is fed by every member gene that OmniPath links to it. So the two families
can reach a cyclase through different numbers of edges, and under a per-destination divisor a receptor admitted to
both families then drives the cyclase by the difference in edge counts, whichever family is its primary transducer.

What this measures on a graph:
  1. the signed edges from each G-alpha member gene's nodes into each adenylyl cyclase's nodes, by family;
  2. for every receptor whose graph edges reach both a Gs and a Gi/o member, the sign of the response at the adenylyl
     cyclases and at cytosolic cAMP to a gain-of-function seed on the receptor's gene, with every relation's gain set
     equal so the structure alone decides, under total_in_degree and forward_cone;
  3. the same with each G-alpha-to-cyclase edge weighted by 1 over the number of its family's members feeding that
     cyclase, which is suggestion (b) of 9.77: each family reaches the cyclase as one unit.

The expected sign is the primary transducer's: up for a receptor whose only primary family is Gs, down for Gi/o, and
none for a receptor with both as primary.

Usage:
  python experiments/measure_g_alpha_family_balance.py --graph-dir data/processed/graph_full_neuronal_split_binders_drugs_v5 \
      --evidence-dir data/processed/evidence_full_v5 --output docs/g_alpha_family_balance_measured.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure_forward_cone_divisor import build_encoder  # noqa: E402

from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data  # noqa: E402

COUPLING_TABLE = Path("configs/admitted_receptor_g_alpha_coupling.csv")
FAMILY_OF_G_ALPHA = {"GNAS": "Gs", "GNAL": "Gs", "GNAI1": "Gi/o", "GNAI2": "Gi/o", "GNAI3": "Gi/o", "GNAO1": "Gi/o", "GNAZ": "Gi/o"}
ADENYLYL_CYCLASES = [f"ADCY{number}" for number in range(1, 10)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    data = load_experiment_data(arguments.graph_dir, arguments.evidence_dir, group_by="disease_cluster_and_targets", drug_entry="nodes")
    graph_nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet")
    symbol_of_node_id = dict(zip(graph_nodes.node_id, graph_nodes.gene_symbol))
    node_ids = list(data.node_ids)
    symbol = np.array([symbol_of_node_id.get(node_id) if isinstance(symbol_of_node_id.get(node_id), str) else "" for node_id in node_ids])
    node_type = np.asarray(data.node_types)
    source, target, sign = np.asarray(data.edge_source), np.asarray(data.edge_target), np.asarray(data.edge_sign, dtype=float)

    # 1. G alpha -> adenylyl cyclase edges, by family and sign
    into_cyclase = np.isin(symbol[source], list(FAMILY_OF_G_ALPHA)) & np.isin(symbol[target], ADENYLYL_CYCLASES)
    edge_counts = defaultdict(lambda: defaultdict(int))
    for edge in np.flatnonzero(into_cyclase):
        family = FAMILY_OF_G_ALPHA[symbol[source[edge]]]
        edge_counts[symbol[target[edge]]][f"{family} {'+' if sign[edge] > 0 else '-' if sign[edge] < 0 else '0'}"] += 1
    print("G alpha -> adenylyl cyclase edges:", json.dumps({cyclase: dict(counts) for cyclase, counts in sorted(edge_counts.items())}))

    # 2. receptors whose signed graph edges reach both families
    coupling = pd.read_csv(COUPLING_TABLE)
    primary_families = coupling[coupling.transducer_role == "primary"].groupby("receptor_gene_symbol").g_alpha_family.agg(set).to_dict()
    to_g_alpha = np.isin(symbol[target], list(FAMILY_OF_G_ALPHA)) & (sign != 0) & ~np.isin(symbol[source], list(FAMILY_OF_G_ALPHA))
    families_reached = defaultdict(set)
    for edge in np.flatnonzero(to_g_alpha):
        families_reached[symbol[source[edge]]].add(FAMILY_OF_G_ALPHA[symbol[target[edge]]])
    dual = sorted(receptor for receptor, families in families_reached.items()
                  if {"Gs", "Gi/o"} <= families and receptor in primary_families)
    print(f"{len(dual)} annotated receptors reach both Gs and Gi/o in the graph")

    gene_node_of = {symbol[index]: index for index in range(len(node_ids)) if node_type[index] == "gene" and symbol[index]}
    cyclase_nodes = np.flatnonzero(np.isin(symbol, ADENYLYL_CYCLASES) & (node_type != "gene"))
    camp_nodes = [index for index, name in enumerate(data.node_display_name) if str(name).lower() == "camp" and str(data.node_compartment[index]) == "c"]

    # 3. the family-as-one-unit weighting: each G alpha -> cyclase edge over the count of its family's edges into that cyclase node
    base_weight = np.ones(len(source)) if data.edge_weight is None else np.asarray(data.edge_weight, dtype=float).copy()
    family_weight = base_weight.copy()
    family_edges_into = defaultdict(int)
    for edge in np.flatnonzero(into_cyclase):
        family_edges_into[(target[edge], FAMILY_OF_G_ALPHA[symbol[source[edge]]])] += 1
    for edge in np.flatnonzero(into_cyclase):
        family_weight[edge] = base_weight[edge] / family_edges_into[(target[edge], FAMILY_OF_G_ALPHA[symbol[source[edge]]])]

    def expected_direction(receptor: str) -> int:
        primary = primary_families.get(receptor, set())
        if "Gs" in primary and "Gi/o" not in primary:
            return 1
        if "Gi/o" in primary and "Gs" not in primary:
            return -1
        return 0

    rows = []
    seedable = [receptor for receptor in dual if receptor in gene_node_of]
    for arm, weights in (("as_built", base_weight), ("family_as_one_unit", family_weight)):
        data.edge_weight = weights
        for normalisation in ("total_in_degree", "forward_cone"):
            encoder = build_encoder(data, normalisation, propagation_channels=1)
            with torch.no_grad():
                encoder.gain_logit.zero_()  # every relation the same gain, so the structure alone sets the sign
            index = torch.as_tensor([[gene_node_of[receptor]] for receptor in seedable])
            sign_and_magnitude = torch.tensor([[[1.0, 1.0]]] * len(seedable))
            with torch.no_grad():
                response = encoder.response(index, sign_and_magnitude)[:, :, 0]  # [R, N]
            for row, receptor in enumerate(seedable):
                cyclase_response = response[row, cyclase_nodes]
                camp_response = float(response[row, camp_nodes].sum()) if camp_nodes else float("nan")
                rows.append({"arm": arm, "normalisation": normalisation, "receptor": receptor, "primary": sorted(primary_families.get(receptor, [])),
                             "expected": expected_direction(receptor), "cyclase_net": float(cyclase_response.sum()),
                             "cyclases_up": int((cyclase_response > 0).sum()), "cyclases_down": int((cyclase_response < 0).sum()),
                             "camp": camp_response})
    table = pd.DataFrame(rows)
    table["cyclase_sign"] = np.sign(table.cyclase_net).astype(int)
    summary = {}
    for (arm, normalisation), group in table.groupby(["arm", "normalisation"]):
        decidable = group[group.expected != 0]
        summary[f"{arm} / {normalisation}"] = {
            "receptors": int(len(group)), "with_one_primary_family": int(len(decidable)),
            "cyclase_sign_matches_primary": int((decidable.cyclase_sign == decidable.expected).sum()),
            "cyclase_sign_opposite_to_primary": int((decidable.cyclase_sign == -decidable.expected).sum()),
            "cyclase_response_zero": int((decidable.cyclase_sign == 0).sum()),
            "gs_primary_receptors_driving_cyclase_down": sorted(decidable[(decidable.expected == 1) & (decidable.cyclase_sign == -1)].receptor),
        }
    report = {"graph": str(arguments.graph_dir), "g_alpha_to_cyclase_edges": {cyclase: dict(counts) for cyclase, counts in sorted(edge_counts.items())},
              "receptors_reaching_both_gs_and_gi_o": dual, "receptors_seeded": seedable, "camp_nodes": [node_ids[i] for i in camp_nodes],
              "summary": summary, "rows": table.to_dict(orient="records")}
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=1, default=str) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
