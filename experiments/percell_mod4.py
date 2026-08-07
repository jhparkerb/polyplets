#!/usr/bin/env python3
"""Check T(n,H) mod 4 cell by cell against the a(40) triangle.

D2ax = {e, h, v, r180} is exactly the height-preserving subgroup of D4, so it
acts on the animals of each fixed height and orbit sizes there divide 4:

    T(n,H) = m1 + 2 m2 + 4 m4,  m1 = I_H(D2ax)

  ==>  T(n,H) = I_H(D2ax)                                            (mod 2)
  ==>  T(n,H) = I_H(<h>) + I_H(<v>) + I_H(C2) - 2 I_H(D2ax)          (mod 4)

(the mod-4 line: the three order-2 subgroups of D2ax are <h>, <v> and
C2 = <r180>, and 2 m2 = sum of I_H over those three, minus 3 I_H(D2ax).)

Inputs, all produced by --byheight modes:
  results/percell_raw/hmirror.byheight.n<N>.out   "n H W count"
  results/percell_raw/r180.byheight.n<N>.out      "n H count", TRUE height
  results/subgroup_d2ax_byheight.txt              "n H count"

I_H(<h>) is the hmirror table summed over W; I_H(<v>) is the SAME table
grouped by W instead, since transposing an h-symmetric W x H animal gives a
v-symmetric H x W one.

Usage: python3 experiments/percell_mod4.py [N]
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANDS = [("H1-10", 1, 10), ("H11-14", 11, 14), ("H15-19", 15, 19),
         ("H20+", 20, 40)]


def read_rows(path, arity):
    out = {}
    with open(os.path.join(ROOT, path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                p = [int(x) for x in line.split()]
                out[tuple(p[:arity])] = p[arity]
    return out


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    hm = read_rows(f"results/percell_raw/hmirror.byheight.n{N}.out", 3)
    c2 = read_rows(f"results/percell_raw/r180.byheight.n{N}.out", 2)
    d2 = read_rows("results/subgroup_d2ax_byheight.txt", 2)

    ih, iv = {}, {}
    for (n, h, w), v in hm.items():
        ih[(n, h)] = ih.get((n, h), 0) + v
        iv[(n, w)] = iv.get((n, w), 0) + v

    tri = {}
    ph = os.path.join(ROOT, "results", "ns_a40", "perheight")
    for h in range(1, N + 1):
        f = os.path.join(ph, f"h{h}.out")
        if not os.path.exists(f):
            continue
        with open(f) as fh:
            for line in fh:
                n, v = line.split()
                if int(v) and int(n) <= N:
                    tri[(int(n), h)] = int(v)

    # Regression: the flat per-n totals of both --byheight tables must equal
    # the banked per-element counts from the sym34 farm.
    banked = {}
    with open(os.path.join(ROOT, "results/sym_counts.txt")) as f:
        for line in f:
            p = line.split()
            if len(p) == 3 and p[0] in ("hmirror", "r180"):
                banked.setdefault(p[0], {})[int(p[1])] = int(p[2])
    fail = 0
    for name, tab in (("hmirror", ih), ("r180", c2)):
        flat = {}
        for (n, _h), v in tab.items():
            flat[n] = flat.get(n, 0) + v
        bad = [n for n in range(1, N + 1)
               if flat.get(n, 0) != banked[name].get(n, 0)]
        print(f"{name} byheight sums vs banked flat, n<={N}: "
              f"{'MISMATCH ' + str(bad) if bad else 'identical'}")
        fail += bool(bad)

    print(f"\n{'band':>8} {'cells':>7} {'mod 2':>8} {'mod 4':>8}")
    tot = bad2 = bad4 = 0
    for label, lo, hi in BANDS:
        cells = [(n, h) for (n, h) in tri if lo <= h <= hi]
        b2 = [c for c in cells if (tri[c] - d2.get(c, 0)) % 2]
        b4 = [c for c in cells
              if (tri[c] - (ih.get(c, 0) + iv.get(c, 0) + c2.get(c, 0)
                            - 2 * d2.get(c, 0))) % 4]
        tot += len(cells)
        bad2 += len(b2)
        bad4 += len(b4)
        print(f"{label:>8} {len(cells):>7} {len(b2):>8} {len(b4):>8}")
        if b4:
            print(f"    mod-4 mismatches: {sorted(b4)[:10]}")
    print(f"{'TOTAL':>8} {tot:>7} {bad2:>8} {bad4:>8}   (mismatch counts)")
    return 1 if (fail or bad2 or bad4) else 0


if __name__ == "__main__":
    sys.exit(main())
