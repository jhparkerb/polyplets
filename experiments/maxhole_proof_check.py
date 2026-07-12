#!/usr/bin/env python3
"""Numerical support for the max-hole theorem  M(n) = round((n-2)^2/8).

M(n) = max total enclosed empty area over n-cell king-polyplets (4-connected
background). Confirmed exactly by g2 --maxhole for n<=17 (results/maxhole.txt).

This checks the proof strategy (results/maxhole-proof.md):
  - CONSTRUCTION (lower bound): the diamond ring |x|+|y|=r has n=4r cells and
    encloses 2r^2-2r+1 = round((n-2)^2/8) cells -> M(4r) achieved exactly.
  - UPPER BOUND: reduce to a single hole (multi-hole is less efficient), then for a
    single 4-connected hole with diagonal ranges ha=range(x+y), hm=range(x-y):
      (I')  A <= ceil(ha*hm/2)          [hole fits its diagonal box, parity sublattice]
      (II') n >= ha + hm + 2            [sealing an ha x hm hole costs >= ha+hm+2 cells]
    Maximizing ceil(ha*hm/2) over integers ha+hm<=n-2 gives ceil(floor((n-2)^2/4)/2)
    = round((n-2)^2/8) = M(n).
Both lemmas are verified here on thousands of random king-polyplets; (II') is the
open crux (see the doc). Run: python3 -m experiments.maxhole_proof_check
"""
from collections import deque
import random, math

M_KNOWN = {4:1,5:1,6:2,7:3,8:5,9:6,10:8,11:10,12:13,13:15,14:18,15:21,16:25,17:28}


def M(n): return math.floor((n - 2) ** 2 / 8 + 0.5)


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


def hole_components(cells):
    cells = set(cells); xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1
    seen = {(x0, y0)}; dq = deque([(x0, y0)])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and p not in cells and p not in seen:
                seen.add(p); dq.append(p)
    es = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
          if (x, y) not in cells and (x, y) not in seen}
    comps = []
    while es:
        s = next(iter(es)); comp = {s}; es.discard(s); dq = deque([s])
        while dq:
            x, y = dq.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (x + dx, y + dy)
                if p in es:
                    es.discard(p); comp.add(p); dq.append(p)
        comps.append(comp)
    return comps


def rng(v): return max(v) - min(v) + 1


def diamond(r):
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1) if abs(x) + abs(y) == r}


def main():
    print("construction: diamond ring |x|+|y|=r")
    for r in range(1, 7):
        c = diamond(r); n = len(c)
        comp = hole_components(c); A = sum(len(h) for h in comp)
        print(f"  r={r}: n={n}  A={A}  round((n-2)^2/8)={M(n)}  {'OK' if A == M(n) else 'NO'}")

    random.seed(11)
    formula_bad = single_bad = single = total = 0
    for _ in range(6000):
        c = set(diamond(random.randint(1, 4)))
        for _ in range(random.randint(0, 12)):
            cell = random.choice(list(c))
            d = random.choice([(1, 0), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 0), (0, -1), (-1, 1)])
            c.add((cell[0] + d[0], cell[1] + d[1]))
        if random.random() < 0.4:
            off = (random.randint(-7, 7), random.randint(-7, 7))
            c |= {(x + off[0], y + off[1]) for x, y in diamond(random.randint(1, 3))}
            c |= {(i, 5) for i in range(min(0, off[0]), max(0, off[0]) + 1)}
        if not king_conn(c):
            continue
        comps = hole_components(c)
        if not comps:
            continue
        total += 1; n = len(c); A = sum(len(h) for h in comps)
        if A > M(n):
            formula_bad += 1
        if len(comps) == 1:
            single += 1; H = comps[0]
            ha = rng([x + y for x, y in H]); hm = rng([x - y for x, y in H])
            if len(H) > math.ceil(ha * hm / 2) or n < ha + hm + 2:
                single_bad += 1
    print(f"\nrandom test: {total} polyplets-with-holes ({single} single-hole)")
    print(f"  total area > M(n)                : {formula_bad} violations")
    print(f"  single-hole (I')&(II') lemmas    : {single_bad} violations")


if __name__ == "__main__":
    main()
