"""experiments/diagnose_module_supports.py: where trained modules sit, and how much of each support node one
perturbation dominates."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from trainer_in_process import run_main_model

from experiments.diagnose_module_supports import describe_modules, diagnose_fold, dominance_shares, markdown, module_readings
from experiments.run_main_model import build_argument_parser, build_models, encode, pad_perturbations
from tests.test_comparative_checks import toy_data
from tests.test_soft_priors_in_the_trainer import write_toy_dataset


def test_a_node_one_perturbation_reads_is_dominated_and_one_four_read_equally_is_not() -> None:
    readings = np.array([[2.0, 1.0, 0.0],
                         [0.0, -1.0, 0.0],
                         [0.0, 1.0, 0.0],
                         [0.0, -1.0, 0.0]])
    share, top_row = dominance_shares(readings)
    assert share[0] == 1.0 and top_row[0] == 0
    assert share[1] == 0.25, "the sign of a reading does not lessen it"
    assert np.isnan(share[2]) and top_row[2] == -1


def test_the_readings_of_every_node_sum_to_the_modules_activation_logit(tmp_path: Path) -> None:
    data = toy_data(tmp_path)
    arguments = build_argument_parser().parse_args(["--graph-dir", str(tmp_path / "graph"), "--evidence-dir", str(tmp_path / "evidence"), "--encoder", "linear_response",
                                                    # one batch on both sides: the encoder's fixed point stops on the batch's relative change, so
                                                    # a perturbation's field moves by about 1e-4 with the company it is batched with
                                                    "--node-state-dim", "6", "--num-modules", "2", "--batch-size", "4"])
    torch.manual_seed(0)
    encoder, head = build_models(data, arguments, torch.device("cpu"))
    rows = np.arange(len(data.perturbation_ids))
    every_node = [np.arange(len(data.node_ids))] * head.num_pathway_modules
    readings = module_readings(encoder, head, data, rows, every_node, None, arguments, torch.device("cpu"))
    encoder.eval()
    head.eval()
    with torch.no_grad():
        node_index, sign_and_magnitude = pad_perturbations(data, rows)
        activation = head.module_activation(encode(encoder, node_index, sign_and_magnitude, None, arguments.field)).numpy()
    for module in range(head.num_pathway_modules):
        logit = readings[module].sum(axis=1) + float(head.module_readout_bias[module].detach())
        assert np.allclose(1.0 / (1.0 + np.exp(-logit)), activation[:, module], atol=1e-6)


def test_the_module_summary_names_its_nodes_degrees_reach_and_dominance() -> None:
    class Data:
        node_ids = ["A", "B", "C", "D"]
        perturbation_ids = ["p0", "p1", "p2"]
    expected_gate = np.array([[0.9, 0.8, 0.1, 0.7]])
    support = [np.array([0, 1, 3])]
    readings = [np.array([[1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0]])]
    in_degree = np.array([1, 50, 2, 3])
    reach = np.array([1, 9, 0, 4])
    module = describe_modules(Data(), np.array([2, 0, 1]), expected_gate, readings, support, in_degree, reach)[0]
    assert module["support_nodes"] == 3 and module["median_in_degree"] == 3.0 and module["median_reach"] == 4.0
    assert module["nodes_no_training_perturbation_moves"] == 1
    assert module["share_of_nodes_dominated_above_0.9"] == 0.5
    assert module["top_nodes_by_gate"][0] == {"node": "A", "expected_gate": 0.9, "in_degree": 1, "reach": 1, "dominance_share": 1.0, "dominated_by": "p2"}, "reading row 0 is the data's row 2"


def trained_run(tmp_path: Path, *extra: str) -> Path:
    paths = write_toy_dataset(tmp_path)
    run_directory = tmp_path / "run"
    command = [sys.executable, "experiments/run_main_model.py", "--graph-dir", str(paths["graph"]), "--evidence-dir", str(paths["evidence"]), "--run-dir", str(run_directory),
               "--encoder", "linear_response", "--max-epochs", "2", "--num-bootstrap", "3", "--refit-on-validation", "--validation-fraction", "0.3",
               "--no-keep-large-groups-in-training", "--fold", "0", "--seed", "0", "--batch-size", "8", "--placebo-negative-weights-file", "none",
               "--group-by", "disease_cluster", "--label-selection", str(paths["selection"]), "--normalisation", "total_in_degree",
               "--num-modules", "2", *extra]
    completed = run_main_model(command[2:])
    assert completed.returncode == 0, completed.stderr[-3000:]
    return next(path for path in run_directory.iterdir() if path.is_dir())


def test_end_to_end_a_run_trained_under_the_rule_records_it_and_its_supports_hold_none_of_the_nodes_it_excluded(tmp_path: Path) -> None:
    fold = trained_run(tmp_path, "--module-support-minimum-reach", "2")
    import json
    results = json.loads((fold / "results.json").read_text())
    recorded = results["module_support_reach"]
    assert recorded["minimum_reach"] == 2 and recorded["rows_counted"] == "the rows given"
    assert recorded["perturbations_counted"] == results["num_train"] + results["num_validation"], "the refit counts its refit rows"
    diagnosis = diagnose_fold(fold, support_threshold=0.0)
    assert diagnosis["checkpoint"] == "refit_checkpoint.pt" and diagnosis["module_support_minimum_reach"] == 2
    for module in diagnosis["modules"]:
        assert all(node["reach"] >= 2 for node in module["top_nodes_by_gate"]), "a support node the rule excluded has gate 0, below any threshold but 0"
    assert "| module |" in markdown([diagnosis])


def test_a_lockbox_run_is_refused(tmp_path: Path) -> None:
    fold = trained_run(tmp_path)
    lockbox_like = fold.parent / (fold.name + "_lockbox")
    fold.rename(lockbox_like)
    with pytest.raises(SystemExit, match="blinded"):
        diagnose_fold(lockbox_like, support_threshold=0.5)
