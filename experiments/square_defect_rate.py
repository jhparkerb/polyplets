#!/usr/bin/env python3
"""Cross-lattice test of the reading "defect rate = (thin-diagonal growth)^2".

For polyplets a one-cell row is followed by a one-cell row in 3 ways, so
T(n,n) = 3^(n-1) and the measured below-onset defect rate is 9 = 3^2.
For square-lattice polyominoes a one-cell row admits only 1 continuation, so
T(n,n) = 1 and the same reading predicts defect rate 1 -- i.e. the square-lattice
diagonal law should fail below its onset only POLYNOMIALLY, not exponentially.

Data: results/bbox_square4_n21.txt, columns  n H W count.
"""
import os, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

T = {}
for line in open(os.path.join(ROOT,"results","bbox_square4_n21.txt")):
    p = line.split()
    if len(p)!=4: continue
    n,H,W,c = int(p[0]),int(p[1]),int(p[2]),int(p[3])
    T[(n,H)] = T.get((n,H),0)+c
NMAX = max(n for n,_ in T)
print("square4 bbox data to n=%d" % NMAX)
print("thin diagonal T(n,n):", [T.get((n,n),0) for n in range(1,9)])

def fitpoly(pts, deg):
    """exact interpolation through deg+1 points; returns coeffs or None"""
    if len(pts) < deg+1: return None
    use = pts[-(deg+1):]
    N = deg+1
    M = [[F(p[0])**i for i in range(N)] + [F(p[1])] for p in use]
    for c in range(N):
        piv = next((r for r in range(c,N) if M[r][c]!=0), None)
        if piv is None: return None
        M[c],M[piv]=M[piv],M[c]
        M[c]=[x/M[c][c] for x in M[c]]
        for r in range(N):
            if r!=c and M[r][c]!=0:
                f=M[r][c]; M[r]=[M[r][i]-f*M[c][i] for i in range(N+1)]
    return [M[i][N] for i in range(N)]

def ev(co,n):
    return sum(c*F(n)**i for i,c in enumerate(co))

print()
print("== is T_sq(n,n-k) a polynomial in n, and from where?")
print("  %3s %8s %28s" % ("k","deg","onset (first n where poly holds up)"))
laws={}
for k in range(0,7):
    pts = [(n, T[(n,n-k)]) for n in range(1,NMAX+1) if (n,n-k) in T and n-k>=1]
    if len(pts) < 4: continue
    found=None
    for deg in range(0,len(pts)-2):
        co = fitpoly(pts,deg)
        if co is None: continue
        # how far back does it hold?
        first = pts[-1][0]
        for n,v in reversed(pts):
            if ev(co,n)==v: first=n
            else: break
        # require it to reproduce at least 3 points beyond those used
        held = sum(1 for n,v in pts if ev(co,n)==v)
        if held >= deg+1+3:
            found=(deg,first,co); break
    if found:
        deg,first,co = found
        laws[k]=co
        print("  %3d %8d %28s   (2k+1 = %d)" % (k,deg,"n >= %d"%first, 2*k+1))
    else:
        print("  %3d %8s" % (k,"none in range"))

print()
print("== defect T - poly below the onset of each diagonal")
print("  %3s %3s %3s %14s %14s %10s" % ("k","n","H","T","poly","T-poly"))
for k in sorted(laws):
    co = laws[k]
    for n in range(k+1, 2*k+1):
        H=n-k
        if (n,H) not in T or H<1: continue
        d = F(T[(n,H)]) - ev(co,n)
        print("  %3d %3d %3d %14d %14s %10s" % (k,n,H,T[(n,H)],ev(co,n),d))
