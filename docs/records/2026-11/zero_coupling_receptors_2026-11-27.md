# Annotated receptors the coupling filter leaves with no signed G-alpha edge, on the filter's inputs (27 November 2026)

Decision 9.22's zero-coupling count, which its status in `docs/open_decisions.md` records as "owed before anything was
dropped and was not taken", measured on 27 November 2026 by `experiments/measure_zero_coupling_receptors.py` at commit
`c1f810e`. It is an engineering measurement: it gives counts and names and says nothing about what they mean for 9.22
or any other decision. The full result, every receptor named, is `zero_coupling_receptors_2026-11-27.json` beside this
file.

**Taken on the inputs before graph assembly, not on a graph.** No graph was assembled. The counts are of the
signalling layer that `build_signaling_layer` (`mechanistic_pathway_learning/graph/build_physiology_graph.py`) makes
from the inputs of section 1, without and with decision 9.23's filter. No later step of `build_physiology_graph` was
applied, so these are not figures of any build (CLAUDE.md, "A measurement carries the graph it was taken on"). **The
count is to be retaken** on the graph of the v5 rebuild, and again after decision 9.99's pass, which may change the
admitted table (9.99 is open, and its row says "nothing in the table changes before its pass"). This record does not
say which build is v5.

## 1. Inputs

| input | path read | SHA-256 | bytes | date |
|---|---|---|---|---|
| OmniPath interactions | `data/raw/omnipath/omnipath_interactions.tsv` of the main checkout (a download, not tracked) | `ce72177f5d9d9675e7e0c22cd61ffb742f4bc9466789f4c3a92707e5ab4cd54a` | 19,206,989 | modified 2026-11-23 15:40:50 UTC, by the raw fetch of 23 November 2026 that the addition of 27 November 2026 to `docs/data_layer_rebuild.md` records |
| admitted coupling table (9.23) | `configs/admitted_receptor_g_alpha_coupling.csv` | `ea98bf6c6536c15e53e63b38ec2ad4029ea99774ee9e467c6d1fc09377af511d` | 112,705 | last changed in commit `4b5cf67` (2026-11-04); 1,972 admitted pairs over 253 receptors |
| curated sign overrides (9.10(a)) | `configs/curated_edge_sign_overrides.csv` | `555c900b262070f9daa2252e69e9759e586ecb23618385ff287c7481e0a7035e` | 16,690 | last changed in commit `b387b33` (2026-10-14); 33 rows, all 33 applied, none with a G alpha as its target |
| build module (the functions run) | `mechanistic_pathway_learning/graph/build_physiology_graph.py` | `8e144f75afa8cc0ec6723c1be2fed9a7fdd50f29638a1443375aad2cf82845e5` | 60,815 | last changed in commit `f46fccc` (2026-11-21) |
| measurement script | `experiments/measure_zero_coupling_receptors.py` | `9e4faff688cc8e978801a0a8117a55a0f73b58fef10076de36d4a78492655eb5` | 20,107 | commit `c1f810e` (2026-11-27) |

The modification time of a tracked file is when the worktree's checkout wrote it (27 November 2026), so for those
files the last commit dates the content. The JSON gives both, and records that none of the four tracked files as
read differed from its last commit.

## 2. What was counted

The script runs `build_signaling_layer` twice over the same OmniPath file and the same overrides. The first run has no
admitted pairs, which gives the layer before the filter. The second has `load_admitted_receptor_g_alpha_coupling`'s
pairs, with the transducer roles and the coupling edge types of decision 9.86 on, which is how `build_physiology_graph`
calls it and gives the layer after the filter. So the sign the filter reads is the build's own: after `expand_complex`
has expanded the complexes, `interaction_sign` has signed the row and the override has corrected it.

- **Annotated receptors**: the 253 symbols in the table's `receptor_gene_symbol` column.
- **G alpha**: the 16 genes of `G_ALPHA_GENE_SYMBOLS` (GNA11, GNA12, GNA13, GNA14, GNA15, GNAI1, GNAI2, GNAI3, GNAL,
  GNAO1, GNAQ, GNAS, GNAT1, GNAT2, GNAT3, GNAZ).
- **An edge into a G alpha** is a stored edge with the receptor as source and a G alpha as target. A binds edge is
  stored in both directions, so a binds row written either way round counts.
- **Signed** means a sign other than 0, which is how `receptor_g_alpha_edge_is_dropped` reads it. An unsigned edge is a
  binds edge, and the filter passes it.

## 3. Counts

| group | receptors |
|---|---|
| at least one signed edge into a G alpha before the filter, none after it | **10** |
| of which left with no edge into a G alpha at all | 8 |
| of which left with binds edges into a G alpha only | 2 |
| no signed edge into a G alpha before the filter (the filter cannot change these) | 59 |
| of which binds edges into a G alpha only | 2 |
| of which no edge into a G alpha, and a participant of some OmniPath row | 33 |
| of which no edge into a G alpha, and in no OmniPath row | 24 |
| at least one signed edge into a G alpha after the filter | 184 |
| of which every kept signed edge negatively signed | 0 |
| total | 253 |

Signed receptor-to-G-alpha edges, counted as distinct receptor, G alpha and sign: 976 before the filter, 666 after,
310 dropped. The build's own counter `receptor_g_alpha_edges_dropped_as_unlisted` reads 433 for the second run,
because it counts once for each expanded receptor and G-alpha pair of every OmniPath row, before duplicates are
dropped. In the same run, `edges_typed_couples_primary` reads 707, `edges_typed_couples_secondary` 110 and
`receptor_g_alpha_edges_left_inhibits` 0.

The counts were checked once against a separate count in a scratch script that does not call the build's functions
(and leaves out the overrides, since none has a G alpha as its target). It gave the same 10, 2, 59, 2, 24, 184, 976
and 666. The scratch script is not kept.

## 4. The 10 receptors with a signed G-alpha edge before the filter and none after it

"Signed edges before" are the receptor's signed edges into a G alpha before the filter, by gene, with the gene's family
and the sign. "Admitted families" are the receptor's families in the admitted table. "Binds left" are the G alphas it
still has a binds edge into after the filter.

| receptor | signed edges before | admitted families | binds left |
|---|---|---|---|
| `FZD10` | GNAO1 (Gi/o) +1, GNAQ (Gq/11) +1 | G12/13 | none |
| `FZD4` | GNAO1 (Gi/o) +1, GNAQ (Gq/11) +1 | G12/13 | none |
| `GPR65` | GNAI1 (Gi/o) +1 | Gs | none |
| `GRM3` | GNAS (Gs) +1 | Gi/o | none |
| `GRM6` | GNAS (Gs) +1 | Gi/o | none |
| `GRM8` | GNAS (Gs) +1 | Gi/o | none |
| `HTR5A` | GNAL (Gs) +1, GNAS (Gs) +1 | Gi/o, Gq/11 | none |
| `PROKR1` | GNAI1 (Gi/o) +1, GNAI2 (Gi/o) +1, GNAI3 (Gi/o) +1 | Gq/11, Gs | none |
| `AGTR2` | GNAQ (Gq/11) +1 | Gi/o | GNAI2, GNAI3 |
| `GRM4` | GNAS (Gs) +1 | Gi/o | GNA15 |

## 5. The 59 receptors with no signed G-alpha edge before the filter

- **Binds edges into a G alpha only (2):** C5AR1, VIPR1.
- **No edge into a G alpha, and a participant of some OmniPath row (33):** ADGRD1, ADGRE2, ADGRL1, BRS3, CALCR, CMKLR1,
  FPR3, GLP2R, GPBAR1, GPR20, GPR26, GPR37, GPR37L1, GPR39, GPR75, GPRC6A, MAS1, MRGPRX3, MRGPRX4, NPBWR2, NPSR1, NPY2R,
  NPY4R, NPY5R, NTSR2, OXER1, PTGDR2, QRFPR, RXFP1, RXFP2, RXFP3, RXFP4, VIPR2.
- **In no OmniPath row (24), compared by symbol:** ADGRG2, ADGRG3, CD97, GPR101, GPR12, GPR139, GPR18, GPR22, GPR27, GPR3,
  GPR31, GPR33, GPR4, GPR6, GPR68, GPR78, HCAR1, HCAR2, HCAR3, MRGPRD, OPN4, OPN5, SUCNR1, TAAR1. The comparison is of
  the table's symbol against OmniPath's gene symbols. Whether OmniPath holds any of these under another symbol was not
  checked.

The 184 receptors that keep a signed edge are named in the JSON.

## 6. Not taken here

- The figure on a built graph, which is to be taken on the v5 rebuild, and the retake after 9.99's pass (above).
- Any reading of these counts for decision 9.22, or for any other decision. Interpreting a measurement for a decision is
  research (CLAUDE.md, "Models"), and the 9.22 row is not edited.
