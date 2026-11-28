"""experiments/build_dopaminergic_expression.py and the HPA cluster type it scales atlas cluster 395 against.

The HPA release pinned since 27 November 2026 has no "splatter" cluster type (REFERENCE_CLUSTER_TYPE). Until 28
November 2026 the step then read every count file and stopped inside trimmed_mean_scale_factor with "no gene reaches
minimum_value in both profiles", which does not say that the reference type is missing. These tests run the step's
main() on a small cluster-type table, with the count-file reader replaced by a fixed profile, so no atlas file is read.
"""
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("h5py")  # the step's module imports it; it is in the experiments extra

from experiments import build_dopaminergic_expression as dopaminergic_step  # noqa: E402

GENE_IDS = [f"ENSG{index:011d}" for index in range(40)]
UMI_COUNT_PER_GENE = 100.0
REFERENCE_NCPM_PER_GENE = 10.0


def write_cluster_type_table(path: Path, cluster_types: list[str]) -> Path:
    """A zipped HPA cluster-type table: every gene of GENE_IDS at REFERENCE_NCPM_PER_GENE in each cluster type."""
    rows = [{"Gene": gene_id, "Gene name": gene_id, "Cluster type": cluster_type, "nCPM": REFERENCE_NCPM_PER_GENE}
            for cluster_type in cluster_types for gene_id in GENE_IDS]
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(path.stem, pd.DataFrame(rows).to_csv(sep="\t", index=False))
    return path


def fixed_cluster_counts(h5ad_path: Path, cluster_id: str) -> tuple[pd.Series, dict]:
    """Stands in for cluster_counts: UMI_COUNT_PER_GENE for every gene, without opening h5ad_path."""
    counts = pd.Series(UMI_COUNT_PER_GENE, index=pd.Index(GENE_IDS, name="ensembl_gene_id"))
    description = {"file": str(h5ad_path), "nuclei": 1, "umis": float(counts.sum()), "nuclei_by_donor": {},
                   "is_primary_data": None}
    return counts, description | {"symbols": {gene_id: gene_id for gene_id in GENE_IDS}}


def run_the_step(monkeypatch, tmp_path: Path, cluster_types: list[str]) -> Path:
    """Run main() on a table of these cluster types; return the output path it was given."""
    table_path = write_cluster_type_table(tmp_path / "rna_single_nuclei_cluster_type.tsv.zip", cluster_types)
    output_path = tmp_path / "output" / "dopaminergic.parquet"
    monkeypatch.setattr(dopaminergic_step, "cluster_counts", fixed_cluster_counts)
    monkeypatch.setattr(sys, "argv", ["build_dopaminergic_expression.py", "--h5ad", str(tmp_path / "never_opened.h5ad"),
                                      "--hpa-cluster-type", str(table_path), "--output", str(output_path)])
    dopaminergic_step.main()
    return output_path


def test_a_release_without_the_reference_cluster_type_is_refused_by_name(monkeypatch, tmp_path):
    with pytest.raises(ValueError, match=f"no row of the reference cluster type '{dopaminergic_step.REFERENCE_CLUSTER_TYPE}'") as refusal:
        run_the_step(monkeypatch, tmp_path, ["dopaminergic", "astrocyte"])
    assert "['astrocyte', 'dopaminergic']" in str(refusal.value), "the refusal lists the cluster types the table holds"
    assert not (tmp_path / "output").exists()


def test_the_reference_is_checked_before_any_count_file_is_read(monkeypatch, tmp_path):
    def count_file_reader_that_must_not_run(h5ad_path, cluster_id):
        raise AssertionError("a count file was read before the reference cluster type was checked")
    table_path = write_cluster_type_table(tmp_path / "rna_single_nuclei_cluster_type.tsv.zip", ["dopaminergic"])
    monkeypatch.setattr(dopaminergic_step, "cluster_counts", count_file_reader_that_must_not_run)
    monkeypatch.setattr(sys, "argv", ["build_dopaminergic_expression.py", "--h5ad", str(tmp_path / "never_opened.h5ad"),
                                      "--hpa-cluster-type", str(table_path), "--output", str(tmp_path / "output.parquet")])
    with pytest.raises(ValueError, match="no row of the reference cluster type"):
        dopaminergic_step.main()


def test_a_release_with_the_reference_cluster_type_is_scaled_against_it(monkeypatch, tmp_path):
    output_path = run_the_step(monkeypatch, tmp_path, [dopaminergic_step.REFERENCE_CLUSTER_TYPE, "astrocyte"])
    table = pd.read_parquet(output_path)
    summary = json.loads(output_path.with_suffix(".summary.json").read_text())
    counts_per_million_per_gene = 1e6 / len(GENE_IDS)
    assert summary["reference_cluster_type"] == dopaminergic_step.REFERENCE_CLUSTER_TYPE
    assert summary["scale_factor_cpm_per_ncpm"] == pytest.approx(counts_per_million_per_gene / REFERENCE_NCPM_PER_GENE)
    assert table["ncpm_aligned"].to_numpy() == pytest.approx(REFERENCE_NCPM_PER_GENE)
