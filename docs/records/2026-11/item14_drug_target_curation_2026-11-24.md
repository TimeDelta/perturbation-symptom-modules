# Item 14 curation sweep — the six plain-MODULATOR drugs, bupropion, and the rest of the sweep

Date: 2026-11-24. Research done on Fable 5.2 up to the point noted below.

## MODEL FALLBACK — read first

Partway through this pass the session model fell back from Fable 5.2 to Opus 4.8 (noted at the
write-up step, after all source reading was complete). Under CLAUDE.md ("Models": a research step whose
model falls back from Fable is stopped and reported, not finished on the fallback model) and this pass's
brief ("If your model falls back from Fable at any point, stop and report"), the research is STOPPED here.

What this means for the rows below:
- Every source read, quote and query in this file and in the progress log was done ON FABLE and is saved
  to disk (`item14_pages/`, `item14_chembl/`). Those readings stand.
- The step of turning those readings into the proposed rows and the final sign recommendations is
  research too (CLAUDE.md: "turning what a source says into a claim, a decision entry or a curated edge").
  It was NOT completed on Fable. The proposed rows below are a DRAFT assembled from Fable-read sources and
  must be re-checked by a Fable pass before the owner relies on them.
- Nothing here is written to the repository (the brief forbids it); rows are proposals only.

## State and reproduction of the six

No v5 tables on disk (`data/processed` absent; `data/raw/chembl_37` holds only LICENSE, the UniProt map and
src1src7). So the drug set was re-derived without the v5 tables as follows:

1. All 7,561 ChEMBL_37 mechanism rows fetched from the EBI REST API (`mechanism.json`, paced ~1/s), cached at
   `item14_chembl/mechanisms.json` (sha256 369ff0ee…b09c0). The API reports ChEMBL_37, release 2026-05-01 —
   the same release the repo pins (`chembl_parent_corrections.csv`). 111 MODULATOR rows on 98 parent molecules.
2. For each parent carrying a plain `MODULATOR` row, membership in the v5 perturbation set was reconstructed
   from the rule in decision 9.117 (a drug is a perturbation iff it has a SIDER 4.1 or OnSIDES v3.1.1 label,
   an ATC code in group N, and a ChEMBL mechanism target in the graph), using the two files that survive on
   disk: `data/raw/sider_4.1/{drug_names,drug_atc}.tsv` and the OnSIDES bridge
   `data/releases/v0.4/onsides/ingredient_identifier_bridge.json` (built 2026-10-05 on ChEMBL_37).

Exactly six MODULATOR-carrying parents have `nervous_system_atc` and a label in SIDER or OnSIDES:

| drug | perturbation_id | ChEMBL parent | MODULATOR target(s) (ChEMBL) |
|---|---|---|---|
| gabapentin | CID100003446 | CHEMBL940 | CHEMBL2363032 (voltage-gated Ca channel complex) |
| pregabalin | CID100125889 | CHEMBL1059 | CHEMBL2363032 |
| levetiracetam | CID100059708 | CHEMBL1286 | CHEMBL1998 (SV2A) MODULATOR + CHEMBL4478 (CACNA1B) BLOCKER |
| brivaracetam | RXCUI:1739745 | CHEMBL607400 | CHEMBL1998 (SV2A) |
| cariprazine | RXCUI:1667655 | CHEMBL2028019 | CHEMBL234 (DRD3) + CHEMBL217 (DRD2), both MODULATOR |
| pentazocine | CID100004736 | CHEMBL100116 | CHEMBL287 (sigma-1/SIGMAR1), two MODULATOR rows |

Match to the recorded count: this is exactly 6, matching commit 7b637d4/4a8a83d's "six get sign 0 from a
plain MODULATOR row". It also matches decision 9.68, which names gabapentin, pregabalin, cariprazine,
brivaracetam and pentazocine as "five drugs inject nothing" (9.68 was measured before levetiracetam's case
surfaced — levetiracetam's SV2A row is sign-0 MODULATOR but its CACNA1B BLOCKER row gives it a non-zero edge,
so it is in the six-with-a-MODULATOR-row set but was not among 9.68's five all-zero drugs).

Difference from the true v5 set: I used the OnSIDES bridge and SIDER ATC as they stand in the v0.4 release
artifacts, and the rule as decision 9.117 states it; I could not run the actual v5 assembler (no rebuild).
Mirogabalin (CHEMBL3545125, N02BF03) and gabapentin enacarbil (CHEMBL1628502) carry MODULATOR rows but are
in neither SIDER nor OnSIDES, so they are not perturbations — consistent with their absence from the six.

## What each drug does at its MODULATOR target (sources read on Fable)

Two independent sources sought per value. Saved pages in `item14_pages/`; ChEMBL rows in `item14_chembl/`.

### gabapentin (CID100003446) and pregabalin (CID100125889) — Ca channel α2δ

ChEMBL writes a single direction-free MODULATOR row against the whole voltage-gated-Ca-channel complex
CHEMBL2363032, with `binding_site_comment` "alpha2delta-1 is binding site: 23836974, 23642658". The true
pharmacological target is the α2δ-1 (CACNA2D1) and α2δ-2 (CACNA2D3) auxiliary subunits, and the action is a
negative/inhibitory one on calcium-channel function and trafficking — not modulation of the pore α1 subunits.

Sources:
- openFDA Neurontin label, set 97935fd9-1d4a-43b6-a5d9-de994591187b, eff. 20260512 (sha 23d05644…): "gabapentin
  binds with high-affinity to the α2δ subunit of voltage-activated calcium channels".
- openFDA Lyrica label, set 60185c88-ecfd-46f9-adb9-b97c6b00a553, eff. 20200615 (sha 10eb0492…): pregabalin
  "binds with high affinity to the alpha 2 -delta site (an auxiliary subunit of voltage-gated calcium
  channels)… reduce calcium-dependent release of pro-nociceptive neurotransmitters… possibly by disrupting
  alpha 2 -delta containing-calcium channel trafficking and/or reducing calcium currents".
- Hendrich et al. 2008, PNAS (PMID 18299583, PMC2265195, [DOI](https://doi.org/10.1073/pnas.0708930105)):
  GBP "inhibits calcium currents, mimicking a lack of alpha(2)delta only when applied chronically"; "reduces
  cell-surface expression of alpha(2)delta-2 and Ca(V)2.1"; no effect for α2δ-3 (CACNA2D3 note: α2δ-3 does not
  bind GBP — see caveat). Field et al. 2006, PNAS (PMID 17088553, [DOI](https://doi.org/10.1073/pnas.0409066103)):
  R217A α2δ-1 point mutant loses pregabalin binding and analgesia → α2δ-1 is the analgesic target.
- Gee et al. 1996, JBC (PMID 8621444, [DOI](https://doi.org/10.1074/jbc.271.10.5768)): [3H]gabapentin binds α2δ.

Caveat the Fable pass flagged: Hendrich names α2δ-1 AND α2δ-2 as GBP-binding (and α2δ-3 as non-binding). The
graph's gabapentin/pregabalin seeds currently spread over the whole 22-subunit complex (incl. α1, β, γ). The
repo's own `binding_sites.csv` already records "alpha2delta-1 is binding site". A faithful curation would
restrict to CACNA2D1 (and, by Hendrich, CACNA2D2 — but CACNA2D2 is NOT a v5/graph node in the v0.4 release;
CACNA2D3 does not bind GBP so arguably should be dropped). Which subunits to keep is a judgement for the owner/
a Fable pass, not settled here.

DRAFT proposed sign: the α2δ action is inhibitory/negative. Candidate sign −0.5 (NEGATIVE ALLOSTERIC
MODULATOR scale) or −1 — this choice is exactly the research step not to be finalized on the fallback model.

### levetiracetam (CID100059708) and brivaracetam (RXCUI:1739745) — SV2A

ChEMBL and GtoPdb both carry SV2A. GtoPdb (ligand 6826 LEV, 9041 BRV; REST API answered 200, saved) labels
the SV2A interaction "Inhibitor / Inhibition", but this rests on radioligand DISPLACEMENT (pIC50/pKi), not a
functional direction — the primary refs are binding/SAR papers (Noyer 1995 PMID 8605950; Kenda 2004 PMID
14736235; Gillard 2011 PMID 21575627). The functional direction of LEV at SV2A is, in the literature, UNKNOWN:

- Lynch et al. 2004, PNAS (PMID 15210974, PMC470764, [DOI](https://doi.org/10.1073/pnas.0308208101)): SV2A is
  the LEV binding site; "LEV acts by modulating the function of SV2A" — modulation, direction unstated.
- Nowack et al. 2011, PLoS One (PMID 22220214, PMC3248421, [DOI](https://doi.org/10.1371/journal.pone.0029560)):
  "how drug binding affects synaptic functioning remains unknown"; LEV "reverses the effects of excess SV2A";
  "changes in SV2 expression in either direction impact neurotransmission"; "one possible mechanism… is that
  it inhibits SV2 protein interactions".
- Löscher et al. 2016, CNS Drugs (PMID 27752944, PMC5078162, [DOI](https://doi.org/10.1007/s40263-016-0384-x)):
  review; no clean enhance/inhibit statement for LEV at SV2A.
- openFDA Keppra XR, set 2919e43b…, eff. 20250624: "levetiracetam binding to synaptic vesicle protein SV2A may
  contribute to the antiepileptic mechanism" — direction unstated. openFDA Briviact, set 3cf2f439…, eff.
  20261105: "high and selective affinity for synaptic vesicle protein 2A (SV2A)… which may contribute to the
  anticonvulsant effect".

DRAFT recommendation: the physiological sign at SV2A is genuinely not established by the sources — this is a
"sources do not determine a sign" case (like 9.121's held-for-owner cases), NOT a case a plain curated sign
fixes. Keeping sign 0 may be the honest reading; GtoPdb's "Inhibition" is a displacement label, not a
functional direction. Flag for the owner. (Levetiracetam separately already gets a non-zero edge from its
CACNA1B BLOCKER row.)

### cariprazine (RXCUI:1667655) — DRD2, DRD3

ChEMBL writes both as MODULATOR with comment "Mixed antagonist/partial agonist". The established action is
PARTIAL AGONIST at D2 and D3 (with D3 preference):
- openFDA Vraylar, set 3435ec73… eff. 20261111 (a repackager's copy of the label; the original is Allergan's
  — a second genuine-manufacturer label should be pulled on the Fable recheck): "partial agonist activity at
  central dopamine D 2 … receptors"; "Cariprazine acts as a partial agonist at the dopamine D 3 and D 2
  receptors with high binding affinity (K i … 0.085 nM, and 0.49 nM (D 2L )…)".
- Kiss et al. 2010, JPET (PMID 20093397, [DOI](https://doi.org/10.1124/jpet.109.160432)): "D(3)/D(2) dopamine
  receptor antagonist-partial agonist"; partial agonist (Emax 71%) at hD3 cAMP, D2L IP Emax 30%.
- Consistency: aripiprazole (CHEMBL1112) and brexpiprazole (CHEMBL2105760) are both written PARTIAL AGONIST at
  DRD2 in ChEMBL_37, so PARTIAL AGONIST for cariprazine matches the project's existing treatment of the class.

DRAFT proposed action: PARTIAL AGONIST (sign +0.5) at DRD2 and DRD3. This is the clearest of the six.

### pentazocine (CID100004736) — SIGMAR1 (and its true primary targets are opioid)

ChEMBL writes only two sigma-1 MODULATOR rows (comment "Mixed agonist/antagonist"), citing Cobos 2008
(PMID 19587856) and DailyMed. ChEMBL carries NO opioid row for pentazocine at all — its principal mechanism
(kappa agonist, mu partial agonist) is entirely missing, which is the larger problem than the sigma sign.
- GtoPdb ligand 1606 is (−)-pentazocine (REST API, saved): kappa partial agonist (pKi 7.8–8.6), mu partial
  agonist (8.4), delta full agonist (7.3), and SIGMAR1 "Antagonist" (primary, NO reference given).
- Literature on the sigma sign is stereochemistry-dependent and conflicting: Cobos 2008 (PMC2701284, full
  text) calls "(+)-pentazocine" a sigma-1 AGONIST; Chien & Pasternak 1993 (PMID 8119306) show (+)-pentazocine
  acts through sigma (haloperidol-reversible, anti-opioid). The marketed drug is the RACEMATE (US labels
  (2R*,6R*,11R*), pentazocine+naloxone, Lupin set 017ef042/Sun 41ebdaaf/Actavis a28450a0 — same wording = one
  source family). GtoPdb's antagonist label is for the (−)-enantiomer; ChEMBL's "Mixed agonist/antagonist" is
  for the racemate. So the sigma sign is genuinely ambiguous and enantiomer-dependent.
- Opioid: Chien & Pasternak 1995 (PMID 8788445): (−)-pentazocine analgesia is kappa-1 (nor-BNI-reversible).
  US label description: "a partial opioid agonist".

DRAFT recommendation: pentazocine is a `catalyzes`-style missing-target case like tramadol (9.121 C5): its
sigma-1 MODULATOR sign is contested AND its principal opioid targets (OPRK1 agonist, OPRM1 partial agonist,
OPRD1) are absent from ChEMBL entirely. Flag for the owner; the sigma sign should probably stay 0/held while
the opioid targets are added (via `drug_target_additions.csv`). Not a single-sign fix.

## CODE CONSTRAINT found (affects how any of this can be wired)

`configs/curated_drug_targets.csv` is read ONLY for a drug whose ChEMBL route gives NO target
(`map_drug_targets_to_graph_nodes.py` docstring line 64; `assemble_evidence_table --curated-drug-targets`
help; `curated_drug_wiring.py`). All six drugs DO have ChEMBL mechanism rows, so curated_drug_targets rows
for them would never be applied. The existing override paths are:
- `chembl_action_conflict_resolutions.csv`: applies ONLY when one target has >1 action type (lines 583–600).
  A plain single MODULATOR row is not a conflict, so this path does not reach gabapentin/pregabalin/
  brivaracetam/pentazocine-sigma/cariprazine as they stand.
- `drug_target_additions.csv`: appends targets ChEMBL does NOT name; REFUSES a target ChEMBL already names.
- `drug_target_exclusions.csv`: removes targets/members.

Consequence: re-signing a target ChEMBL already writes as MODULATOR (cariprazine D2/D3; the α2δ subunits of
the gabapentinoid complex; pentazocine sigma) has NO existing config route — it needs either a new override
table/column or a widening of the conflict-resolution path to cover a single unparsable action type. That is
a code change (not made here) and should be raised with the owner. Adding pentazocine's missing opioid
targets CAN go through `drug_target_additions.csv`. Dropping the non-binding α2δ/pore subunits of the
gabapentinoid complex CAN go through `drug_target_exclusions.csv`. So the sweep's premise — "rows go to
configs/curated_drug_targets.csv" (item 14 text, 9.121 C3) — does not hold for these six, because that file
only fires when ChEMBL gives no target.

## Bupropion's nicotinic antagonism (item-table unverified case)

- In ChEMBL_37? NO. Bupropion (parent CHEMBL894) has only DAT (CHEMBL238) and NET (CHEMBL222) INHIBITOR
  mechanism rows (mec_id 689/690/888/907). No nicotinic (CHRN*) mechanism row exists. GtoPdb ligand 7135
  likewise: NET and DAT inhibition only.
- Two independent primary sources confirm the nicotinic antagonism, both functional and both noncompetitive:
  - Slemmer, Martin & Damaj 2000, JPET (PMID 10991997, [DOI](https://doi.org/10.1016/s0022-3565(24)38905-0)),
    titled "Bupropion is a nicotinic antagonist": blocks nicotine activation of α3β2, α4β2 and α7 nAChRs
    ("~50 and 12 times more effective in blocking alpha(3)beta(2) and alpha(4)beta(2) than alpha(7)");
    "This functional blockade was noncompetitive"; did not displace [3H]nicotine.
  - Fryer & Lukas 1999, JPET (PMID 9862757, [DOI](https://doi.org/10.1016/s0022-3565(24)37928-5)):
    noncompetitive functional inhibition of human muscle (α1βγδ) and ganglionic (α3β4α5±β2) nAChRs.
- The US labels say nothing about nicotinic receptors (Wellbutrin XL set a435da9d eff. 20260210; bupropion SR
  smoking-cessation generics set 2bb61b34, 8069c521: mechanism "presumed to be related to noradrenergic
  and/or dopaminergic mechanisms"). So the smoking-cessation nicotinic mechanism is a literature finding, not
  a label or ChEMBL/GtoPdb one.

So: the item-14 table's bupropion row is now VERIFIED — the transporter rows (SLC6A2, SLC6A3, both −1) are
right; the nicotinic antagonism is real, noncompetitive, at α4β2/α3β2/α7 (and muscle/ganglionic), carried by
neither ChEMBL nor GtoPdb nor the label. If curated, it would be an ANTAGONIST (−1) addition at CHRNA4/CHRNB2
(α4β2), CHRNA3/CHRNB2 (α3β2) and CHRNA7, via `drug_target_additions.csv` — all are v5/graph gene nodes. DRAFT
only; subunit choice and whether to include α7 is a Fable/owner decision.

## Plan for the rest of the sweep (item 14's two routes)

Item 14 names two routes. Which can run before the rebuild:

- Route 1 (label mechanism sections vs target rows, via `read_label_central_action.py`): this reads openFDA
  pharmacology sections, which are cached/fetchable now and need no rebuild. It CAN run before the rebuild.
  Size: the perturbation set is ~214–256 drugs (9.121 dry runs). `configs/centrally_acting_drugs.csv` holds
  924 pool drugs with pre-computed `mechanism_targets`; the sweep proper is over the ~230–260 perturbations.
  A label-vs-targets comparison is one openFDA read per drug (cached), so ~230–260 label reads — feasible in
  one Fable pass, but it is a finder, not an oracle (the script's own caveat: needs ≥8 labels/drug, misses
  sentences in other labels), so each hit still needs manual curation with a second source.
- Route 2 (ChEMBL action types that the sign mapping flattens — SUBSTRATE, RELEASING AGENT, MODULATOR): this
  is a pure query over the ChEMBL mechanism cache (done here: `item14_chembl/mechanisms.json`) and needs no
  rebuild. It CAN run now. Size over ALL ChEMBL_37 (not yet intersected with the v5 set): MODULATOR 111 rows
  / 98 parents (6 in v5, done here), SUBSTRATE 7 rows / 7 parents, RELEASING AGENT 29 rows / 8 parents. Also
  worth including the sign-0 types the map assigns: BINDING AGENT (284 rows), CROSS-LINKING AGENT (45), OTHER
  (37), and None (577). The subset that intersects the ~230–260 v5 perturbations is small (the MODULATOR
  intersection was 6); SUBSTRATE and RELEASING AGENT intersections are the obvious next slices and are each
  only a handful of drugs. NEGATIVE MODULATOR (6 rows) and ALLOSTERIC ANTAGONIST (1) are action types
  `ACTION_TYPE_SIGN` does not know and would raise on — worth auditing too.

Both routes can run before the rebuild. The count of affected EDGES, however, still waits on the rebuild
(item 14 and 9.121 both say so), because edge magnitudes come from the built graph.

Recommended order (for a Fable pass): (1) finish route 2's full action-type×v5 intersection (cheap, done
mostly here); (2) run route 1 as a finder; (3) curate each surfaced drug with two sources. Do NOT run either
route over all 924 pool drugs — only the perturbation set matters.

## Limits / could not check
- No v5 tables on disk, so the six were reconstructed from the OnSIDES bridge + SIDER + decision 9.117's rule,
  not from the actual assembler. The reconstruction matches the recorded count of six.
- EU SmPCs (AEMPS/EMA) were not pulled this pass (the US labels + primary literature gave two sources for the
  verified cases); the Vraylar label read was a repackager's copy — a genuine-manufacturer second label is
  still wanted for cariprazine.
- Per the CLAUDE.md "A drug the sweep corrects moves the perturbation set" limit: any of these corrections
  that changes a drug's edges moves the perturbation set, outcome-blind only while the lockbox is undrawn
  (decision 1.1 — it is undrawn).
- MODEL FALLBACK: the synthesis and proposed rows above are a DRAFT built from Fable-read sources but were not
  finalized on Fable. They need a Fable recheck before the owner relies on them.

---

# Fable recheck and final findings, 24 November 2026

Written by the third pass, on Fable 5.2 (model id `claude-fable-5-2`) from first step to last. It rests on the
readings of the first pass and the verification of the second (both done on Fable before each fell back), which
are in `item14_curation_2026-11-24.progress.md`. This pass fetched no new source. It re-found every quotation
below in `item14_pages/` or `item14_chembl/` and re-read the code lines in the repository at `f2729f1`.
**Where this section and the draft above differ, this section stands.** Nothing was changed in the repository.

Three errors in the draft above, corrected here: "α2δ-2 (CACNA2D3)" should read CACNA2D2; the R217A residue is
struck (finding 2); and "the sigma sign is genuinely ambiguous and enantiomer-dependent" overstated the
disagreement (finding 4).

**How independence is counted.** Two documents from one originator are one source: a label and its repackaged
copy, a label and the sponsor's own papers, a database row and the paper it cites. The second pass applied this
to cariprazine and to Löscher et al. 2016. This pass applied the same test to the remaining papers, from the
author affiliations in the saved Europe PMC records. That moved Field 2006 and Gee 1996 (Pfizer, Parke-Davis)
and Lynch 2004, Kaminski 2009, Gillard 2011 and Klitgaard 2016 (all UCB) into their originators' families. Two
values are left on one source family as a result; findings 2 and 3 name them.

Signs are those of `ACTION_TYPE_SIGN` in `mechanistic_pathway_learning/perturbation/map_drug_targets_to_graph_nodes.py`:
AGONIST +1, PARTIAL AGONIST +0.5, POSITIVE ALLOSTERIC MODULATOR +0.5, NEGATIVE ALLOSTERIC MODULATOR −0.5,
ANTAGONIST, BLOCKER and INHIBITOR −1, MODULATOR 0.

## 1. Findings

### Finding 1. Cariprazine is a partial agonist at DRD2 and DRD3 (two independent sources)

**Claim.** ChEMBL_37 writes both targets as MODULATOR, sign 0 (mec 2402, CHEMBL234 DRD3; mec 2403, CHEMBL217
DRD2; comment "Mixed antagonist/partial agonist"). The sources support PARTIAL AGONIST (+0.5) at both, which is
what ChEMBL_37 already writes for aripiprazole (CHEMBL1112) and brexpiprazole (CHEMBL2105760) at DRD2.

**Source A, the originator's family (one source).**
- US label, Vraylar. The saved openFDA file holds Allergan, Inc., set 4b5f7c65-aa2d-452a-b3db-bc85c06ff12f
  (effective 20251218) and RemedyRepack sets 3435ec73 and f75d1689. Sections 12.1 and 12.2 are the same text in
  all three, so **the manufacturer's and the repackager's labels are one source**. 12.2: "Cariprazine acts as a
  partial agonist at the dopamine D 3 and D 2 receptors with high binding affinity (K i values 0.085 nM, and
  0.49 nM (D 2L ) and 0.69 nM (D 2S ), respectively)". 12.1: "The mechanism of action of cariprazine is unknown.
  However, the efficacy of cariprazine could be mediated through a combination of partial agonist activity at
  central dopamine D 2 and serotonin 5-HT 1A receptors and antagonist activity at serotonin 5-HT 2A receptors."
- Kiss et al. 2010, JPET (PMID 20093397; Gedeon Richter; abstract): "It had partial agonist activity (pEC(50)
  8.58, E(max) 71%) by inhibiting cAMP accumulation in Chinese hamster ovary cells expressing human D(3)
  receptors"; at human D2L it "stimulated inositol phosphate (IP) production (pEC(50) 8.50, E(max) 30%)".
- GtoPdb ligand 7671 (D2 partial agonist pKi 8.2, D3 partial agonist pKi 10.1) cites Kiss 2010 and Agai-Csongor
  et al. 2012 (PMID 22537450, Gedeon Richter). ChEMBL's rows cite the Allergan label and Kiss 2010. Neither
  database adds a source.

**Source B, independent.** Tadori, Forbes, McQuade and Kikuchi 2011, Eur J Pharmacol 668:355-365 (PMID 21816144;
Otsuka Pharmaceutical, a competitor's laboratory; abstract only). RGH-188 (cariprazine) and didesmethyl-RGH-188
in cAMP assays at human D2S, D2L and D3: "All test compounds behaved as dopamine D(2)/D(3) receptor partial
agonists." RGH-188's intrinsic activity at D2S and D2L was "similar to" aripiprazole's and at D3 higher.

**Disagreement, recorded.** Kiss 2010 found the action depends on the assay: "It displayed D(2) and D(3)
antagonism in [(35)S]GTPgammaS binding assays", and its title calls the drug an "antagonist-partial agonist".
That is the basis of ChEMBL's comment. The label, the two cAMP studies and the IP result all read partial
agonist. The label's 12.1 names D2 only for efficacy; D3 is in 12.2.

**Config route.** None. Both targets are named by ChEMBL with a single action type (section 2). Needs code.

### Finding 2. Gabapentin and pregabalin act at the α2δ subunits and reduce calcium-channel function (gabapentin two independent sources; pregabalin's direction one source family)

**Claim.** ChEMBL_37 writes MODULATOR, sign 0, against the whole voltage-gated calcium channel complex
CHEMBL2363032 (mec 1921 gabapentin, mec 1920 pregabalin; binding_site_comment "alpha2delta-1 is binding site:
23836974, 23642658"). The sources put the binding on α2δ-1 (CACNA2D1) and α2δ-2 (CACNA2D2), not on α2δ-3 or the
pore subunits, with a negative effect on channel trafficking and current that is chronic, not acute.

**Source A, the originator's family (Parke-Davis and Pfizer; one source).**
- Neurontin label, set 97935fd9-1d4a-43b6-a5d9-de994591187b (effective 20260512). Binding only, no direction:
  "In vitro studies have shown that gabapentin binds with high-affinity to the α2δ subunit of voltage-activated
  calcium channels; however, the relationship of this binding to the therapeutic effects of gabapentin is
  unknown."
- Lyrica label, set 60185c88-ecfd-46f9-adb9-b97c6b00a553 (effective 20200615; Viatris set d4734e7d has the same
  text). Binding: "binds with high affinity to the alpha 2 -delta site (an auxiliary subunit of voltage-gated
  calcium channels)". Direction, hedged: "pregabalin has been shown to reduce calcium-dependent release of
  pro-nociceptive neurotransmitters in the spinal cord, possibly by disrupting alpha 2 -delta containing-calcium
  channel trafficking and/or reducing calcium currents."
- Field et al. 2006, PNAS (PMID 17088553; Pfizer Global Research and Development; abstract): pregabalin's
  analgesia was studied "in a mutant mouse containing a single-point mutation within the gene encoding a specific
  auxiliary subunit protein (alpha2-delta-1)". **R217A is struck**: the residue is in no saved page, and the
  full text could not be read by two routes (Europe PMC fullTextXML answered HTTP 500 twice; the PubMed
  connector returned no full text for PMC1859964). The abstract's wording is what is cited.
- Gee et al. 1996, JBC (PMID 8621444; Parke-Davis). Title: "The novel anticonvulsant drug, gabapentin
  (Neurontin), binds to the alpha2delta subunit of a calcium channel."

**Source B, independent.** Hendrich et al. 2008, PNAS (PMID 18299583; University College London; abstract).
Gabapentin "binds to an exofacial epitope of the alpha(2)delta-1 and alpha(2)delta-2 auxiliary subunits of
voltage-gated calcium channels, but acute inhibition of calcium currents by GBP is either very minor or absent";
"GBP inhibits calcium currents, mimicking a lack of alpha(2)delta only when applied chronically, but not
acutely"; the effect "is not observed for alpha(2)delta-3, which does not bind GBP"; "GBP reduces cell-surface
expression of alpha(2)delta-2 and Ca(V)2.1 subunits"; and "GBP may act chronically by displacing an endogenous
ligand that is normally a positive modulator of alpha(2)delta subunit function, thereby impairing the trafficking
function of the alpha(2)delta subunits to which it binds." ChEMBL's gabapentin row cites this paper, so ChEMBL
is not a further source.

**Where each drug stands.**
- Gabapentin: site and direction on two independent sources (the originator's binding work; Hendrich).
- Pregabalin: the site rests on the Pfizer family. The direction rests on the Lyrica label alone, with
  "possibly". **One source family.** Second sources tried: GtoPdb ligand 5484, which holds no interaction at
  all, and Hendrich 2008, which tested gabapentin only. Carrying Hendrich's direction over to pregabalin is a
  class inference, and it is recorded as one.

**Disagreements, recorded.**
- GtoPdb ligand 5483 gives gabapentin only as a KCNQ3 and KCNQ5 activator (pEC50 8.3 and 8.7, PMID 30021858,
  not primary) and holds no α2δ row. ChEMBL holds no KCNQ row. Neither database carries what the other does.
- ChEMBL's binding-site comment names α2δ-1 only. Hendrich names α2δ-1 and α2δ-2, as does the code's own table
  (section 2).
- The Neurontin label declines to link binding to effect. Hendrich supplies the link.

**Config route.** No route re-signs the complex row. One config-only route may exist around it (section 2).

### Finding 3. Levetiracetam and brivaracetam bind SV2A; no source read gives a direction

**Claim.** ChEMBL_37 writes MODULATOR, sign 0, at CHEMBL1998 SV2A (mec 672 levetiracetam, mec 5512
brivaracetam). SV2A as the binding target is supported. A sign is not: no source read says whether the drug
raises or lowers SV2A's function. Sign 0 is the reading the sources support today.

**Source A, UCB's family (one source).**
- Keppra and Keppra XR labels, UCB sets 2919e43b, 3ca9df05 and c6d5784d: "Although the molecular significance of
  levetiracetam binding to synaptic vesicle protein SV2A is not understood, levetiracetam and related analogs
  showed a rank order of affinity for SV2A which correlated with the potency of their antiseizure activity".
- Briviact label, UCB set 3cf2f439-0e97-443e-8e33-25ecef616f6c (effective 20261105): "Brivaracetam displays a
  high and selective affinity for synaptic vesicle protein 2A (SV2A) in the brain, which may contribute to the
  anticonvulsant effect."
- Lynch et al. 2004, PNAS (PMID 15210974; UCB Research Inc.): "LEV acts by modulating the function of SV2A".
- Löscher et al. 2016, CNS Drugs (PMC5078162; full text). **Not independent of the labels**: its conflict
  statement reads "Michel Gillard, Zara Sands, Rafal M. Kaminski, and Henrik Klitgaard are employees of UCB
  Pharma", and UCB paid the open-access fee. It says "the underlying mechanistic effect of ligand binding is not
  fully elucidated", offers as "One hypothesis" that binding "would promote/stabilize a conformation that enables
  the protein to fulfill a role in providing seizure protection", and reports "a reduction in exocytosis" in
  brain slices.
- Kaminski 2009 (PMID 19486357), Gillard 2011 (PMID 21575627) and Klitgaard 2016 (PMID 26920914) are UCB papers.
  GtoPdb's rows (ligands 6826 and 9041, rat SV2A, "Inhibitor / Inhibition") cite Kenda 2004 and Noyer 1995, UCB
  binding papers; the label rests on displacement pIC50 and pKi values, not on a functional direction.

**Source B, independent (levetiracetam only).** Nowack et al. 2011, PLoS One (PMID 22220214, PMC3248421;
University of Washington; abstract and full text): "Although it is known that levetiracetam binds the synaptic
vesicle protein SV2A, how drug binding affects synaptic functioning remains unknown"; "levetiracetam reverses the
effects of excess SV2A"; "changes in SV2 expression in either direction impact neurotransmission"; "one possible
mechanism of drug action is that it inhibits SV2 protein interactions".

**Where each drug stands.**
- Levetiracetam: binding at SV2A on two independent sources; direction undetermined in both.
- Brivaracetam: binding at SV2A on the UCB family only. **One source family.** Second sources tried: GtoPdb,
  which cites UCB's papers, and Nowack 2011, which tested levetiracetam only.

**Disagreement, recorded.** The hints point opposite ways. GtoPdb says "Inhibition" and Nowack suggests the drug
"inhibits SV2 protein interactions"; Löscher's hypothesis has the drug stabilising a protective conformation, and
it calls a compound that counteracts levetiracetam a "negative SV2A modulator", which would make levetiracetam
the positive one. None of these is a measured direction.

**Config route.** None is needed while the sign stays 0. A sign, if ruled, has no config route (section 2).

### Finding 4. Pentazocine: the opioid targets are missing from ChEMBL, and the referenced literature calls it a sigma-1 agonist

**Claim, opioid.** ChEMBL_37 holds no opioid mechanism row for pentazocine (parent CHEMBL100116). Its only rows
are two sigma MODULATOR rows (mec 333 and 334, CHEMBL287, comment "Mixed agonist/antagonist"). The drug's
principal action is at the kappa and mu opioid receptors. Three independent sources:
- US labels, pentazocine with naloxone (Lupin set 017ef042, Sun set 41ebdaaf, Actavis set a28450a0; one text,
  one source): "Pentazocine is a mixed agonist-antagonist at opioid receptors. Pentazocine is a partial agonist
  at the mu opioid receptor and an agonist at the kappa opioid receptor." No label mentions sigma.
- GtoPdb ligand 1606, (−)-pentazocine: kappa partial agonist (pKi 7.8-8.6; PMID 9686407, 9262330), mu partial
  agonist (pKi 8.4; PMID 9686407), delta full agonist (pKi 7.3; PMID 9686407). The two cited papers were not
  read.
- Chien and Pasternak 1995 (PMID 8788445; abstract): "The analgesic actions of (-)-pentazocine are readily
  reversed by nor-binaltorphimine, but not by the mu-selective opioid receptor antagonist beta-funaltrexamine,
  implying a kappa 1-opioid receptor mechanism of action"; "(+)-Pentazocine is inactive in all antinociceptive
  assays".

**Disagreements, opioid.** At kappa the label says "agonist" (+1) and GtoPdb "Partial agonist" (+0.5). The delta
row rests on GtoPdb alone and its reference was not read: one source.

**Claim, sigma-1.** The referenced literature read calls both enantiomers sigma-1 agonists. **The "antagonist"
label rests only on an unreferenced GtoPdb row.**
- Chien and Pasternak 1993 (PMID 8119306; abstract): "Both (+)-pentazocine and (-)-pentazocine antagonize
  morphine analgesia equally well. This lack of stereospecificity implies an non-opioid mechanism of action. The
  antagonism of morphine analgesia by (+)-pentazocine is reversed by haloperidol, a potent dopamine D2 and sigma
  receptor antagonist."
- Cobos et al. 2008 (PMC2701284; full text, Table 1; ChEMBL's own reference): "(+)-Pentazocine σ1 [61] +++ [61]
  Agonist [61]" and "(–)-Pentazocine σ1/σ2 [214] ++ [214] Agonist [31]". Its reference 31 is Chien and Pasternak
  1995, so for (−)-pentazocine Cobos is not independent of them. Its reference 61 is Hayashi and Su 2004, so for
  (+)-pentazocine it is a second line; Hayashi and Su was not read.
- GtoPdb target 2552 (sigma-1): (−)-pentazocine "Antagonist", marked primary, with no reference and no affinity.
  The same target lists [3H]pentazocine as "Agonist", also without a reference.

**Where the sigma claim stands.** Agonist for (+)-pentazocine: two lines. Agonist for (−)-pentazocine: one source
family. Antagonist: one unreferenced database row. The marketed drug is the racemate. ChEMBL's "Mixed
agonist/antagonist" comment matches the labels' opioid wording ("mixed agonist-antagonist at opioid receptors"),
and no source read uses it of sigma-1; that it was carried over from the opioid description is this pass's
inference, not something a source states.

**Config route.** The opioid targets can be added through `configs/drug_target_additions.csv`, since ChEMBL names
none of them for this drug. The sigma-1 sign has no config route (section 2).

### Finding 5. Bupropion is a non-competitive antagonist of neuronal nicotinic receptors (three independent sources)

**Claim.** ChEMBL_37 (parent CHEMBL894: DAT and NET INHIBITOR rows only, mec 689, 690, 888, 907) and GtoPdb
(ligand 7135: NET and DAT only) carry no nicotinic target. The US labels are silent: Wellbutrin XL (set a435da9d)
"it is presumed that this action is mediated by noradrenergic and/or dopaminergic mechanisms", and the
smoking-cessation SR labels (sets 2bb61b34, 8069c521) "presumed to be related to noradrenergic and/or
dopaminergic mechanisms". Three laboratories show functional, non-competitive blockade:
- Slemmer, Martin and Damaj 2000, JPET (PMID 10991997; Virginia Commonwealth University; abstract), titled
  "Bupropion is a nicotinic antagonist". α3β2, α4β2 and α7: "It was approximately 50 and 12 times more effective
  in blocking alpha(3)beta(2) and alpha(4)beta(2) than alpha(7.) This functional blockade was noncompetitive".
- Fryer and Lukas 1999, JPET (PMID 9862757; Barrow Neurological Institute; abstract). Muscle-type and ganglionic
  (α3β4-type) receptors: "Functional blockade of human muscle-type and ganglionic nAChR is produced by each of
  the drugs in the low to intermediate micromolar range", "suggesting noncompetitive inhibition of nAChR
  function".
- Mansvelder, Fagen, Chang, Mitchum and McGehee 2007, Biochem Pharmacol 74:1283-1291 (PMID 17868653; University
  of Chicago; abstract): "Bupropion is a broad-spectrum non-competitive nicotinic receptor antagonist"; at a
  clinically relevant concentration "Nicotinic receptors on VTA DA neurons and their synaptic inputs are
  inhibited by 75 - 95% after bupropion treatment."

**Disagreement, recorded.** None on direction. Coverage differs: only Slemmer names α4β2, α3β2 and α7; Fryer and
Lukas cover muscle and ganglionic types; Mansvelder shows native VTA receptors without naming subunits. So each
single subtype rests on one paper, and the class-level claim on three. The label, ChEMBL and GtoPdb omit the
action; they do not contradict it. No potency was taken from these abstracts, so an affinity column would be
empty.

**Config route.** `configs/drug_target_additions.csv`, as cocaine's transporters were added: ChEMBL names no
nicotinic target for bupropion, so `added_targets` does not refuse it. Each row needs a ChEMBL target id whose
record in the build's `targets.json` lists the added gene (lines 476-483). That file is not on disk, so the ids
were not chosen.

### Finding 6. Levetiracetam's CACNA1B edge is not supported by the labels read

**Claim.** ChEMBL_37 mec 990 writes levetiracetam as BLOCKER (−1) of CHEMBL4478, the N-type channel subunit
CACNA1B. This is levetiracetam's only non-zero edge. The row's one reference is DailyMed set
90b553fe-4e94-4cce-b5df-ea3e6487930d.
- That set was not among the labels read. The three current UCB Keppra labels saved (sets 2919e43b, 3ca9df05,
  c6d5784d) contain neither "N-type" nor "calcium" anywhere in the record.
- Löscher et al. 2016 lists, among reported cellular effects, "inhibition of high-voltage-gated (N-type) calcium
  and AMPA currents". It is a review tied to UCB, and the primary papers it cites for this were not read.

**Where it stands.** One database row, whose cited label was not read and whose claim the current labels do not
make, and one review sentence. No primary source and no independent second source has been read. The edge is
neither confirmed nor refuted; it is unverified, and it is a candidate for route 1 of item 14 (label mechanism
text against target rows).

**Config route.** If it is to be removed, `configs/drug_target_exclusions.csv` does it (a row for CHEMBL1286 and
CHEMBL4478). Keeping it needs nothing. Removing it would leave levetiracetam with SV2A at sign 0 only, the same
state as the five drugs decision 9.68 names.

## 2. The code routes

All line numbers are in `mechanistic_pathway_learning/perturbation/map_drug_targets_to_graph_nodes.py` at
`f2729f1`, read and not run.

**Re-signing a MODULATOR target that ChEMBL already names has no config route. It needs code.** Four lines close
the four tables:

1. Line 132, the sign itself: `"MODULATOR": 0.0,`
2. `configs/curated_drug_targets.csv` is the fallback for a drug with no ChEMBL target. The docstring at lines
   63-64: "configs/curated_drug_targets.csv, which is read only for a drug whose ChEMBL route gives no target".
   `mechanistic_pathway_learning/evidence/assemble_evidence_table.py` line 850:
   `if not drug_targets and not withheld and curated_targets_by_perturbation and event.stitch_flat_id in curated_targets_by_perturbation:`
   All six drugs have ChEMBL targets, so a row there is never read.
3. `configs/chembl_action_conflict_resolutions.csv` is consulted only for a conflict. Lines 584-585:
   `action_type = rows[-1][1].get("action_type")` then `if len(action_types) > 1:`. A target with one action type
   keeps ChEMBL's.
4. `configs/drug_target_additions.csv` refuses a target ChEMBL names. Lines 470-472:
   `if target_id in named_target_ids:` raises "is a target the drug's ChEMBL mechanism rows name already; a
   curated action for it belongs in configs/chembl_action_conflict_resolutions.csv, and a removal in
   configs/drug_target_exclusions.csv". Line 605 passes `set(rows_by_target)` as `named_target_ids`: every target
   the rows name, excluded or not.

So cariprazine at CHEMBL217 and CHEMBL234, pentazocine at CHEMBL287 and either drug at SV2A CHEMBL1998 cannot be
re-signed from a config file. Item 14's premise that the rows "go to `configs/curated_drug_targets.csv`" does not
hold for drugs that have ChEMBL targets. The code change would be either a new override keyed on drug and target,
or widening the conflict-resolution path to a single action type the sign map reads as 0.

**One possible config-only route, for the gabapentinoids alone.** The refusal at line 470 is keyed on the ChEMBL
target id. Gabapentin's and pregabalin's rows name the complex CHEMBL2363032. ChEMBL_37 also has the
single-protein targets CHEMBL1919 (α2δ subunit 1) and CHEMBL3896 (α2δ subunit 2), which mirogabalin's rows use
(mec 5441, 5442). So:
- exclude CHEMBL2363032 whole for CHEMBL940 and CHEMBL1059 in `configs/drug_target_exclusions.csv`;
- add CHEMBL1919 with gene CACNA2D1 and a signed action for each drug in `configs/drug_target_additions.csv`.

The added id differs from the named one, so line 470 does not fire, and the exclusion check at line 473 looks
only at the added id. **It depends on:**
- the build's `targets.json` holding CHEMBL1919 with CACNA2D1 in its gene symbols, and being human (lines
  476-483 raise otherwise). No ChEMBL target cache is on disk, so this is unchecked;
- the owner accepting the form: an exclusion paired with an addition in place of a re-sign, and the action type
  and sign of the added row (section 3);
- the route actually running. It was read from the code, not run. In particular, what the binding-site machinery
  does once the complex is excluded is unknown: `configs/binding_sites.csv` holds 26 gabapentin rows on the
  complex (lines 112-137) and none for pregabalin;
- CACNA2D1 being a node of the current graph (section 4);
- α2δ-2. `perturbation/gtopdb_drug_targets.py` line 223 already reads `"alpha2delta-1": ("CACNA2D1", "CACNA2D2"),`
  under the comment "gabapentin and pregabalin bind the alpha-2-delta auxiliary subunits, both of them". That
  table takes effect only when GtoPdb names two or more subunits of the complex, and GtoPdb names none for either
  drug, so today the complex is kept whole at sign 0. A second addition at CHEMBL3896/CACNA2D2 would follow
  Hendrich, but CACNA2D2 was not a node of the one graph checked.

The route is specific to these two drugs because only their MODULATOR row names a complex that has
single-protein counterparts. It does not help cariprazine, pentazocine's sigma-1 or SV2A.

**Routes that exist as the code stands:** pentazocine's opioid targets and bupropion's nicotinic targets by
addition; levetiracetam's CACNA1B by exclusion.

## 3. What is the owner's to rule

1. **The sign magnitude at α2δ.** The sources give a negative direction. They do not choose between −1
   (INHIBITOR or BLOCKER) and −0.5 (NEGATIVE ALLOSTERIC MODULATOR). The physiology on record: the drug binds an
   auxiliary subunit, not the pore; the acute effect on current is "either very minor or absent"; the chronic
   effect is impaired trafficking. With it: whether the target is α2δ-1 alone or α2δ-1 and α2δ-2, and whether
   pregabalin takes gabapentin's direction as a class inference, since its own direction rests on one source
   family. Gabapentin and pregabalin are related cases, each to be ruled on its own.
2. **Whether SV2A stays at sign 0** for levetiracetam and for brivaracetam, each on its own. The sources read
   establish the target and no direction, and the hints conflict. Brivaracetam's binding rests on UCB's family
   alone in what was read.
3. **Pentazocine.** (a) The sigma-1 sign: agonist on the referenced literature (two lines for the (+) enantiomer,
   one family for the (−)), antagonist on one unreferenced GtoPdb row, or held at 0. (b) The missing opioid
   targets: whether to add OPRK1 and OPRM1, and OPRD1 on GtoPdb alone; and at kappa, the label's "agonist" (+1)
   or GtoPdb's "Partial agonist" (+0.5).
4. **The code question.** Whether to write an override for a single MODULATOR row (needed for cariprazine, for
   pentazocine's sigma-1 and for any SV2A sign), and in what form; and whether the gabapentinoids take the
   config-only exclusion-plus-addition route or wait for that override.

Three smaller rulings follow from the findings: cariprazine as PARTIAL AGONIST (+0.5) at DRD2 and DRD3, which
the sources support and which waits only on ruling 4; bupropion's nicotinic addition, with its subunits and its
action type (ANTAGONIST or BLOCKER at −1, or NEGATIVE ALLOSTERIC MODULATOR at −0.5 for a non-competitive
block); and levetiracetam's CACNA1B edge, which needs a primary source read before it is kept or removed. Any of
these that changes a drug's edges can move the perturbation set (decision 9.117's rule).

## 4. The graph-version caveat

**Node membership was checked on the v0.4 release graph only, and that is history.** The check read
`data/releases/v0.4/graph_full/nodes.parquet` (MANIFEST created 6 October 2026) on 24 November 2026. On that graph
the gene nodes CACNA2D1, CACNA2D3, CHRNA3, CHRNA4, CHRNA5, CHRNA7, CHRNB2, CHRNB4, OPRK1, OPRM1, OPRD1, SIGMAR1,
SV2A, DRD2, DRD3, CACNA1B, KCNQ3 and KCNQ5 are present, and CACNA2D2 and CACNA2D4 are absent. v0.4 predates the
decisions that changed the graph's structure, so under "A measurement carries the graph it was taken on" this
says nothing about the current graph. The v5 graph and its tables are not on disk (`data/processed` is absent),
so membership on the current graph is unchecked. Every statement above of the form "is a graph node" or "can be
added" carries that limit, and it has to be checked again on the build the rows are written for.

Two further limits of the same kind. The set of six drugs was reconstructed from decision 9.117's rule, SIDER 4.1
and the OnSIDES bridge of the v0.4 release, not from the v5 assembler; it matches the recorded count of six. And
no ChEMBL target cache is on disk, so no added row's ChEMBL target id was checked against `targets.json`.

## Sources not read, and what rests on them

- Field 2006 full text (two routes failed): nothing rests on it; the residue is struck.
- Tadori 2011 and Mansvelder 2007: abstracts only (Mansvelder's full text answered HTTP 500).
- Hayashi and Su 2004, and GtoPdb's opioid references (PMID 9686407, 9262330): cited through Cobos and GtoPdb,
  not read. The (+)-pentazocine agonist line and the delta row rest on them.
- DailyMed set 90b553fe and the primary papers behind Löscher's N-type sentence: not read. Finding 6 is open for
  that reason.
- EU product information was not read for any of the six.
