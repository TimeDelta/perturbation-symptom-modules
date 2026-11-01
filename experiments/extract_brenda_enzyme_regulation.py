"""Pull BRENDA's enzyme-regulation records for human proteins into one table.

Decision 9.14 and docs/missing_physiology_review.md section 2: the graph can receive a metabolite response but
almost cannot act on one, 600 of 266,966 edges running metabolite to protein and 4 `inhibits` in the whole graph.
BRENDA's inhibitor, activating-compound, Ki, IC50, cofactor and metals/ions fields are that missing layer.

Sign convention matches the graph: an inhibitor arrives at -1, an activating compound at +1, and a cofactor or a
metal ion carries no sign because `cofactor_of` is unsigned.

A note of no inhibition is not an inhibition (decision 9.88, 22 October 2026). BRENDA lists under "inhibitor" every
compound a paper tested for inhibition, and the comment says when it did not inhibit: on the EC 2.7.1.1 page (read 22
October 2026 with experiments/read_public_page.py) 41 of the 396 inhibitor rows carry a note of no inhibition or no
effect by the classifier below, such as "not inhibited by D-glucose 6-phosphate" or "no inhibition of V62L, V62M,
V62Q, V62F, V62K". 40 of them are rows of other organisms, and one is among the 89 human rows: glucokinase mutants,
beside "wild type enzyme ... significantly inhibited". Until this decision every such entry of a human protein became
an `inhibits` row.

The extraction already leaves out the protein entries of other organisms, so a record reaches a row only through the
human entries it names. BRENDA's text release writes a record's comment as one note per group of protein entries,
"#1,4# note <12>; #5# note <13>", and notes_by_protein reads the notes of each human entry apart from the others'; a
comment without the markers is read as one note on every protein of the record. The JSON release was not on the
machine of 22 October 2026 to check which form it carries, so the parser takes either, and the summary counts the
comments of each form. The run of 26 October 2026 on release 2026.1 answered it: no comment of an inhibition field
entry in the JSON carries the markers, so on the JSON every comment is one note on every protein of its record, and
the per-protein reading matters only for the text release. Each note is split into clauses and each clause classed
(classify_clause):

  a clause stating no inhibition or no effect (NO_INHIBITION_OR_EFFECT), about this enzyme;
  the same, scoped to another organism, an isozyme or another form of the enzyme, a mutant or another compound
  (scope_elsewhere): it says nothing about the human wild-type enzyme in either direction;
  a clause stating inhibition (STATES_INHIBITION) or any other clause.

For an entry of the inhibitor, Ki or IC50 field on a human protein (relation_of_notes): no clause of absence leaves
the `inhibits` row as before; a clause of absence about this enzyme with no clause stating inhibition of it makes a
`no_inhibition` row, a negative observation that experiments/map_brenda_regulation_to_graph.py writes to its own table
and never to the edges; a clause of absence about another organism, isozyme, mutant or compound alone makes no row;
and a clause stating inhibition of this enzyme beside a clause of absence keeps the `inhibits` row (concentration
dependence: "no inhibition at 1 mM, 50% inhibition at 10 mM"). The cofactor and metal fields are written as before.

An entry of the activating-compound field (relation_of_activator_notes, the owner's rulings of 1 November 2026 in
decision 9.88) is written as `activates`, as before, unless a note denies an effect on this human enzyme and no clause
states activation, when it becomes a `no_activation` negative that the mapping keeps out of the edges. The absence
pattern is not widened ("Don't widen then"), and the rule is the conservative one ("That's a defensible rule. Use it
for now"). Until 1 November 2026 every activating-compound entry was written as `activates` whatever its note said, and
the summary only counted the notes stating no effect. On release 2026.1 the rule turns two of the 47 such notes into
negatives, pyrazole on EC 1.1.1.284 and Ca2+/calmodulin on EC 2.7.1.23, and leaves the rest as they were, which matches
the Fable reading of all 47 in docs/brenda_activator_note_classification_2026-11-01.md.
"""
import argparse
import collections
import csv
import gzip
import json
import re
from pathlib import Path

import ijson

REGULATION_FIELDS_AND_RELATIONS = {
    "inhibitor": ("inhibits", -1.0),
    "ki_value": ("inhibits", -1.0),
    "ic50_value": ("inhibits", -1.0),
    "activating_compound": ("activates", 1.0),
    "cofactor": ("cofactor_of", 0.0),
    "metals_ions": ("cofactor_of", 0.0),
}
INHIBITION_FIELDS = ("inhibitor", "ki_value", "ic50_value")
NO_INHIBITION_RELATION = "no_inhibition"
NO_ACTIVATION_RELATION = "no_activation"
UNIPROT_ACCESSION_PATTERN = re.compile(r"\b([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})\b")

# --- the notes of a record ---------------------------------------------------------------------------------------
PROTEIN_MARKER = re.compile(r"#(\d+(?:\s*,\s*\d+)*)#")
REFERENCE_MARKER = re.compile(r"\s*<\d+(?:\s*,\s*\d+)*>")
# Clause boundaries: a semicolon; a full stop before the next sentence, unless it ends an abbreviated genus ("E. coli");
# a comma before a negation or before a percentage, so "no inhibition at 1 mM, 50% inhibition at 10 mM" is two clauses.
CLAUSE_BOUNDARY = re.compile(r";\s*|(?<![\s(][A-Z])\.\s+(?=[A-Za-z])|,\s*(?=(?:but\s+|whereas\s+|while\s+)?(?:no|not)\b|\d+(?:\.\d+)?\s*%)", re.I)

# --- the classifying patterns (each audited with its near misses in tests/test_regex_audit.py) ---------------------
# A statement that the compound did not inhibit or had no effect. "no effect on Km" (or Vmax, kcat, affinity) describes
# an inhibitor's kind, not its absence; "no further inhibition" and "not further inhibited" say inhibition is already there.
NO_INHIBITION_OR_EFFECT = re.compile(
    r"\bno\s+(?:(?:significant|detectable|measurable|appreciable|apparent|marked|substantial|product|feedback|inhibitory)\s+){0,2}(?:inhibition|effect)\b"
    r"(?!\s+(?:on|upon)\s+(?:the\s+)?(?:km|k_?m|vmax|v_?max|kcat|k_?cat|affinity|hill|cooperativity|substrate\s+binding|binding|stability|expression)\b)"
    r"|\bnot\s+(?:(?:significantly|markedly|appreciably|detectably|substantially)\s+)?(?:inhibited|affected)\b"
    r"|\b(?:does|do|did)\s*(?:not|n't)\s+(?:(?:significantly|markedly|appreciably)\s+)?(?:inhibit|affect)\b"
    r"|\bfails?\s+to\s+inhibit\b|\bnon-?inhibitory\b|\buninhibited\b|\binsensitive\s+to\b",
    re.I)
# "inhibition is not affected by phosphate" says the inhibition persists; it is not an absence.
INHIBITION_NOT_AFFECTED = re.compile(r"\binhibition\s+(?:is|was|being|remains?)?\s*not\s+(?:significantly\s+)?affected\b", re.I)
STATES_INHIBITION = re.compile(
    r"\binhibit\w*|\b\d+(?:\.\d+)?\s*%\s*(?:inhibition|residual|remaining)|\b(?:un|non-?)?competitive\b|\bmixed[- ]type\b"
    r"|\bdecreases?\b|\breduces?\b|\binactivat\w*|\bblocks?\b|\bsuppress\w*",
    re.I)
ANOTHER_ORGANISM = re.compile(
    r"\b(?:rats?|mice|mouse|murine|bovine|porcine|pigs?|ovine|sheep|canine|dogs?|rabbits?|chickens?|avian|plants?|fungal|fungi|bacterial|parasites?"
    r"|fish|frogs?|amphibian|Drosophila|Arabidopsis|Plasmodium|Trypanosoma|Leishmania)\b",
    re.I)
# An isozyme or another form of the enzyme: the word, a numbered or typed form ("hexokinase II", "type III", "isoform 2"),
# a tissue's or a compartment's enzyme ("enzyme from root", "the liver enzyme", "cytosolic enzyme").
ISOZYME_OR_FORM = re.compile(
    r"\b(?:isozymes?|isoenzymes?|isoforms?|paralogs?|truncated|chimeric|chimeras?)\b"
    r"|\benzymes?\s+(?:\w+\s+){0,3}?from\b"
    r"|\b(?:liver|brain|heart|muscle|kidney|placental?|erythrocyte|lung|intestinal|hepatic|cardiac|renal|cytosolic|mitochondrial|microsomal|soluble"
    r"|non-cytosolic|root|seed|kernel|leaf|sperm)\s+(?:\w+\s+)?enzymes?\b",
    re.I)
# case-sensitive, for the roman numerals; the words that end in "ase" without naming an enzyme are excluded
NUMBERED_FORM = re.compile(r"\b(?:(?!(?:[Ii]n|[Dd]e)creases?\b|[Rr]eleases?\b|[Pp]hases?\b|[Bb]ases?\b|[Cc]ases?\b|[Dd]iseases?\b)[A-Za-z]*ase|[Tt]ype|[Ff]orm|HK|PFK|PK)"
                           r"[\s-]?(?:[IVX]{1,4}|[1-9][A-Z]?)\b")
MUTANT = re.compile(r"\b(?:mutants?|mutated|mutations?|variants?)\b", re.I)
POINT_MUTATION = re.compile(r"\b[ACDEFGHIKLMNPQRSTVWY][1-9]\d{0,3}[ACDEFGHIKLMNPQRSTVWY]\b")  # case-sensitive: V62L, D209A
WILD_TYPE = re.compile(r"\bwild[\s-]?type\b|\bnative\s+enzyme\b", re.I)
# "not inhibited by <name>" names the compound the absence is about; "by 1 mM" or "by the compound" does not
NAMES_A_COMPOUND = re.compile(r"\bby\s+(?!(?:the|this|that|it|its|either|both|excess|high|higher|low|lower|increasing|up)\b)[A-Za-z]", re.I)

# --- the activating-compound field (decision 9.88, the owner's rulings of 1 November 2026) ---------------------------
# The owner ruled on 26 October 2026 that "\"no effect\" should not have an activates edge", and on 1 November 2026,
# after a Fable reading of every activator note the absence pattern catches
# (docs/brenda_activator_note_classification_2026-11-01.md), "Don't widen then" and, of the conservative rule, "That's a
# defensible rule. Use it for now". So the candidates are only the notes NO_INHIBITION_OR_EFFECT already catches, and a
# note becomes a negative only when it denies an effect on this human enzyme and states no activation anywhere.
# Activator notes of no effect are mostly comparisons ("increases activity of the mitochondrial enzyme, no effect on the
# cytosolic enzyme"), and scope_elsewhere does not recognise another substrate, activity or cell line, so the guards
# below lean towards keeping `activates`: each way they can be wrong leaves the edge as it was before the ruling.
# Activation stated anywhere in the note keeps the edge. "Induces" counts: phenobarbital on EC 2.4.1.17 "induces
# activities towards bilirubin" beside its absence for other substrates. The \b keeps "inactivated" out.
STATES_ACTIVATION = re.compile(r"\bactivat\w*|\bstimulat\w*|\benhanc\w*|\bincreas\w*|\binduc\w*|\b\d+(?:\.\d+)?\s*-?\s*fold\b"
                               r"|%\s*activation", re.I)
# The absence must be of an effect: in an activator note "no inhibition" says nothing about activation (phosphate on
# EC 2.7.6.1, "no inhibition up to 75 mM", is an inhibitor observation filed under activating compounds).
EFFECT_ABSENCE = re.compile(r"\beffect\b|\baffect(?:ed|s)?\b|\binsensitive\b", re.I)
# A dose-bounded absence is a point on a dose response, not a denial (spermine on EC 3.1.3.48, "no effect at
# 0.02-0.2 mM", beside a separate record of activation by spermine on the same entry).
DOSE_BOUNDED = re.compile(r"\d\s*(?:mM|uM|µM|nM|pM|M)\b")
# An absence whose subject is a part or a form of the compound compares two forms of it rather than denying that the
# compound acts (lipoylated H-protein on EC 1.4.4.2: "the presence of the lipoyl moiety on H-protein does not affect").
FORM_OF_COMPOUND = re.compile(r"\bpresence of\b|\bmoiety\b|\bdeletion of\b|\btruncat\w*|\bwithout (?:the|its)\b", re.I)

ABSENCE, ABSENCE_ELSEWHERE, INHIBITION, OTHER = "absence", "absence_elsewhere", "inhibition", "other"


def notes_by_protein(comment, protein_indices) -> dict[str, list[str]]:
    """{protein index: its notes} of a record's comment, reference markers removed. BRENDA writes a comment as one note
    per group of protein entries, '#1,4# note <12>; #5# note <13>'; a comment without a marker is one note for every
    protein of the record."""
    text = str(comment or "").strip()
    if not text:
        return {}
    markers = list(PROTEIN_MARKER.finditer(text))
    if not markers:
        note = REFERENCE_MARKER.sub("", text).strip(" ;")
        return {str(index): [note] for index in protein_indices} if note else {}
    notes: dict[str, list[str]] = collections.defaultdict(list)
    for position, marker in enumerate(markers):
        end = markers[position + 1].start() if position + 1 < len(markers) else len(text)
        note = REFERENCE_MARKER.sub("", text[marker.end():end]).strip(" ;")
        if note:
            for index in re.split(r"\s*,\s*", marker.group(1)):
                notes[index].append(note)
    return dict(notes)


def clauses_of(note: str) -> list[str]:
    return [clause.strip(" ,.") for clause in CLAUSE_BOUNDARY.split(note) if clause and clause.strip(" ,.")]


def scope_elsewhere(clause: str, ligand_name: str = "") -> str | None:
    """Why the clause speaks of something other than the human wild-type enzyme and this compound, or None. A clause
    that names the wild type is about it, whatever mutant or isozyme it also names; another organism is never human."""
    if ANOTHER_ORGANISM.search(clause):
        return "another organism"
    if not WILD_TYPE.search(clause):
        if MUTANT.search(clause) or POINT_MUTATION.search(clause):
            return "mutant"
        if ISOZYME_OR_FORM.search(clause) or NUMBERED_FORM.search(clause):
            return "isozyme or another form"
    ligand = ligand_name.strip().lower()
    if ligand and NO_INHIBITION_OR_EFFECT.search(clause) and NAMES_A_COMPOUND.search(clause) and ligand not in clause.lower():
        return "another compound"
    return None


def classify_clause(clause: str, ligand_name: str = "") -> tuple[str, str | None]:
    """(class, scope) of one clause: ABSENCE (no inhibition or no effect, on this enzyme), ABSENCE_ELSEWHERE (the same,
    scoped to another organism, isozyme or form, mutant or compound), INHIBITION (inhibition stated) or OTHER."""
    if NO_INHIBITION_OR_EFFECT.search(clause) and not INHIBITION_NOT_AFFECTED.search(clause):
        scope = scope_elsewhere(clause, ligand_name)
        return (ABSENCE_ELSEWHERE, scope) if scope else (ABSENCE, None)
    if STATES_INHIBITION.search(clause):
        return INHIBITION, scope_elsewhere(clause, ligand_name)
    return OTHER, None


def relation_of_notes(notes: list[str], ligand_name: str = "") -> tuple[str | None, str]:
    """(relation, note class) of an inhibitor, Ki or IC50 entry on one human protein, from that protein's notes:
    ('inhibits', ...) as before, (NO_INHIBITION_RELATION, ...) for a negative observation, or (None, scope) when the
    notes speak of no inhibition elsewhere only and the entry says nothing about the human enzyme."""
    classified = [classify_clause(clause, ligand_name) for note in notes for clause in clauses_of(note)]
    absent_here = any(kind == ABSENCE for kind, _ in classified)
    absent_elsewhere = [scope for kind, scope in classified if kind == ABSENCE_ELSEWHERE]
    if not absent_here and not absent_elsewhere:
        return "inhibits", "no note of absence"
    if any(kind == INHIBITION and scope is None for kind, scope in classified):
        return "inhibits", "inhibition and absence both stated"
    if absent_here:
        return NO_INHIBITION_RELATION, "no inhibition of this enzyme"
    return None, f"no inhibition, {absent_elsewhere[0]}"


def relation_of_activator_notes(notes: list[str], ligand_name: str = "") -> tuple[str, str]:
    """(relation, note class) of an activating-compound entry on one human protein, by the conservative rule the owner
    approved on 1 November 2026 (decision 9.88): (NO_ACTIVATION_RELATION, ...) only when a clause denies an effect on
    this human enzyme, unbounded by a dose and not about a form of the compound, and no clause states activation;
    otherwise ('activates', ...) as before. It never drops a row, so a note the rule cannot read is left as it was."""
    clauses = [clause for note in notes for clause in clauses_of(note)]
    absences = [clause for clause in clauses if NO_INHIBITION_OR_EFFECT.search(clause)]
    if not absences:
        return "activates", "no note of absence"
    if any(STATES_ACTIVATION.search(clause) for clause in clauses):
        return "activates", "activation and absence both stated"
    about_this_enzyme = [clause for clause in absences
                         if EFFECT_ABSENCE.search(clause) and scope_elsewhere(clause, ligand_name) is None
                         and not DOSE_BOUNDED.search(clause) and not FORM_OF_COMPOUND.search(clause)]
    if about_this_enzyme:
        return NO_ACTIVATION_RELATION, "no effect on this enzyme, no activation stated"
    return "activates", "absence not unambiguously about this enzyme, kept"


def human_accessions_of_protein_entry(protein_entry: dict) -> list[str]:
    """BRENDA keys `protein` by index; each entry carries `organism` and, for 40 percent of them, `accessions`.

    Only Homo sapiens entries are kept, because the graph is human. An entry with no accession still identifies the
    enzyme through the EC number, which the caller joins to the local UniProt dump's EC column, so returning an
    empty list here does not lose the record - it moves it to the EC route.
    """
    if "homo sapiens" not in str(protein_entry.get("organism", "")).lower():
        return []
    accession_field = protein_entry.get("accessions") or ""
    text_to_search = accession_field if isinstance(accession_field, str) else " ".join(map(str, accession_field))
    return sorted({match.group(1) for match in UNIPROT_ACCESSION_PATTERN.finditer(text_to_search)})


def human_protein_entries(enzyme_record: dict) -> tuple[dict[str, list[str]], dict[str, str]]:
    """({protein index: accessions, [''] for a human entry without one}, {protein index: organism}) for the human protein
    entries of an enzyme. An entry of another organism is left out here, so a record reaches a row only through the
    human entries it names."""
    accessions_by_protein_index: dict[str, list[str]] = {}
    organism_by_protein_index: dict[str, str] = {}
    for protein_index, protein_entry in (enzyme_record.get("protein") or {}).items():
        if not isinstance(protein_entry, dict):
            continue
        protein_index = str(protein_index)
        is_human = "homo sapiens" in str(protein_entry.get("organism", "")).lower()
        accessions = human_accessions_of_protein_entry(protein_entry)
        if accessions:
            accessions_by_protein_index[protein_index] = accessions
            organism_by_protein_index[protein_index] = str(protein_entry.get("organism", ""))[:60]
        elif is_human:
            # no accession on this entry; the EC number still identifies the enzyme, so the row is written
            # with an empty accession and joined through the local UniProt EC column instead
            accessions_by_protein_index[protein_index] = [""]
            organism_by_protein_index[protein_index] = str(protein_entry.get("organism", ""))[:60]
    return accessions_by_protein_index, organism_by_protein_index


def regulation_rows(ec_number: str, enzyme_record: dict, note_classes: collections.Counter | None = None):
    """The rows of one enzyme: one per (field entry, human protein entry, accession). note_classes, when given, counts
    each (field, relation, note class) of an inhibition field entry and of an activating-compound entry."""
    accessions_by_protein_index, organism_by_protein_index = human_protein_entries(enzyme_record)
    if not accessions_by_protein_index:
        return
    for field_name, (relation_type, sign) in REGULATION_FIELDS_AND_RELATIONS.items():
        for record in enzyme_record.get(field_name) or []:
            ligand_name = str(record.get("value", "")).strip()
            if not ligand_name or ligand_name.lower() in ("more", "-"):
                continue
            protein_indices = [str(index) for index in record.get("proteins") or []]
            notes = notes_by_protein(record.get("comment", ""), protein_indices)
            if note_classes is not None and field_name in INHIBITION_FIELDS and record.get("comment"):
                form = "with" if PROTEIN_MARKER.search(str(record["comment"])) else "without"
                note_classes[f"comments of an inhibition field entry {form} protein markers"] += 1
            for protein_index in protein_indices:
                if protein_index not in accessions_by_protein_index:
                    continue
                own_notes = notes.get(protein_index, [])
                row_relation, row_sign, note_class = relation_type, sign, ""
                if field_name in INHIBITION_FIELDS:
                    row_relation, note_class = relation_of_notes(own_notes, ligand_name)
                    row_sign = sign if row_relation == "inhibits" else 0.0
                    if note_classes is not None:
                        note_classes[f"{field_name}: {row_relation or 'no row'} ({note_class})"] += 1
                    if row_relation is None:
                        continue
                elif field_name == "activating_compound":
                    row_relation, note_class = relation_of_activator_notes(own_notes, ligand_name)
                    row_sign = sign if row_relation == "activates" else 0.0
                    if note_classes is not None:
                        note_classes[f"{field_name}: {row_relation} ({note_class})"] += 1
                for accession in accessions_by_protein_index[protein_index]:
                    yield {"ec_number": ec_number, "field": field_name, "relation_type": row_relation, "sign": row_sign, "ligand_name": ligand_name,
                           "uniprot_accession": accession, "organism_entry": organism_by_protein_index.get(protein_index, ""),
                           "note_class": note_class, "brenda_comment": "; ".join(own_notes)[:300],
                           "brenda_reference_count": len(record.get("references") or [])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("brenda_json", type=Path,
                        help="the BRENDA JSON release unpacked, or data/brenda/brenda_2026_1_human_regulation_subset.json.gz, "
                             "which gives the same rows")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    rows_written = 0
    counts_by_relation = collections.Counter()
    note_classes = collections.Counter()
    distinct_ligand_names: set[str] = set()
    distinct_human_accessions: set[str] = set()
    enzyme_entries_seen = 0

    # the whole release unpacked, or the gzip-compressed human subset that experiments/make_brenda_human_subset.py writes
    open_release = gzip.open if arguments.brenda_json.suffix == ".gz" else open
    with open_release(arguments.brenda_json, "rb") as handle, open(arguments.output, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["ec_number", "field", "relation_type", "sign", "ligand_name",
                                                         "uniprot_accession", "organism_entry", "note_class", "brenda_comment",
                                                         "brenda_reference_count"])
        writer.writeheader()
        for ec_number, enzyme_record in ijson.kvitems(handle, "data"):
            enzyme_entries_seen += 1
            for row in regulation_rows(ec_number, enzyme_record, note_classes):
                writer.writerow(row)
                rows_written += 1
                counts_by_relation[row["relation_type"]] += 1
                distinct_ligand_names.add(row["ligand_name"])
                distinct_human_accessions.add(row["uniprot_accession"])

    summary = {"enzyme_entries_seen": enzyme_entries_seen, "rows_written": rows_written,
               "counts_by_relation": dict(counts_by_relation),
               "note_classes": dict(sorted(note_classes.items())),
               "distinct_ligand_names": len(distinct_ligand_names),
               "distinct_human_accessions": len(distinct_human_accessions)}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
