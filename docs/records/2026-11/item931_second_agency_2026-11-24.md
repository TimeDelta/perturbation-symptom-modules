# Item 9.31: second-agency reading of the twenty silent drugs (research pass, 24 November 2026)

Model: Fable 5.2 throughout, no fallback. Nothing in the repository was edited. Every page was read with
`experiments/read_public_page.py` (through `item931_fetch.py`, which calls its `PublicPageReader`) and saved under
`item931_pages/` with address, time and SHA-256; `item931_work/index.jsonl` maps each address to its saved file,
`item931_work/dpd_scan.jsonl` is the Health Canada product scan and `item931_work/picks.json` the monographs read.
The step-by-step log is `item931_second_agency_2026-11-24.progress.md`. All paths are under
`/tmp/claude-0/-home-user-perturbation-symptom-modules/bb4ac276-3385-5b5c-bac0-09d70d6ba1f5/scratchpad/`.

This pass does not decide admission. Whether a sentence below is a "statement of central action" under item 14(a)
as tightened by item 31 (an action, not penetration; naming the drug; not an adverse event) is the owner's ruling.

## 1. What the rows ask for (origin/main, read in full: 9.29, 9.31, 9.33, 9.34; preregistration item 31)

- **"Silent"** (item 31 b(i)): the first agency's label (the US label read through openFDA, fields
  `mechanism_of_action`, `clinical_pharmacology`, `pharmacodynamics`, `description`) never addresses the central
  nervous system in a pharmacology sense, so the exclusion "rests on absence" and "may therefore be completed from a
  second medicines agency". A label that states the drug does not reach the brain, or addresses penetration, is not
  silent and is not re-read elsewhere.
- **Which twenty.** The preregistration gives the count and not the names. Derived here: the 24 drugs verdicted
  "no such sentence" in `configs/label_central_action.csv` at commit `e493016` (13 October 2026, the table item 31 b(i)
  measured), minus the four it names (metoclopramide, a false exclusion; acebutolol, verapamil, mecamylamine, whose
  labels address penetration). That leaves: **atenolol, carvedilol, betaxolol, warfarin, naproxen, celecoxib,
  diclofenac, ketoprofen, flurbiprofen, pioglitazone, pitavastatin, sulfasalazine, isotretinoin, ribavirin, diltiazem,
  nifedipine, nicardipine, isradipine, nisoldipine, prazosin.** *This derivation should be confirmed by the session;*
  the seven drugs that became "no such sentence" on 14 October under a(ii) (amisulpride, granisetron, palonosetron,
  bisoprolol, pindolol, timolol, metformin) are not among them, since their labels carry a CNS sentence.
- **Second agencies the rows allow.** The owner, 14 October: "any of the reputable English-released agency sources are
  fine". Named: Health Canada product monographs (9.31; 9.34 found the archived template with ACTION AND CLINICAL
  PHARMACOLOGY is served for some products, "a per-drug lottery"), HPRA (Ireland), TGA (Australia), and the EMA
  reports of `configs/ema_assessment_reports.csv` (celecoxib/Onsenal, ketoprofen/Diractin, pioglitazone/Actos,
  ribavirin/Rebetol among the twenty). The UK eMC refused with a human check on 13 October and was not requested.
  AEMPS (Spanish) was dropped by the owner.

## 2. Method

- **Health Canada.** For each drug the Drug Product Database API was asked for its products; one product per
  company was opened at `health-products.canada.ca/dpd-bdpp/info?lang=eng&code=<code>` for the monograph link and date.
  The monographs to read were chosen by a rule fixed before any was read: (1) the innovator brand's monograph;
  (2) the earliest-dated single-ingredient generic monograph, the one most likely to be on the archived template.
  Departures are stated per drug (a scanned PDF with no text layer was replaced by the next-earliest with one;
  isotretinoin's rule pick was Clarus, a branded generic, so Accutane was added).
- **Screen, then read.** Each document was screened with the repository's own patterns (`CENTRAL_ACTION`,
  `READS_AS_NOT_CENTRAL`, `READS_AS_AN_ADVERSE_EVENT` of `experiments/read_label_central_action.py`) and a wider
  exploratory vocabulary (brain, CSF, hypothalamus, medulla, vasomotor, spinal cord, "centrally acting" and the
  like), over the whole document; every hit was read in context and is classified below by the section it sits in.
  Patient-information parts were ignored.
- **Access.** TGA's product-information repository (`www.ebs.tga.gov.au`) disallows every path in its robots file and
  was not read; TGA AusPAR files on `tga.gov.au` are readable. HPRA SmPC PDFs (`assets.hpra.ie`) and MHRA SmPC PDFs
  (`mhraproducts4853.blob.core.windows.net`) were read where a web search supplied the address; the MHRA products
  site itself is rendered by script and gave the reader no document list, and its programmatic service
  `medicines.api.mhra.gov.uk` answered HTTP 503 three times (transient, not a refusal).
- **Limits.** Six old monographs are scanned images with no text layer and the container has no OCR tool (installing
  one into the scratchpad was denied by the permission classifier). Four were read visually on their ACTION pages
  only; their later PHARMACOLOGY sections are unread. Licences were not re-verified in this pass: the EMA terms are
  in `docs/data_sources.md`; Health Canada's are quoted in row 9.31 (non-commercial reproduction, sponsor copyright
  possible); HPRA, MHRA and TGA terms are **unverified** and would need verifying before a quotation from them is
  relied on (none of the quotations that matter below comes from those three).

## 3. Findings per drug

"HC" = Health Canada product monograph at `https://pdf.hres.ca/dpd_pm/<number>.PDF`, read 24 November 2026.
Categories used in the last column, descriptive only: **silent** (no pharmacology-sense CNS sentence);
**negative** (says CNS effects are absent or minimal, or that little reaches the CNS); **penetration**;
**mechanism location** (says where an enzyme or process is, not that the drug acts there); **central effect
stated** (a sentence attributing a CNS effect or site of action to the drug).

| drug | second-agency documents read | what they say about a central action (quotation, section) | category |
| --- | --- | --- | --- |
| atenolol | HC TENORMIN (Searchlight), dated 2023-05-31, 00071128; HC BCI ATENOLOL, dated 2004-08-13, 00000644 (archived template) | Both, mechanism of action: "The mechanism of the antihypertensive effect has not been established. Among the factors that may be involved are: (a) competitive ability to antagonize catecholamine-induced tachycardia at the beta-receptor sites in the heart, thus decreasing cardiac output; (b) inhibition of renin release by the kidneys; (c) inhibition of the vasomotor centres." Both, pharmacokinetics: "Atenolol is extensively distributed to extravascular tissues, but only a small amount is found in the central nervous system." | hedged class hypothesis that does not name the drug, **plus a negative penetration statement naming the drug** |
| carvedilol | HC COREG (GSK), 2006-03-20, 00002132; HC NOVO-CARVEDILOL, 2003-09-03, 00000076 (both archived template with detailed pharmacology) | Nothing outside adverse-event tables. | silent |
| betaxolol | HC BETOPTIC S (Novartis), 2017-03-06, 00038404 (ophthalmic; Canada has no oral betaxolol). HC SANDOZ BETAXOLOL 2005, 00003414, is a scan and was not read. | Adverse reactions only: "Systemic reactions following topical administration of BETOPTIC* S have been reported rarely (e.g., CNS: insomnia and depressive neurosis)." | silent (adverse event only; ophthalmic product) |
| warfarin | HC COUMADIN (BMS), 2018-09-04, 00047189 (the document of 9.34); HC NOVO-WARFARIN, 2005-02-18, 00001092 | CNS words only in indications (cerebral embolism), contraindications and warnings (haemorrhage, fetal CNS abnormalities). Nothing in ACTION AND CLINICAL PHARMACOLOGY. | silent |
| naproxen | HC ANAPROX (Searchlight), 2025-06-25, 00080902; HC AVA-NAPROXEN EC, 2011-03-30, 00012893; HC RIVA-NAPROXEN SODIUM DS, 1999-08-30, 00002523 (scan, ACTION pages read visually) | ANAPROX, 10.2 Pharmacodynamics (animal): "Acute studies were carried out to determine the effects of naproxen sodium on the cardiovascular and central nervous systems. Naproxen sodium was almost inert in cardiovascular system studies. Its CNS effects were minimal." The other two: nothing outside precautions and adverse reactions. | negative |
| celecoxib | EMA Onsenal scientific discussion and product information; HC CELEBREX (BGP), 2025-07-09, 00080998; HC RIVA-CELECOXIB, 2015-01-15, 00028967 (archived template) | EMA scientific discussion, nonclinical pharmacokinetics: "Celecoxib has been shown to pass the blood-brain barrier, to pass the placenta and to be in excreted in milk." EMA SmPC 5.1: "COX-2 is also involved in ovulation, implantation and closure of the ductus arteriosus, regulation of renal function, and central nervous system functions (fever induction, pain perception and cognitive function)." HC RIVA-CELECOXIB, DETAILED PHARMACOLOGY (animal): "Celecoxib also showed analgesic activity in the irritant dorsoflexion mouse model using two different irritants but it did not affect the CNS component of the dorsoflexion pain response." and "Celecoxib was shown to achieve concentrations in brain tissue greater than 2-fold higher than those found in the plasma at the time points used for analgesic testing, demonstrating penetration of this agent into the CNS. When given intrathecally (to the lumbar spinal cord) to rats prior to injection of carrageenan into the foot pad, celecoxib prevented elevations of CSF levels of PGE2, decreased the inflammatory foot edema and elicited analgesia to a thermal stimulus, indicating that a portion of the analgesic efficacy of celecoxib could be at the level of the spinal cord." HC CELEBREX and RIVA, toxicology: "No adverse pharmacological effect of celecoxib on central nervous system or pulmonary function were seen at plasma levels of celecoxib that are 2- to 5-fold and 3- to 6-fold, respectively, greater than the maximal plasma concentrations at the clinical dose range." | **penetration (two agencies agree)**; mechanism location; **one hedged animal sentence placing part of the analgesic effect at the spinal cord after intrathecal dosing**; one sentence denying an effect on a CNS pain component |
| diclofenac | HC VOLTAREN RAPIDE (Novartis), 2026-04-29, 00084524; HC DOM-DICLOFENAC-SR, 2010-04-19, 00010294 | Detailed (animal) pharmacology, both: "A close correlation exists between certain febrile reactions and increased prostaglandin levels in the brain. Diclofenac (0.5 μg/mL) reduces prostaglandin E2 formation which parallels antipyresis but does not induce hypothermia in the afebrile animal." (Voltaren Rapide prints the first clause of the second sentence only.) | mechanism location: the brain is named in the sentence before the drug's, and no sentence says diclofenac acts there |
| ketoprofen | EMA Diractin withdrawal assessment report (topical); HC PMS-KETOPROFEN, 2010-06-08, 00010744; HC KETOPROFEN SR (AA Pharma), 2022-05-10, 00065749. ORUDIS has no monograph in the DPD. | Nothing outside adverse reactions and a driving warning. | silent |
| flurbiprofen | HC ANSAID (Pfizer), 2010-02-03, 00009704; HC TEVA-FLURBIPROFEN, 2015-07-14, 00031214; HC FROBEN SR 2001, 00002678 (scan, ACTION page read visually) | Nothing outside adverse-reaction lists. | silent |
| pioglitazone | EMA Actos scientific discussion and product information; HC ACTOS (Takeda), 2018-01-18, 00043493; HC AG-PIOGLITAZONE, 2011-10-11, 00014465 | EMA scientific discussion, safety pharmacology: "Pioglitazone did not exert relevant effects on the CNS or ANS in mice and cats, or haemodynamics in anaesthetised dogs." EMA product information and both HC monographs: no CNS word at all. | negative |
| pitavastatin | HPRA Livazo 2 mg SmPC (PA2324/001/002); MHRA Livazo 4 mg SmPC; TGA AusPAR product information for LIVALO. Not in the Canadian DPD. | No brain or CNS word in any pharmacology section; SmPC 5.2: "Pitavastatin is actively transported into hepatocytes, the site of action and metabolism". | silent (three agencies) |
| sulfasalazine | HC SALAZOPYRIN (Pfizer), 2003-09-23, 00002673; HC PMS-SULFASALAZINE-E.C., 2020-04-30, 00056638; HC RATIO-SULFASALAZINE 2002, 00002674 (scan, first ACTION page read visually) | Only warnings ("irreversible neuromuscular and CNS changes") and adverse reactions ("CNS reactions: transverse myelitis, convulsions, ..."). | silent (adverse events only) |
| isotretinoin | HC ACCUTANE (Cheplapharm), 2025-09-05, 00081681; HC CLARUS (Mylan), 2026-01-06, 00083106; HC RAN-ISOTRETINOIN, 2019-12-19, 00054586 | CNS only as fetal malformations in contraindications and warnings, and a toxicology finding ("encephalomalacia limited to single microscopic foci in the brain"). | silent |
| ribavirin | EMA Rebetol scientific discussion and product information; HC IBAVYR (Pendopharm), 2022-03-15, 00065054 | EMA scientific discussion: "Ribavirin was tested in the cardiovascular, gastrointestinal, renal, and central nervous systems in rats following a single oral dose of 200 mg/kg. No significant changes were found in blood pressure, heart rate, ECG, urinary excretion, gastric motility, behaviour." EMA product information: psychiatric and CNS effects as warnings and adverse reactions of the combination with interferon only. HC: nothing. | negative |
| diltiazem | HC TIAZAC XC (Bausch), 2025-03-17, 00078910; HC RATIO-DILTIAZEM CD, 2008-11-26, 00007737 (archived template); HC GEN-DILTIAZEM CD, 2004-06-08, 00004212 (scan, ACTION pages read visually) | Nothing outside adverse-reaction headings; the mechanism text is cardiac and vascular smooth muscle only. | silent |
| nifedipine | HC ADALAT OROS (Bayer), 2016-09-29, 00036539; HC NIFEDIPINE ER (Sivem), 2016-11-16, 00037088; HC NIFEDIPINE capsules (AA Pharma), 2023-12-01, 00073685. The old ADALAT rows carry no monograph. | Only a caution about "cerebral vascular insufficiency" and adverse-reaction headings. | silent |
| nicardipine | EMA Article 31 referral, Annex III SmPC for intravenous nicardipine. Both CARDENE rows in the DPD carry no monograph. | 5.1: "Its action is produced mainly on arterial smooth muscle." CNS words only in 4.4 cautions (intracranial pressure, acute cerebral infarction). | silent (intravenous product) |
| isradipine | **None readable.** | Tried: Health Canada DPD (no product under the ingredient or DynaCirc); HPRA (Prescal entry is a licence withdrawn in 1997 with no document); Medsafe (guessed data-sheet address answers "Page not found"); MHRA (products site gives the reader no list; programmatic service 503); TGA repository closed by robots; three web searches restricted to agency hosts. The eMC is the route that would answer and stays refused. | unread |
| nisoldipine | **None readable.** | Tried: Health Canada DPD (no product under the ingredient or Sular); MHRA and TGA as above; two web searches, which found only the Spanish AEMPS fichas (route dropped by the owner) and a discontinued UK Syscor MR. | unread |
| prazosin | HC MINIPRESS (AA Pharma), 2024-03-15, 00074960; HC TEVA-PRAZOSIN, 2024-11-08, 00077686 | Both, 10.2 Pharmacodynamics: "Miscellaneous Actions At doses considerably higher than those required for antihypertensive activity, prazosin hydrochloride has mild CNS depressant activity, decreases heart norepinephrine and adrenal epinephrine in rats, causes diuresis in anesthetized dogs, but fluid retention in conscious dogs and mice, and is hyperglycemic in rats." | **central effect stated**, naming the drug, in animals at supratherapeutic doses. One lineage (a generic's monograph follows the innovator's), so one source, not two |

## 4. Counts

- **18 of the twenty now have a second-agency reading**; isradipine and nisoldipine have none.
- Of the 18: **11 silent at the second agency too** (carvedilol, betaxolol, warfarin, ketoprofen, flurbiprofen,
  pitavastatin, sulfasalazine, isotretinoin, diltiazem, nifedipine, nicardipine); **3 negative** (naproxen "Its CNS
  effects were minimal"; pioglitazone "did not exert relevant effects on the CNS"; ribavirin no behavioural change);
  **atenolol** a negative penetration statement plus a hedged class hypothesis ("inhibition of the vasomotor
  centres"); **diclofenac** a mechanism-location sentence only; **celecoxib** penetration at two agencies plus one
  hedged animal sentence on a spinal site; **prazosin** the only sentence that attributes a CNS effect to the drug
  outright, in animals above antihypertensive doses.
- No second-agency document states, for human therapeutic use, that any of the twenty acts centrally.

## 5. Things the session should know before using this

1. **The list of twenty is derived, not quoted** (section 1). If the owner's twenty differ, the table's rows still
   stand per drug.
2. **Three of the readings turn "silent" into "addressed"**, which matters under the three-way rule of commit
   `673c6c2` / item 31 b(i): atenolol's Canadian monograph says only a small amount reaches the CNS, and naproxen's
   and pioglitazone's second-agency documents report minimal or no CNS effect. Whether a second agency's negative
   statement counts as "an explicit statement" for these drugs is a question for the owner, not answered here.
3. **Route mismatches.** Betaxolol was read only on an ophthalmic monograph, nicardipine only on an intravenous
   SmPC, ketoprofen's EMA report is for a topical product.
4. **Single-source rows.** Prazosin's sentence rests on one lineage; a second independent agency (HPRA or MHRA
   Hypovase SmPC) was not read. Celecoxib's spinal sentence is in a generic's monograph (RIVA-CELECOXIB, 2015) and
   not in the current CELEBREX monograph, which has dropped the detailed animal pharmacology.
5. **Unread parts.** The PHARMACOLOGY sections of the scanned monographs (GEN-DILTIAZEM CD, RIVA-NAPROXEN SODIUM DS,
   RATIO-SULFASALAZINE, FROBEN SR) and all of SANDOZ BETAXOLOL, for want of OCR.
6. **Still open for isradipine and nisoldipine:** the MHRA programmatic service when it answers again; the TGA and
   eMC routes stay closed (robots, human check). Addresses for the owner to open by hand, if wanted:
   `https://products.mhra.gov.uk/substance/?substance=ISRADIPINE` and
   `https://products.mhra.gov.uk/substance/?substance=NISOLDIPINE`.
7. **Licences**: HPRA, MHRA and TGA reuse terms unverified in this pass (section 2).
8. No text addressed to an AI assistant was met on any page. No permission request was left unanswered (the shell
   reader was used throughout).
