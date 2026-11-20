# Critical review of the experimental design, 20 November 2026

Run on Opus at the owner's request; unconfirmed; needs verification on Fable and the owner's reading before it is relied on.

Scope and state read. Repository at HEAD `8eccf472` (20 November 2026). `docs/status.md` was generated on 2026-11-14 at
`072e637f-dirty`, so its counts may lag HEAD. No confirmatory run has been scored, the held-out set has not been drawn
on the v4/v5 tables (decisions 1.1, 1.2), and every slice-period number is retired as evidence (research_summary.md,
status paragraph; decision 9.103). So every flaw below is a flaw in a design that has not yet been run, and most of the
remedies can still be applied before the draw. No outside source was read for this review. I found no text addressed
to an AI in anything I read. The item 37 draft records one source-rule breach of its own (section 22: papers read
through the Consensus connector after jbc.org's robots file refused them, which the draft treats as unread and then
replaced with copies the owner supplied). I note it here and did not act on it.

Labels. Everything under "my reading" is my own reasoning on Opus. Every severity is mine.

## 1. Flaws, ranked by severity

### Critical

**C1. The tested model's registered name runs on the obsolete data, and the registered split is not in the draw code
(a mismatch between registration and code).**
- Evidence. `configs/registered_rules.json` `tested_models` = `confirmatory_v2_linear_response_noisy_or`. In
  `experiments/run_main_model_batch.py:283` that configuration expands `FULL_GRAPH_ARGUMENTS_V2` (lines 43-44):
  `graph_full_neuronal_split_binders`, `evidence_full_v2`, `better_v2_full_v2.parquet`. `configs/head_choice.json`
  binds it to `configs/lockbox_v2.json`, which was drawn on 8 October on `evidence_full_v2`. The check compares paths
  and not hashes ("it would not notice configs/lockbox_v2.json being redrawn"). Against that, `docs/confirmatory_runbook.md:27-34`
  says that "The registered model is the v4 flags ... (`V4_LINEAR_RESPONSE_MODEL`) ... on the v5 tables and the graph
  `graph_full_neuronal_split_binders_drugs_v5`". Amendment item 25 registers a target-partition held-out set
  (prereg ~1835-1958). But `experiments/draw_lockbox.py:5-6,62` still draws whole `disease_cluster_and_targets`
  groups, `V4_SHARED_MODEL` (batch:78) passes `--group-by disease_cluster_and_targets`, and
  `evaluation/target_held_out_split.py` is imported only by the measurement scripts
  (`measure_leakage_only_adversary.py`, `label_review/...`).
- Why it matters. The registry asserts that a name matches a config, but it does not assert that the config is the
  registered model. Run as written, `runs/full/confirmatory_lockbox.sh` would score the wrong graph, labels, split
  and lockbox. Because the lockbox is spent only once, a confirmatory run on the wrong configuration cannot be repeated.
- Remedy. Before the draw: define a `confirmatory_v5_*` configuration from `V4_*_MODEL` with explicit data paths,
  re-register `tested_models` and `robustness_models` to it under an `Amends:` trailer, and implement item 25 in a
  `draw_held_out.py` that writes the drug-side target partition and the gene-side clusters in one file, with that
  file's SHA-256 recorded in `head_choice.json`. Add a test that the tested configuration's graph, evidence and label
  hashes equal the registered ones. Cost: about one day of engineering plus one amendment. (My reading. Verify by
  running the job script with `--dry-run`, if one exists.)

**C2. Confounding by indication in the drug labels, with no rule for it, while the likelihood assumes no false reports
(construct validity).**
- Evidence. Decision 9.124 (open_decisions.md:244) read 106 drug-construct pairs that carry both a "relieves" record
  and "induces" reports, and classed most of them as "the treated disease in the trial or post-marketing population".
  Examples: depressed_mood 2 genuine against 15 population, bradykinesia 1 against 11, psychosis 0 against 4. Its
  masking rule is still open. `positive_unlabelled_likelihood.py:60`: "The false-report rate b is 0 unless set per
  perturbation type". The grade-B selection keeps a pair at a label frequency of 1 percent or more, or when both SIDER
  and OnSIDES list it (prereg, "Better training examples"). Neither condition is a comparison with placebo.
- Why it matters. An antipsychotic "inducing" psychosis, or a dopamine agonist "inducing" parkinsonism, teaches the
  model that a mechanism produces the symptom it actually relieves. In the drug stratum this also rewards popularity
  among drugs of one class, and a sign-aware mechanistic encoder is penalised for being right. It falls on exactly the
  drugs the physiology work concentrates on. It is also not limited to the 106 pairs that carry a relieves record.
  Postmarketing sections inherit the same population and co-prescription confounding (item 13, my inference).
- Remedy. Rule on 9.124 before the draw. Mask an "induces" pair on a construct the drug relieves unless a
  placebo-controlled rate shows an excess, as proposed. More generally, prefer label rows that carry a placebo arm
  (the item 1(d) machinery exists), set b > 0 for grade-B drug rows from a measured audit sample, and report the drug
  stratum with and without population-confounded pairs. Cost: the 9.124 rule is about a day. A 100-pair audit to
  estimate b is a Fable pass of a day or two.

**C3. The held-out set will be drawn after every curation decision, and those decisions were taken with every label
in view (internal validity).**
- Evidence. Item 37 draft section 20 (lines ~1663-1672), ruled: "fix the held-out split first and permanently, then
  draw any sourcing sample at random from the training portion only ... The order to avoid is the reverse". In fact
  drug targets, actions, occupancies and carriers (sections 13-22), symptom constructs (9.58, 9.96), the crosswalk
  exclusions found "by looking at which genes a term supplies" (prereg, symptom expansion), the label rules (9.124)
  and the physiology validation chains (9.51; `configs/physiology_validation_set.csv` rows such as haloperidol,
  DRD2, parkinsonism, which are themselves labels) were all built across all perturbations before any v5 split
  existed. Development models were also run on the 20 October build (9.106), on folds that contain perturbations
  that will enter the new held-out set.
- Why it matters. Most of this curation is label-blind physiology, and the preregistration's rule is "never from any
  model's predictions" (my reading: mostly honoured). Some of it was triggered by a label or a known drug-symptom chain,
  though: 9.124 began with the owner's levodopa and parkinsonism challenge, and the audit checks chains against the
  graph. That kind of curation selectively repairs the routes for pairs that will later be scored. The lockbox is
  therefore not untouched in the sense a reader at the exam will assume.
- Remedy. (i) Draw the item-25 held-out set now, on the current tables, and freeze its membership by hash, even if
  the graph changes later. Item 25 already allows graph changes after the draw if they are outcome-blind. Every later
  sourcing pass then follows the section-20 rule. (ii) Keep a "touched" log of the perturbations whose own targets,
  labels or validation chain a session edited, and report the held-out score in the touched and untouched strata
  separately. Most of the log can be recovered from git (`configs/*.csv` rows keyed by drug). (iii) Add a prospective
  temporal stratum: gene-symptom pairs added to HPO, and drug label events added, after the freeze date. Those labels
  could not have influenced any choice. Cost: (i) hours, (ii) one or two days of git mining, (iii) waiting for HPO and
  label releases. The stratum is small, and finding 4 (history) suggests the score on it will be low.

### High

**H1. No power analysis exists for the design being registered (statistical validity).**
- Evidence. 5.2 and 8.8 are "outstanding" (open_decisions.md:71,105). The only precision statements (prereg:39, 215)
  were measured on the slice and on v0.4/v2, which are retired as evidence. Item 25 holds out 14.5 percent of the 222
  drugs (prereg:1869), about 32 drugs. In 9.35b a leakage-only adversary reached drug-stratum macro +0.054 with a
  per-draw SE of 0.038, and "as few as 4" held-out drugs have any leaked neighbour. Drug groups: 17, the largest
  holding 51 percent of drugs (prereg item 25).
- Why it matters. The mechanistic claims (occupancy, carriers, pH, signed propagation) concern drugs, but the macro
  AUPRC will be dominated by roughly 200 genes and by intellectual disability (20 percent of pairs, 9.61). A group
  bootstrap over a handful of drug clusters is unreliable: with few clusters, percentile intervals undercover (my
  reading, a known property of the cluster bootstrap). Seeds are averaged and not resampled (prereg:215 caveat). A
  null result on the drug side will be uninformative, and a positive one fragile.
- Remedy. Run the 8.8 simulation on v5 before the draw: plant a module effect of known size and measure the power of
  H1 per stratum and pooled. Register the drug and gene strata as separate co-primary readings, each with its own
  power, or state in advance that the drug claim is exploratory. For a drug side this small, use a wild cluster
  bootstrap or a permutation test over held-out drug groups. Cost: the simulation is about 2-4 days of compute and
  code. The rest is an amendment.

**H2. The registered memorisation control cannot run on the registered drug-entry form, and the unseen-mechanism
stratum is not in the scoring code (mismatch between registration and code).**
- Evidence. Items 4 and 25b make the permuted-target control "the primary answer to whether the model uses mechanism
  or drug identity". `run_main_model.py:2373-2376` raises an error when `drug_entry == "nodes"`, which is the default
  on graphs with drug entry nodes (line 2162: "nodes ... which is the default there"), and the v4/v5 graphs are
  `_drugs_` graphs. The confirmatory job is 30 runs of real, permuted-label and rewired variants (runbook step 4),
  with no permuted-target arm. `score_confirmatory.py` has no reading for the unseen-mechanism stratum of item 25c
  (grep finds no such code).
- Why it matters. Without the permuted-target control, a win cannot be told apart from drug-identity memorisation
  through shared targets, which is exactly the leakage of 9.35b. 25c is "the study's only estimate of extrapolation".
- Remedy. Permute the drug-to-target mechanism edges instead of the seeds when entry is through nodes. Add the arm
  (5 seeds) to the job. Add 25c and the input-size baseline as readings in `score_confirmatory.py`. Cost: 1-2 days of
  code plus 5 to 10 more lockbox runs, about 6-12 hours at the registered step times. (My reading; this needs to be
  checked against the v5 entry mode.)

**H3. A registered graph rule is known to be wrong in sign, and the model is still changing (construct and internal
validity).**
- Evidence. research_summary.md:138, finding 17: under `membrane_potential_build = computed_from_the_pools`, 376 of
  382 electrogenic reactions "carry the opposite sign". The replacement was ruled on 4 November 2026 (9.112) and is
  not built. The rule is still registered. Item 37 (around 40 rulings, "Nothing here is built"), 9.119 (the support
  reparameterisation, open), 9.118 (chronic exposure, open) and 9.138 (the sink requirement) all change the
  architecture before the run.
- Why it matters. Any electrical route to a symptom is currently backwards, and the pathway claims (P1, framing c)
  read routes. More generally, the registration describes a moving target. Each change is outcome-blind, but their
  number is itself a forking path over the development data, and it is also the owner's stated limit ("doesn't go too
  far for me to be able to understand").
- Remedy. Set a dated architecture freeze: build 9.112 and the ruled part of item 37, and move the rest of item 37,
  9.118 and 9.119's open options to robustness or post-exam arms. Register the frozen model under its own hashes. Run
  the untrained sign check of finding 10 (`check_linear_response_signs.py`, re-pinned) on the frozen graph for the
  GCH1 worked case before the exam. The slice note in `linear_response_encoder.py` (dopamine "still rises, through a
  route not yet traced") is the warning for that case. Cost: the freeze is a decision; building 9.112 is days.

**H4. The nosology readout cannot separate "the graph" from "a low-rank factorisation of the labels" (construct
validity for framing a).**
- Evidence. Item 26a/e: the profile is the symptom's link column over 8 modules, and the control is the same
  clustering on "the symptom columns of the raw outcome matrix". With 8 modules the noisy-OR head is a rank-8
  factorisation of the perturbation-by-symptom matrix (my reading). Raw-column clustering is a different estimator, so
  a difference between the two partitions can arise from the factorisation's rank and smoothing alone, with no
  contribution from the graph. The registered profile is "8 modules by 2 relations" (prereg:1966-1970, 2079), but
  `relieves` is never trained (run_main_model.py:202, 2961; noisy_or...:187-188 constant initialisation), and
  `nosology_readout.py:155-157` says so ("every run does today ... gives a profile of half that"). It clusters
  symptoms, not conditions.
- Why it matters. The readout's "only positive claim" is the difference from the co-occurrence partition, and that
  difference is confounded with the head's inductive bias.
- Remedy. Add a no-graph twin with the same head as the control: the same noisy-OR head on free perturbation
  embeddings, or `--encoder none` (as in `b3_degree_only`), at rank 8, together with the rewired-graph fit. What the
  graph adds is then the difference from that twin. Amend 26a to one relation, or train `relieves`. Cost: 5 more
  development fits. The amendment is cheap.

### Medium

**M1. Gene and drug labels are different constructs pooled in one macro average (construct and external validity).**
HPO annotations are lifelong, often developmental phenotypes of monogenic syndromes (734 genes whose only label is
intellectual disability, 9.61). Drug labels are acute or subchronic pharmacological effects in treated adults. Item 24
records that a knockout and an inhibitor enter almost identically, and chronic adaptation is unrepresented (9.118). A
pooled macro answers neither question cleanly. Remedy: report the strata as co-primary (as in H1), rule 9.61 (option
(b) or (d) keeps ID from dominating), and state that the steady-state claim covers acute effects only. Cost: an
amendment.

**M2. Many parameters for few labels, and module identifiability is untested.** 98.2 percent of 405,908 parameters
are module supports, about 90 gates per positive (9.119). G1 and G2 gate P1, but P1's power is unknown (5.2). Remedy:
build 9.119's reduced support space before the draw and include the support count in the H1 simulation. Cost: already
planned.

**M3. The label-propensity constants reuse a loss weight.** pi_0 = w + (1 - w) r(t, s), with w = 0.2 taken from the
old negative weight (positive_unlabelled_likelihood.py), and b = 0. This is a numerical convenience, and CLAUDE.md
asks for a stated justification for that kind of choice. Remedy: add a sensitivity arm (w in {0.1, 0.4}) as a
robustness reading, and justify w in 9.90. Cost: development runs only.

**M4. Bootstrap and readings.** The intersection-union test over 4 readings is conservative, which is fine. The best
baseline is chosen as the maximum of 6 on the lockbox. That is also conservative (winner's curse in the baseline's
favour). Documents still say "four baselines" (9.131), while the code holds six, including type_popularity
(score_confirmatory.py:82). That is the stricter version and correct per 9.35b, but the documents should match.
Check that the lockbox baseline job passes `--with-type-popularity` (I did not find it in the runbook; unsure).

**M5. Study bias couples the graph and the labels.** Well-studied genes and drugs have more curated edges and more
reported labels (exploration_queue item 15). The degree strata and the popularity slope of the propensity cover part
of this. Remedy: add literature-popularity strata beside the degree strata as a secondary reading. Cost: small.

### Low

L1. `head_choice.json` checks the lockbox by path (noted in C1). L2. The status page lags HEAD by 6 days, so
regenerate it before the draw. L3. Item 25's one-seventh is a convention, and the registration says so honestly. No
change is needed.

## 2. Framings

All of this section is my own reasoning.

**(a) Nosology: do modules carve conditions by mechanism rather than by diagnosis?**
- What the design supports now. A descriptive clustering of symptoms over 8 modules, fitted in sample (item 26), with
  a co-occurrence control and a resampling stability test.
- What it would need.
  - Carve conditions, not symptoms. That means clustering perturbations (the monogenic disorders, and drugs) by module
    activation (option A of 9.64).
  - Compare the result with diagnostic groupings (Orphanet or ICD classes, DSM/HiTOP through a map fixed in advance)
    and with symptom-profile clustering. The claim is "mechanism carves differently and more usefully".
  - A criterion for "better". 9.131's treatment-differentiation objective needs a trained `relieves` relation and
    STAR*D/CATIE, and access to both is blocked (faculty lead recipient).
  - The no-graph twin of H4.
- Flaws that matter most. H4, M1 (monogenic and developmental labels standing in for common psychiatric conditions),
  M2, C2.
- Verdict. Not defensible as a confirmatory claim at the exam. It is defensible as a pre-registered descriptive
  analysis with an explicit null.

**(b) Drug interactions, including co-prescription (item 13).**
- What the design supports now. Almost nothing as a test.
  - A combination is the sum of its seeds, and the encoder is linear (9.130(b)). A departure from additivity can only
    come from the noisy-OR head, the bottleneck and the pH ceiling, and nobody has measured how large those are.
  - The 106 two-drug, enzyme and carrier statements are training labels (item 17), so they cannot also be the test.
  - Most interaction data is pharmacokinetic, while the clearance edges live only in the `_v4_enzymes` variant.
  - FAERS pair signals carry the co-prescription confounding of item 13. Single-drug postmarketing label rows
    plausibly carry some of it too (C2).
- What it would need.
  - A pharmacodynamic CNS interaction set from a licence-verified source (Fable).
  - Scoring against the additive baseline, preregistered outcome-blind.
  - The minimal co-prescription skip table of item 13, and a co-medication adjustment before any FAERS-derived pair is
    used.
  - A measured nonlinearity budget for the head.
- Flaws that matter most. C2, the linearity, and the label overlap.
- Verdict. Post-exam, as the owner has already parked it (9.130).

**(c) Symptom pathway prediction: which route links a perturbation to a symptom.**
- What the design supports now. P1 behind the G1 and G2 gates, the module supports, the closed-form sensitivity of the
  linear response, and the GCH1 worked case (9.120).
- What it would need.
  - A held-out benchmark of known routes. The 60-row `physiology_validation_set.csv` and the 37 curated-module
    perturbations are candidates, but both were curated in view of the graph, so the routes would have to be frozen
    and kept out of the audit loop.
  - A correct electrical sign (H3).
  - A route faithfulness test, such as ablating the claimed route and checking that the predicted symptom falls.
  - A P1 power estimate (5.2).
- Flaws that matter most. H3 (sign errors invalidate routes directly), M2 (identifiability), C3 (circularity of the
  validation chains).
- Verdict. Defensible as a worked-case demonstration (GCH1, HMBS), not as a statistical claim.

**(d1) Adverse psychiatric-effect prediction for drugs with new mechanisms.**
- What the design supports now. This is the closest fit. The item-25 target split is designed for it, 25c is the
  unseen-mechanism stratum, and the baselines include TransE and the random walk.
- What it would need. H2 (the permuted-target control and 25c in the scoring code), C2 (the label confound) and H1
  (the drug-side power).
- Verdict. The drug-side claim is the one that most directly uses the physiology the owner prioritised.

**(d2) Target and gene prioritisation: which genes' loss produces which symptoms.**
- What the design supports now. The gene stratum. Its shared-node leakage channel is empty (9.35b), and it holds most
  of the power.
- What it would need. A pathway-grouped or subsystem split as a secondary reading. Finding 12 (history) showed that
  the disease-cluster split divides pathways, and finding 3 (history) showed that baselines are at chance inside a
  held-out pathway. It also needs ID ruled (9.61).
- Flaws that matter most. M1, and pathway leakage.

**(d3) Mechanism-of-action inference for poorly characterised drugs (the inverse problem).**
- What it would need. Score candidate target sets by the likelihood of the drug's observed label profile, and
  evaluate on held-out drugs with known targets masked.
- Weakness. Many drugs share targets (58 of 192 targets are held by six or more drugs), so it is identifiable only up
  to equivalence classes.
- Verdict. A good post-exam extension, needing no new data.

**(d4) Drug repurposing.** Not supported. It needs `relieves`, which is never trained (9.131), and the
indication-confounded labels of C2 bias it.

## 3. Recommended exam framing

This recommendation is mine. Put the confirmatory claim forward as hypothesis mining: the recovery of held-out causal
perturbation-to-symptom links. That is what the owner ruled on 13 November 2026 (9.131). Report it in two pre-declared
strata:
- Genes, where the power is.
- Drugs with new mechanisms (item 25, with 25c and the permuted-target control). This is where the physiology is
  tested, and its power is stated honestly.

Alongside the claim:
- The nosology readout, as a registered descriptive secondary with the no-graph twin.
- GCH1 as the worked pathway case, checked for sign on the frozen graph.

Before the draw:
- Fix C1, C2, H2 and H3.
- Run the power simulation (H1).
- Draw the held-out set and freeze it, with the touched-perturbation log (C3).

This framing needs the least new machinery. It is the one the split and controls were designed for, and it does not
depend on the blocked STAR*D access.
