"""Physiology graph construction (design section 4.1).

Layers and sources:
  metabolic      Human-GEM (SBML from github.com/SysBioChalmers/Human-GEM) via cobra:
                 metabolite nodes (compartment-specific), reaction nodes, gene nodes,
                 edges substrate_of (metabolite -> reaction), product_of (reaction -> metabolite),
                 catalyzed_by (gene -> reaction, from the gene-protein-reaction rule; the AND/OR
                 structure of the rule is kept as a reaction attribute, not expanded, in version 1).
                 Reversible reactions get both orientations of their substrate and product edges.
                 A reaction whose metabolites span more than one compartment is tagged is_transport;
                 those reactions are the only edges that connect compartments.
  signaling      OmniPath post-translational interactions (omnipath, pathwayextra, ligrecextra):
                 activates or inhibits by the consensus sign, binds when the sign is unknown
                 (binds edges are added in both directions). Protein complexes written as
                 A_B_C are expanded to their member genes.
  small molecule OmniPath small_molecule_protein interactions joined to Human-GEM metabolites
                 by PubChem identifier (metabolites.tsv): binds edges from a metabolite node
                 (its extracellular instance when present, else every compartment instance)
                 to the receptor or enzyme node, so dopamine reaches DRD1-5 and so on.
  transcription  CollecTRI regulons: regulates_transcription_of with the consensus sign.
  pharmacology   ChEMBL mechanisms: targets, with action type                    (joined downstream)
  attributes     currency tag per metabolite (tag_currency_metabolites); brain expression (--brain-expression, below)

Gene and protein nodes share one identifier space, GENE:<symbol>: metabolic genes with a
symbol in genes.tsv are remapped from their Ensembl identifier, and signaling or
transcription participants that are not in Human-GEM become gene nodes with
in_metabolic_layer false. Metabolic genes without a symbol keep the Ensembl identifier.

Brain expression (GTEx median TPM, --brain-expression) annotates gene nodes with brain_median_tpm_max,
body_median_tpm_max, brain_expression_known and brain_expressed, and gives reactions the largest brain value over
their genes. Cell-class expression (--cell-class-expression, the Human Protein Atlas single-nucleus cluster types
pooled into the brain classes of brain_expression_descriptors, with the peripheral endocrine classes of
peripheral_cell_classes joined on) annotates gene nodes with cell_class_ncpm_max and cell_class_expression_known.
The transcription gate (restrict_transcription_edges_to_expressed_factors, decision 9.76) drops a factor's regulon
only when the factor is at 0 in every cell class and below the TPM threshold in every GTEx tissue of the body;
a factor below the brain TPM threshold whose largest class value is under the detection threshold keeps its edges
with expression_below_detection set, which the edge evidence reads to lower their prior.

Hard structural constraints are enforced here, not in the model: no other edge types,
no symptom-symptom edges, no disease nodes, compartment changes only via transport
reactions, pharmacological edges only with measured activity.

Outputs (output_directory, default data/processed/graph/):
  nodes.parquet          node_id, node_type, display_name, compartment, is_currency, degree,
                         gene_symbol (genes), is_transport and reversible (reactions), base_metabolite_id
  edges.parquet          source_id, target_id, relation_type, sign, evidence_source
  relation_types.json    ordered list used as the encoder's relation index
  graph_summary.json     counts for the Phase 1 quality checks
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict, deque
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.tag_currency_metabolites import retag_currency_by_name, tag_currency_metabolites

RELATION_TYPES: list[str] = [
    "substrate_of",
    "product_of",
    "catalyzed_by",
    "binds",
    "activates",
    "inhibits",
    "regulates_transcription_of",
    "targets",
    # decision 9.86, appended so that every relation before them keeps its index
    "couples_primary",
    "couples_secondary",
    "g_alpha_regulates_effector",
]


def load_human_gem(model_path: Path):
    import pickle

    if model_path.suffix == ".pkl":
        with open(model_path, "rb") as cached:
            return pickle.load(cached)
    from cobra.io import read_sbml_model

    return read_sbml_model(str(model_path))


def gene_symbols_from_table(genes_table_path: Path | None) -> dict[str, str]:
    if genes_table_path is None or not genes_table_path.exists():
        return {}
    symbol_by_ensembl: dict[str, str] = {}
    with open(genes_table_path, encoding="utf-8") as genes_file:
        for row in csv.DictReader(genes_file, delimiter="\t", quotechar='"'):
            symbols = [symbol.strip() for symbol in (row.get("geneSymbols") or "").split(";") if symbol.strip()]
            if symbols:
                symbol_by_ensembl[row["genes"]] = symbols[0]
    return symbol_by_ensembl


def subsystem_by_reaction(model, model_yaml_path: Path | None = None) -> dict[str, str]:
    """Reaction id -> subsystem. SBML groups when the file has them; else the Human-GEM yml, whose reaction
    entries carry a subsystem list (the first entry is kept), parsed line by line to avoid loading the whole document."""
    subsystems: dict[str, str] = {}
    for group in getattr(model, "groups", []):
        for member in group.members:
            subsystems.setdefault(member.id, group.name)
    if subsystems or model_yaml_path is None or not model_yaml_path.exists():
        return subsystems
    current_reaction: str | None = None
    in_subsystem_list = False
    with open(model_yaml_path, encoding="utf-8") as yaml_file:
        for raw_line in yaml_file:
            line = raw_line.strip()
            if line.startswith("- id:"):
                current_reaction = line[len("- id:"):].strip().strip('"').strip("'")
                in_subsystem_list = False
            elif line.startswith("- subsystem:") or line.startswith("subsystem:"):
                remainder = line.split(":", 1)[1].strip()
                in_subsystem_list = remainder == ""
                if remainder and current_reaction is not None:
                    subsystems.setdefault(current_reaction, remainder.strip("[]").split(",")[0].strip().strip('"').strip("'"))
            elif in_subsystem_list and line.startswith("- ") and current_reaction is not None:
                subsystems.setdefault(current_reaction, line[2:].strip().strip('"').strip("'"))
                in_subsystem_list = False
            elif in_subsystem_list and not line.startswith("- "):
                in_subsystem_list = False
    return subsystems


def gene_node_id(symbol: str) -> str:
    return f"GENE:{symbol}"


def build_metabolic_layer(model, symbol_by_ensembl: dict[str, str], model_yaml_path: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    subsystems = subsystem_by_reaction(model, model_yaml_path)
    node_rows: list[dict] = []
    edge_rows: list[dict] = []

    def metabolic_gene_node(gene_identifier: str) -> str:
        symbol = symbol_by_ensembl.get(gene_identifier)
        return gene_node_id(symbol) if symbol else gene_identifier

    for metabolite in model.metabolites:
        node_rows.append({
            "node_id": metabolite.id,
            "node_type": "metabolite",
            "display_name": metabolite.name,
            "compartment": metabolite.compartment,
            "base_metabolite_id": metabolite.id[:-1] if metabolite.id[-1].isalpha() else metabolite.id,
            "degree": len(metabolite.reactions),
        })
    seen_gene_nodes: set[str] = set()
    for gene in model.genes:
        node_identifier = metabolic_gene_node(gene.id)
        if node_identifier in seen_gene_nodes:
            continue
        seen_gene_nodes.add(node_identifier)
        node_rows.append({
            "node_id": node_identifier,
            "node_type": "gene",
            "display_name": symbol_by_ensembl.get(gene.id, gene.id),
            "gene_symbol": symbol_by_ensembl.get(gene.id),
            "ensembl_gene_id": gene.id,
            "in_metabolic_layer": True,
            "degree": len(gene.reactions),
        })
    for reaction in model.reactions:
        compartments = {metabolite.compartment for metabolite in reaction.metabolites}
        node_rows.append({
            "node_id": reaction.id,
            "node_type": "reaction",
            "display_name": reaction.name,
            "compartment": ";".join(sorted(compartments)),
            "is_transport": len(compartments) > 1,
            "reversible": reaction.reversibility,
            "gene_reaction_rule": reaction.gene_reaction_rule,
            "subsystem": subsystems.get(reaction.id, ""),
            "degree": len(reaction.metabolites) + len(reaction.genes),
        })
        for metabolite, coefficient in reaction.metabolites.items():
            is_substrate = coefficient < 0
            # The nominal direction only, from the stoichiometric sign, for reversible reactions as for the rest. The
            # build used to add the mirror pair for every reversible reaction, substrate_of and product_of in both
            # directions at +1, so every participant received +1 and -1 from the same reaction and cancelled: 15,867
            # such pairs, 1,809 metabolites with a field identically zero under every perturbation. Reversal is carried
            # instead by the `reversible` flag on the reaction node, from which the linear-response encoder derives
            # product -> reaction at sign -1 (product_opposes, preregistration item 27): linearised mass action, under
            # which a perturbation that accumulates the product drives the reaction backwards.
            # The magnitude is kept as well as the sign (preregistration item 20, built 14 October 2026). It is how
            # many copies of the participant one turnover consumes or makes, and the linear-response encoder's
            # limiting-step pass divides a node's supply by it, so acetylcholine needing two molecules to open the
            # receptor halves what arrives. Before this the coefficient was read for `is_substrate` and discarded, so
            # every demand was 1 and a reaction consuming two molecules counted as one.
            edge_rows.append({"source_id": metabolite.id if is_substrate else reaction.id, "target_id": reaction.id if is_substrate else metabolite.id, "relation_type": "substrate_of" if is_substrate else "product_of", "sign": 1.0, "evidence_source": "Human-GEM", "stoichiometric_coefficient": abs(float(coefficient))})
        # cobra's reaction.genes is a frozenset, so its iteration order follows the hash seed and a rebuild moved
        # 16,056 catalyzed_by rows on 10 October 2026 (docs/data_layer_rebuild.md); sorted, the build is reproducible
        for gene in sorted(reaction.genes, key=lambda gene: gene.id):
            edge_rows.append({"source_id": metabolic_gene_node(gene.id), "target_id": reaction.id, "relation_type": "catalyzed_by", "sign": 1.0, "evidence_source": "Human-GEM GPR", "stoichiometric_coefficient": 1.0})
    nodes = pd.DataFrame(node_rows)
    edges = pd.DataFrame(edge_rows).drop_duplicates()
    if "stoichiometric_coefficient" in edges.columns:  # 1.0 wherever a relation carries no stoichiometry
        edges["stoichiometric_coefficient"] = edges.stoichiometric_coefficient.fillna(1.0)
    return nodes, edges


def expand_complex(symbol_field: str) -> list[str]:
    """OmniPath writes complexes as A_B_C; return the member symbols (a plain symbol returns itself)."""
    return [member for member in symbol_field.split("_") if member]


def interaction_sign(row: dict) -> tuple[str, float]:
    stimulation = row.get("consensus_stimulation") == "True" or (row.get("is_stimulation") == "True" and row.get("is_inhibition") != "True")
    inhibition = row.get("consensus_inhibition") == "True" or (row.get("is_inhibition") == "True" and row.get("is_stimulation") != "True")
    if stimulation and not inhibition:
        return "activates", 1.0
    if inhibition and not stimulation:
        return "inhibits", -1.0
    return "binds", 0.0


DEFAULT_CURATED_EDGE_SIGN_OVERRIDES_PATH = Path("configs/curated_edge_sign_overrides.csv")


def load_curated_edge_sign_overrides(overrides_path: Path | None) -> dict[tuple[str, str], tuple[str, float]]:
    """Signs that the source annotates one way and the physiology requires the other way.

    Decision 9.10(a), the owner on 14 October 2026: "Go ahead with fixing the data for v4". The case the table was
    written for is the G-protein-coupled receptor kinases and the arrestins: OmniPath records is_stimulation=True
    for GRK and arrestin interactions with a receptor, which reads the interaction as positive regulation of the
    receptor, where phosphorylating a receptor's intracellular face uncouples it from its G protein. The propagation
    reads the sign as the effect on the destination's activity, so a desensitising enzyme has to arrive at -1.

    The table is keyed on the gene symbol pair and carries the sourced value as well as the corrected one, so a
    refresh of the source that changes what it annotates does not silently keep an override that no longer applies:
    an override whose sourced value no longer matches is reported by the caller and not applied.
    """
    if overrides_path is None or not Path(overrides_path).exists():
        return {}
    overrides: dict[tuple[str, str], tuple[str, float]] = {}
    with open(overrides_path, encoding="utf-8") as overrides_file:
        for row in csv.DictReader(overrides_file):
            overrides[(row["source_symbol"], row["target_symbol"])] = (row["relation_type_corrected"],
                                                                       float(row["sign_corrected"]),
                                                                       row["relation_type_as_sourced"],
                                                                       float(row["sign_as_sourced"]))
    return overrides


DEFAULT_ADMITTED_RECEPTOR_G_ALPHA_COUPLING_PATH = Path("configs/admitted_receptor_g_alpha_coupling.csv")
# The G alpha genes of each family, as HGNC groups them: 1426 "G protein subunits alpha, group s", 1428 "group i",
# 1427 "group q", 1429 "group 12/13" (data/raw/hgnc/hgnc_complete_set.txt, read 21 October 2026). Until then the set
# left out GNA14 and GNA15 of the q group and the transducins GNAT1 to GNAT3 of the i group, so no edge into them was
# filtered (decision 9.86). experiments/expand_receptor_g_alpha_families.py expands the admitted table over the same
# groups, and tests/test_receptor_g_alpha_coupling_filter.py holds this mapping to HGNC.
G_ALPHA_FAMILY_MEMBERS: dict[str, tuple[str, ...]] = {
    "Gs": ("GNAL", "GNAS"),
    "Gi/o": ("GNAI1", "GNAI2", "GNAI3", "GNAO1", "GNAT1", "GNAT2", "GNAT3", "GNAZ"),
    "Gq/11": ("GNA11", "GNA14", "GNA15", "GNAQ"),
    "G12/13": ("GNA12", "GNA13"),
}
G_ALPHA_GENE_SYMBOLS = frozenset(gene for members in G_ALPHA_FAMILY_MEMBERS.values() for gene in members)
# The transmembrane adenylyl cyclases, which Gs stimulates and Gi/o inhibits. ADCY10 is the soluble cyclase, regulated
# by bicarbonate and calcium rather than by G proteins, and is left out.
ADENYLYL_CYCLASE_SYMBOLS = frozenset(f"ADCY{number}" for number in range(1, 10))
# Decision 9.86 (the owner, 21 October 2026: "build the suggested change"). Each edge type carries its own learned
# gain in the linear-response encoder, so these separate what was one gain for every activates edge:
#   couples_primary / couples_secondary: an annotated receptor's admitted, positively signed edge into a G alpha of a
#     family GtoPdb lists as its primary or its secondary transducer. The two gains are learned apart, so the model
#     can learn how much a secondary coupling counts against a primary one without a fixed weight (9.20);
#   g_alpha_regulates_effector: a signed edge from any G alpha into a transmembrane adenylyl cyclase, with its sign
#     (+1 Gs, -1 Gi/o). One relation and one positive gain for both directions, so the balance at the cyclase comes
#     from the signs and is no longer the ratio of the activates and inhibits gains, which training sets from the
#     whole graph (measured on v5: an inhibits gain 1.36 times the activates gain would flip ADRB2's cAMP response).
COUPLES_PRIMARY_RELATION = "couples_primary"
COUPLES_SECONDARY_RELATION = "couples_secondary"
G_ALPHA_REGULATES_EFFECTOR_RELATION = "g_alpha_regulates_effector"
COUPLING_RELATIONS: tuple[str, ...] = (COUPLES_PRIMARY_RELATION, COUPLES_SECONDARY_RELATION, G_ALPHA_REGULATES_EFFECTOR_RELATION)


def load_admitted_receptor_g_alpha_coupling(coupling_path: Path | None) -> tuple[set[tuple[str, str]], set[str]]:
    """(admitted receptor-to-G-alpha pairs, the receptors the source annotates).

    Decision 9.23, the owner on 14 October 2026: "yes on the primary and secondary with dropping the 352 unlisted
    since it exactly reproduces the true EVIDENCED physiology". The table is GtoPdb's Primary and Secondary
    Transducer annotation as GPCRdb redistributes it, expanded from a G-protein family to its member genes.

    Two things the second return value is for. A receptor the source does not annotate keeps every edge, because
    absence from a curated sheet is not evidence against a coupling. And a source that is not a receptor at all -
    an RGS protein, a kinase, a transcription factor - is never filtered, since this rule is about which G alpha a
    receptor couples to and says nothing about what else regulates a G alpha (decision 9.27).
    """
    if coupling_path is None or not Path(coupling_path).exists():
        return set(), set()
    admitted_pairs: set[tuple[str, str]] = set()
    annotated_receptors: set[str] = set()
    with open(coupling_path, encoding="utf-8") as coupling_file:
        for row in csv.DictReader(coupling_file):
            receptor = row["receptor_gene_symbol"].strip().upper()
            g_alpha = row["g_alpha_gene_symbol"].strip().upper()
            admitted_pairs.add((receptor, g_alpha))
            annotated_receptors.add(receptor)
    return admitted_pairs, annotated_receptors


def receptor_g_alpha_edge_is_dropped(source_symbol: str, target_symbol: str, sign: float,
                                     admitted_pairs: set[tuple[str, str]], annotated_receptors: set[str]) -> bool:
    """True only for a signed edge from an annotated receptor into a G alpha that the annotation does not list."""
    if sign == 0.0 or not admitted_pairs:
        return False
    source_upper, target_upper = source_symbol.upper(), target_symbol.upper()
    if target_upper not in G_ALPHA_GENE_SYMBOLS or source_upper not in annotated_receptors:
        return False
    return (source_upper, target_upper) not in admitted_pairs


def load_receptor_g_alpha_transducer_roles(coupling_path: Path | None) -> dict[tuple[str, str], str]:
    """{(receptor, G alpha): "primary" or "secondary"} from the admitted table; primary wins where a pair is both."""
    if coupling_path is None or not Path(coupling_path).exists():
        return {}
    roles: dict[tuple[str, str], str] = {}
    with open(coupling_path, encoding="utf-8") as coupling_file:
        for row in csv.DictReader(coupling_file):
            pair = (row["receptor_gene_symbol"].strip().upper(), row["g_alpha_gene_symbol"].strip().upper())
            role = row["transducer_role"].strip().lower()
            if role not in ("primary", "secondary"):
                raise ValueError(f"{coupling_path}: transducer_role {role!r} for {pair} is neither primary nor secondary")
            if roles.get(pair) != "primary":
                roles[pair] = role
    return roles


def typed_coupling_relation(source_symbol: str, target_symbol: str, relation: str, sign: float,
                            transducer_role_of_pair: dict[tuple[str, str], str], annotated_receptors: set[str]) -> str:
    """The edge type of decision 9.86 for a signalling edge, or its relation unchanged.

    An annotated receptor's positively signed edge into an admitted G alpha becomes couples_primary or
    couples_secondary by the pair's transducer role; a signed edge from a G alpha into a transmembrane adenylyl cyclase
    becomes g_alpha_regulates_effector with its sign. An unsigned edge (binds) is never retyped, and neither is a
    receptor's negatively signed edge into a G alpha, which is not a coupling."""
    if sign == 0.0:
        return relation
    source_upper, target_upper = source_symbol.upper(), target_symbol.upper()
    if source_upper in G_ALPHA_GENE_SYMBOLS and target_upper in ADENYLYL_CYCLASE_SYMBOLS:
        return G_ALPHA_REGULATES_EFFECTOR_RELATION
    if sign > 0 and target_upper in G_ALPHA_GENE_SYMBOLS and source_upper in annotated_receptors:
        role = transducer_role_of_pair.get((source_upper, target_upper))
        if role == "primary":
            return COUPLES_PRIMARY_RELATION
        if role == "secondary":
            return COUPLES_SECONDARY_RELATION
    return relation


def add_gene_nodes(nodes: pd.DataFrame, symbols: set[str]) -> pd.DataFrame:
    existing = set(nodes.node_id)
    new_rows = [{"node_id": gene_node_id(symbol), "node_type": "gene", "display_name": symbol, "gene_symbol": symbol, "in_metabolic_layer": False, "degree": 0}
                for symbol in sorted(symbols) if gene_node_id(symbol) not in existing]
    return pd.concat([nodes, pd.DataFrame(new_rows)], ignore_index=True) if new_rows else nodes


def build_signaling_layer(nodes: pd.DataFrame, interactions_path: Path,
                          curated_sign_overrides: dict | None = None,
                          admitted_receptor_g_alpha_coupling: tuple[set, set] | None = None,
                          transducer_role_of_pair: dict[tuple[str, str], str] | None = None,
                          typed_coupling_relations: bool = False) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """curated_sign_overrides (decision 9.10(a), built 14 October 2026) corrects a sign the source states the other
    way round; load_curated_edge_sign_overrides documents why the GRK and arrestin edges need it. The third return
    value counts what was applied and what was skipped, so a build log records both.

    typed_coupling_relations (decision 9.86) gives receptor-to-G-alpha coupling and G-alpha-to-cyclase edges their own
    edge types (typed_coupling_relation); transducer_role_of_pair is load_receptor_g_alpha_transducer_roles. It is
    off here so a caller that names neither builds the layer it always built; build_physiology_graph turns it on.
    """
    overrides = curated_sign_overrides or {}
    admitted_pairs, annotated_receptors = admitted_receptor_g_alpha_coupling or (set(), set())
    edge_rows: list[dict] = []
    symbols: set[str] = set()
    override_counts = {"overrides_loaded": len(overrides), "edges_corrected": 0,
                       "overrides_skipped_because_the_source_no_longer_agrees": 0, "overrides_never_matched": 0,
                       "admitted_coupling_pairs_loaded": len(admitted_pairs),
                       "receptor_g_alpha_edges_dropped_as_unlisted": 0,
                       **{f"edges_typed_{name}": 0 for name in COUPLING_RELATIONS},
                       "receptor_g_alpha_edges_left_inhibits": 0}
    roles = transducer_role_of_pair or {}
    override_keys_that_matched: set[tuple[str, str]] = set()
    with open(interactions_path, encoding="utf-8") as interactions_file:
        for row in csv.DictReader(interactions_file, delimiter="\t"):
            relation, sign = interaction_sign(row)
            sources = expand_complex(row["source_genesymbol"])
            targets = expand_complex(row["target_genesymbol"])
            symbols.update(sources + targets)
            for source in sources:
                for target in targets:
                    if source == target:
                        continue
                    relation_for_this_edge, sign_for_this_edge = relation, sign
                    override = overrides.get((source, target))
                    if override is not None:
                        corrected_relation, corrected_sign, sourced_relation, sourced_sign = override
                        if (relation, sign) == (sourced_relation, sourced_sign):
                            relation_for_this_edge, sign_for_this_edge = corrected_relation, corrected_sign
                            override_counts["edges_corrected"] += 1
                            override_keys_that_matched.add((source, target))
                        else:
                            override_counts["overrides_skipped_because_the_source_no_longer_agrees"] += 1
                    if receptor_g_alpha_edge_is_dropped(source, target, sign_for_this_edge, admitted_pairs, annotated_receptors):
                        override_counts["receptor_g_alpha_edges_dropped_as_unlisted"] += 1
                        continue
                    if typed_coupling_relations:
                        typed = typed_coupling_relation(source, target, relation_for_this_edge, sign_for_this_edge, roles, annotated_receptors)
                        if typed != relation_for_this_edge:
                            override_counts[f"edges_typed_{typed}"] += 1
                            relation_for_this_edge = typed
                        elif (sign_for_this_edge < 0 and target.upper() in G_ALPHA_GENE_SYMBOLS and source.upper() in annotated_receptors):
                            override_counts["receptor_g_alpha_edges_left_inhibits"] += 1
                    edge_rows.append({"source_id": gene_node_id(source), "target_id": gene_node_id(target), "relation_type": relation_for_this_edge, "sign": sign_for_this_edge, "evidence_source": "OmniPath"})
                    if relation_for_this_edge == "binds":
                        edge_rows.append({"source_id": gene_node_id(target), "target_id": gene_node_id(source), "relation_type": relation_for_this_edge, "sign": sign_for_this_edge, "evidence_source": "OmniPath"})
    override_counts["overrides_never_matched"] = len(set(overrides) - override_keys_that_matched)
    return add_gene_nodes(nodes, symbols), pd.DataFrame(edge_rows).drop_duplicates(), override_counts


def build_transcription_layer(nodes: pd.DataFrame, regulons_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    edge_rows: list[dict] = []
    symbols: set[str] = set()
    with open(regulons_path, encoding="utf-8") as regulons_file:
        for row in csv.DictReader(regulons_file, delimiter="\t"):
            _, sign = interaction_sign(row)
            sources = expand_complex(row["source_genesymbol"])
            targets = expand_complex(row["target_genesymbol"])
            symbols.update(sources + targets)
            for source in sources:
                for target in targets:
                    if source != target:
                        edge_rows.append({"source_id": gene_node_id(source), "target_id": gene_node_id(target), "relation_type": "regulates_transcription_of", "sign": sign if sign != 0.0 else 1.0, "evidence_source": "CollecTRI"})
    return add_gene_nodes(nodes, symbols), pd.DataFrame(edge_rows).drop_duplicates()


def build_small_molecule_layer(nodes: pd.DataFrame, small_molecule_path: Path, metabolites_table_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    metabolites_by_pubchem: dict[str, list[str]] = defaultdict(list)
    with open(metabolites_table_path, encoding="utf-8") as metabolites_file:
        for row in csv.DictReader(metabolites_file, delimiter="\t"):
            pubchem_id = (row.get("metPubChemID") or "").strip()
            if pubchem_id:
                metabolites_by_pubchem[pubchem_id].append(row["mets"])
    known_nodes = set(nodes.node_id)
    edge_rows: list[dict] = []
    symbols: set[str] = set()
    with open(small_molecule_path, encoding="utf-8") as small_molecule_file:
        for row in csv.DictReader(small_molecule_file, delimiter="\t"):
            metabolite_instances = [instance for instance in metabolites_by_pubchem.get(row["source"], []) if instance in known_nodes]
            if not metabolite_instances:
                continue
            extracellular = [instance for instance in metabolite_instances if instance.endswith("e")]
            chosen_instances = extracellular or metabolite_instances
            relation, sign = interaction_sign(row)
            for target in expand_complex(row["target_genesymbol"]):
                symbols.add(target)
                for instance in chosen_instances:
                    edge_rows.append({"source_id": instance, "target_id": gene_node_id(target), "relation_type": relation if relation != "binds" else "binds", "sign": sign, "evidence_source": "OmniPath small_molecule_protein"})
    return add_gene_nodes(nodes, symbols), pd.DataFrame(edge_rows).drop_duplicates()


GTEX_BRAIN_TISSUE_PREFIX = "Brain_"


def load_brain_expression(gct_path: Path) -> pd.DataFrame:
    """Per-gene brain and whole-body expression from a GTEx median-TPM GCT file (design section 4.1, reference [30]).

    Returns one row per gene with ensembl_gene_id (version suffix removed), gene_symbol,
    brain_median_tpm_max (the largest median TPM over the brain tissues), brain_median_tpm_mean,
    body_median_tpm_max (the largest median TPM over every tissue of the file, brain included) and
    brain_tissue_count. GTEx v10 has 13 brain tissues; any column whose name starts with Brain_ counts.
    """
    table = pd.read_csv(gct_path, sep="\t", skiprows=2)
    tissue_columns = [column for column in table.columns if column not in ("Name", "Description")]
    brain_columns = [column for column in tissue_columns if column.startswith(GTEX_BRAIN_TISSUE_PREFIX)]
    if not brain_columns:
        raise ValueError(f"{gct_path} has no columns starting with {GTEX_BRAIN_TISSUE_PREFIX}")
    expression = pd.DataFrame({
        "ensembl_gene_id": table["Name"].astype(str).str.split(".").str[0],
        "gene_symbol": table["Description"].astype(str),
        "brain_median_tpm_max": table[brain_columns].max(axis=1).astype(float),
        "brain_median_tpm_mean": table[brain_columns].mean(axis=1).astype(float),
        "body_median_tpm_max": table[tissue_columns].max(axis=1).astype(float),
    })
    expression["brain_tissue_count"] = len(brain_columns)
    # a symbol can map to several Ensembl ids (and vice versa); keep the highest brain expression per key
    return expression.sort_values("brain_median_tpm_max", ascending=False)


def gene_node_values(nodes: pd.DataFrame, expression: pd.DataFrame, column: str) -> pd.Series:
    """expression[column] per gene node, matched by Ensembl id when the node has one and by symbol otherwise, indexed
    like nodes (missing outside the gene nodes and for a gene the table lacks)."""
    by_ensembl = expression.drop_duplicates("ensembl_gene_id").set_index("ensembl_gene_id")[column]
    by_symbol = expression.drop_duplicates("gene_symbol").set_index("gene_symbol")[column]
    gene_mask = nodes.node_type == "gene"
    ensembl_values = nodes.loc[gene_mask, "ensembl_gene_id"].map(by_ensembl) if "ensembl_gene_id" in nodes else pd.Series(index=nodes.index[gene_mask], dtype=float)
    symbol_values = nodes.loc[gene_mask, "gene_symbol"].map(by_symbol)
    values = pd.Series(pd.NA, index=nodes.index, dtype=object)
    values.loc[gene_mask] = ensembl_values.where(ensembl_values.notna(), symbol_values).values
    return pd.to_numeric(values, errors="coerce")


def annotate_brain_expression(nodes: pd.DataFrame, expression: pd.DataFrame, minimum_tpm: float) -> pd.DataFrame:
    """Add brain_median_tpm_max, body_median_tpm_max, brain_expression_known and brain_expressed to gene nodes.

    A gene node is matched by its Ensembl id when it has one (metabolic genes) and by symbol otherwise
    (signaling and transcription genes). brain_expressed is median TPM >= minimum_tpm in at least one
    brain tissue; it is False when the gene is known and below the threshold and also False when the
    gene is not in GTEx, with brain_expression_known separating the two cases. body_median_tpm_max is the
    largest median over every GTEx tissue, which the transcription gate reads (decision 9.76). Reaction nodes
    inherit the largest brain value over the genes that catalyze them, so a reaction's brain weight is available
    to readers.
    """
    nodes = nodes.copy()
    nodes["brain_median_tpm_max"] = gene_node_values(nodes, expression, "brain_median_tpm_max")
    if "body_median_tpm_max" in expression.columns:
        nodes["body_median_tpm_max"] = gene_node_values(nodes, expression, "body_median_tpm_max")
    nodes["brain_expression_known"] = nodes["brain_median_tpm_max"].notna()
    nodes["brain_expressed"] = nodes["brain_median_tpm_max"].fillna(-1.0) >= minimum_tpm
    return nodes


DETECTION_THRESHOLD_NCPM = 1.0  # the Human Protein Atlas detection threshold, the half-saturation of the cell-class weights
CELL_CLASS_NODE_COLUMNS = ("cell_class_ncpm_max", "cell_class_expression_known", "expression_below_detection")


def load_cell_class_expression(hpa_cluster_type_path: Path, gct_path: Path | None = None, geo_pineal_directory: Path | None = None,
                               siletti_aggregate_path: Path | None = None) -> tuple[pd.DataFrame, dict]:
    """(one row per gene with ensembl_gene_id, gene_symbol and cell_class_ncpm_max; a summary) from the Human Protein
    Atlas single-nucleus cluster types pooled into the brain classes, with the peripheral endocrine classes of
    peripheral_cell_classes and the atlas cluster classes of siletti_cluster_classes joined on when their sources are given. cell_class_ncpm_max is the largest raw value over
    the classes with a value, the quantity whose zero the weight builder turns into a weight of 0 in every class.

    The dopaminergic class the weight builder adds (atlas cluster 395) is not read here, since its count files are
    fetched only for the descriptors stage; cluster 395 belongs to the splatter supercluster, which the other_neuron
    class pools, so a gene at 0 there is at 0 in the dopaminergic class as well."""
    from mechanistic_pathway_learning.graph.brain_expression_descriptors import hpa_cell_class_table, read_zipped_table, unambiguous_symbol_to_ensembl
    from mechanistic_pathway_learning.graph.peripheral_cell_classes import add_peripheral_classes
    from mechanistic_pathway_learning.graph.siletti_cluster_classes import add_atlas_cluster_classes

    cluster_table = read_zipped_table(hpa_cluster_type_path)
    class_table, summary = add_peripheral_classes(hpa_cell_class_table(cluster_table), gct_path, geo_pineal_directory)
    class_table, summary["atlas_cluster_classes"] = add_atlas_cluster_classes(class_table, siletti_aggregate_path)
    symbol_to_ensembl = unambiguous_symbol_to_ensembl(cluster_table["Gene name"], cluster_table["Gene"])
    ensembl_to_symbol = {ensembl: symbol for symbol, ensembl in symbol_to_ensembl.items()}
    expression = pd.DataFrame({"ensembl_gene_id": class_table.index.astype(str),
                               "gene_symbol": [ensembl_to_symbol.get(ensembl, "") for ensembl in class_table.index.astype(str)],
                               "cell_class_ncpm_max": class_table.max(axis=1).to_numpy(dtype=float)})
    expression = expression[expression.cell_class_ncpm_max.notna()]
    summary.update({"classes_read": [column.removeprefix("class_") for column in class_table.columns], "genes_with_a_class_value": int(len(expression))})
    return expression.sort_values("cell_class_ncpm_max", ascending=False), summary


def annotate_cell_class_expression(nodes: pd.DataFrame, expression: pd.DataFrame, minimum_tpm: float,
                                   detection_threshold_ncpm: float = DETECTION_THRESHOLD_NCPM) -> pd.DataFrame:
    """Add cell_class_ncpm_max, cell_class_expression_known and expression_below_detection to gene nodes.

    expression_below_detection (decision 9.76) is True for a gene known in GTEx and below minimum_tpm in every brain
    tissue whose largest cell-class value is under detection_threshold_ncpm, or unknown: the sources the model's
    channels read show no class, brain or peripheral, where it is detected. A transcription edge whose factor carries
    the flag keeps its place in the graph and takes the lowered prior of configs/edge_prior_tiers.csv
    (graph/edge_evidence.py), so the data estimates its reliability rather than the build deciding it. The flag needs
    the brain expression columns, so annotate_brain_expression runs first."""
    nodes = nodes.copy()
    nodes["cell_class_ncpm_max"] = gene_node_values(nodes, expression, "cell_class_ncpm_max")
    nodes["cell_class_expression_known"] = nodes["cell_class_ncpm_max"].notna()
    brain_known = nodes["brain_expression_known"] if "brain_expression_known" in nodes.columns else pd.Series(False, index=nodes.index)
    brain_expressed = nodes["brain_expressed"] if "brain_expressed" in nodes.columns else pd.Series(False, index=nodes.index)
    below_detection_in_every_class = ~nodes["cell_class_expression_known"] | (nodes["cell_class_ncpm_max"].fillna(0.0) < detection_threshold_ncpm)
    nodes["expression_below_detection"] = brain_known.astype(bool) & ~brain_expressed.astype(bool) & below_detection_in_every_class
    return nodes


def propagate_brain_expression_to_reactions(nodes: pd.DataFrame, edges: pd.DataFrame) -> pd.DataFrame:
    """Reaction nodes take the largest brain_median_tpm_max over genes linked by catalyzed_by edges."""
    nodes = nodes.copy()
    catalysis = edges[edges.relation_type == "catalyzed_by"]
    gene_values = nodes.set_index("node_id")["brain_median_tpm_max"]
    gene_side = catalysis.target_id.where(catalysis.target_id.isin(gene_values.index), catalysis.source_id)
    reaction_side = catalysis.source_id.where(catalysis.target_id.isin(gene_values.index), catalysis.target_id)
    per_reaction = pd.DataFrame({"reaction": reaction_side.values, "value": gene_side.map(gene_values).values}).dropna().groupby("reaction")["value"].max()
    reaction_mask = nodes.node_type == "reaction"
    nodes.loc[reaction_mask, "brain_median_tpm_max"] = nodes.loc[reaction_mask, "node_id"].map(per_reaction).values
    nodes["brain_expression_known"] = nodes["brain_median_tpm_max"].notna()
    return nodes


def restrict_transcription_edges_to_expressed_factors(nodes: pd.DataFrame, edges: pd.DataFrame, minimum_tpm: float) -> tuple[pd.DataFrame, dict]:
    """Drop regulates_transcription_of edges whose factor the expression sources place nowhere (decision 9.76, the
    owner, 20 October 2026): the factor is known in the cell-class table at 0 in every class, brain and peripheral,
    **and** known in GTEx below minimum_tpm in every tissue of the body. A factor expressed anywhere keeps its
    regulon, and the limiting-step rule of the linear-response encoder attenuates it by the class weights; a factor
    absent from either table keeps it too, because absence from a table is a mapping gap rather than evidence of
    absence. Until 20 October 2026 the gate dropped every factor known below minimum_tpm in every brain tissue
    (design section 3.3), which lost 213 edges of 16 factors on the v5 build, among them PHOX2A (locus coeruleus),
    CRX (pineal) and TBX1, which bulk GTEx cannot see, and FOXE1, whose thyroid hormone reaches the brain; the counts
    of that rule are returned beside the new ones so a build summary records both.

    Returned counts: the edges before; the edges and factors the gate drops; the edges and factors the brain-TPM gate
    would have dropped, split into those now kept because a cell class expresses the factor, those kept because a
    tissue of the body does and those still dropped; the edges whose factor carries expression_below_detection (kept,
    with the lowered prior); and the edges whose factor is unknown to both tables."""
    by_id = nodes.set_index("node_id")
    is_transcription = edges.relation_type == "regulates_transcription_of"
    column = lambda name, default: edges.source_id.map(by_id[name]).fillna(default) if name in by_id.columns else pd.Series(default, index=edges.index)  # noqa: E731
    brain_known = column("brain_expression_known", False).astype(bool)
    brain_expressed = column("brain_expressed", False).astype(bool)
    body_known = column("body_median_tpm_max", float("nan")).notna()
    body_expressed = column("body_median_tpm_max", -1.0).astype(float) >= minimum_tpm
    class_known = column("cell_class_expression_known", False).astype(bool)
    class_max = column("cell_class_ncpm_max", float("nan")).astype(float)
    below_detection = column("expression_below_detection", False).astype(bool)
    brain_gate_would_drop = is_transcription & brain_known & ~brain_expressed
    dropped = is_transcription & class_known & (class_max == 0.0) & body_known & ~body_expressed
    kept_by_class = brain_gate_would_drop & ~dropped & class_known & (class_max > 0.0)
    kept_by_body = brain_gate_would_drop & ~dropped & ~kept_by_class & body_known & body_expressed
    kept_unknown_to_both = is_transcription & ~brain_known & ~class_known
    flagged = is_transcription & ~dropped & below_detection
    factors = lambda mask: int(edges.loc[mask, "source_id"].nunique())  # noqa: E731
    counts = {
        "transcription_edges_before": int(is_transcription.sum()),
        "transcription_edges_dropped_factor_unexpressed": int(dropped.sum()),
        "transcription_factors_dropped": factors(dropped),
        "transcription_edges_the_brain_tpm_gate_would_have_dropped": int(brain_gate_would_drop.sum()),
        "transcription_factors_the_brain_tpm_gate_would_have_dropped": factors(brain_gate_would_drop),
        "transcription_edges_kept_by_cell_class_expression": int(kept_by_class.sum()),
        "transcription_factors_kept_by_cell_class_expression": factors(kept_by_class),
        "transcription_edges_kept_by_body_expression": int(kept_by_body.sum()),
        "transcription_factors_kept_by_body_expression": factors(kept_by_body),
        "transcription_edges_factor_below_detection": int(flagged.sum()),
        "transcription_factors_below_detection": factors(flagged),
        "transcription_edges_kept_factor_expression_unknown": int(kept_unknown_to_both.sum()),
        "transcription_factors_expression_unknown": factors(kept_unknown_to_both),
    }
    return edges[~dropped].copy(), counts


def tag_currency(nodes: pd.DataFrame, degree_quantile_threshold: float) -> pd.DataFrame:
    """The degree rule over the metabolites, then the name rule over every metabolite (never a gene whose symbol spells
    a listed name: the fourth defect of tag_currency_metabolites).

    The second pass is what keeps a species' copies agreeing: a node added after this runs would otherwise carry
    whatever is_currency its adder wrote, which gave thirteen species copies that disagreed (defect 3 of
    tag_currency_metabolites). A build that adds nodes afterwards calls retag_currency_by_name again at the end."""
    metabolites = nodes[nodes.node_type == "metabolite"]
    tagged = tag_currency_metabolites(
        dict(zip(metabolites.node_id, metabolites.display_name)),
        dict(zip(metabolites.node_id, metabolites.degree)),
        degree_quantile_threshold=degree_quantile_threshold,
    )
    tagged = retag_currency_by_name(list(nodes.node_id), list(nodes.display_name), tagged, node_types=list(nodes.node_type))
    nodes = nodes.copy()
    nodes["is_currency"] = nodes.node_id.isin(tagged)
    return nodes


def largest_connected_component_fraction(nodes: pd.DataFrame, edges: pd.DataFrame, exclude_currency: bool) -> float:
    excluded = set(nodes.loc[nodes["is_currency"], "node_id"]) if exclude_currency and "is_currency" in nodes else set()
    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in zip(edges.source_id, edges.target_id):
        if source in excluded or target in excluded:
            continue
        adjacency[source].append(target)
        adjacency[target].append(source)
    all_nodes = [node_id for node_id in nodes.node_id if node_id not in excluded]
    seen: set[str] = set()
    largest = 0
    for start in all_nodes:
        if start in seen:
            continue
        queue = deque([start])
        seen.add(start)
        size = 0
        while queue:
            current = queue.popleft()
            size += 1
            for neighbor in adjacency.get(current, ()):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        largest = max(largest, size)
    return largest / max(1, len(all_nodes))


def summarize(nodes: pd.DataFrame, edges: pd.DataFrame) -> dict:
    metabolites = nodes[nodes.node_type == "metabolite"]
    reactions = nodes[nodes.node_type == "reaction"]
    genes = nodes[nodes.node_type == "gene"]
    return {
        "nodes_by_type": {key: int(value) for key, value in nodes.node_type.value_counts().items()},
        "gene_nodes_in_metabolic_layer": int(genes["in_metabolic_layer"].eq(True).sum()) if "in_metabolic_layer" in genes else 0,
        "edges_by_relation": {key: int(value) for key, value in edges.relation_type.value_counts().items()},
        "metabolites_by_compartment": {key: int(value) for key, value in metabolites.compartment.value_counts().items()},
        "currency_metabolites": int(metabolites.is_currency.sum()),
        "transport_reactions": int(reactions.is_transport.sum()),
        "reversible_reactions": int(reactions.reversible.sum()),
        "reactions_without_gene": int((reactions.gene_reaction_rule.fillna("") == "").sum()),
        "largest_component_fraction_all": largest_connected_component_fraction(nodes, edges, exclude_currency=False),
        "largest_component_fraction_without_currency": largest_connected_component_fraction(nodes, edges, exclude_currency=True),
    }


def build_physiology_graph(
    model_path: Path,
    output_directory: Path,
    genes_table_path: Path | None = None,
    degree_quantile_threshold: float = 0.995,
    signaling_interactions_path: Path | None = None,
    transcription_regulons_path: Path | None = None,
    small_molecule_path: Path | None = None,
    metabolites_table_path: Path | None = None,
    model_yaml_path: Path | None = None,
    brain_expression_path: Path | None = None,
    brain_expression_minimum_tpm: float = 1.0,
    curated_edge_sign_overrides_path: Path | None = DEFAULT_CURATED_EDGE_SIGN_OVERRIDES_PATH,
    admitted_receptor_g_alpha_coupling_path: Path | None = DEFAULT_ADMITTED_RECEPTOR_G_ALPHA_COUPLING_PATH,
    cell_class_expression_path: Path | None = None,
    geo_pineal_directory: Path | None = None,
    siletti_aggregate_path: Path | None = None,
    detection_threshold_ncpm: float = DETECTION_THRESHOLD_NCPM,
    typed_coupling_relations: bool = True,
) -> dict:
    model = load_human_gem(model_path)
    nodes, edges = build_metabolic_layer(model, gene_symbols_from_table(genes_table_path), model_yaml_path)
    edge_tables = [edges]
    if signaling_interactions_path is not None and signaling_interactions_path.exists():
        nodes, signaling_edges, sign_override_counts = build_signaling_layer(
            nodes, signaling_interactions_path,
            curated_sign_overrides=load_curated_edge_sign_overrides(curated_edge_sign_overrides_path),
            admitted_receptor_g_alpha_coupling=load_admitted_receptor_g_alpha_coupling(admitted_receptor_g_alpha_coupling_path),
            transducer_role_of_pair=load_receptor_g_alpha_transducer_roles(admitted_receptor_g_alpha_coupling_path),
            typed_coupling_relations=typed_coupling_relations)
        print(f"curated edge sign overrides: {sign_override_counts}")
        edge_tables.append(signaling_edges)
    if transcription_regulons_path is not None and transcription_regulons_path.exists():
        nodes, transcription_edges = build_transcription_layer(nodes, transcription_regulons_path)
        edge_tables.append(transcription_edges)
    if small_molecule_path is not None and small_molecule_path.exists() and metabolites_table_path is not None:
        nodes, small_molecule_edges = build_small_molecule_layer(nodes, small_molecule_path, metabolites_table_path)
        edge_tables.append(small_molecule_edges)
    edges = pd.concat(edge_tables, ignore_index=True).drop_duplicates()
    edges = edges[edges.source_id.isin(set(nodes.node_id)) & edges.target_id.isin(set(nodes.node_id))]
    brain_expression_counts: dict = {}
    if brain_expression_path is not None and brain_expression_path.exists():
        nodes = annotate_brain_expression(nodes, load_brain_expression(brain_expression_path), brain_expression_minimum_tpm)
        cell_class_summary = None
        if cell_class_expression_path is not None and cell_class_expression_path.exists():
            cell_class_expression, cell_class_summary = load_cell_class_expression(cell_class_expression_path, brain_expression_path, geo_pineal_directory, siletti_aggregate_path)
            nodes = annotate_cell_class_expression(nodes, cell_class_expression, brain_expression_minimum_tpm, detection_threshold_ncpm)
        else:
            print(f"no cell-class expression table at {cell_class_expression_path}: the transcription gate reads GTEx alone, so no factor is dropped "
                  "(a factor's class expression is unknown) and expression_below_detection follows the brain TPM threshold alone")
            nodes = annotate_cell_class_expression(nodes, pd.DataFrame(columns=["ensembl_gene_id", "gene_symbol", "cell_class_ncpm_max"]),
                                                   brain_expression_minimum_tpm, detection_threshold_ncpm)
        edges, brain_expression_counts = restrict_transcription_edges_to_expressed_factors(nodes, edges, brain_expression_minimum_tpm)
        nodes = propagate_brain_expression_to_reactions(nodes, edges)
        genes = nodes[nodes.node_type == "gene"]
        brain_expression_counts.update({
            "brain_expression_minimum_tpm": brain_expression_minimum_tpm,
            "cell_class_detection_threshold_ncpm": detection_threshold_ncpm,
            "gene_nodes_with_brain_expression_known": int(genes.brain_expression_known.sum()),
            "gene_nodes_brain_expressed": int(genes.brain_expressed.sum()),
            "gene_nodes_with_cell_class_expression_known": int(genes.cell_class_expression_known.sum()),
            "gene_nodes_expression_below_detection": int(genes.expression_below_detection.sum()),
            "cell_class_expression": cell_class_summary,
        })
        print(f"transcription gate: {brain_expression_counts}")
    degree = pd.concat([edges.source_id, edges.target_id]).value_counts()
    nodes = nodes.copy()
    nodes["degree"] = nodes.node_id.map(degree).fillna(0).astype(int)
    nodes = tag_currency(nodes, degree_quantile_threshold)
    output_directory.mkdir(parents=True, exist_ok=True)
    import os

    for name, table in (("nodes.parquet", nodes), ("edges.parquet", edges)):  # atomic replace so a concurrent reader never sees a partial file
        table.to_parquet(output_directory / (name + ".tmp"), index=False)
        os.replace(output_directory / (name + ".tmp"), output_directory / name)
    (output_directory / "relation_types.json").write_text(json.dumps(RELATION_TYPES))
    summary = summarize(nodes, edges)
    reactions = nodes[nodes.node_type == "reaction"]
    summary["reactions_with_subsystem"] = int((reactions.subsystem.fillna("") != "").sum())
    summary["distinct_subsystems"] = int(reactions.subsystem.fillna("").replace("", pd.NA).nunique())
    summary["brain_expression"] = brain_expression_counts
    # the sign overrides, the coupling filter and the coupling edge types, so the graph records what its build did
    summary["signaling_layer_counts"] = sign_override_counts if signaling_interactions_path is not None and signaling_interactions_path.exists() else {}
    (output_directory / "graph_summary.json").write_text(json.dumps(summary, indent=1))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model-path", type=Path, default=Path("data/raw/Human-GEM/model/Human-GEM.xml"))
    parser.add_argument("--genes-table", type=Path, default=Path("data/raw/Human-GEM/model/genes.tsv"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/graph"))
    parser.add_argument("--degree-quantile-threshold", type=float, default=0.995)
    parser.add_argument("--signaling", type=Path, default=Path("data/raw/omnipath/omnipath_interactions.tsv"))
    parser.add_argument("--transcription", type=Path, default=Path("data/raw/omnipath/collectri_interactions.tsv"))
    parser.add_argument("--small-molecule", type=Path, default=Path("data/raw/omnipath/small_molecule_protein.tsv"))
    parser.add_argument("--metabolites-table", type=Path, default=Path("data/raw/Human-GEM/model/metabolites.tsv"))
    parser.add_argument("--model-yaml", type=Path, default=Path("data/raw/Human-GEM/model/Human-GEM.yml"), help="source of reaction subsystems when the SBML has no groups")
    parser.add_argument("--brain-expression", type=Path, default=Path("data/raw/gtex/GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz"),
                        help="GTEx median-TPM GCT file; gene nodes get brain and whole-body expression attributes, and the transcription gate reads the body maximum")
    parser.add_argument("--brain-expression-minimum-tpm", type=float, default=1.0, help="median TPM in at least one brain tissue that counts as brain expression evidence; the same threshold over every tissue of the body in the transcription gate")
    parser.add_argument("--cell-class-expression", type=Path, default=Path("data/raw/hpa/rna_single_nuclei_cluster_type/rna_single_nuclei_cluster_type.tsv.zip"),
                        help="Human Protein Atlas single-nucleus cluster types, pooled into the brain cell classes; with --brain-expression, the transcription gate drops a factor's regulon only when the factor is at 0 in every class and below the TPM threshold in every tissue of the body (decision 9.76)")
    parser.add_argument("--geo-pineal-dir", type=Path, default=Path("data/raw/geo/GSE100472"),
                        help="GEO GSE100472 raw counts and NCBI annotation (owner-supplied; GEO refuses automated readers), the source of the pineal class; the thyroid, pancreatic islet and pituitary classes come from the GTEx file. Pass an absent path to build the classes without the pineal")
    parser.add_argument("--siletti-aggregate", type=Path, default=Path("data/raw/siletti_cluster_aggregate/adult_human_20221007_Pool_Clean.agg.loom"),
                        help="the adult human brain atlas's genes x clusters aggregate (Siletti et al. 2023), the source of the noradrenergic_neuron class (cluster 398); pass an absent path to build without it")
    parser.add_argument("--cell-class-detection-threshold-ncpm", type=float, default=DETECTION_THRESHOLD_NCPM,
                        help="a factor below the brain TPM threshold whose largest cell-class value is under this keeps its regulon with expression_below_detection set, which lowers its edges' prior (configs/edge_prior_tiers.csv)")
    parser.add_argument("--curated-edge-sign-overrides", type=Path, default=DEFAULT_CURATED_EDGE_SIGN_OVERRIDES_PATH,
                        help="signs the source annotates one way and the physiology requires the other way (decision 9.10a); pass an absent path to build without them")
    parser.add_argument("--admitted-receptor-g-alpha-coupling", type=Path, default=DEFAULT_ADMITTED_RECEPTOR_G_ALPHA_COUPLING_PATH,
                        help="GtoPdb primary and secondary transducers per receptor (decision 9.23); a signed edge from an annotated receptor into a G alpha the annotation does not list is dropped. Pass an absent path to keep every coupling edge")
    parser.add_argument("--no-typed-coupling-relations", dest="typed_coupling_relations", action="store_false",
                        help="leave receptor-to-G-alpha coupling and G-alpha-to-cyclase edges as activates and inhibits, the graph before decision 9.86, "
                             "for the ablation of the coupling edge types")
    arguments = parser.parse_args()
    summary = build_physiology_graph(arguments.model_path, arguments.output_dir, arguments.genes_table, arguments.degree_quantile_threshold,
                                     arguments.signaling, arguments.transcription, arguments.small_molecule, arguments.metabolites_table, arguments.model_yaml,
                                     arguments.brain_expression, arguments.brain_expression_minimum_tpm,
                                     arguments.curated_edge_sign_overrides,
                                     arguments.admitted_receptor_g_alpha_coupling,
                                     arguments.cell_class_expression, arguments.geo_pineal_dir, arguments.siletti_aggregate,
                                     arguments.cell_class_detection_threshold_ncpm, arguments.typed_coupling_relations)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
