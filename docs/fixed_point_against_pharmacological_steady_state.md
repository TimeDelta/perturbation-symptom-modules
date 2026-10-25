Model self-report: claude-fable-5-1 (Fable 5.1)

# The fixed point against the pharmacological steady state: clocks, invariances and which equilibrium each label reads

Prepared 21 October 2026 for the owner of perturbation-symptom-modules, in answer to: "What about the fact that the fixed point isn't the pharmacological steady state? It's the final settling of the physiology as a whole. How does that play into this?"

What this builds on. `docs/steady_state_readout_alternatives.md` (20 October 2026, 36 references) is taken as read; its diagnosis of what a fixed-point readout cannot say (its section 1) and its ranking of readout alternatives (its section 2) are not repeated. A reference from that file is cited as [P n], where n is its number there. New references are numbered [1], [2], ... in order of first appearance and listed at the end. Every quoted sentence about physiology or pharmacology is from an abstract read through PubMed on 21 October 2026, except the one FDA label sentence, which is from DailyMed, and the three applied-mathematics references marked "not verified through PubMed". Repository facts are from the files named, read at commit 5d56153: `mechanistic_pathway_learning/models/linear_response_encoder.py`, `experiments/measure_propagation_convergence.py`, `docs/tissue_saturation.md`, `docs/linear_response_sign_check.md`, `docs/drug_entry_nodes.md` section F, `docs/physiological_adherence_review.md`, `docs/research_summary.md` and `docs/gene_protein_split.md`.

Notation. N nodes. S_r is the signed in-degree-normalised adjacency of relation r and g_r its learned gain; G = sum_r g_r S_r is the dimensionless gain operator (the prior report's A_c). d is the damping (0.5), u the sustained input, h(t) the state after t rounds. The registered update is

    h(t + 1) = (1 - d) h(t) + d (G h(t) + u),

with fixed point h* = (I - G)^(-1) u. D = diag(kappa_1, ..., kappa_N) is a diagonal matrix of relaxation rates with units of 1/time; A is a coupling matrix with units of 1/time; y is the state in fractional (logarithmic) coordinates, y_i = delta x_i / x_i. T is the dosing interval, omega_0 = 2 pi / T, m a harmonic index. F and S are the fast and slow node sets of a partition, t_obs the time from exposure onset at which a label is observed.

## 0. The answer in brief

The owner's distinction is real and it has a formal home in pharmacokinetic-pharmacodynamic modelling: the concentration reaches its steady state on the drug's elimination clock and the response reaches its own steady state on the response's turnover clock; the two differ (section 1). But the distinction does not enter where the owner may expect. The fixed point of a first-order system written in fractional coordinates depends on the ratio of each coupling to the destination's own relaxation rate and on nothing else about the rates. The encoder's gains are those ratios. So no assignment of relaxation rates to nodes, however heterogeneous, moves any fixed point the encoder computes; the repository's sentence "rates drop out at a steady state" is correct, and the cancellations behind the 0.615 sign-check result (0.593 at convergence) are untouched by rates (section 2). Rates enter in two places only: they decide which nodes have relaxed by the time a label is observed, which turns one fixed point into two or three nested ones (section 3), and they set how much of the dosing swing each node sees, which the fixed point of the mean dose discards (section 4). The germline laboratory labels read the full fixed point and the owner's framing does not help there. Chronic late-onset drug labels read the full fixed point of the mean dose, and what that fixed point lacks is the adaptation loops the graph does not contain, not a time axis. Acute drug labels read the fixed point of the fast subsystem with transcription and translation frozen, evaluated at the peak concentration; that object costs one masked fixed-point loop and zero new parameters, and it is the one change in this report that the owner's framing earns.

## 1. Three clocks, and what a propagation step is in time

The model conflates three clocks. Each is stated with its order of magnitude and a source.

### 1.1 The forcing's clock: pharmacokinetic steady state

Under repeated dosing with first-order elimination, the amount in the body after n elimination half-lives is 1 - 2^(-n) of its steady-state value: 0.90 at n = 3.3, 0.97 at n = 5, 0.99 at n = 7. This is the accumulation that Greenblatt describes: "During multiple dosage, elimination half-life does have value in predicting the rate and relative extent of drug accumulation, as well as the rate of washout after termination of treatment" [1]. The same source warns that half-life is not the clock of a single dose: "Half-life also has limitations as a predictor of a drug's duration of pharmacologic action after single doses, which is related more to distribution than to elimination or clearance" [1]. For the study drugs the elimination clock runs from hours to weeks: quetiapine "is eliminated with a mean terminal half-life of approximately 7 hours" with "median time to reach maximum observed plasma concentration ranging from 1 to 2 hours" [2]; among the SSRIs "their half-lives range between 1 and 4 days for fluoxetine (7 and 15 days for norfluoxetine) and between 21 (paroxetine) and 36 (citalopram) hr for the other SSRIs" [3]. Five half-lives is therefore 1.5 days for quetiapine, a week for citalopram and five to eleven weeks for norfluoxetine.

The pharmacokinetic steady state is a property of the input u(t), not of the network. In the encoder u is held constant from round 0, which is the limit of a drug already at its mean steady-state concentration with the swing between doses removed (section 4).

### 1.2 The network's clocks: relaxation rates by node class

In pharmacodynamics the separation the owner is pointing at is the indirect response model, in which the response has a turnover rate of its own: Jusko and Ko argue that such models "may be more appropriate for diverse drugs when time lags exist between plasma or biophase drug concentrations and the time course of pharmacodynamic responses" [4] [P26]. The response's loss rate constant k_out in those models is exactly a diagonal entry of D. The graph has thousands of such entries, one per node, and they span at least ten orders of magnitude:

| node class in the graph | process that relaxes it | relaxation time | source |
|---|---|---|---|
| extracellular transmitter pool at a synapse | clearance and diffusion | about 1 ms: glutamate "decayed with a time constant of 1.2 milliseconds at cultured hippocampal synapses" | [5] |
| membrane potential, channel conductance states | gating, passive membrane | milliseconds (textbook; not sourced here) | |
| receptor occupancy by a drug | dissociation rate | seconds to minutes, drug specific; not sourced here | |
| intracellular metabolite pool | turnover = pool / flux | seconds to tens of minutes; the glutamate-glutamine cycle runs at "0.32 +/- 0.05 micromol/min/g" in human cortex [6], which against a tissue glutamate pool of the order of 10 micromol/g (the figure the same group's models use; not quoted here) gives a turnover time of about 30 minutes; metabolic networks show "a temporal hierarchy of events that range from chemical equilibration events to the formation of physiologically meaningful pools" | [6] [7] |
| receptor surface pool (sequestration and recycling) | endocytosis and recycling | tens of minutes: for the beta2-adrenergic receptor "the rate constant of agonist-induced sequestration was 0.03/min; the rate constant of receptor recycling was 0.06/min" (time constants 33 and 17 min); internalised receptors "were detected in cells within 2 min of agonist addition" | [8] [9] |
| transcript (gene node of the split graph) | mRNA decay | hours; "transcription factor mRNAs have increased average decay rates compared with other transcripts and are enriched in 'fast-decaying' mRNAs with half-lives <2 h", biosynthetic mRNAs are slower; genome-wide medians of several hours in mammalian cells | [10] [11] |
| protein abundance (protein node) | degradation and resynthesis | days: "Proteins in the brain have significantly slower turnover (average lifetime of 9.0 d) compared with those of the liver (3.0 d) and blood (3.5 d)", with turnover rates "spanning four orders of magnitude" across about 2,500 proteins [12]; in neuronal culture half-lives range "from <1 to >20 days" and "membrane proteins were relatively shorter-lived" [13]; about 3,500 brain protein lifetimes are tabulated in vivo | [12] [13] [14] |
| receptor density adaptation to chronic occupancy | synthesis and trafficking set point | weeks: a 20 to 25 percent rise in striatal dopamine receptor binding after chronic antipsychotic treatment [P6]; 5-HT1A autoreceptor desensitisation over about two weeks [P8] | |
| structural lipid (myelin cholesterol) | recycling with "minimal losses to the circulation" | months to years (the review's half-life estimate is in its text rather than its abstract and is not quoted here) | [15] |

Two consequences. First, "metabolite" is not one rate class: synaptic glutamate relaxes in a millisecond and myelin cholesterol in years, so any rate scheme that assigns one number per node type is wrong by orders of magnitude inside the metabolite class, and any scheme that needs the numbers must get them per node (section 5, R4). Second, the slowest process class the operator represents is translation into protein abundance (days), structural lipid pools aside, and the slowest process the physiology shows under chronic drugs is receptor density adaptation (weeks), which the graph does not represent at all ("no closed adaptation loop for any psychiatric receptor", docs/missing_physiology_review.md section 4, as quoted in the prior report 1.1). So the network's clock to its own fixed point is weeks for most drugs, slower than the pharmacokinetic clock of every study drug except fluoxetine and norfluoxetine, and the "final settling of the physiology as a whole" is slower still and runs through processes the operator lacks.

### 1.3 The label's clock: observation time relative to exposure onset

The germline laboratory labels of docs/linear_response_sign_check.md are measured in patients whose perturbation has been present for life, so t_obs is effectively infinite relative to every relaxation time in the table (a scope exception, episodic decompensation, is in 3.1). The drug labels have no stated t_obs ("No temporal field anywhere", docs/missing_physiology_review.md, as cited in the prior report 2.4) and in reality they spread over the whole range:

| adverse event in the MedDRA label set | observation time after onset | source |
|---|---|---|
| orthostatic hypotension with quetiapine | within hours of a dose (the peak is at 1 to 2 hours [2]), concentrated "especially during the initial dose-titration period" | FDA label text via DailyMed [16] |
| extrapyramidal symptoms with haloperidol | measured at 2 weeks, driven by occupancy at the time: "the likelihood of clinical response, hyperprolactinemia, and extrapyramidal side effects increased significantly as D(2) occupancy exceeded 65%, 72%, and 78%, respectively" | [17] |
| SSRI hyponatraemia | "the median time to onset of hyponatremia was 13 days (range 3 to 120 days)" | [18] |
| clozapine agranulocytosis | of 73 episodes, "61 patients within three months after they began treatment" | [19] |
| tardive dyskinesia | years: "the annualized tardive dyskinesia incidence was 3.9% for second-generation antipsychotics and 5.5% for first-generation antipsychotics" | [20] |

A relieves label from a trial endpoint sits at 6 to 8 weeks for acute trials, after the pharmacokinetic steady state of every study drug but before protein abundance has fully settled for the slowest proteins and before receptor density adaptation has run its course.

### 1.4 What one propagation step is in time

The registered update is forward Euler for

    dh/dtau = -h + G h + u,    tau = kappa t,

with step size delta tau = d = 0.5 in dimensionless time, that is, half of one relaxation time of every node at once. Read exactly rather than through Euler, an isolated node's deviation is multiplied by (1 - d) = 0.5 per round, so one round is exactly one half-life of every node at once, and the registered eight rounds are eight half-lives of every node at once, after which an isolated transient is at 2^(-8) = 0.4 percent. The physical duration of a round is therefore the destination node's half-life: about a millisecond at a synaptic pool node, forty seconds at a metabolite with a one-minute turnover time, twenty minutes at a receptor surface pool, nine hours at a typical transcript (under two at a transcription factor's), six days at an average brain protein. A metabolic edge, a transcription edge and a trafficking edge do not get the same unit of time; each gets its own destination's half-life, and the single damping asserts that all of them advance in lockstep. There is no instant of real time at which a protein has moved eight of its half-lives and a metabolite only eight of its own, so the state after k rounds is not the state of the physiology at any time. It is a damping-weighted partial sum of the walk expansion h* = sum_k G^k u in which the round-k state holds walks of length at most k, a graph-distance cutoff, which is what docs/physiological_adherence_review.md section 14 already says ("the step index separates by graph distance and not by rate") and what docs/tissue_saturation.md measures (median tissue at 0.631 of its settled level by round 8). The convergence in 23 rounds at gain 0.9 (encoder comment at DEFAULT_MAX_PROPAGATION_STEPS) is a property of the gain bound and the normalisation, not of any rate.

One consequence for the number everyone quotes: the 0.615 of finding 10 is the 8-round reading, a truncated walk sum over the 59 percent of pairs it had reached; the fixed-point reading of the same table is 0.593 over 83 percent of pairs against a majority of 0.757 (docs/linear_response_sign_check.md). The steady-state comparison the prior report makes in its 3.1 should quote 0.593 against 0.757, not 0.615 against 0.806. The conclusion does not change; the number does.

## 2. What the fixed point depends on

### 2.1 Two continuous-time parameterisations

Replace the scalar damping by a diagonal relaxation-rate matrix D. There are two ways to write the continuous-time system and they are not equivalent under changes of D.

Parameterisation (a), absolute couplings held fixed:

    dh/dt = -D h + A h + u,    h* = (D - A)^(-1) u,

where A has units of 1/time and does not change when D changes.

Parameterisation (b), dimensionless couplings held fixed:

    dh/dt = D (-h + G h + u_tilde),    h* = (I - G)^(-1) u_tilde,

where G = D^(-1) A is dimensionless and u_tilde = D^(-1) u. The registered update is forward Euler for (b) with D = kappa I and a step kappa delta t = d. The encoder's gains g_r are entries of G, not of A.

### 2.2 Invariance statements

Overall scale of D under (a). Replace D by c D with A and u fixed:

    (c D - A)^(-1) u = (1/c) (I - (1/c) D^(-1) A)^(-1) D^(-1) u = (1/c) sum_k ((1/c) D^(-1) A)^k D^(-1) u.

Every hop is divided by c as well as the input, so long walks are suppressed relative to short ones: the fixed point is not invariant and the change is not a rescaling. In the toy system of 2.6, doubling D lowered every node's value by a factor between 2 and 33, a different factor at each node, so the shape of the fixed point changed and not only its size. The only invariance under (a) is to a change of time unit, D, A and u scaled together.

Heterogeneous ratios under (a). Write (D - A)^(-1) = (I - D^(-1) A)^(-1) D^(-1). A node's row of the hop operator is divided by its own relaxation rate: a slow node integrates its inputs and a fast node attenuates them; the input at a node is likewise divided by that node's rate. With the rates of section 1.2 a protein-abundance node would weigh its inputs about 10^6 times more than a membrane node weighs its own. No steady-state physiology looks like that (a fractional change in an enzyme gives a fractional change of order one in its product, not of order 10^6), which is the first sign that (a) is the wrong reading.

Under (b), any D. The fixed point (I - G)^(-1) u_tilde contains no D. This holds for any positive diagonal D, heterogeneous or not, and it holds for the discrete iteration with any per-node step d_i in (0, 1] that converges: the fixed-point condition h = G h + u_tilde does not contain d_i. It also holds with the encoder's cross-relation mixture in place of the linear G, because the fixed-point condition state = aggregate(state) + u again contains no step size; the mixture is nonlinear but the argument never used linearity, only convergence.

### 2.3 Which parameterisation is physical

The dimensionless one, and the argument is metabolic control analysis, which the encoder cites (Kacser and Burns 1973; Heinrich and Rapoport 1974 [21] [22]). Take a metabolite x_m with stoichiometric coefficients s_mr over reactions r with rates v_r, and linearise about a steady state in fractional coordinates y = delta x / x:

    dy_m/dt = (1/x_m) sum_r s_mr v_r ( sum_j epsilon_rj y_j + pi_r delta E_r / E_r ),

where epsilon_rj = (x_j / v_r) dv_r/dx_j is the elasticity of reaction r to metabolite j and pi_r the elasticity to its enzyme. The diagonal term is minus kappa_m = (1/x_m) sum over consuming reactions of v_c epsilon_cm, the elasticity-weighted turnover of the pool. The off-diagonal term for metabolite j, divided by kappa_m, is

    G_mj = sum_r s_mr v_r epsilon_rj / sum_c v_c epsilon_cm,

with c running over the reactions that consume m: a flux-share-weighted ratio of elasticities, with the pool size x_m cancelled. The turnover rate sets how fast y_m relaxes and nothing about where it relaxes to. Reder's structural theory makes the same point for the whole network: the control matrices are characterised by "properties of the systems which depend only on the structure of the metabolic network, and not on the reaction kinetics" together with the elasticities [23]. The same cancellation holds for a protein with first-order synthesis and degradation (y_protein = y_mRNA at steady state whatever k_deg) and for any first-order node whose inflow and outflow balance at steady state: in fractional coordinates each steady-state equation is dimensionless and its coefficients are elasticities times flux shares.

So the correct reading of the encoder is (b): a gain is the fractional change at the destination per unit fractional change at the source at steady state, which is an elasticity times a flux share, and the registered model's error is that it has one such number per relation for 280,966 edges (docs/physiological_adherence_review.md section 14) and in-degree means in place of flux shares (its section 1), not that it has no rates.

### 2.4 Consequence for "rates drop out"

The repository's sentence "rates drop out at a steady state. With a damped update the settled state satisfies state = update(state) whatever the damping" (docs/drug_entry_nodes.md section F) is correct, and it is correct for a stronger reason than the one given: not only the damping but every physiological relaxation rate drops out of the fixed point once the gains are read as dimensionless steady-state sensitivities, which is the only reading under which the gains are shared across nodes of very different turnover without absurd consequences. The prior report's gloss in its 1.9, "That is correct and it is the whole problem", I disagree with. It is correct and it is not a problem for the fixed point. The problem for the fixed point is the gains (one per relation, means in place of counts, mirror pairs, signs), as the prior report's own 3.1 says one page later. Rates are a problem only for readings that are not the full fixed point, which are sections 3 and 4.

Two further corrections that follow. The time constants tau_k = -1 / ln |mu_k| that the prior report's 2.2 proposes to report are in units of rounds, not time, and the eigenvectors of the uniform-damping operator are not the modes of any physical relaxation; a physical spectrum is that of D (G - I) and needs D. And the prior report's 2.4 writes a per-relation rate k_r into the update; a per-relation rate can change the transient of the full system and nothing else, so as a route to a better steady state it is empty, and as a route to a transient it needs rates per node, not per relation (section 3.4).

### 2.5 Exact cancellations and the sign check

Finding 11 says the aggregate input row sum is exactly zero at 7,811 of 8,460 metabolites that receive both signs, and docs/physiological_adherence_review.md section 2 attributes 15,867 mirror pairs and 1,809 identically silent metabolites to reversible reactions written in both directions. These cancellations are properties of the rows of G. Under (b) a relaxation rate never enters G. Under (a) the row of the hop operator is divided by kappa_m, and kappa_m times zero is zero: the row sum stays zero, so the exact cancellation survives any assignment of node rates under either reading (toy check 7 in 2.6). What breaks it is what the repository has already named: count-preserving normalisation (total_in_degree, decision 4.13), the nominal direction for reversible reactions with product_opposes (amendment item 27, now built according to the adherence review) and edge-specific elasticities.

Could heterogeneous rates move the 0.615 without transient machinery? Under (b), no, by the identity in 2.2: the converged sign agreement (0.593) cannot move by any choice of D. Under (a), yes, but what moves is equivalent to a per-destination-class rescaling of the gains, and since almost every relation in the graph lands on one node class (product_of on metabolites, regulates_transcription_of on genes, catalyzed_by on reactions, encodes on proteins), a per-class rescale is a per-relation rescale, which the model already parameterises and learns. So the honest form of the question is "does any re-weighting of the relation gains move the converged sign agreement?", and that is a sweep that costs minutes (section 5, R1). The 8-round number 0.615 can be moved by rates, because a truncated walk sum is a transient and per-node step sizes change which terms it holds, but moving a transient to fit a label that is a steady state fits an artifact.

### 2.6 Numerical confirmation

A seven-node signed toy (drug target activity, a metabolite, a reaction node, a two-sign metabolite, a transcript, a protein abundance, a membrane-potential-like node) with rates from 3.6 x 10^6 per hour (membrane) to 1/(216 h) (protein) was run with `experiments/fixed_point_rate_checks.py` (numpy only; every number quoted below is printed by it). With dimensionless gains fixed, the fixed point under uniform damping and under per-node steps spanning the full rate range agreed to the solver tolerance (2 x 10^-9). With absolute couplings fixed and D doubled, every node moved and the ratios between nodes changed (for example the protein node fell from -0.099 to -0.003 while the target fell from -1.03 to -0.50). The two-sign row sum stayed zero under row scaling. The sections below use the same toy for the partition and the frequency response.

## 3. Which equilibrium each label class reads

### 3.1 Germline variant with an HPO laboratory abnormality

The forcing is constant for life (no harmonics), t_obs exceeds every relaxation time and every process the operator represents has settled. The right object is the full fixed point h* = (I - G)^(-1) u, read in fractional coordinates, and it is the object the sign check already reads at 32 and 128 rounds (0.596 and 0.593). The owner's distinction does not bear on this label class, and section 2 says no rate assignment can change this number. Two scope limits remain, neither about rates: a developmental residue is not a steady state of the adult graph (prior report 1.8), and some laboratory terms are measured at episodic decompensation (fasting, infection), which is the fixed point under a second forcing the model does not represent.

### 3.2 Chronic exposure with a late-onset adverse event

The forcing is periodic with mean c_bar u and harmonics (section 4); t_obs runs from weeks (hyponatraemia at 13 days [18]) to years (tardive dyskinesia [20]). At the nodes where such events are generated, slow ones, the harmonics are attenuated to a few percent (section 4.3), so the right object is the full fixed point of the mean forcing. That is the object the encoder computes now, and what it lacks for this class is not time but process: receptor density adaptation, desensitisation loops and supersensitivity are state that persists after the drug and gains that depend on state ([P6] [P7] [P5]; prior report 1.2 and 1.4), none of which is in G. For tardive dyskinesia the operator has no process on the relevant clock at all. The fix for this class is the loop curation of the prior report's 2.5, after which the full fixed point becomes the right object; a time axis adds nothing to it.

### 3.3 Single or early dose with an acute adverse event

The forcing is one pulse (or the first few), observed at t_obs of one to a few hours (sedation and orthostasis near the 1 to 2 hour peak of quetiapine [2] [16]). Transcription and translation have not moved; metabolite pools, binding, channel states and second messengers have fully relaxed; the receptor surface pool (17 to 33 minutes [8]) is at the margin. The right object is not an early round of the uniform-damping iteration, which is a graph-distance cutoff (1.4), and it is not an early time point of a full-system simulation either, because that needs rates per node that we have only to an order of magnitude. It is the quasi-steady state of the fast subsystem with the slow variables held at baseline, evaluated at the concentration at t_obs. This is the singular perturbation limit and it is exact as the ratio of slow to fast rates goes to zero; the formal statement and the computation follow.

### 3.4 The formal partition and the computation

Partition the nodes into F (every incoming process has relaxation time much shorter than t_obs) and S (every incoming process has relaxation time much longer than t_obs), with small parameter

    epsilon = max over S of kappa / min over F of kappa.

In block form, parameterisation (b) reads

    dy_F/dt = D_F ( -y_F + G_FF y_F + G_FS y_S + u_F ),
    dy_S/dt = D_S ( -y_S + G_SF y_F + G_SS y_S + u_S ).

Tikhonov's theorem (singular perturbation; Tikhonov 1952, Kokotovic, Khalil and O'Reilly 1986 [24], not verified through PubMed) gives, for times t with 1 / kappa_F << t << 1 / kappa_S and y_S(0) = 0 at baseline, the fast layer

    y_F -> y_F^acute = (I - G_FF)^(-1) u_F,

provided I - G_FF is invertible with the fast subsystem stable, which the contraction supplies since a principal submatrix of an operator with absolute row sums below 0.9 has absolute row sums below 0.9. This is Michaelis and Menten's device applied to the network: "part of a system is assumed to be operating sufficiently fast compared to the rest so that it may be taken to have reached a steady state. This allows, in principle, the fast components to be eliminated" [25]; the quasi-steady-state assumption's validity conditions are set out by Segel and Slemrod (SIAM Review 1989 [26], not verified through PubMed). On the slow time scale the fast variables ride on the slow ones, y_F = (I - G_FF)^(-1) (u_F + G_FS y_S), and the reduced slow system is

    dy_S/dt = D_S ( -(I - G_SS - G_SF (I - G_FF)^(-1) G_FS) y_S + u_S + G_SF (I - G_FF)^(-1) u_F ),

whose fixed point is, by the Schur complement identity, the S block of the full fixed point (toy check 3: identical to six decimals). So the full fixed point is the end of the slow layer and the acute fixed point is the end of the fast layer; the two are nested solutions of the same operator with the same gains. Rates enter only through membership in F and S.

One point about node semantics that the prior report's 2.4 and the repository's section F proposal get right between them. In the split graph a protein node carries two processes: its activity moves within seconds when a drug binds or a metabolite binds (fast), and its abundance moves over days through the encodes edge (slow). Writing y_protein = y_fast + y_slow with each component relaxing at its own rate, the acute layer sets y_slow = 0, which deletes the encodes edge into the protein while keeping the node active for binding, activation and catalysis. So the acute partition is by process, that is by relation, and a node is clamped at baseline only when all of its incoming processes are slow (a gene node, whose only inputs are transcription edges). Freezing the slow relations' gains, as section F proposed, is the correct computation; the prior report's 2.4 framing of it as "two equilibria" is correct; a partition by node alone would be wrong for the protein node and right only for the gene node. In the present graph the slow relations are regulates_transcription_of and encodes; when the trafficking and desensitisation relations of the prior report's 2.5 exist they form an intermediate class (tens of minutes to hours) and a third equilibrium.

The band. Nodes whose relaxation time is within an order of magnitude of t_obs (the receptor surface pool and the fastest transcription-factor transcripts for a two-hour label) are in neither layer. For a first-order node the error of assigning it to the fast side is (1 - e^(-kappa t_obs)) short of its own fixed point, and of assigning it to the slow side e^(-kappa t_obs) of that fixed point; assign each to the nearer side in log time and record the bound. Only for the band would an explicit transient be worth computing, and it is a few hundred nodes, not the graph.

Tikhonov check on the toy. The full heterogeneous-rate system integrated from baseline sits on the acute fixed point at one hour (every fast node within 10^-5, transcript at 7 percent of its final value, protein at 0.02 percent), between the two at one day (transcript at 82 percent, protein at 6 percent) and on the full fixed point at a hundred days. The acute and full readings differed by 3 percent at the target and by 10 percent at the membrane node; a sign difference between them is possible when a slow indirect route opposes a weak direct one, and the contraction does not forbid it.

The computation, as a change to the existing loop and nothing else:

```python
def fixed_point_with_slow_processes_frozen(encoder, perturbation_node_index, perturbation_sign_and_magnitude,
                                           slow_relation_mask, nodes_with_only_slow_inputs):
    """Quasi-steady state of the fast subsystem: the registered fixed-point loop with the slow relations'
    gains set to zero and the nodes that have no fast input held at baseline (deviation zero).

    slow_relation_mask: [R] bool, True for regulates_transcription_of and encodes (and trafficking relations
        once they exist). nodes_with_only_slow_inputs: [N] bool, True for gene nodes on the split graph.
    The full fixed point is the same call with both masks all False, so both readouts share every parameter.
    """
    relation_gain_fast = encoder.relation_gain() * (~slow_relation_mask).to(encoder.relation_gain().dtype)[:, None]
    keep_node = (~nodes_with_only_slow_inputs).to(relation_gain_fast.dtype)[:, None, None]      # [N, 1, 1]
    sustained_input = encoder.sustained_input(perturbation_node_index, perturbation_sign_and_magnitude).permute(1, 0, 2) * keep_node
    state = sustained_input
    for _ in range(encoder.max_propagation_steps):
        messages = encoder.aggregate_relation_messages(state, relation_gain_fast)                 # the existing per-round body
        next_state = ((1.0 - encoder.damping) * state + encoder.damping * (messages + sustained_input)) * keep_node
        if relative_change(next_state, state) < encoder.fixed_point_tolerance:
            return next_state
        state = next_state
    return state
```

For the acute label the input is scaled by the exposure at the observation time, u_F times c(t_obs) / c_bar, with c the normalised concentration profile; for a peak-concentration event that factor is the peak-to-mean ratio of the regimen (section 4.2). Since the fixed point is linear in u, this scales magnitudes and not signs, so for a ranking head it matters only across drugs.

## 4. Dosing periodicity: the mean and the harmonics

### 4.1 Decomposition

At pharmacokinetic steady state the forcing is periodic with the dosing interval T: u(t) = c(t) u_0 with c(t) = c_bar + sum over m of c_hat_m e^(i m omega_0 t). Under parameterisation (b) the periodic steady-state response is

    y(t) = (I - G)^(-1) c_bar u_0 + sum over m of (I - G + i m omega_0 D^(-1))^(-1) c_hat_m u_0 e^(i m omega_0 t).

The first term is the fixed point of the mean forcing, which is what the encoder reads. The harmonics are the frequency response of the network at multiples of the dosing frequency, and this is the first object in this report in which D appears in a way that no gain can absorb: D^(-1) multiplies i omega. Frequency-domain sensitivity analysis of biochemical networks is set out by Ingalls (J Phys Chem B 2004 [27], not verified through PubMed); experimentally, signalling pathways "act as a low-pass filter, integrating the signal when it changes rapidly and following it faithfully when it changes more slowly" [28], and periodic stimulation is the standard way to find "which dynamic range dominates a response" when a cascade "spans a wide range of time scales, including the rapid ligand-receptor interaction and the much slower response of downstream gene expression" [29]. With the encoder's nonlinear cross-relation mixture the superposition in the formula is approximate; it is exact for the mean-only mixture, which is the linear operator.

### 4.2 The forcing's Fourier content

For first-order elimination with rate k_e and bolus dosing every T, the steady-state profile is c(t) proportional to e^(-k_e t) on each interval, and

    |c_hat_m| / c_bar = 1 / sqrt(1 + (m omega_0 / k_e)^2),
    c_max / c_bar = k_e T / (1 - e^(-k_e T)),    c_min / c_max = e^(-k_e T) = 2^(-T / t_half).

The mean c_bar depends on dose rate and clearance only, not on half-life. The swing does:

| regimen (half-life from [2] [3]) | first harmonic over mean | peak over mean | trough over mean | peak over trough |
|---|---|---|---|---|
| quetiapine immediate release, 7 h, twice daily | 0.19 | 1.71 | 0.52 | 3.3 |
| quetiapine immediate release, 7 h, once daily | 0.35 | 2.62 | 0.24 | 10.8 |
| paroxetine, 21 h, once daily | 0.13 | 1.45 | 0.66 | 2.2 |
| citalopram, 36 h, once daily | 0.07 | 1.25 | 0.79 | 1.6 |
| fluoxetine parent, 4 d, once daily | 0.03 | 1.09 | 0.92 | 1.2 |
| norfluoxetine, 11 d, once daily | 0.01 | 1.03 | 0.97 | 1.1 |

Dosing intervals are chosen to match half-lives, which compresses the range: across the study drugs the peak-to-mean ratio of the actual regimen runs from about 1.0 to about 2.6. Any test of the harmonic reading must use the regimen's ratio and not the half-life alone, otherwise it is underpowered by design (section 6).

### 4.3 The nodes' low-pass factors

Ignoring the network's own coupling, a node with rate kappa passes the m-th harmonic with gain 1 / sqrt(1 + (m omega_0 / kappa)^2) and phase lag arctan(m omega_0 / kappa). For once-daily dosing (omega_0 = 0.26 per hour) and the rates of section 1.2:

| node class | relaxation time | first-harmonic gain, 24 h dosing | first-harmonic gain, 12 h dosing |
|---|---|---|---|
| membrane potential, synaptic pools, metabolite pools of minutes | ms to 30 min | 0.99 to 1.00 | 0.99 to 1.00 |
| receptor surface pool | 33 min | 0.99 | 0.96 |
| fast transcription-factor transcript | 2 h half-life | 0.80 | 0.55 |
| typical transcript | 9 h half-life | 0.28 | 0.15 |
| short-lived protein | 1 d half-life | 0.11 | 0.06 |
| average brain protein | 9 d lifetime | 0.02 | 0.01 |

In the coupled toy (check 4) the fast nodes passed the daily harmonic at 0.97 of their DC response, the transcript at 0.27 and the protein at 0.005, matching the table. The membrane node passed it at 1.11, above DC, because at DC the slow protein node fed back an opposing term that the daily harmonic filters out. That is the prior report's "homeostatic feedback that cancels the steady-state effect while the transient drives the symptom" (its 1.1) in the frequency domain: slow opposing adaptation flattens the mean response and leaves the swing, and the fixed point of the mean under-reads any node downstream of such a loop by exactly the amount the loop cancels.

### 4.4 What each label class reads

Germline labels: c_hat_m = 0 for all m; the mean term is the whole response. Chronic late-onset labels at slow nodes: the harmonics arrive at a few percent of DC (the product of a forcing fraction of 0.01 to 0.35 and a node gain of 0.005 to 0.3), so the fixed point of the mean is the right reading to within a few percent even for a seven-hour drug; what it misses is in section 3.2. Acute labels at fast nodes: the node passes the whole swing, so the response tracks c(t) quasi-statically and the peak reading is the fast fixed point at c_max / c_bar times the mean, that is 2.6 times the DC reading for once-daily quetiapine and 1.0 to 1.1 times for the fluoxetine pair. Acute labels at intermediate nodes (a two-hour transcript under twice-daily dosing passes 0.55 of the swing): the only place a full frequency-response solve adds something the two fixed points do not already give.

## 5. Recommendations ranked by cost

Cost is on a runtime-limited GPU cluster with a four-hour wall clock and USR1 checkpointing (slurm/train_resumable.sbatch, as described in the prior report). For each: what, data, new parameters, validation or falsification and whether it changes the steady state and so is testable against the HPO sign check with no new labels. R1 and R5 are the only ones that change the full steady state and so are testable against the HPO sign check; R0 touches it only to confirm that rates do not.

**R0. Rate-invariance check on the real operator (minutes, one CPU, no training, no labels beyond the existing 1,067 pairs).** Rerun experiments/check_linear_response_signs.py to convergence (not 8 rounds) with a per-node step d_i from a five-class table ordered by the physical rates (membrane and extracellular pools; metabolites; receptor surface and protein activity; transcripts; protein abundance) but compressed to {0.9, 0.5, 0.2, 0.1, 0.05}, since the theorem holds for any ratios and the true ratios of 10^10 would need 10^10 rounds to converge; raise the round cap and tighten the tolerance to 1e-6 so that both arms are read at convergence. Prediction from 2.2: sign agreement identical to the uniform-damping convergence value (0.593) to the stopping tolerance. Changes the steady state: no, by theorem; the point of running it is that the theorem is proved for the linear operator and checked numerically only on a toy, and the encoder's real loop has the mixture, the extracellular pool averaging, the presence mask and the bottleneck multiply, any of which could break the homogeneity the argument needs. Null (expected): no movement, and the owner stops looking for rates as a cause of the HPO result. Positive (unexpected): movement, which would mean one of those components is not positively homogeneous or the loop is not converging, either of which is a bug worth finding. New parameters: 0. Data: the five rate classes of section 1.2.

**R1. Relation gain-ratio sweep on the converged sign check (an hour, one CPU, no training).** The honest form of "could rates move the 0.615" (2.5). Sweep the ratios of the metabolic relation gains (product_of, depletes_substrate, substrate_of, catalyzed_by, product_opposes, carrier relations) over a log grid at convergence and record the sign agreement on a gene-level split of the 1,067 pairs (tune on half the genes, report on the other half, since a sweep against the test set is fitting). Changes the steady state: yes; with R5 it is one of the two recommendations here that do. Falsified (as a hope) if no point of the grid lifts the held-out agreement above the majority direction; that result would say the error is at the edge level (flux shares, elasticities, signs, mirror pairs) and no relation-level weighting, rate-derived or learned, can reach it, which is the strongest cheap argument for the total_in_degree and product_opposes arms and for per-edge elasticities (R5). New parameters: 0 (a sweep, not a fit).

**R2. Two nested fixed points as masked loops (one script for the untrained probe; two five-fold runs, about ten four-hour jobs, for the trained twin).** Build the function of 3.4 with slow_relation_mask covering regulates_transcription_of and encodes and nodes_with_only_slow_inputs covering gene nodes; read [h*_acute, h*_full] into the noisy-OR head as 2 C channels. Data: none new for the probe; for the validation, the acute-against-adaptive curation of MedDRA preferred terms that the prior report's 4.3 names (its cheapest new data) plus, per drug, t_max and the regimen's peak-to-mean ratio from the FDA label sections the repository already parses and from [2] [3]. New parameters: 0 in the operator; C extra input channels to the head and whatever the module gates spend on them. Validation: (i) untrained probe, the prior report's 4.5, with the prediction that h*_acute and h*_full differ in sign at a nonempty set of label-bearing nodes and that a drug with both a transcriptional mechanism edge and a fast ionotropic one (valproate, if its histone deacetylase inhibition is among its mechanism edges) separates cleanly; (ii) trained twin against the single-fixed-point model on the drug labels, scored separately in the acute and adaptive strata. Falsified if the two readouts agree in sign at more than 95 percent of label-bearing nodes (then the transcription layer does not reach the labelled symptoms and the owner is sent back to the graph) or if the twin interval includes zero in both strata. Changes the steady state: no; h*_full is unchanged, so the HPO check is blind to it by construction, which is why the validation has to be on drug labels.

**R3. Harmonic reading at the dosing frequency (one complex sparse solve per drug per harmonic, minutes to an hour on one CPU; no training unless fed to the head).** For each drug, solve (I - G + i omega_0 D^(-1)) y_1 = c_hat_1 u_0 with the mean-only (linear) mixture and the five-class D, and report |y_1| and its phase at the label-bearing nodes beside the DC reading; the peak reading is the DC term plus the harmonics evaluated at t_max. Data: dosing interval and half-life per drug (labels; [2] [3]; the repository's docs/exposure_sources); the five rate classes. New parameters: 0 fixed, or 5 learned log-rates with literature priors if the owner insists (see 6.3). Validation: the prior report's 2.3 test, corrected so that pairs are matched on target and separated by the regimen's peak-to-mean ratio (section 4.2), not by half-life: once-daily immediate-release quetiapine (2.6) against the fluoxetine pair (1.0 to 1.1) is a separation; zolpidem against flurazepam is not unless both regimens are specified. Falsified if the peak reading does not reorder acute-stratum predictions relative to DC on the high-ratio drugs. Changes the steady state: no.

**R4. Node-level rates from public tables (weeks of curation, no GPU).** Needed only if R2 or R3 shows signal and the five-class table is too coarse at the band (3.4). Sources: brain protein lifetimes for about 3,500 proteins in vivo [14] and about 2,500 across tissues [12], cultured neuron and glia half-lives for over 5,100 proteins [13]; mRNA half-lives for over 5,000 genes in mouse fibroblasts [11] and human cell lines [10]; receptor sequestration and recycling constants per receptor family from the trafficking literature ([8] [9] for the beta2-adrenergic receptor; psychiatric GPCRs would need their own rows); metabolite turnover as sampled flux over pool size, with pools from brain MRS for a few dozen metabolites and otherwise unknown; BRENDA (CC BY 4.0) for K_m where the pool size is known. Caveats to state in any use: mouse and cell-line values stand in for human brain, and the metabolite class spans ten orders of magnitude so a per-type default is wrong inside it. New parameters: 0 learned; one fixed number per covered node. Validation: does the node-level partition change the F or S membership of more than 5 percent of label-bearing nodes relative to the five-class partition? If not, the class table is enough and R4 is not needed. Changes the steady state: no.

**R5. Per-edge elasticities from saturation (curation plus a rebuild; no new training machinery).** Not about rates, but it is the steady-state change that section 2 points at and the one the sign check can score. For a Michaelis-Menten substrate the elasticity is epsilon = K_m / (K_m + S); with BRENDA K_m and a brain concentration S the edge weight becomes an elasticity instead of 1.0, for the minority of reactions with both numbers. New parameters: 0 learned. Validation: the sign check, held-out by gene as in R1. Falsified if the covered subset's sign agreement does not move. Changes the steady state: yes.

**R6. Learned rates, learned partitions, neural ODEs.** Not recommended; 6.3 says why.

Summary:

| recommendation | cost | new learned parameters | changes h*_full (HPO-testable) | what a null means |
|---|---|---|---|---|
| R0 invariance check | minutes, CPU | 0 | no (by theorem) | theorem holds on the real loop; rates are not the HPO cause |
| R1 gain-ratio sweep | an hour, CPU | 0 | yes | relation-level weighting cannot fix the sign check; the error is per edge |
| R2 nested fixed points | probe: an hour; twin: ten 4 h jobs | 0 in operator, C channels in head | no | transcription layer does not reach labelled symptoms, or labels do not separate acute from adaptive |
| R3 harmonic reading | an hour, CPU | 0 (or 5 with priors) | no | labels do not read the dosing swing |
| R4 node-level rates | weeks of curation | 0 | no | five classes suffice |
| R5 per-edge elasticities | curation and rebuild | 0 | yes | saturation is not the missing elasticity |

## 6. Criticism

### 6.1 Where the owner's framing is right

The fixed point is not the pharmacokinetic steady state, and the two have different clocks: the forcing settles in 3.3 to 5 half-lives and the network in a few multiples of its slowest relevant relaxation time; for every study drug but the fluoxetine pair the network is the slower of the two (1.1 and 1.2). Pharmacodynamics already separates them as the indirect response model's k_out [4] [P26]. The framing is also right that a drug label can be observed before the network has settled, and that an acute label is then a different object from the full fixed point; section 3.4 is the formal version, and it is the one change the framing earns. And the owner's earlier instinct ("Use the convergence instead of 8 steps. 8 steps is arbitrary, not physiological", experiments/measure_propagation_convergence.py) was right for a reason beyond arbitrariness: 1.4 shows the 8-round state is not a time point of anything.

### 6.2 Where it leads somewhere unproductive

Three places.

The phrase "final settling of the physiology as a whole" overstates what h* is. It is the final settling of a linear operator over the processes the graph contains, which stop at protein abundance. The physiology's final settling under a chronic drug includes receptor density adaptation, desensitisation and, for a germline variant, development, none of which is in G. So h* is the settling of a subset of the physiology, and the chronic drug labels fail on it for lack of loops, not for lack of time (3.2). If the framing sends the owner toward adding a time axis before adding the loops, it has sent them the wrong way; the loops change the fixed point and the time axis does not.

The framing invites the belief that relaxation rates could improve the steady-state predictions. Section 2 shows they cannot, under the only reading of the gains that is physical, and that under the other reading they reduce to gain re-weighting the model already has. The HPO failure is a gains-and-structure failure and the owner's framing is silent on it. I would put the time the framing tempts them to spend on rates into R1 and R5 instead.

The framing treats "the fixed point" as the number in finding 10. That number is an 8-round truncated walk sum (1.4). The converged value is 0.593 over 83 percent of pairs against 0.757; comparisons that put 0.615 against 0.806 compare a transient of the model against a steady state of the patient, which is the mismatch the owner is worried about, committed in the other direction.

### 6.3 Which changes would worsen identifiability against about 3,910 observations

Anything that learns a rate. At the full fixed point the gradient of the loss with respect to any relaxation rate is identically zero (2.2), and the acute fixed point depends on rates only through the discrete partition, which has no gradient, so a learned rate is identified only through the harmonic readout, where it trades off against the gains along every path. Per-node rates (49,574) and per-edge rates (280,966) are hopeless; per-relation rates (26) are the ones the prior report's 2.4 warned against and I agree, with the sharper reason that at the fixed point they are not merely weakly identified but unidentifiable. Learned soft partitions (a per-node sigmoid deciding fast against slow) are per-node rates in disguise. Five class-level log-rates with literature priors (R3's option) are identifiable in principle through the harmonics, but the prior would do almost all the work and the posterior would say little; fix them. A neural ODE's vector field is the limit of all of this (prior report 2.11) and would learn the degree structure first, as the trained encoders already do (findings 5 and 16). The nested fixed points of R2 add C input channels to the head and nothing to the operator, which is the only kind of change that about 3,910 observations across roughly 90 constructs can bear.

### 6.4 What a null result looks like for each recommendation

R0: the converged sign agreement does not move under any class rate table. This is the expected outcome and it is informative: it retires rates as a cause of the HPO result on the real loop. The non-null is a bug report.

R1: no gain ratio on a held-out gene split lifts the agreement above the majority direction. Then relation-level weighting is exhausted and the error is per edge; the owner's running arms (total_in_degree, sign ablation, product_opposes) and R5 are where to look.

R2: the acute and full readouts carry the same sign at more than 95 percent of label-bearing nodes, or the trained twin's interval includes zero in both the acute and adaptive strata. The first says the transcription layer does not reach the labelled symptoms (a graph result, not a readout result); the second says the labels do not separate the two time scales, which with no onset field in SIDER or OnSIDES is a live possibility and would make the acute-adaptive curation itself the thing to doubt.

R3: on drugs whose regimen has a peak-to-mean ratio above 2, the peak reading does not reorder acute-stratum predictions relative to DC. Then the label aggregation (adverse-event rates over weeks of trials) has already averaged the swing away, which is what the prior report's 1.3 argued for onset and would then hold for peaks as well.

R4: the node-level partition moves fewer than 5 percent of label-bearing nodes between F and S. Then the five-class table is enough.

R5: the sign agreement on the covered subset does not move. Then saturation is not the missing elasticity and the one-elasticity-per-relation problem is one of flux shares and signs instead.

### 6.5 Where this report disagrees with the prior one

Its 1.9: "rates drop out ... That is correct and it is the whole problem." Correct, not a problem for the fixed point; the problem is the gains (2.4).

Its 2.2: time constants from the uniform-damping spectrum are in rounds, not time; report mode supports, not time constants (2.4).

Its 2.4: the per-relation rate k_r in the update changes no fixed point and no physical transient; the usable content is the two-equilibria mask, which 3.4 derives as a singular perturbation and shows is correctly a mask on relations with gene nodes clamped.

Its 2.3 validation: half-life-matched pairs are underpowered because dosing intervals co-adapt to half-lives; match on the regimen's peak-to-mean ratio (4.2).

Its 3.1 and 1.11: the steady-state comparison should quote the converged 0.593 against 0.757, not the 8-round 0.615 against 0.806 (1.4). The conclusion stands.

Its 2.1 (trajectory features): under uniform damping the trajectory has no time axis, and under heterogeneous rates the transient of the full system is replaced by the nested fixed points except in the band; I would rank 2.1 below 2.4 rather than above it.

### 6.6 What I do not know

Whether the encoder's real loop is positively homogeneous end to end (R0 decides). Whether any label-bearing node changes sign between the acute and full fixed points on the real graph (R2's probe decides). The pool sizes that turn sampled fluxes into metabolite turnover times for more than a few dozen brain metabolites; without them the metabolite class stays an order-of-magnitude assignment. The dissociation rates of the study drugs at their targets, which set whether receptor occupancy itself is in F at a one-hour label (for most it is; for a few slow-dissociating drugs it may not be). And whether the acute-against-adaptive curation of MedDRA terms can be made reliable enough to carry R2's validation; the prior report called it the cheapest new data, and it is also the least checked.

## References

New references, numbered in order of first appearance. Quotes are from the PubMed abstracts unless marked.

[1] D. J. Greenblatt, "Elimination half-life of drugs: value and limitations," Annu. Rev. Med., vol. 36, pp. 421-427, 1985. doi:10.1146/annurev.me.36.020185.002225
[2] C. L. DeVane and C. B. Nemeroff, "Clinical pharmacokinetics of quetiapine: an atypical antipsychotic," Clin. Pharmacokinet., vol. 40, no. 7, pp. 509-522, 2001. doi:10.2165/00003088-200140070-00003
[3] C. Hiemke and S. Härtter, "Pharmacokinetics of selective serotonin reuptake inhibitors," Pharmacol. Ther., vol. 85, no. 1, pp. 11-28, 2000. doi:10.1016/s0163-7258(99)00048-0
[4] W. J. Jusko and H. C. Ko, "Physiologic indirect response models characterize diverse types of pharmacodynamic effects," Clin. Pharmacol. Ther., vol. 56, no. 4, pp. 406-419, 1994. doi:10.1038/clpt.1994.155
[5] J. D. Clements, R. A. Lester, G. Tong, C. E. Jahr and G. L. Westbrook, "The time course of glutamate in the synaptic cleft," Science, vol. 258, no. 5087, pp. 1498-1501, 1992. doi:10.1126/science.1359647
[6] J. Shen et al., "Determination of the rate of the glutamate/glutamine cycle in the human brain by in vivo 13C NMR," Proc. Natl. Acad. Sci. USA, vol. 96, no. 14, pp. 8235-8240, 1999. doi:10.1073/pnas.96.14.8235
[7] N. Jamshidi and B. Ø. Palsson, "Top-down analysis of temporal hierarchy in biochemical reaction networks," PLoS Comput. Biol., vol. 4, no. 9, e1000177, 2008. doi:10.1371/journal.pcbi.1000177
[8] S. Pippig, S. Andexinger and M. J. Lohse, "Sequestration and recycling of beta 2-adrenergic receptors permit receptor resensitization," Mol. Pharmacol., vol. 47, no. 4, pp. 666-676, 1995. PMID 7723728
[9] M. von Zastrow and B. K. Kobilka, "Ligand-regulated internalization and recycling of human beta 2-adrenergic receptors between the plasma membrane and endosomes containing transferrin receptors," J. Biol. Chem., vol. 267, no. 5, pp. 3530-3538, 1992. PMID 1371121
[10] E. Yang et al., "Decay rates of human mRNAs: correlation with functional characteristics and sequence attributes," Genome Res., vol. 13, no. 8, pp. 1863-1872, 2003. doi:10.1101/gr.1272403
[11] B. Schwanhäusser et al., "Global quantification of mammalian gene expression control," Nature, vol. 473, no. 7347, pp. 337-342, 2011. doi:10.1038/nature10098 (the median mRNA and protein half-lives are in the paper's text rather than its abstract and are not quoted here)
[12] J. C. Price, S. Guan, A. Burlingame, S. B. Prusiner and S. Ghaemmaghami, "Analysis of proteome dynamics in the mouse brain," Proc. Natl. Acad. Sci. USA, vol. 107, no. 32, pp. 14508-14513, 2010. doi:10.1073/pnas.1006551107
[13] A. R. Dörrbaum, L. Kochen, J. D. Langer and E. M. Schuman, "Local and global influences on protein turnover in neurons and glia," eLife, vol. 7, e34202, 2018. doi:10.7554/eLife.34202
[14] E. F. Fornasiero et al., "Precisely measured protein lifetimes in the mouse brain reveal differences across tissues and subcellular fractions," Nat. Commun., vol. 9, 4230, 2018. doi:10.1038/s41467-018-06519-0
[15] I. Björkhem and S. Meaney, "Brain cholesterol: long secret life behind a barrier," Arterioscler. Thromb. Vasc. Biol., vol. 24, no. 5, pp. 806-815, 2004. doi:10.1161/01.ATV.0000120374.59826.1b
[16] Quetiapine fumarate tablets, FDA prescribing information, section 5.7 (orthostatic hypotension), read through DailyMed on 21 October 2026, setid 070faf07-0ce7-4354-8643-9d222b72ecad. The phrase quoted is the label's.
[17] S. Kapur, R. Zipursky, C. Jones, G. Remington and S. Houle, "Relationship between dopamine D(2) occupancy, clinical response, and side effects: a double-blind PET study of first-episode schizophrenia," Am. J. Psychiatry, vol. 157, no. 4, pp. 514-520, 2000. doi:10.1176/appi.ajp.157.4.514
[18] B. A. Liu, N. Mittmann, S. R. Knowles and N. H. Shear, "Hyponatremia and the syndrome of inappropriate secretion of antidiuretic hormone associated with the use of selective serotonin reuptake inhibitors: a review of spontaneous reports," CMAJ, vol. 155, no. 5, pp. 519-527, 1996. PMID 8804257
[19] J. M. Alvir, J. A. Lieberman, A. Z. Safferman, J. L. Schwimmer and J. A. Schaaf, "Clozapine-induced agranulocytosis. Incidence and risk factors in the United States," N. Engl. J. Med., vol. 329, no. 3, pp. 162-167, 1993. doi:10.1056/NEJM199307153290303
[20] C. U. Correll and E. M. Schenk, "Tardive dyskinesia and new antipsychotics," Curr. Opin. Psychiatry, vol. 21, no. 2, pp. 151-156, 2008. doi:10.1097/YCO.0b013e3282f53132
[21] H. Kacser and J. A. Burns, "The control of flux," Symp. Soc. Exp. Biol., vol. 27, pp. 65-104, 1973. PMID 4148886 (no abstract in PubMed; cited for the elasticity and control-coefficient formalism the encoder itself cites)
[22] R. Heinrich and T. A. Rapoport, "A linear steady-state treatment of enzymatic chains," Eur. J. Biochem., vol. 42, pp. 89-95 and 97-105, 1974. doi:10.1111/j.1432-1033.1974.tb03319.x (as cited in the prior report and in the encoder)
[23] C. Reder, "Metabolic control theory: a structural approach," J. Theor. Biol., vol. 135, no. 2, pp. 175-201, 1988. doi:10.1016/s0022-5193(88)80073-0
[24] P. Kokotović, H. K. Khalil and J. O'Reilly, Singular Perturbation Methods in Control: Analysis and Design, Academic Press, 1986; A. N. Tikhonov, "Systems of differential equations containing small parameters in the derivatives," Mat. Sb., vol. 31, pp. 575-586, 1952. Not verified through PubMed.
[25] J. Gunawardena, "Time-scale separation - Michaelis and Menten's old idea, still bearing fruit," FEBS J., vol. 281, no. 2, pp. 473-488, 2014. doi:10.1111/febs.12532
[26] L. A. Segel and M. Slemrod, "The quasi-steady-state assumption: a case study in perturbation," SIAM Rev., vol. 31, no. 3, pp. 446-477, 1989. doi:10.1137/1031091. Not verified through PubMed.
[27] B. P. Ingalls, "A frequency domain approach to sensitivity analysis of biochemical networks," J. Phys. Chem. B, vol. 108, no. 3, pp. 1143-1152, 2004. doi:10.1021/jp036567u. Not verified through PubMed.
[28] P. Hersen, M. N. McClean, L. Mahadevan and S. Ramanathan, "Signal processing by the HOG MAP kinase pathway," Proc. Natl. Acad. Sci. USA, vol. 105, no. 20, pp. 7165-7170, 2008. doi:10.1073/pnas.0710770105
[29] J. T. Mettetal, D. Muzzey, C. Gómez-Uribe and A. van Oudenaarden, "The frequency dependence of osmo-adaptation in Saccharomyces cerevisiae," Science, vol. 319, no. 5862, pp. 482-484, 2008. doi:10.1126/science.1151582

Prior-report references reused, by its numbering: [P5] Gainetdinov et al. 2004 (GPCR desensitisation); [P6] Burt, Creese and Snyder 1977 (dopamine receptor binding after chronic antipsychotics); [P7] Chouinard et al. 2017 (supersensitivity psychosis); [P8] Blier and Ward 2003 (5-HT1A autoreceptor desensitisation); [P26] Dayneka, Garg and Jusko 1993 (indirect response models).

Repository documents cited by path: mechanistic_pathway_learning/models/linear_response_encoder.py (update rule, damping 0.5, contraction 0.9, DEFAULT_FIXED_POINT_TOLERANCE 1e-3, DEFAULT_MAX_PROPAGATION_STEPS 60 and the comment that convergence to 1e-3 takes 23, 14 and 11 rounds at gains 0.9, 0.7 and 0.5); experiments/measure_propagation_convergence.py (the owner's instruction of 12 October 2026); docs/tissue_saturation.md (49,574 nodes; median 0.631 of the settled level at round 8); docs/linear_response_sign_check.md (the full table); docs/drug_entry_nodes.md section F ("rates drop out at a steady state", the fast and full equilibria proposal); docs/physiological_adherence_review.md sections 1, 2 and 14; docs/research_summary.md findings 5, 10, 11 and 16; docs/gene_protein_split.md (gene and protein nodes, encodes relation).
