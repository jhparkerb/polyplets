#!/usr/bin/env python3
"""p2_symdiag.py -- diagonal structure of the symmetry-refined triangle:
I(n, n-k) as a parity-split polynomial in n (quasi-polynomial, period 2).

BLIND protocol: polynomials are fitted on SELF-ENUMERATED cells only
(p2_enum --sym klein column, data/p2_sym_n14.txt, own connectivity rule,
n <= 14). The banked I file (results/subgroup_d2ax_byheight.txt, symcount
lineage, n <= 40) is used ONLY as holdout: every matched banked cell with
n >= 15 is a genuine prediction. Exact arithmetic (Fraction).

For each k and each parity class of n (odd-n class is identically 0 when k
is odd -- proved, results/triangle-hunt-klein-parity.md):
  - fit degree d = 0,1,2,... by Lagrange on the TOP d+1 self points;
  - onset = smallest n from which the polynomial matches self data
    contiguously; require >= d+2 matching self points beyond the fitted
    ones... (i.e. total contiguous matches >= 2d+3) else "inconclusive";
  - holdout: banked cells n = 15..40 past onset, all must match exactly.

Run from experiments/tristruct/:  python3 p2_symdiag.py
"""
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SELF = os.path.join(HERE, 'data', 'p2_sym_n14.txt')
NSELF = 14

def load_self():
    d = {}
    with open(SELF) as f:
        for ln in f:
            p = [int(x) for x in ln.split()]
            d[(p[0], p[1])] = p[6]   # klein column
    return d

def load_I():
    d = {}
    with open(os.path.join(ROOT, 'results/subgroup_d2ax_byheight.txt')) as f:
        for ln in f:
            n, H, c = (int(x) for x in ln.split())
            d[(n, H)] = c
    return d

def lagrange(pts):
    """pts: [(x,y)] -> callable exact poly evaluator."""
    def ev(x):
        s = Fraction(0)
        for i, (xi, yi) in enumerate(pts):
            t = Fraction(yi)
            for j, (xj, _) in enumerate(pts):
                if i != j:
                    t *= Fraction(x - xj, xi - xj)
            s += t
        return s
    return ev

def poly_str(pts):
    """Readable form via finite differences on consecutive class points."""
    return "through " + ", ".join("(%d,%d)" % p for p in pts)

def main():
    selfd = load_self()
    banked = load_I()
    print("Symmetric-triangle diagonals I(n,n-k): blind fit on self data "
          "(n<=%d), banked n>=15 pure holdout" % NSELF)
    for k in range(0, 9):
        for par in (0, 1):
            if k % 2 == 1 and par == 1:
                continue   # proved zero
            ns = [n for n in range(k + 1, NSELF + 1)
                  if n % 2 == par and (n, n - k) in selfd]
            vals = {n: selfd[(n, n - k)] for n in ns}
            if len(ns) < 3:
                print("k=%d n%%2=%d: too few self points" % (k, par))
                continue
            found = False
            for d in range(0, 4):
                if len(ns) < d + 2:
                    break
                top = ns[-(d + 1):]
                ev = lagrange([(n, vals[n]) for n in top])
                # onset: extend downward through self data
                onset = top[0]
                for n in reversed([m for m in ns if m < top[0]]):
                    if ev(n) == vals[n]:
                        onset = n
                    else:
                        break
                matches = len([n for n in ns if n >= onset])
                if matches < 2 * d + 3:
                    continue
                hold = [(n, banked.get((n, n - k), 0))
                        for n in range(15, 41) if n % 2 == par and n - k >= 1]
                misses = [(n, v, ev(n)) for n, v in hold if ev(n) != v]
                verdict = ("HOLDOUT %d/%d ALL PASS" % (len(hold), len(hold))
                           if not misses else
                           "FAILS first at n=%d (pred %s, banked %d)"
                           % (misses[0][0], misses[0][2], misses[0][1]))
                print("k=%d n%%2=%d: deg %d, onset n=%d (%d self matches), %s"
                      % (k, par, d, onset, matches, verdict))
                if not misses:
                    # print the polynomial via values at top points
                    print("    fit points: %s" % poly_str(
                        [(n, vals[n]) for n in top]))
                    found = True
                break
            if not found:
                print("k=%d n%%2=%d: no deg<=3 quasi-poly confirmed blind "
                      "(self reach n<=%d)" % (k, par, NSELF))
                phase2(banked, k, par)

def phase2(banked, k, par):
    """Declared fallback (NOT blind): fit on banked n<=22, onset within
    banked, holdout = banked n=23..40 strictly. Derivation touches banked
    fit-region cells; independence scored lower, stated in the writeup."""
    ns = [n for n in range(k + 1, 23) if n % 2 == par
          and (n, n - k) in banked]
    vals = {n: banked[(n, n - k)] for n in ns}
    if len(ns) < 4:
        print("    phase2: too few banked fit points")
        return
    for d in range(0, 5):
        if len(ns) < d + 2:
            break
        top = ns[-(d + 1):]
        ev = lagrange([(n, vals[n]) for n in top])
        onset = top[0]
        for n in reversed([m for m in ns if m < top[0]]):
            if ev(n) == vals[n]:
                onset = n
            else:
                break
        matches = len([n for n in ns if n >= onset])
        if matches < 2 * d + 3:
            continue
        hold = [(n, banked.get((n, n - k), 0))
                for n in range(23, 41) if n % 2 == par and n - k >= 1]
        misses = [(n, v, ev(n)) for n, v in hold if ev(n) != v]
        if not misses:
            print("    phase2 (fit banked n<=22): deg %d, onset n=%d "
                  "(%d fit matches), HOLDOUT %d/%d ALL PASS; fit points %s"
                  % (d, onset, matches, len(hold), len(hold),
                     poly_str([(n, vals[n]) for n in top])))
        else:
            print("    phase2: deg %d fits n<=22 (onset %d) but FAILS "
                  "holdout first at n=%d (pred %s, banked %d)"
                  % (d, onset, misses[0][0], misses[0][2], misses[0][1]))
        return
    print("    phase2: no deg<=4 quasi-poly fits banked n<=22 with "
          "2d+3 support")

if __name__ == '__main__':
    main()
