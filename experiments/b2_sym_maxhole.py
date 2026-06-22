#!/usr/bin/env python3
# B2: maxhole split by symmetry. M(n) (the diamond optimum) is D4-symmetric. Question: does
# the max hole area among ASYMMETRIC (trivial-stabilizer) n-cell polyplets fall short of
# M(n)? I.e. is there a "symmetry premium" for enclosing area? Brute force, n<=9.
from collections import deque

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
ROOK = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def _tup(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return tuple(sorted((x - mx, y - my) for x, y in cells))


def orbit_size(cells):                       # D4 orbit size; 8 = asymmetric, <8 = has symmetry
    imgs = set(); c = set(cells)
    for _ in range(4):
        for im in (c, {(-x, y) for x, y in c}):
            imgs.add(_tup(im))
        c = {(y, -x) for x, y in c}
    return len(imgs)


def hole_area(cells):
    cells = set(cells)
    xs = [x for x, y in cells]; ys = [y for x, y in cells]
    x0, x1 = min(xs) - 1, max(xs) + 1
    y0, y1 = min(ys) - 1, max(ys) + 1
    ext = {(x0, y0)}; dq = deque(ext)
    while dq:
        x, y = dq.popleft()
        for dx, dy in ROOK:
            nb = (x + dx, y + dy)
            if x0 <= nb[0] <= x1 and y0 <= nb[1] <= y1 and nb not in cells and nb not in ext:
                ext.add(nb); dq.append(nb)
    return sum(1 for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
              if (x, y) not in cells and (x, y) not in ext)


import sys
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 9
level = {1: {canon({(0, 0)})}}
for s in range(2, NMAX + 1):
    nxt = set()
    for sh in level[s - 1]:
        for (x, y) in sh:
            for dx, dy in KING:
                c = (x + dx, y + dy)
                if c not in sh:
                    nxt.add(canon(sh | {c}))
    level[s] = nxt

def M(n):                                    # proven diamond optimum (T5)
    return ((n - 2) ** 2 // 4 + 1) // 2 if n >= 2 else 0


print(" n   M(n)   M_asym   M_sym   M(n-1)   M_asym==M(n-1)?")
for s in range(1, NMAX + 1):
    mall = msym = masym = 0
    for sh in level[s]:
        ha = hole_area(sh)
        if ha > mall:
            mall = ha
        if orbit_size(sh) == 8:
            masym = max(masym, ha)
        else:
            msym = max(msym, ha)
    print(f" {s}   {mall:4d}   {masym:5d}   {msym:5d}   {M(s-1):5d}      "
          f"{'YES' if masym == M(s - 1) else 'no'}")
