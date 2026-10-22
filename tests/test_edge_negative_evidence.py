"""Negative and positive edge observations from Negatome, HuRI, Perturb-seq, ChEMBL and GO NOT annotations, and the
likelihood ratios the edge prior takes them with (decision 9.91; graph/edge_negative_evidence.py and the source modules)."""
from __future__ import annotations

import csv
import gzip
import math
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from experiments.run_main_model import (
    ARGUMENTS_RECORDED_ONLY_WHEN_SET,
    EDGE_EVIDENCE_FILE,
    EDGE_NEGATIVE_EVIDENCE_SETTINGS,
    EDGE_PRIOR_SETTINGS,
    build_argument_parser,
    build_edge_priors,
    configuration_fingerprint,
)
from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data
from mechanistic_pathway_learning.graph import chembl_activity_negatives as chembl
from mechanistic_pathway_learning.graph import go_not_annotations as go_not
from mechanistic_pathway_learning.graph import huri_tested_space as huri
from mechanistic_pathway_learning.graph import negatome_negatives as negatome
from mechanistic_pathway_learning.graph import perturbseq_responses as perturbseq
from mechanistic_pathway_learning.graph.edge_evidence import edge_priors, read_edge_tiers
from mechanistic_pathway_learning.graph.edge_negative_evidence import (
    DEFAULT_LIKELIHOOD_RATIOS_PATH,
    PUBLISHED,
    SOURCES,
    apply_likelihood_ratios,
    derived_likelihood_ratios,
    log_likelihood_ratio,
    read_likelihood_ratios,
    summarise_negative_evidence,
)
from mechanistic_pathway_learning.graph.edge_negative_sources import NegativeEvidencePaths, assemble_negative_evidence
from tests.test_edge_priors_in_the_trainer import TIERS, write_edge_evidence
from tests.test_soft_priors_in_the_trainer import write_toy_dataset

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------------------------------------------------
# the likelihood ratios


def test_the_committed_ratio_table_is_the_arithmetic_on_the_published_numbers():
    ratios = read_likelihood_ratios(REPOSITORY_ROOT / DEFAULT_LIKELIHOOD_RATIOS_PATH)
    derived = derived_likelihood_ratios()
    assert set(ratios) == set(derived), "one row per source and kind the published numbers give"
    for key, (present, absent) in derived.items():
        ratio = ratios[key]
        if present is None:
            assert not ratio.measured and ratio.ratio == 1.0, f"{key}: no published measurement, so no effect"
            continue
        assert math.isclose(ratio.probability_given_present, present, rel_tol=1e-8) and math.isclose(ratio.probability_given_absent, absent, rel_tol=1e-8)
        assert (ratio.ratio < 1.0) == (key[1] == "negative"), f"{key}: a negative report lowers the odds and a positive one raises them"
        assert ratio.quote and ratio.reference, f"{key}: every measured ratio carries its quote and its source"


def test_the_published_numbers_give_the_ratios_the_record_states():
    ratios = {key: (present / absent if present is not None else None) for key, (present, absent) in derived_likelihood_ratios().items()}
    assert math.isclose(ratios[("negatome", "negative")], 0.08 / 0.92)
    assert math.isclose(ratios[("huri", "negative")], (1 - 0.02 / 0.81) / (1 - 9 * 8e-6))
    assert math.isclose(ratios[("huri", "positive")], (0.02 / 0.81) / (9 * 8e-6))
    unbound = (0.079 / 1.02 - 0.854 * 0.079) / 0.146
    assert math.isclose(ratios[("perturbseq", "negative")], 0.921 / (1 - unbound)) and 0.921 < ratios[("perturbseq", "negative")] < 1.0
    error = (1 - math.sqrt(0.40)) / 2
    assert math.isclose(ratios[("chembl", "negative")], error / (1 - error)) and math.isclose(ratios[("chembl", "positive")], (1 - error) / error)
    # two exchangeable assays erring with probability e whatever the truth agree with kappa at most (1 - 2e)^2, reached at even prevalence
    for prevalence in (0.1, 0.3, 0.5, 0.8):
        covariance = prevalence * (1 - prevalence) * (1 - 2 * error) ** 2
        kappa = covariance / (covariance + error * (1 - error))
        assert kappa <= PUBLISHED["chembl_kappa_at_10_um"] + 1e-12
    assert math.isclose(0.25 * (1 - 2 * error) ** 2 / (0.25 * (1 - 2 * error) ** 2 + error * (1 - error)), 0.40)


def test_a_table_whose_stated_ratio_disagrees_with_its_probabilities_is_refused(tmp_path):
    path = tmp_path / "ratios.csv"
    path.write_text("source,report,applies_to_relations,probability_given_present,probability_given_absent,likelihood_ratio,basis,quote,reference\n"
                    "huri,negative,binds,0.9,0.99,0.5,,,\n")
    with pytest.raises(ValueError, match="states a ratio"):
        read_likelihood_ratios(path)


def ratio_table(path: Path, relation: str = "binds") -> Path:
    path.write_text("source,report,applies_to_relations,probability_given_present,probability_given_absent,likelihood_ratio,basis,quote,reference\n"
                    f"huri,negative,{relation},0.5,1.0,,,q,r\nhuri,positive,{relation},0.5,0.05,,,q,r\n"
                    f"negatome,negative,{relation},0.1,0.9,,,q,r\nperturbseq,negative,regulates_transcription_of,0.9,0.95,,,q,r\n"
                    f"go_not,negative,{relation},,,,,q,r\n")
    return path


def test_observations_multiply_the_odds_capped_and_only_on_the_relations_their_ratio_names(tmp_path):
    ratios = read_likelihood_ratios(ratio_table(tmp_path / "ratios.csv"))
    evidence = pd.DataFrame({"relation_type": ["binds", "binds", "activates", "binds", "binds"],
                             "huri_negative": [1, 0, 1, 0, 0], "huri_positive": [0, 1, 0, 0, 0], "negatome_negative": [0, 0, 0, 5, 0], "negatome_positive": [0] * 5,
                             "go_not_negative": [0, 0, 0, 0, 3], "go_not_positive": [0] * 5})
    total, contributions = log_likelihood_ratio(evidence, ratios, ("huri", "negatome", "go_not"), observation_cap=2)
    np.testing.assert_allclose(total, [math.log(0.5), math.log(10.0), 0.0, 2 * math.log(1 / 9), 0.0])
    assert contributions["huri_negative"]["observed_on_relations_the_ratio_does_not_cover"] == 1
    assert contributions["go_not_negative"]["edges_moved"] == 0 and "no published measurement" in contributions["go_not_negative"]["why_not_applied"]
    with pytest.raises(ValueError, match="no perturbseq_negative column"):
        log_likelihood_ratio(evidence, ratios, ("perturbseq",))
    with pytest.raises(ValueError, match="unknown negative evidence source"):
        log_likelihood_ratio(evidence, ratios, ("string",))


def test_the_prior_moves_by_its_odds_and_ungated_edges_keep_their_nan():
    probability = np.array([0.9, np.nan, 0.5, 0.9999])
    gated = np.array([True, False, True, True])
    moved = apply_likelihood_ratios(probability, gated, np.array([math.log(1 / 9), math.log(5.0), 0.0, math.log(1e6)]))
    assert math.isclose(moved[0], 0.5) and np.isnan(moved[1]) and moved[2] == 0.5 and moved[3] == pytest.approx(1 - 1e-4)
    assert probability[0] == 0.9, "the input is not changed in place"


# ---------------------------------------------------------------------------------------------------------------------
# HuRI


def huri_evidence() -> pd.DataFrame:
    return pd.DataFrame({"source_id": ["PROTEIN:A", "PROTEIN:B", "GENE:A", "PROTEIN:A", "PROTEIN:A", "PROTEIN:C"],
                         "target_id": ["PROTEIN:B", "PROTEIN:A", "GENE:C", "PROTEIN:Z", "PROTEIN:B", "PROTEIN:D"],
                         "relation_type": ["binds", "binds", "binds", "binds", "activates", "binds"],
                         "family": ["signalling"] * 6, "resources": ["SIGNOR", "SIGNOR;HuRI", "IntAct", "HPRD", "SIGNOR", "SIGNOR"],
                         "pubmed_ids": ["1", "1", "2", "3", "4", "32296183"]})


def test_a_tested_pair_is_a_negative_unless_detected_and_a_detection_already_on_the_edge_counts_once():
    huri_pairs = {frozenset(("A", "B")), frozenset(("C", "D")), frozenset(("E", "E"))}
    tested = huri.tested_genes(huri_pairs) | {"C"}
    assert huri.tested_genes(huri_pairs) == {"A", "B", "C", "D", "E"}
    columns = huri.huri_edge_columns(huri_evidence(), huri_pairs, tested)
    assert columns.huri_status.tolist() == ["detected", "detected_already_a_record", "tested_not_detected", "outside_tested_space", "not_binds",
                                            "detected_already_a_record"]
    assert columns.huri_positive.tolist() == [1, 0, 0, 0, 0, 0] and columns.huri_negative.tolist() == [0, 0, 1, 0, 0, 0]


def test_the_precision_reading_places_a_resource_between_the_random_and_the_reference_rates(tmp_path):
    genes = [f"G{index}" for index in range(10)]
    huri_pairs = {frozenset((genes[0], genes[1])), frozenset((genes[2], genes[3])), frozenset((genes[4], genes[5]))}
    tested = set(genes)
    random = huri.random_pair_rate(huri_pairs, tested)
    assert random["possible_pairs"] == 45 and random["rate"] == pytest.approx(3 / 45)
    lit_bm = {frozenset((genes[0], genes[1])), frozenset((genes[2], genes[3])), frozenset((genes[6], genes[7])), frozenset((genes[0], "OUTSIDE"))}
    reference = huri.detection_rate(lit_bm, huri_pairs, tested)
    assert reference["pairs_inside_tested_space"] == 3 and reference["rate"] == pytest.approx(2 / 3)
    assert huri.precision_from_rates(2 / 3, 2 / 3, 3 / 45) == pytest.approx(1.0) and huri.precision_from_rates(3 / 45, 2 / 3, 3 / 45) == 0.0
    omnipath = pd.DataFrame({"source_genesymbol": ["G0", "G2", "G8", "G4"], "target_genesymbol": ["G1", "G3", "G9", "G5"],
                             "sources": ["IntAct;SIGNOR", "SIGNOR", "SIGNOR;HuRI", "IntAct"],
                             "references": ["IntAct:32296183;SIGNOR:1", "SIGNOR:2", "SIGNOR:3", "IntAct:4"]})
    graph_pairs = {frozenset(pair) for pair in (("G0", "G1"), ("G2", "G3"), ("G8", "G9"), ("G4", "G5"))}
    by_resource = huri.resource_pairs(omnipath, graph_pairs)
    assert by_resource["IntAct"] == {frozenset(("G4", "G5"))}, "IntAct is not credited with a pair it cites only from HuRI's paper"
    assert by_resource["SIGNOR"] == {frozenset(("G0", "G1")), frozenset(("G2", "G3")), frozenset(("G8", "G9"))}
    result = huri.resource_precision(by_resource, graph_pairs, huri_pairs, lit_bm, tested)
    assert "HuRI" not in result["by_resource"], "a resource OmniPath imports from the reference is not scored"
    assert result["by_resource"]["SIGNOR"]["rate"] == pytest.approx(2 / 3) and result["by_resource"]["SIGNOR"]["precision"] == pytest.approx(1.0)


def test_interactome_atlas_tables_are_read_as_symbol_pairs(tmp_path):
    (tmp_path / "HuRI.tsv").write_text("ENSG01\tENSG02\nENSG03\tENSG03\nENSG04\tENSG99\n")
    (tmp_path / "hgnc.txt").write_text("hgnc_id\tsymbol\tensembl_gene_id\tuniprot_ids\nH:1\tA\tENSG01\tP11111\nH:2\tB\tENSG02\t\nH:3\tC\tENSG03\t\nH:4\tD\tENSG04\t\n")
    pairs, mapping = huri.symbol_pairs(huri.read_ensembl_pairs(tmp_path / "HuRI.tsv"), huri.symbol_of_ensembl_gene(tmp_path / "hgnc.txt"))
    assert pairs == {frozenset(("A", "B")), frozenset(("C",))} and mapping["ensembl_ids_without_a_symbol"] == 1


# ---------------------------------------------------------------------------------------------------------------------
# Negatome


def test_negatome_pairs_count_once_per_independent_set_on_every_edge_between_the_proteins(tmp_path):
    directory = tmp_path / "negatome"
    directory.mkdir()
    (directory / "manual.txt").write_text("P11111\tP22222\t12345\tMI:0019\nP11111\tP33333\t2\n")
    (directory / "manual_stringent.txt").write_text("P11111\tP22222\t12345\n")
    (directory / "pdb.txt").write_text("P11111-2\tP22222\t1ABC\nP44444\tP55555\t2XYZ\n")
    (directory / "combined_stringent.txt").write_text("P66666 P77777\n")
    (directory / "manual_pfam.txt").write_text("PF00001\tPF00002\n")
    held = negatome.read_negatome(directory)
    assert held[frozenset(("P11111", "P22222"))] == {"manual", "pdb"} and held[frozenset(("P66666", "P77777"))] == {"combined"}
    assert len(held) == 4
    evidence = pd.DataFrame({"source_id": ["PROTEIN:A:P11111", "GENE:B", "PROTEIN:A:P11111", "PROTEIN:F", "PROTEIN:A:P11111"],
                             "target_id": ["PROTEIN:B:P22222", "GENE:A", "PROTEIN:C", "PROTEIN:G", "PROTEIN:D"],
                             "relation_type": ["binds", "activates", "binds", "binds", "binds"]})
    symbols = {"P11111": "A", "P22222": "B", "P33333": "C", "P66666": "F", "P77777": "G"}
    columns = negatome.negatome_edge_columns(evidence, held, symbols)
    assert columns.negatome_negative.tolist() == [2, 2, 1, 1, 0] and columns.negatome_positive.sum() == 0
    assert columns.negatome_sets.tolist()[:2] == ["manual;pdb", "manual;pdb"]


# ---------------------------------------------------------------------------------------------------------------------
# Perturb-seq


def toy_pseudobulk() -> perturbseq.Pseudobulk:
    genes = {"T1": 0, "T2": 1, "T3": 2, "TF1": 3}
    rows = np.zeros((4, 4))
    rows[0] = [-0.5, 0.0, 0.5, -1.0]  # TF1, strong knockdown: T1 down, T2 unchanged, T3 up
    rows[1] = [0.0, 0.0, 0.0, -0.1]  # TF1 by its other promoter, weaker
    rows[2] = [-2.0, 0.0, 0.0, 0.0]  # TF2, knockdown not confirmed
    rows[3] = [0.0, 0.0, 0.0, 0.0]  # TF3, knockdown not measured
    return perturbseq.Pseudobulk(perturbation_gene=np.array(["TF1", "TF1", "TF2", "TF3"], dtype=object), fold_expression=np.array([0.1, 0.6, 0.9, np.nan]),
                                 control_expression=np.array([1.0, 1.0, 1.0, 0.0]), cells=np.array([400.0, 400.0, 400.0, 400.0]), measured_genes=genes, matrix=rows)


def test_a_confirmed_knockdown_gives_a_negative_for_an_unchanged_target_and_a_positive_only_with_the_signed_direction():
    evidence = pd.DataFrame({"source_id": ["PROTEIN:TF1", "PROTEIN:TF1", "PROTEIN:TF1", "PROTEIN:TF1", "PROTEIN:TF2", "PROTEIN:TF3", "PROTEIN:TF9", "PROTEIN:TF1"],
                             "target_id": ["GENE:T1", "GENE:T2", "GENE:T3", "GENE:T9", "GENE:T1", "GENE:T1", "GENE:T1", "GENE:T1"],
                             "relation_type": ["regulates_transcription_of"] * 7 + ["binds"]})
    signs = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0])
    columns = perturbseq.perturbseq_edge_columns(evidence, signs, toy_pseudobulk())
    assert columns.perturbseq_status.tolist() == ["response_agrees", "no_response", "response_against_sign", "target_not_expressed", "knockdown_unconfirmed",
                                                  "knockdown_unconfirmed", "factor_not_perturbed", "not_regulation"]
    assert columns.perturbseq_positive.tolist() == [1, 0, 0, 0, 0, 0, 0, 0] and columns.perturbseq_negative.tolist() == [0, 1, 0, 0, 0, 0, 0, 0]
    assert columns.perturbseq_z.iloc[0] == pytest.approx(-10.0) and columns.perturbseq_knockdown.iloc[0] == pytest.approx(0.9)
    assert set(columns.perturbseq_cell_line[columns.perturbseq_status.isin(["response_agrees", "no_response"])]) == {"K562"}
    assert perturbseq.perturbed_gene("10000_ZBTB46_P1P2_ENSG00000130584") == "ZBTB46" and perturbseq.perturbed_gene("5_NKX2-1_P1_ENSG1") == "NKX2-1"
    np.testing.assert_allclose(perturbseq.benjamini_hochberg(np.array([0.01, 0.04, 0.03, 0.5])), [0.04, 0.16 / 3, 0.16 / 3, 0.5])


# ---------------------------------------------------------------------------------------------------------------------
# ChEMBL


def test_activity_records_are_called_negative_positive_inconclusive_or_flagged():
    call = chembl.classify_activity
    assert call({"activity_comment": "Not Active"}) == "negative" and call({"activity_comment": "inactive", "pchembl_value": "7"}) == "negative"
    assert call({"standard_relation": ">", "standard_type": "IC50", "standard_units": "nM", "standard_value": "10000"}) == "negative"
    assert call({"standard_relation": ">", "standard_type": "IC50", "standard_units": "nM", "standard_value": "1000"}) == "inconclusive", "a limit below 10 uM says nothing at 10 uM"
    assert call({"standard_relation": ">", "standard_type": "Inhibition", "standard_units": "%", "standard_value": "50"}) == "inconclusive"
    assert call({"standard_relation": "=", "pchembl_value": "5.0"}) == "positive" and call({"standard_relation": "=", "pchembl_value": "4.2"}) == "inconclusive"
    assert call({"standard_relation": "=", "pchembl_value": "8", "data_validity_comment": "Potential transcription error"}) == "flagged"


def test_compounds_and_targets_map_through_chebi_pubchem_and_uniprot_and_documents_count_once(tmp_path):
    nodes = pd.DataFrame({"node_id": ["MAM01c", "MAM02c", "DRUG:CID100000896", "PROTEIN:E1:P11111", "GENE:E2", "MAR1"],
                          "node_type": ["metabolite", "metabolite", "drug", "protein", "gene", "reaction"],
                          "base_metabolite_id": ["MAM01", "CHEBI17632", None, None, None, None]})
    human_gem = chembl.chebi_of_base(pd.DataFrame({"metsNoComp": ["MAM01"], "metChEBIID": ["CHEBI:15422"]}))
    compounds = chembl.compound_ids_of_nodes(nodes, human_gem, {"CHEBI:15422": {"CHEMBL14249"}, "CHEBI:17632": {"CHEMBL1"}}, {"896": ["CHEMBL45"]})
    assert compounds == {"MAM01c": {"CHEMBL14249"}, "MAM02c": {"CHEMBL1"}, "DRUG:CID100000896": {"CHEMBL45"}}
    targets = chembl.target_ids_of_nodes(nodes, {"P11111": {"CHEMBL201"}, "P22222": {"CHEMBL202"}}, {"E2": {"P22222"}})
    assert targets == {"PROTEIN:E1:P11111": {"CHEMBL201"}, "GENE:E2": {"CHEMBL202"}}
    evidence = pd.DataFrame({"source_id": ["MAM01c", "MAM02c", "DRUG:CID100000896", "MAM01c"], "target_id": ["PROTEIN:E1:P11111", "GENE:E2", "GENE:E2", "MAR1"],
                             "relation_type": ["inhibits", "activates", "targets", "substrate_of"]})
    assert chembl.candidate_pairs(evidence, compounds, targets) == {"CHEMBL14249": {"CHEMBL201"}, "CHEMBL1": {"CHEMBL202"}, "CHEMBL45": {"CHEMBL202"}}
    activities = pd.DataFrame([
        {"activity_id": "1", "parent_molecule_chembl_id": "CHEMBL14249", "molecule_chembl_id": "CHEMBL14249", "target_chembl_id": "CHEMBL201", "activity_comment": "Inactive",
         "document_chembl_id": "D1"},
        {"activity_id": "2", "parent_molecule_chembl_id": "CHEMBL14249", "molecule_chembl_id": "CHEMBL9", "target_chembl_id": "CHEMBL201", "activity_comment": "Not Active",
         "document_chembl_id": "D1"},
        {"activity_id": "3", "parent_molecule_chembl_id": "CHEMBL14249", "molecule_chembl_id": "CHEMBL14249", "target_chembl_id": "CHEMBL201", "standard_relation": ">",
         "standard_type": "Ki", "standard_units": "nM", "standard_value": "30000", "document_chembl_id": "D2"},
        {"activity_id": "4", "parent_molecule_chembl_id": "CHEMBL45", "molecule_chembl_id": "CHEMBL45", "target_chembl_id": "CHEMBL202", "standard_relation": "=",
         "pchembl_value": "7.1", "document_chembl_id": "D3"}])
    columns = chembl.chembl_edge_columns(evidence, compounds, targets, activities)
    assert columns.chembl_negative.tolist() == [2, 0, 0, 0], "two documents, and a salt's record counts for its parent"
    assert columns.chembl_positive.tolist() == [0, 0, 1, 0] and columns.chembl_limit_um.iloc[0] == pytest.approx(30.0) and np.isnan(columns.chembl_limit_um.iloc[2])
    assert chembl.pubchem_cid_of_perturbation("CID100000896") == "896" and chembl.pubchem_cid_of_perturbation("CID2244") == "2244"
    assert chembl.chebi_ids_of_base("CHEBI:17632", {}) == {"CHEBI:17632"}


def test_the_target_and_chebi_mappings_are_read_from_the_chembl_and_unichem_files(tmp_path):
    (tmp_path / "map.txt").write_text("# chembl_37 target list\nP11111\tCHEMBL201\tEnzyme\tSINGLE PROTEIN\nP11111\tCHEMBL9999\tComplex\tPROTEIN COMPLEX\n")
    assert chembl.read_target_mapping(tmp_path / "map.txt") == {"P11111": {"CHEMBL201"}}
    with gzip.open(tmp_path / "src1src7.txt.gz", "wt") as handle:
        handle.write("From src:'1'\tTo src:'7'\nCHEMBL14249\tCHEBI:15422\nCHEMBL1\t17632\n")
    assert chembl.read_chebi_mapping(tmp_path / "src1src7.txt.gz") == {"CHEBI:15422": {"CHEMBL14249"}, "CHEBI:17632": {"CHEMBL1"}}


# ---------------------------------------------------------------------------------------------------------------------
# GO NOT annotations

OBO = """format-version: 1.2

[Term]
id: GO:0003674
name: molecular_function

[Term]
id: GO:0140110
name: transcription regulator activity
is_a: GO:0003674

[Term]
id: GO:0003700
name: DNA-binding transcription factor activity
is_a: GO:0140110

[Term]
id: GO:0000981
name: DNA-binding transcription factor activity, RNA polymerase II-specific
is_a: GO:0003700

[Term]
id: GO:0003824
name: catalytic activity
is_a: GO:0003674

[Term]
id: GO:0004340
name: glucokinase activity
is_a: GO:0003824
xref: EC:2.7.1.2

[Term]
id: GO:0005488
name: binding
is_a: GO:0003674

[Term]
id: GO:0005515
name: protein binding
is_a: GO:0005488
"""


def gaf_line(accession, symbol, qualifier, term, reference="PMID:1", evidence_code="IDA", with_from=""):
    return "\t".join(["UniProtKB", accession, symbol, qualifier, term, reference, evidence_code, with_from, "F", "name", "", "protein", "taxon:9606", "20200101", "GO", "", ""])


def test_a_not_rules_out_the_edge_types_it_names_down_its_children_and_a_conflict_counts_neither_way(tmp_path):
    (tmp_path / "go.obo").write_text(OBO)
    lines = [gaf_line("P1", "TF1", "NOT|enables", "GO:0140110"),  # above the rule's term: applies
             gaf_line("P2", "TF2", "NOT|enables", "GO:0000981"),  # below it: says nothing about other factor activity
             gaf_line("P3", "TF3", "NOT|enables", "GO:0003700"), gaf_line("P3", "TF3", "enables", "GO:0000981"),  # conflicted
             gaf_line("P4", "GCK", "NOT|enables", "GO:0004340", "PMID:2"),
             gaf_line("P5", "B1", "NOT|enables", "GO:0005515", "PMID:3", "IPI", "UniProtKB:P6"),
             gaf_line("P7", "B2", "NOT|enables", "GO:0005515", "PMID:4", "IPI", "")]
    with gzip.open(tmp_path / "goa.gaf.gz", "wt") as handle:
        handle.write("!gaf-version: 2.2\n" + "\n".join(lines) + "\n")
    parents, ec_of_term = go_not.read_is_a_and_ec(tmp_path / "go.obo")
    negatives, positive_terms, positive_partners = go_not.read_gaf_molecular_functions(tmp_path / "goa.gaf.gz")
    rules = go_not.read_rules(REPOSITORY_ROOT / go_not.DEFAULT_RULES)
    nodes = pd.DataFrame({"node_id": ["MAR1", "MAR2", "MAR3"], "node_type": ["reaction"] * 3, "is_transport": [False, False, True]})
    evidence = pd.DataFrame({"source_id": ["PROTEIN:TF1", "PROTEIN:TF2", "PROTEIN:TF3", "PROTEIN:GCK", "PROTEIN:GCK", "PROTEIN:B1", "PROTEIN:B6", "PROTEIN:B1", "PROTEIN:B2"],
                             "target_id": ["GENE:X", "GENE:X", "GENE:X", "MAR1", "MAR2", "PROTEIN:B6", "PROTEIN:B1", "PROTEIN:B9", "PROTEIN:B6"],
                             "relation_type": ["regulates_transcription_of"] * 3 + ["catalyzed_by"] * 2 + ["binds"] * 4})
    columns, summary = go_not.go_not_edge_columns(evidence, nodes, rules, negatives, positive_terms, positive_partners, parents, ec_of_term,
                                                  {"MAR1": {"2.7.1.2"}, "MAR2": {"2.7.1.1"}}, {"P6": "B6"})
    assert columns.go_not_negative.tolist() == [1, 0, 0, 1, 0, 1, 1, 0, 0]
    assert summary["by_rule"]["GO:0003700"] == {"annotations": 2, "conflicted": 1} and summary["relations_named_by_rules_absent_from_the_graph"] == \
        ["activates", "inhibits", "phosphorylates"]
    assert columns.go_not_positive.sum() == 0


def test_reaction_ec_numbers_are_read_from_the_sbml_annotation(tmp_path):
    (tmp_path / "model.xml").write_text("""<?xml version="1.0"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><model><listOfReactions>
<reaction id="R_MAR1"><annotation><rdf:RDF><rdf:Description><rdf:li rdf:resource="https://identifiers.org/ec-code/2.7.1.2"/>
<rdf:li rdf:resource="https://identifiers.org/rhea/1"/></rdf:Description></rdf:RDF></annotation></reaction>
<reaction id="R_MAR2"/></listOfReactions></model></sbml>""")
    assert go_not.reaction_ec_numbers(tmp_path / "model.xml") == {"MAR1": {"2.7.1.2"}}


# ---------------------------------------------------------------------------------------------------------------------
# assembly and the trainer


def test_a_source_whose_files_are_absent_writes_no_columns_and_says_so(tmp_path):
    evidence = huri_evidence()
    (tmp_path / "HuRI.tsv").write_text("ENSG01\tENSG02\n")
    (tmp_path / "hgnc.txt").write_text("hgnc_id\tsymbol\tensembl_gene_id\tuniprot_ids\nH:1\tA\tENSG01\t\nH:2\tB\tENSG02\t\nH:3\tC\tENSG03\t\n")
    paths = NegativeEvidencePaths(hgnc=tmp_path / "hgnc.txt", huri=tmp_path / "HuRI.tsv", negatome_directory=tmp_path / "none",
                                  pseudobulk=tmp_path / "none.h5ad", chembl_activities=tmp_path / "none.parquet", go_gaf=tmp_path / "none.gaf.gz")
    columns, summary = assemble_negative_evidence(evidence, evidence, pd.DataFrame({"node_id": [], "node_type": []}), paths)
    assert {column for column in columns.columns if column.endswith(("_negative", "_positive"))} == {"huri_negative", "huri_positive"}
    assert all("absent" in summary["sources"][source] for source in ("negatome", "perturbseq", "chembl", "go_not"))
    assert summary["sources"]["huri"]["tested_genes"] == 2 and summary["counts"]["huri"]["positive"]["edges"] == 1
    assert summarise_negative_evidence(pd.concat([evidence, columns], axis=1))["huri"]["negative"]["by_family_and_relation"] == {}


def test_the_flag_is_off_by_default_and_names_itself_in_the_fingerprint_only_while_on(tmp_path):
    arguments = build_argument_parser().parse_args(["--graph-dir", "g", "--evidence-dir", "e"])
    assert arguments.edge_negative_evidence == [] and arguments.edge_negative_likelihood_ratios == Path("configs/edge_negative_likelihood_ratios.csv")
    assert not EDGE_NEGATIVE_EVIDENCE_SETTINGS & (EDGE_PRIOR_SETTINGS | ARGUMENTS_RECORDED_ONLY_WHEN_SET)
    data = Namespace(outcomes=np.zeros((2, 2)), weights=np.zeros((2, 2)), edge_source=np.array([0]), edge_target=np.array([1]), edge_relation=np.array([0]),
                     perturbation_seeds=[np.array([0])], perturbation_signs=[np.array([-1.0])], perturbation_magnitudes=[np.array([1.0])])
    (tmp_path / EDGE_EVIDENCE_FILE).write_bytes(b"table")
    base = dict(graph_dir=tmp_path, edge_prior_tiers=TIERS, edge_prior_tempering=0.5, edge_prior_count_cap=2, permute_edge_priors=False,
                edge_gate_learning_rate=None, edge_negative_likelihood_ratios=REPOSITORY_ROOT / DEFAULT_LIKELIHOOD_RATIOS_PATH)
    for strength, sources in ((0.0, []), (0.0, ["huri"]), (1.0, [])):
        fingerprint = configuration_fingerprint(Namespace(**base, edge_prior_strength=strength, edge_negative_evidence=sources), data, None)
        assert not [key for key in fingerprint if "negative" in key], "off, a run's fingerprint is what it was before the flag existed"
    on = configuration_fingerprint(Namespace(**base, edge_prior_strength=1.0, edge_negative_evidence=["huri"]), data, None)
    assert on["argument:edge_negative_evidence"] == "['huri']" and len(on["file:edge_negative_likelihood_ratios"]) == 64


def test_the_observations_move_the_gated_priors_by_their_odds_and_leave_labels_and_ungated_edges(tmp_path):
    paths = write_toy_dataset(tmp_path, num_genes=12)
    table = write_edge_evidence(paths["graph"])
    rows = len(table)
    table["huri_negative"] = np.where(np.arange(rows) % 2 == 0, 1, 0)
    table["huri_positive"] = np.where(np.arange(rows) % 5 == 1, 1, 0)
    table.to_parquet(paths["graph"] / EDGE_EVIDENCE_FILE, index=False)
    ratios = ratio_table(tmp_path / "ratios.csv", relation="catalyzed_by;product_of")
    data = load_experiment_data(paths["graph"], paths["evidence"])
    arguments = dict(edge_prior_strength=1.0, encoder="message_passing", graph_dir=paths["graph"], edge_prior_tiers=TIERS, edge_prior_tempering=0.5,
                     edge_prior_count_cap=2, permute_edge_priors=False, seed=0, edge_negative_likelihood_ratios=ratios)
    plain = build_edge_priors(data, Namespace(**arguments, edge_negative_evidence=[]))
    assert plain["negative_evidence"] is None
    plain_probability = data.edge_prior_probability.copy()
    summary = build_edge_priors(data, Namespace(**arguments, edge_negative_evidence=["huri"]))
    gated, probability, _ = edge_priors(table, read_edge_tiers(TIERS))
    odds = np.where(table.huri_negative > 0, 0.5, 1.0) * np.where(table.huri_positive > 0, 10.0, 1.0)
    expected = np.where(gated, probability * odds / (probability * odds + 1 - probability), np.nan)
    np.testing.assert_allclose(data.edge_prior_probability[gated], expected[gated])
    np.testing.assert_array_equal(np.isnan(data.edge_prior_probability), np.isnan(plain_probability))
    moved = gated & (odds != 1.0)
    assert summary["negative_evidence"]["gated_edges_moved"] == int(moved.sum()) and summary["negative_evidence"]["sources"] == ["huri"]
    assert summary["negative_evidence"]["moved_down"] == int((gated & (odds < 1)).sum())
    labelled = build_edge_priors(data, Namespace(**arguments, edge_negative_evidence=["huri"], curated_edge_labels=True, curated_label_minimum_records=2,
                                                 curated_label_minimum_human_records=1))
    assert labelled["negative_evidence"]["labels_with_an_observation_not_applied"] >= 0
    with pytest.raises(ValueError, match="no negatome_negative column"):
        build_edge_priors(data, Namespace(**arguments, edge_negative_evidence=["negatome"]))


def test_the_sources_are_the_five_of_the_decision():
    assert SOURCES == ("negatome", "huri", "perturbseq", "chembl", "go_not")
    with open(REPOSITORY_ROOT / DEFAULT_LIKELIHOOD_RATIOS_PATH, newline="") as handle:
        assert {row["source"] for row in csv.DictReader(handle)} == set(SOURCES)
