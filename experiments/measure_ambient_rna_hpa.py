"""Ambient RNA in HPA's single-nucleus brain cluster types, and what it can and cannot do to the VAMP1 share.

Written for the ambient RNA check of 24 October 2026 (decision 9.68; graph/brain_expression_weights.py docstring).
It reads only the HPA cluster-type table and prints; it writes nothing.

1. Off-target signal of markers: for genes confined to one cell type, the nCPM in other cluster types as a fraction
   of the on-target value. Ambient RNA, and doublets, give that fraction a floor.
2. The floor across all genes: how many expressed genes are at 1 nCPM or more in every cluster type. This does not by
   itself separate ambient RNA from broad expression.
3. VAMP1 and VAMP2 per cluster type, and the class value the graph takes (each gene's largest nCPM over a class's
   cluster types, hpa_cell_class_table), so a class share can be traced to the cluster types that set it.
4. The mixing bound: if a cluster type's profile is (1 - c) * own + c * pooled, its VAMP1 share lies between its own
   share and the pooled share, so ambient RNA cannot push a share below the pooled one. The pooled profile is stood in
   for by the unweighted mean over cluster types; the real pool weights by nuclei.

Usage (from the repository root):
  PYTHONPATH=. python experiments/measure_ambient_rna_hpa.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.brain_expression_descriptors import CELL_CLASS_OF_CLUSTER_TYPE, read_zipped_table

DEFAULT_CLUSTER_TYPE_TABLE = Path("data/raw/hpa/rna_single_nuclei_cluster_type/rna_single_nuclei_cluster_type.tsv.zip")
NEURON_CLASSES = ("excitatory_neuron", "cortical_interneuron", "medium_spiny_neuron", "other_inhibitory_neuron", "other_neuron")
# marker gene -> the cluster type it belongs to, or None for "the cluster type where it is highest"
MARKER_ON_TARGET_CLUSTER_TYPE = {
    "MBP": "oligodendrocyte", "PLP1": "oligodendrocyte", "MOBP": "oligodendrocyte",
    "GFAP": "astrocyte", "AQP4": "astrocyte", "SLC1A2": "astrocyte",
    "P2RY12": "central nervous system macrophage", "CLDN5": "endothelial cell",
    "HBB": None,  # red cells have no nucleus, so haemoglobin RNA in a nucleus droplet is most likely ambient
}
NEURONAL_MARKERS = ("SNAP25", "SYT1", "RBFOX3", "GAD1", "SLC17A7")  # read in glial cluster types only
FOREBRAIN_EXCITATORY_CLUSTER_TYPES = ("upper-layer intratelencephalic", "deep-layer intratelencephalic", "deep-layer near-projecting",
                                      "deep-layer corticothalamic and 6b", "hippocampal CA1-3", "hippocampal CA4",
                                      "hippocampal dentate gyrus", "amygdala excitatory")
CORTICAL_INTERNEURON_CLUSTER_TYPES = ("MGE interneuron", "CGE interneuron", "LAMP5-LHX6 and Chandelier")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cluster-type-table", type=Path, default=DEFAULT_CLUSTER_TYPE_TABLE)
    arguments = parser.parse_args()

    long_table = read_zipped_table(arguments.cluster_type_table)
    ncpm_by_cluster_type = long_table.pivot_table(index="Gene name", columns="Cluster type", values="nCPM", aggfunc="max")
    cluster_types = list(ncpm_by_cluster_type.columns)
    neuron_cluster_types = [name for name in cluster_types if CELL_CLASS_OF_CLUSTER_TYPE[name] in NEURON_CLASSES]
    glial_cluster_types = [name for name in cluster_types if name not in neuron_cluster_types]

    print("1. off-target nCPM of markers, as a fraction of the on-target value")
    for gene, on_target_cluster_type in MARKER_ON_TARGET_CLUSTER_TYPE.items():
        values = ncpm_by_cluster_type.loc[gene]
        top_cluster_type = on_target_cluster_type or values.idxmax()
        off_target = values.drop(index=[top_cluster_type])
        print(f"  {gene:7s} top {top_cluster_type} {values[top_cluster_type]:.0f} nCPM | other cluster types: median "
              f"{off_target.median():.1f} nCPM ({off_target.median() / values[top_cluster_type]:.2%} of top), "
              f"largest {off_target.max():.1f} ({off_target.idxmax()})")
    for gene in NEURONAL_MARKERS:
        values = ncpm_by_cluster_type.loc[gene]
        in_glia = values[glial_cluster_types]
        print(f"  {gene:7s} top {values.idxmax()} {values.max():.0f} nCPM | glial cluster types: median {in_glia.median():.1f} nCPM "
              f"({in_glia.median() / values.max():.2%} of top), largest {in_glia.max():.1f} ({in_glia.idxmax()})")

    expressed_somewhere = (ncpm_by_cluster_type >= 1.0).any(axis=1)
    expressed_everywhere = (ncpm_by_cluster_type >= 1.0).all(axis=1)
    lowest_value = ncpm_by_cluster_type[expressed_somewhere].min(axis=1)
    print(f"\n2. genes at >= 1 nCPM in every one of {len(cluster_types)} cluster types: {int(expressed_everywhere.sum())} of "
          f"{int(expressed_somewhere.sum())} expressed somewhere ({expressed_everywhere.sum() / expressed_somewhere.sum():.1%}); "
          f"lowest cluster-type value of an expressed gene: median {lowest_value.median():.2f} nCPM")

    pair = ncpm_by_cluster_type.loc[["VAMP1", "VAMP2"]].T
    pair["vamp1_share"] = pair.VAMP1 / (pair.VAMP1 + pair.VAMP2)
    pair["cell_class"] = [CELL_CLASS_OF_CLUSTER_TYPE[name] for name in pair.index]
    print("\n3. VAMP1 and VAMP2 by neuronal cluster type, by VAMP1 share")
    print(pair.loc[neuron_cluster_types].sort_values("vamp1_share", ascending=False).round(3).to_string())
    for cell_class in NEURON_CLASSES:
        members = pair[pair.cell_class == cell_class]
        class_share = members.VAMP1.max() / (members.VAMP1.max() + members.VAMP2.max())
        print(f"  {cell_class}: class value VAMP1 {members.VAMP1.max():.1f} ({members.VAMP1.idxmax()}), VAMP2 {members.VAMP2.max():.1f} "
              f"({members.VAMP2.idxmax()}), share {class_share:.3f}; median share over its cluster types {members.vamp1_share.median():.3f}")
    print(f"  forebrain excitatory cluster types: median share {pair.loc[list(FOREBRAIN_EXCITATORY_CLUSTER_TYPES), 'vamp1_share'].median():.3f}; "
          f"cortical interneuron cluster types: median share {pair.loc[list(CORTICAL_INTERNEURON_CLUSTER_TYPES), 'vamp1_share'].median():.3f}")

    pooled_profile = ncpm_by_cluster_type.mean(axis=1)
    pooled_share = pooled_profile["VAMP1"] / (pooled_profile["VAMP1"] + pooled_profile["VAMP2"])
    below_pool = pair[pair.vamp1_share < pooled_share].index.tolist()
    print(f"\n4. pooled stand-in VAMP1 share {pooled_share:.3f}; {len(below_pool)} cluster types sit below it, where ambient RNA can only "
          f"have raised the share: {', '.join(below_pool)}")


if __name__ == "__main__":
    main()
