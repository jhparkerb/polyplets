#!/usr/bin/env python3
"""Idea 2 of results/closed-doors.md, step 0: pin the matching-pair
CONVENTION by brute force before any of the percolation machinery is built.

The plan says the convention decides whether the whole idea works -- "Get this
wrong and nothing will check out" -- and states it as: in the matching identity
each cluster's boundary is measured in the OTHER lattice, i.e. a polyomino's
perimeter w.r.t. the king neighborhood and a polyplet's w.r.t. the rook
neighborhood.

This probe tests that claim instead of assuming it, over EVERY subset of a
small box, by checking the two Euler identities the matching pair is built on:

    C_4(S) - H_8(S) = V - E_4 + Q          (4-connected foreground)
    C_8(S) - H_4(S) = V - E_8 + T - Q      (8-connected foreground)

where V = |S|, E_4 / E_8 = adjacent pairs in S under rook / king adjacency,
Q = 2x2 blocks wholly in S, T = king-adjacency triangles (3-cliques) in S,
C_a = a-connected components of S, and H_a = BOUNDED a-connected components of
the complement (the holes).

If those hold, then the pairing is (foreground a-connectivity <-> background
(matching-a)-connectivity), and the perimeter that goes with an a-cluster in a
cluster generating function is the a-perimeter -- the SAME lattice, because a
maximal a-connected occupied set is exactly one whose a-neighbors are all
vacant. That is the opposite of what the plan says.

Usage: python3 experiments/matching_pair_euler.py [BOX]
"""

import itertools
import sys
from collections import deque

ROOK = [(1, 0), (-1, 0), (0, 1), (0, -1)]
KING = ROOK + [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def comps(cells, nbrs, universe):
    """Number of connected components of `cells` under `nbrs`, within
    `universe`."""
    todo, n = set(cells), 0
    while todo:
        n += 1
        q = deque([todo.pop()])
        while q:
            (x, y) = q.popleft()
            for (dx, dy) in nbrs:
                c = (x + dx, y + dy)
                if c in todo:
                    todo.remove(c)
                    q.append(c)
    return n


def holes(S, nbrs, box):
    """Bounded components of the complement of S, under `nbrs`.

    The complement is taken inside the box padded by one ring; every component
    touching the pad is the unbounded one."""
    w, h = box
    pad = [(x, y) for x in range(-1, w + 1) for y in range(-1, h + 1)
           if (x, y) not in S]
    padset = set(pad)
    seen, n = set(), 0
    for start in pad:
        if start in seen:
            continue
        q, comp = deque([start]), set()
        seen.add(start)
        while q:
            (x, y) = q.popleft()
            comp.add((x, y))
            for (dx, dy) in nbrs:
                c = (x + dx, y + dy)
                if c in padset and c not in seen:
                    seen.add(c)
                    q.append(c)
        touches = any(x in (-1, w) or y in (-1, h) for (x, y) in comp)
        if not touches:
            n += 1
    return n


def stats(S, box):
    V = len(S)
    E4 = sum(1 for (x, y) in S for (dx, dy) in [(1, 0), (0, 1)]
             if (x + dx, y + dy) in S)
    E8 = sum(1 for (x, y) in S
             for (dx, dy) in [(1, 0), (0, 1), (1, 1), (1, -1)]
             if (x + dx, y + dy) in S)
    Q = sum(1 for (x, y) in S
            if all(c in S for c in [(x + 1, y), (x, y + 1), (x + 1, y + 1)]))
    # king 3-cliques
    T = 0
    Sl = sorted(S)
    for i, a in enumerate(Sl):
        for b in Sl[i + 1:]:
            if max(abs(a[0] - b[0]), abs(a[1] - b[1])) != 1:
                continue
            for c in Sl:
                if c <= b:
                    continue
                if (max(abs(a[0] - c[0]), abs(a[1] - c[1])) == 1
                        and max(abs(b[0] - c[0]), abs(b[1] - c[1])) == 1):
                    T += 1
    return V, E4, E8, Q, T


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    box = (k, k)
    cells = [(x, y) for x in range(k) for y in range(k)]
    n_ok4 = n_ok8 = bad4 = bad8 = 0
    ex4 = ex8 = None

    for mask in range(1 << (k * k)):
        S = frozenset(c for i, c in enumerate(cells) if mask >> i & 1)
        if not S:
            continue
        V, E4, E8, Q, T = stats(S, box)
        C4 = comps(S, ROOK, S)
        C8 = comps(S, KING, S)
        H4 = holes(S, ROOK, box)
        H8 = holes(S, KING, box)

        if C4 - H8 == V - E4 + Q:
            n_ok4 += 1
        else:
            bad4 += 1
            ex4 = ex4 or (S, C4, H8, V - E4 + Q)
        if C8 - H4 == V - E8 + T - Q:
            n_ok8 += 1
        else:
            bad8 += 1
            ex8 = ex8 or (S, C8, H4, V - E8 + T - Q)

    tot = n_ok4 + bad4
    print(f"box {k}x{k}: {tot} non-empty subsets\n")
    print(f"  C_4(S) - H_8(S) == V - E_4 + Q       : "
          f"{n_ok4}/{tot} {'ALL HOLD' if not bad4 else f'{bad4} FAIL'}")
    print(f"  C_8(S) - H_4(S) == V - E_8 + T - Q   : "
          f"{n_ok8}/{tot} {'ALL HOLD' if not bad8 else f'{bad8} FAIL'}")
    for label, ex in (("4-conn", ex4), ("8-conn", ex8)):
        if ex:
            S, c, hh, rhs = ex
            print(f"\n  first {label} failure: comps={c} holes={hh} rhs={rhs}")
            for y in range(k - 1, -1, -1):
                print("    " + "".join("#" if (x, y) in S else "."
                                       for x in range(k)))

    # The cross pairings, which the plan's stated convention implies.
    print("\n  cross-pairings (what the plan's convention would need):")
    n1 = n2 = 0
    for mask in range(1 << (k * k)):
        S = frozenset(c for i, c in enumerate(cells) if mask >> i & 1)
        if not S:
            continue
        V, E4, E8, Q, T = stats(S, box)
        if comps(S, ROOK, S) - holes(S, ROOK, box) == V - E4 + Q:
            n1 += 1
        if comps(S, KING, S) - holes(S, KING, box) == V - E8 + T - Q:
            n2 += 1
    print(f"    C_4 - H_4 == V - E_4 + Q      : {n1}/{tot}")
    print(f"    C_8 - H_8 == V - E_8 + T - Q  : {n2}/{tot}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
