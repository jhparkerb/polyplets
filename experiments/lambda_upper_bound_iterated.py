#!/usr/bin/env python3
"""ITERATED (depth-d) rigorous UPPER bound on the king-lattice (polyplet, A006770) growth
constant lambda, generalizing experiments/lambda_upper_bound.py (which is the depth-1 case).

Eden / Klarner-Rivest spanning-tree encoding. Build the animal's BFS tree from a root; every
non-root cell is DISCOVERED by its BFS-parent. A cell C can be the discoverer of a neighbor q
only if no PROPER ANCESTOR of C is adjacent-or-equal to q -- an ancestor has strictly smaller
BFS depth, so q's parent has depth <= depth(ancestor)+1 <= depth(C) < depth(C)+1, hence q is not
C's child. Sound for any depth d: we only ever DROP child-slots that provably cannot occur, so the
encoding still injects every animal and 1/x* (x* = the encoding-GF branch point) is a valid upper
bound on lambda. Increasing d drops more impossible slots => same validity, monotonically tighter.

Cell TYPE at depth d = the last d discoverer-directions (d_0 = own, d_1 = parent's, ...). With C
at the origin and d_k = direction from a cell to its child, ancestor j sits at -(d_0+..+d_j); a
candidate child in direction e sits at +e and its slot is excluded iff Chebyshev(e + d_0+..+d_j)<=1
for some j (ancestor adjacent or coincident). GF system:
    T[s] = x * prod_{e allowed by s} (1 + T[ child_state(s,e) ]),   child_state = (e, d_0,.., d_{d-2}),
and lambda <= 1/x*, solved by bisection on the largest x for which the monotone iteration from 0
stays bounded. Validation anchors: square depth-1 = Eden 27/4 = 6.75 exactly; king depth-1 =
10.3538 (== lambda_upper_bound.py). Depth d>=2 is the rigorous improvement.
"""
from itertools import product

import numpy as np

KING = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
SQUARE = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def king_adj(vx, vy):      # L-infinity: the 8 king neighbours + coincidence
    return max(abs(vx), abs(vy)) <= 1


def rook_adj(vx, vy):      # L1: the 4 rook neighbours + coincidence
    return abs(vx) + abs(vy) <= 1


def build_kids(dirs, depth, adj):
    """kids_mat[i] = padded child-state indices for state i (pad value = sentinel n)."""
    states = list(product(range(len(dirs)), repeat=depth))
    index = {s: i for i, s in enumerate(states)}
    n = len(states)
    kid_lists = []
    for s in states:
        S = []  # prefix sums S_j = d_0+..+d_j in lattice coords
        ax = ay = 0
        for di in s:
            ax += dirs[di][0]; ay += dirs[di][1]
            S.append((ax, ay))
        kids = []
        for ei, e in enumerate(dirs):
            if any(adj(e[0] + sx, e[1] + sy) for (sx, sy) in S):
                continue  # an ancestor is adjacent-or-equal to this slot -> impossible child
            kids.append(index[(ei,) + s[:depth - 1]])
        kid_lists.append(kids)
    maxk = max(len(k) for k in kid_lists)
    kids_mat = np.full((n, maxk), n, dtype=np.int64)  # sentinel index n -> factor 1.0
    for i, k in enumerate(kid_lists):
        kids_mat[i, :len(k)] = k
    return kids_mat, n


def bound(dirs, depth, adj, iters=8000, bisect=64):
    kids_mat, n = build_kids(dirs, depth, adj)
    onep = np.ones(n + 1)  # [0..n-1]=1+T, index n = sentinel = 1.0 (pad)

    def bounded(x):
        T = np.zeros(n)
        for _ in range(iters):
            onep[:n] = 1.0 + T
            newT = x * onep[kids_mat].prod(axis=1)
            if not np.isfinite(newT).all() or newT.max() > 1e9:
                return False
            if np.abs(newT - T).max() < 1e-13:
                return True  # converged to finite fixed point
            T = newT
        return True  # stayed bounded

    lo, hi = 0.0, 0.5
    for _ in range(bisect):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if bounded(m) else (lo, m)
    return 1.0 / ((lo + hi) / 2)


if __name__ == "__main__":
    print("depth   square (anchor)    king/polyplet (target)   #king-types")
    for d in range(1, 8):
        sq = bound(SQUARE, d, rook_adj)
        kg = bound(KING, d, king_adj) if 8 ** d <= 40000 else None
        ks = 8 ** d
        note = "   <- 6.75 / 10.354" if d == 1 else ""
        kgs = f"{kg:10.4f}" if kg is not None else "   (skip)"
        print(f"  {d}     {sq:10.4f}        {kgs}            {ks}{note}")
    print()
    print("known: square lambda ~ 4.0626 (true), Klarner-Rivest upper bound 4.649;")
    print("       king/polyplet lambda ~ 7.13 (estimate), rigorous lower bound 6.540.")
