"""The two stopping statuses scripts/fetch_raw_sources.sh gained on 27 November 2026, after the raw fetch of 23
November brought a Human Protein Atlas release the build cannot read (docs/data_layer_rebuild.md): SHORT, for a body
too small to be a real download, and UNREADABLE, when experiments/check_hpa_downloads.py cannot read the HPA files
with the build's own readers.

The fetch function is taken from the script itself and run by bash against file:// addresses, so the test exercises
the code the script runs rather than a copy of it.
"""
import hashlib
import re
import subprocess
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from experiments.check_hpa_downloads import problems_reading_hpa_downloads
from mechanistic_pathway_learning.graph.brain_expression_descriptors import CELL_CLASS_OF_CLUSTER_TYPE

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FETCH_SCRIPT_TEXT = (REPOSITORY_ROOT / "scripts" / "fetch_raw_sources.sh").read_text()


def fetch_function_and_threshold() -> str:
    """The script's SHORTEST_PLAUSIBLE_DOWNLOAD_BYTES assignment and its fetch() function, as bash source."""
    threshold_line = re.search(r"^SHORTEST_PLAUSIBLE_DOWNLOAD_BYTES=\d+$", FETCH_SCRIPT_TEXT, re.MULTILINE).group(0)
    function_text = re.search(r"^fetch\(\) \{\n.*?^\}\n", FETCH_SCRIPT_TEXT, re.MULTILINE | re.DOTALL).group(0)
    return threshold_line + "\n" + function_text


def run_fetch(tmp_path: Path, source_bytes: bytes, recorded_sha256: str = "-") -> tuple[int, str, Path]:
    """Run the script's fetch() on one file:// source; return its exit status, the report's status and the destination."""
    source_path = tmp_path / "source.bin"
    source_path.write_bytes(source_bytes)
    destination_path = tmp_path / "raw" / "download.bin"
    report_path = tmp_path / "report.tsv"
    report_path.write_text("path\tbytes\tsha256\trecorded_sha256\tstatus\n")
    bash_source = (f"set -uo pipefail\nreport_path='{report_path}'\n{fetch_function_and_threshold()}\n"
                   f"fetch '{destination_path}' 'file://{source_path}' '{recorded_sha256}'\n")
    completed = subprocess.run(["bash", "-c", bash_source], capture_output=True, text=True)
    report_status = report_path.read_text().splitlines()[-1].split("\t")[-1]
    return completed.returncode, report_status, destination_path


def test_a_short_body_with_no_recorded_hash_is_set_aside_and_stops(tmp_path):
    exit_status, report_status, destination_path = run_fetch(tmp_path, b"error\n")
    assert (exit_status, report_status) == (1, "SHORT")
    assert not destination_path.exists()
    assert destination_path.with_name(destination_path.name + ".short").read_bytes() == b"error\n"


def test_a_short_body_whose_hash_is_the_recorded_one_is_kept(tmp_path):
    small_but_pinned = b"x" * 10
    exit_status, report_status, destination_path = run_fetch(
        tmp_path, small_but_pinned, hashlib.sha256(small_but_pinned).hexdigest())
    assert (exit_status, report_status) == (0, "fetched")
    assert destination_path.read_bytes() == small_but_pinned


def test_a_body_at_the_threshold_is_an_ordinary_download(tmp_path):
    threshold = int(re.search(r"^SHORTEST_PLAUSIBLE_DOWNLOAD_BYTES=(\d+)$", FETCH_SCRIPT_TEXT, re.MULTILINE).group(1))
    exit_status, report_status, destination_path = run_fetch(tmp_path, b"y" * threshold)
    assert (exit_status, report_status) == (0, "fetched")
    assert destination_path.stat().st_size == threshold


def test_the_script_stops_on_the_new_statuses_and_checks_hpa_after_fetching_it():
    assert re.search(r"grep -q -P '\\t\(FAILED\|SHORT\|UNREADABLE\)\$' \"\$report_path\"", FETCH_SCRIPT_TEXT)
    second_hpa_fetch = FETCH_SCRIPT_TEXT.index('fetch "$hpa_cluster_type_table_path"')
    hpa_check = FETCH_SCRIPT_TEXT.index("experiments/check_hpa_downloads.py --region-table")
    unreadable_row = FETCH_SCRIPT_TEXT.index("UNREADABLE\\n' \"$hpa_cluster_type_table_path\"")
    assert second_hpa_fetch < hpa_check < unreadable_row


def write_zipped_table(path: Path, table: pd.DataFrame) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(path.stem, table.to_csv(sep="\t", index=False))
    return path


@pytest.fixture
def region_table_path(tmp_path):
    return write_zipped_table(tmp_path / "rna_brain_region_hpa.tsv.zip", pd.DataFrame({
        "Gene": ["ENSG01", "ENSG01"], "Gene name": ["A", "A"], "Brain region": ["cerebellum", "pons"],
        "TPM": [1.0, 2.0], "pTPM": [1.0, 2.0], "nTPM": [1.0, 2.0]}))


def test_cluster_types_the_code_maps_read(tmp_path, region_table_path):
    mapped_cluster_type = sorted(CELL_CLASS_OF_CLUSTER_TYPE)[0]
    cluster_type_table_path = write_zipped_table(tmp_path / "rna_single_nuclei_cluster_type.tsv.zip", pd.DataFrame({
        "Gene": ["ENSG01"], "Gene name": ["A"], "Cluster type": [mapped_cluster_type], "nCPM": [3.0]}))
    assert problems_reading_hpa_downloads(region_table_path, cluster_type_table_path) == []


def test_a_cluster_type_the_code_does_not_map_is_named(tmp_path, region_table_path):
    cluster_type_table_path = write_zipped_table(tmp_path / "rna_single_nuclei_cluster_type.tsv.zip", pd.DataFrame({
        "Gene": ["ENSG01"], "Gene name": ["A"], "Cluster type": ["a cluster type of a later release"], "nCPM": [3.0]}))
    problems = problems_reading_hpa_downloads(region_table_path, cluster_type_table_path)
    assert len(problems) == 1
    assert "cluster types with no cell class" in problems[0]
    assert "a cluster type of a later release" in problems[0]


def test_with_the_dopaminergic_reference_a_release_without_it_is_named(tmp_path, region_table_path):
    """--with-dopaminergic-reference (28 November 2026): a cluster-type file the base graph's readers accept but
    experiments/build_dopaminergic_expression.py cannot scale against is named at fetch time."""
    from experiments.build_dopaminergic_expression import REFERENCE_CLUSTER_TYPE
    mapped_cluster_type_other_than_the_reference = next(
        cluster_type for cluster_type in sorted(CELL_CLASS_OF_CLUSTER_TYPE) if cluster_type != REFERENCE_CLUSTER_TYPE)
    cluster_type_table_path = write_zipped_table(tmp_path / "rna_single_nuclei_cluster_type.tsv.zip", pd.DataFrame({
        "Gene": ["ENSG01"], "Gene name": ["A"], "Cluster type": [mapped_cluster_type_other_than_the_reference], "nCPM": [3.0]}))
    assert problems_reading_hpa_downloads(region_table_path, cluster_type_table_path) == [], "without the flag, as before"
    problems = problems_reading_hpa_downloads(region_table_path, cluster_type_table_path, check_dopaminergic_reference=True)
    assert len(problems) == 1
    assert f"reference cluster type {REFERENCE_CLUSTER_TYPE!r}" in problems[0]
    assert mapped_cluster_type_other_than_the_reference in problems[0]


def test_with_the_dopaminergic_reference_a_release_holding_it_reads(tmp_path, region_table_path):
    from experiments.build_dopaminergic_expression import REFERENCE_CLUSTER_TYPE
    assert REFERENCE_CLUSTER_TYPE in CELL_CLASS_OF_CLUSTER_TYPE
    cluster_type_table_path = write_zipped_table(tmp_path / "rna_single_nuclei_cluster_type.tsv.zip", pd.DataFrame({
        "Gene": ["ENSG01"], "Gene name": ["A"], "Cluster type": [REFERENCE_CLUSTER_TYPE], "nCPM": [3.0]}))
    assert problems_reading_hpa_downloads(region_table_path, cluster_type_table_path, check_dopaminergic_reference=True) == []


def test_the_script_asks_for_the_dopaminergic_reference_under_with_cellxgene_alone():
    """The flag is set from the script's own block, run by bash, and the HPA check is given it."""
    flag_block = re.search(r'^hpa_check_dopaminergic_reference_flag="".*?^fi\n', FETCH_SCRIPT_TEXT, re.MULTILINE | re.DOTALL).group(0)
    for with_cellxgene, expected_flag in (("yes", "--with-dopaminergic-reference"), ("no", "")):
        bash_source = f'set -u\nwith_cellxgene="{with_cellxgene}"\n{flag_block}printf "%s" "$hpa_check_dopaminergic_reference_flag"\n'
        completed = subprocess.run(["bash", "-c", bash_source], capture_output=True, text=True, check=True)
        assert completed.stdout == expected_flag, with_cellxgene
    check_line = next(line for line in FETCH_SCRIPT_TEXT.splitlines() if "experiments/check_hpa_downloads.py --region-table" in line)
    assert check_line.rstrip().endswith("$hpa_check_dopaminergic_reference_flag; then")
    assert FETCH_SCRIPT_TEXT.index(flag_block) < FETCH_SCRIPT_TEXT.index(check_line)
