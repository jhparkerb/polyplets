#!/usr/bin/env python3
# How many fixed n-cell polyplets actually attain the maximum hole area M(n)? The
# "maxhole-optimal multiplicity". Brute force, n<=9. (For n<=3, M=0 and every shape
# trivially attains it; the interesting range is n>=4.)
from collections import deque

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
ROOK = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def hole_area(cells):
    s = set(cells)
    xs = [x for x, y in cells]; ys = [y for x, y in cells]
    x0, x1 = min(xs) - 1, max(xs) + 1
    y0, y1 = min(ys) - 1, max(ys) + 1
    ext = {(x0, y0)}; dq = deque(ext)
    while dq:
        x, y = dq.popleft()
        for dx, dy in ROOK:
            nb = (x + dx, y + dy)
            if x0 <= nb[0] <= x1 and y0 <= nb[1] <= y1 and nb not in s and nb not in ext:
                ext.add(nb); dq.append(nb)
    return sum(1 for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
              if (x, y) not in s and (x, y) not in ext)


def M(n):
    return ((n - 2) ** 2 // 4 + 1) // 2 if n >= 2 else 0


NMAX = 9
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

print(" n   M(n)   #optimal (fixed polyplets attaining M(n))")
mult = []
for s in range(4, NMAX + 1):
    m = M(s)
    cnt = sum(1 for sh in level[s] if hole_area(sh) == m)
    mult.append(cnt)
    print(f" {s}   {m:4d}   {cnt}")
print("multiplicity (n=4..9):", ", ".join(map(str, mult)))
