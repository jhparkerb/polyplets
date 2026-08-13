#!/usr/bin/env python3
"""r3_l3_schema_dp.py — the frontier rule schema, transcribed literally.

Purpose (L3-2 proof scoping): a from-scratch column DP implementing EXACTLY
the three shared propositions of results/triangle-r3-harness.md Part 3 —
(1) cross-cut stencil = previous column rows r-1, r, r+1;
(2) state = component-label partition of the boundary column + sticky
    touch-top/touch-bottom flags, stranded old component => dead;
(3) completion = exactly one component + both touch flags.
No code shared with any engine.  This file is the executable spec a Lean
skeleton (FrontierDef.lean) would mirror; its validation against the banked
triangle is the RED gate for that skeleton's statements.

Validation: T(n,H) for all 1 <= H <= n <= NMAX must equal the banked
triangle loaded via experiments/tristruct/triangle.py.  Fail-closed.
Also prints per-n wall time and total state counts, the anchor for pricing
native_decide pins in Lean.
"""
import sys, time
from collections import defaultdict

sys.path.insert(0, 'experiments/tristruct')
from triangle import Triangle

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 11


def canon(labels):
    """Relabel by first occurrence: the state is the partition, not names."""
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
    """Labels of a lone column: components under within-column king adjacency
    (vertical runs)."""
    labels = [0]*H; cur = 0
    for r in range(H):
        if mask >> r & 1:
            if r > 0 and mask >> (r-1) & 1:
                labels[r] = cur
            else:
                cur += 1; labels[r] = cur
    return canon(labels)


def sweep(H, nmax):
    """Returns dict n -> T(n,H).  State: (labels, touchB, touchT)."""
    result = defaultdict(int)
    # counts: state -> {cells: count}
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
        # harvest: proposition 3 — one component, both flags
        for (labels, tb, tt), vec in counts.items():
            if tb and tt and max(labels) == 1 and min(
                    l for l in labels if l) == 1:
                for c, v in vec.items():
                    result[c] += v
        newcounts = {}
        for (labels, tb, tt), vec in counts.items():
            for mask in masks:
                c_new = bin(mask).count('1')
                # union-find over: new vertical runs, and cross-cut stencil
                # slots 0..H-1 = new rows; H+L = old label L
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
                            unite(r, r-1)                      # prop 1: in-column
                        for rr in (r-1, r, r+1):               # prop 1: stencil
                            if 0 <= rr < H and labels[rr]:
                                unite(r, H + labels[rr])
                # prop 2: stranded old component => dead
                touched = set(find(H + L) for L in range(1, nold + 1)
                              if any(mask >> r & 1 and find(r) == find(H + L)
                                     for r in range(H)))
                roots_old = set(find(H + L) for L in range(1, nold + 1))
                if any(root not in touched for root in roots_old):
                    continue
                newlabels = canon(tuple(
                    (find(r) + 1) if mask >> r & 1 else 0 for r in range(H)))
                # renumber roots consistently: canon does it (names only)
                st = (newlabels,
                      tb or bool(mask & 1), tt or bool(mask >> (H-1) & 1))
                add = {c + c_new: v for c, v in vec.items()
                       if c + c_new <= nmax}
                if not add:
                    continue          # budget exhausted: prune, else no termination
                tgt = newcounts.setdefault(st, defaultdict(int))
                for c, v in add.items():
                    tgt[c] += v
        counts = newcounts
        peak_states = max(peak_states, len(counts))
    return result, peak_states


tri = Triangle.load()
t_all0 = time.time()
bad = 0
for H in range(1, NMAX + 1):
    t0 = time.time()
    res, peak = sweep(H, NMAX)
    dt = time.time() - t0
    for n in range(H, NMAX + 1):
        want = tri.cell(n, H)
        got = res.get(n, 0)
        tag = 'OK' if got == want else 'MISMATCH'
        if got != want:
            bad += 1
            print(f'  T({n},{H}) schema={got} banked={want}  {tag}')
    print(f'H={H:2d}: all n<= {NMAX} checked, peak states={peak}, {dt:.2f} s')
if bad:
    sys.exit(f'ABORT: {bad} mismatches against the banked triangle')
print(f'ALL CELLS MATCH the banked triangle for 1<=H<=n<={NMAX} '
      f'({time.time()-t_all0:.1f} s total)')
