"""The rebuild preflight: what the rebuild would skip, and which existing output is stale.

The two traps it guards, both of which have cost a build: a step whose output exists is skipped, so a rebuild on a
container holding earlier outputs keeps them and reports success (decision 9.106); and an output built before one of
its input tables was regenerated describes the old table while the skip rule keeps it (the BRENDA ordering of the
handoff of 26 October 2026, live again because decision 9.88's no-activation rule regenerates that table).
"""
import os

import pytest

from experiments.check_rebuild_inputs import (
    INPUTS_OF_OUTPUT,
    resolved_and_dynamic,
    newest_modification_time,
    stale_outputs,
    step_outputs,
)

REBUILD_SCRIPT = "scripts/rebuild_data_layer.sh"


def write_rebuild_script(root, *output_paths):
    """A rebuild script of the shape the real one has, with one step per output."""
    lines = ['#!/bin/bash', 'set -uo pipefail', 'processed="data/processed"']
    for output in output_paths:
        lines.append(f'step "{output}" "a step" python experiments/some_script.py')
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / REBUILD_SCRIPT).write_text("\n".join(lines) + "\n")


def test_the_step_outputs_are_read_with_the_scripts_own_variables_expanded():
    outputs = step_outputs('processed="data/processed"\n'
                           'step "$processed/graph_neuronal/nodes.parquet" "the graph" python x.py\n'
                           '  step "${processed}/evidence/records.parquet" "indented" python y.py\n'
                           'echo step not-a-step\n')
    assert outputs == ["data/processed/graph_neuronal/nodes.parquet", "data/processed/evidence/records.parquet"]


def test_the_real_rebuild_scripts_steps_are_all_read():
    """A guard on the parser itself: if the script's step lines change shape, this fails rather than silently
    reporting fewer steps than the rebuild has."""
    from pathlib import Path

    from experiments.check_rebuild_inputs import REBUILD_SCRIPT as real_script

    outputs = step_outputs(Path(real_script).read_text())
    resolved, dynamic = resolved_and_dynamic(outputs)
    assert len(outputs) > 50, len(outputs)
    assert all(output.startswith(("data/raw/", "data/processed/")) for output in resolved), resolved
    # the only paths the parser may leave unresolved are the ones the rebuild builds at run time, from a function
    # argument or a loop variable; anything else means a variable assignment was added and SHELL_VARIABLES not updated,
    # which would silently shrink what the guard covers
    assert sorted(dynamic) == sorted([
        "data/processed/onsides_v3$suffix/onsides_reports.parquet",
        "data/processed/evidence_full_v3$suffix/evidence_records.parquet",
        "data/processed/label_selection/better_v2_full_v3$suffix.parquet",
        "data/processed/$graph/edge_evidence.parquet",
    ]), dynamic


def test_an_output_older_than_an_input_that_builds_it_is_stale(tmp_path):
    marker, inputs = INPUTS_OF_OUTPUT[0]
    input_name = inputs[0]
    output = f"data/processed/graph_{marker}_v5/nodes.parquet"
    write_rebuild_script(tmp_path, "$processed/" + output.split("data/processed/", 1)[1])

    (tmp_path / output).parent.mkdir(parents=True)
    (tmp_path / output).write_text("built")
    (tmp_path / input_name).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / input_name).write_text("regenerated after the build")
    os.utime(tmp_path / output, (1_000, 1_000))
    os.utime(tmp_path / input_name, (2_000, 2_000))

    assert stale_outputs(tmp_path) == [(output, input_name)]

    # the same pair with the output written after the input is not stale, which is the ordinary case
    os.utime(tmp_path / output, (3_000, 3_000))
    assert stale_outputs(tmp_path) == []


def test_an_output_that_does_not_exist_is_not_stale(tmp_path):
    marker, inputs = INPUTS_OF_OUTPUT[0]
    write_rebuild_script(tmp_path, f"$processed/graph_{marker}_v5/nodes.parquet")
    (tmp_path / inputs[0]).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / inputs[0]).write_text("an input with no build yet")
    assert stale_outputs(tmp_path) == []


def test_an_outputs_time_is_the_newest_file_in_its_tree(tmp_path):
    """A built graph is a directory and the step checks for one file inside it, so the directory's own time is not
    what changed when it was written."""
    directory = tmp_path / "graph"
    directory.mkdir()
    (directory / "nodes.parquet").write_text("a")
    (directory / "edges.parquet").write_text("b")
    os.utime(directory / "nodes.parquet", (1_000, 1_000))
    os.utime(directory / "edges.parquet", (5_000, 5_000))
    os.utime(directory, (1_000, 1_000))
    assert newest_modification_time(directory) == 5_000
    assert newest_modification_time(directory / "nodes.parquet") == 1_000


@pytest.mark.parametrize("input_name", [name for _, names in INPUTS_OF_OUTPUT for name in names])
def test_every_input_the_guard_names_exists(input_name):
    """CLAUDE.md: a comment that names a file names one that exists. These are the tables the guard watches, so a
    rename that is not carried here would silently stop the guard watching anything."""
    from experiments.check_rebuild_inputs import REPOSITORY_ROOT

    assert (REPOSITORY_ROOT / input_name).exists(), input_name
