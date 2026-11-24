"""A run records the weighting its evidence table was assembled with (experiments/run_main_model.py,
evidence_weighting_of), so a weighted run shows whether it read the registered reliability weights or the grade
weights of the fixed_grades arm (amendment item 12d; decision 8.5, 24 November 2026)."""
from __future__ import annotations

import pandas as pd
import pytest

from experiments.run_main_model import evidence_weighting_of


def write_records(directory, frame: pd.DataFrame):
    directory.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(directory / "evidence_records.parquet")
    return directory


def test_the_weighting_column_is_read_and_a_table_without_it_is_none(tmp_path):
    assert evidence_weighting_of(write_records(tmp_path / "reliability", pd.DataFrame({"pair": [1, 2], "weighting": ["reliability", "reliability"]}))) == "reliability"
    assert evidence_weighting_of(write_records(tmp_path / "grade", pd.DataFrame({"pair": [1], "weighting": ["grade"]}))) == "grade"
    assert evidence_weighting_of(write_records(tmp_path / "old", pd.DataFrame({"pair": [1]}))) is None


def test_a_table_mixing_two_weightings_is_refused(tmp_path):
    with pytest.raises(ValueError, match="one value on every row"):
        evidence_weighting_of(write_records(tmp_path / "mixed", pd.DataFrame({"pair": [1, 2], "weighting": ["grade", "reliability"]})))
