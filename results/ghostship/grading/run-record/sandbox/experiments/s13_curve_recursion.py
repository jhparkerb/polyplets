#!/usr/bin/env python3
"""Session 13: v-GENERAL local profile recursion (general point of the
singular curve Delta = 0, parametrized x = v^2, y_c = (1-v)^2, s* = 1/v)
and the scaling proof of the s09 curve-amplitude law.

Chart: s = s* + delta^2*tau, lambda := 8v^3(1-v)*tau, mu := lambda - 1
(so the D00 root u_- is mu = 0 and the closing-kernel point sigma+ is
mu = -2). Profiles (leading Laurent coefficients, inner chart):
  M00 = delta^-(4r+2) psi_r,  M10 = delta^-(4r+4) chi_r,
  M11 = delta^-(4r+6) phi_r.
Derived recursion (hand chart-expansion of the s08 operators; see
results/convex-area-local-transfer.md section 5):
  psi_r = -(r*kappa/mu) psi_{r-1}'        psi_0 = -4v^2(1-v)^3/mu
  chi_r = 4v^2(1-v)^2 psi_r + kappa r chi_{r-1}'
  a_r   = 2v chi_r + 8v^2(1-v) r phi_{r-1}'
  phi_r = 4v(1-v)^2 (a_r - a_r(-2))/(mu+2)
  c_r   = a_r(-2)/2,   d_r = c_r/(1-v)    [' = d/dmu = d/dlambda]
with kappa = 32 v^3 (1-v)^3.

CHECKS:
  K1  at v = 1/2 the system == the banked z-form system of
      s13_local_recursion.py (mu == z/2: coefficientwise match of chi,
      phi and c_r for r <= RMAX)
  K2  scaling law: for v in {1/3, 1/5, 3/7, 2/5}, r <= RMAX:
      c_r(v) == (r!)^2 2^(5r+3) (v(1-v))^(3r+5)   [s09 curve law]
  K3  normalized profiles are v-free: chi_r(v)/(Cchi g^r) and
      phi_r(v)/(Cphi g^r) identical across all v (pure functions of mu)

Output: out_s13_curve_recursion.txt
"""
import os, sys
from fractions import Fraction as Fr
from math import factorial

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 12
OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


def dmu(a):
    return {m + 1: -m * c for m, c in a.items()}


def ev(a, z):
    return sum(c * Fr(1, z ** m) for m, c in a.items())


def add(*As):
    r = {}
    for a in As:
        for m, c in a.items():
            r[m] = r.get(m, Fr(0)) + c
    return {m: c for m, c in r.items() if c}


def scal(a, k):
    return {m: k * c for m, c in a.items()}


def divmu2(a):
    """(a(mu) - a(-2))/(mu+2) for Laurent-poly a in 1/mu."""
    av = ev(a, -2)
    M = max(a) if a else 0
    g = {1: -av}
    for k in range(1, M + 1):
        g[k + 1] = a.get(k, Fr(0)) - 2 * g.get(k, Fr(0))
    assert g.get(M + 1, Fr(0)) == 0, "divmu2: non-terminating"
    g.pop(M + 1, None)
    return {m: c for m, c in g.items() if c}


def run_v(v, rmax):
    kap = 32 * v ** 3 * (1 - v) ** 3
    psi = {1: -4 * v ** 2 * (1 - v) ** 3}
    chi = scal(psi, 4 * v ** 2 * (1 - v) ** 2)
    a = scal(chi, 2 * v)
    phi = scal(divmu2(a), 4 * v * (1 - v) ** 2)
    cs = [ev(a, -2) / 2]
    chis, phis = [chi], [phi]
    for r in range(1, rmax + 1):
        psi = scal(dmu(psi), Fr(-r) * kap)   # note: (r kap / (-mu)) d/dmu
        psi = {m + 1: c for m, c in psi.items()}  # multiply by 1/(-mu)...
        # careful: psi_r = -(r kap/mu) psi'; dmu already returns
        # coefficients of psi' in 1/mu basis; multiply by 1/mu = shift
        # m->m+1, and by -r kap: BUT dmu(psi) computed above already
        # scaled by -r kap; the shift is the line above. Sign of 1/mu
        # multiplication is +; the minus sign is in the formula, and
        # dmu returns d/dmu; so psi_r = -r kap * (1/mu) * psi'_{r-1}:
        # scal(dmu(psi), -r kap) then shift. (Done.)
        chi = add(scal(psi, 4 * v ** 2 * (1 - v) ** 2),
                  scal(dmu(chis[r - 1]), kap * r))
        a = add(scal(chi, 2 * v),
                scal(dmu(phis[r - 1]), 8 * v ** 2 * (1 - v) * r))
        phi = scal(divmu2(a), 4 * v * (1 - v) ** 2)
        cs.append(ev(a, -2) / 2)
        chis.append(chi)
        phis.append(phi)
    return cs, chis, phis


say(f"== v-general local recursion, r <= {RMAX} ==")

# K1: v = 1/2 vs banked z-form (z = 2 mu)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
cs, chis, phis = run_v(Fr(1, 2), RMAX)
k1ok = True
zchi = {1: Fr(-1, 16)}
zphi = {1: Fr(-1, 64)}
zchis, zphis = {0: zchi}, {0: zphi}


def dz(a):
    return {m + 1: -m * c for m, c in a.items()}


def divz4(a):
    av = ev(a, -4)
    M = max(a)
    g = {1: -av}
    for k in range(1, M + 1):
        g[k + 1] = a.get(k, Fr(0)) - 4 * g.get(k, Fr(0))
    assert g.get(M + 1, Fr(0)) == 0
    g.pop(M + 1, None)
    return {m: c for m, c in g.items() if c}


zc = [Fr(1, 128)]
for r in range(1, RMAX + 1):
    zpsi = {2 * r + 1: Fr(-factorial(2 * r), 4)}
    zchi = add(scal(zpsi, Fr(1, 4)), scal(dz(zchis[r - 1]), r))
    za = add(zchi, scal(dz(zphis[r - 1]), 2 * r))
    zc.append(ev(za, -4) / 2)
    zchis[r], zphis[r] = zchi, divz4(za)
for r in range(RMAX + 1):
    # z = 2 mu: chi(z) = sum c_m z^-m = sum (c_m/2^m) mu^-m
    c1 = {m: c / Fr(2 ** m) for m, c in zchis[r].items()}
    p1 = {m: c / Fr(2 ** m) for m, c in zphis[r].items()}
    ok = (c1 == chis[r]) and (p1 == phis[r]) and (zc[r] == cs[r])
    k1ok &= ok
say(f"K1 (v=1/2 == banked z-form, r<={RMAX}): {'PASS' if k1ok else 'FAIL'}")

# K2 + K3
k2ok = k3ok = True
norm_ref = None
for v in (Fr(1, 3), Fr(1, 5), Fr(3, 7), Fr(2, 5), Fr(1, 2)):
    cs, chis, phis = run_v(v, RMAX)
    g = 64 * v ** 3 * (1 - v) ** 3
    Cchi = 512 * v ** 4 * (1 - v) ** 5
    Cphi = 8192 * v ** 6 * (1 - v) ** 7
    for r in range(RMAX + 1):
        want = Fr(factorial(r) ** 2) * 2 ** (5 * r + 3) * \
            (v * (1 - v)) ** (3 * r + 5)
        if cs[r] != want:
            k2ok = False
            say(f"  K2 FAIL v={v} r={r}: {cs[r]} != {want}")
    norm = tuple((tuple(sorted(scal(chis[r], 1 / (Cchi * g ** r)).items())),
                  tuple(sorted(scal(phis[r], 1 / (Cphi * g ** r)).items())))
                 for r in range(RMAX + 1))
    if norm_ref is None:
        norm_ref = norm
    elif norm != norm_ref:
        k3ok = False
        say(f"  K3 FAIL v={v}")
say(f"K2 (curve law c_r(v) = (r!)^2 2^(5r+3) (v(1-v))^(3r+5), "
    f"5 values of v, r<={RMAX}): {'PASS' if k2ok else 'FAIL'}")
say(f"K3 (normalized profiles v-free): {'PASS' if k3ok else 'FAIL'}")

with open(os.path.join(ROOT, "out_s13_curve_recursion.txt"), "w") as fp:
    fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
say("receipt: out_s13_curve_recursion.txt")
