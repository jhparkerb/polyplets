#!/usr/bin/env python3
"""Idea 8 of results/closed-doors.md: is the graph on n-polyplets under
connectivity-preserving single-cell moves connected?

MOVE.  From an n-animal A, pick a cell c that is not a cut vertex (so
A \\ {c} is still king-connected and non-empty), then place c at any empty
position king-adjacent to A \\ {c}.  The result is an n-animal, connected by
construction.  This is the standard cell-move chain used to sample lattice
animals; if the graph is connected the chain is irreducible, which is the
gate on a uniform sampler.

THE REFORMULATION THAT MAKES IT CHEAP.  A and B are adjacent iff they share a
common connected (n-1)-subanimal.  So instead of expanding every move (n cells
to lift x ~8n re-attachment sites, ~40x more work), bucket every n-animal by
its set of legal deletions and union the animals that share a bucket.  Same
graph, and the deletions are computed once each.

Vertices are FIXED animals (translation classes), which is what a(n) counts and
what a sampler would target.  If the fixed graph is connected the free graph is
too, being a quotient of it.

Usage: python3 experiments/move_graph_connectivity.py [MAXN]
"""

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from g1_naive import NEIGHBORS  # noqa: E402

NBRS = NEIGHBORS["square8"]


def pack(cells):
    """Normalize to min x = min y = 0 and pack as bytes, one byte per cell.

    n <= 10 bounds every coordinate below 16, so x*16+y fits a byte and the
    sorted byte string is a canonical key for the translation class."""
    mx = min(x for x, y in cells)
    my = min(y for x, y in cells)
    return bytes(sorted(((x - mx) * 16 + (y - my)) for x, y in cells))


def unpack(b):
    return [(v >> 4, v & 15) for v in b]


def grow(maxn):
    """All fixed king animals of exactly maxn cells, as packed keys."""
    cur = {pack([(0, 0)])}
    for _ in range(2, maxn + 1):
        nxt = set()
        for key in cur:
            cells = unpack(key)
            s = set(cells)
            for (x, y) in cells:
                for (dx, dy) in NBRS:
                    c = (x + dx, y + dy)
                    if c not in s:
                        nxt.add(pack(cells + [c]))
        cur = nxt
    return cur


def connected(cells):
    """King-connectivity of a non-empty cell list."""
    s = set(cells)
    seed = next(iter(s))
    seen, stack = {seed}, [seed]
    while stack:
        (x, y) = stack.pop()
        for (dx, dy) in NBRS:
            c = (x + dx, y + dy)
            if c in s and c not in seen:
                seen.add(c)
                stack.append(c)
    return len(seen) == len(s)


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, a):
        p = self.p
        while p[a] != a:
            p[a] = p[p[a]]
            a = p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def analyze(n, verbose=True):
    t0 = time.time()
    keys = sorted(grow(n))
    idx = {k: i for i, k in enumerate(keys)}
    dsu = DSU(len(keys))

    # bucket -> first animal index seen with that deletion
    seen = {}
    isolated = []
    for i, key in enumerate(keys):
        cells = unpack(key)
        deletions = 0
        for j in range(n):
            rest = cells[:j] + cells[j + 1:]
            if not rest or not connected(rest):
                continue
            deletions += 1
            d = pack(rest)
            prev = seen.get(d)
            if prev is None:
                seen[d] = i
            else:
                dsu.union(i, prev)
        if deletions == 0:
            isolated.append(i)

    comps = {}
    for i in range(len(keys)):
        comps.setdefault(dsu.find(i), []).append(i)
    sizes = sorted((len(v) for v in comps.values()), reverse=True)
    wall = time.time() - t0

    if verbose:
        print(f"n = {n:>2}  animals = {len(keys):>9}  "
              f"components = {len(sizes):>6}  "
              f"largest = {sizes[0]:>9}  "
              f"{'CONNECTED' if len(sizes) == 1 else 'DISCONNECTED'}  "
              f"({wall:.1f}s)")
        if len(sizes) > 1:
            print(f"      component sizes: {sizes[:12]}"
                  f"{' ...' if len(sizes) > 12 else ''}")
            # print the smallest components -- these are the obstruction
            small = sorted(comps.values(), key=len)[:3]
            for c in small:
                for i in c[:2]:
                    draw(keys[i], indent="        ")
                    print()
        if isolated:
            print(f"      animals with NO legal move (every cell a cut "
                  f"vertex): {len(isolated)}")
            for i in isolated[:3]:
                draw(keys[i], indent="        ")
                print()
    return len(sizes), len(keys), sizes


def draw(key, indent=""):
    cells = unpack(key)
    w = max(x for x, _ in cells) + 1
    h = max(y for _, y in cells) + 1
    s = set(cells)
    for y in range(h - 1, -1, -1):
        print(indent + "".join("#" if (x, y) in s else "." for x in range(w)))


def main():
    maxn = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print("Idea 8: connectivity of the single-cell-move graph on fixed "
          "king animals\n")
    for n in range(1, maxn + 1):
        analyze(n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
