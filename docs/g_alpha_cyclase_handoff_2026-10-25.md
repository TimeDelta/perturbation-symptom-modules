# Handoff: correct the Gi/o-to-cyclase edges, then return to 9.80 (written 25 October 2026)

Written 25 October 2026 as the Project note `claude/handoff_g_alpha_cyclase_2026-10-25.md`, against `main` at
`f54e3e9`. **Moved into the repository on 27 October 2026** under the owner's ruling that the repository is the single
source of truth ("Everything should rely on the repository moving forward"); the Project note was deleted once this page
held its content. The text below is the note as written, including the status block it carried on 27 October, with
this header added. It is a record: a later correction is a dated addition.

**The cyclase table of section 1 is not a finding.** It was read on Opus on 24 October 2026, before the `CLAUDE.md`
"Models" rule, and no Fable pass has verified it; under that rule it is flagged here and must be rechecked on Fable
before anything is built from it. What this page adds to the repository, which held the rest in decisions 9.97, 9.86,
9.80 and 9.99: the per-isoform table for ADCY3, ADCY4, ADCY7, ADCY8 and ADCY9, the Baldwin et al. 2019 quote on AC9,
the native-against-reconstituted requirement, the second of the two owner questions of section 2, ADCY5's in-degree of
20, and the build plan of section 4.

> **Status on 27 October 2026 (this record is otherwise left as written).** `main` is at 68bde1f; 9.97 is still
> "handed off" and no step below has started.
> - **Section 1, last line: the HRH2 recheck is done.** A Fable session rechecked 9.79 on 26 October 2026 and recorded
>   it as decision 9.99. HRH2's four Gq/11 rows now cite Kühn et al. 1996 alone, because Mitsuhashi et al. 1989
>   excludes Gq/11. Whether HRH2's primary transducer becomes Gs is still the owner's call under 9.79. 9.99 also found
>   83 more receptors whose coupling-table citations are owed a per-row pass on Fable. That is not this task, but it
>   touches the same table, `configs/admitted_receptor_g_alpha_coupling.csv`, and its expansion script.
> - **Section 5: 9.87 is decided.** `scripts/rebuild_data_layer.sh` now builds the neuronal variant with
>   `--membrane-potential computed_from_the_pools` (commits 992913a and baec731). The third command of the chain below
>   needs that flag; take the chain from the script, not from this note.
> - Section 1's cyclase table is still unverified: no Fable pass has read it yet.

The owner's ruling this note carries out (decision 9.97, 25 October 2026): "Order accepted but give me a handoff for
another session to do the work". The order accepted:

1. Correct the Gi/o to adenylyl cyclase edges and check the G beta gamma to cyclase edges.
2. Rebuild v5 and rerun the cAMP sign sweep of 9.86.
3. Then decide 9.80 (whether secondary coupling may outweigh primary coupling).

## 0. Rules that bite on this task

- **Research on Fable** (`CLAUDE.md` "Models"). Steps 1 and 2 below are research: reading sources, turning them into a
  table or a decision entry, and interpreting the sweep for 9.80. On another model, hand each to a subagent with the
  Agent tool's `model` set to `fable`, or leave it undone and say so. Steps 3 to 5 are engineering and may run on any
  model.
- **Push straight to `main`** after the full suite passes (`set -o pipefail; PYTHONPATH=. python -m pytest -q -p
  no:cacheprovider`). No pull requests. Never force-push.
- **Decision ids**: take the next free id with the command in `CLAUDE.md` "Documents" just before committing, and again
  after any `git pull --rebase`. The decision log and the regenerated pages go in **two commits**.
- Quote the owner verbatim with the date for every ruling. They/them pronouns.
- Every number carries the graph, the commit and the command.

## 1. Recheck the cyclase evidence on Fable (research)

The 24 October session read these on Opus, before the Models rule. **Nothing below is a finding yet.**

What it reported, to be confirmed or corrected:

| Isoform | Gi alpha (GNAI1-3) | Go alpha (GNAO1) | Gz alpha (GNAZ) | G beta gamma |
| --- | --- | --- | --- | --- |
| ADCY1 | inhibits | inhibits | inhibits | inhibits |
| ADCY2, ADCY4, ADCY7 | insensitive | not reported | not reported | raises Gs-stimulated activity 5 to 10 fold; no effect alone |
| ADCY3, ADCY8 | insensitive | not reported | not reported | inhibits |
| ADCY5, ADCY6 | inhibits | not reported | inhibits | raises Gs-stimulated activity about 2 fold |
| ADCY9 | not inhibited | not inhibited | not reported | no direct effect |

Sources it named:
- Taussig et al. 1994, J Biol Chem 269:6093, PMID 8119955: types I, II, V and VI only, in Sf9 membranes. Abstract quote
  checked: "Type II adenylyl cyclase appears to be immune to inhibition by these proteins."
- Sadana and Dessauer 2009, Neurosignals 17:5, PMID 18948702, doi:10.1159/000166277, Table 1. Its full text was read
  by a subagent and **not** by the session itself; the PubMed tool returned an empty full text.
- Baldwin et al. 2019, Mol Pharmacol 95:349, PMID 30696718, doi:10.1124/mol.118.114595. Abstract quote checked:
  "although AC9 is not directly inhibited by Gi/o, it can heterodimerize with Gi/o-regulated isoforms, AC5 and AC6."
- Sunahara et al. 1996, Annu Rev Pharmacol Toxicol 36:461, PMID 8725398: "some are inhibited by the alpha subunits
  of the three Gi proteins", without naming which.
- **Not read**: the IUPHAR review, Dessauer et al. 2017, Pharmacol Rev 69:93, PMID 28255005,
  doi:10.1124/pr.116.013078. PMC answered with a browser check and the publisher blocks XML full text. It is the best
  single source; ask the owner to open it if no other route works.

What the Fable pass produces:
- the table above, each cell with a quote, its source and whether the evidence is native or reconstituted/transfected
  (Sadana and Dessauer: the assignments come "in large part from expression of full-length AC isoforms in mammalian
  or insect cells"; native support named only for AC5);
- a second reputable source per cell where the first is thin (`CLAUDE.md` "Reading sources").

**Also flagged for the same recheck**: decision 9.79 (HRH2's primary transducer), read on Opus on 21 October 2026.

## 2. Two questions for the owner before any edge changes

1. **Is insensitivity shown only in reconstituted or transfected systems enough to remove an edge?** 9.20 ruled on
   admitting a coupling, not on removing one, and most of the table above is heterologous.
2. **How should "raises Gs-stimulated activity, no effect alone" be represented?** It is a conjunction (G beta gamma
   AND Gs alpha). The linear-response encoder has no conjunction; the message-passing encoder has
   `conjunction_aggregation = "minimum"` for conjunction relations. Options: leave the G beta gamma edges out of the
   cyclases, keep them as plain positive edges, or a conjunction relation.

Record both rulings in `docs/open_decisions.md` (under 9.97 or a new id) before building.

## 3. Find every edge into the cyclases (engineering)

Measured on the 21 October v5 rebuild (from #11's code, commit 2da7493; **not** current main):
- each of ADCY1 to ADCY9 gets seven `g_alpha_regulates_effector` edges: +1 from GNAS and GNAL, -1 from GNAI1, GNAI2,
  GNAI3, GNAO1 and GNAZ, so 45 inhibitory in all;
- PROTEIN:GNG2 enters PROTEIN:ADCY5 as `inhibits`. The other GNB*/GNG* edges into cyclases were not listed;
- ADCY5 had an in-degree of 20 in all.

On the graph you build in step 5, list **every** edge into the nine cyclase protein nodes by relation, sign and
source, including Reactome entities (`RCTE_*`, members by `member_of`) and Reactome regulators of cyclase reactions,
not only the OmniPath protein edges.

## 4. Build the correction (engineering, after step 2's rulings)

- A curated table in `configs/`, one row per (cyclase gene, G protein gene, effect, PMID), filled from step 1's
  verified cells and nothing else.
- Apply it where the effector edges are typed: `typed_coupling_relation` and `build_signaling_layer` in
  `mechanistic_pathway_learning/graph/build_physiology_graph.py` (`ADENYLYL_CYCLASE_SYMBOLS`,
  `G_ALPHA_REGULATES_EFFECTOR_RELATION`). Count what is dropped in the build summary, as the 9.23 filter does
  (`receptor_g_alpha_edges_dropped_as_unlisted`).
- A flag that restores the old edges, for the ablation, as `--no-typed-coupling-relations` does for 9.86.
- Tests next to `tests/test_receptor_g_alpha_coupling_filter.py`.

## 5. Rebuild v5 and rerun the sweep (engineering; interpreting it is research)

**Rebuild traps** (from the 24 October v5 handoff):
- `scripts/rebuild_data_layer.sh` skips every step whose output exists. Build into a fresh `data/processed`, or move
  the old outputs aside as a **baseline**, and record the sha256 of the baseline's `edges.parquet`.
- Current main needs inputs that cannot be refetched: **GEO GSE100472** (the pineal class), the **Siletti cluster
  aggregate** and the **BRENDA JSON** (licence tick). Ask the owner if any is missing; do not substitute.

The chain the 21 October session ran, from the repository root with `PYTHONPATH=.`:

```
python -m mechanistic_pathway_learning.graph.build_physiology_graph --output-dir data/processed/graph_full
python experiments/build_manganese_graph_variant.py --graph-dirs data/processed/graph_full
python experiments/build_neuronal_graph_variant.py --base-graph-dir data/processed/graph_full_manganese --output-dir data/processed/graph_full_neuronal
python experiments/build_gene_protein_split.py --graph-dir data/processed/graph_full_neuronal --output-dir data/processed/graph_full_neuronal_split
python experiments/build_plasma_binder_variant.py --graph-dirs data/processed/graph_full_neuronal data/processed/graph_full_neuronal_split --markdown-output none
python experiments/build_drug_entry_node_variant.py --graph-dir data/processed/graph_full_neuronal_split_binders --evidence-dir data/processed/evidence_full_v5 --carrier-table configs/drug_plasma_carriers_v4.csv --neomorphic-alleles configs/neomorphic_alleles.csv --output-dir data/processed/graph_full_neuronal_split_binders_drugs_v5
```

Check these against the current `scripts/rebuild_data_layer.sh` before running them; later merges may have added
steps or flags (see the status block above on 9.87).

Then run, before and after the correction:

```
python experiments/measure_g_alpha_family_balance.py --graph-dir <graph> --evidence-dir data/processed/evidence_full_v5 --output <json>
python experiments/sweep_coupling_gain_ratio.py --graph-dir <graph> --evidence-dir data/processed/evidence_full_v5 --vary inhibits activates couples_secondary couples_primary g_alpha_regulates_effector --output <json>
```

**Sweep trap**: `binds` is unsigned and takes `0.9 tanh(logit)`, so a negative base logit gives it a strong negative
gain and reverses signs across the graph. The script holds unsigned relations at 0; keep it that way.

Numbers to compare against (21 October rebuild, base gain 0.1, every other signed gain equal, `binds` 0;
`docs/coupling_gain_ratio_sweep_v5_after_9_77_base_0.1.json`):

| Gain varied | Cyclase sign goes wrong at |
| --- | --- |
| `inhibits` | never, 0.25x to 8x |
| `g_alpha_regulates_effector` | never |
| `couples_secondary` over `couples_primary` | ADRB2 1.5-2x, ADORA1 3-4x, PTGER4 4-6x |
| `activates` | ADORA1 2-3x, by a route not yet traced |

Also report: the count of receptors coupled to both Gs and Gi/o (9 on 21 October) and each receptor's sign at
equal gains.

## 6. Then 9.80 (owner's call; do not build without a ruling)

Bring back whether the `couples_secondary`/`couples_primary` ratio still flips any receptor once the cyclase edges
are right. The options as they stand, with C the propagation channels:

| Option | Extra parameters |
| --- | --- |
| (a) cap the secondary gain at the primary gain (`couples_primary` gain x sigmoid(theta)) | 0 |
| per-edge strengths on `couples_secondary` only | 88, or 88 C (41 receptors) |
| per receptor-family pair, secondary only | 44, or 44 C |
| per-edge strengths on both coupling types | 668, or 668 C |

The owner's question of 24 October set the scope: "I don't need full per edge coupling strengths though, just on
certain relation types, right?" The answer was yes; nothing proposes strengths on all 268,850 edges.

## 7. Loose ends, not this task

- ADORA1's `activates` sensitivity (2-3x) is untraced; record it if the trace is cheap, don't chase it.
- 9.79: HRH2 to primary Gs is still the owner's call, after its Fable recheck.
- The message-passing encoder's registered factorised relations (amendment item 8) name `activates`, not the coupling
  types, so under that encoder the coupling edges get a diagonal transform only (9.86).

## Done when

- [ ] Step 1's table is verified on Fable and in the decision log with quotes
- [ ] Step 2's two rulings are recorded with the owner's words
- [ ] The correction is on `main` with tests and an ablation flag
- [ ] Before/after counts and the sweep are recorded, with graph, commit and command
- [ ] 9.80 is put to the owner with the new thresholds
