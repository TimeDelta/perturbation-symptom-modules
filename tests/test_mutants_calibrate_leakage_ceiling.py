"""Tests added on 28 November 2026 to kill mutants of experiments/calibrate_leakage_ceiling.py that
tests/test_leakage_ceiling.py lets survive (hand-made mutation testing; the mutants and which test kills each are listed
in the working report of the session of 28 November 2026, which is outside the repository). Each test checks what the script's docstrings say it does; its open definitions stay
required arguments. Synthetic records only: nothing here calibrates a real ceiling."""
import json
import sys
from pathlib import Path

import pytest

from mechanistic_pathway_learning.data_release import sha256_of_file
from mechanistic_pathway_learning.evaluation.leakage_only_adversary import registered_channel_list
from tests.test_leakage_ceiling import measurement_record
from tests.test_measure_leakage_only_adversary import write_graph_directory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import calibrate_leakage_ceiling as calibration_script  # noqa: E402
from measure_leakage_only_adversary import graph_file_sha256  # noqa: E402

FIT = ("base_rate_shrunk_mean", "seen_target_share")


def test_an_advantage_key_must_be_the_measurements_key_and_nothing_more():
    """--advantage: "written as the measurement's key ([drug_stratum_|gene_stratum_](macro|micro)_advantage_over_<baseline>)"."""
    with pytest.raises(ValueError, match="key of the form"):
        calibration_script.calibrate(measurement_record(), *FIT, "drug_stratum_macro_advantage_over_type_popularity_later", 0.05, "least_squares_line", 6)
    measurement = measurement_record()
    for draw in measurement["pooling_rules"]["base_rate_shrunk_mean"]["draws"]:
        if "drug_stratum_macro_advantage_over_type_popularity" in draw:
            draw["gene_stratum_micro_advantage_over_degree_popularity"] = draw["drug_stratum_macro_advantage_over_type_popularity"]
    result = calibration_script.calibrate(measurement, *FIT, "gene_stratum_micro_advantage_over_degree_popularity", 0.05, "least_squares_line", 6)
    assert result["ceiling"]["ceiling"] == pytest.approx(0.25) and result["one_standard_error"] == 0.05


def test_a_pooling_rule_the_measurement_did_not_measure_is_refused():
    with pytest.raises(ValueError, match="no draws for pooling rule 'nearest_neighbour_maximum'"):
        calibration_script.calibrate(measurement_record(), "nearest_neighbour_maximum", "seen_target_share",
                                     "drug_stratum_macro_advantage_over_type_popularity", 0.05, "least_squares_line", 6)


def test_a_draw_without_the_statistic_or_with_a_value_that_is_not_finite_is_left_out_with_its_reason():
    """calibrate returns "the points used and the draws left out"."""
    measurement = measurement_record()
    draws = measurement["pooling_rules"]["base_rate_shrunk_mean"]["draws"]
    del draws[0]["seen_target_share"]
    draws[1]["drug_stratum_macro_advantage_over_type_popularity"] = float("nan")
    result = calibration_script.calibrate(measurement, *FIT, "drug_stratum_macro_advantage_over_type_popularity", 0.05, "least_squares_line", 6)
    assert [point["draw_seed"] for point in result["points"]] == [4, 5]
    assert {entry["draw_seed"]: entry["reason"] for entry in result["pseudo_draws_left_out"]} == {
        0: "the draw records no seen_target_share", 1: "a value is not finite",
        2: "the draw held out no row or trained on none", 3: "the draw records no drug_stratum_macro_advantage_over_type_popularity"}


def measured_inputs(directory: Path) -> dict:
    graph = write_graph_directory(directory / "graph")
    evidence = directory / "evidence"
    evidence.mkdir()
    (evidence / "evidence_records.parquet").write_bytes(b"evidence")
    selection = directory / "selection.parquet"
    selection.write_bytes(b"selection")
    measurement = {**measurement_record(), "graph_file_sha256": graph_file_sha256(graph),
                   "evidence_records_sha256": sha256_of_file(evidence / "evidence_records.parquet"),
                   "label_selection_sha256": sha256_of_file(selection)}
    measurement_path = directory / "measurement.json"
    measurement_path.write_text(json.dumps(measurement))
    return {"graph": graph, "evidence": evidence, "selection": selection, "measurement": measurement_path}


def test_a_measurement_on_another_evidence_table_or_label_selection_is_refused(tmp_path):
    """refuse_another_graph: "this refuses a measurement whose graph files, evidence table or label selection differ
    from the ones named here"."""
    inputs = measured_inputs(tmp_path)
    measurement = json.loads(inputs["measurement"].read_text())
    calibration_script.refuse_another_graph(measurement, inputs["graph"], inputs["evidence"], inputs["selection"])
    inputs["selection"].write_bytes(b"another selection")
    with pytest.raises(ValueError, match="label_selection_sha256 differs"):
        calibration_script.refuse_another_graph(measurement, inputs["graph"], inputs["evidence"], inputs["selection"])
    inputs["selection"].write_bytes(b"selection")
    (inputs["evidence"] / "evidence_records.parquet").write_bytes(b"another evidence table")
    with pytest.raises(ValueError, match="evidence_records_sha256 differs"):
        calibration_script.refuse_another_graph(measurement, inputs["graph"], inputs["evidence"], inputs["selection"])


def command(inputs: dict, output: Path, source="the drug stratum's macro reading, synthetic") -> list[str]:
    return ["calibrate_leakage_ceiling.py", "--measurement", str(inputs["measurement"]), "--graph-dir", str(inputs["graph"]),
            "--evidence-dir", str(inputs["evidence"]), "--label-selection", str(inputs["selection"]),
            "--pooling-rule", "base_rate_shrunk_mean", "--statistic", "seen_target_share",
            "--advantage", "drug_stratum_macro_advantage_over_type_popularity", "--one-standard-error", "0.05",
            "--standard-error-source", source, "--curve-form", "least_squares_line", "--num-pseudo-draws", "6",
            "--output", str(output)]


def test_the_command_writes_one_calibration_once_with_where_its_standard_error_was_read(tmp_path, monkeypatch):
    """The docstring: "It writes one JSON file and refuses to overwrite one", and --standard-error-source is "a
    sentence saying where that number was read", recorded beside it."""
    inputs = measured_inputs(tmp_path)
    output = tmp_path / "calibration.json"
    monkeypatch.setattr(sys, "argv", command(inputs, output, source="   "))
    with pytest.raises(SystemExit, match="--standard-error-source is empty"):
        calibration_script.main()
    assert not output.exists()
    monkeypatch.setattr(sys, "argv", command(inputs, output))
    calibration_script.main()
    record = json.loads(output.read_text())
    assert record["standard_error_source"] == "the drug stratum's macro reading, synthetic" and record["one_standard_error"] == 0.05
    assert record["ceiling"]["ceiling"] == pytest.approx(0.25) and record["measurement_sha256"] == sha256_of_file(inputs["measurement"])
    written = output.read_text()
    with pytest.raises(SystemExit, match="a calibration is written once"):
        calibration_script.main()
    assert output.read_text() == written


def test_a_statistic_that_reads_labels_is_refused_even_when_every_draw_records_it():
    """--statistic: "Only statistics that read no label are offered, since the draw has to compute the same one on the
    real draw without opening it". tests/test_leakage_ceiling.py asks for held_out_drugs, which no draw of its record
    holds, so the fit's own refusal (whose message also says "label-free") answered for it; here every draw records the
    statistic asked for."""
    measurement = measurement_record()
    for draw in measurement["pooling_rules"]["base_rate_shrunk_mean"]["draws"]:
        draw["adversary_macro_auprc"] = draw["seen_target_share"]
    with pytest.raises(ValueError, match="statistic must be one of .*the label-free ones, not 'adversary_macro_auprc'"):
        calibration_script.calibrate(measurement, "base_rate_shrunk_mean", "adversary_macro_auprc",
                                     "drug_stratum_macro_advantage_over_type_popularity", 0.05, "least_squares_line", 6)


# ---------------------------------------------------------------- added by the checker of the same day
# Two mutants the checker wrote (not among the 306 of the report) survived every test above: main not calling
# refuse_another_graph, and calibrate recording no channel list.


def test_the_command_refuses_a_measurement_made_on_another_graph_and_writes_nothing(tmp_path, monkeypatch):
    """The module docstring: "this refuses a measurement whose graph files, evidence table or label selection differ
    from the ones named here, which are the draw's"; refuse_another_graph is tested on its own above, this is the
    command."""
    inputs = measured_inputs(tmp_path)
    (inputs["graph"] / "edges.parquet").write_bytes(b"the graph rebuilt since")
    output = tmp_path / "calibration.json"
    monkeypatch.setattr(sys, "argv", command(inputs, output))
    with pytest.raises(ValueError, match="graph_file_sha256 differs"):
        calibration_script.main()
    assert not output.exists()


def test_the_calibration_carries_the_channels_the_measurement_scored():
    """The module docstring: "which channels the measurement scored is copied into the output from the measurement,
    which recorded them"; experiments/draw_held_out_set.py computes the draw's statistics with that channel list."""
    channels = registered_channel_list(2, [("gene", "gene"), ("drug", "gene")], "stored_without_currency_out_edges")
    measurement = measurement_record(channels=channels)
    result = calibration_script.calibrate(measurement, *FIT, "drug_stratum_macro_advantage_over_type_popularity", 0.05, "least_squares_line", 6)
    assert result["channels"] == channels and result["channels"] != registered_channel_list()
