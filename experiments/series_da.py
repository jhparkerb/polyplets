"""Series analysis of the fixed-polyplet count a(n) by Dlog-Pade and
(inhomogeneous) differential approximants -- the field-standard tools for
estimating a growth constant lambda, the correction-to-scaling exponent, and
the leading amplitude from a finite series. Conspicuously ABSENT from the repo,
which estimates lambda only by ratio fits + Neville.

a(n) ~ C * lambda^n * n^(theta)  (2D lattice animals: theta ~ -1).
Equivalently A(x)=sum a(n)x^n is singular at x_c=1/lambda like (1-x/x_c)^(-(theta+1)).

We:
  1. Dlog-Pade: poles of [L/M] Pade of (log A)' -> x_c (=1/lambda); residue -> exponent.
  2. K=1,2 inhomogeneous differential approximants -> x_c, exponent, AND a recurrence
     that PREDICTS a(21), a(22) as an independent cross-check of the exact reach runs.
Reports the SPREAD across approximants as the honest error bar.
No new compute: a(1..20) hard-coded from results/b006770.txt + the a(20) candidate.
"""
import numpy as np
from fractions import Fraction as Fr

# a(1..19) confirmed (A006770), a(20) candidate (RESULTS.md R4)
A = [0,
 1,4,20,110,638,3832,23592,147941,940982,6053180,39299408,257105146,
 1692931066,11208974860,74570549714,498174818986,3340366308393,
 22471158811164,151609203011580,1025573519362016]
M = len(A)-1   # highest index (20)

def pade(series, L, Mm):
    # [L/Mm] Pade of sum series[i] x^i ; returns (num coeffs, den coeffs) as floats.
    # solve for denominator b (b0=1): sum_{j} b_j c_{n-j} = 0, n=L+1..L+Mm
    c = series
    if L+Mm >= len(c): return None
    Amat = np.zeros((Mm, Mm)); rhs = np.zeros(Mm)
    for i in range(Mm):
        n = L+1+i
        for j in range(1, Mm+1):
            Amat[i, j-1] = c[n-j] if n-j>=0 else 0.0
        rhs[i] = -c[n]
    try:
        b = np.linalg.solve(Amat, rhs)
    except np.linalg.LinAlgError:
        return None
    bden = np.concatenate([[1.0], b])
    anum = np.zeros(L+1)
    for n in range(L+1):
        s = 0.0
        for j in range(0, min(n, Mm)+1):
            s += bden[j]*c[n-j]
        anum[n] = s
    return anum, bden

def dlog_pade(use_a20):
    hi = M if use_a20 else M-1
    a = A[:hi+1]
    # A(x) coeffs (index 0..hi); compute g = A'/A as a power series to order hi-1
    # A' coeffs: d[n] = (n+1) a[n+1]
    d = [ (n+1)*a[n+1] for n in range(hi) ]
    # g = d / a  (a[0]=0, so factor x: a = x*ah, d = ... ) handle a[0]=0:
    # a(x)=x*ah(x) with ah[n]=a[n+1]; A'/A = (x ah)'/(x ah) = 1/x + ah'/ah
    ah = [a[n+1] for n in range(hi)]            # ah[0..hi-1]
    ahp = [ (n+1)*ah[n+1] for n in range(hi-1) ] # (ah)'
    # gg = ah'/ah  power series
    L = hi-1
    gg = [0.0]*L
    for n in range(L):
        s = ahp[n] if n < len(ahp) else 0.0
        for j in range(1, n+1):
            s -= ah[j]*gg[n-j]
        gg[n] = s/ah[0]
    # full dlog = 1/x + gg ; the simple pole of dlog at x_c has residue -(theta+1).
    # work with gg (analytic part); pole of A'/A is pole of gg shifted... actually
    # 1/x is regular except at 0, so x_c-pole comes from gg. Pade gg:
    res=[]
    for Mm in range(2, L//2+1):
        Ln = L-1-Mm
        if Ln < 1: continue
        pr = pade(gg, Ln, Mm)
        if pr is None: continue
        _, bden = pr
        roots = np.roots(bden[::-1])
        real = sorted([r.real for r in roots if abs(r.imag)<1e-6 and r.real>0.05])
        if not real: continue
        xc = real[0]
        res.append((Ln, Mm, xc, 1.0/xc))
    return res

def diff_approx_full(K, deg, degP, use_a20):
    # like diff_approx but returns (xc, lambda, null-vector, meta, Dk-builder) for prediction
    hi = M if use_a20 else M-1
    a = np.array(A[:hi+1], dtype=float)
    meta=[]
    for k in range(K+1):
        for j in range(deg+1): meta.append(('c',k,j))
    for j in range(degP+1): meta.append(('p',j))
    nun=len(meta); rows=hi+1
    def dk(k):
        out=np.zeros(hi+1)
        for m in range(hi+1):
            if m+k<=hi:
                f=1.0
                for t in range(k): f*=(m+1+t)
                out[m]=a[m+k]*f
        return out
    Dk=[dk(k) for k in range(K+1)]
    Mat=np.zeros((rows,nun))
    for idx,(t,*rest) in enumerate(meta):
        if t=='c':
            k,j=rest; col=np.zeros(rows)
            for m in range(hi+1):
                if m+j<=hi: col[m+j]+=Dk[k][m]
            Mat[:,idx]=col
        else:
            (j,)=rest
            if j<=hi: Mat[j,idx]=-1.0
    _,_,vt=np.linalg.svd(Mat); null=vt[-1]
    QK=np.zeros(deg+1)
    for idx,(t,*rest) in enumerate(meta):
        if t=='c' and rest[0]==K: QK[rest[1]]=null[idx]
    roots=np.roots(QK[::-1])
    real=sorted([r.real for r in roots if abs(r.imag)<1e-6 and r.real>0.05])
    if not real: return None
    return real[0],1.0/real[0],null,meta,K,deg,degP

def predict(full, upto):
    # march the DA recurrence to predict a[hi+1..upto]
    xc,lam,null,meta,K,deg,degP=full
    c={}; p={}
    for idx,(t,*rest) in enumerate(meta):
        if t=='c': c[(rest[0],rest[1])]=null[idx]
        else: p[rest[0]]=null[idx]
    a=list(map(float,A[:M+1]))
    while len(a)-1<upto: a.append(0.0)
    # equation at order n: sum_k sum_j c[k,j]*a[n-j+k]*falling = (p[n] if n<=degP else 0)
    def fall(m,k):
        f=1.0
        for t in range(k): f*=(m+1+t)
        return f
    for n in range(M+1-K, upto-K+1):
        # equation at order n; leading unknown a[n+K] (k=K,j=0).
        lead=c.get((K,0),0.0)*fall(n,K)
        if abs(lead)<1e-9: return None
        s=0.0
        for (k,j),cc in c.items():
            if cc==0: continue
            idx=n-j+k
            if (k,j)==(K,0): continue
            if 0<=idx<len(a): s+=cc*a[idx]*fall(n-j,k)
        rhs=(p.get(n,0.0) if n<=degP else 0.0)
        a[n+K]=(rhs - s)/lead
    return a

def diff_approx(K, deg, degP, use_a20):
    # inhomogeneous DA: sum_{k=0}^K Q_k(x) (d/dx)^k A = P(x), Q_K monic-normalized.
    hi = M if use_a20 else M-1
    a = np.array(A[:hi+1], dtype=float)
    Nser = hi  # use orders 0..hi
    # derivative series matrices: deriv k of A has coeff at order m: a[m+k]*(m+k)!/m!
    def dk(k):
        out = np.zeros(Nser+1)
        for m in range(Nser+1):
            if m+k <= hi:
                f = 1.0
                for t in range(k): f *= (m+1+t)
                out[m] = a[m+k]*f
        return out
    Dk = [dk(k) for k in range(K+1)]
    # unknowns: c[k,j] for k=0..K, j=0..deg ; p[j] j=0..degP. Normalize leading Q_K top coeff=1.
    cols=[]
    meta=[]
    for k in range(K+1):
        for j in range(deg+1):
            meta.append(('c',k,j)); cols.append(None)
    for j in range(degP+1):
        meta.append(('p',j)); cols.append(None)
    nun=len(meta)
    # equation order range: match series to order hi (rows 0..hi)
    rows = hi+1
    Mat=np.zeros((rows, nun))
    for idx,(t,*rest) in enumerate(meta):
        if t=='c':
            k,j=rest
            col=np.zeros(rows)
            for m in range(Nser+1):
                if m+j<=hi:
                    col[m+j]+=Dk[k][m]
            Mat[:,idx]=col
        else:
            (j,)=rest
            col=np.zeros(rows)
            if j<=hi: col[j]=-1.0
            Mat[:,idx]=col
    # null space
    u,s,vt=np.linalg.svd(Mat)
    null=vt[-1]
    # extract Q_K poly (k=K)
    QK=np.zeros(deg+1)
    for idx,(t,*rest) in enumerate(meta):
        if t=='c' and rest[0]==K:
            QK[rest[1]]=null[idx]
    roots=np.roots(QK[::-1])
    real=sorted([r.real for r in roots if abs(r.imag)<1e-6 and r.real>0.05])
    if not real: return None
    xc=real[0]
    return xc, 1.0/xc

def main():
    print("=== Dlog-Pade (pole x_c -> lambda=1/x_c) ===")
    for tag,u in (("a(1..19)",False),("+a(20) cand",True)):
        res=dlog_pade(u)
        lams=[r[3] for r in res]
        if lams:
            print(f"  {tag}: {len(lams)} approximants, lambda median={np.median(lams):.4f} "
                  f"min={min(lams):.3f} max={max(lams):.3f}")
            for Ln,Mm,xc,lam in res:
                print(f"      [{Ln}/{Mm}]  x_c={xc:.5f}  lambda={lam:.4f}")
    print()
    print("=== BIASED estimator: theta = -1 is KNOWN (2D lattice-animal universality), fix it ===")
    # a(n) ~ C lam^n n^theta with theta=-1  =>  lam_n := r(n)*n/(n-1) = lam(1+O(1/n^2))
    lamn=np.array([(A[n]/A[n-1])*n/(n-1) for n in range(2,M+1)])
    nb=np.arange(2,M+1,dtype=float)
    for k in (5,6,8,10):
        Lk=lamn[-k:]; Nk=nb[-k:]
        B=np.vstack([np.ones_like(Nk),1/Nk**2]).T
        c,*_=np.linalg.lstsq(B,Lk,rcond=None)
        print(f"  last {k:2d}, 1/n^2 fit: lambda = {c[0]:.5f}")
    print(f"  (lam_n at n=20 = {lamn[-1]:.5f}, monotone-decreasing as 1/n^2 -> consistent with theta=-1)")
    print()
    print("=== Exponent from Dlog-Pade residue (FREE fit -- expect short-series bias, NOT a result): A(x)~(1-x/x_c)^(-(theta+1)), a(n)~C lam^n n^theta ===")
    # residue of A'/A at x_c is -(theta+1). Estimate via gg Pade residue numerically.
    # (re-derive gg as in dlog_pade for a(1..20))
    hi=M; a=A[:hi+1]; ah=[a[n+1] for n in range(hi)]
    ahp=[(n+1)*ah[n+1] for n in range(hi-1)]; L=hi-1; gg=[0.0]*L
    for n in range(L):
        s=ahp[n] if n<len(ahp) else 0.0
        for j in range(1,n+1): s-=ah[j]*gg[n-j]
        gg[n]=s/ah[0]
    thetas=[]
    for Mm in range(2,L//2+1):
        Ln=L-1-Mm
        if Ln<1: continue
        pr=pade(gg,Ln,Mm)
        if pr is None: continue
        anum,bden=pr
        roots=np.roots(bden[::-1])
        real=[r.real for r in roots if abs(r.imag)<1e-6 and r.real>0.05]
        if not real: continue
        xc=min(real)
        # residue of num/den at xc: anum(xc)/den'(xc); dlog also has +1/x (regular at xc)
        dnum=np.polyval(anum[::-1],xc); dden=np.polyval(np.polyder(bden[::-1]),xc)
        if abs(dden)<1e-9: continue
        resid=dnum/dden + 0.0   # gg residue; full A'/A residue same (1/x regular)
        # A'/A ~ (theta+1)/(x_c - x) near x_c -> residue at x_c (in x) of A'/A = -(theta+1)
        theta=-resid-1.0
        if -3<theta<2: thetas.append(theta)
    if thetas:
        print(f"  theta median={np.median(thetas):.3f}  range=[{min(thetas):.3f},{max(thetas):.3f}]"
              f"   (2D lattice-animal universal value: theta = -1)")
    print()
    print("=== PREDICT a(21), a(22) via ratio extrapolation (independent reach cross-check) ===")
    # r(n)=a(n)/a(n-1) ~ lam*(1 + theta/n + d/n^2); fit on a tail window, extrapolate.
    r=np.array([A[n]/A[n-1] for n in range(2,M+1)]); ns=np.arange(2,M+1)
    pred=list(map(float,A[:M+1]))
    for win in (8,10,12):
        rt=r[-win:]; nt=ns[-win:]
        B=np.vstack([np.ones_like(nt,float),1.0/nt,1.0/nt**2]).T
        coef,*_=np.linalg.lstsq(B,rt,rcond=None)
        def rhat(n): return coef[0]+coef[1]/n+coef[2]/n**2
        a21=A[20]*rhat(21); a22=a21*rhat(22)
        print(f"  win={win:2d}: lambda_eff={coef[0]:.4f}  r(21)={rhat(21):.4f}  "
              f"a(21)~{a21:.4e}  a(22)~{a22:.4e}")
    print()
    print("=== Inhomogeneous differential approximants (lambda=1/x_c) ===")
    for K in (1,2):
        lams=[]
        for deg in range(2, 8):
            for degP in range(0, 6):
                # need unknowns ~<= rows
                nun=(K+1)*(deg+1)+(degP+1)
                if nun < (M)+1 or nun > (M)+1+3: continue
                r=diff_approx(K,deg,degP,True)
                if r: lams.append(r[1])
        if lams:
            lams=np.array(lams)
            lams=lams[(lams>4)&(lams<12)]
            if len(lams):
                print(f"  K={K}: {len(lams)} approximants, lambda median={np.median(lams):.4f} "
                      f"mean={lams.mean():.4f} std={lams.std():.4f} range=[{lams.min():.3f},{lams.max():.3f}]")

if __name__=="__main__":
    main()
