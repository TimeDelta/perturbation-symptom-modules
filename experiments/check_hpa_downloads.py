"""Check that the two Human Protein Atlas downloads can be read the way the graph build reads them, right after
scripts/fetch_raw_sources.sh fetches them (27 November 2026).

Written after the raw fetch of 23 November 2026 brought a new HPA release whose single-nucleus file names 48 cluster
types, none of them a key of CELL_CLASS_OF_CLUSTER_TYPE, so hpa_cell_class_table raised and the rebuild would have
stopped at its base graph, which every stage runs first (docs/data_layer_rebuild.md, addition of 27 November 2026).
A hash pin cannot catch this by itself, because proteinatlas.org serves the current release at an unversioned
address. This check runs the build's own readers, so it fails exactly when the build would, and it fails at fetch time
instead of partway into a rebuild.

It reads, and changes nothing. It exits 1 and names the problem when the region file has no brain region or the
cluster-type file has a cluster type with no cell class; scripts/fetch_raw_sources.sh then writes an UNREADABLE row
to its report and exits 1 at the end.

Usage:
  PYTHONPATH=. python experiments/check_hpa_downloads.py \
    --region-table data/raw/hpa/rna_brain_region_hpa/rna_brain_region_hpa.tsv.zip \
    --cluster-type-table data/raw/hpa/rna_single_nuclei_cluster_type/rna_single_nuclei_cluster_type.tsv.zip
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mechanistic_pathway_learning.graph.brain_expression_descriptors import (
    hpa_cell_class_table, hpa_region_table, read_zipped_table)


def problems_reading_hpa_downloads(region_table_path: Path, cluster_type_table_path: Path) -> list[str]:
    """What stops the build's HPA readers on these two files, one message per problem; empty when both read."""
    problems = []
    try:
        region_columns = hpa_region_table(read_zipped_table(region_table_path)).columns
        if len(region_columns) == 0:
            problems.append(f"{region_table_path}: no brain region")
    except Exception as error:  # the build's own reader failed: report its message as it is
        problems.append(f"{region_table_path}: {type(error).__name__}: {error}")
    try:
        hpa_cell_class_table(read_zipped_table(cluster_type_table_path))
    except Exception as error:
        problems.append(f"{cluster_type_table_path}: {type(error).__name__}: {error}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--region-table", type=Path, required=True, help="rna_brain_region_hpa.tsv.zip")
    parser.add_argument("--cluster-type-table", type=Path, required=True, help="rna_single_nuclei_cluster_type.tsv.zip")
    arguments = parser.parse_args()
    problems = problems_reading_hpa_downloads(arguments.region_table, arguments.cluster_type_table)
    for problem in problems:
        print(f"UNREADABLE {problem}", file=sys.stderr)
    if not problems:
        print("the build's readers read both Human Protein Atlas downloads")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
