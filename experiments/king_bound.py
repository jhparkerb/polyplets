#!/usr/bin/env python3
"""Assemble the full king twig system (BFS closure over types), verify every
type's recurrence against brute-force counts, then find the growth-constant
upper bound by the monotone-iteration/certificate method.

  phi_T = x + sum_{leaf cases} x*phi_{T'} + sum_{cut cases} x*prod(phi_pieces)

Dominating solution's growth of the G8 type is an upper bound on lambda.
"""
from experiments.king_derive import (decompose, cluster_components, known_empty,
                                      KING8, free_cells, nm)
from experiments.king_types import all_polyplets, type_count, OFF

G8 = frozenset({OFF[o] for o in ('W','SW','S','SE')})

def cut_pieces(forbidden, S):
    ke = known_empty(forbidden, S)
    out = []
    for comp in cluster_components(S):
        u = min(comp, key=lambda p:(p[1],p[0]))
        out.append(frozenset(o for o in KING8 if (u[0]+o[0], u[1]+o[1]) in ke))
    return out

# ---- BFS closure over the type alphabet ----
recur = {}                       # T -> (list of leaf-reduced-types, list of [piece types])
seen = {G8}; queue = [G8]
while queue:
    T = queue.pop()
    leaf, cut = decompose(T)
    leafT = [Tp for (_, _, Tp) in leaf]
    cutT  = [cut_pieces(T, S) for S in cut]
    recur[T] = (leafT, cutT)
    for Tp in leafT + [p for pc in cutT for p in pc]:
        if Tp not in seen:
            seen.add(Tp); queue.append(Tp)
print(f"type alphabet closed: {len(recur)} types")

# ---- verify each type's recurrence numerically (T_true(n) <= RHS_true(n)) ----
lv = all_polyplets(9)
tc = {T: type_count(lv, forbid=tuple(T)) for T in recur}
def rhs_true(T, n):
    leafT, cutT = recur[T]
    s = (1 if n == 1 else 0)                       # base x
    for Tp in leafT: s += tc[Tp].get(n-1, 0)
    for pc in cutT:
        conv = 0
        # sum over compositions of (n-1) into len(pc) positive parts
        if len(pc) == 2:
            a, b = pc
            conv = sum(tc[a].get(i,0)*tc[b].get(n-1-i,0) for i in range(1, n-1))
        elif len(pc) == 1:
            conv = tc[pc[0]].get(n-1, 0)
        else:
            # generic (rare): recursive composition
            def rec(parts, m):
                if len(parts)==1: return tc[parts[0]].get(m,0)
                return sum(tc[parts[0]].get(i,0)*rec(parts[1:], m-i) for i in range(1,m))
            conv = rec(pc, n-1)
        s += conv
    return s
ok = all(tc[T][n] <= rhs_true(T, n) for T in recur for n in range(1,10))
print("all type recurrences are valid over-counts (T_true(n) <= RHS):", ok)

# ---- monotone iteration for the growth constant ----
def step(v, x):
    nv = {}
    for T,(leafT,cutT) in recur.items():
        s = x
        for Tp in leafT: s += x*v[Tp]
        for pc in cutT:
            t = x
            for p in pc: t *= v[p]
            s += t
        nv[T] = s
    return nv

def bounded(x, iters=4000, cap=1e9):
    v = {T: x for T in recur}
    for _ in range(iters):
        nv = step(v, x)
        if nv[G8] > cap: return False
        if abs(nv[G8]-v[G8]) < 1e-13*nv[G8]: return True
        v = nv
    return True

lo, hi = 1.0/12.5, 1.0/6.0                      # x = 1/lambda, lambda in [6,12.5]
for _ in range(60):
    mid = 0.5*(lo+hi)
    if bounded(mid): lo = mid                    # bounded => lambda<=1/mid, raise x
    else: hi = mid
lam = 1.0/(0.5*(lo+hi))
print(f"\nking upper bound  lambda <= {lam:.4f}")
print(f"  sanity: must be > a(n) ratio ~6.9 and > mu_13=6.306, and < crude 12.2")
print(f"  above 6.9? {lam>6.9}   below 12.2? {lam<12.2}")
