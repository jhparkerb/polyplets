#!/usr/bin/env python3
"""refB_parity_check.py -- Refuter B checks on Proposer 2's parity claims.

A. Region audit: cells {n odd, H even, H<=n} for n<=40 -- count them,
   confirm zero cells lie in row 40, and check T(n,H) == 0 (mod 2) on all
   of them, reading the banked per-height files DIRECTLY (own loader, not
   triangle.py; one cell cross-checked against triangle.py).
B. Zero-set exactness: results/subgroup_d2ax_byheight.txt has 630 rows and
   no explicit zeros. Verify (i) every listed count > 0, (ii) the missing
   cells of the 820-cell grid are EXACTLY the 190-cell region.
C. Corollary check: P_k(n) == I(n,n-k) (mod 2) for n >= 2k+1, k <= 13,
   via parity of T(n,n-k) (3^m is odd, so P_k == T on the diagonal), and
   T == I (mod 2) checked cell-by-cell on those diagonal cells.

Run from experiments/tristruct/:  python3 refB_parity_check.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NMAX = 40


def load_T_direct():
    cells = {}
    for H in range(1, NMAX + 1):
        with open(os.path.join(ROOT, 'results/ns_a40/perheight/h%d.out' % H)) as f:
            for ln in f:
                if ln.strip():
                    n, v = (int(x) for x in ln.split())
                    cells[(n, H)] = v
    return cells


def load_I():
    d = {}
    with open(os.path.join(ROOT, 'results/subgroup_d2ax_byheight.txt')) as f:
        for ln in f:
            n, H, c = (int(x) for x in ln.split())
            d[(n, H)] = c
    return d


def main():
    T = load_T_direct()
    I = load_I()

    # sanity: own loader vs triangle.py on one big cell
    from triangle import Triangle
    tri = Triangle.load()
    assert T[(40, 21)] == tri.cell(40, 21), "loader mismatch"

    # A. region audit
    region = [(n, H) for n in range(1, 41) for H in range(1, n + 1)
              if n % 2 == 1 and H % 2 == 0]
    row40 = [c for c in region if c[0] == 40]
    odd_parity = [(n, H) for (n, H) in region if T[(n, H)] % 2 != 0]
    print("A. region cells: %d  (expected 190); row-40 cells: %d (expected 0)"
          % (len(region), len(row40)))
    print("A. cells violating T(n,H) even: %d %s"
          % (len(odd_parity), odd_parity[:10] if odd_parity else ""))
    # region cells where T is actually nonzero (an even-zero would make the
    # parity bit vacuous on that cell)
    vac = [(n, H) for (n, H) in region if T[(n, H)] == 0]
    print("A. region cells with T(n,H)=0 (parity bit vacuous there): %d %s"
          % (len(vac), vac if len(vac) < 12 else vac[:12]))

    # B. zero-set exactness of banked I
    neg = [(k, v) for k, v in I.items() if v <= 0]
    grid = {(n, H) for n in range(1, 41) for H in range(1, n + 1)}
    missing = sorted(grid - set(I))
    not_region = [c for c in missing if not (c[0] % 2 == 1 and c[1] % 2 == 0)]
    region_present = [c for c in region if c in I]
    print("B. listed I counts <= 0: %d; missing grid cells: %d;"
          % (len(neg), len(missing)))
    print("B. missing cells NOT in {n odd,H even}: %d %s"
          % (len(not_region), not_region[:10]))
    print("B. region cells PRESENT in file (should be 0): %d %s"
          % (len(region_present), region_present[:10]))

    # C. diagonal parity corollary, k <= 13 (diagonal law solved region)
    bad = []
    checked = 0
    for k in range(0, 14):
        for n in range(2 * k + 1, 41):
            H = n - k
            if H < 1:
                continue
            checked += 1
            if T[(n, H)] % 2 != I.get((n, H), 0) % 2:
                bad.append((n, H))
    print("C. diagonal cells checked (n>=2k+1, k<=13): %d; T vs I parity "
          "mismatches: %d %s" % (checked, len(bad), bad[:10]))


if __name__ == '__main__':
    main()
