#!/usr/bin/env python3
"""Notary piece K, wave K-delta generator, stage 2: the cleared system.

Builds on stage 1 (`notary_kdelta_gen.py`, `build/notary_kdelta_data.json`).
Computes and verifies, per start:

  d4. the CLEARED polynomial rows: each of the six closing equations
      multiplied by its clearing factor — `(2s)^4` for the root rows (1),(2)
      [q-degree 4], `1` for rows (3),(4), and `(1-u_i)^2 (2s)^k` for the
      cleared P-rows (5),(6) (two w-factors can meet in a product; minimal k
      found by trial) — so that every coefficient of every unknown, and the
      right side, is a POLYNOMIAL in s over the basis (1, A, B, AB).
      Emitted as M[r][c] and R[r] 4-tuples of polynomial strings; verified
      numerically against the walk series (M.x_walk = R to s-order ~22).
  d5. the closed forms satisfy the cleared system, in the exact shape the
      Lean `ring` identity will take: for each row r,
        sum_c M[r][c] * s^(E-e_c) * (D/d_c) * num_c  =  s^E * D * R[r]
      identically in the 4-tuple algebra (E = max shift, D = lcm of the six
      unit denominators, from stage 1).  Sizes reported.
  d6. the determinant certificate FOR THE CLEARED SYSTEM: det of the 6x6
      polynomial matrix as a truncated series — valuation and leading
      coefficient (the number DepthOneKernelUnique pins).  Computed by
      Leibniz over 720 permutations in exact Fractions.
  d7. low-coefficient certificates: coeff n (num_c) = 0 for n < e_c
      (the divX definition guards), asserted from the series.

Output: build/notary_kdelta_data2.json + report.
Exact command:
  python3 experiments/notary_kdelta_gen2.py \
      | tee build/notary_kdelta_gen2.log
Target machine: gympie (local).  Predicted cost: ~3-6 min, one core.
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
from severance_w2_kernel import (                                # noqa: E402
    AA, BB, ONE, ZERO, K, add, sub, smul, mul, inv, pw, poly, U1, U2, Y,
    J0_P0, s)
import severance_w2_kernel as W2                                 # noqa: E402
from depth1_gap_walk import transitions                          # noqa: E402

t0 = time.time()
OUT = {}
D1 = json.load(open('build/notary_kdelta_data.json'))


def stage(name):
    print(f"  [{time.time() - t0:6.1f}s] {name}", flush=True)


def fail(msg):
    print(f"FAIL: {msg}", flush=True)
    sys.exit(1)


# --------------------------------------------------- the cleared equations
def equations_cleared(X, J0c, P0fn, J0_1):
    """As in notary_k_measure m5: rows 5,6 multiplied by D'(u_i)."""
    j1, j2, j3, Jm, p2, p3 = X
    c1 = add(add(smul(-2, j3), smul(8, Jm)),
             add(add(smul(5, j1), smul(6, j2)), add(p3, smul(2, p2))))
    c2 = add(add(smul(2, Jm), smul(2, j1)), add(smul(3, j2), smul(2, p2)))
    c3 = add(j1, smul(2, j2))
    c4 = j2
    RJ = [ZERO, c1, c2, c3, c4]
    RJp = [c1, smul(2, c2), smul(3, c3), smul(4, c4)]
    J0 = [K(v) for v in J0c]
    J0p = [K((i + 1) * J0c[i + 1]) for i in range(len(J0c) - 1)]

    def Q(u):
        return sub(add(poly(u, J0), mul(Y, poly(u, RJ))),
                   add(mul(j1, u), mul(j2, mul(u, u))))

    def Qp(u):
        return sub(add(poly(u, J0p), mul(Y, poly(u, RJp))),
                   add(j1, smul(2, mul(j2, u))))

    def Dp(u):
        oo = add(add(ONE, u), mul(u, u))
        return sub(smul(2, u), smul(2, mul(Y, mul(oo, add(ONE, smul(2, u))))))

    def RP(u):
        iu = inv(sub(ONE, u))
        t = mul(sub(smul(2, j3), p3), u)
        t = add(t, mul(Jm, add(smul(8, pw(u, 2)), mul(smul(12, pw(u, 3)), iu))))
        t = add(t, mul(j1, add(add(smul(4, pw(u, 2)), smul(6, pw(u, 3))),
                               mul(smul(8, pw(u, 4)), iu))))
        t = add(t, mul(j2, add(add(smul(4, pw(u, 2)),
                                   add(smul(6, pw(u, 3)), smul(8, pw(u, 4)))),
                               mul(smul(10, pw(u, 5)), iu))))
        t = add(t, mul(p2, add(add(pw(u, 2), add(smul(4, pw(u, 3)),
                                                 smul(3, pw(u, 4)))),
                               mul(smul(2, pw(u, 5)), iu))))
        return t

    out = [Q(U1), Q(U2),
           sub(sub(j1, K(J0_1)), mul(Y, add(j3, c1))),
           sub(mul(Jm, sub(ONE, smul(9, Y))), Q(K(1)))]
    for u in (U1, U2):
        cleared = sub(mul(Dp(u), add(sub(P0fn(u), mul(p2, pw(u, 2))),
                                     mul(Y, RP(u)))),
                      smul(2, mul(pw(u, 2), Qp(u))))
        out.append(cleared)
    return out


def tup_cancel(t):
    return tuple(sp.cancel(e) for e in t)


def tup_is_poly(t):
    for e in t:
        if e == 0:
            continue
        _, den = sp.fraction(sp.together(sp.cancel(e)))
        if sp.degree(den, s) != 0:
            return False
    return True


def clear_row(row, extra):
    """Multiply row by `extra` (tuple), then minimal s^k to make it poly."""
    row = tup_cancel(mul(extra, row) if extra is not None else row)
    for k in range(0, 16):
        cand = tup_cancel(mul(K(s ** k), row))
        if tup_is_poly(cand):
            return k, tuple(sp.expand(e) for e in cand)
    fail("no s-power clears the row")


ONE_MINUS = {0: sub(ONE, U1), 1: sub(ONE, U2)}

# --------------------------------------------------- walk series for checks
NS = 40


def sz():
    return [Fraction(0)] * NS


def s_mul(a, b):
    out = sz()
    for i, x in enumerate(a):
        if x:
            for j in range(NS - i):
                if b[j]:
                    out[i + j] += x * b[j]
    return out


def s_from_poly(expr):
    out = sz()
    if expr == 0:
        return out
    p = sp.Poly(sp.expand(expr), s)
    for (k,), co in p.as_dict().items():
        if k < NS:
            out[k] = Fraction(int(sp.numer(co)), int(sp.denom(co)))
    return out


def s_sqrt(target):
    out = sz()
    out[0] = Fraction(1)
    for n in range(1, NS):
        out[n] = (target[n] - sum(out[i] * out[n - i]
                                  for i in range(1, n))) / 2
    return out


ONE_S = sz()
ONE_S[0] = Fraction(1)
SER_A = s_sqrt(s_from_poly(AA))
SER_B = s_sqrt(s_from_poly(BB))
BASIS = [ONE_S, SER_A, SER_B, s_mul(SER_A, SER_B)]


def tup_to_series(t):
    out = sz()
    for e, b in zip(t, BASIS):
        if e != 0:
            out = [x + y for x, y in zip(out, s_mul(s_from_poly(e), b))]
    return out


YO = NS // 2 + 1
CAP = 2 * YO + 10
ROWS_T = {}
for g in range(1, CAP + 1):
    for c in 'JP':
        ROWS_T[(g, c)] = transitions(g, c, CAP)


def walk_x(kind):
    d = (dict(j01=4, j02=1, p02=4, pt=6) if kind == 'int'
         else dict(j01=1, j02=0, p02=1, pt=1))
    start = {(1, 'J'): d['j01'], (2, 'J'): d['j02'], (2, 'P'): d['p02']}
    for g in range(3, CAP + 1):
        start[(g, 'P')] = d['pt']
    start = {k: v for k, v in start.items() if v}
    j = [[0] * (CAP + 1) for _ in range(YO + 1)]
    p = [[0] * (CAP + 1) for _ in range(YO + 1)]
    for (g, c), v in start.items():
        (j if c == 'J' else p)[0][g] = v
    for m in range(YO):
        for g in range(1, CAP + 1):
            for c, arr in (('J', j), ('P', p)):
                v = arr[m][g]
                if not v:
                    continue
                for (gp, cp), w in ROWS_T[(g, c)].items():
                    (j if cp == 'J' else p)[m + 1][gp] += v * w

    def even(f):
        out = sz()
        for m in range(YO + 1):
            if 2 * m < NS:
                out[2 * m] = Fraction(f(m))
        return out
    return [even(lambda m: j[m][1]), even(lambda m: j[m][2]),
            even(lambda m: j[m][3]),
            even(lambda m: sum(j[m][g] for g in range(3, 2 * m + 3))),
            even(lambda m: p[m][2]), even(lambda m: p[m][3])]


# ------------------------------------------------------------------ main
NAMES = ['j1', 'j2', 'j3', 'Jm', 'p2', 'p3']
CHK = NS - 6
for kind in ('int', 'bare'):
    print(f"== d4-d7 ({kind})", flush=True)
    J0c, P0fn, J0_1 = J0_P0(kind)
    base = equations_cleared([ZERO] * 6, J0c, P0fn, J0_1)
    cols = []
    for c in range(6):
        e = [ZERO] * 6
        e[c] = ONE
        cols.append([tup_cancel(sub(v, b)) for v, b in
                     zip(equations_cleared(e, J0c, P0fn, J0_1), base)])
    # rows: clear factors
    M_pol = [[None] * 6 for _ in range(6)]
    R_pol = [None] * 6
    ks = []
    for r in range(6):
        extra = None
        if r in (4, 5):
            w = ONE_MINUS[r - 4]
            extra = mul(w, w)
        elif r in (0, 1):
            extra = None                    # s^k alone suffices
        # clear R first to find k, then apply the same factor to all entries
        kR, Rp = clear_row(smul(-1, base[r]), extra)
        kM, Mps = 0, []
        for c in range(6):
            kc, Mp = clear_row(cols[c][r], extra)
            kM = max(kM, kc)
            Mps.append((kc, Mp))
        k = max(kR, kM)
        # rows 1,2 keep half-integer entries from the (2s)-clearing: double
        # them so every emitted coefficient is an integer (Lean numerals).
        dbl = 2 if r in (0, 1) else 1
        R_pol[r] = tuple(sp.expand(dbl * e * s ** (k - kR)) for e in Rp)
        for c in range(6):
            kc, Mp = Mps[c]
            M_pol[r][c] = tuple(sp.expand(dbl * e * s ** (k - kc))
                                for e in Mp)
        ks.append(k)
        mx = max(len(str(e)) for t in ([R_pol[r]] + M_pol[r]) for e in t)
        print(f"    row {r + 1}: s^{k}"
              f"{' (1-u)^2' if r in (4, 5) else ''}, max entry chars {mx}")
    stage(f"d4: rows cleared to polynomials ({kind})")

    # numeric: M.x_walk = R
    XW = walk_x(kind)
    for r in range(6):
        acc = sz()
        for c in range(6):
            t = s_mul(tup_to_series(M_pol[r][c]), XW[c])
            acc = [x + y for x, y in zip(acc, t)]
        d = [x - y for x, y in zip(acc, tup_to_series(R_pol[r]))]
        if any(x != 0 for x in d[:CHK]):
            fail(f"walk fails cleared row {r + 1} ({kind})")
    stage(f"d4: walk satisfies the cleared system to s-order {CHK} ({kind})")

    # d5: closed forms satisfy it, as the Lean ring identity
    ent = D1[f'entries_{kind}']
    es = [e['e'] for e in ent]
    dens = [sp.sympify(e['den']) for e in ent]
    nums = [[sp.sympify(n) for n in e['nums']] for e in ent]
    E = max(es)
    D = sp.S(1)
    for d in dens:
        D = sp.lcm(D, d)
    D = sp.expand(D)
    OUT[f'E_{kind}'] = E
    OUT[f'D_{kind}'] = str(D)
    print(f"    E={E}, D chars {len(str(D))}")
    for r in range(6):
        acc = (sp.S(0),) * 4
        for c in range(6):
            scale = sp.expand(s ** (E - es[c]) * sp.cancel(D / dens[c]))
            acc = add(acc, mul(M_pol[r][c], smul(scale, tuple(nums[c]))))
        target = smul(sp.expand(s ** E * D), R_pol[r])
        diff = sub(acc, target)
        if any(sp.expand(e) != 0 for e in diff):
            fail(f"closed forms fail cleared row {r + 1} ({kind})")
    stage(f"d5: closed forms satisfy the cleared system exactly ({kind})")

    # d6: det certificate for the cleared system
    Mser = [[tup_to_series(M_pol[r][c]) for c in range(6)] for r in range(6)]
    det = sz()
    for perm in permutations(range(6)):
        sign = 1
        pl = list(perm)
        for i in range(6):
            for jx in range(i + 1, 6):
                if pl[i] > pl[jx]:
                    sign = -sign
        t = ONE_S
        for r in range(6):
            t = s_mul(t, Mser[r][perm[r]])
        det = [x + sign * y for x, y in zip(det, t)]
    v = next((i for i, x in enumerate(det) if x != 0), None)
    if v is None or v > CHK:
        fail(f"cleared det vanishes to order {CHK} ({kind})")
    print(f"    cleared det: valuation {v}, lead {det[v]}, "
          f"next {det[v + 1]}, {det[v + 2]}")
    OUT[f'det_{kind}'] = dict(valuation=v, lead=str(det[v]))
    stage(f"d6: cleared-system det certificate ({kind})")

    # d7: divX guards
    for c in range(6):
        ser = tup_to_series(tuple(nums[c]))
        for n in range(es[c]):
            if ser[n] != 0:
                fail(f"num low coeff nonzero: {kind} {NAMES[c]} n={n}")
    stage(f"d7: divX low-coefficient guards ({kind})")

    OUT[f'M_{kind}'] = [[[str(e) for e in M_pol[r][c]] for c in range(6)]
                        for r in range(6)]
    OUT[f'R_{kind}'] = [[str(e) for e in R_pol[r]] for r in range(6)]
    OUT[f'rowclear_{kind}'] = ks

with open('build/notary_kdelta_data2.json', 'w') as f:
    json.dump(OUT, f, indent=1)
stage("dumped build/notary_kdelta_data2.json")
print(f"ALL PASS ({time.time() - t0:.1f}s)")
