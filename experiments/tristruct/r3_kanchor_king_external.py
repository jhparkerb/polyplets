#!/usr/bin/env python3
"""r3_kanchor_king_external.py — the KING rule schema vs the external A006770 prefix.

ADV3-S2 (results/triangle-r3-king-anchor.md): r3_adv3_rook_schema.py showed the
shared schema (harness Part 3, props 1-3) reproduces external SQUARE-lattice
data, but no square agreement can test the king-specific cross-cut content
{r-1, r+1}.  This script runs the king schema spec — the sweep of
r3_l3_schema_dp.py, byte-identical, king stencil (r-1, r, r+1) — and compares
its ROW SUMS  sum_H T(n,H)  against the externally published prefix of
A006770, the only external king-lattice arithmetic in existence:

    n <= 10   Peters, Stauffer, Hoelters & Loewenich, Z. Phys. B 34 (1979) 399
              (attribution per Mertens 1990 ref. 11)
    n <= 14   S. Mertens, J. Stat. Phys. 58 (1990) 1095-1108, Table I
              "nnSquare" (papers/mertens_1990_lattice_animals.pdf)
    n <= 16   D. H. Redelmeier, emails to N. J. A. Sloane, 16 Jul 1991
              (oeis.org/A006770/a006770.pdf — terms read from the scan)
    n  = 17   Joseph Myers, OEIS extension line, Sep 26 2002
    n  = 18   Tremblay & Vernay, RAIRO-ITA 58 (2024) Art. 16, p. 13,
              doi:10.1051/ita/2024013 (added to OEIS Dec 2025)

Derivation independence: this file imports NO banked data — the only numbers
it consumes are the 18 external terms below and its own arithmetic.

Usage: r3_kanchor_king_external.py [NMAX] [--red]
  --red corrupts one COMPARED external term (n <= NMAX); the run must ABORT.
Fail-closed: any row-sum mismatch against the external prefix aborts nonzero.
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

# A006770 external prefix (offset 1), per-term provenance in the docstring.
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180,
           39299408, 257105146, 1692931066, 11208974860, 74570549714,
           498174818986, 3340366308393, 22471158811164]
if RED:
    k = min(NMAX, len(A006770)) - 1   # corrupt a COMPARED term, largest n
    A006770[k] += 1
    print(f'RED: corrupted external term a({k+1})')


def canon(labels):
    m, nxt, out = {}, 1, []
    for L in labels:
        if L == 0:
            out.append(0)
        else:
            if L not in m:
                m[L] = nxt; nxt += 1
            out.append(m[L])
    return tuple(out)


def column_states(mask, H):
    labels = [0]*H; cur = 0
    for r in range(H):
        if mask >> r & 1:
            if r > 0 and mask >> (r-1) & 1:
                labels[r] = cur
            else:
                cur += 1; labels[r] = cur
    return canon(labels)


def sweep(H, nmax):
    """Byte-identical to r3_l3_schema_dp.sweep — the KING stencil (r-1,r,r+1)."""
    result = defaultdict(int)
    counts = {}
    masks = list(range(1, 1 << H))
    for mask in masks:
        st = (column_states(mask, H),
              bool(mask & 1), bool(mask >> (H-1) & 1))
        c = bin(mask).count('1')
        if c <= nmax:
            counts.setdefault(st, defaultdict(int))[c] += 1
    peak_states = len(counts)
    while counts:
        for (labels, tb, tt), vec in counts.items():
            if tb and tt and max(labels) == 1 and min(
                    l for l in labels if l) == 1:
                for c, v in vec.items():
                    result[c] += v
        newcounts = {}
        for (labels, tb, tt), vec in counts.items():
            for mask in masks:
                c_new = bin(mask).count('1')
                nold = max(labels)
                parent = list(range(H + nold + 1))
                def find(x):
                    while parent[x] != x:
                        parent[x] = parent[parent[x]]; x = parent[x]
                    return x
                def unite(x, y):
                    rx, ry = find(x), find(y)
                    if rx != ry: parent[rx] = ry
                for r in range(H):
                    if mask >> r & 1:
                        if r > 0 and mask >> (r-1) & 1:
                            unite(r, r-1)
                        for rr in (r-1, r, r+1):       # the king stencil
                            if 0 <= rr < H and labels[rr]:
                                unite(r, H + labels[rr])
                touched = set(find(H + L) for L in range(1, nold + 1)
                              if any(mask >> r & 1 and find(r) == find(H + L)
                                     for r in range(H)))
                roots_old = set(find(H + L) for L in range(1, nold + 1))
                if any(root not in touched for root in roots_old):
                    continue
                newlabels = canon(tuple(
                    (find(r) + 1) if mask >> r & 1 else 0 for r in range(H)))
                st = (newlabels,
                      tb or bool(mask & 1), tt or bool(mask >> (H-1) & 1))
                add = {c + c_new: v for c, v in vec.items()
                       if c + c_new <= nmax}
                if not add:
                    continue
                tgt = newcounts.setdefault(st, defaultdict(int))
                for c, v in add.items():
                    tgt[c] += v
        counts = newcounts
        peak_states = max(peak_states, len(counts))
    return result, peak_states


t_all0 = time.time()
rowsum = defaultdict(int)
for H in range(1, NMAX + 1):
    t0 = time.time()
    res, peak = sweep(H, NMAX)
    for n, v in res.items():
        rowsum[n] += v
    print(f'H={H:2d}: swept to n<={NMAX}, peak states={peak}, '
          f'{time.time()-t0:.2f} s', flush=True)

bad = ok = 0
for n in range(1, min(NMAX, len(A006770)) + 1):
    got, want = rowsum[n], A006770[n - 1]
    if got != want:
        bad += 1
        print(f'  n={n}: schema row sum={got} external={want}  MISMATCH')
    else:
        ok += 1
        print(f'  n={n}: {got}  OK (external)')
if bad:
    sys.exit(f'ABORT: {bad} mismatches against the external A006770 prefix')
print(f'ALL EXTERNAL CHECKS PASS: {ok} row-sum comparisons vs A006770 '
      f'({time.time()-t_all0:.1f} s total)')
