"""Build the mouse report sources beyond IMPC (decision 9.93): MGI-literature, MGI-screen and SFARI-mouse-models.

Reads the pinned MGI reports and MP ontology under data/raw/mgi, the pinned SFARI pages under data/raw/sfari (see
scripts/fetch_raw_sources.sh), HGNC for the one-to-one mouse-to-human map and the graph's gene nodes, and writes, for
each source, a report table of the evidence_reports schema plus its extra columns (evidence/mgi_mouse_phenotypes.py
EXTRA_COLUMNS, evidence/sfari_mouse_models.py EXTRA_COLUMNS) and a summary of what was read and what was not:

  <output-root>/mgi_literature<suffix>/mgi_literature_reports.parquet, ..._normal_genotypes.parquet, ..._summary.json
  <output-root>/mgi_screen<suffix>/mgi_screen_reports.parquet, ..._normal_genotypes.parquet, ..._summary.json
  <output-root>/sfari<suffix>/sfari_reports.parquet, sfari_summary.json

Each table joins training only through --soft-prior-reports, which is off by default, as IMPC's does.

Usage:
  PYTHONPATH=. python experiments/build_mouse_source_reports.py --graph-dir data/processed/graph_full --suffix _v5
  ... --count-no-abnormal-phenotype-as-absence    # read MGI's MP:0002169 as an absence of every read symptom
  ... --exclude-untyped-alleles                   # leave out alleles whose direction the source does not state
  ... --include-weak                              # also the weak proxies
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.evidence import mgi_mouse_phenotypes as mgi
from mechanistic_pathway_learning.evidence import sfari_mouse_models as sfari
from mechanistic_pathway_learning.evidence.clinical_trial_adverse_events import rows_to_dataframe
from mechanistic_pathway_learning.evidence.impc_knockout_phenotypes import VALIDITY_READ_BY_DEFAULT, VALIDITY_READ_WITH_WEAK, mouse_to_human_symbols, read_crosswalk

MGI_READ_DATE = "2026-10-24"


def report_table(rows: list[dict], extra_columns: tuple[str, ...]) -> pd.DataFrame:
    table = rows_to_dataframe(rows)
    for column in extra_columns:
        values = [row.get(column, "") for row in rows]
        if column.startswith("rubric_"):
            table[column] = pd.Series(values, dtype="float64") if rows else pd.Series(dtype="float64")
        elif column == "whole_genotype_normal":
            table[column] = pd.Series([bool(value) for value in values], dtype="bool") if rows else pd.Series(dtype="bool")
        else:
            table[column] = pd.Series([str(value) for value in values], dtype="object") if rows else pd.Series(dtype="object")
    return table


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mgi-dir", type=Path, default=Path("data/raw/mgi"))
    parser.add_argument("--sfari-dir", type=Path, default=Path("data/raw/sfari"))
    parser.add_argument("--hgnc", type=Path, default=Path("data/raw/hgnc/hgnc_complete_set.txt"))
    parser.add_argument("--graph-dir", type=Path, default=Path("data/processed/graph_full"))
    parser.add_argument("--crosswalk", type=Path, default=Path("configs/impc_symptom_crosswalk_fine.csv"), help="the MP crosswalk, IMPC's")
    parser.add_argument("--sfari-crosswalk", type=Path, default=sfari.DEFAULT_CROSSWALK_PATH)
    parser.add_argument("--sfari-allele-classes", type=Path, default=sfari.DEFAULT_ALLELE_CLASSES_PATH)
    parser.add_argument("--screen-loads", type=Path, default=mgi.DEFAULT_SCREEN_LOADS_PATH)
    parser.add_argument("--descendant-exclusions", type=Path, default=mgi.DEFAULT_DESCENDANT_EXCLUSIONS_PATH)
    parser.add_argument("--output-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--suffix", default="", help="appended to each output directory's name, as _v5 for the fine-level tables")
    parser.add_argument("--sources", nargs="*", default=["mgi-literature", "mgi-screen", "sfari"], choices=["mgi-literature", "mgi-screen", "sfari"])
    parser.add_argument("--include-weak", action="store_true")
    parser.add_argument("--count-no-abnormal-phenotype-as-absence", action="store_true")
    parser.add_argument("--exclude-untyped-alleles", action="store_true")
    arguments = parser.parse_args()

    validities = VALIDITY_READ_WITH_WEAK if arguments.include_weak else VALIDITY_READ_BY_DEFAULT
    nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet", columns=["node_id", "node_type", "gene_symbol"])
    genes = nodes[nodes.node_type == "gene"]
    node_of_symbol = {str(symbol): str(node_id) for node_id, symbol in zip(genes.node_id, genes.gene_symbol) if isinstance(symbol, str)}
    mouse_to_human = mouse_to_human_symbols(arguments.hgnc)
    settings = {"validities_read": list(validities), "count_no_abnormal_phenotype_as_absence": arguments.count_no_abnormal_phenotype_as_absence,
                "include_untyped_alleles": not arguments.exclude_untyped_alleles, "graph_dir": str(arguments.graph_dir)}

    mgi_sources = [source for source in arguments.sources if source.startswith("mgi")]
    if mgi_sources:
        crosswalk = read_crosswalk(arguments.crosswalk)
        names, children = mgi.read_mp_ontology(arguments.mgi_dir / "mp.obo")
        alleles = mgi.read_alleles(arguments.mgi_dir / "MGI_PhenotypicAllele.rpt")
        exclusions = mgi.read_descendant_exclusions(arguments.descendant_exclusions)
        loads = mgi.read_screen_loads(arguments.screen_loads)
        for source in mgi_sources:
            origin = source.split("-", 1)[1]
            rows, normal, counts = mgi.build_reports(mgi.read_genotype_annotations(arguments.mgi_dir / "MGI_PhenoGenoMP.rpt"), alleles, mouse_to_human, node_of_symbol,
                                                     crosswalk, children, exclusions, names, loads, origin, validities,
                                                     arguments.count_no_abnormal_phenotype_as_absence, not arguments.exclude_untyped_alleles,
                                                     release_label=f"reports read {MGI_READ_DATE}", release_date=MGI_READ_DATE)
            name = source.replace("-", "_")
            directory = arguments.output_root / f"{name}{arguments.suffix}"
            directory.mkdir(parents=True, exist_ok=True)
            report_table(rows, mgi.EXTRA_COLUMNS).to_parquet(directory / f"{name}_reports.parquet", index=False)
            pd.DataFrame(normal, columns=["perturbation_id", "mgi_genotype_id", "allelic_composition", "allele_direction", "pubmed_ids", "load"]).to_parquet(
                directory / f"{name}_normal_genotypes.parquet", index=False)
            (directory / f"{name}_summary.json").write_text(json.dumps({"source": mgi.LITERATURE_SOURCE if origin == "literature" else mgi.SCREEN_SOURCE,
                                                                        "settings": settings, "counts": counts}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            print(f"{source}: {counts.get('calls', 0)} calls, {counts.get('absences_from_no_abnormal_phenotype', 0)} absences, "
                  f"{counts.get('genotypes_with_no_abnormal_phenotype', 0)} genotypes with no abnormal phenotype; {directory}")

    if "sfari" in arguments.sources:
        manifest = sfari_manifest(arguments.sfari_dir)
        pages = {gene: (arguments.sfari_dir / entry["saved_as"]).read_text(encoding="utf-8", errors="replace") for gene, entry in manifest.items()}
        release = json.loads((arguments.sfari_dir / "manifest.json").read_text(encoding="utf-8")).get("releases_named_on_the_pages", [""]) if (arguments.sfari_dir / "manifest.json").is_file() else [""]
        rows, counts = sfari.build_reports(pages, set(mouse_to_human.values()), node_of_symbol, sfari.read_crosswalk(arguments.sfari_crosswalk),
                                           sfari.read_allele_classes(arguments.sfari_allele_classes), validities, not arguments.exclude_untyped_alleles,
                                           release_label=";".join(release))
        counts["pages"] = len(pages)
        directory = arguments.output_root / f"sfari{arguments.suffix}"
        directory.mkdir(parents=True, exist_ok=True)
        report_table(rows, sfari.EXTRA_COLUMNS).to_parquet(directory / "sfari_reports.parquet", index=False)
        (directory / "sfari_summary.json").write_text(json.dumps({"source": sfari.SOURCE_NAME, "release": release, "settings": settings, "counts": counts},
                                                                 indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"sfari: {counts.get('calls', 0)} calls, {counts.get('absences', 0)} absences from {len(pages)} pages; {directory}")
    return 0


def sfari_manifest(sfari_dir: Path) -> dict[str, dict]:
    """The pinned pages whose file is present with the SHA-256 the manifest states; a page that changed is refused."""
    import csv
    import hashlib

    pinned = {}
    with open(sfari_dir / "manifest.tsv", newline="", encoding="utf-8") as handle:
        for entry in csv.DictReader(handle, delimiter="\t"):
            if entry["read"] != "True":
                continue
            path = sfari_dir / entry["saved_as"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                raise SystemExit(f"{path}: its SHA-256 is not the one data/raw/sfari/manifest.tsv pins")
            pinned[entry["gene"]] = entry
    return pinned


if __name__ == "__main__":
    sys.exit(main())
