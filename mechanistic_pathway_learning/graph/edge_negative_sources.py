"""Read the five sources of decision 9.91 and write their per-edge columns (graph/edge_negative_evidence.py).

Each source is read when its files are present and recorded as absent, with the paths looked for, when they are not,
and writes no columns, so a table built without one cannot be read as "no observations". Every file read is recorded with its
SHA-256 in the summary.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.graph import chembl_activity_negatives as chembl
from mechanistic_pathway_learning.graph import go_not_annotations as go_not
from mechanistic_pathway_learning.graph import huri_tested_space as huri
from mechanistic_pathway_learning.graph import negatome_negatives as negatome
from mechanistic_pathway_learning.graph import perturbseq_responses as perturbseq
from mechanistic_pathway_learning.graph.edge_negative_evidence import SOURCES, summarise_negative_evidence


@dataclass
class NegativeEvidencePaths:
    hgnc: Path = Path("data/raw/hgnc/hgnc_complete_set.txt")
    negatome_directory: Path = negatome.DEFAULT_NEGATOME_DIRECTORY
    huri: Path = huri.DEFAULT_HURI
    space_iii_genes: Path | None = None
    pseudobulk: Path = perturbseq.DEFAULT_PSEUDOBULK
    chembl_activities: Path = chembl.DEFAULT_ACTIVITIES
    chembl_target_mapping: Path = chembl.DEFAULT_TARGET_MAPPING
    chembl_chebi_mapping: Path = chembl.DEFAULT_CHEBI_MAPPING
    chembl_pubchem_mapping: Path = chembl.DEFAULT_PUBCHEM_MAPPING
    human_gem_metabolites: Path = chembl.DEFAULT_METABOLITES
    go_gaf: Path = go_not.DEFAULT_GAF
    go_obo: Path = go_not.DEFAULT_OBO
    go_rules: Path = go_not.DEFAULT_RULES
    human_gem_sbml: Path = go_not.DEFAULT_SBML
    sources: tuple[str, ...] = field(default_factory=lambda: SOURCES)


def file_record(path: Path) -> dict:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return {"path": str(path), "bytes": Path(path).stat().st_size, "sha256": digest.hexdigest()}


def assemble_negative_evidence(evidence: pd.DataFrame, edges: pd.DataFrame, nodes: pd.DataFrame, paths: NegativeEvidencePaths | None = None) -> tuple[pd.DataFrame, dict]:
    """The columns of every source for the rows of the edge evidence table (which carries source_id, target_id,
    relation_type, family and, where built, resources and pubmed_ids), and a summary: per source its inputs or why it
    is absent, and the counts by family and relation. An absent source writes no columns, so the trainer refuses it
    rather than reading a source it never saw as one that observed nothing."""
    paths = paths or NegativeEvidencePaths()
    frames, summary = [], {"sources": {}}
    hgnc_ready = Path(paths.hgnc).is_file()
    symbol_of_accession = negatome.accession_symbols(paths.hgnc) if hgnc_ready else {}
    for source in paths.sources:
        record: dict = {}
        columns = None
        if source == "negatome":
            files = sorted(Path(paths.negatome_directory).glob("*.txt")) if Path(paths.negatome_directory).is_dir() else []
            if files and hgnc_ready:
                columns = negatome.negatome_edge_columns(evidence, negatome.read_negatome(paths.negatome_directory), symbol_of_accession)
                record["inputs"] = [file_record(path) for path in files]
            else:
                record["absent"] = f"no Negatome pair files in {paths.negatome_directory}" if not files else f"no HGNC table at {paths.hgnc}"
        elif source == "huri":
            if Path(paths.huri).is_file() and hgnc_ready:
                symbol_of_ensembl = huri.symbol_of_ensembl_gene(paths.hgnc)
                huri_pairs, mapping = huri.symbol_pairs(huri.read_ensembl_pairs(paths.huri), symbol_of_ensembl)
                space = set(Path(paths.space_iii_genes).read_text(encoding="utf-8").split()) if paths.space_iii_genes else None
                tested = huri.tested_genes(huri_pairs, space)
                columns = huri.huri_edge_columns(evidence, huri_pairs, tested)
                record.update({"inputs": [file_record(paths.huri)] + ([file_record(paths.space_iii_genes)] if paths.space_iii_genes else []),
                               "pairs": mapping, "tested_genes": len(tested),
                               "tested_space": "Space III gene list" if space else "the genes with at least one HuRI interaction, a subset of Space III",
                               "status": columns["huri_status"].value_counts().to_dict()})
            else:
                record["absent"] = f"no HuRI table at {paths.huri}" if not Path(paths.huri).is_file() else f"no HGNC table at {paths.hgnc}"
        elif source == "perturbseq":
            if Path(paths.pseudobulk).is_file():
                sign = edges["sign"].to_numpy(dtype=float) if "sign" in edges.columns else np.ones(len(evidence))
                columns = perturbseq.perturbseq_edge_columns(evidence, sign, perturbseq.read_pseudobulk(paths.pseudobulk))
                record.update({"inputs": [file_record(paths.pseudobulk)], "cell_line": perturbseq.CELL_LINE,
                               "status": columns.loc[columns["perturbseq_status"] != "not_regulation", "perturbseq_status"].value_counts().to_dict()})
            else:
                record["absent"] = f"no pseudo-bulk table at {paths.pseudobulk}"
        elif source == "chembl":
            needed = [paths.chembl_activities, paths.chembl_target_mapping, paths.chembl_chebi_mapping]
            if all(Path(path).is_file() for path in needed) and hgnc_ready:
                accessions_of_symbol: dict[str, set[str]] = {}
                for accession, symbol in symbol_of_accession.items():
                    accessions_of_symbol.setdefault(symbol, set()).add(accession)
                metabolites = pd.read_csv(paths.human_gem_metabolites, sep="\t", usecols=["metsNoComp", "metChEBIID"]) if Path(paths.human_gem_metabolites).is_file() else None
                compounds = chembl.compound_ids_of_nodes(nodes, chembl.chebi_of_base(metabolites), chembl.read_chebi_mapping(paths.chembl_chebi_mapping),
                                                         chembl.read_pubchem_mapping(paths.chembl_pubchem_mapping))
                targets = chembl.target_ids_of_nodes(nodes, chembl.read_target_mapping(paths.chembl_target_mapping), accessions_of_symbol)
                activities = chembl.normalised_activities(pd.read_parquet(paths.chembl_activities))
                columns = chembl.chembl_edge_columns(evidence, compounds, targets, activities)
                asked = chembl.candidate_pairs(evidence, compounds, targets)
                record.update({"inputs": [file_record(path) for path in needed if Path(path).is_file()]
                               + ([file_record(paths.chembl_pubchem_mapping)] if Path(paths.chembl_pubchem_mapping).is_file() else []),
                               "compound_nodes_mapped": len(compounds), "protein_nodes_mapped": len(targets),
                               "compound_target_pairs_on_edges": int(sum(map(len, asked.values()))), "activity_records": int(len(activities)),
                               "records_by_call": pd.Series([chembl.classify_activity(row) for row in activities.to_dict("records")]).value_counts().to_dict()
                               if len(activities) else {}})
            else:
                record["absent"] = "missing: " + ", ".join(str(path) for path in needed if not Path(path).is_file()) if not all(Path(path).is_file() for path in needed) \
                    else f"no HGNC table at {paths.hgnc}"
        elif source == "go_not":
            needed = [paths.go_gaf, paths.go_obo, paths.go_rules]
            if all(Path(path).is_file() for path in needed):
                parents, ec_of_term = go_not.read_is_a_and_ec(paths.go_obo)
                negatives, positive_terms, positive_partners = go_not.read_gaf_molecular_functions(paths.go_gaf)
                ec_of_reaction = go_not.reaction_ec_numbers(paths.human_gem_sbml) if Path(paths.human_gem_sbml).is_file() else {}
                columns, go_summary = go_not.go_not_edge_columns(evidence, nodes, go_not.read_rules(paths.go_rules), negatives, positive_terms, positive_partners,
                                                                 parents, ec_of_term, ec_of_reaction, symbol_of_accession)
                record.update({"inputs": [file_record(path) for path in needed] + ([file_record(paths.human_gem_sbml)] if Path(paths.human_gem_sbml).is_file() else []),
                               **go_summary, "reactions_with_ec_numbers": len(ec_of_reaction)})
            else:
                record["absent"] = "missing: " + ", ".join(str(path) for path in needed if not Path(path).is_file())
        else:
            raise ValueError(f"unknown source {source!r}")
        if columns is not None:
            frames.append(columns)
        summary["sources"][source] = record
    table = pd.concat(frames, axis=1) if frames else pd.DataFrame(index=evidence.index)
    summary["counts"] = summarise_negative_evidence(pd.concat([evidence[["family", "relation_type"]], table], axis=1))
    return table, summary
