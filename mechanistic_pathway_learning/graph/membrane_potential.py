"""The neuronal membrane potential, computed from the ion pools rather than learned from the reactions.

Why. In the graph as built, `VM_c` received an edge from each of the 405 reactions that move net charge across the
plasma membrane, and the encoder averages a node's incoming messages within a relation, so each one arrived divided by
405 and nothing reached the node (docs/label_source_review.md, sections 22 and 23; the median field at `VM_c` was
2.9e-15). `VM_c` also carries none of the 138 node descriptor columns, so there was nothing else to read it by. The
owner, 12 October 2026: "Why not just change the VM_c to e.g. the Nernst equation", then "Fix the electrical layer".

What this computes. The potential of a membrane with several permeant ions is not the Nernst potential, which is one
ion's equilibrium potential. For a passive membrane at rest it is the parallel-conductance (Millman) equation

    V_m = sum_ion ( g_ion / g_total ) * E_ion,      E_ion = (RT / z_ion F) * ln( [ion]_out / [ion]_in )

and because the encoder's node state is a unitless deviation from rest and not a concentration, the law is used in its
linearised form, which is exact to first order around the resting state:

    change in V_m = sum_ion ( g_ion / g_total ) * (RT / z_ion F) * ( fractional change in [ion]_out
                                                                    - fractional change in [ion]_in )

So each ion pool feeds `VM_c` one edge whose weight is that ion's conductance share times RT/z F, with the sign of the
side it sits on. The weights are fixed numbers from a cited source and are not fitted, which is the point: the
aggregation stops being a learned mean over 405 edges and becomes a stated physical law over six.

Why the parallel-conductance equation and not Goldman-Hodgkin-Katz. GHK weights each ion by a permeability, and no
measured permeability ratio for a mammalian central neuron was found (docs/membrane_potential_constants.md names the
routes tried). The source used here states conductances, not permeabilities, and says so: "Leak currents were
calculated using Ohm's Law, I=g(Vm-E)". Putting its conductances into GHK as if they were permeabilities gives
-33.2 mV against the -72.6 mV it reports, a 39 mV error, so the two laws are not interchangeable here and the law has
to be the one the constants were measured under.

What this cannot claim. The 7 reactions `VM_c` gates are all also sources of charge movement, so the layer is seven
two-cycles through the potential, which is an excitable membrane: regenerative sodium current is positive feedback and
its fixed point is unstable. A model run to a fixed point under a contraction bound cannot show excitability. The
registered claim is therefore the subthreshold steady state, and the contraction bound is part of that claim rather
than a numerical convenience (docs/label_source_review.md 23.3).

The constants, their quotations and where each was read are in docs/membrane_potential_constants.md; the source rows
are in docs/data_sources.md.
"""
from __future__ import annotations

import math

# Düsterwald, Currin, Burman, Akerman, Kay and Raimondo 2018, eLife 7:e39575 (doi 10.7554/eLife.39575, PMID 30260315),
# Table 1, read from the Europe PMC full text on 12 October 2026 under CC BY 4.0. A pump-leak model of a rodent central
# neuron at 37 degrees Celsius. Its own reported steady state is V_m -72.6 mV, E_K -95.1 mV and E_Cl -83.8 mV.
GAS_CONSTANT_JOULES_PER_KELVIN_MOLE = 8.31446
FARADAY_CONSTANT_COULOMBS_PER_MOLE = 96485.33
TEMPERATURE_KELVIN = 310.15
RESTING_CONCENTRATION_MILLIMOLAR = {  # (ion, compartment letter) -> mM; "c" cytosolic, "e" extracellular
    ("Na+", "e"): 145.0, ("Na+", "c"): 14.0,
    ("K+", "e"): 3.5, ("K+", "c"): 122.9,
    ("Cl-", "e"): 119.0, ("Cl-", "c"): 5.2,
    # Calcium is not in Düsterwald et al. 2018, whose full text (PMC6200395, read 5 November 2026) holds the word
    # nowhere and whose Table 1 lists only gNa, gK, gCl and gKCC2. These are Raimondo, Richards and Woodin 2015
    # (`raimondo2015ion`, set B of docs/membrane_potential_constants.md, CC BY), Table 1, typical rest:
    # "Ca2+ | 70 nM | 2 mM | +137 mV". A second source, Silver and Erecinska, gives [Ca2+]e 1.49-1.56 mM and
    # [Ca2+]i 69-74 nM, i.e. +132 to +134 mV, within 4 mV of these (decision 9.113).
    ("Ca2+", "e"): 2.0, ("Ca2+", "c"): 7.0e-5,
}
LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE = {"Na+": 20.0, "K+": 70.0, "Cl-": 20.0}
ION_CHARGE = {"Na+": 1, "K+": 1, "Cl-": -1, "Ca2+": 2}
REPORTED_RESTING_POTENTIAL_MILLIVOLTS = -72.6  # Table 1, row Vm, of the same source
# Which ions carry which route. The two reasons this comment gave for leaving calcium out, until decision 9.113
# corrected them on 8 November 2026, were that "its equilibrium potential lies so far from rest that its relative
# change moves the potential little" and that "the voltage equation above is derived for monovalent ions"
# (written 12 October 2026, commit 84cc176, citing docs/label_source_review.md 23.2). Both are now stated as wrong:
# under the parallel-conductance law the concentration term is dV/dE_i = g_i / g_total whatever E_i is, so the
# distance of E_Ca from rest is not what makes calcium's concentration route small; and the law takes any valence
# through E_i = (RT / z_i F) ln([i]_o / [i]_i), it is Goldman-Hodgkin-Katz that is derived for monovalent ions and
# section 4.1 rejected that. The distance from rest is what makes the CONDUCTANCE term large: dV/dg_i is
# (E_i - V_rest) / g_total, and calcium's is the largest of any ion. So under amendment item 37 calcium is to take a
# conductance term and no pool term, and what holds its conductance term small is its small resting conductance and
# not the law. **As of this commit the constants and weight functions below exist and no build calls them**: the
# pores_and_clamped_pools build of item 37 is not yet wired into graph/reactome_import.py, and the registered value
# membrane_potential_build is still item 35's computed_from_the_pools, under which calcium has neither route.
IONS_IN_THE_VOLTAGE_EQUATION: tuple[str, ...] = ("Na+", "K+", "Cl-")  # the pool (concentration) route
IONS_WITH_A_CONDUCTANCE_TERM: tuple[str, ...] = ("Na+", "K+", "Cl-", "Ca2+")

# The steady-state change in an ion's cytosolic concentration per unit sustained flux, once the Na+/K+-ATPase and
# KCC2 have acted: d ln[ion]_i per uA/cm2 of the ion's own sustained inward current. Derived from Düsterwald et al.
# 2018 Table 1 with no learned parameter (docs/extracellular_pool_sensitivities_2026-11-07.md), and registered as
# amendment item 37 after the owner's ruling of 4 November 2026 in decision 9.112. These are the DIAGONAL of a 3x3
# response matrix whose cross-terms are not zero (a sustained sodium current moves potassium by -0.0248 and chloride
# by +0.0126): item 37 registers the diagonal alone, and the cross-terms it drops are a stated limit of the build,
# not an omission.
PUMP_CLAMPED_POOL_SENSITIVITY = {"Na+": 0.0995, "K+": 0.0035, "Cl-": 0.833}

# The resting conductance of a conductive pore, per ion, in uS/cm2. Sodium, potassium and chloride are the leak
# conductances above. Calcium's is the one value item 37 leaves underdetermined: two independent routes agree only
# within a factor of 1.6, and neither is a generic cortical neuron at body temperature. The measured route is used,
# because the alternative is a fitted model whose optimiser was never constrained at rest and whose own bounds allow
# a factor of three either way; the choice moves the weight from 0.0120 to 0.0076 mV, two to three orders of
# magnitude below the chloride term either way, so no result turns on it (decision 9.113).
CALCIUM_RESTING_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE = 6.3e-3  # Dreyfus et al. 2010, a measured T-type
# window conductance in a rat dorsal-horn interneuron. The alternative, Hay et al. 2011's data-fitted layer 5b
# cortical pyramidal model at 34 degrees Celsius, gives 4.0e-3 uS/cm2 and a weight of 0.0076 mV.
# THE THALAMIC EXCEPTION IS STATED AND NOT BUILT: the T-type window conductance of a thalamic relay neuron is about
# 1.7 uS/cm2, which would weigh about 3.3 mV, more than the whole chloride term, against the 0.012 mV this build
# gives every cell class. It belongs with a future per-cell-class treatment, as the per-class chloride question of
# decision 9.112 does, and neither is built.
THALAMIC_RELAY_CALCIUM_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE = 1.7  # stated, not built


def thermal_voltage_millivolts() -> float:
    """RT/F in millivolts at the source's temperature: 26.73 mV at 37 degrees Celsius."""
    return GAS_CONSTANT_JOULES_PER_KELVIN_MOLE * TEMPERATURE_KELVIN / FARADAY_CONSTANT_COULOMBS_PER_MOLE * 1000.0


def nernst_potential_millivolts(ion: str) -> float:
    """The ion's equilibrium potential at the resting concentrations, (RT/zF) ln([out]/[in])."""
    return (thermal_voltage_millivolts() / ION_CHARGE[ion]) * math.log(
        RESTING_CONCENTRATION_MILLIMOLAR[(ion, "e")] / RESTING_CONCENTRATION_MILLIMOLAR[(ion, "c")])


def conductance_share(ion: str) -> float:
    """The ion's share of the resting leak conductance: 0.636 for K+, 0.182 each for Na+ and Cl-."""
    return LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[ion] / sum(
        LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[name] for name in IONS_IN_THE_VOLTAGE_EQUATION)


def passive_resting_potential_millivolts() -> float:
    """The parallel-conductance potential of these constants, with no pump current: -64.4 mV.

    The source reports -72.6 mV, and the 8.2 mV between them is its electrogenic Na+/K+-ATPase, which its model carries
    as a current of its own. The difference is a baseline and not a response coefficient: with the conductances fixed,
    the pump reaches the potential only by moving the ion pools, and the encoder's state is a deviation from rest, so
    the offset cancels and the coefficients below are unaffected."""
    return sum(conductance_share(ion) * nernst_potential_millivolts(ion) for ion in IONS_IN_THE_VOLTAGE_EQUATION)


def driving_force_coefficients_millivolts() -> dict[tuple[str, str], float]:
    """(ion, compartment letter) -> dV_m per unit fractional change in that pool, in millivolts.

    The extracellular side of a cation raises the potential and its cytosolic side lowers it; chloride is the reverse,
    because its charge is negative. The magnitudes are the ion's conductance share times RT/zF, so potassium carries
    3.5 times sodium or chloride, which is the fact a weight of 1 on every edge threw away."""
    coefficients = {}
    for ion in IONS_IN_THE_VOLTAGE_EQUATION:
        outward = conductance_share(ion) * thermal_voltage_millivolts() / ION_CHARGE[ion]
        coefficients[(ion, "e")] = outward
        coefficients[(ion, "c")] = -outward
    return coefficients


def driving_force_edge_weights() -> dict[tuple[str, str], tuple[float, float]]:
    """(ion, compartment letter) -> (sign, weight) for the pool's edge into VM_c.

    The weights are the coefficients above rescaled to sum to 1 in absolute value, because the graph carries no units
    and the encoder reads an edge as sign x weight: only the ratios between the six are physical, and a total of 1
    keeps the node's summed input on the scale every other node's in-degree mean has. Multiplying all six by one
    constant is a change of the gain the relation learns, not of the physics."""
    coefficients = driving_force_coefficients_millivolts()
    total = sum(abs(value) for value in coefficients.values())
    return {key: (math.copysign(1.0, value), abs(value) / total) for key, value in coefficients.items()}


def total_resting_conductance_microsiemens_per_square_centimetre() -> float:
    """g_total, the resting conductance the weights divide by: 110 uS/cm2, the sum of the three leak conductances.

    Calcium's resting conductance is not added. It is 6.3e-3 uS/cm2, six parts in a hundred thousand of this total,
    and the source's 110 is the resting conductance of the cell it measured; adding a term the source did not count
    would change the divisor of every other ion to no physiological end. 1 / g_total is 9.09 mV per uA/cm2.
    """
    return sum(LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[ion] for ion in IONS_IN_THE_VOLTAGE_EQUATION)


def resting_potential_millivolts() -> float:
    """V_rest the driving forces are taken against: the source's reported -72.6 mV, not the passive -64.4 mV.

    The passive value omits the source's electrogenic Na+/K+-ATPase, which its model carries as a current of its own.
    A driving force is a distance from the cell's actual resting potential, so the reported value is the right one
    here, and it is what the numbers of decision 9.113 were computed against (E_Ca - V_rest = +209.7 mV).
    """
    return REPORTED_RESTING_POTENTIAL_MILLIVOLTS


def pore_driving_force_millivolts(ion: str) -> float:
    """E_i - V_rest for the ion, in millivolts: +135.1 for Na+, -22.5 for K+, -11.1 for Cl- and +209.7 for Ca2+.

    Chloride is -11.07 here against the -11.2 that decision 9.113's row states, because the row took the source's
    reported E_Cl of -83.8 mV while this computes -83.67 mV from the source's own concentrations. The 0.13 mV is
    rounding in the source's table and changes nothing; the computed route is used because every other weight in this
    module is computed from the concentrations too, and one number taken from a different place would be the kind of
    inconsistency a reader cannot check.
    """
    return nernst_potential_millivolts(ion) - resting_potential_millivolts()


def pore_ion_flux_sign(ion: str) -> float:
    """Which way the ION moves through an open pore at rest: sign(V_rest - E_i), as decision 9.112 (c) fixed it.

    Returns -1 for inward and +1 for outward. The item writes the rule as sign(V_rest - E_i), which is the
    convention for a cation; the valence has to enter it for an anion, so what is computed is
    sign(z_i (V_rest - E_i)). Without the valence, chloride at rest (V_rest -72.6 mV above E_Cl -83.7 mV) would read
    as efflux, and it is precisely the six chloride channels Reactome writes as efflux that reading the
    electrochemistry is meant to correct, along with RCT_1296046 written as influx.

    At the registered constants sodium, calcium and chloride move inward at rest and potassium moves outward.

    This is NOT the sign of the pore's edge into VM_c, which is pore_conductance_edge_sign below. The two come apart
    for chloride: its flux is inward while its conductance hyperpolarises, because what the potential responds to is
    where E_i sits relative to rest, not which way the ion goes.
    """
    return math.copysign(1.0, ION_CHARGE[ion] * (resting_potential_millivolts() - nernst_potential_millivolts(ion)))


def pore_conductance_edge_sign(ion: str) -> float:
    """The sign of the pore's edge into VM_c: sign(E_i - V_rest).

    Under the parallel-conductance law dV/dg_i = (E_i - V_rest) / g_total, so opening a conductance pulls the
    potential toward that ion's equilibrium potential. Sodium (E +62.5 mV) and calcium (+137.1 mV) sit above rest and
    depolarise, potassium (-95.1 mV) and chloride (-83.7 mV) sit below it and hyperpolarise. No correction for charge
    is needed or wanted: E_i already carries the valence through its 1/z, so applying the sign of the charge again
    would invert chloride, whose conductance plainly hyperpolarises.
    """
    return math.copysign(1.0, pore_driving_force_millivolts(ion))


def pore_conductance_weight_millivolts(ion: str, conductance_microsiemens_per_square_centimetre: float) -> float:
    """g_i |E_i - V_rest| / g_total in millivolts: what one pore of this ion and this conductance weighs at VM_c.

    The driving force sits in the weight, which is what makes the chloride term small (0.101 mV per uS/cm2 against
    0.205 for potassium and 1.228 for sodium) without any choice being made about it, and what makes calcium's term
    small for its conductance rather than for its distance from rest (1.906 mV per uS/cm2, the largest of any ion,
    times a resting conductance of 6.3e-3).
    """
    return (conductance_microsiemens_per_square_centimetre * abs(pore_driving_force_millivolts(ion))
            / total_resting_conductance_microsiemens_per_square_centimetre())


def clamped_pool_edge_weights() -> dict[tuple[str, str], tuple[float, float]]:
    """(ion, compartment letter) -> (sign, weight) for the pool's edge into VM_c under amendment item 37.

    This is to replace driving_force_edge_weights() for the pores_and_clamped_pools build of amendment item 37, which
    is not yet wired into graph/reactome_import.py: nothing calls this function as of the commit that adds it. Two changes from it: the
    cytosolic weights are the pump-clamped sensitivities rather than conductance share times RT/zF, and the three
    extracellular pools take weight 0 at the registered steady-state readout, which decision 9.112's first
    sub-question ruled on 7 November 2026 (their closed-space values and clearance times are kept for decision
    9.118, and the pools stay as inputs). The signs are unchanged: more cytosolic sodium or potassium lowers the
    pool's contribution to the potential, and chloride is the reverse because its charge is negative.

    The weights are rescaled to sum to 1 in absolute value, as the item-35 weights were, because the graph carries no
    units and only the ratios between the edges are physical. This normalisation does not preserve the physiological
    ratio between the pool route and the conductance edges, which is a limit registered with item 37.
    """
    coefficients: dict[tuple[str, str], float] = {}
    for ion in IONS_IN_THE_VOLTAGE_EQUATION:
        sensitivity = PUMP_CLAMPED_POOL_SENSITIVITY[ion]
        coefficients[(ion, "c")] = -sensitivity if ION_CHARGE[ion] > 0 else sensitivity
        coefficients[(ion, "e")] = 0.0
    total = sum(abs(value) for value in coefficients.values())
    return {key: ((math.copysign(1.0, value) if value else 0.0), abs(value) / total if total else 0.0)
            for key, value in coefficients.items()}
