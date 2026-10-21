"""Cell classes taken from single clusters of the adult human brain atlas, beside the pooled HPA classes (decision 9.76,
the owner, 21 October 2026: "add the Siletti atlas").

Why. The Human Protein Atlas single-nucleus download is at supercluster level: its 34 cluster types are the atlas's
superclusters, so the noradrenergic neurons of the locus coeruleus and the medulla are absorbed into "splatter"
(DBH at most 0.7 nCPM, PHOX2A 0.4), and PHOX2A, which drives DBH, TH and SLC6A2 in those neurons (Morin et al. 1997,
PMID 9115735), fell under the detection threshold in every class. The atlas itself (Siletti et al. 2023, "Transcriptomic
diversity of cell types across the adult human brain", Science 382:eadd7046, PMID 37824663, doi:10.1126/science.add7046)
resolves them: "Our analysis identified 461 clusters and 3313 subclusters organized largely according to developmental
origins and revealing high diversity in midbrain and hindbrain neurons."

The source. The authors publish a genes x clusters aggregate of the final dataset (adult_human_20221007_Pool_Clean.agg.loom,
linked from github.com/linnarsson-lab/adult-human-brain): a loom file whose matrix holds, per gene and cluster, the mean
UMI count per nucleus (its column sums are the clusters' mean total UMI, the "Total UMI" of the authors' cluster
annotation table), with the Ensembl accession of each gene and the cluster id and nucleus count of each column. A
cluster's column divided by its sum and times a million is the cluster's pseudobulk counts per million, the quantity
HPA's nCPM is a normalisation of, and it is placed on the HPA scale as the peripheral classes are: a trimmed mean of M
values of the cluster profile against the mean over the HPA brain classes (peripheral_cell_classes.scaled_to_ncpm).
For a brain cluster against a brain pseudobulk the assumption behind the trimmed mean, that most genes do not differ,
is the one it was made for. The dopaminergic class (experiments/build_dopaminergic_expression.py) scales atlas cluster
395 the same way against HPA's splatter cluster type; the brain-class mean is used here so that every added class is
scaled against the same reference.

The noradrenergic class. CLUSTER_IDS_OF_CLASS names the cluster or clusters a class pools (the mean per nucleus is
weighted by nucleus count when there are several). noradrenergic_neuron is cluster 398 (Splat_398, 2,093 nuclei,
medulla 86.6 percent and pons 12.8 percent by dissection): in the aggregate it ranks first among the 461 clusters in
SLC6A2 (1.71 mean UMI), PHOX2A (0.67) and PHOX2B (1.79), first equal in DBH (0.88, with cluster 399) and third in TH
(2.18, behind the two dopaminergic clusters 395 and 410), so it is the only cluster where the four markers are jointly
high; cluster 399 (DBH 0.88, TH 1.02, SLC6A2 0.50, PHOX2A 0.02) is a medullary group without PHOX2A and is left out.
The authors' subcluster table places the locus coeruleus inside 398: subcluster 872, 122 nuclei, neurotransmitter
"NT-NOR", pons 96.7 percent (the parabrachial dissection, which the dissection notes say overlaps the pontine
structures), top enriched genes PHOX2B-AS1, SLC6A2, DBH, TH, PHOX2A, LINC00682, PHOX2B, SLC18A2. The aggregate is at
cluster level, so the class is the brainstem noradrenergic and adrenergic neurons together (A1, A2, C1, C2 and the
locus coeruleus), not the locus coeruleus alone; a subcluster aggregate would separate them and the authors publish
none.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.peripheral_cell_classes import CLASS_COLUMN_PREFIX, hpa_brain_pseudobulk, scaled_to_ncpm

DEFAULT_SILETTI_AGGREGATE_PATH = Path("data/raw/siletti_cluster_aggregate/adult_human_20221007_Pool_Clean.agg.loom")
CLUSTER_IDS_OF_CLASS = {"noradrenergic_neuron": (398,)}
CLUSTER_CLASSES = tuple(CLUSTER_IDS_OF_CLASS)


def read_cluster_aggregate(loom_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """(Ensembl-indexed mean UMI per nucleus, one column per cluster id; nucleus count per cluster) from the authors'
    aggregate loom. The accession's version suffix is dropped; a gene with several rows keeps its largest."""
    import h5py

    with h5py.File(loom_path, "r") as handle:
        matrix = handle["matrix"][:]
        accessions = handle["row_attrs"]["Accession"][:].astype(str)
        clusters = handle["col_attrs"]["Clusters"][:].astype(int)
        nuclei = handle["col_attrs"]["NCells"][:].astype(int)
    table = pd.DataFrame(matrix, columns=clusters, index=pd.Index([accession.split(".")[0] for accession in accessions], name="ensembl_gene_id"))
    return table.groupby(level=0).max(), pd.Series(nuclei, index=clusters)


def cluster_class_profiles(loom_path: Path, cluster_ids_of_class: dict[str, tuple[int, ...]] = CLUSTER_IDS_OF_CLASS) -> tuple[pd.DataFrame, dict]:
    """(Ensembl-indexed pseudobulk counts per million, one column per class; the nuclei behind each class). A class of
    several clusters takes their mean UMI per nucleus weighted by nucleus count before the counts-per-million step."""
    mean_umi, nuclei = read_cluster_aggregate(Path(loom_path))
    profiles = {}
    nuclei_of_class = {}
    for class_name, cluster_ids in cluster_ids_of_class.items():
        missing = [cluster for cluster in cluster_ids if cluster not in mean_umi.columns]
        if missing:
            raise ValueError(f"{loom_path} has no cluster {missing[0]}")
        weights = nuclei.loc[list(cluster_ids)].astype(float)
        pooled = (mean_umi[list(cluster_ids)] * weights.to_numpy()).sum(axis=1) / float(weights.sum())
        profiles[class_name] = pooled / float(pooled.sum()) * 1e6
        nuclei_of_class[class_name] = int(weights.sum())
    return pd.DataFrame(profiles), nuclei_of_class


def add_atlas_cluster_classes(cell_class_table: pd.DataFrame, loom_path: Path | None = DEFAULT_SILETTI_AGGREGATE_PATH,
                              cluster_ids_of_class: dict[str, tuple[int, ...]] = CLUSTER_IDS_OF_CLASS) -> tuple[pd.DataFrame, dict]:
    """The cell-class table (class_ columns, Ensembl-indexed) with one class_<name> column per atlas cluster class on the
    nCPM scale, joined over the table's own genes; a missing loom adds nothing and the summary says so."""
    summary: dict = {"classes": [], "scale_factor_source_units_per_ncpm": {}, "nuclei": {}, "genes_with_a_value": {}, "siletti_aggregate": None}
    if loom_path is None or not Path(loom_path).exists():
        return cell_class_table, summary
    profiles, nuclei = cluster_class_profiles(Path(loom_path), cluster_ids_of_class)
    reference = hpa_brain_pseudobulk(cell_class_table, excluded_classes=tuple(cluster_ids_of_class))
    columns = []
    for class_name in profiles.columns:
        scaled, factor = scaled_to_ncpm(profiles[[class_name]], profiles[class_name], reference)
        summary["classes"].append(class_name)
        summary["scale_factor_source_units_per_ncpm"][class_name] = factor
        summary["nuclei"][class_name] = nuclei[class_name]
        columns.append(scaled)
    joined_columns = pd.concat(columns, axis=1).add_prefix(CLASS_COLUMN_PREFIX)
    joined = cell_class_table.join(joined_columns, how="left")
    for class_name in profiles.columns:
        summary["genes_with_a_value"][class_name] = int(joined[CLASS_COLUMN_PREFIX + class_name].notna().sum())
    summary["siletti_aggregate"] = str(loom_path)
    return joined, summary
