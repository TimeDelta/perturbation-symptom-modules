"""Corrections to the pinned Human-GEM model, applied where the model is read (rulings Q1, Q5a-b and Q5d of 20 November
2026, and the MAM00373, MAM02766, pristanic acid and 15(R)-HEPE repairs the owner accepted the same day;
docs/item37_rulings_draft_2026-11-13.md sections 21 and 22).

The pinned files under data/raw/Human-GEM/model/ (Human-GEM v2.0.1, scripts/fetch_raw_sources.sh) are never edited.
configs/human_gem_corrections.csv lists each repair, and every reader of the model's metabolite table, of its species
or of its reactions reads through this module, so the repair holds wherever the model is read. The repairs in the
table, by kind:

- A cell of metabolites.tsv that holds the wrong value: an identifier naming the wrong compound, or a structure. Q1:
  six metabolites, ten compartment rows, whose metChEBIID is a deuterated internal standard rather than the compound
  (diazepam carried diazepam-d8, CHEBI:194180, and so on). Q5a and Q5b: the HMDB, LIPID MAPS and MetaNetX ids of MAM03652e and the KEGG and
  MetaNetX ids of MAM20077n, which belong to the compound the other compartment row of the same id really is, and
  the BiGG id of the moved row MAM03652c. MAM00373 (15(R)-HEPE): the c, n, r and x rows carry the structure of a
  16-hydroxy positional isomer, and take the 15(R) structure and CHEBI:90819 that the e row already holds. MAM02766
  ((2S)-pristanic acid): the c, e, r and x rows take the (2S,6R,10R) structure and the ChEBI cell
  "CHEBI:761004;CHEBI:77268" (two ids separated by ";", the form four pinned rows already have; every reader of
  metChEBIID splits the cell on ";").
- A model name that disagrees with the other compartment rows of one compound: MAM02766r "pristanic acid" becomes
  "(2S)-pristanic acid", the name of its c, e and x rows.
- A compartment row filed under the wrong metabolite id (Q5a, Q5b). Node ids, base_metabolite_id and the
  stoichiometry come from the model's species, so such a row is renamed as a species: in the metabolite table, in the
  SBML text (species id, metaid, annotation anchor and every speciesReference) and in a cobra model. MAM03652c, which
  is palmitoylethanolamide, becomes MAM03885c (the id upstream gave it in Human-GEM 2.1.0) beside the extracellular
  MAM03885e the pinned model already has; MAM20077m, the thiamine-diphosphate adduct of the 2-oxoadipate
  dehydrogenase step, becomes MAM20089m, an id unused in the pinned files. A rename changes a node id, so a graph
  built with it is a new graph version.
- A species the pinned model lacks, added as another compartment row of a metabolite it has (Q5d): MAM03885l
  (palmitoylethanolamide, copied from MAM03885e) and MAM01797l (ethanolamine, copied from MAM01797c), the lysosomal
  substrate and product of MAR20093. The new row copies every cell of its template's metabolite-table row as
  corrected, except mets, metsNoComp and the two cells that name one compartment row (metHMR2ID, metRetired, left
  empty: no earlier model had the row), and its template's SBML species and cobra metabolite (name, formula, charge,
  notes, annotations) in its own compartment.
- A reaction's participant moved to another species of the same formula and charge (Q5d): MAR20093, NAAA's
  palmitoylethanolamide hydrolysis, moves from the cytosol to the lysosome, every participant with its coefficient.
  After the move MAM03885c (the Q5a rename of MAM03652c, whose only reaction MAR20093 was) is in no reaction; it keeps
  its row and its species, as ruling Q5a gave them, and the corrections remove nothing.
- A reaction's equation, gene rule or name (15(R)-HEPE): MAR02560 (c) and MAR02571 (r), written "15(R)-HEPE
  hydrolysis", 15(R)-HEPE + H2O <=> 15(R)-HpEPE + 2 H+, off by +2 in charge, become the one-way glutathione-dependent
  reduction 15(R)-HpEPE + 2 GSH -> 15(R)-HEPE + GSSG + H2O, with the nine glutathione peroxidase genes of MAR00988
  and the name "Glutathione: 15(R)-HpEPE oxidoreductase". The nuclear and peroxisomal copies MAR02567 and MAR02577 are
  left as pinned, flagged for follow-up (the owner, 20 November 2026): those compartments hold no GSSG in the model.

The columns of configs/human_gem_corrections.csv (a CSV under configs/ carries no comment lines, since
tests/test_config_csvs_parse.py reads each with pandas and csv.DictReader alike, so they are explained here):

  kind             "value" (replace one cell of metabolites.tsv), "species_id" (rename a compartment row's species
                   id), "species_name" (replace the model name of a species: the SBML name attribute, which the
                   graph's display_name comes from; metabolites.tsv has no name column), "species_added" (add a
                   compartment row of a metabolite the model has), "reaction_species" (replace one participant of a
                   reaction), "reaction_equation" (replace a reaction's participants and direction),
                   "reaction_gene_rule" (replace its gene rule) or "reaction_name" (replace its name).
  row_id           the species id as the pinned files give it (MAM03323c), compartment letter included, for the
                   species kinds; the reaction id (MAR20093) for the reaction kinds; the new species id for a
                   "species_added" row.
  column           the metabolites.tsv column a "value" row replaces (metChEBIID, metSmiles, ...); "mets" for a
                   "species_id" row, whose metsNoComp follows from the new id; "name" for a "species_name" or
                   "reaction_name" row; "copy_of" for a "species_added" row; the participant's species id for a
                   "reaction_species" row; "equation" or "gene_reaction_rule" for those kinds.
  pinned_value     what the pinned file holds there. A correction applies only while the file still holds it: a row
                   that holds something else raises, so a move of the pin cannot pass a stale correction silently.
                   An empty cell is written empty. For "species_added" it is empty, the pinned files having no such
                   species (one that has it raises); for "reaction_species" it is the participant's species id. An
                   equation is written as Human-GEM's yml writes one, "MAM00373c + MAM02040c <=> MAM00375c + 2
                   MAM02039c", and compared as participants, coefficients and direction ("<=>" reversible, "->" one
                   way, as read from the SBML reversible attribute or the cobra lower bound); a gene rule is compared
                   after its and/or terms are put in one order.
  corrected_value  what replaces it. Empty for a value correction blanks the cell (MAM01511 cholesterol-STAR: giving
                   it cholesterol's CHEBI:16113 would move three HPO cholesterol labels onto it, see the row's note).
                   For "species_added", the pinned species of the same metabolite the new row copies. A
                   "reaction_species" participant must have the same formula and charge as the one it replaces, so
                   the move leaves the reaction's balance as it was. A "->" equation sets the lower flux bound to 0
                   (cobra_0_bound in the SBML) and "<=>" to the default lower bound; the upper bound is kept.
  source_1, source_2  the two independent sources the corrected value rests on (CLAUDE.md, "Manual curation takes more
                   than one source"), each with where and when it was read.
  ruling           the ruling the row carries out.
  note             anything else the row needs read beside it, including a disagreement between sources.

Every species id the table names is a pinned id or an added one, so the kinds apply in this order: value cells and
species names, then the added species (which copy their template as corrected), then the reaction corrections, and
the renames last, which reach every speciesReference, the rewritten ones included. MAR20093's substrate is therefore
written MAM03652c (pinned) -> MAM03885l (added), and the rename of MAM03652c to MAM03885c follows. A reaction takes
either "reaction_species" rows or one "reaction_equation" row, not both.

A correction whose row is not in the table it is applied to is skipped, because tests and partial tables pass through
the same readers; tests/test_human_gem_identifier_guards.py checks that every correction applies to the pinned files.

Readers and what they read through here (20 November 2026):
  metabolites.tsv  graph/build_physiology_graph.py (small-molecule layer), graph/edge_negative_sources.py,
                   experiments/build_neuronal_graph_variant.py, experiments/build_node_descriptors.py,
                   experiments/build_plasma_binder_variant.py, experiments/check_laboratory_label_coverage.py,
                   experiments/check_linear_response_signs.py, experiments/fetch_chembl_edge_activities.py and
                   experiments/map_brenda_regulation_to_graph.py, through read_human_gem_metabolites. The metChEBIID
                   readers (evidence/laboratory_abnormality_labels.human_gem_metabolites_by_chebi and
                   graph/chembl_activity_negatives.chebi_of_base) split a cell on ";".
  SBML text        experiments/build_neuronal_graph_variant.py and experiments/build_node_descriptors.py through
                   read_human_gem_sbml_text (charges, EC classes per reaction, Human-GEM participants of the Reactome
                   import).
  cobra model      graph/build_physiology_graph.py through correct_cobra_model (node ids, display names,
                   base_metabolite_id, reaction participants, stoichiometry, reversibility and gene rules), and the
                   reaction-level reads of experiments/audit_physiology.py (mass and charge balance),
                   experiments/measure_blocked_reactions.py and perturbation/flux_sampling_perturbation_features.py
                   through read_human_gem_cobra_model.
Not routed through here, because no correction changes what they read: reactions.tsv (read by no code; it holds
cross-references by reaction id, and no reaction id changes), the EC numbers graph/go_not_annotations.py reads from the
SBML's reaction annotations (no correction changes an EC number), and the yml, read for reaction subsystems
(build_physiology_graph.subsystem_by_reaction) and reaction references (experiments/fetch_record_identifier_crosswalk.py),
both by reaction id. The SBML's own identifiers.org annotations are left as pinned: no reader takes an identifier from
them.
"""
from __future__ import annotations

import csv
import html
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import pandas as pd

DEFAULT_CORRECTIONS_PATH = Path(__file__).resolve().parents[2] / "configs" / "human_gem_corrections.csv"
CORRECTION_COLUMNS = ["kind", "row_id", "column", "pinned_value", "corrected_value", "source_1", "source_2", "ruling", "note"]
CORRECTION_KINDS = ("value", "species_id", "species_name", "species_added", "reaction_species", "reaction_equation",
                    "reaction_gene_rule", "reaction_name")
REACTION_KINDS = ("reaction_species", "reaction_equation", "reaction_gene_rule", "reaction_name")
# metabolites.tsv's identity columns: changed only by a species_id row, never by a value row
SPECIES_ID_COLUMNS = ("mets", "metsNoComp")
# metabolites.tsv's cells that name one compartment row of an earlier model (m01797c, m01797s): left empty on an added row
COMPARTMENT_ROW_COLUMNS = ("metHMR2ID", "metRetired")
SPECIES_ID_PATTERN = re.compile(r"MAM\d+[a-z]")
REACTION_ID_PATTERN = re.compile(r"MAR\d+")
GENE_RULE_TOKEN = re.compile(r"\(|\)|[^\s()]+")
DEFAULT_LOWER_BOUND_PARAMETER, ZERO_BOUND_PARAMETER = "cobra_default_lb", "cobra_0_bound"


def base_metabolite_id(species_id: str) -> str:
    """The id without its compartment letter, as build_physiology_graph.build_metabolic_layer derives base_metabolite_id."""
    return species_id[:-1] if species_id and species_id[-1].isalpha() else species_id


def parse_equation(text: str) -> tuple[dict[str, float], bool]:
    """({species id: signed coefficient, negative for a substrate}, reversible) from "A + 2 B <=> C" or "A -> C"."""
    for arrow, reversible in ((" <=> ", True), (" -> ", False)):
        if arrow in f" {text.strip()} ":
            left, right = f" {text.strip()} ".split(arrow, 1)
            break
    else:
        raise ValueError(f"equation {text!r} has neither ' <=> ' nor ' -> '")
    stoichiometry: dict[str, float] = {}
    for side, sign in ((left, -1.0), (right, 1.0)):
        for term in (part.strip() for part in side.split(" + ") if part.strip()):
            pieces = term.split()
            amount, species = (float(pieces[0]), pieces[1]) if len(pieces) == 2 else (1.0, pieces[0]) if len(pieces) == 1 else (None, term)
            if amount is None or amount <= 0 or not SPECIES_ID_PATTERN.fullmatch(species) or species in stoichiometry:
                raise ValueError(f"equation {text!r}: term {term!r} is not a positive coefficient and a species id used once")
            stoichiometry[species] = sign * amount
    return stoichiometry, reversible


def parse_gene_rule(text: str):
    """A gene rule ("A or (B and C)") as a tree: a gene id, or ("and" | "or", (children...)); None for an empty rule."""
    tokens = GENE_RULE_TOKEN.findall(text or "")
    if not tokens:
        return None
    position = 0

    def expression(operator: str):
        nonlocal position
        children = [factor() if operator == "and" else expression("and")]
        while position < len(tokens) and tokens[position] == operator:
            position += 1
            children.append(factor() if operator == "and" else expression("and"))
        return children[0] if len(children) == 1 else (operator, tuple(children))

    def factor():
        nonlocal position
        if position >= len(tokens) or tokens[position] in (")", "and", "or"):
            raise ValueError(f"gene rule {text!r} is malformed")
        token = tokens[position]
        position += 1
        if token != "(":
            return token
        inner = expression("or")
        if position >= len(tokens) or tokens[position] != ")":
            raise ValueError(f"gene rule {text!r} has an unclosed parenthesis")
        position += 1
        return inner

    tree = expression("or")
    if position != len(tokens):
        raise ValueError(f"gene rule {text!r} is malformed")
    return tree


def canonical_gene_rule(tree) -> str:
    """One text per rule, whatever the order of its terms, so a pinned rule compares equal however it is written."""
    if tree is None:
        return ""
    if isinstance(tree, str):
        return tree
    operator, children = tree
    flat = []
    for child in children:
        flat.extend(child[1] if isinstance(child, tuple) and child[0] == operator else (child,))
    return "(" + f" {operator} ".join(sorted(canonical_gene_rule(child) for child in flat)) + ")"


@dataclass(frozen=True)
class HumanGemCorrections:
    """The table, split by kind. values: (pinned species id, column, pinned value, corrected value);
    species_ids: pinned species id -> corrected species id; species_names: pinned species id -> (pinned name, corrected
    name); species_added: new species id -> the pinned species it copies; reaction_species: reaction id -> {pinned
    participant: new participant}; reaction_equations, reaction_gene_rules, reaction_names: reaction id -> (pinned,
    corrected)."""
    values: tuple[tuple[str, str, str, str], ...] = ()
    species_ids: dict[str, str] = field(default_factory=dict)
    species_names: dict[str, tuple[str, str]] = field(default_factory=dict)
    species_added: dict[str, str] = field(default_factory=dict)
    reaction_species: dict[str, dict[str, str]] = field(default_factory=dict)
    reaction_equations: dict[str, tuple[str, str]] = field(default_factory=dict)
    reaction_gene_rules: dict[str, tuple[str, str]] = field(default_factory=dict)
    reaction_names: dict[str, tuple[str, str]] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return not (self.values or self.species_ids or self.species_names or self.species_added or self.reaction_species
                    or self.reaction_equations or self.reaction_gene_rules or self.reaction_names)

    def corrected_reactions(self) -> set[str]:
        return set(self.reaction_species) | set(self.reaction_equations) | set(self.reaction_gene_rules) | set(self.reaction_names)


NO_CORRECTIONS = HumanGemCorrections()


def parse_corrections(rows: list[dict[str, str]]) -> HumanGemCorrections:
    """Check and split the rows of the table; a malformed row raises ValueError naming it."""
    values: list[tuple[str, str, str, str]] = []
    species_ids: dict[str, str] = {}
    species_names: dict[str, tuple[str, str]] = {}
    species_added: dict[str, str] = {}
    reaction_species: dict[str, dict[str, str]] = {}
    reaction_cells: dict[str, dict[str, tuple[str, str]]] = {kind: {} for kind in ("reaction_equation", "reaction_gene_rule", "reaction_name")}
    seen_cells: set[tuple[str, str]] = set()
    for number, row in enumerate(rows, start=2):
        kind, row_id, column = ((row.get(key) or "").strip() for key in ("kind", "row_id", "column"))
        pinned, corrected = (row.get("pinned_value") or "").strip(), (row.get("corrected_value") or "").strip()
        where = f"configs/human_gem_corrections.csv line {number} ({row_id} {column})"
        if kind not in CORRECTION_KINDS:
            raise ValueError(f"{where}: kind {kind!r} is not one of {CORRECTION_KINDS}")
        if kind in REACTION_KINDS:
            if not REACTION_ID_PATTERN.fullmatch(row_id):
                raise ValueError(f"{where}: row_id of a {kind} row must be a reaction id, such as MAR20093")
        elif not SPECIES_ID_PATTERN.fullmatch(row_id):
            raise ValueError(f"{where}: row_id must be a species id with its compartment letter, such as MAM03323c")
        if (row_id, column) in seen_cells:
            raise ValueError(f"{where}: a second correction of the same cell")
        seen_cells.add((row_id, column))
        if pinned == corrected:
            raise ValueError(f"{where}: the corrected value equals the pinned one")
        if kind == "value":
            if column in SPECIES_ID_COLUMNS or column == "name" or not column:
                raise ValueError(f"{where}: a value row corrects a cell other than the species id; ids change through species_id rows, names through species_name rows")
            values.append((row_id, column, pinned, corrected))
        elif kind == "species_id":
            if column != "mets" or pinned != row_id:
                raise ValueError(f"{where}: a species_id row has column mets and pinned_value equal to its row_id")
            if not SPECIES_ID_PATTERN.fullmatch(corrected) or corrected[-1] != row_id[-1]:
                raise ValueError(f"{where}: the new species id {corrected!r} must be a MAM id in the same compartment")
            species_ids[row_id] = corrected
        elif kind == "species_name":
            if column != "name" or not corrected:
                raise ValueError(f"{where}: a species_name row has column name and a non-empty corrected name")
            species_names[row_id] = (pinned, corrected)
        elif kind == "species_added":
            if column != "copy_of" or pinned:
                raise ValueError(f"{where}: a species_added row has column copy_of and an empty pinned_value")
            if not SPECIES_ID_PATTERN.fullmatch(corrected) or base_metabolite_id(corrected) != base_metabolite_id(row_id) or corrected[-1] == row_id[-1]:
                raise ValueError(f"{where}: an added species copies a species of the same metabolite in another compartment, not {corrected!r}")
            species_added[row_id] = corrected
        elif kind == "reaction_species":
            if not SPECIES_ID_PATTERN.fullmatch(column) or pinned != column or not SPECIES_ID_PATTERN.fullmatch(corrected):
                raise ValueError(f"{where}: a reaction_species row names the pinned participant as column and pinned_value, and a species id as corrected_value")
            reaction_species.setdefault(row_id, {})[column] = corrected
        else:
            expected = {"reaction_equation": "equation", "reaction_gene_rule": "gene_reaction_rule", "reaction_name": "name"}[kind]
            if column != expected:
                raise ValueError(f"{where}: a {kind} row has column {expected}")
            if kind == "reaction_equation":
                parse_equation(pinned), parse_equation(corrected)
            elif kind == "reaction_gene_rule":
                parse_gene_rule(pinned), parse_gene_rule(corrected)
            elif not corrected:
                raise ValueError(f"{where}: a reaction_name row has a non-empty corrected name")
            reaction_cells[kind][row_id] = (pinned, corrected)
    targets = list(species_ids.values())
    if len(set(targets)) != len(targets):
        raise ValueError("configs/human_gem_corrections.csv: two species renamed to the same id")
    if set(targets) & set(species_ids):
        raise ValueError("configs/human_gem_corrections.csv: a rename's new id is itself renamed")
    if set(species_added) & (set(targets) | set(species_ids)):
        raise ValueError("configs/human_gem_corrections.csv: an added species is also a rename's old or new id")
    if both := sorted(set(reaction_species) & set(reaction_cells["reaction_equation"])):
        raise ValueError(f"configs/human_gem_corrections.csv: {both} take both reaction_species rows and a reaction_equation row")
    for reaction, moves in reaction_species.items():
        if len(set(moves.values())) != len(moves) or set(moves.values()) & set(moves):
            raise ValueError(f"configs/human_gem_corrections.csv: the participants of {reaction} would merge")
    return HumanGemCorrections(tuple(values), species_ids, species_names, species_added, reaction_species,
                               reaction_cells["reaction_equation"], reaction_cells["reaction_gene_rule"], reaction_cells["reaction_name"])


@lru_cache(maxsize=4)
def read_human_gem_corrections(path: Path | None = DEFAULT_CORRECTIONS_PATH) -> HumanGemCorrections:
    """The corrections table at path; None, or a path that is not a file, gives no corrections (the pinned model as is)."""
    if path is None or not Path(path).is_file():
        return NO_CORRECTIONS
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CORRECTION_COLUMNS:
            raise ValueError(f"{path}: columns {reader.fieldnames}, expected {CORRECTION_COLUMNS}")
        return parse_corrections(list(reader))


def _cell_text(value) -> str:
    return "" if value is None or (not isinstance(value, str) and pd.isna(value)) else str(value).strip()


def correct_metabolites_table(table: pd.DataFrame, corrections: HumanGemCorrections, empty_cell=float("nan")) -> pd.DataFrame:
    """metabolites.tsv with the corrections applied: value cells first (keyed on the pinned ids), then the added
    species (each a copy of its template's corrected row, placed after it), then the species renames, which set mets and
    metsNoComp. A blanked cell takes empty_cell, which is to be the reader's own empty cell (NaN by default, "" for a
    table read with keep_default_na=False), so the result equals reading a corrected file. The reaction kinds have no
    cell here."""
    if corrections.is_empty() or "mets" not in table.columns:
        return table
    table = table.copy()
    row_of = {species: index for index, species in zip(table.index, table["mets"].astype(str))}
    for row_id, column, pinned, corrected in corrections.values:
        if row_id not in row_of:
            continue
        if column not in table.columns:
            raise ValueError(f"Human-GEM correction of {row_id}: the table has no column {column}")
        held = _cell_text(table.at[row_of[row_id], column])
        if held != pinned:
            raise ValueError(f"Human-GEM correction of {row_id} {column}: the table holds {held!r}, the correction was written against "
                             f"{pinned!r}; re-check the row against the model now read before applying it")
        if table[column].dtype != object:
            table[column] = table[column].astype(object)
        table.at[row_of[row_id], column] = corrected if corrected else empty_cell
    added_after: dict[object, list[pd.Series]] = {}
    for new, template in corrections.species_added.items():
        if new in row_of:
            raise ValueError(f"Human-GEM added species {new}: the table already holds it; re-check the row against the model now read")
        if template not in row_of:
            continue
        added = table.loc[row_of[template]].copy()
        added["mets"] = new
        if "metsNoComp" in added.index:
            added["metsNoComp"] = base_metabolite_id(new)
        for column in COMPARTMENT_ROW_COLUMNS:
            if column in added.index:
                added[column] = empty_cell
        added_after.setdefault(row_of[template], []).append(added)
    if added_after:
        dtypes, pieces, start = table.dtypes.to_dict(), [], 0
        for position, index in enumerate(table.index):
            if index in added_after:
                pieces += [table.iloc[start:position + 1], pd.DataFrame(added_after[index], columns=table.columns)]
                start = position + 1
        table = pd.concat(pieces + [table.iloc[start:]], ignore_index=True).astype(dtypes)
        row_of = {species: index for index, species in zip(table.index, table["mets"].astype(str))}
    present = set(row_of)
    for old, new in corrections.species_ids.items():
        if old not in present:
            continue
        if new in present:
            raise ValueError(f"Human-GEM rename {old} -> {new}: the table already holds {new}")
        index = row_of[old]
        table.at[index, "mets"] = new
        if "metsNoComp" in table.columns:
            table.at[index, "metsNoComp"] = base_metabolite_id(new)
    return table


def read_human_gem_metabolites(path: Path, corrections_path: Path | None = DEFAULT_CORRECTIONS_PATH, usecols: list[str] | None = None,
                               **read_csv_arguments) -> pd.DataFrame:
    """metabolites.tsv with configs/human_gem_corrections.csv applied. The whole table is read and corrected before
    usecols selects, since a correction is keyed on the mets column. corrections_path=None reads the pinned table as is."""
    table = pd.read_csv(path, sep="\t", **read_csv_arguments)
    empty_cell = "" if read_csv_arguments.get("keep_default_na", True) is False else float("nan")
    table = correct_metabolites_table(table, read_human_gem_corrections(corrections_path), empty_cell)
    return table[list(usecols)] if usecols is not None else table


# The SBML text.

def _species_element(sbml_text: str, species: str) -> re.Match | None:
    return re.search(rf'<species [^>]*\bid="M_{re.escape(species)}"[^>]*?(?:/>|>.*?</species>)', sbml_text, re.DOTALL)


def _attribute(tag: str, name: str) -> str | None:
    found = re.search(rf'(?<![\w:]){re.escape(name)}="([^"]*)"', tag)
    return html.unescape(found.group(1)) if found else None


def _set_attribute(tag: str, name: str, value: str) -> str:
    pattern = re.compile(rf'(?<![\w:]){re.escape(name)}="[^"]*"')
    replacement = f"{name}={quoteattr(value)}"
    return pattern.sub(lambda _: replacement, tag, count=1) if pattern.search(tag) else tag.replace(">", f" {replacement}>", 1)


def _species_formula_and_charge(sbml_text: str, species: str) -> tuple[str | None, str | None] | None:
    element = _species_element(sbml_text, species)
    if element is None:
        return None
    opening = re.match(r"<species [^>]*>", element.group(0)).group(0)
    return _attribute(opening, "fbc:chemicalFormula"), _attribute(opening, "fbc:charge")


def _reaction_element(sbml_text: str, reaction: str) -> re.Match | None:
    return re.search(rf'<reaction [^>]*\bid="R_{re.escape(reaction)}"[^>]*>.*?</reaction>', sbml_text, re.DOTALL)


def _sbml_equation(block: str) -> tuple[dict[str, float], bool]:
    stoichiometry: dict[str, float] = {}
    for list_name, sign in (("listOfReactants", -1.0), ("listOfProducts", 1.0)):
        part = re.search(rf"<{list_name}>(.*?)</{list_name}>", block, re.DOTALL)
        for species, amount in re.findall(r'<speciesReference species="M_([^"]+)" stoichiometry="([^"]+)"', part.group(1) if part else ""):
            stoichiometry[species] = stoichiometry.get(species, 0.0) + sign * float(amount)
    opening = re.match(r"<reaction [^>]*>", block).group(0)
    return stoichiometry, _attribute(opening, "reversible") == "true"


def _sbml_gene_rule(block: str):
    """The reaction's fbc:geneProductAssociation as a tree of parse_gene_rule's form; None when it has none."""
    association = re.search(r"<fbc:geneProductAssociation>(.*?)</fbc:geneProductAssociation>", block, re.DOTALL)
    if association is None:
        return None
    stack: list[list] = [[]]
    operators: list[str] = []
    for match in re.finditer(r'<fbc:(or|and)>|</fbc:(or|and)>|<fbc:geneProductRef fbc:geneProduct="G_([^"]+)"\s*/>', association.group(1)):
        if match.group(1):
            operators.append(match.group(1))
            stack.append([])
        elif match.group(2):
            children = stack.pop()
            stack[-1].append((operators.pop(), tuple(children)))
        else:
            stack[-1].append(match.group(3))
    return stack[0][0] if stack[0] else None


def _genes_of(tree) -> list[str]:
    if tree is None:
        return []
    return [tree] if isinstance(tree, str) else [gene for child in tree[1] for gene in _genes_of(child)]


def _fbc_association(tree, indent: str) -> str:
    def element(node, depth: int) -> list[str]:
        pad = indent + "  " * (depth + 1)
        if isinstance(node, str):
            return [f'{pad}<fbc:geneProductRef fbc:geneProduct="G_{node}"/>']
        operator, children = node
        return [f"{pad}<fbc:{operator}>"] + [line for child in children for line in element(child, depth + 1)] + [f"{pad}</fbc:{operator}>"]

    return "\n".join([f"{indent}<fbc:geneProductAssociation>"] + element(tree, 0) + [f"{indent}</fbc:geneProductAssociation>"])


def _species_lists(stoichiometry: dict[str, float], indent: str) -> str:
    lines = []
    for list_name, wanted in (("listOfReactants", lambda amount: amount < 0), ("listOfProducts", lambda amount: amount > 0)):
        references = [f'{indent}  <speciesReference species="M_{species}" stoichiometry="{abs(amount):g}" constant="true"/>'
                      for species, amount in stoichiometry.items() if wanted(amount)]
        if references:
            lines += [f"{indent}<{list_name}>"] + references + [f"{indent}</{list_name}>"]
    return "\n".join(lines)


def _correct_sbml_reaction(block: str, reaction: str, corrections: HumanGemCorrections, sbml_text: str) -> str:
    opening = re.match(r"<reaction [^>]*>", block).group(0)
    indent = re.search(r"\n(\s*)<(?:notes|annotation|listOf|fbc:geneProductAssociation)", block)
    indent = indent.group(1) if indent else "        "
    if reaction in corrections.reaction_names:
        pinned_name, corrected_name = corrections.reaction_names[reaction]
        if (_attribute(opening, "name") or "") != pinned_name:
            raise ValueError(f"Human-GEM name correction of {reaction}: the SBML names it {_attribute(opening, 'name')!r}, the correction was written against {pinned_name!r}")
        opening = _set_attribute(opening, "name", corrected_name)
    if reaction in corrections.reaction_species:
        for old, new in corrections.reaction_species[reaction].items():
            reference = f'<speciesReference species="M_{old}"'
            if block.count(reference) != 1:
                raise ValueError(f"Human-GEM correction of {reaction}: the SBML reaction has {old} {block.count(reference)} times, the correction was written against once")
            if (properties := _species_formula_and_charge(sbml_text, new)) is None:
                raise ValueError(f"Human-GEM correction of {reaction}: the SBML has no species {new}")
            if properties != _species_formula_and_charge(sbml_text, old):
                raise ValueError(f"Human-GEM correction of {reaction}: {new} differs from {old} in formula or charge")
            block = block.replace(reference, f'<speciesReference species="M_{new}"')
    if reaction in corrections.reaction_equations:
        pinned, corrected = (parse_equation(text) for text in corrections.reaction_equations[reaction])
        if _sbml_equation(block) != pinned:
            raise ValueError(f"Human-GEM equation correction of {reaction}: the SBML reaction is not {corrections.reaction_equations[reaction][0]!r}, "
                             "the equation the correction was written against")
        if missing := [species for species in corrected[0] if _species_element(sbml_text, species) is None]:
            raise ValueError(f"Human-GEM equation correction of {reaction}: the SBML has no species {missing}")
        lists = list(re.finditer(r"\n\s*<(listOfReactants|listOfProducts)>.*?</\1>", block, re.DOTALL))
        if lists:
            start = lists[0].start()
            for found in reversed(lists):
                block = block[:found.start()] + block[found.end():]
        else:
            anchor = re.search(r"\n\s*<(?:listOfModifiers|fbc:geneProductAssociation)>|\n\s*</reaction>", block)
            start = anchor.start()
        block = block[:start] + "\n" + _species_lists(corrected[0], indent) + block[start:]
        opening = _set_attribute(opening, "reversible", "true" if corrected[1] else "false")
        lower = _attribute(opening, "fbc:lowerFluxBound")
        if not corrected[1]:
            opening = _set_attribute(opening, "fbc:lowerFluxBound", ZERO_BOUND_PARAMETER)
        elif lower in (None, ZERO_BOUND_PARAMETER):
            opening = _set_attribute(opening, "fbc:lowerFluxBound", DEFAULT_LOWER_BOUND_PARAMETER)
    if reaction in corrections.reaction_gene_rules:
        pinned, corrected = (parse_gene_rule(text) for text in corrections.reaction_gene_rules[reaction])
        if canonical_gene_rule(_sbml_gene_rule(block)) != canonical_gene_rule(pinned):
            raise ValueError(f"Human-GEM gene rule correction of {reaction}: the SBML reaction's rule is not {corrections.reaction_gene_rules[reaction][0]!r}, "
                             "the rule the correction was written against")
        if missing := [gene for gene in _genes_of(corrected) if f'fbc:id="G_{gene}"' not in sbml_text]:
            raise ValueError(f"Human-GEM gene rule correction of {reaction}: the SBML has no gene product {missing}")
        block = re.sub(r"\n\s*<fbc:geneProductAssociation>.*?</fbc:geneProductAssociation>", "", block, flags=re.DOTALL)
        if corrected is not None:
            end = block.rindex("</reaction>")
            line_start = block.rfind("\n", 0, end)
            block = block[:line_start] + "\n" + _fbc_association(corrected, indent) + block[line_start:]
    return opening + block[len(re.match(r"<reaction [^>]*>", block).group(0)):]


def correct_sbml_text(sbml_text: str, corrections: HumanGemCorrections) -> str:
    """The Human-GEM SBML with the corrections applied, in the order of the module docstring: the name attribute of
    each named species; each added species, a copy of its template's element (id, metaid, annotation anchor and
    compartment its own) placed after it; each corrected reaction (name, participants, direction and lower flux bound,
    gene association); then for each renamed species its id, its metaid, its annotation anchor and every
    speciesReference to it."""
    if corrections.is_empty():
        return sbml_text
    for species, (pinned_name, corrected_name) in corrections.species_names.items():
        opening = re.search(rf'<species [^>]*\bid="M_{re.escape(species)}"[^>]*>', sbml_text)
        if opening is None:
            continue
        name = re.search(r'\bname=("[^"]*")', opening.group(0))
        held = name.group(1)[1:-1] if name else ""
        if held != escape(pinned_name, {'"': "&quot;"}):
            raise ValueError(f"Human-GEM name correction of {species}: the SBML names it {held!r}, the correction was written against {pinned_name!r}")
        replaced = opening.group(0).replace(name.group(0), f"name={quoteattr(corrected_name)}", 1)
        sbml_text = sbml_text[:opening.start()] + replaced + sbml_text[opening.end():]
    for new, template in corrections.species_added.items():
        if _species_element(sbml_text, new) is not None:
            raise ValueError(f"Human-GEM added species {new}: the SBML already holds species M_{new}; re-check it against the model now read")
        element = _species_element(sbml_text, template)
        if element is None:
            continue
        if f'<compartment id="{new[-1]}"' not in sbml_text:
            raise ValueError(f"Human-GEM added species {new}: the SBML has no compartment {new[-1]}")
        copy = element.group(0)
        for attribute_form in ('id="M_{}"', 'metaid="meta_M_{}"', 'rdf:about="#meta_M_{}"'):
            copy = copy.replace(attribute_form.format(template), attribute_form.format(new))
        opening = re.match(r"<species [^>]*>", copy).group(0)
        copy = _set_attribute(opening, "compartment", new[-1]) + copy[len(opening):]
        line_start = sbml_text.rfind("\n", 0, element.start())
        sbml_text = sbml_text[:element.end()] + sbml_text[line_start:element.start()] + copy + sbml_text[element.end():]
    for reaction in sorted(corrections.corrected_reactions()):
        element = _reaction_element(sbml_text, reaction)
        if element is None:
            continue
        sbml_text = sbml_text[:element.start()] + _correct_sbml_reaction(element.group(0), reaction, corrections, sbml_text) + sbml_text[element.end():]
    for old, new in corrections.species_ids.items():
        if f'"M_{old}"' not in sbml_text:
            continue
        if re.search(rf'id="M_{re.escape(new)}"', sbml_text):
            raise ValueError(f"Human-GEM rename {old} -> {new}: the SBML already holds species M_{new}")
        for attribute_form in ('id="M_{}"', 'metaid="meta_M_{}"', 'rdf:about="#meta_M_{}"', 'species="M_{}"'):
            sbml_text = sbml_text.replace(attribute_form.format(old), attribute_form.format(new))
    return sbml_text


def read_human_gem_sbml_text(path: Path, corrections_path: Path | None = DEFAULT_CORRECTIONS_PATH) -> str:
    """The Human-GEM SBML file's text with configs/human_gem_corrections.csv's species and reaction corrections applied."""
    return correct_sbml_text(Path(path).read_text(), read_human_gem_corrections(corrections_path))


# The cobra model.

def _correct_cobra_reaction(model, reaction, corrections: HumanGemCorrections) -> None:
    identifier = reaction.id
    if identifier in corrections.reaction_names:
        pinned_name, corrected_name = corrections.reaction_names[identifier]
        if reaction.name != pinned_name:
            raise ValueError(f"Human-GEM name correction of {identifier}: the model names it {reaction.name!r}, the correction was written against {pinned_name!r}")
        reaction.name = corrected_name
    if identifier in corrections.reaction_species:
        held = {metabolite.id: (metabolite, amount) for metabolite, amount in reaction.metabolites.items()}
        for old, new in corrections.reaction_species[identifier].items():
            if old not in held:
                raise ValueError(f"Human-GEM correction of {identifier}: the model reaction has no participant {old}")
            if new not in model.metabolites:
                raise ValueError(f"Human-GEM correction of {identifier}: the model has no species {new}")
            replacement, (metabolite, amount) = model.metabolites.get_by_id(new), held[old]
            if (replacement.formula, replacement.charge) != (metabolite.formula, metabolite.charge):
                raise ValueError(f"Human-GEM correction of {identifier}: {new} differs from {old} in formula or charge")
            reaction.subtract_metabolites({metabolite: amount})
            reaction.add_metabolites({replacement: amount})
    if identifier in corrections.reaction_equations:
        pinned, corrected = (parse_equation(text) for text in corrections.reaction_equations[identifier])
        held = ({metabolite.id: float(amount) for metabolite, amount in reaction.metabolites.items()}, reaction.lower_bound < 0)
        if held != pinned:
            raise ValueError(f"Human-GEM equation correction of {identifier}: the model reaction is not {corrections.reaction_equations[identifier][0]!r}, "
                             "the equation the correction was written against")
        if missing := [species for species in corrected[0] if species not in model.metabolites]:
            raise ValueError(f"Human-GEM equation correction of {identifier}: the model has no species {missing}")
        reaction.subtract_metabolites(dict(reaction.metabolites))
        reaction.add_metabolites({model.metabolites.get_by_id(species): amount for species, amount in corrected[0].items()})
        if not corrected[1]:
            reaction.lower_bound = 0.0
        elif reaction.lower_bound >= 0:
            reaction.lower_bound = -abs(reaction.upper_bound)
    if identifier in corrections.reaction_gene_rules:
        pinned, corrected = corrections.reaction_gene_rules[identifier]
        if canonical_gene_rule(parse_gene_rule(reaction.gene_reaction_rule)) != canonical_gene_rule(parse_gene_rule(pinned)):
            raise ValueError(f"Human-GEM gene rule correction of {identifier}: the model's rule is {reaction.gene_reaction_rule!r}, the correction was written against {pinned!r}")
        reaction.gene_reaction_rule = corrected


def correct_cobra_model(model, corrections: HumanGemCorrections):
    """A cobra model of Human-GEM with the corrections applied in place (and returned), in the order of the module
    docstring: species names, added species (copies of their template in their own compartment), reaction corrections,
    then renames. The reactions hold the metabolite objects, so the stoichiometry follows the rename."""
    if corrections.is_empty():
        return model
    import cobra

    present = {metabolite.id for metabolite in model.metabolites}
    for species, (pinned_name, corrected_name) in corrections.species_names.items():
        if species not in present:
            continue
        metabolite = model.metabolites.get_by_id(species)
        if metabolite.name != pinned_name:
            raise ValueError(f"Human-GEM name correction of {species}: the model names it {metabolite.name!r}, the correction was written against {pinned_name!r}")
        metabolite.name = corrected_name
    for new, template in corrections.species_added.items():
        if new in present:
            raise ValueError(f"Human-GEM added species {new}: the model already holds it; re-check it against the model now read")
        if template not in present:
            continue
        if model.compartments and new[-1] not in model.compartments:
            raise ValueError(f"Human-GEM added species {new}: the model has no compartment {new[-1]}")
        source = model.metabolites.get_by_id(template)
        added = cobra.Metabolite(new, formula=source.formula, name=source.name, compartment=new[-1], charge=source.charge)
        added.notes, added.annotation = dict(source.notes), dict(source.annotation)
        model.add_metabolites([added])
        present.add(new)
    for identifier in sorted(corrections.corrected_reactions()):
        if identifier in model.reactions:
            _correct_cobra_reaction(model, model.reactions.get_by_id(identifier), corrections)
    for old, new in corrections.species_ids.items():
        if old not in present:
            continue
        if new in present:
            raise ValueError(f"Human-GEM rename {old} -> {new}: the model already holds {new}")
        model.metabolites.get_by_id(old).id = new
    model.repair()
    return model


def read_human_gem_cobra_model(path: Path, corrections_path: Path | None = DEFAULT_CORRECTIONS_PATH):
    """The cobra model read from the Human-GEM SBML (or any format cobra.io.load_model reads, for a path that is not
    .xml) with configs/human_gem_corrections.csv applied; corrections_path=None gives the model as the file holds it."""
    from cobra.io import load_model, read_sbml_model

    model = read_sbml_model(str(path)) if Path(path).suffix.lower() == ".xml" else load_model(str(path))
    return correct_cobra_model(model, read_human_gem_corrections(corrections_path))


def corrections_without_their_row(table: pd.DataFrame, sbml_text: str | None, corrections: HumanGemCorrections) -> list[str]:
    """Each correction that the pinned table (or, for a species name or a reaction, the SBML) has no row for, so would
    be skipped. An added species whose template is absent counts, as does one the pinned files already hold."""
    present = set(table["mets"].astype(str))
    missing = [f"{kind} {row_id}" for kind, row_id in
               [("value", row_id) for row_id, *_ in corrections.values] + [("species_id", row_id) for row_id in corrections.species_ids]
               if row_id not in present]
    missing += [f"species_added {new}" for new, template in corrections.species_added.items() if template not in present or new in present]
    if sbml_text is not None:
        missing += [f"species_name {species}" for species in corrections.species_names if f'id="M_{species}"' not in sbml_text]
        missing += [f"reaction {reaction}" for reaction in sorted(corrections.corrected_reactions()) if f'id="R_{reaction}"' not in sbml_text]
    return missing
