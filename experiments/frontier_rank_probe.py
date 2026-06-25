#!/usr/bin/env python3
# frontier_rank_probe.py N -- does a SPARSE diagonal sweep have fewer states than a column
# sweep? Enumerate king-polyplets (Redelmeier, fixed) of size <= N; for each, at its middle
# column-cut and middle anti-diagonal-cut, compute the transfer-matrix frontier signature
# (occupied interface cells, translation-canonicalized, + component partition induced by the
# left part). Count DISTINCT signatures per size for each cut. If diag grows with a smaller
# exponent than column, the sparse (occupancy) representation beats the extent -> the
# lambda^(n/2) dream is alive; if it tracks column, the positional cost is real (dream dead).
# This counts distinct reachable states = an upper bound on the connection-rank, lower bound
# on a real engine's width -- the directly relevant quantity. Gympie, serial. Usage: ... N
import sys
sys.setrecursionlimit(10000)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
NB = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
def allowed(x,y): return y > 0 or (y == 0 and x > 0)

sig_col = [set() for _ in range(N+1)]
sig_diag = [set() for _ in range(N+1)]

def components(cs):
    cs = set(cs); comp = {}; cid = 0
    for c in cs:
        if c in comp: continue
        st = [c]; comp[c] = cid
        while st:
            p = st.pop()
            for dx,dy in NB:
                q = (p[0]+dx, p[1]+dy)
                if q in cs and q not in comp: comp[q] = cid; st.append(q)
        cid += 1
    return comp

def sig_for(cells, coord):       # coord(p) = sweep coordinate (x for col, x+y for diag)
    vals = [coord(p) for p in cells]
    lo, hi = min(vals), max(vals)
    if hi == lo: return None
    c = (lo + hi) // 2                       # left = coord <= c
    left = [p for p in cells if coord(p) <= c]
    if not left or len(left) == len(cells): return None
    comp = components(left)
    # interface = left cells whose coord is within 2 of the cut (king spans dcoord<=2 on diag,
    # 1 on column) -- take coord in {c, c-1} (covers both; column just won't populate c-1 across)
    front = [p for p in left if coord(p) in (c, c-1)]
    if not front: return None
    front.sort(key=lambda p: (coord(p), p[0], p[1]))
    x0 = min(p[0] for p in front); y0 = min(p[1] for p in front)
    lab = {}; nxt = 0; out = []
    for p in front:
        cc = comp[p]
        if cc not in lab: lab[cc] = nxt; nxt += 1
        out.append((coord(p) - c, p[0]-x0, p[1]-y0, lab[cc]))
    return tuple(out)

cells = [(0,0)]; reached = {(0,0)}
def record():
    m = len(cells)
    if 1 <= m <= N:
        s1 = sig_for(cells, lambda p: p[0])
        if s1 is not None: sig_col[m].add(s1)
        s2 = sig_for(cells, lambda p: p[0]+p[1])
        if s2 is not None: sig_diag[m].add(s2)

def grow(untried):
    record()
    if len(cells) == N: return
    u = list(untried)
    while u:
        c = u.pop(); added = []
        for dx,dy in NB:
            nx,ny = c[0]+dx, c[1]+dy
            if allowed(nx,ny) and (nx,ny) not in reached:
                reached.add((nx,ny)); added.append((nx,ny))
        cells.append(c); grow(u + added); cells.pop()
        for a in added: reached.discard(a)

init = [(dx,dy) for dx,dy in NB if allowed(dx,dy)]
for p in init: reached.add(p)
grow(init)

print(f"{'n':>3} {'col_states':>11} {'diag_states':>12} {'col_ratio':>9} {'diag_ratio':>10}")
pc = pd = 0
for m in range(1, N+1):
    a, b = len(sig_col[m]), len(sig_diag[m])
    rc = (a/pc) if pc else 0; rd = (b/pd) if pd else 0
    print(f"{m:>3} {a:>11} {b:>12} {rc:>9.2f} {rd:>10.2f}")
    pc, pd = a, b
