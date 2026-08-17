#!/usr/bin/env python3
"""Session 02: INDEPENDENT brute-force verification of session 01's f(w,h).

Written from the definition only (results/convex-box.md, 'Objects'):
convex king animal in an exact w x h bounding box =
  subset of the w x h grid that is
  (a) row-convex: each nonempty row's cells are contiguous
  (b) column-convex: each nonempty column's cells are contiguous
  (c) king-connected: one component under 8-neighbour adjacency (checked
      by BFS on cells -- NOT by the DP's row-reach shortcut)
  (d) touches all four sides of the box.

Two independent enumerators:
  1. raw_subsets(w,h): iterate ALL 2^(wh) subsets, apply (a)-(d). Definitional
     gold standard, used for wh <= 16.
  2. interval_rows(w,h): DFS over per-row intervals (rows must all be nonempty
     in any valid config when h>=2: an empty row either shrinks the box or
     king-disconnects it), pruning only on column-convexity (a definitional
     predicate); (c) checked by BFS at the leaves, (d) checked explicitly.
     Used for larger boxes. For h==1 handled specially (single full row).

Cross-checks the two against each other where both run, then against the
banked table out_convex_box_38.txt, and verifies a(s) = sum_{w+h=s} f(w,h)
against king_semiperim_38.txt for s <= SMAX.
"""
import sys
from collections import deque

def king_connected(cells):
    if not cells:
        return False
    cs = set(cells)
    start = next(iter(cs))
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                n = (x + dx, y + dy)
                if n in cs and n not in seen:
                    seen.add(n)
                    q.append(n)
    return len(seen) == len(cs)

def ok_subset(cells, w, h):
    if not cells:
        return False
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    if min(xs) != 0 or max(xs) != w - 1 or min(ys) != 0 or max(ys) != h - 1:
        return False
    cs = set(cells)
    # row-convex
    for y in range(h):
        row = sorted(x for (x, yy) in cells if yy == y)
        if row and row != list(range(row[0], row[-1] + 1)):
            return False
    # column-convex
    for x in range(w):
        col = sorted(yy for (xx, yy) in cells if xx == x)
        if col and col != list(range(col[0], col[-1] + 1)):
            return False
    return king_connected(cells)

def raw_subsets(w, h):
    n = w * h
    cnt = 0
    cells_of = [(i % w, i // w) for i in range(n)]
    for mask in range(1, 1 << n):
        cells = [cells_of[i] for i in range(n) if (mask >> i) & 1]
        if ok_subset(cells, w, h):
            cnt += 1
    return cnt

def interval_rows(w, h):
    if h == 1:
        return 1  # must touch left+right and be row-convex: the full row
    intervals = [(l, r) for l in range(w) for r in range(l, w)]
    count = 0
    rows = [None] * h

    def col_ok_prefix(i):
        # after placing rows 0..i, check no column has pattern occ,empty,occ
        # only need to check columns that just became re-occupied at row i
        l, r = rows[i]
        for x in range(w):
            occ = [rows[j][0] <= x <= rows[j][1] for j in range(i + 1)]
            # contiguity of True-run so far: once it goes True->False it may
            # never return True
            seen_true = False
            dead = False
            for v in occ:
                if v and dead:
                    return False
                if v:
                    seen_true = True
                if seen_true and not v:
                    dead = True
        return True

    def dfs(i):
        nonlocal count
        if i == h:
            # touches left/right?
            if min(l for l, r in rows) != 0 or max(r for l, r in rows) != w - 1:
                return
            # full column-convexity (incl. columns empty then occupied is fine;
            # prefix check above already guarantees contiguity)
            cells = [(x, y) for y in range(h) for x in range(rows[y][0], rows[y][1] + 1)]
            if king_connected(cells):
                count += 1
            return
        for iv in intervals:
            rows[i] = iv
            if col_ok_prefix(i):
                dfs(i + 1)
        rows[i] = None

    dfs(0)
    return count

def load_banked():
    tab = {}
    with open('out_convex_box_38.txt') as f:
        lines = f.read().splitlines()
    idx = lines.index('f(w,h) table (rows w=1..38, cols h=1..38):')
    for w, line in enumerate(lines[idx + 1:idx + 39], start=1):
        for h, v in enumerate(line.split(), start=1):
            tab[(w, h)] = int(v)
    return tab

def main():
    banked = load_banked()
    a38 = [int(x) for x in open('king_semiperim_38.txt').read().replace(',', ' ').split()]

    print('== check 1: raw subsets (2^(wh)) vs banked, wh<=16 ==')
    ok = True
    for w in range(1, 17):
        for h in range(1, 17):
            if w * h <= 16:
                b = raw_subsets(w, h)
                match = (b == banked[(w, h)])
                ok &= match
                print(f'  f({w},{h}) raw={b} banked={banked[(w,h)]} {"OK" if match else "MISMATCH"}')
    print('check 1:', 'ALL OK' if ok else 'FAILED')

    print('== check 2: interval-DFS vs raw subsets where both ran ==')
    ok2 = True
    for w in range(1, 17):
        for h in range(2, 17):
            if w * h <= 16:
                b = interval_rows(w, h)
                match = (b == banked[(w, h)])
                ok2 &= match
                if not match:
                    print(f'  f({w},{h}) dfs={b} banked={banked[(w,h)]} MISMATCH')
    print('check 2:', 'ALL OK' if ok2 else 'FAILED')

    smax = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print(f'== check 3: a(s) via interval-DFS, s=2..{smax} ==')
    ok3 = True
    for s in range(2, smax + 1):
        tot = 0
        for w in range(1, s):
            h = s - w
            tot += interval_rows(w, h)
        # king_semiperim_38.txt: a(s) for s=2..39
        ref = a38[s - 2]
        match = (tot == ref)
        ok3 &= match
        print(f'  a({s}) brute={tot} banked={ref} {"OK" if match else "MISMATCH"}')
    print('check 3:', 'ALL OK' if ok3 else 'FAILED')

if __name__ == '__main__':
    main()
