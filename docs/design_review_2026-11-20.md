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

---

## Added 20 November 2026: a check of flaws 1, 3 and 5 against the code

A second Opus pass, at the owner's request ("yes, have an opus agent check those"), tried to refute three of the flaws above; unconfirmed in the same way. Its report follows as written, its own heading demoted.

### Check of three flaws claimed by the design review of 20 November 2026

Run on Opus at the owner's request; unconfirmed.

Claims 1 and 2 were read at HEAD `7b637d48` and claims 3a to 3c at `0f65736c`, both on 20 November 2026, read-only
(the pass was stopped by a container restart after claim 3b's reading and resumed at `0f65736c`). Between the two
heads, of the files cited here only `docs/item37_rulings_draft_2026-11-13.md` moved, its section 20 one line down;
the claim 2 citations below give the `0f65736c` lines. The review checked is
`design_review_2026-11-20.md` (C1, C3, H2 and H3 in its own numbering; the brief's claims 1, 2 and 3), the scratchpad
copy, which commit `3386cc63` added unchanged as `docs/design_review_2026-11-20.md`.

## Claim 1 (review C1): the tested configuration and the lockbox are the obsolete ones

**Verdict: CONFIRMED as a mismatch between registration and code; the consequence ("run as written, would score
the wrong configuration") is real but already recorded and gated, so it is not a hidden flaw.**

What the code and registration hold, at `7b637d48`:

- `configs/registered_rules.json` `tested_models.value` = `["confirmatory_v2_linear_response_noisy_or"]`,
  `robustness_models.value` = `["confirmatory_v2_message_passing_noisy_or"]`; code location "configs/head_choice.json
  chosen values".
- `configs/head_choice.json`: `"lockbox": "configs/lockbox_v2.json"`, `"chosen": {"linear_response":
  "confirmatory_v2_linear_response_noisy_or"}`. Its own note: "The check compares paths rather than the lockbox's
  SHA-256, so it would not notice configs/lockbox_v2.json being redrawn for v4 (decision 1.2)."
- `experiments/run_main_model_batch.py:283-284`: `"confirmatory_v2_linear_response_noisy_or": [... *LINEAR_RESPONSE_ENCODER_V2,
  *FULL_GRAPH_ARGUMENTS_V2, ...]`; lines 43-44: `graph_full_neuronal_split_binders`, `evidence_full_v2`,
  `better_v2_full_v2.parquet`. The registered v4 flags are `V4_LINEAR_RESPONSE_MODEL` (line 88), whose comment
  (lines 70-73) says "No data path is here ... the rebuild of decision 1.2 is still owed". No configuration binds
  them to the v5 tables: `git grep` finds no `confirmatory_v4`, `confirmatory_v5` or `drugs_v5` in the batch file.
- `configs/lockbox_v2.json`: `drawn_at 2026-10-08T07:38:49+00:00`, `group_by disease_cluster_and_targets`, evidence
  SHA `228a4afe…` (evidence_full_v2), 317 perturbations, 28 drugs; committed in `6af9eb11` (2026-10-08). No other
  lockbox file exists (`configs/lockbox_v1.json`, `configs/lockbox_v2.json` only).
- `experiments/draw_lockbox.py:5-6`: "Units are the leakage groups of --group-by (disease_cluster_and_targets ...)";
  `draw_groups` takes whole groups; defaults `evidence_full_v2` and `better_v1_full_v2`. Item 25's rule is in
  `mechanistic_pathway_learning/evaluation/target_held_out_split.py` (with `REGISTERED_HELD_OUT_FRACTION = 1 / 7`,
  asserted by `tests/test_registration_matches_the_code.py:108-111`), but no draw script or the trainer imports it;
  its importers are `leakage_only_adversary.py`, `experiments/measure_leakage_only_adversary.py`,
  `experiments/label_review/off_targets_under_the_target_split.py` and its test. The trainer's
  `--group-by` (`experiments/run_main_model.py:1858`) offers `gene`, `disease_cluster`, `disease_cluster_and_targets`
  only, and `read_lockbox` reads a group-based lockbox.

What the registered documents say, which is where the claim weakens:

- `docs/preregistration.md` item 25 (line 1835 on): the held-out set "is split on mechanism targets, not on drugs";
  "The held-out set is redrawn under this rule"; item 2 (line 1144): "Its membership is redrawn on the table of item 1".
- `docs/open_decisions.md` 1.1 (line 21): "Drawn only on the owner's go-ahead ... Every confirmatory run hangs on 1.1
  and nothing downstream can start"; 1.2 (line 22): "the rebuild and the redraw are owed".
- `docs/confirmatory_runbook.md:27-34` already states the mismatch: "The held-out set is not drawn. The lockbox the
  steps name, configs/lockbox_v2.json, was drawn on the evidence_full_v2 table ... The registered model is the v4 flags
  ... on the v5 tables and the graph `graph_full_neuronal_split_binders_drugs_v5`. The confirmatory_v2 configurations
  below ... are the family as registered on 9 October 2026; no lockbox run has been made on either." Lines 39-44 add
  that the v5 graph is to be rebuilt when 9.112 is built.
- Safety that exists: `read_lockbox` (`mechanistic_pathway_learning/evaluation/experiment_data.py:265-273`) refuses a
  lockbox drawn on another evidence table, label selection or grouping, so a v5 run cannot be scored on lockbox_v2 by
  accident; but the v2 configuration with lockbox_v2 passes every check, and that pair is exactly what the registered
  rule names. `runs/full/confirmatory_lockbox.sh` is not in this checkout (git ignores `runs/`), so the job script was
  not read.

So: the registered name and the head-choice file point at the 9 October family and lockbox_v2, while the registered
prose and the runbook say the tested model is the v4 flags on v5 tables with an item-25 held-out set that has not been
drawn. The lockbox of item 25 has not been drawn at all; lockbox_v2 was drawn on 8 October on evidence_full_v2 and has
never been scored. The review's own word "would" is right only for someone who runs the job against decision 1.1.

Smallest fix (engineering, then an amendment): (1) add a `confirmatory_v5_linear_response_noisy_or` (and the
message-passing twin) from `V4_*_MODEL` with explicit v5 data paths; (2) a draw script that applies
`target_held_out_split` on the drug side and the disease-cluster grouping on the gene side, writing a lockbox file
with evidence and label-selection SHA-256, plus a trainer/`read_lockbox` path that accepts it (the current check that
no group straddles the lockbox does not hold under item 25, since a held-out drug's group may not be held out whole);
(3) make `head_choice.json` and `score_confirmatory.chosen_models` compare the lockbox's SHA-256, not its path.
**Needs an amendment** (`Amends:` trailer) to change `tested_models`/`robustness_models` to the new names; the owner's
go-ahead under 1.1 governs only the draw itself. It needs no new owner ruling on substance, since item 25, 1.2 and the
runbook already say what the tested model is.

## Claim 2 (review C3): curation with every label visible, before the draw, reverses section 20's order

**Verdict: PARTLY. The facts are right; the claim that they breach section 20 is not.**

What is right:

- The held-out set of item 25 is undrawn (claim 1 above; `docs/open_decisions.md` 1.1 open, 1.2 "the rebuild and
  the redraw are owed"). Every curation pass so far (targets, actions, occupancies, carriers, constructs, label rules)
  ran over all perturbations with every label in the tables, so the draw does come after the curation.
- Some fixes were prompted by a known drug-symptom pair. 9.124 (`docs/open_decisions.md:244`) opens "after the
  owner's challenge in 9.121 C2: 'Levodopa is used to TREAT Parkinsonism via conversion to dopamine. How could that
  CAUSE Parkinsonism'". `configs/physiology_validation_set.csv` line 2 is a drug-symptom chain that is also a label
  ("chain,drug,haloperidol,DRD2,antagonist,parkinsonism,induces,A,pet_occupancy_threshold"), audited against the graph
  (9.51, `docs/open_decisions.md:171`). The preregistration itself records label-informed curation: two crosswalk
  exclusions "were found by looking at which genes a term supplies" (`docs/preregistration.md:103`).

What is wrong or overstated:

- **Section 20's scope.** `docs/item37_rulings_draft_2026-11-13.md:1664-1673`, ruled 20 November 2026 (recorded in
  `fac771ef`, "confirmed by the owner"): "**fix the held-out split first and permanently, then draw any sourcing sample
  at random from the training portion only.** ... The order to avoid is the reverse: sampling at random across
  everything and then removing the held-out hits". It governs **random sourcing samples drawn to constrain
  parameters**, and the order it forbids is sample-then-remove-held-out-hits. The owner's words make it prospective:
  "Add that version as a required step eventually". It is "a project-wide rule ... to be recorded as its own
  decision", and no such row exists yet (`grep -i "training portion\|circularity\|sourcing sample"
  docs/open_decisions.md` finds nothing of it). Exhaustive sourcing ("each of the 206 pairs with no value gets a sourcing
  attempt", lines 1680-1681) is not a sample and is outside the rule's mechanism. No curation done before 20 November ran
  under it, so none can have reversed it.
- **The registration permits pre-draw curation in so many words.** The label rule is fixed "from evidence properties
  only ... never from any model's predictions" (`docs/preregistration.md:62-63`), which forbids model-informed
  choices, not label-visible ones. Item 34: "Every one was outcome-blind: no lockbox has been drawn, so no
  confirmatory result existed to see" (`docs/preregistration.md:2602-2603`). The decision log puts graph changes before
  the draw on purpose: 9.69, option (a), "a graph change, so before `draw_lockbox.py`" (`docs/open_decisions.md:189`).
  So the registered meaning of "outcome-blind" is "no lockbox score seen", and on that meaning nothing was breached.

What remains as a fair point: a fix that repairs the route of a specific labelled pair (9.124's own-indication rule,
the validation chains) may later be scored if that drug lands in the held-out set. That is a disclosed limitation of
the registered design, not a breach of section 20.

Smallest fix: (1) record section 20's rule as its own decision row, as the ruling itself asks, stating its scope
(random sourcing samples; prospective from the draw); (2) add a disclosure to the registration that curation before
the draw saw every label and name the label-triggered fixes (9.124, 9.51's chains), with a held-out reading split by
whether a drug's own targets or labels were edited, which can be mined from git. (1) is the owner's own ruling written
down and needs only their confirmation of the wording; (2) is an amendment and needs an owner ruling, since it adds a
reading. The review's remedy (i), to draw now and freeze membership by hash, conflicts with 9.69 (a)'s "before
`draw_lockbox.py`": target re-derivations (gabapentin and pregabalin to CACNA2D1) change item 25's partition, so it
needs an owner ruling and is not the smallest fix.


## Claim 3a (review H2, first half): the registered memorisation control cannot run on the registered drug-entry form

**Verdict: CONFIRMED.** Read at `0f65736c`.

- The control is registered and carries weight. Item 4 reports "the permuted-target negative control" beside the
  score (`docs/preregistration.md:1171-1172`), and item 25b reads it "as the primary answer to whether the model uses
  mechanism or drug identity, because no split can settle it structurally" (`docs/preregistration.md:1915-1917`).
- The registered model seeds a drug on its entry node. The v4 flags (`experiments/run_main_model_batch.py:78-91`) set
  no `--drug-entry`, so the trainer passes `drug_entry=arguments.drug_entry or "nodes"`
  (`experiments/run_main_model.py:2285`; the help at `:2163`: "nodes seeds each drug on its own node, which is the
  default there"), and `load_experiment_data` sets `drug_entry=None if entry_table is None else "nodes"`
  (`mechanistic_pathway_learning/evaluation/experiment_data.py:730`). The registered graph
  `graph_full_neuronal_split_binders_drugs_v5` holds `drug_entry_nodes.parquet` (its summary: 260 drug nodes, 1,268
  mechanism edges), and the registration assumes that form ("for a drug seeded on its entry node, its mechanism
  targets", `docs/preregistration.md:1698`).
- The control refuses that form: "--permute-drug-targets exchanges a drug's seeds, and a drug seeded on its entry node
  has one seed, its own node; its targets are its mechanism edges. Use --drug-entry targets with it"
  (`experiments/run_main_model.py:2373-2376`). The guard came in with the control itself (`ac2d0f14`, 12 October
  2026), two days after entry nodes became the default (`82b3052d`, 10 October), so the control has never been
  runnable on the registered form.
- Nothing schedules it. None of the 97 entries of `CONFIGURATIONS` carries `--permute-drug-targets` or `--drug-entry`
  (checked by importing the module). Runbook step 4 is "the 30 lockbox runs (two models, ... seeds 0 to 4, real labels,
  permuted labels and a symmetric rewiring ...)" (`docs/confirmatory_runbook.md:151-152`), and the registered run plan
  has "Per seed and model, two control runs" (permuted labels, rewiring) and "A model missing any of its fifteen runs is
  not confirmatory" (`docs/preregistration.md:179-183`). No document records the gap (`grep` of `docs/` for the flag
  and the control).

Refutations tried, and why they fail. (i) `--drug-entry targets` lets the flag run, but that is "the ablation arm"
(help, `experiments/run_main_model.py:2164`), a different model input, so a permuted-target score there is not a
control of the tested model. (ii) No other option permutes drug targets: the trainer's other permutations are
`--permute-labels`, `--permute-soft-priors`, `--permute-edge-priors` and the rewiring, and no entry-node permutation
exists anywhere in the code (`grep`). The review's link to 9.35b's leakage is its own reading and was not checked.

Smallest fix. Engineering: in the entry-node form, exchange the drug nodes' mechanism-edge target sets among drugs with
the same number of targets, as a derangement (what `permuted_drug_targets`, `experiments/run_main_model.py:1503`, does
to seeds), each edge keeping its sign and weight, with the permuted edges hashed into the run's summary; a test that a
permuted drug node keeps its degree and loses its targets; one configuration per model; the arm (5 seeds per model)
in the job and in runbook step 4; and a reading in the scorer (3b). **Needs an amendment, not a new ruling on
substance**: items 4 and 25b already register "Permuting which targets each drug has and retraining"
(`docs/preregistration.md:1917`), which an edge permutation is, but the registered run plan counts fifteen runs per
model, so adding the arm amends it (an `Amends:` trailer), and the owner confirms the amendment.

## Claim 3b (review H2, second half): the unseen-mechanism stratum of item 25c is not in the scoring code

**Verdict: CONFIRMED, and the gap is wider: item 4's other two readings are not in the scorer either.** Read at
`0f65736c`.

- Registered: 25c is "Scored apart on the held-out drugs **none** of whose targets appears in training"; "It is the
  study's only estimate of extrapolation to a mechanism never trained on, it is underpowered, and it is fixed here
  before the draw so it cannot be chosen after a result is seen" (`docs/preregistration.md:1951-1955`).
- The scorer has no such reading. `experiments/score_confirmatory.py` (571 lines) scores three variants,
  `VARIANT_SUFFIXES = {"real": "", "permuted": "_permuted", "rewired": "_rewired"}` (`:84`), on
  `H1_READINGS = ("macro", "micro", "macro_within_degree_strata", "micro_within_degree_strata")` (`:86`) with the
  permuted-label and rewiring differences; `grep -i` for unseen, 25c, target_held_out, input size and extrapolation
  finds nothing.
- The helper exists, tested, with no consumer: `mechanisms_never_trained`, "what the unseen-mechanism stratum of item
  25c is scored on" (`mechanistic_pathway_learning/evaluation/target_held_out_split.py:87-94`), is called only by its
  test (`tests/test_target_held_out_split.py:72`).
- Item 4's input-size baseline and target-count strata exist only in development tools: `run_baselines.py
  --with-input-size` (`experiments/run_baselines.py:442`) and `target_count_strata_metric`
  (`experiments/aggregate_main_model_runs.py:75-76`). The scorer reads neither, and runbook step 4 names neither; the
  lockbox-baselines job (`runs/full/lockbox_v2_baselines`) is not in this checkout, so whether it passes
  `--with-input-size` was not seen.

Refutations tried, and why they fail. 25c is secondary and item 4 "changing no model", so neither enters H1, and the
readings could be computed by hand from saved predictions after the score. That would not keep 25c's "fixed here
before the draw": a reading first coded after the lockbox is scored can be shaped by it. The scorer also could not read
25c today whatever its code, because the lockbox it reads (`lockbox_v2`, drawn by groups) holds no target partition
(claim 1).

Smallest fix. Engineering, after claim 1's draw script: a 25c reading in `score_confirmatory.py` that takes the
held-out drugs from the item-25 lockbox file, applies `mechanisms_never_trained`, and reports the drugs whose every
target is untrained with their macro AUPRC and group-bootstrap interval, outside the tested family; the input-size
baseline run in the lockbox-baselines job and the target-count strata and the permuted-target difference (3a) read
beside the score; a test for each on a synthetic lockbox; all committed before the draw. **Needs no owner ruling and no
amendment** for the readings, which items 4 and 25c register; only the permuted-target runs need 3a's amendment.

## Claim 3c (review H3): the registered membrane-potential rule gives the wrong sign for 376 of 382 reactions

**Verdict: CONFIRMED in substance, and now reproduced on the current graphs. The count's precision and three side
claims need correcting.** Read at `0f65736c`. The recount is a count of edges and signs on the graphs of 12 November
2026, not a trained run.

What holds:

- **Registered.** `membrane_potential_build` is "computed_from_the_pools" (`configs/registered_rules.json:79-83`,
  amendment item 35), asserted by `tests/test_registration_matches_the_code.py:124-137` and passed on both builds by
  `scripts/rebuild_data_layer.sh:93,201`. The law is used linearised, "change in V_m = sum_ion ( g_ion / g_total ) *
  (RT / z_ion F) * ( fractional change in [ion]_out - fractional change in [ion]_in )"
  (`mechanistic_pathway_learning/graph/membrane_potential.py:17-18`), so only the concentration term reaches `VM_c`.
- **Ruled, and in no graph.** 9.112's last cell: "ruled (1) with (3), the carrier gap stated; its sub-questions all
  ruled 7 Nov; the amendment of docs/item37_rulings_draft_2026-11-13.md's draft amended under 9.129 (12 Nov); open: registering the amendment of docs/item37_rulings_draft_2026-11-13.md and the rebuild"
  (`docs/open_decisions.md:232`). `graph_full_neuronal` and its seven variants on disk are from the rebuild of 12
  November 2026, whose script says "It does NOT build amendment the amendment of docs/item37_rulings_draft_2026-11-13.md: both calls to build_neuronal_graph_variant.py
  in scripts/rebuild_data_layer.sh keep --membrane-potential computed_from_the_pools" (`runs/rebuild/rebuild_v5_november_12.sh:2-4`, a local file git
  ignores). `data/processed/graph_full_neuronal/neuronal_variant_summary.json` records `membrane_potential_build`
  computed_from_the_pools, `conductance_edges` {} and 6 `driving_force` edges; the registered
  `graph_full_neuronal_split_binders_drugs_v5` has the same 6 edges into `VM_c` and 9 `voltage_gates` edges out.
- **Reproduced, not only cited.** Finding 17 was counted on the 4 November graph (`docs/research_summary.md:209-211`),
  which is no longer on disk. Recounted read-only on the 12 November graphs (scratchpad
  `design_review_check_tools/recount_vm_signs.py`, `recount_vm_signs_charge.py`, `recount_normalised.py`, output
  `recount_12nov.csv`): on `graph_full_neuronal` and on `graph_full_neuronal_split_binders_drugs_v5` alike, 415
  reactions reach a driving-force pool, and with the charge of Na+, K+, Cl- and Ca2+ at Human-GEM's stoichiometry
  **382 have both signs nonzero, 376 carry the opposite sign and 6 agree** (MAR04932, MAR05429, MAR05447, MAR07631,
  MAR07639, RCT_8949703). 9.112's first count (`changes_ion_pool` edges only: 370, 348, 345, three agreeing Na+/Ca2+
  exchangers) also reproduces exactly. So the numbers now stand on the current graph, measured 20 November 2026.
- **Training cannot undo it.** Signed relations take positive gains, "positive for signed relations, either sign for
  unsigned ones" (`mechanistic_pathway_learning/models/linear_response_encoder.py:1129-1134`), and `binds` is the only
  unsigned relation (`:132`), so no gain can flip `driving_force`. The encoder's division does not rescue it either:
  dividing each edge by its pool's in-weight (Na+ 368 and 366, K+ 42 and 34, Cl- 49 and 49, an approximation of the
  registered divisor), 377 of 393 are opposite; the division gives a sign to 23 Na+/Cl- cotransporters whose two
  terms cancel exactly before it.

What needs correcting:

- **"376 of 382 electrogenic reactions" is a four-ion count.** Its reference charge leaves out H+, HCO3-, NH4+ and
  co-transported organic ions. On Human-GEM's own charges, 83 of the 376 are electroneutral (for example `MAR05430`,
  Na+/H+ exchange, and `MAR01528`, Na+/NH4+) and 8 agree in sign (for example `MAR08076` and `MAR08077`, Na+ with two
  HCO3-), which gives **285 opposite of 299, 14 agreeing**, with 89 electroneutral reactions given a nonzero pool
  route (wrong in kind, as 9.112 says of KCC2 and NKCC1). In the other direction, unit-signed Reactome edges make the
  Na+/K+-ATPase (`RCT_936897`) and the EAATs (`RCT_210404`) look electroneutral; both agree in sign with the pool
  route. Neither reference is the physiological one (Human-GEM simplifies some carriers), and which carriers are
  electrogenic is a reading for Fable. On every reference tried, 95 to 98 percent of the charge-moving reactions carry
  the wrong sign, so the substance stands; the figure should carry its reference.
- **"Not built" is true of the graphs, not of the code.** The replacement is in the code as a fourth build,
  `pores_and_clamped_pools` (`mechanistic_pathway_learning/graph/reactome_import.py:137-157`: it "exists because the
  pool route alone carries the opposite of the electrical sign for 376 of 382 charge-moving reactions (9.112)"),
  selectable by `--membrane-potential` (`experiments/build_neuronal_graph_variant.py:333-345`). What is missing is
  the amendment of docs/item37_rulings_draft_2026-11-13.md's registration ("Nothing here is built", `docs/item37_rulings_draft_2026-11-13.md:6`) and the rebuild. A
  parallel engineering pass of 20 November holds three more commits to that build on an unpushed local branch
  (scratchpad `eng_pore_build_2026-11-20.progress.md`). The comment at `reactome_import.py:137` and the help at
  `build_neuronal_graph_variant.py:341` say the amendment of docs/item37_rulings_draft_2026-11-13.md "registers" the build, which it does not yet: stale in tense,
  recorded here and not fixed (this pass is read-only).
- **"Any electrical route to a symptom is currently backwards" overstates "nearly every".** 6 of 382 agree (14 of 299
  on Human-GEM's charges), electroneutral carriers are wrong in kind rather than sign, and a Ca2+ route that does not
  pass through `VM_c` keeps the right sign of the ion's movement. What is backwards is the route through `VM_c`'s 9
  `voltage_gates` edges for nearly every input. Whether the scored AUPRC is sensitive to it was not measured: a learned
  readout may absorb a near-uniform flip at `VM_c`, while the direction and route claims (P1, framing c) cannot.
- **"9.138 (the sink requirement)" names no decision.** The highest id on any branch is 9.131 (the CLAUDE.md command,
  after a fetch); 9.138 is an id drafted in this session's scratch records, and the requirement itself is in the item
  37 draft: "the row is to be drafted, dropping the requirement that a module contain a seed while keeping the sink
  requirement" (`docs/item37_rulings_draft_2026-11-13.md:1915-1916`). 9.118 (`docs/open_decisions.md:238`) and 9.119
  (`:239`) are open, as the review says.
- **The review's remedy conflicts with a standing ruling.** Moving the rest of the amendment of docs/item37_rulings_draft_2026-11-13.md, 9.118 and 9.119 "to robustness
  or post-exam arms" runs against the owner's ruling of 27 October 2026 in CLAUDE.md, "this project IS the qualifying
  exam", under which work is not deferred until after the exam. A dated architecture freeze is the owner's to decide.

Smallest fix. (1) Engineering: land the `pores_and_clamped_pools` build, with the parallel pass's commits, and add a
test on a built graph that each single-ion pore reaches `VM_c` with the sign of E_i - V_rest. (2) The registration:
amendment the amendment of docs/item37_rulings_draft_2026-11-13.md with an `Amends:` trailer changing `membrane_potential_build` to `pores_and_clamped_pools`, with the
test at `tests/test_registration_matches_the_code.py:124-137` and both calls in `scripts/rebuild_data_layer.sh`. (3) The
rebuild of the v5 graphs (a long job, not started here) and a recount of finding 17 on it. 9.112's substance needs no
new ruling (ruled 4 and 7 November), but **registering it needs an owner ruling on timing**: the owner asked to rule
all of the amendment of docs/item37_rulings_draft_2026-11-13.md before any of it is entered ("Let's rule on the rest of it first",
`docs/item37_rulings_draft_2026-11-13.md:5-6`), so registering 9.112's build ahead of the rest is theirs to allow.
Stating finding 17's reference charge corrects a recorded measurement and goes to the owner with this report.

## Verdicts and fixes

| claim | verdict | smallest fix | needs |
|---|---|---|---|
| 1 (C1) tested configuration and lockbox | CONFIRMED as a mismatch; already recorded and gated by 1.1 | `confirmatory_v5_*` configurations, an item-25 draw script, lockbox compared by SHA-256 | amendment for `tested_models`/`robustness_models` |
| 2 (C3) curation before the draw | PARTLY: facts right, breach of section 20 not | section 20's rule as its own decision row; a disclosure with a touched/untouched reading | the owner's confirmation of the row; an amendment and a ruling for the reading |
| 3a (H2) permuted-target control | CONFIRMED | permute the drug nodes' mechanism edges; 5 seeds per model in the job | amendment of the run plan (fifteen runs per model) |
| 3b (H2) 25c not in the scorer | CONFIRMED, wider (item 4's readings too) | 25c, input-size and target-count readings in `score_confirmatory.py`, before the draw | none |
| 3c (H3) membrane-potential sign | CONFIRMED in substance, reproduced on the 12 Nov graphs; figure is four-ion, "not built" is graphs only, 9.138 does not exist | land `pores_and_clamped_pools`, register it, rebuild | amendment the amendment of docs/item37_rulings_draft_2026-11-13.md; an owner ruling to register it ahead of the rest of the amendment of docs/item37_rulings_draft_2026-11-13.md |
