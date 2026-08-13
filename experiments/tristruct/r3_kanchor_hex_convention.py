#!/usr/bin/env python3
"""r3_kanchor_hex_convention.py — pin the Apagodu-Chow polyhex height convention.

ADV3-S1 (results/triangle-r3-king-anchor.md): external per-height polyhex data
exists — Apagodu & Chow, "Counting hexagonal lattice animals confined to a
strip", arXiv:math/0202295v5 (2009), Table 1
(papers/apagodu_2009_hexagonal_animals_strip.pdf), reproduced as OEIS A157608.
Their height is the height of the square-lattice PARITY-POLYOMINO embedding:
each hexagon covers two half-unit rows, adjacent hex columns shift by one
half-unit.  Before any hex schema instantiation can be compared to it, that
convention must be pinned by measurement, not read off the paper.

Claim under test: with the project's axial hex adjacency
((x+-1,y),(x,y+-1),(x-1,y+1),(x+1,y-1) — experiments/hex_gas.py, validated
vs A001207), the geometric half-unit row of cell (x,y) is 2y+x, a hexagon
covers {2y+x, 2y+x+1}, and Apagodu-Chow's strip-K count is

    C(K, n) = #{ fixed n-cell hexanimals with max(2y+x)-min(2y+x)+2 <= K }.

Checked by brute enumeration against Table 1 columns K=3..6 (their n=3..6
rows) and the row-sum control A001207.  Fail-closed; --red corrupts one
compared Table-1 entry and the run must then ABORT.

Usage: r3_kanchor_hex_convention.py [NMAX] [--red]     (NMAX<=8 is seconds)
"""
import sys, time
from collections import defaultdict

NMAX = 7
RED = False
for a in sys.argv[1:]:
    if a == '--red':
        RED = True
    else:
        NMAX = int(a)

# Apagodu-Chow Table 1 series columns (strip height K in half-units, counts by
# hexagonal cell count from n=1), transcribed from the paper's Table 1.
TABLE1 = {
    2: [1, 0, 0, 0, 0, 0, 0, 0],
    3: [1, 2, 2, 2, 2, 2, 2, 2],        # GFseries(3,...) = chains
    4: [1, 3, 6, 11, 19, 32, 53, 87],
    5: [1, 3, 10, 25, 61, 142, 323, 723],
    6: [1, 3, 11, 37, 111, 320, 896],   # paper prints 7 terms for K=6
}
# A001207 (fixed polyhexes) row-sum control, external (Voege-Guttmann lineage).
A001207 = [1, 3, 11, 44, 186, 814, 3652, 16689, 77359, 362671]

if RED:
    K = max(k for k in TABLE1 if len(TABLE1[k]) >= NMAX)
    TABLE1[K][NMAX - 1] += 1
    print(f'RED: corrupted Table 1 entry (K={K}, n={NMAX})')


def hex_neighbors(c):
    x, y = c
    return [(x - 1, y), (x + 1, y), (x, y + 1), (x - 1, y + 1),
            (x, y - 1), (x + 1, y - 1)]


def canon(cells):
    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def brute(nmax):
    """All fixed hexanimals to nmax cells; tally by (n, half-unit height)."""
    seen = {canon({(0, 0)})}
    frontier = list(seen)
    byh = defaultdict(int)
    byh[(1, 2)] = 1
    tot = {1: 1}
    while frontier:
        new = []
        for A in frontier:
            if len(A) >= nmax:
                continue
            cand = set()
            for c in A:
                for nb in hex_neighbors(c):
                    if nb not in A:
                        cand.add(nb)
            for c in cand:
                B = canon(set(A) | {c})
                if B not in seen:
                    seen.add(B)
                    new.append(B)
        frontier = new
        if new:
            n = len(new[0])
            tot[n] = len(new)
            for A in new:
                halves = [2 * y + x for x, y in A]
                byh[(n, max(halves) - min(halves) + 2)] += 1
    return tot, byh


t0 = time.time()
tot, byh = brute(NMAX)
print(f'brute to n={NMAX}: {time.time()-t0:.1f} s')

bad = ok = 0
for n in range(1, NMAX + 1):
    if tot.get(n) != A001207[n - 1]:
        bad += 1
        print(f'  n={n}: brute total={tot.get(n)} A001207={A001207[n-1]}  MISMATCH')
    else:
        ok += 1
for K, series in sorted(TABLE1.items()):
    for i, want in enumerate(series):
        n = i + 1
        if n > NMAX:
            break
        got = sum(v for (nn, h), v in byh.items() if nn == n and h <= K)
        if got != want:
            bad += 1
            print(f'  C(K={K}, n={n}) brute={got} table1={want}  MISMATCH')
        else:
            ok += 1
if bad:
    sys.exit(f'ABORT: {bad} mismatches against Apagodu-Chow Table 1 / A001207')
print(f'CONVENTION PINNED: {ok} comparisons match '
      f'(half-unit height = extent of 2y+x, +2)')
