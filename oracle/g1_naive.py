#!/usr/bin/env python3
"""G1: the naive oracle.

Enumerates fixed lattice animals by brute force: grow every animal of size n
by every adjacent cell, normalize to a translation-canonical form, deduplicate
with a set. No cleverness whatsoever -- this file is the bottom of the chain
of oracles and is meant to be verifiable by inspection.

Lattices:
  square4  polyominoes   (A001168)   cells adjacent iff they share an edge
  square8  polyplets     (A006770)   edge OR corner contact (king moves)
  tri6     polyhexes     (A001207)   site animals on the triangular lattice,
                                     axial coordinates

Usage:  g1_naive.py LATTICE MAXN
Output: one "n count" line per size, b-file format.
"""

import sys

NEIGHBORS = {
    "square4": [(1, 0), (-1, 0), (0, 1), (0, -1)],
    "square8": [(1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1)],
    "tri6":    [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)],
}


def normalize(cells):
    """Translate so the minimum x and y are 0. Canonical for fixed animals."""
    mx = min(x for x, y in cells)
    my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def count_fixed(lattice, maxn):
    """Return {n: number of fixed animals with n cells} for 1 <= n <= maxn."""
    nbrs = NEIGHBORS[lattice]
    current = {frozenset([(0, 0)])}
    counts = {1: 1}
    for n in range(2, maxn + 1):
        grown = set()
        for animal in current:
            for (x, y) in animal:
                for (dx, dy) in nbrs:
                    cell = (x + dx, y + dy)
                    if cell not in animal:
                        grown.add(normalize(animal | {cell}))
        counts[n] = len(grown)
        current = grown
    return counts


def count_by_box(lattice, maxn):
    """Return {(n, w, h): count} where w, h are bounding-box dimensions.

    For tri6 the "box" is the axial-coordinate bounding parallelogram; the
    definition only has to be translation-invariant and shared with G2.
    Deliberately duplicates the growth loop of count_fixed: in the oracle,
    boring beats DRY.
    """
    nbrs = NEIGHBORS[lattice]
    current = {frozenset([(0, 0)])}
    boxes = {(1, 1, 1): 1}
    for n in range(2, maxn + 1):
        grown = set()
        for animal in current:
            for (x, y) in animal:
                for (dx, dy) in nbrs:
                    cell = (x + dx, y + dy)
                    if cell not in animal:
                        grown.add(normalize(animal | {cell}))
        for animal in grown:
            w = max(x for x, y in animal) + 1   # normalized: min is 0
            h = max(y for x, y in animal) + 1
            key = (n, w, h)
            boxes[key] = boxes.get(key, 0) + 1
        current = grown
    return boxes


# The eight elements of D4 acting on square-lattice cell coordinates.
# Order: e, r90, r180, r270, then mirrors h, v, d1 (y=x), d2 (y=-x).
# The first four are the rotation subgroup C4 (one-sided symmetry).
D4 = [
    lambda x, y: (x, y),
    lambda x, y: (-y, x),
    lambda x, y: (-x, -y),
    lambda x, y: (y, -x),
    lambda x, y: (x, -y),
    lambda x, y: (-x, y),
    lambda x, y: (y, x),
    lambda x, y: (-y, -x),
]


def canon_under(cells, t):
    """Apply transform t, translate to the origin, return a sorted tuple.

    A sorted tuple (unlike a frozenset) is orderable, so min() over the
    eight images gives a canonical representative of the free orbit.
    """
    pts = [t(x, y) for (x, y) in cells]
    mx = min(x for x, y in pts)
    my = min(y for x, y in pts)
    return tuple(sorted((x - mx, y - my) for x, y in pts))


def count_symmetry(lattice, maxn):
    """Brute-force free/one-sided/fixed counts and per-element fixed counts.

    Square lattices only (D4 symmetry); polyhexes have a different group.
    Returns {fixed, free, onesided, classfix[8]} as {n: count} dicts.
    Deliberately re-grows from scratch -- oracle clarity over reuse.
    Validates Burnside internally: sum(classfix)/8 == free.
    """
    assert lattice in ("square4", "square8")
    nbrs = NEIGHBORS[lattice]
    fixed, free, onesided = {}, {}, {}
    classfix = {i: {} for i in range(8)}

    def analyze(animals, n):
        free_orbits, onesided_orbits = set(), set()
        cfix = [0] * 8
        for a in animals:
            self_form = canon_under(a, D4[0])
            imgs = [canon_under(a, t) for t in D4]
            for i, im in enumerate(imgs):
                if im == self_form:
                    cfix[i] += 1
            free_orbits.add(min(imgs))
            onesided_orbits.add(min(imgs[:4]))
        free[n] = len(free_orbits)
        onesided[n] = len(onesided_orbits)
        for i in range(8):
            classfix[i][n] = cfix[i]

    current = {frozenset([(0, 0)])}
    fixed[1] = 1
    analyze(current, 1)
    for n in range(2, maxn + 1):
        grown = set()
        for animal in current:
            for (x, y) in animal:
                for (dx, dy) in nbrs:
                    cell = (x + dx, y + dy)
                    if cell not in animal:
                        grown.add(normalize(animal | {cell}))
        fixed[n] = len(grown)
        analyze(grown, n)
        current = grown
    return {"fixed": fixed, "free": free,
            "onesided": onesided, "classfix": classfix}


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in NEIGHBORS:
        sys.exit(f"usage: {sys.argv[0]} {{{'|'.join(NEIGHBORS)}}} MAXN")
    lattice, maxn = sys.argv[1], int(sys.argv[2])
    for n, c in count_fixed(lattice, maxn).items():
        print(n, c)


if __name__ == "__main__":
    main()
