"""Decision 9.23, the owner on 14 October 2026: "yes on the primary and secondary with dropping the 352 unlisted
since it exactly reproduces the true EVIDENCED physiology".

The three cases that matter are kept apart deliberately: an annotated receptor's unlisted coupling is dropped, an
unannotated receptor keeps everything because absence from a curated sheet is not evidence against, and a source
that is not a receptor is never touched, since this rule says nothing about what else regulates a G alpha
(decision 9.27, where the nine RGS and AGS edges were checked and found correctly signed).
"""
import csv
from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.build_physiology_graph import (
    build_signaling_layer,
    load_admitted_receptor_g_alpha_coupling,
    receptor_g_alpha_edge_is_dropped,
)

ADMITTED_COUPLING_PATH = Path("configs/admitted_receptor_g_alpha_coupling.csv")


def test_the_admitted_table_holds_primary_and_secondary_and_expands_families_to_genes():
    admitted_pairs, annotated_receptors = load_admitted_receptor_g_alpha_coupling(ADMITTED_COUPLING_PATH)
    assert admitted_pairs, "the admitted coupling table is empty"
    # HTR1A is primary Gi/o with no secondary, so every Gi/o member is admitted and no Gs or Gq member is
    assert ("HTR1A", "GNAI1") in admitted_pairs
    assert ("HTR1A", "GNAO1") in admitted_pairs
    assert ("HTR1A", "GNAS") not in admitted_pairs
    assert ("HTR1A", "GNAQ") not in admitted_pairs
    # ADRB2 is primary Gs with secondary Gi/o, so both families are admitted
    assert ("ADRB2", "GNAS") in admitted_pairs
    assert ("ADRB2", "GNAI1") in admitted_pairs
    assert "HTR1A" in annotated_receptors and "ADRB2" in annotated_receptors


def test_only_an_annotated_receptors_unlisted_coupling_is_dropped():
    admitted_pairs, annotated_receptors = load_admitted_receptor_g_alpha_coupling(ADMITTED_COUPLING_PATH)
    # an annotated receptor reaching a G alpha the annotation does not list
    assert receptor_g_alpha_edge_is_dropped("HTR1A", "GNAS", 1.0, admitted_pairs, annotated_receptors)
    # the same receptor reaching its own primary family
    assert not receptor_g_alpha_edge_is_dropped("HTR1A", "GNAI1", 1.0, admitted_pairs, annotated_receptors)
    # a secondary coupling survives
    assert not receptor_g_alpha_edge_is_dropped("ADRB2", "GNAI1", 1.0, admitted_pairs, annotated_receptors)
    # a source that is not a receptor is never filtered, however implausible it looks
    assert not receptor_g_alpha_edge_is_dropped("RGS4", "GNAS", -1.0, admitted_pairs, annotated_receptors)
    assert not receptor_g_alpha_edge_is_dropped("PRKACA", "GNAS", 1.0, admitted_pairs, annotated_receptors)
    assert not receptor_g_alpha_edge_is_dropped("MYC", "GNAQ", 1.0, admitted_pairs, annotated_receptors)
    # an unsigned edge is left alone, and a target that is not a G alpha is left alone
    assert not receptor_g_alpha_edge_is_dropped("HTR1A", "GNAS", 0.0, admitted_pairs, annotated_receptors)
    assert not receptor_g_alpha_edge_is_dropped("HTR1A", "MAPK1", 1.0, admitted_pairs, annotated_receptors)


def test_the_filter_drops_the_unlisted_edge_in_the_built_layer(tmp_path):
    interactions_path = tmp_path / "interactions.tsv"
    with open(interactions_path, "w", newline="", encoding="utf-8") as interactions_file:
        writer = csv.DictWriter(interactions_file, delimiter="\t",
                                fieldnames=["source_genesymbol", "target_genesymbol", "is_stimulation",
                                            "is_inhibition", "consensus_stimulation", "consensus_inhibition"])
        writer.writeheader()
        for source_symbol, target_symbol in (("HTR1A", "GNAI1"), ("HTR1A", "GNAS"), ("RGS4", "GNAS")):
            writer.writerow({"source_genesymbol": source_symbol, "target_genesymbol": target_symbol,
                             "is_stimulation": "True", "is_inhibition": "False",
                             "consensus_stimulation": "True", "consensus_inhibition": "False"})
    nodes = pd.DataFrame([{"node_id": "GENE:HTR1A", "node_type": "gene", "gene_symbol": "HTR1A"}])
    coupling = load_admitted_receptor_g_alpha_coupling(ADMITTED_COUPLING_PATH)

    _, edges, counts = build_signaling_layer(nodes, interactions_path, admitted_receptor_g_alpha_coupling=coupling)

    kept = {(row.source_id, row.target_id) for row in edges.itertuples()}
    assert ("GENE:HTR1A", "GENE:GNAI1") in kept, "the primary coupling must survive"
    assert ("GENE:HTR1A", "GENE:GNAS") not in kept, "the unlisted coupling must be dropped"
    assert ("GENE:RGS4", "GENE:GNAS") in kept, "a non-receptor source must not be filtered"
    assert counts["receptor_g_alpha_edges_dropped_as_unlisted"] == 1


def test_an_absent_table_keeps_every_coupling_edge(tmp_path):
    admitted_pairs, annotated_receptors = load_admitted_receptor_g_alpha_coupling(tmp_path / "missing.csv")
    assert (admitted_pairs, annotated_receptors) == (set(), set())
    assert not receptor_g_alpha_edge_is_dropped("HTR1A", "GNAS", 1.0, admitted_pairs, annotated_receptors)


# --- decision 9.77 (the owner, 21 October 2026: "build the suggested change") ---------------------------------------

import pytest  # noqa: E402

from mechanistic_pathway_learning.graph.build_physiology_graph import (  # noqa: E402
    ADENYLYL_CYCLASE_SYMBOLS,
    COUPLES_PRIMARY_RELATION,
    COUPLES_SECONDARY_RELATION,
    G_ALPHA_FAMILY_MEMBERS,
    G_ALPHA_GENE_SYMBOLS,
    G_ALPHA_REGULATES_EFFECTOR_RELATION,
    RELATION_TYPES,
    load_receptor_g_alpha_transducer_roles,
    typed_coupling_relation,
)

HGNC_PATH = Path("data/raw/hgnc/hgnc_complete_set.txt")


def test_the_filter_covers_every_g_alpha_gene_of_the_four_families():
    """GNA14, GNA15 and the transducins were outside the set until 9.77, so no edge into them was filtered."""
    for gene in ("GNA14", "GNA15", "GNAT1", "GNAT2", "GNAT3"):
        assert gene in G_ALPHA_GENE_SYMBOLS
    assert set(G_ALPHA_FAMILY_MEMBERS["Gq/11"]) == {"GNAQ", "GNA11", "GNA14", "GNA15"}


@pytest.mark.skipif(not HGNC_PATH.exists(), reason="the HGNC table is a raw download (scripts/fetch_raw_sources.sh)")
def test_the_family_members_are_hgnc_s_gene_groups_and_the_table_is_their_expansion():
    import importlib.util
    spec = importlib.util.spec_from_file_location("expand_receptor_g_alpha_families", Path("experiments/expand_receptor_g_alpha_families.py"))
    expander = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(expander)
    members = expander.members_from_hgnc(HGNC_PATH)
    assert {family: tuple(genes) for family, genes in members.items()} == {family: tuple(sorted(genes)) for family, genes in G_ALPHA_FAMILY_MEMBERS.items()}
    table = pd.read_csv(ADMITTED_COUPLING_PATH, dtype=str, keep_default_na=False)
    assert expander.as_csv_text(expander.expanded_table(table, members)) == ADMITTED_COUPLING_PATH.read_text(encoding="utf-8")


def test_the_unlisted_gq_family_coupling_of_a_gs_receptor_is_now_dropped():
    admitted_pairs, annotated_receptors = load_admitted_receptor_g_alpha_coupling(ADMITTED_COUPLING_PATH)
    # ADRB2 is primary Gs with secondary Gi/o: no Gq/11 member is admitted, GNA14 included
    assert receptor_g_alpha_edge_is_dropped("ADRB2", "GNA14", 1.0, admitted_pairs, annotated_receptors)
    # a Gq/11-annotated receptor keeps its GNA14 and GNA15 edges under the family rule
    assert not receptor_g_alpha_edge_is_dropped("HRH1", "GNA14", 1.0, admitted_pairs, annotated_receptors)
    assert not receptor_g_alpha_edge_is_dropped("HRH1", "GNA15", 1.0, admitted_pairs, annotated_receptors)
    # rhodopsin is not in the table, so absence keeps its transducin edge
    assert not receptor_g_alpha_edge_is_dropped("RHO", "GNAT1", 1.0, admitted_pairs, annotated_receptors)


def test_the_coupling_edge_types_are_appended_after_every_existing_relation():
    assert RELATION_TYPES[-3:] == [COUPLES_PRIMARY_RELATION, COUPLES_SECONDARY_RELATION, G_ALPHA_REGULATES_EFFECTOR_RELATION]
    assert RELATION_TYPES.index("targets") == 7, "an existing relation moved, which would change the encoder's relation indices"


def test_each_edge_is_typed_by_its_role_and_only_signed_couplings_are_retyped():
    roles = load_receptor_g_alpha_transducer_roles(ADMITTED_COUPLING_PATH)
    _, annotated_receptors = load_admitted_receptor_g_alpha_coupling(ADMITTED_COUPLING_PATH)
    assert typed_coupling_relation("ADRB2", "GNAS", "activates", 1.0, roles, annotated_receptors) == COUPLES_PRIMARY_RELATION
    assert typed_coupling_relation("ADRB2", "GNAI1", "activates", 1.0, roles, annotated_receptors) == COUPLES_SECONDARY_RELATION
    assert typed_coupling_relation("GNAS", "ADCY5", "activates", 1.0, roles, annotated_receptors) == G_ALPHA_REGULATES_EFFECTOR_RELATION
    assert typed_coupling_relation("GNAI1", "ADCY5", "inhibits", -1.0, roles, annotated_receptors) == G_ALPHA_REGULATES_EFFECTOR_RELATION
    assert typed_coupling_relation("GNAS", "ADCY5", "binds", 0.0, roles, annotated_receptors) == "binds", "an unsigned edge keeps binds"
    assert typed_coupling_relation("ADRB2", "GNAS", "inhibits", -1.0, roles, annotated_receptors) == "inhibits", "a negative edge is not a coupling"
    assert typed_coupling_relation("RGS4", "GNAS", "inhibits", -1.0, roles, annotated_receptors) == "inhibits", "a regulator is not a receptor"
    assert typed_coupling_relation("RHO", "GNAT1", "activates", 1.0, roles, annotated_receptors) == "activates", "an unannotated receptor keeps activates"
    assert typed_coupling_relation("GNAQ", "PLCB1", "activates", 1.0, roles, annotated_receptors) == "activates", "only the cyclases are effectors here"
    assert "ADCY10" not in ADENYLYL_CYCLASE_SYMBOLS, "the soluble cyclase is not regulated by G proteins"


def test_the_built_layer_types_the_edges_and_counts_them(tmp_path):
    interactions_path = tmp_path / "interactions.tsv"
    rows = [("ADRB2", "GNAS", "True", "False"), ("ADRB2", "GNAI1", "True", "False"), ("ADRB2", "GNA14", "True", "False"),
            ("GNAS", "ADCY5", "True", "False"), ("GNAI1", "ADCY5", "False", "True"), ("RGS4", "GNAS", "False", "True")]
    with open(interactions_path, "w", newline="", encoding="utf-8") as interactions_file:
        writer = csv.DictWriter(interactions_file, delimiter="\t",
                                fieldnames=["source_genesymbol", "target_genesymbol", "is_stimulation",
                                            "is_inhibition", "consensus_stimulation", "consensus_inhibition"])
        writer.writeheader()
        for source_symbol, target_symbol, stimulation, inhibition in rows:
            writer.writerow({"source_genesymbol": source_symbol, "target_genesymbol": target_symbol, "is_stimulation": stimulation,
                             "is_inhibition": inhibition, "consensus_stimulation": stimulation, "consensus_inhibition": inhibition})
    nodes = pd.DataFrame([{"node_id": "GENE:ADRB2", "node_type": "gene", "gene_symbol": "ADRB2"}])
    coupling = load_admitted_receptor_g_alpha_coupling(ADMITTED_COUPLING_PATH)
    roles = load_receptor_g_alpha_transducer_roles(ADMITTED_COUPLING_PATH)

    _, typed_edges, counts = build_signaling_layer(nodes, interactions_path, admitted_receptor_g_alpha_coupling=coupling,
                                                   transducer_role_of_pair=roles, typed_coupling_relations=True)
    _, untyped_edges, _ = build_signaling_layer(nodes, interactions_path, admitted_receptor_g_alpha_coupling=coupling)

    relation_of = {(row.source_id, row.target_id): (row.relation_type, row.sign) for row in typed_edges.itertuples()}
    assert relation_of[("GENE:ADRB2", "GENE:GNAS")] == (COUPLES_PRIMARY_RELATION, 1.0)
    assert relation_of[("GENE:ADRB2", "GENE:GNAI1")] == (COUPLES_SECONDARY_RELATION, 1.0)
    assert relation_of[("GENE:GNAS", "GENE:ADCY5")] == (G_ALPHA_REGULATES_EFFECTOR_RELATION, 1.0)
    assert relation_of[("GENE:GNAI1", "GENE:ADCY5")] == (G_ALPHA_REGULATES_EFFECTOR_RELATION, -1.0)
    assert relation_of[("GENE:RGS4", "GENE:GNAS")] == ("inhibits", -1.0)
    assert ("GENE:ADRB2", "GENE:GNA14") not in relation_of, "ADRB2's unlisted Gq-family coupling is dropped"
    assert counts["receptor_g_alpha_edges_dropped_as_unlisted"] == 1
    assert counts[f"edges_typed_{COUPLES_PRIMARY_RELATION}"] == 1 and counts[f"edges_typed_{COUPLES_SECONDARY_RELATION}"] == 1
    assert counts[f"edges_typed_{G_ALPHA_REGULATES_EFFECTOR_RELATION}"] == 2
    # off, the same edges keep activates and inhibits: the ablation is the graph before 9.77, the filter fix aside
    assert set(untyped_edges.relation_type) <= {"activates", "inhibits"}
    assert len(untyped_edges) == len(typed_edges)
