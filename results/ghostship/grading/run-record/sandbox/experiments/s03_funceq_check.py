#!/usr/bin/env python3
"""Session 03: numeric validation of the row-adding FUNCTIONAL EQUATION for
convex king animals (and the polyomino control), derived independently of the
convex_box.py DP.

Model (rows added downward, state = (phase, k) with k = last-row interval
length; x marks current bounding-box width via incremental extensions,
y marks rows):

phases: 0=(0,0) opening (l non-incr so far, r non-decr so far; last row spans
        the current box: l = Lmin, r = Rmax)
        1=(1,0) right-staircase (l has strictly increased; r still non-decr;
        r = Rmax, a = l - Lmin > 0 irrelevant to the future)
        2=(0,1) left-staircase (mirror)
        3=(1,1) closing (both flipped; nested decreasing intervals)

Transitions from current length k (all get one factor y; xweight = box growth):
 (0,0)->(0,0): u,v>=0            k'=k+u+v   xw=u+v
 (0,0)->(1,0): i in[1,k], e>=0, (i=k => e>=1)   k'=k+e-i  xw=e
 (0,0)->(0,1): j in[1,k], u>=0, (j=k => u>=1)   k'=k+u-j  xw=u
 (0,0)->(1,1): i,j>=1, i+j<=k-1  k'=k-i-j   xw=0
 (1,0)->(1,0): i in[0,k], e>=0, (i=k => e>=1)   k'=k+e-i  xw=e
 (1,0)->(1,1): i>=0, j>=1, i+j<=k-1             k'=k-i-j  xw=0
 (0,1)->(0,1): j in[0,k], u>=0, (j=k => u>=1)   k'=k+u-j  xw=u
 (0,1)->(1,1): i>=1, j>=0, i+j<=k-1             k'=k-i-j  xw=0
 (1,1)->(1,1): i,j>=0, i+j<=k-1                 k'=k-i-j  xw=0

POLYOMINO control (column-overlap adjacency instead of king reach):
 same but the staircase upper bound is i in [.,k-1] (no i=k boundary case):
 (0,0)->(1,0): i in[1,k-1], e>=0 ; (1,0)->(1,0): i in[0,k-1], e>=0 ; mirrors.

Check: sum over phases at each h of x^w-marginals == f(w,h) from the
validated convex_box.py DP (which was itself brute-force validated).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convex_box import g_table, f_from_g
from collections import defaultdict

W = int(sys.argv[1]) if len(sys.argv) > 1 else 12
H = int(sys.argv[2]) if len(sys.argv) > 2 else 12


def funceq_table(W, H, king=True):
    """f[w][h] computed from the functional-equation transitions."""
    # dp[phase][k] = dict {xdeg: count}
    dp = [defaultdict(lambda: defaultdict(int)) for _ in range(4)]
    for k in range(1, W + 1):
        dp[0][k][k] = 1
    f = [[0] * (H + 1) for _ in range(W + 1)]

    def collect(dp, h):
        for ph in range(4):
            for k, xs in dp[ph].items():
                for w, c in xs.items():
                    if w <= W:
                        f[w][h] += c

    collect(dp, 1)
    for h in range(2, H + 1):
        nd = [defaultdict(lambda: defaultdict(int)) for _ in range(4)]

        def add(ph, k, w, c):
            if k >= 1 and w <= W:
                nd[ph][k][w] += c

        for k in range(1, W + 1):
            for w, c in dp[0][k].items():
                # ->(0,0)
                for u in range(0, W - w + 1):
                    for v in range(0, W - w - u + 1):
                        add(0, k + u + v, w + u + v, c)
                # ->(1,0) and mirror ->(0,1)
                imax = k if king else k - 1
                for i in range(1, imax + 1):
                    emin = 1 if (king and i == k) else 0
                    for e in range(emin, W - w + 1):
                        add(1, k + e - i, w + e, c)
                        add(2, k + e - i, w + e, c)
                # ->(1,1)
                for i in range(1, k - 1 + 1):
                    for j in range(1, k - 1 - i + 1):
                        add(3, k - i - j, w, c)
            for w, c in dp[1][k].items():
                imax = k if king else k - 1
                for i in range(0, imax + 1):
                    emin = 1 if (king and i == k) else 0
                    for e in range(emin, W - w + 1):
                        add(1, k + e - i, w + e, c)
                for i in range(0, k - 1 + 1):
                    for j in range(1, k - 1 - i + 1):
                        add(3, k - i - j, w, c)
            for w, c in dp[2][k].items():
                jmax = k if king else k - 1
                for j in range(0, jmax + 1):
                    umin = 1 if (king and j == k) else 0
                    for u in range(umin, W - w + 1):
                        add(2, k + u - j, w + u, c)
                for i in range(1, k - 1 + 1):
                    for j in range(0, k - 1 - i + 1):
                        add(3, k - i - j, w, c)
            for w, c in dp[3][k].items():
                for i in range(0, k - 1 + 1):
                    for j in range(0, k - 1 - i + 1):
                        add(3, k - i - j, w, c)
        dp = nd
        collect(dp, h)
    return f


for king in (True, False):
    tag = "KING" if king else "POLYOMINO(control)"
    g = g_table(W, H, king=king)
    fdp = f_from_g(g, W, H)
    ffe = funceq_table(W, H, king=king)
    bad = []
    for w in range(1, W + 1):
        for h in range(1, H + 1):
            if fdp[w][h] != ffe[w][h]:
                bad.append((w, h, fdp[w][h], ffe[w][h]))
    if bad:
        print(f"{tag}: MISMATCH ({len(bad)} cells); first 10:")
        for t in bad[:10]:
            print("   w=%d h=%d dp=%d funceq=%d" % t)
    else:
        print(f"{tag}: functional equation matches DP on ALL f(w,h), "
              f"w<={W}, h<={H}  OK")
        print("   sample f(5,5)=%d f(%d,%d)=%d" % (ffe[5][5], W, H, ffe[W][H]))
