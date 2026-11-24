# Literature bias in the curated sources, and ways to correct it (item 15 of docs/exploration_queue.md)

**Run on Opus at the owner's request; needs verification on Fable before it is relied on.** This is a waived pass
(CLAUDE.md "Models": research is done on Fable; the owner asked on 20 November 2026 for this pass to run on Opus 5.5),
and is flagged as such wherever it is recorded.

Date: 20 November 2026. Progress log: literature_bias_2026-11-20.progress.md. Saved pages: literature_bias_pages/.
Bibliography draft: literature_bias_2026-11-20.bib. Every recommendation below is the pass's own reasoning, marked
"(pass's reasoning)", and decides nothing.

## 0. What was read, and how

- Project context: `docs/exploration_queue.md` item 15 and the priority order of 20 November 2026;
  `docs/item37_rulings_draft_2026-11-13.md` sections 14, 15, 17 (carrier share, ion state), 19 and 20; and three
  scratchpad reports of 18 and 19 November 2026 for the project's own measured cases.
- Literature: PubMed records (PubMed connector, E-utilities), Consensus semantic search (peer-reviewed filter on),
  Europe PMC full text for five open-access papers, and Crossref records for six classic statistics papers, the last
  three routes read with `experiments/read_public_page.py` and saved under `literature_bias_pages/` with SHA-256.
- **Read in full text**: Stoeger et al. 2018, Schaefer et al. 2015, Luck et al. 2020, Haynes et al. 2018 (Europe PMC).
  **Abstract only**: every other paper here, including Rolland et al. 2014, Santos et al. 2017 and Oprea et al. 2018,
  whose Europe PMC full text answered HTTP 500 twice (a server error, not a refusal). The second route, NCBI
  E-utilities `efetch`, was **refused by its robots file** (20 November 2026, 16:25 UTC); that refusal was respected
  and not routed through the PubMed connector's full-text tool. **Bibliographic record only** (Crossref): Rubin 1976,
  Little 1993, Heckman 1979, Tobin 1958, Rosenbaum and Rubin 1983, Shimodaira 2000. What those six are said to assume
  below is their standard content, stated from the pass's knowledge, not re-read; the Fable recheck should read them.
- Mestres et al. 2008 (Nat Biotechnol letter, no abstract) and Edwards et al. 2011 (Nature, no abstract) were found
  but not read, and nothing here rests on them.
- No preprint is cited. Every paper has a DOI or PMID in `literature_bias_2026-11-20.bib`.
- **Text addressed to an AI**: the PubMed connector's results carry an "important_legal_notice" telling the reader to
  attribute PubMed and link DOIs; Consensus results carry an "IMPORTANT INSTRUCTIONS" block on citation format. Both
  are tool output, not page text; they were not acted on beyond ordinary citation. No saved page held such text.

## 1. Methods for a value set from a non-random sourced subset (question 1)

The common frame is Rubin's (1976) taxonomy: a value missing **completely at random** (MCAR) leaves the sourced rows
a fair sample; **at random given covariates** (MAR) means the sourced and unsourced rows differ only through things
recorded for both, so conditioning on or reweighting by those things removes the bias; **not at random** (MNAR) means
whether a value is sourced depends on the value itself (a weak binder is not reported because it is weak), which no
amount of conditioning on observed covariates removes. The project's own measurement already points at MNAR for the
occupancy split: a pair is "often unsourced *because* the drug binds weakly there or acts in a way that has no
constant" (`fallback_class_definition_2026-11-18.md`). The methods below differ in which of these they handle.

### 1.1 Measure the selection first (the prerequisite of every method below)

- **What it is.** Model the probability that a row is sourced from covariates known for every row, and compare
  sourced with unsourced rows on them. Two papers show this works on exactly this kind of data. Stoeger et al. 2018
  predicted the number of publications per human gene out of sample from 430 gene features ("Spearman: 0.64"), the
  leading features being RNA and protein abundance across tissues. Pogodin et al. 2019 trained classifiers on ChEMBL
  (87,583 molecules, 919 targets) that "allowed prediction whether the compound had been tested against the
  particular molecular target, despite whether it was active or not", and concluded that "the selection of chemical
  compounds for testing against specific targets is biased".
- **Assumes.** Nothing by itself; it is a diagnostic. It cannot detect MNAR, because the missing values are by
  definition unseen.
- **Needs.** Covariates for both sourced and unsourced rows.
- **Does the project have it.** Yes, largely (pass's reading of the build's tables): target family and mode
  (GtoPdb 2026.3.1 and the ChEMBL_37 eight-value mode rule), brain expression (GTEx, Siletti), drug approval year and
  ATC code, ion state and pKa for the carrier rows, and publication counts per gene, which NCBI's gene-to-PubMed table
  would supply (not checked for presence in the build; its licence is unverified here).

### 1.2 Missing-not-at-random sensitivity analysis (delta adjustment, pattern mixture, tipping point)

- **What it is.** Impute or set the unsourced values under MAR, then shift them by an offset delta and report how far
  the result moves as delta grows. Little 1993 gives the pattern-mixture formulation; Cro et al. 2020 (Stat Med, a
  tutorial): "In δ-based imputation, an offset term, δ, is typically added to the expected value of the missing data to
  assess the impact of unobserved participants having a worse or better response than those observed". Leacy et al.
  2017 vary delta by an auxiliary variable (the same departure for all, or one depending on a recorded covariate); a
  "tipping point" is the delta at which a conclusion changes. Hayati Rezvan et al. 2018 elicited delta from experts and
  pooled the elicitations.
- **Assumes.** Nothing about the true mechanism: it is honest about not knowing it. Copas and Shi 2000, on
  publication bias: "Correcting for this bias is not possible without making untestable assumptions", so a sensitivity
  analysis is offered instead of a correction.
- **Needs.** A defensible range for delta and its sign. Here the sign is known for one case (sourced affinities are
  biased toward tight binding), and the size can be anchored on the project's own measured gaps (amisulpride's own
  5-HT median pK 6.0 against the cross-drug 5-HT class median 8.6; acamprosate 3.5 against 4.9;
  `fallback_class_definition_2026-11-18.md`, measured on the 12 November 2026 build).
- **Does the project have it.** Yes: it needs no new data, only reruns of the measurement at a few delta values.
  **Pass's reasoning:** it is the cheapest method here and the only one that addresses MNAR directly; its output is a
  stated range, not a corrected value, which fits the closest-to-physiology rule because it changes no sourced value.

### 1.3 Selection models (Heckman type)

- **What it is.** Model jointly whether a value is observed and what it is, with correlated errors (Heckman 1979);
  the correction term is estimated from the selection equation. Koné et al. 2019 (BMC Med Res Methodol), in a
  simulation: "When missingness in the outcome data was related to unobserved determinants of the outcome, large and
  systematic biases were found for CCA and MICE, while Heckman-style selection models yielded unbiased estimates".
- **Assumes.** A joint distribution for the two errors (bivariate normal in the classic form; Marchenko and Genton
  2012 show the sensitivity to that and offer a t version) and an **exclusion restriction**: a variable that moves
  whether a value is sourced but not the value itself. Gomes et al. 2020 (Stat Med): the model "requires the study to
  make correct assumptions, both about the joint distribution of the missingness and outcome and that there is a valid
  exclusion restriction"; they found full-likelihood selection models less sensitive to it. Puhani 2000: without a
  good exclusion variable the two-step estimator suffers from collinearity, and simpler estimators are more robust.
- **Needs.** Tens to hundreds of rows per fitted class and a credible exclusion variable.
- **Does the project have it.** **Pass's reasoning: no, not credibly.** The candidates (approval year, publication
  count of the drug or target, whether the drug's original regulatory review is posted) plausibly bear on the value
  too: older drugs were screened against fewer targets and with older assays, and well-studied targets are the
  potent-ligand targets. The classes that need a fallback most hold 4 allosteric and 8 channel-blocker measurements
  (`fallback_class_definition_2026-11-18.md`), far too few to identify a correlation between two error terms. A
  Heckman fit here would be identified by its normality assumption alone, which is the case Puhani warns about.

### 1.4 Inverse probability weighting, propensity scores and covariate-shift weighting

- **What it is.** Weight each sourced row by the inverse of its probability of being sourced (Seaman and White 2013,
  a review: IPW "is a commonly used method to correct this bias", with weight truncation, stabilisation and augmented
  IPW, and multiple imputation "generally being more efficient"); Rosenbaum and Rubin 1983 reduce the covariates to a
  single propensity score. The machine-learning form is covariate-shift adaptation: Shimodaira 2000 weights the
  log-likelihood by the density ratio of target to training inputs, and Sugiyama et al. 2008: "weighted variants
  according to the ratio of test and training input densities are consistent". Importance-weighted cross-validation
  (Sugiyama et al. 2006) is "still unbiased even under the covariate shift", which is the form that scores a fallback
  on rows that resemble the rows it will be applied to. Kouw et al. 2019 show its variance grows when large weights
  arise, the usual failure.
- **Assumes.** MAR given the covariates used, and **positivity**: every kind of unsourced row has sourced rows like it.
  It corrects nothing about MNAR.
- **Needs.** The covariates of 1.1 on every row, and enough sourced rows in every region the unsourced rows occupy.
- **Does the project have it.** The covariates, mostly yes. Positivity, **no** for the classes that matter most
  (pass's reading of the project's counts): 163 of the 206 unsourced occupancy pairs are allosteric or channel pairs,
  with no sourced channel-opener measurement at all; the zwitterion carrier class has two well-measured members; old
  drugs with unposted reviews have no carrier data. Where positivity fails, IPW has nothing to weight and reports an
  infinite weight, which is itself a useful diagnostic.

### 1.5 Censored-value likelihood (Tobit)

- **What it is.** Treat a value reported only as a bound ("Ki > 10 µM") as an interval, not as missing or as the bound
  itself (Tobin 1958). Svensson et al. 2025 adapt ensemble, Bayesian and Gaussian models to censored drug-discovery
  labels with the Tobit likelihood: "despite the partial information available in censored labels, they are essential
  to accurately and reliably model the real pharmaceutical setting".
- **Assumes.** The censoring threshold is known and the value's distribution is specified (normal in pK in the
  classic form).
- **Needs.** The censored rows with their qualifiers, which ChEMBL records (`standard_relation`).
- **Does the project have it.** Yes. The ChEMBL check of 19 November 2026 (ChEMBL_37) found "5,676 cells hold only
  censored values where an exact sibling value exists, transfer failures the script never sees, all on the failing
  side" (item 37 section 19). **Pass's reasoning:** this is the one MNAR mechanism whose form the data reveal (a value
  is absent because it is beyond the assay's range), so it is the one MNAR case that can be corrected rather than
  only bounded.

### 1.6 Study-bias corrections used in network biology

- **Matched nulls by study count.** Schaefer et al. 2015 showed "the degree of a protein is a function of the number
  of times it has been screened for interaction partners" and tested cancer proteins against random sets "replacing
  each cancer protein by a non-cancer protein that had been equally often tested as a bait"; the apparent excess
  degree of cancer proteins then left "no conclusive evidence". They also used degree divided by bait count "as a proxy
  for a bias normalized degree estimate".
- **Degree-preserving nulls.** Lazareva et al. 2021: most active-module methods "do not produce biologically more
  meaningful candidate disease modules on widely used PPI networks than on random networks with the same node degrees",
  so they "mainly learn from the node degrees". Gillis and Pavlidis 2012 found functional signal in gene networks
  "typically concentrated in only a very few interactions".
- **Bias-aware edge costs.** Sarkar et al. 2023 (ROBUST-Web) add "bias-aware edge costs ... which allow to correct for
  study bias in protein-protein interaction networks".
- **Systematic screens as the reference.** Luck et al. 2020 (HuRI): "While Lit-BM is highly biased towards the most
  studied genes, HuRI covers the genome-by-genome space more uniformly"; publication count and expression "strongly
  correlate with ... the number of interaction partners ('degree') in protein complex and literature-curated protein
  interaction networks but not in HuRI".
- **Assume / need / project.** All assume the bias runs through a recorded study count (bait use, publications) or
  through degree. They need per-protein study counts or a systematic screen covering the same space. The project
  (pass's reading) has degree on every node, would have publication counts from NCBI's table, and has systematic
  sources for some tables (HuRI-type screens for PPI, GTEx and Siletti for expression, ChEMBL deposited screens for
  binding), so the comparison "curated rows against the screen" that item 15 proposes is possible where a screen exists.

## 2. Measured evidence of the bias in the kinds of table the project uses (question 2)

### 2.1 Protein and gene study bias (literature)

| measure | number | source |
|---|---|---|
| share of 2015 literature on genes already reported by 1991 | genes reported by 1991, "16% of all genes", "account for 49% of the literature of the year 2015" | Stoeger et al. 2018 (full text) |
| concentration of NIH-funded exploratory work | "5% of the human protein-coding genes accounting for half of the publications" | Stoeger et al. 2018 |
| predictability of attention from gene properties | out-of-sample "Spearman: 0.64" from 430 features | Stoeger et al. 2018 |
| inequality of annotation resources (Gini) | GO 0.25 (2001) to 0.47 (2017); Reactome 0.33; CTD chemical-gene 0.63; DrugBank drug-gene 0.70; GeneRIF 0.79; pooled 0.63 | Haynes et al. 2018 (full text) |
| knowledge deficit across the proteome | "a substantial knowledge deficit for approximately one out of three proteins" | Oprea et al. 2018 (abstract) |
| drug targets of approved drugs | 667 human proteins for 1,578 FDA-approved drugs; "continued dominance of privileged target families" | Santos et al. 2017 (abstract) |
| literature-curated against systematic PPI | systematic map "~30% larger than" small-scale literature at equal quality, literature "highly biased and only covers a relatively small portion of the proteome" | Rolland et al. 2014 (abstract) |
| literature-curated degree tracks popularity | degree correlates with publication count and expression in literature-curated networks "but not in HuRI"; literature maps biased against tissue-preferentially expressed genes | Luck et al. 2020 (full text) |

Two of these bear directly on project tables. Reactome's Gini of 0.33 is the lowest of the resources Haynes measured
but not zero, and the project's edges draw on Reactome. HuRI's finding that literature-curated maps under-represent
tissue-preferentially expressed proteins matters for a brain model, whose distinctive proteins are tissue-specific
(pass's reasoning; not measured on the project's graph).

### 2.2 Binding-affinity and bioactivity coverage

| measure | number | source |
|---|---|---|
| share of records labelled active (pAct > 6) by database | ChEMBL 23.3% active, 43.5% inactive; BindingDB 52.7% active; IUPHAR/BPS (GtoPdb) 79.8% active, 5% inactive | Isigkeit et al. 2022 (full-text excerpt via Consensus) |
| why GtoPdb skews potent | "IUPHAR/BPS focusing on potent, expert-selected chemical tools contained the highest frequency of active labels" | Isigkeit et al. 2022 |
| whether a compound was tested is predictable | ChEMBL 87,583 molecules × 919 targets; tested-or-not predictable; target-activity ROC AUC "about 0.87 and 0.75" for predicted-tested against predicted-untested pairs | Pogodin et al. 2019 (abstract) |
| active fraction in screening deposits | PubChem assay results "2.8% identified as active and 91.4% as inactive"; literature skews "towards biologically active compounds" | An et al. 2025 (excerpt) |
| proprietary against public data | Bayer against ChEMBL: cross-source MCC −0.34 to 0.37; overlap measures "did not correlate with observed performances" | Smajić et al. 2025 (abstract) |
| noise floor for public Ki | independent public Ki of the same pair: "a mean error of 0.44 pK(i) units" | Kramer et al. 2012, as quoted in `fallback_class_definition_2026-11-18.md` |
| intralab assay variability | "approximately 0.3 log units (or a 2-fold difference in activity)" | Schiebroek et al. 2026 (excerpt) |

The contrast between screening deposits (PubChem, about 3% active) and literature curation (GtoPdb, about 80%
active) is the clearest single number for publication and curation bias in affinity tables. **Pass's reasoning:**
the class key ruled in item 37 section 14 is the GtoPdb family, but the values are ChEMBL_37 measurements, so the
skew that matters is ChEMBL's (about 23% active by the Isigkeit definition), not GtoPdb's; the GtoPdb figure matters
wherever a GtoPdb affinity is the source of a row.

### 2.3 Plasma protein binding

| measure | number | source |
|---|---|---|
| shape of the measured fu,p distribution | 2,738 values; "The strongly biased distribution of the fraction unbound in plasma was mitigated by a logarithmic transformation" | Watanabe et al. 2018 (abstract) |
| coverage outside drugs | "experimental plasma protein binding data are scarce for environmentally relevant chemicals"; pharmaceutical training set covered 82 to 99% of their chemical space; error lowest for "highly bound chemicals (MAE 0.07-0.12)" | Ingle et al. 2016 (abstract) |
| human IV PK set | 1,352 drugs, plasma binding "collected from other available sources to supplement" the PK data; date of first disclosure analysed for temporal trends | Lombardo et al. 2018 (abstract) |
| AAG binding | "hundreds of drugs with diverse structures bind to this glycoprotein" (a review, no coverage count) | Israili and Dayton 2001 (abstract) |

No paper found measures how AAG-specific (as against whole-plasma) binding data are distributed over drugs. That
gap is recorded, not filled: the second search route (Consensus after PubMed) found reviews only.

### 2.4 The project's own measured cases (scratchpad reports; numbers are with their build)

| table | number | where and on what |
|---|---|---|
| occupancy split, class median | amisulpride's unsourced 5-HT pairs would take pK 8.6; its own sourced 5-HT median is 6.0. 163 of 206 unsourced pairs are allosteric or channel pairs, against 4 + 8 sourced measurements | `fallback_class_definition_2026-11-18.md`, 12 November 2026 build |
| sibling transfer | 98.5% of ChEMBL sibling pairs come from one paper; across papers the error is about 0.25 log worse; 84.5% of molecule-subtype values rest on one measurement; 5,676 censored-only cells | item 37 section 19, ChEMBL_37 |
| TPM to nCPM fallback | genes outside Table S5 median TPM about 0.03 against 8 to 17; 48-63% within two-fold on all genes, 36-51% on those genes, 84% unscorable | item 15 table, `tpm_fallback_holdout_2026-11-18.md` |
| carrier shares | 28 of 35 numeric shares from McNamara and Meiman 2019 Table 3 (isolated proteins); one laboratory supplies 10 of its 28 drugs | item 15 table; item 37 section 17, C11 |

These are the observations item 15 lists; they are cited here as the project's evidence, not re-measured.

## 3. Each fallback type of item 37: the method that fits, its cost, and the limit to state (question 3)

All of this section is **the pass's reasoning**, built on sections 1 and 2; it recommends and decides nothing. Two
recommendations run through every row, so they are stated once:

- **R-a. Score every fallback by importance-weighted held-out error** (1.4): weight each held-out sourced row by how
  much it resembles the unsourced rows the fallback will be applied to (a propensity model on the covariates of 1.1),
  and report the weighted error beside the unweighted one. Cost: one logistic model per table and a reweighted rerun of
  the existing leave-one-out scripts. It meets item 15's own proposal ("Score every fallback on held-out rows that
  resemble the rows it will be applied to") with a method that has a consistency result behind it.
- **R-b. Report a delta sensitivity** (1.2) on every value the fallback sets: shift the fallback value toward the
  direction the selection is known to run, by amounts anchored on the project's own measured gaps, and report the
  delta at which a downstream result (an occupancy, a module membership) changes. Cost: reruns, no new data.

R-a corrects selection on what is recorded (MAR); R-b bounds selection on the value itself (MNAR). Neither replaces a
sourced value, so neither runs against the closest-to-physiology rule.

| fallback (item 37) | selection most likely at work | method that fits | cost here | limit to state if none is applied |
|---|---|---|---|---|
| **Class centre**: GtoPdb family × mode, back-off at k = 3, not below mode, not for receptor ligands (s.14, s.19) | MNAR toward tight binding: weak or constant-less pairs go unreported (amisulpride 8.6 against 6.0). Also study bias: well-studied families supply most measurements | R-a for the error; R-b one-sided (toward weaker binding) for the value; Tobit (1.5) for censored ChEMBL rows in the class, so a "> 10 µM" counts as weak instead of vanishing | Low for R-a and R-b. Tobit: moderate, a censored likelihood in the class-median step; the qualifiers are already in ChEMBL_37 | "The class centre is a median of sourced measurements, which are biased toward tight binding; its leave-one-out error is a floor for the unsourced pairs, not an estimate" (the project's own wording in `fallback_class_definition_2026-11-18.md` already says this) |
| **Sibling-subtype median**, muscarinic only (s.19) | Within-paper copying: 98.5% of sibling pairs from one paper, 84.5% single measurements; censored-only cells all on the failing side | Score across papers only (a paper-grouped held-out split), which the ChEMBL check already did for the inflation; add Tobit on the 5,676 censored cells to see whether the muscarinic margin survives them | Low: the harvest exists | "The muscarinic margin was measured within ChEMBL_37 with censored cells excluded; it is not tested on cells that hold only a bound" |
| **Shared offset** for unbounded pores (s.20, S2) | The sourced pores are the measurable ones; pores never characterised differ in ways the offset cannot see | The ruled identification condition (SE below the spread) is the right guard for noise. For selection, R-b on the offset: report the result at the offset ± its SE and ± the sourced spread | Low | "The offset is identified from sourced pores only and assumes the unsourced pores depart from their bounds as the sourced ones do (MAR given pore class)" |
| **Fixed value at the sourced siblings' median** (s.20, S2) | As above, with nothing left to identify | R-b only: a tipping-point delta; no weighting is possible because the branch exists where data are too thin | Very low | "The value is the sourced siblings' median and assumes the unsourced member resembles them; that assumption is untested" |
| **Carrier-share classes**: ion state at pH 7.40, soft membership, fraction-weighted class medians, k = 3, no zwitterion value (s.15, s.17) | One-study dominance (28 of 35 shares from Table 3; one laboratory 10 of 28), method bias (isolated proteins), and missing old drugs | Cluster weighting by study, which C11 already does for the beta-blockers (grouping by primary reference), applied to every class value; R-a with approval year and evidence class (isolated protein or whole plasma) as covariates; positivity check: report, per class, the share of fallback drugs with no sourced member of similar approval era or method | Low to moderate: needs approval year on carrier rows | "Class medians rest mostly on one paper's calculation from isolated proteins; drugs whose regulatory reviews are unposted, mostly older drugs, have no member of their kind in the sourced set" |
| **Table S5 term for bulk classes and the out-of-S5 constant** (s.15) | Ascertainment of the measurable: genes outside Table S5 are low-expressed (median TPM about 0.03) and 84% unscorable | R-a weighted by expression level (the scorable out-of-S5 genes reweighted toward the low-TPM ones); the 36-51% already measured on out-of-S5 genes is the honest figure, and the 48-63% on all genes should not be quoted for them | Low | "Accuracy on genes outside Table S5 is measured on the 16% that could be scored, which are the better-expressed ones; for the rest it is unmeasured" |
| **Circularity step**: fix the held-out split first, source from training only (s.20) | Not a fallback, but it decides what the scores of every row above mean | Keep as ruled. Add: draw the held-out split stratified on the covariates of 1.1 so that it contains rows like the unsourced ones (or record the propensity of each held-out row), so that R-a has rows to weight. A random split of sourced rows reproduces the sourced distribution, not the unsourced one | Low, if done before the split is fixed; impossible to add afterwards without breaking the rule's own guarantee | "Held-out error is measured on sourced rows and inherits their selection; it validates the fallback for sourceable rows only" |

**What no method here can fix** (pass's reasoning, agreeing with item 15's third limit): a class with no sourced
member (channel openers, the zwitterion class, the four complex-only genes) violates positivity. IPW cannot weight
it, a selection model cannot identify it, and delta sensitivity can only say how much would have to be wrong. For
these, the ruled answer, send to sourcing and give no value, is also what the missing-data literature implies.

**Which methods do not fit** (pass's reasoning): a Heckman-type model (1.3), for want of a credible exclusion
variable and of rows; and the meta-analytic publication-bias models (Copas and Shi 2000), which need several
estimates of the same quantity with their standard errors and so fit only the few pairs with many independent Ki
values, where the noise floor (0.44 pK) is already the larger concern.

## 4. Recommendation in brief, limits of this pass, and what the Fable recheck should do

**Recommendation (pass's reasoning; the owner decides).** In order of cost: (1) build the covariate table of 1.1 for
every curated table with a fallback and report sourced against unsourced rows on it; (2) stratify the held-out split
on those covariates before it is fixed (section 3, last row), since this cannot be added later; (3) report
importance-weighted held-out error beside the plain error (R-a); (4) report a one-sided delta sensitivity on every
fallback value (R-b); (5) use the censored ChEMBL values through a Tobit likelihood in the class and sibling
statistics. Selection models are not recommended. Each of (3) to (5) changes how a fallback is scored or bounded, not
a sourced value.

**Limits of this pass.**
- It ran on Opus at the owner's request and **needs verification on Fable before it is relied on**.
- Four papers were read in full; the rest at abstract level, and six classics at bibliographic level only.
- Rolland 2014, Santos 2017 and Oprea 2018 full texts could not be read (Europe PMC HTTP 500 twice; NCBI E-utilities
  refused by robots). Their numbers here are the abstracts' numbers.
- The search was two engines (PubMed, Consensus), not a systematic review; a method absent here may exist.
- The project-internal numbers are quoted from scratchpad reports, not re-measured, and carry their build
  (12 November 2026 build; ChEMBL_37), not the registered v5 graph.
- Whether the build holds per-gene publication counts, and the licence of NCBI's gene-to-PubMed table, were not
  checked.
- No licence was verified for any paper: nothing here reuses a paper's data, only short quotations.

**For the Fable recheck.** Re-read every quotation against its source (the saved Europe PMC copies are in
`literature_bias_pages/epmc/`); read Rubin 1976, Little 1993, Heckman 1979, Rosenbaum and Rubin 1983 and Shimodaira
2000 for the assumptions attributed to them; retry the three full texts that failed; and look for a measured survey
of AAG-specific binding coverage, which this pass did not find.

---

**Added 24 November 2026: verified on Fable, and corrected** (`docs/records/2026-11/item15_literature_bias_verification_2026-11-24.md`;
the owner approved every correction on 24 November 2026: "Item 15: yes to all"). This record is append-only, so its text
above stands as written on 20 November and the corrections are stated here. All 38 cited works exist, 33 of 34
quotations are verbatim in their sources, and every literature number is in its source. The project's own numbers taken
from the scratchpad reports of 18 November 2026 cannot be checked, those reports having been lost with the container on
23 November 2026; they are not relied on until re-measured.

- **C1, Tobit (section 1.5).** "so it is the one MNAR case that can be corrected rather than only bounded" is narrowed:
  censored-value handling can correct a class statistic for values recorded only as a bound, given known thresholds and
  an assumed distribution, but not for pairs never measured or deposited, nor the single cell that holds only a bound;
  the Tobit estimate is not robust to a wrong distribution; and a class median needs no likelihood while fewer than half
  its values are censored on one side. The count of 5,676 is the ChEMBL sibling harvest's of 19 November 2026
  (ChEMBL_37, binding Ki, the harvested receptor and transporter families; `docs/item37_rulings_draft_2026-11-13.md`
  section 19): molecule-subtype cells holding only censored values **where an exact sibling value exists**. It is not a
  count over the project's drugs, and it cannot be reproduced today, the harvest's script and output not being on disk.
- **C2, Svensson et al. 2025.** The quotation in section 2 is the arXiv preprint's wording (v1, 6 September 2024). The
  journal's reads: "despite the partial information available in censored labels, they are essential to reliably
  estimate uncertainties in real pharmaceutical settings where approximately one-third or more of experimental labels are
  censored" (read in OpenAlex's index). With that, "No preprint is cited" holds.
- **C3, the "active" shares (section 2.2).** The three figures are not on one scale. On one scale (log-value above 6):
  23.3% in ChEMBL, 52.7% in BindingDB, 79.8% in GtoPdb and 47.1% in the part of PubChem that overlaps them (Isigkeit et
  al. 2022). The 2.8% is a different measure, depositors' outcome labels over all PubChem assay results (An et al. 2025).
  The like-for-like contrast is ChEMBL 23.3% against GtoPdb 79.8%, and the sentence contrasting "about 3% active" with
  "about 80% active" compares two definitions and two populations.
- **C4, Santos et al. 2017.** "667 human proteins for 1,578 FDA-approved drugs" reads: 893 human and pathogen-derived
  biomolecules through which 1,578 US FDA-approved drugs act, 667 of them human-genome-derived proteins.
- **C5, Schiebroek et al. 2026.** The 0.3 log units is an earlier estimate they cite and adopt, not their measurement:
  the source cell reads "an earlier estimate, as cited by Schiebroek et al. 2026 (full text)".
- **C6.** "Rubin's (1976) taxonomy" reads: the taxonomy that grew from Rubin (1976), who defined "missing at random" and
  "observed at random"; the three names are the later standard ones.
- **C7, Heckman.** It assumes, to be identified by more than its distributional assumption, an exclusion restriction;
  "too few rows" refers to the allosteric and channel classes, not the aminergic harvest of 103,196 Ki values; and
  membership of a fixed screening panel is a fourth candidate exclusion variable the record did not weigh.
- **C8, Ingle et al. 2016.** "pharmaceutical training set covered 82 to 99% of their chemical space" reads: the two sets
  "exhibit similarities in terms of chemical space (99-82% overlap)".
- **C9, Shimodaira 2000.** Weighting is optimal only under model misspecification; under a correctly specified model
  the unweighted estimate is asymptotically optimal.
- **C10, Stoeger et al. 2018.** RNA and protein abundance is one of six leading feature categories, so "among the
  leading features".
- **C11, section 0.** "Europe PMC full text for five open-access papers" lists four; it reads four.
- **Identifications.** "Copas and Shi 2000" is their Biostatistics paper (PMID 12933507), not the BMJ paper of the
  same year; "Sugiyama et al. 2006" is the DAGM proceedings chapter; "Kouw et al. 2019" is, by the verifier's best
  match, Kouw, Krijthe and Loog, IEEE MLSP 2019.
- **Missing method families**, named by the verification and not appraised here: worst-case bounds (Horowitz and
  Manski 2000), censoring without a distribution (Powell 1984, Turnbull 1976), Tobit's non-robustness (Arabmazar and
  Schmidt 1982), publication selection on the value (Andrews and Kasy 2019), and noise when combining public
  affinities (Landrum and Riniker 2024).

