#!/usr/bin/env python3
"""Notary piece K, wave K-delta generator, stage 3e: rows 5/6 certificates.

The walkRow5/walkRow6 theorems of DepthOneKernelUnique.lean say the
cleared P-rows follow from the gamma equations. This script computes the
exact `linear_combination` cofactors:

    row - lam * (1-u)^2 * E  =  qu * RELu + qw * RELw + qa * RELrel

where E is the closing_P equation's left side (a free polynomial in
u, w, a|b, s and the six unknowns, mirroring GapWalkClosing's
dP/P0ser/RPser/Qpser definitions verbatim), RELu = 2s*u - (1-s-a)
(resp. 2s*u - (b-1-s)), RELw = (1-u)*w - 1, RELrel = a^2 - AA (resp.
b^2 - BB), and lam is a scalar monomial in s. The full certificate is
RE-VERIFIED as a free polynomial identity before emission; output is
Lean `linear_combination` lines in build/notary_kdelta_row56.lean.txt.

Also re-emits the correct A/B coefficient literals to order 24 and the
per-order coeff lemma statements for the determinant certificate.

Exact command:
  python3 experiments/notary_kdelta_gen5.py \
      | tee build/notary_kdelta_gen5.log
Target machine: gympie (local).  Predicted cost: < 2 min, one core.
Kill/resume: stateless; rerun from scratch.
"""
import json
import os
import sys
import time
from fractions import Fraction

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

s, a, b, u, w = sp.symbols('s a b u w')
X0, X1, X2, X3, X4, X5 = sp.symbols('x0 x1 x2 x3 x4 x5')
UNK = [X0, X1, X2, X3, X4, X5]
UNK_LEAN = ['(jS F 1)', '(jS F 2)', '(jS F 3)', '(JmS F)', '(pS F 2)',
            '(pS F 3)']
AA = 1 - 2 * s - 3 * s ** 2
BB = 1 + 2 * s - 3 * s ** 2

t0 = time.time()
D2 = json.load(open('build/notary_kdelta_data2.json'))


def stage(name):
    print(f"  [{time.time() - t0:6.1f}s] {name}", flush=True)


def fail(msg):
    print(f"FAIL: {msg}", flush=True)
    sys.exit(1)


# ---- the gamma-side expressions, mirroring GapWalkClosing verbatim ----
j1, j2, j3, Jm, p2, p3 = UNK
c1S = -2 * j3 + 8 * Jm + 5 * j1 + 6 * j2 + p3 + 2 * p2
c2S = 2 * Jm + 2 * j1 + 3 * j2 + 2 * p2
c3S = j1 + 2 * j2
c4S = j2


def Qpser(j01, j02):
    return (j01 + 2 * j02 * u - j1 - 2 * j2 * u
            + s ** 2 * (c1S + 2 * c2S * u + 3 * c3S * u ** 2
                        + 4 * c4S * u ** 3))


def RPser():
    return ((2 * j3 - p3) * u
            + Jm * (8 * u ** 2 + 12 * u ** 3 * w)
            + j1 * (4 * u ** 2 + 6 * u ** 3 + 8 * u ** 4 * w)
            + j2 * (4 * u ** 2 + 6 * u ** 3 + 8 * u ** 4 + 10 * u ** 5 * w)
            + p2 * (u ** 2 + 4 * u ** 3 + 3 * u ** 4 + 2 * u ** 5 * w))


def P0ser(p02, pt):
    return p02 * u ** 2 + pt * u ** 3 * w


def dP():
    return 2 * u - 2 * s ** 2 * (1 + u + u ** 2) * (1 + 2 * u)


def lean_poly_in(expr, varmap):
    """Emit a polynomial over the given variable substitution map as a
    Lean expression (integer or rational scalars via numerals)."""
    expr = sp.expand(expr)
    if expr == 0:
        return "0"
    gens = list(varmap.keys())
    p = sp.Poly(expr, *gens)
    parts = []
    for mono, co in p.as_dict().items():
        pq, qq = sp.fraction(sp.nsimplify(co))
        if qq == 1:
            sc = str(pq) if pq >= 0 else f"(-{-pq})"
        else:
            sc = f"(({pq} : ℚ⟦X⟧)/{qq})" if pq >= 0 else \
                 f"((-{-pq} : ℚ⟦X⟧)/{qq})"
        term = [sc]
        for g, k in zip(gens, mono):
            if k == 1:
                term.append(varmap[g])
            elif k >= 2:
                term.append(f"{varmap[g]} ^ {k}")
        parts.append(" * ".join(term))
    return " + ".join(parts)


out = []
CASES = [
    ('int', 5, 'u1', 'a', 4, 1, 4, 6),
    ('int', 6, 'u2', 'b', 4, 1, 4, 6),
    ('bare', 5, 'u1', 'a', 1, 0, 1, 1),
    ('bare', 6, 'u2', 'b', 1, 0, 1, 1),
]
for kind, rowno, uname, relvar, j01, j02, p02, pt in CASES:
    K = kind.capitalize()
    r = rowno - 1
    M = [sp.sympify(D2[f'M_{kind}'][r][c][0])
         + sp.sympify(D2[f'M_{kind}'][r][c][1]) * a
         + sp.sympify(D2[f'M_{kind}'][r][c][2]) * b
         + sp.sympify(D2[f'M_{kind}'][r][c][3]) * a * b for c in range(6)]
    R = (sp.sympify(D2[f'R_{kind}'][r][0])
         + sp.sympify(D2[f'R_{kind}'][r][1]) * a
         + sp.sympify(D2[f'R_{kind}'][r][2]) * b
         + sp.sympify(D2[f'R_{kind}'][r][3]) * a * b)
    row = sp.expand(sum(M[c] * UNK[c] for c in range(6)) - R)

    E = sp.expand(dP() * (P0ser(p02, pt) - p2 * u ** 2 + s ** 2 * RPser())
                  - 2 * u ** 2 * Qpser(j01, j02))
    if uname == 'u1':
        RELu = 2 * s * u - (1 - s - a)
        RELrel = a ** 2 - AA
        rv = a
    else:
        RELu = 2 * s * u - (b - 1 - s)
        RELrel = b ** 2 - BB
        rv = b

    RELw = (1 - u) * w - 1

    # P := lam * (1-u)^2 * E ; find lam = c * s^k matching the clearing.
    # Reduce w first (E has w-degree 1): (1-u)^2*(al + be*w)
    al = sp.expand(E.subs(w, 0))
    be = sp.expand(sp.expand(E - al).coeff(w))
    # (1-u)^2 * E = (1-u)^2 al + (1-u) be * ((1-u) w) ;  (1-u)w = 1 + RELw
    P_red = sp.expand((1 - u) ** 2 * al + (1 - u) * be)
    qw = sp.expand((1 - u) * be)          # cofactor of RELw (pre-lam)
    # fraction-free pseudo-division of P_red by RELu in u:
    #   (2s)^m * P_red = qu * RELu + rem   with polynomial qu, rem
    qu = sp.S(0)
    rem = sp.expand(P_red)
    m = 0
    while True:
        pu = sp.Poly(rem, u)
        d = pu.degree()
        if d < 1:
            break
        lead = pu.coeff_monomial(u ** d)
        qu = sp.expand(2 * s * qu + lead * u ** (d - 1))
        rem = sp.expand(2 * s * rem - lead * u ** (d - 1) * RELu)
        m += 1
    # invariant: (2s)^m * P_red = qu * RELu + rem  (rem u-free)
    # The generator built row = reduce(s^3-ish * (1-u)^2 * E); with the
    # pseudo-division scaling, the exact relation is
    #     scale * row = rem - qa * RELrel,   scale = 2^m * s^(m - k0)
    # where k0 is the row's s-clearing power. Find qa by division.
    k0 = D2[f'rowclear_{kind}'][r]
    if m < k0:
        fail(f"pseudo-division shallower than row clearing ({kind})")
    scale = sp.expand(2 ** m * s ** (m - k0))
    qa, rr = sp.div(sp.Poly(sp.expand(rem - scale * row), rv),
                    sp.Poly(RELrel, rv))
    if sp.expand(rr.as_expr()) != 0:
        fail(f"rel-cofactor remainder nonzero row {rowno} ({kind})")
    qa = qa.as_expr()
    # full re-verification, free polynomial in everything:
    chk = sp.expand((2 * s) ** m * (1 - u) ** 2 * E
                    - (2 * s) ** m * qw * RELw
                    - qu * RELu - qa * RELrel - scale * row)
    if chk != 0:
        fail(f"certificate re-verification failed row {rowno} ({kind})")
    coefE = sp.expand((2 * s) ** m)
    coefW = sp.expand(-(2 * s) ** m * qw)
    coefU = sp.expand(-qu)
    coefREL = sp.expand(-qa)
    # integrality check
    for e in (coefE, coefW, coefU, coefREL, scale):
        for co in sp.Poly(sp.expand(e), s, a, b, u, w, *UNK).as_dict().values():
            if sp.fraction(sp.nsimplify(co))[1] != 1:
                fail(f"non-integer cofactor coefficient row {rowno} ({kind})")
    scale_lean = f"{2 ** m} * X ^ {m - k0}" if m > k0 else f"{2 ** m}"
    stage(f"row {rowno} ({kind}): scale = {scale}, "
          f"sizes qu={len(str(qu))} qw={len(str(qw))} qa={len(str(qa))}")

    # Lean emission
    un = f"Kernel.{uname}"
    wn = "Kernel.w1" if uname == 'u1' else "Kernel.w2"
    Aname = "Kernel.A" if relvar == 'a' else "Kernel.B"
    varmap = {s: "X", a: "Kernel.A", b: "Kernel.B", u: un, w: wn,
              X0: UNK_LEAN[0], X1: UNK_LEAN[1], X2: UNK_LEAN[2],
              X3: UNK_LEAN[3], X4: UNK_LEAN[4], X5: UNK_LEAN[5]}
    eqP = "closing_P_u1 h" if uname == 'u1' else "closing_P_u2 h"
    udef = "Kernel.u1_def" if uname == 'u1' else "Kernel.u2_def"
    wdef = ("Kernel.one_sub_u1_mul_w1" if uname == 'u1'
            else "Kernel.one_sub_u2_mul_w2")
    sq = "Kernel.A_sq" if relvar == 'a' else "Kernel.B_sq"
    # linear_combination: goal lhs-rhs = row. hypotheses as (L - R):
    #  eqP: E = 0 ; udef: 2X*u = rhs -> L-R = RELu ; wdef: (1-u)*w = 1 ->
    #  L-R = RELw ; sq: A*A = AA -> L-R = RELrel (note A*A not A^2).
    coeff_eqP = lean_poly_in(coefE, varmap)
    coeff_udef = lean_poly_in(coefU, varmap)
    coeff_wdef = lean_poly_in(coefW, varmap)
    coeff_sq = lean_poly_in(coefREL, varmap)
    out.append(f"-- walkRow{rowno}{K}  (row {rowno}, {kind}): prove the goal")
    out.append(f"-- scaled by ({scale_lean}), then cancel that factor:")
    out.append(f"--   have h : ({scale_lean} : _) * LHS = ({scale_lean}) * RHS := by")
    out.append(f"  linear_combination ({coeff_eqP}) * ({eqP}) + "
               f"({coeff_udef}) * {udef} + ({coeff_wdef}) * {wdef} + "
               f"({coeff_sq}) * {sq}")
    out.append("")

# A/B literals to order 24 (correct; the earlier docstring hand-copy
# was wrong from order 7)
NS = 26


def s_sqrt(t):
    o = [Fraction(0)] * NS
    o[0] = Fraction(1)
    for n in range(1, NS):
        o[n] = (t[n] - sum(o[i] * o[n - i] for i in range(1, n))) / 2
    return o


tA = [Fraction(0)] * NS
tA[0], tA[1], tA[2] = Fraction(1), Fraction(-2), Fraction(-3)
tB = [Fraction(0)] * NS
tB[0], tB[1], tB[2] = Fraction(1), Fraction(2), Fraction(-3)
SER_A, SER_B = s_sqrt(tA), s_sqrt(tB)
out.append("-- A coefficients 0..24: " + ", ".join(str(x)
                                                   for x in SER_A[:25]))
out.append("-- B coefficients 0..24: " + ", ".join(str(x)
                                                   for x in SER_B[:25]))

with open('build/notary_kdelta_row56.lean.txt', 'w') as f:
    f.write("\n".join(out) + "\n")
stage("wrote build/notary_kdelta_row56.lean.txt")
print(f"ALL PASS ({time.time() - t0:.1f}s)")
