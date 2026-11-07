"""Committed 7 November 2026 (decision 9.112): the derivation behind the registered cytosolic pool weights
S_Na 0.0995, S_K 0.0035 and S_Cl 0.833, written by the review pass of 4 November 2026 and kept until then only in that
session's working directory. Run: python experiments/derive_pump_leak_pool_sensitivity.py

Steady-state linear response of the Düsterwald et al. 2018 single-compartment pump-leak model (eLife 7:e39575,
equations 1-7 and Table 1, read from data/raw/public_pages/ef075a40f518bb46.html on 4 November 2026).

State x = ([Na]i, [K]i, [Cl]i, w, Vm). Extracellular concentrations constant (the paper's assumption). Impermeant
anion moles N_X = [X]i * w fixed, charge z fixed. Steady state:
  Na:  g_Na (V - E_Na) + 3 J_p                 = F * phi_Na      (phi = sustained inward molar flux density, mol/(dm2 s))
  K:   g_K  (V - E_K)  - 2 J_p - J_KCC2        = F * phi_K
  Cl:  g_Cl (V - E_Cl) + J_KCC2 + F * phi_Cl   = 0               (inward anion flux raises [Cl]i)
  osmotic: [Na]+[K]+[Cl]+[X] = Pi_o
  charge:  F([Na]+[K]-[Cl]+z[X]) = Cm Am V     (the paper's equation 1; Am = surface/volume of the cylinder)
with J_p = P ([Na]i/[Na]o)^3, J_KCC2 = g_KCC2 (E_K - E_Cl), I = g (V - E) ohmic.
Units: dm, dm3 = L, mol/L, S/dm2, A/dm2 (1 uS/cm2 = 1e-4 S/dm2; P = 0.1 C/(dm2 s) = 0.1 A/dm2).
"""
import numpy as np
from scipy.optimize import fsolve

F = 96485.33; R = 8.31446; T = 310.15; RT_F = R * T / F           # V
uS_cm2 = 1e-4                                                      # S/dm2
g = {"Na": 20 * uS_cm2, "K": 70 * uS_cm2, "Cl": 20 * uS_cm2}
g_KCC2 = 20 * uS_cm2
P = 0.1                                                            # A/dm2
Cm = 2e-6 * 100                                                    # F/dm2  (2e-6 F/cm2)
out = {"Na": 145e-3, "K": 3.5e-3, "Cl": 119e-3, "X": 29.5e-3}      # mol/L
z = -0.85
Pi_o = sum(out.values())
radius = 5e-5                                                      # dm (5 um)
length = 25e-5                                                     # dm
w0 = np.pi * radius ** 2 * length                                  # dm3; the paper quotes 2.0 pL
N_X = 154.9e-3 * w0                                                # mol of impermeant anion


def nernst(zi, co, ci):
    return RT_F / zi * np.log(co / ci)


def residuals(xs_, p):
    Na, K, Cl, w, V = xs_[0] * 1e-3, xs_[1] * 1e-3, xs_[2] * 1e-3, xs_[3] * 1e-12, xs_[4] * 1e-3
    gNa, gK, gCl, gK2, Pp, phiNa, phiK, phiCl = p
    X = N_X / w
    r = np.sqrt(w / (np.pi * length))                              # radius at this volume
    Am = 2.0 / r                                                   # surface/volume of a cylinder, 1/dm
    ENa, EK, ECl = nernst(1, out["Na"], Na), nernst(1, out["K"], K), nernst(-1, out["Cl"], Cl)
    Jp = Pp * (Na / out["Na"]) ** 3
    JK2 = gK2 * (EK - ECl)
    return [(gNa * (V - ENa) + 3 * Jp - F * phiNa) * 1e4,
            (gK * (V - EK) - 2 * Jp - JK2 - F * phiK) * 1e4,
            (gCl * (V - ECl) + JK2 + F * phiCl) * 1e4,
            (Na + K + Cl + X - Pi_o) * 1e3,
            (F * (Na + K - Cl + z * X) - Cm * Am * V) * 1e-2]


p0 = np.array([g["Na"], g["K"], g["Cl"], g_KCC2, P, 0.0, 0.0, 0.0])
x0 = np.array([14.0, 122.9, 5.2, w0 * 1e12, -72.6])
SCALE = np.array([1e-3, 1e-3, 1e-3, 1e-12, 1e-3])


def solve(p, guess=x0):
    x, info, ok, msg = fsolve(residuals, guess / SCALE, args=(p,), xtol=1e-13, full_output=True)
    assert ok == 1, msg
    assert max(abs(v) for v in residuals(x, p)) < 1e-9, residuals(x, p)
    return x * SCALE


xs = solve(p0, x0 * SCALE)
Na, K, Cl, w, V = xs
print("steady state: [Na]i %.2f mM  [K]i %.2f mM  [Cl]i %.2f mM  w %.3f pL  Vm %.2f mV" % (Na * 1e3, K * 1e3, Cl * 1e3, w * 1e12, V * 1e3))
ENa, EK, ECl = nernst(1, out["Na"], Na), nernst(1, out["K"], K), nernst(-1, out["Cl"], Cl)
print("  E_Na %.1f  E_K %.1f  E_Cl %.1f mV; V - E_Cl = %.1f mV" % (ENa * 1e3, EK * 1e3, ECl * 1e3, (V - ECl) * 1e3))
gtot = g["Na"] + g["K"] + g["Cl"]
Jp = P * (Na / out["Na"]) ** 3
print("  J_p %.3e A/dm2 = %.2f uA/cm2; J_p/g_tot = %.1f mV; g_tot = %.0f uS/cm2" % (Jp, Jp * 1e6 / 100, (Jp / gtot) * 1e3, gtot / uS_cm2))

# Millman (fixed concentrations) coefficients: dV per unit fractional change of each cytosolic pool
c = {ion: -(g[ion] / gtot) * RT_F / zi for ion, zi in (("Na", 1), ("K", 1), ("Cl", -1))}   # V per unit d ln[ion]i
print("\nMillman coefficients dV/dln[ion]i (mV): " + ", ".join("%s %.2f" % (k, v * 1e3) for k, v in c.items()))


def response(index, delta):
    """d(state)/d(parameter index) by central difference."""
    pp, pm = p0.copy(), p0.copy()
    pp[index] += delta; pm[index] -= delta
    return (solve(pp, xs) - solve(pm, xs)) / (2 * delta)


names = ["gNa", "gK", "gCl", "gKCC2", "P", "phiNa", "phiK", "phiCl"]
print("\n== Response to a sustained inward molar flux of one ion (per 1 uA/cm2 of inward current of that ion) ==")
print("1/g_tot (fixed-concentration Thevenin) = %.2f mV per uA/cm2" % ((1e-6 * 100 / gtot) * 1e3))
unit_I = 1e-6 * 100                                                 # 1 uA/cm2 in A/dm2
rows = {}
for ion, idx in (("Na", 5), ("K", 6), ("Cl", 7)):
    d = response(idx, 1e-12)                                        # per mol/(dm2 s)
    d = d * (unit_I / F)                                            # per 1 uA/cm2 of that ion's flux (as molar flux)
    dNa, dK, dCl, dw, dV = d
    conc = c["Na"] * dNa / Na + c["K"] * dK / K + c["Cl"] * dCl / Cl
    dJp = 3 * Jp * dNa / Na
    rows[ion] = d
    print("%-3s: dV_ss = %+.3f mV | d ln[Na]i %+.4f  d ln[K]i %+.4f  d ln[Cl]i %+.4f  d ln w %+.4f | Millman conc. route %+.3f mV, pump-current route %+.3f mV, Thevenin %+.3f mV"
          % (ion, dV * 1e3, dNa / Na, dK / K, dCl / Cl, dw / w, conc * 1e3, -(dJp / gtot) * 1e3, (unit_I / gtot) * 1e3))

print("\n== Response to a sustained conductance change (per 1 uS/cm2 added), exact vs the pair ==")
for ion, idx, E in (("Na", 0, ENa), ("K", 1, EK), ("Cl", 2, ECl)):
    d = response(idx, 1e-9) * uS_cm2
    dNa, dK, dCl, dw, dV = d
    acute = (E - V) / gtot * uS_cm2
    conc = c["Na"] * dNa / Na + c["K"] * dK / K + c["Cl"] * dCl / Cl
    dJp = 3 * Jp * dNa / Na
    print("g%-2s: exact dV_ss %+.3f mV | acute (E-V)/g_tot %+.3f mV | Millman conc. route %+.3f | pump-current route %+.3f | sum of three %+.3f | d ln[Na]i %+.4f d ln[K]i %+.4f d ln[Cl]i %+.4f d ln w %+.4f"
          % (ion, dV * 1e3, acute * 1e3, conc * 1e3, -(dJp / gtot) * 1e3, (acute + conc - dJp / gtot) * 1e3, dNa / Na, dK / K, dCl / Cl, dw / w))
d = response(3, 1e-9) * uS_cm2
dNa, dK, dCl, dw, dV = d
conc = c["Na"] * dNa / Na + c["K"] * dK / K + c["Cl"] * dCl / Cl
dJp = 3 * Jp * dNa / Na
print("gKCC2: exact dV_ss %+.4f mV per uS/cm2 | Millman conc. route %+.4f | pump-current route %+.4f | d ln[Na]i %+.5f d ln[K]i %+.5f d ln[Cl]i %+.5f"
      % (dV * 1e3, conc * 1e3, -(dJp / gtot) * 1e3, dNa / Na, dK / K, dCl / Cl))

print("\n== Large steps, to compare with the paper's figures ==")
for factor in (2.0, 4.0):
    for ion, idx in (("gK", 1), ("gNa", 0), ("gCl", 2), ("gKCC2", 3)):
        pp = p0.copy(); pp[idx] *= factor
        x = solve(pp, xs)
        print("%s x%.0f: Vm %.1f mV, E_K %.1f, E_Cl %.1f, E_Na %.1f, [Cl]i %.2f mM, w/w0 %.3f" % (
            ion, factor, x[4] * 1e3, nernst(1, out["K"], x[1]) * 1e3, nernst(-1, out["Cl"], x[2]) * 1e3, nernst(1, out["Na"], x[0]) * 1e3, x[2] * 1e3, x[3] / w))
pp = p0.copy(); pp[3] = 0.0
x = solve(pp, xs)
print("gKCC2 = 0: Vm %.1f, E_Cl %.1f, E_K %.1f (paper: without KCC2 E_Cl = Vm)" % (x[4] * 1e3, nernst(-1, out["Cl"], x[2]) * 1e3, nernst(1, out["K"], x[1]) * 1e3))

print("\n== Pump-clamped pool sensitivities, per unit of the ion's own flux, relative to the unclamped linearisation ==")
print("Unclamped: the module's pool edge treats a unit sustained flux as a unit fractional change of the pool (no restoring force).")
print("Clamped (this model): d ln[ion]i per 1 uA/cm2 of the ion's own sustained inward flux:")
for ion, i in (("Na", 0), ("K", 1), ("Cl", 2)):
    print("  %-2s self-sensitivity d ln[%s]i / dI_%s = %+.4f per uA/cm2 (that flux is %.3f%% of the ion's resting leak current %.3f uA/cm2)" % (
        ion, ion, ion, rows[ion][i] / xs[i], 100 * unit_I / abs(g[ion] * (V - {"Na": ENa, "K": EK, "Cl": ECl}[ion])), abs(g[ion] * (V - {"Na": ENa, "K": EK, "Cl": ECl}[ion])) * 1e6 / 100))
