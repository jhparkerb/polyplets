#!/usr/bin/env python3
"""Joint census of (area, bounding-box height, site perimeter) for king animals.

Asks what any two of the three tell you about the third, and what all three
together pin down.  Brute force, so small n -- the point is the shape of the
constraint region, not the numbers.

    python3 experiments/king_joint_nhp.py 9

Emits `n H p count` rows plus a summary of the observed envelope.
"""
from __future__ import annotations

import sys
from collections import defaultdict

K8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]


def census(nmax):
    """-> {(n, H, p): count} over fixed king animals, via canonical-set growth."""
    joint = defaultdict(int)

    def stats(a):
        p = len({(x + dx, y + dy) for x, y in a for dx, dy in K8} - a)
        ys = [y for _, y in a]
        return max(ys) - min(ys) + 1, p

    def canon(a):
        mx = min(x for x, _ in a)
        my = min(y for _, y in a)
        return frozenset((x - mx, y - my) for x, y in a)

    seed = frozenset({(0, 0)})
    h, p = stats(seed)
    joint[(1, h, p)] += 1
    frontier = {seed}
    seen = {seed}
    for _ in range(2, nmax + 1):
        nxt = set()
        for a in frontier:
            for cx, cy in a:
                for dx, dy in K8:
                    b = (cx + dx, cy + dy)
                    if b in a:
                        continue
                    q = canon(a | {b})
                    if q in seen:
                        continue
                    seen.add(q)
                    nxt.add(q)
                    h, p = stats(q)
                    joint[(len(q), h, p)] += 1
        frontier = nxt
    return joint


def main(argv):
    nmax = int(argv[1]) if len(argv) > 1 else 8
    joint = census(nmax)

    for key in sorted(joint):
        print("%d %d %d %d" % (*key, joint[key]))

    print("\n-- what two of three pin down --")
    by_nh, by_np, by_hp = defaultdict(set), defaultdict(set), defaultdict(set)
    for n, h, p in joint:
        by_nh[(n, h)].add(p)
        by_np[(n, p)].add(h)
        by_hp[(h, p)].add(n)

    for label, d, third in (("(n,H) -> p", by_nh, "p"),
                            ("(n,p) -> H", by_np, "H"),
                            ("(H,p) -> n", by_hp, "n")):
        widest = max(d, key=lambda k: len(d[k]))
        determined = sum(1 for v in d.values() if len(v) == 1)
        print(f"  {label}: {determined}/{len(d)} pairs determine {third}; "
              f"widest spread {len(d[widest])} at {widest} -> "
              f"{sorted(d[widest])[:3]}..{sorted(d[widest])[-1]}")

    print("\n-- envelope of p at fixed (n,H) --")
    print("   n   H   p_min  p_max   4n+4")
    for n in range(1, nmax + 1):
        for h in range(1, n + 1):
            ps = by_nh.get((n, h))
            if ps:
                print(f"  {n:2d}  {h:2d}   {min(ps):4d}   {max(ps):4d}   {4*n+4:4d}")

    print("\n-- triples pinning a unique fixed animal --")
    uniq = sorted(k for k, v in joint.items() if v == 1)
    print(f"  {len(uniq)} of {len(joint)} live triples hold exactly one animal")
    print(f"  e.g. {uniq[:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
