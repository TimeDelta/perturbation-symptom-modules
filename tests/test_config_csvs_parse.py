"""Every CSV under configs/ parses with pandas and gives the rows csv.DictReader gives.

Added 24 October 2026 (decision 9.93) after configs/impc_symptom_crosswalk.csv held an unquoted comma in the note of
its self_injury row: pandas refused the file, and csv.DictReader read the row with an eighth field that it filed under
the key None, so the note lost its second half without an error and the fine crosswalk generated from it inherited the
truncation.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import pytest

CONFIG_DIRECTORY = Path(__file__).resolve().parents[1] / "configs"
CSV_PATHS = sorted(CONFIG_DIRECTORY.rglob("*.csv"))


@pytest.mark.parametrize("path", CSV_PATHS, ids=lambda path: str(path.relative_to(CONFIG_DIRECTORY)))
def test_config_csv_parses_the_same_with_pandas_and_dictreader(path: Path) -> None:
    table = pd.read_csv(path, dtype=str, keep_default_na=False)
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert all(None not in row for row in rows), f"{path.name}: a row has more fields than the header"
    assert len(rows) == len(table)
    if rows:
        assert list(rows[0].keys()) == list(table.columns)
    for index, row in enumerate(rows):
        assert {key: (value or "") for key, value in row.items()} == table.iloc[index].to_dict(), f"{path.name} row {index + 2}"


def test_there_are_config_csvs() -> None:
    assert len(CSV_PATHS) > 10
