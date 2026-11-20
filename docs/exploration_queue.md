# Exploration queue

Ideas parked for later so they stop taking up working memory. Nothing here is registered or required for the
confirmatory analysis, and nothing here is started. An item names what it would change, what it would cost and the
limits that must not be overstated when it is written up.

This document moved into the repository on 26 October 2026 from the Project note `claude/exploration_queue.md`
(**that note was deleted on 27 October 2026**, when the owner ruled the repository the single source of truth: "Everything should rely on the repo moving forward"; it is named here as the provenance of this page and not as a document to read),
under the owner's standing rule that sources are recorded in the repository. Items 1 to 4 are carried over as they
were tagged; items 5 and 6 are new, both added on 26 October 2026, items 7 and 8 were added on 27 October 2026, item 9 on 28 October 2026, item 10 on 4 November 2026, and items 11, 12 and 13 on 7 November 2026.

Checked against `main` at `0b976bf` on 26 October 2026, and again at `0fd0139` on 4 November 2026. Item 8's literature, read on Opus on 24 October
2026, and item 5's, read on Opus on 26 October 2026, were both rechecked on Fable on 7 November 2026
(`lee2015cytoplasmic` bears on Rbfox1 targets in general, not on VAMP1, which rests on `vuong2018rbfox1`; item 8's
entries say so); both items are parked, so nothing relies on them.

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

## Priority order (20 November 2026)

The owner asked on 20 November 2026 to "prioritize the exploration queue then start an opus 5.5 subagent to start
research on the next highest priority item", and later the same day to add new items. The order is the session's (on Opus), by five tests: how much closer to
physiology the item brings the model, whether its first step can run now, what it costs, whether the owner can follow
it, and whether it bears on what the amendment of `docs/item37_rulings_draft_2026-11-13.md` has just ruled, since its fallbacks, class centres and curation rows
are being sourced now. It replaces the order of 7 November 2026 (the owner: "i don't care about maintaining previous
ordering. you can just overwrite existing order").

1. **Item 15, literature bias in the curated sources.** That amendment rules many values fitted on sourced rows and
   applied to unsourced ones (class centres, sibling medians, shared offsets, the carrier-share classes), which is the
   case item 15 describes. Its literature pass ran on 20 November 2026 on Opus at the owner's request and needs
   verification on Fable before it is relied on (the owner: "just note the literature pass as needing fable
   verification later").
2. **Item 14, the curation sweep over the drug target table.** Its query ran on 20 November 2026 through the corrected
   readers (90 of the 260 v5 drugs fall in a category; six get sign 0 from a plain MODULATOR row with no curated
   override, queued for Fable curation on 21 November 2026); the count of affected edges waits on the rebuild.
3. **Item 21, the Human-GEM sweep** (new, unconfirmed): the systematic form of the correction rows ruled one by one on
   20 November 2026; its corrections belong in the graph version those rows already force.
4. **Item 18, the cross-ion shifts and the pump's own current at `VM_c`** (new, unconfirmed): linear and cheap, from
   the model the build already cites, and it corrects the pool weights the pore build is wiring now.
5. **Item 7, endosomal pH.** Measured 7 November 2026; designed on Opus on 20 November 2026 (unconfirmed); what remains
   is the owner's ruling on the design, then a build.
6. **Item 9, the Krebs cycle and oxidative burden.** Designed on Opus on 20 November 2026 (unconfirmed): oxidant
   sources keyed to the redox state of the carrier pools; the owner's ruling, then sourced rows.
7. **Item 19, the energy charge and extracellular ATP** (new, unconfirmed): the same kind of cut as item 9, needing a
   design ruling of the same kind; its extracellular half is cheap.
8. **Item 6, the fast/slow partition.** Designed on Opus on 20 November 2026 (unconfirmed): the cofactor families first.
9. **Item 11, chronic exposure**, and 10. **item 12, receptor-number plasticity** (decision 9.118): design passes,
   larger, and the tardive dyskinesia construct waits on them.
11. **Item 20, inheritance mode and zygosity of the gene perturbations** (new, unconfirmed): it moves the perturbation
    set, so it comes before any lockbox run.
12. **Item 23, a readout when no stable steady state exists** (new, unconfirmed): with items 11 and 12, after the
    root-finder.
13. **Item 5, occupancy as the drug seed magnitude.** Partly taken up by the amendment, which carries a target weighted
    by occupancy (R3); what remains is to be re-read against that ruling.
14. **Item 17, the plasma free fraction as a modulated quantity** (new, unconfirmed): next to item 5, the other item
    on a drug's input size.
15. **Item 10, the shunt.** 16. **Item 4, phosphorylation.** 17. **Item 2, CollecTRI signs.**
18. **Item 16, DNA methylation.** The reaction exists and leads nowhere; it needs a design before sourcing.
19. **Item 1, sensitivity-matrix rank**, after the rebuild. 20. **Item 8, the VAMP1 share.**
21. **Item 22, protein isoforms inside one UniProt entry** (new, unconfirmed): a large structural change.
22. **Item 3, protein electrostatics**, the largest change.

Item 13 (co-prescription in FAERS) stays parked by the owner's ruling and is not placed.

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


**Added 7 November 2026.** A second seeded sample was read on Fable: seed 20261107, 30 labels from each stratum of the frame rebuilt on the v5 build of 5 November 2026 (2,166 labels whose releases state opposite signs, 1,688 following CollecTRI2 and 478 the 2023 release; the 16 already read excluded). 60 pairs, 38 decidable, the stored sign right for 17. **Pooled with the 11 of 17 October: 24 of 49, 0.49; exact 95% interval 0.34 to 0.64; Beta(1,1) posterior mean 0.49, 95% 0.36 to 0.63**, half the width of before. The interval straddles 0.5: on a disputed label the stored sign is no better than a coin flip, so a latent-sign prior for these labels would sit near 0.5, or near 0.6 for CollecTRI2's sign and 0.4 for the 2023 release's (right for 30 and 19 of 49; the 2023 sign decided from a paper 11 of 22, its default 12 of 24). Neither this item nor the record states a width standard, so whether that is narrow enough is the owner's call; the reading of the pass is that more sampling would sharpen a prior that is already nearly flat. Nine verdicts are judgement calls flagged with their alternative (scored the other way: 22 of 42, 0.38 to 0.67). The sample, the quotes and the 108 bib entries are in the dated addition at the end of `docs/regulation_sign_recuration.md` and the record `docs/collectri_sign_recuration_sample_2026-11-07.md`.

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


**Full text read, 7 November 2026 (Fable).** The owner supplied the interlibrary-loan copy of Needham et al. 2019
that day and the paper was read in full (`needham2019darkphosphoproteome`, whose note now holds the page references).
The abstract claim above is confirmed and the body gives the figures: "more than 95% of reported human
phosphorylation sites have no known kinase or biological function" (page 4), "around 97% of reported phosphosites
currently have no known regulatory kinase" and "fewer than 3% of identified human phosphosites currently have a
reported function" (page 5), against PhosphoSitePlus's "233,295 distinct human phosphorylation sites" as "accessed on
March 2018" (page 2 and the figure legends). The annotation is concentrated and biased: "Just 20% of kinases are
responsible for the phosphorylation of 87% of currently annotated substrates", which "likely reflects biases in the
funding of biological research toward well-studied kinases" (page 2), and "the fact that well-studied kinases
accumulate the most reported substrates may become somewhat of a self-fulfilling prophecy" (page 5); kinase
substrate counts and mouse-phenotype counts "are not correlated" (page 4). Two things the paper does not do: it
makes no count of sites with opposite (activating and inhibitory) effects, and it does not name SIGNOR; its one use
of site direction is as "directional information" for enrichment analysis when "phosphosites are already known to
have an inhibitory or activating function" (page 8), which is where this item puts it too (edge-sign evidence). It
also does not cite Goldbeter and Koshland 1981: ultrasensitivity enters it through Ferrell's papers (its references 51
and 60), and its reference 93 is Goldbeter and Koshland's 1987 paper on energy cost. **Goldbeter and Koshland 1981
verified the same day** (`goldbeter1981amplified`, PNAS 78, 6840-6844, read on the five scanned pages PMC holds): the
use above is as the paper states it, "zero-order ultrasensitivity" that "originates from the kinetic interplay between
two converter enzymes operating in opposite directions, outside the domain of first-order kinetics, and on a target
protein whose total quantity is conserved" (page 6841), with "the condition for zero-order ultrasensitivity is that
one or more of the converter enzymes operate outside the first-order region" (page 6843), so a first-order (linear)
response cannot show it, which is this item's point. Both papers: quotation only, no figure or table into a
committed file (AAAS "some rights reserved; exclusive licensee"; PNAS 1981, licence unverified on PubMed, PMC,
Crossref and OpenAlex). Neither changes the count of 7 November 2026 or the item's test; what the full text adds is
that any annotation-based count is a floor drawn from the well-studied end of the kinome.

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
- Seven of the timescale record's sources were read through Consensus rather than PubMed; they were re-read through
  PubMed on Fable on 6 November 2026, and every quote and use held (the record's dated addition of that day).
- Its relation counts were v4's; re-counted on v5 on 7 November 2026 (a dated addition to the record): the
  relations that straddle about 2 h hold 42.9 per cent of v5's stored edges, and `encodes` and `member_of`, the
  6-week straddlers, 7.1 per cent.
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

**Design pass of 20 November 2026 (on Opus at the owner's request; unconfirmed; needs verification on Fable and the
owner's ruling before it is relied on).** Measured on `data/processed/graph_full_neuronal_split_binders_drugs_v5`, files
dated 12 November 2026, which predate the the amendment of `docs/item37_rulings_draft_2026-11-13.md` rulings, at commit `8eccf472`; the 7 November counts above reproduce
exactly. Of the 62 "de novo" carrier `product_of` edges, about 11 raise a cofactor pool (SPR's three into
tetrahydrobiopterin, CoQ synthesis, thioredoxin assembly, B6 phosphorylation, holo-[ACP]); about 50 are redistributions
misread because a form is off the carrier list: all 14 folate edges (plain THF, folate and the polyglutamates are not
on it), 29 acyl carrier edges (acyl-[ACP] thioesters) and 7 lipoamide edges (S-acyl-dihydrolipoamides). With THF, folate
and the polyglutamates added, every folate carrier edge is redistribution. So the split is computable from the
stoichiometry once a moiety's family is given, but the family is not: Haraldsdóttir and Fleming 2016 (PLoS Comput Biol
12:e1004999, abstract only) state that identifying conserved moieties "requires data on reaction atom mappings in
addition to stoichiometry", which the graph does not hold. The THF question is therefore related to the split (the
folate half depends on it) and stays its own decision. On the drain side every biopterin edge that lowers the total is
a pseudo-reaction. In the encoder's fractional coordinates the conserved-moiety constraint needs each form's resting
share of the total, so it does need sourcing, contrary to "needs no literature sourcing" above; a projection inside the
loop breaks the max-norm contraction for moieties of three or more forms, and under the amendment of `docs/item37_rulings_draft_2026-11-13.md`'s root-finder an exact
conservation law gives non-isolated roots and a zero eigenvalue, so the pass proposes reduced coordinates with a total
node per moiety, fed by the split's total-changing edges, designed with the amendment of `docs/item37_rulings_draft_2026-11-13.md`'s root-finder. Once several stable roots
are kept, rates re-enter through the stability check, which the partition can supply by membership. The pass recommends
(its own view, not a ruling) extending the families by hand on two sources before any split, and puts nine questions to
the owner. Report: the session scratchpad's `item6_design_2026-11-20.md`; nothing in the repository was changed.
Record: `docs/exploration_item6_design_2026-11-20.md`.

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

**What fetching `R-HSA-425986` as the importer stands would do (engineering, on Opus, 7 November 2026; code and v5
read, the pathway's SBML export parsed from the pass's scratchpad copy, sha256 `5bc23c49...c33f6e`).** The export
holds four reactions: the plasma-membrane exchange (SLC9A1-5), SLC9A6,7 on the early endosome, SLC9A9 on the late
endosome, and SLC9A7/8 on the trans-Golgi. But `graph/reactome_import.py`'s `compartment_letter` sends every
compartment name containing "endosom" to `l`, the endolysosome lumen it shares with the lysosome, so the early and
late endosome would be merged back into one compartment with the lysosome on import. And on v5 every proton node in
`l` is a currency node that passes nothing on (Human-GEM's `MAM02039l`, 17 out-edges dropped by the encoder, and
Reactome's `CHEBI15378l`, none), while no Na+ node exists in `l`. So a plain fetch would give SLC9A6 a node and a
reaction, and an NHE6 or NHE9 perturbation would then move only the cytosolic Na+ pool; the luminal acidification
that the literature above makes the mechanism would reach nothing. Representing it needs three things beyond the
fetch: an endosome compartment letter of its own in the importer, a non-currency endosomal proton (or pH) node, and
sourced edges from it to what luminal pH governs (TrkB signalling, lysosomal proteolysis). Whether the pH node joins
the compartment pH weight of `linear_response_encoder.py`, which is still uncalibrated (9.75), is a further question.

**Added 20 November 2026: design (on Opus at the owner's request; unconfirmed; needs verification on Fable and the
owner's ruling before it is relied on).** Graph facts on `graph_full_neuronal_split_binders_drugs_v5`, files of 12
November 2026, which predate the the amendment of `docs/item37_rulings_draft_2026-11-13.md` rulings (Q4's H+ merge, the in-loop pH ceiling, 9.81's saturation), so they
are history once those are built. Fetching `R-HSA-425986` as the importer stands (option A) gives SLC9A6 a node, but
`compartment_letter` sends every endosomal species to `l`, luminal H+ and Na+ are currency, and Reactome's cytosolic
Na+ is the propagating pool `NEURON_MAM02519c`; so an NHE6 or NHE9 loss would reach the graph only through bulk
cytosolic Na+, not through the lumen. The import would also double `MAR05430` and `MAR07695`, and puts SLC9A7 on the
early-endosome exchanger through Reactome's CandidateSet "SLC9A6,7". Separating the endosome from `l` (option B) also
moves CLCN3 and CLCN4/5/6, both labelled genes, and finds no endosomal V-ATPase pump: the graph's only pump reaction,
`MAR00080`, is lysosomal. The pH weight would cover a new letter automatically but would gate only transporter
entities, and it is still uncalibrated in every run (9.75). Option C adds a propagating endosomal proton pool on 9.75's
store pattern and sourced edges out of it. The best-supported edge is pool to `PROTEIN:NTRK2` at -1 (three labs).
Cathepsin D needs two signs on one node, tau is an aggregation finding against a protein level, and GLAST is an
astrocyte finding in a neuronal graph. The direction of the on-disk Reactome CLC reactions has to be checked first. D
(the pH weight only) changes almost nothing on the current code; E (direct gene edges) skips the mediator.
**Labels**: SLC9A6's 113 HPO rows reach five fine symptoms, `intellectual_disability` (Christianson),
`cognitive_impairment`, `parkinsonism`, `bradykinesia` and `resting_tremor`. The last four come only from OMIM:301142
(female-restricted, denominators 1/1 to 2/3). SLC9A9 has no HPO row. Resting endosomal pH: 6.3 early, 6.5 recycling,
5.5 late (Casey et al. 2010 via BioNumbers 115761, licence unverified) against a generic 5.7 (`kondapalli2014endosomalnhe`).
The session's recommendation is C with a single endosome letter: drop SLC9A9 from `MAR05430`, import only the two
endosomal reactions with the hash pinned, add the pool with the TrkB edge alone, and have a Fable pass source the pump
and the CLC direction first. It is the session's and not a ruling. Thirteen questions for the owner, and the full
record, are in the pass's report (`item7_design_2026-11-20.md`, session scratchpad); none has a decision id.
Record: `docs/exploration_item7_design_2026-11-20.md`.

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
- The idea that cytoplasmic Rbfox1 makes nuclear RNA understate interneuron VAMP1 is a hypothesis that no source
  tests. Its VAMP1 half rests on `vuong2018rbfox1` (RBFOX1 binds the Vamp1 3′ UTR; cytoplasmic Rbfox1 is sufficient
  to restore Vamp1; Vamp2 is unchanged) and its mechanism half on `lee2015cytoplasmic` (cytoplasmic Rbfox1 stabilises
  3′ UTR targets in general; the paper never names Vamp1). Both were re-read on Fable on 7 November 2026; neither
  compares nuclear with whole-cell RNA, so the nuclear-understatement step is this repository's inference.

**Added 7 November 2026 (Fable): the proteome check.** The second cheap check was run as far as open sources allow. Carlyle et al. 2017's per-protein table was not reached (`carlyle2017multiregional`: Nature's article page and its static-content ESM files refuse automated readers, the PMC supplement is figures only, and PRIDE PXD005445 holds raw files and a 6.2 GB MaxQuant archive). ProteomicsDB (`samaras2020proteomicsdb`, read by its API, log10 intensities, VAMP1 P23763 against VAMP2 P63027 in the same sample) gives a VAMP1 share VAMP1/(VAMP1+VAMP2) of 0.35 and 0.44 in the two adult frontal cortex samples of `kim2014draft` and 0.15 in whole brain in `wang2019deep` (fetal brain 0.19 and 0.39). A third cortex sample holds VAMP2 only. Limits: the intensity's definition (iBAQ by default) is not confirmed from ProteomicsDB's own documentation; VAMP1 and VAMP2 share tryptic peptides; two cortex samples. The whole-brain value matches the 0.145 mRNA share; the cortex values are 2 to 3 times higher. Not a measured per-cell-type share.

**Checked on the Allen aggregates, 7 November 2026 (Fable).** The published per-cluster medians and 25-75% trimmed means of log2 CPM for the Yao et al. 2021 cortex and hippocampus atlas were read (`yao2021taxonomy`; Allen terms of use: noncommercial research with citation). On SMART-seq the Vamp1/(Vamp1+Vamp2) share of summed cluster CPM is **Pvalb 0.13, Sst 0.05 to 0.06, Sst Chodl 0.03, Sncg 0.03, L5 IT 0.03, L5 PT 0.04 to 0.05, against Vip 0.005 to 0.02, Lamp5 0.004 to 0.009, L2/3 IT 0.005 and L6 CT 0.002 to 0.006**; Vamp2 is near-uniform. So whole-cell mouse data put the MGE interneurons, not interneurons as a class, 10 to 25 times above L2/3 IT and L6 CT, where HPA's human nuclear shares are nearly flat (0.04 to 0.08 against 0.03 to 0.11): the direction the item asked about holds for Pvalb, but the larger disagreement is the excitatory side (5 to 20 times below HPA), with species, platform and compartment confounded. Only Pvalb reaches 0.145. The 10x aggregates read near 0 for most clusters because Vamp1 is detected in under half a cluster's cells (4,125 against 8,894 genes per cell), a detection floor; a mean-CPM share needs the per-cell matrices (over 3 GB, not fetched).

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
  This is engineering and needed the v5 build, made on 5 November 2026; it was done on 7 November 2026 (below).
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

**Added 20 November 2026 (design pass on Opus at the owner's request; unconfirmed, needs verification on Fable and
the owner's ruling before it is relied on).** Counts are on `graph_full_neuronal_split_binders_drugs_v5`, files of 12
November 2026, which predate the the amendment of `docs/item37_rulings_draft_2026-11-13.md` rulings. The pass proposes giving the metabolite-driven edge to the redox
state of the carrier pools, not to succinate or 2-oxoglutarate as substrates. A succinate -> superoxide edge gives the
wrong sign for SDH inhibition. Succinate piles up, yet reverse electron transport stops: malonate inhibits it
(Korshunov 1997, PMID 9369223), and "Stepwise oxidation of the QH(2)/Q pool by increasing malonate concentration
slowed" complex I superoxide (Treberg 2011, PMID 21659507).
Proposed: a relation of its own (working name `redox_state_drives_oxidant`, signed, with its own gain) from:
- a new matrix NADH pool `REDOX_NADH_m`, built as `redox_pools.py` builds `REDOX_NADPH_m` (190 NAD+-reducing and 28
  NADH-oxidising reactions), to superoxide at site IF, +1 (Treberg 2011; Kussmaul & Hirst 2006, PMID 16682634; brain:
  Starkov & Fiskum 2003, PMID 12911618);
- the same pool to H2O2 at the 2-oxoacid dehydrogenases, contested (Tretter 2004 against Quinlan 2014), so a 9.122
  gate;
- the non-currency ubiquinol nodes (`MAM03102m`, Reactome's `CHEBI64183m`) to superoxide at site IQ, +1 (Treberg
  2011; Robb 2018, PMID 29743240);
- optionally ubiquinone at -1, and 2-oxoglutarate to H2O2 (+1).
No Q-pool edge to complex III: its superoxide is "primarily promoted by a partially oxidized rather than by a fully
reduced ubiquinone pool" (Dröse & Brandt 2008, PMID 18522938).
Found on the way, each for its own decision:
- the existing NDUFV1 -> superoxide row (+1) makes a complex I loss lower superoxide, while patient fibroblasts show an
  increase "inversely related" to complex I activity (Verkaart 2007, PMID 17289351; Pitkanen & Robinson 1996,
  PMID 8755643);
- Human-GEM writes SDH (`MAR04652`) and MDH2 (`MAR04141`) against the cycle, so on that route an SDH loss raises
  ubiquinol;
- the Human-GEM and Reactome Q pools are separate nodes;
- all 34 `oxidatively_modifies` edges start from cytosolic oxidants, because the target table has no compartment
  column;
- no mitochondrial membrane-potential node exists, so the site IQ edge asserts the high-protonmotive-force regime.
36 of 2,802 labelled perturbations in `evidence_full_v5` are cycle or chain genes, and no admitted drug targets one.
Cost: about a day of code in `redox_pools.py` and `oxidative_regulation.py`, a third curated table, no encoder change,
riding on the the amendment of `docs/item37_rulings_draft_2026-11-13.md` rebuild. Five new sources need Fable verification and BibTeX entries.
The design pass (`item9_design_2026-11-20.md` in that session's scratchpad) holds the rows, the limits and nine
questions for the owner.
Record: `docs/exploration_item9_design_2026-11-20.md`.

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

---

## 11. Chronic exposure as a represented quantity

Tagged 2026-11-07, at the owner's request (decision 9.118): "I want to try representing both. Please add fable passes
to the queue to research designs for implementing them", answering whether the model should represent chronic exposure
or receptor-number plasticity (question 10 of `docs/tardive_dyskinesia_construct_2026-11-07.md`).

**The idea.** A perturbation now enters as a signed seed whose field settles to one readout. Nothing in the encoder or
the readout knows how long the perturbation has lasted, so an effect that appears only after weeks of exposure cannot be
told from one that appears at once. Tardive dyskinesia against drug-induced parkinsonism is the case that raised it:
both are reached by the same DRD2 antagonism edge with the same sign. The gabapentin and pregabalin effect of 9.69, seen
"only when applied chronically", is a second.

**The owner's proposal, to be tested first:** "one thing could be doing readings at each propagation round that the
perturbation reaches back to a previously visited node but this would cause a bunch of other issues like how to know
which round should actually produce the symptoms though maybe that could be solved by using MDL? The decision in how to
reduce the module supports symptom parameters bears on this though".

**What the pass should read and answer.**
- Whether a propagation round of the encoder corresponds to any physical time, given that the registered readout is the
  settled field, and what `docs/relation_timescale_ordering_2026-10-26.md` (the project's record of the relations'
  physical timescales) allows. The owner's remark of 6 November 2026 is the readout side of the same question: "the
  contraction coefficient should either be different for each drug or be removed completely and find a way to
  determine read out timings".
- How often a perturbation's field returns to a node it has already reached, measured on the v5 drug graph, so that a
  reading at each return is counted rather than assumed.
- What an MDL choice of the reading round costs: a discrete parameter per symptom, or per drug and symptom, and how the
  description length of design section 5.5 would charge for it.
- What exposure-duration models the pharmacology literature uses (time-dependent pharmacodynamics, tolerance and
  sensitisation models, and indirect-response models with a slow compartment), and which of them can sit on a signed
  graph that is linear in the field.
- Which labels carry an onset or a duration that a duration-aware readout could be scored on (SIDER and OnSIDES carry
  little; trial time frames and FAERS onset fields are candidates).
- The bearing on the module-support choice (`docs/module_support_reduction_2026-11-07.md`): how many readings per
  symptom each option can take without the parameter count growing.
- **Added 7 November 2026 (decision 9.112's extracellular pools):** the clearance of the extracellular ion pools is a
  timescale any multi-reading design must carry. At the registered steady-state readout the extracellular pools take
  weight 0 from neuronal currents, but before clearance acts (time constants of about 1 to 4 s for K+) they behave
  as a closed space, where extracellular K+ is the most sensitive pool of the six; the values are kept in
  `docs/membrane_potential_constants.md` ("Extracellular pools: the ruling of 7 November 2026"). A design that cannot
  express that clearance cannot express a seizure or spreading-depolarisation transient either.

**Known limits (do not overstate these in writing).** Nothing here is measured. The DRD2 supersensitivity account of
tardive dyskinesia is the held mechanism, not the only one proposed, and the pass should say which accounts the
literature holds before a design is chosen for one of them.

**Status.** Queued for a Fable pass; not started.

---

## 12. Receptor-number plasticity

Tagged 2026-11-07 with item 11, on the same ruling (decision 9.118).

**The idea.** A receptor node now carries an activity, not an amount. Chronic blockade of D2 receptors is held to
increase their number, and chronic agonism to decrease it, and the adapted amount then changes what every later input
to that receptor does: a change of gain, as the shunt of item 10 is, rather than of value. No relation of the graph means
"sustained occupancy changes receptor density".

**What the pass should read and answer.**
- What is measured about receptor up- and down-regulation under chronic drug exposure for the receptors the drug
  graph's perturbations enter at (DRD2 first; then the 5-HT2A downregulation under antidepressants, beta-adrenoceptor
  downregulation, and GABA_A changes under benzodiazepines), with magnitudes and time courses where sources give them.
- Designs that keep the propagation linear in the field: a slow per-node gain driven by integrated occupancy and read
  in a second, adapted pass (the two-pass device the 9.81 review describes); a receptor-amount node with an adaptive
  edge from the receptor's own activity; or an adaptation term at entry, as a per-perturbation scaling of the seed.
- Whether an adapted pass can predict withdrawal-emergent effects (a supersensitive receptor after the drug is
  stopped), which would give the design a test on labels the project already holds.
- How saturation (9.81) and the module-support choice bear on it, as for item 11.

**Known limits (do not overstate these in writing).** Nothing here is measured. Receptor number is not observed for
most nodes, so a design that needs it per node needs a prior or a default, and the pass should say which nodes have any
measurement at all.

**Status.** Queued for a Fable pass; not started.

---

## 13. Co-prescription confounding in the FAERS reader

Tagged 2026-11-07, at the owner's request: "Drop the coprescription option for now but put it in the exploration
queue" (decision 9.115(f)).

**The idea.** A FAERS report names every drug the patient was taking, so a reaction caused by one drug is reported with
every drug prescribed beside it. The FAERS reader skips a drug and symptom only when the drug is indicated for the
symptom (`indicated_symptoms_by_drug` in `mechanistic_pathway_learning/evidence/faers_disproportionality.py`, the one
correction decision 9.96 admits). The case that raised it: benztropine, procyclidine and trihexyphenidyl carry 184, 84
and 70 FAERS reports of tardive dyskinesia, but every one of their labels places tardive dyskinesia outside the
indication (`docs/anticholinergic_indications_faers_2026-11-07.md`, quotes read on Fable), so the reports come from the
antipsychotic the patients are also taking.

**Two forms, of different size.**
- The minimal form: a curated table of drug and symptom pairs confounded by a co-prescription that the drug's own label
  names, read into the reader's skip beside the indications. The rows are already proposed, with their quotes, in
  section 4 of the record. About an hour of engineering, and a dated addition to 9.96, which as worded admits only the
  indication.
- The general form: an adjustment for co-reported drugs over every drug and symptom, which needs the co-medication of
  each report from openFDA (1,000 queries a day without a key), a method from the pharmacovigilance literature (the
  record lists Avillach et al. 2014, Shaffer et al. 2004 and Fusaroli et al. 2026, read as abstracts) read on Fable,
  and a decision of its own. Days.

**Known limits (do not overstate these in writing).**
- FAERS is grade C: masked from the registered label selection and outside the registered model, which runs no soft
  priors. Either form changes a soft validation stratum, not a label.
- The labels state an effect as well as a bias: anticholinergics "may aggravate" tardive dyskinesia, so a skip
  discards a real signal with the confounded one.
- No paper read measures anticholinergic co-prescription confounding in tardive dyskinesia pharmacovigilance itself.

**Status.** Parked by the owner's ruling; not started.

## 14. A curation sweep over the drug target table, for the mechanisms a single sign cannot carry

Tagged 2026-11-09, at the owner's request after bupropion's nicotinic antagonism came up: "I'm more thinking there
will be a pass for similar missed cases later marked for manual curation". Nothing here is started.

**The idea.** A drug's row in `drug_entry_nodes.parquet` is a target, a sign and a magnitude, taken from ChEMBL's
mechanism rows through `ACTION_TYPE_SIGN` (`mechanistic_pathway_learning/perturbation/map_drug_targets_to_graph_nodes.py`).
That carries an inhibitor and an agonist well. It carries badly, or not at all, a drug that is a transported substrate,
one whose action is at a target ChEMBL files no mechanism row for, and one whose two targets need opposite signs. The
cases below were each found while answering a different question, were each verified where the text says so, and none
is fixed. A sweep would look for the rest of them rather than wait for each to surface.

**The cases found so far, with where they are recorded.**

| drug | what the table holds | what the sources say | recorded |
|---|---|---|---|
| amphetamine | SLC18A2 **-1**, the same as tetrabenazine | a transported substrate that **requires** VMAT2 working; the two are antagonists at that target | 9.127 |
| methamphetamine | SLC6A2, SLC6A3, SLC6A4 all **-1** | a releasing agent, as amphetamine is at **+1**; the two closest congeners are written oppositely, and the -1 rows cannot drive the `catalyzes_reverse_transport` reactions built for this mechanism | 9.127 |
| fenfluramine | HTR1D +1, HTR2C +1, SIGMAR1 -1, **no transporter edge at all** | the EMA summary of product characteristics calls it "a serotonin releasing agent"; the US label names only 5-HT2 and calls the mechanism unknown, so the agencies differ | 9.127 |
| bupropion | SLC6A2 -1, SLC6A3 -1 | the transporter rows are right (it is a noradrenaline-dopamine reuptake inhibitor, not an SNRI); its **nicotinic receptor antagonism**, thought to underlie the smoking-cessation use, is not carried. **Unverified**: no source was read for it, and whether ChEMBL files a mechanism row was not checked | this item only |
| tramadol | the mu opioid receptor only | SERT and NET are missing, and so is the higher mu affinity of its metabolite O-desmethyltramadol | 9.121 C5 |
| zopiclone | a ChEMBL complex of 9 GABA-A subunits, **no gamma subunit** | the site both its labels describe needs gamma; eszopiclone's complex holds 16 subunits, so the magnitude also spreads 1/9 against 1/16 | 9.121 C5 |
| dextroamphetamine | a VMAT2 row the racemate's record lacks | the difference between the enantiomers is overstated by it | 9.121 C5 |
| bupivacaine, levobupivacaine | SCN4A alone, the muscle sodium channel | the eight other local anaesthetics of N01B carry the ten-gene set with the brain-expressed subtypes; this is why its verdict reads "no brain-expressed target" | 9.123 |
| lisuride | no curated row (its sources disagree in sign) | DrugCentral gives one 5-HT2B antagonist row, the Guide to PHARMACOLOGY sixteen rows topped by 5-HT1A full agonism and D2/D3 partial agonism: opposite in sign at dopamine | 9.121 C3 |
| budipine | MAO-B held out | Eltze et al. 1999 against Klockgether et al. 1996, who found no dopaminergic action in vivo | 9.121 C3 |
| pizotifen | SERT held out | its one label places the uptake inhibition in platelets, so it is probably not a central row | 9.121 C3 |

**What the sweep would be.** Over the 230 drug perturbations, find the drugs whose label states a mechanism the target
table does not carry, and the drugs whose action type the sign mapping flattens. Two routes, and the first is cheap:
compare each drug's label mechanism section against its target rows, which the project already reads for registered
rule 14 (`experiments/read_label_central_action.py` fetches those sections and caches them); and check each drug whose
ChEMBL action type is a substrate, a releasing agent or a modulator rather than an inhibitor or an agonist, which is a
query over `data/raw/chembl/mechanisms.json`. Research, so on Fable; the rows would go to
`configs/curated_drug_targets.csv`, which decision 9.121 C3 created for exactly this.

**Known limits (do not overstate these in writing).**
- **The sign is the model's instrument, and some of these cases need more than a sign.** A transported substrate is not
  an agonist with a different number; decision 9.127 records that an always-available reverse reaction would make
  tetrabenazine wrong. So a sweep finds the cases but does not by itself fix the ones that need a mechanism.
- **A drug the sweep corrects moves the perturbation set**, which falls before the held-out draw (9.69's note), so it is
  outcome-blind only while the lockbox is undrawn.
- **The table above is a list of the cases that happened to surface**, not a measured count, and one row of it is
  unverified. The sweep's first job is to say how many there are.


---

## 15. Literature bias in the curated sources, and ways to correct it

Tagged 2026-11-18, at the owner's request: "Can you please add something to the repository that notes a need to look
at literature bias for our curated sources and ways to correct it?" Nothing here is started, and no literature on the
correction methods has been read; the methods named below are candidates for a Fable pass, not findings.

**The problem.** Every curated table in the project (drug targets and affinities, carrier proteins and shares, ambient
concentrations, the per-gene expression factors, the edge evidence behind the graph) holds what someone chose to
measure and publish. What is measured is not a random sample of what exists. Wherever a fallback, a class median, a
prior or a calibration is fitted on the sourced rows and then applied to the unsourced ones, the bias carries into the
values the model uses, and a validation scored on sourced rows does not see it.

**Cases observed on 18 November 2026, each by a Fable pass (scratchpad reports of that date, not yet in the
repository).**

| where | what was seen |
|---|---|
| occupancy split, learned fallback (decision 9.129) | the sourced drug-target pairs are not representative of the unsourced ones, so a class median fitted on them may not transfer (`fallback_class_definition_2026-11-18.md`) |
| TPM to nCPM fallback (decision 9.129, option D) | the genes outside Huuki-Myers et al. 2025 Table S5 are mostly low-expressed in brain (median TPM about 0.03 against 8 to 17); a fallback reported at 48 to 63 per cent within two-fold on all genes reached 36 to 51 per cent on those genes, and 84 per cent of them could not be scored at all (`tpm_fallback_holdout_2026-11-18.md`) |
| carrier shares (`sequesters`) | 28 of the 35 numeric shares come from one paper's calculation on isolated proteins (McNamara and Meiman 2019, Table 3); old drugs and drugs whose original regulatory reviews are unposted have no carrier data at all; a class claim (SSRIs binding mainly AAG) traced back to secondary statements with no primary measurement found (`carrier_class_definition_2026-11-18.md`, `carrier_fulltext_2026-11-18.md`) |
| kinase substrates (item 4 above) | the source itself states the concentration: "Just 20% of kinases are responsible for the phosphorylation of 87% of currently annotated substrates" |

**Kinds of bias to look for (standard terms).** Study bias (well-studied genes, drugs and targets collect more
records); publication bias (positive or large effects are more often published); ascertainment of the measurable
(values below detection, or proteins that are hard to purify, are missing rather than small); method bias (isolated
protein against whole plasma, one assay type dominating a class); and circular curation (a database row derived from
another database or from a review, counted as an independent source).

**Ways to correct it, to be read and appraised on Fable before any is proposed.**
- Measure it first: for each curated table, compare the sourced rows with the unsourced ones on the covariates the
  build already has (expression, publication count, drug approval year, target family), as the two passes above did.
- Score every fallback on held-out rows that resemble the rows it will be applied to, not on all sourced rows.
- Stratify or weight by publication count, so that well-studied entities do not set a class value alone.
- Treat missing values as possibly missing not at random, with a sensitivity analysis on how far the result moves.
- Prefer systematic screens over literature-curated rows where both exist, and use the screens to estimate the bias of
  the curated rows.
- Count sources by independence (CLAUDE.md, "Manual curation takes more than one source"), tracing a secondary
  statement to its primary measurement before it counts.

**Known limits (do not overstate these in writing).**
- The four cases above are the ones that surfaced while answering other questions, not a measured survey.
- A correction that reweights or imputes is itself a modelling choice and falls under the closest-to-physiology rule:
  it needs a stated justification where it replaces a sourced value.
- Some bias cannot be corrected from the project's data at all: a value never measured for any member of a class leaves
  nothing to calibrate against.

**Added 20 November 2026: a literature pass (on Opus at the owner's request; unconfirmed; needs verification on Fable before it is relied on).** Record: `docs/literature_bias_2026-11-20.md`. Four families of method fit here in part: a sensitivity analysis for values missing not at random (a one-sided shift of each fallback value), weighting the sourced rows toward rows like the unsourced ones, network study-bias corrections, and censored-value (Tobit) handling, the one method that can correct rather than bound, since 5,676 ChEMBL cells hold only a censored value. Heckman selection models do not fit: no credible exclusion variable and too few rows. Measured bias read: the 16% of genes reported by 1991 hold 49% of the 2015 literature; the share of records labelled active is 2.8% in PubChem, 23.3% in ChEMBL and 79.8% in GtoPdb; whether a compound was tested against a target is predictable from ChEMBL itself. Its recommendations for the amendment of `docs/item37_rulings_draft_2026-11-13.md`: score held-out error weighted toward rows resembling the unsourced ones, report a one-sided sensitivity per fallback value, and stratify the held-out split on those covariates before it is fixed, which cannot be added afterwards. A class with no sourced member is not correctable by any method. Four papers were read in full; the rest as abstracts and six as bibliographic records only; its bibliography drafts are not in `docs/references.bib`, building an entry being research on Fable.

---

## 16. DNA methylation as a mechanism

Tagged 2026-11-19, at the owner's request: "Can you please add a dna methylation mechanism to the exploration queue?"
Nothing here is started, and no literature has been read for it; the graph facts below were read by the session on 19
November 2026 from `data/processed/graph_full_neuronal_split_binders_drugs_v5` (files dated 12 November 2026, not the
registered v5 of decision 9.106).

**What the graph holds today.**
- **The reaction is there, and leads nowhere.** DNMT1, DNMT3A, DNMT3B, DNMT3L and TRDMT1 catalyse three Human-GEM
  reactions (`MAR04072` in the cytosol, `MAR08640` and `MAR08641` in the nucleus) that turn DNA and S-adenosylmethionine
  into DNA-5-methylcytosine and S-adenosylhomocysteine. The product node `MAM01722n` has one outgoing edge, into the
  artificial biomass reaction `MAR00021`; `MAM01722c` has none. No edge runs from a methylation state to the
  transcription of any gene.
- **The methyl supply is cut.** SAM and SAH (`MAM02877*`, `MAM02871*`) are tagged currency
  (`graph/tag_currency_metabolites.py`, `DEFAULT_CURRENCY_METABOLITE_NAMES`), so a change in the SAM:SAH ratio, which
  would set the rate of every methyltransferase, does not propagate.
- **The methylation enzymes and readers act as transcription factors instead.** 544 `regulates_transcription_of` edges
  leave DNMT1 (185), DNMT3A (60), DNMT3B (70), DNMT3L (3), MBD1 (17), MBD2 (89), MBD3 (1), MECP2 (34), TET1 (15) and TET2 (1),
  all from CollecTRI. A locus-specific mark is thus written as a direct signed edge from the enzyme's
  protein node to its target genes, with no state in between.
- **Demethylation is absent.** TET1 to TET3 carry ascorbate and Fe2+ `cofactor_of` edges, but catalyse no reaction:
  the oxidation of 5-methylcytosine is not in the graph.
- **One drug acts here.** 5-aza-2'-deoxycytidine (decitabine) is in `configs/centrally_acting_drugs.csv` with targets
  DNMT1 and DNMT3A, marked "target only, no measured Kp,uu,brain".

**The idea.** Represent methylation as a state between the enzymes and transcription: a methylation node (per locus,
per gene, or per class of loci) written by the DNMTs from SAM, erased by the TETs, read by MECP2 and the MBD proteins,
and acting on the transcription of the genes it covers. The SAM:SAH ratio would then reach it from one-carbon
metabolism, which the cofactor edges of `graph/cofactor_edges.py` already name as "the methyl supply of
S-adenosylmethionine".

**What a pass would need to settle (research, so on Fable).**
- A source for which genes a methylation state governs in brain cell classes, with sign, that is not CollecTRI's
  enzyme-to-gene edges again: methylome data by cell class, or curated promoter and enhancer methylation effects.
- Whether SAM and SAH should leave the currency list for this route alone, and what that does to the other
  methyltransferases that share them (catechol O-methyltransferase among them).
- The time scale: methylation is usually taken to change slowly relative to signalling (the session's statement, not
  yet sourced), which would place it with item 11 (chronic exposure) and the readout question there rather than with
  the acute fixed point.

**Known limits (do not overstate these in writing).**
- **DNMT1 is a lockbox perturbation** (`configs/lockbox_v2.json`, both `DNMT1` and `cluster:DNMT1`). A mechanism built
  around it changes how a held-out perturbation propagates, so the work is outcome-blind only while the lockbox is
  undrawn, and its design must not use any result on that perturbation.
- The CollecTRI edges may already carry much of the effect in sign; adding a state could change little in the readout
  while adding parameters, which the pass should measure before proposing a build.
- Methylation is locus-specific; any node coarser than a locus is an approximation and needs the justification the
  closest-to-physiology rule asks for.

---

*Items 17 to 23 were proposed on 20 November 2026 by an agent on Opus 5.5 at the owner's request ("please start an opus agent to identify and add new exploration queue items"), drafted from repository files and the session's reports of that day; unconfirmed: each names the research step that would have to run on Fable.*

## 17. The plasma free fraction as a modulated quantity, not a constant

Tagged 2026-11-20, from the amendment of `docs/item37_rulings_draft_2026-11-13.md`, which already sends it here:
"Modelling the free fraction as a modulated quantity is parked in `docs/exploration_queue.md`, since it would reach
every drug bound at site II" (carrier row 20, temazepam). This page held no such item until now. Nothing here is
started and no source has been read for it beyond those the draft cites.

**The idea.** A drug's free fraction enters as a fixed number: the planned `sequesters` edge from a carrier to its
drug carries a weight of (1 - fu) times the carrier's share (the carrier-share build the amendment rules, D4 of the
session's engineering audit of 20 November 2026, a scratchpad report not in the repository). But for an albumin site
II ligand the free fraction moves with the plasma's fatty acids and condition, not with albumin's concentration. The
draft's own rows show it: temazepam's free fraction does not follow albumin in whole plasma (Chin et al. 2011, slope
about 0; Divoll et al. 1981, r = -0.34, p = 0.06); it differed by 44 per cent between two sampling times 90 minutes
apart after a meal, which van Steveninck et al. attribute to free fatty acids (ruling C1, "heparin artefact not
excluded"); and the site's affinity falls to a tenth at an oleate ratio of 3:1 by a conformational change (Menke and
Rietbrock 1987, measured with a marker ligand, not temazepam), while concentration dependence is refuted (Morino and
Sugiyama 1985, rat). A single fu per drug, which the amendment keeps "as an attribute of the drug node", is therefore
the free fraction of one sampling condition. The idea is to carry what moves it, the site's occupancy by fatty acids
and other endogenous ligands, displacement by a second drug, and the condition of the plasma, so that a drug's free
amount depends on them rather than on a constant.

**What it would change.** The free amount of every drug bound at a modulated site. The amendment names site II; the v4
carrier table (`configs/drug_plasma_carriers_v4.csv`, last changed 11 October 2026) gives albumin, alone or with
orosomucoid, for 47 of its 62 drugs, and records no site. The project already writes one form of the question: a
comparative check of kind `displacement` is "the two drugs, with the carrier's nodes lowered", because "the graph has
no edge from a drug to the carrier it occupies" (`mechanistic_pathway_learning/evaluation/comparative_checks.py`). A
lowered albumin node is not a fatty acid lowering one site's affinity, since it also frees albumin's every other cargo,
so the forms to compare are:
- at entry: a free fraction per labelled example, taken from a value measured in the condition, for an example that
  names the condition or the second drug (the combination type of `evidence/combined_perturbations.py` already carries
  "a drug given with its plasma carrier lower");
- a displacement relation from a site's endogenous ligands (the fatty acids albumin carries, already joined to it by
  the `binds` edges of `graph/plasma_binding.py`) to each drug node bound at that site;
- a gate on the `sequesters` weight read from the fatty-acid pool, the device the 9.81 review describes, which 9.81
  has not ruled on.
The agent's reading, not a source's: a displaced free amount is the product of the drug's amount and the site's
state, which an edge of the linear-response encoder cannot form, so the second form would add free drug in proportion
to the fatty-acid change whatever the dose; the first and third carry the product.

**Cost.** A Fable reading pass first: which drugs of the v5 set bind site II or site I by a measured assignment, and
the measured size of fatty-acid, uraemic and co-medication displacement for them, whole-plasma values before isolated
albumin. Days. The entry form is then a short engineering change on the combination type; a relation or a gate is a
design decision of its own.

**Known limits (do not overstate these in writing).**
- **No label of the study varies a carrier**, so no label trains the `sequesters` relation (`comparative_checks.py`,
  `KINDS_THAT_READ_A_TRAINED_RELATION`), and "every row of the evidence table is a (perturbation, symptom) pair with no
  population axis" (`docs/special_population_carrier_signal.md`, generated 22 October 2026 on `evidence_full_v3`). A
  modulated free fraction would be seen, if at all, in the comparative checks, which describe the model's behaviour
  and are not a test it passes or fails.
- The evidence is for one drug. Its largest number, the 44 per cent, is from a meeting abstract with "heparin artefact
  not excluded" (ruling C1), and Menke and Rietbrock's tenfold fall was measured with a marker ligand.
- Which drugs bind site II is not in the repository: the site is the amendment's reading for temazepam (Fitos et al.
  1986, isolated albumin), not a count over the drug set.

**Status.** Not started. It waits on the carrier-share build, since the weight it would modulate, "Weight = (1 - fu) x
the carrier's share of the binding" (the amendment of `docs/item37_rulings_draft_2026-11-13.md`), is ruled and not yet
built.

---

## 18. The cross-ion shifts and the pump's own current at `VM_c`

Tagged 2026-11-20, proposed by an agent on Opus, not asked for by the owner. From decision 9.112, whose ruling lists
"What every option still misses": "the pump's own current (35% of the Na+ answer, one coefficient on the cytosolic
Na+ pool, -24.5 mV per unit fractional change); the cross-ion chloride shift (a Na+ or K+ current moves [Cl-]i more
than its own pool, which diagonal reaction-to-pool edges cannot carry)", and from the comment beside
`PUMP_CLAMPED_POOL_SENSITIVITY` in `mechanistic_pathway_learning/graph/membrane_potential.py`, which calls the dropped
cross-terms "a stated limit of the build, not an omission". Nothing here is started.

**The idea.** The pool route into `VM_c` weights each cytosolic pool by its own pump-clamped sensitivity, the diagonal
of a 3x3 steady-state response (`docs/extracellular_pool_sensitivities_2026-11-07.md`, section 1). Two terms of the
same source model are carried by no edge: the off-diagonal shifts (a sustained inward Na+ current moves ln[Cl-]i by
+0.1366 per uA/cm2, more than its own pool's +0.0995) and the electrogenic Na+/K+-ATPase's own current, which rises
with cytosolic Na+. Unlike the shunt of item 10, both are linear in the pools, so both could be carried by edges with
no change to the encoder: the pump's current as one more coefficient on the cytosolic Na+ pool's edge into `VM_c`,
and the shifts as further reaction-to-pool edges weighted by the matrix's rows, or as pool-to-pool edges.

**What it would change.** The settled `VM_c` of every perturbation that moves a cytosolic pool. The size, on the source
model's own linearisation and not on any graph (the committed `experiments/derive_pump_leak_pool_sensitivity.py`,
rerun 20 November 2026; the arithmetic below is the agent's, unreviewed): a sodium leak conductance raised by
1 uS/cm2 moves the steady V_m by +0.947 mV. Its conductance term is +1.228 mV and its sodium-pool term -0.065 mV, the
two routes the build carries, +1.163 mV together, 23 per cent above the model's answer; the rest is the pump's own
current (-0.330 mV) and the potassium and chloride shifts (+0.114 mV). For sodium the shifts reverse the sign of the
pool route (-0.065 mV alone, +0.049 mV with them). How much of this reaches a label in the build also depends on the
learned gain of `changes_ion_pool`, and is unmeasured.

**Cost.** Engineering for the edges, a day once the form is chosen, since the coefficients come from the model the
build already cites. Before that, the form is a design choice for the owner, and a Fable check of whether a second
pump-leak model gives the same off-diagonal terms (the 7 November record reads Hübel and Dahlem 2014 and the scheme
they take from Kager et al. 2000 for the extracellular side), so that no coefficient rests on one model alone.

**Known limits (do not overstate these in writing).**
- The matrix is one model's: Düsterwald et al. 2018, a single-compartment rodent pump-leak model at 37 degrees Celsius
  with extracellular concentrations held constant. The shifts depend on its KCC2 strength and pump law, and per-class
  chloride (9.112) would change them.
- The pump's current enters as a response to the Na+ pool. It is not a route for a perturbation of the pump itself:
  in the same model a fractional change of pump capacity moves the steady V_m by only +0.38 mV per unit (a 10 per cent
  loss moves -72.59 to -72.63 mV), because the cube-law pump returns to balancing the leak at a higher [Na+]i.
- Reaction-to-pool edges for the shifts add edges into the pool nodes, so the cone divisor the encoder applies to a
  node's incoming edges (9.16) has to be checked there, as 9.87 and 9.112 did for `VM_c`'s own row.
- `ATP1A1` is a lockbox perturbation (`configs/lockbox_v2.json`, with `cluster:ATP1A1`): a design here must not use any
  result on it.

**Status.** Not started. Not on the critical path: the build goes ahead with both terms stated as limits (9.112).

---

## 19. The energy charge and extracellular ATP, which the currency rule silences

Tagged 2026-11-20, proposed by an agent on Opus, not asked for by the owner. From the currency rule of
`mechanistic_pathway_learning/graph/tag_currency_metabolites.py`, which puts ATP, ADP and AMP on
`DEFAULT_CURRENCY_METABOLITE_NAMES` in every compartment; from `docs/cell_state_representation.md` (13 October 2026, on
the v4 graph), which counts the energy charge among the quantities "computed and discarded" and names
`(ATP + 0.5 ADP) / (ATP + ADP + AMP)` among "the quantities still to be built"; and from closed decision 9.71:
"extracellular ATP is a currency metabolite, so the P2X gating by ATP cannot enter as an edge". No row of
`docs/open_decisions.md` names the energy charge (searched 20 November 2026). Nothing here is started.

**What the graph holds** (counted 20 November 2026 on `data/processed/graph_full_neuronal_split_binders_drugs_v5`,
files dated 12 November 2026, the files item 16 reads and not the registered v5 of decision 9.106).
- Every copy of ATP, ADP and AMP, eight compartments each, is currency, and a currency node's outgoing edges are
  dropped. 1,659 edges leave them: 1,247 `substrate_of`, 275 `cofactor_of`, 16 `binds` and 121 regulation edges,
  79 `inhibits` and 42 `activates`, nearly all from BRENDA. Among the regulation edges, AMP activates six of the
  seven AMPK subunit proteins the graph holds (all but PRKAG2), and cytosolic ATP inhibits
  Reactome's "Activation of ATP sensitive Potassium channels in neuroendocrine cells". So the energy sensors the graph
  already names receive nothing from the state they sense.
- Extracellular ATP (`MAM01371e`) is no hub: 15 outgoing edges, 11 of them OmniPath `binds` edges to P2RX1, P2RX3,
  P2RX4, P2RX7, P2RY1, P2RY2, P2RY4, P2RY11, P2RY13, GPR17 and TRPM4, at sign 0. It is tagged by its name alone, while
  adenosine, its product, is on `NEVER_CURRENCY_NAMES` as a transmitter and propagates.
- A perturbation that lowers ATP synthesis therefore stops at the ATP node. In `data/processed/evidence_full_v5`, 43
  perturbations fall on oxidative phosphorylation and mitochondrial-DNA maintenance genes (a pattern of the agent's
  choosing, not a curated list; 143 rows).

**The idea.** Let the adenylate state act without making ATP a hub, by one of the two devices the project already uses
for that: a multiplier read once after the field settles, as compartment pH and the calcium stores are
(`models/linear_response_encoder.py`, `graph/calcium_stores.py`, decision 9.75), here the energy charge as the ratio
above, which `docs/cell_state_representation.md` notes would need no calibration; or a pool node per compartment with
its feedback confined to the reactions and sensors that depend on it, as `graph/redox_pools.py` does for glutathione
and NADPH. Extracellular ATP is a separate and smaller change: a compartment exemption from the name rule, as
`NEVER_CURRENCY_NAMES` made for the transmitters, plus signed agonist edges to the purinergic receptors, since a
`binds` edge at sign 0 would carry nothing even from an untagged node.

**Cost.** The extracellular exemption is engineering (hours), but the signed receptor edges are curation, so on Fable,
two sources a row: which P2X and P2Y receptors ATP and ADP activate. The energy charge is a design decision for the
owner (multiplier or pool node, which targets it reaches) and then a build of the size of `graph/redox_pools.py`.

**Known limits (do not overstate these in writing).**
- Nothing is measured on a model. That a perturbation's effect stops at ATP is a statement about edges, not about
  labels, and the 43 perturbations may reach their labels by other routes.
- Like the pH and store weights, a multiplier would break positive homogeneity, the registered cost of both; and a
  ratio, not being even in the deviation as the pH weight is, would also break the antisymmetry of a gain and a loss
  of function, as the store weight does.
- The BRENDA rows mix allosteric regulation with product inhibition (ADP, recorded as inhibiting PFKM, PFKL and PFKP,
  is a product of the phosphofructokinase reaction; the agent's reading, not checked against BRENDA's own entries), so
  the targets an energy-charge route reaches need curation before they are trusted.
- Four of the 43 are lockbox perturbations (`BCS1L`, `COX10`, `MFN2`, `UQCRC1`), and so is `ABCC9`, a subunit of the
  ATP-sensitive potassium channel: a design here must not use any result on them.

**Status.** Not started.

---

## 20. Inheritance mode and zygosity of the gene perturbations

Tagged 2026-11-20, proposed by an agent on Opus, not asked for by the owner. From decision 9.73, whose option (b),
"Genebass as a gene-level soft prior for a heterozygous loss perturbation", "needs zygosity in the perturbations" (the
row recommends against (b), on the Genebass measurement, and the choice is still the owner's), and from
`docs/physiological_adherence_review.md` (13 October 2026, on the v4 graph), sections 11 and 14: "every gene
perturbation is a complete knockout at magnitude 1". Nothing here is started.

**What the evidence holds** (counted 20 November 2026 on `data/processed/evidence_full_v5`, files dated 12 November
2026, and on the raw files named).
- Each monogenic report is seeded with "its gene's node, sign and magnitude 1"
  (`mechanistic_pathway_learning/evidence/assemble_evidence_table.py`), so a heterozygous loss and a biallelic loss of
  the same gene are one input. Decision 9.54 (d) already splits a gene's reports by mechanism (loss, hypermorph,
  neomorph, `evidence/allele_mechanisms.py`); nothing splits them by inheritance.
- Both sources the project holds state inheritance per gene and disease. HPO's `genes_to_phenotype.txt` (24 October
  2026) carries it as mode-of-inheritance terms: of the 2,542 gene perturbations, 680 have only autosomal dominant
  rows, 1,034 only autosomal recessive, 365 both and 463 neither. Read per labelled row's own diseases, 105
  perturbations, AARS1 among them, carry labels from a dominant disease and a recessive one at once; 5,794 of the
  9,070 row-to-disease links find no inheritance row, mostly Orphanet diseases, whose inheritance is in Orphadata
  product 9, which is not on disk. Gene2Phenotype's "allelic requirement" (`G2P_all_panels.csv`, 2 November 2026)
  covers 1,528 of the perturbations at definitive, strong or moderate confidence (762 monoallelic, 868 biallelic,
  107 both). `allele_mechanisms.py` already reads that column into `Gene2PhenotypeRecord.allelic_requirement`, and
  nothing uses it.

**The idea.** Carry the dose of the lesion. A heterozygous null halves the gene's dosage and a biallelic null removes
it, so the seed's magnitude would follow the allelic requirement of the disease the report comes from, and a gene whose
reports come from both kinds would become two perturbations, as 9.54 (d) made one per mechanism, each keeping the gene
as its leakage group.

**What it would change.** The input magnitude of most gene perturbations, and the perturbation set itself for the
genes labelled from both kinds. In the linear-response encoder a magnitude scales the whole field, so it reaches a
label only through the head; how much that moves the scores is unmeasured. It would also give option (b) of 9.73 the
input it lacks, whatever the owner decides about (b).

**Cost.** Engineering to carry the field and split the reports, a day, plus a scripted fetch of Orphadata product 9.
The magnitude of each class is research on Fable and then the owner's ruling, under the closest-to-physiology rule:
a value of one half for a heterozygous null is the agent's statement of dosage, not a sourced measurement, and
compensation by the remaining copy, hypomorphic alleles with residual activity and dominant-negative products all move
it.

**Known limits (do not overstate these in writing).**
- Inheritance belongs to a gene and disease pair, not to a gene, and the two sources would have to be reconciled pair
  by pair, with their disagreements recorded beside the rows ("Manual curation takes more than one source").
- Dominant inheritance is not haploinsufficiency: gain of function is typed already (9.54), and a dominant-negative
  loss is a deeper loss than a null copy. X-linked genes differ between hemizygous males and heterozygous females,
  and the evidence table has no population axis, sex included, to say which a label comes from.
- The 105 is a lower edge and the 365 an upper edge of one count, not a measured size, and neither says whether a
  split changes any score.
- It moves the perturbation set, which falls before the held-out draw, so it is outcome-blind only while the lockbox
  is undrawn; a gene in the lockbox stays in it with all its parts.

**Status.** Not started.

---

## 21. The pinned Human-GEM against upstream's open issues and merged fixes

Tagged 2026-11-20, proposed by an agent on Opus, not asked for by the owner. From the Fable passes of 20 November 2026
on the pinned model (`human_gem_errors_2026-11-20.md` and `hgem_q5d_2026-11-20.md` in the session scratchpad, not in
the repository), from the corrections they led to (`configs/human_gem_corrections.csv`, 82 rows under the owner's
rulings of that day, applied where the model is read by `mechanistic_pathway_learning/graph/human_gem_corrections.py`),
and from the owner's ruling recorded in the amendment of `docs/item37_rulings_draft_2026-11-13.md`: "it's ALWAYS fine to
use GitHub's search API". Nothing here is started.

**The idea.** Every repair in the table surfaced while another question was being answered: deuterated ChEBI ids, two
compartment rows filed under the wrong metabolite, NAAA's compartment, two structures, a hydroperoxide reduction
written as a hydrolysis. Upstream already lists whole classes of such defects. The pass of 20 November read, on
upstream's main branch (2.1.1), open issue #1185, which lists 87 charge-unbalanced reactions, "A redox step without its
carrier"; #1173, the "oxidation-as-hydrolysis pattern", which names seven reactions; #1164, which the pass cites for
reactions the source model duplicated across compartments (the 12-lipoxygenase family); and #1119, "Ceramidase
reactions are in the cytosol, where no ceramidase acts". And the pin
(Human-GEM v2.0.1, commit `93e8d292a0cb`, `scripts/fetch_raw_sources.sh`) lacks what upstream merged in 2.1.0 and
2.1.1, of which the passes met some (issue #1085 and pull request #1104, both fixed in 2.1.0, and the 17 ChEBI
replacements of ruling Q3). A sweep would list every reaction and metabolite those issues and merged changes name, find
which are in the graph, and pass those to Fable to be decided one by one through the corrections table, rather than
waiting for each to surface.

**What it would change.** Equations, compartments and gene rules of the metabolic layer, so edges, and a node id
wherever a species is renamed or added, which makes each such build a new graph version. How many of the named
reactions lie on any route to a labelled node is not counted.

**Cost.** Listing the issues and merged changes through GitHub's search API, and reading what they cite, is research,
so on Fable; finding which named reactions are in the graph is engineering, about an hour. Each correction is then a
Fable reading and an owner ruling, as the 82 rows of 20 November were. Whether to move the pin to 2.1.1 instead is a
decision of its own and would not replace the sweep: the issues are open upstream too, and upstream keeps MAR20093 in
the cytosol, which ruling Q5d moved to the lysosome.

**Known limits (do not overstate these in writing).**
- An open issue is a proposal, not a correction. It is a lead to sources, and a row must rest on the sources it cites,
  read on their own, two where possible.
- The 87 are upstream's count on its main branch; the pinned 2.0.1 may hold a different set.
- A correction can change nothing the encoder reads: a participant that is a currency metabolite sends nothing
  (item 19), while a gene rule adds catalysis edges. That is the first thing to check for each class.
- The session's repository scope covers only this project, so the route to upstream is GitHub's search API; the ruling
  that allows it is recorded in the amendment, not yet in `CLAUDE.md`.

**Status.** Not started.

---

## 22. Protein isoforms inside one UniProt entry

Tagged 2026-11-20, proposed by an agent on Opus, not asked for by the owner. From
`mechanistic_pathway_learning/graph/gene_protein_split.py`, which states "Isoforms inside one entry are not
represented: no source resolves them", and from `docs/gene_protein_split.md` (8 October 2026, measured on the
`graph_full_neuronal` graph of that date, so history), which calls isoforms "the largest departure" of the split and
quotes `yang2016widespread`: "The majority of isoform pairs share less than 50% of their interactions" and
"alternative isoforms tend to behave like distinct proteins rather than minor variants of each other". Nothing here
is started.

**The idea.** The split makes one protein node per reviewed entry, and splits a gene with several entries only "where
data tell its entries apart" (the owner, 8 October 2026: "only split apart the ones that can actually be differentiated
from each other by data"). The same rule could reach one level down: an entry gets one protein node per group of
isoforms that a source tells apart, and keeps one node otherwise. Whether any source does is the first question, and
the premise "no source resolves them" is narrower than it reads. It holds for the sources that make edges (the
OmniPath interaction file "holds no isoform accession (0 of 126,125 rows on either side)"; the Reactome exports on disk
name 1,552 accessions, none with an isoform suffix, counted 20 November 2026), but IntAct names isoforms, and decision
9.88 already classes each end of a negative record as canonical or isoform: of the 985 records of
`data/raw/intact/intact_negative.txt` (2 November 2026), 333 name an isoform at one end or both, and 763 of the 983
9.88 counted come from Yang et al. 2016's splice-isoform study, whose isoform-resolved positive records are in no file
on disk (`data/raw/intact/` holds the negative file alone, and OmniPath's file names no isoform).

**What it would change.** Edges from isoform-resolved records would go to the isoform node they name, and an IntAct
negative between isoforms could then contest an edge between the same isoforms, rather than being set aside as 9.88
must set it aside today. A drug or allele that acts on one isoform could be seeded on it. Node ids and degrees change,
so each such build is a new graph version, and the registered degree strata move with the split, as the owner ruled
for the split itself.

**Cost.** A Fable pass first: which sources with verified licences resolve isoforms for positive edges, for brain
expression by cell class (an isoform node with no expression of its own takes its entry's weight) and for drug
targets, each named as a candidate here and none read. Then an extension of the split's grouping rule, about two days of
engineering, and a rebuild.

**Known limits (do not overstate these in writing).**
- Most interaction and drug-target records are gene- or entry-level, so most entries would stay one node; the gain is
  confined to the entries a source resolves, and how many those are is not counted.
- An isoform split without isoform-level expression in the cell classes would give each isoform its entry's weight,
  which states nothing new about where it acts.
- Peptides cut from one precursor (POMC's melanocortins and beta-endorphin on one node, PDYN, PENK) are the
  neighbouring departure in the same table of `docs/gene_protein_split.md` and are not part of this item; peptide
  hormones in the extracellular pool are a separate decision under 9.76.
- An example of why it matters, from the agent's general knowledge and not read for this item: the long and short
  forms of the D2 receptor are isoforms of one entry and are held to differ in their pre- and postsynaptic roles.

**Status.** Not started.

---

## 23. A readout that is not the subthreshold fixed point: when no stable steady state exists

Tagged 2026-11-20, proposed by an agent on Opus, not asked for by the owner. From the registered claim
(`docs/preregistration.md`, item 7: "a fixed-point model cannot represent excitability, and the electrical layer's
seven voltage-gated feedback loops are therefore read at their settled value and not as an action potential"), from
case 8 of `docs/nonlinearity_inventory.md` ("Multistability, hysteresis and sustained oscillation"), and from the
direction the amendment of `docs/item37_rulings_draft_2026-11-13.md` rules and has not built: the gain clamp removed,
saturation inside the loop, a root-finder "with perturbations at a bifurcation detected and flagged", several steady
states combined by noisy-OR, and the owner's "keep only stable roots" and "part of the purpose of moving away from the
single fixed point with forced damping (via gain clamp) is to allow modeling of non-steady-state dynamics". Nothing
here is started.

**The idea.** Once the clamp is gone, a perturbation can leave the system with no stable steady state at all: a
sustained oscillation, or regenerative firing through the voltage-gated loops of the electrical layer. Under "keep only
stable roots" such a perturbation has nothing to read and is only flagged. Multistability goes to the deferred
decision on the search for several steady states; this item is the case with none. What a pass would compare, as
candidates and not findings: the average over the cycle, read from the unclamped iteration the amendment keeps for
per-round readings; the cycle's amplitude as a readout of its own; a rate transfer applied to the settled `VM_c`
after the propagation, placed where the pH weight sits; or flagging and excluding such perturbations, with their count
reported.

**What it would change.** The registered claim, which says the model "must not be read as showing excitability", so
this goes through an amendment; and the prediction for every perturbation without a stable root. The graph already
carries a candidate oscillator in signed form: in the v5 graph files (dated 12 November 2026) 124 edges join the nodes
of 20 clock genes of the agent's choosing (among them 48 `regulates_transcription_of`, 30 `inhibits` and 22
`activates`), and the evidence holds PER2, PER3, CRY1, RORA and RORB perturbations with one row each, besides
insomnia and somnolence among its symptoms.

**Cost.** The first step is engineering and cheap: a count of the graph's negative-feedback cycles, beside the count
of positive-feedback cycles the amendment already asks for before the root-finder is built. The rest waits on the
root-finder: a Fable reading pass on how rate and mean-field models read a limit cycle, then design and the owner's
ruling.

**Known limits (do not overstate these in writing).**
- Nothing is measured. How many perturbations would have no stable root is unknown until the unclamped root-finder
  exists, and it may be none.
- A round is not physical time, which the amendment states, so a period read from rounds is no period in seconds; only
  summaries free of time (an average, an amplitude) would mean anything.
- An action potential needs fast gating kinetics and, for conduction, space (9.128: "spatial and suprathreshold"),
  which the graph does not carry; a rate transfer would be a stated layer needing a source, not physiology the graph
  derives.
- `FBXL3`, a clock gene, is a lockbox perturbation: a design here must not use any result on it. The readout records
  retired by decisions 9.103 and 9.104 are not evidence for or against any of this.

**Status.** Not started. Waits on the root-finder of the amendment.

---
