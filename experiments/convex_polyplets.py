#!/usr/bin/env python3
# New-sequence candidate: HV-convex fixed polyplets (king animals every row AND every
# column of which is a contiguous run). Enumerate all fixed polyplets by canonical growth
# (sanity-checked against A006770), then count the HV-convex ones.

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982]  # fixed polyplets, n=1..8


def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def _runs(groups):
    return all(max(v) - min(v) + 1 == len(v) for v in groups.values())


def hv_convex(cells):                       # every row + every column a gap-free run
    rows = {}; cols = {}
    for x, y in cells:
        rows.setdefault(y, []).append(x)
        cols.setdefault(x, []).append(y)
    return _runs(rows) and _runs(cols)


def diag_convex(cells):                     # every diagonal (u=x+y) + anti-diagonal a run
    diags = {}; antis = {}
    for x, y in cells:
        diags.setdefault(x + y, []).append(x)
        antis.setdefault(x - y, []).append(x)
    return _runs(diags) and _runs(antis)


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

print(" n   #fixed polyplets   A006770   ok?   HV-convex   diag-convex")
hv = []; dg = []
for s in range(1, NMAX + 1):
    tot = len(level[s])
    ok = (tot == A006770[s - 1])
    h = sum(1 for sh in level[s] if hv_convex(sh))
    d = sum(1 for sh in level[s] if diag_convex(sh))
    hv.append(h); dg.append(d)
    print(f" {s}      {tot:8d}      {A006770[s-1]:8d}   {'OK' if ok else 'BAD'}   "
          f"{h:6d}      {d:6d}")
print("\nHV-convex fixed polyplets,   n=1..%d:" % NMAX, ", ".join(map(str, hv)))
print("diagonally-convex fixed polyplets, n=1..%d:" % NMAX, ", ".join(map(str, dg)))
