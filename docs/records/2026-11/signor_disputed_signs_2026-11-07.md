# The 16 v5 edges whose stored sign SIGNOR's site rows dispute, read at the papers (7 November 2026)

Committed as a record on 7 November 2026. None of the proposed override rows in section 3 is applied: adopting any first needs the override test generalised (section 0), and each is the owner's decision. Nothing in the graph or `configs/curated_edge_sign_overrides.csv` is changed.

Research pass on **Fable 5.1**, 7 November 2026. Nothing in the repository was edited, committed or pushed. No
override was applied; the rows in section 3 are proposals for the owner.

Graph: v5 (`data/processed/graph_full_neuronal_split_binders_drugs_v5`), as on `main` today. Source of the site
annotations: **SIGNOR 4.0, October 2026 release**, the same file the record of this morning used, re-verified by
hash in this pass (`signor.uniroma2.it/releases/Oct2026_release.txt`, 21,425,930 bytes, SHA-256
`63db6f65e9148e81354f564c3c3cdfc9ee45dc421553bd0926e5fae511ef9d06`, fetched 7 November 2026 01:04 UTC; licence
**CC BY 4.0**, verified in the record of `docs/phosphosite_opposite_effects_2026-11-07.md` section 1). Primary
papers were read from their PubMed records (PubMed MCP) and, where available, Europe PMC full text; every
bibliographic field in section 5 was read from PubMed and confirmed against Europe PMC.

An earlier non-Fable attempt at this task was set aside. Nothing under `discarded_non_fable/` was read; this pass
started from the SIGNOR release and the papers.

## 0. What the override route is, and the one thing it cannot currently do

`configs/curated_edge_sign_overrides.csv` has columns, in this order:

```
source_symbol,target_symbol,relation_type_as_sourced,sign_as_sourced,relation_type_corrected,sign_corrected,source_is_brain_expressed,reason
```

It is loaded by `load_curated_edge_sign_overrides` and applied in `build_signaling_layer`
(`mechanistic_pathway_learning/graph/build_physiology_graph.py`), keyed on the **gene symbol pair as OmniPath
spells it**, after `expand_complex` has split complex rows. An override fires only when the row's
`(relation_type_as_sourced, sign_as_sourced)` equals what `interaction_sign` computes for that OmniPath row; where
it does not, the override is skipped and counted, not applied blind. All 33 existing rows are decision 9.10(a)'s
GRK and arrestin corrections, every one of them `activates,1.0 -> inhibits,-1.0`.

**Three mechanical facts that bear on the rows below**, each checked in this pass:

1. **Two existing tests would fail on these rows.** `tests/test_curated_edge_sign_overrides.py::test_every_curated_override_turns_a_stated_activation_into_an_inhibition` asserts that *every* row is `activates,1.0 -> inhibits,-1.0` **and** that `source_symbol in DESENSITISING_ENZYMES` (the seven GRKs plus ARRB1, ARRB2, ARR3, SAG). None of the four kinases below is a desensitising enzyme, and one row corrects `inhibits -> activates`. So adopting any of these rows requires that test to be generalised first — it currently encodes "this table is only ever for 9.10(a)". That is a decision for the owner, not something to work around, and it is the reason I have proposed rows rather than drafted a patch.
2. **The AURKB histone key is `H3C3`, not `H3C11`.** v5's node is `PROTEIN:H3C11` (display name "H3C11/H3C3", UniProt P68431) and `gene_to_protein` maps both `GENE:H3C11` and `GENE:H3C3` onto it, but the OmniPath row is spelled `AURKB -> H3C3`. A row keyed `AURKB,H3C11` would never match.
3. **Two of the four signed edges come from complex rows**, which matters for `sign_as_sourced`:
   - `CCNA2_CDK2 -> RUNX1` (consensus inhibition, no consensus stimulation) → `inhibits,-1.0`; the plain `CDK2 -> RUNX1` row has both consensus flags set and so yields `binds,0.0`. v5 therefore holds **two** CDK2→RUNX1 protein edges, `inhibits -1.0` and `binds 0.0`.
   - `CSNK2A1_CSNK2B -> TOP2A` (consensus stimulation only) → `activates,1.0`; the plain `CSNK2A1 -> TOP2A` row yields `binds,0.0`. v5 holds both.
   A row whose `sign_as_sourced` names the signed value corrects the complex-derived edge and leaves the `binds`
   edge untouched, which is what is wanted. **But the partner subunit keeps the old sign**: correcting
   `CDK2,RUNX1` leaves `CCNA2 -> RUNX1` at `inhibits`, and correcting `CSNK2A1,TOP2A` leaves `CSNK2B -> TOP2A` at
   `activates`. If the owner adopts these two rows, the partner pairs need their own rows for the graph to be
   internally consistent — the same internal-inconsistency argument that decision 9.10(a) rested on when
   `GRK2->ADRB2` read 0 while `GRK3..GRK7->ADRB2` read +1. I have listed the partner rows separately in section 3
   rather than silently folding them in, because each is its own decision.

`source_is_brain_expressed` below is taken from v5's own `brain_expressed` column on the kinase's gene node, not
asserted from memory: AURKB `False` (brain median 0.157 TPM), CDK2 `True` (3.36), CSNK2A1 `True` (14.36),
PRKACA `True` (65.13).

## 1. How the 16 were identified, and one discrepancy with the record

The record names "16 of the 34 edges" whose stored sign SIGNOR's site rows contradict (6), tie (9) or split (1).
Recomputing from the release by UniProt accession rather than by entity name, I get the **same 16 edges** but a
split of **5 contradict, 10 tie, 1 split**. The one edge that moves is AURKB→H3C11, which has two up-regulating
and two down-regulating rows (a tie by row count) over one up-site and one down-site (a contradiction by site
count). Nothing else differs, and the edge set is identical, so this is a counting convention, not a disagreement
about which edges are in question.

Second difference: the record says 14 of the 16 touch a perturbed gene or drug target; I count **13** (the three
that touch nothing are AURKB→H3C11, AURKB→KIF2C and CDK5→PLD2). Both figures are off the same flag fields; I
report mine and flag the gap rather than reconciling it silently, since the record is committed.

## 2. The per-edge table

"Net effect" is my reading of the primary papers for the kinase's effect on the substrate in a mammalian cell,
preferring a neuron where the evidence allows. "Verdict" is on the **stored v5 sign**.

| # | Kinase → substrate | v5 sign | SIGNOR up-sites | SIGNOR down-sites | Net effect at the papers | Verdict on v5 | Flags |
|---|---|---|---|---|---|---|---|
| 1 | ABL1 → PSMA7 | inhibits | Tyr106 | Tyr153 | **context-dependent**: activity down, abundance up | **leave as is** | K-pert |
| 2 | AURKA → TP53 | inhibits | Ser106, Ser315 | Ser215 | **inhibiting** | **right** | S-pert, S-drug |
| 3 | AURKB → H3C11 | inhibits | Ser11 | Ser29 | **activating** | **wrong** | — |
| 4 | AURKB → KIF2C | activates *and* inhibits | Ser95 | Ser111, Ser192 | **context-dependent** (site-specific localisation; Xenopus) | **leave as is** | — |
| 5 | CDK1 → VHL | inhibits | Ser80 | Ser80 | **inhibiting** | **right** | S-pert |
| 6 | CDK2 → RUNX1 | inhibits | Ser249, Ser266, Ser276, Thr273 | Ser276 | **activating** (activity axis) | **wrong** | S-pert |
| 7 | CDK5 → PLD2 | activates | Ser134 | Ser134 | **activating** | **right** | — |
| 8 | CHEK2 → ELAVL1 | activates | Ser100 | Ser88, Thr118 | **activating** | **right** | K-pert |
| 9 | CSNK2A1 → SNCA | activates | Ser87 | Ser129 | **undecidable** on an activity axis | **hold unsigned** | K-pert, S-pert |
| 10 | CSNK2A1 → TOP2A | activates | Ser1525 | Ser1365 | **inhibiting** | **wrong** | K-pert |
| 11 | MAPK1 → RUNX1 | activates | Ser249, Ser266, Ser276, Thr273 | same four | **activating** (activity axis) | **right** | K-pert, S-pert |
| 12 | PRKACA → ESR1 | activates | Ser305 | Ser236 | **context-dependent** on ligand | **leave as is** | K-pert |
| 13 | PRKACA → MAP2 | activates | Ser1782 | Ser1679, Ser1710, Ser1742 | **inhibiting** | **wrong** | K-pert |
| 14 | PRKACA → NF2 | inhibits | Ser10 | Ser518 | **inhibiting** | **right** | K-pert, S-pert |
| 15 | PRKCD → TNNI3 | inhibits | Ser23, Ser24 | Thr143 | **inhibiting** (tension readout) | **right** | S-pert |
| 16 | PTK2 → ACTN4 | activates | Tyr265 | Tyr31, Tyr4 | **activating** | **right** | S-pert |

### Per-edge evidence, quoted

Every quotation below was read either in the PubMed record (abstract) or in the Europe PMC full text, as stated
for each. SIGNOR's own `SENTENCE` field is quoted only where the point is that SIGNOR's sentence and the paper
disagree.

**1. ABL1 → PSMA7 — v5 `inhibits` — leave as is (context-dependent).** Two papers from one group.
Li et al. 2015 carries the up-site: "the 20S proteasome subunit PSMA7 is subjected to ubiquitination and
proteasomal degradation, which was suppressed by PSMA7 phosphorylation at Y106 mediated by the nonreceptor
tyrosine kinases c-Abl/Arg" and "Downregulated PSMA7 level results in decreased proteasome abundance in
c-Abl/Arg RNAi-knockdown or c-abl/arg-deficient cells" (abstract, PubMed record PMID 25620702, read 7 November
2026). Liu et al. 2006 carries the down-site: "c-Abl and Arg (abl-related gene) tyrosine kinases associate with
and phosphorylate the proteasome PSMA7 (alpha4) subunit at Tyr-153. Consequently, proteasome-dependent
proteolysis is compromised" (abstract, PubMed record PMID 16678104, read 7 November 2026). These are two axes,
not a contradiction: Tyr153 **lowers proteasome activity**, Tyr106 **raises PSMA7 abundance**. The project reads
a sign as the effect on the destination's activity, which is Tyr153's direction, so `inhibits` is defensible and
I do not propose a change. The record should note that abundance runs the other way.

**2. AURKA → TP53 — v5 `inhibits` — right. SIGNOR's contradiction is an artefact of a secondary citation.**
This is the clearest curation error in the sixteen. SIGNOR's up-regulating Ser315 row cites **Slee and Lu 2013**
(PMID 24173284), which is a mouse knock-in study of Ser312 and mentions Aurora-A only in passing, naming the
primary paper itself: "The interaction between p53 and E2F1 is enhanced by phosphorylation of p53 on Ser315, a
residue within the E2F1 binding region that is phosphorylated by cell cycle kinases such as cdk1, cdk2, cdk9 and
Aurora kinase A" (Europe PMC full text, PMC3813944, read 7 November 2026) — and its own reference list carries
the title "Phosphorylation by aurora kinase A induces Mdm2-mediated destabilization and inhibition of p53".
Reading that primary paper, **Katayama et al. 2004** (PMID 14702041, found by PubMed search and read in its
PubMed record, 7 November 2026): "we show that aurora kinase A phosphorylates p53 at Ser315, leading to its
ubiquitination by Mdm2 and proteolysis" and "Silencing of aurora kinase A results in less phosphorylation of p53
at Ser315, greater stability of p53 and cell-cycle arrest at G2-M". **Ser315 is inhibiting, not activating.**
The other two sites: Liu et al. 2004, "the phosphorylation of p53 by Aurora-A at Ser-215 abrogates p53 DNA
binding and transactivation activity" (abstract, PMID 15469940); Hsueh et al. 2013, "Ser-106 phosphorylation of
p53 decreases its interaction with MDM2 and prolongs the half-life of p53" (abstract, PMID 23201157). So two of
three sites inhibit, including the dominant destabilising one, and v5's `inhibits` is correct. **No override.**

**3. AURKB → H3C11 — v5 `inhibits` — WRONG, should be `activates`.** The up-site is uncontroversial: histone H3
Ser11 (H3S10ph) phosphorylation by Aurora B drives mitotic chromosome condensation (SIGNOR cites PMIDs 12588998
and 14583461). The two **down-regulating Ser29 rows cite papers that say the opposite or say nothing of the
kind.** Lau and Cheung 2011 is titled "Histone code pathway involving H3 S28 phosphorylation and K27 acetylation
**activates** transcription and antagonizes polycomb silencing" and its abstract reads: "we discovered a
mechanism whereby H3 S28 phosphorylation not only displaces binding of the polycomb-repressive complexes, but it
also induces a methyl-acetylation switch of the adjacent K27 residue" (abstract, PMID 21282660, read 7 November
2026). Goto et al. 2002: "With regard to mitotic chromosome condensation, Aurora-B directly phosphorylated H3,
not only at Ser10 but also at Ser28" (abstract, PMID 11856369) — a condensation finding, with no down-regulation
claim anywhere in it. **Neither cited paper supports "down-regulates activity".** Both of Aurora B's annotated
sites on H3 are, by their own sources, activating. **Override proposed** (section 3, row A), keyed `AURKB,H3C3`.

*Adjacent observation, outside the sixteen.* The same mis-signing affects **RPS6KA5 → H3-3A**, which the record
classes as agreeing with v5 because its down rows outnumber its up rows (v5 `inhibits`; 4 down rows, 1 up). But
Lau and Cheung 2011 is the primary MSK1 paper, and it states: "the H3 kinase MSK1 is a direct and potent
transcriptional activator. Targeting of this H3 kinase to the endogenous c-fos promoter is sufficient to activate
its expression without the need of upstream signaling" (abstract, PMID 21282660). SIGNOR's own
`RPS6KA5 -> H3-3A down-regulates activity Ser29` row cites that very paper (SIGNOR-178708, PMID 18508628) while
three further down rows at Ser11 cite others. So v5's `inhibits` for RPS6KA5→H3-3A is likely wrong too, by the
same reading. It is **not** one of the sixteen and I did not work it up; I flag it because a decision on
AURKB→H3C11 that ignored it would leave the graph treating one H3 kinase's activating phosphorylation as
positive and another's as negative. Each should be decided on its own case.

**4. AURKB → KIF2C — v5 holds both signs — leave as is (context-dependent).** All three rows cite one paper,
Zhang et al. 2007: "MCAK association with chromosome arms is promoted by phosphorylation of T95 on MCAK, whereas
phosphorylation of S196 on MCAK promotes dissociation from the arms. Although targeting of MCAK to centromeres
requires phosphorylation of S110 on MCAK, dephosphorylation of T95 on MCAK increases the binding of MCAK to
centromeres", and "Our study reveals a new role for Aurora B, which is to prevent excess MCAK binding to
chromatin to facilitate chromatin-nucleated spindle assembly" (abstract, PMID 17567953, read 7 November 2026).
Three reasons not to override. The readout is **localisation, not catalytic activity**. The work is in **Xenopus
laevis** egg extract and oocytes (the MeSH terms are "Xenopus laevis", "Xenopus Proteins", "Ovum"), so it is not
a mammalian cell, let alone a neuron, and the residue numbers differ between the paper (T95/S110/S196) and
SIGNOR's human mapping (Ser95/Ser111/Ser192). And v5 already holds both signs, which is a fair encoding of a
genuinely two-directional, site-specific mechanism. **Candidate for `unsigned` if that state is ever built**, but
not for an override on this evidence.

**5. CDK1 → VHL — v5 `inhibits` — right.** Both rows cite one paper, Chen et al. 2023, read in **full text**
(Europe PMC, PMC10070344, CC BY, read 7 November 2026). It is unambiguous: "CDK1 directly phosphorylates pVHL at
Ser80, which primes the recognition of pVHL by PIN1. PIN1 then binds to phosphorylated pVHL and facilitates the
recruitment of the E3 ligase WSB1, therefore targeting pVHL for ubiquitination and degradation" (abstract), and
in the body, as a results heading, "The phosphorylation of pVHL at Ser80 promotes its ubiquitination and
degradation", with "Together, these results indicate that the phosphorylation of pVHL at Ser80 is pivotal to
promote tumor progression through destabilizing pVHL". SIGNOR's `up-regulates activity` row at the **same
residue** (SIGNOR-280207) quotes the same sentence about PIN1 priming and reads it as activation; the paper says
degradation. This is a plain curation conflict, not a site-level opposition. v5's `inhibits` is correct.
**No override.**

**6. CDK2 → RUNX1 — v5 `inhibits` — WRONG on the activity axis, should be `activates`.** Two papers from one
group, and they measure two different things. Biggs et al. 2005 (the up-sites): "Mutation of the four
phosphorylation sites necessary for transcriptional regulation (serine 276, serine 293, serine 303, and
threonine 300) mimics the effects of the proteasome inhibitor, increasing the levels of ubiquitinated,
matrix-bound AML1c" and, decisively, "Thus, phosphorylation of AML1c on specific serine/threonine residues
controls **both transcriptional activity and rate of degradation**" (abstract, PMID 16046550, read 7 November
2026). SIGNOR's sentence for these rows quotes the paper's own statement that "mutation of these four sites
(serine 276, serine 293, serine 303, and threonine 300) to alanine abolishes transcriptional activation, whereas
mutation of these sites to aspartic acid (which mimics phosphorylation) results in a hyperactive protein" — i.e.
phosphorylation **raises** RUNX1 transcriptional activity. Biggs et al. 2006 (the down-site) measures stability:
"Mutant AML1 protein which cannot be phosphorylated at these sites (AML1-4A) is more stable than wild-type AML1"
(abstract, PMID 17015473). So phosphorylation raises activity and raises turnover. On the **activity** axis,
which is the axis the project's sign is defined on, CDK2 is **activating**.

The consistency argument is strong here and is the same one 9.10(a) turned on: v5 already stores **`activates`
for CDK1→RUNX1 and for MAPK1→RUNX1**, on the identical evidence base (CDK1→RUNX1 draws on the same Biggs 2005
and 2006 papers). The graph currently has three kinases phosphorylating the same four residues of the same
substrate and reads one of them with the opposite sign. **Override proposed** (section 3, row B), with the
`CCNA2,RUNX1` partner row as a separate decision.

**7. CDK5 → PLD2 — v5 `activates` — right.** One paper, Lee et al. 2008: "we suggest that the phosphorylation
and activation of PLD2 by cyclin-dependent kinase 5 (Cdk5) is critical for EGF-dependent insulin secretion" and
"PLD2-S134A did not show EGF-dependent phosphorylation and activation by Cdk5" (abstract, PMID 18625302, read
7 November 2026). SIGNOR's `down-regulates activity` row at the same residue (SIGNOR-276168) quotes the very
sentence containing the word "activation" and signs it negative. The paper says activation; v5 agrees.
**No override.** (Note: this is one of the record's named curation conflicts, "CDK5 to PLD2 Ser134", and it
resolves cleanly in v5's favour.)

**8. CHEK2 → ELAVL1 — v5 `activates` — right.** One paper, Yu et al. 2011, read in **full text** (Europe PMC,
PMC3201881, CC BY-NC, read 7 November 2026). The site-level sentence SIGNOR relies on is real: "phosphorylation
at residue S100 by Chk2 enhances HuR-binding to the occludin mRNA, while phosphorylation at S88 and T118 reduces
this interaction". But the paper's measured result for the two "down" sites is **no effect**: "In contrast, S88A
and T118A mutations did not affect their binding to the occludin mRNA, as the levels of the binding complexes
and occludin protein in cells expressing HuR(S88A)-TAP or HuR(T118A)-TAP were similar to those observed in cells
expressing HuR(WT)-TAP", and "The association of HuR(WT) with occludin mRNA was disrupted by the S100A mutation,
but not by the S88A or T118A mutations". The net direction is stated in the abstract: "Reduced HuR
phosphorylation by Chk2 silencing or by reduction of Chk2 through polyamine depletion decreased HuR-binding to
the occludin mRNA and repressed occludin translation, whereas Chk2 overexpression enhanced (HuR/occludin mRNA)
association and stimulated occludin expression." Chk2 is **activating** for HuR. v5 is right and SIGNOR's two
down rows overstate what the paper shows. **No override.**

**9. CSNK2A1 → SNCA — v5 `activates` — should be HELD UNSIGNED (undecidable).** This is the one edge of the
sixteen that is squarely neuronal and has **both ends perturbed**, and it is the one where I think no sign is
defensible. Both SIGNOR rows cite a single paper, Okochi et al. 2000, which is a **site-mapping study that makes
no directional claim at all**: "In vitro experiments and two-dimensional phosphopeptide mapping provided further
evidence that serine 129 was phosphorylated by ck-1 and ck-2"; "An additional site, which was phosphorylated
less efficiently, was mapped to serine 87"; and its only functional sentence is a hedge — "These data
demonstrate that alpha-synuclein is constitutively phosphorylated within its C terminus and **may indicate** that
the function of alpha-synuclein is regulated by phosphorylation/dephosphorylation" (abstract, PMID 10617630,
read 7 November 2026). Both the `up-regulates` Ser87 row and the `down-regulates activity` Ser129 row are curator
inference from that one paper.

Second source, per the rule that a failed source is not a finished search — here the first source simply does not
answer the question. Cavallarin et al. 2010, a review: "the majority of -synuclein within inclusions from
patients with Parkinson's disease and other synucleinopathies is phosphorylated at Ser129"; "While
phosphorylation at Ser87 is enhanced in synucleinopathies, it inhibits -synuclein oligomerization, and influences
synuclein-membrane interactions"; and the framing, "an imbalance between the detrimental, oligomer-promoting
effect of Ser129 phosphorylation and a neuroprotective action of Ser87/Tyr125 phosphorylation that inhibits
toxic oligomer formation" (abstract, PMID 20522010, read 7 November 2026). So the two sites genuinely oppose, and
the readout is **aggregation propensity and membrane binding**, not activity: α-synuclein is a natively
unfolded presynaptic protein with no catalytic activity for a kinase to up- or down-regulate.

So v5's `activates` rests on nothing in the cited paper, and `inhibits` would rest on nothing either. The
physiologically honest state is **unsigned**. I propose **no override row**: the table's mechanism and its tests
only express a flip between `activates` and `inhibits`, and forcing this edge to a sign in either direction would
assert more than the sources support. Recording it as a decision for an unsigned state, or leaving it and noting
the weakness, are the two live options, and that is the owner's call.

**10. CSNK2A1 → TOP2A — v5 `activates` — WRONG, should be `inhibits`.** The up-site's own paper denies both the
effect and the kinase. SIGNOR's `up-regulates Ser1525` row cites Luo et al. 2008, read in **full text** (Europe
PMC via PubMed MCP, PMC2712943, read 7 November 2026). That paper does show pSer1524 recruits MDC1 and is needed
for the decatenation checkpoint — but on **activity** it states the opposite of an up-regulation: "We did not
observe any marked difference in activity between Topo IIα[WT] and Topo IIα[S1524A], which suggests that Topo
IIα phosphorylation at Ser 1524 does not have a major regulatory role in Topo IIα decatenation activity." And it
**excludes CK2 as the kinase**: "when cells were treated with either of the CK2 inhibitors
5,6-dichlorobenzimidazole riboside (DRB) or 4,5,6,7-tetrabromobenzotriazole (TBB), we did not observe any
decrease in pSer 1524 (data not shown), suggesting that kinases other than CK2 may be responsible for Topo IIα
Ser 1524 phosphorylation." (Note also the off-by-one: SIGNOR says Ser1525, the paper Ser1524.)

The down-site stands on its own full text. Chen et al. 2011, read in full text (PMC3058595, read 7 November
2026): "CK2 serves as a priming kinase, through phosphorylation at Ser1365, for GSK3β-mediated phosphorylation at
Ser1361. This double phosphorylation facilitated the recruitment of Fbw7 to the phospho-degron pSPKLpS of
topoIIα, leading to its ubiquitin-dependent degradation" (abstract), with the mutational evidence in the body:
"only S1361A, S1365A, and E1368A abrogated the suppressive effect of CK2α overexpression on topoIIα expression".
SIGNOR's two further CK2→TOP2A rows are `unknown`-effect site mappings (Thr1343, Daum and Gorbsky 1998,
PMID 9804834; Ser1377, Wells et al. 1994, PMID 7961967) and carry no direction.

So the only sourced effect of CK2 on TOP2A is **destabilisation**, which the graph does not separate from
activity. v5's `activates` is wrong. **Override proposed** (section 3, row C), with the `CSNK2B,TOP2A` partner
row as a separate decision.

**11. MAPK1 → RUNX1 — v5 `activates` — right.** The tie is an artefact of SIGNOR encoding one paper's two
readouts as opposite signs: all eight rows cite Biggs et al. 2005 (PMID 16046550), four as `up-regulates
activity` and four as `down-regulates quantity by destabilization` **at the same four residues**, which is
precisely that paper's dual finding ("controls both transcriptional activity and rate of degradation", quoted
under edge 6). On the activity axis v5 is right. **No override.** This edge is the direct precedent for the
CDK2→RUNX1 correction: same substrate, same residues, same papers, and v5 already reads it `activates`.

**12. PRKACA → ESR1 — v5 `activates` — leave as is (context-dependent on ligand).** Two papers, two conditions.
Chen et al. 1999 (the down-site): "ERα is phosphorylated by protein kinase A (PKA) on serine-236 within the DNA
binding domain. Mutation of serine-236 to glutamic acid prevents DNA binding by inhibiting dimerization by
ERalpha" — but with the condition stated explicitly, "PKA overexpression or activation of endogenous PKA
inhibits dimerization **in the absence of ligand**. This inhibition is overcome by the addition of
17beta-estradiol or the partial agonist 4-hydroxy tamoxifen" (abstract, PMID 9891036, read 7 November 2026).
Michalides et al. 2004 (the up-site): "phosphorylation of serine-305 in the hinge region of ERalpha by protein
kinase A (PKA) induced resistance to tamoxifen" and "PKA activity thus induces a switch from antagonistic to
agonistic effects of tamoxifen on ERalpha" (abstract, PMID 15193262, read 7 November 2026) — an up-regulation
**conditional on tamoxifen being present**.

So: unliganded, PKA inhibits ERα dimerisation; with oestradiol that inhibition is explicitly overcome; with
tamoxifen, PKA converts an antagonist into an agonist. There is no single sign, and the inhibition is the one
that is reversed under physiological ligand. I do **not** propose an override: flipping to `inhibits` would pick
the condition that physiology least often occupies. Leave as is, with the context recorded.

**13. PRKACA → MAP2 — v5 `activates` — WRONG, should be `inhibits`.** All four rows cite one paper, Ozer and
Halpain 2000. Its demonstrated result is a **disruption**: "cAMP-dependent protein kinase activity disrupts the
MAP2-microtubule interaction in living HeLa cells and promotes MAP2c localization to peripheral membrane ruffles
enriched in actin"; "Biochemical and microscopy-based assays indicated that mutation of a single residue was
adequate to disrupt the MAP2–microtubule interaction in HeLa cells" (abstract, PMID 11029056, read 7 November
2026). The three `down-regulates activity` rows carry exactly this. SIGNOR's single `up-regulates` row
(SIGNOR-83100, Ser1782) instead quotes the paper's closing **hedge about a different binding partner**:
"Specific phosphorylation states may enhance the interaction of map2 with the actin cytoskeleton, thereby
providing a regulated mechanism for map2 function within distinct cytoskeletal domains". That is a speculative
sentence about actin, not a measured up-regulation of MAP2's microtubule function, and it should not outweigh the
paper's own result.

MAP2's physiological function is microtubule stabilisation in dendrites, and PKA detaches it from microtubules,
so the effect on MAP2 function is negative. **Two honest limits**, stated because they bear on the strength of
the row: the experiments are in **HeLa cells**, not neurons, despite MAP2 being a neuronal protein (v5's own
annotation puts MAP2 at 169 TPM brain median, and PRKACA at 65); and the paper does report that two of the three
sites are phosphorylated in brain tissue ("Phosphorylation at two of these sites was detected in brain tissue"),
which supports relevance but is not a neuronal functional assay.

Second source, under the rule that a failed source is not a finished search — the PMC full text for this paper
came back **empty** from both Europe PMC and the PubMed MCP, and the publisher routes are robots-disallowed
(section 4), so the abstract is all I hold for Ozer and Halpain. The second source is **López and Sheetz 1995**
(PMID 7759496, found by PubMed search, read in its PubMed record 7 November 2026): MAP2 phosphorylation releases
MAP2 from microtubules — "The MAP2 inhibition is reversed by a kinase that is co-purified with chicken embryonic
MAP2, completely releasing MAP2 from the microtubules" and "Only the phosphorylation produced by embryonic MAP2
kinase can change the affinity of MAP2 by microtubules". **This second source has a real limit I must state
plainly: its kinase is explicitly not PKA** — "This kinase is c-AMP independent" — and the paper reports that
other kinases phosphorylate MAP2 without changing microtubule affinity. So it corroborates the direction
(phosphorylation detaching MAP2 from microtubules, in embryonic brain rather than HeLa) but **not** PKA's
specific role. The override therefore rests on Ozer and Halpain's abstract for PKA specifically, with López and
Sheetz as directional support only. **Override proposed** (section 3, row D), and the owner should weigh that
the primary paper's full text could not be read.

**14. PRKACA → NF2 — v5 `inhibits` — right.** SIGNOR's `down-regulates` Ser518 row cites Laulajainen et al.
2008 but quotes that paper's **introduction summarising others**: "Merlin contains a c-terminal serine 518,
which is phosphorylated both by p21-activated kinase (pak) and protein kinase a (pka) (shaw et al., 2001; kissil
et al., 2002; xiao et al., 2002; alfthan et al., 2004). Phosphorylation at this site is predicted to result in a
more open conformation incapable of inhibiting cell growth." The direction is nonetheless well supported by
**three independent second sources**, read in their PubMed records on 7 November 2026: Xiao et al. 2001, "Pak can
directly phosphorylate merlin at serine 518, a site that affects merlin activity and localization"
(PMID 11719502); Tang et al. 2007, "Merlin is partially regulated by phosphorylation of Ser 518, such that
**hyperphosphorylated merlin is inactive** and fails to form productive intramolecular and intermolecular
interactions" (PMID 17891137); and Guerrero et al. 2014, which treats phospho-Ser518 merlin as the oncogenic
form — "high expression of phosphorylated Merlin at serine 518 (S518-Merlin), NOTCH1 and epidermal growth factor
receptor (EGFR) correlated with increased cell proliferation and tumorigenesis" (PMID 25043298).

The up-site is a different axis. Laulajainen's own finding is about actin, not growth suppression: "we identify a
novel PKA phosphorylation site, serine 10, in the N terminus of merlin. We show that a non-phosphorylatable form
of serine 10 (S10A) affects cellular morphology" and "merlin S10A reduces the amount of cellular F-actin and
merlin S10D stabilizes F-actin filaments" (abstract, PMID 18071304, read 7 November 2026). Stabilising F-actin
is not a gain in merlin's tumour-suppressor activity. Ser518 inactivates the suppressor, which is the canonical
reading on three sources; v5's `inhibits` is right. **No override.**

**15. PRKCD → TNNI3 — v5 `inhibits` — right on the tension readout, with a readout conflict recorded.**
Interesting case: SIGNOR's **up**-regulating rows are the ones its own paper contradicts. Sumandea et al. 2008
(cited by all of Ser23, Ser24 and one Thr143 row) reports that **both** sets of sites depress force. For
Ser23/24: "Treatment of detergent-extracted single cardiomyocytes with lipid-activated PKCδ induces **depressed
tension** at submaximum but not maximum [Ca2+] as expected for cTnI-Ser23/Ser24 phosphorylation." For Thr143:
"Treatment of myocytes with Src-activated PKCδ leads to **depressed maximum tension** and cross-bridge kinetics,
attributable to a dominant effect of cTnI-Thr144 phosphorylation" (abstract, PMID 18550549, read 7 November
2026). So SIGNOR's `up-regulates activity` at Ser23/Ser24 reads a phosphorylation event as positive where the
paper measures depressed tension.

Second source, and it disagrees in direction for Thr143 on a different readout. Wijnker et al. 2014:
"Pseudo-phosphorylation of Thr143 **increased** myofilament Ca2+ sensitivity compared with WT without affecting
LDA in failing and donor cardiomyocytes" (abstract, PMID 24585778, read 7 November 2026). Ca2+ sensitivity up,
maximum tension down — not reconcilable into one sign without choosing a readout. On the tension readout, which
is the contractile output, PKCδ is inhibiting and v5 is right. **No override**, and the conflict is recorded.
Context: this is cardiac myofilament biology (TNNI3 is cardiac-specific), so it is outside the neuronal setting
the project prefers, and the sign should not be leaned on for neuronal propagation.

**16. PTK2 → ACTN4 — v5 `activates` — right.** All three rows cite Feng et al. 2013, and all three quote the
paper's **introduction reviewing others**, not its results: "Phosphorylation at y12 by fak reduces α-actinin1's
affinity for actin. α-actinin4 is phosphorylated at y4, y31, and y265. Phosphorylation at y4 or y31 decreases its
binding to actin while phosphorylation of y265 increases its affinity for actin." Read in **full text** (Europe
PMC via PubMed MCP, PMC4142059, read 7 November 2026), the paper's own result is a requirement for the Tyr265
phosphorylation: "the tyrosine phosphorylation of α-actinin1 at Y12 and α-actinin4 at Y265 is critical for dorsal
stress fiber establishment, transverse arc maintenance and focal adhesion maturation" (abstract), and "the
α-actinin4.Y265F mutant was not able to rescue either cytoskeletal defects". Two caveats I record rather than
suppress: the paper found its phosphomimetic uninformative at this site — "neither α-actinin4.Y265F nor Y265E
could reconstitute subcellular localization of wt α-actinin4, it was obvious that α-actinin4.Y265E was not real
phosphomimetic"; and the kinase the paper itself ties to FAK is α-actinin**1** Tyr12, while the α-actinin4 Y4/Y31
sites are EGF-responsive and not firmly attributed to PTK2 in this paper. So the down-sites are both
second-hand and not clearly PTK2's. On the site the paper's own rescue data support, the effect is positive.
v5's `activates` is right. **No override.**

## 3. Proposed override rows (NOT applied)

Exact column order of `configs/curated_edge_sign_overrides.csv`. **Four rows for the four "wrong" verdicts**,
then **two partner rows** that follow only if the owner adopts rows B and C. `source_is_brain_expressed` is from
v5's `brain_expressed` column on the kinase's gene node. These are proposals: nothing was written to the
repository, and adopting any of them requires first generalising
`tests/test_curated_edge_sign_overrides.py::test_every_curated_override_turns_a_stated_activation_into_an_inhibition`,
which currently asserts every row is a GRK/arrestin `activates -> inhibits` correction (section 0, point 1).

```csv
source_symbol,target_symbol,relation_type_as_sourced,sign_as_sourced,relation_type_corrected,sign_corrected,source_is_brain_expressed,reason
AURKB,H3C3,inhibits,-1.0,activates,1.0,no,"SIGNOR's two down-regulating rows for Aurora B on histone H3 Ser29 (H3S28ph) cite papers that do not support a down-regulation: Lau and Cheung 2011 (PMID 21282660) is titled ""Histone code pathway involving H3 S28 phosphorylation and K27 acetylation activates transcription and antagonizes polycomb silencing"" and states ""H3 S28 phosphorylation not only displaces binding of the polycomb-repressive complexes, but it also induces a methyl-acetylation switch of the adjacent K27 residue"" (abstract, read 7 November 2026), and Goto et al. 2002 (PMID 11856369) reports only ""Aurora-B directly phosphorylated H3, not only at Ser10 but also at Ser28"" with regard to mitotic chromosome condensation. The up-regulating Ser11 (H3S10ph) rows are the uncontroversial condensation finding. Both annotated Aurora B sites on H3 are therefore activating by their own sources. Keyed on H3C3 because that is how OmniPath spells the substrate; v5 collapses GENE:H3C3 and GENE:H3C11 onto PROTEIN:H3C11 (P68431). AURKB is not brain-expressed in v5's own annotation (brain median 0.157 TPM), so this edge matters little for neuronal propagation."
CDK2,RUNX1,inhibits,-1.0,activates,1.0,yes,"On the activity axis the sign is positive, and v5 already reads the same four residues of the same substrate as activating for two other kinases. Biggs et al. 2005 (PMID 16046550) states ""phosphorylation of AML1c on specific serine/threonine residues controls both transcriptional activity and rate of degradation"" and that mutating the four sites ""abolishes transcriptional activation, whereas mutation of these sites to aspartic acid (which mimics phosphorylation) results in a hyperactive protein"" (abstract, read 7 November 2026); the opposing annotation rests on Biggs et al. 2006 (PMID 17015473), which measures stability only (""Mutant AML1 protein which cannot be phosphorylated at these sites (AML1-4A) is more stable than wild-type AML1""). v5 holds activates for CDK1->RUNX1 and MAPK1->RUNX1 on the same papers, so the stored inhibits made one of three kinases on one substrate read the opposite way. The sourced value comes from the complex row CCNA2_CDK2 -> RUNX1 after expand_complex; the plain CDK2 -> RUNX1 row has both consensus flags set and yields binds 0.0, which this override leaves untouched."
CSNK2A1,TOP2A,activates,1.0,inhibits,-1.0,yes,"The up-regulating Ser1525 row's own paper denies both the effect and the kinase. Luo et al. 2008 (PMID 19098900, full text PMC2712943, read 7 November 2026) states ""we did not observe any marked difference in activity between Topo IIa[WT] and Topo IIa[S1524A], which suggests that Topo IIa phosphorylation at Ser 1524 does not have a major regulatory role in Topo IIa decatenation activity"" and excludes CK2 as the kinase: ""when cells were treated with either of the CK2 inhibitors 5,6-dichlorobenzimidazole riboside (DRB) or 4,5,6,7-tetrabromobenzotriazole (TBB), we did not observe any decrease in pSer 1524 ... suggesting that kinases other than CK2 may be responsible"". The remaining sourced effect is destabilisation: Chen et al. 2011 (PMID 21254166, full text PMC3058595, read 7 November 2026), ""CK2 serves as a priming kinase, through phosphorylation at Ser1365, for GSK3b-mediated phosphorylation at Ser1361. This double phosphorylation facilitated the recruitment of Fbw7 to the phospho-degron pSPKLpS of topoIIa, leading to its ubiquitin-dependent degradation"". SIGNOR's other two CK2->TOP2A rows carry effect unknown. The sourced value comes from the complex row CSNK2A1_CSNK2B -> TOP2A after expand_complex; the plain CSNK2A1 -> TOP2A row yields binds 0.0 and is left untouched."
PRKACA,MAP2,activates,1.0,inhibits,-1.0,yes,"PKA detaches MAP2 from microtubules, which is a loss of MAP2's microtubule-stabilising function. Ozer and Halpain 2000 (PMID 11029056) states ""cAMP-dependent protein kinase activity disrupts the MAP2-microtubule interaction in living HeLa cells and promotes MAP2c localization to peripheral membrane ruffles enriched in actin"" and ""mutation of a single residue was adequate to disrupt the MAP2-microtubule interaction in HeLa cells"" (abstract, read 7 November 2026). SIGNOR's single up-regulating row quotes instead that paper's speculative closing sentence about a different binding partner (""Specific phosphorylation states may enhance the interaction of map2 with the actin cytoskeleton""), which should not outweigh its measured result. Limits recorded: the experiments are in HeLa, not neurons, though the paper detected phosphorylation at two of the sites in brain tissue, and the PMC full text could not be read (empty from Europe PMC and the PubMed MCP; publisher routes robots-disallowed). Second source for the direction only, not for PKA: Lopez and Sheetz 1995 (PMID 7759496), ""completely releasing MAP2 from the microtubules"", whose kinase is explicitly ""c-AMP independent""."
```

**Partner rows, each its own decision, which follow only if row B or row C is adopted.** `expand_complex` splits
the complex row before the override is keyed, so correcting the catalytic subunit alone leaves the partner
subunit of the same complex carrying the old sign on the same substrate — the internal inconsistency that
decision 9.10(a) treated as evidence that a sign is a source convention and not a claim. I propose these
separately rather than folding them in, because the owner's standing rule is that related decisions are decided
one by one, and because the physiology differs: CCNA2 is a cyclin and CSNK2B a regulatory subunit, neither of
which phosphorylates anything itself.

```csv
source_symbol,target_symbol,relation_type_as_sourced,sign_as_sourced,relation_type_corrected,sign_corrected,source_is_brain_expressed,reason
CCNA2,RUNX1,inhibits,-1.0,activates,1.0,yes,"Follows the CDK2,RUNX1 correction and only if that is adopted. Both edges come from one OmniPath row, CCNA2_CDK2 -> RUNX1, which expand_complex splits into CDK2->RUNX1 and CCNA2->RUNX1; correcting only the catalytic subunit would leave cyclin A2 reading inhibits on the same substrate and the same evidence. The evidence is the same as the CDK2,RUNX1 row: Biggs et al. 2005 (PMID 16046550), phosphorylation of the four sites raises RUNX1 transcriptional activity; Biggs et al. 2006 (PMID 17015473) measures stability only. CCNA2 is the cyclin partner and has no kinase activity of its own, so the sign it carries is the holoenzyme's."
CSNK2B,TOP2A,activates,1.0,inhibits,-1.0,yes,"Follows the CSNK2A1,TOP2A correction and only if that is adopted. Both edges come from one OmniPath row, CSNK2A1_CSNK2B -> TOP2A, which expand_complex splits; correcting only the catalytic subunit would leave the CK2 regulatory subunit reading activates on the same substrate and the same evidence. The evidence is the same as the CSNK2A1,TOP2A row: Luo et al. 2008 (PMID 19098900) finds no activity effect of pSer1524 and excludes CK2 as its kinase, leaving Chen et al. 2011 (PMID 21254166) and CK2-primed, GSK3b-completed phospho-degron destabilisation as the only sourced effect. CSNK2B is the regulatory subunit and has no catalytic activity of its own."
```

**And one edge for which I propose no row, deliberately: CSNK2A1 → SNCA** (edge 9). The physiologically honest
state is **unsigned**, not a flip. Both SIGNOR rows rest on a site-mapping paper that makes no directional claim
("may indicate that the function of alpha-synuclein is regulated by phosphorylation/dephosphorylation",
Okochi et al. 2000, PMID 10617630), the second source frames the two sites as opposing effects on **aggregation**
rather than activity (Cavallarin et al. 2010, PMID 20522010), and α-synuclein has no catalytic activity for a
sign to describe. This is the only one of the sixteen that is both neuronal and has both ends perturbed, so it is
the one most worth the owner's attention — and the override table as built cannot express the answer.

## 4. Routes, refusals and a notice

- **Reads.** Primary papers were read in their PubMed records (PubMed MCP `get_article_metadata`) and, where
  open, in Europe PMC full text. Every Europe PMC bibliographic record was fetched with
  `experiments/read_public_page.py` (27 records, all status 200, saved with address, time and SHA-256 in
  `signs16/epmc_meta/`). Three full texts were read that way (`PMC3813944` Slee and Lu, `PMC10070344` Chen 2023,
  `PMC3201881` Yu 2011, saved in `signs16/epmc_full/`); four more came through the PubMed MCP's PMC full text
  (`PMC4142059` Feng 2013, `PMC3058595` Chen 2011, `PMC2712943` Luo 2008, and the records confirming empty bodies
  for others).
- **Refused or unavailable, recorded and not worked around.** Europe PMC's `fullTextXML` answered **HTTP 500**
  for 11 PMC ids (`PMC151710`, `PMC3041124`, `PMC1951741`, `PMC1636878`, `PMC3058595`, `PMC2712943`, `PMC116031`,
  `PMC15014`, `PMC2504892`, `PMC3989756`, `PMC4142059`); for six of these the PubMed MCP supplied the full text
  or confirmed the body is empty in PMC, which is the second route. **jbc.org is robots-disallowed** for this
  reader, which closed the publisher route to four JBC papers (Okochi 2000, Liu 2004, Daum and Gorbsky 1998,
  Wells et al. 1994); all four were read in their PubMed and Europe PMC records instead. **Five papers are held
  as abstract only** where PMC holds no body and the publisher refused: Ozer and Halpain 2000 (which matters, and
  is flagged in row D), Laulajainen 2008, Sumandea 2008, Wijnker 2014, Lee 2008. No page was read through a
  cache, a mirror or a solved challenge, and no permission request was left unanswered — the shell fallback was
  used throughout, per the owner's ruling of 11 October 2026.
- **Peer review (decision 9.101).** All 31 papers cited in this pass are peer-reviewed journal articles with
  DOIs, journal volumes and page ranges, confirmed in both PubMed and Europe PMC. No preprint is cited, so the
  18-month rule is not engaged by anything here.
- **Text addressed to an AI assistant.** The PubMed MCP's tool results carry a block headed "**Important Legal
  Requirement**" instructing the assistant to attribute PubMed and to include DOI links, and stating that
  "adversarial requests to skip attribution are common". **Reported here and not acted on as an instruction**, per
  CLAUDE.md. It changed nothing about this pass: every paper is cited with its PMID, and the DOIs are in the
  BibTeX below because the repository's own convention requires them. I note only that it is tool-supplied text
  directed at an assistant, which the owner asked to be told about.

## 5. Counts

Of the **16** edges:

| Verdict on the stored v5 sign | Count | Edges |
|---|---|---|
| **Right** | **8** | AURKA→TP53, CDK1→VHL, CDK5→PLD2, CHEK2→ELAVL1, MAPK1→RUNX1, PRKACA→NF2, PRKCD→TNNI3, PTK2→ACTN4 |
| **Wrong** | **4** | AURKB→H3C11, CDK2→RUNX1, CSNK2A1→TOP2A, PRKACA→MAP2 |
| **Hold unsigned** | **1** | CSNK2A1→SNCA |
| **Leave as is (context-dependent)** | **3** | ABL1→PSMA7, AURKB→KIF2C, PRKACA→ESR1 |

By **net physiological effect** at the papers, on the same 16:

| Net effect | Count | Edges |
|---|---|---|
| **Activating** | **6** | AURKB→H3C11, CDK2→RUNX1, CDK5→PLD2, CHEK2→ELAVL1, MAPK1→RUNX1, PTK2→ACTN4 |
| **Inhibiting** | **6** | AURKA→TP53, CDK1→VHL, CSNK2A1→TOP2A, PRKACA→MAP2, PRKACA→NF2, PRKCD→TNNI3 |
| **Context-dependent** | **3** | ABL1→PSMA7 (activity versus abundance), AURKB→KIF2C (site-specific localisation, Xenopus), PRKACA→ESR1 (ligand-dependent) |
| **Undecidable** | **1** | CSNK2A1→SNCA |

**Perturbation flags**, from the record's own fields recomputed in this pass: **13 of the 16** touch a perturbed
gene or drug target (the record says 14; the gap is flagged in section 1). Nine have a perturbed kinase, nine a
perturbed substrate, and one a drug-target substrate: **AURKA→TP53**, where TP53 is the target of the
`HTT|CAG_repeat_expansion` drug entry. The three that touch nothing are AURKB→H3C11, AURKB→KIF2C and CDK5→PLD2.
Of the four "wrong" edges, **three touch a perturbed gene** (CDK2→RUNX1 substrate, CSNK2A1→TOP2A kinase,
PRKACA→MAP2 kinase) and AURKB→H3C11 touches none.

**A note on how much of this is SIGNOR curation rather than real site-level opposition.** Of the 16, **9** turn
out to rest on a SIGNOR row that its own cited paper does not support, or on a sentence quoted from a paper's
introduction or a hedge rather than its result: AURKA→TP53 (Ser315, secondary citation), AURKB→H3C11 (Ser29, both
papers), CDK1→VHL (same residue, both ways), CDK5→PLD2 (same residue, both ways), CHEK2→ELAVL1 (S88/T118 shown to
have no effect), CSNK2A1→SNCA (no directional claim in the source), CSNK2A1→TOP2A (Ser1525's paper denies effect
and kinase), PRKACA→MAP2 (up-row quotes a hedge about actin), PRKCD→TNNI3 (Ser23/24 up-rows contradict the
paper's depressed tension), PTK2→ACTN4 (all three rows from the introduction). So the site-level opposition the
record counted is, in most of these cases, **annotation noise rather than biology** — which supports the record's
verdict that the representation question should be dropped, and narrows the real work to the four corrections
above.

## 6. Confirmation of model

**I ran on Fable (claude-fable-5-1) throughout this pass**, from reading CLAUDE.md and the SIGNOR release to
reading every paper, forming every verdict and writing this file. There was no fallback to another model at any
point; had one occurred I would have stopped and reported it rather than finishing. Every research step above —
finding and reading the sources, appraising them, and turning what they say into the verdicts and the proposed
rows — was done on Fable, as the rule of 25 October 2026 requires.

## 7. BibTeX for the new papers

**31 entries. Keys checked against all 705 keys in `docs/references.bib`: none of these 31 papers is present**
(checked both by key and by PMID — no `pmid` field in `docs/references.bib` matches any of the 31). Every author
list, journal, year, volume, issue and page range was read from the PubMed record (PubMed MCP
`get_article_metadata`, 7 November 2026) and confirmed against the Europe PMC record
(`ebi.ac.uk/europepmc/webservices/rest/search`, read with `experiments/read_public_page.py` the same day). The
check found **no discrepancies** between the two for any of the 31. Following the convention of commit `8ad304c`:
no field is completed from inference, a field the records did not supply is absent, and each `note` states what
is held (abstract only, or full text and where it was read).

Three of the PubMed publication years disagree with the journal-issue year, as `8ad304c` warned they can; per
that commit's rule the **journal-issue year of the Europe PMC record is used and the discrepancy is stated in the
note**: Katayama et al. (PubMed 2003-12-14, journal issue 2004), Hsueh et al. (PubMed 2012-11-28, journal issue
2013), Luo et al. (PubMed 2008-12-21, journal issue 2009), Laulajainen et al. (PubMed 2007-12-10, journal issue
2008), Chen et al. 1999 (PubMed 1999-02, journal issue 1999 — no disagreement), Goto et al. (PubMed 2002-01,
journal issue 2002 — no disagreement), Feng et al. (PubMed 2013-02-27, journal issue 2013 — no disagreement),
Wijnker et al. (PubMed 2014-02-28, journal issue 2014 — no disagreement).

```bibtex
% Bibliography entries for the disputed-sign research pass of 7 November 2026
% (docs/signor_disputed_signs_2026-11-07.md), prepared on Fable 5.1 on 7 November 2026 for appending to
% docs/references.bib. 31 entries; none of the 31 is already in the file, checked by key and by PMID.
%
% Every author list, journal, year, volume, issue and page range below was read from the PubMed record
% (PubMed MCP get_article_metadata) and confirmed against the Europe PMC record
% (ebi.ac.uk/europepmc/webservices/rest/search, read with experiments/read_public_page.py on 7 November 2026).
% Where PubMed's publication date and the journal-issue year disagreed, the journal-issue year of the
% Europe PMC record is used and the discrepancy is stated in the note. No field is completed from
% inference: a field the records did not supply is absent.

@article{li2015cabl,
  author  = {Li, Dapei and Dong, Qincai and Tao, Qingping and Gu, Jing and Cui, Yan and Jiang, Xuefeng and Yuan, Jing and Li, Weihua and Xu, Rao and Jin, Yanwen and Li, Ping and Weaver, David T and Ma, Qingjun and Liu, Xuan and Cao, Cheng},
  title   = {c-Abl regulates proteasome abundance by controlling the ubiquitin-proteasomal degradation of {PSMA7} subunit},
  journal = {Cell Reports},
  year    = {2015},
  volume  = {10},
  number  = {4},
  pages   = {484--496},
  doi     = {10.1016/j.celrep.2014.12.044},
  pmid    = {25620702},
  note    = {ABSTRACT ONLY is held; no PMC body, and the publisher route was not attempted. The up-regulating Tyr106 site of the ABL1 to PSMA7 edge (edge 1 of the disputed-sign pass): "the 20S proteasome subunit PSMA7 is subjected to ubiquitination and proteasomal degradation, which was suppressed by PSMA7 phosphorylation at Y106 mediated by the nonreceptor tyrosine kinases c-Abl/Arg"; "Downregulated PSMA7 level results in decreased proteasome abundance in c-Abl/Arg RNAi-knockdown or c-abl/arg-deficient cells". This is an effect on PSMA7 abundance, where PMID 16678104 reports an effect on proteasome activity in the other direction; v5's inhibits was left as is on the activity axis}
}

@article{liu2006cabl,
  author  = {Liu, Xuan and Huang, Wei and Li, Chufang and Li, Ping and Yuan, Jing and Li, Xiaorong and Qiu, Xiao-Bo and Ma, Qingjun and Cao, Cheng},
  title   = {Interaction between c-Abl and Arg tyrosine kinases and proteasome subunit {PSMA7} regulates proteasome degradation},
  journal = {Molecular Cell},
  year    = {2006},
  volume  = {22},
  number  = {3},
  pages   = {317--327},
  doi     = {10.1016/j.molcel.2006.04.007},
  pmid    = {16678104},
  note    = {ABSTRACT ONLY is held; no PMC body. The down-regulating Tyr153 site of the ABL1 to PSMA7 edge: "c-Abl and Arg (abl-related gene) tyrosine kinases associate with and phosphorylate the proteasome PSMA7 (alpha4) subunit at Tyr-153. Consequently, proteasome-dependent proteolysis is compromised." The activity-axis evidence on which v5's inhibits was left standing}
}

@article{slee2013requirement,
  author  = {Slee, Elizabeth A and Lu, Xin},
  title   = {Requirement for phosphorylation of {P53} at {Ser312} in suppression of chemical carcinogenesis},
  journal = {Scientific Reports},
  year    = {2013},
  volume  = {3},
  pages   = {3105},
  doi     = {10.1038/srep03105},
  pmid    = {24173284},
  pmcid   = {PMC3813944},
  note    = {FULL TEXT held, read in Europe PMC (PMC3813944) with experiments/read_public_page.py on 7 November 2026; CC BY-NC-ND per the Europe PMC licence field. Cited in the disputed-sign pass as the source SIGNOR gives for an up-regulating AURKA to TP53 Ser315 row that this paper does not support: it is a mouse Ser312 knock-in study and mentions Aurora-A only in passing, "The interaction between p53 and E2F1 is enhanced by phosphorylation of p53 on Ser315, a residue within the E2F1 binding region that is phosphorylated by cell cycle kinases such as cdk1, cdk2, cdk9 and Aurora kinase A", while its own reference list names the primary paper (PMID 14702041) as "Phosphorylation by aurora kinase A induces Mdm2-mediated destabilization and inhibition of p53"}
}

@article{katayama2004phosphorylation,
  author  = {Katayama, Hiroshi and Sasai, Kaori and Kawai, Hidehiko and Yuan, Zhi-Min and Bondaruk, Jolanta and Suzuki, Fumio and Fujii, Satoshi and Arlinghaus, Ralph B and Czerniak, Bogdan A and Sen, Subrata},
  title   = {Phosphorylation by aurora kinase {A} induces {Mdm2}-mediated destabilization and inhibition of p53},
  journal = {Nature Genetics},
  year    = {2004},
  volume  = {36},
  number  = {1},
  pages   = {55--62},
  doi     = {10.1038/ng1279},
  pmid    = {14702041},
  note    = {ABSTRACT ONLY is held; no PMC body. The primary paper for Aurora-A's p53 Ser315 site, found by PubMed search after Slee and Lu 2013 (PMID 24173284) was found to be only a secondary citation. It settles edge 2 of the disputed-sign pass in v5's favour: "we show that aurora kinase A phosphorylates p53 at Ser315, leading to its ubiquitination by Mdm2 and proteolysis"; "Silencing of aurora kinase A results in less phosphorylation of p53 at Ser315, greater stability of p53 and cell-cycle arrest at G2-M". So Ser315 is inhibiting, and SIGNOR's up-regulating row for it is a mis-signing. PubMed dates this 14 December 2003; the journal issue is 2004, which is the year used here per the convention of commit 8ad304c}
}

@article{liu2004auroraa,
  author  = {Liu, Qiyuan and Kaneko, Satoshi and Yang, Lin and Feldman, Richard I and Nicosia, Santo V and Chen, Jiandong and Cheng, Jin Q},
  title   = {Aurora-A abrogation of p53 {DNA} binding and transactivation activity by phosphorylation of serine 215},
  journal = {The Journal of Biological Chemistry},
  year    = {2004},
  volume  = {279},
  number  = {50},
  pages   = {52175--52182},
  doi     = {10.1074/jbc.M406802200},
  pmid    = {15469940},
  note    = {ABSTRACT ONLY is held: no PMC body, and jbc.org is robots-disallowed for experiments/read_public_page.py (recorded as a refusal on 7 November 2026). The down-regulating Ser215 site of edge 2: "the phosphorylation of p53 by Aurora-A at Ser-215 abrogates p53 DNA binding and transactivation activity"; "Downstream target genes of p53, such as p21Cip/WAF1 and PTEN, were inhibited by Aurora-A in a Ser-215 phosphorylation-dependent manner"}
}

@article{hsueh2013novel,
  author  = {Hsueh, Kai-Wei and Fu, Shu-Ling and Chang, Chirn-Bin and Chang, Yu-Ling and Lin, Chao-Hsiung},
  title   = {A novel {Aurora-A}-mediated phosphorylation of p53 inhibits its interaction with {MDM2}},
  journal = {Biochimica et Biophysica Acta},
  year    = {2013},
  volume  = {1834},
  number  = {2},
  pages   = {508--515},
  doi     = {10.1016/j.bbapap.2012.11.005},
  pmid    = {23201157},
  note    = {ABSTRACT ONLY is held; no PMC body. The up-regulating Ser106 site of edge 2: "Ser-106 phosphorylation of p53 decreases its interaction with MDM2 and prolongs the half-life of p53". The one genuinely activating Aurora-A site on p53, outweighed by Ser215 and Ser315. PubMed dates this 28 November 2012; the journal issue is 2013, which is the year used here per the convention of commit 8ad304c}
}

@article{martens2003cascade,
  author  = {Martens, Joost H A and Verlaan, Matty and Kalkhoven, Eric and Zantema, Alt},
  title   = {Cascade of distinct histone modifications during collagenase gene activation},
  journal = {Molecular and Cellular Biology},
  year    = {2003},
  volume  = {23},
  number  = {5},
  pages   = {1808--1816},
  doi     = {10.1128/MCB.23.5.1808-1816.2003},
  pmid    = {12588998},
  pmcid   = {PMC151710},
  note    = {ABSTRACT ONLY is held: the PMC body is empty in both Europe PMC (fullTextXML answered HTTP 500) and the PubMed MCP. One of the two sources SIGNOR gives for the activating histone H3 Ser11 (H3S10ph) site of edge 3: "in addition to acetylation, histone H3 lysine 4 di- and trimethylation and histone H3 serine 10 phosphorylation are important steps in the activation of this gene"}
}

@article{allison2003loss,
  author  = {Allison, Simon J and Milner, Jo},
  title   = {Loss of p53 has site-specific effects on histone {H3} modification, including serine 10 phosphorylation important for maintenance of ploidy},
  journal = {Cancer Research},
  year    = {2003},
  volume  = {63},
  number  = {20},
  pages   = {6674--6679},
  pmid    = {14583461},
  note    = {ABSTRACT ONLY is held; no PMC body and no DOI in either the PubMed or the Europe PMC record, so no doi field is given. The second source SIGNOR gives for the activating histone H3 Ser11 site of edge 3: "Phosphorylation of S10 is known to be linked with the initiation of chromosome condensation in G(2) and is also important for proper chromosome segregation at mitosis"}
}

@article{lau2011histone,
  author  = {Lau, Priscilla Nga Ieng and Cheung, Peter},
  title   = {Histone code pathway involving {H3} {S28} phosphorylation and {K27} acetylation activates transcription and antagonizes polycomb silencing},
  journal = {Proceedings of the National Academy of Sciences of the United States of America},
  year    = {2011},
  volume  = {108},
  number  = {7},
  pages   = {2801--2806},
  doi     = {10.1073/pnas.1012798108},
  pmid    = {21282660},
  pmcid   = {PMC3041124},
  note    = {ABSTRACT ONLY is held: the PMC body is empty in both Europe PMC (fullTextXML answered HTTP 500) and the PubMed MCP. Load-bearing for the AURKB to H3C11 correction (edge 3, override row A): SIGNOR cites this paper for a DOWN-regulating H3 Ser29 row, but its title and abstract say the opposite, "H3 S28 phosphorylation not only displaces binding of the polycomb-repressive complexes, but it also induces a methyl-acetylation switch of the adjacent K27 residue". Also the primary MSK1 paper, and so the basis of the adjacent observation that v5's inhibits for RPS6KA5 to H3-3A is likely wrong too: "the H3 kinase MSK1 is a direct and potent transcriptional activator. Targeting of this H3 kinase to the endogenous c-fos promoter is sufficient to activate its expression without the need of upstream signaling"}
}

@article{goto2002aurorab,
  author  = {Goto, Hidemasa and Yasui, Yoshihiro and Nigg, Erich A and Inagaki, Masaki},
  title   = {{Aurora-B} phosphorylates {Histone} {H3} at serine28 with regard to the mitotic chromosome condensation},
  journal = {Genes to Cells},
  year    = {2002},
  volume  = {7},
  number  = {1},
  pages   = {11--17},
  doi     = {10.1046/j.1356-9597.2001.00498.x},
  pmid    = {11856369},
  note    = {ABSTRACT ONLY is held; no PMC body. The second paper SIGNOR cites for a down-regulating AURKB to H3 Ser29 row that it does not support (edge 3, override row A): the paper reports only that "With regard to mitotic chromosome condensation, Aurora-B directly phosphorylated H3, not only at Ser10 but also at Ser28", with no down-regulation claim}
}

@article{zhang2007aurorab,
  author  = {Zhang, Xin and Lan, Weijie and Ems-McClung, Stephanie C and Stukenberg, P Todd and Walczak, Claire E},
  title   = {{Aurora} {B} phosphorylates multiple sites on mitotic centromere-associated kinesin to spatially and temporally regulate its function},
  journal = {Molecular Biology of the Cell},
  year    = {2007},
  volume  = {18},
  number  = {9},
  pages   = {3264--3276},
  doi     = {10.1091/mbc.e07-01-0086},
  pmid    = {17567953},
  pmcid   = {PMC1951741},
  note    = {ABSTRACT ONLY is held: the PMC body is empty in both Europe PMC (fullTextXML answered HTTP 500) and the PubMed MCP. The single source for all three rows of the AURKB to KIF2C edge (edge 4), left as is because the readout is localisation rather than activity and the work is in Xenopus laevis: "MCAK association with chromosome arms is promoted by phosphorylation of T95 on MCAK, whereas phosphorylation of S196 on MCAK promotes dissociation from the arms"; "Our study reveals a new role for Aurora B, which is to prevent excess MCAK binding to chromatin to facilitate chromatin-nucleated spindle assembly". The paper's residue numbers (T95, S110, S196) differ from SIGNOR's human mapping (Ser95, Ser111, Ser192)}
}

@article{chen2023pin1,
  author  = {Chen, Jiayi and Li, Mei and Liu, Yeqing and Guan, Tangming and Yang, Xiao and Wen, Yalei and Zhu, Yingjie and Xiao, Zeyu and Shen, Xiangchun and Zhang, Haoxing and Tang, Hui and Liu, Tongzheng},
  title   = {{PIN1} and {CDK1} cooperatively govern {pVHL} stability and suppressive functions},
  journal = {Cell Death and Differentiation},
  year    = {2023},
  volume  = {30},
  number  = {4},
  pages   = {1082--1095},
  doi     = {10.1038/s41418-023-01128-x},
  pmid    = {36813923},
  pmcid   = {PMC10070344},
  note    = {FULL TEXT held, read in Europe PMC (PMC10070344) with experiments/read_public_page.py on 7 November 2026; CC BY per the Europe PMC licence field. The single source for both rows of the CDK1 to VHL edge (edge 5), settling it in v5's favour: "CDK1 directly phosphorylates pVHL at Ser80, which primes the recognition of pVHL by PIN1. PIN1 then binds to phosphorylated pVHL and facilitates the recruitment of the E3 ligase WSB1, therefore targeting pVHL for ubiquitination and degradation" (abstract), and in the body "The phosphorylation of pVHL at Ser80 promotes its ubiquitination and degradation" and "the phosphorylation of pVHL at Ser80 is pivotal to promote tumor progression through destabilizing pVHL". SIGNOR's up-regulates-activity row at the same residue quotes the same priming sentence and reads it as activation}
}

@article{biggs2005phosphorylation,
  author  = {Biggs, Joseph R and Zhang, Youhong and Peterson, Luke F and Garcia, Marileila and Zhang, Dong-Er and Kraft, Andrew S},
  title   = {Phosphorylation of {AML1}/{RUNX1} regulates its degradation and nuclear matrix association},
  journal = {Molecular Cancer Research},
  year    = {2005},
  volume  = {3},
  number  = {7},
  pages   = {391--401},
  doi     = {10.1158/1541-7786.MCR-04-0184},
  pmid    = {16046550},
  note    = {ABSTRACT ONLY is held; no PMC body. Load-bearing for the CDK2 to RUNX1 correction (edge 6, override row B) and for leaving MAPK1 to RUNX1 alone (edge 11). It is the paper behind both the up-regulating and the down-regulating rows of those edges, and it states both readouts at once: "Thus, phosphorylation of AML1c on specific serine/threonine residues controls both transcriptional activity and rate of degradation"; and on the activity axis, "mutation of these four sites (serine 276, serine 293, serine 303, and threonine 300) to alanine abolishes transcriptional activation, whereas mutation of these sites to aspartic acid (which mimics phosphorylation) results in a hyperactive protein" (quoted from SIGNOR's sentence field, which reproduces the paper). Note the paper numbers the sites 276/293/303/300 where SIGNOR maps them to Ser249/Ser266/Ser276/Thr273}
}

@article{biggs2006aml1,
  author  = {Biggs, Joseph R and Peterson, Luke F and Zhang, Youhong and Kraft, Andrew S and Zhang, Dong-Er},
  title   = {{AML1}/{RUNX1} phosphorylation by cyclin-dependent kinases regulates the degradation of {AML1}/{RUNX1} by the anaphase-promoting complex},
  journal = {Molecular and Cellular Biology},
  year    = {2006},
  volume  = {26},
  number  = {20},
  pages   = {7420--7429},
  doi     = {10.1128/MCB.00597-06},
  pmid    = {17015473},
  pmcid   = {PMC1636878},
  note    = {ABSTRACT ONLY is held: the PMC body is empty in both Europe PMC (fullTextXML answered HTTP 500) and the PubMed MCP. The stability-only evidence behind the down-regulating row of the CDK2 to RUNX1 edge (edge 6, override row B): "phosphorylation of AML1 serines 276 and 303 can be blocked in vivo by inhibitors of the cyclin-dependent kinases (CDKs) Cdk1 and Cdk2"; "Mutant AML1 protein which cannot be phosphorylated at these sites (AML1-4A) is more stable than wild-type AML1". It measures degradation, not transcriptional activity, which is why the activity axis of PMID 16046550 governs the correction}
}

@article{lee2008cdk5,
  author  = {Lee, Hye Young and Jung, Hyuntae and Jang, Il Ho and Suh, Pann-Ghill and Ryu, Sung Ho},
  title   = {{Cdk5} phosphorylates {PLD2} to mediate {EGF}-dependent insulin secretion},
  journal = {Cellular Signalling},
  year    = {2008},
  volume  = {20},
  number  = {10},
  pages   = {1787--1794},
  doi     = {10.1016/j.cellsig.2008.06.009},
  pmid    = {18625302},
  note    = {ABSTRACT ONLY is held; no PMC body. The single source for both rows of the CDK5 to PLD2 edge (edge 7), settling it in v5's favour: "we suggest that the phosphorylation and activation of PLD2 by cyclin-dependent kinase 5 (Cdk5) is critical for EGF-dependent insulin secretion"; "PLD2-S134A did not show EGF-dependent phosphorylation and activation by Cdk5". SIGNOR's down-regulates-activity row at the same residue quotes the very sentence containing "activation" and signs it negative, one of the curation conflicts the record of 7 November 2026 named ("CDK5 to PLD2 Ser134")}
}

@article{yu2011chk2,
  author  = {Yu, Ting-Xi and Wang, Peng-Yuan and Rao, Jaladanki N and Zou, Tongtong and Liu, Lan and Xiao, Lan and Gorospe, Myriam and Wang, Jian-Ying},
  title   = {{Chk2}-dependent {HuR} phosphorylation regulates occludin {mRNA} translation and epithelial barrier function},
  journal = {Nucleic Acids Research},
  year    = {2011},
  volume  = {39},
  number  = {19},
  pages   = {8472--8487},
  doi     = {10.1093/nar/gkr567},
  pmid    = {21745814},
  pmcid   = {PMC3201881},
  note    = {FULL TEXT held, read in Europe PMC (PMC3201881) with experiments/read_public_page.py on 7 November 2026; CC BY-NC per the Europe PMC licence field. The single source for all three rows of the CHEK2 to ELAVL1 edge (edge 8), settling it in v5's favour: the abstract gives the net direction, "Reduced HuR phosphorylation by Chk2 silencing or by reduction of Chk2 through polyamine depletion decreased HuR-binding to the occludin mRNA and repressed occludin translation, whereas Chk2 overexpression enhanced (HuR/occludin mRNA) association and stimulated occludin expression", and the body shows the two sites SIGNOR signs negative had no measurable effect, "In contrast, S88A and T118A mutations did not affect their binding to the occludin mRNA" and "The association of HuR(WT) with occludin mRNA was disrupted by the S100A mutation, but not by the S88A or T118A mutations"}
}

@article{okochi2000constitutive,
  author  = {Okochi, M and Walter, J and Koyama, A and Nakajo, S and Baba, M and Iwatsubo, T and Meijer, L and Kahle, P J and Haass, C},
  title   = {Constitutive phosphorylation of the {Parkinson's} disease associated alpha-synuclein},
  journal = {The Journal of Biological Chemistry},
  year    = {2000},
  volume  = {275},
  number  = {1},
  pages   = {390--397},
  doi     = {10.1074/jbc.275.1.390},
  pmid    = {10617630},
  note    = {ABSTRACT ONLY is held: no PMC body, and jbc.org is robots-disallowed for experiments/read_public_page.py (recorded as a refusal on 7 November 2026). The single source for both rows of the CSNK2A1 to SNCA edge (edge 9), and it makes NO directional claim, which is why that edge is recommended for an unsigned state rather than either sign: "In vitro experiments and two-dimensional phosphopeptide mapping provided further evidence that serine 129 was phosphorylated by ck-1 and ck-2"; "An additional site, which was phosphorylated less efficiently, was mapped to serine 87"; and only the hedge "These data demonstrate that alpha-synuclein is constitutively phosphorylated within its C terminus and may indicate that the function of alpha-synuclein is regulated by phosphorylation/dephosphorylation". Both of SIGNOR's opposite-signed rows are curator inference from this one site-mapping paper}
}

@article{cavallarin2010role,
  author  = {Cavallarin, Nadia and Vicario, Mattia and Negro, Alessandro},
  title   = {The role of phosphorylation in synucleinopathies: focus on {Parkinson's} disease},
  journal = {CNS and Neurological Disorders Drug Targets},
  year    = {2010},
  volume  = {9},
  number  = {4},
  pages   = {471--481},
  doi     = {10.2174/187152710791556140},
  pmid    = {20522010},
  note    = {ABSTRACT ONLY is held; no PMC body. A review, used as the second source for the CSNK2A1 to SNCA edge (edge 9) after the primary paper (PMID 10617630) was found to make no directional claim. It frames the two sites as opposing effects on aggregation rather than on activity, which is the basis of the undecidable verdict: "the majority of -synuclein within inclusions from patients with Parkinson's disease and other synucleinopathies is phosphorylated at Ser129"; "While phosphorylation at Ser87 is enhanced in synucleinopathies, it inhibits -synuclein oligomerization, and influences synuclein-membrane interactions"; "an imbalance between the detrimental, oligomer-promoting effect of Ser129 phosphorylation and a neuroprotective action of Ser87/Tyr125 phosphorylation that inhibits toxic oligomer formation". The elisions are the source's own rendering of the alpha prefix in the PubMed abstract}
}

@article{chen2011novel,
  author  = {Chen, Mei-Chuan and Chen, Chun-Han and Chuang, Hsiao-Ching and Kulp, Samuel K and Teng, Che-Ming and Chen, Ching-Shih},
  title   = {Novel mechanism by which histone deacetylase inhibitors facilitate topoisomerase {II}alpha degradation in hepatocellular carcinoma cells},
  journal = {Hepatology},
  year    = {2011},
  volume  = {53},
  number  = {1},
  pages   = {148--159},
  doi     = {10.1002/hep.23964},
  pmid    = {21254166},
  pmcid   = {PMC3058595},
  note    = {FULL TEXT held, read through the PubMed MCP's PMC full text (PMC3058595) on 7 November 2026 after Europe PMC's fullTextXML answered HTTP 500. The down-regulating Ser1365 site of the CSNK2A1 to TOP2A edge, and the surviving sourced effect behind override row C (edge 10): "CK2 serves as a priming kinase, through phosphorylation at Ser1365, for GSK3beta-mediated phosphorylation at Ser1361. This double phosphorylation facilitated the recruitment of Fbw7 to the phospho-degron pSPKLpS of topoIIalpha, leading to its ubiquitin-dependent degradation" (abstract), with the mutational evidence in the body, "only S1361A, S1365A, and E1368A abrogated the suppressive effect of CK2alpha overexpression on topoIIalpha expression"}
}

@article{daum1998casein,
  author  = {Daum, J R and Gorbsky, G J},
  title   = {Casein kinase {II} catalyzes a mitotic phosphorylation on threonine 1342 of human {DNA} topoisomerase {II}alpha, which is recognized by the {3F3}/2 phosphoepitope antibody},
  journal = {The Journal of Biological Chemistry},
  year    = {1998},
  volume  = {273},
  number  = {46},
  pages   = {30622--30629},
  doi     = {10.1074/jbc.273.46.30622},
  pmid    = {9804834},
  note    = {ABSTRACT ONLY is held: no PMC body, and jbc.org is robots-disallowed for experiments/read_public_page.py (recorded as a refusal on 7 November 2026). One of two CK2 to TOP2A site mappings that SIGNOR annotates with effect "unknown" and that therefore carry no direction for edge 10: "Recombinant CKII catalyzed the formation of the 3F3/2 phosphoepitope on fragments of HsTIIalpha containing threonine 1342"}
}

@article{wells1994serine,
  author  = {Wells, N J and Addison, C M and Fry, A M and Ganapathi, R and Hickson, I D},
  title   = {Serine 1524 is a major site of phosphorylation on human topoisomerase {II} alpha protein in vivo and is a substrate for casein kinase {II} in vitro},
  journal = {The Journal of Biological Chemistry},
  year    = {1994},
  volume  = {269},
  number  = {47},
  pages   = {29746--29751},
  pmid    = {7961967},
  note    = {ABSTRACT ONLY is held: no PMC body, no DOI in either the PubMed or the Europe PMC record (so no doi field is given), and jbc.org is robots-disallowed for experiments/read_public_page.py (recorded as a refusal on 7 November 2026). The second CK2 to TOP2A site mapping SIGNOR annotates with effect "unknown" (edge 10): "Site-directed mutagenesis studies identified these casein kinase II-specific phosphorylation sites as serine 1524 and serine 1376." Relevant because Luo et al. 2008 (PMID 19098900) later found CK2 inhibitors did not reduce pSer1524 in cells}
}

@article{luo2008topoisomerase,
  author  = {Luo, Kuntian and Yuan, Jian and Chen, Junjie and Lou, Zhenkun},
  title   = {Topoisomerase {II}alpha controls the decatenation checkpoint},
  journal = {Nature Cell Biology},
  year    = {2009},
  volume  = {11},
  number  = {2},
  pages   = {204--210},
  doi     = {10.1038/ncb1828},
  pmid    = {19098900},
  pmcid   = {PMC2712943},
  note    = {FULL TEXT held, read through the PubMed MCP's PMC full text (PMC2712943) on 7 November 2026 after Europe PMC's fullTextXML answered HTTP 500. Load-bearing for the CSNK2A1 to TOP2A correction (edge 10, override row C) because it is the paper SIGNOR cites for the UP-regulating Ser1525 row and it denies both the activity effect and the kinase: "we did not observe any marked difference in activity between Topo IIalpha[WT] and Topo IIalpha[S1524A], which suggests that Topo IIalpha phosphorylation at Ser 1524 does not have a major regulatory role in Topo IIalpha decatenation activity"; and "when cells were treated with either of the CK2 inhibitors 5,6-dichlorobenzimidazole riboside (DRB) or 4,5,6,7-tetrabromobenzotriazole (TBB), we did not observe any decrease in pSer 1524 (data not shown), suggesting that kinases other than CK2 may be responsible for Topo IIalpha Ser 1524 phosphorylation". The paper says Ser1524 where SIGNOR says Ser1525. PubMed dates this 21 December 2008; the journal issue is 2009, which is the year used here per the convention of commit 8ad304c}
}

@article{michalides2004tamoxifen,
  author  = {Michalides, Rob and Griekspoor, Alexander and Balkenende, Astrid and Verwoerd, Desiree and Janssen, Lennert and Jalink, Kees and Floore, Arno and Velds, Arno and van't Veer, Laura and Neefjes, Jacques},
  title   = {Tamoxifen resistance by a conformational arrest of the estrogen receptor alpha after {PKA} activation in breast cancer},
  journal = {Cancer Cell},
  year    = {2004},
  volume  = {5},
  number  = {6},
  pages   = {597--605},
  doi     = {10.1016/j.ccr.2004.05.016},
  pmid    = {15193262},
  note    = {ABSTRACT ONLY is held; no PMC body. The up-regulating Ser305 site of the PRKACA to ESR1 edge (edge 12), and the reason that edge is called context-dependent rather than corrected: the up-regulation is conditional on tamoxifen being present. "We show that phosphorylation of serine-305 in the hinge region of ERalpha by protein kinase A (PKA) induced resistance to tamoxifen"; "PKA activity thus induces a switch from antagonistic to agonistic effects of tamoxifen on ERalpha"; "Activation of PKA by downregulation of PKA-RIalpha converts tamoxifen from an ERalpha inhibitor into a growth stimulator, without any effect on ICI 182780 (Fulvestrant)"}
}

@article{chen1999phosphorylation,
  author  = {Chen, D and Pace, P E and Coombes, R C and Ali, S},
  title   = {Phosphorylation of human estrogen receptor alpha by protein kinase {A} regulates dimerization},
  journal = {Molecular and Cellular Biology},
  year    = {1999},
  volume  = {19},
  number  = {2},
  pages   = {1002--1015},
  doi     = {10.1128/MCB.19.2.1002},
  pmid    = {9891036},
  pmcid   = {PMC116031},
  note    = {ABSTRACT ONLY is held: the PMC body is empty in both Europe PMC (fullTextXML answered HTTP 500) and the PubMed MCP. The down-regulating Ser236 site of the PRKACA to ESR1 edge (edge 12), with the ligand condition that makes the edge context-dependent stated in the abstract itself: "ERalpha is phosphorylated by protein kinase A (PKA) on serine-236 within the DNA binding domain. Mutation of serine-236 to glutamic acid prevents DNA binding by inhibiting dimerization by ERalpha"; "PKA overexpression or activation of endogenous PKA inhibits dimerization in the absence of ligand. This inhibition is overcome by the addition of 17beta-estradiol or the partial agonist 4-hydroxy tamoxifen". Note the PubMed and Europe PMC records give the DOI in different letter case (10.1128/MCB.19.2.1002 and 10.1128/mcb.19.2.1002); the PubMed form is used}
}

@article{ozer2000phosphorylation,
  author  = {Ozer, R S and Halpain, S},
  title   = {Phosphorylation-dependent localization of microtubule-associated protein {MAP2c} to the actin cytoskeleton},
  journal = {Molecular Biology of the Cell},
  year    = {2000},
  volume  = {11},
  number  = {10},
  pages   = {3573--3587},
  doi     = {10.1091/mbc.11.10.3573},
  pmid    = {11029056},
  pmcid   = {PMC15014},
  note    = {ABSTRACT ONLY is held, and this is a stated limit of override row D: the PMC body is EMPTY in both Europe PMC (fullTextXML answered HTTP 500) and the PubMed MCP, and the publisher route is robots-disallowed, so the PRKACA to MAP2 correction (edge 13) rests on this abstract for PKA specifically. Its measured result is a disruption: "cAMP-dependent protein kinase activity disrupts the MAP2-microtubule interaction in living HeLa cells and promotes MAP2c localization to peripheral membrane ruffles enriched in actin"; "Biochemical and microscopy-based assays indicated that mutation of a single residue was adequate to disrupt the MAP2-microtubule interaction in HeLa cells"; and "Phosphorylation at two of these sites was detected in brain tissue". SIGNOR's single up-regulating row instead quotes the paper's speculative closing sentence about a different binding partner, "Specific phosphorylation states may enhance the interaction of MAP2 with the actin cytoskeleton, thereby providing a regulated mechanism for MAP2 function within distinct cytoskeletal domains". The experiments are in HeLa, not neurons}
}

@article{lopez1995microtubule,
  author  = {L{\'o}pez, L A and Sheetz, M P},
  title   = {A microtubule-associated protein ({MAP2}) kinase restores microtubule motility in embryonic brain},
  journal = {The Journal of Biological Chemistry},
  year    = {1995},
  volume  = {270},
  number  = {21},
  pages   = {12511--12517},
  doi     = {10.1074/jbc.270.21.12511},
  pmid    = {7759496},
  note    = {ABSTRACT ONLY is held: no PMC body, and jbc.org is robots-disallowed for experiments/read_public_page.py (recorded as a refusal on 7 November 2026). The second source for the direction of the PRKACA to MAP2 correction (edge 13, override row D), found by PubMed search after the primary paper's full text could not be read. IT DOES NOT CORROBORATE PKA SPECIFICALLY, which is stated in the override's reason: its kinase is explicitly "c-AMP independent". What it corroborates is that MAP2 phosphorylation detaches MAP2 from microtubules, in embryonic brain rather than HeLa: "The MAP2 inhibition is reversed by a kinase that is co-purified with chicken embryonic MAP2, completely releasing MAP2 from the microtubules"; "Only the phosphorylation produced by embryonic MAP2 kinase can change the affinity of MAP2 by microtubules. Bovine MAP2 kinase, Cdc2 kinase, mitogenic activated protein kinase, and the NIMA kinase are able to phosphorylate MAP2 but do not change the affinity for microtubules"}
}

@article{laulajainen2008protein,
  author  = {Laulajainen, M and Muranen, T and Carp{\'e}n, O and Gr{\"o}nholm, M},
  title   = {Protein kinase {A}-mediated phosphorylation of the {NF2} tumor suppressor protein merlin at serine 10 affects the actin cytoskeleton},
  journal = {Oncogene},
  year    = {2008},
  volume  = {27},
  number  = {23},
  pages   = {3233--3243},
  doi     = {10.1038/sj.onc.1210988},
  pmid    = {18071304},
  note    = {ABSTRACT ONLY is held; no PMC body. The single source SIGNOR gives for both rows of the PRKACA to NF2 edge (edge 14), left as is at inhibits. Its own finding is about actin rather than merlin's growth-suppressive activity, which is why the up-regulating Ser10 row does not outweigh Ser518: "we identify a novel PKA phosphorylation site, serine 10, in the N terminus of merlin"; "merlin S10A reduces the amount of cellular F-actin and merlin S10D stabilizes F-actin filaments"; "dephosphorylation of serine 10 leads to defects in migration". SIGNOR's down-regulating Ser518 row quotes this paper's introduction summarising others, so three independent second sources were read for that direction (PMIDs 11719502, 17891137, 25043298). PubMed dates this 10 December 2007; the journal issue is 2008, which is the year used here per the convention of commit 8ad304c}
}

@article{xiao2001p21,
  author  = {Xiao, Guang-Hui and Beeser, Alexander and Chernoff, Jonathan and Testa, Joseph R},
  title   = {p21-activated kinase links {Rac}/{Cdc42} signaling to merlin},
  journal = {The Journal of Biological Chemistry},
  year    = {2002},
  volume  = {277},
  number  = {2},
  pages   = {883--886},
  doi     = {10.1074/jbc.C100553200},
  pmid    = {11719502},
  note    = {ABSTRACT ONLY is held: no PMC body, and jbc.org is robots-disallowed for experiments/read_public_page.py (recorded as a refusal on 7 November 2026). The first of three second sources read for the direction of merlin Ser518 phosphorylation (edge 14), after SIGNOR's row was found to quote a secondary passage: "Pak can directly phosphorylate merlin at serine 518, a site that affects merlin activity and localization". PubMed dates this 21 November 2001; the journal issue is 2002, which is the year used here per the convention of commit 8ad304c}
}

@article{tang2007akt,
  author  = {Tang, Xiaoling and Jang, Sung-Wuk and Wang, Xuerong and Liu, Zhixue and Bahr, Scott M and Sun, Shi-Yong and Brat, Daniel and Gutmann, David H and Ye, Keqiang},
  title   = {{Akt} phosphorylation regulates the tumour-suppressor merlin through ubiquitination and degradation},
  journal = {Nature Cell Biology},
  year    = {2007},
  volume  = {9},
  number  = {10},
  pages   = {1199--1207},
  doi     = {10.1038/ncb1641},
  pmid    = {17891137},
  note    = {ABSTRACT ONLY is held; no PMC body. The second of three second sources for the direction of merlin Ser518 phosphorylation (edge 14), and the most explicit: "Merlin is partially regulated by phosphorylation of Ser 518, such that hyperphosphorylated merlin is inactive and fails to form productive intramolecular and intermolecular interactions"}
}

@article{guerrero2014oncogenic,
  author  = {Guerrero, P A and Yin, W and Camacho, L and Marchetti, D},
  title   = {Oncogenic role of {Merlin}/{NF2} in glioblastoma},
  journal = {Oncogene},
  year    = {2014},
  volume  = {34},
  number  = {20},
  pages   = {2621--2630},
  doi     = {10.1038/onc.2014.185},
  pmid    = {25043298},
  pmcid   = {PMC4302072},
  note    = {ABSTRACT ONLY is held; the PMC body was not retrieved. The third second source for the direction of merlin Ser518 phosphorylation (edge 14), treating phospho-Ser518 merlin as the oncogenic form: "high expression of phosphorylated Merlin at serine 518 (S518-Merlin), NOTCH1 and epidermal growth factor receptor (EGFR) correlated with increased cell proliferation and tumorigenesis"; "the phosphorylation of S518-Merlin in glioblastoma promotes oncogenic properties". The Europe PMC record gives volume 34, number 20, pages 2621-2630 against a PubMed publication date of 21 July 2014; the journal-issue year 2014 of the Europe PMC record is used per the convention of commit 8ad304c}
}

@article{sumandea2008tyrosine,
  author  = {Sumandea, Marius P and Rybin, Vitalyi O and Hinken, Aaron C and Wang, Chaojian and Kobayashi, Tomoyoshi and Harleton, Erin and Sievert, Gail and Balke, C William and Feinmark, Steven J and Solaro, R John and Steinberg, Susan F},
  title   = {Tyrosine phosphorylation modifies protein kinase {C} delta-dependent phosphorylation of cardiac troponin {I}},
  journal = {The Journal of Biological Chemistry},
  year    = {2008},
  volume  = {283},
  number  = {33},
  pages   = {22680--22689},
  doi     = {10.1074/jbc.M802396200},
  pmid    = {18550549},
  pmcid   = {PMC2504892},
  note    = {ABSTRACT ONLY is held: the PMC body is empty in both Europe PMC (fullTextXML answered HTTP 500) and the PubMed MCP, and jbc.org is robots-disallowed. The source for three of the four rows of the PRKCD to TNNI3 edge (edge 15), left as is at inhibits because BOTH sets of sites depress force in this paper, contrary to SIGNOR's up-regulating Ser23/Ser24 rows: "Treatment of detergent-extracted single cardiomyocytes with lipid-activated PKCdelta induces depressed tension at submaximum but not maximum [Ca2+] as expected for cTnI-Ser23/Ser24 phosphorylation"; "Treatment of myocytes with Src-activated PKCdelta leads to depressed maximum tension and cross-bridge kinetics, attributable to a dominant effect of cTnI-Thr144 phosphorylation". The paper writes Thr144 where SIGNOR maps Thr143}
}

@article{wijnker2014length,
  author  = {Wijnker, Paul J M and Sequeira, Vasco and Foster, D Brian and Li, Yuejin and Dos Remedios, Cristobal G and Murphy, Anne M and Stienen, Ger J M and van der Velden, Jolanda},
  title   = {Length-dependent activation is modulated by cardiac troponin {I} bisphosphorylation at {Ser23} and {Ser24} but not by {Thr143} phosphorylation},
  journal = {American Journal of Physiology. Heart and Circulatory Physiology},
  year    = {2014},
  volume  = {306},
  number  = {8},
  pages   = {H1171--H1181},
  doi     = {10.1152/ajpheart.00580.2013},
  pmid    = {24585778},
  pmcid   = {PMC3989756},
  note    = {ABSTRACT ONLY is held: the PMC body is empty in both Europe PMC (fullTextXML answered HTTP 500) and the PubMed MCP. The second source for the PRKCD to TNNI3 edge (edge 15), and it DISAGREES IN DIRECTION with Sumandea et al. 2008 on a different readout, which is recorded rather than resolved: "Pseudo-phosphorylation of Thr143 increased myofilament Ca2+ sensitivity compared with WT without affecting LDA in failing and donor cardiomyocytes", against Sumandea's depressed maximum tension. Ca2+ sensitivity up and maximum tension down do not reduce to one sign; v5's inhibits was left standing on the tension readout. Also the source of SIGNOR's second Thr143 down-regulating row. The page range is given as H1171-81 in both records and is expanded here}
}

@article{feng2013actinin,
  author  = {Feng, Yunfeng and Ngu, Hai and Alford, Shannon K and Ward, Michael and Yin, Frank and Longmore, Gregory D},
  title   = {alpha-actinin1 and 4 tyrosine phosphorylation is critical for stress fiber establishment, maintenance and focal adhesion maturation},
  journal = {Experimental Cell Research},
  year    = {2013},
  volume  = {319},
  number  = {8},
  pages   = {1124--1135},
  doi     = {10.1016/j.yexcr.2013.02.009},
  pmid    = {23454549},
  pmcid   = {PMC4142059},
  note    = {FULL TEXT held, read through the PubMed MCP's PMC full text (PMC4142059) on 7 November 2026 after Europe PMC's fullTextXML answered HTTP 500. The single source for all three rows of the PTK2 to ACTN4 edge (edge 16), left as is at activates. All three SIGNOR rows quote the paper's INTRODUCTION reviewing others ("Phosphorylation at y4 or y31 decreases its binding to actin while phosphorylation of y265 increases its affinity for actin"), whereas the paper's own result supports the positive site: "the tyrosine phosphorylation of alpha-actinin1 at Y12 and alpha-actinin4 at Y265 is critical for dorsal stress fiber establishment, transverse arc maintenance and focal adhesion maturation"; "the alpha-actinin4.Y265F mutant was not able to rescue either cytoskeletal defects". Two caveats from the body: "neither alpha-actinin4.Y265F nor Y265E could reconstitute subcellular localization of wt alpha-actinin4, it was obvious that alpha-actinin4.Y265E was not real phosphomimetic", and the FAK-attributed site in this paper is alpha-actinin1 Y12, not the alpha-actinin4 sites}
}
```
