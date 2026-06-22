#!/usr/bin/env python3
# New-sequence candidate: HV-convex fixed polyplets (king animals every row AND every
# column of which is a contiguous run). Enumerate all fixed polyplets by canonical growth
# (sanity-checked against A006770), then count the HV-convex ones.

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982]  # fixed polyplets, n=1..8


def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def _tup(cells):                            # translate-canonical SORTED tuple (total order;
    mx = min(x for x, y in cells); my = min(y for x, y in cells)   # frozenset < is subset!)
    return tuple(sorted((x - mx, y - my) for x, y in cells))


def d4_canon(cells):                        # free: lexmin sorted-tuple over the 8 D4 images
    best = None
    c = set(cells)
    for _ in range(4):
        for img in (c, {(-x, y) for x, y in c}):
            k = _tup(img)
            if best is None or k < best:
                best = k
        c = {(y, -x) for x, y in c}          # rotate 90
    return best


def c4_canon(cells):                        # one-sided: lexmin over the 4 rotations only
    best = None
    c = set(cells)
    for _ in range(4):
        k = _tup(c)
        if best is None or k < best:
            best = k
        c = {(y, -x) for x, y in c}
    return best


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

A030222 = [1, 2, 5, 22, 94, 524, 3031, 18770, 118133]  # FREE polyplets, n=1..9 (sanity)
print(" n  #fixed  A006770 ok?  HVfix diagfix | #free A030222 ok?  HVfree diagfree")
hv = []; dg = []; hvf = []; dgf = []; hvo = []; dgo = []
for s in range(1, NMAX + 1):
    fixed = level[s]
    h = sum(1 for sh in fixed if hv_convex(sh))
    d = sum(1 for sh in fixed if diag_convex(sh))
    free = {d4_canon(sh) for sh in fixed}                       # dedup up to D4
    hf = len({d4_canon(sh) for sh in fixed if hv_convex(sh)})   # convexity is D4-invariant
    df = len({d4_canon(sh) for sh in fixed if diag_convex(sh)})
    ho = len({c4_canon(sh) for sh in fixed if hv_convex(sh)})   # one-sided (rotations only)
    do = len({c4_canon(sh) for sh in fixed if diag_convex(sh)})
    hvo.append(ho); dgo.append(do)
    hv.append(h); dg.append(d); hvf.append(hf); dgf.append(df)
    okx = 'OK' if len(fixed) == A006770[s - 1] else 'BAD'
    okf = 'OK' if len(free) == A030222[s - 1] else 'BAD'
    print(f" {s} {len(fixed):8d} {okx:3s} {h:5d} {d:6d} | {len(free):6d} {okf:3s} "
          f"{hf:5d} {df:6d}")
print()
print("HV-convex   FIXED:    ", ", ".join(map(str, hv)))
print("HV-convex   ONE-SIDED:", ", ".join(map(str, hvo)))
print("HV-convex   FREE:     ", ", ".join(map(str, hvf)))
print("diag-convex FIXED:    ", ", ".join(map(str, dg)))
print("diag-convex ONE-SIDED:", ", ".join(map(str, dgo)))
print("diag-convex FREE:     ", ", ".join(map(str, dgf)))
