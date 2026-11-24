# Item 21: the pinned Human-GEM against upstream's merged fixes and open issues

Research pass of 24 November 2026, on Fable 5.2 throughout (no fallback). Nothing in the repository was changed.
Every proposal here is for the owner to rule on; an upstream issue or merge is treated as a lead, not as a correction.

Working files (all under the session scratchpad
`/tmp/claude-0/-home-user-perturbation-symptom-modules/bb4ac276-3385-5b5c-bac0-09d70d6ba1f5/scratchpad/`):
- `item21_human_gem_sweep_2026-11-24.progress.md`: the step log.
- `item21_proposed_rows_2026-11-24.csv`: the 9 proposed rows, in the format of `configs/human_gem_corrections.csv`.
- `item21_work/out/classified_changes_refined.tsv`: one row per changed reaction and per changed species row, with
  its class, what changed, and the upstream pull request that changed it (4,062 rows).
- `item21_work/out/by_pr_table.md`, `neuro_highlights.tsv`, `open_issues_digest.md` (the 51 open issues, full text),
  `closed_1085.md`, `closed_1104.md`, `yml_diff.json`, `tsv_diff_*.json`, `attribution.json`.
- `item21_pages/`: every page read with `experiments/read_public_page.py`, each with address, time and SHA-256.
- Scripts: `item21_diff.py`, `item21_attrib.py`, `item21_classify.py`, `item21_refine.py`.

## 1. The pin and upstream

- The pin is confirmed. `scripts/fetch_raw_sources.sh` pins commit `93e8d292a0cb`; upstream's tag `v2.0.1` peels to
  `93e8d292a0cbf9944c15614205dabc47770c07a4`. The files under `data/raw/Human-GEM/model` (`Human-GEM.yml`,
  `Human-GEM.xml`, `metabolites.tsv`) are byte-identical to the tag's (`cmp`).
- Upstream has no changelog file (release notes are the text of the GitHub release). The record of what was merged
  is the commit log: after `git fetch --depth=1000 origin main` in the read-only clone, 68 commits lie between the
  pin and the 2.1.1 release merge `6812be2` (7 October 2026), each model change one squash-merged pull request.
  **30 pull requests changed the model** (`Human-GEM.yml` or `metabolites.tsv`); 2.1.0 (`d1364df`, 5 October 2026)
  holds nearly all of them, 2.1.1 adds gene-table and export fixes only.
- **Upstream did not stop at 2.1.1.** Its `develop` branch (head `3c5fe86d`, 18 November 2026, fetched at depth 300)
  holds a further large curation after 2.1.1 that is in no release. Of the 51 open issues, 26 carry the label
  "fixed in develop". So 2.1.1 is not upstream's current view of the model, and a next release will move it again.

## 2. Whether GitHub's search API was readable

Yes. Through `experiments/read_public_page.py` (which found no robots file on `api.github.com`, "none served, which
the protocol treats as no restriction"), three requests were read and saved, and none was refused:
- open issues, `q=repo:SysBioChalmers/Human-GEM+is:issue+is:open`: 51 issues, bodies included (saved
  `item21_pages/9d4df1e600182f8d.txt`);
- closed issue #1085 and merged pull request #1104, by title words with `is:issue` / `is:pr`.
One request without `is:issue` or `is:pr` answered HTTP 422, a malformed query and not a refusal. Issue comments were
not read (the search API returns bodies only); #1085's comments, where PR #1104 says its "reasoning and evidence"
are, are therefore unread.

## 3. Step 1: what the merged changes alter (v2.0.1 to v2.1.1)

Two listings, kept apart:

**From the commit log (what upstream says it changed):** the 30 pull requests in the table of section 5. The
largest by their own description: #1090 "one base id per metabolite" (duplicate metabolites merged, reactions that
became identical merged), #1104 (structures, formulas, identities; closes #1085), #1105 and #1106 (an "evidence
review" of earlier curation and of pre-existing reaction and gene-rule errors), #1107 (metabolite identity and
cross-references; 221 peptides to all-L, L-carnitine's structure, statins), #1087 and #1086 (cross-references),
#1100 (PXMP2 on 40 peroxisomal transports), #1116 (Ca2+ ATPases split by membrane, ER and Golgi Ca2+ release),
#1096 and #1121 (vitamin E and vitamin D), #1044 (retinoates), #1041 and #1040 (duplicate transports and
lipoxygenase copies).

**From a structural diff of the model files (what actually differs):** `item21_diff.py` parsed both `Human-GEM.yml`
files and both `metabolites.tsv`, `reactions.tsv`, `genes.tsv`.

| | v2.0.1 (pin) | v2.1.1 | removed | added | changed |
|---|---|---|---|---|---|
| species rows (yml) | 8,460 | 8,374 | 134 | 48 | 316 (formula 248, charge 113, name 58, compartment 1) |
| reactions (yml) | 12,877 | 12,748 | 155 | 26 | 335 (equation 211, gene rule 130, name 68, reversibility 29, subsystem 6) |
| genes (yml) | 2,848 | 2,870 | 5 | 27 | - |
| `metabolites.tsv` rows | 8,460 | 8,374 | 134 | 48 | 3,269 rows with a changed cell (metPubChemID 2,119, metSmiles 905, metInChI 901, metSeedID 741 (a new column), metMetaNetXID 585, metLipidMapsID 248, metChEBIID 217, metHMDBID 86, metBiGGID 78, metKEGGID 55) |
| `reactions.tsv` rows | 12,877 | 12,748 | 155 | 26 | 6,584 (cross-references; `spontaneous` flag 181) |

In all, **516 reactions** differ (155 removed, 26 added, 335 changed) and **3,546 species rows of 1,921 base
metabolites** differ in at least one cell that either file holds.

## 4. Step 2: which of these are in the pinned model as the project reads it

`data/processed` does not exist in this container (no rebuild has been approved), so nothing here was counted on a
graph. It was read from the pinned model files and from the code that reads them, and that is all it is:

- `build_physiology_graph.build_metabolic_layer` makes a node of **every** species and every reaction of the model
  and filters none, so every removed or changed reaction and species above is in the base metabolic layer by
  construction. Whether a given one survives into `graph_full_neuronal` or lies on any route to a labelled node was
  not checked and cannot be without the graph tables.
- What a build reads from the model, from the code: a reaction's participants with the sign and magnitude of their
  coefficients, its reversibility, the **set** of genes in its rule (the and/or structure is kept as an attribute,
  not as edges), its name and subsystem as attributes; a species' id, name (which feeds the currency name rule),
  compartment and charge (SBML `fbc:charge`, a node descriptor); and from `metabolites.tsv` three columns only:
  `metPubChemID` (the OmniPath small-molecule join), `metChEBIID` (laboratory labels, ChEMBL) and `metSmiles` (node
  descriptors, from the first row of each base metabolite). No code reads a formula into the graph, nor any other
  cross-reference column, nor `reactions.tsv`.
- Currency: the name list of `tag_currency_metabolites.py` was applied exactly. The degree rule needs the built
  graph; it was approximated on the pinned model's reaction counts (cutoff 137 reactions, 42 species, of which only
  L-carnitine[c], arginine[c] and tryptophan[c] are not already on the name list). That approximation is stated, not
  measured on a graph.

## 5. Step 4: classification of the merged changes

Rules (in `item21_classify.py` and `item21_refine.py`). A changed reaction **changes nothing the encoder reads**
when its non-currency participants with their coefficients, its reversibility and its gene set are all equal in the
two versions (so only currency participants, the and/or structure, the name or the subsystem moved). A changed
species row changes nothing read when its name, compartment, charge and `metChEBIID` are equal, a changed PubChem
id is in neither side of OmniPath's `small_molecule_protein.tsv`, and a changed SMILES gives the same RDKit
descriptors through the project's own `physicochemical_properties` (246 of the 446 base metabolites whose first-row
SMILES changed: stereochemistry and notation). "Named in the corrections table" means the id has a row in
`configs/human_gem_corrections.csv`; section 6 says for each whether upstream agrees.

| | needs a ruling | changes nothing the encoder reads | named in the corrections table | total |
|---|---|---|---|---|
| reactions | **460** | 53 | 3 | 516 |
| species rows | 795 | 2,734 | 17 | 3,546 |
| the same, as base metabolites | **431** | 1,482 | 8 | 1,921 |

The 460 reactions: 155 removed upstream (duplicates merged into a twin, or deprecated), 26 added, and 279 changed,
of which 118 in non-currency participants, 108 in the gene set only, 14 in both, 14 in reversibility only, 12 in
coefficients and reversibility, 8 in coefficients only, 5 in other combinations. The 53 that change nothing: 22
currency participants only (a proton, NADPH for NADH, water), 19 name only, 11 both, 1 name and subsystem.

The 431 base metabolites: 96 removed (merged into another id, which renames nodes), 31 added, 84 with a SMILES
change that moves a descriptor, 53 a ChEBI id only, 44 formula with SMILES, 36 ChEBI with SMILES, 38 a charge
(with formula, some with SMILES), 14 a name only, 6 a PubChem id that OmniPath's small-molecule table holds, 1 a
compartment (MAM00208, c to m), the rest combinations. The 1,482 that change nothing are cross-reference cells no
code reads, SMILES rewrites that leave the descriptors as they were, and 46 formula-only changes.

By pull request (a change touched by two pull requests is counted under each):

| PR | title (commit subject) | reactions: ruling / nothing / in table | species rows: ruling / nothing / in table |
|---|---|---|---|
| #1090 | fix: one base id per metabolite, and correct cytochrome c and water MetaNetX ids | 128 / 0 / 0 | 94 / 0 / 1 |
| #1105 | fix: corrections to curation since v2.0.1 from an evidence review | 102 / 18 / 0 | 105 / 75 / 0 |
| #1106 | fix: pre-existing reaction and GPR errors found in the curation review | 70 / 5 / 0 | 17 / 0 / 0 |
| #1100 | feat: annotate small-solute peroxisomal transport with PXMP2 | 40 / 0 / 0 | 0 / 0 / 0 |
| #1096 | fix: vitamin E beta-oxidation GPRs and electron acceptor, CYP4F2 for omega-hydroxylation | 34 / 0 / 0 | 4 / 0 / 0 |
| #1107 | fix: pre-existing metabolite identity, structure and cross-reference errors | 30 / 19 / 0 | 148 / 444 / 0 |
| #1121 | fix: vitamin D C-23 pathway, FAD hydrolysis and 9-cis-retinol GPRs | 20 / 0 / 0 | 7 / 0 / 0 |
| #1041 | fix: correct mechanism and stoichiometry of duplicate transport reactions | 14 / 2 / 0 | 0 / 0 / 0 |
| #1044 | fix: MAM01026 is 4-oxo-13-cis-retinoate; merge duplicate and correct CYP26 stoichiometry | 13 / 0 / 0 | 10 / 2 / 0 |
| #1095 | fix: QC check for reactions split across compartments, and curation of those found | 12 / 0 / 0 | 7 / 0 / 0 |
| #1028 | fix: couple non-ETF flavoenzymes directly to ubiquinone | 7 / 0 / 0 | 1 / 0 / 0 |
| #1094 | fix: use NADPH in CYP2E1 fatty-acid hydroxylations | 6 / 5 / 0 | 19 / 0 / 0 |
| #1116 | fix: separate the Ca2+ ATPases by membrane and add ER and Golgi Ca2+ release | 6 / 1 / 0 | 2 / 0 / 0 |
| #1104 | fix: curate metabolite structure, formula and identity inconsistencies | 5 / 8 / 1 | 259 / 37 / 12 |
| #1099 | fix: balance reactions that break stoichiometric consistency | 5 / 0 / 0 | 3 / 5 / 1 |
| #1040 | fix: remove charge-imbalanced duplicate lipoxygenase reactions | 5 / 0 / 0 | 0 / 0 / 0 |
| #1081 | fix: route SQOR and CHDH through ubiquinone, drop PRODH2 from proline reactions | 5 / 0 / 0 | 0 / 0 / 0 |
| #1043 | feat: enable collagen secretion and remove duplicate MAR09553 | 3 / 0 / 0 | 2 / 0 / 0 |
| #1089 | fix: merge duplicate galactose-1-phosphate and curate the galactose pathway GPRs | 3 / 0 / 0 | 1 / 0 / 0 |
| #1093 | fix: apply remaining modifyModel.m curations from #418 | 3 / 0 / 0 | 0 / 0 / 0 |
| #1047 | feat: add (S)-dihydroorotate transport and exchange reactions | 2 / 0 / 0 | 1 / 0 / 0 |
| #1030 | fix: reformulate SAM synthesis GPR and remove non-catalytic MAT2B | 2 / 0 / 0 | 0 / 0 / 0 |
| #1033 | feat: associate voltage-gated and store-operated Ca2+ channels with MAR11311 | 1 / 0 / 0 | 0 / 0 / 0 |
| #1038 | fix: remove LDHAL6A from MAR11479 for GPR consistency with MAR11476 | 1 / 0 / 0 | 0 / 0 / 0 |
| #1039 | feat: add cellular succinate export via MCT proton symport | 1 / 0 / 0 | 0 / 0 / 0 |
| #1087 | fix: add and correct reaction and metabolite cross-references | 0 / 0 / 0 | 197 / 1458 / 5 |
| #1084 | fix: export each metabolite's InChI from metabolites.tsv | 0 / 0 / 0 | 82 / 5 / 0 |
| #1088 | fix: correct two metabolite compartments and curate the NAAA ceramidase GPRs | 0 / 0 / 2 | 3 / 0 / 0 |
| unattributed | cells my attribution did not track (unread columns only) | 0 / 0 / 0 | 0 / 836 / 1 |

**What this means for "decided one by one".** 460 reactions and 431 metabolites cannot be read against two sources
each in one pass, and this pass did not try. Upstream's pull requests cite sources for part of them (#1105 to #1107
and #1116 name PMIDs, Rhea and UniProt entries per change in their commit messages; #1090, #1087 and #1104 mostly do
not), and none of those citations was read here except where section 8 says so. So the 460 and 431 are a **list of
candidates with their upstream reason**, in `classified_changes_refined.tsv`, not proposed corrections.

**Changes that touch a transmitter or the calcium pools** (30 reactions, `neuro_highlights.tsv`), listed because
they are where a ruling would matter most to this project, none read against sources here:
- #1105 removed the seven Recon3D "secretion via secretory vesicle (ATP driven)" reactions MAR00052 (5-HTP),
  MAR00058 (acetylcholine), MAR00065 (adrenaline), MAR00334 (dopamine), MAR01396 (glycine), MAR01442 (histamine),
  MAR01555 (noradrenaline) and went "back to the HMR stoichiometries (2 ATP per 3 amines or acetylcholine, 1 ATP per
  3 GABA, glycine or beta-alanine)", citing PMID 32165585; #1106 then took the VMAT rule off the 5-HTP transport
  MAR07634.
- #1116 removed MAR07629 (Ca2+ export with every Ca2+ ATPase family on one rule), and added SERCA, SPCA, IP3
  receptor, ryanodine receptor and TMCO1 reactions MAR20212 to MAR20216 with new species Ca2+[r] and Ca2+[g]; #1033
  put 15 voltage-gated and store-operated channel genes on MAR11311. These overlap what the project's own Reactome
  layer and neuronal ion pools already model, so adopting them without a check could double-count.
- #1105 made the Pictet-Spengler condensations of dopamine, noradrenaline, adrenaline and serotonin one-way with
  changed coefficients (MAR06807, MAR06742, MAR06744, MAR04554); #1081 and #1106 rerouted and removed the choline
  dehydrogenase reactions (MAR08441, MAR04696).

## 6. The corrections table against upstream 2.1.1

Compared row by row (82 rows; printed in the session, summarised here). This matters twice: for what is "already in
the table", and because every row carries a `pinned_value` that must still hold, so **a move of the pin makes the
rows below raise until the table is rewritten**.

- **Upstream 2.1.1 agrees with the table**: MAM01511 ChEBI blank (both rows); MAM03652c renamed MAM03885c;
  MAM20077m renamed MAM20089m; the three ids of MAM03652e and the two of MAM20077n; the MAM00373 15(R)-HEPE
  structure (c, n, r, x) and the MAM02766 pristanic acid structure and name. On a 2.1.1 pin these rows would be
  dropped, not kept (their pinned values are gone).
- **Upstream 2.1.1 differs, so the row would still be needed** (re-anchored): the deuterated ChEBI ids of MAM03323
  (diazepam), MAM02505, MAM02973 and MAM03796 (upstream still carries the deuterated id; MAM03787's row was removed
  upstream altogether); MAM00373's ChEBI (blank upstream, CHEBI:90819 in the table); MAM02766's ChEBI (upstream
  CHEBI:77268 alone, the table keeps both); MAR02560 and MAR02571 (unchanged upstream, still the "hydrolysis");
  MAR20093 to MAR20097 (upstream keeps all five NAAA reactions in the cytosol, and writes MAR20096 and MAR20097 as
  ASAH1 or NAAA or ACER2 or ASAH2 where the table has ASAH1 or NAAA); MAR05339 (upstream keeps NAAA on it); the
  added transport MAR90001 and the six added lysosomal species (absent upstream; MAM20076n is MAM20076c upstream, so
  the `copy_of` template id changes).
- Item 37o's "17 identifiers absent from that release taking upstream's replacements" (ruling Q3) are not rows of
  the csv; where they are held was not traced in this pass.

## 7. Step 3: the issues item 21 names

All four open issues were read in full from the search API's answer. Their named reactions were then looked up in
the pinned yml.

**#1185** (open, 1 November 2026, no "fixed in develop" label): "87 reactions are charge-unbalanced although their
mass balances". It lists the 87 by subsystem and four causes: a redox step without its carrier, oxidised fatty acids
at another protonation state than their neighbours, reactions drawn with the wrong product (six epoxide hydrolase
reactions MAR04027 to MAR04037, which release a catechol where the enzyme makes a dihydrodiol), and a wrong formula
or charge of one species. It cites no literature; it proposes that "a reaction is changed only where a database
entry or a paper names the carrier, the protonation state or the product". **In the pin: all 87 are present, each
with exactly the charge imbalance the issue gives and balanced mass** (computed from the pinned formulas and
charges). Only one of them (MAR06814) changed between 2.0.1 and 2.1.1. Two are already repaired in the corrections
table (MAR02560, MAR02571). The item's caution holds in the other direction as well: the 87 is upstream's count
after its develop-branch fixes, and a crude count on the pin gives 184 charge-unbalanced reactions with balanced
mass (this includes placeholder R and X formulas, so it overstates).
Classification: the missing piece of most of these is a proton, NAD(P)H, O2, H2O2 or glutathione, all currency, so
the part of a repair the encoder would read is the direction, the reversibility and any gene added, not the carrier.
No repair is proposed upstream for 85 of them, so there is nothing to classify yet beyond "lead".
Three of the 87 bear on this project directly and are not fixed anywhere: **MAR03119 "tryptase (melatonin)"**,
melatonin + H2O <=> 6-hydroxymelatonin + 2 H+, reversible and gene-free in the pin (melatonin is never-currency, so
this edge propagates as written); and the serotonin and melatonin biosynthesis reactions MAR04549, MAR04552 and
MAR04553, which were not examined.

**#1173** (open, labelled "fixed in develop" through pull request #1177, in no release): "Reaction equations have
wrong cofactors or directions, and some duplicates form loops". A long evidence table, each row graded by upstream
("strong", "moderate", "weak") with what was read ("abstract only", "cited papers unread"). The oxidation-as-hydrolysis
pattern: MAR01389 and MAR02559 were rewritten on develop as hydroperoxide + 2 GSH => hydroxy acid + GSSG + H2O "with
the GPR and EC of MAR00960", citing RHEA:76707; and "the same oxidation-as-hydrolysis pattern is on MAR02545,
MAR02560, MAR02567, MAR02571, MAR02577 ... left for the bile-acid and eicosanoid curation". Those are the seven.
**In the pin: all seven are present as described.** MAR02560 and MAR02571 are in the corrections table; MAR02567 and
MAR02577 are the nuclear and peroxisomal copies the owner flagged for follow-up; MAR01389, MAR02559 and MAR02545 are
proposed in section 8. A search of the pin for the same shape (X + H2O <=> Y + 2 H+) returns nine more: MAR01383
(9-deoxy-delta12-PGD2), MAR03119 (melatonin, above) and the six epoxide hydrolase reactions; all are on #1185's list.
Other rows of #1173 that touch this project and were not read against their sources: MAR07634 (5-HTP export
rewritten as a gene-free carrier, citing Neels 2008), MAR06734 and MAR06738 (salsolinol formation made one-way and
spontaneous), MAR11311 (Ca2+ channels one-way), MAR04548 (melatonin 6-hydroxylation given O2 and NADPH and merged
into MAR08566), MAR11314 (ATP-driven normetanephrine secretion removed, graded "weak: absence of evidence only"),
MAR04691 (a SLC6A1 GABA transport duplicate merged), and the vesicular secretion notes (VMAT, VAChT, VIAAT papers).

**#1164** (open, 18 October 2026, no label): 12-lipoxygenase reactions copied into compartments where ALOX12 is not
found (MAR01030 [e], MAR01033 [r], MAR01034 [x] beside MAR01029 [c]); the hydroperoxide reduction MAR01037 and
MAR01039 carrying ALOX12 where a glutathione peroxidase belongs; hepoxilin A3 formation MAR01043, MAR01045,
MAR01048, MAR01049, MAR03918, MAR03924 carrying the glutathione peroxidases although it consumes no glutathione;
MAR01010 (14,15-DiHETE <=> 15(S)-HPETE, no O2, no reductant); MAR01026 (an epoxide hydrolase reaction in the
nucleus); and the structure of MAM01048. It cites UniProt P18054, P07203, P36969, P07099, P34913, P16050, Q9BYJ1,
EC 1.11.1.9, RHEA:50216 and RHEA:37951, and Dadaian 1999 (doi 10.1016/s0022-2275(20)32129-5). **In the pin: all 15
reactions are present exactly as the issue prints them.** None is in the corrections table. Every one would change
edges the encoder reads (gene sets, or whole reactions removed), so all 15 need a ruling; none was read against its
sources here, and the issue itself leaves the hepoxilin synthase undecided ("Decide the enzyme").

**#1119** (open, 28 September 2026): "Ceramidase reactions are in the cytosol, where no ceramidase acts". Names
MAR20096, MAR20097 and the generic MAR00716 and MAR00753; cites PMID 12764132 (ASAH1, lysosome), 15655246 (NAAA,
lysosome), 16940153 (ACER2, Golgi), 15845354 (ASAH2, plasma membrane), the four UniProt entries, RHEA:38891 and
RHEA:41291; proposes splitting ceramide hydrolysis into lysosome (ASAH1 or NAAA), Golgi (ACER2) and plasma membrane
(ASAH2) "as a future action". **In the pin**: MAR20096 and MAR20097 are already moved to the lysosome with ASAH1 or
NAAA by the corrections table, on sources the project read itself. **MAR00716** (phytoceramide pool) and **MAR00753**
(dihydroceramide pool) are in the pin, cytosolic, with ACER3 or ASAH1 or ACER1 or ACER2 or ASAH2, and are not in the
table: they need a ruling, and the related decision on MAR20096/97 is recorded here so they can be read together
without being precedent. The issue's other half (a Golgi ACER2 and a plasma-membrane ASAH2 reaction for C16 and C12
ceramide) is what the table's own note on MAR20096 already calls "reactions of their own". #1173 adds that the
Golgi ACER3 reactions MAR20084, MAR20086 and MAR20088 release elaidate where their 9Z substrates give oleate.

**#1085** (closed by pull request #1104, in 2.1.0): the issue body lists, without literature, MAM20077 used for two
compounds, MAM00373e "holds another compound", MAM03652c's formula, stereochemistry that differs between
compartment rows (MAM00040n, MAM00293e, MAM01050e, MAM01316, MAM03887x, MAM03247e, MAM03848, MAM03856, MAM03590c),
4-nitrocatechol and PNP charges, H2S, and pristanal and pristanic acid. **PR #1104**'s body: MAM20089m, "MAM00270 is
20-HETE (it was named 10-HETE)", MAR20093 as palmitoylethanolamide hydrolysis, MAM20017n merged into MAM20015 and
MAR20019 rewritten, MAR03138 deprecated into MAR09550, peptide charges, and structures removed from polymers; "no
reaction becomes mass- or charge-imbalanced; 12 become balanced". It names no paper; its evidence is said to be in
the comments of #1085 and in #1109, which were not read. In the classification #1104 accounts for 259 species rows
and 5 reactions needing a ruling, beside the 12 species rows and 1 reaction the table already names.

## 8. Step 5: proposed rows (9 rows, three reactions), for the owner's ruling

Only the three remaining reactions of the oxidation-as-hydrolysis pattern were taken as far as sources, because item
21 names them, the owner has already ruled on their 15(R) twin, and their sources could be read in this pass. The
rows are in `item21_proposed_rows_2026-11-24.csv`, in the table's nine columns, each `ruling` cell reading
"PROPOSED 24 November 2026, not ruled". Their pinned values were checked against the pinned yml with the project's
own `parse_equation` and `parse_gene_rule`, and each corrected equation balances in mass and charge on the pinned
formulas (C20H29O4, charge -1, + 2 GSH -> C20H29O3, charge -1, + GSSG + H2O).

What the pin holds for all three: the hydroperoxide is made by a lipoxygenase (5(S)-HpEPE by MAR02544, ALOX5;
15-HpETrE by MAR01388, ALOX15 or ALOX15B; 15(S)-HpEPE by MAR02558), and its only link to the hydroxy acid is a
gene-free, reversible "hydrolysis" with the **hydroxy acid as nominal substrate**, +2 in charge. Since the build
takes the nominal direction, the graph's edges run from product to precursor.

| reaction | pinned | proposed equation | proposed name |
|---|---|---|---|
| MAR02559 | 15(S)-HEPE + H2O <=> 15(S)-HpEPE + 2 H+ | `MAM00379c + 2 MAM02026c -> MAM00376c + MAM02027c + MAM02040c` | Glutathione: 15(S)-HpEPE oxidoreductase |
| MAR02545 | 5(S)-HEPE + H2O <=> 5(S)-HpEPE + 2 H+ | `MAM01041c + 2 MAM02026c -> MAM01039c + MAM02027c + MAM02040c` | Glutathione: 5(S)-HpEPE oxidoreductase |
| MAR01389 | 15(S)-HETrE + H2O <=> 15-HpETrE + 2 H+ | `MAM00391c + 2 MAM02026c -> MAM00378c + MAM02027c + MAM02040c` | Glutathione: 15-HpETrE oxidoreductase |

Proposed gene rule for all three: `ENSG00000167468 or ENSG00000233276` (GPX4 or GPX1), with two alternatives the
owner chooses among (below).

**Sources read, on their own.**
1. **Schwarz et al. 2023**, Redox Biol 59:102593, PMID 36608588, [doi:10.1016/j.redox.2022.102593](https://doi.org/10.1016/j.redox.2022.102593),
   full text PMC9827380 read through the PubMed connector. Recombinant human GPX1, GPX2 and GPX4,
   glutathione-reductase-coupled assay, 17 peroxides at 50 uM, among them 5(S)-HpEPE and 15(S)-HpEPE. "The activity
   of GPX2 against all three hydroperoxides derived from eicosapentaenoic acid (5S-, 12S-, and 15S-HpEPE) and the
   hydroperoxides derived from eicosadienoic acid (15S-HpEDE) and docosahexaenoic acid (17S-HpDHA) was very low. In
   contrast, both GPX1 and GPX4 were able to reduce these five substrates, and GPX1 again showed higher efficiency."
   The product was identified for 15(S)-HpEPE ("For 12-HETE, 15-HEPE, and 17-HDHA, only one specific peak was
   detectable"), not for 5(S)-HpEPE. No eicosatrienoate hydroperoxide was tested.
2. **UniProt P07203 (GPX1, entry version 251) and P36969 (GPX4, entry version 236)**, flat files read 24 November
   2026: RHEA:76707 (15(S)-HpEPE) and RHEA:76699 (5(S)-HpEPE), each "PhysiologicalDirection=left-to-right",
   "Evidence={ECO:0000269|PubMed:36608588}". They cite Schwarz 2023 alone, so **UniProt and Rhea are a curated
   reading of source 1, not a second source**, and the rows say so.
3. **Archambault et al. 2018**, PLoS One 13:e0202424, PMID 30118527, [doi:10.1371/journal.pone.0202424](https://doi.org/10.1371/journal.pone.0202424),
   another laboratory, full text PMC6097673 read on Europe PMC (CC BY 4.0, read in the article's licence
   element): human neutrophils and eosinophils given the fatty acids make "13-HODE, 15-HETrE, 15-HETE, 15-HEPE,
   14-HDHA/17-HDHA". The text does not discuss the hydroperoxide or its reductant.
4. **Powell, Gravel and Gravelle 1995**, J Lipid Res 36:2590-2598, PMID 8847485, abstract only (Europe PMC record;
   no PMC full text): human neutrophils given EPA form 5-HEPE and 5-oxo-EPE; "5-oxo-EPE is readily formed from EPA
   via 5-HEPE".
5. **Iversen et al. 1991**, Agents Actions 33:286, PMID 1659156, [doi:10.1007/BF01986575](https://doi.org/10.1007/BF01986575),
   abstract only: human neutrophils form 15-HETrE from dihomo-gamma-linolenic acid.
(Citations 1, 3, 4 and 5 are according to PubMed and Europe PMC.)

**How strong each row is, stated plainly.**
- **MAR02559**: strongest. The exact substrate was measured and the product identified (source 1); an independent
  laboratory shows 15-HEPE is what cells make from EPA (source 3). The enzyme assignment rests on source 1 alone.
  Upstream's develop branch made the same rewrite but graded it "moderate: Rhea of an analogue substrate", which
  misreads RHEA:76707: it is this substrate.
- **MAR02545**: the exact substrate was measured by NADPH consumption, the product not identified by mass
  spectrometry; the direction rests independently on source 4 (abstract only). **A discrepancy in source 1 is
  recorded in the row**: its Table 1 gives the 5(S)-HpEPE row the full name of the 15(S) compound; the abbreviation,
  the catalogue number and the running text all say 5S. Upstream has not rewritten this one.
- **MAR01389**: weakest. The direction and product rest on two laboratories (sources 3 and 5); the glutathione
  peroxidases rest on the class reaction (RHEA:19057) and on the tetraenoate and dienoate neighbours, as the
  accepted 15(R)-HEPE rows rest on the 15(S) analogue. If the owner holds a row to a measurement on its own
  substrate, this one fails that and should wait.

**The gene rule is a choice the sources do not settle**, and the rows record it: (a) GPX1 or GPX4, the two enzymes
measured reducing these substrates (proposed, as closest to what was measured); (b) with GPX2, measured "very low"
on them, though the paper also says "all of them could be reduced to a certain extent by any of the three GPX
enzymes"; (c) the nine-gene rule of MAR00960 and MAR00988 (GPX1 to GPX8 and PRDX6), which the accepted rows
MAR02560 and MAR02571 carry and upstream uses, six of whose genes have no measurement on these substrates in
anything read here. A ruling here is not precedent for MAR02560 and MAR02571, but (a) or (b) would leave those two
with a different rule from their twins, which the owner may want to read together. The enzyme rows rest on one
source; the second sources tried are named in the row (one PubMed search that returned nothing; Sutherland et al.
2001, PMID 11115402, which UniProt cites for the class reaction in platelets, was not read).

**What these rows change in the graph**: for each reaction, the substrate and product edges swap ends, the
reaction becomes one-way, and two (or three, or nine) catalysis edges are added; GSH, GSSG, water and the proton
are currency and send nothing. No node id changes. It is still a new graph version, as every correction is.

**Leads met on the way, not proposed** (no source read): MAR03119 (melatonin "tryptase", section 7); MAR03898
"palmitoyl-CoA hydrolase (15(S)-HPETE)", 15(S)-HPETE <=> 15(S)-HEPE + H2O, which turns an arachidonate
hydroperoxide into an EPA hydroxy acid and is on no upstream list read here; MAR02567 and MAR02577, still as the
owner flagged them; the 15 reactions of #1164; MAR00716 and MAR00753.

## 9. Step 6: rows, or a move of the pin to 2.1.1

This is the owner's decision. What the pass found that bears on it:

- **Scale.** Adopting 2.1.1's changes as rows would mean rulings on about 460 reactions and 431 metabolites, most
  resting on upstream's reading and not on sources this project has read. The table's own standard (two sources
  read per row) cannot be met for that many by correction rows in any reasonable time. A pin move adopts all of them
  at once on upstream's authority, which is the opposite of "decided one by one"; it is simpler, and it is a
  different kind of act.
- **A pin move does not retire the table.** Of the 82 rows, upstream 2.1.1 agrees with about a third (some 27, which would be
  dropped) and still differs on the rest (section 6), and every row's `pinned_value` guard would raise until the
  table is re-anchored: MAM03652c and MAM20077m no longer exist under those ids, MAM20076n is MAM20076c, the gene
  rules of MAR20096 and MAR20097 are four genes, MAM03787's row is gone. The guard doing this is by design.
- **A pin move changes node ids at scale**: 134 species rows leave (96 base metabolites merged or deprecated), 48
  arrive, 155 reactions leave, 26 arrive, 27 genes arrive and 5 leave. Everything keyed on those ids (curated
  tables, laboratory-label mappings, registered counts, the guard tests' expected counts) would need checking; that
  was not scoped here.
- **2.1.1 contains changes this project may not want**, or would want to check against its own layers first: the
  Ca2+ ATPase split and ER/Golgi release (#1116) and the channel genes on MAR11311 (#1033) overlap the Reactome
  layer and the neuronal ion pools; the vesicular secretion reactions were removed and rewritten (#1105); and it
  keeps what the owner already ruled against (NAAA in the cytosol).
- **2.1.1 is already behind upstream.** Twenty-six open issues are fixed on `develop` and unreleased, including the
  whole of #1173. A pin moved to 2.1.1 now would face the same question at the next release; the three reactions of
  section 8, for example, are fixed on `develop` for two and in no branch for the third.
- **The open issues are open on any pin.** #1185's 87 reactions, #1164's 15 and #1119's generic ceramidases are
  identical in 2.0.1 and 2.1.1, so they need rows (or waiting for upstream) whichever pin is chosen. Item 21 said
  this, and the files confirm it.

A middle course exists and is named only as an option: keep the pin, and take from 2.1.x (or from `develop`) only
the changes that touch nodes on a route to a labelled node, once a graph exists to say which those are. That count
needs the rebuild.

## 10. What could not be checked

- Nothing was measured on a graph: `data/processed` is absent. "In the pinned model as the project reads it" means
  the pinned files and the reading code. Which changed reactions are in `graph_full_neuronal`, or on a route to a
  labelled node, is not known.
- The degree rule of the currency tag was approximated from the pinned model's reaction counts.
- Of the roughly 460 reactions and 431 metabolites that need a ruling, sources were read for three reactions only.
  The rest are listed with upstream's stated reason and nothing more.
- Issue comments were not read (the search API returns issue bodies); #1085's comments and #1109, where PR #1104
  places its evidence, are unread. Of #1173's cited papers none was read except through the three rows of section 8.
- Powell 1995 and Iversen 1991 were read as abstracts only. Schwarz 2023's supplementary figures (S3, S4) were not
  read; the discrepancy in its Table 1 was not checked against the supplier's catalogue.
- The 17 ChEBI replacements of ruling Q3 were not traced to where the project holds them.
- The 2.1.1 to `develop` difference was read from commit subjects only; no structural diff of `develop` was made.
- The upstream clone at /home/user/sysbiochalmers/human-gem was deepened by two bounded fetches (main at depth 1000,
  develop at depth 300); its checkout and tags are as they were. The project repository's working tree is clean.
- No licence question arose: nothing new is proposed for ingestion. Human-GEM's own licence was not re-read.
