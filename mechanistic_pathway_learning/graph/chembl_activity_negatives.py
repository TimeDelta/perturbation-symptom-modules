"""ChEMBL 37 activity records as observations on the graph's compound-to-protein edges (decision 9.91).

What is an observation. An activity record of ChEMBL 37 (CC BY-SA 3.0) for a compound the graph holds and a human
single-protein target the graph holds, on an edge from that compound's node to that protein's node:
  - negative: the record is flagged Inactive or Not Active (activity_comment), or states a value only as a lower limit
    (standard_relation ">" or ">=") of at least 10 uM (10,000 nM) for a potency type (IC50, Ki, Kd, EC50, AC50, XC50,
    Potency, Kb). A ">" row states its own detection limit; a limit below 10 uM says nothing at 10 uM and is recorded
    as inconclusive. The largest limit is kept per edge (chembl_limit_um);
  - positive: a measured potency, standard_relation "=", with pchembl_value of at least 5 (10 uM or better);
  - a record ChEMBL flags in data_validity_comment (a transcription error, an out-of-range value) counts neither way.
The likelihood ratio (configs/edge_negative_likelihood_ratios.csv) reads the reproducibility of ChEMBL activity calls
between assays at 10 uM (Landrum and Riniker 2024), so 10 uM is the threshold on both sides. Independent observations
are counted as distinct ChEMBL documents, so one paper's replicate rows count once.

Which compounds. An endogenous metabolite through the identifiers the graph already uses: the node's base metabolite id
to ChEBI (Human-GEM's metChEBIID, or a base id that is itself a ChEBI id, as the BRENDA and Reactome additions name
them) and ChEBI to ChEMBL through UniChem's ChEMBL-ChEBI mapping (EBI FTP, src1src7). A drug node DRUG:<perturbation>
through its PubChem compound (the STITCH id CID1xxxxxxxx) and the PubChem-to-ChEMBL map the drug target fetch pins
(data/raw/chembl/pubchem_to_chembl_with_parents.json), or its ChEMBL id when the perturbation is named by one.
Activities are queried by parent compound, so a salt's records count for its parent.

Which targets. A protein node through its UniProt accession, a gene node through HGNC's UniProt ids, and the accession
to a ChEMBL target of type SINGLE PROTEIN through ChEMBL's chembl_uniprot_mapping.txt. A protein complex or family
target is not read, since its records do not say which member they concern.

Limitation, put to the owner (decision 9.91): an endogenous metabolite can act at concentrations far above 10 uM (ATP
is millimolar in the cytosol), so a record inactive at 10 uM is weak evidence against a metabolite-to-enzyme edge whose
effect is at physiological concentration; the table keeps each record's limit so a stricter rule can be read later.
"""
from __future__ import annotations

import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.graph.edge_evidence import accession_of, symbol_of

DEFAULT_ACTIVITIES = Path("data/raw/chembl_37/edge_activities.parquet")
DEFAULT_TARGET_MAPPING = Path("data/raw/chembl_37/chembl_uniprot_mapping.txt")
DEFAULT_CHEBI_MAPPING = Path("data/raw/chembl_37/src1src7.txt.gz")
DEFAULT_PUBCHEM_MAPPING = Path("data/raw/chembl/pubchem_to_chembl_with_parents.json")
DEFAULT_METABOLITES = Path("data/raw/Human-GEM/model/metabolites.tsv")
CHEMBL_RELATIONS = ("inhibits", "activates", "binds", "targets", "cofactor_of")  # compound-to-protein relations read; the ratio table names those it moves
POTENCY_TYPES = frozenset({"IC50", "Ki", "Kd", "EC50", "AC50", "XC50", "Potency", "Kb"})
INACTIVE_COMMENTS = frozenset({"inactive", "not active"})
NEGATIVE_LIMIT_NM = 10_000.0  # 10 uM, the binning of Landrum and Riniker 2024 the likelihood ratio is read at
POSITIVE_PCHEMBL = 5.0
LOWER_LIMIT_RELATIONS = frozenset({">", ">="})
ACTIVITY_FIELDS = ("activity_id", "molecule_chembl_id", "parent_molecule_chembl_id", "target_chembl_id", "standard_type", "standard_relation",
                   "standard_value", "standard_units", "pchembl_value", "activity_comment", "data_validity_comment", "document_chembl_id", "assay_chembl_id",
                   "assay_type", "target_organism")


def classify_activity(row) -> str:
    """negative, positive, inconclusive or flagged, as the module docstring defines them."""
    get = row.get if isinstance(row, dict) else (lambda name, default=None: getattr(row, name, default))
    if isinstance(get("data_validity_comment"), str) and get("data_validity_comment").strip():
        return "flagged"
    comment = str(get("activity_comment") or "").strip().lower()
    if comment in INACTIVE_COMMENTS:
        return "negative"
    relation = str(get("standard_relation") or "").strip().strip("'")
    value, units, kind = get("standard_value"), str(get("standard_units") or ""), str(get("standard_type") or "")
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = float("nan")
    if relation in LOWER_LIMIT_RELATIONS and kind in POTENCY_TYPES and units == "nM" and np.isfinite(value):
        return "negative" if value >= NEGATIVE_LIMIT_NM else "inconclusive"
    try:
        pchembl = float(get("pchembl_value"))
    except (TypeError, ValueError):
        pchembl = float("nan")
    if relation == "=" and np.isfinite(pchembl) and pchembl >= POSITIVE_PCHEMBL:
        return "positive"
    return "inconclusive"


def read_target_mapping(path: Path = DEFAULT_TARGET_MAPPING) -> dict[str, set[str]]:
    """UniProt accession -> ChEMBL target ids of type SINGLE PROTEIN."""
    mapping: dict[str, set[str]] = defaultdict(set)
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 4 and parts[3].strip() == "SINGLE PROTEIN":
                mapping[parts[0].strip()].add(parts[1].strip())
    return dict(mapping)


def read_chebi_mapping(path: Path = DEFAULT_CHEBI_MAPPING) -> dict[str, set[str]]:
    """ChEBI id ('CHEBI:15422') -> ChEMBL molecule ids, from UniChem's src1src7 file (ChEMBL id, ChEBI id per line)."""
    opener = gzip.open if str(path).endswith(".gz") else open
    mapping: dict[str, set[str]] = defaultdict(set)
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) == 2 and parts[0].startswith("CHEMBL"):
                chebi = parts[1] if parts[1].startswith("CHEBI:") else f"CHEBI:{parts[1]}"
                mapping[chebi].add(parts[0])
    return dict(mapping)


def chebi_of_base(metabolites_table: pd.DataFrame | None) -> dict[str, set[str]]:
    """Human-GEM base metabolite id (metsNoComp) -> its ChEBI ids."""
    if metabolites_table is None:
        return {}
    mapping: dict[str, set[str]] = defaultdict(set)
    for base, cell in zip(metabolites_table["metsNoComp"], metabolites_table["metChEBIID"]):
        for chebi in str(cell).replace(",", ";").split(";") if isinstance(cell, str) else []:
            chebi = chebi.strip()
            if chebi.startswith("CHEBI:"):
                mapping[str(base)].add(chebi)
    return dict(mapping)


def chebi_ids_of_base(base: str, human_gem_chebi: dict[str, set[str]]) -> set[str]:
    """A base metabolite id's ChEBI ids: Human-GEM's for a MAM id, the id itself for 'CHEBI17632' or 'CHEBI:17632'."""
    text = str(base)
    if text.upper().startswith("CHEBI"):
        return {"CHEBI:" + text[5:].lstrip(":_")}
    return set(human_gem_chebi.get(text, set()))


def pubchem_cid_of_perturbation(perturbation_id: str) -> str | None:
    """'CID100000896' (STITCH: 'CID1' then the PubChem CID padded to eight digits) -> '896'."""
    text = str(perturbation_id)
    if text.startswith("CID") and text[3:].isdigit():
        number = int(text[3:])
        return str(number - 100_000_000 if number >= 100_000_000 else number)
    return None


def compound_ids_of_nodes(nodes: pd.DataFrame, human_gem_chebi: dict[str, set[str]], chembl_of_chebi: dict[str, set[str]],
                          chembl_of_pubchem: dict[str, list[str]]) -> dict[str, set[str]]:
    """Graph node id -> ChEMBL molecule ids, for metabolite and drug nodes."""
    compounds: dict[str, set[str]] = {}
    has_base = "base_metabolite_id" in nodes.columns
    for row in nodes.itertuples(index=False):
        node_id, node_type = str(row.node_id), str(getattr(row, "node_type", ""))
        found: set[str] = set()
        if node_type == "metabolite" and has_base and isinstance(row.base_metabolite_id, str):
            for chebi in chebi_ids_of_base(row.base_metabolite_id, human_gem_chebi):
                found |= chembl_of_chebi.get(chebi, set())
        elif node_type == "drug" or node_id.startswith("DRUG:"):
            perturbation = node_id.split(":", 1)[1] if ":" in node_id else node_id
            if perturbation.startswith("CHEMBL"):
                found.add(perturbation)
            cid = pubchem_cid_of_perturbation(perturbation)
            if cid is not None:
                found |= set(chembl_of_pubchem.get(cid, []))
        if found:
            compounds[node_id] = found
    return compounds


def target_ids_of_nodes(nodes: pd.DataFrame, targets_of_accession: dict[str, set[str]], accessions_of_symbol: dict[str, set[str]]) -> dict[str, set[str]]:
    """Graph node id -> ChEMBL single-protein target ids, for protein nodes (by accession) and gene nodes (by symbol)."""
    targets: dict[str, set[str]] = {}
    for row in nodes.itertuples(index=False):
        node_id, node_type = str(row.node_id), str(getattr(row, "node_type", ""))
        if node_type not in ("protein", "gene"):
            continue
        accessions = set()
        entry = getattr(row, "uniprot_entry", None)
        if isinstance(entry, str) and entry:
            accessions |= {part.strip() for part in entry.split(";") if part.strip()}
        accession = accession_of(node_id)
        if accession:
            accessions.add(accession)
        if not accessions:
            accessions = set(accessions_of_symbol.get(symbol_of(node_id), set()))
        found = set().union(*(targets_of_accession.get(accession, set()) for accession in accessions)) if accessions else set()
        if found:
            targets[node_id] = found
    return targets


def candidate_pairs(evidence: pd.DataFrame, compounds: dict[str, set[str]], targets: dict[str, set[str]]) -> dict[str, set[str]]:
    """ChEMBL compound id -> the ChEMBL target ids it has a graph edge to, over the compound-to-protein relations."""
    pairs: dict[str, set[str]] = defaultdict(set)
    selected = evidence["relation_type"].astype(str).isin(CHEMBL_RELATIONS)
    for source, target in zip(evidence.loc[selected, "source_id"], evidence.loc[selected, "target_id"]):
        for compound in compounds.get(str(source), ()):
            pairs[compound] |= targets.get(str(target), set())
    return {compound: found for compound, found in pairs.items() if found}


def chembl_edge_columns(evidence: pd.DataFrame, compounds: dict[str, set[str]], targets: dict[str, set[str]], activities: pd.DataFrame) -> pd.DataFrame:
    """Per row of the edge evidence table: chembl_negative and chembl_positive (distinct documents), chembl_limit_um (the
    largest stated limit among the negative '>' records, NaN when every negative is a flag), chembl_inconclusive and
    chembl_documents."""
    classified = activities.assign(call=[classify_activity(row) for row in activities.to_dict("records")]) if len(activities) else \
        pd.DataFrame(columns=[*ACTIVITY_FIELDS, "call"])
    compound_column = "parent_molecule_chembl_id" if "parent_molecule_chembl_id" in classified.columns else "molecule_chembl_id"
    by_pair: dict[tuple[str, str], dict[str, set]] = defaultdict(lambda: {"negative": set(), "positive": set(), "inconclusive": set(), "limits": set()})
    for row in classified.itertuples(index=False):
        compound = getattr(row, compound_column) or getattr(row, "molecule_chembl_id", None)
        key = (str(compound), str(row.target_chembl_id))
        document = str(getattr(row, "document_chembl_id", "") or getattr(row, "activity_id", ""))
        if row.call in ("negative", "positive", "inconclusive"):
            by_pair[key][row.call].add(document)
        if row.call == "negative" and str(getattr(row, "standard_relation", "") or "") in LOWER_LIMIT_RELATIONS:
            by_pair[key]["limits"].add(float(row.standard_value) / 1000.0)
    negative, positive, inconclusive, limits, documents = [], [], [], [], []
    for source, target, relation in zip(evidence["source_id"], evidence["target_id"], evidence["relation_type"]):
        found = {"negative": set(), "positive": set(), "inconclusive": set(), "limits": set()}
        if str(relation) in CHEMBL_RELATIONS:
            for compound in compounds.get(str(source), ()):
                for target_id in targets.get(str(target), ()):
                    for name, values in by_pair.get((compound, target_id), {}).items():
                        found[name] |= values
        negative.append(len(found["negative"]))
        positive.append(len(found["positive"]))
        inconclusive.append(len(found["inconclusive"]))
        limits.append(max(found["limits"]) if found["limits"] else np.nan)
        documents.append(";".join(sorted(found["negative"] | found["positive"])))
    return pd.DataFrame({"chembl_negative": np.array(negative, dtype=np.int64), "chembl_positive": np.array(positive, dtype=np.int64),
                         "chembl_limit_um": np.array(limits, dtype=float), "chembl_inconclusive": np.array(inconclusive, dtype=np.int64),
                         "chembl_documents": documents}, index=evidence.index)


def read_pubchem_mapping(path: Path = DEFAULT_PUBCHEM_MAPPING) -> dict[str, list[str]]:
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).is_file() else {}
