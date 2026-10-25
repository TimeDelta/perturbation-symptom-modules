# Alternatives to the fixed-point readout in perturbation-symptom-modules

Prepared 20 October 2026 against the repository at commit 344d211 (linear_response_encoder.py, noisy_or_pathway_module_model.py, docs/open_decisions.md 9.68 to 9.72, docs/research_summary.md, docs/physiological_adherence_review.md, docs/missing_physiology_review.md, docs/linear_response_sign_check.md, docs/drug_entry_nodes.md section F, docs/label_source_review.md 19.2 and 23.3). Citations are numbered in order of first appearance; the list is at the end. Every empirical claim about the model is from the repository's own documents or code and says which one. Every empirical claim about physiology carries a reference whose abstract was read through PubMed on 20 October 2026; where I quote, the quote is from that abstract. Where I could not verify something I say so.

Notation used throughout. N nodes, R relations, C propagation channels. S_r is the signed normalised adjacency of relation r, g_rc the learned gain of relation r on channel c, d the damping, u the sustained input (the perturbation held on), h(t) the state at round t. The encoder's update is

    h(t + 1) = (1 - d) h(t) + d (A_c h(t) + u),    A_c = sum_r g_rc S_r,

with transition operator M_c = (1 - d) I + d A_c, and the readout is the fixed point h* = (I - A_c)^(-1) u, which the loop reaches to a relative tolerance of 1e-3 in at most 60 rounds (DEFAULT_FIXED_POINT_TOLERANCE, DEFAULT_MAX_PROPAGATION_STEPS). Everything after the loop (limiting-step bottleneck b, pH weight w_pH, the gate, the expansion to node_state_dim) is a function of h* alone.

## 1. Diagnosis: what a fixed-point readout cannot say

The one-sentence version. h* is a linear functional of u, h* = (I - A_c)^(-1) u, so (i) it carries no information about the path by which the system got there, (ii) it is exactly zero wherever a loop cancels the input at equilibrium, (iii) it is the same object for a perturbation present for an hour and for one present for life, (iv) its sign is fixed by u up to a global flip, and (v) it exists only because the gains are bounded so that spectral_radius(M_c) < 1, which rules out by construction every regime where the real system is not a stable node. Each failure below is one of these five in a particular physiological dress. For each I say whether the current encoder can represent it even in principle, and I distinguish "cannot, because of the fixed point" from "cannot, because the graph lacks the loop", since the second is not an argument against steady state.

1.1 Homeostatic feedback that cancels the steady-state effect while the transient drives the symptom.

Mechanism. A negative feedback loop with an integrating element returns the controlled variable to its set point in the continued presence of the input; this is adaptation, and it is structurally integral control [1][2]: "it is common for the response to an extracellular stimulus to return to its prestimulus value even in the continued presence of the signal-a process termed adaptation or desensitization" and "integral control in some form is necessary for a robust implementation of perfect adaptation" [2]. A search over all three-node enzyme topologies found exactly two core motifs that do this, "a negative feedback loop with a buffering node and an incoherent feedforward loop with a proportioner node" [3]. In psychiatry the controlled variables include extracellular dopamine, whose homeostatic region has been modelled explicitly, with the finding that "mutations or environmental changes can place an individual closer to the edge of the homeostatic region" [4].

What the fixed point does. If the graph contains such a loop with a self-edge of weight 1 at the integrating node (the integrator), the fixed point at the controlled node is exactly zero whatever u is, and the whole response lives in the transient. A two-node check with the encoder's own update (d = 0.5, x driven by u, y an integrator fed by x and inhibiting x) gives peak x = 0.75 at round 2 and x* = 0 at the fixed point. The symptom, if it is driven by the excursion, is unreadable from h*.

Can the current setup represent it. No, and for two separate reasons. First, the readout: an integrator produces an eigenvalue of M_c at 1 on the loop and the contraction bound forbids it, so in the built model the loop leaks and leaves a small nonzero residue, but a leaky integrator still attenuates the steady state far below the peak, so the sign survives and the magnitude does not. Second, the graph: the repository's own review found "no closed adaptation loop for any psychiatric receptor" and that "94 of 116 GRK/arrestin edges into GPCR-family genes read activates at +1", the wrong sign for a desensitising kinase [docs/missing_physiology_review.md section 4]. So at present the feedback is both wrongly signed and unclosed; even a transient readout would see nothing until the graph is fixed.

1.2 Receptor desensitisation and downregulation.

Mechanism. "GPCRs can be desensitized following activation by agonists by becoming phosphorylated by members of the family of G protein-coupled receptor kinases (GRKs). Phosphorylated receptors are then bound by arrestins, which prevent further stimulation of G proteins and downstream signaling pathways" [5]. Chronic antagonism runs the other way: chronic haloperidol, fluphenazine or reserpine "elicits a 20 to 25% increase in striatal dopamine receptor binding" [6], the basis of supersensitivity psychosis, in which "long-term administration of antipsychotics can upregulate D2 receptors and produce receptor supersensitivity manifested by ... movement disorders and supersensitivity psychosis (SP) in patients" [7].

What the fixed point does. Desensitisation is a change in a gain (the receptor's coupling efficiency), not a change in a state. In a linear system the gains g_rc are constants of the operator, so h* cannot contain a term where the output of a receptor lowers that receptor's own transmission. This is a product of two state variables and is outside linearity, which the repository already notes for partial agonism and competition [docs/physiological_adherence_review.md section 12].

Can the current setup represent it. Not in principle: it needs state-dependent gains, which are nonlinear, and the model is linear by registration. A nonlinear fixed point (section 2.7 below) can hold the end state of desensitisation (a lowered gain at equilibrium) but still not the time course of its onset.

1.3 Delayed therapeutic onset.

Mechanism, with the caveat the literature forces. The classical account of SSRI latency is autoreceptor desensitisation: "Their delayed therapeutic activity is believed to result from increased activation of postsynaptic 5-HT1A receptors occurring only after 5-HT neurons regain their normal firing activity. The recovery of this parameter, which is attributable to 5-HT1A autoreceptor desensitization, also restores 5-HT release" [8]. But the trial data do not support a pure delay: a meta-analysis of 28 placebo-controlled trials found "Treatment with SSRIs is associated with symptomatic improvement in depression by the end of the first week of use, and the improvement continues at a decreasing rate for at least 6 weeks" [9], and the parallel analysis for antipsychotics "rejects the commonly held hypothesis that antipsychotic response is delayed. Rather, these findings suggest that the antipsychotic response starts in the first week of treatment and accumulates over time" [10]. Lithium in acute mania shows a medium effect at day 5 (effect size 0.55 against 0.35 for placebo) and 0.79 at day 21 [11]. Ketamine reaches its antidepressant effect "within 110 minutes after injection" and the effect decays over a week [12].

What this means for the readout. Onset is a monotone approach to an asymptote with a time constant of days to weeks, so the asymptote, not the transient, is the quantity a "relieves" label (which is what a trial outcome is) reports. For the induction labels, which are the bulk of the drug set, the adverse-event rate at the label is also a cumulative rate over weeks. So delayed onset is an argument for the steady state, not against it. The mistake would be to read the steady state at the wrong equilibrium: a fast equilibrium with transcription frozen (hours) against a full equilibrium with transcriptional and trafficking adaptation complete (weeks). The repository already proposed exactly this two-equilibrium reading in docs/drug_entry_nodes.md section F ("a fast equilibrium with only the fast relations active ... and a full equilibrium with every relation active, both read by the head") and has not built it.

Can the current setup represent it. The asymptote yes; the two equilibria no, since every relation is active in the one fixed point.

1.4 Withdrawal and rebound of opposite sign to the acute effect.

Mechanism. Opponent-process and allostasis: "Counteradaptive processes such as opponent-process that are part of normal homeostatic limitation of reward function fail to return within the normal homeostatic range" [13]; addiction "results from adaptations in specific brain neurons caused by repeated exposure to a drug of abuse" that are "time-dependent" [14]. Lithium discontinuation: "Recurrences increased sharply soon after discontinuing lithium, but were markedly limited and not merely delayed, by slow discontinuation. Similar reactions may follow discontinuation of other drugs, evidently as responses to long-term pharmacodynamic adaptations" [15]. Antipsychotic withdrawal: the review of supersensitivity psychosis names "rapid relapse after drug discontinuation/dose reduction/switch of antipsychotics" as a defining feature and describes "3 antipsychotic withdrawal syndromes" [7].

What the fixed point does. Rebound is the response to a step down after adaptation to a step up. In a linear system with sustained input the response to removing u is minus the response to applying it, so the rebound of a linear fixed-point model is exactly the mirror image of the acute effect and carries no new information. Real rebound overshoots the baseline because the adapted gains (upregulated receptors) persist after the drug is gone: it needs state that outlives the input, which the fixed point cannot hold because at the fixed point nothing changes.

Can the current setup represent it. No. Not even the sign: the SIDER and OnSIDES labels contain withdrawal events (insomnia on stopping a hypnotic, anxiety on stopping a benzodiazepine) that the model is asked to fit from a perturbation of the opposite sign.

1.5 Tolerance.

Mechanism. Pharmacodynamic tolerance has a time constant and a magnitude of its own: for nicotine "a half-life of development and regression of tolerance of 35 min" and "an approximately 80% reduction of initial (nontolerant) effect" [16]. For benzodiazepines "tolerance develops relatively quickly for the sedative and anticonvulsant actions of benzodiazepines, whereas tolerance to anxiolytic and amnesic effects probably does not develop at all" [17]; this is the sharpest case, because the same drug at the same receptor produces a sedation label that is transient and an anxiolysis label that persists.

What the fixed point does. One h* per drug cannot give sedation a transient reading and anxiolysis a sustained one. Only a readout with a time axis, or two equilibria read separately, can.

Can the current setup represent it. No.

1.6 Multistability and hysteresis.

Mechanism. Positive feedback with a sigmoidal open-loop characteristic is "guaranteed to be bistable for some range of feedback strengths" [18]; the MAPK network in PC-12 cells switches between negative-feedback-only (EGF) and positive-feedback (NGF) topologies, "The latter allows for bi-stable Erk activation dynamics" [19], and "the duration of ERK activation is critical for cell signaling decisions" [20].

What the fixed point does. The contraction bound makes the fixed point unique and globally attracting. A bistable system has two stable fixed points and the one reached depends on the initial state and the history: that is hysteresis, and the model has excluded it by construction. The repository states this plainly for the excitable membrane ("regenerative sodium current is textbook positive feedback and its fixed point is unstable by construction" [docs/label_source_review.md 23.3]) and chose the subthreshold steady state knowingly. The choice is consistent but it is also a statement that no switch-like symptom (a manic switch, a seizure, a psychotic break) can be represented.

Can the current setup represent it. Not in principle, and not with any linear operator: a linear system has one fixed point or a continuum.

1.7 Oscillatory regimes.

Mechanism. The circadian clock is "a transcriptional/translational feedback loop that consists of the CLOCK-BMAL1 heterodimeric transcriptional activator complex and the PER1/2-CRY1/2-CK1δ/ε repressive complex" [21]; negative feedback with ultrasensitivity in a kinase cascade produces oscillations with "period ... from minutes to hours" [22]; thalamic spindles and spike-wave discharge arise from "reciprocal synaptic connectivity between excitatory thalamocortical relay neurons and inhibitory thalamic reticular neurons along with a robust post-inhibitory rebound mechanism" [23]. Insomnia, hypersomnia and the sleep-phase labels in the symptom set are symptoms of an oscillator's phase and amplitude.

What the fixed point does. A stable linear system driven by a constant input has no oscillating fixed point; complex eigenvalues of M_c give damped oscillation in the transient only (the toy loop above has eigenvalues 0.5 ± 0.45 i). A sustained oscillation needs either a limit cycle (nonlinear) or an undamped pair on the unit circle (forbidden by the bound). So h* at a clock gene is a constant, and the model can say that a perturbation raises or lowers PER2 but not that it shifts phase or shortens period.

Can the current setup represent it. No. The transcription layer does contain CLOCK, BMAL1, PER and CRY edges (CollecTRI), so the loop exists; it is the readout that cannot see it oscillate.

1.8 Developmental against adult gene dosage.

Mechanism. The question is whether a lifelong perturbation's symptom is the steady state of the adult network or the residue of a developmental trajectory. The evidence runs both ways and is gene-specific. For MECP2 loss, "activation of MeCP2 expression leads to striking loss of advanced neurological symptoms in both immature and mature adult animals" [24]; for MECP2 duplication, "correction of MeCP2 levels largely reverses the behavioural, molecular and electrophysiological deficits" in adult mice [25]. In these cases the adult steady state is the right object. For the sixteen developmental transcription factors the build drops because they are not brain-expressed in adult GTEx (HAND2, TWIST2, CRX, NEUROG1 and others, decision 9.68), the symptom is a developmental residue and the adult steady state is the wrong object by construction.

Can the current setup represent it. For the reversible cases, yes and the steady state is right. For the developmental residue cases, no readout of an adult graph can, and this is a scope limit to disclose rather than a readout problem to fix.

1.9 Timescale separation across transcriptional, metabolic and electrophysiological processes.

Mechanism. Binding and channel gating settle in milliseconds, metabolite pools in seconds to minutes, trafficking in minutes to hours, transcription and translation in hours to days, receptor density in days to weeks. The repository already states the consequence: "Transcription (hours), trafficking (minutes) and binding (milliseconds) collapse onto one fixed point, separated only by learned gains" and "A propagation step is not a unit of time" [docs/physiological_adherence_review.md section 14].

What the fixed point does. At a steady state the rates drop out ("rates drop out at a steady state. With a damped update the settled state satisfies state = update(state) whatever the damping", docs/drug_entry_nodes.md F). That is correct and it is the whole problem: the four propagation channels with their own gains are described as "time scales" in the command-line help, but because every channel runs to its own fixed point, the channels differ in which equilibrium they compute, not in how fast; they are four static operators. The code comment that the channels "settle at different time scales" is true of the transient and irrelevant to the readout.

Can the current setup represent it. Not as a time axis. It can represent timescale separation only in the two-equilibria form of 1.3, by freezing slow relations in one copy of the operator.

1.10 Dose timing and pharmacokinetics.

Mechanism. The input to the system is not a step but a periodic forcing with the dosing interval, convolved with absorption and elimination. Indirect-response pharmacodynamics gives "a slow onset and a slow return to baseline" with "hysteresis plots showed that drug concentrations preceded the response" [26]. The repository's own exposure table assumes "the steady-state ratio holds at the therapeutic concentration. It says nothing about the time course after a dose" [docs/drug_exposure_table.md]; quetiapine's label describes "transiently high (58%-64%) D2 occupancy 2 to 3 hours after a single dose that then decreases" [docs/label_source_review.md].

What the fixed point does. A linear system driven by a periodic input has a periodic steady state, not a fixed point; reading the fixed point of the mean input is reading the zeroth Fourier coefficient and discarding the peak-trough excursion. For a drug whose adverse events are peak effects (orthostasis, sedation at Cmax) and whose therapeutic effects are trough effects, the fixed point cannot separate them.

Can the current setup represent it. No. The model has no time axis to put the dosing period on. The LTI route in 2.3 is the one that can.

1.11 Two failures the owner did not list but that share the mechanism.

Integrated deviation against level. The HPO laboratory labels the sign check uses (docs/linear_response_sign_check.md) are measured levels at the time of a blood draw in a patient in a lifelong steady state, so for them the steady state is the right object and it still scores 0.615 sign agreement against 0.806 for the majority direction. That number is important for section 3: the steady state is not the reason it is wrong.

Mirror symmetry of loss and gain. The response is odd in u by construction (every statistic in the cross-relation mixture is odd, "a gain of function has to produce the negative of the field a loss of function produces", MIXTURE_STATISTICS comment). Real dosage curves are not: haploinsufficiency and triplosensitivity are asymmetric, a knockout saturates at zero activity and an overexpression does not. This is not a steady-state failure, it is a linearity failure, but a transient readout inherits it unchanged.

## 2. Ranked candidate solutions

Ranked by cost of retrofit on the current code, cheapest first. For each: standard name; what changes about the readout; data needed; compute on a runtime-limited cluster with a 4-hour wall clock and USR1 checkpointing (slurm/train_resumable.sbatch); interaction with the Dawid-Skene soft priors; validation and falsification.

### 2.1 Trajectory statistics of the existing linear propagation (step response readout)

What it is. Keep the operator, record the whole trajectory h(0), ..., h(T) under the sustained input u, and read features of it rather than h(T). Standard terms: step response, settling time, overshoot, integral of the deviation, peak time. Since the perturbation is held on, this is a step response; an impulse response would be the trajectory with u applied at round 0 only, h(t) = M_c^t u, which the registered three-layer message passing was already computing without naming it.

Readout. Per node and channel, candidate features: h* (what exists now); peak_c(n) = max_t |h_c(n, t)| with its sign; peak time t_peak; overshoot ratio peak / |h*|; integrated deviation I_c(n) = sum_t (h_c(n, t) - h*_c(n)); settling time t_settle at tolerance epsilon. In the toy loop the overshoot ratio is 1.40 and in the integrator loop it is unbounded (h* = 0). The noisy-OR head takes the concatenation [h*, peak, I] as a field of 3 C channels and the modules learn which to pool.

Data. None new. The labels are what they are; the hope is that peak features fit the transient-driven labels and h* the sustained ones.

Compute. The loop already runs 11 to 23 rounds; storing T states costs T times the state memory ([N, B, C] at float32 is 34k x 16 x 4 x 4 bytes = 8.7 MB per round, so under 1 GB for 60 rounds) and no extra forward passes. Backward through the stored trajectory is what message passing already does. Negligible.

Dawid-Skene. Untouched; the prior is on labels, not on the readout. One subtlety: the "relieves" labels (29 rows) are trial outcomes at endpoint and should be tied to h*, the "induces" labels to the concatenation. That is a per-relation choice of which features the head may read and costs nothing.

Validation. Twin comparison against the h*-only model, five folds, paired bootstrap, the repository's existing machinery (docs/twin_comparisons.md). Falsified if the twin interval includes zero and the peak features receive negligible module gate mass. A stronger test: on the sign check (finding 10), does any trajectory feature beat 0.615? Since those labels are steady-state measurements the honest prediction is no, and that null is informative (section 3).

Caveat that must be stated. In this encoder the transient is a property of damping d and of graph distance, not of physiology. A node k edges away first receives signal at round k (h(0) = u, one hop per round) and the per-round attenuation is set by the in-degree normalisation, so t_peak is a proxy for path length and the integrated deviation is a proxy for (path count) times (settling time). That means 2.1 is cheap to try and easy to over-read: a positive result would show that path-length-weighted features carry label signal, which is what the random-walk baseline already shows (finding 8), not that physiological transients do.

### 2.2 Spectral analysis of the propagation operator (diagnostic, not a model change)

What it is. Compute the leading eigenvalues and eigenvectors of A_c (equivalently of M_c, since M_c = (1 - d) I + d A_c shares eigenvectors and maps eigenvalue lambda to 1 - d + d lambda). Standard terms: dominant modes, time constants tau_k = -1 / ln |mu_k| where mu_k is an eigenvalue of M_c, stability (|mu_k| < 1), oscillatory modes (complex pairs), non-normality (A_c A_c^T != A_c^T A_c) and transient growth (the numerical abscissa and the pseudospectral radius, not the spectral radius, set the peak of the step response).

What it tells the owner. Three things the fixed point hides. First, where the slow modes live: the eigenvectors with |mu_k| near the contraction bound name the node sets that settle last, and those are the subgraphs where reading at round 8 and at round 60 differ most. Second, whether there are oscillatory modes at all, and on which nodes (complex pairs on the CLOCK/BMAL1/PER/CRY subgraph would say the loop is there and merely damped). Third, non-normality: a signed, directed, in-degree-normalised adjacency is highly non-normal, and in non-normal systems "the recurrent connectivity can amplify the input ... One is induced by the presence of near-critical eigenvalues ... The other relies on W not being normal, which allows the network activity to make large but fast excursions along specific directions" [27]; "balanced amplification" arises exactly when "feedback inhibition stabilizes strong recurrent excitation" and produces "a hidden feedforward connectivity between activity patterns" [28]. The metabolic layer's production-against-consumption pairs (finding 11, 36.6 percent of destinations receive both signs) are this structure. If the operator is strongly non-normal, the transient of 2.1 can be large where h* is small, which is the quantitative reason 2.1 may find something h* does not.

Jordan structure. Not computable numerically on a 34k-node operator and not worth attempting; near-defective eigenvalues show up as large pseudospectra, which is what to measure instead. Say "pseudospectra", not "Jordan form", in anything written.

Data. None.

Compute. Sparse Arnoldi (scipy.sparse.linalg.eigs) for the top 50 to 200 eigenvalues of a 34k x 255k-edge operator runs in minutes on one CPU core; the pseudospectral radius at a few epsilon values by the Lanczos method on (A_c - z I) costs a few hundred sparse solves per z and is an afternoon. Dense eigendecomposition (9 GB, O(N^3)) is out. Note A_c depends on the learned gains, so this is done on the untrained operator and again on each trained fold's operator; four channels, five folds, two encoders is 40 operators.

Dawid-Skene. None.

Validation. This is a diagnostic, so it is validated by whether it predicts where 2.1 finds signal: the nodes with the largest transient-to-steady ratio should be the eigenvector supports of the slowest or most non-normal modes. If 2.1's gains concentrate on nodes the spectrum does not flag, the spectral story is wrong.

### 2.3 Linear time-invariant reading: transfer functions and frequency response

What it is. The encoder is already an LTI system in discrete time with state h, input u and output the field; its transfer function is H_c(z) = d (z I - M_c)^(-1) and its frequency response is H_c(e^(i omega)). The fixed point is H_c(1) = (I - A_c)^(-1), the DC gain. Reading only DC is reading only the zero-frequency component.

What changes. For a drug dosed with interval T_dose, the input is periodic and the output at a node is the DC gain times the mean dose plus the response at omega = 2 pi / T_dose times the peak-trough excursion. A readout of |H_c(e^(i omega))| u at the dosing frequency and at omega = 0 gives the model, for the first time, a peak reading and a trough reading. For gene perturbations only omega = 0 applies, which is right: a knockout is a DC input.

Data. Dosing intervals and half-lives per study drug. Public: the FDA labels the repository already parses (docs/label_central_action.md reads label sections; the dosage and administration and clinical pharmacology sections carry t_half and the interval), the Lombardo 2018 intravenous pharmacokinetics table already recorded in docs/exposure_sources/lombardo2018.md and the Schulz 2020 therapeutic concentration table in docs/exposure_sources/schulz2020.md. DrugBank's half-life field is an alternative source under its licence; the repository rule is to verify licence first.

Compute. One sparse complex linear solve per (drug, frequency, channel), equivalent to one fixed-point iteration with a complex shift; cheaper than training. The frequency response does not need to be learned, only read, and it can be cached per drug.

Dawid-Skene. None directly. It does give the evidence model a new feature if the owner later wants it: a label event that is a peak effect (sedation, hypotension) against one that is a trough effect; MedDRA does not carry this, so it would have to be curated, and that is the weak point.

Validation. Compare the peak-reading against the DC reading on sedation-type labels within drugs that share a target but differ in half-life (zolpidem against flurazepam at GABA-A; lorazepam against diazepam). Falsified if the half-life stratification does not change the ranking of these pairs, or if drugs with long half-lives, for which peak and trough coincide, are not predicted better by DC alone.

Honest limit. This does not fix any of 1.1, 1.2, 1.4, 1.5, 1.6; it fixes 1.10 only and partially 1.9 (frequency separates fast from slow relations if their gains are read as rate constants, which they are not).

### 2.4 Multi-timescale propagation: separate relaxation rates per edge class, two or more equilibria

What it is. Give each relation a relaxation rate k_r (per round) so that the update is

    h(t + 1) = h(t) + sum_r k_r (g_r S_r h(t) - h(t) ... )

in the form of a first-order linear ODE discretised by forward Euler with per-relation time constants, or more simply keep the damped iteration and freeze the slow relations (regulates_transcription_of, encodes, the trafficking edges when they exist) at zero gain in a fast copy of the operator. Read two fixed points: h*_fast with slow relations frozen and h*_full with everything on. This is the proposal already written in docs/drug_entry_nodes.md section F and not built.

Readout. Concatenate [h*_fast, h*_full] (2 C channels) and let the modules choose. h*_full - h*_fast is the adaptation term: what transcription and expression change contributes on top of the acute response. A relieves label is tied to h*_full; an induces label can be read from either.

Data. A rate class per relation. This is a lookup, not a dataset: binding and catalysis fast, transport and metabolite pools intermediate, transcription and expression slow. Three classes are defensible from textbook kinetics without a source per edge; more than three invites invented numbers.

Compute. Two fixed points per batch instead of one, so twice the propagation cost, with the fast one converging in fewer rounds because the frozen relations shorten paths. Fits within the current 4-hour fold budget if --max-epochs is held.

Dawid-Skene. The reliability model's item is a (perturbation, symptom, relation) triple; it does not know which equilibrium a report refers to. If the owner later adds a time-to-onset field to the report table (the evidence table has none: "No temporal field anywhere", docs/missing_physiology_review.md), the item could carry "acute" or "chronic" and the loss could tie acute reports to h*_fast. Without that field, the choice of equilibrium is left to the module gates, which is weaker but needs nothing new.

Validation. On the benzodiazepine set, sedation and anxiolysis labels against the same drug: if h*_full - h*_fast carries module mass for sedation (tolerance develops) and not for anxiolysis (it does not) [17], the two-equilibria reading has done what it was built to do. Falsified if the module gates on the difference channel stay near zero or if the twin against the single-equilibrium model includes zero.

Identifiability. This is the proposal that most tempts the owner to add free time constants per relation. Do not: with 26 gains per channel already and under 4,000 labelled observations, a learned k_r per relation is weakly identified and would mostly fit the degree structure. Fix the rate classes by hand and learn only the gains, as now.

### 2.5 Explicit homeostatic controller nodes and integral-control motifs

What it is. Add to the graph, as typed nodes and edges with their own relation, the adaptation loops that the review found missing or wrongly signed: GRK and arrestin desensitisation of each psychiatric GPCR (the five existing receptor-to-arrestin edges are for CCR7, PTH1R, CHRNA7, GPR182 and LHCGR, none psychiatric; docs/missing_physiology_review.md section 4), autoreceptor feedback on monoamine release (5-HT1A on raphe firing [8], D2 autoreceptors), transporter upregulation, receptor-density adaptation to chronic occupancy [6]. Each loop is the "negative feedback loop with a buffering node" of the adaptation design table [3], and an integrating buffer node is a node with a self-edge of weight near 1 under its own relation (integrates). The antithetic integral motif, two species that annihilate each other, is the stochastic version of the same thing [29] and is not needed here.

Readout. If the loops are closed and the readout stays h*, the model gains correct steady states for adaptation (the receptor's steady output returns toward baseline, the receptor density ends up raised) but not the transient. Combined with 2.1 it gains both. This is the one proposal where the readout change and the graph change multiply: 2.1 without 2.5 reads transients of the wrong loops; 2.5 without 2.1 reads the correct steady state of loops whose point is the transient.

Data. Curated and small. The GRK/arrestin edges exist (116, mostly wrongly signed) and need a sign recuration under the repository's existing regulation_sign_recuration procedure (decision 9.72). Autoreceptor pairs: docs/curated_presynaptic_receptors.csv already exists. Receptor-density adaptation to chronic antagonism is in the literature for D2 [6][7] and for GABA-A subunits [17] and would be a dozen rows. Sources: Guide to PHARMACOLOGY for receptor-arrestin coupling, Reactome's "GPCR downstream signalling" and "Arrestin-mediated" pathways which the build already imports, SIGNOR for signed directed edges with a mechanism field.

Compute. A few hundred edges and a new relation: nothing.

Dawid-Skene. None for the labels. For the edge gates (decision 9.57), the new edges get an evidence prior like any other; a curated loop with two PubMed ids is a tier the system already has.

Validation. Direct and cheap: with the D2 adaptation loop closed, a chronic D2 antagonist's h*_full should raise D2 receptor density (the Burt 1977 finding [6]) and lower the net D2 blockade relative to h*_fast; a 5-HT reuptake blocker's h*_full should show raphe firing recovered relative to h*_fast [8]. These are sign checks on named nodes that need no symptom labels and could be in the comparative_checks.csv of the preregistration. Falsified if the signs come out wrong with the loop closed, which would mean the loop's own signs or normalisation are wrong.

### 2.6 Signal propagation as a weighted sum over walks (path-integral reading)

What it is. The fixed point is itself a walk sum, h* = sum_k A_c^k u, every walk length weighted equally. A length-dependent weighting replaces it with h_f = sum_k f(k) A_c^k u. With f(k) = 1 / k! this is the communicability e^(A_c) u, "a broad generalization of the concept of the shortest path" [30]; with f(k) = beta^k it is the Katz index; with f(k) = e^(-k / tau) it is a resolvent at a different point. The transient readouts of 2.1 are also walk sums: the round-T state is sum_(k <= T) (binomial weights from the damping) A_c^k u.

Readout. Choose f per channel, or learn a small parametric f (two parameters, scale and decay) per relation class. The physiological reading: a fast relation should contribute at any walk length, a slow one only on short walks within the observation window. That is a length-dependent weighting by relation, which reduces to 2.4.

Data. None.

Compute. Communicability by Krylov methods (expm_multiply) costs a few dozen sparse matvecs per perturbation; comparable to the current loop.

Dawid-Skene. None.

Validation. Against the random walk with restart baseline, which is the Katz-type walk sum the trained models have not beaten (finding 5). If a signed communicability beats the unsigned walk on the disease-cluster split, the sign information and the walk weighting both carry signal; if it ties, the sign information is not being read by any walk weighting and section 3's argument that the signs are the problem gains weight.

### 2.7 Nonlinear fixed point: deep equilibrium reading with saturating nodes

What it is. Keep the fixed-point readout but make the update nonlinear, h = phi(A_c h + u) with a non-expansive phi (tanh or a bounded saturating map), and differentiate through the fixed point by the implicit function theorem. In machine learning this is the deep equilibrium model; the repository's own note says "The canonical references could not be verified from this workspace" [docs/label_source_review.md 19.2] and I will not add them from memory either; the owner should add them from arXiv. In systems biology it is the steady state of a saturating (Michaelis-Menten or Hill) network.

What it fixes. 1.2 partly (a saturating node is where a desensitised receptor's output flattens), 1.11's mirror symmetry (phi need not be odd), the "a knockout is not small" objection to linear response [docs/drug_entry_nodes.md F]. What it does not fix: anything in the transient (1.1, 1.4, 1.5, 1.10) and it still forbids multistability if phi is contractive; allowing multistability means dropping the contraction and then the fixed point depends on the initial state, which is a feature (hysteresis) and a training nightmare (which basin).

Data. None for tanh; Michaelis-Menten constants per reaction for a kinetic phi, which BRENDA supplies under CC BY 4.0 (docs/missing_physiology_review.md section 7) for a minority of the 13,793 reactions.

Compute. Implicit differentiation costs one extra linear solve per backward pass, around the cost of the forward loop. Fits the budget.

Dawid-Skene. None.

Validation. Sign check (finding 10) first: a nonlinear fixed point that still scores 0.615 has not helped. Then the twin.

### 2.8 Boolean and multi-valued logic with asynchronous update; attractor and basin analysis

What it is. Discretise node states (0/1 or 0/1/2), write each node's update as a logic function of its inputs, clamp the perturbed node ("fixing the activity value of the drug target component to the Boolean value 0", the method used to predict drug synergies in gastric cancer cells with four of five predictions confirmed [31]), and compute attractors under asynchronous update, which exists precisely because synchronous update "fails to take into account the variety of time scales associated with different types of biological processes" [32]. The readout is the attractor reached (a fixed point or a cyclic attractor) and the basin sizes.

What it fixes. Multistability and oscillation (1.6, 1.7) become representable: a cyclic attractor is an oscillator and several attractors are multistability. Logic can encode AND (a complex needs all members) and OR, which the message-passing minimum and the linear mean conflate [docs/physiological_adherence_review.md section 10].

What it costs. Everything quantitative. Logic has no magnitude, no dose and no stoichiometry, so the linear encoder's one real advantage (conserved currencies, stoichiometric reversal) is gone. And the state space is 2^N: attractor analysis on 34k nodes is impossible without reduction, and the reduction methods that provably conserve attractors [33] are for networks of tens to hundreds of nodes. The realistic form is a logic model of a few hundred curated nodes (the psychiatric receptor, autoreceptor, transporter and clock subgraph) as a module beside the linear encoder, not a replacement.

Data. Logic rules per node; CellCollective, the BioModels qualitative models and SIGNOR's signed directed edges give rules for signalling but not for the metabolic layer.

Compute. Simulation of a few hundred nodes is cheap; it is the curation that costs.

Dawid-Skene. None.

Validation. Does the logic module predict the known cyclic attractor of the clock subgraph under no perturbation and its loss under CRY or PER perturbation? That is a known-answer test with no symptom labels. Falsified if the curated rules do not reproduce the published attractors before any symptom is fitted.

### 2.9 Kinetic ODE models where parameters exist (mass action, Michaelis-Menten)

What it is. For the subgraph where rate constants are known, write dx/dt = S v(x; k) with the stoichiometric matrix S and kinetic laws v, integrate from the baseline with the perturbation applied and read the trajectory. This is what the whole field of dynamic metabolic modelling does for pathways of tens of reactions.

What it fixes. Everything in section 1 that the subgraph covers, with real time on the axis.

What it costs. Parameters. BRENDA has K_m and k_cat for a minority of human reactions, measured in vitro, often not in brain. Human-GEM has 13,793 reactions. No genome-scale kinetic model of human metabolism exists with validated parameters, and the attempt would produce a model whose predictions are set by the parameters the owner guessed. The Dawid-Skene machinery cannot help: it weights evidence about labels, not evidence about rate constants.

Where it is worth it. The one-carbon and monoamine subgraph, for which the mathematical models already exist and have been used to study homeostasis of homocysteine and extracellular dopamine [4]. A twenty-reaction kinetic model of monoamine synthesis, release, reuptake and degradation, run under each drug's occupancy, would give dopamine and serotonin time courses that the linear encoder could take as an input channel. That is a bounded project.

Compute. Trivial for twenty reactions; the ODE solve per perturbation is milliseconds.

Validation. Against measured CSF or microdialysis monoamine changes under the study drugs where they exist in humans (the repository's effect-site review lists the sparse human CSF data).

### 2.10 Constraint-based dynamics for the metabolic subgraph (dynamic FBA, regulatory FBA)

What it is. Dynamic FBA solves a flux balance problem at each time step with uptake bounds updated from the external concentrations, "a framework for analyzing the transience of metabolism due to metabolic reprogramming" [34]; regulatory FBA adds Boolean transcriptional rules as time-dependent flux bounds, which "sharply reduces the number of active extreme pathways" [35][36].

Why it does not fit. Both need an objective function, and the repository's position is right: "the brain has no defensible single objective; sampling is the planned route" [docs/research_summary.md section 5]. Flux sampling over time is possible but the sampled distribution at each step is unconstrained by any dynamics unless an objective closes it. Regulatory FBA's transcriptional rules would, however, be the natural place for the two-equilibria idea of 2.4 inside the metabolic layer: a fast FBA with enzyme capacities fixed and a slow one with capacities moved by the transcriptional layer's h*.

Data. The transcriptional rules already exist as CollecTRI edges; enzyme capacity bounds would come from brain proteomics (the brain expression weights the graph already carries).

Compute. One LP per reaction set per step; the flux-sampling array job exists (slurm/flux_sampling_array.sbatch) and has not been run.

Validation. The B4 flux-feature baseline that Aim 3 already names; the dynamic version is a step after that one has run.

### 2.11 Neural ODE or continuous-depth graph network

What it is. Replace the fixed iteration with dh/dt = f_theta(h, u, graph) integrated by an adaptive solver, with f_theta a learned message-passing function. Continuous depth gives a time axis and adaptive step counts.

Why it ranks last among the retrofits. The time axis it gives is not physiological unless f_theta is constrained to be, and the constraints that would make it so (per-relation rates, saturation, conservation) are exactly 2.4, 2.7 and 2.9 again, now with a learned function in the middle that the labels cannot identify. A neural ODE on 34k nodes with 4,000 labels and a 4-hour wall clock will learn a smooth interpolant of the degree structure. The adjoint method's memory is attractive, the identifiability is not. I would not build this before 2.4 and 2.5 have been tried, and I would not expect it to beat them.

Compute. Adaptive solvers make the per-batch cost unpredictable, which is a problem under a hard wall clock with checkpoint-on-signal.

Dawid-Skene. None.

### 2.12 Full redesign: a curated dynamic core inside a static scaffold

What it would be. Keep the genome-scale signed graph as a static scaffold that computes h* (it does something: the wiring carries label signal, finding 8). Inside it, build a dynamic core of a few hundred nodes, the psychiatric pharmacology that the labels actually concern: monoamine synthesis, release, reuptake and degradation; the GPCRs with their GRK/arrestin loops and density adaptation; GABA-A and NMDA with subunit composition; the clock loop; the HPA axis if organ labels are ever added. Model the core as a kinetic or logic system with real time (2.8 or 2.9), driven by the scaffold's h* at its boundary and by each drug's pharmacokinetic forcing (2.3), and read from it the features that section 1 says matter: peak, integrated deviation, adapted steady state, rebound on withdrawal, period and phase of the clock. The scaffold's job becomes computing how a distant metabolic perturbation reaches the core's boundary; the core's job is to turn that into a time course.

Why last. It abandons the project's distinguishing claim, that the whole physiology graph is the model. It also adds curated structure of exactly the kind the owner refuses for symptoms ("no hard symptom-level constraints"), though not for mechanisms, where the owner accepts curated edges (the sodium channel families, the VGLUT loading reaction). It is the right design if the week's experiments in section 4 show that the readout is the limit; it is the wrong design if they show the graph is.

## 3. Criticism of the framing

3.1 The evidence does not yet say the steady state is the culprit.

The strongest fact in the repository is finding 10: the untrained linear response predicts the direction of measured metabolite changes with 0.615 sign agreement against 0.806 for always guessing "increased", on 1,067 gene-metabolite pairs from HPO laboratory abnormalities. Those labels are steady-state measurements of patients in a lifelong steady state. A steady-state model is the right model for them and it still fails. More: docs/linear_response_sign_check.md reads the response at 8, 32 and 128 steps and the sign agreement moves from 0.615 to 0.596 to 0.593. If the transient carried the missing information, the round-8 reading (a transient) would differ from the round-128 reading (the fixed point) in a direction that mattered. It does not. On this test, where the steady state is the right object, the problem is not the readout.

What the sign check does implicate: the reversible-reaction cancellation (15,867 pairs, 1,809 metabolites with identically zero field, docs/physiological_adherence_review.md section 2), the per-node averaging that annihilates production against consumption at 92 percent of metabolites that receive both signs (finding 11), the one-elasticity-per-relation parameterisation (26 gains for 280,966 edges), and the input magnitude (a knockout at magnitude 1 under a small-change linearisation). All four are about what A_c is, not about reading its fixed point.

3.2 The dead ends are not a steady-state problem either.

186 gene perturbations with no route past their own protein, five drugs that inject nothing, nine channel families with no conduction route (decisions 9.68, 9.69, 9.71). No readout of any kind sees past a missing edge. These are 8.4 percent of perturbations and 6.8 percent of positive gene pairs, and the fix is edges (pull requests #2 and #3 exist). The 3,795 regulation edges with opposite signs between the two CollecTRI releases, 1,930 of them labels (decision 9.72), are the same: a transient readout of a wrong-signed edge is a wrong-signed transient.

3.3 What would distinguish the three causes.

Graph incompleteness: stratify every score by the perturbation's reach (experiments/measure_perturbation_reach.py already computes it). If the model trails the random walk only on low-reach perturbations and ties it on high-reach ones, the graph is the limit. The repository has the analogous stratification for split pathways (finding 13) and it was informative.

Sign errors: the sign ablations exist (EDGE_SIGNS all_positive and permuted). If the all-positive model scores the same as the signed one, the signs are not being read; if the permuted model scores the same as the signed one, the signs are being read but are wrong as often as right. Finding 15 found edge direction neither costs nor adds for the walk. Finish the sign ablation (one fold of five was running at the last summary) before touching the readout.

Label noise: the Dawid-Skene posterior gives a reliability per item. Score the model on the top-posterior quartile only. If AUPRC rises sharply there and nowhere else, the ceiling is the labels. The time split's result (finding 4: no baseline predicts later monogenic findings, AUROC 0.432 on publication-dated new positives) is already a warning that the labels do not generalise across time for anything, which no readout fixes.

Steady state: the test that isolates it is 2.1 against h* on the drug labels only, where the transient arguments of section 1 apply, stratified by whether the label event is one pharmacology calls acute (sedation, nausea, orthostasis) or adaptive (tardive dyskinesia, withdrawal insomnia, tolerance). That stratification does not exist and would have to be curated from MedDRA preferred terms; it is the cheapest piece of new data in this report and the one that would make the steady-state question answerable.

3.4 Which fixes worsen identifiability.

Any free time constant per relation (2.4 done badly, 2.11 always) multiplies parameters against a label set of under 4,000 observations and 25 symptoms of which several have fewer than 100 positives. The two-equilibria version of 2.4 with hand-fixed rate classes adds zero parameters to the operator and C channels to the head; that is the only version to build. Per-reaction kinetic parameters (2.9 at scale) are unidentifiable from symptom labels and must come from BRENDA or not at all. Nonlinear fixed points (2.7) that permit multistability make the output depend on the initial state and so make every training example depend on an unobserved basin; keep the contraction unless the owner wants to model switches explicitly with a basin label. A neural ODE's f_theta is an unconstrained function and will absorb the degree structure first, as the trained encoders already do (findings 5 and 16: a trained readout on the walk's own distributions does not beat the untrained walk).

3.5 One thing the framing gets right.

The owner's intuition is correct for a definable subset of the drug labels: tolerance, withdrawal, rebound, supersensitivity and peak-concentration adverse events are transient or adaptive phenomena and a fixed point cannot represent them (1.4, 1.5, 1.10). For gene perturbations and for trial outcomes the steady state is the right object and the owner should resist the temptation to abandon it there. The project's own two-equilibria note (docs/drug_entry_nodes.md F) is the sharpest statement of this already in the repository and it was never built.

## 4. Experiments for this week

Each is runnable on the existing code and data release, needs no new graph, and has a stated null.

4.1 Trajectory readout twin (2.1). Add a --readout-features flag to LinearResponseEncoder.response that returns [h*, signed peak, integrated deviation] as 3 C channels (the loop already holds every state; keep a running max and sum). Train the b6_linear_response configuration with and without it, five folds, disease-cluster split, the existing batch driver and aggregator. Null: the paired-bootstrap interval of the twin includes zero and the module gate mass on the peak and integral channels is under 10 percent. Cost: two five-fold runs, about ten 4-hour jobs. Also run the sign check with the peak feature: null is sign agreement within 0.02 of 0.615, which I predict.

4.2 Spectrum of the operator (2.2). One script, no training: build the registered encoder on v0.4 graph_full, extract A_c for each untrained channel, run scipy.sparse.linalg.eigs for the 100 largest-magnitude eigenvalues, report |mu_k|, time constants, complex pairs, and the eigenvector supports (which node types, which subsystems). Then compute the numerical abscissa of A_c (largest eigenvalue of (A_c + A_c^T) / 2) against its spectral radius: the ratio is the cheapest measure of non-normality. Null: no complex pairs, numerical abscissa within a factor of 1.5 of the spectral radius, slow modes supported on currency-adjacent hubs only. A positive result (complex pairs on the clock subgraph, large non-normality on the metabolic layer) tells the owner where 4.1 should find signal and makes 4.1 interpretable.

4.3 Acute-against-adaptive stratification of the drug labels (3.3). Curate a two-column file of MedDRA preferred terms in the symptom crosswalk: acute (sedation, somnolence, dizziness, nausea, agitation on initiation) against adaptive (tardive dyskinesia, withdrawal syndrome terms, rebound insomnia, tolerance, dependence). Score the existing trained runs on the two strata separately. Null: the model's deficit against the random walk is the same in both strata. If the deficit is concentrated in the adaptive stratum, the steady-state argument has its first direct evidence; if it is uniform, the readout is not the limit.

4.4 Reach stratification (3.3). Join experiments/measure_perturbation_reach.py output to the existing fold predictions and score by reach tercile. Null: the deficit against the random walk is the same across terciles. This runs in minutes.

4.5 Two-equilibria probe, untrained (2.4). Freeze regulates_transcription_of and encodes gains at zero in a copy of the operator and compute h*_fast beside h*_full for the 222 drugs; report the nodes where they differ most and in which direction. Null: the difference is below 1e-6 everywhere a label lands, meaning the transcription layer does not reach the labelled symptoms' modules at all, which would send the owner back to the graph rather than to the readout. Positive: D2 and 5-HT1A density nodes differ in the directions of [6] and [8]. Since the GRK/arrestin signs are known to be wrong (94 of 116), the positive result is not expected until decision 9.72's recuration reaches those edges, and the probe would show that.

4.6 Finish the sign ablations (3.3). The all_positive and permuted arms were one fold of five at the last summary. Finishing them costs eight jobs and decides whether any readout change can matter: if the signed, all-positive and permuted operators tie, the readout is not reading signs, and section 1 is moot until it does.

The order I would run them: 4.4 and 4.2 today (no training), 4.6 and 4.1 submitted tonight, 4.3 curated while they run, 4.5 when 4.2 says where to look.

## References

[1] N. Barkai and S. Leibler, "Robustness in simple biochemical networks," Nature, vol. 387, no. 6636, pp. 913-917, 1997. doi:10.1038/43199
[2] T. M. Yi, Y. Huang, M. I. Simon and J. Doyle, "Robust perfect adaptation in bacterial chemotaxis through integral feedback control," Proc. Natl. Acad. Sci. USA, vol. 97, no. 9, pp. 4649-4653, 2000. doi:10.1073/pnas.97.9.4649
[3] W. Ma, A. Trusina, H. El-Samad, W. A. Lim and C. Tang, "Defining network topologies that can achieve biochemical adaptation," Cell, vol. 138, no. 4, pp. 760-773, 2009. doi:10.1016/j.cell.2009.06.013
[4] H. F. Nijhout, J. Best and M. C. Reed, "Escape from homeostasis," Math. Biosci., vol. 257, pp. 104-110, 2014. doi:10.1016/j.mbs.2014.08.015
[5] R. R. Gainetdinov, R. T. Premont, L. M. Bohn, R. J. Lefkowitz and M. G. Caron, "Desensitization of G protein-coupled receptors and neuronal functions," Annu. Rev. Neurosci., vol. 27, pp. 107-144, 2004. doi:10.1146/annurev.neuro.27.070203.144206
[6] D. R. Burt, I. Creese and S. H. Snyder, "Antischizophrenic drugs: chronic treatment elevates dopamine receptor binding in brain," Science, vol. 196, no. 4287, pp. 326-328, 1977. doi:10.1126/science.847477
[7] G. Chouinard et al., "Antipsychotic-induced dopamine supersensitivity psychosis: pharmacology, criteria, and therapy," Psychother. Psychosom., vol. 86, no. 4, pp. 189-219, 2017. doi:10.1159/000477313
[8] P. Blier and N. M. Ward, "Is there a role for 5-HT1A agonists in the treatment of depression?," Biol. Psychiatry, vol. 53, no. 3, pp. 193-203, 2003. doi:10.1016/s0006-3223(02)01643-8
[9] M. J. Taylor, N. Freemantle, J. R. Geddes and Z. Bhagwagar, "Early onset of selective serotonin reuptake inhibitor antidepressant action: systematic review and meta-analysis," Arch. Gen. Psychiatry, vol. 63, no. 11, pp. 1217-1223, 2006. doi:10.1001/archpsyc.63.11.1217
[10] O. Agid, S. Kapur, T. Arenovich and R. B. Zipursky, "Delayed-onset hypothesis of antipsychotic action: a hypothesis tested and rejected," Arch. Gen. Psychiatry, vol. 60, no. 12, pp. 1228-1235, 2003. doi:10.1001/archpsyc.60.12.1228
[11] C. L. Bowden et al., "Effect size of efficacy measures comparing divalproex, lithium and placebo in acute mania," Depress. Anxiety, vol. 6, no. 1, pp. 26-30, 1997. doi:10.1002/(sici)1520-6394(1997)6:1<26::aid-da4>3.0.co;2-3
[12] C. A. Zarate et al., "A randomized trial of an N-methyl-D-aspartate antagonist in treatment-resistant major depression," Arch. Gen. Psychiatry, vol. 63, no. 8, pp. 856-864, 2006. doi:10.1001/archpsyc.63.8.856
[13] G. F. Koob and M. Le Moal, "Drug addiction, dysregulation of reward, and allostasis," Neuropsychopharmacology, vol. 24, no. 2, pp. 97-129, 2001. doi:10.1016/S0893-133X(00)00195-0
[14] E. J. Nestler and G. K. Aghajanian, "Molecular and cellular basis of addiction," Science, vol. 278, no. 5335, pp. 58-63, 1997. doi:10.1126/science.278.5335.58
[15] R. J. Baldessarini, L. Tondo and A. C. Viguera, "Discontinuing lithium maintenance treatment in bipolar disorders: risks and implications," Bipolar Disord., vol. 1, no. 1, pp. 17-24, 1999. doi:10.1034/j.1399-5618.1999.10106.x
[16] H. C. Porchet, N. L. Benowitz and L. B. Sheiner, "Pharmacodynamic model of tolerance: application to nicotine," J. Pharmacol. Exp. Ther., vol. 244, no. 1, pp. 231-236, 1988. PMID 3336000
[17] C. H. Vinkers and B. Olivier, "Mechanisms underlying tolerance after long-term benzodiazepine use: a future for subtype-selective GABA(A) receptor modulators?," Adv. Pharmacol. Sci., vol. 2012, 416864, 2012. doi:10.1155/2012/416864
[18] D. Angeli, J. E. Ferrell and E. D. Sontag, "Detection of multistability, bifurcations, and hysteresis in a large class of biological positive-feedback systems," Proc. Natl. Acad. Sci. USA, vol. 101, no. 7, pp. 1822-1827, 2004. doi:10.1073/pnas.0308265100
[19] S. D. M. Santos, P. J. Verveer and P. I. H. Bastiaens, "Growth factor-induced MAPK network topology shapes Erk response determining PC-12 cell fate," Nat. Cell Biol., vol. 9, no. 3, pp. 324-330, 2007. doi:10.1038/ncb1543
[20] C. J. Marshall, "Specificity of receptor tyrosine kinase signaling: transient versus sustained extracellular signal-regulated kinase activation," Cell, vol. 80, no. 2, pp. 179-185, 1995. doi:10.1016/0092-8674(95)90401-8
[21] I. Laothamatas, E. S. Rasmussen, C. B. Green and J. S. Takahashi, "Metabolic and chemical architecture of the mammalian circadian clock," Cell Chem. Biol., vol. 30, no. 9, pp. 1033-1052, 2023. doi:10.1016/j.chembiol.2023.08.014
[22] B. N. Kholodenko, "Negative feedback and ultrasensitivity can bring about oscillations in the mitogen-activated protein kinase cascades," Eur. J. Biochem., vol. 267, no. 6, pp. 1583-1588, 2000. doi:10.1046/j.1432-1327.2000.01197.x
[23] J. R. Huguenard and D. A. McCormick, "Thalamic synchrony and dynamic regulation of global forebrain oscillations," Trends Neurosci., vol. 30, no. 7, pp. 350-356, 2007. doi:10.1016/j.tins.2007.05.007
[24] J. Guy, J. Gan, J. Selfridge, S. Cobb and A. Bird, "Reversal of neurological defects in a mouse model of Rett syndrome," Science, vol. 315, no. 5815, pp. 1143-1147, 2007. doi:10.1126/science.1138389
[25] Y. Sztainberg et al., "Reversal of phenotypes in MECP2 duplication mice using genetic rescue or antisense oligonucleotides," Nature, vol. 528, no. 7580, pp. 123-126, 2015. doi:10.1038/nature16159
[26] N. L. Dayneka, V. Garg and W. J. Jusko, "Comparison of four basic models of indirect pharmacodynamic responses," J. Pharmacokinet. Biopharm., vol. 21, no. 4, pp. 457-478, 1993. doi:10.1007/BF01061691
[27] G. Hennequin, T. P. Vogels and W. Gerstner, "Non-normal amplification in random balanced neuronal networks," Phys. Rev. E, vol. 86, 011909, 2012. doi:10.1103/PhysRevE.86.011909
[28] B. K. Murphy and K. D. Miller, "Balanced amplification: a new mechanism of selective amplification of neural activity patterns," Neuron, vol. 61, no. 4, pp. 635-648, 2009. doi:10.1016/j.neuron.2009.02.005
[29] C. Briat, A. Gupta and M. Khammash, "Antithetic integral feedback ensures robust perfect adaptation in noisy biomolecular networks," Cell Syst., vol. 2, no. 1, pp. 15-26, 2016. doi:10.1016/j.cels.2016.01.004
[30] E. Estrada and N. Hatano, "Communicability in complex networks," Phys. Rev. E, vol. 77, 036111, 2008. doi:10.1103/PhysRevE.77.036111
[31] Å. Flobak et al., "Discovery of drug synergies in gastric cancer cells predicted by logical modeling," PLoS Comput. Biol., vol. 11, no. 8, e1004426, 2015. doi:10.1371/journal.pcbi.1004426
[32] A. Saadatpour, I. Albert and R. Albert, "Attractor analysis of asynchronous Boolean models of signal transduction networks," J. Theor. Biol., vol. 266, no. 4, pp. 641-656, 2010. doi:10.1016/j.jtbi.2010.07.022
[33] A. Saadatpour, R. Albert and T. C. Reluga, "A reduction method for Boolean network models proven to conserve attractors," SIAM J. Appl. Dyn. Syst., vol. 12, no. 4, pp. 1997-2011, 2013. doi:10.1137/13090537X
[34] R. Mahadevan, J. S. Edwards and F. J. Doyle, "Dynamic flux balance analysis of diauxic growth in Escherichia coli," Biophys. J., vol. 83, no. 3, pp. 1331-1340, 2002. doi:10.1016/S0006-3495(02)73903-9
[35] M. W. Covert, C. H. Schilling and B. Palsson, "Regulation of gene expression in flux balance models of metabolism," J. Theor. Biol., vol. 213, no. 1, pp. 73-88, 2001. doi:10.1006/jtbi.2001.2405
[36] M. W. Covert and B. O. Palsson, "Constraints-based models: regulation of gene expression reduces the steady-state solution space," J. Theor. Biol., vol. 221, no. 3, pp. 309-325, 2003. doi:10.1006/jtbi.2003.3071

Also consulted and cited by repository path rather than number: R. Heinrich and T. A. Rapoport, Eur. J. Biochem. 42:89-95 and 97-105, 1974 (the linear steady-state treatment the encoder cites; doi:10.1111/j.1432-1033.1974.tb03319.x for the second paper); A. Liu et al., "From expression footprints to causal pathways: contextualizing large signaling networks with CARNIVAL," NPJ Syst. Biol. Appl. 5:40, 2019, doi:10.1038/s41540-019-0118-z, as the standard sign-consistency approach the project's sign ablation can be compared with; U. Alon, "Network motifs: theory and experimental approaches," Nat. Rev. Genet. 8:450-461, 2007, doi:10.1038/nrg2102, for the motif vocabulary of section 2.5.

Not verified and therefore not cited: the deep equilibrium model papers (Bai, Kolter and Koltun 2019) and the neural ODE paper (Chen et al. 2018) are arXiv and NeurIPS records that the PubMed connector does not index; the repository has the same gap (docs/label_source_review.md 19.2). The owner should add them from arXiv. Trefethen's pseudospectra book is the standard reference for section 2.2's transient growth statements and is likewise not a PubMed record.
