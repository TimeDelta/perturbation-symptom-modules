# Item 40 (7)'s pilot on planted networks: the ramp, the fold jump and the oscillation rule (27 November 2026)

An engineering measurement of 27 November 2026, on planted networks only. **No graph build was read.** The code is
`mechanistic_pathway_learning/models/exposure_ramp.py` (item 40 (1), (2), (4) and (5) on a generic update map) and
`experiments/run_exposure_ramp_pilot.py` (the planted fixtures, the references, the checks), run at commit `f5bf64f`
with no change to either file (the output's `code_differs_from_commit` is false). The full output is
`exposure_ramp_pilot_2026-11-27.json` beside this file. No outside source was read. This record decides nothing,
reinterprets nothing in item 40, and proposes neither the tolerance nor the time budget of item 40 (7). Item 40 and
row 9.153 of `docs/open_decisions.md` are unchanged. Where a rule did not behave as written, the record says so. What
follows from that is the owner's to decide, and reading a measurement for a decision is research under `CLAUDE.md`'s
rules, not part of this record.

Item 40 (7) asks for "a pilot on a small planted network, with one branch of a bistable switch and one oscillating
loop, checking that the ramp, the fold jump and the oscillation rule behave as written". The pilot's other half times
one warm-started level and one unrolled cycle on the confirmatory graph and counts how spread out the peak levels
are. That half waits on the v5 rebuild and is not here.

## 1. What was run

The command, from the repository root:

```
PYTHONPATH=. python experiments/run_exposure_ramp_pilot.py --number-of-levels 10 --rest-is-read no \
    --step-size 0.02 --comparison-step-sizes 0.5 0.1 0.05 0.02 0.01 --anderson-memory 5 \
    --anderson-regularization 0 --anderson-iteration-cap 2000 --settle-tolerance 1e-11 \
    --relaxation-iteration-cap 60000 --stability-probe-steps 400 --state-match-tolerance 1e-4 \
    --cycle-tolerance 1e-2 --cycle-iteration-cap 40000 --adjoint-tolerance 1e-11 --adjoint-iteration-cap 100000 \
    --warm-start-after-oscillation last_relaxation_state --finite-difference-step 1e-6 \
    --gradient-agreement-tolerance 1e-4 --profile-step 1e-6 --profile-points 5 --ode-tolerance 1e-10 \
    --ode-settling-time 3000 --ode-reading-time 200 --timing-repeats 5 \
    --output docs/records/2026-11/exposure_ramp_pilot_2026-11-27.json
```

Every value in it is a required argument with no default, because no ruling sets it. They are this run's values, not
proposals. Two of them are definitions that item 40 leaves open, not numerical settings:

- **Whether rest is among the levels the maximum is taken over** (`--rest-is-read no`). Item 40 (1) raises a drug
  "from 0 to its full exposure in levels evenly spaced", and reads a gene or allele perturbation "at its full level
  alone". The two readings of "from 0" differ whenever a drug lowers a symptom's logit at every level above rest.
- **Where the next level starts after an oscillating level** (`--warm-start-after-oscillation
  last_relaxation_state`). Item 40 (1) solves each level "from the previous level's steady state", and an oscillating
  level has none. The run started from the last state of the recorded relaxation; the other choice is the cycle's
  centre.

**The planted networks** (`PLANTED_SWITCH`, `PLANTED_LOOP`, `PLANTED_COMBINED` in the script) are test values, not
sourced, registered or physiological. Every node updates as h <- S(W h + u) with the stand-in saturation
S(x) = (1 + H) / (1 + H exp(-n x)) - 1, which has a floor at -1, a ceiling at the headroom H, and S(0) = 0. Here
H = 9 and n = 1. This is not 37f's form, which 37f leaves as "soft (Michaelis-Menten or Hill)". The relaxation is
h <- h + step (S(W h + u) - h) with step 0.02, and the comparison in section 4 runs other steps.

- **The switch**: two nodes that activate each other with weight 0.6, the drug entering the first at a full input of
  1.0. It has three steady states at rest, so it is bistable there.
- **The loop**: three nodes in a ring, entry to middle +1.5, middle to inhibitor +1.5 and inhibitor to entry -1.5, the
  drug entering the entry node at a full input of 3.0.
- **The combined network**: the two side by side with no edge between them, one drug entering the switch at 1.3 and
  the loop at 3.0. Its head has three symptoms: the switch's partner node, the loop's inhibitor node, and the switch's
  entry node less its partner.

Ten levels were solved, at 0.1 to 1.0 of the full input, and rest was not read.

## 2. The switch: the branch from rest and the fold

The reference, computed apart from the ramp, is the scalar equation a = S(w S(w a) + u) for the entry node, solved on
a grid and refined by bisection. The lower branch ends at a fold at **0.41833** of the full exposure.

| level | exposure | solved by | map evaluations | fold flag | state (entry, partner) |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.1 | Anderson mixing | 10 | no | 0.140315, 0.078362 |
| 2 | 0.2 | Anderson mixing | 11 | no | 0.316179, 0.184159 |
| 3 | 0.3 | Anderson mixing | 13 | no | 0.555416, 0.342404 |
| 4 | 0.4 | Anderson mixing | 15 | no | 0.994181, 0.678816 |
| 5 | 0.5 | plain relaxation (Anderson did not converge in 2,000) | 4,549 | **yes** | 8.683769, 8.531596 |
| 6 | 0.6 | Anderson mixing | 7 | no | 8.714355, 8.539722 |
| 7 to 10 | 0.7 to 1.0 | Anderson mixing | 7 to 8 | no | 8.741922, 8.546930 to 8.809463, 8.564139 |

- **The ramp reads the branch from rest** (rule (1) and (5)), as written. Before the fold every level sits on the
  lowest of the three steady states, and after it on the only one left. The largest distance from the reference is
  2.0e-11.
- **The fold jump is kept and flagged**, as written. The flag is raised at level 5, the first level past the fold,
  and at no other level. The jump lands on the other stable state.
- **The fold test finds a fold only where the system is still bistable at the level before the jump.** This switch
  is bistable from rest to the fold, so that holds at every level here. A fold whose bistable range falls wholly
  between two levels is crossed, and the jump kept, without the flag. `tests/test_exposure_ramp.py`
  (`test_a_fold_whose_bistable_range_lies_wholly_between_two_levels_is_not_flagged`) pins that on a weaker switch;
  this run does not measure it.
- **Anderson mixing did not make the jump.** At level 5, starting from the lower branch's last state, it had not
  converged after its 2,000 evaluations. The plain relaxation from the same start made the landing in the remaining
  2,549. Every other level settled under Anderson mixing in 7 to 15 evaluations. This run's Anderson memory of 5
  combines six residuals of a two-node state, more residuals than the state has dimensions, with no regularization;
  the run did not vary the memory.
- The growth rate of the linearized relaxation at level 4, which lies 0.018 below the fold, is 0.997921. At rest it is
  0.990799, and past the fold 0.9825 to 0.9841.

## 3. The loop: the oscillation rule

The references, computed apart from the ramp:

- the loop's one equilibrium, by Newton's method;
- the exposure at which the stepped relaxation stops settling on it (the step's spectral radius crosses 1):
  **0.53374** at step 0.02;
- the ODE's Hopf point, where the largest real part of the eigenvalues of the Jacobian crosses 1: **0.59672**;
- the ODE's limit cycle, integrated by `solve_ivp` (DOP853, tolerance 1e-10), its centre read on a grid of 200,001
  points over 200 time units after 3,000 time units of settling.

Levels 1 to 5 (0.1 to 0.5) settled on the equilibrium under Anderson mixing. Levels 6 to 10 (0.6 to 1.0) were flagged
oscillating, which is exactly the set past the stepped onset.

| level | Anderson's growth rate at its state | cycle length (steps) | centre read (entry, middle, inhibitor) | equilibrium | ODE cycle centre |
| --- | --- | --- | --- | --- | --- |
| 6 | 1.000946 | 188 | 0.314701, 0.575880, 1.129452 | 0.326626, 0.535161, 0.986930 | 0.326197, 0.536251, 0.990844 |
| 7 | 1.001834 | 191 | 0.353161, 0.711980, 1.521047 | 0.363170, 0.607755, 1.165999 | 0.351664, 0.661892, 1.359244 |
| 8 | 1.002336 | 193 | 0.403517, 0.846052, 1.900708 | 0.396761, 0.676907, 1.347172 | 0.391361, 0.785013, 1.719600 |
| 9 | 1.002666 | 194 | 0.459419, 0.977337, 2.257366 | 0.427874, 0.743057, 1.530070 | 0.438516, 0.905787, 2.065483 |
| 10 | 1.003158 | 195 | 0.517457, 1.105530, 2.583871 | 0.456893, 0.806596, 1.714396 | 0.489159, 1.024004, 2.390220 |

- **Anderson mixing converged on the equilibrium inside the cycle at every oscillating level.** That state is one the
  relaxation moves away from, with growth rates of 1.0009 to 1.0032. The stability probe rejected it each time, and the
  oscillation rule fired only because of that probe. Without it, all five levels would have been read as settled at
  the equilibrium, and none would have been flagged.
- **The level is read at the centre of one cycle and flagged**, as written. The highest and lowest values of the last
  cycle moved from those of the cycle before by 2.3e-5 to 1.7e-4, within the cycle tolerance of 1e-2. The period is
  not a whole number of steps, so the sampled extremes move a little from cycle to cycle.
- **Detecting an oscillating level costs the cap.** A level is known not to settle only once the relaxation has spent
  its cap. Each oscillating level cost 100,015 to 100,029 map evaluations: the few that Anderson mixing took to
  converge on the equilibrium, the 60,000 of the relaxation, and the 40,000 recorded steps the cycle is found in. A
  settled level cost 15 to 20.
- The centre is neither the equilibrium nor the ODE's centre. Section 4 shows how it moves with the step.

## 4. The oscillation depends on the step size

The loop was run with the same ten levels at each compared step. Each "distance" is the largest node difference
between the centre read at the full exposure and the ODE's centre there, which is (0.489159, 1.024004, 2.390220).

| step | stepped onset (fraction) | levels flagged oscillating | cycle length at full exposure | centre read at full exposure | distance from the ODE's centre |
| --- | --- | --- | --- | --- | --- |
| 0.5 | none: rest itself is unstable | refused at rest (growth rate 1.02133) | | | |
| 0.1 | 0.35217 | 4 to 10 | 44 | 0.679924, 1.512917, 3.266554 | 0.876 |
| 0.05 | 0.45500 | 5 to 10 | 82 | 0.570124, 1.244113, 2.864976 | 0.475 |
| 0.02 | 0.53374 | 6 to 10 | 195 | 0.517457, 1.105530, 2.583871 | 0.194 |
| 0.01 | 0.56398 | 6 to 10 | 384 | 0.502560, 1.063628, 2.487138 | 0.097 |
| ODE | 0.59672 (Hopf) | | | 0.489159, 1.024004, 2.390220 | |

- **Where the oscillation starts depends on the step size.** The stepped relaxation stops settling before the ODE
  does, and the gap closes as the step shrinks. At step 0.1, levels 4 and 5 (0.4 and 0.5) are flagged oscillating,
  although the ODE dh/dt = F(h, u) - h settles there.
- **The centre read depends on the step size.** At the full exposure it differs from the ODE's centre by an amount
  roughly proportional to the step: 0.876, 0.475, 0.194 and 0.097 at steps 0.1, 0.05, 0.02 and 0.01.
- **At step 0.5 the ramp refuses this loop's rest state.** The stepped relaxation does not settle on it (growth rate
  1.02133), although the ODE's rest is stable. 0.5 is the damping the linear-response encoder runs today
  (`mechanistic_pathway_learning/models/linear_response_encoder.py`, `damping`).

Item 40 itself names the step size as one of the three things a peak over iteration rounds would read ("the step size
of the iteration (the damping of 0.5 is a forward-Euler step of dh/dt = F(h) - h)"). On this loop, the oscillation
rule is exposed to it as well. A steady state itself does not depend on the step, but whether the stepped relaxation
settles on it does, as the step-0.5 row shows.

## 5. The combined network: the per-symptom maximum and the solves

Here the switch's fold falls at 0.32179 of the full exposure, and the loop's stepped onset is again 0.53374.

- Level 4 was flagged as the fold, and levels 6 to 10 as oscillating.
- The three symptoms peaked at levels 10, 10 and 3. The predictions, 8.576405, 2.583871 and 0.302893, are each
  symptom's highest logit over the ten levels.
- **One solve per distinct peak level**, as written. Level 3 is settled and got one adjoint solve (converged in 5
  evaluations). Level 10 is oscillating and got one cycle unrolled (195 steps).
- **A level is flagged oscillating as a whole.** The first symptom reads the switch, which has settled at level 10. It
  peaks there because the loop oscillates at that level, so its gradient comes from the unrolled cycle (section 6).
- The fold test runs only between two settled levels (`exposure_ramp.solve_level`). Here the fold came before the
  loop's onset and was flagged. A fold falling at a level where another part of the network oscillates would not be
  flagged. That is the code's behaviour, tested in `tests/test_exposure_ramp.py`, and is not measured here.

## 6. The gradients

The gradients were checked by central differences with a step of 1e-6. A gap is |backward pass - finite difference|
divided by the larger of the two.

**The implicit gradient at a settled peak level** matches finite differences of the whole readout (the ramp and the
maximum), as written:

| symptom (network), peak level | parameter | backward pass | finite difference | gap |
| --- | --- | --- | --- | --- |
| switch partner (switch), level 10 | weight partner to entry | 0.41191498 | 0.41191499 | 2.6e-8 |
| | weight entry to partner | 3.77831901 | 3.77831901 | 2.3e-9 |
| | full entry input | 0.04809765 | 0.04809765 | 9.8e-10 |
| entry less partner (combined), level 3 | weight partner to entry | 0.74025175 | 0.74025168 | 9.8e-8 |
| | weight entry to partner | -0.35436551 | -0.35436550 | 2.3e-8 |
| | full entry input of the switch | 0.35847007 | 0.35847123 | 3.2e-6 |

**The unrolled-cycle gradient** was checked for the loop's inhibitor symptom at level 10 (195 steps). It matches finite
differences of the centre unrolled from the same detached first state over the same steps (gaps 5.7e-10 to 2.1e-9),
which is what "unrolling one cycle of the relaxation and backpropagating through its steps" computes. It does **not**
match finite differences of the whole readout, where the cycle's first state is re-solved too:

| parameter | backward pass (one cycle) | finite difference, same first state | finite difference, whole readout |
| --- | --- | --- | --- |
| weight entry to middle | 0.39039178 | 0.39039178 | 9.69216730 |
| weight middle to inhibitor | 1.01554710 | 1.01554710 | 7.42362915 |
| weight inhibitor to entry | 0.45017285 | 0.45017285 | -4.31038421 |
| full entry input | 0.25440436 | 0.25440436 | 4.55910206 |

**The whole readout is not smooth at this scale.** The profile below is the inhibitor symptom's prediction from the
whole readout, beside the centre from the same first state, at the weight from the entry to the middle node moved by
k x 1e-6:

| offset | whole readout | same first state |
| --- | --- | --- |
| -5e-6 | 2.58381839 | 2.58386934 |
| -4e-6 | 2.58382966 | 2.58386973 |
| -3e-6 | 2.58384059 | 2.58387012 |
| -2e-6 | 2.58385118 | 2.58387051 |
| -1e-6 | 2.58386142 | 2.58387090 |
| 0 | 2.58387129 | 2.58387129 |
| +1e-6 | 2.58388080 | 2.58387168 |
| +2e-6 | 2.58388994 | 2.58387207 |
| +3e-6 | 2.58389869 | 2.58387246 |
| +4e-6 | 2.58387094 | 2.58387285 |
| +5e-6 | 2.58383919 | 2.58387324 |

From -5e-6 to +3e-6 the whole readout rises at about 9 to 11 per unit, 25 times the one-cycle gradient. Between +3e-6
and +4e-6 it drops by 2.8e-5 and then keeps falling. The centre from the same first state rises evenly at 0.39 per
unit throughout. The record does not establish what causes the break. One candidate is that the cycle's first state
or its sampled extremes moved to another step of the long relaxation, but it was not tested.

Item 40 (4) says the unrolled gradient is "the gradient of the value the model predicts". On this loop, it is the
gradient of the centre from a fixed first state. The value the whole readout predicts also depends on where that
first state falls, after the long relaxation that leads to it, and the one-cycle gradient leaves that dependence out.

**At a node that does not move over the cycle, the unrolled gradient is zero.** This is the combined network's switch
symptom at level 10. The switch's nodes are constant over the cycle, so each node's highest and lowest values tie
across all 195 steps. Torch's max and min take the first tied step, which is the detached first state, so no gradient
reaches the switch. The value does move with the switch's weights:

| parameter | backward pass (one cycle) | finite difference, same first state | finite difference, whole readout |
| --- | --- | --- | --- |
| weight partner to entry | 0 | 0.13225693 | 0.29582582 |
| weight entry to partner | 0 | 1.78865930 | 3.66811742 |
| full entry input of the switch | 0 | 0.01542102 | 0.03449299 |
| weight loop middle to loop inhibitor | 0 | 0 | 0 |

The whole readout's finite difference here is the derivative of the switch's steady state, the derivative the
implicit gradient gives at a settled level. The centre from the same first state moves at 0.45 to 0.49 times that
rate.

## 7. Timings, planted networks only

Each timing is the median of 5 runs, on one thread, at step 0.02:

| what | seconds |
| --- | --- |
| one warm-started settled level (the switch's full level, from level 9) | 0.041 |
| one warm-started oscillating level (the loop's full level, from level 9), most of it the two caps of section 3 | 1.956 |
| one unrolled cycle with its backward pass (the loop's full level, 195 steps) | 0.016 |

These are timings of a two-node and a three-node network, on one thread. They say nothing about the confirmatory
graph and are not a basis for item 40 (7)'s time budget.

## 8. What this pilot does not do

- It does not time a level or a cycle on the confirmatory graph, or count the spread of the peak levels there. Both
  wait on the v5 rebuild.
- It does not propose the tolerance or the time budget of item 40 (7), which are proposed for the owner with those
  measurements.
- It does not choose between the readings left open in section 1 (whether rest is read, and the warm start after an
  oscillating level), or decide whether a step-size-dependent oscillation, a zero gradient through a non-oscillating
  node, or the gap between the one-cycle and whole-readout gradients needs anything. Those are the owner's.
- It does not change item 40, row 9.153, the encoder or the trainer. Nothing in them calls the prototype.
