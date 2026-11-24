"""Decision 8.5 from the rebuild's side: the class is built behind `--open-targets-scoped-rows`, and until 24
November 2026 `scripts/rebuild_data_layer.sh` passed the flag to none of its assembler calls, built the table the
flag names in no step, and no script fetched the curation that table is made from. The assembler also treated a path
that did not exist as no path, so a build that asked for the class and one that got it looked the same. These tests
hold each link of that chain.
"""
import re
from pathlib import Path

import pytest

from mechanistic_pathway_learning.evidence import assemble_evidence_table

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REBUILD_SCRIPT = (REPOSITORY_ROOT / "scripts" / "rebuild_data_layer.sh").read_text()
FETCH_SCRIPT = (REPOSITORY_ROOT / "scripts" / "fetch_raw_sources.sh").read_text()
ROWS_PATH = "$processed/off_target_scoping/open_targets_symptom_rows.parquet"


def commands(script_text: str) -> list[str]:
    """The script's commands with their continuation lines joined, comments left out."""
    joined = re.sub(r"\\\n", " ", script_text)
    return [line.strip() for line in joined.splitlines() if line.strip() and not line.strip().startswith("#")]


def assembler_calls() -> dict[str, str]:
    """output directory -> the assembler command that writes it."""
    calls = {}
    for command in commands(REBUILD_SCRIPT):
        if "assemble_evidence_table" in command:
            calls[re.search(r'--output-dir "([^"]+)"', command).group(1)] = command
    return calls


def test_the_registered_tables_are_assembled_with_the_class():
    calls = assembler_calls()
    for output_directory in ("$processed/evidence_full_v4", "$processed/evidence_full_v5"):
        assert '--open-targets-scoped-rows "$open_targets_rows"' in calls[output_directory], output_directory
    assert f'open_targets_rows="{ROWS_PATH}"' in commands(REBUILD_SCRIPT)


def test_the_v3_reproductions_are_assembled_without_it():
    """They reproduce builds that predate the decision of 13 October 2026; the preregistration enters the class "at
    the v4 rebuild"."""
    assert "--open-targets-scoped-rows" not in assembler_calls()["$processed/evidence_full_v3$suffix"]


def test_the_table_the_flag_names_is_built_before_the_first_assembler_call_that_reads_it():
    script_commands = commands(REBUILD_SCRIPT)
    build_step = next(index for index, command in enumerate(script_commands)
                      if command.startswith(f'step "{ROWS_PATH}"') and "scope_open_targets_symptom_labels.py" in command)
    first_reader = next(index for index, command in enumerate(script_commands) if "--open-targets-scoped-rows" in command)
    assert build_step < first_reader
    assert f'--rows-output "$open_targets_rows"' in script_commands[build_step]


def test_the_curation_the_table_is_made_from_is_fetched_at_a_pinned_commit_and_hash():
    from experiments.scope_open_targets_symptom_labels import ADVERSE_EFFECTS, SECONDARY_PHARMACOLOGY

    fetches = [command for command in commands(FETCH_SCRIPT) if command.startswith("fetch ") and "opentargets_curation" in command]
    assert len(fetches) == 2
    for path in (ADVERSE_EFFECTS, SECONDARY_PHARMACOLOGY):
        fetch = next(command for command in fetches if f"$raw_directory/opentargets_curation/{path.name}" in command)
        assert path.as_posix() == f"data/raw/opentargets_curation/{path.name}"
        assert re.fullmatch(r"[0-9a-f]{64}", fetch.split()[-1]), "the fetch carries no SHA-256 pin"
    assert re.search(r'open_targets_curation_url="https://raw\.githubusercontent\.com/opentargets/curation/[0-9a-f]{40}/target_safety"', FETCH_SCRIPT)


def test_a_scoped_rows_path_that_does_not_exist_is_an_error_and_not_a_table_without_the_class(tmp_path):
    """Raised before anything is read, so none of the other arguments needs to exist."""
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError, match="open_targets_scoped_rows_path"):
        assemble_evidence_table.assemble(missing, missing, missing, missing, missing, missing,
                                         open_targets_scoped_rows_path=tmp_path / "open_targets_symptom_rows.parquet")
