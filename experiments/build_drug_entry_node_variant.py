"""Build the drug-entry-node variant of a graph directory (mechanistic_pathway_learning/graph/drug_entry_nodes.py;
docs/records/2026-10/drug_entry_nodes.md): <graph-dir>_drugs, with one node per drug perturbation, its mechanism edges and, for a
drug whose plasma carrier is known, the carrier's sequestration edge.

It writes a new directory and changes no existing one, so no registered input moves. Whether a confirmatory
configuration reads the variant is the user's decision and needs a dated amendment (docs/records/2026-10/drug_entry_nodes.md).

Inputs:
  - the source graph directory, with gene_to_protein.parquet when it splits genes from proteins, so a drug's mechanism
    edges land on the protein nodes its seeds would land on;
  - the evidence table, whose drug rows name each drug perturbation and its seeds (perturbation_nodes);
  - configs/drug_plasma_carriers.csv, the carrier of each drug the labels or the fraction-unbound database name one for
    (experiments/scope_label_plasma_binder_coverage.py); pass --carrier-table none to add no sequestration edge;
  - configs/drugs_acting_as_graph_compounds.csv, the drugs that are themselves a graph metabolite and get no node;
    where a row sets moves_mechanism_to_compound_edges (melatonin), the ChEMBL caches of --chembl-dir, from which the
    drug's mechanism is read so that the merge can sign the compound's own edges to its targets
    (graph/drug_entry_nodes.py, "The merge"; compound_mechanisms_of_graph);
  - with --clearing-enzymes, configs/drug_clearing_enzymes.csv (experiments/build_drug_clearing_enzymes.py): each row
    marked gives_an_edge adds a clearance edge, relation clears and sign -1, from the enzyme to the drug's node.

Outputs in the new directory: nodes.parquet, edges.parquet and relation_types.json with rows appended and none changed
but the compound edges a merge signs, which the summary lists (compound_edges_signed_at_the_merge) and the build checks
are the only rows changed, in relation, sign and evidence only;
drug_entry_nodes.parquet, one row per mechanism edge with its sign and magnitude, which the loader reads
(experiment_data.load_experiment_data, drug_entry); drug_entry_summary.json; and a copy of every other file of the
source directory. Each --descriptor-table and --cell-class-weights pair (source:destination) writes the per-node table
with a row per drug node: zeros for descriptors, ones for cell-class weights.

Usage:
  PYTHONPATH=. python experiments/build_drug_entry_node_variant.py --graph-dir data/processed/graph_full_neuronal_split_binders \\
      --evidence-dir data/processed/evidence_full_v3_parkinsonism
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.evaluation.experiment_data import drug_seeds_on_proteins, read_protein_of_gene
from mechanistic_pathway_learning.evidence.allele_mechanisms import read_neomorphic_alleles
from mechanistic_pathway_learning.graph.drug_entry_nodes import (
    DRUG_ENTRY_FILE,
    DRUG_NODE_TYPE,
    ENTRY_NODE_TYPES,
    add_allele_entry_nodes,
    add_drug_entry_nodes,
    extend_table_for_drug_nodes,
)
from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import (
    CHEMBL_RELEASE_FILENAME,
    DRUGS_ACTING_AS_GRAPH_COMPOUNDS_PATH,
    ChemblCaches,
    GraphNodeLookup,
    compound_mechanism_targets,
    load_chembl_caches,
    read_compounds_moving_their_mechanism,
)

SUMMARY_FILE = "drug_entry_summary.json"
REWRITTEN_FILES = ("nodes.parquet", "edges.parquet", "relation_types.json", DRUG_ENTRY_FILE, SUMMARY_FILE)
DESCRIPTOR_FILL, CELL_CLASS_WEIGHT_FILL = 0.0, 1.0
MERGE_CHANGED_EDGE_COLUMNS = ("relation_type", "sign", "evidence_source")  # what a merge changes on a compound edge (sign_compound_edges)


def source_and_destination(value: str) -> tuple[Path, Path]:
    source, separator, destination = value.partition(":")
    if not separator or not source or not destination:
        raise argparse.ArgumentTypeError("expected source:destination")
    return Path(source), Path(destination)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def drug_seeds_of_evidence(evidence: pd.DataFrame, node_ids: set[str], protein_of_gene: dict[str, list[str]]) -> dict[str, tuple[str, list[tuple[str, float, float]]]]:
    """perturbation id -> (drug name, the seeds the loader places for it on this graph).

    The same two steps as experiment_data.load_experiment_data: keep the triples whose node is in the graph, then on a
    split graph move each target gene's triple onto its protein nodes."""
    drug_rows = evidence[evidence.perturbation_type == "drug"].drop_duplicates("perturbation_id")
    seeds = {}
    for row in drug_rows.itertuples(index=False):
        triples = [triple for triple in json.loads(row.perturbation_nodes) if triple[0] in node_ids]
        if protein_of_gene:
            triples = drug_seeds_on_proteins(triples, protein_of_gene)
        seeds[str(row.perturbation_id)] = (str(row.perturbation_label), [(str(node_id), float(sign), float(magnitude)) for node_id, sign, magnitude in triples])
    return seeds


def compound_mechanisms_of_graph(moving_compounds: dict[frozenset[str], list[str]], caches: ChemblCaches, nodes: pd.DataFrame,
                                 protein_of_gene: dict[str, list[str]]) -> dict[frozenset[str], list[tuple[str, float]]]:
    """For each listed compound whose drug's mechanism moves onto the compound's edges at the merge
    (read_compounds_moving_their_mechanism), the (node id, sign) of each node of this graph the mechanism reaches: the
    targets compound_mechanism_targets reads from the caches, placed as the drug's own seeds were placed before the
    merge (GraphNodeLookup.perturbation_nodes, then drug_seeds_on_proteins on a split graph, the two steps of
    drug_seeds_of_evidence). Refused: a compound none of whose ChEMBL forms has a mechanism target left, and one whose
    targets have no node in this graph, since either merge would move nothing."""
    lookup = GraphNodeLookup.from_nodes(nodes)
    mechanisms: dict[frozenset[str], list[tuple[str, float]]] = {}
    for bases, targets in compound_mechanism_targets(moving_compounds, caches).items():
        if not targets:
            raise ValueError(f"the listing moves the mechanism of {sorted(bases)}, but none of its ChEMBL forms {moving_compounds[bases]} has a mechanism target")
        triples = lookup.perturbation_nodes(targets)
        if protein_of_gene:
            triples = drug_seeds_on_proteins(triples, protein_of_gene)
        if not triples:
            raise ValueError(f"no target of the mechanism of {sorted(bases)} ({[target.target_chembl_id for target in targets]}) is a node of this graph")
        mechanisms[bases] = [(str(node_id), float(sign)) for node_id, sign, _ in triples]
    return mechanisms


def edge_rows_changed(edges: pd.DataFrame, new_edges: pd.DataFrame) -> tuple[list[int], list[str]]:
    """(the positions of edges' rows that differ in new_edges, which begins with them; the columns they differ in). Two
    missing values are equal."""
    before = edges.reset_index(drop=True)
    after = new_edges.iloc[: len(edges)].reset_index(drop=True)
    differs = before.ne(after) & ~(before.isna() & after.isna())
    return [int(row) for row in differs.any(axis=1).to_numpy().nonzero()[0]], [str(column) for column in differs.columns[differs.any(axis=0).to_numpy()]]


def graph_compound_base_ids(path: Path) -> list[frozenset[str]]:
    if not path.exists():
        return []
    table = pd.read_csv(path, dtype=str).fillna("")
    return [frozenset(base_id for base_id in cell.split(";") if base_id) for cell in table.base_metabolite_ids if cell]


def extend_tables_for_entry_nodes(arguments) -> None:
    """--tables-only: the per-node tables of a variant graph that was built without them. The graph files are read,
    never written, so their hashes do not move; each table's source, hash and fill value are added to per_node_tables
    in the variant's summary, where a full build records them."""
    output_directory = arguments.output_dir or arguments.graph_dir.parent / f"{arguments.graph_dir.name}_drugs"
    nodes = pd.read_parquet(output_directory / "nodes.parquet")
    source_nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet")
    entry_node_ids = list(nodes.node_id[nodes.node_type.isin(ENTRY_NODE_TYPES)])
    written_tables = {}
    for (source, destination), fill_value in [(pair, DESCRIPTOR_FILL) for pair in arguments.descriptor_table] + [(pair, CELL_CLASS_WEIGHT_FILL) for pair in arguments.cell_class_weights]:
        if destination.exists() and not arguments.overwrite:
            raise SystemExit(f"{destination} exists; pass --overwrite to replace it")
        table = pd.read_parquet(source)
        missing = set(source_nodes.node_id) - set(table.index)
        if missing:
            raise SystemExit(f"{source} has no row for {len(missing)} nodes of {arguments.graph_dir}")
        extended = extend_table_for_drug_nodes(table, entry_node_ids, fill_value)
        if set(nodes.node_id) - set(extended.index):
            raise SystemExit(f"{destination} would still miss nodes of {output_directory}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        extended.to_parquet(destination)
        written_tables[str(destination)] = {"source": str(source), "source_sha256": file_sha256(source), "sha256": file_sha256(destination), "fill_value": fill_value,
                                            "written_by": "--tables-only"}
        print(f"wrote {destination}: {len(extended):,} rows, {len(entry_node_ids)} entry nodes filled with {fill_value}")
    summary_path = output_directory / SUMMARY_FILE
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        summary["per_node_tables"] = {**summary.get("per_node_tables", {}), **written_tables}
        summary_path.write_text(json.dumps(summary, indent=1) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--graph-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None, help="default: <graph-dir>_drugs")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--carrier-table", default="configs/drug_plasma_carriers.csv", help="per-drug plasma carrier; none adds no sequestration edge")
    parser.add_argument("--clearing-enzymes", default="none",
                        help="per-drug clearing enzymes (configs/drug_clearing_enzymes.csv); the rows with gives_an_edge add a clearance edge, relation clears. none, the default, adds none")
    parser.add_argument("--drugs-acting-as-graph-compounds", type=Path, default=DRUGS_ACTING_AS_GRAPH_COMPOUNDS_PATH)
    parser.add_argument("--chembl-dir", type=Path, default=Path("data/raw/chembl"),
                        help="the ChEMBL caches (experiments/fetch_chembl_drug_targets.py) a listed endogenous drug's mechanism is read from for the merge; "
                             "read only when --drugs-acting-as-graph-compounds sets moves_mechanism_to_compound_edges on a row")
    parser.add_argument("--descriptor-table", type=source_and_destination, action="append", default=[])
    parser.add_argument("--cell-class-weights", type=source_and_destination, action="append", default=[])
    parser.add_argument("--neomorphic-alleles", default="none",
                        help="curated neomorphic alleles (configs/neomorphic_alleles.csv, decision 9.54): one entry node per allele with its cited mechanism edges. "
                             "none, the default, adds none")
    parser.add_argument("--tables-only", action="store_true",
                        help="extend --descriptor-table and --cell-class-weights for the entry nodes of the graph already in --output-dir, and write no graph file")
    parser.add_argument("--overwrite", action="store_true")
    arguments = parser.parse_args()
    if arguments.tables_only:
        extend_tables_for_entry_nodes(arguments)
        return

    output_directory = arguments.output_dir or arguments.graph_dir.parent / f"{arguments.graph_dir.name}_drugs"
    if (output_directory / "nodes.parquet").exists() and not arguments.overwrite:
        raise SystemExit(f"{output_directory} already holds a graph; pass --overwrite to replace it")
    nodes = pd.read_parquet(arguments.graph_dir / "nodes.parquet")
    edges = pd.read_parquet(arguments.graph_dir / "edges.parquet")
    relation_types = json.loads((arguments.graph_dir / "relation_types.json").read_text())
    if (nodes.node_type == DRUG_NODE_TYPE).any():
        raise SystemExit(f"{arguments.graph_dir} already has drug nodes")
    protein_of_gene = read_protein_of_gene(arguments.graph_dir)
    evidence = pd.read_parquet(arguments.evidence_dir / "evidence_records.parquet")
    drug_seeds = drug_seeds_of_evidence(evidence, set(nodes.node_id), protein_of_gene)
    carriers = None
    if str(arguments.carrier_table).lower() != "none":
        carriers = pd.read_csv(arguments.carrier_table, dtype=str).fillna("")
        carriers = carriers.assign(evidence=carriers.source)
    carrier_nodes_of_gene = None
    if protein_of_gene:  # binding is the protein's property on a split graph, as for the plasma carriage edges; so is catalysis
        carrier_nodes_of_gene = {gene_node.removeprefix("GENE:"): proteins for gene_node, proteins in protein_of_gene.items()}
    clearing_enzymes = None
    if str(arguments.clearing_enzymes).lower() != "none":
        clearing_enzymes = pd.read_csv(arguments.clearing_enzymes, dtype=str).fillna("")
        clearing_enzymes = clearing_enzymes[clearing_enzymes.gives_an_edge.str.lower() == "true"]
        clearing_enzymes = clearing_enzymes.assign(evidence="FDA Table of Pharmacogenetic Associations, section " + clearing_enzymes.fda_table_section)

    # the merge (graph/drug_entry_nodes.py): a listed endogenous drug's mechanism, read from the same caches as the evidence build's
    moving_compounds = read_compounds_moving_their_mechanism(arguments.drugs_acting_as_graph_compounds)
    compound_mechanisms, merge_inputs = None, {}
    if moving_compounds:
        compound_mechanisms = compound_mechanisms_of_graph(moving_compounds, load_chembl_caches(arguments.chembl_dir), nodes, protein_of_gene)
        release_path = arguments.chembl_dir / CHEMBL_RELEASE_FILENAME
        merge_inputs = {
            "drugs_acting_as_graph_compounds": str(arguments.drugs_acting_as_graph_compounds),
            "drugs_acting_as_graph_compounds_sha256": file_sha256(arguments.drugs_acting_as_graph_compounds),
            "chembl_dir": str(arguments.chembl_dir),
            "chembl_release": json.loads(release_path.read_text()).get("chembl_db_version") if release_path.exists() else None,
            "chembl_mechanisms_sha256": file_sha256(arguments.chembl_dir / "mechanisms.json"),
            "chembl_targets_sha256": file_sha256(arguments.chembl_dir / "targets.json"),
            "compound_mechanisms": {";".join(sorted(bases)): [list(pair) for pair in mechanism] for bases, mechanism in sorted(compound_mechanisms.items(), key=lambda item: sorted(item[0]))},
        }

    new_nodes, new_edges, new_relations, entry_table, summary = add_drug_entry_nodes(
        nodes, edges, relation_types, drug_seeds, graph_compound_base_ids(arguments.drugs_acting_as_graph_compounds), carriers, carrier_nodes_of_gene, clearing_enzymes,
        compound_mechanisms)
    if str(arguments.neomorphic_alleles).lower() != "none":  # after the drugs, so the graph without alleles is this one with its last rows dropped
        new_nodes, new_edges, new_relations, allele_entries, allele_summary = add_allele_entry_nodes(
            new_nodes, new_edges, new_relations, read_neomorphic_alleles(Path(arguments.neomorphic_alleles)), protein_of_gene)
        entry_table = pd.concat([entry_table, allele_entries], ignore_index=True)
        summary.update(allele_summary, neomorphic_alleles=str(arguments.neomorphic_alleles), neomorphic_alleles_sha256=file_sha256(Path(arguments.neomorphic_alleles)))
    changed_rows, changed_columns = edge_rows_changed(edges, new_edges)
    signed_rows = sorted(record["edge_row"] for record in summary.get("compound_edges_signed_at_the_merge", []))
    if (not new_nodes.iloc[: len(nodes)].reset_index(drop=True).equals(nodes) or changed_rows != signed_rows
            or not set(changed_columns) <= set(MERGE_CHANGED_EDGE_COLUMNS)):
        raise SystemExit("an existing node or edge row changed other than in the relation, sign and evidence of the compound edges a merge signs; "
                         "the variant must otherwise only append")

    output_directory.mkdir(parents=True, exist_ok=True)
    for source_file in sorted(arguments.graph_dir.iterdir()):  # gene_to_protein.parquet and the source's own summaries
        if source_file.is_file() and source_file.name not in REWRITTEN_FILES:
            shutil.copy2(source_file, output_directory / source_file.name)
    new_nodes.to_parquet(output_directory / "nodes.parquet")
    new_edges.to_parquet(output_directory / "edges.parquet")
    (output_directory / "relation_types.json").write_text(json.dumps(new_relations, indent=1) + "\n")
    entry_table.to_parquet(output_directory / DRUG_ENTRY_FILE, index=False)
    drug_node_ids = list(new_nodes.node_id[new_nodes.node_type.isin(ENTRY_NODE_TYPES)])  # drugs and alleles
    written_tables = {}
    for (source, destination), fill_value in [(pair, DESCRIPTOR_FILL) for pair in arguments.descriptor_table] + [(pair, CELL_CLASS_WEIGHT_FILL) for pair in arguments.cell_class_weights]:
        if destination.exists() and not arguments.overwrite:
            raise SystemExit(f"{destination} exists; pass --overwrite to replace it")
        table = pd.read_parquet(source)
        missing = set(nodes.node_id) - set(table.index)
        if missing:
            raise SystemExit(f"{source} has no row for {len(missing)} nodes of {arguments.graph_dir}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        extend_table_for_drug_nodes(table, drug_node_ids, fill_value).to_parquet(destination)
        written_tables[str(destination)] = {"source": str(source), "source_sha256": file_sha256(source), "sha256": file_sha256(destination), "fill_value": fill_value}
    summary.update(
        source_graph=str(arguments.graph_dir), evidence=str(arguments.evidence_dir),
        evidence_records_sha256=file_sha256(arguments.evidence_dir / "evidence_records.parquet"),
        carrier_table=None if carriers is None else str(arguments.carrier_table),
        carrier_table_sha256=None if carriers is None else file_sha256(Path(arguments.carrier_table)),
        **({} if clearing_enzymes is None else {"clearing_enzymes": str(arguments.clearing_enzymes), "clearing_enzymes_sha256": file_sha256(Path(arguments.clearing_enzymes))}),
        **merge_inputs,
        nodes=int(len(new_nodes)), edges=int(len(new_edges)),
        source_nodes_sha256=file_sha256(arguments.graph_dir / "nodes.parquet"), source_edges_sha256=file_sha256(arguments.graph_dir / "edges.parquet"),
        nodes_sha256=file_sha256(output_directory / "nodes.parquet"), edges_sha256=file_sha256(output_directory / "edges.parquet"),
        per_node_tables=written_tables,
    )
    (output_directory / SUMMARY_FILE).write_text(json.dumps(summary, indent=1) + "\n")
    print(output_directory, json.dumps({key: value for key, value in summary.items() if not isinstance(value, list) or len(value) < 12}, indent=1))


if __name__ == "__main__":
    main()
