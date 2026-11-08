"""Curated inputs that let a drug the owner admitted reach the evidence table when a label source alone does not (decision 9.117).

A drug becomes a perturbation only by carrying a SIDER 4.1 or OnSIDES v3.1.1 label that the assembler qualifies: an
admitted ATC code and a mechanism target that is a graph node. Decision 9.117 measured on 7 November 2026 that drugs the
owner had already admitted (9.7b, registered rule 14) fall out of that test for mechanical reasons, and the owner asked on
8 November 2026 that they be "included if curation is possible". The three tables read here are the curation, each a
config with its source per row:

  configs/atc_code_supplements.csv           an ATC code a label source holds for the substance under another identifier
                                             (lithium: SIDER files N05AN01 under CID100028486 and none under CID100011125,
                                             the identifier the OnSIDES bridge unifies lithium carbonate with)
  configs/psychiatric_drug_additions_v4_draft.csv
                                             DrugCentral and Guide to PHARMACOLOGY targets of the 9.7 drugs
                                             (docs/psychiatric_drug_additions.md); only its role "mechanism" rows are read,
                                             as that document requires ("Only the mechanism rows are candidates for a seed"),
                                             and only for a drug whose ChEMBL route yields no target; with it
                                             configs/curated_drug_targets.csv, the targets decision 9.121 C3 curated
                                             (a label-stated or single-source target accepted, the owner, 8 November 2026)
  configs/excluded_drug_perturbations.csv    drugs admitted on their ATC code that act outside the brain, which nothing
                                             models (decision 9.121 C4), each with the label sentences that say so
  configs/rejected_sider_indications.csv     SIDER indication rows that misread a label: a condition the drug does not
                                             treat, read from its indication's wording (decision 9.124)
  configs/perturbation_identity_overrides.csv
                                             the perturbation an OnSIDES ingredient reports on, where the bridge's
                                             ChEMBL-parent unification put an enantiomer under another drug and the
                                             enantiomers act differently or are not known to act alike (split; decision
                                             9.121 C5, where the sources show they act the same the merge stands),
                                             left a salt of the same active ion as a drug of its own (merge),
                                             or gave it a ChEMBL parent with no mechanism row where the drug's own
                                             record holds one (parent; decision 9.121)

None of them changes what a label says; each changes which perturbation a label is filed under, whether the
qualification can read the drug at all, or (the exclusion list) whether a drug enters.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Mapping

from mechanistic_pathway_learning.perturbation.map_drug_targets_to_graph_nodes import DrugTarget

if TYPE_CHECKING:
    from mechanistic_pathway_learning.evidence.onsides_identifier_bridge import IngredientBridge

ATC_CODE_SUPPLEMENTS_PATH = Path("configs/atc_code_supplements.csv")
CURATED_DRUG_TARGETS_PATH = Path("configs/psychiatric_drug_additions_v4_draft.csv")
CURATED_DRUG_TARGETS_PATHS = (CURATED_DRUG_TARGETS_PATH, Path("configs/curated_drug_targets.csv"))
EXCLUDED_DRUG_PERTURBATIONS_PATH = Path("configs/excluded_drug_perturbations.csv")
REJECTED_SIDER_INDICATIONS_PATH = Path("configs/rejected_sider_indications.csv")
PERTURBATION_IDENTITY_OVERRIDES_PATH = Path("configs/perturbation_identity_overrides.csv")
CURATED_TARGET_PREFIX = "CURATED:"  # target id of a curated row that names no ChEMBL target
IDENTITY_OVERRIDE_KINDS = ("split", "merge", "parent")
SEED_ROLE = "mechanism"


def read_atc_code_supplements(path: Path) -> dict[str, list[str]]:
    """perturbation_id -> the ATC codes the supplement table adds to it, in file order."""
    supplements: dict[str, list[str]] = {}
    with open(path, encoding="utf-8", newline="") as supplement_file:
        for row in csv.DictReader(supplement_file):
            perturbation_id, atc_code = row["perturbation_id"].strip(), row["atc_code"].strip()
            if not perturbation_id or not atc_code:
                raise ValueError(f"{path}: a row without perturbation_id or atc_code: {row}")
            if not (row.get("source") or "").strip():
                raise ValueError(f"{path}: the supplement {perturbation_id} {atc_code} names no source")
            codes = supplements.setdefault(perturbation_id, [])
            if atc_code in codes:
                raise ValueError(f"{path} lists {perturbation_id} {atc_code} twice")
            codes.append(atc_code)
    return supplements


def supplemented_atc_codes(perturbation_id: str, atc_codes: list[str], supplements: Mapping[str, list[str]]) -> list[str]:
    """The drug's own codes followed by the supplement's codes it does not already carry."""
    return list(atc_codes) + [code for code in supplements.get(perturbation_id, []) if code not in atc_codes]


def read_curated_mechanism_targets(path: Path) -> dict[str, list[DrugTarget]]:
    """perturbation_id -> DrugTargets from the role "mechanism" rows of a drug-to-target table.

    Rows naming the same ChEMBL target are one target, so a family row stays one target split over its genes (lithium's
    GSK3A and GSK3B under CHEMBL2095188, 0.5 each), the way the ChEMBL route reads it; a row naming no ChEMBL target is
    its own single-gene target under CURATED:<gene>. Each gene keeps the table's own sign; the target takes its first row's
    action type, and rows of one target with opposite signs are an error."""
    rows_by_target: dict[tuple[str, str], list[dict]] = {}
    with open(path, encoding="utf-8", newline="") as table_file:
        for row in csv.DictReader(table_file):
            if row["role"].strip() != SEED_ROLE:
                continue
            if row.get("target_is_graph_node", "True").strip() != "True":
                continue
            gene = row["gene"].strip()
            target_id = row["target_chembl_id"].strip() or f"{CURATED_TARGET_PREFIX}{gene}"
            rows_by_target.setdefault((row["perturbation_id"].strip(), target_id), []).append(row)
    targets_by_perturbation: dict[str, list[DrugTarget]] = {}
    for (perturbation_id, target_id), rows in rows_by_target.items():
        signs = sorted({float(row["sign"]) for row in rows})
        if signs[0] * signs[-1] < 0:  # subunits of one target may differ in action (agonist +1, partial agonist +0.5), never in direction
            raise ValueError(f"{path}: {perturbation_id} {target_id} carries the signs {signs}")
        target = DrugTarget(target_id, rows[0]["action_type"].strip().upper(), gene_symbols=[row["gene"].strip() for row in rows],
                            target_type="SINGLE PROTEIN" if len(rows) == 1 else "PROTEIN FAMILY",
                            gene_signs={row["gene"].strip(): float(row["sign"]) for row in rows})
        targets_by_perturbation.setdefault(perturbation_id, []).append(target)
    return {perturbation_id: sorted(targets, key=lambda target: target.target_chembl_id) for perturbation_id, targets in targets_by_perturbation.items()}


@dataclass(frozen=True)
class IdentityOverride:
    ingredient_id: str
    ingredient_name: str
    kind: str  # one of IDENTITY_OVERRIDE_KINDS
    perturbation_id: str
    reason: str
    chembl_parent: str = ""  # the ChEMBL parent the ingredient takes instead of the bridge's; required for kind "parent"


def read_perturbation_identity_overrides(path: Path) -> dict[str, IdentityOverride]:
    """OnSIDES ingredient id -> the perturbation its labels are filed under instead of the bridge's choice."""
    overrides: dict[str, IdentityOverride] = {}
    with open(path, encoding="utf-8", newline="") as override_file:
        for row in csv.DictReader(override_file):
            override = IdentityOverride(row["ingredient_id"].strip(), row["ingredient_name"].strip(), row["kind"].strip(), row["perturbation_id"].strip(),
                                        row["reason"].strip(), (row.get("chembl_parent") or "").strip())
            if override.kind not in IDENTITY_OVERRIDE_KINDS:
                raise ValueError(f"{path}: kind {override.kind!r} for {override.ingredient_name}; choose from {IDENTITY_OVERRIDE_KINDS}")
            if override.kind == "parent" and not override.chembl_parent:
                raise ValueError(f"{path}: the parent override of {override.ingredient_name} names no chembl_parent")
            if override.kind == "split" and override.chembl_parent:
                raise ValueError(f"{path}: a split keeps the ingredient's own parent; {override.ingredient_name} names one")
            if not override.reason:
                raise ValueError(f"{path}: the override of {override.ingredient_name} states no reason")
            if override.ingredient_id in overrides:
                raise ValueError(f"{path} lists ingredient {override.ingredient_id} twice")
            overrides[override.ingredient_id] = override
    return overrides


def apply_perturbation_identity_overrides(bridges: Mapping[str, "IngredientBridge"], overrides: Mapping[str, IdentityOverride],
                                          sider_drug_names: Mapping[str, str] | None = None) -> list[str]:
    """Refile each overridden ingredient under its override's perturbation, in place; returns the ingredient ids changed.

    A split gives the ingredient the perturbation_id of an OnSIDES-only drug (fallback_perturbation_id) and drops the
    SIDER partner, so its labels and its own ChEMBL parent's targets make a perturbation of their own; the SIDER drug
    keeps its 2015 labels, which SIDER's stereo-flattened identifier pools across the forms; the former SIDER CID is kept
    as split_from_sider_pubchem_cid, so the time split still finds the ingredient's pairs on those 2015 labels. A merge files the
    ingredient under an existing SIDER perturbation, taking that drug's name and identifier from a bridge already
    unified with it, or, where no ingredient is unified with that SIDER drug, its name from sider_drug_names (STITCH
    flat id -> name, drug_names.tsv as corrected) and no SIDER ATC codes beyond the ones the supplement table adds. A
    parent override keeps the perturbation and replaces the ChEMBL parent the bridge chose (a stereo-specific record or
    none at all) by the drug's own record, which holds the mechanism; a merge may name a parent too. The parent the
    bridge chose is kept as chembl_parent_overridden_from. An override naming an ingredient the bridge lacks is an error,
    so a stale row cannot pass silently."""
    from mechanistic_pathway_learning.evidence.onsides_identifier_bridge import (
        UNIFICATION_METHOD_OVERRIDE_MERGE, UNIFICATION_METHOD_OVERRIDE_SPLIT, fallback_perturbation_id)
    from mechanistic_pathway_learning.perturbation.gtopdb_drug_targets import pubchem_cid_from_perturbation_id

    missing = sorted(ingredient_id for ingredient_id in overrides if ingredient_id not in bridges)
    if missing:
        raise ValueError(f"identity overrides name ingredients the bridge does not hold: {missing}")
    changed: list[str] = []
    for ingredient_id, override in overrides.items():
        bridge = bridges[ingredient_id]
        if override.kind == "split":
            if override.perturbation_id != fallback_perturbation_id(ingredient_id):
                raise ValueError(f"the split of {override.ingredient_name} must take {fallback_perturbation_id(ingredient_id)}, not {override.perturbation_id}")
            bridge.perturbation_id, bridge.unified_with_sider, bridge.unification_method = override.perturbation_id, False, UNIFICATION_METHOD_OVERRIDE_SPLIT
            bridge.split_from_sider_pubchem_cid, bridge.sider_pubchem_cid, bridge.sider_drug_name = bridge.sider_pubchem_cid, None, None
        elif override.kind == "parent":
            if override.perturbation_id != bridge.perturbation_id:
                raise ValueError(f"the parent override of {override.ingredient_name} names {override.perturbation_id}, but the bridge files it under {bridge.perturbation_id}")
        else:
            partners = [other for other in bridges.values() if other.perturbation_id == override.perturbation_id and other.unified_with_sider and other.ingredient_id not in overrides]
            if partners:
                sider_drug_name, atc_codes_sider = partners[0].sider_drug_name, list(partners[0].atc_codes_sider)
            elif sider_drug_names and override.perturbation_id in sider_drug_names:
                sider_drug_name, atc_codes_sider = sider_drug_names[override.perturbation_id], []
            else:
                raise ValueError(f"the merge of {override.ingredient_name} names {override.perturbation_id}, which no unified ingredient holds and no SIDER name is given for")
            bridge.perturbation_id, bridge.unified_with_sider, bridge.unification_method = override.perturbation_id, True, UNIFICATION_METHOD_OVERRIDE_MERGE
            bridge.sider_pubchem_cid, bridge.sider_drug_name = pubchem_cid_from_perturbation_id(override.perturbation_id), sider_drug_name
            bridge.atc_codes_sider = atc_codes_sider
        if override.chembl_parent:
            bridge.chembl_parent_overridden_from, bridge.chembl_parent = bridge.chembl_parent, override.chembl_parent
        changed.append(ingredient_id)
    return changed


def apply_atc_code_supplements(bridges: Mapping[str, "IngredientBridge"], supplements: Mapping[str, list[str]]) -> list[str]:
    """Set atc_codes_curated on every ingredient whose perturbation the supplement table names (after any identity
    override, so a merged salt takes the codes of the drug it joins); returns the ingredient ids changed."""
    changed: list[str] = []
    for ingredient_id, bridge in bridges.items():
        codes = supplements.get(bridge.perturbation_id, [])
        if codes:
            bridge.atc_codes_curated = list(codes)
            bridge.nervous_system_atc = any(code.startswith("N") for code in bridge.atc_codes)
            changed.append(ingredient_id)
    return changed


def read_curated_mechanism_targets_from(paths) -> dict[str, list[DrugTarget]]:
    """read_curated_mechanism_targets over several tables; a perturbation two tables both curate is an error, so one
    drug's targets are never assembled from two curations."""
    merged: dict[str, list[DrugTarget]] = {}
    for path in paths:
        for perturbation_id, targets in read_curated_mechanism_targets(Path(path)).items():
            if perturbation_id in merged:
                raise ValueError(f"{perturbation_id} is curated in more than one of {[str(path) for path in paths]}")
            merged[perturbation_id] = targets
    return merged


def read_excluded_drug_perturbations(path: Path) -> dict[str, str]:
    """perturbation_id -> the reason it is excluded; every row names its reason and its source."""
    excluded: dict[str, str] = {}
    with open(path, encoding="utf-8", newline="") as excluded_file:
        for row in csv.DictReader(excluded_file):
            perturbation_id = row["perturbation_id"].strip()
            if not row["reason"].strip() or not row["source"].strip():
                raise ValueError(f"{path}: the exclusion of {perturbation_id} names no reason or no source")
            if perturbation_id in excluded:
                raise ValueError(f"{path} lists {perturbation_id} twice")
            excluded[perturbation_id] = row["reason"].strip()
    return excluded


def read_rejected_sider_indications(path: Path) -> set[tuple[str, str]]:
    """{(STITCH flat id, MedDRA preferred term lowercase)} of SIDER indication rows to drop; every row names its reason
    and its source. Only "relieves" events are matched: the same term as an adverse event of the drug is untouched."""
    rejected: set[tuple[str, str]] = set()
    with open(path, encoding="utf-8", newline="") as rejected_file:
        for row in csv.DictReader(rejected_file):
            key = (row["stitch_flat_id"].strip(), row["meddra_preferred_term"].strip().lower())
            if not row["reason"].strip() or not row["source"].strip():
                raise ValueError(f"{path}: the rejection of {key} names no reason or no source")
            if key in rejected:
                raise ValueError(f"{path} lists {key} twice")
            rejected.add(key)
    return rejected
