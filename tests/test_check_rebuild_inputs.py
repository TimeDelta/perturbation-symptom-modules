"""The rebuild preflight: what the rebuild would skip, and which existing output is stale.

The two traps it guards, both of which have cost a build: a step whose output exists is skipped, so a rebuild on a
container holding earlier outputs keeps them and reports success (decision 9.106); and an output built before one of
its input tables was regenerated describes the old table while the skip rule keeps it (the BRENDA ordering of the
handoff of 26 October 2026, live again because decision 9.88's no-activation rule regenerates that table).
"""
import os
import subprocess
from pathlib import Path

import pytest

from experiments.check_rebuild_inputs import (
    GENERATORS_OF_TABLE,
    INPUTS_OF_OUTPUT,
    REBUILD_SCRIPT,
    REPOSITORY_ROOT,
    resolved_and_dynamic,
    newest_modification_time,
    stale_outputs,
    step_outputs,
    tables_behind_their_generator,
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
    assert (REPOSITORY_ROOT / input_name).exists(), input_name


def commit_file(root, path, text, when):
    """Write a file and commit it at a fixed time, so a test can order two commits without sleeping."""
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text)
    environment = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when,
                   "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.com",
                   "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.com"}
    subprocess.run(["git", "add", path], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", f"add {path}"], cwd=root, check=True, capture_output=True,
                   env=environment)


def test_a_table_committed_before_its_generator_is_reported(tmp_path):
    """The third trap of the preflight: the derived BRENDA table is committed, not built, so neither of the other two
    checks looks at it, and on 2 November 2026 it held none of decision 9.88's no-activation rule."""
    table, generators = GENERATORS_OF_TABLE[0]
    generator = generators[0]
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    commit_file(tmp_path, table, "the derived table\n", "2026-11-01T00:00:00+00:00")
    commit_file(tmp_path, generator, "the generator, changed after the table\n", "2026-11-02T00:00:00+00:00")
    assert tables_behind_their_generator(tmp_path) == [(table, generator)]

    # the ordinary case, the table regenerated after the change, reports nothing
    commit_file(tmp_path, table, "the derived table, regenerated\n", "2026-11-03T00:00:00+00:00")
    assert tables_behind_their_generator(tmp_path) == []


def test_a_table_git_knows_nothing_of_is_not_reported(tmp_path):
    """An untracked table, or a clone too shallow to hold its commit, gives no commit time; the guard says nothing
    rather than guessing, because a false report here would send an operator to regenerate a current table."""
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    commit_file(tmp_path, "unrelated.txt", "so the repository has a commit\n", "2026-11-01T00:00:00+00:00")
    assert tables_behind_their_generator(tmp_path) == []


@pytest.mark.parametrize("named", [name for table, generators in GENERATORS_OF_TABLE
                                   for name in (table, *generators)])
def test_every_table_and_generator_the_guard_names_exists(named):
    """CLAUDE.md: a comment that names a file names one that exists. A rename not carried here would stop the guard
    watching anything, silently."""
    from experiments.check_rebuild_inputs import REPOSITORY_ROOT

    assert (REPOSITORY_ROOT / named).exists(), named


def test_the_brenda_stage_regenerates_the_table_the_neuronal_step_reads():
    """The sequencing the handoff of 26 October 2026 named, now in the script rather than in a note: the stage runs the
    extraction and the mapping, maps against the split graph, and tells the operator what to rebuild when the table
    changes. Before 2 November 2026 none of these commands was in any script."""
    script_text = Path(REBUILD_SCRIPT).read_text()
    assert 'if [ "$stage" = "brenda" ]; then' in script_text
    brenda_stage = script_text.split('if [ "$stage" = "brenda" ]; then', 1)[1]
    for required in ("experiments/extract_brenda_enzyme_regulation.py",
                     "experiments/map_brenda_regulation_to_graph.py",
                     "graph_full_neuronal_split",
                     "configs/brenda_metabolite_enzyme_regulation.csv",
                     "configs/brenda_metabolite_enzyme_no_activation.csv"):
        assert required in brenda_stage, required
    # the stage must not delete the downstream graphs itself; it prints what to delete and leaves the choice
    assert "rm -rf" in brenda_stage and "DOWNSTREAM" in brenda_stage
