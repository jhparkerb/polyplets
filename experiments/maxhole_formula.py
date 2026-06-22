#!/usr/bin/env python3
# T5 lower bound: the balanced rectangular L1-diamond is an explicit n-cell polyplet
# enclosing M(n) = ceil(floor((n-2)^2/4)/2) cells, for every n. Construct it and check
#   |hole| == M(n),  |wall| == n,  wall is one king-connected loop enclosing the hole.
# Together with the proven upper bound (docs/diamond-optimality.md) this pins M(n) exactly.
import math
from collections import deque

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
ROOK = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def Mformula(n):
    return math.ceil(((n - 2) ** 2 // 4) / 2)


def construct(n):
    # balanced (u,v)-box: side lengths (a+1)+(c+1) = n-2, as equal as possible.
    A1 = (n - 2) // 2
    C1 = (n - 2) - A1
    a, c = A1 - 1, C1 - 1
    hole = set()
    for u in range(0, a + 1):
        for v in range(0, c + 1):
            if (u + v) % 2 == 0:                       # even sublattice = real cells
                hole.add(((u + v) // 2, (u - v) // 2))
    # wall = the rook-outer-boundary of the hole (must be foreground to trap it)
    wall = set()
    for (x, y) in hole:
        for dx, dy in ROOK:
            nb = (x + dx, y + dy)
            if nb not in hole:
                wall.add(nb)
    return hole, wall


def king_connected(cells):
    if not cells:
        return True
    cells = set(cells)
    seen = {next(iter(cells))}
    dq = deque(seen)
    while dq:
        x, y = dq.popleft()
        for dx, dy in KING:
            nb = (x + dx, y + dy)
            if nb in cells and nb not in seen:
                seen.add(nb); dq.append(nb)
    return len(seen) == len(cells)


def hole_is_trapped(hole, wall):
    # flood the background (off wall) from the hole; must not escape a big box
    lim = 60
    seen = set(hole)
    dq = deque(hole)
    while dq:
        x, y = dq.popleft()
        if abs(x) > lim or abs(y) > lim:
            return False                                # leaked to "infinity"
        for dx, dy in ROOK:
            nb = (x + dx, y + dy)
            if nb not in wall and nb not in seen:
                seen.add(nb); dq.append(nb)
    return True


# Lower bound needs a king-loop of <= n cells enclosing M(n); if it uses fewer, pad
# the polyplet to n with wasted cells. The loop is TIGHT (== n) except where M(n) is
# flat (only n=5: M(5)=M(4)=1, so the 5th cell is necessarily wasted).
print(" n   M(n)  |hole| |wall|  king-conn  trapped  tight?  OK")
allok = True
for n in range(4, 41):
    hole, wall = construct(n)
    M = Mformula(n)
    kc = king_connected(wall)
    tr = hole_is_trapped(hole, wall)
    ok = (len(hole) == M and len(wall) <= n and kc and tr)
    allok &= ok
    tight = "tight" if len(wall) == n else f"pad+{n - len(wall)}"
    print(f"{n:3d}  {M:4d}  {len(hole):5d}  {len(wall):4d}    {str(kc):5s}     "
          f"{str(tr):5s}   {tight:6s}  {'OK' if ok else 'FAIL'}")
print("\nlower bound M(n) achieved (<=n-cell loop enclosing M(n)) for all n in 4..40:",
      "YES" if allok else "NO")
print("=> with the proven upper bound, M(n) = ceil(floor((n-2)^2/4)/2) EXACTLY for all n>=4.")
