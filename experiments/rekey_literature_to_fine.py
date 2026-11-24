"""Re-key a literature report table from the coarse constructs to the fine constructs (decision 9.58).

The literature sources (PubTator3, CTD) are mapped through MeSH descriptors. The fine crosswalk keeps a descriptor with
its coarse construct's namesake unless configs/fine_construct_term_overrides.csv names its D-number (since 24 November
2026: Aggression D000374 goes to aggressive_behavior, not to irritability). So the fine-level literature table is the
coarse one with its symptom column renamed by each row's descriptor: no row is added or dropped. A table without a
mesh_descriptor column is renamed to the namesakes, as every table was before that date. Used where the raw literature
cache is not on disk and the release table is.

Usage:
  python experiments/rekey_literature_to_fine.py --input data/releases/v0.4/literature/literature_reports.parquet \\
      --output data/processed/literature_v5/literature_reports.parquet
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.evidence.symptom_constructs import (
    COARSE_CROSSWALK_PATH,
    TERM_OVERRIDES_PATH,
    fine_construct_of_descriptor,
    namesake_of_coarse,
    read_rows,
    read_term_overrides,
)


def rekey(reports: pd.DataFrame, namesake: dict[str, str], by_descriptor: dict[str, str] | None = None) -> pd.DataFrame:
    """The reports with symptom renamed to the fine construct and the coarse name kept in coarse_symptom. A row whose
    mesh_descriptor is in by_descriptor (descriptor -> fine construct) takes that construct; any other row takes its
    coarse construct's namesake."""
    unknown = sorted(set(reports.symptom) - set(namesake))
    if unknown:
        raise ValueError(f"symptoms with no coarse construct: {unknown}")
    renamed = reports.copy()
    renamed["coarse_symptom"] = renamed.symptom
    renamed["symptom"] = renamed.symptom.map(namesake)
    if by_descriptor and "mesh_descriptor" in renamed.columns:
        carried = renamed.mesh_descriptor.map(by_descriptor)
        renamed["symptom"] = carried.where(carried.notna(), renamed.symptom)
    if "report_id" in renamed.columns:
        renamed["report_id"] = [report_id.replace(f"|{coarse}|", f"|{fine}|") if coarse != fine else report_id
                                for report_id, coarse, fine in zip(renamed.report_id, renamed.coarse_symptom, renamed.symptom)]
    return renamed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--crosswalk", type=Path, default=COARSE_CROSSWALK_PATH)
    parser.add_argument("--term-overrides", type=Path, default=TERM_OVERRIDES_PATH)
    arguments = parser.parse_args()
    coarse_rows = read_rows(arguments.crosswalk)
    namesake = namesake_of_coarse(coarse_rows)
    by_descriptor = fine_construct_of_descriptor(coarse_rows, read_term_overrides(arguments.term_overrides))
    reports = pd.read_parquet(arguments.input)
    renamed = rekey(reports, namesake, by_descriptor)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    renamed.to_parquet(arguments.output, index=False)
    renamed_count = int((renamed.symptom != renamed.coarse_symptom).sum())
    moved = {descriptor: fine for descriptor, fine in by_descriptor.items() if fine not in namesake.values()}
    summary = {"input": str(arguments.input), "rows": int(len(renamed)), "rows_renamed": renamed_count, "namesake_of_coarse": namesake,
               "descriptors_moved_from_the_namesake": moved}
    (arguments.output.parent / "rekey_summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {arguments.output}: {len(renamed)} rows, {renamed_count} renamed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
