#!/usr/bin/env python3
"""Assemble a(n) mod 4 (and mod 8 where the inputs reach) from subgroup counts.

D4 acts on fixed king animals; orbit sizes divide 8, so with n_k = #orbits of
size k,  a(n) = n1 + 2 n2 + 4 n4 + 8 n8.  Writing I(H) for the number of fixed
animals invariant under a subgroup H <= D4 and F(H) for those with stabiliser
EXACTLY H (so I(H) = sum over K >= H of F(K)):

  n1 = F(D4) = I(D4)
  2 n2 = F(C4) + F(D2ax) + F(D2diag)
       = I(C4) + I(D2ax) + I(D2diag) - 3 I(D4)
  4 n4 = F(C2) + 2 F(<h>) + 2 F(<d>)
       = [Fix(r180) - I(C4) - I(D2ax) - I(D2diag) + 2 I(D4)]
         + 2 [Fix(h) - I(D2ax)] + 2 [Fix(d) - I(D2diag)]

giving

  a(n) = I(C4) + I(D2ax) + I(D2diag) - 2 I(D4)                        (mod 4)
  a(n) = Fix(r180) + 2 Fix(h) + 2 Fix(d) - I(D2ax) - I(D2diag)        (mod 8)

The mod-4 line needs only the three order-4 subgroups, each a quotient-domain
family of size ~lambda^(n/4) -- reachable to n=40 on a laptop.  The mod-8 line
additionally needs the per-ELEMENT counts Fix(h) and Fix(d), which are
lambda^(n/2) families and stop at the banked n=34 / n=33.

Inputs: results/subgroup_counts.txt (this campaign), results/sym_counts.txt
(banked Fix(g)), results/b006770_upload.txt (the sequence under test).

Usage: python3 experiments/subgroup_mod4.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_keyed(path):
    """Parse '<key> <n> <value>' lines into {key: {n: value}}."""
    out = {}
    with open(os.path.join(ROOT, path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) != 3:
                continue
            key, n, v = parts
            out.setdefault(key, {})[int(n)] = int(v)
    return out


def read_bfile(path):
    terms = {}
    with open(os.path.join(ROOT, path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                n, v = line.split()
                terms[int(n)] = int(v)
    return terms


# The a(40) run's own height bands, from results/ns_a40/PROVENANCE.md's
# "Corroboration by mass" table -- so the coverage below is reported against
# the same partition that states which bands had no second source.
BANDS = [("H1-10", 1, 10), ("H11-14", 11, 14), ("H15-19", 15, 19),
         ("H20", 20, 20), ("H21", 21, 21), ("H22-40", 22, 40)]


def triangle_parity(maxn):
    """T(n,H) = I_H(D2ax) (mod 2), cell by cell, against the a(40) triangle.

    D2ax = {e, h, v, r180} is exactly the height-preserving subgroup of D4
    (r90, r270 and both diagonal mirrors swap height with width), so it acts
    on the animals of each fixed height and orbit sizes there divide 4.
    """
    ph = os.path.join(ROOT, "results", "ns_a40", "perheight")
    if not os.path.isdir(ph):
        print("\nno results/ns_a40/perheight -- skipping the triangle check")
        return 0
    tri = {}
    for h in range(1, 41):
        f = os.path.join(ph, f"h{h}.out")
        if not os.path.exists(f):
            continue
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    n, v = line.split()
                    if int(v):
                        tri[(int(n), h)] = int(v)

    byh = {}
    with open(os.path.join(ROOT, "results/subgroup_d2ax_byheight.txt")) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                n, h, v = (int(x) for x in line.split())
                byh[(n, h)] = v

    print(f"\nT(n,H) = I_H(D2ax) (mod 2), a(40) triangle vs subgroup counts")
    print(f"{'band':>8} {'cells':>7} {'mass share of a(40)':>20} {'mismatches':>11}")
    a40 = sum(v for (n, _h), v in tri.items() if n == 40)
    total_bad, total_cells = [], 0
    for label, lo, hi in BANDS:
        cells = [(n, h) for (n, h) in tri if lo <= h <= hi and n <= maxn]
        bad = [c for c in cells if (tri[c] - byh.get(c, 0)) % 2]
        share = sum(tri[(40, h)] for h in range(lo, hi + 1)
                    if (40, h) in tri) / a40 if a40 else 0
        total_bad += bad
        total_cells += len(cells)
        print(f"{label:>8} {len(cells):>7} {100 * share:>19.2f}% "
              f"{len(bad) if bad else 0:>11}")
    print(f"{'TOTAL':>8} {total_cells:>7} {100.0:>19.2f}% "
          f"{len(total_bad):>11}")
    if total_bad:
        print(f"  MISMATCHED CELLS: {sorted(total_bad)[:20]}")
    return 1 if total_bad else 0


def main():
    sub = read_keyed("results/subgroup_counts.txt")
    banked = read_keyed("results/sym_counts.txt")
    a = read_bfile("results/b006770_upload.txt")
    fail = 0

    def g(d, n):
        return d.get(n, 0)

    # Regression: the c4 column recomputes what the sym34 farm banked as r90.
    # Same object by a different route (the subgroup CLI path), so any drift
    # here is a bug in this campaign, not a new result.
    r90 = banked["r90"]
    bad = sorted({n for n in set(sub["c4"]) | set(r90)
                  if n <= max(r90) and g(sub["c4"], n) != g(r90, n)})
    print(f"c4 vs banked r90 (n<={max(r90)}): "
          f"{'MISMATCH ' + str(bad) if bad else 'identical on all rows'}")
    fail += bool(bad)

    maxn = max(sub["c4"])
    print(f"\n{'n':>3} {'a(n) mod 4':>10} {'predicted':>10} "
          f"{'a(n) mod 8':>10} {'predicted':>10}")
    mod4_bad, mod8_bad, mod8_rows = [], [], 0
    for n in range(1, maxn + 1):
        p4 = (g(sub["c4"], n) + g(sub["d2ax"], n) + g(sub["d2diag"], n)
              - 2 * g(sub["d4"], n)) % 4
        ok4 = (n in a) and a[n] % 4 == p4
        if n in a and not ok4:
            mod4_bad.append(n)
        # mod 8 only where the expensive per-element counts exist.
        have8 = (n in banked["r180"] and n in banked["hmirror"]
                 and (n in banked["dmirror33"] or n in banked["dmirror32"]))
        if have8:
            fixd = banked["dmirror33"].get(n, banked["dmirror32"].get(n, 0))
            p8 = (g(banked["r180"], n) + 2 * g(banked["hmirror"], n)
                  + 2 * fixd - g(sub["d2ax"], n) - g(sub["d2diag"], n)) % 8
            mod8_rows += 1
            if n in a and a[n] % 8 != p8:
                mod8_bad.append(n)
            s8 = f"{a[n] % 8:>10} {p8:>10}" if n in a else f"{'-':>10} {p8:>10}"
        else:
            s8 = f"{'-':>10} {'-':>10}"
        s4 = f"{a[n] % 4:>10}" if n in a else f"{'-':>10}"
        print(f"{n:>3} {s4} {p4:>10} {s8}")

    print(f"\nmod 4: {maxn} rows predicted, "
          f"{sum(1 for n in range(1, maxn + 1) if n in a)} comparable, "
          f"{'MISMATCH ' + str(mod4_bad) if mod4_bad else '0 mismatches'}")
    print(f"mod 8: {mod8_rows} rows predicted, "
          f"{'MISMATCH ' + str(mod8_bad) if mod8_bad else '0 mismatches'}")
    fail += bool(mod4_bad) + bool(mod8_bad)

    fail += triangle_parity(maxn)

    if maxn in a:
        print(f"\na({maxn}) = {a[maxn]}")
        print(f"  banked   mod 4 = {a[maxn] % 4}")
        p4 = (g(sub['c4'], maxn) + g(sub['d2ax'], maxn)
              + g(sub['d2diag'], maxn) - 2 * g(sub['d4'], maxn)) % 4
        print(f"  subgroup mod 4 = {p4}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
