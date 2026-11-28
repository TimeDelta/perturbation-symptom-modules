"""Draw the sourcing sample of amendment item 38 (g) from the training portion, after the held-out split is fixed
(decision 9.134; built 28 November 2026, not run).

**Status: an unreviewed draft** (written 28 November 2026, not yet reviewed by the owner). It runs
mechanistic_pathway_learning/evaluation/sourcing_sample.py on files, and that module's docstring holds what is ruled,
what follows from (g), and the open definitions. Nothing here has been run on real data, no real held-out set
has been read with it and no sample has been drawn.

It is run once the held-out set of decision 1.1 is drawn, and not before: it refuses a held-out set that does not
record the evidence table and label selection it was drawn on, or records others than the --evidence-dir and
--label-selection given here, and refuses strata (experiments/write_research_strata_and_eras.py's record and cells
file, written before the draw) made on others, or whose cells file is not the one the record names.

What it leaves to the caller, because neither (g) nor 9.134 settles it, each a required argument with no default:
--seed, --quota-unit (sourcing_sample.QUOTA_UNITS), --stratum-reading (STRATUM_READINGS), --era-reading
(ERA_READINGS) and --draw-order (DRAW_ORDERS).

Writes two files and prints their SHA-256, refusing to overwrite either, since a sample drawn is not redrawn:
- --output-cells, a CSV with one row per cell drawn into a quota cell (research_strata_and_eras.write_cells);
- --output-record, the JSON record of the rule, every quota cell with its labelled development cells, those without
  a counted record, its candidates and how many were drawn, and the SHA-256 of every file read, with a
  sha256sum-format sidecar <record>.sha256 (research_strata_and_eras.write_record).

Usage, from the repository root (only once the held-out set is drawn):
  PYTHONPATH=. python experiments/draw_sourcing_sample.py --held-out <held-out set.json> \\
      --strata-record <record.json> --strata-cells <cells.csv> --evidence-dir <evidence> \\
      --label-selection <selection.parquet> --seed <n> --quota-unit <crossed|apart> \\
      --stratum-reading <research_stratum|none_against_any> --era-reading <first_record_era_thirds|first_record_era_two_way> \\
      --draw-order <one_generator_in_quota_order|one_generator_per_quota_cell> \\
      --output-cells <sample.csv> --output-record <sample.json>
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from mechanistic_pathway_learning.evaluation.research_strata_and_eras import file_sha256, write_cells, write_record
from mechanistic_pathway_learning.evaluation.sourcing_sample import (
    DRAW_ORDERS, ERA_READINGS, QUOTA_UNITS, STRATUM_READINGS, draw_sourcing_sample_from_files)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--held-out", type=Path, required=True, help="the held-out set, in experiments/draw_lockbox.py's format")
    parser.add_argument("--strata-record", type=Path, required=True, help="the record experiments/write_research_strata_and_eras.py wrote")
    parser.add_argument("--strata-cells", type=Path, required=True, help="the cells file that record names")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--label-selection", required=True, help="the label selection parquet, or none")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--quota-unit", choices=QUOTA_UNITS, required=True)
    parser.add_argument("--stratum-reading", choices=STRATUM_READINGS, required=True)
    parser.add_argument("--era-reading", choices=ERA_READINGS, required=True)
    parser.add_argument("--draw-order", choices=DRAW_ORDERS, required=True)
    parser.add_argument("--output-cells", type=Path, required=True)
    parser.add_argument("--output-record", type=Path, required=True)
    arguments = parser.parse_args(argv)

    for path in (arguments.output_cells, arguments.output_record, Path(f"{arguments.output_record}.sha256")):
        if path.exists():
            raise SystemExit(f"{path} exists; a sourcing sample is drawn once and is not overwritten")
    label_selection = None if arguments.label_selection in ("", "none") else Path(arguments.label_selection)
    evidence_records_sha256 = file_sha256(arguments.evidence_dir / "evidence_records.parquet")
    label_selection_sha256 = file_sha256(label_selection) if label_selection else None
    sample, record = draw_sourcing_sample_from_files(
        arguments.held_out, arguments.strata_record, arguments.strata_cells, evidence_records_sha256=evidence_records_sha256,
        label_selection_sha256=label_selection_sha256, seed=arguments.seed, quota_unit=arguments.quota_unit,
        stratum_reading=arguments.stratum_reading, era_reading=arguments.era_reading, draw_order=arguments.draw_order)
    cells_sha256 = write_cells(sample, arguments.output_cells)
    record = {"drawn_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **record,
              "evidence_dir": str(arguments.evidence_dir), "label_selection": str(label_selection) if label_selection else None,
              "sample_file": str(arguments.output_cells), "sample_sha256": cells_sha256}
    record_sha256 = write_record(record, arguments.output_record)
    print(json.dumps({key: record[key] for key in ("rule", "num_rows_drawn", "num_distinct_cells_to_read")}, indent=1))
    print(f"{arguments.output_cells} SHA-256 {cells_sha256}")
    print(f"{arguments.output_record} SHA-256 {record_sha256}")


if __name__ == "__main__":
    main()
