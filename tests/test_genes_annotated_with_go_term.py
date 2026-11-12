"""The shared GO lookup behind the channel audit and amendment item 37's conductance edges."""
from __future__ import annotations

import gzip

import pandas as pd
import pytest

from mechanistic_pathway_learning.graph.protein_descriptors import (
    CHANNEL_ACTIVITY_OF_ION, ION_CHANNEL_ACTIVITY, genes_annotated_with_go_term, genes_annotated_with_go_terms,
    read_go_ancestors)

CHANNEL_ACTIVITY = ION_CHANNEL_ACTIVITY
VOLTAGE_GATED_POTASSIUM = "GO:0005249"  # a descendant of it
UNRELATED_TERM = "GO:0016787"


def write_ontology(directory):
    """A tiny OBO in which the voltage-gated potassium term is_a the channel term."""
    path = directory / "go-basic.obo"
    path.write_text(
        "[Term]\n"
        f"id: {CHANNEL_ACTIVITY}\n"
        "name: monoatomic ion channel activity\n\n"
        "[Term]\n"
        f"id: {VOLTAGE_GATED_POTASSIUM}\n"
        "name: voltage-gated potassium channel activity\n"
        f"is_a: {CHANNEL_ACTIVITY} ! monoatomic ion channel activity\n\n"
        "[Term]\n"
        f"id: {UNRELATED_TERM}\n"
        "name: hydrolase activity\n",
        encoding="utf-8")
    return path


def write_annotations(directory, rows):
    """A GAF holding the columns this lookup reads: 1 accession, 3 qualifier, 4 term, 8 aspect."""
    path = directory / "goa.gaf.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("!gaf-version: 2.2\n")
        for accession, qualifier, term, aspect in rows:
            fields = ["UniProtKB", accession, "SYM", qualifier, term, "REF", "IDA", "", aspect]
            handle.write("\t".join(fields) + "\n")
    return path


@pytest.fixture
def uniprot_table():
    return pd.DataFrame({"Entry": ["P1", "P2", "P3", "P4"],
                         "Gene Names (primary)": ["KCNQ2", "SCN1A", "SOMEHYDROLASE", "KCNA1;KCNA1B"]})


def test_a_descendant_term_answers_for_the_parent(tmp_path, uniprot_table):
    """A protein annotated voltage-gated potassium channel activity is a channel, though the row never names
    GO:0005216: the term is matched against the row's propagated ancestors."""
    annotations = write_annotations(tmp_path, [("P1", "enables", VOLTAGE_GATED_POTASSIUM, "F")])
    genes = genes_annotated_with_go_term(uniprot_table, annotations, read_go_ancestors(write_ontology(tmp_path)),
                                         CHANNEL_ACTIVITY)
    assert genes == {"KCNQ2"}


def test_a_not_qualified_row_does_not_make_the_protein_a_channel(tmp_path, uniprot_table):
    annotations = write_annotations(tmp_path, [("P2", "NOT|enables", CHANNEL_ACTIVITY, "F")])
    genes = genes_annotated_with_go_term(uniprot_table, annotations, read_go_ancestors(write_ontology(tmp_path)),
                                         CHANNEL_ACTIVITY)
    assert genes == set()


def test_only_the_molecular_function_aspect_is_read(tmp_path, uniprot_table):
    """Aspect C or P carrying the same term is not a statement that the protein has the activity."""
    annotations = write_annotations(tmp_path, [("P1", "enables", CHANNEL_ACTIVITY, "C"),
                                               ("P2", "involved_in", CHANNEL_ACTIVITY, "P")])
    genes = genes_annotated_with_go_term(uniprot_table, annotations, read_go_ancestors(write_ontology(tmp_path)),
                                         CHANNEL_ACTIVITY)
    assert genes == set()


def test_an_unrelated_term_is_not_a_channel(tmp_path, uniprot_table):
    annotations = write_annotations(tmp_path, [("P3", "enables", UNRELATED_TERM, "F")])
    genes = genes_annotated_with_go_term(uniprot_table, annotations, read_go_ancestors(write_ontology(tmp_path)),
                                         CHANNEL_ACTIVITY)
    assert genes == set()


def test_one_symbol_per_accession_the_first_the_table_names(tmp_path, uniprot_table):
    annotations = write_annotations(tmp_path, [("P4", "enables", CHANNEL_ACTIVITY, "F")])
    genes = genes_annotated_with_go_term(uniprot_table, annotations, read_go_ancestors(write_ontology(tmp_path)),
                                         CHANNEL_ACTIVITY)
    assert genes == {"KCNA1"}


def test_an_accession_the_uniprot_table_does_not_hold_is_skipped(tmp_path, uniprot_table):
    """The GAF covers more than the reviewed proteome, so a row whose accession has no reviewed entry is dropped
    rather than contributing an empty symbol."""
    annotations = write_annotations(tmp_path, [("P9", "enables", CHANNEL_ACTIVITY, "F")])
    genes = genes_annotated_with_go_term(uniprot_table, annotations, read_go_ancestors(write_ontology(tmp_path)),
                                         CHANNEL_ACTIVITY)
    assert genes == set()


def test_one_pass_over_several_terms_agrees_with_one_term_at_a_time(tmp_path, uniprot_table):
    """The pores build reads the root channel term and the four per-ion terms in one pass of the GAF (decision 9.129
    (2)); each term's set must be what the single-term reader gives, including the empty set for a term no row
    reaches."""
    annotations = write_annotations(tmp_path, [("P1", "enables", VOLTAGE_GATED_POTASSIUM, "F"),
                                               ("P3", "enables", UNRELATED_TERM, "F")])
    ancestors = read_go_ancestors(write_ontology(tmp_path))
    terms = [CHANNEL_ACTIVITY, VOLTAGE_GATED_POTASSIUM, UNRELATED_TERM, "GO:0005272"]
    together = genes_annotated_with_go_terms(uniprot_table, annotations, ancestors, terms)
    assert together == {term: genes_annotated_with_go_term(uniprot_table, annotations, ancestors, term) for term in terms}
    assert together[CHANNEL_ACTIVITY] == {"KCNQ2"} and together["GO:0005272"] == set()


def test_each_ion_names_its_own_channel_term():
    """The four terms decision 9.129 (2) ruled, keyed by the ion names graph/reactome_import.py uses for a pore."""
    assert CHANNEL_ACTIVITY_OF_ION == {"Na+": "GO:0005272", "K+": "GO:0005267", "Cl-": "GO:0005254",
                                       "Ca2+": "GO:0005262"}
