"""The fine symptom constructs derived from the coarse crosswalk (evidence/symptom_constructs.py, decision 9.58)."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments.build_fine_symptom_crosswalk import complete_addition, render  # noqa: E402
from mechanistic_pathway_learning.evidence.symptom_constructs import (  # noqa: E402
    FINE_COLUMNS,
    IMPC_COLUMNS,
    HpoVocabulary,
    assign_term,
    build_fine_crosswalk,
    coarse_of_fine,
    annotate_extra_roots,
    fine_constructs_of,
    fine_impc_rows,
    phrase,
    read_extra_roots,
    read_rows,
    read_term_overrides,
    slug,
    split_cell,
    stems,
    with_extra_roots,
    write_rows,
)

OBO = """format-version: 1.2

[Term]
id: HP:0000001
name: All

[Term]
id: HP:0000709
name: Psychosis
synonym: "Psychotic episodes" EXACT []
is_a: HP:0000001 ! All

[Term]
id: HP:0000738
name: Hallucinations
synonym: "Hallucination" EXACT layperson []
is_a: HP:0000709 ! Psychosis

[Term]
id: HP:0000746
name: Delusion
synonym: "Delusions" EXACT layperson []
is_a: HP:0000709 ! Psychosis

[Term]
id: HP:0008765
name: Visual hallucinations
synonym: "Hallucination, visual" EXACT []
is_a: HP:0000738 ! Hallucinations

[Term]
id: HP:0000713
name: Agitation
is_a: HP:0000001 ! All

[Term]
id: HP:0000711
name: Restlessness
synonym: "Motor restlessness" EXACT []
is_a: HP:0000001 ! All

[Term]
id: HP:0001249
name: Intellectual disability
synonym: "Low intelligence" RELATED []
is_a: HP:0000001 ! All

[Term]
id: HP:9999999
name: Obsolete thing
is_obsolete: true
"""


def coarse_rows():
    return [
        {"target_symptom": "psychosis", "hpo_ids": "HP:0000709;HP:0000738;HP:0000746", "hpo_names": "Psychosis;Hallucinations;Delusion", "excluded_hpo_ids": "",
         "meddra_preferred_terms": "Psychotic disorder;Hallucination;Delusion;Hallucination, visual;Acute psychosis", "questionnaire_item": "", "rdoc_domain": "perception",
         "identifier_status": "verified", "notes": "four roots", "mesh_descriptors": "D011618", "mesh_descriptor_level": "diagnosis"},
        {"target_symptom": "psychomotor_agitation", "hpo_ids": "HP:0000713;HP:0000711", "hpo_names": "Agitation;Restlessness", "excluded_hpo_ids": "",
         "meddra_preferred_terms": "Agitation;Restlessness;Akathisia", "questionnaire_item": "PHQ-9 item 8", "rdoc_domain": "arousal", "identifier_status": "verified",
         "notes": "", "mesh_descriptors": "", "mesh_descriptor_level": ""},
        {"target_symptom": "anxiety", "hpo_ids": "HP:0000739", "hpo_names": "Anxiety", "excluded_hpo_ids": "", "meddra_preferred_terms": "Anxiety;Nervousness",
         "questionnaire_item": "GAD-7", "rdoc_domain": "negative_valence", "identifier_status": "verified", "notes": "one root", "mesh_descriptors": "D001007",
         "mesh_descriptor_level": "symptom"},
        {"target_symptom": "catatonia", "hpo_ids": "", "hpo_names": "", "excluded_hpo_ids": "", "meddra_preferred_terms": "Catatonia", "questionnaire_item": "",
         "rdoc_domain": "", "identifier_status": "", "notes": "no HPO root", "mesh_descriptors": "", "mesh_descriptor_level": ""},
    ]


@pytest.fixture
def vocabulary(tmp_path):
    obo = tmp_path / "hp.obo"
    obo.write_text(OBO, encoding="utf-8")
    return HpoVocabulary.from_obo(obo)


def test_slugs_stems_and_phrases_normalise_spelling_plurals_and_word_order():
    assert slug("Pill-rolling tremor") == "pill_rolling_tremor" and slug("  Aggressive behavior ") == "aggressive_behavior"
    assert stems("Suicidal behaviour") == {"suicid"} and stems("Suicidal behaviour", keep_stop_words=True) == {"suicid", "behavior"}
    assert phrase("Hallucination, visual") == phrase("Visual hallucinations")


def test_a_fused_row_splits_at_its_roots_and_a_single_root_row_keeps_its_name():
    psychosis, agitation, anxiety, catatonia = (fine_constructs_of(row) for row in coarse_rows())
    assert [construct.name for construct in psychosis] == ["psychosis", "hallucinations", "delusion"]
    assert [construct.is_namesake for construct in psychosis] == [True, False, False], "the root whose name slugs to the coarse name is the namesake"
    assert [construct.name for construct in agitation] == ["agitation", "restlessness"] and agitation[0].is_namesake, "no root slugs to the coarse name, so the first is"
    assert [(construct.name, construct.hpo_id) for construct in anxiety] == [("anxiety", "HP:0000739")]
    assert [(construct.name, construct.hpo_id) for construct in catatonia] == [("catatonia", "")]
    with pytest.raises(ValueError, match="hpo_names"):
        fine_constructs_of({"target_symptom": "x", "hpo_ids": "HP:1;HP:2", "hpo_names": "One"})


def test_the_vocabulary_reads_names_synonyms_and_descendants_and_drops_obsolete_terms(vocabulary):
    assert vocabulary.names_by_term["HP:0000738"] == "Hallucinations" and "HP:9999999" not in vocabulary.parents_by_term
    phrases = vocabulary.phrases_of("HP:0000738", [])
    assert phrase("Hallucination, visual") in phrases and phrase("Visual hallucinations") in phrases and phrase("Delusion") not in phrases
    assert phrase("Visual hallucinations") not in vocabulary.phrases_of("HP:0000738", ["HP:0008765"]), "an excluded descendant leaves the construct's vocabulary"
    assert "episod" in vocabulary.root_stems_of("HP:0000709")
    assert vocabulary.ancestors_of("HP:0008765") == {"HP:0000738", "HP:0000709", "HP:0000001"} and vocabulary.ancestors_of("HP:0000001") == set()


def test_terms_are_assigned_by_override_then_vocabulary_then_stems_then_namesake(vocabulary):
    constructs = fine_constructs_of(coarse_rows()[0])
    assert assign_term("Hallucination, visual", constructs, {}, vocabulary) == ("hallucinations", "hpo vocabulary"), "a descendant's synonym, in another word order"
    assert assign_term("Delusion", constructs, {}, vocabulary) == ("delusion", "hpo vocabulary")
    assert assign_term("Acute psychosis", constructs, {}, vocabulary) == ("psychosis", "stem match")
    assert assign_term("Psychotic disorder", constructs, {}, vocabulary) == ("psychosis", "stem match"), "through the root's synonym 'Psychotic episodes'"
    assert assign_term("Unrelated term", constructs, {}, vocabulary) == ("psychosis", "namesake")
    assert assign_term("Psychotic disorder", constructs, {"psychotic disorder": "delusion"}, vocabulary) == ("delusion", "override")
    with pytest.raises(ValueError, match="not a construct"):
        assign_term("Psychotic disorder", constructs, {"psychotic disorder": "anxiety"}, vocabulary)
    assert assign_term("Anxiety", fine_constructs_of(coarse_rows()[2]), {}, vocabulary) == ("anxiety", "single construct")


def test_the_fine_crosswalk_carries_terms_apart_keeps_mesh_with_the_namesake_and_adds_constructs(vocabulary):
    additions = [complete_addition({"target_symptom": "intellectual_disability", "hpo_ids": "HP:0001249", "rdoc_domain": "cognitive_systems", "mesh_descriptors": "D008607",
                                    "mesh_descriptor_level": "diagnosis", "notes": "added"}, vocabulary, ["Intellectual disability", "Low intelligence", "Anxiety"])]
    rows, assignments = build_fine_crosswalk(coarse_rows(), additions, {"akathisia": "restlessness"}, vocabulary)
    by_name = {row["target_symptom"]: row for row in rows}
    assert list(by_name) == ["psychosis", "hallucinations", "delusion", "agitation", "restlessness", "anxiety", "catatonia", "intellectual_disability"]
    assert by_name["hallucinations"]["meddra_preferred_terms"] == "Hallucination;Hallucination, visual" and by_name["delusion"]["meddra_preferred_terms"] == "Delusion"
    assert by_name["psychosis"]["meddra_preferred_terms"] == "Psychotic disorder;Acute psychosis"
    assert by_name["psychosis"]["mesh_descriptors"] == "D011618" and by_name["hallucinations"]["mesh_descriptors"] == "", "MeSH stays with the namesake"
    assert by_name["psychosis"]["excluded_hpo_ids"] == "HP:0000738;HP:0000746", "the parent root excludes the sibling roots that descend from it"
    assert by_name["hallucinations"]["excluded_hpo_ids"] == ""
    assert by_name["agitation"]["questionnaire_item"] == "PHQ-9 item 8" and by_name["restlessness"]["questionnaire_item"] == ""
    assert by_name["restlessness"]["meddra_preferred_terms"] == "Restlessness;Akathisia", "the override moved Akathisia"
    assert by_name["anxiety"]["notes"] == "one root" and by_name["hallucinations"]["notes"].startswith("derived from psychosis")
    assert by_name["intellectual_disability"]["hpo_names"] == "Intellectual disability"
    assert by_name["intellectual_disability"]["meddra_preferred_terms"] == "Intellectual disability;Low intelligence", "the preferred terms whose words the ontology uses"
    assert coarse_of_fine(rows)["delusion"] == "psychosis" and coarse_of_fine(rows)["intellectual_disability"] == "intellectual_disability"
    assert {assignment["how"] for assignment in assignments} == {"hpo vocabulary", "override", "stem match", "single construct"}
    with pytest.raises(ValueError, match="named twice"):
        build_fine_crosswalk(coarse_rows() + [coarse_rows()[2]], [], {}, vocabulary)


def test_a_row_kept_together_stays_one_fine_construct_holding_every_root(vocabulary, tmp_path):
    from mechanistic_pathway_learning.evidence.symptom_constructs import read_kept_together
    agitation_row = coarse_rows()[1]
    assert [construct.name for construct in fine_constructs_of(agitation_row, set())] == ["agitation", "restlessness"]
    (kept,) = fine_constructs_of(agitation_row, {"psychomotor_agitation"})
    assert (kept.name, kept.coarse, kept.hpo_id, kept.hpo_name, kept.is_namesake) == ("psychomotor_agitation", "psychomotor_agitation", "HP:0000713;HP:0000711", "Agitation;Restlessness", True)
    assert [construct.name for construct in fine_constructs_of(agitation_row)] == ["agitation", "restlessness"], "the committed table does not name this row"
    with open(tmp_path / "kept.csv", "w", newline="") as handle:
        handle.write("coarse_symptom,date,note\npsychomotor_agitation,2026-11-24,one phenomenon\n")
    assert [row["coarse_symptom"] for row in read_kept_together(tmp_path / "kept.csv")] == ["psychomotor_agitation"] and read_kept_together(tmp_path / "missing.csv") == []
    with open(tmp_path / "unreasoned.csv", "w", newline="") as handle:
        handle.write("coarse_symptom,date,note\npsychomotor_agitation,2026-11-24,\n")
    with pytest.raises(ValueError, match="missing note"):
        read_kept_together(tmp_path / "unreasoned.csv")
    page = render("stamp", [{column: "" for column in FINE_COLUMNS} | {"target_symptom": "psychomotor_agitation", "coarse_symptom": "psychomotor_agitation",
                                                                         "hpo_ids": "HP:0000713;HP:0000711", "hpo_names": "Agitation;Restlessness"}], [], [],
                  kept_together=[{"coarse_symptom": "psychomotor_agitation", "date": "2026-11-24", "note": "one phenomenon"}])
    assert "## Constructs whose roots are kept together" in page and "| psychomotor_agitation | HP:0000713; HP:0000711 Agitation; Restlessness | 2026-11-24 | one phenomenon |" in page
    assert "## Constructs whose roots are kept together" not in render("stamp", [], [], [])


def test_the_committed_crosswalk_keeps_both_dream_terms_in_abnormal_dreams():
    """The owner, 24 November 2026, on leaving HP:0032938 out as a term defined by its cause: "why not map to nightmares?"."""
    for name in ("docs/symptom_crosswalk.csv", "docs/symptom_crosswalk_fine.csv"):
        row = {row["target_symptom"]: row for row in read_rows(ROOT / name)}["abnormal_dreams"]
        assert row["hpo_ids"] == "HP:5200287;HP:0032938" and row["meddra_preferred_terms"] == "Abnormal dreams;Nightmare", name
        assert row["hpo_names"] == "Recurrent distressing nightmares;Recurrent trauma-related distressing dreams", name


def test_an_override_moves_a_mesh_descriptor_with_its_level_from_the_namesake(vocabulary):
    from mechanistic_pathway_learning.evidence.symptom_constructs import fine_construct_of_descriptor
    coarse = coarse_rows()
    coarse[0]["mesh_descriptors"], coarse[0]["mesh_descriptor_level"] = "D011618;D006212", "diagnosis;symptom"
    rows, assignments = build_fine_crosswalk(coarse, [], {"d006212": "hallucinations"}, vocabulary)
    by_name = {row["target_symptom"]: row for row in rows}
    assert (by_name["psychosis"]["mesh_descriptors"], by_name["psychosis"]["mesh_descriptor_level"]) == ("D011618", "diagnosis")
    assert (by_name["hallucinations"]["mesh_descriptors"], by_name["hallucinations"]["mesh_descriptor_level"]) == ("D006212", "symptom")
    assert by_name["delusion"]["mesh_descriptors"] == "" and by_name["anxiety"]["mesh_descriptors"] == "D001007"
    assert {"coarse_symptom": "psychosis", "term": "D006212", "kind": "mesh", "fine_construct": "hallucinations", "how": "override"} in assignments
    assert fine_construct_of_descriptor(coarse, {"d006212": "hallucinations"}) == {"D011618": "psychosis", "D006212": "hallucinations", "D001007": "anxiety"}
    page = render("stamp", rows, assignments, [])
    assert "## MeSH descriptors moved from the namesake" in page and "| psychosis | D006212 | hallucinations |" in page
    assert "## MeSH descriptors moved" not in render("stamp", *build_fine_crosswalk(coarse, [], {}, vocabulary), [])
    with pytest.raises(ValueError, match="not a construct of psychosis"):
        build_fine_crosswalk(coarse, [], {"d006212": "anxiety"}, vocabulary)


def test_the_impc_crosswalk_is_rekeyed_to_the_fine_constructs():
    impc = [
        {"target_symptom": "psychosis", "relation": "induces", "mp_term_ids": "", "mp_term_names": "", "negative_procedure_codes": "", "validity": "endophenotype_only", "note": "never read"},
        {"target_symptom": "psychomotor_agitation", "relation": "induces", "mp_term_ids": "MP:0001399", "mp_term_names": "hyperactivity;restlessness", "negative_procedure_codes": "OFD", "validity": "moderate", "note": ""},
        {"target_symptom": "anxiety", "relation": "induces", "mp_term_ids": "MP:0001363", "mp_term_names": "increased anxiety-related response", "negative_procedure_codes": "OFD", "validity": "strong", "note": ""},
    ]
    rows = fine_impc_rows(impc, coarse_rows(), [{"target_symptom": "intellectual_disability", "hpo_ids": "HP:0001249"}])
    by_key = {(row["target_symptom"], row["relation"]): row for row in rows}
    assert by_key[("psychosis", "induces")]["validity"] == "endophenotype_only" and by_key[("hallucinations", "induces")]["validity"] == "none"
    assert by_key[("restlessness", "induces")]["mp_term_ids"] == "MP:0001399", "the MP term names match restlessness, not agitation"
    assert by_key[("agitation", "induces")]["validity"] == "none" and "restlessness" in by_key[("agitation", "induces")]["note"]
    assert by_key[("anxiety", "induces")]["validity"] == "strong"
    assert by_key[("intellectual_disability", "induces")]["validity"] == "none"
    with pytest.raises(ValueError, match="does not hold"):
        fine_impc_rows([{**impc[0], "target_symptom": "unknown"}], coarse_rows(), [])


def test_rows_round_trip_through_the_writer_and_the_page_lists_every_assignment(tmp_path, vocabulary):
    rows, assignments = build_fine_crosswalk(coarse_rows(), [], {}, vocabulary)
    impc_rows = fine_impc_rows([], coarse_rows(), [])
    write_rows(tmp_path / "fine.csv", rows, FINE_COLUMNS)
    write_rows(tmp_path / "impc.csv", impc_rows, IMPC_COLUMNS)
    assert read_rows(tmp_path / "fine.csv") == [{column: row.get(column, "") for column in FINE_COLUMNS} for row in rows]
    assert read_rows(tmp_path / "impc.csv") == []
    with open(tmp_path / "overrides.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["term", "fine_construct", "note"])
        writer.writerow(["Akathisia", "restlessness", "motor"])
    assert read_term_overrides(tmp_path / "overrides.csv") == {"akathisia": "restlessness"} and read_term_overrides(tmp_path / "missing.csv") == {}
    page = render("stamp", rows, assignments, impc_rows)
    assert "| hallucinations | psychosis | HP:0000738 Hallucinations |" in page and "| psychosis | Hallucination, visual | hallucinations | hpo vocabulary |" in page
    assert "7 fine constructs from 4 coarse ones" in page and "Counts:" in page


def test_the_committed_fine_crosswalk_is_a_fresh_build_of_the_committed_inputs():
    """The two derived crosswalk files, the fine one and the IMPC one, are generated: a change to the coarse crosswalk, the
    coarse IMPC crosswalk, the additions or the overrides without a rerun fails here (--check has compared the IMPC file
    too since 28 November 2026; the next test holds that without hp.obo). The page is not compared."""
    import subprocess
    root = Path(__file__).resolve().parents[1]
    required_raw_inputs = ("data/raw/hpo/hp.obo", "data/raw/sider_4.1/meddra_all_se.tsv.gz")  # HPO; SIDER's vocabulary
    missing_raw_inputs = [path for path in required_raw_inputs if not (root / path).exists()]
    if missing_raw_inputs:
        pytest.skip(f"not fetched: {', '.join(missing_raw_inputs)}")
    result = subprocess.run([sys.executable, "experiments/build_fine_symptom_crosswalk.py", "--check"], cwd=root, capture_output=True, text=True, env={"PYTHONPATH": ".", "PATH": "/usr/bin:/bin:/usr/local/bin"})
    assert result.returncode == 0, result.stdout + result.stderr
    fine = read_rows(root / "docs/symptom_crosswalk_fine.csv")
    coarse = read_rows(root / "docs/symptom_crosswalk.csv")
    extra_roots = read_rows(root / "configs/fine_construct_extra_roots.csv")
    additions = {row["target_symptom"] for row in read_rows(root / "configs/symptom_construct_additions.csv")}
    assert {"intellectual_disability", "tardive_dyskinesia", "orofacial_dyskinesia", "extrapyramidal_dyskinesia"} <= additions  # 9.58, 9.115, 9.116
    kept_together = {row["coarse_symptom"] for row in read_rows(root / "configs/fine_construct_kept_together.csv")}
    assert kept_together == {"abnormal_dreams"}, "a row here is an exception to one construct per root and needs the owner's ruling"
    assert len(fine) == sum(1 if row["target_symptom"] in kept_together else max(1, len([part for part in row["hpo_ids"].split(";") if part]))
                            for row in coarse) + len(additions) + len(extra_roots)
    assert {row["coarse_symptom"] for row in fine} == {row["target_symptom"] for row in coarse} | additions


def test_the_check_fails_when_either_crosswalk_file_alone_is_stale(monkeypatch, tmp_path, capsys):
    """An override keyed by an MP term id moves a row of the IMPC file alone, so --check must fail on a stale IMPC file
    beside a current fine one; until 28 November 2026 it compared the fine file only. A stale fine file beside a current
    IMPC one fails as well. The build is replaced by fixed rows and every path by a file under tmp_path, so neither
    hp.obo nor a committed file is read."""
    import experiments.build_fine_symptom_crosswalk as fine_builder
    fresh_fine_rows = [{column: f"{column} of the fresh build" for column in FINE_COLUMNS}]
    fresh_impc_rows = [{column: f"{column} of the fresh build" for column in IMPC_COLUMNS}]
    fine_path, impc_path, coarse_path = tmp_path / "fine.csv", tmp_path / "impc_fine.csv", tmp_path / "coarse.csv"
    write_rows(coarse_path, [], fine_builder.CROSSWALK_COLUMNS)
    write_rows(fine_path, fresh_fine_rows, FINE_COLUMNS)
    write_rows(impc_path, [{**fresh_impc_rows[0], "validity": "a validity no rerun wrote"}], IMPC_COLUMNS)
    monkeypatch.setattr(fine_builder, "FINE_CROSSWALK_PATH", fine_path)
    monkeypatch.setattr(fine_builder, "IMPC_FINE_PATH", impc_path)
    monkeypatch.setattr(fine_builder, "COARSE_CROSSWALK_PATH", coarse_path)
    monkeypatch.setattr(fine_builder, "build", lambda obo, sider: (fresh_fine_rows, [], fresh_impc_rows, []))
    monkeypatch.setattr(fine_builder, "HpoVocabulary", type("NoVocabulary", (), {"from_obo": staticmethod(lambda obo: None)}))
    monkeypatch.setattr(fine_builder, "checked_kept_together", lambda coarse_rows, vocabulary: [])
    monkeypatch.setattr(sys, "argv", ["build_fine_symptom_crosswalk.py", "--check"])

    assert fine_builder.main() == 1
    printed = capsys.readouterr().out
    assert f"{impc_path} differs from a fresh build" in printed and f"{fine_path} differs" not in printed
    write_rows(impc_path, fresh_impc_rows, IMPC_COLUMNS)
    assert fine_builder.main() == 0
    assert "are current" in capsys.readouterr().out
    # and the other way round, which the hp.obo test above holds only where hp.obo is fetched
    write_rows(fine_path, [{**fresh_fine_rows[0], "hpo_ids": "an HPO id no rerun wrote"}], FINE_COLUMNS)
    assert fine_builder.main() == 1
    printed = capsys.readouterr().out
    assert f"{fine_path} differs from a fresh build" in printed and f"{impc_path} differs" not in printed


def test_the_literature_table_is_rekeyed_to_the_namesakes_without_a_row_moving():
    import pandas as pd
    from mechanistic_pathway_learning.evidence.symptom_constructs import namesake_of_coarse
    from experiments.rekey_literature_to_fine import rekey
    namesake = namesake_of_coarse(coarse_rows())
    assert namesake == {"psychosis": "psychosis", "psychomotor_agitation": "agitation", "anxiety": "anxiety", "catatonia": "catatonia"}
    reports = pd.DataFrame({"report_id": ["PubTator3|PMID:1|MESH:D011595|psychomotor_agitation|1", "CTD|PMID:2|MESH:D001007|anxiety|1"],
                            "symptom": ["psychomotor_agitation", "anxiety"], "report_value": [1, 1]})
    renamed = rekey(reports, namesake)
    assert list(renamed.symptom) == ["agitation", "anxiety"] and list(renamed.coarse_symptom) == ["psychomotor_agitation", "anxiety"]
    assert renamed.report_id[0] == "PubTator3|PMID:1|MESH:D011595|agitation|1" and renamed.report_id[1] == reports.report_id[1]
    with pytest.raises(ValueError, match="no coarse construct"):
        rekey(pd.DataFrame({"symptom": ["unknown"], "report_value": [1]}), namesake)
    # a descriptor an override moved takes its rows with it; the others stay with the namesake
    reports = pd.DataFrame({"report_id": ["CTD|PMID:3|MESH:D006212|psychosis|1", "CTD|PMID:4|MESH:D011618|psychosis|1"], "symptom": ["psychosis", "psychosis"],
                            "mesh_descriptor": ["D006212", "D011618"], "report_value": [1, 1]})
    moved = rekey(reports, namesake, {"D006212": "hallucinations", "D011618": "psychosis"})
    assert list(moved.symptom) == ["hallucinations", "psychosis"] and list(moved.coarse_symptom) == ["psychosis", "psychosis"]
    assert list(moved.report_id) == ["CTD|PMID:3|MESH:D006212|hallucinations|1", "CTD|PMID:4|MESH:D011618|psychosis|1"]
    assert list(rekey(reports, namesake).symptom) == ["psychosis", "psychosis"], "without the descriptor table every row goes to the namesake"


def test_the_committed_crosswalk_files_mesh_aggression_under_aggressive_behavior_and_agitation_under_one_construct():
    """The owner's rulings of 24 November 2026: MeSH Aggression D000374 belongs to aggressive_behavior, Irritable Mood
    D007508 stays with irritability, and MedDRA Agitation is a term of agitation alone. A preferred term listed under
    two rows goes to whichever comes last in the file (read_preferred_term_to_target_symptom), so none may be."""
    for name in ("docs/symptom_crosswalk.csv", "docs/symptom_crosswalk_fine.csv"):
        holders: dict[str, list[str]] = {}
        for row in read_rows(ROOT / name):
            for term in split_cell(row["meddra_preferred_terms"]):
                holders.setdefault(term.lower(), []).append(row["target_symptom"])
        assert {term: rows for term, rows in holders.items() if len(rows) > 1} == {}, name
    fine = {row["target_symptom"]: row for row in read_rows(ROOT / "docs/symptom_crosswalk_fine.csv")}
    assert (fine["aggressive_behavior"]["mesh_descriptors"], fine["aggressive_behavior"]["mesh_descriptor_level"]) == ("D000374", "symptom")
    assert (fine["irritability"]["mesh_descriptors"], fine["irritability"]["mesh_descriptor_level"]) == ("D007508", "symptom")
    assert "Agitation" in split_cell(fine["agitation"]["meddra_preferred_terms"]) and fine["irritability"]["meddra_preferred_terms"] == "Irritability"



def test_an_mp_override_moves_a_mouse_proxy_before_the_name_match():
    """An override keyed by an MP term id sends the coarse row's proxy to the construct it names; the name match would
    send the hyperactivity-and-restlessness proxy to restlessness."""
    impc = [{"target_symptom": "psychomotor_agitation", "relation": "induces", "mp_term_ids": "MP:0001399", "mp_term_names": "hyperactivity;restlessness",
             "negative_procedure_codes": "OFD", "validity": "moderate", "note": ""}]
    by_key = {(row["target_symptom"], row["relation"]): row for row in fine_impc_rows(impc, coarse_rows(), [], {"mp:0001399": "agitation"})}
    assert by_key[("agitation", "induces")]["mp_term_ids"] == "MP:0001399"
    assert by_key[("restlessness", "induces")]["validity"] == "none" and "agitation" in by_key[("restlessness", "induces")]["note"]
    with pytest.raises(ValueError, match="one construct of"):
        fine_impc_rows(impc, coarse_rows(), [], {"mp:0001399": "anxiety"})


def test_the_committed_mouse_crosswalk_puts_increased_aggression_under_aggressive_behavior():
    """The owner, 24 November 2026, answering "Yes" to moving MP:0005655 increased aggression the same way as MeSH
    Aggression: the proxy belongs to aggressive_behavior, and irritability holds no mouse proxy."""
    rows = {(row["target_symptom"], row["relation"]): row for row in read_rows(ROOT / "configs/impc_symptom_crosswalk_fine.csv")}
    assert rows[("aggressive_behavior", "induces")]["mp_term_ids"] == "MP:0005655"
    assert rows[("irritability", "induces")]["mp_term_ids"] == "" and rows[("irritability", "induces")]["validity"] == "none"


AKATHISIA_STANZA = """
[Term]
id: HP:0031943
name: Akathisia
is_a: HP:0000711 ! Restlessness
"""

AKATHISIA_ROOT = {"coarse_symptom": "psychomotor_agitation", "hpo_id": "HP:0031943", "hpo_name": "Akathisia", "rdoc_domain": "sensorimotor",
                  "decision": "9.74", "note": "split out"}


@pytest.fixture
def vocabulary_with_akathisia(tmp_path):
    obo = tmp_path / "hp_with_akathisia.obo"
    obo.write_text(OBO + AKATHISIA_STANZA, encoding="utf-8")
    return HpoVocabulary.from_obo(obo)


def test_an_extra_root_splits_a_construct_out_below_its_parent_root(vocabulary_with_akathisia):
    coarse = coarse_rows()
    derivation = with_extra_roots(coarse, [AKATHISIA_ROOT], vocabulary_with_akathisia)
    assert coarse[1]["hpo_ids"] == "HP:0000713;HP:0000711", "the coarse rows passed in are not changed"
    assert derivation[1]["hpo_ids"] == "HP:0000713;HP:0000711;HP:0031943" and derivation[1]["hpo_names"] == "Agitation;Restlessness;Akathisia"
    assert [row["target_symptom"] for row in derivation] == [row["target_symptom"] for row in coarse]
    rows, assignments = build_fine_crosswalk(derivation, [], {}, vocabulary_with_akathisia)
    rows = annotate_extra_roots(rows, [AKATHISIA_ROOT])
    by_name = {row["target_symptom"]: row for row in rows}
    assert by_name["restlessness"]["excluded_hpo_ids"] == "HP:0031943", "the parent root excludes the root split out below it"
    assert by_name["restlessness"]["meddra_preferred_terms"] == "Restlessness" and by_name["akathisia"]["meddra_preferred_terms"] == "Akathisia"
    assert by_name["akathisia"]["coarse_symptom"] == "psychomotor_agitation" and by_name["akathisia"]["hpo_ids"] == "HP:0031943"
    assert by_name["akathisia"]["rdoc_domain"] == "sensorimotor" and by_name["restlessness"]["rdoc_domain"] == "arousal"
    assert "decision 9.74" in by_name["akathisia"]["notes"] and "decision 9.74" not in by_name["restlessness"]["notes"]
    how = {assignment["term"]: (assignment["fine_construct"], assignment["how"]) for assignment in assignments}
    assert how["Akathisia"] == ("akathisia", "hpo vocabulary"), "the most specific root that names the term holds it"
    assert by_name["agitation"]["questionnaire_item"] == "PHQ-9 item 8", "the namesake keeps the coarse row's questionnaire item"


def test_an_extra_root_that_would_change_the_coarse_construct_is_refused(vocabulary_with_akathisia):
    def refused(extra, match, vocabulary=vocabulary_with_akathisia, rows=None):
        with pytest.raises(ValueError, match=match):
            with_extra_roots(rows if rows is not None else coarse_rows(), [{**AKATHISIA_ROOT, **extra}], vocabulary)
    refused({"coarse_symptom": "unknown"}, "does not hold")
    refused({"hpo_id": "HP:0000711", "hpo_name": "Restlessness"}, "already a root")
    refused({"coarse_symptom": "anxiety"}, "would rename")
    refused({"hpo_name": "Akathisias"}, "is named 'Akathisia' in hp.obo")
    refused({"hpo_id": "HP:0000746", "hpo_name": "Delusion"}, "under none of")
    excluded = coarse_rows()
    excluded[1]["excluded_hpo_ids"] = "HP:0031943"
    refused({}, "is excluded from", rows=excluded)
    assert with_extra_roots(coarse_rows(), [], vocabulary_with_akathisia) == coarse_rows()


def test_extra_roots_are_read_with_their_required_columns(tmp_path):
    assert read_extra_roots(tmp_path / "absent.csv") == []
    path = tmp_path / "extra.csv"
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["coarse_symptom", "hpo_id", "hpo_name", "rdoc_domain", "decision", "note"])
        writer.writerow(["psychomotor_agitation", "HP:0031943", "Akathisia", "", "", ""])
    with pytest.raises(ValueError, match="missing decision"):
        read_extra_roots(path)


def test_the_page_lists_the_constructs_split_out_below_a_root(vocabulary_with_akathisia):
    derivation = with_extra_roots(coarse_rows(), [AKATHISIA_ROOT], vocabulary_with_akathisia)
    rows, assignments = build_fine_crosswalk(derivation, [], {}, vocabulary_with_akathisia)
    page = render("stamp", annotate_extra_roots(rows, [AKATHISIA_ROOT]), assignments, [], [AKATHISIA_ROOT])
    assert "## Constructs split out below a coarse construct's roots" in page
    assert "| psychomotor_agitation | HP:0031943 Akathisia | sensorimotor | 9.74 | split out |" in page
    assert "| psychomotor_agitation | Akathisia | akathisia | hpo vocabulary |" in page
    assert "## Constructs split out" not in render("stamp", rows, assignments, [])


ROOT = Path(__file__).resolve().parents[1]


def test_the_committed_crosswalk_holds_akathisia_apart_from_restlessness():
    """Decision 9.74: akathisia is a fine construct of its own; the coarse crosswalk as registered still files it under
    psychomotor agitation."""
    fine = {row["target_symptom"]: row for row in read_rows(ROOT / "docs/symptom_crosswalk_fine.csv")}
    assert fine["akathisia"]["hpo_ids"] == "HP:0031943" and fine["akathisia"]["meddra_preferred_terms"] == "Akathisia"
    assert fine["akathisia"]["coarse_symptom"] == "psychomotor_agitation" and fine["akathisia"]["rdoc_domain"] == "sensorimotor"
    assert "Akathisia" not in fine["restlessness"]["meddra_preferred_terms"].split(";")
    assert "HP:0031943" in fine["restlessness"]["excluded_hpo_ids"].split(";")
    coarse = {row["target_symptom"]: row for row in read_rows(ROOT / "docs/symptom_crosswalk.csv")}
    assert "Akathisia" in coarse["psychomotor_agitation"]["meddra_preferred_terms"].split(";")
    assert coarse["psychomotor_agitation"]["hpo_ids"] == "HP:0000713;HP:0000711", "the registered coarse row is unchanged"


def test_the_coarse_construct_covers_the_same_hpo_terms_with_the_extra_root():
    obo = ROOT / "data/raw/hpo/hp.obo"
    if not obo.exists():
        pytest.skip("hp.obo is not fetched")
    vocabulary = HpoVocabulary.from_obo(obo)
    coarse = read_rows(ROOT / "docs/symptom_crosswalk.csv")
    derivation = with_extra_roots(coarse, read_extra_roots(ROOT / "configs/fine_construct_extra_roots.csv"), vocabulary)

    def covered(row):
        terms = set()
        for root in [part for part in row["hpo_ids"].split(";") if part]:
            terms |= {root} | {term for term, _ in [(t, None) for t in vocabulary.parents_by_term if root in vocabulary.ancestors_of(t)]}
        for excluded in [part for part in row["excluded_hpo_ids"].split(";") if part]:
            terms -= {excluded} | {t for t in vocabulary.parents_by_term if excluded in vocabulary.ancestors_of(t)}
        return terms
    for before, after in zip(coarse, derivation):
        assert covered(before) == covered(after), f"{before['target_symptom']} covers other terms with the extra roots"


def test_the_barnes_scale_reads_akathisia_and_every_scale_construct_is_a_fine_construct():
    fine = {row["target_symptom"] for row in read_rows(ROOT / "docs/symptom_crosswalk_fine.csv")}
    scales = read_rows(ROOT / "configs/trial_outcome_scale_crosswalk.csv")
    barnes = [row for row in scales if row["scale"] == "Barnes Akathisia"]
    assert [row["construct"] for row in barnes] == ["akathisia"]
    assert {row["construct"] for row in scales} <= fine
