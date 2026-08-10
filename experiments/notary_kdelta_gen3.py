#!/usr/bin/env python3
"""Notary piece K, wave K-delta generator, stage 3a: emit the Sol module data.

Reads build/notary_kdelta_data.json and build/notary_kdelta_data2.json and
emits build/notary_kdelta_sol.lean.txt: Lean-syntax fragments for
DepthOneKernelSol.lean —

  * polynomial literals for the numerators, denominators, cleared-row
    entries (as `PowerSeries ℚ` expressions in X);
  * the twelve cleared-row identities in num-form (the d5 shape), each with
    its `linear_combination` certificate over the two square relations
    A*A = 1-2X-3X^2 and B*B = 1+2X-3X^2, computed by free-polynomial
    reduction and RE-VERIFIED symbolically before emission;
  * the divX low-coefficient guard values.

Every emitted identity is re-checked: lhs - rhs == cA*(a^2-AA) + cB*(b^2-BB)
expands to zero as a free polynomial in (s, a, b).

Exact command:
  python3 experiments/notary_kdelta_gen3.py \
      | tee build/notary_kdelta_gen3.log
Target machine: gympie (local).  Predicted cost: < 2 min, one core.
Kill/resume: stateless; rerun from scratch.
"""
import json
import os
import sys
import time

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

s = sp.symbols('s')
a, b = sp.symbols('a b')
AA = 1 - 2 * s - 3 * s ** 2
BB = 1 + 2 * s - 3 * s ** 2

t0 = time.time()
D1 = json.load(open('build/notary_kdelta_data.json'))
D2 = json.load(open('build/notary_kdelta_data2.json'))
NAMES = ['j1', 'j2', 'j3', 'Jm', 'p2', 'p3']
LNAME = {'j1': 'J1', 'j2': 'J2', 'j3': 'J3', 'Jm': 'Jm', 'p2': 'P2',
         'p3': 'P3'}


def stage(name):
    print(f"  [{time.time() - t0:6.1f}s] {name}", flush=True)


def fail(msg):
    print(f"FAIL: {msg}", flush=True)
    sys.exit(1)


def lean_q(r):
    """A rational as a Lean ℚ scalar factor string."""
    r = sp.nsimplify(r)
    p, q = sp.fraction(r)
    if q == 1:
        return str(p) if p >= 0 else f"(-{-p})"
    return f"({p}/{q} : ℚ)" if p >= 0 else f"(-{-p}/{q} : ℚ)"


def lean_poly(expr):
    """A polynomial in s as a Lean `PowerSeries ℚ` expression in X."""
    expr = sp.expand(expr)
    if expr == 0:
        return "0"
    p = sp.Poly(expr, s)
    terms = []
    for (k,), co in sorted(p.as_dict().items()):
        pq, qq = sp.fraction(sp.nsimplify(co))
        if qq != 1:
            base = f"C ({pq}/{qq} : ℚ)"
        else:
            base = f"C ({pq} : ℚ)"
        if k == 0:
            terms.append(base)
        elif k == 1:
            terms.append(f"{base} * X")
        else:
            terms.append(f"{base} * X ^ {k}")
    return " + ".join(terms).replace("+ C (-", "+ C (-")


def lean_tup(tup_strs, aname="Kernel.A", bname="Kernel.B"):
    """A 4-tuple of polynomial strings -> Lean basis combination."""
    parts = []
    for i, t in enumerate(tup_strs):
        e = sp.sympify(t)
        if e == 0:
            continue
        pol = f"({lean_poly(e)})"
        basis = [None, aname, bname, f"({aname} * {bname})"][i]
        parts.append(pol if basis is None else f"{pol} * {basis}")
    return " + ".join(parts) if parts else "0"


def tup_to_free(tup_strs):
    """4-tuple of strings -> free polynomial in (s, a, b)."""
    t = [sp.sympify(x) for x in tup_strs]
    return sp.expand(t[0] + t[1] * a + t[2] * b + t[3] * a * b)


def reduce_free(expr):
    """Reduce a free poly by a^2 -> AA, b^2 -> BB; return (residue, cA, cB)
    with expr = residue + cA*(a^2 - AA) + cB*(b^2 - BB)."""
    cA = sp.S(0)
    cB = sp.S(0)
    e = sp.expand(expr)
    changed = True
    while changed:
        changed = False
        pa = sp.Poly(e, a)
        if pa.degree() >= 2:
            # e = sum_k coeff_k a^k ; replace a^k (k>=2) via a^2 = AA + (a^2-AA)
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


out = []
for kind in ('int', 'bare'):
    K = kind.capitalize()
    ent = D1[f'entries_{kind}']
    es = [e['e'] for e in ent]
    dens = [sp.sympify(e['den']) for e in ent]
    E = D2[f'E_{kind}']
    D = sp.sympify(D2[f'D_{kind}'])

    out.append(f"-- ==================== start: {kind} ====================")
    # numerators and denominators
    for c, e in enumerate(ent):
        nm = LNAME[NAMES[c]]
        out.append(f"noncomputable def num{nm}{K} : PowerSeries ℚ :=")
        out.append(f"  {lean_tup(e['nums'])}")
        out.append(f"noncomputable def den{nm}{K} : PowerSeries ℚ :=")
        out.append(f"  {lean_poly(dens[c])}")
        out.append(f"-- shift e = {e['e']}; den(0) = "
                   f"{sp.sympify(e['den']).subs(s, 0)}")
    out.append(f"-- E = {E}, D:")
    out.append(f"noncomputable def denAll{K} : PowerSeries ℚ :=")
    out.append(f"  {lean_poly(D)}")

    # cleared rows in num-form with certificates
    M = D2[f'M_{kind}']
    R = D2[f'R_{kind}']
    for r in range(6):
        lhs_free = sp.S(0)
        for c in range(6):
            scale = sp.expand(s ** (E - es[c]) * sp.cancel(D / dens[c]))
            lhs_free += tup_to_free(M[r][c]) * scale * tup_to_free(
                ent[c]['nums'])
        rhs_free = sp.expand(s ** E * D) * tup_to_free(R[r])
        diff = sp.expand(lhs_free - rhs_free)
        residue, cA, cB = reduce_free(diff)
        if sp.expand(residue) != 0:
            fail(f"row {r + 1} ({kind}): residue nonzero after reduction")
        # re-verify certificate as free polynomial identity
        chk = sp.expand(diff - cA * (a ** 2 - AA) - cB * (b ** 2 - BB))
        if chk != 0:
            fail(f"row {r + 1} ({kind}): certificate fails")
        out.append(f"-- row {r + 1} ({kind}): sizes cA={len(str(cA))} "
                   f"cB={len(str(cB))}")
        # emit the row statement pieces
        terms = []
        for c in range(6):
            nm = LNAME[NAMES[c]]
            scale = sp.expand(s ** (E - es[c]) * sp.cancel(D / dens[c]))
            terms.append(f"({lean_tup(M[r][c])}) * ({lean_poly(scale)}) * "
                         f"num{nm}{K}")
        lhs = " +\n      ".join(terms)
        rhs = f"({lean_poly(sp.expand(s ** E * D))}) * ({lean_tup(R[r])})"
        out.append(f"theorem row{r + 1}{K} :")
        out.append(f"    {lhs}")
        out.append(f"      = {rhs} := by")
        # certificate in Lean form: polynomials in X, A, B
        def free_to_lean(e):
            e = sp.expand(e)
            if e == 0:
                return "0"
            # collect over a, b monomials
            parts = []
            pab = sp.Poly(e, a, b)
            for (ka, kb), co in sorted(pab.as_dict().items()):
                pol = f"({lean_poly(co)})"
                mon = []
                if ka:
                    mon.append("Kernel.A" if ka == 1 else f"Kernel.A ^ {ka}")
                if kb:
                    mon.append("Kernel.B" if kb == 1 else f"Kernel.B ^ {kb}")
                parts.append(" * ".join([pol] + mon))
            return " + ".join(parts)
        out.append(f"  linear_combination ({free_to_lean(cA)}) * "
                   f"Kernel.A_sq + ({free_to_lean(cB)}) * Kernel.B_sq")
        out.append("")
    stage(f"rows + certificates emitted and re-verified ({kind})")

os.makedirs('build', exist_ok=True)
with open('build/notary_kdelta_sol.lean.txt', 'w') as f:
    f.write("\n".join(out) + "\n")
stage("wrote build/notary_kdelta_sol.lean.txt")
print(f"ALL PASS ({time.time() - t0:.1f}s)")
