#!/usr/bin/env python3
"""Component-count stratification of polyplets: C(n,c) = # fixed polyplets of n
cells whose EDGE-connected (rook) components number exactly c. The pieces are
polyominoes joined only at corners. Built-in checks:
  sum_c C(n,c) = A006770 (all polyplets)
  C(n,1)       = A001168 (fixed polyominoes -- single edge-component)
"""
import sys
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 9
KING = [(dx, dy) for dx in (-1,0,1) for dy in (-1,0,1) if (dx,dy) != (0,0)]
ROOK = [(1,0),(-1,0),(0,1),(0,-1)]
A006770 = [1,4,20,110,638,3832,23592,147941,940982,6053180]
A001168 = [1,2,6,19,63,216,760,2725,9910,36446]

def norm(cells):
    mx = min(x for x,y in cells); my = min(y for x,y in cells)
    return frozenset((x-mx, y-my) for x,y in cells)

def edge_components(cells):
    cs = set(cells); seen = set(); comp = 0
    for c in cs:
        if c in seen: continue
        comp += 1; stack=[c]; seen.add(c)
        while stack:
            x,y = stack.pop()
            for dx,dy in ROOK:
                p=(x+dx,y+dy)
                if p in cs and p not in seen: seen.add(p); stack.append(p)
    return comp

from collections import Counter
level = {norm([(0,0)])}
allc=[]; strat=[]
for n in range(1, NMAX+1):
    allc.append(len(level))
    strat.append(Counter(edge_components(a) for a in level))
    if n < NMAX:
        nxt=set()
        for a in level:
            occ=set(a); cand=set()
            for x,y in a:
                for dx,dy in KING:
                    p=(x+dx,y+dy)
                    if p not in occ: cand.add(p)
            for p in cand: nxt.add(norm(occ|{p}))
        level=nxt

maxc = max(max(s) for s in strat)
print("n | total  A006770 ok | C(n,1)  A001168 ok | " + " ".join(f"c={c}" for c in range(1,maxc+1)))
for i in range(NMAX):
    s=strat[i]; tot=allc[i]
    okall = "OK" if i<len(A006770) and A006770[i]==tot else "??"
    c1 = s.get(1,0)
    ok1 = "OK" if i<len(A001168) and A001168[i]==c1 else "??"
    dist=" ".join(f"{s.get(c,0):>7}" for c in range(1,maxc+1))
    print(f"{i+1:2d}| {tot:>7} {okall} | {c1:>7} {ok1} | {dist}")
