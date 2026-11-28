"""Tests added on 28 November 2026 to kill mutants of experiments/score_research_strata_and_eras.py that
tests/test_research_strata_and_eras.py lets survive (hand-made mutation testing; the mutants and which test kills each
were listed in the working report of the session of 28 November 2026, which is outside the repository). Each test checks what the script's docstrings say it does. Synthetic tables and a
toy graph only: no real held-out set is scored."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mechanistic_pathway_learning.evaluation.research_strata_and_eras import UNLABELLED_CELL, assign_strata_and_eras, file_sha256, read_cells, write_cells, write_record
from tests.test_research_strata_and_eras import scorer_inputs, search_row, synthetic_assignment_inputs

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import score_research_strata_and_eras as scorer  # noqa: E402

SYMPTOMS = ["a", "b", "c"]


# ---------------------------------------------------------------- the pieces


def test_a_cells_file_naming_a_symptom_the_data_lacks_is_refused():
    """cell_label_arrays refuses "the cells file names perturbations or symptoms the data does not hold"."""
    search, scored = synthetic_assignment_inputs()
    cells, _ = assign_strata_and_eras(search, scored)
    with pytest.raises(ValueError, match="does not hold"):
        scorer.cell_label_arrays(cells, sorted(set(cells.perturbation_id)), ["anxiety"])


def test_a_stratum_scores_only_the_cells_the_label_mask_keeps():
    """stratum_masks: "The cells each stratum of a reading scores", which are the labelled cells of the label mask
    given: a pair a label selection set aside is scored in no stratum (research_strata_and_eras, rule 4)."""
    research = np.array([["none", "any", "any"]], dtype=object)
    label_mask = np.array([[False, True, False]])
    masks = scorer.stratum_masks(research, "none_against_any", label_mask)
    assert masks["none"].tolist() == [[False, False, False]] and masks["any"].tolist() == [[False, True, False]]
    eras = np.array([["from_2016", UNLABELLED_CELL, UNLABELLED_CELL]], dtype=object)
    masks = scorer.stratum_masks(eras, "first_record_era_two_way", np.array([[True, False, True]]))
    assert list(masks) == ["from_2016"] and masks["from_2016"].tolist() == [[True, False, True]]


def test_the_best_baseline_is_chosen_among_the_defined_scores():
    """best_of: "The baseline with the highest seed-mean score, among those with a defined one; None when none has"."""
    assert scorer.best_of({"popularity": float("nan"), "degree_popularity": 0.3, "type_popularity": 0.1}) == "degree_popularity"
    assert scorer.best_of({"popularity": 0.2, "degree_popularity": float("nan")}) == "popularity"
    assert scorer.best_of({"popularity": float("nan")}) is None


def test_the_interval_is_the_2_5_and_97_5_percentiles_of_the_defined_resamples():
    """The module docstring: "the 2.5 and 97.5 percentiles of the resampled differences"."""
    result = scorer.interval([float(value) for value in range(101)] + [float("nan")])
    assert result == {"lower_95": pytest.approx(2.5), "upper_95": pytest.approx(97.5), "num_resamples_defined": 101}


def test_with_every_resample_the_held_out_set_itself_the_interval_closes_on_the_difference(monkeypatch):
    """The interval is that of "the seed mean of the model minus that baseline" over resamples of the held-out rows, so
    a bootstrap that returns the held-out rows unchanged gives an interval of one point, the observed difference. The
    positives per macro symptom are the stratum's held-out positives."""
    monkeypatch.setattr(scorer, "bootstrap_rows", lambda unit, members_of_group, num_rows, generator: np.arange(num_rows))
    outcomes, label_mask, held_out, types, groups, cell_labels, models, baselines = scorer_inputs()
    result = scorer.descriptive_readings(outcomes, label_mask, held_out, types, groups, SYMPTOMS, cell_labels, models, baselines, seeds=[0, 1],
                                         num_bootstrap=3, bootstrap_seed=0, minimum_positives_to_score=2, pooled_research_stratum_defined=True)
    checked = 0
    for scope_entry in result.values():
        for by_stratum in scope_entry["readings"].values():
            for entry in by_stratum.values():
                for metric in scorer.METRICS:
                    difference = entry["differences"]["tested"][metric]
                    if np.isfinite(difference["difference"]):
                        assert difference["lower_95"] == pytest.approx(difference["difference"])
                        assert difference["upper_95"] == pytest.approx(difference["difference"])
                        assert difference["num_resamples_defined"] == 3
                        checked += 1
    assert checked > 10
    rows = np.flatnonzero(held_out)
    gene_rows = rows[np.array(types)[rows] == "gene"]
    entry = result["gene"]["readings"]["none_against_any"]["any"]
    held_positives = ((outcomes[gene_rows] > 0) & (cell_labels["none_against_any"][gene_rows] == "any")).sum(axis=0)
    assert entry["held_out_positives_per_macro_symptom"] == {symptom: int(held_positives[SYMPTOMS.index(symptom)]) for symptom in entry["macro_symptoms"]}
    assert entry["macro_symptoms"]


def test_each_scope_draws_its_resamples_from_the_bootstrap_seed_plus_its_position(monkeypatch):
    """--bootstrap-seed: "the confirmatory scorer's; each scope draws from this plus its position" (the scopes are the
    types in sorted order, then pooled)."""
    first_states = []
    generators_seen = []  # kept alive, so that a later scope's generator cannot take an earlier one's id
    original = scorer.bootstrap_rows

    def recording(unit, members_of_group, num_rows, generator):
        if not any(generator is seen for seen in generators_seen):
            generators_seen.append(generator)
            first_states.append(json.dumps(generator.bit_generator.state, sort_keys=True, default=int))
        return original(unit, members_of_group, num_rows, generator)

    monkeypatch.setattr(scorer, "bootstrap_rows", recording)
    outcomes, label_mask, held_out, types, groups, cell_labels, models, baselines = scorer_inputs()
    result = scorer.descriptive_readings(outcomes, label_mask, held_out, types, groups, SYMPTOMS, cell_labels, models, baselines, seeds=[0, 1],
                                         num_bootstrap=2, bootstrap_seed=40, minimum_positives_to_score=2, pooled_research_stratum_defined=False)
    assert list(result) == ["drug", "gene", "pooled"]
    assert first_states == [json.dumps(np.random.default_rng(40 + position).bit_generator.state, sort_keys=True, default=int) for position in range(3)]


def test_the_page_says_why_the_pooled_research_stratum_is_not_given():
    result = {"pooled": {"held_out_perturbations": 4, "held_out_leakage_groups": 2, "readings": {},
                         "research_stratum_not_pooled": "the types took different forms of strata"}}
    assert scorer.markdown_lines(result, ["tested"], ["# header"])[-1] == "pooled: research_stratum not given: the types took different forms of strata."


# ---------------------------------------------------------------- what main refuses before it reads a stratum


class ReachedTheLockbox(Exception):
    """Raised in place of read_lockbox: main got past every check on the strata files."""


def written_strata(tmp_path: Path, monkeypatch) -> dict:
    """The writer's own end-to-end inputs (tests/test_research_strata_and_eras.py), written by
    experiments/write_research_strata_and_eras.py, and a confirmatory scoring of a lockbox file."""
    import write_research_strata_and_eras as writer
    from tests.test_drug_entry_nodes import RELATIONS, evidence_row, toy_graph, write_graph
    nodes, edges = toy_graph()
    write_graph(tmp_path / "graph", nodes, edges, RELATIONS)
    (tmp_path / "evidence").mkdir()
    seeds = {"knockout_A": ("gene", [["GENE:A", -1.0, 1.0]]), "knockout_B": ("gene", [["GENE:B", -1.0, 1.0]]),
             "drug_one": ("drug", [["GENE:A", -1.0, 0.5]])}
    rows = []
    for perturbation, (kind, nodes_of) in seeds.items():
        rows.append(evidence_row(perturbation, kind, f"cluster:{perturbation}", nodes_of))
        if perturbation != "knockout_B":
            rows.append(evidence_row(perturbation, kind, f"cluster:{perturbation}", nodes_of) | {"symptom": "fatigue"})
    pd.DataFrame(rows).to_parquet(tmp_path / "evidence" / "evidence_records.parquet", index=False)
    counts = {("knockout_A", "anxiety"): 4, ("knockout_A", "fatigue"): 1, ("knockout_B", "anxiety"): 0, ("knockout_B", "fatigue"): 2,
              ("drug_one", "anxiety"): 0, ("drug_one", "fatigue"): 3}
    pd.DataFrame([search_row(perturbation, symptom, count, 1990 + count if count else None) for (perturbation, symptom), count in counts.items()]
                 ).to_csv(tmp_path / "search.csv", index=False)
    monkeypatch.setattr(writer, "MINIMUM_POSITIVES_TO_SCORE", 1)
    monkeypatch.setattr(scorer, "MINIMUM_POSITIVES_TO_SCORE", 1)
    common = ["--graph-dir", str(tmp_path / "graph"), "--evidence-dir", str(tmp_path / "evidence"), "--label-selection", "none",
              "--search-table", str(tmp_path / "search.csv")]
    monkeypatch.setattr(sys, "argv", ["write_research_strata_and_eras.py", *common, "--output-record", str(tmp_path / "record.json"),
                                      "--output-cells", str(tmp_path / "cells.csv")])
    writer.main()
    lockbox = tmp_path / "lockbox.json"
    lockbox.write_text(json.dumps({"perturbation_ids": ["knockout_A"]}))
    confirmatory = tmp_path / "confirmatory"
    confirmatory.mkdir()
    (confirmatory / "SCORED").write_text("")
    (confirmatory / "lockbox_scores.json").write_text(json.dumps({"lockbox_sha256": file_sha256(lockbox)}))
    monkeypatch.setattr(sys, "argv", ["score_research_strata_and_eras.py", *common, "--strata-record", str(tmp_path / "record.json"),
                                      "--strata-cells", str(tmp_path / "cells.csv"), "--lockbox", str(lockbox), "--models", "tested",
                                      "--confirmatory-output-dir", str(confirmatory), "--output", str(tmp_path / "out.json"),
                                      "--markdown-output", str(tmp_path / "out.md")])

    def reached_the_lockbox(*arguments, **keywords):
        raise ReachedTheLockbox

    monkeypatch.setattr(scorer, "read_lockbox", reached_the_lockbox)
    return {"record": tmp_path / "record.json", "cells": tmp_path / "cells.csv", "search": tmp_path / "search.csv", "confirmatory": confirmatory}


def test_unchanged_strata_pass_every_check_main_makes_before_the_lockbox(tmp_path, monkeypatch):
    written_strata(tmp_path, monkeypatch)
    with pytest.raises(ReachedTheLockbox):
        scorer.main()


def test_main_refuses_to_run_before_the_confirmatory_scoring_of_that_lockbox(tmp_path, monkeypatch):
    """The docstring: it "refuses to run until experiments/score_confirmatory.py has scored that set (its SCORED marker
    and lockbox_scores.json in --confirmatory-output-dir, for the same lockbox file)"."""
    paths = written_strata(tmp_path, monkeypatch)
    (paths["confirmatory"] / "lockbox_scores.json").write_text(json.dumps({"lockbox_sha256": "another lockbox"}))
    with pytest.raises(SystemExit, match="scored another lockbox"):
        scorer.main()
    (paths["confirmatory"] / "lockbox_scores.json").unlink()
    with pytest.raises(SystemExit, match="has not scored the held-out set"):
        scorer.main()


def test_main_refuses_strata_files_that_are_not_the_ones_written(tmp_path, monkeypatch):
    """The docstring: "the script checks the cells file against the record's SHA-256, the search table, graph,
    evidence table and label selection against the hashes the record holds"; the record itself is checked against its
    sidecar."""
    paths = written_strata(tmp_path, monkeypatch)
    original_record, original_cells, original_search = (paths[name].read_text() for name in ("record", "cells", "search"))
    paths["record"].write_text(original_record + " ")
    with pytest.raises(SystemExit, match="is not the file"):
        scorer.main()
    paths["record"].write_text(original_record)
    paths["cells"].write_text(original_cells + "\n")
    with pytest.raises(SystemExit, match="is not the cells file"):
        scorer.main()
    paths["cells"].write_text(original_cells)
    paths["search"].write_text(original_search + "\n")
    with pytest.raises(SystemExit, match="written on other files than those scored now: \\['search_table_sha256'\\]"):
        scorer.main()


def test_main_refuses_cuts_moved_after_they_were_written(tmp_path, monkeypatch):
    """The docstring: it "recomputes the assignment from the search table and the data, refusing if any cell's stratum
    differs ("The cuts are not moved after the draw")", even when the moved cells file and its record agree."""
    paths = written_strata(tmp_path, monkeypatch)
    cells = read_cells(paths["cells"])
    position = int(np.flatnonzero(cells.research_stratum.to_numpy() != "")[0])
    cells.loc[position, "research_stratum"] = "upper_third" if cells.research_stratum[position] != "upper_third" else "lower_third"
    record = json.loads(paths["record"].read_text())
    record["cells_sha256"] = write_cells(cells, paths["cells"])
    write_record(record, paths["record"])
    with pytest.raises(SystemExit, match="the cuts are not moved after the draw"):
        scorer.main()


def test_the_micro_symptoms_are_those_with_the_minimum_of_the_strata_positives_in_the_whole_data():
    """The module docstring: "the registered micro AUPRC (score_confirmatory.micro_auprc) over the symptoms with that
    many of the stratum's positives in the whole data", where the macro counts them "among the held-out cells". The
    minimum is chosen so that some stratum holds exactly that many positives of a symptom in the whole data, and so
    that the whole-data and held-out lists differ for some stratum."""
    outcomes, label_mask, held_out, types, groups, cell_labels, models, baselines = scorer_inputs()
    positive, kinds, labels = outcomes > 0, np.array(types), cell_labels["none_against_any"]
    held_rows = np.flatnonzero(held_out)
    strata = [(kind, stratum) for kind in ("gene", "drug") for stratum in ("none", "any")]
    whole = {(kind, stratum): (positive & (labels == stratum))[kinds == kind].sum(axis=0) for kind, stratum in strata}
    held = {(kind, stratum): (positive & (labels == stratum))[held_rows[kinds[held_rows] == kind]].sum(axis=0) for kind, stratum in strata}

    def symptoms_with(counts, minimum):
        return [SYMPTOMS[column] for column in range(len(SYMPTOMS)) if counts[column] >= minimum]

    minimum = next(candidate for candidate in range(2, 20) if any(candidate in counts for counts in whole.values())
                   and any(symptoms_with(whole[key], candidate) != symptoms_with(held[key], candidate) for key in strata))
    result = scorer.descriptive_readings(outcomes, label_mask, held_out, types, groups, SYMPTOMS, cell_labels, models, baselines, seeds=[0, 1],
                                         num_bootstrap=2, bootstrap_seed=0, minimum_positives_to_score=minimum, pooled_research_stratum_defined=False)
    for kind, stratum in strata:
        assert result[kind]["readings"]["none_against_any"][stratum]["micro_symptoms"] == symptoms_with(whole[(kind, stratum)], minimum)
