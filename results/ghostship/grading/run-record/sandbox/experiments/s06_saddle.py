#!/usr/bin/env python3
"""s06: q->1- oscillation law for K(q) (king) and J(q) (control).

Saddle-point analysis of K(e^-eps) = sum (-1)^m (2-q^m) q^{T_m}/(q;q)_m^2:
with u = m*eps, exponent g(u)/eps, g(u) = -u^2/2 - 2 Li2(e^-u) + pi^2/3.
Poisson mode e^{i pi m}: saddle g'(u) = -i pi, i.e. u + 2 log(1-e^-u) = i pi.
Exponentiating: (1-w)^2 = -w for w = e^-u  =>  w = e^{+-i pi/3} (6th roots
of unity!), u* = i pi/3 for the +i pi mode. Closed forms:
  G := g(u*) + i pi u* = 2 i Cl2(pi/3)          (PURE IMAGINARY -- Cl2(pi/3)
                                                 = Gieseking's constant A143298)
  g''(u*) = i sqrt(3)
  h~(u*)  = (2-w) e^{-u*/2} / (1-w) = sqrt(3) e^{-i pi/3}   [king]
          = e^{-u*/2}/(1-w) = e^{-i pi/2}                    [control J]
  (the e^{-u/2} from q^{T_m} = e^{-u^2/2eps - u/2}; the 1/(1-e^-u) from the
   Euler-Maclaurin half-term of log (q^{m+1};q)_inf^2; (eps/2pi) from
   1/(q;q)_inf^2 modular asymptotics; saddle Gaussian gives
   (1/eps)*sqrt(2 pi eps/(-G'')).)

PREDICTIONS (validated below against high-precision Decimal evaluations):
  K(e^-eps) = 2*3^{1/4} sqrt(eps/2pi) cos(2Cl2(pi/3)/eps - pi/12) * (1+O(eps))
  J(e^-eps) = 2*3^{-1/4} sqrt(eps/2pi) cos(2Cl2(pi/3)/eps - pi/4) * (1+O(eps))
  (the overall factor 2 -- both conjugate saddles per Poisson mode -- is fixed
   empirically below: extremum ratios -> 2 with (ratio-2)/eps -> -1/3 [king],
   O(eps^2) [control])
  zeros:  2Cl2(pi/3)/(pi eps_k) = k + 7/12 + O(eps)   [king]
                                = k + 3/4  + O(eps)   [control]
=> zeros accumulate at q=1- with eps_k ~ 2Cl2(pi/3)/(pi k): the explicit
   mechanism for infinitely many poles of F(1,1,q) (non-D-finiteness program).
"""
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction as Fr
import math, re, time

# ---------- pi and Cl2(pi/3) to 60 digits (Machin + Bernoulli/zeta series) ----------
getcontext().prec = 80
def dec_atan_inv(n):   # atan(1/n)
    x = Decimal(1)/n; x2 = x*x; term = x; s = Decimal(0); k = 0
    while term != 0:
        s += term/(2*k+1) if k % 2 == 0 else -term/(2*k+1)
        term *= x2; k += 1
        if k > 500: break
    return s
PI = 16*dec_atan_inv(5) - 4*dec_atan_inv(239)

def bernoulli_upto(M):
    B = [Fr(1)]
    for m in range(1, M+1):
        s = Fr(0)
        for j in range(m):
            s += Fr(math.comb(m+1, j)) * B[j]
        B.append(-s/Fr(m+1))
    return B
BER = bernoulli_upto(90)

def clausen_pi3():
    th = PI/3
    s = th - th*th.ln()
    thp = th**3
    for n in range(1, 44):
        zfac = Fr((-1)**(n+1)) * BER[2*n] / Fr(2*math.factorial(2*n))
        s += Decimal(zfac.numerator)/Decimal(zfac.denominator) * thp / (n*(2*n+1))
        thp *= th*th
    return s
CL2 = clausen_pi3()
IMG = 2*CL2
print("pi          = %s" % str(PI)[:52])
print("Cl2(pi/3)   = %s   (Gieseking, cf. A143298)" % str(CL2)[:52])
print("ImG = 2*Cl2 = %s" % str(IMG)[:52])

# ---------- high-precision evaluation of K / J at q = e^-eps ----------
def eval_KJ(eps, mode='king'):
    """K(e^-eps) [or J] via straight Decimal summation with adaptive precision."""
    D = int(Decimal("0.86")/eps) + 60
    with localcontext() as ctx:
        ctx.prec = D
        e = +eps
        q = (-e).exp()
        S = Decimal(1); t_prev_mag = Decimal(1); maxt = Decimal(1)
        qm = Decimal(1); qT = Decimal(1); poch2 = Decimal(1)
        m = 0; tiny = Decimal(10)**(-(D-15))
        while True:
            m += 1
            qm *= q; qT *= qm; poch2 *= (1-qm)*(1-qm)
            t = ((2-qm) if mode == 'king' else Decimal(1))*qT/poch2
            S += t if m % 2 == 0 else -t
            if t > maxt: maxt = t
            if m*float(eps) > 1.0 and t < tiny*maxt:
                break
            assert m < 100000
        return +S

# quick sanity: K(0.3) > 0, K(0.33) < 0 (q_c ~ 0.3196 certified)
assert eval_KJ(-Decimal("0.3").ln()) > 0 and eval_KJ(-Decimal("0.33").ln()) < 0
print("sanity: sign change of K across certified q_c  OK")

SQ2PI = (2*PI).sqrt()
AMP_K = Decimal(3).sqrt().sqrt()/SQ2PI       # 3^{1/4}/sqrt(2pi)
AMP_J = 1/(Decimal(3).sqrt().sqrt()*SQ2PI)   # 3^{-1/4}/sqrt(2pi)
OFF = {'king': Fr(7,12), 'control': Fr(3,4)}
AMP = {'king': AMP_K, 'control': AMP_J}
print("predicted amplitude const: king 3^(1/4)/sqrt(2pi) = %s" % str(AMP_K)[:20])
print("                        control 3^(-1/4)/sqrt(2pi) = %s" % str(AMP_J)[:20])

def eps_at_phase(x):
    """eps such that 2Cl2/(pi*eps) = x."""
    return IMG/(PI*Decimal(x.numerator)/Decimal(x.denominator))

# ---------- zero hunt + offset law ----------
def find_zero(k, mode, refine=100):
    """zero of K/J between phase-extrema k+off-1/2 and k+off+1/2; returns eps_k."""
    off = OFF[mode]
    lo = eps_at_phase(Fr(k) + off + Fr(1,2))   # smaller eps = later extremum
    hi = eps_at_phase(Fr(k) + off - Fr(1,2))
    flo, fhi = eval_KJ(lo, mode), eval_KJ(hi, mode)
    if flo == 0: return lo
    if fhi == 0: return hi
    if (flo > 0) == (fhi > 0):
        # scan for the sign change (asymptotics may be shifted at low k)
        pts = [lo + (hi-lo)*Decimal(j)/16 for j in range(17)]
        vals = [eval_KJ(p, mode) for p in pts]
        found = None
        for j in range(16):
            if (vals[j] > 0) != (vals[j+1] > 0):
                lo, hi, flo, fhi = pts[j], pts[j+1], vals[j], vals[j+1]
                found = True; break
        assert found, ("no sign change near k", k, mode)
    for _ in range(refine):
        mid = (lo+hi)/2
        fm = eval_KJ(mid, mode)
        if fm == 0: return mid
        if (fm > 0) == (flo > 0): lo, flo = mid, fm
        else: hi, fhi = mid, fm
        if hi-lo < Decimal(10)**(-40): break
    return (lo+hi)/2

def offset(epsk, k):
    return IMG/(PI*epsk) - k

t0 = time.time()
print("\n== KING zero law: o_k := 2Cl2/(pi eps_k) - k  (predicted -> 7/12 = 0.58333...) ==")
king_zeros = {}
for k in list(range(5, 31)) + [35, 40, 45, 50, 55, 60]:
    ek = find_zero(k, 'king')
    king_zeros[k] = ek
    print("  k=%2d  eps_k=%.30f  o_k=%.12f" % (k, float(ek), float(offset(ek, k))))
print("  (%.1fs)" % (time.time()-t0))
# Richardson: o_k = o_inf + c*eps -> extrapolate with the two largest k
ks = sorted(king_zeros)
k1, k2 = ks[-2], ks[-1]
e1, e2 = king_zeros[k1], king_zeros[k2]
o1, o2 = offset(e1, k1), offset(e2, k2)
o_inf = o2 + (o2-o1)*e2/(e1-e2)
print("  Richardson o_inf = %.10f   vs 7/12 = %.10f   diff=%.2e"
      % (float(o_inf), 7/12, float(o_inf)-7/12))

print("\n== KING amplitude law: K(eps)*(-1)^k / (3^(1/4) sqrt(eps/2pi)) at extrema (-> 2) ==")
for k in [6, 10, 20, 40, 60, 90]:
    ee = eps_at_phase(Fr(k) + Fr(1,12))   # cos(...)=(-1)^k here per prediction
    val = eval_KJ(ee, 'king')
    pred = AMP_K*ee.sqrt()
    r = val/pred*((-1)**k)
    print("  k=%2d  eps=%.6f  ratio=%.8f   (ratio-2)/eps=%.4f"
          % (k, float(ee), float(r), (float(r)-2)/float(ee)))

print("\n== CONTROL (J) zero law: o_k predicted -> 3/4 ==")
ctrl_zeros = {}
for k in list(range(5, 21)) + [30, 40]:
    ek = find_zero(k, 'control')
    ctrl_zeros[k] = ek
    print("  k=%2d  eps_k=%.25f  o_k=%.12f" % (k, float(ek), float(offset(ek, k))))
ks = sorted(ctrl_zeros); k1, k2 = ks[-2], ks[-1]
e1, e2 = ctrl_zeros[k1], ctrl_zeros[k2]
o1, o2 = offset(e1, k1), offset(e2, k2)
o_inf = o2 + (o2-o1)*e2/(e1-e2)
print("  Richardson o_inf = %.10f   vs 3/4" % float(o_inf))

print("\n== CONTROL amplitude: J*(-1)^k/(3^(-1/4) sqrt(eps/2pi)) at extrema (-> 2) ==")
for k in [6, 10, 20, 40]:
    ee = eps_at_phase(Fr(k) + Fr(1,4))
    val = eval_KJ(ee, 'control')
    r = val/(AMP_J*ee.sqrt())*((-1)**k)
    print("  k=%2d  eps=%.6f  ratio=%.8f" % (k, float(ee), float(r)))

# ---------- map s05's banked zeros onto true indices ----------
print("\n== s05 banked zeros -> true index by the law (k_est = 2Cl2/(pi eps) - 7/12) ==")
banked = []
for line in open('out_s05_zeros_scan.txt'):
    m = re.match(r'\s*q_(\d+) = (0\.\d+)', line)
    if m and banked.__len__() < 37 and 'KING' not in line:
        banked.append((int(m.group(1)), Decimal(m.group(2))))
    if len(banked) == 37: break
prev = None
for idx, qb in banked:
    epsb = -qb.ln()
    kest = float(IMG/(PI*epsb)) - 7.0/12.0
    flag = ""
    kr = round(kest)
    if abs(kest - kr) > 0.02: flag = "  <-- OFF-LATTICE (s05 precision artifact?)"
    elif prev is not None and kr != prev + 1: flag = "  <-- gap: s05 missed %d zero(s)" % (kr-prev-1)
    print("  banked #%2d  q=%.15f  k_est=%8.3f%s" % (idx, float(qb), kest, flag))
    prev = kr
print("\nNote: banked #1,#2 are q_c and q_2 (asymptotic law not applicable that far from 1).")

# verify the suspect banked high zeros by re-locating true zeros there
print("\n== independent re-location of zeros near banked #33..#37 (adaptive precision) ==")
for k in [46, 57, 63, 78, 94]:
    try:
        ek = find_zero(k, 'king')
        print("  true k=%2d  q_k=%.20f  o_k=%.10f" % (k, math.exp(-float(ek)), float(offset(ek, k))))
    except AssertionError as ex:
        print("  true k=%2d  NOT FOUND in predicted bracket: %s" % (k, ex))
print("\ntotal %.1fs" % (time.time()-t0))
