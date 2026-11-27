"""Guards on Human-GEM's metabolite identifiers and corrected reactions, read after configs/human_gem_corrections.csv is
applied (rulings Q2 and Q5c of 20 November 2026, docs/item37_rulings_draft_2026-11-13.md section 21; Q5d, the
15(R)-HEPE repair, NAAA's other reactions and the palmitoylethanolamide transport of the same day, section 22).

Q2: no metChEBIID may resolve to an isotopically labelled ChEBI record, or be absent from the pinned ChEBI release
(data/raw/chebi/chebi_core.obo.gz, release 257). A pass of 20 November 2026 found six metabolites (ten compartment
rows) annotated with a deuterated internal standard in place of the compound, diazepam-d8 for diazepam among them; the
corrections table repairs them. A record counts as labelled on any of the three signals that pass used: an isotopic
layer in its InChI, an isotope atom in its SMILES, or descent by is_a from CHEBI:139358 "isotopically modified
compound" (which holds the deuterated and tritiated classes).

Q5c: the compartment rows that share one metsNoComp must agree on the first block of the InChIKey of their own InChI
and on their model name (the SBML name). Before the corrections both cases of ruling Q5 fail it: MAM03652's cytosolic
row is palmitoylethanolamide, a different key, and MAM20077's two rows carry the names of two unrelated compounds.

Q5d, 15(R)-HEPE, NAAA's other reactions and the transport: the corrected reactions are what the rulings say (MAR20093
to MAR20097 wholly in the lysosome, MAR20096 and MAR20097 with ASAH1 beside NAAA, MAR05339 without NAAA; MAR02560 and
MAR02571 the one-way glutathione-dependent reduction with the glutathione peroxidases; the added MAR90001 a reversible,
gene-free palmitoylethanolamide transport from cytosol to lysosome), every reaction the corrections touch or add
balances in elements and charge, and no reaction of the model is less balanced in charge than the pinned one is.

The cases these guards find that no ruling has repaired yet are listed below by name, each with its reason, so the
tests pass now and fail on any new case. A listed case that no longer occurs fails as well, so the list is shortened
when its ruling lands rather than left stale.

The tests read gitignored raw data and skip when it is not on disk (scripts/fetch_raw_sources.sh fetches it).
"""
from __future__ import annotations

import gzip
import html
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pytest

from mechanistic_pathway_learning.graph.human_gem_corrections import (
    corrections_without_their_row,
    read_human_gem_corrections,
    read_human_gem_metabolites,
    read_human_gem_sbml_text,
)

HUMAN_GEM_DIRECTORY = Path("data/raw/Human-GEM/model")
METABOLITES_PATH = HUMAN_GEM_DIRECTORY / "metabolites.tsv"
SBML_PATH = HUMAN_GEM_DIRECTORY / "Human-GEM.xml"
YAML_PATH = HUMAN_GEM_DIRECTORY / "Human-GEM.yml"
CHEBI_PATH = Path("data/raw/chebi/chebi_core.obo.gz")
ISOTOPICALLY_MODIFIED_COMPOUND = "CHEBI:139358"
SMILES_ISOTOPE_ATOM = re.compile(r"\[\d+[A-Za-z]")

# Q2. The 17 metabolites whose metChEBIID is in no record of ChEBI 257, found by the pass of 20 November 2026
# (human_gem_chebi_audit.csv of that pass). Ruling Q3: each takes upstream Human-GEM's replacement, checked one by one;
# until that curation is done they stay here.
ABSENT_FROM_CHEBI_PENDING_Q3 = {
    ("MAM00341", "CHEBI:1038735"): "13,16,19-docosatrienoic acid; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM00604", "CHEBI:805752"): "21-hydroxyallopregnanolone; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM00623", "CHEBI:387060"): "26-hydroxycholesterol; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM00664", "CHEBI:240943"): "2-methylbutyrylglycine; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM00821", "CHEBI:742324"): "3-methoxytyramine; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM01161", "CHEBI:308079"): "6-hydroxymelatonin; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM01315", "CHEBI:730073"): "alloxan; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM01450", "CHEBI:1307929"): "cholesterol; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM01597", "CHEBI:1146900"): "CoA; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM01766", "CHEBI:708641"): "ecgonine; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM02744", "CHEBI:583972"): "phylloquinone; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM03136", "CHEBI:1127735"): "vanillylmandelate; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM03142", "CHEBI:283119"): "vitamin D3; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM03155", "CHEBI:1305691"): "xylitol; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM03569", "CHEBI:603631"): "cis,cis-11,14-eicosadienoic acid; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM03630", "CHEBI:356660"): "Glycylproline; Q3 curation pending (upstream replacement, checked one by one)",
    ("MAM03813", "CHEBI:580913"): "1-Heptadecanoylglycerophosphocholine; Q3 curation pending (upstream replacement, checked one by one)",
}
# Q2. H+ is annotated as CHEBI:24636 "proton", the 1H ion, whose InChI and SMILES are isotopic by construction, where
# Reactome uses hydron, CHEBI:15378. Ruling Q4 (amendment item 37o) is that the duplicate proton is merged into one
# node per compartment; the merge is not yet built, so the guard exempts the proton until it lands.
LABELLED_PENDING_Q4 = {
    ("MAM02039", "CHEBI:24636"): "H+ annotated as proton rather than hydron; ruled a merge (Q4, item 37o), not yet built",
}
# Q5c. Disagreements the guard finds in the corrected model that are not yet adjudicated. Empty since 20 November 2026:
# the two the guard found that day beyond ruling Q5, the c, n, r and x structure of MAM00373 (15(R)-HEPE) and the name
# of MAM02766r, were repaired in configs/human_gem_corrections.csv when the owner accepted them ("MAM00373 and MAM02766
# suggestions accepted").
INCHIKEY_DISAGREEMENTS_NOT_YET_ADJUDICATED: dict[str, str] = {}
NAME_DISAGREEMENTS_NOT_YET_ADJUDICATED: dict[str, str] = {}
# 15(R)-HEPE. The nuclear and peroxisomal copies of "15(R)-HEPE hydrolysis", off by +2 in charge as MAR02560 and
# MAR02571 were; the owner, 20 November 2026: they stay as pinned and are "flagged for follow-up". The model has no
# GSSG in either compartment, so the rewrite of the other two would need species there.
LEFT_AS_PINNED_FLAGGED_FOR_FOLLOW_UP = {
    "MAR02567": "15(R)-HEPE hydrolysis, nucleus: left as pinned, flagged for follow-up (the owner, 20 November 2026); unadjudicated",
    "MAR02577": "15(R)-HEPE hydrolysis, peroxisome: left as pinned, flagged for follow-up (the owner, 20 November 2026); unadjudicated",
}
# Species in no reaction after the corrections; the pinned model has none. Each is the cytosolic substrate of one of
# NAAA's reactions, which was its only reaction and moved to the lysosome (the owner, 20 November 2026: "accept the
# five NAAA verdicts"). Whether the rows should stay is not ruled, so they stay and are listed. MAM03885c, the
# cytosolic palmitoylethanolamide row ruling Q5a gave MAM03652c, was listed here until the transport MAR90001 (the
# owner, 20 November 2026: "yes, option 1 as long as it passes the check") put it in a reaction again.
SPECIES_IN_NO_REACTION_NOT_YET_ADJUDICATED = {
    "MAM03550c": "cytosolic N-dodecanoylethanolamine, whose only reaction MAR20094 moved to the lysosome; unadjudicated",
    "MAM03977c": "cytosolic N-tetradecanoylethanolamine, whose only reaction MAR20095 moved to the lysosome; unadjudicated",
    "MAM20075c": "cytosolic N-dodecanoylsphingosine, whose only reaction MAR20097 moved to the lysosome; unadjudicated",
    "MAM20076n": "N-hexadecanoylsphingosine, compartment c despite its n suffix, whose only reaction MAR20096 moved to the lysosome; unadjudicated",
}
NAAA, ASAH1 = "ENSG00000138744", "ENSG00000104763"
GLUTATHIONE_PEROXIDASES = {"ENSG00000116157", "ENSG00000117592", "ENSG00000164294", "ENSG00000167468", "ENSG00000176153",
                           "ENSG00000198704", "ENSG00000211445", "ENSG00000224586", "ENSG00000233276"}


def read_chebi_records(path: Path) -> tuple[dict[str, dict], dict[str, str]]:
    """(record by primary id, primary id by secondary id) from chebi_core.obo(.gz). A record holds name, inchi,
    smiles, is_a (a list) and obsolete."""
    opener = gzip.open if str(path).endswith(".gz") else open
    records: dict[str, dict] = {}
    primary_of: dict[str, str] = {}
    current = None
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line in ("[Term]", "[Typedef]"):
                current = None
            elif line.startswith("id: CHEBI:"):
                current = records.setdefault(line[4:], {"id": line[4:], "is_a": [], "obsolete": False})
            elif current is None:
                continue
            elif line.startswith("name: "):
                current["name"] = line[6:]
            elif line.startswith("alt_id: "):
                primary_of[line[8:]] = current["id"]
            elif line.startswith("is_a: CHEBI:"):
                current["is_a"].append(line[6:].split()[0])
            elif line.startswith("is_obsolete: true"):
                current["obsolete"] = True
            elif "chemrof:inchi_string" in line:
                current["inchi"] = line.split('"')[1]
            elif "chemrof:smiles_string" in line:
                current["smiles"] = line.split('"')[1]
    return records, primary_of


def descendants(root: str, records: dict[str, dict]) -> set[str]:
    """root and every record below it by is_a."""
    children: dict[str, set[str]] = defaultdict(set)
    for identifier, record in records.items():
        for parent in record["is_a"]:
            children[parent].add(identifier)
    found, stack = set(), [root]
    while stack:
        identifier = stack.pop()
        if identifier not in found:
            found.add(identifier)
            stack.extend(children[identifier])
    return found


def isotope_signals(record: dict, labelled_classes: set[str]) -> list[str]:
    """Which of the three isotope signals a ChEBI record carries; empty when it carries none."""
    signals = []
    inchi_layers = record.get("inchi", "").split("/")[1:]
    if any(layer.startswith("i") for layer in inchi_layers):
        signals.append("InChI isotopic layer")
    if SMILES_ISOTOPE_ATOM.search(record.get("smiles", "")):
        signals.append("SMILES isotope atom")
    if record["id"] in labelled_classes and record["id"] != ISOTOPICALLY_MODIFIED_COMPOUND:
        signals.append(f"descends from {ISOTOPICALLY_MODIFIED_COMPOUND}")
    return signals


def chebi_problems(metabolites: pd.DataFrame, records: dict[str, dict], primary_of: dict[str, str]) -> tuple[dict, dict]:
    """({(metsNoComp, ChEBI id): reason} absent from the release, {(metsNoComp, ChEBI id): signals} labelled)."""
    labelled_classes = descendants(ISOTOPICALLY_MODIFIED_COMPOUND, records)
    absent, labelled = {}, {}
    for base, cell in zip(metabolites["metsNoComp"], metabolites["metChEBIID"]):
        for chebi_id in (part.strip() for part in str(cell).split(";")):
            if not chebi_id:
                continue
            record = records.get(primary_of.get(chebi_id, chebi_id))
            if record is None:
                absent[(base, chebi_id)] = "not in the pinned ChEBI release"
            elif signals := isotope_signals(record, labelled_classes):
                labelled[(base, chebi_id)] = "; ".join(signals)
    return absent, labelled


def model_names(sbml_text: str) -> dict[str, str]:
    """Species id (without M_) -> its SBML name."""
    names = {}
    for tag in re.finditer(r"<species [^>]*>", sbml_text):
        attributes = dict(re.findall(r'([\w:]+)="([^"]*)"', tag.group(0)))
        if attributes.get("id", "").startswith("M_"):
            names[attributes["id"][2:]] = html.unescape(attributes.get("name", ""))
    return names


def compartment_disagreements(metabolites: pd.DataFrame, names: dict[str, str], inchikey_of) -> tuple[dict, dict]:
    """({metsNoComp: {species: key block}} where the rows disagree on the first InChIKey block of their own InChI,
    {metsNoComp: {species: name}} where they disagree on the model name). A row without an InChI takes no part in the
    first."""
    keys: dict[str, dict[str, str]] = defaultdict(dict)
    labels: dict[str, dict[str, str]] = defaultdict(dict)
    for species, base, inchi_text in zip(metabolites["mets"], metabolites["metsNoComp"], metabolites["metInChI"]):
        labels[base][species] = names.get(species, "")
        if inchi_text.strip():
            key = inchikey_of(inchi_text.strip())
            keys[base][species] = key.split("-")[0] if key else "<no key>"
    return ({base: by_row for base, by_row in keys.items() if len(set(by_row.values())) > 1},
            {base: by_row for base, by_row in labels.items() if len(set(by_row.values())) > 1})


def compare_with_known(found: dict, known: dict, what: str) -> None:
    new = {case: found[case] for case in found if case not in known}
    gone = sorted(case for case in known if case not in found)
    assert not new, f"{what}, a case no ruling covers: {new}"
    assert not gone, f"{what}: listed as known but no longer found, so remove it from the list here: {gone}"


# Unit tests of the guards' own logic, on records written here (no raw data needed).

def test_each_isotope_signal_is_read_and_an_unlabelled_record_carries_none():
    records = {
        "CHEBI:139358": {"id": "CHEBI:139358", "is_a": [], "obsolete": False},
        "CHEBI:76107": {"id": "CHEBI:76107", "is_a": ["CHEBI:139358"], "obsolete": False},
        "CHEBI:1": {"id": "CHEBI:1", "is_a": ["CHEBI:76107"], "obsolete": False, "inchi": "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3/i1D3"},
        "CHEBI:2": {"id": "CHEBI:2", "is_a": [], "obsolete": False, "smiles": "[13CH3]O"},
        "CHEBI:3": {"id": "CHEBI:3", "is_a": [], "obsolete": False, "inchi": "InChI=1S/CH4O/c1-2/h2H,1H3", "smiles": "CO"},
    }
    classes = descendants("CHEBI:139358", records)
    assert isotope_signals(records["CHEBI:1"], classes) == ["InChI isotopic layer", "descends from CHEBI:139358"]
    assert isotope_signals(records["CHEBI:2"], classes) == ["SMILES isotope atom"]
    assert isotope_signals(records["CHEBI:3"], classes) == []
    # a stereo layer (/t, /b) or a protonation layer (/p) is not isotopic; an explicit-hydrogen SMILES atom [H] is not an isotope
    assert isotope_signals({"id": "CHEBI:4", "is_a": [], "inchi": "InChI=1S/C3H7NO2/c1-2(4)3(5)6/h2H,4H2,1H3,(H,5,6)/p-1/t2-/m0/s1",
                            "smiles": "[H][C@](C)(N)C([O-])=O"}, classes) == []


def test_the_problems_resolve_secondary_ids_and_split_cells():
    records = {"CHEBI:10": {"id": "CHEBI:10", "is_a": [], "obsolete": False, "inchi": "InChI=1S/CH4/h1H4"},
               "CHEBI:11": {"id": "CHEBI:11", "is_a": [], "obsolete": False, "inchi": "InChI=1S/CH4/h1H4/i1+1"}}
    table = pd.DataFrame({"metsNoComp": ["MAM1", "MAM2", "MAM3"], "metChEBIID": ["CHEBI:99", "CHEBI:10;CHEBI:12", ""]})
    absent, labelled = chebi_problems(table, records, {"CHEBI:99": "CHEBI:10", "CHEBI:12": "CHEBI:11"})
    assert absent == {}
    assert labelled == {("MAM2", "CHEBI:12"): "InChI isotopic layer"}
    absent, _ = chebi_problems(pd.DataFrame({"metsNoComp": ["MAM4"], "metChEBIID": ["CHEBI:77"]}), records, {})
    assert absent == {("MAM4", "CHEBI:77"): "not in the pinned ChEBI release"}


def test_compartment_rows_are_compared_on_key_block_and_name():
    table = pd.DataFrame({"mets": ["MAM1c", "MAM1e", "MAM2c", "MAM2m"], "metsNoComp": ["MAM1", "MAM1", "MAM2", "MAM2"],
                          "metInChI": ["InChI=A", "InChI=B", "InChI=A", ""]})
    keys = {"InChI=A": "AAAA-BBBB-N", "InChI=B": "CCCC-BBBB-N"}
    key_disagreements, name_disagreements = compartment_disagreements(
        table, {"MAM1c": "x", "MAM1e": "x", "MAM2c": "y", "MAM2m": "z"}, keys.get)
    assert key_disagreements == {"MAM1": {"MAM1c": "AAAA", "MAM1e": "CCCC"}}
    assert name_disagreements == {"MAM2": {"MAM2c": "y", "MAM2m": "z"}}
    with pytest.raises(AssertionError, match="no ruling covers"):
        compare_with_known(key_disagreements, {}, "InChIKey")
    with pytest.raises(AssertionError, match="no longer found"):
        compare_with_known({}, {"MAM9": "fixed"}, "InChIKey")


# The guards on the pinned files.

needs_model = pytest.mark.skipif(not (METABOLITES_PATH.exists() and SBML_PATH.exists()), reason="the pinned Human-GEM model is not present")
needs_chebi = pytest.mark.skipif(not CHEBI_PATH.exists(), reason="the pinned ChEBI ontology is not present")


@pytest.fixture(scope="module")
def corrected_metabolites() -> pd.DataFrame:
    return read_human_gem_metabolites(METABOLITES_PATH, dtype=str, keep_default_na=False)


@pytest.fixture(scope="module")
def corrected_sbml_text() -> str:
    return read_human_gem_sbml_text(SBML_PATH)


@needs_model
def test_every_correction_finds_its_row_in_the_pinned_files(corrected_sbml_text):
    pinned = pd.read_csv(METABOLITES_PATH, sep="\t", dtype=str, keep_default_na=False)
    assert corrections_without_their_row(pinned, SBML_PATH.read_text(), read_human_gem_corrections()) == []


@needs_model
def test_the_renamed_ids_are_unused_in_the_pinned_files_and_used_once_after():
    corrections = read_human_gem_corrections()
    texts = [path.read_text() for path in (METABOLITES_PATH, SBML_PATH, YAML_PATH) if path.exists()]
    for new in list(corrections.species_ids.values()) + list(corrections.species_added) + list(corrections.reactions_added):
        assert all(new not in text for text in texts), f"{new} is already in a pinned Human-GEM file"
    assert "MAM20089" not in "".join(texts), "MAM20089 was to be an id unused by the pinned model"


@needs_model
def test_the_renames_reach_the_table_and_the_sbml(corrected_metabolites, corrected_sbml_text):
    rows = corrected_metabolites.set_index("mets")
    assert rows.at["MAM03885c", "metsNoComp"] == "MAM03885" and rows.at["MAM03885c", "metChEBIID"] == "CHEBI:71464"
    assert rows.at["MAM20089m", "metsNoComp"] == "MAM20089" and rows.at["MAM20089m", "metChEBIID"] == "CHEBI:29144"
    assert "MAM03652c" not in rows.index and "MAM20077m" not in rows.index
    names = model_names(corrected_sbml_text)
    assert names["MAM03885c"] == "Palmitoylethanolamide" and "MAM03652c" not in names and "MAM20077m" not in names
    # the renames reach every speciesReference: no reference to an old id is left. MAM20089m keeps its reactions
    assert 'species="M_MAM20089m"' in corrected_sbml_text and 'species="M_MAM03885l"' in corrected_sbml_text
    # MAM03885c's only reaction, MAR20093, moved to the lysosome (Q5d); it is in the added transport MAR90001 alone
    assert 'species="M_MAM03652c"' not in corrected_sbml_text and 'species="M_MAM20077m"' not in corrected_sbml_text
    assert reactions_of(corrected_sbml_text, "MAM03885c") == {"MAR90001"} and 'id="M_MAM03885c"' in corrected_sbml_text


@needs_model
@needs_chebi
def test_no_chebi_id_is_isotopically_labelled_or_absent_from_the_pinned_release(corrected_metabolites):
    """Ruling Q2: would have caught the six deuterated annotations and the 17 absent ids."""
    records, primary_of = read_chebi_records(CHEBI_PATH)
    absent, labelled = chebi_problems(corrected_metabolites, records, primary_of)
    compare_with_known(absent, ABSENT_FROM_CHEBI_PENDING_Q3, "a metChEBIID absent from ChEBI 257")
    compare_with_known(labelled, LABELLED_PENDING_Q4, "a metChEBIID that is an isotopically labelled ChEBI record")


@needs_model
@needs_chebi
def test_the_guard_catches_the_six_deuterated_annotations_in_the_pinned_table():
    """The guard checked against the defect it was written for: without the corrections it finds all six."""
    records, primary_of = read_chebi_records(CHEBI_PATH)
    pinned = pd.read_csv(METABOLITES_PATH, sep="\t", dtype=str, keep_default_na=False)
    _, labelled = chebi_problems(pinned, records, primary_of)
    assert set(labelled) - set(LABELLED_PENDING_Q4) == {
        ("MAM03323", "CHEBI:194180"), ("MAM01511", "CHEBI:140435"), ("MAM02505", "CHEBI:145118"),
        ("MAM02973", "CHEBI:192250"), ("MAM03787", "CHEBI:137735"), ("MAM03796", "CHEBI:230390")}


def inchikey_reader():
    rdkit_inchi = pytest.importorskip("rdkit.Chem.inchi")
    from rdkit import RDLogger

    RDLogger.DisableLog("rdApp.*")
    return rdkit_inchi.InchiToInchiKey


@needs_model
def test_compartment_rows_of_one_metabolite_agree_on_structure_and_name(corrected_metabolites, corrected_sbml_text):
    """Ruling Q5c."""
    key_disagreements, name_disagreements = compartment_disagreements(corrected_metabolites, model_names(corrected_sbml_text), inchikey_reader())
    compare_with_known(key_disagreements, INCHIKEY_DISAGREEMENTS_NOT_YET_ADJUDICATED, "compartment rows of one metsNoComp with different InChIKey first blocks")
    compare_with_known(name_disagreements, NAME_DISAGREEMENTS_NOT_YET_ADJUDICATED, "compartment rows of one metsNoComp with different model names")


@needs_model
def test_the_compartment_guard_catches_every_repaired_case_in_the_pinned_files():
    """Without the corrections the guard finds the two cases of ruling Q5 (MAM03652, MAM20077) and the two it found
    itself on 20 November 2026 (MAM00373, MAM02766), and nothing else."""
    pinned = pd.read_csv(METABOLITES_PATH, sep="\t", dtype=str, keep_default_na=False)
    key_disagreements, name_disagreements = compartment_disagreements(pinned, model_names(SBML_PATH.read_text()), inchikey_reader())
    assert set(key_disagreements) - set(INCHIKEY_DISAGREEMENTS_NOT_YET_ADJUDICATED) == {"MAM03652", "MAM00373"}
    assert set(name_disagreements) - set(NAME_DISAGREEMENTS_NOT_YET_ADJUDICATED) == {"MAM20077", "MAM02766"}


def species_properties(sbml_text: str) -> dict[str, tuple[int | None, str]]:
    """Species id (without M_) -> (charge, formula) from the SBML."""
    properties = {}
    for tag in re.finditer(r"<species [^>]*>", sbml_text):
        attributes = dict(re.findall(r'([\w:]+)="([^"]*)"', tag.group(0)))
        charge = attributes.get("fbc:charge")
        properties[attributes["id"][2:]] = (int(charge) if charge is not None else None, attributes.get("fbc:chemicalFormula", ""))
    return properties


def reaction_participants(sbml_text: str) -> dict[str, dict[str, float]]:
    """Reaction id (without R_) -> {species id: signed stoichiometry, negative for a reactant}."""
    reactions = {}
    for match in re.finditer(r'<reaction [^>]*?\bid="R_(\w+)"(.*?)</reaction>', sbml_text, re.DOTALL):
        reactants, _, products = match.group(2).partition("listOfProducts")
        participants: dict[str, float] = {}
        for part, sign in ((reactants, -1.0), (products, 1.0)):
            for species, amount in re.findall(r'<speciesReference species="M_([^"]+)" stoichiometry="([^"]+)"', part):
                participants[species] = participants.get(species, 0.0) + sign * float(amount)
        reactions[match.group(1)] = participants
    return reactions


def imbalance(participants: dict[str, float], properties: dict) -> tuple[float | None, dict[str, float]]:
    """(charge imbalance, None when a participant has no charge; {element: imbalance} for the elements that do not balance)."""
    charge, elements = 0.0, {}
    for species, amount in participants.items():
        species_charge, formula = properties[species]
        charge = None if charge is None or species_charge is None else charge + amount * species_charge
        for element, count in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
            elements[element] = elements.get(element, 0.0) + amount * (int(count) if count else 1)
    return charge, {element: value for element, value in elements.items() if abs(value) > 1e-9}


def reactions_of(sbml_text: str, species: str) -> set[str]:
    return {reaction for reaction, participants in reaction_participants(sbml_text).items() if species in participants}


def reaction_opening(sbml_text: str, reaction: str) -> str:
    return re.search(rf'<reaction [^>]*\bid="R_{reaction}"[^>]*>', sbml_text).group(0)


def reaction_genes(sbml_text: str, reaction: str) -> set[str]:
    block = re.search(rf'<reaction [^>]*\bid="R_{reaction}".*?</reaction>', sbml_text, re.DOTALL).group(0)
    return set(re.findall(r'fbc:geneProduct="G_([^"]+)"', block))


@needs_model
def test_the_corrected_reactions_are_what_the_rulings_say(corrected_sbml_text, corrected_metabolites):
    """Q5d and 15(R)-HEPE, read from the corrected SBML (cobra reads the same model: tests/test_human_gem_corrections.py)."""
    reactions = reaction_participants(corrected_sbml_text)
    assert reactions["MAR20093"] == {"MAM02040l": -1.0, "MAM03885l": -1.0, "MAM01797l": 1.0, "MAM02674l": 1.0}
    assert reaction_genes(corrected_sbml_text, "MAR20093") == {"ENSG00000138744"}, "NAAA alone, as pinned"
    assert 'fbc:lowerFluxBound="cobra_0_bound"' in reaction_opening(corrected_sbml_text, "MAR20093")
    for reaction, letter in (("MAR02560", "c"), ("MAR02571", "r")):
        assert reactions[reaction] == {f"MAM00375{letter}": -1.0, f"MAM02026{letter}": -2.0, f"MAM00373{letter}": 1.0,
                                       f"MAM02027{letter}": 1.0, f"MAM02040{letter}": 1.0}
        opening = reaction_opening(corrected_sbml_text, reaction)
        assert 'reversible="false"' in opening and 'fbc:lowerFluxBound="cobra_0_bound"' in opening and 'fbc:upperFluxBound="cobra_default_ub"' in opening
        assert 'name="Glutathione: 15(R)-HpEPE oxidoreductase"' in opening
        assert reaction_genes(corrected_sbml_text, reaction) == GLUTATHIONE_PEROXIDASES == reaction_genes(corrected_sbml_text, "MAR00988")
    names = model_names(corrected_sbml_text)
    assert names["MAM03885l"] == "Palmitoylethanolamide" and names["MAM01797l"] == "ethanolamine"
    rows = corrected_metabolites.set_index("mets")
    assert rows.at["MAM03885l", "metChEBIID"] == "CHEBI:71464" and rows.at["MAM01797l", "metChEBIID"] == "CHEBI:16000"
    assert rows.at["MAM03885l", "metHMR2ID"] == "" and rows.at["MAM01797l", "metRetired"] == ""
    # NAAA's other reactions: each wholly in the lysosome, on the added species, every coefficient as pinned
    assert reactions["MAR20094"] == {"MAM02040l": -1.0, "MAM03550l": -1.0, "MAM01797l": 1.0, "MAM02344l": 1.0}
    assert reactions["MAR20095"] == {"MAM02040l": -1.0, "MAM03977l": -1.0, "MAM01797l": 1.0, "MAM02494l": 1.0}
    assert reactions["MAR20096"] == {"MAM02040l": -1.0, "MAM20076l": -1.0, "MAM02674l": 1.0, "MAM02929l": 1.0}
    assert reactions["MAR20097"] == {"MAM02040l": -1.0, "MAM20075l": -1.0, "MAM02344l": 1.0, "MAM02929l": 1.0}
    for reaction in ("MAR20094", "MAR20095"):
        assert reaction_genes(corrected_sbml_text, reaction) == {NAAA}
    for reaction in ("MAR20096", "MAR20097"):
        assert reaction_genes(corrected_sbml_text, reaction) == {ASAH1, NAAA}
    for reaction in ("MAR20093", "MAR20094", "MAR20095", "MAR20096", "MAR20097"):
        assert 'fbc:lowerFluxBound="cobra_0_bound"' in reaction_opening(corrected_sbml_text, reaction)
    assert reaction_genes(corrected_sbml_text, "MAR05339") == reaction_genes(SBML_PATH.read_text(), "MAR05339") - {NAAA}
    assert len(reaction_genes(corrected_sbml_text, "MAR05339")) == 11
    # the palmitoylethanolamide transport, added
    assert reactions["MAR90001"] == {"MAM03885c": -1.0, "MAM03885l": 1.0} and reaction_genes(corrected_sbml_text, "MAR90001") == set()
    opening = reaction_opening(corrected_sbml_text, "MAR90001")
    assert 'reversible="true"' in opening and 'fbc:lowerFluxBound="cobra_default_lb"' in opening and 'fbc:upperFluxBound="cobra_default_ub"' in opening
    assert 'name="transport of palmitoylethanolamide (cytosol to lysosome)"' in opening
    for species, name in (("MAM03550l", "C12:0-Ethanolamide, Didecanoyl Ethanolamide"), ("MAM20076l", "N-hexadecanoylsphing-4-enine")):
        assert names[species] == name
    assert rows.at["MAM20076l", "metChEBIID"] == "CHEBI:72959" and rows.at["MAM03550l", "metsNoComp"] == "MAM03550"
    assert re.search(r'<species [^>]*id="M_MAM20076l"[^>]*compartment="l"', corrected_sbml_text)
    assert "MAM20076c" not in rows.index, "the alternative rename was not chosen"
    pinned = reaction_participants(SBML_PATH.read_text())
    for reaction in LEFT_AS_PINNED_FLAGGED_FOR_FOLLOW_UP:
        assert reactions[reaction] == pinned[reaction], f"{reaction} is to stay as pinned"
        assert reaction not in read_human_gem_corrections().corrected_reactions()


@needs_model
def test_no_reaction_is_less_balanced_in_charge_after_the_corrections(corrected_sbml_text):
    """Every reaction the corrections touch or add balances in elements and charge; no other reaction's charge balance
    changes. The two copies of 15(R)-HEPE hydrolysis left as pinned keep their +2, listed with the owner's reason."""
    pinned_text = SBML_PATH.read_text()
    pinned, corrected = reaction_participants(pinned_text), reaction_participants(corrected_sbml_text)
    pinned_properties, corrected_properties = species_properties(pinned_text), species_properties(corrected_sbml_text)
    added = set(read_human_gem_corrections().reactions_added)
    assert set(corrected) == set(pinned) | added and not set(pinned) & added
    touched = read_human_gem_corrections().corrected_reactions() | added
    for reaction in sorted(touched):
        charge, elements = imbalance(corrected[reaction], corrected_properties)
        assert charge == 0 and elements == {}, f"{reaction} does not balance after its correction: charge {charge}, elements {elements}"
    for reaction in pinned:
        before = imbalance(pinned[reaction], pinned_properties)[0]
        after = imbalance(corrected[reaction], corrected_properties)[0]
        if reaction not in touched:
            assert before == after, f"{reaction}: its charge balance moved from {before} to {after}, and no correction names it"
        elif before is not None and after is not None:
            assert abs(after) <= abs(before), f"{reaction}: less balanced in charge after its correction"
    for reaction in LEFT_AS_PINNED_FLAGGED_FOR_FOLLOW_UP:
        assert imbalance(corrected[reaction], corrected_properties)[0] == 2.0


@needs_model
def test_every_species_is_in_a_reaction_but_the_listed_ones(corrected_sbml_text):
    referenced = set(re.findall(r'<speciesReference species="M_([^"]+)"', corrected_sbml_text))
    pinned_text = SBML_PATH.read_text()
    assert set(species_properties(pinned_text)) <= set(re.findall(r'<speciesReference species="M_([^"]+)"', pinned_text)), "the pinned model has none"
    unreferenced = {species: "in no reaction" for species in species_properties(corrected_sbml_text) if species not in referenced}
    compare_with_known(unreferenced, SPECIES_IN_NO_REACTION_NOT_YET_ADJUDICATED, "a species in no reaction")


@needs_model
def test_both_readers_of_metchebiid_split_the_two_id_cell_of_pristanic_acid():
    """MAM02766 carries "CHEBI:761004;CHEBI:77268" (the owner, 20 November 2026: "Pristanic acid accept"). Every reader of
    the column goes through one of these two, and each id reaches the base."""
    from mechanistic_pathway_learning.evidence.laboratory_abnormality_labels import human_gem_metabolites_by_chebi
    from mechanistic_pathway_learning.graph.chembl_activity_negatives import chebi_of_base

    table = read_human_gem_metabolites(METABOLITES_PATH)
    by_chebi = human_gem_metabolites_by_chebi(table)
    assert "MAM02766" in by_chebi["CHEBI:761004"] and "MAM02766" in by_chebi["CHEBI:77268"]
    assert chebi_of_base(read_human_gem_metabolites(METABOLITES_PATH, usecols=["metsNoComp", "metChEBIID"]))["MAM02766"] == {"CHEBI:761004", "CHEBI:77268"}
