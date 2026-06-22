#!/usr/bin/env python3
# B3: minimum KING-perimeter of an n-cell polyplet -- the king-lattice analogue of A027709
# (min polyomino perimeter). King-perimeter = number of empty cells king-adjacent to the
# animal (the cells you would fill to "wall it off" in the king graph). Brute force, n<=9.
KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]


def canon(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def king_perim(cells):
    s = set(cells)
    boundary = set()
    for (x, y) in cells:
        for dx, dy in KING:
            nb = (x + dx, y + dy)
            if nb not in s:
                boundary.add(nb)
    return len(boundary)


NMAX = 9
level = {1: {canon({(0, 0)})}}
for s in range(2, NMAX + 1):
    nxt = set()
    for sh in level[s - 1]:
        for (x, y) in sh:
            for dx, dy in KING:
                c = (x + dx, y + dy)
                if c not in sh:
                    nxt.add(canon(sh | {c}))
    level[s] = nxt

from math import ceil, sqrt
A027709 = [2 * ceil(2 * sqrt(n)) for n in range(1, NMAX + 1)]
mins = [min(king_perim(sh) for sh in level[s]) for s in range(1, NMAX + 1)]
print("min king-perimeter of an n-cell polyplet, n=1..%d:" % NMAX)
print("  measured     :", ", ".join(map(str, mins)))
print("  A027709(n)+4 :", ", ".join(str(p + 4) for p in A027709))
ok = all(mins[i] == A027709[i] + 4 for i in range(NMAX))
print("  => min king-perimeter(n) = A027709(n) + 4  (RIGOROUS for compact rectangles):", ok)
print("  king-perim of a filled w x h box = (w+2)(h+2)-wh = 2(w+h)+4 = rook-perim + 4,")
print("  and both minima are the compact box, so this is just A027709 shifted -- not a new")
print("  sequence, but a clean king-vs-rook isoperimetric identity.")
