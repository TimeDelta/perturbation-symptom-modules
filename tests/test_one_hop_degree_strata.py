"""The degree used for strata and normalisation hops over encodes on a graph that splits genes from proteins."""
from pathlib import Path

import numpy as np
import pytest

from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data
from mechanistic_pathway_learning.evaluation.ranking_and_calibration_metrics import degree_strata

# The monogenic slice (the pilot graph of data/releases/v0.4), its evidence table and its gene/protein split, on which
# the tests below check the hop over encodes. The slice block of scripts/rebuild_data_layer.sh writes them: it copies
# the first two from the release (data/releases/v0.4/graph and evidence_slice_sweeps) and builds the split with
# experiments/build_gene_protein_split.py, which also reads the UniProt proteome, the Reactome export and
# data/raw/chembl/targets.json. Running `bash scripts/rebuild_data_layer.sh slice` is not only that block: like every
# stage it first runs the shared raw fetches, graph builds and evidence tables whose outputs are missing, so on a disk
# without them it runs for hours and writes the directory names the registered rebuild will write (decision 9.106).
# Since 27 November 2026 it stops instead after the first of them: scripts/fetch_raw_sources.sh exits 1, so no slice
# table is written, until the cluster types of the pinned HPA release have a cell class (decision 9.155 (1); the usage
# comment of scripts/rebuild_data_layer.sh says why).
MERGED_GRAPH = Path("data/processed/graph")
SPLIT_GRAPH = Path("data/processed/graph_split")
EVIDENCE = Path("data/processed/evidence")
SLICE_TABLES_ARE_MISSING = (
    "{graph_directory} or {evidence_directory} is not built here. They come from the slice block of "
    "scripts/rebuild_data_layer.sh (two copies from data/releases/v0.4 and experiments/build_gene_protein_split.py, which "
    "also needs data/raw/uniprot/uniprot_human_reviewed.tsv.gz, data/raw/reactome/current and data/raw/chembl/targets.json); "
    "the script's slice stage first runs every shared fetch and build whose output is missing, which on a fresh disk is hours "
    "and writes the registered rebuild's directory names (decision 9.106)")


def load(graph_directory: Path):
    if not (graph_directory / "nodes.parquet").exists() or not (EVIDENCE / "evidence_records.parquet").exists():
        pytest.skip(SLICE_TABLES_ARE_MISSING.format(graph_directory=graph_directory, evidence_directory=EVIDENCE))
    return load_experiment_data(graph_directory, EVIDENCE, group_by="disease_cluster")


def test_the_seed_degree_collapses_on_the_split_graph_and_the_encodes_hop_does_not():
    split = load(SPLIT_GRAPH)
    assert len(np.unique(split.perturbation_degrees)) == 1, "the split graph is expected to give every perturbed gene degree 1"
    assert len(np.unique(split.perturbation_degrees_with_encoded_proteins)) > 1
    assert len(np.unique(degree_strata(split.perturbation_degrees_with_encoded_proteins))) > 1


def test_the_split_strata_are_the_merged_graph_strata():
    """The registered stratification is the merged graph's; the hop over encodes reproduces it."""
    merged, split = load(MERGED_GRAPH), load(SPLIT_GRAPH)
    assert list(merged.perturbation_ids) == list(split.perturbation_ids)
    assert np.array_equal(degree_strata(merged.perturbation_degrees), degree_strata(split.perturbation_degrees_for_strata))


def test_the_encodes_hop_recovers_the_merged_degree_itself_on_the_slice():
    """Not only the strata: on the slice the hop over encodes gives back the merged graph's degree value."""
    merged, split = load(MERGED_GRAPH), load(SPLIT_GRAPH)
    assert np.array_equal(split.perturbation_degrees_for_strata, merged.perturbation_degrees)


def test_a_merged_graph_keeps_the_seed_degree():
    merged = load(MERGED_GRAPH)
    assert np.array_equal(merged.perturbation_degrees_for_strata, merged.perturbation_degrees)
    assert np.array_equal(merged.perturbation_degrees_with_encoded_proteins, merged.perturbation_degrees)  # no encodes relation to hop over


def test_the_encodes_hop_is_at_least_the_seed_degree_everywhere():
    for graph_directory in (MERGED_GRAPH, SPLIT_GRAPH):
        data = load(graph_directory)
        assert (data.perturbation_degrees_with_encoded_proteins >= data.perturbation_degrees).all()
