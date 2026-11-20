# Amendment item 37: the owner's rulings of 13 to 20 November 2026, before they are entered in the decision log

A draft, for the owner to act on. It holds the owner's words of 13 to 20 November 2026 on the open parts of decision 9.129
and on the questions that came out of them, each with the session's proposal it answered, so that they are kept in
the repository while the remaining parts are ruled. The owner asked to rule on everything before anything is entered
in `docs/open_decisions.md` ("Let's rule on the rest of it first"). Nothing here is built, and nothing here is a
decision row: once every part is ruled, the contents become rows of `docs/open_decisions.md` (an addition to 9.129
and new decisions with ids taken at that time), and this draft is then deleted or reduced to a pointer to them, as
the owner chooses. It is edited in place: a correction the owner asks for fixes the original wording (CLAUDE.md,
"Pushing").

The research behind the proposals was done by Fable passes of 13 November 2026, each checked for its model tags, the
hosts it read and the SHA-256 of every page it saved. Their findings are summarised here only as far as a ruling
depends on them; the decision rows will carry the sources.

## 1. Design question 1: a reaction whose catalysts span two pore classes

The owner, in this order: "why not map to both classes separately with different nodes for each?"; "well embryonic
doesn't really matter for the muscle receptor composition, right?"; "i still think it's best to split the nodes";
"but the muscles node could be a sink that gets added as the end part of a module supporting i.e. nicotinic blocking
of ganglion preventing downstream depolarization"; on the session's proposal, "accepted proposal but 9.128 and 9.121
C4 remain unchanged"; "Try sourcing the needed data for the split first"; asked whether the muscle node should be
adult-only, "Adult only". Part (iii) of the proposal was then replaced: the owner asked "i guess there's not really a
need to include the muscle neuron nodes so it can be excluded, right?", and to the session's rewording "A pore that
does not sit on a central neuron is not added to the graph. The muscle-type nicotinic receptor is not added, and its
subunits leave the neuronal entities. Decisions 9.121 C4 and 9.128 are unchanged." answered "accepted".

The Fable-drafted addition to 9.129 that records this, as the owner last saw it, is the appendix.

## 2. α7 homomeric nicotinic receptors (A)

- The owner asked "why make a7 hormones their own class and not other hormones?" (read as homomers). The session
  answered that under the registered monovalent weight law a subtype earns a class only when its permeability changes
  its weight, and that the Pf ruling of section 4 makes α7 different in its calcium share.
- **A1, ruled.** A Fable pass found GTEx v10's CHRNA7 value (0.36 TPM brain maximum, below the 1 TPM filter) to be
  the outlier against HPA's regional bulk and the Siletti et al. 2023 nuclei. Proposal: restore CHRNA7 with a curated
  override naming both sources. The owner: "use A1."
- **A2, ruled.** Proposal: α7 as its own class and population; part (ii) splits `RCT_629595` into an α7 node and a
  heteromer node; the heteromer node shares the nicotinic unit of D1; the α7 node takes its own Pf into the Ca²⁺ pool
  and the neuronal nicotinic permeability into `VM_c` unless an α7 value is sourced. The owner: "A2. split".
- **A3, ruled.** Proposal: check whether GTEx under-counts other genes the same way. The owner: "A3. yes". This led to
  section 7.

## 3. CHRNA9 (B)

Proposal: record only that the brain-expression filter removes it (brain maximum 0.07 TPM), which agrees with the
source the 13 November pass read. The owner: "B. sure".

## 4. The divalent-permeability question, a decision of its own

The owner: "use option 3 with the individual potency factors, right? though i would like it if the Ca2+ ion pool
were somehow synced with the VM_c effect". The session read "individual potency factors" as each pore class's own
measured fractional Ca²⁺ current (Pf) and proposed:

> Option 3. (a) A non-selective pore class's calcium share is its own measured Pf, from two sources where possible,
> with any gap stated. (b) Its weight into `VM_c` stays on the registered monovalent law, with the Ca²⁺ share counted
> in full as inward current. (c) Its edge into the cytosolic Ca²⁺ pool is Pf times the current its `VM_c` edge is
> built from; a Ca²⁺-selective pore has Pf = 1. (d) Every input to the cytosolic Ca²⁺ pool, including pumps,
> exchangers and stores, takes the same current unit, decided together with the carrier question of 9.129 (3)(iv).

Asked "Is that reading right, and do you want (d) decided together with the carrier question?", the owner answered
"yes and yes".

- **Disagreeing measurements.** Proposal: native measurements over recombinant, otherwise the range. The owner:
  "native over recombinant otherwise range accepted", then "but only use the range if we can't find a way to reduce it
  to a single scalar or a smaller range".
- **Populations with no measured Pf** (after the 13 November sourcing pass: TRPC1/4/5, TRPC3/6, TRPM2, TRPM6/7, TRPV3
  and NALCN). The options were (a) Pf derived from the pore's P_Ca/P_Na through GHK, flagged; (b) the value of the
  nearest measured relative; (c) no Ca²⁺-pool edge. The owner: "i guess a is fine but can we do something like train a
  model to predict the error to the true value from that calculated value?" The session proposed: (1) search for a
  published empirical relation between Pf and P_Ca/P_Na; (2) if none, fit a simple log-log relation to the channels
  with both measurements, tested leaving out one channel and one channel family at a time; (3) use it only if it beats
  raw GHK out of sample. The owner: "yes". Two Fable passes of 13 and 14 November 2026 found no published relation
  across channel families and fitted 17 channels with both measurements: by leave-one-out logit RMSE, raw GHK 0.83, a
  constant odds factor 0.63, and adding how P_Ca/P_Na was measured (biionic or mixed) 0.65, no better. Proposal:
  derive Pf by GHK times the constant odds factor 0.56, each derived value flagged with its 95 per cent interval of
  ×/÷3.8 and recorded as an order-of-magnitude value, not a measurement. The owner: "Yes".
- **The TRPV1 calibration pair.** The calibration paired TRPV1's Pf from native rat sensory neurones with a P_Ca/P_Na
  from recombinant cells (9.6). Proposal: the matched native pair. The owner: "Yes". A Fable check of 14 November 2026
  reduced the two native ratios, 1.9 (Nagy and Rang 1999, 10 mM Ca²⁺) and 0.24 (Oh et al. 1996, 100 mM Ca²⁺), to
  Nagy and Rang's on the conditions of the Pf measurement. The owner then asked "we probably shouldn't be using the
  simplified equation though, right? since we're already using the linearized GHK proxy": a paper's P_Ca/P_Na is its
  reversal potential put through the paper's own equation, and feeding it into the build's GHK mixes two models.
  Proposal: re-derive every ratio, calibration and gap alike, from its paper's reversal potentials and solutions with
  the equation the prediction uses, and refit. Before that, the owner asked "let's ensure that the GHK form that the Pf
  derivation uses is the most appropriate form". The session found the calibration comparing GHK's net Ca²⁺ share with
  each measured Pf but predicting the gap populations' inward share, and proposed the net share on both sides, since a
  dye-overload Pf measures the net share and ruling (c) builds the pool edge from the net current of the pore's
  `VM_c` edge. The owner: "your reading of the ruling is correct. yes, please run the fable pass". A Fable pass of 16 November 2026 recommended
  the form: activities rather than concentrations, one convention in derivation and prediction (Ca²⁺ about 0.30 and
  the monovalent ions about 0.72, Guggenheim, with MacInnes as a sensitivity check; two new sourced constants, no
  registered value moved); each P_Ca/P_Na derived as the exact zero of the same current equation at the paper's
  own absolute reversal potential, with no shortcut formula; each row read with its own solutions and
  temperature; no surface-charge term, the densities being available for one channel only; and no model beyond
  the constant-field equations, since none has usable per-channel parameters. The owner, 16 November 2026:
  "for decision 3a, scuggestions accepted". The form costs seven of the 17 calibration rows for want of
  reversal potentials or solutions, so a Fable pass was started to recover them before the refit; the owner
  asked to be given the papers it cannot retrieve ("ask me to retrieve DOIs for papers that can't be
  retrieved"). The factor and interval are measured by that refit and are not yet known; the 0.62 and ×/÷2.7
  found with the native TRPV1 pair under the old convention are superseded by it.
- **Which measurement a gap population's P_Ca/P_Na comes from.** TRPC4 (1.1 to 77 in the Concise Guide), TRPC5
  (1.8 to 9.5) and TRPV3 have no measured Pf and published ratios that disagree widely. The session proposed taking
  the measurement whose conditions are nearest the build's, not an average, since measurements under different
  conditions measure different things. The owner asked "wouldn't the bionic version be preferable for the TRPC
  proteins since they admit multiple ions and, under the GHK equation, this changes what the Pf for Ca would be?";
  the session agreed for channels with no measured P_K/P_Na, because a ratio derived from a mixed solution then rests
  on the assumption P_K = P_Na while a biionic one does not, and the high-calcium bias of a biionic recording is not
  systematic (the calibration's method term changed sign; Jatzke et al. 2002's pairs go ×2.0, ×1.1 and ×0.29) and
  lies inside the factor's interval. Ruled (the owner, 16 November 2026: "yes, that captures it"), the measurement
  ranked by: (1) re-derivable under the form above, with reversal potentials and both solutions in a patch-clamped
  cell; (2) subunit composition matching the population (TRPC1/4 or TRPC1/5 heteromers for that population);
  (3) a biionic solution where the channel has no measured P_K/P_Na, otherwise a mixed solution near 2 mM Ca²⁺;
  (4) native neurons, then mammalian cell lines; (5) human; (6) temperature nearest 37 °C. A range is kept only where
  two measurements tie on every criterion and still disagree.
- **Criterion 3 revised.** After the ranking was ruled, Zeilhofer et al. 1997 showed TRPV1's Pf in 145 mM Na⁺
  following GHK with P_Ca/P_Na about 2.4, against 11.7 from Nagy and Rang 1999's sodium-free NMDG recordings, and
  Estacion et al. 2006 recorded the same TRPC6 channel reversing at -58 mV sodium-free against -7 mV with sodium
  present: a sodium-free biionic recording overstates calcium's share for TRP channels, while the assumption P_K =
  P_Na it was chosen to avoid moves a weight by under 2 per cent (the 9 November pass). Proposed: prefer a
  sodium-containing mixed solution, with P_K = P_Na assumed where unmeasured, and use a sodium-free biionic recording
  only as a flagged fallback. The owner, 16 November 2026: "yes". It changes TRPM6/7's measurement to Monteilh-Zoller
  et al. 2003 (mouse TRPM7, sodium present, -7.2 ± 2.7 mV, n = 39); TRPC3/6 (Estacion 2006) and TRPV3 (Chung et al.
  2005) are unchanged; TRPM2 (Xia et al. 2008) and TRPC1/4 and TRPC1/5 (Storch et al. 2012) have only sodium-free
  measurements and keep them, flagged.
- **NALCN (decision 6).** A Fable pass of 16 November 2026 read Lu et al. 2007 (NALCN alone in HEK cells, sodium-free:
  P_Ca 0.5 against P_Na 1.3), Chua et al. 2020 (the full human complex: no current in 110 mM Ca²⁺ in eight cells; 1 mM
  Ca²⁺ blocks the sodium current by 83 per cent; NALCN alone non-functional) and Bouasse et al. 2019 (the sodium current
  two- to threefold larger at 0.1 than at 2 mM Ca²⁺). Proposal: Pf = 0, since the complex a neuron carries passes no
  detectable calcium, with Lu's value recorded as a disagreement from a preparation Chua finds non-functional. The
  owner: "NALCN Pf = 0 for Ca accepted". Extracellular calcium's block of NALCN's sodium current is decision 9.114's,
  not this one's.
- **A range in a measurement, and how the graph uses it.** A pore's Ca²⁺-pool edge takes one number, so a range
  becomes one value in the build. For TRPV3, whose two activation states disagree (Chung et al. 2005, Table I: +11.7 and
  +3.7 mV), the session offered (a) the geometric mean of the Pf derived at each end, the ends kept as its interval;
  (b) a sensitivity run at both ends; (c) a fit choice, which adds learned parameters; (d) sourcing which state
  prevails. The owner, 16 November 2026: "a plus b for TRPV3 instead of d because the physiological state changes over
  time in a way that matters for Pf, geo mean will give middle of all measured states, and it would also mean carrying
  that expensive sourcing decision into other similar cases that might come up in the future". So (a) and (b), and the
  same for any later case where a channel's measured states disagree.
- **TRPC1/4/5 split.** Storch et al. 2012's two heteromers tie on every criterion and disagree (TRPC4 with TRPC1,
  -27.9 mV; TRPC5 with TRPC1, -53.1 mV; figure readings, sodium-free). Being two channels rather than two states of
  one, they could be two populations under ruling C's co-assembly rule. The owner: "split TRPC1/4/5". So TRPC1/4 and
  TRPC1/5 are two population nodes, each with its own Pf. Under ruling D each takes one unit, so no share between them
  is needed; the cost is one more unit of TRP weight at `VM_c`.

## 5. The non-selective TRP channels (C)

The session first proposed one mixed-cation TRP class with a convention for the set's Pf, which spans about 3 to 24
per cent; the owner: "yikes. that's a wide range. better solution?" The session then proposed: TRPV5 and TRPV6 (no
neuronal expression found in human brain, so not on a central neuron under section 1's part (iii)) and TRPC4AP (a
scaffold, not a pore subunit) leave `RCT_3295579`; the reaction is split into one node per pore population by
co-assembly (TRPC1/4/5, TRPC3/6, TRPM2, TRPM3, TRPM6/7, TRPV1 and TRPV3 among its brain-expressed members, a grouping
the 13 November sourcing pass confirmed), each with its own Pf, and a `VM_c` weight on the mixed-cation law with
P_K = P_Na assumed. The owner: "that makes way more sense for c. confirm c split." On what to do for a population with
no Pf, the owner asked "are there any relevant cases currently? if not, might be able to not decide."; there are,
and section 4 holds the route agreed for them.

**TRPA1, ruled.** The session asked whether TRPA1, best known in sensory ganglia, sits on a central neuron under
section 1's part (iii). A Fable pass of 16 November 2026 found functional TRPA1 on central neurons in rodents, from
three independent laboratories (layer 5 pyramidal neurons of somatosensory cortex, Kheradpezhouh et al. 2017, with a
knockout control; layer II/III of anterior cingulate cortex, Kawabata et al. 2023, pharmacology only; urocortin
neurons of the Edinger-Westphal nucleus, Al-Omari et al. 2023), and in humans mRNA only (Kormos et al. 2022); the
hippocampal signal on disk is likely astrocytic (Shigetomi et al. 2013). The owner, 16 November 2026: "keep TRPA1 with
the stated rodent-only plus human mRNA note". TRPA1 stays, recorded as resting on rodent functional evidence and
human mRNA.

## 6. Design question 3: a class sitting on several reactions (D)

- **D, ruled.** Proposal: one weight per pore population, with a curated, sourced table of which reactions are the
  same pore. The owner: "D. yes".
- **D1, ruled.** Proposal: the three nicotinic reactions as one population sharing one unit, the Ca²⁺-written
  reactions taking the Pf share and the Na⁺-written one the rest. The owner first asked "D1. doesn't leaving the split
  make more sense?", then answered "D1. fine. merge"; asked whether "merge" meant one shared weight with the three
  reactions kept, or one curated reaction replacing them, the owner answered "i meant option 1" (the shared weight).
- **D2, ruled.** Proposal: the same-pore rule reaches the single-ion pores too, each same-pore row sourced, since
  overlapping catalysts are not proof of one pore. The owner: "D2. yes".

## 7. The brain-expression filter, a decision of its own

The 13 November screen found genes that GTEx v10's brain tissues place below 1 TPM while HPA's regional bulk and the
Siletti nuclei do not, among them the serotonin and noradrenaline transporters (SLC6A4, SLC6A2) and TPH2, whose mRNA
sits in small brainstem nuclei that GTEx does not sample. The owner: "i think region-restricted genes is better fix,
no?" The session proposed counting a gene as brain-expressed when it reaches the threshold in any brain region of
GTEx or of HPA's regional bulk; the owner: "that's fine but it needs to make sure to create those new cell types so
their relative gene expression levels can be unique." On v5, matched by symbol, the rule turns 1,420 genes
brain-expressed, 15 of them drug targets of 88 of the 260 drugs. The cell classes of decision 9.76 hold no
serotonergic neuron class. A Fable pass of 13 and 14 November 2026 proposed classes from single clusters of the
Siletti et al. 2023 atlas, ranked by the study's drug targets each carries at three times every current class. The
owner, 14 November 2026: "Yes to purkinje even with one source because it's important for some movement disorders,
habenula, histaminergic", and, asked whether the serotonergic class was approved too, "Yes". So four classes are
ruled: serotonergic (cluster 397), Purkinje (314, on one source), medial habenula (334) and histaminergic (432). The
owner then asked whether the search for a second source for the forebrain cholinergic class (cluster 400) had been
exhaustive; it had not, and a second search was started. On orexin, the owner asked "Orexin shouldn't be zero
targets. What about Suvorexant?"; the session answered that suvorexant, lemborexant and daridorexant target the
orexin receptors HCRTR1 and HCRTR2, which sit on the neurons orexin projects to (HCRTR1's top class is the
noradrenergic one; HCRTR2, brain-expressed under the region rule, peaks in cluster 397), not on the orexin neurons,
and that the orexin neurons cannot be a class of their own at cluster resolution, being about 9 per cent of cluster
410 beside the vasopressin and oxytocin neurons.

## 8. Carriers among the pore catalysts

- **SLC26A8, ruled.** The owner first wrote "exclude SLC26A8 but because it's for the testes."; the session reported
  that it is also brain-expressed (GTEx, HPA and the Siletti nuclei) and proposed the reason TCDB and UniProt give, that
  it is an exchanger. The owner: "if it's a brain-expressed carrier, then it should be included as a carrier, right?"
  The session proposed: "SLC26A8 is a brain-expressed carrier. It is kept as a carrier and excluded from the pore test,
  because TCDB and UniProt describe it as an exchanger. MAR06534 is split into a pore node and a carrier node under
  part (ii)." The owner: "SLC26A8 accepted."
- **The screen of the other reactions,** asked for by the owner ("start the other reactions screen."), found
  `MAR06534` the only reaction mixing a channel and a carrier when read by the functional description, with a second
  carrier, SLC26A2, on it. Three proposals are open: (a) classify by the functional description (TCDB's entry text
  and UniProt) rather than by TCDB's class number, which files ClC-2 among carriers and the K_ATP sulfonylurea
  receptors among primary transporters; (b) remove the scramblase anoctamins (ANO7 and six others) from the
  catalysts of `RCT_2684901`; (c) fix the build so that gene nodes added after the expression annotation (182 of them
  on v5, KCNK1 at 146 TPM among them) receive their GTEx values, built together with section 7's rule. **(a) ruled** (the owner, 16 November
  2026: "use functional  description"): a pore catalyst is classed by what TCDB's entry text and UniProt say it does,
  not by its TC class number, each disagreement between the two recorded beside its gene. **(b) ruled** (the
  owner, 16 November 2026: "yes"). The session found that the screen's "none brain-expressed" for ANO3, ANO4, ANO5,
  ANO8 and ANO10 is the annotation fault of (c): their expression is unknown in v5, and once (c) and section 7's rule
  apply they are brain-expressed (ANO3 at 140 TPM in HPA's basal ganglia). Ruled: ANO1, ANO2 and ANO6 stay as the
  catalysts of `RCT_2684901` (ANO6 on the reading that it is a channel that also scrambles); ANO3, ANO4, ANO5, ANO7,
  ANO8, ANO9 and ANO10 leave them, the genes staying in the graph. ANO7's non-channel status has two sources; for
  the other six only UniProt was read, so a Fable check of their TCDB entry text comes before the removal is built.
  That check (a Fable pass of 16 November 2026) changed the grounds for three of them, and the owner ruled the
  corrected version ("use corrected 8b"): ANO3, ANO8 and ANO10 leave as not chloride channels, by TCDB and UniProt;
  ANO4 leaves because TCDB calls it a cation channel as well as a scramblase, so it does not carry the chloride this
  reaction moves; ANO5 leaves because TCDB calls it an "intracellular calcium-activated chloride channel", not this
  plasma-membrane pore, its disagreement with UniProt recorded; ANO7 leaves as a scramblase, by both; and ANO9 leaves
  because neither source supports a function and it is below the expression threshold. The sentence the 13 November
  screen attributed to UniProt's ANO9 entry is not in the saved row, an error of that screen.
  **(c) ruled** (the owner, 16 November 2026: "yes"). In v5, 357 gene nodes have brain expression unknown: 183 are
  in the GTEx file by symbol, 182 of them gene nodes a later build stage adds after `annotate_brain_expression` has
  run, and 174 are in no GTEx row. Every step that gates on `brain_expressed` reads unknown as not expressed. Ruled:
  the expression values are attached after the last stage that adds gene nodes, a correction of the code and not a
  change of what brain-expressed means; built together with section 7's rule in one rebuild; the before-and-after
  counts (genes whose flag changes, pores and catalysts, drug targets moving from a plasma to a brain site) shown to
  the owner once the rebuild has run, the code being committable before them (the owner, 20 November 2026, told that
  the counts come only from a build: "oh. then i don't need the counts before it's committed for 8c"); and a test that fails while a gene node whose symbol is in the expression
  table carries no value.

## 9. Saturation inside the fixed point (decision 9.81, open)

Raised while sizing the conductance edges. The owner: "that's the other thing that's really been bothering me is the
forced contraction into a fixed point that doesn't necessarily represent the steady state", then "saturation has to
exist within the fixed point to properly represent physiology, right?" The session agreed for this project's large
perturbations (knockouts, high occupancy), noting that the encoder applies its nonlinearities after the fixed point,
and that a saturating operator is the physiological stabiliser the gain clamp stands in for. The owner: "yes but do
the ceilings per node where possible even though it's a very large sourcing job. just use the per-relation-type
version as a learned default fallback ceiling unless there's no ceiling. honestly, i think i'd rather just move
towards the version with the stabilizing nonlinearities inside the fixed point loop and remove the damping."

The session pointed out that the damping sets the transient only (the encoder's docstring: "damping sets the
transient only"), so removing it changes no steady state; the owner: "the .9 gain clamp is what i meant by removing
the damping". On the row normalisation: "keep forward cone norm". The session described a root-finder in place of the
damped iteration (Anderson acceleration forward, the implicit function theorem backward; Bai, Kolter and Koltun 2019
and Walker and Ni 2011, from the session's own knowledge and to be checked by a Fable pass before they are cited).
Asked "what about when multiple steps have saturation?", the session proposed soft saturation (Michaelis-Menten or
Hill), so that a chain of saturated steps keeps a nonzero gradient; a floor at -1 for every node, since activity
cannot fall below zero; and a sourced upward headroom per node, (maximum - rest) / rest. The owner: "yes to all three,
root-finder and learned fallback".

So the direction, not yet built and not yet registered: (1) saturation inside the fixed-point loop, soft
(Michaelis-Menten or Hill); (2) a floor at -1 for every node; (3) a sourced upward headroom per node wherever one can
be sourced; (4) a learned headroom per relation type as the fallback, and none where no ceiling exists; (5) the 0.9
gain clamp removed; (6) the `forward_cone` normalisation kept; (7) the damped iteration replaced by a root-finder with
implicit differentiation, starting from rest, with perturbations at a bifurcation detected and flagged. Changing the
tested model goes through an amendment, as 9.81 already records ("it's fine as an amendment"). Before it is built:
9.81's four counts and a count of positive-feedback cycles on v5, and a Fable pass scoping which node kinds can be
given a sourced headroom.

**Added 17 November 2026: two readouts, and several steady states.** The session pointed out that a root-finder
leaves no propagation rounds, while item 11 of `docs/exploration_queue.md` holds the owner's proposal of "readings at
each propagation round that the perturbation reaches back to a previously visited node". The owner, on the mass-balance
rule the session had proposed for the pumps: "part of the purpose of moving away from the single fixed point with
forced damping (via gain clamp) is to allow modeling of non-steady-state dynamics". Offered (a) both readouts, (b) the
iteration only, (c) the root-finder only, the owner answered: "i was thinking option a except that: instead of clamped
gains for the root-finder, it will still allow unclamped gains and finding of multiple steady states". So item (7)
reads: a root-finder for the steady states and an unclamped iteration with saturation inside for per-round readings,
both without the gain clamp; the root-finder searches for several steady states rather than only the one reached from
rest. Open with it: the search method (multistart, or deflation, Farrell, Birkisson and Funke 2015, from the session's
own knowledge and to be checked by a Fable pass), which no method makes complete; keeping only stable roots; and that
a round is not physical time while the relations carry no timescale.

**How several steady states enter a prediction.** The owner: "i'm wary to force a single steady state to be the
predictor because it could be the case that the symptoms show up for both steady states in the bistable switch". The
session offered (a) a noisy-OR across every stable steady state, the head's own combination rule, a symptom predicted
if any stable state produces it, which suits labels that say whether a drug causes a symptom in some patients; and (b)
a mixture weighted by the fraction of multistart runs reaching each state, which suits frequency labels but rests on
an arbitrary spread of starting states. Neither adds a learned parameter. The owner, 17 November 2026: "definitely
option a". Recorded with it: a steady state the search misses takes its symptoms with it, so the search's
incompleteness bears on the prediction and is to be stated, and the search is to be generous with starting points.
The owner, the same day: "keep only stable roots. i lean towards deflation. please start the fable check for the
deflation vs multistart". So only roots that the stability check finds stable enter a prediction, and the search
method waits on that Fable check.

## 10. Conductance units, permeabilities and the carrier test's second source (17 November 2026)

- **Counted units kept.** A Fable pass of 16 November 2026 (on the owner's condition, "i guess it depends on
  whether the proportions can be well sourced") found a resting conductance in central neurons well sourced for 2 to
  4 of 47 pore populations (5.9 per cent of the present weight), 14 thin and 29 not sourced, measured values ranging
  over orders of magnitude between neuron types, and no conductance for either TRPC1 heteromer; a scheme mixing sized
  and counted populations is not coherent at `VM_c`. The owner: "keep 1/4 and 1/5 as nodes since the proportions for
  splitting can't be sourced". So ruling D's one unit per population stands as a stated interim, with TRPC1/4 and
  TRPC1/5 one unit each, the coverage recorded as the reason.
- **Neuronal nicotinic P_K/P_Na.** The registered 1.2 rests on Xenopus oocytes under two-electrode clamp (the same
  ground on which the owner dropped calibration rows) and on unpublished observations; the repository's record holds a
  native-neuron value of 1.23. The owner: "yes. native 1.23 instead of oocytes".
- **NALCN P_K/P_Na.** The registered 1.0 cites Ren 2011's "equally permeable", a review from the laboratory of Lu et
  al. 2007, which measured P_Na 1.3 and P_K 1.2 (0.92) on NALCN alone in HEK cells. The session first proposed keeping
  1.0 because Chua et al. 2020 find NALCN alone non-functional, then withdrew that, since the caveat applies to the
  rounding as much as to the measurement it rounds; the owner supplied the publisher's copy of Lu 2007 and asked
  "attached paper suggests ratio of about .92 ... thoughts?", then ruled "yes to 0.92". The effect on the weight is
  under 2 per cent.
- **The carrier test's second source.** The screen of 13 November 2026 read TCDB and UniProt for the 267 catalyst
  genes of the 56 pore reactions; by the functional description the owner ruled in section 8 (a), one reaction mixes a
  channel and a carrier (`MAR06534`), handled by section 8's split. This answers 9.129 (2)'s open second source. The
  owner: "continue".

## 11. The same-pore table (17 November 2026)

A Fable pass of 17 November 2026 built the curated table ruling D asks for: 52 populations over the 56 pore reactions
(65 pore nodes after the ruled splits), 11 of them holding more than one reaction, every row quoted and checked. It
raised six questions; the owner accepted the session's recommendations for the first five ("accepted suggestions for
1-5 from the same-pore table run questions"):
1. K_ATP's three reactions are two populations, Kir6.1 (KCNJ8) and Kir6.2 (KCNJ11), by the co-assembly rule of section
   5, unless sources show the two co-assemble in neurons (a Fable check).
2. RCT_2684901's three remaining channels, ANO1, ANO2 and ANO6, are three populations by the same rule.
3. SCN7A (Nax) is split out of MAR_SODIUM_LEAK, a different pore from NALCN, and excluded under section 1's part (iii)
   if a second source confirms its glial location (a Fable check; one source so far).
4. The six Kir2, Kir4 and Kir5 genes that Reactome's GIRK complex holds, and that neither UniProt nor the Concise Guide
   supports as GIRK subunits, are removed from that entity, as TRPC4AP was from the TRP set.
5. MAR06534, written by Human-GEM as a 1 Cl⁻ : 2 HCO₃⁻ exchange, gives its pore node chloride alone; the exchange
   stoichiometry stays with the carrier node of section 8.
The sixth, which kainate reaction is the calcium-permeable one (Reactome and the Concise Guide against UniProt and
Köhler et al. 1993), waits on a Fable reading of Köhler et al. 1993, which the owner supplied.

## 12. Further rulings of 17 November 2026

- **5-HT3A Pf: 3.2 per cent.** A Fable pass read Noam, Wadman and van Hooft 2008 (J Physiol 586:3629) in full: its
  4.1 per cent without and 3.2 per cent with 5 mM ATP in the pipette differ by a receptor effect the authors attribute
  to intracellular ATP acting at the RRR residues ("excluding a phosphorylation-mediated mechanism"), a mutant lacking
  them showing no fall, so not by calcium buffering; a cytosol holds millimolar ATP. Unreplicated. The owner: "3.2%
  accepted".
- **Three forebrain cholinergic classes.** The two-class split of section 7 was computed from the Siletti subclusters:
  NGFR and MEPE mark only subclusters 1641 and 1642, not 1637 and 1638, though those come mostly from the substantia
  innominata. A Fable pass found NGFR-negative cholinergic neurons a known basal-forebrain population (ventral
  pallidum and sublenticular substantia innominata; Heckers 1994, Hecker and Mesulam 1994, Poulin 2006). Proposed: three
  classes, striatal (1634-1636), NGFR-negative basal forebrain (1637, 1638) and NGFR-positive basal forebrain (1641,
  1642, and 1640, which shares their OPRM1 and CD36). The owner: "accepted".
- **The carrier clause's wording.** The drafted "+7.0 ... +10.7 ... +5.4" mV per µA/cm² are the model's whole
  steady-state response to a carrier's current (`experiments/derive_pump_leak_pool_sensitivity.py`'s `dV_ss`), what a
  carrier is denied; the pool route itself is -0.48, -0.06 and -4.05 mV, 5.3, 0.65 and 44.5 per cent of a conductance
  edge (1/g_total = 9.09 mV). The corrected wording a Fable pass drafted (`item37_values_2026-11-17.md`, section 3, in
  that session's scratchpad) gives both sets and limits "near zero" to sodium and potassium. The owner: "yes".
- **TRPC3/6 and TRPM6/7.** Their sodium-present reversal potentials (Estacion et al. 2006, -7 mV; Monteilh-Zoller et
  al. 2003, -7.2 mV) lie below the zero-calcium reversal the form gives (+8.8 and -0.9 mV), so the form has no
  solution for them, which the session read as a sign of calcium block or of wrong monovalent assumptions. By the
  ranking's first criterion they fall through to their sodium-free measurements, flagged. The owner: "yes, with stated
  fallback".
- **The pumps and exchangers of the Ca²⁺ pool.** Offered a stated limitation until population sizes exist, the owner
  answered "go straight to the population sizes please": a Fable pass sources them. The pass (17 November 2026,
  `ca_pool_fluxes_2026-11-17.md` in that session's scratchpad, all claude-fable-5-2) found no resting flux through
  any route measured in a central neuron, no measured pump or exchanger density (Bartol et al. 2015: "There have been
  no direct experimental estimates of the density of PMCA's on spine or dendritic membranes"), and clearance shares
  that differ by cell type more than one reference set could carry. The owner: "sounds like there's no way around the
  per-open-channel version". So the pool keeps the per-open-channel basis, and the population basis is recorded as
  not sourceable on 17 November 2026, a limitation and not a numerical choice.
- **HCN headroom: the distal dendrite.** A Fable pass read Magee 1998 (J Neurosci 18:7613, owner's copy) in full
  (`headroom_supplied_papers_2026-11-17.md` in that session's scratchpad): rat CA1, cell-attached, distal dendrite with
  Na+ in the pipette, V1/2 -80.5 ± 1.3 mV, k 6.7 ± 0.7, open fraction 0.235 and headroom 3.3 at -72.6 mV, the measured
  condition nearest to physiology; one laboratory for the slope, so the row stays thin. The owner: "distal dendrite
  headroom for HCN accepted".
- **The NMDA receptor's Mg2+ block is modelled in full.** On the item-37 dry-run graph (`graph_9129`, 12 November
  2026) the block is only the sign of the `voltage_gates` edge from `VM_c` to `RCT_432164` (+1, weight 1, as every
  such edge); `MAM02482e` has no edge to the receptor and no [Mg2+]e is registered. Jahr and Stevens 1990 (J Neurosci
  10:3178, owner's copy, Eq. 5, read by a Fable pass) give g(V) = 1/[1 + exp(-0.062V)([Mg2+]/3.57)], 0.038 unblocked
  at -72.6 mV and 1 mM. The owner, told nothing in the set perturbs Mg2+: "it's worth it regardless of whether
  something perturbs Mg because it sets the base fraction blocked for NMDA". So: [Mg2+]e is registered from two
  sources; the block's constants take a second source; an `inhibits` edge runs from `MAM02482e` to the receptor; the
  voltage edge carries the slope of Eq. 5 at rest; and the resting unblocked fraction enters NMDA's headroom and,
  once counted units give way to conductances (ruling D's interim), its resting conductance.
- **One resting potential for every headroom.** Each source's gating curve is evaluated at the registered -72.6 mV,
  not at the source's own resting potential, which is recorded beside the row; whether each source's midpoint is
  corrected for the liquid-junction potential is checked by a Fable pass and recorded with it. The owner: "i accept the
  single registered -72.6mV. run the resting potentials fable pass to get the new column values please".
- **Conditional reversal of exchangers, gated by the driving force.** Proposed by the session: each exchanger keeps
  its forward route and gains a reverse route, each gated by a smooth function of the sign of its own driving force
  computed from the current state (`VM_c` and the ion pools; for NCX 3 E_Na - 2 E_Ca - V), with no learned
  parameters; computable now for NCX, NCKX with K+, NKCC1 and KCC2, and not for transporters coupled to H+, NH4+ or an
  organic substrate until their concentrations are registered; a reversible Human-GEM reaction is written in its
  resting direction and the gate carries reversal; amphetamine's reverse route stays gated on the drug, as built. It
  replaces, for these exchangers, a direction fixed at build time (decision 9.112) and an always-available reverse
  route (decision 9.127's concern; for VMAT2 the session proposed on 9 November 2026 a reaction "gated on
  amphetamine", after the owner asked "What about reversal of VMAT2?"). The owner had meant a conditional
  route from the start ("i wasn't suggesting an ALWAYS reversible route ... only a conditionally reversible one"),
  and on the proposal: "yes. that reversal route implementation is acceptable". Each exchanger's case (NCX under
  9.127, NCKX's MAR01529 and MAR07632) is still settled on its own physiology.
- **NCKX keeps only its K+ form.** `MAR01529` (Recon3D, reversible, written as Ca2+ entry with NH4+) and `MAR07632`
  (HMR, forward only, with neutral NH3) are one reaction imported twice (BiGG NCNt, one MetaNetX id). A Fable pass
  (`nckx_nh4_2026-11-17.md` in that session's scratchpad) found NCKX does accept NH4+ at the K+ site (Schnetkamp and
  Szerencsei 1991; Lee, Ho and Lee 2007; Boyer et al. 1999) but no central-neuron measurement, no physiological role
  in any source, and NH4+ in at most about 0.15 per cent of forward cycles at brain concentrations. The owner: "leave
  out the NH4 and keep only the K+ version". So both NH4+/NH3 reactions leave the graph and `MAR07631` stays; the
  justification for leaving out a supported mechanism is its negligible share of the flux, not a numerical reason.
- **Ambient glutamate is the receptor-sensed nanomolar value.** The owner, on the 120-fold dispute: "b. use the
  25 nM". Chiu and Jahr 2017 (owner's copy) measure 25.6 ± 3.2 nM in rat accumbens core slices at 32 °C with NMDA
  receptors as the sensor, test a micromolar non-synaptic compartment and reject it, and attribute the microdialysis
  values (0.2 to 35 µM) to impaired uptake around the probe. It is not independent of Herman and Jahr 2007 (same
  senior author and method), and both are slices; Cavelier and Attwell 2005 is the independent check still wanted.
  So the receptors report's sentence that "microdialysis may sample a compartment the receptors do not see" is
  **withdrawn** on 17 November 2026: the paper rejects that reading.
- **Hill coefficients are sourced, not assumed.** The owner: "c. source them". Every ligand-gated population's
  headroom used n = 1 while most have two or more agonist sites, which understates the headroom by (K/C)^(n-1) at
  C below K; a Fable pass sources n per population, and a population whose n cannot be sourced keeps n = 1 with that
  stated in its row.
- **A ceiling is multiplied by the share of the population that can reach it.** At -72.6 mV part of each
  voltage-gated population is inactivated and cannot open without first hyperpolarising: 11 to 29 per cent of Nav,
  72 per cent of Cav3, 49 to 79 per cent of A-type Kv (`headroom_channels_pools_2026-11-17.md`). The owner: "g.
  multiply by the share of the population that cannot open without first hyperpolarizing" - so the ceiling is the
  non-inactivated share and not "all channels open", which is the physiological version; a population whose
  inactivated share is not sourced keeps the full ceiling with that stated in its row.
- **The redox pools are sourced in neurons or not used.** The glutathione (c, m, r, x) and NADPH (c, m, r, n, x)
  nodes came out nearly rigid (headrooms 0.0006 to 0.07, except ER glutathione 0.3 to 2) on sources of which none is
  a neuron or brain tissue. Offered those values, the learned fallback, or a sourcing pass, the owner: "h. try to
  source them properly in a fable pass please".
- **Resting activity includes agonist-independent openings, so the headroom's denominator is both terms.** A
  headroom is (max - rest)/rest, and the receptor pass computed `rest` from agonist occupancy alone. Wlodarczyk et al.
  2013 report the tonic current of dentate granule cells "predominantly generated by GABA-independent" openings, so
  that denominator is too small and the headroom too large. Offered the learned fallback or the occupancy value for
  extrasynaptic GABA-A, the session proposed instead that the formula is what is wrong: rest = spontaneous +
  agonist-driven, for every population with measurable spontaneous openings, not GABA-A alone, spontaneous P_open
  being a measurable quantity. The owner: "yes to both d and l". So a Fable pass sources the agonist-independent
  share per assembly beside the Hill coefficients of the ruling above; a population whose spontaneous share cannot be
  sourced keeps agonist-only rest with that stated in its row.
- **One method per quantity across the populations it is compared over (the uniform-method rule).** Under
  forward_cone row normalisation only the ratios at a node matter, so nearly every sourced number enters a comparison
  between populations, and a quantity sourced by different methods turns a method difference into an apparent
  physiological one. Measured spreads: temperature (gating shifts, large for TREK/TRAAK), the liquid-junction
  potential (5 to 11 mV, as large as real differences between pores: `resting_potential_columns_2026-11-17.md`),
  native against heterologous expression (the HCN midpoint differs by tens of millivolts), the resting potential
  (2.0 to 2.7-fold on the rows affected, already ruled to the single registered -72.6 mV). **The rule**: where a
  quantity enters a comparison between populations, the method is uniform across them, or the difference is recorded
  as method-dependent and not read as physiology; where a better-sourced value exists for only a few populations,
  both are recorded and the uniform one is used. **Its cost, stated because the physiological version is otherwise
  the default**: the uniform choice is sometimes the less physiological one, as in keeping Jahr and Stevens 1990 at
  room temperature over Chiu and Carter 2022 at 34.7 °C for the Mg2+ block. The justification is that mixed methods
  put a false difference between two nodes, which is itself a physiological error and not a numerical convenience.
  The owner, asked whether the consistency reasoning of the Mg2+ constants should extend further ("shouldn't this
  extend to other things as well though?") and shown the rule: "yes to both d and l". This settles ruling (l), the
  temperature policy and the junction-potential question together. It is general rather than particular to item 37,
  so it may warrant its own decision row or a CLAUDE.md line; that is not assumed here.
- **Extracellular magnesium: ionised 0.8 mM, range 0.66 to 1.15 mM, the ionised share recorded as open.** Needed by
  the Mg2+-block ruling above; neither registered constants source states a magnesium concentration (Düsterwald et
  al. 2018 gives a bath recipe only, and set B, Raimondo, Burman, Katz and Akerman 2015, has no magnesium row).
  **Sources, both read first-hand by Fable passes of 17 November 2026** (`mg_block_2026-11-17.md`,
  `mg_sources_check_2026-11-17.md`, `mercieri2012_csf_mg_2026-11-17.md`, `mg_ionised_share_2026-11-17.md`):
  Mercieri et al. 2012 (Br J Anaesth 109:208, owner's copy) measure 0.83 mmol/l ionised and 1.19 mmol/l total in the
  same lumbar CSF of 16 adults, awake, before any intervention; Ding et al. 2016 (Science 352:550, owner's copy with
  its supplement) measure free interstitial magnesium in mouse somatosensory cortex by Mg2+-selective microelectrode,
  the one method independent of the analyser electrodes every human value rests on, at 0.69 to 0.70 mM awake and 0.80
  to 0.83 mM asleep. Total CSF magnesium of 1.13 to 1.19 mmol/l is recorded beside the row as a separate quantity,
  and the sleep-wake swing of 0.11 to 0.13 mM with it. **The ionised share of total is open, not 69 to 70 per cent**:
  Apostol et al. 2010 prints 95.5 per cent for 10 non-pregnant women and 59.7 to 63.3 per cent for two pregnant
  groups on the same instrument model, attributing the difference to pregnancy, which Mercieri's non-pregnant 69 to
  70 per cent contradicts; no source validates the electrode in cerebrospinal fluid, and the Mercieri pass found the
  same instrument reporting ionised calcium at 50 per cent of total in both CSF and serum although CSF protein is
  about a thousandth of serum protein. **Why the human value and not Ding's awake 0.70**: 0.70 mM is mouse cortical
  interstitium, not a human value, so the choice is of species and compartment and not of behavioural state (that 0.8
  also matches Ding's sleeping cortex is a coincidence across two species and two compartments); Ding's absolute
  level is pulled toward the 1.0 mM magnesium of the cranial-window bath, which the paper shows reaches the recording
  depth, and its electrode is poorly selective against calcium. The owner, told that 0.7 is mouse: "k accepted".
  At 0.8 mM the NMDA receptor is 4.7 per cent unblocked at -72.6 mV by Jahr and Stevens' Eq. 5 (5.7 per cent at 0.66,
  3.3 per cent at 1.15). **Not registered, and nothing in the model uses them yet**: free mitochondrial magnesium
  (0.8 mM, range 0.5 to 1.5, Rutter et al. 1990 and Jung et al. 1990, both isolated heart mitochondria, neither
  neuronal) and free neuronal cytosolic magnesium (0.5 mM, range about 0.15 to 1.0, Brocard et al. 1993 and Kato et
  al. 1998, abstracts only).
- **The Mg2+ block is carried per GluN2 class.** Kuner and Schoepfer 1996 give the voltage dependence delta as about
  1.05 for NR2A and NR2B against 0.73 to 0.75 for NR2C and NR2D at similar K0, and Yi et al. 2019 give 4.5 mM/1.08
  (2B), 6.6/0.95 (2B-2D) and 11/0.82 (2D), so at -72.6 mV and 0.8 mM the unblocked fraction is 1.0 to 1.5 per cent
  for GluN2A and GluN2B against 4 to 11 per cent for GluN2C and GluN2D, a difference of about tenfold. The owner:
  "m. one per GluN2 class unless you disagree"; the session agrees, with two costs recorded. **First**, `RCT_432164`
  carries GRIN1 and GRIN2A-D together, so it is split, by the mechanism section 1 already rules for a reaction whose
  catalysts span two classes (the classes a reaction can contain are those whose defining subunits assemble from its
  catalysts, and it is split into one node per class), which is why this needs no new mechanism. **Second**, a split
  that carried only the block would be inconsistent: the agonist EC50 also differs by GluN2 subunit (Erreger et al.
  2007), so each class node carries its own agonist affinity as well as its own block, and the Pf and P_Ca/P_Na of
  each are stated per class or stated as shared. **A simplification to record**: triheteromers are intermediate
  (Yi's 2B-2D row), so a two-class split puts them in one class or the other; three classes would follow the sources
  more closely and are not proposed here.
- **A busy or unavailable service is not a refusal.** `experiments/read_public_page.py` counted 429 (too many
  requests) and 503 (service unavailable) among the statuses that mean the site refused the reader, beside 401, 403
  and 407. Three Fable passes of 17 November 2026 met them from Europe PMC while sending several requests at once,
  and the same addresses on the same host answered 200 a few minutes later, one at a time. The owner: "429 and 503
  status codes should not count as refusals". So the script now reports them as transient, with the instruction to
  wait and request the same address on the same host again rather than a cache, a mirror or another host; a challenge
  marker in the body is still a refusal whatever the status, and the rest of the reader's limits are unchanged. The
  change is in the script, its docstring and
  `tests/test_read_public_page.py::test_a_busy_or_unavailable_service_is_not_a_refusal`. It is a reading rule rather
  than part of item 37, so it needs its own decision row and a CLAUDE.md line; that is not assumed here. **Records to
  correct when it lands**: the passes of 17 November 2026 that wrote Europe PMC 503s down as refusals
  (`redox_pools_neuronal_2026-11-17.md`, `affinity_end_2026-11-17.md`, `ambient_transmitters_2026-11-17.md`), and the
  Mg2+ source check's PubMed 429.
- **Derived Pf uses the raw GHK solution, with no calibration factor.** The 9 clean calibration rows plus Samways and
  Egan 2011's TRPV1 row give a factor of 1.27, spread ×/÷2.34, whose leave-one-out error (0.378 leaving a channel out,
  0.387 leaving a family out) barely beats the raw form's 0.413, which a 2 mV error in one reversal potential erases;
  the one TRP row points the other way (×0.56). The owner: "1. raw GHK per previous decision that the model-based
  needed to beat it" — the earlier ruling being that a model-based correction is used only if it beats the raw form,
  which it does not. So the factor is dropped and the gap is recorded rather than fitted.
- **Hill coefficients and EC50s come from HEK cells where the preparations differ.** The owner: "6. use HEK over
  oocytes", which settles α4β2δ at 27.5 (HEK, Sexton et al. 2021) over 0.16 (oocytes, Pierce et al. 2019) and matches
  the EC50 set the GABA-A rows already use (Mortensen et al. 2012, HEK). It is an application of the uniform-method
  rule to the preparation, not a judgement that oocyte recordings are wrong; the oocyte values stay recorded beside
  the rows.
- **Phosphorylation stays in the exploration queue, and is done before the qualifying exam.** The owner: "12. leave in
  exploration queue for now but it needs done before the qual exam". This is item 4 of `docs/exploration_queue.md`
  (dropping the phosphorylation-site nodes and fixing the 16 signs one by one). It is not a gate on item 37, and under
  the project's own rule that the project IS the qualifying exam it is not deferred past it either.
- **VM_c's two-sided bound is set once item 37 is built.** The reversal potentials are solid (E_K -95.11 mV and E_Na
  +62.48 mV, i.e. -22.51 and +135.08 mV from rest; E_Ca +137.11 if calcium's conductance term is counted), but one
  state unit at `VM_c` depends on how the item-37 conductance weights combine with forward_cone's row normalisation
  in the built graph, so the bound in state units is computed from the built edges and not from either reading a pass
  could take from the module alone. The owner: "13. sure. once item 37 is done being built". The generic floor at -1
  does not bind on any reading, lying below E_K.
- **BRENDA's full kinetics are fetched.** The owner: "16. fetch", so the enzyme rows are not left on the fallback.
- **The bottleneck and pH ceiling stay inside the loop.** The owner: "17. inside".
- **The uniform-method rule is amended for a bias that is not a common monotone transform.** The owner raised it: "i
  was worried about nonlinearity for the uniform method rule". The rule preserves the ratios a node's row
  normalisation depends on only if the method's bias acts the same way on every population compared - which holds for
  temperature (a Q10 is multiplicative and same-signed across channels) and for the liquid-junction potential (a
  common offset in millivolts), and fails for quantitative microdialysis across transmitters, which reads about
  120-fold high for glutamate (Chiu and Jahr 2017) and several-fold low for dopamine (Chen 2005, Bungay 2003), the
  bias depending on each transmitter's uptake kinetics beside the probe. **The amendment**: the uniform-method rule
  applies where the method's bias is plausibly a common monotone transform across the populations compared; where it
  is not, each population takes its best evidence and the method is recorded on its row, with cross-method
  comparisons marked method-dependent and not read as physiology. The owner: "accepted uniformity amendment". This is
  what the glutamate ruling above already did, and it is why ambient concentrations are treated per ligand while
  gating curves are not.
- **Criterion 3 keeps the wording ruled on 16 November 2026.** Its TRPV1 rationale is **withdrawn**: Samways and Egan
  2011 (owner's copy) show TRPV1's sodium-present and sodium-free fractional calcium currents agree, so the 2.4
  against 11.7 contrast of Zeilhofer et al. 1997 and Nagy and Rang 1999 does not support the criterion. The TRPC6
  evidence stands (Estacion et al. 2006: the same channel reverses at -58 mV sodium-free against -7 mV with sodium
  present), so the criterion rests on one case rather than two. The owner, told this: "for criterion 3: sure, keep it
  as previously ruled on 16 Nov since TRPC6 still shows evidence". No row changes.
- **The affinity end: the depletion nulls where they exist, GtoPdb's high-affinity end only where an occupancy
  measurement backs it, a stated midpoint elsewhere.** A Fable pass of 17 November 2026 (`affinity_end_2026-11-17.md`)
  tested the choice beyond D2: the high-affinity end is backed by a measurement for D2 alone and **contradicted** for
  5-HT1A (every point of GtoPdb's range predicts a 2.8- to 8-fold rise in tracer binding on serotonin depletion,
  against none observed after a raphe lesion, reserpine or pCPA) and for 5-HT2A; for D1 and the muscarinic receptors
  every end predicts an undetectable occupancy, so no end is separated. The session's reading, accepted by the owner
  ("for the contradiction, you suggestion is accepted"): **(iv)** where a depletion null exists, the bound it implies
  on K is used (HTR1A: K at or above about 9 nM at 1.4 nM ambient, so headroom at or above 6.4), because a lower
  bound on K is a lower bound on headroom and that is the conservative input to a soft ceiling, and the nulls are in
  vivo while GtoPdb's range is an in vitro binding-state artefact; **(iii)** elsewhere, the high-affinity end only
  where an occupancy measurement backs it and a midpoint, stated as a construction, where none does. **GtoPdb gives
  no median for the receptors that matter** (D1-D5, 5-HT1A, 5-HT1B, 5-HT2A, M1-M4 carry ranges only), so a midpoint
  there is the session's construction and is recorded as such under the modelling rule. **(iii) may have no members**:
  its only one was D2, whose fit uses 5 nM dopamine, which the voltammetry pass of the same day puts nearer 20 nM
  (at which the high end gives occupancy 0.24 against 0.11 measured).
- **Revised the same day: the unsettled affinity end becomes a learned parameter that starts at the midpoint.** The
  owner, 17 November 2026 at 20:38 UTC, after the ruling above: "I think it's probably better design to start a learned
  param at the midpoint for the affinity end even though it could cost params in an already overburdened dataset",
  adding that the module supports are being reduced separately. So where GtoPdb gives a range and no occupancy
  measurement settles which end holds, the affinity is not fixed at a constructed midpoint but learned, initialised
  there, which removes the need to justify the construction as a fixed value: the midpoint becomes a starting point and
  not a claim. **The cost, counted on the receptor pass's table**: of the 431 receptor proteins in v5, 83 have a sourced
  or thin affinity and **45 of those carry a GtoPdb range** (35 class A and 9 class C GPCRs and one Cys-loop receptor;
  32 are drug targets), so a learned affinity per receptor adds 45 parameters, against at most 22 for the whole
  per-relation-type fallback. **Open, for the owner** (the session's reading of how the revision meets the earlier
  ruling, not assumed): whether a depletion-null bound (HTR1A: K at or above about 9 nM) becomes a constraint the
  learned value may not cross, which keeps the in vivo evidence the earlier ruling rested on; whether D2 keeps its
  measured occupancy fixed or also learns from it; and whether one learned shift in log K per receptor family (two or
  three parameters, the high- against low-affinity balance being set by G-protein coupling, which is plausibly a family
  property) would serve instead of 45, which matters while the parameter count is being reduced.
- **A depletion-null bound is a hard constraint on the learned affinity.** The owner, on the first of the questions
  above: "Yes to the depletion null bound hard constraint on the learned param". So where a depletion study finds no
  rise in tracer binding, the learned K may not fall below the bound the null implies (HTR1A: K at or above about 9 nM
  at 1.4 nM ambient serotonin, so headroom at or above 6.4); the fit can move the affinity anywhere the in vivo
  evidence allows and nowhere it forbids.
- **Revised again the same day, and superseded on 18 November 2026: no learned affinity; the midpoint is fixed and a
  two-build screen measures what the ranges are worth.** The owner weighed branching on each range instead of learning
  it and saw the cost: "I'd have to branch at every range with that option, which would quickly explode given the
  multiple loops to get to steady state" - worse than the sign multiverse, since a sign has two states while an affinity
  range is continuous, so branching means a grid over 20 or 45 receptors with a full fixed-point solve at each point,
  and item 1 of `docs/exploration_queue.md` does not help (its rank-one Woodbury updates and series equivalence classes
  are for sign flips). Offered a middle option, the owner, at 23:43 UTC: "I like the middle option for the affinity".
  **So**: every range stays at its midpoint with no learned parameter, and after the item-37 build two runs - every
  range at its high-affinity end, then every range at its low end - measure how far the ranges can move predictions. Two
  runs rather than a grid. **Its limit, recorded**: because headroom K/C is monotone in K, the two runs bracket each
  node's headroom, but not the predictions, since paths of mixed sign can make an output non-monotone in any one K; it
  is a screen, not a bound. If predictions barely move, the fixed midpoint stands and no parameter is wanted; if they
  move, the learned form returns with its evidence. **This settles the counting questions**: there is no 45 against 20,
  and no separate ruling for the two orexin receptors, every range being treated alike. **The parameter count was never
  the argument**: 20 parameters is 0.005 per cent of the nominal 405,908 and 0.1 per cent of the identifiable bound of
  19,927; the reason to prefer a fixed value is that a free parameter can absorb error from elsewhere in the model and
  hide it, which the bounds limit but do not prevent. **Superseded on 18 November 2026.** The owner, at 17:34 UTC: "i
  thought i ruled against doing the two-build screen version and sticking to learned params inside the soft/hard clamped
  bounds based on evidence prior since the 5-ht1a disbelief comment". So the learned parameter of the two bullets above
  stands, inside the clamped bounds recorded below, and no two-build screen is run.
- **The hard bound needs human in vivo evidence AND complete depletion; otherwise it is soft.** The owner, 18
  November 2026, on whether in vivo evidence should be ranked by species (their first proposal) or by how complete
  the depletion was (the session's): "i guess the nulls should hard bound only for human invivo complete depletion.
  where there are cases that don't have both together, it's a soft bound where the softness of the bound is scaled by
  the reliability of the evidence prior determined by the same method as the rest of the evidence prior reliability
  estimation" - that is, by the method that sets the evidence prior's reliability, which today is decision 9.59's
  calibrated regression (`mechanistic_pathway_learning/evidence/calibrated_reliability.py`; 9.50 retired the
  Dawid-Skene posterior as the strength setter). That regression is fitted on perturbation-symptom pairs against the
  label table, so how it would score a measurement such as a depletion study is open. **Consequence, which
  the owner should see before this is built**: the one receptor the bound bites on, HTR1A, gets a SOFT bound and not
  a hard one, because no study has both legs - the human depletion studies use acute tryptophan depletion, which is
  partial, and the near-complete depletions (raphe lesion, reserpine, pCPA) are rodent. The hard branch may have no
  members at all today. **When the bounds apply at all**: not now. The owner, on the session's reading that a soft
  bound needs something to act on while the affinity is a fixed midpoint: "the soft bound is for the case where i add
  the learned params there if the two extreme bound runs show a difference (even though the monotonicity doesn't
  transfer to the predictions)". **That contingency was lifted on 18 November 2026 and the bounds apply from the
  start**: the owner, correcting this session's record, ruled for learned affinities inside the clamped bounds and
  against the two-build screen as the gate ("i thought i ruled against doing the two-build screen version and
  sticking to learned params inside the soft/hard clamped bounds based on evidence prior since the 5-ht1a disbelief
  comment", with the ambiguity resolved in the next message: "i mean i ruled FOR sticking to learned params"). So the
  learned affinities are in from the first build, each carrying the hard bound where a human in vivo study with
  complete depletion exists and the reliability-scaled soft bound otherwise, and nothing waits on a screen.
- **HTR1A's screen range is widened to span the dispute (18 November 2026).** GtoPdb's range for 5-HT1A (0.2 to
  0.794 nM) lies wholly inside the region the depletion nulls contradict, so both ends of the two-build screen give a
  headroom of about 0.25 to 0.57 against the 6.4 or more the nulls imply, and the screen as specified cannot surface
  the conflict. Offered (a) accept with the contradiction recorded, (b) the fallback for HTR1A now, or (c) widen its
  screen range to 0.2 nM at the low end and the null bound's 9 nM at the high end, the owner: "so widen it". The
  owner's reason for doubting the weaker branch, recorded because it is the ground of the ruling: "i have a hard time
  believing that a 22x change of 5-HT1A will not move predictions". The label exposure measured on v5 the same day
  supports that: HTR1A carries 45 kept drug pairs on the agonist side (aripiprazole, buspirone, vilazodone,
  vortioxetine) and 9 on the antagonist side (amisulpride), and 22 serotonin reuptake blockers with 213 kept pairs
  reach it through the extracellular pool, out of 1,384 kept drug pairs in all. So the screen's two runs use the
  widened interval for HTR1A and each receptor's own published range elsewhere. **Corrected 18 November 2026**: the
  owner ruled against the two-build screen and for learned affinities inside the clamps (see the entry above), so the
  widened interval is not a pair of screen runs but **HTR1A's clamp interval**, 0.2 nM at the low end and the null
  bound's 9 nM at the high end, which the learned affinity may move within; elsewhere a learned affinity is clamped to
  its own published range. The widening still does the work the owner's reason asks of it, since GtoPdb's range alone
  would have confined the learned value to the contradicted region.
- **Clamped learning is the general form, and the clamp is not only a depletion null (18 November 2026).** Put to the
  owner that a depletion-null clamp has at most two members, 5-HT1A and 5-HT2A being the only receptors for which the
  17 November affinity pass found nulls (D2 has a measured occupancy, which is a different instrument), so for the
  other 43 of the 45 receptors carrying a GtoPdb range there is no null to clamp to and a "clamped learned parameter"
  would be a free one. The owner: "1a and 2a being the only depletion nulls for clamping is fine. it should probably
  apply to other param types too though for the clamped learning". So the form generalises: **a learned parameter is
  clamped to whatever bound its own evidence supplies**, which is the published range where only a range exists, a
  depletion null where one exists (hard for human in vivo complete depletion, soft and reliability-scaled otherwise,
  as ruled above), and a measured occupancy where one exists (D2, 3.8 to 11.5). The session reads "other param types"
  as covering the other item-37 learned values and not the affinities alone: the per-relation-type resting-fraction
  fallback, the soft-saturation ceilings and D2's headroom. **Not ruled and left for the owner**: whether a parameter
  with no bound of any kind stays fixed rather than learned, and whether a clamp is enforced by reparametrisation
  (a bounded transform) or by projection after each step, which is an implementation choice to be recorded with the
  build.
  **Both left-open points are now ruled (18 November 2026).** The owner: "i would say a param with no bound should stay
  fixed only because there's no data on its bounds and leaving it unbounded leaves the amount of error it absorbs
  unbounded. i think the bounded transform is better for training dynamics reasons (i.e. vanishing better than dead
  gradients)." So a parameter with no bound of any kind stays fixed, with the owner's reason recorded as the
  justification the modelling rule asks for; and a clamp is enforced by a bounded transform rather than by projection,
  on the ground that a saturating transform gives vanishing gradients at the bound while projection gives dead ones.
- **The region-by-class weights come from the Siletti dissections, not from HPA's 13 regions (18 November 2026).** The
  primate pass found that at the 13 HPA consensus regions the nigrostriatal and mesolimbic dopamine projections
  collapse into one midbrain-to-basal-ganglia edge, because HPA holds a single basal ganglia region, so option C's
  separation of dorsal striatum from ventral striatum and nucleus accumbens cannot be built on that parcellation. The
  owner: "use siletti". So the regions are taken from the atlas's dissections, the route the dopaminergic class
  (cluster 395) already uses.
- **Methamphetamine's transporter signs are inverted, and VMAT2 reversal is added (18 November 2026).** A Fable pass
  of 18 November (`family_target_signs_2026-11-18.md`) found that methamphetamine's only ChEMBL mechanism row is
  against the protein-family target "Monoamine transporter" (CHEMBL2363064) typed INHIBITOR, which v5 spreads as -1
  over SLC6A2, SLC6A3 and SLC6A4, while amphetamine and dextroamphetamine carry single-protein RELEASING AGENT rows
  for the dopamine and noradrenaline transporters. Methamphetamine is a substrate-type releaser (Sulzer 2005; Rothman
  2001), so under the convention of `experiments/audit_physiology.py` it takes +1 at SLC6A3 and SLC6A2 and a weak +1
  at SLC6A4, with potency NET at least DAT and both far above SERT (Rothman's rank order; Han and Gu 2006). VMAT2 was
  missing from its targets, where amphetamine carries it. The owner: "please add VMAT2 reversal to methamphetamine".
  **What that needs, recorded because a sign alone cannot express it**: v5 has SLC18A2 catalysing only two loading
  reactions (`MAR_HISTAMINE_LOADING`, `MAR_NORADRENALINE_LOADING`) and no vesicular efflux reaction, so a reversal
  needs a new curated reaction of the form the three plasma-membrane effluxes already take
  (`MAR_DOPAMINE_EFFLUX` and its two siblings, catalysed through the relation type `catalyzes_reverse_transport`);
  and because a drug's mechanism edge lands on the protein node, one sign would drive loading and reversal together,
  so expressing "inhibits loading and promotes efflux" needs either two mechanism edges or the learned per-relation
  gains to separate them. The existing SLC18A2 rows (amphetamine, dextroamphetamine, lisdexamfetamine, valbenazine
  and one further drug) all carry -1, so the new row's sign is to be set against them rather than in isolation.
- **D2 is learned inside its measured occupancy range, the same way.** The owner: "For d2, do the same hard learning
  constraints". D2 is the one receptor whose resting occupancy by its own agonist is measured directly: Caravaggio et
  al. 2020 pooled human PET and SPECT studies that deplete dopamine with AMPT and found about 11 per cent of striatal
  D2 occupied at rest, range 8 to 21 per cent, i.e. a headroom of 8.1 with a range of 3.8 to 11.5. So D2's headroom is
  learned with 3.8 and 11.5 as hard bounds, as the depletion nulls bound the others. **Why the measurement and not a
  calculation**: occupancy needs neither the affinity nor the ambient concentration, and both are disputed for D2 (the
  affinity end is what this ruling is about, and the voltammetry pass of the same day puts basal dopamine nearer 20 nM
  than the 5 nM the receptor table uses). **Recorded with it**: the measurement is striatal and may not hold for D2
  elsewhere; benzamide tracers see only the receptors they reach; and reading a headroom off an occupancy assumes the
  response is proportional to occupancy, which a receptor reserve would break.
- **The learned fallback stays per relation type, and is used only where no value is sourced.** The owner, correcting
  the session's reading of their question: "sorry. i meant per-relation-type. and only for the unsourced values is
  good for that per-relation learned fallback". So the 28 pore populations with no sourced resting fraction take the
  per-relation-type fallback (at most 22 parameters across the whole graph, against 28 for a per-channel fallback and
  52 for one per pore), and the nine sourced as unbounded (Nav, Cav1, Cav2, Cav3, BK, SK, anoctamin, ASIC, AMPA, their
  resting fractions 10^3 to 10^6 below their ceilings) get **no ceiling**, which is what their measurements say: a
  learned ceiling for them could fit one closer than the sources allow, which would be less physiological and would
  also spend parameters the owner has asked to reduce.
- **The TRPV1 calibration row.** The owner supplied Samways and Egan 2011's author manuscript, so the row rests on the
  owner's copy, not on the page an earlier pass recorded as refused.
- **Headroom stays one value per node, not per region (18 November 2026).** The owner asked whether headroom could
  differ physiologically between regions; the session answered that it does where measured (Hashimoto et al. 1995,
  PMID 7644027, Table 1: glycine 9.25 uM in rat mPFC, n = 25, and 2.75 uM in striatum, n = 4, giving the native NMDA
  strychnine-sensitive glycine-receptor headroom 13.6 and 107; see the correction of 19 November 2026 below), and that the graph has no region structure to hold it: its 16 cell classes on v5
  are cell types, regional only by accident (the dopaminergic class is one midbrain cluster, Siletti 395), and the 13
  HPA brain regions enter only as node descriptors read by the output gate, not by propagation. The owner kept it this
  way ("i think i'll keep it this way for now"), first on parameter count, then correcting that reason themselves:
  "actually, adding the true region structure mostly adds more gates than more params". The reason recorded is
  therefore compute and sourcing, not parameters. A region group in `linear_response_encoder.py` is a fixed expression gate
  on the shared adjacency; it adds only the per-channel parameters (`gain_logit`, `mixture_logit`, `channel_expansion`
  and the like, on the order of 60 to 100 per group, not measured), while each group is a full propagation over the
  adjacency, so run time grows with the group count; and region-by-class weights would have to come from the Siletti
  per-dissection files while most regional ambient and headroom values are unsourced. So each sourced headroom is one
  value per node, and its row records the region it was measured in and why that region was taken. A numerical reason
  (compute) and a sourcing limit against the more physiological version, stated here as the Modelling rule asks.
- **Forebrain glycine takes the cortical value, for now (18 November 2026).** Hashimoto et al. 1995 (PMID 7644027,
  Table 1): 9.25 uM in awake rat mPFC, n = 25, corrected for in vitro recovery only, giving the native NMDA
  strychnine-sensitive glycine-receptor headroom 13.6 (against 107 for striatum, 2.75 uM, n = 4, and 117 for the spinal 2.6 uM used until now). **Corrected 19 November 2026**: these three numbers are (42.9/C)^1.7 on the Jiang et al. 2009 curve for the native strychnine-sensitive glycine receptor, not for the NMDA receptor's glycine site, which had no retrieved EC50 until Matsui et al. 1995 supplied one (`matsui_dserine_2026-11-19.md`). The ruling that forebrain ambient glycine takes the cortical value is unaffected; what that concentration gives the GRIN1 site is a different number. **Rulings of 19 November 2026 on the Matsui pass** (`matsui_dserine_2026-11-19.md`): (1) the GRIN1
  glycine site takes glycine and D-serine together, summed as x = Gly/K_gly + D-Ser/K_Dser, since it is one site with
  two endogenous full agonists (the owner: "Yes"), which needs an ambient D-serine value of its own (forebrain about
  5.75 to 6.5 uM, Hashimoto and Matsui, one laboratory); (3) which potency set (Matsui 1995, D-serine 3 to 4 fold more
  potent, against Zhao 2022, equal or weaker) and which GluN2 partner stands for the single GRIN1 node is left to a
  Fable pass (the owner: "I can't adjudicate that. Defer to fable"); (4) the per-region co-agonist identity is not a
  separate question, following the region split already ruled for glycine, except that the GRIN1 node has no region
  structure on v5 and so takes a forebrain value until that structure exists. On bulk against receptor-sensed (2) and
  on a learned parameter seeded at the single-laboratory value (5) the owner is still deciding.
  The owner: "go with cortex for glycine for now with a note to followup with methods for incorporating evidence from
  multiple regions if this fable pass comes back saying not to incorporate the regional structure and followup on
  splitting it per region otherwise". **Follow-up, conditional on the Fable pass on anatomical connections between
  regions started 18 November 2026** (`anatomical_connectivity_2026-11-18.md` in that session's scratchpad): if it
  advises against regional structure, decide a method for combining evidence from several regions into one node's
  value (the session's proposal, not ruled: the regions' values measure different true quantities, so they combine by
  the aggregate H = sum a_i (1 - o_i) / sum a_i o_i with a_i the regional receptor amount, and evidence strength sets
  each region's uncertainty, not its weight); if it advises for regional structure, split the value per region. **The
  question set aside with it**: regional pools, region-by-class channel groups and a readout per region (VM_c per
  region at least) go together, and connectivity between regions is needed even for the pools, since a projection
  neuron's mRNA sits at its somata and its release at its terminals; they are one decision outside item 37.
  **The condition is met (18 November 2026).** The pass recommended a minimal regional version (monoamine projection
  edges with regional copies of the fast-cleared pools, release at the terminal region), and the owner: "i agree with
  minimal regional structure. we just need to rule on what form", preferring a primate connectome to the Allen mouse
  one (a second Fable pass, `primate_connectome_2026-11-18.md`, was started for it). So glycine's follow-up is the
  split per region, once the form is ruled; the multi-region combination method is not needed for it.
  **The form is ruled: option C (18 November 2026).** Offered (A) regional copies of the pools with projection edges
  and the receptors shared, (B) region-by-class channel groups for a few regions with projection edges, or (C) B with
  the regions chosen by the axes the labels hold, the owner: "i choose option C". The label count behind it
  (`data/processed/label_selection/better_v2_full_v5.parquet`, measured 18 November 2026: 1,384 kept drug pairs, 190
  drugs, 33 symptoms) found no endocrine symptom, so the tuberoinfundibular projection has nothing to fit and is left
  out, while motor (7 symptoms, about 137 pairs), sleep and arousal (somnolence the largest, 158), psychotic,
  affective, impulse, appetite and cognitive axes are present. The regions proposed with C, which the session reads
  the ruling as taking: dorsal striatum (motor), ventral striatum and nucleus accumbens (impulse, psychotic),
  prefrontal cortex (cognition, psychotic), hypothalamus (sleep, appetite) and the brainstem and midbrain source nuclei;
  the histaminergic projection is added to the pass's monoamine list for somnolence. Costs recorded: region-by-class
  weights from the Siletti per-dissection files (their route under the CELLxGENE block to be checked), a curated
  projection table with two sources per row, and a map from the primate parcellation onto these regions. The owner,
  on the session's flag that pramipexole, ropinirole and pergolide carry parkinsonism labels while treating
  Parkinson's disease: "the ropinirole case is a dose-dependent effect", so it is not treated as indication
  confounding.

- **The v5 rebuild of the dry run and the measured sensitivity rank come after item 37 is pushed.** The owner, 18
  November 2026: "should happen after item 37 is pushed remote".

- **A pore is added when it sits on any central cell class.** The owner, 18 November 2026, correcting section 1's part
  (iii), which admitted only pores on a central neuron: "yes, that's the correct way: cell central class is the rule".
  Glial classes count, and "ependymal choroid should be included because it feeds the glymphatic system. same for
  vascular, but only for central vasculature". A pore on no central cell class (the muscle-type nicotinic receptor)
  stays out. Kir6.1 is kept as its own population weighted by class expression, its reason corrected to mostly
  non-neuronal (mural cells, then astroglia); Nax is kept as its own population, split from NALCN, its conductance
  flagged (the owner: "otherwise, suggestions accepted").
- **Clearance is registered in the confirmatory model.** The owner, 18 November 2026: "just REGISTER it. i don't care
  how. no clearance, etc. is unacceptable for this project". The seed split is the sourced-ratio version renormalised
  to 1 per drug, with the uniform split as fallback; the quantities beyond C and K that the 18 November answer lists
  are sourced first (the owner: "accepted. please start the sourcing pass").
- **Dose enters through concentration, not a therapeutic-index scale.** The owner accepted that labels are not
  dose-resolved and that a concentration sweep gives the multiple readouts.
- **Clearance runs through one universal clearance node.** The owner, 18 November 2026, accepting that clearing
  enzymes are not disjoint from endogenous metabolism: "there will have to be a universal clearance node with a
  separate edge from clearing enzyme to the clearance node for each substrate that the enzyme clears".

## 13. Rulings of 18 November 2026 on the occupancy split, plasma binding and ambient dopamine

Recorded by the session on 18 November 2026 from the owner's messages of that day; shown to the owner before any
commit. Graph counts are on the build directory `graph_full_neuronal_split_binders_drugs_v5` (files of 12 November
2026, not the registered v5), measured 18 November 2026.

- **IC50 and EC50 are admitted, after sourcing is attempted.** The owner: "i say that IC50 should be included just make
  sure to attempt sourcing values first". **Withdrawn:** the session had written of an "owner's not-IC50 rule"; the
  owner never gave one ("i never said gave a 'not-IC50 rule'"), and a Fable pass traced the phrase to a session's own
  planning note (`affinity_with_ic50_2026-11-18.md`, section 1). The repository already pools the types
  (`docs/off_target_scoping.md`). With the four types admitted, 259 of 465 pairs carry a value (Ki 189, IC50 48, EC50
  12, Kd 10; 189 with two sources) and 206 carry none. The earlier counts of 363 and 383 were equilibrium-only counts
  taken during a partial harvest and are superseded. No Cheng-Prusoff conversion is made: the pass finds it
  conditionally defensible for 20 of the 48 IC50 rows and not for the 28 channel, transporter and allosteric rows. The
  quantity type stays on each row, and a drug whose shares mix types is marked method-dependent under the
  uniform-method rule.
- **A modulator's potentiation EC50 is admitted on the same footing.** The session had asked whether the potentiation
  EC50s of positive allosteric modulators (the volatile anaesthetics, Krasowski and Harrison 2000; stiripentol, Fisher
  2009) should enter the split or go to the learned fallback, because they are not binding constants. The owner, 18
  November 2026: "i don't see why EC50 would be treated any differently than IC50 in terms of inclusion for
  occupancy". **The session's distinction does not hold**: an IC50 is a functional potency conditional on its assay
  as well, and IC50s are already admitted without conversion. So these values enter as EC50 rows, with the receptor
  assembly they were measured on recorded beside each value, and the uniform-method rule marks any drug whose shares
  mix types. Pairs no source covers (a subunit not in a measured assembly, the KCNK pairs, desflurane) still go to
  the learned fallback, after sourcing is attempted.
- **No uniform fallback.** The owner: "no uniform fallback. it's too non-physiological". Its replacement, the owner:
  "a learned fallback starting with equal shares but i'm open to other ideas". The session proposed starting from the
  median of the sourced pairs of the same class in log space, tying pairs by class with a per-pair offset shrunk
  toward the class value, and a soft clamp to the class's sourced range with strength set by evidence. The owner:
  "yes but \"by class\" is doing a lot of work here and needs a strict definition that should be addressed by a fable
  pass". **So the shape is accepted and the definition of class is open**, with a Fable pass started on it
  (`fallback_class_definition_2026-11-18.md`).
- **The `sequesters` weight is the bound fraction times the carrier's share.** The owner: "use option a for the
  per-carrier weighting with your suggested fallback order". Weight = (1 - fu) x the carrier's share of the binding,
  with fu kept as an attribute of the drug node; a drug with no measured human fu takes the ranked fallbacks of
  `sequesters_fu_2026-11-18.md`, section 5. For the 30 heavily bound drugs with no carrier edge, the owner: "have all
  sourcing options been exhausted [...]? if so, then use the familiar learned fallback soft-clamped to measured range
  with clamping strength based on evidence prior". Sourcing was not exhausted, so a Fable pass is naming the carriers
  first (`carrier_identity_2026-11-18.md`).
- **The carrier share takes the ranked sources, and its last resort is the occupancy split's learned fallback, not an
  equal split.** The carrier pass named a carrier for 16 of the 30 drugs (8 from two independent sources), found weak
  evidence only for 4 and none for 10, and set out the sources of a share within a named carrier set: a published
  split (rotigotine, remifentanil, nortriptyline, methohexital), a conversion of isolated-protein percents (lemborexant,
  istradefylline, vortioxetine), then the acid/base class rule, protein concentrations with an affinity ratio, and a
  regression of fu on each protein, with an equal split last. The owner, 18 November 2026: "this is fine but use the
  same replacement for the uniform fallback as the occupancy". **So the order stands and the equal split is
  replaced**: where no source gives the share, it is learned, starting from the median of the sourced members of the
  same class in log space, with a per-drug offset shrunk toward the class value and a soft clamp to the class's
  sourced range whose strength is set by the evidence prior. What a class is here is open, as it is for the occupancy
  split, and carries the same guard against circular reasoning.
- **A monkey Kp,uu is accepted.** The owner: "kp,uu: accept monkey also".
- **A compound that is both a study drug and another drug's active metabolite is treated as both.** The owner: "joint
  drugs/metabolites: treat as both".
- **TPM and single-nucleus counts per million are not interchangeable without the per-gene confounds.** The build
  already rescales by a trimmed mean of M-values (`trimmed_mean_scale_factor`), which fixes the scale and not the
  per-gene bias, transcript length first among them. The owner asked for "a fable pass to source the other confounds to
  be able to convert between TPM and nCPM" (`tpm_ncpm_confounds_2026-11-18.md`).
- **The conversion is option D: transcript length plus the published nuclei-to-bulk factor.** The pass set out five
  options, scored on the share of genes within two-fold across four tissue pairs with no coefficient fitted on the pair
  scored: one global factor (the build today) 30 to 35 per cent; transcript length alone (B) 37 to 46; lengths, GC and
  poly(A) sites (C) 45 to 63; transcript length plus Huuki-Myers et al. 2025 Table S5 (D) 66 to 82; and per-class
  pre-mRNA modelling from the authors' spliced and unspliced matrices (E), the physiological version. The owner, 18
  November 2026: "for the TPM confounds, go with option D. record the numerical reasoning that it confines the
  confounds in that the measured values and makes more of the values accurate to within 2x". So log2(nCPM / TPM) =
  log2(GTEx collapsed-model length) + the Table S5 log ratio + a constant. **Justification under the modelling rule**
  (the session's reading of the owner's reason): D's per-gene term is a measured value, so the confounds it corrects
  are held in a published measurement rather than in a slope fitted on the project's data, and it brings the most
  genes within two-fold (66 to 82 per cent, against 30 to 35 today). E is not used because it cannot be obtained: the
  link in the authors' README to the spliced and unspliced matrices answers 404 (18 November 2026). **Limits recorded
  with it**: Table S5 is one study of ten donors in one cortical area, and the fit is worse in putamen (channels and
  receptors 45 to 75 per cent); it covers 9,894 of the 12,660 mapped gene nodes; every figure is tissue against tissue,
  with nothing tested per cell class or in thyroid, pituitary or islet, where the build's conversions are actually
  made; the pre-mRNA share per class, ambient RNA and the composition of the bulk reference stay uncorrected. GENCODE,
  whose annotation gives the length, has no named licence found and no row in `docs/data_sources.md`.
- **The conversion runs from TPM to nCPM, and a gene outside Table S5 takes transcript length alone.** On direction
  the owner, 18 November 2026: "I thought that was the only direction that was viable". So the bulk columns (GTEx
  thyroid, pituitary and islet, `graph/peripheral_cell_classes.py`, `scaled_to_ncpm`) are moved onto the nuclei nCPM
  scale the brain classes and the registered thresholds already use. The per-gene term is invertible, so the other
  direction is possible in arithmetic; TPM to nCPM is taken because the reference scale and most columns are nCPM, and
  converting them instead would move every threshold registered on that scale. For the 2,766 mapped gene nodes that
  Table S5 does not cover, the owner first accepted an annotation fallback (transcript length, intron length and GC,
  reported at 48 to 63 per cent within two-fold); a gene-held-out check (`tpm_fallback_holdout_2026-11-18.md`, data
  files at `e170c31f`, 18 November 2026) then found that figure was scored almost entirely on Table S5 genes, and that
  on the genes outside it the fallback reached 36 to 51 per cent, with no consistent gain over transcript length alone
  (42 to 45 per cent; global factor 35 to 39). The owner, 19 November 2026: "go with transcript length alone for the
  fallback since it's at least mechanistic correction". So log2(nCPM / TPM) = log2(GTEx collapsed-model length) + a
  constant for those genes, with nothing fitted on the project's data, which keeps D's reason (no fitted per-gene
  slope) for every gene. **The recorded figure** (the owner: "Yes" to replacing it): 36 to 51 per cent within two-fold
  for the fitted fallback and 42 to 45 for length alone, measured on the 431 of the 2,766 nodes that have an observed
  ratio in at least one tissue pair; the other 2,335 (84 per cent, mostly near zero in brain) are unmeasured. Gene-level
  cross-validation showed no leakage in the earlier tissue-held-out scoring (at most 0.5 point); that report's sentence
  "no row is fitted on the genes it is scored on" holds of observations, not genes. **Limits** (the owner: "Yes" to
  recording the offset as a limit): genes outside Table S5 sit 0.2 to 0.85 log2 above the calibration set on the genes
  inside it, and that offset cannot be estimated in a tissue with no paired nuclei data, so it stays uncorrected;
  nothing in D or the fallback is tested outside brain tissue, where the conversions are actually made, and 861 of the
  out-of-S5 genes reach TPM 1 in thyroid, pituitary or pancreas with no observed brain ratio. On that the owner asked
  for sources: "Look for sources because I don't think we have for peripheral yet and start it now please" (a Fable
  pass started 19 November 2026, `peripheral_ncpm_sources_2026-11-19.md`). The pineal column (GEO GSE100472) is a
  full-length read CPM, a third scale whose length term is already in the value, so its conversion would drop the
  length term; that is the session's arithmetic and is open.
- **Sources for the peripheral conversion, and the rulings on them** (`peripheral_ncpm_sources_2026-11-19.md`, a Fable
  pass of 19 November 2026). Found: HPA single nuclei for pituitary (Zhang et al. 2022, six glands, GSE178452), GTEx's
  unpublished `single-cell/v11/` release (10x Multiome nuclei, 21 tissues, 4 donors, pancreas with a beta-cell label, no
  thyroid or pituitary), side-by-side nuclei and whole cells from islets (Kang et al. 2023; Basile et al. 2021) and GTEx
  v9 snRNA-seq (Eraslan et al. 2022, 8 tissues); for healthy thyroid, nothing. The owner, 19 November 2026:
  - **Islet**: "yes. no" to fetching the v11 pancreas file with GTEx pancreas TPM, and to whether an unpublished
    release counts as evidence; the owner, confirming: "unpublished releases don't count". So the v11 release is not
    evidence for any conversion, the islet has no published nuclei-to-bulk source on disk, and the islet GEO series
    GSE217837 (Kang et al. 2023, published) is wanted: the owner supplied a paper for it on 19 November 2026, which
    turned out to be a later article citing the series (Kang et al. 2025, Nat Commun, doi:10.1038/s41467-025-62670-5),
    not the data files.
  - **Thyroid**: rests on the transfer test ("it depends on the result"); "cancer-adjacent nuclei are out: too much
    confound".
  - **Transfer test** (whether a per-gene factor measured in brain holds in other tissues, measured on GTEx nuclei
    against GTEx bulk): "yes". With the v11 release out, it runs on GTEx v9 snRNA-seq alone (Eraslan et al. 2022,
    published; 8 non-endocrine tissues).
  - **Licences**: "whatever you think is right". The session's choice: GTEx is recorded as open access with no named
    licence found, unverified, with the routes tried (bucket description files, the portal's robots refusal, the Cell
    Annotation Platform page) and the portal's licence page left for the owner to open; the GPL-3 Zenodo record goes
    with the cancer-adjacent data and is not recorded.
  - **HPA refetch** of the single-cell-type table (`docs/data_sources.md` row 26 holds 154 cell types; the page lists
    155): "sure".
  - **Pituitary**: "use HPA directly". So the pituitary class is read from HPA's single-cell-type table (refetched 19
    November 2026, 155 cell types, sha256 2fdc5094...), which splits it by lineage (somatotrophs, lactotrophs,
    corticotrophs, gonadotrophs, thyrotrophs, pituitary stem cells) on the nCPM scale of the brain classes, so no TPM
    conversion applies to it. The owner, 19 November 2026, on whether each lineage is a class: "separate classes". So the pituitary becomes six
    classes, one per HPA lineage, and ALX1 to PRL acts where lactotrophs express it.
    The owner had asked whether this was an HPA "slice size problem because the pituitary is small"; the session found
    no such problem recorded in the repository.
- **Ambient dopamine.** At D2 nothing changes: the PET depletion studies measure occupancy, which is the ratio of
  concentration to affinity, and a drug's competition at D2 needs only that ratio, 1/(1 - occupancy) = 1.09 to 1.27, so
  the disputed D2 affinity cancels. The session had called the value circular and proposed dropping it; the owner:
  "i think you might be overreacting again [...] they could be measured without competition". Checked per ligand: of
  the sixteen ambient values only three are receptor-based (dopamine at D2 by tracer displacement; glutamate by NMDA
  receptor current; adenosine by antagonist shift, which microdialysis matches independently), and none is circular
  outside the sensing receptor. So the session's flag to revisit the glutamate ruling is **withdrawn**. For the
  concentration exported to the other dopamine receptors and the transporter, the owner: "carry the range estimates for
  the disputed d2 affinity through the calculation to the bounds for the learned param", and, on extending the lower
  bound to the estimates that do not use a receptor (7 to 20 nM, Chen 2005; 20 to 30 nM, awake voltammetry): "sure,
  widen the lower bound of exported concentrations".
- **The depletion behind the D2 occupancy is incomplete, in direction if not in size.** The owner: "double check the
  AMPT depletion please". The human studies report plasma homovanillic acid falling 61 to 71 per cent (Verhoeff et al.
  2001, 2002, 2003), so the 8 to 21 per cent occupancy is a lower bound on that account; no abstract gives the fall of
  brain dopamine, and the full texts were not read (`ampt_depletion_check_2026-11-18.md`).
- **So D2's lower headroom bound is soft, and incomplete depletion softens any bound.** The owner, 18 November 2026:
  "make the D2 bound soft since it's depletion was incomplete. that rule can extend to any other cases too". So the
  lower bound of 3.8 becomes a soft bound whose softness is scaled by the reliability of the evidence prior, by the
  same method as the other soft bounds of section 7 above, and the upper bound of 11.5 stays as it was: incomplete
  depletion biases the measured occupancy downwards, which weakens the floor it implies and not the ceiling. The rule
  generalises, and it carries both legs of the earlier ruling, not one (the owner, the same day: "remember the other
  half of that depletion null that i ruled earlier too: it has to be human AND fully depleted to be a hard bound").
  **So a bound read off a depletion experiment is hard only where the experiment is human in vivo AND the depletion is
  complete.** A bound resting on an incomplete depletion, or on one whose completeness is unestablished, enters as a
  soft bound; so does one resting on an animal experiment, however complete its depletion. This widens the ruling of
  section 7, which stated both legs for the depletion nulls of 5-HT1A and 5-HT2A, to every bound of this kind, D2's
  included. D2 fails on the second leg alone: Caravaggio et al. 2020 pool human studies, so the measurement is human
  in vivo, and it is the incompleteness of the AMPT depletion that makes the floor soft.
- **Withdrawn the same day:** that serotonin was settled at 1.4 nM for P32 and P33 (it is unruled: 1.4 nM by
  microdialysis against 52 to 77 nM by voltammetry; only the mismatch between P32 and P33 is a fix), and that
  microdialysis "reads dopamine several-fold low" as a measured fact (the owner: "how can you know [...] unless you
  know the real value"; it is a directional inference from Bungay 2003 and Chen 2005).
- **429 and 503 are not refusals.** The owner: "i already ruled on the 429/503 error codes. they don't count as blocks
  so retry them". The session treats 500 and a timeout the same way. Still to be written as its own decision row and a
  line in `CLAUDE.md`, with the reader's missed case (PubMed's HTTP 203 human check is reported as a plain status).

## 14. Rulings of 19 November 2026 on the class for the occupancy split's learned fallback

From the Fable pass `fallback_class_definition_2026-11-18.md` (measured on the 12 November 2026 build, not the
registered v5). The owner, 19 November 2026: "1-4. go with recommendations"; so:

- **Class** = GtoPdb family of the protein (pinned release 2026.3.1) crossed with the pair's mode of action.
- **Mode** = the eight-value rule over the ChEMBL_37 action type and protein class, not the raw action type.
- **Back-off** at fewer than k = 3 sourced measurements: GtoPdb type × mode, then mode alone, and **no value below
  mode**: never the global median. A pair with no level of at least k measurements is listed for sourcing.
- **Not for receptor ligands.** The owner, on the 0.3 log10 bar (+0.34 overall, +0.10 [−0.01, 0.21] inside the
  receptor ligands): "then don't use it for the receptor ligands".
- **Amisulpride's 11 serotonin pairs** are curated before any fallback is applied ("yes").
- **Prodrugs and metabolite-acting drugs** take the metabolite's sourced values ("yes"), each decided on its own case.
  The owner added: "the fact that you ask if metabolite-acting drugs take the metabolite sourced value makes me worry
  that their metabolizing enzymes are not properly represented in the graph. please double check it".
- **The glutamate receptors are split** into AMPA, kainate and NMDA ("they definitely need split"), by ChEMBL_37
  protein class level 4 ("yes, level 4").
- **Quantity types in a class statistic: option (b)** ("go with b"): the median and clamp range of a class are taken
  over sourced measurements of the class's expected quantity family where at least k exist, and otherwise pooled with
  the mix recorded on the row. Option (c), pooling after a fixed factor-of-two shift of IC50, is not used.
- **Acamprosate's 13 GABA-A edges are removed** ("remove acamprosate edges"): an edge with no share does nothing in
  propagation, and the claim it carried is a sourced negative, recorded in the curation file rather than the graph.
- **Two Fable passes started 19 November 2026** at the owner's request ("yes start both fable passes"): the prodrug
  and metabolite audit (`prodrug_audit_2026-11-19.md`) and the subtype transfer question behind the sibling centre
  (`subtype_transfer_2026-11-19.md`).
- **A receptor-ligand pair with no sourced value gets no fallback value and is listed for sourcing** (the owner: "no
  value for receptor ligands: send to sourcing").
- **SCN7A**: the four edges (orphenadrine, primidone, topiramate, cenobamate, all through ChEMBL_37 target
  CHEMBL2331043) are checked on Fable (the owner: "yes check SCN7A on fable"; `scn7a_check_2026-11-19.md`).
- **Still open from this pass:** the sibling-subtype centre (the owner: "i can't decide. i see both sides equally").
  The Fable pass on it (`subtype_transfer_2026-11-19.md`) found it a physiological transfer for aminergic receptor
  families (error 0.16 to 0.52 log10, near the 0.44 assay floor of Kramer et al. 2012) and the uniform fallback in
  another form for the channel and allosteric pairs, whose "siblings" are one value copied across subunits (40 of the
  49 pairs); it recommends restricting the centre to receptor families with at least two distinct sourced siblings.
  The owner, 19 November 2026: "wait for ChEMBL check", the pass's out-of-project validation on ChEMBL, still
  harvesting.

## 15. Rulings of 19 November 2026 on the carrier share, ambient values and expression

- **The carrier-share class is ion state, and ion state is taken at the compartment's sourced in vivo pH** (the owner:
  "the ion state should depend on a sourced invivo pH for the compartment"), not at a fixed 7.4. The six conversions
  made by research passes (istradefylline, lemborexant, vortioxetine, fosphenytoin, melatonin, cocaine) count as
  sourced members ("count the 6 conversions"). Where MoKa has no row, a Fable pass looks for other sourced pKa values
  ("start a fable pass to check for fallbacks from MoKa"; `ion_state_sources_2026-11-19.md`). McNamara and Meiman
  2019 Table 3's shares, calculated from binding to isolated albumin and AAG rather than measured in plasma, count as
  sourced at a lower evidence weight than a whole-plasma split (the owner: "count Table 3 with the lower weight"),
  each row marked "calculated from isolated proteins".
- **Non-plasma carriers get `sequesters` edges, confined to the compartments they occupy** (the owner: "they should
  get edges but make sure they are confined to compartments in which they appear"): erythrocytes in blood, lipoproteins
  where lipoprotein particles are, and so on.
- **Deferred** by the owner: ambient serotonin, the peptide receptor bands, and how the calibrated regression scores a
  depletion study for a soft bound.
- **The bulk classes take option D with slope 1** (the owner: "suggestions accepted", on the transfer test,
  `transfer_test_2026-11-19.md`): thyroid and the other bulk-converted classes take the Table S5 term at slope 1, with
  the accuracy recorded as 52 to 64 per cent within two-fold measured in eight non-brain GTEx tissues (Eraslan et al.
  2022) and unmeasured in thyroid, not the 66 to 82 per cent of brain; the over-correction outside brain (measured slope
  0.57 to 0.78) is recorded as a limit; the factor derivable from the GTEx v9 atlas is not used as the conversion; and
  the mitochondrial genes are left out of the normalisation that sets each tissue's constant, because nuclei hold almost
  none of their RNA and a bulk TPM column spends 20 to 67 per cent of its million on them.

- **The pineal column is converted without the length term** (the owner: "yes"): it is full-length read CPM, which
  already carries transcript length, so log2(nCPM / read CPM) = the Table S5 term + a constant, a gene outside Table
  S5 taking the constant alone, and the mitochondrial genes left out of the normalisation as for the TPM columns.
- **The islet check uses GSE217837** (Kang et al. 2023, Genome Medicine): the owner gave the three supplementary-file
  addresses from the GEO page (scRNA, snRNA and graft in vivo snRNA count matrices, 178.7 to 227.5 MB), fetched on
  19 November 2026 under the CLAUDE.md exception for a data file its provider published for download, each pinned by
  SHA-256 in `scripts/fetch_raw_sources.sh`.
- **The search for several steady states is deferred to a decision of its own, outside item 37** (the owner: "defer to
  separate decision outside item 37 with item 37 written under the understanding that something will eventually be
  added to address it"). So item 37 is written on the understanding that a method for finding several steady states
  (deflation, multistart or a hybrid, `deflation_multistart_2026-11-17.md`) will be added later, with its stability
  criterion, its starting states and its handling of roots at a bifurcation.

- **Ion state: sourced pKa values, arterial plasma, and fractions, not a hard class** (the Fable pass
  `ion_state_sources_2026-11-19.md`: 60 of 95 drugs with a sourced pKa, 28 measured; one sourced member, nelfinavir,
  moves cationic to neutral; the class still misses the bar, +0.23). The owner, 19 November 2026: "Yes to carrying
  the fraction" (each drug's charged fractions by Henderson-Hasselbalch, so a drug near a pKa is not forced into one
  class), assigned as a mixture of class medians (the owner: "For soft membership: a"): each sourced member counts
  toward every class in proportion to its charged fractions, so a class median is a weighted median and the clamp
  range a pair of weighted quantiles, and a fallback drug starts at the fraction-weighted mix of the class medians,
  with nothing fitted; the regression on the fraction is not used; "Arterial makes more sense" (plasma carriers at
  pH 7.40); and, on the gap between the 20 to 25 °C at which most pKa values were measured and 37 °C, "Start the
  source now" (a Fable pass, `pka_temperature_2026-11-19.md`).

- **A zwitterion or ampholyte stays one drug node, with its carrier influence split across its microspecies by
  linkage.** The owner, 19 November 2026, after proposing separate nodes per ionisable group at 1/n ("I figured 1/n
  was wrong but I didn't know if it should be just the fraction by molarity or that times some property of each
  group. The linkage issue is much bigger. That might be solvable by keeping a single node and splitting its influence
  since drugs don't currently have node descriptors. Oh. That's what you suggest. Do that"). So each microspecies
  enters by its measured fraction times its own affinity for the carrier, the equilibrium between forms shifting as
  one is bound, rather than at 1/n or at its resting fraction alone; separate nodes are not used. The formula, the
  microconstants to source (tiagabine first) and the case of unknown per-form affinities are with a Fable pass
  (`zwitterion_2026-11-19.md`). That pass found tiagabine 97 to 99 per cent zwitterion at pH 7.40 however its
  unknowns are set. The owner, 19 November 2026, on its rulings: "go with your recommendations for the zwitterion
  rulings". So:
  - tiagabine's macroscopic pKa values (3.3 for the acid, 9.4 for the amine; the Australian GABITRIL Product
    Information, revised 18 May 2018) are used on one source, marked as such;
  - where no tautomeric constant (KZ) is measured, an estimate from a blocked-site analogue is allowed, labelled with
    its range (tiagabine: log KZ about 4.7, 3.7 to 5.7, from arecaidine against its methyl ester; the pass's estimate);
  - step 1 replaces the four-way class: y = log10 of the sum over forms of f_i times 10^(y_class(i)), the class medians
    mixed by each form's fraction, with nothing new fitted;
  - step 2, linkage, is on now: at most three shared parameters for how albumin's affinity differs between forms,
    started at zero and bounded at plus or minus one log unit on Dargó et al. 2020's measured pKa shifts on binding;
  - the zwitterion class gets no value until a zwitterionic member is sourced (the k = 3 rule), so tiagabine is listed
    for sourcing;
  - cetirizine and fexofenadine are sourced as zwitterionic members (Pagliara et al. 1998 and the Krogsgaard-Larsen
    papers are subscription-only, for the owner to supply);
  - the independent-sites calculation is used only where a drug's two pKa values are more than about two units apart;
    the rest (oxicams, fluoroquinolones, niflumic acid) are flagged as needing microconstants.

## 16. Rulings of 19 November 2026 on the remaining list

The owner, 19 November 2026, on the numbered list of open decisions with the session's recommendation beside each:
"All accepted. For 8: yes". So, in that list's order:

**The pKa temperature correction** (`pka_temperature_2026-11-19.md`; the shift is sourced from Sun and Avdeef 2011,
the IUPAC digitized dataset and NIST 2002, which agree within 0.05 at the median: aliphatic amines -0.27 to -0.34,
imidazole -0.25, aromatic amines -0.17, pyridine-type nitrogens -0.15, barbiturates -0.16, phenols -0.14, sulfonamides
-0.20, carboxylic acids about 0):

1. The fraction is computed from the corrected constant: a direct 37 °C value where one is measured (10 of 60 drugs,
   lidocaine 7.61 at 36 °C among them), the group shift otherwise. **Justification under the modelling rule**: leaving
   a 25 °C constant as printed biases every base one way, toward more charge than it carries at body temperature; the
   group median stands in because no 37 °C measurement was found for 50 of the 60.
2. The shift is the group median, not a shift that also depends on the constant, which would need a fitted relation.
3. The within-group range rides with the fraction (buspirone 0.40 to 0.61), as other ranges are carried to bounds.
4. Constants at plasma ionic strength, about 0.15 M, as Sun and Avdeef measured them. Recorded with it: ionic strength
   works against the temperature shift for bases (lidocaine 7.61 in water against about 7.8 in salt).
5. Values are cited as facts with their source and no table is copied: Sun and Avdeef and NIST are both closed, and
   values derived from the IUPAC dataset (CC BY-NC 4.0) stay out of repository files, every one of its eight in-scope
   drugs having a second source.

**The ion state** (`ion_state_sources_2026-11-19.md`):

6. Where sources disagree, the median of the measured aqueous values, the rule that pass fixed before recomputing.
7. For the 35 drugs with no sourced pKa: MoKa's value first, marked calculated, then the structural rule once its four
   defects are repaired (acidic heteroaryl sulfonamides, the pyrazolidinedione acid, the azide artefact that made
   azidocillin "zwitterionic", weak-base amines of nelfinavir's kind). Cisplatin, which has no constant, gets no class.
8. **PubChem becomes a third host exception to the robots rule, for its measured pKa records** (the owner: "For 8:
   yes"), after `ftp.ebi.ac.uk` and `dblp.org`. As with those, it covers that host over https, the robots file is still
   read and its answer recorded beside the page, and the reader's other limits hold. Recorded with it: PubChem's
   records carry each depositor's own licence, so a record's licence is verified before its value is relied on. **To be
   written into `CLAUDE.md` "Reading sources" with the other two.**
9. Health Canada and the FDA printing the same manufacturer's number is one source, not two, as the rule on two
   renderings of one document already says.
10. The 11 near-boundary drugs among the 89 uncurated (phenobarbital, thiopental, acetazolamide and the rest) are
    sourced; the other 78 are not.
11. Nelfinavir moves cationic to neutral, on a potentiometric pKa of 6.00.

**The islet conversion** (`islet_check_2026-11-19.md`):

12. The islet constant is set on the Kang et al. 2023 nuclei, which removes the two-fold low bias that the
    mitochondrial exclusion leaves when the constant is borrowed from brain.
13. The general rule: mitochondrial genes stay out, and each tissue's constant is set robustly against that tissue's
    own dominant genes where nuclei data exist, rather than by dropping genes above 1 per cent of a bulk column, which
    is a threshold and would need its own justification. **Why the earlier reasoning was wrong**: the session had
    treated mitochondrial genes as the special case; the real problem is any small set of genes that dominates a bulk
    column and that nuclei do not hold in proportion (GTEx `Pancreas_Islets` spends 32 per cent of its million on INS,
    50 per cent on ten genes). Before the exclusion the two dilutions cancelled by accident, brain losing about half
    its million to mitochondrial genes and islets about half to hormones and enzymes. Thyroid is barely affected (TG is
    1.2 per cent of its bulk); pituitary no longer converts at all, being read from HPA.
14. The accuracy recorded for the islet class is 58 per cent of genes within two-fold (52 to 60 by donor), measured on
    the Kang nuclei against GTEx `Pancreas_Islets`, with slope 1 supported in islets (measured 0.91).
15. The islet class stays converted GTEx bulk, not the Kang nuclei: those are three donors, cultured overnight with
    stress genes up, SoupX-adjusted, beta-rich, and their licence is unverified.
16. The acinar transcripts in GTEx `Pancreas_Islets` (PRSS1 2.4 per cent, CPA1 1.5 per cent of the million) are
    recorded as a limit of the laser capture.
17. The hormone genes outside Table S5 (INS, GCG, TTR, IAPP, PPY, over-predicted 5 to 95 fold by length alone) take the
    islet's own measured nuclei-to-bulk ratio from Kang, which is a measured per-gene value in the right tissue and so
    carries option D's reason.
18. Table S5's upper tail (511 of 17,660 values above +5; ATP6V0C over-predicted 4,700 fold, SCG5 900 fold) is
    investigated by a short Fable pass before anything is bounded, a bound being a numerical device.
19. The donor mapping, inferred from the data, is checked against GEO's sample table when the owner can supply it.

**The carrier rows** (`carrier_fulltext_2026-11-18.md`, `temazepam_binding_2026-11-19.md`):

20. **Temazepam: albumin, moderate weight, with the row marked that its free fraction is modulated by fatty acids and
    condition rather than driven by albumin concentration.** Albumin is the only carrier any source names or
    characterises (Fitos et al. 1986, isolated albumin, Sudlow site II), but in whole plasma the free fraction does not
    follow albumin (Chin et al. 2011, slope about 0; Divoll et al. 1981, r = -0.34, p = 0.06), while it moved 44 per
    cent at matched concentration between fast and slow infusion (van Steveninck et al. 1994, abstract) and the site's
    affinity falls to a tenth at an oleate ratio of 3:1 by a conformational change (Menke and Rietbrock 1987, measured
    with a marker ligand, not temazepam). Concentration dependence is refuted (Morino and Sugiyama 1985, rat).
    Modelling the free fraction as a modulated quantity is parked in `docs/exploration_queue.md`, since it would reach
    every drug bound at site II. **A caution from the session, not from a source**: heparin in a sampling line releases
    fatty acids in the tube, which can raise a measured free fraction, so van Steveninck's full text is fetched before
    that number is relied on.
21. Apomorphine takes albumin and AAG edges from the FDA Apokyn review's quoted 88 and 33 per cent, marked
    isolated-protein percents (they sum to 121) at the lower weight.
22. Fluphenazine takes an AAG edge beside its albumin edge, both isolated-protein, at the lower weight; Kornguth et al.
    1981's full text would firm it up.
23. Sertraline keeps albumin alone; its AAG claim stays unsourced until Murdoch and McTavish 1992 or DeVane et al. 2002
    is read, every route to it so far being a secondary statement.
24. ORM1 against ORM2 is weighted by their plasma abundance, about 2 to 3 against 1, not equally.

**SCN7A and primidone** (`scn7a_check_2026-11-19.md`):

25. The SCN7A edge is removed for all 26 drugs that carry it, not only the four examined: it is an artefact of the
    ChEMBL_37 family target CHEMBL2331043, whose record lists SCN7A as a "GROUP MEMBER", Nax has its own single-protein
    target with none of these mechanisms on it, and no source shows any of them acting on Nax (phenytoin has evidence
    against, no strong block at 300 µM; lidocaine's only evidence is block at 10 mM on an engineered open mutant).
    Recorded with it: PROTEIN:SCN7A catalyses `MAR_SODIUM_LEAK` beside NALCN, so these edges were acting on the sodium
    leak; this meets ruling 3 of section 1.
26. Primidone's ten sodium-channel edges move to phenobarbital: primidone's label says its mechanism "is not known",
    the recordings are on phenobarbital (Macdonald and McLean 1986; Schwarz 1979), and phenobarbital's own node carried
    no sodium-channel target.

**Prodrugs and metabolites** (`prodrug_audit_2026-11-19.md`; the build has no `clears` edge, no drug-to-enzyme and no
drug-to-metabolite edge, so no drug's metabolism is represented, which is what the owner suspected):

27. `configs/drug_clearing_enzymes.csv` (44 FDA pharmacogenetic rows) is applied in the next build, carrying out the
    ruling of 11 October 2026 that was never built.
28. Levodopa is seeded on the L-dopa compound node (`MAM02354`, added to `configs/drugs_acting_as_graph_compounds.csv`)
    and its DRD3 `targets` edge is dropped: L-dopa has no intrinsic dopamine-receptor agonism, and the physiological
    route (L-dopa, DDC, dopamine, the receptors) is already built on the compound side and merely unreachable.
29. The seven drug-and-compound duplicates (melatonin, acetaminophen, diazepam, midazolam, cocaine, lithium) and
    pitolisant are each decided on their own case under "related decisions are decided one by one", melatonin first,
    whose compound node already binds the same receptors MTNR1A and MTNR1B. Acetaminophen needs care: its FAAH and
    TRPV1 rows describe the brain metabolite AM404, not the parent.
30. A prodrug whose converting step has no natural graph node (lisdexamfetamine's erythrocyte peptidase, clorazepate's
    gastric decarboxylation) keeps the active species' targets on the parent, with the reason recorded: conversion is
    near-complete before the drug reaches the brain, clorazepate having "essentially no circulating parent".
31. **Open**: the active metabolites with a receptor profile of their own (dextrorphan, tramadol's M1, norquetiapine at
    NET, cariprazine's DDCAR, carbamazepine epoxide), where the choice is the metabolite's targets on the parent row
    against a parent-to-metabolite edge. Either needs the metabolite's measured brain exposure, which is a further
    sourcing step, so the session offered no recommendation and the owner's "all accepted" does not reach it.
32. The 56 audit rows marked "secondary verification pending" get a second external source before any is relied on.

## 17. Rulings of 19 November 2026 on the five research passes and the owner's papers

The owner ruled on the passes that reported through 19 November 2026 (the Table S5 tail, the prodrug follow-ups, the
ion-state round two, the carrier round two, and the reading of the papers the owner supplied). The owner answered each
by code, then "The rest of those lettered suggestions are accepted as-is", and later "P5 accepted", "I5 accepted",
"C19-20 accepted" and, on the Japanese interview forms, "You can keep them as read for c21".

### Prodrugs and the duplicate drug and compound nodes

- **P1. Melatonin's drug node is merged onto its compound node, and the merged node keeps the drug class type.** The
  owner: "Yes but give the melatonin node the drug class type too so that it can be known in the module growing phase
  for the seed to sink requirement." The compound node already binds MTNR1A and MTNR1B, the drug's two targets, and
  carries the clearing enzymes; the agonist sign is preserved.
- **A question of its own, raised in the same message and ruled to be a separate decision.** The owner: "I'm wondering
  if it would be better not to require the module to include a seed since that biases it towards known studied
  targets. They should each contain a sink though", and, asked whether that should be its own decision row, "P1. Yes.
  Separate decision is good". The reason is that a seed is by construction a known drug target, so requiring one
  biases every module toward well-studied proteins, while the sink requirement keeps the constraint that a module
  reaches a symptom-side endpoint. Item 37 is written so that the module-growing phase can drop the seed requirement
  without reopening it.
- **P2. Acetaminophen: AM404 becomes a node of its own, formed from the parent, and takes the FAAH and TRPV1 edges
  with the FAAH sign corrected; the drug and compound nodes are merged only once that branch exists.** The pass
  established from Hogestatt 2005 (PMID 15987694) and Mallet 2010 (PMID 20862299) that those two edges describe the
  brain metabolite and not the parent, and that FAAH makes the active species rather than being inhibited by the
  parent, so the sign as built is wrong. This follows the levodopa ruling.
- **P3. Withdrawn as put, and still open.** The session recommended keeping diazepam, midazolam, lithium and
  pitolisant as two nodes each on the ground that merging "would delete the drug's mechanism"; the owner asked "P3.
  What?" and the session could not justify the claim, since a merge taking the union of both nodes' edges loses
  nothing. What stands: the duplicated edges (lithium's IMPA1, pitolisant's HRH3) are removed with their signs
  preserved. Whether the four pairs merge waits on a reading of what the merge does to edges, which is engineering and
  not research.
- **P4. Cocaine's drug node is missing its principal targets (the dopamine, serotonin and noradrenaline
  transporters), which are curated from two sources by a Fable pass before any merge is ruled on.** The node as built
  carries only a ten-member sodium-channel family target, the artefact pattern the SCN7A check flagged.
- **P5. Primidone keeps one class-level sodium-channel annotation at reduced weight, flagged as a class or
  batrachotoxin-site effect, in place of its ten family-member edges; phenobarbital gets none; PEMA gets none.** The
  owner first pushed back, "I thought primidone worked on sodium channels...", and accepted the revised form, "P5
  accepted". The textbook claim behind primidone's ChEMBL mechanism row (mec 1960) is not disputed; what no source
  supports is a specific Nav subtype, so the ten-member expansion is the family-target artefact again. For
  phenobarbital the evidence points elsewhere: Lingamaneni and Hemmings 2003 (PMID 12538378) place its action at the
  GABA-A picrotoxinin site and name phenytoin and carbamazepine, not phenobarbital, as the sodium-channel
  antagonists, and Schwarz 1979 and Macdonald and McLean 1986 show only non-subtype effects at millimolar
  concentrations. In the build phenobarbital holds 13 GABA-A edges and no sodium-channel edge. No source gives PEMA
  any target.
- **P6. Four audit rows are corrected to their sources**: amphetamine (4-hydroxyamphetamine and norephedrine are
  minor active metabolites, against the audit's "inactive"), brexpiprazole (the label says DM-3411 does not
  contribute therapeutically, which is stronger than "less active"), buprenorphine (norbuprenorphine is potent in
  vitro but limited centrally by P-glycoprotein efflux) and haloperidol (reduced haloperidol's activity is contested,
  Froemming against Kudo).
- **Also recorded, not a ruling**: of the 56 rows marked "secondary verification pending" (section 16 item 32), 54 now
  carry a second independent source. Lithium and pimavanserin rest on an FDA label alone after openFDA, Europe PMC,
  PubMed and the EMA were tried; lithium is not metabolized, so there is no metabolite to cite, and nothing outside
  the label names pimavanserin's AC-279.

### The TPM-to-nCPM conversion: Table S5's upper tail

The cause of the wrong upper tail is established and is an annotation artefact on the bulk side of the paper's own
comparison, not a property of the measurement and not an error in the project's join. GENCODE v40 holds 875
read-through genes, which are second gene records sharing the exons of two neighbours; SPEAQeasy at the commit the
paper names counts genes with featureCounts over the whole annotation, so a read on a shared exon is assigned to
neither record and the paper's bulk count for the real gene is near zero. GTEx's `collapse_annotation.py` excludes
read-through transcripts, so GTEx's TPM for those genes is intact. The effect is a dose: by share of the canonical
transcript lying inside another record, the fraction of genes whose bulk value is more than eight-fold below GTEx
runs 0.1% (none), 1.9% (25 to 50%), 14.4% (50 to 75%) and 66.1% (75 to 100%), and the same split appears in all 13
tissue pairs.

- **T1. The proposed bound on the value is replaced by an annotation rule: a gene whose canonical transcript lies at
  least 50% inside another GENCODE v40 record, or which is pseudoautosomal, is treated as outside Table S5. That is
  292 genes.** A bound would cut long genes that are right and keep wrong genes beneath it, since 73 of 510 islet
  genes between +3 and +5 and 687 at +3 or below are also affected. The threshold is a choice, justified by the
  overlap table above and by the cause being established; flagging genes instead by how far the paper's bulk misses
  GTEx would score the correction against the data it is checked on.
- **T2. A flagged gene takes transcript length alone, as section 16's fallback ruling has it; in islets it takes its
  own measured ratio where that ratio is stable.** Scoring the flag as T1 sets it leaves the overall figures almost
  unchanged (islets 59.3% to 59.6% within two-fold, A46 82.0% to 82.3%) while removing the errors of hundreds to
  thousands of times; the flagged genes themselves go from 14.7% to 39.6% within two-fold in islets.
- **T3. The islet hormone genes.** IAPP, G6PC2, GC and UCN3 are used as measured (ratios 0.165, 0.40, 0.034, 0.050).
  INS, GCG and TTR vary 5- to 9-fold between the three Kang donors, against a median donor sd of 0.23 log2, because
  the authors' per-sample ambient adjustment stripped the hormone in some donors and not others (GCG in alpha nuclei
  4,810 CPM in donor A against 55 in donor B), not because the donors differ in cell mix. A Fable pass looks for the
  unadjusted counts; failing that, the value comes from the donors where the hormone was not stripped, with the donor
  range recorded. PPY rests on two donors, being exactly zero in donor B along with 27 other abundant ambient genes.
- **T4. The same annotation rule applies in brain**, where 45% of the flagged genes are also over-predicted beyond
  ten-fold in A46. The defect is in the table, not in the tissue.

### The ion state of the carrier-share class

- **I1. The PubChem exception's scope**: an HSDB line counts as a source by the work it cites (Merck Index, AHFS,
  Remington, LOGKOW or a paper), not as a source in itself; DrugBank deposits inside PubChem stay unread, under the
  DrugBank ruling; and the scope in code is the "Dissociation Constants" heading of the `/rest/pug_view` service.
  **A correction to `CLAUDE.md` follows from this**: the line written on 19 November 2026 names `/rest/pug` as the
  refused address, which is where the refusal was met, but the measured records are served under `/rest/pug_view`,
  which PubChem's robots file allows for a user-requested read while disallowing `/rest/pug/`. The reader
  (`experiments/read_public_page.py`) does not yet hold `pubchem.ncbi.nlm.nih.gov` in its exempt hosts; the pass
  worked through a wrapper that added it at run time and refused anything but the robots file and that heading.
  Of the 35 drugs with no measured value PubChem answered for two (melatonin, uncharged across the range;
  duloxetine 9.6 in a cosolvent, cationic), and neither changes a class. Febuxostat 3.60 (anionic) came from a Health
  Canada file the predecessor had already saved. 32 of 95 drugs remain unsourced.
- **I2. Where a drug's sourced pKa values disagree, the range is not merely recorded: it becomes bounds on a learned
  parameter, or is propagated through the calculation.** The owner: "The range shouldn't JUST be recorded. It needs to
  be included as either bounds on a learned param or propagated through a calculation". Mianserin is the first case:
  its charged fraction is a learned parameter bounded by its pKa spread (7.1 to 8.4, a fraction of 0.21 to 0.84),
  seeded at the median of its sources (7.75 at 37 degrees C, fraction 0.55).
- **I3. Enalaprilat takes the papers' value (7.84 to 8.02, two groups) over the manufacturer's single 7.6, and is
  classed by charged group, so zwitterionic, not by net charge.** The linkage ruling of section 15 works per charged
  group, and a net-charge label would hide the ammonium. Benazeprilat is treated the same way.
- **I4. Sufentanil takes the direct 35 degrees C value (8.51, charged fraction 0.93) rather than the shifted
  room-temperature median (7.66), under the standing preference for a direct measurement over a corrected one, with
  the oddity recorded: an amine's pKa usually falls as temperature rises and this one is higher.**
- **I5. Structural repairs 1 to 3 are taken and repair 4 is left out.** The owner asked "I5. What are the structural
  repairs?" and, on the answer, "I5 accepted". The four patterns, written before measuring and holding no fitted
  number: (1) a sulfonamide N-H on an aromatic ring with two or more ring heteroatoms is acidic; (2) the C-H at
  position 4 of a pyrazolidine-3,5-dione is acidic; (3) a positive formal charge counts as a permanent cation only if
  no neighbour is negative, which stops an azide being counted as a cation; (4) an aliphatic amine with two different
  weakeners (alpha-carbonyl, beta-oxygen, benzylic or allylic, propargylic) is not counted as protonated. Repairs 1 to
  3 fix sulfadimethoxine, oxyphenbutazone, nelfinavir, nicardipine and ampicillin and move 8 compounds toward MoKa
  and none away; repair 4 breaks naloxone, gains nothing on the 14 drugs the rule had not seen, and moves 18
  compounds toward MoKa and 18 away. Agreement with sourced classes at 37 degrees C rises from 85% to 91% of 74
  drugs, a gain measured partly on the drugs the repairs were written against.
- **I6. A barbiturate pattern, or one for primary heteroaryl sulfonamides, is added only if it is checked on members
  the pattern was not written from.** Otherwise it is fitted to the failures it fixes.
- **I7. Febuxostat's 3.60 enters as a single source**, recorded with the second sources tried.
- **Class changes that follow.** Six of the eleven uncurated drugs change class on a sourced value at pH 7.40 and 37
  degrees C: phenobarbital neutral to anionic (0.62), acetazolamide neutral to anionic (0.72), thiopental anionic to
  neutral (0.48, on the line), ampicillin zwitterionic to anionic (0.24), naloxone neutral to cationic (0.65) and
  enalaprilat anionic to zwitterionic (0.68). Mianserin, articaine, sufentanil, riluzole and triazolam keep their
  class. All eleven are in the label sets only, so no sourced member and no drug awaiting the fallback moves. Through
  the repaired rule, among the 32 still unsourced, azidocillin goes zwitterionic to anionic, sulfamethoxydiazine
  neutral to anionic by analogy with sulfadimethoxine, and rasagiline cationic to neutral, which rests on the rule
  alone. Thiopental sitting on the line and phenobarbital crossing it change nothing, because soft membership (option
  (a), section 15) carries the fraction rather than a class label.

### The carrier share

- **C1. Temazepam's marker is reworded**: the 44% difference in free fraction is a difference between two sampling
  times 90 minutes apart after a meal, which the authors attribute to free fatty acids ("the differences in protein
  binding at the end of the linear phase of the infusions appeared to be related to changes in free fatty acid
  levels, which were higher shortly after breakfast", Br J Clin Pharmacol 1992;33(5):533P, the meeting abstract of
  van Steveninck 1994), with "heparin artefact not excluded" standing until the full text is read. The comparison is
  not matched in time, so infusion rate is confounded with time since the meal, and nothing read says how the samples
  were drawn or assayed. The concern is well founded in kind: Desmond 1980 has heparin raising oxazepam and diazepam
  free fraction by 150 to 250%, Brown 1981 calls the effect "to, a large extent, in vitro artifacts", and Naranjo 1980
  that "small doses of heparin, such as those in heparin locks, can affect drug binding".
- **C2. There is no zwitterion class value.** Each member takes its own measured split, and a zwitterion with no
  measured split goes to sourcing, as receptor ligands do under the section 14 ruling. The session first recommended a
  class median with the spread as its quantile width and withdrew it when the owner's papers were read: of the
  members, only levocetirizine (-0.99) and alvimopan (below -2.7) are well measured, and they lie nearly two orders
  of magnitude apart, which is too thin for a class value. (`y` throughout is log10 of AAG binding over albumin
  binding.)
- **C3. A member resting on one source is accepted, flagged as single source, with the second sources tried listed
  beside the row.**
- **C4. Argatroban enters as a zwitterion member at y = +0.22, flagged single source, with method, pH, temperature
  and protein concentrations unstated.** The owner ruled "C4 and C6. Source them now please". The label sentence
  traces to the FDA pharmacology review of NDA 20,883 (review page 38): "The in vitro binding of argatroban (0.5 uM)
  to albumin (HSA) and alpha 1-acid glycoprotein (alpha 1 -AGP) in human serum were 20.3% and 34.0%, respectively",
  beside total human serum protein binding of 53.7%. The ambiguity the session had held the member out for turns out
  not to matter: both readings of that sentence, separate percentages bound or components of the total, give the same
  ratio of 34.0 to 20.3. That the two sum to 54.3, within rounding of 53.7, favours the components reading. Its pKa
  values are 0.5 (carboxylic acid) and 11.0 (guanidine), so it is a zwitterion at pH 7.40. Every document carrying
  these figures - the FDA label and two reviews, the UK SmPC, the Health Canada monographs, the Japanese package
  insert and interview form - rests on one originator study, Tatsuno et al. 1986, Yakuri to Chiryo 14(S5):1105-1111,
  which has no PubMed record and needs a library request; it is the only route to the method and conditions.
- **C5. The quotations the carrier round two pass took from PMC's page scans are treated as unread.** The PDF of the
  temazepam meeting abstract was behind a check that the visitor is human, and the pass read the page images PMC's
  article page embeds instead, which reaches the text the check guarded; the session's permission classifier refused
  the same route on a second attempt. The two free scans the owner can open are PMC1381443 (the abstract) and
  PMC1430077 (Naranjo 1980). **Also recorded, as a break of the source rules**: that pass sent 16 drug-name lookups
  to PubChem's PUG-REST service with curl before the reader reported that path disallowed, so the robots file was not
  read first; only drug names were sent, and the values it used came from pages the ion-state pass had already saved.
- **C6. Cefotiam and tianeptine are not counted until their pKa is sourced** (both now are: C13 and C19).
- **C7. Fluphenazine records AAG as a carrier with no share.** Kornguth 1981 (Biochem Pharmacol 30:2435, doi
  10.1016/0006-2952(81)90338-5) gives Ka 2.6 x 10^5 per M, so Kd 3.9 micromolar, on purified human AAG by equilibrium
  dialysis at pH 7.4 and 25 degrees C, at one concentration, with albumin measured for imipramine only. Miyoshi 1992
  (Pharm Res 9:845, doi 10.1023/a:1015880327911) is a second, independent laboratory showing fluphenazine and
  perphenazine bind isolated human AAG.
- **C8. Apomorphine keeps both albumin figures with the disagreement stated, and no share is derived from either.**
  Fanali 2010 (IUBMB Life 62:371, doi 10.1002/iub.317) gives Kd 3.0 and 3.2 micromolar on fatty-acid-free human
  albumin at pH 7.2 and 25 degrees C at the warfarin site, which at plasma albumin works out near 99.5% bound (the
  session's arithmetic), against the sponsor poster's 88%. Fanali used defatted albumin and its title reports
  allosteric modulation, so fatty acids in plasma may account for part of the gap; that is the session's reading, not
  the paper's. Covalent binding is noted as a caution.
- **C9. Preskorn's sentence does not name a carrier for sertraline or paroxetine.** The owner asked "C9. What?" and
  "C9 what was the Prescott book again?"; the source is Sheldon Preskorn's book on the SSRIs, section 6, which the
  owner pasted from `preskorn.com/books/ssri_s6.html` on 19 November 2026. Its protein-binding paragraph reads
  "However, SSRIs are weakly bound primarily to a1-acid glycoprotein", and that sentence carries no reference number
  where the paragraph's other claims do, so there is no measurement behind it to check. The owner supplied the chapter's reference
  list on 19 November 2026, and it does not rescue the claim. The list is alphabetical and unnumbered, so 213, 94 and
  199 cannot be resolved by position, and a Fable pass found that none of its ten candidates bearing on plasma
  protein binding names albumin or alpha-1-acid glycoprotein in its abstract, nine of the ten being reviews, which
  could at most repeat the claim. The one original measurement is Aronoff 1984 (PMID 6610522), on fluoxetine alone:
  "The extent of fluoxetine binding to plasma protein was determined by equilibrium dialysis", naming no carrier. The
  list holds no original study of which protein binds sertraline or paroxetine. Every full text is closed, so the
  finding rests on abstracts. Where the paragraph probably comes from, by wording and not by a resolved number: van
  Harten 1993 (PMID 8384945), whose abstract carries the same figures and grouping, "Plasma protein binding of
  fluoxetine, paroxetine and sertraline is > or = 95%; values for fluvoxamine (77%) and citalopram (50%) are much
  lower." **A point against the paragraph, recorded**: it says the highly bound SSRIs "have not been found to increase
  the free fraction of concomitantly administered drugs", while the sponsor's own warfarin study in its reference list
  (PMID 9068934, first author Apseloff, not Wilner as the list has it) reports "a statistically significant (p = 0.02)
  increase in unbound warfarin ... in the sertraline group", judged not clinically relevant. That bears on the
  paragraph's reliability, not on carrier identity.
  **Added 20 November 2026: Warrington 1991 read in full.** The owner supplied it (PMID 1806626, an OCR scan; a Fable pass read it and an Opus check found its quotations verbatim). It names no binding protein for sertraline and never mentions alpha-1-acid glycoprotein: "Sertraline is about 98% bound to plasma proteins" (p. 18), uncited, and albumin appears only as "the main binding protein for these drugs", propranolol and warfarin; Table 1 (p. 12) gives 1.39 to 1.53% unbound after 30 days of administration, uncited, very probably from Ronfeld et al. 1997 (PMID 9068932, abstract only read), the next paper to request. So C9 stands, and "Every full text is closed" above now holds for every work but this one. The sertraline row moves from 0.02 to 0.015 unbound: asked whether it should, the owner answered "for sertraline: sure" (20 November 2026). Table 1's four group means are 1.39 to 1.53% unbound, mean 1.46%, after 30 days of administration, with no method stated, so Ronfeld et al. 1997 stays the primary source to read. The value enters with the carrier-share build, which adds measured values beside the label table; today the only fraction in the repository is the label's, 0.02 from "highly bound to serum proteins (98%)" (configs/drug_label_protein_binding.csv, generated by experiments/read_label_protein_binding.py), and experiments/build_drug_exposure_table.py takes Lombardo et al. 2018 first and the label otherwise. **Added 20 November 2026: Ronfeld et al. 1997 read (on Opus at the owner's request while Fable was at its limit; unconfirmed until a Fable check).** The owner supplied it (PMID 9068932). It is the primary study behind Warrington's Table 1, whose numbers are its day-30 row, so it is not a second, independent source: the volunteers' own plasma dialysed to equilibrium against sodium phosphate buffer, pH 7.4, "at ambient temperature", for 18 hours, with [14C]sertraline added; 11 volunteers per group; percent unbound on day 30 1.39 to 1.53 by group, mean 1.46% (0.0146), and 1.50% on day 1, the elderly lower than the young and women lower than men. So 0.015 stands. Recorded beside it: the measurement is at room temperature, not at 37 degrees C, and no binding protein is named.
- **C10. Nefazodone's carrier search closes as exhausted, after the reading passes finish.** The owner: "C10. Wait
  for all current fable passes to finish reading papers, then yes". Greene and Barbhaiya 1997 (Clin Pharmacokinet
  33:260, doi 10.2165/00003088-199733040-00002), the manufacturer's own review, gives 98.4 to 99.8% bound from data
  on file and names no protein; only an FDA records request remains. The same review gives its metabolites as
  hydroxy-nefazodone 98%, triazoledione 99% and mCPP 66 to 74% bound, all called active, with triazoledione's AUC
  about 2.7 times the parent's; those go to the active-metabolite ruling (A1) and not to a row of their own.
- **C11. McNamara and Meiman 2019 Table 3's six beta-blockers count as one study when a class value is fitted,
  grouped by primary reference.** The transcription is now verified digit for digit against the PDF, so section 16's
  "not yet checked" flag comes off; one laboratory supplies 10 of its 28 drugs.
- **C12. Perphenazine counts Miyoshi 1992 as its second source, for AAG binding only.**
- **C13. Tianeptine leaves the zwitterion class and stays as a single-source row in the anionic class.** Zini 1990
  (Br J Clin Pharmacol 29(1):9-18, PMID 2297464, PMC1380055) gives pKa 4.4 (acidic) and 6.86 (basic), stated without
  method or reference, so it is about 0.78 anion at pH 7.40; by equilibrium dialysis at pH 7.4 and 37 degrees C the
  authors' simulation puts albumin at 93.80% and AAG at 2.00% of drug in plasma, y = -1.67.
- **C14. Melphalan's y of -0.48 is withdrawn.** Gera 1989's "60%" and "20%" are percent bound in protein solutions,
  not shares: ultrafiltration after 10 minutes at 37 degrees C in unbuffered saline, pH not stated, with no
  AAG-alone arm. Read off its Figure 4, albumin alone binds about 43% and albumin with AAG about 60% at therapeutic
  concentrations, which puts y near 0.0 (the pass's arithmetic), and the two proteins explain about a tenth of serum
  binding. The row records "binds both albumin and AAG, no usable share", the figure-derived value is not registered,
  and any class value is fitted without melphalan. About 30% of melphalan in serum is covalently bound, which is not
  carriage, and its amine pKa is still unsourced.
- **C15. Cetirizine and levocetirizine count as one member, taking levocetirizine's y of -0.99, with cetirizine's
  value recorded beside it as a disagreement within one laboratory.** Bree 2002 (Fundam Clin Pharmacol 16(6):471-478,
  PMID 12685505) measured levocetirizine by equilibrium dialysis at pH 7.4 and 37 degrees C on isolated proteins at
  physiological concentrations and in plasma directly, the isolated capacities summing to 10.26 against 10.39 in
  plasma. Pagliara 1998 (J Med Chem 41(6):853-863, PMID 9526560) gives cetirizine's measured pKa as 2.19, 2.93
  (acid) and 8.00 by potentiometry in water at 25 degrees C, so about 0.80 zwitterion and 0.20 anion at pH 7.40 (the
  pass's arithmetic), with binding at pH 7.4 and 37 degrees C of albumin n 2.24, Ka 5.42 per mM and AAG n 1.74, Ka
  5.12 per mM, the authors putting AAG and lipoproteins at "5% or less of total serum binding"; its AAG capacity is
  3.6-fold lower than Bree's for levocetirizine from the same laboratory.
- **C16. Where a paper reports both, the share is taken on albumin with fatty acids, not defatted albumin.** It is
  closer to plasma, and in Bree it is the form that reproduces the plasma result; the choice moves y by 0.4 to 0.7.
- **C17. Every member is rescaled to one stated plasma AAG concentration.** The papers use 18, 20 and 25 micromolar
  and the earlier reports assumed 15, differences reaching 0.2 log units; a Fable pass sources a typical adult value.
- **C18. The search for a fluoroquinolone AAG split stops.** Bergogne-Berezin 2002 (Clin Pharmacokinet
  41(10):741-750, PMID 12162760) says they are "bound predominantly to albumin" with no number and names AAG only for
  macrolides; at 20 to 40% bound the carrier weight is small either way.
- **C19. Cefotiam goes in the anionic class, its dominant form, with the unassigned constant recorded beside it.**
  The NIHS Blue Book, quoting the Pansporin interview form, gives pKa1 2.6, pKa2 4.6 and pKa3 7.0 by alkali
  titration, with no temperature and no assignment of groups; the Halospor form repeats them. If the 7.0 is the
  dimethylamino group (the pass's inference from the structure) cefotiam is about 72% anion and 28% zwitterion at pH
  7.40, and less zwitterion at 37 degrees C, which fits the albumin-only binding Querol-Ferrer 1991 reports better
  than the zwitterion class does.
- **C20. Both pKa sets (argatroban's and cefotiam's) are accepted as single source, flagged, with the second sources
  tried listed.** Pansporin and Halospor are the same Takeda substance, so they are one source; PubChem holds no
  record and PubMed, Europe PMC and Consensus returned none.
- **C21. The Japanese interview forms stand as read, from JAPIC.** The owner's qualm was the document type - "The
  only qualm I have is that it's an interview instead of a paper" - and on the answer that an interview form is a
  manufacturer-written technical dossier in a format set by the Japanese Society of Hospital Pharmacists, companion
  to the package insert and the place such constants are published in Japan, the owner ruled "You can keep them as
  read for c21". Its evidence class is a label's: manufacturer-authored, submitted to a regulator, not peer reviewed,
  and that is recorded beside the values; both forms also name the underlying study. The routing was the second half
  of the question: the agency's own host (PMDA) is robots-disallowed and the pass read JAPIC's copy of the same
  document, treating JAPIC as a separate official publisher rather than a mirror or cache. The owner's ruling keeps
  the values, so that reading stands.

### The NMDA receptor's glycine site (the Matsui rulings)

- **M1, M3 and M4** are recorded in section 16's note on the Matsui pass: GRIN1 takes glycine and D-serine together;
  the potency set and the GluN2 partner are deferred to a Fable pass; and item 4 held no question beyond the glycine
  region ruling, the GRIN1 node taking a forebrain value until region structure exists.
- **M2. The site's occupancy is computed from a receptor-sensed co-agonist level, not from the bulk dialysate value,
  carried as a functional ratio rather than as a concentration.** The owner's "The rest of those lettered suggestions
  are accepted as-is" covers the ruling; the number moved as the papers were read and is recorded under "Still open"
  below. What five papers across two laboratory lines establish: no source puts the synaptic site at saturation.
  Bergeron 1998 (PMID 9861038) has a GlyT1 blocker raising a compound PSC by 50.4 +/- 9.8% (n=18) and, with 10
  micromolar glycine already in the bath, a further 42.5 +/- 10.5% (n=3), concluding that "even during perfusion with
  medium containing glycine at 10 uM, the glycine transport is of sufficient capacity to maintain glycine
  concentration within the proximity of the NMDAR at a subsaturating concentration"; Martina 2004 (PMID 15064326) has
  10 micromolar glycine raising an isolated NMDA EPSC by 34.14 +/- 7.35% (n=7); Le Bail 2015 (PMID 25550512), an
  independent line, has a GlyT1 blocker at +52.6 +/- 10.3% (n=15) and a D-amino-acid-oxidase inhibitor at +135.6 +/-
  35.4% (n=8) on an isolated NMDA field response in adults at 28 to 30 degrees C; Fossat 2012 (PMID 21690263) adds
  the arm the others lacked, exogenous D-serine on the baseline isolated NMDA current in adult prefrontal cortex,
  "125.0 +/- 6.2% of control, n = 17, P = 0.001". Ratios of ambient to raised response (the passes' arithmetic, each
  an upper bound since no manipulation is shown to saturate): prefrontal cortex about 0.80, or nearer 0.76 given the
  paper's own D-serine EC50 of 26.5 micromolar; CA1 0.61 to 0.75 from transporter block; CA1 0.42 from the one
  enzyme inhibitor, unreplicated. **Two corrections to what the session reported earlier**: the "50% enhancement"
  attributed to Martina is Bergeron's figure quoted in Martina's introduction, Martina's own being 34%; and Bergeron
  measured a compound current in which the NMDA part is about a sixth of the signal, so his percentages are not
  fractions of the NMDA response and are not directly comparable with the others.
- **M5. Where the value cannot be sourced elsewhere, it is a learned parameter seeded at the single-laboratory value,
  with the clamp width set by the evidence-prior reliability.** The owner: "If it can't be sourced elsewhere: What do
  you think about using a learned param with that starting value?", and accepted the session's answer that it fits,
  the clamp resting on the evidence prior and sharing a dependency with the open calibrated-regression question.
- **Also established, and reframing M2 rather than answering it.** Papouin 2012 (PMID 22863013) shows that at CA1 in
  adult rat the synaptic NMDA receptors are gated by D-serine and the extrasynaptic ones by glycine: removing
  D-serine cut the field response to "42.4 +/- 4.1%, n=27" at room temperature and "68.6 +/- 4.0%, n=12" at 36
  degrees C, removing glycine left it at "101.3 +/- 3.1%, n=20", while removing glycine cut the extrasynaptic tonic
  current by about half ("12.1 +/- 2.9 vs 26.8 +/- 3.1 pA"). Le Bail 2015 shows the dominant co-agonist differs by
  synapse and age: adult CA1 rests mostly on D-serine, the adult dentate gyrus mostly on glycine, juvenile CA1 on
  glycine alone, and its two removals are not additive (losses summing to 119% at CA1 and 85% at the dentate gyrus),
  so a co-agonist's share cannot be read as a fraction of the response. Papouin shares its senior authors with Fossat
  and Le Bail, so those three are one laboratory line and only two lines exist; no laboratory independent of both has
  applied a saturating D-serine to a baseline synaptic response. Refusals met and not routed around: Le Bail's
  supporting information, which holds the controls behind the 0.42, at PMC (a check that the visitor is human) and at
  the publisher (HTTP 403); Fossat's supplementary figure 2, which holds the dose-response, was not in the PDF
  supplied.

### Active metabolites (section 16 item 31, now ruled)

- **A1. A metabolite with its own measured receptor profile becomes a node of its own, formed from the parent by the
  enzyme that makes it, where both its brain exposure and its potency are sourced; otherwise it is not modelled.**
  This follows the levodopa ruling and P2's AM404 branch. It brings in norfluoxetine, whose half-life of 7 to 15 days
  and potency equal to the parent's are recorded in Preskorn section 6, and nefazodone's triazoledione (C10); by the
  same test desmethylsertraline probably falls below the line, one estimate putting its contribution at 6 to 15% of
  the parent's serotonin-uptake effect. The owner may name a threshold.

## 18. Rulings of 19 November 2026 on the module-growing phase, the drug merge and the active metabolites

- **P1.1. Every endogenous drug perturbation, that is one whose molecule the body makes and the graph already carries
  as a compound, seeds on that compound's own metabolite nodes.** The heading first read "whose molecule is itself a
  graph compound", which is wider than the owner's words and would have drawn in acetaminophen, cocaine, diazepam,
  midazolam, pitolisant and lithium, each of which the body does not make and each of which P2, P3 or P4 already
  holds; corrected in place 20 November 2026 to the quoted wording. The owner: "All endogenous drug perturbations should work that way", generalising the melatonin ruling of
  section 17 (P1). The mechanism exists: `graph/drug_entry_nodes.py` gives such a drug no node of its own, the
  perturbation staying "seeded on the compound's own metabolite nodes" so that "One molecule is then one node whether
  it is made by the body or taken as a drug", and `is_graph_compound` fires only when every seed is already a
  metabolite node of a compound listed in `configs/drugs_acting_as_graph_compounds.csv`. **What it needs**: that file
  holds one row, tryptophan, so the set must be curated. The candidates among the project's 260 drugs are the
  hormones and nutrients given as drugs (the thyroid hormones, hydrocortisone, the sex steroids, folate, cobalamin,
  cholecalciferol), melatonin, and anything else whose molecule already exists as a metabolite node; and melatonin's
  seeds must be re-pointed from its two receptors to its own metabolite nodes, or the guard refuses the merge.
- **P3 is settled by the same reading, and the session's first two answers were both wrong.** The merge is not an edge
  union: in the graph-compound branch no drug node is created and no `targets` edge is written, so edges are dropped,
  which is what the pass said and the session wrongly denied. But the guard makes it harmless: diazepam's and
  midazolam's seeds are GABA-A protein nodes, not their own metabolite nodes, so `is_graph_compound` is false and they
  keep a drug node whatever the configuration says. **Keeping the four pairs apart is already what the code does**,
  and the only change is removing the duplicated edges (lithium's IMPA1, pitolisant's HRH3) with their signs
  preserved.
- **P1.2 and P7. No flag marking a node as a drug is added, and P7 is withdrawn.** The owner asked "is there no
  existing graph framework that can accommodate multiple node types?", accepted a flag as the cheaper answer ("P7
  this sounds like it's a fine option"), then asked "Actually, didn't we decide that the module growing doesn't need
  to know about which things are targets?" and, on the session's check, "I agree p7 should be dropped". **The check**:
  no registered decision and no design document states a seed-to-sink requirement; the phrase occurs in the
  repository only in the owner's own message of 19 November 2026 and in the session's record of it. So the flag had no
  consumer, and the session had taken the requirement from the owner's wording without verifying it existed. The
  design points the other way: `graph/drug_entry_nodes.py` holds that a drug node "holds no identity. It has a type
  and a degree and nothing else, so a held-out drug's node is as informative as a training drug's and no parameter
  belongs to one drug", and `evaluation/target_held_out_split.py` exists, so a readable drug marker would work
  against both and would leak the held-out structure on a target-held-out split. On the framework question: some
  graphs do carry several labels per node, Neo4j's being the usual case, but here `node_type` is what the encoder
  indexes to choose a node's parameters, so a second type would mean either a combined type, which splits parameters
  and leaves less data per type, or a change to that indexing.
- **The module-growing phase excludes entry nodes, by the constant that defines them.** The owner: "make sure that
  the module growing excludes drug nodes", then "Alleles too", then "You can actually use that constant as the
  exclusion rule". So the rule is stated as `node_type in ENTRY_NODE_TYPES`
  (`graph/drug_entry_nodes.py:69`, today `(DRUG_NODE_TYPE, ALLELE_NODE_TYPE)`) rather than as a list of names, and a
  later entry node type is excluded by construction. **State as built**: the module gate is one learnable gate per
  (module, graph node) over every node (`models/noisy_or_pathway_module_model.py:44`), with no node-type filter, so
  drug and allele nodes are eligible for module support today. The mask needed already exists and is already built
  from that constant: `entry_node_mask` in `evaluation/experiment_data.py:673`, described there as "True for a node
  that exists only in the perturbation seeded on it (a drug node)", and the message-passing encoder already takes it.
  The change is to pass it into the module gate and hold those gates at zero.
- **A1's threshold: none, and a metabolite's edges are weighted instead.** The owner: "A1. No cut. Weight edges". So
  a metabolite that clears the sourcing bar of section 17 (A1) enters with its edges weighted by its relative
  occupancy, the metabolite's free brain concentration over its affinity against the parent's, rather than being
  admitted or cut on a line. Desmethylsertraline, estimated at 6 to 15% of the parent's serotonin-uptake effect,
  enters at that weight rather than falling below a threshold. This matches how fractions are carried elsewhere in
  item 37: the charged fraction of a drug whose pKa sources disagree (section 17, I2) and the carrier shares
  (section 15).

## 19. Rulings of 20 November 2026 on the occupancy classes, the endogenous merge and deletion

### The class definition after the ChEMBL check

The harvest finished on 19 November 2026 (ChEMBL_37, release 2026-05-01; 103,196 usable binding Ki values, 39,334
molecules) and **argues against the sibling-subtype centre rather than for it**. Mean error in pK units, sibling
median against the class centre: all families 0.97 against 1.03; muscarinic 0.54 against 1.15; adrenoceptor 0.80
against 0.99; 5-HT 0.87 against 0.98; transporter 0.87 against 0.97; opioid 1.06 against 1.06; histamine 1.13 against
1.48; dopamine 1.25 against 0.98. Three findings matter more than the table: 98.5% of the sibling pairs come from one
paper, and across papers the sibling error is about 0.25 log worse in every family, which is larger than the
advantage itself; 84.5% of molecule-subtype values rest on a single measurement; and 5,676 cells hold only censored
values where an exact sibling value exists, transfer failures the script never sees, all on the failing side.

**Why this does not contradict the earlier 0.4 to 0.6.** The owner asked whether the earlier figure had been measured
before the current release was fetched. It had not: it was never measured on ChEMBL at all, but on the project's own
curated affinities, 4 to 61 values per family, and the subtype-transfer report already records that once copied cells
are removed the project-internal error is 0.67. Restricted to the project's own drugs inside ChEMBL the sibling error
is 0.83, between the two. Muscarinic shows the pattern: project-internal 0.16 on four values, ChEMBL 0.54 on 4,880.

- **The sibling centre is adopted for the muscarinic receptors only**, where the margin survives the within-paper
  inflation; every other family keeps the class centre.
- **Everything sourceable is sourced.** The owner, 20 November 2026, on the proposal to send topiramate's eight AMPA
  and kainate pairs to sourcing: "Not just topiramate. Everything sourcable should be sourced". So a pair whose class
  has fewer than the required measurements goes to sourcing wherever a source can be found, and the learned fallback
  is what remains after sourcing, not an alternative to it.
- **Level 4 applies to the ionotropic glutamate receptors only.** The owner: "then ionotropic glutamate receptors
  only". ChEMBL's level 4 separates exactly AMPA (GRIA1-4), kainate (GRIK1-5) and NMDA (GRIN1, GRIN2A-D, GRIN3A), and
  HGNC's gene groups 1200, 1199 and 1201 give the same three sets gene for gene, so the split the owner ruled for is
  sourced twice. **As a general depth it would do damage**: all 35 aminergic receptors already harvested share one
  level-4 class, "Monoamine receptor", and separate only at level 5, so a general level-4 rule would merge the five
  aminergic families and destroy the muscarinic result above. GABA-A and the sodium channels have no level 4 at all;
  both end at level 3.
- **Genes with no single-protein ChEMBL target stay out of any ChEMBL check, and their pairs go to sourcing.** The
  owner: "Yes". GRIK4, GABRE, GABRG2 and GABRQ exist only inside complex targets, and three of the 40 channel pairs
  sit at these genes. A complex target cannot give a subunit-specific value, and using one would reproduce the
  family-target artefact one level up.
- **SCN7A stays apart from the nine other sodium channels**, pending its own check. The owner: "ok". ChEMBL gives it a
  single-protein target (CHEMBL3585) and classes it as a voltage-gated sodium channel; HGNC puts it in no gene group.
  The disagreement is recorded and the map holds it in a family of its own.
- **A round-2 Ki harvest is on the list and not run.** The owner: "sure. Add it to the list but don't run it yet since
  that's likely a large fable run, right?". Scope when it runs: binding Ki only, not IC50, since the class-statistics
  ruling of section 14 takes the expected quantity type only; AMPA against kainate (exact Ki counts GRIA1-4 74, 99,
  15, 37; GRIK1, 2, 3, 5 168, 119, 31, 34) and the GABA-A alpha subunits (alpha-1 298, alpha-2 105, alpha-3 56,
  alpha-5 474). What it cannot test whatever is done: GRIN2A, 2C, 2D and 3A hold 0 binding Ki, and most sodium
  channels 0 to 15, their ChEMBL data being functional IC50.
- **Curated and ready**: SCRATCH/gene_target_map_round2_2026-11-19.json holds 34 of 38 genes resolved to one human
  single-protein target each, the accession on two independent sources (HGNC and UniProt), the target id on ChEMBL
  alone read three ways. Each of the ten sodium channels has its own single-protein target, so the family artefact
  need not recur there; the two family targets are named as not used.

### The endogenous merge

- **P1.1a. Melatonin's compound-node receptor edges take the agonist sign before the merge.** The owner: "P1.1 a,b
  accepted". The compound node already binds MTNR1A and MTNR1B but at sign 0, so the agonist direction lives only on
  the drug node's `targets` edges and a merge as things stand would convert an agonist into an interaction with no
  direction.
- **P1.1b. Brexanolone and sodium oxybate merge only once their compound nodes carry the receptor edges, sourced.**
  Their compound nodes (MAM01314 and MAM03277) carry no receptor edge at all, so merging now would lose the mechanism
  outright: brexanolone's six GABA-A edges at +0.5 and oxybate's two GABA-B edges at +1 exist only on the drug node.
  Until then they keep their drug nodes, as P2 holds acetaminophen until the AM404 branch exists.
  **This vindicates the objection the session twice got wrong.** The prodrug pass warned that a merge would delete a
  drug's mechanism; the session denied it for diazepam and midazolam, where the guard refuses the merge, and the
  warning turns out to be exactly right for the two drugs the ruling does reach.
- **The set is three drugs, not the dozen the session guessed.** No thyroid hormone, hydrocortisone, sex steroid,
  folate, cobalamin or cholecalciferol is among the 260 admitted drugs, though several match a node in
  `configs/centrally_acting_drugs.csv`. Levodopa is a fourth case, already ruled under item 28, and P1.1 agrees with
  it. Excluded although the molecule is a node, because the body does not make it, and each held by its own ruling:
  acetaminophen (P2), cocaine (P4), diazepam, midazolam, pitolisant (P3) and lithium (P3, where only the ion matches).

### Working rules recorded the same day

- **Deleting files to free disk.** The owner, 20 November 2026: "Only ok to delete the stuff that can be easily
  fetched via script without my intervention". So a file is deleted only when a script can fetch it again
  unattended; anything the owner supplied, anything saved as provenance for a quotation or a licence, and anything
  whose source needs a login, a human check or a library request stays. Acted on the same day: the volume reached 99%
  full with 661 MB free, and the session deleted a byte-identical duplicate of a Reactome mapping file, a BioPAX
  archive already extracted beside its contents, and three Reactome download files in the scratchpad, all re-fetchable
  by script, which freed about 1.1 GB. `data/raw/siletti_cellxgene` (9 GB) and `data/raw/gtex` (1.8 GB) were left
  alone. **This belongs in `CLAUDE.md`** and is on the records list below.
- **P8. Cocaine's ten sodium-channel edges are replaced by one class-level annotation at reduced weight**, as P5 does
  for primidone. They rest on one ChEMBL mechanism row (mec 8842) pointing at the ten-member protein family target
  CHEMBL2331043, the same family as the SCN7A check, with the Numbrino FDA label as its reference, and no source
  names a subtype: the label says "voltage-gated sodium channels" at class level. Unlike primidone, the class-level
  action here is the drug's labelled mechanism, so it is well supported and only its resolution is at fault.
- **Cocaine's three transporter targets are curated** (P4): SLC6A3 0.23, SLC6A4 0.74 and SLC6A2 0.48 micromolar, all
  inhibition so sign -1, each on ChEMBL binding records and Han and Gu 2006 (PMID 16515684, PMC1448202), with GtoPdb
  and Miller 2001 (PMID 11223167) as a third source for the dopamine transporter. **Recorded as an omission, not a
  contradiction**: the FDA label gives cocaine's mechanism as the sodium-channel action alone and is silent on all
  three transporters, so it cannot serve as the second source for them.

## 20. Rulings of 20 November 2026 on the islet hormones, the unbounded fallbacks and the sourcing order

### The islet hormone values (L to P)

A pass of 20 November 2026 found that the published GSE217837 matrix keeps 15 digits of the authors' SoupX
arithmetic, so for any nucleus that retained some of a gene the original whole-number count comes back exactly
(residuals about 1e-12), which is self-validating: nothing but the true integer lands on an integer. For a nucleus
zeroed by the adjustment only an upper bound returns.

- **L. The reconstructed floor stands, recorded as "at least".** The owner: "L accepted". Nuclei CPM over GTEx bulk
  CPM, donor A: GCG 0.055, TTR 0.013, INS 0.033, against published values of 0.046, 0.0088 and 0.019, each of which
  is a floor on the quantity wanted. The four genes already ruled "used as measured" hold up, their reconstructed
  values being 0.98 to 1.24 times the published ones (IAPP 1.10, G6PC2 0.98, GC 1.03, UCN3 1.24).
- **M. The raw reads are not fetched now, and the read is postponed rather than abandoned.** The owner: "M just
  postpone the read though until disk frees or a new session". The five nuclei runs are 31.9 GB in total
  (SRR22266766 to SRR22266770, MD5s in the pass's report), each file over 2 GB, against about 2 GB free on this
  volume. Counting intronic reads separately would be the better measurement, since an intronic read cannot be
  ambient or cytoplasmic.
- **N. INS is recorded as a limit, not a value.** The owner: "N-P accepted". No donor meets the retention criterion
  (at least 90% of a hormone's own-class nuclei in a cluster that kept the gene; control genes score 94 to 100%):
  INS scores 72%, 43% and 6% across donors A, B and C, and donor C lost every INS count in both beta clusters. Donor
  A retains GCG (99%) and TTR (96% at cluster level, though 72% of its alpha nuclei individually lost TTR).
- **O. The donor whose sex contradicts the paper is recorded as an unsettled disagreement.** Table S1 lists all three
  in-vitro donors as male; donor A is female in the data (XIST in 90% of nuclei, Y genes exactly zero). No ratio
  depends on it. The donor mapping itself is sourced from the paper's Additional file 1 Table S2 (snRNA_1/2/3 are
  HP20240, HP20245, HP21189), confirmed by the SRA read counts reproducing that table's mean reads per nucleus; only
  "matrix suffix order equals sample order" remains inferred, GEO's sample table carrying no donor information.
- **P. GitHub access is not widened** to read the authors' code, which would only confirm an adjustment rule the data
  already evidence.
- **The donor split is arithmetic, not biology**, which is why a one-donor value is preferred: whole cells from the
  same three donors agree within 1.2 to 1.5-fold where the nuclei differ 8 to 100-fold, and whole clusters sit at
  exactly zero. Some real pre-adjustment difference probably exists, but not of that size.

### The unbounded fallback parameters (S2)

The owner proposed, and the session's two refinements were accepted ("S2 adjustments accepted"): bounds from sourced
siblings where they exist; a single shared offset for what remains; and a fixed value where even that is not
identified. The refinements:

- **"Fixed" is fixed at the sourced siblings' median**, not at a number chosen for the purpose, so the last branch
  does not reintroduce the unsourced constant that S3 is about.
- **The threshold is a condition, not a count.** A shared offset is one parameter however many pores share it, so the
  count does not change the parameter budget; what it changes is whether the offset is identified. The condition is
  that the offset's standard error is smaller than the spread it is meant to correct; below that it absorbs
  pore-specific noise and the value may as well be fixed. The owner's figure of about ten is the fallback where that
  condition cannot be computed.

### Avoiding circularity when sourcing to constrain (a required step)

The owner, on the order of operations: "Ok. Add that version as a required step eventually". The step: **fix the
held-out split first and permanently, then draw any sourcing sample at random from the training portion only.** That
keeps the randomness where it earns its keep, so easy targets cannot be cherry-picked, and makes overlap impossible
by construction rather than by checking afterwards. The order to avoid is the reverse: sampling at random across
everything and then removing the held-out hits lets the held-out set decide what gets sourced, so it has influenced
the training-time constraints, which is the same leak in a less visible form. Sourced labels for held-out items may be
collected, but never enter any constraint or loss; they are for checking at the end. This is a project-wide rule, not
one for the unbounded pores alone, and is to be recorded as its own decision.

### The sourcing order

**"Everything sourceable is sourced" is batched by family and comes before the damping measurements.** The owner:
"Batching by family makes sense but don't start yet. Just add it to the todo before the damping measurements". Scale,
so the batching has something to go on: about 11 channel pairs go to sourcing at once (topiramate's eight AMPA and
kainate pairs, and the three at the complex-only genes GRIK4, GABRE, GABRG2 and GABRQ), and each of the 206 pairs
with no value gets a sourcing attempt before any fallback applies.

## 21. Rulings of 20 November 2026 on Human-GEM's identifiers, the pH comments and the drug-target screen

### Human-GEM's ChEBI column (Q1 to Q5)

A pass of 20 November 2026 (`human_gem_errors_2026-11-20.md` in the session scratchpad) confirmed that six
metabolites, ten compartment rows, carry the ChEBI id of a deuterated form rather than the compound: diazepam
(CHEBI:194180 diazepam-d8, correct id 49575), cholesterol-STAR (140435 cholesterol-d6), N1-methyl-2-pyridone-5-
carboxamide (145118, correct 27410), tetradecanoylcarnitine (192250, correct 84634), octadecadienoate (137735, correct
30245) and oleoyl ethanolamide (230390, correct 71466). It is an upstream annotation the project copied; Human-GEM
main (2.1.1) still carries four of the six. The owner: "Q1-4 suggestions accepted".

- **Q1. A corrections table applied where `metabolites.tsv` is read**, not an edit of the pinned raw file: the five
  ids above, and a blank for cholesterol-STAR (MAM01511), because giving it CHEBI:16113 would move three HPO
  cholesterol labels from cholesterol (MAM01450) onto cholesterol-STAR.
- **Q2. A guard test** that fails when a `metChEBIID` resolves to an isotopically labelled ChEBI record or is absent
  from the pinned ChEBI release. It would have caught all 23 affected metabolites.
- **Q3. The 17 metabolites whose ids are not in ChEBI 257** (among them cholesterol, coenzyme A, vitamin D3 and
  3-methoxytyramine) take upstream's replacements, each checked individually rather than as a batch.
- **Q4. The duplicate H+ gets a decision of its own**: Human-GEM annotates H+ as "proton" (CHEBI:24636) where Reactome
  uses hydron (CHEBI:15378), so the build carries a second H+ of seven nodes and 90 Reactome edges beside Human-GEM's,
  and second nodes for 3-methoxytyramine (3 edges) and coenzyme A (4 edges).
- **Q5. The two metabolites whose ids name different compounds in different compartments are handed to a Fable
  pass.** The owner: "Q5 I'm unqualified for that. Give to fable and start now". MAM03652 carries palmitoleoyl
  ethanolamide (CHEBI:71465, C16:1) in the extracellular row and palmitoyl ethanolamide (CHEBI:71464, C16:0) in the
  cytosolic row; MAM20077, named a thiamine-diphosphate intermediate, carries CHEBI:29144 (4-carboxy-1-
  hydroxybutylthiamine diphosphate) in the mitochondrial row and CHEBI:83767 (2''-O-acetyl-ADP-D-ribose) in the
  nuclear row, and its recorded structure matches the latter. The pass decides each one on its own physiology, as
  CLAUDE.md requires, and reports whether one id is wrong or two compounds were merged under one id.
- **Q5 ruled on the Fable pass's findings** (`cross_compartment_conflicts_2026-11-20.md`), each case on its own:
  neither is a wrong ChEBI id; in each, one compartment row is filed under the wrong metabolite id. The owner: "Q5
  a-c accepted".
  - **Q5a. MAM03652c is palmitoylethanolamide (C16:0), not the C16:1 compound**, and moves to MAM03885c, named
    "Palmitoylethanolamide". Its formula (C18H37NO2), structure, CHEBI:71464 and KEGG C16512 are all PEA's, and its only
    reaction, MAR20093 (NAAA, RHEA:45064), yields palmitate; UniProt Q02083 and Tsuboi 2005 (PMID 15655246) are the
    second sources. MAM03652e stays the C16:1 compound with CHEBI:71465, and its three ids that are PEA's are corrected
    (HMDB0002100 to HMDB0013648, LMFA08040013 to LMFA08040043, MNXM107548 to MNXM67518). In the build today NAAA's
    substrate is mislabelled and PEA (MAM03885e) has no enzyme.
  - **Q5b. MAM20077 holds two unrelated compounds and is split.** MAM20077m, 2-(4-carboxy-1-hydroxybutyl)thiamine
    diphosphate (CHEBI:29144), the 2-oxoadipate dehydrogenase step of lysine degradation (MAR20173 and MAR04599, OGDH
    or DHTKD1 with DLST), becomes MAM20089m, unused in the pinned files and upstream's own choice. MAM20077n keeps its
    id as O-acetyl-ADP-ribose (CHEBI:83767, MAR20099, MACROD1, MACROD2 or OARD1), with KEGG C22667 corrected to C20658
    and MNXM37367 to MNXM732228. The session's hypothesis of a merge held, but it named the 2-oxoglutarate step, which
    was wrong. In the build the wiring is right but MAM20077m carries O-acetyl-ADP-ribose's structure descriptors,
    because descriptors take the first SMILES per base id.
  - **Both repairs need a species rename where the model is read**, not only a corrections-table row, since node ids
    come from the model file; one node id changes in each case, so the graph version changes. No drug, binder, BRENDA
    or Reactome edge touches the four nodes.
  - **Q5c. A guard test** fails when rows sharing one `metsNoComp` disagree on InChIKey first block or on model name;
    it would have caught both, and sits beside Q2's.
  - **Still open, Q5d**, a decision of its own: NAAA is lysosomal by UniProt and Tsuboi 2005, while Human-GEM puts
    MAR20093 in the cytosol, pinned and upstream alike.
  - **A source-rule exception, granted for this read.** The pass read upstream Human-GEM's issue #1085 and pull request
    #1104 (both cases fixed the same way in v2.1.0) through GitHub's search API after the repository endpoints answered
    403, which is this session's repository scope. The session reported it as routing around a refusal; the owner, 20
    November 2026: "The upstream read is fine". This covers that read and is not recorded as a standing exception.
- **Withdrawn, not a ruling**: a second identifier error reported on 19 November 2026, PubChem 6305 (tryptophan)
  mapped to the lithium ion and oxybate in `pubchem_to_chembl_with_parents.json`, does not exist. The file holds no
  key 6305; the claim came from a pass reading two unrelated lines of its own output as one. The file rebuilds from
  its inputs exactly and 50 of 50 sampled keys matched UniChem.

### The pH comments (S3c)

**Done.** The owner: "S3c yes". The two comments describing `log_ph_activity_width` in
`models/linear_response_encoder.py` called the width "the half-width of a typical enzyme pH-activity curve, and a
learned floor"; it is the pH distance at which activity falls to 1/e (half-width at half-maximum is 0.83 of it), no
learned floor exists, and the seed of 1.0 is not typical of the sourced curves (median 1.47). The docstring of
`graph/compartment_ph.py` still gave the form used before 13 October 2026, exp(-(sensitivity * proton deviation)
** 2), and still claimed a gain-of-function is the exact negative of a loss-of-function, a mirror withdrawn on 13
October 2026 when the log form was adopted. Both are corrected in the working tree, with the earlier form framed as
history with its date. The change is to comments only. It touched a file five study-sheet diagrams depict, so the
session checked each against the doc on 20 November 2026: the doc never calls the width a half-width, names no floor,
and already shows the log form and the broken evenness, so none was wrong, and all five were re-stamped.
**Still open: S3a**, the seed and clamp (the session recommends seed 1.5 and clamp 0.7 to 2.8, the sourced tenth to
ninetieth range), **and S3b**, whether the centring error, an optimum fixed at each compartment's resting pH where
15 of 31 non-lysosomal enzyme classes sit 0.5 or more away from it, becomes a decision of its own.

### The drug-target screen

- **R1. The ChEMBL identifier-cache defect is being fixed now, on Opus.** The owner: "Start the ChEMBL ID cache
  defect fix now. It should be fine for opus". The screen found that the cache under `data/raw/chembl/` holds a salt
  or other non-parent form for about 21 drugs, which ChEMBL answers with nothing when asked as a parent, and that 5
  more sit under a second parent. Nothing yet says what in the project reads through those ids; the repair pass
  traces that and drafts a corrections table and a guard test without applying them.
- **The screen's thin tail is flagged for follow-up.** The owner: "Flag the thin tail for follow up". Of the 570
  missing targets at the affinity line, 356 rest on one document and 262 on one record, so before any of them is
  curated onto a node it needs a second source.
- **Still open: R2** (an affinity line relative to the drug's own tightest carried target, since cocaine's three
  transporters straddle any one absolute line), **R3** (a target that is real binding at reachable concentration is
  carried, weighted by occupancy) **and R4** (a mechanism row on a family target becomes one class-level annotation
  at reduced weight; 130 of 260 drugs have such a row and for 105 every row is of that kind).

## 22. Rulings of 20 November 2026, late batch

- **R2, accepted.** The affinity line for the drug-target screen is relative to each drug's own tightest carried
  target, with a floor; no single absolute line serves both cocaine's transporters and the antipsychotics.
- **R3, accepted.** A target that is real binding at reachable concentration is carried, weighted by occupancy.
- **R4, accepted in principle; its sourcing waits.** A mechanism row on a family target becomes one class-level
  annotation at reduced weight. The weight is to come from a sourced within-family affinity spread, a larger Fable
  sourcing effort that the owner asked to start no earlier than 21 November 2026, when Fable usage resets.
- **Methylphenidate is split into its two enantiomers**, on the escitalopram precedent; the enantiomer-specific values
  (affinities, fraction unbound and the rest) remain to be sourced. A research brief for that sourcing was stopped twice
  by a safety filter on 20 November 2026 and not sent.
- **"Last action read wins" is replaced by flagging for curation.** The owner: "yes, always flag for curation
  instead". A drug-target pair with conflicting ChEMBL action types is withheld and listed until a curated resolution
  row settles it (being built).
- **S3a: the learned pH width is the fallback for enzymes with no sourced curve**, seeded at 1.5 and held between 0.7 and 2.8 (the tenth to ninetieth percentile of 71 BRENDA rows over 25 EC numbers). The owner: "S3a accepted as fallback". Once S3b is built, an enzyme with a sourced curve uses its own optimum and width.
- **S3b is a decision of its own** (enzyme pH optima centred on the compartment's resting pH).
- **P3 is a no-op.** The owner: "P3 then no-op". Pitolisant has no direct HRH3 edge on its compound node, and lithium's two IMPA1 edges leave from different nodes, the drug node and the Li+ compound node, so a lithium perturbation, which enters only at the drug node, reaches IMPA1 once; removing either edge changes no result.
- **Conflicting ChEMBL actions, as built**: on v5 one drug is affected. Varenicline's two edges (CHRNA4, CHRNB2) are withheld until a curated row resolves AGONIST on one molecule against PARTIAL AGONIST on its parent; they are its only edges, so its 116 reports leave the build until then. Eight drugs conflict in all.
- **Varenicline's conflict is resolved as PARTIAL AGONIST**, on both CHRNA4 and CHRNB2; the owner: "accept". A Fable
  pass of 20 November 2026 (`varenicline_action_2026-11-20.md` in the session scratchpad) found the Chantix label
  (section 11), the EMA SmPC (5.1) and two functional studies (Mihalak 2006, PMID 16766716; Rollema 2007, PMID
  17157884; abstracts only) saying partial agonist at α4β2. Disagreements recorded in the row: GtoPdb codes "Agonist",
  and ChEMBL's AGONIST row sits on the tartrate salt and cites a label that no longer resolves. The row is in
  `configs/chembl_action_conflict_resolutions.csv`; measured again the same day, both of varenicline's v5 pairs are
  resolved and no v5 pair is withheld.
- **Q4: the duplicate H+ is merged.** The owner: "i thought they NEEDED to be merged ... no other valid options
  exist". Human-GEM's proton (CHEBI:24636) and Reactome's hydron (CHEBI:15378) become one node per compartment.
- **Q5d is a decision of its own, to be made by a Fable pass** (NAAA's compartment).
- **The steady-state search goes to a decision outside item 37.**
- **S4 goes to a decision outside item 37.** The owner: "s4 is separate decision". S4 is the anchor on the
  module-to-symptom links (`anchored_link_prior_penalty`, written for those links but not wired to them; the model
  config's entry for it, `link_anchor` in `configs/model_noisy_or_pathway_modules.yaml`, disabled with a hand-set
  strength of 0.99, is read by no code; and there is no sourced prior), found by the soft-prior-clamp check the owner
  asked for under M2; it sits on the readout side, which item 37 does not build.
- **Q5d: MAR20093 moves to the lysosome; NAAA's other reactions are decided one by one.** The owner: "Q5d just
  MAR20093: start fable pass now for the other NAAA reactions to each be decided individually". A Fable pass of 20
  November 2026 (`hgem_q5d_2026-11-20.md` in the session scratchpad) found NAAA active only at acid pH (optimum 4.5)
  and lysosomal by two lines (Tsuboi et al. 2005 and 2007, one laboratory, which UniProt restates; Hong et al. 1999,
  another); upstream Human-GEM 2.1.1 keeps the reaction cytosolic. The pinned model has no lysosomal copy of the
  substrate, so the move adds species. MAR20094, MAR20095, MAR20096, MAR20097 and MAR05339 went to a second Fable
  pass the same day.
  After the move, cytosolic palmitoylethanolamide (`MAM03885c`, from Q5a) is in no reaction and the lysosomal copy has
  no supply. The owner, offered a sourced cytosol-to-lysosome transport, removing the cytosolic node, or flagging both:
  "yes, option 1 as long as it passes the check". The transport is added only if a Fable check of its sources passes.
  A source-rule breach on the way: the second pass read Tsuboi et al. 2005 and Ueda et al. 2001 (both J Biol Chem)
  through the Consensus connector after jbc.org's robots file refused the page reader, and Casasampere et al. 2015
  there after Europe PMC answered HTTP 500 (transient, to be retried). Those readings are treated as unread; the owner
  supplied both JBC papers the same day, and a Fable pass checks every claim against them.
- **NAAA's other reactions, each decided on its own; the five verdicts accepted.** The owner: "accept the five NAAA
  verdicts". From the Fable passes of 20 November 2026 (`naaa_other_reactions_2026-11-20.md` and
  `naaa_recheck_2026-11-20.md` in the session scratchpad), rechecked against the two JBC papers the owner supplied
  (36 of 37 quotations verbatim, one corrected, none absent): MAR20094 (C12:0 ethanolamide; one source, 4% of the
  palmitoylethanolamide rate, Tsuboi et al. 2005) and MAR20095 (C14:0 ethanolamide; 27% in Tsuboi et al. 2005, 48% in
  Ueda et al. 2001, one laboratory) move to the lysosome with NAAA kept; MAR20096 (C16 ceramide, whose substrate id
  MAM20076n is a cytosolic row misnamed) and MAR20097 (C12 ceramide) move to the lysosome with the gene rule ASAH1 or
  NAAA, NAAA's ceramide activity being about 0.15% of its palmitoylethanolamide rate; MAR05339, which deacetylates one
  urocanate-cysteine metabolite, loses the NAAA gene and is otherwise unchanged (upstream issue #553; PR #884 removed
  NAAA from its neighbours only). Casasampere et al. 2015's fold values stay unverified (Europe PMC HTTP 500 on five
  spaced retries; its abstract supports NAAA's minor ceramide activity).
- **The palmitoylethanolamide transport passes its check, as a reversible gene-free exchange** MAM03885c <=> MAM03885l:
  Tsuboi et al. 2005, p. 11090, "These results suggested the presence of passive or active transport of NAEs to
  lysosomes", an inference with no mechanism tested, and Petrosino et al. 2015 independently (abstract). A form with a
  gene or one-way fails the check. MAR20093 still carries no flux in the model, having no cytosolic source of the
  substrate and no exit for ethanolamine from the lysosome; the graph's edges are unaffected by that.
- **Pristanic acid takes the (2S,6R,10R) structure, with ChEBI `CHEBI:761004;CHEBI:77268`** on the c, e, r and x rows
  of MAM02766. The owner: "Pristanic acid accept". CHEBI:761004 in ChEBI 257 carries upstream 2.1.1's structure, and
  Ferdinandusse et al. 2002 fix 6R,10R independently; CHEBI:77268 is kept beside it because Rhea names the reaction by
  it and the label mapper reaches "pristanic acid" only through it. No v5 descriptor changes.
- **The 15(R)-HEPE reaction is rewritten as a glutathione-dependent hydroperoxide reduction.** The owner: "15(R)-HEPE
  accept". MAR02560 (c) and MAR02571 (r) become 15(R)-HpEPE + 2 GSH -> 15(R)-HEPE + GSSG + H2O, irreversible, with the
  glutathione peroxidases as genes, after the model's MAR00988; the pinned equation balances in atoms and is off by +2
  in charge. The enzyme assignment for the 15(R) epimer rests on the class reaction and the 15(S) analogue. Upstream is
  unchanged; its open issue #1173 proposes the same for the 15(S) twin. The n and x copies (MAR02567, MAR02577) are
  not drafted, those compartments carrying no GSSG in the model; they are left as pinned and flagged for follow-up
  (the owner: "flagged for follow-up").
- **The seed-requirement decision: the reading of "seed" is confirmed, and the rest is the decision's own.** The
  owner: "1. yes" (a seed is the node a perturbation enters at, not the seed gates of 9.119), and on what a sink is
  and how strict "contain" is: "i guess the real answer is that this is it's own decision and doesn't need answered
  for item 37". The owner's leaning, recorded for that decision: sinks sourced and curated, a node already part of
  another module counted toward it, and "contain" strict.
- **C17: the reference plasma concentrations for the carrier share.** A Fable pass of 19 November 2026
  (`aag_concentration_2026-11-19.md` in the session scratchpad; abstracts only, NHANES computed by the pass) put five
  questions; the owner, 20 November 2026, answered each:
  - **AAG 0.75 g/L, range 0.4 to 1.2 g/L, stated in g/L.** The owner: "use .75 with range .4-1.2". Four independent
    sources agree on about 0.75 g/L (Blain et al. 1985, PMID 4074621, 200 healthy subjects, mean 0.77; Quest's and
    Labcorp's adult reference intervals; NHANES 2015-2018 women 18 to 49 with CRP below 10 mg/L, survey-weighted median
    0.74, 2.5th to 97.5th centile 0.39 to 1.24). Recorded and not settled: two smaller laboratory series and the
    certified reference serum give about 0.5 to 0.6 g/L. g/L is the unit because most binding experiments make up the
    protein by weight, so the assumed molecular mass cancels.
  - **37 kDa where a molar value is shown** (0.75 g/L is then about 20 µM). The owner: "accept". It is the
    mass-spectrometry value of the intact protein; the standard review's 41 to 43 kDa is what the binding papers
    assumed.
  - **A healthy-adult reference**, with the disease multipliers recorded beside it. The owner: "yes, healthy
    reference".
  - **Albumin 42.5 g/L, range 42 to 47 g/L.** The owner: "yes but extend range to 42-47", widening the survey's 42 to
    43 g/L to take in the pooled healthy controls' 44 to 47 g/L; asked whether the centre should move to the middle of
    the range, "keep the starting point at 42.5 w/ extended range".
  - **McNamara's 28 members are not called rescaled**; they are carried as "at the authors' control concentrations,
    unknown" until the primary papers are read. The owner: "accept".
- **The CLAUDE.md drafts are accepted** (the PubChem `/rest/pug_view` scope, the disk-deletion rule, the DrugBank
  wording).
- **MAM00373 and MAM02766 repairs accepted** (`mam00373_2026-11-20.md` in the session scratchpad): the correct
  15(R)-HEPE structure on the c, n, r and x rows with CHEBI:90819, and the name "(2S)-pristanic acid" on MAM02766r.
- **The BiGG-id row of Q5a is kept.**
- **P1.1a happens inside the merge step**, so every endogenous drug is handled by one code path and the build stays
  reproducible.
- **Reading upstream through GitHub's search API.** The owner: "i meant that it's ALWAYS fine to use GitHub's search
  API". The session's own repository scope covers only this project, and adding the Human-GEM repository to the session
  was refused by the session's permission classifier on 20 November 2026; recorded here, not yet in `CLAUDE.md`, until
  the route is settled.

## 23. Three rulings of 19 November 2026, recorded on 20 November 2026

These were answered on 19 November 2026 and missed from the draft until a check on 20 November 2026.

- **M2: seed 0.75, clamp 0.4 to 0.85.** The session's recommendation was "seed 0.75, clamp 0.4 to 0.85" for the
  learned co-agonist occupancy; the owner: "M2 yes". Earlier the same evening the owner asked that the soft-prior
  clamps be used "where appropriate (check the whole project please)".
- **M6: the GRIN1 node is not split.** The session's recommendation was "don't split the GluN1 node; one node for the
  synaptic pool", after a Fable pass found the subunit proxy contested and the graph unable to express either split;
  the owner: "M6. Don't split".
- **S1: clamp widths come from the sourced range**, with the reliability posterior used only for a soft bound; the
  owner: "S1 yes".

## Still open

Rewritten 19 November 2026, after the rulings of section 17.

- **Waiting on the owner.**
  - **P3.** Whether the four duplicate pairs (diazepam, midazolam, lithium, pitolisant) merge. The session's reason
    for keeping them apart did not hold; the answer waits on a reading of what the merge does to edges, which is
    engineering.
  - **M2's number.** The session recommends seeding the learned parameter at 0.75 and clamping it to 0.4 to 0.85,
    that range being the measured spread across the two laboratory lines rather than a guess, with the per-region
    values recorded beside it so the clamp can tighten when region structure arrives. The alternative is to seed at
    the best-evidenced single experiment, Fossat's 0.76 to 0.80 in prefrontal cortex.
  - **M6.** Whether the GRIN1 node is the synaptic pool, the extrasynaptic pool or both pooled, now that Papouin 2012
    has the two gated by different co-agonists at different distances from saturation. The session recommends the
    synaptic pool, since that is the pool the symptom-side signalling runs through, with the extrasynaptic pool
    recorded as nearer saturation and the split added to the exploration queue as a dependency of the deferred node
    structure.
  - **A1's threshold**, if the owner wants one, for how much a metabolite must contribute before it becomes a node.
  - **The seed requirement**, ruled on 19 November 2026 to be a decision of its own (section 17, P1): the row is to
    be drafted, dropping the requirement that a module contain a seed while keeping the sink requirement.
- **Occupancy split.** The sibling-subtype centre, waiting on the ChEMBL harvest (section 14), which stopped early at
  23 of 42 target files and was restarted on 19 November 2026; the 206 pairs with no value, group by group; cocaine's
  missing transporter targets (section 17, P4).
- **Carrier share.** The temperature of every fraction-unbound measurement, and for each one taken away from
  37 °C a 37 °C measurement or the binding enthalpy for a van 't Hoff correction (the owner, 20 November 2026, "yes" to
  sourcing them; queued for Fable; the correction itself to be ruled once the values are in). The plasma AAG concentration every member is rescaled to (section 17, C17); the nefazodone
  closure, which waits only on the reading passes (C10); Tatsuno et al. 1986, the originator study behind every
  argatroban figure, which has no PubMed record and needs a library request, and is the only route to that study's
  method, pH and temperature.
- **Deferred by the owner.** Ambient serotonin (1.4 nM against 52 to 77 nM; the P32/P33 mismatch fixed either way);
  the peptide receptor bands; how the calibrated regression scores a depletion study for a soft bound.
- **Deferred to a decision outside item 37.** The search for several steady states (section 15).
- **Expression.** The unadjusted Kang counts for INS, GCG and TTR (section 17, T3, a Fable pass); GEO's sample table
  for the islet donor mapping.
- **Papers for the owner to supply.** van Steveninck 1994 (doi 10.1038/clpt.1994.67), which settles whether
  temazepam's 44% is physiology or a heparin artefact; Querol-Ferrer 1991 (PMID 1725995), read so far as an abstract
  only; Fossat's supplementary figure 2, which holds the D-serine dose-response and was not in the PDF supplied; Le
  Bail's supporting information, refused at both addresses, which holds the controls behind the 0.42; Preskorn section
  6's reference list, if the page has one (C9). Two Wiley items behind a sign-in the session cannot make: Ferraboschi
  2013 (doi 10.1002/chir.22228) and Rawson 1993 (doi 10.1002/jps.2600820627), either of which would be a second
  source for argatroban's pKa. Henneberger 2010 is the remaining candidate for a D-serine measurement from a third
  laboratory; its identifier is not yet verified.
- **Records.** The 429/503/500/timeout decision row and `CLAUDE.md` line, with PubMed's HTTP 203 gap; the PubChem
  exception's `CLAUDE.md` line, which needs the `/rest/pug_view` correction of section 17 (I1) and the host added to
  `experiments/read_public_page.py` and its test; the JAPIC routing ruling of section 17 (C21) as a `CLAUDE.md` line;
  the three committed Kp,uu values of 9.123; the GENCODE licence row and GTEx recorded as unverified; `docs/data_sources.md`
  row 26 (HPA, 154 to 155 cell types); the ruled sections 4, 7 and 8 written into the record, with the TCDB second
  source of 9.129 (2) and 9.129's carrier clause figures; then registration of item 37.

## Appendix: the addition to 9.129 for section 1, as drafted by a Fable pass on 13 November 2026

**Added 13 November 2026: design question 1 of (4), a reaction whose catalysts span two pore classes, is ruled and not built.** The owner, 13 November 2026, in this order: "why not map to both classes separately with different nodes for each?"; "well embryonic doesn't really matter for the muscle receptor composition, right?"; "i still think it's best to split the nodes"; "but the muscles node could be a sink that gets added as the end part of a module supporting i.e. nicotinic blocking of ganglion preventing downstream depolarization"; and on the session's proposal, "accepted proposal but 9.128 and 9.121 C4 remain unchanged". The proposal: "(i) The classes a reaction can contain are those whose defining subunits can assemble from its catalysts, which replaces the choice by alphabetical gene order. (ii) Where two classes can both assemble, the reaction is split into one node per class, each taking the catalysts that assemble it. (iii) A node for a pore that does not sit on a central neuron is a sink: modules can read it, and it has no edge into `VM_c` or the neuronal ion pools. The muscle-type nicotinic receptor enters this way, as a curated node of the adult composition α1₂β1δε, with CHRNB1 among its catalysts, from two sources. (iv) Decisions 9.121 C4 and 9.128 are unchanged by it." Then "Try sourcing the needed data for the split first" and, asked whether the curated node should be adult-only or CHRNG get a fetal-form node, "Adult only". **Part (iii) was replaced the same day.** The owner: "i guess there's not really a need to include the muscle neuron nodes so it can be excluded, right?"; to the session's rewording, "A pore that does not sit on a central neuron is not added to the graph. The muscle-type nicotinic receptor is not added, and its subunits leave the neuronal entities. Decisions 9.121 C4 and 9.128 are unchanged.", the owner: "accepted". With no curated node, "Adult only" has nothing to apply to. The reason is physiological and not numerical: the graph models a central neuron and this receptor sits on the muscle fibre, which agrees with 9.121 C4's reason ("nothing outside the brain modeled"). Supporting measurements: on `graph_full_neuronal_split_binders_drugs_v5` (files of 12 November 2026) none of the 260 drugs has a `targets` or `sequesters` edge to CHRNA1, CHRNB1, CHRND, CHRNE or CHRNG or to an entity holding them, while nicotine and varenicline reach CHRNA4 and CHRNB2; on the dry-run build above, GTEx brain medians are CHRNA1 0.63 and CHRND 0.20 TPM, below the 1 TPM threshold, CHRNB1 9.18 and CHRNE 2.84. **Sourced** by a Fable pass of 13 November 2026 (`nicotinic_split_sources_2026-11-13.md` in that session's scratchpad; 57 turns, all claude-fable-5-2) on the pinned export `R-HSA-112316.sbml` (Reactome v98, sha256 `9f6c17cf...b66e`). No nicotinic reaction is split under (ii): UniProt P11230 (sha256 `f5e86c02...6b52`) gives the muscle receptor as a "Pentamer of two alpha chains, and one each of the beta, delta, and gamma (in immature muscle) or epsilon (in mature muscle) chains", the Concise Guide 2023/24 (PMC11339754, sha256 `4a0c122a...044b`) as "(α1)2β1δϵ", and CHRNB1 is a member of no entity, so the muscle class assembles from none. CHRND, CHRNE and CHRNG leave RCTE_629590 (catalyst of RCT_622325) and its unbound set RCTE_629576; CHRNA1 leaves RCTE_629600 (RCT_622326), RCTE_629592 (RCT_629595) and their unbound sets RCTE_629586 and RCTE_629581: six entities on the dry-run build. CHRNB1's absence rests on two readings, not independent sources: P11230 is on 0 lines of the export, which covers one pathway, and UniProt's flat file of P11230 (entry version 246 of 04-NOV-2026, sha256 `d4ecec2d...6f9c`) has 161 cross-reference lines and none to Reactome. **Disagreements between sources, not settled**: the 2023/24 Guide as deposited reads "For α1, α3, α4 and β2 and β4 subunits, pairwise combinations" where 2019/20 (PMC6844578) reads "For α2, α3, α4"; UniProt's CHRNA5 entry requires "another alpha subunit" in one comment and "another beta subunit" in the other; no source read states outright that α1 forms no receptor without the muscle partners. **Open**: α7 homomers as a class of their own would make RCT_629595 a two-class reaction; CHRNA9 assembles alone and stays, though Zoli et al. 2018 (PMC6018187) write "Normal brain does not express α9 or α9-α10 mRNAs". The comment block at `mechanistic_pathway_learning/graph/membrane_potential.py` lines 397-407 and the test at `tests/test_mixed_pore_weights.py` lines 144-153 are corrected in the commit that builds this. Checked by the session on 13 November 2026, on Opus, as computation and not research: the 22 saved pages and the export match their hashes, and 38 of the record's 40 quotations are verbatim in them. **None of it is built**: `graph/reactome_import.py` still takes the class of the first catalyst gene in sorted order.
