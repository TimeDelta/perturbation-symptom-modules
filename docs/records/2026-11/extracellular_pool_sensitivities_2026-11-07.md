# Extracellular pool sensitivities for decision 9.112 (Fable pass, 7 November 2026)

## Status and next steps

COMPLETE (20:30 UTC, 7 November 2026). Model: Fable, no fallback at any step. Nothing in
the repository was edited. Pages read with `experiments/read_public_page.py` are saved under
`data/raw/public_pages/` (untracked), each with its address, time and SHA-256 in the `.json` beside it; the hashes
are in section 9. The derivation script was `ecs_pass/ecs_sensitivity.py` in the pass's working directory (its run `run2.txt` is the
one reported); it is committed as `experiments/derive_extracellular_pool_sensitivity.py`, and the 4 November script
as `experiments/derive_pump_leak_pool_sensitivity.py` (see the addition at the end).

If a later pass resumes: everything below is final except where marked "for the owner".

## 0. Question

The ruling of 4 November 2026 on 9.112 (options (1) and (3)) weights the six pool edges into `VM_c` by the
pump-clamped pool sensitivity. The cytosolic three were derived from Düsterwald et al. 2018 Table 1:
S_Na 0.0995, S_K 0.0035, S_Cl 0.833 (d ln[ion]_i per µA/cm² of the ion's own sustained inward current, pump and
KCC2 active). The source holds [Na+]o 145, [K+]o 3.5, [Cl-]o 119 mM constant, so the extracellular pools have no
weight. The owner asked: "Can you not source the value from another study to compare?". This pass derives the
extracellular sensitivities from more than one independent source and compares them.

## 1. Definition, and the cytosolic derivation reproduced

The derivation behind the cytosolic values is a scratch script of the 4 November pass, not in the repository
(decision 9.112: "the derivation script are in the pass report of 4 November 2026 (scratch, not committed)").
Rerun today, it reproduces the steady state ([Na+]i 14.00, [K+]i 122.87, [Cl-]i 5.16 mM, V_m -72.59 mV) and

    inward current of  d ln[Na]i  d ln[K]i  d ln[Cl]i   (per µA/cm², Düsterwald et al. 2018, ECS constant)
    Na+                 +0.0995   -0.0109    +0.1366
    K+                  -0.0248   +0.0035    +0.1990
    Cl-                 +0.0126   +0.0014    +0.8330

Definition (the script's docstring, kept here): a sustained inward molar flux density phi of one ion is added to
the Düsterwald et al. 2018 single-compartment pump-leak model (ohmic leaks g_Na 20, g_K 70, g_Cl 20 µS/cm²; pump
J_p = P ([Na+]i/[Na+]o)^3 with P = 0.1 C/(dm² s); J_KCC2 = g_KCC2 (E_K - E_Cl), g_KCC2 = 20 µS/cm²; osmotic and
charge constraints with water movement; extracellular concentrations constant; 37 °C). The new steady state is
solved and S_i = d ln[ion]_i / dI with I = F phi expressed in µA/cm². "Inward" is the ion moving into the cytosol,
for the anion too (so an inward Cl- flux is an outward electrical current). The extracellular value on the same
definition is S_o = d ln[ion]_o / dI for the same sustained inward flux, at steady state, with the pump, KCC2
and whatever the source gives the extracellular compartment (volume, glia, bath) active.

**The algebra that decides most of what follows** (the pass's reasoning, confirmed by every numerical case
below). At the new steady state the net transmembrane flux of each ion is zero again, otherwise [ion]_i would
still be drifting; so at steady state the neuron delivers no net flux to the extracellular space. Therefore:
- an ion whose extracellular pool exchanges with a reservoir by a flux that vanishes only when [ion]_o equals the
  reservoir's value (diffusive coupling to a bath or the vasculature, Hübel's eq. 35, Cressman's I_diff) has
  S_o = 0 exactly at steady state, whatever the exchange rate; the rate sets only the time constant of the
  transient. (Hübel and Dahlem: "the diffusive coupling Eq. (35) makes [K_e = K_bath] a necessary fixed point
  condition".)
- an ion with no reservoir (closed mass conservation between cytosol and ECS) has d(ion moles)_o = -d(ion
  moles)_i, so S_o ≈ -(V_i/V_e) ([ion]_i/[ion]_o) S_i, corrected by the water that follows the cytosolic change.
  This is why the closed value is large for K+ ([K+]i/[K+]o ≈ 35) and small for Na+ and Cl- (0.1 and 0.04).
- a reversible glial buffer of finite capacity (Hübel's scheme, taken from Kager et al. 2000) lies in between; at
  rest it holds almost nothing (section 2), so it behaves as the closed case.

So the extracellular values are not fixed by measured parameters in the way the cytosolic ones are: they depend on
whether the source gives the ion a reservoir, and on the cell-to-ECS volume ratio. The sources are compared on
exactly that.

## 2. Source (a): Hübel and Dahlem 2014 (PLoS Comput Biol 10:e1003941; bib `hubel2014dynamics`)

Read today: PMC JATS (Europe PMC REST, PMC4256015, saved `c310e73063546c11.txt`), the PLoS article HTML
(`295ad5a724018587.html`), the PLoS manuscript XML (`768a5f5f21a59333.txt`); in all three the equations and the
table's symbols are images. So the equations were taken from the authors' own XPPAUT code, ModelDB accession
167714 (the paper: "The simulation code is available from ModelDB, the accession number is 167714"), downloaded
from `https://modeldb.science/download/167714` (zip, 5301 bytes, SHA-256 b9c1effe...; modeldb.science serves no
robots rule against it; unzipped in an empty directory). Its `spreading-depression.ode` (header: "Code for
article by N. Huebel and M. A. Dahlem ... PLoS Comp Biol (2014) ... Oct. 7, 2014") reads, verbatim:

    par vol_i=2.16 / par vol_e=0.72
    nai =  nai0 + ki0 - ki - cli0 + cli
    nae = (nai0 * Vol_i + nae0 * vol_e - nai * vol_i) / vol_e
    cle = (cli0 * Vol_i + cle0 * vol_e - cli * vol_i) / vol_e
    ke  = (ki0  * Vol_i + ke0  * vol_e - ki  * vol_i) / vol_e + dk
    IPUMP  = MAX_PUMP / (1.0 + exp((NA_PUMP - NAI)/3.)) / (1. + exp(K_PUMP - ke)) * z     (MAX_PUMP=6.8, NA_PUMP=25, K_PUMP=5.5)
    par lambda=3.0e-05 / par b0=500 / par K_cr=15. / par k1=5.e-8          (per ms; the file multiplies rates by 1000)
    J_DIFF   = lambda * (k_bath - ke)
    dk_DOT_1 = J_DIFF                                                       (s=1: "diffusive coupling")
    k2       = k1 / (1 + exp((K_cr - ke) / 1.09))
    dk_DOT_0 = -k1 * dk - k2 * ke * (B0 + dk)                               (s=0: "glial buffering")
    par CONV=9.55589e-05 ; ki_DOT = -1. / Vol_i * CONV * I_K ; cli_DOT = 1. / Vol_i * CONV * I_CL_L

Table 1 of the paper ("Parameters for ion-based model"; values read in the PLoS HTML, descriptions the paper's):
"1 µF/cm² | membrane capacitance"; "0.0175 mS/cm² | leak cond." (Na+), "100 mS/cm² | max. gated cond.";
"0.05 mS/cm² | leak cond." (K+), "40 mS/cm² | max. gated cond."; "0.02 mS/cm² | leak cond." (Cl-); initial ICS/ECS
concentrations Na+ 25.23/125.31, K+ 129.26/4, Cl- 9.9/123.27 mM; Nernst potentials 39.74, −92.94, −68 mV;
"2,160 µm³ | ICS volume"; "720 µm³ | ECS volume"; "922 µm² | membrane surface area"; "9.556e–2 | conversion
factor"; "6.8 µA/cm² | max. pump current"; "5e–5/(mM sec) | buffering rate"; "5e–5/sec | backward buffering rate";
"3e–2/sec | diffusive coupling strength"; "4 | conc. of extracell. bath"; "500 | initial buffer conc." The code's
26.64 mV for RT/F puts the model at 309 K (36 °C). **Volume ratio V_i : V_e = 2160 : 720 = 3 : 1** (ECS fraction
0.25 of the modelled tissue). Na+ and Cl- are closed (mass conservation, the `nae`, `cle` lines); K+ alone has a
reservoir, by one of the two schemes.

Prose quoted (PMC text, read 4 and 7 November 2026):
- "We are going to discuss two regulation schemes—coupling to an extracellular bath and glial buffering. They could
  be implemented simultaneously, but for our purpose it will suffice to apply only one scheme at a time."
- "We are using the buffer model from Ref. [Kager et al. 2000] in which the potassium-dependent buffering rate
  [lambda_1] is given as ... The parameter [lambda_1] is normally assumed to have the same numerical value as the
  constant backward buffering rate [lambda_2] which is hence an overall parameter for the buffering strength."
- "Note that the parameters we have chosen are up to almost one order of magnitude lower than intact brain values
  like the ones used in Refs. ... While this does not affect the general time scale separation between glial or
  vascular ion regulation and ion fluxes across the cellular membrane, the duration of SD depends crucially on
  these parameters."
- "Since SD is in particular characterized by an extreme elevation of potassium in the ECS we will only discuss
  potassium regulation." Discussion: "considering only diffusive regulation of potassium is physically
  inconsistent, but adding an analoguous regulation term for sodium turns out not to alter the dynamics
  qualitatively."
- Time scales: the glia scheme "contains a forward buffering process that reduces [K_e] at a time scale ... and a
  backward buffering process with time scale ..." (numbers are images; from k1 = 5e-5/s the backward time constant
  is 2×10⁴ s ≈ 5.6 h; the ModelDB summary reads "the slower backward buffering (minutes to hours)").

**Derivation in Hübel's own model** (`experiments/derive_extracellular_pool_sensitivity.py`, Model B: the ODE file's equations solved for the fixed
point with the HH gated currents at rest, V_m -67.2 mV, then with a sustained inward flux of one ion added to that
ion's current; central differences). Per µA/cm² of the ion's own inward flux:

    scheme                 S_o(Na+)  S_o(K+)   S_o(Cl-)  | S_i(Na+)  S_i(K+)   S_i(Cl-)   (own-ion, 3:1)
    closed (dk = 0)        -0.065    -0.177    -0.264    |  +0.108    +0.0018   +1.10
    glia (s = 0)           -0.065    -0.176    -0.264    |  +0.108    +0.0020   +1.10
    bath (s = 1)           -0.063     0.000    -0.348    |  +0.104    +0.037    +1.44
    glia, V_i:V_e = 4:1    -0.082    -0.171    -0.332    |  +0.102    +0.0015   +1.04

Cross terms in the closed/glia case: an inward Cl- flux moves [K+]o by -0.52 and [Na+]o by -0.24; an inward K+
flux moves [Na+]o by -0.070 and [Cl-]o by -0.077. The glial buffer at rest holds 0.08 mM of K+ (ECS units) and
takes 0.10 mM per mM rise in [K+]o (k2/k1 = 4×10⁻⁵ at 4 mM, K_cr being 15 mM), which is why "glia" equals "closed"
at rest: the buffer is built for the spreading-depression regime, not the resting one. Hübel's cytosolic values
(0.108, 0.0018-0.037, 1.10-1.44) are an independent check of the registered ones (0.0995, 0.0035, 0.833): the same
order of magnitude and ordering from a model with different conductances, pump law and no KCC2.

## 3. Source (b): Kager, Wadman and Somjen 2000 (J Neurophysiol 84:495; bib `kager2000simulated`)

Full text closed on every route today: `https://journals.physiology.org/doi/full/10.1152/jn.2000.84.1.495` is
disallowed by the site's robots file (refused 19:43 UTC); Europe PMC's record (saved `5428466fc1f87281.txt`):
isOpenAccess N, inPMC N, the only "Free" link an abstract page and the DOI "Subscription required"; no PMC version.
The abstract gives the structure: "The neuron was surrounded by an interstitial space where extracellular potassium
and sodium concentration ([K(+)]<sub>o</sub> and [Na(+)]<sub>o</sub>) could rise or fall ... A Na-K exchange pump operated to restore
ion balances. In addition, extracellular potassium concentration, [K(+)]<sub>o</sub>, was also controlled by a 'glial'
uptake function." Hübel and Dahlem 2014 re-implemented it ("the physiologically much more detailed KWS model")
with "The morphological parameters (compartmental volumes and membrane surface area) are the same as for the
reduced model", i.e. 3:1, and took its glial buffer ("the buffer model from Ref. [12]", with K_cr 15 mM and the
1.09 mM slope in the code). So Kager's regulation structure is the glia scheme of section 2 and its steady-state
answer is the same (closed-like for K+, closed for Na+; Kager has Cl- too per the Somjen 2008 abstracts, with
unknown closure). Kager's own interstitial volume fraction, buffer capacity and rates are not read.
**For the owner to supply, if wanted**: the Kager 2000 PDF (and the Somjen, Kager and Wadman 2008 pair, J Comput
Neurosci 25:349 and 26:139, both closed, Europe PMC OA N, which add a glial compartment with its own pump and a
"glia-endothelial 'buffer' system").

## 4. Source (c): further models with an interstitial compartment

### 4.1 Cressman, Ullah, Ziburkus, Schiff and Barreto 2009 (J Comput Neurosci 26:159; PMC2704057) and the
companion Ullah, Cressman, Barreto and Schiff 2009 (26:171; PMC2951284)

Both read today through the PubMed connector (author manuscripts; the parameter table of paper I is not in the
connector's text; beta is stated in paper II). Quotes:
- Paper II: "The factor [beta]=7.0 corrects for the volume fraction between the interior of the cell and the
  extracellular space when calculating the concentration change and is based on [refs]." So **V_i : V_e = 7 : 1**.
- Paper I, glia: "The capacity of glial cells to remove excess potassium from the extracellular space is modeled by
  [I_glia = G_glia/(1 + exp((18 - [K]o)/2.5))] ... This highly simplified model incorporates both passive and
  active uptake into a single sigmoidal response function that depends on the extracellular potassium
  concentration alone. Normal conditions correspond to [G_glia] = 66 mM/s, and [K]o = 4.0 mM." "Two factors allow
  the glia to provide a nearly insatiable buffer for the extracellular space."
- Paper I, diffusion: "The diffusion of potassium away from the local extracellular micro-environment is modeled
  by [I_diff = epsilon([K]o - k_o,inf)] ... Here, [k_o,inf] is the concentration of potassium in the largest nearby
  reservoir. Physiologically, this would correspond to either the bath solution in a slice preparation, or the
  vasculature in the intact brain (noting that [K]o is kept below the plasma level by trans-endothelial
  transport). For normal conditions, we use [k_o,inf] = 4.0. The diffusion constant, obtained from Fick's law, is
  [epsilon = 2D/(Δx)²], where we use [D] = 2.5×10⁻⁶ cm²/s for K+ in water and estimate Δx ≈ 20 μm for intact brain
  reflecting the average distance between capillaries; thus [epsilon] = 1.2 Hz."
- Paper I, sodium and chloride: "we assume that the total amount of sodium is conserved, and hence only one
  differential equation for sodium is needed. Here, 144.0 mM is the sodium concentration outside the cell under
  normal resting conditions for a mammalian neuron." "the chloride concentrations were fixed at [Cl]i = 6.0 mM and
  [Cl]o = 130 mM." Pump: "Normal resting conditions are attained when [rho] = 1.25 mM/s."
- Paper I, on steady state: "If the reservoir concentration [k_o,inf] remains only slightly elevated for a long
  period of time the model cell will ultimately reach a new fixed point in [K]o nearly equal to the bath
  concentration." And its limits: "The two most severe [approximations], insatiable glial buffering and the
  assumption that internal potassium can be calculated using [eq. 3], should hold for times that are long compared
  to the time scale of individual spikes, bursts, and seizures. However, for even longer times (on the order of
  thousands of seconds), the saturation of glia as well as the decoupling of the internal potassium from the
  sodium dynamics will lead to more substantial errors".

Derivation (structural, not a solve of their HH model): K+ has a reservoir route (diffusion at 1.2 Hz plus a pure
sink), so at the steady state of a model that conserves [K+]i, S_o(K+) = 0, in the authors' words "nearly equal to
the bath concentration"; the exchange rate (1.2 Hz, i.e. a 0.8 s time constant, which they derive from a 20 µm
capillary spacing) sets the transient only. Na+ is closed with beta = 7 and no water movement, so
S_o(Na+) = -7 × (18/144) × S_i(Na+) = -0.875 S_i(Na+), about -0.09 per µA/cm² if S_i is the registered 0.0995.
Cl- is fixed by assumption (0). Run in Model A at 7:1 (section 6) the closed Na+ value is only -0.003 to -0.015,
because the water that follows the cytosolic Na+ gain shrinks the ECS and concentrates what is left; Cressman has
no water term. So the Na+ spread between sources is set by the water assumption, not by a measured constant.

### 4.2 Not read

Wei, Ullah and Schiff 2014 (J Neurosci 34:11733, PMC4145176): the PubMed connector returned an empty full text,
www.jneurosci.org answered HTTP 403, Europe PMC's XML service answered HTTP 500 (five tries over 40 minutes, also
for PMC2704057, PMC2322935, PMC2951284, PMC3059345; PMC4256015 succeeded at 19:43 UTC, so the service was failing,
not refusing). Øyehaug et al. 2012 (J Comput Neurosci 32:147, PMID 21667153): closed (Europe PMC OA N, not in
PMC; link.springer.com answered a human check). Somjen, Kager and Wadman 2008 and 2009: closed (above). None of
these changes the structural answer: each gives K+ a reservoir (bath, vasculature or a glial compartment) and
closes Na+ by conservation; Øyehaug's astrocyte has explicit Na+/K+/Cl- transport and would be the one source with
a glial Na+ and Cl- route, which is why it is the first to read if the owner wants a non-zero Na+_o or Cl-_o from
a source rather than from an assumption.

## 5. Source (d): experimental anchors (abstracts, read in PubMed today; Europe PMC records saved)

- Volume fraction. Nicholson and Syková 1998, Trends Neurosci 21:207: "Diffusion measurements with molecules <500
  Mr show that alpha approximately 0.2 and lambda approximately 1.6 ... in severe ischemia alpha = 0.04". So the
  tissue V_i : V_e is about 4 : 1 (all cells, glia included, not neurons alone); the models' 3:1 (Hübel, Kager) and
  7:1 (Cressman) bracket it. Rat and other mammals; review.
- The K+ reservoir is real and fast. Ransom, Ransom and Sontheimer 2000, J Physiol 522:427 (rat optic nerve,
  K+-selective microelectrodes): "Post-stimulus recovery of [K+]o followed a double-exponential time course with an
  initial, fast time constant, tau fast, of 0.9 +/- 0.2 s (mean +/- S.D.) and a later, slow time constant, tau slow,
  of 4.2 +/- 1 s following a 1 s, 100 Hz stimulus"; "The apparent temperature coefficients (Q10, 27-37 degrees C)
  for the fast and slow components ... were 1.7 and 2.6". Larsen et al. 2014, Glia 62:608 (rat hippocampal slices):
  "inhibition of the different isoforms of Na(+)/K(+)-ATPase reduced post-stimulus clearance of K(+) transients"
  and "Kir4.1 and Na(+)/K(+)-ATPase serve temporally distinct roles". Heinemann and Lux 1977, Brain Res 120:231
  (cat cortex): "The maximal values of aK were 10.2 mequiv./1 during stimulation of the cortical surface"; "It is
  suggested that the ceiling in its steady state is maintained by an active K+ uptake mechanism which balances
  extra releases of K+."
- The reservoir clamps the interstitium on long time scales, even against the plasma. Jones and Keep 1987,
  J Physiol 383:441 (rat, K+-selective microelectrodes): "plasma, CSF and ISF [K+] did not vary significantly with
  age, the over-all mean concentrations being 3.8, 3.1 and 3.2 mM respectively"; "1-day-old neonates were able to
  maintain a normal forebrain ISF [K+] during hyperkalaemia."
These do not give S_o directly. They bound the models: the ECS is a fifth to a quarter of tissue volume; K+ leaves
it with time constants of about 1 and 4 s (so the transient a graph edge would carry lasts seconds, the steady
state of a chronic perturbation is reached long before any drug or genotype effect is read); and the steady-state
[K+]o is held by uptake and by the blood-brain barrier, which is the "reservoir" of the models.

## 6. Comparison table

S_o = d ln[ion]_o per µA/cm² of the ion's own sustained inward flux, steady state. Model A is the project's
Düsterwald et al. 2018 constants with a finite ECS added (37 °C; `experiments/derive_extracellular_pool_sensitivity.py`); Model B is Hübel and
Dahlem's own model (36 °C). Cytosolic counterparts in the same run are in brackets; the registered values are
S_Na 0.0995, S_K 0.0035, S_Cl 0.833.

    source / structure                        V_i:V_e   S_o(Na+)          S_o(K+)            S_o(Cl-)
    Düsterwald 2018 as registered (ECS const)   inf     0 (by assumption)  0 (by assumption)  0 (by assumption)
    Model A, K+ bath (Hübel eq.35/Cressman)     3:1     -0.008 [0.091]     0.000 [0.0049]     -0.044 [0.785]
      same                                      4:1     -0.010 [0.089]     0.000 [0.0046]     -0.059 [0.772]
      same                                      7:1     -0.015 [0.085]     0.000 [0.0036]     -0.096 [0.737]
    Model A, closed ECS                         3:1     -0.003 [0.091]     -0.195 [0.0012]    -0.008 [0.305]
      same                                      4:1     -0.003 [0.090]     -0.204 [0.0011]    -0.010 [0.281]
      same                                      7:1     -0.003 [0.089]     -0.217 [0.0009]    -0.016 [0.245]
    Model A, Hübel/Kager glial buffer           3:1     -0.003 [0.091]     -0.192 [0.0012]    -0.009 [0.311]
      same                                      4:1     -0.003 [0.090]     -0.202 [0.0011]    -0.011 [0.286]
    Model B (Hübel), closed or glia             3:1     -0.065 [0.108]     -0.177 [0.0018]    -0.264 [1.10]
    Model B (Hübel), bath                       3:1     -0.063 [0.104]     0.000 [0.037]      -0.348 [1.44]
    Model B (Hübel), glia                       4:1     -0.082 [0.102]     -0.171 [0.0015]    -0.332 [1.04]
    Cressman/Ullah 2009, structural             7:1     -0.875 S_i ≈ -0.09  0 ("nearly equal   0 (fixed)
      (K+ bath + sink; Na+ closed, no water)                              to the bath")
    Physiology (every ion has a BBB/CSF route;  4:1     0                  0                  0
      the pass's reading of (d); see 7)

Range across sources: S_o(Na+) 0 to -0.09; S_o(K+) 0 or -0.17 to -0.22; S_o(Cl-) 0 to -0.35. They agree in order
of magnitude within a structure and disagree between structures, and the structure is the reservoir assumption:
- **K+_o**: every source that gives K+ a reservoir (Hübel bath, Cressman, and the experimental anchors) gives
  exactly 0 at steady state; every closed or glia-at-rest case gives -0.17 to -0.22, which is **50 to 200 times
  the cytosolic S_K** and the largest diagonal term after S_Cl. The two answers differ by the physics, not by
  parameters: the exchange rate (Hübel 0.03/s, Cressman 1.2/s, measured 0.2-1/s) drops out of the steady state.
- **Na+_o**: 0.03 to 0.9 of the cytosolic S_Na, depending on whether water follows (Model A) or not (Model B,
  Cressman) and on the volume ratio; 0 with any Na+ reservoir. Negative sign throughout (the ECS loses what the
  cytosol gains).
- **Cl-_o**: 0.01 to 0.4 of the cytosolic S_Cl; same dependence; 0 with a reservoir.
- Cross terms (not carried by diagonal pool edges in any case): in closed/glia structures an inward Cl- flux moves
  [K+]o by -0.52 to -0.62, more than any own-ion term except S_Cl, and an inward Na+ flux by +0.12 to +0.14.
- In the bath structure the cytosolic values stay within 10 % of the registered ones (Model A 3:1 and 4:1), so a
  finite ECS with a K+ reservoir changes nothing already ruled; in the closed structure S_Cl falls to 0.25-0.31 and
  S_K to 0.001, because E_K floats.

Preparations and species against the registered rodent central neuron at 37 °C: Düsterwald 2018 is the registered
set (37 °C, a model neuron); Hübel 2014 is a generic HH neuron at 36 °C whose concentrations and leaks come from
Kager 2000's rat hippocampal pyramidal cell (MeSH: Rats); Cressman 2009 is a "mammalian neuron" model with 144/4 mM
Na+/K+ and no temperature read; Nicholson and Syková 1998 is mainly rat cortex (review); Jones and Keep 1987 and
Ransom 2000 are rat (Ransom at 37 °C, white matter); Larsen 2014 rat hippocampal slices; Heinemann and Lux 1977
cat cortex. None of the model sources is specific to a neuron type, and none differs from the registered set in a
way that moves the structural answer.

## 7. Recommendation, for the owner to rule on

**Set all three extracellular weights to 0, and state the gap.** Not because the sources could not fix them, but
because, on the definition the cytosolic weights use (steady state of a sustained flux, with the restoring
mechanisms active), every source that gives the extracellular space its physiological exchange route gives 0, and
the experimental anchors say that route exists and is fast (K+: 1 and 4 s time constants; [K+]o held at 3.2 mM
against plasma 3.8 and against hyperkalaemia; ceiling "maintained by an active K+ uptake mechanism"). The non-zero
values are the closed-compartment values, which the models' own authors describe as slice-like or transient
(Hübel: the K+-only regulation is "physically inconsistent"; Cressman: "nearly equal to the bath concentration";
Heinemann and Lux's ceiling is a steady state of uptake, not of accumulation). Under "the version closest to
physiology is used", 0 is the physiological steady-state value, not a numerical convenience; the justification to
record is the reservoir argument of section 1 with the anchors of section 5.

The gap to state with it: (i) the ECS pools carry no transient; on the seconds scale after a perturbation [K+]o
is the most sensitive pool of the six (-0.2 per µA/cm² own-ion, -0.5 to -0.6 from a Cl- flux), and the graph's
steady-state weights do not represent it (Hübel's bath time constant 33 s, Cressman's 0.8 s, Ransom's 0.9 and 4.2
s); (ii) for Na+_o and Cl-_o the 0 rests on the blood-brain-barrier route that the models omit and the anchors
document only for K+ (Jones and Keep; Hübel's remark covers Na+ by analogy, not by data); (iii) the per-reaction
`changes_ion_pool` edges into the extracellular pools would then reach `VM_c` at weight 0, so a perturbation of a
reaction that moves only an extracellular pool (a glial or endothelial transporter, if the neuronal graph holds
any) has no concentration route to `VM_c`, which should be said beside the carrier gap 9.112 already states.

Alternatives, if the owner prefers a derived non-zero value:
- K+_o: a derived value is defensible only for a transient or slice regime: -0.19 (3:1) to -0.22 (7:1), range
  -0.17 to -0.22 across Models A and B; it would make the extracellular K+ edge 50-200 times the cytosolic one and
  is inconsistent with the steady-state definition of the other five weights. Not recommended.
- Na+_o: -0.003 to -0.09, the spread set by the water assumption (not a parameter any source fixes); midpoint of
  the two models that carry the project's volume ratio choice, -0.01 (Model A, bath, 4:1) to -0.08 (Model B,
  4:1). Cl-_o: -0.01 to -0.35 likewise. If chosen, Model A at 4:1 with the K+ bath (-0.010 and -0.059) is the one
  on the registered constants, Nicholson and Syková's alpha 0.2, and the K+ reservoir; it would need the water
  assumption recorded as the open parameter.
- A further reading: Øyehaug et al. 2012 (closed; CellML model public) is the one candidate with explicit glial
  Na+, K+ and Cl- transport, and Kager 2000 (closed) for its own volumes and buffer. Neither is needed for the
  recommendation above; both would be needed to put a sourced non-zero number on Na+_o or Cl-_o.

## 8. BibTeX for papers not already in `docs/references.bib`

Checked: the bib holds `dusterwald2018chloride`, `kager2000simulated`, `hubel2014dynamics`; none of the keys below
(grep for cressman, ullah, nicholson, heinemann, ransom, larsen, jones1987, kofuji: no match). Every field below is
from the PubMed record read today and matched against the Europe PMC record saved today (`a0880dd58216fdf7.txt`,
`308b44f771a0e5e9.txt`). Suggested addition to the existing `hubel2014dynamics` note (not applied): "Read again on
Fable on 7 November 2026 for the extracellular pools of decision 9.112: Table 1 ('2,160 µm3 | ICS volume',
'720 µm3 | ECS volume', '6.8 µA/cm2 | max. pump current', '5e-5/(mM sec) | buffering rate', '5e-5/sec | backward
buffering rate', '3e-2/sec | diffusive coupling strength', '4 | conc. of extracell. bath', '500 | initial buffer
conc.') and the authors' XPPAUT code, ModelDB 167714, for the equations the PMC and PLoS versions hold only as
images."

@article{cressman2009influence,
  author  = {Cressman, John R. and Ullah, Ghanim and Ziburkus, Jokubas and Schiff, Steven J. and Barreto, Ernest},
  title   = {The influence of sodium and potassium dynamics on excitability, seizures, and the stability of persistent states: {I}. {Single} neuron dynamics},
  journal = {Journal of Computational Neuroscience},
  year    = {2009},
  volume  = {26},
  number  = {2},
  pages   = {159--170},
  doi     = {10.1007/s10827-008-0132-4},
  pmid    = {19169801},
  pmcid   = {PMC2704057},
  note    = {FULL TEXT read on Fable on 7 November 2026 through the PubMed connector (PMC author manuscript; its parameter table is not in that text); Europe {PMC} isOpenAccess N, inPMC Y; every field read from the PubMed record and confirmed against Europe {PMC}. Third source for the extracellular pools of decision 9.112: glia as a sigmoidal sink, "Normal conditions correspond to [G\_glia] = 66 mM/s, and [K]o = 4.0 mM", diffusion to a reservoir "either the bath solution in a slice preparation, or the vasculature in the intact brain (noting that [K]o is kept below the plasma level by trans-endothelial transport)" with epsilon = 1.2 Hz from "Δx ≈ 20 μm ... the average distance between capillaries"; sodium closed ("we assume that the total amount of sodium is conserved"), chloride fixed; and on long times "the model cell will ultimately reach a new fixed point in [K]o nearly equal to the bath concentration". The volume ratio beta = 7.0 is stated in the companion paper, ullah2009influence}
}

@article{ullah2009influence,
  author  = {Ullah, Ghanim and Cressman, John R. and Barreto, Ernest and Schiff, Steven J.},
  title   = {The influence of sodium and potassium dynamics on excitability, seizures, and the stability of persistent states. {II}. {Network} and glial dynamics},
  journal = {Journal of Computational Neuroscience},
  year    = {2009},
  volume  = {26},
  number  = {2},
  pages   = {171--183},
  doi     = {10.1007/s10827-008-0130-6},
  pmid    = {19083088},
  pmcid   = {PMC2951284},
  note    = {FULL TEXT read on Fable on 7 November 2026 through the PubMed connector (PMC author manuscript); Europe {PMC} isOpenAccess N, inPMC Y; every field read from the PubMed record and confirmed against Europe {PMC}. Cited in decision 9.112 for the cell-to-interstitium volume ratio of the Cressman model: "The factor [beta]=7.0 corrects for the volume fraction between the interior of the cell and the extracellular space when calculating the concentration change"}
}

@article{nicholson1998extracellular,
  author  = {Nicholson, Charles and Sykov{\'a}, Eva},
  title   = {Extracellular space structure revealed by diffusion analysis},
  journal = {Trends in Neurosciences},
  year    = {1998},
  volume  = {21},
  number  = {5},
  pages   = {207--215},
  doi     = {10.1016/s0166-2236(98)01261-2},
  pmid    = {9610885},
  note    = {Abstract only (not open access; Europe {PMC} isOpenAccess N, checked on Fable 7 November 2026); every field read from the PubMed record and confirmed against Europe {PMC}. Experimental anchor for the extracellular volume fraction in decision 9.112: "Diffusion measurements with molecules <500 Mr show that alpha approximately 0.2 and lambda approximately 1.6 ... in severe ischemia alpha = 0.04". Review. The PubMed record gives the authors' initials only; the first names are as the journal prints them}
}

@article{jones1987control,
  author  = {Jones, H. C. and Keep, R. F.},
  title   = {The control of potassium concentration in the cerebrospinal fluid and brain interstitial fluid of developing rats},
  journal = {The Journal of Physiology},
  year    = {1987},
  volume  = {383},
  pages   = {441--453},
  doi     = {10.1113/jphysiol.1987.sp016419},
  pmid    = {3656129},
  pmcid   = {PMC1183080},
  note    = {Abstract only (the PMC copy is a scan; Europe {PMC} isOpenAccess N, checked on Fable 7 November 2026); every field read from the PubMed record and confirmed against Europe {PMC}. Experimental anchor in decision 9.112 for the reservoir that clamps the interstitial potassium at steady state: "plasma, CSF and ISF [K+] did not vary significantly with age, the over-all mean concentrations being 3.8, 3.1 and 3.2 mM respectively" and "1-day-old neonates were able to maintain a normal forebrain ISF [K+] during hyperkalaemia" (rat, K+-selective microelectrodes)}
}

@article{heinemann1977ceiling,
  author  = {Heinemann, U. and Lux, H. D.},
  title   = {Ceiling of stimulus induced rises in extracellular potassium concentration in the cerebral cortex of cat},
  journal = {Brain Research},
  year    = {1977},
  volume  = {120},
  number  = {2},
  pages   = {231--249},
  doi     = {10.1016/0006-8993(77)90903-9},
  pmid    = {832122},
  note    = {Abstract only (not open access; Europe {PMC} isOpenAccess N, checked on Fable 7 November 2026); every field read from the PubMed record and confirmed against Europe {PMC}. Experimental anchor in decision 9.112: "The maximal values of aK were 10.2 mequiv./1 during stimulation of the cortical surface" and "It is suggested that the ceiling in its steady state is maintained by an active K+ uptake mechanism which balances extra releases of K+" (cat somatosensory cortex, ion-sensitive microelectrodes)}
}

@article{ransom2000activity,
  author  = {Ransom, C. B. and Ransom, B. R. and Sontheimer, H.},
  title   = {Activity-dependent extracellular {K+} accumulation in rat optic nerve: the role of glial and axonal {Na+} pumps},
  journal = {The Journal of Physiology},
  year    = {2000},
  volume  = {522},
  number  = {Pt 3},
  pages   = {427--442},
  doi     = {10.1111/j.1469-7793.2000.00427.x},
  pmid    = {10713967},
  pmcid   = {PMC2269766},
  note    = {Abstract only (Europe {PMC} isOpenAccess N, checked on Fable 7 November 2026); every field read from the PubMed record and confirmed against Europe {PMC}. Experimental anchor in decision 9.112 for the time constants of extracellular K+ clearance: "Post-stimulus recovery of [K+]o followed a double-exponential time course with an initial, fast time constant, tau fast, of 0.9 +/- 0.2 s (mean +/- S.D.) and a later, slow time constant, tau slow, of 4.2 +/- 1 s following a 1 s, 100 Hz stimulus"; "The apparent temperature coefficients (Q10, 27-37 degrees C) for the fast and slow components ... were 1.7 and 2.6" (adult rat optic nerve, a white-matter tract)}
}

@article{larsen2014contributions,
  author  = {Larsen, Brian Roland and Assentoft, Mette and Cotrina, Maria L. and Hua, Susan Z. and Nedergaard, Maiken and Kaila, Kai and Voipio, Juha and MacAulay, Nanna},
  title   = {Contributions of the {Na+/K+-ATPase}, {NKCC1}, and {Kir4.1} to hippocampal {K+} clearance and volume responses},
  journal = {Glia},
  year    = {2014},
  volume  = {62},
  number  = {4},
  pages   = {608--622},
  doi     = {10.1002/glia.22629},
  pmid    = {24482245},
  pmcid   = {PMC4302754},
  note    = {Abstract only (Europe {PMC} isOpenAccess N, checked on Fable 7 November 2026); every field read from the PubMed record and confirmed against Europe {PMC}. Experimental anchor in decision 9.112 for the mechanism of the extracellular K+ reservoir route: "inhibition of the different isoforms of Na(+)/K(+)-ATPase reduced post-stimulus clearance of K(+) transients" and "Kir4.1 and Na(+)/K(+)-ATPase serve temporally distinct roles" (rat hippocampal slices)}
}

## 9. Refusals, closed full texts, text addressed to an AI, provenance

- Text addressed to an AI: every PubMed connector result carries an "Important Legal Requirement" block
  instructing the reader how to attribute; reported, not acted on (the citations above follow the repository's
  convention). No Consensus call was made.
- Refusals respected: journals.physiology.org (robots file; Kager 2000); pmc.ncbi.nlm.nih.gov/articles/ (human
  check; Cressman); www.jneurosci.org (HTTP 403; Wei 2014); europepmc.org/articles/ and europepmc.org/api/
  (robots file); link.springer.com (human check; Cressman). Service error, not refusal: Europe PMC REST
  fullTextXML answered HTTP 500 for PMC2704057, PMC4145176, PMC2322935, PMC2951284, PMC3059345 (19:46-20:00 UTC),
  while PMC4256015 succeeded (19:43).
- Closed full texts for the owner to supply if wanted: Kager, Wadman and Somjen 2000; Somjen, Kager and Wadman
  2008 (J Comput Neurosci 25:349) and 2009 (26:139); Øyehaug et al. 2012 (32:147). Not needed for the
  recommendation; needed for a sourced non-zero Na+_o or Cl-_o.
- No fetch-tool permission request was raised; nothing was withdrawn for that reason.
- Saved pages (SHA-256 prefix, all `data/raw/public_pages/`): c310e73063546c11 (Hübel PMC JATS),
  295ad5a724018587 (Hübel PLoS HTML), 768a5f5f21a59333 (Hübel PLoS manuscript XML), e37090ba6436738c (ModelDB
  167714 page), b9c1effeee47e05f (ModelDB 167714 zip), a2a047308f6a3762 (ModelDB 113446 record, Somjen 2008, not
  Cressman), 5428466fc1f87281 (Europe PMC record of Kager 2000), a0880dd58216fdf7 and 308b44f771a0e5e9 (Europe
  PMC records of the papers cited).
- Model: Fable throughout.

---

## Added 7 November 2026: the owner's ruling

Committed as a record the same day, unchanged except for the model lines and the names of the derivation scripts,
now committed as `experiments/derive_extracellular_pool_sensitivity.py` and, for the cytosolic weights of 4 November,
`experiments/derive_pump_leak_pool_sensitivity.py`. Asked whether the brain acts as an open or a closed space, the
session answered that it depends on the timescale: open, held to a regulated set point, at steady state; close to
closed over milliseconds to seconds. The owner then asked whether this should depend on reading at several points
(decision 9.118), and ruled, on the session's proposal ("Commit the pass and record it that way"): **the extracellular
pools take weight 0 from neuronal currents at the registered steady-state readout; the closed-space values of section
6 and the clearance time constants of section 5 are kept for 9.118, so that an earlier reading, if 9.118 adds one, has
its transient weights; and the extracellular pools are kept as inputs that perturbations of the clearance system can
move.** The three gaps of section 7 are stated with the build. Recorded in decision 9.112 and in
`docs/membrane_potential_constants.md`; exploration queue item 11 names the clearance as a timescale any multi-reading
design must carry.
