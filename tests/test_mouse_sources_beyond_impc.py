"""The mouse report sources of decision 9.93: MGI-literature, MGI-screen (evidence/mgi_mouse_phenotypes.py) and
SFARI-mouse-models (evidence/sfari_mouse_models.py), on small fixtures written here."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from mechanistic_pathway_learning.evidence import mgi_mouse_phenotypes as mgi
from mechanistic_pathway_learning.evidence import sfari_mouse_models as sfari
from mechanistic_pathway_learning.evidence.calibrated_reliability import SPECIES_OF_SOURCE
from mechanistic_pathway_learning.evidence.impc_knockout_phenotypes import CrosswalkRow, read_crosswalk

OBO = """format-version: 1.2

[Term]
id: MP:0001399
name: hyperactivity

[Term]
id: MP:0031391
name: increased locomotor activity
is_a: MP:0001399 ! hyperactivity

[Term]
id: MP:0008911
name: induced hyperactivity
is_a: MP:0001399 ! hyperactivity

[Term]
id: MP:0001363
name: increased anxiety-related response

[Term]
id: MP:0002169
name: no abnormal phenotype detected
"""

ALLELES = "\n".join([
    "#header",
    "MGI:1\tGenea<tm1Abc>\ttargeted mutation 1, Abc\tTargeted\tNull/knockout\t\tMGI:100\tGenea",
    "MGI:2\tGenea<tm1(KOMP)Wtsi>\ttargeted mutation 1, Wellcome\tTargeted\tNull/knockout\t\tMGI:100\tGenea",
    "MGI:3\tGeneb<tm1Lex>\ttargeted mutation 1, Lexicon Genetics\tTargeted\tNull/knockout\t\tMGI:200\tGeneb",
    "MGI:4\tGenec<tm2Abc>\ttargeted mutation 2, Abc\tTargeted\tConstitutively active\t\tMGI:300\tGenec",
    "MGI:5\tGened<Tg(Prnp-SNCA*A53T)1Xyz>\ttransgene insertion 1, Xyz\tTransgenic\tInserted expressed sequence\t\tMGI:400\tGened",
    "MGI:6\tGenee<m1Btlr>\tmutation 1, Bruce Beutler\tChemically induced (ENU)\tNot Specified\t\tMGI:500\tGenee",
    "MGI:7\tGenea<tm1cAbc>\ttargeted mutation 1c, Abc\tTargeted\tConditional ready|No functional change\t\tMGI:100\tGenea",
]) + "\n"

GENOTYPES = "\n".join([
    # literature, null: hyperactivity through a descendant, and the handling-induced descendant that is excluded
    "Genea<tm1Abc>/Genea<tm1Abc>\tGenea<tm1Abc>\tinvolves: 129\tMP:0031391\t111\tMGI:100\tMGI:G1",
    "Genea<tm1Abc>/Genea<tm1Abc>\tGenea<tm1Abc>\tinvolves: 129\tMP:0008911\t111\tMGI:100\tMGI:G1",
    "Genea<tm1Abc>/Genea<tm1Abc>\tGenea<tm1Abc>\tinvolves: 129\tMP:0001399\t222\tMGI:100\tMGI:G1",
    # a published paper on a consortium allele is not MGI-literature
    "Genea<tm1(KOMP)Wtsi>/Genea<tm1(KOMP)Wtsi>\tGenea<tm1(KOMP)Wtsi>\tC57BL/6N\tMP:0001399\t333\tMGI:100\tMGI:G2",
    # a Lexicon direct load without a PubMed id is MGI-screen, normal on everything
    "Geneb<tm1Lex>/Geneb<tm1Lex>\tGeneb<tm1Lex>\tB6;129\tMP:0002169\t\tMGI:200\tMGI:G3",
    # gain of function, keyed to the allele perturbation
    "Genec<tm2Abc>/Genec<+>\tGenec<tm2Abc>|Genec<+>\tB6\tMP:0001363\t444\tMGI:300\tMGI:G4",
    # a transgene at the locus is not read
    "Gened<Tg(Prnp-SNCA*A53T)1Xyz>/0\tGened<Tg(Prnp-SNCA*A53T)1Xyz>\tB6\tMP:0001399\t555\tMGI:400\tMGI:G5",
    # a Beutler ENU allele without a direction is untyped and is a screen row
    "Genee<m1Btlr>/Genee<m1Btlr>\tGenee<m1Btlr>\tC57BL/6J\tMP:0001399\t\tMGI:500\tMGI:G6",
    # a floxed allele without a recombinase changes nothing
    "Genea<tm1cAbc>/Genea<tm1cAbc>\tGenea<tm1cAbc>\tB6\tMP:0001399\t666\tMGI:100\tMGI:G7",
]) + "\n"

CROSSWALK = [CrosswalkRow("hyperactivity", "induces", ("MP:0001399",), ("OFD",), "strong", "note"),
             CrosswalkRow("anxiety", "induces", ("MP:0001363",), ("OFD",), "moderate", "note")]
MOUSE_TO_HUMAN = {"MGI:100": "GENEA", "MGI:200": "GENEB", "MGI:300": "GENEC", "MGI:400": "GENED", "MGI:500": "GENEE"}
NODES = {symbol: f"GENE:{symbol}" for symbol in MOUSE_TO_HUMAN.values()}


@pytest.fixture()
def mgi_inputs(tmp_path: Path):
    (tmp_path / "mp.obo").write_text(OBO, encoding="utf-8")
    (tmp_path / "alleles.rpt").write_text(ALLELES, encoding="utf-8")
    (tmp_path / "genotypes.rpt").write_text(GENOTYPES, encoding="utf-8")
    names, children = mgi.read_mp_ontology(tmp_path / "mp.obo")
    return tmp_path, names, children, mgi.read_alleles(tmp_path / "alleles.rpt")


def build(mgi_inputs, origin, **options):
    directory, names, children, alleles = mgi_inputs
    return mgi.build_reports(mgi.read_genotype_annotations(directory / "genotypes.rpt"), alleles, MOUSE_TO_HUMAN, NODES, CROSSWALK, children,
                             mgi.read_descendant_exclusions(), names, mgi.read_screen_loads(), origin, **options)


def test_the_new_sources_are_mouse_sources_of_the_regression():
    for source in (mgi.LITERATURE_SOURCE, mgi.SCREEN_SOURCE, sfari.SOURCE_NAME):
        assert SPECIES_OF_SOURCE[source] == "mouse"


def test_mgi_literature_reads_descendants_but_not_the_excluded_ones_and_leaves_out_consortium_alleles(mgi_inputs):
    rows, normal, counts = build(mgi_inputs, "literature")
    hyperactivity = [row for row in rows if row["symptom"] == "hyperactivity"]
    assert sorted(row["source_term_id"] for row in hyperactivity) == ["MP:0001399", "MP:0031391"], "MP:0008911 is handling-induced and excluded"
    assert {row["references"] for row in hyperactivity} == {"PMID:111", "PMID:222"} and all(row["source"] == mgi.LITERATURE_SOURCE for row in rows)
    assert counts["origin:consortium_in_literature"] == 1 and counts["allele_not_read:transgenic"] == 1 and counts["allele_not_read:no functional change"] == 1
    assert all(row["evidence_class"] == "animal" and row["report_value"] == 1 for row in rows)


def test_mgi_gain_of_function_is_keyed_to_the_allele_perturbation_and_seeded_positive(mgi_inputs):
    rows, _, _ = build(mgi_inputs, "literature")
    anxiety = [row for row in rows if row["symptom"] == "anxiety"]
    assert len(anxiety) == 1 and anxiety[0]["perturbation_id"] == "GENEC|gain_of_function" and anxiety[0]["allele_direction"] == "gain_of_function"
    assert json.loads(anxiety[0]["perturbation_nodes"]) == [["GENE:GENEC", 1.0, 1.0]]
    null = next(row for row in rows if row["perturbation_id"] == "GENEA")
    assert json.loads(null["perturbation_nodes"]) == [["GENE:GENEA", -1.0, 1.0]]


def test_mgi_screen_selects_the_configured_loads_and_keeps_no_abnormal_phenotype_out_of_the_absences_by_default(mgi_inputs):
    rows, normal, counts = build(mgi_inputs, "screen")
    assert [row["perturbation_id"] for row in rows] == ["GENEE"] and rows[0]["allele_direction"] == "untyped" and rows[0]["mgi_origin"] == "Beutler Mutagenetix"
    assert [entry["perturbation_id"] for entry in normal] == ["GENEB"] and counts["genotypes_with_no_abnormal_phenotype"] == 1
    assert not [row for row in rows if row["report_value"] == 0]
    counted, _, counted_counts = build(mgi_inputs, "screen", count_normal_as_absence=True)
    absences = [row for row in counted if row["report_value"] == 0]
    assert sorted(row["symptom"] for row in absences) == ["anxiety", "hyperactivity"] and all(row["whole_genotype_normal"] for row in absences)
    without_untyped, _, _ = build(mgi_inputs, "screen", include_untyped=False)
    assert not without_untyped


def test_allele_direction_rules():
    def allele(kind, attributes):
        return mgi.MgiAllele("MGI:x", "G<x>", "", kind, frozenset(attributes), "MGI:1")
    assert mgi.allele_direction(allele("Targeted", {"Null/knockout", "Reporter"}))[0] == "loss_of_function"
    assert mgi.allele_direction(allele("Targeted", {"Dominant negative"}))[0] == "loss_of_function"
    assert mgi.allele_direction(allele("Targeted", {"Hypomorph"}))[0] == "loss_of_function"
    assert mgi.allele_direction(allele("Targeted", {"Constitutively active"}))[0] == "gain_of_function"
    assert mgi.allele_direction(allele("Targeted", {"Null/knockout", "Constitutively active"}))[0] is None
    assert mgi.allele_direction(allele("Targeted", {"Inserted expressed sequence"}))[0] is None
    assert mgi.allele_direction(allele("Targeted", {"Reporter"}))[0] is None
    assert mgi.allele_direction(allele("Gene trapped", {"Reporter"}))[0] == "untyped"
    assert mgi.allele_direction(allele("Chemically induced (ENU)", {""}))[0] == "untyped"
    assert mgi.zygosity("A<a>/A<a>") == "homozygous" and mgi.zygosity("A<a>/A<+>") == "heterozygous" and mgi.zygosity("A<a>/A<b>") == "compound heterozygous"


def test_the_descendant_exclusions_name_real_descendants_of_crosswalk_terms():
    crosswalk_terms = {term for row in read_crosswalk(Path("configs/impc_symptom_crosswalk_fine.csv")) for term in row.mp_term_ids}
    for term, reason in mgi.read_descendant_exclusions().items():
        assert term.startswith("MP:") and reason
    import csv
    with open(mgi.DEFAULT_DESCENDANT_EXCLUSIONS_PATH, newline="", encoding="utf-8") as handle:
        assert {row["ancestor_in_crosswalk"] for row in csv.DictReader(handle)} <= crosswalk_terms


SFARI_PAGE = """<html>Latest Release: 2026 Q2
<div class="data-block">
<span class="data-block__title">M_GENEA_1_KO_HM<span class="data-block__title">
<h6 class="data-block__subheader">Model Type: <span class="data-block__value">Genetic<span></h6>
<h6 class="data-block__subheader">Model Genotype: <span class="data-block__value">Homozygous<span></h6>
<h6 class="data-block__subheader">Allele Type: <span class="data-block__value">Targeted (Knock Out)<span></h6>
<h6 class="data-block__subheader">Genetic Background: <span class="data-block__value">C57BL/6<span></h6>
<table><tbody>
<tr class="table__row"><td class="table__cell">Motor phenotype</td><td class="table__cell">General locomotor activity: ambulatory activity</td><td class="table__cell">Increased</td><td class="table__cell">Open field test</td><td class="table__cell">8 weeks</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/123">A</a></td></tr>
<tr class="table__row"><td class="table__cell">Emotion</td><td class="table__cell">Anxiety</td><td class="table__cell">No change</td><td class="table__cell">Elevated plus maze test</td><td class="table__cell">8 weeks</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/123">A</a></td></tr>
<tr class="table__row"><td class="table__cell">Learning &amp; memory</td><td class="table__cell">Spatial working memory</td><td class="table__cell">No change</td><td class="table__cell">Y-maze test</td><td class="table__cell">8 weeks</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/123">A</a></td></tr>
<tr class="table__row"><td class="table__cell">Learning &amp; memory</td><td class="table__cell">Object recognition memory</td><td class="table__cell">Decreased</td><td class="table__cell">Novel object recognition test</td><td class="table__cell">8 weeks</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/123">A</a></td></tr>
<tr class="table__row"><td class="table__cell">Emotion</td><td class="table__cell">Depression</td><td class="table__cell">Increased</td><td class="table__cell">Forced swim test</td><td class="table__cell">8 weeks</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/123">A</a></td></tr>
<tr class="table__row"><td class="table__cell">Motor phenotype</td><td class="table__cell">General locomotor activity</td><td class="table__cell">No change</td><td class="table__cell">Novel cage test</td><td class="table__cell">8 weeks</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/124">B</a></td></tr>
<tr class="table__row"><td class="table__cell">Social behavior</td><td class="table__cell">Social approach</td><td class="table__cell">Not reported</td><td class="table__cell">NA</td><td class="table__cell">NA</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/124">B</a></td></tr>
</tbody></table>
</div>
<div class="data-block">
<span class="data-block__title">M_GENEA_2_RESCUE<span class="data-block__title">
<h6 class="data-block__subheader">Model Type: <span class="data-block__value">RESCUE-Pharmaceutical<span></h6>
<h6 class="data-block__subheader">Model Genotype: <span class="data-block__value">Homozygous<span></h6>
<h6 class="data-block__subheader">Allele Type: <span class="data-block__value">Knockout<span></h6>
<table><tbody>
<tr class="table__row"><td class="table__cell">Emotion</td><td class="table__cell">Anxiety</td><td class="table__cell">Restored</td><td class="table__cell">Open field test</td><td class="table__cell">8 weeks</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/125">C</a></td></tr>
</tbody></table>
</div>
<div class="data-block">
<span class="data-block__title">M_GENEA_3_OE<span class="data-block__title">
<h6 class="data-block__subheader">Model Type: <span class="data-block__value">Genetic<span></h6>
<h6 class="data-block__subheader">Model Genotype: <span class="data-block__value">Transgenic<span></h6>
<h6 class="data-block__subheader">Allele Type: <span class="data-block__value">Overexpression<span></h6>
<table><tbody>
<tr class="table__row"><td class="table__cell">Emotion</td><td class="table__cell">Anxiety</td><td class="table__cell">Decreased</td><td class="table__cell">Open field test</td><td class="table__cell">8 weeks</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/126">D</a></td></tr>
<tr class="table__row"><td class="table__cell">Emotion</td><td class="table__cell">Anxiety</td><td class="table__cell">Refractory</td><td class="table__cell">Open field test</td><td class="table__cell">8 weeks</td><td class="table__cell"><a href="https://www.ncbi.nlm.nih.gov/pubmed/126">D</a></td></tr>
</tbody></table>
</div>
</html>"""


def test_sfari_page_parsing_reads_each_model_block():
    models = sfari.parse_page(SFARI_PAGE)
    assert [model["model"] for model in models] == ["M_GENEA_1_KO_HM", "M_GENEA_2_RESCUE", "M_GENEA_3_OE"]
    assert models[0]["allele_type"] == "Targeted (Knock Out)" and models[0]["rows"][3]["category"] == "Learning & memory" and models[0]["rows"][0]["pmid"] == "123"


def test_sfari_calls_absences_rescue_rows_and_narrow_tests():
    rows, counts = sfari.build_reports({"GENEA": SFARI_PAGE, "NOTONE": SFARI_PAGE}, {"GENEA"}, {"GENEA": "GENE:GENEA"}, sfari.read_crosswalk(), sfari.read_allele_classes())
    by = {(row["perturbation_id"], row["symptom"], row["relation"], row["report_value"]) for row in rows}
    assert ("GENEA", "hyperactivity", "induces", 1) in by, "increased open-field locomotion is a hyperactivity call"
    assert ("GENEA", "psychomotor_retardation", "induces", 0) in by, "a no change in the novel cage is an absence of hypolocomotion"
    assert ("GENEA", "hyperactivity", "induces", 0) not in by, "the model's own hyperactivity call blocks its absence on another test"
    assert ("GENEA", "anxiety", "induces", 0) in by, "a no change on the elevated plus maze is an anxiety absence"
    assert ("GENEA", "cognitive_impairment", "induces", 1) in by, "a decreased object recognition memory is an impairment"
    assert not [key for key in by if key[1] == "cognitive_impairment" and key[3] == 0], "one memory test is not read as the absence of cognitive impairment"
    assert not [key for key in by if key[1] == "depressed_mood"], "the forced swim test has no defensible proxy"
    assert ("GENEA|gain_of_function", "anxiety", "relieves", 1) in by, "overexpression is a gain of function; decreased anxiety relieves"
    assert counts["model_not_read:rescue-pharmaceutical"] == 1 and counts["row_dropped:refractory"] == 1 and counts["row_untested"] == 1
    assert counts["genes_without_a_one_to_one_mouse_orthologue"] == 1
    assert all(row["source"] == sfari.SOURCE_NAME and row["evidence_class"] == "animal" for row in rows)


def test_sfari_configs_cover_every_class_and_name_no_proxy_for_constructs_without_one():
    classes = sfari.read_allele_classes()
    assert set(classes.values()) <= set(sfari.ALLELE_CLASSES) and classes["conditional knockout"] == "not_read" and classes["knockout"] == "loss_of_function"
    crosswalk = sfari.read_crosswalk()
    read = {row.target_symptom for row in crosswalk if row.validity in ("strong", "moderate", "weak")}
    assert not read & {"psychosis", "suicidal_ideation", "suicide_behaviors", "abnormal_dreams", "emotional_lability", "depressed_mood"}
    impc_symptoms = {row.symptom for row in read_crosswalk(Path("configs/impc_symptom_crosswalk_fine.csv"))}
    assert {row.target_symptom for row in crosswalk} <= impc_symptoms, "every SFARI row names a fine construct"
