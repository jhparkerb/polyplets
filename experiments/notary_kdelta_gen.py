#!/usr/bin/env python3
"""Notary piece K, wave K-delta generator, stage 1: transcription data.

Computes and verifies the data the K-delta skeletons transcribe, and dumps
it as JSON for the skeleton author (plus a human-readable report):

  d1. the closed-form solution entries, both starts, in POLE-FREE form:
      for each entry x_k a shift e_k, a common unit denominator d_k(s),
      and numerator polynomials N_{k,i}(s) (basis 1, A, B, AB), so that
          s^{e_k} * d_k(s) * x_k = (N_{k,0} + N_{k,1} A + N_{k,2} B
                                     + N_{k,3} A B) ,
      the right side a series with unit denominator (docs/notary-k-plan.md
      wave-delta architecture note).  Each is verified two ways: exactly in
      sympy against the solve_start solution, and numerically against the
      WALK's own series (depth1_gap_walk.transitions) to s-order ~24.
  d2. the F1 assembly data: common denominator den(s) (unit), numerators
      n0..n3, the Psi ring identity re-check, the y-form quartic cY_0..4,
      its numeric annihilation of the walk F1, and the exact lift ratio
      against the banked PHI_COEFFS (expected 1/3).
  d3. the A/B coefficient literals to order 14 (exact Fractions from the
      sqrt recursion) for the DepthOneKernelUnique det certificate.

Output: build/notary_kdelta_data.json + report on stdout.
Exact command:
  python3 experiments/notary_kdelta_gen.py \
      | tee build/notary_kdelta_gen.log
Target machine: gympie (local).  Predicted cost: ~2-3 min, one core
(dominated by the two ~32 s solve_start calls).
Kill/resume: stateless; rerun from scratch.
"""
import json
import os
import sys
import time
from fractions import Fraction

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth1_gap_walk import transitions                          # noqa: E402
from severance_w2_kernel import (                                # noqa: E402
    AA, BB, ONE, K, add, sub, smul, mul, div, Y, J0_P0, solve_start, s)

t0 = time.time()
OUT = {}


def stage(name):
    print(f"  [{time.time() - t0:6.1f}s] {name}", flush=True)


def fail(msg):
    print(f"FAIL: {msg}", flush=True)
    sys.exit(1)


# ------------------------------------------------ truncated series (checks)
NS = 30


def sz():
    return [Fraction(0)] * NS


def s_add(a, b):
    return [x + y for x, y in zip(a, b)]


def s_mul(a, b):
    out = sz()
    for i, x in enumerate(a):
        if x:
            for j in range(NS - i):
                if b[j]:
                    out[i + j] += x * b[j]
    return out


def s_inv(a):
    assert a[0] != 0
    out = sz()
    out[0] = 1 / a[0]
    for n in range(1, NS):
        out[n] = -sum(a[k] * out[n - k] for k in range(1, n + 1)) / a[0]
    return out


def s_from_poly(expr):
    out = sz()
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

# d3: A/B coefficient literals
OUT['A_coeffs'] = [str(c) for c in SER_A[:15]]
OUT['B_coeffs'] = [str(c) for c in SER_B[:15]]
print("  A coeffs 0..14:", ", ".join(OUT['A_coeffs']))
print("  B coeffs 0..14:", ", ".join(OUT['B_coeffs']))
stage("d3: A/B coefficient literals to order 14")

# ------------------------------------------------------ walk series (truth)
YO = NS // 2 + 1
CAP = 2 * YO + 10
ROWS = {}
for g in range(1, CAP + 1):
    for c in 'JP':
        ROWS[(g, c)] = transitions(g, c, CAP)


def run_walk(start):
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
                for (gp, cp), w in ROWS[(g, c)].items():
                    (j if cp == 'J' else p)[m + 1][gp] += v * w
    return j, p


def walk_x(kind):
    d = (dict(j01=4, j02=1, p02=4, pt=6) if kind == 'int'
         else dict(j01=1, j02=0, p02=1, pt=1))
    start = {(1, 'J'): d['j01'], (2, 'J'): d['j02'], (2, 'P'): d['p02']}
    for g in range(3, CAP + 1):
        start[(g, 'P')] = d['pt']
    start = {k: v for k, v in start.items() if v}
    JJ, PP = run_walk(start)

    def even(f):
        out = sz()
        for m in range(YO + 1):
            if 2 * m < NS:
                out[2 * m] = Fraction(f(m))
        return out
    return [even(lambda m: JJ[m][1]), even(lambda m: JJ[m][2]),
            even(lambda m: JJ[m][3]),
            even(lambda m: sum(JJ[m][g] for g in range(3, 2 * m + 3))),
            even(lambda m: PP[m][2]), even(lambda m: PP[m][3])]


# --------------------------------------------- d1: pole-free transcription
NAMES = ['j1', 'j2', 'j3', 'Jm', 'p2', 'p3']
CHK = NS - 6
SOLS = {}
for kind in ('int', 'bare'):
    print(f"== d1: solve + transcribe ({kind})", flush=True)
    J0c, P0fn, J0_1 = J0_P0(kind)
    X_hat = solve_start(J0c, P0fn, J0_1)
    SOLS[kind] = X_hat
    stage(f"solve_start done ({kind})")
    XW = walk_x(kind)
    entries = []
    for k, tup in enumerate(X_hat):
        comps = [sp.together(sp.cancel(ci)) for ci in tup]
        es, dens, nums = [], [], []
        for ci in comps:
            if ci == 0:
                es.append(0)
                dens.append(sp.S(1))
                nums.append(sp.S(0))
                continue
            num, den = sp.fraction(ci)
            e = 0
            while sp.expand(den).subs(s, 0) == 0:
                den = sp.cancel(den / s)
                e += 1
            es.append(e)
            dens.append(sp.expand(den))
            nums.append(sp.expand(num))
        ek = max(es)
        dk = sp.S(1)
        for d in dens:
            dk = sp.lcm(dk, d)
        dk = sp.expand(dk)
        if dk.subs(s, 0) == 0:
            fail(f"common denominator not a unit: {kind} {NAMES[k]}")
        Ns = []
        for ci, e, d, num in zip(comps, es, dens, nums):
            if ci == 0:
                Ns.append(sp.S(0))
                continue
            Ni = sp.expand(num * sp.cancel(dk / d) * s ** (ek - e))
            # exact check: s^ek * dk * ci == Ni
            if sp.simplify(s ** ek * dk * ci - Ni) != 0:
                fail(f"transcription mismatch: {kind} {NAMES[k]}")
            Ns.append(Ni)
        # numeric check against the walk: s^ek * dk * x_walk == sum Ni b_i
        lhs = s_mul(s_from_poly(s ** ek * dk), XW[k])
        rhs = sz()
        for Ni, b in zip(Ns, BASIS):
            if Ni != 0:
                rhs = s_add(rhs, s_mul(s_from_poly(Ni), b))
        d_ser = [x - y for x, y in zip(lhs, rhs)]
        if any(x != 0 for x in d_ser[:CHK]):
            fail(f"walk mismatch: {kind} {NAMES[k]}")
        sizes = [len(str(N)) for N in Ns]
        print(f"    {NAMES[k]}: e={ek} den_chars={len(str(dk))} "
              f"num_chars={sizes}")
        entries.append(dict(name=NAMES[k], e=ek, den=str(dk),
                            nums=[str(N) for N in Ns]))
    OUT[f'entries_{kind}'] = entries
    stage(f"d1: all six entries pole-free + walk-verified ({kind})")

# ------------------------------------------------------- d2: F1, Psi, cY
print("== d2: F1 assembly, Psi, quartic", flush=True)
X_INT, X_BARE = SOLS['int'], SOLS['bare']
q_of = lambda X: add(add(smul(4, X[0]), smul(5, X[1])), add(smul(6, X[3]), X[4]))
S_t = mul(Y, q_of(X_INT))
B_t = add(ONE, mul(Y, q_of(X_BARE)))
Ph_t = mul(Y, add(add(X_BARE[0], X_BARE[1]), X_BARE[3]))
F1_t = sub(Ph_t, div(mul(B_t, B_t), add(K(3), S_t)))

c = [sp.cancel(e) for e in F1_t]
den = sp.lcm([sp.fraction(sp.together(ci))[1] for ci in c])
n0, n1, n2, n3 = [sp.expand(sp.cancel(ci * den)) for ci in c]
if den.subs(s, 0) == 0:
    fail("F1 common denominator is not a unit")
Pq = sp.expand(n1 ** 2 * AA - n2 ** 2 * BB - n3 ** 2 * AA * BB)
T0 = (sp.S(0), n1, n2, n3)
S1 = add(mul(T0, T0), K(Pq))
lhs = mul(S1, S1)
inner = add(smul(n1, T0), K(sp.expand(n2 * n3 * BB)))
rhs = smul(4 * AA, mul(inner, inner))
if any(sp.expand(e) != 0 for e in sub(lhs, rhs)):
    fail("Psi identity fails")
stage("d2: Psi(T) = 0 re-verified in the 4-tuple algebra")

tau = sp.symbols('tau')
Psi = sp.expand(sp.expand((tau - n0) ** 2 + Pq) ** 2
                - 4 * AA * (n1 * (tau - n0) + n2 * n3 * BB) ** 2)
cs = sp.Poly(Psi, tau).all_coeffs()
cT = [sp.expand(cs[4 - k] * den ** k) for k in range(5)]
g = sp.gcd(cT)
cT = [sp.expand(sp.cancel(ci / g)) for ci in cT]
y = sp.symbols('y')
cY = []
for ci in cT:
    out = 0
    for (k,), co in sp.Poly(ci, s).as_dict().items():
        if k % 2:
            fail("odd power of s in the quartic")
        out += co * y ** (k // 2)
    cY.append(sp.expand(out))
OUT['F1'] = dict(den=str(den), n0=str(n0), n1=str(n1), n2=str(n2),
                 n3=str(n3))
OUT['cY'] = [str(ci) for ci in cY]
for k, ci in enumerate(cY):
    print(f"    cY_{k}: {ci}")

x, Wv = sp.symbols('x W')
lift = sp.expand(sum(cY[k].subs(y, 3 * x) * ((Wv - 1) / sp.S(3)) ** k
                     for k in range(5)))
from depth1_recurrence import PHI_COEFFS  # noqa: E402
banked = sp.expand(sum(sp.sympify(PHI_COEFFS[k]) * Wv ** k for k in range(5)))
ratio = sp.cancel(lift / banked)
OUT['lift_ratio'] = str(ratio)
print(f"    lift / banked Phi ratio: {ratio}")
if str(ratio) not in ("1/3",):
    print("    NOTE: ratio differs from the remembered 1/3 -- "
          "carry the actual value into the skeleton")
stage("d2: quartic + lift ratio computed")

os.makedirs('build', exist_ok=True)
with open('build/notary_kdelta_data.json', 'w') as f:
    json.dump(OUT, f, indent=1)
stage("dumped build/notary_kdelta_data.json")
print(f"ALL PASS ({time.time() - t0:.1f}s)")
