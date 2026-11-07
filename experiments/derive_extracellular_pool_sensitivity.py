"""Committed 7 November 2026 (decision 9.112; docs/extracellular_pool_sensitivities_2026-11-07.md): the derivation
behind the extracellular values recorded with the owner's ruling of that day. Model B's equations were transcribed
from the authors' ModelDB file; the file itself is not committed. Run: python experiments/derive_extracellular_pool_sensitivity.py

Steady-state sensitivity of the EXTRACELLULAR pools to a sustained inward current of one ion, in two models with
an interstitial compartment, under three regulation schemes. Fable pass of 7 November 2026 for decision 9.112.

Definition (the same as the cytosolic derivation of 4 November 2026): add a sustained inward current I of one ion
(1 uA/cm2, into the cytosol), solve the new steady state with the pump (and KCC2 where the model has it) active, and
report d ln[ion]_o and d ln[ion]_i per uA/cm2.

Model A: Duesterwald et al. 2018 pump-leak model (eLife 7:e39575, Table 1) extended with a finite ECS of volume
  V_e = w0 / ratio (water moves, so V_e = V_tot - w), closed mass conservation for Na+, K+, Cl-, a fixed ECS
  impermeant anion X_o (29.5 mM at rest, the value that neutralises 145 + 3.5 - 119), the ECS osmolarity replacing
  the fixed Pi_o. K+ regulation: 'closed' (none), 'bath' (K_o held at its bath value at steady state: diffusive
  coupling of any strength), 'glia' (Huebel and Dahlem 2014's reversible buffer: at steady state the buffer holds
  -dk = k2(K_o) K_o B0 / (k1 + k2(K_o) K_o) with k2 = k1 / (1 + exp((15 - K_o)/1.09)), B0 = 500 mM of ECS).
Model B: Huebel and Dahlem 2014 (PLoS Comput Biol 10:e1003941), equations as in the authors' XPPAUT file
  spreading-depression.ode (ModelDB 167714): HH gated Na+ and K+ currents, leaks, pump
  6.8/(1+exp((25-Na_i)/3))/(1+exp(5.5-K_e)) uA/cm2, V_i:V_e = 2.16:0.72, Na+ and Cl- closed, K+ regulated by
  s=0 glia or s=1 bath, or closed (dk = 0).
"""
import numpy as np
from scipy.optimize import fsolve

# ------------------------------------------------------------------ Model A: Duesterwald + ECS
F = 96485.33; R = 8.31446; T = 310.15; RT_F = R * T / F
uS_cm2 = 1e-4
gA = {"Na": 20 * uS_cm2, "K": 70 * uS_cm2, "Cl": 20 * uS_cm2}
g_KCC2 = 20 * uS_cm2
P = 0.1
Cm = 2e-6 * 100
out0 = {"Na": 145e-3, "K": 3.5e-3, "Cl": 119e-3, "X": 29.5e-3}
zX = -0.85
radius = 5e-5; length = 25e-5
w0 = np.pi * radius ** 2 * length
N_X = 154.9e-3 * w0
unit_I = 1e-6 * 100  # 1 uA/cm2 in A/dm2
# Huebel glia constants (per second; K in mM)
k1 = 5e-5; B0 = 500.0; K_cr = 15.0


def nernst(zi, co, ci):
    return RT_F / zi * np.log(co / ci)


def model_a(ratio, scheme, phi, verbose=False):
    """ratio = V_i/V_e at rest. phi = dict of sustained inward molar flux densities (mol/(dm2 s)). Returns state."""
    V_e0 = w0 / ratio
    V_tot = w0 + V_e0
    N = {ion: 14.0e-3 * 0 for ion in ("Na", "K", "Cl")}  # placeholder
    # total moles from the rest state of the single-compartment model (solved below)
    rest = {"Na": 14.0e-3, "K": 122.87e-3, "Cl": 5.16e-3}
    # we fix totals from the rest state so that at phi = 0 the closed system reproduces the rest state
    N = {ion: rest[ion] * w0 + out0[ion] * V_e0 for ion in rest}
    NXo = out0["X"] * V_e0

    def unpack(xs):
        Na, K, Cl, w, V, Ko = xs[0] * 1e-3, xs[1] * 1e-3, xs[2] * 1e-3, xs[3] * 1e-12, xs[4] * 1e-3, xs[5] * 1e-3
        return Na, K, Cl, w, V, Ko

    def residuals(xs):
        Na, K, Cl, w, V, Ko = unpack(xs)
        V_e = V_tot - w
        Nao = (N["Na"] - Na * w) / V_e
        Clo = (N["Cl"] - Cl * w) / V_e
        Xo = NXo / V_e
        X = N_X / w
        r = np.sqrt(w / (np.pi * length)); Am = 2.0 / r
        ENa, EK, ECl = nernst(1, Nao, Na), nernst(1, Ko, K), nernst(-1, Clo, Cl)
        Jp = P * (Na / Nao) ** 3
        JK2 = g_KCC2 * (EK - ECl)
        # K_o closure
        if scheme == "closed":
            Ko_res = Ko - (N["K"] - K * w) / V_e
        elif scheme == "bath":
            Ko_res = Ko - out0["K"]
        elif scheme == "glia":
            Ko_mM = Ko * 1e3
            k2 = k1 / (1 + np.exp((K_cr - Ko_mM) / 1.09))
            dk = -k2 * Ko_mM * B0 / (k1 + k2 * Ko_mM)  # mM, K removed from the ECS by the buffer (negative)
            Ko_res = Ko - ((N["K"] - K * w) / V_e + dk * 1e-3)
        return [(gA["Na"] * (V - ENa) + 3 * Jp - F * phi.get("Na", 0.0)) * 1e4,
                (gA["K"] * (V - EK) - 2 * Jp - JK2 - F * phi.get("K", 0.0)) * 1e4,
                (gA["Cl"] * (V - ECl) + JK2 + F * phi.get("Cl", 0.0)) * 1e4,
                (Na + K + Cl + X - (Nao + Ko + Clo + Xo)) * 1e3,
                (F * (Na + K - Cl + zX * X) - Cm * Am * V) * 1e-2,
                Ko_res * 1e3]

    x0 = np.array([14.0, 122.87, 5.16, w0 * 1e12, -72.6, 3.5])
    x, info, ok, msg = fsolve(residuals, x0, xtol=1e-13, full_output=True)
    assert ok == 1, msg
    assert max(abs(v) for v in residuals(x)) < 1e-8, residuals(x)
    Na, K, Cl, w, V, Ko = unpack(x)
    V_e = V_tot - w
    Nao = (N["Na"] - Na * w) / V_e; Clo = (N["Cl"] - Cl * w) / V_e
    return dict(Na=Na, K=K, Cl=Cl, w=w, V=V, Nao=Nao, Ko=Ko, Clo=Clo, Ve=V_e)


def sens_a(ratio, scheme):
    base = model_a(ratio, scheme, {})
    out = {}
    d = 1e-12  # mol/(dm2 s)
    for ion in ("Na", "K", "Cl"):
        p = model_a(ratio, scheme, {ion: d}); m = model_a(ratio, scheme, {ion: -d})
        scale = unit_I / F / (2 * d)
        out[ion] = {k: (p[k] - m[k]) / base[k] * scale for k in ("Na", "K", "Cl", "Nao", "Ko", "Clo", "w", "Ve")}
        out[ion]["dV_mV"] = (p["V"] - m["V"]) * scale * 1e3
    return base, out


# ------------------------------------------------------------------ Model B: Huebel and Dahlem 2014 (ODE file)
vol_i, vol_e = 2.16, 0.72
nai0, ki0, cli0, ke0, nae0, cle0 = 25.231485, 129.25764, 9.900239, 4.0, 125.30555, 123.2716
G_NA_L, G_NA_G, G_K_L, G_K_G, G_CL_L = 0.0175, 100.0, 0.05, 40.0, 0.02
NA_PUMP, K_PUMP, MAX_PUMP = 25.0, 5.5, 6.8
lam = 3.0e-05; b0 = 500.0; K_cr_b = 15.0; k1_b = 5.e-8  # per ms, as in the file
CONV = 9.55589e-05; PHI = 3.0


def model_b(scheme, I_add, vol_e_=vol_e):
    """I_add: dict ion -> added INWARD current in uA/cm2 (positive = into the cell). scheme: closed|glia|bath."""
    def residuals(xs):
        v, n, ki, cli, dk = xs
        A_N = 0.01 * (v + 34.0) / (1.0 - np.exp(-0.1 * (v + 34.0)))
        B_N = 0.125 * np.exp(-(v + 44.0) / 80.0)
        A_M = 0.1 * (v + 30.0) / (1.0 - np.exp(-0.1 * (v + 30.0)))
        B_M = 4.0 * np.exp(-(v + 55.0) / 18.0)
        m = A_M / (A_M + B_M)
        h = 1 - 1. / (1 + np.exp(-6.5 * (n - 0.35)))
        nai = nai0 + ki0 - ki - cli0 + cli
        nae = (nai0 * vol_i + nae0 * vol_e_ - nai * vol_i) / vol_e_
        cle = (cli0 * vol_i + cle0 * vol_e_ - cli * vol_i) / vol_e_
        ke = (ki0 * vol_i + ke0 * vol_e_ - ki * vol_i) / vol_e_ + dk
        EK = 26.64 * np.log(ke / ki); ENA = 26.64 * np.log(nae / nai); ECL = -26.64 * np.log(cle / cli)
        I_NA_L = G_NA_L * (v - ENA); I_NA_G = G_NA_G * m ** 3 * h * (v - ENA)
        I_K_L = G_K_L * (v - EK); I_K_G = G_K_G * n ** 4 * (v - EK)
        I_CL_L = G_CL_L * (v - ECL)
        IPUMP = MAX_PUMP / (1.0 + np.exp((NA_PUMP - nai) / 3.)) / (1. + np.exp(K_PUMP - ke))
        # HH sign: outward positive. An added INWARD current of ion X is -I_add[X].
        I_NA = I_NA_L + I_NA_G + 3. * IPUMP - I_add.get("Na", 0.0)
        I_K = I_K_L + I_K_G - 2. * IPUMP - I_add.get("K", 0.0)
        # Cl-: an inward MOLAR flux of the anion is an outward (positive) HH current, so it is added, not subtracted.
        I_CL = I_CL_L + I_add.get("Cl", 0.0)
        if scheme == "glia":
            k2 = k1_b / (1 + np.exp((K_cr_b - ke) / 1.09))
            dk_dot = -k1_b * dk - k2 * ke * (b0 + dk)
        elif scheme == "bath":
            dk_dot = lam * (4.0 - ke)
        else:
            dk_dot = dk  # closed: dk = 0
        return [-(I_CL + I_NA + I_K), PHI * (A_N * (1 - n) - B_N * n) * 1e2, -CONV / vol_i * I_K * 1e4,
                CONV / vol_i * I_CL * 1e4, dk_dot * 1e6]

    x0 = np.array([-67.193253, 0.069410823, 129.25764, 9.900239, 0.0])
    x, info, ok, msg = fsolve(residuals, x0, xtol=1e-13, full_output=True)
    assert ok == 1, msg
    assert max(abs(r) for r in residuals(x)) < 1e-7, residuals(x)
    v, n, ki, cli, dk = x
    nai = nai0 + ki0 - ki - cli0 + cli
    nae = (nai0 * vol_i + nae0 * vol_e_ - nai * vol_i) / vol_e_
    cle = (cli0 * vol_i + cle0 * vol_e_ - cli * vol_i) / vol_e_
    ke = (ki0 * vol_i + ke0 * vol_e_ - ki * vol_i) / vol_e_ + dk
    return dict(Na=nai, K=ki, Cl=cli, Nao=nae, Ko=ke, Clo=cle, V=v, dk=dk, n=n)


def sens_b(scheme, vol_e_=vol_e):
    base = model_b(scheme, {}, vol_e_)
    out = {}
    d = 1e-4
    for ion in ("Na", "K", "Cl"):
        p = model_b(scheme, {ion: d}, vol_e_); m = model_b(scheme, {ion: -d}, vol_e_)
        out[ion] = {k: (p[k] - m[k]) / base[k] / (2 * d) for k in ("Na", "K", "Cl", "Nao", "Ko", "Clo")}
        out[ion]["dV_mV"] = (p["V"] - m["V"]) / (2 * d)
    return base, out


def show(title, base, out):
    print("\n" + title)
    print("  rest: [Na]i %.2f [K]i %.2f [Cl]i %.2f | [Na]o %.2f [K]o %.3f [Cl]o %.2f mM | Vm %.2f mV" % (
        base["Na"] * (1e3 if base["Na"] < 1 else 1), base["K"] * (1e3 if base["K"] < 1 else 1), base["Cl"] * (1e3 if base["Cl"] < 1 else 1),
        base["Nao"] * (1e3 if base["Nao"] < 1 else 1), base["Ko"] * (1e3 if base["Ko"] < 1 else 1), base["Clo"] * (1e3 if base["Clo"] < 1 else 1),
        base["V"] * (1e3 if abs(base["V"]) < 1 else 1)))
    print("  per 1 uA/cm2 sustained inward current of:   d ln[Na]i  d ln[K]i   d ln[Cl]i |  d ln[Na]o  d ln[K]o   d ln[Cl]o |  dV_ss mV")
    for ion in ("Na", "K", "Cl"):
        o = out[ion]
        print("  %-3s                                      %+10.4f %+10.4f %+10.4f | %+10.4f %+10.4f %+10.4f | %+8.3f" % (
            ion, o["Na"], o["K"], o["Cl"], o["Nao"], o["Ko"], o["Clo"], o["dV_mV"]) + ("   d ln w %+.4f d ln V_e %+.4f" % (o["w"], o["Ve"]) if "w" in o else ""))


if __name__ == "__main__":
    print("=== Model A: Duesterwald et al. 2018 pump-leak model + finite ECS (project constants, 37 C) ===")
    for ratio in (3.0, 4.0, 7.0):
        for scheme in ("closed", "bath", "glia"):
            base, out = sens_a(ratio, scheme)
            show("Model A, V_i:V_e = %.0f:1, K+ regulation: %s" % (ratio, scheme), base, out)
    print("\n=== Model B: Huebel and Dahlem 2014, the authors' ODE file (ModelDB 167714), V_i:V_e = 3:1 ===")
    for scheme in ("closed", "glia", "bath"):
        base, out = sens_b(scheme)
        show("Model B, K+ regulation: %s" % scheme, base, out)
    base, out = sens_b("glia", vol_e_=vol_i / 4.0)
    show("Model B, glia, V_i:V_e = 4:1 (alpha 0.2)", base, out)
    # Glial buffer share at rest, Huebel scheme
    for Ko in (3.5, 4.0):
        k2 = k1 / (1 + np.exp((K_cr - Ko) / 1.09))
        dk = -k2 * Ko * B0 / (k1 + k2 * Ko)
        eps = 1e-3
        k2p = k1 / (1 + np.exp((K_cr - Ko - eps) / 1.09)); dkp = -k2p * (Ko + eps) * B0 / (k1 + k2p * (Ko + eps))
        print("\nHuebel glial buffer at K_o = %.1f mM: holds %.4f mM (ECS units); slope d(buffered)/dK_o = %.4f" % (Ko, -dk, -(dkp - dk) / eps))
