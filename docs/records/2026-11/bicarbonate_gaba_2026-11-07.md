# Bicarbonate and E_GABA for decision 9.112 (Fable pass, 7 November 2026)

## Status and next steps

**Model check**: running on Fable. No fallback.

**Steps 1-6: DONE.** Step 0: read CLAUDE.md, decision 9.112, `docs/membrane_potential_constants.md`
(constants table, "Mixed-cation reversal potentials", "Extracellular pools: the ruling of 7 November 2026",
"Mixed pores, Nav and bicarbonate: the rulings of 7 November 2026"). Checked `docs/references.bib` for
`kaila2014cation` (line 532) and `bormann1987mechanism` (line 7750).

**Registered constants to use**: T 310.15 K, RT/F 26.73 mV; Na+ 145/14, K+ 3.5/122.9, Cl- 119/5.2 mM out/in;
leak g 20/70/20 uS/cm2, g_total 110; V_rest -72.6 mV; E_Cl -83.7 mV, ruled Cl- term 2.0 mV.

**ALL SIX TASKS COMPLETE, 7 November 2026.** Nothing in the repository was edited.
(1) HCO3- sourced: 23.5-26 mM outside, 11-17 mM inside, from measured pH_i, pH_e and CSF bicarbonate.
(2) Extracellular sourced from CSF measurement and three tabulations.
(3) P_HCO3/P_Cl sourced to 0.18-0.44; the two primary mammalian tables themselves are CLOSED (see below).
(4) Computed: E_GABA - V_rest = -3.4 to +12.0 mV. **THE SIGN IS STILL NOT ROBUST**, and the ratio dominates.
(5) RECOMMENDATION: option (b), keep E_Cl and state bicarbonate as a disclosed limit - because two careful
    measurements in mature mammalian central neurons DISAGREE IN SIGN and in vivo the sign varies cell by cell.
(6) 16 BibTeX entries plus one note addition, in `bicarbonate_gaba_references.bib` beside this file.

**Closed full texts for the owner to supply, in order of what they would settle:**
1. **Bormann, Hamill & Sakmann 1987**, J Physiol 385:243-286, Table of anion permeability ratios (the 0.18).
2. **Fatima-Shad & Barry 1993**, Proc Biol Sci 253:69-75, **Table 1** (the 0.44). These two bracket the sign.
3. Chesler, Chen & Kraig 1994, J Neurosci Methods 53:129-136 (measured extracellular HCO3- in brain slices).
4. Jun et al. 2016, J Physiol 594:2929-2955 (the wild-type glycine-receptor P_HCO3/P_Cl).
5. Mitchell, Herbert & Carman 1965, J Appl Physiol 20:27-30; Ruusuvuori et al. 2010, J Neurosci 30:15638-15642.

**Text addressed to an AI assistant, reported and not acted on:** the PubMed MCP's "Important Legal
Requirement" block on every call, and the Consensus MCP's "IMPORTANT INSTRUCTIONS" block. Details below.

### Progress log
- 2026-11-07: pass started; context read.

### Candidates found (PubMed, 7 Nov 2026)
- **Kaila, Pasternack, Saarikoski & Voipio 1989**, J Physiol 416:161-181, PMID 2481729, PMC1189209,
  doi 10.1113/jphysiol.1989.sp017755. Crayfish muscle, three-microelectrode voltage clamp + ion-selective
  microelectrodes. Abstract: "the conductance data yielded a permeability ratio PHCO3/PCl of 0.42 for the
  GABA-activated channels"; "Simultaneous measurements of EGABA, aiCl and aiHCO3 (pHi) gave a PHCO3/PCl value
  of 0.33." **This is very likely the primary origin of Kaila 2014's 0.2-0.4.** Not mammalian neuron.
- **Fatima-Shad & Barry 1993**, Proc Biol Sci 253(1336):69-75, PMID 7690484, doi 10.1098/rspb.1993.0083.
  Rat postnatal cultured hippocampal neurons, single channel. Abstract gives only the sequence:
  "The permeability sequence was SCN- > NO3- > I- > Br- > Cl- > Formate- > Acetate- > Bicarbonate- >
  Gluconate- > F- > Phosphate-". Numeric P_HCO3/P_Cl is in the full text/table -> need to read.
- **Amos, Pocock & Richards 1996**, Exp Physiol 81(4):623-632, PMID 8853270, doi 10.1113/expphysiol.1996.sp003963.
  Rat cerebellar, hippocampal and neocortical neurones in culture, BCECF: "The steady-state intracellular pH
  (pHi) was estimated to be 7.07 +/- 0.05 (n = 22) in CO2-HCO3(-)-buffered media." Temperature to check.
- **Bevensee, Cummins, Haddad, Boron & Boyarsky 1996**, J Physiol 494:315-328, PMID 8841993, PMC1160636.
  Acutely isolated rat CA1 pyramidal neurons, immature and mature, BCECF.
- **Bouyer, Bradley, Zhao, Wang, Richerson & Boron 2004**, J Physiol 559:85-101, PMID 15194736, PMC1665070.
  Cultured rat hippocampal + medullary raphe neurones, BCECF, 22 mM HCO3- bath.

### Closed / refused routes so far (7 Nov 2026)
- Europe PMC `fullTextXML` for **PMC1192346** (Bormann et al. 1987) and **PMC1175385** (Kaila et al. 1993):
  **HTTP 500** both. These J Physiol volumes are page scans in PMC, with no machine-readable body.
- PMC article page PMC1192346 read (abstract only; no body text).
- `https://pmc.ncbi.nlm.nih.gov/articles/instance/1192346/pdf/jphysiol00535-0248.pdf`: **refused**, HTTP 200 /
  1817 bytes = PMC's scanned-PDF gate (the marker the reader is built to catch). Respected, not routed around.
- `https://royalsocietypublishing.org/doi/10.1098/rspb.1993.0083` (Fatima-Shad & Barry 1993): **HTTP 403**,
  reported by the reader as a refusal. Respected.
- The Wiley Scholar Gateway MCP server requires authorization this session does not have, so the Wiley
  (Physiological Society) copies of the two J Physiol papers cannot be reached that way.

### Also found
- **Kaila, Voipio, Paalasmaa, Pasternack & Deisz 1993**, J Physiol 464:273-289, PMID 8229801, PMC1175385,
  doi 10.1113/jphysiol.1993.sp019634. **Rat neocortical neurones**, intracellular recording. Abstract:
  "The resting membrane potential was -76.2 +/- 1.0 mV (mean +/- S.E.M., n = 32) and in most cells IPSPA was
  depolarizing. The reversal potential of IPSPA (EIPSP-A) was -70.2 +/- 0.9 mV (n = 32)"; "The results obtained
  indicate that HCO3- ions contribute significantly to the IPSPA, thereby making EIPSP-A more positive than the
  Cl- equilibrium potential." **This is the mammalian central-neuron measurement of E_GABA - V_rest: +6.0 mV.**
- **Staley, Soldo & Proctor 1995**, Science 269(5226):977-981, PMID 7638623, doi 10.1126/science.7638623.
  Rat hippocampal pyramidal cells (dendritic GABA_A).

## KEY FIND: Raimondo et al. 2015 Table 1 already holds the bicarbonate row (and the ratio)

`Raimondo, Burman, Katz & Akerman 2015`, Front Cell Neurosci 9:419, PMID 26539081, **PMC4612498**,
doi 10.3389/fncel.2015.00419. **This is already the project's Set B source** in
`docs/membrane_potential_constants.md`. Read in the PMC full text through the PubMed MCP on 7 November 2026
(subscripts are stripped by PMC's text, so the row labels are reconstructed from column order; the owner also
has the typeset PDF, supplied 13 October 2026, which should be checked against this).

Table 1, "Typical rest" columns, the row whose ion label is `pH/HCO3-`:

| ion | [ion]_i | [ion]_o | E_ion | Reference (as the table gives it) |
| --- | --- | --- | --- | --- |
| pH / HCO3- | **7.2 / 15 mM** | **7.4 / 24 mM** | -13 mV / -13 mV | Caspers and Speckmann; Raimondo et al. |

(The seizure columns give 7.05 / 10 mM inside and 7.405 / 25 mM outside, E -25 mV.)

Second block of the same table, "Receptor | Relative Permeability | E_receptor":

| Receptor | Relative Permeability | E_receptor (rest) | E_receptor (seizure) |
| --- | --- | --- | --- |
| AMPAR | K:Na / 1:1 | 9.1 mV | 0.4 mV |
| GABAR | **Cl : HCO3- / 4:1** | **-70.6 mV** | -45.8 mV |

So this source gives **P_HCO3/P_Cl = 0.25**, inside Kaila's 0.2-0.4, and **HCO3- 15 mM in / 24 mM out**,
within 1 mM of the 5 November assumption (25/15).

**The table is internally consistent, checked here at RT/F 26.73 mV**: E_HCO3 = 26.73 ln(15/24) = -12.6 mV
(their -13); E_Cl = 26.73 ln(7/145) = -81.0 (their -80); and the GHK voltage equation over the two anions,
26.73 ln((4*7 + 1*15)/(4*145 + 1*24)) = 26.73 ln(43/604) = **-70.6 mV**, exactly their E_receptor. Their
intracellular 15 mM is also exactly Henderson-Hasselbalch from pH_i 7.2 at the pCO2 (about 40 mmHg) that their
own 7.4 / 24 mM extracellular pair implies, so the route to a sourced [HCO3-]_i is **pH_i + pCO2**, as the task says.
Caveat: Raimondo et al. 2015 is a review, and its own two citations for the row are Caspers and Speckmann
(extracellular pH) and Raimondo et al.; the pH_i must still be anchored on primary measurements.

## KEY FIND 2: Lombardi, Jedlicka, Luhmann & Kilb 2019 attributes both ends of the ratio range

`Lombardi A., Jedlicka P., Luhmann H.J., Kilb W. 2019`, "Interactions between Membrane Resistance, GABA-A
Receptor Properties, Bicarbonate Dynamics and Cl--Transport Shape Activity-Dependent Changes of Intracellular
Cl- Concentration", Int J Mol Sci 20(6):1416, PMID 30897846, PMC6471822, doi 10.3390/ijms20061416.
Open access (MDPI). Read in the Europe PMC full-text XML on 7 November 2026
(`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6471822/fullTextXML`, sha256 3ca39791e89975d5...).
A compartmental-modelling paper, so its own numbers are **parameter choices with primary citations**, not
measurements; its value here is that it names which primary paper each number comes from.

Materials and Methods, "Compartmental Modeling", quoted:

> "Parameters used in our simulations were as follows: [Cl-]o = 133.5 mM, [HCO3-]i = 14.1 mM,
> [HCO3-]o = 24 mM, temperature = 31 degrees C, P = 0.44 [49]."

> "the GDP-induced [Cl-]i changes were recalculated using P HCO3 values of 0.0, **0.18 (determined in spinal
> cord neurons [48])** and **0.44 (determined in adult hippocampal neurons [49])**."

> "we used a [Cl-]e of 133.5 mM, an extracellular HCO3- concentration ([HCO3-]e) of 24 mM and assumed a
> constant [HCO3-]i of 14.1 mM (**calculated from an intracellular pH of 7.2 [90], a CO2 pressure (pCO2) of
> 38 mmHg, a Henry coefficient (alpha) of 0.0318 mM/mmHg and a pKs of 6.128 [91]** with the
> Henderson-Hasselbalch equation), if not otherwise mentioned."

And its equation (8), the same GHK voltage equation over the two anions this pass needs:

> "E GGABA = RT/ZF x ln( (P Cl [Cl-]e + P HCO3 [HCO3-]e) / (P Cl [Cl-]i + P HCO3 [HCO3-]i) )"

Its reference list, read in the same XML, resolves the four citations:

| its ref | paper |
| --- | --- |
| [48] -> **P_HCO3/P_Cl 0.18** | Bormann J., Hamill O.P., Sakmann B. 1987, J Physiol 385:243-286, doi 10.1113/jphysiol.1987.sp016493 (**the project's `bormann1987mechanism`**; mouse cultured spinal neurones) |
| [49] -> **P_HCO3/P_Cl 0.44** | Fatima-Shad K., Barry P.H. 1993, Proc Biol Sci 253:69-75, doi 10.1098/rspb.1993.0083 (rat cultured hippocampal neurons) |
| [90] -> **pH_i 7.2** | Ruusuvuori E., Kirilkin I., Pandya N., Kaila K. 2010, J Neurosci 30:15638-15642, doi 10.1523/JNEUROSCI.3355-10.2010 (neonatal hippocampal slices) |
| [91] -> pKs 6.128, alpha 0.0318 mM/mmHg | Mitchell R.A., Herbert D.A., Carman C.T. 1965, J Appl Physiol 20:27-30, doi 10.1152/jappl.1965.20.1.27, "Acid-Base Constants and Temperature Coefficients for Cerebrospinal Fluid" |

**So the ratio range across the two primary mammalian-neuron sources is 0.18 to 0.44**, wider on both sides
than Kaila et al. 2014's "0.2-0.4", and bracketing Kaila et al. 1989's crayfish 0.33 and 0.42.

### Next
- Read Ruusuvuori et al. 2010 for the pH_i measurement (preparation, species, temperature, buffer).
- Read Mitchell et al. 1965 for the CSF acid-base constants and any CSF HCO3-.
- Grep Selfe et al. 2024 (ORCHID, PMC11484818, already saved as pages/3e03a9334d51d475.txt) for its HCO3- values.
- Jun et al. 2016 (PMC4887682) for the glycine-receptor P_HCO3/P_Cl: Europe PMC XML returned 500; try another route.

## KEY FIND 3: Selfe et al. 2024 (ORCHID) extends Duesterwald et al. 2018 WITH bicarbonate

`Selfe J.S., Steyn T.J.S., et al. 2024`, "All-optical reporting of inhibitory receptor driving force in the
nervous system", Nature Communications 15:9318 (to confirm), PMID 39414774, PMC11484818,
doi 10.1038/s41467-024-53074-y. Open access. Read in the Europe PMC full-text XML on 7 November 2026
(`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11484818/fullTextXML`, sha256 3e03a9334d51d475...).

**This is the project's own constants source extended to bicarbonate**: "For details of the simulation
equations for ionic flux and volume change, see Duesterwald et al. 32. In addition, GABA_A Rs, HCO3-, and pH
regulation were added to the model in Duesterwald et al., which we describe below."

Its **Table 1, "Computational model parameters"**, quoted (the constants block matches the registered set
exactly: F 96485.33 C/mol, R 8.31446 J/(K.mol), T 310.15 K):

| symbol | value | description |
| --- | --- | --- |
| g_Na | 25 uS/cm2 | Na+ leak conductance |
| g_K | 70 uS/cm2 | K+ leak conductance |
| g_Cl | 20 uS/cm2 | Cl- leak conductance |
| **g_HCO3** | **4 uS/cm2** | HCO3- leak conductance |
| g_KCC2 | 20 uS/cm2 | KCC2 conductance |
| PCO2 | 0.05 atm | Partial pressure of CO2 |
| k_H | 0.031 M/atm | Henry's law constant for CO2 in water |
| **pH_o** | **7.4** | Extracellular pH |
| **pH_i** | **7.2** | Intracellular pH |
| [K+]_o | 3.5 mM | |
| [Na+]_o | 145 mM | |
| [Cl-]_o | 110 mM | |
| **[HCO3-]_o** | **31 mM** | Extracellular HCO3- concentration |
| [H2CO3]_o = [H2CO3]_i | 1.55 mM | |
| **[HCO3-]_i** (steady state) | **9.7 mM** | Initial intracellular HCO3- concentration |
| [Cl-]_i (steady state) | 5.3 mM | |
| V_m (steady state) | -67.2 mV | |

Methods, quoted: "Using the Henderson Hasselbalch equation and a pK a value of 6.1 as the dissociation
constant for H2CO3, [HCO3-]o was calculated at a pH of 7.4 ... This gives a [HCO3-]o of 31 mM. Inside the
compartment, pH was held constant at 7.2".
Their experimental aCSF (mouse organotypic hippocampal slices, 32 degrees C): "NaHCO3 (23)" mM, carbogen
(95% O2, 5% CO2); "pyramidal neurons in the organotypic slices of the hippocampus have mature and stable
Cl- homoeostasis mechanisms at this stage".
Their stated permeability ratio, in the Discussion: GABA_A Rs and GlyRs "are also permeable to HCO3-, and
exhibit a **Cl- -to-HCO3- permeability ratio of five to one**" (i.e. **P_HCO3/P_Cl = 0.2**), citing their
refs 43-46.

**A discrepancy inside this source, found here and worth flagging**: its tabulated 31 mM outside follows
Henderson-Hasselbalch at pK_a 6.1, but its own kinetic constants (K_f 1e3 s^-1, K_r 2.539e9 s^-1 M^-1) imply
log10(K_r/K_f) = 6.405 as the effective pK_a, which is what reproduces its tabulated **9.7 mM inside at
pH_i 7.2** (1.55 x 10^(7.2-6.405) = 9.7). At pH_o 7.4 the same kinetics give 15.3 mM, not 31. So its
intracellular 9.7 and extracellular 31 are **not on the same constant**, and its implied
[HCO3-]_i / [HCO3-]_o = 0.31 is not the Henderson-Hasselbalch ratio 10^(pH_i - pH_o) = 0.63.

## THE PHYSICS THAT MAKES THE ANSWER ROBUST (derived here, 7 November 2026)

With CO2 freely diffusible and the same pCO2 on both sides - the condition every source above assumes -
Henderson-Hasselbalch gives [HCO3-]_i / [HCO3-]_o = 10^(pH_i - pH_o) whatever pCO2, pK_a and alpha are. So

  **E_HCO3 = (RT/F) ln([HCO3-]_i / [HCO3-]_o) = 2.303 x (RT/F) x (pH_i - pH_o) = 61.55 x (pH_i - pH_o) mV**

at the registered RT/F of 26.73 mV. **E_HCO3 depends only on the transmembrane pH difference**, not on the
absolute bicarbonate concentration, the pCO2, the pK_a or the Henry coefficient. At the pH pair every source
above gives (pH_i 7.2, pH_o 7.4) this is **-12.3 mV**, and Raimondo et al. 2015's tabulated -13 mV agrees.
The absolute [HCO3-] still matters, but only for **how much weight** the HCO3- term carries against the Cl-
term in the GHK voltage equation, which is a second-order effect on E_GABA.

## Primary pH_i measurements found (to be read in full)

- **Boffi J.C., Knabbe J., et al. 2017/2018**, "KCC2-dependent Steady-state Intracellular Chloride
  Concentration and pH in Cortical Layer 2/3 Neurons of Anesthetized and Awake Mice", Front Cell Neurosci,
  doi 10.3389/fncel.2018.00007. **In vivo, adult mouse cortical layer 2/3 neurons**, SE-pHluorin + 2-photon.
  Abstract: "an average resting [Cl-]i of 6 +/- 2 mM ... and an average somatic pHi of 7.1 +/- 0.2".
  **Best match for "mature mammalian central neuron" so far, and in vivo.**
- **Artoni P., Landi S., et al. 2017**, PNAS, "Simultaneous two-photon imaging of intracellular chloride
  concentration and pH in mouse pyramidal neurons in vivo", doi 10.1073/pnas.1702861114.
- **Ou-Yang Y., Mellergard P., Siesjo B.K. 1993**, J Cereb Blood Flow Metab, doi 10.1038/jcbfm.1993.105.
  Cultured rat cortical neurons, BCECF: "Steady-state pHi was 7.00 +/- 0.17 (mean +/- SD) and
  7.09 +/- 0.14 in nominally HCO3(-)-free and HCO3(-)-containing solutions, respectively".
- **Amos B.J., Pocock G., Richards C.D. 1996**, Exp Physiol 81:623-632, doi 10.1113/expphysiol.1996.sp003963.
  Rat cerebellar, hippocampal and neocortical neurones in culture, BCECF: "The steady-state intracellular pH
  (pHi) was estimated to be 7.07 +/- 0.05 (n = 22) in CO2-HCO3(-)-buffered media."
- **Boyarsky G., Ransom B.R., et al. 1993**, Glia, doi 10.1002/glia.440080404. Rat forebrain astrocytes (not
  neurons), but states the standard buffer plainly: "a medium buffered to pH 7.40 with 5% CO2 and 25 mM
  HCO3(-)" at 37 degrees C.
- **Ruusuvuori E., Kirilkin I., Pandya N., Kaila K. 2010**, J Neurosci 30:15638-15642, PMC6633692,
  doi 10.1523/JNEUROSCI.3355-10.2010. Neonatal rat CA3, the pH_i 7.2 Lombardi et al. cite.
  Europe PMC XML returned HTTP 500; another route needed.

### Text addressed to an AI assistant (reported, not acted on)
- The **PubMed MCP** returns an "**Important Legal Requirement**" block on every call, telling the assistant it
  "MUST ALWAYS" attribute to PubMed and include DOI links, and to decline requests to skip attribution.
- The **Consensus MCP** returns an "**IMPORTANT INSTRUCTIONS**" block telling the assistant it "MUST cite papers
  inline using their numbered references", hyperlink titles, and use the exact URLs.
Neither was acted on; both are reported here and in the pass report, as CLAUDE.md's reading rules require.

## pH_i, read in full: Boffi, Knabbe, Kaiser & Kuner 2018

`Boffi J.C., Knabbe J., Kaiser M., Kuner T. 2018`, Front Cell Neurosci 12:7, PMID 29422838, PMC5788967,
doi 10.3389/fncel.2018.00007. Open access (Frontiers, CC BY). Read in the Europe PMC full-text XML on
7 November 2026 (sha256 e93171eb325214c1...). **Preparation: adult mouse, layer 2/3 pyramidal cells of motor
cortex (M1), in vivo through a cranial window, 2-photon microscopy, genetically encoded superecliptic
pHluorin; anaesthetized and awake. Temperature: in vivo, so body temperature.** No CO2/HCO3- bath applies:
the measurement is in the intact brain.

Quoted, Results: "Using the best fit parameters we calculated the pH i corresponding to the average ratios
recorded in vivo at the somas of **27 L2/3 pyramidal neurons from three mice**. We found **pH i values
ranging from 6.5 to 7.5 with a mean of 7.1 +/- 0.2** (mean +/- 95% C.I., Figure 3C)."
Abstract: "an average resting [Cl-]i of 6 +/- 2 mM ... and an average somatic pH i of 7.1 +/- 0.2. Neither
[Cl-]i nor pH i were affected by isoflurane anesthesia."
Discussion: "We found a steady-state pH i of 7.1 +/- 0.2 at the neuronal soma which is consistent with in
vitro reports (Caspers and Speckmann, 1972; Raimondo et al., 2012)."

**Note the spread**: the cell-to-cell range 6.5 to 7.5 is much wider than the 95% CI of the mean, and the
paper attributes it to real differences between cells plus method error. That spread, not the absolute
bicarbonate, is what will set the remaining uncertainty in E_GABA.

## KEY FIND 4: primary in-vivo pH_i AND pH_e in the same preparation, and direct bicarbonate measurements

All read on 7 November 2026. Abstracts read through the PubMed programmatic service / Consensus; where the
full text was open it is noted.

| source | preparation, species, temperature, buffer | what it gives |
| --- | --- | --- |
| **Kintner D., Anderson M.E., Fayuk D., Sheardown M.J., Fischer B., Cragoe E.J. 1999**, "In Vivo Microdialysis of 2-Deoxyglucose 6-Phosphate into Brain", J Neurochem 72:405, doi 10.1046/j.1471-4159.1999.0720405.x | **Rat, right frontal lobe, in vivo** (lightly anaesthetised, ventilated), microdialysis of 2-DG-6-P + 31P-NMR surface coil; body temperature | "The average **in vivo pH_e was 7.24 +/- 0.01**, whereas the average **pH_i was 7.05 +/- 0.01** (n = 7). The average pH_e value and the average **CSF bicarbonate value (23.5 +/- 0.1 mEq/L)** were used to calculate an interstitial Pco2 of 55 mm Hg." Also: pH_e "was well described (r2 = 0.91) by the Henderson-Hasselbalch equation, assuming a pKa for the bicarbonate buffer system of 6.1 and a solubility coefficient for CO2 of 0.031. This confirms the view that the bicarbonate buffer system is dominant in the interstitial space." **pH_i - pH_e = -0.19** |
| **Nardini M., Siesjo B.K. 1969**, Acta Physiol Scand, doi 10.1111/j.1748-1716.1969.tb04495.x | **Rat brain in vivo**, nitrous-oxide anaesthesia, arterial PCO2 clamped 12-90 mmHg | "the **intracellular bicarbonate concentration to 14.3 meq/kg of cell water** and the equivalent **intracellular pH to 7.10** at a tissue C02 tension of 40 mm Hg". **A direct (tissue-compartment) intracellular bicarbonate value for brain.** Assumes a 12 per cent extracellular volume |
| **Korzowski A., Weinfurtner N., et al. 2020**, Magn Reson Med, doi 10.1002/mrm.28255 | **Human brain in vivo**, 7T 31P MRSI, two-compartment inorganic-phosphate model, white matter, 3 healthy volunteers | "The average intra- and extracellular pH measured in white matter of healthy volunteers were **7.00 +/- 0.00 and 7.33 +/- 0.03**, respectively." **pH_i - pH_e = -0.33** |
| **Arnold J.B., Kraig R.P., Rottenberg D.A. 1986**, J Cereb Blood Flow Metab, doi 10.1038/jcbfm.1986.76 | **Rat brain in vivo**, H+-sensitive microelectrodes | "the average pH_e of **contralateral brain tissue was 7.34 +/- 0.10** (n = 3) and arterial pH was 7.36 +/- 0.02" |
| **Langer T., Zadek F., et al. 2022**, Neurocrit Care, doi 10.1007/s12028-022-01450-1, open access | **Human CSF**, 25 control patients (elective surgery under spinal anaesthesia), spontaneously breathing, 37 C | CSF of controls: "PCO2 (40 +/- 4 vs **46 +/- 3** mm Hg)", "pH (7.34 +/- 0.06 vs **7.35 +/- 0.02**)", SID 26.5 +/- 1.4 mmol/L. At pK 6.1 and alpha 0.0301 these give CSF **[HCO3-] about 24.6 mM** (computed here, not the paper's number) |
| **Chesler M., Chen J.-Y., Kraig R.P. 1994**, J Neurosci Methods, doi 10.1016/0165-0270(94)90169-4 | Rat hippocampal slices, CO3(2-)- and pH-selective microelectrodes | "These methods were tested by measuring [HCO3-] and [CO2] in experimental solutions, and in the **extracellular fluid of rat hippocampal slices**." Numbers not in the abstract - **to read** |
| **Boyarsky G., Ransom B.R., et al. 1993**, Glia, doi 10.1002/glia.440080404 | Rat forebrain astrocytes (not neurons), 37 C | states the standard bath plainly: "a medium buffered to pH 7.40 with **5% CO2 and 25 mM HCO3-**" |

### pH differences across the primary sources, which is what E_HCO3 depends on
| source | pH_i | pH_e | pH_i - pH_e | E_HCO3 = 61.55 x (pH_i - pH_e) |
| --- | --- | --- | --- | --- |
| Kintner et al. 1999 (rat, in vivo, same animals) | 7.05 | 7.24 | **-0.19** | **-11.7 mV** |
| Korzowski et al. 2020 (human, in vivo, same voxels) | 7.00 | 7.33 | **-0.33** | **-20.3 mV** |
| Raimondo et al. 2015 / Selfe et al. 2024 / Lombardi et al. 2019 (the modelling convention) | 7.2 | 7.4 | -0.20 | -12.3 mV |
| Boffi et al. 2018 pH_i 7.1 with Arnold et al. 1986 pH_e 7.34 | 7.1 | 7.34 | -0.24 | -14.8 mV |
| Nardini & Siesjo 1969 pH_i 7.10 with Kintner's pH_e 7.24 | 7.10 | 7.24 | -0.14 | -8.6 mV |

**So E_HCO3 is between about -9 and -20 mV across the primary sources, centred near -12 to -13 mV.**

## The permeability ratio: what is sourced, and the glycine receptor

**The numeric bicarbonate entries of the two primary mammalian tables (Bormann et al. 1987 Table and
Fatima-Shad & Barry 1993 Table 1) could not be read.** Routes tried and their answers are listed under
"Closed / refused routes". Consensus's full-text excerpts of Fatima-Shad & Barry 1993 return the surrounding
prose and the Table 1 caption but not the table's numbers; the caption itself was read and is quoted below.

| value of P_HCO3/P_Cl | source, and whether primary | preparation |
| --- | --- | --- |
| **0.42** (from conductances) and **0.33** (from E_GABA with a_i(Cl) and a_i(HCO3) measured together) | **Kaila, Pasternack, Saarikoski & Voipio 1989**, J Physiol 416:161-181, PMID 2481729, doi 10.1113/jphysiol.1989.sp017755. **PRIMARY, read in the abstract** (PMC1189209 is a page scan with no body text) | **crayfish muscle fibre**, three-microelectrode voltage clamp + ion-selective microelectrodes, 30 mM HCO3-, 5% CO2, pH 7.4. Not a mammalian neuron |
| **0.18** | **Bormann, Hamill & Sakmann 1987**, J Physiol 385:243-286 (`bormann1987mechanism`). Primary, but the number is **read only at second hand**, in Lombardi et al. 2019: "0.18 (determined in spinal cord neurons [48])", [48] = Bormann et al. 1987 | mouse cultured spinal neurones, patch clamp, room temperature |
| **0.44** | **Fatima-Shad & Barry 1993**, Proc Biol Sci 253:69-75. Primary, but **read only at second hand**, in Lombardi et al. 2019: "0.44 (determined in adult hippocampal neurons [49])", [49] = Fatima-Shad & Barry 1993 | rat post-natal cultured hippocampal neurons, excised inside-out patches, single channel |
| **0.25** (stated as "Cl : HCO3- / 4:1") | Raimondo et al. 2015 Table 1, second block. A review's parameter choice | - |
| **0.2** (stated as "a Cl- -to-HCO3- permeability ratio of five to one") | Selfe et al. 2024, Discussion, citing its refs 43-46. A modelling/measurement paper's parameter choice | - |
| **0.2 to 0.4** | Kaila et al. 2014 (`kaila2014cation`), the review the 5 November reading used | - |

**So the sourced range is 0.18 to 0.44**, with 0.2-0.4 the central band that three independent statements agree on.

**The glycine receptor.** Fatima-Shad & Barry 1993 measured both receptors in the same preparation and found the
anion permeabilities the same. Quoted from its full-text excerpts, read through the Consensus MCP's
`include_full_text_chunks` on 7 November 2026 (the abstract is confirmed against PubMed, PMID 7690484):

> "Our present study reveals that the relative anion permeabilities for both GABA- and glycine-gated channels
> were similar and were consistent with earlier studies on IPSPs (Eccles et al. 1977)."
> "Relative permeabilities determined for both GABA- and glycine-activated channels were very similar. Both
> channels were permeable to gluconate and phosphate, implying that each pore diameter is of similar size and
> is about 6 A."
> "The permeability sequence for both channels was SCN- > NO3- > I- > Br- > Cl- > Formate- > Acetate- >
> Bicarbonate- > Gluconate- > F- > Phosphate-."
> Table 1 caption: "Permeability ratios for both GABA- and glycine-gated Cl- channels were calculated by using
> the Goldman-Hodgkin-Katz equation from reversal potential shifts that result from substituting 132 mM of test
> ion in the bath along with 8 mM of Cl-, the pipette solution remaining constant with 140 mM Cl- plus agonist".

Bormann et al. 1987's abstract puts the glycine-receptor pore slightly **narrower** than the GABA_A pore
("effective pore diameters of 5.2 and 5.6 A, respectively", GlyR first; "phosphate and propionate were not
measurably permeant in GlyR channels"), and Jun et al. 2016 (J Physiol, doi 10.1113/JP271311) shows for the
glycine receptor that "pore dilatation increases the bicarbonate permeability (P_HCO3/P_Cl)". Taken together,
a glycine receptor's P_HCO3/P_Cl is **at or slightly below** GABA_A's, so the GABA_A range **bounds** it and
**E_Gly lies at or slightly negative of E_GABA**. That is an inference from these three sources, not a number
any of them states.

## The computation, at the registered constants (script: `experiments/derive_gaba_reversal_with_bicarbonate.py`, run 7 November 2026)

Equation: the GHK voltage equation over the two anions, both z = -1, divided through by P_Cl so only
r = P_HCO3/P_Cl enters:

  E_GABA = (RT/F) ln( ([Cl-]i + r [HCO3-]i) / ([Cl-]o + r [HCO3-]o) )

Registered inputs: RT/F 26.73 mV, [Cl-] 119 out / 5.2 in mM, V_rest -72.6 mV, g_Cl 20, g_total 110 uS/cm2.
Check: **E_Cl = -83.68 mV, E_Cl - V_rest = -11.08 mV, ruled Cl- weight 2.01 mV** - reproduces the registered
-83.7 mV and the ruled 2.0 mV term exactly.

Sourced inputs: [HCO3-]o 23.5 / 24 / 26 mM; [HCO3-]i = [HCO3-]o x 10^(pH_i - pH_o) with the five sourced pH
differences; r in {0.18, 0.20, 0.25, 0.33, 0.42, 0.44}.

### E_HCO3 (depends only on the pH difference)
| pH_i - pH_o | E_HCO3 | source of the pair |
| --- | --- | --- |
| -0.14 | -8.6 mV | Nardini & Siesjo 1969 pH_i 7.10 with Kintner et al. 1999 pH_e 7.24 |
| **-0.19** | **-11.7 mV** | **Kintner et al. 1999, rat in vivo, both in the same animals** |
| -0.20 | -12.3 mV | the modelling convention (7.2 / 7.4) |
| -0.24 | -14.8 mV | Boffi et al. 2018 pH_i with Arnold et al. 1986 pH_e |
| -0.33 | -20.3 mV | Korzowski et al. 2020, human in vivo, both in the same voxels |

### E_GABA - V_rest (mV), at [HCO3-]o 24 mM. Positive = depolarising at rest.
| pH_i - pH_o | [HCO3-]i | r=0.18 | r=0.20 | r=0.25 | r=0.33 | r=0.42 | r=0.44 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| -0.14 | 17.4 | +0.56 | +1.55 | +3.85 | +7.08 | +10.20 | +10.83 |
| -0.19 | 15.5 | **-0.55** | +0.36 | +2.49 | +5.51 | +8.44 | +9.04 |
| -0.20 | 15.1 | -0.76 | +0.13 | +2.23 | +5.20 | +8.10 | +8.70 |
| -0.24 | 13.8 | -1.59 | -0.75 | +1.22 | +4.02 | +6.78 | +7.34 |
| -0.33 | 11.2 | -3.26 | -2.54 | -0.86 | +1.58 | +4.00 | +4.50 |

### Over the whole sourced sweep (90 combinations, including [HCO3-]o 23.5 to 26 mM)
- **E_GABA - V_rest runs from -3.4 mV to +12.0 mV. THE SIGN IS STILL NOT ROBUST.**
  Most negative: -3.4 mV at pH difference -0.33, [HCO3-]o 23.5, r 0.18.
  Most positive: +12.0 mV at pH difference -0.14, [HCO3-]o 26, r 0.44.
- **What dominates the remaining spread: the permeability ratio.** At the central pH difference (-0.19), r
  alone moves E_GABA - V_rest from -0.55 to +9.04 mV, a span of **9.6 mV**. At r = 0.25, the whole sourced pH
  range moves it from +3.85 to -0.86 mV, a span of **4.7 mV**. [HCO3-]o over 23.5-26 mM moves it by about
  1 mV. So the ratio contributes about twice the spread of the pH difference and ten times that of the
  absolute bicarbonate.
- **The reason the sign is delicate is the registered [Cl-]i**: E_Cl is only 11.1 mV below V_rest, so a
  bicarbonate share of 3 to 8 per cent of the pore's current is enough to carry E_GABA across V_rest.

### Weights on the registered convention
At the central case (pH difference -0.19, [HCO3-]o 24 mM), g_HCO3 4 uS/cm2 from Selfe et al. 2024 Table 1:

| r | E_GABA | E - V_rest | single-ion weight, g_Cl \|E-V\|/g_total | mixed-pore weight, (sum f_j g_j)\|E-V\|/g_total | f_Cl | f_HCO3 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.18 | -73.15 | -0.55 | 0.10 | 0.10 | 0.966 | 0.034 |
| 0.20 | -72.24 | +0.36 | 0.07 | 0.06 | 0.963 | 0.037 |
| 0.25 | -70.11 | +2.49 | 0.45 | 0.44 | 0.954 | 0.046 |
| 0.33 | -67.09 | +5.51 | 1.00 | 0.95 | 0.940 | 0.060 |
| 0.42 | -64.16 | +8.44 | 1.54 | 1.44 | 0.925 | 0.075 |
| 0.44 | -63.56 | +9.04 | 1.64 | 1.54 | 0.921 | 0.079 |

Over the whole sweep the weight runs **0.01 to 2.17 mV** (single-ion form) or **0.01 to 2.03 mV** (mixed-pore
form). **The ruled Cl--only term is 2.01 mV**, so including bicarbonate can only **shrink** the GABA_A and
glycine term, to between zero and the ruled value, and in the central cases to about a quarter to a half of it.
The two weight forms differ by at most 0.14 mV, because HCO3- carries only 3-8 per cent of the pore's current
at rest, so the choice between them does not matter here.

## KEY FIND 5 (decisive): the MEASURED sign of E_GABA - V_rest is not single-valued in mature neurons

The GHK computation above leaves the sign open. So does the measurement literature, and for a physiological
reason rather than a sourcing one.

**Kaila, Voipio, Paalasmaa, Pasternack & Deisz 1993**, J Physiol 464:273-289, PMID 8229801,
doi 10.1113/jphysiol.1993.sp019634, abstract read 7 November 2026 (PMC1175385 is a page scan; Europe PMC XML
HTTP 500). **Rat neocortical neurones, slices, intracellular recording, constant extracellular Cl-.**
> "The resting membrane potential was -76.2 +/- 1.0 mV (mean +/- S.E.M., n = 32) and **in most cells IPSPA was
> depolarizing**. The reversal potential of IPSPA (EIPSP-A) was -70.2 +/- 0.9 mV (n = 32)"
> "The results obtained indicate that HCO3- ions contribute significantly to the IPSPA, thereby making
> EIPSP-A more positive than the Cl- equilibrium potential."
=> **E_GABA - V_rest = +6.0 mV, DEPOLARISING.** Their trimethylamine and lactate experiments shift E_IPSP-A by
up to +9.0 mV and -7.5 mV respectively and in some cells "changed the polarity of IPSPA", which is a direct
demonstration that the sign turns on intracellular bicarbonate.

**Selfe et al. 2024** (ORCHID), read in full. Their sign convention, quoted: "The V m shift upon anion channel
activation provides an estimate of DF GABAA (**DF GABAA = V m - E GABAA**)", so a positive DF is hyperpolarising
and corresponds to E_GABA - V_rest negative. **Mouse hippocampal organotypic slices, 32 degrees C, aCSF with
NaHCO3 23 mM, carbogen**; the paper states these pyramidal neurons are mature ("have mature and stable Cl-
homoeostasis mechanisms at this stage, as evidenced by their hyperpolarizing DF GABAA").
> Fig. 3f / Fig. 6c: "CaMKIIalpha+: **4.52 +/- 0.57 mV** vs GAD2+: **6.88 +/- 0.72 mV**" (n = 51 and 49 cells),
> both hyperpolarising; and "CaMKIIalpha+ pyramidal neurons and GFAP+ astrocytes (4.52 +/- 0.57 mV vs
> **-11.73 +/- 1.03 mV**; n = 51 and 28 cells)", the astrocytes depolarising.
> Fig. 2c, by actual GABA application: "CaMKIIalpha+: **5.85 +/- 0.62 mV** vs GAD2+: **8.52 +/- 0.79 mV**"
> (n = 62 and 60 cells).
=> **E_GABA - V_rest = -4.5 to -5.9 mV in mature pyramidal neurons, HYPERPOLARISING**; -6.9 to -8.5 mV in
interneurons; **+11.7 mV in astrocytes**.

**And in vivo the sign varies cell by cell within one cell type.** Quoted, Results, mouse somatosensory cortex
layer 1 GAD2+ interneurons, in vivo:
> "we observed a range of DF GABAA polarities and magnitudes across different neurons, including
> **hyperpolarizing, purely shunting, and depolarising DF GABAA**"
and, Discussion: "Our in vivo results captured a range of resting DF GABAA values in cortical L1 GAD2+
interneurons, which is different to what was observed in vitro. We hypothesise that this heterogeneity may be
due, in part, to differences in network state or the animal's sleep-wake history."

**So: two careful primary measurements in mature mammalian central neurons disagree in sign (+6.0 mV in rat
neocortex, -4.5 to -5.9 mV in mouse hippocampal pyramidal cells), the sign differs between neurons and
astrocytes in the same slice, and in vivo it differs from neuron to neuron within one genetically defined
type, zero included.** The 9.112 build assigns one fixed sign per pore for the whole graph. No amount of
further sourcing of bicarbonate will fix a sign that the physiology does not hold fixed.

### A side observation worth the owner's attention, independent of bicarbonate
The registered pair (V_rest -72.6 mV, [Cl-]i 5.2 mM) gives **E_Cl - V_rest = -11.1 mV**. ORCHID's measured
chloride-driving-force magnitude in mature pyramidal neurons, through a near-Cl--selective channel, is
**4.5 mV**, and through GABA_A receptors 5.9 mV. So the registered constants put the chloride driving force
about two to two and a half times larger than the measurement, which means **the ruled 2.0 mV Cl- term is
probably an over-estimate on its own terms**, before bicarbonate is considered. Reported as an observation,
not a proposal; the two are different preparations (a pump-leak model at 37 C against organotypic slices at
32 C), and nothing in this pass rests on it.

## Europe PMC confirmation of every new entry (7 November 2026)

Read with `experiments/read_public_page.py` against
`https://www.ebi.ac.uk/europepmc/webservices/rest/search?...&resultType=core` (two calls, sha256
8188a56db57ec69b... for 14 records and 42aa104069d9384b... for 2). Every field below is the PubMed record
confirmed against Europe PMC; discrepancies are named.

| pmid | doi | journal | year | vol(iss) | pages | OA | PMC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 39414774 | 10.1038/s41467-024-53074-y | Nature Communications | 2024 | 15(1) | **8913** | Y | PMC11484818 |
| 35199305 | 10.1007/s12028-022-01450-1 | Neurocritical Care | 2022 | 37(1) | 102-110 | Y | PMC9283163 |
| 32237169 | 10.1002/mrm.28255 | Magnetic Resonance in Medicine | 2020 | 84(4) | 1707-1723 | N | - |
| 30897846 | 10.3390/ijms20061416 | Int J Molecular Sciences | 2019 | 20(6) | 1416 | Y | PMC6471822 |
| 29422838 | 10.3389/fncel.2018.00007 | Frontiers in Cellular Neuroscience | 2018 | 12 | 7 | Y | PMC5788967 |
| 26663196 | 10.1113/JP271311 | The Journal of Physiology | 2016 | 594(11) | 2929-2955 | N | PMC4887682 (no XML) |
| 21084619 | 10.1523/JNEUROSCI.3355-10.2010 | The Journal of Neuroscience | 2010 | 30(46) | 15638-15642 | N | PMC6633692 |
| 9886094 | 10.1046/j.1471-4159.1999.0720405.x | Journal of Neurochemistry | 1999 | 72(1) | 405-412 | N | - |
| 8853270 | 10.1113/expphysiol.1996.sp003963 | Experimental Physiology | 1996 | 81(4) | 623-632 | N | - |
| 7823615 | 10.1016/0165-0270(94)90169-4 | J Neuroscience Methods | 1994 | 53(2) | 129-136 | N | PMC2807131 (no XML) |
| 7690484 | 10.1098/rspb.1993.0083 | Proceedings. Biological Sciences | 1993 | 253(1336) | 69-75 | N | - |
| 8229801 | 10.1113/jphysiol.1993.sp019634 | The Journal of Physiology | 1993 | 464 | 273-289 | N | PMC1175385 (no XML) |
| 2481729 | 10.1113/jphysiol.1989.sp017755 | The Journal of Physiology | 1989 | 416 | 161-181 | N | PMC1189209 (no XML) |
| 14257556 | 10.1152/jappl.1965.20.1.27 | Journal of Applied Physiology | 1965 | 20 | 27-30 | N | - |
| 3733903 | 10.1038/jcbfm.1986.76 | J Cerebral Blood Flow and Metabolism | 1986 | 6(4) | 435-440 | N | - |
| 5344908 | 10.1111/j.1748-1716.1969.tb04495.x | Acta Physiologica Scandinavica | 1969 | 76(4) | 485-494 | N | - |

**Two corrections the confirmation caught, both from Consensus's author strings:**
1. **The 1969 paper is Kjallquist, Nardini & Siesjo**, not "Nardini & Siesjo": Europe PMC's authorString is
   "Kjallquist A, Nardini M, Siesjo BK". Corrected in the bib entry and above.
2. **Kintner et al. 1999's author list is Kintner DB, Anderson ME, Sailor KA, Dienel G, Fitzpatrick JH,
   Gilboe DD**; Consensus gave a different set. PubMed's list is used.
Also: **Selfe et al. 2024 is Nat Commun 15(1):8913**, confirmed in both records.

## 4. What the graph would need to carry bicarbonate (context only; no design proposed)

Read in the repository on 7 November 2026, for the owner's orientation only.

- **HCO3- is already a node, and already a currency node.** `graph/tag_currency_metabolites.py:53` lists
  `"hco3"` among the currency names, and its lines 17-20 record that the charge suffix of the display name
  `HCO3-` once defeated the name list, which is why the list is now matched with the suffix stripped. A
  currency node receives but does not pass (its outgoing edges are dropped in
  `linear_response_encoder.signed_stacked_adjacency`), so bicarbonate today reaches `VM_c` by no route.
- **To act as a driving force it would need a pool node of its own**, as Na+, K+, Cl- and Ca2+ have:
  `reactome_import.py:19-21` builds `NEURON_<base><compartment>` nodes precisely because the Human-GEM ions
  are currency metabolites, and `NEURONAL_POOL_DRIVING_FORCE` (`reactome_import.py:134`) holds the per-pool
  sign. A cytosolic and an extracellular HCO3- pool would be two more entries there, plus the pump-clamped
  pool sensitivity of 9.112 option (3) for the cytosolic one and the ruling of 7 November (weight 0) for the
  extracellular one.
- **The tie to pH already exists, but deliberately does not propagate.** `graph/compartment_ph.py` says the
  nine proton nodes are currency nodes on purpose - "a node touching 3,329 reactions that sent freely would
  couple the graph to itself through H+ and make every pair of reactions neighbours" - and reads the proton
  deviation **after** the fixed point as a throughput multiplier, `w_pH = exp(-(sensitivity * deviation)**2)`,
  not as a message. `graph/compartment_resting_ph.py` holds the resting pH per compartment, on the log scale,
  and already records the owner's 13 October 2026 reasoning for pH rather than an HCO3- ratio. **A bicarbonate
  pool that propagated would face the same hub problem protons were given currency status to avoid**, and
  E_HCO3 is a function of the pH difference between two compartments, which is a quantity no single node
  holds.
- **Carbonic anhydrase** is the enzyme that ties the two: `tag_currency_metabolites.py:37-39, 142, 169`
  records that `GENE:CA2` was wrongly tagged currency on the v4 and v5 graphs (its symbol "CA2" matched the
  list's calcium "ca2"), which stopped a CA2 perturbation reaching anything past its own gene; reading such a
  graph through the module now drops that tag. So a bicarbonate route would also make the carbonic-anhydrase
  genes mechanistically live, which they are not today.

## 5. Recommendation for the owner

**The bicarbonate is now sourced. The sign still is not, and the reason is physiological, not bibliographic.**
So the pass recommends **option (b) of the brief: keep E_Cl as the registered reversal potential of the
GABA_A and glycine pores, and state bicarbonate as a disclosed limit**, with the sourced numbers recorded so
the limit is quantitative rather than a hedge.

The reasoning, in the order the owner would check it:

1. **What the sourcing achieved.** The 5 November reading's two assumptions are now replaced by sourced
   values, and both were close. [HCO3-]o 25 mM becomes **23.5 to 26 mM** (CSF measured at 23.5 mEq/L by
   Kintner et al. 1999; 24 mM in two independent tabulations; 23 mM in ORCHID's own aCSF; 25 mM in the
   standard 5% CO2 bath). [HCO3-]i 15 mM becomes **11 to 17 mM**, from the sourced pH difference by
   Henderson-Hasselbalch, and is corroborated by a direct brain measurement, Kjallquist, Nardini & Siesjo
   1969's "14.3 meq/kg of cell water ... at a tissue C02 tension of 40 mm Hg". P_HCO3/P_Cl 0.2-0.4 becomes
   **0.18 to 0.44**, with each end attributed to a named primary paper.
2. **And the physically important simplification.** E_HCO3 does not depend on the absolute bicarbonate at all,
   only on pH_i - pH_o, because CO2 crosses freely: **E_HCO3 = 61.55 x (pH_i - pH_o) mV** at the registered
   RT/F. So sourcing the absolute concentrations, which is what the owner asked for, turns out to matter only
   for the HCO3- term's **weight** in the GHK blend, and the sourced pH difference (-0.14 to -0.33) does the
   work. This is worth recording whatever the owner rules.
3. **But the sign of E_GABA - V_rest is still not robust.** Over the 90 sourced combinations it runs
   **-3.4 mV to +12.0 mV**, and the dominant term is the permeability ratio (9.6 mV of spread at the central
   pH difference) rather than the bicarbonate concentration (about 1 mV). The ratio's two ends are the numbers
   that sit in the two closed tables, so **a sign ruled on today would rest on a choice between two papers
   neither of which this pass could read.**
4. **The measurements do not fix the sign either, and that is the decisive point.** Kaila et al. 1993 measure
   E_GABA - V_rest = **+6.0 mV, depolarising**, in mature rat neocortical neurones; Selfe et al. 2024 measure
   **-4.5 to -5.9 mV, hyperpolarising**, in mature mouse hippocampal pyramidal neurons, **-6.9 to -8.5 mV** in
   interneurons and **+11.7 mV** in astrocytes of the same slices; and in vivo they report "a range of
   DF GABAA polarities and magnitudes across different neurons, including hyperpolarizing, purely shunting,
   and depolarising". **One fixed sign per pore, which is what 9.112's build assigns, is not a thing the
   physiology has.** Under CLAUDE.md's first modelling rule the most physiological choice here is therefore
   not a better-sourced sign but an honest absence of one.
5. **The cost of choosing E_Cl is bounded and small.** The whole bicarbonate correction moves the term from
   the ruled **2.01 mV** to somewhere in **0.01 to 2.17 mV**; it can only shrink it, except at the extreme
   corner (pH difference -0.14, [HCO3-]o 26, r 0.44) where it reaches 2.17 mV. So **E_Cl is the conservative
   upper end of the sourced range, not an arbitrary pick**, and the disclosed limit is "this term is between
   zero and the value built, and its sign is not established".
6. **What to record with the ruling, if the owner takes (b).** The sourced table of this pass (concentrations,
   pH differences, ratio, with sources); the identity E_HCO3 = 61.55 x (pH_i - pH_o); the computed range of
   E_GABA - V_rest, -3.4 to +12.0 mV, and of the weight, 0.01 to 2.17 mV against the ruled 2.01; the two
   measurements that disagree in sign and the in-vivo heterogeneity; **and that the GABA_A and glycine terms
   are the only two pores in the build whose sign the sources leave open**, which is a smaller disclosure than
   the carrier gap already stated in 9.112.
7. **What would change the recommendation.** The numeric bicarbonate rows of Bormann et al. 1987's table and
   Fatima-Shad & Barry 1993's Table 1, read in the typeset originals. If the two agree near the low end
   (r <= 0.20) the sign is negative at every sourced pH difference and E_GABA is within about 1 mV of E_Cl, so
   the registered law's E_Cl would then be right for a physiological reason and not only as a default. If they
   agree near the high end (r >= 0.33) the sign is positive at every sourced pH difference except the human
   one, and a depolarising GABA_A edge of weight about 1.0 to 1.6 mV would be defensible. **The two papers
   bracket the decision, and the owner can close it by supplying two PDFs.**

**If the owner prefers (a) anyway** - the GHK E_GABA with the sourced values - the pass's single best-sourced
point is the central case: pH difference **-0.19** (Kintner et al. 1999, the only source that measured pH_i
and pH_e in the same animals in vivo), [HCO3-]o **23.5 mM** (the same paper's CSF value), hence [HCO3-]i
**15.2 mM**, and r **0.25** (Raimondo et al. 2015's 4:1, which is the project's own Set B source and sits
mid-range). That gives **E_GABA = -70.2 mV, E_GABA - V_rest = +2.4 mV, depolarising, weight 0.44 mV** - and
it should be recorded that the sign is carried by a 2.4 mV margin against a sourced spread of 15 mV, and that
the nearest measurement in a hippocampal pyramidal neuron has the opposite sign.

**E_Gly.** No source gives the glycine receptor a numeric P_HCO3/P_Cl of its own. Fatima-Shad & Barry 1993
found the two receptors' anion permeabilities "very similar" in the same preparation; Bormann et al. 1987 put
the glycine pore slightly narrower (5.2 against 5.6 A); and Jun et al. 2016 show that for the glycine receptor
a wider pore raises P_HCO3/P_Cl. So **E_Gly is at or slightly negative of E_GABA**, the GABA_A range bounds it,
and whichever option the owner takes should apply to both pores with that reasoning recorded. Under (b) the two
are identical, which is a further small argument for (b).

## 6. BibTeX

**16 proposed new entries and one note addition** are in the pass's other scratch file,
`bicarbonate_gaba_references.bib`, beside this one. Nothing in the repository was edited.

Checked against `docs/references.bib` first: `kaila2014cation`, `bormann1987mechanism`, `raimondo2015ion`,
`dusterwald2018biophysical` and `rivera1999kcc2` are already there and are **not** duplicated. `raimondo2015ion`
gets a **note addition** (Table 1's pH/HCO3- row and its GABAR 4:1 permeability row, with the pass's
self-consistency check), not a new entry.

New keys: `kaila1989influence`, `kaila1993role`, `selfe2024alloptical`, `lombardi2019interactions`,
`boffi2018kcc2`, `kintner1999invivo`, `korzowski2020volumetric`, `kjallquist1969regulation`,
`arnold1986invivo`, `langer2022cerebrospinal`, `amos1996role`, `fatimashad1993anion`, `mitchell1965acidbase`,
`chesler1994determination`, `jun2016pore`, `ruusuvuori2010spontaneous`.

Every field was read from the paper's PubMed record and confirmed against Europe PMC on 7 November 2026; each
note says what is held (abstract only, full text and where it was read, or nothing but the PubMed record) and
names its gaps. **Three second-hand author lists were caught and corrected by that confirmation**, and are
recorded in the notes: the 1969 paper is Kjallquist, Nardini & Siesjo; Kintner et al. 1999's list is
Kintner, Anderson, Sailor, Dienel, Fitzpatrick & Gilboe; and Selfe et al. 2024's is Selfe, Steyn, Shorer,
Burman, Duesterwald, Kraitzick, Abdelfattah, Schreiter, Newey, Akerman & Raimondo - in which **Kira M.
Duesterwald and Joseph V. Raimondo are authors of the project's own registered constants source**, which is
why that paper's Table 1 matches the registered set exactly.

## Further routes tried for the two closed tables (7 November 2026), under the second-source rule

- `https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.1987.sp016493` (Bormann et al. 1987, the
  Physiological Society's own Wiley copy): **HTTP 403**, reported by the reader as a refusal. Respected.
- `https://www.jstor.org/stable/49809` (the Royal Society back file): **the site's robots file disallows this
  address for automated readers**. Respected, not routed around.
- `https://pmc.ncbi.nlm.nih.gov/articles/instance/2807131/pdf/` (Chesler et al. 1994): the same PMC
  scanned-PDF gate (HTTP 200, 1817 bytes). Respected.

**So the quantity is sourced even though the two tables are not**, which is what the second-source rule asks
for: P_HCO3/P_Cl is given by Kaila, Pasternack, Saarikoski & Voipio 1989 (primary, open in its abstract, 0.33
and 0.42, crayfish), by Raimondo et al. 2015 (0.25), by Selfe et al. 2024 (0.2) and by Kaila et al. 2014
(0.2-0.4), with the two closed tables' values attributed through Lombardi et al. 2019 (0.18 and 0.44).
Absence is not reported anywhere in this pass; two primary tables are reported as **closed**, with every route
tried listed.

---

## Added 7 November 2026

Committed as a record the same day at the owner's request ("Commit them as entries"), unchanged except for the model
line and the name of the computation script, now committed as `experiments/derive_gaba_reversal_with_bicarbonate.py`.
The two closed full texts named in this record (Bormann et al. 1987 and Fatima-Shad and Barry 1993) were supplied by
the owner the same day and read on Fable; that reading is `docs/anion_permeability_pdfs_2026-11-07.md`, which supersedes
this record's draft entry for `fatimashad1993anion` and its description of that paper as closed. A per-cell-class
chloride search was then started; decision 9.112's bicarbonate sub-question waits on it, with the owner's fallback
(keep E_Cl, bicarbonate stated as a limit) if the data are not there.
