# Drafts for the owner from the living-document reviews of 27 November 2026

A draft: text for the owner to act on, nothing in it applied. The living-document reviews of 27 November 2026 read
twenty documents against the repository at `eec6e85`, one group of documents to a reviewer and an independent
check of each review. Their factual corrections to the documents they were allowed to edit are on `main` in the
commits of 27 and 28 November 2026 that name these reviews. What each review could not apply is collected here
verbatim: corrections to the owner's own documents (`CLAUDE.md`, `docs/preregistration.md`,
`docs/research_summary.md`), suggestions for the study sheet, which changes only with the owner's approval, steps
proposed for the runbook, and the questions only the owner can answer. Where a group's checker found a draft
wrong, its correction is given beside the draft and the draft is not to be applied as it stands. A change to
`docs/preregistration.md` goes through an amendment with an `Amends:` trailer, and a change to `CLAUDE.md` is
the owner's. Committed on 28 November 2026 at the owner's request of 27 November ("Just merge and push
everything. I'll review it later"), before the owner had read it.

What each group leaves owed to a Fable pass, because it is reading sources, is listed under the group.

## CLAUDE.md, docs/preregistration.md and docs/research_summary.md (the owner's documents; none edited)

### CLAUDE.md

**C1 (Pushing, line 361).**
- **Old:** "Every remote branch other than `main` predates direct pushing; on 25 October 2026 all but `entmax-mixture-weighting` were checked…"
- **Fact (local origin refs):** six remote branches have tips after 24 October 2026:
  - `claude/friendly-allen-q5xf0t` (25 Oct)
  - `wip/not-evidence-27oct` and `wip/not-evidence-era-27oct` (27 Oct; `docs/development_sessions.md:700` calls them safety copies the owner may delete)
  - `recovery/queue-item-27-2026-11-23`
  - `recovery/study-sheet-audit-2026-11-24`
  - `recovery/study-sheet-registry-2026-11-24`
- **Proposed:** "Every remote branch other than `main` that existed on 25 October 2026 predates direct pushing; on 25 October 2026 all but `entmax-mixture-weighting` were checked… The branches pushed since as safety or recovery copies (`wip/not-evidence-27oct`, `wip/not-evidence-era-27oct`, `recovery/queue-item-27-2026-11-23`, `recovery/study-sheet-audit-2026-11-24`, `recovery/study-sheet-registry-2026-11-24`) are not `main`'s state either."
- **Question for the owner:** does "just leave the branches alone" cover the later branches too?

**C2 (Documents, line 312).**
- **Old:** "`pytest tests/test_documentation_process.py -q` (the last two generators were added on 27 October and 2 November 2026; the test fails on a page any of them would write differently)."
- **Proposed (a), true today:** "…; the test fails on a page four of them would write differently; `docs/amendment_history.md` is checked only by `python experiments/generate_amendment_history.py --check`, which no test runs yet)."
- **Proposed (b), true once the test defect above is fixed:** "`pytest tests/test_documentation_process.py tests/test_amendment_history.py -q` (…; together they fail on a page any of them would write differently)."
- **Added 28 November 2026, a note beside the collected text, which is unchanged:** the guards branch landed on `main` on 28 November 2026. Its commit `1976150` on `wave4/guards-and-hook` is `abb0700` on `main` ("Make the amendment-history test run the generator's --check, so a stale page fails"), and `tests/test_amendment_history.py::test_the_generated_file_is_current` now runs `python3 experiments/generate_amendment_history.py --check`. So option (b) is the true wording for `CLAUDE.md` line 312, and option (a), whose "which no test runs yet" no longer holds, is not. `CLAUDE.md` is the owner's and is not edited.

### docs/research_summary.md

**RS-C8 (add under the "## 6." heading, after the 27 October note).** "Added 27 November 2026: this table was the decision log kept by hand from 3 to 13 October 2026, with two later rows (22 and 24 October). Since 12 October 2026 decisions are recorded in `docs/open_decisions.md`, whose chronology `docs/decision_history.md` generates from the git history, and this table receives no new rows. It is kept as the record of the decisions of that period."
- Whether the table is closed, or should be kept up to date again, is the owner's call.

**RS1 (lines 119–121).**
- **Old:** "Added 27 October 2026: every row of this table is a measurement of 3 to 8 October 2026 on the slice or the v0.4 full graph and is history…"
- **Problem:** row 17 was added on 7 Nov 2026. It is a count of 4 Nov on `graph_full_neuronal` (decision 9.112).
- **Proposed:** "Added 27 October 2026: every row this table then held (rows 1 to 16) is a measurement of 3 to 8 October 2026 … No row is edited or renumbered. Added 27 November 2026: row 17, added on 7 November 2026, is a count of 4 November 2026 on `data/processed/graph_full_neuronal` (decision 9.112), outside the period the status paragraph reads that ruling as covering; its graph and date are in the same list."

**RS2 (lines 145–147).**
- **Old:** "…the v5 build the registration names was made on 5 November 2026, before decision 9.112 is built, and the October directories under the v5 names came from a build the owner had not asked for, decision 9.106):"
- **Proposed:** "…the v5 build the registration names was made on 5 November 2026 and rebuilt on 12 November 2026 from `graph_full_neuronal` down (`docs/data_layer_rebuild.md`), both under the registered `computed_from_the_pools`, so 9.112's rebuild is still owed; the October directories under the v5 names came from a build the owner had not asked for, decision 9.106):"

**RS3 (lines 212–214).**
- **Old:** "- Finding 17: `data/processed/graph_full_neuronal` of 4 November 2026 (Reactome release 98), a count of edges and signs, not a trained run. The v5 build of 5 November 2026 carries the same membrane-potential layer, so the finding bears on it until 9.112 is built."
- **Proposed:** "- Finding 17 (added 7 November 2026; measured after the period this list retires, and listed here for its graph): `data/processed/graph_full_neuronal` of 4 November 2026 (Reactome release 98), a count of edges and signs, not a trained run. The v5 build of 5 November 2026 and its rebuild of 12 November 2026 carry the same membrane-potential layer (`computed_from_the_pools`), so the finding bears on both until 9.112 is built."

**RS4 (line 248).** This contradicts lines 53–55, `label_likelihood` `positive_unlabelled` (9.90) and item 34d.
- **Old:** "no: unobserved pairs are unlabelled and sampled at reduced weight (design 5.4)"
- **Proposed:** "no: unobserved pairs are unlabelled; under the registered `label_likelihood` (`positive_unlabelled`, decision 9.90, amendment item 34d) each enters once as an unlabelled pair of a positive-unlabelled likelihood, not as a negative at reduced weight, which is the `--label-likelihood weighted` arm (design 5.4)"

**RS5 (line 250).** Flux sampling was dropped from the confirmation on 8 Oct (the section 6 row of that date).
- **Old:** "the brain has no defensible single objective; sampling is the planned route, with the coverage limits of finding 7"
- **Proposed:** "the brain has no defensible single objective; flux sampling, the route then planned, was dropped from the confirmation on 8 October 2026 (section 6: 14 percent of kept pairs reachable by a Human-GEM knockout, about 0.9 core-hours per knockout, no brain medium) and stays the Aim 3 branch if Aim 2 fails (B4); finding 7's coverage count is a slice-period number"

**RS6 (line 247).** The registered flag list uses `--group-by disease_cluster_and_targets` (`V4_SHARED_MODEL`, `run_main_model_batch.py:81`), and item 25 splits the held-out set by target.
- **Old:** "disease-cluster grouping, drugs grouped by dominant target, permuted-label and rewired-graph controls (design 6.1, 6.3)."
- **Proposed:** "disease-cluster grouping with each drug grouped with the genes it targets (`disease_cluster_and_targets`, the registered flag list of `experiments/run_main_model_batch.py`), the held-out set split on mechanism targets (amendment item 25), permuted-label and rewired-graph controls (design 6.1, 6.3)."
- Note: design 6.1 says "dominant target" too. That is another group's document.

**RS9 (line 227).** `model_pipeline.png` last changed on 17 Oct (`6fc913e`, `cf57d4b`), and `docs/figures.md` says "The drawing of 17 October 2026".
- **Old:** "(docs/figures.md section 1, redrawn 9 October 2026)"
- **Proposed:** "(docs/figures.md section 1, last redrawn 17 October 2026)"

**RS8 (lines 73–75, Aim 2 status).**
- **Old:** "…the held-out set waits for the owner's go-ahead (decision 1.1) and the v4 rebuild and redraw (decision 1.2)."
- **Proposed:** "…the held-out set waits for the owner's go-ahead and the leakage ceiling that now gates the draw (decisions 1.1 and 9.35), the rebuild and redraw of decision 1.2, and the Human-GEM update decision 9.151 orders before the draw (ruled 24 November 2026, not built)."
- **Add after the H1 bullet:** "Added 27 November 2026: amendment item 39 (decision 9.150) adds a rule of the tested model, registered and switched on 24 November 2026 as `module_support_minimum_reach` (value 2): no module holds a node that fewer than two training perturbation sources can reach; the robustness model runs without it. Amendment items 37 (23 November 2026; decision 9.132 holds what it leaves owed) and 40 (24 November 2026, decision 9.153) are registered and their builds are owed; `docs/preregistration.md` states what each changes."

**RS7 (lines 143–144, minor).** `docs/status.md` reports only the graph and table counts. The grade and literature counts come from `data/releases/v0.4/evidence_full/evidence_summary.json` and `.../literature/literature_summary.json`.
- **Old:** "the counts below are that release's and are reported by docs/status.md."
- **Proposed:** "the counts below are that release's (`data/releases/v0.4/MANIFEST.json` and the summaries beside its tables; `docs/status.md` reports the graph and table counts)."

**Optional:** lines 107–108 could note that `forward_cone` was withdrawn by the owner on 20 November and stays registered until 37f's root-finder is built (9.16, item 37f). This is an omission, not an error.

### docs/preregistration.md

**PR1 (item 37, lines 2820–2821; this is the critic's "37-build-state-correction").**
- **Old:** "…which is the authority for what this item registers; nothing of it is built."
- **What the code at `eec6e85` already holds:**
  - **Before registration (20 Nov):**
    - `27fbeb4`: entry nodes excluded from module support. 37m itself says "this is built".
    - `4c9ec11`: the Human-GEM corrections table applied where the model is read (37o).
    - `5410145`: NAAA's other reactions moved to the lysosome (37o).
    - `daeff3b`: levodopa (37m).
    - `bdbe933`: melatonin (37m).
    - `f71a3aa`: conflicting ChEMBL action types flagged for curation (37h).
  - **After registration, `2c3696d` (27 Nov):**
    - 37a (iii) and (v): the CHRND/E/G, CHRNA1, TRPC4AP and TRPV5/6 removals, applied under every build at the next rebuild.
    - 37d: the 1.23 and 0.92 ratios, read only by `pores_and_clamped_pools`.
  - No built graph carries any of this; the last build was 12 November.
- **Proposed, added after that sentence:** "Added 27 November 2026, as a record of what is coded: no built graph carries any part of this item (the last build is that of 12 November 2026), but parts are in the code: the module gate's exclusion of entry nodes (37m, `27fbeb4`), the Human-GEM corrections table and the NAAA moves (37o, `4c9ec11`, `5410145`), levodopa's and melatonin's seeding on their compound nodes (37m, `daeff3b`, `bdbe933`), the flagging of conflicting ChEMBL action types (37h, `f71a3aa`), and, on 27 November 2026, 37a's (iii) and (v) member removals and 37d's two permeability ratios (`2c3696d`)."

**PR2 (37m, line 3295).** The file has held three rows (tryptophan, levodopa, melatonin) since 20 Nov, both at registration (`a0582b9`) and at `eec6e85`.
- **Old:** "…listed in `configs/drugs_acting_as_graph_compounds.csv`, which holds one row and must be curated."
- **Proposed:** "…which holds three rows (tryptophan, levodopa and melatonin) and must be curated."

**PR3 (line 1538).** This line was written in `c0ae91a` (24 Nov, 15:07). `ead5262` (18:45 the same day) set the table, and 8.5's last cell reads "Set 24 November 2026".
- **Old:** "Which table the weighted arm reads is not yet set (decision 8.5)."
- **Proposed:** "Which table the weighted arm reads was set the same day (decision 8.5): the weighted arms are pointed at `evidence_full_v5_reliability` where they are launched (`scripts/soft_prior_grid.sh`, `experiments/run_main_model_batch.py`), and every run records the weighting its table was assembled with (`evidence_weighting` in its results)."

**Left unchanged:** the statements in items 37 (23 Nov) and 38 that the rules file holds "twelve rules". Each is framed by its own amendment's date.

**Owed to a Fable pass:**

This check used no outside sources.

The reviewer listed three things owed to a Fable pass, and they remain owed:
- **CLAUDE.md:** the quoted outside sources were not re-read (support.claude.com, GtoPdb webServices.jsp and others).
- **docs/research_summary.md:** the literature claim of line 254 (Q1) was not checked: "The literature search has not yet found a published case…".
- **docs/preregistration.md:** the source claims of items 36 to 40 were not checked (Kazmi, Langthaler, Sato, the Europe PMC staff post, NLM coverage and others), and no licence was verified.

## The model documents: docs/nonlinearity_inventory.md (not stamped), docs/module_health.md

A. Inventory section 8, after the paragraph of 2 November (heading possibly "## 8. Open in 9.81 when this was written"):
"**Added 27 November 2026.** Decision 9.81 is ruled and registered, not built. Its option (a) is amendment item 37f (23 November 2026): saturation inside the fixed-point loop, soft; a floor at -1 for every node; a sourced headroom per node with a learned per-relation-type fallback where none is sourced; the 0.9 gain clamp removed; the bottleneck and the pH ceiling inside the loop; and a root-finder in place of the damped iteration. Amendment item 40 (24 November 2026, decision 9.153) replaces 37f (7)'s readout with each symptom's highest logit along the steady states a perturbation passes through as its exposure rises from rest; 37f (1) to (6) stand. That answers question 1 for every case at once, as the registered direction. Still open in 9.81: its four counts and a count of positive-feedback cycles on the v5 rebuild, which come before the build; the per-edge normalisation question, which item 37 does not settle; and the definition of count 3. Whether 37f answers questions 2 and 3 is the owner's. Until 37f is built, sections 1 and 2 describe the code: the bottleneck and the pH weight act after the loop (cases 6 and 8's status), and the contraction keeps the fixed point unique."

B. Inventory case 9, section 7's last bullet, and section 8's note of 2 November all say "the owner chose a conjunction relation (9.97)" and that a plain positive edge is "ruled out". Row 9.97 records the later rulings of 8 November 2026: Q2 "fourth option accepted", plain positive edges weighted by resting Gs activity, the linearisation of the conjunction at rest; and the resting-Gs weight is "Option c", a relation type of its own whose per-channel gain learns the weight.
- Proposed case 9 status: "**The owner chose a conjunction relation** (2 November 2026, decision 9.97), then on 8 November 2026 accepted its linearisation at rest: plain positive edges weighted by resting Gs activity (the owner: "fourth option accepted"), as a relation type of their own whose per-channel gain learns the weight (option C; "Option c"). Built with the batched rebuild of 9.97's status."
- Proposed addition to section 7's bullet: "(9.97's ruling of 8 November 2026 represents it by its linearisation at rest: case 9)".
- Section 8's note: whether question 2 is again only about complexes is the owner's reading.

C. module_health.md and docs/confirmatory_runbook.md step 0 still say the user decides the module fix. Both readings failed on 8 October and the next candidate was paused. Question for the owner: was the module fix decided beyond the leak start already registered, and if so, where should it be recorded?

**Owed to a Fable pass:** Nothing new. Mapping the 48 HPA cluster types, including `dopaminergic`, to cell classes is already owed under decision 9.155 (1). Which record names calcitonin for CALCA's split (figure 7) is a data check, not research, and needs data/processed, which is not on this disk.

## The runbook group: docs/confirmatory_runbook.md and the decision rows it reads

Verbatim from the reviewer (not in either commit):

(A) A runbook step for item 38. c2f10a7 lists it as not built. Proposed as step 2c:
"2c. Before the draw (amendment item 38 (d) and (g)): after the evidence table is rebuilt, the per-cell search of (g) is run as a research pass and its table committed; then `PYTHONPATH=. python experiments/write_research_strata_and_eras.py --search-table <search table> --output-record <record.json> --output-cells <cells.csv>` is run on the graph, evidence table and label selection the draw will be made on. It refuses while any cell is unexplained, records the SHA-256 of the search table, the graph, the evidence table, the label selection and the cells file, and refuses to overwrite an earlier record. The record and the cells file are committed before step 3's go-ahead draws the held-out set. After step 4's confirmatory scoring, `experiments/score_research_strata_and_eras.py` reads the same lockbox and reports the descriptive readings beside that scoring; it spends no alpha and gives no p-value."

(B) Item 39 and development readings:
"Development and lockbox runs of the tested model made from 24 November 2026 carry the reach rule; runs before that date do not (decision 9.150: "every run before that date was made without the rule"), so a step 1c reading made before that date is not a reading of the registered model."

(C) Items 37f and 40 and the tested model:
"Item 37 states that "the tested model is unchanged until the amendment 37f's build will need"; the v4 flags stay the registered model until 37f and item 40 are built and that amendment is registered."

(D) Step 3's preconditions:
"Step 3's go-ahead draws the held-out set only after the five ordered steps of decision 9.151 are done, on the graph rebuilt from them, and after the rule of decision 9.35's one-standard-error adversary is registered as an amendment item ("owed before the draw")."

Also for the owner to correct, since these are status cells and not this review's documents: rows 9.115, 9.116 and 9.152 say the fine rebuild is outstanding, but the 12 November 2026 rebuild rebuilt every v5 table on the fine configs (docs/data_layer_rebuild.md).

Checker's notes on the drafts:
- (A): the command as written would read the scripts' v2 defaults (graph_full_neuronal, evidence_full_v2, better_v2_full_v2). It needs --graph-dir, --evidence-dir and --label-selection to run on the draw's data, and so does score_research_strata_and_eras.py.
- (D): it could also name 9.36 (ruled 24 November 2026: the k=2 reached-node channel enters 9.35's adversary).
- The row note: 9.152 should be dropped. It was built on 24 November, after the 12 November rebuild, so its fine rebuild really is outstanding.
- The quotations in (B), (C) and (D) match rows 9.150, 9.35 and 9.151 and item 37 at eec6e85.

**Owed to a Fable pass:**

Nothing new arose from this check. As the reviewer reported, neither review re-read the quotations, licence statements and source claims in docs/membrane_potential_constants.md. That is research and out of scope. Also not checked: the RCT reaction ids of 6 November that the membrane doc places 'in the v5 graph'. No graph data is on disk, and the statement is dated.

## The study sheet (suggestions not laid in the doc) and the exploration queue

Suggestions drafted for the owner, not laid in the doc (block ids from the rev-198 outline):
1. .510 "Of those 80, only a few gate any work." Proposed: "Of the decisions waiting on you (109 in docs/status.md at eec6e85), only a few gate any work."
2. Checklist .570:
   - 9.97 item. Proposed: "9.97's two questions were ruled on 2 November 2026; what remains is the form of the G beta gamma conjunction (Option A, the two-pass row gate set out in 9.81, not yet ruled)."
   - 9.87 item. Proposed: "9.87 closed: the registered build is computed_from_the_pools (amendment item 35, `membrane_potential_build`); the 5 and 12 November builds used it; 9.112's change is not built."
   - Fagerholm item. Proposed: "Settled as decision 9.100 (27 October 2026): excluded, mentions kept."
   - GSE100472 item: still holds.
3. .15637 (labels). Proposed addition: "These counts are history (CLAUDE.md, 'A measurement carries the graph it was taken on'). The rebuild ran on 5 and again on 12 November 2026; the 12 November evidence_full_v5 holds 9,819 rows over 2,802 perturbations and 260 drugs (docs/data_layer_rebuild.md), and the label table has not been recounted here."
4. Critique list .7082:
   - Item 1, old: "No current graph exists..." Proposed: "A graph named graph_full_neuronal_split_binders_drugs_v5 was built on 5 November and rebuilt on 12 November 2026 from graph_full_neuronal down, with computed_from_the_pools; 9.112's rebuild is owed (9.106). The 22 October build was lost, and its counts are history."
   - Item 4: the 2,705 x 39 counts are from the lost build; typo "handlesk" -> "handles".
   - Item 7, old: "90 open against 60 closed, with 80 waiting on you". Proposed: "122 open against 75 closed, 109 waiting on you, at eec6e85; docs/status.md now lists 13 'open with nothing owed, kept as a record' apart."
5. .9782, old: "Three ideas are parked behind the qualifying exam and none is started". Proposed: "docs/exploration_queue.md holds 27 items in the priority order of 20 November 2026, several with passes run; you ruled on 27 October 2026 that work is not gated behind the exam. Three are below." The CollecTRI row, which says "11 decidable pairs ... 0.35 to 0.85", should note the 7 November pooled sample (24 of 49, 0.36 to 0.63).
6. .14504 (concept 6). Add the same 7 November pooled sample.
7. Things-only-you-can-do table .3669:
   - Dessauer 2017: you supplied it on 2 November 2026 and it was read (dessauer2017iuphar).
   - Fagerholm: decided as 9.100.
   - BRENDA: the table was regenerated on 4 November 2026 (41598f4).
8. .10674/.10973:
   - The Project notes were retired on 27 October 2026 (the repository is the single source).
   - "No Zotero connector ... not added to your library" no longer applies: papers go to docs/references.bib. zou2025kpuu, zou2026correction and dessauer2017iuphar are there; Ramocki 2010 is not.
Not checked further: whether R0 has been run (.1401) and whether the 24 October cyclase table's Fable recheck (critique item 3) is done. Both are research-adjacent and were left for a Fable or owner read.

CHECKER'S CORRECTION (not part of the verbatim drafts): the 9.97 item of suggestion 2 contradicts 9.97's row, whose status reads "ruled 8 November 2026: both questions and the edge proposals; the edge changes and the evidence family wait for the batched rebuild, then the sign sweep of 9.86 and 9.80". Correct that item before the drafts go to the owner. The other drafts were checked against the repository and hold:
- 109 waiting, 122 open, 75 closed and 13 kept as a record (all at eec6e85).
- 9.87 is struck.
- 9.100's exclusion.
- 9,819 / 2,802 / 260.
- 24 of 49 and 0.36 to 0.63.
- dessauer2017iuphar, zou2025kpuu and zou2026correction are in docs/references.bib; Ramocki is not.
- 41598f4 is the BRENDA regeneration of 4 November.

**Owed to a Fable pass:**

- A docs/references.bib entry for yao2021taxonomy (exploration queue item 8). The key has never been in the bibliography, and the queue now says so.
- Re-read item 7's two licence pages, which the fetch tool's permission check refused or withdrew on 27 October 2026. Under CLAUDE.md "An unanswered permission request is not a finding", they are to be read again, for example with experiments/read_public_page.py:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC4066934/
  - https://doi.org/10.3389/fncel.2014.00172
- Left by the reviewer for a Fable or owner read: whether R0 has been run (study sheet .1401), and whether the Fable recheck of the 24 October cyclase table (study-sheet critique item 3) is done.

## docs/data_sources.md: the AEMPS revision dates

The AEMPS licence quoted in docs/data_sources.md requires that a reused text 'mencionar la fecha de la ultima actualizacion de los documentos'. The AEMPS citations in configs/curated_drug_targets.csv give the nregistro, digest and read time but no last-update date, while tianeptine's row of configs/curated_label_events.csv gives 'Fecha de la revision del texto: Septiembre 2019'. Should each AEMPS-cited row carry its ficha tecnica's revision date?

**Owed to a Fable pass:**

Licence rows for sources the repository reads that have no row in docs/data_sources.md:
- GEO GSE217837 (fetched by scripts/fetch_raw_sources.sh since cb4f6c9).
- Health Canada, the DPD and the monographs (configs/admitted_atc_prefixes.csv quotes MINIPRESS, and the curated tables cite monographs).
- HPRA, MHRA and TGA (read for 9.31 on 24 November 2026; their terms are recorded as unverified in docs/records/2026-11/item931_second_agency_2026-11-24.md).
- ANSM's public database and PMDA (cited by the curated tables).

Other checks:
- Whether the openFDA row's terms also cover the DailyMed and Drugs@FDA renderings that configs/curated_label_events.csv cites.
- The Allen Institute's CC BY-NC 4.0 listing of the atlas, which only the script comment states (the cluster-400 row marks it unverified).
- Whether HPA's licence statement still reads the same for the release pinned since 27 November (9.155 (4)).
- A cell class for each of the 48 new cluster types (9.155 (1)), then the owner where a type does not fall into one class.

The licence-reading question on AEMPS revision dates goes to the owner through that research pass.

## The checker's findings on the owner-docs drafts

- **info** (.claude/worktrees/wf_7d5069a6-061-6): The reviewer's worktree was missing from `git worktree list` and from disk, though branch wave3/owner-docs was still there at 15e2403 (main of then: eec6e85 plus 8 commits, none of them by the reviewer). I recreated it at the same path on that branch with `git worktree add`. That writes only worktree metadata under the main repository's .git; the main checkout's working tree was not touched. I made no commits and pushed nothing. Both the worktree and the main checkout are clean.
- **info** (configs/documentation_registry.json): Checks (2), (5) and (6) hold. CLAUDE.md, docs/preregistration.md and docs/research_summary.md still read reviewed 2026-11-07 / as_of_commit aa35ab0, so none is stamped. None of the three was edited by the branch or by any of the 8 commits after eec6e85; among the files checked, only other documents' registry stamps changed in those commits. The branch has no commits of its own, so it has no trailers to check and no generated page or configs/study_sheet_diagrams.json committed.
- **info** (CLAUDE.md): Both corrections are confirmed against the repository.
- C1: by the local origin refs (not re-fetched), five remote branches were pushed after the 25 October check: wip/not-evidence-27oct (2026-10-27 12:13 -0400), wip/not-evidence-era-27oct (14:29 -0400), recovery/queue-item-27-2026-11-23, recovery/study-sheet-audit-2026-11-24 and recovery/study-sheet-registry-2026-11-24. So line 361's 'Every remote branch other than `main` predates direct pushing' is false.
- C2: tests/test_amendment_history.py::test_the_generated_file_is_current (lines 104-108) only asserts that docs/amendment_history.md exists and has its header. No test runs `generate_amendment_history.py --check`. tests/test_documentation_process.py runs --check only for the decision history, the status page, the file index and the registered core. So line 312's 'the test fails on a page any of them would write differently' is false.
- **nit** (CLAUDE.md): C1's 'Fact' bullet counts six branches after 24 October and includes claude/friendly-allen-q5xf0t '(25 Oct)'. Its tip is 2026-10-25 01:01 UTC, which is 2026-10-24 21:01 -0400. docs/development_sessions.md:396 also lists it among the branches found on 25 October, so the 25 October check covered it. The branches that make the sentence false are the five later ones. The drafted wording already names exactly those five, so the draft needs no change.
- **info** (docs/research_summary.md): Every drafted correction is confirmed at eec6e85.
- RS1: row 17 was added in fa56e78 (2026-11-07). Decision 9.112 measured it on the 4 November 2026 data/processed/graph_full_neuronal.
- RS2 and RS3: docs/data_layer_rebuild.md records the rebuild of 12 November 2026, which rebuilt graph_full_neuronal and kept `--membrane-potential computed_from_the_pools`.
- RS4: the registered label_likelihood is positive_unlabelled, and `--label-likelihood weighted` is a choice in experiments/run_main_model.py:2081.
- RS5: the section 6 row of 2026-10-08 drops flux sampling, and docs/experiment_design.md:170 agrees.
- RS6: V4_SHARED_MODEL in experiments/run_main_model_batch.py:81 passes `--group-by disease_cluster_and_targets`, which is also run_main_model.py's default (line 1903). Item 25 splits the held-out set on mechanism targets.
- RS7: docs/status.md at eec6e85 gives no grade or paper counts. They are in evidence_summary.json (by_grade A 2425, B 876, C 609) and literature_summary.json (distinct_pmids 134747). The status page's literature/documents count, 32,647, is a different number.
- RS8: 1.1's last cell reads 'the owner's: the ceiling, before the draw'. 9.35 was ruled 24 Nov and is not built. 9.151 is 'ruled, not built'. 9.150 was registered and switched on 24 Nov as module_support_minimum_reach = 2. 9.132 and 9.153 say what they say in the draft.
- RS9: docs/figures/model_pipeline.png last changed in 6fc913e and cf57d4b (17 Oct).
- C8: section 6 rows are dated 3 to 13 Oct plus one of 22 Oct and one of 24 Oct. c3519e8 (2026-10-12) created docs/open_decisions.md.
- The SUBGROUPS_KEPT_BY_THE_DECISION_OF_12_OCTOBER constant was removed in 8c9d824 (9.89).
- **nit** (docs/research_summary.md): C8 says decision_history.md lists '50 decisions recorded after 24 October'. That count is at 15e2403. At eec6e85, the base of the review, it is 49: 9.96 to 9.139, 9.150 to 9.153 and 9.155. 9.154 arrived in 4462981, after eec6e85.
- **nit** (docs/research_summary.md): The RS6 draft understates the registered grouping. merge_drugs_with_their_targets (mechanistic_pathway_learning/evaluation/experiment_data.py:286-289, 455-456) holds each drug out with every labelled gene it targets and also with every drug that shares a target node. Suggested wording for the owner: 'each drug held out with the genes it targets and the drugs that share a target'.
- **info** (docs/preregistration.md): All three corrections are confirmed.
- PR1: 27fbeb4, 4c9ec11, f71a3aa, daeff3b, 5410145 and bdbe933 (all 20 Nov) and 2c3696d (27 Nov) are ancestors of eec6e85 and hold the coded parts the draft names. 37m itself says 'this is built'. Item 37 was registered at a0582b9 on 23 Nov, after those 20 November commits, so 'nothing of it is built' (line 2820) was already untrue when it was written.
- PR2: configs/drugs_acting_as_graph_compounds.csv has three rows (tryptophan, levodopa, melatonin) since daeff3b and bdbe933.
- PR3: line 1538 came from c0ae91a (2026-11-24 15:07 UTC). ead5262 (18:45 the same day) set the table, and the text 'Set 24 November 2026' is in 8.5's last cell. The sentence sits inside an 'Added 24 November 2026' paragraph, and the setting happened the same day. Whether to rewrite it or add a dated note is the owner's call.
- **non-blocking (outside this group's scope)** (tests/test_amendment_history.py): I confirmed the reviewer's code defect by reading the test. Its docstring promises '--check in test form' but the body never runs `experiments/generate_amendment_history.py --check`, so no test catches a stale docs/amendment_history.md. Today `--check` passes ('up to date (7 amendments)'), so nothing is stale now. I did not fix it here: it is a test change outside this document review. Once it is fixed, draft C2(b) becomes the true wording for CLAUDE.md line 312.
