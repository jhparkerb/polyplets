#!/usr/bin/env python3
"""What ARE the perimeter-preserving removals at one corner of an isoperimetric hull?

results/perimeter-both-ends.md measures the free-removal counts per hull and
finds P(x)^4 on king's square box and P(x)^6 on tri6's hexagon -- a Young diagram
at each corner, independently -- but square4's diamond gives 1,4,18,60,187,524,
whose 4th root 1,1,3,5,9,14 is NOT the partition numbers. That 4th root is an
inference; this script measures the per-corner series DIRECTLY, by confining the
removals to a single corner of a hull big enough that the corners cannot
interact, and then prints the SHAPES so the rule can be read off rather than
guessed.

The control is king: its corner must reproduce the partition numbers
1, 1, 2, 3, 5, 7, and its shapes must be Young diagrams. If it does not, the
method is wrong and square4's answer means nothing.

The lead being tested for square4: undo the rotation with
(a,b) = ((u+v)/2, (u-v)/2) and a diamond tip becomes the CONE {a >= |b|}. Free
removals looked like an order-ideal condition by hand -- the tip cell is free,
the cell behind it is not free until the tip goes -- and for king's square corner
that same condition gives order ideals of the quadrant, which are exactly the
partitions. So the prediction is that square4's per-tip series counts ORDER
IDEALS OF THE CONE, the cone's analogue of a Young diagram.

    python3 experiments/perimeter_min_tip_shapes.py --lattice square4 --radius 8
    python3 experiments/perimeter_min_tip_shapes.py --lattice square8 --radius 8
"""

from __future__ import annotations

import argparse
import itertools
import sys
from collections import defaultdict

# (offsets, parity_filter) per lattice, in the frame perimeter_min uses.
LAT = {
    # square4 in the rotated frame: 4 diagonal neighbours, cells carry u+v even
    "square4": ([(-1, -1), (1, -1), (-1, 1), (1, 1)], True),
    # square8 in the plain frame: 8 king neighbours, no parity filter
    "square8": ([(-1, -1), (0, -1), (1, -1), (-1, 0),
                 (1, 0), (-1, 1), (0, 1), (1, 1)], False),
}


def perimeter(cells, offs):
    """Number of distinct EMPTY cells adjacent to the animal."""
    occ = cells
    per = set()
    for (u, v) in occ:
        for du, dv in offs:
            q = (u + du, v + dv)
            if q not in occ:
                per.add(q)
    return len(per)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lattice", required=True, choices=sorted(LAT))
    ap.add_argument("--radius", type=int, default=8,
                    help="hull half-size; must be big enough that removals near "
                         "one corner cannot reach another")
    ap.add_argument("--jmax", type=int, default=5)
    ap.add_argument("--show", type=int, default=3,
                    help="print the actual shapes up to this size")
    args = ap.parse_args()

    offs, parity = LAT[args.lattice]
    R = args.radius
    side = 2 * R + 1
    hull = {(u, v) for u in range(side) for v in range(side)
            if (not parity) or ((u + v) % 2 == 0)}
    base = perimeter(hull, offs)

    # Candidate removal cells: those near the (0,0) corner. Keeping them well
    # inside the hull's own extent means a removal can never shrink the bounding
    # box or reach another corner, so what is measured is one corner alone.
    cand = sorted(c for c in hull if c[0] + c[1] <= 2 * args.jmax + 2)
    print("lattice %s  hull side %d (%d cells)  base perimeter %d"
          % (args.lattice, side, len(hull), base))
    print("candidate cells near the corner: %d" % len(cand))

    def connected(cells):
        if not cells:
            return True
        start = next(iter(cells))
        seen, stack = {start}, [start]
        while stack:
            u, v = stack.pop()
            for du, dv in offs:
                q = (u + du, v + dv)
                if q in cells and q not in seen:
                    seen.add(q)
                    stack.append(q)
        return len(seen) == len(cells)

    counts = defaultdict(int)
    shapes = defaultdict(list)
    for j in range(0, args.jmax + 1):
        for S in itertools.combinations(cand, j):
            rem = hull - set(S)
            if perimeter(rem, offs) != base:
                continue
            if not connected(rem):
                continue
            counts[j] += 1
            if j <= args.show:
                shapes[j].append(S)
    print()
    print("per-corner free-removal counts, j = 0..%d:" % args.jmax)
    print("   %s" % [counts[j] for j in range(args.jmax + 1)])
    print()
    print("partition numbers p(j) for comparison:  [1, 1, 2, 3, 5, 7, 11]")
    print()

    # Shapes, in cone coordinates for square4 (undo the rotation) and plain
    # coordinates for square8.
    for j in range(1, args.show + 1):
        print("shapes of size %d (%d of them):" % (j, counts[j]))
        for S in shapes[j]:
            if args.lattice == "square4":
                pts = [((u + v) // 2, (u - v) // 2) for (u, v) in S]
                print("   cone(a,b): %s" % sorted(pts))
            else:
                print("   (u,v): %s" % sorted(S))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
