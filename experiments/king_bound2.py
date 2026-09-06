#!/usr/bin/env python3
"""Tightened king twig system: a type is (forbidden, required) offsets -- track
which neighbors are known-OCCUPIED, not just empty, so multi-neighbor leaf
reductions don't forget context. Everything verified against brute force, then
the certificate/monotone iteration gives the bound.
"""
from experiments.king_types import all_polyplets, type_count, OFF

KING8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
def W(R): return [(dx,dy) for dx in range(-R,R+1) for dy in range(-R,R+1) if (dx,dy)!=(0,0)]
R = 1
WIN = W(R)

def free_cells(f, r): return [d for d in KING8 if d not in f and d not in r]

def cluster(cells):
    cells=set(cells); seen=set(); comps=[]
    for s in cells:
        if s in seen: continue
        c=[]; st=[s]; seen.add(s)
        while st:
            p=st.pop(); c.append(p)
            for q in cells:
                if q not in seen and max(abs(p[0]-q[0]),abs(p[1]-q[1]))==1:
                    seen.add(q); st.append(q)
        comps.append(c)
    return comps

def reduce_type(f, r, S, comp):
    """re-mark u = lowest-leftmost occupied cell of `comp`; new (forbidden,required)."""
    occ = set(r) | set(S)                     # occupied neighbors of c (c itself removed)
    ke  = set(f) | (set(free_cells(f,r)) - set(S)) | {(0,0)}   # known-empty (c-frame)
    u   = min(comp, key=lambda p:(p[1],p[0]))
    fu  = frozenset(o for o in WIN if (u[0]+o[0],u[1]+o[1]) in ke)
    ru  = frozenset(o for o in WIN if (u[0]+o[0],u[1]+o[1]) in occ and (u[0]+o[0],u[1]+o[1])!=u)
    return (fu, ru)

def decompose(T):
    f, r = T
    fc = free_cells(f, r)
    leafT=[]; cutT=[]
    for mask in range(0, 1<<len(fc)):
        S=[fc[i] for i in range(len(fc)) if mask>>i & 1]
        occ = set(r)|set(S)
        if not occ: continue                  # c must connect to something
        comps = cluster(occ)
        if len(comps)==1:
            leafT.append(reduce_type(f,r,S,comps[0]))
        else:
            cutT.append([reduce_type(f,r,S,comp) for comp in comps])
    return leafT, cutT

G8 = (frozenset({OFF[o] for o in ('W','SW','S','SE')}), frozenset())

# BFS closure
recur={}; seen={G8}; q=[G8]
while q:
    T=q.pop(); leafT,cutT=decompose(T); recur[T]=(leafT,cutT)
    for Tp in leafT+[p for pc in cutT for p in pc]:
        if Tp not in seen: seen.add(Tp); q.append(Tp)
print(f"tightened type alphabet: {len(recur)} types")

# verify recurrences vs brute force
lv=all_polyplets(9)
tc={T: type_count(lv, forbid=tuple(T[0]), require=tuple(T[1])) for T in recur}
def rhs(T,n):
    leafT,cutT=recur[T]; s=(1 if n==1 else 0)
    for Tp in leafT: s+=tc[Tp].get(n-1,0)
    for pc in cutT:
        def rec(parts,m):
            if len(parts)==1: return tc[parts[0]].get(m,0)
            return sum(tc[parts[0]].get(i,0)*rec(parts[1:],m-i) for i in range(1,m))
        s+=rec(pc,n-1)
    return s
bad=[(T,n) for T in recur for n in range(1,10) if tc[T][n] > rhs(T,n)]
print("all recurrences valid over-counts:", not bad, ("" if not bad else f" FAIL {bad[:3]}"))

# monotone iteration
def step(v,x):
    nv={}
    for T,(leafT,cutT) in recur.items():
        s=x
        for Tp in leafT: s+=x*v[Tp]
        for pc in cutT:
            t=x
            for p in pc: t*=v[p]
            s+=t
        nv[T]=s
    return nv
def bounded(x,iters=6000,cap=1e9):
    v={T:x for T in recur}
    for _ in range(iters):
        nv=step(v,x)
        if nv[G8]>cap: return False
        if abs(nv[G8]-v[G8])<1e-13*nv[G8]: return True
        v=nv
    return True
lo,hi=1/13.0,1/6.0
for _ in range(60):
    m=0.5*(lo+hi)
    if bounded(m): lo=m
    else: hi=m
lam=1/(0.5*(lo+hi))
print(f"\nking upper bound  lambda <= {lam:.4f}")
print(f"  > a(n) ratio 6.9? {lam>6.9}   < crude 12.2? {lam<12.2}")
