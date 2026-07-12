#!/usr/bin/env python3
"""The peeling route to the master inequality (multi-hole M(n) reduction).

Chain (results/maxhole-proof.md):
  PEELING LEMMA:  hole-free F', interior I with |I|>=2  =>  |shell4(I)| <= |S|-4
  + recursion f(m) <= (m-4) + f(m-4) with bases f(4)=1,f(5)=1,f(6)=2,f(7)=3
  => f(m) = round((m-2)^2/8) EXACTLY  =>  master inequality  =>  multi-hole M(n).

Decomposition of the peeling lemma (both verified here, proofs open):
  (A-int) for each king-component J of I (|J|>=2):
          |shell4(J)| <= r_u(J)+r_v(J)-2      [FALSE for general king sets --
          counterexample found -- TRUE and almost always tight for interiors]
  (Sigma) sum_j max(r_u,j+r_v,j-2, 1) <= |S|-4.
Run: python3 -m experiments.maxhole_peeling_check
"""
import math
import random
from collections import deque


def shell4(A):
    A = set(A)
    return {p for p in A if any((p[0] + dx, p[1] + dy) not in A
                                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


def king_comps(A):
    A = set(A); out = []
    while A:
        s = next(iter(A)); comp = {s}; A.discard(s); dq = deque([s])
        while dq:
            x, y = dq.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = (x + dx, y + dy)
                    if (dx or dy) and p in A:
                        A.discard(p); comp.add(p); dq.append(p)
        out.append(comp)
    return out


def rng_uv(A):
    us = [x + y for x, y in A]; vs = [x - y for x, y in A]
    return max(us) - min(us) + 1, max(vs) - min(vs) + 1


def bg_fill(cells):
    cells = set(cells); xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1
    seen = {(x0, y0)}; dq = deque([(x0, y0)])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and p not in cells and p not in seen:
                seen.add(p); dq.append(p)
    return cells | {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
                    if (x, y) not in cells and (x, y) not in seen}


def diamond(r):
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1) if abs(x) + abs(y) == r}


def M(m):
    return math.floor((m - 2) ** 2 / 8 + 0.5)


def main():
    # recursion arithmetic: f(m) = (m-4)+f(m-4), f(4)=1, f(5)=1, f(6)=2, f(7)=3
    f = {4: 1, 5: 1, 6: 2, 7: 3}
    ok = True
    for m in range(8, 200):
        f[m] = (m - 4) + f[m - 4]
        ok &= (f[m] == M(m))
    print("recursion reproduces round((m-2)^2/8) exactly, m<=199:", ok and all(f[m] == M(m) for m in (4, 5, 6, 7)))

    random.seed(11)
    peel_bad = a_bad = s_bad = 0
    peel_n = a_n = s_n = 0
    a_tight = s_tight = 0
    for trial in range(9000):
        c = set(diamond(random.randint(1, 4)))
        for _ in range(random.randint(0, 18)):
            cell = random.choice(list(c))
            d = random.choice([(1, 0), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 0), (0, -1), (-1, 1)])
            c.add((cell[0] + d[0], cell[1] + d[1]))
        if len(king_comps(set(c))) != 1:
            continue
        Fp = bg_fill(c)
        S = shell4(Fp); I = set(Fp) - S
        if len(I) < 2:
            continue
        # peeling lemma
        peel_n += 1
        if len(shell4(I)) > len(S) - 4:
            peel_bad += 1
        # decomposition
        tot = 0
        for J in king_comps(I):
            ru, rv = rng_uv(J)
            if len(J) >= 2:
                a_n += 1
                sj = len(shell4(J))
                if sj > ru + rv - 2:
                    a_bad += 1
                if sj == ru + rv - 2:
                    a_tight += 1
            tot += max(ru + rv - 2, 1)
        s_n += 1
        if tot > len(S) - 4:
            s_bad += 1
        if tot == len(S) - 4:
            s_tight += 1
    print(f"peeling lemma: {peel_n} tested, {peel_bad} violations")
    print(f"(A-int):       {a_n} components, {a_bad} violations, {a_tight} tight")
    print(f"(Sigma):       {s_n} tested, {s_bad} violations, {s_tight} tight")


if __name__ == "__main__":
    main()
