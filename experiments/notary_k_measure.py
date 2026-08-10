#!/usr/bin/env python3
"""Notary piece K, measurement 0: price the cleared 6x6 system and pre-verify
the planned Lean statement set.

Campaign Notary piece K (docs/notary-kernel-scoping.md): formalize the kernel
method at all orders, ending in `Phi(x, N(x)) = 0` exactly in Lean.  Before any
skeleton is written this script measures the objects the decomposition depends
on and numerically verifies every statement class the skeletons will assert.

  m1. row values: the generic (g >= 3) and boundary transition rows and start
      vectors, printed as the literal statements of GapWalkRowVals.lean and
      re-asserted against depth1_gap_walk.transitions;
  m2. P-tail constancy: min g0(m) with p_m(g) constant for g >= g0 (exact cone
      values), vs. the candidate threshold the Lean induction will carry;
  m3. the two master double-series identities, coefficient-wise in (y, u):
        D.J3 = u^2 Q             (J-side)
        D.(P3 - 2 J3) = u^2 (P0 - p2 u^2 - 2 J3 + y R_P)   (P-side)
  m4. sqrt recursions A, B; u1, u2 as shifted series; kernel identities
      u^2 = y (1+u+u^2)^2 to s-order 40; agreement with the sympy roots;
  m5. the CLEARED 6x6 system (rows 5,6 multiplied through by D'(u_i)):
      the walk's own series satisfy it (both starts), the sympy solution
      satisfies it, det valuation + leading coefficient (the Lean uniqueness
      certificate), and adj-based sanity that det != 0;
  m6. transcription sizes: the 6 solution entries per start as (num, den)
      pairs over Q(s) per basis component 1, A, B, AB; den(0) != 0 asserts
      (units in Q[[s]]); char sizes for the agent briefs;
  m7. the elimination identity Psi(T) = 0 in the 4-tuple algebra, the y-form
      quartic cY_k, the numeric check sum_k cY_k(s^2) F1^k = 0, and the exact
      scale linking sum_k cY_k(3x) ((W-1)/3)^k to the banked Phi(x, W).

Exact command:
  python3 experiments/notary_k_measure.py | tee build/notary_k_measure.log
Target machine: gympie (local).  Predicted cost: ~3-6 min, one core, < 1 GB
(dominated by the two ~32 s solve_start calls and the truncated-series det).
Kill/resume: stateless; rerun from scratch.
"""
import os
import sys
import time
from fractions import Fraction
from itertools import permutations

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth1_gap_walk import transitions                          # noqa: E402
import severance_w2_kernel as W2                                 # noqa: E402
from severance_w2_kernel import (                                # noqa: E402
    AA, BB, ONE, ZERO, K, add, sub, smul, mul, div, inv, pw, poly,
    U1, U2, Y, J0_P0, solve_start, s)

NS = 56                       # s-length of truncated-series arithmetic
EMARGIN = 14                  # Laurent margin: per-basis-component s-poles
VNS = NS - EMARGIN            # results of tup_to_ser are exact to s^(VNS-1)
YO = 14                       # y-orders of walk data (s-order 28)
UO = 44                       # u-orders checked in the master identities
BULK = {-2: 1, -1: 2, 0: 3, 1: 2, 2: 1}

t0 = time.time()


def stage(name):
    print(f"  [{time.time() - t0:7.2f}s] {name}", flush=True)


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


# ---------------------------------------------------------------- series model
# Q[[s]] mod s^NS as lists of Fraction, length NS.

def sz():
    return [Fraction(0)] * NS


def s_add(a, b):
    return [x + y for x, y in zip(a, b)]


def s_sub(a, b):
    return [x - y for x, y in zip(a, b)]


def s_scale(k, a):
    return [k * x for x in a]


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
        acc = Fraction(0)
        for i in range(1, n + 1):
            acc += a[i] * out[n - i]
        out[n] = -acc / a[0]
    return out


def s_shift_down(a, k):
    """a / s^k, asserting the low coefficients vanish."""
    assert all(x == 0 for x in a[:k]), a[:k]
    return a[k:] + [Fraction(0)] * k


def s_sqrt(target):
    """c with c^2 = target, c[0] = 1 (target[0] = 1)."""
    assert target[0] == 1
    c = sz()
    c[0] = Fraction(1)
    for n in range(1, NS):
        acc = Fraction(0)
        for i in range(1, n):
            acc += c[i] * c[n - i]
        c[n] = (target[n] - acc) / 2
    return c


def s_from_poly(expr):
    """Series of a polynomial in s (sympy expr)."""
    p = sp.Poly(sp.expand(expr), s)
    out = sz()
    for (k,), co in p.as_dict().items():
        if k < NS:
            q = sp.Rational(co)
            out[k] = Fraction(int(q.p), int(q.q))
    return out


def rat_split(expr):
    """num, den0, e with expr = num / (s^e den0), den0(0) != 0."""
    num, den = sp.fraction(sp.together(sp.cancel(expr)))
    e = 0
    while den.subs(s, 0) == 0:
        den = sp.cancel(den / s)
        e += 1
    return num, den, e


def s_from_rat(expr):
    """Series of a rational function of s with den(0) != 0."""
    num, den, e = rat_split(expr)
    if e:
        fail(f"non-unit denominator in Q[[s]]: {expr}")
    return s_mul(s_from_poly(num), s_inv(s_from_poly(den)))


# the two square roots and the kernel roots, as recursions (the Lean route)
SER_AA = s_from_poly(AA)
SER_BB = s_from_poly(BB)
SER_A = s_sqrt(SER_AA)
SER_B = s_sqrt(SER_BB)
ONE_S = s_from_poly(sp.S(1))
SER_S = s_from_poly(s)
SER_Y = s_from_poly(s ** 2)


def tup_to_ser(t):
    """(c0, c1, c2, c3) over Q(s) -> series c0 + c1 A + c2 B + c3 A B.

    Individual components may carry s-poles (up to EMARGIN) that cancel in
    the combination; work in a Laurent window and assert regularity.  The
    result is exact to s^(VNS-1); entries above that are truncation garbage.
    """
    total = [Fraction(0)] * (NS + EMARGIN)     # index i <-> s^(i - EMARGIN)
    basis = (None, SER_A, SER_B, s_mul(SER_A, SER_B))
    for comp, bser in zip(t, basis):
        if comp == 0:
            continue
        num, den0, e = rat_split(comp)
        if e > EMARGIN:
            fail(f"pole order {e} exceeds Laurent margin: {comp}")
        cser = s_mul(s_from_poly(num), s_inv(s_from_poly(den0)))
        if bser is not None:
            cser = s_mul(cser, bser)
        for i in range(NS):
            idx = i + EMARGIN - e
            if idx < NS + EMARGIN:
                total[idx] += cser[i]
    if any(x != 0 for x in total[:EMARGIN]):
        fail("Laurent tail does not cancel in tup_to_ser")
    return total[EMARGIN:]


# ------------------------------------------------------- m1: the row values
print("== m1: row values (GapWalkRowVals statement set)", flush=True)

GPMAX = 60


def bulk_at(g, gp):
    return BULK.get(gp - g, 0)


def claimed_row(g, c, gp, cp):
    """The closed-form transition value the Lean lemmas will state."""
    if g >= 3:
        if c == 'P':
            if gp == 1:
                return (1 if g == 3 else 0) if cp == 'J' else 0
            v = bulk_at(g, gp)
            return v if cp == 'P' else 0
        # J-source
        if gp == 1:
            return (8 - bulk_at(g, 1) if cp == 'J' else 0)
        if gp == 2:
            base = 2 + bulk_at(g, 2) if cp == 'J' else 8 - 2 * bulk_at(g, 2)
            return base
        # gp >= 3
        if cp == 'J':
            return bulk_at(g, gp)
        return 12 - 2 * bulk_at(g, gp)
    # boundary rows, from severance_w2_kernel.BOUNDARY
    head, tail_from, tw = W2.BOUNDARY[(g, c)]
    v = head.get((gp, cp), 0)
    if cp == 'P' and gp >= tail_from:
        v += tw
    return v


bad = 0
for g in list(range(1, 30)):
    c_list = ['J', 'P']
    for c in c_list:
        row = transitions(g, c, GPMAX)
        for gp in range(1, GPMAX + 1):
            for cp in c_list:
                want = claimed_row(g, c, gp, cp)
                got = row.get((gp, cp), 0)
                if want != got:
                    bad += 1
                    print(f"  MISMATCH row ({g},{c}) -> ({gp},{cp}): "
                          f"claimed {want} actual {got}")
if bad:
    fail(f"{bad} row-value mismatches")
stage("generic + boundary closed forms match transitions, g <= 29, gp <= 60")

# start vectors (dp_int of the reference; asserted in W2.check_walk too)
W2.check_walk()
stage("check_walk(): rows and start vectors re-asserted verbatim")

# ------------------------------------------- m2: walk data and tail threshold
print("== m2: exact walk data, P-tail constancy", flush=True)

CAP = 2 * YO + NS + 10        # cone: g + 2m <= CAP exact for g <= NS+10


def run_walk(start):
    j = [[0] * (CAP + 1) for _ in range(YO + 1)]
    p = [[0] * (CAP + 1) for _ in range(YO + 1)]
    for (g, c), v in start.items():
        (j if c == 'J' else p)[0][g] = v
    rows = {}
    for g in range(1, CAP + 1):
        for c in 'JP':
            rows[(g, c)] = transitions(g, c, CAP)
    for m in range(YO):
        for g in range(1, CAP + 1):
            for c, arr in (('J', j), ('P', p)):
                v = arr[m][g]
                if not v:
                    continue
                for (gp, cp), w in rows[(g, c)].items():
                    (j if cp == 'J' else p)[m + 1][gp] += v * w
    return j, p


start_int = {(1, 'J'): 4, (2, 'J'): 1, (2, 'P'): 4}
for g in range(3, CAP + 1):
    start_int[(g, 'P')] = 6
start_bare = {(1, 'J'): 1}
for g in range(2, CAP + 1):
    start_bare[(g, 'P')] = 1

JI, PI = run_walk(start_int)
JB, PB = run_walk(start_bare)
stage(f"walk run to y-order {YO}, cap {CAP}, both starts")

for name, JJ in (("int", JI), ("bare", JB)):
    for m in range(YO + 1):
        for g in range(2 * m + 3, CAP + 1):
            if JJ[m][g]:
                fail(f"J-support violated ({name}) m={m} g={g}")
stage("J-support <= 2m+2 confirmed, both starts")

print("  P-tail thresholds (min g0 with p_m constant on [g0, cone edge]):")
for name, PP in (("int", PI), ("bare", PB)):
    th = []
    for m in range(YO + 1):
        edge = CAP - 2 * m - 2
        g0 = edge
        while g0 > 1 and PP[m][g0 - 1] == PP[m][edge]:
            g0 -= 1
        th.append(g0)
        if g0 > 2 * m + 3:
            fail(f"P-tail threshold {g0} exceeds 2m+3 at m={m} ({name})")
    print(f"    {name}: {th}  (candidate bound 2m+3: "
          f"{[2 * m + 3 for m in range(YO + 1)]})")
stage("P-tail constant from g >= 2m+3 (<= candidate bound), both starts")

# ---------------------------------- m3: master identities, coefficient-wise


def col(arr, g, m):
    return arr[m][g] if 1 <= g <= CAP else 0


def check_master(JJ, PP, J0c, P0head, P0tailfrom, P0tw, label):
    """[u^n][y^m] of the two master identities, n <= UO, m <= YO-1."""
    # D = u^2 - y (1 + 2u + 3u^2 + 2u^3 + u^4): handled inline below.
    kernel = [1, 2, 3, 2, 1]          # coeffs of (1+u+u^2)^2, u^0..u^4

    def J3(n, m):
        return col(JJ, n, m) if n >= 3 else 0

    def P3(n, m):
        return col(PP, n, m) if n >= 3 else 0

    j1 = lambda m: col(JJ, 1, m)
    j2 = lambda m: col(JJ, 2, m)
    j3 = lambda m: col(JJ, 3, m)
    p2 = lambda m: col(PP, 2, m)
    p3 = lambda m: col(PP, 3, m)
    Jm = lambda m: sum(col(JJ, g, m) for g in range(3, 2 * m + 3))

    def RJ(n, m):
        if n < 1 or n > 4:
            return 0
        c1 = -2 * j3(m) + 8 * Jm(m) + 5 * j1(m) + 6 * j2(m) + p3(m) + 2 * p2(m)
        c2 = 2 * Jm(m) + 2 * j1(m) + 3 * j2(m) + 2 * p2(m)
        c3 = j1(m) + 2 * j2(m)
        c4 = j2(m)
        return [0, c1, c2, c3, c4][n]

    def RP(n, m):
        # (2j3-p3) u + Jm (8u^2 + 12 u^3/(1-u)) + j1 (4u^2+6u^3+8u^4/(1-u))
        # + j2 (4u^2+6u^3+8u^4+10u^5/(1-u)) + p2 (u^2+4u^3+3u^4+2u^5/(1-u))
        if n < 1:
            return 0
        v = 0
        if n == 1:
            v += 2 * j3(m) - p3(m)
        if n == 2:
            v += 8 * Jm(m) + 4 * j1(m) + 4 * j2(m) + p2(m)
        if n == 3:
            v += 6 * j1(m) + 6 * j2(m) + 4 * p2(m)
        if n >= 3:
            v += 12 * Jm(m)
        if n == 4:
            v += 8 * j2(m) + 3 * p2(m)
        if n >= 4:
            v += 8 * j1(m)
        if n >= 5:
            v += 10 * j2(m) + 2 * p2(m)
        return v

    def J0(n):
        return J0c[n] if 0 <= n < len(J0c) else 0

    def P0(n):
        if n < 1:
            return 0
        v = P0head.get(n, 0)
        if n >= P0tailfrom:
            v += P0tw
        return v

    for m in range(YO):
        for n in range(UO + 1):
            # J-side: [u^n][y^m+? ] of D.J3 - u^2 Q = 0, per y-order:
            # coeff y^M: J3(n-2, M) - sum_k kernel[k] J3(n-k, M-1)
            #   - [ J0(n-2) [M=0] - j1(M)[n=3] - j2(M)[n=4] + RJ(n-2, M-1) ]
            for M in (m,):
                lhs = J3(n - 2, M) - (sum(kernel[k] * J3(n - k, M - 1)
                                          for k in range(5)) if M >= 1 else 0)
                rhs = (J0(n - 2) if M == 0 else 0)
                rhs -= j1(M) if n == 3 else 0
                rhs -= j2(M) if n == 4 else 0
                rhs += RJ(n - 2, M - 1) if M >= 1 else 0
                if lhs != rhs:
                    fail(f"J-master ({label}) n={n} M={M}: {lhs} != {rhs}")
            # P-side: D.(P3-2J3) = u^2 (P0 - p2 u^2 - 2 J3 + y R_P)
            M = m
            f = lambda nn, MM: P3(nn, MM) - 2 * J3(nn, MM)
            lhs = f(n - 2, M) - (sum(kernel[k] * f(n - k, M - 1)
                                     for k in range(5)) if M >= 1 else 0)
            rhs = (P0(n - 2) if M == 0 else 0)
            rhs -= p2(M) if n == 4 else 0
            rhs -= 2 * J3(n - 2, M)
            rhs += RP(n - 2, M - 1) if M >= 1 else 0
            if lhs != rhs:
                fail(f"P-master ({label}) n={n} M={M}: {lhs} != {rhs}")


print("== m3: master identities coefficient-wise", flush=True)
check_master(JI, PI, [0, 4, 1], {2: 4}, 3, 6, "int")
check_master(JB, PB, [0, 1], {}, 2, 1, "bare")
stage(f"D.J3 = u^2 Q and P-master verified, n <= {UO}, y-order < {YO}, both starts")

# --------------------------------------------- m4: roots as shifted series
print("== m4: sqrt recursions and kernel roots", flush=True)

assert s_mul(SER_A, SER_A) == SER_AA and s_mul(SER_B, SER_B) == SER_BB
U1_SER = s_shift_down(s_scale(Fraction(1, 2),
                              s_sub(s_sub(ONE_S, SER_S), SER_A)), 1)
U2_SER = s_shift_down(s_scale(Fraction(1, 2),
                              s_sub(SER_B, s_add(ONE_S, SER_S))), 1)
for u in (U1_SER, U2_SER):
    oo = s_add(s_add(ONE_S, u), s_mul(u, u))
    lhs = s_mul(u, u)
    rhs = s_mul(SER_Y, s_mul(oo, oo))
    if lhs[:NS - 4] != rhs[:NS - 4]:      # top orders lost to the shift
        fail("kernel identity fails for a shifted root")
for tup, ser, nm in ((U1, U1_SER, "u1"), (U2, U2_SER, "u2")):
    if tup_to_ser(tup)[:VNS - 2] != ser[:VNS - 2]:
        fail(f"{nm} shifted series disagrees with sympy root")
stage("A/B recursions square correctly; u1, u2 satisfy the kernel, match sympy")

# ------------------------------------------------- m5: the cleared 6x6 system
print("== m5: cleared 6x6 system, walk check, det certificate", flush=True)


def equations_cleared(X, J0c, P0fn, J0_1):
    """severance_w2_kernel.equations with rows 5,6 multiplied by D'(u_i)."""
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


def x_walk(JJ, PP):
    """The walk's six series as truncated Q[[s]] elements (y = s^2)."""
    def yser(f):
        out = sz()
        for m in range(YO + 1):
            if 2 * m < NS:
                out[2 * m] = Fraction(f(m))
        return out
    return [yser(lambda m: col(JJ, 1, m)), yser(lambda m: col(JJ, 2, m)),
            yser(lambda m: col(JJ, 3, m)),
            yser(lambda m: sum(col(JJ, g, m) for g in range(3, 2 * m + 3))),
            yser(lambda m: col(PP, 2, m)), yser(lambda m: col(PP, 3, m))]


CHECK_TO = 2 * YO             # trust walk data to s-order 2*YO

for kind, (JJ, PP) in (("int", (JI, PI)), ("bare", (JB, PB))):
    J0c, P0fn, J0_1 = J0_P0(kind)
    rhs = [smul(-1, e) for e in equations_cleared([ZERO] * 6, J0c, P0fn, J0_1)]
    cols = []
    for k in range(6):
        e = [ZERO] * 6
        e[k] = ONE
        cols.append([add(v, r) for v, r in
                     zip(equations_cleared(e, J0c, P0fn, J0_1), rhs)])
    M_ser = [[tup_to_ser(cols[c][r]) for c in range(6)] for r in range(6)]
    R_ser = [tup_to_ser(rhs[r]) for r in range(6)]
    XW = x_walk(JJ, PP)
    for r in range(6):
        acc = sz()
        for c in range(6):
            acc = s_add(acc, s_mul(M_ser[r][c], XW[c]))
        d = s_sub(acc, R_ser[r])
        if any(x != 0 for x in d[:CHECK_TO]):
            fail(f"walk does not satisfy cleared eq {r + 1} ({kind}): "
                 f"{d[:CHECK_TO]}")
    stage(f"walk series satisfy the cleared system to s-order {CHECK_TO} ({kind})")

    # det via Leibniz over truncated series
    det = sz()
    for perm in permutations(range(6)):
        sign = 1
        pl = list(perm)
        for i in range(6):
            for jx in range(i + 1, 6):
                if pl[i] > pl[jx]:
                    sign = -sign
        term = ONE_S
        for r in range(6):
            term = s_mul(term, M_ser[r][perm[r]])
        det = s_add(det, s_scale(sign, term))
    v = next((i for i, x in enumerate(det) if x != 0), None)
    if v is None:
        fail(f"det underflows the truncation ({kind})")
    print(f"    det ({kind}): valuation {v}, leading {det[v]}, "
          f"next {det[v + 1:v + 4]}")
    stage(f"det certificate computed ({kind})")

    # sympy solution satisfies the cleared system exactly
    X_hat = solve_start(J0c, P0fn, J0_1)
    res = equations_cleared(X_hat, J0c, P0fn, J0_1)
    for r, e in enumerate(res):
        if any(sp.cancel(sp.together(c)) != 0 for c in e):
            fail(f"sympy solution fails cleared eq {r + 1} ({kind})")
    stage(f"sympy solution satisfies the cleared system exactly ({kind})")

    # walk series match the closed forms
    for i in range(6):
        d = s_sub(tup_to_ser(X_hat[i]), XW[i])
        if any(x != 0 for x in d[:CHECK_TO]):
            fail(f"closed form {i} != walk series ({kind})")
    stage(f"closed forms match walk series to s-order {CHECK_TO} ({kind})")

    # m6: transcription sizes
    names = ["j1", "j2", "j3", "Jm", "p2", "p3"]
    print(f"    transcription sizes ({kind}), per basis component "
          f"(num_chars/den_chars@pole-order):")
    for i, t in enumerate(X_hat):
        parts = []
        for comp in t:
            if comp == 0:
                parts.append("0")
                continue
            num, den0, e = rat_split(comp)
            parts.append(f"{len(str(sp.expand(num)))}/"
                         f"{len(str(sp.expand(den0)))}@{e}")
        print(f"      {names[i]}: {'  '.join(parts)}")
    if kind == "int":
        X_INT = X_hat
    else:
        X_BARE = X_hat

# ------------------------------------------------- m7: elimination identity
print("== m7: elimination identity and the y-form quartic", flush=True)

q_of = lambda X: add(add(smul(4, X[0]), smul(5, X[1])),
                     add(smul(6, X[3]), X[4]))
S_t = mul(Y, q_of(X_INT))
B_t = add(ONE, mul(Y, q_of(X_BARE)))
Ph_t = mul(Y, add(add(X_BARE[0], X_BARE[1]), X_BARE[3]))
F1_t = sub(Ph_t, div(mul(B_t, B_t), add(K(3), S_t)))
stage("F1 assembled from the two solutions")

c = [sp.cancel(e) for e in F1_t]
den = sp.lcm([sp.fraction(sp.together(ci))[1] for ci in c])
n0, n1, n2, n3 = [sp.expand(sp.cancel(ci * den)) for ci in c]
if den.subs(s, 0) == 0:
    fail("F1 common denominator is not a unit in Q[[s]]")
print(f"    common den (chars {len(str(sp.expand(den)))}), den(0) = {den.subs(s, 0)}")
Pq = sp.expand(n1 ** 2 * AA - n2 ** 2 * BB - n3 ** 2 * AA * BB)
T0 = (sp.S(0), n1, n2, n3)
S1 = add(mul(T0, T0), K(Pq))
lhs = mul(S1, S1)
inner = add(smul(n1, T0), K(sp.expand(n2 * n3 * BB)))
rhs = smul(4 * AA, mul(inner, inner))
diff = sub(lhs, rhs)
if any(sp.expand(e) != 0 for e in diff):
    fail("Psi identity fails in the 4-tuple algebra")
stage("Psi(T) = 0 verified in the 4-tuple algebra (the `ring` lemma)")

# y-form quartic cY_k and its numeric annihilation of F1
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
            fail("odd power of s in the eliminated quartic")
        out += co * y ** (k // 2)
    cY.append(sp.expand(out))
print("    cY_k (y-form quartic, before x-rescale):")
for k, ci in enumerate(cY):
    print(f"      tau^{k}: {sp.factor(ci)}  (chars {len(str(ci))})")

F1_ser = tup_to_ser(F1_t)
acc = sz()
pw_ser = ONE_S
for k in range(5):
    cser = s_from_poly(cY[k].subs(y, s ** 2))
    acc = s_add(acc, s_mul(cser, pw_ser))
    pw_ser = s_mul(pw_ser, F1_ser)
if any(x != 0 for x in acc[:VNS]):
    fail("sum cY_k(s^2) F1^k != 0 numerically")
stage(f"sum_k cY_k(s^2) F1^k = 0 to s-order {VNS - 1}")

# exact scale linking the y-form to the banked Phi(x, W)
x, Wv = sp.symbols('x W')
lift = sp.expand(sum(cY[k].subs(y, 3 * x) * ((Wv - 1) / sp.S(3)) ** k
                     for k in range(5)))
from depth1_recurrence import PHI_COEFFS  # noqa: E402
banked = sp.expand(sum(sp.sympify(PHI_COEFFS[k]) * Wv ** k for k in range(5)))
ratio = sp.cancel(lift / banked)
print(f"    lift / banked Phi ratio: {ratio}")
if not ratio.is_rational_function(x):
    fail("lift is not a rational multiple of banked Phi")
num, denr = sp.fraction(ratio)
if sp.degree(num, x) > 0 or sp.degree(denr, x) > 0:
    fail(f"lift/banked ratio is not constant: {ratio}")
stage("y-form lifts to a constant multiple of the banked Phi(x, W)")

print(f"\nALL MEASUREMENTS PASS  ({time.time() - t0:.1f}s total)")
