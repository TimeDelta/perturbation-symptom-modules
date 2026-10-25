"""Build the per-edge evidence table of a graph for the edge priors (decision 9.57).

Reads the raw OmniPath and CollecTRI tables (their references and sources, which the graph build fetches and drops),
IntAct's curated non-interacting pairs (classed against UniProt's reviewed human proteome, so that only a record between
two whole proteins contests an edge: decision 9.88) and the graph's edges; writes <graph-dir>/edge_evidence.parquet aligned to
edges.parquet row for row (family, kind, records, contested, the PubMed ids the record count counts and the resources
that state the edge, the edge's own source_id, target_id and relation_type, which the trainer checks against the graph
before it reads a row, factor_below_detection for a transcription edge whose factor's gene node carries
expression_below_detection in nodes.parquet (decision 9.76: such an edge takes the lowered tier and is never a label),
and, with the species cache of experiments/fetch_icite_species.py, how many of its records iCite
scored, how many are human evidence and how many record animals and no human, and, with the OmniPath evidences
downloads, the PubMed ids behind each signed edge's sign, how CollecTRI decided a regulation's sign and whether its
two CollecTRI releases dispute it: graph/sign_evidence.py, decisions 9.70 and 9.72, and, for every source of decision 9.91
whose files are present, its negative and positive edge observations: graph/edge_negative_sources.py) and
edge_evidence_summary.json, which
records the SHA-256 of the edges.parquet it was built from and how many curated edges the label rule of decision 9.63
(b) takes as known. The graph files themselves are not touched, so no graph hash moves. The priors are computed from
this table by experiments/run_main_model.py under --edge-prior-strength.

Usage:
  python experiments/build_edge_evidence.py --graph-dir data/processed/graph_full_neuronal_split_binders_drugs_v4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.edge_evidence import (
    DEFAULT_TIERS_PATH,
    DEFAULT_CURATED_EDGE_SPECIES_PATH,
    FACTOR_BELOW_DETECTION_COLUMN,
    NONHUMAN_ONLY_EVIDENCE_COLUMN,
    curated_edge_labels,
    edge_evidence_table,
    edge_priors,
    factor_below_detection_flags,
    nonhuman_only_evidence_flags,
    read_curated_edge_species,
    read_edge_tiers,
    read_species,
    signalling_references,
    species_of_records,
    split_pubmed_ids,
    summarise,
    transcription_references,
)
from mechanistic_pathway_learning.graph.edge_negative_sources import NegativeEvidencePaths, assemble_negative_evidence
from mechanistic_pathway_learning.graph.edge_negatives import (
    DEFAULT_REVIEWED_PROTEOME,
    gene_pairs_between_whole_proteins,
    read_human_negative_pairs,
    read_reviewed_proteome,
)
from mechanistic_pathway_learning.graph.sign_evidence import (
    DEFAULT_SIGNALLING_EVIDENCES,
    DEFAULT_TRANSCRIPTION_EVIDENCES,
    DISPUTE_COLUMN,
    read_evidences,
    sign_evidence_columns,
    sign_reference_table,
)


DEFAULT_SPECIES = Path("data/raw/icite/icite_species.parquet")


def label_summary(evidence: pd.DataFrame, species: pd.DataFrame) -> dict:
    """How many curated edges the label rule of decision 9.63 (b) takes as known, by family, beside what stricter
    readings of "evidence from humans" would take (for the owner, not used by the trainer)."""
    curated = evidence["kind"] == "curated"
    labels = curated_edge_labels(evidence)
    stricter = species_of_records(evidence["pubmed_ids"], species, human_share_above=0.5)
    by_family = {}
    for family, group in evidence[curated].groupby("family"):
        by_family[family] = {"curated_edges": int(len(group)), "not_contested_two_or_more_records": int(((group.records >= 2) & ~group.contested).sum()),
                             "labels": int(labels[group.index].sum()) if len(group) else 0}
    return {"rule": "curated kind, not contested, at least 2 records (distinct PubMed ids), at least 1 with iCite human score above 0",
            "labels": int(labels.sum()), "by_family": by_family,
            "curated_edges_with_an_unscored_record": int((curated & (evidence["species_known_records"] < evidence["records"])).sum()),
            "curated_edges_with_an_animal_only_record": int((curated & (evidence["animal_only_records"] > 0)).sum()),
            "stricter_readings": {
                "two_human_records": int(curated_edge_labels(evidence, minimum_human_records=2).sum()),
                "a_record_with_human_score_above_one_half": int(curated_edge_labels(evidence.assign(human_records=stricter["human_records"])).sum()),
                **({f"sign_with_{minimum}_or_more_records": int(curated_edge_labels(evidence, minimum_sign_records=minimum).sum()) for minimum in (1, 2)}
                   if "sign_basis" in evidence.columns else {}),
                "bulk_papers_as_one_record": int(curated_edge_labels(evidence, bulk_papers="one").sum()),
                "bulk_papers_not_counted": int(curated_edge_labels(evidence, bulk_papers="none").sum()),
                **({"sign_undisputed": int(curated_edge_labels(evidence, exclude_disputed_signs=True).sum()),
                    "sign_with_1_or_more_records_and_undisputed": int(curated_edge_labels(evidence, minimum_sign_records=1, exclude_disputed_signs=True).sum())}
                   if DISPUTE_COLUMN in evidence.columns else {})}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--omnipath", type=Path, default=Path("data/raw/omnipath/omnipath_interactions.tsv"))
    parser.add_argument("--collectri", type=Path, default=Path("data/raw/omnipath/collectri_interactions.tsv"))
    parser.add_argument("--intact-negative", type=Path, default=Path("data/raw/intact/intact_negative.txt"))
    parser.add_argument("--uniprot", type=Path, default=DEFAULT_REVIEWED_PROTEOME,
                        help="UniProt's reviewed human proteome; an IntAct record on an isoform, a chain or an entry outside it contests no edge (decision 9.88)")
    parser.add_argument("--tiers", type=Path, default=DEFAULT_TIERS_PATH)
    parser.add_argument("--signalling-evidences", type=Path, default=DEFAULT_SIGNALLING_EVIDENCES,
                        help="OmniPath's interactions with fields=evidences (scripts/fetch_raw_sources.sh); without it and the next the table has no sign columns")
    parser.add_argument("--transcription-evidences", type=Path, default=DEFAULT_TRANSCRIPTION_EVIDENCES,
                        help="the same for the CollecTRI dataset, which carries CollecTRI's sign_decision")
    parser.add_argument("--curated-edge-species", type=Path, default=DEFAULT_CURATED_EDGE_SPECIES_PATH,
                        help="the edges whose every cited record is non-human, with the sentence that says so (decision 9.76); such an edge takes the nonhuman_only_evidence tier")
    parser.add_argument("--species", type=Path, default=DEFAULT_SPECIES,
                        help="iCite's species scores per PubMed id (experiments/fetch_icite_species.py); without it the table has no species columns and "
                             "the trainer cannot take curated edges as labels (decision 9.63)")
    parser.add_argument("--negative-evidence", action=argparse.BooleanOptionalAction, default=True,
                        help="add the negative and positive edge observations of decision 9.91 for every source whose files are in data/raw "
                             "(graph/edge_negative_sources.py); a source whose files are absent writes no columns")
    arguments = parser.parse_args()
    columns = ["source", "target", "source_genesymbol", "target_genesymbol", "sources", "references"]
    references = pd.concat([signalling_references(pd.read_csv(arguments.omnipath, sep="\t", usecols=columns)),
                            transcription_references(pd.read_csv(arguments.collectri, sep="\t", usecols=columns))], ignore_index=True)
    negative_records = read_human_negative_pairs(arguments.intact_negative, read_reviewed_proteome(arguments.uniprot))
    negative_pairs = gene_pairs_between_whole_proteins(negative_records)
    edges = pd.read_parquet(arguments.graph_dir / "edges.parquet")
    evidence = edge_evidence_table(edges, references, negative_pairs)
    evidence = evidence.assign(source_id=edges.source_id.to_numpy(), target_id=edges.target_id.to_numpy(), relation_type=edges.relation_type.to_numpy())
    nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet")
    evidence[FACTOR_BELOW_DETECTION_COLUMN] = factor_below_detection_flags(evidence, nodes)
    curated_species = read_curated_edge_species(arguments.curated_edge_species) if arguments.curated_edge_species.is_file() else {}
    evidence[NONHUMAN_ONLY_EVIDENCE_COLUMN] = nonhuman_only_evidence_flags(evidence, curated_species)
    if "expression_below_detection" not in nodes.columns:
        print(f"{arguments.graph_dir}/nodes.parquet has no expression_below_detection column (built before decision 9.76): no transcription edge takes the lowered tier",
              file=sys.stderr)
    sign_summary = None
    if arguments.signalling_evidences.is_file() and arguments.transcription_evidences.is_file():
        sign_tables = pd.concat([sign_reference_table(read_evidences(arguments.signalling_evidences), "signalling"),
                                 sign_reference_table(read_evidences(arguments.transcription_evidences), "transcription")], ignore_index=True)
        evidence = pd.concat([evidence, sign_evidence_columns(edges, evidence["family"], sign_tables)], axis=1)
        signed = ~evidence["sign_basis"].fillna("").astype(str).isin(["", "unsigned"])
        sign_summary = {"signalling_evidences": {"path": str(arguments.signalling_evidences), "sha256": hashlib.sha256(arguments.signalling_evidences.read_bytes()).hexdigest()},
                        "transcription_evidences": {"path": str(arguments.transcription_evidences),
                                                    "sha256": hashlib.sha256(arguments.transcription_evidences.read_bytes()).hexdigest()},
                        "signed_edges": int(signed.sum()), "sign_basis": evidence.loc[signed, "sign_basis"].value_counts().head(12).to_dict(),
                        "signed_edges_with_no_pubmed_id_behind_the_sign": int((signed & (evidence["sign_records"] == 0)).sum()),
                        "regulations_whose_collectri_releases_dispute_the_sign": int(evidence[DISPUTE_COLUMN].sum())}
    else:
        print("no OmniPath evidences downloads: the table has no sign columns (decision 9.70)", file=sys.stderr)
    species_summary, labels = None, None
    if arguments.species.is_file():
        species = read_species(arguments.species)
        evidence = pd.concat([evidence, species_of_records(evidence["pubmed_ids"], species)], axis=1)
        curated_ids = {identifier for cell in evidence.loc[evidence["kind"] == "curated", "pubmed_ids"] for identifier in split_pubmed_ids(cell)}
        species_summary = {"path": str(arguments.species), "sha256": hashlib.sha256(arguments.species.read_bytes()).hexdigest(),
                           "curated_pubmed_ids": len(curated_ids), "curated_pubmed_ids_unscored": len(curated_ids - set(species.index))}
        labels = label_summary(evidence, species)
    else:
        print(f"no species cache at {arguments.species}: run experiments/fetch_icite_species.py first, or no curated edge can be taken as a label", file=sys.stderr)
    negative_summary = None
    if arguments.negative_evidence:
        negative_columns, negative_summary = assemble_negative_evidence(evidence, edges, nodes, NegativeEvidencePaths())
        evidence = pd.concat([evidence, negative_columns], axis=1)
        absent = [source for source, record in negative_summary["sources"].items() if "absent" in record]
        if absent:
            print(f"negative edge observations (decision 9.91) absent for {', '.join(absent)}: their files are not in data/raw; "
                  "experiments/build_edge_negative_evidence.py adds them later", file=sys.stderr)
    evidence.to_parquet(arguments.graph_dir / "edge_evidence.parquet", index=False)
    gated, probability, strength = edge_priors(evidence, read_edge_tiers(arguments.tiers))
    edges_sha256 = hashlib.sha256((arguments.graph_dir / "edges.parquet").read_bytes()).hexdigest()
    summary = {"graph_dir": str(arguments.graph_dir), "edges_sha256": edges_sha256, "tiers": str(arguments.tiers), **summarise(evidence, gated, probability, strength),
               "intact_negatives": {"human_records": len(negative_records), "records_between_whole_proteins": sum(pair.between_whole_proteins for pair in negative_records),
                                    "gene_pairs_between_whole_proteins": len(negative_pairs)},
               "species": species_summary, "curated_edge_labels": labels, "sign_evidence": sign_summary,
               "negative_evidence": negative_summary}
    (arguments.graph_dir / "edge_evidence_summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {arguments.graph_dir / 'edge_evidence.parquet'}: {summary['gated']:,} of {summary['edges']:,} edges gated, {summary['contested']} contested"
          + ("" if labels is None else f"; {labels['labels']:,} curated edges are labels under decision 9.63 (b)")
          + f"; {summary[FACTOR_BELOW_DETECTION_COLUMN]['edges']:,} transcription edges of {summary[FACTOR_BELOW_DETECTION_COLUMN]['factors']} factors below detection take the lowered tier"
          + f"; {summary[NONHUMAN_ONLY_EVIDENCE_COLUMN]['edges']} edges cite non-human records only (curated), {summary[NONHUMAN_ONLY_EVIDENCE_COLUMN]['edges_every_record_animal_only_by_icite']:,} would under iCite's scores")
    for key, value in summary["by_family_and_kind"].items():
        print(f"  {key:34s} {value['edges']:7,} edges, mean prior {value['mean_prior'] if value['mean_prior'] is None else round(value['mean_prior'], 3)}, mean strength {value['mean_strength']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
