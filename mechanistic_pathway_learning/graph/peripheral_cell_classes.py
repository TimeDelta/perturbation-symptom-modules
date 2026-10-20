"""Peripheral endocrine cell classes beside the brain classes, and the per-gene expression check the transcription gate
reads (decision 9.76, the owner, 20 October 2026: "add the thyroid, pineal, pancreatic, etc. cell types").

Why they exist. Four of the sixteen transcription factors whose regulons the build dropped as not brain expressed act
through a peripheral organ whose product reaches the brain: FOXE1 drives thyroid hormone synthesis (TG, TPO, SLC5A5,
TSHR; the graph carries the route in through SLC16A2 and DIO2), CRX drives AANAT and ASMT in the pineal (melatonin),
ALX3 drives INS and SST in the islet, and ALX1 drives PRL in the pituitary. A factor at 0 in every brain class has
nowhere to act in a brain-only channel; a class for the organ gives its regulon a channel where it is expressed, and the
extracellular pool (brain_expression_weights.extracellular_pool_nodes) carries a product that is an extracellular
metabolite - thyroxine, triiodothyronine, melatonin - into every other class. A peptide hormone (insulin, somatostatin,
prolactin) is a protein node, which the pool does not carry, so the islet and pituitary classes propagate their own
regulons and the hormone's receptors downstream at the organ's weights only; that limit is stated here and in the
decision row rather than hidden.

The classes and their sources:

  thyroid           GTEx v10 median TPM, tissue Thyroid
  pancreatic_islet  GTEx v10 median TPM, tissue Pancreas_Islets (v10 reports the islets apart from the acini)
  pituitary         GTEx v10 median TPM, tissue Pituitary
  pineal            FANTOM5 CAGE of two adult pineal bodies (donors of 76 and 60 years), as Expression Atlas E-MTAB-3358
                    reports it per gene (tags per million; the two replicates averaged by Expression Atlas). GTEx and
                    the Human Protein Atlas sample no pineal.

How a tissue-level class is made commensurate with the single-nucleus classes. The brain classes are Human Protein
Atlas single-nucleus pseudobulk nCPM, and a gene's weight in a class is its expression relative to its largest class
with a half-saturation at HPA's detection threshold of 1 nCPM (brain_expression_weights.relative_expression_weights), so
the peripheral columns have to sit on the nCPM scale before the maximum over classes is taken. Each source is placed
there by the trimmed mean of M values (brain_expression_descriptors.trimmed_mean_scale_factor, the step the dopaminergic
class already uses), with the source's own adult brain samples as the values and the mean over the HPA brain classes as
the reference: for GTEx the mean of the thirteen brain tissue medians, for FANTOM5 the mean of its adult brain regions.
The factor so found divides the source's peripheral columns. What this fixes is the scale: how many of a source's units
make one nCPM. What it cannot fix is per gene. A bulk tissue is a mixture, so a product of one cell type is diluted by
stroma, blood and, in the pituitary, the other endocrine lineages, and a stromal gene is counted that the specific cell
does not express; RNA-seq TPM is normalised by transcript length and CAGE and single-nucleus counts are not; and the
nuclear transcriptome of a nucleus differs from the whole-cell transcriptome of a tissue. The TMM assumption that most
genes are not differentially expressed between the paired brain profiles holds only roughly for a bulk tissue against
a pseudobulk of sorted classes. The limit, stated plainly: a peripheral class's weight is right to within the scale and
wrong by the composition of the tissue, so it says whether the organ expresses a gene and roughly how strongly against
the brain classes, and it does not resolve which of the organ's cells does. For the two uses the classes were added for
this is enough: a gene at 0 in a tissue is at 0 in every cell of it, which is what the transcription gate asks, and a
tissue-specific factor such as FOXE1 (164 TPM in thyroid, 0 in every brain class) takes a weight near 1 in its organ
whatever the factor, since the weight is relative to the gene's own largest class.

A gene absent from a source gets a missing value in that source's classes, as a gene absent from the HPA table does,
which the weight builder reads as weight 1 (nothing is known, so nothing is blocked). Expression Atlas lists the
protein-coding genes with a tag above 0 in at least one tissue, so a protein-coding gene absent from it is either
without a CAGE peak or silent in every FANTOM5 tissue, and the two cannot be told apart; it is read as unknown.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.brain_expression_descriptors import GTEX_BRAIN_TISSUE_PREFIX, trimmed_mean_scale_factor

GTEX_TISSUE_OF_CLASS = {"thyroid": "Thyroid", "pancreatic_islet": "Pancreas_Islets", "pituitary": "Pituitary"}
EXPRESSION_ATLAS_COLUMN_OF_CLASS = {"pineal": "adult, pineal body"}
# the FANTOM5 adult brain regions whose mean is the source's brain profile for the scale factor (the pineal, the
# pituitary, the spinal cord and the olfactory apparatus are not among them)
EXPRESSION_ATLAS_ADULT_BRAIN_COLUMNS = (
    "adult, amygdala", "adult, brain", "adult, caudate nucleus", "adult, cerebellum", "adult, diencephalon", "adult, dorsal thalamus",
    "adult, globus pallidus", "adult, hippocampal formation", "adult, locus ceruleus", "adult, medulla oblongata", "adult, middle frontal gyrus",
    "adult, middle temporal gyrus", "adult, occipital cortex", "adult, occipital lobe", "adult, parietal lobe", "adult, putamen",
    "adult, substantia nigra")
PERIPHERAL_CLASSES = tuple(GTEX_TISSUE_OF_CLASS) + tuple(EXPRESSION_ATLAS_COLUMN_OF_CLASS)
CLASS_COLUMN_PREFIX = "class_"
DEFAULT_GTEX_PATH = Path("data/raw/gtex/GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz")
DEFAULT_EXPRESSION_ATLAS_PATH = Path("data/raw/expression_atlas/E-MTAB-3358/E-MTAB-3358-tpms.tsv")


def gtex_profiles(gct_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """(Ensembl-indexed median TPM of the GTEx tissues of GTEX_TISSUE_OF_CLASS, columns named by class; the mean over
    the brain tissues per gene). A gene with several Ensembl versions keeps the largest value."""
    table = pd.read_csv(gct_path, sep="\t", skiprows=2)
    missing = [tissue for tissue in GTEX_TISSUE_OF_CLASS.values() if tissue not in table.columns]
    if missing:
        raise ValueError(f"{gct_path} has no column {missing[0]}")
    brain_columns = [column for column in table.columns if column.startswith(GTEX_BRAIN_TISSUE_PREFIX)]
    if not brain_columns:
        raise ValueError(f"{gct_path} has no columns starting with {GTEX_BRAIN_TISSUE_PREFIX}")
    ensembl = table["Name"].astype(str).str.split(".").str[0]
    peripheral = pd.DataFrame({class_name: table[tissue].astype(float).to_numpy() for class_name, tissue in GTEX_TISSUE_OF_CLASS.items()})
    peripheral["brain_mean"] = table[brain_columns].astype(float).mean(axis=1).to_numpy()
    peripheral.index = pd.Index(ensembl, name="ensembl_gene_id")
    peripheral = peripheral.groupby(level=0).max()
    return peripheral[list(GTEX_TISSUE_OF_CLASS)], peripheral["brain_mean"]


def expression_atlas_profiles(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """(Ensembl-indexed tags per million of the Expression Atlas columns of EXPRESSION_ATLAS_COLUMN_OF_CLASS, named by
    class; the mean over the adult brain columns). A blank cell is a gene below the download's cutoff of 0, read as 0."""
    table = pd.read_csv(path, sep="\t", comment="#")
    needed = list(EXPRESSION_ATLAS_COLUMN_OF_CLASS.values()) + list(EXPRESSION_ATLAS_ADULT_BRAIN_COLUMNS)
    missing = [column for column in needed if column not in table.columns]
    if missing:
        raise ValueError(f"{path} has no column {missing[0]!r}")
    values = table[needed].astype(float).fillna(0.0)
    values.index = pd.Index(table["Gene ID"].astype(str), name="ensembl_gene_id")
    values = values.groupby(level=0).max()
    profiles = pd.DataFrame({class_name: values[column] for class_name, column in EXPRESSION_ATLAS_COLUMN_OF_CLASS.items()})
    return profiles, values[list(EXPRESSION_ATLAS_ADULT_BRAIN_COLUMNS)].mean(axis=1)


def hpa_brain_pseudobulk(cell_class_table: pd.DataFrame) -> pd.Series:
    """The mean nCPM over the brain cell classes per gene, the reference the scale factors are estimated against."""
    columns = [column for column in cell_class_table.columns if column.startswith(CLASS_COLUMN_PREFIX)]
    if not columns:
        raise ValueError("the cell-class table has no class_ columns")
    return cell_class_table[columns].astype(float).mean(axis=1)


def scaled_to_ncpm(profiles: pd.DataFrame, source_brain: pd.Series, reference_brain: pd.Series) -> tuple[pd.DataFrame, float]:
    """(profiles divided by the source's scale factor, the factor): the trimmed mean of M values of the source's brain
    profile against the reference brain profile, so that the result is on the reference's nCPM scale."""
    factor = trimmed_mean_scale_factor(source_brain.dropna(), reference_brain.dropna())
    return profiles / factor, factor


def peripheral_class_table(cell_class_table: pd.DataFrame, gct_path: Path | None = DEFAULT_GTEX_PATH,
                           expression_atlas_path: Path | None = DEFAULT_EXPRESSION_ATLAS_PATH) -> tuple[pd.DataFrame, dict]:
    """(Ensembl-indexed table with one class_<name> column per peripheral class on the nCPM scale, a summary of the scale
    factors and gene counts). A source whose path is None or absent contributes no column, and the summary says so."""
    reference = hpa_brain_pseudobulk(cell_class_table)
    columns: list[pd.DataFrame] = []
    summary: dict = {"classes": [], "scale_factor_source_units_per_ncpm": {}, "genes_with_a_value": {}}
    sources = ((gct_path, gtex_profiles, "gtex"), (expression_atlas_path, expression_atlas_profiles, "expression_atlas_fantom5"))
    for path, reader, name in sources:
        if path is None or not Path(path).exists():
            summary[name] = None
            continue
        profiles, source_brain = reader(Path(path))
        scaled, factor = scaled_to_ncpm(profiles, source_brain, reference)
        summary[name] = str(path)
        summary["scale_factor_source_units_per_ncpm"][name] = factor
        for class_name in scaled.columns:
            summary["classes"].append(class_name)
            summary["genes_with_a_value"][class_name] = int(scaled[class_name].notna().sum())
        columns.append(scaled.add_prefix(CLASS_COLUMN_PREFIX))
    if not columns:
        return pd.DataFrame(index=pd.Index([], name="ensembl_gene_id")), summary
    return pd.concat(columns, axis=1).rename_axis("ensembl_gene_id"), summary


def add_peripheral_classes(cell_class_table: pd.DataFrame, gct_path: Path | None = DEFAULT_GTEX_PATH,
                           expression_atlas_path: Path | None = DEFAULT_EXPRESSION_ATLAS_PATH) -> tuple[pd.DataFrame, dict]:
    """The cell-class table (class_ columns, Ensembl-indexed) with the peripheral classes joined on over its own genes:
    a gene the brain table lacks stays unknown in every class, so the gene set the weights cover does not change, and a
    gene a peripheral source lacks is missing in that class, as the dopaminergic join leaves a gene its profile lacks."""
    peripheral, summary = peripheral_class_table(cell_class_table, gct_path, expression_atlas_path)
    if peripheral.empty:
        return cell_class_table, summary
    return cell_class_table.join(peripheral, how="left"), summary
