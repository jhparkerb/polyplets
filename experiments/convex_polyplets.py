#!/usr/bin/env python3
# New-sequence candidate: HV-convex fixed polyplets (king animals every row AND every
# column of which is a contiguous run). Enumerate all fixed polyplets by canonical growth
# (sanity-checked against A006770), then count the HV-convex ones.

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982]  # fixed polyplets, n=1..8


def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def hv_convex(cells):
    rows = {}; cols = {}
    for x, y in cells:
        rows.setdefault(y, []).append(x)
        cols.setdefault(x, []).append(y)
    for v in rows.values():
        if max(v) - min(v) + 1 != len(v):   # row must be a gap-free run
            return False
    for v in cols.values():
        if max(v) - min(v) + 1 != len(v):
            return False
    return True


NMAX = 9
# level[s] = set of canonical fixed polyplets of size s
level = {1: {canon({(0, 0)})}}
for s in range(2, NMAX + 1):
    nxt = set()
    for shape in level[s - 1]:
        for (x, y) in shape:
            for dx, dy in KING:
                c = (x + dx, y + dy)
                if c not in shape:
                    nxt.add(canon(shape | {c}))
    level[s] = nxt

print(" n   #fixed polyplets   A006770   ok?   HV-convex")
hv = []
for s in range(1, NMAX + 1):
    tot = len(level[s])
    ok = (tot == A006770[s - 1])
    h = sum(1 for sh in level[s] if hv_convex(sh))
    hv.append(h)
    print(f" {s}      {tot:8d}      {A006770[s-1]:8d}   {'OK' if ok else 'BAD'}   {h:6d}")
print("\nHV-convex fixed polyplets, n=1..%d:" % NMAX)
print(", ".join(map(str, hv)))
