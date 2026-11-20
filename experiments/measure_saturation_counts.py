"""Decision 9.81's counts, taken before amendment item 37's saturation and root-finder are built (an engineering
measurement; nothing here interprets a count for a decision).

Why. The item 37 rulings draft (docs/item37_rulings_draft_2026-11-13.md, section 9) puts these before the saturation of
item 37's sub-item 37f is built: "9.81's four counts and a count of positive-feedback cycles on v5". The four are
decision 9.81's, from its Fable design review of 4 November 2026, which defers every saturation operator "until four
counts exist on the v5 rebuild of November 2026 (perturbations with more than one seed; per candidate operator, the
(perturbation, node) pairs at which it fires; the labelled contrasts that can separate a saturation in the field from
the head's; cones reaching a proton node)". The record is taken on the rebuild. A run on any other build is a record of
that build (CLAUDE.md, "A measurement carries the graph it was taken on"), so the output names the graph and evidence
directories, the SHA-256 of each file read, and the date.

What is counted:

1. **Seeds.** Perturbations with more than one seed, from the evidence table's perturbation_nodes and from the
   encoder's input under each drug_entry mode of load_experiment_data ("targets" seeds a drug on its targets, "nodes"
   on its own node, the trainer's default on a graph with drug entry nodes), with the histogram of seed counts. Under
   "nodes" the fan-out sits on the mechanism edges, so the number of targets edges per drug node is counted too.
2. **Firing.** Per candidate operator, the (perturbation, node) pairs at which it would fire, read on the settled
   linear state the loop returns (LinearResponseEncoder.response: before the limiting-step bottleneck and the pH
   weight, the state a saturation inside the loop would act on), under drug_entry "nodes". The operators are those of
   37f: the floor at -1 for every node (the rulings draft, section 9: "a floor at -1 for every node"), firing where
   the state is below -1, and the sourced upward headroom per node, firing where the state is above the node's
   headroom; a node without a headroom has no ceiling ("none where no ceiling exists"). Pairs are split into those at
   a seed, those at a direct mechanism target of a drug or allele seed, and those beyond both, since the review named
   the floor as a candidate amendment "if it fires beyond the seeds". The encoder is the registered propagation that
   experiments/measure_forward_cone_divisor.py builds (build_encoder: forward_cone, cofactor relations, reversible
   reactions, drug entry nodes, edge weights; no cell-class weights, edge gates or descriptors), one channel.
3. **Not counted: the labelled contrasts.** Neither 9.81 nor the rulings draft says which pair or set of labelled
   perturbations counts as a contrast (the same seeds at another signed magnitude, a gain against a loss of function, a
   combination against its parts), nor which label pattern within one is informative under the registered
   positive_unlabelled likelihood, where an outcome of 0 is unlabelled. So this script stops at it, and the definition is
   a question for the owner.
4. **Cones.** Forward cones reaching a proton node: one cone per seed under forward_cone (encoder.cone_columns), and
   whether it reaches any node named H+ (compartment_ph.PROTON_DISPLAY_NAME), a governing proton node of
   compartment_ph_inputs, and VM_c, with the cone sizes.
5. **Positive-feedback cycles.** Simple directed cycles of the signed graph by length and by the sign of their edge
   product, positive (an even number of negative edges) or negative, with those through VM_c, a voltage_gates edge, a
   drug node and each neuronal ion pool (a node whose id starts NEURON_) counted apart, and the strongly connected
   components the cycles lie in. A relation whose sign the gain carries (UNSIGNED_RELATIONS, binds) and an edge of sign 0
   have no sign to multiply, so they are left out, which the output says. Each simple cycle is counted once, from its
   smallest node index; one ordered pair holding edges of both signs gives two cycles. A self-loop is counted apart.
   Enumeration is exact up to the length bound and grows quickly with it.

What it leaves to the caller, because no ruling settles it, each a required argument with no default:

- **--gains**, the gains count 2 is read at: "init", the untrained draw of build_encoder (torch seed 0) with the loop
  as registered; or "fixed:G", every signed relation's gain and the entry gain set to G (below the encoder's
  contraction bound), and the unsigned relations' gains to 0. Which gains the record is taken at is the owner's.
- **--ceiling**, the headroom per node: the path of a table with columns node_id and headroom, a headroom being
  (maximum - rest) / rest, the rulings' form; or "none", which counts the floor alone. The headroom tables are
  item 37's [P 13] and are not sourced yet.
- **--cycle-edges**, the signed graph of count 5: "stored", the stored edges with currency nodes' outgoing edges dropped
  as the encoder drops them; or "encoder", the encoder's own entries (expanded_adjacency_entries: the derived
  depletes_substrate and product_opposes edges and the carrier relations, currency out-edges dropped).
- **--max-cycle-length**, the bound of the enumeration.

It changes nothing it reads and writes one JSON file, which it refuses to put under the repository's data/ directory.

Usage, from the repository root:
  PYTHONPATH=. python experiments/measure_saturation_counts.py --graph-dir <build directory> --evidence-dir <evidence> \\
      --gains init --ceiling none --cycle-edges stored --max-cycle-length 4 --output <path outside data/>
"""
from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = REPOSITORY_ROOT / "data"
MEMBRANE_POTENTIAL_NODE = "VM_c"
NEURONAL_POOL_PREFIX = "NEURON_"
VOLTAGE_GATES_RELATION = "voltage_gates"
CYCLE_EDGE_SETS = ("stored", "encoder")
DRUG_ENTRY_MODES = ("targets", "nodes")
FIRING_DRUG_ENTRY = "nodes"  # the trainer's default on a graph with drug entry nodes (experiments/run_main_model.py)
FLOOR = -1.0  # item 37 rulings draft, section 9: "a floor at -1 for every node"


# ---------------------------------------------------------------- count 1


def seed_count_summary(seed_counts: list[int], perturbation_types: list[str]) -> dict:
    """How many perturbations have more than one seed, by type, with the histogram of seed counts."""
    counts = np.asarray(seed_counts, dtype=np.int64)
    types = np.asarray(perturbation_types, dtype=object)
    if counts.shape != types.shape:
        raise ValueError("one seed count and one type per perturbation")
    return {"perturbations": int(counts.size), "more_than_one_seed": int((counts > 1).sum()),
            "more_than_one_seed_by_type": dict(sorted(collections.Counter(types[counts > 1].tolist()).items())),
            "by_type": dict(sorted(collections.Counter(types.tolist()).items())),
            "seed_count_histogram": {int(k): int(v) for k, v in sorted(collections.Counter(counts.tolist()).items())}}


# ---------------------------------------------------------------- count 2


def read_headroom_table(path: Path, node_ids: list[str]) -> dict[int, float]:
    """node index -> headroom, from a table with columns node_id and headroom (module docstring, --ceiling).

    Refuses a table without those columns, a node the graph does not hold, a node given twice, and a headroom that is
    not a positive finite number: a ceiling at or below rest would fire at rest."""
    table = pd.read_csv(path, dtype={"node_id": str})
    if not {"node_id", "headroom"} <= set(table.columns):
        raise ValueError(f"{path} needs the columns node_id and headroom, not {list(table.columns)}")
    index_of = {node_id: index for index, node_id in enumerate(node_ids)}
    headroom: dict[int, float] = {}
    for line_number, (node_id, value) in enumerate(zip(table.node_id, table.headroom), start=2):
        if node_id not in index_of:
            raise ValueError(f"{path} line {line_number}: {node_id!r} is not a node of the graph")
        if index_of[node_id] in headroom:
            raise ValueError(f"{path} line {line_number}: {node_id!r} is given twice")
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{path} line {line_number}: the headroom of {node_id!r} is {value}, not a positive number")
        headroom[index_of[node_id]] = value
    return headroom


def new_firing_tally() -> dict:
    return {"pairs": 0, "pairs_at_seeds": 0, "pairs_at_mechanism_targets": 0, "pairs_beyond_seeds_and_targets": 0,
            "perturbations_with_any": 0, "perturbations_with_any_beyond_seeds_and_targets": 0,
            "by_node_type_beyond_seeds_and_targets": collections.Counter(), "nodes_beyond_seeds_and_targets": collections.Counter(),
            "perturbations_firing_beyond_seeds_and_targets": []}


def tally_firing(tally: dict, fires: np.ndarray, seed_mask: np.ndarray, target_mask: np.ndarray, node_types: np.ndarray,
                 perturbation_ids: list[str]) -> None:
    """Add one batch's firing to tally. fires, seed_mask and target_mask are [batch, nodes] booleans; a pair at a seed
    counts as at a seed even when it is also a target, and target_mask is the direct mechanism targets of the seeds."""
    fires, seed_mask, target_mask = (np.asarray(array, dtype=bool) for array in (fires, seed_mask, target_mask))
    at_targets = fires & ~seed_mask & target_mask
    beyond = fires & ~seed_mask & ~target_mask
    tally["pairs"] += int(fires.sum())
    tally["pairs_at_seeds"] += int((fires & seed_mask).sum())
    tally["pairs_at_mechanism_targets"] += int(at_targets.sum())
    tally["pairs_beyond_seeds_and_targets"] += int(beyond.sum())
    tally["perturbations_with_any"] += int(fires.any(axis=1).sum())
    tally["perturbations_with_any_beyond_seeds_and_targets"] += int(beyond.any(axis=1).sum())
    rows, columns = beyond.nonzero()
    tally["by_node_type_beyond_seeds_and_targets"].update(np.asarray(node_types)[columns].tolist())
    tally["nodes_beyond_seeds_and_targets"].update(columns.tolist())
    for row in np.flatnonzero(beyond.any(axis=1)):
        tally["perturbations_firing_beyond_seeds_and_targets"].append([perturbation_ids[row], int(beyond[row].sum())])


def operator_firing(state: np.ndarray, headroom: dict[int, float] | None) -> dict[str, np.ndarray]:
    """operator name -> [batch, nodes] booleans: the floor where the state is below FLOOR, and, with a headroom table,
    the ceiling where the state is above the node's headroom (a node the table does not name has none)."""
    state = np.asarray(state, dtype=float)
    fired = {"floor": state < FLOOR}
    if headroom is not None:
        ceiling = np.full(state.shape[1], np.inf)
        for node, value in headroom.items():
            ceiling[node] = value
        fired["ceiling"] = state > ceiling[None, :]
    return fired


def finished_tally(tally: dict, node_ids: list[str]) -> dict:
    result = {key: value for key, value in tally.items() if key not in ("by_node_type_beyond_seeds_and_targets", "nodes_beyond_seeds_and_targets")}
    result["by_node_type_beyond_seeds_and_targets"] = dict(sorted(tally["by_node_type_beyond_seeds_and_targets"].items()))
    result["distinct_nodes_beyond_seeds_and_targets"] = len(tally["nodes_beyond_seeds_and_targets"])
    result["most_frequent_nodes_beyond_seeds_and_targets"] = [[node_ids[node], count] for node, count in tally["nodes_beyond_seeds_and_targets"].most_common(12)]
    return result


# ---------------------------------------------------------------- count 4


def reduce_cone_batch(reached: np.ndarray, node_sets: dict[str, list[int]]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """For [nodes, columns] booleans (the nodes each seed's cone holds): each column's cone size, and per node set
    whether each column reaches any node of it. A batch is reduced as it comes, so no [nodes, columns] matrix of the
    whole table is kept."""
    reached = np.asarray(reached, dtype=bool)
    reaches = {name: reached[list(nodes)].any(axis=0) if len(nodes) else np.zeros(reached.shape[1], dtype=bool) for name, nodes in node_sets.items()}
    return reached.sum(axis=0), reaches


def cone_summary(sizes: np.ndarray, reaches: dict[str, np.ndarray], column_types: list[str], node_sets: dict[str, list[int]], graph_nodes: int) -> dict:
    """How many columns reach any node of each set, overall and by the column's perturbation type, with the cone sizes."""
    sizes = np.asarray(sizes)
    types = np.asarray(column_types, dtype=object)
    summary: dict = {"columns": int(sizes.size), "graph_nodes": int(graph_nodes), "by_perturbation_type": {}}
    for name, nodes in node_sets.items():
        reach = np.asarray(reaches[name], dtype=bool)
        summary[f"reach_{name}"] = int(reach.sum())
        summary[f"nodes_in_{name}"] = len(nodes)
        for perturbation_type in sorted(set(types.tolist())):
            by_type = summary["by_perturbation_type"].setdefault(perturbation_type, {"columns": int((types == perturbation_type).sum())})
            by_type[f"reach_{name}"] = int((reach & (types == perturbation_type)).sum())
    if sizes.size:
        summary["cone_size"] = {"median": float(np.median(sizes)), "p10": float(np.quantile(sizes, 0.1)), "p90": float(np.quantile(sizes, 0.9)),
                                "minimum": int(sizes.min()), "maximum": int(sizes.max())}
    return summary


def cone_reach_summary(reached: np.ndarray, column_types: list[str], node_sets: dict[str, list[int]]) -> dict:
    """cone_summary of one [nodes, columns] matrix."""
    sizes, reaches = reduce_cone_batch(reached, node_sets)
    return cone_summary(sizes, reaches, column_types, node_sets, np.asarray(reached).shape[0])


# ---------------------------------------------------------------- count 5


def signed_cycle_counts(num_nodes: int, source, target, sign, max_length: int, node_flags: dict[str, list[int]] | None = None,
                        edge_flags: dict[str, np.ndarray] | None = None) -> dict:
    """Simple directed cycles of length 2 to max_length by the sign of their edge product (module docstring, count 5).

    source, target and sign are one value per edge; sign must be +1 or -1 (an edge without a sign has no place in a
    sign product). node_flags names node sets and edge_flags boolean masks over the edges; a cycle through any node of a
    set, or along any flagged edge, is also counted under that name. Edges repeating an ordered pair and a sign are one
    edge, flagged if any of them is; a pair with both signs is two edges, so two cycles. A self-loop is counted apart,
    as a cycle of length 1. Exact, by depth-first search from each node through nodes of larger index inside its
    strongly connected component."""
    import scipy.sparse as sparse
    from scipy.sparse.csgraph import connected_components

    if max_length < 2:
        raise ValueError("max_length is at least 2")
    source, target = np.asarray(source, dtype=np.int64), np.asarray(target, dtype=np.int64)
    sign = np.asarray(sign, dtype=float)
    if not (source.shape == target.shape == sign.shape):
        raise ValueError("one source, target and sign per edge")
    if len(sign) and not np.isin(sign, (-1.0, 1.0)).all():
        raise ValueError("every edge sign is +1 or -1")
    node_flags = node_flags or {}
    edge_flags = edge_flags or {}
    names = list(node_flags) + list(edge_flags)
    node_bits = np.zeros(num_nodes, dtype=np.int64)
    for bit, nodes in enumerate(node_flags.values()):
        node_bits[list(nodes)] |= 1 << bit

    frame = pd.DataFrame({"u": source, "v": target, "s": sign.astype(np.int8)})
    flag_columns = [f"flag_{offset}" for offset in range(len(edge_flags))]
    for column, mask in zip(flag_columns, edge_flags.values()):
        frame[column] = np.asarray(mask, dtype=bool)
    if flag_columns:  # an edge repeating a pair and a sign is flagged if any of its copies is
        distinct = frame.groupby(["u", "v", "s"], sort=True, as_index=False)[flag_columns].max()
    else:
        distinct = frame.drop_duplicates(["u", "v", "s"]).sort_values(["u", "v", "s"]).reset_index(drop=True)
    distinct["b"] = np.zeros(len(distinct), dtype=np.int64)
    for offset, column in enumerate(flag_columns, start=len(node_flags)):
        distinct["b"] |= distinct[column].to_numpy(dtype=np.int64) << offset
    loops = distinct[distinct.u == distinct.v]
    distinct = distinct[distinct.u != distinct.v]
    both_signs = int((distinct.groupby(["u", "v"]).s.nunique() > 1).sum())

    result: dict = {"edges_given": int(len(sign)), "distinct_signed_edges": int(len(distinct)), "ordered_pairs_with_both_signs": both_signs,
                    "self_loops": {"positive": int((loops.s > 0).sum()), "negative": int((loops.s < 0).sum())}, "max_length": int(max_length),
                    "by_length": {}}
    matrix = sparse.csr_matrix((np.ones(len(distinct)), (distinct.u.to_numpy(), distinct.v.to_numpy())), shape=(num_nodes, num_nodes))
    _, label = connected_components(matrix, directed=True, connection="strong")
    sizes = np.bincount(label, minlength=1)
    result["strongly_connected_components"] = {"components": int(len(sizes)), "nontrivial": int((sizes > 1).sum()),
                                               "largest": int(sizes.max()) if len(sizes) else 0,
                                               "nontrivial_size_histogram": {int(k): int(v) for k, v in sorted(collections.Counter(sizes[sizes > 1].tolist()).items())}}
    inside = label[distinct.u.to_numpy()] == label[distinct.v.to_numpy()]
    distinct = distinct[inside]
    neighbours: list[list[tuple[int, int, int]]] = [[] for _ in range(num_nodes)]
    for u, v, s, bits in zip(distinct.u.tolist(), distinct.v.tolist(), distinct.s.tolist(), distinct.b.tolist()):
        neighbours[u].append((v, s, bits))
    keys = [[entry[0] for entry in row] for row in neighbours]  # sorted by v, from the groupby

    counts = np.zeros((max_length + 1, 2), dtype=np.int64)  # [length, positive?]
    flagged = np.zeros((max_length + 1, 2, max(1, len(names))), dtype=np.int64)
    node_bits_list = node_bits.tolist()
    for start in np.flatnonzero(sizes[label] > 1).tolist():
        on_path = {start}
        # stack frames: (node, position in its neighbour list, path sign, path bits, depth)
        stack = [(start, bisect.bisect_left(keys[start], start + 1), 1, node_bits_list[start], 0)]
        while stack:
            node, position, path_sign, path_bits, depth = stack.pop()
            row = neighbours[node]
            if position < len(row):
                stack.append((node, position + 1, path_sign, path_bits, depth))
                next_node, edge_sign, bits = row[position]
                if next_node == start:
                    continue
                # an edge back to start is skipped here and counted once, when its node is left (below)
                if next_node not in on_path and depth + 1 < max_length:
                    on_path.add(next_node)
                    stack.append((next_node, bisect.bisect_left(keys[next_node], start), path_sign * edge_sign,
                                  path_bits | bits | node_bits_list[next_node], depth + 1))
                continue
            # every neighbour of node has been tried: close the cycles back to start, then leave node
            if depth >= 1:
                closing = bisect.bisect_left(keys[node], start)
                while closing < len(row) and row[closing][0] == start:
                    _, edge_sign, bits = row[closing]
                    length = depth + 1
                    positive = 1 if path_sign * edge_sign > 0 else 0
                    counts[length, positive] += 1
                    mask = path_bits | bits
                    if mask:
                        for bit in range(len(names)):
                            if (mask >> bit) & 1:
                                flagged[length, positive, bit] += 1
                    closing += 1
            on_path.discard(node)
    for length in range(2, max_length + 1):
        entry = {"positive": int(counts[length, 1]), "negative": int(counts[length, 0])}
        for bit, name in enumerate(names):
            entry[f"positive_through_{name}"] = int(flagged[length, 1, bit])
            entry[f"negative_through_{name}"] = int(flagged[length, 0, bit])
        result["by_length"][length] = entry
    return result


def signed_edges(edges: pd.DataFrame, relation_names: list[str], unsigned_relations: tuple[str, ...], non_propagating: np.ndarray) -> tuple[pd.DataFrame, dict]:
    """The edges count 5 multiplies signs along: integer source, target, relation and sign rows, with the relations
    whose sign the gain carries, edges of sign 0 and the outgoing edges of non-propagating nodes left out, and how many
    of each were left out."""
    relation = np.asarray(relation_names, dtype=object)[edges.relation.to_numpy()]
    unsigned = np.isin(relation, list(unsigned_relations))
    zero = edges.sign.to_numpy() == 0
    silent = np.asarray(non_propagating, dtype=bool)[edges.source.to_numpy()]
    keep = ~unsigned & ~zero & ~silent
    left_out = {"edges_of_unsigned_relations": int((unsigned & ~silent).sum()), "edges_of_sign_0": int((zero & ~unsigned & ~silent).sum()),
                "edges_from_non_propagating_nodes": int(silent.sum())}
    kept = edges[keep].copy()
    kept["sign"] = np.sign(kept.sign.to_numpy())
    kept["relation_name"] = relation[keep]
    return kept, left_out


# ---------------------------------------------------------------- the run


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def refuse_output_under_data(output: Path) -> None:
    """This script writes nothing into data/ (module docstring): refused under the repository's data/ as written, as
    resolved, and under the target of any link inside it (a worktree links data/raw and data/processed to the main
    checkout's)."""
    roots = {Path(os.path.abspath(DATA_DIRECTORY)), DATA_DIRECTORY.resolve()}
    if DATA_DIRECTORY.is_dir():
        roots |= {child.resolve() for child in DATA_DIRECTORY.iterdir() if child.is_symlink()}
    for path in {Path(os.path.abspath(output)), Path(output).resolve()}:
        if any(path == root or root in path.parents for root in roots):
            raise ValueError(f"{output} is under {DATA_DIRECTORY}; the counts are written outside data/")


def parse_gains(text: str) -> tuple[str, float | None]:
    if text == "init":
        return "init", None
    if text.startswith("fixed:"):
        value = float(text.removeprefix("fixed:"))
        if not 0.0 < value < 1.0:
            raise argparse.ArgumentTypeError(f"fixed gain {value} is not between 0 and 1")
        return "fixed", value
    raise argparse.ArgumentTypeError(f"--gains is init or fixed:G, not {text!r}")


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--gains", type=parse_gains, required=True, help="init or fixed:G (module docstring); no default, the choice is the owner's")
    parser.add_argument("--ceiling", required=True, help="a headroom table (node_id, headroom) or none (module docstring); no default")
    parser.add_argument("--cycle-edges", choices=CYCLE_EDGE_SETS, required=True, help="the signed graph of the cycle count; no default")
    parser.add_argument("--max-cycle-length", type=int, required=True, help="the bound of the cycle enumeration; no default")
    parser.add_argument("--batch-size", type=int, default=64, help="perturbations per propagation batch (memory only)")
    parser.add_argument("--max-rounds", type=int, default=None, help="override the encoder's registered round limit (the output records it)")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    if arguments.max_cycle_length < 2:
        parser.error("--max-cycle-length is at least 2")
    return arguments


def main(argv: list[str] | None = None) -> None:
    import torch

    from experiments.measure_forward_cone_divisor import build_encoder, pad
    from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data
    from mechanistic_pathway_learning.graph.compartment_ph import PROTON_DISPLAY_NAME, compartment_ph_inputs
    from mechanistic_pathway_learning.graph.drug_entry_nodes import DRUG_NODE_TYPE
    from mechanistic_pathway_learning.models.linear_response_encoder import UNSIGNED_RELATIONS, LinearResponseEncoder

    arguments = parse_arguments(argv)
    refuse_output_under_data(arguments.output)
    started = time.time()
    record: dict = {"what": "decision 9.81's counts 1, 2 and 4 and the positive-feedback cycles (experiments/measure_saturation_counts.py); count 3 not taken",
                    "date": time.strftime("%Y-%m-%d"), "graph_dir": str(arguments.graph_dir), "evidence_dir": str(arguments.evidence_dir),
                    "inputs_sha256": {}, "choices": {"gains": list(arguments.gains), "ceiling": arguments.ceiling, "cycle_edges": arguments.cycle_edges,
                                                     "max_cycle_length": arguments.max_cycle_length}}
    for path in sorted(list(arguments.graph_dir.glob("*.parquet")) + list(arguments.evidence_dir.glob("evidence_records.parquet"))):
        record["inputs_sha256"][str(path)] = sha256_of(path)

    # count 1
    evidence = pd.read_parquet(arguments.evidence_dir / "evidence_records.parquet", columns=["perturbation_id", "perturbation_type", "perturbation_nodes"])
    first = evidence.drop_duplicates("perturbation_id")
    record["count1_seeds"] = {"evidence_table": seed_count_summary([len(json.loads(text)) for text in first.perturbation_nodes], first.perturbation_type.tolist())}
    data = None
    for mode in DRUG_ENTRY_MODES:
        loaded = load_experiment_data(arguments.graph_dir, arguments.evidence_dir, group_by="disease_cluster_and_targets", drug_entry=mode)
        record["count1_seeds"][f"encoder_input_drug_entry_{mode}"] = seed_count_summary([len(seeds) for seeds in loaded.perturbation_seeds], list(loaded.perturbation_types))
        if mode == FIRING_DRUG_ENTRY:
            data = loaded
    node_ids = list(data.node_ids)
    node_types = np.asarray(data.node_types, dtype=object)
    encoder = build_encoder(data, "forward_cone", propagation_channels=1)
    if encoder.entry_edge_source is not None:
        fan_out = collections.Counter(encoder.entry_edge_source.tolist())
        drug_nodes = [int(seeds[0]) for seeds, kind in zip(data.perturbation_seeds, data.perturbation_types) if kind == DRUG_NODE_TYPE and len(seeds)]
        per_drug = [fan_out.get(node, 0) for node in drug_nodes]
        record["count1_seeds"]["mechanism_edges_per_drug_node"] = {"drug_nodes": len(per_drug), "more_than_one": int(sum(count > 1 for count in per_drug)),
                                                                   "histogram": {int(k): int(v) for k, v in sorted(collections.Counter(per_drug).items())}}

    # count 2: the gains, then the loop
    gains_kind, gain = arguments.gains
    if gains_kind == "fixed":
        if gain >= encoder.maximum_gain:
            raise ValueError(f"fixed gain {gain} is not below the encoder's contraction bound {encoder.maximum_gain}")
        with torch.no_grad():
            encoder.gain_logit.fill_(math.log(gain / (encoder.maximum_gain - gain)))
            if encoder.gain_logit.shape[0] == len(encoder.relation_names):
                encoder.gain_logit[encoder.relation_is_unsigned] = 0.0
            if encoder.entry_gain_logit is not None:
                encoder.entry_gain_logit.fill_(math.log(gain / (1.0 - gain)))
    if arguments.max_rounds is not None:
        encoder.max_propagation_steps = arguments.max_rounds
    headroom = None if arguments.ceiling == "none" else read_headroom_table(Path(arguments.ceiling), node_ids)
    tallies: dict[str, dict] = {}
    rounds_taken: list[int] = []
    extremes = [math.inf, -math.inf]
    proton_nodes = [index for index, name in enumerate(data.node_display_name) if str(name).strip() == PROTON_DISPLAY_NAME]
    governing = [int(index) for index in compartment_ph_inputs(data).get("ph_proton_node_index", [])]
    node_sets = {"any_proton_node": proton_nodes, "a_governing_proton_node": governing,
                 MEMBRANE_POTENTIAL_NODE: [node_ids.index(MEMBRANE_POTENTIAL_NODE)] if MEMBRANE_POTENTIAL_NODE in node_ids else []}
    cone_sizes: list[np.ndarray] = []
    cone_reaches: dict[str, list[np.ndarray]] = {name: [] for name in node_sets}
    cone_types: list[str] = []
    rows = np.arange(len(data.perturbation_ids))
    for start in range(0, len(rows), arguments.batch_size):
        batch = rows[start:start + arguments.batch_size]
        index, sign_and_magnitude = pad(data, batch)
        with torch.no_grad():
            _, column_perturbation, reached = encoder.cone_columns(index, sign_and_magnitude)
            state = encoder.response(index, sign_and_magnitude)[:, :, 0].numpy()
        encoder.clear_cone_reach_cache()
        rounds_taken.append(int(encoder.propagation_steps_taken))
        sizes, reaches = reduce_cone_batch(reached.numpy(), node_sets)
        cone_sizes.append(sizes)
        for name, reach in reaches.items():
            cone_reaches[name].append(reach)
        cone_types.extend(data.perturbation_types[batch[position]] for position in column_perturbation.tolist())
        extremes = [min(extremes[0], float(state.min())), max(extremes[1], float(state.max()))]
        seed_mask = np.zeros(state.shape, dtype=bool)
        target_mask = np.zeros(state.shape, dtype=bool)
        for row, perturbation in enumerate(batch):
            seeds = list(data.perturbation_seeds[perturbation])
            seed_mask[row, seeds] = True
            if encoder.entry_edge_source is not None:
                for seed in seeds:
                    target_mask[row, encoder.entry_edge_target[encoder.entry_edge_source == int(seed)].numpy()] = True
        ids = [data.perturbation_ids[perturbation] for perturbation in batch]
        for name, fires in operator_firing(state, headroom).items():
            tally_firing(tallies.setdefault(name, new_firing_tally()), fires, seed_mask, target_mask, node_types, ids)
    record["count2_firing"] = {"drug_entry": FIRING_DRUG_ENTRY, "perturbations": int(len(rows)), "pairs_total": int(len(rows) * len(node_ids)),
                               "relation_gains": {name: round(float(value), 6) for name, value in zip(encoder.relation_names, encoder.relation_gain().detach()[:, 0])},
                               "entry_gains": [] if encoder.entry_gain_logit is None else [round(float(value), 6) for value in torch.sigmoid(encoder.entry_gain_logit.detach()[:, 0])],
                               "input_weight": [round(float(value), 6) for value in encoder.injection_weights().detach()],
                               "loop": {"damping": float(encoder.damping), "tolerance": encoder.fixed_point_tolerance, "max_rounds": int(encoder.max_propagation_steps),
                                        "rounds_taken_per_batch": {"minimum": min(rounds_taken), "maximum": max(rounds_taken)},
                                        "every_batch_settled": bool(max(rounds_taken) < encoder.max_propagation_steps)},
                               "state_minimum": extremes[0], "state_maximum": extremes[1],
                               "headroom_nodes": 0 if headroom is None else len(headroom),
                               "operators": {name: finished_tally(tally, node_ids) for name, tally in tallies.items()}}
    record["count3_labelled_contrasts"] = "not taken: neither decision 9.81 nor the item 37 rulings draft defines the contrast (module docstring, count 3)"
    record["count4_cones"] = cone_summary(np.concatenate(cone_sizes), {name: np.concatenate(parts) for name, parts in cone_reaches.items()},
                                          cone_types, node_sets, len(node_ids))

    # count 5
    if arguments.cycle_edges == "stored":
        relation_names = list(data.relation_types)
        edges = pd.DataFrame({"source": np.asarray(data.edge_source), "target": np.asarray(data.edge_target),
                              "relation": np.asarray(data.edge_relation), "sign": np.asarray(data.edge_sign, dtype=float)})
    else:
        from mechanistic_pathway_learning.graph.cofactor_edges import cofactor_edge_mask

        cofactor = torch.as_tensor(cofactor_edge_mask(data.edge_source, data.edge_target, data.edge_relation, data.relation_types,
                                                      data.node_base_metabolite_id, data.node_display_name, data.is_currency))
        entries = LinearResponseEncoder.expanded_adjacency_entries(
            len(node_ids), data.relation_types, torch.as_tensor(data.edge_source), torch.as_tensor(data.edge_target), torch.as_tensor(data.edge_relation),
            torch.as_tensor(data.edge_sign), torch.as_tensor(data.is_currency), cofactor,
            reversible_reactions=torch.as_tensor(data.is_reversible_reaction) if data.is_reversible_reaction is not None else None)
        relation_names = list(entries["relation_names"])
        sign = entries["sign"].numpy().astype(float)
        relation = entries["relation"].numpy()
        # expanded_adjacency_entries writes +1 on an unsigned relation's entries (the gain carries the sign); signed_edges leaves them out
        edges = pd.DataFrame({"source": entries["source"].numpy(), "target": entries["target"].numpy(), "relation": relation, "sign": sign})
    kept, left_out = signed_edges(edges, relation_names, UNSIGNED_RELATIONS, np.asarray(data.is_currency, dtype=bool))
    drug_nodes = [index for index, kind in enumerate(node_types) if kind == DRUG_NODE_TYPE]
    pools = {node_id: [index] for index, node_id in enumerate(node_ids) if str(node_id).startswith(NEURONAL_POOL_PREFIX)}
    cycles = signed_cycle_counts(len(node_ids), kept.source.to_numpy(), kept.target.to_numpy(), kept.sign.to_numpy(), arguments.max_cycle_length,
                                 node_flags={MEMBRANE_POTENTIAL_NODE: node_sets[MEMBRANE_POTENTIAL_NODE], "a_drug_node": drug_nodes, **pools},
                                 edge_flags={"a_voltage_gates_edge": (kept.relation_name == VOLTAGE_GATES_RELATION).to_numpy()})
    record["count5_positive_feedback_cycles"] = {"edge_set": arguments.cycle_edges, "left_out": left_out, **cycles}
    record["seconds"] = round(time.time() - started, 1)
    arguments.output.write_text(json.dumps(record, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({key: record[key] for key in ("date", "graph_dir", "choices", "seconds")}, indent=1))


if __name__ == "__main__":
    main()
