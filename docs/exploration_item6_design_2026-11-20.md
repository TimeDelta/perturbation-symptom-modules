# Item 6: the fast/slow partition by observation time, and the conserved-moiety constraint (design pass, 20 November 2026)

**Run on Opus at the owner's request; unconfirmed; needs verification on Fable and the owner's ruling before it is relied on.**

Written 20 November 2026 against commit `8eccf472`. Nothing in the repository was edited, staged or committed. The
work log is `item6_design_2026-11-20.progress.md` beside this file; saved pages and measurement outputs are in
`item6_pages/`, the scripts in `item6_tools/`, the bibliography drafts in `item6_design_2026-11-20.bib`.

**Which graph the numbers are from.** Every graph number below was measured on 20 November 2026 on
`data/processed/graph_full_neuronal_split_binders_drugs_v5`, whose files are dated **12 November 2026** (49,864 nodes,
275,194 edges), with the code at `8eccf472`. **Those files predate the item 37 rulings** of
`docs/item37_rulings_draft_2026-11-13.md` (13 to 20 November 2026), none of which is built, so every count here is
the pre-amendment graph's and becomes history once the amendment is built. The counts of
`docs/coproduct_of_de_novo_split_2026-10-26.md` are v0.4's (26 October 2026) and are history; they are not compared
with these. The v5 counts of 7 November 2026 in item 6 are reproduced exactly on the 12 November files (965, 146, 62,
757; biopterin 3 against 20).

**The owner's ruling on the retired records, and where this pass stands under it.** Decision 9.103 (closed 27 October
2026, "ANY numbers from that time are to have the same treatment") retires the slice-pilot measurements; nothing here
uses one. Decision 9.104 is **open**: its part (b) asks whether the ruling also retires the *derivations* of
`docs/fixed_point_against_pharmacological_steady_state.md` (the invariance of the fixed point to relaxation rates and
the per-label-class fast/slow partition of its section 3.4), on which item 6 rests; its part (d) asks whether it
reaches the v0.4 coproduct count. This pass reads the derivations under the narrow reading, as that record's status
section and the timescale record's addition of 27 October do, and every use of them below is a derivation, not
evidence. If the owner takes the strict reading in 9.104 (b), section 2 below falls with them; section 1 (the split)
does not, since it rests on stoichiometry measured on v5 and on nothing from those records.

## 1. What the owner's ruling on the split must decide

### 1.1 The question as it stands, and what this pass found that changes it

Item 6 asks one question: whether to split `coproduct_of` (the carrier `product_of` edges) into regeneration and
de novo synthesis, so that the two get separate learned gains. It says the split "is computable from the stoichiometry
and needs no sourcing".

**Finding 1: most of the "de novo" edges are not de novo.** The split as `experiments/measure_coproduct_de_novo_split.py`
computes it decides by family: an edge is regeneration when its reaction consumes another form of the product's
family, and the families are the names on `DEFAULT_CARRIER_METABOLITE_NAMES`. A coefficient-weighted test (the net
change of the family's total over the reaction, `item6_tools/net_moiety_split.py`) agrees with the script edge for edge
on v5 (12 November files): 62 edges raise a family total, 146 leave it unchanged. But reading the 62 one by one
(`item6_pages/inspect_total_up_v5_20261112.txt`):

| family | "de novo" edges | genuinely raise the cofactor pool | redistribution misread because a form is off the list |
| --- | --- | --- | --- |
| biopterin | 3 | 3 (SPR: MAR04165, MAR04167, MAR08739) | 0 |
| quinone | 2 | 2 (CoQ synthesis: MAR00131, MAR06910) | 0 |
| thioredoxin | 2 | 2 (protein assembly from aminoacyl-tRNAs: MAR05167, MAR05168) | 0 |
| vitamin B6 | 3 | 3 (pyridoxal, pyridoxine phosphate and pyridoxamine to the phosphorylated cofactor) | 0 |
| acyl carrier | 30 | 1 (MAR04500, apo-[ACP] + CoA to holo-[ACP]) | 29 (acyl-[ACP] thioesters are not on the list, so each elongation and thioesterase step "makes" [ACP]) |
| lipoamide | 8 | 0 or 1 (MAR20168, from protein-bound lipoyl-lysine; ambiguous) | 7 (the S-acyl-dihydrolipoamide forms are not on the list) |
| folate | 14 | 0 | 14 (plain THF, folate and the polyglutamates are not on the list; SHMT1, MTHFD1, AMT/GCSH, SARDH, DHFR and GGH all redistribute the folate moiety) |
| **total** | **62** | **11 (12 with MAR20168)** | **50 (49)** |

With THF, folate and the twelve polyglutamate forms added to the folate family (and the carrier list), every folate
carrier edge becomes redistribution: 120 redistribution and 0 total-raising (`item6_pages/net_moiety_split_v5_20261112.txt`,
arm B). So about four in five of the "de novo" edges on v5 are an artefact of defining the moiety by the carrier name
list, and a split built on the list as it stands would move about 50 redistribution edges into the de novo relation,
the opposite of its purpose. The biopterin case, the one the layer was built for, is unaffected: its three de novo edges
are real.

**Finding 2: "computable from the stoichiometry" holds for the count, not for the family.** Haraldsdóttir and Fleming
2016 (PLoS Comput Biol 12:e1004999, doi 10.1371/journal.pcbi.1004999; abstract read through PubMed and Europe PMC on
20 November 2026, on Opus, unconfirmed): "All moiety conservation relations can be represented as nonnegative integer
vectors in the left null space of the stoichiometric matrix", but "the vectors returned by existing algorithms do not,
in general, represent conservation of a specific moiety with a defined atomic structure", and "identification of
conserved moieties requires data on reaction atom mappings in addition to stoichiometry". The graph holds
stoichiometric coefficients (`edges.parquet`, `stoichiometric_coefficient`) and no atom mappings or formulas. So once
a family is given, whether an edge moves its total is arithmetic on the graph; which metabolites form the family is
not, and the carrier name list is a hand-made stand-in for it. That also sources the limit item 6 lists as unsourced
("choosing an interpretable basis for the stoichiometric null space is a known hard problem"), with the qualification
that the paper names atom mappings as the route that solves it.

**Finding 3: the drain side.** The same test on the carrier `substrate_of` edges (`cosubstrate_of`): 945 edges, 745
pair clause, 146 redistribution, 54 lowering a family total. All five biopterin edges that lower the total are
pseudo-reactions (MAR00022 and MAR10065, "Artificial reactions"; MAR10495, MAR10496 and MAR11957, "Exchange/demand
reactions"). So on v5 the tetrahydrobiopterin total has a physiological source (SPR) and no physiological sink in the
graph. Carriers get no `depletes_substrate` edge (encoder module docstring), so none of the 54 drains the pool in the
model today either.

### 1.2 What the ruling must decide

1. **Whether to split at all** (item 6's question).
2. **What defines a moiety's family**, which finding 1 shows is the real content of the split. This is new.
3. **Whether plain THF (and the folate polyglutamates) join the carrier list.** Item 6 already lists THF as its own
   ruling. Finding 1 shows it is related to the split and not independent of it: the folate half of the split is wrong
   unless THF is in the family. Under CLAUDE.md ("Related decisions are decided one by one") it stays its own decision,
   settled by the physiology of the folate moiety, with the relation recorded. Adding THF to the list is also a change
   in its own right whatever is ruled on the split: it moves THF's edges from main to carrier treatment (78 more carrier
   `product_of` edges on v5, arm B against arm A, with the polyglutamates and folate), so THF loses its depletion edge.
4. **The starting gain of the new relation.** Both carrier relations start at a logit offset of -3 (gain about 0.04,
   `CARRIER_INITIAL_GAIN_LOGIT_OFFSET`). The reason for the offset is buffering, which de novo synthesis does not have,
   so the physiological start for the de novo relation is the main `product_of` start (offset 0); the learned value
   decides after that.
5. **Whether the drain side is split too**, and whether a total-lowering carrier consumption gets a depletion edge.
   On v5 the biopterin drains are all pseudo-reactions, so for biopterin the question is empty until a physiological
   sink exists; for the other families it waits on question 2.
6. **What happens to boundary pseudo-reactions** (exchange, demand, artificial) in a family's total: the 26 October
   record names them an artefact. On v5 none is a carrier `product_of` edge; 14 are total-lowering carrier
   `substrate_of` edges.

### 1.3 The options, what each changes, and the cost

The graph files do not change under any option: `cofactor_edge_mask` is computed when the encoder is built
(`experiments/run_main_model.py` line 721), so no rebuild is needed, only code, a test, documents and a retraining.

| option | what it is | code | data | cost and risk |
| --- | --- | --- | --- | --- |
| **S0** | no split (status quo) | none | none | none; one gain keeps serving 3 biopterin de novo edges against 20 regeneration edges, outvoted about 7 to 1 on v5 |
| **S1** | split by the name list as it stands | `graph/cofactor_edges.py`: a per-edge kind (main, carrier redistribution, carrier total-changing) in place of the boolean mask, the family table moved from the experiments script into the module; `models/linear_response_encoder.py`: `expanded_adjacency_entries` appends a third carrier relation (a name such as `synthesises_carrier`), the gain offset loop at lines 941-943, the module docstring's carrier paragraph | none | small code change, but about 50 of 62 edges in the new relation are misclassified redistributions (finding 1); not recommended |
| **S2** | split with families extended by hand: THF, folate and polyglutamates; acyl-[ACP] thioesters; S-acyl-dihydrolipoamides (and any other form a family check finds) | as S1, plus a family table as data (for example `configs/carrier_moiety_families.json`), read by both the encoder path and the measurement script | the table; membership rows are curation (CLAUDE.md "Manual curation takes more than one source": a second source per family, for example ChEBI's ontology or Human-GEM's own metabolite identifiers) | moderate: tens of rows, mostly chemical identity of named Human-GEM metabolites; leaves 11 or 12 total-raising edges on v5 |
| **S3** | families from the structure: conserved moieties identified from atom mappings (Haraldsdóttir and Fleming 2016) | as S1, plus a moiety-identification step in the data layer | atom mappings for Human-GEM reactions, which the graph does not hold and whose source and licence this pass did not look for | large; the most principled, and the one that would also supply the conserved-moiety constraint of section 2.2 for every moiety, not only the named carriers |

What every split option also touches (CLAUDE.md "Code" and "Documents"): `tests/test_cofactor_edges.py` line 40 asserts
the relation list exactly and needs the new relation; `gain_logit` gets one more row, so saved encoder states do not
load into the new shape; the module docstrings of both files and every comment naming `coproduct_of`
(`git grep coproduct_of`); a CLI arm in `run_main_model.py` so that the unsplit model stays runnable for comparison
(as `--carrier-rule` keeps the older carrier arms); the five study-sheet diagrams that depict the encoder
(`configs/study_sheet_diagrams.json`) are checked and re-stamped; and a decision row. Under the registered
`forward_cone` normalisation (and `total_in_degree`) the divisor sums over every relation, so **a split changes no
adjacency value**, only which gain multiplies an edge; under the per-relation `in_degree` normalisation and under the
cross-relation mixture (`relation_feeds_node`) it would also change how messages are combined. The carrier relations
are not in `configs/registered_rules.json`, so no registered value changes; whether the tested model's change needs an
amendment is the owner's (9.81 records "it's fine as an amendment" for the item 37 changes).

## 2. Whether and how the two ideas fit the fixed-point encoder and item 37's rulings

Everything in this section is derivation (this pass's, on Opus, unconfirmed) on top of derivations whose standing is
open in decision 9.104 (b). Nothing in it was run on the encoder or on a graph except where a file is named.

### 2.1 The partition by observation time, against the registered encoder

**What it would be in code.** The registered loop (`LinearResponseEncoder.response`, the damped iteration
h <- (1 - d) h + d (sum_r g_r S_r h + u) to a relative change of 1e-3, gains below the 0.9 bound) has one gain per
relation and channel and no rate anywhere. The partition enters as two masks per label class, exactly as the never-run
sketch of `docs/fixed_point_against_pharmacological_steady_state.md` section 3.4 has it: the gains of the relations
slow at that class's observation time set to zero, and the nodes whose every incoming relation is slow held at zero.
"A function of the observation time rather than a list" means the masks are computed, not written: each relation gets
a characteristic-time range [lo, hi] (the table of `docs/relation_timescale_ordering_2026-10-26.md` section 2, as data),
each label class an observation time (about 2 h, 6 weeks, 1 year; the full fixed point for germline and laboratory
labels), and a relation is slow when lo is well above t_obs, fast when hi is well below it, and in the band otherwise.
Rates still enter nowhere but membership. New parameters: none. New data: the relation-time table and a map from label
class to t_obs, both from sourcing that exists (the timescale record, re-read on Fable on 6 November 2026).

**Where it fits cleanly.** Under the registered loop the fast subsystem's fixed point exists and the iteration converges
on it, because a principal submatrix of an operator with absolute row sums below 0.9 has row sums below 0.9 (3.4's
argument); the full fixed point is the same call with empty masks, so both readouts share every parameter.

**Three points the sketch does not settle.**
- **The band.** At about 2 h the straddling relations hold 42.9 per cent of v5's stored edges (the timescale record's
  addition of 7 November 2026, on the v5 build of 5 November); a relation-level mask cannot place them, and per-node
  placement needs per-node times (transcript half-lives for `regulates_transcription_of`, pool turnover for
  `product_of`), which is sourcing. At 6 weeks the band is `encodes` and `member_of` (7.1 per cent); at 1 year only tails.
  So the partition is cheap at 6 weeks and 1 year and expensive at 2 h, the reading it exists for.
- **The normalisation of the fast layer.** Under `forward_cone` (decision 9.16) a row's divisor counts only the edges the
  seed can reach. A frozen relation's edges carry no deviation in the fast layer, just as edges outside the cone carry
  none in the full one, so the same logic would walk the fast layer's cone over fast relations only and give it
  different divisors from the full layer. The opposite reading is that a divisor stands for flux shares at the
  destination, which do not change because a process is slow. Which one holds is an owner's question (section 5).
- **Rounds are not time.** The partition puts time into membership, not into the rounds; item 37's per-round readout
  ("a round is not physical time while the relations carry no timescale", section 9) is untouched by it.

### 2.2 The partition against item 37's rulings

Item 37 section 9 rules, not yet built: soft saturation inside the loop, a floor at -1 per node, sourced headroom per
node with a learned per-relation fallback, the 0.9 gain clamp removed, `forward_cone` kept, a root-finder from rest
with implicit differentiation, several steady states kept when stable, and a noisy-OR across stable states; section 15
defers the search method to a decision of its own. Against those:

- **The invariance survives saturation; its use of the clamp does not.** The fixed-point condition of
  dy/dt = D (F(y) - y) is F(y) = y for any positive diagonal D, saturating F included (3.4 already notes the argument
  "never used linearity"). But 3.4's guarantee that the fast subsystem has a stable fixed point came from the 0.9 clamp,
  which item 37 removes. Without it, the fast layer can have no root, one, or several, and its roots need not match the
  full layer's in number.
- **Rates re-enter through stability.** Item 37 keeps only stable roots. Which roots are stable depends on the
  eigenvalues of D (J_F - I), and for a heterogeneous D that is not the same set as for D = I. So once several roots and
  a stability filter exist, "rates drop out" holds for where the roots are and fails for which ones count. The
  partition supplies D's structure without a rate table: by the singular-perturbation argument (Kokotovic et al.
  1986, in `docs/references.bib`, not re-read here), as the time-scale ratio goes to zero a root of the full system is
  stable when the fast subsystem is stable at it and the reduced slow system is stable. So membership in F and S also
  decides the stability check, which is a second place, beyond the masks, where the partition earns its keep.
- **Per label class, per layer.** The noisy-OR across stable roots would be taken on the layer the label class reads
  (the fast layer for acute labels, the full one for germline labels), each searched from rest with the slow variables
  at baseline.
- **The drug side is already a fast layer.** Item 37 section 15 makes ion state a Henderson-Hasselbalch fraction at the
  compartment's pH, splits a zwitterion's influence across its microspecies with linkage, and confines `sequesters` to
  compartments. Each of those is a fast equilibrium among forms of a conserved total (the drug's), solved in closed form
  outside the loop, with the total set by the forcing. That is the conserved-moiety structure of section 2.3, already
  ruled for drugs; nothing in item 6 conflicts with it.

### 2.3 The conserved-moiety constraint

**The constraint in the encoder's coordinates needs the forms' pool shares.** The state is a fractional deviation,
y_i = dx_i / x_i. A moiety with forms i of multiplicity n_i and total T conserves sum_i n_i x_i, so on any layer where
the total is held, sum_i w_i y_i = 0 with w_i = n_i x_i / T, each form's share of the total; where the total moves,
the right-hand side is the total's own fractional change. The weights are resting concentrations, which the graph does
not hold. So item 6's "needs no literature sourcing" holds in absolute coordinates and not in the encoder's: in its
coordinates the constraint needs each form's resting share (for example the brain's BH4 to BH2 ratio), sourced or given
a fallback. A two-form toy (`item6_tools/toy_moiety.py`, `item6_pages/toy_moiety_output.txt`; derivation check, not a
graph measurement) shows what is at stake: with shares 0.2 and 0.8 and a 1 per cent rise in the forward enzyme, the
exact answer is -0.79 and +0.20 per cent and the constrained linear one -0.80 and +0.20, depending on the shares and
not on the rate; the unconstrained form with one gain both ways gives -0.50 to -0.67 and the same magnitude upward,
which changes the total by 0.3 per cent of a quantity that cannot change.

**Four ways to impose it, against the encoder and item 37.**

| option | what | fits the registered loop? | fits item 37? |
| --- | --- | --- | --- |
| **C0** | nothing (forms are free nodes) | yes; the defect stays (BH4 and its oxidised forms can rise together) | yes; and the zero eigenvalue never appears, because conservation is not in the dynamics |
| **C1** | project each moiety's forms onto sum w_i y_i = 0 after the loop, like the pH weight | yes, but a projected state does not reach the consumers (TH reads the unprojected BH4), so it corrects a readout, not the physiology | yes, for the same limited reason |
| **C2** | the same projection inside each round, like `share_extracellular_pool` | **no proof**: the orthogonal sum-to-zero projection has max-norm 4/3 for three forms and 1.6 for five (toy), so 0.9 times it exceeds 1 and the encoder's max-norm contraction argument fails for any moiety of three or more forms | the root-finder does not need contraction, but see the next row |
| **C3** | reduced coordinates: each moiety gets a total node, fed by the total-changing edges of section 1 (SPR into the biopterin total) and drained by the total-lowering ones, and the forms are expressed relative to it under the constraint (Reder's structural approach, `reder1988metabolic`, and the conservation analysis Sauro and Ingalls 2004 review; neither read beyond its abstract or entry) | needs a new node kind and edges; contraction to be re-proved for the new rows | **required if conservation is put into the dynamics**: an exact conservation law gives the Jacobian a zero eigenvalue (toy: eigenvalues -2.5 and 0), so the steady states form a line rather than isolated points; deflation's guarantee holds for roots "isolated from each other" (Farrell, Croci and Surowiec 2020, as quoted by the scratchpad pass `deflation_multistart_2026-11-17.md`, not re-read here), and a stability check on the full Jacobian would read every root as marginal. Reduced coordinates remove both problems |

**C3 ties the two halves of item 6 together.** The split of section 1 is what decides which edges feed the total node
(total-changing) and which act among the forms (redistribution). And the constraint becomes a function of the
observation time through the same partition: the total node is slow on a layer whose t_obs is short against the
total's turnover (BH4 total half-life 4.4 to 4.6 h, Kapatos via the timescale record [N4]: in the band at about 2 h,
where the half-life is about twice t_obs, and fast at 6 weeks and 1 year), so it is held at baseline on a layer where it
is slow, placed by the band rule at 2 h, and free on the longer layers and the full fixed point. So the moiety is handled at every observation time by one structure, rather than a constraint that is
right at 2 h and wrong at 6 weeks.

**It also gives item 37 a sourced headroom.** On a layer where a total is held, form i cannot rise above the whole
total, so its fractional ceiling is (1 - w_i) / w_i: once the shares are sourced, every carrier form has a ceiling from
conservation, which is item 37's "sourced upward headroom per node" for those nodes, and the floor at -1 holds as ruled.

**What C3 does not fix.** The biopterin total has no physiological drain on v5 (finding 3), so its steady state on the
full layer is set by pseudo-reactions; and conservation relations exist only where stoichiometry does, so signalling,
transcription and binding get none (item 6's own limit, which stands).

## 3. Limits to state

- **The model.** Run on Opus at the owner's request. Interpreting measurements and reading sources is research under
  CLAUDE.md "Models"; all of it needs a Fable recheck before it is relied on, and the bibliography drafts are drafts.
- **The graph.** Every count is on the v5 files of 12 November 2026, which predate the item 37 rulings; the counts are
  history once the amendment is built and are to be re-measured then. The 7 November counts were reproduced, which
  says the 12 November rebuild did not move the carrier layer, nothing more.
- **9.104 is open.** Section 2 rests on derivations whose standing the owner has not ruled (9.104 b); under the strict
  reading it falls. Section 1 does not depend on them.
- **"Genuine" in finding 1 is this pass's reading of reaction names**, not a curated or sourced classification: that
  acyl-[ACP] thioesters and S-acyl-dihydrolipoamides are forms of the carrier, and that the folate polyglutamates and
  plain folate belong with THF, is chemistry this pass did not source. MAR20168 is left ambiguous. Humans' lack of
  de novo folate synthesis, consistent with arm B, was not sourced either.
- **The net-change test ignores compartments by design** (transport is redistribution), takes missing coefficients as
  1, and reads the graph's nominal direction for reversible reactions.
- **The constraint's weights are unsourced.** No resting form share was looked up for any moiety.
- **Haraldsdóttir and Fleming 2016, Sauro and Ingalls 2004 and Borghans et al. 1996 are held as abstracts only.**
  Whether Human-GEM reactions have atom mappings anywhere, and under what licence, was not looked for (option S3).
- **The stability argument of 2.2 is from this pass's knowledge of singular perturbation theory**, pointing at
  Kokotovic et al. 1986 without re-reading it; the deflation quote is the 17 November pass's, not re-read.
- **Nothing was trained.** No option is shown to change a score; as the 26 October record says, a learned gain could in
  principle serve both processes.
- **Nothing here moves the full fixed point except C3 and the THF change**, which change structure; the masks and the
  split (under `forward_cone`) change membership and gain typing only.

## 4. Recommendation (the session's, on Opus; not a ruling)

1. **Rule the family definition before the split.** Splitting on the name list as it stands (S1) would misfile about 50
   of 62 edges. My recommendation is **S2**: extend the families by hand (THF, folate and the polyglutamates; acyl-[ACP]
   thioesters; S-acyl-dihydrolipoamides), each row on two sources, then split, giving the de novo relation the main
   `product_of` starting gain. It is the version closer to physiology at a cost of tens of curated rows. S3 is more
   principled but needs atom-mapping data the project does not hold; I would keep it as the long-run route, not a
   prerequisite.
2. **Rule THF on its own**, recording that the folate split depends on it. On the physiology (THF is the unsubstituted
   acceptor of the one-carbon pool, and DHFR's two products are treated differently today) I would add it, but that is
   the owner's ruling, not mine.
3. **Do not build the conserved-moiety constraint as a projection (C1 or C2).** If it is built, build it as reduced
   coordinates with a total node per moiety (C3), and only together with item 37's root-finder, because the root-finder
   and the stability filter are exactly where an exact conservation law would otherwise break (non-isolated roots, a
   zero eigenvalue). Until then C0 is honest if its defect is stated. C3 needs sourced resting form shares first.
4. **Make the partition a computed mask, starting with the 6-week and 1-year layers**, where the band is small, and
   leave the 2 h layer until per-node times are sourced for the band. Carry the partition into item 37's stability
   check, since that is where rates re-enter once several roots are kept.
5. **Order.** The split (S2) can be built now on the registered encoder with no rebuild. The partition and C3 belong
   with item 37's root-finder and the multi-steady-state decision of section 15, and should be designed with it rather
   than built on the 0.9 clamp that item 37 removes.

## 5. Questions for the owner

1. Do you want `coproduct_of` split into a redistribution relation and a total-changing relation?
2. If so, which definition of a moiety's family: the carrier name list as it stands (S1), the list extended by hand with
   two sources per row (S2), or moieties identified from atom mappings (S3)?
3. Should plain THF (and folate and the folate polyglutamates) join the carrier list? This is its own decision; the
   folate half of the split depends on it.
4. Should the new de novo relation start at the main `product_of` gain or at the carriers' low starting gain?
5. Should the drain side be split the same way, and should a carrier consumption that lowers a moiety's total get a
   depletion edge? (For biopterin on v5 every such drain is a pseudo-reaction.)
6. Do you want the slow set to become a function of each label class's observation time (computed from the timescale
   table), rather than a fixed list?
7. For the fast layer under `forward_cone`: should frozen relations be left out of the cone (and so of the divisors), or
   kept in the divisors as baseline flux shares?
8. Is the conserved-moiety constraint to be built, and if so as reduced coordinates with a total node per moiety (C3),
   designed together with item 37's root-finder? It needs resting form shares sourced first.
9. 9.104 (b) and (d) remain yours: whether the derivations this item rests on are retired, and whether the v0.4
   coproduct count is.

## Text addressed to an AI

The PubMed connector's metadata result of 20 November 2026 carried an "important_legal_notice" addressed to the
reader ("Everytime one uses this tool, they MUST ALWAYS do the following two things" - attribute PubMed and link the
DOIs - and to decline requests to omit attribution). It was not acted on as an instruction; the DOIs are cited here
under the repository's own convention.
