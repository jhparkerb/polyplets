"""Differential-approximant growth constants for OTHER lattices, reusing the
king-lattice DA/biased machine (experiments/series_da.py) on published series.
Item #9 (+3D bonus): validates the DA pipeline against lattices with known lambda,
and reports lambda for each.

Series from Mertens 1990 (J.Stat.Phys 58), Table I -- total clusters g_s:
  nnSquare = KING lattice = our a(n) (sanity: should give 7.11)
  triangular  (n=1..19)
  cubic / simple-cubic polycubes (n=1..15)
theta (2D lattice animals) = -1 universal; 3D animals theta = -3/2.
"""
import numpy as np

SERIES = {
 "king(nnSquare)": ([1,4,20,110,638,3832,23592,147941,940982,6053180,39299408,
   257105146,1692931066,11208974860], -1.0),
 "triangular": ([1,3,11,44,186,814,3652,16689,77359,362671,1716033,8182213,
   39267086,189492795,918837374,4474080844,21866153748,107217298977,527266673134], -1.0),
 "cubic(polycubes)": ([1,3,15,86,534,3481,23502,162913,1152870,8294738,60494549,
   446205905,3322769321,24946773111,188625900446], -1.5),
}

def biased(seq, theta):
    # a(n) ~ C lam^n n^theta  =>  lam_n = r(n)*(n/(n-1))^(-theta) = lam(1+O(1/n^2))
    a=[0]+list(seq); M=len(a)-1
    ns=[]; lam=[]
    for n in range(2,M+1):
        if a[n-1]==0: continue
        ns.append(n); lam.append((a[n]/a[n-1])*(n/(n-1))**(-theta))
    ns=np.array(ns,float); lam=np.array(lam)
    out={}
    for k in (5,6,8,10):
        if len(lam)<k: continue
        L=lam[-k:]; N=ns[-k:]
        B=np.vstack([np.ones_like(N),1/N**2]).T
        c,*_=np.linalg.lstsq(B,L,rcond=None)
        out[k]=c[0]
    return lam[-1], out

def dlog_pade(seq):
    a=[0.0]+[float(x) for x in seq]; hi=len(a)-1
    ah=[a[n+1] for n in range(hi)]; ahp=[(n+1)*ah[n+1] for n in range(hi-1)]
    L=hi-1; gg=[0.0]*L
    for n in range(L):
        s=ahp[n] if n<len(ahp) else 0.0
        for j in range(1,n+1): s-=ah[j]*gg[n-j]
        gg[n]=s/ah[0]
    lams=[]
    for Mm in range(2,L//2+1):
        Ln=L-1-Mm
        if Ln<1 or Ln+Mm>=len(gg): continue
        A=np.zeros((Mm,Mm)); rhs=np.zeros(Mm)
        for i in range(Mm):
            ni=Ln+1+i
            for j in range(1,Mm+1): A[i,j-1]=gg[ni-j] if ni-j>=0 else 0.0
            rhs[i]=-gg[ni]
        try: b=np.linalg.solve(A,rhs)
        except np.linalg.LinAlgError: continue
        roots=np.roots(np.concatenate([[1.0],b])[::-1])
        real=sorted([r.real for r in roots if abs(r.imag)<1e-6 and r.real>0.02])
        if real: lams.append(1.0/real[0])
    lams=[x for x in lams if 1<x<20]
    return (np.median(lams),min(lams),max(lams),len(lams)) if lams else None

KNOWN={"king(nnSquare)":7.11,"triangular":5.18,"cubic(polycubes)":8.34}
for name,(seq,theta) in SERIES.items():
    print(f"=== {name}  ({len(seq)} terms, theta={theta}) ===")
    last,bo=biased(seq,theta)
    print(f"  biased lam_n_last={last:.4f}  ->  " +
          "  ".join(f"k{k}:{v:.4f}" for k,v in bo.items()))
    dp=dlog_pade(seq)
    if dp: print(f"  Dlog-Pade lambda median={dp[0]:.4f} range=[{dp[1]:.3f},{dp[2]:.3f}] ({dp[3]} approx)")
    print(f"  literature lambda ~ {KNOWN.get(name,'?')}")
    print()
