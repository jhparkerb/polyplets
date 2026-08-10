#!/usr/bin/env python3
"""Notary piece K, wave K-gamma: pre-verify every skeleton statement.

Verifies numerically, in truncated Fraction arithmetic over Q[[s]] with the
walk data from depth1_gap_walk.transitions (the independent source), every
statement the wave K-gamma skeleton (`GapWalkClosing.lean`) asserts, in the
exact form stated:

  g1. JmY_step (y-level column-sum recurrence):
        JmY = y (jY1 + 3 jY2 + 9 JmY - 3 jY3 - jY4)
  g2. the premultiplied evaluated J-master, for u in {u1, u2} (and a
      non-root sanity u = s + s^2):
        u^2 (D(u) J3ser) = u^2 (u^2 Qser),  D(u) = u^2 - s^2 (1+u+u^2)^2
      with J3ser = sum_{g>=3} jS_g u^g, Qser as transcribed for Lean;
  g3. the premultiplied evaluated P-master:
        u^2 (D(u) (P3ser - 2 J3ser))
          = u^2 (u^2 (P0ser - p2 u^2 - 2 J3ser + s^2 RPser))
      with P0ser = p02 u^2 + pt u^3 w, w = (1-u)^{-1}, RPser as transcribed;
  g4. the premultiplied evaluated J-master derivative:
        u^2 (u dP(u) J3ser + D(u) J3serW) = u^2 (2 u^2 Qser + u^3 Qpser)
      with J3serW = sum_{g>=3} g jS_g u^g, dP(u) = 2u - 2 s^2 (1+u+u^2)(1+2u);
  g5. the six closing equations in the exact Lean transcriptions
      (equations_cleared of notary_k_measure, restated):
        (1),(2)  Qser(u_i) = 0
        (3)      jS1 = j01 + s^2 (jS3 + c1S)
        (4)      JmS (1 - 9 s^2) = j01 + j02 - jS1 - jS2
                   + s^2 (c1S + c2S + c3S + c4S)
        (5),(6)  dP(u_i) (P0ser - p2S u_i^2 + s^2 RPser(u_i))
                   - 2 u_i^2 Qpser(u_i) = 0
  g6. root facts: coeff 1 u1 = 1, coeff 1 u2 = -1 (the u_i != 0
      certificates), constant coefficients 0;
  g7. geometric collapse: (1-u) sum_{g>=K} u^g = u^K for K = 0, 3, 5.

All series truncated at s-order NS; assertions to s-order NS-8 (top orders
lost to shifts/products).  Exact command:
  python3 experiments/notary_kgamma_statements.py \
      | tee build/notary_kgamma_statements.log
Target machine: gympie (local).  Predicted cost: < 60 s, one core, tiny.
Kill/resume: stateless; rerun from scratch.
"""
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth1_gap_walk import transitions                          # noqa: E402

NS = 44                       # s-length of truncated arithmetic
CHK = NS - 8                  # assert equality to this s-order
YO = NS // 2 + 1              # y-orders of walk data needed
GLIM = NS + 6                 # gap columns retained (val >= g kills the rest)
CAP = 2 * YO + GLIM + 8
t0 = time.time()


def stage(name):
    print(f"  [{time.time() - t0:6.1f}s] {name}", flush=True)


def fail(msg):
    print(f"FAIL: {msg}", flush=True)
    sys.exit(1)


# ---------------------------------------------------------------- series ops
def sz():
    return [Fraction(0)] * NS


def s_add(a, b):
    return [x + y for x, y in zip(a, b)]


def s_sub(a, b):
    return [x - y for x, y in zip(a, b)]


def s_scale(k, a):
    return [Fraction(k) * x for x in a]


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


def s_pow(a, k):
    out = sz()
    out[0] = Fraction(1)
    for _ in range(k):
        out = s_mul(out, a)
    return out


def s_sqrt(target):
    out = sz()
    out[0] = Fraction(1)
    for n in range(1, NS):
        out[n] = (target[n] - sum(out[i] * out[n - i]
                                  for i in range(1, n))) / 2
    return out


def const(c):
    out = sz()
    out[0] = Fraction(c)
    return out


ONE = const(1)
S = sz()
S[1] = Fraction(1)
Y = s_mul(S, S)

def assert_eq(a, b, label):
    d = s_sub(a, b)
    if any(x != 0 for x in d[:CHK]):
        k = next(i for i, x in enumerate(d) if x != 0)
        fail(f"{label}: differ from s^{k}: {d[k]}")


# ------------------------------------------------------------------- roots
AA = s_sub(s_sub(ONE, s_scale(2, S)), s_scale(3, Y))     # 1 - 2s - 3s^2
BB = s_sub(s_add(ONE, s_scale(2, S)), s_scale(3, Y))     # 1 + 2s - 3s^2
A = s_sqrt(AA)
B = s_sqrt(BB)
assert_eq(s_mul(A, A), AA, "A^2")
assert_eq(s_mul(B, B), BB, "B^2")


def shift_down(a, k):
    assert all(x == 0 for x in a[:k])
    return a[k:] + [Fraction(0)] * k


U1 = shift_down(s_scale(Fraction(1, 2), s_sub(s_sub(ONE, S), A)), 1)
U2 = shift_down(s_scale(Fraction(1, 2), s_sub(B, s_add(ONE, S))), 1)
if U1[0] != 0 or U2[0] != 0:
    fail("root constant coefficients nonzero")
if U1[1] != 1 or U2[1] != -1:
    fail(f"g6: coeff 1 of roots: {U1[1]}, {U2[1]} (want 1, -1)")
stage("g6: coeff 1 u1 = 1, coeff 1 u2 = -1, constant terms 0")

USANE = s_add(S, Y)           # a non-root test point with cc = 0


def D_of(u):
    oo = s_add(s_add(ONE, u), s_mul(u, u))
    return s_sub(s_mul(u, u), s_mul(Y, s_mul(oo, oo)))


def dP_of(u):
    oo = s_add(s_add(ONE, u), s_mul(u, u))
    return s_sub(s_scale(2, u),
                 s_scale(2, s_mul(Y, s_mul(oo, s_add(ONE, s_scale(2, u))))))


for u, nm in ((U1, "u1"), (U2, "u2")):
    assert_eq(D_of(u), sz(), f"kernel D({nm})")
stage("roots satisfy the kernel")

# g7: geometric collapse
for u in (U1, U2, USANE):
    for K in (0, 3, 5):
        geo = sz()
        for g in range(K, GLIM):
            geo = s_add(geo, s_pow(u, g))
        assert_eq(s_mul(s_sub(ONE, u), geo), s_pow(u, K), f"geom K={K}")
stage("g7: (1-u) sum_{g>=K} u^g = u^K")

# ------------------------------------------------------------------- walk
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


START = {
    'int':  dict(j01=4, j02=1, p02=4, pt=6),
    'bare': dict(j01=1, j02=0, p02=1, pt=1),
}


def start_vec(d):
    v = {(1, 'J'): d['j01'], (2, 'J'): d['j02'], (2, 'P'): d['p02']}
    for g in range(3, CAP + 1):
        v[(g, 'P')] = d['pt']
    return {k: w for k, w in v.items() if w}


for name, dd in START.items():
    JJ, PP = run_walk(start_vec(dd))

    def even(f):
        out = sz()
        for m in range(YO + 1):
            if 2 * m < NS:
                out[2 * m] = Fraction(f(m))
        return out

    jS = {g: even(lambda m, g=g: JJ[m][g]) for g in range(1, GLIM)}
    pS = {g: even(lambda m, g=g: PP[m][g]) for g in range(1, GLIM)}
    JmS = even(lambda m: sum(JJ[m][g] for g in range(3, 2 * m + 3)))

    # g1: JmY_step (checked in the s-variable; equivalent statement)
    rhs = s_mul(Y, s_add(s_add(jS[1], s_scale(3, jS[2])),
                         s_sub(s_scale(9, JmS),
                               s_add(s_scale(3, jS[3]), jS[4]))))
    assert_eq(JmS, rhs, f"g1 JmY_step ({name})")
    stage(f"g1: JmY_step ({name})")

    c1S = s_add(s_sub(s_scale(8, JmS), s_scale(2, jS[3])),
                s_add(s_add(s_scale(5, jS[1]), s_scale(6, jS[2])),
                      s_add(pS[3], s_scale(2, pS[2]))))
    c2S = s_add(s_add(s_scale(2, JmS), s_scale(2, jS[1])),
                s_add(s_scale(3, jS[2]), s_scale(2, pS[2])))
    c3S = s_add(jS[1], s_scale(2, jS[2]))
    c4S = jS[2]
    j01, j02, p02, pt = (dd[k] for k in ('j01', 'j02', 'p02', 'pt'))

    def Qser(u):
        t = s_sub(s_add(s_scale(j01, u), s_scale(j02, s_pow(u, 2))),
                  s_add(s_mul(jS[1], u), s_mul(jS[2], s_pow(u, 2))))
        rj = s_add(s_add(s_mul(c1S, u), s_mul(c2S, s_pow(u, 2))),
                   s_add(s_mul(c3S, s_pow(u, 3)), s_mul(c4S, s_pow(u, 4))))
        return s_add(t, s_mul(Y, rj))

    def Qpser(u):
        t = s_sub(s_add(const(j01), s_scale(2 * j02, u)),
                  s_add(jS[1], s_scale(2, s_mul(jS[2], u))))
        rjp = s_add(s_add(c1S, s_scale(2, s_mul(c2S, u))),
                    s_add(s_scale(3, s_mul(c3S, s_pow(u, 2))),
                          s_scale(4, s_mul(c4S, s_pow(u, 3)))))
        return s_add(t, s_mul(Y, rjp))

    def RPser(u, w):
        t = s_mul(s_sub(s_scale(2, jS[3]), pS[3]), u)
        t = s_add(t, s_mul(JmS, s_add(s_scale(8, s_pow(u, 2)),
                                      s_scale(12, s_mul(s_pow(u, 3), w)))))
        t = s_add(t, s_mul(jS[1], s_add(
            s_add(s_scale(4, s_pow(u, 2)), s_scale(6, s_pow(u, 3))),
            s_scale(8, s_mul(s_pow(u, 4), w)))))
        t = s_add(t, s_mul(jS[2], s_add(
            s_add(s_scale(4, s_pow(u, 2)),
                  s_add(s_scale(6, s_pow(u, 3)), s_scale(8, s_pow(u, 4)))),
            s_scale(10, s_mul(s_pow(u, 5), w)))))
        t = s_add(t, s_mul(pS[2], s_add(
            s_add(s_pow(u, 2),
                  s_add(s_scale(4, s_pow(u, 3)), s_scale(3, s_pow(u, 4)))),
            s_scale(2, s_mul(s_pow(u, 5), w)))))
        return t

    def P0ser(u, w):
        return s_add(s_scale(p02, s_pow(u, 2)),
                     s_scale(pt, s_mul(s_pow(u, 3), w)))

    def J3ser(u):
        t = sz()
        for g in range(3, GLIM):
            t = s_add(t, s_mul(jS[g], s_pow(u, g)))
        return t

    def P3ser(u):
        t = sz()
        for g in range(3, GLIM):
            t = s_add(t, s_mul(pS[g], s_pow(u, g)))
        return t

    def J3serW(u):
        t = sz()
        for g in range(3, GLIM):
            t = s_add(t, s_scale(g, s_mul(jS[g], s_pow(u, g))))
        return t

    # g2, g3, g4 at both roots and the non-root point
    for u, nm in ((U1, "u1"), (U2, "u2"), (USANE, "s+s^2")):
        u2 = s_pow(u, 2)
        w = s_inv(s_sub(ONE, u))
        j3 = J3ser(u)
        lhs = s_mul(u2, s_mul(D_of(u), j3))
        rhs = s_mul(u2, s_mul(u2, Qser(u)))
        assert_eq(lhs, rhs, f"g2 J-master ({name}, {nm})")
        p3 = P3ser(u)
        f3 = s_sub(p3, s_scale(2, j3))
        lhs = s_mul(u2, s_mul(D_of(u), f3))
        inner = s_add(s_sub(s_sub(P0ser(u, w), s_mul(pS[2], u2)),
                            s_scale(2, j3)),
                      s_mul(Y, RPser(u, w)))
        rhs = s_mul(u2, s_mul(u2, inner))
        assert_eq(lhs, rhs, f"g3 P-master ({name}, {nm})")
        lhs = s_mul(u2, s_add(s_mul(u, s_mul(dP_of(u), j3)),
                              s_mul(D_of(u), J3serW(u))))
        rhs = s_mul(u2, s_add(s_scale(2, s_mul(u2, Qser(u))),
                              s_mul(s_pow(u, 3), Qpser(u))))
        assert_eq(lhs, rhs, f"g4 J-deriv-master ({name}, {nm})")
    stage(f"g2-g4: three premultiplied masters, both roots + non-root ({name})")

    # g5: the six closing equations
    assert_eq(Qser(U1), sz(), f"g5 eq1 ({name})")
    assert_eq(Qser(U2), sz(), f"g5 eq2 ({name})")
    assert_eq(jS[1], s_add(const(j01), s_mul(Y, s_add(jS[3], c1S))),
              f"g5 eq3 ({name})")
    assert_eq(s_mul(JmS, s_sub(ONE, s_scale(9, Y))),
              s_add(s_sub(const(j01 + j02), s_add(jS[1], jS[2])),
                    s_mul(Y, s_add(s_add(c1S, c2S), s_add(c3S, c4S)))),
              f"g5 eq4 ({name})")
    for u, lbl in ((U1, "eq5"), (U2, "eq6")):
        w = s_inv(s_sub(ONE, u))
        t = s_add(s_sub(P0ser(u, w), s_mul(pS[2], s_pow(u, 2))),
                  s_mul(Y, RPser(u, w)))
        lhs = s_sub(s_mul(dP_of(u), t),
                    s_scale(2, s_mul(s_pow(u, 2), Qpser(u))))
        assert_eq(lhs, sz(), f"g5 {lbl} ({name})")
    stage(f"g5: six closing equations ({name})")

    # dJ3 intermediate: dP(u_i) J3ser(u_i) = u_i^2 Qpser(u_i)
    for u, nm in ((U1, "u1"), (U2, "u2")):
        assert_eq(s_mul(dP_of(u), J3ser(u)),
                  s_mul(s_pow(u, 2), Qpser(u)), f"dJ3 ({name}, {nm})")
    stage(f"dJ3: dP(u_i) J3(u_i) = u_i^2 Q'(u_i) ({name})")

print(f"ALL PASS ({time.time() - t0:.1f}s)")
