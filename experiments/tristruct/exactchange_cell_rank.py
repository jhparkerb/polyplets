#!/usr/bin/env python3
"""Exact Change probe 2: char-2 rank of the CELL-level functional.

The column-level minimal automaton (rank A034299(H-1), probe 1) needs one
r x r transition matrix per column mask -- 2^H - 1 matrices, useless at
H = 21.  An algorithm needs the strip functional to stay low-rank when read
ONE CELL AT A TIME (alphabet {0,1}, H bits per column, LSB = row 0): then the
compressed DP is two GF(2) matrices applied 21 x 40 times.  This probe
measures that rank.

Presentation: product automaton (column state s, row j, prefix mask m).  The
Hankel rank is a property of the functional, not the presentation, so no
minimization is needed -- observability closure over the product does it.
Empty columns are dead (masks are nonzero in the column automaton), matching
the column-level convention.

Fail-closed: the column-level rank is recomputed from this cell-level closure
by restricting to whole-column words -- it must reproduce the banked A034299
values (asserted upstream in probe 1; here the automaton is the same object,
so the anchor is the state census, asserted against Motzkin(H+1)-1).
"""
import sys
import time

import numpy as np

from r3_inv_rank_probe import build_automaton, motzkin


def build_cell_automaton(H):
    order, delta, accept, masks = build_automaton(H)
    n = len(order)
    assert n == motzkin(H + 1) - 1, f"H={H}: column census {n} != Motzkin"
    midx = {m: i for i, m in enumerate(masks)}
    # cell states: (s, j, m) with 0 <= j < H, m < 2^j; entry point j=0, m=0
    states = {}
    order2 = []

    def sid(t):
        if t not in states:
            states[t] = len(states)
            order2.append(t)
        return states[t]

    todo = [(s, 0, 0) for s in range(n)]
    for t in todo:
        sid(t)
    todo = list(order2)
    trans = {}
    while todo:
        t = todo.pop()
        s, j, m = t
        for b in (0, 1):
            mm = m | (b << j)
            if j == H - 1:
                if mm == 0:
                    continue  # empty column: dead
                s2 = delta[s, midx[mm]]
                if s2 < 0:
                    continue
                u = (int(s2), 0, 0)
            else:
                u = (s, j + 1, mm)
            known = u in states
            trans[(states[t], b)] = sid(u)
            if not known:
                todo.append(u)
    N = len(order2)
    d2 = np.full((N, 2), -1, dtype=np.int64)
    for (si, b), ti in trans.items():
        d2[si, b] = ti
    acc2 = np.zeros(N, dtype=bool)
    for t, i in states.items():
        s, j, m = t
        if j == 0 and m == 0 and accept[s]:
            acc2[i] = True
    return order2, d2, acc2


def obs_rank_gf2(delta, accept):
    """Returns (basis dict pivot->row-int, list of basis rows as bool arrays)."""
    n, na = delta.shape
    basis = {}

    def reduce_add(row):
        while row:
            p = row.bit_length() - 1
            if p in basis:
                row ^= basis[p]
            else:
                basis[p] = row
                return True
        return False

    def vec_to_int(v):
        return int.from_bytes(np.packbits(v[::-1]).tobytes(), 'big')

    keep = []
    frontier = [accept.copy()]
    if reduce_add(vec_to_int(accept)):
        keep.append(accept.copy())
    while frontier:
        nxt = []
        for g in frontier:
            for mi in range(na):
                d = delta[:, mi]
                h = np.zeros(n, dtype=bool)
                ok = d >= 0
                h[ok] = g[d[ok]]
                if reduce_add(vec_to_int(h)):
                    nxt.append(h)
                    keep.append(h)
        frontier = nxt
    return basis, keep


def transition_density(delta, basis, keep):
    """Express g o delta_b in the pivot basis for every closure generator g;
    report row-weight stats of the two compressed transition matrices."""
    n, na = delta.shape

    def vec_to_int(v):
        return int.from_bytes(np.packbits(v[::-1]).tobytes(), 'big')

    weights = {0: [], 1: []}
    for b in (0, 1):
        d = delta[:, b]
        ok = d >= 0
        for g in keep:
            h = np.zeros(n, dtype=bool)
            h[ok] = g[d[ok]]
            row = vec_to_int(h)
            w = 0
            while row:
                p = row.bit_length() - 1
                assert p in basis, "closure not invariant -- broken"
                row ^= basis[p]
                w += 1
            weights[b].append(w)
    return weights


def a034299(H):
    return (2 ** (H + 4) - (-1) ** H * (6 * H + 7) - 9) // 36


def main():
    hs = [int(a) for a in sys.argv[1:]] or list(range(4, 8))
    print("H  cell_states  cell_rank_GF2  col_rank(A034299)  ratio")
    for H in hs:
        t0 = time.time()
        order2, d2, acc2 = build_cell_automaton(H)
        basis, keep = obs_rank_gf2(d2, acc2)
        r = len(basis)
        cr = a034299(H)
        w = transition_density(d2, basis, keep)
        w0, w1 = w[0], w[1]
        print(f"{H}  {len(order2)}  {r}  {cr}  {r/cr:.3f}   "
              f"A0 row-weight avg={sum(w0)/len(w0):.1f} max={max(w0)}  "
              f"A1 avg={sum(w1)/len(w1):.1f} max={max(w1)}  "
              f"dense would be ~{r//2}   ({time.time()-t0:.1f}s)", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
