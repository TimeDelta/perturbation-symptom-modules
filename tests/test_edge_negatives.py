"""IntAct's curated non-interacting pairs against the graph's protein edges (mechanistic_pathway_learning/graph/edge_negatives.py)."""
from __future__ import annotations

import gzip

import pandas as pd
import pytest

from mechanistic_pathway_learning.graph.edge_negatives import (
    CANONICAL,
    ISOFORM,
    UNREVIEWED,
    NegativePair,
    audit,
    contradicted_edges,
    gene_pairs_between_whole_proteins,
    read_human_negative_pairs,
    read_reviewed_proteome,
    symbol_of_node,
)
from mechanistic_pathway_learning.graph.edge_evidence import edge_evidence_table

# UniProt's reviewed proteome as the tests need it: accession -> primary gene name
REVIEWED = {"P04637": "TP53", "Q00987": "MDM2", "Q07817": "BCL2L1", "Q92934": "BAD", "Q9Y616": "IRAK3", "O43187": "IRAK2", "Q9NWZ3": "IRAK4",
            "Q99836": "MYD88", "P12345": "AAA", "P23456": "BBB"}

HEADER = ["#ID(s) interactor A", "ID(s) interactor B", "Alt. ID(s) interactor A", "Alt. ID(s) interactor B", "Alias(es) interactor A", "Alias(es) interactor B",
          "Interaction detection method(s)", "Publication 1st author(s)", "Publication Identifier(s)", "Taxid interactor A", "Taxid interactor B",
          "Interaction type(s)", "Source database(s)", "Interaction identifier(s)", "Confidence value(s)"]


def mitab_row(acc_a: str, acc_b: str, gene_a: str, gene_b: str, taxid_b: str = "taxid:9606(human)|taxid:9606(Homo sapiens)") -> list[str]:
    return [f"uniprotkb:{acc_a}", f"uniprotkb:{acc_b}", "-", "-", f"psi-mi:x_human(display_long)|uniprotkb:{gene_a}(gene name)",
            f"psi-mi:y_human(display_long)|uniprotkb:{gene_b}(gene name)", 'psi-mi:"MI:0018"(two hybrid)', "Doe J (2020)", "pubmed:12345",
            "taxid:9606(human)|taxid:9606(Homo sapiens)", taxid_b, 'psi-mi:"MI:0915"(physical association)', 'psi-mi:"MI:0469"(IntAct)', "intact:EBI-1", "-"]


def write_mitab(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as mitab:
        mitab.write("\t".join(HEADER) + "\n")
        for row in rows:
            mitab.write("\t".join(row) + "\n")


def test_human_pairs_are_read_with_the_isoform_kept_and_other_species_left_out(tmp_path):
    path = tmp_path / "intact_negative.txt"
    write_mitab(path, [mitab_row("P04637-2", "Q00987", "TP53", "MDM2"), mitab_row("P12345", "P23456", "AAA", "BBB", taxid_b="taxid:10090(mouse)|taxid:10090(Mus musculus)")])
    pairs = read_human_negative_pairs(path, REVIEWED)
    assert [(pair.accession_a, pair.accession_b, pair.gene_a, pair.gene_b, pair.entry_kind_a, pair.entry_kind_b) for pair in pairs] == [
        ("P04637-2", "Q00987", "TP53", "MDM2", ISOFORM, CANONICAL)]
    assert pairs[0].publications == "pubmed:12345" and "physical association" in pairs[0].interaction_type
    assert not pairs[0].between_whole_proteins


def test_the_two_textbook_cases_are_isoform_records_and_contest_no_edge(tmp_path):
    """Decision 9.88: BCL2L1 isoform Q07817-2 with BAD and IRAK4's unreviewed entry F8VVZ1 with MYD88 (Yang et al. 2016)
    were read as gene-level absences of two well-established interactions. A record between two canonical entries
    still contests its gene pair."""
    path = tmp_path / "intact_negative.txt"
    write_mitab(path, [mitab_row("Q07817-2", "Q92934", "BCL2L1", "BAD"), mitab_row("F8VVZ1", "Q99836", "IRAK4", "MYD88"),
                       mitab_row("P04637", "Q00987", "TP53", "MDM2")])
    pairs = read_human_negative_pairs(path, REVIEWED)
    assert [(pair.entry_kind_a, pair.entry_kind_b) for pair in pairs] == [(ISOFORM, CANONICAL), (UNREVIEWED, CANONICAL), (CANONICAL, CANONICAL)]
    assert gene_pairs_between_whole_proteins(pairs) == {frozenset(("TP53", "MDM2"))}
    nodes = pd.DataFrame({"node_id": [f"PROTEIN:{gene}" for gene in ("BCL2L1", "BAD", "IRAK4", "MYD88", "TP53", "MDM2")], "node_type": ["protein"] * 6,
                          "gene_symbol": ["BCL2L1", "BAD", "IRAK4", "MYD88", "TP53", "MDM2"]})
    edges = pd.DataFrame({"source_id": ["PROTEIN:BAD", "PROTEIN:MYD88", "PROTEIN:MDM2"], "target_id": ["PROTEIN:BCL2L1", "PROTEIN:IRAK4", "PROTEIN:TP53"],
                          "relation_type": ["inhibits", "activates", "inhibits"], "sign": [-1.0, 1.0, -1.0], "evidence_source": ["OmniPath"] * 3})
    contradicted = contradicted_edges(pairs, edges, nodes)
    assert contradicted.source_id.tolist() == ["PROTEIN:MDM2"]
    assert (contradicted.intact_accession_a.iloc[0], contradicted.intact_accession_b.iloc[0]) == ("P04637", "Q00987")
    evidence = edge_evidence_table(edges, pd.DataFrame(), gene_pairs_between_whole_proteins(pairs))
    assert evidence.contested.tolist() == [False, False, True]


def test_a_canonical_end_takes_uniprots_gene_name_and_an_unreviewed_end_keeps_intacts(tmp_path):
    path = tmp_path / "intact_negative.txt"
    write_mitab(path, [mitab_row("P04637", "A0A0S2Z3D2", "p53_alias", "BCL2L1")])
    pair = read_human_negative_pairs(path, REVIEWED)[0]
    assert (pair.gene_a, pair.gene_b) == ("TP53", "BCL2L1") and (pair.entry_kind_a, pair.entry_kind_b) == (CANONICAL, UNREVIEWED)


def test_an_interactor_without_a_uniprotkb_identifier_is_not_read(tmp_path):
    path = tmp_path / "intact_negative.txt"
    row = mitab_row("P04637", "Q00987", "TP53", "MDM2")
    row[1] = "intact:EBI-7424890"
    write_mitab(path, [row])
    assert read_human_negative_pairs(path, REVIEWED) == []


def test_reading_without_the_reviewed_proteome_is_refused(tmp_path):
    """Without the proteome an unreviewed entry such as F8VVZ1 cannot be told from a canonical one, which is the error
    decision 9.88 corrects, so the reader does not guess."""
    path = tmp_path / "intact_negative.txt"
    write_mitab(path, [mitab_row("P04637", "Q00987", "TP53", "MDM2")])
    with pytest.raises(ValueError):
        read_human_negative_pairs(path, {})


def test_the_reviewed_proteome_is_read_from_uniprots_tsv(tmp_path):
    path = tmp_path / "uniprot_human_reviewed.tsv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("Entry\tGene Names (primary)\tHGNC\nP04637\tTP53\tHGNC:11998;\nQ8N7X0\t\t\n")
    assert read_reviewed_proteome(path) == {"P04637": "TP53", "Q8N7X0": ""}


def test_contradicted_edges_are_found_in_either_direction_on_gene_or_protein_nodes():
    pairs = [NegativePair("P1", "P2", "TP53", "MDM2", "physical association", "two hybrid", "pubmed:1")]
    nodes = pd.DataFrame({"node_id": ["GENE:TP53", "PROTEIN:MDM2", "GENE:BRCA1", "MAM1c"], "node_type": ["gene", "protein", "gene", "metabolite"],
                          "gene_symbol": ["TP53", "MDM2", "BRCA1", None]})
    edges = pd.DataFrame({"source_id": ["PROTEIN:MDM2", "GENE:BRCA1", "GENE:TP53"], "target_id": ["GENE:TP53", "GENE:TP53", "MAM1c"],
                          "relation_type": ["inhibits", "binds", "substrate_of"], "sign": [-1.0, 0.0, 1.0], "evidence_source": ["OmniPath", "OmniPath", "Human-GEM"]})
    contradicted = contradicted_edges(pairs, edges, nodes)
    assert contradicted.source_id.tolist() == ["PROTEIN:MDM2"] and contradicted.intact_publications.iloc[0] == "pubmed:1"
    assert symbol_of_node(nodes) == {"GENE:TP53": "TP53", "PROTEIN:MDM2": "MDM2", "GENE:BRCA1": "BRCA1"}


def test_the_audit_judges_a_source_on_the_pairs_the_anchor_set_names():
    pairs = [NegativePair("P1", "P2", "TP53", "MDM2", "physical association", "two hybrid", "pubmed:1"),
             NegativePair("P3", "P4", "AKT1", "BRCA1", "direct interaction", "pull down", "pubmed:2")]
    nodes = pd.DataFrame({"node_id": ["GENE:TP53", "GENE:MDM2", "GENE:BRCA1", "GENE:AKT1", "GENE:EGFR"], "node_type": ["gene"] * 5,
                          "gene_symbol": ["TP53", "MDM2", "BRCA1", "AKT1", "EGFR"]})
    edges = pd.DataFrame({"source_id": ["GENE:MDM2", "GENE:TP53", "GENE:EGFR", "GENE:AKT1"], "target_id": ["GENE:TP53", "GENE:BRCA1", "GENE:AKT1", "GENE:BRCA1"],
                          "relation_type": ["inhibits", "binds", "activates", "binds"], "sign": [-1.0, 0.0, 1.0, 0.0],
                          "evidence_source": ["OmniPath", "OmniPath", "OmniPath", "CollecTRI"]})
    result = audit(pairs, edges, nodes)
    # OmniPath: three edges, two join proteins the set names (MDM2-TP53, TP53-BRCA1); one is a negative pair (MDM2-TP53); EGFR is unnamed
    assert result["by_source"]["OmniPath"] == {"edges_on_named_proteins": 2, "edges_on_a_negative_pair": 1}
    assert result["by_source"]["CollecTRI"] == {"edges_on_named_proteins": 1, "edges_on_a_negative_pair": 1}
    assert result["human_negative_records"] == 2 and result["records_between_whole_proteins"] == 2 and result["proteins_named"] == 4
    assert result["gene_pairs_between_whole_proteins"] == 2 and result["edges_on_a_negative_pair"] == 2


def test_the_audit_counts_isoform_records_apart_and_judges_sources_on_whole_proteins_only():
    pairs = [NegativePair("P1", "P2", "TP53", "MDM2", "physical association", "two hybrid", "pubmed:1"),
             NegativePair("Q07817-2", "Q92934", "BCL2L1", "BAD", "physical association", "two hybrid array", "pubmed:26871637", ISOFORM, CANONICAL),
             NegativePair("F8VVZ1", "Q99836", "IRAK4", "MYD88", "physical association", "two hybrid array", "pubmed:26871637", UNREVIEWED, CANONICAL)]
    nodes = pd.DataFrame({"node_id": ["GENE:TP53", "GENE:MDM2", "GENE:BCL2L1", "GENE:BAD"], "node_type": ["gene"] * 4, "gene_symbol": ["TP53", "MDM2", "BCL2L1", "BAD"]})
    edges = pd.DataFrame({"source_id": ["GENE:MDM2", "GENE:BAD"], "target_id": ["GENE:TP53", "GENE:BCL2L1"], "relation_type": ["inhibits", "inhibits"],
                          "sign": [-1.0, -1.0], "evidence_source": ["OmniPath", "OmniPath"]})
    result = audit(pairs, edges, nodes)
    assert result["human_negative_records"] == 3 and result["records_between_whole_proteins"] == 1
    assert result["records_set_aside_by_entry_kinds"] == {"canonical+isoform": 1, "canonical+unreviewed": 1}
    assert result["by_source"]["OmniPath"] == {"edges_on_named_proteins": 1, "edges_on_a_negative_pair": 1}
