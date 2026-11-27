# Brain expression pipeline map (amendment item 37b part (c); rulings draft section 8 (c))

A draft for the owner, written 27 November 2026 by an engineering pass that read the code only (no outside source and no
built graph), and committed the same day at the owner's request ("Just merge and push everything. I'll review it
later") before the owner had read it. It maps what amendment item 37b part (c) would touch and sets out three ways to
build it without choosing between them; nothing in it is built or ruled. Every `file:line` reference is to `main` at
`342c8b8`, the last commit before it was written, and may have moved since: `scripts/fetch_raw_sources.sh`, for one,
gained the HPA guards and pins of 27 November 2026 after it. The HPA release it names is the one pinned until decision
9.155, whose new release the build cannot yet read.

The ruling, from docs/item37_rulings_draft_2026-11-13.md:242-250 and docs/preregistration.md:2888-2895:
- 357 gene nodes on the v5 graph have unknown brain expression.
- 183 of them are in the GTEx file by symbol, and 182 of those are added by a later stage, after `annotate_brain_expression` has run.
- Every gate on `brain_expressed` reads unknown as not expressed.
- The values are to be attached after the last stage that adds gene nodes, built together with section 7's region rule (preregistration.md:2877-2879: any brain region of GTEx or of HPA's regional bulk).
- A test must fail while a gene node whose symbol is in the expression table carries no value.

Unexplained from the code: the one gene that is in GTEx by symbol but not added later. `gene_node_values` falls back to the symbol (build_physiology_graph.py:536-541). This needs the data to explain.

## 1. Stages of scripts/rebuild_data_layer.sh

The `step` helper skips any step whose output exists (:43-53). Lines 84-93 sit outside every `if`, so they run under every stage argument. The v4 graph is `graph_full_neuronal_split_binders_drugs_v4`, built by the default `graphs` stage. The v5 graph is `..._drugs_v5`, built by `fine`, which needs `graphs` to have built the split and binders graphs first.

| lines | stage | calls | input graph -> output | builds |
|---|---|---|---|---|
| 56-76 | raw sources | fetch scripts | - | both |
| 84-85 | base graph | `build_physiology_graph` (build_physiology_graph.py:744-828, main :831-867, GTEx default :842) | - -> graph_full | v4, v5 |
| 86 | gene identifier map | evidence/gene_identifier_map.py (reads graph_full genes, :218) | graph_full -> literature table | both |
| 87 | manganese | build_manganese_graph_variant.py -> manganese_extension.add_manganese (:78) | graph_full -> graph_full_manganese | v4, v5 |
| 91-93 | neuronal and oxidative | build_neuronal_graph_variant.py:302-435 | graph_full_manganese -> graph_full_neuronal | v4, v5 |
| 96-97 (graphs only) | gene and protein split | build_gene_protein_split.py -> gene_protein_split.split_graph (:203) | graph_full_neuronal -> graph_full_neuronal_split | v4, v5 |
| 98-99 (graphs only) | plasma binders | build_plasma_binder_variant.py:119-141 | neuronal and split -> graph_full_neuronal_binders, graph_full_neuronal_split_binders | v4, v5 |
| 117-119 | Open Targets statements | scope_open_targets_symptom_labels.py | reads graph_full | v4, v5 tables |
| 122-141, 151-165 | evidence v3, v4 and labels | assemble_evidence_table --graph-dir graph_full | reads graph_full | v3, v4 |
| 175-176 | drug entry (v3 table) | build_drug_entry_node_variant.py | split_binders -> split_binders_drugs | neither (v3) |
| 177-179 | drug entry v4 | same | split_binders -> split_binders_drugs_v4 | v4 |
| 181-184 | drug entry v4 with clearance | same, --clearing-enzymes | split_binders -> ..._drugs_v4_enzymes | v4 |
| 187-192 | iCite; edge evidence | build_edge_evidence.py | side table beside neuronal, drugs, drugs_v4, drugs_v4_enzymes | v4 |
| 199-206 | trials, FAERS, IMPC | IMPC reads graph_full | - | v4 |
| 213-222 (slice) | slice lineage | cp of release graph, then manganese, neuronal, split | graph -> graph_manganese -> graph_neuronal; graph -> graph_split | neither |
| 224-274 (descriptors) | descriptors and weights | build_node_descriptors, build_brain_expression_descriptors, build_cell_class_weights (read graph_full_neuronal, :243, :249, :252); split again with `--overwrite` (:255-258); binders (:259, skipped if present); drug tables `--tables-only` (:262-273) | neuronal -> split (rewritten) | v4, v5 inputs |
| 294-329 (fine) | evidence v5, reliability, labels | assemble_evidence_table --graph-dir graph_full | reads graph_full | v5 |
| 330-333 (fine) | drug entry and neomorphic alleles v5 | build_drug_entry_node_variant.py --neomorphic-alleles | split_binders -> ..._drugs_v5 | v5 |
| 334-349 (fine) | iCite; edge evidence v5; per-node tables v5 | build_edge_evidence; --tables-only | drugs_v5 | v5 |
| 350-372 (fine) | absence and mouse sources | IMPC, mouse and cross-species read graph_full | - | v5 |
| 394-437 (brenda) | derived BRENDA table | map_brenda_regulation_to_graph.py | reads graph_full_neuronal_split | either |

## 2. Gene nodes added per stage

Gene nodes are `node_type == "gene"`, with ids `GENE:<symbol>` (build_physiology_graph.py:392-394).

- **graph_full adds genes, all before the annotation.** The metabolic layer adds them at :190 and `add_gene_nodes` (:392) is called from the signalling (:458), transcription (:474) and small-molecule (:500) layers. All of this happens before the annotation at :786, so graph_full's own genes are annotated.
- **Manganese adds SLC30A10 when it is absent.** See `GENES_ADDED_WHEN_ABSENT` (manganese_extension.py:44, 87-91). The new row is blank (`blank`, :82), so its expression columns are None.
- **The neuronal stage adds genes.** In `import_reactome_layer` (reactome_import.py:379):
  - store-sensor genes (:521);
  - Reactome entity members (:541);
  - curated-reaction catalysts (:610);
  - curated-reaction activators (:615);
  - each through `add_node`, which builds the row from `blank` (:447, :474-476).

  `add_release_regulation` adds receptor genes (neurotransmission_regulation.py:60-67, `blank` :45). These stages add none:
  - oxidative regulation skips absent genes (oxidative_regulation.py:102, :119);
  - BRENDA skips them too (brenda_enzyme_regulation.py:99, :124-126);
  - curated mechanisms raises on an absent node (curated_mechanisms.py:90-95);
  - alternative members require an existing gene (curated_mechanisms.py:185-186);
  - redox pools adds metabolites only (redox_pools.py:101).
- **The split adds no gene nodes.** It adds `protein` nodes (gene_protein_split.py:43, 219-234) with all columns NaN (:222) and the four flags set False (:230-232).
- **Binders adds no nodes** (build_plasma_binder_variant.py:14).
- **Drug entry adds no gene nodes.** It adds `drug` and `allele` nodes only (drug_entry_nodes.py:77, 90, 316, 407), and carrier, enzyme and allele targets must already exist (:288, :303, :397). The build refuses if an existing node row changes (build_drug_entry_node_variant.py:239-242).

The neuronal stage (rebuild :91-93) is therefore the last stage that adds gene nodes, in both the v4 and v5 lineages.

## 3. Reads of the expression columns

"Later gene nodes" below means the manganese and neuronal additions.

- **build_physiology_graph.py:608-611**, `annotate_cell_class_expression`, reads `brain_expression_known` and `brain_expressed`. It runs in graph_full, before the later additions, so it never sees them. Those nodes are left with `expression_below_detection` set to None.
- **build_physiology_graph.py:646-655**, the transcription gate, reads all seven columns. It runs in graph_full (:796), before the later additions.
  - It gates only `regulates_transcription_of`, and no later stage adds that relation: the string does not occur in reactome_import.py, neurotransmission_regulation.py, oxidative_regulation.py, curated_mechanisms.py, drug_entry_nodes.py or docs/curated_dead_end_mechanisms.csv.
  - So it is unaffected. Here unknown means kept (:655).
- **build_physiology_graph.py:619-625**, `propagate`, reads gene `brain_median_tpm_max`. It runs in graph_full only.
  - Reactions added later get no value: RCT_* and MAR_* curated reactions (reactome_import.py:562, 602) and MAR_MN2_* (manganese_extension.py:97).
  - Catalysts added later, such as KCNK1, never pass their value to a reaction.
- **build_physiology_graph.py:798-805**, the summary counts, run in graph_full.
- **edge_evidence.py:402-405** (called from build_edge_evidence.py:129, 132) reads `expression_below_detection` with `fillna(False)`. It runs after every gene-adding stage (rebuild :190-192, :336-337).
  - A later gene node reads as not flagged.
  - Only edges of the transcription family are flagged (:406, family "transcription" :109), and those factors are graph_full genes, so in practice no later node is consulted.
- **experiment_data.py:719-720**, the loader, reads `brain_median_tpm_max` (fillna 0) and `brain_expressed` (`== True`) into the structural features (:146-149). It runs at training time on the final graph.
  - **A later gene node reads as 0 TPM and not expressed.**
- **measure_target_occupancy.py:57-66** reads `brain_expressed == True` to choose the site at :127-130. The default graph is graph_full_neuronal (:101), and the read happens after the additions.
  - **A later gene is read in plasma.**
  - The same function is reused by compare_expression_rebuild.py:44, 134 and label_review/measured_occupancy_leakage.py:104 (default graph_full_neuronal, :91).
- **apply_central_action_rule.py:92-97, 113, 126-127** reads `brain_expressed` with `fillna(False)`. The docstring example uses drugs_v4_enzymes (:48), after the additions.
  - **A target whose gene was added later counts as "no brain-expressed target".**
  - Its output is configs/centrally_acting_drugs.csv (`brain_expressed_targets` column).
- **label_review/gtopdb_leakage_cost.py:68** reads with `bool(expressed)`, and None reads as False. The graph is passed by flag (example drugs_v4_enzymes, :21), after the additions. **Unknown reads as not expressed.**
- **label_review/tissue_representation_options.py:97 and 187-189** read `brain_median_tpm_max` (a notna count) and `brain_expressed is True`. The default is split_binders (:86), after the additions. **Unknown reads as not expressed.**
- **summarise_graph.py:64, 69** count `== True`. The defaults are drugs_v4 and drugs_v4_enzymes (:27). **Unknown counts as not expressed.**
- **compare_expression_rebuild.py:55-56, 110-111** reads unknown as False by design (:9-10). This is the before-and-after tool for the fix.
- **write_descriptor_column_doc.py:124** and gene_protein_split.py:47-48 only name columns. `EXPRESSION_NODE_COLUMNS` is defined and not used anywhere.

These read the tables, not the node columns, so the ordering does not affect them:
- build_neuronal_graph_variant.py:379-380, which feeds reactome_import.py:655 (Human-GEM reactions with a brain-expressed catalyst join the electrical layer);
- curated_mechanisms.py:159-174 (`alternative_share`);
- the descriptors (build_brain_expression_descriptors.py:43-55, matching by Ensembl id or symbol through brain_expression_descriptors.py:201-212, on graph_full_neuronal, so they cover the later genes).

## 4. Where the annotation runs

- `annotate_brain_expression` is called only at build_physiology_graph.py:786.
- `annotate_cell_class_expression` is called at :790 or :794.
- `propagate_brain_expression_to_reactions` is called at :797.
- No later stage re-runs them. The only callers are that file and tests/test_brain_expression_annotation.py:54-55, 92, 101-102.
- The nearest precedent is currency tagging, which is re-applied after node additions (reactome_import.py:793-803; build_physiology_graph.py:683-685).

## 5. Tests and what a test of the ruling's form could check

**What exists now.**
- tests/test_brain_expression_annotation.py:38-93, 96-107 and 110-129 cover matching, the gate, propagation and the loader features, all on fixtures.
- tests/test_gene_protein_split.py:53-54 and :95-96 check that expression stays on the gene nodes.
- tests/test_item37_rebuild_comparisons.py:58-127 covers the comparison tool.
- tests/test_edge_evidence.py:241-250 covers the below-detection flag.
- No test checks that gene nodes added after graph_full carry values.

**A fixture test (no built graph).**
- Build a toy graph with no GENE:SLC30A10 and a toy GCT that includes SLC30A10 (the `write_gct` pattern, test_brain_expression_annotation.py:17-27).
- Run `add_manganese` (manganese_extension.py:78), or `add_release_regulation` (neurotransmission_regulation.py:39) with a one-row receptor table.
- First assert that a helper, "gene nodes whose symbol is in the expression table and whose value is null", flags the new node. This proves the test can fail.
- Then apply the fix and assert the helper returns nothing, for all the expression columns, not only `brain_median_tpm_max`.
- Add a second fixture on a `split_graph` output (gene_protein_split.py:203) that checks reaction values survive (see the pitfall in section 6).

**A data test (skipped when the graph is absent).**
- Follow the suite's skip patterns: tests/test_currency_tagging.py:68-73 and :130-136, or tests/test_chloride_charge_sum.py:35-39.
- Skip unless data/processed/graph_full_neuronal_split_binders_drugs_v5/nodes.parquet (and the v4, v4_enzymes, graph_full_neuronal and split_binders graphs) and the GTEx GCT exist.
- Load the GCT with `load_brain_expression` (:506) and assert that no gene node whose symbol is in the table carries a null value.
- Use whatever table the annotation reads once the region rule adds HPA regional bulk (data/raw/hpa/rna_brain_region_hpa, fetch_raw_sources.sh:133).
- Out of scope for the test: the 174 genes in no GTEx row, and composite symbols such as "HBA1; HBA2" (gene_protein_split.py:57-59).
- With data/processed absent in this checkout, this test would be skipped here.

## 6. Ways to fix it (not chosen between)

**(A) Annotate again at the end of the neuronal stage.** After build_neuronal_graph_variant.py:419 and before the write at :424, call the three functions on the completed table.
- This needs the inputs for the cell-class step: HPA cluster types, GEO pineal and Siletti (defaults at build_physiology_graph.py:845-850). Without them, `expression_below_detection` falls back to the brain threshold alone (:791-795).
- It touches rebuild :91-93 (and the slice at :217-219), and every downstream graph has to be deleted and rebuilt, because of the skip rule (:43-53).
- What it leaves wrong:
  - Nothing stops a future stage from adding blank genes except the test.
  - `propagate` now gives values to the RCT_* and MAR_* reactions. That changes the loader's reaction features (experiment_data.py:719), which compare_expression_rebuild.py does not count.
  - `propagate` also recomputes `brain_expression_known` for every node (:625).
- A variant is to have each gene-adding stage (manganese and neuronal) re-annotate its own additions.

**(B) A separate annotation stage on the finished graphs.** Run it after the drug-entry steps (rebuild :175-184 and :330-333) and before edge evidence (:190-192, :336-337), which reads `expression_below_detection`.
- **Pitfall:** after the split, the `catalyzed_by` ends are protein nodes holding NaN (gene_protein_split.py:222, 255-261). `propagate` (:619-624) would then set every reaction to NaN, so it would have to go through the `encodes` edges instead.
- An in-place rewrite cannot be a `step` keyed on nodes.parquet, and it leaves the recorded `nodes_sha256` out of date (build_drug_entry_node_variant.py:272-276).
- What it leaves wrong: the intermediate graphs stay unannotated unless they are also processed, and the readers' defaults point at them (measure_target_occupancy.py:101, measured_occupancy_leakage.py:91, tissue_representation_options.py:86).

**(C) Compute expression where it is read.** Give the loader (experiment_data.py:719-720) and the site, central-action and leakage readers one shared function that reads the expression table directly, as build_neuronal_graph_variant.py:379-380 and the descriptors already do. The graph_full annotation stays for the transcription gate (:796).
- No graph file or hash changes.
- What it leaves wrong:
  - The node tables still carry blanks, so a test of the ruling's form (a gene node carrying no value) would still fail unless the columns are dropped.
  - "Attached after the last stage" arguably reads as a graph-build change.
  - Every reader has to switch, and a missed one stays wrong.

**Common to all three.**
- The region rule changes `annotate_brain_expression`'s inputs, since it reads GTEx only (load_brain_expression, :506-528).
- The neuronal gate keeps its own GTEx-only set (build_neuronal_graph_variant.py:380, reactome_import.py:655). After the region rule, that set would disagree with the node flag unless it is changed too.
- The preflight compares only modification times of the inputs it knows (experiments/check_rebuild_inputs.py:1-47).
