#!/usr/bin/env python3
"""JOB-IND-1 -- the incumbent-free oracle, pointed at the B1 rows.

Every committed check on the B1 C++ binary compares it against the incumbent
engine (tests/gate_cutcount_b1.py checks A, B, F), so the king-adjacency
stencil the two share has never been tested against anything else. This script
is the missing control: it grows every fixed king animal by literal flood fill
over the 3x3 neighbourhood, buckets by bounding-box height, and compares
against T(n,H) derived from B1's own C_H rows.

No transfer matrix, no cut, no frontier, no partition, no second difference on
the brute side -- and no contact with results/ns_a40 or results/triangle.txt.
The only input is results/cutcount_b1/rows/, which B1 produced.

  usage: r4_indoracle_brute.py <rowdir> <nmax> [--stencil king|rook] [--perturb n,H]

--stencil rook and --perturb are the RED controls: each must make the
comparison fail, and --perturb must name the exact cell it broke.

Fail-closed: exit 2 on mismatch, exit 3 if it compared nothing, exit 1 on bad
input. Only exit 0 means cells were compared and agreed.
"""

import sys
from collections import deque

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
ROOK = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def normalize(cells):
    """Translate so the minimum x and y are 0. Fixed animals: translation only."""
    mx = min(c[0] for c in cells)
    my = min(c[1] for c in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def grow(nmax, nbrs):
    """All fixed animals of size 1..nmax, by adding one neighbouring cell at a
    time and deduplicating on the translation-normalized form. Returns
    {n: set of frozensets}."""
    levels = {1: {frozenset({(0, 0)})}}
    for n in range(2, nmax + 1):
        nxt = set()
        for shape in levels[n - 1]:
            frontier = set()
            for (x, y) in shape:
                for (dx, dy) in nbrs:
                    p = (x + dx, y + dy)
                    if p not in shape:
                        frontier.add(p)
            for p in frontier:
                nxt.add(normalize(shape | {p}))
        levels[n] = nxt
    return levels


def connected(cells, nbrs):
    """Verify connectivity by flood fill -- the definition, checked literally."""
    it = iter(cells)
    start = next(it)
    seen = {start}
    q = deque([start])
    while q:
        (x, y) = q.popleft()
        for (dx, dy) in nbrs:
            p = (x + dx, y + dy)
            if p in cells and p not in seen:
                seen.add(p)
                q.append(p)
    return len(seen) == len(cells)


def height(cells):
    return max(y for _, y in cells) - min(y for _, y in cells) + 1


def brute_table(nmax, nbrs):
    """T(n,H) by growth + flood fill. Every shape is connectivity-checked
    independently of how it was grown -- the growth could be wrong and the
    check would catch it."""
    levels = grow(nmax, nbrs)
    T = {}
    for n, shapes in levels.items():
        for s in shapes:
            if not connected(s, nbrs):
                print(f"FAIL internal: grew a disconnected shape at n={n}: {sorted(s)}")
                sys.exit(1)
            H = height(s)
            T[(n, H)] = T.get((n, H), 0) + 1
    return T


def load_rows(path):
    d = {}
    with open(path) as f:
        for line in f:
            p = line.split()
            if len(p) == 2:
                d[int(p[0])] = int(p[1])
    return d


def b1_table(rowdir, nmax, hmax):
    """T(n,H) = C_H(n) - 2 C_{H-1}(n) + C_{H-2}(n), from B1's own rows."""
    C = {}
    for H in range(1, hmax + 1):
        try:
            C[H] = load_rows(f"{rowdir}/C{H}.out")
        except OSError as e:
            print(f"FAIL cannot read B1 row H={H}: {e}")
            sys.exit(1)
    C[0] = {n: 0 for n in range(nmax + 1)}
    C[-1] = {n: 0 for n in range(nmax + 1)}
    T = {}
    for H in range(1, hmax + 1):
        for n in range(1, nmax + 1):
            if n in C[H]:
                T[(n, H)] = C[H][n] - 2 * C[H - 1].get(n, 0) + C[H - 2].get(n, 0)
    return T


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip())
        return 1
    rowdir, nmax = argv[1], int(argv[2])
    stencil, perturb = "king", None
    i = 3
    while i < len(argv):
        if argv[i] == "--stencil":
            stencil = argv[i + 1]; i += 2
        elif argv[i] == "--perturb":
            a, b = argv[i + 1].split(","); perturb = (int(a), int(b)); i += 2
        else:
            print(f"FAIL unknown argument {argv[i]}"); return 1

    nbrs = KING if stencil == "king" else ROOK
    print(f"stencil={stencil} nmax={nmax} rowdir={rowdir} perturb={perturb}")

    brute = brute_table(nmax, nbrs)
    if perturb:
        brute[perturb] = brute.get(perturb, 0) + 1
        print(f"RED: perturbed brute cell {perturb} by +1")

    hmax = max(H for (_, H) in brute)
    b1 = b1_table(rowdir, nmax, hmax)

    checked, bad = 0, []
    for (n, H), v in sorted(brute.items()):
        if (n, H) not in b1:
            continue
        checked += 1
        if b1[(n, H)] != v:
            bad.append(f"MISMATCH T({n},{H}): brute={v} b1={b1[(n,H)]}")
    for line in bad[:10]:
        print(line)

    total = sum(v for (n, _), v in brute.items() if n <= nmax)
    print(f"brute animals total (n<={nmax}): {total}")
    if bad:
        print(f"\nFAIL {len(bad)} mismatch(es) over {checked} compared cells")
        return 2
    if not checked:
        print("FAIL compared 0 cells -- a check that cannot fail is not a check")
        return 3
    print(f"\nOK {checked} cells agree: literal flood-fill definition vs B1 rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
