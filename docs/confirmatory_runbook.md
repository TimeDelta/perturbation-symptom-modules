# Confirmatory runbook

The steps that run the confirmatory experiment of docs/preregistration.md ("Confirmatory specification, 8 October 2026"
and its amendments). The specification decides what is run; this file decides in which order and who may do what. The
job scripts are under runs/full/ (not committed); the check-in prompts point here. The job registry, the resume
script and the rule that pauses the check-in routines while no job is active are in docs/job_harness.md.

Two families. The first (confirmatory_* configurations, configs/lockbox_v1.json, better_v1 labels) is not tested: its
development pilots (steps 1 and 1b) are reported as checks that each configuration trains. The second
(confirmatory_v2_* configurations, configs/lockbox_v2.json, better_v2 labels, rotated stratified validation, group
bootstrap; the user's decisions of 8 October 2026 and the amendments that record them) is the one tested. No
second-family run starts before the module fix is decided (step 0).

What has changed since the steps below were written (8 and 9 October 2026), as `configs/registered_rules.json`,
`configs/head_choice.json`, `docs/open_decisions.md` and the amendments of `docs/preregistration.md` record it; the
steps are kept as written and a step that one of these changes touches says so where it applies:

- One tested model, not two. The user dropped the sigmoid head on 8 October 2026, which left the noisy-OR head of each
  encoder; on 22 October 2026 the message-passing encoder moved out of the tested family to a robustness reading
  (decision 9.77, the owner: "Defer it to robustness"). The registered rules `tested_models`
  (`confirmatory_v2_linear_response_noisy_or`) and `robustness_models` (`confirmatory_v2_message_passing_noisy_or`)
  hold this, and `configs/head_choice.json` carries the two under `chosen` and `robustness`.
- No magnitude floor. The floor of 8 October (each model's 95 percent half-width plus 0.005, computed in the scoring)
  was removed on 15 October 2026 (the owner: "no floor. paired interval"); the registered rule `floor_rule` is `none`,
  which is the default of `experiments/score_confirmatory.py --floor-rule`.
- The one-sided level is 0.05 (decision 9.78, 22 October 2026), after 0.025 per model while two models were tested.
- The held-out set is not drawn. The lockbox the steps name, configs/lockbox_v2.json, was drawn on the evidence_full_v2
  table; the registration since 12 October 2026 (amendment items 1, 2 and 25) rebuilds the table (v4, then the v5 fine
  constructs) and redraws the held-out set on it by the target partition of item 25, only on the owner's go-ahead and
  under the leakage ceiling of decision 9.35 (decisions 1.1 and 1.2). Decision 9.35's status since 24 November 2026
  reads "ruled 24 November 2026, not built: the one-standard-error adversary", and its cell ends "The draw is made
  after the Human-GEM update of 9.151, on the graph built from it. Registering the rule is an amendment item, owed
  before the draw." The registered model is the v4 flags of
  experiments/run_main_model_batch.py (`V4_LINEAR_RESPONSE_MODEL`, `V4_MESSAGE_PASSING_MODEL`), which the trainer's
  defaults equal, on the v5 tables and the graph `graph_full_neuronal_split_binders_drugs_v5`. The confirmatory_v2
  configurations below (graph_full_neuronal_split_binders, evidence_full_v2, better_v2, lockbox_v2) are the family as
  registered on 9 October 2026; no lockbox run has been made on either.
- The descriptor treatment is decided (amendment item 21, 13 October 2026): `seed_masked` in both encoders, which is
  the trainer's default with `--node-descriptors`. Step 2b's wait for the user's confirmation ended with it.
- The membrane potential is computed from the pools (decision 9.87, 26 October 2026): the registered rule
  `membrane_potential_build` is `computed_from_the_pools`, and `scripts/rebuild_data_layer.sh` passes it to every
  neuronal variant it builds, so the graph a run reads is the one that script writes.
- The graph named above, `graph_full_neuronal_split_binders_drugs_v5`, was built by `scripts/rebuild_data_layer.sh` on
  5 November 2026 (decision 9.106) and rebuilt on 12 November 2026 from `graph_full_neuronal` down, still with
  `computed_from_the_pools` (`docs/data_layer_rebuild.md`, "The rebuild of 12 November 2026"). Both builds carry the
  membrane-potential layer that decision 9.112 ruled on and has not built, so 9.112's rebuild from `graph_full_neuronal`
  is still owed, and no run reads the graph as the registered graph before then. The directories of that name written
  on 20 October 2026 came from a build the owner had not asked for and are not v5. Whether the measurements taken on the 20 October build are reported as history only, as `CLAUDE.md`
  ("A measurement carries the graph it was taken on") points toward, is the owner's open question 9.106 (a).
- The Reactome release is the latest Reactome serves until the lockbox is drawn (decision 9.111, 4 November 2026). **Before
  the held-out set is drawn**, pin the release the registered graph was built from: read it from that graph's summary
  (`reactome_pathways.reactome_release`), commit its exports under `data/` (CC0, `docs/data_sources.md`), point the readers
  at the committed copy and make `experiments/fetch_reactome_pathways.py` refuse any other release. Reactome's content
  service serves only its current release, so a release left uncommitted cannot be fetched again.
- The Human-GEM pin is updated before the draw (decision 9.151, the owner, 24 November 2026; its status: "ruled, not
  built"). Until then it stays at v2.0.1 (commit `93e8d292a0cb`, `scripts/fetch_raw_sources.sh`), with the 82 rows of
  `configs/human_gem_corrections.csv`. The row's steps: "**Before the draw, in order:** (1) the pin moves to the latest
  upstream release then published, not `develop`; (2) the corrections table is re-anchored to it, a row upstream now
  agrees with dropped and a row it still differs on kept, so the owner's earlier rulings (NAAA's compartment, MAR20093
  under Q5d) stand against upstream; (3) a graph is built on the new release, and the changes that touch transmitter or
  calcium nodes or lie on a route to a labelled node are counted on it and adjudicated one by one through the
  corrections table, two sources where possible; (4) the rest are adopted on upstream's authority and disclosed as a
  limitation; (5) the graph is rebuilt, and the draw is made on it."
- The labels' likelihood is positive-unlabelled (decision 9.90; the registered default since 24 October 2026, commit
  `039bbd8`, amendment item 34d). The registered rule `label_likelihood` is `positive_unlabelled`: "Every pair the label
  selection keeps is counted once, at its code length under a positive-unlabelled likelihood
  (models/positive_unlabelled_likelihood.py)". It is the default of `experiments/run_main_model.py --label-likelihood`
  and is named in `V4_SHARED_MODEL`; the weighted loss of amendment item 3 it replaces is the `--label-likelihood
  weighted` arm.
- Module supports have a minimum reach (amendment item 39, registered 24 November 2026; decision 9.150, the owner's
  ruling of 22 November 2026). The registered rule `module_support_minimum_reach` is 2: "No module of the tested model
  holds a node that fewer than 2 distinct seed nodes of the run's training rows (the refit's rows in a refit) can
  reach", with the code location "experiments/run_main_model.py --module-support-minimum-reach, resolved by
  resolve_registered_defaults to 2 for the linear-response encoder with the noisy-OR head and to 0 otherwise".
  `V4_LINEAR_RESPONSE_MODEL` names `--module-support-minimum-reach 2`. Row 9.150's status: "the robustness model runs
  without it, a disclosed limitation of item 39 (g); every run before that date was made without the rule".
- Items 37, 38 and 40 were also registered after 7 November 2026. They are cited here by number, date and the status
  their rows give; what each changes in the steps below is not stated here.
  - Item 37 (amendment of 23 November 2026, sub-items 37a to 37o). Decision 9.132's status: "registered 23 Nov 2026;
    open: the eight `[R n]` rules (`[R 7]` withdrawn), the nineteen `[P n]` values, and the records and rebuild listed
    here".
  - Item 38 (amendment of 23 November 2026 (second)). The part of decision 9.131's status dated that day: "23 Nov, the
    owner: hypothesis mining and the recovery of causal hypotheses are not claimed for now and need a separate
    experiment with its own held-out draw; the date a pair was established is not irrelevant and is reported apart,
    descriptively, dated by the earliest record of the pair's literature search". The engineering of its readings (d)
    and (g) was built on 27 November 2026 on synthetic tables (commit `c2f10a7`:
    `experiments/write_research_strata_and_eras.py`, `experiments/score_research_strata_and_eras.py` and
    `mechanistic_pathway_learning/evaluation/research_strata_and_eras.py`); that commit lists as not built "a step for
    these scripts in docs/confirmatory_runbook.md", and item 38 says "The search of (g) is owed after the rebuild and
    before the draw."
  - Item 40 (amendment of 24 November 2026 (second); it amends 37f (7)). Decision 9.153's status: "ruled 24 November
    2026 and registered as item 40; not built: it is built with 37f's encoder; owed before the build: the pilot of
    item 40 (7), which proposes the tolerance and the time budget for the owner". The planted-network part of that
    pilot was built and run on 27 November 2026 (commits `23aef69` and `d637572`,
    `docs/records/2026-11/exposure_ramp_pilot_2026-11-27.md`); its confirmatory-graph part, and the tolerance and time
    budget it proposes, are not done.

## Steps

0. Module fix (the user, 8 October 2026: "Fixing the modules first makes sense"): the slice runs of
   runs/module_fix/module_fix_slice.sh (job module_fix_slice), read with experiments/module_health.py under the rule of
   docs/module_health.md, which was written before the runs. When it ends, report the reading for each encoder to the
   user. The leak start is applied (the user, 8 October 2026); apply nothing more to a confirmatory_v2 configuration
   before the user decides. Further candidates, if needed, go
   through the same rule. The job split_slice (runs/module_fix/split_slice.sh) starts when module_fix_slice ends and
   runs the gene and protein split arms on the slice (docs/gene_protein_split.md); report its readings with the module
   fix, since the user may move the confirmatory configurations to the split before v2_development resumes. When the
   user has decided, write runs/full/v2_development.go, move
   runs/jobs/paused/v2_development.job back to runs/jobs/ and resume it (step 1c).
   Done, 9 October 2026 (the user's decision; docs/preregistration.md, amendment of 9 October 2026): the second family
   trains on data/processed/graph_full_neuronal_split, and later the same day on its plasma-binder variant
   data/processed/graph_full_neuronal_split_binders (the user: "yes, include binder edges in confirmatory graph";
   amendment of 9 October 2026 (fourth)). The configurations carry it (experiments/run_main_model_batch.py), and
   because git ignores runs/, the two job scripts were edited in place and the change is recorded here so it can be
   reapplied in a fresh container: in runs/full/v2_development.sh and runs/full/confirmatory_lockbox.sh the
   run_baselines.py call reads `--graph-dir data/processed/graph_full_neuronal_split_binders`, and
   confirmatory_lockbox.sh passes the same `--graph-dir` to experiments/score_confirmatory.py, whose own default still
   names the merged graph. The variant directory is built by experiments/build_plasma_binder_variant.py, which must be
   run before either job in a fresh container, because data/processed is not in git.
   The H2 rewiring holds `encodes` fixed (the user, 9 October 2026: "Encodes should not be rewired in H2."), which is
   the default of experiments/run_main_model.py, so no job script changes and `--rewire-encodes` is not used.
1. confirmatory_pilots (first family, registered 8 October 2026): fold 0, seed 0 development pilots of the four confirmatory
   configurations (runs/full/confirmatory_*_disease_cluster_and_targets_development/fold0_seed0), then the development
   baselines (runs/full/baselines_v2_development, docs/generated/phase2_baselines_full_v2_development.md). When it ends, check that
   each pilot trained: the training loss falls, no NaN, an early-stopping epoch. A low development score is not a failure
   to train. Report each pilot's development macro and micro AUPRC against the development baselines and commit the
   baseline document. Compare on fold 0 (the per_fold entries with fold 0 in runs/full/baselines_v2_development/results.json;
   the baseline document shows pooled scores and per-fold means only): that fold holds the leakage group
   of 232 perturbations and is atypical (amendment of 8 October on the early-stopping validation set). The confirmatory
   configurations carry --keep-large-groups-in-training; on fold 0 it leaves the split unchanged, so pilots that ran
   before it was added stand. Ended 8 October 2026; all four trained (docs/records/2026-10/confirmatory_pilots_development.md).
1b. refit_pilots (registered 8 October 2026, after confirmatory_pilots): the four pilots refitted on their training and
   validation perturbations together for best epoch + 1 epochs (--refit-on-validation, amendment of 8 October on the
   refit). When it ends, check each refit trained (falling training loss, no NaN) and report its fold-0 development
   macro and micro AUPRC against the development baselines beside the early-stopped scores
   (results_early_stopped.json and the refit entry of results.json). Ended 8 October 2026; all four refits ran
   (docs/records/2026-10/confirmatory_pilots_development.md).
1c. v2_development (second family; registered 8 October 2026, stopped before it trained anything and paused the same
   day, runs/jobs/paused/; it refuses to start without runs/full/v2_development.go): the development baselines of
   lockbox_v2 (runs/full/baselines_lockbox_v2_development, docs/generated/phase2_baselines_lockbox_v2_development.md,
   which experiments/run_baselines.py `--markdown-output` writes when the job runs, moved there if the job writes it
   at the top of docs/ (docs/documentation_process.md, "Where documents live"); no commit holds it yet), then the two
   configurations confirmatory_v2_{message_passing,linear_response}_noisy_or on the five grouped development folds with
   seed 0 (runs/full/confirmatory_v2_*_disease_cluster_and_targets_development/fold<k>_seed0). configs/head_choice.json
   was written on 15 October 2026 from the user's decision, not from this job, and amended on 22 October 2026 (decision
   9.77): `chosen` names confirmatory_v2_linear_response_noisy_or and `robustness` names
   confirmatory_v2_message_passing_noisy_or. experiments/choose_heads.py is not run. When the job ends, check that each
   of the 10 runs trained (falling training loss, no NaN, a refit) and that its modules pass the health reading of step
   0. Report each configuration's five-fold readings against the best baselines, and commit the baseline document.
1d. After 1c: register the ablation of the two tested models, `<chosen configuration>_without_descriptors` on the same
   five development folds with seed 0 (`bash runs/full/v2_ablation.sh`, one chain per encoder at 2 threads, as in
   runs/full/v2_development.sh), and report it against the tested models when it ends. It is a development reading and does
   not hold up step 3.
2. encoder_descriptors_brain (slice, registered 8 October 2026): b3_linear_response_cofactors_descriptors_brain and
   b3_typed_nodes_descriptors_brain, five folds each. When it ends, run

   ```
   OMP_NUM_THREADS=1 PYTHONPATH=. python experiments/compare_twin_runs.py \
     --pairs b3_linear_response_cofactors_descriptors_brain:b3_linear_response_cofactors b3_typed_nodes_descriptors_brain:b3_typed_nodes \
     --markdown-output docs/generated/descriptor_rule.md --json-output runs/descriptor_rule.json
   ```

   and report the descriptor rule of the amendment of 8 October: for each encoder, the mean of its six differences (macro
   and micro AUPRC; per fold, pooled and within degree strata). Done on 8 October (linear response +0.002, message passing
   -0.018 against a b3_typed_nodes that predates the GTEx structural columns). The rule's drop branch is withdrawn (user,
   8 October: "I really don't want to drop them"; amendment on how the node descriptors enter), so no configuration
   changes on it.
2b. descriptor_treatments_message_passing and descriptor_treatments_linear_response (slice, registered 8 October 2026):
   b3_typed_nodes retrained under the current code, then five arms of each encoder, five folds each: seed_masked and
   zero_init_slow (amendment on how the node descriptors enter) and without_gene, without_gene_derived and
   without_protein (amendment on descriptor blocks per node type); the message-passing job then writes docs/generated/graph_reliance.md, docs/generated/descriptor_rule.md (again, against the
   retrained b3_typed_nodes) and docs/generated/descriptor_treatments.md (runs/encoder/descriptor_treatments_summary.sh). When it
   ends, report the treatment rule for each encoder over all five arms: each arm's graph reliance, the mean of its six
   differences against the plain arm, and which arm the rule picks. Do not edit a configuration on it before the
   user confirms. On their confirmation, for an encoder whose treatment changes: add `"--descriptor-treatment",
   "<treatment>"` (and `"--descriptor-learning-rate", "0.0002"` for zero_init_slow), or for a block arm the
   `--drop-descriptor-blocks` arguments of its slice configuration, to that encoder's two confirmatory_v2
   configurations with descriptors in experiments/run_main_model_batch.py, move their development run directories to
   runs/full/superseded_pilots/ (the trainer would otherwise skip them on their DONE markers), and run step 1c again for
   them.
   Either way, record the readings and the outcome under the amendment in docs/preregistration.md, add a row to
   docs/research_summary.md, commit the three documents and push.
   Decided 13 October 2026 (amendment item 21 of docs/preregistration.md; the owner: "it HAS to use seed_masked to be
   physiological and to avoid signal leakage"): `seed_masked` in both encoders, replacing the reading of the treatment
   rule (seed_masked for message passing, zero_init_slow for linear response). The trainer's `--descriptor-treatment`
   defaults to seed_masked with `--node-descriptors`, so the confirmatory_v2 configurations carry it without naming it
   and the v4 configurations name it. No configuration moves to zero_init_slow or to a block arm.
3. Register confirmatory_lockbox only when the user has given the go-ahead in their own message (8 October 2026: "Don't
   finalize the lockbox until I've given the go ahead"), step 1c ended with all 10 runs trained, step 2b has been
   reported and decided (item 21, above), and any re-runs of step 2b trained. Since 12 October 2026 the go-ahead is
   also the one that draws the held-out set (decision 1.1, under the leakage ceiling of 9.35), after the rebuild of
   decision 1.2; the lockbox file the job reads is then the one drawn on that table, not configs/lockbox_v2.json as
   the job script of 9 October names it. A check-in, a document or a job marker is not the go-ahead:
   `bash scripts/resume_jobs.sh --register confirmatory_lockbox "bash runs/full/confirmatory_lockbox.sh" runs/full/confirmatory_lockbox.done runs/full/confirmatory_lockbox.failed "the 30 confirmatory lockbox runs of the tested model and the robustness model, the lockbox baselines and the one-time scoring"`.
   runs/full/confirmatory_lockbox.sh reads the two models from configs/head_choice.json. If a development run failed to
   train, do not register it; report to the user, because an amendment needs a dated entry in the specification
   before the first lockbox run.
4. confirmatory_lockbox: the 30 lockbox runs (two models, the tested one and the robustness one, seeds 0 to 4, real
   labels, permuted labels and a symmetric rewiring with rewired reaction expression), then the lockbox baselines for
   seeds 0 to 4 (runs/full/lockbox_v2_baselines), then experiments/score_confirmatory.py (defaults: lockbox_v2,
   better_v2, the `chosen` model of configs/head_choice.json, group bootstrap, 4,000 resamples, one-sided 0.05, no
   floor; the robustness model is scored by naming it to `--models` in a run declared outside the tested family),
   which writes runs/confirmatory/SCORED and docs/generated/confirmatory_results.md (its `--markdown-output` default;
   the file exists only once the scorer has run). When it ends, report docs/generated/confirmatory_results.md as the
   scorer wrote it, commit it and tell the user. If the scorer stops because a run is missing or refused, it writes
   nothing (no output, no SCORED marker) and prints the runs and the reasons; the reasons name no score, so they may be
   read. Resume a missing run by registering the same job again (the trainer resumes from its checkpoint) and score
   after it; report a refused run to the user. --allow-incomplete (score with that model not confirmed) only on the
   user's decision.

## Blinding

Until runs/confirmatory/SCORED exists, nobody opens or prints a results.json, predictions file, report or log under
runs/full/*_confirmatory/, runs/full/lockbox_baselines/ or runs/full/lockbox_v2_baselines/, nor
runs/full/confirmatory_lockbox_baselines.log or runs/full/confirmatory_scoring.log. The two trainer logs
runs/full/confirmatory_lockbox_first_model.log and runs/full/confirmatory_lockbox_second_model.log print no lockbox
score (experiments/run_main_model.py) and may be read.
score_confirmatory.py runs once; a second scoring (--rescore, or a run after SCORED exists) is not done.

## Not to be done

- Any second-family run (development baselines included) before the user decides the module fix (step 0), and any run
  of the second family's sigmoid configurations.
- Full-graph training other than the jobs above (refit_pilots, v2_development and the step 1d ablation among them) and
  development runs of a descriptor treatment the slice selects (the user allowed full-graph tests of the treatments on
  8 October). The first family's ablation_pilots_without_descriptors job was retired before it trained anything
  (superseded by step 1d).
- Edits to the confirmatory_v2 configurations, configs/lockbox_v2.json, configs/head_choice.json (written 15 October
  2026), experiments/choose_heads.py, experiments/score_confirmatory.py or the decision rule, except where step 2b
  directs or the user decides. The user's decisions so far are the amendments the registered rules record: the floor
  removed (15 October 2026), the message-passing encoder moved to robustness in configs/head_choice.json (22 October
  2026, decision 9.77) and the scorer's `--alpha` default returned to 0.05 (decision 9.78). The first family's
  configurations and configs/lockbox_v1.json stay as records.
- Regenerating graph_full_neuronal, evidence_full_v2, the better_v1 or better_v2 selection, the node descriptors, the
  cell-class weights or the expression tables of experiments/write_expression_tables.py while a confirmatory job reads
  them.
- Re-registering the paused full-graph B3 job (runs/jobs/paused/).
