#!/usr/bin/env python3
"""s06: prove s02's tentative N_h(+-1) halving identities from the PROVEN
closed form F(x,y) = -(M + 2x^2y^2(1+x+y)^2 sqrt(Delta))/(2K Delta^2),
K = x+y+xy, Delta = (1-x-y)^2-4xy  (docs/proofs/convex-box-kernel.md).

Steps (all exact, Fraction arithmetic):
 A. M(-1,y) exact polynomial; F(-1,y) as element of Q(y)[s], s=sqrt(4+y^2).
    Phi(y) := sum_h N_h(-1) y^h = (1/2) F(-1,4y)  [since N_h(-1)=2^(2h-1)R_h(-1)].
    Cross-check coefficients of Phi vs banked N_h(-1) (out_s02_rowgf.txt), h<=18.
 B. x->1 limit: M(1-e, Y e^2) == -2Y e^5 (mod e^6)  [exact expansion] which forces
    G(Y) := sum_h N_h(1) Y^h = Y/(1-4Y)^2 - 4Y^2 (1-4Y)^(-3/2).
    Verify limit F(1-e,Ye^2)/e -> G(Y) by exact truncated series in (Y,e), and
    cross-check G's coefficients vs banked N_h(1) and vs A153337 closed form
    c_h = h 4^(h-1) - 2(h-1) C(2h-2,h-1).
 C. Even/odd split of Phi (exact rational-function identities in Q(y)[s]):
    even(Phi) = -4 G(-y^2)   <=>  N_{2k}(-1) = (-1)^(k+1) 4 N_k(1), k>=1
    odd(Phi)  = y(1-4y^2)/(1+4y^2)^2 - 2y
              <=>  N_{2k+1}(-1) = (-1)^k (2k+1) 4^k, k>=1;  N_1(-1) = -1 boundary.
"""
from fractions import Fraction as Fr
import re, sys

NY = 44  # truncation order in y / Y

# ---------- truncated power series over Fraction: list of coeffs ----------
def padd(a, b):
    n = max(len(a), len(b)); r = [Fr(0)]*n
    for i,c in enumerate(a): r[i] += c
    for i,c in enumerate(b): r[i] += c
    return r
def pscale(a, c): return [c*x for x in a]
def pmul(a, b, N=NY+1):
    r = [Fr(0)]*min(N, len(a)+len(b)-1)
    for i,ai in enumerate(a):
        if ai == 0: continue
        for j,bj in enumerate(b):
            if i+j >= len(r): break
            r[i+j] += ai*bj
    return r
def pinv(a, N=NY+1):
    assert a[0] != 0
    r = [Fr(1)/a[0]] + [Fr(0)]*(N-1)
    for n in range(1, N):
        s = Fr(0)
        for k in range(1, min(n, len(a)-1)+1):
            s += a[k]*r[n-k]
        r[n] = -s/a[0]
    return r
def psqrt(a, N=NY+1):
    assert a[0] == 1
    r = [Fr(1)] + [Fr(0)]*(N-1)
    for n in range(1, N):
        s = Fr(0)
        for k in range(1, n):
            s += r[k]*r[n-k]
        an = a[n] if n < len(a) else Fr(0)
        r[n] = (an - s)/2
    return r

# ---------- the banked M polynomial (out_s02_KM.txt), as {(i,j):c} ----------
M_TERMS = {(1,2):-2,(2,1):-2,(1,3):6,(2,2):8,(3,1):6,(1,4):-6,(2,3):-8,(3,2):-8,
           (4,1):-6,(1,5):2,(3,3):6,(5,1):2,(2,5):2,(3,4):2,(4,3):2,(5,2):2,
           (3,5):2,(4,4):-4,(5,3):2}

def M_at_x(xval, N=NY+1):
    """M(xval, y) as y-poly, xval a Fraction."""
    r = [Fr(0)]*N
    for (i,j),c in M_TERMS.items():
        if j < N: r[j] += Fr(c) * xval**i
    return r

# sanity: M(t,t) must be -4t^3+20t^4-28t^5+10t^6+8t^7 (banked)
Mtt = {}
for (i,j),c in M_TERMS.items(): Mtt[i+j] = Mtt.get(i+j,0)+c
Mtt = {k:v for k,v in Mtt.items() if v != 0}
assert Mtt == {3:-4,4:20,5:-28,6:10,7:8}, Mtt
print("sanity: M(t,t) matches banked {3:-4,4:20,5:-28,6:10,7:8}")

# ---------- Part A: F(-1,y) ----------
Mm1 = M_at_x(Fr(-1))
print("A. M(-1,y) coeffs y^1..y^5:", [int(c) for c in Mm1[1:6]])
assert Mm1[1:6] == [Fr(-16),Fr(16),Fr(-20),Fr(0),Fr(-2)] and all(c==0 for c in Mm1[6:])
# F(-1,y) = (M(-1,y) + 2 y^4 sqrt(4+y^2)) / (2 (4+y^2)^2)   [K=-1, (1+x+y)^2=y^2, x^2=1]
# as series: sqrt(4+y^2) = 2*sqrt(1+y^2/4)
s4 = pscale(psqrt([Fr(1),Fr(0),Fr(1,4)]), Fr(2))          # sqrt(4+y^2)
den = pinv(pmul([Fr(4),Fr(0),Fr(1)],[Fr(4),Fr(0),Fr(1)])) # 1/(4+y^2)^2
y4 = [Fr(0)]*4+[Fr(1)]
Fm1 = pmul(padd(Mm1, pscale(pmul(y4, s4), Fr(2))), pscale(den, Fr(1,2)))
# Phi(y) = sum N_h(-1) y^h = (1/2) F(-1, 4y)
Phi = [Fr(1,2)*c*Fr(4)**h for h,c in enumerate(Fm1)]
print("A. Phi coeffs h=1..10 (should be N_h(-1)):", [int(c) for c in Phi[1:11]])

# banked N_h from out_s02_rowgf.txt
Ntab = {}
for line in open('out_s02_rowgf.txt'):
    m = re.match(r'\s*N_(\d+)\(x\) = \[(.*)\]', line)
    if m:
        Ntab[int(m.group(1))] = [int(t) for t in m.group(2).split(',')]
Nm1 = {h: sum(c*(-1)**k for k,c in enumerate(p)) for h,p in Ntab.items()}
N1  = {h: sum(p) for h,p in Ntab.items()}
okA = all(Phi[h] == Nm1[h] for h in Ntab)
print("A. Phi[h] == banked N_h(-1) for h in", sorted(Ntab), ":", okA)
assert okA

# closed form of Phi as exact rational + sqrt part (paper derivation):
# Phi = (-y+4y^2-20y^3-32y^5)/(1+4y^2)^2 + 16 y^4 sqrt(1+4y^2)/(1+4y^2)^2
s14 = psqrt([Fr(1),Fr(0),Fr(4)])                          # sqrt(1+4y^2)
d14 = pinv(pmul([Fr(1),Fr(0),Fr(4)],[Fr(1),Fr(0),Fr(4)])) # 1/(1+4y^2)^2
ratA = pmul([Fr(0),Fr(-1),Fr(4),Fr(-20),Fr(0),Fr(-32)], d14)
sqrA = pmul(pscale(pmul(y4, s14), Fr(16)), d14)
PhiCF = padd(ratA, sqrA)
okA2 = all(PhiCF[h] == Phi[h] for h in range(NY+1))
print("A. closed form Phi == series Phi to y^%d:" % NY, okA2)
assert okA2

# ---------- Part B: x->1 limit, exact ----------
# M(1-e, Y e^2) mod e^6: expand exactly (polynomial identity in Y).
# term c * (1-e)^i * Y^j * e^(2j): only j<=2 contributes below e^6... j in 1..5
from math import comb
Ecoef = [ {} for _ in range(6) ]   # Ecoef[k][j] = coeff of e^k Y^j
for (i,j),c in M_TERMS.items():
    for a in range(0, 6-2*j+1):
        if 2*j+a > 5: break
        Ecoef[2*j+a][j] = Ecoef[2*j+a].get(j,Fr(0)) + Fr(c)*Fr((-1)**a*comb(i,a))
low = {k:v for k,v in enumerate(Ecoef) if any(x!=0 for x in v.values())}
print("B. M(1-e,Ye^2) nonzero e-orders <=5:", {k:{j:int(x) for j,x in v.items() if x!=0} for k,v in low.items()})
assert all(all(x==0 for x in Ecoef[k].values()) for k in range(5)), "e^0..e^4 must vanish"
assert {j:x for j,x in Ecoef[5].items() if x!=0} == {1: Fr(-2)}, Ecoef[5]
print("B. PROVEN: M(1-e,Ye^2) == -2Y e^5 (mod e^6)  -- exactly the m5(Y)=-2Y the limit needs")

# Full limit check by exact bivariate truncated series: F(1-e,Ye^2)/e as series
# in e (order <=3) with Y-series coefficients; e^0 term must equal G(Y).
NE = 4
def bpadd(A,B): return [padd(a,b) for a,b in zip(A,B)]
def bpmul(A,B):
    R = [[Fr(0)]*(NY+1) for _ in range(NE)]
    for i,a in enumerate(A):
        if all(c==0 for c in a): continue
        for j,b in enumerate(B):
            if i+j >= NE: break
            m = pmul(a,b)
            R[i+j] = padd(R[i+j], m)
    return R
def bpinv(A):
    a0 = A[0]; a0inv = pinv(a0)
    R = [[Fr(0)]*(NY+1) for _ in range(NE)]
    R[0] = a0inv
    for n in range(1,NE):
        s = [Fr(0)]*(NY+1)
        for k in range(1,n+1):
            s = padd(s, pmul(A[k] if k < len(A) else [Fr(0)], R[n-k]))
        R[n] = pmul(pscale(s,Fr(-1)), a0inv)
    return R
def bpsqrt(A):
    # A[0] must have sqrt as series; Newton on e-order
    R = [[Fr(0)]*(NY+1) for _ in range(NE)]
    R[0] = psqrt(A[0]) if A[0][0]==1 else None
    assert R[0] is not None
    half = pscale(pinv(R[0]), Fr(1,2))
    for n in range(1,NE):
        s = [Fr(0)]*(NY+1)
        for k in range(1,n):
            s = padd(s, pmul(R[k],R[n-k]))
        an = A[n] if n < len(A) else [Fr(0)]
        R[n] = pmul(padd(an, pscale(s,Fr(-1))), half)
    return R
Ypoly = lambda *cs: list(map(Fr,cs))
ZERO = [Fr(0)]*(NY+1)
# building blocks as [e^0, e^1, ...] with Y-series entries
one  = [Ypoly(1), ZERO, ZERO, ZERO]
x_   = [Ypoly(1), Ypoly(-1), ZERO, ZERO]                    # 1-e
y_   = [ZERO, ZERO, Ypoly(0,1), ZERO]                       # Y e^2
# W = (1-4Y) + 2Y e + Y^2 e^2 ; Delta = e^2 W ; sqrt(Delta) = e sqrt(W)
W    = [Ypoly(1,-4), Ypoly(0,2), Ypoly(0,0,1), ZERO]
sqW  = bpsqrt(W)
K_   = bpadd(bpadd(x_,y_), bpmul(x_,y_))
# M(1-e, Ye^2): compute exactly to e^3+5? We need F/e to e^0 only, but carry NE=4:
# M/e^5 needs M to e^(5+3). Instead: use M = e^5 * Mq with Mq from exact expansion.
# Expand M fully in e up to e^8 with Y-polys (exact, 19 terms):
NE2 = 9
Mfull = [ [Fr(0)]*(NY+1) for _ in range(NE2) ]
for (i,j),c in M_TERMS.items():
    # c (1-e)^i Y^j e^{2j}
    for a in range(0, NE2-2*j):
        if 2*j+a >= NE2: break
        if 2*j+a < len(Mfull) and j <= NY:
            Mfull[2*j+a][j] += Fr(c)*Fr((-1)**a*comb(i,a))
assert all(all(c==0 for c in Mfull[k]) for k in range(5))
Mq = Mfull[5:9]  # M / e^5, e-order 0..3
# term2/e^5 = 2 (1-e)^2 Y^2 (2-e+Ye^2)^2 sqrt(W)
two_ = [Ypoly(2), Ypoly(-1), Ypoly(0,1), ZERO]
t2 = bpmul(bpmul([Ypoly(0,0,2), ZERO, ZERO, ZERO], bpmul(x_,x_)), bpmul(bpmul(two_,two_), sqW))
num = bpadd(Mq, t2)
Fdive = bpmul(num, bpmul(bpinv(bpmul([pscale(K_[0],2),pscale(K_[1],2),pscale(K_[2],2),pscale(K_[3],2)], bpmul(W,W))), [pscale(Ypoly(1),Fr(-1)),ZERO,ZERO,ZERO]))
G_series = Fdive[0]
# target G(Y) = Y/(1-4Y)^2 - 4Y^2 (1-4Y)^(-3/2)
inv14 = pinv([Fr(1),Fr(-4)])
Gt = padd(pmul([Fr(0),Fr(1)], pmul(inv14,inv14)),
          pscale(pmul([Fr(0),Fr(0),Fr(1)], pmul(inv14, pinv(psqrt([Fr(1),Fr(-4)])))), Fr(-4)))
okB = G_series[:NY] == Gt[:NY]
print("B. lim_{e->0} F(1-e,Ye^2)/e == Y/(1-4Y)^2 - 4Y^2(1-4Y)^(-3/2) to Y^%d:" % (NY-1), okB)
assert okB
okB2 = all(Gt[h] == N1[h] for h in Ntab)
print("B. G[h] == banked N_h(1) for h<=18:", okB2)
okB3 = all(Gt[h] == h*4**(h-1) - 2*(h-1)*comb(2*h-2,h-1) for h in range(1,NY))
print("B. G[h] == A153337 closed form h*4^(h-1)-2(h-1)C(2h-2,h-1), h<%d:" % NY, okB3)
assert okB2 and okB3

# ---------- Part C: even/odd identities (exact in Q(y)[s]) ----------
# rational part numerator A(y) = -y+4y^2-20y^3-32y^5 over D=(1+4y^2)^2.
# even: (A(y)+A(-y))/2 = 4y^2. Required: -4 * [rational part of G(-y^2)] = 4y^2/(1+4y^2)^2. Identical.
# sqrt: Phi_sqrt = 16y^4 s/(1+4y^2)^2 ; required -4*(-4Y^2(1-4Y)^{-3/2})|_{Y=-y^2}
#       = 16y^4 (1+4y^2)^{-3/2} = 16y^4 s/(1+4y^2)^2 since s^2 = 1+4y^2. Identical.
# odd: (A(y)-A(-y))/2 = -y-20y^3-32y^5 ; required y(1-4y^2) - 2y(1+4y^2)^2
oddreq = padd([Fr(0),Fr(1),Fr(0),Fr(-4)], pscale(pmul([Fr(0),Fr(2)], pmul([Fr(1),Fr(0),Fr(4)],[Fr(1),Fr(0),Fr(4)])), Fr(-1)))
print("C. odd-part numerator identity  -y-20y^3-32y^5 == y(1-4y^2)-2y(1+4y^2)^2:",
      oddreq[:6] == [Fr(0),Fr(-1),Fr(0),Fr(-20),Fr(0),Fr(-32)] and all(c==0 for c in oddreq[6:]))
# hence, coefficientwise for all k (given row polynomiality per h):
okC1 = all(Phi[2*k] == (-1)**(k+1)*4*Gt[k] for k in range(1, NY//2))
okC2 = all(Phi[2*k+1] == (-1)**k*(2*k+1)*4**k for k in range(1, (NY-1)//2))
print("C. N_{2k}(-1) = (-1)^(k+1) 4 N_k(1)  for k=1..%d:" % (NY//2-1), okC1)
print("C. N_{2k+1}(-1) = (-1)^k (2k+1) 4^k  for k=1..%d:" % ((NY-1)//2-1), okC2)
print("C. boundary: N_1(-1) =", int(Phi[1]), "(claim formula would give +1; k=0 is the sole exception)")
assert okC1 and okC2 and Phi[1] == -1
print("\nALL CHECKS PASS")
