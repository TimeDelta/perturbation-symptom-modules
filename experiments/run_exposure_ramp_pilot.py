"""The planted-network half of item 40 (7)'s pilot (decision 9.153): "a pilot on a small planted network, with one
branch of a bistable switch and one oscillating loop, checking that the ramp, the fold jump and the oscillation rule
behave as written". An engineering measurement on planted fixtures; nothing here interprets a result for a decision.

What it runs. The readout of mechanistic_pathway_learning/models/exposure_ramp.py (item 40 (1) to (5) on a generic
update map) on three planted networks, each checked against a reference computed apart from the ramp:

1. **The switch** (planted_bistable_switch): two nodes that activate each other, the drug entering the first. It is
   bistable at rest, so the ramp starts on the lower branch, and the lower branch ends at a fold inside the ramp. The
   reference is the scalar fixed-point equation of the entry node, a = S(w S(w a) + u), whose roots are found on a
   fine grid and refined by bisection (switch_scalar_roots), and the fold's exposure, found by bisection on the number
   of roots (switch_fold_fraction). Checked: the ramp reads the lowest root before the fold and the highest after it,
   the fold flag is raised at the first level past the fold and at no other, and every level settles.
2. **The loop** (planted_oscillating_loop): three nodes in a ring, two activating edges and one inhibiting, the drug
   entering the first. The reference is the equilibrium (the loop has one) and the onset of oscillation: under the ODE
   dh/dt = F(h, u) - h where the leading eigenvalue of the Jacobian of F crosses real part 1 (ode_hopf_fraction), and
   under the stepped relaxation where the step's spectral radius crosses 1 (relaxation_onset_fraction), with the ODE's
   limit cycle integrated by scipy's solve_ivp and its centre read on a fine time grid (ode_cycle_centre). Checked: the
   levels below the stepped onset settle and those above it are flagged oscillating; at each oscillating level,
   whether Anderson mixing converged on the equilibrium inside the cycle and was rejected by the stability probe; and
   the centre read, beside the equilibrium and the ODE's centre. The same loop is run at each of
   --comparison-step-sizes, so the record shows how the onset and the centre move with the step size.
3. **The combined network** (planted_combined_network): the switch and the loop side by side, one drug reaching both,
   with a head of three symptoms chosen so that they peak at different levels. Checked: each symptom's prediction is
   its highest logit over the levels read, there is one adjoint solve per distinct settled peak level and one cycle
   unrolled per distinct oscillating one. A level is flagged oscillating as a whole, so a symptom that reads the
   settled switch can peak at a level where only the loop oscillates; its gradient there is a finding, below.

The gradients (item 40 (4)), each by central finite differences of size --finite-difference-step:

- checked: the implicit gradient at a settled peak level against finite differences of the whole readout (ramp and
  maximum), on the switch and on the combined network;
- checked, on the loop: the unrolled-cycle gradient against finite differences of the centre unrolled from the same
  detached first state over the same number of steps, which is what backpropagating through the cycle's steps
  computes where no node's highest or lowest value is tied between steps;
- recorded and not judged: the unrolled-cycle gradient against finite differences of the whole readout, where the
  first state of the cycle is itself re-solved, the gap being what the one-cycle gradient leaves out (the dependence
  through the relaxation that led to the cycle); the same two comparisons for the combined network's switch symptom
  at its oscillating peak, where the switch's nodes do not move over the cycle (unrolled_cycle_centre); and a profile
  of the whole readout of the loop's inhibitor symptom at --profile-points values on each side of one edge weight,
  --profile-step apart, beside the centre from the same first state (whole_readout_profile).

Timing, on the planted networks only (item 40 (7) times one level and one cycle on the confirmatory graph, which waits
on the v5 rebuild): one warm-started settled level, one oscillating level, and one unrolled cycle with its backward
pass, each the median of --timing-repeats runs. Planted timings say nothing about the confirmatory graph.

**The planted values** (PLANTED_SWITCH, PLANTED_LOOP, PLANTED_COMBINED) are test values, chosen so that the switch is
bistable at rest with its fold inside the ramp and the loop oscillates in the upper half of it. They are not sourced,
not registered and not physiology. The saturation (soft_saturation) is a stand-in, not 37f's form, which item 37f
leaves as "soft (Michaelis-Menten or Hill)": S(x) = (1 + H) / (1 + H exp(-n x)) - 1, a floor at -1 (37f (2)), a
ceiling at the headroom H and S(0) = 0, which is (1 + H) times the Hill function a^n / (H + a^n) of the input activity
a = exp(x), less 1. A bistable switch needs a sigmoid response, which this has where H > 1; the results hold for these
fixtures only.

What it leaves to the caller, because no ruling settles it, each a required argument with no default: every setting
of ExposureRampSettings (the step size, Anderson mixing's memory, regularization and cap, the settle tolerance and the
relaxation's cap, the probe steps, the fold test's state-match tolerance, the cycle tolerance and cap, the adjoint
solve's tolerance and cap, the warm start after an oscillating level), the number of levels, whether rest is read, the
step sizes compared, the finite-difference step and the relative agreement the gradient checks are passed at, the
profile's spacing and number of values, the ODE reference's integration tolerance, settling time and reading time, and
the timing repeats.

It writes one JSON file, refused under the repository's data/ directory.

Usage, from the repository root:
  PYTHONPATH=. python experiments/run_exposure_ramp_pilot.py --number-of-levels 10 --rest-is-read no \\
      --step-size 0.02 --comparison-step-sizes 0.5 0.1 0.05 0.02 0.01 --anderson-memory 5 \\
      --anderson-regularization 0 --anderson-iteration-cap 2000 --settle-tolerance 1e-11 \\
      --relaxation-iteration-cap 60000 --stability-probe-steps 400 --state-match-tolerance 1e-4 \\
      --cycle-tolerance 1e-2 --cycle-iteration-cap 40000 --adjoint-tolerance 1e-11 --adjoint-iteration-cap 100000 \\
      --warm-start-after-oscillation last_relaxation_state --finite-difference-step 1e-6 \\
      --gradient-agreement-tolerance 1e-4 --profile-step 1e-6 --profile-points 5 --ode-tolerance 1e-10 \\
      --ode-settling-time 3000 --ode-reading-time 200 --timing-repeats 5 --output <path outside data/>
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import os
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

from mechanistic_pathway_learning.models.exposure_ramp import (
    OSCILLATING,
    SETTLED,
    ExposureRamp,
    ExposureRampSettings,
    exposure_fractions,
    largest_absolute_entry,
    read_symptom_peaks,
    run_exposure_ramp,
    solve_level,
    unrolled_cycle_centre,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = REPOSITORY_ROOT / "data"
DTYPE = torch.float64

# The planted values (module docstring): test values, not sourced, not registered, not physiology.
PLANTED_SWITCH = {"headroom": 9.0, "steepness": 1.0, "loop_weight": 0.6, "full_entry_input": 1.0}
PLANTED_LOOP = {"headroom": 9.0, "steepness": 1.0, "loop_weight": 1.5, "full_entry_input": 3.0}
# the combined network: the switch entered more strongly, so that its fold falls before the loop's onset, and a head
# whose three symptoms read the switch's partner node, the loop's inhibiting node, and the switch's entry node less its
# partner (which falls when the switch jumps, so it peaks before the fold)
PLANTED_COMBINED = {"switch_full_entry_input": 1.3, "loop_full_entry_input": 3.0,
                    "symptom_names": ("switch_partner_high", "loop_inhibitor_high", "switch_entry_over_partner"),
                    "head_weights": ((0.0, 1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0, 1.0), (1.0, -1.0, 0.0, 0.0, 0.0)),
                    "head_bias": (0.0, 0.0, 0.0)}


# ---------------------------------------------------------------- the planted fixtures


def soft_saturation(summed_input: torch.Tensor, headroom: torch.Tensor, steepness: torch.Tensor) -> torch.Tensor:
    """The fixtures' stand-in saturation (module docstring): floor -1, ceiling the headroom, 0 at 0."""
    return (1.0 + headroom) / (1.0 + headroom * torch.exp(-steepness * summed_input)) - 1.0


@dataclasses.dataclass(frozen=True)
class PlantedNetwork:
    """A planted network: h <- S(W h + u) node by node (edge_weights[target, source]), and a linear head
    head_weights h + head_bias giving one logit per symptom. full_exposure is the input u at the full exposure."""

    node_names: tuple[str, ...]
    edge_weights: torch.Tensor
    headroom: torch.Tensor
    steepness: torch.Tensor
    full_exposure: torch.Tensor
    head_weights: torch.Tensor
    head_bias: torch.Tensor
    symptom_names: tuple[str, ...]

    def update_map(self, state: torch.Tensor, exposure_input: torch.Tensor) -> torch.Tensor:
        return soft_saturation(self.edge_weights @ state + exposure_input, self.headroom, self.steepness)

    def head(self, state: torch.Tensor) -> torch.Tensor:
        return self.head_weights @ state + self.head_bias

    @property
    def rest_state(self) -> torch.Tensor:
        return torch.zeros(len(self.node_names), dtype=DTYPE)

    def with_entry(self, parameter: str, index: tuple[int, ...], change: float) -> "PlantedNetwork":
        """A copy with one entry of one parameter (edge_weights, full_exposure, head_weights, head_bias) moved by
        change, for finite differences."""
        moved = getattr(self, parameter).detach().clone()
        moved[index] += change
        return dataclasses.replace(self, **{parameter: moved})

    def differentiable(self) -> "PlantedNetwork":
        """A copy whose parameters are fresh leaves that require gradients."""
        return dataclasses.replace(self, **{name: getattr(self, name).detach().clone().requires_grad_(True)
                                            for name in ("edge_weights", "full_exposure", "head_weights", "head_bias")})


def _tensor(values) -> torch.Tensor:
    return torch.tensor(values, dtype=DTYPE)


def planted_bistable_switch(*, headroom: float, steepness: float, loop_weight: float, full_entry_input: float) -> PlantedNetwork:
    """Two nodes that activate each other with one weight; the drug enters the first. The head reads each node as one
    symptom."""
    edge_weights = _tensor([[0.0, loop_weight], [loop_weight, 0.0]])
    return PlantedNetwork(("switch_entry", "switch_partner"), edge_weights, _tensor([headroom] * 2),
                          _tensor([steepness] * 2), _tensor([full_entry_input, 0.0]), torch.eye(2, dtype=DTYPE),
                          torch.zeros(2, dtype=DTYPE), ("switch_entry_high", "switch_partner_high"))


def planted_oscillating_loop(*, headroom: float, steepness: float, loop_weight: float, full_entry_input: float) -> PlantedNetwork:
    """Three nodes in a ring: the entry activates the middle node, the middle node activates the inhibitor, and the
    inhibitor inhibits the entry, each edge of the one weight in size; the drug enters the first. The head reads each
    node as one symptom."""
    edge_weights = torch.zeros(3, 3, dtype=DTYPE)
    edge_weights[1, 0] = loop_weight
    edge_weights[2, 1] = loop_weight
    edge_weights[0, 2] = -loop_weight
    return PlantedNetwork(("loop_entry", "loop_middle", "loop_inhibitor"), edge_weights, _tensor([headroom] * 3),
                          _tensor([steepness] * 3), _tensor([full_entry_input, 0.0, 0.0]), torch.eye(3, dtype=DTYPE),
                          torch.zeros(3, dtype=DTYPE), ("loop_entry_high", "loop_middle_high", "loop_inhibitor_high"))


def planted_combined_network(*, switch: PlantedNetwork, loop: PlantedNetwork, switch_full_entry_input: float,
                             loop_full_entry_input: float, head_weights, head_bias, symptom_names) -> PlantedNetwork:
    """The switch and the loop side by side (no edge between them), one drug entering both entry nodes, with a head
    over the five nodes (switch nodes first)."""
    nodes = switch.node_names + loop.node_names
    edge_weights = torch.block_diag(switch.edge_weights, loop.edge_weights)
    full_exposure = torch.zeros(len(nodes), dtype=DTYPE)
    full_exposure[0] = switch_full_entry_input
    full_exposure[len(switch.node_names)] = loop_full_entry_input
    return PlantedNetwork(nodes, edge_weights, torch.cat([switch.headroom, loop.headroom]),
                          torch.cat([switch.steepness, loop.steepness]), full_exposure, _tensor(head_weights),
                          _tensor(head_bias), tuple(symptom_names))


def planted_networks() -> dict[str, PlantedNetwork]:
    switch = planted_bistable_switch(**PLANTED_SWITCH)
    loop = planted_oscillating_loop(**PLANTED_LOOP)
    combined = planted_combined_network(switch=switch, loop=loop, **PLANTED_COMBINED)
    return {"switch": switch, "loop": loop, "combined": combined}


# ---------------------------------------------------------------- references computed apart from the ramp


def _saturation_numpy(x, headroom: float, steepness: float):
    return (1.0 + headroom) / (1.0 + headroom * np.exp(-steepness * x)) - 1.0


def switch_scalar_roots(*, headroom: float, steepness: float, loop_weight: float, entry_input: float,
                        grid_points: int = 200001) -> list[tuple[float, float]]:
    """Every steady state of the switch at one entry input, as (entry, partner) pairs in increasing order: the roots
    of a = S(w S(w a) + u) - which the switch's steady states satisfy, the partner being S(w a) - located on a grid over
    the open range (-1, headroom) of the entry node and refined by bisection. The grid size is the reference's own
    resolution, not a setting of the ramp."""
    def residual(entry):
        return _saturation_numpy(loop_weight * _saturation_numpy(loop_weight * entry, headroom, steepness) + entry_input,
                                 headroom, steepness) - entry

    grid = np.linspace(-1.0 + 1e-12, headroom - 1e-12, grid_points)
    values = residual(grid)
    roots = []
    for index in np.nonzero(np.sign(values[:-1]) * np.sign(values[1:]) <= 0)[0]:
        low, high = grid[index], grid[index + 1]
        if values[index] == 0.0:
            roots.append(low)
            continue
        for _ in range(200):
            middle = 0.5 * (low + high)
            if np.sign(residual(middle)) == np.sign(residual(low)):
                low = middle
            else:
                high = middle
        roots.append(0.5 * (low + high))
    unique = []
    for root in sorted(roots):
        if not unique or root - unique[-1] > 1e-9:
            unique.append(root)
    return [(float(root), float(_saturation_numpy(loop_weight * root, headroom, steepness))) for root in unique]


def switch_fold_fraction(*, headroom: float, steepness: float, loop_weight: float, full_entry_input: float,
                         bisection_steps: int = 60) -> float | None:
    """The fraction of the full exposure at which the switch's lower branch ends (the number of steady states drops
    from three to one), by bisection; None where the switch is not bistable at rest or the fold lies past the ramp."""
    def root_count(fraction):
        return len(switch_scalar_roots(headroom=headroom, steepness=steepness, loop_weight=loop_weight,
                                       entry_input=fraction * full_entry_input))

    if root_count(0.0) < 3 or root_count(1.0) > 1:
        return None
    low, high = 0.0, 1.0
    for _ in range(bisection_steps):
        middle = 0.5 * (low + high)
        if root_count(middle) >= 3:
            low = middle
        else:
            high = middle
    return 0.5 * (low + high)


def network_jacobian(network: PlantedNetwork, state: torch.Tensor, exposure_input: torch.Tensor) -> np.ndarray:
    """The Jacobian of the update map at a state, dense (the planted networks are small)."""
    return torch.autograd.functional.jacobian(lambda h: network.update_map(h, exposure_input.detach()),
                                              state.detach()).numpy()


def loop_equilibrium(network: PlantedNetwork, exposure_input: torch.Tensor, newton_tolerance: float = 1e-14) -> torch.Tensor:
    """The loop's equilibrium (a ring with one inhibiting edge has one) by Newton's method from rest on the dense
    Jacobian; the tolerance is the reference's own."""
    state = torch.zeros(len(network.node_names), dtype=DTYPE)
    for _ in range(200):
        residual = (network.update_map(state, exposure_input) - state).detach()
        if largest_absolute_entry(residual) <= newton_tolerance:
            return state
        jacobian = network_jacobian(network, state, exposure_input)
        step = np.linalg.solve(jacobian - np.eye(len(state)), -residual.numpy())
        state = state + torch.from_numpy(step)
    raise RuntimeError("Newton's method did not find the loop's equilibrium")


def _bisect_onset(network: PlantedNetwork, criterion, bisection_steps: int = 60) -> float | None:
    """The smallest fraction of the full exposure at which criterion(jacobian at the equilibrium) turns positive,
    assuming it changes sign once along the ramp; None where it does not change sign between 0 and 1."""
    def value(fraction):
        exposure_input = fraction * network.full_exposure.detach()
        return criterion(network_jacobian(network, loop_equilibrium(network, exposure_input), exposure_input))

    if value(0.0) >= 0.0 or value(1.0) <= 0.0:
        return None
    low, high = 0.0, 1.0
    for _ in range(bisection_steps):
        middle = 0.5 * (low + high)
        if value(middle) > 0.0:
            high = middle
        else:
            low = middle
    return 0.5 * (low + high)


def ode_hopf_fraction(network: PlantedNetwork) -> float | None:
    """Where the equilibrium of dh/dt = F(h, u) - h loses stability: the largest real part of the eigenvalues of the
    Jacobian of F crosses 1."""
    return _bisect_onset(network, lambda jacobian: float(np.linalg.eigvals(jacobian).real.max()) - 1.0)


def relaxation_onset_fraction(network: PlantedNetwork, step_size: float) -> float | None:
    """Where the equilibrium stops being one the stepped relaxation settles on: the spectral radius of
    I + step_size (J - I) crosses 1."""
    def criterion(jacobian):
        step_jacobian = np.eye(len(jacobian)) + step_size * (jacobian - np.eye(len(jacobian)))
        return float(np.abs(np.linalg.eigvals(step_jacobian)).max()) - 1.0

    return _bisect_onset(network, criterion)


def ode_cycle_centre(network: PlantedNetwork, exposure_input: torch.Tensor, *, tolerance: float, settling_time: float,
                     reading_time: float, reading_points: int = 200001) -> dict:
    """The ODE dh/dt = F(h, u) - h integrated by solve_ivp (DOP853) from just off the equilibrium for settling_time,
    then over reading_time, read on a grid of reading_points: each node's highest and lowest value and the centre,
    halfway between. A range below 1e-6 is reported as no oscillation (the ODE settled)."""
    from scipy.integrate import solve_ivp

    weights = network.edge_weights.detach().numpy()
    headroom = network.headroom.detach().numpy()
    steepness = network.steepness.detach().numpy()
    entry = exposure_input.detach().numpy()

    def derivative(_time, state):
        return _saturation_numpy(weights @ state + entry, headroom, steepness) - state

    start = loop_equilibrium(network, exposure_input).numpy() + 1e-3
    settled = solve_ivp(derivative, (0.0, settling_time), start, method="DOP853", rtol=tolerance, atol=tolerance)
    times = np.linspace(0.0, reading_time, reading_points)
    reading = solve_ivp(derivative, (0.0, reading_time), settled.y[:, -1], method="DOP853", rtol=tolerance,
                        atol=tolerance, t_eval=times)
    highest, lowest = reading.y.max(axis=1), reading.y.min(axis=1)
    oscillates = bool((highest - lowest).max() > 1e-6)
    return {"oscillates": oscillates, "highest": highest.tolist(), "lowest": lowest.tolist(),
            "centre": (0.5 * (highest + lowest)).tolist()}


# ---------------------------------------------------------------- the checks


def settings_from_arguments(arguments: argparse.Namespace, step_size: float | None = None) -> ExposureRampSettings:
    return ExposureRampSettings(
        step_size=arguments.step_size if step_size is None else step_size, anderson_memory=arguments.anderson_memory,
        anderson_regularization=arguments.anderson_regularization, anderson_iteration_cap=arguments.anderson_iteration_cap,
        settle_tolerance=arguments.settle_tolerance, relaxation_iteration_cap=arguments.relaxation_iteration_cap,
        stability_probe_steps=arguments.stability_probe_steps, state_match_tolerance=arguments.state_match_tolerance,
        cycle_tolerance=arguments.cycle_tolerance, cycle_iteration_cap=arguments.cycle_iteration_cap,
        adjoint_tolerance=arguments.adjoint_tolerance, adjoint_iteration_cap=arguments.adjoint_iteration_cap,
        warm_start_after_oscillation=arguments.warm_start_after_oscillation)


def ramp_for(network: PlantedNetwork, fractions, settings: ExposureRampSettings) -> ExposureRamp:
    return run_exposure_ramp(network.update_map, network.rest_state, network.full_exposure, fractions, settings)


def _rounded(values, digits: int = 6):
    return [round(float(value), digits) for value in torch.as_tensor(values).reshape(-1).tolist()]


def level_table(ramp: ExposureRamp) -> list[dict]:
    """Every level visited, rest first, as the record prints it."""
    rows = []
    for index, level in enumerate(ramp.levels):
        row = {"level_index": index, "exposure_fraction": round(level.exposure_fraction, 6), "kind": level.kind,
               "read": index in ramp.read_level_indices, "solver": level.solver, "map_evaluations": level.map_evaluations,
               "state_or_centre": _rounded(level.state), "growth_rate": None if level.growth_rate is None else round(level.growth_rate, 6),
               "anderson_rejection": level.anderson_rejection, "fold_jump": level.fold_jump,
               "anderson_disagreed": level.anderson_disagreed}
        if level.anderson_state is not None:
            row["anderson_state"] = _rounded(level.anderson_state)
            row["anderson_growth_rate"] = round(level.anderson_growth_rate, 6)
        if level.cycle is not None:
            row["cycle_length"] = level.cycle.length
            row["cycle_highest"] = _rounded(level.cycle.highest)
            row["cycle_lowest"] = _rounded(level.cycle.lowest)
            row["cycle_change_from_previous_cycle"] = level.cycle.change_from_previous_cycle
        rows.append(row)
    return rows


def check_switch(network: PlantedNetwork, fractions, settings: ExposureRampSettings) -> dict:
    """Check 1 (module docstring): the branch from rest, the fold flag and the jump, against the scalar reference."""
    ramp = ramp_for(network, fractions, settings)
    fold = switch_fold_fraction(**PLANTED_SWITCH)
    rows = level_table(ramp)
    agreements = []
    for index, level in enumerate(ramp.levels[1:], start=1):
        roots = switch_scalar_roots(headroom=PLANTED_SWITCH["headroom"], steepness=PLANTED_SWITCH["steepness"],
                                    loop_weight=PLANTED_SWITCH["loop_weight"],
                                    entry_input=level.exposure_fraction * PLANTED_SWITCH["full_entry_input"])
        expected = roots[0] if fold is None or level.exposure_fraction < fold else roots[-1]
        distance = largest_absolute_entry(level.state - _tensor(expected))
        agreements.append({"level_index": index, "steady_states_at_this_input": len(roots),
                           "expected_branch": "lowest" if expected == roots[0] else "highest",
                           "distance_from_expected": distance})
    first_past_fold = next((index for index, level in enumerate(ramp.levels) if fold is not None
                            and level.exposure_fraction > fold), None)
    passed = (all(level.kind == SETTLED for level in ramp.levels)
              and ramp.fold_levels == ((first_past_fold,) if first_past_fold is not None else ())
              and all(entry["distance_from_expected"] <= 10 * settings.state_match_tolerance for entry in agreements))
    return {"fold_fraction_reference": fold, "first_level_past_the_fold": first_past_fold, "fold_levels": list(ramp.fold_levels),
            "levels": rows, "agreement_with_reference": agreements, "passed": passed}


def check_loop(network: PlantedNetwork, fractions, settings: ExposureRampSettings, ode_settings: dict) -> dict:
    """Check 2 (module docstring): which levels settle and which oscillate, against the onset of the stepped
    relaxation, with the Anderson candidate, the equilibrium and the ODE's centre at each oscillating level."""
    ramp = ramp_for(network, fractions, settings)
    onset = relaxation_onset_fraction(network, settings.step_size)
    rows = level_table(ramp)
    for row, level in zip(rows, ramp.levels):
        exposure_input = level.exposure_fraction * network.full_exposure.detach()
        equilibrium = loop_equilibrium(network, exposure_input)
        row["equilibrium"] = _rounded(equilibrium)
        if level.kind == OSCILLATING:
            row["anderson_landed_on_the_equilibrium"] = (level.anderson_state is not None and
                                                         largest_absolute_entry(level.anderson_state - equilibrium) <= 1e-6)
            row["ode_reference"] = ode_cycle_centre(network, exposure_input, **ode_settings)
    expected_kinds = [SETTLED if onset is None or level.exposure_fraction < onset else OSCILLATING for level in ramp.levels]
    passed = [level.kind for level in ramp.levels] == expected_kinds
    return {"relaxation_onset_fraction_reference": onset, "ode_hopf_fraction_reference": ode_hopf_fraction(network),
            "oscillating_levels": list(ramp.oscillating_levels), "levels": rows, "passed": passed}


def check_step_size_dependence(network: PlantedNetwork, fractions, arguments: argparse.Namespace, ode_settings: dict) -> dict:
    """The loop at each compared step size: where its rest stops being one the relaxation settles on, the stepped
    onset, the first oscillating level, and the centre read at the full exposure, beside the ODE's."""
    ode_full = ode_cycle_centre(network, network.full_exposure, **ode_settings)
    rows = []
    for step_size in arguments.comparison_step_sizes:
        settings = settings_from_arguments(arguments, step_size)
        row = {"step_size": step_size, "relaxation_onset_fraction": relaxation_onset_fraction(network, step_size)}
        try:
            ramp = ramp_for(network, fractions, settings)
        except ValueError as refusal:
            row["refused"] = str(refusal)
            rows.append(row)
            continue
        full = ramp.levels[-1]
        row.update({"oscillating_levels": list(ramp.oscillating_levels), "unresolved_levels": list(ramp.unresolved_levels),
                    "full_level_kind": full.kind, "full_level_state_or_centre": _rounded(full.state),
                    "full_level_cycle_length": None if full.cycle is None else full.cycle.length,
                    "full_level_distance_from_ode_centre": largest_absolute_entry(full.state - _tensor(ode_full["centre"]))})
        rows.append(row)
    return {"ode_hopf_fraction": ode_hopf_fraction(network), "ode_centre_at_full_exposure": ode_full, "by_step_size": rows}


def readout_value(network: PlantedNetwork, fractions, settings: ExposureRampSettings) -> torch.Tensor:
    """The whole readout, ramp and maximum, without gradients: what finite differences of the prediction difference."""
    ramp = ramp_for(network, fractions, settings)
    return read_symptom_peaks(ramp, network.update_map, network.head).prediction.detach()


def gradient_of_prediction(network: PlantedNetwork, fractions, settings: ExposureRampSettings, symptom: int):
    """The readout's gradient of one symptom's prediction, by the module's backward pass, with the peak level and the
    record of the solves."""
    differentiable = network.differentiable()
    ramp = ramp_for(differentiable, fractions, settings)
    peaks = read_symptom_peaks(ramp, differentiable.update_map, differentiable.head)
    peaks.prediction[symptom].backward()
    gradients = {name: getattr(differentiable, name).grad for name in ("edge_weights", "full_exposure", "head_weights", "head_bias")}
    return gradients, peaks, ramp


def _relative_gap(analytic: float, numeric: float) -> float:
    return abs(analytic - numeric) / max(abs(analytic), abs(numeric), 1e-12)


def check_implicit_gradient(network: PlantedNetwork, fractions, settings: ExposureRampSettings, symptom: int,
                            entries, step: float, agreement: float) -> dict:
    """The implicit gradient at a settled peak level against central differences of the whole readout."""
    gradients, peaks, ramp = gradient_of_prediction(network, fractions, settings, symptom)
    peak = peaks.peak_level_indices[symptom]
    rows = []
    for parameter, index in entries:
        forward = readout_value(network.with_entry(parameter, index, step), fractions, settings)[symptom]
        backward = readout_value(network.with_entry(parameter, index, -step), fractions, settings)[symptom]
        numeric = float(forward - backward) / (2 * step)
        analytic = float(gradients[parameter][index])
        rows.append({"parameter": parameter, "index": list(index), "backward_pass": analytic, "finite_difference": numeric,
                     "relative_gap": _relative_gap(analytic, numeric)})
    return {"symptom": network.symptom_names[symptom], "peak_level_index": peak, "peak_level_kind": ramp.levels[peak].kind,
            "peak_exposure_fraction": ramp.levels[peak].exposure_fraction, "adjoint_solves": peaks.gradient_record.adjoint_solves,
            "entries": rows, "passed": ramp.levels[peak].kind == SETTLED and all(row["relative_gap"] <= agreement for row in rows)}


def check_unrolled_gradient(network: PlantedNetwork, fractions, settings: ExposureRampSettings, symptom: int, entries,
                            step: float, agreement: float) -> dict:
    """The unrolled-cycle gradient at an oscillating peak level, against central differences of (a) the centre
    unrolled from the same detached first state over the same steps, which the backward pass computes wherever no
    node's highest or lowest value over the cycle is tied between steps, and (b) the whole readout, the gap to which is
    recorded and not judged. matches_same_first_state says whether (a) agreed; the nodes that do not move over the cycle
    are listed, since their highest and lowest values tie (unrolled_cycle_centre)."""
    gradients, peaks, ramp = gradient_of_prediction(network, fractions, settings, symptom)
    peak = peaks.peak_level_indices[symptom]
    level = ramp.levels[peak]
    if level.kind != OSCILLATING:
        return {"symptom": network.symptom_names[symptom], "peak_level_index": peak, "peak_level_kind": level.kind,
                "matches_same_first_state": False, "note": "the symptom does not peak at an oscillating level"}
    start, length = level.cycle.start_state, level.cycle.length

    def fixed_start_value(moved: PlantedNetwork) -> float:
        with torch.no_grad():
            centre = unrolled_cycle_centre(moved.update_map, start, level.exposure_fraction * moved.full_exposure, length,
                                           settings.step_size)
            return float(moved.head(centre)[symptom])

    rows = []
    for parameter, index in entries:
        fixed = (fixed_start_value(network.with_entry(parameter, index, step))
                 - fixed_start_value(network.with_entry(parameter, index, -step))) / (2 * step)
        whole = float(readout_value(network.with_entry(parameter, index, step), fractions, settings)[symptom]
                      - readout_value(network.with_entry(parameter, index, -step), fractions, settings)[symptom]) / (2 * step)
        analytic = float(gradients[parameter][index])
        rows.append({"parameter": parameter, "index": list(index), "backward_pass": analytic,
                     "finite_difference_same_first_state": fixed, "relative_gap_same_first_state": _relative_gap(analytic, fixed),
                     "finite_difference_whole_readout": whole, "relative_gap_whole_readout": _relative_gap(analytic, whole)})
    constant = [network.node_names[node] for node in range(len(network.node_names))
                if float(level.cycle.highest[node]) == float(level.cycle.lowest[node])]
    return {"symptom": network.symptom_names[symptom], "peak_level_index": peak, "peak_level_kind": level.kind,
            "peak_exposure_fraction": level.exposure_fraction, "cycle_length": length,
            "nodes_that_do_not_move_over_the_cycle": constant, "unrolled_cycles": peaks.gradient_record.unrolled_cycles,
            "entries": rows, "matches_same_first_state": all(row["relative_gap_same_first_state"] <= agreement for row in rows)}


def whole_readout_profile(network: PlantedNetwork, fractions, settings: ExposureRampSettings, symptom: int,
                          parameter: str, index: tuple[int, ...], step: float, points: int) -> dict:
    """One symptom's prediction from the whole readout, and its centre unrolled from the peak level's cycle start
    (detached) over the same steps, at the parameter moved by k * step for k = -points..points: whether each is a
    smooth function of the parameter at that scale, which the record reads off the values."""
    ramp = ramp_for(network, fractions, settings)
    peak = read_symptom_peaks(ramp, network.update_map, network.head).peak_level_indices[symptom]
    level = ramp.levels[peak]
    rows = []
    for offset in range(-points, points + 1):
        moved = network.with_entry(parameter, index, offset * step)
        row = {"offset": offset * step, "whole_readout": float(readout_value(moved, fractions, settings)[symptom])}
        if level.kind == OSCILLATING:
            with torch.no_grad():
                centre = unrolled_cycle_centre(moved.update_map, level.cycle.start_state,
                                               level.exposure_fraction * moved.full_exposure, level.cycle.length,
                                               settings.step_size)
            row["same_first_state"] = float(moved.head(centre)[symptom])
        rows.append(row)
    return {"symptom": network.symptom_names[symptom], "parameter": parameter, "index": list(index),
            "peak_level_index": peak, "peak_level_kind": level.kind, "step": step, "values": rows}


def check_combined(network: PlantedNetwork, fractions, settings: ExposureRampSettings) -> dict:
    """Check 3 (module docstring): the per-symptom maximum, and one solve per distinct peak level."""
    differentiable = network.differentiable()
    ramp = ramp_for(differentiable, fractions, settings)
    peaks = read_symptom_peaks(ramp, differentiable.update_map, differentiable.head)
    peaks.prediction.sum().backward()
    logits = peaks.logits_by_level
    maxima_match = bool(torch.allclose(peaks.prediction.detach(), logits.max(dim=0).values, atol=10 * settings.settle_tolerance))
    settled_peaks = [index for index in peaks.distinct_peak_levels if ramp.levels[index].kind == SETTLED]
    oscillating_peaks = [index for index in peaks.distinct_peak_levels if ramp.levels[index].kind == OSCILLATING]
    solves_match = (sorted(solve["level_index"] for solve in peaks.gradient_record.adjoint_solves) == settled_peaks
                    and sorted(cycle["level_index"] for cycle in peaks.gradient_record.unrolled_cycles) == oscillating_peaks)
    return {"symptoms": list(network.symptom_names), "levels": level_table(ramp), "read_level_indices": list(ramp.read_level_indices),
            "logits_by_read_level": [_rounded(row) for row in logits], "prediction": _rounded(peaks.prediction.detach()),
            "peak_level_indices": list(peaks.peak_level_indices), "distinct_peak_levels": list(peaks.distinct_peak_levels),
            "adjoint_solves": peaks.gradient_record.adjoint_solves, "unrolled_cycles": peaks.gradient_record.unrolled_cycles,
            "fold_levels": list(ramp.fold_levels), "oscillating_levels": list(ramp.oscillating_levels),
            "passed": maxima_match and solves_match and len(peaks.distinct_peak_levels) > 1}


def _median_seconds(function, repeats: int) -> float:
    durations = []
    for _ in range(repeats):
        started = time.perf_counter()
        function()
        durations.append(time.perf_counter() - started)
    return statistics.median(durations)


def planted_timings(networks: dict[str, PlantedNetwork], fractions, settings: ExposureRampSettings, repeats: int) -> dict:
    """One warm-started settled level (the switch's full level, from the level before), one oscillating level (the
    loop's full level, from the level before), and one unrolled cycle with its backward pass (the loop's full level),
    each the median of repeats runs, in seconds; planted networks only (module docstring)."""
    timings = {"repeats": repeats, "torch_threads": torch.get_num_threads()}
    for name, label in (("switch", "warm_started_settled_level_seconds"), ("loop", "warm_started_oscillating_level_seconds")):
        network = networks[name]
        ramp = ramp_for(network, fractions, settings)
        timings[label] = _median_seconds(lambda: solve_level(network.update_map, ramp.levels[-2], ramp.levels[-1].exposure_fraction,
                                                             network.full_exposure, settings), repeats)
        timings[label.replace("_seconds", "_kind")] = ramp.levels[-1].kind
    loop = networks["loop"]
    ramp = ramp_for(loop, fractions, settings)
    level = ramp.levels[-1]
    if level.kind == OSCILLATING:
        def unrolled_cycle_with_backward():
            differentiable = loop.differentiable()
            centre = unrolled_cycle_centre(differentiable.update_map, level.cycle.start_state,
                                           level.exposure_fraction * differentiable.full_exposure, level.cycle.length,
                                           settings.step_size)
            differentiable.head(centre).sum().backward()

        timings["unrolled_cycle_with_backward_seconds"] = _median_seconds(unrolled_cycle_with_backward, repeats)
        timings["unrolled_cycle_length"] = level.cycle.length
    return timings


# ---------------------------------------------------------------- the command line


def refuse_output_under_data(output: Path) -> None:
    """This script writes nothing into data/ (module docstring): refused under the repository's data/ as written, as
    resolved, and under the target of any link inside it (a worktree links data/raw and data/processed to the main
    checkout's data/)."""
    roots = {Path(os.path.abspath(DATA_DIRECTORY)), DATA_DIRECTORY.resolve()}
    if DATA_DIRECTORY.is_dir():
        for child in DATA_DIRECTORY.iterdir():
            if child.is_symlink():
                target = child.resolve()
                roots.update({target, target.parent})
    candidates = {Path(os.path.abspath(output)), output.resolve()}
    for root in roots:
        for candidate in candidates:
            if candidate == root or root in candidate.parents:
                raise SystemExit(f"refusing to write under {root}: this script writes nothing into data/")


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    required = parser.add_argument_group("required, each with no default (module docstring)")
    required.add_argument("--number-of-levels", type=int, required=True)
    required.add_argument("--rest-is-read", choices=("yes", "no"), required=True)
    required.add_argument("--step-size", type=float, required=True)
    required.add_argument("--comparison-step-sizes", type=float, nargs="+", required=True)
    required.add_argument("--anderson-memory", type=int, required=True)
    required.add_argument("--anderson-regularization", type=float, required=True)
    required.add_argument("--anderson-iteration-cap", type=int, required=True)
    required.add_argument("--settle-tolerance", type=float, required=True)
    required.add_argument("--relaxation-iteration-cap", type=int, required=True)
    required.add_argument("--stability-probe-steps", type=int, required=True)
    required.add_argument("--state-match-tolerance", type=float, required=True)
    required.add_argument("--cycle-tolerance", type=float, required=True)
    required.add_argument("--cycle-iteration-cap", type=int, required=True)
    required.add_argument("--adjoint-tolerance", type=float, required=True)
    required.add_argument("--adjoint-iteration-cap", type=int, required=True)
    required.add_argument("--warm-start-after-oscillation", choices=("last_relaxation_state", "cycle_centre"), required=True)
    required.add_argument("--finite-difference-step", type=float, required=True)
    required.add_argument("--gradient-agreement-tolerance", type=float, required=True,
                          help="the relative gap at which a gradient check that should match exactly is passed")
    required.add_argument("--profile-step", type=float, required=True,
                          help="the spacing of the parameter values the whole readout's profile is taken at")
    required.add_argument("--profile-points", type=int, required=True, help="the profile's values on each side")
    required.add_argument("--ode-tolerance", type=float, required=True)
    required.add_argument("--ode-settling-time", type=float, required=True)
    required.add_argument("--ode-reading-time", type=float, required=True)
    required.add_argument("--timing-repeats", type=int, required=True)
    required.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def run_pilot(arguments: argparse.Namespace) -> dict:
    settings = settings_from_arguments(arguments)
    fractions = exposure_fractions(arguments.number_of_levels, arguments.rest_is_read == "yes")
    ode_settings = {"tolerance": arguments.ode_tolerance, "settling_time": arguments.ode_settling_time,
                    "reading_time": arguments.ode_reading_time}
    networks = planted_networks()
    step, agreement = arguments.finite_difference_step, arguments.gradient_agreement_tolerance
    switch, loop, combined = networks["switch"], networks["loop"], networks["combined"]
    edge_entries_switch = [("edge_weights", (0, 1)), ("edge_weights", (1, 0)), ("full_exposure", (0,))]
    edge_entries_loop = [("edge_weights", (1, 0)), ("edge_weights", (2, 1)), ("edge_weights", (0, 2)), ("full_exposure", (0,))]
    # the switch block's entries, whose derivatives are not zero; the unrolled check adds one loop edge (loop_middle to
    # loop_inhibitor), through which the switch's symptoms have no route, so its derivative is zero exactly
    edge_entries_combined = [("edge_weights", (0, 1)), ("edge_weights", (1, 0)), ("full_exposure", (0,))]
    edge_entries_combined_unrolled = edge_entries_combined + [("edge_weights", (4, 3))]
    results = {
        "switch": check_switch(switch, fractions, settings),
        "loop": check_loop(loop, fractions, settings, ode_settings),
        "step_size_dependence": check_step_size_dependence(loop, fractions, arguments, ode_settings),
        "combined": check_combined(combined, fractions, settings),
        "gradients": {
            "implicit_switch_partner_at_its_peak":
                check_implicit_gradient(switch, fractions, settings, 1, edge_entries_switch, step, agreement),
            "implicit_combined_entry_over_partner_at_its_peak":
                check_implicit_gradient(combined, fractions, settings, 2, edge_entries_combined, step, agreement),
            "unrolled_loop_inhibitor_at_its_peak":
                check_unrolled_gradient(loop, fractions, settings, 2, edge_entries_loop, step, agreement),
            "unrolled_combined_switch_partner_at_its_peak":
                check_unrolled_gradient(combined, fractions, settings, 0, edge_entries_combined_unrolled, step, agreement),
        },
        "whole_readout_profile_loop_inhibitor": whole_readout_profile(loop, fractions, settings, 2, "edge_weights", (1, 0),
                                                                      arguments.profile_step, arguments.profile_points),
        "timings_planted_only": planted_timings(networks, fractions, settings, arguments.timing_repeats),
    }
    return results


def main(argv: list[str] | None = None) -> None:
    arguments = parse_arguments(argv)
    refuse_output_under_data(arguments.output)
    torch.set_num_threads(1)
    started = datetime.now(timezone.utc)
    results = run_pilot(arguments)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT, capture_output=True, text=True).stdout.strip()
    # whether the code this run executed differs from that commit: the two files the pilot runs
    uncommitted = subprocess.run(["git", "status", "--porcelain", "--", "experiments/run_exposure_ramp_pilot.py",
                                  "mechanistic_pathway_learning/models/exposure_ramp.py"], cwd=REPOSITORY_ROOT,
                                 capture_output=True, text=True).stdout.strip()
    document = {"what": "item 40 (7)'s pilot on planted networks (experiments/run_exposure_ramp_pilot.py)",
                "measured": started.isoformat(timespec="seconds"), "commit": commit,
                "code_differs_from_commit": bool(uncommitted), "torch": torch.__version__,
                "graph": "planted networks only (PLANTED_SWITCH, PLANTED_LOOP, PLANTED_COMBINED); no graph build",
                "arguments": {key: (str(value) if isinstance(value, Path) else value) for key, value in vars(arguments).items()},
                "planted_values": {"switch": PLANTED_SWITCH, "loop": PLANTED_LOOP,
                                   "combined": {key: (list(value) if isinstance(value, tuple) else value)
                                                for key, value in PLANTED_COMBINED.items()}},
                "results": results,
                # the checks that must hold by construction; the combined network's unrolled gradient and the whole
                # readout's finite differences at an oscillating level are findings, recorded and not judged
                "checks_passed": {"switch": results["switch"]["passed"], "loop": results["loop"]["passed"],
                                  "combined": results["combined"]["passed"],
                                  **{name: check["passed"] for name, check in results["gradients"].items()
                                     if name.startswith("implicit_")},
                                  "unrolled_loop_inhibitor_at_its_peak":
                                      results["gradients"]["unrolled_loop_inhibitor_at_its_peak"]["matches_same_first_state"]}}
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(document, indent=1, default=lambda value: None if value is None or
                                           (isinstance(value, float) and math.isnan(value)) else str(value)) + "\n")
    print(json.dumps(document["checks_passed"], indent=1))


if __name__ == "__main__":
    main()
