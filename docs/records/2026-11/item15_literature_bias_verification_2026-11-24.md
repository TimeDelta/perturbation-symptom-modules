# Fable verification of docs/literature_bias_2026-11-20.md (queue item 15)

Date: 24 November 2026. Model: Fable 5.2 throughout, no fallback. The repository was not changed. Progress log:
item15_verification_2026-11-24.progress.md. Saved pages: item15_pages/ (epmc_index, epmc_fulltext, crossref, openalex, misc, classics),
each with address, time and SHA-256 from experiments/read_public_page.py. Bibliographic data below are, according to PubMed, as its
records give them, confirmed against Europe PMC; DOIs are given for every work.

## 0. What could be re-read and what could not

- The Opus pass's progress log, its .bib draft, its saved pages (literature_bias_pages/) and the three scratchpad reports it quotes
  (fallback_class_definition_2026-11-18.md, tpm_fallback_holdout_2026-11-18.md, carrier_class_definition_2026-11-18.md) are not on
  this machine and not in the repository. Every citation was therefore re-identified from the record's author, year and quotation.
- Read in full text here (Europe PMC XML): Stoeger 2018, Schaefer 2015, Luck 2020, Haynes 2018, Isigkeit 2022, An 2025, Schiebroek 2026.
- Abstract (PubMed and Europe PMC, or OpenAlex / Consensus index for works outside PubMed): all others except Tobin 1958.
- Bibliographic record only: Tobin 1958 (no index holds an abstract; the Cowles reprint address answered with a search page).
- Refusals respected: export.arxiv.org/api and link.springer.com (robots). Transient, not a refusal: Europe PMC full text for
  Rolland 2014, Santos 2017, Oprea 2018 answered HTTP 500 again (three more tries on 24 November); all three are author manuscripts
  outside Europe PMC's open-access subset, the likely standing cause. Their numbers are abstract numbers and are verified there.
- Text addressed to an AI or asking for personal data, not acted on: the PubMed connector's "important_legal_notice", the Consensus
  "IMPORTANT INSTRUCTIONS" block (both tool output), and Semantic Scholar's "?email=<INSERT_YOUR_EMAIL>" in its JSON.

## 1. Citations: every cited work exists (38 of 38)

| work | identified as | indexes |
|---|---|---|
| Rubin 1976 | Biometrika 63(3):581-592, doi 10.1093/biomet/63.3.581 | Crossref, OpenAlex |
| Little 1993 | J Am Stat Assoc 88(421):125-134, doi 10.1080/01621459.1993.10594302 | Crossref, OpenAlex |
| Heckman 1979 | Econometrica 47(1):153-161, doi 10.2307/1912352 | Crossref, OpenAlex |
| Tobin 1958 | Econometrica 26(1):24-36, doi 10.2307/1907382 | Crossref, OpenAlex, Semantic Scholar |
| Rosenbaum and Rubin 1983 | Biometrika 70(1):41-55, doi 10.1093/biomet/70.1.41 | Crossref, OpenAlex |
| Shimodaira 2000 | J Stat Plan Inference 90(2):227-244, doi 10.1016/S0378-3758(00)00115-4 | Crossref, OpenAlex, Consensus |
| Stoeger 2018 | PLoS Biol 16(9):e2006643, PMID 30226837, doi 10.1371/journal.pbio.2006643 | PubMed, Europe PMC |
| Pogodin 2019 | SAR QSAR Environ Res 30(10):759-773, PMID 31547686, doi 10.1080/1062936X.2019.1665580 | PubMed, Europe PMC |
| Cro 2020 | Stat Med 39(21):2815-2842, PMID 32419182, doi 10.1002/sim.8569 | PubMed, Europe PMC |
| Leacy 2017 | Am J Epidemiol 185(4):304-315, PMID 28073767, doi 10.1093/aje/kww107 | PubMed, Europe PMC |
| Hayati Rezvan 2018 | Hayati Rezvan, Lee, Simpson, Longit Life Course Stud 9(3):259-278, doi 10.14301/llcs.v9i3.503 (not in PubMed) | Crossref, OpenAlex |
| Copas and Shi 2000 | Biostatistics 1(3):247-262, PMID 12933507, doi 10.1093/biostatistics/1.3.247 (NOT their BMJ paper of the same year, PMID 10669446) | PubMed, Europe PMC |
| Kone 2019 | BMC Med Res Methodol 19(1):231, PMID 31815610, doi 10.1186/s12874-019-0840-7 | PubMed, Europe PMC |
| Marchenko and Genton 2012 | J Am Stat Assoc 107(497):304-317, doi 10.1080/01621459.2012.656011 | Crossref, OpenAlex |
| Gomes 2020 | Stat Med 39(11):1658-1674, PMID 32059073, doi 10.1002/sim.8504 | PubMed, Europe PMC |
| Puhani 2000 | J Econ Surv 14(1):53-68, doi 10.1111/1467-6419.00104 | Crossref |
| Seaman and White 2013 | Stat Methods Med Res 22(3):278-295 (online 2011), PMID 21220355, doi 10.1177/0962280210395740 | PubMed, Europe PMC |
| Sugiyama 2008 | Sugiyama, Suzuki, Nakajima, Kashima, von Bunau, Kawanabe, Ann Inst Stat Math 60(4):699-746, doi 10.1007/s10463-008-0197-x | Crossref, OpenAlex, Consensus |
| "Sugiyama 2006" | Sugiyama, Blankertz, Krauledat, Dornhege, Muller, DAGM 2006, LNCS 4174:354-363, doi 10.1007/11861898_36 (reviewed proceedings; journal version JMLR 8, 2007) | Crossref, OpenAlex, Consensus |
| "Kouw 2019" | most likely Kouw, Krijthe, Loog, IEEE MLSP 2019, doi 10.1109/MLSP.2019.8918731; the record gives no title and its .bib is lost, so this identification is mine | Crossref, OpenAlex |
| Svensson 2025 | Svensson, Friesacher, Winiwarter, Mervin, Arany, Engkvist, Artif Intell Life Sci 7:100128, doi 10.1016/j.ailsci.2025.100128 (not in PubMed) | Crossref, OpenAlex, Semantic Scholar |
| Schaefer 2015 | Front Genet 6:260, PMID 26300911, doi 10.3389/fgene.2015.00260 | PubMed, Europe PMC |
| Lazareva 2021 | Brief Bioinform 22(5):bbab066, PMID 33782690, doi 10.1093/bib/bbab066 | Europe PMC, bib |
| Gillis and Pavlidis 2012 | PLoS Comput Biol 8(3):e1002444, PMID 22479173, doi 10.1371/journal.pcbi.1002444 | Europe PMC, bib |
| Sarkar 2023 | Bioinformatics 39(6):btad345, PMID 37233198, doi 10.1093/bioinformatics/btad345 | PubMed, Europe PMC |
| Luck 2020 | Nature 580(7803):402-408, PMID 32296183, doi 10.1038/s41586-020-2188-x | PubMed, Europe PMC |
| Haynes 2018 | Sci Rep 8(1):1362, PMID 29358745, doi 10.1038/s41598-018-19333-x | Europe PMC, bib |
| Oprea 2018 | Nat Rev Drug Discov 17(5):317-332, PMID 29472638, doi 10.1038/nrd.2018.14 | PubMed, Europe PMC |
| Santos 2017 | Nat Rev Drug Discov 16(1):19-34, PMID 27910877, doi 10.1038/nrd.2016.230 | PubMed, Europe PMC |
| Rolland 2014 | Cell 159(5):1212-1226, PMID 25416956, doi 10.1016/j.cell.2014.10.050 | Europe PMC, bib |
| Isigkeit 2022 | Molecules 27(8):2513, PMID 35458710, doi 10.3390/molecules27082513 | PubMed, Europe PMC |
| An 2025 | An S, Lee Y, Gong J, et al., "InertDB ...", J Cheminform 17(1):49, PMID 40211375, doi 10.1186/s13321-025-00999-1 | Europe PMC |
| Smajic 2025 | Chem Res Toxicol 38(5):820-833, PMID 40253625, doi 10.1021/acs.chemrestox.4c00347 | PubMed, Europe PMC |
| Kramer 2012 | J Med Chem 55(11):5165-5173, PMID 22643060, doi 10.1021/jm300131x | PubMed, Europe PMC |
| Schiebroek 2026 | Schiebroek, Landrum, Riniker, J Chem Inf Model 66(13):7446-7452, PMID 42335255, doi 10.1021/acs.jcim.6c01018 | PubMed, Europe PMC |
| Watanabe 2018 | Mol Pharm 15(11):5302-5311, PMID 30259749, doi 10.1021/acs.molpharmaceut.8b00785 | PubMed, Europe PMC |
| Ingle 2016 | J Chem Inf Model 56(11):2243-2252, PMID 27684444, doi 10.1021/acs.jcim.6b00291 | PubMed, Europe PMC |
| Lombardo 2018 / Israili and Dayton 2001 | PMID 30115648 / PMID 11495502, as in docs/references.bib | Europe PMC, bib |

Mestres 2008 and Edwards 2011 (found, not read, nothing rests on them) were not checked.

## 2. Quotations: 33 of 34 verbatim in the source; one is from the preprint, not the journal

Verbatim in the abstract (PubMed/Europe PMC): Pogodin (all four), Cro, Copas and Shi, Kone, Gomes, Seaman and White, Sarkar, Oprea,
Santos ("continued dominance of privileged target families"), Rolland (both), Lazareva (both), Gillis, Smajic (both), Kramer, Watanabe,
Ingle ("scarce ...", "MAE 0.07-0.12"), Lombardo, Israili, Schaefer ("the degree of a protein is a function ...", "no conclusive evidence").
Verbatim in the full text (Europe PMC): Stoeger (all four), Schaefer (the two method quotes), Luck (both), Isigkeit ("IUPHAR/BPS
focusing on potent, expert-selected chemical tools ..."), An (both), Schiebroek. Verbatim in the abstract as indexed by Consensus:
Sugiyama 2008, Sugiyama 2006.

**Not as quoted: Svensson et al. 2025.** The record's wording is the arXiv preprint's (arXiv:2409.04313 v1, 6 September 2024). The
journal abstract (OpenAlex index; one source, the publisher page is a redirect script and Crossref holds no abstract) ends "they are
essential to reliably estimate uncertainties in real pharmaceutical settings where approximately one-third or more of experimental
labels are censored". The record also says "No preprint is cited", which the quotation contradicts.

## 3. Numbers: all literature numbers are in their sources; two are presented misleadingly; the project's own are mostly uncheckable

- In source as stated: Stoeger 0.64, 430, 16%, 49%, 5%; Haynes 0.25, 0.47, 0.33, 0.63, 0.70, 0.79, 0.63; Oprea one in three; Rolland ~30%;
  Isigkeit 23.3, 43.5, 52.7, 79.8, 5; Pogodin 87,583, 919, 0.87, 0.75; An 2.8, 91.4; Smajic -0.34 to 0.37; Kramer 0.44; Schiebroek 0.3;
  Watanabe 2,738; Ingle 0.07-0.12; Lombardo 1,352.
- **Misleading (a): the PubChem / ChEMBL / GtoPdb active shares.** 23.3% and 79.8% are Isigkeit's (records with log-value above 6); 2.8%
  is An's (depositors' outcome labels over all PubChem assay results). Isigkeit's own PubChem figure, in the same sentence as the
  ChEMBL one, is 47.1% active and 15.6% inactive (PubChem restricted to compounds found in the other databases). The record omits it,
  and the queue's line puts 2.8, 23.3 and 79.8 on one scale.
- **Misleading (b): Santos.** "667 human proteins for 1,578 FDA-approved drugs": the 1,578 drugs act through 893 human and
  pathogen-derived biomolecules, of which 667 are human-genome-derived proteins.
- Not a measurement of the cited paper: Schiebroek's 0.3 log units is an estimate from earlier work, cited in their introduction and
  then adopted as "the assumed experimental variability".
- Derived by the record itself: "about 3%" and "about 80%" (rounding); "about 23% active" (rounding). Nothing else.
- **Project-internal numbers.** Found in the repository: 5,676, 98.5%, 84.5%, "about 0.25 log" (item 37 draft, section 19, lines
  1599-1606); "206 pairs" (line 1748); "10 of its 28" (line 1442); "28 of the 35" and the TPM figures (queue item 15 table); Kramer's 0.44
  (line 996). **Not found anywhere in the repository**: 163 of 206; amisulpride 8.6 against 6.0; acamprosate 3.5 against 4.9; 4
  allosteric and 8 channel-blocker measurements; "no sourced channel-opener measurement"; "two well-measured" zwitterion members. They
  rest on scratchpad reports that are not on this machine, so they could not be checked.

### The count 5,676: where it comes from

Its only source in the repository is docs/item37_rulings_draft_2026-11-13.md, section 19, "The class definition after the ChEMBL
check" (lines 1599-1606, commit fac771e of 20 November 2026): "The harvest finished on 19 November 2026 (ChEMBL_37, release 2026-05-01;
103,196 usable binding Ki values, 39,334 molecules)" and "5,676 cells hold only censored values where an exact sibling value exists,
transfer failures the script never sees, all on the failing side". So: taken on ChEMBL_37 (release 2026-05-01), binding Ki only, the
receptor and transporter families of the sibling-transfer harvest, a cell being a molecule-subtype pair, measured 19 November 2026. It
is a table measurement, not a graph measurement, and not a count over the project's own drugs. The harvest script and its output are
not in the repository and not on this machine, so the count is not reproducible from the repository today. The queue's summary
("5,676 ChEMBL cells hold only a censored value") drops the condition "where an exact sibling value exists" and the scope. No count of
censored rows among the project's own class-centre inputs exists.

## 4. Appraisal

**Tobit "can correct rather than bound": stands only in a narrowed form.** What a censored likelihood can do is correct a class-level
statistic for the rows that record a bound, when each row's threshold is known and the assumed distribution holds. What it cannot do:
(i) recover the value of a cell that holds only a bound, which stays an interval; (ii) correct for pairs never assayed or never
deposited, which is the selection behind the unsourced occupancy pairs and the amisulpride gap, so it does not correct "the bias toward
tight binding" in general; (iii) hold up under a wrong distribution: the Tobit estimate is known not to be robust to non-normality or
unequal variance (Arabmazar and Schmidt 1982, Econometrica 50(4):1055, doi 10.2307/1912776; stated from my knowledge, bibliographic
record only). A class median needs no likelihood at all while fewer than half of its values are censored on one side, which fits the
ruled class centre better than a normal likelihood. Svensson et al. is fair support for using Tobit on drug-discovery labels, but its
subject is uncertainty estimation in machine-learning models, not bias correction of public Ki tables. "Does the project have it: Yes"
is true only in that ChEMBL_37 records the relation; how many censored rows fall in the project's classes is unmeasured.

**Heckman models "do not fit": stands.** The verdict rests on the exclusion-variable argument, which is fair to Gomes 2020 and Puhani
2000 at abstract level. Three qualifications: an exclusion restriction is not a formal assumption of Heckman 1979 (the model is
formally identified by its distributional assumption; the working-paper version, NBER w0172, confirms the bivariate normal density),
so "Assumes" should read "in practice needs"; "too few rows" is true of the allosteric and channel classes (4 and 8 measurements, a
number I could not check) but not of the aminergic harvest (103,196 Ki values); and the record weighed three candidate exclusion
variables only, where membership of a fixed screening panel is a fourth it did not consider. Puhani's abstract speaks of collinearity,
not of exclusion variables; the link is in the body, which I did not read. Kone's quoted result is a simulation and I read the
abstract only.

**The other families: fair.** Delta adjustment (Cro, Leacy, Hayati Rezvan), IPW (Seaman and White), covariate-shift weighting (Sugiyama,
Kouw) and the network corrections (Schaefer, Lazareva, Sarkar, Luck) are described as their abstracts or full texts describe them. Two
additions: Shimodaira shows weighting is optimal only when the model is misspecified, and that under a correctly specified model the
unweighted estimate is asymptotically optimal, a condition the record omits; and delta adjustment does assume something, namely that
the departure is a shift of the stated form within the stated range. "Rubin's (1976) taxonomy" is loose: Rubin 1976 defines "missing at
random" and "observed at random"; the three names are the later standard ones.

Section 3 and the recommendations are the pass's reasoning and are marked so; nothing in the sources contradicts them, and the
remark that the held-out split must be stratified before it is fixed follows from the weighting literature (positivity).

## 5. Missing sources (narrow; bibliographic records only, content from my knowledge unless said)

- **Partial identification (worst-case bounds)**: Manski; Horowitz and Manski 2000, J Am Stat Assoc 95(449) (Crossref returned the
  rejoinder at p. 87; the main article's record was not retrieved). The assumption-free form of "bound, do not correct", a companion
  to R-b.
- **Censoring without a distribution**: Powell 1984, J Econometrics 25(3):303-325, doi 10.1016/0304-4076(84)90004-6 (censored least
  absolute deviations, i.e. medians under censoring); Turnbull 1976, J R Stat Soc B 38(3):290-295, doi 10.1111/j.2517-6161.1976.tb01597.x.
- **Selection on the value at publication**: Andrews and Kasy 2019, Am Econ Rev 109(8):2766-2794, doi 10.1257/aer.20180310, which models
  the probability of publication as a function of the result; closer to "a weak binder is not reported" than Copas and Shi, with the
  same need for replicated estimates.
- **Noise when combining public affinities**: Landrum and Riniker 2024, J Chem Inf Model (PMID 38394344), the likely source of the 0.3
  figure Schiebroek cites and a second source beside Kramer 2012; Kramer's abstract itself reports "repeated citations of single
  measurements (90% of all pairs)", independent support for the project's 98.5%.
- Still not found: a measured survey of AAG-specific binding coverage (not searched further in this pass).
