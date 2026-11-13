# Amendment item 37: the owner's rulings of 13 November 2026, before they are entered in the decision log

A draft, for the owner to act on. It holds the owner's words of 13 November 2026 on the open parts of decision 9.129
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
  raw GHK out of sample. The owner: "yes". Not yet done.

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
brain-expressed, 14 of them drug targets of 87 of the 260 drugs. The cell classes of decision 9.76 hold no
serotonergic neuron class; a Fable pass identifying it and any other missing neuron class was started and stopped at
the model's usage limit, unfinished.

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
  on v5, KCNK1 at 146 TPM among them) receive their GTEx values, built together with section 7's rule.

## Still open

Sections 4 (the calibration of derived Pf), 7 (the cell classes) and 8 (a), (b) and (c); the TCDB second source of
9.129 (2) is answered by section 8's screen and is to be written into the record with it; 9.129's carrier clause
figures; then registration of item 37.

## Appendix: the addition to 9.129 for section 1, as drafted by a Fable pass on 13 November 2026

**Added 13 November 2026: design question 1 of (4), a reaction whose catalysts span two pore classes, is ruled and not built.** The owner, 13 November 2026, in this order: "why not map to both classes separately with different nodes for each?"; "well embryonic doesn't really matter for the muscle receptor composition, right?"; "i still think it's best to split the nodes"; "but the muscles node could be a sink that gets added as the end part of a module supporting i.e. nicotinic blocking of ganglion preventing downstream depolarization"; and on the session's proposal, "accepted proposal but 9.128 and 9.121 C4 remain unchanged". The proposal: "(i) The classes a reaction can contain are those whose defining subunits can assemble from its catalysts, which replaces the choice by alphabetical gene order. (ii) Where two classes can both assemble, the reaction is split into one node per class, each taking the catalysts that assemble it. (iii) A node for a pore that does not sit on a central neuron is a sink: modules can read it, and it has no edge into `VM_c` or the neuronal ion pools. The muscle-type nicotinic receptor enters this way, as a curated node of the adult composition α1₂β1δε, with CHRNB1 among its catalysts, from two sources. (iv) Decisions 9.121 C4 and 9.128 are unchanged by it." Then "Try sourcing the needed data for the split first" and, asked whether the curated node should be adult-only or CHRNG get a fetal-form node, "Adult only". **Part (iii) was replaced the same day.** The owner: "i guess there's not really a need to include the muscle neuron nodes so it can be excluded, right?"; to the session's rewording, "A pore that does not sit on a central neuron is not added to the graph. The muscle-type nicotinic receptor is not added, and its subunits leave the neuronal entities. Decisions 9.121 C4 and 9.128 are unchanged.", the owner: "accepted". With no curated node, "Adult only" has nothing to apply to. The reason is physiological and not numerical: the graph models a central neuron and this receptor sits on the muscle fibre, which agrees with 9.121 C4's reason ("nothing outside the brain modeled"). Supporting measurements: on `graph_full_neuronal_split_binders_drugs_v5` (files of 12 November 2026) none of the 260 drugs has a `targets` or `sequesters` edge to CHRNA1, CHRNB1, CHRND, CHRNE or CHRNG or to an entity holding them, while nicotine and varenicline reach CHRNA4 and CHRNB2; on the dry-run build above, GTEx brain medians are CHRNA1 0.63 and CHRND 0.20 TPM, below the 1 TPM threshold, CHRNB1 9.18 and CHRNE 2.84. **Sourced** by a Fable pass of 13 November 2026 (`nicotinic_split_sources_2026-11-13.md` in that session's scratchpad; 57 turns, all claude-fable-5-2) on the pinned export `R-HSA-112316.sbml` (Reactome v98, sha256 `9f6c17cf...b66e`). No nicotinic reaction is split under (ii): UniProt P11230 (sha256 `f5e86c02...6b52`) gives the muscle receptor as a "Pentamer of two alpha chains, and one each of the beta, delta, and gamma (in immature muscle) or epsilon (in mature muscle) chains", the Concise Guide 2023/24 (PMC11339754, sha256 `4a0c122a...044b`) as "(α1)2β1δϵ", and CHRNB1 is a member of no entity, so the muscle class assembles from none. CHRND, CHRNE and CHRNG leave RCTE_629590 (catalyst of RCT_622325) and its unbound set RCTE_629576; CHRNA1 leaves RCTE_629600 (RCT_622326), RCTE_629592 (RCT_629595) and their unbound sets RCTE_629586 and RCTE_629581: six entities on the dry-run build. CHRNB1's absence rests on two readings, not independent sources: P11230 is on 0 lines of the export, which covers one pathway, and UniProt's flat file of P11230 (entry version 246 of 04-NOV-2026, sha256 `d4ecec2d...6f9c`) has 161 cross-reference lines and none to Reactome. **Disagreements between sources, not settled**: the 2023/24 Guide as deposited reads "For α1, α3, α4 and β2 and β4 subunits, pairwise combinations" where 2019/20 (PMC6844578) reads "For α2, α3, α4"; UniProt's CHRNA5 entry requires "another alpha subunit" in one comment and "another beta subunit" in the other; no source read states outright that α1 forms no receptor without the muscle partners. **Open**: α7 homomers as a class of their own would make RCT_629595 a two-class reaction; CHRNA9 assembles alone and stays, though Zoli et al. 2018 (PMC6018187) write "Normal brain does not express α9 or α9-α10 mRNAs". The comment block at `mechanistic_pathway_learning/graph/membrane_potential.py` lines 397-407 and the test at `tests/test_mixed_pore_weights.py` lines 144-153 are corrected in the commit that builds this. Checked by the session on 13 November 2026, on Opus, as computation and not research: the 22 saved pages and the export match their hashes, and 38 of the record's 40 quotations are verbatim in them. **None of it is built**: `graph/reactome_import.py` still takes the class of the first catalyst gene in sorted order.
