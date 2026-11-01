"""The activating-compound rule of decision 9.88 (the owner's rulings of 1 November 2026).

The owner ruled on 26 October 2026 that "\"no effect\" should not have an activates edge", and on 1 November 2026, after
a Fable reading of every activator note the absence pattern catches (docs/brenda_activator_note_classification_2026-11-01
.md), "Don't widen then" and, of the conservative rule, "That's a defensible rule. Use it for now". Every case below is a
note of BRENDA release 2026.1 (CC BY 4.0, docs/data_sources.md), quoted as the reading quotes it, with its row label
there. The rule may only ever turn a clean denial of an effect on this enzyme into a negative; each other way it can be
wrong must leave the `activates` edge as it was before the ruling.
"""
import json
import pytest

from experiments.extract_brenda_enzyme_regulation import (
    NO_ACTIVATION_RELATION,
    regulation_rows,
    relation_of_activator_notes,
)
from experiments.map_brenda_regulation_to_graph import overlap_with_relation

import pandas as pd


# the two clean negatives of the reading: an effect denied on this human enzyme, no activation stated anywhere
@pytest.mark.parametrize("note, ligand", [
    ("no effect", "pyrazole"),  # C1, EC 1.1.1.284
    ("Ca2+/calmodulin has no detectable effect on recombinant human NAD kinase", "Calmodulin"),  # C13, EC 2.7.1.23
])
def test_a_clean_denial_of_an_effect_on_this_enzyme_is_a_negative(note, ligand):
    assert relation_of_activator_notes([note], ligand)[0] == NO_ACTIVATION_RELATION


# notes the rule must leave as `activates`, one for each guard
@pytest.mark.parametrize("note, ligand, guard", [
    # activation stated beside the absence: the absence is a comparison, the commonest case in the reading
    ("increases activity of the mitochondrial enzyme, no effect on the activity of the cytosolic enzyme", "succinate",
     "activation stated"),  # C2, EC 1.1.1.40
    ("2 mM, 4fold increase in activity of type I enzyme, no effect on type II enzyme", "spermine",
     "activation stated"),  # C14, EC 2.7.1.68
    # "induces" counts as stating activation
    ("induces activities towards bilirubin and 1-naphthol whereas does not affect activities against morphine and chloramphenicol",
     "Phenobarbital", "induces"),  # C10, EC 2.4.1.17
    # an absence of inhibition is not an absence of activation
    ("no inhibition up to 75 mM", "phosphate", "inhibition, not effect"),  # C21, EC 2.7.6.1
    # a dose-bounded absence is a point on a dose response
    ("no effect at 0.02-0.2 mM", "spermine", "dose-bounded"),  # C30, EC 3.1.3.48
    # an absence about a form or part of the compound compares two forms of it
    ("the presence of the lipoyl moiety on H-protein does not affect the rates of GLDC catalysed glycine decarboxylation",
     "lipoylated H-protein", "form of the compound"),  # C6, EC 1.4.4.2
])
def test_an_absence_that_is_not_a_clean_denial_keeps_the_edge(note, ligand, guard):
    assert relation_of_activator_notes([note], ligand)[0] == "activates", guard


def test_the_absence_pattern_is_not_widened():
    """"Don't widen then": a note of "no activation" or "does not activate" is not a candidate, so it keeps `activates`.
    The widening was also unsafe: case-insensitive, "no activation" matches the compound NO in "NO activation" on
    soluble guanylyl cyclase, EC 4.6.1.2, a textbook activation (W23 of the reading)."""
    assert relation_of_activator_notes(["no stimulation of GTP hydrolysis"], "GAP")[0] == "activates"  # W20
    assert relation_of_activator_notes(["analog of NADP+ does not stimulate the reverse cyclohydrolase activity"],
                                       "2',5'-ADP")[0] == "activates"  # W18
    assert relation_of_activator_notes(["NO activation of the enzyme requires the reduced heme"], "NO")[0] == "activates"


def test_a_note_with_no_absence_is_written_as_before():
    assert relation_of_activator_notes(["2fold activation at 1 mM"], "ATP") == ("activates", "no note of absence")
    assert relation_of_activator_notes([], "ATP") == ("activates", "no note of absence")


def test_a_negative_row_carries_no_sign_and_the_relation():
    enzyme = {"protein": {"1": {"organism": "Homo sapiens", "accessions": ["O95544"]}},
              "activating_compound": [
                  {"value": "Calmodulin", "proteins": ["1"], "references": ["1"],
                   "comment": "Ca2+/calmodulin has no detectable effect on recombinant human NAD kinase"},
                  {"value": "ATP", "proteins": ["1"], "references": ["2"], "comment": "2fold activation"}]}
    rows = {row["ligand_name"]: row for row in regulation_rows("2.7.1.23", enzyme)}
    assert rows["Calmodulin"]["relation_type"] == NO_ACTIVATION_RELATION and rows["Calmodulin"]["sign"] == 0.0
    assert rows["ATP"]["relation_type"] == "activates" and rows["ATP"]["sign"] == 1.0


def test_a_negative_that_falls_on_an_activates_pair_is_counted_and_kept_apart():
    pairs = pd.DataFrame([{"base_metabolite_id": "MAM01", "uniprot_accession": "O95544", "relation_type": "activates"}])
    negatives = pd.DataFrame([{"base_metabolite_id": "MAM01", "uniprot_accession": "O95544"},
                              {"base_metabolite_id": "MAM02", "uniprot_accession": "O95544"}])
    assert overlap_with_relation(negatives, pairs, "activates") == 1
    assert overlap_with_relation(negatives.iloc[0:0], pairs, "activates") == 0
