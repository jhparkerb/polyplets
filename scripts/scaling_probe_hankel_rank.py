#!/usr/bin/env python3
"""Scaling probe S3 (docs/scaling-exploration-brief.md, lane C, 2026-08-11).

Exact bond dimension of the height-H king-animal transfer operator: by the
Carlyle-Paz / Fliess theorem, the minimal dimension of ANY weighted-automaton
(= exact MPS/MPO bond dimension, = minimal linear TM) realization of the
counting function equals the rank of its Hankel matrix. If that rank grows
strictly slower than the partition-frontier state count (1, 3, 8, 20, 50,
126, 322, ...; ~2.65x/height), an exact compressed representation exists and
the brief's tensor-network direction is live; if it matches, the direction
is dead with a number.

f(w), for w a word of nonzero column masks: x^{#cells} if the configuration
is king-connected (one component), else 0 -- evaluated by FLOOD FILL on the
explicit grid (no partition DP anywhere), at random x in F_p. Hankel entries
f(uv) over prefixes u / suffixes v sampled up to length L; rank via Gaussian
elimination mod p. Rank is reported at two prefix lengths to show
saturation, and at 3 random x specializations (max taken; specialization
only ever underestimates the rank over Q(x)).

Usage: python3 scripts/scaling_probe_hankel_rank.py Hmax
"""
import sys, random
import numpy as np

P = 1_000_003
random.seed(11)


def connected_cells(word, H):
    cells = set()
    for j, m in enumerate(word):
        for i in range(H):
            if m >> i & 1:
                cells.add((i, j))
    if not cells:
        return 0, True
    seen = set()
    stack = [next(iter(cells))]
    seen.add(stack[0])
    while stack:
        i, j = stack.pop()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                nb = (i + di, j + dj)
                if nb in cells and nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
    return len(cells), len(seen) == len(cells)


def words(H, L, cap):
    letters = list(range(1, 1 << H))
    out = [()]
    layer = [()]
    for _ in range(L):
        layer = [w + (a,) for w in layer for a in letters]
        if len(layer) > cap:
            layer = random.sample(layer, cap)
        out += layer
    if len(out) > cap:
        out = out[:1 + (1 << H) - 1] + random.sample(out[1 + (1 << H) - 1:],
                                                     cap - (1 << H))
    return out


def rank_mod_p(M, p):
    M = M % p
    r = 0
    rows, cols = M.shape
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if M[i, c]:
                piv = i
                break
        if piv is None:
            continue
        M[[r, piv]] = M[[piv, r]]
        inv = pow(int(M[r, c]), p - 2, p)
        M[r] = (M[r] * inv) % p
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] = (M[i] - M[i, c] * M[r]) % p
        r += 1
        if r == rows:
            break
    return r


def hankel_rank(H, L, cap=400, nx=3):
    W = words(H, L, cap)
    best = 0
    for _ in range(nx):
        x = random.randrange(2, P)
        xp = [pow(x, k, P) for k in range(0, 4 * H * L + 4)]
        M = np.zeros((len(W), len(W)), dtype=np.int64)
        for a, u in enumerate(W):
            for b, v in enumerate(W):
                n, conn = connected_cells(u + v, H)
                if n and conn:
                    M[a, b] = xp[n]
        best = max(best, rank_mod_p(M, P))
    return best, len(W)


STATES = {1: 1, 2: 3, 3: 8, 4: 20, 5: 50, 6: 126, 7: 322}

if __name__ == '__main__':
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    for H in range(2, Hmax + 1):
        r2, n2 = hankel_rank(H, 2)
        r3, n3 = hankel_rank(H, 3)
        sat = 'saturated' if r3 == r2 else 'NOT saturated (true rank higher)'
        print(f'H={H}: rank>={max(r2, r3)} (len<=2: {r2} on {n2} words; '
              f'len<=3: {r3} on {n3} words; {sat}) '
              f'vs partition states {STATES.get(H)}', flush=True)
