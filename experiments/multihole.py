#!/usr/bin/env python3
# Multi-hole maxhole: M_k(n) = max total enclosed-empty area over fixed n-cell polyplets
# with EXACTLY k holes (M_1 = M(n), the diamond result T3/T5). Generalizes the (u,v)
# isoperimetric framework. Brute-force: enumerate fixed polyplets (verified vs A006770),
# compute (#holes, total hole area) per shape, take the max area per (n,k).
from collections import deque

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
ROOK = [(1, 0), (-1, 0), (0, 1), (0, -1)]
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982]


def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def holes(cells):
    cells = set(cells)
    xs = [x for x, y in cells]; ys = [y for x, y in cells]
    x0, x1 = min(xs) - 1, max(xs) + 1
    y0, y1 = min(ys) - 1, max(ys) + 1
    ext = {(x0, y0)}; dq = deque(ext)        # flood the exterior (4-conn empty) from a corner
    while dq:
        x, y = dq.popleft()
        for dx, dy in ROOK:
            nb = (x + dx, y + dy)
            if x0 <= nb[0] <= x1 and y0 <= nb[1] <= y1 and nb not in cells and nb not in ext:
                ext.add(nb); dq.append(nb)
    hole = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
            if (x, y) not in cells and (x, y) not in ext}
    seen = set(); ncomp = 0
    for c in hole:
        if c in seen:
            continue
        ncomp += 1; dq = deque([c]); seen.add(c)
        while dq:
            x, y = dq.popleft()
            for dx, dy in ROOK:
                nb = (x + dx, y + dy)
                if nb in hole and nb not in seen:
                    seen.add(nb); dq.append(nb)
    return ncomp, len(hole)


NMAX = 9
level = {1: {canon({(0, 0)})}}
for s in range(2, NMAX + 1):
    nxt = set()
    for shape in level[s - 1]:
        for (x, y) in shape:
            for dx, dy in KING:
                c = (x + dx, y + dy)
                if c not in shape:
                    nxt.add(canon(shape | {c}))
    level[s] = nxt

import math


def Mformula(n):
    return math.ceil(((n - 2) ** 2 // 4) / 2)


print(" n   M_k(n) per k          M_total  M(n)  M_total==M(n)?")
for s in range(1, NMAX + 1):
    best = {}
    for sh in level[s]:
        k, area = holes(sh)
        if area and k:
            best[k] = max(best.get(k, 0), area)
    mtot = max(best.values()) if best else 0
    mf = Mformula(s)
    per = "  ".join(f"M_{k}={best[k]}" for k in sorted(best)) or "(no holes)"
    print(f" {s}  {per:32s} {mtot:4d}  {mf:4d}   {'YES' if mtot == mf else 'NO'}")
print()
print("=> max TOTAL enclosed area over ALL n-cell polyplets (any # holes) = M(n):")
print("   the single diamond beats every multi-hole configuration.")
