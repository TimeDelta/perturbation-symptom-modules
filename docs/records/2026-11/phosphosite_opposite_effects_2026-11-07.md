# Item 4 of docs/exploration_queue.md: the site-level count that decides it (7 November 2026)

Research pass on Fable 5.1, 7 November 2026. Nothing in the repository was edited. Graph: v5
(`data/processed/graph_full_neuronal_split_binders_drugs_v5`), perturbations `data/processed/evidence_full_v5`,
both as on `main` today. Every page below was read with `experiments/read_public_page.py`; the saved pages, the
downloaded data and the counting script were kept in the session's scratchpad (`pages_signor/`, `signor_release/`,
`pages_omnipath/`, `omnipath_enzsub/`, `pages_psp/`, `pages_iptmnet/`, `iptmnet_readme/`, `pages_europepmc/`,
`scripts/count_signor_sites.py`, `signor_counts.json`). No third-party data went into the repository, and the
counting script was not committed, so the count is reproducible from the procedure in section 2, not from a script
in the repository.

Committed as a record on 7 November 2026. Whether item 4 is dropped is the owner's; nothing in the graph or the
sign-override table is changed by it.

## 1. Sources and licences

| Source | What it holds | Licence, verified by quotation | Usable for the count? |
|---|---|---|---|
| **SIGNOR 4.0**, October 2026 release, `signor.uniroma2.it/releases/Oct2026_release.txt` (21,425,930 bytes, SHA-256 `63db6f65e9148e81354f564c3c3cdfc9ee45dc421553bd0926e5fae511ef9d06`, fetched 7 November 2026 01:04 UTC) | per causal relation: `EFFECT`, `MECHANISM`, `RESIDUE`, `PMID`, `DIRECT`, `SENTENCE`; 43,727 rows, 33,494 human | **CC BY 4.0**: "SIGNOR 4.0 is licensed under Creative Commons Attribution 4.0 International" (`signor.uniroma2.it/documentation` and `signor.uniroma2.it/about`, both read 7 November 2026; the same sentence the 12 October 2026 reading of `docs/data_sources.md` row 83 quotes). The release file is linked from the public downloads page with no login; the robots file allowed it. The site asks to be cited as Lo Surdo et al. 2026 (`/about`, "Citing SIGNOR") | **Yes**: the one source found that states, per residue, which kinase and which effect |
| **OmniPath `enzsub`**, `omnipathdb.org/enzsub?genesymbols=1&fields=sources,references,curation_effort&organisms=9606&format=tsv` (5,058,512 bytes, SHA-256 `fffa905bcdffc92ab694c5664e84eb3eb5a96918e105547c15ae1ae90979453b`, 7 November 2026) | 41,505 enzyme-substrate-site rows (39,037 phosphorylation; 20,165 kinase-substrate pairs, 7,813 with two or more sites); columns `enzyme, substrate, residue_type, residue_offset, modification, sources, references, curation_effort` | Per resource, as OmniPath's own `resources` listing states them (read 7 November 2026): SIGNOR, ProtMapper, REACH, RLIMS-P, Sparser "CC BY 4.0"; Reactome "CC0 1.0"; dbPTM and BEL-Large-Corpus "NAR Open Access"; MIMP "LGPLv3"; NCI-PID "BSD"; **PhosphoSite (three variants) "CC BY-NC-SA 3.0"**, DEPOD "CC BY-NC 4.0", Li2012 "CC BY-NC 3.0", HPRD "HPRD", phosphoELM "ELM Software License Agreement", KEA "Unspecified NC-SA", PhosphoNetworks "PhosphoNetworks" (all `purpose: academic` or `non_profit`). The service's `license` argument (`academic;commercial;...`) filters by these | **No, by content, not licence**: the table carries sites and the modification type but **no effect field**; the sign in OmniPath is per interaction (the `interactions` query), never per site, so opposite effects at different sites cannot be read from it. 60 of SIGNOR's 76 opposite-effect pairs are in it as site rows without a sign |
| **PhosphoSitePlus** Regulatory_sites | per site: `ON_FUNCTION` ("enzymatic activity, induced" / ", inhibited"), per Hornbeck et al. 2015: "6368 sites control 8 different molecular functions including [...] 1178 that induce enzymatic activity, [...] and 399 that inhibit enzymatic activity" (full text, PMC4383998) | **Not read on the provider's site**: `www.phosphosite.org/homeAction` and `/staticSiteLicense` answered with a sign-in form ("Sign in With other accounts Sign in with Google Or With existing account Username Password"), and `/staticDownloads` is a 1,946-byte JavaScript shell with no readable content. **A login is a refusal** (CLAUDE.md), recorded and not worked around. Second route: OmniPath's resources listing states PhosphoSite as "CC BY-NC-SA 3.0", "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 International", purpose "academic" (read 7 November 2026). The paper's full text in PMC carries no licence sentence | **No**: not obtainable under the rules; licence known only at second hand |
| **iPTMnet** 6.2, `research.bioinformatics.udel.edu/iptmnet` | `ptm.txt`: `ptm_type, source, substrate_UniProtAC, substrate_genename, organism, site, enzyme_UniProtAC, enzyme_genename, note, pmid` (README read 7 November 2026) | **Contradictory, so unverified**: the licence page says "the iPTMnet database is protected under the CC BY-NC-SA 4.0 (Attribution-NonCommercial-ShareAlike 4.0 International) license" and the download page "This download is provided according to the terms of the CC BY-NC-SA 4.0 [...] license" (both `/iptmnet/license`, `/iptmnet/download`, read 7 November 2026); the README of the same files ends "We have chosen to apply the Creative Commons Attribution (CC BY 4.0) License (https://creativecommons.org/licenses/by/4.0/) to file downloads of the iPTMnet database." after opening with the CC BY-NC-SA 4.0 text. The directory `/iptmnet_data/` itself answers 403 | **No, by content**: no effect field at all, only enzyme, substrate, site and source |

So one source answers the question, SIGNOR, and its licence permits the count. The count below is on SIGNOR alone.

**What SIGNOR's `EFFECT` means.** Lo Surdo et al. 2026: "each interaction in SIGNOR is annotated with the presented
molecular mechanism and with the resulting effect (up- or down-regulation) on the target entity. Moreover, whenever
possible SIGNOR curators also capture the modified residue (e.g. Ser123) within the target sequence"; "76% and 49%
of the phosphorylation and dephosphorylation reactions, respectively, are annotated at the amino acid position
level" (full text, PMC12807704). In the October 2026 file the `EFFECT` values on human protein-to-protein
phosphorylation rows are: `up-regulates` 2,560, `up-regulates activity` 2,547, `down-regulates` 1,551,
`down-regulates activity` 1,283, `down-regulates quantity by destabilization` 439, `unknown` 428, `up-regulates
quantity by stabilization` 211, `down-regulates quantity` 87, `up-regulates quantity` 85, `down-regulates quantity
by repression` 1. The count reads every `up-regulates*` as activating and every `down-regulates*` as inhibiting,
which is what the graph's `activates`/`inhibits` collapse to; a quantity effect (stabilisation, destabilisation) is
kept in that reading because the graph does not separate activity from abundance either. `unknown` rows count as
neither. 7,812 of the 9,192 rows name a residue (85 percent, the paper's 76 percent being over all entity types);
1,380 do not.

## 2. The count on v5 (measured 7 November 2026, graph v5)

Procedure (`scripts/count_signor_sites.py`): human rows, `TYPEA` and `TYPEB` both `protein` (dropping 777
protein-family, 567 complex and 22 fusion-protein kinases, and 239 family, 115 complex and 9 other substrates),
`MECHANISM` = `phosphorylation`; per (kinase accession, substrate accession) the set of residues annotated
up-regulating and the set annotated down-regulating. A SIGNOR accession is mapped to a v5 `PROTEIN:` node by
`nodes.uniprot_entry`, then by gene symbol; a pair "is on v5" when v5 holds an `activates` or `inhibits` edge from
that kinase node to that substrate node (84,866 such protein-to-protein edges, 84,514 distinct pairs, all but 1,221
of them from OmniPath). Perturbed genes are the 2,566 `GENE:` nodes in `evidence_reports.perturbation_nodes`,
mapped to their protein through `gene_to_protein.parquet` (all 2,566 map); drug targets are the 166 proteins in
`drug_entry_nodes.target_node_id`.

| Count | SIGNOR pairs | On a v5 kinase-to-substrate `activates`/`inhibits` edge | Of those, touching a perturbed gene or drug target |
|---|---|---|---|
| Kinase-substrate pairs with a phosphorylation row | 5,514 | | |
| **At least one up-regulating residue and at least one down-regulating residue** (the item's test) | **76** | **34** | **28** |
| of which opposite effects at distinct residues | 61 | 27 | 22 |
| of which one residue annotated both ways (a curation conflict, e.g. CDK1 to VHL Ser80, CDK5 to PLD2 Ser134) | 15 | 7 | 6 |
| Loose: any up row and any down row, residue named or not | 93 | 42 | 33 |

The 34 edges are 0.04 percent of v5's 84,866 protein-to-protein signalling edges and involve 22 kinases. On 28 of
them one end is a perturbed gene (13 kinases, 21 substrates); on 2 the substrate is a drug target (SCN5A, 26
sodium-channel drugs; TP53 as a target of the `HTT|CAG_repeat_expansion` entry). Every one of the 34 kinases lies
within two directed hops of a perturbation seed, but so do most protein nodes (28,011 of 49,834 nodes are within
three hops of a seed), so that figure does not discriminate. **"Paths to labelled symptoms" cannot be counted as
written**: v5 has no symptom nodes; a symptom is a label on a perturbation, so the paths in question are the paths
from the 2,566 perturbed genes and 230 drug nodes, which is what the touch count and the hop count measure.

How the stored v5 sign relates to SIGNOR's sites, over the 34: the sign agrees with the majority of SIGNOR's
rows for 18, disagrees for 6, SIGNOR's rows tie for 9, and v5 already holds both signs for 1 (AURKB to KIF2C).

The 34 edges (v5 sign; SIGNOR up-regulating sites | down-regulating sites; flags: K/S-pert = kinase/substrate is a
perturbed gene, S-drug = substrate is a drug target):

| Kinase | Substrate | v5 | Up sites | Down sites | Flags |
|---|---|---|---|---|---|
| ABL1 | PSMA7 | inhibits | Tyr106 | Tyr153 | K-pert |
| ABL1 | RAD51 | activates | Tyr315 (+1 row without residue) | Tyr54 | K-pert S-pert |
| AURKA | TP53 | inhibits | Ser106, Ser315 | Ser215 | S-pert S-drug |
| AURKB | H3C11 | inhibits | Ser11 | Ser29 | |
| AURKB | KIF2C | activates and inhibits | Ser95 | Ser111, Ser192 | |
| CAMK2D | SCN5A | activates | Ser516, Ser571, Thr594 | Ser516, Thr594 | S-pert S-drug (26 drugs) |
| CDK1 | CDC25C | activates | Ser122, Ser214, Thr130, Thr48, Thr67 | Ser168 | |
| CDK1 | RUNX1 | activates | Ser21, Ser249, Ser266, Ser276, Ser397, Thr273 | Ser276 | S-pert |
| CDK1 | VHL | inhibits | Ser80 | Ser80 | S-pert |
| CDK2 | CDC6 | inhibits | Ser106 | Ser54, Ser74 | S-pert |
| CDK2 | RUNX1 | inhibits | Ser249, Ser266, Ser276, Thr273 | Ser276 | S-pert |
| CDK5 | PLD2 | activates | Ser134 | Ser134 | |
| CHEK2 | ELAVL1 | activates | Ser100 | Ser88, Thr118 | K-pert |
| CHUK | CYLD | inhibits | Ser422, Ser441 | Ser418, Ser432, Ser436, Ser439, Ser444 | S-pert |
| CSNK2A1 | ATF1 | inhibits | Ser63 | Ser36, Ser38, Ser41, Ser44 | K-pert |
| CSNK2A1 | SNCA | activates | Ser87 | Ser129 | K-pert S-pert |
| CSNK2A1 | TOP2A | activates | Ser1525 | Ser1365 | K-pert |
| EIF2AK1 | EIF2S1 | inhibits | Ser49 | Ser52 (+1 without residue) | K-pert |
| IKBKB | CYLD | inhibits | Ser422, Ser441 | Ser418, Ser432, Ser436, Ser439, Ser444 | S-pert |
| MAPK1 | ERF | activates | Ser161, Ser246, Ser251 | Thr526 | K-pert S-pert |
| MAPK1 | RUNX1 | activates | Ser249, Ser266, Ser276, Thr273 | Ser249, Ser266, Ser276, Thr273 | K-pert S-pert |
| MAPK8 | BCL2 | inhibits | Ser70 | Ser87, Thr69 (+1 without residue) | S-pert |
| MAPK8 | BCL2L11 | activates | Thr116 (+2 without residue) | Ser69 (+1 without residue) | |
| PLK1 | KIF2C | activates | Ser632, Ser633, Ser715 (+1 without residue) | Ser621 | |
| PRKACA | CFTR | activates | Ser660, Ser795, Ser813 | Ser737, Ser768 | K-pert S-pert |
| PRKACA | ESR1 | activates | Ser305 | Ser236 | K-pert |
| PRKACA | MAP2 | activates | Ser1782 | Ser1679, Ser1710, Ser1742 | K-pert |
| PRKACA | NF2 | inhibits | Ser10 | Ser518 | K-pert S-pert |
| PRKCA | RAF1 | activates | Ser497, Ser619 | Ser43 | S-pert |
| PRKCD | TNNI3 | inhibits | Ser23, Ser24 | Thr143 | S-pert |
| PTK2 | ACTN4 | activates | Tyr265 | Tyr31, Tyr4 | S-pert |
| RPS6KA5 | H3-3A | inhibits | Ser11 | Ser11, Ser29 | S-pert |
| SGK1 | NEDD4L | inhibits | Ser342 | Ser448 (+1 without residue) | S-pert |
| SRC | CTNNB1 | activates | Tyr333, Tyr654 | Tyr86 | S-pert |

The 8 edges in the loose count and not above (an opposite effect stated only in a row with no residue): MAPK3 to
SMAD2, TBK1 to SIKE1, GSK3B to MITF, CDK5 to LMTK2, MAPK1 to PDE4D, MAPK1 to SMAD2, PLK1 to STK3, SRC to TIAM1.
The 42 opposite-effect pairs not on any v5 `activates`/`inhibits` edge include 14 autophosphorylations (LRRK2,
ERBB2, STK11, FGFR3, SRC, JAK2, TTK, NEK2, PRKDC, CSF1R, HCK, JAK3, TGFBR2, CAMK2A), which the graph has no self-edge
for, and pairs such as CSNK1A1 to SNCA and ROCK1 to KCNK3 that v5 holds as `binds` or not at all.

**Limits of the count.** SIGNOR covers 38 percent of the proteome ("only 38% of the human proteome (7820
proteins) is now integrated in the SIGNOR network", Lo Surdo et al. 2026) and, on the 12 October 2026 reading,
11.0 percent of the graph's `activates` and 22.2 percent of its `inhibits` edges (`docs/label_source_review.md`
16.3; the confirmatory graph of that date, not v5). PhosphoSitePlus's regulatory sites, the larger annotation,
could not be read. So 34 is a count of what is annotated in the one open source, a floor on the phenomenon and not
an estimate of it; and most phosphosites have no annotated function at all (Needham et al. 2019, already in the
item). Family and complex kinases (PKA, PKC, CK2 as families; 1,344 rows) are outside the count because the graph
has no family nodes to match them to.

## 3. Verdict, by item 4's own test

**Drop the representation question.** The item's test is "If the count is small, drop this item", and the count
is 34 edges of 84,866, 28 touching a perturbation, in a graph where a kinase and a phosphatase on one substrate are
already two signed edges. Nothing in the 34 needs a site node or a phosphorylation relation: each is a sign
question on an existing edge, which is the item's own "entry point: edge sign". What the count does leave is
small and concrete: 16 of the 34 edges have a stored sign that SIGNOR's site rows contradict (6), tie on (9) or
split (1), and 14 of those 16 touch a perturbed gene. Those are candidates for the sign-evidence route the item
names (an edge prior or a row in `configs/curated_edge_sign_overrides.csv`, each read at the paper), under the
owner's standing rule that a related decision is taken on its own case; they do not need the item kept open. The
basis of the verdict is the measurement above, on v5, on 7 November 2026, from SIGNOR's October 2026 release; it
would change only if PhosphoSitePlus became readable under the rules and its 1,178 inducing and 399 inhibiting
sites (2014 figures) put many more kinase-substrate pairs in both classes on v5. Whether to drop is the owner's.

## 4. Dated addition for item 4 of docs/exploration_queue.md (1,484 characters, 7 November 2026)

**The decisive count, measured 7 November 2026 on v5 (Fable).** SIGNOR 4.0, October 2026 release (CC BY 4.0,
"SIGNOR 4.0 is licensed under Creative Commons Attribution 4.0 International", signor.uniroma2.it/documentation,
read that day), is the one open source that states per residue which kinase and which effect: of its 5,514 human
kinase-substrate phosphorylation pairs, 76 carry at least one up-regulating and one down-regulating residue (61 at
distinct residues, 15 with one residue annotated both ways). **34 of the 76 are v5 `activates`/`inhibits` edges**
(0.04 percent of 84,866 protein-to-protein signalling edges, 22 kinases); **28 touch a perturbed gene or drug
target** (SCN5A, TP53). v5 has no symptom nodes, so "paths to labelled symptoms" was read as paths from
perturbed genes. The stored sign agrees with SIGNOR's site majority on 18, disagrees on 6, ties on 9, and v5 holds
both signs for 1. OmniPath's `enzsub` carries sites with no effect field; PhosphoSitePlus answered with a sign-in
form (a refusal); iPTMnet's files carry no effect field and its licence pages contradict each other (CC BY-NC-SA
4.0 on the site, CC BY 4.0 at the foot of the README). **By the item's own test the count is small: the
representation question is dropped, pending the owner's word.** The 16 edges whose sign SIGNOR disputes are a
sign-evidence candidate for the override table, not a reason to keep the item. Record:
`docs/phosphosite_opposite_effects_2026-11-07.md`; source `losurdo2026signor`.

## 5. BibTeX (keys checked against docs/references.bib: neither exists; `licata2020signor` holds SIGNOR 2.0)

Both read from the PubMed record (PubMed MCP `get_article_metadata`, 7 November 2026) and confirmed against Europe
PMC (`ebi.ac.uk/europepmc/webservices/rest/search`, read with `experiments/read_public_page.py` the same day).

```bibtex
@article{losurdo2026signor,
  author  = {Lo Surdo, Prisca and Iannuccelli, Marta and Karis, Klas and Meo, Eleonora and Omidi, Parnian and Tosoni, Marta and Graziosi, Simone and Panni, Simona and Fiorillo, Maria Teresa and Licata, Luana and Sacco, Francesca and Gyori, Benjamin M. and Perfetto, Livia},
  title   = {{SIGNOR} 4.0: the 2025 update with focus on phosphorylation data},
  journal = {Nucleic Acids Research},
  year    = {2026},
  volume  = {54},
  number  = {D1},
  pages   = {D682--D690},
  doi     = {10.1093/nar/gkaf1237},
  pmid    = {41243950},
  note    = {The source of the site-level count that decides item 4 of docs/exploration\_queue.md (research pass of 7 November 2026, on Fable). Full text read through PubMed Central PMC12807704 on 7 November 2026. Quoted: "each interaction in SIGNOR is annotated with the presented molecular mechanism and with the resulting effect (up- or down-regulation) on the target entity. Moreover, whenever possible SIGNOR curators also capture the modified residue (e.g. Ser123) within the target sequence"; "76% and 49% of the phosphorylation and dephosphorylation reactions, respectively, are annotated at the amino acid position level"; "only 38% of the human proteome (7820 proteins) is now integrated in the SIGNOR network". The paper SIGNOR's own about page asks to be cited for release 4.0. Europe PMC gives firstPublicationDate 2026-01-01 and the PubMed record 6 January 2026 in volume 54, issue D1, so the year is 2026; the site's own citation line reads "2025 Nov 17 [...] Epub ahead of print". Open access; Europe PMC isOpenAccess Y}
}

@article{hornbeck2015phosphositeplus,
  author  = {Hornbeck, Peter V. and Zhang, Bin and Murray, Beth and Kornhauser, Jon M. and Latham, Vaughan and Skrzypek, Elzbieta},
  title   = {{PhosphoSitePlus}, 2014: mutations, {PTMs} and recalibrations},
  journal = {Nucleic Acids Research},
  year    = {2015},
  volume  = {43},
  number  = {Database issue},
  pages   = {D512--D520},
  doi     = {10.1093/nar/gku1267},
  pmid    = {25514926},
  note    = {Cited in the item 4 pass of 7 November 2026 (on Fable) for what the PhosphoSitePlus Regulatory sites download holds, the dataset that could not be read because the provider's pages answer with a sign-in form. Full text read through PubMed Central PMC4383998 on 7 November 2026. Quoted: "The 'Regulatory Sites' dataset provides curated information mainly from LTP papers about 7211 sites on 2374 proteins that regulate downstream cellular processes, molecular functions and protein-protein interactions"; "6368 sites control 8 different molecular functions including 1788 that regulate intracellular localization, 1178 that induce enzymatic activity, 1045 that regulate protein stabilization or degradation and 399 that inhibit enzymatic activity". The full text carries no licence sentence; the licence (CC BY-NC-SA 3.0) is known to the project only from OmniPath's resources listing, read 7 November 2026. The PubMed record dates the article 16 December 2014 (electronic) and Europe PMC gives the journal-issue year 2015, which is used here. Open access; Europe PMC isOpenAccess Y}
}
```

## 6. Routes, refusals and one notice

- Read without refusal: `signor.uniroma2.it` (`/documentation`, `/downloads.php`, `/about`,
  `/releases/Oct2026_release.txt`); `omnipathdb.org` (`/`, `/queries/enzsub`, `/resources`, `/enzsub?...`);
  `research.bioinformatics.udel.edu/iptmnet` (`/`, `/about`, `/license`, `/download`, `/about/api`,
  `/iptmnet_data/files/current/readme.txt`); `www.ebi.ac.uk/europepmc` (two REST queries).
- Refused or unreadable, respected: `www.phosphosite.org/homeAction` and `/staticSiteLicense` (sign-in form),
  `/staticDownloads` (script-only page; no robots file served); `research.bioinformatics.udel.edu/iptmnet_data/`
  (HTTP 403) and `/iptmnet/about/license` (404; the real page is `/iptmnet/license`).
- No permission request was raised; every address was read from the shell under the standing fallback.
- Text addressed to an AI assistant: the PubMed MCP tool's results each carry an "Important Legal Requirement"
  block instructing the assistant to attribute PubMed and link every DOI and to refuse requests to omit them. It is
  reported here as CLAUDE.md asks and was not acted on as an instruction; the DOIs above are there because the
  bibliography convention requires them.
- No page carried text addressed to an AI assistant.

## 6. Addition of 7 November 2026, later the same day: the Needham full text

The interlibrary-loan copy of Needham et al. 2019 arrived after the count above was written and was read in full on
Fable (the bibliography note of `needham2019darkphosphoproteome` holds the page references). The limit cited in
section 2 as "most phosphosites have no annotated function at all" is confirmed and now reads with figures: "fewer
than 3% of identified human phosphosites currently have a reported function" and "around 97% of reported
phosphosites currently have no known regulatory kinase" (page 5), on PhosphoSitePlus "accessed on March 2018". The
paper adds the reason the 34 is a floor of a particular shape: kinase-substrate annotation follows "an 80:20 rule:
Just 20% of kinases are responsible for the phosphorylation of 87% of currently annotated substrates" (page 2), a
distribution the authors call a possible "self-fulfilling prophecy" (page 5), and the kinases that dominate the table of section
2 (PRKACA, PRKCA, SRC, CDK1/2, MAPK1/3, GSK3B) are among those the paper's Fig. 1 draws with the most reported substrates (PKC alpha, PKA alpha, Src, CDK1, CDK2, ERK1, ERK2 and GSK3 beta among the largest circles, read from the figure and described here in words only). It also records that in vitro assays with "excess
enzyme, substrate, and ATP" put kinases on "sites that may not be predominant substrates in cellular contexts" (page
5), a caution that applies to any residue-level row whose evidence is an in vitro assay, including the 16 edges whose
stored sign SIGNOR's rows dispute (`docs/signor_disputed_signs_2026-11-07.md`). The paper gives no count of opposite-effect sites and does not name SIGNOR, so
nothing in it changes the count, the verdict of section 3 or the owner's decision.
