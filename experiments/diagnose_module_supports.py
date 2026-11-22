"""Where the trained modules of finished runs sit: for every node a module holds, its in-degree, how many training
sources can reach it, and how much of the module's reading of it comes from a single perturbation.

The reach rule (models/support_reach.py) keeps out of every module a node that one perturbation source or none can
reach. A node many sources can reach in principle may still be read, in practice, through one perturbation alone, and
a module holding it then works as a lookup entry for that perturbation's labels; this measures how often that happens
after training, which the rule cannot see before it. It also gives the in-degree of each support node beside the
graph's, the measurement that would set the strength of a degree-weighted node cost, if one is adopted.

For module k and support node n, the module's reading of n under perturbation p is support[k, n] * (field[p, n, :] .
readout_weight[k, :]), its term in the module's activation logit (NoisyOrPathwayModuleHead.module_activation, sum
pooling). The dominance share of n in k is the largest absolute reading over the run's training perturbations divided by
the sum of them: 1 when a single perturbation is all the module reads there, 1 / P when P perturbations are read equally.
A node is in a module's support when its expected gate is at least --support-threshold.

The run is rebuilt as experiments/evaluate_on_rewired_graph.py rebuilds it (its arguments from results.json, its best or
refitted weights), and its training rows are rebuilt with the trainer's split_indices and checked against the test
perturbations the run recorded. Lockbox runs are refused, since the lockbox is blinded until the confirmatory scoring,
and so are rewired runs, whose graph this does not rebuild.

    OMP_NUM_THREADS=1 PYTHONPATH=. python experiments/diagnose_module_supports.py --run-dirs runs/<configuration>/<fold> ... \\
      --json-output runs/module_support_diagnosis.json --markdown-output runs/module_support_diagnosis.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.evaluate_on_rewired_graph import experiment_data, stored_arguments, trained_models  # noqa: E402
from experiments.run_main_model import build_edge_priors, encode, pad_perturbations, split_indices  # noqa: E402
from mechanistic_pathway_learning.models.support_reach import distinct_seed_nodes, encoder_walkable_adjacency, source_reach  # noqa: E402

DEFAULT_SUPPORT_THRESHOLD = 0.5
DOMINANCE_LEVELS = (0.5, 0.9)
TOP_NODES_SHOWN = 10


def dominance_shares(readings: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """readings [perturbations, nodes] of one module: per node, the largest absolute reading over the sum of them, and
    the row it comes from; NaN and -1 for a node no perturbation moves."""
    magnitude = np.abs(readings)
    total = magnitude.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        share = np.where(total > 0, magnitude.max(axis=0) / total, np.nan)
    top_row = np.where(total > 0, magnitude.argmax(axis=0), -1)
    return share, top_row


def module_readings(encoder, head, data, rows: np.ndarray, support_nodes: list[np.ndarray], adjacencies, arguments, device) -> list[np.ndarray]:
    """For each module, the readings [len(rows), len(its support nodes)] of its support nodes under each row's field."""
    encoder.eval()
    head.eval()  # before the support is read: in training mode the gate is a random sample, in eval mode its expectation
    support = head.module_support().detach()
    readout = head.module_readout_weight.detach()
    readings = [[] for _ in support_nodes]
    with torch.no_grad():
        for start in range(0, len(rows), arguments.batch_size):
            batch = rows[start:start + arguments.batch_size]
            node_index, sign_and_magnitude = pad_perturbations(data, batch)
            field = encode(encoder, node_index.to(device), sign_and_magnitude.to(device), adjacencies, arguments.field)
            for module, nodes in enumerate(support_nodes):
                node_tensor = torch.as_tensor(nodes, dtype=torch.long, device=field.device)
                term = support[module, node_tensor][None, :] * (field[:, node_tensor, :] @ readout[module])
                readings[module].append(term.cpu().numpy())
    return [np.concatenate(parts, axis=0) if parts else np.zeros((0, len(nodes))) for parts, nodes in zip(readings, support_nodes)]


def describe_modules(data, rows: np.ndarray, expected_gate: np.ndarray, readings: list[np.ndarray], support_nodes: list[np.ndarray],
                     in_degree: np.ndarray, reach: np.ndarray) -> list[dict]:
    """One summary per module of where its support sits and how much of it one perturbation dominates."""
    graph_degree_99th = float(np.percentile(in_degree, 99))
    modules = []
    for module, nodes in enumerate(support_nodes):
        share, top_row = dominance_shares(readings[module])
        by_gate = nodes[np.argsort(-expected_gate[module, nodes])][:TOP_NODES_SHOWN]
        position = {node: index for index, node in enumerate(nodes.tolist())}
        modules.append({
            "module": module,
            "support_nodes": int(len(nodes)),
            "median_in_degree": float(np.median(in_degree[nodes])) if len(nodes) else None,
            "share_in_the_graphs_top_1_percent_by_in_degree": float(np.mean(in_degree[nodes] > graph_degree_99th)) if len(nodes) else None,
            "median_reach": float(np.median(reach[nodes])) if len(nodes) else None,
            "median_dominance_share": float(np.nanmedian(share)) if np.isfinite(share).any() else None,
            **{f"share_of_nodes_dominated_above_{level}": float(np.mean(share[np.isfinite(share)] > level)) if np.isfinite(share).any() else None
               for level in DOMINANCE_LEVELS},
            "nodes_no_training_perturbation_moves": int(np.isnan(share).sum()),
            "top_nodes_by_gate": [{"node": str(data.node_ids[node]), "expected_gate": round(float(expected_gate[module, node]), 4),
                                   "in_degree": int(in_degree[node]), "reach": int(reach[node]),
                                   "dominance_share": None if np.isnan(share[position[node]]) else round(float(share[position[node]]), 4),
                                   "dominated_by": None if top_row[position[node]] < 0 else str(data.perturbation_ids[rows[top_row[position[node]]]])}
                                  for node in by_gate.tolist()],
        })
    return modules


def training_rows(data, arguments, results: dict, fold_directory: Path) -> np.ndarray:
    """The rows the run's weights were fitted on, rebuilt with the trainer's split and checked against its test rows."""
    train_indices, validation_indices, test_indices, _ = split_indices(data, arguments)
    if [data.perturbation_ids[i] for i in test_indices] != results["test_perturbation_ids"]:
        raise SystemExit(f"{fold_directory}: the split rebuilt here does not give the test perturbations the run recorded")
    return np.sort(np.concatenate([train_indices, validation_indices])) if results.get("refit") else np.asarray(train_indices)


def diagnose_fold(fold_directory: Path, support_threshold: float) -> dict:
    results = json.loads((fold_directory / "results.json").read_text())
    arguments = stored_arguments(results)
    if arguments.score_lockbox or "lockbox" in fold_directory.name or fold_directory.parent.name.endswith("_confirmatory"):
        raise SystemExit(f"{fold_directory}: lockbox runs are blinded until the confirmatory scoring")
    if results.get("rewiring"):
        raise SystemExit(f"{fold_directory}: a rewired run's graph is not rebuilt here")
    if arguments.head == "sigmoid" or arguments.encoder != "linear_response":
        raise SystemExit(f"{fold_directory}: module supports and reach are defined for the noisy-OR head on the linear-response encoder")
    device = torch.device("cpu")
    data = experiment_data(arguments)
    build_edge_priors(data, arguments)
    rows = training_rows(data, arguments, results, fold_directory)
    checkpoint_name = "refit_checkpoint.pt" if results.get("refit") else "checkpoint.pt"
    loaded = torch.load(fold_directory / checkpoint_name, map_location=device, weights_only=False)
    checkpoint = {"state": {}, "encoder": loaded["encoder"], "head": loaded["head"]} if results.get("refit") else loaded
    torch.manual_seed(arguments.seed)
    encoder, head, adjacencies = trained_models(data, arguments, checkpoint, device)
    expected_gate = head.support_gate.expected_gate().detach().cpu().numpy()
    support_nodes = [np.flatnonzero(expected_gate[module] >= support_threshold) for module in range(expected_gate.shape[0])]
    adjacency, carries = encoder_walkable_adjacency(encoder, len(data.node_ids))
    reach = source_reach(adjacency, distinct_seed_nodes(data.perturbation_seeds[row] for row in rows), carries)
    in_degree = np.bincount(np.asarray(data.edge_target, dtype=int), minlength=len(data.node_ids))
    readings = module_readings(encoder, head, data, rows, support_nodes, adjacencies, arguments, device)
    return {"run": str(fold_directory), "checkpoint": checkpoint_name, "training_rows": int(len(rows)), "support_threshold": support_threshold,
            "graph_dir": str(arguments.graph_dir), "graph_median_in_degree": float(np.median(in_degree)),
            "graph_99th_percentile_in_degree": float(np.percentile(in_degree, 99)),
            "module_support_minimum_reach": int(getattr(arguments, "module_support_minimum_reach", 0)),
            "modules": describe_modules(data, rows, expected_gate, readings, support_nodes, in_degree, reach)}


def markdown(diagnoses: list[dict]) -> str:
    lines = ["| run | module | support nodes | median in-degree (graph) | in top 1% | median reach | median dominance | dominated > 0.5 | > 0.9 |",
             "|---|---|---|---|---|---|---|---|---|"]
    def shown(value, digits=2):
        return "-" if value is None else f"{value:.{digits}f}" if isinstance(value, float) else str(value)
    for diagnosis in diagnoses:
        for module in diagnosis["modules"]:
            lines.append(f"| {Path(diagnosis['run']).name} | {module['module']} | {module['support_nodes']} | "
                         f"{shown(module['median_in_degree'], 0)} ({diagnosis['graph_median_in_degree']:.0f}) | "
                         f"{shown(module['share_in_the_graphs_top_1_percent_by_in_degree'])} | {shown(module['median_reach'], 0)} | "
                         f"{shown(module['median_dominance_share'])} | {shown(module['share_of_nodes_dominated_above_0.5'])} | {shown(module['share_of_nodes_dominated_above_0.9'])} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--run-dirs", type=Path, nargs="+", required=True, help="fold directories, each with results.json and its checkpoint")
    parser.add_argument("--support-threshold", type=float, default=DEFAULT_SUPPORT_THRESHOLD, help="the expected gate at which a node counts as support")
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path)
    arguments = parser.parse_args()
    diagnoses = [diagnose_fold(directory, arguments.support_threshold) for directory in arguments.run_dirs]
    arguments.json_output.write_text(json.dumps(diagnoses, indent=2) + "\n")
    if arguments.markdown_output is not None:
        arguments.markdown_output.write_text(markdown(diagnoses))
    print(markdown(diagnoses))


if __name__ == "__main__":
    main()
