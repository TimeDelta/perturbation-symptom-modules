<!-- A record: corrected by a dated addition, not by an edit. -->

**Provenance and standing.** Researched on 26 October 2026 against commit 0b976bf by a subagent run on Fable 5.1
(claude-fable-5-1), as CLAUDE.md "Models" requires of research, and brought into the repository on 26 October 2026.
Nothing in it is registered. It changes no rule, no code and no model input; it reports what sourcing says about
which side of an observation time each relation falls on, which is the only way rates enter the Tikhonov partition
of `docs/fixed_point_against_pharmacological_steady_state.md` section 3.4 ("Rates enter only through membership in F
and S").

**Three limits to read it with.**

1. **Seven sources were read through the Consensus search tool and not through PubMed** ([N7], [N8], [N13], [N14],
   [N16], [N21], [N23]); each is marked "Consensus only" where it is used and in section 7. They are not to be
   relied on in a registered document until re-read through PubMed, and section 4 names what to do about each.
2. **The relation counts are v4's.** v5 was not rebuilt for this, and the 26 relations are the v4 audit's
   (`docs/physiology_audit.md`, 17 October 2026, commit 4642a07) plus the three decision-9.86 coupling relations and
   `clears`, which exists only in the `_enzymes` variant.
3. **The slow set it corrects is a proposal, not a registered rule.** `git grep` finds
   `{regulates_transcription_of, encodes}` only in documents, never in code; the masked loop of section 3.4 is a
   sketch that was never built. So section 6 corrects a proposal.

**The finding that matters most** is in section 6: the proposed slow set is defensible only against a roughly
two-hour observation time, and even there transcription straddles. At about six weeks transcription is fast and
`encodes` straddles, which inverts it. A single fixed slow set cannot be right for more than one label class, so the
partition is a function of the observation time rather than a list.

**A claim of section 3.4 that this contradicts**: that the band is "a few hundred nodes, not the graph". That holds
at six weeks and at a year and fails at about two hours, where section 3 here puts the band at thousands of edges
over at least five relations. The acute reading is the one the fast/slow split exists to produce, and it is the one
least entitled to the limit the split rests on.

---

# Relation-level timescale ordering for the fast/slow partition

Written 26 October 2026 (PubMed and Europe PMC reads timestamped 27 October 2026 UTC) against commit 0b976bf, for the
parked exploration item on the Tikhonov partition of `docs/fixed_point_against_pharmacological_steady_state.md`
section 3.4 ("Rates enter only through membership in F and S"). The node-level rate table of that document's section
1.2 and the label onset times of its 1.3 are taken as read and cited as [1.2] and [1.3]; their references keep their
numbers there ([5], [8], [10]-[15], [2], [3]). New sources are [N1] onward and are listed at the end with the sentence
quoted and where it was read.

## 0. What this is and is not

- The partition is of **relations**, not nodes (3.4: a protein node carries a fast activity process and a slow
  abundance process; only a node whose every incoming relation is slow is clamped). So the unit binned here is "the
  process a relation stands for, relaxing at its destination's rate", which is what section 1.4 says one propagation
  step costs in time.
- Three bins against three thresholds: **about 2 h** (acute adverse event, 1 to 2 h after a dose), **about 6 weeks**
  (trial endpoint at 6 to 8 weeks; clozapine agranulocytosis mostly within 3 months and SSRI hyponatraemia at a median
  13 days sit near this column), **about 1 year** (tardive dyskinesia). A germline variant or HPO laboratory label reads
  the full fixed point and needs no partition.
- FAST means the plausible range of the relation's relaxation time lies well below t_obs (an order of magnitude or
  more); SLOW well above; STRADDLES means the range crosses t_obs, or spans so many orders of magnitude within one
  relation that one bin would misstate a non-negligible part of its edges. Where the bulk is clearly one bin and a
  known tail crosses the threshold, both are written ("FAST; tail straddles"), because the per-node treatment the
  partition then needs is confined to the tail, which is cheaper than treating the relation as straddling wholesale.
- Not done, by the brief: no rates as coefficients in the update, no calibrated constants, no code or rule changes.

**The 2 h threshold itself.** Several onset times in 1.3 are fine; one note. The "about 2 h" column is read against the
quetiapine peak at 1 to 2 h [2] and the label's "especially during the initial dose-titration period" [16 of that
document]. Orthostasis at the first doses is partly a first-pass of alpha-1 blockade without adaptation, so the acute
layer is right for it; but the titration period runs days, during which transcription and much of translation have
moved, so "acute" labels that the dataset attaches to the first week are not 2 h labels. The threshold looks right for
the first-dose event and wrong if applied to the whole titration window. Nothing else in 1.3 looked wrong.

## 1. What the current graph holds

`docs/physiology_audit.md` (generated 17 October 2026 at commit 4642a07 on `graph_full_neuronal_split_binders_drugs_v4`)
lists 22 relations with edge counts: activates 69,909; regulates_transcription_of 41,638; binds 31,177; substrate_of
29,250; product_of 28,804; catalyzed_by 24,266; inhibits 19,740; encodes 12,736; member_of 6,767; cofactor_of 2,183;
targets 1,058; changes_membrane_potential 408; changes_ion_pool 395; changes_redox_pool 331; sequesters 101;
regulates_release 89; oxidatively_modifies 41; produces_oxidant 28; redox_capacity 19; voltage_gates 7; driving_force
4; catalyzes_reverse_transport 3. The v5 rebuild adds the three coupling relations of decision 9.86
(`couples_primary`, `couples_secondary`, `g_alpha_regulates_effector`; `build_physiology_graph.py` RELATION_TYPES) and
`clears` exists only in the `_enzymes` variant (23 edge rows, `docs/drug_entry_nodes.md`). The linear-response encoder
derives four more at load time (`depletes_substrate`, `product_opposes`, `cosubstrate_of`, `coproduct_of`;
`linear_response_encoder.py` lines 114 to 131). That is 26 graph relations plus 4 derived, which matches "about 26".
I did not rebuild v5 to count its edges; the counts above are v4's and are reported as such (CLAUDE.md, "a measurement
carries the graph it was taken on").

One repository fact to state plainly: the slow set {regulates_transcription_of, encodes} is **not hard-coded in any
code path**. `git grep` finds it only in documents (`docs/fixed_point_against_pharmacological_steady_state.md` 3.4 and
its sketch `fixed_point_with_slow_processes_frozen`; `docs/steady_state_readout_alternatives.md` 2.4 and 4.5;
`docs/drug_entry_nodes.md` section F). The masked loop is proposed, not built. So what follows corrects a proposal, not
a registered rule.

## 2. The table

Columns: relation | process (source -> destination; what relaxes) | characteristic time, range | bin at ~2 h | ~6 wk |
~1 yr | source. Licences are in the source list (section 7). "Inherits" means the relation is derived by the encoder
from the parent and takes the parent's row.

| relation | process it stands for | characteristic time | ~2 h | ~6 wk | ~1 yr | source |
|---|---|---|---|---|---|---|
| substrate_of | metabolite -> reaction, mass action: the flux answers its substrate within the enzyme's catalytic cycle; a reaction node has no pool of its own | sub-second to seconds (1/kcat; the "average enzyme" has kcat/KM of about 10^5 /s/M) | FAST | FAST | FAST | [N1] |
| product_opposes (derived) | product -> reaction, -1, reversible reactions only | inherits substrate_of | FAST | FAST | FAST | inherits |
| product_of | reaction -> metabolite pool: relaxation = pool / flux (turnover time) | seconds to tens of minutes for most intracellular pools (glutamate about 30 min [1.2]); hours for slow pools (BH4 total half-life 4.4 to 4.6 h [N4]; brain GSH time constant about 13 h [N13, Consensus only]; NAA about 14 h [N13]); months to years for structural lipid (myelin cholesterol [15 of 1.2]) | STRADDLES (hour-scale pools: GSH, NAA, BH4, lipids) | FAST; structural-lipid tail straddles | FAST; myelin-lipid tail straddles | [1.2] [6] [7] [N2] [N4] [N13] |
| depletes_substrate (derived) | reaction -> substrate pool, -1 | inherits product_of | STRADDLES | FAST (tail) | FAST (tail) | inherits |
| cosubstrate_of (derived, carrier) | carrier form -> reaction (supply) | inherits substrate_of; carries REDISTRIBUTION between carrier forms (section 5) | FAST | FAST | FAST | inherits; [N3] |
| coproduct_of (derived, carrier) | reaction -> carrier form | two timescales in one relation (section 5): redistribution between forms is minutes or faster (qBH2 half-life 0.9 to 5 min [N5]; "ultrarapid phase of cofactor equilibrium" [N3]); the TOTAL moves on synthesis/degradation (BH4 total half-life 4.4 to 4.6 h in neuronal culture [N4]) and the name-clause edges include those synthesis edges | STRADDLES | FAST | FAST | [N3] [N4] [N5] |
| catalyzed_by, catalyzes_reverse_transport | enzyme protein -> reaction: flux answers enzyme activity within the catalytic cycle. The enzyme's abundance is the encodes row, not this one | sub-second to seconds | FAST | FAST | FAST | [N1] |
| binds | protein -> protein (OmniPath, unsigned) and cargo -> plasma binder: bound-state occupancy relaxes at koff | protein-ligand koff spans "nearly 10 orders of magnitude" [N6]; protein-protein residence times "typically range from minutes to hours" [N7, Consensus only]; weak transient dimers micromolar [N8, Consensus only] | STRADDLES | FAST | FAST | [N6] [N7] [N8] |
| activates, inhibits | post-translational signalling (OmniPath), metabolite -> enzyme regulation (BRENDA), ligand -> receptor activation node, Ca2+ -> release (Reactome layer) | allosteric and binding effects instantaneous to seconds; kinase cascades within the first minute ("events previously shown to occur in the first minute of mAChR occupation (the mobilization of intracellular Ca2+, activation of protein kinase C)" [N9]); a tail of OmniPath edges mediated by ubiquitination/degradation or trafficking relaxes in tens of minutes to hours (receptor sequestration 17 to 33 min [8 of 1.2]) | FAST; trafficking/degradation tail straddles | FAST | FAST | [N9] [1.2] |
| regulates_transcription_of | TF protein -> transcript level: induction plus mRNA decay | immediate-early genes: increased "within 15 min", 100-fold at 30 to 45 min, "returns to its basal level 2 hr after" [N10]; TF mRNAs half-lives <2 h [10 of 1.2]; genome-wide medians of several hours [11 of 1.2] | **STRADDLES** (IEG and TF transcripts relax within t_obs; typical transcripts do not) | **FAST** | **FAST** | [N10] [10] [11] |
| encodes | transcript -> protein abundance: degradation and resynthesis | brain proteins average lifetime 9.0 d, turnover spanning four orders of magnitude [12 of 1.2]; neuronal half-lives "<1 to >20 days" [13]; non-dividing cells "half-lives ranging from 10 to >1000 h" [N11]; exceptionally long-lived proteins (nucleoporins) "maintained over a cell's life" [N12] | SLOW (bulk); small fast tail of short-lived proteins (Fos protein gone by 4 to 8 h [N14, Consensus only]) | **STRADDLES** (9 d average against 42 d is a factor 5, not an order; >1000 h tail; coherent complex turnover [N11]) | FAST; long-lived-protein tail straddles | [12] [13] [14] [N11] [N12] |
| targets (entry) | drug -> protein: occupancy relaxes at kon*C + koff; the drug's concentration is the forcing (1.1), not this relation | most drugs dissociate faster than they are eliminated ("they have a slower elimination compared with dissociation" [N15]); slow-off drugs minutes to hours (CDK8 inhibitors "from minutes to hours" [N16, Consensus only]); covalent/irreversible inhibitors relax only by resynthesis: brain MAO-B "40 day half-time" after selegiline [N17] | STRADDLES (slow-off and covalent tail) | FAST; covalent tail straddles (40 d ~ 6 wk) | FAST | [N15] [N16] [N17] |
| sequesters (drug entry) | plasma carrier -> free drug, -1: bound/free equilibration | koff 0.67 /s (imipramine) and 1.7 /s (carbamazepine) on albumin [N18]; "the longest experimentally observed average bound time of drug to human albumin was as much as 11 min" [N19] | FAST | FAST | FAST | [N18] [N19] |
| clears (drug entry, `_enzymes` variant) | clearing enzyme -> drug concentration, -1: relaxes on the elimination clock, 3 to 5 half-lives | quetiapine t1/2 about 7 h [2]; SSRIs 21 to 36 h, fluoxetine 1 to 4 d, norfluoxetine 7 to 15 d [3] | SLOW for the study drugs (shortest about 7 h); STRADDLES if a drug with t1/2 near 1 h is in the 222 | FAST, except fluoxetine/norfluoxetine (5 half-lives = 5 to 11 wk) STRADDLES | FAST | [1.1] [2] [3] |
| member_of | subunit protein -> complex entity (decision 4.2 gates by the limiting member) | assembly/disassembly on binds' clock (minutes to hours) and complex abundance on the subunits' encodes clock; "subunits of protein complexes tend to have coherent turnover" [N11] | STRADDLES | STRADDLES (inherits encodes' straddle) | FAST | [N7] [N11]; not sourced on its own |
| cofactor_of | cofactor or metal -> enzyme (BRENDA, manganese extension) | not sourced: loose metal exchange ms to s; tightly bound PLP, heme exchange only with the protein (days) | STRADDLES | FAST | FAST | unsourced (section 4) |
| couples_primary, couples_secondary, g_alpha_regulates_effector | receptor -> G alpha activation; G alpha -> adenylyl cyclase | not sourced here: GTPase cycle sub-second to seconds, cAMP seconds to minutes (textbook) | FAST | FAST | FAST | unsourced (section 4) |
| regulates_release | receptor activation node -> release reaction | not sourced here: autoreceptor feedback seconds; inherits activates | FAST | FAST | FAST | inherits activates |
| changes_membrane_potential, voltage_gates, driving_force | charge flux -> VM_c; VM_c -> gated pores; pool -> Nernst potential (algebraic: relaxation rate effectively infinite, not zero) | milliseconds (textbook, as in 1.2; not sourced) | FAST | FAST | FAST | [1.2] textbook |
| changes_ion_pool | transmembrane ion flux -> neuronal ion pool | extracellular K+: "astrocytes buffer within 6 to 9 seconds more than 80% of the potassium released by neurons" [N20]; clearance processes "take place at the time scale of seconds" [N21, Consensus only]; cytosolic Na+/K+ bulk pools under sustained activity: minutes, not sourced | FAST | FAST | FAST | [N20] [N21] |
| changes_redox_pool, redox_capacity | reactions -> REDOX_GSH / REDOX_NADPH pool nodes; pool -> dependent reactions | GSH node carries both timescales (section 5): reduction of GSSG and consumption are fast; "some glutathione turns over rapidly (t 1/2, approximately 30 min in adults)" [N22]; whole-pool time constant about 13 h in rat brain [N13, Consensus only]; mouse brain half-life 59.5 to 79.1 h [N23, Consensus only]. NADPH node carries redistribution only (its edges are NADP+ <-> NADPH interconversions) | GSH STRADDLES; NADPH FAST | FAST | FAST | [N3] [N13] [N22] [N23] |
| oxidatively_modifies, produces_oxidant | oxidant -> protein activity; enzyme -> oxidant pool | not sourced: oxidant pools ms to s; reversible thiol oxidation reversed in minutes, irreversible modifications only with protein turnover | produces_oxidant FAST; oxidatively_modifies STRADDLES (irreversible tail) | FAST | FAST | unsourced (section 4) |

## 3. The STRADDLES set, by threshold

**At about 2 h (acute labels).** regulates_transcription_of, product_of (and depletes_substrate), coproduct_of, binds,
targets, member_of, cofactor_of, changes_redox_pool (GSH), oxidatively_modifies; activates/inhibits only in their
trafficking and degradation tail. Why each:
- regulates_transcription_of: immediate-early and TF transcripts rise within 15 min and are back at baseline by 2 h
  [N10], so for those genes the 2 h reading is already their fixed point, while the median transcript (half-life of
  hours [11]) has barely moved. One relation, both sides of t_obs. Freezing all 41,638 edges, as the proposal does,
  deletes the IEG response from an acute reading that physiologically contains it.
- product_of / depletes_substrate: the metabolite class is not one rate class ([1.2] already says so); the hour-scale
  pools (GSH, NAA, BH4, structural lipids) sit on or above 2 h while most pools are seconds to minutes.
- coproduct_of: carries redistribution (minutes) and total synthesis (hours) in the same relation (section 5).
- binds: koff over ten orders of magnitude [N6]; protein-protein residence "minutes to hours" [N7] brackets 2 h.
- targets: slow-off and covalent drugs; the occupancy of a covalently inhibited enzyme does not relax at all on this
  clock [N17].
- member_of, cofactor_of: binds-like kinetics plus abundance; unsourced range brackets 2 h.
- changes_redox_pool (GSH): fast pool (30 min [N22]) and whole pool (13 to 60 h [N13] [N23]) on one node.

**At about 6 weeks (trial endpoint; hyponatraemia at 13 d and agranulocytosis within 3 months read nearby).** encodes
(the central one), member_of through it, clears for fluoxetine/norfluoxetine, targets for covalent inhibitors
(MAO-B 40 d [N17] is almost exactly this threshold), product_of for structural lipids. Everything else, transcription
included, is FAST here.

**At about 1 year (tardive dyskinesia).** Only tails: exceptionally long-lived proteins (encodes [N12]) and myelin
lipid (product_of [15]). Every relation's bulk is FAST, which is the full fixed point; what tardive dyskinesia lacks
is the adaptation loop the graph does not hold (3.2), not a partition.

**Consequence for the partition.** The three-bin structure the 3.4 sketch assumes (one slow set, one fast set, a thin
band of a few hundred nodes) holds cleanly at 1 year and roughly at 6 weeks with encodes as the straddler. At 2 h the
band is not a few hundred nodes: it contains the IEG and TF transcripts (thousands of regulates_transcription_of
edges), the hour-scale metabolite pools, and the slow-off drug targets. The epsilon -> 0 limit is honest at 2 h only
if the band is treated per node (assign to the nearer side in log time and record the bound, as 3.4 says), and the
bound will not be small for the IEG transcripts.

## 4. Not sourced, what was tried, what a second source would be

- cofactor_of (metal and cofactor binding kinetics): no search run; the relation mixes Mg2+ (fast exchange) with
  PLP and heme (co-purify with the enzyme). Second source: the koff literature per cofactor class (e.g. PLP Schiff-base
  exchange studies) or BRENDA's own kinetic fields, which hold KM and Ki but not koff.
- couples_primary/secondary, g_alpha_regulates_effector, regulates_release: textbook GPCR/G-protein cycle times;
  not searched. Second source: RGS-accelerated GTP hydrolysis rates (seconds) and cAMP imaging time courses.
- membrane time constant (changes_membrane_potential, voltage_gates): kept as 1.2 has it, "textbook; not sourced".
- oxidatively_modifies / produces_oxidant: not searched. Second source: peroxiredoxin/thioredoxin reduction kinetics
  for the reversible arm.
- Bar-Even et al. [N1]: both PubMed and Europe PMC carry the abstract with "a k(cat) of ~0 s(-1)", a lost digit of
  the paper's "~10 s(-1)". I quote the kcat/KM clause, which is intact, and flag the kcat clause as a transcription
  fault in both indexes; the PubMed HTML page itself returned HTTP 203 through the proxy and was not read.
- Dörrbaum, Price, Fornasiero, Schwanhäusser, Yang: not re-read; cited as 1.2 cites them.
- Consensus-only records ([N7] [N8] [N13] [N14] [N16] [N21] [N23]): abstract read through the Consensus search tool,
  not through PubMed; PMIDs not looked up this session. Each is marked "Consensus only" and should be read through
  PubMed before any of its sentences is relied on in a registered document.
- Nothing hit a robots refusal or a human check. The one failed route (PubMed HTML, HTTP 203) had Europe PMC as its
  second source and that was used.

## 5. Conserved and non-relaxing quantities (the coordinator's refinement)

A conserved moiety has two timescales, on opposite sides of the partition: **redistribution** among its forms is fast
and on that clock the forms obey a weighted sum-to-zero constraint instead of relaxing independently; the **total**
moves only by synthesis and degradation, which is slow. Reich and Sel'kov said exactly this in 1975: "an ultrarapid
phase of cofactor equilibrium can be distinguished from the fast phase of substrate equilibrium", and "the essential
variables at the metabolic time scale are carrier pools and the degree of occupancy of these carriers by metabolic
groups" [N3]. Hatakeyama and Furusawa show the same structure can produce "slow relaxation, with a longer timescale
than that of elementary reactions" through "the feedback based on the moiety conservation" [N24].

Which timescale each carrier relation carries in this graph (read off `cofactor_edges.py` and `redox_pools.py`):
- `cosubstrate_of` (carrier form -> reaction): redistribution only. The source is one form (BH4, THF, ubiquinol,
  PLP, PAPS, aminoacyl-tRNA, 2-oxoglutarate/glutamate in a transamination); its level feeds the consumer's rate.
- `coproduct_of` (reaction -> carrier form): **both**, mixed within one relation. The name clause marks every
  substrate_of/product_of edge of a listed form, including the de novo synthesis edges (SPR -> BH4, DHFR -> THF) and
  the degradation/export edges, so an edge that moves the TOTAL and an edge that moves one FORM (DHPR: qBH2 -> BH4;
  PCBD1) carry the same relation and the same learned gain. The pair clause (PAPS/PAP, aminoacyl-tRNA/tRNA,
  2-OG/glutamate) marks only recurring-pair reactions and so carries redistribution only.
- `changes_redox_pool` into REDOX_GSH: both (glutathione reductase and the hydrolases move forms and import; the
  synthetase and the conjugations/export move the total); into REDOX_NADPH: redistribution only, since its edges are
  the NADP+ <-> NADPH interconversions and the total NADP(H) pool is not represented.
- `sequesters`: redistribution of a conserved total (bound + free drug at fixed total) between plasma carrier and free
  pool, on a sub-second to minutes clock [N18] [N19]; the carrier's own abundance is a separate, slow variable.
- Ion pools: cytosolic and extracellular K+ redistribute in seconds [N20]; the brain's total K+ is set by exchange with
  blood and CSF on a clock not sourced here. The graph carries redistribution only.

**Does the sourcing support the repository's carrier treatment?** Yes on the mechanism and with one correction on the
clock. The treatment says a recycled pool barely moves when one consumer slows (so no depletion edge on carriers) but a
synthesis defect drains it (so the supply edges stay; GCH1 and 13 other slice genes). That is the two-timescale
structure: on the fast clock the total is fixed and a consumer slowing only shifts form occupancy, which the
redistribution edges carry; a synthesis defect lowers the total, which only the synthesis-side edges can carry. The
correction: for BH4 the "slow" total is **hours**, not days. Kapatos measured a BH4 half-life of 4.4 to 4.6 h and
a turnover time of 6.4 to 6.7 h in neuronal cultures, and concluded "The turnover of the cofactor is thus rapid enough
that alterations in its synthesis or degradation could acutely modify the rate of monoamine biosynthesis" [N4]. So the
drainable pool is drained within a day, which supports the GCH1 reading at the 6-week and 1-year thresholds and puts
it in the STRADDLES band at 2 h, not in the slow set. The fast arm is faster than any threshold: qBH2's half-life is
0.9 to 5 min even by autoxidation alone [N5], and enzymatic recycling by DHPR is faster still.

**Non-relaxing quantities and the positive-diagonal hypothesis.** Three cases to record:
1. On the fast layer a conserved total has relaxation rate exactly zero: the forms' deviations sum to zero, so the
   fast subsystem has a zero eigenvalue along the total and I - G_FF is singular in that direction unless the
   constraint is imposed. In this graph that singularity does not appear, because each carrier form is a separate
   node with its own in-degree-normalised row and nothing ties the rows together; the price is that the fast layer can
   raise BH4 and qBH2 together, which the conservation law forbids. That is the "positive diagonal" hypothesis of the
   invariance theorem (2.2) being satisfied by construction while the physiology violates it. A per-moiety
   sum-to-zero projection on the fast layer would be the physiological fix; it is a constraint, not a rate, and it is
   not ruled out by "rates drop out".
2. `driving_force` and the Nernst relation are algebraic (infinite rate, not zero); they sit inside the fast layer at
   every threshold without difficulty.
3. Covalent inhibition under `targets` has relaxation rate zero on every clock shorter than the enzyme's resynthesis
   (MAO-B 40 d [N17]): the occupancy is a non-relaxing state until the encodes clock moves it. This is the one entry
   relation whose "fast" treatment is wrong at 2 h and at 6 weeks.
4. Not conserved but worth noting: the structural lipid pools (myelin cholesterol) relax so slowly that they are
   effectively non-relaxing at every drug label's clock; they belong to the slow set at all three thresholds.

## 6. Where this contradicts the existing partition

1. **{regulates_transcription_of, encodes} is the right slow set only for the 2 h label, and even there transcription
   straddles.** At 6 weeks regulates_transcription_of is FAST (every transcript has relaxed many times over) and
   encodes STRADDLES; at 1 year both are FAST except the long-lived-protein tail. The proposal in 3.4 reads the
   same slow set for "the acute label" only, so it is not wrong as written, but any extension of the masked loop to
   the 6-week stratum must drop transcription from the slow set and treat encodes as a band, not a layer.
2. **At 2 h the IEG transcripts should not be frozen.** The fast tail of regulates_transcription_of (c-fos, c-jun,
   zif/268 and the TF transcripts with half-lives under 2 h) has fully relaxed by t_obs [N10] [10]. Freezing the whole
   relation removes a response that is physiologically present at 2 h. The honest treatment is per gene: a transcript
   half-life table (Schwanhäusser or Yang, both already cited) decides the side.
3. **Relations treated as fast that should not be, at 2 h:** `targets` for slow-off and covalent drugs (the entry
   relation is read as fast by default because occupancy is the sustained input); `binds` for high-affinity
   complexes; `coproduct_of` for the synthesis-side edges; `changes_redox_pool` for the GSH total; `product_of`
   for the hour-scale pools. None of these is wholesale slow, so none goes into the slow set; each needs the band
   treatment.
4. **`clears` is slow at 2 h and straddles 6 weeks for fluoxetine.** Section 3.4's sketch never mentions it, and the
   `_enzymes` variant would put it in the fast layer by default. For the acute reading it belongs in the slow set
   (the drug's concentration at 2 h is set by the dose and absorption, not by clearance equilibrium), which is also
   what 3.4's "input scaled by the exposure at the observation time" already does implicitly.
5. **The band is not "a few hundred nodes" at 2 h.** It holds the IEG/TF transcripts, hour-scale metabolite pools and
   slow-off targets; the count is thousands of edges across at least five relations. The sentence in 3.4 should be
   read as true at 6 weeks and 1 year and false at 2 h.
6. **Nothing here moves the full fixed point** (2.2 and 2.4 of the document stand), and nothing here is a rate
   coefficient. What it changes is membership, which is the one place rates were already said to enter.

## 7. Sources, with the sentence quoted and where it was read

Repository: `docs/fixed_point_against_pharmacological_steady_state.md` at 0b976bf (sections 1.1 to 1.4, 2.2, 3.4 and
its references [2] [3] [5] [8] [10] [11] [12] [13] [14] [15], cited above by those numbers);
`docs/nonlinearity_inventory.md`; `docs/physiology_audit.md` (relation counts, v4, 17 October 2026);
`mechanistic_pathway_learning/models/linear_response_encoder.py` (module docstring; derived relations at lines 114 to
131); `mechanistic_pathway_learning/graph/cofactor_edges.py`, `redox_pools.py`, `reactome_import.py`,
`drug_entry_nodes.py`, `gene_protein_split.py`, `build_physiology_graph.py`.

All abstracts below were read on 27 October 2026 UTC through the session's PubMed MCP server (`get_article_metadata`)
unless marked "Consensus only" (read through the Consensus search tool, abstract as it returned it). Licence fields
were read from the PubMed MCP server's `get_copyright_status` (PubMed/PMC records) and from the Europe PMC REST
service (`www.ebi.ac.uk/europepmc/webservices/rest/search`, `license` field), both on the same date. For an article
with no open licence, the licence is the publisher's copyright and the quotation is a short citation of an abstract;
the PubMed copyright statement is quoted where the record holds one, and "no statement in either record" is written
where it does not.

- [N1] A. Bar-Even et al., "The moderately efficient enzyme: evolutionary and physicochemical trends shaping enzyme
  parameters," Biochemistry 50(21):4402-10, 2011. PMID 21506553, doi:10.1021/bi2002289. Quoted: the "average enzyme"
  exhibits "a k(cat)/K(M) of ~10(5) s(-1) M(-1), much below the diffusion limit". The same abstract reads "a k(cat) of
  ~0 s(-1)" in both PubMed and Europe PMC, a transcription fault (the paper's figure is about 10 /s); not relied on.
  Licence: no open licence (Europe PMC license field empty; no statement in the PubMed record); publisher copyright
  (ACS). Address for the owner: https://doi.org/10.1021/bi2002289
- [N2] I. E. Nikerel et al., "Model reduction and a priori kinetic parameter identifiability analysis using
  metabolome time series for metabolic reaction networks with linlog kinetics," Metab. Eng. 11(1):20-30, 2008. PMID
  18718548, doi:10.1016/j.ymben.2008.07.004. Quoted: "We approximate the time constant of each metabolite pool by
  their turn-over time and classify the pools accordingly into two groups: fast and slow pools." Licence: no open
  licence (Europe PMC field empty; no statement in PubMed record); publisher copyright (Elsevier).
- [N3] J. G. Reich and E. E. Sel'kov, "Time hierarchy, equilibrium and non-equilibrium in metabolic systems,"
  BioSystems 7(1):39-50, 1975. PMID 1156673, doi:10.1016/0303-2647(75)90041-6. Quoted: "The equilibration is fast;
  an ultrarapid phase of cofactor equilibrium can be distinguished from the fast phase of substrate equilibrium" and
  "It can be strictly shown that the essential variables at the metabolic time scale are carrier pools and the degree
  of occupancy of these carriers by metabolic groups." Licence: no open licence (Europe PMC field empty; no statement
  in PubMed record); publisher copyright (Elsevier).
- [N4] G. Kapatos, "Tetrahydrobiopterin synthesis rate and turnover time in neuronal cultures from embryonic rat
  mesencephalon and hypothalamus," J. Neurochem. 55(1):129-36, 1990. PMID 2355214,
  doi:10.1111/j.1471-4159.1990.tb08830.x. Quoted: "BH4 turnover time for MES (6.68 +/- 0.67 h) and HYP (6.40 +/- 0.62
  h) and half-life for MES (4.63 +/- 0.46 h) and HYP (4.44 +/- 0.43 h) did not differ. The turnover of the cofactor
  is thus rapid enough that alterations in its synthesis or degradation could acutely modify the rate of monoamine
  biosynthesis." Licence: no open licence (Europe PMC field empty; no statement in PubMed record); publisher
  copyright (Wiley / ISN).
- [N5] A. Boulghobra et al., "Autoxidation Kinetics of Tetrahydrobiopterin - Giving Quinonoid Dihydrobiopterin the
  Consideration It Deserves," Molecules 28(3):1267, 2023. PMID 36770933, PMC9921404,
  doi:10.3390/molecules28031267. Quoted: "This is mainly due to its short half-life, which goes from 0.9 to 5 min
  according to previous studies." Licence: **CC BY 4.0, verified**: PMC record via the PubMed server's copyright tool,
  "license": "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/", statement "© 2023 by the authors."
- [N6] H. Liu et al., "Public Data Set of Protein-Ligand Dissociation Kinetic Constants for Quantitative
  Structure-Kinetics Relationship Studies," ACS Omega 7(22):18985-96, 2022. PMID 35694511, PMC9178723,
  doi:10.1021/acsomega.2c02156. Quoted: "The entire data set covers 155 types of protein, with their dissociation
  kinetic constants () spanning nearly 10 orders of magnitude." Licence: **CC BY-NC-ND, verified**: Europe PMC
  license field "cc by-nc-nd", isOpenAccess "Y"; PubMed statement "© 2022 The Authors. Published by American Chemical
  Society."
- [N7] G. D'Arrigo et al., "Computational screening of the effects of mutations on protein-protein off-rates and
  dissociation mechanisms by tauRAMD," Commun. Biol. 2024, doi:10.1038/s42003-024-06880-5. **Consensus only.** Quoted
  from the Consensus abstract: "residence times, which typically range from minutes to hours". Licence: the Consensus
  record carries "© 2024. The Author(s)." (Communications Biology is CC BY by default); **not verified** through PMC
  this session. Address: https://doi.org/10.1038/s42003-024-06880-5
- [N8] I. M. A. Nooren and J. M. Thornton, "Structural characterisation and functional significance of transient
  protein-protein interactions," J. Mol. Biol. 2003, doi:10.1016/s0022-2836(02)01281-0. **Consensus only.** Quoted:
  "16 experimentally validated 'weak' transient homodimers, which are known to exist as monomers and dimers at
  physiological concentration, with dissociation constants in the micromolar range". Licence: not verified; publisher
  copyright (Elsevier) presumed.
- [N9] J. Trejo and J. H. Brown, "c-fos and c-jun are induced by muscarinic receptor activation of protein kinase C
  but are differentially regulated by intracellular calcium," J. Biol. Chem. 266(12):7876-82, 1991. PMID 1902229.
  Quoted: "only 1.5 min of agonist stimulation is needed to give maximal increases in c-fos or c-jun mRNA at 30 min"
  and "events previously shown to occur in the first minute of mAChR occupation (the mobilization of intracellular
  Ca2+, activation of protein kinase C)". Licence: no statement in the PubMed record; JBC articles of this era are
  now free to read under ASBMB; **not verified**. Address: https://pubmed.ncbi.nlm.nih.gov/1902229/
- [N10] J. Milbrandt, "Nerve growth factor rapidly induces c-fos mRNA in PC12 rat pheochromocytoma cells," PNAS
  83(13):4789-93, 1986. PMID 3014510, PMC323827, doi:10.1073/pnas.83.13.4789. Quoted: "NGF treatment of PC12 cells
  results in an increased level of c-fos mRNA within 15 min. An approximately 100-fold increase in the level of c-fos
  mRNA occurs 30-45 min after exposure to NGF and the c-fos mRNA concentration returns to its basal level 2 hr after
  NGF treatment." Licence: no open licence (Europe PMC field empty; no statement in PubMed or PMC record); PNAS
  copyright; in PMC as a free back-issue.
- [N11] T. Mathieson et al., "Systematic analysis of protein turnover in primary cells," Nat. Commun. 9:689, 2018.
  PMID 29449567, PMC5814408, doi:10.1038/s41467-018-03106-1. Quoted: "This approach allows exact determination of
  protein half-lives ranging from 10 to >1000 h" and "subunits of protein complexes tend to have coherent turnover".
  Licence: **CC BY 4.0, verified**: PMC record via the copyright tool, "license": "CC BY 4.0", statement "© The
  Author(s) 2018".
- [N12] B. H. Toyama et al., "Identification of long-lived proteins reveals exceptional stability of essential
  cellular structures," Cell 154(5):971-82, 2013. PMID 23993091, PMC3788602, doi:10.1016/j.cell.2013.07.037. Quoted:
  "nuclear pore complexes (NPCs) are maintained over a cell's life through slow but finite exchange of even its most
  stable subcomplexes". Licence: PubMed statement "Copyright © 2013 Elsevier Inc. All rights reserved."; in PMC as an
  author manuscript.
- [N13] I.-Y. Choi and R. Gruetter, "Dynamic or inert metabolism? Turnover of N-acetyl aspartate and glutathione from
  D-[1-13C]glucose in the rat brain in vivo," J. Neurochem. 2004, doi:10.1111/j.1471-4159.2004.02716.x. **Consensus
  only.** Quoted: "The turnover rate of GSH was 0.06 +/- 0.02 micromol/(g h) with a time constant of 13 +/- 2 h" and
  for NAA "time constants 14 +/- 2 and 13 +/- 2 h". Licence: not verified; publisher copyright (Wiley / ISN) presumed.
- [N14] F. R. Sharp et al., "c-fos mRNA, Fos, and Fos-related antigen induction by hypertonic saline and stress,"
  J. Neurosci. 1991, doi:10.1523/jneurosci.11-08-02321.1991. **Consensus only.** Quoted: "Fos protein, detected using
  a specific monoclonal antibody, was maximal at 1-2 hr and disappeared 4-8 hr after HS administration." Licence: not
  verified (J. Neurosci. back issues are free to read; licence not read).
- [N15] G. Dahl and T. Akerud, "Pharmacokinetics and the drug-target residence time concept," Drug Discov. Today
  18(15-16):697-707, 2013. PMID 23500610, doi:10.1016/j.drudis.2013.02.010. Quoted: "prolongation of binding owing to
  a long drug-target residence time can only occur when the binding dissociation is slower than the PK elimination.
  Data for several drugs and/or drug candidates in the literature indicate that the opposite is observed, that is,
  they have a slower elimination compared with dissociation." Licence: PubMed statement "Copyright © 2013 Elsevier
  Ltd. All rights reserved."
- [N16] S. Ziada et al., "Estimation of Drug-Target Residence Time by Targeted Molecular Dynamics Simulations,"
  J. Chem. Inf. Model. 2022, doi:10.1021/acs.jcim.2c00852. **Consensus only.** Quoted: "a dataset of 10 arylpyrazole
  inhibitors of CDK8 ... for which the experimental residence time of the inhibitors ranges from minutes to hours".
  Licence: not verified; publisher copyright (ACS) presumed.
- [N17] J. S. Fowler et al., "Slow recovery of human brain MAO B after L-deprenyl (Selegeline) withdrawal," Synapse
  18(2):86-93, 1994. PMID 7839316, doi:10.1002/syn.890180203. Quoted: "Since enzyme inhibition is irreversible, the
  recovery of functional enzyme activity after withdrawal from L-deprenyl requires the synthesis of new enzyme. We
  have measured a 40 day half-time for brain MAO B synthesis in Parkinson's disease and in normal subjects after
  withdrawal from L-deprenyl." Licence: no open licence (Europe PMC field empty; no statement in PubMed record);
  publisher copyright (Wiley).
- [N18] Z. Tong et al., "Kinetic studies of drug-protein interactions by using peak profiling and high-performance
  affinity chromatography: examination of multi-site interactions of drugs with human serum albumin columns,"
  J. Chromatogr. A 1218(15):2065-71, 2010. PMID 21067755, PMC3065503, doi:10.1016/j.chroma.2010.10.070. Quoted:
  "Dissociation rate constants of 1.7 (±0.2) s(-1) and 0.67 (±0.04) s(-1) at pH 7.4 and 37°C were estimated by this
  approach for HSA in its interactions with carbamazepine and imipramine, respectively." Licence: PubMed statement
  "Copyright © 2010 Elsevier B.V. All rights reserved."; in PMC as an NIH author manuscript.
- [N19] L. M. Berezhkovskiy, "Determination of hepatic clearance with the account of drug-protein binding kinetics,"
  J. Pharm. Sci. 101(10):3936-45, 2012. PMID 22767378, doi:10.1002/jps.23235. Quoted: "Typically, the dissociation of
  drug-protein complex is fast. However, the longest experimentally observed average bound time of drug to human
  albumin was as much as 11 min, whereas the time that a drug molecule spends in blood while passing through the liver
  is around 19 s." Licence: PubMed statement "Copyright © 2012 Wiley Periodicals, Inc."
- [N20] J. Sibille, K. Dao Duc, D. Holcman and N. Rouach, "The neuroglial potassium cycle during neurotransmission:
  role of Kir4.1 channels," PLoS Comput. Biol. 11(3):e1004137, 2015. PMID 25826753, PMC4380507,
  doi:10.1371/journal.pcbi.1004137. Quoted: "we show that astrocytes buffer within 6 to 9 seconds more than 80% of the
  potassium released by neurons in response to basal, repetitive and tetanic stimulations." Licence: **CC BY 4.0,
  verified**: PMC record via the copyright tool, "license": "CC BY 4.0", statement "© 2015 Sibille et al"; Europe PMC
  license field "cc by".
- [N21] G. Halnes et al., "Electrodiffusive Model for Astrocytic and Neuronal Ion Concentration Dynamics," PLoS
  Comput. Biol. 2013, doi:10.1371/journal.pcbi.1003386. **Consensus only.** Quoted: "These processes, that take place
  at the time scale of seconds, demand a mathematical description able to account for the spatiotemporal variations
  in ion concentrations". Licence: PLoS Computational Biology publishes under CC BY; **not verified** on this record
  this session.
- [N22] A. Jain, J. Mårtensson, E. Stole, P. A. Auld and A. Meister, "Glutathione deficiency leads to mitochondrial
  damage in brain," PNAS 88(5):1913-7, 1991. PMID 2000395, PMC51136, doi:10.1073/pnas.88.5.1913. Quoted:
  "Observations on turnover and utilization of brain glutathione in newborn, preweaning, and adult rats show that (i)
  some glutathione turns over rapidly (t 1/2, approximately 30 min in adults, approximately 8 min in newborns), (ii)
  several pools of glutathione probably exist". Licence: no open licence (Europe PMC field empty; no statement in
  PubMed or PMC record); PNAS copyright; in PMC as a free back-issue.
- [N23] M. L. Chang et al., "The effects of oxidative stress on in vivo brain GSH turnover in young and mature mice,"
  Mol. Chem. Neuropathol. 1997, doi:10.1007/bf02815097. **Consensus only** (two PubMed title searches returned no
  record). Quoted: "The half-life of GSH in the 2-mo-old mouse was 59.5 h and in the 8-mo-old mouse was 79.1 h."
  Licence: not verified; publisher copyright (Springer) presumed.
- [N24] T. S. Hatakeyama and C. Furusawa, "Metabolic dynamics restricted by conserved carriers: Jamming and feedback,"
  PLoS Comput. Biol. 13(11):e1005847, 2017. PMID 29112954, PMC5693451, doi:10.1371/journal.pcbi.1005847. Quoted: "The
  CCC can show slow relaxation, with a longer timescale than that of elementary reactions" and "the CCC demonstrates
  robustness against internal fluctuations due to the feedback based on the moiety conservation." Licence: **CC BY
  4.0, verified**: PMC record via the copyright tool, "license": "CC BY 4.0", statement "© 2017 Hatakeyama, Furusawa";
  Europe PMC license field "cc by".

Also read but not quoted in the table: R. A. Copeland, D. L. Pompliano and T. D. Meek, Nat. Rev. Drug Discov.
5(9):730-9, 2006 (PMID 16888652) and Copeland 2015 (PMID 26678621), the residence-time model's statements, whose
abstracts give no numbers; B. N. Kholodenko, Nat. Rev. Mol. Cell Biol. 7(3):165-76, 2006 (PMID 16482094), no timescale
in the abstract; J. M. Dietschy and S. D. Turley, J. Lipid Res. 45(8):1375-97, 2004 (PMID 15254070), no half-life in
the abstract, so [15] of 1.2 stands as the lipid citation.

Pages saved by `experiments/read_public_page.py` this session: one attempt at
https://pubmed.ncbi.nlm.nih.gov/21506553/ (HTTP 203 through the proxy, not read), record in the session scratchpad
directory, not in the repository.

**Added 27 October 2026 (a dated addition to this append-only record).** On 27 October 2026 the owner retired the two
readout records this one builds on (`docs/fixed_point_against_pharmacological_steady_state.md`,
`docs/steady_state_readout_alternatives.md`) as evidence, and then ruled that "ANY numbers from that time are to have
the same treatment", meaning the slice-pilot measurements of 3 to 8 October 2026 (findings 1 to 16 of
`docs/research_summary.md`; decisions 9.103 and 9.104). Checked against this record on that day: it cites none of
those numbers. Its one slice-derived figure, "GCH1 and 13 other slice genes" (section on the carrier treatment), is a
count of genes in the slice's label table, not a measurement of the pilot, and is kept with that description. What it
does build on is the derivations of section 3.4 of the companion record (the Tikhonov partition, "Rates enter only
through membership in F and S"), which the owner's words retire as numbers do not reach; whether the derivations are
retired too is left to the owner in decision 9.104, and until it is answered this record is read as resting on an
unretired derivation and on its own sourcing.
