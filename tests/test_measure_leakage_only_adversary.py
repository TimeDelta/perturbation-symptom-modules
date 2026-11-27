"""experiments/measure_leakage_only_adversary.py: the reached-node channel of decision 9.36 (ruled 24 November 2026: "the
k=2 reached-node channel enters the adversary of 9.35, with k as a sensitivity sweep") switched on by its arguments and
off by default, the digests that say which graph the pseudo-draws were made on, and the checkpoint directory that is
resumed only on the inputs its draws were computed on. Synthetic data only: nothing here reads a real graph."""
import argparse
import json
from pathlib import Path

import numpy as np
import pytest

from experiments.measure_leakage_only_adversary import (
    CHECKPOINT_INPUTS_FILE, SHARED_SEED_NODE_RUN_DEFAULTS, claim_checkpoint_directory, graph_file_sha256, one_draw,
    parse_type_pairs, resolve_channel_arguments)
from mechanistic_pathway_learning.evaluation.experiment_data import ExperimentData
from mechanistic_pathway_learning.evaluation.leakage_only_adversary import reached_nodes_of_perturbations, registered_channel_list


def synthetic_data(num_genes=28, num_drugs=21, num_targets=9) -> ExperimentData:
    generator = np.random.default_rng(3)
    target_names = [f"PROTEIN:T{index}" for index in range(num_targets)]
    gene_names = [f"GENE:G{index}" for index in range(num_genes)]
    node_ids = target_names + gene_names
    drug_seeds = [sorted(generator.choice(num_targets, size=int(generator.integers(1, 4)), replace=False).tolist()) for _ in range(num_drugs)]
    gene_seeds = [[num_targets + index] for index in range(num_genes)]
    perturbation_ids = [f"d{index}" for index in range(num_drugs)] + [f"g{index}" for index in range(num_genes)]
    kinds = ["drug"] * num_drugs + ["gene"] * num_genes
    groups = [f"drug_group_{index}" for index in range(num_drugs)] + [f"cluster_{index // 2}" for index in range(num_genes)]
    seeds = [np.array(seed) for seed in drug_seeds + gene_seeds]
    num_perturbations = len(perturbation_ids)
    outcomes = (generator.random((num_perturbations, 3)) < 0.4).astype(float)
    # each gene reaches its target's protein: gene index i encodes target i % num_targets
    edge_source = np.array([num_targets + index for index in range(num_genes)])
    edge_target = np.array([index % num_targets for index in range(num_genes)])
    return ExperimentData(
        node_ids=node_ids, node_index={name: index for index, name in enumerate(node_ids)},
        node_types=np.array(["protein"] * num_targets + ["gene"] * num_genes), is_currency=np.zeros(len(node_ids), dtype=bool),
        node_degree=np.ones(len(node_ids)), edge_source=edge_source, edge_target=edge_target,
        edge_relation=np.zeros(len(edge_source), dtype=int), relation_types=["encodes"], symptoms=["anxiety", "fatigue", "tremor"],
        perturbation_ids=perturbation_ids, perturbation_labels=perturbation_ids, perturbation_types=kinds, group_ids=groups,
        perturbation_seeds=seeds, perturbation_signs=[np.array([-1.0] * len(seed)) for seed in seeds],
        perturbation_magnitudes=[np.array([1.0] * len(seed)) for seed in seeds], outcomes=outcomes, weights=outcomes,
        in_metabolic_layer=np.ones(num_perturbations, dtype=bool), frequencies=np.where(outcomes > 0, 0.4, np.nan),
        label_mask=np.ones_like(outcomes, dtype=bool), label_selection_summary={"sha256": "selection"})


def write_graph_directory(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    for name in ("nodes.parquet", "edges.parquet"):
        (directory / name).write_bytes(name.encode())
    (directory / "relation_types.json").write_text("[]")
    return directory


# ---------------------------------------------------------------- the channel's arguments


def namespace(**overrides):
    values = {"reached_node_hops": None, "reached_node_type_pairs": None, "reached_node_edges": None,
              "checkpoint_dir": None, "json_output": None, "markdown_output": None}
    values.update(overrides)
    return argparse.Namespace(**values)


def test_the_shared_seed_node_run_keeps_its_paths_and_a_reached_node_run_must_name_its_own(tmp_path):
    parser = argparse.ArgumentParser()
    off = namespace()
    assert resolve_channel_arguments(parser, off) is None
    assert off.json_output == SHARED_SEED_NODE_RUN_DEFAULTS["json_output"]
    with pytest.raises(SystemExit):
        resolve_channel_arguments(parser, namespace(reached_node_type_pairs=["gene:gene"]))
    with pytest.raises(SystemExit):
        resolve_channel_arguments(parser, namespace(reached_node_hops=2, reached_node_edges="stored"))
    with pytest.raises(SystemExit):
        resolve_channel_arguments(parser, namespace(reached_node_hops=2, reached_node_type_pairs=["gene:gene"], reached_node_edges="stored"))
    own_paths = {"checkpoint_dir": tmp_path / "draws", "json_output": tmp_path / "k2.json", "markdown_output": tmp_path / "k2.md"}
    with pytest.raises(SystemExit):
        resolve_channel_arguments(parser, namespace(reached_node_hops=2, reached_node_type_pairs=["gene:gene"], reached_node_edges="stored",
                                                    **{**own_paths, "json_output": SHARED_SEED_NODE_RUN_DEFAULTS["json_output"]}))
    on = namespace(reached_node_hops=2, reached_node_type_pairs=["gene:gene", "drug:gene"], reached_node_edges="stored", **own_paths)
    assert resolve_channel_arguments(parser, on) == [("gene", "gene"), ("drug", "gene")]
    with pytest.raises(ValueError):
        parse_type_pairs(["gene"])


def test_a_measurement_with_the_channel_at_k0_reads_what_the_channel_off_reads():
    """k = 0 is the shared seed node channel, so the adversary's readings match; only the extra statistic differs."""
    data = synthetic_data()
    off = one_draw(data, 100, "base_rate_shrunk_mean", 20)
    reached = reached_nodes_of_perturbations(data.perturbation_ids, data.perturbation_seeds, data.node_ids, data.edge_source, data.edge_target, 0)
    every_pair = [(left, right) for left in ("gene", "drug") for right in ("gene", "drug")]
    at_zero = one_draw(data, 100, "base_rate_shrunk_mean", 20, reached, every_pair)
    assert "seen_reached_node_share" not in off and "seen_reached_node_share" in at_zero
    del at_zero["seen_reached_node_share"]
    assert json.dumps(off, sort_keys=True) == json.dumps(at_zero, sort_keys=True)


# ---------------------------------------------------------------- which graph, and the checkpoint directory


def test_the_graph_is_identified_by_the_files_the_loader_reads(tmp_path):
    graph = write_graph_directory(tmp_path / "graph")
    digests = graph_file_sha256(graph)
    assert sorted(digests) == ["edges.parquet", "nodes.parquet", "relation_types.json"]
    (graph / "drug_entry_nodes.parquet").write_bytes(b"entries")
    assert "drug_entry_nodes.parquet" in graph_file_sha256(graph)
    (graph / "edges.parquet").write_bytes(b"another graph")
    assert graph_file_sha256(graph)["edges.parquet"] != digests["edges.parquet"]
    with pytest.raises(FileNotFoundError):
        graph_file_sha256(tmp_path / "no_graph")


def test_a_checkpoint_directory_is_resumed_only_on_the_inputs_its_draws_were_computed_on(tmp_path):
    """A checkpointed draw is named by pooling rule and seed only, so resuming on another graph or with other channels
    would write this run's digests over draws made on other inputs, and those digests are what say which graph the
    pseudo-draws were made on."""
    inputs = {"graph_file_sha256": {"nodes.parquet": "n"}, "evidence_records_sha256": "e", "label_selection_sha256": "s",
              "group_by": "disease_cluster", "num_bootstrap": 20, "lockbox_excluded": None,
              "excluded_lockbox_perturbations": 0, "channels": registered_channel_list(2, [("gene", "gene")], "stored")}
    directory = tmp_path / "draws"
    claim_checkpoint_directory(directory, inputs)
    assert json.loads((directory / CHECKPOINT_INPUTS_FILE).read_text()) == json.loads(json.dumps(inputs))
    (directory / "base_rate_shrunk_mean_draw_000.json").write_text("{}")
    claim_checkpoint_directory(directory, inputs)  # the same inputs resume
    with pytest.raises(SystemExit, match="graph_file_sha256"):
        claim_checkpoint_directory(directory, {**inputs, "graph_file_sha256": {"nodes.parquet": "a later graph"}})
    with pytest.raises(SystemExit, match="channels"):
        claim_checkpoint_directory(directory, {**inputs, "channels": registered_channel_list(1, [("gene", "gene")], "stored")})
    legacy = tmp_path / "legacy"
    legacy.mkdir()
    (legacy / "base_rate_shrunk_mean_draw_000.json").write_text("{}")
    with pytest.raises(SystemExit, match=CHECKPOINT_INPUTS_FILE):
        claim_checkpoint_directory(legacy, inputs)
