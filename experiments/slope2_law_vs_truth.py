#!/usr/bin/env python3
"""The slope-2 line is exactly the onset line, and the law is nearly exact on it.

n = 2H  <=>  k = n-H = H  <=>  x = H/k = 1.  The diagonal law's proved region is
n >= 2k+1, i.e. H >= k+1, so EVERY slope-2 cell sits one step below onset (depth
j = 2k+1-n = 1).  results/diagonal-law-below-onset.md measures the relative
defect there as exp(-|g(1)| k) with |g(1)| ~ 1.3.

Three things checked, all exact where exactness is possible:

  A. law vs truth on n = 2H for H = 2..19 (P_k wired to k=19): how many digits,
     and does ln(defect/T) fall linearly in H with the predicted slope?
  B. the law's OWN growth ratios on the slope-2 line, against the saddle-point
     prediction mu_2 = 42.3946 from experiments/grand_form_saddle.py.
  C. the truth's growth ratios, same line -- must track (B) to the precision of
     (A), which is the whole point: the measured slice growth and the analytic
     saddle are the same constant.

Run: python3 experiments/slope2_law_vs_truth.py
"""
import math
import os
import re
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_pk():
    src = open(os.path.join(ROOT, "orchestrator", "sweep.go")).read()
    blk = src[src.index("var diagCoeffTable"):]
    blk = blk[:blk.index("\n}\n")]
    out = {}
    for m in re.finditer(r'(?m)^\t(\d+):\s*\{\[\]string\{(.*?)\},\s*(\d+)\},',
                         blk, re.S):
        k = int(m.group(1))
        coeffs = [int(s) for s in re.findall(r'"(-?\d+)"', m.group(2))]
        out[k] = (coeffs, int(m.group(3)))
    return out


def law(n, k, P):
    """P_k(n) * 3^(n-1-3k), exact Fraction (integer when the law is valid)."""
    coeffs, den = P[k]
    v = 0
    for c in coeffs:           # descending
        v = v * n + c
    e = n - 1 - 3 * k
    val = F(v, den)
    if e >= 0:
        return val * 3 ** e
    return val / 3 ** (-e)


def read_tri():
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
    return tri


MU_SADDLE = 42.394597


def main():
    P = read_pk()
    tri = read_tri()

    print("== A. law vs truth on the slope-2 line n = 2H (k = H, depth j = 1)")
    print("  %3s %3s %22s %10s %12s"
          % ("H", "k", "T(2H,H)", "digits", "ln(def/T)"))
    rows = []
    for H in range(2, 20):
        n = 2 * H
        if (n, H) not in tri or H not in P:
            continue
        T = tri[(n, H)]
        Lv = law(n, H, P)
        d = F(T) - Lv
        if d == 0:
            print("  %3d %3d %22d %10s %12s" % (H, H, T, "EXACT", "-inf"))
            continue
        rel = abs(float(d) / T)
        rows.append((H, math.log(rel)))
        print("  %3d %3d %22d %10.1f %12.4f"
              % (H, H, T, -math.log10(rel), math.log(rel)))
    print("  (defect sign: %s)"
          % ("law underestimates" if F(tri[(38, 19)]) - law(38, 19, P) > 0
             else "law overestimates"))
    if len(rows) >= 3:
        (h1, l1), (h2, l2) = rows[-2], rows[-1]
        print("  local slope d ln(rel)/dH at the tail = %.4f  "
              "(= g(1); below-onset note has g(0.95) = -1.3084)"
              % (l2 - l1))

    print()
    print("== B/C. growth ratios on the slope-2 line vs the saddle mu_2 = %.6f"
          % MU_SADDLE)
    print("  %3s %14s %14s %12s %12s"
          % ("H", "ratio(truth)", "ratio(law)", "T/law-1", "Rich(truth)"))
    prevT = prevL = None
    rr = []
    for H in range(2, 21):
        n = 2 * H
        if (n, H) not in tri:
            continue
        T = tri[(n, H)]
        Lv = law(n, H, P) if H in P else None
        rt = (T / prevT) if prevT else None
        rl = (float(Lv) / float(prevL)) if (Lv is not None and prevL) else None
        if rt:
            rr.append((H, rt))
        rich = ""
        if len(rr) >= 2:
            (H1, r1), (H2, r2) = rr[-2], rr[-1]
            rich = "%12.4f" % ((H2 * r2 - H1 * r1) / (H2 - H1))
        print("  %3d %14s %14s %12s %12s"
              % (H,
                 "%14.5f" % rt if rt else "",
                 "%14.5f" % rl if rl else "",
                 "%12.3e" % (float(F(T) - Lv) / T) if Lv is not None else "",
                 rich))
        prevT, prevL = T, Lv

    # second-order extrapolation of the truth ratios: r_H = mu (1 + c1/H + c2/H^2)
    print()
    print("== extrapolating the measured ratios to H = infinity")
    for m in (2, 3, 4):
        pts = rr[-m - 1:]
        if len(pts) < m + 1:
            continue
        # fit r = mu + c1/H + ... + cm/H^m by exact elimination
        import itertools
        A = [[F(1)] + [F(1, p[0] ** i) for i in range(1, m + 1)] for p in pts]
        rhs = [F(p[1]).limit_denominator(10 ** 12) for p in pts]
        # gaussian elimination
        N = m + 1
        M = [A[i] + [rhs[i]] for i in range(N)]
        for c in range(N):
            piv = next(r for r in range(c, N) if M[r][c] != 0)
            M[c], M[piv] = M[piv], M[c]
            M[c] = [x / M[c][c] for x in M[c]]
            for r in range(N):
                if r != c and M[r][c] != 0:
                    f = M[r][c]
                    M[r] = [M[r][i] - f * M[c][i] for i in range(N + 1)]
        mu = float(M[0][N])
        print("  order %d (H = %d..%d):  mu_2 = %.5f   [saddle %.5f, "
              "diff %+.3f%%]"
              % (m, pts[0][0], pts[-1][0], mu, MU_SADDLE,
                 100 * (mu - MU_SADDLE) / MU_SADDLE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
