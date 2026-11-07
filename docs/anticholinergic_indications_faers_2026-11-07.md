# Anticholinergic indications for the FAERS tardive dyskinesia reader (research pass, 7 November 2026)

Model: Fable (no fallback). Nothing in the repository was edited by this pass.

## Status

- [x] 1. Label indication sentences (benztropine, procyclidine, trihexyphenidyl)
- [x] 2. What each label says about tardive dyskinesia; the two readings for the owner
- [x] 3. Where these drugs' indications map now in the repository
- [x] 4. Proposed rows for configs/faers_curated_indications.csv
- [x] 5. Peer-reviewed sources on co-prescription / indication confounding
- [x] Report (in the SubagentHandback; the questions for the owner end section 4)

## 1. Label indication sentences

All pages below were read on 7 November 2026 with `PYTHONPATH=. python experiments/read_public_page.py`, saved with
their SHA-256 sidecars in the pass's working directory, which is not kept. The addresses were constructed by this pass (DailyMed's documented REST service and the eMC
search page), so the shell fallback applied; no permission request was raised. DailyMed serves no robots file ("none
served, which the protocol treats as no restriction"); medicines.org.uk and health-products.canada.ca answered 200 and
the reader did not refuse them.

### Benztropine (US; `CID100002344`)

- **Source.** DailyMed SPL, Benztropine Mesylate Tablets, Par Health USA, LLC, set id `c19664aa-a797-4192-b5f3-e906a7cac048`,
  SPL version 11, effective time 20260820 (published on DailyMed 29 September 2026). Address read:
  `https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/c19664aa-a797-4192-b5f3-e906a7cac048.xml` (SHA-256
  41e9ff0d0742c8a95bd8a5ba5c5805b5b3cd2ba77dc4b14ee6dddf51712b52b3; the human-readable page is
  `https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c19664aa-a797-4192-b5f3-e906a7cac048`). Read 7 November 2026, 17:56 UTC.
- **INDICATIONS AND USAGE (verbatim).** "For use as an adjunct in the therapy of all forms of parkinsonism. Useful also
  in the control of extrapyramidal disorders (except tardive dyskinesia – see PRECAUTIONS) due to neuroleptic drugs
  (e.g., phenothiazines)."
- **Second US label, same wording.** Benztropine Mesylate Injection, Hikma Pharmaceuticals USA Inc., set id
  `95620f40-5ddf-41b8-80a5-f658248f26f0`, SPL version 10, effective time 20240411
  (`https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/95620f40-5ddf-41b8-80a5-f658248f26f0.xml`, SHA-256
  7735c2089c13eb2f1b109329a1b91a10875b484549b87b82f2db639da79a8241, read 7 November 2026): "For use as an adjunct in
  the therapy of all forms of parkinsonism (see DOSAGE AND ADMINISTRATION). Useful also in the control of extrapyramidal
  disorders (except tardive dyskinesia — see PRECAUTIONS) due to neuroleptic drugs (e.g., phenothiazines)."
- Note: both are generic (ANDA) labels; the originator Cogentin labels are no longer listed on DailyMed under this
  search (56 SPLs for benztropine on 7 November 2026, all generics or repackagers). Generic labels carry the reference
  listed drug's text, and the two read here agree word for word on the indication.

### Trihexyphenidyl (US; `CID100005572`)

- **Source.** DailyMed SPL, Trihexyphenidyl Hydrochloride Tablets, Actavis Pharma, Inc., set id
  `a44d7803-164d-4a67-9356-581c45de8596`, SPL version 10, effective time 20240202 (published on DailyMed 16 January 2025).
  Address read: `https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/a44d7803-164d-4a67-9356-581c45de8596.xml`
  (SHA-256 f0ab58a657c6a50f8da5d0c966f2d877659879d31e07f594ba1e70d61399e818). Read 7 November 2026, 17:56 UTC.
- **INDICATIONS (verbatim).** "This drug is indicated as an adjunct in the treatment of all forms of parkinsonism
  (postencephalitic, arteriosclerotic, and idiopathic). It is often useful as adjuvant therapy when treating these forms
  of parkinsonism with levodopa. Additionally, it is indicated for the control of extrapyramidal disorders caused by
  central nervous system drugs such as the dibenzoxazepines, phenothiazines, thioxanthenes, and butyrophenones."
- The indication section does **not** name tardive dyskinesia; the PRECAUTIONS section does (section 2).

### Procyclidine (not marketed in the US; `RXCUI:8718`)

DailyMed holds no procyclidine SPL (the project's route table, `configs/drug_administration_routes.csv`, already
records "no label route"), so the second agency is the UK MHRA through the eMC, which holds five procyclidine SmPCs
(search `https://www.medicines.org.uk/emc/search?q=procyclidine`, read 7 November 2026). Two were read:

- **Source A (current generic SmPC).** Procyclidine Hydrochloride 5 mg tablets, Generics (U.K.) Limited T/A Viatris,
  PL 04569/0110, "Date of revision of the text 06/2026", "Last updated on emc: 26 Jun 2026".
  `https://www.medicines.org.uk/emc/product/8488/smpc` (SHA-256
  a95e21d7faee833be826ce45fb3fa4f797fa1c81f678e70dba30297826e0a06b). Read 7 November 2026, 17:57 UTC.
  **4.1 Therapeutic indications (verbatim).** "Procyclidine is indicated in all forms of Parkinson's disease:
  idiopathic (paralysis agitans), post encephalitic and arteriosclerotic. Symptoms often responding well to procyclidine
  include: rigidity, akinesia, tremor, speech and writing difficulties, gait, sialorrhoea and drooling, sweating,
  oculogyric crises and depressed mood. Tardive dyskinesia is not improved by procyclidine and may be made worse (see
  section 4.4). Procyclidine is also used to control troublesome extrapyramidal symptoms induced by neuroleptic drugs
  including pseudo-parkinsonism, acute dystonic reactions and akathisia."
- **Source B (originator brand).** Kemadrin Tablets 5 mg, Aspen Pharma Trading Limited, PL 39699/0046, "Date of
  revision of the text 21/02/2016", "Last updated on emc: 02 Mar 2016". `https://www.medicines.org.uk/emc/product/5460/smpc`
  (SHA-256 d5cfc7bdb221a05837411d82ae244db8861280318b33ebb4923156f22db798ae). Read 7 November 2026, 17:57 UTC.
  **4.1 Therapeutic indications (verbatim).** "Kemadrin is indicated for the treatment and symptomatic relief of all
  forms of Parkinson's disease e.g. idiopathic (paralysis agitans), postencephalitic and arteriosclerotic disease.
  Kemadrin is also indicated for the control of extrapyramidal symptoms induced by neuroleptic drugs including
  pseudo-parkinsonism, acute dystonic reactions and akathisia."
- Health Canada: the DPD's API lists procyclidine hydrochloride products (drug codes 958, 6392, 2062, 6394, 964, 5725,
  3763, 60346; `https://health-products.canada.ca/api/drug/activeingredient/?lang=en&ingredientname=procyclidine`,
  read 7 November 2026). See the status note below for whether a monograph was read.

## 2. Tardive dyskinesia in the labels

Every label read says the same three things: anticholinergics do not relieve tardive dyskinesia, may aggravate it, and
(for benztropine) are not recommended in patients who have it. Verbatim:

- **Benztropine (Par tablets, PRECAUTIONS; identical in the Hikma injection but for "have been discontinued").**
  "Tardive dyskinesia may appear in some patients on long-term therapy with phenothiazines and related agents, or may
  occur after therapy with these drugs has been discontinued. Antiparkinsonism agents do not alleviate the symptoms of
  tardive dyskinesia, and in some instances may aggravate them. Benztropine mesylate is not recommended for use in
  patients with tardive dyskinesia." And the indication itself excludes it: "(except tardive dyskinesia – see
  PRECAUTIONS)". So the owner's recollection is right in substance; the exact wording is "control of extrapyramidal
  disorders (except tardive dyskinesia – see PRECAUTIONS) due to neuroleptic drugs (e.g., phenothiazines)".
- **Trihexyphenidyl (Actavis tablets, PRECAUTIONS).** "Tardive dyskinesia may appear in some patients on long term
  therapy with antipsychotic drugs or may occur after therapy when these drugs have been discontinued. Antiparkinson
  agents do not alleviate the symptoms of tardive dyskinesia and in some instances may aggravate them. However,
  parkinsonism and tardive dyskinesia often coexist in patients receiving chronic neuroleptic treatment, and
  anticholinergic therapy with trihexyphenidyl hydrochloride may relieve some of these parkinsonism symptoms." The
  indication section does not mention tardive dyskinesia at all.
- **Procyclidine (Viatris SmPC, section 4.1 and 4.4).** In 4.1: "Tardive dyskinesia is not improved by procyclidine and
  may be made worse (see section 4.4)." In 4.4: "Tardive dyskinesia. In a proportion of patients undergoing neuroleptic
  treatment, tardive dyskinesias will occur. While anticholinergic agents do not cause this syndrome, when given in
  combination with neuroleptics, they may exacerbate the symptoms of tardive dyskinesia or reduce the threshold at
  which dyskinesias appear in patients predisposed to this abnormality. In such individuals subsequent adjustment of
  neuroleptic therapy or reduction in anticholinergic treatment should be considered."
  **Kemadrin SmPC, 4.4** (same text, with the typographical "dysknesias"): "In a proportion of patients undergoing
  neuroleptic treatment, tardive dysknesias will occur. While anticholinergic agents do not cause this syndrome, when
  given in combination with neuroleptics they may exacerbate the symptoms of tardive dyskinesia or reduce the threshold
  at which these symptoms appear in predisposed patients."

**A detail from SIDER that bears on this.** `data/raw/sider_4.1/meddra_all_indications.tsv.gz` holds, for benztropine
(CID100002344), `Tardive dyskinesia` with detection method `text_mention`, not `NLP_indication`; for tetrabenazine
(CID100006018) it holds `Tardive dyskinesia` as `NLP_indication`. SIDER's NLP therefore read the benztropine label's
"(except tardive dyskinesia)" as a mention and not an indication, which is the correct reading, and
`load_drug_label_events.py` (default `indication_methods=("NLP_indication",)`) drops it. For trihexyphenidyl and
procyclidine SIDER holds no tardive dyskinesia indication row of any method (procyclidine is not in SIDER at all; its
only evidence rows are two OnSIDES-label `induces` rows).

### What follows for the owner's ruling (the two readings; not decided here)

The labels place tardive dyskinesia **outside** the indication of all three anticholinergics, and two of them
(benztropine, procyclidine) say so in the indication sentence itself. So the FAERS tardive dyskinesia reports naming
benztropine, procyclidine and trihexyphenidyl are not reports of the indicated condition. They are, on the labels'
own account, reports from patients "on long-term therapy with phenothiazines and related agents" who were given the
anticholinergic for the drug-induced parkinsonism, dystonia or akathisia that "often coexist" with tardive dyskinesia
("parkinsonism and tardive dyskinesia often coexist in patients receiving chronic neuroleptic treatment", the
trihexyphenidyl label). The confounder is therefore the co-prescribed antipsychotic (confounding by co-medication, or
by the indication for the co-medication), with a second mechanism the labels themselves name: the anticholinergic "may
aggravate" an existing tardive dyskinesia, which makes some of the reports plausibly genuine aggravation reports and
not pure confounding.

- **Reading 1 (literal).** Decision 9.96 admits "the removal of labels that match the drug's own indication". The drug's
  own indication is parkinsonism / drug-induced extrapyramidal disorder; it is not tardive dyskinesia, and the label
  explicitly carves tardive dyskinesia out. A curated `relieves` row for `tardive_dyskinesia` would state something the
  label contradicts ("not improved ... and may be made worse"). Under this reading the hand-curated file may hold only
  what the labels support (parkinsonism, and under the fine crosswalk the extrapyramidal terms that map to it, plus
  akathisia and dystonia for procyclidine), and the tardive dyskinesia pairs stay in the FAERS reader as candidate
  signals, where the reader's `limitations` text already names "co-medication (one report names several drugs)". The
  tetrabenazine pair is the only one skipped as indication-confounded, by SIDER's own NLP_indication row.
- **Reading 2 (the owner's 7 November 2026 "Yes", read as covering this case).** The purpose of the 9.96 correction is to
  keep a reader from scoring a drug as inducing the condition it is given to patients who already have, or are on the
  course of getting, that condition. The anticholinergics are given to the exact population in which tardive dyskinesia
  arises, for a sibling adverse effect of the same co-prescribed drug class, and the labels say they do not cause it
  ("While anticholinergic agents do not cause this syndrome"). Under this reading the owner extends the curated file to
  a `tardive_dyskinesia` row for each of the three, resting on the ruling and on the labels' "do not cause" sentence, not
  on an indication match, and marked so. The cost is that the labels' "may aggravate" and "reduce the threshold" sentences
  describe a real pharmacological effect on the symptom, which the skip would also discard; whether an aggravation of an
  antipsychotic-induced syndrome counts as the anticholinergic "inducing" the symptom at PROTEIN:CHRM1 is a modelling
  question for the owner.

Either way, a row for tardive dyskinesia would not literally be a "match to the drug's own indication", so if Reading 2
is taken, 9.96 needs a dated amendment or a sub-decision saying that a co-prescription confounder named in the label's
own precautions is admitted alongside the indication match, and the row is flagged as resting on the ruling.

## 3. Current mapping in the repository

- **Fine crosswalk (`docs/symptom_crosswalk_fine.csv`).** `parkinsonism` (HP:0001300) carries the MedDRA preferred terms
  `Parkinsonism;Drug-induced parkinsonism;Extrapyramidal disorder;Parkinsonian gait`; `akathisia` (HP:0031943) carries
  `Akathisia`; `bradykinesia`, `resting_tremor`, `pill_rolling_tremor`, `cogwheel_rigidity` and
  `extrapyramidal_muscular_rigidity` are the other fine constructs under coarse `parkinsonism`. No construct carries a
  dystonia term (grep for "dystonia" in the committed crosswalk finds nothing). The parent session's uncommitted working
  tree (read 7 November 2026, about 18:05 UTC) adds three rows to the crosswalk: `tardive_dyskinesia` (HP:0040141,
  MedDRA `Tardive dyskinesia`, decision 9.115), `orofacial_dyskinesia` (HP:0002310) and `extrapyramidal_dyskinesia`
  (HP:0007308), the last two under decision 9.116; neither 9.115 nor 9.116 is a row of `docs/open_decisions.md` yet.
  The two new dyskinesia constructs carry no MedDRA term in the diff, so no label row of this pass maps to them.
- **SIDER indication handling (`mechanistic_pathway_learning/evidence/load_drug_label_events.py`).** Indications become
  `relieves` events only when SIDER's detection method is `NLP_indication` (default `indication_methods`), at the
  preferred-term level, mapped to a target symptom through the crosswalk's MedDRA terms; source `SIDER-indication`,
  one `label_text` report per indication.
- **v5 evidence table (`data/processed/evidence_full_v5/evidence_reports.parquet`, read 7 November 2026).** `relieves`
  rows of the four drugs:

  | perturbation_id | drug | symptom | source_term_label | source |
  |---|---|---|---|---|
  | CID100002344 | benztropine | parkinsonism | Extrapyramidal disorder | SIDER-indication |
  | CID100002344 | benztropine | parkinsonism | Parkinsonism | SIDER-indication |
  | CID100005572 | trihexyphenidyl | parkinsonism | Parkinsonism | SIDER-indication |
  | RXCUI:8718 | procyclidine | (none) | | |
  | CID100006018 | tetrabenazine | (none in v5) | | |

  So in v5 `indicated_symptoms_by_drug` gives benztropine and trihexyphenidyl `{parkinsonism}` and procyclidine and
  tetrabenazine nothing. Tetrabenazine's SIDER rows (`Chorea`, `Huntington's disease`, `Tardive dyskinesia`, all
  `NLP_indication`) map to no v5 construct; once `tardive_dyskinesia` is a construct and the table is rebuilt, its
  `Tardive dyskinesia` row becomes the one `relieves` pair the 9.115 note measured. Trihexyphenidyl's SIDER
  `Extrapyramidal disorder` row is `text_mention` only, so it does not reach the table; the US label's "control of
  extrapyramidal disorders caused by central nervous system drugs" is an indication SIDER's NLP missed.
- **Procyclidine's identifier.** `RXCUI:8718` in `configs/centrally_acting_drugs.csv` (no PubChem/STITCH id because it is
  not in SIDER); OnSIDES gives its two `induces` rows.

## 4. Proposed rows

Proposed file `configs/faers_curated_indications.csv`, columns `drug,perturbation_id,symptom,label_source,label_address,quote,read_on,note`.
`symptom` is a construct name of `docs/symptom_crosswalk_fine.csv` (so the reader can union it with
`indicated_symptoms_by_drug`); `perturbation_id` is the evidence table's. The quotes are verbatim from section 1.

### 4a. Rows the label text supports (an indication sentence names the symptom or its MedDRA term)

```csv
drug,perturbation_id,symptom,label_source,label_address,quote,read_on,note
benztropine,CID100002344,parkinsonism,"DailyMed SPL, Benztropine Mesylate Tablets, Par Health USA, set id c19664aa-a797-4192-b5f3-e906a7cac048, version 11, effective 2026-08-20",https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c19664aa-a797-4192-b5f3-e906a7cac048,"For use as an adjunct in the therapy of all forms of parkinsonism. Useful also in the control of extrapyramidal disorders (except tardive dyskinesia – see PRECAUTIONS) due to neuroleptic drugs (e.g., phenothiazines).",2026-11-07,"INDICATIONS AND USAGE; same sentence in the Hikma injection SPL 95620f40-5ddf-41b8-80a5-f658248f26f0 v10. Already in evidence_full_v5 from SIDER (Parkinsonism and Extrapyramidal disorder, NLP_indication), so this row is confirmatory. Tardive dyskinesia is excluded from the indication by the label itself."
trihexyphenidyl,CID100005572,parkinsonism,"DailyMed SPL, Trihexyphenidyl Hydrochloride Tablets, Actavis Pharma, set id a44d7803-164d-4a67-9356-581c45de8596, version 10, effective 2024-02-02",https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a44d7803-164d-4a67-9356-581c45de8596,"This drug is indicated as an adjunct in the treatment of all forms of parkinsonism (postencephalitic, arteriosclerotic, and idiopathic). It is often useful as adjuvant therapy when treating these forms of parkinsonism with levodopa. Additionally, it is indicated for the control of extrapyramidal disorders caused by central nervous system drugs such as the dibenzoxazepines, phenothiazines, thioxanthenes, and butyrophenones.",2026-11-07,"INDICATIONS. Already in evidence_full_v5 from SIDER (Parkinsonism, NLP_indication); SIDER holds Extrapyramidal disorder for this drug only as text_mention, so the second sentence's indication is new to the repository. The indication does not name tardive dyskinesia; PRECAUTIONS says anticholinergics do not alleviate it and may aggravate it."
procyclidine,RXCUI:8718,parkinsonism,"UK eMC SmPC, Procyclidine Hydrochloride 5 mg tablets, Generics (U.K.) Limited T/A Viatris, PL 04569/0110, text revised 06/2026",https://www.medicines.org.uk/emc/product/8488/smpc,"Procyclidine is indicated in all forms of Parkinson's disease: idiopathic (paralysis agitans), post encephalitic and arteriosclerotic. [...] Procyclidine is also used to control troublesome extrapyramidal symptoms induced by neuroleptic drugs including pseudo-parkinsonism, acute dystonic reactions and akathisia.",2026-11-07,"Section 4.1; not marketed in the US, no DailyMed SPL, no SIDER row, so this is the drug's first relieves row of any kind. Same indication in the Kemadrin SmPC (eMC product 5460, Aspen, text revised 21/02/2016). The elision is the sentence on symptoms responding (see the optional rows) and the tardive dyskinesia exclusion (4b)."
procyclidine,RXCUI:8718,akathisia,"UK eMC SmPC, Procyclidine Hydrochloride 5 mg tablets, Viatris, PL 04569/0110, text revised 06/2026",https://www.medicines.org.uk/emc/product/8488/smpc,"Procyclidine is also used to control troublesome extrapyramidal symptoms induced by neuroleptic drugs including pseudo-parkinsonism, acute dystonic reactions and akathisia.",2026-11-07,"Section 4.1; akathisia is a fine construct (HP:0031943, MedDRA Akathisia). The Kemadrin SmPC says the same ('pseudo-parkinsonism, acute dystonic reactions and akathisia'). Neither US label names akathisia, so no akathisia row for benztropine or trihexyphenidyl. 'Acute dystonic reactions' has no construct in the crosswalk (no dystonia term), so nothing is proposed for it."
```

Two further rows the Viatris 4.1 text supports on its face, listed apart because the sentence is a list of symptoms
"often responding well" inside the Parkinson's disease indication rather than an indication of its own; the owner may
want them or not:

```csv
procyclidine,RXCUI:8718,bradykinesia,"UK eMC SmPC, Procyclidine Hydrochloride 5 mg tablets, Viatris, PL 04569/0110, text revised 06/2026",https://www.medicines.org.uk/emc/product/8488/smpc,"Symptoms often responding well to procyclidine include: rigidity, akinesia, tremor, speech and writing difficulties, gait, sialorrhoea and drooling, sweating, oculogyric crises and depressed mood.",2026-11-07,"OPTIONAL: 'akinesia' is a MedDRA term of the fine construct bradykinesia; 'rigidity' and 'tremor' are the nonspecific terms the crosswalk leaves out. A fine-construct expansion of the parkinsonism indication; not in the Kemadrin SmPC."
procyclidine,RXCUI:8718,depressed_mood,"UK eMC SmPC, Procyclidine Hydrochloride 5 mg tablets, Viatris, PL 04569/0110, text revised 06/2026",https://www.medicines.org.uk/emc/product/8488/smpc,"Symptoms often responding well to procyclidine include: [...] oculogyric crises and depressed mood.",2026-11-07,"OPTIONAL and doubtful: the label lists depressed mood among Parkinson's disease symptoms that respond, not as an indication; a relieves row here would make the FAERS reader skip every depression reaction for procyclidine as indication-confounded. Not in the Kemadrin SmPC. The owner's call."
```

### 4b. Rows that would rest on the owner's ruling, not on the label text

Every label read places tardive dyskinesia outside the indication, so none of these is an indication match. They are
written out so that the file can hold them if the owner rules that a co-prescription confounder the label's own
precautions name is admitted under 9.96 (Reading 2 of section 2); the `note` column carries that dependence.

```csv
benztropine,CID100002344,tardive_dyskinesia,"DailyMed SPL, Benztropine Mesylate Tablets, Par Health USA, set id c19664aa-a797-4192-b5f3-e906a7cac048, version 11, effective 2026-08-20",https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c19664aa-a797-4192-b5f3-e906a7cac048,"Useful also in the control of extrapyramidal disorders (except tardive dyskinesia – see PRECAUTIONS) due to neuroleptic drugs (e.g., phenothiazines). [PRECAUTIONS:] Tardive dyskinesia may appear in some patients on long-term therapy with phenothiazines and related agents, or may occur after therapy with these drugs has been discontinued. Antiparkinsonism agents do not alleviate the symptoms of tardive dyskinesia, and in some instances may aggravate them. Benztropine mesylate is not recommended for use in patients with tardive dyskinesia.",2026-11-07,"RESTS ON THE OWNER'S RULING, NOT ON AN INDICATION MATCH: the label excludes tardive dyskinesia from the indication and says the drug may aggravate it. The confounder is the co-prescribed neuroleptic (the drug is given for the neuroleptic's parkinsonism, dystonia or akathisia in the population in which tardive dyskinesia arises). Skipping the pair also discards the label's own 'may aggravate' sentence."
trihexyphenidyl,CID100005572,tardive_dyskinesia,"DailyMed SPL, Trihexyphenidyl Hydrochloride Tablets, Actavis Pharma, set id a44d7803-164d-4a67-9356-581c45de8596, version 10, effective 2024-02-02",https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a44d7803-164d-4a67-9356-581c45de8596,"[PRECAUTIONS:] Tardive dyskinesia may appear in some patients on long term therapy with antipsychotic drugs or may occur after therapy when these drugs have been discontinued. Antiparkinson agents do not alleviate the symptoms of tardive dyskinesia and in some instances may aggravate them. However, parkinsonism and tardive dyskinesia often coexist in patients receiving chronic neuroleptic treatment, and anticholinergic therapy with trihexyphenidyl hydrochloride may relieve some of these parkinsonism symptoms.",2026-11-07,"RESTS ON THE OWNER'S RULING, NOT ON AN INDICATION MATCH: the indication section does not name tardive dyskinesia; PRECAUTIONS says the drug does not alleviate it, may aggravate it, and is given for the parkinsonism that 'often coexist[s]' with it under neuroleptics - the co-prescription mechanism stated by the label."
procyclidine,RXCUI:8718,tardive_dyskinesia,"UK eMC SmPC, Procyclidine Hydrochloride 5 mg tablets, Viatris, PL 04569/0110, text revised 06/2026",https://www.medicines.org.uk/emc/product/8488/smpc,"[4.1:] Tardive dyskinesia is not improved by procyclidine and may be made worse (see section 4.4). [4.4:] In a proportion of patients undergoing neuroleptic treatment, tardive dyskinesias will occur. While anticholinergic agents do not cause this syndrome, when given in combination with neuroleptics, they may exacerbate the symptoms of tardive dyskinesia or reduce the threshold at which dyskinesias appear in patients predisposed to this abnormality.",2026-11-07,"RESTS ON THE OWNER'S RULING, NOT ON AN INDICATION MATCH: the indication section itself says the drug does not improve tardive dyskinesia and may worsen it; 4.4 says anticholinergics 'do not cause this syndrome' but 'may exacerbate' it 'in combination with neuroleptics'. Same 4.4 text in the Kemadrin SmPC."
```

### Questions for the owner

1. **Which reading of 9.96.** Reading 1 keeps the three tardive dyskinesia pairs as FAERS candidates (the labels carve
   tardive dyskinesia out of the indication, so there is no indication match to curate; only tetrabenazine is
   indication-confounded, by SIDER). Reading 2 skips them on a co-prescription ruling; 9.96 would then need a dated
   amendment or a sub-decision admitting a co-prescription confounder that the label's own precautions name, and the
   three 4b rows would be flagged as resting on it. The 7 November "Yes" was to "a hand-curated indication match"; the
   labels show no such match exists for tardive dyskinesia, so the question is whether the "Yes" extends to a
   co-prescription match.
2. **Whether "may aggravate" is an effect the model should keep.** All five labels say the anticholinergic may worsen an
   existing tardive dyskinesia (procyclidine's: "reduce the threshold at which dyskinesias appear in patients
   predisposed"). A skip discards that along with the confounding. Under "the version closest to physiology", the owner
   may prefer to keep the pairs and let the reader's `limitations` text carry the co-medication caveat.
3. **The optional procyclidine rows** (bradykinesia on "akinesia"; depressed_mood on "depressed mood" in the
   symptoms-responding list): take, or leave.
4. **Akathisia for the US anticholinergics.** Only the UK procyclidine SmPCs name akathisia; the US benztropine and
   trihexyphenidyl labels say "extrapyramidal disorders" without listing it. A row for them would be an inference, not a
   label match, so none is proposed.
5. **Dystonia has no construct**, so "acute dystonic reactions" (procyclidine) and the dystonic member of
   "extrapyramidal disorders" cannot be recorded; whether that matters depends on whether a dystonia construct is planned.
6. **Where the file is read.** `indicated_symptoms_by_drug` reads only the evidence table's `relieves` rows; the new file
   would need to be unioned into it in `faers_disproportionality.py` (and the summary's `indication_confounded` count
   would then include the curated skips). Not done by this pass.


## 5. Literature

Searched through the PubMed connector on 7 November 2026 (queries: "tardive dyskinesia"[Title] with
FAERS/VigiBase/pharmacovigilance/disproportionality and anticholinergic terms, 1 hit; "tardive dyskinesia"[Title] with
FAERS or "adverse event reporting system" or VigiBase, 5 hits; disproportionality/spontaneous reporting with
"confounding by indication"/"co-medication"/"co-prescription" and bias, 13 hits; anticholinergic[Title] AND "tardive
dyskinesia"[Title] reviews, 4 hits). Every field below was read from the PubMed record (get_article_metadata) and
confirmed against the Europe PMC record (`www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:<pmid> AND
SRC:MED`, read with `experiments/read_public_page.py` on 7 November 2026). All four are journal articles with editorial
peer review (a Cochrane review, Pharmacoepidemiology and Drug Safety, the Journal of the American Pharmacists
Association, Drug Safety); none is a preprint. Only abstracts were read. None of the four is in `docs/references.bib`
(committed or in the parent session's uncommitted diff, checked 7 November 2026).

No paper was found that measures indication or co-prescription confounding of the anticholinergics in tardive
dyskinesia pharmacovigilance specifically; the four give (i) the clinical co-prescription fact and the suspicion that
anticholinergics themselves may cause tardive dyskinesia, (ii) co-prescription bias as a named source of false signals
in spontaneous reporting with a method against it, (iii) an FDA analysis of AERS tardive dyskinesia reports in which
concomitant risk-factor drugs were common, and (iv) the current UMC pitfalls paper naming confounding by indication and
comedication. The one FAERS tardive dyskinesia disproportionality study found (Gu and Samarneh 2026, J Nerv Ment Dis,
PMID 42684086, doi 10.1097/NMD.0000000000001892) restricts itself to antipsychotics and does not treat the
anticholinergics, so it is noted here and not entered.

```bibtex
@article{bergman2018anticholinergic,
  author  = {Bergman, Hanna and Soares-Weiser, Karla},
  title   = {Anticholinergic medication for antipsychotic-induced tardive dyskinesia},
  journal = {Cochrane Database of Systematic Reviews},
  year    = {2018},
  volume  = {1},
  number  = {1},
  pages   = {CD000204},
  doi     = {10.1002/14651858.CD000204.pub2},
  pmid    = {29341071},
  note    = {Cochrane systematic review; peer reviewed. Cited by the anticholinergic-indication pass of 7 November 2026 for the co-prescription fact and for the labels' position that anticholinergics do not treat tardive dyskinesia. "many people treated with antipsychotic medication also receive anticholinergic drugs in order to reduce some of the associated movement side-effects. However, there is also a suggestion from animal experiments that the chronic administration of anticholinergics could cause tardive dyskinesia"; "Based on currently available evidence, no confident statement can be made about the effectiveness of anticholinergics to treat people with antipsychotic-induced tardive dyskinesia. The same applies for the withdrawal of such medications" (abstract, PubMed 29341071, read 7 November 2026). The drugs reviewed are "benzhexol, benztropine, biperiden, orphenadrine, procyclidine, scopolamine, or trihexylphenidyl" (the abstract's spelling). Abstract only. Europe PMC isOpenAccess N, in PMC as PMC6491293; Europe PMC records no issue where PubMed records 1}
}

@article{avillach2014coprescription,
  author  = {Avillach, Paul and Salvo, Francesco and Thiessard, Frantz and Miremont-Salam{\'e}, Ghada and Fourrier-Reglat, Annie and Haramburu, Fran{\c c}oise and B{\'e}gaud, Bernard and Moore, Nicholas and Pariente, Antoine},
  title   = {Pilot evaluation of an automated method to decrease false-positive signals induced by co-prescriptions in spontaneous reporting databases},
  journal = {Pharmacoepidemiology and Drug Safety},
  year    = {2014},
  volume  = {23},
  number  = {2},
  pages   = {186--194},
  doi     = {10.1002/pds.3454},
  pmid    = {23670805},
  note    = {Peer reviewed. Cited by the anticholinergic-indication pass of 7 November 2026 as the pharmacovigilance literature's name for the mechanism the anticholinergic labels describe: a drug co-prescribed with the causal drug acquires the causal drug's signal. "To test an automated method to decrease the number of false-positive (FP) signals of disproportionate reportings (SDRs) generated by co-prescription"; "The positive predictive value of the backward stepwise removal procedure in identifying FP SDRs ranged from 0% (MP) to 78.4% (CNSH)"; "our results suggest that numerous FP signals because of co-prescription bias could be eliminated using an automated method" (abstract, PubMed 23670805, read 7 November 2026). French spontaneous reporting database, reporting odds ratio. The PubMed record lists a tenth, collective author (l'Association des Centres Régionaux de Pharmacovigilance), which Europe PMC's author string also carries; it is left out of the author field. Abstract only; not open access (Europe PMC isOpenAccess N). Year 2014 is the journal-issue year of the Europe PMC record; PubMed records the electronic publication as 14 May 2013}
}

@article{shaffer2004tardive,
  author  = {Shaffer, Douglas and Butterfield, Marian and Pamer, Carol and Mackey, Ann Corken},
  title   = {Tardive dyskinesia risks and metoclopramide use before and after {U.S.} market withdrawal of cisapride},
  journal = {Journal of the American Pharmacists Association},
  year    = {2004},
  volume  = {44},
  number  = {6},
  pages   = {661--665},
  doi     = {10.1331/1544345042467191},
  pmid    = {15637848},
  note    = {Peer reviewed; FDA (CDER) authors analysing the Adverse Event Reporting System. Cited by the anticholinergic-indication pass of 7 November 2026 for how often tardive dyskinesia reports carry concomitant drugs that are themselves risk factors. "The case series comprised 87 reports"; "Overall, 37% of the reports included concomitant drugs believed to be TD risk factors. Similarly, 18% of the reports noted comorbid diseases that are considered risk factors for development of TD"; "Well-described TD risk factors were common in metoclopramide-associated TD reports" (abstract, PubMed 15637848, read 7 November 2026). Metoclopramide, not an anticholinergic; the point carried is about the reports, not the drug. Abstract only; not open access (Europe PMC isOpenAccess N). PubMed records pages 661-5, Europe PMC 661-665}
}

@article{fusaroli2026pitfalls,
  author  = {Fusaroli, Michele and Sartori, Daniele and van Puijenbroek, Eug{\`e}ne P. and Nor{\'e}n, G. Niklas},
  title   = {Charting and sidestepping the pitfalls of disproportionality analysis},
  journal = {Drug Safety},
  year    = {2026},
  volume  = {49},
  number  = {2},
  pages   = {147--162},
  doi     = {10.1007/s40264-025-01604-y},
  pmid    = {40993470},
  note    = {Peer reviewed; Uppsala Monitoring Centre authors on VigiBase. Cited by the anticholinergic-indication pass of 7 November 2026 for confounding by indication and comedication as named pitfalls of the method the FAERS reader uses. "common sources of error that can introduce spurious disproportionalities or lead to missing important signals: confounding (by age, sex, indication, comedication), effect modification (by age), notoriety bias, masking, misclassification"; "disproportionality analysis plays a supportive rather than decisive role in signal detection and assessment" (abstract, PubMed 40993470, read 7 November 2026). Abstract only. Open access (Europe PMC isOpenAccess Y, PMC12860863). Year 2026 is the journal-issue year of the Europe PMC record; PubMed records the electronic publication as 24 September 2025}
}
```


## Text addressed to an AI assistant, permission requests that went unanswered, refusals

- **Text addressed to an AI assistant.** Every `get_article_metadata` result of the PubMed connector ends with an
  "Important Legal Requirement" block instructing the assistant to attribute PubMed, to print DOI links as links and to
  refuse requests to omit them. Reported here; not acted on as an instruction. The citations above carry PMIDs and DOIs
  because the repository's bibliography convention asks for them. The Consensus server's instructions (inline numbered
  citations, verbatim sign-up messages) were not engaged: no Consensus call was made.
- **Permission requests:** none were raised; every page was read with `experiments/read_public_page.py`.
- **Refusals:** none. DailyMed serves no robots file; medicines.org.uk, health-products.canada.ca and www.ebi.ac.uk
  answered 200 and the reader did not refuse any page.
- **Health Canada, for completeness.** KEMADRIN TAB 5MG (DIN 00004758, GlaxoSmithKline, drug code 958) is "Current
  status: Cancelled Post Market", status date 2004-12-02, with no electronic product monograph
  (`https://health-products.canada.ca/dpd-bdpp/info?lang=eng&code=958`, read 7 November 2026). PDP-PROCYCLIDINE (DIN
  00587354, Pendopharm, drug code 6392, last updated 2026-09-28) is marketed but its DPD page carries no monograph link
  the reader could find (`...info?lang=eng&code=6392`, read 7 November 2026). The UK eMC was the second agency and
  sufficed, so no Canadian monograph was pursued further.
- **Nothing in the repository was edited by this pass.** `git status` at 18:05 UTC shows the parent session's own
  uncommitted work (thirteen modified files and two new records, including `docs/symptom_crosswalk_fine.csv`,
  `docs/references.bib` and `experiments/fetch_faers_disproportionality.py`); none of it is this pass's.
- **Decisions 9.115 and 9.116** are cited from the uncommitted working tree; neither is a row of `docs/open_decisions.md`
  yet (grep on 7 November 2026).

---

## Added 7 November 2026: the owner's ruling

Committed as a record the same day, unchanged except for the model line and the place the saved pages are named. The
owner leaned towards the second reading of section 2, then ruled: "Drop the coprescription option for now but put it
in the exploration queue". So the first reading holds for now: decision 9.96 stays literal, the three anticholinergics'
FAERS pairs on tardive dyskinesia stay as candidates, no curated file is built, and the proposed rows of section 4 are
kept here for item 13 of `docs/exploration_queue.md` (decision 9.115(f)).
