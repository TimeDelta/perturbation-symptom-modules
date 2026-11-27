# Draft amendment item 41: the fine symptom list (for the owner; not registered)

**Status.** DRAFT, written 27 November 2026 for the owner to read, and committed to `docs/drafts/` the same day
at the owner's request ("Just merge and push everything. I'll review it later"), before the owner had read it.
Nothing here is registered: `docs/preregistration.md` is unchanged and no `Amends:` trailer has been written. Under the
rule of 13 November 2026 ("don't automatically push to origin unless you're sure you actually understood me"), this
draft rests on my reading of the owner's rulings in several places, so registering it waits for the owner to confirm
those readings.

**What it was written from.** `main` at commit `342c8b8` (HEAD equal to `origin/main`; not fetched). I read rows
9.58, 9.61 and 9.152 of `docs/open_decisions.md` in full, and also the rows that changed the fine list after 9.58:
9.74, 9.96, 9.115 and 9.116. I also read `docs/preregistration.md` (its opening, the symptom block of 7 October 2026,
item 1, the "What is still open" block and items 33 to 40), `configs/registered_rules.json`,
`docs/symptom_crosswalk.csv`, `docs/symptom_crosswalk_fine.csv`, the four inputs of the fine builder in `configs/`,
`configs/impc_symptom_crosswalk_fine.csv`, `docs/generated/fine_symptom_constructs.md`,
`mechanistic_pathway_learning/evidence/symptom_constructs.py`, `experiments/build_fine_symptom_crosswalk.py`,
`experiments/score_confirmatory.py` and `configs/study_sheet_diagrams.json`. I also ran `git grep` for every reader
of the two crosswalks. No external source was read. I ran
`PYTHONPATH=. python experiments/build_fine_symptom_crosswalk.py --check` on 27 November 2026 against
`data/raw/hpo/hp.obo`. It printed "docs/symptom_crosswalk_fine.csv is current" and wrote nothing. The working log is
`docs/drafts/amendment_fine_symptom_list_draft.progress.md`.

**How the readings are marked.** A ruling quoted from a row is in quotation marks, with its row. Where I had to read
the owner's intent rather than quote it, the text carries **[Reading Rn]**. Each reading is explained, with what
the owner would need to confirm, in the section "The readings" after the item.

**Item number.** 41, provisionally: decision 9.154 (recorded 27 November 2026) may also become an amendment item, and
the number goes to whichever is registered first. `docs/preregistration.md` holds no item 41. Its last item is 40, registered in commit `d2e746d`.
No commit on any local or remote-tracking ref names an item 41.

---

## The item as it would be added to `docs/preregistration.md`

Amendment, [date of registration], written before any lockbox run and before the held-out set has been drawn
(decision 1.1 is open).

**41. The registered symptom list is the fine construct list of `docs/symptom_crosswalk_fine.csv`: 42 constructs
derived from the 24 registered coarse constructs and four additions, one per HPO root and named by it, with
merging left to the model as an output and not an input (decision 9.58, with the crosswalk as decisions 9.74, 9.115,
9.116 and 9.152 left it)** (the owner, 16 October 2026: "Intellectual disability should be separate from cognitive
impairment, preferably with the ability for them to merge based on the data because I don't want to risk inheriting
the existing nosology ... the whole point of this project is creating the basis for a new psych nosology" and "Do it.
Finely grained symptoms is the goal"). Decision 9.58 holds the ruling and is the authority for this item. It recorded
the item as owed "before v0.5: the amendment of the registered symptom list (no item of `docs/preregistration.md`
registers the fine list yet)". Each later change to the list is held by its own decision, cited where it applies.
**[Reading R1, R2]**

**a. Why.** Until this item, the registration named the coarse list. Its opening freezes "symptom set and HPO term
exclusions (docs/symptom_crosswalk.csv ...)". The amendment of 7 October 2026 set the list's frame and its
additions. Item 1 registered "parkinsonism as the 24th symptom". That list fuses several HPO roots into one
construct in seven rows. In 9.58's words: "psychosis: psychosis, hallucinations, delusion, paranoia;
irritability_or_aggression; psychomotor_agitation: agitation, restlessness; apathy: apathy, abulia; suicidality:
ideation, behaviours; increased_appetite: polyphagia, bulimia; parkinsonism: six roots". Intellectual disability
(HP:0001249) reached no construct, because it is a sibling of HP:0100543 and not a descendant of it. A fused row
decides a merge before the model sees the data, which is the inherited nosology the owner ruled against. The v5
tables are built on the fine crosswalk (`scripts/rebuild_data_layer.sh fine`). The scorer reads its symptom list
from the data and refuses a run "trained on another symptom list" (`experiments/score_confirmatory.py`). So the list
the confirmatory test would score is the fine list, and the registration has to name it. Decisions 9.74 and 9.115 (h)
each treated a single fine-level addition as "a decision and a dated note", not an amendment, because the
registration then named only the coarse constructs. This item is the amendment those additions were waiting on.
**[Reading R5]**

**b. The rule that makes the list.** `experiments/build_fine_symptom_crosswalk.py`
(`mechanistic_pathway_learning/evidence/symptom_constructs.py`) derives the fine crosswalk from the coarse one. It
does not author the list.
(1) A coarse construct with several HPO roots is split at those roots into one fine construct per root, named by the
root's HPO name. A construct with one root keeps its coarse name. A parent root excludes any sibling root that
descends from it.
(2) The coarse row's MedDRA preferred terms are shared out in this order: a row of
`configs/fine_construct_term_overrides.csv`; then the HPO vocabulary of the construct (the names and synonyms of its
root and kept descendants); then shared word stems with the root's name; then the coarse row's namesake. A MeSH
descriptor and the questionnaire item stay with the namesake unless an override names the descriptor by its
D-number. Every assignment is listed in `docs/generated/fine_symptom_constructs.md`. On 24 November 2026 it gave
hpo vocabulary 17, stem match 9, override 5, namesake 4 and single construct 60.
(3) The mouse crosswalk is re-keyed the same way (`configs/impc_symptom_crosswalk_fine.csv`). A fine construct that
receives no proxy from its coarse row takes validity "none", "because a proxy stated for a coarse construct was not
stated for its parts".
(4) The build is checked against the committed files: `--check` passes, and `tests/test_symptom_constructs.py`
asserts that the committed crosswalk is a fresh build of its inputs.

The exceptions to one construct per root, each ruled by its own decision:
- **A root added below a coarse root, for the fine level only** (`configs/fine_construct_extra_roots.csv`):
  akathisia, HP:0031943, split out of restlessness. Decision 9.74, the owner, 19 October 2026: "I think
  physiologically, it should be split out". The coarse construct's coverage is unchanged, and a test checks this on
  hp.obo.
- **Roots kept together as one construct** (`configs/fine_construct_kept_together.csv`): abnormal_dreams, holding
  HP:5200287 Recurrent distressing nightmares and HP:0032938 Recurrent trauma-related distressing dreams. Decision
  9.152 (1): "Include the latest release of hpo to get nightmares", "3 why not map to nightmares?", and, offered the
  exception, the split with an empty construct or dropping the second term: "1 I meant a". The reason recorded is
  that "the symptom is the dream phenomenon whatever its cause".
- **Constructs added that no coarse row holds** (`configs/symptom_construct_additions.csv`): intellectual_disability,
  HP:0001249 (decision 9.58, quoted in the heading); tardive_dyskinesia, HP:0040141 (decision 9.115, Q1: "Yes");
  orofacial_dyskinesia, HP:0002310, and extrapyramidal_dyskinesia, HP:0007308 (decision 9.116: "Sure. As long as they
  pass all the other checks"). The checks of 9.116 were run on hp/releases/2026-09-01 on 7 November 2026.
- **Placements the owner ruled on, 24 November 2026** (decision 9.152):
  - (2) MedDRA "Agitation" belongs to agitation alone: "2 accepted". It is removed from irritability_or_aggression, and
    a test fails when any MedDRA term sits under two rows.
  - (3) MeSH D000374 Aggression goes to aggressive_behavior: "Shouldn't mesh aggression go to aggressive behavior fine
    constructs?". Irritable Mood D007508 stays with irritability.
  - (4) HP:0031843 Abnormally slow thought process becomes psychomotor_retardation's HPO root: "4 add it".
  - (5) MP:0005655 increased aggression goes to aggressive_behavior: "Yes".
  - (6) SFARI's Aggression entity goes to aggressive_behavior in `configs/sfari_symptom_crosswalk.csv`: "move the
    second mouse source".
- **Placements made by the building session on 16 October 2026 and registered as built**: the MedDRA overrides
  Hostility and Anger (to aggressive_behavior), Extrapyramidal disorder (to parkinsonism), and Hypokinesia and
  Akinesia (to bradykinesia). The owner has not ruled on them one by one. Decision 9.116 says the Extrapyramidal
  disorder override "is the owner's if it is to move". **[Reading R4]**

**c. The list.** The 42 constructs of `docs/symptom_crosswalk_fine.csv` as last changed in commit `72dcf89` (24
November 2026). The counts are read from the files on 27 November 2026. "MedDRA" is the number of MedDRA preferred
terms that give the construct its drug-label positives. "MeSH" is the number of MeSH descriptors that give it
literature. "Mouse" is the best validity of its rows in `configs/impc_symptom_crosswalk_fine.csv`.

| # | fine construct | coarse construct | HPO root(s) | MedDRA | MeSH | RDoC domain | mouse | from |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `depressed_mood` | `depressed_mood` | HP:0000716 | 6 | 3 | negative_valence | none | 9.58 (coarse row kept) |
| 2 | `anhedonia` | `anhedonia` | HP:0012154 | 1 | 1 | positive_valence | none | 9.58 (coarse row kept) |
| 3 | `anxiety` | `anxiety` | HP:0000739 | 7 | 2 | negative_valence | moderate | 9.58 (coarse row kept) |
| 4 | `irritability` | `irritability_or_aggression` | HP:0000737 | 1 | 1 | negative_valence; arousal | none | 9.58 (split) |
| 5 | `aggressive_behavior` | `irritability_or_aggression` | HP:0000718 | 3 | 1 | negative_valence; arousal | moderate | 9.58 (split); 9.152 (3), (5), (6) |
| 6 | `insomnia` | `insomnia` | HP:0100785 | 5 | 1 | arousal_regulatory | moderate | 9.58 (coarse row kept) |
| 7 | `somnolence_or_hypersomnia` | `somnolence_or_hypersomnia` | HP:0001262 | 4 | 2 | arousal_regulatory | moderate | 9.58 (coarse row kept) |
| 8 | `fatigue` | `fatigue` | HP:0012378 | 2 | 2 | arousal_regulatory | none | 9.58 (coarse row kept) |
| 9 | `agitation` | `psychomotor_agitation` | HP:0000713 | 2 | 1 | arousal | none | 9.58 (split); 9.152 (2) |
| 10 | `restlessness` | `psychomotor_agitation` | HP:0000711 | 1 | 0 | arousal | none | 9.58 (split) |
| 11 | `akathisia` | `psychomotor_agitation` | HP:0031943 | 1 | 0 | sensorimotor | none | 9.74 (root added below restlessness) |
| 12 | `psychomotor_retardation` | `psychomotor_retardation` | HP:0031843 | 2 | 0 | arousal | moderate | 9.58 (coarse row kept); root 9.152 (4) |
| 13 | `psychosis` | `psychosis` | HP:0000709 | 3 | 3 | cognitive_systems; perception | endophenotype_only | 9.58 (split) |
| 14 | `hallucinations` | `psychosis` | HP:0000738 | 4 | 0 | cognitive_systems; perception | none | 9.58 (split) |
| 15 | `delusion` | `psychosis` | HP:0000746 | 1 | 0 | cognitive_systems; perception | none | 9.58 (split) |
| 16 | `paranoia` | `psychosis` | HP:0011999 | 1 | 0 | cognitive_systems; perception | none | 9.58 (split) |
| 17 | `cognitive_impairment` | `cognitive_impairment` | HP:0100543 | 9 | 4 | cognitive_systems | moderate | 9.58 (coarse row kept) |
| 18 | `elevated_mood_or_mania` | `elevated_mood_or_mania` | HP:0100754 | 4 | 2 | positive_valence; arousal | none | 9.58 (coarse row kept) |
| 19 | `apathy` | `apathy` | HP:0000741 | 1 | 0 | positive_valence | none | 9.58 (split) |
| 20 | `abulia` | `apathy` | HP:0012671 | 0 | 0 | positive_valence | none | 9.58 (split) |
| 21 | `suicidal_ideation` | `suicidality` | HP:0031589 | 2 | 0 | negative_valence | none | 9.58 (split) |
| 22 | `suicide_behaviors` | `suicidality` | HP:5200330 | 3 | 0 | negative_valence | none | 9.58 (split) |
| 23 | `self_injury` | `self_injury` | HP:0100716 | 3 | 0 | negative_valence; cognitive_systems | none | 9.58 (coarse row kept) |
| 24 | `compulsive_behavior` | `compulsive_behavior` | HP:0000722 | 3 | 0 | cognitive_systems | weak | 9.58 (coarse row kept) |
| 25 | `disinhibition_or_impulsivity` | `disinhibition_or_impulsivity` | HP:0000734 | 7 | 0 | cognitive_systems; positive_valence | none | 9.58 (coarse row kept) |
| 26 | `hyperactivity` | `hyperactivity` | HP:0000752 | 0 | 0 | arousal | strong | 9.58 (coarse row kept) |
| 27 | `emotional_lability` | `emotional_lability` | HP:0000712 | 2 | 0 | negative_valence | none | 9.58 (coarse row kept) |
| 28 | `polyphagia` | `increased_appetite` | HP:0002591 | 2 | 0 | arousal_regulatory | strong | 9.58 (split) |
| 29 | `bulimia` | `increased_appetite` | HP:0100739 | 1 | 0 | arousal_regulatory | none | 9.58 (split) |
| 30 | `abnormal_dreams` | `abnormal_dreams` | HP:5200287; HP:0032938 | 2 | 0 | arousal_regulatory | none | 9.58 (coarse row kept); roots kept together 9.152 (1) |
| 31 | `decreased_libido` | `decreased_libido` | HP:0046504 | 2 | 0 | positive_valence | none | 9.58 (coarse row kept) |
| 32 | `catatonia` | `catatonia` | (none) | 1 | 0 | arousal; sensorimotor | none | 9.58 (coarse row kept) |
| 33 | `parkinsonism` | `parkinsonism` | HP:0001300 | 4 | 0 | sensorimotor | none | 9.58 (split) |
| 34 | `bradykinesia` | `parkinsonism` | HP:0002067 | 3 | 0 | sensorimotor | none | 9.58 (split) |
| 35 | `resting_tremor` | `parkinsonism` | HP:0002322 | 1 | 0 | sensorimotor | weak | 9.58 (split) |
| 36 | `pill_rolling_tremor` | `parkinsonism` | HP:0025387 | 0 | 0 | sensorimotor | none | 9.58 (split) |
| 37 | `cogwheel_rigidity` | `parkinsonism` | HP:0002396 | 1 | 0 | sensorimotor | none | 9.58 (split) |
| 38 | `extrapyramidal_muscular_rigidity` | `parkinsonism` | HP:0007076 | 0 | 0 | sensorimotor | none | 9.58 (split) |
| 39 | `intellectual_disability` | `intellectual_disability` | HP:0001249 | 1 | 1 | cognitive_systems | none | 9.58 (addition) |
| 40 | `tardive_dyskinesia` | `tardive_dyskinesia` | HP:0040141 | 1 | 1 | sensorimotor | none | 9.115 (addition) |
| 41 | `orofacial_dyskinesia` | `orofacial_dyskinesia` | HP:0002310 | 0 | 0 | sensorimotor | none | 9.116 (addition) |
| 42 | `extrapyramidal_dyskinesia` | `extrapyramidal_dyskinesia` | HP:0007308 | 0 | 0 | sensorimotor | none | 9.116 (addition) |

**The counts.**
- 42 constructs from 28 coarse rows: the 24 registered rows and the four rows of
  `configs/symptom_construct_additions.csv`. That is 38 at 9.58's build of 16 October 2026, 39 with akathisia
  (9.74), 40 with tardive dyskinesia (9.115) and 42 with the two dyskinesias (9.116).
- Seven coarse rows are split into 20 constructs: parkinsonism 6, psychosis 4, psychomotor_agitation 3 (two roots
  and the root added by 9.74), and irritability_or_aggression, apathy, suicidality and increased_appetite 2 each.
  Seventeen coarse rows keep their name as a single construct.
- 42 HPO roots in all. 40 constructs have one root, abnormal_dreams has two, and catatonia has none: it has no HPO
  term, so it has no gene label from HPO.
- 97 MedDRA preferred terms, none under two constructs (the coarse rows hold 95; the additions bring "Mental
  retardation" and "Tardive dyskinesia"). Six constructs have no MedDRA preferred term and so no drug-label
  positive: abulia, hyperactivity, pill_rolling_tremor, extrapyramidal_muscular_rigidity, orofacial_dyskinesia and
  extrapyramidal_dyskinesia.
- 25 MeSH descriptors on 14 constructs.
- 17 constructs carry a questionnaire item.
- 11 constructs have a mouse proxy of a validity other than "none".
- RDoC domains, counted once per construct per domain: sensorimotor 11, cognitive_systems 9, negative_valence 8,
  arousal 8, positive_valence 6, arousal_regulatory 6, perception 4.

**What the list holds in labels is not measured on this list.** No evidence table has been built on the 42-construct
crosswalk. The fine rebuild that 9.115, 9.116 and 9.152 put the changes into is outstanding, and no evidence table
is on the machine this draft was written on. The last per-construct measurements are history, on an earlier list:
on the v5 tables of 16 October 2026 (38 constructs), 8,059 label pairs, of which intellectual disability held 1,620,
"twice cognitive impairment's 756" (9.61). On the same tables, 9.74 measured akathisia at 62 pairs and restlessness
at 75 before its split was built. On `evidence_full_v5`, before its row, 9.115 measured tardive dyskinesia at 0 gene
pairs and 43 drug label pairs. These are not evidence about the table the list will be scored on. The counts on that
table are reported with its build directory and date when it is rebuilt.

**d. The coarse crosswalk changed on 24 November 2026, and this item states the change.** The opening of this
document freezes the coarse crosswalk's "symptom set and HPO term exclusions". Three commits of 24 November 2026
(`c7f3151`, `8dab64b`, `72dcf89`) changed `docs/symptom_crosswalk.csv` itself under decision 9.152:
- abnormal_dreams gained its first HPO roots, HP:5200287 and HP:0032938, and its status moved from `no_hpo_term` to
  verified;
- psychomotor_retardation gained HP:0031843, also moving from `no_hpo_term`;
- MedDRA "Agitation" left irritability_or_aggression.
No commit message of the three names the registration. The set of coarse constructs is unchanged at 24. What changed
is their HPO roots and one MedDRA term. 9.152 records the effect on labels. Neither dream term carries a gene
annotation in HPO v2026-09-01. All 487 SIDER Agitation events already went to agitation. HP:0031843 brings 7 genes
in v2026-09-01 (CLTC, DMPK, HTT, NOTCH3, PRNP, SLC2A3, VPS13A), with the limit 9.152 states: "the term covers
slowed thought only and HPO has no term for slowed movement, so these gene labels cover half of the construct".
**[Reading R3]**

**e. What scoring does with the list, unchanged.** Each fine construct is a symptom for every registered rule. A
construct enters the macro average with at least five positives and one negative (`minimum_positives_to_score` in
`configs/registered_rules.json`, unchanged). The macro average takes the constructs with at least five positives in
the held-out set, fixed in the lockbox file. The micro average takes every scored construct. Which constructs are
scored is a count on the rebuilt table and is not registered here. The constructs with no MedDRA term, or with no
HPO root, may fall below the minimum. The rule handles that without a decision, as 9.116 noted. No coarse construct
is scored in the confirmatory test: a merge of fine constructs is read from the fitted model (9.58: "the
module-to-symptom structure of the head is where a data-driven merge would show"), not scored as a label. Item 38
(g) builds a construct's query from its row of `docs/symptom_crosswalk_fine.csv`, "(`docs/symptom_crosswalk.csv`
where a coarse construct is scored)". Under this item that parenthesis has nothing to apply to. **[Reading R6]**

**f. What this item supersedes in the earlier text, which is kept as the record.**
- The opening line's frozen "symptom set ... (docs/symptom_crosswalk.csv ...)". The scored list is now the fine list
  of (c). The coarse crosswalk stays registered as the source the fine list is derived from, with its HPO term
  exclusions, which the fine constructs inherit. **[Reading R1]**
- The 7 October 2026 "Not added" bullet, for intellectual disability alone ("intellectual disability and speech
  delay (developmental, not a symptom state)"). Speech delay and the bullet's other exclusions stand until decision
  9.96's candidate pool is built. **[Reading R8]**
- The 7 October 2026 "Frame" (a symptom of a standard instrument with an HPO or MedDRA term). The frame governs how
  the coarse list was chosen. The fine list follows the rule of (b) and the additions ruled by their decisions.
  **[Reading R7]**
- Item 1's "parkinsonism as the 24th symptom" stands as the record of the coarse list. Parkinsonism's six fine
  constructs replace it in what is scored.
- The closing "To fill in" entry "final symptom set after go/no-go" is filled in part. The list is registered here.
  The scored subset is fixed by the rebuilt table's counts under `minimum_positives_to_score`, and the list may be
  changed by decisions 9.61 and 9.96. **[Reading R11]**

**g. What stays open, and is deliberately not registered here.**
- **The intellectual disability scale, decision 9.61**, which is the owner's: options (a) to (d). This item
  registers intellectual_disability as a construct of the list. It does not choose between (a) keeping all 734 genes
  whose only label it is, (b) admitting only genes with a second, state-construct label, (c) weighting its loss share
  to a median construct's, or (d) holding it out of training and reading it as a held-out construct. Option (d) would
  change it from a trained and scored construct into a read-only one, so the scored list waits on 9.61 for this one
  construct. 9.61's scientific question stands as it was written: intellectual disability "is a developmental trait
  present from early life, while the other constructs are states". **[Reading R9]**
- **The data-defined bound of the symptom set, decision 9.96**, open as the owner's (a) to (d). It was ruled that
  "it has to be data-defined. that's the only acceptable way" and that the candidate pool is every symptom term of
  every label source ("Good suggestion. Use it"). The pool is not built ("Not started: this row is the record
  only"). This item registers the list as it is built today. A list drawn from 9.96's pool would be registered by a
  later amendment. **[Reading R10]**
- **The literature cache rebuilt per construct**, owed by 9.58. The literature table is keyed to the namesake
  constructs, so hallucinations, delusion and paranoia "carry no literature until the raw literature cache is
  rebuilt with per-construct MeSH descriptors".
- **The fine rebuild** (`scripts/rebuild_data_layer.sh fine`) that puts the changes of 9.115, 9.116 and 9.152 into
  the v5 evidence, and the per-construct counts measured on it.
- **The MeSH descriptor of intellectual_disability**, D008607, which its row records as "MeSH unverified", awaiting
  `experiments/verify_mesh_symptom_descriptors.py`.
- **The Extrapyramidal disorder override** (to parkinsonism), which 9.116 left as the owner's if it is to move.
- **The minimum assessment ages** of the constructs added since 9.92 (`configs/symptom_minimum_assessment_age.csv`),
  marked the owner's to confirm under 9.92 in rows 9.115 and 9.116.
- **The v5 lockbox** (decision 9.53, "v5 needs a new lockbox anyway", as 9.61 puts it) and the draw (decision 1.1).
- **Where the crosswalks live.** `configs/moved_paths.json` plans to move both crosswalks to `configs/` in its phase
  3. This item names them by their present paths, and the move would update them here.

**What this item changes in the registration, and what it does not.** It registers the symptom list the
confirmatory test scores, the rule that derives it and the exceptions each decision ruled. It also states the change
of 24 November 2026 to the coarse crosswalk the registration had frozen.

It changes no registered rule. `configs/registered_rules.json` holds thirteen rules: `floor_rule`, `alpha_one_sided`,
`tested_models`, `robustness_models`, `held_out_fraction`, `bootstrap_unit`, `num_bootstrap`,
`minimum_positives_to_score`, `normalisation`, `validation_fold_rule`, `label_likelihood`,
`membrane_potential_build` and `module_support_minimum_reach`. None of them lists the constructs or names a
crosswalk, so the commit that registers this item carries no `Amends:` trailer. This was checked on 27 November 2026
rather than assumed.

It changes no hypothesis, model, baseline, split, threshold or level, and no code. The crosswalk, its builder and
its tests are already built, and items 25, 33, 34, 38 and 39 stand word for word. It is outcome-blind: no held-out
set has been drawn, decision 1.1 being open, so no confirmatory result existed to see. **[Reading R12]**

---

## The readings, for the owner to confirm

- **R1. What "the registered symptom list" is, and what amending it does.** 9.58 says only "the registered symptom
  list is amended before v0.5". I read the list as the one the registration's opening freezes, extended on 7 October
  2026 and by item 1. I read "amended" as: the fine list replaces the coarse list as the list scored, and the coarse
  crosswalk stays registered as the source the fine list is derived from. The alternative is to register both levels
  side by side, with the coarse list scored as a secondary reading. Nothing in 9.58 asks for that, and "merging is an
  output of the model, not an input" argues against it.
- **R2. The list "as the rulings left it" is today's 42, not 9.58's 38.** The draft registers the crosswalk as it
  stands on `main` (last changed `72dcf89`). That includes 9.74, 9.115, 9.116 and 9.152, each cited for what it
  changed.
- **R3. The 24 November changes to the coarse crosswalk.** The owner ruled each change (9.152 (1), (2), (4)). I found
  no record that they were asked whether the changes amend the frozen coarse set. The draft states the changes in
  the registration rather than leaving the frozen set silently changed. If the owner prefers, (d) can instead become
  its own dated note.
- **R4. The five overrides of 16 October 2026.** They were the building session's. 9.58 records them as built ("5 by
  override"), with every assignment listed so the owner can move any. The draft registers them as built and says so.
  It does not present them as rulings.
- **R5. What this does to later fine-level additions.** 9.74's correction and 9.115 (h) (Q11, "Yes. Please do so")
  held that a fine-level addition is "a decision and a dated note, ... not an amendment", because the registration
  named only the coarse list. Once this item registers the fine list, an addition changes a registered list. So from
  then on it would need its own amendment item. This reverses the practice of 9.74 and 9.115 for additions made after
  this item. One more point: as far as `grep` shows, no dated note for 9.115 was ever added to
  `docs/preregistration.md`. This item covers that addition, but the owner should say whether "Please do so" asked
  for a note that is still owed.
- **R6. No coarse construct is scored.** This is read from "merging is an output of the model, not an input" and from
  9.58's "the module-to-symptom structure of the head is where a data-driven merge would show". If so, item 38 (g)'s
  "where a coarse construct is scored" has nothing to apply to. The draft does not edit item 38. It says so here.
- **R7. The instrument frame of 7 October 2026 applies to the coarse list only.** The fine constructs were admitted
  by 9.58's rule and by the decisions of 9.115 and 9.116, not by the frame.
- **R8. "Not added: intellectual disability" is superseded for intellectual disability alone.** Its other exclusions
  (speech delay, tics, decreased appetite and the rest) stand until 9.96's pool is built.
- **R9. 9.61 does not block registration.** The draft registers intellectual_disability as a construct and leaves
  its treatment in training and scoring to 9.61. This follows the brief and 9.58's "the ID scale is 9.61". The owner
  may prefer to rule 9.61 first, because option (d) changes what is scored.
- **R10. 9.96 does not block registration.** 9.96 makes the bound data-defined, but nothing of it is built. The draft
  registers the built list and expects a later amendment when the pool is built. The owner may instead want the item
  to say outright that the list is provisional until 9.96 is built.
- **R11. The closing "To fill in" entry.** "final symptom set after go/no-go" is the skeleton's wording. I read this
  item as filling it in part: the list is registered, and the scored subset follows from the counts.
- **R12. Registering before the fine rebuild.** 9.58 lists "the evidence tables are rebuilt and the registered
  symptom list is amended before v0.5" without an order. The draft can be registered before the rebuild, because it
  fixes the list and the rule and not any count. Registered before the counts exist, it is also blind to them.

## For the commit that registers it (once the readings are confirmed)

- It is a commit that acts on the session's reading of the owner. Under the rule of 13 November 2026 it is shown to
  the owner and pushed only after they confirm.
- The status cell of 9.58 ("owed by a session before v0.5: the amendment of the registered symptom list ...") needs a
  uniquely anchored replacement, not a rewrite of the row, saying the amendment is registered as item 41. The
  literature cache stays owed.
- The generators under "Documents" in `CLAUDE.md`, run in a second commit after the change to
  `docs/open_decisions.md`, then `pytest tests/test_documentation_process.py -q` and the full suite.
- Study sheet: no diagram or passage in `configs/study_sheet_diagrams.json` declares 9.58, 9.61, 9.74, 9.96, 9.115,
  9.116, 9.152 or a crosswalk file, so the guard names none. The diagram "From perturbation to symptom score in seven
  stages" (`d282955a-f81a`) should still be read once, in case it states a symptom count.
- **An option not drafted, for the owner:** the list's identity could become a fourteenth registered rule (for
  example `symptom_constructs`, the 42 names, asserted by `tests/test_registration_matches_the_code.py` against
  `docs/symptom_crosswalk_fine.csv`). That would make a change to the list fail the suite until it is registered. It
  would need an `Amends:` trailer, and it would flag the diagram above, which declares
  `configs/registered_rules.json`. The draft does not take this option, because no ruling asks for it.
