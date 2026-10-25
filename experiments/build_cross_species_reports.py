"""Build the report sources of species other than mouse and human (decision 9.94; evidence/cross_species_reports.py).

Reads the pinned files under data/raw (scripts/fetch_raw_sources.sh): alliance/ORTHOLOGY-ALLIANCE_COMBINED.tsv.gz,
rgd/rattus_genes_mp, chembl_rat_behaviour/{assays,activities}.json, flybase/genotype_phenotype_data_fb_2026_03.tsv.gz,
zfin/phenotype_fish.txt and fish_components_fish.txt, wormbase/phenotype_association.WS298.wb and
fenckova_2019/mmc2.xlsx (supplied by the owner, so not fetched), with the MP ontology of data/raw/mgi, the graph's gene
nodes and the ChEMBL identifiers of the drug tables. Writes one directory per source under --output-root, each with
<source>_reports.parquet (the evidence_reports schema plus EXTRA_COLUMNS) and <source>_summary.json. A source whose
input file is missing is skipped and named. Each table joins training only through --soft-prior-reports (and so under
--label-likelihood weighted, since the positive-unlabelled likelihood of 9.90 takes no soft prior).

Usage:
  PYTHONPATH=. python experiments/build_cross_species_reports.py --graph-dir data/processed/graph_full --suffix _v5
  ... --include-weak --include-validity weak_intellectual_disability weak_worm   # the classes off by default
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.evidence import cross_species_reports as species
from mechanistic_pathway_learning.evidence import mgi_mouse_phenotypes as mgi
from mechanistic_pathway_learning.evidence.clinical_trial_adverse_events import rows_to_dataframe
from mechanistic_pathway_learning.evidence.impc_knockout_phenotypes import VALIDITY_READ_BY_DEFAULT, VALIDITY_READ_WITH_WEAK, read_crosswalk

DIRECTORY_OF_SOURCE = {"RGD-rat": "rgd_rat", "ChEMBL-rat-in-vivo": "chembl_rat_in_vivo", "FlyBase-classical": "flybase_classical", "FlyBase-RNAi": "flybase_rnai",
                       "Fenckova-2019-RNAi": "fenckova_2019", "ZFIN-mutant": "zfin_mutant", "ZFIN-morpholino": "zfin_morpholino",
                       "WormBase-variation": "wormbase_variation", "WormBase-RNAi": "wormbase_rnai"}


def report_table(rows: list[dict]) -> pd.DataFrame:
    table = rows_to_dataframe(rows)
    for column in species.EXTRA_COLUMNS:
        values = [row.get(column, "") for row in rows]
        table[column] = pd.Series(values, dtype="float64" if column.startswith("rubric_") else "object") if rows else pd.Series(dtype="float64" if column.startswith("rubric_") else "object")
    return table


def chembl_perturbations(raw: Path, drug_ids: set[str]) -> dict[str, list[str]]:
    """ChEMBL id -> the drug perturbations of the tables it names: through UniChem's PubChem map (a STITCH flat id is
    CID1 and the eight-digit CID), ChEMBL's parents, and the OnSIDES bridge for the RxNorm-keyed drugs."""
    mapping: dict[str, set[str]] = {}
    unichem = json.loads((raw / "chembl/unichem_pubchem_to_chembl.json").read_text(encoding="utf-8"))
    parents = json.loads((raw / "chembl/molecule_parents.json").read_text(encoding="utf-8"))
    for drug in drug_ids:
        if drug.startswith("CID1"):
            for chembl_id in unichem.get(str(int(drug[4:])), []):
                mapping.setdefault(chembl_id, set()).add(drug)
                parent = parents.get(chembl_id, {}).get("parent")
                if parent:
                    mapping.setdefault(parent, set()).add(drug)
    bridge_path = raw / "onsides/v3.1.1/ingredient_identifier_bridge.json"
    if bridge_path.is_file():
        ingredients = json.loads(bridge_path.read_text(encoding="utf-8")).get("ingredients", [])
        for ingredient in (ingredients.values() if isinstance(ingredients, dict) else ingredients):
            if ingredient.get("perturbation_id") in drug_ids and ingredient.get("chembl_parent"):
                mapping.setdefault(ingredient["chembl_parent"], set()).add(ingredient["perturbation_id"])
    return {chembl_id: sorted(drugs) for chembl_id, drugs in mapping.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--hgnc", type=Path, default=None, help="HGNC's complete set, for the current symbols of the Fenckova table (default data/raw/hgnc)")
    parser.add_argument("--graph-dir", type=Path, default=Path("data/processed/graph_full"))
    parser.add_argument("--drug-tables", type=Path, nargs="*", default=[Path("data/processed/evidence_full_v5/evidence_reports.parquet")],
                        help="report tables whose drug perturbations the rat drug source keys to")
    parser.add_argument("--crosswalk", type=Path, default=Path("configs/impc_symptom_crosswalk_fine.csv"))
    parser.add_argument("--species-crosswalk", type=Path, default=species.DEFAULT_CROSSWALK_PATH)
    parser.add_argument("--output-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--suffix", default="")
    parser.add_argument("--include-weak", action="store_true")
    parser.add_argument("--include-validity", nargs="*", default=[], choices=list(species.SEPARATE_VALIDITY_CLASSES))
    arguments = parser.parse_args()

    raw = arguments.raw_dir
    validities = tuple([*(VALIDITY_READ_WITH_WEAK if arguments.include_weak else VALIDITY_READ_BY_DEFAULT), *arguments.include_validity])
    nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet", columns=["node_id", "node_type", "gene_symbol"])
    genes = nodes[nodes.node_type == "gene"]
    node_of_symbol = {str(symbol): str(node_id) for node_id, symbol in zip(genes.node_id, genes.gene_symbol) if isinstance(symbol, str)}
    orthology = raw / "alliance/ORTHOLOGY-ALLIANCE_COMBINED.tsv.gz"
    crosswalk = species.read_species_crosswalk(arguments.species_crosswalk)
    built: dict[str, tuple[list[dict], dict]] = {}
    skipped = []

    if (raw / "rgd/rattus_genes_mp").is_file():
        names, children = mgi.read_mp_ontology(raw / "mgi/mp.obo")
        built["RGD-rat"] = species.build_rgd_rat(raw / "rgd/rattus_genes_mp", species.read_one_to_one_orthologs(orthology, "rat"), node_of_symbol,
                                                 read_crosswalk(arguments.crosswalk), children, mgi.read_descendant_exclusions(), names, validities)
    else:
        skipped.append("RGD-rat")
    if (raw / "chembl_rat_behaviour/activities.json").is_file():
        drug_ids = set()
        for path in arguments.drug_tables:
            table = pd.read_parquet(path, columns=["perturbation_id", "perturbation_type"])
            drug_ids |= set(table[table.perturbation_type == "drug"].perturbation_id.astype(str))
        validity = "moderate" if "moderate" in validities else None
        if validity:
            built["ChEMBL-rat-in-vivo"] = species.build_chembl_rat(json.loads((raw / "chembl_rat_behaviour/assays.json").read_text(encoding="utf-8")),
                                                                   json.loads((raw / "chembl_rat_behaviour/activities.json").read_text(encoding="utf-8")),
                                                                   chembl_perturbations(raw, drug_ids), validity)
    else:
        skipped.append("ChEMBL-rat-in-vivo")
    fly = species.read_one_to_one_orthologs(orthology, "fly")
    if (raw / "flybase/genotype_phenotype_data_fb_2026_03.tsv.gz").is_file():
        rows, counts = species.build_flybase(raw / "flybase/genotype_phenotype_data_fb_2026_03.tsv.gz", fly, node_of_symbol, crosswalk, species.read_drivers(), validities)
        for source in ("FlyBase-classical", "FlyBase-RNAi"):
            built[source] = ([row for row in rows if row["source"] == source], counts)
    else:
        skipped += ["FlyBase-classical", "FlyBase-RNAi"]
    if (raw / "fenckova_2019/mmc2.xlsx").is_file():
        lines, category_of = species.read_fenckova_workbook(raw / "fenckova_2019/mmc2.xlsx")
        built["Fenckova-2019-RNAi"] = species.build_fenckova(lines, category_of, fly, node_of_symbol, crosswalk, validities,
                                                             species.current_hgnc_symbols(arguments.hgnc or raw / "hgnc/hgnc_complete_set.txt"))
    else:
        skipped.append("Fenckova-2019-RNAi")
    if (raw / "zfin/phenotype_fish.txt").is_file():
        rows, counts = species.build_zfin(raw / "zfin/phenotype_fish.txt", species.read_fish_components(raw / "zfin/fish_components_fish.txt"),
                                          species.read_one_to_one_orthologs(orthology, "zebrafish"), node_of_symbol, crosswalk, validities)
        for source in ("ZFIN-mutant", "ZFIN-morpholino"):
            built[source] = ([row for row in rows if row["source"] == source], counts)
    else:
        skipped += ["ZFIN-mutant", "ZFIN-morpholino"]
    if (raw / "wormbase/phenotype_association.WS298.wb").is_file():
        rows, counts = species.build_wormbase(raw / "wormbase/phenotype_association.WS298.wb", species.read_one_to_one_orthologs(orthology, "worm"), node_of_symbol,
                                              crosswalk, validities)
        for source in ("WormBase-variation", "WormBase-RNAi"):
            built[source] = ([row for row in rows if row["source"] == source], counts)
    else:
        skipped += ["WormBase-variation", "WormBase-RNAi"]

    for source, (rows, counts) in built.items():
        name = DIRECTORY_OF_SOURCE[source]
        directory = arguments.output_root / f"{name}{arguments.suffix}"
        directory.mkdir(parents=True, exist_ok=True)
        report_table(rows).to_parquet(directory / f"{name}_reports.parquet", index=False)
        summary = {"source": source, "species": species.SOURCE_SPECIES[source], "validities_read": list(validities), "graph_dir": str(arguments.graph_dir),
                   "rows": len(rows), "calls": sum(row["report_value"] == 1 for row in rows), "absences": sum(row["report_value"] == 0 for row in rows), "counts": counts}
        (directory / f"{name}_summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
        print(f"{source}: {summary['calls']} calls, {summary['absences']} absences; {directory}")
    if skipped:
        print(f"skipped, input missing: {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
