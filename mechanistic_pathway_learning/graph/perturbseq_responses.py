"""Genome-wide Perturb-seq in K562 as observations on the graph's regulation edges (decision 9.91).

Replogle et al. 2022 (doi 10.1016/j.cell.2022.05.013) knocked down every expressed gene and every transcription factor of
Lambert et al. 2018 by CRISPRi in K562 cells and read single-cell transcriptomes; the authors publish pseudo-bulk
tables (figshare plus 20029387, CC BY 4.0). This module reads the gemgroup z-normalised pseudo-bulk table
(K562_gwps_normalized_bulk_01.h5ad, 374,587,922 bytes): per perturbation, the mean z-score of each gene expressed at more
than 0.01 UMI per cell, the cells behind it (num_cells_filtered) and the on-target knockdown (fold_expr, the target's
expression in perturbed cells over controls).

An observation on a regulation edge, factor -> target:
  - the factor's perturbation is in the table and its knockdown is confirmed: fold_expr measured and at most 0.7, the
    authors' own criterion ("an on-target knockdown, if measured, of at least 30%"), less a target "not detected",
    which the authors admitted and this reading does not;
  - the target is among the measured genes (expressed in K562);
  - the change is tested per gene from the pseudo-bulk alone: each cell's z-score has mean 0 and variance 1 over the
    control cells of its gemgroup by construction, so under no effect the mean over n perturbed cells has standard
    error 1 / sqrt(n), and z = mean * sqrt(n) is read against the normal distribution, two-sided, with the
    Benjamini-Hochberg correction over the measured genes of the perturbation at 0.05. The authors tested single cells
    with the Anderson-Darling test, which the pseudo-bulk does not allow; this test is cruder and needs the central
    limit theorem on sparse counts (the median perturbation has 166 cells).
A significant change is a positive when its direction is the one the edge's sign implies (a knocked-down activator
lowers its target) and is recorded against the sign otherwise, without counting; no significant change is a negative.
One observation per edge: a factor with several perturbations (its promoters) is read at its strongest knockdown.

K562 is a chronic myeloid leukaemia line, not a neural one, and every observation carries that
(perturbseq_cell_line). A regulation can be real in neurons and silent in K562; the likelihood ratio of
configs/edge_negative_likelihood_ratios.csv (Cusanovich et al. 2014, bound genes that respond to a knockdown: median
7.9%) is measured in another non-neural line and does not correct for the cell type either.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.graph.edge_evidence import symbol_of

DEFAULT_PSEUDOBULK = Path("data/raw/replogle2022/K562_gwps_normalized_bulk_01.h5ad")
REGULATION_RELATION = "regulates_transcription_of"
KNOCKDOWN_FOLD_MAXIMUM = 0.7  # "an on-target knockdown, if measured, of at least 30%" (Replogle et al. 2022, STAR Methods)
FALSE_DISCOVERY_RATE = 0.05
CELL_LINE = "K562"
STATUSES = ("response_agrees", "response_against_sign", "no_response", "knockdown_unconfirmed", "target_not_expressed", "factor_not_perturbed", "not_regulation")


@dataclass
class Pseudobulk:
    """The pieces of the pseudo-bulk table this module reads; z_of_row reads a perturbation's row on demand."""
    perturbation_gene: np.ndarray  # gene symbol of each perturbation row
    fold_expression: np.ndarray
    control_expression: np.ndarray
    cells: np.ndarray
    measured_genes: dict[str, int]  # gene symbol -> column
    path: Path | None = None
    matrix: np.ndarray | None = None  # rows held in memory (tests); otherwise read from path

    def z_of_row(self, row: int) -> np.ndarray:
        if self.matrix is not None:
            return np.asarray(self.matrix[row], dtype=float)
        import h5py

        with h5py.File(self.path, "r") as handle:
            return np.asarray(handle["X"][row], dtype=float)

    def z_of_rows(self, rows: list[int]) -> dict[int, np.ndarray]:
        if self.matrix is not None or not rows:
            return {row: self.z_of_row(row) for row in rows}
        import h5py

        ordered = sorted(set(rows))
        with h5py.File(self.path, "r") as handle:
            block = handle["X"][ordered, :]
        return {row: np.asarray(values, dtype=float) for row, values in zip(ordered, block)}


def _decoded(values) -> np.ndarray:
    return np.array([value.decode() if isinstance(value, bytes) else str(value) for value in values], dtype=object)


def perturbed_gene(identifier: str) -> str:
    """The gene of a perturbation id: '10000_ZBTB46_P1P2_ENSG00000130584' -> 'ZBTB46' (index, symbol, promoters, gene id)."""
    parts = str(identifier).split("_")
    return "_".join(parts[1:-2]) if len(parts) >= 4 else str(identifier)


def read_pseudobulk(path: Path = DEFAULT_PSEUDOBULK) -> Pseudobulk:
    """The observation and gene annotations of the table; the matrix stays on disk."""
    import h5py

    with h5py.File(path, "r") as handle:
        observations = handle["obs"]
        index_name = observations.attrs["_index"]
        perturbations = _decoded(observations[index_name][:])
        genes = handle["var"]
        names = genes["gene_name"]
        if "__categories" in genes and "gene_name" in genes["__categories"]:
            names = _decoded(genes["__categories"]["gene_name"][:])[genes["gene_name"][:]]
        else:
            names = _decoded(names[:])
        return Pseudobulk(perturbation_gene=np.array([perturbed_gene(identifier) for identifier in perturbations], dtype=object),
                          fold_expression=observations["fold_expr"][:].astype(float), control_expression=observations["control_expr"][:].astype(float),
                          cells=observations["num_cells_filtered"][:].astype(float),
                          measured_genes={str(name): column for column, name in enumerate(names)}, path=Path(path))


def benjamini_hochberg(p_values: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values."""
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values)
    ranked = p_values[order] * len(p_values) / np.arange(1, len(p_values) + 1)
    adjusted = np.minimum.accumulate(ranked[::-1])[::-1]
    result = np.empty_like(adjusted)
    result[order] = np.minimum(adjusted, 1.0)
    return result


def two_sided_normal_p(z: np.ndarray) -> np.ndarray:
    from scipy.stats import norm

    return 2.0 * norm.sf(np.abs(np.asarray(z, dtype=float)))


def strongest_knockdown_rows(table: Pseudobulk) -> dict[str, int]:
    """Per perturbed gene, its row with the lowest measured fold expression (a row whose knockdown was not measured is
    kept only when the gene has no measured row)."""
    best: dict[str, tuple[float, int]] = {}
    for row, (gene, fold, control) in enumerate(zip(table.perturbation_gene, table.fold_expression, table.control_expression)):
        measured = np.isfinite(fold) and np.isfinite(control) and control > 0
        key = (fold if measured else math.inf, row)
        if gene not in best or key < best[gene]:
            best[gene] = key
    return {gene: row for gene, (_, row) in best.items()}


def perturbseq_edge_columns(evidence: pd.DataFrame, edge_sign: np.ndarray, table: Pseudobulk) -> pd.DataFrame:
    """Per row of the edge evidence table: perturbseq_negative, perturbseq_positive, perturbseq_status, perturbseq_z (the
    target's test statistic), perturbseq_knockdown (1 - fold expression of the factor) and perturbseq_cell_line."""
    rows_of_factor = strongest_knockdown_rows(table)
    is_regulation = evidence["relation_type"].astype(str).to_numpy() == REGULATION_RELATION
    factors = [symbol_of(source) for source in evidence["source_id"]]
    targets = [symbol_of(target) for target in evidence["target_id"]]
    needed = sorted({rows_of_factor[factor] for factor, regulation in zip(factors, is_regulation) if regulation and factor in rows_of_factor})
    z_rows = table.z_of_rows(needed)
    adjusted = {}
    for row, z_mean in z_rows.items():
        statistic = z_mean * math.sqrt(max(table.cells[row], 0.0))
        adjusted[row] = (statistic, benjamini_hochberg(two_sided_normal_p(statistic)))
    negative = np.zeros(len(evidence), dtype=np.int64)
    positive = np.zeros(len(evidence), dtype=np.int64)
    status = np.full(len(evidence), "not_regulation", dtype=object)
    statistic_column = np.full(len(evidence), np.nan)
    knockdown = np.full(len(evidence), np.nan)
    cell_line = np.full(len(evidence), "", dtype=object)
    signs = np.asarray(edge_sign, dtype=float)
    for position, (regulation, factor, target) in enumerate(zip(is_regulation, factors, targets)):
        if not regulation:
            continue
        row = rows_of_factor.get(factor)
        if row is None:
            status[position] = "factor_not_perturbed"
            continue
        fold = table.fold_expression[row]
        knockdown[position] = 1.0 - fold if np.isfinite(fold) else np.nan
        cell_line[position] = CELL_LINE
        if not (np.isfinite(fold) and np.isfinite(table.control_expression[row]) and table.control_expression[row] > 0 and fold <= KNOCKDOWN_FOLD_MAXIMUM):
            status[position] = "knockdown_unconfirmed"
            continue
        column = table.measured_genes.get(target)
        if column is None:
            status[position] = "target_not_expressed"
            continue
        statistic, q_values = adjusted[row]
        statistic_column[position] = statistic[column]
        if q_values[column] > FALSE_DISCOVERY_RATE:
            status[position], negative[position] = "no_response", 1
        elif -np.sign(statistic[column]) == np.sign(signs[position]):  # knocking down an activator lowers its target
            status[position], positive[position] = "response_agrees", 1
        else:
            status[position] = "response_against_sign"
    return pd.DataFrame({"perturbseq_negative": negative, "perturbseq_positive": positive, "perturbseq_status": status, "perturbseq_z": statistic_column,
                         "perturbseq_knockdown": knockdown, "perturbseq_cell_line": cell_line}, index=evidence.index)
