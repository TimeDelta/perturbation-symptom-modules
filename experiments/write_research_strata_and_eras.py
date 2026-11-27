"""Write the eras and research strata of amendment item 38 (d) and (g), with the boundaries each type took, before the
held-out set of decision 1.1 is drawn (docs/preregistration.md, item 38: the boundary years "are written with the
hashed dates before the draw and no outcome enters them"; the strata's form and boundaries "are written with the
hashed counts before the draw").

Reads the per-cell search table of (g), in the schema mechanistic_pathway_learning/evaluation/research_strata_and_eras.py
states (an assumption the (g) pass may revise), and the evidence table and label selection the draw will be made on,
through load_experiment_data as experiments/score_confirmatory.py reads them. The scored table is every perturbation
of the data against every symptom with at least MINIMUM_POSITIVES_TO_SCORE kept positives in the whole data, the
registered micro set. It refuses, writing nothing, while any cell of that table has no row in the search table or is
marked not searched with no reason (item 38 (g): "the reading is not run while any remain unexplained").

Writes two files and prints their SHA-256:
- --output-cells, a CSV with one row per cell of the scored table: its type, whether it is a kept positive, whether a
  label selection set it aside, its registered gene date (proleptic Gregorian ordinal, 0 when undated), its count and
  earliest year, the reason it was left out if it was not searched, and its stratum under each reading;
- --output-record, the JSON record of what each type took (the form of its strata and their boundaries, its era
  boundary years, the cells and kept positives per stratum, the cells left out by reason), with the SHA-256 of the
  search table, of the evidence and graph files, of the label selection and of the cells file, and a sha256sum-format
  sidecar <record>.sha256.
Both are to be committed before the draw. It refuses to overwrite either, since "The cuts are not moved after the
draw"; a recomputation before the draw deletes them first, and git keeps what they held.

Usage, from the repository root:
  PYTHONPATH=. python experiments/write_research_strata_and_eras.py --search-table <search output> \\
      --output-record <record.json> --output-cells <cells.csv>
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_confirmatory import MINIMUM_POSITIVES_TO_SCORE  # noqa: E402

from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data  # noqa: E402
from mechanistic_pathway_learning.evaluation.research_strata_and_eras import (  # noqa: E402
    assign_strata_and_eras, file_sha256, read_cell_search_table, scored_cells_from_experiment_data, write_cells, write_record)


def input_hashes(graph_directory: Path, evidence_directory: Path, label_selection: Path | None, search_table: Path) -> dict:
    """The SHA-256 of every file the assignment rests on, which the scorer checks again before it reads a stratum."""
    return {"search_table_sha256": file_sha256(search_table),
            "graph_files_sha256": {name: file_sha256(graph_directory / f"{name}.parquet") for name in ("nodes", "edges")},
            "evidence_records_sha256": file_sha256(evidence_directory / "evidence_records.parquet"),
            "label_selection_sha256": file_sha256(label_selection) if label_selection else None}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, default=Path("data/processed/graph_full_neuronal"))
    parser.add_argument("--evidence-dir", type=Path, default=Path("data/processed/evidence_full_v2"))
    parser.add_argument("--label-selection", type=Path, default=Path("data/processed/label_selection/better_v2_full_v2.parquet"))
    parser.add_argument("--group-by", default="disease_cluster_and_targets", help="passed to load_experiment_data; the labels do not depend on it")
    parser.add_argument("--search-table", type=Path, required=True, help="the per-cell search table of item 38 (g), parquet or CSV")
    parser.add_argument("--output-record", type=Path, required=True)
    parser.add_argument("--output-cells", type=Path, required=True)
    arguments = parser.parse_args()

    for path in (arguments.output_record, arguments.output_cells, Path(f"{arguments.output_record}.sha256")):
        if path.exists():
            raise SystemExit(f"{path} exists: the cuts are not moved once written (item 38 (d)); delete it first to recompute before the draw")
    label_selection = None if str(arguments.label_selection) in ("", "none") else arguments.label_selection
    search_table = read_cell_search_table(arguments.search_table)
    data = load_experiment_data(arguments.graph_dir, arguments.evidence_dir, group_by=arguments.group_by, label_selection=label_selection)
    cells, record = assign_strata_and_eras(search_table, scored_cells_from_experiment_data(data, MINIMUM_POSITIVES_TO_SCORE))
    cells_sha256 = write_cells(cells, arguments.output_cells)
    record = {
        "what": "item 38 (d) and (g) of docs/preregistration.md: the eras and research strata of every cell, written before the draw of decision 1.1",
        "written_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "tracked_changes": subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True).stdout.splitlines(),
        "graph_dir": str(arguments.graph_dir), "evidence_dir": str(arguments.evidence_dir),
        "label_selection": str(label_selection) if label_selection else None, "search_table": str(arguments.search_table),
        **input_hashes(arguments.graph_dir, arguments.evidence_dir, label_selection, arguments.search_table),
        "minimum_positives_to_score": MINIMUM_POSITIVES_TO_SCORE,
        "cells_file": str(arguments.output_cells), "cells_sha256": cells_sha256,
        **record,
    }
    record_sha256 = write_record(record, arguments.output_record)
    for name, entry in record["types"].items():
        strata, eras = entry["research_strata"], entry["first_record_eras"]
        print(f"{name}: strata {strata['form']} {strata['boundaries']} cells {strata['cells']}; eras {eras['boundary_years']} "
              f"over {eras['num_dated_kept_positives']} dated kept positives; left out {entry['left_out_not_searched']['cells']} cells")
    print(f"{arguments.output_cells} SHA-256 {cells_sha256}")
    print(f"{arguments.output_record} SHA-256 {record_sha256}")


if __name__ == "__main__":
    main()
