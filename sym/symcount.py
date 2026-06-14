"""S2 symmetric-animal counter (corrected design, June 13, 2026).

Counts connected g-symmetric lattice animals by size, for a symmetry group g
acting on the square (king) lattice with its centre/axis pinned at a fixed
location. Method: Redelmeier over the ORBIT GRAPH (nodes = <g>-orbits of
cells) to enumerate connected orbit-subsets once each, then keep only those
whose lifted CELL set is genuinely king-connected. That connectivity filter is
the fix over the rejected pure orbit-subgraph count (which scored
symmetric-but-disconnected sets like {(1,0),(-1,0)} as valid). See
docs-s2-symmetric-enumerator.md.

Pinning the centre removes translation freedom, so each symmetric
translation-class is counted once; summing over all centre placements of a
symmetry type reproduces Burnside's Fix(g).
"""

KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]


def build_orbit_graph(group, R):
    """group: list of cell->cell transforms (a group, incl. identity).
    R: animals of size <= R fit within radius R of the pinned centre.
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


def count_symmetric(group, maxn):
    """Return {n: # connected g-symmetric animals of size n} for 1<=n<=maxn,
    with g's centre pinned (one placement)."""
    orbits, adj = build_orbit_graph(group, maxn)
    weight = [len(o) for o in orbits]
    counts = [0] * (maxn + 1)
    V = len(orbits)
    reached = [False] * V

    def search(root, chosen, untried, w):
        cells = [c for idx in chosen for c in orbits[idx]]
        if _connected(cells):
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
    "C":  [ID, lambda x, y: (-x, -y)],       # centre on a cell
    "Mh": [ID, lambda x, y: (1 - x, -y)],    # horizontal-edge midpoint
    "Mv": [ID, lambda x, y: (-x, 1 - y)],    # vertical-edge midpoint
    "V":  [ID, lambda x, y: (1 - x, 1 - y)], # vertex
}


def count_symmetry_type(placements, maxn):
    """Sum counts over all centre placements of one symmetry type."""
    total = {}
    for group in placements.values():
        for n, c in count_symmetric(group, maxn).items():
            total[n] = total.get(n, 0) + c
    return total
