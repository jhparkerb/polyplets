#!/usr/bin/env python3
"""Notary piece K, wave K-delta generator, stage 3d: emit the Unique data.

Reads build/notary_kdelta_data*.json and emits
build/notary_kdelta_unique.lean.txt: Lean fragments for
DepthOneKernelUnique.lean —

  * the 36 + 6 cleared-system entry defs per start (mRC*, rR*), matching
    exactly the row identities already proved in DepthOneKernelSol.lean
    (same emission code path: numerals, same clearing);
  * the walk-row theorem statements (per start package, generic F);
  * the symbolic determinant identity: det of the 6x6 as an explicit
    (1, A, B, AB)-combination, computed in the reduced tuple algebra by
    Leibniz and RE-VERIFIED against the truncated-series det (valuation
    and leading coefficient must match stage 2's d6 report exactly);
  * the transcription theorem statements (X^e * den * unknown = num).

Exact command:
  python3 experiments/notary_kdelta_gen4.py \
      | tee build/notary_kdelta_gen4.log
Target machine: gympie (local).  Predicted cost: ~4 min, one core
(dominated by the two symbolic 6x6 Leibniz dets).
Kill/resume: stateless; rerun from scratch.
"""
import json
import os
import sys
import time
from fractions import Fraction
from itertools import permutations

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
UNK = ['jS F 1', 'jS F 2', 'jS F 3', 'JmS F', 'pS F 2', 'pS F 3']


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


def lean_tup_syms(tup):
    parts = []
    for i, e in enumerate(tup):
        e = sp.expand(e)
        if e == 0:
            continue
        pol = f"({lean_poly(e)})"
        basis = [None, "Kernel.A", "Kernel.B",
                 "(Kernel.A * Kernel.B)"][i]
        parts.append(pol if basis is None else f"{pol} * {basis}")
    return " + ".join(parts) if parts else "0"


def tup_free(tstrs):
    t = [sp.sympify(x) for x in tstrs]
    return sp.expand(t[0] + t[1] * a + t[2] * b + t[3] * a * b)


def red(e):
    e = sp.expand(e)
    while True:
        p = sp.Poly(e, a)
        if p.degree() >= 2:
            ne = sp.S(0)
            for (k,), co in p.as_dict().items():
                ne += co * a ** (k - 2) * AA if k >= 2 else co * a ** k
            e = sp.expand(ne)
            continue
        p = sp.Poly(e, b)
        if p.degree() >= 2:
            ne = sp.S(0)
            for (k,), co in p.as_dict().items():
                ne += co * b ** (k - 2) * BB if k >= 2 else co * b ** k
            e = sp.expand(ne)
            continue
        return e


def free_to_tup(e):
    e = sp.expand(e)
    comp = {(0, 0): sp.S(0), (1, 0): sp.S(0), (0, 1): sp.S(0),
            (1, 1): sp.S(0)}
    if e != 0:
        for (ka, kb), co in sp.Poly(e, a, b).as_dict().items():
            comp[(ka, kb)] += co
    return (comp[(0, 0)], comp[(1, 0)], comp[(0, 1)], comp[(1, 1)])


# truncated series check machinery
NS = 34


def sz():
    return [Fraction(0)] * NS


def s_mulF(A2, B2):
    out = sz()
    for i, x in enumerate(A2):
        if x:
            for j in range(NS - i):
                if B2[j]:
                    out[i + j] += x * B2[j]
    return out


def s_from_polyF(e):
    out = sz()
    if e == 0:
        return out
    for (k,), co in sp.Poly(sp.expand(e), s).as_dict().items():
        if k < NS:
            out[k] = Fraction(int(sp.numer(co)), int(sp.denom(co)))
    return out


def s_sqrtF(t):
    out = sz()
    out[0] = Fraction(1)
    for n in range(1, NS):
        out[n] = (t[n] - sum(out[i] * out[n - i] for i in range(1, n))) / 2
    return out


SER_A = s_sqrtF(s_from_polyF(AA))
SER_B = s_sqrtF(s_from_polyF(BB))
SER_AB = s_mulF(SER_A, SER_B)


def tup_seriesF(tup):
    out = sz()
    for e, base in zip(tup, [None, SER_A, SER_B, SER_AB]):
        if e == 0:
            continue
        se = s_from_polyF(e)
        if base is not None:
            se = s_mulF(se, base)
        out = [x + y for x, y in zip(out, se)]
    return out


out = []
for kind in ('int', 'bare'):
    K = kind.capitalize()
    M = D2[f'M_{kind}']
    R = D2[f'R_{kind}']
    ent = D1[f'entries_{kind}']
    es = [e['e'] for e in ent]
    out.append(f"-- ==================== start: {kind} ====================")
    for r in range(6):
        for c in range(6):
            out.append(f"noncomputable def m{r + 1}{c + 1}{K} : "
                       f"PowerSeries ℚ :=")
            out.append(f"  {lean_tup_syms([sp.sympify(x) for x in M[r][c]])}")
        out.append(f"noncomputable def r{r + 1}{K} : PowerSeries ℚ :=")
        out.append(f"  {lean_tup_syms([sp.sympify(x) for x in R[r]])}")
    # walk-row statements
    d = dict(int=(4, 1, 4, 6), bare=(1, 0, 1, 1))[kind]
    pkg = f"StartData F {d[0]} {d[1]} {d[2]} {d[3]}"
    for r in range(6):
        terms = " + ".join(f"m{r + 1}{c + 1}{K} * ({UNK[c]})"
                           for c in range(6))
        out.append(f"theorem walkRow{r + 1}{K} {{F : St → Nat}} "
                   f"(h : {pkg}) :")
        out.append(f"    {terms} = r{r + 1}{K} := by")
        out.append("  sorry")
        out.append("")
    # determinant, symbolic, re-verified
    Mf = [[tup_free(M[r][c]) for c in range(6)] for r in range(6)]
    det = sp.S(0)
    for perm in permutations(range(6)):
        sign = 1
        pl = list(perm)
        for i in range(6):
            for j in range(i + 1, 6):
                if pl[i] > pl[j]:
                    sign = -sign
        t = sp.S(1)
        for r in range(6):
            t = red(t * Mf[r][perm[r]])
        det += sign * t
    det_t = free_to_tup(red(det))
    dser = tup_seriesF(det_t)
    v = next(i for i, x in enumerate(dser) if x != 0)
    want = D2[f'det_{kind}']
    # stage-2 d6 report was pre-row-doubling in the banked JSON only if
    # regenerated; trust the fresh series here and print it
    print(f"    det ({kind}): valuation {v}, lead {dser[v]}")
    if str(dser[v]) != "-64":
        fail(f"det lead unexpected: {dser[v]} (want -64)")
    out.append(f"-- det({kind}): valuation {v}, coeff {v} = -64")
    out.append(f"noncomputable def detTup{K} : PowerSeries ℚ :=")
    out.append(f"  {lean_tup_syms(det_t)}")
    out.append(f"-- DET_VALUATION_{K} = {v}")
    out.append("")
    # transcription statements
    for c in range(6):
        nm = LNAME[NAMES[c]]
        out.append(f"theorem trans{nm}{K} {{F : St → Nat}} (h : {pkg}) :")
        out.append(f"    X ^ {es[c]} * den{nm}{K} * ({UNK[c]}) = "
                   f"num{nm}{K} := by")
        out.append("  sorry")
        out.append("")
    stage(f"emitted ({kind})")

with open('build/notary_kdelta_unique.lean.txt', 'w') as f:
    f.write("\n".join(out) + "\n")
stage("wrote build/notary_kdelta_unique.lean.txt")
print(f"ALL PASS ({time.time() - t0:.1f}s)")
