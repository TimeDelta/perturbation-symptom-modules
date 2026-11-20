# Real-world problems the model could answer for the qualifying exam (second week of January 2027)

Research pass of 7 November 2026, on Fable 5.1 (no fallback occurred), at commit `ca8eda1` (HEAD of `main` and of
`origin/main` at the start of the pass; working tree clean). This file rules nothing and changes nothing in the
repository. It costs the owner's four named framings and proposes others, each as a real-world scientific question
the model answers. The 9.112 sign correction and the evaluation methodology appear only as enabling work, as the
owner ruled (commit `ca8eda1`: "the intermediate problem must be a real-world scientific question the model answers,
not an internal result such as the 9.112 membrane-potential sign correction or the evaluation methodology").

Reading convention. "Some results" means a development-level reading on the current graph, reported with its graph
and date, under the registered split rule, with its controls, and never a confirmatory lockbox score. Every
measurement below that predates the v5 build is cited as history under decisions 9.82 and 9.103
(`docs/research_summary.md`, status paragraph: "ANY numbers from that time are to have the same treatment"). No text
addressed to an AI assistant was met in any file read.

---

## 1. What the model can answer today

**Built.** The v5 data layer exists on this container, built by `scripts/rebuild_data_layer.sh` on 5 November 2026
from `main` at `1e98f5d` (decision 9.106, dated addition of 5 November 2026): `graph_full_neuronal_split_binders_drugs_v5`,
49,834 nodes and 275,006 edges, Reactome release 98, one allele node `ALLELE:HTT_CAG_repeat_expansion`. It "still
carries the membrane-potential layer that 9.112 ruled on and has not built, so it is rebuilt from `graph_full_neuronal`
when 9.112 is built, and no run reads it as the registered graph before then" (`docs/confirmatory_runbook.md`, the
dated paragraph on the v5 graph). So **every framing below that trains a model waits on the owner ruling 9.112 and on
a rebuild of the neuronal variants** (the 4-5 November rebuild took about a day of wall time for the fine stage; the
rebuild from `graph_full_neuronal` is shorter, since the base graph stands).

**Trained.** Nothing on v5. "No full-graph model has scored a test set" (`docs/preregistration.md`, confirmatory
specification); "no confirmatory run has been scored, and the held-out set waits for the owner's go-ahead (decision
1.1) and the v4 rebuild and redraw (decision 1.2)" (`docs/research_summary.md`, Aim 2). The runbook's step 1c, the
second family's development runs, "refuses to start without runs/full/v2_development.go" and has not run
(`docs/confirmatory_runbook.md`, step 1c). The registered model is the linear-response encoder with the noisy-OR head
(`tested_models` = `confirmatory_v2_linear_response_noisy_or`, `configs/registered_rules.json`), the message-passing
encoder a robustness reading (9.77). The trainer runs grouped folds with or without a lockbox file (`--lockbox`
defaults to `None`, `experiments/run_main_model.py:1833`), so a development reading on v5 needs no draw.

**Lockbox.** None drawn on v5. `configs/lockbox_v2.json` was drawn on `evidence_full_v2` and is superseded by the
registered redraw on the rebuilt table under item 25's target partition, "only on the owner's go-ahead and under the
leakage ceiling of decision 9.35 (decisions 1.1 and 1.2)" (`docs/confirmatory_runbook.md`); `held_out_fraction` is
1/7 (`configs/registered_rules.json`). 9.35 (the ceiling) is "Unbuilt either way" (`docs/open_decisions.md`, row
9.35). The draw is one-shot and the scoring runs once ("score_confirmatory.py runs once; a second scoring ... is not
done", runbook, Blinding). A framing that needs the draw therefore needs 9.35 ruled and built, 1.2's orphenadrine
measurement, 1.1's go-ahead, the Reactome release pinned (9.111), then "30 lockbox runs" plus baselines, which the
registration costed at "about 70 hours" for 60 runs on the smaller October graph (`docs/preregistration.md`, Compute).

**Labels held on v5** (`data/processed/evidence_full_v5/evidence_summary.json`, built 5 November 2026): 9,414
observations over 2,768 perturbations and 38 fine symptom constructs; by class and relation, monogenic induces 6,433,
pharmacological induces 2,841, pharmacological relieves 140; by grade A 5,456, B 2,981, C 977. Reports: 20,590 rows
from HPO-OMIM (3,948 positive, 153 negative), HPO-Orphanet (5,945 / 38), SIDER-label 7,625, SIDER-indication 187,
OnSIDES-label 2,694. Drugs: 230 (listed in section 3.1 below by class where it matters). The label selection
`better_v2_full_v5` keeps 4,486 of 8,221 positive pairs (3,265 gene, 1,221 drug; 1,740 genes and 161 drugs with a kept
positive) and masks 965 grade-C gene pairs; kept drug pairs by relation (my join of the selection to the evidence
table, 7 November 2026): induces 1,221, **relieves 51**.

**Soft evidence held, never labels** (grade C or D; `--soft-prior-reports`, decision 9.48): FAERS 2,370 signals and
124 absences over 230 drugs (`data/processed/faers_v5/faers_summary.json`); ClinicalTrials.gov adverse-event arms
2,887 positive and 794 negative reports (`clinical_trials_v5/clinical_trial_summary.json`); trial outcome measures
231 relief, 74 worsening, 12 no-effect comparisons (`docs/clinical_trial_outcome_evidence.md`, generated 5 November
2026 against `evidence_full_v4`); IMPC 1,255 positive and 21,091 negative knockout reports over 5,361 human genes
(`docs/impc_knockout_evidence.md`, generated 4 November 2026); MGI, SFARI, RGD, ZFIN, FlyBase and WormBase tables
(decisions 9.93, 9.94; `docs/mouse_sources_measured_v5.md`, measured 24 October 2026 on the 22 October build, so
history for the current graph). Evidenced negatives (9.92): Phenopacket Store exclusions and statin trial negatives,
behind flags off by default.

**What the model gives, once trained, that a real-world question can use**: for a held-out gene allele or drug, a
probability per symptom and relation; per symptom, the modules linked to it with their supports (mechanism cards,
`mechanistic_pathway_learning/evaluation/mechanism_cards.py`, "one mechanism card per symptom"); and, for the
linear-response encoder alone, the closed-form steady-state field of any perturbation on every node without training
(the registered reason it is the tested model, `configs/registered_rules.json`, `tested_models`). Untrained, the field
reaches physiology nodes but not symptoms; the symptom map needs the trained head.

---

## 2. The four named framings, costed

Common to all four: (i) 9.112 ruled and the neuronal variants rebuilt before any training; (ii) one set of
development runs of the registered configuration on five grouped folds, seed 0, with the development baselines and
the permuted-label control (the content of runbook step 1c, run without a lockbox file or on a declared development
pseudo-draw of item 25's rule, as 9.35b's 20 pseudo-draws were made), which is of the order of a few days on the
4-core machine by the registration's timing (2.1 s per step, about 35 epochs to early stopping, on the smaller
October graph; v5 is larger); (iii) interpretation of the readings on Fable (CLAUDE.md, Models). None of the four
needs the confirmatory draw for a development-level answer; each is flagged where its confirmatory form would.

### 2.1 Predict a perturbation's symptoms, scoped to one drug class

- **Claim.** Routing a drug's mechanism targets through the physiology graph predicts which psychiatric and motor
  constructs its label reports, for drugs whose targets the model never trained on.
- **Evidence held.** Scoped to the dopamine D2-ligand class: 26 antipsychotic ingredients are in v5
  (amisulpride to ziprasidone, listed by my query of 7 November 2026); they carry 96 grade-B induces pairs on the
  extrapyramidal constructs (parkinsonism 26, akathisia 25, bradykinesia 18, cogwheel rigidity 11, restlessness 10,
  resting tremor 6), of which 45 are kept by `better_v2_full_v5`; across all 57 drugs with a kept extrapyramidal
  pair there are 105 kept pairs (parkinsonism 43 drugs, akathisia 31, bradykinesia 26). The mirror class is held too:
  dopamine agonists (levodopa, pramipexole, ropinirole, rotigotine, pergolide, apomorphine, bromocriptine,
  cabergoline) with label pairs on hallucinations and psychosis, and 5 kept relieves pairs on parkinsonism. FAERS and
  trial-arm comparisons on the same pairs exist as soft validation strata.
- **Must be built or ruled first.** 9.112 (the D2 route runs through Gi-coupled signalling and GIRK potassium
  conductance, which is exactly the layer 9.112 found inverted); the development runs above; a declared development
  hold-out that puts the D2 ligands in the test fold. Under the trainer's `disease_cluster_and_targets` grouping, with
  `--max-drug-targets 0`, how the 230 drugs chain into groups on v5 is unmeasured (the v2 lockbox history records one
  group of 232 perturbations holding 63 drugs); item 25's target partition is the registered alternative and holds a
  target out with every drug sharing it. Which to use for development is an owner question (Q1 below).
- **Some results by mid-January.** For the fold that holds the D2 ligands out: AUPRC and the paired difference
  against the best baseline on the extrapyramidal constructs for those drugs; the mechanism card of parkinsonism
  naming the modules and the route from DRD2; the same reading on the permuted-label run. A confirmatory version
  needs the draw: **strong cost, not proposed**.
- **Cost.** Low beyond the common cost: a per-class slice of the readings the pipeline already writes, plus a Fable
  pass checking the route the cards name against the pharmacology literature.
- **Main risk.** The whole class leaves training together, so the model must reach parkinsonism from DRD2 by
  propagation through nodes trained on other perturbations; a null here is informative but is the benchmark result
  the owner does not want as the headline. Label-text pairs without frequencies are the majority of the class's
  evidence (`evidence_code` label_text and non_us_label_section).
- **Within the owner's reach.** Yes: one receptor, one pathway, one symptom family, one table of readings.

### 2.2 Mechanistic nosology (Aim 3)

- **Claim.** Symptom constructs that the fitted modules link through the same physiology share a mechanistic basis
  across the disorders they are curated in.
- **Evidence held.** The 38 constructs' label profiles; external structure for validation only (Grotzinger et al.
  2022, Cross-Disorder Group 2019, `docs/nosology_discovery_options.md` section 4).
- **Must be built or ruled first.** Everything in 2.1's common list, then stable consensus modules across seeds and
  folds (design section 5.5), then decision 9.64's three questions (which unit first, whether option A leads, whether
  external structures are compared before the lockbox is read). The registration makes Aim 3 "conditional on Aim 2"
  (`docs/research_summary.md`), so pursuing it before the confirmatory test needs the owner to reframe it as
  exploratory, in a dated amendment.
- **Some results.** A symptom-by-module link matrix from the development runs with its cross-seed stability, and the
  grouping of constructs it implies, against a null from the rewired-graph run. No draw needed for this; the
  validation on held-out perturbations the draft prescribes would.
- **Cost.** Medium: three to five seeds of the development runs, the matching code of option (A), the null of (D).
- **Main risk.** Highest of the four: on the slice no module passed the sufficiency test (finding 6, history), and
  whether v5 modules are stable is unmeasured. A nosology from unstable modules is not a result.
- **Within reach.** The reading is, the stability machinery less so. Best kept as "where this leads" in the exam.

### 2.3 Drug repurposing

- **Claim.** A drug's predicted "relieves" probability for a construct it is not indicated for is a testable
  hypothesis that registered trials or the literature already bear on.
- **Evidence held.** 140 relieves pairs (SIDER-indication, grade B), 51 kept; 231 trial-outcome relief comparisons
  and 12 no-effect comparisons on crosswalked scales (grade C soft, `docs/clinical_trial_outcome_evidence.md`),
  which is the natural external check: a predicted off-indication relief either has a placebo-controlled comparison
  with results or does not.
- **Must be built or ruled first.** The common list; nothing else registered. The relieves head trains on 51 kept
  pairs, so a decision on whether trial-outcome relief comparisons may enter the relieves labels for a development
  reading (they are "never a label" under 9.48 and 9.60) would change the picture and is an owner question.
- **Some results.** A ranked list of the top off-indication relieves predictions from the development folds, each
  checked on Fable against ClinicalTrials.gov results and PubMed, with a null from randomly paired drugs and
  constructs. No draw needed.
- **Cost.** Low compute, medium research (one literature pass per prediction).
- **Main risk.** 51 training pairs; the relieves matrix is the thinnest object in the model, and a hit list is easy
  to over-read. Defensible as a hypothesis generator, not as a validated prediction.
- **Within reach.** Yes.

### 2.4 Explain one disorder

- **Claim.** The model's route from one gene's loss of function to its curated symptom profile matches the known
  mechanism of that disorder, with the gene held out of training.
- **Evidence held.** Candidates with grade-A profiles on v5 and a mechanism inside the metabolic layer, where the
  graph is closest to physiology: HMBS (acute intermittent porphyria; 8 grade-A constructs including anxiety,
  hallucinations, insomnia, paranoia), ATP7B (Wilson disease; 9, including psychosis, depressed mood, parkinsonism),
  GCH1 (dopa-responsive dystonia; 10, including parkinsonism, depressed mood, anxiety), PAH, CYP27A1, NPC1, OTC. Each
  is a single gene whose pathway (heme, copper, tetrahydrobiopterin and dopamine, phenylalanine, bile acid,
  cholesterol transport, urea) is in Human-GEM. Genes absent from v5 among those I checked: GLUL, KCNT1, PNPO, PRRT2,
  CPT2, ETFDH, MUT, RNASEH2A, UMPS (no evidence row).
- **Must be built or ruled first.** The common list; the choice of disorder (owner, Q2); for a channelopathy
  (SCN2A, SCN1A, GABRA1, GABRG2, KCNQ2, CACNA1A all carry labels) also 9.113 and the shunt limit of exploration item
  10, so a channelopathy is the costlier choice and sits closest to the bug fix the owner ruled out.
- **Some results.** From the fold holding the gene out: its predicted profile against the HPO profile and against a
  degree-matched gene's; the mechanism cards of its top constructs; the untrained closed-form field from the gene to
  the pathway nodes a Fable literature pass names as the mechanism. No draw needed.
- **Cost.** Low once the development runs exist; one Fable pass per disorder for the mechanism sources.
- **Main risk.** A single worked case is a narrative unless quantified against the matched control; and the gene's
  disease cluster leaves training with it, so the profile must come from the pathway, which is the point.
- **Within reach.** Yes; the most legible of the four.

---

## 3. Other options

### 3.1 Developed

- **Dopamine-axis positive control, both directions (developed; folds into 2.1 and 2.4).** One mechanism, read in
  two directions and two perturbation types: D2 antagonists and VMAT2 depletion (tetrabenazine carries kept
  parkinsonism and depressed-mood pairs) induce parkinsonism; GCH1, TH and SLC6A3 loss of function carry grade-A
  parkinsonism; dopamine agonists and levodopa relieve it and induce hallucinations. The model has never seen this
  told as one story, and the labels for all of it are held. Recommended as the headline question's shape: "does one
  pathway, perturbed from either side by genes and drugs, give the symptom profile physiology says it should?"
- **Cross-species check on hyperactivity (developed as a secondary validation).** IMPC holds 507 positive and 4,626
  negative hyperactivity reports with validity "strong" (`docs/impc_knockout_evidence.md`), on genes the model scores
  without training on mouse data. Reading: AUPRC of the model's human hyperactivity score against the IMPC call on
  genes IMPC tested. No draw. Risk: the base rates measured on the 22 October build showed IMPC calls barely enrich
  the human labels (hyperactivity 6/84 against 0.048 base, `docs/mouse_sources_measured_v5.md`, history), and the
  human head trains on 84 kept hyperactivity gene pairs. Cheap, independent of HPO curation, worth one table.
- **Antipsychotic-class recovery of extrapyramidal effects as a positive control.** Developed inside 2.1; it is the
  same reading. Prolactin is not a construct of the 38 and is outside the symptom scope, so the prolactin half of the
  owner's example needs a construct addition (`configs/symptom_construct_additions.csv`, a crosswalk row, an
  amendment) and is an owner decision (Q3); the graph has a pituitary class (GTEx Pituitary, `docs/data_sources.md`),
  so it is feasible but not free.

### 3.2 Rejected, with the reason

- **Specific adverse-event questions outside the construct set.** Tardive dyskinesia, hyponatraemia and
  agranulocytosis are not among the 38 constructs; the first is a chronic adaptation a linear response around rest
  does not represent, the other two are renal, endocrine or haematological end-points the neuronal graph does not
  reach. Each would need a new construct, a label source and graph content, before January. Rejected as headline.
- **Channelopathy symptom account as the headline.** Feasible in labels (section 2.4) but it tests the layer 9.112
  and 9.113 are still ruling on, so it is the bug fix in another coat; keep for after the rebuild, as a secondary
  case if time allows.
- **Cross-species beyond IMPC as headline.** Literature mouse sources carry the selection bias the measured page
  names ("made for genes already tied to the human phenotype"); IMPC alone is usable, and as validation, not as the
  question.

---

## 4. Ranked recommendation and a dated path

Ranked by the most defensible real-world result for the least that must be ruled or drawn:

1. **The dopamine axis, both directions (2.1 with 2.4's GCH1 or a D2 drug as the worked case).** One pathway, genes
   and drugs, labels held on both sides, no draw, legible.
2. **Explain one metabolic disorder (2.4: HMBS or ATP7B)**, from the same development runs at no extra training.
3. **IMPC hyperactivity validation (3.1)**, one table, as support.
4. **Repurposing hit list (2.3)**, as hypothesis generation only.
5. **Nosology (2.2)**, as the exam's forward look, not its result.

None of the five needs the confirmatory draw. Dates (proposals; each step waits on the one above it):

| dates | step | who |
| --- | --- | --- |
| 7-14 Nov | owner rules 9.112 (and 9.113, 9.114, or defers them with disclosure); answers Q1-Q3; rebuild of the neuronal variants from `graph_full_neuronal` | owner; engineering |
| 14-24 Nov | development runs of the registered configuration on v5: five grouped folds, seed 0, baselines, permuted-label control; module health read per runbook step 0 | engineering |
| 24 Nov-5 Dec | readings for the dopamine axis and the worked disorder; mechanism cards; Fable pass on the routes against the literature | research on Fable |
| 5-19 Dec | seeds 1-2 for stability; IMPC hyperactivity table; repurposing hit list with its checks | engineering, then Fable |
| 19 Dec-9 Jan | write-up, figures redrawn on v5 (`docs/figures.md`), study-sheet diagrams re-stamped, buffer for one more development iteration | owner, session |

---

## 5. Owner decisions each framing needs

- **9.112** (rule the option; every framing). **9.113, 9.114** (rule or defer with disclosure; needed for any
  claim about calcium or ion-regulated enzymes; 2.4's channelopathy variant cannot proceed without them).
- **9.106 (a)**: whether 20 October readings are history; affects what may be cited, not what is run.
- **Q1 (new)**: that development-level grouped readings on v5, made before the confirmatory draw and on a declared
  development hold-out (the trainer's grouping or an item-25 pseudo-draw), are permitted and are not the draw of 1.1;
  and which hold-out instrument to use for the D2 class.
- **Q2 (new)**: which disorder is the worked case (HMBS, ATP7B, GCH1 or another).
- **Q3 (new)**: whether a prolactin construct is added for the positive control (an amendment), or the control stays
  on the extrapyramidal constructs.
- **9.64**: only if nosology (2.2) is pursued.
- **9.48 / 9.60 (narrow)**: only for 2.3, whether trial-outcome relief comparisons may inform a development relieves
  reading.
- **Untouched**: 1.1, 1.2, 9.35, 9.111's pin; they gate the draw, which nothing here proposes.

## 6. Sources read

`CLAUDE.md`; `docs/status.md` (generated 7 November 2026 at `37d9537-dirty`); `docs/evidence_reports_spec.md`;
`docs/confirmatory_runbook.md`; `docs/clinical_trial_outcome_evidence.md`; `docs/data_sources.md` (rows 1-56);
`docs/research_summary.md` (sections 1-3, 5, 6); `docs/nosology_discovery_options.md`; `docs/onsides_label_slice.md`;
`docs/impc_knockout_evidence.md`; `docs/mouse_sources_measured_v5.md` (sections 1-3); `docs/exploration_queue.md`
(priority order); `docs/open_decisions.md` rows 1.1, 1.2, 9.35, 9.35b, 9.48, 9.64, 9.92, 9.106, 9.112-9.114;
`configs/registered_rules.json`; `data/processed/evidence_full_v5/evidence_summary.json` and
`evidence_records.parquet`; `data/processed/label_selection/better_v2_full_v5.parquet` and its summary;
`faers_v5`, `impc_v5`, `clinical_trials_v5` summaries; `experiments/run_main_model.py` (split and lockbox arguments);
`mechanistic_pathway_learning/evaluation/mechanism_cards.py`; the removed record at `c4d77af` read from git as history
of the built state only.