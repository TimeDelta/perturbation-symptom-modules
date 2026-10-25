"""The report sources of species beyond mouse (evidence/cross_species_reports.py, decision 9.94), on fixtures."""
from __future__ import annotations

import gzip
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mechanistic_pathway_learning.evidence import cross_species_reports as species
from mechanistic_pathway_learning.evidence.calibrated_reliability import (
    SPECIES_OF_SOURCE,
    cell_table,
    feature_frame,
    fit_calibration,
    species_of_sources,
)

HEADER = "Gene1ID\tGene1Symbol\tGene1SpeciesTaxonID\tGene1SpeciesName\tGene2ID\tGene2Symbol\tGene2SpeciesTaxonID\tGene2SpeciesName\tAlgorithms\tAlgorithmsMatch\tOutOfAlgorithms\tIsBestScore\tIsBestRevScore"


def orthology_file(tmp_path: Path) -> Path:
    rows = [
        ("HGNC:1", "GENEA", "NCBITaxon:9606", "FB:FBgn1", "genea", "NCBITaxon:7227"),  # one to one
        ("FB:FBgn2", "geneb", "NCBITaxon:7227", "HGNC:2", "GENEB", "NCBITaxon:9606"),  # one to one, listed the other way round
        ("HGNC:3", "GENEC", "NCBITaxon:9606", "FB:FBgn3", "genec", "NCBITaxon:7227"),  # one human, two fly genes: not read
        ("HGNC:3", "GENEC", "NCBITaxon:9606", "FB:FBgn4", "genec2", "NCBITaxon:7227"),
        ("HGNC:5", "GENEE", "NCBITaxon:9606", "ZFIN:ZDB-GENE-1", "genee", "NCBITaxon:7955"),
        ("HGNC:6", "GENEF", "NCBITaxon:9606", "WB:WBGene1", "genf-1", "NCBITaxon:6239"),
        ("HGNC:7", "GENEG", "NCBITaxon:9606", "RGD:7", "Geneg", "NCBITaxon:10116"),
    ]
    path = tmp_path / "orthology.tsv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("# Orthology Filter: Stringent\n" + HEADER + "\n")
        for a, b, c, d, e, f in rows:
            handle.write("\t".join([a, b, c, "x", d, e, f, "y", "Alg", "3", "9", "Yes", "Yes"]) + "\n")
    return path


NODES = {symbol: f"GENE:{symbol}" for symbol in ("GENEA", "GENEB", "GENEC", "GENEE", "GENEF", "GENEG", "HUMANONE")}


def test_orthology_is_one_to_one_in_both_directions(tmp_path):
    fly = species.read_one_to_one_orthologs(orthology_file(tmp_path), "fly")
    assert set(fly) == {"FB:FBgn1", "FB:FBgn2"} and fly["FB:FBgn2"] == ("geneb", "HGNC:2", "GENEB")
    assert species.by_symbol(fly) == {"genea": "GENEA", "geneb": "GENEB"}


def test_every_source_has_a_species_and_the_nearest_species_names_a_mixed_pair():
    for source, level in species.SOURCE_SPECIES.items():
        assert SPECIES_OF_SOURCE[source] == level
    assert species_of_sources("FlyBase-RNAi;IMPC-knockout") == "mouse" and species_of_sources("WormBase-RNAi;ZFIN-mutant") == "zebrafish"


def test_rat_allele_direction():
    assert species.rat_allele_direction("Fmr1<sup>em2Mcwi</sup>", "CRISPR/Cas9 induced mutant 2")[0] == "untyped"
    assert species.rat_allele_direction("Gene<sup>em1</sup>", "knockout of exon 2")[0] == "loss_of_function"
    assert species.rat_allele_direction("Gene<sup>Tg(CAG-x)1</sup>", "transgene")[0] is None


def test_fly_genotypes_are_classical_rnai_with_a_permitted_driver_or_not_read():
    drivers = species.read_drivers()
    assert species.fly_genotype(["rut[1]"], drivers)[:2] == ("rut", "FlyBase-classical")
    assert species.fly_genotype(["Scer\\GAL4[elav-C155]", "tau[RNAi.UAS]"], drivers)[:2] == ("tau", "FlyBase-RNAi")
    assert species.fly_genotype(["Scer\\GAL4[Mef2.247.Switch]", "dbr[GD7281]"], drivers)[0] is None, "a restricted driver"
    assert species.fly_genotype(["shi[1.UAS]", "Scer\\GAL4[c316]"], drivers)[0] is None
    assert species.fly_genotype(["Scer\\GAL4[elav-C155]", "Hsap\\APP[UAS]"], drivers)[0] is None, "a human transgene"


def test_flybase_rows(tmp_path):
    path = tmp_path / "fly.tsv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("#genotype_symbols\tgenotype_FBids\tphenotype_name\tphenotype_id\tqualifier_names\tqualifier_ids\treference\n")
        handle.write("genea[1]\tFBal1\tdecreased efficacy of long-term memory\tFBcv:0007522\t\t\tFBrf1\n")
        handle.write("Scer\\GAL4[elav-C155] geneb[GD1]\tFBal2 FBal3\tdecreased sleep\tFBcv:0007514\tadult stage\t\tFBrf2\n")
        handle.write("genea[1]\tFBal1\tabnormal eye color\tFBcv:0000355\t\t\tFBrf3\n")
    rows, counts = species.build_flybase(path, species.read_one_to_one_orthologs(orthology_file(tmp_path), "fly"), NODES, species.read_species_crosswalk(),
                                         species.read_drivers(), ("strong", "moderate"))
    by = {(row["source"], row["perturbation_id"], row["symptom"]) for row in rows}
    assert by == {("FlyBase-classical", "GENEA", "cognitive_impairment"), ("FlyBase-RNAi", "GENEB", "insomnia")}
    with_id, _ = species.build_flybase(path, species.read_one_to_one_orthologs(orthology_file(tmp_path), "fly"), NODES, species.read_species_crosswalk(),
                                       species.read_drivers(), ("strong", "moderate", "weak_intellectual_disability"))
    assert ("GENEA", "intellectual_disability") in {(row["perturbation_id"], row["symptom"]) for row in with_id}, "off by default, read when asked"


def zfin_line(fish, term, name, quality, quality_name, tag, environment="ZDB-EXP-041102-1"):
    fields = [fish, "genee<sup>x/x</sup>", "s", "Larval", "s", "Larval", "", "", "", "", term, name, quality, quality_name, tag, "", "", "", "", "", "", "ZDB-PUB-1", environment]
    return "\t".join(fields) + "\n"


def test_zfin_calls_absences_and_reagents(tmp_path):
    phenotypes = tmp_path / "phenotype_fish.txt"
    phenotypes.write_text(zfin_line("F1", "GO:0036268", "swimming", "PATO:0002051", "increased occurrence", "abnormal")
                          + zfin_line("F2", "GO:0001966", "thigmotaxis", "PATO:0045073", "normal process quality", "normal")
                          + zfin_line("F2", "GO:0001966", "thigmotaxis", "PATO:0045073", "normal process quality", "normal", "ZDB-EXP-999")
                          + zfin_line("F3", "GO:0036268", "swimming", "PATO:0002051", "increased occurrence", "abnormal"), encoding="utf-8")
    components = tmp_path / "components.txt"
    components.write_text("F1\tn\tZDB-GENE-1\tgenee\tZDB-ALT-1\tx\t\t\t\t\tG\tg\n"
                          "F2\tn\tZDB-GENE-1\tgenee\tZDB-MRPHLNO-1\tMO1\t\t\t\t\tG\tg\n"
                          "F3\tn\tZDB-GENE-1\tgenee\tZDB-ALT-2\ty\tZDB-TGCONSTRCT-1\tTg\t\t\tG\tg\n", encoding="utf-8")
    rows, counts = species.build_zfin(phenotypes, species.read_fish_components(components), species.read_one_to_one_orthologs(orthology_file(tmp_path), "zebrafish"),
                                      NODES, species.read_species_crosswalk(), ("strong", "moderate"))
    by = {(row["source"], row["symptom"], row["report_value"]) for row in rows}
    assert by == {("ZFIN-mutant", "hyperactivity", 1), ("ZFIN-morpholino", "anxiety", 0)}
    assert counts["not_read:a treated or non-standard environment"] == 1 and counts["not_read:not one gene, or a transgenic construct"] == 1


def test_wormbase_is_off_by_default_and_reads_not_rows_when_asked(tmp_path):
    path = tmp_path / "worm.wb"
    path.write_text("!gaf\nWB\tWBGene1\tgenf-1\t\tWBPhenotype:0000642\tWB_REF:1\tIMP\tWB:WBVar1\tP\t\t\tgene\ttaxon:6239\t1\tWB\t\t\n"
                    "WB\tWBGene1\tgenf-1\tNOT\tWBPhenotype:0000643\tWB_REF:2\tIMP\tWB:WBRNAi1\tP\t\t\tgene\ttaxon:6239\t1\tWB\t\t\n", encoding="utf-8")
    orthologs = species.read_one_to_one_orthologs(orthology_file(tmp_path), "worm")
    assert species.build_wormbase(path, orthologs, NODES, species.read_species_crosswalk(), ("strong", "moderate"))[0] == []
    rows, _ = species.build_wormbase(path, orthologs, NODES, species.read_species_crosswalk(), ("strong", "moderate", "weak_worm"))
    assert {(row["source"], row["report_value"]) for row in rows} == {("WormBase-variation", 1), ("WormBase-RNAi", 0)}


def test_rat_catalepsy_calls_absences_and_another_drugs_catalepsy():
    assays = [{"assay_chembl_id": "A1", "description": "Induction of catalepsy in rats", "assay_organism": "Rattus norvegicus"},
              {"assay_chembl_id": "A2", "description": "Reversal of haloperidol-induced catalepsy in rats", "assay_organism": "Rattus norvegicus"}]
    activities = [{"activity_id": 1, "assay_chembl_id": "A1", "molecule_chembl_id": "CHEMBL54", "parent_molecule_chembl_id": "CHEMBL54", "standard_type": "ED50", "standard_relation": "=", "standard_value": "0.3"},
                  {"activity_id": 2, "assay_chembl_id": "A1", "molecule_chembl_id": "CHEMBL715", "parent_molecule_chembl_id": "CHEMBL715", "standard_type": "ED50", "standard_relation": ">", "standard_value": "100"},
                  {"activity_id": 3, "assay_chembl_id": "A2", "molecule_chembl_id": "CHEMBL715", "parent_molecule_chembl_id": "CHEMBL715", "standard_type": "ED50", "standard_relation": "=", "standard_value": "3"},
                  {"activity_id": 4, "assay_chembl_id": "A1", "molecule_chembl_id": "CHEMBL715", "parent_molecule_chembl_id": "CHEMBL715", "standard_type": "Inhibition", "standard_relation": "=", "standard_value": "40"}]
    rows, counts = species.build_chembl_rat(assays, activities, {"CHEMBL54": ["CID100003559"], "CHEMBL715": ["CID100002818"]})
    assert {(row["perturbation_id"], row["symptom"], row["report_value"]) for row in rows} == {("CID100003559", "parkinsonism", 1), ("CID100002818", "parkinsonism", 0)}
    assert counts["not_read:catalepsy produced by another drug"] == 1 and counts["not_read:neither a dose producing catalepsy nor a stated absence"] == 1


def fenckova_workbook(path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    workbook = openpyxl.Workbook()
    s2 = workbook.active
    s2.title = "S2"
    s2.append(["Human gene info"])
    s2.append(list(species.FENCKOVA_S2_COLUMNS))
    s2.append(["GENEA", "CG1", "FBgn1", "genea", 101, "NO", "YES", 50, 0.8, 1.9, 0.5, 0.1, 0.0001, 0.001, "Not tested", "Habituation deficit", 0, 1, 0, 0])
    s2.append(["GENEA", "CG1", "FBgn1", "genea", 102, "NO", "YES", 50, 0.8, 1.1, 0.05, 0.1, 0.5, 0.7, "Not tested", "Not affected", 0, 1, 0, 0])
    s2.append(["OLDB", "CG2", "FBgn2", "geneb", 103, "NO", "YES", 50, 0.8, 1.0, 0.0, 0.1, 0.9, 0.95, "Not tested", "Not affected", 1, 0, 0, 0])
    s2.append(["GENEC", "CG3", "FBgn3", "genec", 104, "YES", "NO", 0, 0, 0, 0, 0, 1, 1, "Not tested", "Non-performers", 0, 0, 1, 0])
    s3 = workbook.create_sheet("S3")
    s3.append(["non-peformers", "not affected", "habituation deficient", "premature habituation"])
    s3.append(["GENEC", "OLDB", "GENEA", None])
    workbook.save(path)


def test_fenckova_gene_categories_renamed_symbols_and_orthology_check(tmp_path):
    path = tmp_path / "mmc2.xlsx"
    fenckova_workbook(path)
    lines, category_of = species.read_fenckova_workbook(path)
    assert len(lines) == 4 and category_of == {"GENEC": "non-performers", "OLDB": "not affected", "GENEA": "habituation deficient"}
    fly = species.read_one_to_one_orthologs(orthology_file(tmp_path), "fly")
    validities = ("strong", "moderate", "weak")
    rows, counts = species.build_fenckova(lines, category_of, fly, NODES, species.read_species_crosswalk(), validities, {"OLDB": "GENEB", "GENEA": "GENEA"})
    assert {(row["perturbation_id"], row["report_value"]) for row in rows} == {("GENEA", 1), ("GENEB", 0)}, "the gene's category decides, not its lines"
    assert counts["not_read:lethal"] == 1 and counts["human_symbols_renamed_by_HGNC"] == 1
    assert counts["human_fly_pairs_without_an_Alliance_one_to_one_orthologue"] == 1, "GENEC's fly gene has two human-side partners"
    assert species.build_fenckova(lines, category_of, fly, NODES, species.read_species_crosswalk(), ("strong", "moderate"), {"OLDB": "GENEB"})[0] == [], \
        "weak, so off by default"


def test_each_species_is_pooled_below_the_bar_and_fitted_alone_above_it():
    """Rat with few cells goes to the pooled form; fly with enough gets its own fit; both at once, each on its own count."""
    generator = np.random.default_rng(3)
    rows, rates = [], []
    for index in range(600):
        identifier = f"G{index}"
        if index < 200:
            rows.append((identifier, "anxiety", "monogenic", "positive", 1, 0.7, 0.5, "HPO-OMIM")); rates.append(0.5)
        elif index < 230:
            rows.append((identifier, "anxiety", "animal", "positive", 1, 0.6, 0.3, "RGD-rat")); rates.append(0.4)
        else:
            source = "FlyBase-RNAi" if index % 2 else "FlyBase-classical"
            direction = "negative" if index % 3 == 0 else "positive"
            rows.append((identifier, "anxiety", "animal", direction, 1, 0.0, 0.3, source)); rates.append(0.3)
    pairs = pd.DataFrame(rows, columns=["perturbation_id", "symptom", "evidence_class", "direction", "n_distinct", "prior_probability", "strength", "sources"])
    cells = cell_table(pairs, feature_frame(pairs, {}, {}), [row[0] for row in rows], ["anxiety"])
    outcomes = (generator.random((600, 1)) < np.array(rates)[:, None]).astype(float)
    fitted = fit_calibration(cells, outcomes, None, np.arange(600))
    assert fitted.species_cells["rat"]["positives"] < 20 and fitted.fit_of_species["rat"] == "pooled"
    assert min(fitted.species_cells["fly"]["positives"], fitted.species_cells["fly"]["negatives"]) >= 20 and fitted.fit_of_species["fly"] == "fly"
    assert {"source:FlyBase-RNAi", "source:FlyBase-classical"} <= set(fitted.parts["fly"].penalty_multiples)
