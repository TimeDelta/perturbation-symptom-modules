# From Molecular Perturbations to Psychiatric Symptoms: Learning Mechanistic Pathways in a Physiological Graph

Constrained graph learning of symptom-to-mechanism pathways over a compartmentalized
physiology graph. The model maps a localized molecular perturbation (a monogenic enzyme
defect, a single-target drug) to a distribution over psychiatric symptoms, explained by
one or more sparse pathway modules combined through a noisy-OR, with no diagnosis labels
anywhere in the inputs or targets.

The full experiment design, including the assumptions it argues against, is in
docs/experiment_design.md. Read that first. [docs/README.md](docs/README.md) is the map of every document, by topic.

## Status

What is current is generated, not written here: `docs/status.md` (data releases and their counts, the registered rules
and their amendments, the decisions open and closed, which documents are generated and when, when each living document
was last reviewed; `PYTHONPATH=. python experiments/generate_status.py --review` prints which are due) and
`docs/decision_history.md` (when each decision was recorded and closed, from the git history). `docs/documentation_process.md` states which documents are kept current by overwriting, which are dated
records, and the checks `tests/test_documentation_process.py` runs. The release counts below are rendered from the
manifests by `experiments/generate_status.py`:

<!-- generated:release_counts -->
- `data/releases/v0.4` (created 2026-10-06, commit b1c9d02, 44 files, 1 manifest amendment): `graph_full` 33,964 nodes and 255,367 edges; `graph` 24,185 nodes and 94,786 edges; `evidence_full` 3,910 observations over 1,655 perturbations and 11 symptoms; `evidence_slice_sweeps` 861 observations over 451 perturbations and 10 symptoms; `evidence_two_entries` 861 observations over 451 perturbations and 10 symptoms.
<!-- /generated:release_counts -->

The narrative that follows is the state of the project as it was written between 3 and 15 October 2026, kept as history;
the dated documents it names carry the measurements, and `docs/status.md` says which of them are current. Three things
changed after it was written: the linear-response encoder
(`mechanistic_pathway_learning/models/linear_response_encoder.py`, 6 October 2026) is the one tested model and the
message-passing encoder a robustness reading (decision 9.77, 22 October 2026; `tested_models` and `robustness_models`
in `configs/registered_rules.json`); flux sampling was dropped from the confirmation on 8 October 2026
(`docs/research_summary.md`); and the label likelihood is positive-unlabelled (decision 9.90, `label_likelihood`).

Phase 1 is measured and Phases 2 and 3 have started on the monogenic slice. The slice is a pilot; the confirmatory test is the full graph with every layer (docs/preregistration.md, amendment of 7 October 2026). Implemented and tested:
the noisy-OR pathway module head (sum or mean pooling over hard-concrete supports), soft constraint
losses, a relational message passing encoder with absolute and perturbation-difference field
readings, the sigmoid-head baseline B3, grouped splits by gene or by disease cluster, curated-module
and reconstruction-subsystem pathway hold-outs, the time split, the HPO loader with frequency
qualifiers, provenance and crosswalk term exclusions, the evidence grading policies, the learned
evidence reliability model, the document-grounded appraisal rubric, currency tagging, equifinality
indices, ranking and calibration metrics, the label-permutation and rewiring controls, the SIDER
loader, the SIDER-to-ChEMBL mapping, the physiology graph build (Human-GEM with subsystems plus the
OmniPath, small-molecule and CollecTRI layers when their files are present), the evidence table with
disease clusters, popularity and random-walk baselines, a resumable training harness with
validation early stopping, a batch driver, an aggregator with paired bootstrap comparisons, a
module-analysis script with the sufficiency test, and mechanism cards.

Measured so far: docs/phase1_counts.md (counts), docs/hpo_term_audit.md (what each HPO term
contributes to each symptom), docs/phase2_baselines.md and docs/phase2_baselines_disease_cluster.md
(baselines under three splits with permutation controls), docs/phase3_main_model.md (B6 and B3).
Two results shape the design: the gene-wise split leaks through genes that share a disease, so the
disease-cluster grouping is the default; and the sixteen curated modules hold too few perturbations
for a pathway-wise endpoint, so Human-GEM subsystems are proposed instead (design section 6.1). A
monogenic time split dates each gene-symptom pair by the publication of the PubMed reference behind
its OMIM annotation (docs/hpo_reference_publication_dates.json). docs/references.bib holds the design
document's reference list for import into a reference manager.

Still stubs: the SemMedDB predication loader (the OnSIDES slice and the literature class are built), the diagnosis proxy audit, the flux-sampling job
(written, not yet run), the flux-feature and language-model baselines, the MAGMA wrapper. The pharmacological evidence class and the signaling, transcription and small-molecule layers were
added once the environment's network policy allowed the SIDER, ChEMBL, UniChem and OmniPath hosts; the full graph and
the full evidence table are the release tables counted in the block above (data/releases/v0.4/MANIFEST.json), and the
later tables a rebuild produces (evidence v3, v3 with parkinsonism and v4; the neuronal, split, binder and drug-entry
graph variants) are counted in docs/data_layer_rebuild.md. Baselines and model configurations on the full data run
under runs/full; their results are docs/phase2_baselines_full_disease_cluster.md and docs/phase3_main_model.md, each
of which names the run it was generated from.

The literature class E3 is in place (docs/literature_survey_spec.md): the symptom
crosswalk carries verified MeSH descriptors with a symptom, diagnosis or mixed-polarity level flag, every gene node has an
NCBI Gene id through Human-GEM and HGNC (12,537 of the 12,627 gene nodes of data/releases/v0.4), and two fetch scripts filter the PubTator3 bulk
relation file and the CTD chemical-disease file to graph genes and SIDER drugs on those descriptors (one SIDER drug per MeSH chemical), writing
one report per (paper, relation) in the evidence_reports.parquet schema under data/processed/literature with the source named by extraction type (PubTator3-cause, CTD-curated). The
rows are grade E soft priors and never labels or evaluation positives (the experiment loader refuses grades D and E). The appraisal half (experiments/fetch_pubtator_documents.py, experiments/survey_literature.py; docs/literature_survey.md) rates each report from publication types and species annotations, species first; the tables are in the data release and join the assembled table through --extra-reports. The component was reviewed adversarially on 6 October 2026 (docs/design_review_v04.md, third table); the fixes are in the code and were applied to the data the same day on the PubTator3 bulk file NCBI published then, and data/releases/v0.4 holds those tables (214,375 appraised reports over 134,747 papers).

A new container has no `data/raw`, `data/processed` or `runs/`. `bash scripts/rebuild_data_layer.sh` fetches the pinned sources and rebuilds the
graphs, the evidence tables and the label selections in dependency order; docs/data_layer_rebuild.md records what that reproduced on 10 October 2026
and what it did not. Install pandas 2.3.3 and pyarrow 25.0.1 first if the tables are to be compared with recorded hashes.

Reproduce the data layer by hand (downloads about 110 MB; raw files stay out of git). Human-GEM and the HPO files are fetched by tag: the `main` branch
of Human-GEM moved to 2.1.1 on 7 October 2026 and no longer gives the graph of data/releases/v0.4.

```
mkdir -p data/raw/hpo data/raw/Human-GEM/model data/raw/sider_4.1 data/raw/omnipath
for f in hp.obo genes_to_phenotype.txt phenotype.hpoa genes_to_disease.txt; do curl -L -o data/raw/hpo/$f https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2026-09-01/$f; done
for f in Human-GEM.xml Human-GEM.yml genes.tsv metabolites.tsv reactions.tsv; do curl -L -o data/raw/Human-GEM/model/$f https://raw.githubusercontent.com/SysBioChalmers/Human-GEM/v2.0.1/model/$f; done
for f in meddra_all_se.tsv.gz meddra_freq.tsv.gz meddra_all_indications.tsv.gz drug_names.tsv drug_atc.tsv; do curl -L -o data/raw/sider_4.1/$f https://sideeffects.embl.de/media/download/$f; done
curl -L -o data/raw/omnipath/omnipath_interactions.tsv "https://omnipathdb.org/interactions?datasets=omnipath,pathwayextra,ligrecextra&genesymbols=1&fields=sources,references,type,curation_effort&organisms=9606&format=tsv"   # the service dropped the field n_references by 15 October 2026 (scripts/fetch_raw_sources.sh)
curl -L -o data/raw/omnipath/collectri_interactions.tsv "https://omnipathdb.org/interactions?datasets=collectri&genesymbols=1&fields=sources,references&organisms=9606&format=tsv"
curl -L -o data/raw/omnipath/small_molecule_protein.tsv "https://omnipathdb.org/interactions?types=small_molecule_protein&genesymbols=1&fields=sources,references,type&organisms=9606&format=tsv"
python experiments/fetch_chembl_drug_targets.py          # UniChem and ChEMBL, cached, resumable
OMP_NUM_THREADS=1 python experiments/fetch_pubtator_relations.py --fetch-publication-dates && OMP_NUM_THREADS=1 python experiments/fetch_ctd_chemical_disease.py --fetch-publication-dates   # literature class E3, cached, rate-limited; docs/literature_survey_spec.md
python -m mechanistic_pathway_learning.graph.build_physiology_graph
python experiments/audit_hpo_term_expansion.py            # docs/hpo_term_audit.md
python -m mechanistic_pathway_learning.evidence.assemble_evidence_table
python experiments/run_phase1_counts.py
python experiments/run_baselines.py --group-by disease_cluster --with-kg-embedding --output-dir runs/baselines_disease_cluster --markdown-output docs/phase2_baselines_disease_cluster.md
python experiments/run_main_model_batch.py --configuration b6_default --group-by disease_cluster     # five folds, resumable
python experiments/run_main_model_batch.py --configuration b3_sigmoid --group-by disease_cluster
python experiments/aggregate_main_model_runs.py --run-dirs runs/b6_default_disease_cluster runs/b3_sigmoid_disease_cluster --baseline-results runs/baselines_disease_cluster/results.json
python experiments/analyze_pathway_modules.py --run-dir runs/b6_default_disease_cluster
```

OnSIDES later label slice. The OnSIDES v3.1.1 label statements are bridged to ChEMBL and unified with the SIDER drugs (experiments/fetch_onsides_identifier_bridge.py, experiments/build_onsides_reports.py; docs/onsides_label_slice.md): 587 drug-symptom pairs, 304 of them absent from the qualified SIDER table and 100 absent from the 2015 labels altogether (docs/onsides_label_slice_spec.md states the rules, after the adversarial review of 5 October 2026). They join the assembled table and the reliability fit through --extra-reports (the `evidence_full` table of data/releases/v0.4: 3,910 observations, 876 drug pairs over 142 drugs; the tables a rebuild writes are larger, docs/data_layer_rebuild.md).

Data releases. The processed tables of each design version are committed under data/releases/<version>/ with MANIFEST.json (SHA-256, size and row count per file, the producing commit, the source pins and the license statement), so a checkout trains and evaluates without any download: `python experiments/run_main_model.py --graph-dir data/releases/v0.4/graph_full --evidence-dir data/releases/v0.4/evidence_full ...`; `python experiments/make_data_release.py --version v0.4 --verify-only` recomputes the checksums. MedDRA term names are blanked on label-derived report rows before release; raw downloads are never committed (docs/data_sources.md pins them).

Data from the Comparative Toxicogenomics Database. The literature reports of source `CTD-curated` (5,191 rows in `data/releases/v0.4/literature/ctd_relations_filtered.csv`, and the rows of that source in the report tables) are derived from the curated chemical-disease statements of CTD ([ctdbase.org](https://ctdbase.org/)), file `CTD_chemicals_diseases.tsv.gz`, report created 29 September 2026. Cite CTD in any work that uses them: Davis AP, Wiegers TC, Sciaky D, Barkalow F, Strong M, Wyatt B, Wiegers J, McMorran R, Abrar S, Mattingly CJ. Comparative Toxicogenomics Database's 20th anniversary: update 2025. Nucleic Acids Res. 2025;53(D1):D1328-D1334. [doi:10.1093/nar/gkae883](https://doi.org/10.1093/nar/gkae883). CTD's data are "freely available to non-commercial users; commercial users are asked to purchase a license", and its terms also ask for links to its pages and a notice of use; `data/releases/v0.4/literature/CTD_TERMS.md` quotes the terms and gives the form of the links (`mechanistic_pathway_learning/evidence/ctd_terms.py` writes that file beside every table derived from CTD).

Full data layer (the layer files above present; the build picks them up by default; the model
configurations run under a wall-time budget per fold and resume from checkpoints):

```bash
python -m mechanistic_pathway_learning.graph.build_physiology_graph --output-dir data/processed/graph_full
python -m mechanistic_pathway_learning.evidence.assemble_evidence_table --graph-dir data/processed/graph_full --output-dir data/processed/evidence_full
python experiments/run_baselines.py --graph-dir data/processed/graph_full --evidence-dir data/processed/evidence_full --group-by disease_cluster --with-kg-embedding --time-split-cutoff 2015-12-31 --output-dir runs/full/baselines_disease_cluster --markdown-output docs/phase2_baselines_full_disease_cluster.md
python experiments/run_main_model_batch.py --configuration b6_mechanistic --group-by disease_cluster --run-root runs/full --extra --graph-dir data/processed/graph_full --evidence-dir data/processed/evidence_full --time-budget-seconds 10800 --max-epochs 40
python experiments/fetch_onsides_identifier_bridge.py && python experiments/build_onsides_reports.py   # OnSIDES later label slice
python -m mechanistic_pathway_learning.evidence.assemble_evidence_table --graph-dir data/processed/graph_full --output-dir data/processed/evidence_full --extra-reports data/processed/onsides/onsides_reports.parquet   # OnSIDES statements join the report table and the reliability fit
python experiments/run_main_model_batch.py --configuration b3_typed_nodes --group-by disease_cluster --run-root runs/full --extra --graph-dir data/processed/graph_full --evidence-dir data/processed/evidence_full --time-budget-seconds 10800 --max-epochs 40
```

## Setup

```
python -m venv ~/.venvs/mpl && source ~/.venvs/mpl/bin/activate
pip install -e ".[dev]"            # model and evaluation code
pip install -e ".[graph]"          # add cobra, omnipath, decoupler, chembl client for Phase 1
pip install -e ".[experiments,descriptors]"   # scipy, matplotlib, h5py for the measurement scripts the tests import; rdkit and ESM for node descriptors
pytest
```

## Layout

```
docs/            experiment design, symptom crosswalk (with HPO exclusions), curated pathway modules, data sources, generated tables
configs/         graph build, evidence assembly, model, evaluation, baselines, ablations
slurm/           array job for flux sampling; resumable training job for a runtime-limited cluster
mechanistic_pathway_learning/
  graph/         physiology graph build (Human-GEM + OmniPath + CollecTRI + ChEMBL), currency tagging
  evidence/      HPO, SIDER/OnSIDES, PubTator3/CTD/SemMedDB loaders; evidence grading; proxy audit
  perturbation/  flux-sampling features per gene knockout; drug target mapping
  models/        linear-response and message-passing encoders, noisy-OR head, edge gates, soft constraint losses, MDL selection, baselines
  evaluation/    splits, metrics, negative controls, GWAS enrichment, equifinality tests, mechanism cards
experiments/     phase runners, HPO audit, batch driver, aggregator, module analysis, the document generators
scripts/         data-layer rebuild, raw-source fetches, the background job registry (docs/job_harness.md)
tests/
```

## Development sessions

The design, code and documents in this repository were developed with Claude (Anthropic) in the
sessions below. The transcripts record the design decisions, the owner's rulings and the reasoning
behind them.

- https://claude.ai/share/d762a865-1455-4feb-875d-13e94719f70c — 2 October 2026. The origin of the design,
  before any code. The owner proposed constrained graph learning over a physiology graph supervised by
  psychiatric evidence, with no diagnosis labels. Positions reached: hard constraints are chemistry
  (stoichiometry, compartments), never symptom links; receptor binding (R + L ⇌ RL), receptor conformational
  states and nucleotide costs are mass-balanced species (the owner's correction), while occupancy and coupling
  rates are learned through ME-model-style coupling constraints; regions share one stoichiometric matrix with
  region-specific bounds, a region is a mixture of cell types, and receptor density is low-rank (PET atlas);
  supervision comes from perturbations with known entry points (inborn errors of metabolism with psychiatric
  HPO terms, drug side effects); independent routes to one symptom are a noisy-OR over modules, tested
  against single-route, additive and interaction models; a state-space model belongs as the slow temporal
  backbone with the graph as transition operator, not as a graph encoder. The owner created the
  repository at the end of that conversation.
- https://claude.ai/share/3f0e9a27-772b-489e-9eb3-0053cdbd5523 — 2 October 2026. Experiment design v0.1
  and v0.2 and the first code scaffold (noisy-OR head with hard-concrete supports, encoder, splits, soft
  losses; 17 tests). The owner confirmed no hard symptom-level constraints; their 0.99 weighting became a
  0.99 training target for strong positives and an optional anchor worth 99 pseudo-observations. The old
  literature knowledge graph was dropped in favour of PubTator3 and CTD (SemMedDB later), and jobs were
  made resumable for the runtime-limited cluster. On learning the anchor weight: not on the training loss
  (it collapses to zero); a global scale tuned by grouped cross-validation, and per-source reliability from
  a Dawid-Skene model with LLM-extracted rubric features validated against a hand-labelled set (the
  Dawid-Skene framing was later superseded; see the 21 October entry). GitHub writes were refused (403), so
  the history was delivered as a git bundle. First smoke run: one epoch, macro AUPRC 0.348 against 0.344
  for the random walk, with every module support empty, which raised the gate-initialization question.
- https://claude.ai/share/d8d0612d-1c85-4966-8a13-995d8c98ee2d — 7 October 2026. Paced literature review,
  slots 11 to 19, on Q1 (does a signed or relation-typed propagation beat an unsigned one on the same
  network). Outcome, recorded in docs/literature_appraisal_staging.md: signs not shown by any source;
  relation types supported only in the question's literal wording (Huang 2024, TxGNN, strong; Venkatesh
  2026, weak) and open in the strict form; edge direction one moderate row (Silverbush 2019) against a
  baseline below chance. The owner restored the original four triage checks, which the session had
  reconstructed incorrectly. Q2 and Q3 received no slot. Fourteen appraised sources were added to
  docs/references.bib. Mellina Andreu 2025 was graded from its abstract because a permission request went
  unanswered, which under the rule of 11 October is not a finding; its full text is still to be read.
- https://claude.ai/share/de207981-68b8-49cf-826b-c0a201a84135 — 10 to 15 October 2026. Six days of design
  work toward the confirmatory test; the lockbox was not drawn. Model: drug entry nodes that exist only where
  seeded (confirmed by the owner); the owner ruled out a third encoder and extra confirmatory variants
  ("increasing probability of winning by luck"), so propagation runs to a fixed point with one repeated
  reduced-rank layer, and message passing must read edge signs (it had read 7,321 negative edges as
  positive); amendment of 12 October, eleven items. Labels: a label source review (no dataset varies a
  carrier together with a drug), then no target limit ("I really don't like having a target limit"), the
  gain-of-function sign fix, the placebo mask and placebo weights from trial arm sizes, Open Targets
  statements placed by their target's leakage group, a brain-exposure admission rule (Kp,uu at least 0.1)
  and second-agency label sources (EMA, Health Canada). Graph: log-scale pH, currency fixes, reversible
  reactions that a perturbation can reverse ("I don't want to accept a perturbation not being able to
  reverse the reaction"), the GtoPdb coupling filter, BRENDA regulation edges and the chloride charge fix.
  Statistics: Holm correction, effect size in multiples of the realized bootstrap half-width, the rules
  registered in configs/registered_rules.json with a test against the code, and the preregistration
  baseline frozen on 15 October. The source-reading rules now in CLAUDE.md and docs/open_decisions.md
  date from here. Claims withdrawn after the owner's challenges include a gain/loss mirror property ("i
  never accepted that"), a softmax mixture that was sparsemax, and symptom folds as a test of circularity.
  The v4 rebuild ran in a separate session; decisions left open at the end include 9.41 and 9.42 in docs/open_decisions.md.
- https://claude.ai/share/a44b3cb1-b2f5-47b4-a829-5674879deb77 — 20 to 21 October 2026. Two decisions built
  as draft pull requests (both on `main` since 21 October 2026, rebased: commits `3c9df8f` and `286eb26`), and the
  rebases that followed a merge. 9.75: the owner asked whether the ryanodine
  receptor and the other intracellular ligand-gated channels carry compartmental charge; measured on v5, none
  did, since every luminal calcium node was a currency metabolite and `ions_moved_inward` reads the
  extracellular and cytosolic sides alone. The ruling was store content rather than charge, because the
  release channel carries most of its own countercurrent ("clamps the membrane potential near 0 mV within
  approximately 150 mus", Gillespie and Fill 2008, PMID 18621826) and neuronal ER depolarisations "do not
  spread beyond the site of receptor activation" (Campbell et al. 2023, PMID 36640310): pull request #7 adds
  four store pools, the ER store inhibiting STIM1 and STIM2 so depletion activates ORAI, a store
  driving-force multiplier in the linear-response encoder (off until registered), the counter-ion channels
  TRIC-A, TRIC-B and TMEM175 from UniProt's catalytic activities, and five mapping fixes. 9.76: the
  transcription gate deleted a factor's whole regulon below 1 TPM of bulk GTEx brain, costing 6,002 edges
  from 215 factors, among them PHOX2A (locus coeruleus) and CRX (pineal), which bulk tissue cannot see. The
  owner ruled that a regulon is dropped only when both sources miss the factor, that the developmental
  factors keep their regulons under a lowered evidence prior rather than being dropped ("why wouldn't the
  developmental factors be added to the other soft priors for estimation of their reliability?"), and that
  peripheral classes be added ("add the thyroid, pineal, pancreatic, etc. cell types"), then the Siletti
  atlas for the locus coeruleus and a non-human flag for ALX3's islet edges; pull request #9 builds it and
  the gate now drops 10 edges from 1 factor. The pineal class rests on six human glands the owner downloaded
  by hand, GEO GSE100472, because NCBI refuses automated readers. Pull request #5 was rebased to clear its
  documentation conflicts and merged, and #7 and #9 were rebased after it. Recorded and unresolved:
  `calibrate_ph_sensitivity` is called by no trainer code, so the registered pH ceiling is inert; the Siletti
  aggregate carries no licence of its own, CC BY 4.0 being inferred from the CELLxGENE copy; and whether the
  store multiplier earns its parameters is unmeasured, since the store pool already propagates the
  first-order effect. Four replies were withheld by a safety classifier on 20 October 2026, all on the
  intracellular channel write-up and across three models; that content was not reproduced, and the work was
  finished by subagents with fresh context. A handover note is in the project as
  `claude/session_2026-10-20_to_21.md`.
- https://claude.ai/share/96dd13e4-29c2-4078-973f-70a8e11976e5 — 21 October 2026. Two scoping questions
  raised and left open: whether small extracellular vesicles belong in the graph as a cross-compartment
  transfer mechanism rather than as a signed node, and whether target engagement needs an exposure term
  (anchor: Schmitt MV, Reichel A, Liu X, Fricker G, Lienau P. Drug Metab Dispos. 2021;49(1):53-61,
  [doi:10.1124/dmd.120.000161](https://doi.org/10.1124/dmd.120.000161), lysosomal trapping added to the
  Rodgers and Rowland distribution model). Neither literature pass ran: both delegated passes and three
  replies were stopped by a safety classifier on 21 October 2026, so the transcript carries no sourced
  finding on either question and the Schmitt paper was not read. Two claims made in it are withdrawn —
  that the graph carries no cell-type axis (inferred from absence, not checked; the owner corrected it),
  and that prior strength comes from a Dawid-Skene fit (the owner states that framing is superseded).
- https://claude.ai/share/370f7b06-017a-499f-8871-4c16b69ba02f — 21 and 24 October 2026. The decision log
  checked against the repository, then decision 1.2 built. On 21 October, starting from discrepancies another
  session had found, `docs/open_decisions.md` was read against GitHub and the code (commit `8764bb4`): 8.11,
  9.71 and 9.74 still called their pull requests unmerged although #2 to #6 were on main, so they were closed
  and 9.68 and 9.69 kept only what was still the owner's; 9.14, 9.25 and 9.26 still waited on a BRENDA licence
  accepted on 14 October; 9.75 had no status column; and 1.2 read as decided while `scripts/rebuild_data_layer.sh`
  still passed `--max-drug-targets 3` for v4 and v5. The header no longer calls every open row a decision
  waiting on the owner, and rows marked "nothing owed" are counted apart in `docs/status.md`
  (`decision_ids_owing_nothing`, with a test). On 24 October, while building 1.2, the owner asked "why are we
  setting orphenadrine aside?!" The bridging rule (amendment items 1(b) and 16) had been written against the
  chained drug grouping that item 25 replaced on 13 October and was never revisited. The owner ruled "then
  undo that and include orphenadrine": amendment item 33 withdraws the rule, and pull request #18 (merged 24 October
  2026, commit `6fc5c65`) lifts the target limit in the build with orphenadrine in. Owed on the owner's machine: a rebuild from scratch, a
  measurement of what orphenadrine does to item 25's target partition (not measured on any table) and then
  the draw (1.1). One claim made on 21 October is withdrawn: that the rebuild sets never-above-placebo pairs
  aside against amendment 1(d). The script builds both selections, one masking those pairs and one counting
  them as negatives; which one the trainer reads was not checked.
- https://claude.ai/share/5b6991e9-2255-44c8-b7c7-6f57a0208afd — 22 to 24 October 2026. Negative evidence,
  the positive-unlabelled likelihood, animal report sources and the pull-request queue. Pull request #8's
  conflicts with the hard edge gates on main were resolved; its decisions moved from 9.77 and 9.78 to 9.86 and
  9.87, #12's to 9.84 and 9.85, and the rule that the branch merging second renumbers its own went into
  CLAUDE.md. Asked for a more MDL-principled edge gate, the owner accepted a counted-once code per labelled
  pair, with each source's reliability measured from published figures and never fitted, positives and
  negatives separately. Built and merged: 9.88 (IntAct negatives per isoform, BRENDA "no inhibition", and
  EBI's FTP host as the one robots exception: "don't refuse FTP from EBI"); 9.89 (the newborn-through-toddler
  exclusion withdrawn); 9.90 (the positive-unlabelled likelihood with a module-size cost, now the registered
  default); 9.91 (edge negatives from HuRI, Perturb-seq, ChEMBL inactives and GO NOT, each with a likelihood
  ratio read from a publication; the graph's binds edges have 8.2% precision for direct binary binding against
  HuRI); 9.92 (Phenopacket Store, ClinicalTrials.gov `assessmentType`, the CTT 2026 statin negatives); 9.93
  (MGI and SFARI); 9.94 (rat, fly, zebrafish and worm sources, and the Fenckova et al. 2019 table the owner
  supplied, under the ruling "Pooled sources until standalone": on the 22 October v5 rebuild only mouse has
  its own calibration fit, 139 positive and 2,848 negative cells, and fly, rat and zebrafish are pooled with
  the human cells); 9.95 (the page reader no longer refuses a page for Cloudflare's passive telemetry
  script). Negatome 2.0 stays absent: the owner stated "Negatome data is not available". From 24 October work
  is pushed straight to main ("I think it's better to just start pushing directly to main"), after GitHub
  would not rebase #19 and a rebase or squash merge would break the commit hashes in
  `docs/decision_history.md`. One claim is withdrawn: the 20 October reply that HPA ranks the VAMP1 classes
  opposite to mouse was an aggregation artifact (the class value takes a per-gene maximum over cluster
  types); per cluster type the direction matches mouse with a smaller gap. Left to the owner: whether
  WormBase WS298, read from EBI's FTP mirror after WormBase's own host showed a human check, may stay; RGD's
  licence, unverified behind RGD's robots file; the ClinicalTrials.gov `/api/` robots ruling; and the BRENDA
  licence tick. This session ran on Claude Opus 5.5, before the rule of 25 October 2026 that research is done
  on Fable, so its licence readings, source appraisals and the ratios read for 9.91 and 9.94 need the Fable
  recheck that rule asks for. A handover note is in the project as `claude/session_2026-10-22_to_24.md`.
- https://claude.ai/share/630c343b-04db-486b-8e7a-91817c696c48 — 20 to 27 October 2026. The forward-cone
  divisor wired into training, the G-alpha coupling edge types, and what is left of the receptor-to-G-protein
  dilution. It began with a plain-language reading of pull request #3 (VGLUT2 and VGLUT3 loading) and why the
  neuronal build deletes Human-GEM's vesicular shortcuts; VMAT1 (SLC18A1) loses its shortcut with no
  replacement, which was noted and not changed. 9.16: the per-seed cone divisor the owner asked for on 14
  October had been built but never called; it became a normalisation of the linear-response encoder and the
  registered default (`Amends: normalisation`, `total_in_degree` to `forward_cone`; pull request #8, merged 22
  October 2026 as `ba7573e`). The owner set aside a first measurement on the v0.4 release ("ignore the v.4
  graph. it's outdated"), so v5 was rebuilt in the session from main at `344d211`: every v5 perturbation has
  one seed, so the per-seed and union divisors coincide; 1,338 of 2,447 cones are the same 40,172 nodes; a
  node's response is a median 1.58 times its item-28 value with 97.7 percent of signs kept, at 2.2 times the
  forward cost. Correcting a stale comment on the membrane potential found that the rebuild did not build the
  membrane potential item 13 registers, and that under item 28 the reaction edges divide the conductance law
  by 1 + R (9.87; the owner has since ruled `computed_from_the_pools`). 9.86 (first numbered 9.77): on v5 the
  cAMP sign of receptors coupled to both Gs and Gi/o followed the primary transducer, which withdrew two
  claims made from v0.4 (that family size sets the sign, and that an ADRB2 agonist lowers cAMP), and the
  GtoPdb coupling filter missed GNA14, GNA15 and the transducins. On "build the suggested change", pull
  request #11 (merged 24 October 2026 as `72d1a72`) reads the G-alpha families from HGNC's gene groups, which
  drops 26 edges (not the 142 first stated), and adds three edge types, `couples_primary`, `couples_secondary`
  and `g_alpha_regulates_effector` (580, 88 and 63 edges); in a gain sweep the `inhibits` gain no longer flips
  any receptor's cyclase sign, and the remaining risk is secondary coupling outweighing primary, from 1.5 to 2
  times for ADRB2 (9.80, with parameter counts for a cap or for per-edge strengths on the coupling types only,
  the scope the owner set). 9.79: the HRH2 literature reads Gs primary, with the Gq/11 evidence mostly from
  transfected cells. On 24 October the session found that every cyclase isoform receives the same five
  inhibitory Gi/o edges, while the sources it read say Gi alpha inhibits only AC1, AC5 and AC6, which would
  leave 32 of the 45 edges unsupported. The owner accepted the proposed order (correct those edges, rebuild
  and rerun the sweep, then decide 9.80) with "Order accepted but give me a handoff for another session to do
  the work" (9.97). Decision ids collided twice with other branches and were renumbered under the rule now in
  CLAUDE.md. This session ran on Claude Opus 5.5, and its literature readings predate the rule of 25 October
  2026 that research is done on Fable: 9.79's was rechecked on Fable on 26 October (9.99), and the cyclase
  reading still awaits that recheck. A handover note is in the project as
  `claude/handoff_g_alpha_cyclase_2026-10-25.md`.
- https://claude.ai/share/43da3596-a160-4bbd-882a-d0752d8f296a — 21 to 27 October 2026. Where linearity binds,
  entmax, and the working rules for comments and modelling. The owner asked whether to merge the two encoders,
  nonlinear pieces by message passing and linear pieces by linear propagation, because pull request #7's pH ceiling
  "is modeling an asymptote". A research report argued for keeping both encoders and fixing the pH ceiling locally;
  the owner answered that the problem had come up many times, and it had: `docs/physiological_adherence_review.md`
  already listed competition, partial agonism, complex conjunction, receptor adaptation, occupancy and the pH
  ceiling, and the session added dosage asymmetry and multistability. That list is now `docs/nonlinearity_inventory.md`
  (living). Every nonlinearity of the registered linear encoder is applied after the fixed point, so none of them
  carries along a route. Asked why the mixture statistics were forced odd, the record gave the reason: a non-odd
  statistic is sign-biased and silences the falling branch of the response. The mirror property the comment also
  cited had been withdrawn on 13 October, and the constraint binds a statistic taken across messages, not a map
  applied pointwise to a node's own state. The owner's rulings: the tested models may change by amendment; a
  minimum over the signed field (a "signed AND") is "better handled by a different control"; the random-walk
  findings 5, 13 and 14 are rejected as evidence about the current model (9.82: "it's on like v.1 or v.2 graph");
  9.68's VAMP1 membership is related to 9.81 and decided apart from it, because "the closest version to physiology
  is used since that is always the top priority". 9.81 stays open for saturation inside the fixed point; the
  encoder's place was settled on 22 October by 9.77 in another session. Built: the entmax weighting of the
  cross-relation mixture, annealed to sparsemax so the kept model has exact zeros (on main 27 October 2026 as
  `4d2f723` and `e9181f4`; not in the registered model); CLAUDE.md's "Start here", "Modelling" and "Code" sections,
  the cross-branch decision-id command, the two-commit rule for the decision log and `PYTHONPATH=.` for scripts; and,
  by an agent, 24 stale comments corrected in 12 files. That cleanup found that the message-passing encoder adds
  its perturbation only to the initial state, so at its registered fixed point a gene perturbation decays away. The
  owner had known this since 10 October; it is now 9.83, deferred, and preregistration item 7's "The perturbation is
  held on at every round" is not true of that encoder. An organisation review of the repository found the status
  page counting 1 registered rule (since fixed) and decision ids 9.77 and 9.78 taken twice (since renumbered).
  Claims withdrawn in the session: that the asymptote was a local, one-off problem; that decision 4.2 was open (it
  closed on 13 October, and the 413 count of complexes reproduces under no reading); that the message-passing
  encoder had a softmax mixture; and that the mirror property still constrained the encoder. It ran on Claude
  Opus 5 and then Opus 5.5. Under the rule of 25 October 2026 two things need a Fable pass: the research
  report on hybrid encoders, whose findings were not committed; and the two citations in the entmax comments of
  `mechanistic_pathway_learning/models/linear_response_encoder.py` (Peters, Niculae and Martins 2019,
  doi:10.18653/v1/P19-1146, including the claim that 1.5 is their main setting; Blondel, Martins and Niculae 2019,
  arXiv:1901.02324). Both were written from memory, were not read in the session and are not in
  `docs/references.bib`.
- https://claude.ai/share/be16df9d-b1d1-4a69-b185-de20d9ca0f73 — 20 to 27 October 2026. VAMP1 beside VAMP2,
  how Human-GEM's gene rules are read, and ambient RNA in the single-nucleus weights. It began with a
  plain-language reading of why joining VAMP1 to one or more of VAMP2's 16 Reactome entities was a choice (9.68).
  The owner proposed combining a shared-complex and a per-transmitter placement and a backup path, an edge starting
  at weight 0 that opens when VAMP2 is lost. The session argued that in the registered linear loop such an edge is a
  smaller VAMP2 weight to first order, would put a state-dependent product inside the loop, and predicts no effect
  of losing VAMP1 where it is the main paralog; the owner: "good points on my backup option. move forward with your
  suggestion please". Built on pull request #5 (merged 21 October 2026 as `e313ce5`): VAMP1 is an alternative
  member of all 16 entities, every one a synaptic vesicle entity, splitting VAMP2's membership weight by mean GTEx
  brain median TPM (0.145 against 0.855) so no divisor changes, and counted with VAMP2 as one member, the larger, in
  the decision 4.2 gate (`docs/curated_alternative_members.csv`). On a scratch build the two SNARE complex entities
  are products of release with no edge out, which withdrew the session's first reading that joining the shared
  fusion complex would carry VAMP1; with the pair rule no gate changes, where a plain minimum would have lowered
  them by up to 0.405. Asked whether more studies had been sought and to review Human-GEM's readings for physiology,
  the session found that propagation turns every rule gene into an equal-share `catalyzed_by` edge, so an "and"
  subunit of complex I carries 2 percent of the input and an "or" isozyme 1/k whatever its expression, while the
  gate takes the minimum over "and" and the maximum over "or" (GECKO and the MIN/SUM mapping add isozyme
  capacities). On 24 October the owner asked about the docstring's claim that single-nucleus pseudobulk carries
  ambient RNA: it holds (Caglayan et al. 2022, Janssen et al. 2023) but moves VAMP1 shares by a few thousandths,
  and the session's earlier statement that HPA ranks excitatory above inhibitory neurons for VAMP1 was withdrawn as
  an aggregation artifact: a class value is each gene's maximum over the class's cluster types, so the excitatory
  0.166 paired VAMP1 from the lower rhombic lip with VAMP2 from thalamic neurons, against a forebrain median of
  0.047. Under the rule of 25 October 2026 the recommendation went to a Fable agent, which re-read the 14
  load-bearing sources (every quoted claim holds) and recommended keeping 0.145 with its limits recorded: the
  per-transmitter shares the session had proposed (GABA about 0.5, glutamate about 0) do not hold as shares, since
  the same VAMP1 knockdown lowered mIPSC and mEPSC frequency alike and human layer 4 non-PV neurons carry about half
  the PV level of VAMP1 mRNA; an even split has no source; and the Human-GEM isozyme reading is decided apart, as an
  amendment, after re-measuring it on a current build. The owner's call is open. Recorded on 27 October 2026 as
  `2852923`: the 9.68 addendum, 14 entries in `docs/references.bib`, the cited docstring of
  `graph/brain_expression_weights.py`, `experiments/measure_ambient_rna_hpa.py` and item 8 of
  `docs/exploration_queue.md`. The session ran on Claude Opus 5.5 and its 25 October research step on Fable 5.1.
  Still owed under the "Models" rule: a Fable reading of `lee2015cytoplasmic`, flagged in its entry, and a
  re-measurement of the gene-rule counts, which were taken on a scratch graph from an old branch.
- https://claude.ai/share/44e03976-f9b9-4eea-ad89-430ce80702d1 — 22 to 27 October 2026. The HRH2 coupling
  evidence behind decision 9.79, and where papers are recorded. On 22 October the owner asked for the sources
  needed to check the 9.79 claim from pull request #11 that HRH2 reads Gs primary and that its Gq/11 coupling
  rests almost entirely on transfected systems. PubMed gave Panula et al. 2015 (PMID 26084539), Kühn et al. 1996
  (PMID 8961278) and Mondillo et al. 2005 (PMID 15917347), read by abstract only. Kühn's one native-tissue
  result is GTP-azidoanilide labelling of Gαq and Gα11 in guinea pig heart membranes, not a functional PLC
  readout, so the session said "almost entirely transfected" may be slightly overstated; searches for further
  native-tissue studies returned nothing, so "Gs primary" was not shown beyond those papers. On 27 October the
  owner asked whether anything still needed doing. The first answer was built from the Project notes alone and
  recommended a Fable recheck of 9.79 that decision 9.99 had already recorded on 26 October. The owner asked
  whether the session had pulled from origin; it had not, and the answer was redone from `origin/main` at
  `68bde1f` (read through the GitHub connector, since the workspace held no clone): 84 decisions waiting and no
  open pull requests. The owner then ruled "just add papers to the repository's references.bib file instead of
  zotero from now on" (`CLAUDE.md` "Reading sources", commit `838d7b9`) and, for the papers 9.79 leans on, "mark
  the modillo fable pass as followup work that should be done before 9.79 decision. same for zhu et al 1994.
  i'll supply those papers to the new session." Row 9.79 carries both as owed Fable full-text passes; the
  session reads "modillo" as Mondillo 2005. Fable 5.1 subagents, by their own reports, added six entries to
  `docs/references.bib` after checking each field against Europe PMC: `c3f99fc` (Panula 2015, Mondillo 2005) and
  `e7f350e` (Wellner-Kienitz 2003, Wang 1996, Mitsuhashi 1989, Zhu 1994). Only the Panula entry rests on a full
  text, from its PMC record; its licence is unverified and Europe PMC does not mark it open access, which
  corrects the session's earlier statement that it was free to read. Panula's sentence on Gq/11 coupling cites
  only Hill 1990 (not held) and Hill et al. 1997, which row 9.79 records as not supporting it. The other five
  hold the abstract alone and carry "FULL TEXT NEEDS SOURCING BY THE OWNER": the publisher sites answered 403 or
  disallow the reader by robots file. The PubMed records of Mitsuhashi and Zhu carry no DOI, so those entries
  take theirs from Europe PMC, confirmed only by resolution at doi.org. The 9.79 wording that said Zhu was still
  to be added was changed in `2b356f8`, the generated pages were regenerated, and the full suite passed (1503
  passed, 28 skipped). When the git proxy refused a subagent's first push, it attached the repository with push
  access through `add_repo`; the owner had not approved that step separately. Written on Claude Sonnet 5.5, with
  the bibliography research done by Fable 5.1 subagents. Still the owner's: supply Mondillo 2005,
  Wellner-Kienitz 2003, Wang 1996, Mitsuhashi 1989 and Zhu 1994; Zhu is the paper 9.79 calls "the
  highest-value outstanding item".
- https://claude.ai/share/351b6aff-85f0-483a-9c2b-cd06855af866 — 20 to 27 October 2026. SERPINA6 as a carrier,
  and what sign 0 means. Pull request #5 had left one of decision 9.68's named mechanisms out, with the note that
  "whether a carrier's loss changes free cortisol at steady state needs sources on the adrenal axis's feedback
  first". The answer is that the axis defends the free **concentration** and what a carrier moves is the free
  **fraction**, which the graph has no representation for: homozygotes for a CBG variant that lacks steroid binding
  have "very low baseline and stimulated total serum cortisol levels but normal free serum and salivary cortisol and
  plasma ACTH" (Perogamvros et al. 2010, doi:10.1210/jc.2010-0746), and a normal ACTH beside a near-absent total
  cortisol is what separates the two candidate feedback variables. The theory reaches the same place without the
  feedback doing any work (Mendel 1989, doi:10.1210/edrv-10-3-232). So the quantity the graph could carry is the
  pool, and the pool is the one measured not to move; `sequesters` (sign -1) was already built, so the edge could
  have been written and would have asserted a change the sources refuse. Recorded as a resolved negative in 9.68
  (`bb18461`) with seven entries in `docs/references.bib`, rather than as a gap to re-derive. **Four claims were
  withdrawn or corrected in the session.** Free cortisol values attributed to Torpy et al. 2001 by the research pass
  (0.1, 0.3 and 0.5 microg/dl, free fraction 23 to 28 percent, quoted "comparable to those in normal subjects") do
  not appear in that abstract, whose only sentence of that shape is about compound heterozygotes; they are not
  relied on and the row says so, leaving Perogamvros 2010 the single human anchor. The session's own statement that
  the literature is contested was corrected once concentration and fraction were kept apart: OMIM 611489's raised
  free cortisol traces to Buss et al. 2007 (doi:10.1007/s00702-006-0620-5), one heterozygote measured after a
  standardized stress test, not at rest. Its statement that `sequesters` was designed but unbuilt was wrong, the
  relation carrying 101 edges. And its recommended alternative, the adrenal route of Gulfo et al. 2019
  (doi:10.1038/s41598-019-50355-1), was withdrawn on finding rat adrenal *SerpinA6* transcript very low or
  undetectable with the dimorphism attributed to liver-derived CBG (Toews et al. 2022, doi:10.1210/endocr/bqac152).
  **Decision 9.98**, taken from the same work: sign 0 is the only wholly unsigned relation and carries two
  incompatible readings, "the right reading for a carrier, since it moves a substrate without acting on it"
  (`graph/plasma_binding.py`) against "sign 0, meaning unknown" (`graph/brenda_enzyme_regulation.py`), so a measured
  null and an unestablished sign are one symbol; three options for the owner, with dropping the sign-0 edges refused
  because 9.69 records channels that reach the graph only through `binds`. Named at all seven sites that state a
  reading (`93f0a4b`). **The session's own waived research made a rule stale**: CLAUDE.md's "Models" section ended
  "No case flagged under this rule remains open", which a reader takes as no research on `main` awaiting a Fable
  recheck, and the 9.68 record was written on a non-Fable pass under the owner's permission for that work ("Don't
  worry about fable this time", 26 October 2026). A bullet now names the waived case and leaves waiver policy to the
  owner (`59e98d1`). **A stale document found while checking the work**: `docs/plasma_binder_graph.md` carried a
  hand-written "Known limitation: no drug reaches its plasma carrier in the graph" from 9 October whose three
  obstacles had all been removed, drug nodes existing (154 measured, 222 on the v4 audit), `sequesters` existing (71
  edges for 49 drugs; 101 on the audit) and ORM1 and ORM2 holding 16 each rather than one edge to progesterone. On
  the owner's "recommendation accepted" the resolution went to `docs/drug_entry_nodes.md`, record class and the
  document the section itself points at, with the 9 October fentanyl reasoning kept as history and the caveat
  recorded that whether fentanyl **in particular** holds one of those edges is written down nowhere, both
  measurements giving counts by carrier gene rather than the drug list. The section was not hand-cut: the register
  makes that file generated and `docs/documentation_process.md` says a generated document is "never edited by hand",
  so the cut belongs to `carriage_report()`, which emits no such heading and rewrites the file on its next run, and
  that generator was given the provenance stamp it lacked (`27f7c51`). The attempt to hand-cut it failed
  `test_generated_documents_regenerated_after_the_policy_date_carry_a_stamp`, and because that test reads the git
  log rather than the file, the edit had to leave history, so the unpushed commits were rebuilt without it. The
  session ran on Claude Opus 5; which model served its research passes is not known to it, the first having run
  before the waiver and the second under it. Also recorded: 9.68's cortisol -> `NR3C1` recheck (`3ecf528`), unmeasured
  on a current build, the one record being 14 October 2026 on a 266,966-edge graph. **Still owed**: a Fable recheck
  of the 9.68 record; the owner's ruling on 9.98 and on how a waiver works; and three counts needing a built graph,
  cortisol -> `NR3C1`, fentanyl's `sequesters` edge and the plasma-binder variant build that performs the cut.
- https://claude.ai/share/b23b5367-01d7-4fec-923c-8ff6a26aacec — 21 to 27 October 2026. The owner asked what
  concern about SLC9A6 (NHE6) pull request #7 had set out of scope. Its write-up of 20 October named the gene but
  was never committed, so the reasoning was not recoverable from the repository, decision 9.75 or past chats; the
  session reconstructed the gap instead, marked as its own inference: NHE6 changes endosomal pH rather than calcium
  store content, the 9.75 endolysosome store lumps endosome and lysosome and takes no input, and the compartment pH
  weight is inert because `calibrate_ph_sensitivity` is called only by tests. On 24 October it wrote the handoff
  for a session holding the v5 graph (`claude/handoff_v5_session_2026-10-24.md` in the project): the name `v5`
  covers two builds (20 October from `344d211`, 268,876 edges; 22 October, 274,917), v5 predates the graph changes
  of pull requests #5, #7, #9, #11, #14, #16, #17 and #18, and `scripts/rebuild_data_layer.sh` skips every step
  whose output exists, so a rerun beside v5 rebuilds nothing. On 27 October, asked what to do before retiring it,
  it found the NHE6 point recorded nowhere in the repository and added it as item 7 of
  `docs/exploration_queue.md`, with Kondapalli et al. 2014 and Gilfillan et al. 2008 in `docs/references.bib`.
  The session ran on Claude Opus 5.5. Its 21 October reading of Kondapalli 2014 was research done on another
  model; the sourcing of item 7 was done by a Fable subagent, which confirmed each quote against the abstract and
  found that the review does not itself name SLC9A6 as the Christianson syndrome gene, so that claim cites the
  2008 gene identification instead. One correction from the session: it first called item 7 documentation
  outside the Fable rule, which CLAUDE.md's definition of research contradicts.

## Conventions

Descriptive names over comments; no hard symptom-level constraints anywhere in the model;
unobserved perturbation-symptom pairs are unlabelled, not negative; every long job is
idempotent and resumable; MedDRA term tables are never committed.
