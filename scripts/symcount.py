"""S2 symmetric-animal counter (corrected design, June 13, 2026).

Counts connected g-symmetric lattice animals by size, for a symmetry group g
acting on the square (king) lattice with its center/axis pinned at a fixed
location. Method: Redelmeier over the ORBIT GRAPH (nodes = <g>-orbits of
cells) to enumerate connected orbit-subsets once each, then keep only those
whose lifted CELL set is genuinely king-connected. That connectivity filter is
the fix over the rejected pure orbit-subgraph count (which scored
symmetric-but-disconnected sets like {(1,0),(-1,0)} as valid). See
docs-s2-symmetric-enumerator.md.

Pinning the center removes translation freedom, so each symmetric
translation-class is counted once; summing over all center placements of a
symmetry type reproduces Burnside's Fix(g).
"""

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]


def build_orbit_graph(group, R):
    """group: list of cell->cell transforms (a group, incl. identity).
    R: animals of size <= R fit within radius R of the pinned center.
    Returns (orbits, adj): orbits[i] = frozenset of cells; adj[i] = set of
    orbit indices king-adjacent to i. Orbits leaving the box are dropped.
    """
    lo, hi = -(R + 1), R + 1
    inbox = lambda c: lo <= c[0] <= hi and lo <= c[1] <= hi
    seen = set()
    orbits = []
    for x in range(lo, hi + 1):
        for y in range(lo, hi + 1):
            c = (x, y)
            if c in seen:
                continue
            orb = {t(*c) for t in group}
            seen |= orb
            if all(inbox(o) for o in orb):
                orbits.append(frozenset(orb))
    orbits.sort(key=min)
    cell2idx = {}
    for i, o in enumerate(orbits):
        for c in o:
            cell2idx[c] = i
    adj = [set() for _ in orbits]
    for i, o in enumerate(orbits):
        for (x, y) in o:
            for dx, dy in KING:
                j = cell2idx.get((x + dx, y + dy))
                if j is not None and j != i:
                    adj[i].add(j)
                    adj[j].add(i)
    return orbits, adj


def _connected(cells):
    cells = set(cells)
    start = next(iter(cells))
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for dx, dy in KING:
            n = (x + dx, y + dy)
            if n in cells and n not in seen:
                seen.add(n)
                stack.append(n)
    return len(seen) == len(cells)


def count_symmetric(group, maxn, anchor=None):
    """Return {n: # connected g-symmetric animals of size n} for 1<=n<=maxn,
    with g's center/axis pinned (one placement).

    anchor: optional predicate(cells)->bool used to pin any residual
    translation a pinned *axis* still allows (a rotation center pins
    everything, so anchor=None there; a mirror line leaves translation ALONG
    it free, so the anchor selects one canonical translate)."""
    orbits, adj = build_orbit_graph(group, maxn + 2)
    weight = [len(o) for o in orbits]
    counts = [0] * (maxn + 1)
    V = len(orbits)
    reached = [False] * V

    def search(root, chosen, untried, w):
        cells = [c for idx in chosen for c in orbits[idx]]
        if _connected(cells) and (anchor is None or anchor(cells)):
            counts[w] += 1
        ut = list(untried)
        while ut:
            v = ut.pop()
            nw = w + weight[v]
            if nw <= maxn:
                newun = list(ut)
                newly = []
                for u in adj[v]:
                    if u > root and not reached[u]:
                        reached[u] = True
                        newly.append(u)
                        newun.append(u)
                search(root, chosen + [v], newun, nw)
                for u in newly:
                    reached[u] = False

    for root in range(V):
        if weight[root] > maxn:
            continue
        for i in range(V):
            reached[i] = False
        reached[root] = True
        untried = []
        for u in adj[root]:
            if u > root and not reached[u]:
                reached[u] = True
                untried.append(u)
        search(root, [root], untried, weight[root])
    return {n: counts[n] for n in range(1, maxn + 1) if counts[n]}


# Symmetry-type placements as transform groups (identity first).
ID = lambda x, y: (x, y)

R180_PLACEMENTS = {
    "C":  [ID, lambda x, y: (-x, -y)],       # center on a cell
    "Mh": [ID, lambda x, y: (1 - x, -y)],    # horizontal-edge midpoint
    "Mv": [ID, lambda x, y: (-x, 1 - y)],    # vertical-edge midpoint
    "V":  [ID, lambda x, y: (1 - x, 1 - y)], # vertex
}

# 90-degree rotational symmetry: the 4-fold center sits on a cell or a vertex
# (never an edge midpoint). Each group is the 4 rotations about that center.
R90_PLACEMENTS = {
    "cell":   [ID,
               lambda x, y: (-y, x),
               lambda x, y: (-x, -y),
               lambda x, y: (y, -x)],
    "vertex": [ID,
               lambda x, y: (1 - y, x),
               lambda x, y: (1 - x, 1 - y),
               lambda x, y: (y, 1 - x)],
}

# Axis-parallel mirror (count the horizontal orientation only; Burnside's
# coefficient 2 covers the vertical one). Axis runs through a row of cells or
# between two rows.
HMIRROR_PLACEMENTS = {
    "through_cells": [ID, lambda x, y: (x, -y)],
    "between_rows":  [ID, lambda x, y: (x, 1 - y)],
}

# Diagonal mirror (main diagonal only; coefficient 2 covers the anti-diagonal).
# A diagonal lattice reflection must run through cell centers, so there is just
# the one placement.
DMIRROR_PLACEMENTS = {
    "through_cells": [ID, lambda x, y: (y, x)],
}

# --- Order-4 and order-8 SUBGROUPS of D4 -------------------------------------
#
# The four types above are the per-ELEMENT fixed-point counts Burnside needs.
# The orbit-SIZE distribution needs per-SUBGROUP invariant counts instead, and
# those are different objects: I(D2ax) is the set of animals fixed by BOTH axis
# mirrors, not Fix(h).  Each subgroup below has a fixed point (its center), so
# every placement pins translation completely and no anchor is needed.
#
# C4 = <r90> is already R90_PLACEMENTS: invariance under r90 IS invariance
# under the whole cyclic group, so no new placements are needed for it.

# D2ax = {e, h, v, r180}: two perpendicular axis-parallel mirrors, x = E/2 and
# y = F/2, each through a line of cells (0) or between two lines (1).
D2AX_PLACEMENTS = {
    f"x{E}y{F}": [ID,
                  (lambda E, F: lambda x, y: (x, F - y))(E, F),
                  (lambda E, F: lambda x, y: (E - x, y))(E, F),
                  (lambda E, F: lambda x, y: (E - x, F - y))(E, F)]
    for E in (0, 1) for F in (0, 1)
}

# D2diag = {e, d, ad, r180}: the two diagonal mirrors.  A diagonal lattice
# reflection must run through cell centers, so the axes are y = x and
# x + y = D; translation moves the pair by (-a+b, a+b), so only D mod 2
# survives -- two placements, centered on a cell (D=0) or a vertex (D=1).
D2DIAG_PLACEMENTS = {
    f"d{D}": [ID,
              lambda x, y: (y, x),
              (lambda D: lambda x, y: (D - y, D - x))(D),
              (lambda D: lambda x, y: (D - x, D - y))(D)]
    for D in (0, 1)
}

# D4, the full group: center on a cell (V=0) or a vertex (V=1), as for r90.
D4_PLACEMENTS = {
    f"c{V}": [ID,
              (lambda V: lambda x, y: (V - y, x))(V),
              (lambda V: lambda x, y: (V - x, V - y))(V),
              (lambda V: lambda x, y: (y, V - x))(V),
              (lambda V: lambda x, y: (x, V - y))(V),
              (lambda V: lambda x, y: (V - x, y))(V),
              lambda x, y: (y, x),
              (lambda V: lambda x, y: (V - y, V - x))(V)]
    for V in (0, 1)
}


# Residual-translation anchors: a rotation center pins position fully (None);
# a horizontal mirror axis leaves x free -> pin leftmost cell at x=0; a
# diagonal axis leaves the (1,1) direction free -> pin min(x+y) to {0,1}
# (translation along the diagonal moves x+y in steps of 2).
NO_ANCHOR = None


def _anchor_xmin0(cells):
    return min(c[0] for c in cells) == 0


def _anchor_diag(cells):
    return min(c[0] + c[1] for c in cells) in (0, 1)


# Each symmetry type: (placements, anchor). Summing placements -> Fix(g).
SYMMETRY_TYPES = {
    "90-degree rotation":  (R90_PLACEMENTS, NO_ANCHOR),
    "180-degree rotation": (R180_PLACEMENTS, NO_ANCHOR),
    "axis mirror":         (HMIRROR_PLACEMENTS, _anchor_xmin0),
    "diagonal mirror":     (DMIRROR_PLACEMENTS, _anchor_diag),
}


# Each SUBGROUP: (placements, anchor). Summing placements -> I(H), the number
# of fixed animals invariant under H. Keys match symcount_fast's CLI names.
SUBGROUP_TYPES = {
    "c4":     (R90_PLACEMENTS,    NO_ANCHOR),
    "d2ax":   (D2AX_PLACEMENTS,   NO_ANCHOR),
    "d2diag": (D2DIAG_PLACEMENTS, NO_ANCHOR),
    "d4":     (D4_PLACEMENTS,     NO_ANCHOR),
}


def count_symmetry_type(placements, maxn, anchor=None):
    """Sum counts over all center/axis placements of one symmetry type."""
    total = {}
    for group in placements.values():
        for n, c in count_symmetric(group, maxn, anchor).items():
            total[n] = total.get(n, 0) + c
    return total
