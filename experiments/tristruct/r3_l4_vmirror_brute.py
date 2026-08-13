#!/usr/bin/env python3
"""r3_l4_vmirror_brute: from-scratch brute-force reference for I_H(<v>).

Enumerates ALL fixed polyplets (king-connected animals up to translation)
n <= 8 by canonical-translation growth -- no orbit graph, no frontier, no
shared code -- classifies each by v-mirror invariance (x -> -x about either
axis placement, up to translation) and true bbox height, and compares with
the banked symtm hmirror table grouped by W (the transpose reading percell
used). Pins the semantics any future vmirror quotient mode must match.
Exact integers; runs in seconds.
"""
import collections, itertools, os

ROOT = "/Users/jasonp/src/polyominoes"
NMAX = 8
KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]

def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)

def enumerate_fixed(nmax):
    """All fixed polyplets by size, as canonical frozensets."""
    animals = {1: {frozenset([(0, 0)])}}
    for n in range(2, nmax + 1):
        cur = set()
        for a in animals[n - 1]:
            for (x, y) in a:
                for dx, dy in KING:
                    c = (x + dx, y + dy)
                    if c not in a:
                        cur.add(canon(a | {c}))
        animals[n] = cur
    return animals

def is_vsym(a):
    # invariant under x -> -x up to translation (either axis placement)
    return canon({(-x, y) for x, y in a}) == canon(a)

def main():
    animals = enumerate_fixed(NMAX)
    # sanity: fixed polyplet counts A006770
    counts = [len(animals[n]) for n in range(1, NMAX + 1)]
    assert counts == [1, 4, 20, 110, 638, 3832, 23592, 147941], counts
    print("A006770 check n<=8: OK", counts)

    brute = collections.Counter()
    for n in range(1, NMAX + 1):
        for a in animals[n]:
            if is_vsym(a):
                H = max(y for _, y in a) - min(y for _, y in a) + 1
                brute[(n, H)] += 1

    banked = collections.Counter()
    with open(os.path.join(ROOT, "results/percell_raw/hmirror.byheight.n32.out")) as f:
        for line in f:
            n, H, W, c = map(int, line.split())
            if n <= NMAX:
                banked[(n, W)] += c   # transpose reading: I_W(<v>)

    keys = set(brute) | set(banked)
    mism = sum(1 for k in keys if brute[k] != banked[k])
    for k in sorted(keys):
        if brute[k] != banked[k]:
            print("MISMATCH", k, "brute", brute[k], "banked", banked[k])
    print(f"I_H(<v>) brute vs banked-transpose, n<={NMAX}: "
          f"{len(keys)} cells, {mism} mismatches")

if __name__ == "__main__":
    main()
