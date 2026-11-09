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
