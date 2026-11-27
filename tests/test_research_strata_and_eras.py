"""The eras and research strata of amendment item 38 (d) and (g), and their descriptive scorer, on synthetic tables only
(mechanistic_pathway_learning/evaluation/research_strata_and_eras.py, experiments/write_research_strata_and_eras.py,
experiments/score_research_strata_and_eras.py)."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import yaml

from mechanistic_pathway_learning.evaluation import research_strata_and_eras as strata_module
from mechanistic_pathway_learning.evaluation.research_strata_and_eras import (
    TWO_WAY_ERA_CUT, UNLABELLED_CELL, UnexplainedUnsearchedCells, assign_strata_and_eras, equal_count_third_boundaries,
    first_record_eras_of_one_type, read_cell_search_table, read_cells, refuse_unexplained_unsearched_cells, registered_date_eras,
    research_strata_of_one_type, same_assignment, scored_cells_from_experiment_data, validated_cell_search_table, write_cells, write_record)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "experiments"))


def search_row(perturbation_id, symptom, count, year=None, status="searched", reason=""):
    return {"perturbation_id": perturbation_id, "symptom": symptom, "search_status": status, "record_count": count,
            "earliest_record_year": year, "not_searched_reason": reason}


def scored_cell(perturbation_id, symptom, perturbation_type, kept_positive=False, set_aside=False, registered_date=0):
    return {"perturbation_id": perturbation_id, "symptom": symptom, "perturbation_type": perturbation_type, "kept_positive": kept_positive,
            "set_aside_by_label_selection": set_aside, "registered_date_ordinal": registered_date}


# --- the registered cut and the schema ---------------------------------------------------------------------------------

def test_the_two_way_cut_is_the_one_configs_evaluation_yaml_holds():
    evaluation = yaml.safe_load((REPOSITORY_ROOT / "configs" / "evaluation.yaml").read_text())
    assert TWO_WAY_ERA_CUT == date.fromisoformat(evaluation["splits"]["time_split"]["monogenic_cutoff"])


def test_the_search_table_schema_is_checked():
    good = pd.DataFrame([search_row("g1", "anxiety", 3, 1990), search_row("g1", "fatigue", 0),
                         search_row("g2", "anxiety", None, status="not_searched", reason="refused twice")])
    table = validated_cell_search_table(good)
    assert table.record_count.dtype == "Int64" and table.record_count.isna().tolist() == [False, False, True]
    with pytest.raises(ValueError, match="lacks"):
        validated_cell_search_table(good.drop(columns=["earliest_record_year"]))
    bad_rows = {
        "repeat a cell": [search_row("g1", "anxiety", 3, 1990), search_row("g1", "anxiety", 2, 1991)],
        "records but no earliest_record_year": [search_row("g1", "anxiety", 3)],
        "no record but an earliest_record_year": [search_row("g1", "anxiety", 0, 1990)],
        "never as zero": [search_row("g1", "anxiety", 0, status="not_searched", reason="timeout")],
        "a negative record_count": [search_row("g1", "anxiety", -1)],
        "not a whole number": [search_row("g1", "anxiety", 1.5, 1990)],
        "search_status holds": [search_row("g1", "anxiety", 1, 1990, status="maybe")],
        "a searched cell with a not_searched_reason": [search_row("g1", "anxiety", 1, 1990, reason="why")],
    }
    for message, rows in bad_rows.items():
        with pytest.raises(ValueError, match=message):
            validated_cell_search_table(pd.DataFrame(rows))


def test_the_search_table_reads_from_csv_and_parquet(tmp_path):
    frame = pd.DataFrame([search_row("g1", "anxiety", 3, 1990), search_row("g1", "fatigue", 0),
                          search_row("g2", "anxiety", None, status="not_searched", reason="refused twice")])
    frame.to_csv(tmp_path / "search.csv", index=False)
    frame.to_parquet(tmp_path / "search.parquet")
    for path in (tmp_path / "search.csv", tmp_path / "search.parquet"):
        table = read_cell_search_table(path)
        assert table.record_count.tolist()[:2] == [3, 0] and pd.isna(table.record_count.iloc[2])
        assert table.not_searched_reason.tolist() == ["", "", "refused twice"]


def test_the_reading_refuses_while_a_cell_is_unexplained():
    scored = pd.DataFrame([scored_cell("g1", "anxiety", "gene"), scored_cell("g1", "fatigue", "gene")])
    explained = validated_cell_search_table(pd.DataFrame([search_row("g1", "anxiety", 2, 2001),
                                                          search_row("g1", "fatigue", None, status="not_searched", reason="refused twice")]))
    refuse_unexplained_unsearched_cells(explained, scored)  # a reason explains it
    no_row = explained.iloc[:1]
    with pytest.raises(UnexplainedUnsearchedCells, match="1 cells of the scored table have no row"):
        refuse_unexplained_unsearched_cells(no_row, scored)
    no_reason = explained.assign(not_searched_reason=["", ""])
    with pytest.raises(UnexplainedUnsearchedCells, match="1 are marked not searched with no reason"):
        refuse_unexplained_unsearched_cells(no_reason, scored)
    foreign = validated_cell_search_table(pd.concat([explained, pd.DataFrame([search_row("g9", "anxiety", 1, 2000)])]))
    with pytest.raises(ValueError, match="another evidence table"):
        refuse_unexplained_unsearched_cells(foreign, scored)
    with pytest.raises(UnexplainedUnsearchedCells):
        assign_strata_and_eras(no_reason, scored)


# --- thirds, strata and eras -------------------------------------------------------------------------------------------

def test_thirds_are_cut_by_position_with_ties_kept_in_the_lower_group():
    assert equal_count_third_boundaries(np.arange(1, 10)) == (3.0, 6.0)  # 3, 3, 3
    assert equal_count_third_boundaries(np.arange(1, 11)) == (4.0, 7.0)  # 4, 3, 3, as measurement_coverage_strata cuts
    assert equal_count_third_boundaries(np.array([5.0])) == (5.0, 5.0)
    assert equal_count_third_boundaries(np.array([])) is None
    # 2 at the first boundary: every 2 goes to the lower third, and the second boundary is read at its own position
    counts = np.array([1, 2, 2, 2, 2, 3, 4, 5, 6])
    strata, summary = research_strata_of_one_type(counts)
    assert summary["form"] == "tertiles" and summary["boundaries"] == {"largest_count_in_the_lower_third": 2.0, "largest_count_in_the_middle_third": 3.0}
    assert strata.tolist() == ["lower_third"] * 5 + ["middle_third"] + ["upper_third"] * 3


def test_a_tie_can_leave_a_third_empty_and_it_is_not_refilled():
    strata, summary = research_strata_of_one_type(np.array([1, 1, 1, 1, 1, 1, 1, 2, 3]))
    assert summary["boundaries"] == {"largest_count_in_the_lower_third": 1.0, "largest_count_in_the_middle_third": 1.0}
    assert strata.tolist().count("middle_third") == 0 and strata.tolist().count("lower_third") == 7


def test_the_form_turns_on_a_third_of_the_cells_being_none():
    exactly_a_third = np.array([0, 0, 0, 1, 2, 3, 4, 5, 6])
    _, summary = research_strata_of_one_type(exactly_a_third)
    assert summary["form"] == "tertiles" and summary["num_none_cells"] == 3  # "no more than a third"
    more_than_a_third = np.array([0, 0, 0, 0, 0, 1, 2, 3, 4])
    strata, summary = research_strata_of_one_type(more_than_a_third)
    assert summary["form"] == "none_fewer_more" and summary["boundaries"] == {"median_count_of_the_cells_with_a_record": 2.5}
    assert strata.tolist() == ["none"] * 5 + ["fewer", "fewer", "more", "more"]
    strata, summary = research_strata_of_one_type(np.array([0, 0, 0, 1, 2, 3]))  # an odd number with a record: the median is a count
    assert summary["boundaries"]["median_count_of_the_cells_with_a_record"] == 2.0
    assert strata.tolist() == ["none"] * 3 + ["fewer", "fewer", "more"]  # "fewer (at or below it)"
    strata, summary = research_strata_of_one_type(np.array([0, 0]))
    assert summary["form"] == "none_fewer_more" and strata.tolist() == ["none", "none"]
    strata, summary = research_strata_of_one_type(np.array([]))
    assert summary["form"] is None and not len(strata)


def test_eras_are_cut_on_the_dated_kept_positives_only():
    years = np.array([1950, 1960, 1970, 1980, 1990, 2000, 2010, 2016, 2020, 1900, np.nan, np.nan])
    counts = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 0, 0])
    kept = np.array([True] * 9 + [False, True, False])  # the 1900 cell is unlabelled, so it moves no boundary
    thirds, two_way, summary = first_record_eras_of_one_type(years, kept, counts)
    assert summary["boundary_years"] == {"last_year_of_the_first_third": 1970, "last_year_of_the_second_third": 2000}
    assert summary["num_dated_kept_positives"] == 9 and summary["num_undated_kept_positives"] == 1
    assert thirds.tolist() == ["first_third"] * 3 + ["second_third"] * 3 + ["last_third"] * 3 + [UNLABELLED_CELL, "undated", UNLABELLED_CELL]
    assert two_way.tolist() == ["through_2015"] * 7 + ["from_2016"] * 2 + [UNLABELLED_CELL, "undated", UNLABELLED_CELL]
    # ties at a boundary year stay in the earlier third
    thirds, _, summary = first_record_eras_of_one_type(np.array([1990, 1990, 1990, 1990, 2000, 2010]), np.ones(6, dtype=bool), np.ones(6))
    assert summary["boundary_years"]["last_year_of_the_first_third"] == 1990 and thirds.tolist().count("first_third") == 4


def test_the_registered_gene_date_is_read_at_the_end_of_2015():
    ordinals = np.array([date(2015, 12, 31).toordinal(), date(2016, 1, 1).toordinal(), 0, date(2010, 5, 1).toordinal()])
    kept = np.array([True, True, True, False])
    assert registered_date_eras(ordinals, kept).tolist() == ["through_2015", "from_2016", "undated", UNLABELLED_CELL]


# --- the assignment of a whole table -----------------------------------------------------------------------------------

def synthetic_assignment_inputs():
    """Six genes and three drugs against two symptoms. Gene counts: few none, so tertiles; drug counts: mostly none."""
    gene_counts = {"g1": (0, 1), "g2": (2, 3), "g3": (4, 5), "g4": (6, 7), "g5": (8, 9), "g6": (10, 11)}
    gene_years = {"g1": (None, 1960), "g2": (1970, 1980), "g3": (1990, 2000), "g4": (2005, 2010), "g5": (2014, 2016), "g6": (2018, 2020)}
    rows, cells = [], []
    for gene, (anxiety, fatigue) in gene_counts.items():
        for symptom, count, year in (("anxiety", anxiety, gene_years[gene][0]), ("fatigue", fatigue, gene_years[gene][1])):
            rows.append(search_row(gene, symptom, count, year))
            cells.append(scored_cell(gene, symptom, "gene", kept_positive=symptom == "fatigue" or gene == "g1",
                                     registered_date=date(2012, 1, 1).toordinal() if gene in ("g1", "g2") else 0))
    for drug, counts in {"d1": (0, 0), "d2": (0, 5), "d3": (2, None)}.items():
        for symptom, count in zip(("anxiety", "fatigue"), counts):
            if count is None:
                rows.append(search_row(drug, symptom, None, status="not_searched", reason="refused twice"))
            else:
                rows.append(search_row(drug, symptom, count, 2001 if count else None))
            cells.append(scored_cell(drug, symptom, "drug", kept_positive=drug == "d2", set_aside=(drug, symptom) == ("d1", "fatigue")))
    rows.append(search_row("g1", "headache", 3, 1999))  # a symptom the table does not score: left out and counted
    return validated_cell_search_table(pd.DataFrame(rows)), pd.DataFrame(cells)


def test_each_type_is_binned_apart_and_the_record_says_what_it_took():
    search, scored = synthetic_assignment_inputs()
    cells, record = assign_strata_and_eras(search, scored)
    gene, drug = record["types"]["gene"], record["types"]["drug"]
    assert gene["research_strata"]["form"] == "tertiles" and gene["research_strata"]["num_cells"] == 12
    assert gene["research_strata"]["boundaries"] == {"largest_count_in_the_lower_third": 3.0, "largest_count_in_the_middle_third": 7.0}
    assert drug["research_strata"]["form"] == "none_fewer_more"
    # the drug cell not searched is left out: not binned, not in the share of none, named by its reason
    assert drug["research_strata"]["num_cells"] == 5 and drug["research_strata"]["num_none_cells"] == 3
    assert drug["left_out_not_searched"] == {"cells": 1, "kept_positives": 0, "cells_by_reason": {"refused twice": 1}}
    assert record["search_rows_of_symptoms_the_table_does_not_score"] == 1
    assert record["pooled_research_stratum"]["defined"] is False and "different forms" in record["pooled_research_stratum"]["reason"]
    by_cell = cells.set_index(["perturbation_id", "symptom"])
    assert by_cell.loc[("d3", "fatigue"), "left_out_reason"] == "refused twice"
    assert all(by_cell.loc[("d3", "fatigue"), column] == "" for column in strata_module.READING_COLUMNS)
    # a pair a label selection set aside is binned by its count but is in no era
    assert by_cell.loc[("d1", "fatigue"), "research_stratum"] == "none" and by_cell.loc[("d1", "fatigue"), "first_record_era_thirds"] == ""
    # gene eras: six dated kept positives (the fatigue cells), one undated (g1 anxiety, no record)
    assert gene["first_record_eras"]["boundary_years"] == {"last_year_of_the_first_third": 1980, "last_year_of_the_second_third": 2010}
    assert by_cell.loc[("g1", "anxiety"), "first_record_era_thirds"] == "undated"
    assert by_cell.loc[("g5", "fatigue"), "first_record_era_two_way"] == "from_2016"
    assert by_cell.loc[("g3", "anxiety"), "first_record_era_thirds"] == UNLABELLED_CELL
    # the registered gene date is read for genes only
    assert by_cell.loc[("g2", "fatigue"), "registered_date_era_two_way"] == "through_2015"
    assert by_cell.loc[("g3", "fatigue"), "registered_date_era_two_way"] == "undated"
    assert by_cell.loc[("d2", "fatigue"), "registered_date_era_two_way"] == ""
    assert "registered_date_two_way" in gene and "registered_date_two_way" not in drug
    assert cells.none_against_any[cells.perturbation_type == "gene"].tolist().count("none") == 1


def test_the_pooled_research_stratum_is_defined_when_both_types_take_one_form():
    search, scored = synthetic_assignment_inputs()
    drug_rows = search.perturbation_id.str.startswith("d") & (search.search_status == "searched")
    search.loc[drug_rows, "record_count"] = pd.array([1, 2, 3, 4, 5], dtype="Int64")
    search.loc[drug_rows, "earliest_record_year"] = pd.array([2001] * 5, dtype="Int64")
    _, record = assign_strata_and_eras(validated_cell_search_table(search), scored)
    assert record["pooled_research_stratum"] == {"defined": True, "form": "tertiles"}


def test_the_cells_and_the_record_are_written_hashed_and_read_back(tmp_path):
    search, scored = synthetic_assignment_inputs()
    cells, record = assign_strata_and_eras(search, scored)
    cells_sha256 = write_cells(cells, tmp_path / "cells.csv")
    assert cells_sha256 == strata_module.file_sha256(tmp_path / "cells.csv")
    read_back = read_cells(tmp_path / "cells.csv")
    assert same_assignment(cells, read_back) == []
    moved = read_back.copy()
    moved.loc[0, "research_stratum"] = "upper_third"
    assert same_assignment(cells, moved) == ["research_stratum"]
    assert same_assignment(cells, read_back.iloc[1:]) == ["the cells themselves"]
    record_sha256 = write_record(record, tmp_path / "record.json")
    assert (tmp_path / "record.json.sha256").read_text() == f"{record_sha256}  record.json\n"
    assert json.loads((tmp_path / "record.json").read_text())["types"]["gene"]["research_strata"]["form"] == "tertiles"


def test_the_scored_cells_are_every_perturbation_against_every_scored_symptom():
    outcomes = np.zeros((6, 3))
    outcomes[:5, 0] = 1  # five kept positives: scored
    outcomes[:4, 1] = 1  # four: not scored
    outcomes[:6, 2] = 1
    label_mask = np.ones_like(outcomes, dtype=bool)
    label_mask[5, 2] = False  # set aside, so the third symptom keeps five
    dates = np.zeros((6, 3), dtype=np.int64)
    dates[0, 0] = date(2001, 1, 1).toordinal()
    data = SimpleNamespace(outcomes=outcomes, label_mask=label_mask, evidence_dates=dates, symptoms=["a", "b", "c"],
                           perturbation_ids=[f"p{i}" for i in range(6)], perturbation_types=["gene"] * 5 + ["drug"])
    cells = scored_cells_from_experiment_data(data, minimum_positives_to_score=5)
    assert sorted(set(cells.symptom)) == ["a", "c"] and len(cells) == 12
    row = cells[(cells.perturbation_id == "p5") & (cells.symptom == "c")].iloc[0]
    assert bool(row.set_aside_by_label_selection) and not bool(row.kept_positive) and row.perturbation_type == "drug"
    assert cells[(cells.perturbation_id == "p0") & (cells.symptom == "a")].registered_date_ordinal.iloc[0] == date(2001, 1, 1).toordinal()


# --- the descriptive scorer --------------------------------------------------------------------------------------------

def test_cell_label_arrays_place_each_stratum_at_its_cell():
    from score_research_strata_and_eras import cell_label_arrays
    search, scored = synthetic_assignment_inputs()
    cells, _ = assign_strata_and_eras(search, scored)
    perturbation_ids = sorted(set(cells.perturbation_id))
    arrays = cell_label_arrays(cells, perturbation_ids, ["anxiety", "fatigue", "headache"])
    assert arrays["research_stratum"].shape == (9, 3) and (arrays["research_stratum"][:, 2] == "").all()
    assert arrays["first_record_era_thirds"][perturbation_ids.index("g1"), 0] == "undated"
    with pytest.raises(ValueError, match="does not hold"):
        cell_label_arrays(cells, perturbation_ids[:-1], ["anxiety", "fatigue"])


def scorer_inputs(num_perturbations=40, num_symptoms=3, seed=0):
    """A synthetic held-out set: half genes, half drugs, two per leakage group, with labels and predictions."""
    generator = np.random.default_rng(seed)
    outcomes = (generator.random((num_perturbations, num_symptoms)) < 0.4).astype(float)
    label_mask = np.ones_like(outcomes, dtype=bool)
    types = ["gene" if i % 2 == 0 else "drug" for i in range(num_perturbations)]
    groups = [f"group{i // 2}" for i in range(num_perturbations)]
    held_out = np.zeros(num_perturbations, dtype=bool)
    held_out[: num_perturbations * 3 // 4] = True
    research = np.where(generator.random(outcomes.shape) < 0.5, "none", "any").astype(object)
    eras = np.where(outcomes > 0, np.where(generator.random(outcomes.shape) < 0.5, "through_2015", "from_2016"), UNLABELLED_CELL).astype(object)
    cell_labels = {reading: np.full(outcomes.shape, "", dtype=object) for reading in strata_module.READING_COLUMNS}
    cell_labels["none_against_any"] = research
    cell_labels["research_stratum"] = np.where(research == "none", "none", "more").astype(object)
    cell_labels["first_record_era_two_way"] = eras
    gene_rows = np.array(types) == "gene"
    cell_labels["registered_date_era_two_way"][gene_rows] = eras[gene_rows]
    rows = np.flatnonzero(held_out)
    model = {s: outcomes[rows] * 0.6 + generator.random((len(rows), num_symptoms)) * 0.5 for s in (0, 1)}
    baselines = {"popularity": {s: generator.random((len(rows), num_symptoms)) for s in (0, 1)},
                 "degree_popularity": {s: outcomes[rows] * 0.3 + generator.random((len(rows), num_symptoms)) for s in (0, 1)}}
    return outcomes, label_mask, held_out, types, groups, cell_labels, {"tested": model}, baselines


def test_the_scorer_reads_each_stratum_on_its_own_cells_and_each_era_on_its_positives():
    from score_confirmatory import macro_auprc, micro_auprc
    from score_research_strata_and_eras import descriptive_readings
    outcomes, label_mask, held_out, types, groups, cell_labels, models, baselines = scorer_inputs()
    symptoms = ["a", "b", "c"]
    result = descriptive_readings(outcomes, label_mask, held_out, types, groups, symptoms, cell_labels, models, baselines, seeds=[0, 1],
                                  num_bootstrap=30, bootstrap_seed=1, minimum_positives_to_score=2, pooled_research_stratum_defined=False)
    assert set(result) == {"drug", "gene", "pooled"}
    assert "registered_date_era_two_way" in result["gene"]["readings"] and "registered_date_era_two_way" not in result["drug"]["readings"]
    assert set(result["pooled"]["readings"]) == {"none_against_any"} and "research_stratum_not_pooled" in result["pooled"]
    assert result["gene"]["readings"]["first_record_era_thirds"] == {}  # no cell holds a third in this table
    rows = np.flatnonzero(held_out)
    gene_positions = np.flatnonzero(np.array(types)[rows] == "gene")
    held_rows = rows[gene_positions]

    # a research stratum holds its own cells
    entry = result["gene"]["readings"]["none_against_any"]["none"]
    mask = label_mask[held_rows] & (cell_labels["none_against_any"][held_rows] == "none")
    assert entry["held_out_cells"] == int(mask.sum()) and entry["held_out_positives"] == int((outcomes[held_rows] * mask).sum())
    macro_columns = [symptoms.index(symptom) for symptom in entry["macro_symptoms"]]
    assert macro_columns == [c for c in range(3) if (outcomes[held_rows][:, c] * mask[:, c]).sum() >= 2]
    gene_rows_all = np.flatnonzero(np.array(types) == "gene")
    whole_mask = cell_labels["none_against_any"][gene_rows_all] == "none"
    assert [symptoms.index(s) for s in entry["micro_symptoms"]] == [c for c in range(3) if (outcomes[gene_rows_all][:, c] * whole_mask[:, c]).sum() >= 2]

    def seed_mean_macro(by_seed):
        return float(np.mean([macro_auprc(by_seed[s][gene_positions], outcomes[held_rows], mask, macro_columns) for s in (0, 1)]))

    for name, by_seed in baselines.items():
        assert entry["baseline_scores"][name]["macro"] == pytest.approx(seed_mean_macro(by_seed))
    best = max(baselines, key=lambda name: seed_mean_macro(baselines[name]))
    assert entry["best_baseline"]["macro"] == best
    assert entry["differences"]["tested"]["macro"]["difference"] == pytest.approx(seed_mean_macro(models["tested"]) - seed_mean_macro(baselines[best]))
    difference = entry["differences"]["tested"]["macro"]
    assert difference["num_resamples_defined"] > 0 and difference["lower_95"] <= difference["upper_95"]

    # an era holds its positives, scored against every unlabelled cell
    era = result["gene"]["readings"]["first_record_era_two_way"]["from_2016"]
    labels = cell_labels["first_record_era_two_way"][held_rows]
    era_mask = label_mask[held_rows] & ((labels == "from_2016") | (labels == UNLABELLED_CELL))
    assert era["held_out_cells"] == int(era_mask.sum())
    assert era["held_out_positives"] == int(((outcomes[held_rows] > 0) & (labels == "from_2016")).sum())
    micro_columns = [symptoms.index(s) for s in era["micro_symptoms"]]
    expected_micro = np.mean([micro_auprc(models["tested"][s][gene_positions], outcomes[held_rows], era_mask, micro_columns) for s in (0, 1)])
    assert era["model_scores"]["tested"]["micro"] == pytest.approx(expected_micro)


def test_the_scorer_is_reproducible_and_pools_research_strata_when_defined():
    from score_research_strata_and_eras import descriptive_readings
    outcomes, label_mask, held_out, types, groups, cell_labels, models, baselines = scorer_inputs()
    arguments = dict(seeds=[0, 1], num_bootstrap=20, bootstrap_seed=3, minimum_positives_to_score=2)
    first = descriptive_readings(outcomes, label_mask, held_out, types, groups, ["a", "b", "c"], cell_labels, models, baselines,
                                 pooled_research_stratum_defined=True, **arguments)
    second = descriptive_readings(outcomes, label_mask, held_out, types, groups, ["a", "b", "c"], cell_labels, models, baselines,
                                  pooled_research_stratum_defined=True, **arguments)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert set(first["pooled"]["readings"]) == {"research_stratum", "none_against_any"}
    pooled = first["pooled"]["readings"]["none_against_any"]["any"]
    by_type = sum(first[kind]["readings"]["none_against_any"]["any"]["held_out_cells"] for kind in ("gene", "drug"))
    assert pooled["held_out_cells"] == by_type


def test_the_bootstrap_resamples_whole_leakage_groups(monkeypatch):
    import score_research_strata_and_eras as scorer
    seen_units = []
    original = scorer.bootstrap_rows

    def recording(unit, members_of_group, num_rows, generator):
        seen_units.append((unit, [len(members) for members in members_of_group]))
        return original(unit, members_of_group, num_rows, generator)

    monkeypatch.setattr(scorer, "bootstrap_rows", recording)
    outcomes, label_mask, held_out, types, groups, cell_labels, models, baselines = scorer_inputs()
    scorer.descriptive_readings(outcomes, label_mask, held_out, types, groups, ["a", "b", "c"], cell_labels, models, baselines, seeds=[0, 1],
                                num_bootstrap=2, bootstrap_seed=0, minimum_positives_to_score=2, pooled_research_stratum_defined=False)
    assert {unit for unit, _ in seen_units} == {"group"}
    # each type's groups hold one perturbation of that type (one gene and one drug per group); pooled, two
    assert sorted({tuple(sizes) for _, sizes in seen_units}, key=len)[-1] == tuple([2] * 15)


def test_the_scorer_refuses_before_the_confirmatory_scoring(tmp_path, monkeypatch):
    import score_research_strata_and_eras as scorer
    lockbox = tmp_path / "lockbox.json"
    lockbox.write_text("{}")
    monkeypatch.setattr(sys, "argv", ["score_research_strata_and_eras.py", "--lockbox", str(lockbox), "--confirmatory-output-dir", str(tmp_path / "confirmatory"),
                                      "--search-table", "s", "--strata-record", "r", "--strata-cells", "c"])
    with pytest.raises(SystemExit, match="has not scored the held-out set"):
        scorer.main()


def test_the_writer_refuses_to_move_written_cuts(tmp_path, monkeypatch):
    import write_research_strata_and_eras as writer
    (tmp_path / "record.json").write_text("{}")
    monkeypatch.setattr(sys, "argv", ["write_research_strata_and_eras.py", "--search-table", str(tmp_path / "search.csv"),
                                      "--output-record", str(tmp_path / "record.json"), "--output-cells", str(tmp_path / "cells.csv")])
    with pytest.raises(SystemExit, match="the cuts are not moved"):
        writer.main()


def test_the_writer_writes_the_cells_and_the_record_from_the_data_and_the_search(tmp_path, monkeypatch):
    """End to end on a toy graph and evidence table: three gene knockouts and two drugs against two symptoms."""
    import write_research_strata_and_eras as writer
    from tests.test_drug_entry_nodes import RELATIONS, evidence_row, toy_graph, write_graph
    nodes, edges = toy_graph()
    write_graph(tmp_path / "graph", nodes, edges, RELATIONS)
    (tmp_path / "evidence").mkdir()
    seeds = {"knockout_A": ("gene", [["GENE:A", -1.0, 1.0]]), "knockout_B": ("gene", [["GENE:B", -1.0, 1.0]]), "knockout_C": ("gene", [["GENE:C", -1.0, 1.0]]),
             "drug_one": ("drug", [["GENE:A", -1.0, 0.5]]), "drug_two": ("drug", [["GENE:B", 0.5, 1.0]])}
    rows = []
    for perturbation, (kind, nodes_of) in seeds.items():
        rows.append(evidence_row(perturbation, kind, f"cluster:{perturbation}", nodes_of) | {"evidence_date": "2010-05-01" if perturbation == "knockout_A" else None})
        if perturbation in ("knockout_A", "drug_one"):
            rows.append(evidence_row(perturbation, kind, f"cluster:{perturbation}", nodes_of) | {"symptom": "fatigue"})
    pd.DataFrame(rows).to_parquet(tmp_path / "evidence" / "evidence_records.parquet", index=False)
    counts = {("knockout_A", "anxiety"): 4, ("knockout_A", "fatigue"): 1, ("knockout_B", "anxiety"): 0, ("knockout_B", "fatigue"): 2,
              ("knockout_C", "anxiety"): 9, ("knockout_C", "fatigue"): 3, ("drug_one", "anxiety"): 0, ("drug_one", "fatigue"): 0, ("drug_two", "anxiety"): 7}
    search = pd.DataFrame([search_row(perturbation, symptom, count, 1990 + count if count else None) for (perturbation, symptom), count in counts.items()]
                          + [search_row("drug_two", "fatigue", None, status="not_searched", reason="no searchable term")])
    search.to_csv(tmp_path / "search.csv", index=False)
    monkeypatch.setattr(writer, "MINIMUM_POSITIVES_TO_SCORE", 1)
    arguments = ["write_research_strata_and_eras.py", "--graph-dir", str(tmp_path / "graph"), "--evidence-dir", str(tmp_path / "evidence"),
                 "--label-selection", "none", "--search-table", str(tmp_path / "search.csv"),
                 "--output-record", str(tmp_path / "out" / "record.json"), "--output-cells", str(tmp_path / "out" / "cells.csv")]
    monkeypatch.setattr(sys, "argv", arguments)
    writer.main()
    record = json.loads((tmp_path / "out" / "record.json").read_text())
    assert record["cells_sha256"] == strata_module.file_sha256(tmp_path / "out" / "cells.csv")
    assert record["search_table_sha256"] == strata_module.file_sha256(tmp_path / "search.csv")
    assert (tmp_path / "out" / "record.json.sha256").read_text().split()[0] == strata_module.file_sha256(tmp_path / "out" / "record.json")
    assert record["scored_symptoms"] == ["anxiety", "fatigue"] and record["num_scored_cells"] == 10
    assert record["types"]["gene"]["research_strata"]["form"] == "tertiles"
    assert record["types"]["drug"]["left_out_not_searched"]["cells_by_reason"] == {"no searchable term": 1}
    cells = read_cells(tmp_path / "out" / "cells.csv").set_index(["perturbation_id", "symptom"])
    assert cells.loc[("knockout_A", "anxiety"), "registered_date_era_two_way"] == "through_2015"
    assert cells.loc[("knockout_B", "anxiety"), "registered_date_era_two_way"] == "undated"
    assert cells.loc[("knockout_B", "fatigue"), "first_record_era_thirds"] == UNLABELLED_CELL
    assert cells.loc[("drug_one", "anxiety"), "first_record_era_two_way"] == "undated"
    # a second writing over the first is refused, and an unexplained cell stops the writer before it writes anything
    with pytest.raises(SystemExit, match="the cuts are not moved"):
        writer.main()
    search.loc[search.perturbation_id == "drug_two", "not_searched_reason"] = ""
    search.to_csv(tmp_path / "search.csv", index=False)
    arguments[-3:] = [str(tmp_path / "again" / "record.json"), "--output-cells", str(tmp_path / "again" / "cells.csv")]
    with pytest.raises(UnexplainedUnsearchedCells):
        writer.main()
    assert not (tmp_path / "again").exists()
