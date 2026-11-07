# Exploration queue

Ideas parked for later so they stop taking up working memory. Nothing here is registered or required for the
confirmatory analysis, and nothing here is started. An item names what it would change, what it would cost and the
limits that must not be overstated when it is written up.

This document moved into the repository on 26 October 2026 from the Project note `claude/exploration_queue.md`
(**that note was deleted on 27 October 2026**, when the owner ruled the repository the single source of truth: "Everything should rely on the repo moving forward"; it is named here as the provenance of this page and not as a document to read),
under the owner's standing rule that sources are recorded in the repository. Items 1 to 4 are carried over as they
were tagged; items 5 and 6 are new, both added on 26 October 2026, items 7 and 8 were added on 27 October 2026, item 9 on 28 October 2026, and item 10 on 4 November 2026.

Checked against `main` at `0b976bf` on 26 October 2026, and again at `0fd0139` on 4 November 2026. Item 8 carries
literature read on Opus and not yet rechecked on Fable (its source `lee2015cytoplasmic`, read on 24 October 2026),
flagged where it stands; the item is parked, so nothing relies on it. Item 5's literature, read on Opus on 26 October
2026, was rechecked on Fable on 7 November 2026.

Added 27 October 2026: the owner retired the two readout records (`docs/steady_state_readout_alternatives.md`,
`docs/fixed_point_against_pharmacological_steady_state.md`) as evidence and ruled that "ANY numbers from that time are
to have the same treatment", the slice-pilot measurements of 3 to 8 October 2026 (decisions 9.103 and 9.104). Checked
against every item on this page that day: items 4 and 6 build on those records' derivations (item 4 on section 1.2's
state dependence, item 6 on section 3.4's Tikhonov partition), which the ruling's words, being about numbers, do not reach; whether
they do is the owner's to say (9.104). One item cites a count on the v0.4 slice graph: item 6's "49 de novo edges
against 1,030 redistribution edges on the v0.4 slice" (`docs/coproduct_of_de_novo_split_2026-10-26.md`), measured on
26 October 2026, so outside the period by date and on an earlier graph; it is kept with its graph named, as CLAUDE.md
"Modelling" requires, and the owner may extend the ruling to it. No item cites finding 10 or any other number of the
retired table.

## Priority order (7 November 2026)

The owner asked on 7 November 2026 to "prioritize the exploration queue and start the next few items". The order is
the session's (on Opus), by four tests: how much closer to physiology the item brings the model (CLAUDE.md
"Modelling"), whether its first step can run now that the v5 drug graph exists (decision 9.106), what it costs, and
whether the owner can follow it. Items 7, 9 and 6 were started that day (their measurements are dated additions in
each item); item 5's Fable recheck was started the same day. So the sentence above that "nothing here is started" no
longer holds for those four.

1. **Item 7, endosomal pH (SLC9A6, SLC9A9).** A monogenic gene with psychiatric phenotypes turns out to be absent from
   the graph, so its labels are lost; cheap to measure, a data-layer change to fix.
2. **Item 9, the Krebs cycle and oxidative burden.** The route the physiology needs is missing by construction; the
   fix is one owner ruling (a metabolite-driven `produces_oxidant`) plus sourced rows.
3. **Item 6, the fast/slow partition and the `coproduct_of` split.** Its sources were re-read on 6 November 2026 and
   the split is computable from the stoichiometry, so it is ready for the owner's ruling on the split.
4. **Item 5, occupancy as the drug seed magnitude.** Most of the data exists; its literature needed a Fable recheck,
   started 7 November 2026; then the cheap field-level measurement.
5. **Item 10, the shunt.** A literature pass to count the perturbations whose main mechanism is shunting inhibition,
   so the 9.112 limit is counted rather than described.
6. **Item 4, phosphorylation.** One Fable count decides whether to drop it.
7. **Item 2, CollecTRI sign recuration.** Cheap research; it feeds a sign prior rather than a mechanism.
8. **Item 1, sensitivity-matrix rank.** Methodologically strong but heavy; better after the 9.112 rebuild, when
   the operator it would factor is the one that will be tested.
9. **Item 8, the VAMP1 share.** Small expected effect on one membership weight.
10. **Item 3, protein electrostatics.** The largest change and the hardest to follow; stays parked.

---

## 1. Sensitivity-matrix rank as a bound on multiverse degrees of freedom

Tagged 2026-10-22.

**The idea.** Build the matrix of first-order sensitivities of each labeled outcome node to each of the 3,795
sign-disputed edges, one adjoint solve per labeled outcome against a cached factorization of (I - A). Its numerical
rank, with tolerance set by label noise, upper-bounds how many independent directions the entire branch multiverse
can move predictions in. If that rank is small relative to 3,795, most of the apparent combinatorial explosion is
bookkeeping rather than distinct scientific questions.

**Two companion reductions.**
- Rank-one update per branch: flipping one edge's sign is a rank-one change to A, so Woodbury gives the exact
  updated steady state from the cached factorization instead of a full fixed-point run.
- Equivalence classing: disputed edges in series affect a downstream label only through the product of their signs,
  so many distinct assignments give identical predictions and collapse into one class.

**Why it matters methodologically.** Every pair of branches the compression merges is a pair the labels cannot
distinguish. The compression ratio and the identifiability audit are the same quantity viewed from two sides.

**Known limits (do not overstate these in writing).**
- First-order and linearized; a sign flip is a finite jump.
- The rank depends on the chosen tolerance.
- Bounds movement in predictions, not the count of answerable sign questions; the `class_bottleneck` min across
  classes is not injective and will merge more branches than identifiability alone would.
- Clean only for the linear-response encoder. No closed-form steady state for message passing. In-loop aggregators
  (`CrossRelationAggregator`) would break all three reductions; they are off by default.

**Candidate transfer to neuroscience (unverified, worth a literature pass).** The shape of this result resembles
degeneracy in neural circuits, where many distinct parameter sets produce the same observed activity. Starting
points to check: Prinz, Bucher and Marder on similar network activity from disparate circuit parameters; Marder and
Goaillard on variability and homeostasis; Gutenkunst et al. on sloppy parameter sensitivities, already cited
elsewhere in this project. Open question is whether the low-rank sensitivity structure here is the same phenomenon
as circuit degeneracy or only an analogy.

---

## 2. Larger seeded recuration of disputed CollecTRI signs

Tagged 2026-10-22.

The current recuration rests on 11 decidable pairs, with the stored sign right on 7
(`docs/regulation_sign_recuration.md`). The posterior interval runs roughly 0.35 to 0.85, too wide to set a
latent-sign prior from. A larger seeded sample is cheap and would be worth more than further analysis of the
existing 11.

---

## 3. Protein electrostatics and molecular interaction mechanisms as inputs

Tagged 2026-10-24. Owner's idea; no literature pass yet.

**The idea.** Bring protein biophysics into the physiology: electric field representations of proteins
(Poisson-Boltzmann potentials; FFT-based long-range electrostatics as in particle-mesh Ewald) and other molecular
interaction mechanisms, possibly with the contraction bound removed so the model carries dynamics.

**Where it lands in the existing inventory.** Not new as a goal. The mechanisms it names are cases 1, 2, 4 and 5 of
`docs/nonlinearity_inventory.md` (competition, partial agonism, desensitisation, occupancy). Removing the
contraction bound is case 8 and open question 1 of the same file.

**The readout problem.** The graph carries no rate constants, so without the fixed point there is no clock to say
when to read. Candidates, none clean:
- deep equilibrium (Bai, Kolter and Koltun 2019): keep the fixed point, allow saturation inside it, keep uniqueness
  with a non-expansive map;
- long-time average, which returns the fixed point whenever the system is stable and is the readout the
  chronic-dosing labels imply;
- attractor reached from the baseline attractor under the perturbation, which needs rates to define settling.

**Most defensible entry point.** A prior on `binds` edges (precision 8.2% against HuRI) from structure-based
affinity, which is a data-layer change reviewed like any other edge prior, not a change to propagation.

**Known limits (do not overstate these in writing).**
- The model is dimensionless in time; iteration count is not time.
- `VM_c` is the only electrical node and is compartment scale; protein-scale fields do not meet it in the
  propagation.
- A new encoder amends the confirmatory family, which since 22 October 2026 is one tested model (the
  linear-response encoder; decision 9.77), and with it the multiplicity budget.

**Status.** Parked behind the qualifying exam.

---

## 4. Protein phosphorylation as an explicit relation or as site nodes

Tagged 2026-10-26. Owner's question. Answered on Opus from repository files and general knowledge; no literature
pass on Fable yet.

**Where it stands in the graph.** Kinase effects enter as OmniPath `activates` and `inhibits` edges.
`configs/go_not_edge_rules.csv`: "no relation of the graph states phosphorylation (OmniPath's activates and inhibits
do not say how they act)". GRK and arrestin edges onto receptors are already set to -1 by decision 9.10(a)
(`configs/curated_edge_sign_overrides.csv`).

**Why not as propagation.** Under the linear-response encoder a kinase and a phosphatase acting on one substrate are
two edges of opposite sign into one node, which the graph already has. What phosphorylation does beyond that
(ultrasensitivity from opposed enzymes near saturation, Goldbeter and Koshland 1981; multisite thresholds;
desensitisation) is a saturation or a product of states. `docs/steady_state_readout_alternatives.md` section 1.2
places desensitisation outside linearity. Phosphorylation is fast, so its rate drops out of every fixed point and it
sits in the fast set of R2's partition. Site nodes would be relays carrying the same net sign, adding path length
and in-degree dilution.

**Entry point: edge sign.** A kinase can act on one substrate at an activating site and at an inhibitory site (named
in `docs/label_source_review.md`), and OmniPath's consensus sign collapses the two, the same failure mode as 9.72.
Site-level function annotations (PhosphoSitePlus regulatory sites; SIGNOR residue-level entries) could supply sign
evidence as an edge prior on the data layer, reviewed like any other edge prior.

**The measurement that decides it (research, so on Fable).** On the current graph, count kinase-to-substrate edges
whose substrate has both activating and inhibitory sites annotated for that kinase, then count how many of those
touch perturbed genes or lie on paths to labelled symptoms. If the count is small, drop this item.

**Known limits (do not overstate these in writing).**
- Most phosphosites have no annotated function (Needham et al. 2019, Sci Signal, `needham2019darkphosphoproteome`;
  verified 1 November 2026: "functional assignments of phosphosites are almost negligible" and kinases are
  identified for "less than 5% of the phosphoproteome", abstract read through PubMed 30670635 and confirmed
  against Europe PMC).
- Desensitisation as a mechanism waits on case 4 of `docs/nonlinearity_inventory.md`; explicit phosphorylation adds
  nothing there until saturation enters the propagation.

**Status.** Parked behind the decisions in `docs/status.md`. Until 4 November 2026 this line also parked it behind the
qualifying exam and the 9.97 cyclase handoff. The owner, 27 October 2026: "i disagree with gating things behind the
qualifying exam because this project IS the qualifying exam. i just need to make sure it doesn't go too far for me to
be able to understand the project", so what bounds an item is whether the owner can follow it, not the exam. The
cyclase handoff is worked through: both of 9.97's questions were ruled on 2 November 2026 and no Gi/o-to-cyclase edge
changes on them; what remains of 9.97 is the form of the G beta gamma conjunction and, after the rebuild, the sign
sweep of 9.86 before 9.80 is decided.

**The decisive count, measured 7 November 2026 on v5 (Fable).** SIGNOR 4.0, October 2026 release (CC BY 4.0,
"SIGNOR 4.0 is licensed under Creative Commons Attribution 4.0 International", signor.uniroma2.it/documentation,
read that day), is the one open source that states per residue which kinase and which effect: of its 5,514 human
kinase-substrate phosphorylation pairs, 76 carry at least one up-regulating and one down-regulating residue (61 at
distinct residues, 15 with one residue annotated both ways). **34 of the 76 are v5 `activates`/`inhibits` edges**
(0.04 percent of 84,866 protein-to-protein signalling edges, 22 kinases); **28 touch a perturbed gene or drug
target** (SCN5A, TP53). v5 has no symptom nodes, so "paths to labelled symptoms" was read as paths from
perturbed genes. The stored sign agrees with SIGNOR's site majority on 18, disagrees on 6, ties on 9, and v5 holds
both signs for 1. OmniPath's `enzsub` carries sites with no effect field; PhosphoSitePlus answered with a sign-in
form (a refusal); iPTMnet's files carry no effect field and its licence pages contradict each other (CC BY-NC-SA
4.0 on the site, CC BY 4.0 at the foot of the README). **By the item's own test the count is small, so the
pass recommends dropping the representation question; that is the owner's to decide.** The 16 edges whose sign SIGNOR disputes are a
sign-evidence candidate for the override table, not a reason to keep the item. Record:
`docs/phosphosite_opposite_effects_2026-11-07.md`; source `losurdo2026signor`.

---

## 5. Occupancy as the drug seed magnitude

Tagged 2026-10-26. The owner's question of 26 October 2026, on reading that a drug enters at magnitude 1: "But
complete removal seems harsh". Written on Opus from repository files; the literature below was read on Opus and
rechecked on Fable on 7 November 2026 (CLAUDE.md "Models").

**The idea.** Replace the unit seed magnitude of a drug perturbation by the drug's occupancy at each target, so a
drug that engages 40 percent of one target and 95 percent of another enters as 0.40 and 0.95 rather than as a unit
split evenly between them.

**Most of the data is already in the repository, which is the main reason to record this rather than scope it from
scratch.** `experiments/measure_target_occupancy.py` writes `docs/target_occupancy_measured.md` on the 222 drugs of
`data/processed/evidence_full_v4`, with occupancy `C / (C + K)` at each target's own site, `C` from
`docs/drug_exposure_table.md` and `K` the larger of the DrugCentral and Guide to PHARMACOLOGY affinities. 115 drugs
have a concentration and an affinity at one or more mechanism genes, over 305 drug-gene pairs; items 5c and 29
calibrate an imputed concentration for a further 68 drugs
(`mechanistic_pathway_learning/perturbation/occupancy_calibration.py`,
`docs/occupancy_coverage_and_shift_transfer.md`), so 183 of 222 drugs already carry a mechanism-target occupancy on
one scale.

**What is not built is the wiring.** `map_drug_targets_to_graph_nodes.py` seeds each mechanism target with
magnitude 1 spread over its graph nodes, and item 5 of the preregistration records that the occupancy anchor "binds
nothing yet" because no registered input reads an off-target. The occupancy machinery exists for off-target scoping
and for the `has_measured_occupancy` stratum, not for the magnitude a drug enters with.

**Three measured facts that set what the change would do**, all from `docs/target_occupancy_measured.md` at the
high end of the therapeutic range. The first is read at each target's own site; the second and third are from that
document's unbound-plasma section, which is the one that reports them:
- The best-bound mechanism target has a median occupancy of 0.90, quartiles 0.63 and 0.98: at or above 0.9 for 59
  of 115 drugs and below 0.5 for 23. So the change is not a uniform shrink.
- Within a drug, for the 75 drugs with an affinity at two or more mechanism genes, the occupancies differ by a
  median of 0.17, and by 0.5 or more for 12 drugs. A unit input split evenly treats them as equal. Read at the
  unbound brain concentration instead, over the 44 drugs that have one, the median difference is 0.34.
- Summing a drug's mechanism occupancies gives a median total of 1.18 against the current total of 1, so the
  overall scale barely moves and the change is almost entirely in how the input is distributed.

**What it would cost.** A change to how a drug perturbation enters is a change to a registered perturbation model,
so it needs an `Amends:` trailer and a dated amendment. Decision 1.3(c) already settles that occupancy is not
required of every drug (the owner, 13 October 2026: "Don't REQUIRE occupancy though"), so the 39 drugs with no
affinity would keep a unit seed and the arm would carry two scales in one column unless the owner rules otherwise.

**The cheapest measurement, before any amendment.** The linear-response encoder's field is linear in the input, so
rescaling a drug's seeds is a reweighting of the per-target responses and the new field can be read without a fresh
fixed-point solve wherever per-target responses are cached. That gives the size of the change on the field for
nothing. The head is not linear, so a prediction-level reading needs a pass.

**What the literature says, read on Opus on 26 October 2026 and rechecked on Fable on 7 November 2026.** The recheck
read each PubMed record and confirmed it against Europe PMC; every number below is in the abstract as both hold it.
None of the four is open access, so only the abstracts are held. All four are peer-reviewed journal articles
(decision 9.101). The recheck corrected one word (Meyer: "mean") and added the experimental design to Ghabrial.
- Occupancy at therapeutic doses is high but far from complete, and it varies within one drug: haloperidol at 1.0
  or 2.5 mg/day gave D2 occupancies of 38 to 87 percent across 22 first-episode patients, measured at two weeks on
  the assigned dose (non-responders were then raised to 5.0 mg/day for the four-week evaluation), with the
  likelihood of response, hyperprolactinaemia and extrapyramidal effects increasing significantly as occupancy
  exceeded 65, 72 and 78 percent (Kapur et al. 2000,
  [doi:10.1176/appi.ajp.157.4.514](https://doi.org/10.1176/appi.ajp.157.4.514); `kapur2000relationship` in
  `docs/references.bib`).
- Five serotonin reuptake inhibitors (citalopram, fluoxetine, sertraline, paroxetine and extended-release
  venlafaxine, which the paper counts as its five SSRIs) at their minimum therapeutic doses gave a mean striatal
  serotonin-transporter occupancy of 76 to 85 percent, and for each drug "as the dose (or plasma level) increased,
  occupancy increased nonlinearly, with a plateau for higher doses" (Meyer et al. 2004,
  [doi:10.1176/appi.ajp.161.5.826](https://doi.org/10.1176/appi.ajp.161.5.826)).
- Dose is the wrong anchor, which is why the measured concentration is the right one: saturable presystemic
  metabolism is "one of the more important sources of nonlinearity", named for verapamil, propranolol and
  hydralazine, and makes circulating concentration "sensitive not only to dose size but also to rate of
  absorption", though the same review closes by noting that "only a few of the many hundreds of drugs in use
  exhibit nonlinear behaviour that leads to clinical implications", so the argument holds for a minority of drugs
  (Ludden 1991, [doi:10.2165/00003088-199120060-00001](https://doi.org/10.2165/00003088-199120060-00001)). In the
  isolated perfused rat liver propranolol's bioavailability rose from 0.012 to 0.288 as the inflow concentration
  rose about four-fold (4.97 to 20.4 micromolar) in a recirculating design, and from 0.0077 to 0.136 in a single-pass
  design; the paper attributes the difference to product inhibition by accumulating metabolites, so the larger rise
  is partly an artefact of recirculation (Ghabrial et al. 1994,
  [doi:10.1002/jps.2600830704](https://doi.org/10.1002/jps.2600830704)).

**Known limits (do not overstate these in writing).**
- Occupancy is not effect. For an antagonist the change in signalling depends on the endogenous tone at that
  target, which no source in this repository constrains; that is case 2 of `docs/nonlinearity_inventory.md`.
- It does not touch the knockout-against-inhibitor conflation of `docs/physiological_adherence_review.md` section
  11. A drug at 0.8 and a lifelong knockout at 1 would still differ only in magnitude, not in developmental timing
  or in which cells are reached.
- 39 of the 222 drugs have no affinity at any mechanism gene, so no occupancy exists for them at all.
- The brain-side concentration rests on a `Kp,uu,brain` that is available for 94 of 222 drugs and is human for 13
  (`docs/drug_exposure_table.md`), so most per-target occupancies read in brain inherit an animal ratio.
- EC50 and IC50 values are pooled with Ki and Kd, active metabolites are not added to the parent, and a drug that
  is not a reversible ligand (an irreversible inhibitor such as vigabatrin, a prodrug, a releaser) is not described
  by one-site occupancy at all.
- Summed occupancy correlates with the number of targets counted at 0.84, so an occupancy input carries some of the
  same degree information the drug-node flag was criticised for in `docs/drug_entry_nodes.md`.

**Status.** Parked. Not on the critical path of the 9.97 cyclase handoff, the lockbox sequence or the steady-state
arms R0, R1 and R5, and it cannot be scored on the 1,067 HPO pairs, which carry no drug perturbations.

---

## 6. The fast/slow partition as a function of the observation time, and the conserved-moiety constraint

Tagged 2026-10-26, from the owner's question of that date about pulling timeframe ranges per edge type, and their
refinement that what matters is only which side of an observation time a relation falls on.

**What it is.** The Tikhonov partition of `docs/fixed_point_against_pharmacological_steady_state.md` section 3.4
splits relations into a fast layer and a slow layer, and "Rates enter only through membership in F and S". The slow
set is currently proposed as `{regulates_transcription_of, encodes}` — a proposal, not code: `git grep` finds it only
in documents and the masked loop is a sketch. The idea is to replace the fixed list with an ordering plus thresholds,
so membership is derived for each label class's observation time rather than asserted once.

**Why that is better than a rate table.** Rates cannot enter the update: at the fixed point every rate drops out, and
a per-relation rate changes the transient of the full system and nothing else. Membership is the only channel rates
have. And a fixed list can serve only one observation time, which the sourcing in
`docs/relation_timescale_ordering_2026-10-26.md` shows is a real problem rather than a hypothetical one: at about two
hours the proposed slow set is defensible and transcription already straddles, while at about six weeks transcription
is fast and `encodes` straddles, inverting it.

**What is already done.** `docs/relation_timescale_ordering_2026-10-26.md` bins the relations against about 2 hours,
6 weeks and 1 year, with the straddling set reported as a finding rather than a gap, and corrects section 3.4's claim
that the band is "a few hundred nodes": that holds at 6 weeks and 1 year and fails at 2 hours, where the band is
thousands of edges over at least five relations.

**The conserved-moiety half.** A conserved moiety has two timescales, not one: redistribution among its forms is fast
and holds the total fixed, while the total moves only through synthesis and degradation, which is slow. On the fast
layer a conserved total has a relaxation rate of exactly zero, so it sits outside the positive-diagonal hypothesis
the invariance argument needs. The graph avoids the singularity by giving each form its own unconstrained node, at
the price of being able to raise tetrahydrobiopterin and quinonoid dihydrobiopterin together, which conservation
forbids. The physiological fix is a per-moiety sum-to-zero projection, which is a constraint and not a rate, and it
needs no literature sourcing: the constraint's form is arithmetic and moiety membership is computable from the
stoichiometry already in the graph. What does need sourcing is the licence to treat a total as fixed over a given
observation time, which is what the timescale record supplies.

**The nearest concrete defect**, measured and recorded separately in
`docs/coproduct_of_de_novo_split_2026-10-26.md`: the carrier relation `coproduct_of` mixes regeneration with de novo
synthesis under one learned gain, 49 de novo edges against 1,030 redistribution edges on the v0.4 slice, and within
the biopterin family 2 against 37. Splitting it is computable from the stoichiometry and needs no sourcing.

**Known limits (do not overstate these in writing).**
- Seven of the timescale record's sources were read through Consensus rather than PubMed and are marked as such;
  they are not to be relied on in a registered document until re-read.
- Its relation counts are v4's; v5 was not rebuilt for it.
- Choosing an interpretable basis for the stoichiometric null space is a known hard problem and was not attempted;
  that claim is itself unsourced and would need a Fable pass.
- Conservation relations exist only for the stoichiometric sublayer, so signalling, transcription and binding get
  none.
- Nothing here moves the full fixed point. Every item changes membership or structure, not the steady state the
  registered model reads.

**What would need an owner ruling**, none of which has a decision id yet: whether to split `coproduct_of`; whether
plain THF's absence from the carrier list is an oversight; and whether the slow set becomes a function of the
observation time rather than a list.

**Status.** Parked. Not on the critical path of the 9.97 cyclase handoff, the lockbox sequence or the steady-state
arms R0, R1 and R5.

**Measured 7 November 2026 on `graph_full_neuronal_split_binders_drugs_v5` (engineering, on Opus; started at the
owner's request)**, with `experiments/measure_coproduct_de_novo_split.py --graph` pointed at v5: 965 carrier
`product_of` (`coproduct_of`) edges, 146 regeneration, 62 de novo and 757 under the recurring-pair clause, which is a
redistribution by construction; within the biopterin family 3 de novo (the three SPR reactions that make
tetrahydrobiopterin) against 20 regeneration. The family split: acyl carrier 30 de novo and 0 regeneration, folate 14
and 28, lipoamide 8 and 3, ascorbate 0 and 36. The v0.4 slice counts above (49 against 1,030; 2 against 37) are
history and are not compared with these. The first limit listed above is discharged: the seven Consensus-only sources
were re-read through PubMed on Fable on 6 November 2026 and every quote and use held (the timescale record's dated
addition of that day). What remains is the owner's: whether to split `coproduct_of`.

---

## 7. Endosomal pH: SLC9A6 (NHE6), SLC9A9 (NHE9) and the endolysosome node

Tagged 2026-10-27. Raised on 21 October 2026, when the owner asked what concern about SLC9A6 pull request #7 had set
out of scope; the write-up of 20 October behind that pull request named it and was never committed, so its reasoning
is lost and this item restates the gap from sources.

**The physiology.** The endosomal Na+/H+ exchangers set the pH of early and recycling endosomes against the proton
pump: "By providing a leak pathway for protons pumped by the V-ATPase, eNHE determine luminal pH and regulate cation
(Na(+), K(+)) content in early and recycling endosomal compartments", and "Loss-of-function mutations in eNHE cause
hyperacidification of endosomal lumen, as a result of imbalance in pump and leak pathways"; "Two isoforms, NHE6 and
NHE9 are highly expressed in brain, including hippocampus and cortex" (Kondapalli, Prasad and Rao 2014,
`kondapalli2014endosomalnhe`). SLC9A6 is the Christianson syndrome gene: a family with an X-linked syndrome "resembling
Angelman syndrome" carried "a deletion in the SLC9A6 gene encoding the Na(+)/H(+) exchanger NHE6", and further
mutations were found in "two XLMR families with epilepsy and ataxia, including the family designated as having
Christianson syndrome" (Gilfillan et al. 2008, `gilfillan2008slc9a6`).

**Why it matters here.** A monogenic gene with psychiatric and neurological phenotypes whose mechanism is a
compartment's pH. The symptom crosswalks already name SLC9A6 among the genes behind Inappropriate laughter, which is
excluded under `disinhibition_or_impulsivity` as mostly the Angelman sign.

**Where it meets the graph** (read on `main` at `68bde1f`, 27 October 2026; no graph was available, so nothing below is
a count):
- SLC9A6 and SLC9A9 appear in no code, config or curated table; only the two symptom crosswalks name SLC9A6. Their
  edges out and their reach are unmeasured.
- Decision 9.75's endolysosome store (`l`, "endolysosome lumen" in `graph/reactome_import.py`) lumps the endosome with
  the lysosome, and on the scratch rebuild of 20 October it took no reaction in and fed two ("0 in, 2 out"). NHE6 and
  NHE9 act on early and recycling endosomes, a compartment the graph does not separate.
- The quantity NHE6 changes is luminal pH, which belongs with the compartment pH weight of `linear_response_encoder.py`,
  and that weight is inert: `calibrate_ph_sensitivity` is called by no trainer code, only by tests (recorded under 9.75).
  Routing NHE6 into pH would change nothing until that is settled.

**The direction is stated.** Unlike TMEM175, whose coupling to lysosomal release 9.75 left at "activates nothing: no
paper read states the direction", loss of these exchangers acidifies the lumen.

**Known limits (do not overstate these in writing).**
- Kondapalli 2014 is a review, and its abstract speaks of the eNHE as a class; it names neither gene in the text
  quoted, and it does not assign phenotypes to isoforms.
- The disease association of NHE9 is not sourced here.
- The licences of both papers were read from PMC's licence metadata through the PubMed copyright tool, not from a
  sentence on the page: the two page reads were refused by the fetch tool's permission check on 27 October 2026
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC4066934/ and https://doi.org/10.3389/fncel.2014.00172).

**What would need an owner ruling**, none of which has a decision id yet: whether the endosome and the lysosome are
separated; whether endosomal pH becomes a node or stays inside the pH weight; and the inert pH calibration, which is a
registered-model matter.

**Status.** Parked. Measure first, on the current graph: SLC9A6's and SLC9A9's edges out and reach, and whether a
perturbation of either gets past its own protein.

**Measured 7 November 2026 on `graph_full_neuronal_split_binders_drugs_v5` (engineering, on Opus; started at the
owner's request).** SLC9A6 has no node in the graph: no edge source of the build names it (not Human-GEM's gene
rules, not Reactome release 98's SBML, not OmniPath or CollecTRI; HuRI's one SLC9A6 pair, with ENSG00000027697, feeds
only the edge priors of `graph/edge_negative_evidence.py`). So the 113 SLC9A6 rows of
`data/raw/hpo/genes_to_phenotype.txt` yield no evidence report in `data/processed/evidence_full_v5`. SLC9A9 is
present only as one of six catalysts of Human-GEM `MAR05430`, "transport of H+ and Na+ (cytosol to extracellular)",
with SLC9A1 to SLC9A5, so a SLC9A9 perturbation moves the plasma-membrane Na+ pools and extracellular H+, not an
endosome. The endolysosome store `NEURON_MAM01413l` still has 0 edges in and 2 out. Reach is not informative here: a
SLC9A9 seed reaches 41,117 of 49,834 nodes, as almost every seed does. A Fable pass on NHE6 and NHE9 localisation,
direction and disease association was started the same day.

**Added 7 November 2026** (the Fable pass; full record `docs/endosomal_nhe_literature_2026-11-07.md`, 16 references).
`MAR05430`'s SLC9A9 catalysis is **not physiological**: Human-GEM's `genes.tsv` sources its "Cell membrane;Lysosome"
to DeepLoc2, a prediction, while UniProt Q8IVB4 puts NHE9 on endosomal membranes and gives "Cell membrane" only by
similarity to a mouse hair-bundle study. NHE6 (Q92581) reaches the surface only during vesicular recycling
(`ohgaki2008rack1`). Direction under loss, with signs an edge could carry: luminal pH falls, and with it TrkB
signalling (`ouyang2013nhe6trkb`, with independent labs `kucharava2020nhe6hearing`, `gao2025nhe6trkbagonist`,
`lizarraga2021csipscneurons`); lysosomal proteolysis falls while endosomal cathepsin D rises
(`pescosolido2021nhe6lysosome`); tau rises (`lee2022nhe6ratlysosome`, human post-mortem `garbern2010slc9a6tau`).
NHE9's disease association is now sourced: autism (`morrow2008autismloci`, `kondapalli2013nhe9`, loss-of-function
variants) and ADHD (`laskysu2008adhdgwas`, `markunas2010slc9a9adhd`), the ADHD link suggestive only with one negative
GWAS. **The premise of this item is corrected: Reactome release 98 is current and already holds both genes**, in
`R-HSA-425986` "Sodium/Proton exchangers", which the build's fetch list omits; its reactions put SLC9A6 (grouped with
SLC9A7, a membership question like 9.68's) on the early endosome and SLC9A9 on the late endosome, with the early
endosome, late endosome and plasma membrane as separate compartments. So no later release is needed; what is missing
is fetching that pathway, keeping its plasma-membrane reaction distinct from the endosomal ones, and a pH node. Two
frictions the record names: reactome.org's robots file blocks the reader (the SBML export route was used, respected),
so a fetch needs its hash pinned; and Reactome's late-endosome compartment for NHE9 follows a 2005 reading that a 2013
astrocyte study puts on recycling endosomes instead, a disagreement to rule on rather than import unseen.

---

## 8. A measured per-cell-type VAMP1 share

Tagged 2026-10-27, from the review of decision 9.68 on 25 October 2026.

**The idea.** VAMP1 joins VAMP2's 16 synaptic vesicle entities with one share, 0.145, the ratio of the two genes'
mean GTEx brain median TPM (human, whole tissue). The physiology is cell-type dependent: in mouse, VAMP1 protein is
in inhibitory and not excitatory terminals (`vuong2018rbfox1`), and the 16 entities are already split by transmitter,
so a per-transmitter share could carry that. It is parked because no measured human per-cell-type share exists:
HPA's nuclear per-cluster-type shares are nearly uniform (0.03 to 0.11), and human whole-cell in situ data put
non-PV cortical neurons at about half the PV level of VAMP1 mRNA (`chung2024rbfox1`).

**The cheapest checks.**
- The Allen mouse cortex and hippocampus whole-cell 10x atlas (Yao et al. 2021): Vamp1 and Vamp2 by subclass
  (Pvalb, Sst, Vip, Lamp5 against L2/3 IT, L5 IT, L6 CT). Set beside the HPA nuclear shares, it tests whether nuclear
  data understate the interneuron share in the species the protein evidence comes from.
- A human regional brain proteome (for example Carlyle et al. 2017): a VAMP1 to VAMP2 protein share for cortex,
  which is the quantity the membership weight stands for.
- The supplement of Siletti et al. 2023 (`siletti2023transcriptomic`), still unread: whether the HPA input was
  corrected for ambient RNA.

**Known limits (do not overstate these in writing).**
- A knockdown effect size is not a share: the same VAMP1 knockdown lowered mIPSC and mEPSC frequency by about 50%
  each (`vuong2018rbfox1`).
- An mRNA share does not carry VAMP1's lower efficiency (`zimmermann2014synaptobrevin`).
- The idea that cytoplasmic Rbfox1 makes nuclear RNA understate interneuron VAMP1 is a hypothesis, and its one
  source (`lee2015cytoplasmic`) was read on Opus and is not yet rechecked on Fable.

**What would need an owner ruling.** Whether a per-transmitter share replaces the single share, once one is measured.
The owner's call on keeping 0.145 is open in decision 9.68.

**Status.** Parked. Not on the critical path of the 9.97 cyclase handoff, the lockbox sequence or the steady-state
arms.

## 9. The Krebs cycle's effect on oxidative burden

Tagged 2026-10-28, at the owner's request ("please add the kreb's cycle effect on oxidative burden to the exploration
queue").

**The idea.** Represent how the tricarboxylic acid cycle bears on oxidative burden, so that a perturbation of a cycle
enzyme, or of the supply into the cycle, can move the oxidant species the graph already carries. What the graph holds
today, measured on the curated tables at `main` `d0a9c7d` on 28 October 2026 (tables, not a graph build):
- `mechanistic_pathway_learning/graph/oxidative_regulation.py` makes `produces_oxidant` edges, gene to oxidant, from
  `docs/curated_oxidant_sources.csv` (23 rows) and `oxidatively_modifies` edges, oxidant to gene, from
  `docs/curated_oxidant_targets.csv` (38 rows), both built into the neuronal variants by
  `experiments/build_neuronal_graph_variant.py`.
- The respiratory-chain sources are two genes, NDUFV1 (complex I) and UQCRFS1 (complex III). **No tricarboxylic acid
  cycle enzyme is listed as an oxidant source.**
- Of the cycle's genes, only ACO2 appears, and only as a target: four rows, superoxide, hydrogen peroxide,
  peroxynitrite and nitric oxide, each signed -1.
- The cycle's reactions and the NADH they make are in the Human-GEM metabolic layer, while oxidant production is an
  edge from a gene node, so whether a change in cycle flux or in the NADH supplied to complex I reaches the superoxide
  that complex I makes is not established for this graph.

**The cheapest checks.**
- Trace, on the current build, whether a seed on a cycle enzyme reaches any oxidant node, and by which relations.
  This is engineering and needs the real v5 build, which does not exist yet (decision 9.106).
- A Fable pass on the literature: which cycle enzymes are themselves oxidant sources in human or mammalian
  mitochondria, which are oxidant targets beyond ACO2, and whether the effect of cycle flux on respiratory-chain
  superoxide is stated with a sign that a graph edge could carry. Nothing on this page asserts any of it yet.

**Known limits (do not overstate these in writing).**
- Oxidant production by the respiratory chain depends on the redox state of its carriers and on membrane potential,
  not on flux alone, and the linear-response encoder carries a signed steady-state response, not a rate law.
- The tables are built from PubMed abstracts (`docs/data_sources.md`), and `docs/curated_oxidant_edges_unverified.csv`
  holds 10 proposed edges that were not admitted.

**What would need an owner ruling.** Whether metabolite pools, such as NADH or succinate, may drive a
`produces_oxidant` edge, which today starts only from a gene. That would be a new kind of edge for that relation.

**Status.** Parked. Not on the critical path of the v5 rebuild, the 9.97 cyclase work or the lockbox sequence.

**Measured 7 November 2026 on `graph_full_neuronal_split_binders_drugs_v5` (engineering, on Opus; started at the
owner's request).** Counting reach, every one of 18 cycle and pyruvate-dehydrogenase gene seeds reaches all 14
oxidant nodes (the targets of `produces_oxidant` and sources of `oxidatively_modifies`), so reach decides nothing: the
shortest routes run through protein binding (for example OGDH `binds` ABL1, `activates` SHC1, `produces_oxidant`
H2O2) or through four to nine metabolic hops. **The route the physiology needs is absent by construction.** Complex I
and complex III superoxide are `produces_oxidant` edges from `PROTEIN:NDUFV1` and `PROTEIN:UQCRFS1`, and neither
protein node receives any edge from a metabolite; mitochondrial NADH (`MAM02553m`) is a currency node and passes
nothing on. So a change in cycle flux or in the NADH supplied to complex I cannot move respiratory-chain superoxide in
this graph, whatever the gains. That makes the owner ruling named below (whether a metabolite pool may drive a
`produces_oxidant` edge) the gate. A Fable pass on the cycle's oxidant sources and targets was started the same day.
Reachability here follows stored edges plus the encoder's `depletes_substrate` and `product_opposes`, never leaving
a currency node, and ignores signs.

**The Fable literature pass, recorded 7 November 2026 in `docs/krebs_oxidant_literature_2026-11-07.md` (24
peer-reviewed sources, every field confirmed against Europe PMC; no row applied to the curated tables).** Eight
candidate rows fit today's schema and need no new edge kind. Oxidant sources (gene to oxidant): DLD and DLST, from
heterozygous-knockout brain mitochondria; SDHA, at the complex II flavin site; GPD2. Oxidant targets (oxidant to
gene): H2O2 on OGDH (weak, at or above 100 µM, so below the existing ACO2 rows), H2O2 and 4-hydroxynonenal on the
DLST and DLAT lipoic-acid sites, peroxynitrite and superoxide on SDHA. Three findings bear on item 9's own framing.
H2O2 on SDHA is **rejected** as a direct edge: it acts through oxaloacetate (Moser et al. 2009). **NADH cannot be the
route**, confirming the measurement above from the other side: it is a currency node, while succinate (`MAM02943m`)
and 2-oxoglutarate (`MAM01306m`) are not, so the cheapest metabolite-driven edge would be succinate to superoxide by
reverse electron transport, or 2-oxoglutarate to H2O2, not NADH. But succinate's sign holds only above a membrane-
potential threshold that no graph node carries, and the reverse-transport site "is not in equilibrium with the NAD
reduction state", so it needs a ruling of its own, separate from any NADH edge. Four further rows (OGDH, PDHA1 and
DLAT as sources; DLD, OGDH and PDHA1 as targets) are flagged where the evidence is complex-level or rests on a single
source. The pass read the oxoacid-dehydrogenase sources and targets in brain and mammalian mitochondria; one source
set (T-6) is a single group, and one (S-5) has no brain preparation.

## 10. The shunt: inhibition by conductance that no edge into `VM_c` carries

Tagged 2026-11-04, at the owner's request ("I'd actually say add the shunt to the exploration queue to find other,
potentially non-architectural options"), when decision 9.112 was ruled.

**The idea.** A rise in a channel's conductance does two things. It pulls the membrane potential toward that ion's
reversal potential, which the conductance edges ruled under 9.112 carry. It also lowers the membrane's input
resistance, which shrinks the voltage change every other input produces. The second is the shunt. Kaila et al. 2014
(`kaila2014cation`, read on Fable in the PMC author manuscript PMC4294553 on 4 November 2026): "shunting inhibition,
which can take place at any level of the membrane potential". It changes the gain of `VM_c`'s other inputs, not the
value of `VM_c`, so no signed edge into a scalar `VM_c` can represent it, under any option of 9.112. GABA_A and the
glycine receptor are the plainest cases, because at a mature neuron's resting potential their reversal potential lies
close to it (V_rest - E_Cl = +11.2 mV at the registered constants), so their effect on `VM_c` is small and most of their
inhibition is the shunt.

**Where to look first, for options that do not change the encoder.**
- The labels and the head: whether the symptom labels a shunt would move are already reached through another route the
  graph carries (the receptor's coupling, the cotransporters, downstream transmitter release), so that the shunt is a
  matter of magnitude rather than of a missing direction.
- The input side: whether a drug or allele acting mainly by shunt can be represented at entry, as a per-perturbation
  scaling of the inputs into `VM_c`, which leaves the propagation linear in the field.
- A disclosed limit: a list of the perturbations whose main published mechanism is shunting inhibition, so the
  limitation is counted rather than described.
- Only then architectural options: a gate on `VM_c`'s row read from a settled first pass, the device the 9.81 review
  describes, which 9.81 has not ruled on.

**Known limits (do not overstate these in writing).**
- Nothing here is measured. Which perturbations act mainly by shunt is unread, and so is whether any label depends on it.
- The Kaila et al. 2014 quotation is from the author manuscript; the published text at nature.com answered a check that
  the visitor is human and is unread.

**Status.** Parked. Not on the critical path: 9.112's build goes ahead without it, with the shunt stated as a limit.

**Measured 7 November 2026** (Fable pass; full record `docs/shunting_inhibition_count_2026-11-07.md`; on the v5 split-binders drug graph and `evidence_full_v5`). Of the 46 GABA_A / glycine-receptor perturbations in the v5 evidence (35 drugs, 11 genes, 438 labelled pairs), **10 have a source stating a conductance-dominated main mechanism**: propofol and thiopental (Bieda & MacIver 2004, gabazine "failed to block the propofol-induced depression of intrinsic excitability"), etomidate (Cheng et al. 2006), isoflurane (Caraiscos et al. 2004), ganaxolone (class only, Stell et al. 2003, which names no drug), and `GABRD`, `GABRA5`, `GLRA1`, `GLRA2`, `GLRB`. They carry **38 labelled pairs, 56 reports, all `induces`**, across 19 constructs, none carried only by them. **Benzodiazepines and Z-drugs are not among them**: Nusser & Mody 2002 report zolpidem "augmented phasic inhibition by 66%, while leaving the mean tonic conductance unchanged". **The labels-and-the-head option is partly answered and cuts the wrong way.** `VM_c` sits five hops from every seed, by the one route `catalyzed_by` -> `changes_ion_pool` (Cl- pools) -> `driving_force`; a shorter conductance-independent route exists at hop 3, the `regulates_release` edges of `RCPT_GABRA1`, `RCPT_GABRB2`, `RCPT_GABRG2` (GABA, glutamate, serotonin, histamine) and `RCPT_GLRA1` (glutamate). **37 of the 46 have it; the nine that do not include four of the ten shunt cases** (`GABRA5`, `GABRD`, `GLRA2`, `GLRB`), whose only exit is the chloride pool. **No shunting-to-hyperpolarising ratio was found.** The nearest is Staley & Mody 1992, cited by 9.112: 50 percent of excitatory charge shunted with the GABA_A reversal 19 mV **above** rest, so no hyperpolarising part. **Counterweight**: Pavlov et al. 2009 find tonic GABA_A currents in CA1 pyramidal cells "exclusively affect offset and not gain".
