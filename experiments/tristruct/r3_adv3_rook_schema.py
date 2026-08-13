#!/usr/bin/env python3
"""r3_adv3_rook_schema.py — the shared rule schema, rook stencil, vs external data.

ADV-3 (external anchor): r3_l3_schema_dp.py implements the three shared
propositions of results/triangle-r3-harness.md Part 3 verbatim and reproduces
the banked king triangle.  Those propositions are lattice-generic: swapping the
cross-cut stencil {r-1, r, r+1} -> {r} (and nothing else) must yield fixed
SQUARE-LATTICE polyominoes counted by height of the bounding box — numbers
published by other people, computed by other methods:

  - A292357 a-file (Andrew Howroyd): fixed polyominoes by (width, height,
    cells) for all boxes with width+height <= 24 — complete per-height sums
    T_sq(n,H) for every n <= 23.  Local copy: r3_adv3_a292357.txt.
  - A027053 = column w=2 of A308359 (R. J. Mathar): fixed n-ominoes of
    bounding-box width exactly 2, n <= 33.  By the transpose bijection this
    is T_sq(n, H=2).
  - A335606: width exactly 3, n <= 33 (Zeilberger: order-14 linear
    recurrence, so extensible to any n).  = T_sq(n, H=3).
  - Row sums must equal A001168 (fixed polyominoes, banked to n=70 in
    papers/counting_polyominoes_revisited.pdf lineage).

The DIFF against r3_l3_schema_dp.py is exactly one line: the stencil tuple
(r-1, r, r+1) -> (r,).  Propositions 2 (label partition sufficiency +
stranded-component death) and 3 (one component + both touch flags = height
exactly H) are byte-identical.  Agreement therefore externally corroborates
props 2+3 and the generic shape of prop 1; the king-specific stencil CONTENT
({r-1, r+1} across the cut) stays untested — say so wherever this is cited.

Usage: r3_adv3_rook_schema.py [NMAX] [--red]
  --red corrupts one external table entry; the run must then ABORT.
Fail-closed: any mismatch against any external source aborts nonzero.
"""
import os, sys, time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
NMAX = 8
RED = False
for a in sys.argv[1:]:
    if a == '--red':
        RED = True
    else:
        NMAX = int(a)

# ---- external data ---------------------------------------------------------
# A027053 (offset 2): T_sq(n, H=2) for n = 2..33 (transpose of width-2).
A027053 = [1, 4, 9, 18, 35, 66, 123, 228, 421, 776, 1429, 2630, 4839, 8902,
           16375, 30120, 55401, 101900, 187425, 344730, 634059, 1166218,
           2145011, 3945292, 7256525, 13346832, 24548653, 45152014, 83047503,
           152748174, 280947695, 516743376]
# A335606 (offset 3): T_sq(n, H=3) for n = 3..33.
A335606 = [1, 8, 31, 95, 269, 721, 1866, 4728, 11804, 29162, 71502, 174342,
           423341, 1024786, 2474934, 5966625, 14365256, 34550674, 83035396,
           199440433, 478814076, 1149133511, 2757142136, 6613933242,
           15863281135, 38042981575, 91225540813, 218739876078, 524464594304,
           1257437814143, 3014693395137]
# A001168 (offset 1): fixed polyominoes, first 23 terms (row-sum control).
A001168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910, 36446, 135268, 505861,
           1903890, 7204874, 27394666, 104592937, 400795844, 1540820542,
           5940738676, 22964779660, 88983512783, 345532572678, 1344372335524]


def load_box_table():
    """Howroyd a292357.txt -> ext[(n,H)] = sum over widths, where complete.

    File rows: width a <= height b, cells n, count = B(n, a, b) = B(n, b, a).
    T_sq(n,H) = sum_W B(n,W,H); every occurring width W <= n-H+1, so the sum
    is complete from the file (coverage a+b <= 24) iff n <= 23.
    """
    box = {}
    with open(os.path.join(HERE, 'r3_adv3_a292357.txt')) as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            a, b, n, c = map(int, line.split())
            box[(n, a, b)] = c
            box[(n, b, a)] = c
    if RED:
        # must corrupt a cell the run actually compares (n <= NMAX), else the
        # control is blind — first version of this guard was, caught red-first
        k = max(k for k in box if k[0] <= NMAX)
        box[k] += 1
        print(f'RED: corrupted box entry {k}')
    ext = defaultdict(int)
    for (n, w, h), c in box.items():
        if n <= 23:
            ext[(n, h)] += c
    return ext


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
    """Identical to r3_l3_schema_dp.sweep except the one stencil line."""
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
                        for rr in (r,):            # THE DIFF: rook stencil
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


ext = load_box_table()
bad = ok = 0
T = {}
t_all0 = time.time()
for H in range(1, NMAX + 1):
    t0 = time.time()
    res, peak = sweep(H, NMAX)
    dt = time.time() - t0
    for n in range(H, NMAX + 1):
        got = res.get(n, 0)
        T[(n, H)] = got
        want = ext.get((n, H))
        if want is None:
            continue
        if got != want:
            bad += 1
            print(f'  T_sq({n},{H}) schema={got} howroyd={want}  MISMATCH')
        else:
            ok += 1
    print(f'H={H:2d}: n<={NMAX} swept, peak states={peak}, {dt:.2f} s')

# tall-narrow externals, far past the box table: H=2 vs A027053, H=3 vs A335606
for H, seq, off, lim in ((2, A027053, 2, 33), (3, A335606, 3, 33)):
    t0 = time.time()
    res, _ = sweep(H, lim)
    for i, want in enumerate(seq):
        n = off + i
        got = res.get(n, 0)
        if got != want:
            bad += 1
            print(f'  T_sq({n},{H}) schema={got} oeis={want}  MISMATCH')
        else:
            ok += 1
    print(f'H={H} deep run to n={lim} vs OEIS column: {time.time()-t0:.2f} s')

# row-sum control vs A001168 over fully-swept rows (n <= NMAX needs all H <= n)
for n in range(1, NMAX + 1):
    s = sum(T.get((n, H), 0) for H in range(1, n + 1))
    if s != A001168[n - 1]:
        bad += 1
        print(f'  row {n}: sum={s} A001168={A001168[n-1]}  MISMATCH')
    else:
        ok += 1

if bad:
    sys.exit(f'ABORT: {bad} mismatches against external square-lattice data')
print(f'ALL EXTERNAL CHECKS PASS: {ok} comparisons '
      f'(box table n<={NMAX}, H=2 to n=33, H=3 to n=33, row sums) '
      f'({time.time()-t_all0:.1f} s total)')
