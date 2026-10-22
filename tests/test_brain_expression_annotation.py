"""GTEx brain expression on gene nodes, reaction inheritance and the transcription gate (design 3.3 and 4.1; decision 9.76)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.build_physiology_graph import (
    annotate_brain_expression,
    annotate_cell_class_expression,
    load_brain_expression,
    propagate_brain_expression_to_reactions,
    restrict_transcription_edges_to_expressed_factors,
)


def write_gct(path: Path) -> None:
    header = ["Name", "Description", "Liver", "Brain_Cortex", "Brain_Hypothalamus"]
    rows = [
        ["ENSG00000000419.12", "DPM1", "50", "0.2", "3.5"],   # expressed in one brain tissue
        ["ENSG00000001084.13", "GCLC", "80", "0.1", "0.4"],   # known, below threshold
        ["ENSG00000999999.1", "TFHIGH", "1", "12", "20"],    # matched by symbol only
        ["ENSG00000888888.1", "TFLOW", "9", "0.0", "0.3"],   # below the brain threshold, expressed in the liver
        ["ENSG00000777777.1", "TFNOWHERE", "0.2", "0.0", "0.1"],  # below the threshold in every tissue
        ["ENSG00000666666.1", "TFCLASS", "0.1", "0.0", "0.0"],    # below the threshold everywhere in GTEx, seen by one cell class
    ]
    path.write_text("#1.2\n6\t3\n" + "\n".join("\t".join(row) for row in [header, *rows]) + "\n")


def cell_class_table() -> pd.DataFrame:
    """The per-gene largest class value the build reads: TFLOW at 0 in every class, TFNOWHERE at 0, TFCLASS at 0.4 (under
    the detection threshold), DPM1 and GCLC detected."""
    return pd.DataFrame({"ensembl_gene_id": ["ENSG00000000419", "ENSG00000001084", "ENSG00000888888", "ENSG00000777777", "ENSG00000666666"],
                         "gene_symbol": ["DPM1", "GCLC", "TFLOW", "TFNOWHERE", "TFCLASS"],
                         "cell_class_ncpm_max": [30.0, 2.0, 0.0, 0.0, 0.4]})


def test_annotation_matches_ensembl_then_symbol_and_the_gate_reads_body_and_class_expression(tmp_path: Path) -> None:
    gct = tmp_path / "median_tpm.gct"
    write_gct(gct)
    expression = load_brain_expression(gct)
    assert expression.brain_tissue_count.iloc[0] == 2
    assert expression.set_index("gene_symbol").loc["TFLOW", "body_median_tpm_max"] == 9.0  # the liver counts toward the body maximum
    nodes = pd.DataFrame([
        {"node_id": "GENE:DPM1", "node_type": "gene", "gene_symbol": "DPM1", "ensembl_gene_id": "ENSG00000000419"},
        {"node_id": "GENE:GCLC", "node_type": "gene", "gene_symbol": "GCLC", "ensembl_gene_id": "ENSG00000001084"},
        {"node_id": "GENE:TFHIGH", "node_type": "gene", "gene_symbol": "TFHIGH", "ensembl_gene_id": None},
        {"node_id": "GENE:TFLOW", "node_type": "gene", "gene_symbol": "TFLOW", "ensembl_gene_id": None},
        {"node_id": "GENE:TFNOWHERE", "node_type": "gene", "gene_symbol": "TFNOWHERE", "ensembl_gene_id": None},
        {"node_id": "GENE:TFCLASS", "node_type": "gene", "gene_symbol": "TFCLASS", "ensembl_gene_id": None},
        {"node_id": "GENE:UNKNOWN", "node_type": "gene", "gene_symbol": "UNKNOWN", "ensembl_gene_id": None},
        {"node_id": "MAR00001", "node_type": "reaction", "gene_symbol": None, "ensembl_gene_id": None},
    ])
    annotated = annotate_brain_expression(nodes, expression, minimum_tpm=1.0)
    annotated = annotate_cell_class_expression(annotated, cell_class_table(), minimum_tpm=1.0, detection_threshold_ncpm=1.0)
    by_id = annotated.set_index("node_id")
    assert by_id.loc["GENE:DPM1", "brain_expressed"] and by_id.loc["GENE:DPM1", "brain_median_tpm_max"] == 3.5 and by_id.loc["GENE:DPM1", "body_median_tpm_max"] == 50.0
    assert by_id.loc["GENE:GCLC", "brain_expression_known"] and not by_id.loc["GENE:GCLC", "brain_expressed"]
    assert by_id.loc["GENE:TFHIGH", "brain_expressed"]  # symbol match for a gene without an Ensembl id
    assert not by_id.loc["GENE:UNKNOWN", "brain_expression_known"] and not by_id.loc["GENE:UNKNOWN", "brain_expressed"]
    assert by_id.loc["GENE:TFLOW", "cell_class_expression_known"] and by_id.loc["GENE:TFLOW", "cell_class_ncpm_max"] == 0.0
    assert not by_id.loc["GENE:UNKNOWN", "cell_class_expression_known"] and pd.isna(by_id.loc["GENE:UNKNOWN", "cell_class_ncpm_max"])
    # the flag the edge prior reads: below the brain threshold and under detection in every class (or unknown to the classes)
    assert by_id.expression_below_detection.to_dict() == {"GENE:DPM1": False, "GENE:GCLC": False, "GENE:TFHIGH": False, "GENE:TFLOW": True,
                                                          "GENE:TFNOWHERE": True, "GENE:TFCLASS": True, "GENE:UNKNOWN": False, "MAR00001": False}
    edges = pd.DataFrame([
        {"source_id": "MAR00001", "target_id": "GENE:GCLC", "relation_type": "catalyzed_by", "sign": 0.0},
        {"source_id": "MAR00001", "target_id": "GENE:DPM1", "relation_type": "catalyzed_by", "sign": 0.0},
        {"source_id": "GENE:TFHIGH", "target_id": "GENE:DPM1", "relation_type": "regulates_transcription_of", "sign": 1.0},
        {"source_id": "GENE:TFLOW", "target_id": "GENE:DPM1", "relation_type": "regulates_transcription_of", "sign": 1.0},
        {"source_id": "GENE:TFNOWHERE", "target_id": "GENE:DPM1", "relation_type": "regulates_transcription_of", "sign": 1.0},
        {"source_id": "GENE:TFNOWHERE", "target_id": "GENE:GCLC", "relation_type": "regulates_transcription_of", "sign": -1.0},
        {"source_id": "GENE:TFCLASS", "target_id": "GENE:DPM1", "relation_type": "regulates_transcription_of", "sign": 1.0},
        {"source_id": "GENE:GCLC", "target_id": "GENE:DPM1", "relation_type": "regulates_transcription_of", "sign": 1.0},
        {"source_id": "GENE:UNKNOWN", "target_id": "GENE:DPM1", "relation_type": "regulates_transcription_of", "sign": -1.0},
        {"source_id": "GENE:TFNOWHERE", "target_id": "GENE:DPM1", "relation_type": "activates", "sign": 1.0},
    ])
    kept, counts = restrict_transcription_edges_to_expressed_factors(annotated, edges, minimum_tpm=1.0)
    # only TFNOWHERE is dropped: at 0 in every class and below the threshold in every tissue of the body
    assert counts["transcription_edges_before"] == 7 and counts["transcription_edges_dropped_factor_unexpressed"] == 2 and counts["transcription_factors_dropped"] == 1
    assert not ((kept.source_id == "GENE:TFNOWHERE") & (kept.relation_type == "regulates_transcription_of")).any()
    assert ((kept.source_id == "GENE:TFNOWHERE") & (kept.relation_type == "activates")).any()  # only regulon edges are gated
    # TFLOW (liver) is kept by its body expression, TFCLASS by its class value, GCLC by both; the brain-TPM gate would have dropped all four factors
    assert ((kept.source_id == "GENE:TFLOW") & (kept.relation_type == "regulates_transcription_of")).any()
    assert ((kept.source_id == "GENE:TFCLASS") & (kept.relation_type == "regulates_transcription_of")).any()
    assert counts["transcription_edges_the_brain_tpm_gate_would_have_dropped"] == 5 and counts["transcription_factors_the_brain_tpm_gate_would_have_dropped"] == 4
    assert counts["transcription_edges_kept_by_cell_class_expression"] == 2 and counts["transcription_factors_kept_by_cell_class_expression"] == 2  # TFCLASS, GCLC
    assert counts["transcription_edges_kept_by_body_expression"] == 1 and counts["transcription_factors_kept_by_body_expression"] == 1  # TFLOW
    assert counts["transcription_edges_factor_below_detection"] == 2 and counts["transcription_factors_below_detection"] == 2  # TFLOW and TFCLASS, kept, lowered prior
    assert counts["transcription_edges_kept_factor_expression_unknown"] == 1 and counts["transcription_factors_expression_unknown"] == 1
    assert len(kept) == 8
    with_reactions = propagate_brain_expression_to_reactions(annotated, kept)
    assert with_reactions.set_index("node_id").loc["MAR00001", "brain_median_tpm_max"] == 3.5  # largest over its genes


def test_without_a_cell_class_table_nothing_is_dropped_and_the_flag_follows_the_brain_threshold(tmp_path: Path) -> None:
    gct = tmp_path / "median_tpm.gct"
    write_gct(gct)
    nodes = pd.DataFrame([{"node_id": "GENE:TFNOWHERE", "node_type": "gene", "gene_symbol": "TFNOWHERE", "ensembl_gene_id": None},
                          {"node_id": "GENE:DPM1", "node_type": "gene", "gene_symbol": "DPM1", "ensembl_gene_id": "ENSG00000000419"}])
    annotated = annotate_brain_expression(nodes, load_brain_expression(gct), minimum_tpm=1.0)
    annotated = annotate_cell_class_expression(annotated, pd.DataFrame(columns=["ensembl_gene_id", "gene_symbol", "cell_class_ncpm_max"]), minimum_tpm=1.0)
    assert not annotated.cell_class_expression_known.any() and annotated.set_index("node_id").expression_below_detection.to_dict() == {"GENE:TFNOWHERE": True, "GENE:DPM1": False}
    edges = pd.DataFrame([{"source_id": "GENE:TFNOWHERE", "target_id": "GENE:DPM1", "relation_type": "regulates_transcription_of", "sign": 1.0}])
    kept, counts = restrict_transcription_edges_to_expressed_factors(annotated, edges, minimum_tpm=1.0)
    assert len(kept) == 1 and counts["transcription_edges_dropped_factor_unexpressed"] == 0, "absence from the class table is a mapping gap, not evidence"
    assert counts["transcription_edges_factor_below_detection"] == 1


def test_structural_features_carry_brain_expression_when_present() -> None:
    import numpy as np

    from mechanistic_pathway_learning.evaluation.experiment_data import ExperimentData

    def make(brain_expression, brain_expressed):
        return ExperimentData(
            node_ids=["a", "b"], node_index={"a": 0, "b": 1}, node_types=np.array(["gene", "reaction"]), is_currency=np.array([False, False]),
            node_degree=np.array([1.0, 3.0]), edge_source=np.array([0]), edge_target=np.array([1]), edge_relation=np.array([0]), relation_types=["catalyzed_by"],
            symptoms=["anxiety"], perturbation_ids=["g"], perturbation_labels=["g"], perturbation_types=["gene"], group_ids=["g"],
            perturbation_seeds=[np.array([0])], perturbation_signs=[np.array([-1.0])], perturbation_magnitudes=[np.array([1.0])],
            outcomes=np.ones((1, 1)), weights=np.ones((1, 1)), in_metabolic_layer=np.array([True]),
            node_brain_expression=brain_expression, node_brain_expressed=brain_expressed,
        )

    without = make(None, None).structural_node_features()
    with_expression = make(np.log1p(np.array([3.5, 0.0])), np.array([True, False])).structural_node_features()
    assert without.shape == with_expression.shape  # the feature width is fixed so models built on either graph have the same input size
    assert np.all(without[:, -2:] == 0.0)
    assert np.isclose(with_expression[0, -2], np.log1p(3.5)) and with_expression[0, -1] == 1.0 and with_expression[1, -1] == 0.0
