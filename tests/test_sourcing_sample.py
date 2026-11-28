"""The sourcing sample of decision 9.134 as amendment item 38 (g) draws it (mechanistic_pathway_learning/evaluation/
sourcing_sample.py, experiments/draw_sourcing_sample.py), on synthetic tables only: no real held-out set is read and
nothing real is drawn. The strata and eras are made by research_strata_and_eras.assign_strata_and_eras, as the
sample's real input will be."""
from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mechanistic_pathway_learning.evaluation.research_strata_and_eras import (
    assign_strata_and_eras, file_sha256, validated_cell_search_table, write_cells, write_record)
from mechanistic_pathway_learning.evaluation.sourcing_sample import (
    DRAW_ORDERS, ERA_READINGS, QUOTA_UNITS, SAMPLE_SIZE_PER_STRATUM, STRATUM_READINGS, draw_sourcing_sample,
    draw_sourcing_sample_from_files, held_out_perturbation_ids)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from draw_sourcing_sample import main as draw_sourcing_sample_main  # noqa: E402

EVIDENCE, SELECTION = "e" * 64, "s" * 64
SYMPTOMS = ("anxiety", "fatigue", "insomnia", "psychosis")


def synthetic_cells(num_per_type=150, seed=0) -> pd.DataFrame:
    """Every cell of a scored table of genes, drugs and a few combinations with its strata and eras. Genes are mostly
    none, so they take none, fewer and more; drugs mostly have a record, so they take tertiles, whose lower third holds
    the cells with no record; the combinations, binned as a type of their own, give quota cells of fewer than 20. A few
    cells were not searched, with a reason."""
    rng = np.random.default_rng(seed)
    scored, search = [], []
    for kind, prefix, none_share, number in (("gene", "g", 0.6, num_per_type), ("drug", "d", 0.2, num_per_type), ("combination", "c", 0.2, 12)):
        for index in range(number):
            perturbation_id = f"{prefix}{index:03d}"
            for symptom in SYMPTOMS:
                scored.append({"perturbation_id": perturbation_id, "symptom": symptom, "perturbation_type": kind,
                               "kept_positive": bool(rng.random() < 0.45), "set_aside_by_label_selection": False,
                               "registered_date_ordinal": 0})
                row = {"perturbation_id": perturbation_id, "symptom": symptom, "search_status": "searched",
                       "record_count": 0, "earliest_record_year": None, "not_searched_reason": ""}
                if rng.random() < 0.03:
                    row.update(search_status="not_searched", record_count=None, not_searched_reason="refused twice")
                elif rng.random() >= none_share:
                    row.update(record_count=int(rng.integers(1, 300)), earliest_record_year=int(rng.integers(1950, 2025)))
                search.append(row)
    cells, _ = assign_strata_and_eras(validated_cell_search_table(pd.DataFrame(search)), pd.DataFrame(scored))
    return cells


def held_out_set(cells: pd.DataFrame, every=7, **overrides) -> dict:
    perturbations = sorted(set(cells.perturbation_id))
    return {"group_by": "disease_cluster_and_targets", "evidence_records_sha256": EVIDENCE, "label_selection_sha256": SELECTION,
            "perturbation_ids": perturbations[::every], **overrides}


CHOICES = {"seed": 11, "quota_unit": "crossed", "stratum_reading": "research_stratum", "era_reading": "first_record_era_thirds",
           "draw_order": "one_generator_in_quota_order"}


def draw(cells, held_out=None, **changes):
    return draw_sourcing_sample(cells, held_out if held_out is not None else held_out_set(cells), evidence_records_sha256=EVIDENCE,
                                label_selection_sha256=SELECTION, **{**CHOICES, **changes})


@pytest.fixture(scope="module")
def cells():
    return synthetic_cells()


# ---------------------------------------------------------------- what is drawn


@pytest.mark.parametrize("quota_unit", QUOTA_UNITS)
@pytest.mark.parametrize("draw_order", DRAW_ORDERS)
def test_only_labelled_development_cells_with_a_counted_record_are_drawn_up_to_twenty_per_quota_cell(cells, quota_unit, draw_order):
    held_out = held_out_set(cells)
    sample, record = draw(cells, held_out, quota_unit=quota_unit, draw_order=draw_order)
    joined = sample.merge(cells, on=["perturbation_id", "symptom"], suffixes=("", "_of_cell"), validate="many_to_one")
    assert not joined.perturbation_id.isin(held_out["perturbation_ids"]).any()
    assert joined.kept_positive.all() and (joined.record_count > 0).all()
    assert (joined.stratum == joined.research_stratum).all() and (joined.era == joined.first_record_era_thirds).all()
    drawn_per_quota_cell = sample.quota_cell.value_counts()
    for quota in record["quota_cells"]:
        assert quota["drawn"] == min(SAMPLE_SIZE_PER_STRATUM, quota["candidates"]) == drawn_per_quota_cell.get(quota["quota_cell"], 0)
        assert quota["all_candidates_drawn"] == (quota["candidates"] <= SAMPLE_SIZE_PER_STRATUM)
        assert quota["candidates"] + quota["without_a_counted_record"] == quota["labelled_development_cells"]
    # the synthetic table exercises the cap, the all-of-them rule and quota cells with nothing to read
    assert any(quota["candidates"] > SAMPLE_SIZE_PER_STRATUM for quota in record["quota_cells"])
    assert any(0 < quota["candidates"] <= SAMPLE_SIZE_PER_STRATUM for quota in record["quota_cells"])
    assert any(quota["candidates"] == 0 and quota["without_a_counted_record"] > 0 for quota in record["quota_cells"])
    development = cells[~cells.perturbation_id.isin(held_out["perturbation_ids"]) & cells.kept_positive]
    left_out = development.research_stratum == ""
    assert record["labelled_development_cells_left_out_as_not_searched"] == development[left_out].perturbation_type.value_counts().sort_index().to_dict()
    families = 1 if quota_unit == "crossed" else 2
    assert sum(quota["labelled_development_cells"] for quota in record["quota_cells"]) == families * int((~left_out).sum())
    assert record["num_distinct_cells_to_read"] == len(sample.drop_duplicates(["perturbation_id", "symptom"]))
    assert record["num_development_perturbations"] == cells.perturbation_id.nunique() - len(held_out["perturbation_ids"])


def test_a_seed_gives_one_sample_whatever_the_order_of_the_rows_and_another_seed_another(cells):
    sample, _ = draw(cells)
    shuffled = cells.sample(frac=1.0, random_state=3).reset_index(drop=True)
    pd.testing.assert_frame_equal(draw(shuffled)[0], sample)
    for draw_order in DRAW_ORDERS:
        first, second = draw(cells, draw_order=draw_order, seed=1)[0], draw(cells, draw_order=draw_order, seed=2)[0]
        assert not first[["perturbation_id", "symptom"]].equals(second[["perturbation_id", "symptom"]])


def test_nothing_of_a_held_out_cell_changes_the_sample(cells):
    """Decision 9.134: the held-out set must not "decide what gets sourced"."""
    held_out = held_out_set(cells)
    in_held_out = cells.perturbation_id.isin(held_out["perturbation_ids"])
    changed = cells.copy()
    changed.loc[in_held_out, "kept_positive"] = ~changed.loc[in_held_out, "kept_positive"]
    changed.loc[in_held_out, "record_count"] = 999
    changed.loc[in_held_out, "earliest_record_year"] = 1900
    changed.loc[in_held_out, "research_stratum"] = "more"
    for draw_order in DRAW_ORDERS:
        pd.testing.assert_frame_equal(draw(changed, held_out, draw_order=draw_order)[0], draw(cells, held_out, draw_order=draw_order)[0])


def test_a_generator_per_quota_cell_keeps_each_quota_cell_apart_from_the_others(cells):
    genes = cells[cells.perturbation_type == "gene"].reset_index(drop=True)
    held_out_genes = {**held_out_set(cells), "perturbation_ids": [pid for pid in held_out_set(cells)["perturbation_ids"] if pid.startswith("g")]}
    capped = [quota["quota_cell"] for quota in draw(genes, held_out_genes, quota_unit="apart")[1]["quota_cells"]
              if quota["candidates"] > SAMPLE_SIZE_PER_STRATUM]
    assert capped

    def drawn(table, draw_order):
        sample = draw(table, held_out_genes, quota_unit="apart", draw_order=draw_order)[0]
        return {name: set(zip(group.perturbation_id, group.symptom)) for name, group in sample[sample.quota_cell.isin(capped)].groupby("quota_cell")}

    assert drawn(cells, "one_generator_per_quota_cell") == drawn(genes, "one_generator_per_quota_cell")
    # with one generator the combination and drug quota cells, which come first, move where the gene quota cells start in its stream
    assert drawn(cells, "one_generator_in_quota_order") != drawn(genes, "one_generator_in_quota_order")


def test_apart_draws_a_type_by_stratum_and_by_era_separately_in_reporting_order(cells):
    sample, record = draw(cells, quota_unit="apart")
    names = [quota["quota_cell"] for quota in record["quota_cells"]]
    assert [name.split(" | ")[0] for name in names] == sorted(name.split(" | ")[0] for name in names)  # types sorted
    assert names[0].startswith("combination | research_stratum=lower_third")
    gene_names = [name for name in names if name.startswith("gene")]
    first_era = next(position for position, name in enumerate(gene_names) if "first_record_era_thirds=" in name)
    assert all("research_stratum=" in name for name in gene_names[:first_era]) and all("first_record_era_thirds=" in name for name in gene_names[first_era:])
    assert [name.split("=")[1] for name in gene_names[:first_era]] == ["none", "fewer", "more"]
    assert record["num_distinct_cells_to_read"] < record["num_rows_drawn"]  # some cells were drawn by stratum and by era
    crossed = draw(cells, quota_unit="crossed")[1]
    assert all("research_stratum=" in quota["quota_cell"] and "first_record_era_thirds=" in quota["quota_cell"] for quota in crossed["quota_cells"])


def test_the_two_stratum_form_and_the_two_way_era_can_be_read_instead(cells):
    sample, record = draw(cells, stratum_reading="none_against_any", era_reading="first_record_era_two_way")
    assert set(sample.stratum) == {"any"} and set(sample.era) <= {"through_2015", "from_2016"}
    assert {quota["none_against_any"] for quota in record["quota_cells"]} == {"none", "any"}


# ---------------------------------------------------------------- what is refused


def test_a_held_out_set_not_drawn_on_this_evidence_and_label_selection_is_refused(cells):
    table = set(cells.perturbation_id)
    good = held_out_set(cells)
    assert held_out_perturbation_ids(good, EVIDENCE, SELECTION, table) == set(good["perturbation_ids"])
    refusals = {
        "drawn on evidence": {**good, "evidence_records_sha256": "x" * 64},
        "drawn on label selection": {**good, "label_selection_sha256": "x" * 64},
        "records no evidence_records_sha256": {key: value for key, value in good.items() if key != "evidence_records_sha256"},
        "records no label_selection_sha256": {key: value for key, value in good.items() if key != "label_selection_sha256"},
        "names no perturbation_ids": {**good, "perturbation_ids": []},
        "names a perturbation twice": {**good, "perturbation_ids": good["perturbation_ids"] + good["perturbation_ids"][:1]},
        "does not hold": {**good, "perturbation_ids": good["perturbation_ids"] + ["g999"]},
        "no training portion": {**good, "perturbation_ids": sorted(table)},
        "not all strings": {**good, "perturbation_ids": [1, 2]},
    }
    for message, held_out in refusals.items():
        with pytest.raises(ValueError, match=message):
            held_out_perturbation_ids(held_out, EVIDENCE, SELECTION, table)
        with pytest.raises(ValueError, match=message):
            draw(cells, held_out)
    unselected = {**good, "label_selection_sha256": None}  # drawn with no label selection, and sampled with none
    assert held_out_perturbation_ids(unselected, EVIDENCE, None, table) == set(good["perturbation_ids"])


def test_every_open_definition_is_required_and_checked(cells):
    parameters = inspect.signature(draw_sourcing_sample).parameters
    for name in ("evidence_records_sha256", "label_selection_sha256", *CHOICES):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY and parameters[name].default is inspect.Parameter.empty
    with pytest.raises(TypeError):
        draw_sourcing_sample(cells, held_out_set(cells), evidence_records_sha256=EVIDENCE, label_selection_sha256=SELECTION,
                             **{key: value for key, value in CHOICES.items() if key != "seed"})
    for change in ({"seed": True}, {"seed": -1}, {"seed": 1.5}, {"quota_unit": "both"}, {"stratum_reading": "first_record_era_thirds"},
                   {"era_reading": "registered_date_era_two_way"}, {"draw_order": "sorted"}):
        with pytest.raises(ValueError):
            draw(cells, **change)
    assert STRATUM_READINGS == ("research_stratum", "none_against_any")
    assert ERA_READINGS == ("first_record_era_thirds", "first_record_era_two_way")


def test_cells_that_are_not_the_strata_assignment_are_refused(cells):
    with pytest.raises(ValueError, match="lack"):
        draw(cells.drop(columns=["first_record_era_thirds"]))
    with pytest.raises(ValueError, match="repeat a cell"):
        draw(pd.concat([cells, cells.head(1)], ignore_index=True))
    odd = cells.copy()
    odd.loc[odd.kept_positive & (odd.research_stratum != ""), "first_record_era_thirds"] = "unlabelled"
    with pytest.raises(ValueError, match="does not"):
        draw(odd)


# ---------------------------------------------------------------- the files and the command


def write_inputs(directory: Path, cells: pd.DataFrame) -> dict[str, Path]:
    evidence_dir = directory / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "evidence_records.parquet").write_bytes(b"synthetic evidence")
    selection = directory / "selection.parquet"
    selection.write_bytes(b"synthetic label selection")
    digests = {"evidence_records_sha256": file_sha256(evidence_dir / "evidence_records.parquet"), "label_selection_sha256": file_sha256(selection)}
    cells_path = directory / "strata_cells.csv"
    record_path = directory / "strata_record.json"
    write_record({**digests, "cells_sha256": write_cells(cells, cells_path)}, record_path)
    held_out_path = directory / "held_out.json"
    held_out_path.write_text(json.dumps({**held_out_set(cells), **digests}))
    return {"evidence_dir": evidence_dir, "selection": selection, "cells": cells_path, "record": record_path, "held_out": held_out_path, **digests}


def test_the_files_are_checked_before_anything_is_drawn(tmp_path, cells):
    inputs = write_inputs(tmp_path, cells)
    digests = {key: inputs[key] for key in ("evidence_records_sha256", "label_selection_sha256")}
    sample, record = draw_sourcing_sample_from_files(inputs["held_out"], inputs["record"], inputs["cells"], **digests, **CHOICES)
    held_out = json.loads(inputs["held_out"].read_text())
    pd.testing.assert_frame_equal(sample, draw_sourcing_sample(cells, held_out, **digests, **CHOICES)[0], check_dtype=False)
    assert record["inputs"]["cells_sha256"] == file_sha256(inputs["cells"]) and record["inputs"]["held_out_set_sha256"] == file_sha256(inputs["held_out"])
    with pytest.raises(ValueError, match="another evidence"):
        draw_sourcing_sample_from_files(inputs["held_out"], inputs["record"], inputs["cells"], **{**digests, "evidence_records_sha256": "x" * 64}, **CHOICES)
    with pytest.raises(ValueError, match="another label selection"):
        draw_sourcing_sample_from_files(inputs["held_out"], inputs["record"], inputs["cells"], **{**digests, "label_selection_sha256": None}, **CHOICES)
    inputs["cells"].write_text(inputs["cells"].read_text().replace("g001", "g998", 1))
    with pytest.raises(ValueError, match="is not the cells file"):
        draw_sourcing_sample_from_files(inputs["held_out"], inputs["record"], inputs["cells"], **digests, **CHOICES)
    inputs["record"].write_text(inputs["record"].read_text().replace('"cells_sha256"', '"cells_sha256" ', 1))
    with pytest.raises(ValueError, match="sidecar"):
        draw_sourcing_sample_from_files(inputs["held_out"], inputs["record"], inputs["cells"], **digests, **CHOICES)


def command_arguments(inputs: dict, directory: Path, **choices) -> list[str]:
    choices = {**CHOICES, **choices}
    return ["--held-out", str(inputs["held_out"]), "--strata-record", str(inputs["record"]), "--strata-cells", str(inputs["cells"]),
            "--evidence-dir", str(inputs["evidence_dir"]), "--label-selection", str(inputs["selection"]),
            "--seed", str(choices["seed"]), "--quota-unit", choices["quota_unit"], "--stratum-reading", choices["stratum_reading"],
            "--era-reading", choices["era_reading"], "--draw-order", choices["draw_order"],
            "--output-cells", str(directory / "sample.csv"), "--output-record", str(directory / "sample.json")]


def test_the_command_writes_the_sample_once_and_needs_every_open_definition(tmp_path, cells, capsys):
    inputs = write_inputs(tmp_path / "inputs", cells)
    arguments = command_arguments(inputs, tmp_path)
    draw_sourcing_sample_main(arguments)
    record = json.loads((tmp_path / "sample.json").read_text())
    assert record["sample_sha256"] == file_sha256(tmp_path / "sample.csv")
    assert (tmp_path / "sample.json.sha256").read_text().split()[0] == file_sha256(tmp_path / "sample.json")
    assert record["rule"]["seed"] == CHOICES["seed"] and len(pd.read_csv(tmp_path / "sample.csv")) == record["num_rows_drawn"]
    with pytest.raises(SystemExit, match="not overwritten"):
        draw_sourcing_sample_main(arguments)
    for flag in ("--seed", "--quota-unit", "--stratum-reading", "--era-reading", "--draw-order"):
        position = arguments.index(flag)
        with pytest.raises(SystemExit):
            draw_sourcing_sample_main(arguments[:position] + arguments[position + 2:])
