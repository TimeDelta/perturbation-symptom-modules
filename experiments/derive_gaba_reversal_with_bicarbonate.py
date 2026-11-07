"""Committed 7 November 2026 (decision 9.112; docs/bicarbonate_gaba_2026-11-07.md). Run: python experiments/derive_gaba_reversal_with_bicarbonate.py

E_GABA and E_Gly by the GHK voltage equation at the registered constants of decision 9.112.

Registered (docs/membrane_potential_constants.md, set A, Duesterwald et al. 2018):
  RT/F 26.73 mV at 310.15 K; [Cl-] 119 out / 5.2 in mM; V_rest -72.6 mV;
  leak g 20 (Na+) / 70 (K+) / 20 (Cl-) uS/cm2, g_total 110; ruled Cl- term 2.0 mV.
Bicarbonate, sourced by the pass of 7 November 2026 (not registered):
  [HCO3-]_o 23.5-26 mM (Kintner et al. 1999 CSF 23.5; Boyarsky et al. 1993 bath 25;
  Raimondo et al. 2015 and Lombardi et al. 2019 24; Selfe et al. 2024 aCSF 23);
  [HCO3-]_i = [HCO3-]_o * 10^(pH_i - pH_o), with pH_i - pH_o from -0.14 to -0.33.
  g_HCO3 4 uS/cm2 (Selfe et al. 2024 Table 1, extending Duesterwald et al. 2018).
"""
import math
import itertools

RT_F = 26.73           # mV, registered
CL_O, CL_I = 119.0, 5.2  # mM, registered
V_REST = -72.6         # mV, registered
G_CL = 20.0            # uS/cm2, registered
G_HCO3 = 4.0           # uS/cm2, Selfe et al. 2024 Table 1
G_TOTAL = 110.0        # uS/cm2, registered (Na+ 20 + K+ 70 + Cl- 20)


def e_anion(c_in, c_out):
    """Nernst potential of a monovalent anion (z = -1)."""
    return RT_F * math.log(c_in / c_out)


def e_rev_ghk(ratio, hco3_i, hco3_o):
    """GHK voltage equation over Cl- and HCO3-, both z = -1.

    E = (RT/F) ln( (P_Cl [Cl]i + P_HCO3 [HCO3]i) / (P_Cl [Cl]o + P_HCO3 [HCO3]o) ),
    divided through by P_Cl so only ratio = P_HCO3/P_Cl enters.
    """
    num = CL_I + ratio * hco3_i
    den = CL_O + ratio * hco3_o
    return RT_F * math.log(num / den)


def current_shares(ratio, hco3_i, hco3_o, v):
    """Share of the pore's current carried by each anion at potential v, by the GHK current equation.

    For an anion (z = -1) the GHK flux is proportional to
      P * u * ([X]o - [X]i exp(-u)) / (1 - exp(-u)),  u = -vF/RT = -v/(RT/F),
    and only the ratio of the two terms is needed, so the common factors cancel.
    """
    u = -v / RT_F
    if abs(u) < 1e-9:
        f_cl = 1.0 * (CL_O - CL_I)
        f_hco3 = ratio * (hco3_o - hco3_i)
    else:
        k = u / (1.0 - math.exp(-u))
        f_cl = 1.0 * k * (CL_O - CL_I * math.exp(-u))
        f_hco3 = ratio * k * (hco3_o - hco3_i * math.exp(-u))
    total = abs(f_cl) + abs(f_hco3)
    return abs(f_cl) / total, abs(f_hco3) / total


def weight_single_ion(e_rev):
    """The ruled single-ion weight, using the chloride leak conductance for the pore."""
    return G_CL * abs(e_rev - V_REST) / G_TOTAL


def weight_mixed(ratio, hco3_i, hco3_o, e_rev):
    """The ruled mixed-pore weight, (sum_j f_j g_j) |E_rev - V_rest| / g_total."""
    f_cl, f_hco3 = current_shares(ratio, hco3_i, hco3_o, V_REST)
    g_chord = f_cl * G_CL + f_hco3 * G_HCO3
    return g_chord * abs(e_rev - V_REST) / G_TOTAL, f_cl, f_hco3


E_CL = e_anion(CL_I, CL_O)
print(f"Registered check: E_Cl = {E_CL:.2f} mV; E_Cl - V_rest = {E_CL - V_REST:+.2f} mV; "
      f"ruled Cl- weight = {weight_single_ion(E_CL):.2f} mV")
print()

RATIOS = [0.18, 0.20, 0.25, 0.33, 0.42, 0.44]
DPH = [(-0.14, "Nardini & Siesjo 1969 pH_i 7.10 with Kintner et al. 1999 pH_e 7.24"),
       (-0.19, "Kintner et al. 1999, rat in vivo, same animals (7.05 / 7.24)"),
       (-0.20, "Raimondo 2015 / Lombardi 2019 / Selfe 2024 convention (7.2 / 7.4)"),
       (-0.24, "Boffi et al. 2018 pH_i 7.1 with Arnold et al. 1986 pH_e 7.34"),
       (-0.33, "Korzowski et al. 2020, human in vivo, same voxels (7.00 / 7.33)")]
HCO3_O = [23.5, 24.0, 26.0]

print("== E_HCO3, which depends only on the pH difference ==")
for d, label in DPH:
    print(f"  dpH {d:+.2f}  E_HCO3 = {2.302585 * RT_F * d:+6.2f} mV   ({label})")
print()

print("== E_GABA at [HCO3-]o 24 mM, across the sourced ratio and pH ranges ==")
print(f"{'dpH':>6} {'[HCO3]i':>8} | " + " ".join(f"r={r:<5.2f}" for r in RATIOS))
rows = []
for d, _ in DPH:
    hi = 24.0 * 10 ** d
    cells = []
    for r in RATIOS:
        e = e_rev_ghk(r, hi, 24.0)
        cells.append(e)
        rows.append((d, 24.0, r, e))
    print(f"{d:+6.2f} {hi:8.1f} | " + " ".join(f"{e:+7.2f}" for e in cells))
print()

print("== E_GABA - V_rest (mV), same grid; + means depolarising at rest ==")
print(f"{'dPH':>6} {'[HCO3]i':>8} | " + " ".join(f"r={r:<5.2f}" for r in RATIOS))
for d, _ in DPH:
    hi = 24.0 * 10 ** d
    print(f"{d:+6.2f} {hi:8.1f} | " + " ".join(
        f"{e_rev_ghk(r, hi, 24.0) - V_REST:+7.2f}" for r in RATIOS))
print()

print("== full sweep over [HCO3-]o too: extremes of E_GABA - V_rest ==")
allv = []
for d, _ in DPH:
    for ho in HCO3_O:
        hi = ho * 10 ** d
        for r in RATIOS:
            allv.append((e_rev_ghk(r, hi, ho) - V_REST, d, ho, round(hi, 1), r))
allv.sort()
print(f"  most negative: {allv[0][0]:+.2f} mV at dpH {allv[0][1]:+.2f}, "
      f"[HCO3]o {allv[0][2]}, [HCO3]i {allv[0][3]}, r {allv[0][4]}")
print(f"  most positive: {allv[-1][0]:+.2f} mV at dpH {allv[-1][1]:+.2f}, "
      f"[HCO3]o {allv[-1][2]}, [HCO3]i {allv[-1][3]}, r {allv[-1][4]}")
print(f"  sign: {'all positive (depolarising)' if allv[0][0] > 0 else 'MIXED'}; "
      f"n = {len(allv)} combinations")
print()

print("== weights, at the central case dpH -0.19, [HCO3]o 24 mM ==")
hi = 24.0 * 10 ** -0.19
for r in RATIOS:
    e = e_rev_ghk(r, hi, 24.0)
    w1 = weight_single_ion(e)
    wm, f_cl, f_hco3 = weight_mixed(r, hi, 24.0, e)
    print(f"  r={r:<5.2f} E_GABA {e:+7.2f} mV, E-V {e - V_REST:+6.2f} mV, "
          f"single-ion weight {w1:5.2f} mV, mixed weight {wm:5.2f} mV "
          f"(f_Cl {f_cl:.3f}, f_HCO3 {f_hco3:.3f})")
print()

print("== weight range over the whole sourced sweep ==")
ws = []
for d, _ in DPH:
    for ho in HCO3_O:
        hi = ho * 10 ** d
        for r in RATIOS:
            e = e_rev_ghk(r, hi, ho)
            wm, _, _ = weight_mixed(r, hi, ho, e)
            ws.append((weight_single_ion(e), wm, d, ho, r))
ws.sort()
print(f"  single-ion weight: {ws[0][0]:.2f} to {ws[-1][0]:.2f} mV")
wm_sorted = sorted(w[1] for w in ws)
print(f"  mixed weight:      {wm_sorted[0]:.2f} to {wm_sorted[-1]:.2f} mV")
print(f"  (the ruled Cl--only term is {weight_single_ion(E_CL):.2f} mV)")
