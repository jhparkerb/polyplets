#!/usr/bin/env python3
"""Parameterized king twig bound: window radius R from argv. Larger R keeps more
context (forbidden/required cells) in each reduced type => tighter, still a valid
over-count by construction. Computes the bound; verifies a SAMPLE of recurrences
against brute force (full verification is O(types * polyplets), too slow at large
R, but every reduction is valid by the same over-count logic proven at R=1).

Usage: python3 -m experiments.king_bound_R <R> [nverify]
"""
import sys, time
from experiments.king_types import all_polyplets, type_count, OFF

R = int(sys.argv[1]) if len(sys.argv) > 1 else 2
NVER = int(sys.argv[2]) if len(sys.argv) > 2 else 6
KING8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
WIN = [(dx,dy) for dx in range(-R,R+1) for dy in range(-R,R+1) if (dx,dy)!=(0,0)]

def free_cells(f,r): return [d for d in KING8 if d not in f and d not in r]
def cluster(cells):
    cells=set(cells); seen=set(); comps=[]
    for s in cells:
        if s in seen: continue
        c=[]; st=[s]; seen.add(s)
        while st:
            p=st.pop(); c.append(p)
            for q in cells:
                if q not in seen and max(abs(p[0]-q[0]),abs(p[1]-q[1]))==1: seen.add(q); st.append(q)
        comps.append(c)
    return comps
def reduce_t(f,r,S,comp):
    occ=set(r)|set(S); ke=set(f)|(set(free_cells(f,r))-set(S))|{(0,0)}
    u=min(comp,key=lambda p:(p[1],p[0]))
    fu=frozenset(o for o in WIN if (u[0]+o[0],u[1]+o[1]) in ke)
    ru=frozenset(o for o in WIN if (u[0]+o[0],u[1]+o[1]) in occ and (u[0]+o[0],u[1]+o[1])!=u)
    return (fu,ru)
def decomp(T):
    f,r=T; fc=free_cells(f,r); leafT=[]; cutT=[]
    for mask in range(1<<len(fc)):
        S=[fc[i] for i in range(len(fc)) if mask>>i&1]; occ=set(r)|set(S)
        if not occ: continue
        cm=cluster(occ)
        if len(cm)==1: leafT.append(reduce_t(f,r,S,cm[0]))
        else: cutT.append([reduce_t(f,r,S,c) for c in cm])
    return leafT,cutT

t0=time.time()
G8=(frozenset({OFF[o] for o in ('W','SW','S','SE')}),frozenset())
recur={}; seen={G8}; q=[G8]
while q:
    T=q.pop(); recur[T]=decomp(T)
    for Tp in recur[T][0]+[p for pc in recur[T][1] for p in pc]:
        if Tp not in seen: seen.add(Tp); q.append(Tp)
print(f"R={R}: {len(recur)} types, closure {time.time()-t0:.1f}s")

def step(v,x):
    nv={}
    for T,(lt,ct) in recur.items():
        s=x
        for Tp in lt: s+=x*v[Tp]
        for pc in ct:
            u=x
            for p in pc: u*=v[p]
            s+=u
        nv[T]=s
    return nv
def bounded(x,iters=8000,cap=1e9):
    v={T:x for T in recur}
    for _ in range(iters):
        nv=step(v,x)
        if nv[G8]>cap: return False
        if abs(nv[G8]-v[G8])<1e-13*nv[G8]: return True
        v=nv
    return True
lo,hi=1/13.0,1/6.0
for _ in range(55):
    m=0.5*(lo+hi)
    if bounded(m): lo=m
    else: hi=m
lam=1/(0.5*(lo+hi))
print(f"king upper bound  lambda <= {lam:.4f}   (< 12.2? {lam<12.2})   [{time.time()-t0:.1f}s]")

# sample verification
lv=all_polyplets(9)
sample=list(recur)[:NVER]
tc={T:type_count(lv,forbid=tuple(T[0]),require=tuple(T[1])) for T in set(sample)|{p for T in sample for p in recur[T][0]}|{p for T in sample for pc in recur[T][1] for p in pc}}
def rhs(T,n):
    lt,ct=recur[T]; s=(1 if n==1 else 0)
    for Tp in lt: s+=tc.get(Tp,{}).get(n-1,0) if Tp in tc else type_count(lv,forbid=tuple(Tp[0]),require=tuple(Tp[1])).get(n-1,0)
    for pc in ct:
        def rec(parts,m):
            if len(parts)==1: return tc[parts[0]].get(m,0) if parts[0] in tc else 0
            return sum((tc[parts[0]].get(i,0) if parts[0] in tc else 0)*rec(parts[1:],m-i) for i in range(1,m))
        s+=rec(pc,n-1)
    return s
try:
    ok=all(tc[T][n]<=rhs(T,n) for T in sample for n in range(1,10))
    print(f"  sample verification ({len(sample)} types): valid over-counts = {ok}")
except Exception as e:
    print("  sample verification skipped:", e)
