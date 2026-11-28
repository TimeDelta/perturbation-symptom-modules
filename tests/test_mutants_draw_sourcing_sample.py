"""Tests added on 28 November 2026 to kill mutants of experiments/draw_sourcing_sample.py that
tests/test_sourcing_sample.py lets survive (hand-made mutation testing; the mutants and which test kills each are listed
in the working report of the session of 28 November 2026, which is outside the repository). Synthetic tables only: no real held-out set is read and nothing real is drawn."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from mechanistic_pathway_learning.evaluation.research_strata_and_eras import write_cells, write_record
from tests.test_sourcing_sample import CHOICES, command_arguments, held_out_set, synthetic_cells, write_inputs

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from draw_sourcing_sample import main as draw_sourcing_sample_main  # noqa: E402


@pytest.fixture(scope="module")
def cells():
    return synthetic_cells()


@pytest.mark.parametrize("existing", ["sample.csv", "sample.json", "sample.json.sha256"])
def test_each_output_that_exists_stops_the_command_before_it_writes(tmp_path, cells, existing):
    """The docstring: it writes two files and a sidecar, "refusing to overwrite either, since a sample drawn is not
    redrawn"; any one of them already there is refused, and nothing is written."""
    inputs = write_inputs(tmp_path / "inputs", cells)
    (tmp_path / existing).write_text("drawn before")
    with pytest.raises(SystemExit, match="not overwritten"):
        draw_sourcing_sample_main(command_arguments(inputs, tmp_path))
    assert sorted(path.name for path in tmp_path.iterdir() if path.is_file()) == [existing]
    assert (tmp_path / existing).read_text() == "drawn before"


def test_no_label_selection_is_given_as_none(tmp_path, cells):
    """--label-selection: "the label selection parquet, or none"; the record then names no label selection."""
    inputs = write_inputs(tmp_path / "inputs", cells)
    held_out = {**held_out_set(cells), "evidence_records_sha256": inputs["evidence_records_sha256"], "label_selection_sha256": None}
    inputs["held_out"].write_text(json.dumps(held_out))
    write_record({"evidence_records_sha256": inputs["evidence_records_sha256"], "label_selection_sha256": None,
                  "cells_sha256": write_cells(cells, inputs["cells"])}, inputs["record"])
    arguments = command_arguments(inputs, tmp_path)
    arguments[arguments.index("--label-selection") + 1] = "none"
    draw_sourcing_sample_main(arguments)
    record = json.loads((tmp_path / "sample.json").read_text())
    assert record["label_selection"] is None and record["held_out_set"]["label_selection_sha256"] is None
    assert record["rule"]["seed"] == CHOICES["seed"]
