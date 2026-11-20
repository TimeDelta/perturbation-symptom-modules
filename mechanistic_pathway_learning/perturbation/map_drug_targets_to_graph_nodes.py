"""Drug perturbations from ChEMBL mechanisms (design section 4.2, E2).

A drug becomes a perturbation of the graph through its mechanism targets: an
inhibitor, antagonist or blocker is a negative sign on the target nodes, an
agonist or activator a positive sign. Targets that are enzymes or transporters
reach the metabolic layer directly; receptor targets reach it only through the
signaling and transcription layers.

Every ChEMBL target type is placed where the graph has a node for it
(GraphNodeLookup.nodes_of_target, docs/drug_targets_any_type.md):
- protein targets (single proteins, complexes, families): the gene nodes of their gene symbols;
- nucleic-acid targets that name a gene (the mRNA or pre-mRNA of TTR, SMN2, APOB): that gene's node, by Ensembl id;
- metals, small molecules, lipids and oligosaccharides: the Human-GEM metabolites of
  configs/non_protein_drug_targets.csv, every compartment of each;
- a drug with no mechanism target under any of its ChEMBL forms whose active compound is itself a graph metabolite
  (tryptophan, and levodopa once configs/drug_target_exclusions.csv removes its one row, DRD3 agonism, which L-dopa
  does not have; configs/drugs_acting_as_graph_compounds.csv): that metabolite, raised (EXOGENOUS SUPPLY). Lithium is
  not listed: ChEMBL records IMPA1 and GSK3 inhibition on lithium carbonate and lithium citrate, so it falls under the
  single-target rule like any drug with protein targets (check_graph_compounds_have_no_mechanism enforces this). GABA is
  not listed: the only label rows under its PubChem id (SIDER CID 119) are an immune globulin's.
Targets in another organism stay out (human_only), and DNA, RNA, antibodies and unnamed classes have no node.
A complex target's magnitude 1 is spread over its subunits' nodes; the evidence build first narrows a complex to the
subunits the Guide to PHARMACOLOGY names for the drug, each with its own sign (DrugTarget.gene_signs;
perturbation/gtopdb_drug_targets.ComplexTargetNarrowing, decision 8.11).

Inputs are the caches written by experiments/fetch_chembl_drug_targets.py. Its PubChem-to-ChEMBL map
(pubchem_to_chembl_with_parents.json) is read through read_pubchem_to_chembl, which adds the parents of
configs/chembl_parent_corrections.csv. For some PubChem ids of the ChEMBL_37 cache (184 when the table was made,
20 November 2026) the map holds no id, or only forms other than the parent that carries the drug's mechanisms and
activity records: a registration UniChem returns whose molecule_hierarchy parent is itself, or a salt the fetch never
resolved to its parent because the salt carries mechanisms of its own. A refetch writes the same map, so the
correction is made where the map is read. Both readers of the map, the mechanism route here (load_chembl_caches)
and the activity route of graph/chembl_activity_negatives.py (read_pubchem_mapping), go through it.

One drug, one target, one action. When the mechanism rows of a drug's ChEMBL ids give one target more than one action
type (docetaxel's tubulin INHIBITOR and STABILISER), the owner's ruling of 20 November 2026 is to "always flag for
curation instead" of choosing one. mechanism_targets takes the action a row of configs/chembl_action_conflict_resolutions.csv
names for the pair; without such a row it withholds the target, so the drug gets no edge to it, and reports the
conflict (ActionConflict), which the evidence build and the OnSIDES build write as chembl_action_conflicts.csv. A
withheld target still counts against the single-target rule and still keeps a drug from the fallbacks meant for a drug
ChEMBL gives no target. Every run before 20 November 2026 kept the action of the last row read.

A ruled removal. configs/drug_target_exclusions.csv lists mechanism targets, or members of a family or complex
target, that a ruling of the owner's removes, each row with its ruling and sources (DrugTargetExclusion). A row names
a drug and a target (the drug's edges to that whole target go), or a target and one member gene, for one drug or, with
drug_chembl_id blank, for every drug (that member leaves the target, and the target's magnitude is spread over the
members left, as over the members that are graph nodes). mechanism_targets applies the table before anything else, so
an excluded target is neither kept, nor reported as an action conflict, nor counted against the single-target rule,
and check_graph_compounds_have_no_mechanism reads a ChEMBL form whose every mechanism row is excluded as carrying none.
Every run before 20 November 2026 kept every target ChEMBL gives.

A ruled addition, the twin of a ruled removal. configs/drug_target_additions.csv lists targets a ruling of the owner's
adds to a drug whose ChEMBL mechanism rows do not name them, each row with its ruling and sources and, where sourced,
the affinity and the quantity type it was measured as (DrugTargetAddition). The first rows are cocaine's dopamine,
serotonin and noradrenaline transporters (item 37 rulings draft, section 17, P4, and section 19): ChEMBL curates no
transporter mechanism for cocaine, only its sodium-channel family row, so the fallback of
configs/curated_drug_targets.csv, which is read only for a drug whose ChEMBL route gives no target, never reaches it.
mechanism_targets appends the additions after the targets the ChEMBL rows give, so both label routes, the SIDER route
and the OnSIDES bridge, carry them. An added target is a mechanism target like any other: it counts against the
single-target rule, keeps a drug from the fallbacks meant for a drug ChEMBL gives no target, counts as a mechanism for
check_graph_compounds_have_no_mechanism, and takes magnitude 1 spread over its genes. The affinity is recorded for the
occupancy weighting of amendment item 37 (37h, 37i), which is not built and which nothing reads yet. A row that adds a
target the drug's ChEMBL rows already name, or one its exclusions remove, is refused: a curated action for a target
ChEMBL names belongs in configs/chembl_action_conflict_resolutions.csv. Every build until the table was added (20
November 2026) carried only the targets ChEMBL's mechanism rows give; the latest, of 12 November 2026, holds cocaine's
ten sodium-channel edges and no transporter.
"""
from __future__ import annotations

import csv
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import pandas as pd

PUBCHEM_TO_CHEMBL_FILENAME = "pubchem_to_chembl_with_parents.json"
CHEMBL_RELEASE_FILENAME = "chembl_release.json"
# PubChem CID -> the ChEMBL parent the cache misses, verified against the pinned release it names (chembl_release)
CHEMBL_PARENT_CORRECTIONS_PATH = Path(__file__).resolve().parents[2] / "configs" / "chembl_parent_corrections.csv"
# (drug ChEMBL id, target ChEMBL id) -> the action curated for a pair whose ChEMBL rows disagree (module docstring)
CHEMBL_ACTION_CONFLICT_RESOLUTIONS_PATH = Path(__file__).resolve().parents[2] / "configs" / "chembl_action_conflict_resolutions.csv"
ACTION_CONFLICT_RESOLUTION_COLUMNS = ("drug_chembl_id", "target_chembl_id", "chosen_action", "sources", "note")
ACTION_CONFLICTS_REPORT_FILENAME = "chembl_action_conflicts.csv"
# mechanism targets, or members of one, that a ruling removes (module docstring, "A ruled removal")
DRUG_TARGET_EXCLUSIONS_PATH = Path(__file__).resolve().parents[2] / "configs" / "drug_target_exclusions.csv"
DRUG_TARGET_EXCLUSION_COLUMNS = ("drug_chembl_id", "target_chembl_id", "gene_symbol", "ruling", "sources", "note")
# targets a ruling adds to a drug whose ChEMBL mechanism rows do not name them (module docstring, "A ruled addition")
DRUG_TARGET_ADDITIONS_PATH = Path(__file__).resolve().parents[2] / "configs" / "drug_target_additions.csv"
DRUG_TARGET_ADDITION_COLUMNS = ("drug_chembl_id", "target_chembl_id", "gene_symbol", "action_type", "affinity_um", "affinity_measure",
                                "ruling", "sources", "note")
# the quantity types amendment item 37's occupancy split admits (item 37 rulings draft, section 13: Ki, IC50, EC50, Kd)
AFFINITY_MEASURES = ("Ki", "Kd", "IC50", "EC50")
NON_PROTEIN_TARGETS_PATH = Path("configs/non_protein_drug_targets.csv")
DRUGS_ACTING_AS_GRAPH_COMPOUNDS_PATH = Path("configs/drugs_acting_as_graph_compounds.csv")
EXOGENOUS_SUPPLY = "EXOGENOUS SUPPLY"  # action of a drug that is itself the graph compound it raises
GRAPH_COMPOUND_TARGET_PREFIX = "COMPOUND:"  # target id of that action: COMPOUND:<Human-GEM base metabolite ids>

ACTION_TYPE_SIGN: dict[str, float] = {
    "INHIBITOR": -1.0,
    "ANTAGONIST": -1.0,
    "BLOCKER": -1.0,
    "NEGATIVE ALLOSTERIC MODULATOR": -0.5,
    "INVERSE AGONIST": -1.0,
    "CHELATING AGENT": -1.0,
    "SEQUESTERING AGENT": -1.0,
    "DEGRADER": -1.0,
    "RNAI INHIBITOR": -1.0,  # the target is a gene's mRNA, so its product falls
    "ANTISENSE INHIBITOR": -1.0,
    "HYDROLYTIC ENZYME": -1.0,  # an enzyme given as a drug (enzyme replacement) removes the substrate it targets
    "OXIDATIVE ENZYME": -1.0,
    "REDUCING AGENT": -1.0,  # the target molecule is reduced away (cysteamine on cystine)
    "AGONIST": 1.0,
    "PARTIAL AGONIST": 0.5,
    "ACTIVATOR": 1.0,
    "POSITIVE ALLOSTERIC MODULATOR": 0.5,
    "POSITIVE MODULATOR": 0.5,  # SMN2 pre-mRNA splicing modifiers raise full-length SMN
    "OPENER": 1.0,
    "RELEASING AGENT": 1.0,
    "STABILISER": 0.5,
    EXOGENOUS_SUPPLY: 1.0,
    "SUBSTRATE": 0.0,
    "MODULATOR": 0.0,
    "BINDING AGENT": 0.0,
    "CROSS-LINKING AGENT": 0.0,
    "OTHER": 0.0,
}


@dataclass
class DrugTarget:
    target_chembl_id: str
    action_type: str | None
    gene_symbols: list[str] = field(default_factory=list)
    target_type: str | None = None
    pref_name: str | None = None
    accessions: list[str] = field(default_factory=list)  # UniProt accessions, or the Ensembl gene id of a nucleic-acid target
    # a sign per subunit, where a complex target was narrowed to the subunits the Guide to PHARMACOLOGY names and its
    # rows state their own action (perturbation/gtopdb_drug_targets.py, decision 8.11); empty, every subunit takes sign
    gene_signs: dict[str, float] = field(default_factory=dict)

    @property
    def sign(self) -> float:
        return ACTION_TYPE_SIGN.get((self.action_type or "OTHER").upper(), 0.0)

    def sign_of(self, gene_symbol: str) -> float:
        return float(self.gene_signs.get(gene_symbol, self.sign))


@dataclass(frozen=True)
class ActionConflictResolution:
    """A row of configs/chembl_action_conflict_resolutions.csv: the action curated for one drug and target."""
    drug_chembl_id: str
    target_chembl_id: str
    chosen_action: str
    sources: str
    note: str = ""


@dataclass(frozen=True)
class DrugTargetExclusion:
    """A row of configs/drug_target_exclusions.csv (module docstring, "A ruled removal"): drug_chembl_id blank means
    every drug, gene_symbol blank the whole target; a row may not leave both blank."""
    drug_chembl_id: str
    target_chembl_id: str
    gene_symbol: str
    ruling: str
    sources: str
    note: str = ""

    def applies_to(self, target_chembl_id: str, drug_chembl_ids: set[str]) -> bool:
        return self.target_chembl_id == target_chembl_id and (not self.drug_chembl_id or self.drug_chembl_id in drug_chembl_ids)


@dataclass(frozen=True)
class DrugTargetAddition:
    """A row of configs/drug_target_additions.csv (module docstring, "A ruled addition"): one gene of a ChEMBL target a
    ruling adds to one drug, with the action that gives its sign. affinity_um is the sourced affinity in micromolar and
    affinity_measure its quantity type (AFFINITY_MEASURES), both None where none is sourced; recorded for the occupancy
    weighting of amendment item 37, which is not built, and read by nothing else."""
    drug_chembl_id: str
    target_chembl_id: str
    gene_symbol: str
    action_type: str
    ruling: str
    sources: str
    affinity_um: float | None = None
    affinity_measure: str | None = None
    note: str = ""

    @property
    def sign(self) -> float:
        return ACTION_TYPE_SIGN[self.action_type]


@dataclass(frozen=True)
class ActionConflict:
    """One target to which a drug's ChEMBL mechanism rows give more than one action type (module docstring).

    resolved_action is the action of the resolution row applied, and None for a target withheld until one is curated."""
    drug_chembl_ids: tuple[str, ...]  # the ChEMBL ids the drug was looked up by
    target_chembl_id: str
    action_types: tuple[str, ...]  # the distinct action types of the rows, sorted
    mechanism_rows: tuple[str, ...]  # "<molecule_chembl_id>:<action_type>:<mec_id>" of each row naming the target
    target_pref_name: str | None = None
    gene_symbols: tuple[str, ...] = ()
    resolved_action: str | None = None
    resolution_drug_chembl_id: str | None = None

    @property
    def withheld(self) -> bool:
        return self.resolved_action is None


@dataclass
class ChemblCaches:
    pubchem_to_chembl: dict[str, list[str]]
    mechanisms_by_molecule: dict[str, list[dict]]
    targets: dict[str, dict]
    # configs/chembl_action_conflict_resolutions.csv as read_action_conflict_resolutions keys it; None reads that table
    action_resolutions: Mapping[tuple[str, str], ActionConflictResolution] | None = None


def mechanisms_by_parent_and_molecule(mechanisms: list[dict]) -> dict[str, list[dict]]:
    """ChEMBL molecule id -> its mechanisms, keyed by molecule_chembl_id and by parent_molecule_chembl_id.

    ChEMBL records many mechanisms on a salt or prodrug form with the parent in parent_molecule_chembl_id (1,626 of the
    7,561 rows of ChEMBL 37; amitriptyline's are on its hydrochloride CHEMBL1200964, parent CHEMBL629), so a table keyed
    by molecule_chembl_id alone misses them for the parent. The SIDER route, the OnSIDES bridge, the target fetch and
    the report builder all key the table through this function so they apply one rule.
    """
    by_molecule: dict[str, list[dict]] = {}
    for mechanism in mechanisms:
        for key in sorted({mechanism.get("molecule_chembl_id"), mechanism.get("parent_molecule_chembl_id")} - {None, ""}):
            by_molecule.setdefault(key, []).append(mechanism)
    return by_molecule


def read_chembl_parent_corrections(path: Path | None = CHEMBL_PARENT_CORRECTIONS_PATH) -> tuple[dict[str, list[str]], set[str]]:
    """(PubChem CID as the cache keys it -> the ChEMBL parents to add, the ChEMBL releases the rows were verified on)
    of configs/chembl_parent_corrections.csv; ({}, set()) without a table."""
    if path is None or not Path(path).exists():
        return {}, set()
    corrections: dict[str, list[str]] = {}
    releases: set[str] = set()
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            parent = (row.get("correct_parent_chembl_id") or "").strip()
            if not parent:
                continue
            cid = str(int(row["pubchem_cid"]))
            if parent not in corrections.setdefault(cid, []):
                corrections[cid].append(parent)
            releases.add((row.get("chembl_release") or "").strip())
    return corrections, releases


def corrected_pubchem_to_chembl(pubchem_to_chembl: dict[str, list[str]], corrections: dict[str, list[str]]) -> dict[str, list[str]]:
    """pubchem_to_chembl with each correction's parents added to its CID's ids (a union: the cache's own ids are kept,
    since a salt registered as a mechanism molecule resolves through them; a CID the cache lacks or maps to nothing
    gets the parents alone). A new dict; the input is not changed."""
    corrected = {cid: list(chembl_ids) for cid, chembl_ids in pubchem_to_chembl.items()}
    for cid, parents in corrections.items():
        chembl_ids = corrected.setdefault(cid, [])
        chembl_ids.extend(parent for parent in parents if parent not in chembl_ids)
    return corrected


def read_pubchem_to_chembl(mapping_path: Path, corrections_path: Path | None = CHEMBL_PARENT_CORRECTIONS_PATH) -> dict[str, list[str]]:
    """The cache's PubChem-to-ChEMBL map with configs/chembl_parent_corrections.csv applied (module docstring).

    The table's parents were verified against one ChEMBL release, so when the cache directory names its release
    (chembl_release.json beside the map) and a row names another, this refuses rather than add an id the cache's
    release may not hold. corrections_path None reads the map as the fetch wrote it.
    """
    mapping_path = Path(mapping_path)
    pubchem_to_chembl = json.loads(mapping_path.read_text(encoding="utf-8"))
    corrections, releases = read_chembl_parent_corrections(corrections_path)
    if not corrections:
        return pubchem_to_chembl
    release_path = mapping_path.parent / CHEMBL_RELEASE_FILENAME
    if release_path.exists():
        cache_release = json.loads(release_path.read_text(encoding="utf-8")).get("chembl_db_version")
        if releases != {cache_release}:
            raise ValueError(f"{corrections_path} was verified on {sorted(releases)} but {mapping_path} is from {cache_release}; "
                             "re-verify every row against the new release before applying it")
    return corrected_pubchem_to_chembl(pubchem_to_chembl, corrections)


def read_action_conflict_resolutions(path: Path | None = CHEMBL_ACTION_CONFLICT_RESOLUTIONS_PATH) -> dict[tuple[str, str], ActionConflictResolution]:
    """(drug ChEMBL id, target ChEMBL id) -> its row of configs/chembl_action_conflict_resolutions.csv; {} without a table.

    Refuses a table with other columns, a row without both ids, a chosen action ACTION_TYPE_SIGN does not know, a row
    that names no source (a curated row names its sources), and a pair given twice."""
    if path is None or not Path(path).exists():
        return {}
    resolutions: dict[tuple[str, str], ActionConflictResolution] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != ACTION_CONFLICT_RESOLUTION_COLUMNS:
            raise ValueError(f"{path} has columns {reader.fieldnames}, expected {list(ACTION_CONFLICT_RESOLUTION_COLUMNS)}")
        for line_number, row in enumerate(reader, start=2):
            values = {column: (row.get(column) or "").strip() for column in ACTION_CONFLICT_RESOLUTION_COLUMNS}
            resolution = ActionConflictResolution(values["drug_chembl_id"], values["target_chembl_id"], values["chosen_action"].upper(), values["sources"], values["note"])
            if not resolution.drug_chembl_id or not resolution.target_chembl_id:
                raise ValueError(f"{path} line {line_number}: a row needs both drug_chembl_id and target_chembl_id")
            if resolution.chosen_action not in ACTION_TYPE_SIGN:
                raise ValueError(f"{path} line {line_number}: chosen_action {values['chosen_action']!r} is not an action type of ACTION_TYPE_SIGN")
            if not resolution.sources:
                raise ValueError(f"{path} line {line_number}: a curated row names its sources")
            key = (resolution.drug_chembl_id, resolution.target_chembl_id)
            if key in resolutions:
                raise ValueError(f"{path} line {line_number}: {key} is resolved twice")
            resolutions[key] = resolution
    return resolutions


@lru_cache(maxsize=8)
def _cached_action_conflict_resolutions(path: str, modified_ns: int, size: int) -> dict[tuple[str, str], ActionConflictResolution]:
    return read_action_conflict_resolutions(Path(path))


def default_action_conflict_resolutions() -> dict[tuple[str, str], ActionConflictResolution]:
    """configs/chembl_action_conflict_resolutions.csv, read again only when the file changes; {} without it."""
    path = CHEMBL_ACTION_CONFLICT_RESOLUTIONS_PATH
    if not path.exists():
        return {}
    stat = path.stat()
    return _cached_action_conflict_resolutions(str(path), stat.st_mtime_ns, stat.st_size)


def read_drug_target_exclusions(path: Path | None = DRUG_TARGET_EXCLUSIONS_PATH) -> tuple[DrugTargetExclusion, ...]:
    """The rows of configs/drug_target_exclusions.csv; () without a table.

    Refuses a table with other columns, a row without a target, a row that leaves both the drug and the member blank
    (it would remove a whole target from every drug, which no ruling has asked for), a row that names no ruling or no
    source (a curated row names its sources), and a row given twice."""
    if path is None or not Path(path).exists():
        return ()
    exclusions: list[DrugTargetExclusion] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != DRUG_TARGET_EXCLUSION_COLUMNS:
            raise ValueError(f"{path} has columns {reader.fieldnames}, expected {list(DRUG_TARGET_EXCLUSION_COLUMNS)}")
        for line_number, row in enumerate(reader, start=2):
            values = {column: (row.get(column) or "").strip() for column in DRUG_TARGET_EXCLUSION_COLUMNS}
            exclusion = DrugTargetExclusion(**values)
            if not exclusion.target_chembl_id:
                raise ValueError(f"{path} line {line_number}: a row names the target it removes from")
            if not exclusion.drug_chembl_id and not exclusion.gene_symbol:
                raise ValueError(f"{path} line {line_number}: a row names a drug, a member gene or both")
            if not exclusion.ruling or not exclusion.sources:
                raise ValueError(f"{path} line {line_number}: a curated row names its ruling and its sources")
            key = (exclusion.drug_chembl_id, exclusion.target_chembl_id, exclusion.gene_symbol)
            if any((other.drug_chembl_id, other.target_chembl_id, other.gene_symbol) == key for other in exclusions):
                raise ValueError(f"{path} line {line_number}: {key} is given twice")
            exclusions.append(exclusion)
    return tuple(exclusions)


@lru_cache(maxsize=8)
def _cached_drug_target_exclusions(path: str, modified_ns: int, size: int) -> tuple[DrugTargetExclusion, ...]:
    return read_drug_target_exclusions(Path(path))


def default_drug_target_exclusions() -> tuple[DrugTargetExclusion, ...]:
    """configs/drug_target_exclusions.csv, read again only when the file changes; () without it."""
    path = DRUG_TARGET_EXCLUSIONS_PATH
    if not path.exists():
        return ()
    stat = path.stat()
    return _cached_drug_target_exclusions(str(path), stat.st_mtime_ns, stat.st_size)


def read_drug_target_additions(path: Path | None = DRUG_TARGET_ADDITIONS_PATH) -> tuple[DrugTargetAddition, ...]:
    """The rows of configs/drug_target_additions.csv, in file order; () without a table.

    Refuses a table with other columns, a row without its drug, target or gene, an action type ACTION_TYPE_SIGN does not
    know, a row that names no ruling or no source (a curated row names its sources), an affinity that is not a positive
    number, an affinity without its quantity type or a quantity type without an affinity, a quantity type outside
    AFFINITY_MEASURES, a row given twice, and two rows of one drug and target that give different actions (one drug, one
    target, one action)."""
    if path is None or not Path(path).exists():
        return ()
    additions: list[DrugTargetAddition] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != DRUG_TARGET_ADDITION_COLUMNS:
            raise ValueError(f"{path} has columns {reader.fieldnames}, expected {list(DRUG_TARGET_ADDITION_COLUMNS)}")
        for line_number, row in enumerate(reader, start=2):
            values = {column: (row.get(column) or "").strip() for column in DRUG_TARGET_ADDITION_COLUMNS}
            if not values["drug_chembl_id"] or not values["target_chembl_id"] or not values["gene_symbol"]:
                raise ValueError(f"{path} line {line_number}: a row names the drug, the target and the gene it adds")
            action_type = values["action_type"].upper()
            if action_type not in ACTION_TYPE_SIGN:
                raise ValueError(f"{path} line {line_number}: action_type {values['action_type']!r} is not an action type of ACTION_TYPE_SIGN")
            if not values["ruling"] or not values["sources"]:
                raise ValueError(f"{path} line {line_number}: a curated row names its ruling and its sources")
            if bool(values["affinity_um"]) != bool(values["affinity_measure"]):
                raise ValueError(f"{path} line {line_number}: an affinity is given with its quantity type, and a quantity type with its affinity")
            affinity_um = None
            if values["affinity_um"]:
                try:
                    affinity_um = float(values["affinity_um"])
                except ValueError:
                    affinity_um = float("nan")
                if not affinity_um > 0 or affinity_um == float("inf"):
                    raise ValueError(f"{path} line {line_number}: affinity_um {values['affinity_um']!r} is not a positive number")
                if values["affinity_measure"] not in AFFINITY_MEASURES:
                    raise ValueError(f"{path} line {line_number}: affinity_measure {values['affinity_measure']!r} is not one of {list(AFFINITY_MEASURES)}")
            addition = DrugTargetAddition(values["drug_chembl_id"], values["target_chembl_id"], values["gene_symbol"], action_type,
                                          values["ruling"], values["sources"], affinity_um, values["affinity_measure"] or None, values["note"])
            for other in additions:
                if (other.drug_chembl_id, other.target_chembl_id) != (addition.drug_chembl_id, addition.target_chembl_id):
                    continue
                if other.gene_symbol == addition.gene_symbol:
                    raise ValueError(f"{path} line {line_number}: {(addition.drug_chembl_id, addition.target_chembl_id, addition.gene_symbol)} is given twice")
                if other.action_type != addition.action_type:
                    raise ValueError(f"{path} line {line_number}: {addition.drug_chembl_id} {addition.target_chembl_id} is given the actions "
                                     f"{other.action_type} and {addition.action_type}")
            additions.append(addition)
    return tuple(additions)


@lru_cache(maxsize=8)
def _cached_drug_target_additions(path: str, modified_ns: int, size: int) -> tuple[DrugTargetAddition, ...]:
    return read_drug_target_additions(Path(path))


def default_drug_target_additions() -> tuple[DrugTargetAddition, ...]:
    """configs/drug_target_additions.csv, read again only when the file changes; () without it."""
    path = DRUG_TARGET_ADDITIONS_PATH
    if not path.exists():
        return ()
    stat = path.stat()
    return _cached_drug_target_additions(str(path), stat.st_mtime_ns, stat.st_size)


def added_targets(drug_chembl_ids: set[str], named_target_ids: set[str], targets: dict[str, dict], additions: tuple[DrugTargetAddition, ...],
                  exclusions: tuple[DrugTargetExclusion, ...], human_only: bool = True) -> list[DrugTarget]:
    """The targets additions adds to the drug known by drug_chembl_ids (its ids and the molecule and parent ids of its
    mechanism rows), one DrugTarget per added ChEMBL target with the rows' genes in file order (module docstring, "A
    ruled addition").

    Refuses, rather than drops, an addition that cannot stand: a target among named_target_ids (the targets the drug's
    ChEMBL rows name, kept or not), a target or gene exclusions remove for this drug, a target the cache's targets hold
    no record of (its genes and organism come from the record), a gene the record does not list, and, with human_only,
    a target in another organism. A ruled row that silently did nothing is what this table exists to prevent."""
    rows_by_target: dict[str, list[DrugTargetAddition]] = {}
    for addition in additions:
        if addition.drug_chembl_id in drug_chembl_ids:
            rows_by_target.setdefault(addition.target_chembl_id, []).append(addition)
    added: list[DrugTarget] = []
    for target_id, rows in rows_by_target.items():
        where = f"configs/drug_target_additions.csv: {rows[0].drug_chembl_id} {target_id}"
        if target_id in named_target_ids:
            raise ValueError(f"{where} is a target the drug's ChEMBL mechanism rows name already; a curated action for it belongs in "
                             "configs/chembl_action_conflict_resolutions.csv, and a removal in configs/drug_target_exclusions.csv")
        removed_whole, removed_members = excluded_members(target_id, drug_chembl_ids, exclusions)
        if removed_whole or removed_members & {row.gene_symbol for row in rows}:
            raise ValueError(f"{where} is added and removed by configs/drug_target_exclusions.csv for the same drug")
        record = targets.get(target_id)
        if record is None:
            raise ValueError(f"{where}: the ChEMBL cache holds no record of the target, so its genes and organism are unknown")
        if human_only and record.get("organism") != "Homo sapiens":
            raise ValueError(f"{where}: the target is in {record.get('organism')!r}, not Homo sapiens")
        missing = [row.gene_symbol for row in rows if row.gene_symbol not in (record.get("gene_symbols") or [])]
        if missing:
            raise ValueError(f"{where}: the cache's record of the target lists {record.get('gene_symbols')}, not {missing}")
        added.append(DrugTarget(target_id, rows[0].action_type, [row.gene_symbol for row in rows], record.get("target_type"),
                                record.get("pref_name"), record.get("accessions", [])))
    return added


def excluded_members(target_chembl_id: str, drug_chembl_ids: set[str], exclusions: tuple[DrugTargetExclusion, ...]) -> tuple[bool, set[str]]:
    """(whether the whole target is removed for this drug, the member genes removed from it) under exclusions."""
    applying = [exclusion for exclusion in exclusions if exclusion.applies_to(target_chembl_id, drug_chembl_ids)]
    return any(not exclusion.gene_symbol for exclusion in applying), {exclusion.gene_symbol for exclusion in applying if exclusion.gene_symbol}


def load_chembl_caches(chembl_directory: Path, corrections_path: Path | None = CHEMBL_PARENT_CORRECTIONS_PATH,
                       action_resolutions_path: Path | None = CHEMBL_ACTION_CONFLICT_RESOLUTIONS_PATH) -> ChemblCaches:
    """The ChEMBL caches of chembl_directory, the PubChem-to-ChEMBL map corrected by read_pubchem_to_chembl and the
    action conflicts resolved by action_resolutions_path (None: no conflict is resolved, every one is withheld)."""
    pubchem_to_chembl = read_pubchem_to_chembl(Path(chembl_directory) / PUBCHEM_TO_CHEMBL_FILENAME, corrections_path)
    mechanisms_by_molecule = mechanisms_by_parent_and_molecule(json.loads((chembl_directory / "mechanisms.json").read_text()))
    targets = json.loads((chembl_directory / "targets.json").read_text())
    return ChemblCaches(pubchem_to_chembl, mechanisms_by_molecule, targets, read_action_conflict_resolutions(action_resolutions_path))


def normalized_action_type(action_type: str | None) -> str | None:
    """A ChEMBL action type upper-cased and stripped; None or blank stays None (a row recording no action)."""
    return (action_type or "").strip().upper() or None


def mechanism_targets(chembl_ids: list[str], mechanisms_by_molecule: dict[str, list[dict]], targets: dict[str, dict], human_only: bool = True,
                      missing_target_ids: set[str] | None = None,
                      action_resolutions: Mapping[tuple[str, str], ActionConflictResolution] | None = None,
                      conflicts: list[ActionConflict] | None = None,
                      exclusions: tuple[DrugTargetExclusion, ...] | None = None,
                      additions: tuple[DrugTargetAddition, ...] | None = None) -> list[DrugTarget]:
    """Mechanism targets of the given ChEMBL molecules (the ids of one drug), one entry per ChEMBL target (families count as one).

    The removals of exclusions are applied first (module docstring, "A ruled removal"; None reads
    configs/drug_target_exclusions.csv, () removes nothing): a row keyed by one of chembl_ids, or by the molecule or
    parent id of a row naming the target, applies. A target removed whole is dropped before anything below; a target
    whose every member gene is removed is dropped too.

    The targets of additions are appended last, after the targets the ChEMBL rows give (module docstring, "A ruled
    addition"; None reads configs/drug_target_additions.csv, () adds nothing): a row keyed by one of chembl_ids, or by
    the molecule or parent id of any of the drug's mechanism rows, applies, and added_targets refuses one that cannot
    stand.

    When the rows naming one target, over all of chembl_ids, carry more than one action type (compared upper-cased; a
    row with no action type counts as one more), no action is chosen from them (module docstring, ruling of 20 November
    2026): the target takes the chosen action of the action_resolutions row keyed by one of chembl_ids and the target,
    and is withheld without one. Each such target is appended to conflicts, when a list is passed, as an ActionConflict,
    resolved or withheld. action_resolutions None reads configs/chembl_action_conflict_resolutions.csv; {} resolves
    nothing. Two resolution rows for one target under two of the drug's ids that choose different actions are refused.
    Every run before 20 November 2026 kept the action of the last row read.

    A target id without a record in targets is kept (its organism is unknown, so the human filter cannot drop it, and
    it has no gene symbols) and added to missing_target_ids when a set is passed.
    """
    if action_resolutions is None:
        action_resolutions = default_action_conflict_resolutions()
    if exclusions is None:
        exclusions = default_drug_target_exclusions()
    if additions is None:
        additions = default_drug_target_additions()
    rows_by_target: dict[str, list[tuple[str, dict]]] = {}
    for chembl_id in chembl_ids:
        for mechanism in mechanisms_by_molecule.get(chembl_id, []):
            target_id = mechanism.get("target_chembl_id")
            if not target_id:
                continue
            rows_by_target.setdefault(target_id, [])
            if all(mechanism is not seen for _, seen in rows_by_target[target_id]):  # a row keyed by both a salt and its parent is one row
                rows_by_target[target_id].append((chembl_id, mechanism))
    drug_targets: list[DrugTarget] = []
    for target_id, rows in rows_by_target.items():
        drug_ids_of_rows = set(chembl_ids) | {mechanism.get(key) for _, mechanism in rows for key in ("molecule_chembl_id", "parent_molecule_chembl_id")}
        removed_whole, removed_members = excluded_members(target_id, drug_ids_of_rows - {None, ""}, exclusions)
        if removed_whole:
            continue
        record = targets.get(target_id)
        if record is None:
            if missing_target_ids is not None:
                missing_target_ids.add(target_id)
            record = {}
        if human_only and record.get("organism") not in (None, "Homo sapiens"):
            continue
        if removed_members:
            members = list(record.get("gene_symbols", []))
            kept_members = [gene for gene in members if gene not in removed_members]
            if members and not kept_members:
                continue
            record = record | {"gene_symbols": kept_members}
        action_types = {normalized_action_type(mechanism.get("action_type")) for _, mechanism in rows}
        action_type = rows[-1][1].get("action_type")
        if len(action_types) > 1:
            drug_ids = tuple(dict.fromkeys(chembl_id for chembl_id in chembl_ids if chembl_id))
            resolutions = {action_resolutions[(drug_id, target_id)] for drug_id in drug_ids if (drug_id, target_id) in action_resolutions}
            if len({resolution.chosen_action for resolution in resolutions}) > 1:
                raise ValueError(f"the resolutions of {target_id} under {drug_ids} choose different actions: {sorted(resolutions, key=str)}")
            resolution = min(resolutions, key=lambda resolution: resolution.drug_chembl_id) if resolutions else None
            if conflicts is not None:
                conflicts.append(ActionConflict(
                    drug_ids, target_id, tuple(sorted(action or "None" for action in action_types)),
                    tuple(f"{mechanism.get('molecule_chembl_id')}:{mechanism.get('action_type')}:{mechanism.get('mec_id')}" for _, mechanism in rows),
                    record.get("pref_name"), tuple(record.get("gene_symbols", [])),
                    resolution.chosen_action if resolution else None, resolution.drug_chembl_id if resolution else None))
            if resolution is None:
                continue
            action_type = resolution.chosen_action
        drug_targets.append(DrugTarget(target_id, action_type, record.get("gene_symbols", []), record.get("target_type"),
                                       record.get("pref_name"), record.get("accessions", [])))
    if additions:
        drug_ids = set(chembl_ids) | {mechanism.get(key) for rows in rows_by_target.values() for _, mechanism in rows
                                      for key in ("molecule_chembl_id", "parent_molecule_chembl_id")}
        drug_targets.extend(added_targets(drug_ids - {None, ""}, set(rows_by_target), targets, additions, exclusions, human_only))
    return drug_targets


def withheld_count(conflicts: list[ActionConflict]) -> int:
    """How many distinct targets conflicts withholds (ActionConflict.withheld)."""
    return len({conflict.target_chembl_id for conflict in conflicts if conflict.withheld})


ACTION_CONFLICTS_REPORT_COLUMNS = ("perturbation_id", "perturbation_label", "route", "drug_chembl_ids", "target_chembl_id", "target_pref_name",
                                   "gene_symbols", "action_types", "mechanism_rows", "status", "resolved_action", "resolution_drug_chembl_id")


def action_conflict_report_rows(perturbation_id: str, perturbation_label: str, route: str, conflicts: list[ActionConflict]) -> list[dict]:
    """Rows of the conflicts report (ACTION_CONFLICTS_REPORT_COLUMNS) for one drug; status is withheld or resolved."""
    return [{"perturbation_id": perturbation_id, "perturbation_label": perturbation_label, "route": route,
             "drug_chembl_ids": ";".join(conflict.drug_chembl_ids), "target_chembl_id": conflict.target_chembl_id,
             "target_pref_name": conflict.target_pref_name or "", "gene_symbols": ";".join(conflict.gene_symbols),
             "action_types": ";".join(conflict.action_types), "mechanism_rows": ";".join(conflict.mechanism_rows),
             "status": "withheld" if conflict.withheld else "resolved", "resolved_action": conflict.resolved_action or "",
             "resolution_drug_chembl_id": conflict.resolution_drug_chembl_id or ""} for conflict in conflicts]


def write_action_conflicts_report(rows: list[dict], path: Path) -> None:
    """Write the conflicts report, one row per distinct row of rows, sorted; the header alone when there is none."""
    unique = sorted({tuple(str(row[column]) for column in ACTION_CONFLICTS_REPORT_COLUMNS) for row in rows})
    pd.DataFrame(unique, columns=list(ACTION_CONFLICTS_REPORT_COLUMNS)).to_csv(path, index=False)


def drug_targets_for_pubchem_cid(pubchem_cid: int, caches: ChemblCaches, human_only: bool = True, extra_chembl_ids: list[str] | None = None,
                                 conflicts: list[ActionConflict] | None = None) -> list[DrugTarget]:
    """Mechanism targets for a SIDER drug, through its ids in caches.pubchem_to_chembl (the cache map with
    configs/chembl_parent_corrections.csv applied, read_pubchem_to_chembl). extra_chembl_ids adds molecules found
    another way (the ChEMBL parents the OnSIDES bridge unified with the drug, when these ids give no target). A target
    whose rows disagree on the action is resolved by caches.action_resolutions or withheld, and appended to conflicts
    (mechanism_targets)."""
    chembl_ids = list(caches.pubchem_to_chembl.get(str(pubchem_cid), [])) + [chembl_id for chembl_id in extra_chembl_ids or [] if chembl_id]
    return mechanism_targets(chembl_ids, caches.mechanisms_by_molecule, caches.targets, human_only=human_only,
                             action_resolutions=caches.action_resolutions, conflicts=conflicts)


def has_dominant_target(drug_targets: list[DrugTarget], max_targets: int | None = 1, withheld_targets: int = 0) -> bool:
    """Version 1 dominant-target rule: at most max_targets distinct ChEMBL targets with a mechanism, a ruled addition of
    configs/drug_target_additions.csv counting as one (module docstring, "A ruled addition").

    Affinity margins are not yet used; a ChEMBL protein-family target (for example the GABA-A
    receptor) counts as one target even though it maps to many gene nodes. max_targets None or 0 lifts the cap: any
    drug with at least one mechanism target passes, and each of its targets is seeded with magnitude 1 spread over
    that target's nodes (docs/drug_targets_any_type.md, "Lifting the single-target rule"). withheld_targets counts the
    targets withheld for an unresolved action conflict (mechanism_targets, withheld_count) against the cap, so
    withholding one of two targets does not admit a drug the rule would refuse; a drug needs a kept target to pass.
    """
    return len(drug_targets) > 0 and (not max_targets or len(drug_targets) + withheld_targets <= max_targets)


def load_drugs_acting_as_graph_compounds(path: Path = DRUGS_ACTING_AS_GRAPH_COMPOUNDS_PATH) -> tuple[dict[int, list[str]], dict[str, list[str]]]:
    """(PubChem CID -> base metabolite ids, ChEMBL id -> base metabolite ids) of configs/drugs_acting_as_graph_compounds.csv."""
    if not Path(path).exists():
        return {}, {}
    table = pd.read_csv(path, dtype=str).fillna("")
    by_pubchem_cid: dict[int, list[str]] = {}
    by_chembl_id: dict[str, list[str]] = {}
    for row in table.itertuples(index=False):
        base_ids = [base_id for base_id in row.base_metabolite_ids.split(";") if base_id]
        if row.pubchem_cid:
            by_pubchem_cid[int(row.pubchem_cid)] = base_ids
        for chembl_id in (identifier for identifier in row.chembl_ids.split(";") if identifier):
            by_chembl_id[chembl_id] = base_ids
    return by_pubchem_cid, by_chembl_id


def check_graph_compounds_have_no_mechanism(compounds_by_chembl_id: dict[str, list[str]], mechanisms_by_molecule: dict[str, list[dict]],
                                            exclusions: tuple[DrugTargetExclusion, ...] | None = None,
                                            additions: tuple[DrugTargetAddition, ...] | None = None) -> None:
    """Refuse a graph-compound entry whose ChEMBL form carries a mechanism: such a drug has protein (or other) targets and
    follows the mechanism rule, so one drug cannot enter through one identifier and be excluded through another. A
    mechanism row whose whole target exclusions removes for that form is not counted (None reads
    configs/drug_target_exclusions.csv); a ruled addition keyed by the form, or by the molecule or parent id of one of
    its mechanism rows, is counted as a mechanism (None reads configs/drug_target_additions.csv)."""
    if exclusions is None:
        exclusions = default_drug_target_exclusions()
    if additions is None:
        additions = default_drug_target_additions()
    added_for = {addition.drug_chembl_id for addition in additions}

    def kept(chembl_id: str, mechanism: dict) -> bool:
        drug_ids = {chembl_id, mechanism.get("molecule_chembl_id"), mechanism.get("parent_molecule_chembl_id")} - {None, ""}
        return not excluded_members(mechanism.get("target_chembl_id") or "", drug_ids, exclusions)[0]

    def has_addition(chembl_id: str) -> bool:
        drug_ids = {chembl_id} | {mechanism.get(key) for mechanism in mechanisms_by_molecule.get(chembl_id, [])
                                  for key in ("molecule_chembl_id", "parent_molecule_chembl_id")}
        return bool(added_for & (drug_ids - {None, ""}))

    with_mechanisms = sorted(chembl_id for chembl_id in compounds_by_chembl_id
                             if has_addition(chembl_id) or any(kept(chembl_id, mechanism) for mechanism in mechanisms_by_molecule.get(chembl_id, [])))
    if with_mechanisms:
        raise ValueError(f"{DRUGS_ACTING_AS_GRAPH_COMPOUNDS_PATH} lists ChEMBL forms that carry a mechanism: {with_mechanisms}")


def graph_compound_target(base_metabolite_ids: list[str]) -> DrugTarget:
    """The one target of a drug that is itself a graph compound: its metabolite nodes, raised."""
    return DrugTarget(GRAPH_COMPOUND_TARGET_PREFIX + ";".join(base_metabolite_ids), EXOGENOUS_SUPPLY, target_type="GRAPH COMPOUND")


def graph_compound_targets(drug_targets: list[DrugTarget], pubchem_cid: int | None, chembl_ids: list[str],
                           compounds_by_pubchem_cid: dict[int, list[str]], compounds_by_chembl_id: dict[str, list[str]]) -> list[DrugTarget]:
    """drug_targets unchanged when ChEMBL gives the drug any mechanism target; otherwise the graph-compound target of
    configs/drugs_acting_as_graph_compounds.csv when the drug is listed there, else none."""
    if drug_targets:
        return drug_targets
    base_ids = compounds_by_pubchem_cid.get(pubchem_cid) if pubchem_cid is not None else None
    for chembl_id in chembl_ids:
        base_ids = base_ids or compounds_by_chembl_id.get(chembl_id)
    return [graph_compound_target(base_ids)] if base_ids else []


@dataclass
class GraphNodeLookup:
    """Graph nodes a drug target stands for, for every ChEMBL target type (module docstring)."""

    node_by_symbol: dict[str, str]
    node_by_ensembl_gene: dict[str, str]
    metabolite_nodes_by_base_id: dict[str, list[str]]
    metabolites_by_target_id: dict[str, list[str]] = field(default_factory=dict)  # configs/non_protein_drug_targets.csv

    @classmethod
    def from_nodes(cls, nodes: pd.DataFrame, non_protein_targets_path: Path | None = NON_PROTEIN_TARGETS_PATH) -> "GraphNodeLookup":
        genes = nodes[nodes.node_type == "gene"]
        node_by_symbol = {symbol: node_id for symbol, node_id in zip(genes.gene_symbol, genes.node_id) if isinstance(symbol, str) and symbol}
        node_by_ensembl_gene = {}
        if "ensembl_gene_id" in genes.columns:
            node_by_ensembl_gene = {ensembl: node_id for ensembl, node_id in zip(genes.ensembl_gene_id, genes.node_id) if isinstance(ensembl, str) and ensembl}
        metabolites = nodes[nodes.node_type == "metabolite"]
        metabolite_nodes_by_base_id: dict[str, list[str]] = {}
        if "base_metabolite_id" in metabolites.columns:
            for base_id, node_id in zip(metabolites.base_metabolite_id, metabolites.node_id):
                if isinstance(base_id, str):
                    metabolite_nodes_by_base_id.setdefault(base_id, []).append(node_id)
        metabolites_by_target_id: dict[str, list[str]] = {}
        if non_protein_targets_path is not None and Path(non_protein_targets_path).exists():
            table = pd.read_csv(non_protein_targets_path, dtype=str).fillna("")
            metabolites_by_target_id = {row.target_chembl_id: [base_id for base_id in row.base_metabolite_ids.split(";") if base_id]
                                        for row in table.itertuples(index=False)}
        return cls(node_by_symbol, node_by_ensembl_gene, {base_id: sorted(node_ids) for base_id, node_ids in metabolite_nodes_by_base_id.items()}, metabolites_by_target_id)

    def nodes_of_target(self, target: DrugTarget) -> list[str]:
        gene_nodes = [self.node_by_symbol[symbol] for symbol in target.gene_symbols if symbol in self.node_by_symbol]
        if gene_nodes:
            return gene_nodes
        if target.target_type == "NUCLEIC-ACID":
            return [self.node_by_ensembl_gene[accession] for accession in target.accessions if accession in self.node_by_ensembl_gene]
        if target.target_chembl_id.startswith(GRAPH_COMPOUND_TARGET_PREFIX):
            base_ids = target.target_chembl_id.removeprefix(GRAPH_COMPOUND_TARGET_PREFIX).split(";")
        else:
            base_ids = self.metabolites_by_target_id.get(target.target_chembl_id, [])
        return [node_id for base_id in base_ids for node_id in self.metabolite_nodes_by_base_id.get(base_id, [])]

    def perturbation_nodes(self, drug_targets: list[DrugTarget]) -> list[list]:
        """[node id, sign, magnitude] triples; magnitude is 1 / number of graph nodes under each target. A gene node takes
        its subunit's own sign when the target carries one (DrugTarget.gene_signs), the target's sign otherwise."""
        triples: list[list] = []
        for target in drug_targets:
            mapped = self.nodes_of_target(target)
            symbol_of_node = {self.node_by_symbol[symbol]: symbol for symbol in target.gene_symbols if symbol in self.node_by_symbol}
            triples.extend([node_id, target.sign_of(symbol_of_node[node_id]) if node_id in symbol_of_node else target.sign, 1.0 / len(mapped)]
                           for node_id in mapped)
        return triples
