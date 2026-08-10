#!/usr/bin/env python3
"""Notary piece K, wave K-delta generator, stage 3f: emit the Phi module data.

Reads build/notary_kdelta_data.json (F1 tuple den/n0..n3, the y-form quartic
cY_0..cY_4, lift ratio) and emits build/notary_kdelta_phi.lean.txt: Lean
fragments for DepthOneKernelPhi.lean —

  * the scalar elimination identity `Psi(numTuple) = 0` in ℚ[s, a, b] mod the
    two square relations a^2 = AA, b^2 = BB, with its `linear_combination`
    certificate over `Kernel.A_sq`/`Kernel.B_sq`, computed by free-polynomial
    reduction and RE-VERIFIED before emission.  This is the whole quartic:
    with numTuple = n0 + n1 a + n2 b + n3 ab and d = numTuple - n0,
        ((d^2 + Pq)^2 - 4 AA (d n1 + n2 n3 BB)^2) = cA (a^2 - AA) + cB (b^2 - BB);
  * the five y-form quartic coefficients cY_0..cY_4 as `ℚ[y]` literals;
  * the lift `ring` identity, an equality of polynomials in (x, W):
        sum_k cY_k(3x) ((W-1)/3)^k = (1/3) sum_k phiC_k(x) W^k
    (phiC from experiments/depth1_recurrence.py::PHI_COEFFS), RE-VERIFIED.

Every emitted identity is re-checked symbolically.  Reports cofactor sizes so
the skeleton can pick heartbeat/recursion budgets.

Exact command:
  python3 experiments/notary_kdelta_gen6.py | tee build/notary_kdelta_gen6.log
Target machine: gympie (local).  Predicted cost: < 1 min, one core.
Kill/resume: stateless; rerun from scratch.
"""
import json
import os
import sys
import time

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

s, a, b, y, x, W = sp.symbols('s a b y x W')
AA = 1 - 2 * s - 3 * s ** 2
BB = 1 + 2 * s - 3 * s ** 2

t0 = time.time()
D1 = json.load(open('build/notary_kdelta_data.json'))


def stage(name):
    print(f"  [{time.time() - t0:6.1f}s] {name}", flush=True)


def fail(msg):
    print(f"FAIL: {msg}", flush=True)
    sys.exit(1)


def lean_poly(expr, var="X"):
    """Integer-coefficient polynomial in `s` as a Lean expression in `var`,
    bare numerals (a `C`-literal is an opaque atom to `ring`)."""
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
            terms.append(f"{base} * {var}")
        else:
            terms.append(f"{base} * {var} ^ {k}")
    return " + ".join(terms)


def lean_poly_y(expr, var="X"):
    """Integer-coefficient polynomial in `y` as a Lean expr in `var`."""
    expr = sp.expand(expr)
    if expr == 0:
        return "0"
    p = sp.Poly(expr, y)
    terms = []
    for (k,), co in sorted(p.as_dict().items()):
        pq, qq = sp.fraction(sp.nsimplify(co))
        if qq != 1:
            fail(f"non-integer coefficient {co}")
        base = str(pq) if pq >= 0 else f"(-{-pq})"
        if k == 0:
            terms.append(base)
        elif k == 1:
            terms.append(f"{base} * {var}")
        else:
            terms.append(f"{base} * {var} ^ {k}")
    return " + ".join(terms)


def reduce_free(expr):
    """expr = residue + cA (a^2-AA) + cB (b^2-BB); residue is a,b-linear."""
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
    """Free poly in (s, a, b) -> Lean expr over Kernel.A / Kernel.B."""
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
if den.subs(s, 0) == 0:
    fail("den is not a unit in Q[[s]]")
stage(f"loaded F1 tuple (den {len(str(sp.expand(den)))} chars, den(0)="
      f"{den.subs(s, 0)})")

# --- the scalar elimination identity Psi(numTuple) = 0 ------------------
Pq = sp.expand(n1 ** 2 * AA - n2 ** 2 * BB - n3 ** 2 * AA * BB)
d = n1 * a + n2 * b + n3 * a * b            # numTuple - n0, as free poly
lhs = sp.expand((d ** 2 + Pq) ** 2)
rhs = sp.expand(4 * AA * (d * n1 + n2 * n3 * BB) ** 2)
diff = sp.expand(lhs - rhs)
residue, cA, cB = reduce_free(diff)
if sp.expand(residue) != 0:
    fail("Psi residue nonzero after reduction")
chk = sp.expand(diff - cA * (a ** 2 - AA) - cB * (b ** 2 - BB))
if chk != 0:
    fail("Psi certificate fails")
stage(f"Psi certificate OK (cA {len(str(cA))} chars, cB {len(str(cB))} chars)")

# --- cY literals (y-form quartic) and the lift ring identity ------------
cY = [sp.sympify(c) for c in D1['cY']]
# re-derive cY from the tuple to confirm the banked literals
cT = []
tau = sp.symbols('tau')
Psi_tau = sp.expand(sp.expand((tau - n0) ** 2 + Pq) ** 2
                    - 4 * AA * (n1 * (tau - n0) + n2 * n3 * BB) ** 2)
cs = sp.Poly(Psi_tau, tau).all_coeffs()
cTk = [sp.expand(cs[4 - k] * den ** k) for k in range(5)]
g = sp.gcd(cTk)
cTk = [sp.expand(sp.cancel(ci / g)) for ci in cTk]
cY_check = []
for ci in cTk:
    out = sp.S(0)
    for (k,), co in sp.Poly(ci, s).as_dict().items():
        if k % 2:
            fail("odd power of s in the eliminated quartic")
        out += co * y ** (k // 2)
    cY_check.append(sp.expand(out))
for k in range(5):
    if sp.expand(cY[k] - cY_check[k]) != 0:
        fail(f"cY_{k} banked literal disagrees with re-derivation")
stage("cY_0..cY_4 re-derived and matched to banked literals")

from depth1_recurrence import PHI_COEFFS  # noqa: E402
lift = sp.expand(sum(cY[k].subs(y, 3 * x) * ((W - 1) / sp.S(3)) ** k
                     for k in range(5)))
banked = sp.expand(sum(sp.sympify(PHI_COEFFS[k]) * W ** k for k in range(5)))
if sp.expand(3 * lift - banked) != 0:
    fail("lift identity 3*sum cY_k(3x)((W-1)/3)^k = Phi fails")
stage("lift ring identity verified: 3*(y-form) = banked Phi(x, W)")

# --- emit ---------------------------------------------------------------
out = []
out.append("-- Psi(numTuple) = 0 : the scalar quartic, mod a^2=AA, b^2=BB")
out.append("-- numTuple = n0 + n1 A + n2 B + n3 A B ; d = numTuple - n0")
out.append(f"-- den(0) = {den.subs(s, 0)}")
out.append("noncomputable def phiN0 : PowerSeries ℚ := " + lean_poly(n0))
out.append("noncomputable def phiN1 : PowerSeries ℚ := " + lean_poly(n1))
out.append("noncomputable def phiN2 : PowerSeries ℚ := " + lean_poly(n2))
out.append("noncomputable def phiN3 : PowerSeries ℚ := " + lean_poly(n3))
out.append("noncomputable def phiDen : PowerSeries ℚ := " + lean_poly(den))
out.append("noncomputable def phiPq : PowerSeries ℚ := " + free_to_lean(Pq))
out.append("")
out.append(f"-- Psi certificate sizes: cA {len(str(cA))}, cB {len(str(cB))}")
out.append("-- linear_combination certificate for the scalar quartic:")
out.append(f"--   ({free_to_lean(cA)})")
out.append("--     * Kernel.A_sq +")
out.append(f"--   ({free_to_lean(cB)})")
out.append("--     * Kernel.B_sq")
out.append("")
for k in range(5):
    out.append(f"noncomputable def phiCY{k} : PowerSeries ℚ := "
               + lean_poly_y(cY[k]))
out.append("")
out.append("-- lift: 3 * sum_k cY_k(3x) ((W-1)/3)^k = sum_k phiC_k(x) W^k")
out.append(f"-- (PHI_COEFFS degree-{max(sp.degree(sp.sympify(c), x) for c in PHI_COEFFS[0:1])} in x)")

# also emit the full certificate as ready-to-paste linear_combination
cert = f"linear_combination ({free_to_lean(cA)}) * Kernel.A_sq + " \
       f"({free_to_lean(cB)}) * Kernel.B_sq"
with open('build/notary_kdelta_phi_cert.txt', 'w') as f:
    f.write(cert + "\n")

with open('build/notary_kdelta_phi.lean.txt', 'w') as f:
    f.write("\n".join(out) + "\n")
stage("wrote build/notary_kdelta_phi.lean.txt + phi_cert.txt")
print(f"ALL PASS ({time.time() - t0:.1f}s)  "
      f"[Psi cert cA/cB = {len(str(cA))}/{len(str(cB))} chars]")
