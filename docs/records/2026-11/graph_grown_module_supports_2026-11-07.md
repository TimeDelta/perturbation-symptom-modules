# Graph-grown module supports (option 2 of decision 9.119): literature, design, counts and compute

Research pass of 7 November 2026, on Fable (no fallback occurred). The repository was read at `main` 16a3c847
(7 November 2026); nothing was edited, committed or pushed. **This record rules nothing**; every choice below is the
owner's. Every count marked "measured" was computed in this pass on the v5 drug graph
`data/processed/graph_full_neuronal_split_binders_drugs_v5` (built 5 November 2026; 49,834 nodes, 275,006 edges) on
7 November 2026, by a script kept with this pass in its working directory, which is not kept. Numbers quoted from
`docs/module_support_reduction_2026-11-07.md` (the earlier pass) are marked so.

Text addressed to an AI assistant was met and not acted on: the PubMed connector's "Important Legal Requirement"
block on every call, and the Consensus search tool's "IMPORTANT INSTRUCTIONS" block. No permission request was left
unanswered: every page was read through a connector or `experiments/read_public_page.py`.

## 0. The option in one paragraph

Today (`mechanistic_pathway_learning/models/noisy_or_pathway_module_model.py`, `HardConcreteNodeGate`) module m owns a
hard-concrete gate z[m, n] on every node and reads the field through `einsum("kn,bnd->bkd")` with sum pooling. Under
option 2 the gate becomes a **seed** gate s[m, n]; the membership is **grown** from the open seeds along the graph by a
kernel K(θ_m) with a learned spread θ_m per module (heat kernel exp(-t_m L), personalised PageRank with restart α_m, or
a k-hop neighbourhood), z_m = g(K(θ_m)ᵀ s_m), and everything downstream (pooling, readout, links, noisy-OR, the
sparsity penalty on the gates, stability selection) stays. The description-length unit counts active seeds (and the
spread). The nominal gate count is still M × N unless the candidate seeds are restricted; the saving is in the
effective count (a module is a handful of seeds and one scale), and in what the parameterisation lets a held-out node
do (section 2.6).

## 1. Literature

Every source below is peer reviewed; journal articles were read from the PubMed record through the PubMed connector
and confirmed against the Europe PMC REST record (`www.ebi.ac.uk/europepmc/webservices/rest/search`, read with
`experiments/read_public_page.py`), all on 7 November 2026; conference papers were read on the conference's own
proceedings page (section 9 says which). Quotes are from the abstract unless the full text is named.

### 1.1 Network propagation for disease genes and modules

- **Random walk with restart (Köhler et al. 2008, Am J Hum Genet, PMID 18371930).** "a global network distance
  measure, random walk analysis, for definition of similarities in protein-protein interaction networks", tested "on
  110 disease-gene families with a total of 783 genes", reaching "an area under the ROC curve of up to 98% on simulated
  linkage intervals". Its closing sentence is the assumption option 2 rests on: the results "add weight to the
  assumption that phenotypically similar diseases are associated with disturbances of subnetworks within the larger
  protein interactome that extend beyond the disease proteins themselves."
- **PRINCE (Vanunu et al. 2010, PLoS Comput Biol, PMID 20090828).** "a global, network-based method for prioritizing
  disease genes and inferring protein complex associations", "based on formulating constraints on the prioritization
  function that relate to its smoothness over the network and usage of prior information"; the motivating observation
  is "that genes causing the same or similar diseases tend to lie close to one another in a network of protein-protein
  or functional interactions". The smoothness constraint is the Laplacian form the earlier pass's option (d) named.
- **HotNet2 (Leiserson et al. 2015, Nat Genet, PMID 25501392; full text read in PMC4444046).** The abstract: "HotNet2,
  a new algorithm to find mutated subnetworks that overcomes the limitations of existing single-gene, pathway and
  network approaches", finding "16 significantly mutated subnetworks" in 3,281 TCGA samples. The method, from the
  full text: "HotNet2 uses a directed heat diffusion model"; "an insulated heat diffusion process that considers both
  the scores on individual genes/proteins as well as the topology of interactions"; "At each time step, nodes in the
  graph pass to and receive heat from their neighbors, but also retain a fraction of their heat, governed by an
  insulating parameter"; "The insulated heat model can also described in terms of a random walk with restart"; and the
  reason for the directed, insulated form: with undirected diffusion "many of the resulting subnetworks are 'hot' stars
  determined by a single high-scoring node and the immediate neighbors of this node", and "HotNet2 returns >80% fewer
  hot stars/spiders than HotNet". The subnetworks are strongly connected components of a thresholded exchanged-heat
  graph, and the threshold is set from permuted data. **What it assumes**: that a perturbed set is connected on the
  interaction network (its output is a connected component by construction), and that hubs must be insulated or they
  dominate. Its spread parameter β is chosen "from the protein-protein interaction network, independent of any gene
  scores"; it is not learned.
- **DIAMOnD (Ghiassian, Menche and Barabási 2015, PLoS Comput Biol, PMID 25853560).** From "a comprehensive corpus of
  70 complex diseases", "We find that disease associated proteins do not reside within locally dense communities and
  instead identify connectivity significance as the most predictive quantity." The algorithm grows a module from known
  disease proteins one node at a time by the significance of its connections to the current module. **What it
  assumes**: "protein interaction networks can be viewed as maps in which diseases can be identified with localized
  perturbation within a certain neighborhood"; its finding against density is a warning to any kernel that rewards
  dense neighbourhoods (a heat kernel does).
- **The review (Cowen et al. 2017, Nat Rev Genet, PMID 28607512; already `ref24_cowen2017` in `docs/references.bib`,
  record verified today: Cowen, Ideker, Raphael and Sharan, vol. 18, pp. 551-562).** "Fundamental to network
  analysis is the concept that genes underlying the same phenotype tend to interact; this principle can be used to
  combine and to amplify signals from individual genes." Random walks, information diffusion and electrical resistance
  "are variations of a unifying mathematical machinery - network propagation".
- **Benchmarks.** Picart-Armada et al. 2019 (PLoS Comput Biol, PMID 31479437): 12 propagation algorithms on 22
  diseases, "diffusion-based prioritisers and machine learning applied to diffusion-based features are suited for drug
  discovery in practice and improve over simpler neighbour-voting methods"; also "Standard cross-validation led to
  over-optimistic performance estimates due to the presence of protein complexes", which bears on the project's
  pathway-wise split (a grown module leaks across a complex). Choobdar et al. 2019 (Nat Methods, PMID 31471613; already
  `choobdar2019assessment`): "Our robust assessment of 75 module identification methods reveals top-performing
  algorithms, which recover complementary trait-associated modules. We find that most of these modules correspond to
  core disease-relevant pathways". Huang et al. 2018 (Cell Syst, already `huang2018systematic`) is the network
  comparison the knowledge-graph review already cites.

### 1.2 The disease-module hypothesis: how well is it supported?

- **Barabási, Gulbahce and Loscalzo 2011 (Nat Rev Genet, PMID 21164525)** state the hypothesis as the programme of
  network medicine: "the identification of disease modules and pathways".
- **Menche et al. 2015 (Science, PMID 25700523; full text read in PMC4435741).** The hypothesis: "the cellular
  components associated with a disease segregate in the same neighborhood of the human interactome". The finding, on
  299 MeSH diseases over 141,296 interactions: "disease genes associated with 226 of the 299 diseases show a
  statistically significant tendency to form disease modules"; but also "their observable modules comprising on
  average only 20% of the respective disease genes", "while ~80% of the disease proteins are disconnected from the
  observable module, these isolates tend to be localized in its network vicinity", and a percolation argument that
  "for diseases with fewer than ~25 genes, the module is too fragmented to be observable in the current interactome".
  Their separation measure s_AB (mean shortest distance between two diseases' proteins against the diseases' own
  diameters) predicts co-expression, symptom similarity and comorbidity, and "about 59% of disease pairs do not share
  genes" yet are related through it.
- **Agrawal, Zitnik and Leskovec 2018 (Pac Symp Biocomput 23:111-122, PMID 29218874; DOI
  10.1142/9789813235533_0011 per Europe PMC; a programme-committee-reviewed conference paper, decision 9.101).** The
  counter-finding, on 519 disease pathways: "90% of pathways do not correspond to single well-connected components in
  the PPI network. Instead, proteins associated with a single disease tend to form many separate connected
  components/regions in the network"; propagation methods' "performance is especially poor on diseases with
  disconnected pathways"; "network connectivity structure alone may not be sufficient for disease pathway discovery."

**Reading for option 2.** The hypothesis is supported in its weak form (members agglomerate: nearest-member distances
are short and GO similarity rises with agglomeration) and not in its strong form (members form one connected
component: Menche's 20 per cent observable, Agrawal's 90 per cent disconnected). A kernel spread from a few seeds
captures the weak form (a node near a seed is a member) and does not need the strong one, provided a module may hold
several seeds in separate regions, which a seed gate over all candidates allows and a single-exemplar form (section
10) does not. All of these findings are on protein-protein interactomes; this project's graph is mechanistic
(reactions, metabolites, complexes, receptor coupling), where a metabolic pathway is connected by construction, so the
assumption is tested directly on v5 in section 2.7.

### 1.3 Neural models that learn a diffusion or seed-based support

- **Graph diffusion convolution (Gasteiger, Weißenberger and Günnemann 2019, NeurIPS 32; proceedings page read
  today).** "Graph diffusion convolution (GDC)" "leverages generalized graph diffusion, examples of which are the heat
  kernel and personalized PageRank. It alleviates the problem of noisy and often arbitrarily defined edges in real
  graphs." The kernel is precomputed and sparsified (top-k or threshold per row) and then used as the adjacency; the
  spread (t or α) is a tuned hyperparameter, not learned.
- **Adaptive diffusion convolution (Zhao, Dong, Ding, Kharlamov and Tang 2021, NeurIPS 34:23321-23333; proceedings
  page read today).** "the neighborhood size in GDC is manually tuned for each graph by conducting grid search over
  the validation set"; ADC learns "the optimal neighborhood size from the data" and "a dedicated propagation
  neighborhood for each GNN layer and each feature channel". This is the published form of "a learned spread per
  module": the heat-kernel t is a trained parameter, with the kernel evaluated by a truncated series.
- **Class-specific learned diffusions (Berberidis, Nikolakopoulos and Giannakis 2019, IEEE Trans Signal Process
  67(5):1307-1321; Crossref record read today; abstract from the Consensus record).** "learning class-specific
  diffusion functions adapted to the underlying network topology", via "'landing probabilities' of class-specific
  random walks", so that the diffusion is "potentially different for each class": a learned polynomial in the walk
  matrix per class, the closest published analogue of one learned kernel per module.
- **Predict-then-propagate (APPNP) and generalised PageRank GNNs** were returned by the Consensus search as the
  personalised-PageRank propagation inside a trained network (Klicpera, Bojchevski and Günnemann; Chien et al.). Both
  are ICLR papers; ICLR registers no DOIs, and every route to their venue refused today: dblp answered a check that
  the visitor is human (HTTP 202) on the search page and the publication API, OpenAlex and Semantic Scholar answered
  HTTP 429, and OpenReview's page and both API hosts answered "Verifying your browser". Under decision 9.101 they are
  named here as not verified and get no BibTeX; the check to repeat is the dblp or OpenReview record.
- Nothing peer reviewed was found that learns **seed gates** jointly with a spread inside a trained network for
  biological modules; HotNet2's seeds are the data (mutation scores) and its spread is fixed, GDC's and ADC's seeds are
  every node (the kernel is the convolution), and Berberidis's seeds are labelled nodes. The combination the option
  proposes (L0 seed gates, a learned spread per module, a noisy-OR readout) is not in the literature read, which is
  stated as not found, not as absent (PubMed and Consensus were searched, not exhaustively).

## 2. Design on this graph

### 2.1 Which graph to spread on (measured 7 November 2026 on v5)

The spread graph is a second object beside the encoder's adjacency, and its relations are a physiological choice:
membership of a pathway is not the same relation as propagation of a perturbation.

- **Direction.** Physiology's pathway membership is not directional: the enzyme, its substrate, its product and the
  gene that encodes it are in one pathway whichever way the signal flows. So the version closest to physiology is
  **undirected**. A directed forward spread makes module m "what lies downstream of its seeds", which is the forward
  cone of a perturbation seeded there, so the module's shape becomes the perturbation's own reach and the option
  drifts toward the earlier pass's option (e). A directed spread also has more dead seeds (section 2.5: 1,260 against
  467). HotNet2 uses direction to insulate hubs, not to define membership.
- **Sign.** Unsigned (|S|). An inhibitor is as much a pathway member as an activator; the sign is read by the
  encoder's field and the module's readout r_m, not by the membership.
- **Relation types.** Pathway-defining relations: `substrate_of`, `product_of`, `catalyzed_by`, `encodes`,
  `member_of`, `cofactor_of` (the metabolic and complex layer); `activates`, `inhibits`, `couples_primary`,
  `couples_secondary`, `g_alpha_regulates_effector`, `regulates_release` (signalling). Three groups need a ruling:
  (i) `regulates_transcription_of` (47,630 edges): a TF's regulon is a biological unit, but SP1 (degree 1,486), MYC
  (1,877), TP53 (1,613), NFKB1 (1,260), JUN (1,235) would merge every pathway they touch into one neighbourhood;
  (ii) `binds` (31,177 edges, sign 0): physical interaction without direction or sign, the relation the disease-module
  literature is built on, but the noisiest layer; (iii) `targets` (1,075 edges, drug to protein): a drug node joins
  its targets to each other in two hops (a drug that binds DRD2 and HTR2A makes dopamine and serotonin receptors
  neighbours), which is pharmacology, not physiology, so the pass excludes `targets` and the 230 drug nodes from the
  spread graph; likewise the single `membrane_potential` node (798 `changes_ion_pool` edges) joins every ion channel.
- **Currency nodes.** `is_currency` marks 271 metabolite nodes (H+ cytosolic degree 2,706, H2O 2,047, ATP 1,221,
  ADP 791, Pi 764). The encoder drops every edge whose source is a currency node (`non_propagating_nodes`,
  `run_main_model.py` line 729). For an undirected spread the analogue is to drop every edge touching one: 228,088
  undirected edges without them against 253,278 with (measured). Effect on a single seed's spread (median over 8
  example protein seeds TH, DRD2, SLC6A4, HTR2A, GAD1, OTC, HPRT1, CYP21A2; nodes above 1 per cent of the row maximum):
  none at heat t = 0.5 (26 and 26) or t = 2 (106 and 106); at t = 8, 1,218 without currency nodes against 1,712 with,
  and 37,410 against 42,623 nodes above 10^-4 of the maximum. So currency nodes matter only at long spreads, where
  they let the spread leak to most of the graph. **Hub proteins are not currency** and are the larger leak: the
  degree-normalised kernels (D^-1/2 A D^-1/2, or the walk D^-1 A) divide a hub's outgoing mass among its neighbours,
  which is the literature's device (HotNet2's insulation, PPR's restart) and is numerical, not physiological (a TF
  with a thousand targets regulates each fully); it is justified here by the measured leak and by HotNet2's "hot star"
  finding, and recorded as such.

### 2.2 Which kernel is closest to physiology, and which is numerical

None of the three kernels is a physiological process: pathway membership is not a diffusion of heat. What physiology
states is that a pathway is a chain of connected steps, so the closest literal reading is **a k-hop neighbourhood of
the seeds along pathway-defining relations**, with the hop count the module's extent. Heat diffusion and PPR are the
smooth, differentiable relaxations of that neighbourhood (a continuous t or α in place of an integer k) that let the
spread be learned by gradient; choosing one of them over the hop count is a numerical choice (differentiability) and
carries that justification. Between the two: PPR's restart has the reading "mass retained near the seed" (HotNet2's
insulation) and its spread ranks nodes by walk proximity; the heat kernel's t is a scale and its tail is wider
(measured, undirected without currency: at the parameters that give a median effective size near 50 to 70 nodes,
heat t = 2 reaches 2,535 nodes above 10^-4 of the maximum, PPR α = 0.15 reaches 8,319). The hard membership a reader
needs (section 5) is a threshold on either, which the hop count gives without a threshold.

A membership in [0, 1] from several seeds: the sum Σ_j s_j K[j, n] exceeds 1 under many seeds, so a form is needed.
The noisy-OR of seeds, z[m, n] = 1 - Π_j (1 - s_j K[j, n]), is the project's own idiom (a node is a member if any
seed's spread reaches it), keeps [0, 1], and reduces to K[j, n] for one seed; a clamp or a learned scale are the
numerical alternatives.

### 2.3 Interaction with the encoder's propagation

The field is already a propagation (signed, in-degree-normalised, the cone divisor, 17 channels), and the module
spread is a second one. The activation reads Σ_n z[m, n] r_m · x_n = Σ_j s_j Σ_n K[j, n] r_m · x_n: the kernel applied
to the field, read at the seeds. So the effective receptive field of a seed is the composition of the encoder's
propagation and the module's spread, and the two trade off: a short spread with far-reaching encoder gains reads the
same as a long spread with short gains. The spread parameter is therefore partly confounded with the encoder's gains;
the confound is partial because the gains are shared by every module and the spreads are not, so what the spreads
can learn is the difference between modules' extents, not the absolute reach. **Does it matter?** For prediction, no:
it is a reparameterisation. For interpretation, yes: a module's extent is not read off t_m alone but off the hard
membership (z above a threshold), which is what `module_health`'s `median_support_size` already reads. It also
answers the earlier pass's identifiability face (a support on any subset of co-varying nodes gives the same
activation): under a spread, the subset is tied to the graph, so the fitted seed set is the identifiable object up to
a shift of a seed within a dense cluster (section 5).

### 2.4 How a held-out node joins a module

Under the per-node gate a node that no training perturbation's field reaches gets only the sparsity gradient and
closes, so "a node first reached by a held-out perturbation's cone cannot be in any support at test time" (earlier
pass, section 1). Under a grown support a node's membership z[m, n] = g(Σ_j s_j K[j, n]) depends on its graph
position and not on its own gate: an unreached node is a member when it lies in the spread of an open seed. Measured:
of the 10,351 nodes outside every training cone (section 2.5), 9,197 are within two undirected hops of a reached node
and 9,593 within three, so almost all of them can be members of a module whose seeds lie among reached nodes. This is
the disease-module hypothesis used as an inductive bias (a neighbour of members is a member), and it is the one gain
of option 2 that no count expresses.

### 2.5 Gradient flow and dead seed gates (measured 7 November 2026 on v5)

**The field's reach.** The loader (`load_experiment_data`, `group_by="disease_cluster_and_targets"`,
`drug_entry="nodes"`, the default label grades A and B) gives 2,455 perturbations with 2,399 distinct seed nodes; the
union of their forward cones under the encoder's rule (currency nodes pass nothing on) covers **39,483** nodes and
leaves **10,351** unreached (40,338 and 9,496 if currency nodes passed on; 39,563 reached with every label grade,
2,653 seed nodes). The earlier pass reported 42,389 reached from 2,797 seed nodes and 7,445 unreached; this pass could
not reproduce those three numbers under any of the four loader settings tried (label grades A and B or all; drug
entry nodes or targets), and the earlier record does not say how its seed set was formed (the v5 evidence records
hold 2,636 distinct `perturbation_nodes` strings). Both are reported; the counts below use this pass's 39,483.

**When a seed gate gets gradient.** With sum pooling on the difference field, ∂loss/∂z[m, n] is zero on an unreached
node (its state is zero), so ∂loss/∂s[m, j] = Σ_n K[j, n] ∂loss/∂z[m, n] is zero exactly when the spread from j puts no
mass on any reached node. Measured as (K r)[j] with r the indicator of the 39,483 reached nodes:

| kernel (spread graph) | seeds with mass on reached nodes below 10^-12 | below 10^-6 | below 10^-3 |
|---|---|---|---|
| heat t = 0.5, undirected, no currency | 467 | 518 | 899 |
| heat t = 2 | 467 | 470 | 535 |
| heat t = 8 | 467 | 467 | 695 |
| PPR α = 0.5 / 0.15 / 0.05, undirected | 467 / 467 / 467 | 467 / 467 / 467 | 546 / 467 / 467 |
| PPR α = 0.5, 0.15, 0.05, directed forward (currency sources dropped) | 1,260 | 1,260 | 1,260 |
| k-hop, undirected, k = 1 / 2 / 3 | 3,526 / 1,154 / 758 | | |
| k-hop, directed forward, k = 1 / 2 / 3 | 3,274 / 1,404 / 1,291 | | |
| **per-node gate today** | **10,351** | | |

The 467 are nodes in components that hold no reached node (the undirected spread graph has 685 components). So an
undirected kernel leaves about 500 of 49,834 seed gates dead against 10,351 today, a directed one 1,260, and a one-hop
neighbourhood 3,526. "Alive" is not "learnable": below 10^-3 of mass the gradient is small, and under Adam a small
gradient is normalised to a full step (design 5.5's caveat), so far seeds move on noise; the stability selection is
what sorts that out, as it does for the present gates.

**Closure overstates the field's neighbourhood.** The forward cone to closure of 2,212 of the 2,455 perturbations is
one and the same set of 38,079 nodes (measured in section 10.3), so "reached at closure" is almost graph-wide and the
10,351 unreached nodes are the nodes outside the giant forward-reachable set; the field's magnitude decays with
distance under the contraction, and the hop-bounded cones (median 231 nodes at three hops, 5,801 at four) are the
better picture of where a perturbation's signal is. The dead-gate counts above use closure, as the registered fixed
point does; under a hop-bounded reading more seeds are weakly fed and the stability selection matters more.

Within the candidate sets of section 3, dead seeds (mass below 10^-6, heat t = 2 undirected / PPR α = 0.15
directed / per-node gate today): every node 470 / 1,260 / 10,351; field-reached union 0 / 0 / 0; drug-target nodes
0 / 0 / 0; curated anchors 0 / 0 / 6; field-reached gene and protein nodes 0 / 0 / 0; gene, protein and protein-entity
nodes 48 / 161 / 7,060.

### 2.6 What a single seed grows into (measured, 8 example protein seeds, median; "size" = nodes above 1 per cent of the row maximum, participation ratio in brackets)

| spread | heat t = 0.5 | t = 2 | t = 8 | PPR α = 0.5 | α = 0.15 | α = 0.05 |
|---|---|---|---|---|---|---|
| undirected, no currency | 26 (3.8) | 106 (49) | 1,218 (1,048) | 30 (6.2) | 82 (66) | 155 (429) |
| directed forward | | | | 21 (3.6) | 42 (19) | 82 (49) |

For TH under heat t = 2 (undirected) the top members after TH itself are the dopa/dopamine metabolites and reactions
(MAM01154c, MAR06728, MAR08537, MAM01698c), DNAJC12, the dopamine receptors DRD5, DRD1, DRD4, DRD3, DDC, and also GLP1R
and TYMS; under directed PPR α = 0.15: DDC, then CDK2, CDK1, PRKACB (kinases that regulate TH, reached forward through
`activates`), DRD1-5, CAMK2D, CAMK2B, FGF2, FOSB, the two reactions, SLC18A2 and SLC18A1. So a seed at TH grows a module
that is recognisably the catecholamine module of `docs/curated_pathway_modules.csv` (TH, DDC, SLC18A2, the receptors)
plus the kinase and receptor neighbours curation leaves out, which is the cross-pathway behaviour the owner wants
(9.119(2)) and also where a reader will need the hard threshold.

### 2.7 Is the assumption true on this graph? (measured 7 November 2026 on v5)

Menche et al.'s test applied to the 16 curated modules on the spread graph (undirected, unsigned, currency nodes,
drug `targets` edges and the membrane-potential node removed; 226,998 undirected edges, 685 components): for each
module's protein nodes, the largest part connected at a path length of at most L, and the mean distance from a member
to its nearest other member, against 30 random protein sets of the same size.

| module | protein nodes | largest part at L ≤ 2 (of n) | parts at L ≤ 2 | largest part at L ≤ 3 | mean nearest-member distance | random mean (sd) | z |
|---|---|---|---|---|---|---|---|
| catecholamine | 10 | 10 | 1 | 10 | 1.80 | 2.95 (0.34) | -3.4 |
| serotonin_melatonin | 7 | 6 | 2 | 7 | 2.14 | 3.06 (0.49) | -1.9 |
| tetrahydrobiopterin | 5 | 4 | 2 | 5 | 2.20 | 3.28 (0.61) | -1.8 |
| phenylalanine_tyrosine | 4 | 3 | 2 | 4 | 2.25 | 3.24 (0.59) | -1.7 |
| tryptophan_kynurenine | 7 | 3 | 4 | 4 | 2.43 | 3.19 (0.44) | -1.7 |
| gaba_glutamate | 7 | 5 | 3 | 6 | 2.43 | 3.04 (0.46) | -1.3 |
| one_carbon_homocysteine | 10 | 3 | 8 | 8 | 3.00 | 2.97 (0.41) | +0.1 |
| urea_cycle | 8 | 2 | 5 | 8 | 2.25 | 3.13 (0.38) | -2.3 |
| heme_porphyrin | 8 | 3 | 4 | 8 | 2.25 | 2.95 (0.34) | -2.0 |
| copper_metal | 3 | 3 | 1 | 3 | 2.00 | 3.52 (0.90) | -1.7 |
| sterol_lysosomal_lipid | 8 | 2 | 7 | 2 | 3.63 | 2.98 (0.44) | +1.5 |
| creatine_energy | 6 | 2 | 5 | 6 | 2.67 | 3.05 (0.44) | -0.9 |
| purine_pyrimidine | 4 | 1 | 4 | 3 | 3.50 | 3.34 (0.69) | +0.2 |
| acetylcholine_histamine_adenosine | 7 | 3 | 4 | 7 | 2.29 | 3.02 (0.43) | -1.7 |
| steroid_thyroid | 6 | 2 | 4 | 5 | 2.50 | 3.14 (0.41) | -1.6 |
| vitamin_cofactor_transport | 4 | 1 | 4 | 1 | 4.25 | 3.49 (0.75) | +1.0 |

Reading. Protein nodes are never adjacent on this graph (an enzyme touches a reaction, not another enzyme), so L = 1
is empty for every module and the natural unit is L = 2 (enzyme - reaction - enzyme, or protein - protein through one
intermediate) and L = 3. At L ≤ 2 the median module has 40 per cent of its members in one connected part; at L ≤ 3
the median is 100 per cent (12 of 16 modules fully connected; the exceptions are sterol_lysosomal_lipid, 2 of 8,
vitamin_cofactor_transport, 1 of 4, purine_pyrimidine, 3 of 4, and tryptophan_kynurenine, 4 of 7). The mean
nearest-member distance is below the random expectation for 12 of 16 modules (z between -1.3 and -3.4; the
catecholamine module -3.4, the urea cycle -2.3, heme -2.0), at the random value for one_carbon_homocysteine and
purine_pyrimidine, and above it for sterol_lysosomal_lipid and vitamin_cofactor_transport, whose members are
transporters and lysosomal enzymes of different compartments that the curated list groups by clinical theme rather
than by a shared reaction chain. So on v5 the assumption holds in Menche's weak form for three quarters of the
curated modules and in the strong form (one part at L ≤ 3) for twelve of sixteen, which is a stronger result than
on protein-protein interactomes (Menche's 20 per cent observable; Agrawal's 90 per cent disconnected) because the
metabolic layer connects enzymes through their reactions by construction. The four modules the spread would not
reconstruct from one seed are the ones a seed gate over several seeds handles, and they are the argument for several
seeds per module (section 10.2) against a single exemplar.

## 3. Counts (measured 7 November 2026 on v5; M = 8; "+ 8" is one spread per module)

| candidate seed set | nodes | nominal seed gates | per positive (4,446) | physiology of the restriction |
|---|---|---|---|---|
| every node | 49,834 | 398,672 + 8 | 90 | none needed; the physiological version |
| field-reached union | 39,483 | 315,864 + 8 | 71 | numerical (identifiability); on this graph it removes only gates that are dead under the per-node form and 467 to 1,260 under a kernel |
| gene, protein and protein-entity nodes | 27,214 | 217,712 + 8 | 49 | "a module is seeded at a gene product" (metabolites and reactions join by spread): physiological for the signalling layer, not for a metabolic module seeded at a metabolite |
| field-reached gene and protein nodes | 18,674 | 149,392 + 8 | 34 | the two above combined |
| perturbation entry nodes (distinct training seeds) | 2,399 | 19,192 + 8 | 4.3 | "a module is seeded where a perturbation enters": data-defined, numerical |
| curated anchors (103 genes; gene and protein nodes) | 205 | 1,640 + 8 | 0.37 | confines seeds to curation, the owner's 9.119(2) concern; spread still crosses pathways |
| drug-target nodes (`drug_entry_nodes.parquet`) | 166 (165 proteins, 1 gene) | 1,328 + 8 | 0.30 | pharmacological, not physiological; biases modules to drug targets |

Beside the earlier pass's options (its counts, v5): (a) sets 1,432 (10^3 to 10^4 with GO); (b) anchors + 1-hop
11,840; (c) descriptors 1,296 to 5,440; attention d = 16 2,720; (d) ≤ 640; (e) 0; (f) 199,336.

**Effective count.** The description length counts expected active seeds Σ_m E[#nonzero s_m] plus 8 spreads. A target
to state for the owner: the curated modules hold 3 to 10 genes each (103 over 16), HotNet2's 16 consensus subnetworks
hold "147 genes" together (about 9 each), so a fitted module of 3 to 10 seeds and 8 modules is 25 to 80 active seeds
plus 8 spreads: on the order of 10^2 numbers describing the whole support layer, against 4,446 positives. The nominal
count under "every node" stays 398,680 and is what the amendment must state honestly, as the earlier pass said of the
attention hybrid.

## 4. Compute (measured 7 November 2026 on this machine, 4 CPU threads, scipy and torch, 8 module columns at once)

| operation on the undirected spread graph (49,834 nodes, 228,088 edges) | time |
|---|---|
| one sparse matrix × [N, 8] product, scipy | 2.1 ms (directed walk 1.6 ms) |
| the same in torch CPU sparse CSR | 20 ms |
| exp(-2L) B by Krylov (`scipy.sparse.linalg.expm_multiply`) | 392 ms (t = 8: 580 ms) |
| Chebyshev series for exp(-2L) B, 10 / 20 / 40 terms | 84 / 71 / 139 ms; largest error against Krylov 8 × 10^-8 / 10^-16 / 10^-16 |
| PPR by 40 power steps | 152 ms |

A training step needs one spread forward and one backward (K is symmetric, so ∂/∂s is K applied to the readout
gradient; ∂/∂t of exp(-tL) s is -L exp(-tL) s, one more product). With a 20-term Chebyshev series in torch that is
about 2 × 20 × 20 ms = 0.8 s per step on this CPU, which is of the order of the registered per-epoch slice times the
preregistration quotes for the encoder ("2.1 s (linear response, noisy-OR)") and small beside the encoder on a GPU,
where a sparse product on 275,006 edges is sub-millisecond. Two cheaper forms: (i) GDC's precomputation, one
sparsified kernel per value of a spread grid (top-k per row; k = 256 is 12.8 M entries per kernel, where the dense
kernel is 2.5 × 10^9), with the spread a softmax over the grid, which makes the spread discrete and the kernel
inspectable but adds a sparsification threshold; (ii) a k-hop neighbourhood, which is k products and no series.

## 5. Interpretability for the nosology aim

- **What a reader reads off a module.** Its seeds (a list of named nodes, typically a few), its spread (a scale, or a
  hop count, or the hard membership size at the read-out threshold), and the hard membership itself (z above 0.5, as
  `module_health` reads today). "Module 3: seeds TH, DDC, SLC6A3; extent two hops; 94 members" is a readable object in
  a way that a 25-node fallback support is not (`docs/module_names.md`: 314 of 400 pilot supports "mixed").
  Stability selection runs on seeds (Jaccard of seed sets across folds and seeds) and on hard memberships; seeds are
  the smaller and more stable object, but a seed can shift one hop inside a dense cluster with almost no change of
  membership, so the consensus is stated on the membership as well.
- **Modules that cut across curated pathways.** Yes, natively: a module with seeds in two pathways, or one seed at a
  junction node (DDC is in both the catecholamine and the serotonin curated modules; TH's spread already reaches
  GLP1R and the CDKs, section 2.6), with nothing in the parameterisation tying membership to a curated boundary. That
  is what the owner asked for in 9.119(2) and what option (a) cannot give.
- **Comparison with curated pathways afterwards.** Three readings, two of which exist: the subsystem-share enrichment
  of `experiments/analyze_pathway_modules.py` (`describe_support`, `module_label`) on the hard membership; the seed
  overlap with the curated gene lists and the Human-GEM subsystems; and, new, Menche's separation s_AB between the
  grown module and each curated set on the spread graph, which says whether a module sits inside, beside or across
  curated pathways without a membership threshold.
- **What is lost.** A module's name is derived, not given, as under option (a); and a spread is not a physiological
  quantity, so the reader must be told that "extent" is a kernel scale.

## 6. Registered and lockbox implications

- **Clauses that change.** Design 5.3 ("K modules, each with a learned sparse support m_k in [0, 1]^|V|
  (hard-concrete relaxation of an L0 penalty [26])"; `docs/preregistration.md` section 1 restates it as "one hard
  concrete gate per module and node"): the support becomes m_k = g(K(θ_k)ᵀ s_k) with s_k the hard-concrete gate.
  Design 5.5's model cost "number of active support nodes" becomes active seeds plus one spread per module (section
  10.1 on whether the membership mass is also charged). The trainer defaults keep `--gate-initial-log-alpha`,
  `--gate-init-noise`, `--gate-learning-rate`, `--module-bias-init` (the seeds are the same gate) and gain a kernel,
  an initial spread, its learning rate and the candidate set. `module_health`'s `median_support_size` keeps its meaning
  on the hard membership; its gate-travel reading moves to the seeds. `analyze_pathway_modules.py` gains the seed
  list and the separation reading. The study-sheet diagrams 012dc8f5-8ee9 ("A module is a learned set of nodes") and
  15448121-6479 ("Almost every parameter is module membership") each get an as-decided version (a module is a set of
  seeds grown along the graph; the count table with the chosen candidate set). No entry of
  `configs/registered_rules.json` names the support parameterisation today (checked: the words "gate" and "support"
  do not occur in it); the amendment adds one, asserted by `tests/test_registration_matches_the_code.py`.
- **Tested model or robustness arm.** Under 9.119(1) the tested model's support parameterisation changes before the
  first confirmatory run, outcome-blind while the v5 lockbox is undrawn (the draw waits on 9.111), and attention is
  the robustness arm. Option 2 can be the tested parameterisation (then option (a) or attention is the arm) or a second
  arm beside attention under `robustness_models`; which is the owner's under 9.119(2). The physiology rule favours the
  option that needs no numerical restriction, which is option 2 with every node a candidate seed, whose nominal count
  is then unchanged and whose effective count is what the description length controls.
- **Pathway-wise hold-out.** A held-out curated module's genes stay candidate seeds and its nodes stay reachable by
  spread from neighbouring seeds; what leaks is graph structure, which the registered design already shares between
  folds, not labels or memberships. Picart-Armada's finding that complexes inflate cross-validation applies to the
  grouped split and is already handled by the disease-cluster grouping.

## 7. Comparison with option 1 (sets as a prior with description-length-charged departures, the expiMap form)

| | option 1: fixed sets + charged per-node residual | option 2: seeds grown along the graph |
|---|---|---|
| physiology encoded | curation's units, with listed exceptions | connectivity's units: a pathway is a connected chain of steps |
| what it rests on | the curated sets being the right units (9.63's circularity for pathways) | the disease-module hypothesis in its weak form (section 1.2, 2.7) |
| nominal count on v5 | M × P (1,432 at P = 179) + residual candidate (11,840 on anchors + 1-hop, 398,672 unrestricted) | M × candidates + M (398,680 unrestricted; 19,200 on entry nodes; 1,648 on anchors) |
| effective count | active sets + active residual nodes | active seeds + spreads (10^2) |
| held-out node | by set membership (nodes in no set: 20,409, earlier pass) never | by graph proximity; every node in a component with a seed |
| cross-pathway module | union of whole sets, or part of a set only through the charged residual | native |
| readability | named sets ± exceptions: best for naming | seeds + extent: names derived afterwards |
| published analogue | expiMap (`lotfollahi2023biologically`): fixed programs "while simultaneously refining them and learning de novo programs" | HotNet2 (fixed spread, seeds from data), ADC (learned spread), Berberidis (learned per-class diffusion) |
| compute | a fixed P × N matrix product | one spread per step (section 4) |

The two combine: option 1's residual can itself be grown (a departure is a seed plus a short spread, which is
HotNet2's "subnetwork around a known pathway"), and option 2's seeds can start at the curated anchors (section 10.3).
Which is the tested model turns on 9.119(2): whether the nosology's units should be curation's or the graph's.

## 8. Questions for the owner (each its own question)

1. Whether option 2 is the tested model's support parameterisation (an amendment before the confirmatory run) or a
   robustness arm beside attention.
2. The spread graph's relations: whether `regulates_transcription_of` and `binds` define membership (hub TFs merge
   pathways; `binds` is the disease-module literature's layer); and confirmation that drug `targets` edges, drug
   nodes and the membrane-potential node are left out of the spread (the pass's proposal).
3. Direction and sign of the spread: undirected and unsigned (the pass's reading of physiology) or forward-directed
   like the encoder.
4. The kernel: the k-hop neighbourhood (closest to "a chain of connected steps", integer extent) or its differentiable
   relaxation (heat kernel or PPR, a numerical choice for the gradient), and the membership form (noisy-OR of seeds
   proposed).
5. The candidate seed set: every node (physiological, nominal count unchanged) or one of the restrictions of section
   3, each numerical and carrying its justification.
6. Hubs: degree normalisation of the spread (the literature's insulation, numerical) against excluding hub relations
   (physiological but coarser).
7. The description-length unit: active seeds plus spread only, or also the membership mass (section 10.1).
8. Whether K stays preset at 8 with post-hoc selection, or an overcomplete pool or exemplar form is adopted (section
   10.2).
9. Seed initialisation: equal, from the curated anchors, or from the training cones' node frequency (section 10.3).
10. Whether the assumption test of section 2.7 (curated modules' connectivity on the spread graph) should be a
    registered check of the amendment.

## 9. Sources, with where each was read

- Repository at `main` 16a3c847, 7 November 2026, as named in the text.
- PubMed records through the PubMed connector, 7 November 2026: PMIDs 25501392, 25700523, 20090828, 18371930,
  31479437, 25853560, 29218874, 28607512, 21164525, 31471613, 17218491; full texts PMC4444046 and PMC4435741 through
  the same connector. Each PubMed record confirmed against the Europe PMC REST record read with
  `experiments/read_public_page.py` the same day (titles, author strings, journals, volumes, issues, pages and years
  agree; Europe PMC supplies the DOI 10.1142/9789813235533_0011 that the PubMed record of 29218874 lacks).
- Crossref records (`api.crossref.org/works/<doi>`, read with `experiments/read_public_page.py`, 7 November 2026):
  10.1109/TSP.2018.2889984, 10.1016/0005-1098(78)90005-5, 10.1198/016214501753168398, 10.1214/10-AOAS435.
- Proceedings pages read with `experiments/read_public_page.py`, 7 November 2026: `papers.nips.cc` paper_files 2019
  hash 23c894276a2c5a16470e6a31f4618d73 (SHA-256 de6a18f4…), `proceedings.neurips.cc` 2021 hash
  c42af2fa7356818e0389593714f59b52 (55581fa3…), `www.jmlr.org/papers/v12/griffiths11a.html` (eb3eba36…).
- Refusals recorded (section 1.3): dblp.org search page and `/search/publ/api` (HTTP 202, a check that the visitor is
  human, under the owner's dblp exception), api.openalex.org (HTTP 429, twice, 20 s apart), api.semanticscholar.org
  (HTTP 429), openreview.net forum pages and api.openreview.net / api2.openreview.net (a "Verifying your browser"
  page). None was read through a cache or mirror.
- Consensus search tool, 7 November 2026, for the neural diffusion literature (its records were used to find the
  papers; every field in section 11 comes from the proceedings page or Crossref, not from Consensus).

## 10. The owner's additions of 7 November 2026: a size term, not presetting K, seeding, and overlap

The owner (7 November 2026, relayed by the session): "maybe it's worth including a counter balance loss term in the
MDL for explainability in the form of module sizes? Then it wouldn't require presetting a number of modules but how
would you seed it then?", clarified the same day: "I just meant that decreasing the size of each module would improve
interpretability. I plan towards option 2 with the per node seeds merging but it has to be allowed to overlap (a
[node] can belong to multiple modules) otherwise the cross module interperetability causes issues". Nothing here is
ruled; the owner's direction (exemplar seeds that merge, overlap required) is taken as the form to study.

### 10.1 Module size in the description length

**What the design charges today.** Design 5.5 and `models/minimum_description_length_selection.py`: model cost =
node_cost × active support nodes + link_cost × nonzero links, with "a node cost of log2(num_graph_nodes) bits ... the
natural choice (the cost of naming a node)", `node_naming_cost_nats = log(N)` = 10.82 nats = 15.6 bits on v5; K is
chosen by training candidate values separately and taking the smallest total. So the size cost is already linear in
module size, at a fixed per-node price, and it is not a free weight: it is a code.

**The proper two-part code, measured on v5 (N = 49,834).** Coding a support of s members by its size then its
identity costs log2 N + log2 C(N, s) bits (Rissanen 1978, Automatica, the two-part code: "the shortest description of
the data"; Hansen and Yu 2001, JASA, the review that sets out two-part and mixture codes, and which this pass read
only through its Crossref record and title, so nothing is quoted from it):

| s | code bits | per member | linear code (15.6 bits per member) | code ÷ linear | marginal bits of the s-th member |
|---|---|---|---|---|---|
| 1 | 31.2 | 31.2 | 15.6 | 2.0 | 15.6 |
| 5 | 86.7 | 17.3 | 78.0 | 1.11 | 13.3 |
| 10 | 149.9 | 15.0 | 156 | 0.96 | 12.3 |
| 50 | 581.6 | 11.6 | 780 | 0.75 | 10.0 |
| 100 | 1,051 | 10.5 | 1,560 | 0.67 | 9.0 |
| 1,000 | 7,077 | 7.1 | 15,600 | 0.45 | 5.6 |
| 5,000 | 23,433 | 4.7 | 78,000 | 0.30 | 3.2 |
| 25,000 | 49,841 | 2.0 | 390,000 | 0.13 | 1.0 |

(The design's linear cost is 1 nat per node in the code and log2 N bits per node in the docstring; the table uses the
docstring's price. Under 1 nat per node the linear column is 1.44 bits per member and the ratio is 10 times larger.)
Reading: the exact code is **concave** in s. Its marginal cost falls from 15.6 bits for the first member to 9 bits at
100 members and 1 bit at 25,000: a large module is cheap per node because there are few ways to be nearly everything.
So **coding alone gives no pressure toward small modules beyond the linear one; it gives less**, and the sizes that
matter for readability (5 to 100 members) are where the two codes agree within a factor of 1.5. The exact code has a
real use: it is what makes "naming a node" cost 15.6 bits rather than a free coefficient, and it adds a module-level
term log2 N for the size itself, which is one of the per-module costs section 10.2 needs.

**A readability size term is a free weight.** A cost that rises faster than the code (a convex term, s² or a cap)
cannot be derived from a code length over this graph; it would be a prior over module sizes, and a prior is a code
only if it is stated as one (a distribution over s that puts little mass on large s, which is then a choice, not a
measurement). Under MDL the honest form is: state the size prior explicitly as a code (for example, a geometric
prior on s with its parameter fixed before fitting, or chosen by the data cost across folds), record it as a
decision with the physiology rule's justification (readability is not physiology, so this is a numerical choice made
for the nosology aim and must say so), and keep it out of the confirmatory selection unless registered. The owner's
own preference for data-determined choices (9.119(2)) argues for letting the data set the size prior's parameter on
development folds, which the design's "candidate values trained separately" machinery already does for K.

**What a size pressure costs in fit, and whether it fragments a pathway.** The field co-varies along a pathway
(earlier pass, section 3(3)): if a module reads the field at 5 nodes or at 50 co-varying nodes the activation is
nearly the same, so a size cost loses little fit until the module is cut below the nodes that carry independent
signal; the loss is sharp once a pathway's distinct branches are forced apart, because the noisy-OR then needs two
modules and two links where one would do, and the description length pays the per-module cost twice. That is the
fragmentation risk: a size term alone favours many tiny modules (two modules of 5 cost no more than one of 10 under
a linear code and less under the exact code), so it needs a counterweight that charges splitting: a per-module cost
(log2 K_max for the count, log2 N for each module's size, and the links: with S = 39 symptoms and two relations,
coding L nonzero links among 2KS costs log2 C(2KS, L) + log2(2KS), measured 68 bits at K = 8, L = 8 and 134 at L = 20,
rising with K). On this graph the curated modules are 3 to 10 genes (section 2.7), and a module cut to that size at
L ≤ 3 is still connected for 12 of 16 of them, so a size prior centred near 10 seeds would not fragment the curated
pathways on v5; what it would fragment is a module that spans two curated pathways (the owner's wanted case), which
then needs to be worth its second module's cost. Overlap (section 10.4) changes the arithmetic: a node in two
modules is coded twice, so overlapping small modules are not cheaper than one large one.

### 10.2 Not presetting K

**(a) An overcomplete pool pruned by module-level gates.** K_max modules, each with a hard-concrete module gate g_m
(the existing gate class with N = 1) multiplying its activation, and a per-module cost in the description length (the
count code, the size code, the links). K_max is a bound, and the check that it is not a choice is that the fit does
not use all of it: with K_max = 32 on v5 the nominal count is 32 × (seed gates + 1 spread + 1 module gate) and the
effective count is the open modules. Psorakis et al. 2011 (Phys Rev E, PMID 21797448) is the overlapping-community
form of this: "a Bayesian non-negative matrix factorization model to extract overlapping modules", "soft-partitioning
solutions, assignment of node participation scores to modules", with the number of modules determined by relevance
determination on an overcomplete factorisation. Parameters on v5 (M = K_max = 32): every node 32 × 49,834 = 1,594,688
seed gates + 64; entry nodes 32 × 2,399 = 76,768 + 64; anchors 6,560 + 64. The pool multiplies the nominal count by
K_max / 8 and leaves the effective count to the fit.

**(b) The exemplar form (the owner's direction).** Each candidate node j carries one seed gate e_j (N gates, not
M × N) and a spread θ_j; an open exemplar founds a module whose membership is K(θ_j)[j, ·]; K is the number of open
exemplars. Affinity propagation (Frey and Dueck 2007, Science, PMID 17218491) is the published exemplar method:
"Clustering data by identifying a subset of representative examples", where "Real-valued messages are exchanged
between data points until a high-quality set of exemplars and corresponding clusters gradually emerges"; it was
applied to "detect genes in microarray data". But it assigns each point to one exemplar, which violates the owner's
overlap requirement, and a module has a single centre. Two losses of a single centre: a module whose members sit in
two regions (four of the sixteen curated modules on v5, section 2.7) cannot be one exemplar's spread; and the spread
from a centre is radially symmetric in graph distance, so a pathway that runs as a chain is cut at its ends. **How
exemplars merge.** Multi-exemplar affinity propagation (Wang, Lai, Suen and Zhu 2013, IEEE Trans Pattern Anal Mach
Intell 35(9):2223-2237; Crossref record read, abstract not held) lets a cluster have several exemplars under a
"super-exemplar"; the gradient analogue here is a merge gate: a learned, sparse, symmetric affinity a_jk between
open exemplars (hard-concrete again), and a module is a connected set of exemplars under a; its membership is the
noisy-OR of its exemplars' spreads. The nominal count of the merge gates is the number of candidate pairs, which is
why the candidates have to be restricted for the merge to be countable: on entry nodes, 2,399 × 2,398 / 2 = 2.9 M
pairs unrestricted, or a_jk defined only for pairs within the spread of each other (sparse, a few thousand). A
simpler merge that needs no pair gates: two open exemplars whose spreads overlap above a threshold are read as one
module at read-out (the stability-selection pass), which merges without parameters but makes K a read-out quantity.
**Overlap in the exemplar form.** Overlap is native when a node's membership in each module is computed from that
module's exemplars alone (z[m, n] = noisy-OR over m's exemplars of K[j, n]), and a seed can sit in several modules
because membership does not consume it; it is lost only if nodes are assigned to their nearest exemplar (affinity
propagation's rule) or if memberships are normalised over modules (section 10.4).

**(c) Bayesian nonparametric forms.** The Indian buffet process (Griffiths and Ghahramani 2011, JMLR 12:1185-1224;
page read today) is "a probability distribution over equivalence classes of sparse binary matrices with a finite
number of rows and an unbounded number of columns": rows are nodes, columns are modules, and a row may hold several
ones, so **the IBP is overlapping by construction** and does not preset K. It has been used for gene modules:
Knowles and Ghahramani 2011 (Ann Appl Stat 5(2B):1534-1552; Crossref record, abstract not held) is a "Nonparametric
Bayesian sparse factor model with application to gene expression modeling", the IBP placing genes in an unbounded
number of sparse factors. For networks, the mixed-membership stochastic blockmodel (Airoldi, Blei, Fienberg and
Xing 2008, JMLR 9:1981-2014; page read today) gives each node a membership distribution over blocks (overlap, K
preset), and Yu et al. 2020 (Front Comput Sci 14(6); Crossref record) put the IBP on the community assignment matrix
"which can allow K to increase as more and more data are encountered instead of to be fixed in advance". What these
do not have is a graph-grown membership: the IBP's binary matrix is free per node, so its parameter count is the
per-node gate's (N × K_max latent bits, 1.6 M at K_max = 32 on v5) and its sparsity comes from the prior, not the
graph. An IBP over **exemplars** (a binary matrix of candidates × modules with the membership grown from the chosen
exemplars) would be the nonparametric version of (b); the pass found no published instance.

**Counts of the exemplar form on v5 (measured candidate sizes; "+ spreads" is one per candidate, "+ merges" is the
sparse pair gates, counted here as pairs within two hops on the spread graph, not measured):**

| candidate exemplars | exemplar gates | spreads | nominal (gates + spreads) | per positive |
|---|---|---|---|---|
| every node | 49,834 | 49,834 | 99,668 (+ merges) | 22 |
| field-reached union | 39,483 | 39,483 | 78,966 | 18 |
| field-reached gene and protein nodes | 18,674 | 18,674 | 37,348 | 8.4 |
| perturbation entry nodes | 2,399 | 2,399 | 4,798 | 1.1 |
| curated anchors | 205 | 205 | 410 | 0.09 |
| drug-target nodes | 166 | 166 | 332 | 0.07 |

Against the M × N forms: the exemplar form with every node a candidate is 99,668 nominal (4 times below the present
398,672 and the same order as the restricted M × N forms), and it is the only form whose nominal count does not grow
with K. With one spread shared by all exemplars (a numerical simplification), the count halves. The effective count
is the open exemplars (10^1) plus their spreads.

### 10.3 "How would you seed it": initialising the exemplar gates

Each initialisation is a prior and imposes something:

- **All candidates equal and slightly closed** (`--gate-initial-log-alpha` below the open point with `--gate-init-noise`
  for symmetry breaking, the present scheme): imposes nothing but the symmetry-breaking noise, so which exemplars open
  is decided by the data gradient; under Adam a gate the field reaches weakly still takes full steps, so the early
  fit is noisy and the stability selection across seeds is what makes the open set trustworthy. The risk is the
  degenerate mode of `docs/experiment_design.md` section 10 (every module opening on the same hub nodes), which a
  degree-normalised kernel reduces but does not remove.
- **From the curated anchors** (205 nodes open, the rest closed): imposes the curated pathways as the starting modules,
  which is the owner's 9.119(2) concern ("forcing our notions onto the final ontology"); it is defensible only as a
  robustness arm ("does the fit stay where curation put it?") or as the pathway-wise hold-out's control, not as the
  tested model's start.
- **From the training cones' node frequency** (how often a node lies in a training perturbation's forward cone;
  measured on v5 below): data-derived, training folds only, blind to the lockbox because it uses the perturbations'
  seeds and the graph and no label. It imposes that modules start where the field is, which is where gradients are,
  so it speeds the fit; its bias is toward hubs and toward nodes downstream of many perturbations, which the measured
  distribution makes concrete:

  **Measured on v5, 7 November 2026** (2,455 training perturbations under the loader settings of section 2.5; a
  node's cone frequency is the number of perturbations with the node inside the forward cone of at least one of
  their seeds, currency nodes passing nothing on). **At closure the frequency is binary and useless as a start**:
  2,212 of the 2,455 perturbations have the same forward cone of 38,079 nodes (the giant forward-reachable set), the
  rest have cones of a few nodes, so 38,079 nodes have count 2,212 to 2,228 and the other 11,755 have count 0 to 9.
  The usable form is hop-bounded (a node within k forward hops of a seed), which is also what the field's decay with
  distance means physically:

  | k | median cone size | nodes in no cone | count quantiles over reached nodes (10, 50, 90, 99 pct) | share of memberships in the top 10 per cent of nodes | Spearman with in-degree | fold stability: Spearman between the five grouped training sets, min / median; top-decile Jaccard min / median | nodes in no training cone, per fold |
  |---|---|---|---|---|---|---|---|
  | 1 | 2 | 45,163 | 1, 1, 1, 5 | 1.00 | 0.21 | -0.38 / 0.10; 0.46 / 0.74 | 45,814 to 47,021 |
  | 2 | 8 | 33,087 | 1, 2, 7, 32 | 0.74 | 0.65 | 0.48 / 0.79; 0.53 / 0.75 | 34,181 to 37,438 |
  | **3** | 231 | 22,630 | 1, 11, 235, 624 | 0.75 | 0.54 | 0.93 / 0.97; 0.85 / 0.97 | 23,614 to 25,096 |
  | 4 | 5,801 | 16,329 | 1, 168, 1,273, 1,570 | 0.43 | 0.56 | 0.99 / 1.00; 0.91 / 0.96 | 16,986 to 17,909 |
  | 6 | 26,516 | 11,847 | 11, 1,744, 1,871, 1,900 | 0.19 | 0.61 | 1.00 / 1.00; 0.78 / 0.88 | 12,122 to 12,620 |
  | closure | 38,079 | 10,351 | 2,212, 2,212, 2,212, 2,213 | 0.13 | 0.22 | 0.92 / 0.94; 0.04 / 0.05 | 10,522 to 10,872 |

  (Folds here are five grouped splits of the training perturbations by `group_ids` under
  `disease_cluster_and_targets`, a stand-in for the registered folds; the lockbox is not drawn, so every perturbation
  is development data today.) The nodes a k = 3 start would open first: TP53 (count 1,170; degree 1,613), MAPK14
  (1,124), GSK3B (1,111), CTNNB1, NFKB1, AKT1, MAPK3, EGFR, SRC, CDKN1B, RELA, MAPK8; at k = 2, ATM, PRKCA, RPS6KA3,
  GSK3B, CDK1; at k = 1, the drug targets themselves (DRD2 38, the GABA-A subunits 32 to 34, HTR2A 28, the sodium
  channels 27 to 28). By type at k = 3, the median protein lies in 31 cones and 20 per cent of proteins in none;
  the median gene in 1 and 42 per cent in none; the median metabolite and reaction in 0 (70 and 60 per cent in none).

  **How the frequencies are computed, per fold.** For fold f, over the training perturbations of f alone (the
  grouped split's training side; the lockbox perturbations are in no fold's training side, so the start is blind to
  the lockbox by construction once it is drawn, and until then the computation is deferred or done on the
  development set only), seed each perturbation at its entry nodes, walk k forward hops under the encoder's rule,
  and count per node; or, closer to what the modules read, sum the magnitude of the untrained encoder's difference
  field over the training perturbations at the registered initial gains, which is the same quantity weighted by the
  encoder's decay rather than cut at k hops and is the version that carries no hop parameter (k is a numerical
  choice; the field magnitude is the encoder's own statement of where a perturbation's effect lies). The frequency
  is then mapped to the gate's starting log-alpha by a monotone map that opens the top decile (or a fixed quantile)
  and leaves the rest at the present closed start.

  **What it imposes, and whether to normalise.** Two biases are measured: toward hubs (Spearman with in-degree
  0.54 at k = 3; the first twelve nodes are the signalling hubs above) and toward the signalling layer (proteins in
  31 cones at the median, metabolites and reactions in 0, because the drugs and most monogenic seeds enter at
  proteins and the metabolic layer lies three or more hops downstream). Dividing by in-degree over-corrects: the
  measured count-per-in-degree ranking is topped by in-degree-1 metabolites and reactions downstream of hubs. The
  honest normalisations are (i) rank within node type and within the project's registered degree terciles, so that
  the top decile holds the most-reached node of each type and tercile rather than the hubs; or (ii) DIAMOnD's
  connectivity significance (Ghiassian et al. 2015), a count against its expectation given degree, which is the
  literature's device for the same bias; or (iii) accept the hub start and rely on the degree-normalised spread
  kernel and the sparsity gradient to close the hubs, which the measured leak (section 2.1) argues against. The pass
  recommends (i), because it uses the project's own stratification and imposes no model.

  **Interaction with the merging, overlapping exemplar form.** The top-decile exemplars at k = 3 are hubs whose
  spreads overlap heavily (TP53, GSK3B, MAPK14, AKT1 lie within two hops of one another), so a merge rule read on
  spread overlap would fuse them into one signalling module at the start; the overlap requirement means they need
  not be fused, but the fit then starts with several near-duplicate modules, which is the permutation-and-merge
  non-identifiability at its worst, and the description length's per-module cost is what prunes the duplicates.
  Under normalisation (i) the start opens one exemplar per type and tercile stratum, which spreads the initial
  modules across the metabolic and signalling layers and makes the early merges informative.

  **Stability selection.** The start is nearly the same across folds at k ≥ 3 (Spearman 0.93 to 1.00; top-decile
  Jaccard 0.85 to 0.97 at k = 3), so fold disagreement after training is the data's, as with an equal start; what
  the frequency start adds is a control the equal start lacks: the permuted-label run has the same start (labels do
  not enter it), so a module that appears in the permuted run too is a product of the start and the graph, not of
  the labels, which is exactly what the owner's 9.119(2) concern needs to see.

  **Nodes no training perturbation reaches** (22,630 at k = 3, 10,351 at closure; per fold 23,614 to 25,096 at
  k = 3) start closed. That is not the dead-gate problem again: under the grown form a closed exemplar still gets
  gradient whenever its spread touches field-reached nodes (section 2.5: about 470 dead under an undirected kernel,
  1,260 directed), so the start is a prior the data can overturn, at the price of the sparsity gradient it must
  outrun; and membership does not need the exemplar at all, since an unreached node becomes a member through a
  neighbouring exemplar's spread (9,197 of the 10,351 closure-unreached nodes are within two undirected hops of a
  reached node). An exemplar at an unreached node is in any case a poor one, because its own field is zero and
  only its spread reads anything. The one real loss is a rare monogenic pathway whose perturbations are few: its
  exemplars start closed and open only if its positives outweigh the sparsity gradient, which is where the
  pathway-wise hold-out will show the effect.

  The initialisation would open the candidates in the top decile of cone frequency (or set log-alpha to a monotone
  function of it); because the frequency is a property of the training folds, it differs between folds, and the
  stability selection then compares open sets that started differently, which is a stronger test than seeds that
  started alike. The cost is that a module anchored at a node few perturbations reach (a rare monogenic pathway)
  starts closed and must be opened by its few positives against the sparsity gradient.

**Stability selection and the three.** Equal starts give the cleanest selection (every fold starts the same, so
disagreement is the data's); anchor starts give agreement by construction and so the selection cannot distinguish a
stable module from an unmoved prior; frequency starts vary by fold and so the selection measures whether the data
overrides the start, which is the most informative reading but needs the match-by-Jaccard pairing the preregistration
already uses for supports (item on "matched one to one across the subsamples by support Jaccard").

### 10.4 Overlap: the head, the description length, identifiability

- **The head as written.** `NoisyOrPathwayModuleHead.module_support` returns `support_gate()`, a sigmoid-derived
  hard-concrete value per (module, node) with no normalisation across modules; `module_activation` reads each module
  with `einsum("kn,bnd->bkd")` independently; the noisy-OR combines modules by Π_k (1 - link × activation), which is
  symmetric in the modules and indifferent to a node being read twice. So overlap is allowed today and survives any
  per-module normalisation over nodes (sigmoid gates, sparsemax or entmax within a module, the earlier pass's
  section 3(5)); it is lost only by a normalisation across modules for each node (a softmax over k at fixed n), which
  nothing in the head does. The grown forms of section 2 and 10.2 keep this: membership is computed per module from
  its own seeds.
- **Description length under overlap.** A node in two modules is coded twice (once in each module's support), under
  both the linear and the exact code, because the code describes each module; that is right for MDL (two modules
  that share 30 nodes are two descriptions) and it is the counterweight that stops the size term of 10.1 from
  favouring many overlapping small modules. In the exemplar form the shared node is not coded at all; what is coded
  is the exemplars and spreads, and two overlapping modules cost their exemplars twice only if they share an
  exemplar.
- **Identifiability.** Design 5.5 already names permutation, split and merge; overlap makes split and merge
  continuous (a module can shed part of itself into a neighbour by degrees) and adds a new ambiguity for grown
  supports: two overlapping modules with different seeds and spreads can have the same membership on the field's
  support. The remedy is the registered one, stability selection across seeds and folds with Jaccard matching, read
  on the hard membership and, in the exemplar form, on the open exemplar set as well; and the equifinality
  sufficiency test (design 6.5, `NoisyOrOutput.module_contribution`) remains well defined, since it ablates a module's
  contribution, not a node's.

### 10.5 Which published overlapping-module methods permit what

| method | module draws on several seeds | node in several modules | K preset | graph-grown |
|---|---|---|---|---|
| clique percolation (Palla et al. 2005, Nature, PMID 15944704: "most of the actual networks are made of highly overlapping cohesive groups of nodes") | yes (k-cliques chain) | yes | no | yes, by cliques |
| link communities (Ahn, Bagrow and Lehmann 2010, Nature, PMID 20562860: "communities as groups of links rather than nodes", "link communities naturally incorporate overlap") | yes | yes | no (a dendrogram cut) | yes |
| BigCLAM (Yang and Leskovec 2013, WSDM, DOI 10.1145/2433396.2433471: "nodes belong to multiple clusters at once", "overlaps between communities are densely connected") | yes (affiliation weights) | yes | K chosen by held-out likelihood | fitted to the graph, not grown |
| Bayesian NMF (Psorakis et al. 2011) | yes | yes ("soft-partitioning") | no (relevance determination) | fitted, not grown |
| affinity propagation (Frey and Dueck 2007) | no (one exemplar) | **no** | no | similarity-based |
| multi-exemplar AP (Wang et al. 2013) | yes | **no** | no | similarity-based |
| multiple local communities of one seed (Kamuhanda, Wang and He 2020, IEEE Trans Comput Soc Syst 7(5):1220-1233: "a seed member usually belongs to multiple local overlapping communities"; PPR sampling then sparse NMF) | yes | yes | no (per seed) | yes, PPR |
| IBP latent features (Griffiths and Ghahramani 2011; Knowles and Ghahramani 2011 for genes; Yu et al. 2020 for communities) | yes | yes | no | no |
| HotNet2 (section 1.1) | yes | no (components are disjoint) | no | yes |

So the forms that satisfy both of the owner's requirements (several seeds per module, overlap) are the affiliation
and NMF family, link communities, Kamuhanda's seed-local form and the IBP; plain and multi-exemplar affinity
propagation do not, and HotNet2's components do not overlap. The exemplar-with-merge form of 10.2(b) sits in the
affiliation family with the membership grown rather than fitted, which is the combination not found published.


## 11. BibTeX for the new sources

Keys checked against `docs/references.bib` at 16a3c847: none of the 24 below exists there. Already present and not
repeated: `ref24_cowen2017` (its fields were verified against the PubMed record today: Cowen, Ideker, Raphael and
Sharan, Nat Rev Genet 18(9):551-562, 2017, PMID 28607512, DOI 10.1038/nrg.2017.38, all as the entry has them, the
author list abbreviated "and others"), `choobdar2019assessment` (verified: Nat Methods 16(9):843-852, 2019, PMID
31471613, which the entry lacks), `huang2018systematic`, `lotfollahi2023biologically`, `ref26_welling2018`. Journal
fields are from the PubMed record and confirmed against Europe PMC; conference and non-PubMed fields from the
proceedings page or the Crossref record, as each note says. A field the records did not supply is absent. The two
ICLR papers of section 1.3 get no entry (venue unverified today).

```bibtex
@article{leiserson2015pancancer,
  author  = {Leiserson, Mark D. M. and Vandin, Fabio and Wu, Hsin-Ta and Dobson, Jason R. and Eldridge, Jonathan V. and Thomas, Jacob L. and Papoutsaki, Alexandra and Kim, Younhun and Niu, Beifang and McLellan, Michael and Lawrence, Michael S. and Gonzalez-Perez, Abel and Tamborero, David and Cheng, Yuwei and Ryslik, Gregory A. and Lopez-Bigas, Nuria and Getz, Gad and Ding, Li and Raphael, Benjamin J.},
  title   = {Pan-cancer network analysis identifies combinations of rare somatic mutations across pathways and protein complexes},
  journal = {Nature Genetics},
  year    = {2015},
  volume  = {47},
  number  = {2},
  pages   = {106--114},
  doi     = {10.1038/ng.3168},
  pmid    = {25501392},
  note    = {FULL TEXT READ (PMC4444046, through the PubMed connector on Fable on 7 November 2026); fields from the PubMed record and confirmed against Europe PMC (PubMed dates the record 15 December 2014, Europe PMC gives the issue year 2015, used here). HotNet2: "an insulated heat diffusion process", "a directed heat diffusion model"; "nodes in the graph pass to and receive heat from their neighbors, but also retain a fraction of their heat, governed by an insulating parameter"; "The insulated heat model can also described in terms of a random walk with restart"; undirected diffusion gives "'hot' stars determined by a single high-scoring node and the immediate neighbors of this node" and "HotNet2 returns >80% fewer hot stars/spiders than HotNet". The spread parameter is set from the network, not learned; subnetworks are disjoint strongly connected components}
}

@article{menche2015uncovering,
  author  = {Menche, J{\"o}rg and Sharma, Amitabh and Kitsak, Maksim and Ghiassian, Susan Dina and Vidal, Marc and Loscalzo, Joseph and Barab{\'a}si, Albert-L{\'a}szl{\'o}},
  title   = {Disease networks. {Uncovering} disease-disease relationships through the incomplete interactome},
  journal = {Science},
  year    = {2015},
  volume  = {347},
  number  = {6224},
  pages   = {1257601},
  doi     = {10.1126/science.1257601},
  pmid    = {25700523},
  note    = {FULL TEXT READ (the PMC author manuscript PMC4435741, through the PubMed connector on Fable on 7 November 2026); fields from the PubMed record and confirmed against Europe PMC. The disease-module hypothesis and its test: "disease genes associated with 226 of the 299 diseases show a statistically significant tendency to form disease modules"; "their observable modules comprising on average only 20% of the respective disease genes"; "while ~80% of the disease proteins are disconnected from the observable module, these isolates tend to be localized in its network vicinity"; "for diseases with fewer than ~25 genes, the module is too fragmented to be observable in the current interactome". The separation measure s_AB is the post-hoc comparison of a grown module with a curated set proposed in the graph-grown supports pass}
}

@article{vanunu2010associating,
  author  = {Vanunu, Oron and Magger, Oded and Ruppin, Eytan and Shlomi, Tomer and Sharan, Roded},
  title   = {Associating genes and protein complexes with disease via network propagation},
  journal = {PLoS Computational Biology},
  year    = {2010},
  volume  = {6},
  number  = {1},
  pages   = {e1000641},
  doi     = {10.1371/journal.pcbi.1000641},
  pmid    = {20090828},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC2797085). PRINCE: "constraints on the prioritization function that relate to its smoothness over the network and usage of prior information"; motivated by "the observation that genes causing the same or similar diseases tend to lie close to one another in a network"}
}

@article{kohler2008walking,
  author  = {K{\"o}hler, Sebastian and Bauer, Sebastian and Horn, Denise and Robinson, Peter N.},
  title   = {Walking the interactome for prioritization of candidate disease genes},
  journal = {American Journal of Human Genetics},
  year    = {2008},
  volume  = {82},
  number  = {4},
  pages   = {949--958},
  doi     = {10.1016/j.ajhg.2008.02.013},
  pmid    = {18371930},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC2427257). Random walk with restart for disease genes; the results "add weight to the assumption that phenotypically similar diseases are associated with disturbances of subnetworks within the larger protein interactome that extend beyond the disease proteins themselves"}
}

@article{ghiassian2015diamond,
  author  = {Ghiassian, Susan Dina and Menche, J{\"o}rg and Barab{\'a}si, Albert-L{\'a}szl{\'o}},
  title   = {A {DIseAse} {MOdule} {Detection} ({DIAMOnD}) algorithm derived from a systematic analysis of connectivity patterns of disease proteins in the human interactome},
  journal = {PLoS Computational Biology},
  year    = {2015},
  volume  = {11},
  number  = {4},
  pages   = {e1004120},
  doi     = {10.1371/journal.pcbi.1004120},
  pmid    = {25853560},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC4390154). "disease associated proteins do not reside within locally dense communities and instead identify connectivity significance as the most predictive quantity"; a warning against kernels that reward density}
}

@article{picartarmada2019benchmarking,
  author  = {Picart-Armada, Sergio and Barrett, Steven J. and Will{\'e}, David R. and Perera-Lluna, Alexandre and Gutteridge, Alex and Dessailly, Benoit H.},
  title   = {Benchmarking network propagation methods for disease gene identification},
  journal = {PLoS Computational Biology},
  year    = {2019},
  volume  = {15},
  number  = {9},
  pages   = {e1007276},
  doi     = {10.1371/journal.pcbi.1007276},
  pmid    = {31479437},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC6743778). "diffusion-based prioritisers and machine learning applied to diffusion-based features are suited for drug discovery in practice and improve over simpler neighbour-voting methods"; "Standard cross-validation led to over-optimistic performance estimates due to the presence of protein complexes"}
}

@inproceedings{agrawal2018largescale,
  author    = {Agrawal, Monica and Zitnik, Marinka and Leskovec, Jure},
  title     = {Large-scale analysis of disease pathways in the human interactome},
  booktitle = {Pacific Symposium on Biocomputing},
  year      = {2018},
  volume    = {23},
  pages     = {111--122},
  doi       = {10.1142/9789813235533_0011},
  pmid      = {29218874},
  note      = {Peer reviewed (PSB programme committee; decision 9.101). ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC (PMC5731453), which supplies the DOI the PubMed record lacks. The counter-finding to the disease-module hypothesis: "90% of pathways do not correspond to single well-connected components in the PPI network"; "network connectivity structure alone may not be sufficient for disease pathway discovery"}
}

@article{barabasi2011network,
  author  = {Barab{\'a}si, Albert-L{\'a}szl{\'o} and Gulbahce, Natali and Loscalzo, Joseph},
  title   = {Network medicine: a network-based approach to human disease},
  journal = {Nature Reviews Genetics},
  year    = {2011},
  volume  = {12},
  number  = {1},
  pages   = {56--68},
  doi     = {10.1038/nrg2918},
  pmid    = {21164525},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 (PMC3140052). The programme behind the disease-module hypothesis: network medicine leads "to the identification of disease modules and pathways"}
}

@inproceedings{gasteiger2019diffusion,
  author    = {Gasteiger, Johannes and Wei{\ss}enberger, Stefan and G{\"u}nnemann, Stephan},
  title     = {Diffusion Improves Graph Learning},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2019},
  volume    = {32},
  url       = {https://papers.nips.cc/paper_files/paper/2019/hash/23c894276a2c5a16470e6a31f4618d73-Abstract.html},
  note      = {Peer reviewed (NeurIPS 2019 programme committee; decision 9.101); NeurIPS registers no DOI. ABSTRACT ONLY HELD, read on the proceedings page with experiments/read_public_page.py on Fable on 7 November 2026 (SHA-256 de6a18f47fe99dc9...); the author list is as the proceedings page prints it (the first author published earlier as Klicpera). Graph diffusion convolution "leverages generalized graph diffusion, examples of which are the heat kernel and personalized PageRank"; the kernel is precomputed and sparsified and the spread is tuned, not learned}
}

@inproceedings{zhao2021adaptive,
  author    = {Zhao, Jialin and Dong, Yuxiao and Ding, Ming and Kharlamov, Evgeny and Tang, Jie},
  title     = {Adaptive Diffusion in Graph Neural Networks},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2021},
  volume    = {34},
  pages     = {23321--23333},
  url       = {https://proceedings.neurips.cc/paper/2021/hash/c42af2fa7356818e0389593714f59b52-Abstract.html},
  note      = {Peer reviewed (NeurIPS 2021 programme committee; decision 9.101); NeurIPS registers no DOI. ABSTRACT ONLY HELD, read on the proceedings page with experiments/read_public_page.py on Fable on 7 November 2026 (SHA-256 55581fa366c46665...). "the neighborhood size in GDC is manually tuned for each graph"; ADC learns "the optimal neighborhood size from the data" and "a dedicated propagation neighborhood for each GNN layer and each feature channel": the published form of a learned spread per module}
}

@article{berberidis2019adaptive,
  author  = {Berberidis, Dimitris and Nikolakopoulos, Athanasios N. and Giannakis, Georgios B.},
  title   = {Adaptive Diffusions for Scalable Learning Over Graphs},
  journal = {IEEE Transactions on Signal Processing},
  year    = {2019},
  volume  = {67},
  number  = {5},
  pages   = {1307--1321},
  doi     = {10.1109/TSP.2018.2889984},
  note    = {ABSTRACT ONLY HELD, from the Consensus search record, with every field from the Crossref record read with experiments/read_public_page.py on Fable on 7 November 2026 (not indexed by PubMed). "learning class-specific diffusion functions adapted to the underlying network topology", through "'landing probabilities' of class-specific random walks": a learned diffusion per class, the analogue of one learned kernel per module}
}

@article{rissanen1978modeling,
  author  = {Rissanen, J.},
  title   = {Modeling by shortest data description},
  journal = {Automatica},
  year    = {1978},
  volume  = {14},
  number  = {5},
  pages   = {465--471},
  doi     = {10.1016/0005-1098(78)90005-5},
  note    = {Crossref record only (read with experiments/read_public_page.py on Fable on 7 November 2026; not in PubMed); the text was not read and nothing is quoted from it. The origin of the two-part code the module-size analysis of the graph-grown supports pass uses}
}

@article{hansen2001model,
  author  = {Hansen, Mark H. and Yu, Bin},
  title   = {Model Selection and the Principle of Minimum Description Length},
  journal = {Journal of the American Statistical Association},
  year    = {2001},
  volume  = {96},
  number  = {454},
  pages   = {746--774},
  doi     = {10.1198/016214501753168398},
  note    = {Crossref record only (read with experiments/read_public_page.py on Fable on 7 November 2026; not in PubMed); the text was not read and nothing is quoted from it. The review of two-part and mixture MDL codes}
}

@article{griffiths2011indian,
  author  = {Griffiths, Thomas L. and Ghahramani, Zoubin},
  title   = {The {Indian} Buffet Process: An Introduction and Review},
  journal = {Journal of Machine Learning Research},
  year    = {2011},
  volume  = {12},
  number  = {32},
  pages   = {1185--1224},
  url     = {https://www.jmlr.org/papers/v12/griffiths11a.html},
  note    = {ABSTRACT ONLY HELD, read on the JMLR page with experiments/read_public_page.py on Fable on 7 November 2026 (SHA-256 eb3eba3686ec6594...); JMLR registers no DOI for this volume. "a probability distribution over equivalence classes of sparse binary matrices with a finite number of rows and an unbounded number of columns": overlapping latent features with an unbounded count}
}

@article{knowles2011nonparametric,
  author  = {Knowles, David and Ghahramani, Zoubin},
  title   = {Nonparametric {Bayesian} sparse factor models with application to gene expression modeling},
  journal = {The Annals of Applied Statistics},
  year    = {2011},
  volume  = {5},
  number  = {2B},
  pages   = {1534--1552},
  doi     = {10.1214/10-AOAS435},
  note    = {Crossref record only (read with experiments/read_public_page.py on Fable on 7 November 2026; not in PubMed); the text was not read and nothing is quoted from it beyond the title. The Indian buffet process applied to gene modules (sparse factors over genes)}
}

@article{frey2007clustering,
  author  = {Frey, Brendan J. and Dueck, Delbert},
  title   = {Clustering by passing messages between data points},
  journal = {Science},
  year    = {2007},
  volume  = {315},
  number  = {5814},
  pages   = {972--976},
  doi     = {10.1126/science.1136800},
  pmid    = {17218491},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC. Affinity propagation: "Clustering data by identifying a subset of representative examples"; "Real-valued messages are exchanged between data points until a high-quality set of exemplars and corresponding clusters gradually emerges". Assigns each point to one exemplar, so it does not give overlapping modules}
}

@article{wang2013multiexemplar,
  author  = {Wang, Chang-Dong and Lai, Jian-Huang and Suen, Ching Y. and Zhu, Jun-Yong},
  title   = {Multi-Exemplar Affinity Propagation},
  journal = {IEEE Transactions on Pattern Analysis and Machine Intelligence},
  year    = {2013},
  volume  = {35},
  number  = {9},
  pages   = {2223--2237},
  doi     = {10.1109/TPAMI.2013.28},
  note    = {Crossref record only (read with experiments/read_public_page.py on Fable on 7 November 2026; not in PubMed); the text was not read and nothing is quoted from it beyond the title. Affinity propagation with several exemplars per cluster; still a hard assignment of points}
}

@article{airoldi2008mixed,
  author  = {Airoldi, Edoardo M. and Blei, David M. and Fienberg, Stephen E. and Xing, Eric P.},
  title   = {Mixed Membership Stochastic Blockmodels},
  journal = {Journal of Machine Learning Research},
  year    = {2008},
  volume  = {9},
  number  = {65},
  pages   = {1981--2014},
  url     = {https://www.jmlr.org/papers/v9/airoldi08a.html},
  note    = {ABSTRACT ONLY HELD, read on the JMLR page with experiments/read_public_page.py on Fable on 7 November 2026 (SHA-256 1b4ad2c2a78fb2ae...); JMLR registers no DOI for this volume. Each node holds a membership distribution over blocks: overlap with K preset}
}

@inproceedings{yang2013overlapping,
  author    = {Yang, Jaewon and Leskovec, Jure},
  title     = {Overlapping community detection at scale: a nonnegative matrix factorization approach},
  booktitle = {Proceedings of the sixth ACM international conference on Web search and data mining (WSDM 2013)},
  year      = {2013},
  pages     = {587--596},
  publisher = {ACM},
  doi       = {10.1145/2433396.2433471},
  note      = {Peer reviewed (WSDM 2013 programme committee; decision 9.101). ABSTRACT ONLY HELD, from the Consensus search record, with every field from the Crossref record read with experiments/read_public_page.py on Fable on 7 November 2026 (the Crossref title is the short form "Overlapping community detection at scale"; the subtitle is as Consensus prints it). BigCLAM: "nodes belong to multiple clusters at once"; "overlaps between communities are densely connected"}
}

@article{psorakis2011overlapping,
  author  = {Psorakis, Ioannis and Roberts, Stephen and Ebden, Mark and Sheldon, Ben},
  title   = {Overlapping community detection using {Bayesian} non-negative matrix factorization},
  journal = {Physical Review E},
  year    = {2011},
  volume  = {83},
  number  = {6 Pt 2},
  pages   = {066114},
  doi     = {10.1103/PhysRevE.83.066114},
  pmid    = {21797448},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC. "a Bayesian non-negative matrix factorization model to extract overlapping modules from a network", with "soft-partitioning solutions, assignment of node participation scores to modules": an overcomplete factorisation pruned to the number of modules the data support}
}

@article{ahn2010link,
  author  = {Ahn, Yong-Yeol and Bagrow, James P. and Lehmann, Sune},
  title   = {Link communities reveal multiscale complexity in networks},
  journal = {Nature},
  year    = {2010},
  volume  = {466},
  number  = {7307},
  pages   = {761--764},
  doi     = {10.1038/nature09182},
  pmid    = {20562860},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC. "we reinvent communities as groups of links rather than nodes"; "link communities naturally incorporate overlap while revealing hierarchical organization"; found "in many networks, including major biological networks such as protein-protein interaction and metabolic networks"}
}

@article{palla2005uncovering,
  author  = {Palla, Gergely and Der{\'e}nyi, Imre and Farkas, Ill{\'e}s and Vicsek, Tam{\'a}s},
  title   = {Uncovering the overlapping community structure of complex networks in nature and society},
  journal = {Nature},
  year    = {2005},
  volume  = {435},
  number  = {7043},
  pages   = {814--818},
  doi     = {10.1038/nature03607},
  pmid    = {15944704},
  note    = {ABSTRACT ONLY HELD, read from the PubMed record on Fable on 7 November 2026 and confirmed against Europe PMC. Clique percolation: "The existing deterministic methods used for large networks find separated communities, whereas most of the actual networks are made of highly overlapping cohesive groups of nodes"}
}

@article{kamuhanda2020sparse,
  author  = {Kamuhanda, Dany and Wang, Meng and He, Kun},
  title   = {Sparse Nonnegative Matrix Factorization for Multiple-Local-Community Detection},
  journal = {IEEE Transactions on Computational Social Systems},
  year    = {2020},
  volume  = {7},
  number  = {5},
  pages   = {1220--1233},
  doi     = {10.1109/TCSS.2020.3008860},
  note    = {ABSTRACT ONLY HELD, from the Consensus search record (which labels it a preprint; the Crossref record read with experiments/read_public_page.py on Fable on 7 November 2026 types it a journal article in the October 2020 issue, so it is cited as peer reviewed). "a seed member usually belongs to multiple local overlapping communities"; "local sampling with Personalized PageRank (PPR)" then sparse NMF: the published form of several overlapping modules grown from one seed}
}

@article{yu2020estimating,
  author  = {Yu, Qianchen and Yu, Zhiwen and Wang, Zhu and Wang, Xiaofeng and Wang, Yongzhi},
  title   = {Estimating posterior inference quality of the relational infinite latent feature model for overlapping community detection},
  journal = {Frontiers of Computer Science},
  year    = {2020},
  volume  = {14},
  number  = {6},
  doi     = {10.1007/s11704-020-9370-z},
  note    = {ABSTRACT ONLY HELD, from the Consensus search record, with every field from the Crossref record read with experiments/read_public_page.py on Fable on 7 November 2026 (not in PubMed; the record gives no page range). The Indian buffet process on the community assignment matrix, "which can allow K to increase as more and more data are encountered instead of to be fixed in advance"}
}
```

---

## Added 7 November 2026

Committed as a record the same day at the owner's request ("Commit it with the bib entries"), unchanged except for the
model line and the sentence naming where the measuring script was kept. Since the pass reported, decision 9.119 has
recorded: that the earlier pass's 42,389 reached and 7,445 unreached nodes were not reproduced here (39,483 and 10,351),
both counts standing until the difference is traced; the owner's caveat that "The current graph is incomplete", so the
connectivity counts of sections 1 and 2 are properties of v5 and are to be measured again on the graph the
confirmatory run uses; and a proposed path requirement with an end defined by the data, reported as a check on fitted
modules. None of the ten questions of section 8 has been ruled.
