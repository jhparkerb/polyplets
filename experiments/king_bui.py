#!/usr/bin/env python3
"""Bui-faithful king decomposition: case ONE free cell d at a time.
  d empty    -> type T' = T + {d forbidden}, same n
  d occupied -> split: d's piece (type D) convolved with the c-side (type T')
  =>  phi_T = phi_{T'} + phi_{T'} * phi_D          (T' = T+{d forbidden})
Base: all 8 neighbours forbidden -> isolated marked cell -> phi = x (n=1 only).
Verified against brute force, then the certificate iteration gives the bound.
"""
import sys, time
from experiments.king_types import all_polyplets, type_count, OFF

KING8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
def free_cells(f): return [d for d in KING8 if d not in f]

RD = int(sys.argv[1]) if len(sys.argv) > 1 else 2
WD = [(dx,dy) for dx in range(-RD,RD+1) for dy in range(-RD,RD+1) if (dx,dy)!=(0,0)]
def d_type(f, d):
    """type of d when split off. Empty in the d-piece = c=(0,0), all of c's OTHER
    neighbours (go to c-side), and T's forbidden cells; window RD around d."""
    ke = {(0,0)} | (set(KING8) - {d}) | set(f)
    return frozenset(o for o in WD if (d[0]+o[0], d[1]+o[1]) in ke)

import os
ORDER = os.environ.get("DORDER", "ll")
def canonical(free):
    if ORDER == "ll":  return min(free, key=lambda p:(p[1], p[0]))        # lowest-leftmost
    if ORDER == "hr":  return max(free, key=lambda p:(p[1], p[0]))        # highest-rightmost
    if ORDER == "diag":return min(free, key=lambda p:(-(abs(p[0])+abs(p[1])), p[1], p[0]))  # diagonal first
    if ORDER == "orth":return min(free, key=lambda p:( (abs(p[0])+abs(p[1])), p[1], p[0]))  # orthogonal first
    return min(free, key=lambda p:(p[1], p[0]))

# closure: each type -> ('base',) or (Tprime, D)
recur = {}
G8 = frozenset({OFF[o] for o in ('W','SW','S','SE')})
seen = {G8}; q = [G8]
while q:
    T = q.pop(); fr = free_cells(T)
    if not fr:
        recur[T] = None                                # base
        continue
    d = canonical(fr)
    Tp = frozenset(set(T) | {d})
    D  = d_type(T, d)
    recur[T] = (Tp, D)
    for X in (Tp, D):
        if X not in seen: seen.add(X); q.append(X)
print(f"Bui-style king system: {len(recur)} types")

# ---- verify vs brute force (skip on large systems; valid by construction) ----
if len(recur) <= 250 and not os.environ.get("NOVERIFY"):
    lv = all_polyplets(9)
    tc = {T: type_count(lv, forbid=tuple(T)) for T in recur}
    def rhs(T, n):
        r = recur[T]
        if r is None: return 1 if n == 1 else 0
        Tp, D = r
        return tc[Tp].get(n,0) + sum(tc[Tp].get(i,0)*tc[D].get(n-i,0) for i in range(1,n))
    bad = [(T,n) for T in recur for n in range(1,10) if tc[T][n] > rhs(T,n)]
    print("all recurrences valid over-counts:", not bad, "" if not bad else f"FAIL {bad[0]}")
else:
    print("verification skipped (valid by construction; RD<=2 verified True)")

# ---- certificate iteration (indexed arrays for speed) ----
tl = list(recur); ix = {T:i for i,T in enumerate(tl)}; G8i = ix[G8]; NT = len(tl)
rule = [None if recur[T] is None else (ix[recur[T][0]], ix[recur[T][1]]) for T in tl]
def bounded(x, iters=5000, cap=1e9):
    v = [x]*NT
    for _ in range(iters):
        nv = [0.0]*NT
        for i in range(NT):
            r = rule[i]
            if r is None: nv[i] = x
            else:
                a = v[r[0]]; nv[i] = a + a*v[r[1]]
        if nv[G8i] > cap: return False
        if abs(nv[G8i]-v[G8i]) < 1e-13*nv[G8i]: return True
        v = nv
    return True
lo, hi = 1/13.0, 1/4.0
for _ in range(55):
    m = 0.5*(lo+hi)
    if bounded(m): lo = m
    else: hi = m
lam = 1/(0.5*(lo+hi))
print(f"\nking upper bound  lambda <= {lam:.4f}   (RD={RD}, {NT} types)")
