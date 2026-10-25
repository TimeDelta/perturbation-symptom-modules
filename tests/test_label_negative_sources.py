"""Evidenced negatives from Phenopacket Store exclusions and from the statin-placebo meta-analysis, and the per-pair
strength matrices the loader exposes for them (decision 9.92)."""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mechanistic_pathway_learning.evaluation.experiment_data import EVIDENCED_NEGATIVE_ARRAYS, load_experiment_data, restrict_to_perturbations
from mechanistic_pathway_learning.evidence.load_monogenic_phenotype_annotations import load_hpo_is_a_parents_from_obo
from mechanistic_pathway_learning.evidence.phenopacket_store import (
    ABSENT_ANCESTOR_EXCLUSION,
    ABSENT_ROOT_EXCLUSION,
    ABSENT_STUDY_COMPLETE,
    EXCLUSION_AGE_UNKNOWN,
    EXCLUSION_BELOW_MINIMUM_AGE,
    INDIVIDUALS_ASSESSED_COLUMN,
    INDIVIDUALS_OBSERVED_COLUMN,
    NARROW_EXCLUSION_NOT_COUNTED,
    OBSERVED,
    OBSERVED_IN_CARVED_OUT_DESCENDANT,
    AlleleKeys,
    clean_negative_pairs,
    gene_resolver,
    individual_status_table,
    load_hpo_term_replacements,
    pair_counts,
    parse_iso8601_duration_years,
    read_constructs,
    read_minimum_ages,
    read_phenopackets,
    years_of_time_element,
)

OBO = """format-version: 1.2

[Term]
id: HP:0000001
name: All

[Term]
id: HP:0000708
name: Atypical behavior
is_a: HP:0000001 ! All

[Term]
id: HP:0000752
name: Hyperactivity
is_a: HP:0000708 ! Atypical behavior

[Term]
id: HP:0007018
name: Attention deficit hyperactivity disorder
is_a: HP:0000752 ! Hyperactivity

[Term]
id: HP:0000716
name: Depression
alt_id: HP:9000010
is_a: HP:0000708 ! Atypical behavior

[Term]
id: HP:9000001
name: Narrow depressive feature
is_a: HP:0000716 ! Depression

[Term]
id: HP:0002360
name: Sleep disturbance
is_a: HP:0000001 ! All

[Term]
id: HP:0100785
name: Insomnia
is_a: HP:0002360 ! Sleep disturbance

[Term]
id: HP:9000009
name: obsolete depression
is_obsolete: true
replaced_by: HP:0000716
"""

CROSSWALK = """target_symptom,hpo_ids,excluded_hpo_ids
depressed_mood,HP:0000716,
hyperactivity,HP:0000752,HP:0007018
insomnia,HP:0100785,
"""


def feature(term: str, excluded: bool = False) -> dict:
    return {"type": {"id": term}, **({"excluded": True} if excluded else {})}


def phenopacket(identifier: str, gene: str, features: list[dict], age: str | None = "P10Y", study: str = "PMID:1", disease: str = "OMIM:100000",
                second_gene: str | None = None) -> dict:
    genomic = [{"interpretationStatus": "CAUSATIVE", "variantInterpretation": {"variationDescriptor": {"geneContext": {"valueId": "", "symbol": gene}}}}]
    if second_gene:
        genomic.append({"interpretationStatus": "CAUSATIVE", "variantInterpretation": {"variationDescriptor": {"geneContext": {"valueId": "", "symbol": second_gene}}}})
    return {"id": identifier, "subject": {"id": identifier, **({"timeAtLastEncounter": {"age": {"iso8601duration": age}}} if age else {})},
            "phenotypicFeatures": features,
            "interpretations": [{"diagnosis": {"disease": {"id": disease}, "genomicInterpretations": genomic}}],
            "metaData": {"externalReferences": [{"id": study}]}}


PHENOPACKETS = [
    phenopacket("P1", "GENEA", [feature("HP:0000716", True)]),                                  # the root excluded: absent
    phenopacket("P2", "GENEA", [feature("HP:9000001", True)]),                                  # a narrow term excluded: not counted
    phenopacket("P3", "GENEB", [feature("HP:0000752", True)], age="P8Y", study="PMID:2"),       # the root excluded ...
    phenopacket("P4", "GENEB", [feature("HP:0007018")], study="PMID:2"),                        # ... and ADHD observed in the study: carved out
    phenopacket("P5", "GENEA", [feature("HP:0000716", True)], age="P2Y"),                       # a toddler: below the minimum age
    phenopacket("P6", "GENEA", [feature("HP:9000010", True)], age=None),                        # Depression by its alt id, no age
    phenopacket("P7", "GENEC", [feature("HP:0002360", True)], age="P20Y"),                      # Sleep disturbance excluded: an ancestor
    phenopacket("P8", "GENED", [feature("HP:9000001")], study="PMID:3"),                        # the narrow term observed in the study ...
    phenopacket("P9", "GENED", [feature("HP:9000001", True)], study="PMID:3"),                  # ... and excluded here: study-complete
    phenopacket("P10", "OLDA", [feature("HP:9000009", True)]),                                  # a previous symbol and an obsolete term
    phenopacket("P11", "GENEA", [feature("HP:0000716", True)], second_gene="GENEB"),            # two genes: not a single-gene perturbation
]


@pytest.fixture()
def inputs(tmp_path: Path) -> dict:
    obo = tmp_path / "hp.obo"
    obo.write_text(OBO)
    crosswalk = tmp_path / "crosswalk.csv"
    crosswalk.write_text(CROSSWALK)
    ages = tmp_path / "ages.csv"
    ages.write_text("target_symptom,minimum_age_years\ndepressed_mood,3\nhyperactivity,3\ninsomnia,3\n")
    hgnc = tmp_path / "hgnc.txt"
    hgnc.write_text("hgnc_id\tsymbol\tprev_symbol\tstatus\nHGNC:1\tGENEA\tOLDA\tApproved\nHGNC:2\tGENEB\t\tApproved\nHGNC:3\tGENEC\t\tApproved\nHGNC:4\tGENED\t\tApproved\n")
    archive = tmp_path / "all_phenopackets.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        for packet in PHENOPACKETS:
            handle.writestr(f"0.1.27/{packet['id']}/{packet['id']}.json", json.dumps(packet))
    parents = load_hpo_is_a_parents_from_obo(obo)
    statuses, counts = individual_status_table(read_phenopackets(archive), read_constructs(crosswalk, parents), parents, read_minimum_ages(ages),
                                               gene_resolver(hgnc, {"GENEA", "GENEB", "GENEC", "GENED"}), load_hpo_term_replacements(obo))
    return {"statuses": statuses, "counts": counts, "archive": archive, "obo": obo, "crosswalk": crosswalk, "ages": ages, "hgnc": hgnc}


def status_of(statuses: pd.DataFrame, identifier: str, symptom: str) -> str | None:
    rows = statuses[(statuses.phenopacket_id == identifier) & (statuses.symptom == symptom)]
    return rows.status.iloc[0] if len(rows) else None


def test_ages_are_read_from_durations_gestational_ages_and_onset_classes_at_their_lower_bound():
    assert parse_iso8601_duration_years("P3Y6M") == pytest.approx(3.5)
    assert parse_iso8601_duration_years("P14D") == pytest.approx(14 / 365.25)
    assert parse_iso8601_duration_years("") is None and parse_iso8601_duration_years("not an age") is None
    assert years_of_time_element({"gestationalAge": {"weeks": 30}}) == 0.0
    assert years_of_time_element({"ontologyClass": {"id": "HP:0003621"}}) == 5.0  # Juvenile onset: "between the age of 5 and 15 years"
    assert years_of_time_element({"ontologyClass": {"id": "HP:0000000"}}) is None


def test_each_individual_gets_the_status_the_rules_give(inputs):
    statuses = inputs["statuses"]
    assert status_of(statuses, "P1", "depressed_mood") == ABSENT_ROOT_EXCLUSION
    assert status_of(statuses, "P2", "depressed_mood") == NARROW_EXCLUSION_NOT_COUNTED  # a narrow NOT does not negate the construct
    assert status_of(statuses, "P3", "hyperactivity") == ABSENT_ROOT_EXCLUSION
    assert status_of(statuses, "P4", "hyperactivity") == OBSERVED_IN_CARVED_OUT_DESCENDANT  # ADHD: under the root, carved out
    assert status_of(statuses, "P5", "depressed_mood") == EXCLUSION_BELOW_MINIMUM_AGE
    assert status_of(statuses, "P6", "depressed_mood") == EXCLUSION_AGE_UNKNOWN  # the alt id was read as Depression
    assert status_of(statuses, "P7", "insomnia") == ABSENT_ANCESTOR_EXCLUSION
    assert status_of(statuses, "P8", "depressed_mood") == OBSERVED
    assert status_of(statuses, "P9", "depressed_mood") == ABSENT_STUDY_COMPLETE
    assert status_of(statuses, "P10", "depressed_mood") == ABSENT_ROOT_EXCLUSION  # OLDA is GENEA; the obsolete term is Depression
    assert statuses[statuses.phenopacket_id == "P10"].gene.iloc[0] == "GENEA"
    assert "P11" not in set(statuses.phenopacket_id) and inputs["counts"]["left_out_several_genes"] == 1


def test_n_counts_the_rule_chosen_and_every_status_is_counted_beside_it(inputs):
    root = pair_counts(inputs["statuses"], key="gene", exclusion_rule="root").set_index(["perturbation_id", "symptom"])
    default = pair_counts(inputs["statuses"], key="gene").set_index(["perturbation_id", "symptom"])
    broad = pair_counts(inputs["statuses"], key="gene", exclusion_rule="root_or_ancestor_or_study_complete").set_index(["perturbation_id", "symptom"])
    assert root.loc[("GENEA", "depressed_mood"), INDIVIDUALS_ASSESSED_COLUMN] == 2  # P1 and P10
    assert root.loc[("GENEA", "depressed_mood"), "individuals_narrow_exclusion_not_counted"] == 1
    assert root.loc[("GENEA", "depressed_mood"), "individuals_exclusion_below_minimum_age"] == 1
    assert (root.loc[("GENED", "depressed_mood"), INDIVIDUALS_OBSERVED_COLUMN], root.loc[("GENED", "depressed_mood"), INDIVIDUALS_ASSESSED_COLUMN]) == (1, 1)
    assert default.loc[("GENED", "depressed_mood"), INDIVIDUALS_ASSESSED_COLUMN] == 2  # study-complete adds P9
    assert default.loc[("GENEC", "insomnia"), INDIVIDUALS_ASSESSED_COLUMN] == 0 and broad.loc[("GENEC", "insomnia"), INDIVIDUALS_ASSESSED_COLUMN] == 1
    assert default.loc[("GENEB", "hyperactivity"), "individuals_observed_in_carved_out_descendant"] == 1


def test_a_clean_negative_has_no_observation_no_carved_out_observation_and_no_positive(inputs):
    counts = pair_counts(inputs["statuses"], key="gene")
    clean = set(zip(*[clean_negative_pairs(counts, set())[column] for column in ("perturbation_id", "symptom")]))
    assert clean == {("GENEA", "depressed_mood")}  # GENEB hyperactivity has ADHD observed; GENED depression is observed
    assert clean_negative_pairs(counts, {("GENEA", "depressed_mood")}).empty  # a current positive is never negated
    broad = pair_counts(inputs["statuses"], key="gene", exclusion_rule="root_or_ancestor_or_study_complete")
    assert ("GENEC", "insomnia") in set(zip(*[clean_negative_pairs(broad, set())[column] for column in ("perturbation_id", "symptom")]))


def test_allele_keying_moves_a_gain_of_function_disease_to_its_allele(inputs):
    keys = AlleleKeys({("GENEA", "OMIM:100000"): ("GENEA|gain_of_function", "hypermorph", "orphanet typed")})
    statuses, _ = individual_status_table(read_phenopackets(inputs["archive"]), read_constructs(inputs["crosswalk"], load_hpo_is_a_parents_from_obo(inputs["obo"])),
                                          load_hpo_is_a_parents_from_obo(inputs["obo"]), read_minimum_ages(inputs["ages"]),
                                          gene_resolver(inputs["hgnc"], {"GENEA", "GENEB", "GENEC", "GENED"}), load_hpo_term_replacements(inputs["obo"]), keys)
    by_allele = pair_counts(statuses, key="allele")
    assert "GENEA|gain_of_function" in set(by_allele.perturbation_id) and "GENEA" not in set(by_allele.perturbation_id)
    assert set(pair_counts(statuses, key="gene").perturbation_id) >= {"GENEA"}


def write_graph_and_evidence(tmp_path: Path) -> tuple[Path, Path]:
    graph_directory, evidence_directory = tmp_path / "graph", tmp_path / "evidence"
    graph_directory.mkdir()
    evidence_directory.mkdir()
    pd.DataFrame({"node_id": ["GENE:GENEA", "GENE:GENEB", "GENE:HMGCR", "R1"], "node_type": ["gene", "gene", "gene", "reaction"], "degree": [1, 1, 1, 3],
                  "is_currency": [False] * 4}).to_parquet(graph_directory / "nodes.parquet")
    pd.DataFrame({"source_id": ["GENE:GENEA", "GENE:GENEB", "GENE:HMGCR"], "target_id": ["R1"] * 3, "relation_type": ["catalyzed_by"] * 3}).to_parquet(graph_directory / "edges.parquet")
    (graph_directory / "relation_types.json").write_text(json.dumps(["catalyzed_by"]))

    def row(perturbation_id, perturbation_type, symptom, frequency, grade="A", node="GENE:GENEA"):
        return {"perturbation_id": perturbation_id, "perturbation_type": perturbation_type, "perturbation_label": perturbation_id, "group_id": perturbation_id,
                "symptom": symptom, "relation": "induces", "grade": grade, "weight": 0.8, "in_metabolic_layer": True, "label_frequency": frequency,
                "source": "HPO-OMIM" if perturbation_type == "gene" else "SIDER-label", "positive_report_count": 1, "perturbation_nodes": json.dumps([[node, -1.0, 1.0]])}
    pd.DataFrame([
        row("GENEA", "gene", "anxiety", 0.5), row("GENEB", "gene", "anxiety", float("nan"), node="GENE:GENEB"),
        row("GENEB", "gene", "insomnia", 0.4, grade="C", node="GENE:GENEB"),
        row("CID100002250", "drug", "depressed_mood", 0.02, grade="B", node="GENE:HMGCR"), row("CID100132804", "drug", "anxiety", 0.02, grade="B", node="GENE:HMGCR"),
    ]).to_parquet(evidence_directory / "evidence_records.parquet")
    return graph_directory, evidence_directory


def write_counts(path: Path) -> Path:
    rows = [("GENEA", "depressed_mood", 0, 4, 4, 0), ("GENEA", "anxiety", 3, 5, 2, 0), ("GENEB", "anxiety", 1, 4, 3, 0), ("GENEB", "insomnia", 0, 3, 3, 0),
            ("GENEB", "hyperactivity", 0, 6, 6, 2)]
    pd.DataFrame([{"perturbation_id": p, "gene": p, "symptom": s, INDIVIDUALS_OBSERVED_COLUMN: k, INDIVIDUALS_ASSESSED_COLUMN: n, "individuals_absent_root_exclusion": a,
                   "individuals_absent_study_complete": 0, "individuals_absent_ancestor_exclusion": 0, "individuals_narrow_exclusion_not_counted": 0,
                   "individuals_observed_in_carved_out_descendant": carved, "individuals_exclusion_below_minimum_age": 0, "individuals_exclusion_age_unknown": 0,
                   "studies": "PMID:1", "exclusion_rule": "root_or_study_complete"} for p, s, k, n, a, carved in rows]).to_parquet(path)
    return path


def statin_table(path: Path) -> Path:
    rows = []
    for perturbation_id, drug, in_trials in (("CID100002250", "atorvastatin", True), ("CID100132804", "pitavastatin", False)):
        for symptom, rate_ratio, lower, upper in (("depressed_mood", 0.95, 0.89, 1.01), ("insomnia", 1.00, 0.93, 1.07)):
            rows.append({"perturbation_id": perturbation_id, "drug": drug, "symptom": symptom, "in_the_trials": str(in_trials), "outcome": "outcome", "trials": 19,
                         "participants": 123940, "rate_ratio": rate_ratio, "rate_ratio_lower_95": lower, "rate_ratio_upper_95": upper, "pmid": "41655587", "quote": "q"})
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def build(tmp_path: Path, evidence_directory: Path, name: str, *flags: str) -> tuple[Path, pd.DataFrame, dict]:
    output = tmp_path / f"{name}.parquet"
    completed = subprocess.run([sys.executable, "experiments/build_label_selection.py", "--evidence-dir", str(evidence_directory), "--output", str(output), *flags],
                               capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    return output, pd.read_parquet(output), json.loads(output.with_suffix(".summary.json").read_text())


def test_without_the_flags_the_selection_is_the_one_the_registered_rule_writes(tmp_path: Path):
    _, evidence_directory = write_graph_and_evidence(tmp_path)
    plain_path, plain, plain_summary = build(tmp_path, evidence_directory, "plain", "--mask-grades", "C")
    assert list(plain.columns) == ["perturbation_id", "symptom", "perturbation_type", "label_frequency", "keep", "reason", "masks_a_negative"]
    assert "evidenced_negative_sources" not in plain_summary


def test_phenopacket_exclusions_become_evidenced_negatives_and_k_of_n_a_frequency(tmp_path: Path):
    _, evidence_directory = write_graph_and_evidence(tmp_path)
    counts = write_counts(tmp_path / "counts.parquet")
    _, plain, _ = build(tmp_path, evidence_directory, "plain", "--mask-grades", "C")
    _, annotated, _ = build(tmp_path, evidence_directory, "annotated", "--mask-grades", "C", "--phenopacket-counts", str(counts))
    assert annotated.keep.tolist() == plain.keep.tolist()  # the counts alone change nothing
    assert annotated.set_index(["perturbation_id", "symptom"]).loc[("GENEA", "anxiety"), INDIVIDUALS_ASSESSED_COLUMN] == 5
    _, selection, summary = build(tmp_path, evidence_directory, "negatives", "--mask-grades", "C", "--phenopacket-counts", str(counts),
                                  "--phenopacket-exclusions-as-negative", "--phenopacket-frequency")
    negatives = selection[selection.counts_as_negative]
    # GENEB insomnia has a grade C positive record; GENEB hyperactivity an observation in a carved-out descendant
    assert sorted(zip(negatives.perturbation_id, negatives.symptom)) == [("GENEA", "depressed_mood")]
    assert negatives.evidenced_negative_source.tolist() == ["Phenopacket-Store"] and not negatives.keep.any()
    geneb = selection.set_index(["perturbation_id", "symptom"]).loc[("GENEB", "anxiety")]
    assert geneb.label_frequency == pytest.approx(0.25) and not geneb.keep and "Phenopacket Store frequency 1 of 4" in geneb.reason
    report = summary["evidenced_negative_sources"]["phenopacket"]
    assert report["exclusions_as_negative"]["evidenced_negatives"] == 1
    assert report["exclusions_as_negative"]["of_them_contradicting_a_positive_record"] == 1  # GENEB insomnia
    assert report["frequency"] == {"gene_pairs_without_an_hpo_frequency_given_one": 1, "of_them_kept": 0, "of_them_set_aside": 1}


def test_statin_trial_negatives_relabel_a_positive_and_extrapolation_needs_its_own_flag(tmp_path: Path):
    _, evidence_directory = write_graph_and_evidence(tmp_path)
    table = statin_table(tmp_path / "statins.csv")
    _, selection, summary = build(tmp_path, evidence_directory, "statins", "--mask-grades", "C", "--statin-trial-negatives-as-negative", "--statin-trial-negatives", str(table))
    by_pair = selection.set_index(["perturbation_id", "symptom"])
    assert by_pair.loc[("CID100002250", "depressed_mood"), "counts_as_negative"] and not by_pair.loc[("CID100002250", "depressed_mood"), "keep"]
    assert by_pair.loc[("CID100002250", "insomnia"), "meta_analysis_participants"] == 123940
    assert ("CID100132804", "insomnia") not in by_pair.index  # pitavastatin was in none of the trials
    statins = summary["evidenced_negative_sources"]["statin_trials"]
    assert statins["label_positives_relabelled"] == ["atorvastatin depressed_mood"] and statins["rows_added_for_unlabelled_pairs"] == ["atorvastatin insomnia"]
    _, extrapolated, _ = build(tmp_path, evidence_directory, "extrapolated", "--mask-grades", "C", "--statin-trial-negatives-as-negative",
                               "--statin-trial-negatives", str(table), "--admit-class-extrapolation")
    assert ("CID100132804", "insomnia") in set(zip(extrapolated.perturbation_id, extrapolated.symptom))
    refused = subprocess.run([sys.executable, "experiments/build_label_selection.py", "--evidence-dir", str(evidence_directory), "--output", str(tmp_path / "x.parquet"),
                              "--phenopacket-exclusions-as-negative"], capture_output=True, text=True)
    assert refused.returncode != 0 and "--phenopacket-counts" in refused.stderr


def test_the_loader_marks_unlabelled_pairs_and_exposes_the_strength_matrices(tmp_path: Path):
    graph_directory, evidence_directory = write_graph_and_evidence(tmp_path)
    counts = write_counts(tmp_path / "counts.parquet")
    table = statin_table(tmp_path / "statins.csv")
    path, _, _ = build(tmp_path, evidence_directory, "both", "--mask-grades", "C", "--phenopacket-counts", str(counts), "--phenopacket-exclusions-as-negative",
                       "--statin-trial-negatives-as-negative", "--statin-trial-negatives", str(table))
    data = load_experiment_data(graph_directory, evidence_directory, label_selection=path, symptoms=["anxiety", "depressed_mood", "insomnia"])
    gene, statin = data.perturbation_ids.index("GENEA"), data.perturbation_ids.index("CID100002250")
    depressed, insomnia, anxiety = (data.symptoms.index(symptom) for symptom in ("depressed_mood", "insomnia", "anxiety"))
    assert data.outcomes[gene, depressed] == 0 and data.label_mask[gene, depressed] and data.evidenced_negative[gene, depressed]
    assert data.evidenced_negative_source[gene, depressed] == "Phenopacket-Store"
    assert data.phenopacket_individuals_assessed[gene, depressed] == 4 and data.phenopacket_individuals_observed[gene, anxiety] == 3
    assert data.outcomes[statin, depressed] == 0 and data.evidenced_negative[statin, depressed]  # relabelled positive
    assert data.evidenced_negative[statin, insomnia] and data.meta_analysis_rate_ratio_upper_95[statin, insomnia] == pytest.approx(1.07)
    assert np.isnan(data.meta_analysis_participants[gene, depressed])
    summary = data.label_selection_summary
    assert summary["unlabelled_pairs_made_evidenced_negatives"] == 2 and summary["positive_pairs_relabelled_as_negatives"] == 1
    assert summary["evidenced_negatives_by_source"] == {"CTT-statin-placebo-trials-2026": 2, "Phenopacket-Store": 1}
    restricted = restrict_to_perturbations(data, np.array([perturbation_id == "GENEA" for perturbation_id in data.perturbation_ids]))
    for name in EVIDENCED_NEGATIVE_ARRAYS:
        assert getattr(restricted, name).shape[0] == 1
    plain = load_experiment_data(graph_directory, evidence_directory, label_selection=build(tmp_path, evidence_directory, "plain", "--mask-grades", "C")[0])
    assert all(getattr(plain, name) is None for name in EVIDENCED_NEGATIVE_ARRAYS)
    assert "unlabelled_pairs_made_evidenced_negatives" not in plain.label_selection_summary


def test_a_counts_as_negative_row_without_a_source_still_needs_a_positive(tmp_path: Path):
    """The never-above-placebo rows name no source and, as before, act on a positive only."""
    graph_directory, evidence_directory = write_graph_and_evidence(tmp_path)
    selection = tmp_path / "selection.parquet"
    pd.DataFrame({"perturbation_id": ["GENEA"], "symptom": ["depressed_mood"], "perturbation_type": ["gene"], "label_frequency": [float("nan")],
                  "keep": [False], "reason": ["x"], "counts_as_negative": [True]}).to_parquet(selection)
    data = load_experiment_data(graph_directory, evidence_directory, label_selection=selection, symptoms=["anxiety", "depressed_mood"])
    assert not data.evidenced_negative.any() and data.label_selection_summary["selection_rows_not_matching_a_positive"] == 1


def test_the_curated_statin_table_and_the_minimum_ages_cover_what_they_must():
    table = pd.read_csv("configs/statin_trial_negatives.csv", dtype={"pmid": str})
    assert set(table.symptom) == {"cognitive_impairment", "depressed_mood", "insomnia"} and (table.pmid == "41655587").all()
    assert set(table[table.in_the_trials].drug) == {"atorvastatin", "lovastatin", "pravastatin", "rosuvastatin", "simvastatin"}
    assert ((table.rate_ratio_lower_95 < 1) & (table.rate_ratio_upper_95 > 1)).all()  # every interval spans no effect
    ages = pd.read_csv("configs/symptom_minimum_assessment_age.csv")
    names = set(pd.read_csv("docs/symptom_crosswalk.csv").target_symptom) | set(pd.read_csv("docs/symptom_crosswalk_fine.csv").target_symptom)
    assert names <= set(ages.target_symptom) and (ages.minimum_age_years >= 3).all() and ages.quote.notna().all()


def test_the_trial_arm_measurement_reads_the_cache_only_and_splits_absences_by_assessment(tmp_path: Path):
    from experiments.measure_label_negative_sources import measure_trial_arms
    from tests.test_clinical_trial_adverse_events import event, study

    evidence_directory, cache = tmp_path / "evidence", tmp_path / "cache"
    evidence_directory.mkdir()
    cache.mkdir()
    pd.DataFrame([{"perturbation_id": "CID1", "perturbation_type": "drug", "perturbation_label": "examplone", "perturbation_nodes": "[]",
                   "model_description": "human; drug label; ChEMBL targets CHEMBL1:ANTAGONIST"},
                  {"perturbation_id": "CID2", "perturbation_type": "drug", "perturbation_label": "uncachedol", "perturbation_nodes": "[]",
                   "model_description": "human; drug label; ChEMBL targets CHEMBL2:AGONIST"}]).to_parquet(evidence_directory / "evidence_reports.parquet")
    crosswalk = tmp_path / "crosswalk.csv"
    crosswalk.write_text("target_symptom,meddra_preferred_terms\ninsomnia,Insomnia\nanxiety,Anxiety\nsomnolence_or_hypersomnia,Somnolence\n")
    trial = study("NCT30", [("EG0", "Examplone"), ("EG1", "Placebo")],
                  [event("Insomnia", {"EG0": (2, 200), "EG1": (6, 200)}, assessment="SYSTEMATIC_ASSESSMENT"),
                   event("Anxiety", {"EG0": (3, 200), "EG1": (5, 200)}, assessment="NON_SYSTEMATIC_ASSESSMENT"),
                   event("Somnolence", {"EG0": (9, 200), "EG1": (2, 200)}, assessment="NON_SYSTEMATIC_ASSESSMENT")])
    (cache / "examplone.json").write_text(json.dumps({"drug": "examplone", "studies": [trial]}))
    result = measure_trial_arms(cache, evidence_directory, crosswalk, tmp_path / "no_sider", kept={("CID1", "anxiety")}, lockbox_perturbations=set())
    assert result["drugs_without_a_cache_file"] == ["uncachedol"]
    assert (result["absence_reports_before_filter"], result["absence_reports_after_filter"]) == (2, 1)
    assert result["absence_reports_by_assessment_type"] == {"SYSTEMATIC_ASSESSMENT": 1, "NON_SYSTEMATIC_ASSESSMENT": 1}
    check = result["development_label_check"]
    assert check["absence_pairs"] == {"pairs": 2, "label_positive": 1, "percent": 50.0}
    assert check["absence_pairs_not_systematically_assessed"] == {"pairs": 1, "label_positive": 1, "percent": 100.0}
