#!/usr/bin/env python3
"""Master isoperimetric inequality for the multi-hole reduction of M(n).

Reduction (results/maxhole-proof.md): fill an animal's holes -> hole-free F' with
A <= interior4(F') and n >= |shell4(F')|. So the multi-hole bound follows from:
    interior4(F') <= round((|shell4(F')| - 2)^2 / 8)      [master inequality]
This script verifies it on random filled animals (0 violations expected; solid
diamonds tight) and re-demonstrates the counterexample to the RANGE-form core
(two lone interior cells in separate lobes), which killed the naive moat route.
Run: python3 -m experiments.maxhole_master_check
"""
import math
import random
from collections import deque


def background_split(cells):
    cells = set(cells); xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1
    seen = {(x0, y0)}; dq = deque([(x0, y0)])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and p not in cells and p not in seen:
                seen.add(p); dq.append(p)
    holes = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
             if (x, y) not in cells and (x, y) not in seen}
    return holes


def king_conn(cells):
    cells = set(cells); c0 = next(iter(cells)); seen = {c0}; dq = deque([c0])
    while dq:
        x, y = dq.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if (dx or dy) and p in cells and p not in seen:
                    seen.add(p); dq.append(p)
    return len(seen) == len(cells)


def diamond(r):
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1) if abs(x) + abs(y) == r}


def M(m):
    return math.floor((m - 2) ** 2 / 8 + 0.5)


def main():
    random.seed(7)
    tested = tight = 0; bad = []
    range_core_counterexample = None
    for trial in range(6000):
        c = set(diamond(random.randint(1, 4)))
        for _ in range(random.randint(0, 14)):
            cell = random.choice(list(c))
            d = random.choice([(1, 0), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 0), (0, -1), (-1, 1)])
            c.add((cell[0] + d[0], cell[1] + d[1]))
        if not king_conn(c):
            continue
        Fp = c | background_split(c)
        shell = {p for p in Fp if any((p[0] + dx, p[1] + dy) not in Fp
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        interior = Fp - shell
        tested += 1
        if len(interior) > M(len(shell)):
            bad.append(trial)
        if interior and len(interior) == M(len(shell)):
            tight += 1
        if interior and range_core_counterexample is None:
            us = [x + y for x, y in interior]; vs = [x - y for x, y in interior]
            if (max(us) - min(us) + 1) + (max(vs) - min(vs) + 1) > len(shell) - 2:
                range_core_counterexample = (trial, sorted(Fp))
    print(f"filled animals tested: {tested}   master violations: {len(bad)}   tight: {tight}")
    print("range-core counterexample found:", range_core_counterexample is not None,
          "(disconnected interiors break the naive moat route)")
    for r in range(2, 12):
        Fp = {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1) if abs(x) + abs(y) <= r}
        shell = {p for p in Fp if any((p[0] + dx, p[1] + dy) not in Fp
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        assert len(Fp) - len(shell) == M(len(shell))
    print("solid diamonds exactly tight, r=2..11: True")


if __name__ == "__main__":
    main()
