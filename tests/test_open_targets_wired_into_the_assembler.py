"""Decision 8.5, built 14 October 2026 on option (a), after the effect was measured rather than assumed.

8.5 and amendment item 12d are the same item: `reliability_reports` was written for the owner's instruction "add
it to the Dawid-Skene fit estimates" and `assemble_evidence_table.py` never called it, so the decision of 13
October was unbuilt. What these tests pin is the property that makes the wiring safe - the class changes a weight
through the reliability fit and creates no label - and the one guard that option (a) leaves inactive.
"""
import inspect


from mechanistic_pathway_learning.evidence import assemble_evidence_table
from mechanistic_pathway_learning.evidence.load_open_targets_statements import (
    CuratedStatement,
    perturbations_of_target_by_direction,
    reliability_reports,
)

EXISTING_ITEM = ("GRIN1", "psychosis", "induces")
PERTURBATION_OF_TARGET = {("GRIN1", "inhibition"): "GRIN1"}


def a_statement(target: str, direction: str, symptom: str) -> CuratedStatement:
    return CuratedStatement(target, direction, symptom, f"{direction} of {target}", "pmid:1")


def test_the_assembler_takes_the_scoped_rows_path_so_the_class_can_reach_the_fit():
    """The wiring 8.5 was about: the loader existed, was tested, and had no caller."""
    assert "open_targets_scoped_rows_path" in inspect.signature(assemble_evidence_table.assemble).parameters


def test_the_assembler_imports_the_loader_it_had_never_called():
    assert hasattr(assemble_evidence_table, "reliability_reports")
    assert hasattr(assemble_evidence_table, "human_worded_statements")


def test_a_report_is_emitted_only_for_an_item_that_already_carries_a_positive_report():
    """The load-bearing guard, and the one that is active. Without it a target-safety statement could turn a
    documented absence into a trained and scored positive."""
    on_an_existing_positive = reliability_reports([a_statement("GRIN1", "inhibition", "psychosis")],
                                                 {EXISTING_ITEM}, PERTURBATION_OF_TARGET)
    assert len(on_an_existing_positive) == 1
    on_an_item_with_no_positive = reliability_reports([a_statement("GRIN1", "inhibition", "psychosis")],
                                                      set(), PERTURBATION_OF_TARGET)
    assert on_an_item_with_no_positive == []


def test_a_statement_about_a_target_that_is_not_a_perturbation_emits_nothing():
    assert reliability_reports([a_statement("CHRM1", "inhibition", "psychosis")],
                               {EXISTING_ITEM}, PERTURBATION_OF_TARGET) == []


def test_the_evidenced_negative_guard_still_works_when_a_caller_can_supply_the_set():
    """Option (a) leaves this inactive inside assemble(), because the set is computed downstream. The guard itself
    is intact, so a later caller that has the set can use it - which is what option (b) would have been."""
    skipped = reliability_reports([a_statement("GRIN1", "inhibition", "psychosis")], {EXISTING_ITEM},
                                  PERTURBATION_OF_TARGET, evidenced_negative_pairs={("GRIN1", "psychosis")})
    assert skipped == []


def test_the_emitted_report_names_the_class_and_carries_a_positive_value():
    report = reliability_reports([a_statement("GRIN1", "inhibition", "psychosis")],
                                 {EXISTING_ITEM}, PERTURBATION_OF_TARGET)[0]
    assert report["report_value"] == 1
    assert "Open Targets" in report["source"]
    assert report["perturbation_id"] == "GRIN1"
    assert report["symptom"] == "psychosis"


def test_the_comment_on_the_inactive_guard_states_the_measurement_of_14_october_as_dated_history():
    """The comment beside the inactive guard justifies it by the measurement of 14 October 2026, taken when every
    statement joined the bare gene symbol. Since the direction join of 24 November 2026 that count is not what the
    class emits, so the comment states it in the past tense with its date (CLAUDE.md, Code: history is kept only when
    it is framed as history, with a date)."""
    comment_lines_of_assemble = [line.strip()[1:].strip() for line in inspect.getsource(assemble_evidence_table.assemble).splitlines()
                                 if line.strip().startswith("#")]
    comments_of_assemble_as_one_text = " ".join(comment_lines_of_assemble)  # a phrase wrapped over two lines reads whole
    assert "the class emits 14 reports" not in comments_of_assemble_as_one_text
    assert "Measured before choosing, on 14 October 2026" in comments_of_assemble_as_one_text
    assert "the class emitted 14 reports" in comments_of_assemble_as_one_text


def test_of_the_four_items_the_guard_comment_names_only_the_inhibition_statement_joins_without_the_gain_of_function_allele():
    """What the comment says the direction join did to the four items of 14 October: GABRA1 depressed_mood, HTR2A
    cognitive_impairment and HTR2A psychosis are activation statements in the curation, so on a table without the
    `<gene>|gain_of_function` allele (every table built without --allele-perturbations) they join nothing, and SLC6A4
    anxiety, an inhibition statement, still joins the bare gene."""
    import pandas as pd
    from mechanistic_pathway_learning.evidence.load_open_targets_statements import FINE_CONSTRUCT_MAP_PATH

    items_named_in_the_comment = {("GABRA1", "depressed_mood"), ("HTR2A", "cognitive_impairment"),
                                  ("HTR2A", "psychosis"), ("SLC6A4", "anxiety")}
    curated_rows = pd.read_csv(FINE_CONSTRUCT_MAP_PATH, dtype=str)
    statements_of_the_named_items = [a_statement(row.target, row.direction, row.coarse_symptom)
                                     for row in curated_rows.itertuples()
                                     if (row.target, row.coarse_symptom) in items_named_in_the_comment]
    assert sorted((statement.target, statement.symptom, statement.direction) for statement in statements_of_the_named_items) == [
        ("GABRA1", "depressed_mood", "activation"), ("HTR2A", "cognitive_impairment", "activation"),
        ("HTR2A", "psychosis", "activation"), ("SLC6A4", "anxiety", "inhibition")]
    joins_without_a_gain_of_function_allele = perturbations_of_target_by_direction({"GABRA1", "HTR2A", "SLC6A4"})
    items_with_a_positive_report = {(target, symptom, "induces") for target, symptom in items_named_in_the_comment}
    reports = reliability_reports(statements_of_the_named_items, items_with_a_positive_report,
                                  joins_without_a_gain_of_function_allele)
    assert [(report["perturbation_id"], report["symptom"]) for report in reports] == [("SLC6A4", "anxiety")]


def test_each_direction_joins_the_allele_that_moves_the_target_the_same_way():
    """The owner, 24 November 2026: "1 yes please fix", on joining inhibition statements to the loss-of-function
    allele and activation statements to the gain-of-function allele. Before, both joined the bare gene symbol, so
    an activation statement attached to the gene's loss of function."""
    joins = perturbations_of_target_by_direction({"GRIN1", "GRIN1|gain_of_function", "HTR2C"})
    assert joins[("GRIN1", "inhibition")] == "GRIN1"
    assert joins[("GRIN1", "activation")] == "GRIN1|gain_of_function"
    assert ("HTR2C", "activation") not in joins  # no gain-of-function allele, so nothing to join
    activation_item = ("GRIN1|gain_of_function", "psychosis", "induces")
    activation = reliability_reports([a_statement("GRIN1", "activation", "psychosis")],
                                     {EXISTING_ITEM, activation_item}, joins)
    assert [report["perturbation_id"] for report in activation] == ["GRIN1|gain_of_function"]
    assert reliability_reports([a_statement("HTR2C", "activation", "psychosis")],
                               {("HTR2C", "psychosis", "induces")}, joins) == []


def test_a_curated_allele_other_than_gain_of_function_joins_no_statement():
    """A neomorph or any other "<gene>|..." allele does what its own mechanism edges say, not more or less of the
    gene's normal activity, so neither direction of a target-level statement describes it."""
    joins = perturbations_of_target_by_direction({"HTT|polyglutamine_expansion"})
    assert joins == {}


def test_a_fine_construct_table_moves_each_statement_to_the_constructs_its_wording_names():
    """Decision 8.5, the owner, 24 November 2026: "Use a: Map statements by curated wording to fine constructs"."""
    mapping = {("GRIN1", "inhibition", "psychosis"): ("psychosis", "hallucinations")}
    items = {("GRIN1", "psychosis", "induces"), ("GRIN1", "hallucinations", "induces")}
    reports = reliability_reports([a_statement("GRIN1", "inhibition", "psychosis")], items, PERTURBATION_OF_TARGET,
                                  fine_constructs_of_statement=mapping)
    assert sorted(report["symptom"] for report in reports) == ["hallucinations", "psychosis"]
    assert len({report["report_id"] for report in reports}) == 2  # one statement, two constructs, two distinct ids
    assert {report["source_term_id"] for report in reports} == {"psychosis"}  # the statement's own coarse symptom


def test_a_statement_missing_from_the_fine_construct_map_is_an_error_not_a_silent_namesake():
    import pytest
    with pytest.raises(KeyError):
        reliability_reports([a_statement("GRIN1", "inhibition", "psychosis")], {EXISTING_ITEM}, PERTURBATION_OF_TARGET,
                            fine_constructs_of_statement={})


def test_the_registered_fine_construct_map_names_only_fine_constructs_and_carries_the_owners_rulings():
    import pandas as pd
    from mechanistic_pathway_learning.evidence.load_open_targets_statements import load_fine_construct_map
    mapping = load_fine_construct_map()
    assert len(mapping) == 111  # the statements docs/generated/open_targets_reliability_effect.json counts
    fine_constructs = set(pd.read_csv("docs/symptom_crosswalk_fine.csv").target_symptom)
    assert all(constructs and set(constructs) <= fine_constructs for constructs in mapping.values())
    assert mapping[("ADORA2A", "inhibition", "psychomotor_agitation")] == ("agitation", "anxiety")  # "3 add anxiety"
    assert mapping[("DRD1", "inhibition", "suicidality")] == ("suicidal_ideation",)
    assert mapping[("DRD1", "inhibition", "parkinsonism")] == ("parkinsonism",)
