# Reducing the module-support parameter count: options and a recommendation

Research pass of 7 November 2026, on Fable (no fallback occurred). The repository was read at `main`
3f00e8c (7 November 2026); nothing was edited, committed or pushed. **This record rules nothing**; every choice below is
the owner's. Counts marked "measured" were computed in this pass on the v5 drug graph
`data/processed/graph_full_neuronal_split_binders_drugs_v5` (built 5 November 2026; 49,834 nodes, 275,006 edges), today;
numbers quoted from `docs/open_decisions.md` 9.90 are from the v5 label tables of 22 October 2026 and are marked so.
No text addressed to an AI assistant was met on any page read.

## 1. The current count, recomputed from the code

Shapes read from `mechanistic_pathway_learning/models/noisy_or_pathway_module_model.py` and
`mechanistic_pathway_learning/models/linear_response_encoder.py` under the registered configuration
`confirmatory_v2_linear_response_noisy_or` (`experiments/run_main_model_batch.py`: `LINEAR_RESPONSE_ENCODER_V2` with the
cell-class weights, `NOISY_OR_SETTINGS`, the trainer's defaults `--num-modules 8`, `--node-state-dim 32`,
`--channels-per-cell-class 1`, `--cross-relation-aggregator mean`, `--node-features typed`). Sizes on v5: N = 49,834
nodes; M = 8 modules; D = 32; C = 17 propagation channels (the 17 cell classes of
`data/processed/cell_class_weights/full_neuronal_split_drugs_v5_cell_class_weights.parquet`, one channel each);
S = 39 symptoms (9.90's count on the v5 label table); F = 162 node-feature columns (24 structural: 8 node types,
10 compartments, 6 flags, `ExperimentData.structural_node_features`; plus the 138 descriptor columns of
`data/processed/node_descriptors/full_neuronal_split_drugs_v5_descriptors_brain_expression.parquet`); R = 28 relation
gain rows (24 relation types in `edges.parquet` plus the derived relations the encoder adds; the 28 is the study
sheet's count and was not re-derived from the encoder here).

| Learned tensor | Shape | Count |
|---|---|---|
| Module supports, `HardConcreteNodeGate.log_alpha` | M × N = 8 × 49,834 | **398,672** |
| Encoder output gate, `nn.Linear(F, D)` | 162 × 32 + 32 | 5,216 |
| Module-symptom links, `module_symptom_link_logit` | 2 × M × S = 2 × 8 × 39 | 624 |
| Channel expansion | C × D = 17 × 32 | 544 |
| Relation gains, `gain_logit` | R × C = 28 × 17 | 476 |
| Module readout weight and bias | M × D + M | 264 |
| Symptom leaks | 2 × S | 78 |
| Entry gains (one entry relation, `targets`) | 1 × C | 17 |
| Input weights (positive form) | C | 17 |
| **Total** | | **405,908** |

The supports are 98.2 per cent of the learned parameters. The study sheet's diagram "Almost every parameter is module
membership" (widget 15448121-6479, read today) gives 405,140 and 98.4 per cent; the difference is that it counts the
output gate on the 138 descriptor columns alone (4,448) where the code's `output_gate` reads all 162 columns (5,216).
Not counted on either side: the pH sensitivity and width (2 per compartment with a proton node; `--compartment-ph` is
not in `LINEAR_RESPONSE_ENCODER_V2`) and the calcium-store sensitivities, which exist only when their inputs are given.

Against the labels (9.90, v5 tables of 22 October 2026): 4,446 labelled positives, 87,042 unlabelled pairs and 70
evidenced negatives, 91,558 counted pairs over 2,447 perturbations. So there are **90 support gates per positive label**
and 4.4 per counted pair. The 8 modules of the registered run each hold one gate per node, including the 7,445 nodes no
perturbation's field reaches at all (measured: the union of forward cones from the 2,797 seed nodes of the v5 evidence
records covers 42,389 of 49,834 nodes). A gate the field never reaches receives only the sparsity gradient and closes
(the docstring of `time_scale_parameter_groups`), which also means that a node first reached by a held-out
perturbation's cone cannot be in any support at test time: under the per-node parameterisation, membership of such a
node is unlearnable by construction. This is the identifiability fact the options below are weighed against.

## 2. The options

Sizes used throughout (all measured today on v5 unless marked): P = number of named sets; the derived set membership of
section 2(a) covers 29,425 of 49,834 nodes.

| Option | How it works here | Support parameters on v5 | Physiology encoded / given up | Identifiability against 4,446 positives | Build cost | Registered model changed | Risk |
|---|---|---|---|---|---|---|---|
| **(a) supports over named pathway sets** | z = clamp(G B, 0, 1): G is an M × P hard-concrete gate (the existing `HardConcreteNodeGate` with N replaced by P), B a fixed P × N membership matrix built from the data layer; the curated modules are sets with an anchor prior | P on v5: 148 Human-GEM subsystems (138 with a gene) + 15 Reactome pathways (kept per pathway instead of the one subsystem "Reactome") + 16 curated modules = 179 → **8 × 179 = 1,432**; with GO biological-process terms for the signalling layer, P of a few hundred to a few thousand → 10^3 to 10^4 | A module is a union of named pathways: physiology's own units, the nosology aim's "modules as dimensions" (9.64 (A)) read as named sets from the start. Given up: a module that uses part of a set, and membership of the 20,409 nodes no set covers (9,994 genes, 9,904 proteins of the signalling and transcription layers, 230 drugs) until gene-set membership for them is built | 0.3 gates per positive; a node reached only by a held-out perturbation inherits its set's membership | Membership matrix (subsystem, Ensembl ids of the gene-reaction rules, `encodes`, substrate and product edges, Reactome pathway id retained in `reactome_import.py`, GO terms already fetched under CC BY 4.0, `docs/data_sources.md` row 57; Reactome CC0, row 61); head change of some dozens of lines; description-length unit; tests; naming rule becomes trivial. Days | Yes: preregistration 5.3 "one hard concrete gate per node", design 5.5's expected active nodes, the registered defaults; a new rule would be registered | Set boundaries are inherited from curators (circularity in the sense of 9.63 for pathways rather than nosology); coarse sets (Transport reactions, 4,037 reactions) act as hubs |
| **(b) supports restricted to a candidate set** | the M × N gate masked to a fixed node set; everything else as now | field-reachable union: 42,389 → 339,112; gene, protein and protein-entity nodes: 27,214 → 217,712; field-reachable gene/protein nodes: 20,563 → 164,504; brain-expressed genes: 10,399 → 83,192; the 16 curated modules' 103 anchor genes (205 gene and protein nodes) with their 1-hop undirected neighbourhood: 1,480 → **11,840**; 2-hop: 20,229 → 161,832 | Anchors + 1-hop encodes "a module is built around a curated pathway and its immediate interactors"; the other restrictions are numerical (reachability, node type) and the brain-expression one contradicts the peripheral cell classes the encoder carries (thyroid, pancreatic islet, pituitary, pineal) | 2.7 gates per positive for anchors + 1-hop; otherwise 19 to 76 | A mask: hours | Yes for any mask, the same clauses as (a) | A module cannot leave the anchors' neighbourhood, so discovery is confined to the curated list's vicinity; the three large restrictions reduce nothing of the order asked |
| **(c) amortised supports, z = f(node descriptors)** | k_n = W x_n from the F fixed features, q_m a module query, z[m,n] = σ(q_m · k_n) or a sparsemax or entmax over n (section 3) | linear map z = σ(w_m · x_n): M × F = 8 × 162 = 1,296 (+ 8 biases); query-key with d = 8: 1,360; d = 16: **2,720**; d = 32: 5,440; small MLP F → 32 → M: 5,440 | A module is "every node with these properties"; physiological only when the properties are physiological annotations (set membership, cell-class expression, compartment); with the 64 protein `rrr` columns (ESM reductions) it is a learned similarity, not a pathway. Nodes with identical descriptors have identical membership | 0.6 gates per positive at d = 16; a held-out node gets a support from its descriptors | Head change only, descriptors exist: a day; d is a numerical choice needing a stated justification | Yes, the same clauses | Supports that follow descriptor blocks (all unreviewed proteins in or out together); 314 of 400 pilot supports were already "mixed" (`docs/module_names.md`) and a descriptor rule does not of itself make them nameable |
| **(d) hierarchical or smoothed supports** | one gate per (module, node type × compartment): M × 8 × 10 ≤ 640; or z = σ(U a_m) with U the first k eigenvectors of the symmetrised normalised graph Laplacian: M × k, k = 64 → 512 | Type × compartment is coarser than any pathway ("all cytosolic metabolites"); Laplacian smoothing encodes "membership varies smoothly along the graph", which pathways do (they are connected) but the eigenbasis mixes every pathway into every basis function, so no module is a set | 0.1 per positive | Eigendecomposition of a 50k-node graph (scipy, sparse, feasible): hours | Yes | Not readable as pathways; Li and Li 2008 keep an L1 term precisely because smoothness alone selects nothing |
| **(e) supports read from the field** | no learned z: module m reads the field through r_m alone, or z[m,n] = g(field_n) | **0** | A module becomes whatever the perturbation reaches, so it is the perturbation's own cone and has no identity across perturbations; the nosology needs modules that are fixed objects | the readout r_m and links alone, 264 + 702 | Trivial | Yes; it is the uniform-weights baseline of Wiegreffe and Pinter in this setting and worth running as a control | It removes the object the experiment is about |
| **(f) fewer modules** | `--num-modules 4` | 4 × 49,834 = 199,336 | None gained; the description-length criterion (5.5) already chooses K | 45 per positive | None | `--num-modules` is a default, a candidate of the MDL comparison | Not an order-of-magnitude lever |
| **(g) literature forms** | see section 4 | | | | | | |

## 3. The owner's addition: an interpretable attention layer

The owner's constraint: "It has to stay interpretable for the future nosology aim".

**(1) The design and its count.** Each module m has a learned query q_m ∈ R^d; each node n a key k_n = W x_n with
W ∈ R^{d×F} shared by every node and x_n the fixed node features. The membership is either
support[m, n] = sparsemax_n(q_m · k_n / √d) or α-entmax_n(·), one simplex per module, or support[m, n] = σ(q_m · k_n)
when a node may belong to several modules. Parameters: M·d + d·F (+ d biases). On v5 with F = 162: d = 8 gives
64 + 1,296 = 1,360; d = 16 gives 128 + 2,592 = **2,720**; d = 32 gives 256 + 5,184 = 5,440; against 8 × 49,834 =
398,672, a reduction of 73 to 293 times. With the 24 structural columns dropped (F = 138) the counts are 1,168, 2,336
and 4,672. If pathway-set memberships are added to x_n as binary columns (section 2(a)'s P ≈ 179 sets), F = 341 and
d = 16 gives 5,584. Note on the normalised forms: a sparsemax or entmax support sums to 1 over 49,834 nodes, so with
the registered `--pooling sum` the module reads a weighted mean of the field, which is the `mean` pooling the head's
docstring describes; on the difference field that is well defined (unreached nodes are zero) but the activation scale
changes with the support size, and the readout bias of −3 (`--module-bias-init`) would be retuned. The sigmoid form
keeps the present semantics (a gate in [0, 1] per node, multi-membership, sum pooling).

**(2) Relation to option (c).** It is a special case of z = f(node descriptors): f is the bilinear map x ↦ σ(q_mᵀ W x)
(or its normalised version), that is a rank-d factorisation of the M × F linear map w_m = Wᵀ q_m. Against the plain
linear map (M × F = 1,296 parameters) attention adds nothing in expressiveness when d ≥ M and loses expressiveness when
d < M (the eight w_m are then constrained to a d-dimensional subspace); it saves parameters only when d < M·F/(M+F),
that is d < 7.6 here, which is below M. Against a small MLP (F → h → M) it is less expressive and about as large at
h = d. What it adds is the normalisation across nodes (sparsemax or entmax), which the other two do not have, and a
readable structure: q_m is one vector per module and k_n one vector per node, so a module is a point in the same
d-space as the nodes and membership is a dot product, which a reader can plot. What it costs is a scale (√d, the
temperature) and the choice of d, both numerical.

**(3) Interpretability for nosology.** The debate: Jain and Wallace 2019 (NAACL, peer reviewed; DOI
10.18653/v1/N19-1357; abstract read on the ACL Anthology page with `experiments/read_public_page.py` today, SHA-256
4f01e740…) report that "models equipped with attention provide a distribution over attended-to input units, and this
is often presented (at least implicitly) as communicating the relative importance of inputs", and find "that they
largely do not. For example, learned attention weights are frequently uncorrelated with gradient-based measures of
feature importance, and one can identify very different attention distributions that nonetheless yield equivalent
predictions", concluding that "standard attention modules do not provide meaningful explanations and should not be
treated as though they do." Wiegreffe and Pinter 2019 (EMNLP-IJCNLP, peer reviewed; DOI 10.18653/v1/D19-1002; SHA-256
1feadf4b…) reply that "such a claim depends on one's definition of explanation, and that testing it needs to take into
account all elements of the model", and "propose four alternative tests to determine when/whether attention can be
used as explanation: a simple uniform-weights baseline; a variance calibration based on multiple random seed runs; a
diagnostic framework using frozen weights from pretrained models; and an end-to-end adversarial attention training
protocol", finding "that even when reliable adversarial distributions can be found, they don't perform well on the
simple diagnostic, indicating that prior work does not disprove the usefulness of attention mechanisms for
explainability."

Does the critique apply here? Half of it. The first finding (attention uncorrelated with gradient importance) does
not: here the weights are the memberships the model uses, not a post-hoc account; a node's contribution to module m is
exactly z[m,n] · r_m · x_n, so a zero membership is a zero contribution by construction, and the contribution is what
`NoisyOrOutput.module_contribution` already reads. The second finding (different distributions, same predictions)
applies in full and is the project's own non-identifiability stated in design section 5.5 (permutation, split, merge),
plus a new face: when the field co-varies along a pathway, a support on any subset of the co-varying nodes gives the
same activation, so the fitted support is one of many. Nothing in the architecture removes that; stability selection
across seeds and folds does, which is Wiegreffe and Pinter's "variance calibration based on multiple random seed runs",
and their "uniform-weights baseline" is option (e) above, which should be run as the control. So attention is no less
interpretable than the present gates, and no more: in both, a membership is trustworthy only as a consensus support.

What a reader can read off q_m. When x_n holds named annotations (pathway-set membership, cell-class and region
expression, compartment, node type), q_m is a weight vector over named features and the module is a rule: "nodes of
the dopamine and serotonin subsystems expressed in medium spiny and dopaminergic neurons", which can be stated,
compared across seeds and matched to a curated module without looking at the support at all. When x_n is a learned
embedding (the 64 protein `rrr` columns, reduced ESM embeddings, 40 per cent of the present F), the components of q_m
have no names; the module is then readable only through its support, as today, and the reduction in parameters has
bought identifiability but no new interpretability. The current descriptor table is half of each: 10 metabolite
properties, 8 EC classes, 2 flags and 54 expression columns are named; the 64 protein columns are not.

**(4) Physiology cost and the hybrid.** Nodes with identical descriptors get identical memberships. On v5 that is not
hypothetical: the descriptor blocks are zero outside a node's type, proteins without ESM descriptors share one row, and
genes share rows within an expression pattern, so whole blocks enter or leave a module together, and no node-specific
fact (this transporter and not its paralog) can be learned. The hybrid z[m,n] = σ(q_m · k_n + r[m,n]) with r a sparse
per-node residual repairs that: with the project's own L0 machinery (a hard-concrete gate on each r, Louizos, Welling
and Kingma 2018, already `ref26_welling2018`) the expected number of nonzero residuals is what the description length
counts, and with a spike-and-slab prior the same in Bayesian form (M·N slab means plus M·N spike probabilities,
797,344 numbers; an L1 residual is M·N = 398,672). **The nominal count of the hybrid is therefore back at M·N plus the
attention's 2,720**; what falls is the number of residuals that stay nonzero, which is a property of the fit and the
penalty, not of the parameterisation. The nominal count falls only when r is confined to a candidate set, which is
option (b) again: anchors + 1-hop gives 2,720 + 11,840 = 14,560; field-reachable gene and protein nodes 2,720 +
164,504. This is the honest statement the owner should see: attention alone reaches 10^3; attention with a free
per-node residual is 10^5 nominal and 10^3 to 10^4 effective; attention with a candidate-set residual is 10^4.

**(5) Sparsity.** The project's entmax is the cross-relation mixture's weighting (`CrossRelationAggregator`,
`--mixture-weighting entmax` under `--cross-relation-aggregator softmax_mixture`; the registered default aggregator is
`mean`), which weighs five statistics per node type and channel: five-way vectors, not 50,000-way. Over 49,834 nodes
the questions are exact zeros and their stability. Exact zeros: sparsemax (Martins and Astudillo 2016, ICML, peer
reviewed; PMLR page read today, SHA-256 9d19a294…) is "a new activation function similar to the traditional softmax,
but able to output sparse probabilities", and α-entmax (Peters, Niculae and Martins 2019, ACL, peer reviewed; DOI
10.18653/v1/P19-1146; SHA-256 600ad26e…) "includes softmax and sparsemax as particular cases, and is sparse for any
α > 1", with "fast algorithms to evaluate these transformations and their gradients, which scale well for large
vocabulary sizes"; a sort of 50k scores per module per step is cheap. Stability, from the definition rather than a
source (this pass's own reading): sparsemax is the Euclidean projection onto the simplex, so a coordinate below the
threshold τ has exactly zero output and, since the Jacobian is zero off the support, receives no gradient from the
loss on its own score; a node leaves the support and returns only when τ falls because the in-support scores fall.
Under a per-node free score that is the dead-gate problem; under the amortised score q_m · W x_n it is not, because
W and q_m move with every in-support node and carry the excluded nodes' scores with them. Two consequences: the
support set changes discontinuously between steps while the output is continuous (sparsemax is piecewise linear), so
the identity of the support is only stable once the in-support scores sit a margin above τ, which an annealed α (the
project's `--mixture-entmax-anneal-epochs` pattern) and a read-out pass at the end (the pattern of 9.62's second pass)
would give; and tied scores enter and leave together, so with block-identical descriptors the support size jumps by
blocks, which the hard-concrete gates never do. The sigmoid form has no exact zeros at all; sparsity there comes from
the L0 residual or a threshold at read-out, as the current gates do (hard support = gate above 0.5).

**(6) Registered values and amendments touched.** The same clauses as section 5: preregistration section 5.3's
"one hard concrete gate per node", design 5.5's description length in expected active nodes (an attention support has
no such count; the unit would become expected nonzero memberships or residuals), the registered trainer defaults
(`--gate-initial-log-alpha`, `--gate-init-noise`, `--gate-learning-rate 0.05`, `--module-bias-init -3`, which belong
to the hard-concrete gate and would be replaced by d, a temperature and a learning rate for q and W), the
`module_health` readings (`median_support_size` on the hard support), the naming rule of
`experiments/analyze_pathway_modules.py` (which gains a second, better route: the rule read off q_m), and the two study
sheet diagrams that depict the head (012dc8f5-8ee9 and 15448121-6479). No entry of `configs/registered_rules.json`
names the support parameterisation today; the amendment would add one.

## 4. What the literature offers (option (g))

Every paper below is peer reviewed (journal articles on PubMed and confirmed against Europe PMC today; conference
papers on the ACL Anthology and PMLR with Crossref records, decision 9.101's reading that programme-committee review is
peer review). Quotes are from the abstracts as read.

- **Fixed named sets as the layer (the form of option (a)).** VEGA (Seninge et al. 2021, Nat Commun, PMID 34584103):
  a sparse variational autoencoder "whose decoder wiring mirrors user-provided gene modules, providing direct
  interpretability to the latent variables". DCell (Ma et al. 2018, Nat Methods, PMID 29505029): "a VNN embedded in the
  hierarchical structure of 2,526 subsystems comprising a eukaryotic cell", where "80% of the importance for growth
  prediction is captured by 484 subsystems (21%)", which is the project's description-length selection applied to sets.
  DrugCell (Kuenzi et al. 2020, Cancer Cell, PMID 33096023): "Tumor genotypes induce states in cellular subsystems that
  are integrated with drug structure to predict response". P-NET (Elmarakeby et al. 2021, Nature, PMID 34552244):
  "biologically informed fully interpretable neural networks enable preclinical discovery and clinical prediction".
  All four fix the membership from a database and learn only the weights on it; none learns a per-node membership.
- **Fixed sets refined, with de novo sets beside them (the form of the hybrid).** expiMap (Lotfollahi et al. 2023,
  Nat Cell Biol, PMID 36732632) learns "to map cells into biologically understandable components representing known
  'gene programs'. The activity of each cell for a gene program is learned while simultaneously refining them and
  learning de novo programs." This is the closest published analogue of "named sets plus a sparse per-node residual
  plus a few free modules", and its refinement is a sparsity penalty on departures from the set, as the hybrid's r is.
- **Knowledge-primed networks (the graph itself as the architecture).** KPNN (Fortelny and Bock 2020, Genome Biol,
  PMID 32746932): "every node has a molecular equivalent, such as a protein or gene, and every edge has a mechanistic
  interpretation"; their learning method stabilises "node weights in the presence of redundancy" and controls "for
  uneven connectivity in biological networks". The encoder here already is this; the lesson for the head is their
  redundancy control, which is the co-varying-pathway non-identifiability of section 3(3).
- **Structured sparsity.** Group lasso (Yuan and Lin 2006, J R Stat Soc B 68:49-67, DOI
  10.1111/j.1467-9868.2005.00532.x, Crossref record read today): "the problem of selecting grouped variables (factors)
  for accurate prediction in regression"; a group penalty on the per-node gates grouped by set gives option (a)'s
  behaviour (a set enters whole) without removing the per-node parameters, so it reduces the effective, not the
  nominal, count. Network-constrained regularisation (Li and Li 2008, Bioinformatics, PMID 18310618): a penalty that
  "penalizes the L(1)-norm of the coefficients but encourages smoothness of the coefficients on the network", "where
  the network is represented as a graph and its corresponding Laplacian matrix"; this is option (d)'s smoothing with
  the L1 term that option (d) alone lacks, and again an effective rather than nominal reduction. L0 through hard
  concrete gates (Louizos et al. 2018, already cited) is what the head has.
- **Topic models over pathways.** No peer-reviewed topic model that places pathway sets as the topics' vocabulary over
  perturbation-symptom data was found by this pass (PubMed and Consensus were not searched exhaustively for it; the
  gene-program models above occupy that niche). Stated as not found, not as absent.

## 5. Recommendation (the pass's, for the owner to rule on)

**First, option (a): supports over named pathway sets, with the curated modules as sets and the sets' union as the
support space.** It is the most physiological parameterisation on the table: physiology states its own units as
pathways, the project's curated modules are already sets of this kind, and the published interpretable models (VEGA,
DCell, DrugCell, P-NET) all take this form. It reaches the target without a numerical justification: 1,432 gates for
179 sets on v5, 10^3 to 10^4 once the signalling layer's 20,000 uncovered gene and protein nodes get set membership from
GO and Reactome gene sets (both licences already verified in `docs/data_sources.md`). It keeps the hard-concrete gate,
the description length (per set, or per member node, the owner's choice), the stability selection and the noisy-OR
unchanged, so the architecture the owner follows changes in one place. It answers the module-naming failure of
`docs/module_names.md` by construction, and it is what 9.64's option (A) needs: dimensions that are named sets.
What it gives up is stated in the table: a module cannot select part of a set, and a node in no set cannot be a
member. Those two are what the second part is for.

**Second, as the per-node escape hatch inside (a), option (b) in its anchor form: a sparse per-node residual confined to
the curated anchors' 1-hop neighbourhood** (1,480 nodes, 11,840 gates; 13,272 with the set gates). The residual is
the existing hard-concrete gate on a candidate set, with the same penalty, so a module can add or drop single nodes
near the physiology the project has curated. This restriction is a numerical choice (identifiability: 2.7 gates per
positive instead of 90) and is recorded as such; the physiological version, a residual over every node, is not used
because the nominal count returns to M·N and a node no training cone reaches cannot be learned anyway (section 1).

**Attention (section 3) is recommended as a robustness arm rather than the tested parameterisation**, run with named
descriptors (set memberships and expression, the protein embeddings dropped), because its reduction is of the same
order (2,720) but its physiology is weaker: a module becomes a property rule, and with the present descriptors 40 per
cent of the features are unnamed embeddings. If the owner prefers it for the tested model, the sigmoid form with
named descriptors is the version closest to physiology among the attention forms, and the decision needs the
justification the modelling rule asks for (why a rule over properties rather than a set of pathways).

Option (e) should be run once as the uniform-weights control whatever is chosen; (d) and (f) are not recommended;
the larger masks of (b) reduce nothing of the order asked.

## 6. Registered and lockbox implications

- The head is specified by preregistration section 5.3 (a sparse support "over graph nodes (one hard concrete gate per
  node)", as `docs/nosology_discovery_options.md` section 1 restates it), the description length of design section 5.5
  (expected active support nodes), and the registered trainer defaults (`V4_SHARED_MODEL`: `--module-bias-init -3`,
  `--gate-init-noise 0.5`, `--gate-learning-rate 0.05`; amendment items 3 and 23 as 9.90 reads them). No rule in
  `configs/registered_rules.json` names the support parameterisation; `tested_models` names the configuration. So any
  of (a) to (e) is an amendment of the tested model: a new registered rule (for example `module_support_space`, with
  `code_location` the head's constructor) asserted by `tests/test_registration_matches_the_code.py`, an `Amends:`
  trailer, and a dated amendment in `docs/preregistration.md`.
- **Outcome-blind**: the task brief states no lockbox is drawn; `docs/confirmatory_runbook.md` says the v5 lockbox is
  drawn only when the Reactome release is pinned (9.111), and `configs/lockbox_v2.json` was drawn on an earlier
  evidence table. No confirmatory run has been scored. The amendment is outcome-blind now and stops being so at the
  draw; the pass did not verify the draw status beyond those two documents, so that is checked at the time.
- Robustness instead of amendment: the registered head runs as is and (a), or attention, is a second arm under
  `robustness_models`, read with intervals and no alpha, the pattern 9.77 set for the message-passing encoder.
- Study sheet (CLAUDE.md "Documents"): diagrams 012dc8f5-8ee9 ("How the modules …") and 15448121-6479 (parameter
  count) depict the head; a ruling that changes the support space makes each a two-version diagram (as built, as
  decided) and re-stamps `configs/study_sheet_diagrams.json`.
- Code comments that state the per-node gate (`noisy_or_pathway_module_model.py` module docstring,
  `module_health.md`'s `median_support_size`, `analyze_pathway_modules.py`'s `module_label`) change in the same commit
  as the code (CLAUDE.md "Code").
- The curated-module hold-out (preregistration: no curated module reaches 10 kept positives) is unaffected by the
  support space, but under (a) a held-out module's set is still a column of B, so the pathway-wise split must mask that
  set's gate or the hold-out leaks the membership (not the labels); to be stated in the amendment.

## 7. Owner decisions needed

New questions (each its own row; related decisions are decided one by one):

1. Whether the support parameterisation changes before the first confirmatory run (an amendment to the tested model)
   or is added as a robustness arm beside the registered head.
2. For option (a): which sets define the support space on v5: Human-GEM subsystems (148), Reactome pathways kept per
   pathway (15 imported), the 16 curated modules, and for the signalling and transcription layers GO biological-process
   terms (at which depth) or Reactome gene sets; and whether a node belongs to a set by catalysis, by substrate or
   product, or both.
3. Whether a per-node residual is allowed, and on which candidate set (the anchors' 1-hop neighbourhood is the pass's
   proposal; the 2-hop set is 20,229 nodes); this is a numerical restriction and carries its justification.
4. The description-length unit under sets: one nat per set, or one per member node (which keeps 5.5's unit and makes a
   large set expensive), and how the residual is costed.
5. For attention: whether the descriptors must be named physiological annotations for q_m to count as interpretable
   (the pass's reading of the owner's constraint), and the values of d and the temperature with their justification.
6. Pooling under a normalised membership (sparsemax or entmax): keep `--pooling sum` with the changed scale, or the
   sigmoid form that keeps the registered semantics.
7. Whether option (e) runs as the uniform-weights control.

Existing ids touched: 9.64 (the modules as the nosology's dimensions: option (a) makes them named sets); 9.90 (h)
(description-length units); 5.2 (power with supports of 1 to 20 genes, which (a) changes to sets); 9.62 (the read-out
pass pattern, if a sparsemax support takes it).

## 8. Sources, with where each was read

- Code and documents of the repository at `main` 3f00e8c (7 November 2026), as named in the text.
- Study sheet (https://claude.ai/artifact/RzVm4LjdeHmzzdSyzJ5j65), widget 15448121-6479, read today through the
  Claude Docs connector.
- PubMed records through the PubMed connector today: PMIDs 34552244, 32746932, 29505029, 33096023, 36732632, 34584103,
  18310618; each confirmed against the Europe PMC REST record (`www.ebi.ac.uk/europepmc/webservices/rest/search`,
  read with `experiments/read_public_page.py` today): titles, author strings, journals, volumes, issues and years agree.
- ACL Anthology pages N19-1357 (SHA-256 4f01e74092248bce…), D19-1002 (1feadf4ba9ce34aa…), P19-1146 (600ad26e95e3b5a7…)
  and the PMLR page v48/martins16 (9d19a294598e48f4…), read with `experiments/read_public_page.py` today; Crossref
  records of the three ACL DOIs and of 10.1111/j.1467-9868.2005.00532.x read the same way. PMLR volume 48 registers no
  DOI; the entry carries the PMLR address instead.
- Unanswered permission requests: none (every page was read through the shell fallback or a connector).

## 9. BibTeX for the new sources

Keys checked against `docs/references.bib` at 3f00e8c: none of the twelve exists there (`ref26_welling2018` and
`meinshausen2010stability` are the existing related entries and are not repeated). Fields of the journal articles are
from the PubMed record and confirmed against Europe PMC; conference fields from the ACL Anthology or PMLR page and the
Crossref record. A field the records did not supply is absent.

```bibtex
@article{elmarakeby2021biologically,
  author  = {Elmarakeby, Haitham A. and Hwang, Justin and Arafeh, Rand and Crowdis, Jett and Gang, Sydney and Liu, David and AlDubayan, Saud H. and Salari, Keyan and Kregel, Steven and Richter, Camden and Arnoff, Taylor E. and Park, Jihye and Hahn, William C. and Van Allen, Eliezer M.},
  title   = {Biologically informed deep neural network for prostate cancer discovery},
  journal = {Nature},
  year    = {2021},
  volume  = {598},
  number  = {7880},
  pages   = {348--352},
  doi     = {10.1038/s41586-021-03922-4},
  pmid    = {34552244},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC8514339). Quoted: "biologically informed fully interpretable neural networks enable preclinical discovery and clinical prediction in prostate cancer". P-NET fixes gene-to-pathway membership from a database and learns the weights on it: the form of the pathway-set support option}
}

@article{fortelny2020knowledge,
  author  = {Fortelny, Nikolaus and Bock, Christoph},
  title   = {Knowledge-primed neural networks enable biologically interpretable deep learning on single-cell sequencing data},
  journal = {Genome Biology},
  year    = {2020},
  volume  = {21},
  number  = {1},
  pages   = {190},
  doi     = {10.1186/s13059-020-02100-5},
  pmid    = {32746932},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC7397672). Quoted: "every node has a molecular equivalent, such as a protein or gene, and every edge has a mechanistic interpretation"; the learning method stabilises "node weights in the presence of redundancy" and controls "for uneven connectivity in biological networks"}
}

@article{ma2018using,
  author  = {Ma, Jianzhu and Yu, Michael Ku and Fong, Samson and Ono, Keiichiro and Sage, Eric and Demchak, Barry and Sharan, Roded and Ideker, Trey},
  title   = {Using deep learning to model the hierarchical structure and function of a cell},
  journal = {Nature Methods},
  year    = {2018},
  volume  = {15},
  number  = {4},
  pages   = {290--298},
  doi     = {10.1038/nmeth.4627},
  pmid    = {29505029},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC5882547). Quoted: "a VNN embedded in the hierarchical structure of 2,526 subsystems comprising a eukaryotic cell"; "80% of the importance for growth prediction is captured by 484 subsystems (21%)". DCell: subsystems from a database as the architecture, importance concentrated on a fifth of them}
}

@article{kuenzi2020predicting,
  author  = {Kuenzi, Brent M. and Park, Jisoo and Fong, Samson H. and Sanchez, Kyle S. and Lee, John and Kreisberg, Jason F. and Ma, Jianzhu and Ideker, Trey},
  title   = {Predicting Drug Response and Synergy Using a Deep Learning Model of Human Cancer Cells},
  journal = {Cancer Cell},
  year    = {2020},
  volume  = {38},
  number  = {5},
  pages   = {672--684.e6},
  doi     = {10.1016/j.ccell.2020.09.014},
  pmid    = {33096023},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC7737474). Quoted: "Tumor genotypes induce states in cellular subsystems that are integrated with drug structure to predict response to therapy". DrugCell: perturbations read through fixed subsystems, the pathway-set form}
}

@article{lotfollahi2023biologically,
  author  = {Lotfollahi, Mohammad and Rybakov, Sergei and Hrovatin, Karin and Hediyeh-Zadeh, Soroor and Talavera-L{\'o}pez, Carlos and Misharin, Alexander V. and Theis, Fabian J.},
  title   = {Biologically informed deep learning to query gene programs in single-cell atlases},
  journal = {Nature Cell Biology},
  year    = {2023},
  volume  = {25},
  number  = {2},
  pages   = {337--350},
  doi     = {10.1038/s41556-022-01072-x},
  pmid    = {36732632},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC9928587). Quoted: expiMap learns "to map cells into biologically understandable components representing known 'gene programs'. The activity of each cell for a gene program is learned while simultaneously refining them and learning de novo programs." The published analogue of named sets with a sparse per-node refinement and free modules beside them}
}

@article{seninge2021vega,
  author  = {Seninge, Lucas and Anastopoulos, Ioannis and Ding, Hongxu and Stuart, Joshua},
  title   = {{VEGA} is an interpretable generative model for inferring biological network activity in single-cell transcriptomics},
  journal = {Nature Communications},
  year    = {2021},
  volume  = {12},
  number  = {1},
  pages   = {5684},
  doi     = {10.1038/s41467-021-26017-0},
  pmid    = {34584103},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC8478947). Quoted: a sparse variational autoencoder "whose decoder wiring mirrors user-provided gene modules, providing direct interpretability to the latent variables"}
}

@article{li2008network,
  author  = {Li, Caiyan and Li, Hongzhe},
  title   = {Network-constrained regularization and variable selection for analysis of genomic data},
  journal = {Bioinformatics},
  year    = {2008},
  volume  = {24},
  number  = {9},
  pages   = {1175--1182},
  doi     = {10.1093/bioinformatics/btn081},
  pmid    = {18310618},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC. Quoted: a penalty that "penalizes the L(1)-norm of the coefficients but encourages smoothness of the coefficients on the network", "where the network is represented as a graph and its corresponding Laplacian matrix". The Laplacian-smoothed support option with the L1 term it needs}
}

@article{yuan2006model,
  author  = {Yuan, Ming and Lin, Yi},
  title   = {Model Selection and Estimation in Regression with Grouped Variables},
  journal = {Journal of the Royal Statistical Society Series B: Statistical Methodology},
  year    = {2006},
  volume  = {68},
  number  = {1},
  pages   = {49--67},
  doi     = {10.1111/j.1467-9868.2005.00532.x},
  note    = {ABSTRACT ONLY HELD, from the Crossref record read with experiments/read_public_page.py on Fable on 7 November 2026 (not indexed by PubMed or Europe PMC). Quoted: "We consider the problem of selecting grouped variables (factors) for accurate prediction in regression." The group lasso: a set-level penalty on per-node gates, an effective rather than nominal reduction}
}

@inproceedings{jain2019attention,
  author    = {Jain, Sarthak and Wallace, Byron C.},
  title     = {Attention is not Explanation},
  booktitle = {Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers)},
  year      = {2019},
  pages     = {3543--3556},
  address   = {Minneapolis, Minnesota},
  publisher = {Association for Computational Linguistics},
  doi       = {10.18653/v1/N19-1357},
  note      = {Peer reviewed (NAACL 2019 programme committee; decision 9.101). ABSTRACT ONLY HELD, read on the ACL Anthology page with experiments/read_public_page.py on Fable on 7 November 2026 (SHA-256 4f01e74092248bce...) and matched to the Crossref record. Quoted: "learned attention weights are frequently uncorrelated with gradient-based measures of feature importance, and one can identify very different attention distributions that nonetheless yield equivalent predictions"; "standard attention modules do not provide meaningful explanations and should not be treated as though they do"}
}

@inproceedings{wiegreffe2019attention,
  author    = {Wiegreffe, Sarah and Pinter, Yuval},
  title     = {Attention is not not Explanation},
  booktitle = {Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)},
  year      = {2019},
  pages     = {11--20},
  address   = {Hong Kong, China},
  publisher = {Association for Computational Linguistics},
  doi       = {10.18653/v1/D19-1002},
  note      = {Peer reviewed (EMNLP-IJCNLP 2019 programme committee; decision 9.101). ABSTRACT ONLY HELD, read on the ACL Anthology page with experiments/read_public_page.py on Fable on 7 November 2026 (SHA-256 1feadf4ba9ce34aa...) and matched to the Crossref record. Quoted: "such a claim depends on one's definition of explanation, and that testing it needs to take into account all elements of the model"; the four tests, "a simple uniform-weights baseline; a variance calibration based on multiple random seed runs; a diagnostic framework using frozen weights from pretrained models; and an end-to-end adversarial attention training protocol"}
}

@inproceedings{peters2019sparse,
  author    = {Peters, Ben and Niculae, Vlad and Martins, Andr{\'e} F. T.},
  title     = {Sparse Sequence-to-Sequence Models},
  booktitle = {Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics},
  year      = {2019},
  pages     = {1504--1519},
  address   = {Florence, Italy},
  publisher = {Association for Computational Linguistics},
  doi       = {10.18653/v1/P19-1146},
  note      = {Peer reviewed (ACL 2019 programme committee; decision 9.101). ABSTRACT ONLY HELD, read on the ACL Anthology page with experiments/read_public_page.py on Fable on 7 November 2026 (SHA-256 600ad26e95e3b5a7...) and matched to the Crossref record. Quoted: the alpha-entmax family "includes softmax and sparsemax as particular cases, and is sparse for any alpha > 1", with "fast algorithms to evaluate these transformations and their gradients, which scale well for large vocabulary sizes". The paper the encoder's DEFAULT_MIXTURE_ENTMAX_EXPONENT comment already names}
}

@inproceedings{martins2016softmax,
  author    = {Martins, Andre and Astudillo, Ramon},
  title     = {From Softmax to Sparsemax: A Sparse Model of Attention and Multi-Label Classification},
  booktitle = {Proceedings of The 33rd International Conference on Machine Learning},
  year      = {2016},
  series    = {Proceedings of Machine Learning Research},
  volume    = {48},
  pages     = {1614--1623},
  address   = {New York, New York, USA},
  publisher = {PMLR},
  url       = {https://proceedings.mlr.press/v48/martins16.html},
  note      = {Peer reviewed (ICML 2016 programme committee; decision 9.101); PMLR volume 48 registers no DOI. ABSTRACT ONLY HELD, read on the PMLR page with experiments/read_public_page.py on Fable on 7 November 2026 (SHA-256 9d19a294598e48f4...). Quoted: "a new activation function similar to the traditional softmax, but able to output sparse probabilities"; "we show how its Jacobian can be efficiently computed". The author names are as the PMLR page prints them, without accents}
}
```

---

## Added 7 November 2026

Committed as a record the same day, unchanged except for the model line. The owner has not ruled on the seven
questions of section 7; the owner's question on readings at each propagation round (exploration queue items 11 and 12,
decision 9.118) was raised as bearing on this choice and is recorded there.
