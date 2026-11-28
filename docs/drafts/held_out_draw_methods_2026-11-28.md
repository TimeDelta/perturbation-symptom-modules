# Held-out draw: methods that could reduce leakage further (draft, 28 November 2026)

A draft for the owner, answering "please consider other draw methods that could reduce leakage further". It rests on
the repository at `91bc9b8` (28 November 2026), read only, and claims nothing about the current state beyond what that
commit shows. Nothing outside the repository was read and nothing is cited from memory as evidence: "literature owed"
marks each claim a literature pass must source. Every number below is **history**. Each was measured on an October 2026
table or graph, or on release v0.4, and the table or graph is named beside it. None comes from the graph the draw will
be made on, which 9.151 has not built yet. The only graph on this disk is release v0.4 (built 6 October 2026), so no
number about the draw's graph can be taken here, and none was. This note was not written on Fable. Reading code and
rulings is design work, but reading a recorded number towards a choice is research under CLAUDE.md, so a Fable pass
rechecks those readings before any of them enters a decision row. It was written by a design pass of 28 November 2026
from a map of the current rule, four proposal passes and two critiques. Those were kept in the session's scratchpad and
are not committed; every claim taken from them is restated here with the place in this repository it rests on. Nothing in this note is ruled or built.

## 1. The answer

Four changes would reduce leakage further, and this note recommends all four: hold out a held-out target's own gene
with its disease cluster (M1), draw the gene side as a seeded prefix of whole groups (M2), fit each candidate seed's
ceiling inside that seed's own training rows (M3), and commit the seed order and every free definition of 9.35 before
the 9.151 graph is built (M4). None of them rejects a draw, so none becomes the search 9.35 warns against. A fifth,
M5, closes nothing but reports the reading by an exposure fixed at the draw, which reads no labels. The cost is one
amendment item (9.35 already owes one), a change of gene-side grouping that reverses the choice of 9 October 2026, code
in the split and the draw script, and counts on the draw's graph that read no labels. The reading falls only by what
the removed leak was worth, which is credit taken from the model, not a harder draw selected. Every method that removes
graph neighbours (buffers, community or minimum-cut splits, optimised draws) was rejected: on every recorded graph it
empties the training set or makes the held-out set the most isolated mechanisms, and that changes the question.

M1 and M2 matter most, because each meets a gap between what the rulings assume and what the code does. On a
gene/protein split graph the code leaves M1's identity leak open, although 9.35's decision cell counts it as closed.
And the largest group lands in fold 0 under every seed, so every calibration pseudo-draw holds out the same gene block
the real draw will. Four channels stay open after the four changes:

- a held-out drug's other targets, reached through training genes;
- compound-seeded drugs;
- receptor subtypes;
- the reverse of M1.

They are better bounded by type pairs in the 9.35 adversary, ruled before calibration, than split on.

## 2. What the current rule closes and leaves open

The rule is item 25's target split, gated by 9.35's ceiling as ruled on 24 November 2026. It is built as an unreviewed
draft in commit `2a28851` and has never been run on real data. Channel numbers follow the map.

| # | channel | status at `91bc9b8` | where |
|---|---|---|---|
| 1 | a training drug shares a held-out target | closed by construction (seed-node identity) | `target_held_out_split.py` l.76 |
| 2 | the held-out target's own gene perturbation trains | **open on a split graph.** 9.35's decision cell and the module docstring call it closed, but the target rule never matches a gene seed, and `two_sided_held_out_perturbations` does not pass the gene map | split l.19-21, 78-85, 102-103; item 25 l.1874-1881 |
| 2r | the reverse: a lockbox gene whose protein is a training drug's target | open; on no list | split l.104-108 |
| 3 | every held-out drug has a target no training drug has | closed against drugs; weakened by 2 and 9 | `mechanisms_never_trained` l.112-119 |
| 4 | a held-out drug's other targets are held by training drugs | open by design ("the price of keeping the label exact"); bounded by the 9.35 ceiling once that is registered and built | 9.35; `seen_target_share` |
| 5 | a held-out drug's other targets, reached through training genes | open. The shared-seed channel cannot see it, and the (drug, gene) type pair is unruled | `leakage_only_adversary.py` l.40-50 |
| 6 | gene-gene sharing of a node within k=2 | ruled into the adversary (9.36); never run | 9.36 |
| 7 | sharing reached only by longer walks | not scored; disclosed | `registered_channel_list` |
| 8 | disease entries of 20 or more genes | disclosed, open | prereg l.581-587 |
| 9 | compound-seeded drugs, and seeds on different subunits of one complex | open; unmeasured | `configs/drugs_acting_as_graph_compounds.csv` |
| 10 | off-targets | reported, not split on | 1.3(g); 25c |
| 11 | graph content curated over every perturbation | disclosed; no draw reaches it | 38(c) |
| 12 | selection by redrawing | the seed loop is closed (first passing seed); the free parameters are open; in tension with 25(b2) | 9.35; `leakage_ceiling.py` l.24-42 |
| 13 | the calibration reads labels of rows the draw will hold out | open ("a partial guard"); near-total on the gene side, see below | `draw_held_out_set.py` l.112-115 |
| 14 | perturbations used in development enter the new lockbox | open; not on the channel list | prereg l.144-146, 743-760; 9.120 |
| 15 | combinations drawn apart from their parts | conditional: no combinations are in the draw today | split l.106-108 |
| 16 | the same pair through a second source | closed: a perturbation is held out whole | 38(c) |

**The gene side is not a random draw today.** This follows from the code and sits outside the channel list.
`assign_grouped_folds` (`perturbation_wise_and_pathway_wise_splits.py` l.20-48) works like this:

- It sorts groups largest first, so the seed only orders groups of equal size.
- It gives each group to the fold with the fewest members, and `min` picks fold 0 on a tie.
- The gene side is the non-drugs in fold 0 (`two_sided_held_out_perturbations` l.104-108).

So the largest group is in the lockbox under every seed. The 8 October 2026 amendment found this same behaviour for the
validation fold and fixed it there (prereg l.411-417, l.634), but the held-out draw did not inherit the fix.

The 9.35b record is consistent with this (`docs/generated/leakage_only_adversary.json`; 14 October 2026;
`graph_full_neuronal_split_binders_drugs_v4_enzymes`, `evidence_full_v4`, `better_v2_full_v4`):

- 170 held-out genes in all 20 pseudo-draws;
- a gene-stratum macro advantage over degree_popularity of -0.041607339229220996 in all 20.

Whether the 20 gene sets were identical was not checked: the file holds per-draw summaries only. 170 of 1,414 genes is
12.0 percent, not the "one seventh of each side" the registered `held_out_fraction` means, because the fold sizes count
drugs. Two consequences follow:

- Channel 13 is close to total on the gene side, since every calibration pseudo-draw holds out the block the real draw
  will hold out.
- 9.36's gene statistic barely varies across pseudo-draws, so it can hardly be calibrated.

There is also a possible tie to channel 14. On the October table, development fold 0, where the pilots ran, had the
largest group as its test set (prereg l.418-420). If the rebuilt table's largest group is descended from that block,
fold 0 would put into the lockbox the block the pilots were scored on. Checking this is a label-free membership
comparison, and it is owed.

## 3. The methods

The 20 proposals of the four passes were reviewed by two critics, one on statistics and one on the rulings. Several
proposals turned out to be the same method seen from different angles, and are merged below; the pass ids are given in
brackets. Three methods come from the critics rather than from a proposal pass:

- M2, from both critics;
- M4, from the rulings critic;
- M21, from the statistics critic, who noted that no pass had proposed it.

"Label-free" means the method reads no symptom label of a held-out row.

| | method | what it closes | label-free | cost | rulings touched | verdict after critique |
|---|---|---|---|---|---|---|
| **M1** | Coupled draw, forward closure: a held-out target's gene is held out with its disease cluster (G1, L2(i), C1, E1a) | 2; makes 3 hold against training genes too | yes | gene side's composition changes; forced clusters can push it past one seventh; drug and gene rows become dependent | amends item 25's gene side (l.1874-1881) and 38(a); reverses the 9 Oct grouping (l.988-995) | **recommend**, as an amendment |
| **M2** | Gene side as a seeded prefix of whole groups, nearest one seventh of the genes (critics) | 13 on the gene side; lets the seed order of 12 act on genes | yes | a group larger than one seventh needs a stated rule | keeps item 25's text and the meaning of `held_out_fraction`; replaces the fold-0 code | **recommend** |
| **M3** | Nested calibration: each candidate's ceiling fitted inside its own training rows (C3) | 13 | yes (reads that candidate's training labels only) | one calibration per seed examined; pseudo-draws train on five sevenths, which lowers the acceptance rate | delivers 9.35's "no lockbox label is read"; the 1.1 reading is the owner's to confirm | **recommend** |
| **M4** | Seed order, pseudo-draw seeds and every free definition of 9.35 committed before the 9.151 graph is built (critic) | 12, through the order and the definitions | yes | none beyond deciding them | 9.35 "seed order fixed in advance" | **recommend** |
| **M5** | Readings by a label-free exposure fixed at the draw, plus the accepted draw's rank among the pseudo-draws (E3, G5) | none; shows how far a result rests on 4-6, and how much 12 selected | yes | thin strata (25c was about 7 drugs per draw, 14 Oct 2026, history) | extends 25c; follows 38(d) and (g); adds nothing to H1's family | **recommend**, descriptive only |
| M6 | More type pairs in the adversary: (drug, gene), (gene, drug), (drug, drug); a target-family channel (G2, G4, L2(iii), C2, critic) | bounds 5, 9 and receptor subtypes | yes | each gating channel lowers the acceptance rate, which raises the downward shift | 9.35's channel list; 9.36 ruled genes only | consider: each pair ruled, and gating or reported, before calibration |
| M7 | Three parts of the joint ceiling: acceptance rate shown with the go-ahead; one-sided range rule; depth aligned for cross-type pairs only (C2) | fixes the extrapolation defect of `2a28851` | yes | the range rule lowers the acceptance rate | the 9.35 amendment | consider, into the amendment |
| M8 | Mirror closure: a gene whose protein is a training drug's target kept off the gene side, or those drugs purged (C1, L2(ii), E1b) | 2r | yes | bars most druggable genes' clusters from the gene side, or purges an unmeasured number of training drugs | item 25(a)'s unit ("each target individually"); 38(a); 9.120 | the owner's own decision after counts; not adopted by default |
| M9 | Leakage-lookup baseline reported beside H1, outside its family (E2) | the lookup credit of 4, as a comparator | yes | none if reported only | 38(b)'s six baselines, confirmed 23 Nov 2026 | consider, reported only |
| M10 | Label-provenance channels: ATC class, every disease entry, cited papers (L3) | none; measures three routes on no list | yes | none if reported only | 9.35 part 4 | consider, reported only, gating status fixed before calibration |
| M11 | Purge the genes of a held-out drug's seen targets (G2) | a second copy of 4 and 5 | yes | a third class of row; cluster mates keep the labels | item 2's scope; 9.134; 9.150 | no: bound 5 with M6 |
| M12 | Purge the held-out target's single gene from training (E1a as a purge) | 2, in part | yes | its cluster mates keep the same annotations | item 2's scope | no: M1 closes it whole and scores it |
| M13 | Mask training copies of labels from entries of 20 or more genes that a held-out gene shares (L1) | 8 | yes | changes the registered `label_likelihood`; baselines must read the same mask | `label_likelihood`; prereg l.581-587; 9.134 | no, as a draw method: a label decision first (on Fable) |
| M14 | Stratified target order (C4) | none on average; narrows the high tail of 4 | yes | coarser prefix | item 25(a)'s order | not now; only if decided before calibration, by target class |
| M15 | Buffers of two or more hops; wide purge of neighbours (G3, E4) | 5, 6, 7 | yes | empties training: 515 of about 1,290 development perturbations sat one edge from a held-out seed and 606 two (10 Oct 2026, `graph_full_neuronal_split_binders`); 83.7% of genes form one k=2 block (14 Oct 2026, v4_enzymes) | 9.36; item 25 | reject |
| M16 | Cold intermediate nodes: split on each perturbation's k-step reach (G4) | 6, 7, 9 | yes | membership follows reach size, so degree | item 25; 1.3(g); 9.36 | reject; the complex idea goes into M6 as (drug, drug) |
| M17 | Community or minimum-cut split; optimised draw by integer program (G5, C5) | 4-6 and 9, to their minimum | yes | the search at its limit; the held-out set becomes the most isolated mechanisms | 9.35; 25(b2); 9.120 | reject; the attainable minimum may be a reported line, low priority |
| M18 | Inverse-exposure weighting, or regression to zero exposure (E5) | 4-6, in expectation | yes | the effective sample collapses; AUPRC has no per-perturbation part; a new free curve | 38(a)'s estimand | reject |
| M19 | Time split on first-record eras (L4) | none: the graph carries no dates | only if dated over every cell | membership follows research volume (Spearman -0.62, release v0.4, 23 Nov 2026, history) | 38(d): "It is not a time split" | reject |
| M20 | Source split, or leave-symptom-out (L5) | none across perturbations | partly | the test set leans to disagreements between sources; a held-out symptom is degenerate under the noisy-OR head | 38(a), 38(c), 25(b2), 26c | reject |
| M21 | Cross-fitting: score all seven target folds instead of one lockbox (critic) | 12, 13 and the spread from seed to seed | yes | 7 times the runs; every perturbation is scored, including those development used (14 at its maximum) | 1.1's one-shot lockbox; item 25(d); 9.134, 9.150, 38(g) | not recommended; listed so the owner sees it |
| M22 | One joint ceiling plane over every channel, reading and pooling rule (C2 as written) | nothing shown beyond the current AND of ceilings | yes | not identified while the gene side is fixed; lowers the acceptance rate; past one paragraph | 9.35; 9.36 | not as written; its sound parts are M7 |

M22 has one trap of its own. Measuring depth from the protein for every pair would quietly turn 9.36's ruled two-step
gene channel into the three-step one: 98.2 percent of genes in one block, where the owner accepted 83.7 percent ("Oh
well on the genes"). So alignment applies to cross-type pairs only, as M7 says.

### M1. Coupled draw: a held-out target's gene goes with it

**How it works.**

1. Draw the drug side exactly as now.
2. Find each held-out target's gene by identity, not by a walk. The evidence table lists a drug's targets as gene
   nodes, and on a split graph `drug_seeds_on_proteins` replaces each one by its protein nodes
   (`experiment_data.py` l.369-379, from `read_protein_of_gene`, l.356-366). Inverting that map gives the gene of each
   held-out protein target.
3. Every gene perturbation that seeds such a gene node is held out, together with its whole disease cluster.
4. The rest of the gene side is drawn by M2's prefix, with the forced clusters counted first. Suppose the forced
   clusters alone pass one seventh of the genes. Then a rule written in advance applies. This note suggests stopping
   at the forced set and reporting the overshoot, since refusing the seed would reject a draw on a property of the
   split (25(b2)).
5. In the group bootstrap, a held-out drug and the gene clusters held out with it count as one unit. Otherwise the two
   are treated as independent, which understates the standard error, and with it both 9.35's threshold and H1's
   interval. The units are read from membership alone.
6. Every calibration pseudo-draw applies the same rule.

**Why the grouping changes.** On 9 October 2026 the registration kept `disease_cluster_and_targets` for the
confirmatory reading, because joining a drug to its target genes closed this same channel (prereg l.988-995). Under
item 25 that grouping also joins every drug to every drug that shares any target with it. So a group lands on both
sides in nearly every draw, and `read_lockbox` refuses the result (`experiment_data.py` l.279-282). M1 delivers what
that grouping was chosen for, without the joining of drug to drug, and under `disease_cluster` nothing straddles. So the
closure and the change of grouping are one amendment.

**Why it is an amendment and not a fix.** Item 25 registered that the target rule pulls in no gene, and called that
"as it should be" (l.1874-1881). The closure that 9.35 claims is in the session's decision cell, not in the owner's
ruling cell.

**What it closes, in size** (history, from before item 25: 7 October 2026, `evidence_full_v2`, `graph_full_neuronal`,
`docs/generated/drug_target_leakage.md`):

- 69 of 73 drugs that target a labelled gene had that gene in another fold;
- 66 of 418 kept drug positives were also kept positives of that gene;
- P(drug positive | target gene positive) was 0.28, against 0.17 overall.

The same record warns that an agonist and a lifelong loss need not give the same symptoms. So the transfer is a lookup
to remove, not an identity.

**Physiology.** This is the closest version to physiology. The gene encodes the very protein the drug binds, and item
25's split is sign-blind, which this keeps.

**Two follow-ups, each its own ruling.**

- Extending the closure from the held-out targets to every target no training drug has would make 25c's stratum unseen
  through genes as well. But 25c was fixed "before the draw", so the extension needs a ruling of its own.
- Whether GCH1's or HMBS's protein is a drug mechanism target, so that their cluster could be forced to the held-out
  side, is a label-free check owed under 9.120.

### M2. The gene side drawn the way the drug side is

**How it works.** Shuffle the gene side's whole groups with the seed, and keep the prefix whose gene share is nearest
one seventh. This is the rule `held_out_targets` already applies to targets (`target_held_out_split.py` l.42-64).

**What it changes.**

- The seed decides the gene side, as 9.35's seed order, 9.120's "left to chance" and 9.134's "fix the held-out split
  first" all assume.
- Groups stay whole, and the gene side becomes one seventh of the genes, which is what `held_out_fraction` says.
- The group bootstrap gets many gene-side units instead of about one.

It changes the fold-0 code of `two_sided_held_out_perturbations`, not item 25's text, which says only "by the
registered disease-cluster grouping". It is the counterpart for the held-out set of the 8 October 2026 fix to the
validation fold.

**Two edge cases need a stated rule.**

- A group larger than one seventh, if it comes first in the order, overshoots the fraction. On record the largest
  gene group held 12 percent of the genes (item 25 l.1879-1880, 13 Oct 2026, history).
- As written, the prefix rule returns an empty side when the first unit in the order alone holds more than two
  sevenths. The empty prefix is then nearer the fraction, and the loop stops (l.56-64). An empty side gives a statistic
  that is not a finite number, which `draw_passes` refuses, so such a seed fails rather than passes. The same applies
  to the drug side if any one target is held by more than two sevenths of the drugs. That count on the rebuilt table
  is owed.

### M3. Nested calibration

**How it works.**

1. For the first seed in the order, draw its held-out set, reading no label.
2. Make the pseudo-draws among that seed's training rows only, sized so that each pseudo-held-out set has the real
   draw's absolute size.
3. Fit and invert the curve, and check the seed.
4. If the seed fails, treat the next seed the same way.

Under the draft, pseudo-draws run over every perturbation and only an identical seed is refused. Under M3, no
pseudo-draw of the accepted seed's calibration contains a row that seed holds out. It also answers a question the draft
left open: which rows are the development set before a lockbox exists. The answer is the candidate's own training rows.

**What it leaves.** When earlier seeds fail, their calibrations have read labels of rows that a later accepted seed
holds out. That residue is stated, and it is zero when the first seed passes.

**Cost.**

- One calibration per seed examined. The measurement is slow enough that its script already checkpoints each draw, so
  that a run stopped by the background time limit can resume (`--checkpoint-dir`, `measure_leakage_only_adversary.py`
  l.238-242).
- Pseudo-draws train on five sevenths of the rows, against six sevenths for the real draw. Their statistics therefore
  sit lower, and the real draw may fall above the fitted range. M7's range rule would then refuse it, which lowers the
  acceptance rate.
- The size of the pseudo-held-out sets is chosen before calibration. Smaller sets keep training nearer six sevenths, at
  the price of noisier advantages.

**What the owner confirms.** That a rule fixed in advance, whose value is computed for each candidate after its
held-out set is drawn, is the "bound fixed beforehand" of 1.1.

### M4. Fix everything before the draw's graph exists

9.35 rules that the seed order is "fixed in advance", but not in advance of what. Every statistic the draw checks is
label-free, so anyone holding the graph can compute it. An order written after the graph exists could therefore have
been arranged around per-seed statistics. That is the search 9.35 rules out, reached through the order rather than by
redrawing.

**What is committed.** Hashed in the amendment commit, before the 9.151 graph is built:

- the seed order and the pseudo-draw seeds;
- every definition the draft leaves to the caller: the reading and its one standard error, the curve form, the pooling
  rule, the statistics and how they combine, the type pairs and the edge set, the number of pseudo-draws, the gene-side
  grouping, and which rows count as development;
- what a low acceptance rate does: nothing. The rule stands, and the rate is reported.

### M5. Readings by exposure, fixed at the draw

**How it works.** At the draw, each held-out perturbation gets an exposure. This is the adversary's own support through
the registered channels: the shared-node weight of its training neighbours. It is label-free, recorded in the lockbox
file with its cuts, and hashed there.

- **Drugs:** 25c's stratum (no target in training) against the rest.
- **Genes:** zero exposure, then thirds of the positive exposures. At k=2, sharing is nearly everywhere.

**How it is scored**, as 38(d) and (g) are:

- descriptive, and spending no alpha;
- model minus best baseline;
- `minimum_positives_to_score` per stratum;
- the group bootstrap at 95 percent;
- the adversary's own advantage beside the model's.

Exposure goes with how many targets a drug has, its class, degree and research volume. So a gradient shows where a
result sits; it is not a leakage-corrected estimate.

**One added line.** Where the accepted draw's label-free statistics rank among the pseudo-draws'. That shows how much
the seed loop selected, without looking at any later seed. Keep to one gradient per side, so that the readings stay
within what the owner can follow.

### M6 to M10, briefly

**M6, more type pairs in the adversary.** The adversary sees a channel only if its type pair is covered. Each addition
is ruled on its own, and registered as gating or reported before any calibration on the draw's graph:

- **(drug, gene) and (gene, drug).** Depth is counted from the protein, so a gene's walk takes one step more than a
  drug's (9.36: "At k=1 a gene reaches only its own protein"). This pair sees channel 5 and what M1 and M8 leave.
- **(drug, drug) at k=2.** This sees channel 9, for example melatonin against drugs on MTNR1A or MTNR1B, or drugs on
  different subunits of one complex.
- **A target-family channel.** A held-out target that is new as a node can be a paralogue, such as a receptor subtype,
  of a training drug's target. The graph gave away a held-out target's family 0.90 to 0.97 of the time, against a
  chance rate of 0.09 (`docs/generated/leakage_group_rules.md` l.60, citing `docs/family_in_graph.md`; October 2026,
  history). Its family source needs curating, which is research and needs two sources.
- **(gene, gene)** keeps 9.36's two steps from the gene seed.

**M7, three parts of the joint ceiling.** Put three things into the amendment:

- the acceptance rate on pseudo-draws, computed label-free and shown with the go-ahead;
- a range rule that refuses a draw whose statistic lies above every pseudo-draw. This replaces the extrapolation defect
  of `2a28851`. It is one-sided, because a draw below every pseudo-draw is the cleanest;
- depth alignment for M6's cross-type pairs only.

Keep the per-statistic ceilings unless a fit shows that a joint plane is better determined. The plane cannot be
determined while the gene side is fixed, so M2 comes first.

**M8, the mirror closure.** There are two forms, and each has a cost to count on the draw's graph first.

- **Eligibility.** A cluster that holds the gene of a training target cannot be drawn to the gene side. About 97
  percent of targets train (history: about 6 held targets per draw out of 192, 13 Oct 2026), so this bars most
  druggable genes' clusters from the gene side. Closing it fully also needs target units joined through their genes'
  clusters, which changes item 25(a)'s unit from the owner's "each target individually".
- **Purge.** Training drugs that act on a held-out gene's protein are left out of training and scoring. This keeps the
  composition, but it removes an unmeasured number of training drugs. It lowers the drug reading through less training,
  not through a removed leak, and it has the same tension with 9.134 and 9.150 as M11.

Without either form, M6's (gene, drug) pair bounds this channel.

**M9, the lookup as a comparator.** The baseline exists behind `experiments/run_baselines.py --with-leakage-lookup`
(l.442). It would be reported as "model minus lookup", spending no alpha. It does not enter H1's best-of set, for two
reasons. 38(b) names six baselines and the owner confirmed it on 23 November. And a learned model can draw more from
the same leak than a fixed pooling rule can, so beating the lookup does not show that the margin is free of the leak.

**M10, provenance channels.** `leaked_neighbours` takes any map from a perturbation to keys, so three keys fit without
new machinery:

- drug ATC classes, for label text written for a whole class;
- every disease entry, with no 20-gene cut;
- cited papers, which would need a cap.

They are reported only. Text written for a whole class is a label question, not a draw question: the project already
excluded suicidal ideation because "label events are dominated by class-wide boxed warnings rather than mechanism"
(`docs/experiment_design.md` l.91).

### Not recommended, with the reason

- **M11 and M12, purges of genes.** A single-gene purge leaves the gene's cluster mates training, and they carry the
  same entry's annotations (prereg l.584). A purge chosen by held-out membership is a training-time change set by the
  held-out set. That sits in tension with 9.134, which names this order as the one to avoid, and with 9.150's reason,
  that lockbox membership must not shape the model. M1 closes channel 2 whole and scores the cluster; M6 bounds
  channel 5.
- **M13, the large-entry mask.** It changes the registered `label_likelihood` ("Every pair the label selection keeps
  is counted once"), so it needs an `Amends:` trailer. By its own argument, the masked pairs are the held-out genes'
  labels, so the held-out side would decide a training-time change. The more physiological version is to drop
  group-level entries' annotations as labels everywhere, which does not depend on the draw. That is a label-selection
  decision, and research on Fable.
- **M14, the stratified order.** It lowers no channel on average; it only narrows the tail, which raises the
  acceptance rate. "Only if the acceptance rate is low" would choose the procedure on calibration output, which is the
  search again. Decide it before calibration, by target class (a curated source), or not at all.
- **M15 to M17, splits on graph neighbourhoods.** On every recorded graph, a depth of two or more empties training, and
  one step is M1. A split on reach selects by degree. A community split or a minimum cut is 9.35's leakage-minimising
  search at its limit: the seed means nothing, the held-out set becomes the most isolated mechanisms, and 25(b2), 9.35
  and 9.120 all break. The owner's own sentence in 9.36 is the reason in one line: "without it being able to use that
  gap in targets along the path for generalization, i don't see how it will generalize well".
- **M18, weighting.** It moves the estimand to a hypothetical low-leakage population, and it adds a free curve.
- **M19 and M20, time and source splits.** The graph carries no dates, so a time split closes nothing here, and its
  membership would follow research volume. A source split leans towards disagreements between sources. A symptom split
  cannot be scored by the registered head.
- **M21, cross-fitting.** It is the one method that removes the draw's selection entirely, so it is listed. But it
  replaces 1.1's one-shot lockbox: item 25 itself says "only cross-validation removes the choice, and that is a
  different design", and leave-one-target-out was costed and not taken. It scores every perturbation, including those
  whose outputs informed development (channel 14 at its maximum). And 9.134's sampling from training only, 9.150's
  supports and 38(g)'s read sample would each have to be redone fold by fold.
- **M22, the full joint plane.** See the table. Its sound parts are M7.

## 4. The objection of 9.35, answered once

9.35 makes a criticism of its own premise:

- A leakage number reads no label, so checking it does not select on the outcome.
- The hazard is redrawing. Low-leakage draws hold more unseen mechanism, so they are harder, and a search that
  minimises leakage biases the confirmatory reading downward.

So reducing leakage can change the claim. Here is how each kind of method stands against that.

- **Closing a channel by construction, or making the draw random (M1, M2).** No draw is rejected, so nothing is
  selected. The reading falls by what the leak was worth, which is credit taken away, not a harder draw chosen.
  - M1 does change what is held out: a held-out mechanism is now also held out from gene perturbations. Item 25's rule
    already states that claim (the split module's docstring: "this is what puts a mechanism the model never trained on
    into every held-out drug"), so M1 sharpens the claim rather than changing it. Its one shift is in composition: the
    forced clusters are druggable genes' clusters. That shift is disclosed.
  - M2 replaces a fixed block of genes with a random one. It changes which genes are scored, not what is asked.
- **Fixing the procedure (M3, M4).** These change where the ceiling comes from and when the definitions are fixed.
  Neither compares one seed with another. M3 lowers the acceptance rate a little, because its pseudo-draws train on
  five sevenths of the rows, so it adds a little of the shift described next.
- **Bounding by a ceiling** (9.35 as ruled, and M6 for any channel made to gate). Taking the first passing seed is not
  a search, but it is a selection.
  - Illustrative arithmetic, not a measurement: a normal approximation from the constrained-draws pass, recomputed
    here. Suppose a fraction p of draws pass, and the statistic correlates with the reading by rho. The accepted draw's
    reading then moves by about rho times phi(z)/p of the reading's spread, where z is the p-th quantile. That is 0.11
    at p = 0.95, 0.20 at 0.9, 0.42 at 0.75, 0.80 at 0.5 and 1.27 at 0.25, against 1.87 for taking the lowest of 20
    seeds.
  - So each gating condition added lowers p, and moves first-passing towards a search.
  - The estimand becomes conditional: the model's advantage on a held-out set through which the registered channels can
    carry less than one standard error. The shift can make a pass harder; it cannot produce one.
- **Splitting on neighbourhoods, or optimising (M15 to M17).** These are the search at its limit, or a selection by
  degree. The question becomes generalisation to mechanisms that are isolated from training. Weighting (M18) gets to
  the same place by another route: it moves the estimand to a hypothetical population with little leakage.
- **Describing (M5, M9, M10).** These change nothing. They show the gradient, and how much the seed loop selected.

Item 25(b2) still reads: "The draw is not repeated until the condition holds: rejecting draws on a property of the
split would bias which targets end up held out". 9.35 accepted rejection on a label-free leakage statistic. The
amendment has to say so in those words, and keep rejection on anything read from labels, such as symptom support,
refused.

**What the owner would be choosing between.**

- **(a) The registered question, made cleaner.** A random item-25 draw, with:
  - the identity leak closed by construction (M1);
  - the gene side drawn at random (M2);
  - the contamination of the ceiling removed (M3, M4);
  - what item 25 leaves open by design bounded by one ceiling and disclosed;
  - the reading shown by exposure (M5).

  The leakage left is the price item 25 already accepted, now bounded and shown.
- **(b) A lower leakage number, bought with more gates or with neighbourhood splits.** This gives a narrower question
  (mechanisms isolated from training), a less representative held-out set, and a reading biased downward by an amount
  that grows as acceptance falls.

This note recommends (a). The one dial between the two is which of M6's channels gate, and it is set before
calibration. Showing the acceptance rate with the go-ahead (M7) tells the owner where that setting sits between (a)
and (b). It cannot be a reason to change the gates afterwards, because then choosing the gates becomes the search
(channel 12). M4 writes that down in advance.

## 5. What each method would need

**What every method needs.**

- **The amendment item that registers 9.35**, which is owed before the draw. The preregistration does not yet mention
  9.35, 9.36 or a ceiling.
- **A decision row recording the owner's answers.** It takes the next id free on every branch, and it is shown to the
  owner before it is pushed, since it rests on reading them.
- **The fixes the draft already owes:** the two known defects of `2a28851`, and corrections of the stale text listed at
  the end, made in the same commit.
- **Measurements on the draw's graph only.** None can be taken on this disk: release v0.4 is history, and the graph of
  9.151 is not built. Every count in the last column below is label-free, so it can be run on the new graph before any
  calibration.

| method | ruling (the owner) | amendment item | code | measurement on the draw's graph |
|---|---|---|---|---|
| M1 | the closure; `disease_cluster` as the grouping; the overshoot rule; drug and gene as one bootstrap unit. The extension to every never-trained target is ruled separately | yes: item 25's gene side, 38(a), the 9 Oct grouping. `held_out_fraction` keeps its value; `bootstrap_unit` keeps "group", with its units restated | `two_sided_held_out_perturbations` and its docstrings; `draw_held_out_set.py` (grouping, docstring l.44-46); the same rule in `measure_leakage_only_adversary.py`; the bootstrap units in `score_confirmatory.py`; tests | forced clusters per draw, and whether they pass one seventh of the genes; size of the joined units; whether GCH1's or HMBS's protein is a mechanism target |
| M2 | the two edge-case rules | yes, one sentence: the gene side is a seeded prefix of whole groups | `two_sided_held_out_perturbations`; tests | largest group under the chosen grouping; whether it descends from the 8 Oct block the pilots were tested on; drugs on the most-shared target |
| M3 | whether it meets 1.1; the size of the pseudo-held-out sets | yes | `draw_held_out_set.draw_held_out_set` calls the calibration per seed; `measure_leakage_only_adversary` restricted to the candidate's training rows; `calibrate_leakage_ceiling` | the calibration itself, on the draw's graph; the acceptance rate on pseudo-draws |
| M4 | every free definition (listed in M4) | yes, committed and hashed before the 9.151 graph is built | a file holding the seed order and the definitions, checked by the draw script | none |
| M5 | the exposure, its cuts, one gradient per side | yes, as 25c was | the draw records each exposure; `score_confirmatory.py` reports the strata | none before the draw; cuts fixed at it |
| M6 | each type pair, and whether it gates | yes, in the channel list | the reached-node channel with depth per type; family keys | reach statistics; the family source curated on Fable from two sources |
| M7 | the range rule; showing the acceptance rate | yes | `statistic_ceiling`, `ceilings_of_calibrations` (defect 2) | the acceptance rate |
| M8 | which form, if any, after the counts | yes; item 25(a)'s unit if eligibility | the split, or a purge mask in every runner and baseline | training drugs on held-out genes' proteins per draw; clusters holding druggable genes |
| M9 | a reported comparator only | yes, as a reported reading | `score_confirmatory.py` reports it | none |
| M10 | which keys; reported only | yes, in the channel list | key maps for `leaked_neighbours` | none |

The amendment also has to settle two things. It must say whether item 2's added-drug stratum (prereg l.1144-1148,
which is not marked superseded) still applies under the new draw. And it must reconcile the draw with 25(b2), as in
section 4.

## 6. Literature owed

These are the claims a literature pass on Fable must source before any of them enters a decision row, with the
standard method names to search for. Nothing here is cited from memory.

1. **What a cold split closes when one mechanism appears in two kinds of perturbation (M1).** Search for: cold-target,
   cold-drug and cold-pair splits; cold-start evaluation in drug-target and perturbation-response prediction.
2. **Whether a gene's loss of function and a drug acting on its protein share symptoms, and whether the sign matters**
   (agonist against loss of function; lifelong against acute) (M1, M8). Search for: concordance of Mendelian phenotypes
   with drug adverse effects; genetic evidence for drug side effects; phenocopy of a gene loss by pharmacological
   inhibition.
3. **Group randomisation with forced inclusion, and must-link constrained splits (M1, M8).** Search for: constrained
   (must-link) group splitting; grouped cross-validation and leakage.
4. **The cluster bootstrap when dependent rows sit in separate units (M1, M2, and the open SE question).** Search for:
   whether treating dependent rows as independent understates the standard error; how a bootstrap over perturbations
   compares with a cluster bootstrap. The pseudo-draws use the first (`measure_leakage_only_adversary.py` l.198-203)
   and the test registers the second.
5. **Greedy balanced fold assignment and stratified group k-fold (M2).** Search for: group k-fold assignment by
   size; balanced randomisation under group constraints.
6. **Nested calibration (M3).** Search for: nested cross-validation; selection bias from tuning on test rows;
   calibration of an acceptance threshold without test labels.
7. **Rerandomisation with a pre-specified acceptance criterion (9.35, M7, section 4).** Search for: rerandomisation;
   acceptance-rejection sampling; inference after rerandomisation and the conditional estimand.
8. **Selection on a property correlated with difficulty (section 4, M17).** Search for: optimised against random data
   splits; similarity-based and adversarial splits, and their effect on measured generalisation.
9. **Applicability-domain or similarity-stratified evaluation (M5).** Search for: performance against similarity to
   the training set; reporting of thin strata.
10. **A lookup baseline as a leakage control (M9).** Search for: nearest-neighbour or memorisation baselines in link
    prediction and drug-target evaluation; whether adding a baseline to a best-of comparison changes the level of an
    intersection-union test.
11. **Paralogue sharing (M6's family channel).** Search for: phenotype similarity of paralogous genes; receptor subtype
    selectivity and shared adverse effects; functional redundancy in gene families.
12. **Group-level disease entries (M10, M13).** Search for: how HPO and Orphanet annotate a group-of-disorders entry to
    its member genes, and whether shared group annotations inflate held-out scores in gene-phenotype prediction.
13. **Class labelling (M10).** Search for: class labelling of adverse reactions at the FDA, EMA, MHRA and PMDA; whether
    class text concentrates in Boxed Warning and Warnings and Precautions.
14. **For the rejected methods, only if the owner wants them argued from sources:**
    - purging and embargo in cross-validation (M11 to M13);
    - buffered or spatially blocked cross-validation and the choice of buffer width (M15);
    - node-disjoint, scaffold and community-based splits for graph prediction (M16, M17);
    - balanced graph partitioning (M17);
    - covariate-shift importance weighting and effective sample size (M18);
    - temporal validation when the knowledge graph is undated (M19);
    - agreement between SIDER and OnSIDES, and between OMIM and Orphanet (M20);
    - cross-fitting against a single holdout for a confirmatory test (M21).

## 7. Questions for the owner

1. Should a held-out target's own gene be held out with its whole disease cluster (M1)? This amends item 25's gene
   side, which on 13 October registered zero genes pulled in as "as it should be".
2. If yes, should the gene side's grouping become `disease_cluster`? This replaces `disease_cluster_and_targets`,
   which was kept on 9 October for this same leak, and which under item 25 straddles in nearly every draw.
3. If the forced clusters alone pass one seventh of the genes, should the draw stop at the forced set and report the
   overshoot, or refuse the seed?
4. Should a held-out drug and the gene clusters held out with it count as one unit in the group bootstrap?
5. Should the closure extend from the held-out targets to every target no training drug has? That would make 25c's
   stratum unseen through genes too. Yes, no, or later?
6. Should the gene side be drawn as a seeded prefix of whole groups, nearest one seventh of the genes, instead of
   fold 0 (M2)?
7. Is a ceiling rule fixed in advance, with its value fitted for each candidate inside that candidate's training rows
   (M3), the "bound fixed beforehand" that 1.1 means?
8. Should the seed order, the pseudo-draw seeds and every free definition of 9.35 be committed before the 9.151 graph
   is built (M4)?
9. "One standard error of the test's own reading": should this be the registered group bootstrap's standard error,
   and on which reading (macro or micro; whole set or drug stratum)? The pseudo-draws currently bootstrap over
   perturbations.
10. Which cross-type pairs should enter the adversary, and should each one gate or only be reported? The candidates
    are (drug, gene) and (gene, drug), with depth counted from the protein, and (drug, drug) (M6).
11. Should a receptor-subtype (target-family) channel enter the adversary, with a family-unseen line inside 25c (M6)?
12. If the acceptance rate turns out low, should the registered rule stand unchanged, with the rate reported beside
    the result (M4, M7)?
13. The mirror (M8): once its counts on the draw's graph are known, should it be closed by eligibility, by purge, or
    left to the adversary?
14. Should the result be reported by exposure, with one gradient per side, together with the accepted draw's rank
    among the pseudo-draws (M5)?
15. Should the leakage-lookup baseline be reported beside the result, outside H1's family (M9)?
16. Should disease entries of 20 or more genes (channel 8) be taken up as a label-selection question on Fable,
    rather than as a mask applied per draw (M13)?
17. Should cross-fitting over seven target folds (M21) be ruled out, keeping the one-shot lockbox?
18. Does item 2's added-drug stratum still apply under the new draw?

## Notes

**Stale text found.** These were found while writing and are reported, not fixed, since this pass was read only. A
commit that adopts M1 or M2 corrects them in the same commit.

- The docstring of `target_held_out_split.py` (l.19-21) and that of `held_out_perturbations`, `leakage_only_adversary.py`
  l.40-44, and 9.35's decision cell all say the gene perturbation of a held-out target is held out with it. On a split
  graph, `two_sided_held_out_perturbations` does not do this.
- `experiments/draw_held_out_set.py` l.44-46 says the gene-side grouping is left open "because no ruling settles it".
  Against that, the 9 October 2026 registration (prereg l.994) keeps `disease_cluster_and_targets` for the
  confirmatory reading.

**The model.** This note was not written on Fable. The recorded numbers it reads towards a choice need a Fable recheck
before they enter a decision row: the 9.35b record, the October leakage records and item 25's counts. So does every
item of section 6.

**What was and was not done.**

- No text addressed to an AI assistant was found in the files read.
- The pass edited nothing in the repository. This copy was committed afterwards on 28 November 2026; only its opening
  paragraph, the two lines that name the model and this list were changed.
- No measurement was taken. The one computation was the illustrative arithmetic of section 4, which uses no data.

**Files.** The map, the four proposal passes (graph structure, labels and sources, estimation, constrained draws), the
two critiques (statistics, rulings) and their progress logs were written to the session's scratchpad on 28 November
2026 and are not in the repository.
