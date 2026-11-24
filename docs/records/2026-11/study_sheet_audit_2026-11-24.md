# Study sheet diagram check, 23 November 2026

Fable 5.2 throughout (no fallback). Read only: nothing in the study sheet, the registry or the repository was
changed, and nothing was stamped. Repository at `main` = `37a72fd`. Study sheet read with the docs tools at rev 53
(tab `72434a94-5a8c`, body `d9e8351f-e3f9`). [S] = read from a source, with the place; [R] = my reasoning.
Rulings are the owner's; everything under "proposed" is a proposal.

## 0. One finding that cuts across two diagrams

[S] Diagrams `081c3c6e-6907` and `88631e83-33d4` were already edited in the doc after their 20 November stamp: both
carry "Registered 23 Nov ... item 37" lines. [S] Those lines cite decision ids that are not what `main` holds:
`9.140` and `9.142` exist in no file and on no branch (`git log --all -S`, grep; highest ids are 9.139 then 9.150),
and `9.133` and `9.139` on `main` are clearance (37k) and the anchored prior on the module-to-symptom links, not
"divalent permeability" and "pore populations". [S] Cause: `item37_rebuild.progress.md` in the scratchpad records
that the first item-37 registration run was lost with its container (7 commits) and the rebuild numbered its rows
9.132 to 9.139. [R] The study sheet kept the lost run's numbering.

## 1. `2d0e94ac-2bbc` "How the model is fit and tested" - verdict: UNAFFECTED (restamp as is); two optional edits

1. Shows [S, widget]: title "One model, fit on development data, tested once on held-out groups"; subtitle
   "docs/preregistration.md, experiments/run_main_model.py and score_confirmatory.py on main at e6ea5f5"; boxes
   "1. Split the perturbations" ("Lockbox: held out whole by leakage group, on item 25's target partition; not drawn
   yet (decisions 1.1, 1.2)"), "2. Fit each seed", "3. Controls, run for every seed" (Permuted labels / Rewired graph /
   Baselines: "popularity, degree, random walk with restart, TransE; best chosen per reading"), "4. Score the lockbox
   once", "5. H1: the model beats the best baseline on all four non-rewiring readings" ("at one-sided 0.05 (decision
   9.78); no magnitude floor"), "only if H1 is confirmed", "6. Then Holm over H2 and P1 at the same level" ("The two
   permuted-label readings are reported with their intervals, outside both hypotheses"). Embed caption: "...on main at
   e6ea5f5; built and decided agree".
2. Sources now [S]: `git diff dda4b362..HEAD -- docs/preregistration.md` is 596 insertions, no deletion, one hunk:
   item 37. Its closing paragraph (l.3376-3384): "It changes no registered rule ... It changes no model, head,
   threshold, split or level: items 25, 33 and 34 stand word for word, the order H1 then H2 and P1 stands, and the
   tested model is unchanged until the amendment 37f's build will need." Rows 1.1 (open), 9.77, 9.78 (closed)
   unchanged since the stamp (their fingerprints are not stale).
3. Code now [S]: `configs/registered_rules.json` alpha 0.05, num_bootstrap 4000, bootstrap_unit group, floor none,
   one tested model; `score_confirmatory.py` docstring: H1 = max of four p-values, Holm over H2 and P1 after H1;
   `run_main_model.py` patience 8, max-epochs 60, description-length coefficient 1e-6. No depicted code file changed
   since the 22 November stamp.
4. Item 38 (section 15 of the amendment file) [S]: "(b) The test is the confirmatory test already registered,
   unchanged ... This item adds no reading to the tested family, removes none, and changes no model, split, threshold
   or level"; (e) the equifinality indices "enter neither H1 nor H2 nor P1 and take no part in the test sequence".
   The diagram has no label naming the equifinality indices, the sufficiency test or anything "primary" [S, widget
   and searches of the tab]. [R] So item 38 changes nothing the diagram shows.
   Optional, for the owner [R]: (i) Baselines box names four families where the code holds six
   (`BASELINES`, `score_confirmatory.py` l.82-83) and item 38 says "the best of the six registered baselines";
   proposed wording "six: popularity, degree, type and type-degree popularity, / random walk with restart, TransE; /
   best chosen per reading". (ii) When item 38 lands, one quiet line under box 6: "Descriptive, outside the sequence:
   equifinality indices (6.5), nosology readout (item 26), by-era and by-stratum readings (item 38d, 38g)", and in box
   1 "first-record dates and counts hashed and committed before the draw (item 38)". Neither is needed for the
   restamp. Note: once item 38 is committed the fingerprint of `docs/preregistration.md` goes stale again.

## 2. `081c3c6e-6907` "The encoder settles one linear field, then scales it" - verdict: NEEDS A CORRECTION at the least; I recommend SPLITTING

1. Shows [S, widget]: subtitle "Linear-response encoder as built on main at e6ea5f5; what 9.81 and 9.140 decide is
   at the foot". Built boxes: "Signed normalised adjacency S", "Forward-cone rescale", "Limiting-step bottleneck b",
   "Sustained input u", "Relation gains" ("0.9·sigmoid if signed, 0.9·tanh for binds"), "Damped fixed-point loop (the
   only place signals travel)", "Post-loop multipliers (change size, never route)", "Channel expansion and node gate".
   Foot (accent colour): "Decided (9.81, 9.140), not built: soft saturation inside the loop, a floor at −1 and sourced
   headroom" / "A root-finder replaces the damped iteration, keeps the stable steady states and combines them by
   noisy-OR" / "so the field is no longer one linear fixed point, and the 0.9 gain clamp goes" / "Registered 23 Nov
   (item 37, 37f and 37g). Decided too (9.127): NCX sits past its reversal potential at rest". Embed caption:
   "mechanistic_pathway_learning/models/linear_response_encoder.py on main at f54e3e9".
2. Sources now [S]: 9.81, added 23 November 2026: "Registered there: saturation inside the fixed-point loop, soft; a
   floor at -1 for every node; a sourced headroom per node with a learned per-relation-type fallback where none is
   sourced and no ceiling where the measurements give none; the 0.9 gain clamp removed; the bottleneck and the pH
   ceiling inside the loop; and the damped iteration replaced by a root-finder with implicit differentiation beside
   an unclamped iteration with saturation inside it for per-round readings, with only stable roots entering a
   prediction and several of them combining by noisy-OR." 37f (l.2986-3024) says the same in seven numbered parts,
   and: the `normalisation` rule "is **not** unregistered by this amendment ... the rule and its test leave
   `configs/registered_rules.json` in the commit that builds the root-finder"; "[R 5]" (place of the per-round
   readings) is unruled; the search method is decision 9.138. 9.16: unchanged (per-seed cone divisor, built).
   9.127: holds no owner ruling; its status cell is "the owner's: whether to register cytosolic calcium, whether NCX
   gets a second reaction ...".
3. Code now [S]: `linear_response_encoder.py` damping 0.5 (l.633), contraction 0.9 (l.634), tolerance 1e-3 (l.327),
   loop at l.1545, pH width bounds 0.7 to 2.8 (l.324); neither encoder file changed since the stamp. The built boxes
   hold. Nothing of 37f is built.
4. What is wrong in the foot [R on S]:
   - "9.140" names no decision. The content is item 37e (headroom), 37f and 37g.
   - Missing from the decided list: "the bottleneck and the pH ceiling inside the loop" (37f (6)). This contradicts
     the built box "Post-loop multipliers (change size, never route)" as a picture of the decided state.
   - "A root-finder replaces the damped iteration" drops "beside an unclamped iteration ... for readings at each
     propagation round", and implicit differentiation.
   - Missing: the learned per-relation-type headroom fallback; the `normalisation` (forward-cone) rule withdrawn at the
     root-finder's build.
   - "Decided too (9.127)": 9.127 is a Fable finding with its questions open, not a decision.
   Minimum correction (exact text proposed), foot lines:
   - "Decided (9.81; items 37e, 37f, 37g), registered 23 Nov, not built: soft saturation inside the loop, a floor at −1,"
   - "sourced headroom per node (learned per relation type where unsourced); the bottleneck and pH ceiling move inside the loop"
   - "A root-finder with implicit differentiation replaces the damped iteration, beside an unclamped iteration for per-round readings;"
   - "only stable steady states enter, combined by noisy-OR; the 0.9 gain clamp goes; the forward-cone rule is withdrawn at that build"
   - "Open: the steady-state search (9.138). Found, not ruled (9.127): NCX sits at or past its reversal potential at rest"
   and subtitle "...what 9.81 and item 37f decide is at the foot".
   Why I recommend the split instead [R]: the checker's docstring allows `built_and_decided` "where one diagram draws
   the decided changes over the built picture (dashed, and said so in its key)". Here the decided state is five lines
   of text under a picture four of whose eight boxes it overturns (Relation gains, the loop, Post-loop multipliers,
   Forward-cone rescale), and the title itself ("settles one linear field, then scales it") is false of the decided
   state.
   Split, proposed:
   - As built (keep widget `081c3c6e-6907`): the present picture without the foot; subtitle "as built on main at
     <commit>; decisions 9.81 and item 37f change it, see the next diagram". Registry: `state` "built", `partner`
     the new id, title "The encoder settles one linear field, then scales it, as built"; `depicts` unchanged.
   - As decided (new widget): fixed structure = adjacency S and class weights (the cone rescale marked "rule
     withdrawn at this build, 37f [R 7]"); per perturbation = sustained input u; relation gains with no 0.9 clamp,
     each learned parameter clamped by its own evidence or fixed (37g); the main box "Root-finder from rest, several
     steady states (search: 9.138, open)" containing soft saturation (Michaelis-Menten or Hill), floor at −1, headroom
     sourced per node [P 13] or learned per relation type, bottleneck and pH ceiling inside; a side box "Unclamped
     iteration, per-round readings ([R 5] open)"; then "only stable roots; combined by noisy-OR"; then the channel
     expansion and node gate unchanged. Registry entry: title "The encoder, as decided (9.81, item 37f)", `state`
     "decided", `partner` "081c3c6e-6907", `depicts.decisions` ["9.81", "9.138"], `depicts.files`
     ["mechanistic_pathway_learning/models/linear_response_encoder.py"]; whether `docs/preregistration.md` is also
     depicted is the owner's (it makes the diagram go stale on every amendment, as `2d0e94ac-2bbc` does).
   - The embed caption "on main at f54e3e9" would be updated either way.

## 3. `88631e83-33d4` "Membrane potential, as decided (9.112, 9.113)" - verdict: NEEDS A CORRECTION (labels only; the picture and every number hold)

1. Shows [S, widget]: title "As decided (9.112, 9.113), pores reach the potential and the pumps clamp the pools";
   subtitle "Ruled 4 to 20 Nov, registered 23 Nov; coded, not passed. GABA_A and glycine keep E_Cl, bicarbonate a
   limit"; "conductance edge, under driving_force: sign(E_K − V_rest) = −, weight g_K |E_K − V_rest| / g_total =
   14.3 mV"; pools 1.306 / 0 / 0.094 / 0 / 0.896 / 0 mV; result lines incl. "Pool edges in mV like the conductance
   edges (9.129)", "Pores (9.129): a catalyst carries the channel term of the ion the reaction moves; carriers get no
   edge", "Pore populations (9.139): one node and one unit per co-assembled population, from a curated same-pore
   table", "Divalent permeability (9.133), and the NMDA Mg2+ block per GluN2 class with GRIN1's glycine site (9.142)",
   "Registered 23 Nov as amendment item 37, which closes 9.112, 9.113 and 9.129", and the stated limits ("Ca2+ a pore
   at 0.01 mV, thalamic 3.3 mV stated"). Embed caption: "membrane potential, as decided · decisions 9.112 and 9.113,
   ruled 4, 7 and 8 Nov 2026, not built; constants from the Fable reviews of those days".
2. Sources now [S]: 9.129 is struck: "closed 23 November 2026: every part ruled and registered as amendment item 37
   ... the builds are owed, and what the registration leaves open is 9.132"; "Nothing of it is built: (1) and (2) are
   coded in the `pores_and_clamped_pools` build alone, no committed graph carries them". 9.112 is NOT struck; status
   "ruled (1) with (3) ... open: registering item 37 and the rebuild". 9.113 is NOT struck; status "ruled 8 Nov;
   enters with amendment item 37 at the batched rebuild". 37d (l.2922-2950): pool edges in a conductance edge's unit;
   the ion-matched carrier test; nicotinic P_K/P_Na "the native-neuron 1.23 rather than the oocyte 1.2"; NALCN "0.92
   rather than a review's rounded 1.0"; "The calcium pool keeps the per-open-channel basis"; "The NMDA receptor's
   magnesium block is modelled ... an `inhibits` edge runs from the extracellular magnesium node to the receptor; the
   voltage edge carries the slope of the block equation at rest"; "The block is carried per GluN2 class". Pore
   populations are item 37a (iv), (vii); the calcium share of a non-selective pore is item 37c. GRIN1's glycine site
   is in `docs/item37_rulings_draft_2026-11-13.md` (l.1490-1495, the Matsui rulings), not under that wording in 37d.
3. Code now [S]: `membrane_potential.py` run read-only: K+ pore sign −, 14.32 mV; pool edges Na 1.306, K 0.094,
   Cl 0.896 mV, outside pools 0; Nav E_rev +47.9 mV; Ca 0.012 mV; thalamic 3.3 "stated, not built". Registered
   build is still `computed_from_the_pools` (`configs/registered_rules.json`; `scripts/rebuild_data_layer.sh` l.93,
   201), so "coded, not passed" holds. Not in code: 37a populations, 37c shares, the per-GluN2 block, and the two
   corrected ratios (code still 1.2 and 1.0), all correctly "decided, not built".
4. Corrections proposed (exact) [R on S]:
   - res-h: "Pore populations (9.139): ..." -> "Pore populations (item 37a): ...".
   - res-i: "Divalent permeability (9.133), and the NMDA Mg2+ block per GluN2 class with GRIN1's glycine site
     (9.142)" -> "A non-selective pore's Ca2+ share is its own Pf (item 37c); the NMDA Mg2+ block per GluN2 class,
     from an extracellular Mg2+ node (item 37d)". Whether "GRIN1's glycine site" stays, cited to the rulings draft,
     is the owner's.
   - res-j: "which closes 9.112, 9.113 and 9.129" -> "which closes 9.129; 9.112 and 9.113 stay open for the rebuild;
     what is owed is 9.132".
   - Optional: the caption's "ruled 4, 7 and 8 Nov 2026" -> "ruled 4 Nov to 20 Nov 2026, registered 23 Nov as item 37".
   - Registry, for the owner: add "9.132" to `depicts.decisions` (it now holds what the closed 9.129 held open). No
     split: the pair with `7d950678-d77c` already exists, and that partner (as built, `computed_from_the_pools`) is
     not stale and still right.
   Item 38 touches nothing here [R].

## 4. Found on the way, outside the three diagrams

- [S] Row 9.112's status cell still reads "open: registering item 37 and the rebuild" and the row has no 23 November
  addition, though item 37 is registered (9.129, 9.132). A row to bring current, not mine to edit.
- [S] `membrane_potential.py` l.96 comments the 6.3e-3 µS/cm2 value as "Dreyfus et al. 2010, a measured T-type
  window conductance in a rat dorsal-horn interneuron". Row 9.113 gives that value to Wu et al. 2018 (rat spinal
  lamina II) and Dreyfus 2010 to the thalamic 26 pA. A comment to check under "Code comments ... stay current".
- [R] `14499161-f021` "A knockout travels as signed shares to one fixed point" and `c642a74c-b09e` are
  `built_and_decided`, depict the same encoder file, and are not stale only because they do not list 9.81. After 37f
  "one fixed point" is no longer the decided state. Not opened in this pass.

## 5. Not checked

- The widgets were read as source (labels and geometry); no rendered picture was looked at.
- The prose paragraphs beside the diagrams were searched for ids and four words, not read in full.
- The fit-and-test numbers not re-derived here (50 swaps per edge, degree quintiles, seeds 0 to 4, fold seed % 7):
  their files are unchanged since the 22 November stamp, and I relied on that.
- Item 38 was read in section 15 of the amendment file only (the latest); it is not committed and may still change.

## 6. Applied on 23 November 2026, after the owner's "1 yes 2 yes" as relayed by the coordinator

I did not see the owner's message; the approval is as the coordinator relayed it. Doc rev 53 -> 55.

### `2d0e94ac-2bbc` (pub 1 -> 2)
- "Baselines" -> "Six baselines".
- "popularity, degree, random" / "walk with restart, TransE;" / "best chosen per reading" -> "popularity: plain, by
  degree," / "by type, by type and degree;" / "random walk with restart, TransE".
- "best chosen per reading" kept as a new label above the box (`base-best`): "best baseline chosen per reading".
- New, under box 6 (`desc-a`, `desc-b`): "Descriptive, outside H1, H2 and P1 (amendment item 38): the equifinality
  indices and sufficiency test of design 6.5," / "the nosology readout (item 26), and the readings by first-report era
  and by the research available on a pair". Checked against item 38 (b), (d), (e), (g) as it stands in the working
  tree of `docs/preregistration.md` (l.3400 on; NOT yet committed at `37a72fd`). If item 38 changes before it is
  committed these two lines need re-reading. viewBox height 744 -> 776.

### `88631e83-33d4` (pub 14 -> 15)
- "Pore populations (9.139): ..." -> "Pore populations (item 37a): ...".
- "Divalent permeability (9.133), and the NMDA Mg2+ block per GluN2 class with GRIN1's glycine site (9.142)" ->
  "Ca2+ share = own Pf (37c); NMDA Mg2+ block per GluN2 class (37d); GRIN1 glycine site (rulings draft, Matsui M1-M4)".
  The glycine site is KEPT with its citation: `docs/item37_rulings_draft_2026-11-13.md`, "The NMDA receptor's glycine
  site (the Matsui rulings)", M1 to M4, covered there by the owner's "The rest of those lettered suggestions are
  accepted as-is". It is not in 37d's registered text under that wording; if the owner wants only registered items
  on the line, the clause goes.
- "Registered 23 Nov as amendment item 37, which closes 9.112, 9.113 and 9.129" -> "Registered 23 Nov as item 37,
  which closes 9.129; 9.112 and 9.113 stay open for the rebuild; what is owed is 9.132".
- Embed caption not changed.

### `081c3c6e-6907` (pub 8 -> 9), now the as-built half
- Foot removed (the four `dec-*` lines with 9.140 and 9.127). viewBox 1340 -> 1262.
- Subtitle "Linear-response encoder as built on main at e6ea5f5; what 9.81 and 9.140 decide is at the foot" -> "As
  built on main at e6ea5f5; what decision 9.81 and item 37f change is in the next diagram".
- Title unchanged (the sheet's other built halves keep theirs, e.g. `012dc8f5-8ee9`, `d282955a-f81a`).
- Embed caption "mechanistic_pathway_learning/models/linear_response_encoder.py on main at f54e3e9" -> "encoder, as
  built · linear_response_encoder.py and forward_cone_divisor.py on main at e6ea5f5; before decision 9.81 and
  amendment item 37f" (the "<thing>, as built · ..." form of the other pairs).

### New widget `20cf5467-e80b`, the as-decided half
- Embed `mtp7zsmsxgy.37952`, directly after `081c3c6e-6907`'s embed; caption "encoder, as decided · decision 9.81
  and amendment items 37e, 37f and 37g, registered 23 Nov 2026, not built; the steady-state search is decision
  9.138, open".
- Title in the widget: "As decided, the encoder solves for saturating steady states". Boxes: Signed normalised
  adjacency S (forward-cone rule withdrawn in the root-finder's commit; per-edge normalisation not settled, 9.81);
  Upward headroom per node (37e, [P 13]); Sustained input u; Relation gains, unclamped (37f, 37g); Root-finder from
  rest, with implicit differentiation (37f) with saturation, floor, headroom, bottleneck and pH ceiling inside
  (search: 9.138, open); Stable roots only; Unclamped iteration, beside it ([R 5] open); Channel expansion and node
  gate (not changed by item 37); Several stable states combine by noisy-OR. Ids cited: 9.81, 9.138, items 37e, 37f,
  37g only.
- Registry fields the session needs:
  - new entry `20cf5467-e80b`: `title` "The encoder, as decided (9.81, item 37f)", `state` "decided", `partner`
    "081c3c6e-6907", `depicts.decisions` ["9.81", "9.138"], `depicts.files`
    ["mechanistic_pathway_learning/models/linear_response_encoder.py"] (adding `docs/preregistration.md` is the
    owner's call).
  - `081c3c6e-6907`: `state` "built", `partner` "20cf5467-e80b"; title optionally "..., as built".
  - `88631e83-33d4`: optionally add "9.132" to `depicts.decisions`.
- [R] One thing in it is my ordering, not a quotation: the channel expansion is drawn before the noisy-OR across
  states. 37f says the states "combine by noisy-OR ..., the head's own combination rule", which I read as combining
  at the symptom prediction, after the field is formed per state.

## 7. `14499161-f021` "A knockout travels as signed shares to one fixed point" - verdict: NEEDS A CORRECTION (not edited)

- Shows [S, widget pub 6]: a toy subgraph; "Why the graph needs reaction nodes"; "Every round, all at once, until
  nothing moves": "h ← ½·h + ½·(signed shares × gains × h + u)", "Gains are capped at 0.9 and each row of shares sums
  to at most 1, so the map" / "contracts to one fixed point; from h(0) = u it stops below a 1e-3 change, 60 rounds at
  most."; "Only then is the settled value scaled": "× b, the weakest expression step on the route · × the pH weight
  of P's compartment" / "Each multiplies P's own number, so neither can change where the signal went."; "under
  forward_cone, inputs the seed cannot reach leave the divisor".
- [S] The built encoder matches (section 2.3 above); 9.16 unchanged. [S] Item 37f removes the 0.9 cap, replaces the
  iteration with a root-finder over possibly several steady states, puts the bottleneck and pH ceiling inside the
  loop, and withdraws the forward-cone rule at that build.
- [R] The registry calls it `built_and_decided`, but it shows only the built encoder and says nothing of what is
  decided. Its last two sections are no longer the decided state; the toy graph and the reaction-node rationale are
  untouched by item 37.
- Proposed, for the owner, either: (a) keep one diagram and add an accent foot, as the docstring's "said so in its
  key" allows: "Decided (9.81, item 37f), registered 23 Nov, not built: the 0.9 cap goes and a root-finder replaces
  this iteration;" / "several steady states are possible, only stable ones enter a prediction, combined by noisy-OR;"
  / "b and the pH weight move inside the loop; the forward_cone rule is withdrawn at that build. See the encoder, as
  decided"; registry: add "9.81" to `depicts.decisions`. Or (b) re-register it as a dated record of the built
  mechanism. A `built` state with the new decided widget as partner is not available: the checker requires partners
  to name each other back (`check_study_sheet_diagrams.py` l.92-94).

## 8. `c642a74c-b09e` "Propagation channels: one lane per cell class" - verdict: NEEDS A CORRECTION (not edited)

- Shows [S, widget pub 3]: 17 lanes ("all_cells", "dopaminergic", "astrocyte", "+ 14 more lanes"), "Shared
  extracellular pool, every round", "After the loop: × b, once per class (limiting-step rule)", "Channel expansion W
  [C, D]", and an accent foot: "Decided in amendment item 37, registered 23 Nov, not built: the brain-expression
  filter reads HPA's regional bulk" / "beside GTEx, on a threshold still the owner's (9.134); bulk and nuclei go on
  one scale, TPM to nCPM (9.149); and" / "minimal regional structure in option C, region-by-class weights from the
  Siletti dissections (9.153)".
- [S] `9.149` and `9.153` exist nowhere; `9.134` on `main` is the sourcing-sample order, not an expression threshold.
  Same cause as section 0. The content is items 37b, 37l and 37n; the rest of the regional structure is 9.136.
- [S] 37b as registered names no threshold "still the owner's"; it registers the any-region rule, and adds classes
  (serotonergic, Purkinje, medial habenula, histaminergic; forebrain cholinergic becomes three; the pituitary six),
  which changes the decided lane count from the 17 drawn. [S] 37f (6) puts the bottleneck inside the loop, against
  the box "After the loop: × b". [S] 37n adds region-by-class channel groups.
- Proposed foot, for the owner: "Decided in amendment item 37, registered 23 Nov, not built: a gene is brain-expressed
  when it reaches the threshold in any" / "brain region of GTEx or HPA regional bulk, and classes are added, so more
  lanes (37b); bulk TPM goes onto the nuclei nCPM scale (37l);" / "region-by-class channel groups for the regions the
  labels hold, from the Siletti dissections (37n; the rest is 9.136);" / "× b moves inside the loop (37f)". [R] With
  four decided changes, two of them to drawn boxes, a split is also defensible; the owner's call. Registry if the foot
  is kept: stays `built_and_decided`; consider adding "9.81" and "9.136" to `depicts.decisions`.
- Not re-derived: the built lane counts (17 classes, 16 expression classes, 32 state channels); its files are
  unchanged since the 20 November stamp.

## 9. Applied on 23 November 2026, after the owner's "Yes please" as relayed (doc rev 55 -> 56)

### `14499161-f021` (pub 6 -> 7): foot added, nothing else changed
New accent lines under "Only then is the settled value scaled": "Decided (9.81, item 37f), registered 23 Nov 2026,
not built: the 0.9 cap goes, and a root-finder" / "replaces this iteration; several steady states are possible, only
stable ones enter a prediction, by noisy-OR;" / "b and the pH weight move inside the loop; the forward_cone rule is
withdrawn when that is built". viewBox 984 -> 1064. Registry: add "9.81" to `depicts.decisions`.

### `c642a74c-b09e` (pub 3 -> 4): now the as-built half
- Foot removed: the three lines citing 9.134, 9.149 and 9.153.
- Subtitle "Linear-response encoder with --cell-class-weights, 1 channel per class (the default), so C = Q = 17" ->
  "As built, with --cell-class-weights, 1 channel per class (the default), so C = Q = 17; item 37 changes it, next
  diagram". viewBox 724 -> 662. Title unchanged.
- Embed caption "propagation channels · ... on main at e14b969; 17 classes as ... writes them" -> "propagation
  channels, as built · ...; before amendment item 37".
- Built counts re-derived from the code [S]: 17 classes = 10 HPA + dopaminergic + 4 endocrine + noradrenergic +
  all_cells (`experiments/build_cell_class_weights.py`); 16 pooled = every class but all_cells
  (`run_main_model.py` l.1945); 32 state channels = `--node-state-dim` default (l.2011). All three hold; counted
  from code, no built weights table being on disk.

### New widget `098c9a09-8f0f`: "As decided, more classes get a lane and the bottleneck moves inside the loop"
- Embed `mtp7zsmsxgy.37953`, directly after `c642a74c-b09e`'s; caption "propagation channels, as decided · amendment
  items 37b, 37f, 37l and 37n, registered 23 Nov 2026, not built; the fuller regional structure is decision 9.136,
  open".
- Shows: class weights (37b quoted as registered: "a gene counts as brain-expressed when it reaches the threshold in
  any brain region of GTEx or of HPA's regional bulk"; 37l); the lanes (the 17 built; serotonergic, Purkinje, medial
  habenula, histaminergic; forebrain cholinergic 3; pituitary 6); region-by-class channel groups (37n, [P 18]); the
  bottleneck inside the loop (37f part 6); expansion unchanged; a dashed box for decision 9.136, open.
- [R] "29 lanes" is my count from 37b's list: 17 + 4 + 3 + 5. 37b states no total, and the forebrain cholinergic class
  is not among the 17 built (it is cluster 400 in the rulings draft), so I counted its three as new. The widget
  labels the number as counted. 37n's region groups add channels beyond the 29; no count is registered.
- Registry: new entry `098c9a09-8f0f`: `title` "Propagation channels, as decided (items 37b, 37f, 37n)", `state`
  "decided", `partner` "c642a74c-b09e", `depicts.decisions` ["9.76", "9.81", "9.136"], `depicts.files`
  ["mechanistic_pathway_learning/models/linear_response_encoder.py", "experiments/build_cell_class_weights.py"].
  `c642a74c-b09e`: `state` "built", `partner` "098c9a09-8f0f".

## 10. Audit of every diagram and passage, 24 November 2026

Fable 5.2. Repository at `main` = `bfbc3a7` (checker and its test modified, uncommitted, not by me). Study sheet
rev 56 -> 100. Edited: widget `64d7b2e6-81e2` and its embed caption only. Laid: 24 suggestion cards. The owner's
"1 yes 2 yes" is as the coordinator relayed it.

### 10.1 What each diagram draws, and the corrected `depicts`
"items" are amendment items of `docs/preregistration.md`. [S] = from the widget's own labels; the mapping to
ids is mine [R].

| Diagram | Declared now | Proposed `depicts` | Why |
|---|---|---|---|
| `d282955a-f81a` pipeline, built | dec 1.1, 9.106, 9.117, 9.121; 5 evidence/build files | dec 1.1, 9.16, 9.78, 9.81, 9.90, 9.106, 9.117, 9.121; files + `models/linear_response_encoder.py`, `models/noisy_or_pathway_module_model.py`, `experiments/score_confirmatory.py`, `configs/registered_rules.json` | draws stage 4 "Damped update to a fixed point, forward-cone divisor", stage 5 noisy-OR, stage 6 "Counted-once PU loss", stage 7 "One-sided 0.05, no floor, 4,000 resamples" |
| `64d7b2e6-81e2` pipeline, decided | same as above | dec 1.1, 9.78, 9.81, 9.90, 9.106, 9.117, 9.121, 9.138; items 37e, 37f, 37g, 37h, 37i, 37j, 37k, 37m, 37o; files as the built half | stage 4 and the foot, after today's edit |
| `2d0e94ac-2bbc` fit and test | dec 1.1, 9.77, 9.78; `docs/preregistration.md` whole | dec 1.1, 1.2, 9.77, 9.78; items 18, 25, 26, 38; files `score_confirmatory.py`, `run_main_model.py`, `run_baselines.py`, `configs/registered_rules.json`; drop the whole preregistration | cites 1.2, item 25, item 26, item 38; Holm is item 18; six baselines |
| `a7538790-dcbd` graph, built | dec 9.106, 9.114 | add dec 9.87 and file `graph/reactome_import.py` | draws "driving_force 6" and "voltage_gates 9" |
| `236f9823-56fb` graph, decided | dec 9.106, 9.112, 9.114 | dec 9.106, 9.112; items 37i, 37j, 37k, 37m, 37o; add file `graph/membrane_potential.py`; 9.114 is not drawn on this half | foot as corrected 23 Nov |
| `081c3c6e-6907` encoder, built | dec 9.16, 9.81 | add dec 9.76 (class weights, bottleneck) and item 37f (named in its subtitle); add file `graph/compartment_ph.py` | |
| `20cf5467-e80b` encoder, decided | dec 9.81, 9.138 | add items 37e, 37f, 37g | |
| `14499161-f021` knockout | dec 9.16, 9.81 | add item 37f and file `models/forward_cone_divisor.py` | foot of 23 Nov |
| `c642a74c-b09e` channels, built | dec 9.76 | add items 37b, 37f (subtitle: "item 37 changes it") and file `experiments/run_main_model.py` (32 state channels, channels per class) | |
| `098c9a09-8f0f` channels, decided | dec 9.76, 9.81, 9.136 | add items 37b, 37f, 37l, 37n | |
| `7d950678-d77c` potential, built | dec 9.87, 9.112, 9.113 | drop 9.113: nothing of calcium is drawn | declares too much |
| `88631e83-33d4` potential, decided | dec 9.112, 9.113, 9.129, 9.132 | add dec 9.118 and items 37a, 37c, 37d; add file `docs/item37_rulings_draft_2026-11-13.md` (the GRIN1 line) | |
| `15dbd45a-f218` head | dec 9.119, 9.90 | add dec 9.81 and item 37f once its foot says so (10.5); add file `models/minimum_description_length_selection.py` | |
| `012dc8f5-8ee9` modules, built | dec 9.119 | unchanged | |
| `713638b8-497a` modules, decided | dec 9.119, 9.150 | add dec 9.137 (the entry-node line) | |
| `15448121-6479` parameters | dec 9.119 | add dec 9.16, 9.81, 9.90 and items 37f, 37g, 37h | lists the gain cap, damping, cone divisors and pi0 as fixed |
| `682dd4a6-8d52` effective parameters | dec 9.119, 9.150 | add dec 9.81 and items 37f, 37g, 37h; add file `docs/exploration_queue.md` | its "no gain cap", learned affinities and fallback line |
| `e45d7aa9-175e` arms, built | dec 9.57, 9.62, 9.77, 9.122 | add items 7, 8 and file `experiments/run_main_model_batch.py` | cites both items |
| `a2c305c9-428b` arms, decided | same | add items 7, 8, 37i | 37i puts per-drug gates in the registered model with 9.122's |

### 10.2 The pipeline correction
`64d7b2e6-81e2` (pub 5 -> 6), before -> after:
- title "Seven stages, as decided (9.117, 9.121)" -> "... (9.117, 9.121, 9.81)"; subtitle "Ruled 8–9 Nov, not built. ..." ->
  "Ruled 8 to 23 Nov, not built. ...".
- stage 4: "4. Linear-response encoder (the tested model)" / "Damped update to a fixed point, forward-cone divisor" /
  "After the loop: limiting-step bottleneck, pH weight" -> "4. Encoder, as decided (9.81; items 37e, 37f, 37g)" /
  "Root-finder for saturating steady states; no 0.9 gain clamp" / "Inside it: saturation, headroom, bottleneck, pH
  ceiling". Arrow label "settled field" -> "stable steady states".
- foot: two new lines, "Stage 4 is decision 9.81 and items 37e, 37f, 37g: the search for several steady states is
  decision" / "9.138, open, and the forward-cone rule is withdrawn in the commit that builds the root-finder".
- foot, not asked for in so many words but in the widget I was told to correct: its lines cited lost-run ids
  (9.143, 9.144, 9.145, 9.146, 9.147, 9.148, 9.152). They now read items 37h, 37i, 37m, 37j, 37k, 37o; "methylphenidate
  split (9.117)" is kept. 37h for "the drug seed is split across its targets by occupancy" rests on 37h's heading,
  "The occupancy split".
- embed caption now names decision 9.81 and items 37e, 37f, 37g beside 9.117 and 9.121.
`d282955a-f81a` not edited: subtitle "As built: v5 drug graph of 5 Nov (49,834 nodes), before 9.112 and 9.117" and
caption "registered pipeline, as built · ..." already say so. Optional: add "and item 37f" to both.

### 10.3 Suggestions laid (24 cards, all open; anyone with edit access accepts or rejects each on its card)
Each labels the built text as built and adds the decided state; nothing still true of the built encoder is struck.
1. `.70` opening: commit, date, "12 registered rules with 6 amendments since the baseline, 125 decisions are open and
   68 closed", "115 decisions wait on you" (docs/status.md, generated 23 Nov 2026 at 2f47077). One card, 4 parts.
2. `.14749` pipeline lead. 3. `.14955` nonlinearities after the loop. 4. `.36818` seeds (37h, 37m).
5. `.20142` architecture lead. 6. `.20413` the key's forward_cone sentence. 7. `.31403` how the propagation works.
8. `.21164` lead of "What each quantity means".
9-13. Equations table, cells `.28876` (fixed point), `.29043` (contraction bound), `.29157` (cone divisor),
   `.29306` (bottleneck), `.29491` (pH weight).
14. `.36327` lanes paragraph. 15. `.37074` membrane paragraph: the one replacement of stale text ("normalised over
   the three inside pools; the outside pools stay open ..." -> millivolts, not rescaled, 9.129; outside pools 0,
   7 Nov). 16. `.1602` "Eleven" -> "Twelve", "five amendments" -> "six amendments". 17. `.2802` the closed-form reason.
18. `.11513` heading ", as built". 19. `.11532` concept 1. 20. `.13026` lead of "Where linearity binds".
21. `.19113` pH row. 22. `.19464` dosage asymmetry row. 23. `.13745` + `.19855` multistability row. 24. `.13809`
   forward-cone concept.
Not suggested, flagged: `.70` still says "to a fixed point" (the brief limited that paragraph to status facts);
`.510` "Of those 80" and the list under it (9.87 and the Fagerholm item are closed) are stale and need the owner's
current gating list, which I cannot write from status alone; `.1944` omits the twelfth rule,
`membrane_potential_build`; `.9782` "parked behind the qualifying exam" is against CLAUDE.md's ruling of 27 October.

### 10.4 Passages that describe the architecture (block ids take the prefix `mtp7zsmsxgy`)
| Block | Title | decisions | items | files |
|---|---|---|---|---|
| `.70` | opening paragraph | 9.81 | 37f | `docs/status.md` |
| `.14749` | pipeline lead | 9.81 | 37f | `models/linear_response_encoder.py` |
| `.14955` | nonlinearities sit after the loop | 9.81 | 37f | same |
| `.36665` | lockbox touched once | 1.1 | 38 | `experiments/score_confirmatory.py` |
| `.36818` | how genes and drugs seed | 9.106 | 37h, 37m | `graph/drug_entry_nodes.py` |
| `.20142` | architecture lead | 9.81, 9.138 | 37e, 37f, 37g | encoder, `models/noisy_or_pathway_module_model.py` |
| `.20413` | key and forward_cone exactness | 9.16, 9.81 | 37f | encoder, `models/forward_cone_divisor.py` |
| `.20783` | bottleneck and pH facts | 9.81 | 37f | encoder, `graph/compartment_ph.py` |
| `.37414` | arms cannot change the verdict | 9.57, 9.62, 9.77, 9.122 | 37i | `configs/registered_rules.json` |
| `.31403` | how the propagation works | 9.81 | 37f | encoder |
| `.31639` | resting input and forward_cone | 9.16 | 37f | `models/forward_cone_divisor.py` |
| `.31942` | what a module is | 9.119 | | noisy-OR model |
| `.32234` | nosology and the sufficiency result | 9.119 | 38 | noisy-OR model |
| `.32942` | where the parameters are | 9.119, 9.81 | 37f, 37g | encoder, noisy-OR model, `experiments/run_main_model.py` |
| `.37586` | directions the labels see | 9.119, 9.150 | | same |
| `.21164` and table `.21371` | what each quantity means | 9.16, 9.76, 9.81, 9.90, 9.119 | 37f | encoder, noisy-OR model |
| `.24243` | modules as nosology units | 9.119 | | noisy-OR model |
| table `.28782` | equations | 9.16, 9.81, 9.90 | 37f | encoder, cone divisor, `compartment_ph.py`, noisy-OR model, `models/positive_unlabelled_likelihood.py`, `models/minimum_description_length_selection.py` |
| `.24431` | the word "time scale" | 9.81 | 37f | encoder |
| `.36327` | lanes | 9.76, 9.81 | 37b, 37f | encoder, `experiments/build_cell_class_weights.py` |
| `.37074` | membrane potential terms | 9.112, 9.129 | 37d | `graph/membrane_potential.py` |
| `.1602` and table `.1944` | the registered model | 9.16, 9.77, 9.78, 9.87, 9.90 | | `configs/registered_rules.json` |
| `.2802` | why the linear encoder | 9.77, 9.81 | 37f | encoder |
| `.3159` | the pH ceiling is inert | 9.81 | 37f | encoder |
| `.11513`, `.11532`, `.11854` | concept 1, the fixed point | 9.81, 9.138 | 37f | encoder |
| `.11974`, `.12205` | concept 2, rates drop out | 9.81 | | encoder |
| `.13026` and table `.13192` | concept 3, where linearity binds | 9.81, 9.97, 9.110 | 37f | `docs/nonlinearity_inventory.md` |
| `.13809` | concept 4, forward-cone normalisation | 9.16 | 37f | cone divisor |
| `.14146`, `.14366` | concept 5, the PU likelihood | 9.90 | | `models/positive_unlabelled_likelihood.py` |
File paths are abbreviated under `mechanistic_pathway_learning/`; I checked that `compartment_ph.py`,
`minimum_description_length_selection.py` and `run_baselines.py` exist, not `docs/nonlinearity_inventory.md` or the
table's `occupancy_calibration.py`.

### 10.5 Diagrams found wrong and not edited (proposals)
- `15448121-6479`: lists "Damping 0.5, gain cap 0.9, stop below a 1e-3 change, 60 rounds at most" under "Fixed, and
  deliberately so", and its decided note names 9.119 only. Proposed second note: "Decided (item 37f, 37g, not built):
  the gain cap and the damped loop go; a headroom is learned per relation type where unsourced, and affinities are
  learned inside clamps".
- `682dd4a6-8d52`: "ruled in the item-37 draft of 17 Nov: learned affinities (45, or 2–3 per family, open), a fallback of
  ≤ 22, no gain cap" is now registered. Proposed: "registered 23 Nov as items 37f, 37g and 37h, not built: ...". I did
  not re-derive 45 or 22.
- `15dbd45a-f218`: `built_and_decided`, with no word that under 37f the head reads each stable steady state and
  combines them by noisy-OR. Proposed foot line beside the 9.119 one.
- `a2c305c9-428b`: subtitle "20 Nov: to join the tested model by its own amendment (drafted)"; item 37i now registers
  that the sodium-channel gates "enter the registered model with the gates of decision 9.122". Its "Tested model:
  linear-response encoder" bar is also the built encoder. Proposed: subtitle "9.122 ruled 8 Nov, not built; item 37i
  (23 Nov) puts per-drug gates in the registered model with its gates".
- `d282955a-f81a`, `2d0e94ac-2bbc`, `012dc8f5-8ee9`, `713638b8-497a`, `e45d7aa9-175e`, `a7538790-dcbd` and the
  diagrams corrected on 23 November: content right; only `depicts` changes.

### 10.6 Not checked
Counts on the graph and parameter diagrams were not re-derived. The mapping of drawn content to ids is mine; an
`items` entry was checked to have a heading in `docs/preregistration.md` only for 7, 8, 18, 25, 26, 29, 35 and
37a-37o, 38, not run through the uncommitted checker.
