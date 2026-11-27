# The carrier relation `coproduct_of` mixes regeneration with de novo synthesis

Measured 26 October 2026 at commit 0b976bf by `experiments/measure_coproduct_de_novo_split.py`, on
`data/releases/v0.4/graph` and `data/releases/v0.4/graph_full`. A record: corrected by a dated addition, not by an
edit. The v5 build was lost with its container and `data/processed` was empty in the checkout this was run from, so
the counts below are the released v0.4 graph's and are not a statement about the current graph (CLAUDE.md,
"A measurement carries the graph it was taken on"). Both v0.4 graphs give identical counts, since the two differ
outside the metabolic layer.

Nothing here changes a graph, a rule, a model input or a registered value.

## What was measured and why

`mechanistic_pathway_learning/graph/cofactor_edges.py` marks an edge as a carrier edge when the metabolite's name is
on the carrier list. That clause keys on the metabolite's identity and not on what the reaction does to the moiety's
total, so one relation and so one learned gain carries two physically opposite processes:

- **regeneration**, where the reaction also consumes a metabolite of the same moiety, redistributing material inside
  a conserved total that does not move. This is the behaviour the low carrier gain exists to produce: the module
  docstring's reason for the layer is that a PAH loss of function leaving tetrahydrobiopterin unconsumed must not
  raise tyrosine hydroxylase flux and dopamine, "the opposite of what phenylketonuria shows".
- **de novo synthesis**, where it does not, so the moiety's total increases. This is the behaviour a synthesis defect
  needs: the same docstring records that dropping carrier edges altogether left "a GCH1 loss lowering
  tetrahydrobiopterin with nothing downstream able to see it", and that 14 slice genes with 30 positive pairs make or
  recycle carriers.

Buffered-fast and drainable-slow are the two timescales of a conserved moiety, and they want opposite gains. The test
applied here is whether the edge moves the moiety's total: an edge is regeneration when its reaction consumes any
metabolite of its product's family, and de novo when it does not. That definition is the script's, not the
repository's, and it is the operational form of "does this edge change the total".

## The counts

| kind | edges | share |
| --- | --- | --- |
| recurring-pair clause, no named family | 779 | 72.2% |
| regeneration | 251 | 23.3% |
| **de novo** | **49** | **4.5%** |
| total `coproduct_of` | 1,079 | |

A recurring substrate-product pair is a redistribution by construction, so the pair-clause edges belong with
regeneration; counted that way the split is 1,030 against 49. Among the name-clause carriers alone (300 edges) de
novo is 49, or 16.3%.

By family, de novo against regeneration: acyl carrier 23/8, folate 11/60, lipoamide 6/9, vitamin B6 3/9, biopterin
2/37, quinone 2/20, thioredoxin 2/29, ascorbate 0/55, cytochrome 0/17, ferredoxin 0/7.

## The biopterin route, which is the case the layer was built for

Of 39 carrier `product_of` edges into a biopterin, **two** are de novo and both are sepiapterin reductase
(`MAR04167` and `MAR08739`, gene SPR). The other 37 are regeneration: QDPR, PCBD1 and PCBD2, the hydroxylases TH,
PAH, TPH1 and TPH2 handing back 4alpha-hydroxytetrahydrobiopterin, plus transport and exchange reactions.

Where the de novo signal travels is the point. **Every product of GCH1 and of PTS is a main `product_of` edge, not a
carrier edge** — dihydroneopterin triphosphate, 6-pyruvoyltetrahydropterin, formate and the rest carry no name from
the carrier list. Only the last step of de novo synthesis, SPR to tetrahydrobiopterin, is a carrier edge. So the
whole de novo route into the biopterin pool passes through exactly one carrier-gained edge, at a gain that starts
near 0.04 (logit offset -3).

The consequence is that within the biopterin family one learned gain is fitted against 37 regeneration edges and 2
de novo edges, which want it low and high respectively; the de novo side is outvoted about 18 to 1 within its own
family. The GCH1 result the module docstring reports rests on that single edge.

## An inconsistency in the carrier list, found while measuring

`dihydrofolate` is on `DEFAULT_CARRIER_METABOLITE_NAMES`, as is every substituted folate (5,10-methylene-THF,
5-methyl-THF, 10-formyl-THF, 5,10-methenyl-THF, 5-formyl-THF, 5-formiminotetrahydrofolate). Plain `THF` is not. DHFR's
two products are therefore treated differently in the same reaction: THF takes full main-substrate coupling and
dihydrofolate takes carrier treatment. Since THF is the unsubstituted acceptor of the one-carbon pool, the conserved
folate moiety is cut across carrier and main treatment at the node where a conservation constraint would bind.

Whether that is an oversight in the list or a decision is not recorded anywhere this measurement found, and it is
left for the owner rather than assumed.

## What this does and does not support

It supports splitting `coproduct_of` by whether the reaction consumes the same moiety, which is computable from the
stoichiometry already in the graph and needs no literature sourcing. On the v0.4 slice that moves 49 edges into a
relation of their own and gives de novo synthesis a gain separate from regeneration.

It does not establish that the split improves any score. No model was trained and no label was read. The gains are
learned, so a fit could in principle find a value that serves both processes; the measurement says only that one
parameter is being asked to do two opposite jobs, and how lopsided the evidence for it is within each family.

## Limits of the measurement

- The v0.4 graph, not the current one. The family counts will move with a rebuild, and the biopterin route should be
  re-measured on v5 before being relied on.
- The de novo/regeneration test is this script's definition, stated above, not a repository rule.
- Transport reactions count as regeneration, which is correct, since a transport reaction moves one form of the
  moiety between compartments. Exchange and demand reactions also count as regeneration, which is an artefact of
  their being boundary pseudo-reactions rather than physiology; the script prints the subsystem so they can be told
  apart. Of the 39 biopterin edges, 10 are transport reactions and 3 are exchange or demand reactions, so 3 are the
  artefact and 10 are a correct reading of redistribution across compartments.
- The 779 pair-clause edges have no family under the script's grouping, so their assignment to redistribution is an
  inference from how the clause is written and not a measurement.
