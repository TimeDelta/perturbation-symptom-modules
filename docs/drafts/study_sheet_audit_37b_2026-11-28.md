# Study-sheet corrections owed when item 37b's cell classes land (draft, 28 November 2026)

**What this is.** A draft for the owner to approve, written on 28 November 2026. **Nothing in the study sheet was
changed**, nothing in `configs/study_sheet_diagrams.json` was changed or stamped, and no outside source was read. It
was written from the repository at `main` = `c24727c` and from the branch `wave4/cell-classes-37b` (commits `f87ab5a`
and `c739bcb`, forked from `91bc9b8`), which builds amendment item 37b's cell classes in code and has not landed. The
study sheet (https://claude.ai/artifact/RzVm4LjdeHmzzdSyzJ5j65) was read with the docs tools on 28 November 2026:
diagram `c642a74c-b09e` at publication 4, `098c9a09-8f0f` at publication 2, `236f9823-56fb` at publication 9, and
passage `mtp7zsmsxgy.36327` at revision 121 of the body (`d9e8351f-e3f9`, document revision 198). Every "current
text" below is quoted from those reads. Line numbers marked "branch" are of the branch's tip `c739bcb`; those marked
"main" are of `c24727c`. A rebase when the branch lands can move them.

Sections 1 to 4 are corrections the branch makes necessary. Sections 5 and 6 are two gaps that predate the branch.
Section 7 is the registry's declarations. Section 8 lists what is the owner's to decide.

## 1. Why the three entries go wrong when the branch lands

In this repository "built" means what the code does by default, not what the last weight table on disk holds. Commit
`7844a0b` (22 November 2026) corrected diagram `012dc8f5-8ee9` because "The exclusion was built on 20 November 2026
(27fbeb42)", and `27fbeb4` changes code and tests only. Commit `4fbe651` (22 November 2026) left five diagrams' built
state alone because "The rule is off by default, so what each shows as built is unchanged". The branch's implementer
judged the three entries still right, reading "built" as the weight tables last built; its checker read the
precedent above and found all three wrong once the branch lands. This draft follows the precedent.

What the branch's code builds by default, with every source it reads on disk (`experiments/build_cell_class_weights.py`,
branch lines 51-53 join the classes and lines 66-75 name the default paths; line 104 adds `all_cells`):

| Lanes | Classes | Defined at (branch) |
| --- | --- | --- |
| 1 | `all_cells` | `experiments/build_cell_class_weights.py` line 104 |
| 10 | the HPA single-nucleus brain classes | unchanged (`graph/brain_expression_descriptors.py`, `hpa_cell_class_table`, main line 106) |
| 1 | dopaminergic (atlas cluster 395) | unchanged (`add_dopaminergic_class`, main line 144) |
| 5 | atlas clusters: noradrenergic (398, decision 9.76) and item 37b's serotonergic (397), Purkinje (314), medial habenula (334), histaminergic (432) | `graph/siletti_cluster_classes.py` lines 79-81 |
| 3 | item 37b's cholinergic classes from subclusters of cluster 400: striatal (1634-1636), NGFR-negative basal forebrain (1637, 1638), NGFR-positive basal forebrain (1640-1642) | `graph/siletti_cluster_classes.py` lines 84-87 |
| 3 | thyroid and pancreatic islet (GTEx), pineal (GEO GSE100472) | `graph/peripheral_cell_classes.py` line 86 (the GTEx pituitary is gone) |
| 6 | item 37b's pituitary lineages from HPA's single-cell-type table | `graph/peripheral_cell_classes.py` lines 91-96 |

That is **29 lanes, 28 expression classes and `all_cells`**, the count diagram `098c9a09-8f0f` already gives for the
list in 37b. An absent source adds no class, so the count a build gives depends on the disk. Read on this
container's disk on 28 November 2026:

- The six pituitary lanes need HPA's `rna_single_cell_type.tsv.zip` at `data/raw/hpa/rna_single_cell_type/`
  (`graph/peripheral_cell_classes.py` branch line 102). No script fetches it and it is not on this disk; an absent
  table adds no pituitary class at all (branch line 217). So a build without it has 23 lanes and no pituitary lane,
  until a release of the table is chosen and pinned.
- The three cholinergic lanes need the atlas's CELLxGENE Splatter file
  (`graph/siletti_cluster_classes.py` branch line 78), which `scripts/fetch_raw_sources.sh` fetches only with
  `--with-cellxgene`. It is on this disk; a build without it has three lanes fewer.
- The pineal lane needs GEO GSE100472's counts, which the owner supplied, at `data/raw/geo/GSE100472`
  (`graph/peripheral_cell_classes.py` branch line 99; an absent directory adds no pineal class, branch line 208).
  They are not on this disk either (`data/raw/geo/` holds only GSE217837), which was so before the branch too.
- The ten HPA lanes need HPA's single-nucleus cluster-type table in a release whose cluster types
  `CELL_CLASS_OF_CLUSTER_TYPE` maps (`graph/brain_expression_descriptors.py` main lines 53-72: the 34 types of the
  release read until 23 November 2026, pooled into the ten classes). The table on this disk is the release decision
  9.155 took on 27 November 2026 (SHA-256 `b24e46d4`, 48 cluster types), none of which that mapping names, so
  `hpa_cell_class_table` (main lines 106-110) raises "cluster types with no cell class" (run on this disk's table on
  28 November 2026 by the checker of this draft) and `experiments/build_cell_class_weights.py` stops there (branch
  line 49), before any class is built. Decision 9.155 lists the mapping as owed before a rebuild. This holds at
  `c24727c` too, for the 17 lanes the built diagram draws today.

So no build on this disk today gives any lanes at all. Once the 48 types are mapped, a build here without the
pituitary table and the pineal counts would have **22 lanes** (29 less the six pituitary lanes and the pineal), if
the mapping keeps the ten HPA classes, which is decision 9.155's to settle.

The proposals below draw the 29 the code defines and say where it depends on a source; section 8 asks the owner
whether the built diagram should draw 29 or what a build on a given disk gives.

Unchanged by the branch, and used below: the shared extracellular pool averages every class except `all_cells`
(`experiments/run_main_model.py` main line 410); the channel count is classes times `--channels-per-cell-class`
(`mechanistic_pathway_learning/models/linear_response_encoder.py` main line 913; the default 1 is
`experiments/run_main_model.py` main line 1964); the expansion width is `--node-state-dim`, default 32
(`experiments/run_main_model.py` main line 2032).

## 2. Diagram `c642a74c-b09e`, "Propagation channels: one lane per cell class" (state: built)

| Text element | Current text (quoted) | Proposed text once the branch lands | Code that makes the change |
| --- | --- | --- | --- |
| `subtitle` | "As built, with --cell-class-weights, 1 channel per class (the default), so C = Q = 17; item 37 changes it, next diagram" | "As built, with --cell-class-weights, 1 channel per class (the default), so C = Q = 29 with every source on disk; the rest of item 37 changes it, next diagram" | the table in section 1; item 37b's classes are now built, the rest of item 37 (37f, 37l, 37n) is not |
| `lane4-name` | "+ 14 more lanes" | "+ 26 more lanes" | 29 lanes less the three drawn (`all_cells`, dopaminergic, astrocyte) |
| `lane4-a` | "9 more HPA classes" | unchanged | |
| `lane4-b` | "4 endocrine glands" | "8 atlas classes" | `graph/siletti_cluster_classes.py` branch lines 79-81 and 84-87 (five cluster classes and three cholinergic classes) |
| `lane4-c` | "noradrenergic (LC)" | "9 endocrine classes" | `graph/peripheral_cell_classes.py` branch lines 86 and 91-96 (thyroid, islet, pineal and six pituitary lineages) |
| new `note-c`, below `note-b` | (none) | "Atlas: noradrenergic (brainstem, cluster 398); from 37b serotonergic, Purkinje, medial habenula, histaminergic," | the same lines; the noradrenergic label is section 6 |
| new `note-d` | (none) | "3 forebrain cholinergic. Endocrine: thyroid, islet, pineal, and 6 pituitary lineages from HPA (37b; needs its table)." | `graph/peripheral_cell_classes.py` branch lines 102 and 217 |
| `pool-a` | "extracellular metabolites take the mean over the 16 expression classes," | "extracellular metabolites take the mean over the 28 expression classes," | `experiments/run_main_model.py` main line 410, every class but `all_cells`, now 28 |
| `exp-a` | "field = (h · W) ⊙ node gate: the 17 class channels become 32 state channels for the head" | "field = (h · W) ⊙ node gate: the 29 class channels become 32 state channels for the head" | `linear_response_encoder.py` main line 913 and `run_main_model.py` main line 2032 |

Layout: the box `lane-others` holds three lines of about 21 characters at 11.5 px, so the class names move to two
note lines; the `svg` viewBox grows from 662 to about 698 for them. The title, the input box, the loop container, the
three named lanes, `not-pooled`, `after-loop`, `exp-b`, `note-a` and `note-b` stay true and are not changed.

## 3. Diagram `098c9a09-8f0f`, "Propagation channels, as decided (items 37b, 37f, 37l, 37n)" (state: decided)

The 29 and its makeup match the branch's code exactly. What goes wrong is each statement that the classes are not
built. The region rule and the annotation-order repair of 37b (`cw-a`, `cw-b`), 37l (`cw-c`), 37n (`regions`) and
37f (`bottleneck-inside`) are not built by the branch, so those elements stay as they are.

| Text element | Current text (quoted) | Proposed text once the branch lands | Code that makes the change |
| --- | --- | --- | --- |
| `subtitle` | "Amendment items 37b, 37f, 37l and 37n, registered 23 Nov 2026; nothing here is built" | "Amendment items 37b, 37f, 37l and 37n, registered 23 Nov 2026; only 37b's cell classes are built (<date the branch lands>)" | section 1 |
| `loop-label` | "Inside the loop: one lane per class, 29 by the list in 37b where 17 are built" | "Inside the loop: one lane per class, 29 by the list in 37b, all built as the previous diagram shows" | section 1 |
| `loop-count` | "29 = 17 built + 4 new + 3 cholinergic + 5 more pituitary, counted from the list in 37b" | "29 = 17 before 37b + 4 new + 3 cholinergic + 5 more pituitary, counted from the list in 37b" | section 1 |
| `lb-name` | "The 17 built lanes" | "The 17 lanes before 37b" | |
| `ls-c` | "HPA lineage, where 1 is built" | "HPA lineage, replacing GTEx's one" | `graph/peripheral_cell_classes.py` branch lines 86 and 91-96 |

An alternative, if the owner prefers it: once the classes are built the two diagrams agree on the lanes, so the three
lane boxes (`lanes-built`, `lanes-new`, `lanes-split`) could be replaced by one line, "Lanes: the 29 classes of 37b, as
built (previous diagram)", leaving this diagram to show only what differs (37b's region rule, 37l, 37n, 37f). The
proposal above is the smaller change.

## 4. Passage `mtp7zsmsxgy.36327` ("lanes")

Current text (quoted): "As built, under the limiting-step rule expression leaves the loop, so inside it the 17 lanes
differ only in their learned gains. One lane's response reaches another only through the shared extracellular pool
and the expansion W. As decided and not built: item 37f moves the bottleneck inside the loop, and item 37b adds cell
classes, so there are more than 17 lanes."

Proposed text once the branch lands: "As built, under the limiting-step rule expression leaves the loop, so inside it
the lanes differ only in their learned gains: 29 with every source on disk, `all_cells` and 28 expression classes,
item 37b's among them. One lane's response reaches another only through the shared extracellular pool and the
expansion W. As decided and not built: item 37f moves the bottleneck inside the loop."

Code: the table in section 1. The 37f clause holds (the branch does not touch the encoder); the 37b clause is
removed because 37b's classes are then built.

## 5. Gap before the branch: diagram `236f9823-56fb` does not list item 37a

Diagram `236f9823-56fb` ("What the graph holds, as decided") lists what item 37 decided and has not built. Current
text (quoted, four lines): "Also decided, not built: one universal clearance node with dose entering by concentration
(item 37k); the duplicate" / "H+ merged into one node per compartment (item 37o); an endogenous drug seeds on its own
compound (item 37m); the" / "drug-target screen's relative affinity line (item 37i) and the sequesters weight from the
carrier's share (item 37j)" / "All registered 23 Nov as amendment item 37".

Item 37a (`docs/preregistration.md` line 2835) changes what the graph holds and is not in the list: a reaction's
classes are what its catalysts assemble, two classes that can both assemble split the reaction into one node per class,
a pore on no central cell class is not added, and there is one weight per pore population. Part of it is in code:
the member removals of 37a (iii) (the muscle-type nicotinic subunits) and of 37a (v) (TRPC4AP, TRPV5, TRPV6) are rows
of `REACTOME_ENTITY_MEMBERS_REMOVED` in `experiments/build_neuronal_graph_variant.py` (main lines 109-146, commit
`2c3696d`, 27 November 2026), applied under every `--membrane-potential` build. The rest is not built:
`mechanistic_pathway_learning/graph/reactome_import.py` still gives a pore reaction the class of its first catalyst
gene in sorted order (main line 695), which 37a (i) replaces, and the same comment in
`experiments/build_neuronal_graph_variant.py` names as owed and not coded the seven anoctamins `RCT_2684901` loses
under 37a (v) and the six Kir2, Kir4 and Kir5 genes that leave Reactome's GIRK entity (main lines 127-129).

Proposed: `d37-c` ends with a semicolon, "... the sequesters weight from the carrier's share (item 37j);", so that
the list runs on, and two new lines follow it, before the closing line (viewBox from 762 to about 798):

- new `d37-e`: "pore reactions take the classes their catalysts assemble, one node and one weight per co-assembled population,"
- new `d37-f`: "and a pore on no central cell class is left out (item 37a; some of its member removals are in code since 27 Nov)"

## 6. Gap before the branch: diagram `c642a74c-b09e` labels cluster 398 "noradrenergic (LC)"

Current text (quoted): `lane4-c` "noradrenergic (LC)". The class is atlas cluster 398, and the module docstring of
`mechanistic_pathway_learning/graph/siletti_cluster_classes.py` (branch lines 36-37, main lines 34-35, unchanged since
commit `4eeb923` of 21 October 2026) says "the class is the brainstem noradrenergic and adrenergic neurons together (A1,
A2, C1, C2 and the locus coeruleus), not the locus coeruleus alone"; the same docstring gives the cluster as "Splat_398,
2,093 nuclei, medulla 86.6 percent and pons 12.8 percent by dissection" (branch lines 28-29, main lines 26-27).

Proposed: if the branch lands, the label moves to `note-c` as "noradrenergic (brainstem, cluster 398)" (section 2). If
the correction is made first, on its own: `lane4-c` "noradrenergic (LC)" becomes "brainstem noradrenergic".

The same gap is in the quantity table. Its "class weights w [N, Q]" row (table `mtp7zsmsxgy.21371`, row `.21796`,
paragraph `mtp7zsmsxgy.25416`, read in the live doc at revision 198 on 28 November 2026 by the checker of this draft)
says "How much each cell type (excitatory neurons, astrocytes, locus coeruleus, pineal and the rest) expresses a gene,
from HPA, GTEx and the Siletti atlas". The branch does not make it wrong ("and the rest" covers the new classes, and
the pituitary lineages come from HPA), but "locus coeruleus" is the cluster-398 gap, and the row also leaves out GEO
GSE100472, the pineal class's source, which was so before the branch. Proposed: "How much each cell type (excitatory
neurons, astrocytes, brainstem noradrenergic neurons, pineal and the rest) expresses a gene, from HPA, GTEx, GEO
GSE100472 and the Siletti atlas". The table is registered under passage `mtp7zsmsxgy.21164` ("what each quantity
means (lead and table .21371)"; section 7).

## 7. The registry's declarations (`configs/study_sheet_diagrams.json`), proposed and not applied

An entry lists every decision row, amendment item and code file its diagram or passage depicts (CLAUDE.md,
Documents, 24 November 2026). Proposed additions, to be applied by the session that lands the branch, after the doc is
corrected and before it stamps the entries:

| Entry | Declares now (files) | Add | Why |
| --- | --- | --- | --- |
| `c642a74c-b09e` (built) | `models/linear_response_encoder.py`, `experiments/build_cell_class_weights.py`, `experiments/run_main_model.py` | `mechanistic_pathway_learning/graph/siletti_cluster_classes.py`, `mechanistic_pathway_learning/graph/peripheral_cell_classes.py`; also proposed: `mechanistic_pathway_learning/graph/brain_expression_descriptors.py` | the first two define the atlas and endocrine classes the lanes draw and are what the branch changes; the third defines the HPA classes and the dopaminergic class the diagram draws as lanes |
| `098c9a09-8f0f` (decided) | `models/linear_response_encoder.py`, `experiments/build_cell_class_weights.py` | the same three; also proposed: `experiments/run_main_model.py` | as above; `run_main_model.py` line 410 decides which classes share the pool that `loop-note` calls "as built" |
| `mtp7zsmsxgy.36327` (passage) | `models/linear_response_encoder.py`, `experiments/build_cell_class_weights.py` | the same three; also proposed: `experiments/run_main_model.py` | the passage counts the lanes and names the shared pool |
| `236f9823-56fb` (decided) | `graph/drug_entry_nodes.py`, `configs/neomorphic_alleles.csv`, `graph/brenda_enzyme_regulation.py`, `graph/membrane_potential.py` | item `37a` in `items`; files `mechanistic_pathway_learning/graph/reactome_import.py` and `experiments/build_neuronal_graph_variant.py` | section 5: the first-catalyst choice 37a replaces (line 695) and the coded member removals |
| `mtp7zsmsxgy.21164` (passage: the quantity table) | `models/linear_response_encoder.py`, `models/noisy_or_pathway_module_model.py` | also proposed: `mechanistic_pathway_learning/graph/siletti_cluster_classes.py`, `mechanistic_pathway_learning/graph/peripheral_cell_classes.py` | its class-weights row names cell types and their sources (section 6); not needed for the branch, which leaves the row true |

The two files the branch's checker named (`siletti_cluster_classes.py`, `peripheral_cell_classes.py`) are the firm
proposal: the branch changes them, and the guard did not flag the three entries for them only because they are not
declared. The others are pre-existing omissions of the same kind; adding them makes the guard flag these entries when
those files change, which is its purpose. In JSON, for the first three entries:

```json
"files": [
  "mechanistic_pathway_learning/models/linear_response_encoder.py",
  "experiments/build_cell_class_weights.py",
  "mechanistic_pathway_learning/graph/siletti_cluster_classes.py",
  "mechanistic_pathway_learning/graph/peripheral_cell_classes.py",
  "mechanistic_pathway_learning/graph/brain_expression_descriptors.py"
]
```

with `experiments/run_main_model.py` kept in `c642a74c-b09e` and added to the other two. For `236f9823-56fb`, `"37a"`
joins `items` and the two files join `files`. The new fingerprints are written by
`PYTHONPATH=. python experiments/check_study_sheet_diagrams.py --stamp <id>` once each entry has been checked against
the doc.

The repository's copies of the doc go stale with it. `docs/study_sheet.md`, the doc's Markdown copy (a living
document, last exported from revision 197), holds the quantity row (line 156), the passage (line 216) and the
captions of the figures: line 208, for `c642a74c-b09e`, reads "17 classes as experiments/build_cell_class_weights.py
writes them; before amendment item 37", and line 212, for `098c9a09-8f0f`, "not built". The figures themselves are
`docs/study_sheet_figures/13_propagation_channels_as_built.png`, `13b_propagation_channels_as_decided.png` and
`04_graph_as_decided.png` (line 48, for `236f9823-56fb`). Once the doc is corrected they are refreshed by exporting it
again, as that copy's provenance line says.

## 8. For the owner

1. Approve, change or refuse the corrections of sections 2 to 6. Nothing is applied until you answer.
2. Whether the built diagram `c642a74c-b09e` draws the 29 lanes the code defines (proposed) or what a build on a
   given disk gives. On this disk no build runs until decision 9.155's 48 HPA cluster types are mapped (section 1),
   which is so for the 17 lanes the diagram draws today as well; after that, a build here would have 22 lanes, with
   no pituitary lane until HPA's single-cell-type table is fetched and pinned, and no pineal lane until the
   owner-supplied GEO GSE100472 counts are on the disk again.
3. For `098c9a09-8f0f`, the smaller wording change of section 3 or the alternative that leaves the lanes to the built
   diagram.
4. Section 5 reads 37a's coded member removals as built, by the same reading as section 1. If so, whether the built
   partner `a7538790-dcbd` should say so too: its counts are of the v5 graph of 5 November, and the removals change
   `member_of` edges only at the next `--membrane-potential` rebuild.
