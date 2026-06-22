#!/usr/bin/env python3
# Max hole area under the 8-CONNECTED background convention, M_8(n), vs the 4-bg diamond
# result M(n) (T3/T5). An 8-bg hole is an 8-connected empty region, so the enclosing wall
# must be ROOK-connected (no diagonal gaps) -- a different geometry from the 4-bg diamond.
# First 8-bg hole is at n=8 (the 3x3 ring). Brute force, n<=10.
from collections import deque

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]


def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def hole8_area(cells):
    s = set(cells)
    xs = [x for x, y in cells]; ys = [y for x, y in cells]
    x0, x1 = min(xs) - 1, max(xs) + 1
    y0, y1 = min(ys) - 1, max(ys) + 1
    ext = {(x0, y0)}; dq = deque(ext)
    while dq:                                  # 8-connected background flood from a corner
        x, y = dq.popleft()
        for dx, dy in KING:
            nb = (x + dx, y + dy)
            if x0 <= nb[0] <= x1 and y0 <= nb[1] <= y1 and nb not in s and nb not in ext:
                ext.add(nb); dq.append(nb)
    return sum(1 for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
              if (x, y) not in s and (x, y) not in ext)


def M4(n):                                     # the proven 4-bg diamond optimum
    return ((n - 2) ** 2 // 4 + 1) // 2 if n >= 2 else 0


NMAX = 10
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

print(" n   M_8(n)   M_4(n) [diamond]")
m8 = []
for s in range(1, NMAX + 1):
    v = max((hole8_area(sh) for sh in level[s]), default=0)
    m8.append(v)
    print(f" {s}    {v:4d}      {M4(s):4d}")
print("M_8(n):", ", ".join(map(str, m8)))
