"""Decision 9.22's zero-coupling count on the coupling filter's inputs (experiments/measure_zero_coupling_receptors.py),
on a small OmniPath table and admitted table whose groups are known by hand.

Each fixture receptor is built to land in one group of the script's docstring: one that loses its only signed G-alpha
edge and keeps nothing, one that loses it and keeps a binds edge written the other way round, one reaching a G alpha
only through an expanded complex, one that keeps an admitted coupling, one whose only kept edge is negatively signed,
one whose sign a curated override flips before the filter reads it, one whose unlisted edge an override makes unsigned
so the filter passes it, one with binds edges only, one in OmniPath with no G-alpha edge, and one absent from OmniPath.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from experiments.measure_zero_coupling_receptors import (
    REPOSITORY_ROOT,
    file_provenance,
    main,
    measure_zero_coupling,
    repository_commit,
)

OMNIPATH_FIELDS = ["source_genesymbol", "target_genesymbol", "is_stimulation", "is_inhibition",
                   "consensus_stimulation", "consensus_inhibition"]
ACTIVATES, INHIBITS, UNSIGNED = ("True", "False"), ("False", "True"), ("False", "False")

FIXTURE_INTERACTIONS = [
    ("LOSTALL", "GNAS", ACTIVATES),            # unlisted: dropped, nothing left
    ("LOSTBINDS", "GNAQ", ACTIVATES),          # unlisted: dropped ...
    ("GNAI2", "LOSTBINDS", UNSIGNED),          # ... and a binds row written G alpha first, stored both ways
    ("COMPLEXED", "GNAO1_GNB1_GNG2", ACTIVATES),  # the complex expands to an unlisted G alpha
    ("KEEPS", "GNAS", ACTIVATES),              # admitted: kept
    ("KEEPS", "GNAQ", ACTIVATES),              # unlisted: dropped, but KEEPS keeps GNAS
    ("KEEPSNEG", "GNAI1", INHIBITS),           # admitted and negatively signed: kept, not a coupling
    ("FLIPPED", "GNAI1", ACTIVATES),           # admitted; the override below makes it inhibits before the filter
    ("MADEUNSIGNED", "GNAS", ACTIVATES),       # unlisted; the override below makes it binds, which the filter passes
    ("BINDSONLY", "GNAS", UNSIGNED),           # binds only, before and after
    ("NOEDGE", "MAPK1", ACTIVATES),            # in OmniPath, no G-alpha edge
    ("RGS4", "GNAS", INHIBITS),                # not an annotated receptor: never counted
]
FIXTURE_ADMITTED = [  # receptor, G alpha, family, role
    ("LOSTALL", "GNAI1", "Gi/o", "primary"),
    ("LOSTBINDS", "GNAI1", "Gi/o", "primary"),
    ("COMPLEXED", "GNAI1", "Gi/o", "primary"),
    ("KEEPS", "GNAS", "Gs", "primary"),
    ("KEEPSNEG", "GNAI1", "Gi/o", "primary"),
    ("FLIPPED", "GNAI1", "Gi/o", "primary"),
    ("MADEUNSIGNED", "GNAI1", "Gi/o", "primary"),
    ("BINDSONLY", "GNAS", "Gs", "primary"),
    ("NOEDGE", "GNAS", "Gs", "primary"),
    ("ABSENT", "GNAS", "Gs", "secondary"),
]
FIXTURE_OVERRIDES = [  # source, target, as sourced, as corrected
    ("FLIPPED", "GNAI1", ("activates", "1.0"), ("inhibits", "-1.0")),
    ("MADEUNSIGNED", "GNAS", ("activates", "1.0"), ("binds", "0.0")),
]


def write_fixture_inputs(directory: Path) -> tuple[Path, Path, Path]:
    interactions_path, admitted_path, overrides_path = directory / "interactions.tsv", directory / "admitted.csv", directory / "overrides.csv"
    with open(interactions_path, "w", newline="", encoding="utf-8") as interactions_file:
        writer = csv.DictWriter(interactions_file, delimiter="\t", fieldnames=OMNIPATH_FIELDS)
        writer.writeheader()
        for source, target, (stimulation, inhibition) in FIXTURE_INTERACTIONS:
            writer.writerow({"source_genesymbol": source, "target_genesymbol": target, "is_stimulation": stimulation,
                             "is_inhibition": inhibition, "consensus_stimulation": stimulation, "consensus_inhibition": inhibition})
    with open(admitted_path, "w", newline="", encoding="utf-8") as admitted_file:
        writer = csv.writer(admitted_file)
        writer.writerow(["receptor_gene_symbol", "g_alpha_gene_symbol", "g_alpha_family", "transducer_role"])
        writer.writerows(FIXTURE_ADMITTED)
    with open(overrides_path, "w", newline="", encoding="utf-8") as overrides_file:
        writer = csv.writer(overrides_file)
        writer.writerow(["source_symbol", "target_symbol", "relation_type_as_sourced", "sign_as_sourced",
                         "relation_type_corrected", "sign_corrected", "source_is_brain_expressed", "reason"])
        for source, target, (sourced_relation, sourced_sign), (corrected_relation, corrected_sign) in FIXTURE_OVERRIDES:
            writer.writerow([source, target, sourced_relation, sourced_sign, corrected_relation, corrected_sign, "True", "test"])
    return interactions_path, admitted_path, overrides_path


def names(group: dict) -> list[str]:
    return [entry["receptor"] if isinstance(entry, dict) else entry for entry in group["receptors"]]


def test_every_fixture_receptor_lands_in_its_group(tmp_path):
    result = measure_zero_coupling(*write_fixture_inputs(tmp_path))
    receptors = result["receptors"]
    lost = receptors["signed_edge_before_and_none_after"]
    assert names(lost["left_with_no_edge_into_a_g_alpha"]) == ["COMPLEXED", "LOSTALL"]
    assert names(lost["left_with_binds_edges_only"]) == ["LOSTBINDS"]
    assert lost["count"] == 3
    never = receptors["no_signed_edge_before_the_filter"]
    assert names(never["binds_edges_only"]) == ["BINDSONLY", "MADEUNSIGNED"], "an override to binds is applied before the filter, as in the build"
    assert names(never["no_edge_into_a_g_alpha_and_in_omnipath"]) == ["NOEDGE"]
    assert names(never["no_edge_into_a_g_alpha_and_absent_from_omnipath"]) == ["ABSENT"]
    kept = receptors["keeps_a_signed_edge_after_the_filter"]
    assert kept["receptors"] == ["FLIPPED", "KEEPS", "KEEPSNEG"]
    assert kept["only_negatively_signed_edges_kept"]["receptors"] == ["FLIPPED", "KEEPSNEG"]
    assert result["annotated_receptors"] == len(FIXTURE_ADMITTED)
    assert sum(receptors[group]["count"] for group in receptors) == len(FIXTURE_ADMITTED)


def test_the_lost_receptors_carry_their_edges_and_admitted_families(tmp_path):
    lost = measure_zero_coupling(*write_fixture_inputs(tmp_path))["receptors"]["signed_edge_before_and_none_after"]
    by_name = {entry["receptor"]: entry for group in ("left_with_no_edge_into_a_g_alpha", "left_with_binds_edges_only")
               for entry in lost[group]["receptors"]}
    assert by_name["LOSTALL"]["signed_edges_before_the_filter"] == ["GNAS (Gs) +1"]
    assert by_name["LOSTALL"]["admitted_families"] == ["Gi/o"]
    assert by_name["COMPLEXED"]["signed_edges_before_the_filter"] == ["GNAO1 (Gi/o) +1"], "only the complex's G alpha counts"
    assert by_name["LOSTBINDS"]["binds_edges_left"] == ["GNAI2"], "a binds row written G alpha first is stored both ways"


def test_the_edge_counts_agree_with_the_builds_own_counter(tmp_path):
    result = measure_zero_coupling(*write_fixture_inputs(tmp_path))
    # before: LOSTALL-GNAS, LOSTBINDS-GNAQ, COMPLEXED-GNAO1, KEEPS-GNAS, KEEPS-GNAQ, KEEPSNEG-GNAI1, FLIPPED-GNAI1
    assert result["signed_receptor_to_g_alpha_edges"] == {"before_the_filter": 7, "after_the_filter": 3, "dropped": 4}
    assert result["build_counters_with_the_filter"]["receptor_g_alpha_edges_dropped_as_unlisted"] == 4
    assert result["build_counters_without_the_filter"]["receptor_g_alpha_edges_dropped_as_unlisted"] == 0
    assert result["curated_override_rows_whose_target_is_a_g_alpha"] == 2
    assert result["build_counters_with_the_filter"]["edges_corrected"] == 2


def test_an_empty_admitted_table_is_refused_rather_than_read_as_no_filter(tmp_path):
    interactions_path, admitted_path, overrides_path = write_fixture_inputs(tmp_path)
    admitted_path.write_text("receptor_gene_symbol,g_alpha_gene_symbol,g_alpha_family,transducer_role\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no admitted pair"):
        measure_zero_coupling(interactions_path, admitted_path, overrides_path)


@pytest.mark.parametrize("interactions_text", ["\t".join(OMNIPATH_FIELDS) + "\n", ""], ids=["header only", "zero bytes"])
def test_an_omnipath_table_with_no_row_is_read_as_it_is(tmp_path, interactions_text):
    """The docstring's promise: an OmniPath table that exists but holds no row gives a record with no edge, every
    annotated receptor absent from OmniPath. Until 28 November 2026 the run stopped with AttributeError, because
    build_signaling_layer returns a frame with no columns when it makes no edge row."""
    interactions_path, admitted_path, overrides_path = write_fixture_inputs(tmp_path)
    interactions_path.write_text(interactions_text, encoding="utf-8")
    output_path = tmp_path / "out" / "zero_coupling.json"
    main(["--omnipath-interactions", str(interactions_path), "--admitted-coupling", str(admitted_path),
          "--curated-edge-sign-overrides", str(overrides_path), "--output", str(output_path)])
    record = json.loads(output_path.read_text(encoding="utf-8"))
    assert record["signed_receptor_to_g_alpha_edges"] == {"before_the_filter": 0, "after_the_filter": 0, "dropped": 0}
    absent_from_omnipath = record["receptors"]["no_signed_edge_before_the_filter"]["no_edge_into_a_g_alpha_and_absent_from_omnipath"]
    assert absent_from_omnipath["receptors"] == sorted(receptor for receptor, _, _, _ in FIXTURE_ADMITTED)
    assert record["receptors"]["signed_edge_before_and_none_after"]["count"] == 0
    assert record["receptors"]["keeps_a_signed_edge_after_the_filter"]["count"] == 0


def test_the_run_writes_the_record_with_the_inputs_hashes(tmp_path):
    interactions_path, admitted_path, overrides_path = write_fixture_inputs(tmp_path)
    output_path = tmp_path / "out" / "zero_coupling.json"
    main(["--omnipath-interactions", str(interactions_path), "--admitted-coupling", str(admitted_path),
          "--curated-edge-sign-overrides", str(overrides_path), "--output", str(output_path)])
    record = json.loads(output_path.read_text(encoding="utf-8"))
    assert record["inputs"]["omnipath_interactions"]["sha256"] == hashlib.sha256(interactions_path.read_bytes()).hexdigest()
    assert record["inputs"]["admitted_coupling"]["bytes"] == admitted_path.stat().st_size
    assert record["inputs"]["admitted_coupling"]["last_commit"] is None, "a file git does not track has no commit"
    assert record["inputs"]["admitted_coupling"]["differs_from_last_commit"] is None
    assert record["build_module"]["path"] == "mechanistic_pathway_learning/graph/build_physiology_graph.py"
    assert record["measurement_script"]["path"] == "experiments/measure_zero_coupling_receptors.py"
    assert "before graph assembly" in record["taken_on"]
    assert record["receptors"]["signed_edge_before_and_none_after"]["count"] == 3


def test_a_missing_input_and_an_output_under_data_are_refused(tmp_path):
    interactions_path, admitted_path, overrides_path = write_fixture_inputs(tmp_path)
    with pytest.raises(FileNotFoundError, match="--curated-edge-sign-overrides"):
        main(["--omnipath-interactions", str(interactions_path), "--admitted-coupling", str(admitted_path),
              "--curated-edge-sign-overrides", str(tmp_path / "absent.csv"), "--output", str(tmp_path / "out.json")])
    with pytest.raises(ValueError, match="outside data/"):
        main(["--omnipath-interactions", str(interactions_path), "--admitted-coupling", str(admitted_path),
              "--curated-edge-sign-overrides", str(overrides_path), "--output", str(REPOSITORY_ROOT / "data" / "zero_coupling.json")])
    assert not (REPOSITORY_ROOT / "data" / "zero_coupling.json").exists()


@pytest.mark.skipif(repository_commit() is None, reason="needs the repository's git history")
def test_a_tracked_input_read_by_a_relative_path_from_another_directory_is_dated_by_its_commit(monkeypatch):
    monkeypatch.chdir(REPOSITORY_ROOT / "configs")
    provenance = file_provenance(Path("admitted_receptor_g_alpha_coupling.csv"))
    assert provenance["last_commit"] is not None and provenance["last_commit_date"] is not None
    assert provenance["sha256"] == hashlib.sha256((REPOSITORY_ROOT / "configs" / "admitted_receptor_g_alpha_coupling.csv").read_bytes()).hexdigest()
