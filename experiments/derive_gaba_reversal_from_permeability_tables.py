"""Committed 7 November 2026 (decision 9.112; docs/anion_permeability_pdfs_2026-11-07.md). Run: python experiments/derive_gaba_reversal_from_permeability_tables.py

E_GABA and E_Gly at the registered constants, with the two PDFs' measured P_HCO3/P_Cl.

Extends experiments/derive_gaba_reversal_with_bicarbonate.py (the pass of 7 November 2026) with the ratios read on 7 November 2026 in the
owner's two supplied PDFs instead of the second-hand values:
  Bormann, Hamill & Sakmann 1987, J Physiol 385:243-286, Table 2 (page 258):
    GABA (GABAR)  P_HCO3/P_Cl = 0.18, from E_rev -40 +/- 2 mV (s.d.)
    glycine (GlyR) P_HCO3/P_Cl = 0.11, from E_rev -49 +/- 2 mV (s.d.)
    No error is printed on the ratio itself and no n is given, so the error below is this pass's
    propagation of the +/- 2 mV through the paper's own eqn. (1) in its own conditions.
  Fatima-Shad & Barry 1993, Proc R Soc Lond B 253:69-75, Table 1 (page 71):
    GABA   P_HCO3/P_Cl = 0.44 +/- 0.02 (s.e.m., n = 15)
    glycine P_HCO3/P_Cl = 0.4  +/- 0.02 (s.e.m., n = 15)

Registered constants (docs/membrane_potential_constants.md, set A, Duesterwald et al. 2018):
  RT/F 26.73 mV at 310.15 K; [Cl-] 119 out / 5.2 in mM; V_rest -72.6 mV;
  leak g 20 (Na+) / 70 (K+) / 20 (Cl-) uS/cm2, g_total 110; ruled Cl- term 2.0 mV.
Sourced bicarbonate (the pass of 7 November 2026): [HCO3-]o 23.5-26 mM;
  [HCO3-]i = [HCO3-]o * 10^(pH_i - pH_o), pH_i - pH_o from -0.14 to -0.33.
"""
import math

RT_F = 26.73             # mV, registered, 310.15 K
CL_O, CL_I = 119.0, 5.2  # mM, registered
V_REST = -72.6           # mV, registered
G_CL, G_HCO3, G_TOTAL = 20.0, 4.0, 110.0  # uS/cm2; g_HCO3 from Selfe et al. 2024 Table 1


def e_rev_ghk(r, hco3_i, hco3_o):
    """GHK voltage equation over Cl- and HCO3-, both z = -1, divided through by P_Cl."""
    return RT_F * math.log((CL_I + r * hco3_i) / (CL_O + r * hco3_o))


def current_shares(r, hco3_i, hco3_o, v):
    """Share of the pore's current each anion carries at v, by the GHK current equation."""
    u = -v / RT_F
    k = u / (1.0 - math.exp(-u))
    f_cl = k * (CL_O - CL_I * math.exp(-u))
    f_hco3 = r * k * (hco3_o - hco3_i * math.exp(-u))
    t = abs(f_cl) + abs(f_hco3)
    return abs(f_cl) / t, abs(f_hco3) / t


def w_single(e):
    return G_CL * abs(e - V_REST) / G_TOTAL


def w_mixed(r, hi, ho, e):
    f_cl, f_h = current_shares(r, hi, ho, V_REST)
    return (f_cl * G_CL + f_h * G_HCO3) * abs(e - V_REST) / G_TOTAL, f_cl, f_h


# ---- Bormann's ratio error, propagated here from his +/- 2 mV (his eqn. 1, his conditions) ----
# Bi-ionic: outside 145 mM-Cl- (activity 110 mM, his Methods); inside 140 mM test anion + 4 mM Cl-
# (activities 0.75 and 0.76 of those, his Methods, "not much different from 0.75 (within +/- 3%)").
# His eqn. (1): V_0 = -(RT/F) ln( ([Cl]o + r [A]o) / ([Cl]i + r [A]i) ), [A]o = 0.
# => [Cl]i + r [A]i = [Cl]o exp(V_0 / (RT/F)); dr = ([Cl]i + r[A]i) / ([A]i (RT/F)) dV_0.
RT_F_22 = 25.43          # mV at 22 C, the midpoint of his stated 20-23 C
A_I, CL_I_B, CL_O_B = 140 * 0.75, 4 * 0.76, 110.0
print("== Bormann et al. 1987 Table 2: the ratio reconstructed from his E_rev, and its error ==")
BORMANN = {}
for name, v0, printed in (("GABA (GABAR)", -40.0, 0.18), ("glycine (GlyR)", -49.0, 0.11)):
    r = (CL_O_B * math.exp(v0 / RT_F_22) - CL_I_B) / A_I
    dr = (CL_I_B + r * A_I) / (A_I * RT_F_22) * 2.0
    BORMANN[name] = (printed, dr)
    print(f"  {name:>15}: E_rev {v0:+.0f} +/- 2 mV (s.d.) -> r = {r:.3f} "
          f"(the paper prints {printed}); +/- 2 mV propagates to +/- {dr:.3f}")
print()

FS = {"GABA (GABAR)": (0.44, 0.02), "glycine (GlyR)": (0.4, 0.02)}

DPH = [(-0.14, "Nardini & Siesjo 1969 pH_i 7.10 with Kintner et al. 1999 pH_e 7.24"),
       (-0.19, "Kintner et al. 1999, rat in vivo, same animals (7.05 / 7.24)"),
       (-0.20, "the modelling convention (7.2 / 7.4)"),
       (-0.24, "Boffi et al. 2018 pH_i with Arnold et al. 1986 pH_e"),
       (-0.33, "Korzowski et al. 2020, human in vivo, same voxels (7.00 / 7.33)")]
HCO3_O = [23.5, 24.0, 26.0]

E_CL = RT_F * math.log(CL_I / CL_O)
print(f"Registered check: E_Cl = {E_CL:.2f} mV, E_Cl - V_rest = {E_CL - V_REST:+.2f} mV, "
      f"ruled Cl- term = {w_single(E_CL):.2f} mV")
print()

SETS = [("Bormann et al. 1987", "GABA (GABAR)", BORMANN["GABA (GABAR)"][0], BORMANN["GABA (GABAR)"][1]),
        ("Bormann et al. 1987", "glycine (GlyR)", BORMANN["glycine (GlyR)"][0], BORMANN["glycine (GlyR)"][1]),
        ("Fatima-Shad & Barry 1993", "GABA (GABAR)", FS["GABA (GABAR)"][0], FS["GABA (GABAR)"][1]),
        ("Fatima-Shad & Barry 1993", "glycine (GlyR)", FS["glycine (GlyR)"][0], FS["glycine (GlyR)"][1])]

print("== E_rev - V_rest (mV) over the sourced bicarbonate range, per paper and receptor ==")
print("   (ratio swept over r +/- its error; + means depolarising at rest)")
print(f"{'paper':<26}{'receptor':<16}{'r':>14} | {'E-V min':>8}{'E-V max':>9}  {'sign':<16}"
      f"{'weight min':>11}{'weight max':>11}")
summary = {}
for paper, rec, r0, dr in SETS:
    vals, wts, wms = [], [], []
    for r in (r0 - dr, r0, r0 + dr):
        for d, _ in DPH:
            for ho in HCO3_O:
                hi = ho * 10 ** d
                e = e_rev_ghk(r, hi, ho)
                vals.append(e - V_REST)
                wts.append(w_single(e))
                wms.append(w_mixed(r, hi, ho, e)[0])
    lo, hi_ = min(vals), max(vals)
    sign = ("hyperpolarising" if hi_ < 0 else "depolarising" if lo > 0 else "MIXED")
    summary[(paper, rec)] = (r0, dr, lo, hi_, sign, min(wts), max(wts), min(wms), max(wms))
    print(f"{paper:<26}{rec:<16}{r0:.2f} +/- {dr:.2f} | {lo:+8.2f}{hi_:+9.2f}  {sign:<16}"
          f"{min(wts):11.2f}{max(wts):11.2f}")
print()

print("== the central case: pH difference -0.19, [HCO3-]o 23.5 mM (Kintner et al. 1999, same animals) ==")
ho = 23.5
hi = ho * 10 ** -0.19
print(f"   [HCO3-]i = {hi:.1f} mM; E_HCO3 = {RT_F * math.log(hi / ho):+.2f} mV")
print(f"{'paper':<26}{'receptor':<16}{'r':>6} {'E_rev':>8} {'E-V':>8} {'w_single':>9} {'w_mixed':>8} "
      f"{'f_Cl':>6} {'f_HCO3':>7}")
for paper, rec, r0, dr in SETS:
    e = e_rev_ghk(r0, hi, ho)
    wm, f_cl, f_h = w_mixed(r0, hi, ho, e)
    print(f"{paper:<26}{rec:<16}{r0:6.2f} {e:+8.2f} {e - V_REST:+8.2f} {w_single(e):9.2f} {wm:8.2f} "
          f"{f_cl:6.3f} {f_h:7.3f}")
print()

print("== E_rev - V_rest across the whole sourced pH and [HCO3-]o grid, at each paper's central r ==")
for paper, rec, r0, dr in SETS:
    print(f"  {paper}, {rec}, r = {r0}")
    print(f"    {'dpH':>6} {'[HCO3]i':>8} |" + "".join(f"{ho:>9.1f}" for ho in HCO3_O))
    for d, _ in DPH:
        cells = []
        for ho in HCO3_O:
            h_i = ho * 10 ** d
            cells.append(e_rev_ghk(r0, h_i, ho) - V_REST)
        print(f"    {d:+6.2f} {24.0 * 10 ** d:8.1f} |" + "".join(f"{c:+9.2f}" for c in cells))
print()

print("== the question the threshold asks: are BOTH papers at or below 0.20, or BOTH at or above 0.33? ==")
for rec in ("GABA (GABAR)", "glycine (GlyR)"):
    rs = [(p, summary[(p, rec)][0]) for p in ("Bormann et al. 1987", "Fatima-Shad & Barry 1993")]
    print(f"  {rec}: " + ", ".join(f"{p.split()[0]} {r}" for p, r in rs)
          + ("  -> BOTH <= 0.20" if all(r <= 0.20 for _, r in rs)
             else "  -> BOTH >= 0.33" if all(r >= 0.33 for _, r in rs)
             else "  -> THEY STRADDLE THE THRESHOLD: neither branch fires"))
print()
print("== union over both papers, both receptors, the whole sourced sweep ==")
alllo = min(summary[k][2] for k in summary)
allhi = max(summary[k][3] for k in summary)
print(f"  E_rev - V_rest runs {alllo:+.2f} to {allhi:+.2f} mV; "
      f"{'MIXED SIGN' if alllo < 0 < allhi else 'one sign'}")
print(f"  single-ion weight {min(summary[k][5] for k in summary):.2f} to "
      f"{max(summary[k][6] for k in summary):.2f} mV; mixed-pore weight "
      f"{min(summary[k][7] for k in summary):.2f} to {max(summary[k][8] for k in summary):.2f} mV; "
      f"the ruled Cl- term is {w_single(E_CL):.2f} mV")
