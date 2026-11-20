"""The Human-GEM corrections loader (graph/human_gem_corrections.py) on small tables written here, so its behaviour is
tested without the raw model. The guards on the pinned files are in tests/test_human_gem_identifier_guards.py."""
from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd
import pytest

from mechanistic_pathway_learning.graph.human_gem_corrections import (
    CORRECTION_COLUMNS,
    canonical_gene_rule,
    DEFAULT_CORRECTIONS_PATH,
    NO_CORRECTIONS,
    base_metabolite_id,
    correct_cobra_model,
    correct_metabolites_table,
    correct_sbml_text,
    corrections_without_their_row,
    parse_corrections,
    parse_equation,
    parse_gene_rule,
    read_human_gem_corrections,
    read_human_gem_cobra_model,
    read_human_gem_metabolites,
    read_human_gem_sbml_text,
)


def row(kind, row_id, column, pinned, corrected):
    return {"kind": kind, "row_id": row_id, "column": column, "pinned_value": pinned, "corrected_value": corrected,
            "source_1": "s1", "source_2": "s2", "ruling": "test", "note": ""}


FIXTURE_ROWS = [
    row("value", "MAM00001c", "metChEBIID", "CHEBI:900", "CHEBI:100"),
    row("value", "MAM00001r", "metChEBIID", "CHEBI:900", "CHEBI:100"),
    row("value", "MAM00002c", "metChEBIID", "CHEBI:901", ""),
    row("value", "MAM00003e", "metKEGGID", "C00009", "C00003"),
    row("species_id", "MAM00003c", "mets", "MAM00003c", "MAM00009c"),
    row("species_name", "MAM00003c", "name", "Compound three, C3:1 (Delta 2)", "Compound nine"),
]

METABOLITES_TSV = (
    "mets\tmetsNoComp\tmetKEGGID\tmetChEBIID\tmetPubChemID\n"
    "MAM00001c\tMAM00001\tC00001\tCHEBI:900\t11\n"
    "MAM00001r\tMAM00001\tC00001\tCHEBI:900\t11\n"
    "MAM00002c\tMAM00002\t\tCHEBI:901\t\n"
    "MAM00003e\tMAM00003\tC00009\tCHEBI:300\t\n"
    "MAM00003c\tMAM00003\tC00009\tCHEBI:309\t\n"
    "MAM00009e\tMAM00009\tC00009\tCHEBI:309\t\n"
)

SBML_TEXT = """<sbml><model><listOfSpecies>
      <species metaid="meta_M_MAM00003c" sboTerm="SBO:0000247" id="M_MAM00003c" name="Compound three, C3:1 (Delta 2)" compartment="c" fbc:charge="0">
        <annotation><rdf:RDF><rdf:Description rdf:about="#meta_M_MAM00003c"/></rdf:RDF></annotation>
      </species>
      <species metaid="meta_M_MAM00003e" sboTerm="SBO:0000247" id="M_MAM00003e" name="Compound three, C3:1 (Delta 2)" compartment="e" fbc:charge="0"/>
      <species metaid="meta_M_MAM00009e" sboTerm="SBO:0000247" id="M_MAM00009e" name="Compound nine" compartment="e" fbc:charge="-1"/>
</listOfSpecies><listOfReactions>
      <reaction id="R_MAR1"><listOfReactants><speciesReference species="M_MAM00003c" stoichiometry="1" constant="true"/></listOfReactants>
      <listOfProducts><speciesReference species="M_MAM00001c" stoichiometry="2" constant="true"/></listOfProducts></reaction>
      <reaction id="R_MAR2"><listOfReactants><speciesReference species="M_MAM00003e" stoichiometry="1" constant="true"/></listOfReactants></reaction>
</listOfReactions></model></sbml>"""


def write_corrections(path: Path, rows: list[dict]) -> Path:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CORRECTION_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


@pytest.fixture
def corrections_path(tmp_path) -> Path:
    return write_corrections(tmp_path / "corrections.csv", FIXTURE_ROWS)


@pytest.fixture
def metabolites_path(tmp_path) -> Path:
    path = tmp_path / "metabolites.tsv"
    path.write_text(METABOLITES_TSV)
    return path


def test_the_table_is_split_by_kind(corrections_path):
    corrections = read_human_gem_corrections(corrections_path)
    assert corrections.values == (("MAM00001c", "metChEBIID", "CHEBI:900", "CHEBI:100"), ("MAM00001r", "metChEBIID", "CHEBI:900", "CHEBI:100"),
                                  ("MAM00002c", "metChEBIID", "CHEBI:901", ""), ("MAM00003e", "metKEGGID", "C00009", "C00003"))
    assert corrections.species_ids == {"MAM00003c": "MAM00009c"}
    assert corrections.species_names == {"MAM00003c": ("Compound three, C3:1 (Delta 2)", "Compound nine")}


def test_an_absent_table_or_none_gives_no_corrections(tmp_path):
    assert read_human_gem_corrections(None) is NO_CORRECTIONS
    assert read_human_gem_corrections(tmp_path / "missing.csv") is NO_CORRECTIONS


def test_value_cells_are_replaced_and_a_blank_correction_empties_the_cell(metabolites_path, corrections_path):
    table = read_human_gem_metabolites(metabolites_path, corrections_path).set_index("mets")
    assert table.at["MAM00001c", "metChEBIID"] == "CHEBI:100" and table.at["MAM00001r", "metChEBIID"] == "CHEBI:100"
    assert pd.isna(table.at["MAM00002c", "metChEBIID"])
    assert table.at["MAM00003e", "metKEGGID"] == "C00003"
    # read as text, the blank is the reader's own empty cell, so the result equals reading a corrected file
    as_text = read_human_gem_metabolites(metabolites_path, corrections_path, dtype=str, keep_default_na=False).set_index("mets")
    assert as_text.at["MAM00002c", "metChEBIID"] == ""
    assert as_text.at["MAM00001c", "metPubChemID"] == "11"


def test_a_rename_sets_mets_and_metsnocomp_and_leaves_the_other_cells(metabolites_path, corrections_path):
    table = read_human_gem_metabolites(metabolites_path, corrections_path)
    renamed = table[table.mets == "MAM00009c"].iloc[0]
    assert renamed.metsNoComp == "MAM00009" and renamed.metChEBIID == "CHEBI:309" and renamed.metKEGGID == "C00009"
    assert "MAM00003c" not in set(table.mets)
    assert list(table.mets) == ["MAM00001c", "MAM00001r", "MAM00002c", "MAM00003e", "MAM00009c", "MAM00009e"]
    assert base_metabolite_id("MAM00009c") == "MAM00009" and base_metabolite_id("CHEBI15378") == "CHEBI15378"


def test_usecols_selects_after_the_corrections(metabolites_path, corrections_path):
    table = read_human_gem_metabolites(metabolites_path, corrections_path, usecols=["metsNoComp", "metChEBIID"])
    assert list(table.columns) == ["metsNoComp", "metChEBIID"]
    assert list(table.metsNoComp) == ["MAM00001", "MAM00001", "MAM00002", "MAM00003", "MAM00009", "MAM00009"]


def test_the_pinned_table_is_read_unchanged_without_corrections(metabolites_path):
    assert read_human_gem_metabolites(metabolites_path, None).equals(pd.read_csv(metabolites_path, sep="\t"))


def test_a_correction_whose_row_is_absent_is_skipped_and_reported(corrections_path):
    table = pd.DataFrame({"mets": ["MAM00001c"], "metsNoComp": ["MAM00001"], "metChEBIID": ["CHEBI:900"], "metKEGGID": [""]})
    corrections = read_human_gem_corrections(corrections_path)
    corrected = correct_metabolites_table(table, corrections)
    assert list(corrected.metChEBIID) == ["CHEBI:100"]
    assert corrections_without_their_row(table, None, corrections) == ["value MAM00001r", "value MAM00002c", "value MAM00003e", "species_id MAM00003c"]
    assert corrections_without_their_row(table, SBML_TEXT, corrections)[-1:] == ["species_id MAM00003c"]
    assert table.metChEBIID.iloc[0] == "CHEBI:900", "the input table is not modified"


def test_a_cell_that_no_longer_holds_the_pinned_value_raises(corrections_path):
    table = pd.DataFrame({"mets": ["MAM00001c"], "metsNoComp": ["MAM00001"], "metChEBIID": ["CHEBI:555"]})
    with pytest.raises(ValueError, match="written against 'CHEBI:900'"):
        correct_metabolites_table(table, read_human_gem_corrections(corrections_path))


def test_a_rename_onto_an_id_the_table_already_holds_raises(corrections_path):
    table = pd.DataFrame({"mets": ["MAM00003c", "MAM00009c"], "metsNoComp": ["MAM00003", "MAM00009"], "metKEGGID": ["", ""]})
    with pytest.raises(ValueError, match="already holds MAM00009c"):
        correct_metabolites_table(table, read_human_gem_corrections(corrections_path))


@pytest.mark.parametrize("bad_row, message", [
    (row("swap", "MAM00001c", "metChEBIID", "a", "b"), "kind"),
    (row("value", "MAM00001", "metChEBIID", "a", "b"), "compartment letter"),
    (row("value", "MAM00001c", "metsNoComp", "MAM00001", "MAM00002"), "species_id rows"),
    (row("value", "MAM00001c", "metChEBIID", "CHEBI:1", "CHEBI:1"), "equals the pinned"),
    (row("species_id", "MAM00001c", "mets", "MAM00001c", "MAM00002m"), "same compartment"),
    (row("species_id", "MAM00001c", "mets", "MAM00007c", "MAM00002c"), "pinned_value equal to its row_id"),
    (row("species_name", "MAM00001c", "name", "old", ""), "non-empty corrected name"),
])
def test_malformed_rows_are_refused(bad_row, message):
    with pytest.raises(ValueError, match=message):
        parse_corrections([bad_row])


def test_two_corrections_of_one_cell_and_chained_renames_are_refused():
    with pytest.raises(ValueError, match="second correction"):
        parse_corrections([row("value", "MAM00001c", "metChEBIID", "a", "b"), row("value", "MAM00001c", "metChEBIID", "a", "c")])
    with pytest.raises(ValueError, match="same id"):
        parse_corrections([row("species_id", "MAM00001c", "mets", "MAM00001c", "MAM00005c"),
                           row("species_id", "MAM00002c", "mets", "MAM00002c", "MAM00005c")])
    with pytest.raises(ValueError, match="itself renamed"):
        parse_corrections([row("species_id", "MAM00001c", "mets", "MAM00001c", "MAM00002c"),
                           row("species_id", "MAM00002c", "mets", "MAM00002c", "MAM00003c")])


def test_a_table_with_other_columns_is_refused(tmp_path):
    path = tmp_path / "corrections.csv"
    path.write_text("kind,row_id,column,pinned_value,corrected_value\n")
    with pytest.raises(ValueError, match="expected"):
        read_human_gem_corrections(path)


def test_the_sbml_rename_reaches_the_species_its_anchors_and_every_reference(corrections_path, tmp_path):
    corrections = read_human_gem_corrections(corrections_path)
    corrected = correct_sbml_text(SBML_TEXT, corrections)
    assert 'id="M_MAM00009c" name="Compound nine"' in corrected
    assert 'metaid="meta_M_MAM00009c"' in corrected and 'rdf:about="#meta_M_MAM00009c"' in corrected
    assert 'speciesReference species="M_MAM00009c"' in corrected
    assert "MAM00003c" not in corrected
    # the extracellular row of the old id keeps its id and its name
    assert 'id="M_MAM00003e" name="Compound three, C3:1 (Delta 2)"' in corrected and 'species="M_MAM00003e"' in corrected
    (tmp_path / "model.xml").write_text(SBML_TEXT)
    assert read_human_gem_sbml_text(tmp_path / "model.xml", corrections_path) == corrected
    assert read_human_gem_sbml_text(tmp_path / "model.xml", None) == SBML_TEXT


def test_the_sbml_charges_and_participants_follow_the_rename(corrections_path):
    from mechanistic_pathway_learning.graph.node_descriptors import metabolite_charges_from_sbml
    from mechanistic_pathway_learning.graph.reactome_import import HUMAN_GEM_REFERENCE_PATTERN

    corrected = correct_sbml_text(SBML_TEXT, read_human_gem_corrections(corrections_path))
    assert set(metabolite_charges_from_sbml(corrected)) == {"MAM00003", "MAM00009"}
    assert ("MAM00009", "c", "1") in HUMAN_GEM_REFERENCE_PATTERN.findall(corrected)


def test_an_sbml_name_that_no_longer_holds_the_pinned_name_raises(corrections_path):
    changed = SBML_TEXT.replace('id="M_MAM00003c" name="Compound three, C3:1 (Delta 2)"', 'id="M_MAM00003c" name="Something else"')
    with pytest.raises(ValueError, match="written against"):
        correct_sbml_text(changed, read_human_gem_corrections(corrections_path))


def test_an_sbml_rename_onto_a_species_it_holds_raises(corrections_path):
    clashing = SBML_TEXT.replace('id="M_MAM00009e"', 'id="M_MAM00009c"')
    with pytest.raises(ValueError, match="already holds species M_MAM00009c"):
        correct_sbml_text(clashing, read_human_gem_corrections(corrections_path))


def test_the_cobra_model_takes_the_name_and_the_rename_with_its_stoichiometry(corrections_path):
    cobra = pytest.importorskip("cobra")
    model = cobra.Model("fixture")
    old = cobra.Metabolite("MAM00003c", name="Compound three, C3:1 (Delta 2)", compartment="c")
    product = cobra.Metabolite("MAM00001c", name="Compound one", compartment="c")
    reaction = cobra.Reaction("MAR1")
    reaction.add_metabolites({old: -1.0, product: 2.0})
    model.add_reactions([reaction])
    correct_cobra_model(model, read_human_gem_corrections(corrections_path))
    renamed = model.metabolites.get_by_id("MAM00009c")
    assert renamed.name == "Compound nine" and "MAM00003c" not in model.metabolites
    assert model.reactions.MAR1.metabolites[renamed] == -1.0
    assert {metabolite.id for metabolite in model.reactions.MAR1.metabolites} == {"MAM00009c", "MAM00001c"}


def test_the_graph_builder_reads_the_model_through_the_corrections(corrections_path):
    pytest.importorskip("cobra")
    import cobra

    from mechanistic_pathway_learning.graph.build_physiology_graph import build_metabolic_layer

    model = cobra.Model("fixture")
    reaction = cobra.Reaction("MAR1")
    reaction.add_metabolites({cobra.Metabolite("MAM00003c", name="Compound three, C3:1 (Delta 2)", compartment="c"): -1.0,
                              cobra.Metabolite("MAM00001c", name="Compound one", compartment="c"): 1.0})
    model.add_reactions([reaction])
    nodes, edges = build_metabolic_layer(correct_cobra_model(model, read_human_gem_corrections(corrections_path)), {})
    renamed = nodes.set_index("node_id").loc["MAM00009c"]
    assert renamed.base_metabolite_id == "MAM00009" and renamed.display_name == "Compound nine"
    assert ((edges.source_id == "MAM00009c") & (edges.target_id == "MAR1") & (edges.relation_type == "substrate_of")).any()


def test_the_small_molecule_layer_joins_through_the_corrected_table(tmp_path, metabolites_path, monkeypatch):
    import mechanistic_pathway_learning.graph.build_physiology_graph as graph_builder

    corrections = write_corrections(tmp_path / "corrections.csv",
                                    [row("species_id", "MAM00001c", "mets", "MAM00001c", "MAM00008c")])
    monkeypatch.setattr(graph_builder, "read_human_gem_metabolites",
                        lambda path, **arguments: read_human_gem_metabolites(path, corrections, **arguments))
    small_molecules = tmp_path / "small_molecule.tsv"
    small_molecules.write_text("source\ttarget_genesymbol\tis_stimulation\tis_inhibition\tconsensus_stimulation\tconsensus_inhibition\n"
                               "11\tDRD1\t1\t0\t1\t0\n")
    nodes = pd.DataFrame({"node_id": ["MAM00008c", "MAM00001r"], "node_type": ["metabolite", "metabolite"]})
    _, edges = graph_builder.build_small_molecule_layer(nodes, small_molecules, metabolites_path)
    assert set(edges.source_id) == {"MAM00008c", "MAM00001r"}, "PubChem 11 is read as text (not 11.0) and reaches the renamed row"


def test_the_repository_table_parses():
    corrections = read_human_gem_corrections(DEFAULT_CORRECTIONS_PATH)
    assert corrections.species_ids == {"MAM03652c": "MAM03885c", "MAM20077m": "MAM20089m"}
    assert corrections.species_names == {"MAM03652c": ("Hexadecenoyl Ethanolamide, C16:1-Ethanolamide (Delta 9)", "Palmitoylethanolamide"),
                                         "MAM02766r": ("pristanic acid", "(2S)-pristanic acid")}
    chebi = {row_id: corrected for row_id, column, _, corrected in corrections.values if column == "metChEBIID"}
    assert chebi == {"MAM03323c": "CHEBI:49575", "MAM03323r": "CHEBI:49575", "MAM02505c": "CHEBI:27410", "MAM02973c": "CHEBI:84634",
                     "MAM02973m": "CHEBI:84634", "MAM02973r": "CHEBI:84634", "MAM03787c": "CHEBI:30245", "MAM03796e": "CHEBI:71466",
                     "MAM01511c": "", "MAM01511m": "",
                     "MAM00373c": "CHEBI:90819", "MAM00373n": "CHEBI:90819", "MAM00373r": "CHEBI:90819", "MAM00373x": "CHEBI:90819",
                     "MAM02766c": "CHEBI:761004;CHEBI:77268", "MAM02766e": "CHEBI:761004;CHEBI:77268",
                     "MAM02766r": "CHEBI:761004;CHEBI:77268", "MAM02766x": "CHEBI:761004;CHEBI:77268"}
    pristanate = "CC(C)CCC[C@@H](C)CCC[C@@H](C)CCC[C@H](C)C(=O)[O-]"
    assert {row_id for row_id, column, _, corrected in corrections.values if column == "metSmiles" and corrected == pristanate} == {
        "MAM02766c", "MAM02766e", "MAM02766r", "MAM02766x"}
    # Q5d: MAR20093 moves to the lysosome, on two added species; 15(R)-HEPE: MAR02560 and MAR02571 are rewritten, and
    # their nuclear and peroxisomal copies MAR02567 and MAR02577 are left as pinned, flagged for follow-up
    assert corrections.species_added == {"MAM03885l": "MAM03885e", "MAM01797l": "MAM01797c"}
    assert corrections.reaction_species == {"MAR20093": {"MAM03652c": "MAM03885l", "MAM02040c": "MAM02040l", "MAM01797c": "MAM01797l",
                                                         "MAM02674c": "MAM02674l"}}
    assert corrections.reaction_equations == {
        "MAR02560": ("MAM00373c + MAM02040c <=> MAM00375c + 2 MAM02039c", "MAM00375c + 2 MAM02026c -> MAM00373c + MAM02027c + MAM02040c"),
        "MAR02571": ("MAM00373r + MAM02040r <=> MAM00375r + 2 MAM02039r", "MAM00375r + 2 MAM02026r -> MAM00373r + MAM02027r + MAM02040r")}
    peroxidases = " or ".join(["ENSG00000116157", "ENSG00000117592", "ENSG00000164294", "ENSG00000167468", "ENSG00000176153",
                               "ENSG00000198704", "ENSG00000211445", "ENSG00000224586", "ENSG00000233276"])
    assert corrections.reaction_gene_rules == {"MAR02560": ("", peroxidases), "MAR02571": ("", peroxidases)}
    assert corrections.reaction_names == {reaction: ("15(R)-HEPE hydrolysis", "Glutathione: 15(R)-HpEPE oxidoreductase") for reaction in ("MAR02560", "MAR02571")}
    assert not {"MAR02567", "MAR02577"} & corrections.corrected_reactions()
    with open(DEFAULT_CORRECTIONS_PATH, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert all(row["source_1"].strip() and row["source_2"].strip() and row["ruling"].strip() for row in rows), "every row names two sources and its ruling"


# The species_added and reaction kinds, on a small cobra model written to SBML by cobra itself, so the SBML text is in
# the form the pinned file has (cobra wrote it) and the corrected text can be read back and compared with the corrected
# cobra model.

REACTION_ROWS = [
    row("species_id", "MAM00011c", "mets", "MAM00011c", "MAM00012c"),
    row("species_added", "MAM00012l", "copy_of", "", "MAM00012e"),
    row("species_added", "MAM00030l", "copy_of", "", "MAM00030c"),
    row("reaction_species", "MAR10", "MAM00011c", "MAM00011c", "MAM00012l"),
    row("reaction_species", "MAR10", "MAM00020c", "MAM00020c", "MAM00020l"),
    row("reaction_species", "MAR10", "MAM00030c", "MAM00030c", "MAM00030l"),
    row("reaction_species", "MAR10", "MAM00040c", "MAM00040c", "MAM00040l"),
    row("reaction_equation", "MAR20", "equation", "MAM00050c + MAM00020c <=> MAM00060c + 2 MAM00080c",
        "MAM00060c + 2 MAM00090c -> MAM00050c + MAM00091c + MAM00020c"),
    row("reaction_gene_rule", "MAR20", "gene_reaction_rule", "", "G1 or (G2 and G3)"),
    row("reaction_name", "MAR20", "name", "hydrolysis", "Glutathione: oxidoreductase"),
]

REACTION_METABOLITES_TSV = (
    "mets\tmetsNoComp\tmetChEBIID\tmetHMR2ID\tmetRetired\n"
    "MAM00011c\tMAM00011\tCHEBI:12\t\t\n"
    "MAM00012e\tMAM00012\tCHEBI:12\t\tm00012s\n"
    "MAM00030c\tMAM00030\tCHEBI:30\tm00030c\tm00030c\n"
    "MAM00030e\tMAM00030\tCHEBI:30\tm00030s\tm00030s\n"
)


def reaction_fixture_model():
    cobra = pytest.importorskip("cobra")
    model = cobra.Model("fixture")
    species = {}
    for identifier, name, formula, charge in [
        ("MAM00011c", "Amide", "C18H37NO2", 0), ("MAM00012e", "Amide", "C18H37NO2", 0), ("MAM00020c", "H2O", "H2O", 0),
        ("MAM00020l", "H2O", "H2O", 0), ("MAM00030c", "amine", "C2H8NO", 1), ("MAM00040c", "acid", "C16H31O2", -1),
        ("MAM00040l", "acid", "C16H31O2", -1), ("MAM00050c", "alcohol", "C20H29O3", -1), ("MAM00060c", "hydroperoxide", "C20H29O4", -1),
        ("MAM00080c", "H+", "H", 1), ("MAM00090c", "GSH", "C10H16N3O6S", -1), ("MAM00091c", "GSSG", "C20H30N6O12S2", -2)]:
        species[identifier] = cobra.Metabolite(identifier, name=name, formula=formula, charge=charge, compartment=identifier[-1])
        species[identifier].annotation = {"chebi": f"CHEBI:{identifier[3:8]}"}
    hydrolysis = cobra.Reaction("MAR10", name="MAR10", lower_bound=0.0, upper_bound=1000.0)
    hydrolysis.add_metabolites({species["MAM00020c"]: -1, species["MAM00011c"]: -1, species["MAM00030c"]: 1, species["MAM00040c"]: 1})
    hydrolysis.gene_reaction_rule = "G4"
    unbalanced = cobra.Reaction("MAR20", name="hydrolysis", lower_bound=-1000.0, upper_bound=1000.0)
    unbalanced.add_metabolites({species["MAM00050c"]: -1, species["MAM00020c"]: -1, species["MAM00060c"]: 1, species["MAM00080c"]: 2})
    peroxidase = cobra.Reaction("MAR30", name="the peroxidases' own reaction", lower_bound=0.0, upper_bound=1000.0)
    peroxidase.add_metabolites({species["MAM00090c"]: -2, species["MAM00091c"]: 1, species["MAM00012e"]: -1, species["MAM00040l"]: 1,
                                species["MAM00020l"]: 1})
    peroxidase.gene_reaction_rule = "G1 or G2 or G3"
    model.add_reactions([hydrolysis, unbalanced, peroxidase])
    return model


@pytest.fixture
def reaction_corrections(tmp_path):
    return read_human_gem_corrections(write_corrections(tmp_path / "reaction_corrections.csv", REACTION_ROWS))


@pytest.fixture
def fixture_sbml(tmp_path) -> str:
    from cobra.io import write_sbml_model

    path = tmp_path / "fixture.xml"
    write_sbml_model(reaction_fixture_model(), str(path))
    return path.read_text()


def test_equations_and_gene_rules_are_parsed_and_compared_in_one_order():
    assert parse_equation("MAM00060c + 2 MAM00090c -> MAM00050c + MAM00091c") == (
        {"MAM00060c": -1.0, "MAM00090c": -2.0, "MAM00050c": 1.0, "MAM00091c": 1.0}, False)
    assert parse_equation("MAM00001c <=> 0.5 MAM00002c")[1] is True
    for bad in ("MAM00001c = MAM00002c", "MAM00001c -> MAM00001c + MAM00002c", "MAM00001 -> MAM00002c", "-1 MAM00001c -> MAM00002c"):
        with pytest.raises(ValueError):
            parse_equation(bad)
    assert parse_gene_rule("") is None
    assert canonical_gene_rule(parse_gene_rule("(G3 and G2) or G1")) == canonical_gene_rule(parse_gene_rule("G1 or (G2 and G3)")) == "((G2 and G3) or G1)"
    assert canonical_gene_rule(parse_gene_rule("G1 or (G2 or G3)")) == "(G1 or G2 or G3)"
    for bad in ("G1 or", "(G1 and G2", "G1 G2", "and G1"):
        with pytest.raises(ValueError):
            parse_gene_rule(bad)


def test_the_reaction_kinds_are_split(reaction_corrections):
    assert reaction_corrections.species_added == {"MAM00012l": "MAM00012e", "MAM00030l": "MAM00030c"}
    assert reaction_corrections.reaction_species == {"MAR10": {"MAM00011c": "MAM00012l", "MAM00020c": "MAM00020l", "MAM00030c": "MAM00030l",
                                                               "MAM00040c": "MAM00040l"}}
    assert set(reaction_corrections.reaction_equations) == set(reaction_corrections.reaction_gene_rules) == set(reaction_corrections.reaction_names) == {"MAR20"}
    assert reaction_corrections.corrected_reactions() == {"MAR10", "MAR20"}


def test_an_added_species_copies_its_corrected_template_after_it_and_leaves_the_compartment_row_cells_empty(tmp_path, reaction_corrections):
    path = tmp_path / "metabolites.tsv"
    path.write_text(REACTION_METABOLITES_TSV)
    corrections = write_corrections(tmp_path / "corrections.csv", REACTION_ROWS + [row("value", "MAM00030c", "metChEBIID", "CHEBI:30", "CHEBI:31")])
    table = read_human_gem_metabolites(path, corrections, dtype=str, keep_default_na=False)
    assert list(table.mets) == ["MAM00012c", "MAM00012e", "MAM00012l", "MAM00030c", "MAM00030l", "MAM00030e"]
    added = table.set_index("mets").loc["MAM00030l"]
    assert (added.metsNoComp, added.metChEBIID, added.metHMR2ID, added.metRetired) == ("MAM00030", "CHEBI:31", "", "")
    assert table.set_index("mets").at["MAM00012l", "metRetired"] == ""
    with_nan = read_human_gem_metabolites(path, corrections).set_index("mets")
    assert pd.isna(with_nan.at["MAM00030l", "metHMR2ID"]) and with_nan.at["MAM00030e", "metHMR2ID"] == "m00030s"


def test_an_added_species_the_table_already_holds_raises(reaction_corrections):
    table = pd.DataFrame({"mets": ["MAM00030c", "MAM00030l"], "metsNoComp": ["MAM00030", "MAM00030"]})
    with pytest.raises(ValueError, match="already holds it"):
        correct_metabolites_table(table, reaction_corrections)


def test_the_sbml_takes_the_added_species_and_the_corrected_reactions(fixture_sbml, reaction_corrections):
    from mechanistic_pathway_learning.graph.node_descriptors import metabolite_charges_from_sbml
    from mechanistic_pathway_learning.graph.reactome_import import read_human_gem_participants

    corrected = correct_sbml_text(fixture_sbml, reaction_corrections)
    added = re.search(r'<species [^>]*id="M_MAM00030l"[^>]*>', corrected).group(0)
    assert 'compartment="l"' in added and 'metaid="meta_M_MAM00030l"' in added and 'fbc:charge="1"' in added
    assert 'rdf:about="#meta_M_MAM00030l"' in corrected and 'id="M_MAM00030c"' in corrected
    participants = read_human_gem_participants(corrected, {"MAM00012", "MAM00030", "MAM00090"})
    assert sorted(participants["MAR10"]) == [("in", "MAM00012", "l", 1.0), ("in", "MAM00020", "l", 1.0), ("out", "MAM00030", "l", 1.0), ("out", "MAM00040", "l", 1.0)]
    assert sorted(participants["MAR20"]) == [("in", "MAM00060", "c", 1.0), ("in", "MAM00090", "c", 2.0), ("out", "MAM00020", "c", 1.0),
                                             ("out", "MAM00050", "c", 1.0), ("out", "MAM00091", "c", 1.0)]
    opening = re.search(r'<reaction [^>]*id="R_MAR20"[^>]*>', corrected).group(0)
    assert 'name="Glutathione: oxidoreductase"' in opening and 'reversible="false"' in opening and 'fbc:lowerFluxBound="cobra_0_bound"' in opening
    assert "MAM00011c" not in corrected and 'species="M_MAM00012c"' not in corrected, "the rename reaches every reference, and MAR10 moved"
    assert metabolite_charges_from_sbml(corrected)["MAM00030"] == 1


def test_the_corrected_sbml_and_the_corrected_cobra_model_are_one_model(fixture_sbml, reaction_corrections, tmp_path):
    from cobra.io import read_sbml_model

    path = tmp_path / "corrected.xml"
    path.write_text(correct_sbml_text(fixture_sbml, reaction_corrections))
    (tmp_path / "pinned.xml").write_text(fixture_sbml)
    write_corrections(tmp_path / "reaction_corrections.csv", REACTION_ROWS)

    def signature(model):
        return ({reaction.id: (reaction.name, sorted((metabolite.id, amount) for metabolite, amount in reaction.metabolites.items()), reaction.bounds,
                               canonical_gene_rule(parse_gene_rule(reaction.gene_reaction_rule))) for reaction in model.reactions},
                {metabolite.id: (metabolite.name, metabolite.compartment, metabolite.formula, metabolite.charge) for metabolite in model.metabolites})

    from_text = read_sbml_model(str(path))
    from_model = read_human_gem_cobra_model(tmp_path / "pinned.xml", tmp_path / "reaction_corrections.csv")
    assert signature(from_text) == signature(from_model)
    reactions, species = signature(from_model)
    assert reactions["MAR20"] == ("Glutathione: oxidoreductase", sorted([("MAM00060c", -1.0), ("MAM00090c", -2.0), ("MAM00050c", 1.0), ("MAM00091c", 1.0),
                                                                          ("MAM00020c", 1.0)]), (0.0, 1000.0), "((G2 and G3) or G1)")
    assert reactions["MAR10"][1] == sorted([("MAM00012l", -1.0), ("MAM00020l", -1.0), ("MAM00030l", 1.0), ("MAM00040l", 1.0)])
    assert species["MAM00012l"] == ("Amide", "l", "C18H37NO2", 0) and species["MAM00012c"] == ("Amide", "c", "C18H37NO2", 0)
    assert from_model.reactions.MAR20.check_mass_balance() == {}


def test_the_graph_builder_sees_the_moved_and_rewritten_reactions(reaction_corrections):
    from mechanistic_pathway_learning.graph.build_physiology_graph import build_metabolic_layer

    nodes, edges = build_metabolic_layer(correct_cobra_model(reaction_fixture_model(), reaction_corrections), {})
    reactions = nodes[nodes.node_type == "reaction"].set_index("node_id")
    assert reactions.at["MAR10", "compartment"] == "l" and not reactions.at["MAR20", "reversible"]
    assert reactions.at["MAR20", "display_name"] == "Glutathione: oxidoreductase"
    assert set(edges[(edges.relation_type == "catalyzed_by") & (edges.target_id == "MAR20")].source_id) == {"G1", "G2", "G3"}
    assert ((edges.source_id == "MAM00090c") & (edges.target_id == "MAR20") & (edges.stoichiometric_coefficient == 2.0)).any()
    assert nodes.set_index("node_id").at["MAM00012c", "degree"] == 0, "the renamed cytosolic row stays, in no reaction"


@pytest.mark.parametrize("changed_row, message", [
    (row("reaction_name", "MAR20", "name", "something else", "Glutathione: oxidoreductase"), "written against 'something else'"),
    (row("reaction_equation", "MAR20", "equation", "MAM00050c + MAM00020c -> MAM00060c + 2 MAM00080c", "MAM00060c + 2 MAM00090c -> MAM00050c + MAM00091c + MAM00020c"),
     "equation the correction was written against"),
    (row("reaction_gene_rule", "MAR20", "gene_reaction_rule", "G9", "G1 or (G2 and G3)"), "written against"),
    (row("reaction_gene_rule", "MAR20", "gene_reaction_rule", "", "G1 or G8"), "no gene product|no species|G8"),
    (row("reaction_species", "MAR10", "MAM00050c", "MAM00050c", "MAM00020l"), "no participant|0 times"),
    (row("reaction_species", "MAR10", "MAM00011c", "MAM00011c", "MAM00020l"), "formula or charge"),
])
def test_a_reaction_correction_against_a_stale_pinned_value_raises_in_the_sbml_and_the_model(fixture_sbml, changed_row, message):
    kind = changed_row["kind"]
    rows = [entry for entry in REACTION_ROWS if not (entry["row_id"] == changed_row["row_id"] and entry["kind"] == kind)] + [changed_row]
    corrections = parse_corrections(rows)
    with pytest.raises(ValueError, match=message):
        correct_sbml_text(fixture_sbml, corrections)
    if "G8" not in str(changed_row["corrected_value"]):  # cobra adds a gene it does not hold, so only the SBML can refuse it
        with pytest.raises(ValueError, match=message):
            correct_cobra_model(reaction_fixture_model(), corrections)


def test_an_added_species_the_sbml_or_the_model_already_holds_raises(fixture_sbml):
    corrections = parse_corrections([row("species_added", "MAM00040l", "copy_of", "", "MAM00040c")])
    with pytest.raises(ValueError, match="already holds"):
        correct_sbml_text(fixture_sbml, corrections)
    with pytest.raises(ValueError, match="already holds it"):
        correct_cobra_model(reaction_fixture_model(), corrections)


@pytest.mark.parametrize("bad_row, message", [
    (row("reaction_name", "MAM00001c", "name", "a", "b"), "reaction id"),
    (row("reaction_name", "MAR1", "name", "a", ""), "non-empty corrected name"),
    (row("reaction_equation", "MAR1", "stoichiometry", "MAM00001c -> MAM00002c", "MAM00002c -> MAM00001c"), "column equation"),
    (row("reaction_equation", "MAR1", "equation", "MAM00001c -> MAM00002c", "MAM00002c = MAM00001c"), "neither"),
    (row("reaction_gene_rule", "MAR1", "gene_reaction_rule", "", "G1 or"), "malformed"),
    (row("reaction_species", "MAR1", "MAM00001c", "MAM00002c", "MAM00001l"), "pinned participant"),
    (row("species_added", "MAM00001l", "copy_of", "MAM00001l", "MAM00001c"), "empty pinned_value"),
    (row("species_added", "MAM00001l", "copy_of", "", "MAM00002c"), "same metabolite"),
    (row("species_added", "MAM00001l", "copy_of", "", "MAM00001l"), "equals the pinned|same metabolite"),
])
def test_malformed_reaction_and_added_species_rows_are_refused(bad_row, message):
    with pytest.raises(ValueError, match=message):
        parse_corrections([bad_row])


def test_a_reaction_takes_participant_moves_or_an_equation_not_both_and_no_participants_merge():
    with pytest.raises(ValueError, match="both reaction_species rows and a reaction_equation row"):
        parse_corrections([row("reaction_species", "MAR1", "MAM00001c", "MAM00001c", "MAM00001l"),
                           row("reaction_equation", "MAR1", "equation", "MAM00001c -> MAM00002c", "MAM00001l -> MAM00002c")])
    with pytest.raises(ValueError, match="would merge"):
        parse_corrections([row("reaction_species", "MAR1", "MAM00001c", "MAM00001c", "MAM00001l"),
                           row("reaction_species", "MAR1", "MAM00002c", "MAM00002c", "MAM00001l")])
    with pytest.raises(ValueError, match="added species is also a rename"):
        parse_corrections([row("species_added", "MAM00001l", "copy_of", "", "MAM00001c"), row("species_id", "MAM00001l", "mets", "MAM00001l", "MAM00002l")])


def test_a_reaction_or_template_absent_from_the_files_is_reported(fixture_sbml, reaction_corrections):
    table = pd.DataFrame({"mets": ["MAM00011c", "MAM00030c"]})
    assert corrections_without_their_row(table, None, reaction_corrections) == ["species_added MAM00012l"]
    without_mar20 = re.sub(r'<reaction [^>]*id="R_MAR20".*?</reaction>', "", fixture_sbml, flags=re.DOTALL)
    assert corrections_without_their_row(table, without_mar20, reaction_corrections)[-1:] == ["reaction MAR20"]
