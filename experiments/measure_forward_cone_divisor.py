"""What the forward-cone divisor (decision 9.16) changes on a real graph, against item 28's total_in_degree.

For every perturbation of an evidence table, the encoder is built three times with the same parameters (one seed,
so the gains are the same draw) under total_in_degree, forward_cone_union and forward_cone, and the propagated
response is compared before the limiting-step bottleneck and the pH weight, which read the settled state the same
way under all three. Reported:

  - how much of the graph a seed's cone holds, and how often the cone divisor differs from total_in_degree at a row
    inside the cone (the ratio total / cone);
  - how the response changes: magnitude ratio and sign agreement where total_in_degree's response is nonzero, overall
    and by node type, and at the membrane potential node;
  - what it costs: seconds per batch of the propagation under each normalisation.

The model is the registered linear-response model's propagation (cofactor relations, reversible reactions, drug
entry nodes, edge weights) without cell-class weights or node descriptors, which this script does not need: the
cell-class weights act after the loop through the bottleneck, so they change neither the divisor nor the propagation
compared here. Untrained gains are used on purpose: the question is what the divisor does at fixed gains.

Usage:
  python experiments/measure_forward_cone_divisor.py --graph-dir data/processed/graph_full_neuronal_split_binders_drugs_v5 \
      --evidence-dir data/processed/evidence_full_v5 --output docs/forward_cone_divisor_measured.json
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data
from mechanistic_pathway_learning.graph.cofactor_edges import cofactor_edge_mask
from mechanistic_pathway_learning.graph.drug_entry_nodes import ENTRY_RELATIONS
from mechanistic_pathway_learning.models.linear_response_encoder import LinearResponseEncoder

NORMALISATIONS_COMPARED = ("total_in_degree", "forward_cone_union", "forward_cone")
MEMBRANE_POTENTIAL_NODE = "VM_c"
SAMPLE_PER_BATCH = 20_000


def pad(data, indices: np.ndarray) -> tuple[torch.Tensor, torch.Tensor]:
    """The trainer's pad_perturbations, repeated so this script does not import the trainer."""
    max_nodes = max(1, max(len(data.perturbation_seeds[i]) for i in indices))
    node_index = torch.full((len(indices), max_nodes), -1, dtype=torch.long)
    sign_and_magnitude = torch.zeros((len(indices), max_nodes, 2))
    for row, i in enumerate(indices):
        seeds = data.perturbation_seeds[i]
        node_index[row, : len(seeds)] = torch.as_tensor(seeds, dtype=torch.long)
        sign_and_magnitude[row, : len(seeds), 0] = torch.as_tensor(data.perturbation_signs[i], dtype=torch.float32)
        sign_and_magnitude[row, : len(seeds), 1] = torch.as_tensor(data.perturbation_magnitudes[i], dtype=torch.float32)
    return node_index, sign_and_magnitude


def build_encoder(data, normalisation: str, propagation_channels: int) -> LinearResponseEncoder:
    torch.manual_seed(0)
    cofactor_edges = torch.as_tensor(cofactor_edge_mask(data.edge_source, data.edge_target, data.edge_relation, data.relation_types,
                                                        data.node_base_metabolite_id, data.node_display_name, data.is_currency))
    distinct_node_types = sorted(set(data.node_types.tolist()))
    node_type_one_hot = torch.nn.functional.one_hot(
        torch.as_tensor([distinct_node_types.index(node_type) for node_type in data.node_types]), len(distinct_node_types)).float()
    entry_inputs = {} if data.edge_weight is None else {"edge_weight": torch.as_tensor(data.edge_weight)}
    if getattr(data, "entry_node_mask", None) is not None:
        entry_inputs.update(entry_relation_names=ENTRY_RELATIONS, entry_node_mask=torch.as_tensor(data.entry_node_mask))
    return LinearResponseEncoder(
        len(data.node_ids), data.relation_types, torch.as_tensor(data.edge_source), torch.as_tensor(data.edge_target),
        torch.as_tensor(data.edge_relation), torch.as_tensor(data.edge_sign), node_type_one_hot, node_state_dim=4,
        non_propagating_nodes=torch.as_tensor(data.is_currency), cofactor_edges=cofactor_edges,
        reversible_reactions=torch.as_tensor(data.is_reversible_reaction) if data.is_reversible_reaction is not None else None,
        fixed_point_tolerance=1e-3, propagation_channels=propagation_channels, normalisation=normalisation, **entry_inputs)


def quantiles(values: torch.Tensor) -> dict:
    if values.numel() == 0:
        return {"count": 0}
    values = values.double()
    return {"count": int(values.numel()), "median": float(values.median()), "p10": float(values.quantile(0.1)),
            "p90": float(values.quantile(0.9)), "maximum": float(values.max())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--propagation-channels", type=int, default=4)
    parser.add_argument("--max-perturbations", type=int, default=None, help="the first N perturbations only, for a quick reading")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    data = load_experiment_data(arguments.graph_dir, arguments.evidence_dir, group_by="disease_cluster_and_targets", drug_entry="nodes")
    all_rows = np.arange(len(data.perturbation_ids))
    if arguments.max_perturbations is not None:
        all_rows = all_rows[: arguments.max_perturbations]
    batches = [all_rows[start : start + arguments.batch_size] for start in range(0, len(all_rows), arguments.batch_size)]
    node_types = np.asarray(data.node_types)
    node_ids = list(data.node_ids)
    membrane_potential = node_ids.index(MEMBRANE_POTENTIAL_NODE) if MEMBRANE_POTENTIAL_NODE in node_ids else None

    # Summarised batch by batch: holding every perturbation's [N] response under three normalisations, and every row's
    # divisor ratio, does not fit in a few gigabytes, so the distributions are read from a fixed-seed sample of each
    # batch (SAMPLE_PER_BATCH values), and counts and per-perturbation figures are kept whole.
    generator = torch.Generator().manual_seed(0)

    def sample(values: torch.Tensor, size: int = SAMPLE_PER_BATCH) -> torch.Tensor:
        if values.numel() <= size:
            return values.reshape(-1)
        return values.reshape(-1)[torch.randperm(values.numel(), generator=generator)[:size]]

    encoders = {name: build_encoder(data, name, arguments.propagation_channels) for name in NORMALISATIONS_COMPARED}
    seconds: dict[str, list[float]] = {name: [] for name in NORMALISATIONS_COMPARED}
    cone_share_of_nodes, ratio_inside_cone_sample, columns_per_batch = [], [], []
    rows_inside_cone, rows_above = 0, 0
    distinct_types = sorted(set(node_types.tolist()))
    type_of_node = torch.as_tensor([distinct_types.index(node_type) for node_type in node_types])
    tallies = {name: {"live": 0, "sign_agreement": 0, "nonzero_only_here": 0, "ratio_sample": [], "by_type": {node_type: [] for node_type in distinct_types},
                      "at_VM_c": [], "norm_ratio_per_perturbation": []} for name in ("forward_cone_union", "forward_cone")}
    per_seed_over_union_sample = []
    for batch in batches:
        node_index, sign_and_magnitude = pad(data, batch)
        summed = {}
        with torch.no_grad():
            for name, encoder in encoders.items():
                start = time.perf_counter()
                response = encoder.response(node_index, sign_and_magnitude)  # [B, N, C]
                seconds[name].append(time.perf_counter() - start)
                # one number per node and perturbation: the response summed over channels, signed by channel 0's direction
                summed[name] = response.abs().sum(dim=-1) * torch.sign(response[..., 0])
            _, _, reached = encoders["forward_cone"].cone_columns(node_index, sign_and_magnitude)
            columns_per_batch.append(int(reached.shape[1]))
            cone_share_of_nodes.append(reached.float().mean(dim=0))
            ratio = encoders["forward_cone"].cone_row_ratio(reached)[:, :, 0]
            inside = ratio[reached[encoders["forward_cone"].row_target_index]]
            rows_inside_cone += int(inside.numel())
            rows_above += int((inside > 1.01).sum())
            ratio_inside_cone_sample.append(sample(inside))
        reference = summed["total_in_degree"]
        live = reference.abs() > 0
        for name, tally in tallies.items():
            changed = summed[name]
            tally["live"] += int(live.sum())
            tally["sign_agreement"] += int((torch.sign(changed) == torch.sign(reference))[live].sum())
            tally["nonzero_only_here"] += int(((changed.abs() > 0) & ~live).sum())
            magnitude_ratio = torch.where(live, changed.abs() / reference.abs().clamp_min(1e-30), torch.zeros_like(changed))
            tally["ratio_sample"].append(sample(magnitude_ratio[live]))
            for type_index, node_type in enumerate(distinct_types):
                type_live = live & (type_of_node == type_index)[None, :]
                tally["by_type"][node_type].append(sample(magnitude_ratio[type_live], SAMPLE_PER_BATCH // 4))
            if membrane_potential is not None:
                at_potential = live[:, membrane_potential]
                tally["at_VM_c"].append(magnitude_ratio[:, membrane_potential][at_potential])
            has_response = reference.norm(dim=1) > 0
            tally["norm_ratio_per_perturbation"].append((changed.norm(dim=1) / reference.norm(dim=1).clamp_min(1e-30))[has_response])
        per_seed_over_union_sample.append(sample(summed["forward_cone"].abs()[live] / summed["forward_cone_union"].abs()[live].clamp_min(1e-30)))
    for name in NORMALISATIONS_COMPARED:
        print(f"{name}: {np.median(seconds[name]):.2f} s a batch (median over {len(batches)})", flush=True)
    comparisons = {}
    for name, tally in tallies.items():
        comparisons[name] = {
            "magnitude_ratio_where_total_in_degree_is_nonzero (sampled)": quantiles(torch.cat(tally["ratio_sample"])),
            "sign_agreement": tally["sign_agreement"] / max(tally["live"], 1),
            "node_responses_compared": tally["live"],
            "nonzero_only_under_this_normalisation": tally["nonzero_only_here"],
            "response_norm_ratio_per_perturbation": quantiles(torch.cat(tally["norm_ratio_per_perturbation"])),
            "magnitude_ratio_by_node_type (sampled)": {node_type: quantiles(torch.cat(values)) for node_type, values in tally["by_type"].items()},
        }
        if membrane_potential is not None:
            comparisons[name]["magnitude_ratio_at_VM_c"] = quantiles(torch.cat(tally["at_VM_c"]))
    report = {
        "graph": str(arguments.graph_dir), "evidence": str(arguments.evidence_dir), "perturbations": int(len(all_rows)),
        "nodes": len(node_ids), "edges": int(len(data.edge_source)),
        "seeds_per_perturbation": quantiles(torch.as_tensor([len(data.perturbation_seeds[i]) for i in all_rows], dtype=torch.float64)),
        "perturbation_types": {kind: int(count) for kind, count in zip(*np.unique(np.asarray(data.perturbation_types)[all_rows], return_counts=True))},
        "columns_per_batch_under_forward_cone": quantiles(torch.as_tensor(columns_per_batch, dtype=torch.float64)),
        "share_of_nodes_in_a_seed_cone": quantiles(torch.cat(cone_share_of_nodes)),
        "total_over_cone_divisor_at_rows_inside_the_cone": {**quantiles(torch.cat(ratio_inside_cone_sample)), "sampled": True,
                                                             "rows_inside_the_cone": rows_inside_cone,
                                                             "share_above_1.01": rows_above / max(rows_inside_cone, 1)},
        "against_total_in_degree": comparisons,
        "per_seed_over_union_magnitude (sampled)": quantiles(torch.cat(per_seed_over_union_sample)),
        "seconds_per_batch": {name: quantiles(torch.as_tensor(values, dtype=torch.float64)) for name, values in seconds.items()},
        "batch_size": arguments.batch_size, "propagation_channels": arguments.propagation_channels, "sample_per_batch": SAMPLE_PER_BATCH,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "against_total_in_degree"}, indent=1))
    print(json.dumps(comparisons, indent=1))


if __name__ == "__main__":
    main()
