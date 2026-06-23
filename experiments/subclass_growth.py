"""Growth constants & amplitude of polyplet SUBCLASSES, reusing the biased-DA
machine from series_da.py on different subsequences. Addresses brainstorm items:
  #2 lambda_0 (hole-free)      from results/holes_n18.txt k=0 column
  #4 lambda_k (k=1,2,3 holes)  from results/holes_n18.txt  -> test lambda_k = lambda
  #3 critical amplitude C in a(n) ~ C lambda^n n^theta  (theta=-1, lambda=7.1101)
  #11 symmetric-subclass growth ~ sqrt(lambda)  from results/symmetry_classes.txt
No new compute; pure analysis of saved counts.
"""
import numpy as np, re

LAM = 7.1101   # from experiments/series_da.py (DA + biased ratio agree)

A = [0,1,4,20,110,638,3832,23592,147941,940982,6053180,39299408,257105146,
 1692931066,11208974860,74570549714,498174818986,3340366308393,
 22471158811164,151609203011580,1025573519362016]

def load_holes():
    by = {}   # by[k][n] = count
    for line in open("results/holes_n18.txt"):
        p = line.split()
        if len(p)!=3: continue
        n,k,c = int(p[0]),int(p[1]),int(p[2])
        by.setdefault(k,{})[n]=c
    return by

def load_sym():
    cols=None; rows={}
    for line in open("results/symmetry_classes.txt"):
        if line.strip().startswith("n ") or re.match(r"\s*n\s+asymmetric",line):
            cols=line.split()
            continue
        m=re.match(r"\s*(\d+)\s+(.*)",line)
        if cols and m and m.group(1).isdigit():
            vals=line.split()
            try: rows[int(vals[0])]=[int(x) for x in vals[1:9]]
            except ValueError: pass
    # columns order: asymmetric mirror_ortho mirror_diag C2 C4 D2_ortho D2_diag D4
    return rows

def biased_lambda(seq_dict, label, theta=-1.0):
    # seq_dict: {n: count}; lam_n = r(n)*(n/(n-1))^(-theta) ; for theta=-1 -> r(n)*n/(n-1)...
    # general: a(n)~C lam^n n^theta => r(n)=lam (n/(n-1))^theta => lam_n=r(n)*(n/(n-1))^(-theta)
    ns=sorted(seq_dict)
    pairs=[(n,seq_dict[n]/seq_dict[n-1]) for n in ns if n-1 in seq_dict and seq_dict[n-1]>0]
    if len(pairs)<5:
        print(f"  {label}: too few terms ({len(pairs)})"); return None
    nn=np.array([p[0] for p in pairs],float); r=np.array([p[1] for p in pairs])
    lamn = r*(nn/(nn-1))**(-theta)
    # Richardson 1/n^2 on tail
    k=min(8,len(lamn))
    L=lamn[-k:]; N=nn[-k:]
    B=np.vstack([np.ones_like(N),1/N**2]).T
    c,*_=np.linalg.lstsq(B,L,rcond=None)
    print(f"  {label}: terms={len(pairs)} (n<= {int(nn[-1])})  r_last={r[-1]:.4f}  "
          f"lam_n_last={lamn[-1]:.4f}  -> lambda ~ {c[0]:.4f}")
    return c[0]

def dlog_pade_lambda(seq_dict,label):
    # build series from n=1.., pad index0=0, Dlog-Pade for the dominant singularity
    ns=sorted(seq_dict); hi=ns[-1]
    a=[0.0]*(hi+1)
    for n in ns: a[n]=float(seq_dict[n])
    if a[1]==0:
        return None
    ah=[a[n+1] for n in range(hi)]; ahp=[(n+1)*ah[n+1] for n in range(hi-1)]
    L=hi-1; gg=[0.0]*L
    for n in range(L):
        s=ahp[n] if n<len(ahp) else 0.0
        for j in range(1,n+1): s-=ah[j]*gg[n-j]
        gg[n]=s/ah[0]
    lams=[]
    for Mm in range(2,L//2+1):
        Ln=L-1-Mm
        if Ln<1: continue
        # Pade [Ln/Mm] of gg
        c=gg
        if Ln+Mm>=len(c): continue
        Amat=np.zeros((Mm,Mm)); rhs=np.zeros(Mm)
        for i in range(Mm):
            nidx=Ln+1+i
            for j in range(1,Mm+1): Amat[i,j-1]=c[nidx-j] if nidx-j>=0 else 0.0
            rhs[i]=-c[nidx]
        try: b=np.linalg.solve(Amat,rhs)
        except np.linalg.LinAlgError: continue
        roots=np.roots(np.concatenate([[1.0],b])[::-1])
        real=sorted([rt.real for rt in roots if abs(rt.imag)<1e-6 and rt.real>0.02])
        if real: lams.append(1.0/real[0])
    lams=[x for x in lams if 1<x<12]
    if lams:
        print(f"  {label}: Dlog-Pade lambda median={np.median(lams):.4f} "
              f"range=[{min(lams):.3f},{max(lams):.3f}] ({len(lams)} approx)")
        return np.median(lams)

def main():
    by=load_holes()
    print("=== #2 lambda_0  (hole-free, k=0) ===")
    a0=by[0]
    print(f"  A_0 series n=1..{max(a0)}: "+", ".join(str(a0[n]) for n in sorted(a0))[:90]+" ...")
    l0b=biased_lambda(a0,"hole-free biased(theta=-1)")
    l0p=dlog_pade_lambda(a0,"hole-free")
    if l0b: print(f"  -> lambda_0 ~ {l0b:.3f} ;  lambda_0/lambda = {l0b/LAM:.4f}  (vs noted ~0.977)")
    print()
    print("=== #4 lambda_k  (k=1,2,3 holes) -- test lambda_k = lambda ===")
    for k in (1,2,3):
        if k in by: biased_lambda(by[k],f"k={k} biased(theta=-1)")
    print(f"  (reference lambda = {LAM})")
    print()
    print("=== #3 critical amplitude C:  a(n) ~ C lambda^n n^theta, theta=-1 ===")
    print(f"  C_n = a(n)*n / lambda^n   (lambda={LAM})")
    Cs=[]
    for n in range(8,len(A)):
        Cn=A[n]*n/LAM**n; Cs.append(Cn)
        if n>=12: print(f"    n={n:2d}  C_n = {Cn:.5f}")
    # extrapolate C_n in 1/n
    ns=np.arange(8,len(A)); Cs=np.array(Cs)
    B=np.vstack([np.ones_like(ns,float),1/ns]).T
    c,*_=np.linalg.lstsq(B,Cs,rcond=None)
    print(f"  -> amplitude C ~ {c[0]:.4f}  (1/n extrapolation; sensitive to lambda)")
    print()
    print("=== #11 symmetric-subclass growth (expect ~ sqrt(lambda) = %.4f) ===" % (LAM**0.5))
    rows=load_sym()
    # columns: 0 asym 1 mirror_ortho 2 mirror_diag 3 C2 4 C4 5 D2o 6 D2d 7 D4
    for idx,name in [(1,"mirror_ortho"),(2,"mirror_diag"),(3,"C2")]:
        d={n:rows[n][idx] for n in rows if rows[n][idx]>0}
        biased_lambda(d,f"{name} biased(theta=-1)")
        dlog_pade_lambda(d,f"{name}")
    print(f"  sqrt(lambda) = {LAM**0.5:.4f}")

if __name__=="__main__":
    main()
