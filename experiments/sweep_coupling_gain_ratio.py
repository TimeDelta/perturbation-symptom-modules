"""How the cAMP sign of the receptors coupled to both Gs and Gi/o depends on a ratio of relation gains (decision 9.77).

Every signed relation's gain is set to BASE_GAIN, the unsigned binds to 0, except one, which is set to ratio x BASE_GAIN, and the net response of the
transmembrane adenylyl cyclases to a gain-of-function seed on each receptor's gene is read under the registered
normalisation. Before the coupling edge types, the varied relation is inhibits (against activates): it carries every
Gi/o-to-cyclase edge and its gain is shared with the rest of the graph. After them, the varied relation is
couples_secondary (against couples_primary), and inhibits is swept as well to show whether the cyclase still depends on it.

Usage:
  python experiments/sweep_coupling_gain_ratio.py --graph-dir <graph> --evidence-dir <evidence> --vary inhibits couples_secondary --output <json>
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure_forward_cone_divisor import build_encoder  # noqa: E402

from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data  # noqa: E402

RECEPTORS = {"ADRB2": 1, "PTGER4": 1, "ADORA1": -1}  # the expected cyclase direction from the primary transducer
ADENYLYL_CYCLASES = [f"ADCY{number}" for number in range(1, 10)]
BASE_GAIN = 0.1
RATIOS = (0.25, 0.5, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0)


def logit_of_gain(gain: float, maximum_gain: float) -> float:
    return math.log(gain / (maximum_gain - gain))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--vary", nargs="+", required=True)
    parser.add_argument("--normalisation", default="forward_cone")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    data = load_experiment_data(arguments.graph_dir, arguments.evidence_dir, group_by="disease_cluster_and_targets", drug_entry="nodes")
    graph_nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet")
    symbol_of_node_id = dict(zip(graph_nodes.node_id, graph_nodes.gene_symbol))
    symbol = np.array([symbol_of_node_id.get(node_id) if isinstance(symbol_of_node_id.get(node_id), str) else "" for node_id in data.node_ids])
    node_type = np.asarray(data.node_types)
    gene_node = {symbol[i]: i for i in range(len(symbol)) if node_type[i] == "gene" and symbol[i]}
    cyclase_nodes = torch.as_tensor(np.flatnonzero(np.isin(symbol, ADENYLYL_CYCLASES) & (node_type != "gene")))
    encoder = build_encoder(data, arguments.normalisation, propagation_channels=1)
    receptors = [receptor for receptor in RECEPTORS if receptor in gene_node]
    index = torch.as_tensor([[gene_node[receptor]] for receptor in receptors])
    sign_and_magnitude = torch.tensor([[[1.0, 1.0]]] * len(receptors))
    base_logit = logit_of_gain(BASE_GAIN, encoder.maximum_gain)
    results = {}
    for relation in arguments.vary:
        if relation not in encoder.relation_names:
            results[relation] = "not in this graph"
            continue
        position = encoder.relation_names.index(relation)
        sweep = []
        for ratio in RATIOS:
            with torch.no_grad():
                encoder.gain_logit.fill_(base_logit)
                # an unsigned relation (binds) takes 0.9 tanh(logit), so the signed base logit would give it a strong
                # negative gain; it is held at 0, as in the equal-gain check of measure_g_alpha_family_balance.py
                encoder.gain_logit[encoder.relation_is_unsigned] = 0.0
                encoder.gain_logit[position] = logit_of_gain(BASE_GAIN * ratio, encoder.maximum_gain)
                response = encoder.response(index, sign_and_magnitude)[:, :, 0]
            net = response[:, cyclase_nodes].sum(dim=1)
            sweep.append({"ratio": ratio, **{receptor: float(net[row]) for row, receptor in enumerate(receptors)}})
        first_flip = {}
        for receptor in receptors:
            flipped = [row["ratio"] for row in sweep if np.sign(row[receptor]) != RECEPTORS[receptor]]
            first_flip[receptor] = min(flipped) if flipped else None
        results[relation] = {"sweep": sweep, "smallest_ratio_with_the_wrong_sign": first_flip}
        print(relation, "smallest ratio with the wrong cyclase sign:", first_flip, flush=True)
    arguments.output.write_text(json.dumps({"graph": str(arguments.graph_dir), "normalisation": arguments.normalisation, "base_gain": BASE_GAIN,
                                            "receptors_expected_direction": RECEPTORS, "results": results}, indent=1) + "\n")


if __name__ == "__main__":
    main()
