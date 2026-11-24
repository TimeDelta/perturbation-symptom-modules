# Deflation, multistart and continuation for the search of decision 9.138 (Fable pass, 24 November 2026)

Redo of the lost `deflation_multistart_2026-11-17.md`. Model: Fable 5.2 throughout, no fallback. Repository read at
`origin/main` `43b82a8`; nothing in it was edited. Progress log: `deflation_multistart_2026-11-24.progress.md` beside
this file. Saved pages: `deflation_pages/` beside this file (each with its address, time and SHA-256, written by
`experiments/read_public_page.py`; `pdftotext` output beside each PDF). This pass decides nothing; section 6 is a
recommendation and is marked as this pass's reasoning.

How to read the source marks: **[full text]** means the quoted sentence was read in the saved full text;
**[abstract]** means only the abstract or a search excerpt was read; **[record]** means only the bibliographic record
was confirmed. "My reasoning" marks a statement no source was read for.

## 1. What item 37f and decision 9.138 already fix, and what they leave

Fixed by item 37f (`docs/preregistration.md`, lines 2986-3023), registered and not built:

- the update saturates inside the fixed point (soft, Michaelis-Menten or Hill), with a floor at -1 per node and no 0.9
  gain clamp;
- a root-finder with implicit differentiation replaces the damped iteration, "started from rest", and searches "for
  several steady states rather than only the one reached from rest";
- "Only stable roots enter a prediction, and several stable states combine by noisy-OR";
- a missed state "takes its symptoms with it, so the search's incompleteness bears on the prediction and is stated,
  and the search is to be generous with its starting points";
- perturbations at a bifurcation are to be detected and flagged (9.138's wording of what 37f requires).

Left to 9.138, in its own words: "multistart, deflation or a hybrid"; "the stability criterion; the starting states
[...]; and how a root at a bifurcation is handled". The owner's lean is recorded: "i lean towards deflation". 9.138
also says the citations the session offered "are from its own knowledge and are to be checked by a Fable pass before
they are cited anywhere"; section 5 is that check.

**Scale.** The brief's "about 50,000 nodes and 270,000 edges" is not a release. `docs/status.md` (generated 24 November
2026) lists one release, v0.4, whose `graph_full` has 33,964 nodes and 255,367 edges. The 50,000 figure matches the v5
build named in `docs/exploration_item9_design_2026-11-20.md`
(`data/processed/graph_full_neuronal_split_binders_drugs_v5`, files dated 12 November 2026, 49,864 nodes, 275,194
edges). That build is not on this machine; only release v0.4 is. The cost probe of section 4 is therefore on v0.4's
structure and says so.

## 2. The three methods, what each guarantees and what it does not

### 2.1 Deflation

What it is: after a root r of F is found, solve the modified problem G(x) = M(x; r) F(x), where M blows up at r, so
Newton's method cannot return to r; repeat from the same starting state.

Guarantees:

- It will not return a root it already has. Farrell, Birkisson and Funke 2015 [full text]: "Brown and Gearhart prove
  that the deflated Newton sequence will not converge to the previous solution, assuming r is simple." Farrell, Croci
  and Surowiec 2020 [full text]: "A semismooth Newton method applied to G from any initial guess in Z \ {r} will not
  converge to r [...] if semismooth Newton is applied to G, and it converges, it will converge to a distinct solution."
- Roots of the deflated problem are roots of the original one (same paper: "G preserves roots").

Does not guarantee:

- Completeness. Farrell, Birkisson and Funke 2015 [full text]: "While deflation does not guarantee that all solutions
  of the problem will be found, it has proven itself useful". Charalampidis, Kevrekidis and Farrell 2018 [full text of
  the arXiv version]: "there is no guarantee that all of the relevant solutions (for a given parameter value) will be
  obtained in this way, as Newton's method may fail to converge [...] if initialized far from a solution."
- That even a second root is found from the same start. Farrell, Croci and Surowiec 2020, Remark 8 [full text]: "It
  would be of significant interest to derive sufficient conditions guaranteeing the convergence of the same initial
  guess to two distinct solutions via deflation."
- Insensitivity to its own parameters. Farrell, Birkisson and Funke 2015 [full text]: "the algorithm is highly
  sensitive to the choice of the shift parameter. Varying the shift parameter from 10^0, 10^-1, ..., 10^-7, the
  deflation procedure identifies between 1 and 7 solutions. At present we are unable to give a priori guidance on the
  choice of the shift parameter, and reluctantly resort to numerical experimentation."
- Anything about stability. It returns unstable roots as readily as stable ones: in the same paper's Allen-Cahn
  example, from a zero guess, it "finds three solutions (figure 4.2): one unstable solution" and two stable ones.

Conditions it needs:

- Isolated roots. This is the one trace the lost pass left in the repository
  (`docs/exploration_item6_design_2026-11-20.md`, line 211), and it is confirmed: deflation "can successfully identify
  multiple solutions [...] provided they exist and are isolated from each other" (Farrell, Croci and Surowiec 2020
  [full text]); "an isolated root of F, i.e. F'(phi_1) is invertible" (Charalampidis et al. 2018 [full text]). So a
  root at a bifurcation, or a line of roots under an exact conservation law (item 6, option C3), is outside the
  guarantee.
- A Newton-type solver. The whole theory is stated for Newton's method on G, not for a damped or Anderson-accelerated
  fixed-point iteration. My reasoning: 37f's "root-finder" would have to be Newton-Krylov (or a quasi-Newton method
  using the residual norm as its merit function) for the guarantee to apply as stated.
- 37f's floor at -1 is covered if it is a hard maximum: Farrell, Croci and Surowiec 2020 is the deflation theory for
  semismooth residuals of exactly that kind.

### 2.2 Multistart

What it is: run the solver from many starting states and keep the distinct limits. Farrell, Birkisson and Funke 2015
[full text] describe it as the standard: "The typical current approach to finding distinct solutions is to start
Newton's method with many different initial guesses, hoping to find starting points that lie in different basins of
attraction."

Guarantees, all from the global-optimisation literature and all asymptotic:

- With random starts, every root whose basin has positive volume is found with probability tending to 1 as the number
  of starts grows. Rinnooy Kan and Timmer 1987 [abstract]: their multi-level methods "with probability 1, find all
  relevant local minima of the objective function with the smallest possible number of local searches." Jaiswal and
  Larson 2024 [search excerpt of the full text], on that method: it "provides asymptotic guarantees in identifying all
  the local minima assuming all stationary points of the objective function are separated by a positive distance."
- A stopping rule with a stated risk exists. Boender and Rinnooy Kan 1987 [abstract]: "By viewing a set of observed
  minima as a sample from a generalized multinomial distribution whose cells correspond to the local optima [...] we
  obtain the posterior distribution of the number of local optima and of the relative size of their regions of
  attraction."

Does not guarantee:

- Anything at a finite number of starts; a root with a small basin is missed with a probability set by that basin's
  share of the sampled volume (Zilinskas et al. 2019 [search excerpt]: the inference is multinomial in the volumes of
  the regions of attraction, and "The main difficulty is caused by the fact that l [the number of minimizers] is
  usually unknown").
- Efficiency. Zilinskas et al. 2019 [abstract]: "In its pure form, multistart has low efficiency. However, the
  simplicity of multistart [...] make it very attractive especially in high-dimensional problems".
- These results are for minimising a function. They carry to root-finding only as far as "each start converges to the
  attractor whose basin it is in", which holds for a time-stepping or fixed-point solver and not for Newton (my
  reasoning; the sources above do not treat root-finding).

What the solver does to the result (this matters for "only stable roots"): Laing 2014 [full text], on finding fixed
points by iterating the dynamics forward: "Only stable fixed points can be found using this method. For fixed mu there
may be multiple stable fixed points, and which one is found depends on the value of the initial condition, in a way
that may not be obvious." And on Newton: "Newton's method has the advantage that its convergence does not depend on
the stability of the fixed point, and thus it could also be used to find the unstable fixed point". So multistart with
the unclamped iteration returns only roots stable under that iteration, and multistart with Newton returns both kinds,
as deflation does.

### 2.3 Continuation and homotopy (the third standard family)

Farrell, Birkisson and Funke 2015 [full text] name it as the alternative: "There are two main alternative approaches
to identifying distinct solutions of nonlinear systems: numerical continuation, and the approximate integration of the
associated Davidenko differential equation." Three variants are relevant.

**(a) Pseudo-arclength continuation in a parameter.** Follow a known root as a parameter moves, through folds, with
stability read along the branch. Here the natural parameter is the perturbation's strength, from 0 (rest, where the
root is known) to 1. Guarantee: it traces the whole branch connected to the start. Laing 2014 [full text] is an
introduction on high-dimensional neural models. What it does not do: Charalampidis et al. 2018 describe the gap that
deflated continuation fills, "the algorithm is capable of discovering disconnected branches, those not continuously
connected to known solutions" [full text], which plain continuation cannot. (The fuller statement, "disconnected
branches are overlooked", is in Farrell, Beentjes and Birkisson, arXiv 1603.00809, which is excluded; see section 5.)
It is sequential: Aruliah et al. 2012 [search excerpt] call it "an inherently sequential predictor-corrector method"
in which "The most expensive part of the algorithm is computation of the corrector steps (because each corrector step
usually involves solving a linear system of equations)".

**(b) Deflated continuation.** Continuation of every known branch, plus deflation at each parameter step to discover
branches not connected to them. It is what the deflation authors themselves recommend rather than deflation alone:
deflation "provides a powerful complement to continuation methods" (Farrell, Birkisson and Funke 2015 [full text]).
Still incomplete: "While deflated continuation is not guaranteed to compute the full bifurcation diagram"
(Charalampidis et al. 2018, abstract [full text]). Cost: "The only expensive subroutine required by deflated
continuation is the computation of the Newton step of the undeflated system" (same paper). A second peer-reviewed
description: Pintore et al. 2020 [abstract]: "the former is used to entirely track each known branch of the diagram,
while the latter is exploited to discover the new ones."

**(c) Polynomial homotopy continuation.** The only method read that is complete. Mehta 2011 [full text]: "So long as a
system of polynomial equations is known to have only isolated solutions, the NPHC guarantees that we obtain all
complex solutions of the system". Its price is the number of paths: "the maximum number of solutions in C^N is
prod d_i, where d_i is the degree of the ith polynomial", and the homotopy tracks that many paths; the largest system
in that paper has N = 13. A Michaelis-Menten or Hill update can be cleared to polynomial form, but with about 50,000
equations of degree 2 or more the bound is at least 2^50,000 paths. My reasoning from the quoted bound: complete in
principle and out of reach at this scale; it could serve only on a small subnetwork (one feedback module) as a check
of the other methods.

**A fourth route, for part of the graph only.** Angeli, Ferrell and Sontag 2004 [abstract only; according to PubMed,
[doi:10.1073/pnas.0308265100](https://doi.org/10.1073/pnas.0308265100)]: for positive-feedback systems, "Provided that
this open-loop, feedback-blocked system is monotone and possesses a sigmoidal characteristic, the system is guaranteed
to be bistable for some range of feedback strengths", with "a simple graphical method for deducing the stability
behavior". The full text was not obtained, so nothing more is claimed from it; it is named because a guarantee of this
kind, where it applies, is stronger than any search.

## 3. The comparison

| | Deflation (Newton from one or few starts) | Multistart (many starts) | Continuation in perturbation strength, with deflation at each step |
|---|---|---|---|
| Guarantees | never returns a known root; roots are true roots (2.1) | every root with a positive-volume basin, as starts go to infinity (2.2) | the whole branch connected to rest, plus whatever deflation adds (2.3) |
| Does not guarantee | completeness; even a second root; robustness to shift and power | anything at finite starts; small basins | completeness ("not guaranteed to compute the full bifurcation diagram") |
| Returns unstable roots | yes; they are found and then discarded | no if the solver is the iteration; yes if Newton | yes |
| Needs | Newton-type solver; isolated roots | only the forward solver | Newton-type solver; a step size in the parameter |
| Forward cost per perturbation | (K+1) Newton solves for K roots: the last one must fail, running to the iteration cap | M solves, independent, batched | (steps) x (branches) Newton solves, plus a deflated attempt per step |
| Parallel | sequential in the roots | fully parallel | sequential in the parameter |
| Seeds | none: deterministic from a fixed start | seed-dependent if starts are random; deterministic if starts are a fixed list | none |

Notes on the rows, which are my reasoning except where a source is named:

- **The failing solve.** Deflation stops when "Newton's method no longer converges to any solution within a fixed
  amount of work" (Charalampidis et al. 2018 [full text]); the 2015 paper used "100 maximum iterations". So every
  perturbation, including the (probably large) majority with one steady state, pays one full failed solve. The cap is
  therefore both the main cost and part of the definition of "found".
- **Reproducibility.** Deflation from rest has no random element; two runs differ only through solver tolerances. But
  it is sensitive in another way: the 2015 paper's count of roots moved between 1 and 7 with the shift parameter, so
  the result is reproducible across seeds and fragile across settings. Multistart with random starts varies with the
  seed exactly for the roots that matter (small basins); with a fixed list of starts, or a fixed low-discrepancy
  sequence, it is as reproducible as deflation. In about 50,000 dimensions, independent uniform random starts are
  nearly alike in every summary (each node is drawn independently), so they are a poor way to reach a basin defined by
  a few nodes of one feedback loop; starts built from the structure (rest; each positive-feedback module at its floor
  or ceiling) target such basins and random ones do not.
- **Stability check, the same for all three.** Linearise at the root and compute the leading eigenvalue of the
  Jacobian without forming a dense matrix. Laing 2014 [full text]: "we need the eigenvalues of J, or at least a few
  with the largest real part, to determine stability. The Matlab function eigs does not need J, only its product with
  an arbitrary vector". Lehoucq and Salinger 2001 [abstract] did this at "matrix systems of order up to 4 million".
  The check is itself iterative and can err: Meerbergen, Spence and Roose 1994 [abstract], "rational preconditioners
  are very reliable in general but they can miss rightmost eigenvalues with large imaginary part"; Rostami and Xue
  2018 [abstract], "Commonly used transformations such as shift-invert are unreliable and may cause convergence to a
  wrong eigenvalue". So "stable" is a computed verdict with its own tolerance, and a missed unstable eigenvalue admits
  an unstable root into a prediction.
- **Which stability.** No source read settles this, and it is the owner's to rule (section 6). For a root of
  x = g(x) with Jacobian Dg: under the plain iteration it is stable when every eigenvalue of Dg has modulus below 1;
  under the relaxation dx/dt = g(x) - x it is stable when every eigenvalue has real part below 1; under a damped
  iteration the region lies between the two. An eigenvalue of -2 (a strong negative feedback) is unstable under the
  first and stable under the second. The encoder's own docstring says "damping sets the transient only"; that is true
  of where the roots are and not of which of them are stable. And 37f records that "a round is not physical time
  while the relations carry no timescale": with per-node time constants, stability can depend on them, so until
  timescales exist any criterion is a convention.
- **Implicit differentiation, the same for all three.** The gradient is taken at each root of the original F and does
  not see how the root was found: Bai, Kolter and Koltun 2019 [full text], "this result is independent of the
  root-finding algorithm we choose". So the deflation operator never enters a gradient. What it needs is an invertible
  Jacobian at the root: Blondel et al. 2022 [full text], the framework applies "if I - d1T(x*(theta), theta) is
  invertible" and "theoretically only applies to settings where the implicit function theorem is valid". That fails
  exactly at a fold, where a stable and an unstable root merge; this is the same condition as deflation's "isolated"
  and the same event 37f wants flagged, so one quantity (how close the Jacobian is to singular) can serve all three
  purposes. Each stable root costs one more linear solve backward. Two consequences are my reasoning: (i) the noisy-OR
  over the stable roots is discontinuous in the parameters wherever a root appears, disappears or changes stability,
  whatever the search; (ii) an incomplete search adds a second discontinuity, a root found in one epoch and missed in
  the next, which a deterministic search makes repeatable but not smooth.
- **Uniqueness is not the default.** Winston and Kolter 2020 [full text]: in deep equilibrium models "solutions [...]
  are not guaranteed to exist or be unique, making the output of the models potentially ill-defined"; their remedy is
  a constraint that "guarantees stable convergence to a unique fixed point", which is what the 0.9 gain clamp did and
  37f removed. Anil et al. 2022 [full text] name the property the multistart question turns on: "path independence",
  the "tendency to converge to the same steady-state behaviour regardless of initialization".

## 4. Cost at this project's scale

Measured on 24 November 2026 with `deflation_cost_probe.py` (scratchpad), on **the structure of release v0.4
`graph_full` only** (33,811 nodes carrying edges, 249,869 distinct entries), with **synthetic weights** (sign times
0.9 over the row sum), a tanh update and a random state, on 4 CPU cores. It is not a measurement of the encoder, of
the v5 build or of 37f's update, none of which could be run; it sizes the linear algebra only, and its weights are
contractive by construction, which is the easy case.

| Operation | Time | Where it is used |
|---|---|---|
| one sparse product with the adjacency | 0.6 ms | every step of an iteration; every Krylov step |
| sparse direct LU of the Jacobian | 25 s, 26.9 million nonzeros (95 times fill) | a Newton step by direct solve |
| one solve with that LU | 0.05 s | |
| GMRES(50), no preconditioner, to 1e-8 | 40 iterations, 6.1 s (untuned) | a Newton step by Krylov solve; the backward solve |
| six leading eigenvalues (largest real part; largest modulus) | 6.1 s; 6.9 s | the stability check |

Reading it (my reasoning): the pattern does not factor cheaply, so Newton by direct factorisation is out inside a
training loop and deflation means Newton-Krylov. Deflation adds almost nothing per step to that: "the deflated
Jacobian is dense" but "is a rank-one perturbation" handled by "the Sherman-Morrison formula", and "the number of
Krylov iterations is observed not to grow as solutions are deflated" (Farrell, Birkisson and Funke 2015 [full text]).
The cost that scales is the count: with the 1,655 perturbations of v0.4's `evidence_full`, deflation runs at least two
Newton solves per perturbation per pass (the root and the failed attempt), each of several Krylov solves, plus an
eigenvalue computation per root. Multistart with the iteration costs M batched iterations of sparse products and no
linear solves forward. Continuation multiplies deflation's cost by the number of parameter steps. With unclamped
gains the Jacobian near a fold is nearly singular and every Krylov figure above gets worse.

## 5. The citations the rows offered "from the session's own knowledge", checked

| Citation in the rows | Finding |
|---|---|
| Farrell, Birkisson and Funke 2015 (deflation) | Exists: "Deflation Techniques for Finding Distinct Solutions of Nonlinear Partial Differential Equations", SIAM J Sci Comput 37(4):A2026-A2045, doi 10.1137/140984798 (Crossref). Read in full as arXiv 1410.5620v2; the Crossref abstract matches. It supports what the rows use it for. |
| Bai, Kolter and Koltun 2019 (implicit function theorem backward) | Exists (`bai2019deep` in `docs/references.bib`); read in full as arXiv 1909.01377. It supports the backward pass. **Correction:** its forward solver is Broyden's method, not Anderson acceleration, and it starts from zero; the rulings draft's "Anderson acceleration forward, the implicit function theorem backward; Bai, Kolter and Koltun 2019 and Walker and Ni 2011" should not be read as Bai et al. using Anderson. It says nothing about several equilibria. |
| Walker and Ni 2011 (Anderson acceleration) | Exists: "Anderson Acceleration for Fixed-Point Iterations", SIAM J Numer Anal 49(4):1715-1735, doi 10.1137/10078356X. **Abstract only** (Crossref): relates the method to quasi-Newton updating and shows it "essentially equivalent" to GMRES on linear problems. Full text is behind SIAM's subscription and was not read. |
| Farrell, Croci and Surowiec 2020 (the lost pass's "isolated from each other") | Exists: "Deflation for semismooth equations", Optim Methods Softw 35(6):1248-1271, doi 10.1080/10556788.2019.1613655. Read in full as arXiv 1904.13299v1; the quotation is confirmed word for word. |

Also met:

- **Brown and Gearhart 1971**, Numer Math 16:334-342, doi 10.1007/BF02165004: record only (Crossref, which misspells
  the first author "Brow"). Its lemma is used here only as Farrell et al. state it.
- **Farrell, Beentjes and Birkisson, "The computation of disconnected bifurcation diagrams", arXiv 1603.00809**
  (2 March 2016): read in full, but Crossref holds no journal record and Consensus lists it as a preprint. Posted more
  than 18 months ago with no peer-reviewed version found, so under the preprint rule of `CLAUDE.md` it is **excluded**:
  nothing in this report rests on it, and deflated continuation is cited from Charalampidis, Kevrekidis and Farrell
  2018 (Commun Nonlinear Sci Numer Simul 54:482-499, doi 10.1016/j.cnsns.2017.05.024) and Pintore et al. 2020.
- Winston and Kolter 2020, Blondel et al. 2022 and Anil et al. 2022 are NeurIPS papers (programme-committee review),
  read as their arXiv versions. Blondel et al. is confirmed in Crossref's NeurIPS 2022 record; the other two venues
  are as printed on the papers and were not confirmed against a second record.

None of these is in `docs/references.bib` except `bai2019deep`; no entry was built, the repository not being edited.

## 6. What the owner has to choose, and a recommendation

### What is open (each is the owner's; none is decided here)

1. **The search**: deflation, multistart, or a hybrid; and whether the perturbation is ramped from 0 (continuation)
   or switched on at full strength.
2. **The solver the search runs on.** Deflation's guarantee is for Newton. If 37f's root-finder is Anderson or
   Broyden on the fixed-point map, either the solver changes or the guarantee is not the one in the literature.
3. **The stability criterion**: under which dynamics a root is called stable (iteration, damped iteration,
   relaxation), with what margin, and by which eigenvalue computation. By the physiology rule this should be the
   dynamics closest to the tissue's, and 37f says the timescales that would define it are not there yet.
4. **The starting states**: rest only; rest plus a fixed structural list; random with a seed; and how many.
5. **The deflation settings**, if deflation is used: power, shift, the iteration cap that defines "no further root",
   and the distance at which two roots count as one.
6. **Bifurcations**: the threshold on near-singularity that flags a root, and whether a flagged root enters the
   noisy-OR, is dropped, or is reported beside the prediction.
7. **How incompleteness is stated**, which 37f requires: for example roots found, unstable roots discarded, failed
   solves and flagged roots, per perturbation.
8. **Training against evaluation**: whether the full search runs inside training or only at evaluation. Running it
   only at evaluation changes the tested model between the two and would need its own justification.
9. **Non-isolated roots**: if item 6 puts conservation into the dynamics, roots form lines and both deflation and the
   stability check need the reduced coordinates of option C3 first.

### Recommendation (this pass's reasoning, not a ruling)

**A hybrid whose core is deflation, as the owner leans: deflation run from rest and from a short fixed list of
structural starting states, each new solve deflated against every root already found, with the stability check
applied afterwards.** The reasons:

- It is deterministic, so a prediction does not depend on a seed, and it never spends a solve rediscovering a root,
  which is where plain multistart spends most of its budget.
- The fixed list of starts answers 37f's "generous with its starting points" and covers deflation's known weakness,
  that nothing guarantees a second root from one start (Remark 8 above). It is how the deflation authors use it
  themselves: as a complement to other sources of starting points, not alone.
- It finds the unstable roots as well. They do not enter a prediction, but an unstable root between two stable ones
  is the evidence that a perturbation is at a switch, and a root that is nearly singular is the bifurcation flag 37f
  asks for; a search that only ever sees stable roots (multistart on the iteration) has neither.
- Continuation in the perturbation's strength is the most physiological reading (a dose rising from zero, with
  hysteresis), and I would name it as the direction to go if the pilot below shows states that the fixed-strength
  search misses; its cost, several times that of deflation, is the stated numerical reason not to start there.

Three things I would put before the owner with it:

- **The literature does not rank deflation against multistart on a system like this one.** Every deflation result
  read is on discretised differential equations or small complementarity problems; every multistart guarantee is
  asymptotic and from optimisation. The honest basis for a choice is a pilot: a small network with a planted bistable
  switch, where the true set of steady states is known (and can be confirmed completely by polynomial homotopy at that
  size), run through both searches with the registered update. That is engineering once the choices above are made.
- **Most perturbations may have one steady state.** 37f already owes "a count of positive-feedback cycles" before the
  build. Where a perturbation's Jacobian can be bounded as a contraction over the whole box between floor and
  headroom, the steady state is unique and no search is needed; running that check first would confine the search,
  and its failed final solve, to the perturbations that can be multistable at all. This is my suggestion and no source
  was read for it.
- **The case against the lean**, so it is weighed: deflation forces a Newton-Krylov solver and one failed solve per
  perturbation, is sensitive to settings its own authors could not give guidance on, and returns unstable roots that
  are then thrown away; multistart on the unclamped iteration needs no linear solves forward, batches on a GPU,
  returns only roots stable under the iteration, and uses the solver 37f already registers for the per-round
  readings. If the stability criterion is ruled to be stability under that iteration, multistart computes exactly the
  set the prediction wants, and its weakness is only the choice of starts.

## 7. What could not be read, and limits

- **Walker and Ni 2011**: abstract only (subscription). **Brown and Gearhart 1971**: record only.
- **Rinnooy Kan and Timmer 1987, Boender and Rinnooy Kan 1987**: abstracts only (Consensus); **Jaiswal and Larson
  2024, Zilinskas et al. 2019, Aruliah et al. 2012, Pintore et al. 2020**: abstract and search excerpts only.
- **Meerbergen, Spence and Roose 1994; Lehoucq and Salinger 2001; Rostami and Xue 2018**: abstracts only.
- **Angeli, Ferrell and Sontag 2004**: abstract only. Europe PMC's full-text service answered HTTP 500 for PMC357011
  (a transient error, not a refusal, and the record is not open access there); the PubMed connector returned no full
  text. Not retried on another host.
- **Allgower and Georg, "Numerical Continuation Methods"** (the standard book) and the Davidenko-equation route the
  2015 paper names were not read; continuation rests on Laing 2014 and the deflation papers.
- No permission request was made or left unanswered; every page was read from the shell with
  `experiments/read_public_page.py` (arXiv, Crossref's REST service, Europe PMC's REST service at under one request a
  second) or through the Consensus and PubMed connectors. No site refused.
- Second sources: each guarantee and each non-guarantee of deflation has two (the 2015 paper and either the 2020
  semismooth paper or Charalampidis 2018), though all share one author, Farrell, so they are not independent in the
  sense of the curation rule; no deflation source without him was read. Multistart's asymptotic guarantee has two
  (Rinnooy Kan and Timmer; Jaiswal and Larson, the second reporting the first). The implicit-function condition has
  two independent ones (Bai et al.; Blondel et al.). The stability check has several independent ones. Polynomial
  homotopy's completeness rests on Mehta 2011 alone.
- The cost probe is on release v0.4's structure with synthetic contractive weights (section 4). The v5 build was not
  available, and nothing was measured on the encoder.
- Statements marked "my reasoning" (the dependence of stability on the dynamics chosen, the behaviour of random
  starts in high dimension, the contraction pre-check, the discontinuities of the noisy-OR) have no source read for
  them and should be checked before any is written into a decision row.
