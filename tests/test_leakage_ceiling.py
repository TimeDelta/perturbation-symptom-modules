"""Decision 9.35's leakage ceiling (ruled 24 November 2026: "Use 1.a but not on current graph. On graph at time of draw,
right?") and the draw it gates, built with every open definition left to the caller. Synthetic data only: nothing
here draws a held-out set or reads a real graph. The measurement's own tests, of the reached-node channel's arguments,
the k = 0 equivalence, graph_file_sha256 and the checkpoint guard, are in tests/test_measure_leakage_only_adversary.py."""
import json
import shutil
import sys
from pathlib import Path

import pandas as pd
import pytest

from mechanistic_pathway_learning.data_release import sha256_of_file
from mechanistic_pathway_learning.evaluation.leakage_ceiling import (
    GRAPH_BUILD_SUMMARIES,
    REACTOME_RELEASE_SUMMARY,
    draw_passes,
    first_passing_seed,
    fit_advantage_curve,
    reactome_release_of_graph,
    statistic_ceiling,
    validated_seed_order,
)
from mechanistic_pathway_learning.evaluation.leakage_only_adversary import registered_channel_list, seen_target_share
from mechanistic_pathway_learning.evaluation.target_held_out_split import (
    REGISTERED_HELD_OUT_FRACTION,
    targets_of_drugs,
    two_sided_held_out_perturbations,
)
from tests.test_measure_leakage_only_adversary import synthetic_data, write_graph_directory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from calibrate_leakage_ceiling import calibrate, refuse_another_graph  # noqa: E402
from draw_held_out_set import draw_held_out_set  # noqa: E402
from measure_leakage_only_adversary import graph_file_sha256, registered_two_sided_draw  # noqa: E402


# ---------------------------------------------------------------- the curve and its inversion


def test_a_line_is_inverted_where_it_reaches_one_standard_error():
    statistics = [0.1, 0.2, 0.3, 0.4]
    curve = fit_advantage_curve(statistics, [0.1 * value for value in statistics], "least_squares_line")
    assert curve["slope"] == pytest.approx(0.1) and curve["intercept"] == pytest.approx(0.0, abs=1e-12)
    result = statistic_ceiling(curve, 0.025)
    assert result["status"] == "ceiling" and result["ceiling"] == pytest.approx(0.25) and result["within_observed_range"]
    assert statistic_ceiling(curve, 0.08)["within_observed_range"] is False  # 0.8, beyond the largest pseudo-draw


def test_a_curve_that_gives_no_ceiling_is_reported_and_not_turned_into_one():
    flat = fit_advantage_curve([0.1, 0.2, 0.3], [0.03, 0.02, 0.01], "least_squares_line")
    assert statistic_ceiling(flat, 0.02)["ceiling"] is None
    isotonic = fit_advantage_curve([0.1, 0.2, 0.3], [0.0, 0.01, 0.02], "isotonic_increasing")
    assert statistic_ceiling(isotonic, 0.05)["ceiling"] is None  # never reaches the threshold in range
    assert statistic_ceiling(isotonic, 0.0001)["ceiling"] is not None
    already_above = fit_advantage_curve([0.1, 0.2], [0.06, 0.07], "isotonic_increasing")
    assert statistic_ceiling(already_above, 0.05)["ceiling"] is None


def test_an_isotonic_fit_is_inverted_between_its_knots():
    curve = fit_advantage_curve([0.1, 0.2, 0.3, 0.4], [0.0, 0.01, 0.03, 0.05], "isotonic_increasing")
    # 0.02 lies halfway between the knots at 0.2 (0.01) and 0.3 (0.03)
    assert statistic_ceiling(curve, 0.02)["ceiling"] == pytest.approx(0.25)


def test_the_curve_has_no_default_form_and_needs_two_statistic_values():
    with pytest.raises(ValueError):
        fit_advantage_curve([0.1, 0.2], [0.0, 0.1], "spline")
    with pytest.raises(ValueError):
        fit_advantage_curve([0.2, 0.2, float("nan")], [0.0, 0.1, 0.2], "least_squares_line")
    curve = fit_advantage_curve([0.1, 0.2, float("nan")], [0.0, 0.1, 0.2], "least_squares_line")
    assert curve["pseudo_draws_left_out_as_not_finite"] == 1
    with pytest.raises(ValueError):
        statistic_ceiling(curve, 0.0)


# ---------------------------------------------------------------- acceptance


def test_a_draw_passes_only_strictly_below_every_ceiling():
    assert draw_passes({"a": 0.1, "b": 0.2}, {"a": 0.2, "b": 0.3}) == (True, [])
    assert draw_passes({"a": 0.2}, {"a": 0.2})[0] is False  # at the ceiling the fitted advantage is one standard error
    assert draw_passes({"a": float("nan")}, {"a": 0.2})[0] is False
    assert draw_passes({}, {"a": 0.2})[0] is False
    with pytest.raises(ValueError):
        draw_passes({"a": 0.1}, {})


def test_the_first_passing_seed_is_accepted_and_no_later_seed_is_examined():
    statistic_of_seed = {7: 0.5, 3: 0.4, 9: 0.1, 4: 0.05}
    called = []

    def statistics_of_seed(seed):
        called.append(seed)
        return {"share": statistic_of_seed[seed]}

    result = first_passing_seed([7, 3, 9, 4], statistics_of_seed, {"share": 0.3})
    assert result["accepted_seed"] == 9 and called == [7, 3, 9]  # 4 also passes and is never looked at
    assert [entry["passed"] for entry in result["examined"]] == [False, False, True]
    assert first_passing_seed([7, 3], statistics_of_seed, {"share": 0.01})["accepted_seed"] is None


def test_the_seed_order_must_be_whole_numbers_without_a_repeat():
    assert validated_seed_order([5, 2, 9]) == [5, 2, 9]
    for bad in ([], [1, 1], [1.0, 2], [True, 2], ["1"]):
        with pytest.raises(ValueError):
            validated_seed_order(bad)


# ---------------------------------------------------------------- the graph the draw is made on


# Fixture graphs laid out as the builders of the registered chain lay theirs out (scripts/rebuild_data_layer.sh), under
# a stand-in repository root, each with the summary its builder writes and only the keys reactome_release_of_graph
# reads, its source recorded as the relative path the builder was given.

PROCESSED = "data/processed"


def write_parquet_graph(directory: Path, node_types: list[str], relations: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    directory.mkdir(parents=True, exist_ok=True)
    nodes = pd.DataFrame({"node_id": [f"N{position}" for position in range(len(node_types))], "node_type": node_types})
    edges = pd.DataFrame({"source_id": ["N0"] * len(relations), "target_id": ["N1"] * len(relations), "relation_type": relations})
    nodes.to_parquet(directory / "nodes.parquet")
    edges.to_parquet(directory / "edges.parquet")
    (directory / "relation_types.json").write_text(json.dumps(sorted(set(relations))))
    return nodes, edges


def value_counts(table: pd.DataFrame, column: str) -> dict:
    return {str(value): int(count) for value, count in table[column].value_counts().items()}


def build_neuronal(root: Path, name="graph_full_neuronal", release=98) -> Path:
    directory = root / PROCESSED / name
    nodes, edges = write_parquet_graph(directory, ["gene", "gene", "metabolite", "reaction"], ["catalyzes", "produces", "produces"])
    summary = {"base_graph": f"{PROCESSED}/graph_full_manganese", "nodes_by_type": value_counts(nodes, "node_type"),
               "edges_by_relation": value_counts(edges, "relation_type")}
    if release is not None:
        summary["reactome_pathways"] = {"reactome_release": release, "pathways": {}}
    (directory / "neuronal_variant_summary.json").write_text(json.dumps(summary, indent=1))
    (directory / "node_descriptors_summary.json").write_text(json.dumps({"rows": 4}))
    return directory


def build_split(root: Path, source: Path, name="graph_full_neuronal_split") -> Path:
    directory = root / PROCESSED / name
    source_nodes, source_edges = pd.read_parquet(source / "nodes.parquet"), pd.read_parquet(source / "edges.parquet")
    nodes, edges = write_parquet_graph(directory, list(source_nodes.node_type) + ["protein", "protein"],
                                       list(source_edges.relation_type) + ["encodes", "encodes"])
    pd.DataFrame({"gene_node_id": ["N0", "N1"], "protein_node_id": ["N4", "N5"]}).to_parquet(directory / "gene_to_protein.parquet")
    (directory / "split_summary.json").write_text(json.dumps({
        "gene_nodes": int((source_nodes.node_type == "gene").sum()), "edges_before": len(source_edges), "edges_after": len(edges),
        "edges_per_relation": value_counts(edges, "relation_type"), "graph_dir": str(source.relative_to(root)),
        "output_dir": str(directory.relative_to(root)), "nodes_before": len(source_nodes), "nodes_after": len(nodes)}, indent=1))
    return directory


def build_binders(root: Path, source: Path) -> Path:
    directory = source.parent / f"{source.name}_binders"  # build_plasma_binder_variant.py's own naming
    source_nodes, source_edges = pd.read_parquet(source / "nodes.parquet"), pd.read_parquet(source / "edges.parquet")
    nodes, edges = write_parquet_graph(directory, list(source_nodes.node_type), list(source_edges.relation_type) + ["binds"])
    for copied in ("node_descriptors_summary.json", "gene_to_protein.parquet"):  # its COPIED_FILES that the fixture holds
        if (source / copied).exists():
            shutil.copyfile(source / copied, directory / copied)
    (directory / "plasma_binder_summary.json").write_text(json.dumps({
        "edges_added": 1, "source_graph": str(source.relative_to(root)), "nodes": len(nodes), "edges_before": len(source_edges),
        "edges_after": len(edges)}, indent=1))
    return directory


def build_drugs(root: Path, source: Path, name: str) -> Path:
    directory = root / PROCESSED / name
    source_nodes, source_edges = pd.read_parquet(source / "nodes.parquet"), pd.read_parquet(source / "edges.parquet")
    for source_file in sorted(source.iterdir()):  # build_drug_entry_node_variant.py copies every file it does not rewrite
        if source_file.is_file() and source_file.name not in ("nodes.parquet", "edges.parquet", "relation_types.json"):
            directory.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, directory / source_file.name)
    write_parquet_graph(directory, list(source_nodes.node_type) + ["drug"], list(source_edges.relation_type) + ["targets"])
    (directory / "drug_entry_summary.json").write_text(json.dumps({
        "source_graph": str(source.relative_to(root)), "source_nodes_sha256": sha256_of_file(source / "nodes.parquet"),
        "source_edges_sha256": sha256_of_file(source / "edges.parquet"), "nodes_sha256": sha256_of_file(directory / "nodes.parquet"),
        "edges_sha256": sha256_of_file(directory / "edges.parquet")}, indent=1))
    return directory


def registered_chain(root: Path) -> dict[str, Path]:
    neuronal = build_neuronal(root)
    split = build_split(root, neuronal)
    split_binders = build_binders(root, split)
    return {"neuronal": neuronal, "split": split, "neuronal_binders": build_binders(root, neuronal),
            "split_binders": split_binders, "drugs_v5": build_drugs(root, split_binders, "graph_full_neuronal_split_binders_drugs_v5")}


def test_the_reactome_release_is_found_on_every_graph_of_the_registered_chain(tmp_path):
    chain = registered_chain(tmp_path)
    expected_links = {"neuronal": [], "split": ["split_summary.json"], "neuronal_binders": ["plasma_binder_summary.json"],
                      "split_binders": ["plasma_binder_summary.json", "split_summary.json"],
                      "drugs_v5": ["drug_entry_summary.json", "plasma_binder_summary.json", "split_summary.json"]}
    for graph, links in expected_links.items():
        found = reactome_release_of_graph(chain[graph], relative_to=tmp_path)
        assert found["reactome_release"] == "98"
        assert found["read_from"] == str(chain["neuronal"] / "neuronal_variant_summary.json")
        assert [link["summary"] for link in found["lineage"]] == links
        if links:
            assert Path(found["lineage"][0]["graph_dir"]) == chain[graph]
            assert Path(found["lineage"][-1]["source_graph_dir"]) == chain["neuronal"]
    drugs = reactome_release_of_graph(chain["drugs_v5"], relative_to=tmp_path)["lineage"]
    # the drug variant holds a copy of the binders' summary, and its own summary is told from it by what each records of its output
    assert (chain["drugs_v5"] / "plasma_binder_summary.json").exists()
    assert drugs[0]["source_recorded_as"] == f"{PROCESSED}/graph_full_neuronal_split_binders"
    assert "SHA-256" in drugs[0]["link_checked_by"] and "row counts" in drugs[1]["link_checked_by"] and "row counts" in drugs[2]["link_checked_by"]


def test_a_zero_count_a_categorical_column_records_is_not_a_mismatch(tmp_path):
    chain = registered_chain(tmp_path)
    neuronal = json.loads((chain["neuronal"] / "neuronal_variant_summary.json").read_text())
    neuronal["nodes_by_type"]["protein"] = 0
    (chain["neuronal"] / "neuronal_variant_summary.json").write_text(json.dumps(neuronal))
    assert reactome_release_of_graph(chain["split"], relative_to=tmp_path)["reactome_release"] == "98"


def test_a_relative_source_is_resolved_against_the_working_directory_by_default(tmp_path, monkeypatch):
    chain = registered_chain(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert reactome_release_of_graph(Path(PROCESSED) / "graph_full_neuronal_split_binders_drugs_v5")["reactome_release"] == "98"
    monkeypatch.chdir(chain["split"])  # elsewhere the recorded paths lead nowhere, and that is refused, not searched for
    with pytest.raises(ValueError, match="cannot be followed"):
        reactome_release_of_graph(chain["drugs_v5"])


def test_a_graph_without_a_recorded_lineage_is_refused(tmp_path):
    write_parquet_graph(tmp_path / "bare", ["gene", "gene"], ["catalyzes"])
    with pytest.raises(ValueError, match="lineage of .* is not recorded"):
        reactome_release_of_graph(tmp_path / "bare", relative_to=tmp_path)
    with pytest.raises(ValueError, match="holds no nodes.parquet"):
        reactome_release_of_graph(tmp_path / "missing", relative_to=tmp_path)
    chain = registered_chain(tmp_path)
    summary = json.loads((chain["split"] / "split_summary.json").read_text())
    del summary["graph_dir"]
    (chain["split"] / "split_summary.json").write_text(json.dumps(summary))
    with pytest.raises(ValueError, match="names no graph it was built from"):
        reactome_release_of_graph(chain["split_binders"], relative_to=tmp_path)


def test_a_summary_that_does_not_describe_its_directory_is_not_its_own(tmp_path):
    chain = registered_chain(tmp_path)
    neuronal = json.loads((chain["neuronal"] / "neuronal_variant_summary.json").read_text())
    neuronal["nodes_by_type"]["gene"] += 1
    (chain["neuronal"] / "neuronal_variant_summary.json").write_text(json.dumps(neuronal))
    with pytest.raises(ValueError, match="does not describe this directory's graph files"):
        reactome_release_of_graph(chain["split"], relative_to=tmp_path)


def test_a_source_rebuilt_since_the_derived_graph_is_refused(tmp_path):
    chain = registered_chain(tmp_path)
    edges = pd.read_parquet(chain["split_binders"] / "edges.parquet")
    edges.loc[0, "target_id"] = "N2"  # same rows, other content: only a digest sees it
    edges.to_parquet(chain["split_binders"] / "edges.parquet")
    with pytest.raises(ValueError, match="is not the graph .* was built from, by the SHA-256"):
        reactome_release_of_graph(chain["drugs_v5"], relative_to=tmp_path)
    write_parquet_graph(chain["neuronal"], ["gene", "gene", "gene", "metabolite", "reaction"], ["catalyzes", "produces", "produces"])
    with pytest.raises(ValueError, match="row counts"):
        reactome_release_of_graph(chain["neuronal_binders"], relative_to=tmp_path)


def test_an_ambiguous_or_circular_lineage_is_refused(tmp_path):
    chain = registered_chain(tmp_path)
    nodes, edges = pd.read_parquet(chain["drugs_v5"] / "nodes.parquet"), pd.read_parquet(chain["drugs_v5"] / "edges.parquet")
    (chain["drugs_v5"] / "plasma_binder_summary.json").write_text(json.dumps({
        "source_graph": f"{PROCESSED}/graph_full_neuronal_split", "nodes": len(nodes), "edges_before": len(edges) - 1, "edges_after": len(edges)}))
    with pytest.raises(ValueError, match="ambiguous"):
        reactome_release_of_graph(chain["drugs_v5"], relative_to=tmp_path)
    first, second = tmp_path / "first", tmp_path / "second"
    for directory, other in ((first, second), (second, first)):
        nodes, edges = write_parquet_graph(directory, ["gene", "protein"], ["encodes"])
        (directory / "split_summary.json").write_text(json.dumps({
            "graph_dir": str(other), "nodes_before": 2, "edges_before": 1, "gene_nodes": 1, "nodes_after": 2, "edges_after": 1,
            "edges_per_relation": {"encodes": 1}}))
    with pytest.raises(ValueError, match="returns to"):
        reactome_release_of_graph(first, relative_to=tmp_path)


def test_a_neuronal_summary_without_a_release_is_refused(tmp_path):
    neuronal = build_neuronal(tmp_path, release=None)
    with pytest.raises(ValueError, match="9.111"):
        reactome_release_of_graph(build_split(tmp_path, neuronal), relative_to=tmp_path)


REPOSITORY = Path(__file__).resolve().parents[1]


def test_the_builders_still_write_the_summaries_and_keys_the_lineage_reads():
    # what each builder's source must still say for GRAPH_BUILD_SUMMARIES to describe what it writes
    written = {
        "neuronal_variant_summary.json": ["base_graph=", "reactome_pathways=", "nodes_by_type=", "edges_by_relation="],
        "split_summary.json": ['"graph_dir": str(arguments.graph_dir)', '"nodes_before"', '"nodes_after"', '"edges_before"',
                               '"edges_after"', '"gene_nodes"', '"edges_per_relation"'],
        "plasma_binder_summary.json": ["source_graph=str(graph_directory)", "nodes=len(new_nodes)", "edges_before=len(edges)",
                                       "edges_after=len(new_edges)"],
        "drug_entry_summary.json": ["source_graph=str(arguments.graph_dir)", "source_nodes_sha256=", "source_edges_sha256=",
                                    "nodes_sha256=", "edges_sha256="],
    }
    assert set(written) == set(GRAPH_BUILD_SUMMARIES) and REACTOME_RELEASE_SUMMARY in written
    for summary_name, keys in written.items():
        builder = GRAPH_BUILD_SUMMARIES[summary_name]["builder"]
        text = (REPOSITORY / builder).read_text()
        if summary_name == "split_summary.json":  # the split's counts are made in the module the builder calls
            text += (REPOSITORY / "mechanistic_pathway_learning/graph/gene_protein_split.py").read_text()
        if summary_name == "plasma_binder_summary.json":
            assert "new_nodes = nodes.copy()" in (REPOSITORY / "mechanistic_pathway_learning/graph/plasma_binding.py").read_text()
        assert summary_name in text, f"{builder} no longer names {summary_name}"
        for key in keys:
            assert key in text, f"{builder} no longer writes {key} into {summary_name}"


# ---------------------------------------------------------------- the calibration


def measurement_record(num_draws=6, channels=None):
    draws = [{"draw_seed": seed, "usable": True, "seen_target_share": 0.1 * (seed + 1),
              "drug_stratum_macro_advantage_over_type_popularity": 0.02 * (seed + 1)} for seed in range(num_draws)]
    draws[2]["usable"] = False
    del draws[3]["drug_stratum_macro_advantage_over_type_popularity"]
    return {"num_draws": num_draws, "pseudo_draw_seeds": list(range(num_draws)), "group_by": "disease_cluster",
            "channels": channels or registered_channel_list(), "lockbox_excluded": None,
            "pooling_rules": {"base_rate_shrunk_mean": {"draws": draws}}}


def test_the_calibration_fits_the_usable_draws_and_names_the_rest():
    result = calibrate(measurement_record(), "base_rate_shrunk_mean", "seen_target_share",
                       "drug_stratum_macro_advantage_over_type_popularity", 0.05, "least_squares_line", 6)
    assert [point["draw_seed"] for point in result["points"]] == [0, 1, 4, 5]
    assert {entry["draw_seed"] for entry in result["pseudo_draws_left_out"]} == {2, 3}
    assert result["ceiling"]["ceiling"] == pytest.approx(0.25)  # advantage = 0.2 x share, so 0.05 at 0.25
    assert result["pseudo_draw_seeds"] == list(range(6)) and result["group_by"] == "disease_cluster"


def test_the_calibration_refuses_what_it_cannot_read_without_labels_or_was_not_measured():
    arguments = ("base_rate_shrunk_mean", "seen_target_share", "drug_stratum_macro_advantage_over_type_popularity", 0.05, "least_squares_line")
    with pytest.raises(ValueError, match="pseudo-draws"):
        calibrate(measurement_record(), *arguments, 20)  # the count is the caller's and must match
    with pytest.raises(ValueError, match="label-free"):
        calibrate(measurement_record(), "base_rate_shrunk_mean", "held_out_drugs", arguments[2], 0.05, "least_squares_line", 6)
    with pytest.raises(ValueError, match="key"):
        calibrate(measurement_record(), "base_rate_shrunk_mean", "seen_target_share", "adversary_macro_auprc", 0.05, "least_squares_line", 6)
    with pytest.raises(ValueError, match="reached-node channel"):
        calibrate(measurement_record(), "base_rate_shrunk_mean", "seen_reached_node_share", arguments[2], 0.05, "least_squares_line", 6)


def test_the_calibration_refuses_a_measurement_made_on_another_graph(tmp_path):
    graph = write_graph_directory(tmp_path / "graph")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "evidence_records.parquet").write_bytes(b"evidence")
    selection = tmp_path / "selection.parquet"
    selection.write_bytes(b"selection")
    digests = {"graph_file_sha256": graph_file_sha256(graph),
               "evidence_records_sha256": sha256_of_file(evidence / "evidence_records.parquet"),
               "label_selection_sha256": sha256_of_file(selection)}
    refuse_another_graph(digests, graph, evidence, selection)  # the same inputs pass
    with pytest.raises(ValueError, match="records no"):
        refuse_another_graph({}, graph, evidence, selection)  # a measurement from before 27 November 2026
    (graph / "edges.parquet").write_bytes(b"a later graph")
    with pytest.raises(ValueError, match="graph the draw is made on"):
        refuse_another_graph(digests, graph, evidence, selection)


# ---------------------------------------------------------------- the draw


DIGESTS = {"graph_file_sha256": {"nodes.parquet": "n"}, "evidence_records_sha256": "e", "label_selection_sha256": "selection"}


def calibration_record(statistic="seen_target_share", ceiling=1.0, channels=None, pseudo_draw_seeds=range(5), group_by="disease_cluster"):
    return {**DIGESTS, "statistic": statistic, "ceiling": {"ceiling": ceiling, "status": "ceiling"},
            "channels": channels or registered_channel_list(), "pseudo_draw_seeds": list(pseudo_draw_seeds), "group_by": group_by}


def test_the_two_sided_draw_holds_each_side_out_at_the_registered_fraction():
    data = synthetic_data()
    held_out, held_targets = two_sided_held_out_perturbations(
        data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids, data.group_ids, seed=11)
    assert registered_two_sided_draw(data, 11) == (held_out, held_targets)  # the measurement draws by the same function
    targets = targets_of_drugs(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids)
    for drug, own in targets.items():
        assert (drug in held_out) == bool(own & held_targets)
    held_genes = [identifier for identifier in held_out if identifier.startswith("g")]
    assert 0 < len(held_genes) < 28 * 2 * REGISTERED_HELD_OUT_FRACTION
    group_of = dict(zip(data.perturbation_ids, data.group_ids))
    gene_groups_held = {group_of[gene] for gene in held_genes}
    assert all(gene in held_out for gene in data.perturbation_ids if gene.startswith("g") and group_of[gene] in gene_groups_held)


def test_the_draw_accepts_the_first_seed_below_the_ceiling():
    data = synthetic_data()
    targets = targets_of_drugs(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids)

    def share(seed):
        held_out, _ = two_sided_held_out_perturbations(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds,
                                                       data.node_ids, data.group_ids, seed)
        return seen_target_share(targets, held_out)

    order = list(range(100, 140))
    shares = [share(seed) for seed in order]
    later = next(position for position in range(1, len(order)) if shares[position] < shares[0])
    record = draw_held_out_set(data, order, [calibration_record(ceiling=shares[0])], "disease_cluster", DIGESTS)
    assert record["accepted_seed"] == order[later]
    assert [entry["seed"] for entry in record["examined_seeds"]] == order[:later + 1]
    expected, _ = two_sided_held_out_perturbations(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds,
                                                   data.node_ids, data.group_ids, order[later])
    assert record["perturbation_ids"] == sorted(expected)
    assert record["num_perturbations"] + record["num_development_perturbations"] == len(data.perturbation_ids)
    assert set(record["symptoms_in_the_macro_average"]) <= set(data.symptoms)
    assert record["channels"] == registered_channel_list()


def test_a_draw_where_no_seed_passes_holds_nothing_out():
    record = draw_held_out_set(synthetic_data(), [100, 101], [calibration_record(ceiling=-1.0)], "disease_cluster", DIGESTS)
    assert record["accepted_seed"] is None and "perturbation_ids" not in record and len(record["examined_seeds"]) == 2


def test_the_draw_refuses_ceilings_from_other_inputs_or_seeds_the_calibration_scored():
    data = synthetic_data()
    with pytest.raises(ValueError, match="pseudo-draws"):
        draw_held_out_set(data, [3, 100], [calibration_record()], "disease_cluster", DIGESTS)
    with pytest.raises(ValueError, match="graph the draw is made on"):
        draw_held_out_set(data, [100], [calibration_record()], "disease_cluster", {**DIGESTS, "graph_file_sha256": {"nodes.parquet": "m"}})
    with pytest.raises(ValueError, match="grouped the gene side"):
        draw_held_out_set(data, [100], [calibration_record()], "disease_cluster_and_targets", DIGESTS)
    with pytest.raises(ValueError, match="owner"):
        draw_held_out_set(data, [100], [{**calibration_record(), "ceiling": {"ceiling": None, "status": "no ceiling"}}], "disease_cluster", DIGESTS)
    with pytest.raises(ValueError, match="two calibrations"):
        draw_held_out_set(data, [100], [calibration_record(), calibration_record()], "disease_cluster", DIGESTS)
    reached_channels = registered_channel_list(1, [("drug", "gene")], "stored")
    with pytest.raises(ValueError, match="different channels"):
        draw_held_out_set(data, [100], [calibration_record(), calibration_record("seen_reached_node_share", channels=reached_channels)],
                          "disease_cluster", DIGESTS)
    with pytest.raises(ValueError, match="reached-node channel on"):
        draw_held_out_set(data, [100], [calibration_record("seen_reached_node_share")], "disease_cluster", DIGESTS)


def test_the_draw_checks_the_reached_node_statistic_with_the_calibrated_channel():
    data = synthetic_data()
    channels = registered_channel_list(1, [("drug", "gene")], "stored")
    calibrations = [calibration_record(ceiling=2.0, channels=channels),
                    calibration_record("seen_reached_node_share", ceiling=2.0, channels=channels)]
    record = draw_held_out_set(data, [100, 101], calibrations, "disease_cluster", DIGESTS)
    assert record["accepted_seed"] == 100
    statistics = record["examined_seeds"][0]["statistics"]
    assert set(statistics) == {"seen_target_share", "seen_reached_node_share"} and 0.0 <= statistics["seen_reached_node_share"] <= 1.0
