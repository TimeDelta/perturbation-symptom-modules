# BRENDA's Ca2+ regulation records read into classes, for decision 9.114 (6 November 2026)

A research pass on Fable 5.1, 6 November 2026. Source table: `data/processed/brenda_regulation_records.csv` (BRENDA release 2026.1,
CC BY 4.0, verified in `docs/data_sources.md`; the comments quoted below are BRENDA's and are quoted with attribution). Graph:
`data/processed/graph_full_neuronal_split_binders_drugs_v5` (built 5 November 2026), whose 263 regulation edges out of `MAM01413c`
are exactly the 263 pairs of `configs/brenda_metabolite_enzyme_regulation.csv` on base `MAM01413` (checked: no pair on either side
is missing from the other). Localisations: `data/raw/uniprot/uniprot_human_reviewed.tsv.gz`, column "Subcellular location [CC]".
Precedent: decision 9.88's reading of the 47 activator notes (`docs/brenda_activator_note_classification_2026-11-01.md`), which
read each note in full and classed it by what the note says about this human enzyme. This page does the same for calcium. It
makes no ruling and changes nothing in the repository.

Files beside this page (committed with it on 6 November 2026):

- `docs/brenda_calcium_records_2026-11-06.csv`: every one of the 880 records with its class and the comment.
- `docs/brenda_calcium_proteins_2026-11-06.csv`: the 234 proteins that carry an edge, with class mix, compartment and the outcome under each rule.
- `docs/brenda_calcium_edges_2026-11-06.csv`: the 263 edges with the records behind each and the outcome under each rule.

## 1. What was read

The task named 746 Ca2+ `metals_ions` records on 166 human proteins. Read whole: the ligand names "Ca2+" (873 rows) and "Calcium"
(7), both of which the mapping resolves to `MAM01413` (the other calcium-named ligands, "calcium/calmodulin", "calcium chloride",
"calcium pentosan polysulfate" and so on, resolve to nothing and are not in the graph; they were not read). Of the 880 human
records, 751 are `metals_ions` (746 "Ca2+" + 5 "Calcium"), 111 inhibitor and 18 activating compound. 311 carry a UniProt
accession stated by BRENDA (166 distinct accessions among the `metals_ions` records: that is the task's 166) and 569 carry none;
the mapping resolves the latter through the EC class when it names exactly one reviewed human accession. After both routes and
the graph-node check, **538 records on 234 proteins make the 263 edges** (470 `metals_ions` on 207 proteins, 56 inhibitor on 45,
12 activating on 11), and 342 records make no edge (the EC class names none or several accessions, or the accession is not a
graph protein). All 880 were read and classed; the per-protein table and the edge counts are over the 538 that make edges.

The `brenda_comment` field is truncated by the extractor at about 300 characters; 40 records have no comment at all (22 of them
inhibitor rows).

## 2. The classes

Each record was classed by reading its comment, by what the comment says about Ca2+ and this enzyme. One class per record; where
a comment says two things the class is the one that bears on whether the record is evidence of regulation by cytosolic calcium in
the living cell. The suggested scheme was kept and adjusted in three ways, each with its reason:

| Class | Definition | Why |
|---|---|---|
| **A** sensing mechanism or physiological range | names calmodulin, an EF-hand, a C2, C2-like or PLAT domain, a Ca2+/GTP switch, a translocation on Ca2+ influx, a cellular Ca2+ rise ("cytosolic", "intracellular", "influx", "ionophore", "oscillations"), or a stated concentration at or below 0.01 mM (10 uM, the ceiling of a cytosolic transient), "micromolar", "nanomolar" or "physiological" | the task's (i); the concentration limb added because a half-maximum of 140 nM (EEF2K) or 400 nM (NADK) is as much a sensing claim as a named domain |
| **B** structural or bound ion | crystal structure, "contains n Ca2+", binding-site residues, stability, dimerisation, membrane binding by a Gla or CUB domain | the task's (ii) |
| **C** bare requirement or activation | "required", "activates", "dependent on", "stimulates", "Ca2+-dependent enzyme", with no concentration and no cellular context | the task's (iii); the 66% the keyword pass could not place |
| **D** requirement at a stated concentration above the cytosolic range | the stated optimum, half-maximum or assay concentration is above 0.01 mM ("5 mM used in assay conditions", "optimum 15 mM", "K0.5 0.18 mM") | split from (iii) because a stated millimolar requirement is positive evidence that the enzyme is not regulated by cytosolic calcium, where a bare "required" is silent; PADI2's own comment says it: "at least 10 times higher than cellular calcium concentrations" |
| **E** inhibition | the ion inhibits; sub-flag `cyt` when the concentration is at or below 0.01 mM or a cellular mechanism is stated ("low concentrations" for AC5/6, "cellular Ca2+ ... lowers SGC activity"), `mM` when 0.1 mM or more is stated, `un` when none is | the task's (iv), with the concentration |
| **F** nonspecific divalent | Ca2+ replaces, is replaced by, or is compared with Mg2+, Mn2+, Co2+ ("20% as effective as Mn2+", "can partially substitute for Mg2+", "either Mg2+ or Ca2+") | the task's (v) |
| **G** no effect or not required | "no effect", "not required", "activity is independent of Ca2+", "Ca2+ alone does not activate" | the 11 the keyword pass found; added so that they are not counted as evidence |
| **H** Ca2+ is the pump's substrate | the EC 7.2.2.10 Ca2+-ATPases (PMCA, SPCA, SERCA), whose "dependent on" is substrate dependence | added: the row's loop question turns on these five |
| **I** indirect, reverse, method or ambiguous | Ca2+ regulates the gene's transcription or the enzyme's secretion, the enzyme causes a Ca2+ signal, a method is described ("temperature dependence ... in presence and absence of Ca2+"), a comment about zinc, or activation and inhibition both stated by substrate | added so that these do not pass as regulation of activity |
| **N** no comment | the record carries no comment (22 of the 40 are inhibitor rows) | the task's (vii) |

The task's (vi), extracellular or secreted enzyme, is a property of the protein and not of the comment, so it is carried as a
**compartment flag per protein** from UniProt's subcellular location, applied on top of the record class: `cyt` (cytosol, nucleus,
or the cytosolic face of a membrane), `ext` (secreted, extracellular matrix, or the extracellular face of the plasma membrane, the
ectoenzymes), `lum` (ER, Golgi, lysosome or secretory-granule lumen), `mito` (mitochondrial matrix), `memb` (a membrane enzyme
whose active-site face UniProt does not state), `pump` (the five Ca2+-ATPases). Twenty proteins have no location text in the
local UniProt table (listed in section 4) and were assigned from the protein's known function, marked `noCC` in the CSV, to be
verified.

## 3. Counts

All 880 records: A 108 (12%) | B 97 (11%) | C 313 (36%) | D 110 (12%) | E 96 (11%) | F 64 (7%) | G 13 (1%) | H 16 (2%) | I 23 (3%) | N 40 (5%).

The 751 `metals_ions` records: A 104 (14%) | B 96 (13%) | C 307 (41%) | D 109 (15%) | E 11 (1%) | F 63 (8%) | G 13 (2%) | H 16 (2%) | I 17 (2%) | N 15 (2%).

The 111 inhibitor records: A 0 (0%) | B 0 (0%) | C 0 (0%) | D 0 (0%) | E 85 (77%) | F 0 (0%) | G 0 (0%) | H 0 (0%) | I 4 (4%) | N 22 (20%). The 18 activating-compound records: A 4 (22%) | B 1 (6%) | C 6 (33%) | D 1 (6%) | E 0 (0%) | F 1 (6%) | G 0 (0%) | H 0 (0%) | I 2 (11%) | N 3 (17%).

**The 538 records that make the 263 edges**: A 67 (12%) | B 69 (13%) | C 210 (39%) | D 60 (11%) | E 46 (9%) | F 30 (6%) | G 5 (1%) | H 5 (1%) | I 19 (4%) | N 27 (5%).
Of these, the 470 `metals_ions` records that make the 207 `cofactor_of` edges: A 63 (13%) | B 68 (14%) | C 207 (44%) | D 60 (13%) | E 6 (1%) | F 29 (6%) | G 5 (1%) | H 5 (1%) | I 13 (3%) | N 14 (3%).

Inhibition sub-flags, all 96 E records: {'mM': 45, 'un': 41, 'cyt': 10}; of the 46 that make edges: {'mM': 28, 'un': 14, 'cyt': 4}.

Against the keyword pass of 5 November (12% sensing, 7% structural, 3% inhibiting, 66% bare, of 746): the reading gives, of the
751 `metals_ions` records, 14% sensing, 13% structural, 41% bare, 15% at a stated concentration above the cytosolic range, 8%
nonspecific divalent, 2% no effect, 2% inhibition in the `metals_ions` field itself. The 66% "bare" of the keyword pass splits
into 41% that are bare and 15% whose comment states a concentration that rules cytosolic regulation out, plus 8% that name Mg2+
or Mn2+ as equivalent.

Compartments of the 234 proteins with edges: {'ext': 62, 'cyt': 130, 'lum': 29, 'pump': 5, 'mito': 4, 'memb': 4}.

The 342 records that make no edge: classes {'C': 103, 'D': 50, 'E': 50, 'A': 41, 'F': 34, 'B': 28, 'N': 13, 'H': 11, 'G': 8, 'I': 4}; they include the CaMKII, PKC, PLC, calpain 2,
NOX5 and SERCA class-level records (route "ec_n" with n > 1 accessions), which are sensing records that the mapping cannot
assign to one protein, and are not lost evidence for a rule but are outside the 263 edges.

## 4. Per-protein table

The full table is `docs/brenda_calcium_proteins_2026-11-06.csv` (234 rows: accession, gene, compartment, UniProt location, number of records,
class mix overall and by BRENDA field, the v5 edges, and the outcome of each edge under rules R1, R2 and R3 of section 6).
Summaries:

**The 62 secreted and extracellular proteins** (70 edges; neither cytosolic node is right; `MAM01413e` is the compartment, at
1-2 mM free Ca2+, which is also where their millimolar optima sit): MASP2, ENPP3, ADAM10, ADAMTS3, KLK8, ENTPD6, F13A1, F2, C1R, F9, F10, F11, MMP1, PROC, CFI, MPO, HPN, BCHE, C2, ELANE, MMP2, MMP3, CTSG, F7, MMP7, C1S, GZMB, ACR, BMP1, PLA2G2A, MMP9, ANPEP, AOC1, ENPP1, MMP8, PRTN3, DNASE1, PON1, AOAH, MMP12, TGM4, KLK7, ENTPD1, MMP14, GPLD1, FOLH1, ENPEP, PAPPA, ENPP2, PON3, MEP1A, MEP1B, NOTUM, ADAMTS13, PCSK9, GGH, CPB2, CTRC, KLK15, ASAH2, ENTPD2, ST14.
Their records are quoted in section 5c. Two of them need a word: ADAM10's two comments name "cellular influx of Ca2+" as the
activator, so although its catalytic domain is extracellular the regulation stated is cytosolic and the rules below move it;
F13A1 is cytoplasmic in most tissues and secreted into plasma, and its Ca2+ requirement is that of plasma FXIIIa (class C), so
it is flagged `ext`.

**The 29 lumenal proteins and 4 of unstated face** (37 edges): TPP1, MAN1A2, PLOD3, GLCE, CTSD, STS, FURIN, ARSA, B4GALT1, ARSB, ABO, PCSK2, NAGA, PAM, MGAT1, PCSK1, PRCP, FUT7, ASPH, MBTPS1, PON2, ACER2, XYLT1, SUMF1, ACER1, CANT1, PTDSS2, FUT8, ENTPD7, MAN1C1, ACER3, MAN1B1, MGAT4A. The Golgi glycosyltransferases and
mannosidases, furin and the proprotein convertases, the lysosomal enzymes and ER-lumen enzymes. Lumenal free Ca2+ is neither the
cytosolic pool nor `MAM01413e`; the graph has store nodes from 9.75 for the ER, but no lumenal regulation target, so these are
proposed to stay inert where they are, with the limit recorded.

**The 4 mitochondrial proteins** (4 edges): MMUT, CRAT, OGDH, PPA2. OGDH's comment is a sensing one (K0.5 130 nM, two
Ca2+-binding sites on E1): matrix Ca2+ follows cytosolic Ca2+ through the uniporter, so OGDH is the one case where a cytosolic
pool edge would be a relay rather than a wrong compartment. Left as a sub-question rather than moved.

**The 5 pumps** (5 `cofactor_of` edges): ATP2C2, ATP2B1, ATP2C1, ATP2B2, ATP2B3. Class H: "at very low Ca2+ concentrations the PMCA is
nearly inactive". Moved as `activates` under every rule, which forms the three PMCA feedback loops the row names.

**The 20 proteins with no UniProt location text locally** (assigned from function, `noCC` in the CSV): EEF2K, NADK, ACR, PEPD, FAH, DCTD, TGM4, NUDT2, GALK1, PDE1A, PPAT, TPH2, TTL, NANP, CTRC, SRR, TPK1, NANS, RNF181, GMPR2.

## 5. Quotes

Every record in class A, class E, and on a protein flagged `ext`, as the task asked (the CSV holds the comment of every record).
Format: [record id] gene accession, EC, BRENDA field, whether it makes an edge, compartment, class, reference count: "comment".

### 5a. Class A, sensing mechanism or physiological range (108 records, 67 of them making an edge)

- [245] EEF2K O00418, EC 2.7.11.20, metals_ions, edge, cyt, class A, refs 1: "strong activation, activation in response to exercise in skeletal muscle"
- [246] EEF2K O00418, EC 2.7.11.20, metals_ions, edge, cyt, class A, refs 2: "Ca2+/calmodulin-dependent enzyme"
- [247] EEF2K O00418, EC 2.7.11.20, metals_ions, edge, cyt, class A, refs 1: "Ca2+/calmodulin stimulates the autophosphorylation of elongation factor 2 kinase on Thr348 and Ser500 to regulate its activity and calcium dependence. Half-maximal activity at 140 nM Ca2+. Maximal activity 0.003 mM Ca2+"
- [248] EEF2K O00418, EC 2.7.11.20, metals_ions, edge, cyt, class A, refs 1: "Ca2+/calmodulin-dependent enzyme. Ca2+/calmodulin enhance the ability of the enzyme to bind to ATP"
- [249] EEF2K O00418, EC 2.7.11.20, metals_ions, edge, cyt, class A, refs 2: "a Ca2+/calmodulin-dependent protein kinase"
- [250] EEF2K O00418, EC 2.7.11.20, metals_ions, edge, cyt, class A, refs 1: "required for maintaining the interaction with activator calmodulin"
- [251] EEF2K O00418, EC 2.7.11.20, metals_ions, edge, cyt, class A, refs 1: "Ca2+ enhances the affinity of calmodulin toward the enzyme, 0.15 mM Ca2+ is used in assay conditions"
- [709] ADAM10 O14672, EC 3.4.24.81, metals_ions, edge, ext, class A, refs 1: "ADAM10-mediated proteolysis of VE-cadherin is induced by Ca2+ influx"
- [710] ADAM10 O14672, EC 3.4.24.81, metals_ions, edge, ext, class A, refs 1: "activation of the enzyme can be achieved by cellular influx of Ca2+"
- [878] PLSCR1 O15162, EC 7.6.2.1, metals_ions, edge, cyt, class A, refs 1: "activates, dependent on for redistibution of plasma membrane phospholipids, the enzyme contains a EF-hand-like Ca2+ binding motif, overview. A 1000fold increase in cytosolic Ca2+ level in response to cell activation, coagulation and apoptotic signal inactivates the ATP transporters and activates the"
- [13] ALOX15B O15296, EC 1.13.11.33, metals_ions, edge, cyt, class A, refs 1: "Ca2+ binds to the PLAT domain of 15-LOX-2, resulting in a translocation from the cytosol to the membrane"
- [183] NADK O95544, EC 2.7.1.23, metals_ions, edge, cyt, class A, refs 1: "half-maximal activity at free calcium of approximately 0.0004 mM"
- [196] EGFR P00533, EC 2.7.10.1, metals_ions, edge, cyt, class A, refs 1: "ligand-binding induced dimerization enables transautophosphorylation of ErbB1 which results in enhanced intracellular cytoplasmic Ca2+ concentration activating calmodulin which reverses autoinhibition by net charge changes in the juxtamembranes"
- [330] BCHE P06276, EC 3.1.1.8, metals_ions, edge, ext, class A, refs 1: "activates 9fold at 0.5 mM with substrate O-ethyl-O-(4-nitrophenyl)-phenylphosphonothioate via a specific EF-hand calcium binding site, molecular modelling of Ca2+ binding to EF-hands, disruption by H2O2-mediated oxidation"
- [628] CAPN1 P07384, EC 3.4.22.52, metals_ions, edge, cyt, class A, refs 1: "maximal activation at about 0.002 mM"
- [629] CAPN1 P07384, EC 3.4.22.52, metals_ions, edge, cyt, class A, refs 1: "sensitive to the frequency of fast Ca2+ oscillations in vitro"
- [631] CAPN1 P07384, EC 3.4.22.52, metals_ions, edge, cyt, class A, refs 1: "dependent on (0.002-0.02 mM). At resting [Ca2+], mu-calpain is present predominantly in its full-length, unautolysed/unactivated forms. Once activated, mu-calpain appears in its autolysed form. Endogenously expressed mu-calpain is activated within a physiological [Ca2+] range in a Ca2+- and time-dep"
- [632] CAPN1 P07384, EC 3.4.22.52, metals_ions, edge, cyt, class A, refs 1: "dependent on, dysfunctional mitochondria increase cytosolic calcium, thereby inducing calpain activation"
- [633] CAPN1 P07384, EC 3.4.22.52, metals_ions, edge, cyt, class A, refs 1: "mu-calpain is autolytically activated at micromolar Ca2+, mice muscle fibers that are partially excitation-contraction uncoupled by exposure to 0.005 mM Ca2+ for 3 min (no ATP) show the presence of autolytic activation of a proportion of the human mu-calpain present"
- [634] CAPN1 P07384, EC 3.4.22.52, metals_ions, edge, cyt, class A, refs 1: "requires a micromolar concentration of calcium ions"
- [635] CAPN1 P07384, EC 3.4.22.52, metals_ions, edge, cyt, class A, refs 1: "the enzyme requires micromolar calcium concentrations for activation"
- [22] ALOX5 P09917, EC 1.13.11.34, metals_ions, edge, cyt, class A, refs 1: "the enzyme is activated by a Ca2+-mediated translocation to membranes"
- [23] ALOX5 P09917, EC 1.13.11.34, metals_ions, edge, cyt, class A, refs 1: "activates, Ca2+ induces the translocation of 5-LO from a soluble compartment to nuclear structures, where 5-LO co-localizes with 5-LO activating protein, FLAP"
- [24] ALOX5 P09917, EC 1.13.11.34, metals_ions, edge, cyt, class A, refs 1: "binds at the C2-like domain, stimulates and induces enzyme translocation from the nuclear soluble to the envelope fraction, both Ca2+ and glyceride might decrease the concentration of lipid hydroperoxide needed for activation of 5-LO, enabling cellular 5-LO product formation at a low redox tone"
- [25] ALOX5 P09917, EC 1.13.11.34, metals_ions, edge, cyt, class A, refs 1: "stimulation with calcium ionophore"
- [26] ALOX5 P09917, EC 1.13.11.34, metals_ions, edge, cyt, class A, refs 1: "upon stimulation with calcium ionophore, GFP-5-lipoxygenase translocates to the nuclear envelope allowing it to interact with 5-lipoxygenase activating protein (FLAP) and leukotriene C4 synthase"
- [27] ALOX5 P09917, EC 1.13.11.34, metals_ions, edge, cyt, class A, refs 1: "Ca2+ is required for 5LO activity, the enzyme contains two Ca2+, full activation is reached at 0.004-0.01 mM Ca2+"
- [29] ALOX5 P09917, EC 1.13.11.34, metals_ions, edge, cyt, class A, refs 1: "5-LOX is recruited to the nuclear membrane upon cellular Ca2+ influx. Calcium binds to allosteric sites in the 5-LOX N-terminal polycystin-1/lipoxygenase/alpha-toxin (PLAT) domain, promoting attachment to the membrane via conserved tryptophan residues that embed into the lipid bilayer"
- [30] ALOX5 P09917, EC 1.13.11.34, metals_ions, edge, cyt, class A, refs 1: "allosteric modulator involved in membrane binding by the enzyme"
- [400] PLCG2 P16885, EC 3.1.4.11, metals_ions, edge, cyt, class A, refs 1: "PLCgamma2, Ca2+-dependent, highest activity at 0.005-0.01 mM"
- [653] CAPN3 P20807, EC 3.4.22.54, metals_ions, edge, cyt, class A, refs 1: "regulated by Ca2+, contains 2 EF-hand calcium-binding domains. Activated by micromolar concentrations of calcium"
- [102] TGM2 P21980, EC 2.3.2.13, metals_ions, edge, cyt, class A, refs 1: "the enzyme is allosterically regulated by Ca2+ ions and nucleotides (GMP, GDP, GTP, GTPgammaS), which trigger opposing conformational changes. Nucleotides push transglutaminase 2 into its compact, closed state, while Ca2+ triggers an extended form"
- [96] TGM2 P21980, EC 2.3.2.13, metals_ions, edge, cyt, class A, refs 1: "dependent on, the protein transamidase activity of TG2 is positively regulated by calcium and negatively regulated by GTP. The wild-type and mutant enzymes both contain six Ca2+ binding sites"
- [98] TGM2 P21980, EC 2.3.2.13, metals_ions, edge, cyt, class A, refs 1: "required, three calcium binding sites are thought to exist on tTG, GTP/GDP and Ca2+ are able to compete with one another to convert tTG from the closed- to open-state, and vice versa"
- [161] ITPKA P23677, EC 2.7.1.127, metals_ions, edge, cyt, class A, refs 2: "the enzyme is activated by Ca2+/calmodulin"
- [147] DGKA P23743, EC 2.7.1.107, metals_ions, edge, cyt, class A, refs 1: "0.001 mM used in assay conditions. The enzyme is positively regulated by Ca2+"
- [148] DGKA P23743, EC 2.7.1.107, metals_ions, edge, cyt, class A, refs 1: "the enzyme is positively regulated by Ca2+ binding to its N-terminal EF-hand domains. Cooperative binding of two Ca2+ ions dissociates the dimer into a well-folded monomer, which resists to proteolysis"
- [163] ITPKB P27987, EC 2.7.1.127, metals_ions, edge, cyt, class A, refs 3: "the enzyme is highly activated by Ca2+/calmodulin"
- [40] NOS1 P29475, EC 1.14.13.39, metals_ions, edge, cyt, class A, refs 1: "the raise of intracellular calcium levels increases nNOS dephosphorylation and enzymatic activity"
- [809] CTH P32929, EC 4.4.1.1, metals_ions, edge, cyt, class A, refs 1: "Ca2+ promotes activation of CSE, H2S production by CSE is a Ca2+-dependent phenomenon"
- [487] PRCP P42785, EC 3.4.16.2, metals_ions, edge, lum, class A, refs 1: "optimal activity at 0.01 mM"
- [238] PHKA2 P46019, EC 2.7.11.19, metals_ions, edge, cyt, class A, refs 1: "required, interacts with the delta subunit"
- [382] PDE1A P54750, EC 3.1.4.1, activating_compound, edge, cyt, class A, refs 1: "stimulated by their binding to Ca2+/calmodulin"
- [408] PDE1B Q01064, EC 3.1.4.17, metals_ions, edge, cyt, class A, refs 4: "Ca2+/calmodulin stimulated"
- [49] OGDH Q02218, EC 1.2.1.105, metals_ions, edge, mito, class A, refs 1: "K0.5 value in absence of NADH is 0.00013 mM, in presence of NADH is 0.00781 mM. Component E1 has two potential Ca2+ -binding sites, site 1 (D114ADLD) and site 2 (E139SDLD). A mutated form of E1, D114A, shows a 6-fold decrease in sensitivity for Ca2+ ,whereas variantx02site1 (sequence of site 1 is re"
- [831] GUCY2D Q02846, EC 4.6.1.2, metals_ions, edge, cyt, class A, refs 1: "the activity of wild-type GC-E shows a strong dependency on free Ca2+ and GCAP1, but it is less sensitive to GCAP2"
- [357] PPP3CA Q08209, EC 3.1.3.16, metals_ions, edge, cyt, class A, refs 1: "calcineurin is a calcium- and calmodulin-dependent enzyme"
- [218] CAMK2B Q13554, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 42: "Ca2+/calmodulin-dependent"
- [219] CAMK2D Q13557, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 42: "Ca2+/calmodulin-dependent"
- [217] CAMK1 Q14012, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 1: "the enzyme responds directly to Ca2+-calmodulin with increased activity"
- [220] CAMK1 Q14012, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 42: "Ca2+/calmodulin-dependent"
- [383] PDE1C Q14123, EC 3.1.4.1, activating_compound, edge, cyt, class A, refs 1: "stimulated by their binding to Ca2+/calmodulin"
- [412] PDE1C Q14123, EC 3.1.4.17, metals_ions, edge, cyt, class A, refs 1: "the catalytic activity of PDE1 is stimulated by their binding to Ca2+/calmodulin"
- [197] PTK2B Q14289, EC 2.7.10.2, activating_compound, edge, cyt, class A, refs 1: "G-protein coupled receptor PAC1 regulates the tyrosine phosphorylation of isoform PYK2 in NCI-H838 nonsmall cell lung cancer cells. PYK2 phosphorylation is dependent upon Ca2+. The ability of PAC1 to regulate PYK2 is dependent on phospholipase and Src, and partially dependent on proteinkinase C"
- [618] ESPL1 Q14674, EC 3.4.22.49, metals_ions, edge, cyt, class A, refs 1: "Ca2+-levels affect separase function, C-terminal region contains a Ca2+-binding motif"
- [221] CAMK4 Q16566, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 42: "Ca2+/calmodulin-dependent"
- [227] CAMK4 Q16566, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 1: "calcium-calmodulin dependent signalling via Ca2+ leads to activation of CAMKIV autoinhibition"
- [228] CAMK4 Q16566, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 2: "calcium/calmodulin-dependent enzyme"
- [104] UBE3B Q7Z3V4, EC 2.3.2.26, activating_compound, edge, cyt, class A, refs 1: "when the concentration of calcium is increased, calmodulin is released from UBE3B, resulting in an increase in ubiquitylation activity"
- [849] TTL Q8NG68, EC 6.3.2.25, metals_ions, edge, cyt, class A, refs 1: "required for the N-formyl-Met-Leu-Phe-induced and the antibiotic A23187-induced stimulation"
- [172] CERK Q8TCT0, EC 2.7.1.138, metals_ions, edge, cyt, class A, refs 1: "stimulation above 0.0001 mM, maximal activation at 0.5 mM"
- [162] ITPKC Q96DU7, EC 2.7.1.127, metals_ions, edge, cyt, class A, refs 2: "the enzyme is activated by Ca2+/calmodulin"
- [352] PPP3R2 Q96LZ3, EC 3.1.3.16, metals_ions, edge, cyt, class A, refs 1: "the regulatory subunit is an EF-hand Ca2+-binding protein"
- [224] CAMK1G Q96NX5, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 1: "dependent on, activates, the Ca2+/calmodulin-binding domain overlaps with the autoinhibition domain"
- [229] CAMKK2 Q96RR4, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 2: "calcium/calmodulin-dependent enzyme"
- [105] RNF181 Q9P0P0, EC 2.3.2.27, metals_ions, edge, cyt, class A, refs 1: "ubiquitination in the platelet is modulated by elevated intracellular calcium level"
- [222] CAMK2A Q9UQM7, EC 2.7.11.17, metals_ions, edge, cyt, class A, refs 42: "Ca2+/calmodulin-dependent"
- [12] EC 1.13.11.33 (unresolved, route ec_3), EC 1.13.11.33, metals_ions, no edge, -, class A, refs 1: "in the presence of Ca2+, with or without calcium ionophore, the majority of 15-LO-1 is found in the membrane fraction, although significant amounts are also detected in the supernatant fraction"
- [152] EC 2.7.1.127 (unresolved, route ec_3), EC 2.7.1.127, metals_ions, no edge, -, class A, refs 1: "phosphorylation of Thr-311 of isoenzyme A by CaM kinase II results in a 25fold increase in sensitivity to the Ca2+/calmodulin complex"
- [153] EC 2.7.1.127 (unresolved, route ec_3), EC 2.7.1.127, metals_ions, no edge, -, class A, refs 1: "the 3 isoenzymes A, B and C can be distinguished by their sensitivity to Ca2+/calmodulin"
- [155] EC 2.7.1.127 (unresolved, route ec_3), EC 2.7.1.127, metals_ions, no edge, -, class A, refs 4: "at physiological concentrations"
- [156] EC 2.7.1.127 (unresolved, route ec_3), EC 2.7.1.127, metals_ions, no edge, -, class A, refs 26: "activation by Ca2+/calmodulin"
- [157] EC 2.7.1.127 (unresolved, route ec_3), EC 2.7.1.127, metals_ions, no edge, -, class A, refs 1: "17fold stimulation by Ca2+/calmodulin at saturating calmodulin and 0.01 mM free Ca2+"
- [159] EC 2.7.1.127 (unresolved, route ec_3), EC 2.7.1.127, metals_ions, no edge, -, class A, refs 1: "activation by calmodulin in a Ca2+-dependent manner"
- [160] EC 2.7.1.127 (unresolved, route ec_3), EC 2.7.1.127, metals_ions, no edge, -, class A, refs 1: "regulatory function in concert with calmodulin"
- [171] EC 2.7.1.138 (unresolved, route ec_2), EC 2.7.1.138, metals_ions, no edge, -, class A, refs 1: "required for activity, 60 nM - 3 mM, 20fold linear increase in activity, progressive loss of activity at higher concentrations"
- [204] EC 2.7.11.13 (unresolved, route ec_15), EC 2.7.11.13, metals_ions, no edge, -, class A, refs 1: "binds to C2 domain of PKC, regulatory fucntion for isozymes alpha, betaI, betaII, and gamma, overview"
- [206] EC 2.7.11.13 (unresolved, route ec_15), EC 2.7.11.13, metals_ions, no edge, -, class A, refs 1: "required, second messenger involved in PKC regulation, some isozymes are Ca2+-independent"
- [223] EC 2.7.11.17 (unresolved, route ec_11), EC 2.7.11.17, metals_ions, no edge, -, class A, refs 1: "dependent on, activates the nonphosphorylated CaMKIV, the autoinhibitory domain harbors the binding site for Ca2+ and calmodulin"
- [225] EC 2.7.11.17 (unresolved, route ec_11), EC 2.7.11.17, metals_ions, no edge, -, class A, refs 1: "dependent on, Ca2+/calmodulin activate CaMKII prior to autophosphorylation which renders the enzyme independent of Ca2+/calmodulin"
- [237] EC 2.7.11.19 (unresolved, route ec_2), EC 2.7.11.19, metals_ions, no edge, -, class A, refs 1: "Ca2+-sensitivity of the enzyme is mediated by the delta-subunit which is identical with calmodulin"
- [253] EC 2.7.11.31 (unresolved, route ec_2), EC 2.7.11.31, metals_ions, no edge, -, class A, refs 1: "increases in intracellular Ca2+ levels activate AMPK is via the activation of CaMKKs, mechanism, overview"
- [319] EC 3.1.1.4 (unresolved, route ec_29), EC 3.1.1.4, metals_ions, no edge, -, class A, refs 1: "Ca2+-dependent PLA2-association with cellular membranes at a concentration of 300-500 nM"
- [321] EC 3.1.1.4 (unresolved, route ec_29), EC 3.1.1.4, metals_ions, no edge, -, class A, refs 1: "calcium, phosphorylation at Ser505 and the putative phosphatidylinositol 4,5-bisphosphate binding site regulate translocation and arachidonic acid release, overview. Influx of extracellular calcium is essential for stable binding of cPLA2alpha to Golgi and arachidonic acid release. phosphatidylinosi"
- [354] EC 3.1.3.16 (unresolved, route ec_83), EC 3.1.3.16, metals_ions, no edge, -, class A, refs 4: "calcineurin is dependent on Ca2+/calmodulin"
- [361] EC 3.1.3.17 (unresolved, route ec_0), EC 3.1.3.17, metals_ions, no edge, -, class A, refs 1: "oscillation of cytosolic Ca2+, has an important regulatory function in the phosphorylation-dephosphorylation cycle for regulation of glycogen phosphorylase activity, overview"
- [388] EC 3.1.4.1 (unresolved, route ec_3), EC 3.1.4.1, metals_ions, no edge, -, class A, refs 1: "0.2 mM activity in MAA cells stimulated ca. 2fold, with calmodulin"
- [39] EC 1.14.13.39 (unresolved, route ec_3), EC 1.14.13.39, metals_ions, no edge, -, class A, refs 1: "Ca2+/calmodulin is required for citrulline/NO formation and for superoxide formation in absence of tetrahydropterin"
- [398] EC 3.1.4.11 (unresolved, route ec_13), EC 3.1.4.11, metals_ions, no edge, -, class A, refs 1: "required, maximal hydrolysis of phosphatidylinositol 4,5-diphosphate at 0.004 mM, maximal hydrolysis of phosphatidylinositol at 0.5 mM"
- [402] EC 3.1.4.11 (unresolved, route ec_13), EC 3.1.4.11, metals_ions, no edge, -, class A, refs 1: "Ca2+ flowing activates phospholipase C leading to the depletion of phosphatidylinositol 4,5-bisphosphate and formation of inositol 1,4,5-trisphosphate in TRPV6-expressing cells"
- [404] EC 3.1.4.11 (unresolved, route ec_13), EC 3.1.4.11, metals_ions, no edge, -, class A, refs 1: "all PLC isozymes require calcium for their activity, the PLCdelta-type is one of the most sensitive to calcium, suggesting that the activity of the PLCdelta-type may be regulated by calcium. PLCzeta is extremely sensitive to the calcium concentration"
- [409] EC 3.1.4.17 (unresolved, route ec_8), EC 3.1.4.17, metals_ions, no edge, -, class A, refs 1: "isoform PDE1B2 activity can be regulated by changes in Ca2+ levels"
- [414] EC 3.1.4.3 (unresolved, route ec_4), EC 3.1.4.3, metals_ions, no edge, -, class A, refs 1: "recombinant PLC d3: maximum activity with 0.001 mM, recombinant PLC d1: maximum activity with 0.01 mM"
- [422] EC 3.1.4.4 (unresolved, route ec_3), EC 3.1.4.4, metals_ions, no edge, -, class A, refs 3: "micromolar levels for maximal activity"
- [472] EC 3.4.11.18 (unresolved, route ec_4), EC 3.4.11.18, metals_ions, no edge, -, class A, refs 1: "0.0001-0.001 mM, activity is enhanced 5-10fold"
- [48] EC 1.2.1.105 (unresolved, route ec_0), EC 1.2.1.105, metals_ions, no edge, -, class A, refs 1: "0.01 mM, decreases the concentration of 2-oxoglutarate required for half-maximal activity, inhibition at higher concentrations"
- [57] EC 1.6.3.1 (unresolved, route ec_5), EC 1.6.3.1, metals_ions, no edge, -, class A, refs 1: "Ca2+-induced conformation change of NADPH oxidase 5 N-terminus leads to enzyme activation through an intramolecular interaction"
- [58] EC 1.6.3.1 (unresolved, route ec_5), EC 1.6.3.1, metals_ions, no edge, -, class A, refs 1: "generation of H2O2 by transfected isoform Duox2 depends on Ca2+"
- [59] EC 1.6.3.1 (unresolved, route ec_5), EC 1.6.3.1, metals_ions, no edge, -, class A, refs 1: "store-operated Ca2+ entry is required at the beginning of NADPH oxidase activation in response to N-formyl-L-methionyl-L-leucyl-Lphenylalanine in neutrophil-like HL-60 cells. When extracellular Ca2+ is initially removed, early addition of Ca2+ after stimulation causes a complete restoration of Ca2+ "
- [60] EC 1.6.3.1 (unresolved, route ec_5), EC 1.6.3.1, metals_ions, no edge, -, class A, refs 1: "an increase in cytosolic calcium concentration triggers high superoxide production by Nox5. Calcium induces binding of the N-terminal domain of Nox5 to the dehydrogenase domain, thus relieving autoinhibition. Two mechanisms may increase Nox5 sensitivity, allowing activation by resting calcium concen"
- [61] EC 1.6.3.1 (unresolved, route ec_5), EC 1.6.3.1, metals_ions, no edge, -, class A, refs 1: "the activity of NOX5 appears to be regulated by a self-contained Ca2+ binding domain, residues 1-169, the conformational change of the domain upon Ca2+ binding is essential for domain-domain interaction and superoxide production. Ca2+ binding to Ca2+ binding domain induces a conformational change th"
- [72] EC 2.3.1.67 (unresolved, route ec_2), EC 2.3.1.67, metals_ions, no edge, -, class A, refs 1: "optimal activity at 0.0002 mM"
- [729] EC 3.5.1.23 (unresolved, route ec_6), EC 3.5.1.23, metals_ions, no edge, -, class A, refs 1: "activates, required by ACER2 for both its in vitro and cellular activities. Cellular ACER2 activity is inhibited by depletion of Ca2+ from Golgi lumen"
- [772] EC 3.5.4.6 (unresolved, route ec_3), EC 3.5.4.6, metals_ions, no edge, -, class A, refs 1: "activates erythrocyte AMP deaminase [isoform E (AMPD3)] through a protein-protein interaction between calmodulin and the N-terminal domain of the AMPD3 polypeptide"
- [822] EC 4.6.1.1 (unresolved, route ec_10), EC 4.6.1.1, metals_ions, no edge, -, class A, refs 1: "during artificial or agonist-induced Ca2+ oscillations, periodic changes in cAMP that depended upon Ca2+ stimulation of AC8 with subsequent PKA-mediated phosphodiesterase 4 activity"
- [828] EC 4.6.1.2 (unresolved, route ec_9), EC 4.6.1.2, metals_ions, no edge, -, class A, refs 1: "modulates the membrane guanylate cyclase transduction machinery by both inhibiting and stimulating it involving the guanylate cyclae, the guanylate cyclase activating protein type 1, S100B, and neurocalcin delta, mechanism, overview"
- [420] GDPD3 Q7L5L3, EC 3.1.4.39, metals_ions, no edge, -, class A, refs 1: "stimulated by micromolar concentrations of Ca2+"
- [34] P4HTM Q9NXG6, EC 1.14.11.29, metals_ions, no edge, -, class A, refs 1: "the crystal structure reveals an EF domain with two Ca2+-binding motifs inserted within the catalytic domain. The proximity of the EF domain to the active site suggests that Ca2+ binding is relevant to the catalytic activity. Functional analysis demonstrates that Ca2+-binding affinity of P4H-TM is w"

### 5b. Class E, inhibition (96 records, 46 making an edge)

- [484] TPP1 O14773, EC 3.4.14.9, inhibitor, edge, lum, class E [mM], refs 1: "activating up to 0.1, inhibitory above"
- [811] ADCY6 O43306, EC 4.6.1.1, inhibitor, edge, cyt, class E [cyt], refs 1: "at low concentrations"
- [812] ADCY6 O43306, EC 4.6.1.1, inhibitor, edge, cyt, class E [cyt], refs 1: "inhibition by low concentrations"
- [560] F2 P00734, EC 3.4.21.5, inhibitor, edge, ext, class E [mM], refs 1: "slight inhibition at 10 mM"
- [523] F9 P00740, EC 3.4.21.22, inhibitor, edge, ext, class E [mM], refs 1: "5 mM"
- [567] F10 P00742, EC 3.4.21.6, inhibitor, edge, ext, class E [mM], refs 1: "the strength of the dimer interaction is strongly Ca2+-concentration-dependent, such that significant dimer forms in solution only at or above 5 mM Ca2+"
- [580] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class E [mM], refs 1: "the enzyme is sharply regulated by a Ca2+ switch centered at 1.16 mM, below which factor Xa is active and above which factor Xa forms inactive dimers on phosphatidylserine-exposing membranes"
- [469] EPHX1 P07099, EC 3.3.2.9, inhibitor, edge, cyt, class E [mM], refs 1: "20% inhibition at 1 mM"
- [470] EPHX1 P07099, EC 3.3.2.9, metals_ions, edge, cyt, class E [mM], refs 1: "20% inhibition at 1 mM"
- [547] ELANE P08246, EC 3.4.21.37, metals_ions, edge, ext, class E [un], refs 1: "inhibition of SP-D protein cleavage at physiological concentrations"
- [140] HMBS P08397, EC 2.5.1.61, inhibitor, edge, cyt, class E [mM], refs 1: "25 mM CaCl2, 90% inhibition"
- [141] HMBS P08397, EC 2.5.1.61, inhibitor, edge, cyt, class E [mM], refs 1: "0.1 mM CaCl2, 80% inhibition"
- [592] FURIN P09958, EC 3.4.21.75, inhibitor, edge, lum, class E [mM], refs 1: "5-10 mM inhibit"
- [593] FURIN P09958, EC 3.4.21.75, inhibitor, edge, lum, class E [un], refs 2: "activation below"
- [594] FURIN P09958, EC 3.4.21.75, inhibitor, edge, lum, class E [mM], refs 1: "100 mM"
- [599] FURIN P09958, EC 3.4.21.75, metals_ions, edge, lum, class E [mM], refs 1: "5-10 mM inhibit"
- [431] ARSA P15289, EC 3.1.6.8, inhibitor, edge, lum, class E [mM], refs 1: "at 30 mM"
- [432] ARSA P15289, EC 3.1.6.8, inhibitor, edge, lum, class E [mM], refs 1: "CaCl2 reduces the reaction rate in the low millimolar range"
- [842] MMUT P22033, EC 5.4.99.2, inhibitor, edge, mito, class E [un], refs 1: "at high concentrations"
- [335] DNASE1 P24855, EC 3.1.21.1, inhibitor, edge, ext, class E [mM], refs 1: "80% inhibition at 0.1 mM"
- [807] APEX1 P27695, EC 4.2.99.18, inhibitor, edge, cyt, class E [un], refs 1: "Ca2+ cause a complete loss of catalytic activity of APE1 with retention of binding potential"
- [198] CSK P41240, EC 2.7.10.4, inhibitor, edge, cyt, class E [mM], refs 1: "with Mg+, there is a steep fall in enzyme activity towards poly(Glu-Tyr) when the Ca2+ concentrations are in the millimolar range"
- [75] TGM4 P49221, EC 2.3.2.13, inhibitor, edge, ext, class E [mM], refs 1: "10 mM"
- [775] NUDT2 P50583, EC 3.6.1.17, inhibitor, edge, cyt, class E [mM], refs 1: "Ki: 0.3 mM"
- [50] BLVRA P53004, EC 1.3.1.24, inhibitor, edge, cyt, class E [un], refs 1: "abolishes autophosphorylation of BVR"
- [364] PSPH P78330, EC 3.1.3.3, inhibitor, edge, cyt, class E [un], refs 1: "inhibition even in presence of Mg2+, replacement of sixfold coordinated Mg2+ in active site by Ca2+ results in sevenfold coordinated metal ion, explaining the inhibitory effect of Ca2+"
- [806] NTHL1 P78549, EC 4.2.99.18, inhibitor, edge, cyt, class E [mM], refs 1: "50% inhibition at 5-10 mM"
- [826] GUCY1A1 Q02108, EC 4.6.1.2, inhibitor, edge, cyt, class E [cyt], refs 1: "Ca2+ inhibits SGC. Calcium treatment dramatically decreases Vmax and KM(GTP) for purified SGC or SGC expressed in different cell lines. Carbachol-, thrombospondin-1-, or angiotensin II-induced increase of cellular Ca2+ lowers SGC activity. Depolarization of pituitary cells by high K+ and L-type Ca2+"
- [827] GUCY1B1 Q02153, EC 4.6.1.2, inhibitor, edge, cyt, class E [cyt], refs 1: "Ca2+ inhibits SGC. Calcium treatment dramatically decreases Vmax and KM(GTP) for purified SGC or SGC expressed in different cell lines. Carbachol-, thrombospondin-1-, or angiotensin II-induced increase of cellular Ca2+ lowers SGC activity. Depolarization of pituitary cells by high K+ and L-type Ca2+"
- [474] ENPEP Q07075, EC 3.4.11.7, inhibitor, edge, ext, class E [un], refs 1: "inhibits activity with Gln-substrate, regulatory function and influence on substrate specificity"
- [475] ENPEP Q07075, EC 3.4.11.7, inhibitor, edge, ext, class E [un], refs 1: "substrate-specific inhibition, overview"
- [774] PPA1 Q15181, EC 3.6.1.1, inhibitor, edge, cyt, class E [mM], refs 1: "over 90% inhibition at 0.12 mM"
- [668] MEP1A Q16819, EC 3.4.24.18, inhibitor, edge, ext, class E [mM], refs 1: "above 1 mM, metalloproteinase, does not require additional Ca2+"
- [670] MEP1A Q16819, EC 3.4.24.18, metals_ions, edge, ext, class E [mM], refs 1: "Ca2+ inhibits above 1 mM"
- [695] MEP1B Q16820, EC 3.4.24.63, inhibitor, edge, ext, class E [un], refs 1: "calcium negatively regulates meprin beta activity and attenuates substrate cleavage"
- [696] MEP1B Q16820, EC 3.4.24.63, inhibitor, edge, ext, class E [un], refs 1: "inhibits, a negative regulator of meprin beta"
- [698] MEP1B Q16820, EC 3.4.24.63, metals_ions, edge, ext, class E [un], refs 1: "physiologic calcium concentrations display a dual role by (1) directly inhibiting meprin beta activity and (2) supporting meprin beta folding during biosynthesis"
- [711] ADAMTS13 Q76LX8, EC 3.4.24.87, inhibitor, edge, ext, class E [un], refs 1: "enzyme catalytic activity in blood plasma is tuned by varying buffer calcium, with lower divalent ion concentrations enhancing cleavage"
- [166] CERK Q8TCT0, EC 2.7.1.138, inhibitor, edge, cyt, class E [mM], refs 1: "above 1 mM"
- [167] CERK Q8TCT0, EC 2.7.1.138, inhibitor, edge, cyt, class E [mM], refs 1: "inhibition above 1 mM"
- [511] CTRC Q99895, EC 3.4.21.2, inhibitor, edge, ext, class E [mM], refs 1: "increasing the Ca2+ concentration from 0.025 mM to 1 mM progressively inhibits the degradation of cationic trypsin by chymotrypsin C, with essentially complete protection observed at 1 mM Ca2+"
- [777] THTPA Q9BU02, EC 3.6.1.28, inhibitor, edge, cyt, class E [un], refs 1: "inhibits by competition with Mg2+"
- [773] PPA2 Q9H2U2, EC 3.6.1.1, inhibitor, edge, mito, class E [mM], refs 1: "over 90% inhibition at 0.12 mM"
- [139] NANS Q9NR45, EC 2.5.1.57, inhibitor, edge, cyt, class E [mM], refs 1: "1 mM, 76% decrease of activity"
- [63] GMPR2 Q9P2T1, EC 1.7.1.7, inhibitor, edge, cyt, class E [mM], refs 1: "1 mM, 49% inhibition"
- [345] NOCT Q9UK39, EC 3.1.3.108, inhibitor, edge, cyt, class E [un], refs 1: "NOCT is inactive in the presence of Zn2+ and Ca2+ presumably due imperfect transition state formed due to a slight size mismatch of these ions"
- [113] EC 2.4.1.155 (unresolved, route ec_2), EC 2.4.1.155, inhibitor, no edge, -, class E [un], refs 1: "20% of maximal activity"
- [114] EC 2.4.1.155 (unresolved, route ec_2), EC 2.4.1.155, inhibitor, no edge, -, class E [un], refs 1: "35% of maximal activity"
- [151] EC 2.7.1.127 (unresolved, route ec_3), EC 2.7.1.127, inhibitor, no edge, -, class E [un], refs 1: "at higher concentrations"
- [189] EC 2.7.1.67 (unresolved, route ec_4), EC 2.7.1.67, inhibitor, no edge, -, class E [un], refs 2: "inhibits in the presence of Mg2+"
- [190] EC 2.7.1.67 (unresolved, route ec_4), EC 2.7.1.67, inhibitor, no edge, -, class E [un], refs 1: "inhibition depends in Ca2+ concentration"
- [254] EC 2.7.2.3 (unresolved, route ec_2), EC 2.7.2.3, inhibitor, no edge, -, class E [mM], refs 1: "inhibition above 1 mM"
- [255] EC 2.7.2.3 (unresolved, route ec_2), EC 2.7.2.3, inhibitor, no edge, -, class E [un], refs 1: "partial inhibition in presence of Mg2+"
- [266] EC 2.7.7.7 (unresolved, route ec_15), EC 2.7.7.7, inhibitor, no edge, -, class E [un], refs 1: "polymerase alpha"
- [270] EC 2.7.8.2 (unresolved, route ec_2), EC 2.7.8.2, inhibitor, no edge, -, class E [mM], refs 1: "0.1 mM (14.1% activity left) or 1 mM (1.41% activity left), estimated in presence of 20 mM Mg2+, inhibition partially reduced in presence of 0.5 mM EDTA: 33.3% or 3.70% activity left for 0.1 mM or 1 mM Ca2+, respectively (100% activity: 20 mM Mg2+, 0.5 mM EDTA, no Ca2+)"
- [272] EC 2.8.2.20 (unresolved, route ec_2), EC 2.8.2.20, inhibitor, no edge, -, class E [un], refs 1: "inhibits both isozymes"
- [277] EC 3.1.1.13 (unresolved, route ec_5), EC 3.1.1.13, inhibitor, no edge, -, class E [mM], refs 1: "50% inhibition at 5 mM"
- [334] EC 3.1.13.4 (unresolved, route ec_8), EC 3.1.13.4, inhibitor, no edge, -, class E [mM], refs 1: "3 mM gradually decreases activity about 15fold"
- [341] EC 3.1.22.1 (unresolved, route ec_2), EC 3.1.22.1, inhibitor, no edge, -, class E [un], refs 1: "strong inhibition"
- [342] EC 3.1.26.4 (unresolved, route ec_12), EC 3.1.26.4, inhibitor, no edge, -, class E [un], refs 1: "calcium ions generally inactivate the enzyme and abolish catalysis"
- [344] EC 3.1.3.1 (unresolved, route ec_4), EC 3.1.3.1, inhibitor, no edge, -, class E [mM], refs 1: "10 mM, glycogen synthase phosphatase activity"
- [346] EC 3.1.3.11 (unresolved, route ec_2), EC 3.1.3.11, inhibitor, no edge, -, class E [un], refs 1: "Ca2+ affects conformation of the catalytic loop 52-72 of muscle FBPase and inhibits its activity by competing with activatory divalent cations, e.g. Mg2+ and Zn2+. Aldolase associates with FBPase in its active form, i.e. with loop 52-72 in the engaged conformation, while Ca2+ stabilizes the disengag"
- [366] EC 3.1.3.36 (unresolved, route ec_9), EC 3.1.3.36, inhibitor, no edge, -, class E [un], refs 1: "competitive with Mg2+ in presence of optimal concentrations of Mg2+"
- [377] EC 3.1.3.74 (unresolved, route ec_2), EC 3.1.3.74, inhibitor, no edge, -, class E [un], refs 1: "competitive inhibition versus Mg2+, noncompetitive versus substrate"
- [380] EC 3.1.30.1 (unresolved, route ec_0), EC 3.1.30.1, inhibitor, no edge, -, class E [mM], refs 1: "35.1% of maximal activity with 0.1 mM denaturated DNA, 74.7% with 0.5 mM polydeoxythymidylic acid as substrate, competitive inhibition"
- [389] EC 3.1.4.11 (unresolved, route ec_13), EC 3.1.4.11, inhibitor, no edge, -, class E [un], refs 1: "at high concentrations"
- [390] EC 3.1.4.11 (unresolved, route ec_13), EC 3.1.4.11, inhibitor, no edge, -, class E [mM], refs 1: "concentrations above 1 mM are inhibitory"
- [407] EC 3.1.4.12 (unresolved, route ec_5), EC 3.1.4.12, inhibitor, no edge, -, class E [un], refs 1: "slight"
- [44] EC 1.16.3.1 (unresolved, route ec_6), EC 1.16.3.1, inhibitor, no edge, -, class E [un], refs 1: "weak inhibitor"
- [46] EC 1.2.1.105 (unresolved, route ec_0), EC 1.2.1.105, inhibitor, no edge, -, class E [cyt], refs 1: "0.01 mM, decreases the concentration of 2-oxoglutarate required for half-maximal activity, inhibition at higher concentrations"
- [460] EC 3.2.1.18 (unresolved, route ec_4), EC 3.2.1.18, inhibitor, no edge, -, class E [mM], refs 1: "above 1 mM"
- [466] EC 3.3.2.10 (unresolved, route ec_2), EC 3.3.2.10, inhibitor, no edge, -, class E [mM], refs 1: "25% inhibition at 1 mM"
- [467] EC 3.3.2.10 (unresolved, route ec_2), EC 3.3.2.10, inhibitor, no edge, -, class E [un], refs 1: "inhibition of Mg2+-dependent acrtivity"
- [544] EC 3.4.21.35 (unresolved, route ec_2), EC 3.4.21.35, inhibitor, no edge, -, class E [un], refs 1: "linear competitive"
- [565] EC 3.4.21.59 (unresolved, route ec_3), EC 3.4.21.59, inhibitor, no edge, -, class E [mM], refs 1: "5 mM is needed to cause an irreversible 50% loss of activity after 60 min at room temperature"
- [62] EC 1.7.1.7 (unresolved, route ec_2), EC 1.7.1.7, inhibitor, no edge, -, class E [mM], refs 1: "10 mM, 54% inhibition"
- [64] EC 1.8.1.9 (unresolved, route ec_4), EC 1.8.1.9, inhibitor, no edge, -, class E [un], refs 1: "non-reversible by EDTA"
- [67] EC 1.8.4.2 (unresolved, route ec_2), EC 1.8.4.2, inhibitor, no edge, -, class E [un], refs 2: "slight"
- [71] EC 2.3.1.125 (unresolved, route ec_0), EC 2.3.1.125, inhibitor, no edge, -, class E [mM], refs 1: "6% inhibition at 2 mM"
- [734] EC 3.5.1.4 (unresolved, route ec_0), EC 3.5.1.4, inhibitor, no edge, -, class E [un], refs 1: "1-linear competitive inhibition of the amidase activity"
- [813] EC 4.6.1.1 (unresolved, route ec_10), EC 4.6.1.1, inhibitor, no edge, -, class E [cyt], refs 1: "AC5 and AC6 are inhibited by Ca2+ at both sub- and supra-micromolar concentration, Ca2+ inhibits the soluble adenylate cyclase core composed of the C1 domain of AC5 and the C2 domain of AC2, at micromolar concentration Ca2+ inhibition is non-exclusive with respect to diphosphate, but at 0.1 mM Ca2+ "
- [814] EC 4.6.1.1 (unresolved, route ec_10), EC 4.6.1.1, inhibitor, no edge, -, class E [un], refs 1: "isoforms AC5 and AC6 are inhibited by Ca2+"
- [824] EC 4.6.1.2 (unresolved, route ec_9), EC 4.6.1.2, inhibitor, no edge, -, class E [cyt], refs 1: "modulates the membrane guanylate cyclase transduction machinery by both inhibiting and stimulating it involving the guanylate cyclae, the guanylate cyclase activating protein type 1, S100B, and neurocalcin delta, mechanism, overview"
- [825] EC 4.6.1.2 (unresolved, route ec_9), EC 4.6.1.2, inhibitor, no edge, -, class E [cyt], refs 1: "the enzyme is inhibited by high intracellular Ca2+ concentration"
- [851] EC 6.5.1.1 (unresolved, route ec_3), EC 6.5.1.1, inhibitor, no edge, -, class E [un], refs 1: "CaCl2 inhibits Mg2+-catalyzed reaction"
- [872] EC 7.6.2.1 (unresolved, route ec_21), EC 7.6.2.1, inhibitor, no edge, -, class E [cyt], refs 1: "0.0002 mM, inhibits from the cytofacial surface"
- [208] EC 2.7.11.15 (unresolved, route ec_2), EC 2.7.11.15, metals_ions, no edge, -, class E [un], refs 1: "inhibits GRK2"
- [209] EC 2.7.11.16 (unresolved, route ec_5), EC 2.7.11.16, metals_ions, no edge, -, class E [un], refs 1: "inhibits GRK5"
- [369] EC 3.1.3.4 (unresolved, route ec_8), EC 3.1.3.4, metals_ions, no edge, -, class E [un], refs 1: "moderate inhibition of cytosolic and particulate activity"
- [468] EC 3.3.2.10 (unresolved, route ec_2), EC 3.3.2.10, metals_ions, no edge, -, class E [mM], refs 1: "25% inhibition at 1 mM"
- [199] PSKH1 P11801, EC 2.7.11.1, metals_ions, no edge, -, class E [cyt], refs 1: "autophosphorylation activity is repressed upon addition of Ca2+/calmodulin"
- [605] TMPRSS15 P98073, EC 3.4.21.9, inhibitor, no edge, -, class E [mM], refs 1: "50% inhibition at 10 mM"
- [606] TMPRSS15 P98073, EC 3.4.21.9, inhibitor, no edge, -, class E [un], refs 1: "slight inhibition of substrates with one or two Asp/Glu residues at P2-P3 positions"
- [803] AZIN2 Q96A70, EC 4.1.1.19, inhibitor, no edge, -, class E [mM], refs 1: "1 mM"
- [482] XPNPEP1 Q9NQW7, EC 3.4.11.9, inhibitor, no edge, -, class E [mM], refs 1: "83.1% inhibition at 1 mM"
- [493] PGPEP1 Q9NXJ5, EC 3.4.19.3, inhibitor, no edge, -, class E [mM], refs 1: "1 mM, 20% inhibition"

### 5c. Records on secreted or extracellular proteins (218 records making an edge)

- [497] MASP2 O00187, EC 3.4.21.104, metals_ions, edge, ext, class C, refs 1: "required"
- [498] MASP2 O00187, EC 3.4.21.104, metals_ions, edge, ext, class B, refs 1: "enables dimerization"
- [499] MASP2 O00187, EC 3.4.21.104, metals_ions, edge, ext, class B, refs 1: "required for dimerization"
- [500] MASP2 O00187, EC 3.4.21.104, metals_ions, edge, ext, class B, refs 1: "Ca2+-dependent dimerization, Ca2+ is bound to the distal end of the CUB1 module of MAp19 and of MASP-2"
- [501] MASP2 O00187, EC 3.4.21.104, metals_ions, edge, ext, class B, refs 1: "interaction of MASP-2 with mannan-binding lectin is Ca2+-dependent, the Ca2+-binding site is located in the CUB1 module, overview"
- [794] ENPP3 O14638, EC 3.6.1.9, metals_ions, edge, ext, class C, refs 2: "required"
- [709] ADAM10 O14672, EC 3.4.24.81, metals_ions, edge, ext, class A, refs 1: "ADAM10-mediated proteolysis of VE-cadherin is induced by Ca2+ influx"
- [710] ADAM10 O14672, EC 3.4.24.81, metals_ions, edge, ext, class A, refs 1: "activation of the enzyme can be achieved by cellular influx of Ca2+"
- [660] ADAMTS3 O15072, EC 3.4.24.14, metals_ions, edge, ext, class C, refs 2: "required"
- [509] KLK8 O60259, EC 3.4.21.118, metals_ions, edge, ext, class C, refs 1: "4fold stimulation"
- [510] KLK8 O60259, EC 3.4.21.118, metals_ions, edge, ext, class D, refs 1: "150.2% activity at 10 mM"
- [792] ENTPD6 O75354, EC 3.6.1.6, metals_ions, edge, ext, class F, refs 1: "activates, slightly more effective than Mg2+"
- [81] F13A1 P00488, EC 2.3.2.13, metals_ions, edge, ext, class C, refs 10: "required"
- [561] F2 P00734, EC 3.4.21.5, activating_compound, edge, ext, class I, refs 1: "analysis of temperature dependence of pseudo-first order rate constants for enzyme-catalyzed hydrolysis of prothrombin-derived substrates, in presence and absence of Ca2+"
- [560] F2 P00734, EC 3.4.21.5, inhibitor, edge, ext, class E [mM], refs 1: "slight inhibition at 10 mM"
- [562] F2 P00734, EC 3.4.21.5, metals_ions, edge, ext, class C, refs 3: "required"
- [563] F2 P00734, EC 3.4.21.5, metals_ions, edge, ext, class C, refs 1: "activates"
- [564] F2 P00734, EC 3.4.21.5, metals_ions, edge, ext, class C, refs 1: "required for thrombin activation by factor Xa"
- [550] C1R P00736, EC 3.4.21.41, inhibitor, edge, ext, class I, refs 1: "reaction with C1s"
- [551] C1R P00736, EC 3.4.21.41, metals_ions, edge, ext, class C, refs 2: "dependent on"
- [552] C1R P00736, EC 3.4.21.41, metals_ions, edge, ext, class B, refs 1: "the NH2-terminal alpha fragment of the enzyme contains one high affinity Ca2+ binding site"
- [553] C1R P00736, EC 3.4.21.41, metals_ions, edge, ext, class B, refs 1: "binding of four Ca2+ per enzyme dimer"
- [523] F9 P00740, EC 3.4.21.22, inhibitor, edge, ext, class E [mM], refs 1: "5 mM"
- [524] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class C, refs 3: "activates"
- [525] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class C, refs 3: "activates"
- [526] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class C, refs 1: "factor IX activation is the first calcium-dependent reaction in intrinsic system clotting"
- [527] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class D, refs 1: "4-8fold allosteric activation at 5 mM"
- [528] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class D, refs 1: "5 mM, optimal concentration for cleavage of factor X by factor IXa on phospholipid membranes"
- [529] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class B, refs 1: "for proper binding of factor IXa to phospholipid and factor VIIIa, all of the Ca2+-sites in factor IXa must be filled"
- [530] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class I, refs 1: "binding of a subpopulation of platelets to the enzyme is activated by the protease-activated receptor-1, PAR-1, requirring both release of calcium from internal stores and influx of extracellular calcium, overview"
- [531] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class C, refs 1: "hughly activating"
- [532] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class C, refs 1: "the reaction is performed by the intrinsic FX-activating complex consisting of FIXa and FVIIIa on a negatively charged phospholipid surface in presence of Ca2+"
- [533] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class D, refs 1: "inhibition of activation of aFIX to FIXa when lowering concentration from 1.0 to 0.5 mM"
- [534] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class B, refs 1: "factor IXa contains a high-affinity Ca2+-binding site"
- [535] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class D, refs 1: "Ca2+ enhances the activity of factor IXa (5 mM used in assay conditions)"
- [536] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class D, refs 1: "5 mM used in assay conditions"
- [537] F9 P00740, EC 3.4.21.22, metals_ions, edge, ext, class B, refs 1: "presence of Ca2+ reduces fluctuations of residues of the Ca2+-loop. Ca2+ and Na+ together reduces fluctuations in residues of the Ca2+- and Na+-loops (residues 70-80, 183-194 and 217-225)"
- [568] F10 P00742, EC 3.4.21.6, activating_compound, edge, ext, class C, refs 1: "required"
- [569] F10 P00742, EC 3.4.21.6, activating_compound, edge, ext, class B, refs 1: "binding to the enzyme stabilizes the binding of Na+, required for prothrombinase complex formation"
- [566] F10 P00742, EC 3.4.21.6, inhibitor, edge, ext, class I, refs 1: "presence of heparin enhances inhibition by protein inhibitor C up to 42fold in the presence of a physiological Ca2+ concentration. In the absence of Ca2+, no enhancement of inhibition is observed"
- [567] F10 P00742, EC 3.4.21.6, inhibitor, edge, ext, class E [mM], refs 1: "the strength of the dimer interaction is strongly Ca2+-concentration-dependent, such that significant dimer forms in solution only at or above 5 mM Ca2+"
- [570] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class C, refs 6: "required"
- [571] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class C, refs 1: "activates"
- [572] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class C, refs 1: "required for activity"
- [573] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class B, refs 1: "dependent on, required for coordination of the enzyme domains, residues Asp46, Gly47, Gln49, and Gly64 are involved in Ca2+ binding, modeling of the calcium-binding site within the serine protease domain"
- [574] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class C, refs 1: "required as part of thr prothrombinase enzyme complex"
- [575] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class B, refs 1: "required for binding of the EGF-like domains at the catalytic C-terminus and the N-terminus, the EGF-like domain are linked via Ca2+ to the Gla-domain of the enzyme, which itself does not need Ca2+ for binding of C6PS"
- [576] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class C, refs 1: "required, part of prothrombinase complex"
- [577] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class C, refs 1: "required, part of the prothrombinase complex"
- [578] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class B, refs 1: "Ca2+-dependent binding of factor Xa to e.g. phospholipids"
- [579] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class B, refs 1: "ion binding site structure, overview"
- [580] F10 P00742, EC 3.4.21.6, metals_ions, edge, ext, class E [mM], refs 1: "the enzyme is sharply regulated by a Ca2+ switch centered at 1.16 mM, below which factor Xa is active and above which factor Xa forms inactive dimers on phosphatidylserine-exposing membranes"
- [539] F11 P03951, EC 3.4.21.27, metals_ions, edge, ext, class C, refs 3: "substrate factor IX: Ca2+ activates"
- [540] F11 P03951, EC 3.4.21.27, metals_ions, edge, ext, class C, refs 1: "required for proteolytic activity"
- [541] F11 P03951, EC 3.4.21.27, metals_ions, edge, ext, class C, refs 1: "factor XIa activates factor IX upon the addition of Ca2+"
- [542] F11 P03951, EC 3.4.21.27, metals_ions, edge, ext, class D, refs 2: "5 mM used in assay conditions"
- [543] F11 P03951, EC 3.4.21.27, metals_ions, edge, ext, class N, refs 1: "(no comment)"
- [700] MMP1 P03956, EC 3.4.24.7, metals_ions, edge, ext, class C, refs 3: "required"
- [701] MMP1 P03956, EC 3.4.24.7, metals_ions, edge, ext, class C, refs 1: "activates"
- [702] MMP1 P03956, EC 3.4.24.7, metals_ions, edge, ext, class B, refs 1: "both collagen and globular protein substrates of collagenase may bind Ca2+ and Zn2+ in the active site"
- [703] MMP1 P03956, EC 3.4.24.7, metals_ions, edge, ext, class D, refs 1: "optimum concentration 5 mM"
- [582] PROC P04070, EC 3.4.21.69, metals_ions, edge, ext, class C, refs 5: "required"
- [583] PROC P04070, EC 3.4.21.69, metals_ions, edge, ext, class B, refs 1: "contains gamma-carboxyglutamic acid residues required for Ca2+-dependent membrane binding"
- [584] PROC P04070, EC 3.4.21.69, metals_ions, edge, ext, class C, refs 1: "required for optimal activity"
- [585] PROC P04070, EC 3.4.21.69, metals_ions, edge, ext, class C, refs 1: "required, calcium enhances the amidolytic activity of APC by 2fold, the Ca2+ and Na+ metal ion-binding sites are linked energetically"
- [586] PROC P04070, EC 3.4.21.69, metals_ions, edge, ext, class I, refs 1: "the activated enzyme induces cytsolic Ca2+ signals, mechanism"
- [587] PROC P04070, EC 3.4.21.69, metals_ions, edge, ext, class I, refs 1: "significantly increases recombinant activated protein C binding to the neutrophil surface"
- [588] PROC P04070, EC 3.4.21.69, metals_ions, edge, ext, class B, refs 1: "a group of four or five divalent cation binding sites in the Gla-domain show a high specificity for Ca2+. Ca2+ interactions are essential for the anticoagulant functions of APC and are influenced by mutations in different regions of the Gla-domain"
- [589] PROC P04070, EC 3.4.21.69, metals_ions, edge, ext, class C, refs 1: "the presence of Ca2+ is essential for Zn2+ to enhance protein C activation because Zn2+ alone fails to support protein C activation"
- [590] PROC P04070, EC 3.4.21.69, metals_ions, edge, ext, class I, refs 1: "decreases the binding affinity of APC and Tie2 at 1 mM and 1-12 h"
- [559] CFI P05156, EC 3.4.21.45, metals_ions, edge, ext, class B, refs 1: "two Ca2+ ions per molecule are present, each bound to one of the LDLRA domains. Crystallization data"
- [5] MPO P05164, EC 1.11.2.2, metals_ions, edge, ext, class N, refs 1: "(no comment)"
- [502] HPN P05981, EC 3.4.21.106, metals_ions, edge, ext, class D, refs 1: "optimal concentration: 5 mM"
- [330] BCHE P06276, EC 3.1.1.8, metals_ions, edge, ext, class A, refs 1: "activates 9fold at 0.5 mM with substrate O-ethyl-O-(4-nitrophenyl)-phenylphosphonothioate via a specific EF-hand calcium binding site, molecular modelling of Ca2+ binding to EF-hands, disruption by H2O2-mediated oxidation"
- [557] C2 P06681, EC 3.4.21.43, metals_ions, edge, ext, class C, refs 1: "dependent on"
- [558] C2 P06681, EC 3.4.21.43, metals_ions, edge, ext, class C, refs 1: "formation of the bimolecular complex C4b2a, i.e. C3 convertase"
- [546] ELANE P08246, EC 3.4.21.37, metals_ions, edge, ext, class C, refs 2: "required"
- [547] ELANE P08246, EC 3.4.21.37, metals_ions, edge, ext, class E [un], refs 1: "inhibition of SP-D protein cleavage at physiological concentrations"
- [679] MMP2 P08253, EC 3.4.24.24, metals_ions, edge, ext, class C, refs 5: "required"
- [680] MMP2 P08253, EC 3.4.24.24, metals_ions, edge, ext, class C, refs 1: "dependent on"
- [681] MMP2 P08253, EC 3.4.24.24, metals_ions, edge, ext, class C, refs 1: "required, gelatinase A synthetic 19000 MW catalytic domain"
- [682] MMP2 P08253, EC 3.4.24.24, metals_ions, edge, ext, class B, refs 1: "4-bladed beta-propeller protein in which the 4 blades are arranged around a channel-like opening in which Ca2+ and a Na+Cl- ion pair are bound"
- [683] MMP2 P08253, EC 3.4.24.24, metals_ions, edge, ext, class C, refs 2: "required for activity"
- [684] MMP2 P08253, EC 3.4.24.24, metals_ions, edge, ext, class C, refs 1: "active site requires calcium ions"
- [685] MMP2 P08253, EC 3.4.24.24, metals_ions, edge, ext, class B, refs 1: "hemopexin-like domain requires Ca2+ for fibronectin and heparin binding"
- [686] MMP2 P08253, EC 3.4.24.24, metals_ions, edge, ext, class B, refs 1: "Ca2+is essential for homodimerization of enzyme MMP-2, analysis, detailed overview"
- [687] MMP2 P08253, EC 3.4.24.24, metals_ions, edge, ext, class C, refs 1: "essential for gelatinase activity, no gelatinase activity at 1 mM Ca2+"
- [663] MMP3 P08254, EC 3.4.24.17, metals_ions, edge, ext, class D, refs 1: "removal of Ca2+ from the enzyme solution results in a complete loss of activity that can be fully restored by addition of 1 mM Ca2+"
- [664] MMP3 P08254, EC 3.4.24.17, metals_ions, edge, ext, class D, refs 1: "Ca2+ is required to maintain the active conformation of the enzyme, full activity is detected at 1 mM Ca2+, at pH 7.5 and is retained at even higher concentrations of Ca2+, at lower concentrations the enzyme is autolyzed"
- [665] MMP3 P08254, EC 3.4.24.17, metals_ions, edge, ext, class B, refs 1: "proenzyme contains 3 Ca2+"
- [666] MMP3 P08254, EC 3.4.24.17, metals_ions, edge, ext, class C, refs 1: "calcium-dependent"
- [667] MMP3 P08254, EC 3.4.24.17, metals_ions, edge, ext, class B, refs 1: "required, the catalytic domains contain Ca2+ ions"
- [512] CTSG P08311, EC 3.4.21.20, metals_ions, edge, ext, class I, refs 1: "enzyme triggers calcium mobilization"
- [513] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class C, refs 1: "required"
- [514] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class C, refs 1: "activates"
- [515] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class B, refs 1: "bound to the backbone-carbonyl groups of Asp72 and Glu75, and to the side-chain carboxylate groups of Glu70 and Glu80"
- [516] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class B, refs 1: "binding structure"
- [517] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class B, refs 1: "dependent on, eight Ca2+ are bound via the Gla domain and involved in enzyme binding to the membrane with different tasks, structure and coordination, mechanism of Ca2+-mediated binding, overview"
- [518] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class B, refs 1: "one FVIIa molecule binds 8 Ca2+ in the epidermal growth factor-like and the gamma-carboxyglutamic acid-rich domains"
- [519] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class B, refs 1: "Ca2+ ions constitute an important cofactor for FVIIa and bind to a total of nine sites, seven in the N-terminal gamma-carboxyglutamic acid (Gla) domain and one each in the first EGF-like and protease domains"
- [520] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class D, refs 1: "5 mM used in assay conditions"
- [521] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class B, refs 1: "the enzyme binds the phospholipid membrane in a Ca2+-dependent manner. Ca2+ ions are required for assembly and function of the tissue factor-enzyme complex"
- [522] F7 P08709, EC 3.4.21.21, metals_ions, edge, ext, class C, refs 1: "Ca2+ increased the hydrolytic activity of FVIIa towards substrate S-2288 by about 60fold in the absence of Na+ and by about 82fold in the presence of Na+. Ca2+ stabilizes the Ca2+-binding loop (the 70-loop) and Na+-binding loops but not the tissue factor-binding region. Na+ and Ca2+ together stabili"
- [676] MMP7 P09237, EC 3.4.24.23, metals_ions, edge, ext, class C, refs 4: "required"
- [677] MMP7 P09237, EC 3.4.24.23, metals_ions, edge, ext, class C, refs 4: "required"
- [678] MMP7 P09237, EC 3.4.24.23, metals_ions, edge, ext, class I, refs 1: "contains a zinc ion essential for enzyme activity as well as a second zinc ion necessary for enzyme stability"
- [554] C1S P09871, EC 3.4.21.42, metals_ions, edge, ext, class C, refs 2: "dependent on"
- [555] C1S P09871, EC 3.4.21.42, metals_ions, edge, ext, class B, refs 1: "the NH2-terminal alpha fragment of the enzyme contains one high affinity Ca2+ binding site"
- [556] C1S P09871, EC 3.4.21.42, metals_ions, edge, ext, class B, refs 1: "recombinant CUB1-EGF-CUB2 region of enzyme C1s , dependent on, required for substrate binding. The CUB1-EGF-CUB2 domains of C1s are arranged linearly with three Ca2+: one in each CUB domain and one within the EGF-like domain, near the CUB1-EGF junction"
- [604] GZMB P10144, EC 3.4.21.79, metals_ions, edge, ext, class N, refs 1: "(no comment)"
- [496] ACR P10323, EC 3.4.21.10, metals_ions, edge, ext, class C, refs 5: "activates"
- [674] BMP1 P13497, EC 3.4.24.19, metals_ions, edge, ext, class C, refs 1: "required for activity"
- [675] BMP1 P13497, EC 3.4.24.21, metals_ions, edge, ext, class C, refs 1: "activates, a positive regulator of BMP-1"
- [323] PLA2G2A P14555, EC 3.1.1.4, metals_ions, edge, ext, class C, refs 1: "the secretory isozyme is Ca2+-dependent"
- [689] MMP9 P14780, EC 3.4.24.35, metals_ions, edge, ext, class C, refs 4: "required"
- [690] MMP9 P14780, EC 3.4.24.35, metals_ions, edge, ext, class C, refs 4: "required"
- [691] MMP9 P14780, EC 3.4.24.35, metals_ions, edge, ext, class C, refs 2: "dependent on"
- [692] MMP9 P14780, EC 3.4.24.35, metals_ions, edge, ext, class C, refs 1: "calcium and zinc dependent metalloproteinase"
- [693] MMP9 P14780, EC 3.4.24.35, metals_ions, edge, ext, class C, refs 1: "required"
- [473] ANPEP P15144, EC 3.4.11.2, inhibitor, edge, ext, class N, refs 1: "(no comment)"
- [51] AOC1 P19801, EC 1.4.3.22, metals_ions, edge, ext, class B, refs 1: "tightly bound, proposed to occupy a second metal-binding site"
- [52] AOC1 P19801, EC 1.4.3.22, metals_ions, edge, ext, class B, refs 1: "enzmye contains 2 Ca2+-binding sites per subunit"
- [795] ENPP1 P22413, EC 3.6.1.9, metals_ions, edge, ext, class C, refs 2: "required"
- [688] MMP8 P22894, EC 3.4.24.34, metals_ions, edge, ext, class N, refs 3: "(no comment)"
- [603] PRTN3 P24158, EC 3.4.21.76, metals_ions, edge, ext, class C, refs 1: "required"
- [335] DNASE1 P24855, EC 3.1.21.1, inhibitor, edge, ext, class E [mM], refs 1: "80% inhibition at 0.1 mM"
- [336] DNASE1 P24855, EC 3.1.21.1, metals_ions, edge, ext, class F, refs 8: "activation synergistic with Mg2+"
- [337] DNASE1 P24855, EC 3.1.21.1, metals_ions, edge, ext, class B, refs 1: "stabilizing enzyme structure"
- [338] DNASE1 P24855, EC 3.1.21.1, metals_ions, edge, ext, class F, refs 1: "activates, DNase I is a Ca2+/Mg2+-dependent enzyme, synergism"
- [339] DNASE1 P24855, EC 3.1.21.1, metals_ions, edge, ext, class D, refs 1: "1 mM optimal concentration"
- [340] DNASE1 P24855, EC 3.1.21.1, metals_ions, edge, ext, class F, refs 1: "highest activity at 5 mM, but only 50% activtiy compared to Mg2+"
- [281] PON1 P27169, EC 3.1.1.2, metals_ions, edge, ext, class C, refs 5: "required"
- [283] PON1 P27169, EC 3.1.1.2, metals_ions, edge, ext, class C, refs 4: "dependent on"
- [284] PON1 P27169, EC 3.1.1.2, metals_ions, edge, ext, class C, refs 2: "required for activity"
- [285] PON1 P27169, EC 3.1.1.2, metals_ions, edge, ext, class B, refs 1: "Asp269 and Glu53 participate in the ligation of catalytic Ca2+"
- [287] PON1 P27169, EC 3.1.1.2, metals_ions, edge, ext, class B, refs 1: "contains Ca2+"
- [296] PON1 P27169, EC 3.1.1.2, metals_ions, edge, ext, class D, refs 1: "1.6 mM used in assay conditions"
- [297] PON1 P27169, EC 3.1.1.2, metals_ions, edge, ext, class B, refs 1: "dependent on. The enzyme possesses 2 Ca2+ ions"
- [299] PON1 P27169, EC 3.1.1.25, metals_ions, edge, ext, class C, refs 3: "dependent on"
- [301] PON1 P27169, EC 3.1.1.25, metals_ions, edge, ext, class C, refs 1: "required for activity"
- [303] PON1 P27169, EC 3.1.1.25, metals_ions, edge, ext, class B, refs 1: "Asp269 and Glu53 participate in the ligation of catalytic Ca2+"
- [311] PON1 P27169, EC 3.1.1.25, metals_ions, edge, ext, class B, refs 1: "dependent on. The enzyme possesses 2 Ca2+ ions"
- [332] PON1 P27169, EC 3.1.1.81, metals_ions, edge, ext, class C, refs 1: "required for catalysis"
- [436] PON1 P27169, EC 3.1.8.1, metals_ions, edge, ext, class C, refs 7: "required"
- [439] PON1 P27169, EC 3.1.8.1, metals_ions, edge, ext, class C, refs 10: "dependent on"
- [440] PON1 P27169, EC 3.1.8.1, metals_ions, edge, ext, class C, refs 1: "required for activity"
- [444] PON1 P27169, EC 3.1.8.1, metals_ions, edge, ext, class B, refs 1: "involved in catalysis, active site structure, overview"
- [445] PON1 P27169, EC 3.1.8.1, metals_ions, edge, ext, class B, refs 1: "Asp269 and Glu53 participate in the ligation of catalytic Ca2+"
- [447] PON1 P27169, EC 3.1.8.1, metals_ions, edge, ext, class B, refs 1: "contains Ca2+"
- [448] PON1 P27169, EC 3.1.8.1, metals_ions, edge, ext, class B, refs 1: "required for enzyme stability and activity"
- [453] PON1 P27169, EC 3.1.8.1, metals_ions, edge, ext, class B, refs 1: "dependent on. The enzyme possesses 2 Ca2+ ions"
- [802] PON1 P27169, EC 3.8.2.2, metals_ions, edge, ext, class C, refs 7: "dependent on"
- [328] AOAH P28039, EC 3.1.1.77, metals_ions, edge, ext, class C, refs 1: "CaCl2 enhances activity at pH 4.8 by 1.5-2 fold"
- [329] AOAH P28039, EC 3.1.1.77, metals_ions, edge, ext, class D, refs 1: "5 mM enhances activity by 30-50% at low substrate concentration, inhibitory at high substrate concentration"
- [699] MMP12 P39900, EC 3.4.24.65, metals_ions, edge, ext, class N, refs 4: "(no comment)"
- [75] TGM4 P49221, EC 2.3.2.13, inhibitor, edge, ext, class E [mM], refs 1: "10 mM"
- [82] TGM4 P49221, EC 2.3.2.13, metals_ions, edge, ext, class D, refs 1: "optimal concentration: 5 mM"
- [506] KLK7 P49862, EC 3.4.21.117, metals_ions, edge, ext, class C, refs 1: "slight activation"
- [507] KLK7 P49862, EC 3.4.21.117, metals_ions, edge, ext, class C, refs 1: "slight enhancement of activity"
- [508] KLK7 P49862, EC 3.4.21.117, metals_ions, edge, ext, class N, refs 2: "(no comment)"
- [782] ENTPD1 P49961, EC 3.6.1.5, metals_ions, edge, ext, class C, refs 11: "required"
- [707] MMP14 P50281, EC 3.4.24.80, metals_ions, edge, ext, class B, refs 1: "enzyme-bound"
- [708] MMP14 P50281, EC 3.4.24.80, metals_ions, edge, ext, class C, refs 1: "a calcium- and zinc-dependent transmembrane endopeptidase"
- [425] GPLD1 P80108, EC 3.1.4.50, metals_ions, edge, ext, class C, refs 1: "requirement"
- [426] GPLD1 P80108, EC 3.1.4.50, metals_ions, edge, ext, class C, refs 3: "activation"
- [491] FOLH1 Q04609, EC 3.4.17.21, metals_ions, edge, ext, class B, refs 1: "even a slight disruption of the Ca2+-binding site destabilizes the three-dimensional fold of glutamate carboxypeptidase II and is associated with impaired secretion, a high propensity to form nonphysiological oligomers, and an inability to bind active site-targeted ligands. Additionally, the Ca2+-bi"
- [477] ENPEP Q07075, EC 3.4.11.7, activating_compound, edge, ext, class I, refs 1: "Ca2+ up- or down-regulates the enzyme activity depending on the substrate tested"
- [474] ENPEP Q07075, EC 3.4.11.7, inhibitor, edge, ext, class E [un], refs 1: "inhibits activity with Gln-substrate, regulatory function and influence on substrate specificity"
- [475] ENPEP Q07075, EC 3.4.11.7, inhibitor, edge, ext, class E [un], refs 1: "substrate-specific inhibition, overview"
- [476] ENPEP Q07075, EC 3.4.11.7, inhibitor, edge, ext, class I, refs 1: "Ca2+ up- or down-regulates the enzyme activity depending on the substrate tested"
- [478] ENPEP Q07075, EC 3.4.11.7, metals_ions, edge, ext, class C, refs 10: "activation"
- [479] ENPEP Q07075, EC 3.4.11.7, metals_ions, edge, ext, class I, refs 1: "activates activity with some substrates, decreases activity with other substrates, required for activity with Asp-/Glu-substrates, regulatory function and influence on substrate specificity"
- [480] ENPEP Q07075, EC 3.4.11.7, metals_ions, edge, ext, class D, refs 1: "activates, best at 1 mM, substrate-specific activation"
- [481] ENPEP Q07075, EC 3.4.11.7, metals_ions, edge, ext, class D, refs 1: "maximal activation at 4 mM Ca2+"
- [705] PAPPA Q13219, EC 3.4.24.79, metals_ions, edge, ext, class B, refs 1: "the LNR module reversibly binds a calcium ion and that bound calcium is required for antibody binding"
- [706] PAPPA Q13219, EC 3.4.24.79, metals_ions, edge, ext, class D, refs 1: "1 mM used in assay conditions"
- [416] ENPP2 Q13822, EC 3.1.4.39, metals_ions, edge, ext, class C, refs 1: "required"
- [417] ENPP2 Q13822, EC 3.1.4.39, metals_ions, edge, ext, class I, refs 1: "check the sensitivity to metals for the human and murine isoforms, concentrations ranging from 0.1 to 1000 mM"
- [418] ENPP2 Q13822, EC 3.1.4.39, metals_ions, edge, ext, class I, refs 1: "check the sensitivity to metals for the human and murine isoforms, concentrations ranging from 0.1 to 1000 mM"
- [419] ENPP2 Q13822, EC 3.1.4.39, metals_ions, edge, ext, class F, refs 1: "similar stimulation of LysoPLD activity by addition of Ca2+ and Mg2+ occurs. Mg2+ or Ca2+ may act to stabilize the structure of ATX or shield the electric charge of the substrate"
- [300] PON3 Q15166, EC 3.1.1.25, metals_ions, edge, ext, class C, refs 3: "dependent on"
- [668] MEP1A Q16819, EC 3.4.24.18, inhibitor, edge, ext, class E [mM], refs 1: "above 1 mM, metalloproteinase, does not require additional Ca2+"
- [669] MEP1A Q16819, EC 3.4.24.18, metals_ions, edge, ext, class I, refs 3: "metalloendopeptidase"
- [670] MEP1A Q16819, EC 3.4.24.18, metals_ions, edge, ext, class E [mM], refs 1: "Ca2+ inhibits above 1 mM"
- [671] MEP1A Q16819, EC 3.4.24.18, metals_ions, edge, ext, class B, refs 2: "3 mol calcium per mol subunit (atomic absorption spectroscopy)"
- [672] MEP1A Q16819, EC 3.4.24.18, metals_ions, edge, ext, class C, refs 1: "Ca2+ reactivates inactive apoenzyme"
- [673] MEP1A Q16819, EC 3.4.24.18, metals_ions, edge, ext, class C, refs 1: "required"
- [695] MEP1B Q16820, EC 3.4.24.63, inhibitor, edge, ext, class E [un], refs 1: "calcium negatively regulates meprin beta activity and attenuates substrate cleavage"
- [696] MEP1B Q16820, EC 3.4.24.63, inhibitor, edge, ext, class E [un], refs 1: "inhibits, a negative regulator of meprin beta"
- [697] MEP1B Q16820, EC 3.4.24.63, metals_ions, edge, ext, class C, refs 1: "required"
- [698] MEP1B Q16820, EC 3.4.24.63, metals_ions, edge, ext, class E [un], refs 1: "physiologic calcium concentrations display a dual role by (1) directly inhibiting meprin beta activity and (2) supporting meprin beta folding during biosynthesis"
- [333] NOTUM Q6P988, EC 3.1.1.98, metals_ions, edge, ext, class D, refs 1: "5 mM used in assay conditions"
- [711] ADAMTS13 Q76LX8, EC 3.4.24.87, inhibitor, edge, ext, class E [un], refs 1: "enzyme catalytic activity in blood plasma is tuned by varying buffer calcium, with lower divalent ion concentrations enhancing cleavage"
- [712] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class C, refs 8: "required"
- [713] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class C, refs 1: "dependent on"
- [714] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class C, refs 1: "dependent"
- [715] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class C, refs 1: "activating"
- [716] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class B, refs 1: "Ca2+ binding site with coordinates Asp173, Cys281, Asp284, and Met249, activating"
- [717] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class B, refs 1: "metalloprotease, conserved binding site using Glu83, ASp173, Cys281, Asp284"
- [718] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class C, refs 1: "cooperative role for Ca2+ and Zn2+ in supporting ADAMTS13 activity"
- [719] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class B, refs 1: "ADAMTS13 has a predicted calcium-binding site"
- [720] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class D, refs 1: "in citrate-anticoagulated plasma activity is enhanced about 3fold by calcium ions (up to 5 mM), cleavage of von Willebrand factor by recombinant ADAMTS13 is activated up to 200fold by calcium ions"
- [721] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class B, refs 1: "highly dependent on, Ca2+ induces a conformational change in ADAMTS13, but only under low-ionic-strength conditions, which is abolished in mutants E83A and D173A. The Ca2+-binding site in proximity to the ADAMTS13 active site comprises Glu184, Asp187, and Glu212, identified by homology modelling. Mu"
- [722] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class D, refs 1: "ADAMTS13 activity in the reaction buffer containing 0.9 mM Ca2+ without incubation is enhanced 2.7times compared to the value determined in the absence of Ca2+. The activity of ADAMTS13 in the presence of 10 mM Ca2+ is enhanced 3-5fold"
- [723] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class C, refs 1: "Ca2+ ions are also required for enzyme function"
- [724] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class B, refs 1: "the catalytic domain of the enzyme possesses up to three putative Ca2+ binding sites"
- [725] ADAMTS13 Q76LX8, EC 3.4.24.87, metals_ions, edge, ext, class B, refs 1: "ADAMTS13 binds coiled von Willebrand factor primarily through the CUB domain in a calcium-dependent manner"
- [581] PCSK9 Q8NBP7, EC 3.4.21.61, metals_ions, edge, ext, class C, refs 7: "required"
- [494] GGH Q92820, EC 3.4.19.9, metals_ions, edge, ext, class C, refs 1: "slight activation"
- [495] GGH Q92820, EC 3.4.19.9, metals_ions, edge, ext, class C, refs 2: "activation"
- [488] CPB2 Q96IY4, EC 3.4.17.20, metals_ions, edge, ext, class C, refs 1: "required for activation of the enzyme"
- [489] CPB2 Q96IY4, EC 3.4.17.20, metals_ions, edge, ext, class C, refs 1: "required for enzyme activation"
- [511] CTRC Q99895, EC 3.4.21.2, inhibitor, edge, ext, class E [mM], refs 1: "increasing the Ca2+ concentration from 0.025 mM to 1 mM progressively inhibits the degradation of cationic trypsin by chymotrypsin C, with essentially complete protection observed at 1 mM Ca2+"
- [545] KLK15 Q9H2R5, EC 3.4.21.35, metals_ions, edge, ext, class D, refs 1: "Ca2+ enhances the enzyme activity at concentrations of 2.5 and 5 mM"
- [727] ASAH2 Q9NR71, EC 3.5.1.23, metals_ions, edge, ext, class C, refs 3: "required"
- [728] ASAH2 Q9NR71, EC 3.5.1.23, metals_ions, edge, ext, class C, refs 3: "activates"
- [791] ENTPD2 Q9Y5L3, EC 3.6.1.5, metals_ions, edge, ext, class C, refs 1: "activates, required"
- [503] ST14 Q9Y5Y6, EC 3.4.21.109, metals_ions, edge, ext, class C, refs 1: "required for autoactivation"

## 6. Candidate rules and their edge counts (the 263 Ca2+ regulation edges on `MAM01413c` in v5)

Common to every rule: an edge on a `pump` protein moves to `NEURON_MAM01413c` as `activates`; an edge on an `ext` protein is
retargeted to `MAM01413e` with its relation unchanged (ADAM10 excepted, moved as `activates`); an edge on a `lum`, `memb` or
`mito` protein stays on `MAM01413c`, inert, with the limit recorded; an edge whose records are all class G or I is dropped, as is
a `cofactor_of` edge whose only `metals_ions` record states inhibition (EPHX1, "20% inhibition at 1 mM"; sign wrong); an edge
whose only record has no comment stays where it is. The rules differ on the cytosolic proteins.

| Rule | What moves, on a `cyt` protein | move to pool | of which `activates` / `inhibits` / `cofactor_of` | retarget to `MAM01413e` | stay on `MAM01413c` (cytosolic, inert) | stay (lumenal or unstated face) | stay (mitochondrial) | drop | proteins the pool reaches |
|---|---|---|---|---|---|---|---|---|---|
| **R1 sensing** | `cofactor_of`/`activates` edge with at least one class A record moves as `activates`; `inhibits` edge with an E `cyt` record moves as `inhibits` | 46 | 43 / 3 / 0 | 70 | 94 | 37 | 4 | 12 | 45 |
| **R2 sensing or bare** | as R1, and an edge whose records are bare (class C) with no A moves as `cofactor_of`; `inhibits` with E `cyt` or E `un` moves | 97 | 43 / 8 / 46 | 70 | 43 | 37 | 4 | 12 | 93 |
| **R3 all cytosolic** | every edge on a `cyt` protein moves with its relation (A records as `activates`) | 140 | 47 / 23 / 70 | 70 | 0 | 37 | 4 | 12 | 129 |

Each row sums to 263. "stay on `MAM01413c`" under R1 is 83 edges whose cytosolic records are bare, millimolar, structural or
nonspecific, plus 11 whose one record has no comment; under R2 it is 22 + 11 (the millimolar, structural and nonspecific ones);
under R3 none.

**The 46 edges R1 moves** (46 rows; gene, relation, class mix): EEF2K cofactor_of (A7 C6); ADAM10 cofactor_of (A2); PLSCR1 cofactor_of (A1); ALOX15B cofactor_of (A1); ADCY6 inhibits (E2); ATP2C2 cofactor_of (H1); NADK cofactor_of (A1 G1); EGFR cofactor_of (A1); CAPN1 cofactor_of (A7 B1 C6 D4); ALOX5 cofactor_of (A8 B1 C6 D3 I1); PLCG2 cofactor_of (A1); ATP2B1 cofactor_of (H1); CAPN3 cofactor_of (A1 C6 D2); TGM2 cofactor_of (A3 C6); ITPKA cofactor_of (A1); DGKA cofactor_of (A2 C1); ITPKB cofactor_of (A1); NOS1 cofactor_of (A1); CTH cofactor_of (A1); PHKA2 cofactor_of (A1); PDE1A activates (A1); ATP2C1 cofactor_of (H1); PDE1B cofactor_of (A1 C1); ATP2B2 cofactor_of (H1); GUCY1A1 inhibits (E1); GUCY1B1 inhibits (E1); GUCY2D cofactor_of (A1); PPP3CA cofactor_of (A1 C2); CAMK2B cofactor_of (A1); CAMK2D cofactor_of (A1 C1); CAMK1 cofactor_of (A2 C1); PDE1C activates (A1); PDE1C cofactor_of (A1); PTK2B activates (A1); ESPL1 cofactor_of (A1); CAMK4 cofactor_of (A3 C1 D1); ATP2B3 cofactor_of (H1); UBE3B activates (A1); TTL cofactor_of (A1); CERK cofactor_of (A1 F2); ITPKC cofactor_of (A1); PPP3R2 cofactor_of (A1); CAMK1G cofactor_of (A1); CAMKK2 cofactor_of (A1); RNF181 cofactor_of (A1); CAMK2A cofactor_of (A1).

**The 12 edges every rule drops**: PLD2 cofactor_of (G1, cyt); F2 activates (I1, ext); C1R inhibits (I1, ext); PRKCG cofactor_of (G1, cyt); EPHX1 cofactor_of (E1, cyt); CTSG cofactor_of (I1, ext); COMT inhibits (I1, cyt); THOP1 cofactor_of (I1, cyt); ENPEP activates (I1, ext); PLD1 cofactor_of (G1, cyt); GUK1 cofactor_of (G1, cyt); TPH2 cofactor_of (I1, cyt).

**What R1 says about the physiology**: the pool reaches the enzymes whose comments name the cell's calcium sensing (the CaM
kinases I, II and IV and CaMKK2, calcineurin and its B subunit, calpains 1 and 3, PLCG2, ALOX5 and ALOX15B, the PDE1s, DGKA,
ITPK A/B/C, NOS1, EEF2K, PHKA2, PLSCR1, EGFR, PTK2B, UBE3B, TTL, RNF181, CTH, ESPL1, GUCY2D, CERK) and is inhibited into ADCY6
and soluble guanylate cyclase; the pumps close their loops. The 94 cytosolic edges it leaves inert are the ones BRENDA's comment
cannot vouch for (bare "required" or "activates": TGM1/3/6, PADI1/3/4/6, PPP1CA/CB/CC, ADCY8/9/10, MYLK and MYLK2, CAMK2G, CAMK1D,
PLCB1, PLCH1, NOS3, DUOX2, DAGLA/B, PLSCR2/3/4, SRR), vouches against (PADI2, half-maximal at 0.18 mM and "at least 10 times
higher than cellular calcium concentrations"; SOD1 at 5 mM; KMT5A, TDG, SND1 and ATP11C with only an assay concentration), or
reads as nonspecific (ADK, PDXK, GALK1, TPK1, FLAD1, SPHK1, PPAT, RTCA, PEPD, TUBG1, LPIN1, ALG5: "can substitute for Mg2+").
Some of the bare ones are, by textbook physiology not read in this pass, calcium sensors (MYLK, ADCY8, CAMK2G, PLCB1, DUOX2),
which is the cost of a rule that reads BRENDA's comment and nothing else; R2 recovers them at the price of moving every bare
"required" on a cytosolic enzyme, including ones where the requirement is likely structural (the transglutaminases, the PADIs).
The 17 cytosolic `inhibits` edges R1 leaves are inhibition at 0.1 mM or more (HMBS, CSK, NUDT2, PPA1, NANS, GMPR2, CERK) or at
no stated concentration (EPHX1, APEX1, BLVRA, PSPH, NTHL1, THTPA, NOCT).

**Cases flagged for the owner, whichever rule**:

- GUCY2D (retinal guanylate cyclase): the one comment, "the activity of wild-type GC-E shows a strong dependency on free Ca2+ and
  GCAP1", gives no direction; the BRENDA edge is `cofactor_of` (+) and R1 would move it as `activates`. The direction of the
  GCAP-mediated regulation was not read in this pass and should be before a sign is given.
- NADK: record [183] "half-maximal activity at free calcium of approximately 0.0004 mM" (class A) beside record [184] "Ca2+/calmodulin
  has no detectable effect on recombinant human NAD kinase" (class G; 9.88's one `no_activation` case). The two are from different
  references; R1 moves the edge on the first.
- CERK: record [172] "stimulation above 0.0001 mM, maximal activation at 0.5 mM" is classed A on its onset at 100 nM, with two
  records saying Ca2+ "stimulates to a lesser extent than Mg2+" (F); borderline.
- TGM2: records [96], [98], [102] class A on the Ca2+/GTP allosteric switch; the enzyme is mainly cytosolic but its transamidase
  activity in the cell is held off by GTP at resting Ca2+, so the moved edge is right in direction and weak in effect.
- EEF2K, OGDH and NADK give sub-micromolar half-maxima; calpain 1 gives both "micromolar" (A) and 0.04-0.053 mM (D) from
  different references, and its edge moves on the A records.
- The three `inhibits` edges R1 moves: ADCY6 ("inhibition by low concentrations"; the class-level record [813] says "sub- and
  supra-micromolar"), GUCY1A1 and GUCY1B1 ("Carbachol-, thrombospondin-1-, or angiotensin II-induced increase of cellular Ca2+
  lowers SGC activity").
- PRKCG: BRENDA's one comment, "activity is independent of Ca2+", is classed G and the edge dropped, although PKC gamma is a
  conventional (Ca2+-dependent) isozyme; the class-level PKC records [204]-[206] that say so name no accession.

## 7. A dated addition for row 9.114 (1447 characters)

**Added 6 November 2026: the Ca2+ comments read into classes (a Fable pass; `brenda_calcium_comment_classes.md` and three CSVs in that session's scratchpad, not committed).** Of 880 human Ca2+ records (751 `metals_ions`, 111 inhibitor, 18 activating), 538 on 234 proteins make the 263 v5 edges. Their classes, by reading: sensing mechanism or physiological range 67 (12%), structural 69, bare "required/activates" 210 (39%), a stated concentration above the cytosolic range 60, inhibition 46 (4 at a cytosolic concentration or by a cellular mechanism), replaced by Mg2+/Mn2+ 30, no effect 5, pump substrate 5, indirect 19, no comment 27. By UniProt localisation 62 of the 234 proteins are secreted or ectoenzymes (coagulation, complement, MMPs, PON1; 70 edges), where `MAM01413e` is the compartment, 33 lumenal (37 edges), 4 mitochondrial, 5 pumps, 130 cytosolic. **Rules, of 263 edges**: R1 (move only on a named sensing mechanism or cytosolic range; pumps as `activates`) moves 46 (43 `activates`, 3 `inhibits`; CaMKs, calcineurin, calpains, PLCG2, ALOX5, PDE1s, NOS1, sGC, PMCA), retargets 70 to `MAM01413e`, leaves 94 cytosolic and 41 lumenal/mitochondrial edges inert, drops 12 (no effect, indirect, EPHX1's wrong sign); R2 (also bare "required") moves 97; R3 (every cytosolic edge) 140. Flagged: GUCY2D's comment gives no direction; NADK has a 400 nM half-maximum beside 9.88's no-effect note; 20 proteins lack UniProt location text locally.
