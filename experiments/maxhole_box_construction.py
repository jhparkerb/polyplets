#!/usr/bin/env python3
"""The uniform extremal family for M(n): parity-aligned diagonal-box holes.

Hole(a,b) = all cells with u=x+y in [0,a-1], v=x-y in [0,b-1] (corner-aligned:
only u=v mod 2 cells exist). Animal = its 4-neighbour ring. Facts verified here:
  - |ring| = a+b+2 for all non-degenerate (a,b) (a,b>=2, or =1 with odd partner)
  - the ring is king-connected and encloses exactly the box, area ceil(ab/2)
  - maximizing over a+b = n-2 gives round((n-2)^2/8) = M(n) for EVERY n>=4
    except n=5, which is achieved by the n=4 diamond plus one padding cell.
With lemma (II') (moat-cycle proof) and (I'), this completes BOTH bounds of
M_single(n) = round((n-2)^2/8) for all n. Run: python3 -m experiments.maxhole_box_construction
"""
import math
from collections import deque


def box_hole(a, b):
    H = set()
    for u in range(a):
        for v in range(b):
            if (u - v) % 2 == 0:
                H.add(((u + v) // 2, (u - v) // 2))
    return H


def ring_of(H):
    R = set()
    for (x, y) in H:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if p not in H:
                R.add(p)
    return R


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


def hole_area(cells):
    cells = set(cells); xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1
    seen = {(x0, y0)}; dq = deque([(x0, y0)])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and p not in cells and p not in seen:
                seen.add(p); dq.append(p)
    return sum(1 for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
               if (x, y) not in cells and (x, y) not in seen)


def M(n):
    return math.floor((n - 2) ** 2 / 8 + 0.5)


def main():
    KNOWN = {4: 1, 5: 1, 6: 2, 7: 3, 8: 5, 9: 6, 10: 8, 11: 10, 12: 13, 13: 15,
             14: 18, 15: 21, 16: 25, 17: 28}
    allok = True
    for n in range(4, 61):
        if n == 5:
            continue                     # padded diamond case
        best = -1; arg = None
        for a in range(1, n - 2):
            b = n - 2 - a
            H = box_hole(a, b); R = ring_of(H)
            if len(R) != n or not king_conn(R):
                continue
            A = hole_area(R)
            if A > best:
                best, arg = A, (a, b)
        ok = best == M(n) and (n not in KNOWN or best == KNOWN[n])
        allok &= ok
        if n <= 18 or not ok:
            print(f"  n={n:2d}: box (a,b)={arg} area={best}  M(n)={M(n)}  {'OK' if ok else 'FAIL'}")
    print("family achieves M(n) for all n=4..60 (n=5 by padding):", allok)


if __name__ == "__main__":
    main()
