"""Decision 9.81's counts before amendment item 37's saturation is built (experiments/measure_saturation_counts.py), on
small synthetic graphs whose answers are known by hand."""
from __future__ import annotations

import argparse
import itertools

import numpy as np
import pytest

from experiments.measure_saturation_counts import (
    FLAG_LIMIT,
    cone_reach_summary,
    finished_tally,
    new_firing_tally,
    operator_excess,
    parse_arguments,
    parse_ceiling,
    read_headroom_table,
    refuse_output_under_data,
    seed_count_summary,
    signed_cycle_counts,
    signed_edges,
    tally_firing,
    DATA_DIRECTORY,
)


def cycles(edges, num_nodes, max_length, **flags):
    source, target, sign = zip(*edges) if edges else ((), (), ())
    return signed_cycle_counts(num_nodes, list(source), list(target), list(sign), max_length, **flags)


def test_a_triangle_with_one_negative_edge_is_one_negative_cycle_of_length_three():
    result = cycles([(0, 1, 1), (1, 2, 1), (2, 0, -1)], 3, 3)
    assert result["by_length"][3] == {"positive": 0, "negative": 1}
    assert result["by_length"][2] == {"positive": 0, "negative": 0}
    assert result["strongly_connected_components"]["largest"] == 3


def test_two_negative_edges_make_a_positive_cycle_and_a_mutual_pair_is_a_cycle_of_length_two():
    result = cycles([(0, 1, -1), (1, 0, -1), (1, 2, 1), (2, 1, 1)], 3, 3)
    assert result["by_length"][2] == {"positive": 2, "negative": 0}
    assert result["by_length"][3] == {"positive": 0, "negative": 0}


def test_a_pair_with_both_signs_gives_two_cycles_and_repeated_edges_one():
    result = cycles([(0, 1, 1), (0, 1, -1), (0, 1, 1), (1, 0, 1)], 2, 2)
    assert result["by_length"][2] == {"positive": 1, "negative": 1}
    assert result["ordered_pairs_with_both_signs"] == 1 and result["distinct_signed_edges"] == 3


def test_the_length_bound_is_respected_and_a_self_loop_is_counted_apart():
    square = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1), (2, 2, -1)]
    assert cycles(square, 4, 3)["by_length"][3] == {"positive": 0, "negative": 0}
    bounded = cycles(square, 4, 4)
    assert bounded["by_length"][4] == {"positive": 1, "negative": 0}
    assert bounded["self_loops"] == {"positive": 0, "negative": 1}
    with pytest.raises(ValueError):
        cycles(square, 4, 1)


def test_cycles_through_a_flagged_node_or_edge_are_counted_apart():
    # a figure eight through node 0: 0-1-0 positive, 0-2-3-0 negative; the edge 2->3 flagged
    edges = [(0, 1, 1), (1, 0, 1), (0, 2, 1), (2, 3, -1), (3, 0, 1)]
    flag = np.array([False, False, False, True, False])
    result = cycles(edges, 4, 3, node_flags={"one": [1], "zero": [0]}, edge_flags={"the_edge": flag})
    assert result["by_length"][2]["positive"] == 1 and result["by_length"][3]["negative"] == 1
    assert result["by_length"][2]["positive_through_one"] == 1 and result["by_length"][3]["negative_through_one"] == 0
    assert result["by_length"][2]["positive_through_zero"] == 1 and result["by_length"][3]["negative_through_zero"] == 1
    assert result["by_length"][3]["negative_through_the_edge"] == 1 and result["by_length"][2]["positive_through_the_edge"] == 0


def test_an_edge_without_a_sign_is_refused():
    with pytest.raises(ValueError, match="\\+1 or -1"):
        cycles([(0, 1, 0), (1, 0, 1)], 2, 2)


def test_the_counts_match_networkx_on_random_signed_graphs():
    networkx = pytest.importorskip("networkx")
    rng = np.random.default_rng(7)
    for trial in range(6):
        num_nodes = 9
        pairs = [(u, v) for u, v in itertools.permutations(range(num_nodes), 2) if rng.random() < 0.3]
        edges = [(u, v, int(rng.choice([-1, 1]))) for u, v in pairs]
        result = cycles(edges, num_nodes, 5)
        graph = networkx.DiGraph()
        graph.add_nodes_from(range(num_nodes))
        sign_of = {}
        for u, v, s in edges:
            graph.add_edge(u, v)
            sign_of[(u, v)] = s
        expected = {length: {"positive": 0, "negative": 0} for length in range(2, 6)}
        for cycle in networkx.simple_cycles(graph, length_bound=5):
            if len(cycle) < 2:
                continue
            product = np.prod([sign_of[(cycle[i], cycle[(i + 1) % len(cycle)])] for i in range(len(cycle))])
            expected[len(cycle)]["positive" if product > 0 else "negative"] += 1
        assert {length: {key: result["by_length"][length][key] for key in ("positive", "negative")} for length in range(2, 6)} == expected, trial


def test_signed_edges_leaves_out_unsigned_relations_sign_zero_and_silent_sources():
    import pandas as pd

    edges = pd.DataFrame({"source": [0, 0, 1, 2, 2], "target": [1, 2, 2, 0, 1], "relation": [0, 1, 0, 0, 0], "sign": [1.0, 1.0, 0.0, -0.5, 1.0]})
    kept, left_out = signed_edges(edges, ["activates", "binds"], ("binds",), np.array([False, False, False]))
    assert kept[["source", "target"]].values.tolist() == [[0, 1], [2, 0], [2, 1]] and kept.sign.tolist() == [1.0, -1.0, 1.0]
    assert left_out == {"edges_of_unsigned_relations": 1, "edges_of_sign_0": 1, "edges_from_non_propagating_nodes": 0}
    _, silent = signed_edges(edges, ["activates", "binds"], ("binds",), np.array([False, False, True]))
    assert silent["edges_from_non_propagating_nodes"] == 2


def test_seed_counts_by_type_with_their_histogram():
    summary = seed_count_summary([1, 3, 1, 2], ["gene", "drug", "drug", "allele"])
    assert summary["more_than_one_seed"] == 2 and summary["more_than_one_seed_by_type"] == {"allele": 1, "drug": 1}
    assert summary["seed_count_histogram"] == {1: 2, 2: 1, 3: 1}
    with pytest.raises(ValueError):
        seed_count_summary([1], ["gene", "drug"])


def test_the_floor_and_a_sourced_ceiling_fire_where_the_state_crosses_them_and_pairs_split_by_place():
    state = np.array([[-1.5, -0.2, 2.0, 0.9], [0.1, -1.01, 0.3, 4.0]])
    excess = operator_excess(state, {2: 1.5, 3: 3.0})
    assert (excess["floor"] > 0).tolist() == [[True, False, False, False], [False, True, False, False]]
    assert (excess["ceiling"] > 0).tolist() == [[False, False, True, False], [False, False, False, True]]
    assert set(operator_excess(state, None)) == {"floor"}  # --ceiling none counts the floor alone
    seeds = np.array([[True, False, False, False], [False, False, False, False]])
    targets = np.array([[False, False, True, False], [False, True, False, False]])
    tally = new_firing_tally()
    tally_firing(tally, excess["floor"], seeds, targets, np.array(["gene", "protein", "reaction", "metabolite"], dtype=object), ["p1", "p2"])
    assert (tally["pairs"], tally["pairs_at_seeds"], tally["pairs_at_mechanism_targets"], tally["pairs_beyond_seeds_and_targets"]) == (2, 1, 1, 0)
    ceiling = new_firing_tally()
    tally_firing(ceiling, excess["ceiling"], seeds, targets, np.array(["gene", "protein", "reaction", "metabolite"], dtype=object), ["p1", "p2"])
    assert ceiling["pairs_at_mechanism_targets"] == 1 and ceiling["pairs_beyond_seeds_and_targets"] == 1
    assert ceiling["perturbations_firing_beyond_seeds_and_targets"] == [["p2", 1]]


def test_a_pair_firing_by_less_than_the_loops_tolerance_is_counted_apart_from_one_firing_by_more():
    """Most of the floor's 213 pairs on the 12 November build sit within 1e-6 of -1, inside the loop's own
    fixed_point_tolerance of 1e-3, so the count at the limit alone would read as a fact about the graph."""
    state = np.array([[-1.0 - 1e-7, -1.0 - 2e-3, -0.5]])
    excess = operator_excess(state, None)["floor"]
    tally = new_firing_tally((0.0, 1e-6, 1e-3))
    tally_firing(tally, excess, np.zeros(state.shape, dtype=bool), np.zeros(state.shape, dtype=bool),
                 np.array(["gene", "gene", "gene"], dtype=object), ["p1"])
    assert tally["pairs"] == 2 and tally["pairs_above_margin"] == {"0": 2, "1e-06": 1, "0.001": 1}
    assert tally["largest_excess"] == pytest.approx(2e-3)
    assert finished_tally(tally, ["a", "b", "c"])["margins"] == [0.0, 1e-6, 1e-3]
    empty = new_firing_tally()
    tally_firing(empty, operator_excess(np.array([[0.0, 0.5]]), None)["floor"], np.zeros((1, 2), dtype=bool),
                 np.zeros((1, 2), dtype=bool), np.array(["gene", "gene"], dtype=object), ["p1"])
    assert empty["pairs"] == 0 and empty["largest_excess"] == 0.0 and set(empty["pairs_above_margin"].values()) == {0}


def test_the_ceiling_takes_a_uniform_stand_in_a_sourced_table_or_none(tmp_path):
    """The sourced headroom tables are item 37's [P 13] and do not exist, so --ceiling also takes the stand-in the
    scratch measurement of 16 November 2026 used; the record says it is not sourced."""
    assert parse_ceiling("none") == ("none", None)
    assert parse_ceiling("uniform:1") == ("uniform", 1.0)
    table = tmp_path / "headroom.csv"
    table.write_text("node_id,headroom\nB,3.3\n")
    assert parse_ceiling(str(table)) == ("table", table)
    for text in ("uniform:0", "uniform:-1", "uniform:nan", str(tmp_path / "absent.csv"), "1.5"):
        with pytest.raises(argparse.ArgumentTypeError):
            parse_ceiling(text)


def test_more_flags_than_one_int64_word_holds_are_refused_by_name():
    """Each node and edge flag takes one bit of the int64 word carried along a path, so past FLAG_LIMIT the shift
    overflows; the refusal names the count rather than letting numpy raise."""
    edges = [(0, 1, 1.0), (1, 0, 1.0)]
    full = cycles(edges, 2, 2, node_flags={f"f{bit}": [0] for bit in range(FLAG_LIMIT)})
    assert full["by_length"][2]["positive"] == 1 and full["by_length"][2][f"positive_through_f{FLAG_LIMIT - 1}"] == 1
    with pytest.raises(ValueError, match=f"more than the {FLAG_LIMIT}"):
        cycles(edges, 2, 2, node_flags={f"f{bit}": [0] for bit in range(FLAG_LIMIT + 1)})
    with pytest.raises(ValueError, match=f"more than the {FLAG_LIMIT}"):
        cycles(edges, 2, 2, node_flags={f"f{bit}": [0] for bit in range(FLAG_LIMIT)},
               edge_flags={"an_edge": np.array([True, False])})


def test_the_headroom_table_refuses_an_unknown_node_a_repeat_and_a_headroom_that_fires_at_rest(tmp_path):
    path = tmp_path / "headroom.csv"
    path.write_text("node_id,headroom\nB,3.3\n")
    assert read_headroom_table(path, ["A", "B"]) == {1: 3.3}
    for text, message in (("node_id,headroom\nC,1\n", "not a node"), ("node_id,headroom\nA,1\nA,2\n", "twice"),
                          ("node_id,headroom\nA,0\n", "not a positive"), ("node_id,headroom\nA,nan\n", "not a positive"),
                          ("node,headroom\nA,1\n", "columns")):
        path.write_text(text)
        with pytest.raises(ValueError, match=message):
            read_headroom_table(path, ["A", "B"])


def test_cones_reaching_a_node_set_by_type_with_their_sizes():
    reached = np.array([[1, 0, 1], [0, 0, 1], [1, 1, 0]], dtype=bool)  # [nodes, columns]
    summary = cone_reach_summary(reached, ["gene", "drug", "drug"], {"protons": [1], "membrane": [2]})
    assert summary["reach_protons"] == 1 and summary["reach_membrane"] == 2
    assert summary["by_perturbation_type"]["drug"] == {"columns": 2, "reach_protons": 1, "reach_membrane": 1}
    assert summary["cone_size"]["maximum"] == 2 and summary["cone_size"]["minimum"] == 1


def test_the_choices_no_ruling_settles_are_required_and_the_output_stays_out_of_data(tmp_path):
    required = ["--graph-dir", "g", "--evidence-dir", "e", "--gains", "init", "--ceiling", "none", "--cycle-edges", "stored",
                "--max-cycle-length", "3", "--output", str(tmp_path / "counts.json")]
    assert parse_arguments(required).gains == ("init", None) and parse_arguments(required).ceiling == ("none", None)
    for flag in ("--gains", "--ceiling", "--cycle-edges", "--max-cycle-length"):
        position = required.index(flag)
        with pytest.raises(SystemExit):
            parse_arguments(required[:position] + required[position + 2:])
    assert parse_arguments(required[:5] + ["fixed:0.5"] + required[6:]).gains == ("fixed", 0.5)
    with pytest.raises(SystemExit):
        parse_arguments(required[:5] + ["fixed:1.5"] + required[6:])
    with pytest.raises(ValueError, match="outside data"):
        refuse_output_under_data(DATA_DIRECTORY / "processed" / "counts.json")
    refuse_output_under_data(tmp_path / "counts.json")


def test_the_output_guard_refuses_the_data_directory_a_link_inside_it_points_into(tmp_path, monkeypatch):
    """A worktree links data/raw and data/processed into the main checkout's data/, so that data/ and the children it
    does not link (data/brenda, data/releases) are refused too, not only the link's own target."""
    import experiments.measure_saturation_counts as module

    checkout, worktree = tmp_path / "checkout" / "data", tmp_path / "worktree" / "data"
    (checkout / "raw").mkdir(parents=True)
    (checkout / "brenda").mkdir()
    worktree.mkdir(parents=True)
    (worktree / "raw").symlink_to(checkout / "raw")
    monkeypatch.setattr(module, "DATA_DIRECTORY", worktree)
    for refused in (worktree / "counts.json", worktree / "raw" / "counts.json", checkout / "counts.json",
                    checkout / "raw" / "counts.json", checkout / "brenda" / "counts.json"):
        with pytest.raises(ValueError, match="outside data"):
            module.refuse_output_under_data(refused)
    module.refuse_output_under_data(tmp_path / "counts.json")  # beside both, not under either
    module.refuse_output_under_data(tmp_path / "checkout" / "counts.json")
