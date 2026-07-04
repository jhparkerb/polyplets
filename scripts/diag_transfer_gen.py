#!/usr/bin/env python3
"""General connectivity-tracking transfer matrix for the diagonal closed forms.

State = (top-row shape, partition of its cells into connected components of the
built-so-far animal). Rows are king-move; y marks per-row excess (cells-1).
Transitions are generated automatically by union-find over consecutive rows:

  * place the new row r2 at every horizontal shift that king-touches r1;
  * every component of r1 must have a cell touching r2 (else it orphans -> a
    permanent disconnection -> invalid);
  * the new frontier partition merges r2 cells that are directly adjacent
    (same-row gap 1) or that touch a common r1 component (a bridge).

Bottom row: any shape, partition = its within-row adjacency. Top row: valid iff
its cells are a single component. Then T(n,H=R) = L . T(y)^(R-1) . R and
[y^k] T(n,R) = T(R+k, R). Truncating y at order K bounds the excess, so the
state set (rows with <=K+1 cells) is finite.

Validated against the exact closed forms P_0, P_1, P_2. No data, no runs.
"""
from fractions import Fraction as F
from itertools import combinations

# ---- truncated power series in y (mod y^(K+1)) over Q ----
class PS:
    __slots__ = ("c", "K")
    def __init__(self, c, K):
        self.K = K
        self.c = [F(x) for x in c[:K + 1]] + [F(0)] * (K + 1 - len(c))
    def __add__(self, o):
        return PS([a + b for a, b in zip(self.c, o.c)], self.K)
    def __mul__(self, o):
        if isinstance(o, PS):
            r = [F(0)] * (self.K + 1)
            for i, a in enumerate(self.c):
                if a:
                    for j, b in enumerate(o.c):
                        if i + j > self.K:
                            break
                        r[i + j] += a * b
            return PS(r, self.K)
        return PS([a * F(o) for a in self.c], self.K)
    __rmul__ = __mul__

def canon_part(labels):
    m, out = {}, []
    for l in labels:
        if l not in m:
            m[l] = len(m)
        out.append(m[l])
    return tuple(out)

def uf_find(par, x):
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x

def internal_partition(row):
    n = len(row)
    par = list(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if abs(row[i] - row[j]) == 1:
                par[uf_find(par, i)] = uf_find(par, j)
    return canon_part([uf_find(par, i) for i in range(n)])

def enum_rows(maxcells, maxwidth):
    rows = []
    for size in range(1, maxcells + 1):
        for combo in combinations(range(1, maxwidth + 1), size - 1):
            rows.append((0,) + combo)
    return rows

def transitions(r1, part1, r2):
    """Yield resulting frontier state (r2, newpart) for each valid shift."""
    w1 = max(r1)
    out = []
    for shift in range(-(max(r2) + 1), w1 + 2):
        r2a = [c + shift for c in r2]
        adj = [[abs(r1[i] - r2a[j]) <= 1 for j in range(len(r2))] for i in range(len(r1))]
        # every r1 component must touch r2
        comps = {}
        for i, l in enumerate(part1):
            comps.setdefault(l, []).append(i)
        if not all(any(adj[i][j] for i in cells for j in range(len(r2)))
                   for cells in comps.values()):
            continue
        # union-find over r2 cells
        nr = len(r2)
        par = list(range(nr))
        for a in range(nr):
            for b in range(a + 1, nr):
                if abs(r2a[a] - r2a[b]) == 1:
                    par[uf_find(par, a)] = uf_find(par, b)
        r2comp = [set() for _ in range(nr)]
        for j in range(nr):
            for i in range(len(r1)):
                if adj[i][j]:
                    r2comp[j].add(part1[i])
        for a in range(nr):
            for b in range(a + 1, nr):
                if r2comp[a] & r2comp[b]:
                    par[uf_find(par, a)] = uf_find(par, b)
        out.append((r2, canon_part([uf_find(par, j) for j in range(nr)])))
    return out

def build(K, maxwidth):
    rows = enum_rows(K + 1, maxwidth)
    # discover states by BFS from bottom states
    start = {(r, internal_partition(r)) for r in rows}
    states = set(start)
    frontier = list(start)
    edges = {}  # (s1 -> {s2: count})
    while frontier:
        s1 = frontier.pop()
        r1, part1 = s1
        d = {}
        for r2 in rows:
            for s2 in transitions(r1, part1, r2):
                d[s2] = d.get(s2, 0) + 1
                if s2 not in states:
                    states.add(s2)
                    frontier.append(s2)
        edges[s1] = d
    # complete edges for any state discovered but not yet expanded
    for s1 in list(states):
        if s1 not in edges:
            r1, part1 = s1
            d = {}
            for r2 in rows:
                for s2 in transitions(r1, part1, r2):
                    d[s2] = d.get(s2, 0) + 1
            edges[s1] = d
    idx = {s: i for i, s in enumerate(sorted(states))}
    N = len(idx)
    # transfer matrix T[i][j] and vectors
    T = [[PS([0], K) for _ in range(N)] for _ in range(N)]
    for s1, d in edges.items():
        i = idx[s1]
        for s2, cnt in d.items():
            r2 = s2[0]
            T[i][idx[s2]] = T[i][idx[s2]] + PS(([0] * (len(r2) - 1)) + [cnt], K)
    L = [PS([0], K) for _ in range(N)]
    for s in start:
        r = s[0]
        L[idx[s]] = L[idx[s]] + PS(([0] * (len(r) - 1)) + [1], K)
    Rv = [PS([1] if max(s[1]) == 0 else [0], K) for s in sorted(states)]
    return T, L, Rv, N

def T_nH(T, L, Rv, R, K, N):
    v = L[:]                       # row vector; apply T (R-1) times
    for _ in range(R - 1):
        v = [sum((v[i] * T[i][j] for i in range(N)), PS([0], K)) for j in range(N)]
    return sum((v[j] * Rv[j] for j in range(N)), PS([0], K))

def expected(k, R):
    n = R + k
    if k == 0:
        return F(3) ** (n - 1)
    if k == 1:
        return (25 * n - 45) * F(3) ** (n - 4)
    if k == 2:
        return F(1, 2) * (625 * n * n - 2459 * n + 1134) * F(3) ** (n - 7)
    return None

if __name__ == "__main__":
    import sys
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    maxwidth = int(sys.argv[2]) if len(sys.argv) > 2 else 2 * K + 2
    T, L, Rv, N = build(K, maxwidth)
    print(f"K={K} maxwidth={maxwidth}: {N} interface states")
    allok = True
    for R in range(2, 10):
        ps = T_nH(T, L, Rv, R, K, N)
        line = [f"R={R}"]
        for k in range(K + 1):
            got = ps.c[k]
            exp = expected(k, R)
            ok = (exp is None) or (got == exp)
            allok &= ok if exp is not None else True
            mark = "" if ok else "  <-- MISMATCH"
            line.append(f"[y^{k}]={got}{'' if exp is None else ('=P%d ok'%k if ok else ' != %s'%exp)}{mark}")
        print("  " + " | ".join(line))
    print("ALL MATCH P_0..P_%d" % K if allok else "MISMATCH FOUND")
