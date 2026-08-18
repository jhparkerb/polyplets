#!/usr/bin/env python3
"""Degree of the tail numerator N~_k of a site-perimeter defect class.

The class's tail series from its onset is x^onset * N~(x) / D(x) with
deg N~ < deg D.  L6 states deg N~_k = deg D_k - 1 exactly; this measures it
instead of asserting it, so the k=6 row is data and not an extrapolation.

    python3 experiments/perimeter_defect_tail_degree.py results/perimdefect_square8_n78_k6.txt --k 6
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict

PHI = {1: [1, -1], 2: [1, 1], 3: [1, 1, 1]}


def read_census(path, k):
    # column 0 is n, column 1 is the defect, the last column is the count;
    # rows for one (n, defect) may be split across several lines.
    pts = defaultdict(int)
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        if int(f[1]) == k:
            pts[int(f[0])] += int(f[-1])
    return dict(pts)


def polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("census")
    ap.add_argument("--k", type=int, required=True)
    args = ap.parse_args()
    k = args.k
    # Phi_d first appears at k = 2d-1, so Phi_2 starts at k=3, not k=2.
    exps = {1: k + 1, 2: max(0, k - 1) if k >= 3 else 0, 3: max(0, k - 4)}
    D = [1]
    for d, e in exps.items():
        for _ in range(e):
            D = polymul(D, PHI[d])
    onset = k * (k + 1) // 2 + 3
    pts = read_census(args.census, k)
    nmax = max(pts)
    tail = [pts.get(n, 0) for n in range(onset, nmax + 1)]
    prod = polymul(tail, D)
    # The tail is truncated at nmax, so the top deg D coefficients of the
    # product are contaminated by the terms the census does not have.  Only
    # indices up to (nmax - onset) - deg D are exact; look for the top nonzero
    # one there, and report the window so a too-short census is visible.
    bound = len(D) - 1
    exact = (nmax - onset) - bound
    top = max((i for i, c in enumerate(prod[:exact + 1]) if c), default=-1)
    print("k=%d  onset=%d  deg D=%d  deg N~=%d  (exact window 0..%d)  %s"
          % (k, onset, bound, top, exact,
             "= deg D - 1" if top == bound - 1 else "!= deg D - 1"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
