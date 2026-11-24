# Open Targets target-safety statements mapped to fine constructs by curated wording (proposal, 24 November 2026)

Research pass on Fable (claude-fable-5-2), no fallback. Worktree `.claude/worktrees/ot-fine-map` at origin/main 468ccb7;
nothing in the repository was edited, committed or pushed. This is a proposal for decision 8.5 under the owner's ruling
of 24 November 2026 ("Map statements by curated wording to fine constructs"); it decides nothing beyond the mapping.

Files: `ot_fine_construct_map_2026-11-24.csv` (one row per statement), `ot_fine_construct_map_2026-11-24.progress.md`,
`ot_work/` (get_statements.py, build_map.py, statements.json, scoped_rows.csv, MeSH index), `ot_raw/` (the two
curation files), `pages/` (saved MeSH records with address, time, SHA-256).

## 1. The statements

- `adverse_effects.tsv` and `secondary_pharmacology.json` fetched from raw.githubusercontent.com/opentargets/curation at
  commit 1ddf04e7c998bf599746777a3c022b97e1c6888f; SHA-256 4dc79e2e...1615 and 4a6dcf6b...1844, both equal to the
  digests in `scripts/fetch_raw_sources.sh`.
- `experiments/scope_open_targets_symptom_labels.py` has no option that skips the graph (it reads `nodes.parquet` for
  one count), so its selection was reproduced by importing it unchanged: `mapped_rows`, keep `row_class == "positive"`,
  then `human_worded_statements`. 430 positive rows, **111 statements**, the count
  `docs/generated/open_targets_reliability_effect.json` records.
- By coarse symptom: cognitive_impairment 31, insomnia 18, psychosis 14, somnolence_or_hypersomnia 9, anxiety 9,
  depressed_mood 8, psychomotor_agitation 7, irritability_or_aggression 6, fatigue 3, elevated_mood_or_mania 2,
  parkinsonism 2, suicidality 1, abnormal_dreams 1.
- The curated wording was read as it stands in the curation; the three reviews behind it (Lynch 2017, Bowes 2012,
  Urban 2012) were not opened.

## 2. Sources

1. First: the crosswalk's own terms, `docs/symptom_crosswalk_fine.csv` at 468ccb7 (HPO ids, MedDRA terms, notes,
   exclusions).
2. HPO definitions, synonyms and is_a, `data/raw/hpo/hp.obo` of the main checkout, data-version hp/releases/2026-09-01.
   The crosswalk's roots come from HPO, so HPO is independent of the crosswalk for definitions and placement of terms
   the crosswalk does not list, and not for the roots themselves.
3. MeSH scope notes and concepts, read 24 November 2026 from id.nlm.nih.gov/mesh/<id>.json with
   `experiments/read_public_page.py` (saved in `pages/`).
4. MedDRA lower-level-term to preferred-term pairs as they occur in SIDER 4.1 `meddra_all_se.tsv.gz` (the only public
   MedDRA hierarchy on disk; it gives LLT-to-PT and nothing above PT).
5. SNOMED CT International through the connector, 24 November 2026, for two terms.

Refusal recorded: `id.nlm.nih.gov/mesh/sparql` is disallowed by the site's robots file; not read, and the single
records were read instead, which robots allows. No page carried text addressed to an AI assistant.

## 3. The mapping by wording (35 distinct wordings)

Quoted definitions are in the progress log, steps 4 to 8; each CSV row carries its own reason, sources and disagreement.

| Coarse symptom | Wording | Fine construct | Basis |
|---|---|---|---|
| cognitive_impairment | cognitive deficit; decreased memory; memory impairment; potential memory impairments; decreased cognitive function; disruption of cognitive functions such as learning and memory; confusion; anterograde amnesia; delirium and disoriented behaviour | cognitive_impairment | wording |
| insomnia | insomnia | insomnia | wording |
| insomnia | decreased sleep; sleep disturbances | insomnia | namesake_too_vague |
| psychosis | psychosis; psychosis (schizophrenia-like) | psychosis | wording |
| psychosis | hallucinations; interaction with dopaminergic transmission and hallucination | hallucinations | wording |
| psychosis | schizophrenia (one row, inside HTR2A activation) | none for that row | - |
| somnolence_or_hypersomnia | sedation; drowsiness | somnolence_or_hypersomnia | wording |
| anxiety | anxiety; increased anxiety; potentially anxiogenic; increase in anxiety-related effects | anxiety | wording |
| depressed_mood | depression; dysphoria | depressed_mood | wording |
| fatigue | fatigue | fatigue | wording |
| elevated_mood_or_mania | euphoria | elevated_mood_or_mania | wording |
| parkinsonism | parkinsonism; parkinsonian symptoms (tremors) | parkinsonism | wording |
| abnormal_dreams | nightmares | abnormal_dreams | wording |
| psychomotor_agitation | agitation; nervousness (tremors, agitation) | agitation | wording |
| irritability_or_aggression | irritability | irritability | wording |
| irritability_or_aggression | increased aggression | aggressive_behavior | wording |
| suicidality | suicidal intent | suicidal_ideation | wording |

A statement with several rows takes the union of what its rows name; a vague row beside a naming row adds nothing.

## 4. Counts

111 statements, 113 assignments (two statements take two constructs).

| Fine construct | Statements |
|---|---|
| cognitive_impairment | 31 |
| insomnia | 18 (2 by wording, 16 on the namesake as too vague) |
| psychosis | 10 |
| somnolence_or_hypersomnia | 9 |
| anxiety | 9 |
| depressed_mood | 8 |
| agitation | 7 |
| hallucinations | 6 |
| irritability | 4 |
| fatigue | 3 |
| aggressive_behavior | 2 |
| elevated_mood_or_mania | 2 |
| parkinsonism | 2 |
| suicidal_ideation | 1 |
| abnormal_dreams | 1 |

- Of the 97 that joined a namesake before: 4 move off it entirely (psychosis to hallucinations: CNR1, DRD2, OPRK1,
  SIGMAR1 activation), 2 keep it and gain hallucinations (GRIN1, HTR2A activation), 91 are unchanged.
- Of the 14 that joined nothing before: all 14 now join a construct (agitation 7, irritability 4, aggressive_behavior
  2, suicidal_ideation 1).
- Join nothing now: 0 statements. One curated row ("schizophrenia", HTR2A activation, Bowes 2012) names no fine
  construct; its statement is carried by its other rows.
- On the namesake as too vague: 16, all insomnia (15 "decreased sleep", 1 "sleep disturbances", MAOA inhibition).
- No statement was assigned outside its coarse parent. No statement reaches restlessness, akathisia, delusion,
  paranoia, suicide_behaviors, resting_tremor, bradykinesia or intellectual_disability.

## 5. Cases I was unsure of

1. **"suicidal intent" (DRD1 inhibition)** to suicidal_ideation. No crosswalk term says intent, and suicidality has no
   namesake, so the alternative is joining nothing. SNOMED files Suicidal intent (finding) 304594002 under Suicidal
   thoughts; HPO reserves Suicide behaviors for "Suicide attempts or preparations". HPO's own ideation definition does
   not mention intent.
2. **"decreased sleep" (15 statements)** kept on insomnia as too vague, not as wording. HPO has Decreased need for
   sleep (HP:5200276) beside Insomnia. The join is the same either way; only the basis differs.
3. **"parkinsonian symptoms (tremors)" (DRD1 inhibition)**: parkinsonism only. HPO gives "Parkinsonian tremor" as a
   synonym of Resting tremor, which would support adding resting_tremor; the wording does not say rest.
4. **"psychosis" (8 statements)** is called wording, not namesake_too_vague, because the fine construct psychosis has
   its own HPO term. Same join either way.
5. **"schizophrenia" row** treated as naming nothing (diagnosis; HPO puts it outside Psychosis). The alternative is to
   read it as psychosis; HTR2A activation already has a "psychosis" row, so the result does not change.
6. **Cross-parent, reported and not moved:** "nervousness (tremors, agitation)" (ADORA2A inhibition) names nervousness,
   a term of fine anxiety. And MedDRA "Agitation" is listed in the crosswalk under fine irritability as well as fine
   agitation, so all 7 agitation statements match a term of a construct under irritability_or_aggression.
7. **Hedged or loose wording** assigned as it reads: "potentially anxiogenic" (HTR1A inhibition), "increase in
   anxiety-related effects" (NPY1R inhibition), "potential memory impairments" (HTR2A activation).
8. **"increased aggression"** (ADORA2A, HTR1B inhibition): the phrase is also how rodent aggression assays are
   reported; the scoping script classes it as human-worded and that was left alone.

## 6. Disagreements between sources

- Drowsiness: MedDRA files it under PT Somnolence and MeSH under Sleepiness; HPO keeps Drowsiness (HP:0002329) outside
  the crosswalk's root HP:0001262.
- Dysphoria: the crosswalk's MedDRA list puts it in depressed_mood; HPO keeps Dysphoria (HP:0033838) beside
  Depression, not under it.
- Euphoria: crosswalk MedDRA "Euphoric mood"; HPO Euphoria (HP:0031844) is outside Mania (HP:0100754).
- Sleep disturbance: HPO's parent of Insomnia; MedDRA maps it to PT Sleep disorder, not Insomnia.
- Agitation, restlessness, akathisia: MeSH folds all three into Psychomotor Agitation (D011595, second concept
  Akathisia); HPO distinguishes agitation from restlessness by distress and the crosswalk keeps three constructs.
- Aggression: the crosswalk lists MeSH D000374 Aggression under fine irritability and none under aggressive_behavior;
  HPO and MedDRA put aggression in aggressive_behavior.
- Parkinsonian tremor: HPO synonym of Resting tremor; SNOMED child of Tremor with nothing on rest.
- Schizophrenia: the scoping pattern files it under coarse psychosis; HPO and the crosswalk's psychosis terms do not.

## 7. Seen in passing, not acted on

- hp/releases/2026-09-01 holds HP:5200287 Recurrent distressing nightmares, while the crosswalk's abnormal_dreams note
  says "no HPO term for nightmares or abnormal dreams".

## 8. CLAUDE.md

Followed throughout. Three notes: the report was drafted in the progress log and the build script as the work went and
written out as a file at the end, not section by section; the MedDRA hierarchy was read only as SIDER carries it
(LLT to PT), since MedDRA itself is licensed and no public copy of its upper levels was sought; rows whose wording
equals a crosswalk term rest on the crosswalk plus one second source, and the suicidal intent row rests on HPO and
SNOMED with no crosswalk term naming it.
