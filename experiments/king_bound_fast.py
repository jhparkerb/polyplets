#!/usr/bin/env python3
"""Fast indexed king twig bound for larger windows R. Closes the type alphabet,
flattens to integer-indexed term lists, and runs the monotone iteration on arrays
(no per-type brute-force verification -- larger R is a valid over-count by the
same construction proven at R=1). Usage: python3 -m experiments.king_bound_fast <R>
"""
import sys, time
from experiments.king_types import OFF

R = int(sys.argv[1]) if len(sys.argv) > 1 else 2
KING8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
WIN = [(dx,dy) for dx in range(-R,R+1) for dy in range(-R,R+1) if (dx,dy)!=(0,0)]

def fc(f,r): return [d for d in KING8 if d not in f and d not in r]
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
def red(f,r,S,comp):
    occ=set(r)|set(S); ke=set(f)|(set(fc(f,r))-set(S))|{(0,0)}
    u=min(comp,key=lambda p:(p[1],p[0]))
    return (frozenset(o for o in WIN if (u[0]+o[0],u[1]+o[1]) in ke),
            frozenset(o for o in WIN if (u[0]+o[0],u[1]+o[1]) in occ and (u[0]+o[0],u[1]+o[1])!=u))

t0=time.time()
G8=(frozenset({OFF[o] for o in ('W','SW','S','SE')}),frozenset())
recur={}; seen={G8}; q=[G8]
while q:
    f,r=q.pop(); fcl=fc(f,r); leafT=[]; cutT=[]
    for mask in range(1<<len(fcl)):
        S=[fcl[i] for i in range(len(fcl)) if mask>>i&1]; occ=set(r)|set(S)
        if not occ: continue
        cm=cluster(occ)
        if len(cm)==1: leafT.append(red(f,r,S,cm[0]))
        else: cutT.append(tuple(red(f,r,S,c) for c in cm))
    recur[(f,r)]=(leafT,cutT)
    for Tp in leafT+[p for pc in cutT for p in pc]:
        if Tp not in seen: seen.add(Tp); q.append(Tp)
types=list(recur); idx={T:i for i,T in enumerate(types)}
G8i=idx[G8]; NT=len(types)
leaf=[[idx[Tp] for Tp in recur[T][0]] for T in types]
cut =[[tuple(idx[p] for p in pc) for pc in recur[T][1]] for T in types]
print(f"R={R}: {NT} types, closure {time.time()-t0:.1f}s")

def bounded(x, iters=3000, cap=1e9):
    v=[x]*NT
    for _ in range(iters):
        nv=[0.0]*NT
        for i in range(NT):
            s=x
            li=leaf[i]
            if li:
                acc=0.0
                for j in li: acc+=v[j]
                s+=x*acc
            for pc in cut[i]:
                t=x
                for p in pc: t*=v[p]
                s+=t
            nv[i]=s
        if nv[G8i]>cap: return False
        if abs(nv[G8i]-v[G8i])<1e-12*nv[G8i]: return True
        v=nv
    return True

lo,hi=1/13.0,1/6.0
for _ in range(45):
    m=0.5*(lo+hi)
    if bounded(m): lo=m
    else: hi=m
lam=1/(0.5*(lo+hi))
print(f"king upper bound  lambda <= {lam:.4f}   (< 12.2 crude? {lam<12.2})   total {time.time()-t0:.1f}s")
