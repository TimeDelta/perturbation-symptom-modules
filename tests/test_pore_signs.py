"""The two signs of a pore at rest, pinned at the registered constants (amendment item 37, decision 9.129 (iii)).

Why these tests exist. Item 37 repairs a sign: the pool route gave the opposite of the electrical sign for most
charge-moving reactions (decision 9.112). Its draft of 8 November 2026 then wrote a pore's flux direction as
sign(V_rest - E_i), which is the convention for a cation and reads chloride as efflux, the very error the item was
opened on. graph/membrane_potential.py has computed sign(z_i (V_rest - E_i)) since commit 73b5e1ee, but until
12 November 2026 no test held it, so nothing would have caught a change back to the draft's wording.

Two signs are pinned because they come apart for chloride: its ion moves inward while its conductance hyperpolarises,
since what the potential responds to is where E_i sits relative to rest, not which way the ion goes.
"""
from __future__ import annotations

import math

import pytest

from mechanistic_pathway_learning.graph.membrane_potential import (
    nernst_potential_millivolts, pore_conductance_edge_sign, pore_ion_flux_sign, resting_potential_millivolts)

INWARD, OUTWARD = -1.0, +1.0
DEPOLARISING, HYPERPOLARISING = +1.0, -1.0


@pytest.mark.parametrize("ion,expected_direction", [
    ("Na+", INWARD), ("K+", OUTWARD), ("Cl-", INWARD), ("Ca2+", INWARD)])
def test_which_way_the_ion_moves_through_an_open_pore_at_rest(ion, expected_direction):
    assert pore_ion_flux_sign(ion) == expected_direction


@pytest.mark.parametrize("ion,expected_effect", [
    ("Na+", DEPOLARISING), ("K+", HYPERPOLARISING), ("Cl-", HYPERPOLARISING), ("Ca2+", DEPOLARISING)])
def test_which_way_opening_the_pore_moves_the_potential(ion, expected_effect):
    assert pore_conductance_edge_sign(ion) == expected_effect


def test_the_cation_convention_of_the_draft_would_read_chloride_as_efflux():
    """The guard itself: sign(V_rest - E_i) without the valence gives chloride the wrong direction, and the code must
    not agree with it. If this test fails because the two agree, the valence has been dropped."""
    resting, chloride_reversal = resting_potential_millivolts(), nernst_potential_millivolts("Cl-")
    assert chloride_reversal < resting, "the test assumes E_Cl below rest, as at the registered constants"
    cation_convention = math.copysign(1.0, resting - chloride_reversal)
    assert cation_convention == OUTWARD
    assert pore_ion_flux_sign("Cl-") != cation_convention


@pytest.mark.parametrize("ion", ["Na+", "K+", "Ca2+"])
def test_for_a_cation_the_valence_changes_nothing(ion):
    """The correction is for anions only; every cation keeps the sign the draft's convention gives."""
    resting = resting_potential_millivolts()
    assert pore_ion_flux_sign(ion) == math.copysign(1.0, resting - nernst_potential_millivolts(ion))


def test_chloride_is_where_the_two_signs_agree_and_potassium_where_they_differ():
    """Flux direction and edge sign are distinct quantities: they share a sign for chloride (inward, hyperpolarising)
    and they are opposite for sodium (inward, depolarising) and potassium (outward, hyperpolarising), so neither can
    stand in for the other."""
    assert pore_ion_flux_sign("Cl-") == pore_conductance_edge_sign("Cl-")
    assert pore_ion_flux_sign("Na+") != pore_conductance_edge_sign("Na+")
    assert pore_ion_flux_sign("K+") != pore_conductance_edge_sign("K+")
