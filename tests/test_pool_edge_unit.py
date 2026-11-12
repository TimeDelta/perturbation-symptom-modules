"""The two routes into VM_c in one unit (amendment item 37, decision 9.129 (1), ruled 12 November 2026).

Why these tests exist. Until that ruling the pool edges were rescaled to sum to 1 while the conductance edges were in
millivolts, so the two routes into VM_c shared a row without sharing a unit; the rescale gave every pool the chloride
leak's current by accident. These tests hold the conversion explicit: both routes are a millivolts-per-current
coefficient times one leak-sized current of the ion, so their ratio for one reaction is the physiological one.
"""
from __future__ import annotations

import pytest

from mechanistic_pathway_learning.graph.membrane_potential import (
    LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE, PUMP_CLAMPED_POOL_SENSITIVITY, clamped_pool_edge_weights,
    driving_force_coefficients_millivolts, leak_current_microamperes_per_square_centimetre,
    pore_conductance_weight_millivolts, total_resting_conductance_microsiemens_per_square_centimetre)

IONS = ("Na+", "K+", "Cl-")


@pytest.mark.parametrize("ion,expected_current", [("Na+", 2.7016), ("K+", 1.5757), ("Cl-", 0.2213)])
def test_one_leak_sized_current_at_rest(ion, expected_current):
    assert leak_current_microamperes_per_square_centimetre(ion) == pytest.approx(expected_current, abs=5e-4)


@pytest.mark.parametrize("ion,expected_weight", [("Na+", 1.306), ("K+", 0.094), ("Cl-", 0.896)])
def test_the_cytosolic_pool_edges_are_in_millivolts(ion, expected_weight):
    """The values of the Fable pass of 10 November 2026, which the ruling took."""
    _, weight = clamped_pool_edge_weights()[(ion, "c")]
    assert weight == pytest.approx(expected_weight, abs=5e-4)


@pytest.mark.parametrize("ion", IONS)
def test_both_routes_are_a_coefficient_times_the_same_current(ion):
    """A conductance edge is 1/g_total times the current; a pool edge is c_i S_i times it. So dividing out the current
    leaves each route's millivolts per uA/cm2, which is what makes them comparable for one reaction."""
    current = leak_current_microamperes_per_square_centimetre(ion)
    conductance_edge = pore_conductance_weight_millivolts(ion, LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[ion])
    assert conductance_edge / current == pytest.approx(1000.0 / total_resting_conductance_microsiemens_per_square_centimetre())
    _, pool_edge = clamped_pool_edge_weights()[(ion, "c")]
    pool_coefficient = abs(PUMP_CLAMPED_POOL_SENSITIVITY[ion] * driving_force_coefficients_millivolts()[(ion, "c")])
    assert pool_edge / current == pytest.approx(pool_coefficient)


@pytest.mark.parametrize("ion,physiological_ratio", [("Na+", 0.053), ("K+", 0.0065), ("Cl-", 0.445)])
def test_the_pool_route_is_below_the_charge_route_for_every_ion(ion, physiological_ratio):
    """Pool edge over conductance edge for one leak-sized unit is the physiological ratio of the two routes, 5.3, 0.65
    and 44.5 per cent; every one below 1 is what keeps a pore's net sign safe from its own pool route."""
    _, pool_edge = clamped_pool_edge_weights()[(ion, "c")]
    conductance_edge = pore_conductance_weight_millivolts(ion, LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[ion])
    assert pool_edge / conductance_edge == pytest.approx(physiological_ratio, abs=5e-4)
    assert pool_edge < conductance_edge


def test_the_pool_edges_are_not_rescaled_to_sum_to_one():
    """What every build before 12 November 2026 did, as history: the weights summed to 1."""
    total = sum(weight for _, weight in clamped_pool_edge_weights().values())
    assert total == pytest.approx(2.296, abs=1e-3)
    assert total != pytest.approx(1.0)


@pytest.mark.parametrize("ion", IONS)
def test_the_extracellular_pools_carry_nothing(ion):
    assert clamped_pool_edge_weights()[(ion, "e")] == (0.0, 0.0)
