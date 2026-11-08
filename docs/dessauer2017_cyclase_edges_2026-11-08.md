# Dessauer et al. 2017 (PMID 28255005), Q1/Q2 and the G-protein-to-cyclase edge table

Pass of 8 November 2026, on Fable. Extends `docs/label_source_review.md` section 43 (the full reading of
2 November 2026) and does not redo it.

## Status and next steps

**This pass is complete.** All of it was done on Fable; the model did not fall back. Nothing in the repository
was edited.

- [x] Read CLAUDE.md, decision 9.97 in full, `docs/label_source_review.md` sections 37, 40 and 43.
- [x] **Q1** - read section I.C (pp. 97-99), Table 3's legend (p. 112), p. 113 and section IV.A (p. 119).
      **Verdict: the claim holds with qualifications for admitting a positive and does NOT hold for removing an
      edge**, and it wrongly merges two tiers the review keeps apart (purified/cell-free = "direct"; intact
      cell/transfected = weaker). So the owner's conditional acceptance is not triggered in the removing direction.
      This agrees with their independent ruling of 2 November 2026.
- [x] **Q2a** - G beta gamma per isoform, from Table 3 (p. 112), the prose of II.D (p. 112), p. 111 (AC7) and p. 101.
- [x] **Q2b** - **no resting-Gs weight found after four sources.** What exists and could be adapted is recorded,
      with its cost.
- [x] Edge-by-edge table for all 63 `g_alpha_regulates_effector` edges plus the GNG2 edge, with a proposal each.
- [x] GNG2-into-ADCY5: **remove**, and the removal does not depend on Q1's failing direction.
- [x] GNAL per isoform: **two edges newly supported** (ADCY3, ADCY5) on native-tissue evidence found outside the
      two reviews; the other seven unsourced. This corrects sections 40 and 43, which both said GNAL was supported
      in neither direction.
- [x] Licence verified three ways: quotation only.
- [x] BibTeX entry drafted (`dessauer2017iuphar` is absent from `docs/references.bib`).
- [x] Text addressed to an AI: **none in the PDF**; the PubMed and Consensus connectors each carried one, reported
      and not acted on.

### Three things for the owner that are new and are not in section 43

1. **ADCY9 and Gs.** D17's universal "ACs 1-9 are activated by Gαs" is unreferenced for AC9 (all three of its
   citations predate AC9's cloning), and the one direct test found contradicts it: Chen and Antoni 2023
   (PMID 36657828) report that AC9 "is not regulated by heterotrimeric G proteins". Transfected, so it cannot
   remove the edge alone - but the edge it contradicts has no reference either.
2. **GNAO1 into ADCY2/5/6** is the strongest removal case in the table: three stated negatives and **no positive
   from any source**, unlike Gi-into-AC2, which has a contrary positive. The 2 November ruling was framed against
   the case that had one. Worth a separate question.
3. **GNAL in a neuronal graph.** In striatum, Golf and not Gs is the stimulatory subunit - "striatonigral neurons
   contain high levels of G(olf) alpha and little, if any, Gs alpha" (Hervé et al. 1993) - and the cyclase there is
   AC5 by knockout (D17 p. 116). This bears on more than one row.

## Pin

`data/raw/supplied_papers/pmid28255005_dessauer2017.pdf`, re-supplied 8 November 2026, SHA-256
`ceec84560bec5f6d2c189ce7df4b8318494dd2db3cbb168fad49e8baaab73e8b`, 3,743,366 bytes, 47 pages. A different download
of the same article than the copy read on 2 November 2026 (SHA-256 `3c35fb0f...`), so quotations and page numbers
from section 43 stand. PDF-to-printed offset 92 (PDF page 1 = printed p. 93).

## Q1. Are reconstituted or transfected systems "the standard test" of direct G-protein action on a cyclase?

Read on Fable on 8 November 2026 from the pinned PDF: section I.C "Model Systems for Adenylyl Cyclase Analysis"
(pp. 97-99, comprising I.C.1 "From Organs to Purified Adenylyl Cyclases", I.C.2 "Studies with Purified C1 and C2
Subunits" and I.C.3 "Methodological Aspects"), plus Table 3's legend (p. 112) and p. 113.

### The one sentence that most directly answers the question: Table 3's own legend

> "This table focuses on known direct regulators of AC, although there are indirect routes to altering AC activity.
> Some of the effects listed have been clearly demonstrated as 'direct' using purified, cell free components, whereas
> others have only been shown in intact cells. In the case of the latter, one must consider indirect mechanisms as
> well as the requirement for other factors for the effect to be realized." (Table 3 legend, p. 112)

So the review's own criterion for **direct** is "purified, cell free components" - i.e. purified protein or
reconstituted membranes. Intact cells (which is what a transfected HEK/COS experiment is) are explicitly the weaker
category, demoted in the same sentence by two named confounds: indirect mechanisms, and a requirement for other
factors. **Purified/reconstituted and transfected are therefore not one tier in this review; they are two, and only
the first is what the review calls direct.**

### The systems, in the review's order, with the limit it states for each

1. **Crude organ membranes.** "Research on ACs started with crude organ membrane fractions (Rall and Sutherland,
   1958; Sutherland et al., 1962)... Although organ membranes contain numerous AC isoforms, this system is relatively
   close to the physiologic situation." (p. 97) - the most physiological, but **isoform-ambiguous**, so it cannot
   assign an effect to an isoform on its own.
2. **Native cells / cell lines.** "Studies with membranes from native cells such as platelets ... or cultured cells
   such as neuroblastoma cells ... also yielded most valuable insights into the mechanisms of AC regulation. Of
   particular importance in this regard are the S49 lymphoma wild-type cells and the Gαs-deficient cyc- cells" (p. 97).
   Same isoform ambiguity.
3. **Knockout and transgenic mice.** "Experiments with native organs have been successfully complemented with gene
   knockout studies and transgene overexpression studies in mice (Ferguson and Storm, 2004; Sadana and Dessauer,
   2009)." (p. 97) And, decisively, at p. 113: "**AC isoform knockout serves as the most reliable tool for
   understanding the contribution of individual ACs to a given cell's signaling repertoire.**"
4. **Purified holoenzyme.** "purification of functionally and structurally intact GPCRs ... and particularly mACs
   turned out to be much more difficult because of their very low abundance and conformational and thermal
   instability under the conditions used for purification" (p. 97). So the purified full-length enzyme is the hardest
   route and is little used.
5. **HEK293 overexpression.** "ACs can be overexpressed in mammalian cells, HEK293 cells being a very popular model
   system (Jacobowitz et al., 1994). **One should keep in mind that HEK293 cells endogenously express several mACs,
   providing background activity** (Atwood et al., 2011; Yu et al., 2014)." (p. 97)
6. **Sf9 overexpression (the system of Taussig et al. 1994).** "ACs can also be effectively overexpressed in
   Spodoptera frugiperda Sf9 cells (Taussig et al., 1994b). Although few studies have been performed with ACs
   purified from Sf9 cells (Taussig et al., 1993a,b), **most studies are conducted with crude Sf9 membranes
   overexpressing a given AC isoform**, increasing stability of the enzymes and facilitating the execution of
   extensive pharmacological studies... **Again, the background activity of the endogenous membrane AC of Sf9 cells
   needs to be properly considered in overexpression studies** (Pinto et al., 2008). Like mammalian mACs, the
   membrane AC of Sf9 cells is potently inhibited by MANT ... nucleotides ... and effectively activated by FSK"
   (p. 97) - i.e. the insect-cell background enzyme is itself regulable, so it is not an inert baseline.
7. **Purified C1:C2 (the soluble catalytic core).** "Expression in Escherichia coli of a fusion protein of parts of
   the C1 and C2 domains of ACs 1 and 2 ... resulted in a FSK- and Gαs-stimulated enzyme (Tang and Gilman, 1995).
   This landmark study showed that for the essential aspects of catalysis and regulation, the transmembrane domains
   are dispensable" (p. 97). Its limits are stated twice and they are **fatal to isoform-specific claims**:
   > "**However, it should be kept in mind that this system constitutes a hybrid with subunits from different AC
   > isoforms so that it can serve just as a model for mACs in general.**" (p. 98)
   > "The most widely used purified mAC system is 5C1(dog):2C2(rat) (Table 1). The high conservation of the catalytic
   > domains between dog and rat tempers concerns regarding the use of proteins from different species, but
   > **regulation and interactions with the N terminus is missing in this system** (Gao et al., 2007)." (p. 98)
   Single-isoform C1:C2 exists for ACs 2, 5, 7 and 9, but "functionality of these systems seems to be very dependent
   on the specific length of the expressed subunit" (p. 98).
8. **Intact-cell cAMP assays (transfection).** "In most studies, AC activity is assessed in intact cells... However,
   **formally, intact cell assays do not reflect AC activity assays but constitute cAMP accumulation assays. In
   intact cell assays, the ATP substrate concentration for ACs cannot be readily controlled.**" cAMP is also exported
   by MRP4/5, and the PDE and MRP inhibitors used are unspecific, so "**caution must be exerted when interpreting the
   results of intact-cell studies with PDE- and MRP inhibitors**" (p. 99).

### The cell-free systems have their own named artefact, and it points at Gi specifically

> "A highly important variable in AC assays with cell-free preparations is the choice of the particular divalent
> cation, Mg2+ or Mn2+. In general, with Mn2+, higher catalytic activities than with Mg2+ are obtained ... Moreover,
> **Mn2+ can functionally uncouple AC from Gi-proteins** (Hildebrandt et al., 1982; Jakobs et al., 1983a,b; Dessauer
> et al., 2002; Gille and Seifert, 2003) **and alter basal AC activities** (Pieroni et al., 1995). Although Mg2+ is
> usually assumed to be the physiologic cation of catalysis (Ross et al., 1978), indirect evidence points to a role
> of Mn2+ as cation for catalysis, at least for sAC" (p. 98)

This is a named mechanism by which a cell-free assay can produce a **false negative for Gi inhibition specifically**,
which is exactly the class of result (the stated negatives of Sunahara 1996 and of Table 3's "not AC2") that Q1 asks
whether to act on. It is restated at p. 113: "Defining this is a challenge given that Mg2+ and Mn2+ levels cause
sizable changes in AC activity and that isoforms may have varying sensitivities to both Gαs and FSK."

### Verdict on the Q1 claim

The session's claim was: *reconstituted or transfected systems are the standard test of whether a G protein acts
directly on a cyclase isoform, so insensitivity shown there is enough to remove an edge.*

**It holds in its first half and fails in its second, and it wrongly joins two tiers the review keeps apart.**

- **Holds:** reconstitution with purified, cell-free components *is* the review's criterion for calling a regulator
  "direct" (Table 3 legend, p. 112), and for Gαs it is explicitly the standard: Sunahara 1996 p. 468, "The majority
  of these studies have been performed by reconstitution of membranes from cells expressing defined subtypes of the
  enzyme with activated (GTPγS-bound) Gsα" (section 40). Dessauer 2017 does not contradict that.
- **Fails, first:** *transfected* is not in that tier. The same legend separates "only been shown in intact cells"
  and tells the reader to consider "indirect mechanisms as well as the requirement for other factors". p. 99 adds
  that an intact-cell assay is not an AC-activity assay at all but a cAMP-accumulation assay with uncontrolled ATP
  and cAMP export. So a transfected negative is the weakest evidence the review names, not a standard test.
- **Fails, second and decisively for the inference Q1 was asked to license:** *being the standard test for a positive
  does not make insensitivity in it sufficient for a negative.* The review names an artefact that removes Gi coupling
  in cell-free assays (Mn2+, p. 98), endogenous background AC in both HEK293 and Sf9 (p. 97), the loss of the N
  terminus and of isoform identity in the most-used purified system (p. 98), and it says the **knockout**, not the
  reconstitution, is "the most reliable tool" (p. 113). Sunahara 1996 applies that same scepticism to a transfected
  negative in terms - "we view as premature claims that type I (or other) adenylyl cyclase is not responsive to Gsα
  in vivo" (pp. 468-469, section 40) - and Taussig 1994 applies it to its own negative, "it is conceivable that Giα
  might inhibit type II adenylyl cyclase under some condition not tested in the present experiments" (p. 6100,
  section 37).

**So: the claim holds with qualifications for admitting a positive, and does not hold for removing an edge.** The
owner's conditional acceptance in Q1 ("if that's the standard test then I accept it") is therefore not triggered in
the direction that would remove edges. This agrees with, and now has the IUPHAR review's own methodological section
behind it, the owner's independent ruling of 2 November 2026 under 9.97: "transfected and reconstituted cases are too
weak of evidence to stand alone". **No edge is removed on a reconstituted or transfected negative by this pass.**

What *would* meet the review's own standard for a negative: an isoform knockout (p. 113), or a negative in a
near-physiological preparation ("organ membranes ... relatively close to the physiologic situation", p. 97) in which
the isoform's identity is established by other means.

### Two further Q1 passages found on 8 November, in section IV.A (p. 119)

The review states the systems question again, this time as advice to the reader, and it is the clearest statement in
the paper of what each system can and cannot settle:

> "One important parameter when evaluating reports of AC-specific modulators is the system that was used. As noted in
> section I.C.3, a variety of methodologies are routinely used to assess AC activity, and two common approaches use
> either cellular membranes or intact cell preparations from cells overexpressing individual AC isoforms. The assays
> are biologically distinct (see section I.C.3) and have advantages and disadvantages that are important to consider
> when evaluating published reports. **Studies with cell membranes can provide important mechanistic insight (i.e.,
> direct versus indirect, competitive versus noncompetitive) and AC isoform specificity information (particularly
> when Sf9 membranes expressing a given AC isoform); however, the assays are generally of low throughput** (Brand
> et al., 2013). **Intact cell studies are well suited for high-throughput studies but provide only limited
> information regarding modulator mechanism.**" (p. 119)

> "Advantages of intact cell studies include a more native cellular environment, and presumably only cell permeable
> modulators will be active. **However, counterscreening against other AC isoforms and studies examining the
> potential role of G proteins (e.g., pertussis toxin treatment and sequestering Gβγ subunits) are important
> considerations for intact cell studies.** The results of intact cell studies can further be strengthened and
> supported by additional studies using cell membranes. **Ultimately, one would like confirmation that
> pharmacological inhibition and genetic inhibition give rise to similar results.**" (p. 119)

These two passages are the strongest support in the paper for the first half of the Q1 claim (membranes = the system
that establishes directness and isoform specificity) and, in the last sentence, the strongest statement that the
reconstituted result is not the end of the chain: genetic confirmation is wanted. They do not say insensitivity in
such a system is sufficient to deny an interaction; the review never addresses the negative direction at all.

----

## Q2a. G beta gamma per isoform, as Dessauer 2017 states it

### Table 3 (p. 112), the two Gβγ rows, verbatim

| Regulator | Effect | AC Isoform | References |
|---|---|---|---|
| Gβγ | Inhibition | AC1, AC3, AC8 | Taussig et al. (1993b); Diel et al. (2006) |
| Gβγ | Stimulation (conditional) | AC2, AC4, AC5, AC6 | Tang and Gilman (1991); Gao and Gilman (1991); Thomas and Hoffman (1996); Gao et al. (2007); Brand et al. (2015) |

(Quoted as text, not reproduced as a table in any committed file - the licence is quotation-only.)
**AC7 and AC9 appear in neither row.**

### The prose of section II.D (p. 112), verbatim

> "Gβγ subunits increase the activity of ACs 2 and 4 (Gao and Gilman, 1991; Tang and Gilman, 1991; Taussig et al.,
> 1993b). **The stimulatory effects of Gβγ typically require the presence of another activator such as Gαs or FSK**
> (Tang and Gilman, 1991). When overexpressed, Gβγ subunits have been reported to inhibit ACs 5 and 6 (Bayewitch
> et al., 1998). However, cellular and in vitro assays using purified proteins display a conditional stimulation of
> AC5 and AC6 by Gβγ (Gao et al., 2007; Thomas and Hoffman, 1996) that involves different structural determinants in
> AC5 compared with AC6 (Brand et al., 2015)." (p. 112)

Note the word **"typically"**: the conditionality is stated as the usual case, not as an exceptionless rule, and the
condition is disjunctive - "Gαs **or** FSK". Compare Taussig 1994, which for AC2 found the opposite about FSK:
"stimulating activity dramatically in the presence of Gsα (but not forskolin)" (p. 6099, section 37). So the review
generalises a condition that its own primary source states more narrowly. For the Q2 weighting this matters: on
Taussig's primary result the AC2 condition is Gsα specifically, which is the conjunction the owner's option 4
linearises; on the review's wording any activator will do.

### AC7, in prose only, direction given only by context

> "Activation of prostaglandin EP1 receptors facilitates dopamine D1 receptor activation of cAMP production (Ehrlich
> et al., 2013). This effect depends on Gβγ signaling and expression of **AC7, a Gβγ-sensitive isoform**, and may
> explain how prostaglandin E2 can regulate neuronal dopamine signaling." (p. 111)

"Gβγ-sensitive" names no sign; the sentence it sits in is about *facilitation* of D1-stimulated cAMP, i.e. positive,
and D1 is a Gs-coupled receptor, so the context is Gβγ raising a Gs-driven response - the same conditional shape as
AC2/AC4. Ehrlich et al. 2013 is a transfected HEK293T study (its title ends "in human embryonic kidney 293T cells",
section 43). Table 3 omits AC7 from both Gβγ rows, so the review does not carry this into its own summary.

### AC9: nothing. Gβγ is not stated for AC9 anywhere in the 47 pages.

### One more Gβγ statement, structural (p. 101)

> "The exceptionally long insert in 2C2 between β3' and α3' is not fully resolved in 5C1:2C2 structures and probably
> involved in interactions with Gβγ (Chen et al., 1995), **a characteristic modulator of AC2**." (p. 101)

A structural corroboration that the AC2-Gβγ interaction is direct and on the catalytic core.

### Per-isoform summary of Gβγ in this review

| Isoform | Dessauer 2017 | Conditional on Gs? | System |
|---|---|---|---|
| AC1 | Inhibition (Table 3) | No condition stated | Taussig 1993b purified/Sf9; Diel 2006 |
| AC2 | Stimulation, conditional (Table 3; p. 112) | Yes - "Gαs or FSK" (p. 112); Taussig 1994 says Gsα but **not** forskolin (p. 6099) | Purified/reconstituted; structure p. 101 |
| AC3 | Inhibition (Table 3) | No condition stated | Diel et al. 2006, "Adenylyl cyclase type III is inhibited by Gβγ", J Biol Chem 281:288-294 |
| AC4 | Stimulation, conditional (Table 3; p. 112) | Yes | Purified/reconstituted |
| AC5 | Stimulation, conditional (Table 3; p. 112) | Yes | "cellular and in vitro assays using purified proteins" (p. 112); an overexpression report of *inhibition* (Bayewitch 1998) treated as superseded |
| AC6 | Stimulation, conditional (Table 3; p. 112) | Yes | As AC5; different structural determinants (Brand et al. 2015) |
| AC7 | "a Gβγ-sensitive isoform" (p. 111), sign implied positive by context; **absent from Table 3** | Implied (facilitates a Gs-coupled D1 response) | Transfected HEK293T (Ehrlich et al. 2013) |
| AC8 | Inhibition (Table 3) | No condition stated | Taussig 1993b; Diel 2006 |
| AC9 | Not stated anywhere | - | - |

### Reconciliation with Sunahara 1996 (section 40) on Gβγ

- **AC1, AC2, AC4:** the two reviews agree (AC1 inhibited; AC2 and AC4 conditionally stimulated, "dependent on
  coincidental activation by Gsα", Sunahara p. 469).
- **AC3:** Dessauer 2017 adds an inhibition Sunahara did not carry, on a primary paper (Diel et al. 2006).
- **AC8:** Sunahara had "perhaps VIII" (p. 475); Dessauer 2017 carries AC8 inhibition without the hedge.
- **AC5 and AC6: the two reviews contradict each other outright.** Sunahara 1996: "βγ has no effect on the type V or
  type VI enzyme" (p. 471) and Table 2 "not ACV, VI" (p. 468). Dessauer 2017: conditional **stimulation** of AC5 and
  AC6 (Table 3; p. 112), on later work (Thomas and Hoffman 1996; Gao et al. 2007; Brand et al. 2015). Dessauer 2017
  is the later review and names the primary papers, so it supersedes. **Neither supports inhibition of AC5 by Gβγ
  except the single overexpression report (Bayewitch et al. 1998) that Dessauer 2017 explicitly sets aside.**
- **AC7:** Sunahara marked it "VII unknown" (p. 473); Dessauer 2017 adds the prose line only.
- **AC9:** both silent.

----

## Q2b. A resting or basal Gs weight: what exists, after four sources

The owner's option 4 linearises the Gβγ conjunction at the resting operating point, so the weight wanted is the
resting fraction of active Gsα (in neurons), or a basal cyclase activity relative to Gs-stimulated activity.

**No such number was found.** Sources tried, in order:

1. **Dessauer et al. 2017 itself** (all 47 pages searched for "basal", "constitutive", "resting"). It gives basal
   activity *per isoform* but never relative to Gs, and never a fraction of Gs in the active state:
   > "Regulation differences aside, mAC isoforms also differ in their basal and maximal activities. For example AC2
   > has a 10- to 15-fold higher basal activity compared with AC6, although FSK-stimulated activities only differ
   > twofold (Pieroni et al., 1995)." (p. 113)
   > "Studies with purified AC1 and AC2 suggest FSK-stimulated AC1 activity is ~3.5 times higher than AC2, with a
   > turnover number of ~15 per second (Taussig et al., 1993b). AC5 has even higher activity with a FSK/PKC-
   > stimulated turnover number of 59 second-1 (Kawabe et al., 1994). This compares favorably with the **Gαs- and
   > Gαs/FSK-stimulated 5C1:2C2 turnover numbers of 30 and 100 second-1**, respectively (Dessauer et al., 1997)."
   > (p. 113)
   > "AC2 is characterized by a high degree of ligand-independent constitutive activity (Pieroni et al., 1995; Pinto
   > et al., 2008)." (p. 121)
   The one Gs-referenced pair (30 vs 100 s-1) is Gsα versus Gsα-plus-FSK on the **hybrid 5C1:2C2**, not basal versus
   Gs, and the hybrid is "just as a model for mACs in general" (p. 98). So the review gives no usable weight.
2. **Pieroni et al. 1995**, the primary source behind p. 113 (PMID 7673172, doi 10.1074/jbc.270.36.21368,
   J Biol Chem 270:21368-73, "Distinct characteristics of the basal activities of adenylyl cyclases 2 and 6"; record
   and abstract read on PubMed, 8 November 2026). Its abstract gives basal-versus-**forskolin** ratios, per isoform,
   in Sf9 membranes: "Forskolin stimulated AC6 greater than 40-fold at 0.5-2 mM Mg2+, whereas AC2 was stimulated
   4-6-fold. At 20 mM Mg2+, AC2 was stimulated 2-fold by forskolin, whereas AC6 was stimulated 18-fold", with basal
   Vmax 281 (AC2) against 11 (AC6) pmol/mg/min at 20 mM Mg2+. **Forskolin is not Gs**, the Mg2+ dependence is the
   paper's own point ("due to differential regulation by Mg2+ ions rather than intrinsic catalytic capabilities"),
   and the system is overexpressing insect-cell membranes - the tier Dessauer 2017 warns carries its own background
   AC (p. 97). So this is a basal-to-stimulated ratio, but not the one the weight needs, and not in neurons.
3. **A PubMed search** for a resting/basal activated fraction of Gsα in brain or neurons (8 November 2026): no
   record. The nearest results concern Gsα abundance and turnover, not its activated fraction - e.g. Levis and
   Bourne 1992 (J Cell Biol 119:1297) measures degradation and membrane avidity of activated αs, not a resting
   fraction.
4. **A Consensus search** over the peer-reviewed corpus, twice (resting active-Gsα fraction in neurons; basal AC
   activity as a percentage of Gs-stimulated in brain membranes). The brain-membrane literature reports basal and
   GTPγS- or GppNHp-stimulated activities **side by side but as separate assay values**, without reporting the
   resting *in vivo* ratio: e.g. Young et al. 1993 (Neurochem Int, doi 10.1016/0197-0186(93)90057-c), "Although
   basal adenylyl cyclase activity was similar in all regions, GTPγS-stimulated adenylyl cyclase activity and
   forskolin-stimulated activity showed specific brain regional patterns". A GTPγS-stimulated value is a maximal,
   non-hydrolysable-analogue value, not the resting operating point, so it cannot set the weight either. The closest
   statement found to a resting activated fraction of any Gα in brain is for **Go, not Gs**, and is qualitative:
   "the vast majority of Gαo in the brain is in its inactive, GDP-bound form" (Yadav et al. 2025, PLOS One,
   doi 10.1371/journal.pone.0337998).

**Conclusion: none found after four sources.** Reported as absence under the owner's rule of 15 October 2026, with
the sources named. What exists and could be *adapted*, with its cost stated:

- The **basal-to-forskolin** ratio per isoform (Pieroni 1995, via Dessauer 2017 p. 113) is the only per-isoform
  number of the right shape. Using it as the Gs weight substitutes forskolin for Gsα; the review itself says the two
  are not interchangeable at AC9 ("ACs 1-8, but not AC9, are activated by FSK", p. 119) and are synergistic rather
  than equivalent elsewhere ("There is marked synergism between Gαs and FSK with respect to increasing Vmax of
  catalysis", p. 119). That is a numerical convenience, not the physiological quantity, so under CLAUDE.md
  "Modelling" it needs a stated justification recorded with the decision.
- A **single global weight** (one resting-Gs scalar for all isoforms) would avoid claiming a per-isoform number the
  sources do not support, at the cost of flattening the 10- to 15-fold per-isoform basal spread the review states.

**A separate finding that bears on the weight's shape.** The Gβγ edges do not all need it. Table 3's *inhibition*
row (AC1, AC3, AC8) carries no Gs condition in either review - Sunahara calls βγ "a reasonably potent and very
efficacious inhibitor of type I adenylyl cyclase ... the effect of beta-gamma appears to be exerted directly on the
enzyme" (p. 469, section 40). So only the **conditional stimulation** edges (AC2, AC4, AC5, AC6, and AC7 by the
prose line) are a conjunction needing the resting-Gs weight; the three inhibitory edges are plain negative edges at
full weight. Linearising all seven at a resting-Gs weight would be wrong for three of them.

----

## The edge-by-edge table: ADCY1-9 against GNAS, GNAL, GNAI1/2/3, GNAO1, GNAZ, Gbetagamma

Sources, by their short names below: **D17** = Dessauer et al. 2017 (this pass and section 43); **S96** = Sunahara,
Dessauer and Gilman 1996 (section 40); **T94** = Taussig et al. 1994 (section 37); **CI93** = Chen and Iyengar 1993
(PMID 8389756, abstract only, full text still unread); **CA23** = Chen and Antoni 2023 (PMID 36657828); **H93** =
Hervé et al. 1993 (PMID 8478697); **Dr91** = Drinnan et al. 1991 (PMID 19912784).

Baseline, as 9.97 records it on v5: 9 GNAS + 9 GNAL stimulatory, 45 GNAI1/2/3/GNAO1/GNAZ inhibitory = 63
`g_alpha_regulates_effector` edges, plus GNG2 into ADCY5 as `inhibits`.

### GNAS (Gαs) -> ADCY1-9, 9 edges: KEEP all 9, one flagged

D17 states the universal three times: "ACs 1-9 are activated by Gαs, and ACs 1-8 are also activated by FSK" (p. 99);
"All mACs are activated by Gαs (Tang and Gilman, 1992; Iyengar, 1993; Jones et al., 1990)" (p. 112); Table 3 "Gαs |
Stimulation | All isoforms | Iyengar (1993)". S96 p. 468: "All eight of the mammalian adenylyl cyclases
characterized thus far can be stimulated directly by Gsα", with the system named - "The majority of these studies
have been performed by reconstitution of membranes from cells expressing defined subtypes of the enzyme with
activated (GTPγS-bound) Gsα" (p. 468). Reconstituted positive, the tier Q1 confirms as the standard test.

**Proposal: keep all 9.** Rests on D17 + S96; depends on Q1 in the positive direction, which holds.

**ADCY9, flagged.** Two things are wrong with the universal at AC9. (a) All three of D17's references predate AC9's
cloning (Premont et al. 1996), so for AC9 the universal is asserted, not evidenced (section 43). (b) A direct test
found this pass contradicts it: **CA23**, "Human transmembrane adenylyl cyclase 9 (AC9) is not regulated by
heterotrimeric G proteins. Key to the resistance to stimulation by Gs-coupled receptors (GsRs) is auto-inhibition by
the COOH-terminal domain (C2b)... AC9 appears to be tailored to support constitutive activation of cyclic AMP
effector systems." (abstract, Life Sci Alliance 6(4):e202201791, doi 10.26508/lsa.202201791, read on PubMed
8 November 2026; peer reviewed; full text not yet read). The system is HEK293FT with a GloSensor reporter - an
intact-cell cAMP-accumulation assay, the weakest tier under Q1 - so under the owner's ruling of 2 November 2026 it
**cannot remove the edge alone**. But it is the only direct test of Gs on AC9 found in any source, and it is
negative, against an unreferenced universal. **Recommended: keep, flag the row, and put the question to the owner
separately.** This is new and is not in section 43.

### GNAL (Gαolf) -> ADCY1-9, 9 edges: 2 newly supported, 7 unsourced

Section 40 and section 43 both concluded "GNAL is not supported in either direction". **That stands for the reviews
and is now partly superseded by native-tissue evidence found outside them.**

- **GNAL -> ADCY3.** D17, native olfactory tissue: "Odorants interact with GPCRs to stimulate AC via activation of
  the G-protein Gαolf. All components of this signaling system, including AC3, are located within olfactory cilia
  (Wang and Storm, 2003). Deletion of AC3 leads to major defects in odorant-induced signaling" (p. 115), and "Key
  components of the olfactory signal transduction machinery (olfactory receptors, AC3, and Gαolf) are expressed in
  the distal nephron (Pluznick et al., 2009)" (p. 115). Colocalisation in native cilia plus an AC3 knockout
  phenotype in the Gαolf-driven pathway. **Proposal: keep, cite D17 p. 115, mark the support as native-tissue
  pathway evidence (indirect: no Gαolf-on-AC3 reconstitution exists in any source read).**
- **GNAL -> ADCY5.** A two-step native argument, neither step from D17's Table 3:
  (i) **H93**, native rat striatum: "striatonigral neurons contain high levels of G(olf) alpha and little, if any,
  Gs alpha, suggesting that the coupling of D1 receptor to adenylyl cyclase is provided by G(olf) alpha" (abstract,
  J Neurosci 13:2237-48, doi 10.1523/JNEUROSCI.13-05-02237.1993); corroborated by **Dr91**, "in the striatum,
  G(olf) transcripts are approximately 10-fold more abundant than G(salpha) transcripts. Thus G(olf) is not an
  olfactory neuron-specific G protein. It is also the major stimulatory G protein in the basal ganglia, where it may
  couple D1 dopamine receptors to adenylyl cyclase" (abstract, Mol Cell Neurosci 2:66-70,
  doi 10.1016/1044-7431(91)90040-u). Both read on PubMed, 8 November 2026; both peer reviewed.
  (ii) **D17**, the knockout that names the isoform: "Dopamine D1 receptor and D2 receptor signaling to AC is
  abolished in striatum upon knockout of AC5" (p. 116).
  Together: in native striatum the stimulatory G protein on the D1-to-cyclase step is Golf, and the cyclase is AC5
  by knockout - the tool D17 itself calls "the most reliable tool" (p. 113). **This is the only G-protein-to-cyclase
  edge in the whole table with native-tissue and knockout support**, and it is stronger evidence than the
  reconstituted Gi results. **Proposal: keep, cite H93 + Dr91 + D17 p. 116, mark the support as native-tissue plus
  isoform knockout (indirect: the two steps are in different papers, and no Golf-on-AC5 reconstitution was found).**
  This is relevant to the project beyond this row: the graph is neuronal, and in striatum Golf, not Gs, is the
  stimulatory subunit.
- **GNAL -> ADCY1, 2, 4, 6, 7, 8, 9 (7 edges).** No source read tests Gαolf on these. S96 names Golf once, as "an
  olfactory form of Gsα" (p. 463), on no cyclase; D17 names it only with AC3. **Proposal: mark unsourced under
  9.99's rule.** Does not depend on Q1.

### GNAI1, GNAI2, GNAI3 (Gαi) -> ADCY1-9, 27 edges

Neither review divides Gαi1/2/3 (D17's Table 3 row is undivided; section 43). The per-subunit resolution exists only
in **T94**, whose subunits were Giα1, Giα2, Giα3, Goα, Gqα (section 37). So for ADCY1/5/6 the per-subunit edges are
genuinely supported; elsewhere the reviews speak only of "Gαi".

| Target | D17 | S96 | Other | Proposal | Depends on Q1? |
|---|---|---|---|---|---|
| ADCY1 (×3) | Table 3 "Gαi \| Inhibition \| AC1, AC5, AC6"; "Only ACs 1, 5, and 6 are directly inhibited by Gαi" (p. 112) | "ACI, V, VI" (Table 2, p. 468) | T94, purified/reconstituted, per subunit | **Keep (3)**, supported | Yes, positive direction - holds |
| ADCY5 (×3) | as above | as above | T94; Giα inhibition of AC5 weakens as Gsα rises (Fig. 8, p. 6097) | **Keep (3)**, supported | Yes, positive - holds |
| ADCY6 (×3) | as above | as above | T94 (canine AC6); CI93 reports Gi2α inhibition of type 6 in transfection | **Keep (3)**, supported | Yes, positive - holds |
| ADCY2 (×3) | Table 3 "not AC2"; "Only ACs 1, 5, and 6" (p. 112), no hedge | "not ACII" (Table 2) | T94's own hedge, "it is conceivable that Giα might inhibit type II adenylyl cyclase under some condition not tested" (p. 6100); **CI93 reports the opposite**, "50-60% inhibition of hCG-stimulated cAMP accumulation of the type 2 adenylyl cyclase" by Q205LGi2-alpha | **Keep (3)**, flagged contradicted-but-not-removable | **Yes, and decisively**: removal was the Q1 question; Q1 does not hold for removal, so they stay |
| ADCY3 (×3) | not addressed; covered only by the unreferenced "Only" | not addressed | **CI93**: "hCG stimulation of types 3 and 6 adenylyl cyclases was also extensively inhibited by co-transfection with the Q205LGi2-alpha cDNA" | **GNAI2 -> ADCY3: keep (1), weakly sourced** (one transfected positive, full text unread). **GNAI1, GNAI3 -> ADCY3: mark unsourced (2)** | No |
| ADCY4, ADCY7, ADCY8, ADCY9 (×3 each = 12) | not addressed; "Only ACs 1, 5, and 6" is unreferenced for them | not addressed (S96's Table 2 has no AC7 or AC9 at all) | none found | **Mark unsourced (12)** under 9.99 | No |

A note on D17's "Only". Read strictly it is a negative for AC3, AC4, AC7, AC8 and AC9 as well as AC2. But it carries
no reference for any of them (section 43), and D17 is the Gilman laboratory's own reconstituted result restated with
Taussig's hedge removed, not an independent source. Under Q1 an unreferenced universal negative in a review is
weaker still than the reconstituted negative it generalises, so it removes nothing.

### GNAO1 (Gαo) -> ADCY1-9, 9 edges

**D17 contributes nothing here**: Table 3 has no Gαo row and Gαo appears only in the abbreviations list with no
cyclase role (section 43). The evidence is S96 and T94 alone.

| Target | Evidence | Proposal | Depends on Q1? |
|---|---|---|---|
| ADCY1 | S96 Table 2 "ACI"; "type I is uniquely (although not dramatically) inhibited by Goα" (p. 475); T94, AC1 is "the only form of adenylyl cyclase studied to date that can be inhibited by Goα" (p. 6096) | **Keep (1)**, supported | Yes, positive - holds |
| ADCY2 | S96 Table 2 "not ACII"; CI93, GTPase-deficient Go1α did not inhibit type 2 in co-transfected COS-7 | **Keep (1)**, flagged contradicted | Yes - Q1 keeps it |
| ADCY5, ADCY6 | S96 Table 2 "not ACV, VI"; T94, "Goα has no obvious effect on types V or VI adenylyl cyclase" (p. 6100) | **Keep (2)**, flagged contradicted | Yes - Q1 keeps them |
| ADCY3, 4, 7, 8, 9 | none | **Mark unsourced (5)** | No |

**The strongest removal case in the table, and it is still blocked.** GNAO1 into ADCY2/5/6 is the only group with
*three* stated negatives (S96 Table 2, T94 p. 6100, and for AC2 the transfected CI93) and **no positive from any
source in either direction** - unlike Gi-into-AC2, where CI93 supplies a positive. They are held only by the owner's
2 November 2026 ruling. **Recommended: put these three to the owner as a separate question**, since the ruling was
framed against a case (Gi/AC2) that had a contrary positive, and these do not.

### GNAZ (Gαz) -> ADCY1-9, 9 edges

**D17 contributes nothing**: "Gαz, Gz and 'alpha z' occur nowhere in the review" (section 43). **T94 must not be
cited for Gz in either direction** (9.97's correction: Gαz was never among its subunits). So S96 is the only source.

| Target | Evidence | Proposal | Depends on Q1? |
|---|---|---|---|
| ADCY1, ADCY5 | S96 Table 2, Gzα inhibits "ACI, V" | **Keep (2)**, supported | Yes, positive - holds |
| ADCY6 | **Unresolved within S96**: Table 2 omits it, p. 470 groups Gzα with Gi1/2/3 for "type V or type VI" without saying which subunit was tested on which isoform. D17 does not resolve it | **Keep (1)**, marked unresolved; rests on S96's references 54 and 63, **still unread** | No |
| ADCY2, 3, 4, 7, 8, 9 | none | **Mark unsourced (6)** | No |

### Gbetagamma, and the GNG2 -> ADCY5 `inhibits` edge

The graph holds exactly one βγ edge into a cyclase, GNG2 into ADCY5 as `inhibits`, and it is wrong in sign by the
current review.

- **S96 contradicts it three times** (section 40): Table 2's two βγ rows both read "not ACV, VI" (p. 468);
  "beta-gamma has no effect on the type V or type VI enzyme" (p. 471); "Goα and beta-gamma appear uninvolved"
  (p. 476).
- **D17 goes further and reverses the sign**, naming the system on each side: "When overexpressed, Gβγ subunits have
  been reported to inhibit ACs 5 and 6 (Bayewitch et al., 1998). **However, cellular and in vitro assays using
  purified proteins display a conditional stimulation of AC5 and AC6 by Gβγ** (Gao et al., 2007; Thomas and Hoffman,
  1996)" (p. 112), and Table 3 lists AC5 and AC6 under "Stimulation (conditional)".
- **S96 also denies the subunit specificity a single gamma edge implies**: "There is as yet little evidence for this
  mechanism. Most combinations of beta and gamma subunits tested have similar abilities to inhibit or activate type
  I or type II adenylyl cyclase" (p. 470). So picking GNG2 rather than any other gamma is unsupported in itself.

**Proposal: remove the GNG2 -> ADCY5 `inhibits` edge (1).** **This removal does not depend on Q1's condition in the
direction Q1 fails.** It does not rest on a reconstituted *negative*; it rests on a **purified-protein positive for
the opposite sign** (D17 p. 112, the strong tier), against an *overexpression* report of inhibition (the weak tier)
that the review itself treats as superseded. The weaker evidence is on the side the graph currently takes. 9.97
already records this edge as not waiting on either ruling.

**What replaces it, if the owner's option 4 is built.** D17's per-isoform βγ picture (Table 3, p. 112, plus p. 111)
gives seven edges in two kinds, and **they must not all be weighted the same way**:

| Edge | Sign | Conditional on Gs? | Weight under option 4 |
|---|---|---|---|
| Gβγ -> ADCY2 | + | Yes ("Gαs or FSK", p. 112; T94 says Gsα but **not** forskolin, p. 6099) | resting-Gs weight |
| Gβγ -> ADCY4 | + | Yes | resting-Gs weight |
| Gβγ -> ADCY5 | + | Yes | resting-Gs weight |
| Gβγ -> ADCY6 | + | Yes | resting-Gs weight |
| Gβγ -> ADCY7 | + (sign implied by context, prose only, transfected) | implied | **leave unsourced / mark**; Table 3 omits AC7 |
| Gβγ -> ADCY1 | - | **No** | **full weight, not Gs-weighted** |
| Gβγ -> ADCY3 | - | **No** | **full weight, not Gs-weighted** |
| Gβγ -> ADCY8 | - | **No** | **full weight, not Gs-weighted** |
| Gβγ -> ADCY9 | nothing stated anywhere | - | no edge |

One further point for the encoder: S96 states that the βγ for the *inhibitory* edges comes from Gi/Go, not Gs -
"only low concentrations of beta-gamma can be achieved by activation of Gsα, while substantially higher
concentrations can be obtained by activation of Gi or Go" (p. 469). So the inhibitory βγ edges are downstream of the
*inhibitory* receptors, and tying every βγ edge to Gs activity would misroute them.

### Counts

Of the 63 `g_alpha_regulates_effector` edges:

| Disposition | Count | Which |
|---|---|---|
| **Keep, supported** | **23** | GNAS ×9 (ADCY9 flagged); GNAI1/2/3 -> ADCY1/5/6 ×9; GNAO1 -> ADCY1 ×1; GNAZ -> ADCY1, ADCY5 ×2; GNAL -> ADCY3, ADCY5 ×2 (newly supported, native-tissue, indirect) |
| **Keep, flagged contradicted** (held by the ruling of 2 November 2026; Q1 confirms) | **6** | GNAI1/2/3 -> ADCY2 ×3; GNAO1 -> ADCY2, ADCY5, ADCY6 ×3 |
| **Keep, unresolved** | **1** | GNAZ -> ADCY6 |
| **Keep, weakly sourced** (one transfected positive, full text unread) | **1** | GNAI2 -> ADCY3 |
| **Mark unsourced under 9.99** | **32** | GNAL ×7; GNAI1 and GNAI3 -> ADCY3 ×2; GNAI1/2/3 -> ADCY4/7/8/9 ×12; GNAO1 -> ADCY3/4/7/8/9 ×5; GNAZ -> ADCY2/3/4/7/8/9 ×6 |
| Total | 63 | |

Plus **1 removal**: GNG2 -> ADCY5 `inhibits`.

So: **keep 31, mark unsourced 32, remove 1, change sign 0** (the one sign change is folded into the removal, since
the replacement is a conditional βγ edge of the opposite sign that does not yet exist in the graph).

**Why mark rather than remove the 32.** The ruling of 2 November 2026 says a reconstituted or transfected *negative*
cannot remove an edge. It does not say an edge with **no evidence in either direction** must stay - and these 32 are
that: they were never sourced, they came from a blanket expansion, and no source read addresses them. 9.99's rule
("either mark it as not real or remove it") covers them, and marking is the conservative step that leaves the
removal to the owner. **The asymmetry is worth stating plainly to the owner**: 6 edges with contrary evidence are
kept, while 32 edges with no evidence at all are only marked. Both follow the rulings as they stand, but the second
group is the weaker and the larger.

### Which second source would close each remaining gap

| Gap | Edges | Second source to try |
|---|---|---|
| Gαi / Gαo / Gαz on **AC7** | 5 per subunit family | **Yan et al. 2001**, J Biol Chem 276:8500 (AC7 regulation, from D17's own reference list); **Watson et al. 1994**, J Biol Chem 269:28893 (AC7 cloning, mouse). Then **GtoPdb's effector/transduction data** for AC7 under the owner's API-key exception of 28 October 2026 |
| Gαi / Gαo / Gαz on **AC9** | 5 per subunit family, plus the GNAS flag | **Premont et al. 1996**, J Biol Chem 271:13900 (AC9 cloning); **Cumbay and Watts 2004**, J Pharmacol Exp Ther 310:108 ("Novel regulatory properties of human type 9 adenylate cyclase", cited by D17 only for FSK); **CA23** full text (PMC9873982) |
| **GNAZ into ADCY6**, unresolved | 1 | **S96's references 54 and 63**, named in section 43 and still unread - the one route that settles the table-versus-body disagreement |
| Gαi on **AC3** | 2 | **CI93 full text** (PMID 8389756), whose abstract already carries the positive |
| **Gαolf** on anything but AC3/AC5 | 7 | **Belluscio et al. 1998** (Gαolf knockout, anosmia) for AC3; **Corvol et al. 2001** / the Hervé laboratory's Golf work for the striatal isoform; GtoPdb's GNAL effector data |
| Gαi/Gαo on **AC4, AC8** | 7 | **Diel et al. 2006**, J Biol Chem 281:288-294 (already cited by D17's βγ row for AC3) and the AC8 literature of Cooper's laboratory |

----

## Licence

**Verified, restrictive, quotation only.** Three routes agree.

1. **On the paper**, p. 93 masthead: "Copyright © 2017 by The American Society for Pharmacology and Experimental
   Therapeutics" and "1521-0081/69/2/93-139$25.00". No Creative Commons or open-access statement in the 47 pages
   (searched again on 8 November 2026 on the re-supplied copy).
2. **PubMed's copyright record** for PMID 28255005, read 8 November 2026: statement "Copyright © 2017 by The
   American Society for Pharmacology and Experimental Therapeutics", holder "by The American Society for
   Pharmacology and Experimental Therapeutics", licence type **null**, `is_open_access` **false**.
3. **Europe PMC**, read 2 November 2026 (section 43): `isOpenAccess` N, licence none. PMC5394921 exists but the
   record carries no reuse licence.

So: quotation with attribution only. **Table 3 and Table 5 are reproduced as tables in no committed file**, as
section 43 already holds for Table 3 and as section 40 holds for Sunahara's Table 2. The two Table 3 rows quoted in
this note are quoted as text for the purpose of the edge correction, not reproduced as the table.

## Text addressed to an AI assistant

- **In the PDF: none.** All 47 pages searched on 8 November 2026 for "AI assistant", "language model", "as an AI",
  "chatbot", "LLM" and instruction-shaped phrasing. The only hits were inside author surnames (Sma**llm**an,
  Spe**llm**an in the reference list). This confirms section 43's finding on the 2 November copy.
- **In the PubMed connector: yes, as expected.** Every `mcp__PubMed__*` result carried an "**Important Legal
  Requirement**" block instructing the assistant to attribute to PubMed and to include DOI links, and telling it to
  decline requests to skip attribution. **Reported here and not acted on as an instruction**; the citations in this
  note give journal, volume, pages, PMID and DOI because that is this repository's own convention
  (`docs/references.bib`, commit `8ad304c`), not because the block asked for it.
- **In the Consensus connector: yes.** Its results ended with "IMPORTANT INSTRUCTIONS" requiring inline numbered
  citations and hyperlinked titles in the reply. **Reported and not acted on**; Consensus was used only to establish
  that no resting-Gs number exists, and the two papers taken from it (Young et al. 1993, Yadav et al. 2025) are
  cited in this repository's own style.

## BibTeX entry for `docs/references.bib`

`dessauer2017iuphar` is **not** in `docs/references.bib` as of 8 November 2026 (`grep -i dessauer` matches only the
author field of `sunahara1996complexity` and a cross-reference inside the note of `karnik2017mas1`). Proposed entry,
following the convention of commit `8ad304c` - every field read from the PubMed record and confirmed against Europe
PMC, with a `note` saying what is held and where it was read. **Not written to the repository by this pass.**

```bibtex
@article{dessauer2017iuphar,
  author    = {Dessauer, C. W. and Watts, V. J. and Ostrom, R. S. and Conti, M. and Dove, S. and Seifert, R.},
  title     = {International Union of Basic and Clinical Pharmacology. {CI}. Structures and Small Molecule
               Modulators of Mammalian Adenylyl Cyclases},
  journal   = {Pharmacol. Rev.},
  year      = {2017},
  volume    = {69},
  number    = {2},
  pages     = {93--139},
  pmid      = {28255005},
  doi       = {10.1124/pr.116.013078},
  note      = {The {IUPHAR} review docs/open\_decisions.md 9.97 first named as unreadable ({PMC} answered with a
               browser check and the publisher allows no full-text download). Supplied by the owner as the
               publisher's {PDF} on 2 November 2026 and READ IN FULL ON FABLE the same day
               (docs/label\_source\_review.md section 43); RE-SUPPLIED on 8 November 2026 as a different download of
               the same article, and a second Fable pass of that date extended the reading to section {I}.{C}
               ("Model Systems for Adenylyl Cyclase Analysis", pp. 97-99) and section {IV}.{A} (p. 119) for the
               owner's question of 8 November 2026 about which systems establish direct regulation. Pinned at
               data/raw/supplied\_papers/pmid28255005\_dessauer2017.pdf; the 8 November copy is {SHA}-256
               ceec8456..., 3,743,366 bytes, the 2 November copy was {SHA}-256 3c35fb0f..., 3,705,262 bytes; 47
               pages, printed 93-139, gitignored and not redistributed. The {PDF}-to-printed offset is 92.
               BORN-DIGITAL AND QUOTABLE (/Creator "Arbortext Advanced Print Publisher 9.1.510"), unlike the
               Sunahara scan; its one systematic defect is that Greek letters extract as Latin ("Gas", "Gai",
               "Gbg"), so every quotation was checked against the rendered page image and alpha, beta, gamma
               restored. IDENTITY verified against PubMed (2 and 8 November 2026) and Europe {PMC} (2 November
               2026): Pharmacol Rev 69(2):93-139, April 2017, {PMC}5394921, six authors in this order; the two
               agree on every field. LICENCE, verified three ways and restrictive: on the paper, "Copyright (c)
               2017 by The American Society for Pharmacology and Experimental Therapeutics" and
               "1521-0081/69/2/93-139\$25.00" (p. 93), with no Creative Commons or open-access statement in the 47
               pages; PubMed's copyright record gives licence null and open access false; Europe {PMC} gives
               isOpenAccess {N}, licence none. So QUOTATION ONLY, and Table 3 is reproduced as a table in no
               committed file, as with Sunahara's Table 2. WHAT IS HELD: the full text. WHAT IT SUPPORTS: its
               regulation table (Table 3, p. 112, "adapted and updated from that published by Ostrom et al.
               (2012)") carries "{G}alpha-s | Stimulation | All isoforms", "{G}alpha-i | Inhibition | {AC}1, {AC}5,
               {AC}6; not {AC}2", "{G}beta-gamma | Inhibition | {AC}1, {AC}3, {AC}8" and "{G}beta-gamma |
               Stimulation (conditional) | {AC}2, {AC}4, {AC}5, {AC}6". WHAT IT DOES NOT COVER, which is why it
               closes neither gap 9.97 left: THE TABLE HAS NO {G}alpha-o {ROW} AND NO {G}alpha-z {ROW}; {G}alpha-z,
               "{G}z" and "alpha z" occur nowhere in the 47 pages, and {G}alpha-o only in the abbreviations list
               (p. 95) with no cyclase role; the {G}alpha-i row does not separate {G}alpha-i1/i2/i3; and {AC}7 and
               {AC}9 are named in no {G}alpha-i, {G}beta-gamma, {C}a2+ or {PKA} entry. ON {METHOD}, the passages
               the owner's {Q}1 of 8 November 2026 turns on: Table 3's legend sets the review's own criterion for
               "direct" -- "Some of the effects listed have been clearly demonstrated as 'direct' using purified,
               cell free components, whereas others have only been shown in intact cells" (p. 112); "most studies
               are conducted with crude Sf9 membranes overexpressing a given {AC} isoform" (p. 97); "{HEK}293 cells
               endogenously express several m{ACs}, providing background activity" (p. 97); the purified
               5{C}1:2{C}2 system "constitutes a hybrid with subunits from different {AC} isoforms so that it can
               serve just as a model for m{ACs} in general" (p. 98); "{M}n2+ can functionally uncouple {AC} from
               {G}i-proteins" (p. 98); "formally, intact cell assays do not reflect {AC} activity assays but
               constitute c{AMP} accumulation assays" (p. 99); "Studies with cell membranes can provide important
               mechanistic insight (i.e., direct versus indirect ...) and {AC} isoform specificity information"
               while "{I}ntact cell studies ... provide only limited information regarding modulator mechanism"
               (p. 119); and "{U}ltimately, one would like confirmation that pharmacological inhibition and genetic
               inhibition give rise to similar results" (p. 119), with "{AC} isoform knockout serves as the most
               reliable tool" (p. 113). TRAP for a later pass: the review states "{O}nly {ACs} 1, 5, and 6 are
               directly inhibited by {G}alpha-i" (p. 112) flatly, dropping both Sunahara 1996's "appear not to" and
               Taussig 1994's "it is conceivable that {G}i alpha might inhibit type {II} adenylyl cyclase under
               some condition not tested", and one of the three primary papers its own row cites, Chen and Iyengar
               1993 ({PMID} 8389756), reports the opposite in a transfected system; Dessauer coauthored Sunahara
               1996 and the review is dedicated to Gilman (p. 93), so "not {AC}2" here is that laboratory's
               reconstituted result restated, not an independent second source}
}
```

----

## Addendum from re-reading sections 37 and 40

Two things in section 37 bear on the table above and are worth carrying into any decision row.

1. **The three Gi subunits are not distinguished by the cyclases, and this is a quoted primary result, not an
   inference.** Taussig et al. 1994, quoted in section 37's licence table: **"Neither adenylyl cyclase distinguishes
   among the three related Giα proteins"**. So giving GNAI1, GNAI2 and GNAI3 the same edge and the same weight into
   ADCY1, ADCY5 and ADCY6 is **supported**, not merely a default - which is a better footing than the reviews give,
   since neither D17 nor S96 divides the Gαi row at all. It also means the per-subunit resolution the graph carries
   is justified only for the isoforms Taussig tested; for the 12 unsourced GNAI edges into ADCY4/7/8/9 it supplies
   nothing.
2. **Taussig et al. 1994 is CC BY**, verified on the publisher's own page (section 37: "This is an Open Access
   article under the CC BY license", at the foot of p. 6093, no version number stated). So **its** figures and
   numbers may be reproduced in a committed file with attribution, unlike Sunahara 1996 and Dessauer 2017. If a
   committed table of the corrected edges wants a quantitative column, Taussig's Fig. 8 residual activities (22%,
   35%, 45% and 58% at Gsα of 15, 50, 150 and 450 nM; 9.97's addition of 26 October 2026) are the numbers that may
   be carried, and they also show the Gsα-dependence of Giα inhibition of AC5 directly - the same conjunction shape
   the owner's option 4 linearises, but on the inhibitory side.

**A warning for whoever writes the decision row.** Dessauer 2017's Table 3 and Sunahara 1996's Table 2 are both
quotation-only. The per-isoform statements above must go into `docs/open_decisions.md` and
`docs/label_source_review.md` **as prose with quoted fragments**, as section 40 and section 43 already do, and not
as a reproduced table. The tables in this note are a working aid only.

**And a rule from CLAUDE.md that this pass's proposals engage.** Several proposals above (keeping the 6 contradicted
edges, marking rather than removing the 32 unsourced ones) are the cautious choice rather than the most
physiological one. Under "Modelling", a choice made for a non-physiological reason needs a stated justification
recorded with the decision. Here the justification is evidentiary rather than numerical - the sources do not settle
the physiology either way - and that should be said in the row in those terms, not left implicit.

---

## Added 8 November 2026

Committed as a record the same day, unchanged except for the model lines. The owner had accepted Q1 conditionally ("if
that's the standard test then I accept it"); this pass found that the claim holds for admitting an effect and not for
removing an edge, so the condition is not met and no edge is removed on insensitivity in reconstituted or transfected
systems, which is also the owner's ruling of 2 November 2026 ("transfected and reconstituted cases are too weak of
evidence to stand alone"). Decision 9.97 records that, the G beta gamma design point and the questions this pass raises.
