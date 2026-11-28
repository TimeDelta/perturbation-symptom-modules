"""Tests added on 28 November 2026 to kill mutants of mechanistic_pathway_learning/evaluation/leakage_ceiling.py that the
tests of tests/test_leakage_ceiling.py let survive (hand-made mutation testing; the mutants and which test kills each
were listed in the working report of the session of 28 November 2026, which is outside the repository). Each test checks what a docstring of the module says the code does; none treats
an open choice of the draft as registered. Synthetic data only."""
import json

import numpy as np
import pandas as pd
import pytest

from mechanistic_pathway_learning.evaluation.leakage_ceiling import (
    draw_passes,
    first_passing_seed,
    fit_advantage_curve,
    reactome_release_of_graph,
    statistic_ceiling,
    validated_seed_order,
)
from tests.test_leakage_ceiling import build_neuronal, build_split, registered_chain, write_parquet_graph


def hand_made_line(slope, intercept, lowest=0.1, highest=0.4):
    """A curve in the form fit_advantage_curve returns, with values chosen so that the inversion is exact."""
    return {"curve_form": "least_squares_line", "slope": slope, "intercept": intercept,
            "observed_statistic_range": [lowest, highest]}


# ---------------------------------------------------------------- the fit


def test_a_fit_needs_one_advantage_per_statistic():
    """_finite_pairs: "label_free_statistics and advantages must be one value per pseudo-draw, the same number of each"."""
    with pytest.raises(ValueError, match="one value per pseudo-draw"):
        fit_advantage_curve([0.1, 0.2, 0.3], [0.01, 0.02], "least_squares_line")


def test_a_pseudo_draw_whose_advantage_is_not_finite_is_left_out_and_counted():
    """fit_advantage_curve: "Pseudo-draws where either value is not finite are left out and counted"."""
    curve = fit_advantage_curve([0.1, 0.2, 0.3, 0.4], [0.01, float("nan"), 0.03, float("inf")], "least_squares_line")
    assert curve["pseudo_draws_fitted"] == 2 and curve["pseudo_draws_left_out_as_not_finite"] == 2
    assert curve["slope"] == pytest.approx(0.1) and curve["intercept"] == pytest.approx(0.0, abs=1e-12)
    assert curve["observed_statistic_range"] == [0.1, 0.3]


def test_the_isotonic_fit_does_not_decrease():
    """CURVE_FORMS: "an isotonic (non-decreasing) fit", so advantages that fall with the statistic fit a flat line."""
    curve = fit_advantage_curve([0.1, 0.2, 0.3], [0.05, 0.03, 0.01], "isotonic_increasing")
    assert np.all(np.diff(curve["knot_advantages"]) >= 0)
    assert curve["knot_advantages"] == pytest.approx([0.03] * len(curve["knot_advantages"]))


# ---------------------------------------------------------------- the inversion


def test_a_line_is_inverted_with_its_intercept():
    """statistic_ceiling: the statistic "at which the fitted advantage reaches one_standard_error"."""
    statistics = [0.1, 0.2, 0.3]
    curve = fit_advantage_curve(statistics, [0.01 + 0.1 * value for value in statistics], "least_squares_line")
    assert curve["intercept"] == pytest.approx(0.01)
    result = statistic_ceiling(curve, 0.04)
    assert result["ceiling"] == pytest.approx(0.3) and curve["slope"] * result["ceiling"] + curve["intercept"] == pytest.approx(0.04)


def test_a_line_that_is_exactly_flat_gives_no_ceiling():
    """Module docstring: "a line that does not rise with the statistic" gives no finite ceiling."""
    result = statistic_ceiling(hand_made_line(slope=0.0, intercept=0.01), 0.02)
    assert result["ceiling"] is None and "does not rise" in result["status"]


def test_a_line_ceiling_at_either_end_of_the_observed_range_is_inside_it():
    """statistic_ceiling: "inside or outside the observed range (the flag says which)"; the range is the smallest and
    largest statistic observed, both of which are inside it."""
    curve = hand_made_line(slope=1.0, intercept=0.0, lowest=0.125, highest=0.375)
    assert statistic_ceiling(curve, 0.125) == {"ceiling": 0.125, "within_observed_range": True, "status": "ceiling"}
    assert statistic_ceiling(curve, 0.375) == {"ceiling": 0.375, "within_observed_range": True, "status": "ceiling"}
    assert statistic_ceiling(curve, 0.0625)["within_observed_range"] is False
    assert statistic_ceiling(curve, 0.5)["within_observed_range"] is False


def test_a_standard_error_that_is_not_a_number_is_refused():
    """statistic_ceiling: "one_standard_error must be a positive number"."""
    for curve in (hand_made_line(slope=0.1, intercept=0.0),
                  fit_advantage_curve([0.1, 0.2, 0.3], [0.0, 0.01, 0.03], "isotonic_increasing")):
        with pytest.raises(ValueError, match="positive number"):
            statistic_ceiling(curve, float("nan"))


def test_an_isotonic_fit_reaching_the_threshold_at_its_last_knot_gives_a_ceiling_inside_the_range():
    """Module docstring: no ceiling only for an isotonic fit "that never reaches the threshold over the observed range";
    one that reaches it exactly at the largest statistic reaches it there."""
    curve = fit_advantage_curve([0.1, 0.2], [0.0, 0.02], "isotonic_increasing")
    result = statistic_ceiling(curve, 0.02)
    assert result["status"] == "ceiling" and result["ceiling"] == pytest.approx(0.2) and result["within_observed_range"] is True


def test_an_isotonic_ceiling_is_flagged_inside_the_observed_range():
    """statistic_ceiling: an isotonic fit is inverted "only inside the observed range", so its flag is always True."""
    curve = fit_advantage_curve([0.1, 0.2, 0.3, 0.4], [0.0, 0.01, 0.03, 0.05], "isotonic_increasing")
    assert statistic_ceiling(curve, 0.02) == {"ceiling": pytest.approx(0.25), "within_observed_range": True, "status": "ceiling"}


def test_an_isotonic_plateau_at_the_threshold_puts_the_ceiling_where_the_plateau_starts():
    """statistic_ceiling: the statistic "at which the fitted advantage reaches one_standard_error", and the module
    docstring: a draw passes strictly below the ceiling "since the advantage must stay *below* one standard error".
    Pooling the falling pair (0.75, 0.5) gives a plateau at 0.625 from 0.3 to 0.4; at one standard error 0.625 the fit
    reaches it at 0.3, so a draw at 0.35, whose fitted advantage is one standard error, does not pass. (Added by the
    checker of 28 November 2026: the mutant reading the first knot strictly above the threshold, noted as equivalent,
    puts the ceiling at 0.4, the plateau's end.)"""
    curve = fit_advantage_curve([0.1, 0.2, 0.3, 0.4, 0.5], [0.0, 0.25, 0.75, 0.5, 1.0], "isotonic_increasing")
    assert curve["knot_statistics"] == pytest.approx([0.1, 0.2, 0.3, 0.4, 0.5])
    assert curve["knot_advantages"] == pytest.approx([0.0, 0.25, 0.625, 0.625, 1.0])
    assert statistic_ceiling(curve, 0.625) == {"ceiling": pytest.approx(0.3), "within_observed_range": True, "status": "ceiling"}
    assert draw_passes({"share": 0.35}, {"share": statistic_ceiling(curve, 0.625)["ceiling"]})[0] is False


# ---------------------------------------------------------------- acceptance


def test_a_statistic_of_minus_infinity_does_not_pass():
    """draw_passes: "a draw passes when every statistic named in ceilings is finite and strictly below its ceiling"."""
    passed, reasons = draw_passes({"share": float("-inf")}, {"share": 0.2})
    assert passed is False and reasons == ["share is not a finite number (-inf)"]


def test_a_numpy_integer_seed_is_a_whole_number():
    """validated_seed_order: "The real draw's seed order as a list of whole numbers"; a seed order read with numpy is one."""
    seeds = validated_seed_order(np.array([5, 2, 9]))
    assert seeds == [5, 2, 9] and all(type(seed) is int for seed in seeds)


def test_the_first_passing_seed_refuses_an_order_it_would_examine_twice():
    """first_passing_seed examines validated_seed_order's order: a repeat "would examine one draw twice", so it is
    refused before any seed is examined."""
    called = []

    def statistics_of_seed(seed):
        called.append(seed)
        return {"share": 0.9}

    with pytest.raises(ValueError, match="repeats a seed"):
        first_passing_seed([4, 4], statistics_of_seed, {"share": 0.3})
    with pytest.raises(ValueError, match="empty"):
        first_passing_seed([], statistics_of_seed, {"share": 0.3})
    assert called == []


# ---------------------------------------------------------------- the lineage the Reactome release is read through


def rewrite_summary(directory, name, **changes):
    summary = json.loads((directory / name).read_text())
    summary.update(changes)
    (directory / name).write_text(json.dumps(summary))
    return summary


def test_a_categorical_columns_zero_counts_are_not_counted_from_the_files(tmp_path):
    """_mismatches: a count per type is compared without the zero entries "which a categorical column's value_counts
    gives and the files do not"."""
    chain = registered_chain(tmp_path)
    nodes = pd.read_parquet(chain["neuronal"] / "nodes.parquet")
    nodes["node_type"] = pd.Categorical(nodes.node_type, categories=["gene", "metabolite", "protein", "reaction"])
    nodes.to_parquet(chain["neuronal"] / "nodes.parquet")
    assert (pd.read_parquet(chain["neuronal"] / "nodes.parquet").node_type.value_counts() == 0).any()  # the zero is there to drop
    assert reactome_release_of_graph(chain["neuronal"], relative_to=tmp_path)["reactome_release"] == "98"


def test_a_summary_that_records_no_key_the_check_reads_is_not_the_directorys_own(tmp_path):
    """_mismatches gives a sentence for a key "that the summary does not record"."""
    chain = registered_chain(tmp_path)
    summary = json.loads((chain["neuronal"] / "neuronal_variant_summary.json").read_text())
    del summary["edges_by_relation"]
    (chain["neuronal"] / "neuronal_variant_summary.json").write_text(json.dumps(summary))
    with pytest.raises(ValueError, match="does not describe this directory's graph files \\(it records no edges_by_relation\\)"):
        reactome_release_of_graph(chain["neuronal"], relative_to=tmp_path)


@pytest.mark.parametrize("graph, summary_name, key", [
    ("neuronal", "neuronal_variant_summary.json", "edges_by_relation"),
    ("split", "split_summary.json", "nodes_after"),
    ("split", "split_summary.json", "edges_after"),
    ("split_binders", "plasma_binder_summary.json", "nodes"),
    ("split_binders", "plasma_binder_summary.json", "edges_after"),
])
def test_each_record_a_summary_keeps_of_its_builders_output_is_checked(tmp_path, graph, summary_name, key):
    """A summary is a directory's own when "what it records of its builder's output matches the directory's graph
    files"; every key read for that (_own_output_mismatches) has to match, not only some of them."""
    chain = registered_chain(tmp_path)
    summary = json.loads((chain[graph] / summary_name).read_text())
    if isinstance(summary[key], dict):
        first = sorted(summary[key])[0]
        changed = {**summary[key], first: summary[key][first] + 1}
    else:
        changed = summary[key] + 1
    rewrite_summary(chain[graph], summary_name, **{key: changed})
    with pytest.raises(ValueError, match=f"{summary_name} does not describe this directory's graph files .*{key}"):
        reactome_release_of_graph(chain[graph], relative_to=tmp_path)


def test_a_drug_variant_whose_edges_changed_after_its_summary_is_refused(tmp_path):
    """The drug entry variant's own summary is checked by the digests of both graph files."""
    chain = registered_chain(tmp_path)
    edges = pd.read_parquet(chain["drugs_v5"] / "edges.parquet")
    edges.loc[0, "target_id"] = "N2"  # same rows, other content: only the digest sees it
    edges.to_parquet(chain["drugs_v5"] / "edges.parquet")
    with pytest.raises(ValueError, match="drug_entry_summary.json does not describe this directory's graph files .*edges_sha256"):
        reactome_release_of_graph(chain["drugs_v5"], relative_to=tmp_path)


def test_a_drug_variants_source_whose_nodes_changed_since_is_refused(tmp_path):
    """The drug entry variant's link to its source is checked by "the SHA-256 of the source's nodes.parquet and
    edges.parquet": a change to the nodes alone, which no row count of the source's own summary sees, is refused."""
    chain = registered_chain(tmp_path)
    nodes = pd.read_parquet(chain["split_binders"] / "nodes.parquet")
    nodes.loc[0, "node_id"] = "N99"
    nodes.to_parquet(chain["split_binders"] / "nodes.parquet")
    assert reactome_release_of_graph(chain["split_binders"], relative_to=tmp_path)["reactome_release"] == "98"  # its own lineage still holds
    with pytest.raises(ValueError, match="by the SHA-256 .*source_nodes_sha256"):
        reactome_release_of_graph(chain["drugs_v5"], relative_to=tmp_path)


def test_a_source_with_another_edge_is_refused_by_the_row_counts_its_derived_graph_recorded(tmp_path):
    """The split's and the binders' links are checked by the source's row counts, edges included."""
    chain = registered_chain(tmp_path)
    write_parquet_graph(chain["neuronal"], ["gene", "gene", "metabolite", "reaction"], ["catalyzes", "produces", "produces", "produces"])
    with pytest.raises(ValueError, match="by the source's row counts of nodes, edges and gene nodes .*its edges_before is 3 where the files give 4"):
        reactome_release_of_graph(chain["split"], relative_to=tmp_path)
    with pytest.raises(ValueError, match="by the source's row counts of nodes and edges .*its edges_before is 3 where the files give 4"):
        reactome_release_of_graph(chain["neuronal_binders"], relative_to=tmp_path)


def test_a_summary_file_that_is_not_a_json_object_is_passed_over(tmp_path):
    """_own_summary keeps reading when a file of GRAPH_BUILD_SUMMARIES is not JSON or not a JSON object: it is not the
    directory's own summary, and the directory's own one is still found."""
    chain = registered_chain(tmp_path)
    (chain["split"] / "plasma_binder_summary.json").write_text("not json {")
    (chain["split"] / "drug_entry_summary.json").write_text(json.dumps(["a", "list"]))
    found = reactome_release_of_graph(chain["split"], relative_to=tmp_path)
    assert found["reactome_release"] == "98" and [link["summary"] for link in found["lineage"]] == ["split_summary.json"]
    (chain["split"] / "split_summary.json").write_text("[]")
    with pytest.raises(ValueError, match="is not recorded.*plasma_binder_summary.json is not JSON.*is not a JSON object"):
        reactome_release_of_graph(chain["split"], relative_to=tmp_path)


def test_an_empty_recorded_source_is_an_unrecorded_lineage(tmp_path):
    """reactome_release_of_graph: a summary that "names no graph it was built from" is refused as such."""
    neuronal = build_neuronal(tmp_path)
    split = build_split(tmp_path, neuronal)
    rewrite_summary(split, "split_summary.json", graph_dir="")
    with pytest.raises(ValueError, match="names no graph it was built from"):
        reactome_release_of_graph(split, relative_to=tmp_path)
