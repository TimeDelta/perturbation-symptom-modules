"""Item 40's exposure-ramp readout (mechanistic_pathway_learning/models/exposure_ramp.py, decision 9.153) on the planted
networks of experiments/run_exposure_ramp_pilot.py: each rule of item 40 (1), (2), (4) and (5) checked as written,
against references computed apart from the ramp. Every setting is passed explicitly; the values are test values."""
from __future__ import annotations

import dataclasses

import numpy as np
import pytest
import torch

from experiments.run_exposure_ramp_pilot import (
    DATA_DIRECTORY,
    PLANTED_LOOP,
    PLANTED_SWITCH,
    PlantedNetwork,
    loop_equilibrium,
    network_jacobian,
    parse_arguments,
    planted_bistable_switch,
    planted_combined_network,
    planted_oscillating_loop,
    refuse_output_under_data,
    relaxation_onset_fraction,
    soft_saturation,
    switch_fold_fraction,
    switch_scalar_roots,
)
from mechanistic_pathway_learning.models import exposure_ramp
from mechanistic_pathway_learning.models.exposure_ramp import (
    OSCILLATING,
    SETTLED,
    SOLVED_BY_PLAIN_RELAXATION,
    UNRESOLVED,
    ExposureRampSettings,
    FixedPointSolve,
    anderson_fixed_point,
    exposure_fractions,
    find_cycle,
    largest_absolute_entry,
    lifelong_perturbation_fractions,
    plain_relaxation,
    read_symptom_peaks,
    record_relaxation,
    relaxation_growth_rate,
    rest_reading,
    run_exposure_ramp,
    solve_level,
    unrolled_cycle_centre,
)

DTYPE = torch.float64


def settings(**changes) -> ExposureRampSettings:
    """Test values for every setting; a test changes the ones it is about."""
    values = dict(step_size=0.5, anderson_memory=3, anderson_regularization=0.0, anderson_iteration_cap=500,
                  settle_tolerance=1e-12, relaxation_iteration_cap=20000, stability_probe_steps=200,
                  state_match_tolerance=1e-5, cycle_tolerance=2e-2, cycle_iteration_cap=6000, adjoint_tolerance=1e-12,
                  adjoint_iteration_cap=20000, warm_start_after_oscillation="last_relaxation_state")
    values.update(changes)
    return ExposureRampSettings(**values)


LOOP_SETTINGS = dict(step_size=0.1, relaxation_iteration_cap=6000, cycle_iteration_cap=6000)


def switch() -> PlantedNetwork:
    return planted_bistable_switch(**PLANTED_SWITCH)


def loop() -> PlantedNetwork:
    return planted_oscillating_loop(**PLANTED_LOOP)


def ramp_of(network: PlantedNetwork, fractions, ramp_settings: ExposureRampSettings):
    return run_exposure_ramp(network.update_map, network.rest_state, network.full_exposure, fractions, ramp_settings)


@pytest.fixture(scope="module")
def switch_ramp():
    return ramp_of(switch(), exposure_fractions(10, False), settings())


@pytest.fixture(scope="module")
def loop_ramp():
    return ramp_of(loop(), exposure_fractions(5, False), settings(**LOOP_SETTINGS))


# ---------------------------------------------------------------- rule (1): the levels


def test_the_levels_are_evenly_spaced_to_the_full_exposure_and_rest_is_read_only_when_asked():
    assert exposure_fractions(4, False) == (0.25, 0.5, 0.75, 1.0)
    assert exposure_fractions(4, True) == (0.0, 0.25, 0.5, 0.75, 1.0)
    for bad in (0, -1, 2.5):
        with pytest.raises(ValueError):
            exposure_fractions(bad, False)
    with pytest.raises(ValueError):
        exposure_fractions(3, "no")


def test_a_lifelong_perturbation_is_read_at_its_full_level_alone_reached_from_rest():
    ramp = ramp_of(switch(), lifelong_perturbation_fractions(), settings())
    assert [level.exposure_fraction for level in ramp.levels] == [0.0, 1.0] and ramp.read_level_indices == (1,)
    expected = switch_scalar_roots(headroom=9.0, steepness=1.0, loop_weight=0.6, entry_input=1.0)
    assert len(expected) == 1 and largest_absolute_entry(ramp.levels[1].state - torch.tensor(expected[0], dtype=DTYPE)) < 1e-8


def test_reading_rest_puts_it_among_the_levels_the_maximum_is_taken_over():
    network = switch()
    network = dataclasses.replace(network, head_weights=-network.head_weights)  # both logits fall as exposure rises
    with_rest = read_symptom_peaks(ramp_of(network, exposure_fractions(4, True), settings()), network.update_map, network.head)
    without_rest = read_symptom_peaks(ramp_of(network, exposure_fractions(4, False), settings()), network.update_map, network.head)
    assert with_rest.peak_level_indices == (0, 0) and torch.allclose(with_rest.prediction, torch.zeros(2, dtype=DTYPE))
    assert without_rest.peak_level_indices == (1, 1) and bool((without_rest.prediction < 0).all())


def test_the_ramp_refuses_levels_that_do_not_end_at_the_full_exposure_or_do_not_rise():
    for fractions in ((0.5,), (0.5, 0.25, 1.0), (0.5, 0.5, 1.0), (0.5, 1.5)):
        with pytest.raises(ValueError):
            ramp_of(switch(), fractions, settings())


def test_every_setting_is_required_and_bad_values_are_refused():
    with pytest.raises(TypeError):
        ExposureRampSettings(step_size=0.5)
    for change in ({"step_size": 0.0}, {"step_size": 1.5}, {"anderson_memory": -1}, {"settle_tolerance": 0.0},
                   {"relaxation_iteration_cap": 0}, {"stability_probe_steps": 1}, {"warm_start_after_oscillation": "rest"},
                   {"anderson_regularization": -1.0}):
        with pytest.raises(ValueError):
            settings(**change)


# ---------------------------------------------------------------- rule (4): the solver


def test_anderson_mixing_with_no_memory_is_the_plain_relaxation():
    network, exposure_input = switch(), 0.3 * switch().full_exposure
    mixed = anderson_fixed_point(lambda state: network.update_map(state, exposure_input), network.rest_state, 0.5, 0, 0.0,
                                 1e-12, 5000)
    plain = plain_relaxation(network.update_map, network.rest_state, exposure_input, 0.5, 1e-12, 5000)
    assert mixed.converged and plain.converged and mixed.map_evaluations == plain.map_evaluations
    assert torch.equal(mixed.state, plain.state)


def test_anderson_mixing_settles_a_level_in_fewer_evaluations_than_the_plain_relaxation():
    network, exposure_input = switch(), 0.3 * switch().full_exposure
    mixed = anderson_fixed_point(lambda state: network.update_map(state, exposure_input), network.rest_state, 0.5, 3, 0.0,
                                 1e-12, 5000)
    plain = plain_relaxation(network.update_map, network.rest_state, exposure_input, 0.5, 1e-12, 5000)
    assert mixed.converged and mixed.map_evaluations < plain.map_evaluations
    assert largest_absolute_entry(mixed.state - plain.state) < 1e-10


def test_the_growth_rate_is_the_spectral_radius_of_the_relaxation_step():
    for network, fraction, step_size in ((switch(), 0.3, 0.5), (loop(), 0.2, 0.1), (loop(), 1.0, 0.1)):
        exposure_input = fraction * network.full_exposure
        state = loop_equilibrium(network, exposure_input)
        jacobian = network_jacobian(network, state, exposure_input)
        radius = float(np.abs(np.linalg.eigvals(np.eye(len(state)) + step_size * (jacobian - np.eye(len(state))))).max())
        assert relaxation_growth_rate(network.update_map, state, exposure_input, step_size, 400) == pytest.approx(radius, rel=2e-3)


def test_the_ramp_reads_the_branch_from_rest_and_flags_the_fold_where_the_branch_ends(switch_ramp):
    fold = switch_fold_fraction(**PLANTED_SWITCH)
    assert 0.4 < fold < 0.5
    for level in switch_ramp.levels[1:]:
        roots = switch_scalar_roots(headroom=9.0, steepness=1.0, loop_weight=0.6, entry_input=level.exposure_fraction)
        expected = roots[0] if level.exposure_fraction < fold else roots[-1]
        assert level.kind == SETTLED
        assert largest_absolute_entry(level.state - torch.tensor(expected, dtype=DTYPE)) < 1e-6
        assert len(roots) == (3 if level.exposure_fraction < fold else 1)
    assert switch_ramp.fold_levels == (5,), "the first level past the fold, and no other"
    assert all(level.fold_jump is False for index, level in enumerate(switch_ramp.levels[1:], start=1) if index != 5)


def test_a_fold_whose_bistable_range_lies_wholly_between_two_levels_is_not_flagged():
    """The fold test's documented limit (exposure_ramp module docstring, rule (4); LevelReading.fold_jump): it finds a
    fold only where the system is still bistable at the earlier level's input. This weaker switch (test values) is
    bistable only between entry inputs 1.0 and 1.2, levels 5 and 6 of ten: the ramp jumps from the lower branch to the
    upper one between them and the flag is not raised. With one more level inside the bistable range it is raised."""
    weaker = dict(headroom=9.0, steepness=1.0, loop_weight=0.42)
    network = planted_bistable_switch(**weaker, full_entry_input=2.0)

    def roots(entry_input):
        return [torch.tensor(root, dtype=DTYPE) for root in switch_scalar_roots(**weaker, entry_input=entry_input)]

    assert len(roots(1.0)) == 1 and len(roots(1.03)) == 3 and len(roots(1.2)) == 1
    coarse = ramp_of(network, exposure_fractions(10, False), settings())
    before, after = coarse.levels[5], coarse.levels[6]
    assert (before.exposure_fraction, after.exposure_fraction) == (0.5, 0.6)
    assert largest_absolute_entry(before.state - roots(1.0)[0]) < 1e-6
    assert largest_absolute_entry(after.state - roots(1.2)[0]) < 1e-6
    assert bool((after.state > roots(1.03)[1]).all()), "past the middle, unstable state: the ramp jumped"
    assert after.kind == SETTLED and after.fold_jump is False and coarse.fold_levels == ()
    with_a_level_inside = tuple(sorted(exposure_fractions(10, False) + (0.515,)))  # entry input 1.03
    finer = ramp_of(network, with_a_level_inside, settings())
    assert finer.levels[6].exposure_fraction == 0.515 and finer.fold_levels == (7,)


def test_only_the_branch_from_rest_is_read_where_another_stable_state_exists():
    network = dataclasses.replace(switch(), full_exposure=torch.tensor([0.3, 0.0], dtype=DTYPE))  # inside the bistable range
    ramp = ramp_of(network, exposure_fractions(3, False), settings())
    roots = switch_scalar_roots(headroom=9.0, steepness=1.0, loop_weight=0.6, entry_input=0.3)
    assert len(roots) == 3 and ramp.fold_levels == ()
    assert largest_absolute_entry(ramp.levels[-1].state - torch.tensor(roots[0], dtype=DTYPE)) < 1e-6
    upper = plain_relaxation(network.update_map, torch.tensor(roots[-1], dtype=DTYPE) + 0.1, network.full_exposure, 0.5,
                             1e-12, 20000)
    assert upper.converged and largest_absolute_entry(upper.state - torch.tensor(roots[-1], dtype=DTYPE)) < 1e-6


def test_an_anderson_landing_that_the_plain_relaxation_does_not_reach_is_replaced(monkeypatch):
    network = switch()
    ramp_settings = settings()
    previous = solve_level(network.update_map, rest_reading(network.update_map, network.rest_state, network.full_exposure,
                                                            ramp_settings), 0.2, network.full_exposure, ramp_settings)
    upper = torch.tensor(switch_scalar_roots(headroom=9.0, steepness=1.0, loop_weight=0.6, entry_input=0.3)[-1], dtype=DTYPE)
    real_anderson = exposure_ramp.anderson_fixed_point

    def anderson_that_overshoots_once(fixed_point_map, initial_state, *rest):
        if largest_absolute_entry(initial_state - previous.state) == 0.0:
            return FixedPointSolve(upper, True, 1, 0.0)  # a stable state, but not the one the relaxation reaches
        return real_anderson(fixed_point_map, initial_state, *rest)

    monkeypatch.setattr(exposure_ramp, "anderson_fixed_point", anderson_that_overshoots_once)
    level = solve_level(network.update_map, previous, 0.3, network.full_exposure, ramp_settings)
    lower = torch.tensor(switch_scalar_roots(headroom=9.0, steepness=1.0, loop_weight=0.6, entry_input=0.3)[0], dtype=DTYPE)
    assert level.anderson_disagreed and level.solver == SOLVED_BY_PLAIN_RELAXATION and level.fold_jump is False
    assert largest_absolute_entry(level.state - lower) < 1e-6


def test_levels_past_the_stepped_onset_oscillate_and_anderson_mixing_lands_on_the_equilibrium_inside(loop_ramp):
    network = loop()
    onset = relaxation_onset_fraction(network, LOOP_SETTINGS["step_size"])
    assert 0.2 < onset < 0.6
    for level in loop_ramp.levels[1:]:
        equilibrium = loop_equilibrium(network, level.exposure_fraction * network.full_exposure)
        if level.exposure_fraction < onset:
            assert level.kind == SETTLED and largest_absolute_entry(level.state - equilibrium) < 1e-8
        else:
            assert level.kind == OSCILLATING
            assert level.anderson_rejection == "unstable" and level.anderson_growth_rate > 1.0
            assert largest_absolute_entry(level.anderson_state - equilibrium) < 1e-8, "Anderson mixing converged on it"
            assert largest_absolute_entry(level.state - equilibrium) > 1e-2, "the centre is not the equilibrium"


def test_an_oscillating_level_is_read_halfway_between_each_nodes_highest_and_lowest_over_one_cycle(loop_ramp):
    network, ramp_settings = loop(), settings(**LOOP_SETTINGS)
    level = loop_ramp.levels[-1]
    assert level.kind == OSCILLATING
    assert torch.equal(level.state, 0.5 * (level.cycle.highest + level.cycle.lowest))
    continued = record_relaxation(network.update_map, level.last_relaxation_state, network.full_exposure,
                                  ramp_settings.step_size, 20 * level.cycle.length)
    for start in range(0, 19 * level.cycle.length, level.cycle.length):
        window = continued[start:start + level.cycle.length]
        assert largest_absolute_entry(window.max(dim=0).values - level.cycle.highest) <= ramp_settings.cycle_tolerance
        assert largest_absolute_entry(window.min(dim=0).values - level.cycle.lowest) <= ramp_settings.cycle_tolerance
    assert largest_absolute_entry(unrolled_cycle_centre(network.update_map, level.cycle.start_state, network.full_exposure,
                                                        level.cycle.length, ramp_settings.step_size) - level.state) == 0.0


def test_a_settling_trajectory_has_no_cycle_and_a_steady_cycle_is_found():
    network = loop()
    settling = record_relaxation(network.update_map, network.rest_state, 0.2 * network.full_exposure, 0.1, 3000)
    assert find_cycle(settling, 1e-3) is None
    cycling = record_relaxation(network.update_map, network.rest_state, network.full_exposure, 0.1, 6000)
    cycle = find_cycle(cycling, 2e-2)
    assert cycle is not None and 30 < cycle.length < 60


def test_the_next_level_starts_where_the_setting_says_after_an_oscillating_level(loop_ramp):
    level = loop_ramp.levels[-1]
    assert torch.equal(level.warm_start(settings(warm_start_after_oscillation="last_relaxation_state")), level.last_relaxation_state)
    assert torch.equal(level.warm_start(settings(warm_start_after_oscillation="cycle_centre")), level.state)


def test_the_fold_test_is_not_evaluated_beside_an_oscillating_level(loop_ramp):
    for index, level in enumerate(loop_ramp.levels[1:], start=1):
        if level.kind != SETTLED or loop_ramp.levels[index - 1].kind != SETTLED:
            assert level.fold_jump is None
        else:
            assert level.fold_jump is False


def test_a_rest_state_the_relaxation_does_not_settle_on_is_refused():
    with pytest.raises(ValueError, match="does not settle on the rest state"):
        ramp_of(loop(), exposure_fractions(2, False), settings(step_size=0.5))
    with pytest.raises(ValueError, match="not a steady state"):
        run_exposure_ramp(switch().update_map, torch.tensor([0.5, 0.5], dtype=DTYPE), switch().full_exposure, (1.0,), settings())


def test_a_level_that_neither_settles_nor_cycles_is_unresolved_and_the_readout_refuses_it():
    ramp = ramp_of(loop(), (1.0,), settings(step_size=0.1, relaxation_iteration_cap=50, cycle_iteration_cap=60))
    assert ramp.levels[-1].kind == UNRESOLVED and ramp.unresolved_levels == (1,)
    with pytest.raises(ValueError, match="defines no reading"):
        read_symptom_peaks(ramp, loop().update_map, loop().head)


# ---------------------------------------------------------------- rule (2): the readout, and the gradients


def differentiable_peaks(network: PlantedNetwork, fractions, ramp_settings):
    differentiable = network.differentiable()
    ramp = ramp_of(differentiable, fractions, ramp_settings)
    return differentiable, ramp, read_symptom_peaks(ramp, differentiable.update_map, differentiable.head)


def test_each_symptoms_prediction_is_its_highest_logit_taken_hard_through_that_level_alone(switch_ramp):
    network = dataclasses.replace(switch(), head_weights=torch.tensor([[0.0, 1.0], [1.0, -1.0]], dtype=DTYPE),
                                  head_bias=torch.zeros(2, dtype=DTYPE))
    differentiable, ramp, peaks = differentiable_peaks(network, exposure_fractions(10, False), settings())
    assert torch.allclose(peaks.prediction.detach(), peaks.logits_by_level.max(dim=0).values, atol=1e-10)
    assert peaks.peak_level_indices == (10, 4), "the partner peaks at the full level, entry less partner before the fold"
    peaks.prediction[1].backward()
    assert torch.equal(differentiable.head_bias.grad, torch.tensor([0.0, 1.0], dtype=DTYPE))
    assert torch.allclose(differentiable.head_weights.grad[1], ramp.levels[4].state, atol=1e-10)
    assert torch.equal(differentiable.head_weights.grad[0], torch.zeros(2, dtype=DTYPE))


def test_one_adjoint_solve_per_distinct_peak_level():
    network = dataclasses.replace(switch(), head_weights=torch.tensor([[0.0, 1.0], [1.0, -1.0], [0.0, 2.0]], dtype=DTYPE),
                                  head_bias=torch.zeros(3, dtype=DTYPE), symptom_names=("a", "b", "c"))
    _, _, peaks = differentiable_peaks(network, exposure_fractions(10, False), settings())
    assert peaks.distinct_peak_levels == (4, 10)
    peaks.prediction.sum().backward()
    assert sorted(solve["level_index"] for solve in peaks.gradient_record.adjoint_solves) == [4, 10]
    assert all(solve["converged"] for solve in peaks.gradient_record.adjoint_solves)


def whole_readout(network: PlantedNetwork, fractions, ramp_settings) -> torch.Tensor:
    ramp = ramp_of(network, fractions, ramp_settings)
    return read_symptom_peaks(ramp, network.update_map, network.head).prediction.detach()


@pytest.mark.parametrize("symptom_row, expected_peak", [((0.0, 1.0), 10), ((1.0, -1.0), 4)])
def test_the_implicit_gradient_at_a_settled_peak_matches_finite_differences_of_the_whole_readout(symptom_row, expected_peak):
    network = dataclasses.replace(switch(), head_weights=torch.tensor([symptom_row], dtype=DTYPE),
                                  head_bias=torch.zeros(1, dtype=DTYPE), symptom_names=("s",))
    fractions, ramp_settings = exposure_fractions(10, False), settings()
    differentiable, ramp, peaks = differentiable_peaks(network, fractions, ramp_settings)
    assert peaks.peak_level_indices == (expected_peak,) and ramp.levels[expected_peak].kind == SETTLED
    peaks.prediction[0].backward()
    step = 1e-6
    for parameter, index in (("edge_weights", (0, 1)), ("edge_weights", (1, 0)), ("full_exposure", (0,))):
        numeric = float(whole_readout(network.with_entry(parameter, index, step), fractions, ramp_settings)[0]
                        - whole_readout(network.with_entry(parameter, index, -step), fractions, ramp_settings)[0]) / (2 * step)
        analytic = float(getattr(differentiable, parameter).grad[index])
        assert analytic == pytest.approx(numeric, rel=1e-5, abs=1e-8)


def test_an_adjoint_solve_that_does_not_converge_is_an_error():
    network = switch()
    _, _, peaks = differentiable_peaks(network, exposure_fractions(4, False), settings(adjoint_iteration_cap=2))
    with pytest.raises(RuntimeError, match="adjoint solve"):
        peaks.prediction.sum().backward()


def test_the_unrolled_cycle_gradient_is_the_gradient_of_the_centre_unrolled_from_the_same_first_state(loop_ramp):
    network, fractions, ramp_settings = loop(), exposure_fractions(5, False), settings(**LOOP_SETTINGS)
    differentiable, ramp, peaks = differentiable_peaks(network, fractions, ramp_settings)
    symptom = 2  # the inhibitor's level
    level_index = peaks.peak_level_indices[symptom]
    level = ramp.levels[level_index]
    assert level.kind == OSCILLATING and peaks.gradient_record.unrolled_cycles[0]["level_index"] == level_index
    peaks.prediction[symptom].backward()

    def centre_value(moved: PlantedNetwork) -> float:
        with torch.no_grad():
            centre = unrolled_cycle_centre(moved.update_map, level.cycle.start_state, level.exposure_fraction * moved.full_exposure,
                                           level.cycle.length, ramp_settings.step_size)
            return float(moved.head(centre)[symptom])

    step = 1e-6
    for parameter, index in (("edge_weights", (1, 0)), ("edge_weights", (0, 2)), ("full_exposure", (0,)), ("head_weights", (2, 2))):
        numeric = (centre_value(network.with_entry(parameter, index, step))
                   - centre_value(network.with_entry(parameter, index, -step))) / (2 * step)
        analytic = float(getattr(differentiable, parameter).grad[index])
        assert analytic == pytest.approx(numeric, rel=1e-6, abs=1e-9)


def test_a_node_that_does_not_move_over_the_cycle_passes_no_gradient_through_its_centre():
    """unrolled_cycle_centre's documented behaviour: at a level flagged oscillating as a whole, the settled switch's
    highest and lowest values over the cycle tie, the first tied step is the detached first state, and the gradient
    through that node's centre is zero, although the centre from the same first state moves with the weight."""
    network = planted_combined_network(switch=switch(), loop=loop(), switch_full_entry_input=1.3, loop_full_entry_input=3.0,
                                       head_weights=((0.0, 1.0, 0.0, 0.0, 0.0),), head_bias=(0.0,), symptom_names=("s",))
    ramp_settings = settings(**LOOP_SETTINGS)
    differentiable, ramp, peaks = differentiable_peaks(network, lifelong_perturbation_fractions(), ramp_settings)
    level = ramp.levels[1]
    assert level.kind == OSCILLATING and float(level.cycle.highest[1]) == float(level.cycle.lowest[1])
    peaks.prediction[0].backward()
    assert float(differentiable.edge_weights.grad[1, 0]) == 0.0

    def centre_value(moved: PlantedNetwork) -> float:
        with torch.no_grad():
            return float(unrolled_cycle_centre(moved.update_map, level.cycle.start_state, moved.full_exposure,
                                               level.cycle.length, ramp_settings.step_size)[1])

    step = 1e-6
    moved = (centre_value(network.with_entry("edge_weights", (1, 0), step))
             - centre_value(network.with_entry("edge_weights", (1, 0), -step))) / (2 * step)
    assert moved > 1e-2


# ---------------------------------------------------------------- the fixtures and the pilot's command line


def test_the_stand_in_saturation_has_its_floor_its_ceiling_and_rest_at_zero():
    headroom, steepness = torch.tensor(9.0, dtype=DTYPE), torch.tensor(1.0, dtype=DTYPE)
    values = soft_saturation(torch.tensor([-200.0, 0.0, 200.0], dtype=DTYPE), headroom, steepness)
    assert values.tolist() == pytest.approx([-1.0, 0.0, 9.0])
    assert torch.all(soft_saturation(torch.linspace(-50, 50, 1001, dtype=DTYPE), headroom, steepness) > -1.0 - 1e-12)


def test_the_planted_switch_is_bistable_at_rest_and_the_planted_loop_has_one_equilibrium():
    assert len(switch_scalar_roots(headroom=9.0, steepness=1.0, loop_weight=0.6, entry_input=0.0)) == 3
    for fraction in (0.0, 0.5, 1.0):
        exposure_input = fraction * loop().full_exposure
        state = loop_equilibrium(loop(), exposure_input)
        assert largest_absolute_entry(loop().update_map(state, exposure_input) - state) < 1e-12


def test_the_pilot_requires_every_argument_and_writes_nothing_under_data(tmp_path):
    with pytest.raises(SystemExit):
        parse_arguments(["--number-of-levels", "10", "--output", str(tmp_path / "out.json")])
    with pytest.raises(SystemExit):
        refuse_output_under_data(DATA_DIRECTORY / "pilot.json")
    refuse_output_under_data(tmp_path / "pilot.json")
