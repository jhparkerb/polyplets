#!/usr/bin/env python3
"""Ground-truth enumerator for the king upper-bound derivation. Brute-force all
fixed polyplets, and count marked-cell "types" N(n) = #(P, c) where P is an
n-cell polyplet, c a cell of P, and c's local neighbourhood matches a pattern
(some offsets FORBIDDEN = must be empty, some REQUIRED = must be occupied).

Everything downstream (the convolution recurrences, the certificate bound) gets
checked against these exact counts, so no hand-tracking error survives.
"""
import sys
from collections import defaultdict

KING = [(dx,dy) for dx in(-1,0,1) for dy in(-1,0,1) if (dx,dy)!=(0,0)]
# named king offsets (x right, y up)
OFF = {'E':(1,0),'W':(-1,0),'N':(0,1),'S':(0,-1),
       'NE':(1,1),'NW':(-1,1),'SE':(1,-1),'SW':(-1,-1)}

def norm(cells):
    mx=min(x for x,y in cells); my=min(y for x,y in cells)
    return frozenset((x-mx,y-my) for x,y in cells)

def all_polyplets(nmax):
    """fixed (translation-class) king-connected animals, by size, 1..nmax."""
    levels={1:{norm([(0,0)])}}
    for n in range(2,nmax+1):
        nxt=set()
        for a in levels[n-1]:
            occ=set(a); cand=set()
            for x,y in a:
                for dx,dy in KING:
                    p=(x+dx,y+dy)
                    if p not in occ: cand.add(p)
            for p in cand: nxt.add(norm(occ|{p}))
        levels[n]=nxt
    return levels

def type_count(levels, forbid=(), require=(), nmax=None):
    """N(n) for the type: c a cell with all `forbid` offsets empty and all
    `require` offsets occupied (offsets given as names or (dx,dy))."""
    F=[OFF[o] if isinstance(o,str) else o for o in forbid]
    R=[OFF[o] if isinstance(o,str) else o for o in require]
    out={}
    for n,polys in levels.items():
        if nmax and n>nmax: continue
        cnt=0
        for P in polys:
            cells=set(P)
            for (cx,cy) in cells:
                ok=all((cx+dx,cy+dy) not in cells for dx,dy in F) and \
                   all((cx+dx,cy+dy) in cells for dx,dy in R)
                if ok: cnt+=1
        out[n]=cnt
    return out

if __name__=="__main__":
    NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 9
    lv=all_polyplets(NMAX)
    A={n:len(lv[n]) for n in lv}
    print("n :  A(n)=#polyplets (must match A006770: 1,4,20,110,638,3832,23592,147941,940982)")
    print("    ", [A[n] for n in sorted(A)])
    # base fact: G8 = corner type, forbidden {W,SW,S,SE}
    G8=type_count(lv,forbid=('W','SW','S','SE'))
    print("\nG8(n) = #(P,c) with c's W,SW,S,SE empty  (the marked-corner type):")
    print("  n :", list(range(1,NMAX+1)))
    print("  A :", [A[n] for n in range(1,NMAX+1)])
    print("  G8:", [G8[n] for n in range(1,NMAX+1)])
    print("  base fact A(n) <= G8(n) <= n*A(n):",
          all(A[n]<=G8[n]<=n*A[n] for n in range(1,NMAX+1)))
    # growth check: G8 ratio should approach lambda ~7.11 like A
    print("  A ratios :", [round(A[n]/A[n-1],3) for n in range(2,NMAX+1)])
    print("  G8 ratios:", [round(G8[n]/G8[n-1],3) for n in range(2,NMAX+1)])
