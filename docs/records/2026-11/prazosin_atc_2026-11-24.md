# Prazosin's WHO ATC code, checked against two sources (24 November 2026)

## 1. The value under check
`data/raw/sider_4.1/drug_atc.tsv`, line 870: `CID100004893	C02CA01` (the only row for that CID).

## 2. Source 1: WHO Collaborating Centre for Drug Statistics Methodology, ATC/DDD Index
Read with `experiments/read_public_page.py` (robots file allowed all three pages; status 200). Index stamp on each page: "Last updated: 2026-01-20".
- `https://atcddd.fhi.no/atc_ddd_index/?code=C02CA01`, read 2026-11-24T18:39:23Z, saved `pages_who/6ebd61b356773d8a.html`. Under "C02CA Alpha-adrenoreceptor antagonists": "C02CA01 prazosin 5 mg O". Group note: "Combinations with diuretics, see C02LE - Alpha-adrenoreceptor antagonists and diuretics. Alfuzosin and terazosin are classified in G04CA."
- `https://atcddd.fhi.no/atc_ddd_index/?name=prazosin&namesearchtype=containing`, read 2026-11-24T18:39:25Z, saved `pages_who/a8f1fa01dfa842b4.html`: "Found 2 entries containing 'prazosin'. C02CA01 prazosin C02LE01 prazosin and diuretics".
- `https://atcddd.fhi.no/atc_ddd_index/?code=C02LE01`, read 2026-11-24T18:39:43Z, saved `pages_who/86082b4e98ac8d25.html`: "C02LE Alpha-adrenoreceptor antagonists and diuretics ... C02LE01 prazosin and diuretics" (no DDD assigned).

## 3. Source 2: NLM RxNav (RxNorm / RxClass REST API)
Read with the same script (robots allowed; status 200).
- `https://rxnav.nlm.nih.gov/REST/rxcui/8629/property.json?propName=ATC`, read 2026-11-24T18:39:41Z, saved `pages_rxnav/9c0f78364e41d33f.txt`: `{"propCategory":"CODES","propName":"ATC","propValue":"C02CA01"}` - the single ATC value on the ingredient prazosin (RxCUI 8629).
- `https://rxnav.nlm.nih.gov/REST/rxclass/class/byDrugName.json?drugName=prazosin&relaSource=ATC`, read 18:39:27Z, saved `pages_rxnav/811714fbd625dd6f.txt`: one class, `"classId":"C02CA","className":"Alpha-adrenoreceptor antagonists","classType":"ATC1-4"` (RxClass holds levels 1 to 4 only).
- Same with `relaSource=ATCPROD`, read 18:39:30Z, saved `pages_rxnav/c9765e57357b7e10.txt`: single-ingredient prazosin products are C02CA; the three "polythiazide 0.5 MG / prazosin N MG Oral Capsule" products are `"classId":"C02LE","className":"Alpha-adrenoreceptor antagonists and diuretics"`.

## 4. Finding
- Both sources give plain prazosin exactly one code, C02CA01, matching SIDER 4.1.
- One other code carries the name: the combination code C02LE01 "prazosin and diuretics" (a fixed combination product, not the substance alone). RxNav agrees at the 4th level (C02LE for polythiazide/prazosin).
- No code in group N, G or any other anatomical group: the WHO name search returns two entries only, and RxNorm holds one ATC value.

## 5. Limits
- Independence: RxNorm's ATC values are NLM's own incorporation of the WHO classification, so the second source is independent as a publisher and a rendering, but ATC has one originating authority. It confirms SIDER's transcription, which is the question here.
- RxClass gives the 4th level only; the 5th-level match for the second source rests on the RxNorm property call.
- The licences of the two sources were not part of this task and were not verified in this pass.
- No source refused, no human check met, and no page carried text addressed to an AI assistant.

Read on Fable on 24 November 2026 for decision 9.31. The saved pages (`pages_who/`, `pages_rxnav/`, each with its address, time and SHA-256) are in that session's scratch directory and are not in the repository; every page is a public one that `experiments/read_public_page.py` reads again unattended.
