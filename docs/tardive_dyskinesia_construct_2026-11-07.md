# Scoping tardive dyskinesia as a fine symptom construct

Research pass, 7 November 2026. Rules: CLAUDE.md of `/home/user/perturbation-symptom-modules`.
Model: Fable throughout; no fallback occurred.

**This document rules nothing and changes nothing in the repository.** It was written as a draft for the owner and is
committed as a record on 7 November 2026, after the owner's rulings (decisions 9.115 and 9.116), unchanged except for
this paragraph, the model lines and the place the saved pages are named; the rulings and what was built are in the
dated addition at the end. No row was applied by the pass itself.

Measurements carry their graph and table versions, per the rule of 21 October 2026. The evidence tables are
`data/processed/evidence_full_v5` and `data/processed/label_selection/better_v2_full_v5.parquet` (both built
5 November 2026); the graph is `data/processed/graph_full_neuronal_split_binders_drugs_v5`; HPO is
`data/raw/hpo/hp.obo`, `data-version: hp/releases/2026-09-01`; OnSIDES is v3.1.1; SIDER is 4.1. Measured
7 November 2026.

---

## 1. Ontology

### 1.1 What HPO holds

Read from `data/raw/hpo/hp.obo` (`data-version: hp/releases/2026-09-01`), quoted verbatim.

| HPO id | name | is_a parent(s), as hp.obo gives them | definition / comment, quoted | descendants (term included) |
| --- | --- | --- | --- | --- |
| **HP:0040141** | **Tardive dyskinesia** | `is_a: HP:0100660 ! Dyskinesia` — one parent only | no `def:`; `comment: the involuntary movements are tardive, meaning they have a slow or belated onset` | **1 (a leaf; no synonyms)** |
| HP:0100660 | Dyskinesia | `is_a: HP:0100022 ! Abnormality of movement` | `def: "A movement disorder which consists of effects including diminished voluntary movements and the presence of involuntary movements."`; synonyms `"Disorder of involuntary muscle movements"`, `"Dyskinesias"`, `"Dyskinesis"` | 4 |
| HP:0002310 | Orofacial dyskinesia | `is_a: HP:0100660 ! Dyskinesia` | no `def:`; synonym `"Orofacial dyskinesias"` | 1 (leaf) |
| HP:0007308 | Extrapyramidal dyskinesia | `is_a: HP:0002071 ! Abnormality of extrapyramidal motor function`, `is_a: HP:0100660 ! Dyskinesia` | no `def:`, no synonyms | 1 (leaf) |
| HP:0002072 | Chorea | `is_a: HP:0004305 ! Involuntary movements` | `def: "Chorea (Greek for 'dance') refers to widespread arrhythmic involuntary movements of a forcible, jerky and restless fashion. ... Chorea can involve the trunk, neck, face, tongue, and extremities."` | 4 |
| HP:0002305 | Athetosis | `is_a: HP:0004305 ! Involuntary movements` | `def: "A slow, continuous, involuntary writhing movement that prevents maintenance of a stable posture. ... In contrast to chorea, in athetosis, the same regions of the body are repeatedly involved."` | 1 (leaf) |
| HP:0001266 | Choreoathetosis | `is_a: HP:0002072 ! Chorea`, `is_a: HP:0002305 ! Athetosis` | `def: "Involuntary movements characterized by both athetosis (inability to sustain muscles in a fixed position) and chorea (widespread jerky arrhythmic movements)."` | 3 |
| HP:0001332 | Dystonia | `is_a: HP:0100022 ! Abnormality of movement` | `def: "An abnormally increased muscular tone that causes fixed abnormal postures. There is a slow, intermittent twisting motion ..."` | 20 |
| HP:0002487 | Hyperkinetic movements | `is_a: HP:0100022 ! Abnormality of movement` | `def: "Motor hyperactivity with excessive movement of muscles of the body as a whole."`; synonyms `"Hyperkinesia"`, `"Hyperkinesis"` | 1 (leaf) |
| HP:0004305 | Involuntary movements | `is_a: HP:0011442 ! Abnormal central motor function`, `is_a: HP:0100022 ! Abnormality of movement` | `def: "Involuntary contractions of muscle leading to involuntary movements of extremities, neck, trunk, or face."` | 57 |
| HP:0031943 | Akathisia (already a construct, decision 9.74) | `is_a: HP:0000711 ! Restlessness`, `is_a: HP:0004305 ! Involuntary movements` | `def: "A state of motor restlessness, usually in the lower extremities, that is often but not always accompanied by a subjective sense of inner restlessness, an urge to move, and anxiety or dysphoria."` | 1 (leaf) |

**Answer to "is tardive dyskinesia its own root or does it sit under a chorea/dyskinesia root?"** It sits under a
**dyskinesia** root, not a chorea root. Its full ancestor chain in hp.obo is

`HP:0040141 → HP:0100660 Dyskinesia → HP:0100022 Abnormality of movement → HP:0012638 Abnormal nervous system physiology → HP:0000707 Abnormality of the nervous system → HP:0000118 Phenotypic abnormality → HP:0000001 All`.

HPO does **not** put Tardive dyskinesia under Chorea, Athetosis, Choreoathetosis, Hyperkinetic movements or
Involuntary movements, even though the clinical phenomenology is choreiform. The `HP:0100660 Dyskinesia` root is
unusually tight: its whole expansion is **4 terms** — itself, Orofacial dyskinesia, Extrapyramidal dyskinesia,
Tardive dyskinesia. This is the same situation the parkinsonism row records for its own root ("HPO: Parkinsonism
expands to 2 terms only").

**HPO holds no term for tardive dystonia.** A `grep` of `name:` lines in hp.obo for `tardive` returns one hit,
HP:0040141. So "tardive dystonia" cannot be a construct from HPO; the only dystonia terms are the phenomenological
ones (HP:0001332 Dystonia and its 19 descendants, including HP:0012048 Oromandibular dystonia and HP:0000643
Blepharospasm), none of which is drug-specific or delayed.

**Second source for the HPO ids** (CLAUDE.md, "a failed source is not a finished search"; here the first source did
not fail, but the ids are load-bearing so they were confirmed independently). EMBL-EBI OLS4 REST API, read
7 November 2026 with `experiments/read_public_page.py` (`www.ebi.ac.uk` keeps its own robots rules and allowed the
read; this is *not* the `ftp.ebi.ac.uk` exception):
`https://www.ebi.ac.uk/ols4/api/ontologies/hp/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FHP_0040141`
returned `"obo_id": "HP:0040141"`, `"label": "Tardive dyskinesia"`, `"description": ["the involuntary movements are
tardive, meaning they have a slow or belated onset"]`, `"synonyms": []`, `"is_obsolete": false`. Matches hp.obo
exactly, including the absence of synonyms.

### 1.2 Tardive dyskinesia distinguished from acute dystonia and from akathisia

The three are separate entities in HPO, SNOMED CT and ICD-10-CM, and each separation was verified.

**HPO.** Akathisia (HP:0031943) descends from Restlessness and Involuntary movements; Tardive dyskinesia
(HP:0040141) descends from Dyskinesia. Checked programmatically on hp.obo: `HP:0031943 in descendants_of('HP:0040141')`
is **False**, and HP:0040141 is in the expansion of none of the parkinsonism roots (HP:0001300, HP:0002067,
HP:0002322, HP:0025387, HP:0002396, HP:0007076), nor of HP:0000752 Hyperactivity, HP:0000713 Agitation or
HP:0000711 Restlessness. HPO has no term for acute dystonic reaction at all; the nearest is the untimed
HP:0001332 Dystonia.

**SNOMED CT** (`snomedct`, branch MAIN, read 7 November 2026 through the SNOMED terminology service). Searching
"tardive dyskinesia" returns, among 20 hits: `102449007` PT "Tardive dyskinesia", FSN `"Tardive dyskinesia
(disorder)"`, active, definition status PRIMITIVE; `38941006` FSN `"Neuroleptic-induced tardive dyskinesia
(disorder)"`; `1259642009` FSN `"Chorea due to tardive dyskinesia (disorder)"`. The **direct parent** of
`102449007` is `98811000119103` "Subacute dyskinesia caused by drug" — so SNOMED, unlike HPO, puts tardive
dyskinesia under a *drug-caused* parent, not under a phenomenological dyskinesia parent.

**ICD-10-CM** FY2027 code set, read 7 November 2026. The three are three distinct billable codes under two
different categories:

| code | long description, quoted | the entity |
| --- | --- | --- |
| `G24.01` | "Drug induced subacute dyskinesia" | tardive dyskinesia |
| `G24.02` | "Drug induced acute dystonia" | the acute dystonic reaction — a different syndrome |
| `G25.71` | "Drug induced akathisia" | akathisia, already its own construct (9.74) |
| `G24.09` | "Other drug induced dystonia" | — |
| `G25.70` | "Drug induced movement disorder, unspecified" | the undifferentiated parent |
| `G25.79` | "Other drug induced movement disorders" | — |

Three agencies' vocabularies therefore agree that tardive dyskinesia, acute dystonia and akathisia are three
things. Under decision 9.58 ("constructs go to the finest level the sources support") that is three constructs,
of which akathisia already exists.

### 1.3 MedDRA preferred terms a label would use

The project holds two MedDRA vocabularies. Both were read directly; MedDRA itself is licence-restricted and was
not fetched.

**OnSIDES v3.1.1** `vocab_meddra_adverse_effect.parquet` (6,423 rows). The terms in this family, with the term type
OnSIDES records:

| meddra_id | meddra_name | term type |
| --- | --- | --- |
| 10043118 | **Tardive dyskinesia** | **PT** |
| 10013916 | Dyskinesia | PT |
| 10030976 | Oral dyskinesia | LLT |
| 10013983 | Dystonia | PT |
| 10013986 | Dystonic reaction | LLT |
| 10066608 | Acute dystonia | LLT |
| 10008754 | Choreoathetosis | PT |
| 10008748 | Chorea | PT |
| 10042732 | Sydenham's chorea | PT |
| 10003620 | Athetosis | PT |
| 10020651 | Hyperkinesia | PT |
| 10020653 | Hyperkinesis | LLT |
| 10028293 | Muscle contractions involuntary | PT |
| 10028041 | Movements involuntary | LLT |
| 10022898 | Involuntary muscle movement | LLT |
| 10067954 | Oromandibular dystonia | PT |
| 10005159 | Blepharospasm | PT |
| 10044074 | Torticollis | PT |
| 10044684 | Trismus | PT |
| 10037076 | Protrusion tongue | PT |
| 10043963 | Tongue movement disturbance | PT |
| 10006514 | Bruxism | PT |
| 10061991 | Grimacing | PT |
| 10028622 | Myoclonus | PT |

**SIDER 4.1** `meddra_all_se.tsv.gz`, distinct PT names (4,251 in all). The family is present as:
`Tardive dyskinesia`, `Dyskinesia`, `Choreoathetosis`, `Chorea`, `Athetosis`, `Hyperkinesia`, `Dystonia`,
`Oromandibular dystonia`, `Blepharospasm`, `Torticollis`, `Trismus`, `Bruxism`, `Myoclonus`, `Grimacing`,
`Protrusion tongue`, `Muscle contractions involuntary`.

**Neither vocabulary holds a PT "Orofacial dyskinesia" or any term containing "tardive dystonia".** OnSIDES holds
only the LLT "Oral dyskinesia", and SIDER's LLT→PT pairing (`sider_lower_level_to_preferred_terms`) maps
`'oral dyskinesia'` to **no** preferred term, so OnSIDES' Oral dyskinesia rows cannot reach any construct through
the registered route. That is a gap, recorded in §6 as a sub-choice, not a blocker.

**What the builder would actually assign.** Running `complete_addition` from
`experiments/build_fine_symptom_crosswalk.py` against hp.obo and SIDER's PT list, for each candidate root:

| candidate root | hpo_names the builder writes | MedDRA PTs the builder matches |
| --- | --- | --- |
| **HP:0040141** | Tardive dyskinesia | **`Tardive dyskinesia`** — exactly one |
| HP:0100660 | Dyskinesia | `Dyskinesia;Tardive dyskinesia` |
| HP:0002310 | Orofacial dyskinesia | *(none)* |
| HP:0007308 | Extrapyramidal dyskinesia | *(none)* |
| HP:0002487 | Hyperkinetic movements | `Hyperkinesia` |
| HP:0002072 | Chorea | `Chorea;Choreoathetosis` |
| HP:0001266 | Choreoathetosis | `Choreoathetosis` |
| HP:0001332 | Dystonia | `Blepharospasm;Dystonia;Oculogyric crisis;Oromandibular dystonia;Spasmodic dysphonia;Torticollis` |

The last row is the warning. A Dystonia root pulls in **Oculogyric crisis** and, through SIDER's LLT pairing, the
OnSIDES lower-level terms **`Acute dystonia`** and **`Dystonic reaction`** (both pair to the PT `dystonia`, checked
7 November 2026). An addition rooted at HP:0001332 would therefore fuse the acute dystonic reaction — onset in
hours to days, reversible — into a construct meant for the delayed, often irreversible one. Under 9.58 that is a
merge supplied as an input, which the decision forbids.

### 1.4 MeSH descriptor

Read from the NLM MeSH RDF service with `experiments/read_public_page.py`, 7 November 2026 (`id.nlm.nih.gov`
served both requests, status 200; the pages were saved with their SHA-256 in the pass's working directory, which is not kept).

`https://id.nlm.nih.gov/mesh/lookup/descriptor?label=Tardive%20Dyskinesia&match=exact&limit=10` returned, verbatim:

```
[{"resource":"http://id.nlm.nih.gov/mesh/D000071057","label":"Tardive Dyskinesia"}]
```

`https://id.nlm.nih.gov/mesh/D000071057.json` (served as N-Triples) gave, verbatim:

```
<http://id.nlm.nih.gov/mesh/D000071057> <http://www.w3.org/2000/01/rdf-schema#label> "Tardive Dyskinesia"@en .
<http://id.nlm.nih.gov/mesh/D000071057> <http://id.nlm.nih.gov/mesh/vocab#treeNumber> <http://id.nlm.nih.gov/mesh/C23.888.592.350.275.500> .
<http://id.nlm.nih.gov/mesh/D000071057> <http://id.nlm.nih.gov/mesh/vocab#treeNumber> <http://id.nlm.nih.gov/mesh/C10.228.662.262.500.500> .
<http://id.nlm.nih.gov/mesh/D000071057> <http://id.nlm.nih.gov/mesh/vocab#treeNumber> <http://id.nlm.nih.gov/mesh/C10.597.350.275.500> .
```

And its parent, `https://id.nlm.nih.gov/mesh/D004409.json`:

```
<http://id.nlm.nih.gov/mesh/D004409> <http://www.w3.org/2000/01/rdf-schema#label> "Dyskinesia, Drug-Induced"@en .
<http://id.nlm.nih.gov/mesh/D004409> <http://id.nlm.nih.gov/mesh/vocab#treeNumber> <http://id.nlm.nih.gov/mesh/C23.888.592.350.275> .
<http://id.nlm.nih.gov/mesh/D004409> <http://id.nlm.nih.gov/mesh/vocab#treeNumber> <http://id.nlm.nih.gov/mesh/C10.597.350.275> .
<http://id.nlm.nih.gov/mesh/D004409> <http://id.nlm.nih.gov/mesh/vocab#treeNumber> <http://id.nlm.nih.gov/mesh/C10.228.662.262.500> .
<http://id.nlm.nih.gov/mesh/D004409> <http://id.nlm.nih.gov/mesh/vocab#treeNumber> <http://id.nlm.nih.gov/mesh/C10.720.312> .
<http://id.nlm.nih.gov/mesh/D004409> <http://id.nlm.nih.gov/mesh/vocab#treeNumber> <http://id.nlm.nih.gov/mesh/C25.100.750> .
<http://id.nlm.nih.gov/mesh/D004409> <http://id.nlm.nih.gov/mesh/vocab#treeNumber> <http://id.nlm.nih.gov/mesh/C25.723.705.200> .
```

So **D000071057 Tardive Dyskinesia** is a direct child of **D004409 Dyskinesia, Drug-Induced**
(`C23.888.592.350.275` → `...275.500`). Against the tree prefixes that
`experiments/verify_mesh_symptom_descriptors.py` uses, `C23.888` and `C10.597` are symptom branches and `C10.228`
is a diagnosis branch, so the descriptor sits in both — predominantly symptom (two of three branches). This matters
because the literature class E3 has a channel only where a MeSH descriptor is assigned; parkinsonism has none
("No MeSH descriptor is assigned yet, so the literature class E3 has no channel for this symptom until one is
verified; it is left empty rather than guessed" — the parkinsonism row of `docs/symptom_crosswalk.csv`), whereas
tardive dyskinesia *does* have an exact descriptor. I have **not** run
`experiments/verify_mesh_symptom_descriptors.py`, so the PubTator3 vocabulary-membership half of the check is
outstanding; the proposed note says so, following the `intellectual_disability` precedent.

**MeSH is the one vocabulary of the four that supplies a ready-made broader drug-induced-hyperkinesia root**
(D004409). HPO does not; its parent, HP:0100660 Dyskinesia, is not drug-specific.

---

## 2. Evidence held

Engineering run with pandas on the current tables; the interpretation below is this pass's. Perturbation matching
to SIDER and OnSIDES was done by lower-cased drug name against the 230 drug perturbation labels of
`evidence_full_v5`, not through the project's full identifier bridge, so the drug counts are **estimates within
about one or two drugs**, not pipeline output. The OnSIDES figures do go through the project's own
`aggregate_label_statements` and `sider_lower_level_to_preferred_terms`, and the qualifying-ingredient set was
taken from `data/processed/onsides_v5/onsides_reports.parquet` where `qualifies` is true (197 ingredients).

### 2.1 Where the construct would stand

`evidence_full_v5` holds **9,414 records over 39 constructs**, 6,433 gene and 2,981 drug; grades are
monogenic A 5,456 / monogenic C 977 / pharmacological B 2,981. Drug sources in the records table are SIDER 4.1
(1,567) and OnSIDES-label (1,414) only; FAERS and the clinical-trial tables are separate report tables that feed
the reliability fit and the priors, not the label pairs.

### 2.2 By source, for a construct rooted at HP:0040141 (MedDRA PT `Tardive dyskinesia`)

| source | class / grade | what it would carry | detail |
| --- | --- | --- | --- |
| **HPO `genes_to_phenotype`** | monogenic, A and C | **0 gene pairs** | HP:0040141 has **0 annotation rows and 0 genes** in `data/raw/hpo/genes_to_phenotype.txt` (333,983 rows). It is a leaf, so descendant expansion adds nothing. For comparison on the same file: HP:0100660 Dyskinesia 227 rows / 201 genes (268 / 223 with its 3 descendants), HP:0002310 Orofacial dyskinesia 34 / 30, HP:0007308 Extrapyramidal dyskinesia 7 / 7, HP:0002072 Chorea 234 / 190, HP:0001332 Dystonia 654 / 462. |
| **SIDER 4.1 labels** | pharmacological, B, `induces` | **35 drug pairs** | 41 SIDER drugs carry the PT; 35 are among the 230 study perturbations. The 6 that are not: metoclopramide, promethazine, propericiazine, zuclopenthixol, and the brand rows Vallergan and Zyprexa. |
| **OnSIDES v3.1.1 labels** | pharmacological, B, `induces` | **26 drug pairs** | 33 ingredients carry the PT across 49 deduplicated label statements; 26 of those ingredients qualify in v5 and map to 26 perturbations. Sections: NA 21, WP (warnings and precautions) 14, AR (adverse reactions) 5. Countries: US 19, EU 7, UK 7, JP 7. Seven ingredients with a TD statement do not qualify as v5 perturbations: **metoclopramide**, zuclopenthixol, flupenthixol, trimeprazine, methotrimeprazine, samidorphan, obinutuzumab. |
| **union of the two label sources** | B | **43 drug pairs** | 18 in both, 17 SIDER-only, 8 OnSIDES-only. |
| **SIDER indications** | pharmacological, B, `relieves` | **1 pair — tetrabenazine** | See §3.3. |
| **FAERS (openFDA)** | human_association, **C, never a label** | 28 of the 230 drugs | See §2.4. |
| **ClinicalTrials.gov adverse events** | human_association, C | 14 arm-level TD rows over 14 trials, 5 drugs | See §2.5. |
| **ClinicalTrials.gov outcomes (AIMS)** | human_association, C | ≈20 drugs with AIMS outcome measures | See §2.6. |
| **IMPC / mouse** | — | **none** | `data/raw/mgi/mp.obo` has no term whose name contains "tardive"; the nearest are `abnormal involuntary movement` and `dystonia`. `fine_impc_rows` gives an added construct a `validity: none` row automatically, which is correct here. |
| **Literature (E3, MeSH)** | soft prior only | a channel exists | D000071057 is an exact descriptor (§1.4); whether PubTator3/CTD annotate to it is untested. |

### 2.3 The label-source drugs, named

**In both SIDER and OnSIDES (18):** amoxapine, aripiprazole, asenapine, clozapine, doxepin, fluoxetine,
fluphenazine, haloperidol, loxapine, lurasidone, olanzapine, paliperidone, perphenazine, pimozide,
prochlorperazine, quetiapine, risperidone, venlafaxine.

**SIDER only (17):** amisulpride, amitriptyline, bupropion, chlorpromazine, citalopram, clomipramine, deprenyl,
droperidol, fluvoxamine, memantine, modafinil, thioridazine, thiothixene, trazodone, valproate, ziprasidone,
zolmitriptan.

**OnSIDES only (8):** benperidol, brexpiprazole, cariprazine, iloperidone, lumateperone, molindone,
trifluoperazine, zolpidem.

The expected inducers are all present and they dominate: the typical D2 antagonists (haloperidol, chlorpromazine,
fluphenazine, perphenazine, thioridazine, thiothixene, trifluoperazine, pimozide, droperidol, benperidol,
loxapine, molindone), the D2-antagonist antiemetic prochlorperazine, and the atypicals (olanzapine, risperidone,
paliperidone, quetiapine, clozapine, aripiprazole, brexpiprazole, cariprazine, asenapine, lurasidone, iloperidone,
lumateperone, amisulpride, ziprasidone). The remainder are antidepressants (amoxapine, amitriptyline,
clomipramine, doxepin, fluoxetine, fluvoxamine, citalopram, venlafaxine, trazodone, bupropion) and a short tail
(memantine, modafinil, valproate, deprenyl, zolmitriptan, zolpidem).

### 2.4 FAERS

`data/raw/faers/*.json` holds, per drug, the **top 100 reactions only** (`listed_reactions: 100` with
`smallest_listed_count`), so a term appears only if it is in that drug's top 100. `TARDIVE DYSKINESIA` is, for
**28 of the 230 drugs**, with report counts against each drug's total:

aripiprazole 2905/123305, risperidone 909/75400, olanzapine 653/69867, brexpiprazole 603/16890, cariprazine
392/9636, haloperidol 380/24482, paliperidone 340/23466, lumateperone 217/7706, **benztropine 184/7430**,
**tetrabenazine 163/7327**, chlorpromazine 110/6280, perphenazine 101/2087, **procyclidine 84/1813**, ziprasidone
76/3603, **trihexyphenidyl 70/2460**, fluvoxamine 53/3886, loxapine 53/3966, thioridazine 42/624, lurasidone
41/2618, fluphenazine 36/1473, trifluoperazine 26/736, daridorexant 25/2777, iloperidone 24/1476, vilazodone
21/870, pimozide 12/482, propoxyphene 10/477, thiothixene 10/217, tiagabine 3/247.

Two cautions, both of them the loader's own documented biases rather than new ones. (a) The five drugs in bold are
**confounded by indication in the direction that inverts the sign**: benztropine, procyclidine and trihexyphenidyl
are anticholinergics given *for* drug-induced movement disorders, and tetrabenazine is a VMAT2 inhibitor given *for*
tardive dyskinesia. The loader's docstring already names this bias ("confounding by indication (an antidepressant's
'depression' reports)"), and decision 9.96 accepts exactly one correction, "the removal of labels that match the
drug's own indication". For tetrabenazine, SIDER's indication table supplies that match (§3.3); for the three
anticholinergics it does not, so the owner would have to decide whether a hand-curated indication match is admitted.
(b) **FAERS cannot be computed for this construct as the data stand**: `data/raw/faers/_background.json` holds
`reaction_totals` for only **95** reactions — the terms of the *current* crosswalk — and `TARDIVE DYSKINESIA` is not
among them (`AKATHISIA` 13658 and `PARKINSONISM` 9761 are). A disproportionality statistic needs the background
reaction total, so adding the construct requires one further openFDA background query and a refetch. Engineering,
small, but it must happen before any FAERS number for TD is quoted.

### 2.5 ClinicalTrials.gov adverse events

`data/raw/clinicaltrials/*.json` carries MedDRA-coded adverse-event tables with per-arm `numAffected` and
`numAtRisk`, so these are genuine placebo-controlled counts rather than spontaneous reports. Rows whose `term`
begins "Tardive"/"tardive", by drug (rows, distinct trials): risperidone (7, 7), lurasidone (3, 3), paliperidone
(2, 2), aripiprazole (1, 1), cocaine (1, 1) — **14 rows over 14 trials, 5 drugs**. One row carries the note
`"Early signs of mild tardive dyskinesia"` and several carry
`"assessmentType": "SYSTEMATIC_ASSESSMENT"`, which the report schema already records as
`symptom_systematically_assessed`. The cocaine row should be read as a trial population finding rather than a
cocaine effect and is worth a look before it is used.

### 2.6 ClinicalTrials.gov outcomes — the AIMS channel, and a homonym trap

This is the most interesting unused evidence. The **Abnormal Involuntary Movement Scale (AIMS)** is the standard
instrument for tardive dyskinesia, and `data/raw/clinicaltrials_outcomes/*.json` carries AIMS outcome measures,
with baseline-to-endpoint change scores by arm, for roughly **20 study drugs**: amphetamine, aripiprazole,
asenapine, brexpiprazole, bupropion, citalopram, clozapine, fluoxetine, galantamine, haloperidol, lamotrigine,
levodopa, lisdexamfetamine, lumateperone, lurasidone, modafinil, olanzapine, paliperidone, quetiapine,
risperidone, valproate, varenicline, ziprasidone. Example titles, verbatim: `"Change From Baseline in Abnormal
Involuntary Movement Scale (AIMS) Total Score"`, `"Adjusted Mean Change From Baseline in AIMS Item 8 During Phase
3"`, `"AIMS Global Severity Score"`. `configs/trial_outcome_scale_crosswalk.csv` has **no AIMS row**, so none of
this reaches the model today; `docs/clinical_trial_outcome_reports.parquet` holds 317 rows over 17 constructs and
TD is not one of them.

**The trap.** About 25 other drugs — the anaesthetics, local anaesthetics and opioids (alfentanil, articaine,
bupivacaine, chloroprocaine, desflurane, diphenhydramine, droperidol, fentanyl, haloperidol, hydromorphone,
isoflurane, ketamine, lidocaine, meperidine, mepivacaine, methadone, morphine, oxycodone, oxymorphone, prilocaine,
procaine, propofol, remifentanil, ropivacaine, scopolamine, sevoflurane, sufentanil, tetracaine) — carry the
outcome title `"Anesthesia Information Management System (AIMS)"`, a completely different AIMS. A pattern matching
`\bAIMS\b` alone would silently manufacture tardive-dyskinesia outcomes for two dozen anaesthetics. Any row added
to `configs/trial_outcome_scale_crosswalk.csv` must match `Abnormal Involuntary Movement` (and may match
`\bAIMS\b` only in conjunction with it), and `levodopa`'s AIMS rows are about levodopa-induced dyskinesia, not
tardive dyskinesia, so they would need separating too. Flagged; not resolved.

### 2.7 Kept pairs under `better_v2_full_v5`

The registered rule (`experiments/build_label_selection.py`): a drug pair is kept when its maximum label frequency
is at least 0.01, else when it is listed by **both** SIDER and OnSIDES; otherwise it is set aside. A gene pair needs
frequency at least 0.3.

SIDER's `meddra_freq.tsv.gz` carries a frequency row for the PT `Tardive dyskinesia` on 16 of the 35 SIDER drugs.
All but four are the word-coded bands that fall below 0.01 (`postmarketing` 0–0.001, `rare` 0–0.001, `very rare`
0–0.0001). Four reach 0.01 at the band's upper bound: amisulpride (`uncommon`, 0.001–0.01), olanzapine
(`infrequent`, 0.001–0.01), quetiapine (`infrequent`), ziprasidone (`uncommon`); risperidone has an explicit
`1%` row.

**Estimated kept pairs: 20 drug, 0 gene, 20 in all.**

| kept (20) | reason |
| --- | --- |
| amoxapine, aripiprazole, asenapine, clozapine, doxepin, fluoxetine, fluphenazine, haloperidol, loxapine, lurasidone, paliperidone, perphenazine, pimozide, prochlorperazine, venlafaxine | listed by both SIDER and OnSIDES |
| amisulpride, olanzapine, quetiapine, risperidone, ziprasidone | frequency 0.010, at least 0.01 |

**Set aside (23):** amitriptyline, benperidol, brexpiprazole, bupropion, cariprazine, chlorpromazine, citalopram,
clomipramine, deprenyl, droperidol, fluvoxamine, iloperidone, lumateperone, memantine, modafinil, molindone,
thioridazine, thiothixene, trazodone, trifluoperazine, valproate, zolmitriptan, zolpidem.

Chlorpromazine and thioridazine being set aside is an artefact worth noting: both are archetypal TD inducers, but
SIDER is their only source and its band is `postmarketing`. The placebo-arm comparison step
(`placebo_arm_comparisons`, which set aside 70 pairs elsewhere in v5) was **not** run for this estimate, so 20 is
an upper bound on the kept count by at most a few pairs.

**Where that places the construct.** Against `better_v2_full_v5`'s own `kept_by_symptom`, a construct with 43 pairs
and ~20 kept would sit between cogwheel_rigidity (46 pairs / 20 kept) and akathisia (62 / 32), above
restlessness (62 / 14), extrapyramidal_muscular_rigidity (10 / 10), psychomotor_retardation (17 / 4),
pill_rolling_tremor (8 / 3), catatonia (14 / 1), bulimia (9 / 2), abulia (4 / 2) and anhedonia (1 / 0). It would
be a **drug-only construct**, which is the same shape as akathisia (62 pairs, 61 drugs, 1 gene — the measurement
in decision 9.74), and the precedent for accepting that shape is 9.74's own ruling.

---

## 3. Scope and sign

### 3.1 One construct or several?

**One, rooted at HP:0040141, is what the sources support.** The reasoning, decision by decision rather than by
analogy (CLAUDE.md, "related decisions are decided one by one"):

- **Decision 9.58 settles the direction.** "Constructs go to the finest level the sources support; merging is an
  output of the model, not an input." Four vocabularies name tardive dyskinesia as its own term (HP:0040141,
  MedDRA PT 10043118, SNOMED 102449007, ICD-10-CM G24.01, MeSH D000071057). That is the finest level available,
  and it is the level at which every label source actually speaks: 43 of the 43 label pairs come from the PT
  `Tardive dyskinesia` itself, not from a broader term.
- **Decision 9.96 settles standing.** "Every symptom term of every label source is a candidate, there is no seed."
  `Tardive dyskinesia` is a PT in both label vocabularies and is currently claimed by **no** construct (checked:
  none of the 39 fine rows lists `Tardive dyskinesia`, `Dyskinesia`, `Choreoathetosis`, `Chorea`, `Dystonia` or
  `Hyperkinesia` among its `meddra_preferred_terms`). So these pairs are being discarded today, not reassigned.
- **A broader drug-induced-hyperkinesia root is not available in HPO** and should not be synthesised. The
  candidate is HP:0100660 Dyskinesia, which is *not* drug-specific: rooting there adds the PT `Dyskinesia` (82 of
  the 230 study drugs in SIDER, 60 qualifying OnSIDES perturbations) and, crucially, **201 genes** of monogenic
  dyskinesia. Those genes are not tardive dyskinesia under any reading — they are the dyskinesias of inherited
  movement disorders — so the broad root would manufacture a gene channel out of a different phenomenon. It also
  pulls in levodopa-induced dyskinesia through the dopamine agonists (bromocriptine, pergolide, lisuride,
  ropinirole, rotigotine, pramipexole, apomorphine all carry `Dyskinesia` in SIDER), which shares the
  phenomenology and inverts the pharmacology. Under "the version closest to physiology is used", the narrow root
  is the physiological one and needs no numerical justification.
- **MeSH's D004409 "Dyskinesia, Drug-Induced" is the one real candidate for a broader root**, and it is a
  *better* broad root than HP:0100660 because it is drug-specific. But the builder's additions table is keyed on
  an HPO id (`complete_addition` reads `hpo_ids` and takes the name and the MedDRA terms from the ontology), so
  there is no HPO term that expresses D004409's extension. Making a construct at that level would mean authoring
  a name, which 9.58's implementation deliberately forbids ("each fine construct is named by its root's HPO name,
  so none is authored here"). **Recommendation: do not create a broad root now.** If the owner wants the broader
  grouping, the honest routes are (i) leave it to the model, which is what 9.58 says merging is for, or (ii) a
  second, separate decision about whether the additions schema should admit a non-HPO root.
- **A second and third construct are available on the same argument and should be decided separately**, not
  bundled: `orofacial_dyskinesia` (HP:0002310) and `extrapyramidal_dyskinesia` (HP:0007308). Both are HPO leaves,
  both have gene annotations (30 and 7 genes), and both have **zero** MedDRA terms in either label vocabulary, so
  each would be a gene-only construct with no drug channel — the mirror image of tardive dyskinesia. They are
  listed in §6 as a separate question, not folded into this one.

### 3.2 Collisions with existing constructs

Checked programmatically against all 39 rows of `docs/symptom_crosswalk_fine.csv` (expanding each root through
`descendants_of` and subtracting each row's `excluded_hpo_ids`):

- **No existing fine construct's expansion contains HP:0040141, HP:0100660, HP:0002310 or HP:0007308.** Zero hits.
- **No existing fine construct's root lies inside the HP:0100660 Dyskinesia expansion.** Zero hits, so even the
  broad root would not steal a root from anyone.
- **akathisia (HP:0031943):** no collision. Akathisia descends from Restlessness and Involuntary movements;
  HP:0040141 descends from Dyskinesia; neither is an ancestor of the other. The MedDRA terms are disjoint
  (`Akathisia` vs `Tardive dyskinesia`), the ICD-10 codes are different (`G25.71` vs `G24.01`), and the
  phenomenology is different (subjective restlessness with an urge to move vs objective involuntary choreiform
  movement). Note that 15 drugs already carry *both* akathisia and restlessness labels (9.74's measurement); TD
  will likewise overlap akathisia at the drug level, and under 9.58 that overlap is for the model to resolve, not
  for hand reassignment.
- **hyperactivity (HP:0000752):** no collision. HP:0040141 is not in its expansion, and hyperactivity carries
  **no** MedDRA term at all (its crosswalk note: "no MedDRA term: Psychomotor hyperactivity stays under
  psychomotor_agitation"). The names are near-homonyms — HPO's HP:0002487 Hyperkinetic movements is defined as
  "Motor hyperactivity with excessive movement of muscles of the body as a whole" — but nothing in the
  hyperactivity row would move.
- **agitation (HP:0000713) and restlessness (HP:0000711):** no collision; HP:0040141 is in neither expansion.
- **parkinsonism and its five siblings:** no collision in the ontology — HP:0040141 is in the expansion of none of
  the six parkinsonism roots, and the parkinsonism row's MedDRA list (`Parkinsonism;Drug-induced
  parkinsonism;Extrapyramidal disorder;Bradykinesia;Hypokinesia;Cogwheel rigidity;Akinesia;Parkinsonian rest
  tremor;Parkinsonian gait`) contains no dyskinesia term. **But there is a real collision at the drug level and in
  the graph**, and it is the substantive problem: see §5.
- One thing *would* move if the owner chose the broad HP:0100660 root: `configs/fine_construct_term_overrides.csv`
  sends `Extrapyramidal disorder` to `parkinsonism` with the note "the general drug-induced extrapyramidal term,
  not rigidity alone". A construct named from HP:0007308 Extrapyramidal dyskinesia would make that override
  contestable. With the narrow HP:0040141 root, it is untouched.

### 3.3 Exclusions needed (`excluded_hpo_ids`)

**None. The column stays empty.**

HP:0040141 has exactly **one** term in its expansion — itself — because `descendants_of('HP:0040141')` returns
`['HP:0040141']`. There is nothing to exclude. Specifically:

- it cannot absorb a parkinsonian term, because none of HP:0001300, HP:0002067, HP:0002322, HP:0025387,
  HP:0002396 or HP:0007076 is a descendant of it (nor it of them);
- it cannot absorb akathisia, because HP:0031943 is not a descendant of it;
- it cannot absorb acute dystonia, because HPO has no such term and HP:0001332 Dystonia is a sibling of
  HP:0100660 under HP:0100022, not a descendant of HP:0040141;
- it cannot absorb chorea, athetosis or choreoathetosis, which sit under HP:0004305 Involuntary movements.

This is a genuine advantage of the narrow root over every alternative. For contrast, were the owner to choose
HP:0100660 Dyskinesia, the exclusions needed to keep it honest would be `HP:0002310;HP:0007308` (to stop it
expanding over the two sibling dyskinesias, if those became constructs) — and even then the 201 monogenic
dyskinesia genes and the dopamine-agonist `Dyskinesia` labels would still come in, which no exclusion list can fix.

### 3.4 Sign

The construct is a **mixed-sign** one, and both signs are physiologically right and already supported:

- **`induces`** — the 43 label pairs, 17 of whose 20 kept members are D2 antagonists entering the graph at
  PROTEIN:DRD2 with sign −1 (§5).
- **`relieves`** — **exactly one pair: tetrabenazine**, a VMAT2 inhibitor. `configs/evidence_assembly.yaml` sets
  `include_relieves_relation: true`, and `mechanistic_pathway_learning/evidence/load_drug_label_events.py` keeps
  only SIDER's `NLP_indication` detection method, dropping `NLP_precondition` and `text_mention`
  (`indication_methods: tuple[str, ...] = ("NLP_indication",)`; the docstring: it "drops NLP_precondition and
  text_mention, which include mentions of the condition"). Of SIDER's 29 indication rows naming dyskinesia or
  tardive dyskinesia, **only tetrabenazine's is `NLP_indication`**:
  `tetrabenazine | C0686347 | NLP_indication | Tardive Dyskinesia | PT | C0686347 | Tardive dyskinesia`.
  **This filter is what keeps the sign correct**, and it is worth stating plainly: the rows it drops would
  otherwise assert that **prochlorperazine**, **clozapine** and **benztropine** (`text_mention`) and
  **trifluoperazine** and **molindone** (`NLP_precondition`) *relieve* tardive dyskinesia. Prochlorperazine and
  trifluoperazine are among the construct's own inducers. The registered filter already handles this; nothing
  needs changing, but a future pass must not relax it.

**Valbenazine and deutetrabenazine, the registered treatments, are not perturbations in v5.** Both appear in
`data/raw/gtopdb_2026/ligands.csv`, `ligand_id_mapping.csv` and `interactions.csv` — so the graph layer knows them
as VMAT2 ligands — and both are named inside the clinical-trial JSON of tetrabenazine, fluoxetine and paroxetine,
but neither is among the 230 drug perturbations. So the relief side of this construct rests on tetrabenazine alone
until the drug table is extended. Two further named inducers are also missing from the perturbation set and carry
TD label statements: **metoclopramide** (a D2 antagonist with, in the US, a boxed warning for tardive dyskinesia,
and an OnSIDES TD statement) and the thioxanthenes **zuclopenthixol** and **flupenthixol**. Extending the drug
table is a separate decision; it is flagged in §6, not proposed here.

---

## 4. Proposed row(s) — NOT APPLIED

### 4.1 The mechanism to use: `configs/symptom_construct_additions.csv`, not extra roots

`configs/fine_construct_extra_roots.csv` is the wrong mechanism. `with_extra_roots` requires that the added root
"must sit under one of the row's roots … so that the coarse construct's expansion is the same set of terms before
and after", and raises `ValueError` otherwise ("`{hpo_id} {hpo_name} is under none of {coarse}'s roots, so it would
widen the coarse construct`"). HP:0040141 is under none of the 24 coarse rows' roots — verified: no coarse row's
expansion contains it. It also requires the coarse row to have at least two roots. So the additions table is the
only route, exactly as it was for `intellectual_disability` ("a sibling of HP:0100543, not a descendant").

### 4.2 The row

`configs/symptom_construct_additions.csv` column order, as the file's header gives it:

```
target_symptom,hpo_ids,rdoc_domain,mesh_descriptors,mesh_descriptor_level,notes
```

Proposed row, to be appended after the `intellectual_disability` row:

```csv
tardive_dyskinesia,HP:0040141,sensorimotor,D000071057,symptom,"decision 9.58: a construct of its own at the finest level the sources name, and the hyperkinetic (delayed, often irreversible) pole of the drug-induced extrapyramidal constructs, against the hypokinetic parkinsonism family. HP:0040141 is a leaf under HP:0100660 Dyskinesia with 0 descendants, so excluded_hpo_ids is empty and it can absorb no parkinsonian, akathisia, chorea or dystonia term; it is in the expansion of no existing construct and the MedDRA PT Tardive dyskinesia is claimed by none. The broader root was not taken: HPO's HP:0100660 Dyskinesia is not drug-specific and would add 201 monogenic dyskinesia genes and the dopamine agonists' levodopa-induced dyskinesia labels, and MeSH's drug-specific D004409 Dyskinesia, Drug-Induced has no HPO counterpart this table can key on. Name and MedDRA terms are read from hp.obo (hp/releases/2026-09-01) and the SIDER vocabulary by the builder, which matches the single PT Tardive dyskinesia; MeSH D000071057 Tardive Dyskinesia read from id.nlm.nih.gov 7 November 2026, tree numbers C23.888.592.350.275.500, C10.597.350.275.500 and C10.228.662.262.500.500, and it awaits experiments/verify_mesh_symptom_descriptors.py. No mouse proxy exists (mp.obo has no tardive term), so the IMPC fine row is validity none. Measured 7 November 2026 on evidence_full_v5: 0 gene pairs (HP:0040141 carries no HPO gene annotation), 43 drug label pairs (35 SIDER, 26 OnSIDES, 18 in both) and 1 relieves pair (tetrabenazine, SIDER NLP_indication), about 20 kept under better_v2_full_v5"
```

Notes on each field, so the owner can change any of them:

- **`target_symptom`** `tardive_dyskinesia` — this is `slug("Tardive dyskinesia")`, so the builder's own naming
  rule produces it; nothing is authored.
- **`hpo_ids`** `HP:0040141` — one root. `build_fine_crosswalk` raises if an addition names several
  ("`addition {name} names several HPO roots; add one construct per root`").
- **`rdoc_domain`** `sensorimotor` — the value the parkinsonism row uses, and the value 9.74 gave akathisia
  ("its RDoC domain in the crosswalk would be sensorimotor rather than arousal"). A movement symptom, so
  sensorimotor alone; not `arousal`, which is what would be right if this were akathisia or agitation.
- **`mesh_descriptors`** `D000071057` — verified in §1.4. **Sub-choice:** the parkinsonism precedent left MeSH
  empty rather than guess, but here the descriptor is exact and read from NLM, and the
  `intellectual_disability` precedent fills it with a note that the verifier is outstanding. If the owner prefers
  the parkinsonism treatment, leave both MeSH columns empty; the construct then has no E3 channel.
- **`mesh_descriptor_level`** `symptom` — two of its three tree numbers are symptom branches under
  `verify_mesh_symptom_descriptors.py`'s prefixes (`C23.888`, `C10.597`); the third (`C10.228`) is a diagnosis
  branch. `symptom` is the honest primary reading; the alternative, following the
  `elevated_mood_or_mania` row's style, would be to record both.
- **`excluded_hpo_ids`** — the file has no such column and the row needs none (§3.3). The builder reads it with
  `addition.get("excluded_hpo_ids")`, so an absent column is empty, as it already is for
  `intellectual_disability`. **Do not add the column for this row.**
- **`identifier_status`** — the file has no such column either; `complete_addition` fills it with
  "`hpo id and name read from hp.obo; MedDRA terms matched from the vocabulary; MeSH unverified`". That default
  text is correct here except for the last clause, since the MeSH id *was* read from NLM but not run through the
  verifier. Either leave the default or add an `identifier_status` column saying so — a sub-choice, noted in §6.

### 4.3 What else would need a row if this is ruled in (listed, not proposed)

1. `configs/symptom_minimum_assessment_age.csv` — every construct has a row (decision 9.92, "the owner's to
   confirm"). The parkinsonism-family rows all use 3 years with the Egger et al. 2006 anchor; TD would most
   naturally follow, but that is a separate judgment and the drug evidence is adult.
2. `configs/trial_outcome_scale_crosswalk.csv` — an AIMS row, matching `Abnormal Involuntary Movement` and
   **not** `\bAIMS\b` alone (§2.6). Worth real care: without it the AIMS channel is lost; with the wrong pattern
   two dozen anaesthetics acquire a tardive-dyskinesia outcome.
3. `data/raw/faers/_background.json` — one more openFDA background reaction total for `TARDIVE DYSKINESIA`
   (§2.4), without which no FAERS statistic for this construct can be computed.
4. `configs/impc_symptom_crosswalk_fine.csv` — generated; `fine_impc_rows` adds the `validity: none` row by itself.
5. The generated pages and the registration: `docs/symptom_crosswalk_fine.csv`,
   `docs/fine_symptom_constructs.md`, the v5 evidence rebuild (`scripts/rebuild_data_layer.sh fine`), and the
   generators and tests named under "Documents" in CLAUDE.md. Decision 9.74 records that the coarse set of the
   registration is unchanged by a fine-level addition and that "no registered rule fixes the construct list, so
   this is a decision … not an amendment"; the same should hold here, but the owner should confirm it rather than
   inherit it, since 9.74's correction note shows that question was itself got wrong once.
6. `configs/study_sheet_diagrams.json` and the study sheet's diagrams, under the rule of 5 November 2026, if any
   diagram depicts the symptom set.

---

## 5. Broader graph reach — flagged, not resolved

**Short answer: the inducing side is reachable, the relieving side is reachable by a different route, and the
delay and irreversibility are not representable at all. Tardive dyskinesia and parkinsonism enter the v5 graph at
the same node with the same sign.**

Measured on `data/processed/graph_full_neuronal_split_binders_drugs_v5` (49,834 nodes), 7 November 2026.

**The machinery is present.** `nodes.parquet` holds `GENE:` and `PROTEIN:` nodes, plus Reactome reaction and
entity nodes, for the whole striatal cast: SLC18A2 (VMAT2; 4 nodes, including `RCTE_372544` and `RCTE_374907`),
SLC18A1, DRD1, DRD2 (9 nodes, including `RCPT_DRD2`), DRD3, PPP1R1B (DARPP-32), PDE10A, ADORA2A, GAD1, GAD2, TH,
SLC6A3.

**The inducing route exists.** `drug_entry_nodes.parquet` puts 38 drugs on `PROTEIN:DRD2`, 28 of them with
sign −1. **17 of the 20 estimated kept TD inducers enter there with sign −1**: amisulpride, amoxapine,
aripiprazole, asenapine, clozapine, fluphenazine, haloperidol, loxapine, lurasidone, olanzapine, paliperidone,
perphenazine, pimozide, prochlorperazine, quetiapine, risperidone, ziprasidone. So this is not a label with no
mechanistic route.

**The relieving route exists and is distinct.** Three drugs enter at `PROTEIN:SLC18A2`, all with sign −1:
**tetrabenazine**, amphetamine and lisdexamfetamine. Tetrabenazine is the construct's single `relieves` pair, and
it enters the graph at VMAT2, not at DRD2 — so the relief edge has its own entry point and is not a sign flip of
the inducing one. That is a good property: the model could in principle learn that −1 at DRD2 and −1 at SLC18A2
have opposite consequences for this symptom.

**Three kept inducers have no DRD2 entry at all:** doxepin, fluoxetine and venlafaxine. Their TD label statements
would have to be explained by some other route or would be unexplainable. Worth a look; not resolved here.

**The hard problem, stated plainly.** Tardive dyskinesia's mechanism is held to be **D2 receptor supersensitivity**
— an adaptive upregulation of post-synaptic D2 receptors after *chronic* blockade. The v5 graph is a signed
propagation graph over molecular entities with no representation of exposure duration, receptor number, or
plasticity. There is no node for "upregulated D2 receptor" and no edge type that means "chronic blockade
increases receptor density". Consequently:

- **Parkinsonism and tardive dyskinesia share the same entry point, the same target and the same sign.** The 17
  kept TD inducers above are very largely the same drugs that give the parkinsonism construct its 109 kept pairs,
  entering at `PROTEIN:DRD2` with sign −1 in both cases. From the graph alone the two symptoms are
  **indistinguishable**: one hypokinetic, one hyperkinetic, both reached by DRD2 antagonism. Whatever separates
  them has to come from the symptom head, not from propagation.
- This is not an argument against adding the construct — 9.96 makes the symptom set data-defined, and a symptom
  the graph cannot yet separate is exactly the kind of thing the module structure is meant to be tested on. But it
  *is* an argument against expecting the model to predict TD specifically, and it should be said out loud before
  any result is read.
- The nearest precedent in the decision log is 9.69's observation about gabapentin and pregabalin, where Hendrich
  et al. 2008 showed an effect that appears "only when applied chronically" and the graph had no way to express
  the chronicity. The same gap, in a different place.

**Flagged for the owner, not resolved:** whether the architecture should acquire any representation of chronic
exposure or receptor-number plasticity, and if not, whether tardive dyskinesia should be reported as a construct
the graph is known to be unable to separate from parkinsonism. Both are architecture questions well outside this
pass.

---

## 6. Owner decisions needed

**The main question.**

> **Q1. Is `tardive_dyskinesia` added as a fine symptom construct, rooted at HP:0040141, by the row of §4.2?**
> The evidence it brings, measured 7 November 2026 on `evidence_full_v5`: 43 drug label pairs (35 SIDER,
> 26 OnSIDES, 18 in both), ~20 kept under `better_v2_full_v5`, 1 `relieves` pair (tetrabenazine), **0 gene
> pairs**. It would be a drug-only construct, the same shape as akathisia (9.74), sitting between
> cogwheel_rigidity and akathisia in size. It collides with nothing and needs no exclusions. The model can reach
> its inducers (17 of 20 enter at PROTEIN:DRD2, sign −1) but cannot distinguish it from parkinsonism, which
> enters at the same node with the same sign (§5).

**Sub-choices, each separable from Q1.**

> **Q2. The MeSH columns.** Fill them with `D000071057` / `symptom`, as §4.2 proposes and as
> `intellectual_disability` does, or leave them empty as the parkinsonism row does? Filling them opens the E3
> literature channel; leaving them empty keeps the "verified or nothing" discipline. The id and its three tree
> numbers were read from `id.nlm.nih.gov` on 7 November 2026 but have not been through
> `experiments/verify_mesh_symptom_descriptors.py`.

> **Q3. A broader drug-induced-hyperkinesia root.** Recommended: no, for now. HPO's HP:0100660 Dyskinesia is not
> drug-specific and would bring in 201 monogenic dyskinesia genes and the dopamine agonists'
> levodopa-induced-dyskinesia labels; MeSH's D004409 "Dyskinesia, Drug-Induced" is the right extension but has no
> HPO counterpart the additions table can key on, and authoring a name is what 9.58's implementation forbids.
> Under 9.58 the grouping is the model's job. **If** the owner wants it anyway, the question becomes: should the
> additions schema admit a non-HPO root, which is a schema decision of its own.

> **Q4. `orofacial_dyskinesia` (HP:0002310) and `extrapyramidal_dyskinesia` (HP:0007308)** — two further HPO
> leaves under HP:0100660, each with gene annotations (30 and 7 genes) and **zero** MedDRA terms in either label
> vocabulary, so each would be a gene-only construct. Decided separately from Q1 and from each other
> (CLAUDE.md: "related decisions are decided one by one"). Note that a construct named from HP:0007308 would make
> the existing `Extrapyramidal disorder → parkinsonism` override in
> `configs/fine_construct_term_overrides.csv` contestable.

> **Q5. The AIMS outcome channel.** Add a row to `configs/trial_outcome_scale_crosswalk.csv` for the Abnormal
> Involuntary Movement Scale (≈20 study drugs carry AIMS outcome measures, none of which reaches the model
> today)? If yes, the pattern must match `Abnormal Involuntary Movement` and not `\bAIMS\b` alone, because ≈25
> anaesthetics and opioids carry the title "Anesthesia Information Management System (AIMS)"; and levodopa's AIMS
> rows measure levodopa-induced dyskinesia, not tardive dyskinesia.

> **Q6. The FAERS background.** `_background.json` holds `reaction_totals` for only the 95 current crosswalk
> terms and lacks `TARDIVE DYSKINESIA`, so no disproportionality statistic can be computed for this construct
> without one more openFDA query and a refetch. Authorise that fetch?

> **Q7. FAERS confounding by indication.** Four of the 28 FAERS drugs reporting TD are drugs given *for* movement
> disorders: tetrabenazine (a VMAT2 inhibitor, 163 reports) and the anticholinergics benztropine (184),
> procyclidine (84) and trihexyphenidyl (70). Decision 9.96 admits exactly one correction, "the removal of labels
> that match the drug's own indication". SIDER's indication table supplies that match for tetrabenazine but not
> for the three anticholinergics. Is a hand-curated indication match admitted for them, or do their FAERS rows
> stand with the bias recorded?

> **Q8. The drug table.** Valbenazine and deutetrabenazine — the registered treatments for tardive dyskinesia —
> are **not** perturbations in v5, although both are in `data/raw/gtopdb_2026` as VMAT2 ligands; so the relief
> side rests on tetrabenazine alone. Three inducers with TD label statements are also absent:
> **metoclopramide** (and in the US it carries a boxed warning for tardive dyskinesia), zuclopenthixol and
> flupenthixol. Extend the drug perturbation set, and if so by which rule? This is a drug-table change, which
> 9.69's row notes falls before `draw_lockbox.py`.

> **Q9. The `identifier_status` text.** `complete_addition`'s default ends "MeSH unverified", which would be
> slightly wrong if Q2 is answered yes (the id was read from NLM; only the PubTator3 half is outstanding). Leave
> the default, or add an `identifier_status` column to the additions file with corrected wording?

> **Q10. Architecture, flagged only.** Should anything in the model represent chronic exposure or receptor-number
> plasticity, given that tardive dyskinesia and parkinsonism are reached by the same DRD2 antagonism edge with the
> same sign and the graph has no way to separate them (§5)? If not, should the construct be reported as one the
> graph is known to be unable to separate from parkinsonism?

> **Q11. Registration.** 9.74 recorded, with a correction, that a fine-level addition changes nothing the
> preregistration names and so is "a decision and a dated note", not an amendment. Does the same hold for an
> addition through `configs/symptom_construct_additions.csv` rather than through
> `configs/fine_construct_extra_roots.csv`? Worth confirming rather than inheriting.

---

## 7. Sources read, refusals, and text addressed to an AI assistant

**Local sources read:** `data/raw/hpo/hp.obo` (hp/releases/2026-09-01), `data/raw/hpo/genes_to_phenotype.txt`,
`data/raw/sider_4.1/{meddra_all_se,meddra_freq,meddra_all_indications}.tsv.gz` and `drug_names.tsv`,
`data/raw/onsides/v3.1.1/parquet/*.parquet`, `data/raw/faers/*.json` (231 files),
`data/raw/clinicaltrials/*.json` (230 files), `data/raw/clinicaltrials_outcomes/*.json`,
`data/raw/mgi/mp.obo`, `data/processed/evidence_full_v5/*`, `data/processed/label_selection/better_v2_full_v5*`,
`data/processed/{onsides_v5,faers_v5,clinical_trials_v5,clinical_trial_outcomes}/*`,
`data/processed/graph_full_neuronal_split_binders_drugs_v5/{nodes,drug_entry_nodes}.parquet`,
`data/raw/gtopdb_2026/{ligands,ligand_id_mapping,interactions}.csv` (grep only), and the repository's own code and
configs as cited inline.

**Remote sources read**, all with `experiments/read_public_page.py` on 7 November 2026, each saved with its
address, time and SHA-256 in the pass's working directory, which is not kept:

| address | status | what it gave |
| --- | --- | --- |
| `https://id.nlm.nih.gov/mesh/lookup/descriptor?label=Tardive%20Dyskinesia&match=exact&limit=10` | 200 | D000071057 |
| `https://id.nlm.nih.gov/mesh/D000071057.json` | 200 | label and 3 tree numbers |
| `https://id.nlm.nih.gov/mesh/D004409.json` | 200 | label and 7 tree numbers (the parent) |
| `https://www.ebi.ac.uk/ols4/api/ontologies/hp/terms?iri=...HP_0040141` | 200 | HP:0040141 confirmed independently of hp.obo |

**Terminology services used** (MCP connectors, not web fetches): SNOMED CT (`snomedct`, branch MAIN) for
102449007, 38941006, 1259642009 and the direct parent 98811000119103; ICD-10-CM FY2027 for the G24 and G25.7
categories.

**Refusals:** none. No robots rule blocked any read, no host presented a check that the visitor is human, and no
permission request was raised or withdrawn. No licence question arose, because no new data source was added — every
source read here is already in `docs/data_sources.md`.

**Text addressed to an AI assistant:** none was encountered on any page or in any tool result, and nothing of that
kind was acted on.

**Model:** Fable for the whole pass, including every reading and every interpretation. No fallback occurred, so
nothing here needs a Fable recheck under the "Models" rules. The pandas measurements of §2 and §5 are engineering;
their interpretation in §2.7, §3 and §5 is research and was done on Fable, as required.

**Not done, and why.** `experiments/verify_mesh_symptom_descriptors.py` was not run (it would write into
`data/raw/pubtator3/`, and this pass wrote nothing into the checkout). The placebo-arm comparison step of
`build_label_selection.py` was not applied to the TD estimate, so "~20 kept" is an upper bound by at most a few
pairs. The SIDER and OnSIDES drug counts were matched by lower-cased name rather than through the project's
identifier bridge, so they are estimates within about one or two drugs. No file in the repository was created,
edited, committed or pushed.

---

## Added 7 November 2026: the owner's rulings and what was built

The owner answered the eleven questions of section 6 the same day; the rulings are decisions 9.115 (tardive dyskinesia)
and 9.116 (the two gene-only constructs of Q4), with the drug-table question of Q8 in 9.117 and the architecture
question of Q10 in 9.118. Built on the same day, in the session's engineering steps, not in this pass:

- `experiments/verify_mesh_symptom_descriptors.py` was run on D000071057 (Q2, "Verify it first. Then, yes"): a valid
  MeSH id, label Tardive Dyskinesia, tree numbers C10.228.662.262.500.500, C10.597.350.275.500 and
  C23.888.592.350.275.500 ("both branches" in the script's reading), and in the PubTator3 vocabulary as
  `@DISEASE_Tardive_Dyskinesia`. The MeSH columns were filled.
- The row of section 4.2 was added to `configs/symptom_construct_additions.csv` with an `identifier_status` column
  carrying the corrected wording (Q9), and rows for `orofacial_dyskinesia` (HP:0002310) and `extrapyramidal_dyskinesia`
  (HP:0007308) were added after the checks of 9.116 (Q4). `docs/symptom_crosswalk_fine.csv` holds 42 constructs.
- `configs/trial_outcome_scale_crosswalk.csv` gained the AIMS row of section 2.6 (Q5), with a new column that keeps it
  from reading a Parkinson's or Huntington's trial.
- The FAERS background was supplemented with `TARDIVE DYSKINESIA` (Q6): 28,241 reports of 21,054,159 in the system.
  The same check found `MENTAL RETARDATION`, the term of the earlier `intellectual_disability` addition, also missing:
  351 reports.
