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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# PHI, read_census and polymul are this script's neighbour's, not copies of it:
# a second implementation of the same cyclotomic arithmetic is a second thing to
# keep right.
from perimeter_defect_denominator import PHI, polymul, read_census  # noqa: E402


def denominator(k):
    """D_k = Phi_1^(k+1) Phi_2^(k-1) Phi_3^(k-4), nonpositive exponents dropped.

    Phi_d first appears at k = 2d-1, so Phi_2 starts at k = 3 -- one step later
    than max(0, k-1) would put it.  perimeter_defect_denominator.py can be
    looser here because it scans candidates and reports the minimal one that
    passes; this script divides by exactly one denominator and has to have it
    right.
    """
    exps = {1: k + 1, 2: max(0, k - 1) if k >= 3 else 0, 3: max(0, k - 4)}
    D = [1]
    for d, e in exps.items():
        for _ in range(e):
            D = polymul(D, PHI[d])
    return D


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
