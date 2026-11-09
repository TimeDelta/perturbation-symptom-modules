"""The mixed-cation pore weight rule of amendment item 37, pinned to the values
docs/membrane_potential_constants.md records.

Why these tests exist. That document records a weight per pore but states that the script behind the numbers was
never committed, so on 9 November 2026 the rule was recovered by derivation instead and checked against every
recorded value. These tests hold it to those values, so that a change to the registered constants, or to the rule,
shows up as a disagreement with the record rather than as a silently different graph.
"""
from __future__ import annotations

import pytest

from mechanistic_pathway_learning.graph.membrane_potential import (
    LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE, MIXED_PORE_PERMEABILITIES,
    chord_conductance_per_unit_permeability, mixed_pore_conductance_microsiemens_per_square_centimetre,
    mixed_pore_reversal_potential_millivolts, mixed_pore_weight_millivolts, pore_conductance_weight_millivolts)

# (pore, recorded reversal potential in mV, recorded weight in mV), from the reconciliation table of 6 November 2026
RECORDED = [
    ("nicotinic, neuronal", -2.1, 18.83),
    ("NALCN", +2.2, 19.09),
    ("AMPA", -0.8, 18.91),
    ("kainate", -0.8, 18.91),
    ("NMDA", +2.2, 19.09),
    ("nicotinic, muscle", -0.1, 18.95),
    ("5-HT3", -0.1, 18.95),
    ("P2X", +2.2, 19.09),
    ("TRPM4/5", +2.2, 19.09),
    ("HCN", -23.0, 17.06),
    ("Nav", +47.9, 22.77),
]


@pytest.mark.parametrize("pore,recorded_reversal,recorded_weight", RECORDED)
def test_the_recorded_reversal_potential_and_weight_are_reproduced(pore, recorded_reversal, recorded_weight):
    """The record rounds the weight to 0.01 mV, so that is held tightly. It rounds most reversal potentials to 0.1 mV
    but gives HCN's as a whole-millivolt range, "-23 to -33 mV", so the potential is held to 0.15: the computed values
    sit within 0.04 mV of every recorded figure except HCN's, which is 0.10 mV from the rounded -23."""
    permeability = MIXED_PORE_PERMEABILITIES[pore]
    assert mixed_pore_reversal_potential_millivolts(permeability) == pytest.approx(recorded_reversal, abs=0.15)
    assert mixed_pore_weight_millivolts(permeability) == pytest.approx(recorded_weight, abs=0.01)


def test_the_second_hcn_permeability_ratio_also_reproduces():
    """Macri et al. 2012 give two ratios; the table holds 0.35 and records the other as -33 mV weighing 15.45."""
    assert mixed_pore_reversal_potential_millivolts({"Na+": 0.23, "K+": 1.0}) == pytest.approx(-33.0, abs=0.15)
    assert mixed_pore_weight_millivolts({"Na+": 0.23, "K+": 1.0}) == pytest.approx(15.45, abs=0.01)


def test_the_chord_conductances_per_unit_permeability_are_the_recovered_values():
    assert chord_conductance_per_unit_permeability("Na+") == pytest.approx(3.10241, abs=5e-5)
    assert chord_conductance_per_unit_permeability("K+") == pytest.approx(0.59768, abs=5e-5)
    assert chord_conductance_per_unit_permeability("Cl-") == pytest.approx(0.70108, abs=5e-5)


@pytest.mark.parametrize("ion", ["Na+", "K+", "Cl-"])
def test_a_single_ion_pore_is_the_rules_endpoint_and_returns_that_ions_leak_conductance(ion):
    """The normalisation is what makes this true, and it is why the mixed rule and the single-ion rule agree at the
    edges: a pore permeable to one ion alone must weigh exactly what that ion's leak conductance weighs."""
    assert mixed_pore_conductance_microsiemens_per_square_centimetre({ion: 1.0}) == pytest.approx(
        LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[ion])
    assert mixed_pore_weight_millivolts({ion: 1.0}) == pytest.approx(
        pore_conductance_weight_millivolts(ion, LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[ion]))


def test_the_registered_single_ion_terms_are_the_ones_the_record_states():
    """"the ruled single-ion terms for comparison are Na+ 24.6, K+ 14.3 and Cl- 2.0 mV" (section 3 of the document)."""
    leak = LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE
    assert pore_conductance_weight_millivolts("Na+", leak["Na+"]) == pytest.approx(24.6, abs=0.05)
    assert pore_conductance_weight_millivolts("K+", leak["K+"]) == pytest.approx(14.3, abs=0.05)
    assert pore_conductance_weight_millivolts("Cl-", leak["Cl-"]) == pytest.approx(2.0, abs=0.05)


def test_only_the_permeability_ratio_matters_and_not_its_scale():
    """The permeabilities are in arbitrary units, so scaling every one of them must change nothing."""
    one = {"Na+": 1.0, "K+": 1.2}
    scaled = {ion: 37.0 * share for ion, share in one.items()}
    assert mixed_pore_weight_millivolts(scaled) == pytest.approx(mixed_pore_weight_millivolts(one))
    assert mixed_pore_reversal_potential_millivolts(scaled) == pytest.approx(
        mixed_pore_reversal_potential_millivolts(one))


def test_every_mixed_pore_depolarises_at_rest():
    """Decision 9.112's content rests on this: "Every mixed pore still depolarises at V_rest"."""
    for pore, permeability in MIXED_PORE_PERMEABILITIES.items():
        assert mixed_pore_reversal_potential_millivolts(permeability) > -72.6, pore


def test_every_mixed_pore_class_has_a_gene_prefix_and_every_prefix_names_a_real_class():
    """A prefix naming a class the permeability table does not hold would select no weight, and a class no prefix
    reaches would never be built."""
    from mechanistic_pathway_learning.graph.membrane_potential import MIXED_PORE_GENE_PREFIXES

    classes_from_prefixes = {pore_class for _, pore_class in MIXED_PORE_GENE_PREFIXES}
    assert classes_from_prefixes <= set(MIXED_PORE_PERMEABILITIES), (
        classes_from_prefixes - set(MIXED_PORE_PERMEABILITIES))
    assert set(MIXED_PORE_PERMEABILITIES) == classes_from_prefixes, (
        set(MIXED_PORE_PERMEABILITIES) - classes_from_prefixes)


@pytest.mark.parametrize("gene,pore_class", [
    ("CHRNA7", "nicotinic, neuronal"), ("CHRNB2", "nicotinic, neuronal"), ("CHRND", "nicotinic, muscle"),
    ("GRIA1", "AMPA"), ("GRIK2", "kainate"), ("GRIN2B", "NMDA"), ("HTR3A", "5-HT3"), ("P2RX4", "P2X"),
    ("TRPM4", "TRPM4/5"), ("TRPM5", "TRPM4/5"), ("NALCN", "NALCN"), ("HCN1", "HCN"), ("SCN1A", "Nav"),
])
def test_a_mixed_pore_gene_resolves_to_its_class(gene, pore_class):
    from mechanistic_pathway_learning.graph.membrane_potential import mixed_pore_class_of_gene

    assert mixed_pore_class_of_gene(gene) == pore_class


@pytest.mark.parametrize("gene", ["KCNQ2", "KCNJ2", "CLCN2", "CACNA1C", "GRID2", "SLC6A4", "ATP1A1", "SLC1A2"])
def test_a_gene_that_is_not_a_mixed_pore_takes_the_single_ion_route(gene):
    """A potassium, chloride or calcium channel carries one ion and its weight is that ion's. SLC6A4 is here because
    the serotonin transporter carries an annotated channel activity and so passes the GO term; it moves 5-HT with
    Na+ and Cl-, so the single-ion rule is what excludes it, and it must not pick up a mixed-pore weight on the way."""
    from mechanistic_pathway_learning.graph.membrane_potential import mixed_pore_class_of_gene

    assert mixed_pore_class_of_gene(gene) is None


def test_the_glutamate_classes_are_split_where_the_weights_differ():
    """experiments/audit_channel_conduction.py lumps AMPA, kainate and NMDA into one family; the permeability table
    gives NMDA a different weight from the other two, so the prefixes split them."""
    from mechanistic_pathway_learning.graph.membrane_potential import mixed_pore_class_of_gene

    ampa = mixed_pore_weight_millivolts(MIXED_PORE_PERMEABILITIES[mixed_pore_class_of_gene("GRIA1")])
    kainate = mixed_pore_weight_millivolts(MIXED_PORE_PERMEABILITIES[mixed_pore_class_of_gene("GRIK2")])
    nmda = mixed_pore_weight_millivolts(MIXED_PORE_PERMEABILITIES[mixed_pore_class_of_gene("GRIN2B")])
    assert ampa == pytest.approx(kainate)
    assert nmda != pytest.approx(ampa)


def test_grina_is_not_an_nmda_receptor_though_the_grin_prefix_would_take_it():
    """UniProt Q7Z429 is "Protein lifeguard 1 ... Potential apoptotic regulator", not a receptor subunit (Fable pass,
    9 November 2026). It is absent from the v5 graph, so this guards a future one."""
    from mechanistic_pathway_learning.graph.membrane_potential import mixed_pore_class_of_gene

    assert mixed_pore_class_of_gene("GRINA") is None
    assert mixed_pore_class_of_gene("GRIN2B") == "NMDA"


def test_chrna1_is_left_in_the_neuronal_class_on_purpose():
    """CHRNA1 assembles the muscle receptor, so taxonomically it belongs in "nicotinic, muscle". It is left where it
    is because graph/reactome_import.py picks a reaction's class from its first sorted catalyst gene, and on the v5
    graph RCT_622326 and RCT_629595 are each decided by CHRNA1 while every other member of each is neuronal: moving
    it would flip two overwhelmingly neuronal reactions to the muscle weight on an alphabetical accident. This test
    exists so the state is deliberate and a later change to it is a decision rather than a drive-by fix."""
    from mechanistic_pathway_learning.graph.membrane_potential import mixed_pore_class_of_gene

    assert mixed_pore_class_of_gene("CHRNA1") == "nicotinic, neuronal"
    assert mixed_pore_class_of_gene("CHRNB1") == "nicotinic, neuronal"
    assert mixed_pore_class_of_gene("CHRND") == "nicotinic, muscle"
