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
  pineal            GEO series GSE100472, "Next Generation Sequencing Study of Circadian Changes in Transcriptome of
                    Human Pineal Gland" (Bozinoski, Klein, Mason and Coon; NICHD; glands from the NDRI): RNA-seq of six
                    human pineal glands, two from deaths at mid-day (GSM2684714, GSM2684715) and four at midnight
                    (GSM2684716 to GSM2684719). GEO's NCBI-generated raw counts (GRCh38.p13, annotation release
                    109.20190905) are turned into counts per million per sample and averaged over the six glands, so
                    the column is a 24-hour-ish mean weighted two day to four night: a night-high gene such as AANAT
                    sits between its day and night levels, nearer the night. The gene is keyed by the Ensembl id of
                    NCBI's annotation table; a GeneID without one is dropped and, where several GeneIDs share an
                    Ensembl id, the largest mean is kept. GTEx and the Human Protein Atlas sample no pineal. The
                    files cannot be fetched by a script (GEO refuses automated readers); the owner supplied them.

How a tissue-level class is made commensurate with the single-nucleus classes. The brain classes are Human Protein
Atlas single-nucleus pseudobulk nCPM, and a gene's weight in a class is its expression relative to its largest class
with a half-saturation at HPA's detection threshold of 1 nCPM (brain_expression_weights.relative_expression_weights), so
the peripheral columns have to sit on the nCPM scale before the maximum over classes is taken. Each source is placed
there by the trimmed mean of M values (brain_expression_descriptors.trimmed_mean_scale_factor, the step the dopaminergic
class already uses), with the source's own adult brain samples as the values and the mean over the HPA brain classes as
the reference: for GTEx the mean of the thirteen brain tissue medians. The factor so found divides the source's
peripheral columns. The GEO series has no brain sample, so the pineal's factor is estimated from the pineal profile
itself against the HPA brain-class mean; that rests on most genes not differing between the pineal and the brain
pseudobulk, which is the assumption the trimmed mean already makes for every bulk tissue here, and the pineal is brain
tissue (the epithalamus), so the assumption is at least as defensible for it as for the thyroid. What the factor fixes
is the scale: how many of a source's units make one nCPM. What it cannot fix is per gene. A bulk tissue is a mixture,
so a product of one cell type is diluted by stroma, blood and, in the pituitary, the other endocrine lineages, and a
stromal gene is counted that the specific cell does not express; RNA-seq TPM is normalised by transcript length and
single-nucleus counts are not (the pineal column is CPM, which is not length-normalised either); and the nuclear
transcriptome of a nucleus differs from the whole-cell transcriptome of a tissue. The limit, stated plainly: a
peripheral class's weight is right to within the scale and wrong by the composition of the tissue, so it says whether
the organ expresses a gene and roughly how strongly against the brain classes, and it does not resolve which of the
organ's cells does. For the two uses the classes were added for this is enough: a gene at 0 in a tissue is at 0 in
every cell of it, which is what the transcription gate asks, and a tissue-specific factor such as FOXE1 (164 TPM in
thyroid, 0 in every brain class) takes a weight near 1 in its organ whatever the factor, since the weight is relative
to the gene's own largest class.

A gene absent from a source gets a missing value in that source's classes, as a gene absent from the HPA table does,
which the weight builder reads as weight 1 (nothing is known, so nothing is blocked). Before 21 October 2026 the pineal
column came from FANTOM5 CAGE through Expression Atlas E-MTAB-3358, whose gene-level table put genes with processed
pseudogenes (GAPDH, ACTB, EEF1A1) near 0 in every tissue and DDC at 0 in the pineal and lacked 1,222 of the graph's
genes; the owner fetched GSE100472 and it was replaced.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.brain_expression_descriptors import GTEX_BRAIN_TISSUE_PREFIX, trimmed_mean_scale_factor

GTEX_TISSUE_OF_CLASS = {"thyroid": "Thyroid", "pancreatic_islet": "Pancreas_Islets", "pituitary": "Pituitary"}
PINEAL_CLASS = "pineal"
GEO_PINEAL_SAMPLES = ("GSM2684714", "GSM2684715", "GSM2684716", "GSM2684717", "GSM2684718", "GSM2684719")  # two day, four night
PERIPHERAL_CLASSES = tuple(GTEX_TISSUE_OF_CLASS) + (PINEAL_CLASS,)
CLASS_COLUMN_PREFIX = "class_"
DEFAULT_GTEX_PATH = Path("data/raw/gtex/GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz")
DEFAULT_GEO_PINEAL_DIRECTORY = Path("data/raw/geo/GSE100472")
GEO_PINEAL_COUNTS_FILE = "GSE100472_raw_counts_GRCh38.p13_NCBI.tsv.gz"
GEO_PINEAL_ANNOTATION_FILE = "Human.GRCh38.p13.annot.tsv.gz"


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


def geo_pineal_profile(directory: Path) -> pd.DataFrame:
    """Ensembl-indexed mean counts per million over the six pineal glands of GSE100472, one column named PINEAL_CLASS.

    Reads GEO's raw count table (GeneID by sample) and NCBI's annotation table (GeneID to EnsemblGeneID); each sample's
    counts are divided by its column sum and multiplied by a million, the six are averaged, a GeneID without an Ensembl
    id is dropped and the largest mean is kept where several GeneIDs share one."""
    directory = Path(directory)
    counts = pd.read_csv(directory / GEO_PINEAL_COUNTS_FILE, sep="\t")
    missing = [sample for sample in GEO_PINEAL_SAMPLES if sample not in counts.columns]
    if missing:
        raise ValueError(f"{directory / GEO_PINEAL_COUNTS_FILE} has no column {missing[0]}")
    annotation = pd.read_csv(directory / GEO_PINEAL_ANNOTATION_FILE, sep="\t", usecols=["GeneID", "EnsemblGeneID"], dtype=str)
    per_sample = counts[list(GEO_PINEAL_SAMPLES)].astype(float)
    cpm = per_sample.div(per_sample.sum(axis=0), axis=1) * 1e6
    table = pd.DataFrame({"GeneID": counts["GeneID"].astype(str), PINEAL_CLASS: cpm.mean(axis=1).to_numpy()})
    table = table.merge(annotation.dropna(subset=["EnsemblGeneID"]), on="GeneID", how="inner")
    profile = table.groupby("EnsemblGeneID")[[PINEAL_CLASS]].max()
    return profile.rename_axis("ensembl_gene_id")


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
                           geo_pineal_directory: Path | None = DEFAULT_GEO_PINEAL_DIRECTORY) -> tuple[pd.DataFrame, dict]:
    """(Ensembl-indexed table with one class_<name> column per peripheral class on the nCPM scale, a summary of the scale
    factors and gene counts). A source whose path is None or absent contributes no column, and the summary says so."""
    reference = hpa_brain_pseudobulk(cell_class_table)
    columns: list[pd.DataFrame] = []
    summary: dict = {"classes": [], "scale_factor_source_units_per_ncpm": {}, "genes_with_a_value": {}}
    if gct_path is not None and Path(gct_path).exists():
        profiles, source_brain = gtex_profiles(Path(gct_path))
        scaled, factor = scaled_to_ncpm(profiles, source_brain, reference)
        summary["gtex"] = str(gct_path)
        summary["scale_factor_source_units_per_ncpm"]["gtex"] = factor
        columns.append(scaled)
    else:
        summary["gtex"] = None
    pineal_counts = None if geo_pineal_directory is None else Path(geo_pineal_directory) / GEO_PINEAL_COUNTS_FILE
    if pineal_counts is not None and pineal_counts.exists() and (Path(geo_pineal_directory) / GEO_PINEAL_ANNOTATION_FILE).exists():
        profile = geo_pineal_profile(Path(geo_pineal_directory))
        # no brain sample in the series: the pineal profile itself is the value the factor is estimated from (module docstring)
        scaled, factor = scaled_to_ncpm(profile, profile[PINEAL_CLASS], reference)
        summary["geo_pineal"] = str(geo_pineal_directory)
        summary["scale_factor_source_units_per_ncpm"]["geo_pineal"] = factor
        columns.append(scaled)
    else:
        summary["geo_pineal"] = None
    for scaled in columns:
        for class_name in scaled.columns:
            summary["classes"].append(class_name)
            summary["genes_with_a_value"][class_name] = int(scaled[class_name].notna().sum())
    if not columns:
        return pd.DataFrame(index=pd.Index([], name="ensembl_gene_id")), summary
    return pd.concat([column.add_prefix(CLASS_COLUMN_PREFIX) for column in columns], axis=1).rename_axis("ensembl_gene_id"), summary


def add_peripheral_classes(cell_class_table: pd.DataFrame, gct_path: Path | None = DEFAULT_GTEX_PATH,
                           geo_pineal_directory: Path | None = DEFAULT_GEO_PINEAL_DIRECTORY) -> tuple[pd.DataFrame, dict]:
    """The cell-class table (class_ columns, Ensembl-indexed) with the peripheral classes joined on over its own genes:
    a gene the brain table lacks stays unknown in every class, so the gene set the weights cover does not change, and a
    gene a peripheral source lacks is missing in that class, as the dopaminergic join leaves a gene its profile lacks."""
    peripheral, summary = peripheral_class_table(cell_class_table, gct_path, geo_pineal_directory)
    if peripheral.empty:
        return cell_class_table, summary
    return cell_class_table.join(peripheral, how="left"), summary
