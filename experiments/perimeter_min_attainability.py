#!/usr/bin/env python3
"""Why some minimum-perimeter columns go constant and others grow.

results/perimeter-both-ends.md reports, without explaining it, that on king the
even-p columns of C(p,i) = A(nmax(p)-i, p) stabilise while the odd-p ones grow,
and that on square4 ALL FOUR residue classes stabilise. The hypothesis tested
here is that the split has nothing to do with parity as such:

    C(p, .) stabilises  <=>  p is ATTAINED as pmin(n) for some n,

i.e. p is an isoperimetric perimeter. King's pmin = 2*ceil(2*sqrt(n)) + 4 is
always even, so no odd p is ever attained and every odd column is a count of
animals whose perimeter is one unit worse than any optimum -- a different
population, with a positional freedom that grows with the boundary. square4's
pmin = 2 + ceil(sqrt(8n-4)) attains every integer past a small exception, so
every column there sits on an attained perimeter and stabilises.

Two things are computed, both from the census already on disk:

  1. the attained set of each lattice, and whether it lines up with the
     stabilising columns cell for cell;
  2. for the columns that do NOT stabilise, the closed form in p -- fitted
     exactly over the rationals with holdouts, so a reported degree is
     overdetermined rather than assumed.

    python3 experiments/perimeter_min_attainability.py results/perimmin_square8_p40_r6.txt --lattice square8
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import defaultdict
from fractions import Fraction


def isqrt_ceil(v: int) -> int:
    r = math.isqrt(v)
    return r if r * r == v else r + 1


PMIN = {
    "square4": lambda n: 2 + isqrt_ceil(8 * n - 4),      # A261491
    "square8": lambda n: 2 * isqrt_ceil(4 * n) + 4,      # A235382
}

HOLDOUTS = 2


def solve_exact(rows):
    m = len(rows)
    A = [list(r) for r in rows]
    for c in range(m):
        piv = next((r for r in range(c, m) if A[r][c] != 0), None)
        if piv is None:
            return None
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]
        A[c] = [v / pv for v in A[c]]
        for r in range(m):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [A[r][m] for r in range(m)]


def fit_poly(pts, degree):
    """pts = [(p, value)]; exact fit of a degree-`degree` polynomial + holdouts."""
    if len(pts) < degree + 1 + HOLDOUTS:
        return None
    rows = [[Fraction(p) ** j for j in range(degree + 1)] + [Fraction(v)]
            for p, v in pts[:degree + 1]]
    co = solve_exact(rows)
    if co is None:
        return None
    for p, v in pts[degree + 1:]:
        if sum(c * Fraction(p) ** j for j, c in enumerate(co)) != v:
            return None
    return co


def show(co):
    terms = []
    for j in range(len(co) - 1, -1, -1):
        c = co[j]
        if c == 0:
            continue
        terms.append("%s%s" % (c, "" if j == 0 else ("*p" if j == 1 else "*p^%d" % j)))
    return " + ".join(terms) if terms else "0"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("census")
    ap.add_argument("--lattice", required=True, choices=sorted(PMIN))
    args = ap.parse_args()

    pmax_hdr = rmax_hdr = None
    tab = defaultdict(int)
    for line in open(args.census):
        if line.startswith("#"):
            m = re.search(r"pmax=(\d+) rmax=(-?\d+)", line)
            if m:
                pmax_hdr, rmax_hdr = int(m.group(1)), int(m.group(2))
            continue
        if not line.strip():
            continue
        n, p, c = (int(f) for f in line.split())
        tab[(n, p)] += c
    if pmax_hdr is None:
        print("census has no perimeter_min header")
        return 1
    imax = rmax_hdr
    pmin = PMIN[args.lattice]

    attained = set()
    nmax_of = {}
    n = 1
    while pmin(n) <= pmax_hdr:
        attained.add(pmin(n))
        nmax_of[pmin(n)] = n
        n += 1
    best, running = 0, {}
    for p in range(min(nmax_of), pmax_hdr + 1):
        if p in nmax_of:
            best = nmax_of[p]
        if best:
            running[p] = best

    ps_all = sorted(running)
    print("lattice %s   p <= %d   deficit i <= %d" % (args.lattice, pmax_hdr, imax))
    print("attained pmin values in range: %s"
          % sorted(x for x in attained if x <= pmax_hdr))
    print("NOT attained: %s"
          % [p for p in ps_all if p not in attained])
    print()

    print("== 1. does 'attained' predict 'stabilises'?")
    print("   p-class | attained | column i=1 stabilises?")
    agree = True
    for p in ps_all:
        pass
    # judge stabilisation per p-residue class mod 4, using column i=1
    for cls in range(4):
        ps = [p for p in ps_all if p % 4 == cls]
        if not ps:
            continue
        att = all(p in attained for p in ps[2:])   # ignore tiny p
        seq = [tab.get((running[p] - 1, p), 0) for p in ps if running[p] - 1 >= 1]
        stab = len(seq) >= 3 and len(set(seq[-3:])) == 1
        ok = (att == stab)
        agree &= ok
        print("   %d mod 4 | %-8s | %-5s  %s"
              % (cls, att, stab, "" if ok else "<-- HYPOTHESIS FAILS"))
    print()
    print("   hypothesis holds on this lattice: %s" % agree)
    print()

    print("== 2. closed forms for the columns that do NOT stabilise")
    found_any = False
    for cls in range(4):
        ps = [p for p in ps_all if p % 4 == cls]
        if not ps or all(p in attained for p in ps[2:]):
            continue
        for i in range(imax + 1):
            live = [(p, tab.get((running[p] - i, p), 0))
                    for p in ps if running[p] - i >= 1]
            # drop the leading pre-regime zeros, which are a different regime
            while live and live[0][1] == 0:
                live = live[1:]
            got = None
            for degree in range(0, 4):
                co = fit_poly(live, degree)
                if co is not None:
                    got = (degree, co)
                    break
            if got:
                found_any = True
                print("   p=%d mod 4, i=%d  (from p=%d, %d pts)  degree %d:  %s"
                      % (cls, i, live[0][0], len(live), got[0], show(got[1])))
            else:
                print("   p=%d mod 4, i=%d  (%d pts)  no fit up to degree 3"
                      % (cls, i, len(live)))
    if not found_any:
        print("   (every column on this lattice stabilises -- nothing to fit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
