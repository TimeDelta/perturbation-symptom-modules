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
# not the law. The pores_and_clamped_pools build of item 37 now calls the constants and weight functions below
# (graph/reactome_import.py); an earlier version of this comment said nothing did, which was true when it was
# written and stopped being true when the build was wired. The REGISTERED value membrane_potential_build is still
# item 35's computed_from_the_pools, under which calcium has neither route, and no graph carries item 37 yet.
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
    """Which way the ION moves through an open pore at rest: sign(z_i (V_rest - E_i)), decision 9.112 (c) as
    corrected by decision 9.129 (iii).

    Returns -1 for inward and +1 for outward. The item's draft of 8 November 2026 wrote the rule as
    sign(V_rest - E_i), corrected by decision 9.129 (iii) on 12 November 2026; that form is the
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


def leak_current_microamperes_per_square_centimetre(ion: str) -> float:
    """g_i |E_i - V_rest| in uA/cm2: the current one leak-sized conductance of this ion carries at rest, Na+ 2.702,
    K+ 1.576 and Cl- 0.221 at the registered constants. uS/cm2 times mV is nA/cm2, hence the 1e-3.

    It is the conversion between the two routes into VM_c (decision 9.129 (1)): a conductance edge weighs
    1/g_total times this current, and a pool edge in the same unit weighs the pool's millivolts per uA/cm2 times it.
    """
    return LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[ion] * abs(pore_driving_force_millivolts(ion)) * 1e-3


def clamped_pool_edge_weights() -> dict[tuple[str, str], tuple[float, float]]:
    """(ion, compartment letter) -> (sign, weight in millivolts) for the pool's edge into VM_c under amendment item 37.

    This replaces driving_force_edge_weights() for the pores_and_clamped_pools build, which graph/reactome_import.py
    calls. No committed graph carries it: the registered membrane_potential_build is still item 35's
    computed_from_the_pools.

    The cytosolic weight is c_i S_i g_i |E_i - V_rest| (decision 9.129 (1), the owner, 12 November 2026), in
    magnitude Na+ 1.306, K+ 0.094 and Cl- 0.896 mV:

    - c_i is item 35's coefficient, millivolts per unit fractional change in the pool;
    - S_i is the pump-clamped pool sensitivity, d ln[ion]_i per uA/cm2 of sustained current, so c_i S_i is
      millivolts per uA/cm2 (Na+ -0.4835, K+ -0.0595, Cl- +4.0479). The sensitivity alone would be a concentration
      change and not a potential change, which is how a first version of this function went wrong;
    - g_i |E_i - V_rest| is one leak-sized current of that ion (leak_current_microamperes_per_square_centimetre),
      which puts the edge in the unit a conductance edge carries: "millivolts for a 100 per cent change of one
      leak-sized unit". A conductance edge is 1/g_total = 9.09 mV times the same current.

    What every version before 12 November 2026 did, as history: the products c_i S_i were rescaled to sum to 1 in
    absolute value (0.105, 0.013, 0.882), on the ground that the graph carries no units. That held while the pools
    were VM_c's only inputs and not once millivolt-weighted conductance edges shared its row: the rescale gave every
    pool the chloride leak's current by accident, leaving the sodium pool edge 12.4 times too small and the potassium
    one 7.2 times against a pore of its own ion. Rescaling both routes together to sum to 1 is not done either,
    because it makes the chloride pores net depolarising once the changes_ion_pool gain exceeds 0.21.

    The three extracellular pools take weight 0 at the registered steady-state readout (decision 9.112's first
    sub-question, ruled 7 November 2026; their closed-space values and clearance times are kept for decision 9.118, and
    the pools stay as inputs).

    The signs come from item 35's coefficient, the sensitivities and currents being magnitudes: more cytosolic sodium
    or potassium lowers the pool's contribution to the potential, and chloride is the reverse because its charge is
    negative.
    """
    item_35_coefficients = driving_force_coefficients_millivolts()
    weights: dict[tuple[str, str], tuple[float, float]] = {}
    for ion in IONS_IN_THE_VOLTAGE_EQUATION:
        millivolts_per_unit_current = PUMP_CLAMPED_POOL_SENSITIVITY[ion] * item_35_coefficients[(ion, "c")]
        weights[(ion, "c")] = (math.copysign(1.0, millivolts_per_unit_current),
                               abs(millivolts_per_unit_current) * leak_current_microamperes_per_square_centimetre(ion))
        weights[(ion, "e")] = (0.0, 0.0)
    return weights


# The mixed-cation pores of amendment item 37's sub-ruling of 7 November 2026: one conductance edge per pore at its
# own reversal potential, with the permeability ratio read from a source where one exists. The ratios are the values
# reconciled by the Fable pass of 6 November 2026 (docs/membrane_potential_constants.md, "Added 6 November 2026"),
# which corrected two of the 5 November readings: neuronal nicotinic to -2.1 mV and NALCN to +2.2 mV. Each entry is
# {ion: permeability}, in arbitrary units since only the ratios enter; "assumed" in the comment marks a ratio no
# source states, which the item carries as a stated assumption rather than a reading.
MIXED_PORE_PERMEABILITIES: dict[str, dict[str, float]] = {
    "nicotinic, neuronal": {"Na+": 1.0, "K+": 1.2},       # Haghighi and Cooper 2000, P_K/P_Na 1.2
    "nicotinic, muscle": {"Na+": 1.0, "K+": 1.1},         # Adams, Dwyer and Hille 1980
    "AMPA": {"Na+": 1.0, "K+": 1.0 / 0.88},               # Jonas and Sakmann 1992, P_Na/P_Cs 0.88
    "kainate": {"Na+": 1.0, "K+": 1.0 / 0.88},            # treated as the edited AMPA case
    "NMDA": {"Na+": 1.0, "K+": 1.0},                      # P_K = P_Na assumed; Mayer and Westbrook 1987 give P_Ca/P_Na
    "5-HT3": {"Na+": 1.0, "K+": 1.10},                    # Yang 1990, P_K/P_Na 1.10
    "P2X": {"Na+": 1.0, "K+": 1.0},                       # Evans et al. 1996, P_K/P_Na 1.0
    "TRPM4/5": {"Na+": 1.0, "K+": 1.0},                   # P_K = P_Na assumed; Launay et al. 2002 state no ratio
    "NALCN": {"Na+": 1.0, "K+": 1.0},                      # Ren 2011, equally permeable to Na+ and K+
    "HCN": {"Na+": 0.35, "K+": 1.0},                      # Macri et al. 2012, P_Na/P_K 0.35
    "Nav": {"Na+": 1.0, "K+": 1.0 / 12.0},                # Hille 1972, P_K/P_Na 1/12; the single-ion check
}


def ghk_current_per_unit_permeability(ion: str, voltage_millivolts: float) -> float:
    """The GHK current of one ion at unit permeability, in arbitrary units (the common F^2/RT factor is dropped).

    Monovalent form, as the registered constants are: the reversal potentials of item 37 carry no divalent term, which
    is why calcium takes a conductance edge of its own at its measured resting conductance instead of entering a
    mixed pore's reversal potential. Only ratios between ions enter the weight below, so the dropped factor and the
    millimolar units cancel.
    """
    charge = ION_CHARGE[ion]
    reduced_voltage = charge * voltage_millivolts / thermal_voltage_millivolts()
    inside, outside = RESTING_CONCENTRATION_MILLIMOLAR[(ion, "c")], RESTING_CONCENTRATION_MILLIMOLAR[(ion, "e")]
    return charge * reduced_voltage * (inside - outside * math.exp(-reduced_voltage)) / (1.0 - math.exp(-reduced_voltage))


def chord_conductance_per_unit_permeability(ion: str) -> float:
    """The ion's GHK chord conductance at rest per unit permeability: 3.10241 for Na+, 0.59768 for K+, 0.70108 for Cl-.

    A chord conductance is the current divided by the driving force, I_i / (V_rest - E_i), so these say how much
    conductance one unit of permeability buys at rest. Sodium buys five times what potassium does, because at rest the
    sodium driving force is large and the potassium one is small.
    """
    return (ghk_current_per_unit_permeability(ion, resting_potential_millivolts())
            / (resting_potential_millivolts() - nernst_potential_millivolts(ion)))


def mixed_pore_reversal_potential_millivolts(permeability: dict[str, float]) -> float:
    """The pore's reversal potential by the GHK voltage equation over monovalent ions, chloride reversed.

    Chloride enters with its concentrations exchanged, which is the standard form for an anion: its inside
    concentration sits in the numerator. No divalent term, as above.
    """
    numerator = sum(share * RESTING_CONCENTRATION_MILLIMOLAR[(ion, "e" if ION_CHARGE[ion] > 0 else "c")]
                    for ion, share in permeability.items())
    denominator = sum(share * RESTING_CONCENTRATION_MILLIMOLAR[(ion, "c" if ION_CHARGE[ion] > 0 else "e")]
                      for ion, share in permeability.items())
    return thermal_voltage_millivolts() * math.log(numerator / denominator)


def mixed_pore_conductance_microsiemens_per_square_centimetre(permeability: dict[str, float]) -> float:
    """The pore's resting conductance: its chord-conductance shares used to apportion the registered leak conductances.

    This is the normalisation that fixes the absolute scale, and the one phrase
    docs/membrane_potential_constants.md leaves out when it calls the rule "the chord-conductance sum". A chord
    conductance is proportional to permeability, and a permeability ratio fixes no absolute scale, so something must.
    What the 6 November 2026 arithmetic did, recovered by derivation on 9 November 2026 and checked against all eleven
    of its recorded weights to within 0.005 mV, is this: scale the permeabilities so the pore's total chord
    conductance is one unit, then let each ion's share of that unit be worth that ion's registered LEAK conductance.

    So the mixed pore is modelled as a chord-share blend of item 37's single-ion pores, and the single-ion terms are
    its endpoints by construction: a pure sodium pore returns 20 uS/cm2 and weighs 24.56 mV, a pure potassium pore 70
    and 14.32 mV. That blend is a modelling choice and not a reading, and it is stated here because it cannot be
    recovered from the record's wording.
    """
    weighted = {ion: share * chord_conductance_per_unit_permeability(ion) for ion, share in permeability.items()}
    total = sum(weighted.values())
    return sum((value / total) * LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[ion]
               for ion, value in weighted.items())


def mixed_pore_weight_millivolts(permeability: dict[str, float]) -> float:
    """The pore's conductance-edge weight: g_pore |E_rev - V_rest| / g_total, in millivolts.

    Reproduces every weight docs/membrane_potential_constants.md records: neuronal nicotinic 18.83, NALCN, NMDA, P2X
    and TRPM4/5 19.09, AMPA and kainate 18.91, muscle nicotinic and 5-HT3 18.95, HCN 17.06 and 15.45, Nav 22.77.

    **A limitation this rule carries, measured 9 November 2026.** The single edge at E_rev and the per-ion split it
    implies (sum over ions of g_i (E_i - V_rest) / g_total) do not agree, because reweighting the GHK chord shares by
    the leak conductances breaks the identity that would make the two equal and the product then mixes two models.
    They are within 4 to 8 per cent for the pores whose E_rev is near 0 mV and 5 per cent for Nav, but 37 per cent
    apart for HCN at P_Na/P_K 0.35 (17.06 against 10.76) and 56 per cent at 0.23 (15.45 against 6.84). The sub-ruling
    of 7 November 2026 chose the single edge, so that is the built quantity, and no sign changes either way. The
    record states the HCN pair of numbers without treating the divergence as a question; it is one, and it belongs
    with the per-cell-class work that decision 9.112's chloride question also needs.
    """
    return (mixed_pore_conductance_microsiemens_per_square_centimetre(permeability)
            * abs(mixed_pore_reversal_potential_millivolts(permeability) - resting_potential_millivolts())
            / total_resting_conductance_microsiemens_per_square_centimetre())


# Which mixed-cation pore class a channel gene belongs to, by gene-symbol prefix, first match winning. The classes
# are MIXED_PORE_PERMEABILITIES' keys; a gene that matches none is not a mixed pore and is read by the single-ion
# rule instead. The prefixes follow the families of experiments/audit_channel_conduction.py, split where the
# permeability table distinguishes what that script lumps: it has one "ionotropic glutamate (AMPA, kainate, NMDA,
# delta)" family, and GRIA, GRIK and GRIN are three classes here with two different weights.
#
# Checked by a Fable pass on 9 November 2026 against UniProtKB reviewed human entries and Alexander et al., Concise
# Guide to PHARMACOLOGY 2023/24: Ion channels (PMC11339754). Every prefix was confirmed except the two below.
#
# **CHRNA1 and CHRNB1 sit in the wrong class here, and correcting the table alone would make the build worse.** The
# alpha1 and beta1 subunits assemble the MUSCLE receptor (UniProt P02708 and P11230, "Pentamer of two alpha chains,
# and one each of the beta, delta, and gamma (in immature muscle) or epsilon (in mature muscle) chains"; the Concise
# Guide's junctional stoichiometry "(alpha1)2beta1deltaepsilon"). But graph/reactome_import.py gives a reaction the
# class of its first catalyst gene in sorted order, and Reactome's nicotinic entities mix muscle and neuronal
# subunits. Measured on the v5 graph, 9 November 2026: RCT_622326 and RCT_629595 are each decided by CHRNA1 while
# every other member of each is neuronal, so moving CHRNA1 would flip two overwhelmingly neuronal reactions from
# 18.83 to 18.95 mV on an alphabetical accident; and "nicotinic, muscle" is selected by NO v5 reaction either way,
# since CHRND, CHRNE and CHRNG occur only in RCT_622325, where CHRNA3 sorts first. The repair belongs to the
# selection rule rather than to this table, and it is the owner's to make. CHRNB1 catalyses nothing in v5, so moving
# it alone would change nothing. Recorded here rather than silently corrected.
#
# The delta glutamate receptors (GRID1, GRID2) are absent, and that absence stands, but the reason once given for it
# does not: whether GluD conducts is **contested**. Against: the Concise Guide, "They do not form a functional
# receptor when expressed solely, or in combination with other ionotropic glutamate receptor subunits, in transfected
# cells", and Itoh et al. 2024 (PMC11295041). For: Carrillo et al. 2021 (PMC8694607), "the GluD2 subtype of delta
# receptor forms cation-selective channels when bound to cerebellin-1 and neurexin-1beta", and Wang et al. 2025
# (PMC12520249), "Here we define GluDs as ligand-gated ion channels", measuring 30.7 pS for purified human GluD2. No
# monovalent permeability ratio was read for wild-type GluD, so no class could carry a sourced value even if one were
# wanted; GRID2 catalyses no reaction in v5 and GRID1 is not a node, so nothing built turns on it.
#
# Also recorded by that pass and deliberately not guarded, being a stated choice rather than an accident: SCN7A (Nax)
# takes the NALCN class through the curated reaction MAR_SODIUM_LEAK it shares with NALCN, which is consistent with
# Noland et al. 2022 (PMC8931054) finding the Nax construct "non-selective among monovalent cations".
NOT_MIXED_PORE_GENES: frozenset[str] = frozenset({"GRINA"})

MIXED_PORE_GENE_PREFIXES: tuple[tuple[str, str], ...] = (
    ("CHRNA", "nicotinic, neuronal"), ("CHRNB", "nicotinic, neuronal"),
    ("CHRND", "nicotinic, muscle"), ("CHRNE", "nicotinic, muscle"), ("CHRNG", "nicotinic, muscle"),
    ("GRIA", "AMPA"), ("GRIK", "kainate"), ("GRIN", "NMDA"),
    ("HTR3", "5-HT3"), ("P2RX", "P2X"),
    ("TRPM4", "TRPM4/5"), ("TRPM5", "TRPM4/5"),
    ("NALCN", "NALCN"), ("HCN", "HCN"),
    ("SCN1A", "Nav"), ("SCN2A", "Nav"), ("SCN3A", "Nav"), ("SCN4A", "Nav"), ("SCN5A", "Nav"),
    ("SCN8A", "Nav"), ("SCN9A", "Nav"), ("SCN10A", "Nav"), ("SCN11A", "Nav"),
)


def mixed_pore_class_of_gene(gene_symbol: str) -> str | None:
    """The mixed-cation pore class a gene belongs to, or None when it is not one of them.

    CHRNA7 is neuronal nicotinic, GRIN2B is NMDA, SCN1A is Nav. A potassium or chloride channel gene returns None and
    takes the single-ion route, which is right: its pore carries one ion and its weight is that ion's.
    """
    symbol = str(gene_symbol).upper()
    if symbol in NOT_MIXED_PORE_GENES:
        return None
    for prefix, pore_class in MIXED_PORE_GENE_PREFIXES:
        if symbol.startswith(prefix):
            return pore_class
    return None


def single_ion_pore_conductance_microsiemens_per_square_centimetre(ion: str) -> float:
    """The resting conductance a pore permeable to this ion alone is given: its leak conductance, and for calcium its
    measured resting conductance.

    Why the leak values and not a per-pore measurement: the project holds no conductance for an individual channel,
    and the record's ruled single-ion terms (Na+ 24.6, K+ 14.3, Cl- 2.0 mV) are these values, which is also what makes
    them the endpoints of the mixed-pore rule. So every single-ion pore of one ion carries the same weight, and what
    distinguishes two sodium channels in the graph is which reactions they catalyse and what gates them, not their
    conductance. That is a limitation of the build and not of the law.
    """
    if ion == "Ca2+":
        return CALCIUM_RESTING_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE
    return LEAK_CONDUCTANCE_MICROSIEMENS_PER_SQUARE_CENTIMETRE[ion]


def conductance_edge_for_a_pore(ion: str | None, pore_class: str | None) -> tuple[float, float, str]:
    """(sign, weight in mV, evidence) of a pore's conductance edge into VM_c, for amendment item 37.

    A pore_class names a mixed-cation pore and takes precedence: its weight comes from its own reversal potential.
    Otherwise the pore carries one ion and takes that ion's term. Raises when neither is given, so a caller cannot
    make an edge for a reaction it has not classified.
    """
    if pore_class is not None:
        permeability = MIXED_PORE_PERMEABILITIES[pore_class]
        reversal = mixed_pore_reversal_potential_millivolts(permeability)
        return (math.copysign(1.0, reversal - resting_potential_millivolts()),
                mixed_pore_weight_millivolts(permeability),
                f"conductance of a mixed-cation pore at its own reversal potential, {pore_class} "
                f"(E_rev {reversal:+.1f} mV; docs/membrane_potential_constants.md)")
    if ion is None:
        raise ValueError("a conductance edge needs either an ion or a mixed-cation pore class")
    conductance = single_ion_pore_conductance_microsiemens_per_square_centimetre(ion)
    return (pore_conductance_edge_sign(ion), pore_conductance_weight_millivolts(ion, conductance),
            f"conductance of a pore permeable to {ion} alone, g |E - V_rest| / g_total "
            f"(E {nernst_potential_millivolts(ion):+.1f} mV; docs/membrane_potential_constants.md)")
