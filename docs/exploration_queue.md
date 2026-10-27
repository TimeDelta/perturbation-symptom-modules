# Exploration queue

Ideas parked for later so they stop taking up working memory. Nothing here is registered or required for the
confirmatory analysis, and nothing here is started. An item names what it would change, what it would cost and the
limits that must not be overstated when it is written up.

This document moved into the repository on 26 October 2026 from the Project note `claude/exploration_queue.md`
(**that note was deleted on 27 October 2026**, when the owner ruled the repository the single source of truth: "Everything should rely on the repo moving forward"; it is named here as the provenance of this page and not as a document to read),
under the owner's standing rule that sources are recorded in the repository. Items 1 to 4 are carried over as they
were tagged; items 5 and 6 are new, both added on 26 October 2026, and items 7 and 8 were added on 27 October 2026.

Checked against `main` at `0b976bf` on 26 October 2026.

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
- Most phosphosites have no annotated function (Needham et al. 2019, Sci Signal; cited from memory, not verified).
- Desensitisation as a mechanism waits on case 4 of `docs/nonlinearity_inventory.md`; explicit phosphorylation adds
  nothing there until saturation enters the propagation.

**Status.** Parked behind the qualifying exam, the 9.97 cyclase handoff and the decisions in `docs/status.md`.

---

## 5. Occupancy as the drug seed magnitude

Tagged 2026-10-26. The owner's question of 26 October 2026, on reading that a drug enters at magnitude 1: "But
complete removal seems harsh". Written on Opus from repository files; the literature below was read on Opus and is
**not yet rechecked on Fable** (CLAUDE.md "Models").

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

**What the literature says, read on Opus on 26 October 2026 and awaiting a Fable recheck.**
- Occupancy at therapeutic doses is high but far from complete, and it varies within one drug: haloperidol at 1.0
  or 2.5 mg/day gave D2 occupancies of 38 to 87 percent across 22 patients, with response, hyperprolactinaemia and
  extrapyramidal effects becoming likely above 65, 72 and 78 percent (Kapur et al. 2000,
  [doi:10.1176/appi.ajp.157.4.514](https://doi.org/10.1176/appi.ajp.157.4.514)).
- Five selective serotonin reuptake inhibitors at their minimum therapeutic doses occupied 76 to 85 percent of the
  serotonin transporter, with occupancy rising nonlinearly and plateauing at higher doses (Meyer et al. 2004,
  [doi:10.1176/appi.ajp.161.5.826](https://doi.org/10.1176/appi.ajp.161.5.826)).
- Dose is the wrong anchor, which is why the measured concentration is the right one: saturable presystemic
  metabolism is "one of the more important sources of nonlinearity", named for verapamil, propranolol and
  hydralazine, and makes concentration depend on the rate of absorption as well as the dose, though the same review
  notes that only a few drugs in use show nonlinear behaviour with clinical implications (Ludden 1991,
  [doi:10.2165/00003088-199120060-00001](https://doi.org/10.2165/00003088-199120060-00001)). In perfused rat liver
  propranolol's bioavailability rose from 0.012 to 0.288 over a four-fold concentration range (Ghabrial et al. 1994,
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
