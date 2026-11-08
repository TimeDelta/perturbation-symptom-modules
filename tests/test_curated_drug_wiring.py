"""Tests for the curated drug wiring of decision 9.117 (evidence/curated_drug_wiring.py): the ATC supplements, the curated
mechanism targets read for a drug ChEMBL leaves without one, the identity overrides of the OnSIDES bridge, and the
committed configs that carry them."""
import csv
import json
from pathlib import Path

import pytest

from mechanistic_pathway_learning.evidence.curated_drug_wiring import (
    ATC_CODE_SUPPLEMENTS_PATH,
    CURATED_DRUG_TARGETS_PATH,
    PERTURBATION_IDENTITY_OVERRIDES_PATH,
    apply_atc_code_supplements,
    apply_perturbation_identity_overrides,
    read_atc_code_supplements,
    read_curated_mechanism_targets,
    read_perturbation_identity_overrides,
    supplemented_atc_codes,
)
from mechanistic_pathway_learning.evidence.load_drug_label_events import has_admitted_atc_code, read_admitted_atc_prefixes
from mechanistic_pathway_learning.evidence.load_onsides_label_events import qualify_ingredient
from mechanistic_pathway_learning.evidence.onsides_identifier_bridge import (
    UNIFICATION_METHOD_OVERRIDE_MERGE,
    UNIFICATION_METHOD_OVERRIDE_SPLIT,
    IngredientBridge,
    load_ingredient_identifier_bridge,
)
from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import GraphNodeLookup

ADMITTED_ATC_PREFIXES_PATH = Path("configs/admitted_atc_prefixes.csv")
BRIDGE_PATH = Path("data/raw/onsides/v3.1.1/ingredient_identifier_bridge.json")
TARGET_COLUMNS = ["perturbation_id", "drug", "gene", "role", "action_type", "sign", "magnitude", "target_chembl_id", "target_is_graph_node"]


def write_targets(path: Path, rows: list[dict]) -> Path:
    with open(path, "w", encoding="utf-8", newline="") as table_file:
        writer = csv.DictWriter(table_file, fieldnames=TARGET_COLUMNS)
        writer.writeheader()
        writer.writerows({column: row.get(column, "") for column in TARGET_COLUMNS} for row in rows)
    return path


def curated_row(perturbation_id: str, gene: str, role: str = "mechanism", action: str = "ANTAGONIST", sign: str = "-1.0", target: str = "") -> dict:
    return {"perturbation_id": perturbation_id, "drug": "d", "gene": gene, "role": role, "action_type": action, "sign": sign, "magnitude": "1.0",
            "target_chembl_id": target, "target_is_graph_node": "True"}


def test_an_atc_supplement_is_added_once_and_needs_a_source(tmp_path: Path) -> None:
    path = tmp_path / "supplements.csv"
    path.write_text("perturbation_id,drug,atc_code,source,note\nCID1,lithium,N05AN01,SIDER,n\n")
    supplements = read_atc_code_supplements(path)
    assert supplemented_atc_codes("CID1", [], supplements) == ["N05AN01"]
    assert supplemented_atc_codes("CID1", ["N05AN01"], supplements) == ["N05AN01"]
    assert supplemented_atc_codes("CID2", ["A03FA01"], supplements) == ["A03FA01"]
    path.write_text("perturbation_id,drug,atc_code,source,note\nCID1,lithium,N05AN01,,n\n")
    with pytest.raises(ValueError, match="names no source"):
        read_atc_code_supplements(path)


def test_only_mechanism_rows_are_read_and_a_family_row_stays_one_target(tmp_path: Path) -> None:
    path = write_targets(tmp_path / "targets.csv", [
        curated_row("CID3", "HTR2A"), curated_row("CID3", "HTR7", role="other"),
        curated_row("CID4", "GSK3A", action="INHIBITOR", target="CHEMBL2095188"), curated_row("CID4", "GSK3B", action="INHIBITOR", target="CHEMBL2095188"),
        curated_row("CID5", "SLC6A3", role="other"),
    ])
    targets = read_curated_mechanism_targets(path)
    assert sorted(targets) == ["CID3", "CID4"]  # a drug with only role "other" rows has no curated seed
    assert [(target.target_chembl_id, target.gene_symbols) for target in targets["CID3"]] == [("CURATED:HTR2A", ["HTR2A"])]
    family, = targets["CID4"]
    assert family.target_chembl_id == "CHEMBL2095188" and family.gene_symbols == ["GSK3A", "GSK3B"] and family.sign == -1.0
    lookup = GraphNodeLookup({"GSK3A": "GENE:GSK3A", "GSK3B": "GENE:GSK3B"}, {}, {})
    assert lookup.perturbation_nodes([family]) == [["GENE:GSK3A", -1.0, 0.5], ["GENE:GSK3B", -1.0, 0.5]]


def test_subunits_may_differ_in_action_but_not_in_direction(tmp_path: Path) -> None:
    same_direction = write_targets(tmp_path / "same.csv", [curated_row("CID6", "A", action="AGONIST", sign="1.0", target="T"),
                                                           curated_row("CID6", "B", action="PARTIAL AGONIST", sign="0.5", target="T")])
    target, = read_curated_mechanism_targets(same_direction)["CID6"]
    assert target.sign_of("A") == 1.0 and target.sign_of("B") == 0.5
    opposite = write_targets(tmp_path / "opposite.csv", [curated_row("CID6", "A", sign="1.0", target="T"), curated_row("CID6", "B", sign="-1.0", target="T")])
    with pytest.raises(ValueError, match="signs"):
        read_curated_mechanism_targets(opposite)


def bridge(ingredient_id: str, name: str, perturbation_id: str, parent: str, sider_cid: int | None, atc: list[str]) -> IngredientBridge:
    return IngredientBridge(ingredient_id, name, "RXCUI", "unii_unichem", chembl_parent=parent, perturbation_id=perturbation_id,
                            unified_with_sider=sider_cid is not None, unification_method="chembl_parent" if sider_cid else "none",
                            sider_pubchem_cid=sider_cid, sider_drug_name=name if sider_cid else None, atc_codes_sider=atc)


def test_the_curated_targets_are_a_fallback_and_never_replace_chembl(tmp_path: Path) -> None:
    mechanisms = {"CHEMBL1": [{"target_chembl_id": "CHEMBL217", "action_type": "ANTAGONIST"}]}
    targets = {"CHEMBL217": {"target_type": "SINGLE PROTEIN", "pref_name": "D2", "target_components": [{"accession": "P14416", "component_synonyms": [{"component_synonym": "DRD2", "syn_type": "GENE_SYMBOL"}]}]}}
    curated = read_curated_mechanism_targets(write_targets(tmp_path / "targets.csv", [curated_row("CID7", "DRD1")]))
    without_chembl = qualify_ingredient(bridge("1", "zuclopenthixol", "CID7", "CHEMBL9", 7, ["N05AF05"]), mechanisms, targets, max_drug_targets=None, curated_targets_by_perturbation=curated)
    assert without_chembl.qualifies and without_chembl.target_source == "curated" and without_chembl.drug_targets[0].gene_symbols == ["DRD1"]
    parentless = qualify_ingredient(bridge("3", "flupenthixol", "CID7", None, None, ["N05AF01"]), mechanisms, targets, max_drug_targets=None, curated_targets_by_perturbation=curated)
    assert parentless.qualifies and parentless.target_source == "curated"  # a parent the bridge missed does not block curated targets
    assert qualify_ingredient(bridge("4", "x", "CID8", None, None, ["N05AF01"]), mechanisms, targets, max_drug_targets=None,
                              curated_targets_by_perturbation=curated).reason == "no_chembl_parent"
    with_chembl = qualify_ingredient(bridge("2", "drug", "CID7", "CHEMBL1", 7, ["N05AF05"]), mechanisms, targets, max_drug_targets=None, curated_targets_by_perturbation=curated)
    assert with_chembl.target_source == "ChEMBL" and [target.target_chembl_id for target in with_chembl.drug_targets] == ["CHEMBL217"]


def overrides_file(tmp_path: Path, rows: list[str]) -> Path:
    path = tmp_path / "overrides.csv"
    path.write_text("ingredient_id,ingredient_name,kind,perturbation_id,reason\n" + "".join(row + "\n" for row in rows))
    return path


def test_a_split_files_the_ingredient_apart_and_keeps_its_2015_identifier_for_the_time_split(tmp_path: Path) -> None:
    bridges = {"321988": bridge("321988", "escitalopram", "CID100002771", "CHEMBL1508", 2771, ["N06AB10"]),
               "2556": bridge("2556", "citalopram", "CID100002771", "CHEMBL549", 2771, ["N06AB04"])}
    overrides = read_perturbation_identity_overrides(overrides_file(tmp_path, ["321988,escitalopram,split,RXCUI:321988,an enantiomer"]))
    assert apply_perturbation_identity_overrides(bridges, overrides) == ["321988"]
    split = bridges["321988"]
    assert (split.perturbation_id, split.unified_with_sider, split.unification_method) == ("RXCUI:321988", False, UNIFICATION_METHOD_OVERRIDE_SPLIT)
    assert split.sider_pubchem_cid is None and split.split_from_sider_pubchem_cid == 2771 and split.chembl_parent == "CHEMBL1508"
    assert bridges["2556"].perturbation_id == "CID100002771"
    wrong_id = read_perturbation_identity_overrides(overrides_file(tmp_path, ["2556,citalopram,split,RXCUI:9,wrong"]))
    with pytest.raises(ValueError, match="must take RXCUI:2556"):
        apply_perturbation_identity_overrides(bridges, wrong_id)


def test_a_merge_files_a_salt_under_its_ion_and_takes_its_codes(tmp_path: Path) -> None:
    bridges = {"42351": bridge("42351", "lithium carbonate", "CID100011125", "CHEMBL1200826", 11125, []),
               "52105": bridge("52105", "lithium citrate", "RXCUI:52105", "CHEMBL1201170", None, [])}
    overrides = read_perturbation_identity_overrides(overrides_file(tmp_path, ["52105,lithium citrate,merge,CID100011125,the same ion"]))
    apply_perturbation_identity_overrides(bridges, overrides)
    merged = bridges["52105"]
    assert (merged.perturbation_id, merged.unified_with_sider, merged.unification_method, merged.sider_pubchem_cid) == ("CID100011125", True, UNIFICATION_METHOD_OVERRIDE_MERGE, 11125)
    supplements_path = tmp_path / "supplements.csv"
    supplements_path.write_text("perturbation_id,drug,atc_code,source,note\nCID100011125,lithium,N05AN01,SIDER,n\n")
    assert sorted(apply_atc_code_supplements(bridges, read_atc_code_supplements(supplements_path))) == ["42351", "52105"]
    assert all(entry.atc_codes == ["N05AN01"] and entry.nervous_system_atc for entry in bridges.values())


def parent_overrides_file(tmp_path: Path, rows: list[str]) -> Path:
    path = tmp_path / "overrides.csv"
    path.write_text("ingredient_id,ingredient_name,kind,perturbation_id,chembl_parent,reason\n" + "".join(row + "\n" for row in rows))
    return path


def test_a_parent_override_keeps_the_perturbation_and_replaces_the_parent(tmp_path: Path) -> None:
    """Decision 9.121 A2: methylphenidate's bridge parent is a stereo record without a mechanism row."""
    bridges = {"6901": bridge("6901", "methylphenidate", "CID100004158", "CHEMBL290634", 4158, ["N06BA04"])}
    overrides = read_perturbation_identity_overrides(parent_overrides_file(tmp_path, ["6901,methylphenidate,parent,CID100004158,CHEMBL796,its own record"]))
    apply_perturbation_identity_overrides(bridges, overrides)
    overridden = bridges["6901"]
    assert (overridden.perturbation_id, overridden.chembl_parent, overridden.chembl_parent_overridden_from) == ("CID100004158", "CHEMBL796", "CHEMBL290634")
    assert overridden.unification_method == "chembl_parent" and overridden.sider_pubchem_cid == 4158
    moved = read_perturbation_identity_overrides(parent_overrides_file(tmp_path, ["6901,methylphenidate,parent,CID1,CHEMBL796,r"]))
    with pytest.raises(ValueError, match="files it under"):
        apply_perturbation_identity_overrides({"6901": bridge("6901", "methylphenidate", "CID100004158", "CHEMBL290634", 4158, [])}, moved)
    with pytest.raises(ValueError, match="names no chembl_parent"):
        read_perturbation_identity_overrides(parent_overrides_file(tmp_path, ["6901,methylphenidate,parent,CID100004158,,r"]))
    with pytest.raises(ValueError, match="keeps the ingredient's own parent"):
        read_perturbation_identity_overrides(parent_overrides_file(tmp_path, ["6901,methylphenidate,split,RXCUI:6901,CHEMBL796,r"]))


def test_a_merge_into_a_sider_drug_no_ingredient_holds_takes_its_name_from_sider(tmp_path: Path) -> None:
    """Decision 9.121 A4: methotrimeprazine is levomepromazine, which no OnSIDES ingredient is unified with."""
    bridges = {"6852": bridge("6852", "methotrimeprazine", "RXCUI:6852", None, None, [])}
    overrides = read_perturbation_identity_overrides(parent_overrides_file(tmp_path, ["6852,methotrimeprazine,merge,CID100003916,CHEMBL1764,one drug"]))
    with pytest.raises(ValueError, match="no SIDER name is given"):
        apply_perturbation_identity_overrides(dict(bridges), overrides)
    apply_perturbation_identity_overrides(bridges, overrides, {"CID100003916": "levomepromazine"})
    merged = bridges["6852"]
    assert (merged.perturbation_id, merged.sider_drug_name, merged.sider_pubchem_cid, merged.chembl_parent) == ("CID100003916", "levomepromazine", 3916, "CHEMBL1764")


def test_an_override_naming_an_absent_ingredient_or_without_a_reason_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="states no reason"):
        read_perturbation_identity_overrides(overrides_file(tmp_path, ["1,a,split,RXCUI:1,"]))
    with pytest.raises(ValueError, match="kind"):
        read_perturbation_identity_overrides(overrides_file(tmp_path, ["1,a,join,RXCUI:1,r"]))
    with pytest.raises(ValueError, match="does not hold"):
        apply_perturbation_identity_overrides({}, read_perturbation_identity_overrides(overrides_file(tmp_path, ["1,a,split,RXCUI:1,r"])))


def test_the_committed_admitted_list_holds_group_n_and_the_rule_14_admissions_only() -> None:
    """Decision 3.2 admitted codeine, cyclobenzaprine, hydrocodone and metoclopramide under rule 14 as item 31 tightened
    it, and 9.7b dextromethorphan, whose part (a) was read at a second medicines agency on 8 November 2026; item 31
    dropped metoprolol and propranolol, so their codes must not be in the list (decision 9.117)."""
    prefixes = read_admitted_atc_prefixes(ADMITTED_ATC_PREFIXES_PATH)
    assert prefixes[0] == "N"
    assert set(prefixes) == {"N", "A03FA01", "R05DA04", "R05DA03", "M03BX08", "R05DA09"}
    assert not has_admitted_atc_code(["C07AB02"], prefixes) and not has_admitted_atc_code(["C07AA05"], prefixes)
    with open(ADMITTED_ATC_PREFIXES_PATH, encoding="utf-8", newline="") as prefix_file:
        assert all(row["source"].strip() and row["reason"].strip() for row in csv.DictReader(prefix_file))


def test_the_committed_tables_parse_and_the_overrides_name_ingredients_the_bridge_holds() -> None:
    supplements = read_atc_code_supplements(ATC_CODE_SUPPLEMENTS_PATH)
    assert supplements["CID100011125"] == ["N05AN01"] and supplements["CID100213046"] == ["N05AE05"] and supplements["OMOP:2721429"] == ["N04BD03"]
    assert len(supplements) == 15 and all(code.startswith("N") for codes in supplements.values() for code in codes)  # lithium, the 13 of 9.121 A1, safinamide
    curated = read_curated_mechanism_targets(CURATED_DRUG_TARGETS_PATH)
    assert {target.gene_symbols[0] for target in curated["CID100012453"]} == {"DRD1", "DRD2"}  # zuclopenthixol
    assert {target.gene_symbols[0] for target in curated["CID100004184"]} == {"HTR2A", "HTR2B", "HTR2C"}  # mianserin, role "mechanism" rows only
    assert "RXCUI:2121751" not in curated  # solriamfetol: no source marks a mechanism row
    assert {target.gene_symbols[0] for target in curated["RXCUI:4495"]} == {"DRD1", "DRD2"}  # flupentixol, OnSIDES's "flupenthixol" (9.121 A5)
    overrides = read_perturbation_identity_overrides(PERTURBATION_IDENTITY_OVERRIDES_PATH)
    if not BRIDGE_PATH.exists():
        pytest.skip(f"{BRIDGE_PATH} is not on this disk")
    bridges = load_ingredient_identifier_bridge(BRIDGE_PATH)
    for ingredient_id, override in overrides.items():
        assert bridges[ingredient_id].ingredient_name == override.ingredient_name
    from mechanistic_pathway_learning.evidence.load_drug_label_events import read_two_column_tsv
    from mechanistic_pathway_learning.evidence.sider_drug_names import corrected_drug_names
    names_path = Path("data/raw/sider_4.1/drug_names.tsv")
    sider_names = corrected_drug_names({key: values[0] for key, values in read_two_column_tsv(names_path).items()}) if names_path.exists() else {"CID100003916": "levomepromazine"}
    apply_perturbation_identity_overrides(bridges, overrides, sider_names)
    assert bridges["6852"].sider_drug_name == "levomepromazine" and bridges["6901"].chembl_parent == "CHEMBL796"
    assert json.dumps(sorted(bridge.perturbation_id for bridge in bridges.values() if bridge.ingredient_name == "escitalopram")) == '["RXCUI:321988"]'
