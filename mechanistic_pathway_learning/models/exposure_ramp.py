"""Amendment item 40's exposure-ramp readout (decision 9.153) on a generic update map: a prototype for the pilot of
item 40 (7), standing apart from the encoder and the trainer.

What it is, and what it is not. Item 40 replaces 37f (7)'s readout: a perturbation's prediction is "each symptom's
highest logit along the steady states a perturbation passes through as its exposure rises from rest". Item 40 is
registered and not built; decision 9.153's status reads "not built: it is built with 37f's encoder; owed before the
build: the pilot of item 40 (7)". This module implements rules (1) to (5) of item 40 on any update map F(h, u), so that
the pilot can check, on a small planted network, "that the ramp, the fold jump and the oscillation rule behave as
written". It is not the registered build: nothing in mechanistic_pathway_learning/models/linear_response_encoder.py or
in the trainer (experiments/run_main_model.py) calls it, 37f's encoder (saturation inside the loop, the floor, the
headroom) does not exist yet, and the planted networks of experiments/run_exposure_ramp_pilot.py are test fixtures.

The relaxation. A state h is a node's deviation from rest, and F(h, u) is one application of the update map at the
input u. The relaxation is dh/dt = F(h, u) - h under equal response rates (item 40, "Why the peak over iteration
rounds is not used"), stepped forward as h <- h + step_size * (F(h, u) - h); a step of 0.5 is the damped iteration the
linear-response encoder runs today. A steady state is a fixed point h = F(h, u).

The rules, each as item 40 writes it (docs/preregistration.md, item 40) and how it is implemented here:

(1) **The ramp.** "A drug perturbation is raised from 0 to its full exposure in levels evenly spaced in the input's
    own units"; "At each level the steady state is solved from the previous level's steady state, so the states read
    are the branch continued from rest." exposure_fractions gives the levels k / N of the full input, k = 1..N; the
    state at exposure 0 is the rest state the caller supplies, checked to settle there. A gene or allele perturbation
    "has no ramp: it is read at its full level alone, the steady state of 37f reached from rest", which is
    run_exposure_ramp with lifelong_perturbation_fractions(). **Left to the caller, because item 40 does not say:**
    whether rest itself is one of the levels the maximum is taken over (rest_is_read, required). Item 40 says the
    levels run "from 0" and also that a gene perturbation is read "at its full level alone", and the two readings of
    "from 0" differ whenever a drug lowers a symptom's logit at every level above rest.
(2) **The readout.** "Each symptom's prediction is its highest logit over the levels, taken hard, so the gradient flows
    through the level that attains it." read_symptom_peaks takes the argmax per symptom over the levels read and
    differentiates the logit at that level alone.
(4) **The solver.** "At each level the unclamped relaxation [...] runs from the previous level's state, accelerated by
    Anderson mixing." anderson_fixed_point mixes the relaxation's steps (with memory 0 it is the plain relaxation).
    "**Stable** means the relaxation settles on the state": Anderson mixing is a quasi-Newton method and can converge
    on a fixed point the relaxation itself moves away from, so a state Anderson mixing returns is kept only when the
    linearized relaxation contracts at it (relaxation_growth_rate below 1); otherwise, or when Anderson mixing does not
    converge, the plain relaxation is run from the same warm start, and a state it settles on is stable by that
    definition. "**A fold**: where the branch from rest ends at a fold, the next level's relaxation lands on another
    stable state; the jump is what the dynamics do, and it is kept and flagged": after two consecutive settled levels
    the relaxation at the earlier level's input is run from the later state, and if it settles more than
    state_match_tolerance away from the earlier state, the system was bistable at the earlier level and the ramp moved
    from one stable state to the other, which is a fold of the branch from rest between the two levels; where Anderson
    mixing produced the landing, it is then confirmed by the plain relaxation from the earlier state (the definition),
    whose state is kept if the two differ, and the level is flagged. The test finds a fold only where the system is
    still bistable at the earlier level's input: a fold whose bistable range lies wholly between two levels is crossed,
    and the jump kept, without the flag (tests/test_exposure_ramp.py pins it on a planted switch). "**A
    level that does not settle** (a sustained oscillation) is read at the centre of the oscillation, each node halfway
    between the highest and the lowest value it takes over one cycle [...] and flagged as oscillating": the plain
    relaxation is continued and recorded, one cycle is found by upward crossings of the midline of the node that
    varies most, and the cycle is accepted when every node's highest and lowest values over the last cycle match those
    of the cycle before within cycle_tolerance. The backward pass: "implicitly, with a matrix-free iterative solve, at
    the level where each symptom's maximum falls", one solve per distinct peak level (the solve is the adjoint system
    w = g + J^T w, relaxed with the same step and Anderson mixing, J^T applied by reverse-mode products); and "where a
    symptom's maximum falls on such a level, the gradient is taken by unrolling one cycle of the relaxation and
    backpropagating through its steps" (unrolled_cycle_centre, from the cycle's first state, detached, through the
    cycle's steps).
(5) **The branch from rest is read.** Only the states the ramp visits enter the prediction; no other steady state is
    searched for (decision 9.138's search is deferred).

Rule (3) is an assumption and a registered limitation, not a computation, and (6) and (7) concern the build and its
measurements; none is implemented here.

**What it leaves to the caller, because no ruling settles it, each a required argument with no default**
(ExposureRampSettings and the ramp's own arguments): the number of levels (item 40 (7) sets it by measured time on the
confirmatory graph, which waits on the v5 rebuild), whether rest is read, the relaxation's step size (item 40 names
the step size as one of the three things a peak over rounds would read, and fixes none), Anderson mixing's memory and
regularization, the settle tolerance, the iteration caps of Anderson mixing and of the plain relaxation, the number of
steps of the stability probe, the state-match tolerance of the fold test, the cycle tolerance and the cap on the
recorded relaxation, the adjoint solve's tolerance and cap, and where the next level starts after an oscillating one
(warm_start_after_oscillation: from the last state of the recorded relaxation, the state the dynamics hold when the
exposure rises, or from the cycle's centre, the state read; item 40 solves each level "from the previous level's
steady state" and an oscillating level has none). The
tolerance and the time budget of item 40 (7) are proposed for the owner with the pilot's measurements on the
confirmatory graph; nothing here proposes them.

**Not defined by item 40, and refused here rather than guessed:** a level that neither settles nor shows a cycle
within the caps (UNRESOLVED) has no reading, so read_symptom_peaks refuses a ramp that holds one. The fold test is not
evaluated where either of the two levels oscillates or is unresolved (its flag is None).

Norms are the largest absolute entry (each node within the tolerance). The probe direction of relaxation_growth_rate
is a fixed draw (PROBE_DIRECTION_SEED) so that runs repeat; it is not a model value.
"""
from __future__ import annotations

import dataclasses
import math
from collections.abc import Callable, Sequence

import torch

UpdateMap = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]
Head = Callable[[torch.Tensor], torch.Tensor]

SETTLED = "settled"
OSCILLATING = "oscillating"
UNRESOLVED = "unresolved"
LEVEL_KINDS = (SETTLED, OSCILLATING, UNRESOLVED)
SOLVED_BY_ANDERSON = "anderson mixing"
SOLVED_BY_PLAIN_RELAXATION = "plain relaxation"
GIVEN_AS_REST = "rest state given"
WARM_STARTS_AFTER_OSCILLATION = ("last_relaxation_state", "cycle_centre")
# the probe direction of relaxation_growth_rate: a fixed draw so that runs repeat (module docstring); not a model value
PROBE_DIRECTION_SEED = 0


def largest_absolute_entry(tensor: torch.Tensor) -> float:
    """The norm used throughout: the largest absolute entry, so a tolerance holds for every node."""
    return float(tensor.detach().abs().max()) if tensor.numel() else 0.0


@dataclasses.dataclass(frozen=True)
class ExposureRampSettings:
    """Every numerical setting of the ramp, each required (module docstring, "What it leaves to the caller").

    step_size: the relaxation's step, h <- h + step_size * (F(h, u) - h), in (0, 1]; also Anderson mixing's mixing
        parameter and the relaxation step of the adjoint solve.
    anderson_memory: how many earlier steps Anderson mixing combines with the current one (0 is the plain relaxation).
    anderson_regularization: added to the diagonal of the residuals' Gram matrix, relative to its largest diagonal
        entry, so that it does not swamp the system as the residuals shrink; zero or more.
    settle_tolerance: a state has settled when every node's residual |F(h, u) - h| is at most this.
    anderson_iteration_cap: the most map evaluations Anderson mixing makes in one settle attempt before the plain
        relaxation is run instead.
    relaxation_iteration_cap: the most map evaluations the plain relaxation makes in one settle attempt.
    stability_probe_steps: products with the linearized relaxation's transpose taken to estimate its growth rate;
        the estimate is the geometric mean growth over the second half; at least 2.
    state_match_tolerance: two settled states at one input are the same state when they differ by at most this (the
        fold test).
    cycle_tolerance: one cycle is accepted when every node's highest and lowest values over the last cycle match those
        over the cycle before within this.
    cycle_iteration_cap: the steps of plain relaxation recorded, after a settle attempt fails, to find a cycle in.
    adjoint_tolerance, adjoint_iteration_cap: the matrix-free adjoint solve's residual tolerance and cap.
    warm_start_after_oscillation: one of WARM_STARTS_AFTER_OSCILLATION.
    """

    step_size: float
    anderson_memory: int
    anderson_regularization: float
    settle_tolerance: float
    anderson_iteration_cap: int
    relaxation_iteration_cap: int
    stability_probe_steps: int
    state_match_tolerance: float
    cycle_tolerance: float
    cycle_iteration_cap: int
    adjoint_tolerance: float
    adjoint_iteration_cap: int
    warm_start_after_oscillation: str

    def __post_init__(self) -> None:
        if not 0.0 < self.step_size <= 1.0:
            raise ValueError("step_size must be in (0, 1]")
        if self.anderson_memory < 0 or int(self.anderson_memory) != self.anderson_memory:
            raise ValueError("anderson_memory must be a whole number, zero or more")
        if self.anderson_regularization < 0.0:
            raise ValueError("anderson_regularization must be zero or more")
        for name in ("settle_tolerance", "state_match_tolerance", "cycle_tolerance", "adjoint_tolerance"):
            if not getattr(self, name) > 0.0:
                raise ValueError(f"{name} must be positive")
        for name in ("anderson_iteration_cap", "relaxation_iteration_cap", "cycle_iteration_cap", "adjoint_iteration_cap"):
            if getattr(self, name) < 1 or int(getattr(self, name)) != getattr(self, name):
                raise ValueError(f"{name} must be a whole number, one or more")
        if self.stability_probe_steps < 2 or int(self.stability_probe_steps) != self.stability_probe_steps:
            raise ValueError("stability_probe_steps must be a whole number, two or more")
        if self.warm_start_after_oscillation not in WARM_STARTS_AFTER_OSCILLATION:
            raise ValueError(f"warm_start_after_oscillation must be one of {WARM_STARTS_AFTER_OSCILLATION}")


def exposure_fractions(number_of_levels: int, rest_is_read: bool) -> tuple[float, ...]:
    """Item 40 (1): the levels evenly spaced from 0 to the full exposure, as fractions of the full input.

    The levels solved are k / number_of_levels for k = 1..number_of_levels, the last being the full exposure. With
    rest_is_read the rest state (fraction 0) is also among the levels the maximum is taken over; whether it is, item 40
    does not say (module docstring, rule (1)), so the caller chooses."""
    if number_of_levels < 1 or int(number_of_levels) != number_of_levels:
        raise ValueError("number_of_levels must be a whole number, one or more")
    if not isinstance(rest_is_read, bool):
        raise ValueError("rest_is_read must be True or False")
    solved = tuple(level / number_of_levels for level in range(1, number_of_levels + 1))
    return ((0.0,) + solved) if rest_is_read else solved


def lifelong_perturbation_fractions() -> tuple[float, ...]:
    """Item 40 (1): a gene or allele perturbation "has no ramp: it is read at its full level alone, the steady state
    of 37f reached from rest"."""
    return (1.0,)


def relaxation_step(update_map: UpdateMap, state: torch.Tensor, exposure_input: torch.Tensor, step_size: float) -> torch.Tensor:
    """One step of the relaxation dh/dt = F(h, u) - h: h + step_size * (F(h, u) - h)."""
    return state + step_size * (update_map(state, exposure_input) - state)


@dataclasses.dataclass(frozen=True)
class FixedPointSolve:
    """The outcome of a fixed-point iteration: the last iterate, whether its residual met the tolerance, the map
    evaluations made, and its residual norm."""

    state: torch.Tensor
    converged: bool
    map_evaluations: int
    residual_norm: float


def anderson_fixed_point(fixed_point_map: Callable[[torch.Tensor], torch.Tensor], initial_state: torch.Tensor,
                         step_size: float, memory: int, regularization: float, tolerance: float,
                         iteration_cap: int) -> FixedPointSolve:
    """x = fixed_point_map(x) by Anderson mixing of the relaxation's steps (type II, the constrained least-squares
    form): with residuals r_i = f(x_i) - x_i over the last memory + 1 iterates, the coefficients a minimise
    |sum_i a_i r_i|^2 with sum_i a_i = 1, and x_next = sum_i a_i ((1 - step_size) x_i + step_size f(x_i)). With memory 0
    this is the plain relaxation x + step_size (f(x) - x). The regularization is relative (ExposureRampSettings).

    The iterate is returned as soon as its residual is at most the tolerance; after iteration_cap map evaluations
    without that, the last iterate is returned with converged False."""
    iterate = initial_state.detach().clone()
    iterates: list[torch.Tensor] = []
    map_values: list[torch.Tensor] = []
    residuals: list[torch.Tensor] = []
    residual_norm = math.inf
    for evaluation in range(1, iteration_cap + 1):
        value = fixed_point_map(iterate).detach()
        residual = value - iterate
        residual_norm = largest_absolute_entry(residual)
        if residual_norm <= tolerance:
            return FixedPointSolve(iterate, True, evaluation, residual_norm)
        if evaluation == iteration_cap:
            break
        iterates.append(iterate)
        map_values.append(value)
        residuals.append(residual)
        if len(residuals) > memory + 1:
            del iterates[0], map_values[0], residuals[0]
        if len(residuals) == 1:
            iterate = iterate + step_size * residual
            continue
        flattened = torch.stack([entry.reshape(-1) for entry in residuals])
        gram = flattened @ flattened.T
        gram = gram + regularization * float(gram.diagonal().max()) * torch.eye(len(residuals), dtype=gram.dtype, device=gram.device)
        ones = torch.ones(len(residuals), dtype=gram.dtype, device=gram.device)
        weights = torch.linalg.solve(gram, ones)
        coefficients = weights / weights.sum()
        mixed_iterates = torch.einsum("i,i...->...", coefficients, torch.stack(iterates))
        mixed_values = torch.einsum("i,i...->...", coefficients, torch.stack(map_values))
        iterate = (1.0 - step_size) * mixed_iterates + step_size * mixed_values
    return FixedPointSolve(iterate, False, iteration_cap, residual_norm)


def plain_relaxation(update_map: UpdateMap, initial_state: torch.Tensor, exposure_input: torch.Tensor, step_size: float,
                     tolerance: float, iteration_cap: int) -> FixedPointSolve:
    """The relaxation itself, unaccelerated, from initial_state until every node's residual is at most the tolerance
    or iteration_cap map evaluations have been made. A state it settles on is stable in item 40 (4)'s sense."""
    state = initial_state.detach().clone()
    residual_norm = math.inf
    for evaluation in range(1, iteration_cap + 1):
        residual = (update_map(state, exposure_input) - state).detach()
        residual_norm = largest_absolute_entry(residual)
        if residual_norm <= tolerance:
            return FixedPointSolve(state, True, evaluation, residual_norm)
        if evaluation == iteration_cap:
            break
        state = state + step_size * residual
    return FixedPointSolve(state, False, iteration_cap, residual_norm)


def _reverse_mode_jacobian_product(update_map: UpdateMap, state: torch.Tensor, exposure_input: torch.Tensor
                                   ) -> Callable[[torch.Tensor], torch.Tensor]:
    """v -> J^T v, J the Jacobian of F(., u) at state, by reverse-mode products on one recorded evaluation."""
    with torch.enable_grad():
        probe_state = state.detach().clone().requires_grad_(True)
        value = update_map(probe_state, exposure_input.detach())

    def product(vector: torch.Tensor) -> torch.Tensor:
        (gradient,) = torch.autograd.grad(value, probe_state, vector, retain_graph=True, allow_unused=True)
        return torch.zeros_like(vector) if gradient is None else gradient

    return product


def relaxation_growth_rate(update_map: UpdateMap, state: torch.Tensor, exposure_input: torch.Tensor, step_size: float,
                           probe_steps: int) -> float:
    """The growth per step of a small deviation under the linearized relaxation at state, matrix-free.

    The linearized step is I + step_size (J - I); its transpose has the same spectrum, so it is applied by reverse-mode
    products. From a fixed direction (PROBE_DIRECTION_SEED) it is applied probe_steps times, each product normalised,
    and the estimate is the geometric mean growth over the second half, after the first half has let the leading
    eigenvalue dominate. Below 1 the relaxation contracts at the state, so it settles there: stable in item 40 (4)'s
    sense. Above 1 a deviation grows, which at a fixed point is a state the relaxation moves away from (a saddle, or
    the equilibrium inside a cycle)."""
    if probe_steps < 2:
        raise ValueError("probe_steps must be two or more")
    transpose_product = _reverse_mode_jacobian_product(update_map, state, exposure_input)
    generator = torch.Generator().manual_seed(PROBE_DIRECTION_SEED)
    direction = torch.randn(state.shape, generator=generator, dtype=state.dtype).to(state.device)
    direction = direction / direction.norm()
    log_growths = []
    for _ in range(probe_steps):
        stepped = direction + step_size * (transpose_product(direction) - direction)
        size = float(stepped.norm())
        if size == 0.0:
            return 0.0
        log_growths.append(math.log(size))
        direction = stepped / size
    second_half = log_growths[probe_steps // 2:]
    return math.exp(sum(second_half) / len(second_half))


@dataclasses.dataclass(frozen=True)
class CycleReading:
    """One cycle of the relaxation: its first state, its length in steps, and each node's highest, lowest and centre
    (halfway between the two) over it; also the largest change of any node's highest or lowest value from the cycle
    before, which the acceptance test bounds by cycle_tolerance."""

    start_state: torch.Tensor
    length: int
    highest: torch.Tensor
    lowest: torch.Tensor
    centre: torch.Tensor
    change_from_previous_cycle: float


def find_cycle(trajectory: torch.Tensor, cycle_tolerance: float) -> CycleReading | None:
    """One cycle in a recorded relaxation (steps x the state's shape), or None when none is found.

    The node that varies most over the trajectory's second half is the section node; a cycle runs from one upward
    crossing of that node's midline (halfway between its highest and lowest values over the second half) to the next.
    The last full cycle is read and accepted when every node's highest and lowest values over it match those over the
    cycle before within cycle_tolerance; fewer than three crossings, or a mismatch, is no cycle. Where the cycle's
    period is not a whole number of steps, its length alternates between neighbouring whole numbers and the sampled
    extremes move from cycle to cycle; change_from_previous_cycle records by how much."""
    steps = trajectory.shape[0]
    flattened = trajectory.reshape(steps, -1)
    second_half = flattened[steps // 2:]
    ranges = second_half.max(dim=0).values - second_half.min(dim=0).values
    section_node = int(ranges.argmax())
    if float(ranges[section_node]) <= cycle_tolerance:
        return None
    section_values = flattened[:, section_node]
    midline = 0.5 * (float(second_half[:, section_node].max()) + float(second_half[:, section_node].min()))
    crossings = [step for step in range(1, steps) if float(section_values[step - 1]) < midline <= float(section_values[step])]
    if len(crossings) < 3:
        return None
    last_cycle = trajectory[crossings[-2]:crossings[-1]]
    cycle_before = trajectory[crossings[-3]:crossings[-2]]
    highest, lowest = last_cycle.max(dim=0).values, last_cycle.min(dim=0).values
    change = max(largest_absolute_entry(highest - cycle_before.max(dim=0).values),
                 largest_absolute_entry(lowest - cycle_before.min(dim=0).values))
    if change > cycle_tolerance:
        return None
    return CycleReading(start_state=trajectory[crossings[-2]].clone(), length=crossings[-1] - crossings[-2],
                        highest=highest, lowest=lowest, centre=0.5 * (highest + lowest), change_from_previous_cycle=change)


def record_relaxation(update_map: UpdateMap, initial_state: torch.Tensor, exposure_input: torch.Tensor, step_size: float,
                      steps: int) -> torch.Tensor:
    """The plain relaxation from initial_state for the given number of steps, every state kept (steps x shape), the
    first being initial_state."""
    states = [initial_state.detach().clone()]
    for _ in range(steps - 1):
        states.append(relaxation_step(update_map, states[-1], exposure_input, step_size).detach())
    return torch.stack(states)


@dataclasses.dataclass(frozen=True)
class LevelReading:
    """What the ramp holds at one level.

    kind is SETTLED (state is the steady state), OSCILLATING (state is the cycle's centre, item 40 (4)) or UNRESOLVED
    (neither within the caps; state is the last state of the recorded relaxation, and no reading is defined). solver
    says which iteration produced a settled state, and anderson_rejection why Anderson mixing's answer was not kept
    ("did not converge", "unstable": converged on a state the relaxation does not settle on), with the state it gave
    and that state's growth rate. growth_rate is the probe's estimate at a settled state. fold_jump is item 40 (4)'s
    fold flag (37f's bifurcation flag): True where the ramp moved to another stable state between the previous level
    and this one, False where the settle at the previous level's input, run from this level's state, lands back on the
    previous state (which misses a fold whose bistable range lies wholly between the two levels: module docstring,
    rule (4)), None where the test is not evaluated; anderson_disagreed is True where the fold test's confirmation by
    the plain relaxation landed elsewhere than Anderson mixing had, and the plain relaxation's state was kept. For an
    oscillating level, cycle holds the cycle read and last_relaxation_state the recorded relaxation's last state."""

    exposure_fraction: float
    kind: str
    state: torch.Tensor
    solver: str | None
    map_evaluations: int
    residual_norm: float
    growth_rate: float | None = None
    anderson_rejection: str | None = None
    anderson_state: torch.Tensor | None = None
    anderson_growth_rate: float | None = None
    fold_jump: bool | None = None
    anderson_disagreed: bool = False
    cycle: CycleReading | None = None
    last_relaxation_state: torch.Tensor | None = None

    def warm_start(self, settings: ExposureRampSettings) -> torch.Tensor:
        """The state the next level's solve starts from (item 40 (1); after an oscillating level, the caller's choice)."""
        if self.kind == OSCILLATING:
            if settings.warm_start_after_oscillation == "cycle_centre":
                return self.state
            return self.last_relaxation_state
        return self.state


@dataclasses.dataclass(frozen=True)
class _SettleAttempt:
    settled: bool
    state: torch.Tensor
    solver: str | None
    map_evaluations: int
    residual_norm: float
    growth_rate: float | None
    anderson_rejection: str | None
    anderson_state: torch.Tensor | None
    anderson_growth_rate: float | None


def _settle(update_map: UpdateMap, warm_start: torch.Tensor, exposure_input: torch.Tensor,
            settings: ExposureRampSettings) -> _SettleAttempt:
    """Anderson mixing from the warm start, kept if it converges on a state the relaxation contracts at; otherwise the
    plain relaxation from the same warm start (module docstring, rule (4))."""
    anderson = anderson_fixed_point(lambda state: update_map(state, exposure_input), warm_start, settings.step_size,
                                    settings.anderson_memory, settings.anderson_regularization, settings.settle_tolerance,
                                    settings.anderson_iteration_cap)
    evaluations = anderson.map_evaluations
    anderson_growth = None
    if anderson.converged:
        anderson_growth = relaxation_growth_rate(update_map, anderson.state, exposure_input, settings.step_size,
                                                 settings.stability_probe_steps)
        if anderson_growth < 1.0:
            return _SettleAttempt(True, anderson.state, SOLVED_BY_ANDERSON, evaluations, anderson.residual_norm,
                                  anderson_growth, None, None, None)
        rejection = "unstable"
    else:
        rejection = "did not converge"
    plain = plain_relaxation(update_map, warm_start, exposure_input, settings.step_size, settings.settle_tolerance,
                             settings.relaxation_iteration_cap)
    evaluations += plain.map_evaluations
    rejected_state = anderson.state if anderson.converged else None
    if plain.converged:
        growth = relaxation_growth_rate(update_map, plain.state, exposure_input, settings.step_size,
                                        settings.stability_probe_steps)
        return _SettleAttempt(True, plain.state, SOLVED_BY_PLAIN_RELAXATION, evaluations, plain.residual_norm, growth,
                              rejection, rejected_state, anderson_growth)
    return _SettleAttempt(False, plain.state, None, evaluations, plain.residual_norm, None, rejection, rejected_state,
                          anderson_growth)


def _fold_test(update_map: UpdateMap, previous: LevelReading, previous_input: torch.Tensor, current_state: torch.Tensor,
               settings: ExposureRampSettings) -> bool | None:
    """True where the relaxation at the previous level's input, run from the current state, settles on a state other
    than the previous one (the system was bistable there and the ramp moved between its stable states); None where it
    does not settle. False where it settles back on the previous state, which is also what happens where the system
    is not bistable at the previous input, so a fold whose bistable range lies wholly between the two levels is not
    found (module docstring, rule (4))."""
    back = _settle(update_map, current_state, previous_input, settings)
    if not back.settled:
        return None
    return largest_absolute_entry(back.state - previous.state) > settings.state_match_tolerance


def solve_level(update_map: UpdateMap, previous: LevelReading, exposure_fraction: float, full_exposure: torch.Tensor,
                settings: ExposureRampSettings) -> LevelReading:
    """One level of the ramp, solved from the previous level's state (module docstring, rules (1) and (4))."""
    with torch.no_grad():
        exposure_input = exposure_fraction * full_exposure.detach()
        previous_input = previous.exposure_fraction * full_exposure.detach()
        attempt = _settle(update_map, previous.warm_start(settings), exposure_input, settings)
        if attempt.settled:
            reading = LevelReading(exposure_fraction, SETTLED, attempt.state, attempt.solver, attempt.map_evaluations,
                                   attempt.residual_norm, attempt.growth_rate, attempt.anderson_rejection,
                                   attempt.anderson_state, attempt.anderson_growth_rate)
            if previous.kind != SETTLED:
                return reading
            jumped = _fold_test(update_map, previous, previous_input, reading.state, settings)
            if jumped and reading.solver == SOLVED_BY_ANDERSON:
                # the definition: does the plain relaxation from the previous state land where Anderson mixing did?
                confirmation = plain_relaxation(update_map, previous.state, exposure_input, settings.step_size,
                                                settings.settle_tolerance, settings.relaxation_iteration_cap)
                if confirmation.converged and largest_absolute_entry(confirmation.state - reading.state) > settings.state_match_tolerance:
                    growth = relaxation_growth_rate(update_map, confirmation.state, exposure_input, settings.step_size,
                                                    settings.stability_probe_steps)
                    reading = dataclasses.replace(reading, state=confirmation.state, solver=SOLVED_BY_PLAIN_RELAXATION,
                                                  map_evaluations=reading.map_evaluations + confirmation.map_evaluations,
                                                  residual_norm=confirmation.residual_norm, growth_rate=growth,
                                                  anderson_disagreed=True)
                    jumped = _fold_test(update_map, previous, previous_input, reading.state, settings)
            return dataclasses.replace(reading, fold_jump=jumped)
        trajectory = record_relaxation(update_map, attempt.state, exposure_input, settings.step_size,
                                       settings.cycle_iteration_cap)
        evaluations = attempt.map_evaluations + settings.cycle_iteration_cap - 1
        cycle = find_cycle(trajectory, settings.cycle_tolerance)
        if cycle is None:
            return LevelReading(exposure_fraction, UNRESOLVED, trajectory[-1], None, evaluations, attempt.residual_norm,
                                None, attempt.anderson_rejection, attempt.anderson_state, attempt.anderson_growth_rate,
                                last_relaxation_state=trajectory[-1])
        return LevelReading(exposure_fraction, OSCILLATING, cycle.centre, None, evaluations, attempt.residual_norm, None,
                            attempt.anderson_rejection, attempt.anderson_state, attempt.anderson_growth_rate,
                            cycle=cycle, last_relaxation_state=trajectory[-1])


def rest_reading(update_map: UpdateMap, rest_state: torch.Tensor, full_exposure: torch.Tensor,
                 settings: ExposureRampSettings) -> LevelReading:
    """The rest state at exposure 0, refused unless the relaxation settles on it there (residual within the settle
    tolerance and a growth rate below 1), since the ramp is "the branch continued from rest"."""
    with torch.no_grad():
        zero_input = 0.0 * full_exposure.detach()
        residual_norm = largest_absolute_entry(update_map(rest_state, zero_input) - rest_state)
        growth = relaxation_growth_rate(update_map, rest_state, zero_input, settings.step_size, settings.stability_probe_steps)
    if residual_norm > settings.settle_tolerance:
        raise ValueError(f"the rest state is not a steady state at exposure 0 (residual {residual_norm:.3g})")
    if growth >= 1.0:
        raise ValueError(f"the relaxation does not settle on the rest state at exposure 0 (growth rate {growth:.6g})")
    return LevelReading(0.0, SETTLED, rest_state.detach().clone(), GIVEN_AS_REST, 1, residual_norm, growth)


@dataclasses.dataclass(frozen=True)
class ExposureRamp:
    """The ramp of one perturbation: every level visited in order, rest first (levels[0], exposure 0), and which of
    them the readout reads (read_level_indices: all of them when rest is read, every level but rest otherwise)."""

    levels: tuple[LevelReading, ...]
    read_level_indices: tuple[int, ...]
    full_exposure: torch.Tensor
    settings: ExposureRampSettings

    @property
    def fold_levels(self) -> tuple[int, ...]:
        return tuple(index for index, level in enumerate(self.levels) if level.fold_jump)

    @property
    def oscillating_levels(self) -> tuple[int, ...]:
        return tuple(index for index, level in enumerate(self.levels) if level.kind == OSCILLATING)

    @property
    def unresolved_levels(self) -> tuple[int, ...]:
        return tuple(index for index, level in enumerate(self.levels) if level.kind == UNRESOLVED)


def run_exposure_ramp(update_map: UpdateMap, rest_state: torch.Tensor, full_exposure: torch.Tensor,
                      fractions: Sequence[float], settings: ExposureRampSettings) -> ExposureRamp:
    """Item 40 (1), (4) and (5): the levels solved in order from rest, each from the previous level's state.

    fractions is exposure_fractions(...) for a drug or lifelong_perturbation_fractions() for a gene or allele: strictly
    increasing, ending at 1, each in [0, 1]; a leading 0 means rest is read. full_exposure is the input at the full
    exposure, in the update map's input units."""
    fractions = tuple(float(fraction) for fraction in fractions)
    if not fractions or fractions[-1] != 1.0:
        raise ValueError("the levels must end at the full exposure, fraction 1")
    if any(not 0.0 <= fraction <= 1.0 for fraction in fractions) or any(b <= a for a, b in zip(fractions, fractions[1:])):
        raise ValueError("the fractions must be strictly increasing within [0, 1]")
    rest_is_read = fractions[0] == 0.0
    levels = [rest_reading(update_map, rest_state, full_exposure, settings)]
    for fraction in fractions[1:] if rest_is_read else fractions:
        levels.append(solve_level(update_map, levels[-1], fraction, full_exposure, settings))
    read = tuple(range(len(levels))) if rest_is_read else tuple(range(1, len(levels)))
    return ExposureRamp(tuple(levels), read, full_exposure, settings)


def unrolled_cycle_centre(update_map: UpdateMap, cycle_start_state: torch.Tensor, exposure_input: torch.Tensor,
                          cycle_length: int, step_size: float) -> torch.Tensor:
    """Item 40 (4): one cycle of the relaxation unrolled from its first state (detached: the gradient runs through the
    cycle's steps, not through the relaxation that led to it), and each node's centre over it, halfway between its
    highest and lowest value. The gradient through the max and min flows to the steps that attain them.

    Where a node takes the same value at several steps of the cycle, its highest and lowest values tie and torch's max
    and min take the first tied step. For a node that does not move over the cycle (a part of the network that has
    settled while another part oscillates, at a level flagged oscillating as a whole) that is the detached first
    state, so no gradient passes through that node's centre, although the centre computed from the same first state
    does move with the parameters (experiments/run_exposure_ramp_pilot.py measures it on the planted networks; the
    record of 27 November 2026, docs/records/2026-11/exposure_ramp_pilot_2026-11-27.md, section 6)."""
    state = cycle_start_state.detach()
    states = [state]
    for _ in range(cycle_length - 1):
        state = relaxation_step(update_map, state, exposure_input, step_size)
        states.append(state)
    stacked = torch.stack(states)
    return 0.5 * (stacked.max(dim=0).values + stacked.min(dim=0).values)


@dataclasses.dataclass
class GradientSolveRecord:
    """What the gradient pass does: one entry per adjoint solve (its peak level and iterations), appended during
    backward, so it is empty until the prediction is differentiated; and one entry per cycle unrolled, appended when
    the prediction is built."""

    adjoint_solves: list[dict] = dataclasses.field(default_factory=list)
    unrolled_cycles: list[dict] = dataclasses.field(default_factory=list)


def _implicitly_differentiated_state(update_map: UpdateMap, steady_state: torch.Tensor, exposure_input: torch.Tensor,
                                     settings: ExposureRampSettings, level_index: int,
                                     record: GradientSolveRecord) -> torch.Tensor:
    """The steady state re-attached to the graph by one application of the map, with its gradient replaced on the way
    back by the solution w of the adjoint system w = g + J^T w (implicit differentiation, item 40 (4)), solved
    matrix-free by the relaxation with Anderson mixing; the gradients of all symptoms peaking at this level arrive
    summed, so it is one solve per distinct peak level."""
    reattached = update_map(steady_state.detach(), exposure_input)
    transpose_product = _reverse_mode_jacobian_product(update_map, steady_state, exposure_input)

    def adjoint(upstream: torch.Tensor) -> torch.Tensor:
        solve = anderson_fixed_point(lambda vector: upstream + transpose_product(vector), upstream, settings.step_size,
                                     settings.anderson_memory, settings.anderson_regularization,
                                     settings.adjoint_tolerance, settings.adjoint_iteration_cap)
        record.adjoint_solves.append({"level_index": level_index, "map_evaluations": solve.map_evaluations,
                                      "converged": solve.converged, "residual_norm": solve.residual_norm})
        if not solve.converged:
            raise RuntimeError(f"the adjoint solve at level {level_index} did not converge within "
                               f"{settings.adjoint_iteration_cap} evaluations (residual {solve.residual_norm:.3g})")
        return solve.state

    if reattached.requires_grad:
        reattached.register_hook(adjoint)
    return reattached


@dataclasses.dataclass(frozen=True)
class SymptomPeaks:
    """Item 40 (2)'s prediction: each symptom's highest logit over the levels read (differentiable through the level
    that attains it), the index into ramp.levels of that level per symptom, every level's logits (no gradient), and
    the record of the backward pass."""

    prediction: torch.Tensor
    peak_level_indices: tuple[int, ...]
    logits_by_level: torch.Tensor
    gradient_record: GradientSolveRecord

    @property
    def distinct_peak_levels(self) -> tuple[int, ...]:
        return tuple(sorted(set(self.peak_level_indices)))


def read_symptom_peaks(ramp: ExposureRamp, update_map: UpdateMap, head: Head) -> SymptomPeaks:
    """Item 40 (2): the head maps each level's state to symptom logits, and each symptom's prediction is its highest
    logit over the levels read, taken hard. The gradient flows through the attaining level alone: implicitly at a
    settled level, by the unrolled cycle at an oscillating one (item 40 (4)). Refuses a ramp with an unresolved level,
    for which item 40 defines no reading."""
    if ramp.unresolved_levels:
        raise ValueError(f"levels {ramp.unresolved_levels} neither settled nor showed a cycle within the caps; item 40 "
                         "defines no reading for such a level")
    with torch.no_grad():
        logits_by_level = torch.stack([head(ramp.levels[index].state) for index in ramp.read_level_indices])
    if logits_by_level.dim() != 2:
        raise ValueError("the head must map a state to a vector of symptom logits")
    peak_positions = logits_by_level.argmax(dim=0).tolist()
    peak_level_indices = tuple(ramp.read_level_indices[position] for position in peak_positions)
    record = GradientSolveRecord()
    logits_at_level: dict[int, torch.Tensor] = {}
    for level_index in sorted(set(peak_level_indices)):
        level = ramp.levels[level_index]
        exposure_input = level.exposure_fraction * ramp.full_exposure
        if level.kind == SETTLED:
            state = _implicitly_differentiated_state(update_map, level.state, exposure_input, ramp.settings, level_index,
                                                     record)
        else:
            state = unrolled_cycle_centre(update_map, level.cycle.start_state, exposure_input, level.cycle.length,
                                          ramp.settings.step_size)
            record.unrolled_cycles.append({"level_index": level_index, "cycle_length": level.cycle.length})
        logits_at_level[level_index] = head(state)
    prediction = torch.stack([logits_at_level[level_index][symptom]
                              for symptom, level_index in enumerate(peak_level_indices)])
    return SymptomPeaks(prediction, peak_level_indices, logits_by_level, record)
