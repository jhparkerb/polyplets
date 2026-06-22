#!/usr/bin/env python3
# New-sequence candidate (S5): fixed KNIGHT animals -- sets of cells connected through
# knight moves (the 8 offsets (+-1,+-2),(+-2,+-1)). Enumerate by canonical growth and
# count by size; report fixed, one-sided (C4), and free (D4) counts.
KNIGHT = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]


def _tup(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return tuple(sorted((x - mx, y - my) for x, y in cells))


def canon(cells):
    return frozenset(_tup(cells))


def c4_canon(cells):                         # one-sided: min over 4 rotations
    best = None; c = set(cells)
    for _ in range(4):
        k = _tup(c)
        if best is None or k < best:
            best = k
        c = {(y, -x) for x, y in c}
    return best


def d4_canon(cells):                         # free: min over 8 D4 images
    best = None; c = set(cells)
    for _ in range(4):
        for img in (c, {(-x, y) for x, y in c}):
            k = _tup(img)
            if best is None or k < best:
                best = k
        c = {(y, -x) for x, y in c}
    return best


NMAX = 8
level = {1: {canon({(0, 0)})}}
for s in range(2, NMAX + 1):
    nxt = set()
    for shape in level[s - 1]:
        for (x, y) in shape:
            for dx, dy in KNIGHT:
                c = (x + dx, y + dy)
                if c not in shape:
                    nxt.add(canon(shape | {c}))
    level[s] = nxt

fixed = [len(level[s]) for s in range(1, NMAX + 1)]
oneside = [len({c4_canon(sh) for sh in level[s]}) for s in range(1, NMAX + 1)]
free = [len({d4_canon(sh) for sh in level[s]}) for s in range(1, NMAX + 1)]
print(f"fixed knight animals,     n=1..{NMAX}:", ", ".join(map(str, fixed)))
print(f"one-sided knight animals, n=1..{NMAX}:", ", ".join(map(str, oneside)))
print(f"free knight animals,      n=1..{NMAX}:", ", ".join(map(str, free)))
