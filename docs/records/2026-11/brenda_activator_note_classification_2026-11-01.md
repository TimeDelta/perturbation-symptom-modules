# BRENDA activating-compound notes stating no effect: a reading for sign-off (1 November 2026)

Measured and read on `data/brenda/brenda_2026_1_human_regulation_subset.json.gz` (BRENDA release 2026.1, the
committed human subset whose extraction is byte-identical to the full release). All note text quoted below is from
that release; BRENDA 2026.1 is licensed CC BY 4.0 (verified in `docs/data_sources.md`), so quotation with attribution
is permitted. Model: this reading was done on Fable 5.1.

## What this is for

The owner ruled on 26 October 2026 that "\"no effect\" should not have an activates edge", and asked that the wording
of each activating-compound note stating no effect be read in full and that the owner sign off on the classes **before
any rule is built** (decision 9.88). Until now the extractor writes every activating-compound entry of a human protein
as `activates`, whatever its note says, and only counts how many carry a no-effect note. This page is that reading. It
makes no ruling and builds nothing: it records, for each note, what the no-effect is about, whether activation of the
same human enzyme is stated, and which of three relations the note supports —

- `activates`: activation of this human enzyme is stated (the no-effect is a comparison or a control, scoped to another
  isozyme, substrate, activity, cell line, concentration, or a variant of the compound);
- `no_activation`: a negative observation about this human enzyme, which would go to a negative table and never to the
  edges (the mirror of a `no_inhibition` row);
- no row: the note says nothing about this human enzyme in either direction (the absence is scoped elsewhere, or the
  note is mis-sorted).

Rows I could not class with confidence are marked `uncertain` and are grouped at the end for the owner to rule on.

## Classes and counts

Two sets, kept apart because the owner is asked to confirm the widening of the pattern separately (see the last
section). The 47 are what the current extractor counts (its `NO_INHIBITION_OR_EFFECT` pattern matches the note); the 25
are what a widened pattern aimed at "no activation", "not activated", "does not activate" and two forms beyond the
handoff would add. The two sets are disjoint.

**The 47 notes the extractor counts today:**

| Relation | Count |
|---|---|
| `activates` (activation stated, no-effect scoped elsewhere) | 38 |
| `no_activation` (negative about this human enzyme) | 2 |
| no row (nothing about this enzyme, or mis-sorted) | 2 |
| `uncertain` | 5 |
| **total** | **47** |

The two `no_activation` are C1 (pyrazole on EC 1.1.1.284, whole note "no effect") and C13 (Ca2+/calmodulin on
EC 2.7.1.23, "no detectable effect on recombinant human NAD kinase"). These are the only two of the 47 that are a clean
negative about the human enzyme itself. The remaining 45 either state activation of this enzyme beside the no-effect
(38), support no row (2), or are uncertain (5).

**The 25 notes a widened pattern would add:**

| Relation | Count |
|---|---|
| `activates` | 21 |
| `no_activation` | 0 |
| no row | 1 |
| `uncertain` | 3 |
| **total** | **25** |

Not one of the 25 is a `no_activation` negative about this human enzyme. Widening the pattern therefore adds no new
negatives to a negative table; its only effect would be the risk of wrongly suppressing the 21 that are activations.

## The odd case: phosphate on EC 2.7.6.1

The handoff flagged phosphate, listed as an activating compound on EC 2.7.6.1 (ribose-phosphate diphosphokinase),
whose note reads "no inhibition up to 75 mM". Six other phosphate records on the same human entry state it is a
requirement or an activator ("specific and absolute requirement", "required for enzymatic activity by class 1 PRSs").
This one note is a mis-sorted inhibitor observation: it says phosphate does not inhibit, which is neither an activation
nor a negative observation about activation. It supports **no row** from the activator field. It does not belong in a
`no_activation` table either, because it is about inhibition, not activation. The current `NO_INHIBITION_OR_EFFECT`
pattern catches it only because of the word "inhibition"; any activator rule should not route it to a negative.

## The full reading

| Row | EC | Activating compound | UniProt | What the no-effect is about | Activation of this enzyme stated? | Relation | Note quote (BRENDA 2026.1) |
|---|---|---|---|---|---|---|---|
| C1 | 1.1.1.284 | pyrazole | — | this enzyme | no | `no_activation` | "no effect" |
| C2 | 1.1.1.40 | succinate | — | another isozyme (the cytosolic enzyme) | yes | `activates` | "increases activity of the mitochondrial enzyme ..., no effect on the activity of the cytosolic enzyme" |
| C3 | 1.1.1.40 | fumarate | — | another isozyme (the cytosolic enzyme) | yes | `activates` | "increases activity of the mitochondrial enzyme ..., no effect on the activity of the cytosolic enzyme" |
| C4 | 1.1.1.42 | liposome | — | another compound (DPPC liposomes) | yes | `activates` | "ICDH activity is enhanced with liposomes at 5 mol% cardiolipin, but inhibited at 30 mol% ... 1,2-Dipalmitoyl-sn-glycero…" |
| C5 | 1.1.1.62 | retinoic acid | — | a concentration (0.0001 mM) | yes | `activates` | "0.001 mM, significant stimulation ..., 0.0001 mM has no effect" |
| C6 | 1.4.4.2 | lipoylated H-protein | P23378 | a modification of the activator (the lipoyl moie | no | `uncertain` | "the presence of the lipoyl moiety on H-protein does not affect the rates of GLDC ... glycine decarboxylation" |
| C7 | 1.6.3.1 | phorbol 12-myristate 13-acetat | — | another compound (GDP-loaded Rac1); unchanged co | yes | `activates` | "GTP-bound Rac1 ... enhanced up to 1.5-fold ..., but GDP-loaded Rac1 does not affect superoxide generating kinetics" |
| C8 | 2.3.1.5 | 5-methoxypsoralen | — | a concentration range (5-25 mM) | yes | `activates` | "activates the enzyme at 50 mM in Colo 205 cells, inhibitory at lower dosage of 0.05-0.5 mM ..., concentrations of 5-25 …" |
| C9 | 2.3.1.50 | small activating subunit of se | — | a truncation of the activator (N-terminal 10 res | yes | `activates` | "activate the catalytic hLCB1/hLCB2 heterodimer ... Deletion of the N-terminal 10 amino acids ... has no effect on the a…" |
| C10 | 2.4.1.17 | Phenobarbital | — | other substrates (morphine, chloramphenicol) | yes | `activates` | "induces activities towards bilirubin and 1-naphthol whereas does not affect activities against morphine and chloramphen…" |
| C11 | 2.7.1.127 | Protein kinase C | — | a kinetic property (sensitivity to Ca2+/calmodul | yes | `activates` | "calmodulin kinase II and protein kinase C added together results in a maximal 60-70fold activation, but protein kinase …" |
| C12 | 2.7.1.127 | CaM kinase II | — | a kinetic property (sensitivity to Ca2+/calmodul | yes | `activates` | "CaM kinase II alone activates 35-40fold in the presence of Ca2+ and calmodulin" |
| C13 | 2.7.1.23 | Calmodulin | O95544 | this enzyme (recombinant human NAD kinase) | no | `no_activation` | "Ca2+/calmodulin has no detectable effect on recombinant human NAD kinase" |
| C14 | 2.7.1.68 | spermine | — | another isozyme (type II enzyme) | yes | `activates` | "2 mM, 4fold increase in activity of type I enzyme, no effect on type II enzyme" |
| C15 | 2.7.10.2 | EPQYEEIPIYL | — | a downstream effect (Kv1.3 channels), not this e | yes | `activates` | "binds to the SH2 domain of the src-kinase and activates it, activation of endogenous src-PTKs does not inhibit Kv1.3 ch…" |
| C16 | 2.7.11.1 | FRAT-2 | — | another activity (unprimed-site phosphorylation) | yes | `activates` | "activates phosphorylation of primed sites of tau protein about 8fold, no effect on unprimed site phosphorylation" |
| C17 | 2.7.11.20 | MG132 | — | another condition and cell line (hypoxic MCF10A, | yes | `activates` | "results in a 5- to 10fold increase in eEF2K levels but has no effect on hypoxic MCF10A or HTB20 cells" |
| C18 | 2.7.11.22 | p34SEI-1 | — | binding, by other proteins (p16, p18) | yes | `activates` | "binds directly to CDK4 and activates it at lower concentrations, but inhibits the enzyme at higher concentrations, ... …" |
| C19 | 2.7.11.26 | FRAT-2 | — | another activity (unprimed-site phosphorylation) | yes | `activates` | "activates phosphorylation of primed sites of tau protein about 8fold, no effect on unprimed site phosphorylation" |
| C20 | 2.7.11.26 | forskolin | — | this enzyme if the entry is GSK-3; the stated in | yes | `uncertain` | "forskolin specifically induces tau hyperphosphorylation by PKA at Ser214 ..., forskolin has no effect on GSK-3" |
| C21 | 2.7.6.1 | phosphate | — | inhibition of this enzyme | no | `no_row` | "no inhibition up to 75 mM" |
| C22 | 2.7.7.86 | Plasmodium falciparum genomic  | Q8N884 | another condition (cGAS-/- cells) | yes | `activates` | "activates cGAS in vivo in THP-1 cells, no effect in enzyme-deficient cGAS-/- THP-1 cells" |
| C23 | 2.8.2.4 | nomegestrol acetate | — | a concentration (high) | yes | `activates` | "stimulates at low concentrations, but has no effect at high concentrations" |
| C24 | 2.8.2.4 | 17-hydroxy-19-nor-7-methyl-17- | — | another cell line (MDA-MB-231) | yes | `activates` | "0.0005-0.00005 mM stimulates the formation of estrone by 40-60%, no effect in MDA-MB-231 cells" |
| C25 | 3.1.1.25 | apolipoprotein apoA-I | P27169 | other compounds (apoA-IV, apoA-II) | yes | `activates` | "only apolipoprotein apoA-I is capable of stimulating the lactonase activity, while apoA-IV and apoA-II have almost no e…" |
| C26 | 3.1.1.3 | CGI-58 | — | another enzyme (HSL) | no | `no_row` | "ATGL activity is greatly enhanced by ... CGI-58. CGI-58 does not affect HSL enzyme activity" |
| C27 | 3.1.1.4 | 12-O-tetradecanoylphorbol-13-a | — | another readout (Prdx6 expression) | yes | `activates` | "has no effect on Prdx6 expression but leads to about 75% increase in aiPLA2 activity" |
| C28 | 3.1.1.47 | platelet-activating factor | — | another isozyme/source (erythrocyte isozyme) | yes | `activates` | "regulatory function on the enzyme form from HepG2 cells and monocyte-derived macrophages, no effect on erythrocytes and…" |
| C29 | 3.1.21.1 | okadaic acid | — | another cell line (CEM-VLB100) | yes | `uncertain` | "increases accessibility to DNA in chromatin ..., no effect on CEM-VLB100 cells" |
| C30 | 3.1.3.48 | spermine | — | this enzyme, a concentration (0.02-0.2 mM) | no | `uncertain` | "no effect at 0.02-0.2 mM" |
| C31 | 3.1.3.5 | ATP | — | another isozyme (cNI) | yes | `activates` | "activates cNII, no effect on cNI" |
| C32 | 3.1.3.5 | ammonium pyrrolidin dithiocarb | — | another readout (LPS-induced increase) | yes | `activates` | "increases the basal activity of ecto-5-nucleotidase by 17% but has no effect on the lipopolysaccharide-induced increase" |
| C33 | 3.1.4.39 | heparin | — | another isozyme (ATXbeta) | yes | `activates` | "enhances the lysoPLD activity of isozyme ATXalpha ... up to 2fold, but it has no detectable effect on ... isozyme ATXbe…" |
| C34 | 3.1.6.2 | 1alpha,25-dihydroxyvitamin D3 | — | other agonists/antagonists (RAR, nuclear VDR) | yes | `activates` | "upregulation of enzyme activity ... retinoic acid receptor specific agonists and antagonist have no effect" |
| C35 | 3.4.21.75 | heparin | — | another substrate (low-pathogenic Mexico H5N2 pe | yes | `activates` | "Heparin ... dramatically enhances processing ... It has no effect on processing of low pathogenic Mexico H5N2 peptide" |
| C36 | 3.4.22.61 | lithium/SB-415286 | — | a condition (the agents alone; healthy hepatocyt | yes | `activates` | "the agents have no effect alone ..., 1.5-2.1fold activation of CH-11-induced apoptosis" |
| C37 | 3.4.24.11 | K49-P1-20 | P08473 | a modification of the activator (N-terminal biot | yes | `activates` | "enhances the activity of neprilysin to 1605% of control ... biotinylation ... has no significant effect on its ability …" |
| C38 | 3.4.24.19 | PCPE-1 | — | other substrates (procollagen VII, laminin etc.) | yes | `activates` | "enhances degredation of procollagen type I 5 fold ..., has no effect on the in vitro BMP-1 processing of procollagen VI…" |
| C39 | 3.4.24.35 | phorbol 12-myristate 13-acetat | — | other compounds (arachidonic/eicosapentaenoic ac | yes | `activates` | "phorbol 12-myristate 13-acetate ..., a known activator of MMP-9 secretion ... Addition of ... arachidonic acid ... alon…" |
| C40 | 3.6.5.1 | RGS14 protein | — | another activity (GTPase activity / nucleotide d | no | `uncertain` | "Purified R14-RBD alone has no appreciable effect on the GTPase activity ...; The GPSM domain ... does not inhibit recep…" |
| C41 | 7.6.2.2 | cholesterol | — | a substrate-size class (800-900 Da drugs) | yes | `activates` | "does not affect that of drugs with molecular mass of between 800 and 900 ... Cholesterol enhances paclitaxel-stimulated…" |
| C42 | 7.6.2.2 | diazepam | — | another activity (daunorubicin efflux) | yes | `activates` | "stimulation of ATPase activity, no effect on daunorubicin efflux" |
| C43 | 7.6.2.2 | Chlordiazepoxide | — | another activity (daunorubicin efflux) | yes | `activates` | "stimulation of ATPase activity, no effect on daunorubicin efflux" |
| C44 | 7.6.2.2 | auraptene | — | another activity (MRP1-mediated efflux) | yes | `activates` | "stimulates the ATPase activity of MRP1. No inhibition of MRP1-mediated efflux ..., but auraptene increases the accumula…" |
| C45 | 7.6.2.2 | bromazepam | — | another activity (daunorubicin efflux) | yes | `activates` | "stimulation of ATPase activity, no effect on daunorubicin efflux" |
| C46 | 7.6.2.2 | glutathione | — | other substrates / another isozyme (MRP3) | yes | `activates` | "5 mM free GSH activates the indomethacin transport by MRP1, no effect on the other substrates tested or on MRP3 activity" |
| C47 | 7.6.2.2 | verapamil | — | another activity (daunorubicin efflux) | yes | `activates` | "stimulation of ATPase activity, no effect on daunorubicin efflux" |
| W1 | 1.14.14.32 | cytochrome b5 | P05093 | a mutant of the activator (H67A, Zn-substituted  | yes | `activates` | "Rat cytochrome b5 stimulates ... human CYP17A1 by a factor of 5. The H67A mutant ... fail to stimulate" |
| W2 | 1.4.1.3 | ADP | — | a mutant of this enzyme (R463A) | no | `no_row` | "no activation of R463A mutant enzyme" |
| W3 | 1.6.3.1 | Rac1 | — | another isozyme (Nox4) | yes | `activates` | "Nox1 is stimulated by constitutively active Rac1 ... Rac1 does not activate Nox4 in transfected cells" |
| W4 | 2.1.1.37 | methylated DNA | — | mutants of this enzyme (N-terminal deletions) | yes | `activates` | "stimulated methylation spreading ... for full-length and the mutant lacking 121 N-terminal amino acids equally well. No…" |
| W5 | 2.3.1.48 | bleomycin | — | another form (free, non-ATM-associated Tip60) | yes | `activates` | "activation of the ATM-associated enzyme by bleomycin, the free, non-ATM-associated, Tip60 activity is not activated by …" |
| W6 | 2.4.1.11 | Insulin | — | a disease condition (type 1 diabetes patients) | yes | `activates` | "stimulation of activity. In patients with type 1 diabetes ... insulin does not stimulate the enzyme activity" |
| W7 | 2.7.1.74 | 2'-deoxyadenosine/deoxycoformy | — | the compound applied alone (no cofactor) | yes | `activates` | "no stimulation of enzyme activity by either compound if applied alone, with both compound at 0.01 mM 2.4fold activation…" |
| W8 | 2.7.11.1 | cytokine | P42336 | another activity (lipid-kinase signaling / proli | yes | `activates` | "sufficient for activating the protein kinase activity of PI3K ... but did not activate PI3K lipid kinase signaling" |
| W9 | 2.7.11.22 | RV-cyclin | — | other isozymes (Cdk7, Cdk9) | yes | `activates` | "enhances CDK8 kinase activity ... It is specific for cdk8, no activation of Cdk7 or Cdk9" |
| W10 | 2.7.11.31 | O2 | — | a cell line (rho0-A549, mitochondrion-deficient) | yes | `activates` | "hypoxia leads to time-dependent AMPK activation ... Hypoxia fails to activate AMPK in mitochondrion-deficient rho0-A549…" |
| W11 | 2.7.7.84 | viral dsRNA | — | other nucleic acids (ssRNA, DNA) | yes | `activates` | "activated by viral double-stranded RNA ... ssRNA or DNA does not activate this class of enzymes" |
| W12 | 2.7.7.86 | dsDNA | Q8N884 | a substrate length (12 bp dsDNA) / another organ | yes | `activates` | "presence of dsDNA activates cGAS. dsDNA of 12 bp in length does not activate mcGAS efficiently" |
| W13 | 3.4.21.77 | CVFAHNYDYLVC | P07288 | an inactive derivative of the activator peptide | yes | `activates` | "stimulates the activity of the enzyme ... No activation of the enzyme by the inactive derivative of peptide B2-NH2" |
| W14 | 3.5.1.98 | N-[(3,5-dimethoxyphenyl)carbam | — | other isozymes (other HDACs) | yes | `activates` | "8.4fold activation of HDAC8. No activation of other HDAC isoenzymes" |
| W15 | 3.5.1.98 | N-(cyclohexylcarbamothioyl)ben | — | other isozymes (other HDACs) | yes | `activates` | "5.6fold activation of HDAC8. No activation of other HDAC isoenzymes" |
| W16 | 3.5.1.98 | N-(phenylcarbamothioyl)benzami | — | other isozymes (other HDACs) | yes | `activates` | "12fold activation of HDAC8. No activation of other HDAC isoenzymes" |
| W17 | 3.5.3.1 | IL-4 | — | a condition/cell type (alveolar macrophages, IL- | yes | `activates` | "up to 16-fold stimulation of enzyme activity in RAW-264.7 cell ... No stimulation of enzyme in alveolar macrophages by …" |
| W18 | 3.5.4.9 | 2',5'-ADP | — | another activity (reverse cyclohydrolase) | no | `uncertain` | "analog of NADP+ does not stimulate the reverse cyclohydrolase activity" |
| W19 | 3.5.4.9 | 5'-ADP | — | another activity (reverse cyclohydrolase) | no | `uncertain` | "analog of NADP+ does not stimulate the reverse cyclohydrolase activity" |
| W20 | 3.6.5.2 | GTPase activating protein GAP | — | this enzyme | no | `uncertain` | "no stimulation of GTP hydrolysis" |
| W21 | 4.1.1.15 | asiaticoside | Q05329 | a condition (absence of PLP) | yes | `activates` | "stimulates at 0.0104 mM in vitro by 22%. No stimulation is observed in the absence of pyridoxal 5-phosphate" |
| W22 | 4.2.1.22 | S-adenosyl-L-methionine | P35520 | a mutant/form (truncated enzyme) | yes | `activates` | "3fold activation, allosteric regulator of the full length enzyme, does not activate the truncated enzyme" |
| W23 | 4.6.1.2 | NO | Q02153 | nothing else; a long mechanistic overview | yes | `activates` | "nitric oxide (NO) binds to soluble guanylyl cyclase (GC1) and stimulates its catalytic activity" |
| W24 | 4.6.1.2 | GCAP1 | Q02846 | a mutant of the activator (GCAP1 M26R) | yes | `activates` | "GCAP1 and GCAP2 activate RetGC1 ... GCAP1 mutant M26R binds but does not activate RetGC1" |
| W25 | 5.6.2.6 | RNA | O60306 | another substrate form (blunt-ended RNA duplex) | yes | `activates` | "highly stimulated in the presence of a 22-nt RNA ... the latter does not stimulate Aquariuss ATPase activity" |

## Uncertain rows, for the owner to rule on

- **C6 (EC 1.4.4.2, lipoylated H-protein):** "the presence of the lipoyl moiety on H-protein does not affect the rates of GLDC ... glycine decarboxylation"
  The absence compares two forms of the compound (lipoylated and not) and says nothing about H-protein against no H-protein. Literal reading: an absence about this enzyme with no activation stated, so no_activation; physiological reading: the note does not deny that H-protein acts on GLDC. H-protein is a protein partner and will not map to a metabolite.
- **C20 (EC 2.7.11.26, forskolin):** "forskolin specifically induces tau hyperphosphorylation by PKA at Ser214 ..., forskolin has no effect on GSK-3"
  EC 2.7.11.26 (tau-protein kinase) protein entry #4 has no accession and no comment; BRENDA files GSK-3beta there. If the entry is read as GSK-3 the note is a no_activation; if as 'a tau-protein kinase' the stated effect is on PKA (EC 2.7.11.11), which is not this enzyme either. Either way the note does not support activates.
- **C29 (EC 3.1.21.1, okadaic acid):** "increases accessibility to DNA in chromatin ..., no effect on CEM-VLB100 cells"
  FLAG: okadaic acid is a phosphatase inhibitor; the note describes chromatin/apoptosis effects, not activation of EC 3.1.21.1 (DNase). The absence is scoped to a cell line, so no negative row; but the note does not clearly support activates of this enzyme either. Owner should see it.
- **C30 (EC 3.1.3.48, spermine):** "no effect at 0.02-0.2 mM"
  FLAG: a second spermine record on the same protein entry #7 reads 'activation', and an inhibitor record reads '2.0-20 mM'. Read alone this note is a bounded no-effect that is a negative observation; read with the activation record it is the low end of a dose response. The mirrored rule classes this record as no_activation and the other as activates, producing both for the same ligand/enzyme. Owner should decide whether a bounded no-effect beside an activation record is kept.
- **C40 (EC 3.6.5.1, RGS14 protein):** "Purified R14-RBD alone has no appreciable effect on the GTPase activity ...; The GPSM domain ... does not inhibit receptor-stimulated GTPase activity"
  FLAG: a long overview note about RGS14 domains. 'GTPase accelerating protein activity' is stated of the RGS domain but the specific clauses caught are the two absences (RBD has no effect; GPSM does not inhibit). The enzyme here is EC 3.6.5.1 (heterotrimeric G-protein GTPase). The note's net direction for this entry is unclear; owner should see it.
- **W18 (EC 3.5.4.9, 2',5'-ADP):** "analog of NADP+ does not stimulate the reverse cyclohydrolase activity"
  FLAG: EC 3.5.4.9 (methenyltetrahydrofolate cyclohydrolase, part of MTHFD1). The note denies stimulation of one activity and states nothing positive here. Could be no_activation (about this enzyme's reverse activity) or no_row (about 'another activity'). 'reverse cyclohydrolase activity' is this enzyme's own reaction, so leans no_activation. Owner should see it. 2',5'-ADP.
- **W19 (EC 3.5.4.9, 5'-ADP):** "analog of NADP+ does not stimulate the reverse cyclohydrolase activity"
  As W18. 5'-ADP.
- **W20 (EC 3.6.5.2, GTPase activating protein GAP):** "no stimulation of GTP hydrolysis"
  FLAG: EC 3.6.5.2 entry #10 has eight other GAP activating records stating activation of GTP hydrolysis (up to 1000fold). This bare clause names no scope, so scope_elsewhere returns None and the mirrored rule makes it no_activation, standing beside many activates rows for the same ligand term. A bounded/context-free no-effect beside strong activation: owner should decide.

Two themes run through these: (i) a bare no-effect record that sits beside a separate activation record for the same
compound and enzyme (C30 spermine, W20 GAP), where reading the record alone gives a negative but reading the pair gives
a dose or context dependence; and (ii) a no-effect about one of the enzyme's own activities or forms (C40 RGS14,
W18/W19 reverse cyclohydrolase, C20 forskolin/GSK-3), where whether that counts as a negative about "this enzyme"
depends on how narrowly the enzyme is defined. C6 and C29 are notes whose caught clause ("does not affect", "no effect
on CEM-VLB100 cells") is real but peripheral to what the note is about.

## A proposed shape for the rule (proposal only)

This mirrors `relation_of_notes` for the inhibition fields:

1. a `STATES_ACTIVATION` pattern — `activat\w*`, `stimulat\w*`, `enhanc\w*`, `increas\w*`, an "N-fold" and a
   "% activation" — the positive counterpart of `STATES_INHIBITION`;
2. an activator-absence pattern — the widened forms, confirmed below;
3. a classifier that, per note: keeps `activates` when activation of this enzyme is stated beside the absence; writes a
   `no_activation` negative row when the absence is about this enzyme and no activation of it is stated; writes no row
   when the absence is scoped elsewhere only; and in the mapping (`map_brenda_regulation_to_graph.py`) routes
   `no_activation` to a negative table and never to the edges, extending the `relation_type == NO_INHIBITION_RELATION`
   test near line 187.

**But a direct mirror is not safe here, and the reading shows why.** A faithful mirror of `relation_of_notes`, run over
these 72 notes, agrees with the hand reading on only 36 of the 64 classed rows. An inhibitor note is clean ("compound X
did not inhibit"); an activator no-effect note is almost always **comparative** ("activates X, no effect on Y"), where
the positive is the finding and the no-effect is a control on another isozyme, substrate, activity, cell line or
concentration. The mirror fails on these because the positive clause itself names the other form, so it is scoped
elsewhere and fails the "activation of this enzyme, unscoped" test, while the negative clause is also scoped elsewhere —
and the note collapses to no row or, when the negative clause carries no scope marker, to `no_activation`, suppressing a
real activation. Two concrete gaps, both of which the handoff suspected:

- **`scope_elsewhere` does not recognise "another substrate or activity" or "another cell line".** Confirmed: it
  returns None for "no effect on daunorubicin efflux" (C42), "no effect in MDA-MB-231 cells" (C24), "ssRNA or DNA does
  not activate this class of enzymes" (W11) and "does not stimulate the reverse cyclohydrolase activity" (W18). It also
  misses isozymes named only by abbreviation or by a bare gene-name ("no effect on cNI" C31, "does not activate Nox4"
  W3). Unless these are added, the rule will route genuine activations to a negative table.
- **The widened pattern must make the activation words case-sensitive (lowercase "no"), or exclude the ligand name.** A
  case-insensitive "no activation" matches the compound **NO** (nitric oxide) inside "NO activation" (W23, EC 4.6.1.2),
  a false positive that turns a textbook activation of soluble guanylyl cyclase into a negative.

Given that the 72 notes yield only 2 clean `no_activation` negatives among the 47 (C1, C13) and 0 among the 25, a
conservative rule is defensible: emit `no_activation` only when the note states no activation anywhere and the absence
is unambiguously about this human enzyme, and otherwise keep `activates`. The owner's sign-off on the classes in the
table is what should set that threshold.

## The widening, by form, for the owner to confirm or reject each

The handoff proposed three forms and guessed the widening would add "roughly 15"; the real figure under those three
forms is 22, and two further forms the pass added bring it to 25. Broken out:

| Form | Rows added | `activates` | `no_activation` | no row | `uncertain` |
|---|---|---|---|---|---|
| handoff: "no activation" / "no stimulation" | 12 | 10 | 0 | 1 | 1 |
| handoff: "not activated" / "not stimulated" | 1 | 1 | 0 | 0 | 0 |
| handoff: "does not activate" / "does not stimulate" | 9 | 7 | 0 | 0 | 2 |
| beyond the handoff: "did not activate" / "did not stimulate" | 1 | 1 | 0 | 0 | 0 |
| beyond the handoff: "fails to activate" / "fails to stimulate" | 2 | 2 | 0 | 0 | 0 |

No form contributes a single `no_activation` negative. The one no-row (W2, "no activation of R463A mutant enzyme") is
already handled by the existing mutant scope. The "no activation / no stimulation" form carries the one demonstrated
false positive (W23, the compound NO). **On the three rows caught only by the two forms beyond the handoff** (W1
"fail to stimulate", W8 "did not activate", W10 "fails to activate"): all three are activations with a comparative
control, none is a negative, so including those two extra forms adds no negatives and only the risk of a false
suppression. On this evidence they are not worth adding. The three handoff forms likewise add no negatives on this
release; their value, if any, is only in not mis-suppressing — which the `STATES_ACTIVATION` rescue and the
`scope_elsewhere` fixes already cover. The owner may reasonably decline the widening entirely for the activator field.
