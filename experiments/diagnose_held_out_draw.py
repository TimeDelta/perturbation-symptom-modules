"""Label-free diagnostics of the held-out draw under the rule as it stands and under its draft options (built 28 November
2026; target_held_out_split.HeldOutDrawOptions, from docs/drafts/held_out_draw_methods_2026-11-28.md, M1 and M2, none
ruled).

What it writes. For a graph directory, an evidence table, one or more groupings, a list of seeds and a fraction, one
JSON file. Per grouping, a population block: how many perturbations, drugs and gene-side perturbations (every
perturbation that is not a drug) there are, the gene side's groups and its largest, and the most-shared target's share
of the drugs, with whether it is above twice the fraction, past which a seed whose order starts with that target draws
an empty drug side (held_out_targets' docstring). Then per seed and per rule of RULES (the rule as it stands; M2; M1
with M2; the identity option alone), the numbers of diagnose_one_draw:

- the drug side's size and the number of held-out targets;
- the gene side's size, its share of every gene-side perturbation and its number of groups;
- the largest group's size and share, how many of its members are on the gene side and whether all are;
- the channel-2 count: held-out targets whose gene's perturbation trains (a perturbation that is not a drug, in
  training, whose seed is the target or, on a split graph, encodes it);
- M1's forced groups: their count, their gene-side size and share, whether they pass the fraction and the overshoot
  (zero, and empty, under a rule without M1's closure);
- the number of leakage groups with members on both sides, which experiment_data.read_lockbox refuses.

Across seeds, per rule, the pairwise Jaccard index of the gene sides (1 for two empty sides), which shows whether a rule
draws the same block under every seed.

What it reads, and what it never reads. It reads no symptom label, and that is structural: load_draw_inputs asks
pandas for the columns of DRAW_INPUT_COLUMNS and ROW_FILTER_COLUMNS of evidence_records.parquet and no others (never
symptom, weight, label_frequency or any other per-symptom value), the node_id and node_type columns of the graph's
nodes.parquet, and the graph's gene_to_protein.parquet, and it returns DrawInputs, which has no field an outcome could
go in (tests/test_diagnose_held_out_draw.py checks the columns asked for and runs it on a table that holds none of the
others). ROW_FILTER_COLUMNS (relation, positive_report_count, grade) are read only to keep the perturbations
experiment_data.load_experiment_data keeps under its defaults (relation "induces", a positive report, grade A or B):
without them the population would hold perturbations the draw never sees.

It interprets nothing. What the numbers say for a choice between the rules is the owner's, and reading a measurement
towards a decision is research (CLAUDE.md, Models). --provenance is a sentence naming the graph the numbers were taken
on and the date (CLAUDE.md, Modelling: "A measurement carries the graph it was taken on"), written at the top of the file.

Usage, from the repository root:
  PYTHONPATH=. python experiments/diagnose_held_out_draw.py --graph-dir <graph> --evidence-dir <evidence> \\
      --group-by disease_cluster disease_cluster_and_targets gene --seeds 0 1 2 --provenance "<graph, built, measured>" \\
      --output <diagnostics.json>
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as parquet

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mechanistic_pathway_learning.data_release import sha256_of_file  # noqa: E402
from mechanistic_pathway_learning.evaluation.experiment_data import (  # noqa: E402
    DEFAULT_LABEL_GRADES, GROUPING_COLUMNS, drug_seeds_on_proteins, merge_drugs_with_their_targets, read_protein_of_gene,
    read_proteins_encoded_by_gene)
from mechanistic_pathway_learning.evaluation.target_held_out_split import (  # noqa: E402
    REGISTERED_HELD_OUT_FRACTION, HeldOutDrawOptions, targets_of_drugs, two_sided_held_out_draw)
from mechanistic_pathway_learning.evidence.combined_perturbations import PARTS_COLUMN, read_parts  # noqa: E402
from mechanistic_pathway_learning.graph.drug_entry_nodes import DRUG_ENTRY_FILE, ENTRY_NODE_TYPES  # noqa: E402
from measure_leakage_only_adversary import graph_file_sha256  # noqa: E402

# The evidence columns the draw's inputs are built from: who each perturbation is, what kind, what it seeds, and its
# groups. PARTS_COLUMN is read too when the table has it (a combination's parts), and the grouping's own column.
DRAW_INPUT_COLUMNS = ("perturbation_id", "perturbation_type", "perturbation_nodes", "group_id")
# Read only to keep the perturbations load_experiment_data keeps under its defaults; relation is required, the two
# others are filtered on when present, as the loader does.
ROW_FILTER_COLUMNS = ("relation", "positive_report_count", "grade")
LOADED_RELATION = "induces"  # load_experiment_data's default relation
NODE_COLUMNS = ("node_id", "node_type")

RULES = {
    "rule_as_it_stands": HeldOutDrawOptions(),
    "m2_seeded_group_prefix": HeldOutDrawOptions(gene_side_rule="seeded_group_prefix"),
    "m1_with_m2": HeldOutDrawOptions(hold_out_genes_encoding_held_out_targets=True, hold_out_whole_groups_of_those_genes=True,
                                     gene_side_rule="seeded_group_prefix"),
    "identity_option_alone": HeldOutDrawOptions(hold_out_genes_encoding_held_out_targets=True),
}


@dataclass(frozen=True)
class DrawInputs:
    """What the held-out draw reads, and nothing else: no outcome, weight or symptom."""

    perturbation_ids: list[str]
    perturbation_types: list[str]
    perturbation_seeds: list[np.ndarray]  # node indices, as load_experiment_data seeds them under drug_entry "targets"
    node_ids: list[str]
    group_ids: list[str]
    proteins_encoded_by_gene: dict[str, set[str]]  # empty on a merged graph
    columns_read: dict[str, list[str]]


def evidence_columns_to_read(evidence_path: Path, group_by: str) -> tuple[list[str], str]:
    """The columns load_draw_inputs asks for, and the grouping's column (group_id on a table written before disease
    clusters existed, as load_experiment_data falls back to)."""
    present = set(parquet.read_schema(evidence_path).names)
    group_column = GROUPING_COLUMNS[group_by] if GROUPING_COLUMNS[group_by] in present else "group_id"
    if "relation" not in present:
        raise ValueError(f"{evidence_path} has no relation column, which load_experiment_data filters on")
    columns = [column for column in DRAW_INPUT_COLUMNS if column in present]
    columns += [column for column in (group_column, PARTS_COLUMN) if column in present and column not in columns]
    columns += [column for column in ROW_FILTER_COLUMNS if column in present]
    return columns, group_column


def load_draw_inputs(graph_directory: Path, evidence_directory: Path, group_by: str) -> DrawInputs:
    """The draw's inputs as load_experiment_data builds them under its defaults (relation "induces", label grades A and
    B, drug_entry "targets", no combination file), from the label-free columns alone. tests/test_diagnose_held_out_draw.py
    checks they equal the loader's own on fixture tables."""
    if group_by not in GROUPING_COLUMNS:
        raise ValueError(f"group_by must be one of {sorted(GROUPING_COLUMNS)}")
    graph_directory, evidence_directory = Path(graph_directory), Path(evidence_directory)
    nodes = pd.read_parquet(graph_directory / "nodes.parquet", columns=list(NODE_COLUMNS))
    if (graph_directory / DRUG_ENTRY_FILE).exists():  # drug_entry "targets" drops the entry nodes
        nodes = nodes[~nodes.node_type.isin(ENTRY_NODE_TYPES)].reset_index(drop=True)
    node_ids = [str(node_id) for node_id in nodes.node_id]
    node_index = {node_id: position for position, node_id in enumerate(node_ids)}
    protein_of_gene = read_protein_of_gene(graph_directory)

    evidence_path = evidence_directory / "evidence_records.parquet"
    columns, group_column = evidence_columns_to_read(evidence_path, group_by)
    evidence = pd.read_parquet(evidence_path, columns=columns)
    evidence = evidence[evidence.relation == LOADED_RELATION]
    if "positive_report_count" in evidence.columns:
        evidence = evidence[evidence.positive_report_count > 0]
    if "grade" in evidence.columns:
        evidence = evidence[evidence.grade.isin(DEFAULT_LABEL_GRADES)]

    types, groups, seeds, group_seeds, parts = {}, {}, {}, {}, {}
    for row in evidence.itertuples(index=False):
        perturbation_id = row.perturbation_id
        types[perturbation_id] = row.perturbation_type  # the last row's, as in load_experiment_data
        groups[perturbation_id] = getattr(row, group_column)
        if perturbation_id in seeds:
            continue
        parts[perturbation_id] = row_parts = read_parts(perturbation_id, row.perturbation_type, row.perturbation_nodes,
                                                        getattr(row, PARTS_COLUMN, None))
        group_triples, target_triples = [], []
        for part in row_parts:
            part_triples = [[node_id, sign, magnitude] for node_id, sign, magnitude in part.nodes if node_id in node_index]
            group_triples += part_triples
            if protein_of_gene and part.part_kind == "drug":  # split graph: a drug seeds its targets' proteins
                part_triples = drug_seeds_on_proteins(part_triples, protein_of_gene)
            target_triples += part_triples
        seeds[perturbation_id] = np.array([node_index[node_id] for node_id, _, _ in target_triples], dtype=int)
        group_seeds[perturbation_id] = np.array([node_index[node_id] for node_id, _, _ in group_triples], dtype=int)
    perturbation_ids = sorted(seeds)
    group_ids = [groups[perturbation_id] for perturbation_id in perturbation_ids]
    if group_by == "disease_cluster_and_targets":
        group_ids = merge_drugs_with_their_targets(perturbation_ids, [types[p] for p in perturbation_ids], group_ids,
                                                   [group_seeds[p] for p in perturbation_ids], node_ids,
                                                   [parts[p] for p in perturbation_ids])
    return DrawInputs(perturbation_ids=[str(p) for p in perturbation_ids], perturbation_types=[types[p] for p in perturbation_ids],
                      perturbation_seeds=[seeds[p] for p in perturbation_ids], node_ids=node_ids,
                      group_ids=[str(group) for group in group_ids],
                      proteins_encoded_by_gene=read_proteins_encoded_by_gene(graph_directory),
                      columns_read={"evidence_records.parquet": columns, "nodes.parquet": list(NODE_COLUMNS)})


def gene_side_count_of_group(inputs: DrawInputs) -> Counter:
    """group -> its number of perturbations that are not drugs."""
    return Counter(group for group, kind in zip(inputs.group_ids, inputs.perturbation_types) if kind != "drug")


def largest_gene_side_group(inputs: DrawInputs) -> tuple[str | None, int, int]:
    """(the largest group by gene-side members, ties to the smallest id; its size; how many groups tie at that size)."""
    counts = gene_side_count_of_group(inputs)
    if not counts:
        return None, 0, 0
    size = max(counts.values())
    tied = sorted(group for group, count in counts.items() if count == size)
    return tied[0], size, len(tied)


def most_shared_target(inputs: DrawInputs, held_out_fraction: float) -> dict:
    """The target held by the most drugs and its share of them; above twice the fraction, a seed whose order starts
    with it draws an empty drug side (held_out_targets' docstring)."""
    targets_of_drug = targets_of_drugs(inputs.perturbation_ids, inputs.perturbation_types, inputs.perturbation_seeds, inputs.node_ids)
    drugs_of_target = Counter(target for own in targets_of_drug.values() for target in own)
    if not drugs_of_target:
        return {"target": None, "drugs": 0, "share_of_drugs": 0.0, "above_twice_the_fraction": False}
    count = max(drugs_of_target.values())
    target = sorted(target for target, drugs in drugs_of_target.items() if drugs == count)[0]
    share = count / len(targets_of_drug)
    return {"target": target, "drugs": count, "share_of_drugs": share, "above_twice_the_fraction": share > 2 * held_out_fraction}


def population(inputs: DrawInputs, held_out_fraction: float) -> dict:
    largest, largest_size, tied = largest_gene_side_group(inputs)
    num_gene_side = sum(1 for kind in inputs.perturbation_types if kind != "drug")
    return {"perturbations": len(inputs.perturbation_ids),
            "drugs": sum(1 for kind in inputs.perturbation_types if kind == "drug"),
            "gene_side_perturbations": num_gene_side,
            "gene_side_groups": len(gene_side_count_of_group(inputs)),
            "largest_group": largest, "largest_group_size": largest_size,
            "largest_group_share": largest_size / num_gene_side if num_gene_side else 0.0,
            "groups_tied_for_largest": tied,
            "split_graph": bool(inputs.proteins_encoded_by_gene),
            "genes_encoding_a_protein_node": len(inputs.proteins_encoded_by_gene),
            "most_shared_target": most_shared_target(inputs, held_out_fraction)}


def held_out_targets_whose_gene_perturbation_trains(inputs: DrawInputs, held_out_ids: set[str], held_out_target_ids: set[str]) -> int:
    """Channel 2: held-out targets that a perturbation in training, not a drug, seeds or (on a split graph) encodes
    through the gene it seeds."""
    names = inputs.node_ids
    trained_target_nodes: set[str] = set()
    for perturbation_id, kind, seeds in zip(inputs.perturbation_ids, inputs.perturbation_types, inputs.perturbation_seeds):
        if kind == "drug" or perturbation_id in held_out_ids:
            continue
        own = {names[int(index)] for index in seeds}
        trained_target_nodes |= own | {protein for node in own for protein in inputs.proteins_encoded_by_gene.get(node, ())}
    return len(held_out_target_ids & trained_target_nodes)


def diagnose_one_draw(inputs: DrawInputs, seed: int, held_out_fraction: float, options: HeldOutDrawOptions) -> tuple[dict, set[str]]:
    """The numbers of one seed under one rule, and its gene side (for the Jaccard index across seeds)."""
    draw = two_sided_held_out_draw(inputs.perturbation_ids, inputs.perturbation_types, inputs.perturbation_seeds,
                                   inputs.node_ids, inputs.group_ids, seed, held_out_fraction, options=options,
                                   proteins_encoded_by_gene=inputs.proteins_encoded_by_gene)
    held = draw.held_out_ids
    gene_side_ids = [p for p, kind in zip(inputs.perturbation_ids, inputs.perturbation_types) if kind != "drug"]
    gene_side_held = {p for p in gene_side_ids if p in held}
    group_of = dict(zip(inputs.perturbation_ids, inputs.group_ids))
    largest, largest_size, _ = largest_gene_side_group(inputs)
    largest_on_side = sum(1 for p in gene_side_held if group_of[p] == largest)
    groups_inside = {group_of[p] for p in inputs.perturbation_ids if p in held}
    groups_outside = {group_of[p] for p in inputs.perturbation_ids if p not in held}
    numbers = {
        "drug_side_size": sum(1 for p, kind in zip(inputs.perturbation_ids, inputs.perturbation_types) if kind == "drug" and p in held),
        "held_out_targets": len(draw.held_out_target_ids),
        "gene_side_size": len(gene_side_held),
        "gene_side_share_of_gene_side_perturbations": len(gene_side_held) / len(gene_side_ids) if gene_side_ids else 0.0,
        "gene_side_groups": len({group_of[p] for p in gene_side_held}),
        "largest_group_size": largest_size,
        "largest_group_share": largest_size / len(gene_side_ids) if gene_side_ids else 0.0,
        "largest_group_members_on_the_gene_side": largest_on_side,
        "largest_group_wholly_on_the_gene_side": bool(largest_size) and largest_on_side == largest_size,
        "held_out_targets_whose_gene_perturbation_trains": held_out_targets_whose_gene_perturbation_trains(inputs, held, draw.held_out_target_ids),
        "m1_forced_groups": len(draw.forced_group_ids),
        "m1_forced_gene_side_size": len(draw.forced_gene_side_ids),
        "m1_forced_share_of_the_gene_side": draw.forced_share_of_the_gene_side,
        "m1_forced_groups_pass_the_fraction": draw.forced_groups_pass_the_fraction,
        "m1_overshoot": draw.overshoot,
        "groups_with_members_on_both_sides": len(groups_inside & groups_outside),
    }
    return numbers, gene_side_held


def jaccard_index(first: set[str], second: set[str]) -> float:
    union = first | second
    return 1.0 if not union else len(first & second) / len(union)


def gene_side_overlap(gene_side_of_seed: dict[int, set[str]]) -> dict:
    """The pairwise Jaccard index of the gene sides of every two seeds, with its range."""
    pairs = [[first, second, jaccard_index(gene_side_of_seed[first], gene_side_of_seed[second])]
             for first, second in itertools.combinations(sorted(gene_side_of_seed), 2)]
    values = [value for _, _, value in pairs]
    return {"pairs": pairs, "minimum": min(values) if values else None, "mean": float(np.mean(values)) if values else None,
            "maximum": max(values) if values else None,
            "the_same_gene_side_under_every_seed": bool(values) and all(value == 1.0 for value in values)}


def diagnose(inputs: DrawInputs, seeds: list[int], held_out_fraction: float, rules: dict[str, HeldOutDrawOptions] = RULES) -> dict:
    """The population block and, per rule, every seed's numbers and the overlap of the gene sides across seeds."""
    result = {"population": population(inputs, held_out_fraction), "rules": {}}
    for name, options in rules.items():
        per_seed, gene_side_of_seed = {}, {}
        for seed in seeds:
            per_seed[str(seed)], gene_side_of_seed[seed] = diagnose_one_draw(inputs, seed, held_out_fraction, options)
        result["rules"][name] = {"options": options.as_record(), "seeds": per_seed,
                                 "gene_side_jaccard_across_seeds": gene_side_overlap(gene_side_of_seed)}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--group-by", nargs="+", choices=sorted(GROUPING_COLUMNS), required=True,
                        help="one or more groupings; each is diagnosed on its own")
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--held-out-fraction", type=float, default=REGISTERED_HELD_OUT_FRACTION)
    parser.add_argument("--provenance", required=True,
                        help="the graph the numbers are taken on, when it was built, and the date measured")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if not arguments.provenance.strip():
        raise SystemExit("--provenance is empty")
    if len(set(arguments.seeds)) != len(arguments.seeds):
        raise SystemExit("--seeds repeats a seed")
    record = {"provenance": arguments.provenance, "made_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "graph_dir": str(arguments.graph_dir), "graph_file_sha256": graph_file_sha256(arguments.graph_dir),
              "evidence_dir": str(arguments.evidence_dir),
              "evidence_records_sha256": sha256_of_file(arguments.evidence_dir / "evidence_records.parquet"),
              "held_out_fraction": arguments.held_out_fraction, "seeds": arguments.seeds,
              "rules": {name: options.as_record() for name, options in RULES.items()}, "groupings": {}}
    for group_by in arguments.group_by:
        inputs = load_draw_inputs(arguments.graph_dir, arguments.evidence_dir, group_by)
        record["groupings"][group_by] = {"columns_read": inputs.columns_read,
                                         **diagnose(inputs, arguments.seeds, arguments.held_out_fraction)}
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(record, indent=1) + "\n")
    print(f"wrote {arguments.output}")


if __name__ == "__main__":
    main()
