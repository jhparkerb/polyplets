#!/usr/bin/env python3
# S3: fixed polyplets by number of DIAGONAL contacts d (unordered pairs of cells at
# offset (+-1,+-1)). Correctness check: ROW SUMS = A006770 (every polyplet counted once).
# NOTE T(n,0) = 2 for n>=2 (only the horizontal and vertical straight lines are diagonal-
# free) -- NOT the polyomino count: a polyomino like the L-tromino is rook-connected yet
# still has a diagonal contact, so "no diagonal contact" is far stricter than rook-connected.
KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982]


def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def ndiag(cells):
    s = set(cells); c = 0
    for (x, y) in cells:
        for dx, dy in ((1, 1), (1, -1)):          # count each unordered pair once
            if (x + dx, y + dy) in s:
                c += 1
    return c


NMAX = 9
level = {1: {canon({(0, 0)})}}
for s in range(2, NMAX + 1):
    nxt = set()
    for shape in level[s - 1]:
        for (x, y) in shape:
            for dx, dy in KING:
                cc = (x + dx, y + dy)
                if cc not in shape:
                    nxt.add(canon(shape | {cc}))
    level[s] = nxt

from collections import Counter
print(" n   T(n,0)   rowsum  A006770 ok?   max d   T(n,d) head")
total_contacts = []
for s in range(1, NMAX + 1):
    row = Counter(ndiag(sh) for sh in level[s])
    rs = sum(row.values())
    md = max(row)
    total_contacts.append(sum(d * c for d, c in row.items()))
    okr = 'OK' if rs == A006770[s - 1] else 'BAD'
    head = " ".join(f"{d}:{row[d]}" for d in range(0, min(md + 1, 6)))
    print(f" {s}   {row.get(0,0):6d}   {rs:7d} {A006770[s-1]:7d} {okr}   {md:3d}   {head}")
print()
print("total diagonal contacts over all n-cell polyplets, n=1..%d:" % NMAX)
print(", ".join(map(str, total_contacts)))
