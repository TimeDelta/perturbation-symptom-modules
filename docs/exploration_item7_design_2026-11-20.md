# Item 7 of `docs/exploration_queue.md`: endosomal pH, NHE6 and NHE9 — design pass (20 November 2026)

**Run on Opus at the owner's request; unconfirmed; needs verification on Fable and the owner's ruling before it is
relied on.**

Nothing in the repository was edited, committed or pushed. Progress log beside this file
(`item7_design_2026-11-20.progress.md`); saved pages under `item7_pages/`; bib drafts in `item7_design_2026-11-20.bib`.
The research steps this pass took (one database entry and one review read for a resting endosomal pH) were done on
Opus at the owner's request and are flagged wherever they are used.

**Which graph every number is from.** All graph counts below were measured on 20 November 2026 on the build directory
`data/processed/graph_full_neuronal_split_binders_drugs_v5`, **files of 12 November 2026** (49,864 nodes, 275,194
edges; `evidence_full_v5` likewise dated 12 November). Those files **predate the item 37 rulings** of 13 to 20
November 2026 (`docs/item37_rulings_draft_2026-11-13.md`), none of which is built in them; in particular Q4 (one H+
node per compartment, ruled 20 November), "the bottleneck and pH ceiling stay inside the loop" (17 November), S3a (the
bounded pH width, in the code since 20 November but not in any run on these files) and the 9.81 direction (saturation
inside the fixed point, a floor at -1 per node, root-finder). So every count here is history the moment those are
built, and the item's own 7 November counts (49,834 nodes) are from an earlier state of the same directory name.
Code was read at the working tree of 20 November 2026.

---

## 1. What the graph holds today (files of 12 November 2026)

| Fact | Measured |
|---|---|
| SLC9A6 | no node; no evidence record (its 113 HPO rows are dropped) |
| SLC9A9 | `PROTEIN:SLC9A9` catalyses only `MAR05430`, "transport of H+ and Na+ (cytosol to extracellular)", whose outputs reach `NEURON_MAM02519c` and `NEURON_MAM02519e` through `changes_ion_pool` |
| SLC9A7, SLC9A8 | Human-GEM Golgi exchangers `MAR07694` (H+/K+) and `MAR07695` (H+/Na+) |
| Compartment `l` ("endolysosome") | 791 nodes: 458 metabolites, 320 reactions, 13 Reactome entities; mostly lysosomal catabolism (keratan, chondroitin and heparan sulfate degradation; cholesterol esters) |
| Protons in `l` | `MAM02039l` (Human-GEM, currency, 17 out / 180 in; the only V-ATPase reaction, `MAR00080`, writes into it) and `CHEBI15378l` (Reactome, currency, 0 out / 3 in, from the CLC exchangers) |
| Other `l` ions | no Na+ node; K+ `MAM02200l` currency; Cl- `MAM02144l` currency |
| Reactome reactions already merged into `l` | CLCN3 (`RCT_2731002`, "late endosome lumen"), CLCN4/5/6 (`RCT_2730692`, "endosome lumen"), CLCN7:OSTM1 (`RCT_2730959`, "lysosomal lumen"), TPCN1/2, ATP13A2, NAAA |
| Calcium store `NEURON_MAM01413l` | 0 in, 2 out (TPCN1/2 and `MAR_TRPML_CALCIUM_RELEASE`) |
| V-ATPase | `MAR00080` "V-Type ATPase, H+ Transporting, Lysosomal" (c;l) only; no endosomal pump reaction anywhere |
| `changes_membrane_potential` edges | 0 (the potential is reached through the pools' `driving_force` only) |
| Downstream targets present | `PROTEIN:NTRK2` (35 out), `BDNF`, `CTSD`, `MAPT`, `SLC1A3`, `TFRC`, `GRIA1`, `RACK1`, `M6PR` |

Two code facts that every option below has to work around:

1. **The pH weight reads one proton node per compartment.** `graph/compartment_ph.py`
   `proton_node_of_compartment` prefers the Human-GEM `MAM` node, so `l`'s weight reads `MAM02039l`; the CLC
   reactions' protons (`CHEBI15378l`) never reach it today. After Q4's merge they would.
2. **The pH weight is inert in every run.** `calibrate_ph_sensitivity` is called by no trainer code, as its own
   docstring says (`models/linear_response_encoder.py`, line 1256 on 20 November 2026); so whatever an option routes
   into a compartment's pH does nothing until that is settled (recorded under 9.75). And the weight is a bell,
   `exp(-(delta pH / w) ** 2)`: it says that a deviation either way costs throughput in that compartment, not which
   way a downstream quantity moves.

---

## 2. The design options

Five options, from least to most change, then the components every option shares. "Cost" is engineering effort and
what has to be sourced; none is large by the standard of item 37. Each option needs a rebuild and gives a new graph
version.

### Option A. Fetch `R-HSA-425986` and import it as the importer stands

**What changes.** One entry in `PATHWAYS` of `experiments/fetch_reactome_pathways.py` and its pin (the 7 November
copy hashes to `5bc23c49aa501543dc6db1d0e1cb29e9cd1cdb9579940e7b9645b2e746c33f6e`, re-hashed today and kept as
`item7_pages/R-HSA-425986_sbml_fetched_2026-11-07.xml`). Nothing else.

**What it does** (dry-parsed today with the importer's own `parse_reactome_sbml` and `compartment_letter`). Four
reactions arrive. Every endosomal species ("early endosome lumen/membrane", "late endosome lumen/membrane") gets the
letter `l`. `GENE:SLC9A6` appears as a member of `RCTE_4084678` "SLC9A6,7", which is a Reactome **CandidateSet** of
Q92581 and Q96T83, and catalyses `RCT_425983`. Reactome's cytosolic Na+ maps to the propagating neuronal pool
`NEURON_MAM02519c`; luminal Na+ becomes a new `MAM02519l` and luminal H+ stays `CHEBI15378l`, both currency by name
(`retag_currency_by_name`). So **an NHE6 or NHE9 loss reaches the graph only through the cytosolic Na+ pool**, and
from there `VM_c` through the pool's `driving_force` edge. The luminal acidification, which every source of the 7
November record makes the mechanism, reaches nothing. After Q4's merge the luminal H+ joins `MAM02039l`, so if the pH
weight were ever calibrated an NHE6 loss would scale the throughput of all 791 lysosomal nodes, a compartment the one
isoform-localisation study excludes ("No significant localization of these NHEs was observed in lysosomes",
Nakamura et al. 2005, Q1 of the 7 November record).

The import also brings **two duplicates**: the plasma-membrane reaction (SLC9A1-5) repeats Human-GEM's `MAR05430`, and
the Golgi reaction (SLC9A7/8) repeats `MAR07695`, so those genes would catalyse two copies of one exchange.

**Cost.** Minutes of code, one rebuild. **Labels**: SLC9A6's HPO rows become evidence records (section 3).
**Limits to state.** The route it gives is not the physiological one: the flux of an endosomal exchanger is not a
measurable term of bulk cytosolic Na+, so the reach is through a pool the gene barely moves. It lumps the endosome
with the lysosome, which Q1 and Pescosolido et al. 2021 (Q12: endosome and lysosome both overacidified, yet
endosomal cathepsin D activity up and lysosomal proteolysis down) both argue against. It keeps `MAR05430`'s
non-physiological SLC9A9 catalysis. Under CLAUDE.md "Modelling" option A alone would need a recorded justification of
why the physiological version is not used; the only one available is cost, which is small for the alternatives.

### Option B. Option A plus an endosome compartment separate from the lysosome

**What changes in code.** `compartment_letter` in `graph/reactome_import.py` (line 249) stops sending "endosom" to
`l`; the other places that name the letters are `ORGANELLE_CALCIUM_STORES` and the store names (lines 176 and 184),
`graph/compartment_resting_ph.py` (`RESTING_PH_BY_COMPARTMENT`, line 45: a resting pH for the new letter is required
by the pH weight), `graph/oxidative_regulation.py` `COMPARTMENT_WORDS` (line 27; it has no "endosom" today, so
nothing moves there), `experiments/analyze_pathway_modules.py` `COMPARTMENT_NAMES` (line 146), and the tests that
enumerate compartments. Two variants:

- **B1, one endosome letter** for every Reactome "endosom" compartment (early, late and the generic "endosome").
- **B2, two letters**: early/recycling endosome and late endosome. Closer to physiology (resting pH 6.3 to 6.5 against
  5.5, below), but it forces a ruling on where NHE9 sits (Reactome's late endosome after Nakamura 2005, against the
  recycling endosome of Kondapalli et al. 2013, Q18) and on where Reactome's generic "endosome lumen" of CLCN4/5/6
  goes, which no source read here settles.

**What else moves.** The split is not only about the NHEs. **CLCN3** ("late endosome") and **CLCN4/5/6**
("endosome") leave `l` with them, and both are labelled genes on v5 (CLCN3 6 evidence records, CLCN4 7: intellectual
disability, anxiety, hyperactivity, self-injury, compulsive behaviour and more). Their reactions would stop feeding the
lysosome's proton and feed the endosome's. The lysosome keeps CLCN7, TPCN1/2, ATP13A2, NAAA, TMEM175, TRPML and
Human-GEM's 320 lysosomal reactions. Human-GEM has no endosome compartment, so no metabolism moves.

**The pH weight follows automatically**: `compartment_ph_inputs` picks up any letter with an "H+" node, adding one
sensitivity and one width parameter per new compartment. What it would gate is only the nodes carrying the endosome
letter, which are a handful of Reactome entities (the exchangers themselves, the CLCs, V-ATPase:ATP6AP1, NOTCH1
[endosome membrane], SLC11A1); reactions spanning two compartments ("c;l") take no weight. So the weight would mostly
scale the transporters' own entity nodes, not TrkB or proteolysis.

**A missing pump.** The pump-leak picture both sources give ("the H+ gradient generated by the V-ATPase ... drives
secondary active transport by eNHE", Kondapalli et al. 2014, full text read 20 November 2026; and Tfn-TfR "delivered
to early endosomes where the V-ATPase lowers the pH of endosomes", same) has no pump in an endosome compartment: the
graph's only V-ATPase reaction is lysosomal, and Reactome's on-disk endosomal V-ATPase event is a binding
(`RCT_5252133`, "ATP6AP1 binds V-ATPase"). An endosomal pumping reaction would be curated (`CuratedReaction` in
`experiments/build_neuronal_graph_variant.py`, as TMEM175 and TRPML are) or imported from a Reactome pathway not yet
fetched; this pass read no reactome.org page and does not know whether one exists.

**Cost.** Small in code (the letter list and a resting pH), moderate in rulings (B2 more than B1).
**Limits.** On its own B fixes the lumping but still gives no route out of the lumen: the endosomal H+ is currency
and sends nothing, so the only reach is still the cytosolic Na+ pool, as in A.

### Option C. Option B plus an endosomal proton pool that propagates, and sourced edges out of it

**What changes.** The endosomal proton becomes a pool node on the pattern decision 9.75 set for the organelle calcium
stores: a `NEURON_`-prefixed node, not currency, that receives from the reactions that move protons across the
endosomal membrane and sends sourced edges. The hub argument behind currency protons does not apply to it: on today's
data it would touch about four reactions (NHE6/7, NHE9, CLCN3, CLCN4/5/6; plus a curated V-ATPase pump), against the
2,706 edges of the cytosolic proton `MAM02039c` (874 out, 1,832 in; files of 12 November 2026). Then curated edges from the pool (`docs/curated_dead_end_mechanisms.csv`, decision
9.68 (a)), each signed for "more luminal H+" (acidification), with the 7 November record's support:

| Edge (from the endosomal H+ pool) | Sign | Support in the 7 November record | Status for a build |
|---|---|---|---|
| to `PROTEIN:NTRK2` (TrkB protein and phosphorylation) | -1 | Q8 mouse, Q9 cochlea, Q10 hippocampus, Q11 human iPSC neurons: three labs | the best-supported arm |
| to arborisation, spines, AMPAR transmission | via TrkB | Q8, Q10, Q11, Q16 | no separate edge needed if TrkB's own edges carry it; whether they do on v5 is not checked here |
| to lysosomal proteolysis (`CTSD`) | needs two signs | Q12: endosomal CatD activity up, lysosomal CatD down | **not expressible on one CTSD node**; leave out, or split CTSD by compartment |
| to tau (`MAPT`) | +1 | Q14 rat, Q15 human post-mortem | the evidence is *aggregation*; `PROTEIN:MAPT` is a level, so the edge would carry a different quantity; flag |
| to surface GLAST (`SLC1A3`), transferrin receptor (`TFRC`) | -1 | Q17, Q19 (NHE9, astrocytes; the loss direction is the authors' extension) | cell-type mismatch in a neuronal graph; single-sourced in direction |
| M6PR/retromer, exosome release, amyloid-beta | various | one source each | out until a second source exists |

**The direction is carried by the substrate edges already.** NHE6 and NHE9 consume luminal H+ (Reactome writes the
lumen proton as a substrate), so their loss leaves more H+ in the lumen: the pool rises, which is acidification, the
sign Q8, Q12 and Q19 report. **The CLC direction has to be checked before C is built.** The on-disk Reactome CLC
reactions write H+ moving cytosol to lumen and Cl- lumen to cytosol; whether that is the physiological direction of
the endosomal 2Cl-/H+ exchangers was not checked by this pass, and under C it decides the sign of a CLCN3 or CLCN4
loss on the pool, so on labelled genes. A Fable pass checks it.

**The pH weight and the pool together.** Under C the pool carries a *signed* first-order effect and the bell weight
(once calibrated and moved inside the loop, as ruled on 17 November) carries the *unsigned* cost of any deviation. One
point favours keeping both: the gain-of-function variant G218R *alkalinises* endosomes and still diminishes dendritic
branching and mature spine density (Ilie et al. 2019, Q16), which a signed edge alone mis-signs (it would predict more
TrkB) and a bell captures. That variant also mistraffics to the plasma membrane, so the case is not clean; it is a
limit to state, not a proof.

**Cost.** Option B's cost, plus one pool node, the curated pump reaction, two to four curated edges (each with two
sources), the CLC direction check, and a resting pH. A Fable sourcing pass for the pump's subunit membership and the
CLC direction. **Limits.** The pool is in arbitrary units like every node; the edges are qualitative signs, with
weights falling back to the per-relation defaults; TrkB is the only arm with independent replication across labs;
NHE6/NHE9 redundancy (Q19: knockdown of NHE9 alone in mouse astrocytes "fell short of significance") is not
represented.

### Option D. Endosomal pH inside the pH weight only, no node

**What changes.** Option B's letter and resting pH, and nothing more. **What it does**: an NHE6 loss deviates the
endosomal H+, and the bell weight scales the endosome-letter nodes. **Limits.** Inert until calibration is wired in;
direction-blind; gates only the transporter entities, so no TrkB or proteolysis effect; reach beyond the exchanger is
again only the cytosolic Na+ pool. This is the item's "stays inside the pH weight" alternative, and on the code as it
stands it changes almost nothing.

### Option E. Curated gene-to-target edges with no pH mediator

**What changes.** A row `GENE:SLC9A6 -> PROTEIN:NTRK2, activates, +1` (and the like) in
`docs/curated_dead_end_mechanisms.csv`, with or without option A for the node. **Limits.** It skips the mediator the
sources name, so NHE6, NHE9, the CLCs and the V-ATPase cannot share it, and a drug acting on endosomal pH (a
lysosomotropic base, for instance) could never reach TrkB through it. It is the cheapest route to reach, and the
furthest from physiology; under CLAUDE.md "Modelling" it needs a justification that nothing here supplies.

### Components every option shares

1. **`MAR05430`'s SLC9A9 catalysis goes** (a `reaction_gene_rule` row of `configs/human_gem_corrections.csv`,
   the 20 November mechanism), on the 7 November finding that Human-GEM's evidence for it is a DeepLoc2 prediction.
   Without it, an SLC9A9 perturbation keeps a non-physiological route in every option.
2. **Import only what is not already there.** Of `R-HSA-425986`'s four reactions, the plasma-membrane and Golgi ones
   duplicate `MAR05430` and `MAR07695`. Importing the pathway whole doubles them; dropping them needs a filter in the
   import (the importer has `REACTOME_ENTITY_MEMBERS_REMOVED`, a member filter, but no reaction filter that this pass
   found).
3. **SLC9A6,7 is a CandidateSet.** The importer gives every UniProt in it `member_of +1`, so SLC9A7 joins the early
   endosome exchanger at full weight. SLC9A7 is a labelled gene (1 record, intellectual disability, OMIM:301024), so
   its membership changes a label's route. A membership question of 9.68's shape, decided on its own physiology.
4. **The K+ arm.** UniProt gives NHE9 a K+/H+ activity (Rhea:29467) that neither Human-GEM nor Reactome carries.
   Whether a curated K+ reaction is added is a sourcing question; the pool's sign does not depend on it.
5. **A resting pH for each new letter** (section 2, sources below), since `compartment_ph_weight` needs one.
6. **The pH weight's calibration** stays the registered-model matter 9.75 recorded. A new compartment adds two
   parameters to a registered form; whether that is an amendment is for the owner (question 9).
7. **The study-sheet diagrams.** A ruling that adds a compartment or a pool changes the architecture, so the commit
   that records it checks the diagrams `tests/test_study_sheet_diagrams_current.py` names and adds this to one
   (CLAUDE.md "Documents").

**Resting endosomal pH, as read today (Opus, flagged).** BioNumbers BNID 115761, the entry
`compartment_resting_ph.py` already uses (read 20 November 2026 through `experiments/read_public_page.py`, sha256
`bdb974333aaa28e2...`), restating Casey, Grinstein and Orlowski 2010 through Theillet et al. 2014: "6.3 in early
endosomes, 6.5 in recycling endosomes, 5.5 in late endosomes, and 4.7 in lysosomes". Second source, of a different
kind: Kondapalli et al. 2014, full text (PMC4066934 through the PubMed API, saved): "the endosomal pH is acidic
(≈5.7) relative to the cytoplasmic pH (≈7.2)". **They disagree for a single-letter design**: 5.7 is a generic
endosomal figure, between the early (6.3) and late (5.5) values. Under B2 the BioNumbers values serve per letter;
under B1 the owner picks one, with the range recorded. A third route, Paroutis, Touret and Grinstein 2004 (BNID
108099, PMID 15304635), gives its values only in a figure and was not read. The BioNumbers licence stays unverified,
as the module already records.

---

## 3. Which labels it would recover, and whether any reach a symptom

Mapped today with the loader's own `expand_symptom_terms` (`evidence/load_monogenic_phenotype_annotations.py`) over
`data/raw/hpo/hp.obo`, `data/raw/hpo/genes_to_phenotype.txt` and the two crosswalks (script
`item7_hpo_map.py` in the scratchpad). Any option that gives SLC9A6 a node (A, B, C, D; E only with A's node)
recovers the same labels; the options differ in the route by which the model could fit them, not in the labels.

**SLC9A6: 113 HPO rows over three diseases.** OMIM:300243 (intellectual developmental disorder, X-linked syndromic,
Christianson type), ORPHA:85278 (Christianson syndrome), and OMIM:301142 (neurodegenerative disorder, X-linked,
female-restricted, with parkinsonism and cognitive impairment; names as `phenotype.hpoa` gives them).

| Target symptom (fine crosswalk; all are symptoms of `evidence_full_v5`) | HPO terms | Disease, frequency |
|---|---|---|
| `intellectual_disability` | Intellectual disability, Severe ID (HP:0001249, HP:0010864); Profound ID (HP:0002187) | OMIM:300243, "-"; ORPHA:85278, very frequent |
| `cognitive_impairment` | Mental deterioration (HP:0001268) | OMIM:301142, 1/2 |
| `parkinsonism` | Parkinsonism (HP:0001300) | OMIM:301142, 1/1 |
| `bradykinesia` | Bradykinesia (HP:0002067) | OMIM:301142, 2/3 |
| `resting_tremor` | Resting tremor (HP:0002322) | OMIM:301142, 1/2 |

On the coarse crosswalk the same rows give `cognitive_impairment` and `parkinsonism` (Bradykinesia and Resting tremor
roll up into parkinsonism; intellectual disability is not a coarse symptom). **So yes, five fine symptoms are
reached.** Inappropriate laughter (HP:0000748, ORPHA:85278) is the one row removed by an exclusion
(`disinhibition_or_impulsivity`, as the item says). Autism, sleep disturbance, hyperkinetic movements, motor stereotypy,
personality changes, happy demeanor, mutism and the seizure terms map to no target symptom.

Two things to state with them. The four movement and cognitive labels rest on OMIM:301142 alone, a female-restricted
disorder with small denominators (1/1, 1/2, 2/3), and its mechanism in the sources read is the degenerative arm (tau,
Q14 and Q15), which is the arm option C can carry least well (a level edge for an aggregation finding). The
intellectual-disability labels sit on the developmental arm (TrkB, arborisation), which is C's best-sourced edge.

**SLC9A9: no label of this kind.** It has no HPO row. On v5 it holds four SFARI mouse-model reports and four IMPC
knockout reports, every one "absent" (hyperactivity, anxiety, psychomotor retardation), and one PubTator
`depressed_mood` co-mention (`sfari_v5`, `impc_v5`, `literature_v5`, files of 12 November 2026); whether those report
tables enter the scored evidence was not checked here. Its autism and ADHD associations (7 November record) are not
labels in the build. So for SLC9A9 the design changes the route, not the label set.

**Side effects on labelled genes.** Under B and C, CLCN3 (6 records) and CLCN4 (7) move to the endosome; under A and
C, SLC9A7 (1 record) gains the early-endosome exchanger by CandidateSet membership; the V-ATPase subunit genes
(ATP6V0A1 4 records, ATP6AP2 6, ATP6V1A 3) would gain an endosomal pump under C. These labels are fitted today on
other routes, so each of these changes moves a fitted label and should be checked after the build.

---

## 4. Recommendation (mine, on Opus; not a ruling)

**Option C on variant B1, built in this order, with the pieces that need sources sourced on Fable first:**

1. Drop SLC9A9 from `MAR05430` (corrections table). Independent of the rest and the clearest physiological error.
2. Fetch `R-HSA-425986` with its hash pinned, importing its two endosomal reactions only (a reaction filter beside
   the member filter), so the plasma-membrane and Golgi exchanges are not doubled.
3. One endosome letter (B1), separate from `l`. I prefer B1 to B2 for now because the sources do not agree where
   NHE9 sits inside the endosomal system and Reactome's generic "endosome" compartment of CLCN4/5/6 cannot be placed in
   either half without new sourcing; that is a justification from the sources, not a numerical one, and B2 is the
   refinement to record as next. The separation from the lysosome itself is what the sources require (Q1, Q12).
4. A propagating endosomal proton pool on the 9.75 store pattern, with **one** curated edge to start, pool to
   `PROTEIN:NTRK2` at -1, the arm replicated across three labs; the tau, cathepsin and GLAST arms recorded as
   candidates with their stated problems, not built.
5. A curated endosomal V-ATPase pumping reaction, after a Fable pass sources its subunit membership, and the CLC
   direction check, before any of 3 to 5 is built.
6. Leave the bell weight to apply to the new letter as it does to every other, with its calibration still the open
   9.75 matter; do not build anything that relies on it.

Why not A: it gives SLC9A6 its labels through a route (cytosolic Na+) that is not the mechanism and lumps a compartment
the sources separate; the cheaper option is not much cheaper. Why not D: on the code as it stands it does nothing.
Why not E: it skips the mediator the sources name.

The item 37 rulings change the ground under this: Q4's H+ merge (needed for B and C to see one proton per
compartment), the pH ceiling inside the loop and 9.81's saturation and floor are all unbuilt. Building C after them
avoids re-measuring twice; the queue's own note says a re-measurement on the 12 November files would be history once
the amendment is built.

---

## 5. Questions for the owner

None has a decision id; ids are taken at commit time by the command in CLAUDE.md. Each is to be decided on its own
physiology, with its relation to the others recorded (CLAUDE.md "Related decisions are decided one by one").

1. **Separate the endosome from the lysosome?** And if so, one endosome letter (B1) or early/recycling and late (B2)?
   Under either, CLCN3 and CLCN4/5/6 move with the NHEs.
2. **Endosomal pH as a propagating pool node with sourced edges (C), as the bell weight only (D), or both?**
3. **Import `R-HSA-425986` whole, or only its two endosomal reactions?** Whole doubles the plasma-membrane and Golgi
   exchanges Human-GEM already carries.
4. **SLC9A7's membership of the early-endosome exchanger** (Reactome's CandidateSet "SLC9A6,7"): full member, a share
   on 9.68's pattern, or out. Not settled by 9.68.
5. **NHE9's compartment**, only under B2: Reactome's late endosome (Nakamura et al. 2005) or the recycling endosome
   (Kondapalli et al. 2013).
6. **Drop SLC9A9 from `MAR05430`?** (The 7 November record finds the catalysis rests on a DeepLoc2 prediction.)
7. **A curated endosomal V-ATPase pump**, sourced by a Fable pass, so the pump-leak balance has its pump?
8. **The resting pH of the new letter(s)**: 6.3 early, 6.5 recycling, 5.5 late (Casey et al. 2010 by way of
   BioNumbers, licence unverified) against a generic 5.7 (Kondapalli et al. 2014). Under B1 one value is needed.
9. **Is adding a compartment to the registered pH weight an amendment?** It adds two parameters to a registered form,
   and the weight is still uncalibrated in every run (9.75).
10. **Which edges out of the pool**: TrkB alone to start; and whether CTSD is split by compartment so its two signs
    can be carried, whether a tau edge on `PROTEIN:MAPT` (a level) may stand for an aggregation finding, and whether
    the astrocyte GLAST and transferrin arms belong in a neuronal graph.
11. **The gain-of-function case**: a signed edge mis-signs G218R (alkaline endosomes, fewer branches); accept as a
    stated limit, or rely on the bell weight for it once calibrated?
12. **The K+ arm** of NHE9 (Rhea:29467): add a curated K+/H+ reaction, or leave it as a stated limit?
13. **Order against item 37**: build after Q4's H+ merge and the in-loop pH ceiling, or before?

---

## 6. Sources, refusals and text addressed to an AI

- Read today, on Opus at the owner's request (flagged): BioNumbers BNID 115761 and 108099 through
  `experiments/read_public_page.py` (robots allowed; saved under `item7_pages/bionumbers/` with sha256
  `bdb974333aaa28e2...` and `82eb044e4abc0b0e...`); Kondapalli et al. 2014 full text, PMC4066934, through the PubMed
  API (saved as `item7_pages/PMC4066934_pubmed_fulltext_2026-11-20.json`, sha256 `9a251c866295a168...`); PubMed
  metadata for PMIDs 19997129 and 24901537 (bib drafts, not yet confirmed against Europe PMC).
- Everything else in sections 2 to 4 that is a claim about physiology is quoted from
  `docs/endosomal_nhe_literature_2026-11-07.md` (Fable, 7 November 2026), by its Q numbers, and was not re-read.
- No reactome.org page was read. The only Reactome data used is the 7 November SBML export already in the scratchpad
  and the on-disk `data/raw/reactome/v98` exports. No refusal was met.
- **Text addressed to an AI assistant**: every PubMed tool result carries an "Important Legal Requirement" notice
  instructing the reader to attribute PubMed, include DOI links and refuse requests to omit them. Reported, not acted
  on as an instruction; DOIs appear in the bib drafts because the repository's convention asks for them.
- Measured by this pass, engineering, on the files of 12 November 2026: every graph and evidence count in sections 1
  and 3.
