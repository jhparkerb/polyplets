#!/usr/bin/env python3
"""Grand-form saddle point: predict the growth of the slope-s slices analytically.

Chain of reasoning being tested:

  1. The grand form says  sum_k P_k(n) y^k = exp(A(y) + n B(y))  with
     A = sum a_j y^j, B = sum b_j y^j.  Extract a_j, b_j exactly from the
     wired P_1..P_19 (orchestrator/sweep.go) by taking the log of the series
     with coefficients that are polynomials in n.  The grand form's content is
     that every log coefficient is LINEAR in n -- checked here for j=1..19,
     which is a simultaneous consistency check on all 19 production polynomials.

  2. results/diagonal-law-below-onset.md measures the closed form to be
     asymptotically exact below its onset: at fixed x = H/k the relative defect
     is exp(-|g(x)| k).  So on any ray k = kappa*H (kappa = s-1) the TRUE slice
     T(sH+c, H) has the same exponential growth as the LAW value
     P_k(n) * 3^(n-1-3k), even though the law is invalid there.

  3. P_k(n) at k = kappa*H, n = (1+kappa)H is a coefficient extraction with a
     large parameter H in both the exponent and the index:
        P = [y^k] exp(A(y) + (1+kappa)H B(y))
          ~ exp(H * phi(kappa)),   phi = stat value of (1+kappa)B(y) - kappa ln y
     saddle:  y B'(y) = kappa/(1+kappa).
     Hence   mu_s = 3^(1-2 kappa) * exp(phi(kappa)).

  4. Compare against the slice growth measured directly from the banked
     triangle (results/slope-slicings.md: mu ~ 41.85 at s=2, still drifting).

Two independent estimators of the same constant, one from 19 exact polynomials
and one from 20 raw counts.  Run: python3 experiments/grand_form_saddle.py
"""
import os
import re
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMAX = 19


# ---------- polynomials in n, Fraction coefficients, ascending order ----------
def padd(a, b):
    m = max(len(a), len(b))
    return [(a[i] if i < len(a) else F(0)) + (b[i] if i < len(b) else F(0))
            for i in range(m)]


def pmul(a, b):
    if not a or not b:
        return [F(0)]
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] += x * y
    return r


def pscale(a, c):
    return [c * x for x in a]


def ptrim(a):
    while len(a) > 1 and a[-1] == 0:
        a = a[:-1]
    return a


# ---------- y-series whose coefficients are polynomials in n ----------
def ymul(A, B):
    R = [[F(0)] for _ in range(KMAX + 1)]
    for i in range(KMAX + 1):
        if A[i] == [F(0)]:
            continue
        for j in range(KMAX + 1 - i):
            if B[j] == [F(0)]:
                continue
            R[i + j] = padd(R[i + j], pmul(A[i], B[j]))
    return R


def read_pk():
    """P_k(n) as polynomials in n (ascending), exact Fractions, k=1..KMAX."""
    src = open(os.path.join(ROOT, "orchestrator", "sweep.go")).read()
    blk = src[src.index("var diagCoeffTable"):]
    blk = blk[:blk.index("\n}\n")]
    # entries look like:  K: {[]string{"c0", "c1", ...}, DENOM},
    out = {}
    for m in re.finditer(r'(?m)^\t(\d+):\s*\{\[\]string\{(.*?)\},\s*(\d+)\},',
                         blk, re.S):
        k = int(m.group(1))
        coeffs = [int(s) for s in re.findall(r'"(-?\d+)"', m.group(2))]
        den = int(m.group(3))
        # stored descending in n, degree k
        assert len(coeffs) == k + 1, (k, len(coeffs))
        out[k] = [F(c, den) for c in reversed(coeffs)]
    return out


def main():
    P = read_pk()
    missing = [k for k in range(1, KMAX + 1) if k not in P]
    if missing:
        print("missing P_k:", missing)
        return 1
    print("read P_1..P_%d from orchestrator/sweep.go" % KMAX)

    # series S = 1 + sum_{k>=1} P_k(n) y^k
    S = [[F(0)] for _ in range(KMAX + 1)]
    S[0] = [F(1)]
    for k in range(1, KMAX + 1):
        S[k] = list(P[k])

    # log(S) = log(1+u) = sum_{m>=1} (-1)^(m+1) u^m / m
    U = [list(c) for c in S]
    U[0] = [F(0)]
    L = [[F(0)] for _ in range(KMAX + 1)]
    Upow = [[F(0)] for _ in range(KMAX + 1)]
    Upow[0] = [F(1)]
    for m in range(1, KMAX + 1):
        Upow = ymul(Upow, U)
        sgn = F(1, m) if m % 2 == 1 else F(-1, m)
        for j in range(KMAX + 1):
            L[j] = padd(L[j], pscale(Upow[j], sgn))

    print()
    print("== grand-form check: is every log coefficient linear in n?")
    a = {}
    b = {}
    bad = 0
    for j in range(1, KMAX + 1):
        c = ptrim(L[j])
        deg = len(c) - 1
        if deg > 1:
            bad += 1
            print("  j=%2d  DEGREE %d  -- NOT linear" % (j, deg))
            continue
        a[j] = c[0]
        b[j] = c[1] if len(c) > 1 else F(0)
    if bad:
        print("  %d violations -- grand form does not hold on this table" % bad)
        return 1
    print("  all j=1..%d linear in n: PASS" % KMAX)
    print("  b_1 = %s (expect 25), a_1 = %s (expect -45)" % (b[1], a[1]))
    assert b[1] == 25 and a[1] == -45

    print()
    print("== the production constants")
    print("  %3s %24s %24s" % ("j", "b_j", "a_j"))
    for j in range(1, KMAX + 1):
        print("  %3d %24s %24s" % (j, float(b[j]), float(a[j])))

    print()
    print("== radius of convergence of B(y) = sum b_j y^j")
    print("  %3s %14s %14s %14s" % ("j", "b_j/b_{j-1}", "|b_j|^(1/j)", "sign"))
    for j in range(2, KMAX + 1):
        if b[j - 1] == 0 or b[j] == 0:
            continue
        r = float(b[j]) / float(b[j - 1])
        root = abs(float(b[j])) ** (1.0 / j)
        print("  %3d %14.6f %14.6f %14s"
              % (j, r, root, "+" if b[j] > 0 else "-"))

    # ---- saddle point ----
    bf = [0.0] + [float(b[j]) for j in range(1, KMAX + 1)]
    af = [0.0] + [float(a[j]) for j in range(1, KMAX + 1)]

    def B(y, J=KMAX):
        return sum(bf[j] * y ** j for j in range(1, J + 1))

    def dB(y, J=KMAX):
        return sum(j * bf[j] * y ** (j - 1) for j in range(1, J + 1))

    def saddle(kappa, J=KMAX):
        """solve y B'(y) = kappa/(1+kappa) by bisection on (0, ymax)"""
        tgt = kappa / (1.0 + kappa)
        lo, hi = 1e-9, 0.02
        # grow hi until f(hi) > tgt or series misbehaves
        while hi < 1.0 and hi * dB(hi, J) < tgt:
            hi *= 1.2
        if hi * dB(hi, J) < tgt:
            return None
        for _ in range(300):
            mid = 0.5 * (lo + hi)
            if mid * dB(mid, J) < tgt:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    import math
    print()
    print("== saddle point per slope   mu_s = 3^(1-2k) exp((1+k)B(y*) - k ln y*)")
    print("  %5s %6s %12s %12s %16s" % ("slope", "kappa", "y*", "tail b_J y*^J",
                                        "mu_s"))
    preds = {}
    for s in (2, 3, 4, 5):
        kappa = float(s - 1)
        ys = saddle(kappa)
        if ys is None:
            print("  s=%d: no saddle inside truncation radius" % s)
            continue
        phi = (1 + kappa) * B(ys) - kappa * math.log(ys)
        mu = 3.0 ** (1 - 2 * kappa) * math.exp(phi)
        tail = abs(bf[KMAX] * ys ** KMAX)
        print("  %5d %6.1f %12.8f %12.3e %16.6f" % (s, kappa, ys, tail, mu))
        preds[s] = mu

    print()
    print("== truncation stability: mu_2 as J (number of b_j used) grows")
    for J in range(6, KMAX + 1):
        ys = saddle(1.0, J)
        if ys is None:
            print("  J=%2d  no saddle" % J)
            continue
        phi = 2 * B(ys, J) - math.log(ys)
        print("  J=%2d  y*=%.8f  mu_2=%.6f" % (J, ys, 3.0 ** (-1) * math.exp(phi)))

    # ---- measured slice growth, for comparison ----
    print()
    print("== measured, from the banked triangle")
    tri = {}
    ph = os.path.join(ROOT, "results", "ns_a40", "perheight")
    for fn in os.listdir(ph):
        m = re.match(r"h(\d+)\.out$", fn)
        if not m:
            continue
        H = int(m.group(1))
        for line in open(os.path.join(ph, fn)):
            p = line.split()
            if len(p) == 2:
                tri[(int(p[0]), H)] = int(p[1])
    for s in (2, 3, 4, 5):
        pts = []
        H = 2
        while (s * H, H) in tri:
            pts.append((H, tri[(s * H, H)]))
            H += 1
        if len(pts) < 4:
            continue
        rats = [(pts[i][0], pts[i][1] / pts[i - 1][1])
                for i in range(1, len(pts))]
        last = rats[-1]
        # Richardson on the ratio in 1/H (ratios approach mu like mu(1+c/H))
        (H1, r1), (H2, r2) = rats[-2], rats[-1]
        rich = (H2 * r2 - H1 * r1) / (H2 - H1)
        print("  s=%d  %2d pts  last ratio(H=%d)=%.4f  Richardson=%.4f  "
              "grand-form=%s"
              % (s, len(pts), last[0], last[1], rich,
                 ("%.4f" % preds[s]) if s in preds else "n/a"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
