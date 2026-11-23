# Pre-registration skeleton (to be completed before Phase 3 and posted to OSF)

Frozen in Phase 0 and 1: symptom set and HPO term exclusions (docs/symptom_crosswalk.csv, audited in
docs/generated/hpo_term_audit.md), curated module scaffolding (docs/curated_pathway_modules.csv), pinned data
versions (docs/data_sources.md), evidence grading policy and weights (configs/evidence_assembly.yaml:
grade A by curated-synopsis provenance with frequency scaling), splits and metrics (configs/evaluation.yaml).

Primary hypothesis: see experiment_design.md section 6.5 (equifinality independence and
convergence indices; sufficiency test by module ablation).

Primary endpoint: macro-averaged AUPRC under the pathway-wise split, proposed model versus the
best of network proximity, knowledge-graph embedding and relational GNN with sigmoid head;
minimum difference 0.05; 95 percent bootstrap interval excluding zero; five seeds by five folds.
**Where the current rules are.** `configs/registered_rules.json` holds the load-bearing registered rules, one entry
each, and is the canonical statement of their current values; `tests/test_registration_matches_the_code.py` asserts
every entry against the implementation it names, so a rule changed in code without changing the registration fails the
suite. Prose in this document refers to that file rather than restating values. Where prose below still carries a
value, the file wins and the prose is a record of what was registered earlier.

**Superseded on the decision rule** (marked 15 October 2026, before any lockbox run): **there is no magnitude floor.**
The floor was revised three times on 8 October (0.05 to a fixed 0.041 macro and 0.028 micro, then to each model's
realised half-width plus 0.005) and removed on 15 October, the owner: "no floor. paired interval". The decision rests on
the paired interval, and effect sizes are reported in standard errors of the available precision. The tested models are
the two noisy-OR configurations by the head decision, not four, and from 22 October 2026 one (item 34b). The 0.05 here
is the first version of the floor and is kept as the record of it. Proposed in design version 0.4 and to be confirmed
here: the pathway-wise split is the Human-GEM subsystem hold-out (pathway subsystems only; transport, exchange and
isolated bins are not pathways), scored on pooled held-out predictions and paired with the permuted-label run of the
same split; the curated modules hold 37 perturbations on the monogenic slice and serve the interpretability overlap
instead.

Failure criterion: if the proposed model does not beat the popularity and network proximity
baselines under the disease-cluster grouped split, the architecture is abandoned before ablations
run. (Design version 0.3 named the gene-wise split; it leaks through genes sharing a disease,
design section 6.1.)

Negative controls run with every split: labels permuted within degree strata; degree-preserving
rewiring; grade shuffle; peripheral-event control.

Precision of the primary comparison on the monogenic slice (451 perturbations, disease-cluster
grouped split): the paired-bootstrap 95 percent half-width of a pooled macro AUPRC difference between
two models is about 0.015 to 0.02 (docs/generated/phase3_main_model.md), so the minimum difference of 0.05 is
detectable there; on the curated-module hold-out (37 perturbations) it is not, which is why the
subsystem definition of the pathway split is proposed above. The full data (drug perturbations and the
signaling layers) will shift these widths and the statement is to be recomputed before posting.

Amendment of 7 October 2026, written after the monogenic-slice results were seen. Nothing here was posted
before those results, so the amendment is disclosed as made after them (Nosek et al. 2018,
doi:10.1073/pnas.1708274114, on preregistration when "the data are preexisting").

- The monogenic slice is a pilot. It has one layer of the graph (the metabolic layer), 451 genes, no brain
  expression and no drug perturbations, and on it even a readout trained on the random walk's own distributions
  does not beat the untrained walk (docs/generated/trained_diffusion_readout.md), so the slice cannot separate a weak mechanism
  from too few labels. Its result, that no trained configuration beats the random walk, does not trigger the failure
  criterion above, and no component (the linear-response encoder, the pathway modules, the node descriptors) is
  dropped on its strength. This is the user's decision of 7 October: the mechanistic encoder and the node properties
  it reads stay until the full graph with all layers and better (not more) training examples has been tested.
- The confirmatory test is the full graph with every layer built at the time of the run (graph_full_neuronal on
  7 October: Human-GEM, OmniPath, CollecTRI and the Reactome neuronal and oxidative layer), the node descriptors and
  the brain region and cell-class expression, under the disease-cluster grouped split. The failure criterion applies
  there unchanged.
- What makes a training example "better" is fixed and dated in this file before the first full-graph model is
  scored, from evidence properties only (grade, frequency qualifier, provenance, layer contact), never from any
  model's predictions.
- The ablations (node descriptors, brain expression, edge signs, relation typing) run whatever the primary result,
  because they are what says which part carries the signal (confirmed by the user on 7 October). The with and without
  descriptors comparison is one of them; the descriptors are not dropped before the final experiment.
- The confirmatory configuration is the full graph with the node descriptors, the brain region and cell-class
  expression, the cell-class propagation channels (including a dopaminergic class) and the better training examples.
  Full-graph runs made before all of these exist are full-graph pilots and are reported as such.

Better training examples, fixed on 7 October 2026 before any full-graph model was scored (experiments/build_label_selection.py;
data/processed/label_selection/better_v1_full.parquet, selection version better_v1):

- A gene pair (grade A, an HPO annotation) is kept when its frequency is at least 0.30, the lower bound of the HPO
  frequency term Frequent (HP:0040282, present in 30 to 79 percent of cases). Pairs annotated Occasional or Very rare,
  pairs with a counted frequency below 30 percent and pairs with no frequency are set aside.
- A drug pair (grade B, SIDER or OnSIDES label) is kept when its label frequency is at least 1 percent, the lower bound of
  the CIOMS frequency category common, or when both SIDER and OnSIDES list it (two separate label extractions). The rest,
  most of them label statements with no frequency, are set aside.
- A pair set aside is masked, not relabelled: it is neither a positive nor a negative in the loss or in any metric
  (load_experiment_data, label_mask). Unobserved pairs stay unlabelled as before.
- On evidence_full this keeps 1,735 of 3,260 positive pairs: 1,395 gene pairs over 844 genes and 340 drug pairs over
  59 drugs. Elevated mood or mania keeps 11 positive pairs and psychomotor retardation keeps 1, so psychomotor
  retardation leaves the macro average (five positives are needed) and elevated mood or mania is scored on few positives.
- Layer contact was considered and not used, because it does not select on graph_full_neuronal: 2,286 of 2,425 gene pairs
  and all 876 drug pairs already touch a non-metabolic layer.
- Every full-graph run, baseline and comparison is trained and scored under this selection. A run trained on another
  selection is refused by the scoring scripts (aggregate_main_model_runs.py, compare_twin_runs.py), which compare the
  SHA-256 of the selection file (ffb06fb4… for better_v1_full). Before this rule, training already weighted each gene
  positive by its frequency (mean weight 0.64 over the 796 gene pairs below 0.30, 1.0 at 0.30 or above and 1.0 with no
  frequency), and every pair counted fully in scoring; the selection removes the set-aside pairs from both.

Symptom list expanded on 7 October 2026 at the user's request, before any full-graph model was scored (docs/symptom_crosswalk.csv,
audited in docs/generated/hpo_term_audit.md; data/processed/evidence_full_v2; the better_v1 rule above applied to it:
data/processed/label_selection/better_v1_full_v2.parquet, SHA-256 c691a9aa…). This replaces evidence_full and better_v1_full
(ffb06fb4…) for every full-graph run; the slice keeps its own evidence table.

- Frame: a symptom is added when it is an item or domain of a standard instrument (PHQ-9, GAD-7, the Neuropsychiatric
  Inventory, HAM-D item 14, Y-BOCS) and has an HPO term, MedDRA preferred terms or both. Diagnosis-level HPO terms stay
  excluded (assumption A7).
- New symptoms: apathy, suicidality, self_injury, compulsive_behavior, disinhibition_or_impulsivity, hyperactivity,
  emotional_lability, increased_appetite, abnormal_dreams, decreased_libido and catatonia. Each excluded descendant is named in
  the crosswalk with its reason. Two were found by looking at which genes a term supplies: Eye poking (all its annotated genes
  are Leber congenital amaurosis genes; it is the oculo-digital sign of blind children) and Inappropriate laughter (mostly the
  Angelman syndrome sign: UBE3A, SLC9A6, MECP2, CDKL5).
- Existing symptoms gained the MedDRA preferred terms drug labels use for the same construct, several of which the HPO side
  already held: Akathisia (psychomotor agitation; HPO Akathisia sits under Restlessness), Delirium, Disorientation and the
  amnesias (cognitive impairment; HPO Delirium sits under Confusion), Paranoia and the hallucination subtypes (psychosis, with
  HPO Paranoia added), Hostility and Anger, the insomnia subtypes, Sedation, Dysphoria and Elevated mood. Tension was added to
  anxiety on the reading that MedDRA files it with the anxiety symptoms; that placement was not checked against the MedDRA
  hierarchy, which the project does not hold.
- Not added: decreased appetite (on drug labels it follows nausea and other gastrointestinal effects); autism and attention
  deficit hyperactivity disorder (diagnosis-level); intellectual disability and speech delay (developmental, not a symptom
  state); tics (a motor disorder); lethargy and drowsiness (in HPO, signs of reduced consciousness); sleep apnoea.
- Counts: 4,439 positive pairs, 2,211 kept (1,793 gene pairs over 925 genes; 418 drug pairs over 61 drugs), against 1,735
  before. Kept pairs by symptom: cognitive impairment 373, fatigue 331, irritability or aggression 273, anxiety 254,
  depressed mood 189, psychomotor agitation 89, psychosis 85, somnolence or hypersomnia 84, hyperactivity 83, self-injury 75,
  emotional lability 66, disinhibition or impulsivity 62, insomnia 57, apathy 54, compulsive behaviour 46, increased appetite 37,
  abnormal dreams 17, suicidality 13, elevated mood or mania 11, decreased libido 11, psychomotor retardation 1, catatonia 0.
- Scored symptoms: every symptom with at least five kept positive pairs in the whole data (so psychomotor retardation and
  catatonia are not scored, and anhedonia has no pair). The macro average takes the symptoms with at least five positives in
  the test set, as before; micro AUPRC (below) takes every scored symptom.
- The pipeline rebuilt from the previous crosswalk reproduces evidence_full and better_v1_full exactly (selection SHA-256
  ffb06fb4… both times), so the changes come from the crosswalk alone.
- What the expansion changes: most of the added kept pairs are gene pairs, and four new symptoms (self-injury, hyperactivity,
  compulsive behaviour, disinhibition) come mostly from neurodevelopmental syndromes with no or few drug positives. Drug kept
  pairs rose from 340 to 418.

Micro AUPRC, added on 7 October 2026 at the user's request (ranking_and_calibration_metrics.micro_auprc): average precision over
every labelled perturbation-symptom pair ranked in one list. It keeps the symptoms the macro average leaves out in a test set
with fewer than five positives. It weighs frequent symptoms more and credits ranking symptoms by base rate, so it is compared
against the same baselines (popularity among them). Every scoring script reports it beside the macro average, in the same
three readings (per fold, pooled, within degree strata).

Leakage grouping, decided 7 October 2026 (experiments/check_drug_target_leakage.py, docs/drug_target_leakage.md): under the
disease-cluster grouping a drug is grouped by its target set, so it can sit in another fold than the loss of function of its
own target gene. On the expanded labels, 69 of the 73 drugs that target a labelled gene had such a gene in another fold, and 66
of the 418 kept drug positives were also kept positives of such a gene. Where a labelled target gene is positive for a symptom
the drug is positive in 67 of 242 pairs (0.28), against 0.17 over all labelled drug pairs. Every full-graph run therefore uses
the grouping disease_cluster_and_targets, which holds a drug out with every labelled gene it targets and every drug sharing a
target node. That closes the overlap (0 drugs, 0 shared positives) and keeps the fold sizes at 307 to 308 perturbations; the
largest group grows from 140 to 232 perturbations.

Confirmatory specification, 8 October 2026 (experiments/score_confirmatory.py implements it). It replaces the primary
endpoint and failure criterion at the top of this file; the reasons are given with each item. Full-graph training before
it: two message-passing pilots interrupted after one epoch, on 3 October (noisy-OR head, the full graph and evidence of
that date, its command not logged) and 6 October (sigmoid head, graph_full with evidence_full), which printed validation
macro AUPRC 0.366 and 0.310 on perturbations some of which are now in the lockbox, and timing runs of five training
steps on a development fold (experiments/run_main_model.py --timing-batches), which score nothing. No full-graph model
has scored a test set. Decisions taken with the user on 7 and 8 October: both heads, both encoders, the rewiring
control, macro and micro AUPRC both required, a degree control, a lockbox, five seeds, and no flux sampling in the
confirmation.

- Split. The grouped split by disease_cluster_and_targets with a lockbox (configs/lockbox_v1.json, SHA-256 ebd851a8…,
  drawn by experiments/draw_lockbox.py with seed 20261007): 317 of 1,539 perturbations (253 genes, 64 drugs, 27 of them with
  a kept positive), 481 kept positive pairs, 18 symptoms with five or more kept positives inside it. The draw takes whole
  leakage groups, per stratum (groups holding a drug with a kept positive, and the rest), in a seeded order, until each
  stratum's lockbox reaches 20 percent of its perturbations; the one group above 5 percent of all perturbations
  (cluster:ABCA3, 232 perturbations) stays in development. The pathway-wise subsystem split of the skeleton becomes a
  secondary reading on the development set: Human-GEM subsystems hold metabolic genes only, so it cannot test drugs or the
  signalling layers.
- Models (experiments/run_main_model_batch.py): confirmatory_message_passing_noisy_or, confirmatory_message_passing_sigmoid,
  confirmatory_linear_response_noisy_or and confirmatory_linear_response_sigmoid. Every one reads graph_full_neuronal
  (nodes 48ebf531…, edges 78cf6c07…), evidence_full_v2 (228a4afe…), the better_v1 selection of it (c691a9aa…) and the node
  descriptors (14033cb3…: protein, metabolite and reaction properties, brain region and cell-class expression). The
  message-passing encoder reads typed node features with the descriptors. The linear-response encoder adds the cofactor
  relations and propagates once per cell class (cell_class_weights 234224d8…: the ten HPA single-nucleus classes, the
  dopaminergic class and an all-cells class), with the 1,684 extracellular metabolites one pool shared by the classes other
  than all cells. The noisy-OR head starts its leaks at the training base rate, its module biases at -3 and its gate noise at
  0.5, with link, leak and gate learning rates 0.02, 0.0002 and 0.05; the sigmoid head uses the trainer defaults. Asymmetry:
  the message-passing encoder sees cell-class expression only as node descriptors, not as channels.
- Training. Each confirmatory run trains on the 1,222 development perturbations, of which one grouped seventh is the
  validation set for early stopping (fold `seed % 7` of round(1 / 0.15) = 7 grouped folds, so seeds 0 to 4 rotate over
  folds 0 to 4 and folds 5 and 6 never serve as validation — corrected 15 October 2026 from "fold 0", which describes
  seed 0 alone, against the validation_fold assignment of run_main_model.py (its lines 1016 and 1048 on that date);
  validation loss, patience 8, at most 60 epochs; as amended on 8 October, drawn from the groups no larger than half of
  it, 142 perturbations, and followed by a
  refit on all 1,222 for the chosen number of epochs, which is the model scored), and scores the lockbox once
  (--lockbox configs/lockbox_v1.json --score-lockbox). Seeds 0 to 4. Per seed and model, two control runs: labels permuted
  within degree quintiles and within the lockbox and the development set apart (rows move whole with their weights and
  label mask; --permute-labels), and the graph rewired within each relation with 50 attempted swaps per edge, no self-loops
  and no repeated edges (--rewire-swaps-per-edge 50; 32 seconds; 0.5 percent of edges stay in place). A model missing any of
  its fifteen runs is not confirmatory.
- Baselines. popularity, degree_popularity, random_walk_with_restart and knowledge_graph_embedding_transe, fitted on the
  development set and scored on the lockbox for each seed (run_baselines.py --lockbox ... --score-lockbox --seed k
  --with-kg-embedding --rewiring-method integer_draws), which also scores them on that seed's permuted labels. The best
  baseline of a reading is the one with the highest seed-mean lockbox score, chosen without reference to any model. The
  relational GNN with sigmoid head, a comparator in the skeleton, is now one of the four tested models; popularity and
  degree_popularity are added because they score highest on the full graph (docs/generated/phase2_baselines_full_v2.md).
- Readings (seed mean of model minus best baseline on the lockbox rows): macro AUPRC over the 18 lockbox symptoms; micro
  AUPRC over every symptom with five or more kept positives in the whole data (20); both after ranking every score inside
  degree strata; the permutation difference in differences (the advantage on the real labels minus the advantage when model
  and baseline are trained and scored on permuted labels); the rewiring difference (the model minus the same model on its
  rewired graph).
-  Hypotheses and decision. **Superseded in three respects by the amendments of 8 October 2026 below** (marked 15
  October 2026, before any lockbox run): Holm's procedure over the eight hypotheses is withdrawn and each model is
  tested on its own at one-sided 0.025 (one model at one-sided 0.05 from 22 October 2026, items 34b and 34c); there is
  no magnitude floor at all as of 15 October 2026, the 0.05 here having been revised twice on 8 October and then
  removed; and the two permutation readings became secondary rather than part of H1. The paragraph is kept as the record
  of the original rule. H1 (prediction) for a model: macro, micro, both within-strata and both permutation readings
  above zero, and the macro and micro differences at least 0.05. H2 (graph content): H1 and both rewiring readings above
  zero. Each reading's one-sided p-value comes from a paired bootstrap over lockbox perturbations (4,000 resamples, the
  same rows for every model, seed and baseline); a hypothesis's p-value is the largest of its readings' (an
  intersection-union test, Berger 1982). Holm's procedure (Holm 1979) runs over the eight hypotheses at one-sided 0.025.
  A model is confirmed for H1 or H2 when Holm rejects that hypothesis and its macro and micro differences reach 0.05.
- Failure criterion, replacing the one at the top: if no model is confirmed for H1, the architecture has not been shown
  to predict better than the baselines. The ablations still run (amendment of 7 October).
- Secondary readings, outside the Holm family and reported with paired intervals: noisy-OR minus sigmoid within each
  encoder, linear response minus message passing within each head, per-symptom AUPRC, the subsystem split and every
  ablation on the development set.
- Order of work. Pilots of any configuration run on the development set only (--lockbox without --score-lockbox; runs land
  in <configuration>_<grouping>_development). If a pilot shows a confirmatory configuration failing to train (a defect, not
  a low score), the configuration may be amended here, dated, before its first lockbox run. The lockbox is scored once by
  experiments/score_confirmatory.py, which writes a SCORED marker; a second scoring is listed in its output.
- Precision. On the full graph a 20 percent grouped hold-out (one of five folds, 308 perturbations, 382 to 548 kept
  positive pairs, 13 to 20 symptoms with five positives) gave paired-bootstrap 95 percent half-widths for differences
  between two baselines of 0.019 to 0.063 in macro AUPRC (median 0.041) and 0.018 to 0.041 in micro (median 0.028)
  (experiments/estimate_holdout_precision.py). At Holm's smallest level, 0.025 / 8, the half-width grows by about 1.4
  (2.73 / 1.96 standard errors), so a macro difference near 0.06 and a micro difference near 0.04 are the smallest the
  lockbox can confirm. Two caveats: a model and a baseline may co-vary less than two baselines do, which widens the
  interval, and the seeds are averaged, not resampled, so seed variance is not in it.
- Compute. On this 4-core machine, at 3 threads and batch 16, a training step on a development fold takes 1.8 s
  (linear response, sigmoid), 2.1 s (linear response, noisy-OR), 2.5 s (message passing, sigmoid) and 2.7 s (message
  passing, noisy-OR), after both encoders were changed on 8 October to multiply only the 54,982 stacked adjacency rows that
  hold an edge instead of all 700,435 (identical output, tested; before the change 15.8, 16.9, 6.9 and 7.0 s). With the
  slice's epochs to early stopping (about 15 for the sigmoid head, about 35 for noisy-OR), the 60 confirmatory runs take
  about 70 hours. Run order: one development pilot per configuration (fold 0, seed 0) to check that it trains; the
  development baselines; the 60 lockbox runs, two at a time with 2 threads each; then the lockbox baselines for seeds 0 to 4
  (their lockbox scores are not read before the models finish) and score_confirmatory.py.
- Flux route. Not in the confirmation: measured on Human-GEM, one LP takes 0.12 seconds with every boundary open, a flux
  variability or sampling warm-up per knockout about 0.9 core-hours; the perturbations a Human-GEM knockout can represent
  hold 14 percent of the kept pairs (235 genes, 15 drugs); no brain medium is defined; and a drug is not a knockout. It stays exploratory.

Amendment, 8 October 2026, written before any lockbox run and before the slice runs it refers to had finished: node
descriptors. On the slice, adding the node descriptors without brain expression lowered both encoders' macro and micro
AUPRC in all six readings of experiments/compare_twin_runs.py (per fold, pooled and within degree strata). Message
passing (b3_typed_nodes_descriptors against b3_typed_nodes): macro per fold -0.030 [-0.056, -0.004], within degree strata
-0.018 [-0.039, -0.002], micro pooled -0.018 [-0.035, +0.003]; with the descriptors it scored the same as the
descriptors-only control without a graph (+0.002 [-0.023, +0.027] per fold). Linear response
(b3_linear_response_cofactors_descriptors against b3_linear_response_cofactors): micro pooled -0.025 [-0.043, -0.008],
micro per fold -0.027 [-0.051, -0.002], macro pooled -0.003 [-0.016, +0.014]. The confirmatory configurations read the
descriptors with brain region and cell-class expression, which the slice had not tested, so two slice arms now test them
(b3_linear_response_cofactors_descriptors_brain and b3_typed_nodes_descriptors_brain). Rule: for each encoder, take the six
differences of its brain-expression arm minus the same encoder without descriptors (b3_linear_response_cofactors;
b3_typed_nodes). If their mean is below zero, that encoder's two confirmatory configurations drop --node-descriptors, their
development pilots are moved aside and rerun before the first lockbox run, and the linear-response encoder keeps its
cell-class channels; otherwise they stay as specified. The rule uses the point estimates, not the intervals, because the
slice cannot resolve differences of this size (half-widths of 0.015 to 0.04) and an input that does not help on
development data adds parameters to a model trained on about 1,000 perturbations. Limitation: the slice is the metabolic
graph, without the signalling, receptor and electrical layers of graph_full_neuronal. Held on 8 October: the user is
deciding how the descriptors enter, so the rule is reported when its runs finish and applied only on their confirmation.

Amendment, 8 October 2026, before any lockbox run (the user's decision): the two permutation readings leave H1 and become
secondary readings, reported with their intervals and p-values outside both hypotheses. H1 is now the macro, micro and
both within-strata readings above zero with the macro and micro differences at least 0.05; H2 is H1 and both rewiring
readings above zero; Holm still runs over the eight hypotheses. **Both of those clauses are superseded by the later
amendments of the same day** (marked 15 October 2026): Holm over the eight hypotheses is withdrawn, and the floors
became 0.041 and 0.028 and then each model's realised half-width plus 0.005, before being removed entirely on
15 October. Reason: the difference in differences subtracts a second
noisy difference, so if the two are nearly uncorrelated its standard error is about 1.4 times that of the plain
difference and it would decide H1 (a projection, not a measurement). The within-strata readings and the degree_popularity
baseline remain the degree control. experiments/score_confirmatory.py implements it. The lockbox runs start only on the
user's go-ahead.

Amendment, 8 October 2026, before any lockbox run and before the slice runs it names had started: how the node
descriptors enter. The user keeps the descriptors in both encoders ("I really don't want to drop them") and asked how to
stop them overwhelming the graph, so the drop branch of the descriptor rule above is withdrawn: neither encoder's
confirmatory configurations drop --node-descriptors. The rule's readings are still reported (docs/generated/descriptor_rule.md).
On 8 October they were: linear response, mean of the six differences +0.002 (macro per fold -0.003, pooled +0.006,
within strata +0.007; micro -0.004, -0.001, +0.007); message passing -0.018 (macro -0.022, +0.002, -0.007; micro -0.040
[-0.057, -0.022], -0.033 [-0.052, -0.012], -0.006). The message-passing reference, b3_typed_nodes, was trained before the
structural node features gained the two GTEx brain expression columns (commit cb5cf70, 3 October; 16 structural columns
against 18), so that comparison, and the message-passing readings of the descriptor amendment above, also change the
structural features. b3_typed_nodes is retrained under the current code (runs/encoder) and the message-passing readings
are reported again.

Why a treatment: scored on a degree-preserving rewiring of its graph at test time (experiments/evaluate_on_rewired_graph.py,
50 attempted swaps per edge, seed 0, the trained weights unchanged), the linear-response encoder without descriptors
(b3_linear_response_cofactors) loses 0.026 ± 0.019 macro AUPRC over five folds and with the brain-expression descriptors
0.001 ± 0.010 (micro 0.004 ± 0.019 and -0.002 ± 0.005), at about the same AUPRC on the real graph; the descriptors-only and local-structural controls lose 0.000, as
a model without edges must. The descriptors replace what the edges gave instead of adding to it. In message passing with
descriptors the best validation epoch is 2 to 5 on the slice and 0 in the full-graph development pilot, and at the best
epoch the descriptor weights are at their initial scale (root mean square 0.049 against 0.046 for the initial uniform
draw), so the descriptors enter as a fixed random projection that tells the nodes apart.

Treatments (mechanistic_pathway_learning/models/descriptor_treatments.py, --descriptor-treatment): seed_masked, under
which each perturbation's perturbed nodes read their structural columns only, in the message-passing base state (in the
perturbed pass and in that perturbation's own unperturbed reference) and in the linear-response output gate, while every
other node keeps its descriptors; and zero_init_slow, under which the descriptor columns get their own linear map,
initialised at zero and trained at 0.0002, a tenth of the main learning rate. Adam moves a parameter by about one
learning rate per step, so on the slice (20 steps per epoch) a descriptor weight moves at most about 0.02 in five epochs;
a weight penalty was not used because under Adam the step does not scale with the gradient (Loshchilov and Hutter, ICLR
2019: L2 regularization and weight decay "are equivalent for standard stochastic gradient descent (when rescaled by the
learning rate), but as we demonstrate this is not the case for adaptive gradient algorithms, such as Adam") and a
penalty acts through the optimum, which early stopping does not reach. With plain (the default) the encoders are
unchanged: the same parameters, random draws and outputs, bit for bit, as before the treatments existed.

Slice arms (runs/encoder, five disease-cluster folds each): b3_typed_nodes_descriptors_brain_seed_masked,
b3_typed_nodes_descriptors_brain_zero_init_slow, b3_linear_response_cofactors_descriptors_brain_seed_masked and
b3_linear_response_cofactors_descriptors_brain_zero_init_slow, each one change from its *_descriptors_brain arm (the
plain arm). Readings per arm: graph reliance, the mean over folds of the macro and micro AUPRC lost on the rewired graph,
averaged over the two (docs/generated/graph_reliance.md); and the six differences of experiments/compare_twin_runs.py against the
plain arm (docs/generated/descriptor_treatments.md). Rule, per encoder: a treatment qualifies if its graph reliance is larger than
the plain arm's and the mean of its six differences against the plain arm is at least -0.01. The qualifying treatment
with the larger graph reliance replaces plain in that encoder's two confirmatory configurations; if none qualifies,
plain stays. Point estimates, as in the descriptor rule, because the slice does not resolve differences of this size.
The margin of -0.01 is below the slice's resolution on purpose: the treatments exist to move the work from the
descriptors to the graph, which the user asked for, and the rule rejects only a treatment whose loss is large enough to
show. As with the descriptor rule, the outcome is reported and applied only on the user's confirmation
(docs/confirmatory_runbook.md, step 2b); a change means new development pilots of the changed configurations before the
first lockbox run. Cost: seed_masked propagates a reference per perturbation, so a message-passing step takes about 2.4
times as long (3.8 against 1.55 seconds on the slice), and so would the 30 message-passing lockbox runs; in the
linear-response encoder it costs one more gate per perturbation. Limitations: test-time rewiring measures how much a
trained model depends on its edges, not whether the real edges beat degree-matched ones (the retrained rewiring control
of H2 asks that); one rewiring seed; the slice is the metabolic graph only; and under seed_masked a perturbation's
neighbours still carry descriptors that describe it indirectly (a gene's reactions carry its EC numbers).

Amendment, 8 October 2026, before the arms it names had started: descriptor blocks per node type. The user suggested
removing the descriptors of some node types, genes first, because a gene's descriptors are largely the graph around it
(which reactions it catalyses and which proteins it binds), and asked for the search to continue on the slice until it
is no longer worth it, with full-graph tests where they say more. --drop-descriptor-blocks leaves whole blocks out
(graph/node_descriptors.py, DESCRIPTOR_BLOCK_PREFIXES: metabolite, reaction_ec, reaction_brain, protein, gene_brain). Three
slice arms per encoder, each one change from its plain *_descriptors_brain arm: without_gene (protein and gene_brain out,
the user's suggestion), without_gene_derived (also reaction_brain, the genes' expression carried onto their reactions by
the gene rule, so a gene seed's own reactions no longer carry its expression pattern) and without_protein (only the
protein function block out; the genes keep brain expression, which the graph does not encode for the message-passing
encoder). On the slice every seed is a gene, so without_gene removes what seed_masked removes there and more, at no extra
compute. These arms join seed_masked and zero_init_slow under the treatment rule of the previous amendment (graph reliance
above the plain arm's, mean of the six differences against the plain arm at least -0.01, the larger graph reliance among
those that qualify). Arms the iteration adds later are dated here before they run, and every arm tried is reported in
docs/generated/graph_reliance.md and docs/generated/descriptor_treatments.md, chosen or not: selecting among slice arms makes the slice
estimate of the chosen arm optimistic, which does not reach the lockbox, since the lockbox is scored once by a model
fixed before it is opened.

Readings of the treatment rule (8 October 2026, descriptor_treatments_message_passing and _linear_response ended; graph
reliance from docs/generated/graph_reliance.md as the mean of macro and micro reliance, the six differences against the plain arm
from docs/generated/descriptor_treatments.md). Not applied: it waits for the user's confirmation (docs/confirmatory_runbook.md,
step 2b).

| encoder | arm | graph reliance | mean of six differences | qualifies |
|---|---|---|---|---|
| message passing | plain (b3_typed_nodes_descriptors_brain) | +0.0045 | | |
| message passing | seed_masked | +0.0149 | +0.0032 | yes |
| message passing | zero_init_slow | +0.0092 | +0.0087 | yes |
| message passing | without_gene | +0.0165 | -0.0003 | yes |
| message passing | without_gene_derived | +0.0150 | -0.0016 | yes |
| message passing | without_protein | +0.0168 | +0.0247 | yes; the rule picks it |
| linear response | plain (b3_linear_response_cofactors_descriptors_brain) | -0.0007 | | |
| linear response | seed_masked | +0.0019 | -0.0095 | yes |
| linear response | zero_init_slow | +0.0072 | +0.0084 | yes |
| linear response | without_gene | +0.0093 | -0.0063 | yes |
| linear response | without_gene_derived | +0.0157 | -0.0047 | yes; the rule picks it |
| linear response | without_protein | -0.0030 | +0.0047 | no (reliance below plain) |

What the readings support. Every arm moves graph reliance by 0.01 to 0.02, against standard deviations over folds of
about 0.02 (docs/generated/graph_reliance.md, one rewiring seed), so the order among arms is not resolved. In the message-passing
encoder without_protein leads without_gene by 0.0003 in reliance, a tie; it is also the only arm with a clear AUPRC
gain over the plain arm (micro +0.043 pooled, 95 percent interval +0.021 to +0.063; macro +0.018, -0.002 to +0.036),
and against b3_typed_nodes without descriptors it gains +0.021 macro pooled (+0.005 to +0.039). In the linear-response
encoder without_gene_derived leads without_gene by 0.006 in reliance and costs -0.005 on the six-difference mean. The
slice holds gene seeds only, so a block's effect on drug perturbations is not measured. If applied, the
message-passing configurations would add --drop-descriptor-blocks protein and the linear-response configurations
--drop-descriptor-blocks protein gene_brain reaction_brain; the latter takes the reaction_brain block out, so for
linear response the rewired reaction expression of H2 would recompute only the reactions' cell-class weights.

The user's decision, 8 October 2026: no arm that drops the protein block ("Which means don't drop proteins", after "the
point of this project is [not] just to predict the symptoms from a pathways graph. It's to be able to use the graph to
determine what the pathways for symptoms are"). Every block arm drops the protein block, so neither rule pick is applied.
The protein block is the 65 columns derived from ESM-2 embeddings that the gene nodes carry (12,643 of 12,810 gene nodes
of graph_full_neuronal; the 1,681 protein_entity nodes carry no descriptor). No arm removes a node or an edge, so under
every arm the modules can name the same genes. Restricted to the arms that keep every block (plain, seed_masked,
zero_init_slow), the rule picks seed_masked for message passing (reliance +0.0149, mean of six differences +0.0032) and
zero_init_slow for linear response (+0.0072, +0.0084). seed_masked hides the descriptors only at each perturbation's
seed nodes, which are gene nodes for gene and drug perturbations alike (evidence_full_v2); every other gene keeps its
protein block. Against the unrestricted message-passing pick, seed_masked keeps most of the reliance (0.0149 against
0.0168, inside one fold standard deviation) and gives up the AUPRC gain (six-difference mean +0.0032 against +0.0247).
Not applied: the restricted picks wait for the user's confirmation; until then the confirmatory_v2 configurations keep
the plain treatment.

Amendment, 8 October 2026, before any lockbox run (the user's decisions): the test, the micro floor, a no-descriptor
branch and graph paring.
-  Test. **Two models, not four** (corrected 15 October 2026: the head decision below drops the sigmoid configurations,
  so this bullet's four-model arithmetic and its 0.096 bound describe a model set that no longer exists; with two tested
  models the chance that one passes by luck is at most 0.05, as the head amendment states; from 22 October 2026 one
  model is tested, at one-sided 0.05, items 34b and 34c). Each tested model is a candidate and is tested on its own at
  one-sided 0.025: H1 first, and H2 only if that model's H1 is confirmed, at the same level. Holm's procedure over the
  eight hypotheses is withdrawn; nothing is divided across models. Consequence, stated beside the results by
  experiments/score_confirmatory.py: with four models and no correction across them, the chance that at least one is
  confirmed by luck is above 0.025, at most 1 - 0.975^4 = 0.096 if the four were independent and less since they share
  the data, the lockbox and the baselines.
- Floors. The macro difference must be at least 0.041 and the micro difference at least 0.028, the median projected
  95 percent half-widths of a macro and a micro difference on a 20 percent hold-out (the precision statement above). The
  first version of this amendment kept the macro floor at 0.05; the user moved it to 0.041 the same day, before any
  lockbox run, so that both floors are the same kind of bar: what the lockbox can detect, not a judged smallest effect
  worth having (a micro difference is the less noisy of the two, so one value of 0.05 would have been a different bar for
  each). At one-sided 0.025 a difference at its floor has a 95 percent interval that just reaches zero
  when the realised width equals the projection, so a floor binds only when the lockbox interval comes out narrower than
  projected and the floors add little to the significance test; the effect sizes and intervals reported next to every
  decision carry the question of size. With Holm withdrawn, the 0.06 and 0.04 of the precision statement (Holm's smallest
  level) no longer apply: at one-sided 0.025 the smallest differences the lockbox can confirm are near the half-widths.
- Ablation branch. The four configurations without --node-descriptors (confirmatory_*_without_descriptors in
  experiments/run_main_model_batch.py) are an ablation, run as development pilots (runs/full/ablation_pilots_without_descriptors.sh)
  and reported against the descriptor configurations; they are not among the tested models.
- Graph paring. Pared graph variants are tested on the development set only if the development pilots do not beat the
  development baselines. After the lockbox has been scored a pared graph can only be an exploratory result, because the
  lockbox is not scored twice.

Amendment, 8 October 2026, before any lockbox run: the early-stopping validation set (a defect found by diagnostics of
the development pilots; the user allowed a change of the stopping rule the same day, if needed and if differences in
fold prevalence could be shown not to interfere).
- Defect. The trainer takes as its early-stopping validation set fold 0 of a grouped split of the training pool into
  seven folds, and assign_grouped_folds places the largest group first, in fold 0. With the lockbox removed the
  development data hold one leakage group of 232 of 1,222 perturbations (disease_cluster_and_targets joins 169 genes and
  63 drugs through shared disease clusters and drug targets). It holds 27 percent of the development positives and 61 to
  100 percent of the positives of seven symptoms (abnormal dreams, decreased libido, elevated mood or mania, insomnia,
  psychomotor retardation, somnolence or hypersomnia, suicidality). A lockbox run's training pool is every development
  perturbation, so for every seed its validation set would have been that group alone and no confirmatory model would
  have trained on it, while the baselines do. Development folds 1 to 4 do the same. Development fold 0, where the pilots
  ran, has the group as its test set, so the pilots were not affected; their test fold is atypical for the same reason
  (rich in drugs and in those seven symptoms), and the development baselines are compared on that fold.
- Change. The eight configurations of the confirmatory family (the four tested models and the four ablations) add
  --keep-large-groups-in-training (experiments/run_main_model.py, early_stopping_validation): a group larger than half
  the expected validation set (0.15 x pool / 2, 92 perturbations in a lockbox run) stays in training and the seven folds
  are drawn over the other groups. In a lockbox run this gives 1,080 training and 142 validation perturbations, the
  largest validation group 58 and 14.5 to 16.1 percent of the positives in validation (seeds 0 to 4), against 990, 232, 232
  and 27 percent. On development fold 0 the split is identical (no group in that pool exceeds 73), so the four pilots
  stand for the amended configurations. Other runs keep the earlier split; on the slice the largest group (27
  perturbations) is about half of each validation set but holds 14 percent of the positives.
- Precision unchanged. The lockbox is unchanged (configs/lockbox_v1.json, 317 perturbations); what shrank is the
  validation set, which is drawn from the development perturbations and scored for no hypothesis. The precision
  statement's five 20 percent folds were drawn over all 1,539 perturbations, and its fold 0 holds the group of 232 (548
  kept positive pairs and 20 scorable symptoms, the most of any fold). The lockbox cannot hold that group, since the
  group lies wholly in the development data, so the four folds without it are the closer match: their medians are 0.040
  macro (range 0.021 to 0.063) and 0.027 micro (0.018 to 0.038) over twelve baseline-pair readings, against 0.041 and
  0.028 over all fifteen. The floors stay at 0.041 and 0.028.
- The stopping metric stays the validation loss. Validation macro AUPRC was considered and not adopted. (i) Not needed:
  the message-passing sigmoid pilot, which the loss stopped at epoch 0, scores macro 0.142 and micro 0.233 on its
  development test at its last state (epoch 8), against 0.131 and 0.257 at the selected state. (ii) Too noisy to choose
  an epoch: on its 140 validation perturbations the paired 95 percent bootstrap interval of the validation macro AUPRC
  difference between those two states is [-0.052, +0.047], wider than the range of validation macro AUPRC over all nine
  epochs (0.036). (iii) Prevalence does interfere. Within a fold every epoch is scored on the same validation
  perturbations, so a symptom's validation prevalence sets the same chance level for every epoch and cancels from the
  comparison, and a per-symptom AUPRC depends only on the ranking within the symptom, so learning a base rate does not
  move it. But prevalence decides which symptoms the validation set can score at all (five positives): 12 on fold 0
  against 18 on its test set, 10 in common, and 11 or 12 in a lockbox run under the amended split. An AUPRC rule would
  stop on a symptom set that leaves out about a third of what the test scores; the loss counts every labelled pair.

Amendment, 8 October 2026, before any lockbox run (the user's objection the same day: the baselines fit on every
development perturbation while the models leave out their early-stopping validation set, so a null result would be
less meaningful): refit after early stopping.
- The eight configurations of the confirmatory family add --refit-on-validation (experiments/run_main_model.py). The
  early-stopping run on the validation set (142 perturbations in a lockbox run) only chooses the number of epochs; a
  fresh model built from the run's seed is then trained on the training and validation perturbations together (all
  1,222 development perturbations in a lockbox run, 977 in a development pilot) for best epoch + 1 epochs, and its test
  predictions are the ones scored. The baselines fit on the same perturbations, so models and baselines now fit on the
  same rows; before, the models fitted on 1,080 of 1,222 (12 percent fewer), which biased a comparison against them and
  would have made a null result partly a cost of the held-out data. This is the second-pass strategy of Goodfellow,
  Bengio and Courville (Deep Learning, 2016, section 7.8, algorithm 7.2). The refit keeps the number of epochs, not the
  number of optimizer steps (each refit epoch has about 13 percent more steps), a choice that book leaves open; the
  overfitting early stopping guards against comes from repeated passes over the same perturbations.
- Permuted-label and rewired-graph runs are refitted the same way, on their own labels and graph. The early-stopped
  model's test predictions are kept (test_predictions_early_stopped.npy) and are not scored. experiments/score_confirmatory.py
  accepts a lockbox run only if it carries the refit and --keep-large-groups-in-training.
- The four development pilots are refitted from their stored early-stopping checkpoints (runs/full/refit_pilots.sh;
  a run that finished without the refit gets only the refit on resume) and reported against the development baselines
  on fold 0 beside their early-stopped scores. The ablation pilots carry the flag from the start.
- Checks on the slice (linear-response encoder, sigmoid head, fold 0, three epochs): a refit interrupted mid-epoch and
  resumed gives the same test predictions as one run straight through (largest difference 0), and so does a refit
  added on resume to a run that had finished without one.
- Cost: best epoch + 1 more epochs per run.

Amendment, 8 October 2026, before any lockbox run: fixes from a code review of the study (the user's request the same
day). Each is a defect against text already in this specification, not a change of the test.
- The TransE baseline is now seeded by --seed (experiments/run_baselines.py); before, every seed fitted the same TransE,
  although experiments/score_confirmatory.py describes the seed as setting its initialisation. Seed 0 is unchanged, so
  the development baselines stand.
- The models' subsystem and module hold-outs run on the development perturbations (--lockbox without --score-lockbox);
  the trainer refused that combination, so the secondary subsystem reading of the models could not run without the
  lockbox perturbations.
- The popularity and degree-scaled popularity baselines take their base rates over the labelled pairs only
  (mechanistic_pathway_learning/models/baselines/popularity_baseline.py). They counted a positive pair the selection set
  aside as a negative, while this specification, the trainer's loss and its leak initialisation treat it as neither.
  Within a symptom (and within a degree stratum) these baselines rank by degree alone, so macro AUPRC and both
  within-strata readings are unchanged; the pooled micro ranking changes, by -0.012 to +0.006 in per-fold micro AUPRC on
  the five development folds (a check run during the review, development rows only).
- read_lockbox also refuses data loaded with another --group-by or another evidence table than the lockbox was drawn on
  (it caught only groups straddling the lockbox, which a finer grouping never does).
- The pathway-wise hold-outs (the secondary subsystem reading, and the curated modules) leave out of each fit the
  perturbations that share a leakage group with a held-out one; they select perturbations by seed gene, so a held-out
  gene's disease-cluster or drug-target partner trained with its labels. On the development set five of the six
  qualifying subsystems have such partners (227 to 343 perturbations, mostly cluster:ABCA3); the lockbox holds whole
  groups and the grouped folds are drawn by group, so neither changes. The --min-holdout-positives filter counts kept
  positive pairs (it counted every positive, so hold-outs qualified on pairs that are never scored): on the development
  set 6 subsystems qualify instead of 21, and no curated module reaches 10 kept positives (the largest has 9).
- A resumed run now trains as an uninterrupted one does (experiments/run_main_model.py). Before: the epoch order was
  reseeded with seed + epoch on resume, where an uninterrupted run draws it from one generator; the torch generator
  behind the noisy-OR gate noise restarted; a checkpoint written in the middle of an epoch restarted that epoch from
  its first batch with a new order, after its first batches had already been applied (a checkpoint on the last batch
  of an epoch trained that epoch twice); and without the refit a crash after early stopping trained further epochs on
  resume. The checkpoint now holds both generators' states and, mid-epoch, the epoch's order, the next batch and the
  partial sums; a run that stopped early is marked finished. Checkpoints are written to a temporary file and renamed.
  On a toy graph (52 perturbations; both heads; resume at an epoch boundary, a mid-epoch interrupt, an interrupt on an
  epoch's last batch, a crash while scoring) every resumed run gives the test predictions of the uninterrupted run
  (largest difference 0), and an uninterrupted run gives the predictions of the code before the change. Runs that
  resumed under the old code keep their results; their test scores are what that run trained to, not what a run from
  scratch would give (the two finished development sigmoid pilots resumed at end-of-epoch checkpoints, their optimizer
  step counts show no batch trained twice).
- A checkpoint now records the training arguments and digests of the loaded inputs (labels, weights, label mask,
  edges, seeds, and the descriptor, cell-class and laboratory files). A resume under other arguments or inputs prints a
  warning and lists the changes in the run's code provenance. A resume does not refuse such a checkpoint, because the
  refit and a longer --max-epochs are legitimate changes on resume and are left out of the comparison. A resume also
  warns when the message-passing node features restored from the checkpoint differ from those built from the current
  files. Before, the split signature covered only the split and the controls. On the toy graph an uninterrupted run
  gives the predictions of the code before the change, and checkpoints written before it resume without a warning.
- With --positive-target-from-frequency (the slice configuration b6_frequency_target only), the early-stopping
  validation loss now uses the frequency targets of the training loss. Before, it scored every positive against 0.99
  under the frequency mode's weights. No confirmatory configuration uses the flag.
- experiments/score_confirmatory.py refuses a run whose predictions are not finite or not one row per lockbox
  perturbation and one column per symptom, whose symptom list differs from the data's, or (rewired variant) whose
  rewiring used another number of swaps per edge than 50; before, a NaN score ranked as the lowest. If a run is missing
  or refused it writes nothing, so a failed run can be resumed without spending the single scoring
  (--allow-incomplete scores with that model not confirmed, only on the user's decision). The scoring record holds the
  git status beside the commit. The scorer also refuses a run whose recorded trainer arguments differ from those its
  configuration in run_main_model_batch.py gives (the resume controls and the variant's own arguments aside), whose
  graph, evidence, descriptor or cell-class file hashes differ from the files being scored, or (permuted variant) whose
  permutation differs from the scorer's draw for that seed. The trainer now records the graph and evidence file hashes
  and a digest of its permutation in results.json. Before, only the baselines' permutation was checked, and nothing
  tied a run to its configuration or to the graph and evidence it read.
- Per-symptom AUPRC is undefined without a positive: per_symptom_auprc returns NaN there, where scikit-learn 1.9
  returns 0, so the per-symptom bootstrap intervals (secondary readings) leave such resamples out instead of scoring
  them 0. The confirmatory scorer computes its own AUPRC, which already left them out.
- Open, for the user's decision: the training loss takes the logarithms of P clamped to [1e-6, 1 - 1e-6]
  (mechanistic_pathway_learning/models/soft_constraint_losses.py), so a pair beyond the clamp has a constant loss and
  no gradient: a positive the sigmoid head scores below logit -13.8 cannot be pulled back, and the validation loss that
  stops training caps it. In the fold-0 development pilots 3.7 percent (message passing) and 1.2 percent (linear
  response) of the sigmoid heads' test probabilities are below 1e-6, among them 13 and 3 labelled positives; on the slice
  0.5 and 0.04 percent. --bce-in-log-space computes both losses from the heads' log P and log(1 - P) (log-sigmoid of the
  logits; for the noisy-OR head the log(1 - P) it already forms); it is off by default, which reproduces every earlier
  run bit for bit (checked on a toy graph for both heads). Whether the confirmatory configurations take it, which would
  need new development pilots of the configurations that change, is the user's decision.
- Decided by the user on 8 October 2026 (amendment below, symmetric rewiring adopted): the rewiring of H2 swaps every stored edge within its relation on its own. binds is
  undirected and stored in both directions (30,682 of its 31,118 edges have their reverse in graph_full_neuronal), and
  after 50 swaps per edge 1,664 do: the null graph keeps every in- and out-degree per relation but not the symmetry,
  so the real-minus-rewired difference also measures the loss of reciprocity. --keep-reciprocated-relations-symmetric
  (trainer and experiments/evaluate_on_rewired_graph.py; negative_controls.reciprocated_relations) rewires a relation
  stored in both directions as undirected edges, by undirected double-edge swaps written back in both directions, the
  treatment Maslov and Sneppen gave undirected networks; on the full graph it keeps all 30,682 reverse pairs, every
  per-relation degree, no duplicate or self-loop, and leaves 0.45 percent of edges unchanged (32 seconds). It is off by
  default, which reproduces every rewired run so far. Not covered by it: a reversible reaction's substrate_of and
  product_of edges between the same metabolite and reaction (15,867 pairs) are two relations and still move apart.
- Decided by the user on 8 October 2026 (amendment below, recomputed from the rewired wiring): a rewired run keeps node features computed from the real gene-reaction associations
  (the reaction_brain descriptor block and the reactions' cell-class weights come from the Human-GEM gene rules), so a
  model trained on the rewired graph still sees which genes catalyse each reaction through its features. This makes
  the rewiring difference of H2 smaller than the wiring's whole contribution: it can cost H2 power, not make it
  confirm wrongly. The alternatives are recomputing those blocks from the rewired catalyzed_by edges, or stating it as a
  limitation.
- The random walk's rewiring control is corrected. The walk merges the relations into one undirected graph with each
  pair once; rewiring the stored directed edges per relation moves apart two edges joining one pair (binds both ways, a
  reversible reaction's two edges), so the walk's rewired graph was denser than its real one (slice: 112,920 adjacency
  entries against about 135,000). --rewiring-method walk_graph (experiments/run_baselines.py and
  experiments/run_rewiring_null_distribution.py; negative_controls.rewire_walk_graph) rewires the walk's own graph so
  every node keeps its number of neighbours. The development reading that the slice wiring carries signal for the walk
  (docs/generated/rewiring_null_distribution.md, 0 of 20 rewirings as good as the real graph, p = 0.048) used the old null. Rerun
  with the new one (docs/generated/rewiring_null_distribution_walk_graph.md), the 20 rewirings give 0.264 ± 0.011 (best 0.285)
  against 0.293 on the real graph, again none as good (p = 0.048), so the reading stands. No confirmatory reading uses
  the walk's rewiring.
  Added 27 October 2026: the numbers in this bullet (0.264, 0.285, 0.293, p = 0.048) are finding 8 of
  `docs/research_summary.md`, measured on 7 and 8 October 2026 on the metabolic slice `data/processed/graph`. The owner
  ruled on 27 October 2026 that every number of that period is not evidence going forward ("ANY numbers from that time
  are to have the same treatment"). The correction of the null itself (`--rewiring-method walk_graph`) is a code fix
  and stands; "the reading stands" is history. Not a registered-rules change, so no `Amends:` trailer.
- The grade-shuffle and peripheral-event controls the skeleton lists under negative controls (design section 6.3)
  were never implemented and are not run; the confirmatory test has the two controls of its specification (permuted
  labels, a secondary reading, and the rewired graph of H2). The peripheral-event control needs adverse events without
  a plausible central mechanism, which the symptom set (central symptoms only) does not hold; a grade shuffle under the
  better_v1 selection would permute the weights of the kept positives only. configs/evaluation.yaml says so, and now
  states that the preregistration supersedes its endpoint and correction entries.
- Disclosed and left as they are. Changing any of them would change the evidence table or the graph, which confirmatory
  jobs read. Each can move the absolute scores of models and baselines alike. None of the counts below reads a lockbox
  outcome: lockbox-side counts use membership, seeds and disease identifiers only.
  - Disease entries annotated to 20 or more genes do not link those genes into one disease cluster
    (assemble_evidence_table.py; design open question 11). Seven entries are excluded this way (ORPHA:442835 with 49
    genes, ORPHA:154 with 45, and others). Such an entry gives every listed gene the same phenotype annotations, so two
    genes in different leakage groups can share labels through it. 29 of the 253 lockbox genes share such an entry with
    a development gene. In the five development folds, 107 test-fold gene kept positives are supported only by such
    entries, and the same entry gives a training gene the same kept positive. The direction of the effect on the
    model-minus-baseline difference is not known.
  - A drug action of type modulator, substrate or other has sign 0 (perturbation/map_drug_targets_to_graph_nodes.py).
    The linear-response encoder's input is sign times magnitude, so for that encoder gabapentin (CID100003446),
    pregabalin (CID100125889) and brivaracetam (RXCUI:1739745) give a field of exactly zero, the same as no
    perturbation. All three are development drugs: gabapentin has 17 positive pairs (12 kept), pregabalin 16 (none kept)
    and brivaracetam 3 (none kept). No lockbox perturbation has an all-zero input. The message-passing encoder still
    sees them, because its injection layer has a bias. The trainer now prints a warning that lists such perturbations.
  - evidence_full_v2 placed drug seeds on graph_full, not on graph_full_neuronal, which the models read. Every seed is a
    node of both. Thirty drugs, all in development, are seeded on fewer target genes than graph_full_neuronal holds, with
    their magnitudes renormalised over the targets present. For example, 21 GABA-A modulators miss GABRG3, the NMDA
    blockers miss GRIN3B, the gabapentinoids miss CACNA2D2 and CACNG4, and amifampridine misses several potassium
    channels. Nine genes that exist only in graph_full_neuronal (AFG3L2, CLCA4, CLCNKB, COX18, FOXRED1, KCNC2, KCNH5,
    NDUFAF4 and UQCC2) have annotations to crosswalk symptoms but are not perturbations. No gene perturbation sits on a
    node that exists only in graph_full_neuronal, so the leakage grouping is unaffected.
  - Every gene perturbation has sign -1 (loss of function), but grade A accepts Orphanet associations marked gain of
    function. In development, 10 of 1,144 gene perturbations (19 of 1,515 kept gene pairs) have only gain-of-function
    causal associations, so the signed encoder reads the wrong sign for them.
  - The symptom columns come from all perturbations. Catatonia is a column only because one lockbox perturbation has a
    set-aside catatonia pair; development holds no catatonia row. Catatonia is not scored (no kept positive). The
    development micro AUPRC of run_main_model.py, run_baselines.py, the aggregation and the twin comparisons ranks all 22
    columns, while the confirmatory micro AUPRC ranks the 20 scored symptoms.
  - Grade C pairs (human association) are not labels in this specification. They count as negatives in scoring and as
    weak negatives in training (159 such pairs among development perturbations). The positive pairs that the selection
    sets aside are masked instead. Masking grade C pairs in the same way would need an amendment; the user decided it on 8 October 2026 (amendment below, better_v2).
  - A drug pair's label frequency, which the selection compares with 1 percent, is the largest over the pair's preferred
    terms of the mean treatment-arm frequency midpoint of that term's SIDER reports
    (assemble_evidence_table.pharmacological_label_frequency). Post-marketing and rare reports (midpoint 0.0005) lower
    the mean, so 6 development drug pairs are set aside although one of their reports is at least 1 percent. The
    selection entry above does not define the frequency; this is the definition the selection file was built with.
- Decided by the user on 8 October 2026 (second amendment below, lockbox_v2): the lockbox draw over-samples drugs (experiments/draw_lockbox.py draw_groups). Each
  stratum's target is 20 percent of the sizes of all its groups, including cluster:ABCA3 (232 perturbations), which stays
  in development for its size. In the stratum of groups holding a drug with a kept positive, the drawable groups summed
  to less than that target, so all of them went into the lockbox. The lockbox therefore holds 64 of the 142 drugs (45
  percent) and 27 of the 61 drugs with a kept positive (44 percent), not 20 percent. All 34 development drugs with a
  kept positive (215 kept positives) are in cluster:ABCA3. Consequences:
  - The development folds put ABCA3 whole into one test fold, so no development reading trains on drug positives and
    then tests on drug positives.
  - In lockbox runs ABCA3 is in training, and the validation set holds no drug kept positive.
  - The lockbox's drug predictions extrapolate from the drug labels of one leakage group.
  The draw does not leak labels. The options are:
  - keep the lockbox and state this as a limitation;
  - return a seeded subset of the lockbox's drug-stratum groups to development, which only removes lockbox members, so
    the precision estimate is recomputed;
  - redraw the lockbox. This is not recommended, because development perturbations that pilots and the descriptor
    decisions have used would enter it.
  A future draw should leave excluded groups out of the target.
- Decided by the user on 8 October 2026 (amendment below, rotated and stratified): the early-stopping validation set is the same in every seed. assign_grouped_folds sorts
  groups largest first and breaks ties toward fold 0, and validation is fold 0, so the seed only reorders groups of
  equal size. For seeds 0 to 4 it is cluster:ARNT2 (58 perturbations) plus 84 single perturbations, with no drug kept
  positive. ARNT2 holds 10.5 percent of the development kept positives, among them 19 of 51 apathy and 15 of 50
  disinhibition positives. After the refit the scored model trains on ARNT2, but every seed's number of epochs is
  chosen on this one set, so the seed variance leaves out the variance from the choice of validation set. Rotating the
  validation fold with the seed (fold = seed mod 7) leaves seed 0, and so the development pilots, unchanged.
- Decided by the user on 8 October 2026 (amendment below, the group bootstrap decides): the scorer's paired bootstrap resamples lockbox perturbations one by one. Perturbations
  of one leakage group share disease annotations or targets, so their scores co-vary, and a bootstrap of single
  perturbations understates the variance. A check on development rows only drew 10 pseudo-lockboxes by the lockbox rule
  from the 1,222 development perturbations (257 to 299 perturbations each), fitted the baselines on the rest, and
  bootstrapped the three baseline-minus-baseline differences under the scorer's macro and micro statistics (1,000
  resamples). Median 95 percent half-widths:
  - resampling perturbations: 0.030 (macro) and 0.028 (micro);
  - resampling whole groups: 0.037 and 0.047 (median ratios 1.23 and 1.76).
  Seven of the ten pseudo-lockboxes hold a group of 50 to 58 perturbations. The lockbox's largest group has 13, and 210
  of its 237 groups are single perturbations. On the three pseudo-lockboxes whose largest group has at most 16
  perturbations, the half-widths are 0.024 and 0.025 resampling perturbations, against 0.027 and 0.038 resampling groups
  (ratios 1.18 and 1.31).
  The floors (0.041 and 0.028) were estimated with symptoms chosen again in each fold and micro AUPRC over all columns.
  Under the scorer's statistics, resampling single perturbations gives half-widths at or below both floors. Resampling
  groups gives a micro half-width above the micro floor (0.047, or 0.038 on the three lockbox-like pseudo-lockboxes),
  and the scorer's p-values are smaller than a group bootstrap would give. The alternative is a bootstrap over the
  lockbox's 237 leakage groups, either for the confirmatory p-values or as a sensitivity reading beside them.
  Resampling whole groups keeps the dependence inside a group; Field and Welsh (2007) show that "the cluster bootstrap
  gives consistent estimates under both the transformation and the random-effect model" of clustered data.
- Open, for the user's decision: no confirmatory baseline is fitted per perturbation type. Over labelled development
  pairs the base rate is 0.159 for drugs and 0.063 for genes, higher for drugs on 16 of 22 symptoms, and the lockbox
  holds 64 drugs of 317 against 78 of 1,222 in development. A predictor that knows only whether a perturbation is a drug
  therefore earns a share of every reading. experiments/measure_perturbation_type_offset.py (docs/generated/perturbation_type_offset.md)
  draws 200 pseudo-lockboxes of 39 drugs and 154 genes from the development set, fits the predictors on the rest and
  scores the four H1 readings as the scorer does. Against the better of popularity and degree_popularity in each draw
  (mean, 2.5 and 97.5 percentiles):
  - type_popularity (per-symptom base rate of the perturbation's type): macro -0.034 [-0.064, -0.002], micro +0.059
    [+0.018, +0.091], macro within degree strata +0.057 [+0.017, +0.096], micro within degree strata +0.034 [+0.009, +0.064];
  - type_degree_popularity (the same times log(1 + degree)): +0.033 [+0.013, +0.058], +0.087 [+0.044, +0.129], +0.021
    [-0.004, +0.048] and +0.013 [+0.000, +0.027].
  Degree strata do not separate the types: the top stratum holds 58 development drugs and 173 genes. Neither graph-free
  predictor passes H1 on its own, but each reaches the micro floor (0.028) and one reaches the macro floor (0.041) inside
  strata, so a model that learns the type offset beside a weak graph signal can pass H1 against these two baselines. The
  random walk and TransE were not drawn (each needs the full graph per draw), so whether either already carries the
  offset is open. The fold-0 development pilots show the effect in reverse: that test fold holds 63 of the 78 development
  drugs, the 15 training drugs have lower base rates than the genes, and the message-passing sigmoid pilot's macro
  AUROC is 0.343 over all test perturbations against 0.409 and 0.457 inside genes and drugs (type_popularity scores 0.336
  on that fold); the linear-response sigmoid pilot reads 0.671 overall against 0.482 and 0.538 inside the types. The
  options are:
  - add type_popularity and type_degree_popularity to the baselines the best baseline of a reading is chosen from (graph
    free, fitted on the development set like popularity), so that the type offset no longer counts toward H1;
  - score the four readings inside perturbation type as well (degree strata crossed with type), as further H1 readings
    or as secondary readings;
  - keep the baselines and state the offset as a limitation.
  The first is cheap and leaves the models untouched; it changes the decision rule, so it is the user's decision.
  run_baselines.py --with-type-popularity fits the two predictors (off by default, so no run so far and none registered
  changes); the scorer uses them only when its --baselines names them.

Amendment, 8 October 2026, before any lockbox run (the user's decisions late the same day on the open items above). It
defines a second confirmatory family (confirmatory_v2_* in experiments/run_main_model_batch.py). The running development
pilots of the first family stay as they are and are reported as checks that each configuration trains.
- Grade C pairs are masked. experiments/build_label_selection.py --mask-grades C writes better_v2_full_v2: its positive
  rows equal better_v1's, and each pair whose only evidence is grade C (a human association) gets a row with keep False
  and masks_a_negative True, which load_experiment_data reads as neither positive nor negative. It masks 172 such pairs
  of the loaded data, 159 of them among the development perturbations of lockbox_v1; before, they were negatives in
  scoring and weak negatives in training.
- The early-stopping validation set rotates with the seed. run_main_model.py --validation-draw rotated_stratified
  splits the training pool once into round(1 / 0.15) = 7 grouped folds with a fixed partition seed, separately for
  groups holding a drug and the rest (the second stratum's folds offset by one, so the largest group of each stratum
  does not share a fold), and validates on fold seed mod 7, so seeds 0 to 4 stop on five disjoint validation sets. Groups
  larger than a quarter of the expected validation set stay in training (half before). On the lockbox_v1 development
  set as a lockbox run's pool, this gives validation sets of 125 to 128 perturbations whose largest group has 9 to 16
  members, holding 7.1 to 8.8 percent of the development kept positives (123 to 153) and 8 to 11 symptoms with five
  or more; the fold-0 draw gave 142 perturbations with cluster:ARNT2 (58) in every seed and 14.5 to 16.1 percent of the
  positives. The cost: the three largest groups (232, 58 and 50 perturbations, which hold a large share of the positives)
  never validate, so each validation set carries about half the positives of the fold-0 draw and its loss is noisier.
  The epoch count still comes from the validation loss, and the refit trains on every development perturbation.
- The confirmatory p-values and intervals come from a paired bootstrap over the lockbox's leakage groups
  (score_confirmatory.py --bootstrap-unit group: whole groups drawn with replacement). The bootstrap over single
  perturbations is reported beside it as a sensitivity reading. Field and Welsh (2007) give the reason quoted in the
  open item above.
- H2's rewiring keeps the relations stored in both directions symmetric (--keep-reciprocated-relations-symmetric), and
  a rewired run recomputes its reactions' expression from its wiring (--recompute-reaction-expression-on-rewired-graph,
  mechanistic_pathway_learning/graph/rewired_expression_features.py). The user asked why the rewired runs should keep
  descriptors derived from the real graph; they should not. Each reaction's gene rule is rewritten onto its rewired
  catalysts (a kept catalyst maps to itself, the others pair in node order; and/or structure kept), and the
  reaction_brain descriptor block and the reactions' cell-class weights are recomputed from the rewritten rules with
  the functions that built them, from the expression tables of experiments/write_expression_tables.py. With the real
  rules those tables reproduce the stored reaction rows exactly (largest difference 0). Intrinsic node properties
  (protein embeddings, metabolite and reaction chemistry, a gene's own expression) stay, since the rewiring moves edges,
  not nodes. They still carry some of the wiring (a protein's embedding predicts some of its partners), which can only
  make the rewired model better and the rewiring difference smaller, so it can cost H2 power but not confirm it
  wrongly. The scorer refuses a rewired run without either flag. runs/full/confirmatory_lockbox.sh passes both.
-  Two tested models instead of four (one from 22 October 2026, item 34b): one head per encoder, chosen on the
  development set before any lockbox run by experiments/choose_heads.py, written before any run it reads existed. For
  each encoder, the noisy-OR and the sigmoid configuration run on the five grouped development folds with seed 0, and so
  do the development baselines. Per fold, the four H1 readings are computed as the scorer computes them on the lockbox,
  each against the best baseline of that reading (the highest five-fold mean, chosen without reference to any model). A
  head's margin is the smallest of: the mean macro difference minus the macro floor, the mean micro difference minus the
  micro floor (0.032 and 0.043, the amendment below) and the two mean within-strata differences. The head with the
  larger margin is tested; margins within 0.001 choose noisy-OR. The other two configurations and the four without
  descriptors stay development readings. With two models tested at one-sided 0.025 each, the chance that at least one
  passes by luck is at most 2 x 0.025 = 0.05 whatever the dependence between the two tests (0.049 if they were
  independent), against at most 0.10 (0.096) with four. The choice reads development folds only, so it does not bias the
  lockbox test of the model it picks.
- Still open: the lockbox's drug share (the user asked for the precision estimate first; a draft that returns lockbox
  drug groups to development until the lockbox holds 20 percent of the drugs and moves unread development gene groups
  in is kept outside the repository and registers nothing), --bce-in-log-space, the per-type popularity baselines and
  the secondary contrasts. The second family's development runs wait for the lockbox decision, because the lockbox
  decides which perturbations are development.

Amendment, 8 October 2026, later the same day, before any lockbox run: the lockbox and the floors (the user's
decisions, after the precision estimate they asked for).
- Lockbox. The confirmatory test scores configs/lockbox_v2.json, derived from lockbox_v1 by experiments/rebalance_lockbox.py
  (its docstring states the rule, written before it was run; seed 20261009). Step 1: lockbox groups holding a drug, in a
  seeded order, return to development while the lockbox keeps at least round(0.2 x 142) = 28 drugs. Step 2: development
  groups with no drug and no perturbation in the fold-0 test or early-stopping validation set of the development pilots
  or in the slice evidence (396 eligible groups, 435 perturbations), in a seeded order, enter until the lockbox holds 317
  perturbations again. Nine groups returned (CHEMBL2023, CHEMBL2094253, CHEMBL2094268, CHEMBL2095181, CHEMBL264 and the
  clusters of ABAT, ALDH5A1, SLC18A2 and SLC6A3) and 38 gene groups entered. lockbox_v2: 317 perturbations (289 genes, 28
  drugs, 11 of them with a kept positive), 266 leakage groups (245 single perturbations, largest 11), 397 kept positive
  pairs, 16 symptoms in the macro average. Development: 1,222 perturbations, 114 drugs, 50 of them with a kept positive
  (before: 78 and 34, all 34 in cluster:ABCA3), 1,814 kept positive pairs. No leakage group straddles the two sides and
  no lockbox perturbation shares a seed node with a development perturbation (checked on the file). The script
  reproduces the file exactly apart from its time stamp.
- What was known when it was derived. Membership, perturbation types and group sizes; the label counts the file records
  (they fix the macro symptoms, as in draw_lockbox.py), which the user saw with the precision estimate before deciding.
  No model output on a perturbation that enters the lockbox entered any decision: the entering genes were outside the
  fold-0 test and validation sets of the development pilots and outside the slice. They were training perturbations of
  the fold-0 development pilots (fitted, not scored) and rows of baseline-only readings: the pre-lockbox precision
  folds (drawn over all 1,539 perturbations, as were lockbox_v1's members), the pseudo-lockboxes of the group bootstrap
  check and those of the perturbation-type check. 85 perturbations of lockbox_v1 that stay are slice perturbations, as
  before. The drug groups that return were never read by a model either. The first family's development pilots trained
  on the entering genes, so they are not readings of the second family; the second family's development runs start
  fresh on the new development set.
- Precision estimate given to the user before the decision. Scaling the precision folds' half-widths (perturbation
  bootstrap) by the square root of the kept positive pairs gives 0.041 macro and 0.028 micro for lockbox_v2 (397) and
  about 0.037 and 0.026 for lockbox_v1 (481). The precision fold whose count is closest to lockbox_v1's (479) gives
  0.028 and 0.022 (3 readings of one fold), the three with 382 to 402 (like lockbox_v2) 0.042 and 0.029 (medians); the
  spread between folds is wider than the counts explain. Under the group bootstrap lockbox_v2, with
  more and smaller groups (266 groups, 245 of them single, against 237 and 210), was expected to come out between 11
  percent narrower and 10 percent wider than lockbox_v1. A lockbox_v1-shaped hold-out cannot be drawn from the
  development data, so the comparison is a projection.
- Floors, revised a third time the same day by the user, before any second-family run: each floor is computed in the
  single scoring from the lockbox itself. For each tested model and for the macro and the micro reading, the floor is
  the half-width of that difference's 95 percent interval under the deciding (group) bootstrap plus 0.005
  (experiments/score_confirmatory.py --floor-rule half_width_plus_margin --floor-margin 0.005, the defaults;
  model_floors). A difference that reaches its floor lies 0.005 above what the lockbox resolves for that comparison.
  For a symmetric bootstrap distribution this is the condition that the interval's lower end exceeds 0.005, so H1's
  macro and micro conditions become a test against a margin of 0.005 instead of zero; with a skewed distribution the
  two differ slightly, and the rule is the half-width form. The floor no longer depends on a projection, and it binds
  by 0.005 above the significance condition whatever width the lockbox gives. Nothing about the floors is computed
  before the scoring, so the blinding is unchanged. The projected floors below (0.032 and 0.043) remain the floors of
  the head choice, where no lockbox interval exists, and the scorer reports them beside the realised floors. Power is
  as stated below when the realised width equals the projected median.
-  **Floors, removed 15 October 2026, before any lockbox run** (the owner: "no floor. paired interval"). There is no
  magnitude bar. A model is confirmed for H1 when it is complete, its four direction conditions hold (macro, micro and
  both within-strata readings above zero, which is a sign condition and not a floor) and its H1 p-value is at or below
  one-sided 0.025 (0.05 from 22 October 2026, item 34c); H2 and P1 follow as already registered. `score_confirmatory.py
  --floor-rule none` is the default and `model_floors` returns minus infinity, so a NaN difference still fails because
  NaN is not at or above minus infinity. `half_width_plus_margin` and `fixed` stay in the code so an earlier reading can
  be reproduced, and neither is the registered rule. **Reason, in the owner's words across 15 October**: "why bother
  arguing an arbitrary setpoint for H1 at all?" and "i'm saying just report the effect size in multiples of the
  available precision". The floor had become nearly inert in any case - its own bullet above says a difference at its
  floor "lies 0.005 above what the lockbox resolves for that comparison", so it was the significance condition shifted
  by a chosen 0.005, and the 0.005 was the only content it added beyond the paired interval. **What carries the question
  of size instead**: the paired interval on `model - best baseline`, which already contains the baseline's instability
  because it is a paired difference, plus effect sizes reported in **standard errors** of the available precision, in
  two versions - a shared divisor, the largest median standard error over the closed registered baseline set and the
  tested models, which makes the two models comparable with each other and states that the effect exceeds any precision
  in the study; and a per-model divisor, each model against its own, which is what shows how well that particular effect
  is resolved. Neither version enters the decision. The deciding bootstrap resamples the five composite seeds and the
  leakage groups together, so the interval includes the seed variance that the precision statement above records as
  missing; the seeds remain joint (the owner: "i don't really care enough to separate them as individual confounds"), so
  the interval is honest about total variability and cannot attribute init against split.
- Projected floors. H1 needed a macro difference of at least 0.032 and a micro difference of at least 0.043 (the user's values):
  the median 95 percent half-width of a difference under the group bootstrap, which now decides, plus 0.005. The
  medians are measured under the scorer's statistics (macro symptoms fixed per hold-out, micro over the scored
  symptoms) on the three development pseudo-lockboxes shaped like the lockbox (largest group at most 16; the group
  bootstrap check above): 0.027 macro (range 0.015 to 0.095) and 0.038 micro (0.025 to 0.053) over nine readings, three
  baseline pairs each (popularity, degree_popularity and the random walk). The first version of this bullet, the same
  day, set 0.053 and 0.042 from a projection, the precision folds' medians (0.041 and 0.028) times the ratio of group to
  perturbation half-widths on those pseudo-lockboxes (1.18 and 1.31). The user asked why the macro floor was not the
  measured median plus 0.005, and it should be: the precision folds' macro bootstrap chooses the scored symptoms again
  in every resample (ranking_and_calibration_metrics.paired_bootstrap_macro_difference skips symptoms with fewer than
  five positives in a resample), so symptoms near the threshold drop in and out and widen the interval, while the
  scorer fixes the macro symptoms in the lockbox file. That earlier projection also stated wrongly that the precision
  folds included TransE; their fifteen readings are the same three pairs over five folds. The precision statement's
  0.041 shares this inflation. With a floor 0.005 above the median width, the floor binds whenever the realised interval
  is no wider than the median, so a difference must also reach a fixed size, not only exclude zero. Three caveats.
  - Nine readings from three pseudo-lockboxes, with a wide range for macro: the median is itself uncertain. If the
    lockbox's realised macro width is larger, the significance test, not the floor, decides H1's macro condition.
    lockbox_v2 averages 16 macro symptoms against 12 or 13 on the pseudo-lockboxes, which should narrow its macro
    interval somewhat. The pairs are baseline against baseline; a model and a baseline may co-vary less, which widens
    the interval.
  - Power. At the median widths (standard errors 0.027 / 1.96 = 0.014 macro and 0.038 / 1.96 = 0.019 micro), a model
    whose true differences equal the floors reaches each floor half the time; reaching a floor with probability 0.8
    needs a true difference near 0.032 + 0.84 x 0.014 = 0.044 macro and 0.043 + 0.84 x 0.019 = 0.059 micro, against
    0.039 and 0.054 for the significance test alone (2.80 standard errors), each on its own; H1 also needs both
    within-strata readings above zero.
  - The scores of the first family's fold-0 development pilots were visible when the floors moved. The floors follow
    from the measured widths by a fixed rule (plus 0.005), not from those scores, and no second-family run had started.
  experiments/score_confirmatory.py now defaults to lockbox_v2, better_v2_full_v2, the two configurations in
  configs/head_choice.json (refusing a choice made on another lockbox's development set), the floors above and baselines
  under runs/full/lockbox_v2_baselines (refusing baselines that scored another lockbox). experiments/choose_heads.py
  takes the same floors. The scorer's statement of the chance that a model passes by luck is now the bound that holds
  whatever the dependence (2 x 0.025 = 0.05 for two models).
- Rewired reaction expression on the full graph (timing check, 50 symmetric swaps per edge, seed 0, on the loaded
  4-core machine): 40 s for the rewiring and 708 s for the recomputation. 7,748 of the 7,759 reactions with a rule
  change rule; 23,410 rule genes are replaced, 347 of them by a catalyst without expression of its own; 8 rule genes
  without a catalyzed_by edge stay. reaction_brain_gtex_brain_max correlates 0.24 between the real and the rewired
  graph and changes on 56 percent of reaction rows; every other descriptor column is unchanged.
- Still open: --bce-in-log-space, the per-type popularity baselines, the secondary contrasts and --start-at-weighted-optimum
  (docs/records/2026-10/best_epoch_zero.md: on the first family's pilots the noisy-OR leaks stayed at the raw base rate, 0.061, against a
  loss-optimal constant of 0.204, and the modules supplied the difference; the sigmoid head reached the constant within
  the first epoch; no pilot's best validation loss fell below that of a constant per-symptom prediction). The second family's
  development runs (its four configurations on the five grouped development folds of lockbox_v2 with seed 0, and the
  development baselines; runs/full/v2_development.sh) start when the first family's pilots end; experiments/choose_heads.py
  reads them. On that development set every fold's early-stopping validation set (92 to 128 perturbations) holds drug
  kept positives except fold 4's. The first family's no-descriptor ablation pilots were retired before they trained
  anything; the second family's ablation runs the two chosen heads without descriptors on the same five folds after the
  head choice.

Amendment, 8 October 2026, before any second-family run (the user's decisions): the sigmoid head is dropped and the
modules are fixed first.
-  Head. "I guess we should drop the sigmoid head then". The tested models are the noisy-OR configurations of the two
  encoders, confirmatory_v2_message_passing_noisy_or and confirmatory_v2_linear_response_noisy_or (from 22 October 2026
  the linear-response configuration alone is tested and the message-passing one is a robustness reading, item 34b). No
  head is chosen on the development runs: experiments/choose_heads.py stays as a record and is not run.
  configs/head_choice.json records the two models as the user's decision, and the scorer and the lockbox job read it as
  before. With two tested models, the chance that one passes by luck stays at most 0.05. The second family's sigmoid
  configurations are not run. Reason (the user's statement of purpose that day, "It's to be able to use the graph to
  determine what the pathways for symptoms are"): only the noisy-OR head has modules that can be read as pathways.
- Order. "Unacceptable to start the v2 experiment runs yet until that is done. Ya. Fixing the modules first makes
  sense." The second family's development job (v2_development) was stopped before it trained anything and is paused.
  It runs only after the user decides the module fix. The module fix is developed on the slice under the rule of
  docs/module_health.md, written before its runs.
- The descriptor-treatment readings above come from slice arms with the sigmoid head (b3_*), so they bear on the
  noisy-OR head only indirectly.
- Leak start (the user, the same day: "Ya. Start at the optimum."). The second family's noisy-OR configurations and
  their no-descriptor ablations carry --start-at-weighted-optimum, so each leak starts at its symptom's loss-optimal
  constant and not at the raw base rate (docs/records/2026-10/best_epoch_zero.md). The slice runs of docs/module_health.md now say
  whether the leak start is enough or more of the fix is needed. The v2 runs still wait for that reading.
- Not decided: the descriptor treatments (the restricted picks above); where the descriptors
  sit (the user: "The genes shouldn't need descriptors but the proteins should"; in graph_full_neuronal a gene node
  stands for the gene and its product, and 11,723 of the 12,810 gene nodes take part in a protein-level relation, while
  the 1,681 protein_entity nodes are Reactome complexes and sets); the confirmatory pathway test (options and the
  decisions it needs: docs/records/2026-10/pathway_test_options.md).
- The user, the same day, on the gene and protein split (docs/gene_protein_split.md): "The rest of that suggested split
  between the genes and proteins makes sense I think except the registered degree strata SHOULD change to the new split",
  and "the brain expression is still provided via pseudo-gene descriptors". Then: "It's just that the descriptors would
  be limited to only the brain expression columns. Also, the several genes [to one] protein change is fine but I would
  also require an equivalent several proteins from one gene. Seed [masking] would then be included." Built into new
  graph directories, not applied to any confirmatory configuration: gene nodes carry the brain expression columns
  only, protein nodes the protein descriptors, one protein node per reviewed entry (37 genes have several), seed
  masking on the slice message-passing arms. Measured: the mapping is not one to one (57 gene nodes share a reviewed
  entry with another gene, 37 have several entries, and isoforms are not resolved by any source), the sources copy
  most edges of a gene onto all its entries (1,082 of 1,395 edge ends), and on the split 140 of 142 drugs fall in the
  top degree stratum. Open: edge ends that name no entry (sent to every entry by default), seed masking over encodes
  partners (on by default on a split graph), the encodes relation in the H2 rewiring, the 110 nodes without a reviewed
  entry, and whether the confirmatory_v2 configurations move to the split graph.

Amendment, 9 October 2026, before any second-family run (the user's decision): the confirmatory family trains on the
graph that splits genes from proteins. This closes the last question of the amendment above.
- The decision, verbatim: "the confirmatory config should definitely be the split graph and include the protein
  descriptors and brain expressions, compartments, everything that physiologically makes sense."
- What changes. The four `confirmatory_v2_*` configurations and their four no-descriptor ablations read
  `data/processed/graph_full_neuronal_split`; the node descriptors come from
  `full_neuronal_split_descriptors_brain_expression.parquet`, which puts the 64 protein components on the 12,709
  protein nodes and the 27 brain region and cell-class expression columns on the gene nodes, with the metabolite and
  reaction blocks and the compartment features as they already were (docs/generated/node_descriptor_columns.md, version 3); the
  linear-response encoder reads `full_neuronal_split_cell_class_weights.parquet`; message passing gets a third layer,
  because a perturbed gene node reaches its protein one hop later (decision 9 of docs/gene_protein_split.md). The
  development baselines (runs/full/v2_development.sh) and the lockbox baselines and scoring
  (runs/full/confirmatory_lockbox.sh, which now passes `--graph-dir`) read the same graph, so the models and the
  baselines see one graph. experiments/score_confirmatory.py itself is unchanged; it takes each run's descriptor and
  cell-class files from that run's own recorded arguments.
- What does not change. The evidence table (`evidence_full_v2`), the better_v2 label selection, configs/lockbox_v2.json
  (drawn on the evidence, not on the graph), configs/head_choice.json, the two tested models, the decision rule, the
  one-sided 0.025 H1-then-H2 sequence and the floors. No run directory existed under any `confirmatory_v2` name when
  this was written, so no finished run changes meaning and nothing is re-scored.
- Degree strata, measured rather than asserted. On a split graph a perturbed gene node has given its product-level
  edges to the protein, so its seed degree is no longer the degree the merged node had, and on the slice it is 1 for
  every perturbation, which collapses the registered strata into one. `perturbation_degrees_for_strata` therefore
  returns, on a graph with protein nodes, the degree of the seeds and of the proteins they encode, less the `encodes`
  edges themselves. Measured on `graph_full_neuronal_split` against the merged graph's seed degree over the 1,539
  perturbations of this evidence table: the same degree value for 1,527, Spearman 0.998, and six perturbations change
  degree quintile (CASP2, FGF8, GBA1, H3-3A, OTX2, WT1); on the slice the value is identical for all 451. The
  stratification is therefore preserved, not redefined, and is not re-registered. The first implementation of this
  hop read every node one edge away; that agreed on the slice but moved 43 percent of the full graph's strata, and it
  was corrected before any run (docs/gene_protein_split_results.md carries both readings).
- Still open, and blocking the lockbox run. Whether `encodes` is rewired in the H2 control (rewiring it would break
  the gene-to-protein identity the split exists to express, so holding it fixed is the proposal, not yet a decision);
  the descriptor treatments; and the development pilots of the two split configurations with the split baselines,
  which must be run and read first.
- The slice reading of docs/gene_protein_split_results.md is not evidence against this change: the user does not
  accept the slice as a verdict on the split until the two confirmatory models are tested on it.

Amendment, 9 October 2026 (second), recording the user's decisions after the first. Each is quoted and then stated as
a rule. No lockbox run has started, and none of these changes a finished run.

- **`encodes` is not rewired in the H2 control** ("Encodes should not be rewired in H2."). The H2 rewiring swaps edges
  within every other relation and leaves the gene-to-protein relation as it is
  (`fast_degree_preserving_rewiring(..., fixed_relations=[encodes])`, which is what `--rewire-encodes` off already
  does, so runs/full/confirmatory_lockbox.sh needs no change). Rewiring it would send gene X's knockout to gene Y's
  protein and to that protein's descriptors, so the H2 reading would measure scrambled identity beside scrambled
  wiring, and a model could lose the H2 comparison for a reason the hypothesis does not name. This closes the first of
  the three items the first amendment of 9 October named as blocking.
- **The protein descriptors keep rank 64** ("I understand the data support more dimensions for the protein descriptors
  but remember that we don't want them to completely outcompete the graph structure. I guess 64 is fine for now."). 64
  is the ceiling of `RANK_GRID` in graph/protein_descriptors.py rather than an interior optimum: held-out R-squared of
  the annotations still rises at the last point (0.113 at rank 48, 0.127 at 64), so the prespecified rule "the smallest
  rank reaching 95 percent of the best on the grid" selects the largest rank on offer. The width is not what keeps the
  graph in charge; the descriptor treatments do (the amendment of 8 October on how the node descriptors enter, and the
  graph-reliance reading of docs/generated/graph_reliance.md), and the no-descriptor ablation of step 1d measures what the
  descriptors are worth on their own. If the treatments leave the descriptors dominant, the answer is a treatment or a
  dropped block, not a narrower table.
- **Repeated affinity measurements of one drug-target pair are aggregated by their maximum** ("Oh. In that case, I
  guess Max is fine."), in place of the median that experiments/scope_off_target_binding.py used. The premise was
  corrected first: a pair with more than one value does not hold one assay run twice but two curators' aggregates of
  different papers (DrugCentral keeps one value per pair 96.5 percent of the time, GtoPdb already medians its own
  papers), and 2,367 pairs are in both sources with a median absolute difference of 0.10 log units, a 90th percentile
  of 1.13 and 12.1 percent differing by more than 1 log unit. The maximum is defensible by Cheng-Prusoff, since an
  IC50-derived pK is biased downward against a Ki and 34.3 percent of DrugCentral pairs carry no Ki or Kd. My own
  proposal was the type-aware rule (median over Ki and Kd when present, maximum otherwise); the user's decision
  overrides it, and the type-aware rule is recorded here as the untried alternative. This changes the off-target
  scoping only: the measurement-coverage strata count genes with an affinity, not their values, so they do not move.
- **Every plasma substrate binder is modelled, and the measured-occupancy extension waits for them** ("All of the
  plasma substrate binders should be modeled. Once AAG and albumin are added, there will be state to attach that
  separate extension to."). The scope, the data audit and what is missing are in docs/plasma_protein_binding.md. The
  graph already holds the binders as gene nodes (ALB, ORM1, ORM2, SERPINA6, SERPINA7, TTR, AFP, SHBG and the
  apolipoproteins) with no edge to anything they carry, so the first stage is binding edges for the substrates, and
  the second is the fraction unbound per drug, which no pinned source in this repository carries. Nothing in the
  confirmatory specification changes on this yet: the extension needs the binder state, and the binder state needs
  data that must be fetched and pinned first.
- **The off-target summary enters the drug input normalisation, not the feature vector** ("You can drop the off target
  summary into the normalization but mark it down as a note in case a situation comes up where it is needed to try.").
  So when off-targets enter a drug's seeds, the summary of their occupancies scales that drug's input alongside
  `drug_input_normalised` (experiments/run_main_model.py), and no drug-level scalar is added beside the graph. The
  note: the standalone feature (mean occupancy over the kept off-targets, which is what I would have taken of the
  three the user offered) stays available and untried, as do log(number of off-targets) and log(sum of occupancies),
  both of which are count-driven and closer to a research-attention proxy than to pharmacology.
- **The leakage-group rules are measured, and the registered grouping stays until the user decides** ("I don't like the
  alphabetical thing. Try the other version of family tie breaking and also make sure to include a measurement of the
  remaining leakage confound from this decision."). experiments/measure_leakage_group_rules.py, run on two evidence
  tables because the answer differs between them: docs/generated/leakage_group_rules.md on the off-target scoping table
  (evidence_full_v3_max3_targets, up to three mechanism targets per drug) and
  docs/generated/leakage_group_rules_evidence_full_v2.md on the table the confirmatory family reads (evidence_full_v2, one
  mechanism target per drug).
  - The tie-break by best-bound mechanism target does what it was asked to do where it applies. On the scoping table it
    takes the largest group from 0.18 to 0.14 of the drugs and moves 15 drugs, among them the antipsychotics, from a
    serotonin-receptor family to the dopamine-receptor family their own affinities name. On `evidence_full_v2` it
    changes nothing at all: no drug there has mechanism targets in more than one family, so the two tie-breaks give the
    same groups and the question is moot for the confirmatory split as it stands.
  - The remaining confound is not the tie-break but the join the family rule drops. On the scoping table, where a drug
    can carry three mechanism targets in different families, 0.49 of test drugs share a mechanism target with a
    training drug under either tie-break, carrying 0.57 of the test fold's kept drug positives, against 0.000 under the
    registered rule, which puts two drugs sharing a target node in one group by construction. On `evidence_full_v2`
    that part is 0.000 under every rule, and what remains is the drug-to-gene leak of docs/drug_target_leakage.md:
    0.377 of test drugs target a gene whose own perturbation is in training, carrying 0.411 of the test fold's kept
    drug positives, against 0.000 under the registered rule.
  - So the family rule's gain is bought with that leak, not with a better partition. Its largest group holds 0.18 of the
    drugs against 0.44 for the registered rule on `evidence_full_v2`; putting the drug-to-gene join back closes the leak
    and takes the largest group to 0.45, which is the registered rule's own figure. `group_by` therefore stays
    `disease_cluster_and_targets` for the confirmatory reading, and the family grouping is available as a development
    sensitivity reading, where the measured leakage is reported beside it rather than assumed away.
- **The Reactome entities get their own annotation vector** ("I like the separate annotation vector much better for the
  complexes"), not the mean of their members' descriptors. graph/complex_descriptors.py and
  experiments/build_complex_descriptors.py: the entity's annotation vector is the union (maximum) of its members'
  Pfam families, EC numbers and GO molecular function terms and the intersection (minimum) of their GO cellular
  component and UniProt location terms, with a DefinedSet or CandidateSet taking the mean over its members because it
  is a disjunction rather than a machine; the vector is standardised with the proteome's statistics and projected onto
  the same annotation-space directions the protein descriptors use. docs/generated/complex_descriptors.md reports the one
  measurement that decides whether the entity block can share the protein block's columns: the correlation, over the
  proteome, between the projection of a protein's recorded annotations and the projection of the annotations predicted
  from its sequence. Wiring the table into a graph's node_descriptors.parquet is a build step, and whether the
  confirmatory graph carries it is the user's call at the lockbox go-ahead.
- **Two symptom mapping conflicts stay open** ("I'll have to look at the antipsychotic bradykinesia and the other one
  later"): `psychomotor_retardation` matches `\bbradykine`, so the relabelling of the DRD2-inhibition claim to
  bradykinesia lands back on the symptom it was taken off; and `compulsive_behavior` matches `stereotyp`, which
  `ANIMAL_READOUT_PATTERN` also matches, so human punding cannot enter as a label without an exception to the
  rodent-readout filter (docs/generated/rodent_readout_human_evidence.md). Neither is changed here.

## Amendment, 9 October 2026 (third)

Three decisions and one question from the user, each quoted.

- **The Reactome entity annotation vectors go into the preregistered descriptor table, and the pilots do not re-run
  yet** ("I'm ok with regenerating the pre-registered input but don't rerun the same pilots until we've completely
  nailed down the design options"). `data/processed/node_descriptors/full_neuronal_split_descriptors_brain_expression.parquet`
  is rebuilt with `--complex-descriptors`: 138 columns against 137, SHA-256 `df38d78c78ffe6d4` against
  `27ed5e89ccb369d9`. The 64 protein components now carry the entity annotation vectors on 1,527 of the 1,681 protein
  entity nodes, and the new column `protein_has_complex_descriptors` marks those rows, because an entity's vector is
  the projection of its recorded annotations while a protein's is the projection of the annotations predicted from its
  sequence, and the two are not the same quantity (docs/generated/complex_descriptors.md). What did not change: the split graph's
  `nodes.parquet`, `edges.parquet` and `gene_to_protein.parquet` reproduce byte-identically, gene rows still carry no
  protein column, protein rows no other column, and the protein nodes' own values are unchanged. No confirmatory or
  development run has been launched on the new table, per the second half of the instruction; the pilots are the
  user's call once the design options are settled.
  - One code change was needed and is worth recording, because it would have failed silently on a later build:
    `gene_protein_split.place_descriptors_on_split` stripped the `protein_` prefix off every column of the block and
    looked the result up in the per-entry protein table, so the new flag would have been sought there as
    `has_complex_descriptors`. It now places only the columns the per-entry table holds and zeroes the rest on the
    protein nodes, which is correct: a protein node is not a Reactome entity.
- **The plasma substrate binders are built, orosomucoid among them** ("Implement the plasma binders please, download
  and pin whatever data you need. orosomucoid should also be implemented"). Stage 1 of
  docs/plasma_protein_binding.md: 27 `binds` edges, sign 0, from the extracellular copy of each cargo metabolite to
  its binder, in `data/processed/graph_full_neuronal_binders` and `data/processed/graph_full_neuronal_split_binders`
  (on the split graph the carriage sits on the protein nodes, since binding is the protein's property). Two sources,
  kept apart in `evidence_source`: the newly pinned UniProt binding-site features
  (`data/raw/uniprot/uniprot_plasma_binders.tsv.gz`, release 2026_03, sha256 `eab6550251dd8056`) and
  docs/curated_plasma_carriage.csv, 22 rows each with its source, PMID, DOI and a quoted sentence. Nothing in the
  confirmatory specification changes: the edges are in variant directories, and folding them into the confirmatory
  graph would need its own amendment and the pilots re-run, which the same message defers.
  - Orosomucoid gets one edge per gene, progesterone, and that is the honest limit rather than an oversight. Its
    UniProt function statement names no specific endogenous cargo ("Binds various ligands in the interior of its
    beta-barrel domain. Also binds synthetic drugs and influences their distribution and availability in the body"),
    and a graph with no drug nodes has nowhere to put the basic drugs that are its real cargo. Orosomucoid therefore
    enters this study through the fraction unbound of stage 2, which still has no pinned source.
- **Target family is recoverable from the graph and from the descriptors, which bounds what any drug grouping can buy**
  (the user's question: "is there any graph structure or attribute that corresponds to family? That might be another
  source of leakage."). Yes, and strongly: experiments/measure_family_in_graph.py, reported in
  docs/generated/family_in_graph.md, scores each channel by leave-one-out nearest neighbour over the graph's gene nodes with a
  GtoPdb family. On the 104 genes that are drug mechanism targets (20 families, chance rate 0.092), a held-out gene's
  family is recovered 0.904 of the time from the 64 protein components, 0.912 from its graph neighbours and 0.973 from
  its Reactome protein-entity memberships; the brain expression block, which carries nothing about a family's
  sequence, reaches 0.173. Over all 2,651 family-bearing gene nodes (498 families, chance 0.004) the figures are 0.790,
  0.576 and 0.821 against 0.043. Same-family gene pairs share a Reactome protein entity 0.732 of the time against
  0.023 for different-family pairs.
  - What follows for the grouping question of docs/generated/leakage_group_rules.md: a family-grouped split changes which drugs
    share a fold, not whether the model can tell which family a held-out target belongs to. The confound is a property
    of the graph and of the descriptor block, so the registered grouping `disease_cluster_and_targets` leaves it
    available too. This is not an argument for or against the family rule; it is a ceiling on what grouping drugs can
    remove, and it belongs in the limitations of any family-grouped sensitivity reading. The measurement is an upper
    bound on the confound, not an estimate of its effect on a score: nearest-neighbour recovery says the information
    is present and easy to reach, not that a trained model uses it. The user has deferred the grouping decision ("I'll
    have to think about the leakage family grouping later").


## Amendment, 9 October 2026 (fourth)

The user's decision, verbatim: "yes, include binder edges in confirmatory graph". The second confirmatory family
trains on the plasma-binder variant of the split graph. No lockbox run and no second-family development run has
started, so no finished run changes meaning and nothing is re-scored.

- **What changes.** The four `confirmatory_v2_*` configurations and their four no-descriptor ablations read
  `data/processed/graph_full_neuronal_split_binders` instead of `data/processed/graph_full_neuronal_split`
  (experiments/run_main_model_batch.py, `FULL_GRAPH_ARGUMENTS_V2`). The development baselines
  (runs/full/v2_development.sh), the lockbox baselines and experiments/score_confirmatory.py are passed the same
  directory (runs/full/confirmatory_lockbox.sh), so the models, the baselines and the scorer read one graph. Because
  git ignores `data/processed` and `runs/`, the variant has to be rebuilt by
  experiments/build_plasma_binder_variant.py in a fresh container and the two job-script edits reapplied; both are
  recorded in docs/confirmatory_runbook.md, step 1b.
- **What the variant is.** The split graph plus 27 `binds` edges, sign 0, from the extracellular copy of a cargo
  metabolite to its binder protein: 19 cargo metabolites and the 11 binder proteins AFP, ALB, APOA1, APOB, ORM1,
  ORM2, RBP4, SERPINA6, SERPINA7, SHBG and TTR (docs/generated/plasma_binder_graph.md). It is a strict superset of the split
  graph: the same node ids, the same `relation_types.json` and the same 279,757 edge rows as its prefix, checked
  through the trainer's loader with nothing trained. The node descriptor table
  (`full_neuronal_split_descriptors_brain_expression.parquet`, 138 columns, SHA-256 `df38d78c78ffe6d4`) and the
  cell-class weights are the registered ones unchanged, because descriptors are keyed by node id and the two
  graph-derived model inputs, the `reaction_brain` block and the reactions' cell-class weights, both follow
  `catalyzed_by`, which carriage leaves alone. In the assembled feature matrix exactly one column moves, the
  log-degree, on exactly the 30 nodes the edges touch.
- **What does not change, measured.** experiments/measure_carriage_graph_effect.py, reported in
  docs/generated/plasma_binder_confirmatory_effect.md: the perturbation ids, the symptom list, the leakage group ids, the
  outcome matrix, the label mask and the weights are identical with and without the carriage edges, so
  configs/lockbox_v2.json, the better_v2 selection, configs/head_choice.json, the two tested models, the decision
  rule, the one-sided 0.025 H1-then-H2 sequence and the floors all stand.
- **The degree strata, and the one point that needs stating.** No perturbation's own seed node is touched, because
  the carriage sits on protein nodes while a gene knockout seeds a gene node. But
  `perturbation_degrees_for_strata` hops from a perturbed gene over `encodes` to its protein, so three binder genes
  that are perturbations change strata degree: ALB 49 to 59, SERPINA6 3 to 5 and TTR 17 to 20. Two move degree
  quintile, ALB from 3 to 4 and SERPINA6 from 0 to 1, and both are development perturbations. No lockbox
  perturbation moves quintile, and the lockbox quintile sizes are identical (46, 69, 64, 74, 64). The two
  within-strata readings of H1 and the secondary within-stratum label permutation are therefore unchanged over the
  lockbox and changed over two development rows.
- **TTR is a lockbox perturbation whose graph neighbourhood this amendment changes after the lockbox was drawn**
  (drawn 2026-10-08; TTR holds 3 selection rows and 1 kept positive, cognitive_impairment). That is stated here
  rather than left implicit. It is defensible on one ground only: the carriage edges come from curated carriage
  literature (docs/curated_plasma_carriage.csv, 22 rows each with a PMID, a DOI and a quoted sentence) and from
  UniProt binding-site features (release 2026_03, sha256 `eab6550251dd8056`), neither of which was consulted for,
  derived from or filtered by any outcome label, and the edge set was fixed before this amendment and is not revised
  after any lockbox score is read. Nothing in the lockbox was opened to choose it. The honest residual is that the
  edge set was chosen by a person reading physiology, not drawn by a rule, and TTR's amyloid neuropathy phenotypes
  are the kind of thing that reading could have been influenced by; a reader who rejects that should read the
  lockbox result for TTR as the one row this amendment could in principle have touched.
- **What is still open.** The second stage of docs/plasma_protein_binding.md, the fraction unbound per drug, is not
  in this amendment and is not in the graph: it has no pinned source, and orosomucoid, whose cargo is basic drugs
  that the graph has no node for, enters through that stage rather than through these edges. The development pilots
  of the two split configurations are not re-run here (the user, the same message: "No new pilots yet"), so the
  carriage edges are registered but not yet read on any run.

Amendment, 12 October 2026, written before any lockbox run, before the held-out set has been redrawn and before any
model has been trained on the evidence table it registers. Each item names the decision it comes from; the decisions
are in docs/research_summary.md under their dates and the measurements behind them in docs/label_source_review.md.
The code for items 7 to 9 is not written at the time of this amendment, so those are registered and have been read on
no run.

**1. The evidence table.** `data/processed/evidence_full_v4` replaces `evidence_full_v2`, carrying four changes.
(a) **No limit on a drug's mechanism targets.** The dominant-target admission test is removed (user, 12 October: "I
really don't like having a target limit"; "I meant drop orphenadrine and the target limit"). (b) **Withdrawn 24 October 2026 by item 33, so orphenadrine is in; kept as the record of what was registered on 12 October:** **A drug whose
target set joins two otherwise separate leakage blocks is set aside**, found by removing each drug in turn and
measuring the largest block. Applied to this table the procedure names orphenadrine and nothing else. Measured: with
the limit, 222 drugs and 5,732 kept positive pairs in blocks of 114 and 71; without it and without the exclusion, 230
drugs with the largest block taking 194 of them and half the kept positive pairs; without the limit and with
orphenadrine set aside, 229 drugs and 5,799 kept positive pairs in blocks of 116 and 77, the largest block holding 51
percent of drugs and 27 percent of kept positive pairs, which is what the three-target rule held to two figures
(docs/label_source_review.md 26.1). (c) **Sign +1 for the 17 genes whose every causal association is a gain of
function**, replacing the disclosure in the registered text that the signed encoder reads the wrong sign for them.
(d) **A kept drug pair whose frequency never exceeds its placebo arm becomes a labelled negative** rather than being
masked (user, 11 October: "Why would working no better than the placebo not be counted as evidence against a
label?"). The table also carries two earlier unregistered changes, drugs with a target of any type with the salt-form
fix, and parkinsonism as the 24th symptom; this amendment registers them together.

**2. The held-out set.** Its membership is redrawn on the table of item 1 by the registered leakage groups. An added
drug that acts on a node of a held-out perturbation is held out as its own stratum, outside the primary score, and
does not train, validate or enter H1 or H2 (user, 11 October: "I accept put the three mechanism target pairs being
mostly in the held out set"). The registered group rule chains; for added perturbations a one-step rule is used
instead, because chaining would pull 149 further perturbations into the held-out set.

**3. The loss.** (The weighted loss of this item was superseded on 24 October 2026 by item 34d, which counts each pair
once; `--equal-drug-shares` stands, the placebo weights now supply item 34d's power a, and the item is kept as the
record and as the `--label-likelihood weighted` arm.) `--equal-drug-shares` is on in every confirmatory configuration
and its ablations: each drug's positives and, apart, its negatives are rescaled to the mean counts over the training
drugs (user, 12 October: "let's do the control version and the equal loss per share version"). The negatives of item
1(d) take a weight of **0.5 by default**, and where the drug's label states the trial arm sizes the weight is
`n_effective / (n_effective + 214.39)` with `n_effective = 1 / (1/n_drug + 1/n_placebo)` and 214.39 the median effective
size over the **25 drugs** that state both arm sizes, so a drug of typical size weighs exactly the default (user, 12
October: "I think -.5 is best unless you disagree" and "look for placebo arm sizes for those specific studies and then
calculate negative weight based on that then use .5 as default for nothing found"). 41 of the 61 pairs carry a measured
weight and 20 the default, and the weights run from 0.057 to 0.772 (`configs/placebo_negative_weights.csv`). A loss
weight below zero is refused by the trainer, and so is a file that gives one.

**Corrected 13 October 2026 to the constant the file was built with.** This item read "214 the median effective size
over the pairs that have one". Both halves were wrong: the median over the 41 pairs is 196.56, and the file's weights
solve to 214.3877, the median over the 25 drugs. The drug median is the right statistic, because the effective size
is a property of the drug's trial and a drug with many symptoms repeats the same number in several pairs, so a pair
median lets those drugs set the constant. The text is corrected to the file rather than the file to the text; the
difference in any weight is below 0.0005 and nothing has been run on either. `tests/test_placebo_negative_weights.py`
now holds the file to the formula, so the two cannot drift apart again.

**4. Reported beside the score, changing no model.** The input-size baseline, macro AUPRC within strata of a drug's
number of targets, and the permuted-target negative control. All three were named before any run on this table.

**5. The occupancy anchor.** Where an off-target ever enters a model input, its occupancy is read from the
measured unbound concentration at each target's own site (user, 12 October). No registered input reads an
off-target, so this binds nothing yet and is written here so the anchor is not chosen by default later.

**5a. Amended 13 October 2026; withdrawn and reinstated the same day, and superseded in its procedure by item 5c.
The calibrated placeholder of item 29 is permitted where no measurement exists** (the owner: "Just amend the item 5"). This item read "and not from the placeholder that fixes the best-bound
target at 90 percent". That prohibition was aimed at the **raw** placeholder, which sets the concentration by
assertion - it pins the best-bound mechanism target at 0.9 occupancy and reads everything else off that - and the
objection to it was that the anchor would be chosen rather than measured. Item 29's placeholder is a different
object: its concentration is corrected by an offset measured against the drugs that have both, and it carries
`has_measured_occupancy` so a reading can be taken with and without it. The objection is met, so the prohibition
is lifted.

**What the amendment does not do is make the two equivalent for an off-target, and the asymmetry is measured.** A
concentration error passes into occupancy almost undamped where occupancy is low and is absorbed where it is near
saturation, and that is exactly the difference between an off-target and a mechanism target. At the calibration's
one-standard-deviation scatter of 1.14 log units:

| | median occupancy | where a one-sd concentration error moves it |
| --- | --- | --- |
| mechanism targets (305 rows) | 0.787 | x1.2 up, x3.7 down |
| off-targets (1,163 rows) | 0.063 | **x7.6 up, x13.0 down** |

So an imputed off-target occupancy is uncertain by about an order of magnitude in either direction, against a
factor of two to four for an imputed mechanism target. **An off-target occupancy that rests on a calibrated
placeholder is therefore reported in the `has_measured_occupancy` stratum and not in the headline**, which is the
same instrument item 29 already registers and not a new one. Whether off-targets enter at all remains decision
1.3.

**5b. Withdrawn on the day it was written, as a misreading. It restored the prohibition for off-targets and
pointed the calibration at mechanism targets instead** (written against the owner's "Ooooh. I think it's better to
put the measured values back then and calibrate the other way", 13 October 2026, and corrected by them the same
evening: "No. That's not what i meant. I mean keep off targets but always use a measured value then impute all
values to get the calibration shift and apply it to only the imputed values that have not been measured.").

**What the misreading was.** "Put the measured values back" was read as "put item 5's prohibition back", so 5b
withdrew 5a and barred an off-target from taking a calibrated placeholder. The sentence was about item 29's claim
that "every drug therefore carries an occupancy on one scale", which reads as putting every drug on the
placeholder scale and so displacing the measurements of the drugs that have them. The owner was asking for those
measurements to be used, not for off-targets to be dropped. Item 5c registers what they described and 5a stands.
The text of 5b is kept below rather than deleted, because it is the second misreading of the same sentence in one
day and the record should show what was registered in error.

**[Withdrawn.]** Item 5a answered the asymmetry it had just measured
with a reporting instrument, a stratum. The owner's reading is that the asymmetry is an argument about which input
the imputation may enter at all, and it is the better reading: a stratum records that a number is unreliable and
still trains on it, while the asymmetry says the off-target number is not a measurement of anything. At a median
off-target occupancy of 0.063 the one-sd band runs from 0.005 to 0.48, which spans absent to half-engaged, so the
imputed value carries no information the affinity did not already carry.

So the rule has two halves, one per target role:

- **An off-target enters a model input only on a measured concentration.** This is item 5's original sentence,
  restored. 5a's lifting of it is withdrawn and not corrected, because the objection 5a answered was the wrong one:
  5a argued that the calibrated placeholder is not the raw placeholder, which is true and does not bear on whether
  an imputed concentration is usable at an occupancy near zero.
- **A mechanism target may take the calibrated placeholder of item 29.** This is where the error is absorbed, and
  it is measured on the population the placeholder is carried to rather than assumed from the population it was
  estimated on: over the 154 imputed mechanism rows the median occupancy is 0.806 and a one-sd error moves it x1.2
  up and x3.5 down, against x1.2 and x3.7 on the drugs that have a measurement
  (`docs/occupancy_coverage_and_shift_transfer.md`).

**The cost is registered with the rule.** The prohibition withholds the off-targets of **61 drugs**: 578 of 1,741
off-target rows, 33.2 percent, on drugs carrying 18.0 percent of the kept positive pairs. **No drug and no label
leaves the study** - a withheld drug keeps its mechanism targets, its input and its labels - which is what
distinguishes this requirement from the one the owner refused on 13 October ("Don't REQUIRE occupancy though ...
some drugs legitimately don't have it"): the requirement is on an off-target entering, not on a drug entering.

**Two limitations are registered with it, and neither is answered here.**

- **A withheld off-target is set to absent, which is a claim and not an abstention.** The input has no third state
  for "engaged, magnitude unknown". Of the 578 withheld rows the placeholder puts 64.4 percent below occupancy
  0.10, where absence is nearly true, and **15.6 percent above 0.5**, where it is not. For those 84 rows the
  prohibition substitutes one misstatement for another.
- **The role is a proxy for position on the saturation curve, and it is lossy in the tail.** What decides whether
  the error is absorbed is the occupancy, not the name of the target. Role tracks it at the median and not at the
  extremes: the worst quarter of imputed mechanism rows move x7.4 or more downwards under the same one-sd error
  and the worst tenth x13.0 or more, which is the off-target figure. A drug's weaker mechanism targets behave like
  off-targets because they sit where off-targets sit. Keying the permission on the imputed occupancy rather than
  on the role is the sharper rule and is not registered here; it is recorded as open point 9.1 of
  `docs/open_decisions.md` for the owner, because the rule registered here is the one they stated.

`has_measured_occupancy` is unaffected and stays: the mechanism side still carries imputed numbers, and that is
what the stratum reads.

**5c. The procedure, as the owner stated it on 13 October 2026**: "keep off targets but always use a measured value
then impute all values to get the calibration shift and apply it to only the imputed values that have not been
measured." It supersedes 5b, which is withdrawn, and fixes the step of 5a and item 29 that was left loose. Four
steps, in order, and the order is part of the registration:

1. **Off-targets are kept.** No occupancy rule bars one. Whether an off-target enters the input at all, and above
   what occupancy, is decision 1.3 and the threshold there is still the owner's; what is settled here is that the
   occupancy scheme does not decide it for them by withholding the number.
2. **A measured value always wins.** Where a drug has a measured unbound concentration, its occupancies are read
   from that concentration at each target's own site, for every target of that drug and in both roles. No
   imputation displaces a measurement, which is the step item 29's "one scale" sentence obscured and item 29 is
   corrected below.
3. **Every value is imputed, including the measured ones, to estimate the shift.** The placeholder is computed
   the same way for a drug that has a measurement and one that does not. That uniformity is what makes the
   comparison on the overlap transferable: a placeholder computed differently for the two groups would measure
   the difference in the procedure rather than in the drugs. The imputed values of the measured drugs are
   scaffolding for the estimate and enter no model input; they are discarded after the shift is taken.
4. **The calibration is applied only where no measurement exists.** A measured value is never calibrated, and a
   calibrated value never overwrites one.

**5c(ii). The calibration is a slope and a bias, not a constant shift** (the owner, 13 October 2026: "A slope plus
bias calibration is better. Do that instead"). The form is

    log10 C_calibrated = slope * log10 C_placeholder + bias

fitted by least squares on the drugs that carry both, one row per drug. The withdrawn constant shift is this
model's special case at `slope = 1`. Written against the placeholder because the placeholder is the quantity being
corrected; a line in it is the same model as a line in the best mechanism affinity, since the placeholder's log
concentration is `log10 9 + 6 - pK`. The fitted values are kept in `configs/occupancy_calibration.json` and the
implementation is `mechanistic_pathway_learning/perturbation/occupancy_calibration.py`.

**Two measurements decided the form, and the second is the stronger**
(`docs/occupancy_coverage_and_shift_transfer.md`).

- **`slope = 1` is refuted and not merely improvable.** A bootstrap of 4,000 draws over the 115 fitting drugs puts
  the slope at **[0.420, 0.643]**, which excludes 1.0. Leaving one drug out, the median absolute error falls from
  **0.852 to 0.524 log10**, a cut of 39 percent.
- **A constant shift makes the quantity a constant.** The placeholder pins the best mechanism target at 0.9
  occupancy, so a constant moves every imputed drug's best target to one and the same number, 0.838, with a
  standard deviation of **zero** over all 68 of them. For those drugs the occupancy of their best-bound target
  would carry no information and the model could read it only as an intercept. Under the calibration it spreads
  0.451 to 0.982, against the measured drugs' 0.135 to 0.988.

**The prediction is clamped to the affinity range it was fitted on**, pK 4.27 to 10.40 on the table in use. Eight
of the 68 imputed drugs sit outside it: ziconotide at pK 1.00 and vigabatrin at 3.07 below, six above led by
dexmedetomidine and ramelteon at 10.90. Unclamped the line puts ziconotide at 261 micromolar against 4.74 clamped.
A calibration line read outside its support is extrapolation and the clamp is registered with the form, not added
after seeing a result.

**Two limitations of the calibration, registered and not resolved.**

- **It does not make the imputed group look like the measured one.** Its median best-target occupancy is 0.931
  against the measured drugs' 0.838 and its spread is narrower, 0.256 against 0.320. The fit minimises error in
  log concentration, not the distance between the two occupancy distributions. `has_measured_occupancy` therefore
  stays and is not made redundant by a better imputation.
- **An affinity read with error attenuates the slope towards zero.** So the mechanistic reading, that exposure
  tracks potency at about half a decade per decade, is weaker than 0.532 suggests, and the true dependence may be
  steeper. This does not touch the out-of-sample error, which is measured on held-out drugs and falls whatever
  causes the slope.

**The parameters are refitted on the table the lockbox is drawn from, not carried over from here.** The rebuild of
decision 1.2 lifts item 1's three-target limit, which changes which gene is a drug's best-bound mechanism target
and so changes every placeholder. What is registered is the form, the fitting rule, the clamp and the file the
fitted values live in; the numbers quoted above are from the table in use and are expected to move. This is the
same treatment item 12a registers for the Open Targets weight.

**What this leaves unchanged.** The offset sits on the concentration and not on the occupancy, for the reason item
29 gives. `has_measured_occupancy` stays, and is now the only instrument separating the two populations, since no
rule withholds a value: every reading is reported within the stratum as well as over all drugs. The two
limitations item 29 registers stand, the scatter of 1.14 log units and the estimation of the offset on the
better-studied drugs.

**6. The comparative checks.** `configs/comparative_checks.csv`, 214 statements named in advance, read after scoring,
testing no hypothesis of the study and changing no decision rule. Only the two-drug kind is a test of a model; the
carrier, displacement and enzyme kinds go through relations no label varies and are reported without a verdict.

**7. The propagation runs to a fixed point.** Both encoders iterate until the relative change falls below **1e-3**,
in place of the registered fixed counts of three message-passing layers and eight linear-response steps (user, 12
October: "Use the convergence instead of 8 steps. 8 steps is arbitrary, not physiological"; "Propagation window is
settled. It goes to a fixed point to simulate steady state"). The perturbation is held on at every round and the
update is bounded so that it is a contraction, without which the iteration has no fixed point. Measured on the
structural propagation at the contraction bound, 1e-3 is reached at 23 steps, and at gains of 0.7 and 0.5 at 14 and
11 (docs/label_source_review.md 17.2). **The claim this supports is the subthreshold steady state**: a fixed-point
model cannot represent excitability, and the electrical layer's seven voltage-gated feedback loops are therefore read
at their settled value and not as an action potential.

**8. The encoder parameterisation.** One set of relation transforms applied at every round, in place of one set per
layer. Each relation owns a diagonal gain of 32 parameters; the nine relations that 2,100 or more development
training pairs reach — `encodes`, `catalyzed_by`, `substrate_of`, `activates`, `product_of`, `binds`,
`regulates_transcription_of`, `inhibits`, `member_of` — additionally own a rank-2 factorisation of 128 parameters.
1,792 parameters in all against the registered 61,440, 0.60 per kept pair against 20.65. The rank follows the number
of training examples that reach a relation rather than its edge count or its flow magnitude, because the flow is
distorted by in-degree; the counts break cleanly at nine relations with 2,100 to 2,468 pairs and eleven with 451 or
fewer, and they are measured on development perturbations only. **Rank 4 is named now as the only step up that may be
taken** if the development runs show the nine underfitting, so that it cannot be chosen after a result is seen. The
factors carry an explicit norm bound, for the same reason as item 7 (user, 12 October: "set the reduced rank bases
with the example share flow through each edge type and 1 repeated layer regardless of depth", and "just do what you
think makes sense instead"; docs/label_source_review.md 26.2).

**9. Message passing reads the edge signs.** Its relation adjacencies take the value `sign / in_degree` in place of
`1 / in_degree`, as the linear-response encoder already does (user, 12 October: "The edge signs are also settled: the
MP has to adhere to the edge signs the same way the linear encoder does"). Twelve relations have a constant sign that
the relation index already carried; the change affects the eight whose sign varies within the relation, 42,903 edges,
of which 7,321 are negative and were read as positive, 7,087 of them transcriptional repressions among
`regulates_transcription_of`'s 41,638 edges. One consequence is registered with it: with signs in the values the
in-degree mean can cancel, so a node with one activator and one repressor of equal weight receives zero.

**10. The Open Targets statements are their own evidence class**, kept apart from gene loss (user, 11 October: "I
accept all the suggestions under section 8 of the label review", whose row 7 states it). The weight that class
carries is not in this amendment and is named in "what is still open" below.

**11. A reading at the peak of the unbound tissue concentration** is for the confirmation stage only, is not trained
on and is not selected on (user, 11 October: "Peak tissue unbound concentration can be relegated to confirmation
only"). Nothing is built for it.

**12. The Open Targets evidence class carries weight 0.45, with 0.0 as a declared secondary.** The number is grade
B's 0.6 times the measured agreement of the class with the study's own labels: of the 118 human-worded Open Targets
triples, 71 name a target that a study drug acts on in the same direction, and 54 of those 71 (0.7606) carry the symptom
on a kept label of that drug, 9 more on a label the selection masked, and 3 (0.042) are contradicted by a placebo
comparison. 0.6 x 0.7606 = 0.4563, **rounded down to the nearest 0.05**, which is 0.45. The direction of the rounding
is not free and is fixed here: the agreement is measured on the triples whose target already has a study drug while
the statements that train are the ones no study drug label makes, so where the rounding has to go one way it goes
towards the lower weight. (Corrected 13 October 2026: this item read "0.6 x 0.761 = 0.457, rounded to 0.45", and
0.457 rounds to 0.46, not 0.45. The registered weight is unchanged at 0.45; what is corrected is the statement of how
it was reached, and `tests/test_open_targets_class_weight.py` now holds the number to the derivation.) This replaces
the 0.3 of the 12 October draft, which was a judgment with no measurement behind it and is withdrawn. **The limitation is registered with the number**: the testable triples
are the ones whose target already has a study drug, and the statements that would train are by construction the ones no
study drug label makes (docs/label_source_review.md 9.3), so the two subsets are disjoint and whether 0.761 carries over
is not something this measurement can say. For that reason a second arm is registered now, before any run: the same
configuration with the class at weight 0.0 and its statements reported as a held-out stratum only. The class is 1.4
percent of training pairs, so the two arms are expected to agree; registering both makes that checkable instead of
assumed. The user expressed no preference between them on 12 October and the standing instruction of that day was to
lock in what I have no objection to.

**12a. The weight is built; the class itself is not, and what the recomputation shows has to be decided before it
is** (13 October 2026). `loss_weight_for_record` now gives an `open_targets` record the fixed 0.45 whatever its
grade, with 0.0 available as the registered secondary, so the arm exists the moment the class does. The class does
not exist: no loader writes those records, and
`experiments/label_review/open_targets_class_composition.py` recomputes on the live table what item 12 states from
the table of 10 October. Two of the three numbers move, and the second is not a number at all.

| | as registered | recomputed on `evidence_full_v4`, after the crosswalk ruling of 13 October |
| --- | --- | --- |
| the class: no kept drug label confirms it and the target is a graph gene | 49 statements, 33 of them training | **65 statements** |
| share of kept pairs | 1.4 percent | **2.18 percent** |
| of the class, inhibition | 16 of 33 | 30 of 65 |
| of the class, activation | 17 of 33 | **35 of 65** |
| agreement of the class with the study's own labels | 0.7606 (54 of 71) | **0.6418 (43 of 67)** |
| the weight that agreement gives | 0.45 | **0.35** |

- **The agreement does not reproduce, and the weight turns on it.** Item 12 derives 0.45 from an agreement of 0.7606
  (54 of 71). Recomputed on the capped v4 table the agreement is 0.6418 (43 of 67), which gives **0.35**, one step
  of the weight scale below the registered number. Four constructions were tried and none returns 54 of 71: matching
  the direction and reading kept labels gives 44 of 70, reading every label the selection lists gives 57 of 70, and
  ignoring the direction gives 72 of 94 (an agreement of 0.766, but on 94 statements rather than 71). The likeliest
  cause is item 1's three-target limit, which the table still carries: a drug's recorded targets stop at three, so a
  drug acting on a statement's target through a fourth is neither testable nor confirming here, and lifting the
  limit adds drugs to both counts. **The weight is therefore provisional at 0.45 and the number that settles it is
  the one the script computes on the rebuilt table, not the one quoted here.** If the rebuild leaves the agreement
  near 0.64 the registered weight becomes 0.35 by the same derivation, and that is a change to make before the
  lockbox is drawn rather than after.
- **The share is 2.18 percent, not 1.4.** The reasoning that the two arms are expected to agree is weakened rather
  than overturned, and the figure moves again at the rebuild, so what is registered is the rule for recomputing it
  and not a number from a table that no longer exists: the script above, on the table the lockbox is drawn from, run
  before the class is built.
- **More than half the class is activation, and an activation is not a label on a row the study has.** The study
  perturbs a gene by knocking it out, bar the 17 seeded as gain of function. "Activation of X causes Y" is a
  different perturbation of the same node, so 35 of the 65 statements would arrive as **new perturbation rows**
  rather than as labels on existing ones. That changes the perturbation set, so it changes the leakage groups, so it
  changes the held-out draw. Item 12 does not say this, and it is why the class cannot be added once the lockbox is
  drawn: it enters at the same rebuild as item 1 or not at all.
- **Two crosswalk mappings are ruled out, and both symptoms leave the class with them** (the owner, 13 October 2026:
  "weight gain -> increased appetite is unsupported as a 1:1 causal inference as is sexual_dysfunction -> decreased
  libido"). A weight change is one outcome of appetite among others and is not a report of appetite; sexual
  dysfunction is wider than libido, covering arousal and orgasmic disorders the symptom does not claim. The two
  wordings were the whole of what those patterns caught: `increased_appetite` had 13 rows of "increased body weight"
  and 2 of "weight gain", `decreased_libido` 7 of "sexual dysfunction", and no row of either says appetite or libido.
  So 22 of 452 curated rows go and **neither symptom is reachable from this curation**. The rejected wordings are
  listed in `REJECTED_WORDINGS` rather than deleted, so a later crosswalk cannot pick them up without reopening the
  ruling. The rest of the crosswalk stands on the same reading ("decreased memory" to cognitive impairment,
  "hallucinations" to psychosis), and the script prints every remaining statement beside the wording it was mapped
  from, which is the review that has not been done.

**12b. No Open Targets statement lands on a scored row** (the owner, 13 October 2026, of the inhibition
statements: "oh ... they're weak evidence", then "ok. drop them"). The weight of 0.45 prices this class in
training and does nothing where it would matter most: **AUPRC reads a label as a label**, so a statement in the
lockbox would score exactly like a grade-A monogenic observation, with no frequency and no recorded absence behind
it. And its effect would exceed its one point, because the macro average takes the symptoms with five or more kept
positives in the lockbox: one such pair could decide **which** symptoms are scored.
`docs/label_source_review.md` 9.3 recommended this when the class looked five times larger: "In the lockbox they
would be scored against the weakest labels of the study".

The two directions resolve differently, because the study already represents one of them.

- **Inhibition carries nothing.** 30 statements. The study's knockout of that gene is a perturbation of the same
  node in the same direction and it is scored, so putting the statement there puts weak evidence into the primary
  score; giving it a row of its own would duplicate a perturbation the table already holds. The ten pairs it would
  have added are not worth either.
- **Activation becomes its own perturbation row, never scored** (the owner: "what about just adding the receptor
  activations as a new perturbation type?", and "what about limiting that perturbation type to the training data
  since it's rows are low and it doesn't have a full mechanism pathway?"). 35 statements on **23 rows**, typed
  `receptor_activation` and seeded +1 at the gene node. Here nothing is duplicated: no other perturbation in the
  table drives these receptors upward, and the activation direction is the one thing this curation uniquely
  carries. The rows are 1.22 percent of perturbations and carry 1.52 labels each.

**12c. What "never scored" means, which is not "always trained".** `run_main_model.withhold_never_scored_rows`
takes a `receptor_activation` row out of every test set, and out of training whenever its leakage group is held
out. The second half is the point: training the activation row of a gene whose knockout sits in the lockbox shows
the model that node perturbed, which is the leak the leakage groups exist to stop. So such a row is **dropped**,
neither trained nor scored, and trained only when its group is not held out. **The held-out draw over every other
perturbation does not move**, because these rows leave the test set whatever group they fall in.

Two reasons this type is kept out of the score rather than merely down-weighted. It carries **no pharmacology at
all** - no exposure, occupancy, route or plasma binding - so the row is identifiable from its inputs alone, while
**43 percent of its labels are one symptom** (cognitive impairment, against 14.4 percent of all kept positives):
"identify the type, rank cognitive impairment" would be a strong rule with no mechanism in it, and macro-AUPRC is
scored per symptom. The base rate is not the exposure it might appear to be: at 0.063 it is exactly the gene rate,
so the type offset of decision 4.6 gains nothing from it.

**12d. The weight is provisional, and the construction behind it is weaker than the number suggests.** Asked how
0.45 was decided (the owner, 13 October 2026: "how did you decide the .45 though?"), the honest answer is that no
session decided it on evidence that reproduces. Its provenance, in order:

1. **0.3**, on 12 October: half of grade B "because halving looked proportionate". Recorded at the time as "a
   judgment with no measurement behind it", and withdrawn.
2. **0.45**, as grade B's 0.6 times the class's measured agreement with the study's own labels, 54 of 71 testable
   triples, 0.761.
3. **The arithmetic does not give 0.45.** 54/71 is 0.7606 and 0.6 x 0.7606 is 0.4563, which rounds to 0.46. The
   item now states the rounding as down to the nearest 0.05, with the extrapolation as the reason for the
   direction, rather than claiming an arithmetic that does not hold.
4. **The agreement does not reproduce.** On the capped table it is 0.6418, 43 of 67, which would give 0.35. Four
   constructions were tried and none returns 54 of 71 (item 12a).

**And the construction multiplies quantities that are not commensurable.** The grade weights are ordinal by
design - `assign_evidence_grades.py`: "Grades are deliberately coarse; the weights are the initial values from the
design" - so 0.6 is a rank expressed as a number and not a probability. The agreement, 0.76 or 0.64, **is** a
probability. Multiplying one by the other treats the agreement as a discount on grade B, which would mean
something only if 0.6 were itself a reliability. The product has no interpretation, and that is a defect in the
derivation and not in the measurement.

**The route that would settle it is already the registered default.** `configs/evidence_assembly.yaml` sets
`weighting: mode: learned_reliability`, and `evidence_reliability_model.py` exists for exactly this reason: "Fixed
grade weights and count-based weights share a flaw: they are set by hand." The Dawid-Skene fit estimates each
source's sensitivity and specificity from the pattern of agreement across sources, with a Beta prior and an
interval. `open_targets` is not in its source list. Adding it there would estimate from the same overlap the 0.761
was hand-computed on, but properly: with a prior, an interval, and no multiplication by an ordinal. The
extrapolation would remain - the sensitivity is estimated on the overlapping triples and applied to the
disjoint ones that train - but it would be explicit in the model rather than buried in a product.

**Decided: the class enters the reliability fit** (the owner, 13 October 2026: "add it to the Dawid-Skene fit
estimates"). `load_open_targets_statements.reliability_reports` emits a report for a statement **only where
another source already reports that item**, and `configs/evidence_assembly.yaml` lists `open_targets` among the
reliability sources. Three things follow from the "only where the item exists" condition, and all three are the
reason for it:

- **It creates no pair.** The assembler makes one observation per (perturbation, symptom, relation) with at least
  one explicit report, so a report on a new item would conjure a scored pair out of a review statement, which 12b
  rules out. Joining an existing item conjures nothing.
- **It reaches the fit and not the grade**, because the grade reads the pair's primary evidence class only. This
  is the route the literature class already takes, so no new machinery is involved.
- **It is estimated exactly where the hand-computed 0.761 was measured.** Those are the statements an existing
  item can corroborate or contradict. The fit redoes that measurement properly: a sensitivity and a specificity
  with a Beta prior and an interval, rather than an ordinal grade weight multiplied by a probability.

**The limit is unchanged and is now explicit in the model rather than hidden in the product.** The statements with
an overlapping item are by construction not the statements that train, so the sensitivity is estimated on one
subset and applied to a disjoint one. That extrapolation was always in the 0.45; what changes is that the fit
states it and carries an interval for it.

**0.45 remains as the fallback** for `--weighting grade`, the fixed-grades arm, where it is a convention and is
labelled one. Under the registered default weighting the class's weight comes from the fit.

**13. `VM_c` is computed, not fitted, and the claim is the subthreshold steady state.** The neuronal membrane potential
is the linearised parallel-conductance equation over the ion pools: each pool feeds `VM_c` one edge whose weight is that
ion's share of the resting leak conductance times RT/zF, six fixed weights adding no free parameter
(`mechanistic_pathway_learning/graph/membrane_potential.py`). Two neuronal extracellular pools are added, sodium and
chloride, so every ion in the equation has both sides; calcium stays a signalling node and does not enter it. The
constants are Düsterwald et al. 2018, eLife 7:e39575, Table 1, under CC BY 4.0, quoted with the place each was read in
`docs/membrane_potential_constants.md`. The law is the parallel-conductance equation and not Goldman-Hodgkin-Katz
because no measured permeability ratio for a mammalian central neuron could be verified and that source states ohmic
conductances, which substituted into GHK miss its own -72.6 mV by 39 mV. The build registered is
`computed_beside_the_reactions`: the 405 `changes_membrane_potential` edges are kept, because deleting them was measured
to lower the field at `VM_c` and not raise it. **This sentence states the superseded rule: the
build registered since 26 October 2026 is `computed_from_the_pools` and the reaction edges are not made (item 35).** Registered with it, as 23.3 required: the seven reactions `VM_c` gates
all feed charge back into it, an excitable membrane is not contractive, and a model run to a fixed point under the
contraction bound represents where the membrane settles under a sustained perturbation and not an action potential. It
must not be read as showing excitability.

**14. A drug outside the nervous-system code is admitted by a three-part rule, read rather than by group name**
(user, 12 October 2026: "Can't exclude all beta blockers … just ones that don't act centrally because beta receptors
are all throughout the brain"; "The revised rule seems good for the beta blockers"; "What about combining the rules?";
"Sounds good. Do it."). All three must hold, and each is a property of the drug established before any outcome is
looked at, which is what keeps the drug set from being selected on the symptoms the study predicts:

  a. **the drug's own label states a central action** in a pharmacology section — mechanism of action, clinical
     pharmacology, pharmacodynamics or description — in a sentence about that drug. The adverse-reaction, warning and
     indication sections are not read, because admitting a drug for the psychiatric events on its label is the
     circularity this rule exists to avoid. `experiments/read_label_central_action.py` finds the candidate sentences
     from openFDA and quotes each with its set identifier; the sentence is then **read** and not counted, because
     class boilerplate ("the mechanism of the antihypertensive effects … has not been established; factors may
     include … vasomotor centers in the brain") appears on every beta blocker's label and says nothing about the drug
     in hand, and a combination-product label can put a drug's only match on a sentence about the other ingredient;
  b. **a mechanism target of the drug is a brain-expressed node** of the confirmatory graph, by the graph's own GTEx
     annotation;
  c. **the drug's measured Kp,uu,brain is at least 0.1.** The threshold is read off the measured distribution of the
     class this came up over rather than chosen: nothing measured lies between nadolol's 0.037 and oxprenolol's 0.20
     (docs/label_source_review.md 29.1).

**A label that states the drug does not reach the brain excludes it, whatever the other two parts say.** That is
positive evidence and it is quoted: nadolol "only minimal amounts of nadolol were detected in the brain", labetalol
"Only negligible amounts of the drug crossed the blood-brain barrier", sotalol "Sotalol crosses the blood brain
barrier poorly", montelukast "minimal distribution across the blood-brain barrier", etoposide "the concentrations are
lower than in extracerebral tumors".

On the evidence read (`configs/label_central_action.csv`, `configs/centrally_acting_drugs.csv`), the rule **admits
metoprolol and propranolol** and holds pindolol (penetrant at 0.50, no label sentence of its own), oxprenolol
(penetrant at 0.20, no US label in openFDA), timolol (a central-action sentence, no measured Kp,uu,brain) and
carvedilol (neither). Nothing is added to a table by this registration: the drug set changes only in the v4 rebuild,
which waits on the held-out draw.

**This rule replaces the ATC-group list for additions.** `configs/admitted_atc_prefixes_draft.csv` was never signed
off and is superseded: its content was a group name plus, for six drugs, a hand-read label sentence, and part (a) is
that same evidence standard applied to every candidate. The three groups whose ATC name states central action
(C02A, M03B, A08AA) and the hormone groups (H, G03) are not admitted by group any more; each of their drugs is subject
to the rule. The list stays in the repository as the record of what was considered.

**What the rule cannot do, registered with it.** It is not an automated gate. Over the 924-drug pool parts (b) and (c)
alone admit metformin, warfarin, omeprazole, etoposide and six NSAIDs while leaving carvedilol out, because almost
every drug has a target expressed somewhere in the brain and because having a measured Kp,uu,brain selects on having
been a reference compound in a brain-penetration study (docs/label_source_review.md 29.2). Part (a) is what turns
those out, and part (a) requires a reading. The screen's recall is also imperfect: metoclopramide, which is in the
superseded list with a hand-read sentence, is missed by the screen at eight labels.

**15. The unbound brain exposure reads more spellings of its own quantity, and its species limit is disclosed.**
`experiments/build_drug_exposure_table.py` matches eight further spellings of the unbound-brain ratio that the corpus
uses — `Kp,uu brain`, `Kp,uu, whole brain`, `Kp,uu,WB`, `Kp,uu,ISF`, `Kpuu,ECF`, `Kpuu,BBB`, the `Kp,uu from AUC…` and
`Kp,uu from VT…` forms, and the cerebral-microdialysis form — with a fluid-or-regional exclusion beside it, so no
cerebrospinal-fluid or regional value can enter (user, 12 October: "Yes keep additional kp,uu values"). 89 drugs become
94, none are lost and 16 values change, five beyond 2-fold; the diff is in the decision log. Registered with it, because
it bears on every occupancy the study computes: **the values are predominantly rodent**, and Fagerholm 2022 reports a
rat-to-monkey R² of 0.74 against a rat-to-human R² of 0.01 (n=13), so the species translation is an unquantified error
on this input and no claim rests on its absolute scale (docs/brain_exposure_data_feasibility.md). **This clause is
superseded from 26 October 2026 by item 36**: the Fagerholm citation is excluded as not peer reviewed, both coefficients
are withdrawn, and the n=13 it attaches to the pair belongs to the rat-to-human comparison alone (n=17 is
rat-to-monkey). The disclosure itself is kept and re-justified there. The cerebrospinal-fluid
exclusion is kept and now has its own evidence: lumbar CSF runs more than 3-fold high for P-gp substrates and
buprenorphine's own measured CSF range spans 46-fold.

**16. Withdrawn 24 October 2026 by item 33, with item 1(b), so no drug is set aside; kept as the record:** **The bridging rule is applied once, and only orphenadrine is set aside** (user, 12 October 2026: "I don't know
about excluding tapentadol. It's got NE effects which are very important. I'm leaning towards leaving only orphenadrine
out."). The rule registered in item 1 had no stopping condition, which was an omission in my drafting: applied again to
the rebuilt table it names tapentadol, which seeds `OPRM1` and `SLC6A2` and so joins the 18-drug opioid block to the
97-drug monoamine block, and a third pass names agomelatine. **One pass is the rule.** The reason given for stopping
there is pharmacological and is recorded as such: tapentadol's noradrenaline reuptake inhibition is part of what the
study is trying to represent, so removing the drug to tidy the split would remove a mechanism rather than an artefact.
The cost is stated with it: the opioid and monoamine blocks stay joined, so the largest block holds 116 of 231 drugs,
50.2 percent of the drugs and 27.0 percent of the kept positive pairs. That is no worse than the table in use, whose
largest block holds 51.4 percent and 27.2 percent, so the rebuild does not degrade the split it inherits
(docs/generated/rebuild_leakage_cost.md). The held-out draw therefore cannot separate opioids from monoamines, and no claim may
rest on its doing so.

**17. The enzyme, carrier and two-drug statements are training labels, in both encoders** (user, 12 October 2026:
"Implement"). 106 combinations and 317 positive pairs from `configs/comparative_checks.csv`, carried as the combined
perturbation type (`mechanistic_pathway_learning/evidence/combined_perturbations.py`). Both confirmatory models train
on them, so the two stay symmetric: the asymmetry I warned of on 12 October rested on the `clears` relation being the
only route these examples inform, and that was wrong. Lowering a clearing enzyme also moves the 61 to 103 reactions it
catalyses, through `catalyzed_by`, a relation with 24,266 edges that every reaction-touching label already trains, so a
combination constrains the net of two routes and the message-passing encoder is not being asked to fit 3,072 fresh
weights from 140 pairs (docs/label_source_review.md 27.1). The 21 negative controls of the check table are **not**
labels (user: "That's fine"): their statement is that nothing is expected, and a labelled negative would assert the
symptom does not occur, which no source states. Under `--equal-drug-shares` a combination shares its drug's loss slot,
so a drug with a statement does not take two drugs' share.

**18. Multiplicity: H1 first, then H2 and P1 by Holm at one-sided 0.025 per model** (user, 12 October 2026, on the
three ways set out in docs/records/2026-10/pathway_test_options.md: "Accepted"). The chance of a false claim stays at most 0.025 per
model and at most 0.05 across the two. H2 therefore needs p below 0.0125 unless P1 also passes. P1 is read only behind
the two gates, G1 (stability) and G2 (faithfulness), which are preconditions and not tests at a level: the claim passes
only if G1, G2 and the Holm-adjusted test all pass, and a precondition can only lower the chance of passing, so the
conjunction keeps the level. The option this rejects is P1 on its own at 0.025, which would let the chance that at least
one of the four claims (two models x H1 and P1) passes by luck reach 0.10. Registered before any confirmatory module
exists, which is the condition docs/records/2026-10/pathway_test_options.md set for fixing it at all.

**19. The probability clamp stays off, and is checked on the development runs** (user, 12 October 2026: "Leave the
clamp off for now but make sure you check for the issue in the dev runs"). The training loss keeps the logarithms of P
clamped to [1e-6, 1 - 1e-6], so a pair beyond the clamp has a constant loss and no gradient, and `--bce-in-log-space`
is not taken. The evidence that motivated it was measured on the sigmoid head, which is no longer in the confirmatory
family (user: "No sigmoid head will be used"), so for the noisy-OR head the clamp is **untested** rather than known to
be harmless, and that is why the check is registered rather than the option. Every development run reports the number
of its test probabilities below 1e-6 and above 1 - 1e-6 and how many labelled positives and negatives are among them
(`clamped_probabilities` in the run record). If labelled positives sit below the clamp in any development run, the
option is reconsidered before the confirmatory runs and not after.

Amendment, 13 October 2026, written before any lockbox run and before the v4 graph is rebuilt. Items 20 to 23 are
built and their tests pass; item 24 lists what the owner's decisions of this date leave open.

**20. A cell class attenuates a response by its limiting step, not by a product along the path** (the owner, 13
October 2026: "min along the path makes WAY more sense to me. do that so it aligns with the physiology"). In place of
multiplying the messages arriving at a node by that node's weight in the class on every round, which charges a route a
factor at every step, the settled response of class k is multiplied once by
`b_k(t) = max over routes to t of min over nodes n on the route of w_k(n)`,
the weakest weight on the widest route, computed by a max-min recurrence over every route (`class_bottleneck`). The
throughput of a chain at steady state is set by its weakest step, which is the same rule the gene rule already applies
inside a reaction, where an "and" takes the minimum. A per-edge stoichiometric demand divides the bottleneck, so a step
consuming two copies of its source is limited at half its availability (the owner: "ACh needing to bind two molecules
to the receptor in order to activate it, which would cut that expression in half"); the graph does not carry those
coefficients yet, so every demand is 1 until the rebuild writes them. At an extracellular pool node shared by the
classes the bottleneck is the largest over the pooled classes, because the pool is one compartment, and an entry node
the perturbation does not seed carries no route. Three things this changes and one it does not. It conditions the
magnitude of a class's response on that class's expression and no longer the route, because a factor applied on every
round compounds whichever factor it is, so the bottleneck has to be factored out of the propagation. The pool then
mixes states no class has attenuated. And the two rules err in opposite directions: the product understates, charging
a route of expressed nodes at every step, while the bottleneck overstates, scaling the sum over every route by the
widest route's ceiling, since masking the thin routes would need a cut-off and the weights have no natural one. What
it does not change is the fixed point, which is reached before the bottleneck is applied.

**No measurement decides whether this rule is used** (the owner, 13 October 2026, on being told the rule was
registered without one: "that doesn't need measured for confirmation to be in the final models. It should just be
in there to mirror the physiology"). They are right, and an earlier draft of this item said otherwise. The rule is
chosen because the throughput of a chain at steady state is set by its weakest step, which is a fact about
pathways and not a hypothesis this study tests; a comparison against the product rule would say how much the
choice moves the predictions, which is not the same question and is not a reason to hold the rule back.

**What does need checking is whether the implementation is the rule**, which is a correctness question and not a
model comparison, and `experiments/measure_limiting_step_rule.py` is repurposed to it. Two properties of the code
are not properties of a limiting step. The bottleneck `b` is computed on the **unsigned, unweighted** structure,
so a route through an inhibitory edge raises the ceiling exactly as an activating route does - "a bottleneck cares
only whether a route exists" is true of a bottleneck and false of a signed one. And `b` scales the settled state,
which already sums every route, so a contribution that arrived through a barely expressed route is credited at the
widest route's ceiling. Both are stated in the encoder and neither has been exercised. The first is a unit test;
the second is a property of the rule as registered and is disclosed rather than fixed, since masking thin routes
would need a cut-off and the weights have no natural one.

**21. A perturbed node does not read its own descriptors: `seed_masked` in both encoders** (the owner, 13 October
2026: "it HAS to use seed_masked to be physiological and to avoid signal leakage"). This replaces the reading of the
treatment rule of 8 October, which picked `seed_masked` for message passing and `zero_init_slow` for the linear
response; under `zero_init_slow` a perturbed node still reads its own descriptors, through a map that starts at zero,
so it does not meet the decision. The reason is a shortcut and not leakage of held-out information: no descriptor block
is derived from the labels, and what `plain` permits is a readout that learns which protein was perturbed and skips the
propagation, which is what the descriptors-only control measures. On the split graph the mask also covers each seed's
`encodes` partner and, for a drug seeded on its entry node, its mechanism targets and their partners. **The seed's
cell-class weights are not masked, and that is deliberate** (the owner, 13 October: "whether the cell class expresses
that knocked out gene at all determines whether the effect even matters in that cell type"): the weights are a separate
input from the descriptors, they set how far a class carries the response rather than naming the node, and under item
20 they are the class's ceiling. The seed's own brain-expression *descriptor* columns (`gene_brain`, `reaction_brain`)
are masked with the rest. The limit already registered holds: a seed's reactions still carry its EC numbers and the
expression its gene rule copied onto them.

**21a. A perturbed node still reads its own regional expression** (the owner, 13 October 2026: "that brain gene
expression masking not acceptable for perturbations ... whether the cell class expresses that knocked out gene at all
determines whether the effect even matters in that cell type"). Of the 138 descriptor columns, the 16 that carry the
perturbed gene's regional and whole-tissue expression stay readable at its seed under `seed_masked`
(`SEED_READS_THESE_DESCRIPTOR_PREFIXES`: the 13 `gene_brain_region_` columns, the two GTEx maxima and the
has-expression flag); the other 122 are masked as item 21 states. The 11 `gene_brain_class_` columns are **not** among
them, because they are the same eleven cell classes as the cell-class weight table, which is already a propagation
input and the better form of them, so unmasking them would add shortcut capacity and no mechanism. The honest residual:
16 columns of expression are still a narrow fingerprint of a gene, so this reopens a small part of the route item 21
closes. What closes it properly is item 23a, which makes the regional axis a propagation input and leaves these
columns redundant in the way the class columns already are. Until that is built the columns are readable, and masking
by column rather than by count is what makes the distinction expressible at all.

**22. Every channel carries the perturbation with the same sign, and the channels start equal** (the owner, 13
October 2026: "each class should be consistently signed within itself"). Each channel's input weight is `exp` of a free
parameter, so it is positive, and all start at one value; the classes stay free to learn different sizes. Before this
each channel held one free weight drawn from a normal distribution, so the sign and the size of the perturbation in a
channel were set by the draw. A readout absorbs a flipped sign everywhere but the extracellular pool, whose mean across
classes is fixed: it averaged copies of one extracellular quantity carrying opposite signs. Measured on a toy chain
with every class weight at 1, the pool lost a factor of 1.2 to 3.1 to that cancellation over six seeds, read negative
for a positive perturbation at one of them, and the channel sizes differed by up to 26 times.

**22a. Compartment pH is a throughput ceiling, read from the settled proton balance** (the owner, 13 October 2026:
"i don't think we've incorporated compartment pH yet, which is important", and of this design: "perfect solution.
implement it"). Protons are already nodes, one per compartment, with 6,271 reaction edges: 2,048 producing and 1,281
consuming reactions at the cytosolic proton alone. Two things stopped that being used, both measured. The nine
Human-GEM proton nodes carry `is_currency`, and a currency node's outgoing edges are dropped, so each one receives and
its deviation is computed while it sends nothing; and the same species has two pools, Human-GEM's `MAM02039*` and
Reactome's `CHEBI15378*`, with different base ids, so they never merged, the Human-GEM copy holding 50 to 100 times
the reactions in every compartment both describe while only the Reactome copy propagates. So whatever pH signal
existed travelled through one to two percent of the reactions that touch a proton. **Resolution:** the Human-GEM node
governs each compartment it describes and Reactome's governs the vacuole, which only it names; and after the
propagation settles, that node's deviation becomes a multiplier on every node in the compartment,
`w_pH = exp(-(sensitivity * deviation) ** 2)`. On the v4 graph that is 18,928 of 49,574 nodes over ten compartments
(cytosol 8,098, extracellular 3,713, mitochondrion 2,104, ER 1,909, peroxisome 984, lysosome 790, Golgi 670, nucleus
568, vacuole 49, intermembrane 43). A weight does not propagate, which is the point: the cytosolic proton touches
3,329 reactions, and a node that sent across all of them would make every pair of reactions neighbours, which is why
the currency mask exists and why unmasking it would be worse than leaving it.
**The form is the log one, which is what a pH is.** `ΔpH = -log10(1 + sensitivity * deviation)` and
`w_pH = exp(-(ΔpH / width) ** 2)`, as `compartment_ph_weight` implements it. Acidifying by a given fraction and
alkalinising by it move pH by different amounts, so the weight is **not** even in the deviation and a
gain-of-function does not take the same weight as a loss-of-function at a node whose compartment the perturbation
moves. That asymmetry is the chemistry and not a defect.

*(An earlier draft of this item registered the even form `exp(-(sensitivity * deviation) ** 2)` and listed among
its properties a **gain-versus-loss mirror**: that a gain of function produces the exact negative of the field a
loss of function produces. The owner never accepted that property and it should not have been in the registration.
It is withdrawn, 13 October 2026. It appears nowhere else in the registration, so nothing rests on it.)*

**What the weight does and does not do.** It is a multiplier on each node's settled value, applied once after the
fixed point and after the bottleneck. It therefore does **not** attenuate the messages a node passes during the
propagation: a collapse of lysosomal pH cannot change the field at any cytosolic node. The cell-class bottleneck
does carry its ceiling along routes, through the max-min recurrence; this one does not.
`docs/physiological_adherence_review.md` section 5 holds its reach (18,928 of 49,796 nodes take a weight; 5,127
transport reactions carry a multi-compartment label and take none, as do all 25,741 gene, protein and drug nodes)
and the conditioning of the proton node the ceiling is read from.

**23. The registered model is the trainer's default** (the owner, 13 October 2026: "all of the v4 stuff should be ON by
default"). Every registered choice that is built is now the default of `experiments/run_main_model.py`: the grouped
split by disease cluster and targets, typed node features, `seed_masked`, the fixed point at 1e-3, the limiting-step
rule, positive input weights, carrier relations and extracellular coupling for the linear response, the graph's edge
signs for message passing, equal drug shares, the placebo negative weight of 0.5, the weighted-optimum start, the
noisy-OR initialisation and learning rates, and the refit on validation. Three safeguards come with it, because a
default that carries a registered choice is how commit `9df62ee` changed a registered model silently
(`docs/records/2026-10/confirmatory_architecture_review.md`, row 8). `experiments/run_main_model_batch.py` states the same model as
explicit flags, `tests/test_registered_defaults.py` holds the two equal so a default cannot drift from the
registration without a test failing, and `VALUES_BEFORE_THE_V4_DEFAULTS` gives every such argument the value it held
before this date, so a finished run is rebuilt as the model it was trained as and not as the current default. Each
choice can still be turned off by name. No data path is a default: the graph, evidence, label selection, descriptors,
cell-class weights and combined perturbations are named per run and belong to the rebuild.

**24. What the decisions of 13 October leave open, registered as open so it is not settled by default later.**
- **23a. The channel axis becomes HPA's cluster types, which is the region-by-class cross already in the source**
  (the owner, 13 October 2026: "i thought the region already had cell type expression levels and that the cross just
  has 0s in some spots, which would mean that particular sparse matrix can be mapped to a reduced one for faster
  processing in the bottleneck pass"). Measured: the 11 cell classes are a pooling of HPA's single-nuclei table, whose
  `Cluster type` column is already region-qualified, and its 34 types are that reduced matrix. About 20 are
  region-specific neuronal types (amygdala excitatory; hippocampal CA1-3, CA4 and dentate gyrus; thalamic excitatory;
  cerebellar inhibitory and Bergmann glia; midbrain-derived inhibitory; mammillary body; medium spiny and eccentric
  medium spiny; seven cortical types) and about 10 are pan-regional glial, vascular and immune types that carry no
  region because they have none. With the Siletti dopaminergic cluster, which HPA has no type for, that is 35 channels
  against the present 12: three times the bottleneck pass rather than the thirteen times a full 12-by-13 cross would
  cost, and the pass is cached per perturbation, so it is paid once per perturbation and not once per epoch. Registered
  before it is built; the cost is to be measured on the rebuilt graph, and the 13 regional descriptor columns of item
  21a become redundant when it lands.
- **Message passing was not at its registered form when this was written.** Item 8 of 12 October (one repeated layer,
  rank-factored, run to a fixed point) was built later on 13 October 2026 (commit `d9ea1e7`;
  `--relation-parameterisation shared_low_rank` is the trainer's default and the encoder runs to the
  `--fixed-point-tolerance` of item 7). What remains is that the encoder does not hold the perturbation on at every
  round (decision 9.83, deferred by the owner), so item 7 is met by the linear-response encoder only.
- **Three registered items had no code when this was written.** The per-pair placebo weights of item 3
  (`configs/placebo_negative_weights.csv`, which the trainer then did not read, applying the 0.5 default to every such
  negative), the Open Targets weight of 0.45 of item 12, and the Holm procedure of item 18. All three were built later
  on 13 October 2026 (commits `a44593d`, the weights file read by `--placebo-negative-weights-file` and Holm over H2 and
  P1 in `experiments/score_confirmatory.py`, and `33572fb`, the weight in `loss_weight_for_record`; item 12a). A run
  made before they were built does not implement them.
- **A gene knockout and an inhibitor of that gene's protein are nearly the same input.** Both reach the protein with
  sign -1 and magnitude 1, differing only in the entry hop, although a knockout removes the protein and everything it
  does while an inhibitor blocks activity and leaves it in place, at a partial occupancy, in the cells the drug
  reaches. The owner's direction of 13 October is that all three differences are to be made (occupancy from item 5's
  measured chain, exposure through the unbound brain ratio, and amount against activity), and that the third needs no
  node of its own for the inhibitor. None is built, and the first two change the graph's inputs, so they belong to the
  rebuild and to the physiology review it waits on.
- **Partial agonism is a halved magnitude in the agonist's direction, which is not what a partial agonist does.**
  `ACTION_TYPE_SIGN` maps a partial agonist, a positive allosteric modulator, a positive modulator and a stabiliser to
  +0.5 and a negative allosteric modulator to -0.5; on the v4 graph that is 357 entry rows at +0.5 and 19 at -0.5, over
  41 of the 222 drugs, of which 33 have no other kind of target. Two distinct errors sit in that bucket. A partial
  agonist's direction depends on the ambient tone, lowering signalling where the tone is above its intrinsic efficacy
  and raising it below, so a fixed +0.5 states one direction for both: aripiprazole at `DRD2` and `HTR1A`, varenicline
  at `CHRNA4` and `CHRNB2`, butorphanol at the opioid receptors, buspirone at `HTR1A`, with nalmefene, vilazodone and
  memantine alongside. And a positive allosteric modulator has no effect without the endogenous ligand, since it
  multiplies an existing signal rather than supplying one, which covers the benzodiazepines and the Z-drugs. Both would
  be answered by the same change, the drug's effect at a receptor scaling the endogenous ligand's state instead of
  adding to it, and that change is not linear, so it cannot sit inside the linear-response encoder without ending the
  linearity items 20 and 22 rest on. Registered as open.
- **Ligand binding competition is surveyed, computable and unbuilt.** `docs/label_source_review.md` 13.4 measured ten
  sources on 12 October: none labels competition for these drugs, and one route computes it from a shared binding site
  plus the two concentrations and affinities, which item 5's table holds for about half the drugs. The widest piece is
  already on disk, DrugCentral's displaced tracer per drug-gene record, which gives 1,021 of 1,307 same-gene drug pairs
  a shared tracer, with ChEMBL's curated site for 21 drugs where the GABA-A sites must be separated. Three limits are
  registered with it. Competition is saturable and so not linear, so it can enter only as a model input computed before
  the propagation and not as a relation inside it. The drug-against-endogenous half needs the endogenous ligand's
  concentration at the synapse, which no source constrains to within orders of magnitude, while its binding site is
  known for 85 of 147 targets. And there is almost nothing to test it on: of the 80 positive two-drug triples only 2
  have opposing actions at one target, and of the two-drug combination statements 19 distinct pairs share a target,
  7 of them with an affinity for both drugs at every shared target. It would therefore be pharmacology built into an
  input, not a tested claim, which is why it is registered as open rather than added (the owner, 12 October: "I don't
  want to add extra confirmatory model variations because that starts increasing probability of winning by luck").

**25. The held-out set is split on mechanism targets, not on drugs, and two readings are registered beside it**
(the owner, 13 October 2026: "NOT splitting on drug itself but splitting on each target individually (so each drug can
have some labels in the test/validation and some in the held-out but all of the labels for a specific mechanism are
consistently split across test and held out)"; "the memorization vs generalization seems like a defensible middle
ground though and i can also report a separate stratum for the unseen mechanisms as an estimate on generalization ...
do it and register all 3").

**Why the drug split cannot stand.** Over 200 full redraws at a held-out fraction of one seventh, **84.4 percent** of
held-out drugs have every target already present in a training drug, because the drugs genuinely share mechanisms: 58
of the 192 targets are held by six or more drugs. No grouping fixes it. Grouping hard enough to remove the sharing
gives a single block of 90 percent of the drugs, and the rare-target rule mitigates without eliminating, as the owner
said ("it doesn't truly stop leakage ... just mitigates it").

**a. The split: a partition of the targets, and a drug is held out whole when any of its targets is in it** (the
owner, 13 October 2026: "i'm actually thinking that's a better fit"). The drug is never trained on, and at test time
it is presented complete, so **the label is exact**: the drug's own observed symptoms are scored against the drug's
own targets.

**What is principled here is the rule, and what is a convention is the size. The registration says which is which**
(the owner, 13 October 2026: "we need a principled way of doing it instead of arbitrarily choosing a number of targets
for hold out, right?", and then, of an attempt to derive the size from the registered held-out fraction: "that's not
principled; it's just pushing the arbitrariness further down the chain"). They are right twice. A target fraction chosen
to reproduce the size the drug split happened to give is convenience; and deriving it instead from the registered
one-seventh only relocates the choice to one seventh, which is itself a convention.

- **The rule is determined by the hypothesis.** A drug is held out when any of its targets is, because the claim under
  test is about mechanism rather than drug identity, and this is what puts a mechanism the model never trained on into
  every held-out drug. Nothing about it is tunable.
- **The size is a convention**, and no construction inside a one-shot lockbox design can make it otherwise. The
  lockbox is drawn once and scored once; only cross-validation removes the choice, and that is a different design.
  What makes one seventh legitimate is not that it is derived but that it was fixed long before this split rule
  existed and is not tuned here.

**The rule governs the drug side; the gene side keeps the grouping it has.** Measured on the live graph, the rule
holds out 14.5 percent of the 222 drugs and so only 2.0 percent of the 1,636 perturbations, because 1,414 of them are
genes and a gene is drawn into it only when its own node is a held-out target. That is as it should be: the leakage
this rule exists to stop is between drugs sharing a mechanism, and the gene side does not have it. Genes are already
in 943 distinct groups with the largest holding 12 percent of them, against the drugs' 17 groups with the largest
holding 51 percent. So the held-out set is drawn on **each side at its own registered fraction**: the genes by the
registered disease-cluster grouping and the drugs by the rule below, one seventh of each rather than one seventh of
the whole.

The target count follows from that fraction: the targets are taken in the order the split's seed fixes and added until
the held-out share of drugs is as near one seventh as a whole number of targets allows. Measured over 200 draws
(`experiments/label_review/target_split_options.py`), that is **3.2 percent of targets**, 6.1 of 192, giving **14.4
percent of drugs** against 14.3, with a spread of 2.3 points.

**The design that has no convention in it, costed and not taken.** Leave-one-target-out: 192 folds, one per target,
nothing chosen. Median 2 drugs held out per fold, mean 6.4, largest 38 (17.1 percent), and 40.7 percent of a held-out
drug's targets seen in training, which is the same split quality the construction above gives (38.8 percent). Its cost
is 192 folds against the registered 60 runs: 192 x 4 configurations x 5 seeds is 3,840 runs. It is recorded here so
that the convention above is a decision taken against a measured alternative rather than for want of one.

What that buys: a held-out drug carries at least one mechanism training never saw, and **61.2 percent of its
mechanisms are new on average**, against the drug split where 84.4 percent of held-out drugs have **every** target
already in training. The residual, stated: the other 38.8 percent of a held-out drug's targets do appear in training
through other drugs, so the model knows part of its mechanism. That is the price of keeping the label exact.

**The registered alternative, and why it is not the primary.** The same sentence also reads as a split on the (drug,
target) **mechanism edge**, where a drug keeps labels on both sides and only its held-out target's contribution is
tested. That guarantees more - the mechanism predicted from is wholly unseen, 0 percent covered - but it costs the
label: the observed symptom was produced by the whole drug, so a partial mechanism is scored against a whole-drug
label, and the noise is one-sided. Since the study's task is (drug to symptoms) with whole-drug labels, the exact
label is worth more than the stronger novelty guarantee, and the edge split is registered here as the alternative
rather than taken. Both readings, and the two weaker ones, were measured before choosing:

| rule | held-out share | fully covered by training mechanisms | has a mechanism training never saw |
|---|---|---|---|
| drug, as drawn today | 14.3% | 84.4% | 15.6% |
| every target held | 3.1% | 81.1% | 18.9% |
| primary target held | 7.1% | 75.8% | 24.2% |
| any target held | 46.0% | 0.0% | 100% |
| **mechanism edge** | **13.8%** | **0.0%** | **100%** |

(that table is drawn at a held-out target fraction of one seventh, which is why `any target held` reads 46 percent
there; the fraction is a free knob and 3 percent is what the primary rule takes.) Neither of the two weaker readings
is taken: holding a drug out only when **every** one of its targets is held out reaches 3.1 percent of drugs and still
leaves 81.1 percent of them fully covered, and splitting on the **primary** target leaves 75.8 percent covered, since
a drug's other targets go on appearing in training.

**b. The permuted-target negative control carries the evidence on memorisation.** Already registered as item 4 and
read as the primary answer to whether the model uses mechanism or drug identity, because no split can settle it
structurally. Permuting which targets each drug has and retraining must lower the score; a score that survives the
permutation is drug identity and not mechanism, whatever the split.

**b2. A symptom is scored only when both sides of the split support it** (the owner, 13 October 2026: "the target
version doesn't guarantee all symptoms being trained either"). They are right, and it is measurable. Over 100 draws of
the rule in (a), a mean of **0.12 symptoms lose every training positive** (at most 1) and **1.05 fall below five**
(at most 2). The cause is visible in the table: one symptom carries a single positive in the whole of it and two more
carry 14 and 15, so a draw that takes that one positive leaves the symptom with nothing. A symptom in that state is
not merely unlearnable, it is **degenerate**: with its links and leak at their initial values the noisy-OR head
returns one fixed ranking of the perturbations for it, identical for every untrained symptom, driven by total module
activation, which is the degree-like quantity the input-size and degree controls already account for. Item 26c gives
the reason, which is an identity of the head rather than a measurement, and the measurement that confirms it
(`experiments/label_review/untrained_symptom_degeneracy.py`: correlation 1.000000, zero perturbations ranked
differently). Scoring it would be scoring the degree baseline under
a symptom's name.

The registered rule already requires **five kept positives in the lockbox** for a symptom to be scored, and that
stays. On the training side the condition is **not five but one**, and the owner's reason is the right one (13 October
2026: "i'm ok with the 5-kept positives for held out but not for training because including it could still help train
parts of pathways for other symptoms"). Two things follow, and they are separate.

- **Every symptom trains, whatever its count.** A symptom with two positives still sends gradient through the modules
  and the encoder, which are shared, so it helps the symptoms that do have support. Dropping it from training would
  throw that away for nothing.
- **A symptom is excluded from the score only when it has no training positive at all**, which is the degenerate case
  and not a thin one: at zero the links and leak never move from their initial values and the head returns the one
  fixed ranking. At two they move, badly, and a bad estimate is still an estimate, so it is scored and its count is
  reported beside it. Measured over 100 draws, that is a mean of 0.12 symptoms excluded rather than the 1.05 a
  five-positive condition would have excluded.

**The draw is not repeated until the condition holds**: rejecting draws on a property of the split would bias which
targets end up held out, which is exactly what the registration exists to prevent. Exclusion costs a symptom;
rejection would cost the split's meaning.

**c. A pre-registered secondary stratum for unseen mechanisms.** Scored apart on the held-out drugs **none** of whose
targets appears in training: the strictest reading available under the primary split, and **21.2 percent of the
held-out side** under the construction above, against the 15.6 percent the drug split would have given. It is the study's only estimate of extrapolation to a
mechanism never trained on, it is underpowered, and it is fixed here before the draw so it cannot be chosen after a
result is seen.

The held-out set is redrawn under this rule, which the owner's direction of 13 October permits ("doesn't have to
maintain current held out set because of the number of changes since that set was drawn").

**26. The nosology readout is a descriptive secondary analysis, reported apart from every prediction claim** (the
owner, 13 October 2026: "i accept the separated metrics for prediction (the 'any target held' version we mentioned
with the closest prefix before the previously registered 1/7 of targets version; not the full target xval because
that's way too expensive) vs nosology readout"). Item 25 governs the prediction side. This item fixes the other side
before any confirmatory run, so the grouping cannot be chosen after it is seen.

**a. What the readout reads.** For each symptom, its column of the module-to-symptom link probabilities, one column
per relation, fitted on all the evidence: `sigmoid(module_symptom_link_logit)[relation, :, symptom]`, 8 modules by 2
relations. That is the symptom's profile over mechanisms in the model's own basis, and clustering the symptoms by it
is the nosology question stated in the model's terms.

**The registration is on the quantity, not on the parameterisation.** If the head is later refactored so that the
links are a product of a shared module-to-latent matrix and a learned symptom vector (the owner's direction of 13
October: "we would remove module_symptom_link_logit and opt instead for a smaller output matrix that is fully
connected across modules and then learn symptom representations alongside that output matrix"), the readout object is
the same profile, recovered as that product, and nothing in this item reopens. The refactor itself is **not**
registered here; it is a head change, and it is listed below as the owner's.

**b. It is fitted in sample, which is legitimate here and is bounded.** The question is descriptive: which symptoms
this model produces through the same mechanisms. For a description, the estimator that uses all the evidence is the
right one. What it forfeits is stated rather than hedged: the readout carries **no** claim that the grouping predicts
anything held out, **no** claim about a symptom outside the set and **no** claim that it would recur in another
cohort. It enters neither H1 nor H2 nor P1, takes no part in the one-sided 0.025 sequence, and is reported in its own
section labelled descriptive. A reader who takes it for a validated nosology has been misled by the report, not by
the analysis, so the label is part of the registration.

**c. A per-symptom fold predicts nothing, and that is an identity. The symptom folds registered below do not
predict.** The identity first, because it fixes what a symptom fold cannot be asked for. With a symptom held out of
training and its own output parameters left at their initial values, its links stay at one common initial logit, so
its link probability is a single constant `c` across modules and

    P(symptom | perturbation) = 1 - (1 - leak) * prod_k (1 - c * activation_k(perturbation)),

where `leak` is the noisy-OR leak of that symptom, the background probability with no module firing, and not the
resting leak conductance of item 13. The product does not depend on the symptom. Two such symptoms are positive
affine maps of one another whatever their leaks, so they correlate at 1 and rank the perturbations identically; the
leak scales and does not reorder. The shared ranking falls as any module activation rises, so it ranks by total
module activation, the degree-like quantity the input-size and degree controls already account for. Measured at the
registered 8 modules and 24 symptoms over three seeds
(`experiments/label_review/untrained_symptom_degeneracy.py`, `docs/generated/untrained_symptom_degeneracy.json`): smallest
correlation between untrained symptoms 1.000000, **zero** perturbations ranked differently by any two of them,
against 0.47 to 0.80 once one symptom trains.

**This item previously read that a per-symptom fold is unavailable "at any parameterisation", and that was wrong.**
The identity above holds only while the symptom's own output parameters sit at their initial values. The
construction the owner specified does not leave them there, and the correction is their (13 October 2026): "i thought
we talked about only doing the symptoms xval in the way that trains a lower rank of output matrix params on the
whole data THEN uses those output matrix params for the per-symptom-folds xval, which is only valid because it's not
being used to test the ability to generalize to new symptoms", and "it doesn't matter how much it leaks held-out
labels. the point is to check for stability".

**d. Stability is measured by resampling perturbations. No symptom fold is registered** (the owner, 13 October
2026: "i don't know that the joint reading refit is worth it, tbh"). The folds were pursued through this item's
drafting and are recorded here as not taken, with the reasons, because the construction is an obvious one to
propose again.

**d1. Why no symptom fold.** Four findings, in the order they arrived, and each narrowed the fold until nothing
was left worth the runs.

- **A fold cannot predict the held-out symptom**, by the identity of (c). That rules out the first thing a symptom
  fold is usually wanted for.
- **The construction that does work predicts nothing either.** Fit the readout on all the evidence, freeze it,
  refit the encoder and modules on the other 23 symptoms, and read the agreement of the supports (decision 4.9).
  The leak of the held-out symptom's labels into the frozen readout is admissible precisely because nothing is
  scored, which is the owner's point ("it doesn't matter how much it leaks held-out labels. the point is to check
  for stability").
- **It does not test circularity**, which is what the fold was being kept for. A module driven by one symptom gives
  that symptom its own module and makes it an outlier, so it produces a vacuous attribution rather than a false
  grouping. Circularity is (e)'s question and only (e)'s.
- **What it does measure is covered, or thin.** Whether a module rests on evidence one symptom uniquely supplies
  decomposes into a degenerate module (module health and gate G1 catch it, with harder perturbations than removing
  one of 24 label columns), a module whose links sit on one symptom (the concentration below, exact and free) and a
  grouping resting on co-occurrence ((e), and the raw label column correlations). What no combination of those
  strictly implies is the joint reading, since the optimiser's behaviour is not a function of them, and that is a
  thin residue against 24 folds x 2 models x 5 seeds, 240 runs where the whole confirmatory is 60. Leave-one-out
  also perturbs weakly, 1 of 24 symptoms, so a module that holds says little and only a module that moves says
  anything.

**What is reported instead, at no cost beyond runs already registered**: the link concentration
`max_s link_ks / sum_s link_ks` of every module in the full-data fit, beside the same statistic from the
permuted-label runs, which is what concentration looks like when no symptom leans on anything and is the
comparison gate G1 already makes for supports. No threshold is drawn on it: (b) fixes that this item makes no
decision, so the concentration is reported as the continuous quantity it is. Were a module's dependence ever
wanted end to end, the scale for "it moved" is the seed-to-seed support Jaccard the five registered seeds already
produce, on the principle the registered floor rule uses, and the route that avoids refitting altogether is an
influence function, recorded and not taken because (basu2021influence) finds such estimates "often erroneous" for
deeper networks and the quantity here runs through the encoder rather than the head alone.

**Decision 4.9 falls with the folds.** Freezing the readout existed to pin module identity across symptom folds.
With no symptom folds, nothing in item 26 freezes anything, and nothing in it asks for a change to the registered
head.

**d2. The perturbation resampling, which is where symptom profile stability is measured** (the owner, 13 October
2026: "resampling on perturbations instead is fine", and "i guess i don't need profile stability under symptom folds
so much as symptom profile stability in general"). Complementary-pair subsamples of the training perturbations
(shah2013variable), refit with nothing frozen, and compare. The profiles move here because the readout is refitted,
which is the other reason a symptom fold could not have carried this reading: under (d1)'s frozen readout every
fold's profiles are identical by construction.

**The reading is at the level of the partition, not of the profile vectors, and that removes the alignment problem
rather than solving it.** The items being clustered are the 24 symptoms, which are the same in every subsample, so
two subsamples' clusterings are compared by one-to-one Jaccard over symptom membership (kuhn1955hungarian) with the
stability index and its interval of (nogueira2018stability), and no coordinate has to mean the same thing in both.
This matters because modules are exchangeable under a refit: a profile vector from one subsample is not comparable
to another's until the modules are matched, and the matching is imperfect whenever modules split or merge. A
partition reading never asks the question.

**The profile vectors are read only behind the module-stability gate.** Where the vectors themselves are wanted -
to say which mechanisms a cluster is built on rather than which symptoms are in it - the modules are first matched
one to one across the subsamples by support Jaccard, and the matched Jaccard is reported beside the reading. A
profile that moves when the module basis has moved says nothing about the symptom, so a low matched Jaccard makes
the vector reading uninterpretable and it is reported as such rather than as instability of the profile. The
partition reading of the paragraph above does not depend on this gate.

The permuted-label runs are the null for both readings, as they are for the supports.

**Neither fold is evidence that the nosology is right.** Both say the structure is reproducible under a perturbation
of the data. A stable grouping of the wrong thing is stable, which is what (e) is for.

**The procedure is fixed now.** Distance: one minus the Pearson correlation between symptoms over the concatenated
induces and relieves profile. Algorithm: hierarchical clustering with average linkage. Number of clusters: taken by
the stability criterion of (benhur2002stability), which also returns the absence of structure ("it provides a means
of rationally defining an optimum number of clusters, and can also detect the lack of structure in data", abstract),
so the readout is able to report that there is no grouping to report. The owner may change any of these before the
first confirmatory run. None changes after it.

**e. The control that decides whether the readout says anything: label co-occurrence.** A symptom's link column is
fitted only to reproduce which perturbations carry that symptom, so two symptoms reported for the same drugs get
similar columns whether or not they share a mechanism. Without a control the readout would recover the label
co-occurrence structure and present it as mechanism. So the same procedure of (d) runs on the symptom columns of the
raw outcome matrix, same distance, same linkage, same stability selection, and the two partitions are compared
cluster by cluster by the same one-to-one Jaccard. **No cluster that the label co-occurrence baseline also returns is
reported as a mechanism-derived grouping.** No threshold is chosen for that comparison: the scale is the mechanism
clustering's own resampling spread from (d), so an agreement inside that spread is read as agreement. What the graph
adds, if anything, is the difference between the two partitions, and that difference is the readout's only positive
claim.

**f. Thin symptoms are reported with their counts and cannot form a cluster by being untrained.** By (c) a column
that has barely moved from its initial value is close to every other such column, so symptoms with little support
would group together and the group would read as a nosological finding while being an artefact of count. The
clustering is therefore over the symptoms meeting the registered condition of five kept positives; symptoms below it
are placed afterwards at their nearest cluster and reported with their counts and no claim. The inclusive clustering
is a declared secondary, reported beside it.

**g. What this item does not settle, and stays the owner's.**
- **The head refactor of (a) is not needed by this item, and nothing else in it is either.** The refactor was
  proposed to make symptom folds possible, then looked load-bearing again as the only way to make profile stability
  measurable under those folds; the owner wants profile stability in general, which (d2) gives without freezing
  anything, and then the folds went altogether. So item 26 asks for no change to the registered head: no latent
  layer, no frozen readout, no new parameter and no free rank. What is left arguing for a refactor is shrinkage
  across symptoms for the thin ones, against an imposed rank, a latent basis in place of named modules, a free
  rank `d`, and another confirmatory variation unless it replaces the current head outright ("I don't want to add
  extra confirmatory model variations because that starts increasing probability of winning by luck"). Decisions
  4.7 and 4.8 keep the two latent forms and what separates them, set aside rather than refused.
- **Whether the readout is published with the confirmatory result or apart from it.** Registering it here fixes the
  procedure either way.

**27. A perturbation can drive a reversible reaction backwards: `product_opposes`, product -> reaction at -1** (the
owner, 13 October 2026: "The reaction should only be able to follow the reversal path under certain conditions",
and "I don't want to accept a perturbation not being able to reverse the reaction").

**Linearised mass action gives reversal without a nonlinearity.** The net rate of a reversible reaction is
`v = k_f [S] - k_r [P]`, so around the steady state `dv = k_f dS - k_r dP`: the product enters the rate at a
negative sign. A perturbation that accumulates the product therefore makes the rate deviation negative and the
reaction runs backwards against its baseline, regenerating the substrate and pulling the product back down; a
perturbation that raises the substrate drives it forwards as before. That is the conditional reversal the owner
described - it happens only when the local state calls for it - and it is linear, so it needs one derived edge and
no gate on the state. Linearity was never the obstacle; the obstacle was that I had framed reversal as switching
edges on and off, when in a deviation model it is the sign of the rate.

*(An earlier draft of this item argued that a nonlinearity was available anyway, "the softmax-mixture aggregator
runs inside the loop". Two things wrong with that, corrected 13 October 2026 when the owner asked why the
aggregator used softmax rather than a sparse maximum. The mixture is **not in the registered model** -
`cross_relation_aggregator` defaults to `mean`, so the registered linear-response loop is linear throughout and
its only nonlinearities are the cell-class bottleneck and the pH weight, both applied after it. And the mixture's
weighting is **sparsemax** by default and has been, returning exact zeros so that a node type either uses a
statistic or does not; only the command-line spelling `softmax_mixture` is historical. Neither changes this item's
conclusion, which needs no nonlinearity at all.)*

**What is built.** The linear-response encoder derives, for every `product_of` edge of a reaction flagged
reversible, the edge product -> reaction at sign -1 under its own relation `product_opposes`, whose gain is learned
and stands for k_r as the other gains stand for elasticities. An irreversible reaction gets none, because a
thermodynamically irreversible step is insensitive to its product. Carrier products, which have no depletion edge,
get none either, for the same consistency. `--reversible-reactions`, on for the linear-response encoder.
`tests/test_reversible_reactions.py` runs the encoder's own adjacency to a fixed point on a three-node chain and
reads the signs: a product rise gives a negative rate and a rising substrate, an irreversible reaction ignores it,
and the forward direction is unchanged.

**What it replaces.** `build_physiology_graph` wrote the mirror pair for every reversible reaction, substrate_of
and product_of in both directions at +1, so the reaction received +1 from its product instead of -1 and every
participant received +1 and -1 from the same reaction. 15,851 such pairs over the 5,713 reversible Human-GEM
reactions, and 1,809 metabolites whose field was identically zero under every perturbation. The build now writes
the nominal direction only, from the stoichiometric sign it already read, and the encoder **refuses** a graph that
still carries the mirror, because on that graph the nominal direction is lost and the derived edge would sit on top
of the cancellation. It therefore reaches a run only at the rebuild; `--no-reversible-reactions` runs the old graph
as it was.

**What it does not do.** It is linear, so it does not saturate: a reaction cannot run backwards faster than its
reverse capacity in the physiology, and here nothing bounds it. That is the limit of the linear response
everywhere and not particular to reversal. The resting direction is Human-GEM's nominal one; a thermodynamic or
flux source could set it per reaction before the propagation (decision 4.10). The message-passing encoder does not
yet carry the relation. And 16 pairs on Reactome reactions not flagged reversible still cancel: species listed on
both sides because one step consumes and regenerates them - GRIP1 and GRIP2, PICK1, the AP2 complex, CoQ and CoQH2,
neuronal K+ in channel gating. Their net stoichiometry is zero, and the right encoding is a modifier edge that
enables the reaction without being consumed or produced. Not built.

**28. The signed adjacency is scaled by `total_in_degree`, so the stoichiometric counts survive** (narrowed on 20
October 2026 to `forward_cone`, item 34a) (the owner, 13
October 2026: "setting mean as the aggregator doesn't sound very physiological though. Can you justify it?", then
"Set total in degree divisor as the normalization method default"). It cannot be justified as physiology, and this
item says so rather than defending it: mass balance at a metabolite is a signed **sum**, and the per-node divisor
exists so the row sums are at most one and the iteration contracts, which is a numerical requirement.

`in_degree` divides by the destination's in-degree **under each relation** and again by the number of relations
feeding it, so five producing reactions against one consuming reaction become one mean against another: 5/10 - 1/2,
exactly zero. That is why **7,811 of the 21,337 destinations with any input have an aggregate row sum of zero and
every one is a metabolite**, 92.3 percent of them, and why the direction at a both-produced-and-consumed metabolite
is fixed by the one gain ratio every metabolite shares rather than by its own stoichiometry.

Added 27 October 2026: the 7,811 of 21,337 count is finding 11 of `docs/research_summary.md`, measured on 7 October
2026 on the metabolic slice `data/processed/graph`, and the owner's ruling of that day ("ANY numbers from that time
are to have the same treatment") retires it as evidence. The arithmetic this paragraph states (5/10 - 1/2 = 0 under
`in_degree`; (5 - 1)/6 under `total_in_degree`) does not depend on the count and stands. The registered value
(`normalisation`, item 28, narrowed by decision 9.16) is not changed by this note; whether the owner wants the count
remeasured on the current graph before the registration is relied on is decision 9.104. Not a registered-rules change,
so no `Amends:` trailer.

`total_in_degree` divides by the destination's in-degree **summed over every relation**. The unsigned row sums are
one exactly as before, so the contraction is unchanged and there is no global shrink, while the same node gives
(5 - 1) / 6 and its sign comes from its own stoichiometry. The `spectral` arm also keeps the counts but divides by
a global 36.3 where the in-degree divisor is smaller at 98.8 percent of destinations, which shrinks the field
nearly everywhere and so makes two changes at once; `total_in_degree` separates them.

**What it does not fix.** The stoichiometric coefficients themselves are still read only for their sign, so a
reaction consuming two molecules counts as one (14.5 percent of both-produced-and-consumed metabolites touch a
non-unit coefficient, and the totals differ at 2.8 percent of those with equal reaction counts). The registered
per-edge demand of item 20 stays unbuilt. This item changes the counting of reactions, not of molecules.

**32. Three registered-but-unbuilt items are built: the per-type baseline, the stoichiometric demand and the
linear encoder's edge weights** (14 October 2026, the owner: "please finish implementing everything").

**a. Decision 4.6, a confirmatory baseline per perturbation type.** `type_popularity` and `type_degree_popularity`
join the baseline set that `run_baselines.py` fits and `score_confirmatory.py` reports. Each fits the symptom base
rate on the training perturbations **of the test perturbation's own type**, falling back to every training
perturbation where a type has none. A model that beats global popularity by learning that drugs carry more symptoms
than genes does not beat this one. The branch existed before the decision; what was missing was its name in the two
tuples, and `tests/test_registered_defaults.py` now holds both.

**b. Item 20's per-edge stoichiometric demand.** The graph build writes `stoichiometric_coefficient` on its reaction
edges, where before it read the coefficient for `is_substrate = coefficient < 0` and discarded the magnitude;
`LinearResponseEncoder.set_bottleneck_edge_demand_from_edges` maps it onto the bottleneck adjacency, keyed on
(relation, target, source); and the trainer calls it and records the counts. Three things are registered with it:

- a **derived** relation keeps demand 1, because `depletes_substrate` and `product_opposes` are built by the
  encoder from `substrate_of` and `product_of` and have no coefficient of their own in the edge table;
- a **fractional** coefficient is clamped to 1 and counted separately. Human-GEM writes half a molecule of O2, and
  a demand below 1 would raise availability across a step and take the bottleneck out of [0, 1], which
  `set_bottleneck_edge_demand` refuses. Clamping is a deviation from the stoichiometry rather than a reading of it,
  so it is reported;
- the consumer side works now and the **coefficients arrive with the v4 rebuild**. A graph built without the column
  keeps every demand at 1 and the trainer says so.

**c. Decision 4.11, the linear-response encoder reads `edge_weight` in its propagation adjacency.** Before this the
weight scaled a drug's mechanism (entry) edges only, so item 13's six conductance weights were inert in this
encoder while the message-passing encoder read them: the two registered encoders disagreed about the physics. **The
weight enters as a share**, the edge and its destination's divisor weighted together, so `sign * w / sum(w at the
target)` replaces `sign / count at the target`. Two reasons that agree: item 28 requires an unsigned row to sum to
1, the same contraction with no global shrink; and the Millman equation the electrical layer linearises uses
conductance **fractions** `g_ion / g_total` rather than absolute conductances, which is what item 13's weights mean.
With every weight 1 it reduces exactly to the unweighted form, and a test holds the two identical. A derived
relation inherits its parent edge's weight, each being the same physical edge read in the other direction.

**What is not built, and why, so the gap is not read as an oversight.**

- **Decision 4.12, the bottleneck over routes of the settled sign, was attempted and reverted.** Building it found
  that it conflicts with the registered linearity of the limiting-step rule: a ceiling that depends on the response
  is not an odd map. Two further findings and a third option are decision 4.12b of `docs/open_decisions.md`. The
  most consequential: selecting the route channel on the settled sign alone zeroes every downstream node of a
  knockout in an all-activating region, because no negative-sign route exists there, which would have cost the gene
  arm's 4,289 evidence rows.
- **Item 12's loader (8.5) and item 5c's occupancy input path (8.1) were unbuilt when this was written.** Both change
  a model input and both enter at the v4 rebuild in any case; after 4.12, neither was work to do at the end of a long
  pass. The loader was wired on 14 October 2026 (commit `016ff6a`, decision 8.5 on option (a):
  `assemble_evidence_table.py --open-targets-scoped-rows`, the class reaching the Dawid-Skene fit as item 12d
  registers); the occupancy input path is still unbuilt (decision 8.1).

**31. Item 14(a) is tightened to a central action, and a second medicines agency is read only where no
pharmacology section exists** (the owner, 13 October 2026: "I'm okay losing metoprolol and propranolol so 1 is
fine", and "Shouldn't it include looking at another regulator for the cases with no US label, though?").

**a. Part (a) requires a statement of central action, not of penetration.** Item 14(a) says "states a central
action" and the drugs admitted under it rested on sentences saying the drug **crosses the blood-brain barrier**,
which is a different claim and one part (c) already measures, quantitatively, as Kp,uu,brain. Read that way, (a)
was a weaker copy of (c) and the rule had two parts doing one job. The three parts are now independent: (a) a
qualitative statement of central action, (b) a brain-expressed mechanism target in the graph, (c) a measured
penetration at or above 0.1.

**The cost is paid, not avoided, and it includes two drugs this registration already admitted.** Tightening (a)
drops **metoprolol and propranolol**, both of which item 14 records as admitted and both of which rest on
penetration sentences ("Metoprolol is also known to cross the blood brain barrier ... CSF concentrations close to
that observed in plasma"; "Propranolol crosses the blood-brain barrier and the placenta"). It also drops felodipine,
indomethacin, nimodipine, omeprazole, granisetron, metformin and pindolol. **The direction matters**: every earlier
amendment to this rule widened it, and a rule each of whose amendments admits more drugs is being tuned, which is
what item 14 exists to prevent. This one narrows it.

**What survives is a reading of four drugs instead of twelve, and the reading is still the authority.** Of the
drugs outside the nervous-system code, four have a sentence naming them that states an action rather than
penetration: **codeine, cyclobenzaprine, hydrocodone and ondansetron**. That list is a shortlist and not a verdict.
The pattern that produced it cannot tell an assertion from a hedge: ondansetron's own label says "It is **not
certain** whether ondansetron's antiemetic action is mediated centrally, peripherally, or in both sites", which the
pattern counts as an action sentence and a reader would not. `docs/records/2026-10/label_central_action_reading.md` holds the
proposed reading of each; decision 3.2 is that reading and remains the owner's.

**a(i). The registered limitation of part (a): it filters on documentation, not on physiology.** Recorded on
14 October 2026 at the owner's instruction, with their ruling on the trade ("label noise is too much of a hinderance
vs a disclaimable data skew in the physio graph"). Whether a label asserts a central action depends on when it was
written and under which guidance, not on whether the drug acts centrally: codeine's label says "Codeine produces
respiratory depression by direct action on brain stem respiratory centers" while ondansetron's says "It is not
certain whether ondansetron's antiemetic action is mediated centrally, peripherally, or in both sites", and both
drugs act centrally to some degree. **Corrected 14 October, the same day, after the owner challenged the
first account of it** ("how can they be penalized by having BETTER structure to the data?! that sounds opposite to
reality and also solvable either way if the data isn't thinner just differently structured"). They are right on both
counts and the first account was wrong. It read: 13 of the 17 passing drugs pass on the older narrative CLINICAL
PHARMACOLOGY section and only 4 on the PLR-format MECHANISM OF ACTION subsection, which was offered as a skew
against better-structured labels. That comparison had no denominator. **With the base rates computed**: of the 80
drugs whose label carries both sections, **25 pass on both, 13 pass on CLINICAL PHARMACOLOGY alone, and zero pass
on MECHANISM OF ACTION alone.** So within one label the older section never loses and sometimes wins, which is not
a penalty on structure. **The cause is the reader, not the label.** The matcher requires the drug and a central
site in a single sentence under 600 characters, and a PLR label distributes that claim across subsections - the
mechanism in 12.1, the site in 12.2 or 12.3 - so a label stating "selective antagonist at the 5-HT2A receptor" in
one subsection and the receptor's cortical location in another states a central action that the reader cannot
assemble. The headroom is visible in the same measurement: PHARMACODYNAMICS is present for 69 drugs and yields a
passing sentence for 15, 21.7 per cent, where that subsection is exactly where a PLR label puts the site. So this
is a defect to fix rather than a property to disclose, and part (a)'s admitted set should be re-read once the
matcher can combine subsections. What survives as a genuine limitation of (a) is narrower: it still depends on a
label asserting rather than implying, so a drug whose central action no regulator wrote down in any form is
excluded on documentation. Because the three parts are independent after this item, a
drug needs a stated central action **and** a brain-expressed mechanism target **and** a measured Kp,uu,brain, and
the first and third both favour the well studied, which compounds the missingness decision 1.3(b) measured for
occupancy. **What follows from it, and is registered here**: the rule stands, because admitting a peripherally
acting drug with a symptom label would inject label noise into a confirmatory set; the skew is disclosed rather
than engineered around; and the excluded-but-plausible drugs are **reported as a named stratum** rather than
deleted from the record, the same treatment `has_measured_occupancy` receives. Two sources can narrow the gap and
neither is required by this item: human PET occupancy, already measured as reaching about one drug in eight but
disproportionately the modern ones (`docs/pet_occupancy_feasibility.md`), and the EMA public assessment reports,
whose terms are verified in `docs/data_sources.md`.

**b. A second medicines agency is read when, and only when, no pharmacology section could be read at all.** The
trigger is the absence of a section to read, which is a property of what is published and not of what it says. **A
label that was read is never re-litigated at a second agency**, because searching for a second opinion only where
the first was unfavourable selects the drug set on the outcome, which is the circularity item 14 exists to prevent.
("Medicines agency" throughout, never "regulator": in this project a regulator is a gene or complex that regulates
a reaction.)

**b(i). The trigger is narrowed from "no section" to "no statement on the question", on the owner's distinction of
14 October 2026.** Their words: "it's fine to search for secondary sources as long as we don't override a
pre-existing explicit label: an implicit label coming from a lack of data though is what i was thinking of". The
rule as first written triggered on the absence of a pharmacology section, which is a cruder proxy for what matters:
whether the label ever addressed central action at all. An exclusion that rests on a label's **silence** is an
inference from absence, and filling it from a second agency overrides nothing. An exclusion that rests on a label's
**statement** is a finding, and a second agency would re-litigate it. **The measurement that makes this operable, corrected the same
day after three faulty passes.** The first count said 17 silent and 7 mentioning; it used a classification pattern
whose own terms were wrong - "medulla" matches the **adrenal and renal** medulla, "neuron" matches a sympathetic
neuron and "cortex" the adrenal cortex. Re-measured with central-only terms and then checked phrase by phrase, the
24 drugs verdicted "no such sentence" break down as: **one false exclusion**, metoclopramide, whose label does state
a central action by its anatomy - "metoclopramide blocks stimulation of the CTZ by agents like l-dopa or
apomorphine" - which the vocabulary missed for want of the term "chemoreceptor trigger zone"; **three whose label
addresses central penetration and reports it as low or absent**, acebutolol ("only minimal quantities have been
detected in the cerebrospinal fluid"), verapamil (a CSF partition coefficient of 0.06) and mecamylamine ("crosses
the blood-brain and placental barriers", a penetration statement that part (a) stopped accepting), so these are not
silent and are excluded on what the label says; and **the remaining twenty genuinely silent on the central nervous
system**, whose exclusion rests on absence and which may therefore be completed from a second medicines agency.
**The matcher fix is correspondingly narrow**: two anatomy terms, "chemoreceptor trigger zone" and "area postrema",
and nothing else. A wider vocabulary was tried and rejected on what it admitted - gabapentin on a CSF-to-plasma
ratio, theophylline on "passes freely ... into the cerebrospinal fluid", verapamil on its partition coefficient and
lamotrigine on a hypothalamic-pituitary interaction, all four penetration or distribution statements that item 31
deliberately stopped accepting. A two-sentence rule pairing an action sentence with a nearby site sentence was also
built and removed as a measured negative: across the seven candidates it found one pairing, and that pairing was the
metoclopramide sentence, which carries drug and site together. `tests/test_central_action_vocabulary.py` now asserts
that the vocabulary matches no peripheral anatomy and that those three penetration sentences are not admitted, which
is the check the three faulty passes lacked.

**a(ii). The screen requires the sentence to name the drug, added 14 October 2026 and it changes the admitted
set.** The two anatomy terms of a(i) exposed something the screen had never required: amisulpride was admitted on
"D 2 receptors are located in the chemoreceptor trigger zone (CTZ) and respond to the dopamine released from the
nerve endings", which states where receptors are and not that the drug acts there, in a sentence that does not
mention amisulpride at all. **Measured before adopting, over the 17 drugs that passed without it: 11 survive and
6 are lost, and all six are lost correctly.** granisetron and palonosetron were admitted on "5-HT 3 receptors are
located ... centrally in the chemoreceptor trigger zone", receptor location rather than drug action; bisoprolol,
pindolol and timolol on class-level hypotheses about beta-blocking agents, naming no drug and hedged with
"postulated" or "possible"; and **metformin on "In mice, no glipizide or metabolites were detectable
autoradiographically in the brain or spinal cord"**, which is a negative finding about a different drug. A
sentence opening with "It", "the drug" or "this drug" satisfies the requirement, because a label uses those
constantly. **The net effect on part (a) is 17 passes to 12**: the six above leave and metoclopramide enters on
"metoclopramide blocks stimulation of the CTZ by agents like l-dopa or apomorphine". This is a correction rather
than a trade, so no compensating relaxation was made.

Seven drugs qualify, and they qualify for two different reasons that are both absences of a section:

- **No United States label exists** (openFDA answers HTTP 404): oxprenolol, celiprolol, penbutolol, etoricoxib and
  valdecoxib. Etoricoxib was never approved in the United States and valdecoxib was withdrawn from it, so for
  these the United States is simply the wrong jurisdiction to ask.
- **The United States label is an over-the-counter Drug Facts label, which has no pharmacology section**:
  loratadine and dextromethorphan. The screen reads `mechanism_of_action`, `clinical_pharmacology`,
  `pharmacodynamics` and `description`, all of them prescription-label fields that an over-the-counter label does
  not carry. A European summary of product characteristics puts the same material in section 5.1, so these are
  evaluable elsewhere and unevaluable here.

**c. A retrieval failure is not an absence, and one had hardened into a verdict.** `read_label_central_action.py`
cached every openFDA response including its failures, so a reset connection was returned on each later run as the
drug's answer. **Codeine had been recorded as "no label section read", 0 sections, on a cached
`Connection reset by peer`.** With the cache repaired to keep only a real response or openFDA's own 404, codeine
reads **24 sections and 36 candidate sentences**, among them "Codeine produces respiratory depression by **direct
action on brain stem respiratory centers**" - which passes the tightened (a) cleanly. So a drug was being excluded
by a network error.

**d. Part (a) reads a stated central action; a stated target belongs to part (b), and the division was tested.** The
screen keeps only sentences naming central anatomy, so a label that states a receptor mechanism without naming the
brain is not a candidate for (a). Codeine's own label says "Codeine is an opioid agonist relatively selective for
the mu-opioid receptor", which the screen never sees. That looked like a blind spot and was measured: of the 24
drugs recorded as "no such sentence", **20 carry a sentence naming the drug and a target with no central-anatomy
word** - and reading them settles it the other way, because they state what the target is rather than that the drug
acts centrally ("Verapamil hydrochloride is a calcium antagonist or slow-channel inhibitor"; "Celecoxib is a potent
inhibitor of prostaglandin synthesis in vitro"). A calcium channel or a cyclo-oxygenase is not a central claim, and
**whether a target is in the brain is what part (b) already tests**, from the graph's GTEx annotation rather than
from sentence matching. So the filter stands: (a) carries a stated central effect, (b) carries the target, and the
two are not redundant. Codeine loses nothing by it - `OPRM1`, `OPRD1` and `OPRK1` are all recorded as mechanism
targets and all three are brain-expressed. The fix is registered with the rule because it is the rule's input: openFDA's 404 is an answer
and is cached; anything else is retried.

**What this changes downstream.** The admitted set changes, so the perturbation set changes, so the leakage groups
and the held-out draw change. **This enters at the v4 rebuild of decision 1.2 or not at all**, which is the same
constraint item 12a registers for the Open Targets class.

**30. A protein complex carries the cell-class weight of its limiting member, at the complex node** (the owner,
13 October 2026, decision 4.2: "Taking the complex's limiting member weight per type makes sense i think but only
if it applies at the complex itself. That's what you mean, right?").

**Where it applies, and why there is only one place it can.** A complex is a `protein_entity` node that its members
reach by `member_of` and that reaches reactions by `catalyzed_by`, `activates`, `inhibits` and `substrate_of`, so a
response travels gene -> complex -> reaction and crosses the complex node. The encoder scales a response by the
destination's class weight at each step, so a weight on the complex gates every path through it exactly once, which
is what a complex is: an obligate subunit a class does not express shuts it there however abundant the others are.
Leaving the members to carry it alone, which is what happened until now, gates each path by whichever subunit it
arrived through, so an abundant subunit passes the response while another is missing - a maximum over the members
where a complex is a minimum. Putting it on the reaction instead would place the weight where the complex is not,
double-gate any path that also crosses the complex, and collide with the Human-GEM gene rule that already sets a
reaction's weight.

**The minimum is taken on the raw nCPM, per class, with the relative weight formed afterwards.** This is the order
`evaluate_gene_rule` already uses for "and", and a complex is the "and" of its subunits. The alternative, a minimum
over the members' relative weights, is a different quantity: the relative weight measures a gene's specificity
across classes, so two subunits with different top classes pull each other down everywhere. Measured, it leaves 55
percent of complexes above 0.9 in no class at all against 31 percent under the registered order
(`docs/complex_limiting_member_weight.md`), and a complex available in no class is one nothing propagates through
anywhere. **Per class** is part of the rule and not an implementation detail: the limiting subunit differs between
classes for 555 of the 1,523 complexes that carry a gate, so a single globally chosen subunit would be a different
rule.

**What it changes.** 1,523 of the 1,681 complexes take a gate, median 0.150, with 44 percent of complex-by-class
pairs below 0.1. The 387 reactions whose regulators are all complexes stop being flat in every class; 382 of them
take a gate. The 158 complexes no member of which carries expression stay at 1, the same convention the encoder
uses for metabolites, the membrane potential and reactions whose rule names no known gene. Gene and reaction
weights do not move. `build_cell_class_weights.py --no-complex-limiting-member` restores the previous behaviour, so
the change is measurable against it.

**H2's rewired-expression arm recomputes the complex gate too** (the owner, 13 October 2026: "Rewire the complex
gates for that control"). The arm permutes the Human-GEM gene rules and recomputes the reactions' cell-class
weights; a complex takes its gate from `member_of` edges and not from a rule, so without this the permutation left
all 1,523 complex gates intact and the rewired condition still carried real expression structure through them. The
rewiring already permutes `member_of` like every other relation, so what was missing was only the recomputation:
under `--recompute-reaction-expression-on-rewired-graph` a complex now takes the limiting member of whichever genes
the rewired graph says belong to it. **Every complex is rewritten, not only those the rewired membership gives a
gate**, because a complex whose real members carry expression and whose rewired members do not would otherwise keep
its real gate, which is the thing the control removes; such a complex takes 1 in every class. The counts go into the
run record (`member_of_edges_rewired`, `complexes_with_a_rewired_gate`,
`complexes_left_flat_by_the_rewiring`).

The flag keeps its name, `--recompute-reaction-expression-on-rewired-graph`, although it now reaches complexes as
well, because `experiments/evaluate_on_rewired_graph.py` rebuilds a finished run from its recorded arguments and a
rename would break that rebuild. A rebuild of a rewired run made before 13 October therefore changes its complex
gates, which is the correction 4.2b asks for; no confirmatory run exists to be affected.

**When it takes effect.** The weights file is rebuilt with the v4 rebuild of decision 1.2 and not before, because
the scorer checks the cell-class file's hash against the run being scored.

**29. Target occupancy is a model input; it is computed where its inputs exist, calibrated where they do not, and
flagged either way** (the owner, 13 October 2026: "I want into occupancy... it's needed for the physiology", and
"Don't REQUIRE occupancy though ... some drugs legitimately don't have it").

**It is not required of a drug.** Requiring it would drop 101 of 222 drugs and 24.7 percent of the kept positive
drug pairs, and the reason those drugs lack it is the literature rather than their pharmacology: all 101 have an
affinity at their targets, 42 lack a therapeutic range or concentration and 59 lack that and a fraction unbound as
well. It is also not the single-target case, which was considered and measured: 28.7 percent of the uncovered
drugs have one target against 29.8 percent of the covered, the same population.

**The placeholder is calibrated, not discarded** (the owner: "i don't want it to throw out the existing
occupancies just because they can't be calculated by that method. It should look at disagreements between the
sources and take the mean or median disagreement as an offset"). The calibration is applied to the
**concentration** and not to the occupancy: occupancy is bounded in [0, 1] and saturating, so an additive offset
on it is ill-defined near either end, while `occupancy = C / (C + Kd)` keeps the bound by construction and is where
the disagreement between the two methods actually sits. **The form is a slope and a bias, registered as item
5c(ii)**; the median disagreement this sentence first named, a constant 2.1 times, was measured and withdrawn,
because it both leaves a dependence on affinity that it cannot reach and makes the best mechanism target's
occupancy a constant across every imputed drug.

**Amended the same day: the four steps of the procedure are registered as item 5c** (the owner: "keep off targets
but always use a measured value then impute all values to get the calibration shift and apply it to only the
imputed values that have not been measured"). Off-targets are kept, a measurement always wins over an imputation,
the placeholder is computed for every drug so that the shift is estimated on a like-for-like overlap, and the
shift is applied only where no measurement exists.

**Every drug therefore carries an occupancy, which removes the confound a missing one would have introduced**:
without it the two groups carry total input with medians 1.00 and 3.0, and which group a drug falls in is whether
it has a published therapeutic range and fraction unbound, a quantity that tracks how long and how widely the drug
has been studied and so correlates with its label count by the same route.

**Corrected 13 October 2026.** This paragraph read "every drug therefore carries an occupancy on **one scale**",
which claims more than the procedure delivers and claims the wrong thing. The two groups are not on one scale: one
carries measurements and the other imputations corrected towards the measurements by a median offset, with 1.14 log
units of scatter left around it. The calibration removes the systematic difference between the groups, not the
difference itself, and nothing displaces a measurement with an imputation (item 5c, step 2). The wording read as if
every drug were put on the placeholder scale, which is what prompted the owner's "put the measured values back" and
the withdrawn item 5b.

**Two limitations are registered with it, and neither is removed by the calibration.**

- **A calibrated placeholder is not a measurement.** The scatter about the offset is 1.14 log units, about two
  orders of magnitude of drug-to-drug disagreement, and no single offset touches it: correcting moves the drugs
  whose concentration lands inside their own measured range from 27 percent only to 30, and the median absolute
  error from 0.75 to 0.70 log units. The bias is what a calibration removes and the scatter is what it does not,
  so **`has_measured_occupancy` is carried as a stratum** and every reading is reported within it as well as over
  all drugs. An imputed concentration carries roughly a ten-fold uncertainty, and how much of it reaches the
  occupancy is `d(log theta) / d(log C) = 1 - theta`, which falls monotonically as the occupancy rises: a saturated
  occupancy absorbs the error, one at `Kd` absorbs half, one near zero passes it through almost whole. (Corrected
  13 October 2026: this read "which an occupancy near saturation absorbs and one near `Kd` does not", which has the
  relation as a U shape rather than monotone and so understates how badly a low occupancy behaves. The correction
  strengthens the case for the stratum rather than weakening it. The withdrawn item 5b also rested on
  the monotone reading, which was the sound part of it.)
- **The offset is estimated where it is least needed, and it does not transfer.** It comes from the drugs that
  have a measured concentration, which are the better-studied ones, and is carried to those that do not. The owner
  accepted this as a stated limitation on 13 October ("That's a valid limitation. Just record it"), and this item
  then said "nothing available measures whether it does". **That was wrong, and item 5c step 3 is what makes the
  measurement possible**: imputing every drug, including the measured ones, puts a placeholder beside each
  measurement and the disagreement can be read against anything observable for both groups. Read against the best
  mechanism affinity it is not flat. The placeholder is `C = 9 * Kd` of that target, so its log concentration
  falls with affinity at a slope of -1 by construction, while the measured concentration falls at -0.532: a more
  potent drug is dosed lower, but only about half as much lower. The remainder stays in the disagreement, no
  constant reaches it, and the drugs the shift is applied to are the more potent ones, a median 0.59 pK above the
  drugs it was estimated on. **So the constant shift is withdrawn and the calibration is a slope and a bias**, item
  5c(ii), on the owner's ruling of 13 October ("A slope plus bias calibration is better. Do that instead"). The
  slope's bootstrap interval excludes 1.0 and the out-of-sample error falls from 0.852 to 0.524 log10
  (`docs/occupancy_coverage_and_shift_transfer.md`). This limitation is therefore answered rather than stated, and
  is no longer the same shape as the extrapolation registered for the Open Targets agreement in item 12d, which
  stays untested. What replaces it is narrower and is registered with 5c(ii): the calibration still does not make
  the imputed group's occupancy distribution match the measured one, so `has_measured_occupancy` stays.

**What this item leaves to others, none of it open.** Off-targets all enter the input at their occupancy, which
is item 5c step 1: occupancy is the magnitude, so an engagement near zero contributes near zero and no threshold is
needed or wanted. The held-out split is on **mechanism targets** and off-target sharing is reported rather than
split on, which is item 25 with its secondary stratum 25c. (Corrected 13 October 2026: this paragraph said "the
occupancy threshold above which an off-target enters the input is decision 1.3 and remains the owner's". There is
no such threshold and there never was. `docs/generated/off_targets_under_the_target_split.md` measures what admitting
off-targets to the **split** would cost, which is a sensitivity reading of an alternative item 25 had already
declined; promoting its "the threshold is the dial" into an open decision invented one. The owner: "I thought we
already settled on option three".) The conflict with item 5 is closed by item 5a, which lifted the prohibition on
the calibrated placeholder: item 5b withdrew 5a and was itself withdrawn as a misreading, and item 5c registers the
procedure. One finding of the 5b measurement outlives it and is recorded as section 9 of `docs/open_decisions.md`:
the target role is a proxy for position on the saturation curve that fails in the tail, so the role is not a sound
basis for any rule and `has_measured_occupancy` is the right instrument, which is what this item already uses.

**What this amendment does not change.** The two tested models and the noisy-OR head of each, the decision rule, the
one-sided 0.025 sequence of H1 then H2, the floors, the degree strata, the node descriptor table, and the training
stopping rule, which stays validation loss with patience 8 and at most 60 epochs. The head choice is not reopened: the
sigmoid head was dropped from the confirmatory family on 8 October because only the noisy-OR head has modules to read
as pathways.

**What is still open, and is deliberately not registered here.**
- ~~**Off-targets in a model input.**~~ **Closed 13 October and registered as item 5c; this bullet is kept because
  the question was re-opened in error after it was settled.** The objection recorded here - that admitting off-targets
  at any threshold from 0.1 to 0.5 takes the largest leakage group to between 203 and 209 of the 222 drugs
  (docs/label_source_review.md 14.3) - was measured against the **group** split that item 25 has since replaced, and
  it largely falls under the target partition: held-out drugs reach 14.1 percent on mechanism targets alone and 14.7
  with off-targets at occupancy 0.25 or 0.10, against the registered 14.3, because item 25 solves for the fraction
  that gives the registered share. What off-targets cost under item 25 is novelty rather than size, and that cost is
  reported rather than split on (item 25c). **Settled: every off-target enters the input at its occupancy (item 5c
  step 1), the split is on mechanism targets (item 25).** See decision 1.3(g).
- **Which held drugs of item 14 are admitted once their missing part is supplied**, narrowed twice since this bullet
  was written. The rule is registered and item 31 tightened part (a) to a stated central action, which drops nine
  drugs that penetration alone had admitted. Of the four held drugs, the search of 13-14 October
  (`docs/records/2026-10/four_held_drugs_search.md`) resolves two: **carvedilol** against admission on positive evidence, since it is
  a P-glycoprotein substrate at the blood-brain barrier with brain uptake rising up to three-fold under cyclosporin A
  (Bart et al. 2005, doi 10.1038/sj.bjp.0706283), which puts Kp,uu,brain below 1; and **timolol** as unmeasured,
  its Kp,uu,brain being absent from all 34 Kp,uu tables and from PubMed. **Oxprenolol and pindolol are blocked by a
  human check at the UK eMC**, recorded as a refusal under the 11 October ruling and not routed around, so reading
  `medicines.org.uk` for Trasicor and pindolol is the user's. Separately, the reading of (a) shortlists **codeine,
  cyclobenzaprine, hydrocodone and ondansetron** - four, not the twelve this bullet's era carried - and a shortlist
  is not a verdict: ondansetron's own label says "It is not certain whether ondansetron's antiemetic action is
  mediated centrally, peripherally, or in both sites". The superseded `configs/admitted_atc_prefixes_draft.csv`
  records what was considered under the old group rule. See decisions 3.1, 3.1b and 3.2.
- **The reach of the electrical layer, which is an aggregation question and not a wiring one.** Item 13 below
  registers the computed potential. What it does not fix is the magnitude of what arrives at `VM_c`, and the
  measurement of 12 October withdrew the diagnosis this item used to carry: the binding divisor is the in-degree of the
  ion pool (364 cytosolic sodium, 339 extracellular) and not the 405 at `VM_c`, so deleting the reaction edges lowers
  the field there by a factor of 26 rather than raising it (docs/label_source_review.md 27.5). Both alternatives the
  encoder already carries were measured worse in magnitude, so this stays open and is disclosed rather than fixed.
- **The held-out set itself**, which is drawn only on the user's go-ahead ("Don't finalize the lockbox until I've
  given the go ahead").


Amendment, 24 October 2026, written before any lockbox run and before the held-out set has been drawn.

**33. No drug is set aside for joining leakage blocks: items 1(b) and 16 are withdrawn and orphenadrine is in** (the
owner, 24 October 2026, on being told why orphenadrine was set aside: "why are we setting orphenadrine aside?!", then
"then undo that and include orphenadrine"). Item 1(a), no limit on a drug's mechanism targets, stands and is now built:
`scripts/rebuild_data_layer.sh` passes `--max-drug-targets 0` to the OnSIDES and evidence steps of v4 and v5.

**Why the rule is withdrawn.** Item 1(b) existed to protect a split. On the table of 12 October, under the grouping in
force that day (a drug joined to every drug sharing a target node), orphenadrine's targets lay in both large blocks
and with it in the largest block held 194 of 230 drugs (`docs/label_source_review.md` 26.1). Item 25 replaced that
grouping on the drug side the next day: the held-out set is a partition of the mechanism targets, and a drug is held
out whole when any of its targets is in it, so no drug-to-drug chaining forms the blocks the rule was written against.
Item 25 was registered without revisiting 1(b) or 16, so the exclusion outlived its reason. Removing the drug also
removes a mechanism, the reason item 16 gave for keeping tapentadol, and the owner's rule of 21 October 2026 is that a
choice made for a non-physiological reason needs a stated justification; the only one on record was the old grouping.

**What it costs is not measured.** What orphenadrine does to item 25's partition (the solved target fraction, the
held-out share, the unseen-mechanism stratum of 25c) has not been measured on any table: the 12 October numbers are
for the chained grouping and are not evidence about item 25. It is read on the rebuilt table, before the draw, with
the graph version and date it was taken on. Every count of drugs in items 1, 16 and 25 that assumed orphenadrine out
moves by one drug at the rebuild.

**What this amendment does not change.** Item 25's split and its two readings, the central-action rule of items 14
and 31, and every model, test and threshold.


Amendment, written 25 October 2026 for the changes registered between 20 and 24 October 2026, before any lockbox run
and before the held-out set has been drawn (decision 1.1 is open).

**34. Four registered rules changed between 20 and 24 October 2026; this item states them in the registration** (the
owner, 25 October 2026: "Amend it"). Each change was made in `configs/registered_rules.json` with an `Amends:` trailer
and is listed in `docs/amendment_history.md`, but this document was not amended with them, so until today its text
still stated the earlier rules. The four are below in the order they were registered. Every one was outcome-blind:
no lockbox has been drawn, so no confirmatory result existed to see. The earlier text is kept as the record and is
marked where it states the superseded rule.

**a. The normalisation is `forward_cone`, which narrows item 28** (decision 9.16; registered 20 October 2026 in commit
`e9758bd`, merged with pull request #8 on 22 October 2026). The owner asked for the per-seed divisor on 14 October
("do the per-seed cone divisor then") and for it to be wired in on 20 October ("can you please implement that"). The
registered rule: each edge is divided by the destination's in-degree summed over every relation, counting only the
edges whose source the seed can reach, per seed, so the unsigned row sums over the edges that carry are one. Item 28's
`total_in_degree` is the same divisor counted over every edge, and the two coincide wherever a seed reaches every node.
Item 28's reasoning stands: the divisor is a numerical requirement for the contraction, not physiology.

**b. One model is tested: the noisy-OR configuration of the linear-response encoder** (decision 9.77; registered 22
October 2026 in commit `342c62d`). The owner: "Defer it to robustness. I don't want it constraining things because
this is more about mechanistically identifiably predictive nosology". `tested_models` is
`confirmatory_v2_linear_response_noisy_or` alone, and the new rule `robustness_models` holds
`confirmatory_v2_message_passing_noisy_or`, which is read and reported with its intervals outside the tested family
and spends no alpha. `configs/head_choice.json` records the tested model under `chosen` and the other under
`robustness`. Both encoders keep the noisy-OR head. A robustness reading that disagrees is reported as a disagreement
and cannot withdraw the tested model's result. What is given up is the corroboration that a second tested encoder of
a different inductive bias would have given.

**c. The one-sided level is 0.05** (decision 9.78; registered 22 October 2026 in commit `8174d18`). The owner: "Move it
back to the .05 alpha please with just one model now". The level was halved to 0.025 on 8 October 2026 only because
two models were tested without a correction across them; with one tested model the registered familywise 0.05 is
carried by one test. H1 comes first, then H2 and P1 by Holm at the same level, so the smaller of their two p-values
faces 0.025 and the larger 0.05. Item 18 is not edited, by decision 9.78: the rule it states is unchanged, and its
"0.0125" now reads 0.025.

**d. The labels' likelihood counts each pair once, as a positive-unlabelled code length; it replaces item 3's weighted
loss** (decision 9.90; registered 24 October 2026 in commit `039bbd8`, merged with pull request #17 the same day). The
owner, 22 October 2026: "labeled / unlabeled costs formulation accepted" and "each label should only be counted once in
the MDL calculation". With f the probability that the link is real, pi the labelling propensity, b the false-report
rate and a the power behind an evidenced negative, a labelled positive costs -log(b + (1 - b) pi f), an unlabelled pair
-log(1 - b) - log(1 - pi f) and an evidenced negative -log(1 - a f). The registered values: pi at the median literature
popularity is w + (1 - w) r(t, s) per perturbation type and symptom, w = 0.2 and r(t, s) the cell's labelled share on
the fit rows, with one popularity slope learned when a literature table is named; b = 0; a is item 3's
n_effective / (n_effective + 214.39), 0.5 where the label states no arm sizes. Every counted pair weighs one, so the
evidence weights, `--negative-weight` as a weight and `--positive-target` are not read, and item 3's placebo weights
now supply a and are no longer loss weights. `--equal-drug-shares` stays on. Item 3's weighted loss is kept as the
`--label-likelihood weighted` arm. The choices decision 9.90 lists as the owner's, (b) to (h), stay open there.

**What this amendment does not change.** The noisy-OR head, the order H1 then H2 and P1, the absence of a magnitude
floor, the group bootstrap and its resamples, item 25's split and every threshold. Counts of confirmatory runs written
before 22 October 2026 (the 60 of items 25 and 26) counted both encoders; whether the robustness model also runs its
permuted and rewired variants is not settled by this item.

**35. The membrane potential is computed from the ion pools and the reaction edges are not made** (the owner, 26
October 2026: "so then definitely compute it by the pools"; decision 9.87, registered in `configs/registered_rules.json`
as `membrane_potential_build` with an `Amends:` trailer). Item 13 registered `computed_beside_the_reactions`, which
keeps one edge from each reaction that moves net charge beside the six weighted pool edges. Its reason was a
measurement made under the `in_degree` divisor, where the two relations at `VM_c` split the input in half; under
amendment item 28 and the `forward_cone` divisor of item 34a the divisor at `VM_c` is 1 + R, R being the 412
charge-moving reactions on the build of 20 October 2026 (**called v5 here until 28 October 2026**, when the owner ruled it an early build a session made unasked and not v5: `graph_full_neuronal_split_binders_drugs_v5` from `main` at `344d211`, decision 9.106; the count is remeasured on the real v5 under 9.87 (b)), so the conductance law arrived at 1/413 of itself and every
reaction edge outweighed every pool edge. Under `computed_from_the_pools` the divisor is 1 and the law arrives whole.
The reactions still reach the potential, through the pools whose contents they move. Outcome-blind: no lockbox has been
drawn, so no confirmatory result existed to see. What item 13 registers about the law itself is unchanged, including
why it is the parallel-conductance equation and not Goldman-Hodgkin-Katz, and so is its registered claim, the
subthreshold steady state. Still owed, and not settled by this item: the field at `VM_c` measured under item 28 and the
cone divisor for all three builds, which decision 4.1 and decision 9.87 (b) both owe.

**36. The species-translation disclosure of item 15 is re-justified without the Fagerholm preprint** (the owner, 25
October 2026: "Exclude the Fagerholm preprint unless you find a peer reviewed version", quoted in a session note, and
26 October 2026, approving that the exclusion be recorded rather than the citations deleted, and stating the
reason of record: "just say that the fagerholm paper was excluded because it was not peer-reviewed and had a potential
conflict of interest"; decision 9.100). A Fable pass of 26 October 2026 found no peer-reviewed version by three
routes, so the condition is not met; the conflict is that the author is at Prosilico AB, whose ANDROMEDA
prediction software the preprint's own methods use, so the paper evaluates data against a product of its
author's company. The preprint's coefficients are withdrawn from every claim. Nothing measured changes: no value was
ever taken from it. The disclosure
item 15 registers is kept, because the fact that drives it is the project's own, and reads from today:

> the values are predominantly non-human (Kp,uu,brain from human 13, non-human primate 8, other animal 73;
> `docs/drug_exposure_table.md`), and cross-species Kp,uu,brain translation is imperfect and substrate-dependent
> (Langthaler et al. 2023: minipig against rat within 2-fold for 47 percent of 17 compounds on literature free
> fractions, the condition this project's collated values meet, and 71 percent when both species' free fractions are
> measured in one assay; Sato et al. 2021: a rat, monkey and human model predicting Kp,uu,brain within 3-fold of
> observed for 71, 73 and 79 percent of compounds), with the largest species differences, 4-fold, in transporter
> substrates such as paliperidone and buspirone, both of them study drugs, so the species translation is an
> unquantified error on this input and no claim rests on its absolute scale; the rat-to-human R² of 0.01 cited until 26 October 2026 is withdrawn with the preprint and no
> coefficient for rodent-to-human transfer is asserted.

**This is weaker than what it replaces, and the registration says so rather than leaving the rodent values looking
better supported than they are.** (**Corrected 26 October 2026, after the owner supplied the Langthaler full text**:
the clause above first read "comparable for most compounds (Langthaler et al. 2023, minipig against rat 71 percent
within 2-fold, n=17)" and named risperidone as the exemplar, both taken from the abstract. The full text gives three
figures for that pair, of which 71 percent is the best and holds only where both species' free fractions come from
one assay, and it places risperidone among the *closest* agreements instead. "Comparable for most compounds" is not
supportable at 47 percent and is withdrawn. Decision 9.100 holds the detail.) Neither replacement source reproduces a near-zero correlation, and neither measures
rodent against human directly: Langthaler's figures are minipig against rat, and its only quantitative human
comparison is of total Kp,brain on four compounds, with the Kp,uu,brain agreement against human explicitly worse
and unquantified,
and Sato scores a mechanistic model against observations within each species. The quotes, the routes and what each
source does and does not support are in `docs/label_source_review.md` section 38. Outcome-blind: no lockbox has been
drawn. Not a registered-rules change, so no `Amends:` trailer: item 15's registered rule is the set of Kp,uu
spellings the table matches, which is untouched; what changes is the disclosure registered beside it.

**Added 27 October 2026: the measurement-noise floor on the free-fraction input rests on Kazmi et al. 2026, and
Fagerholm et al. 2021 is cited only with its conflict stated** (the owner, 27 October 2026, ruling on whether the
peer review of Fagerholm et al. 2021 is reputable enough to rest a noise floor on: "cite it with the asterisk of
potential conflict so use the kazmi paper as the noise floor instead for item 36", and, on the journal,
"Xenobiotica sounds reputable enough but see previous sentence"; decision 9.102). **This adds a second error term
to the same input and changes nothing about the first.** Item 36 above is about translating a Kp,uu,brain value
**between species**. This clause is about the reproducibility of one of the two free fractions that quantity is
built from, **within** a species and **between laboratories**. The two are independent and neither bounds the
other. Registered beside the disclosure above, which now reads with this next to it:

> the unbound plasma fraction that enters Kp,uu,brain is itself a collated measurement with a between-laboratory
> noise floor: across eleven pharmaceutical companies measuring the same twenty compounds, intracompany precision
> was a coefficient of variation under 30 percent while the average cross-company coefficient of variation was
> about 70 percent (Kazmi et al. 2026, the IQ Consortium protein-binding working group), so a free fraction
> collated from the published literature carries a between-laboratory error two to three times the
> within-laboratory error, and the collation records neither the laboratory nor the assay conditions that would
> let it be corrected. Three qualifications are registered with the figure. All twenty of those compounds are
> highly bound, unbound fraction below 1 percent, so the figure is from the hard end of the range and is not an
> all-comers figure. Only the equilibrium-dialysis leg is an eleven-laboratory comparison; the flux-dialysis and
> plasma-P450-inhibition-shift legs were each run by one company. And the figure is for the fraction unbound in
> **plasma**: Kp,uu,brain = Kp,brain x fu,plasma / fu,brain, so it bounds the plasma term alone, there is no
> published between-laboratory figure for the unbound brain fraction or for Kp,uu,brain itself, and no claim rests
> on the absolute scale of either.

**Why the noise cannot be corrected out by stratifying on the assay**, which the owner asked on 27 October 2026.
Within equilibrium dialysis the dialysis device is worth less than 1.25-fold for 14 of the 20 compounds, and for
six of them - fingolimod, itraconazole, lapatinib, venetoclax, verlukast and zafirlukast - the high-throughput
device reads "2.1-fold to 3.4-fold greater" than the rapid-equilibrium device (Kazmi et al. 2026, section 3.4,
p. 9). The effect is real, compound-specific, and given with no conversion coefficient, so it yields no correction
that can be applied to a collated value whose device is unrecorded, which is every value in this project's table.
Accuracy against the three-method consensus is registered with its curation state rather than loosely: before post
hoc curation "10 of 11 companies achieved >80% reported values within 3-fold of the overall consensus f[u] value"
and "Seven of 11 companies achieved an overall average absolute fold error (AAFE) <= 2", with one company at 60
percent within 3-fold and an AAFE at or above 4.6; after curation, 9 of 11 at AAFE <= 2 (section 3.2, p. 8), while
the Discussion gives 6 of 11 for the curated set (p. 10) and the supplemental tables that would settle the
difference were not supplied.

**Fagerholm et al. 2021 is cited, and only with the conflict stated.** Its 2.0-fold median and 185-fold maximum
max-to-minimum laboratory ratio over 117 compounds (Xenobiotica 51(10):1095-1100, PMID 34346291) is the only
figure of its kind on a large all-comers compound set, and it **is** peer reviewed, so decision 9.101's exclusion
does not reach it: Xenobiotica is MEDLINE-indexed, verified by four routes, and actively covered by Scopus from
1971 to 2026 on Elsevier's own source list; the publisher states a double-anonymised review model, and its
deposited dates show one revision round on this paper. What that review could not cover is the conflict. All three
authors are at Prosilico AB and the paper benchmarks laboratory variability against that company's own in silico
prediction method, which is the structure decision 9.100 objected to in the excluded preprint; and under a
double-anonymised model the referees were not shown the authors, so the review could not have weighed that
interest even in principle. **The direction of the incentive is registered with the figure, because it decides how
the figure may be used**: a *larger* measured laboratory spread makes the company's predictions look comparably
reliable, so the incentive runs toward overstating the spread, and the figure is therefore **not** a conservative
bound and is not treated as one. **No unconflicted source reproduces it.** It has been cited, once substantively,
in an independent peer-reviewed review - Ancuceanu et al. 2025, which repeats the 185-fold maximum and the "about
20% of the compounds in a data set of 117 substances showed over 5-fold lab variability" statistic and not the
2.0-fold median - but as of 27 October 2026 no group outside Prosilico has reported its own median
max-to-minimum laboratory ratio for human fu,plasma over a comparable compound set.

**The three unconflicted sources added with this clause, and what each does and does not measure** (the owner,
27 October 2026: "the 3 unconflicted ones should be added"). None of them is a second measurement of the
Fagerholm quantity, and the registration says so rather than implying corroboration. **Wang et al. 2014** (Merck
Research Laboratories) is the standardised within-company case: two laboratories of one company under a single
analytical procedure, six commercial compounds on three days at each site, with **no between-site fold figure
stated** and the qualitative result that after standardisation "data consistency across and within sites was
extremely high". **Ryu et al. 2019** (Pfizer) agrees "generally within 2-fold" between equilibrium dialysis and
ultracentrifugation on 10 highly bound drugs - the same number as Fagerholm's median and a different quantity,
two methods in one laboratory rather than many laboratories. **Lynn et al. 2025** (US Environmental Protection
Agency, with NOAA and RTI International) compares the plasma free fraction across human, rat and rainbow trout for
54 environmental chemicals, finds that "rat plasma generally demonstrated higher f[u,p] values for chemicals than
human", and reports that chemicals above a log Kow of 4.5 are "difficult to measure, and have low reproducibility
across laboratories" - a property-dependent qualitative claim drawn from its comparison with literature values,
not an interlaboratory measurement of its own, since its assays were run in one laboratory. Lynn is also the first
source in this repository to give a directional rat-against-human difference for fu,plasma, so it bears on item
36's species clause above as well as on this one.

**What arithmetic derived from these papers is allowed to be.** Two figures this project finds useful are computed
by Fable passes from numbers the papers publish, and neither is stated or concluded by its paper, so both are
reported as derived with the source named and neither enters a registered claim: from Kazmi et al. 2026's Table 1
literature ranges, a median max-to-minimum laboratory ratio of 3.33-fold over the 13 of 20 compounds that carry a
range, all 13 above 2-fold and the worst at 15.3-fold; and from Wang et al. 2014's Table 4 per-site per-day
values, a median site-to-site ratio of 1.29-fold over six compounds, site 2 above site 1 for all six, with a
median max-to-minimum of 1.61-fold across the six observations per compound. Read as a ladder they say the thing
the registration needs: a standardised assay inside one company runs at roughly 1.3-fold between its own sites,
eleven companies each on their own protocol run at about 70 percent cross-company coefficient of variation, and
values collated from the published literature run at a few-fold max-to-minimum per compound. **This project's
inputs are in the last of those three conditions**, so the spread is attributable to heterogeneity of conditions
between laboratories rather than to an irreducible limit of the assay - which Wang et al. 2014 supports
mechanistically, naming loss of dialysis-membrane integrity from pipetting as the single largest source of error
and standardisation as the remedy, and which it supports by its own history: a standardisation programme running
since 2007, under which "site-specific protocols have been replaced with a single analytical procedure for each
assay", had still left that company's two laboratories incubating under different conditions when the measurement
was made, and the 1.29-fold figure above is what remained once those differences were found and removed.

**What this addition does not change.** No value in `docs/drug_exposure_table.md` or any other table moves, and
nothing is admitted or withdrawn: all three new sources are cited in the disclosure and nowhere else, as
Langthaler et al. 2023 and Sato et al. 2021 already are. The species-translation disclosure above stands word for
word; this clause sits beside it as a second, independent error term on the same input. Outcome-blind: no lockbox
has been drawn - decision 1.1 is open and waiting on the owner's go-ahead ("Don't finalize the lockbox until I've
given the go ahead"), which `docs/status.md` confirms - so no confirmatory result existed to see. Not a
registered-rules change, so no `Amends:` trailer, and this was checked rather than assumed:
`configs/registered_rules.json` holds twelve rules - `floor_rule`, `alpha_one_sided`, `tested_models`,
`robustness_models`, `held_out_fraction`, `bootstrap_unit`, `num_bootstrap`, `minimum_positives_to_score`,
`normalisation`, `validation_fold_rule`, `label_likelihood` and `membrane_potential_build` - and none carries a
free-fraction, Kp,uu or measurement-noise value, so no registered value is touched. The quotes, the routes, the
refusals and the licence of each source are in `docs/label_source_review.md` section 38.

Amendment, 23 November 2026, written before any lockbox run and before the held-out set has been drawn (decision 1.1
is open).

**37. The owner's rulings of 13 to 20 November 2026 on the open parts of decision 9.129, registered before they are
built, as fifteen sub-items** (the owner, 13 November 2026: "Let's rule on the rest of it first", and, on clearance,
18 November 2026: "just REGISTER it. i don't care how. no clearance, etc. is unacceptable for this project").
Decision 9.129 ruled on 12 November 2026 that item 37's draft be amended rather than registered as drafted, and left
four things owed: its three design questions, a second source for the carrier split, the carrier clause's figures,
"then registering item 37". The rulings that answer them are kept with the owner's words in
`docs/item37_rulings_draft_2026-11-13.md`, which is the authority for what this item registers; nothing of it is
built. Decision 9.132 holds, in one place, what this registration leaves owed.

**How to read the placeholders.** Much of item 37 is a rule whose number is not yet measured, and the registration
says which is which rather than leaving a reader to work it out. A value a rule still needs is written `[P n]`; the
owner's standing caveat covers these, item 37 being registered as ruled and not built (decision 9.129), so filling
one needs no further ruling, only the measurement, its second source where the rule asks for one, and the graph
version and date it was taken on (CLAUDE.md, Modelling). A rule still unsettled is written `[R n]`, and **only the
owner's ruling fills it**: no session, pass or build may. The numbers already in use elsewhere are kept: `[R 7]` and
`[R 8]` are the owner's own numbers of 20 November 2026, and `[P 13]` is the sourced headroom tables, which
`experiments/measure_saturation_counts.py` already names that way. The rest are numbered by this registration, which
is why the value placeholders do not run in sub-item order. The lettered codes the draft carries for the batches the
owner answered (P1 to P8, C1 to C21, I1 to I7, T1 to T4, M1 to M6, Q1 to Q5, S1 to S4, A1, L to P, and R1 to R4 of
the drug-target screen) are that draft's codes and are not these placeholders; where a sub-item names one it says so.

**37a. A reaction's classes are what its catalysts assemble, a pore is one population per co-assembly, and a pore is
added when it sits on any central cell class.** (i) The classes a reaction can contain are those whose defining
subunits can assemble from its catalysts, which replaces the choice by the first catalyst gene in sorted order that
`mechanistic_pathway_learning/graph/reactome_import.py` still makes. (ii) Where two classes can both assemble, the
reaction is split into one node per class, each taking the catalysts that assemble it. (iii) A pore that sits on no
central cell class is not added to the graph (the owner, 13 November 2026, on the muscle-type nicotinic receptor:
"accepted"), and **"central cell class", not "central neuron", is the test** (the owner, 18 November 2026: "yes,
that's the correct way: cell central class is the rule"), so glial classes count, and "ependymal choroid should be
included because it feeds the glymphatic system. same for vascular, but only for central vasculature". The
muscle-type receptor stays out and its subunits leave the neuronal entities; decisions 9.121 and 9.128 are unchanged
by it. (iv) One weight per pore population, with a curated, sourced table of which reactions are the same pore,
reaching the single-ion pores too, since overlapping catalysts are not proof of one pore (the owner: "D. yes", then
"D2. yes"); the three nicotinic reactions share one unit, the calcium-written reactions taking the fractional calcium
share and the sodium-written one the rest (the owner: "D1. fine. merge", and, asked which reading of "merge" they
meant, "i meant option 1", the shared weight). (v) The populations the rulings set apart: alpha-7 homomeric nicotinic
receptors are their own class and population, splitting `RCT_629595` (the owner: "A2. split"), with CHRNA7 restored
by a curated override naming both sources against GTEx's outlying 0.36 TPM (the owner: "use A1."); the non-selective
TRP reaction `RCT_3295579` is split into one node per co-assembled population (the owner: "that makes way more sense
for c. confirm c split."), with TRPC1/4 and TRPC1/5 two populations rather than one (the owner: "split TRPC1/4/5")
and TRPC4AP, a scaffold rather than a pore subunit, removed; the six Kir2, Kir4 and Kir5 genes that Reactome's GIRK
complex holds and that neither UniProt nor the Concise Guide supports leave that entity; K_ATP's three reactions are
two populations, Kir6.1 (KCNJ8) and Kir6.2 (KCNJ11), Kir6.1 kept as its own population weighted by class expression
with its reason corrected to mostly non-neuronal; `RCT_2684901` keeps ANO1, ANO2 and ANO6 as three populations and
loses ANO3, ANO4, ANO5, ANO7, ANO8, ANO9 and ANO10, those genes staying in the graph (the owner: "use corrected
8b"); SCN7A (Nax) is split out of `MAR_SODIUM_LEAK` as its own population, a different pore from NALCN, with its
conductance flagged; `MAR06534` is split into a pore node carrying chloride alone and a carrier node carrying the
1 Cl- : 2 HCO3- stoichiometry, SLC26A8 being kept as a carrier and excluded from the pore test (the owner: "SLC26A8
accepted."); and TRPA1 stays, on rodent functional evidence from three laboratories and human mRNA only (the owner:
"keep TRPA1 with the stated rodent-only plus human mRNA note"). TRPV5 and TRPV6 stay out until a pass shows one of
them on a central cell class, a pore with no such evidence not being added (the owner, 20 November 2026: "Yea").
(vi) **A pore catalyst is classed by what TCDB's entry text and UniProt say it does, not by its TC class number** (the
owner: "use functional description"), each disagreement between the two recorded beside its gene; the screen of the
267 catalyst genes of the 56 pore reactions found one reaction mixing a channel and a carrier, which is the second
source decision 9.129 (2) owed. (vii) **One counted unit per population is a stated interim and the reason is
coverage, not preference**: a resting conductance in central neurons is well sourced for 2 to 4 of 47 populations,
thin for 14 and absent for 29, and no conductance exists for either TRPC1 heteromer, so a scheme mixing sized and
counted populations is not coherent at `VM_c` (the owner: "keep 1/4 and 1/5 as nodes since the proportions for
splitting can't be sourced"). The same-pore table and the population list are `[P 1]`.

**37b. A gene is brain-expressed when it reaches the threshold in any brain region, the classes that rule needs are
added, and the expression values are attached after the last stage that adds gene nodes.** The owner, on genes whose
mRNA sits in small nuclei GTEx does not sample: "i think region-restricted genes is better fix, no?", and on the
rule: "that's fine but it needs to make sure to create those new cell types so their relative gene expression levels
can be unique." So a gene counts as brain-expressed when it reaches the threshold in any brain region of GTEx or of
HPA's regional bulk, which on the build of 12 November 2026 turns 1,420 genes brain-expressed, 15 of them drug
targets of 88 of the 260 drugs. The classes ruled with it, each a cluster of the Siletti et al. 2023 atlas:
serotonergic (397), Purkinje (314, on one source and kept because it matters for movement disorders), medial habenula
(334) and histaminergic (432) (the owner, 14 November 2026: "Yes to purkinje even with one source because it's
important for some movement disorders, habenula, histaminergic", and "Yes" for the serotonergic class); the forebrain
cholinergic class becomes three, striatal, NGFR-negative basal forebrain and NGFR-positive basal forebrain (the
owner: "accepted"); and the pituitary becomes six classes, one per HPA lineage (the owner, 19 November 2026: "use HPA
directly", and, asked whether each lineage is a class, "separate classes"). The orexin neurons are not a class at
cluster resolution, being about 9 per cent of one cluster, and the drugs that look like theirs act at HCRTR1 and
HCRTR2 on the neurons orexin projects to. **The annotation order is a code defect, and its repair is not a change of
what brain-expressed means** (the owner: "yes"): of 357 gene nodes whose brain expression is unknown on the
12 November build, 182 are nodes a later build stage adds after `annotate_brain_expression` has run and are in the
GTEx file by symbol, while every step that gates on `brain_expressed` reads unknown as not expressed. The values are
attached after the last stage that adds gene nodes, built together with the region rule in one rebuild, with a test
that fails while a gene node whose symbol is in the expression table carries no value. The before-and-after counts
come only from that build and the code is committable before them (the owner, 20 November 2026: "oh. then i don't
need the counts before it's committed for 8c"); they are `[P 2]`.

**37c. A non-selective pore's calcium share is its own fractional calcium current, derived where none is measured by
the raw constant-field solution with no calibration factor.** The owner, on the four-part reading of their "use
option 3 with the individual potency factors": "yes and yes". (a) A non-selective pore class's calcium share is its
own measured Pf, from two sources where possible, with any gap stated. (b) Its weight into `VM_c` stays on the
registered monovalent law, the calcium share counted in full as inward current. (c) Its edge into the cytosolic
calcium pool is Pf times the current its `VM_c` edge is built from, and a calcium-selective pore has Pf = 1.
(d) Every input to that pool, pumps, exchangers and stores included, takes the same current unit. **The form of the
derivation** (the owner, 16 November 2026: "for decision 3a, scuggestions accepted"): activities rather than
concentrations, one convention in derivation and in prediction, each P_Ca/P_Na derived as the exact zero of the same
current equation at the paper's own absolute reversal potential with no shortcut formula, each row read with its own
solutions and temperature, no surface-charge term, and no model beyond the constant-field equations, none having
usable per-channel parameters. **The measurement a population takes**, ranked (the owner, 16 November 2026: "yes,
that captures it"): re-derivable under that form; subunit composition matching the population; a sodium-containing
mixed solution with P_K = P_Na assumed where unmeasured, a sodium-free biionic recording being a flagged fallback
(the owner, 16 November 2026: "yes"; the criterion keeps the wording ruled that day, its TRPV1 rationale withdrawn on
17 November 2026 and the TRPC6 evidence standing - the owner: "for criterion 3: sure, keep it as previously ruled on
16 Nov since TRPC6 still shows evidence"); native neurons, then mammalian cell lines; human; temperature nearest
37 degrees C. Native measurements are preferred to recombinant, and a range is kept only where two measurements tie
on every criterion and still disagree (the owner: "native over recombinant otherwise range accepted", and "but only
use the range if we can't find a way to reduce it to a single scalar or a smaller range"). **A derived value uses the
raw solution**: the owner, 17 November 2026, "1. raw GHK per previous decision that the model-based needed to beat
it", the earlier ruling being that a model-based correction is used only where it beats the raw form, which the
leave-one-out error does not, so the constant odds factor is dropped, the gap is recorded rather than fitted, and
each derived value is flagged as an order-of-magnitude value and not a measurement. **NALCN takes Pf = 0** (the
owner: "NALCN Pf = 0 for Ca accepted"), the complex a neuron carries passing no detectable calcium, with the
disagreeing value from a preparation found non-functional recorded beside it; extracellular calcium's block of
NALCN's sodium current is decision 9.114's and not this item's. **Where a channel's own activation states disagree,
the value is the geometric mean of the Pf derived at each end, the ends kept as its interval, with a sensitivity run
at both ends** (the owner, 16 November 2026: "a plus b for TRPV3 instead of d because the physiological state changes
over time in a way that matters for Pf, geo mean will give middle of all measured states, and it would also mean
carrying that expensive sourcing decision into other similar cases that might come up in the future"), and the same
for any later case of the kind. Each population's Pf is `[P 3]`; the P_Ca/P_Na values and the re-derivation of the
calibration rows under the form above are `[P 4]`.

**37d. The potential and the pools: the pool edges in a conductance edge's unit, an ion-matched carrier test, two
corrected permeability ratios, and the magnesium block modelled in full.** The two parts decision 9.129 ruled on
12 November 2026 are registered here: each cytosolic pool edge carries a conductance edge's unit rather than a share
of one, and a single-ion conductance edge is given only where a catalyst of the reaction carries the channel-activity
term of the ion that reaction moves, descendants included. Both are coded in the `pores_and_clamped_pools` build
alone, so no committed graph carries them and the registered build's weights are unchanged (decision 9.129). Two of
the build's permeability ratios are corrected on the owner's rulings of 17 November 2026: the neuronal nicotinic
P_K/P_Na is the native-neuron 1.23 rather than the oocyte 1.2 (the owner: "yes. native 1.23 instead of oocytes"), and
NALCN's is 0.92 rather than a review's rounded 1.0 (the owner: "yes to 0.92"); each moves a weight by under 2 per
cent. **The calcium pool keeps the per-open-channel basis, and that is a sourcing limit and not a numerical choice**:
a pass of 17 November 2026 found no resting flux through any route measured in a central neuron, no measured pump or
exchanger density, and clearance shares differing by cell type more than one reference set could carry (the owner:
"sounds like there's no way around the per-open-channel version"), so the population basis is recorded as not
sourceable on that date. **The NMDA receptor's magnesium block is modelled rather than left as the sign of a voltage
gate** (the owner, told that nothing in the drug set perturbs magnesium: "it's worth it regardless of whether
something perturbs Mg because it sets the base fraction blocked for NMDA"): extracellular magnesium is ionised
0.8 mM with the range 0.66 to 1.15 mM, the ionised share of total recorded as open and total CSF magnesium of 1.13 to
1.19 mmol/l recorded beside it as a separate quantity, with the sleep-wake swing of 0.11 to 0.13 mM (the owner, told
that the 0.70 mM alternative is mouse cortical interstitium: "k accepted"); an `inhibits` edge runs from the
extracellular magnesium node to the receptor; the voltage edge carries the slope of the block equation at rest; the
block's constants take a second source; and the resting unblocked fraction enters the receptor's headroom and, once
counted units give way to conductances, its resting conductance. **The block is carried per GluN2 class** (the owner:
"m. one per GluN2 class unless you disagree"), so `RCT_432164` is split by the mechanism 37a (ii) already gives, each
class node carrying its own agonist affinity as well as its own block, and each class's Pf and P_Ca/P_Na stated per
class or stated as shared; recorded with it as a simplification, triheteromers are intermediate, so a two-class split
puts them in one class or the other, and three classes would follow the sources more closely and are not registered
here. The ionised share and the quantities recorded beside it are `[P 5]`; the per-class block constants, their
second source and each class's permeability values are `[P 6]`.

**37e. Headroom is (maximum - rest)/rest, read at one resting potential, with the ceiling cut to the share that can
reach it and rest counting the openings that need no agonist; and one method per quantity across the populations it
is compared over.** Each source's gating curve is evaluated at the registered -72.6 mV, the source's own resting
potential recorded beside the row (the owner: "i accept the single registered -72.6mV. run the resting potentials
fable pass to get the new column values please"). A ligand-gated population's Hill coefficient is sourced and not
assumed to be 1 (the owner: "c. source them"), and a population whose coefficient cannot be sourced keeps 1 with that
stated in its row. A ceiling is multiplied by the share of the population that can open without first
hyperpolarising (the owner: "g. multiply by the share of the population that cannot open without first
hyperpolarizing"), which is the physiological reading of a ceiling rather than "all channels open"; a population
whose inactivated share is not sourced keeps the full ceiling with that stated. Rest is spontaneous plus
agonist-driven openings for every population with measurable agonist-independent activity and not for the
extrasynaptic GABA-A receptors alone (the owner: "yes to both d and l"), a denominator of agonist occupancy alone
making the headroom too large. **Headroom stays one value per node and not one per region** (the owner: "i think
i'll keep it this way for now", then correcting their own first reason: "actually, adding the true region structure
mostly adds more gates than more params"), so the reason of record is compute and sourcing and not parameter count: a
region group is a fixed expression gate on the shared adjacency, so run time grows with the group count, while most
regional ambient and headroom values are unsourced. Each sourced headroom records the region it was measured in and
why that region was taken. **The uniform-method rule** (the owner: "yes to both d and l"): where a quantity enters a
comparison between populations the method is uniform across them, or the difference is recorded as method-dependent
and not read as physiology; where a better-sourced value exists for only a few populations, both are recorded and the
uniform one is used. Its cost is stated because the physiological version is otherwise the default: the uniform
choice is sometimes the less physiological one, and the justification is that mixed methods put a false difference
between two nodes, which is itself a physiological error and not a numerical convenience. **Amended the same day for
a bias that is not a common monotone transform** (the owner, who raised it - "i was worried about nonlinearity for
the uniform method rule" - and then: "accepted uniformity amendment"): the rule applies where the method's bias is
plausibly a common monotone transform across the populations compared, which holds for temperature and for the
liquid-junction potential and fails for quantitative microdialysis across transmitters, whose bias depends on each
transmitter's uptake kinetics; where it is not, each population takes its best evidence, the method is recorded on
its row, and cross-method comparisons are marked method-dependent. Applied to the preparation, a Hill coefficient or
an EC50 comes from HEK cells rather than oocytes where the preparations differ (the owner: "6. use HEK over
oocytes"), the oocyte values staying recorded beside the rows. The Hill coefficients are `[P 7]`, the
non-inactivated and agonist-independent shares `[P 8]`, and the headroom of each node `[P 13]`. **`[R 1]`: whether
the uniform-method rule is also recorded as a decision row of its own and a line in `CLAUDE.md`**, being general
rather than particular to item 37; this registration does not assume it.

**37f. Saturation goes inside the fixed point, the gain clamp goes, and the damped iteration gives way to a
root-finder beside an unclamped iteration.** The owner, 21 October 2026 and again while the conductance edges were
being sized: "saturation has to exist within the fixed point to properly represent physiology, right?", then
"honestly, i think i'd rather just move towards the version with the stabilizing nonlinearities inside the fixed point
loop and remove the damping", and, told that the damping sets the transient only, "the .9 gain clamp is what i meant
by removing the damping"; on the three parts put to them, "yes to all three, root-finder and learned fallback". So,
as the direction registered and not built (decision 9.81, which already records that changing the tested model goes
through an amendment: "it's fine as an amendment"): (1) saturation inside the fixed-point loop, soft
(Michaelis-Menten or Hill), so that a chain of saturated steps keeps a nonzero gradient; (2) a floor at -1 for every
node, activity not being able to fall below zero; (3) a sourced upward headroom per node wherever one can be sourced,
by 37e, which is `[P 13]`; (4) a learned headroom per relation type as the fallback where no value is sourced, and
none where no ceiling exists (the owner, correcting the session's reading of their question: "sorry. i meant
per-relation-type. and only for the unsourced values is good for that per-relation learned fallback"), so the nine
populations sourced as unbounded get no ceiling, which is what their measurements say and what spends fewest
parameters; (5) the 0.9 gain clamp removed; (6) the bottleneck and the pH ceiling inside the loop (the owner:
"17. inside"); (7) the damped iteration replaced by a root-finder with implicit differentiation, started from rest,
beside an unclamped iteration with saturation inside it for readings at each propagation round, both without the gain
clamp, the root-finder searching for several steady states rather than only the one reached from rest (the owner:
"i was thinking option a except that: instead of clamped gains for the root-finder, it will still allow unclamped
gains and finding of multiple steady states"). **Only stable roots enter a prediction, and several stable states
combine by noisy-OR** (the owner: "definitely option a", and "keep only stable roots"), the head's own combination
rule, so a symptom is predicted if any stable state produces it, because "it could be the case that the symptoms show
up for both steady states in the bistable switch"; a state the search misses takes its symptoms with it, so the
search's incompleteness bears on the prediction and is stated, and the search is to be generous with its starting
points. **What this leaves owed.** The method for finding several steady states is deferred to decision 9.138,
outside item 37, "with item 37 written under the understanding that something will eventually be added to address it"
(the owner, 19 November 2026); a round is not physical time while the relations carry no timescale; and the two-sided
bound on `VM_c` in state units is computed from the built edges once item 37 is built (the owner: "13. sure. once
item 37 is done being built"), the generic floor at -1 lying below E_K on every reading. Decision 9.81's four counts,
a count of positive-feedback cycles and the scoping of which node kinds can take a sourced headroom come before the
build. **`[R 7]` is withdrawn.** It asked whether the registered `normalisation` rule is kept; the owner withdrew the
rule itself on 20 November 2026 ("R7 I'm just saying it's no longer needed so unregister it"), having kept it on
16 November ("keep forward cone norm"). It is **not** unregistered by this amendment: the damped iteration in use
needs the divisor to converge, so the rule and its test leave `configs/registered_rules.json` in the commit that
builds the root-finder, under that commit's own `Amends:` trailer, and item 34a stands until then. **`[R 5]`: whether
the per-round readings of the unclamped iteration enter a registered prediction, or stay a reading reported beside
the tested model.** The owner ruled that both readouts exist; which one the confirmatory prediction uses is the
noisy-OR across stable steady states above, and the place of the per-round readings is not ruled.

**37g. A learned parameter is clamped to whatever bound its own evidence supplies, and one with no bound of any kind
stays fixed.** The owner, 18 November 2026: "1a and 2a being the only depletion nulls for clamping is fine. it should
probably apply to other param types too though for the clamped learning", and, on the two points left open with it:
"i would say a param with no bound should stay fixed only because there's no data on its bounds and leaving it
unbounded leaves the amount of error it absorbs unbounded. i think the bounded transform is better for training
dynamics reasons (i.e. vanishing better than dead gradients)." So the bound is the published range where only a range
exists, a depletion null where one exists, and a measured occupancy where one exists; a parameter with no bound of
any kind stays fixed, with the owner's reason recorded as the justification the modelling rule asks for; and a clamp
is enforced by a bounded transform rather than by projection after each step, on the ground that a saturating
transform gives vanishing gradients at the bound while projection gives dead ones. **A bound read off a depletion
experiment is hard only where the experiment is human in vivo and the depletion is complete** (the owner,
18 November 2026: "i guess the nulls should hard bound only for human invivo complete depletion. where there are
cases that don't have both together, it's a soft bound where the softness of the bound is scaled by the reliability
of the evidence prior determined by the same method as the rest of the evidence prior reliability estimation", and
"remember the other half of that depletion null that i ruled earlier too: it has to be human AND fully depleted to be
a hard bound"); a bound resting on an incomplete depletion, on one whose completeness is unestablished, or on an
animal experiment however complete its depletion, enters as a soft bound scaled by the evidence prior's reliability,
which today is decision 9.59's calibrated regression
(`mechanistic_pathway_learning/evidence/calibrated_reliability.py`). **The consequence is recorded rather than left
to the build**: the one receptor the bound bites on, HTR1A, takes a soft bound and not a hard one, because the human
depletions are partial and the near-complete ones are rodent, so the hard branch may have no members today. **The
affinities are learned from the first build, inside their clamps, and no two-build screen is run** (the owner,
18 November 2026: "i thought i ruled against doing the two-build screen version and sticking to learned params
inside the soft/hard clamped bounds based on evidence prior since the 5-ht1a disbelief comment", with the ambiguity
resolved in their next message: "i mean i ruled FOR sticking to learned params"), each initialised at the midpoint of
its range, which makes the midpoint a starting point and not a claim. Where a published range lies wholly inside the
region a depletion null contradicts, the clamp interval is widened to span the dispute rather than confining the
learned value to the contradicted region (the owner: "so widen it"), so HTR1A's clamp runs from 0.2 nM to the null
bound's 9 nM; elsewhere a learned affinity is clamped to its own published range. The owner's reason is recorded
because it is the ground of the ruling: "i have a hard time believing that a 22x change of 5-HT1A will not move
predictions". **D2 is learned inside its measured occupancy range the same way** (the owner: "For d2, do the same
hard learning constraints"), a headroom of 8.1 with bounds 3.8 and 11.5 from the pooled human depletion studies, the
lower bound soft because the depletion behind it was incomplete (the owner: "make the D2 bound soft since it's
depletion was incomplete. that rule can extend to any other cases too") and the upper bound unchanged, since
incomplete depletion biases a measured occupancy downwards and so weakens the floor it implies and not the ceiling.
Recorded with it: the measurement is striatal and may not hold for D2 elsewhere, benzamide tracers see only the
receptors they reach, and reading a headroom off an occupancy assumes a response proportional to occupancy, which a
receptor reserve would break. Every clamp bound and seed this sub-item reaches is `[P 9]`.

**37h. The occupancy split: four quantity types are admitted after sourcing is attempted, and what no source covers
takes a learned fallback whose class is the protein's family crossed with the pair's mode of action.** The owner,
18 November 2026: "i say that IC50 should be included just make sure to attempt sourcing values first", and "i don't
see why EC50 would be treated any differently than IC50 in terms of inclusion for occupancy". So Ki, Kd, IC50 and
EC50 enter, a positive modulator's potentiation EC50 among them with the receptor assembly it was measured on
recorded beside it; no Cheng-Prusoff conversion is made, the conversion being conditionally defensible for part of
the IC50 rows and not for the channel, transporter and allosteric ones; the quantity type stays on each row, and a
drug whose shares mix types is marked method-dependent under 37e's rule. **The session's own "not-IC50 rule" is
withdrawn**: the owner never gave one ("i never said gave a 'not-IC50 rule'") and a pass traced the phrase to a
session's planning note. **There is no uniform fallback** (the owner: "no uniform fallback. it's too
non-physiological"). Its replacement, whose shape the owner accepted and whose class definition they sent to a pass
("yes but \"by class\" is doing a lot of work here and needs a strict definition that should be addressed by a fable
pass") and then ruled ("1-4. go with recommendations"): a pair with no sourced value starts at the median of the
sourced pairs of its class in log space, with a per-pair offset shrunk toward the class value and a soft clamp to the
class's sourced range whose strength is set by the evidence prior. **Class** is the GtoPdb family of the protein,
pinned release, crossed with the pair's mode of action, mode being the eight-value rule over the ChEMBL action type
and protein class rather than the raw action type; below k = 3 sourced measurements the back-off is GtoPdb type by
mode, then mode alone, and **never below mode**, so no global median is used, and a pair with no level holding at
least k measurements is listed for sourcing. A class statistic is taken over sourced measurements of the class's
expected quantity family where at least k exist and otherwise pooled with the mix recorded on the row (the owner:
"go with b"), the fixed-factor alternative not being used. **The fallback is not used for receptor ligands at all**
(the owner: "then don't use it for the receptor ligands", and "no value for receptor ligands: send to sourcing").
**The ionotropic glutamate receptors split by ChEMBL protein class level 4 into AMPA, kainate and NMDA** (the owner:
"they definitely need split", "yes, level 4", then "then ionotropic glutamate receptors only"), a split sourced twice
by HGNC's gene groups and deliberately not generalised, since as a general depth level 4 would merge the five
aminergic families and destroy the muscarinic result below. **The sibling-subtype centre is adopted for the
muscarinic receptors only**, where the margin survives the within-paper inflation the ChEMBL harvest exposed; every
other family keeps the class centre, the harvest having found 98.5 per cent of sibling pairs inside one paper and the
across-paper sibling error about 0.25 log worse. Genes with no single-protein ChEMBL target stay out of any ChEMBL
check and their pairs go to sourcing (the owner: "Yes"), a complex target not being able to give a subunit-specific
value, and SCN7A stays in a family of its own pending its own check (the owner: "ok"). **Everything sourceable is
sourced, and the fallback is what remains after sourcing rather than an alternative to it** (the owner,
20 November 2026: "Not just topiramate. Everything sourcable should be sourced"), batched by family and placed in the
queue before the damping measurements (the owner: "Batching by family makes sense but don't start yet. Just add it to
the todo before the damping measurements"), and every sample drawn for that sourcing follows decision 9.134. **A pair
whose ChEMBL action types conflict is withheld and flagged for curation rather than settled by the last row read**
(the owner: "yes, always flag for curation instead"), the resolutions living in
`configs/chembl_action_conflict_resolutions.csv`; varenicline's two pairs are resolved as partial agonist on both
CHRNA4 and CHRNB2 (the owner: "accept"), with GtoPdb's "Agonist" coding recorded as a disagreement. Amisulpride's
eleven serotonin pairs are curated before any fallback is applied, and acamprosate's thirteen GABA-A edges are
removed, the sourced negative they carried recorded in the curation file rather than in the graph (the owner: "remove
acamprosate edges"). The affinities and the pairs that have none are `[P 10]`; the class statistics the fallback
needs are `[P 11]`.

**37i. A mechanism row on a protein-family target becomes one class-level annotation at reduced weight, and for a
drug whose mechanism is known only at family level that annotation is carried by one binary gate per drug, shared
over the adult central sodium-channel isoforms.** The family-target artefact is the same in three places. SCN7A's
edges are removed for all 26 drugs that carry them and not only the four examined: the ChEMBL family target lists
SCN7A as a group member, Nax has its own single-protein target with none of these mechanisms on it, and no source
shows any of them acting on Nax, while PROTEIN:SCN7A catalyses `MAR_SODIUM_LEAK`, so these edges were acting on the
sodium leak. Primidone's ten sodium-channel edges are replaced by one class-level annotation at reduced weight,
flagged as a class or batrachotoxin-site effect, with phenobarbital and PEMA getting none (the owner, after pushing
back - "I thought primidone worked on sodium channels..." - "P5 accepted", the draft's ruling P5; the textbook claim
behind primidone's mechanism row is not disputed, and what no source supports is a specific subtype). And cocaine's
ten are replaced the same way, where the class-level action is the drug's own labelled mechanism, so it is well
supported and only its resolution is at fault. **The gate, in full.** The owner, 20 November 2026: "Actually, maybe
we make it a categorical edge", "I mean force it to choose one like the categorical gates", then, on a drug acting at
several subtypes at once, "Actually it might hit more than one toe so need one binary gate per type" ("toe" read as
"type"), and "Make them part of the registered model"; then, having given two claims and five sources of their own -
that the classic anticonvulsants bind "a conserved local-anesthetic-like site in the pore-forming alpha-subunit",
"giving them broad, state-dependent activity rather than isoform selectivity", and that the dominant neuronal sodium
channels in the brain are Nav1.1, Nav1.2 and Nav1.6, "along with Nav1.3 during development" - and asked whether one
gate per drug shared across the central isoforms should replace the per-isoform gates: "Yes", and again "1 yes".
**So the registered form is one binary gate per drug**, a hard yes-or-no gate of the kind decisions 9.57 and 9.62 (e)
build, shared over the adult central isoforms Nav1.1 (SCN1A), Nav1.2 (SCN2A) and Nav1.6 (SCN8A), each edge weighted
by that isoform's expression on the central cell class, with Nav1.3 (SCN3A) dropped as developmental and the muscle,
cardiac and peripheral isoforms dropped. **The gate starts at a weak prior**: it rests on class inference, no source
showing primidone itself on a sodium current, and the priors the per-isoform form would have carried were equal and
at the reduced weight a family-level annotation gets (the owner: "2 yes"). The gates enter the registered model with
the gates of decision 9.122 and stay subject to its identifiability screen after the held-out draw; a gate that fails
that screen keeps the class-level annotation at reduced weight in its place. The same form applies to similar cases
only (the owner: "only similar cases"), read as a drug whose mechanism is known for a whole protein family with no
source naming a member. The state dependence of the binding is a stated limit of a steady-state response.
**The screen's other three rulings**, the draft's R2 to R4, all accepted on 20 November 2026: the affinity line is
relative to each drug's own tightest carried target with a floor, no single absolute line serving both cocaine's
transporters and the antipsychotics; a target that is real binding at a reachable concentration is carried, weighted
by occupancy; and a mechanism row on a family target becomes one class-level annotation at reduced weight, which
reaches 130 of the 260 drugs, 105 of them with every row of that kind. Of the 570 missing targets at the affinity
line, 356 rest on one document and 262 on one record, so each takes a second source before it is curated onto a node
(the owner: "Flag the thin tail for follow up"). **Two curations registered with it**: cocaine's drug node takes the
dopamine, serotonin and noradrenaline transporters, all inhibition, on two independent sources each, with the label
recorded as an omission rather than a contradiction, since it gives the sodium-channel action alone; and
methamphetamine's transporter signs are inverted from a family-target inhibition to the releasing direction at SLC6A3
and SLC6A2 with a weak one at SLC6A4, with VMAT2 reversal added (the owner: "please add VMAT2 reversal to
methamphetamine"), which needs a new curated efflux reaction of the form the three plasma-membrane effluxes already
take and either two mechanism edges or the learned per-relation gains, since one sign on the protein node would drive
loading and reversal together, and whose sign is set against the five existing rows at that protein rather than in
isolation. The reduced weight itself comes from a sourced within-family affinity spread, a sourcing effort the owner
asked to start no earlier than 21 November 2026; it is `[P 12]`. **`[R 6]`: whether every drug whose mechanism is
known only at family level takes a gate of this form, or only the cases already curated until each of the others is
sourced.** The owner ruled the form, and "only similar cases"; which of the 130 are similar cases is not ruled.

**37j. Plasma binding: a sequestration edge weighs the bound fraction times the carrier's share, and the share's
class is the drug's ion state at the compartment's sourced in vivo pH.** The owner: "use option a for the per-carrier
weighting with your suggested fallback order". So the weight is (1 - fu) times the carrier's share of the binding,
with fu an attribute of the drug node, and a drug with no measured human fu takes the ranked fallbacks a pass of
18 November 2026 set out (`sequesters_fu_2026-11-18.md`, that session's scratchpad). A share inside a named carrier
set takes, in order, a published split, a conversion of isolated-protein percents, the acid/base class rule, protein
concentrations with an affinity ratio, and a regression of fu on each protein; **the equal split that stood last is
replaced by the occupancy split's learned fallback** (the owner: "this is fine but use the same replacement for the
uniform fallback as the occupancy"), so an unsourced share is learned from the class median in log space with a
per-drug offset and a soft clamp, as 37h has it, and carries the same guard against circular reasoning. **The class
is ion state, and ion state is taken at the compartment's sourced in vivo pH and not at a fixed 7.4** (the owner:
"the ion state should depend on a sourced invivo pH for the compartment"), plasma carriers at arterial pH 7.40 (the
owner: "Arterial makes more sense"). **Membership is soft**: each drug carries its charged fractions by
Henderson-Hasselbalch rather than a class label (the owner: "Yes to carrying the fraction"), and a sourced member
counts toward every class in proportion to those fractions (the owner, on soft membership: "a"), so a class median is
a weighted median, a clamp range a pair of weighted quantiles, and a fallback drug starts at the fraction-weighted
mix of the class medians with nothing fitted; the regression on the fraction is not used. A fraction is computed from
a constant corrected to body temperature, a direct 37 degrees C measurement first and the group median shift
otherwise, at plasma ionic strength, the within-group range riding with the fraction; the justification under the
modelling rule is that leaving a 25 degrees C constant as printed biases every base one way, toward more charge than
it carries at body temperature, and the group median stands in because no 37 degrees C measurement was found for most
drugs. Where a drug's sourced constants disagree the spread becomes bounds on a learned charged fraction or is
propagated through the calculation (the owner: "The range shouldn't JUST be recorded. It needs to be included as
either bounds on a learned param or propagated through a calculation"); where they merely differ, the median of the
measured aqueous values is taken. A drug is classed by charged group and not by net charge, so an ampholyte is
zwitterionic rather than neutral, a net-charge label hiding the ammonium. **A zwitterion or ampholyte stays one drug
node, its carrier influence split across its microspecies by linkage** (the owner: "That might be solvable by keeping
a single node and splitting its influence since drugs don't currently have node descriptors. Oh. That's what you
suggest. Do that"), each microspecies entering by its measured fraction times its own affinity for the carrier, the
equilibrium between forms shifting as one is bound, rather than at 1/n or at its resting fraction alone; the class
statistic over forms replaces the four-way class, and at most three shared parameters carry how albumin's affinity
differs between forms, started at zero and bounded at plus or minus one log unit on measured shifts. **Non-plasma
carriers get sequestration edges confined to the compartments they occupy** (the owner: "they should get edges but
make sure they are confined to compartments in which they appear"). **The reference concentrations** (the owner,
20 November 2026): alpha-1-acid glycoprotein 0.75 g/L with the range 0.4 to 1.2 g/L (the owner: "use .75 with range
.4-1.2"), stated in g/L because most binding experiments make the protein up by weight, so the assumed molecular mass
cancels, with 37 kDa where a molar value is shown (the owner: "accept") and the smaller laboratory series recorded
and not settled; albumin 42.5 g/L with the range 42 to 47 g/L and the starting point kept at 42.5 (the owner: "yes
but extend range to 42-47", and "keep the starting point at 42.5 w/ extended range"); a healthy-adult reference with
the disease multipliers recorded beside it (the owner: "yes, healthy reference"); ORM1 against ORM2 weighted by
plasma abundance, about 2 to 3 against 1, and not equally; and where a paper reports both, the share is taken on
albumin with fatty acids rather than on defatted albumin, as the form nearer plasma. A member resting on one source
is accepted, flagged as single source, with the second sources tried listed beside the row; a value calculated from
binding to isolated proteins counts as sourced at a lower evidence weight than a whole-plasma split (the owner:
"count Table 3 with the lower weight"), marked as such; and a class with no sourced member gets no value, so its
drugs are listed for sourcing. Every carrier identity, share, free fraction and acid dissociation constant still to
be sourced is `[P 14]`. **`[R 2]`: whether either size of the temazepam free-fraction difference, the 44 per cent
between arms or the 27 per cent within one arm, may be relied on.** The full text, read on 23 November 2026, leaves
the heparin caveat standing, narrowed to addressed by the authors by citation and not excluded by their methods, and
the reading reported is that the paper supports the direction and not a size free of that question. **`[R 3]`: the
correction for a fraction-unbound measurement taken away from 37 degrees C**, to be ruled once the sourced values and
binding enthalpies are in (the owner, 20 November 2026, "yes" to sourcing them). **`[R 4]`: whether a free fraction
becomes a modulated quantity** rather than a constant, which is what temazepam's fatty-acid dependence argues for and
which would reach every drug bound at the same albumin site; it is parked in `docs/exploration_queue.md` and is not
registered here.

**37k. Clearance is registered in the confirmatory model, on the dispersion model of hepatic clearance, through one
universal clearance node.** The owner, 18 November 2026: "just REGISTER it. i don't care how. no clearance, etc. is
unacceptable for this project", and "there will have to be a universal clearance node with a separate edge from
clearing enzyme to the clearance node for each substrate that the enzyme clears". **The model is the dispersion
form** (the owner, 22 November 2026: "3 clearance: dispersion form"), and the narrowed framing put to them on
21 November 2026 is accepted ("5 ok"). Under CLAUDE.md's rule that the version closest to physiology is used the
dispersion form needs no justification and the well-stirred form would have needed one, the group that set out the
comparison calling the well-stirred form unphysiologic. The docstring of `experiments/tabulate_drug_routes.py`, which
opened its reason with the well-stirred model, names the dispersion model from the commit that registers this item,
keeping its citation and its three-row conclusion; **whether that narrowing's conclusions survive the dispersion form
is research owed a pass, and no new reasoning about it is registered here or written into the code.** The seed split
is the occupancy split of 37h with its learned class fallback (the owner, 20 November 2026, confirming that reading:
"Yes"), the sourced-ratio version renormalised to 1 per drug; the uniform fallback it first carried is withdrawn
("no uniform fallback. it's too non-physiological"). Dose enters through concentration rather than a
therapeutic-index scale, labels not being dose-resolved, and a concentration sweep gives the multiple readouts.
`configs/drug_clearing_enzymes.csv`, the 44 FDA pharmacogenetic rows, is applied in the next build, carrying out a
ruling of 11 October 2026 that was never built: the build holds no `clears` edge, no drug-to-enzyme edge and no
drug-to-metabolite edge, so no drug's metabolism is represented today, which is what the owner suspected when they
asked for it to be checked. The quantities the split needs beyond those two are sourced first (the owner:
"accepted. please start the sourcing pass") and are `[P 15]`. Decision 9.133 records the ruling and is closed with
its build owed.

**37l. The expression scales are reconciled by converting bulk TPM onto the nuclei nCPM scale with a measured
per-gene term.** The owner, 18 November 2026: "for the TPM confounds, go with option D. record the numerical
reasoning that it confines the confounds in that the measured values and makes more of the values accurate to within
2x". So log2(nCPM / TPM) is the log of the collapsed-model transcript length plus the published per-gene
nuclei-to-bulk log ratio plus a constant. **The justification under the modelling rule**: the per-gene term is a
measured value, so the confounds it corrects are held in a published measurement rather than in a slope fitted on
this project's data, and it brings the most genes within two-fold, 66 to 82 per cent against 30 to 35 for the single
factor the build used; the per-class pre-mRNA version, which is the physiological one, is not used because it cannot
be obtained, the authors' matrices answering 404. The conversion runs from TPM to nCPM and not the other way (the
owner: "I thought that was the only direction that was viable"), because the reference scale and most columns are
nCPM and converting those instead would move every threshold registered on that scale. **A gene the published table
does not cover takes transcript length alone** (the owner, 19 November 2026: "go with transcript length alone for the
fallback since it's at least mechanistic correction"), the fitted annotation fallback having shown no consistent gain
on the genes outside that table, so nothing anywhere in the conversion is fitted on this project's data. **A gene
whose canonical transcript lies at least half inside another annotation record, or which is pseudoautosomal, is
treated as outside the table**, 292 genes, which is an annotation rule in place of the bound first proposed: the
cause of the table's wrong upper tail is established as a read-through annotation artefact on the bulk side of the
paper's own comparison, and a bound would cut long genes that are right and keep wrong genes beneath it. The
threshold is a choice, justified by the measured dose-response of the overlap and by the cause being established, and
the same rule applies in brain, the defect being in the table and not in the tissue. **The peripheral columns**: the
pituitary is read from HPA's single-cell-type table and converts not at all; the pineal column is a full-length read
CPM, which already carries transcript length, so its conversion drops the length term (the owner: "yes"); thyroid and
the other bulk-converted classes take the per-gene term at slope 1 (the owner: "suggestions accepted") with the
accuracy measured in eight non-brain tissues recorded as a limit, unmeasured in thyroid, and the over-correction
outside brain recorded with it; and the islet class stays converted bulk rather than moving onto the nuclei it is
calibrated against, those being three cultured, stress-marked, beta-rich donors of unverified licence. **Mitochondrial
genes stay out of the normalisation that sets each tissue's constant, and each tissue's constant is set robustly
against that tissue's own dominant genes where nuclei data exist**, rather than by dropping genes above a share of a
bulk column, which would be a threshold needing its own justification; the earlier reasoning that treated
mitochondrial genes as the special case was wrong, the real problem being any small set of genes that dominates a
bulk column and that nuclei do not hold in proportion. **The islet hormone genes** take the islet's own measured
nuclei-to-bulk ratio, a measured per-gene value in the right tissue, so it carries the same reason as the per-gene
term: four are used as measured, a reconstructed floor stands and is recorded as "at least" (the owner: "L
accepted"), insulin is recorded as a limit and not a value, no donor meeting the retention criterion, the donor whose
sex contradicts the paper is recorded as an unsettled disagreement on which no ratio depends, and the raw reads are
postponed rather than abandoned (the owner: "N-P accepted", and "M just postpone the read though until disk frees or
a new session"). **An unpublished release is not evidence for any conversion** (the owner, 19 November 2026:
"unpublished releases don't count"), and cancer-adjacent nuclei are out as too confounded ("cancer-adjacent nuclei
are out: too much confound"). **The limits registered with the conversion**: the per-gene table is one study of ten
donors in one cortical area and covers 9,894 of the 12,660 mapped gene nodes; the fit is worse in putamen; nothing is
tested per cell class or in the endocrine tissues where the conversions are actually made; and the pre-mRNA share per
class, ambient RNA and the composition of the bulk reference stay uncorrected. The per-gene terms, the per-tissue
constants and the flagged-gene list are `[P 16]`.

**37m. Drugs, prodrugs and metabolites as nodes: a drug the body makes seeds on the compound it already is, a
metabolite with a profile of its own becomes a node weighted by its relative occupancy, and the module-growing phase
excludes entry nodes.** The owner, 19 November 2026: "All endogenous drug perturbations should work that way",
generalising melatonin's merge ("Yes but give the melatonin node the drug class type too so that it can be known in
the module growing phase for the seed to sink requirement"). So an endogenous drug perturbation, one whose molecule
the body makes and the graph already carries as a compound, seeds on that compound's own metabolite nodes, the merged
node keeping the drug class type; the mechanism is in
`mechanistic_pathway_learning/graph/drug_entry_nodes.py` and fires only where every seed is already a metabolite node
of a compound listed in `configs/drugs_acting_as_graph_compounds.csv`, which holds one row and must be curated.
**The set is three drugs and not the dozen the session guessed**: melatonin, whose compound-node receptor edges take
the agonist sign inside the merge step, so that one code path handles every endogenous drug and a merge does not
convert an agonist into a directionless interaction (the owner: "P1.1 a,b accepted"); and brexanolone and sodium
oxybate, which merge only once their compound nodes carry their receptor edges, sourced, since merging now would lose
the mechanism outright, as the prodrug pass warned and the session twice denied. Levodopa is a fourth case already
ruled, seeded on the L-dopa compound node with its dopamine-receptor edge dropped, since the physiological route is
built on the compound side and merely unreachable. Acetaminophen does not merge until its brain metabolite is a node
of its own, formed from the parent and carrying the two edges that describe the metabolite and not the parent, with
the hydrolase's sign corrected, that enzyme making the active species rather than being inhibited by the parent. A
prodrug whose converting step has no natural graph node keeps the active species' targets on the parent, with the
reason recorded: conversion is near-complete before the drug reaches the brain. **An active metabolite with a
receptor profile of its own becomes a node formed from the parent by the enzyme that makes it, where both its brain
exposure and its potency are sourced, and otherwise is not modelled; there is no threshold, and its edges are
weighted by its relative occupancy instead** (the owner: "A1. No cut. Weight edges"), which is how every other
fraction in item 37 is carried. **No flag marking a node as a drug is added** (the owner: "I agree p7 should be
dropped"), there being no registered seed-to-sink requirement for such a flag to serve, while a readable drug marker
would work against a drug node holding no identity and would leak the structure of a target-held-out split
(`mechanistic_pathway_learning/evaluation/target_held_out_split.py`). **The module-growing phase excludes entry nodes
by the constant that defines them, and this is built** (the owner: "make sure that the module growing excludes drug
nodes", "Alleles too", "You can actually use that constant as the exclusion rule"): the rule is `node_type in
ENTRY_NODE_TYPES` rather than a list of names, so a later entry node type is excluded by construction, and the module
gate of `mechanistic_pathway_learning/models/noisy_or_pathway_module_model.py` takes the mask
`mechanistic_pathway_learning/evaluation/experiment_data.py` builds from that constant and holds those gates at zero.
Whether a module must contain a seed at all is decision 9.137, ruled on 19 November 2026 to be a decision of its own,
and item 37 is written so that the requirement can be dropped without reopening this sub-item. The duplicated edges
of the drug and compound pairs are removed with their signs preserved, which on the built graph changes no result;
methylphenidate is split into its two enantiomers on the escitalopram precedent, its enantiomer-specific values still
to be sourced; and the audit rows marked for secondary verification take a second independent source before any is
relied on, the two that rest on a label alone being named with the routes tried. The curated graph-compound set, the
enantiomer values and the metabolite exposures are `[P 17]`.

**37n. A minimal regional structure, with the regions the labels hold.** The owner, 18 November 2026, choosing among
three forms: "i choose option C" - region-by-class channel groups for a few regions with projection edges, the
regions chosen by the axes the labels hold - after agreeing to "minimal regional structure. we just need to rule on
what form" and ruling that the parcellation comes from the atlas's own dissections and not from HPA's thirteen
consensus regions (the owner: "use siletti"), which hold one basal ganglia region and so cannot separate dorsal from
ventral striatum. **The regions, confirmed by the owner on 23 November 2026** ("Let's start with those regions"), as
the list reads and as a starting set a later ruling may extend: dorsal striatum for the motor axis; ventral striatum
and nucleus accumbens for the impulse and psychotic axes; prefrontal cortex for cognition and the psychotic axis;
hypothalamus for sleep and appetite; the brainstem and midbrain source nuclei; and the histaminergic projection for
somnolence. The tuberoinfundibular projection is left out because the label set holds no endocrine symptom, so it has
nothing to fit. The structure is monoamine and histaminergic projection edges with regional copies of the
fast-cleared pools, release at the terminal region, and the receptors shared. Costs recorded with it: region-by-class
weights from the atlas's per-dissection files, a curated projection table with two sources per row, and a map from
the primate parcellation onto these regions. Headroom stays one value per node under 37e, and the glycine value that
took a cortical measurement for the whole forebrain splits per region once this is built (the owner: "go with cortex
for glycine for now with a note to followup"). The fuller version - regional pools, a readout per region, and the
connectivity even the pools need, since a projection neuron's mRNA sits at its somata and its release at its
terminals - is decision 9.136, one decision outside item 37. The projection table and the region-by-class weights are
`[P 18]`.

**37o. Human-GEM's identifiers are repaired where the model is read, with guard tests, and the duplicate proton is
merged into one node per compartment.** The owner: "Q1-4 suggestions accepted", and, on the duplicate: "i thought
they NEEDED to be merged ... no other valid options exist". So: a corrections table applied where the metabolite
table is read, rather than an edit of the pinned raw file, carrying the five identifier corrections and a blank for
the one whose correct identifier would move three labels onto the wrong node; a guard test that fails when a
metabolite's ChEBI identifier resolves to an isotopically labelled record or is absent from the pinned release, which
would have caught all 23 affected metabolites; the 17 identifiers absent from that release taking upstream's
replacements, each checked individually rather than as a batch, under the rule that related decisions are decided one
by one; and a second guard test that fails when rows sharing one compartment-stripped identifier disagree on
structure or on model name. **The duplicate proton is merged**: the model annotates H+ as proton where Reactome uses
hydron, so the build carries a second H+ of seven nodes and 90 Reactome edges beside the first, with second nodes for
3-methoxytyramine and coenzyme A as well; these become one node per compartment. **Two cross-compartment conflicts
are repaired as one row filed under the wrong metabolite id, neither being a wrong ChEBI id** (the owner: "Q5 a-c
accepted"): the cytosolic row of one entry is palmitoylethanolamide and moves to the node of that name, its three
mis-assigned identifiers corrected, while the extracellular row keeps the C16:1 compound; and the other entry holds
two unrelated compounds and is split, the mitochondrial row taking a new id unused in the pinned files and the
nuclear row keeping its own. Both repairs need a species rename where the model is read and so change the graph
version; no drug, binder, enzyme or Reactome edge touches the four nodes. **The amidase's compartment is the
lysosome** (the owner: "Q5d just MAR20093: start fable pass now for the other NAAA reactions to each be decided
individually"), on an acid pH optimum and two independent lines against upstream's cytosol, with its other reactions
decided one by one and the five verdicts accepted (the owner: "accept the five NAAA verdicts"): two ethanolamide
reactions move with the gene kept, two ceramide reactions move with a two-gene rule, and one loses the gene and is
otherwise unchanged. The supply the move leaves missing is a reversible, gene-free cytosol-to-lysosome exchange,
added because its sources passed the check the owner set ("yes, option 1 as long as it passes the check"), a form
with a gene or with one direction having failed it. Pristanic acid takes the stereochemically specified structure
with both identifiers kept, since one is how the reaction is named and the other is the only route the label mapper
has (the owner: "Pristanic acid accept"); and one hydroperoxide reaction is rewritten as a glutathione-dependent
reduction with the peroxidases as its genes (the owner: "15(R)-HEPE accept"), its two other compartment copies left
as pinned and flagged for follow-up, those compartments carrying no oxidised glutathione in the model (the owner:
"flagged for follow-up"). The corrections table, the renamed species and the counts the guard tests expect are
`[P 19]`.

**`[R 8]` keeps its number and stays open**: ambient serotonin, where microdialysis and voltammetry disagree by a
factor this registration does not split, and the peptide receptor bands. Both were deferred by the owner on
19 November 2026 and neither is filled here. The third deferral the owner made with them, how the calibrated
regression scores a depletion study for a soft bound, is not item 37's and has moved to decision 9.59, where that
regression lives.

**What this amendment changes in the registration, and what it does not.** It registers the rules above before they
are built, which is what decision 9.129 left owed and what the owner asked for; every number a rule still needs is a
`[P n]` and every rule still unsettled is an `[R n]`, so no reader need infer which. It changes no registered rule:
`configs/registered_rules.json` holds the same twelve rules it held before, which was checked and not assumed, so the
commit that registers this item carries no `Amends:` trailer; the `normalisation` rule's withdrawal belongs to the
commit that builds 37f's root-finder, as 37f says. It changes no model, head, threshold, split or level: items 25, 33
and 34 stand word for word, the order H1 then H2 and P1 stands, and the tested model is unchanged until the amendment
37f's build will need. It is outcome-blind: no lockbox has been drawn, decision 1.1 being open and waiting on the
owner's go-ahead, so no confirmatory result existed to see. **Seven decisions are recorded with it and are not part of
it**: 9.133, the clearance ruling of 37k, closed with its build owed; 9.134, how a sourcing sample is drawn once the
held-out split is fixed, which is project-wide and which item 37's own sourcing does not wait on, being exhaustive and
drawing no sample; 9.135, whether an enzyme's pH optimum centred on its compartment's resting pH is a defect to
repair; 9.136, the fuller regional structure of 37n; 9.137, the module's seed requirement; 9.138, the search for
several steady states of 37f; and 9.139, the anchored prior on the module-to-symptom links, which sits on the readout
side item 37 does not build. **What it owes**, besides every placeholder: the rebuild of the dry run and the measured
sensitivity rank, which the owner put after this registration ("should happen after item 37 is pushed remote"); the
records decision 9.129 and the draft's own list leave owed, among them the reading rules of 17 to 20 November 2026 as
rows of their own and lines in `CLAUDE.md`, the three committed Kp,uu values of decision 9.123, the GENCODE licence
row and GTEx recorded as unverified in `docs/data_sources.md`, and that document's single-cell-type row; and the
drug-target screen's identifier-cache repair. Decision 9.132 holds that list in one place.

Amendment, 23 November 2026 (second), written before any lockbox run and before the held-out set has been drawn
(decision 1.1 is open).

**38. The primary claim is held-out prediction: the registered model predicts the labelled symptom associations of
perturbations held out by leakage group better than the registered baselines, given current curated physiology.
Hypothesis mining and causation are not claimed. The equifinality indices are descriptive only** (the owner, 23 November 2026, of this
heading and of (a): "wording accepted"). Decision 9.131 recorded on 13 November 2026 that the exam claims hypothesis mining, by the recovery of
untrained true causal hypotheses. That ruling never reached this document, and on 23 November 2026 the owner set it
aside for the current experiment: "I like that framing but I think it requires a much higher burden of proof than
current data can show"; asked whether the current experiment can show hypothesis mining or the recovery of held-out
causal links, "I don't think the current experiment can truly show it", meaning "both"; and of the ruling itself,
"Not claimed for now. Will need separate experiment with different lockbox draw, etc and will only validate the
method not the model." Until today this document's opening still named the equifinality indices as the primary
hypothesis.

**a. The claim.** For perturbations held out of training whole (genes by the registered disease-cluster grouping,
drugs by item 25's target rule), the registered model ranks the labelled perturbation-symptom pairs above the
unlabelled ones, within each symptom (macro) and pooled (micro), better than the best of the six registered
baselines. "Given current curated physiology" is part of the claim: the model reads a graph built from today's
curated resources, (c). The claim is about labels. A label is a recorded association between a perturbation and a
symptom: a symptom annotated to a disease a gene is recorded as causing, or an adverse event on a drug's label.
**`induces` is the name of the relation those labels are filed under. It is not an assertion that the perturbation
causes the symptom**, and nothing in this registration tests that it does. Nor is the claim that the model finds
links before they are known: every held-out label was already recorded when the model was built.

**b. The test is the confirmatory test already registered, unchanged.** H1 as it stands is the test of the claim:
the macro, micro and both within-strata readings of the tested model minus the best registered baseline of each
reading, above zero on the held-out set, decided by the paired interval with no magnitude floor at the registered
level (`configs/registered_rules.json`; items 18, 25, 33 and 34). The baselines are the six
`experiments/score_confirmatory.py` holds: popularity, degree_popularity, the two per-type baselines of item 32a,
the random walk with restart and TransE. H2, read after H1 as item 18 registers, says whether the content of the
graph carries the prediction, and not its degree sequence alone: the model on the real graph against the same model
on a graph rewired within each relation. P1 follows as registered. This item adds no reading to the tested family,
removes none, and changes no model, split, threshold or level.

**c. What "held out" covers, and what it does not** (confirmed by the owner, 23 November 2026: "right"). It covers
the labels: no label of a held-out perturbation enters training, and the leakage groups keep the same pair from
arriving through a second label source or a drug sharing a target. It does not cover the graph. The graph is built
from curated resources and this project's quoted rows over every perturbation, before the held-out set is drawn; no
edge carries a date, and nothing restricts the graph to what was known before a pair was recorded. So a held-out
pair can be predicted because the edges encode the research that established it. H2 says whether the graph's
content carries the prediction; it does not say whether that content is independent of the pair.

**d. Separate reporting by when a pair was first reported: a descriptive reading** (the owner, 23 November 2026: "I
actually disagree that when it was established is irrelevant because that is highly correlated to the type and
amount of research available for the pair"; on how it should enter: "I was just thinking separate reporting. Thin
evidence but cheap to do"; and on what dates a pair: "Why not go by earlier if fda and first paper publish date?",
of which the first-paper half is the rule, approved by the owner the same day, and the approval half is not used,
for the reason given below). Decision 9.131 had recorded the owner on drug-relief hypotheses: "when the
drug-indication pair was established is irrelevant"; this reverses it.

*It is not a time split.* The model is the registered model, trained on the pairs of every era. The reading shows
whether the model-minus-baseline difference on the held-out set sits mainly in pairs reported early. It cannot show
that the model would have predicted a pair before it was reported: the model has seen pairs of the same era in
training, and the graph it reads is today's, (c). `docs/experiment_design.md` A5 calls a time split one of the
"mandatory parts of the primary analysis"; this registration carries none, registers none for later, and this
reading is not one.

*A pair's date is the publication year of the earliest record the search of (g) counts for its cell*, for genes
and drugs alike, the year being read from that record's PubMed metadata. It is a by-product of the search of (g) and
needs no curation. A cell for which the search counts no record has no date. The dates are hashed and committed
with the counts of (g), before the draw.

*Why a drug's approval year is not used.* An approval dates the events on the original label and not a pair, and
papers on a drug's adverse effects mostly follow its approval, so the earlier of the two would nearly always be the
approval year. No approval date is read, for the main reading or beside it.

*Its weaknesses, stated.* First, the earliest record that names a perturbation and a symptom together is not
necessarily a report that one is associated with the other: for a drug it is often a paper on the symptom as the
drug's indication, or on the symptom in the treated disease, and for a gene it may be a record that names the
symptom in passing. The date is therefore the earliest co-mention, and is at or before the first report, by an
amount the read sample of (g) measures. Second, the further back a record lies the less of it can be searched, (g):
nearly every PubMed record up to 1965 and most of those up to 1989 have no abstract, so an old record is found only
if its title alone names both the perturbation and the symptom. An early pair is therefore dated too late, or not
at all, and the earliest era of a type is thinner and later than the literature it stands for. Third, the National
Library of Medicine states that "MEDLINE includes literature published from 1966 to present, and selected coverage
of literature prior to that period" and holds nothing before 1946 (read 23 November 2026). The second and third
bear on the older drugs more than on the genes.

*What "early" means here* (the owner, 23 November 2026, to the proposal to say so and to run no full-text reading
of any period: "Ok. Good."). An early pair is one whose earliest record found by title and abstract is early; it is
not a pair known to have been reported early. Pairs of the early eras are undercounted and dated late, because most
older records can match only on their titles: of PubMed's records, those with no abstract are 99 per cent of the
ones published up to 1965 and 63 per cent for 1966 to 1989, against 25 per cent for 1990 to 2005, 16 per cent for
2006 to 2015 and 12 per cent since (Europe PMC's search service, 23 November 2026). No full text is read for any
period to correct this.

*The registered gene date is reported beside it, not replaced.* The `time_split` rule of `configs/evaluation.yaml`
(`publication_of_cited_reference_else_biocuration`) dates a gene pair by the publication the annotation cites and
otherwise by the date of biocuration. Most dated gene pairs carry the biocuration date, which is when the pair was
written into the ontology and not when it was reported, and none precedes 2009 (on release v0.4, 928 of the 1,180
dated gene rows, with 1,854 of 3,034 gene rows undated). So that date mostly records the ontology's curation. The
gene reading is given under both dates, and the first-record date is the one the eras below are cut on.

*The eras.* Genes and drugs are read apart, each on its own cuts, because their literatures are of different ages.
Within a type the eras are the thirds of the first-record year over that type's dated labelled pairs in the whole
table, ties kept in the earlier third; the two boundary years are written with the hashed dates before the draw and
no outcome enters them. Each type is also reported two-way at the end of 2015, the cut `configs/evaluation.yaml` has
held since October 2026, so that one cut is common to both types and to the registered gene date. The cuts are not
moved after the draw.

*A cell with no record is a stratum of its own and is never dropped.* These are the cells for which the search counted
no record, so among positives the undated stratum is the **none** stratum of (g): the
two readings share that stratum and differ only in how they divide the rest.

*How it is scored.* Only a labelled pair is read by its date here: an unlabelled cell may have a first record too,
but a date says when a pair was reported, and an unlabelled pair was not. Each era's positives are scored against
the same unlabelled cells of the held-out set, for the model and the baselines alike; the reading is the
model-minus-best-baseline difference for that era's positives, and AUPRC values are not compared between eras, since
they move with the number of positives alone (the owner, 23 November 2026: "within era makes sense"). `minimum_positives_to_score` applies to an era's
positives per symptom. Intervals are the registered paired bootstrap over leakage groups, at 95 per cent.

*It is reported beside (g) and not crossed with it.* A pair's first-record year and the number of records on it come
from the same search and are correlated (on the released literature table: Spearman -0.62, release v0.4, measured 23
November 2026), so the two readings overlap and are not two independent lines of evidence. They are not crossed,
because the cells would be too thin to read.

*It is descriptive and spends no alpha.* It enters neither H1 nor H2 nor P1, is reported in the section labelled
descriptive beside (e), (g) and item 26, and no interval of it is compared with a level. A difference confined to
the early eras would be what reproduction of long-reported pairs looks like, and also what small late strata look
like; a difference present in the late eras would say the advantage is not confined to long-reported pairs, and
would not say the model predicts ahead of the field.

**e. The equifinality indices are descriptive only** (the owner, 23 November 2026: "e yes. Make them descriptive
only"). The independence index, the convergence index and the sufficiency test by module ablation of
`docs/experiment_design.md` section 6.5 are reported in their own section labelled descriptive, beside the nosology
readout of item 26 and under the same bound: they enter neither H1 nor H2 nor P1 and take no part in the test
sequence. The expectations section 6.5 states per symptom are kept as stated in advance and are compared with what
is found; neither outcome is a test at a level (the owner, 23 November 2026: "good").

**f. Relief is not trained and nothing is claimed for it.** The `relieves` relation is not trained by the
registered model, and no route to predicting what a drug relieves is built or validated (decision 9.131). Nothing
about it is registered here.

**g. A descriptive reading by the research available on the pair: every cell is searched first** (the owner, 23
November 2026, asked "Do you want the per-pair research stratum registered as a descriptive reading?": "2 yes"; on
its measure: "research stratum: each cell has to first be exhaustively searched for first, which should help
alleviate the drug vs gene split though it won't fix it"; and on what that search is: "I meant a fable pass
instructed to be exhaustive"). It answers the owner's objection that when a pair was established "is highly
correlated to the type and amount of research available for the pair", for the amount.

*Who searches, and what.* A research pass on Fable, instructed to be exhaustive, searches every cell of the scored
table, and every cell by the same rule (the owner, 23 November 2026: "I think it has to be for every cell to
mitigate bias"): every perturbation of the evidence table against every scored symptom construct, labelled or not, held out
or not. Under decision 9.134 a count or a date for a held-out cell may be collected; none, for any cell, enters
training, a constraint, a loss, a prior or the label selection. They are read by this reading and by (d) alone. The
search draws no sample. It runs after the evidence table is rebuilt and before the draw of decision 1.1, and its
output is hashed and committed before the draw, so that neither the counts, the dates nor the strata can follow the
held-out set or any score (the owner, 23 November 2026: "correct").

*Where, and what counts* (the owner, 23 November 2026: "I guess I'd rather just do abstract and title only then").
A record counts for a cell when its title or abstract names the perturbation and a term of the construct, both in
that one text. No full text is searched, no copy of a paper is sought or read, and the rule is the same for every
record of every period, so that no cell is searched more deeply than another. The records are journal records of
PubMed and the preprints the next paragraph admits; a PubMed record that belongs to a book or a report, such as a
book chapter or a study guide, is not counted (the owner, 23 November 2026, of this, of searching by text alone
and of the one-service plan: "your 1,2,3 from the strata are accepted"). The filter that sets those records aside is
fixed and verified before the first request `[P 24]`: on the one pair checked, Europe PMC's flag for a record that
belongs to a book removed the two book records and nothing else, where its publication type "journal article"
also removed two letters printed in journals, one of them a case report of the pair. Every record that matches
counts, a label's own cited reference among them (the owner, 23 November 2026, asked whether to leave those out:
"No I don't want that. Keep as is"); so a labelled gene pair whose cited reference names both terms starts with one
record, which a drug pair, whose label cites no paper, has no counterpart for. The search is one request per cell
to Europe PMC's REST search on `www.ebi.ac.uk`, over PubMed's records and the admitted preprints together, ordered
by first publication date, which returns the count and the earliest record; PubMed supplies each counted PubMed
record's metadata, its identifier and its publication date. Requests to that service are spaced 10 seconds apart,
the delay the robots file of `www.ebi.ac.uk` states for every reader (the owner, 23 November 2026: "10 second
pace"). At that spacing, with the further counts `[P 23]` needs, the search is estimated at about 13 days of
continuous running for about 68,700 cells; both figures are estimates, the current table not being built at the
time of this amendment. The text-mined count of the released literature table
(`data/releases/v0.4/literature/literature_reports.parquet`, distinct `pmid` per cell, as
`experiments/rekey_literature_to_fine.py` re-keys it) is kept beside the search's count and does not replace it.

*Preprints follow the project's rule on papers with no peer review* (the owner, 23 November 2026: "follow my rule on
preprints"; the rule, 27 October 2026: "No peer review means toss the paper unless it's recent then just mark it for
follow up", recent being 18 months). A preprint has no PubMed record, so its metadata, its posting date and its
link to a published version are read from Europe PMC's preprint records. A preprint counts for a cell only if it
was posted within the 18 months before the search's last publication date `[P 20]` and Europe PMC links it to no
published version; it is then flagged "not peer reviewed", and the share of a cell's counted records that are such
preprints is reported with `[P 23]`. A preprint posted earlier than that with no published version is not
counted. Where a published version exists, that record is counted, once, and the preprint is not. Europe PMC makes
the link from Crossref metadata and by matching titles and authors, and says of it that "where authors and/or
article titles change between preprint and journal publication, it may not be possible to make this connection"
(Europe PMC in 2023, Nucleic Acids Research, doi 10.1093/nar/gkad1085); so a few published papers will be counted
a second time as recent preprints, and a few old preprints with an unlinked published version will be left out.

*One count.* A cell's count is the number of records counted for it under that rule, and it is the count the
strata use. A cell is **none** when no record counts.

*The limit of what a title and an abstract can show, stated and measured.* An abstract is not there for every
record. Of PubMed's records as Europe PMC's search service returned them on 23 November 2026, those with no abstract
were 99 per cent of the records published up to 1965, 63 per cent for 1966 to 1989, 25 per cent for 1990 to 2005, 16
per cent for 2006 to 2015 and 12 per cent for 2016 onward. The National Library of Medicine says of its records for
1946 through 1965 that "the absence of abstracts affects subject retrieval". A record without an abstract can match
on its title alone. So a pair whose literature is old is found less often than one whose literature is recent: its
count is lower, its earliest record is later, and some such pairs fall in the **none** stratum although papers on
them exist. A match in the body of a paper, which no title or abstract repeats, is never found, for any period.
This is not corrected. It is reported: for every research stratum and every era of (d), per type, the share of
counted records that have no abstract, and the share that are preprints `[P 23]`.

*How a query is built, per cell* (the owner, 23 November 2026: "yes", and, of leaving MeSH headings out, "your 1,2,3
from the strata are accepted"). The perturbation's names AND the construct's terms, with a
fixed last publication date `[P 20]` so a count can be reproduced. A gene: its HGNC approved symbol and approved
name, from the HGNC set `scripts/fetch_raw_sources.sh` pins; a symbol that is also a common
word, or is one or two characters long, is searched by its approved name alone, on a list written by rule before
the run and not edited after counts are seen `[P 21]`. A drug: its name in the evidence table and the international
nonproprietary and United States adopted names ChEMBL lists for it, with the corrections of
`configs/sider_drug_name_corrections.csv`; trade names and research codes are not searched. A construct: the
`hpo_names` and `meddra_preferred_terms` of its row in `docs/symptom_crosswalk_fine.csv`
(`docs/symptom_crosswalk.csv` where a coarse construct is scored), each as a phrase.
A construct is searched by that text alone: its MeSH headings are not searched, being an indexer's judgement of a
record and not its authors' words, and the crosswalk holding one for only some constructs. How the query confines names and terms to the title
and abstract in the service's syntax is fixed and verified before the first request `[P 22]`. The query string of every cell is written to the output
with its counts, the time of each request and the first identifiers returned, so that any count can be checked by
reading. A construct with no searchable term is left out of this reading and named.

*The earliest record.* For every cell with a counted record, the search also keeps the identifier of the earliest
one, whether it has an abstract, and its publication year from PubMed's metadata, or from Europe PMC's preprint
record for a preprint, which is the date (d) reads. The search service returns the count and the earliest record in
one request when the results are ordered by first publication date (checked on one query, 23 November 2026; ordered
by print publication date it put records with no print date first, so that order is not used).

*Being exhaustive.* A failed source is not a finished search: a request that fails or is refused is repeated and, if
it still fails, the cell is recorded as not searched with the reason, never as zero. The pass reports the cells it
could not search, and the reading is not run while any remain unexplained.

*What a count and a date mean, checked by reading* (the owner, 23 November 2026: "20 per stratum is fine, classes
and limit ok"). A count says a record names the perturbation and a term of the construct together; it does not say
the record studied the pair, and the earliest such record is not necessarily a report of the association. So 20
labelled cells per research stratum, per era and per type, drawn by a seeded rule from development perturbations
only after the held-out set is fixed (decision 9.134), are read by the pass; where a stratum holds fewer than 20
labelled development cells, all of them are read and the number is reported. For each cell the earliest counted
record is read and put in one of three classes, defined here: **reports the
association**, when the record states that the gene's variant or loss, or the drug, was observed with the symptom
as its effect, in people or in an animal; **names both, otherwise**, when the symptom is the drug's indication,
belongs to the treated or studied disease, is denied, or is mentioned in passing; **wrong entity**, when the name
matched something that is not the perturbation or the term something that is not the construct. Where the earliest
counted record is not of the first class, the later counted records are read in order of date, up to the fifth,
until one is. Reported per stratum and per era: the number of cells read, the share in each class, and, where a
later record was the first to report the association, by how many years the earliest record preceded it. The strata
and the dates are not changed by what is read.

*The strata* (the owner, 23 November 2026: "median split on nonzero cells makes sense"). Fixed here as a rule on the
counts, which no outcome enters. Genes and drugs are binned apart, each over its own cells. Within a type: if no
more than a third of its cells are **none**, three equal-count strata (tertiles), ties kept together in the lower
stratum; otherwise **none**, and the remaining cells split at their median count into **fewer** (at or below it) and
**more** (above it). Which form applied to each type, and the boundaries it gave, are written with the hashed counts
before the draw. The two-stratum form, none against any, is reported beside it always. Every cell is binned by its
own count, positive or unlabelled, so that a stratum holds its own positives and its own unlabelled cells and an
AUPRC inside it is an AUPRC.

*The scoring.* The reading for genes and for drugs apart is the main one; the pooled reading is given beside it.
Inside each stratum of each type: the registered macro and micro AUPRC of the tested model and of every registered
baseline on the held-out set, over the same seeds; the seed mean of the model minus the best baseline, the best
baseline of a stratum being the one with the highest seed-mean score in that stratum, chosen without reference to
any model (the owner, 23 November 2026: "favor baselines is right"); `minimum_positives_to_score` applied within the stratum; the symptoms that entered,
listed, because the strata will not share one list; the 95 per cent interval of the registered paired bootstrap
over leakage groups; and the number of positives and of cells.

*What the search does and does not settle.* A cell of the released literature table with no co-mention was not
thereby unresearched: a gene pair curated from a disease synopsis has a source the text mining did not link.
Searching every cell by name and term reaches such papers where their title or abstract names both. It narrows
the difference between genes and drugs and, in the owner's words, "won't fix it": drugs are named in far more
records than most genes, a label reports an adverse event whether or not a paper studies it, and a count measures
naming and not study. That is why genes and drugs are read apart.

*It is descriptive.* It is reported in the section labelled descriptive, beside (d), (e) and item 26. It enters
neither H1 nor H2 nor P1, spends no alpha, and no interval of it is compared with a level.

*What each outcome would and would not show, stated before any is seen* (the owner, 23 November 2026: "agreed"). If the difference is
above zero in the **none** stratum, its interval excluding zero, the model's advantage over the baselines is not
confined to pairs the searched literature names together; that is evidence against "it reproduces well-studied
links only", in the sense this count measures. It does not show that those pairs were unstudied, that the graph's
edges were free of the research behind them, or that the model would have found a pair before it was recorded. If
the difference is above zero in the highest stratum and its interval covers zero in **none**, that is what
reproduction of well-studied links would look like, and also what a real advantage looks like in a stratum with too
few positives to resolve it; the number of positives and the interval's width are reported so a reader can judge. A
trend across strata is a description: the strata differ in their share of positives, so AUPRC values are not
compared between strata, only the model-minus-baseline difference inside each. Neither outcome is a test at a
level, and neither confirms nor withdraws H1.

**h. Not claimed.** Hypothesis mining is not claimed (the owner, 23 November 2026: "Not claimed for now. Will need
separate experiment with different lockbox draw, etc and will only validate the method not the model."). Causation
is not claimed. Neither is registered here.

**What this item supersedes in the opening of this file, which is kept as the record.** The line "Primary
hypothesis: see experiment_design.md section 6.5 (equifinality independence and convergence indices; sufficiency
test by module ablation)" is superseded by (a), (b) and (e). The "Primary endpoint" lines beneath it were already
superseded and are named here so that the opening is read whole: the "pathway-wise split" by the confirmatory
specification of 8 October 2026, under which it "becomes a secondary reading on the development set", and then by
item 25; the "relational GNN with sigmoid head" as a comparator by the same specification, the sigmoid head being
dropped afterwards and the tested family being one model since items 34b and 34c; "minimum difference 0.05" by the
passage headed "Superseded on the decision rule"; and "five seeds by five folds" by the single held-out set scored
once over seeds 0 to 4.

**What this item changes in the registration, and what it does not.** It states the claim the registered test tests
and what is not claimed, makes the equifinality indices descriptive only, and adds two descriptive readings, (d)
and (g). It changes no registered rule: `configs/registered_rules.json` holds the same twelve rules, so the commit
that registers this item carries no `Amends:` trailer. It is outcome-blind: no held-out set has been drawn, decision
1.1 being open, so no confirmatory result existed to see. It leaves open the values `[P 20]` to `[P 24]`,
and decision 5.2 (whether P1 is primary at all) as it was. No time split is registered or held open. The
search of (g) is owed after the rebuild and before the draw.

To fill in: Phase 1 counts per symptom and grade (docs/generated/phase1_counts.md); final symptom set after
go/no-go; B5 language model and prompt; power statement for the
GWAS enrichment test; the open questions 8 to 10 of design section 11 (frequency as weight or target;
subsystem versus curated pathway split; the deterioration-term exclusion).
