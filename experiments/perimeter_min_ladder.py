#!/usr/bin/env python3
"""The site-perimeter table read from its OTHER end: the minimum-perimeter ladder.

`experiments/perimeter_defect_fit.py` grades A(n,p) by k = pmax(n) - p, the
distance from the MAXIMUM perimeter (sticks).  This grades the same table by
distance from the MINIMUM perimeter (fat, ball-shaped animals).  The two ends
are not mirror images:

  * pmax(n) is LINEAR in n, so n and p are interchangeable and grading in n
    works.  pmin(n) grows like sqrt(n) and is a STEP function -- flat over
    stretches of n, then jumping -- so a ladder indexed by n has columns that
    are at best polynomial in sqrt(n).  The natural row index at this end is p.

  * so we print BOTH: the n-indexed ladder B(n, j) = A(n, pmin(n)+j), and the
    p-indexed one C(p, i) = A(nmax(p)-i, p) where nmax(p) = max{n : pmin(n)<=p}
    is the isoperimetric maximum area at perimeter p.

pmin is not fitted here.  It is taken from the closed forms already banked in
`results/perimeter.md`, both of them published OEIS results:

    square4 (rook adjacency):  A261491, pmin(n) = ceil(2 + sqrt(8n-4))
    square8 (king adjacency):  A235382, pmin(n) = 2*ceil(2*sqrt(n)) + 4

and CHECKED against the census's own measured minimum before anything is
printed.  Both are computed integer-exactly (no float ever enters -- at a step
boundary math.sqrt can land a hair under the true root and silently shift the
whole ladder by one column; see the same trap in
experiments/min_site_perim_closed_form.py).

A p-indexed row is only trustworthy if the census reaches nmax(p); rows that
the census truncates are printed but flagged, because their j=0 entry would
otherwise be a lie (it would report the largest animal WE SAW, not the largest
that exists).

    python3 experiments/perimeter_min_ladder.py results/siteperim_square4_n20.txt --lattice square4
    python3 experiments/perimeter_min_ladder.py results/siteperim_square8_n14.txt --lattice square8

docs/perimeter-defect-plan.md (deleted); the max-end companion is
results/perimeter.md.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict


def isqrt_ceil(v: int) -> int:
    """ceiling(sqrt(v)) for v >= 0, integer-exactly."""
    r = math.isqrt(v)
    return r if r * r == v else r + 1


def pmin_square4(n: int) -> int:
    """A261491: ceil(2 + sqrt(8n-4)) = 2 + ceil(sqrt(8n-4))."""
    return 2 + isqrt_ceil(8 * n - 4)


def pmin_square8(n: int) -> int:
    """A235382: 2*ceil(2*sqrt(n)) + 4 = 2*ceil(sqrt(4n)) + 4."""
    return 2 * isqrt_ceil(4 * n) + 4


PMIN = {"square4": pmin_square4, "square8": pmin_square8}
PMAX = {"square4": lambda n: 2 * n + 2, "square8": lambda n: 4 * n + 4}


def read_census(path):
    """`n p count` rows -> {(n,p): count}, {n: total}."""
    tab = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, p, c = (int(f) for f in line.split())
        tab[(n, p)] = tab.get((n, p), 0) + c
    return tab


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("census", help="`n p count` table from build/g2 --siteperim")
    ap.add_argument("--lattice", required=True, choices=sorted(PMIN))
    ap.add_argument("--jmax", type=int, default=8, help="ladder depth to print")
    args = ap.parse_args()

    pmin = PMIN[args.lattice]
    tab = read_census(args.census)
    ns = sorted({n for n, _ in tab})
    nmaxcensus = max(ns)

    # --- gate: the banked closed form must reproduce the census's own minimum.
    bad = []
    for n in ns:
        meas = min(p for (m, p) in tab if m == n)
        if meas != pmin(n):
            bad.append((n, pmin(n), meas))
    if bad:
        print("PMIN MISMATCH -- closed form vs census, (n, formula, measured):")
        for row in bad:
            print("   ", row)
        return 1
    print("pmin closed form (%s) verified against census for n = %d..%d."
          % (args.lattice, ns[0], nmaxcensus))
    print()

    # --- ladder A: rows n, columns j = p - pmin(n).
    print("B(n, j) = A(n, pmin(n)+j)   [n-indexed: the wrong index, on purpose]")
    hdr = "   n  pmin |" + "".join("%9d" % j for j in range(args.jmax + 1))
    print(hdr)
    print("-" * len(hdr))
    for n in ns:
        row = "%4d  %4d |" % (n, pmin(n))
        for j in range(args.jmax + 1):
            p = pmin(n) + j
            row += "%9s" % (tab.get((n, p), 0) if p <= PMAX[args.lattice](n) else "-")
        print(row)
    print()

    # --- ladder B: rows p, columns i = nmax(p) - n.
    # nmax(p) = max{n : pmin(n) <= p}, computed by scanning pmin (monotone).
    nmax_of_p = {}
    n = 1
    while pmin(n) <= pmin(nmaxcensus) + args.jmax + 4:
        nmax_of_p[pmin(n)] = n          # pmin nondecreasing: last n wins
        n += 1
    # fill p values pmin never attains (pmin skips values) with the running max
    ps = sorted(nmax_of_p)
    running = {}
    best = 0
    for p in range(min(ps), max(ps) + 1):
        if p in nmax_of_p:
            best = nmax_of_p[p]
        if best:
            running[p] = best
    print("C(p, i) = A(nmax(p)-i, p)   [p-indexed: rows are the isoperimetric optima]")
    hdr = "   p  nmax |" + "".join("%9d" % i for i in range(args.jmax + 1)) + "   status"
    print(hdr)
    print("-" * len(hdr))
    for p in sorted(running):
        nm = running[p]
        status = "complete" if nm <= nmaxcensus else "TRUNCATED by census"
        row = "%4d  %4d |" % (p, nm)
        for i in range(args.jmax + 1):
            nn = nm - i
            row += "%9s" % (tab.get((nn, p), 0) if nn >= 1 else "-")
        print(row + "   " + status)
    print()

    # --- the first thing to look at: are the p-indexed columns constant?
    print("p-indexed column differences (complete rows only) -- constant column")
    print("means the entry does not depend on p; linear means it grows with the")
    print("boundary length.")
    complete = [p for p in sorted(running) if running[p] <= nmaxcensus]
    for i in range(args.jmax + 1):
        vals = [(p, tab.get((running[p] - i, p), 0)) for p in complete
                if running[p] - i >= 1]
        if not vals:
            continue
        seq = [v for _, v in vals]
        d1 = [b - a for a, b in zip(seq, seq[1:])]
        d2 = [b - a for a, b in zip(d1, d1[1:])]
        print("  i=%d  p=%-3d..%-3d  %s" % (i, vals[0][0], vals[-1][0], seq))
        print("        d1 %s" % d1)
        print("        d2 %s" % d2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
