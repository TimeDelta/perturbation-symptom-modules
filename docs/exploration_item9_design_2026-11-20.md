# Item 9, the Krebs cycle and oxidative burden: design of the metabolite-driven oxidant relation (20 November 2026)

**Run on Opus at the owner's request; unconfirmed; needs verification on Fable and the owner's ruling before it is relied on.**

A research and design pass for item 9 of `docs/exploration_queue.md`, asked for on Opus 5.5 by the owner on 20 November
2026. Nothing in the repository was edited or committed. The progress log is `item9_design_2026-11-20.progress.md`,
saved pages are under `item9_pages/`, and draft BibTeX is `item9_design_2026-11-20.bib`, all in this scratchpad folder.

**Which graph the numbers come from.** Every graph count below is from
`data/processed/graph_full_neuronal_split_binders_drugs_v5`, files dated 12 November 2026 (49,864 nodes, 275,194 edges,
`drug_entry_summary.json`), read on 20 November 2026. **Those files predate the item 37 rulings**
(`docs/item37_rulings_draft_2026-11-13.md`, ruled 13 to 20 November and not built). So every count here is a count on
the pre-item-37 graph and has to be taken again on the build that carries those rulings. The label counts are from
`data/processed/evidence_full_v5`, files of the same date.

---

## 0. Summary

1. **The 7 November framing should change.** The Fable pass of 7 November (`docs/krebs_oxidant_literature_2026-11-07.md`)
   called succinate (`MAM02943m`) to superoxide by reverse electron transport (M-3) and 2-oxoglutarate (`MAM01306m`) to
   H2O2 (M-4) the cheapest metabolite-driven edges. A succinate edge gives **the wrong sign for SDH inhibition**. Blocking
   SDH makes succinate pile up, yet it stops reverse electron transport: malonate inhibits succinate-driven H2O2
   (Korshunov 1997), and "Stepwise oxidation of the QH(2)/Q pool by increasing malonate concentration slowed the rates of
   both reverse electron transport and rotenone-sensitive superoxide production by complex I" (Treberg 2011). What the
   physiology turns on is **the redox state of the carrier pools**, not the substrate. So this design gives the edges to
   the state variables: the reduction of the matrix NAD pool and of the Q pool.
2. **The proposed relation** has a working name, `redox_state_drives_oxidant` (for the owner to name). It runs from a
   redox-state node to an oxidant node and carries a stored sign. It is kept apart from the gene-driven
   `produces_oxidant`, so it gets its own learned gain. It needs three kinds of source:
   (a) a new **matrix NADH pool node `REDOX_NADH_m`**, built like the existing `REDOX_NADPH_m` in
   `mechanistic_pathway_learning/graph/redox_pools.py`, because NADH itself (`MAM02553m`) is a currency node;
   (b) the existing non-currency **ubiquinol nodes** (`MAM03102m`, and Reactome's duplicate `CHEBI64183m`);
   (c) optionally **2-oxoglutarate** (`MAM01306m`) as the substrate of the OGDH complex's leak.
3. **Six edges are proposed.** Two are sourced from two independent groups each. Two are flagged: one is contested
   between sources and one is a ratio term. Two are optional and rest on one source each (section 2).
4. **The new route conflicts with an existing row.** The `NDUFV1 -> superoxide` row (+1) makes a complex I loss *lower*
   superoxide. Patient fibroblasts show the opposite ("Superoxide production was significantly increased in all but two of
   the patient cell lines", Verkaart 2007; Pitkanen & Robinson 1996), and the NADH-pool route would give that opposite.
   This is for the owner to rule on as its own decision.
5. **Three limits stand whatever is built.**
   - No mitochondrial membrane-potential node exists, and the edge from the Q pool holds only at high protonmotive force.
   - Human-GEM writes SDH in reverse (`MAR04652`, fumarate + ubiquinol -> succinate + ubiquinone), so on that route an
     SDH loss *raises* ubiquinol.
   - All 34 `oxidatively_modifies` edges start from cytosolic oxidant copies, so mitochondrial superoxide modifies no
     protein directly.

---

## 1. What the graph holds today (v5, files of 12 November 2026)

- `produces_oxidant`: 27 edges, all from `PROTEIN:` nodes (`gene_protein_split.py` reroutes them from the gene). The sign
  is hard-coded +1 in `add_oxidative_regulation`. Mitochondrial superoxide `MAM02631m` receives 5 of these edges (NDUFV1,
  UQCRFS1, PRODH, CYP2E1, SOD1) plus 2 `product_of` edges (MAR08411 transport, MAR13081). It is consumed only by the SOD2
  reactions and the peroxynitrite reaction. Mitochondrial H2O2 `MAM02041m` has 35 `product_of` and 6 `produces_oxidant`
  in-edges.
- **Currency.** NADH `MAM02553m` (degree 218) and NAD+ `MAM02552m` (degree 221) are currency nodes and pass nothing on.
  Succinate `MAM02943m` (20), 2-oxoglutarate `MAM01306m` (42), pyruvate `MAM02819m` (16), ubiquinol `MAM03102m` (9) and
  ubiquinone `MAM03103m` (7) are not currency nodes.
- **Two unmerged Q pools.**
  - Human-GEM: ubiquinol is a product of complex I (`MAR06921`) and of ETF-QO (`MAR06911`), and a substrate of complex
    III (`MAR06918`) and of `MAR04652`.
  - Reactome: `CHEBI64183m` CoQH2 and `CHEBI46245m` CoQ, with Reactome's complex I (`RCT_163217`), SDH (`RCT_163213`,
    succinate + CoQ -> fumarate + CoQH2, irreversible, catalysed by `RCTE_70990`, which SDHA to SDHD are `member_of`),
    ETFDH and complex III reactions.
  - This is the same kind of case as item 37's Q4 (the duplicate H+ between Human-GEM and Reactome).
- **Direction.** Human-GEM's SDH reaction `MAR04652` is written fumarate + ubiquinol -> succinate + ubiquinone and is
  reversible. `PROTEIN:SDHA` catalyses it, and SDHA is also a member of the Reactome SDH complex. Applying the encoder's
  edge rules (`catalyzed_by` +1, `product_of` +1, derived `depletes_substrate` -1) to one hop gives opposite answers for
  an SDHA loss on the two routes:
  - the Human-GEM route lowers succinate and raises ubiquinol, the opposite of physiology;
  - the Reactome route lowers CoQH2, which is right.
  This is derived from the rules and **not measured**. MDH2's Human-GEM reaction `MAR04141` is also written in the
  non-physiological direction (oxaloacetate + NADH -> malate + NAD+).
- **The redox pools that exist.** `REDOX_GSH_<c>` and `REDOX_NADPH_<c>` for c, m, r, n and x (for example
  `REDOX_NADPH_m`, degree 45). There is no NADH pool.
- **The only membrane-potential node** is `VM_c`, the plasma membrane potential, computed from six ion pools
  (`membrane_potential_build` = `computed_from_the_pools`, amendment item 35).
- **Oxidant targets.** Every `oxidatively_modifies` edge starts from a cytosolic copy (`MAM02041c`, `MAM02631c`,
  `MAM02714c`, `MAM02609c`, `MAM00988c`, `MAM02149c`), because `docs/curated_oxidant_targets.csv` has no compartment
  column. That includes superoxide -> ACO2, though ACO2 is the mitochondrial aconitase. Mitochondrial H2O2 reaches the
  cytosol through `RCT_3779381`.
- **Who the change would reach.** No `targets` edge of the 260 drugs lands on a cycle, complex I to III, CoQ or ACO2
  protein. Of 2,802 labelled perturbations in `evidence_full_v5`, 36 are cycle or chain genes: ACO2, COQ2, COQ5, COQ7,
  COQ8A, DLAT, DLST, FH, MDH2, MT-ATP6, MT-ATP8, MT-CO1 to MT-CO3, MT-CYB, MT-ND1, MT-ND4, MT-ND5, MT-ND6, NDUFA1,
  NDUFA2, NDUFA6, NDUFB11, NDUFS1, PDHA1, PDHX, PDP1, SDHA to SDHD, SUCLA2, SUCLG1, UQCRC1, UQCRH and UQCRQ. These are the
  perturbations whose labels can test the change.
- **Pool node counts.** A `REDOX_NADH_m` built from Human-GEM stoichiometry, as `redox_pools.py` builds the NADPH pool,
  would collect:
  - +1 from 190 reactions that reduce NAD+ to NADH in the matrix (16 of them reversible);
  - -1 from 28 reactions that oxidise NADH there (11 reversible), among them both complex I reactions.

---

## 2. Design

### 2.1 The relation

- **Name (for the owner).** `redox_state_drives_oxidant`, a new relation beside `produces_oxidant`. Folding it into
  `produces_oxidant` (the owner's question as item 9 words it) is possible: the edges would then share one learned gain
  with the 27 gene-amount edges. I recommend against it. A gene edge says "more of this enzyme makes more oxidant"; a
  state edge is an elasticity, "a more reduced carrier pool makes more oxidant at this site". One positive gain cannot
  scale both quantities.
- **Direction and sign.** From a redox-state node to an oxidant node. The sign is stored per row, +1 or -1, unlike
  `produces_oxidant`. The encoder already reads stored signs and gives signed relations positive gains (module docstring
  of `linear_response_encoder.py`), so it needs no code change. Relation names are not hard-coded in `configs/`,
  `experiments/` or `models/` (`git grep`), so the relation enters through `relation_types.json`.
- **What the encoder does with it.** It adds one term, gain_r times sign over the destination's in-degree in the forward
  cone, at the oxidant node.
  - Under `forward_cone` (decision 9.16), only edges whose source a seed reaches count in the divisor. So a seed on a
    cycle gene dilutes the existing inputs to `MAM02631m` only when it reaches the new sources.
  - The pool node has an out-degree of 2 or 3 and so cannot become the hub the currency rule exists to prevent.
  - Pool nodes take class weight 1.0 in every class (checked on `REDOX_GSH_c` in
    `cell_class_weights/full_neuronal_split_drugs_v5_cell_class_weights.parquet`).

### 2.2 Source nodes and edges

| # | Source node | Target | Sign | Site and physiology | Status |
|---|---|---|---|---|---|
| E1 | `REDOX_NADH_m` (new) | superoxide `MAM02631m` | +1 | complex I flavin, site IF: the NADH/NAD+ ratio sets the rate | **Sourced, two groups** |
| E2 | `REDOX_NADH_m` | H2O2 `MAM02041m` | +1 | 2-oxoacid dehydrogenase complexes (OGDHc, PDHc) | **Contested** (Tretter 2004 against Quinlan 2014): a 9.122 gate with states {absent, +1} |
| E3 | ubiquinol `MAM03102m` and `CHEBI64183m` | superoxide `MAM02631m` | +1 | complex I site IQ by reverse electron transport, as the Q pool is reduced | **Sourced, two groups**; holds only at high protonmotive force (limit L1) |
| E4 | ubiquinone `MAM03103m` and `CHEBI46245m` | superoxide `MAM02631m` | -1 | the second term of the linearised QH2/Q ratio, same sources as E3 | **Flagged**: a modelling choice, not a separate finding |
| E5 | 2-oxoglutarate `MAM01306m` | H2O2 `MAM02041m` | +1 | substrate elasticity of the OGDHc leak; in situ the complexes produce "only when oxidizing their specific 2-oxoacid substrates" | Sourced (Starkov 2004 brain; Quinlan 2014; Tretter 2004 synaptosomes); optional |
| E6 | pyruvate `MAM02819m` | H2O2 `MAM02041m` | +1 | the same at PDHc, about half the OGDHc rate | **One source on a substrate-specific reading** (Quinlan 2014, skeletal muscle); optional, flagged |

**Built on purpose:**

- **No succinate edge** (M-3 of 7 November). Succinate reaches the Q pool through the SDH reactions, so on the Reactome
  route an SDH loss or a malonate-type block lowers ubiquinol and with it E3's superoxide. That is the physiological sign.
- **No ubiquinol to complex III edge.** Dröse & Brandt 2008: bc1 superoxide "is primarily promoted by a partially
  oxidized rather than by a fully reduced ubiquinone pool". The dependence is not monotone, so it has no sign an edge
  could carry.
- **No edge from NADH `MAM02553m` itself**, which stays a currency node.

### 2.3 Interactions with what exists

- **NDUFV1 -> superoxide (+1, existing).** A complex I loss lowers superoxide through this row and raises it through E1,
  because the pool rises when complex I oxidises less NADH. Verkaart 2007 puts the patient increase down to "the
  reduction in cellular CI activity and not ... a further leakage of electrons from mutationally malformed complexes",
  which is E1's mechanism. Keeping both counts the site twice, with opposite signs (question Q3).
- **The rows of 7 November.**
  - S-5 (SDHA -> oxidant, +1) sits beside E3. They describe different sites (IIF against IQ) and do not overlap.
  - S-1 and S-2 (DLD, DLST) carry a knockout direction: Dld+/- brain mitochondria make less H2O2. That agrees with E2 and
    E5.
- **Feedback loops.**
  - With the target compartment fix (section 2.4), the new edges close **negative** loops:
    - Q pool -> superoxide -> SDHA (-1, T-7) -> SDH flux -> Q pool;
    - NADH pool -> H2O2 -> OGDH (-1, T-1) -> less NADH, which Tretter & Adam-Vizi 2000 describe ("inhibition of
      alpha-ketoglutarate dehydrogenase limits the amount of NADH available for the respiratory chain").
  - The 7 November pass called the T-6 + S-5 loop positive. **In graph signs it is negative**: SDHA (+) superoxide (+)
    peroxynitrite (-) SDHA. Radi 1994 observes the positive version ("peroxynitrite induced an enhanced
    succinate-stimulated hydrogen peroxide formation"), so the graph's sign would contradict the observation. This is my
    reading and is unconfirmed. It goes into 9.81's count of positive-feedback cycles before the build.

### 2.4 Changes in code and data, and their cost

1. **`mechanistic_pathway_learning/graph/redox_pools.py`.** Add the matrix NADH pool. Use the same stoichiometric rule
   as for NADPH, with every NADH oxidiser kept, since there are only 28. The module docstring changes in the same commit.
   About 20 lines and one test in `tests/test_neuronal_regulation.py`.
2. **`mechanistic_pathway_learning/graph/oxidative_regulation.py`.**
   - Add a third curated table, for example `docs/curated_oxidant_state_sources.csv`, with columns `source_node,
     species_produced, compartment, sign, site, condition, pmid, doi, supporting_quote, second_pmid,
     second_supporting_quote`. The source is a node id, not a gene.
   - Add a loop that writes `redox_state_drives_oxidant` edges with the stored sign. It reports source nodes absent from
     the graph, as genes are reported now.
   - The docstring and the comment on `SOURCE_RELATION` change in the same commit (CLAUDE.md, "Code").
   - About 30 lines and one test.
3. **Optional, its own decision: a `compartment` column in `docs/curated_oxidant_targets.csv`.** The code already reads
   it (`getattr(row, "compartment", "")`). Without it, the cycle-enzyme targets of 7 November (OGDH, DLST, DLAT, SDHA),
   and ACO2 already, hang on cytosolic oxidants. Setting it moves ACO2's four rows to `…m` copies, which changes existing
   edges.
4. **`experiments/build_neuronal_graph_variant.py` and `scripts/rebuild_data_layer.sh`.** Pass the new table. Study-sheet
   diagrams `d282955a-f81a` and `64d7b2e6-81e2` depict `rebuild_data_layer.sh` and need a check and a re-stamp. The
   decision is architectural and no diagram shows it yet, so it is added to one (CLAUDE.md, "Documents").
5. **A data-layer rebuild.** The graph version changes. It can ride on the rebuild item 37's rulings already need.
6. **Cost.**
   - Engineering: about a day of code and tests, plus one rebuild.
   - Research: a Fable pass to verify the sources of section 3 and build the five BibTeX entries (draft in this folder),
     a few hours.
   - The decision-log work: the ruling, Q1 to Q8.
   - The encoder needs no change. One more relation gain per channel is a parameter count in the tens.

---

## 3. The sourced rows

Every quote is verbatim from a PubMed abstract read through the PubMed connector on 20 November 2026 (saved in
`item9_pages/pubmed_*.json`) or from the 7 November Fable pass, as marked. The five new records were matched against
Europe PMC (`item9_pages/epmc/565731f739e51296.txt`, SHA-256 `565731f7…a3cc`).

| Edge | First source (DOI, PMID): quote | Second source | Preparation |
|---|---|---|---|
| E1 | Treberg, Quinlan & Brand 2011, 10.1074/jbc.M111.252502, PMID 21659507: "superoxide production during forward electron transport in the presence of rotenone was uniquely related to NAD redox state" | Kussmaul & Hirst 2006, 10.1073/pnas.0510977103, PMID 16682634: "Consequently, the ratio and concentrations of NADH and NAD+ determine the rate of superoxide formation". **Brain:** Starkov & Fiskum 2003, 10.1046/j.1471-4159.2003.01908.x, PMID 12911618: "ROS production by mitochondria oxidizing physiological NADH-dependent substrates is regulated by DeltaPsi and by the NAD(P)H redox state" | rat skeletal muscle; isolated bovine complex I; rat brain, no inhibitors |
| E2 | Tretter & Adam-Vizi 2004, 10.1523/JNEUROSCI.1842-04.2004, PMID 15356188: "The higher the NADH/NAD(+) ratio the higher the rate of H(2)O(2) production" (7 November pass) | **Against:** Quinlan et al. 2014, 10.1074/jbc.M113.545301, PMID 24515115: the complexes "produced superoxide/H2O2 at high rates only when oxidizing their specific 2-oxoacid substrates and not in the reverse reaction from NADH" (7 November pass) | isolated enzyme and guinea-pig synaptosomes against rat muscle in situ |
| E3 | Treberg 2011 (as E1): "Stepwise oxidation of the QH(2)/Q pool by increasing malonate concentration slowed the rates of both reverse electron transport and rotenone-sensitive superoxide production by complex I" | Robb et al. 2018, 10.1074/jbc.RA118.003647, PMID 29743240: production by RET "responds to ... the magnitude of Δp, and the redox states of the CoQ and NADH pools", and alternative oxidase "to oxidize the CoQ pool affected RET-mediated O2- production". Supporting, in vivo: Chouchani 2014, 10.1038/nature13909, PMID 25383517; Korshunov 1997, 10.1016/s0014-5793(97)01159-9, PMID 9369223 (malonate inhibits) | rat skeletal muscle; mouse and rat heart; in vivo heart and brain (stroke model) |
| E4 | as E3 (the ratio) | as E3 | — |
| E5 | Starkov et al. 2004, 10.1523/JNEUROSCI.1899-04.2004, PMID 15356189: "alpha-ketoglutarate supported the highest rate of H(2)O(2) production" (7 November pass) | Tretter & Adam-Vizi 2004: "using alpha-ketoglutarate as respiratory substrate, the rate of H(2)O(2) production increased by 2.5-fold"; Quinlan 2014 (substrate-dependent) | rat brain; synaptosomes |
| E6 | Quinlan 2014: production "by the OGDH complex at about twice the rate from the PDH complex" and "only when oxidizing their specific 2-oxoacid substrates" | **None found for a pyruvate-specific elasticity.** Starkov 2004 shows isolated PDHC makes ROS, not the substrate dependence | rat skeletal muscle |

**Sources for the interactions and limits:**

- Complex I loss raises superoxide: Pitkanen & Robinson 1996, 10.1172/JCI118798, PMID 8755643, "We hypothesize that
  oxygen radical production is increased when complex I activity is compromised", with a MnSOD induction that can mask
  it. Verkaart et al. 2007, 10.1016/j.bbadis.2006.12.009, PMID 17289351, quoted in section 2.3.
- No Q-pool sign at complex III: Dröse & Brandt 2008, 10.1074/jbc.M803236200, PMID 18522938.
- The Δψ threshold: Korshunov 1997, "A threshold delta psi value is found, above which a very strong increase in H2O2
  production takes place."

**Rows that still lack a source:**

- **E6's second source.** Searched only through the 7 November pass's records; no dedicated search was made in this pass.
- **A brain preparation for E3.** All the RET sources are heart or skeletal muscle. Chouchani 2014 includes a stroke
  model, but its abstract does not localise the RET to brain mitochondria.
- **E4 as a distinct finding.** It is a modelling consequence of "Q pool redox state", not a separately measured sign.
- **The sign of the NADH pool's own inputs.** These come from Human-GEM stoichiometry, not curation, and inherit
  Human-GEM's written direction (limit L2).
- **Leipnitz et al. 2018** (10.1038/s41598-018-19543-3) studied NDUFV1-mutant fibroblasts, but its abstract states
  increased superoxide for ACAD9 cells only. It is not used.

**Licences.** Not checked. Only abstracts are relied on, and no full text was read.

---

## 4. Limits to state (do not overstate these in writing)

- **L1. Membrane potential.**
  - E3 holds above a Δψ threshold that "slightly exceeds the state 3 delta psi level" (Korshunov 1997). Starkov & Fiskum
    2003 make brain H2O2 depend on Δψ as well as on NAD(P)H.
  - The graph has no mitochondrial potential node, so E3 asserts the high-Δp regime unconditionally, and an uncoupler or
    ADP-driven depolarisation cannot lower superoxide through it.
  - The soft saturation ruled under 9.81 (item 37 draft, section 9) is per node. It is not a gate of one node by
    another, so it cannot carry the threshold either.
  - A computed Δψm node, like `VM_c`, would be a separate and much larger design.
- **L2. Written direction.** Human-GEM writes SDH (`MAR04652`) and MDH2 (`MAR04141`) against their cycle direction. On
  the Human-GEM route an SDH loss raises ubiquinol, and through E3 raises superoxide: the wrong sign. Only the Reactome
  route (`RCT_163213`) gives the right one. Until the two Q pools are merged and the direction is settled, E3 on the
  Human-GEM node can contradict E3 on the Reactome node for the same seed.
- **L3. Linear response carries elasticities at one operating point.**
  - E1 to E5 are local signs. Site IIIQo shows the dependence is not monotone across states.
  - Several roots (9.81) could in principle hold different signs. None is represented.
- **L4. Contested E2.** Isolated enzyme against mitochondria in situ, brain against muscle. The in-situ case is the one
  the graph models.
- **L5. Mitochondrial oxidants modify nothing directly** until the target table gets a compartment column.
- **L6. Preparations.** No E3 source is from brain, E1's brain source is NAD(P)H autofluorescence (it does not separate
  NADH from NADPH), and nearly everything is isolated mitochondria.
- **L7. Counts.** Every count here is from the 12 November files, which predate the item 37 rulings.
- **L8. Unverified.** This pass ran on Opus, and every quotation and the five BibTeX drafts need a Fable pass.
- **L9. Superoxide's site.** The UQCRFS1 row's text names the intermembrane-space face, but `COMPARTMENT_WORDS` tests
  "mitochondri" before "intermembrane", so the row lands on `MAM02631m`. `MAM02631i` exists (degree 2). This is outside
  item 9 and is reported rather than fixed.

---

## 5. Recommendation (mine, on Opus, unconfirmed)

1. **Allow metabolite-driven oxidant edges as a separate relation from redox-state nodes, not from substrates.** Build
   E1 and E3 first: two sources each, physiological sign under SDH and complex I losses.
2. **Put E2 under a 9.122 gate** {absent, +1}. Build E5 and leave E6 out until it has a second source.
3. **Decide E4 with E3**, because it is the same ratio. My preference is to include it, since a ratio linearises into
   two terms. But it doubles E3's weight in effect and is a choice the owner should make knowingly.
4. **Before building:**
   - merge or link the duplicate Q pools (an item 37 Q4-type decision);
   - rule on the NDUFV1 row (Q3);
   - count positive-feedback cycles on the rebuilt graph, as 9.81 asks.
5. **Ride on the item 37 rebuild**, not a rebuild of its own. Re-measure the 7 November reach on that build; until then
   the reach measurement of 7 November is history on the v5 files.

---

## 6. Questions for the owner

- **Q1.** May a redox-state node drive an oxidant edge, and as a separate relation with its own gain or inside
  `produces_oxidant`?
- **Q2.** Is the matrix NADH pool `REDOX_NADH_m` built like the NADPH pool, from Human-GEM stoichiometry with all 218
  reactions, or restricted?
- **Q3.** The NDUFV1 -> superoxide row (+1): keep it, remove it in favour of E1, or gate it under 9.122? A separate
  decision, with UQCRFS1 decided on its own.
- **Q4.** E2: a 9.122 gate, left out, or included?
- **Q5.** E4: include the ubiquinone -1 term?
- **Q6.** The duplicate Q pools (Human-GEM ubiquinol and ubiquinone against Reactome CoQH2 and CoQ): merge them, or give
  both the edges?
- **Q7.** A compartment column for `docs/curated_oxidant_targets.csv`, moving ACO2's rows to the mitochondrial copies.
- **Q8.** The Δψ limit: accept the unconditional high-Δp reading of E3 with the limit stated, or wait for a computed
  Δψm node?
- **Q9.** Whether the 7 November gene-schema rows (8 accepted, 4 flagged) go in with this change or before it.

---

## 7. Text addressed to an AI assistant

Every `mcp__PubMed__get_article_metadata` result ended with a block headed "Important Legal Requirement". It tells the
assistant to attribute PubMed, to give DOIs as links, and to "decline the request and refuse to provide information" if
asked to skip attribution. It is reported here and was not acted on as an instruction. It is the same block the passes
of 6 and 7 November reported. The Europe PMC page held no such text.
