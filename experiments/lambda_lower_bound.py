#!/usr/bin/env python3
"""Rigorous lower bound on the king-lattice growth constant lambda via the Rands-Welsh /
concatenation argument (Jensen's method for square: tau >= 3.903 from the series).
A*(u)=sum a(n) u^{n-1} = 1/(1-P(u)); P(u_c)=1 at u_c=1/lambda. With p_n=[u^n]P >= 0 (renewal),
truncating P at order N gives P_N(u) <= P(u), so the positive root u* of P_N(u)=1 satisfies
u* >= u_c, hence lambda >= 1/u* (and improves monotonically with N)."""
from fractions import Fraction as F
A = [1,4,20,110,638,3832,23592,147941,940982,6053180,39299408,257105146,
     1692931066,11208974860,74570549714,498174818986,3340366308393,
     22471158811164,151609203011580,1025573519362016]   # a(1..20); a(20) candidate

def rw(a):
    N=len(a); c=[F(x) for x in a]; d=[F(0)]*N; d[0]=F(1)/c[0]
    for n in range(1,N): d[n]=-sum(c[k]*d[n-k] for k in range(1,n+1))/c[0]
    p=[F(0)]*N
    for n in range(1,N): p[n]=-d[n]
    allpos=all(p[n]>=0 for n in range(1,N))
    pf=[float(x) for x in p]
    def Pv(u):
        s=0.0; uu=1.0
        for n in range(1,N): uu*=u; s+=pf[n]*uu
        return s
    lo,hi=0.0,0.25
    for _ in range(100):
        m=(lo+hi)/2
        if Pv(m)<1: lo=m
        else: hi=m
    u=(lo+hi)/2
    return allpos,u,1/u

for k in (15,17,19,20):
    ap,u,lam=rw(A[:k])
    tag="confirmed" if k<=19 else "with a(20) candidate"
    print(f"n<={k:2d} [{tag:18s}]: p_n>=0={ap}  u*={u:.6f}  lambda >= {lam:.5f}")
print(f"\nraw Fekete bound a(20)^(1/20) = {A[19]**(1/20):.5f}  (weakest); strip lambda_10 = 5.992")
print("series ESTIMATE (not a bound): lambda ~ 7.12-7.155")
