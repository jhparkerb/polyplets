#!/usr/bin/env python3
"""Notary piece K, wave K-delta generator, stage 3g: the cleared quartic on F1.

The banked `cY_k` are the raw elimination coefficients divided by a common
factor `g(X)` (degree 40).  In Lean we never need `g`: the cleared
annihilation

    bracket := sum_k cY_k(X^2) * numTuple^k * phiDen^(4-k)  ==  0   (mod A^2=AA, B^2=BB)

holds directly, because `g * bracket = phiDen^4 * Psi(numTuple)` is `0` mod the
square relations and `ℚ[X]` is a domain (so the nonzero scalar `g` is a
non-zero-divisor on the rank-4 module `ℚ[X,a,b]/(a^2-AA, b^2-BB)`; `g·r = 0`
forces `r = 0`).  So `bracket` reduces to `0` with its own `A_sq`/`B_sq`
certificate.

This script emits build/notary_kdelta_phi2.lean.txt:
  * `phiCYksq` : the five `cY_k(X^2)` as even-power `X`-polynomials;
  * `bracketExpr` provenance and the `linear_combination` certificate for
    `bracket = 0`, computed by free-polynomial reduction and RE-VERIFIED.

Exact command:
  python3 experiments/notary_kdelta_gen7.py | tee build/notary_kdelta_gen7.log
Target machine: gympie (local).  Predicted cost: < 1 min, one core.
"""
import json
import os
import sys
import time

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

s, a, b, y = sp.symbols('s a b y')
AA = 1 - 2 * s - 3 * s ** 2
BB = 1 + 2 * s - 3 * s ** 2

t0 = time.time()
D1 = json.load(open('build/notary_kdelta_data.json'))


def stage(name):
    print(f"  [{time.time() - t0:6.1f}s] {name}", flush=True)


def fail(msg):
    print(f"FAIL: {msg}", flush=True)
    sys.exit(1)


def lean_poly(expr):
    expr = sp.expand(expr)
    if expr == 0:
        return "0"
    p = sp.Poly(expr, s)
    terms = []
    for (k,), co in sorted(p.as_dict().items()):
        pq, qq = sp.fraction(sp.nsimplify(co))
        if qq != 1:
            fail(f"non-integer coefficient {co}")
        base = str(pq) if pq >= 0 else f"(-{-pq})"
        if k == 0:
            terms.append(base)
        elif k == 1:
            terms.append(f"{base} * X")
        else:
            terms.append(f"{base} * X ^ {k}")
    return " + ".join(terms)


def reduce_free(expr):
    cA = sp.S(0)
    cB = sp.S(0)
    e = sp.expand(expr)
    changed = True
    while changed:
        changed = False
        pa = sp.Poly(e, a)
        if pa.degree() >= 2:
            newe = sp.S(0)
            for (k,), co in pa.as_dict().items():
                if k >= 2:
                    cA += sp.expand(co * a ** (k - 2))
                    newe += co * a ** (k - 2) * AA
                else:
                    newe += co * a ** k
            e = sp.expand(newe)
            changed = True
            continue
        pb = sp.Poly(e, b)
        if pb.degree() >= 2:
            newe = sp.S(0)
            for (k,), co in pb.as_dict().items():
                if k >= 2:
                    cB += sp.expand(co * b ** (k - 2))
                    newe += co * b ** (k - 2) * BB
                else:
                    newe += co * b ** k
            e = sp.expand(newe)
            changed = True
            continue
    return e, sp.expand(cA), sp.expand(cB)


def free_to_lean(e):
    e = sp.expand(e)
    if e == 0:
        return "0"
    parts = []
    for (ka, kb), co in sorted(sp.Poly(e, a, b).as_dict().items()):
        pol = f"({lean_poly(co)})"
        mon = []
        if ka:
            mon.append("Kernel.A" if ka == 1 else f"Kernel.A ^ {ka}")
        if kb:
            mon.append("Kernel.B" if kb == 1 else f"Kernel.B ^ {kb}")
        parts.append(" * ".join([pol] + mon))
    return " + ".join(parts)


F1 = D1['F1']
den = sp.sympify(F1['den'])
n0 = sp.sympify(F1['n0'])
n1 = sp.sympify(F1['n1'])
n2 = sp.sympify(F1['n2'])
n3 = sp.sympify(F1['n3'])
cY = [sp.sympify(c) for c in D1['cY']]  # y-polynomials
numTuple = n0 + n1 * a + n2 * b + n3 * a * b

# bracket = sum_k cY_k(s^2) * numTuple^k * den^(4-k)
bracket = sp.S(0)
for k in range(5):
    cYk_s = cY[k].subs(y, s ** 2)
    bracket += cYk_s * numTuple ** k * den ** (4 - k)
bracket = sp.expand(bracket)
stage(f"bracket assembled ({len(str(bracket))} chars free)")

residue, cA, cB = reduce_free(bracket)
if sp.expand(residue) != 0:
    fail(f"bracket residue nonzero after reduction: {str(residue)[:120]}")
chk = sp.expand(bracket - cA * (a ** 2 - AA) - cB * (b ** 2 - BB))
if chk != 0:
    fail("bracket certificate fails")
stage(f"bracket = 0 certificate OK (cA {len(str(cA))} chars, cB {len(str(cB))})")

# sanity: g * bracket = den^4 * Psi(numTuple) with g = gcd(cTk)
tau = sp.symbols('tau')
Pq = sp.expand(n1 ** 2 * AA - n2 ** 2 * BB - n3 ** 2 * AA * BB)
Psi_tau = sp.expand(sp.expand((tau - n0) ** 2 + Pq) ** 2
                    - 4 * AA * (n1 * (tau - n0) + n2 * n3 * BB) ** 2)
cs = sp.Poly(Psi_tau, tau).all_coeffs()
cTk = [sp.expand(cs[4 - k] * den ** k) for k in range(5)]
g = sp.gcd(cTk)
print(f"    g = gcd(cTk): degree {sp.degree(g, s)}, "
      f"g(0) = {g.subs(s, 0)} (nonzero ⇒ unit, confirms domain argument)")

# emit
out = []
out.append("-- cY_k(X^2): the y-form quartic coefficients at y = X^2 (even).")
for k in range(5):
    out.append(f"noncomputable def phiCY{k}sq : PowerSeries ℚ :=")
    out.append(f"  {lean_poly(cY[k].subs(y, s ** 2))}")
out.append("")
out.append("-- bracket := Σ_k phiCYksq * numTuple^k * phiDen^(4-k) = 0 (mod squares)")
out.append(f"-- certificate sizes: cA {len(str(cA))} chars, cB {len(str(cB))} chars")
out.append("noncomputable def bracket : PowerSeries ℚ :=")
out.append("  phiCY0sq * phiDen ^ 4 + phiCY1sq * numTuple * phiDen ^ 3 +")
out.append("    phiCY2sq * numTuple ^ 2 * phiDen ^ 2 + "
           "phiCY3sq * numTuple ^ 3 * phiDen +")
out.append("    phiCY4sq * numTuple ^ 4")
out.append("")
cert = (f"linear_combination ({free_to_lean(cA)}) * Kernel.A_sq + "
        f"({free_to_lean(cB)}) * Kernel.B_sq")
with open('build/notary_kdelta_phi2_cert.txt', 'w') as f:
    f.write(cert + "\n")
with open('build/notary_kdelta_phi2.lean.txt', 'w') as f:
    f.write("\n".join(out) + "\n")
stage("wrote build/notary_kdelta_phi2.lean.txt + phi2_cert.txt")
print(f"ALL PASS ({time.time() - t0:.1f}s)  "
      f"[bracket cert cA/cB = {len(str(cA))}/{len(str(cB))} chars]")
