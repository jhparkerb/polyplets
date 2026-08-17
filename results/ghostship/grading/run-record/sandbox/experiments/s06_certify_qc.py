#!/usr/bin/env python3
"""s06: CERTIFIED enclosure of q_c (smallest positive zero of K) and mu=1/q_c.

K(q) = sum_{m>=0} (-1)^m t_m(q),  t_m = (2-q^m) q^{m(m+1)/2} / (q;q)_m^2.

All arithmetic exact (fractions.Fraction). Rigor chain:

[R1] Term decrease: for m>=1 and 0<q<=34/100,
     t_{m+1}/t_m = q^{m+1}(2-q^{m+1}) / [(2-q^m)(1-q^{m+1})^2]
                <= 2q^2/[(2-q)(1-q^2)^2] =: r(q)      (q^{m+1}<=q^2, 2-q^{m+1}<=2,
                                                       2-q^m>=2-q, 1-q^{m+1}>=1-q^2)
     r is increasing on (0,1) (numerator increasing, denominator decreasing),
     and we check r(34/100) < 1 exactly.  Hence t_1 >= t_2 >= ... for all
     q in (0,34/100], so for any N>=1 the alternating tail after S_N has sign
     (-1)^(N+1) and magnitude <= t_{N+1}:  K lies between S_N and S_{N+1}.

[R2] Left lemma: on (0,29/100], K >= S_1 = 1 - t_1 = (1-4q+2q^2)/(1-q)^2 > 0
     since 2q^2-4q+1 is decreasing on [0,1] (derivative 4q-4<0) and we check
     its value at q=29/100 > 0 exactly.  (Tail after S_1 is >= 0 by [R1].)

[R3] Derivative bound on the window [qlo,qhi]=[29/100,33/100]:
     t_m'(q) = t_m(q) * ell_m'(q),
     ell_m'(q) = -m q^{m-1}/(2-q^m) + T_m/q + 2*sum_{j<=m} j q^{j-1}/(1-q^j),
     T_m = m(m+1)/2.  Bounds valid for all q in the window:
       sup t_m  <= tau_m := 2 qhi^{T_m} / prod_{j<=m}(1-qhi^j)^2
       |ell_m'| <= B_m   := m qhi^{m-1}/(2-qhi^m) + T_m/qlo
                           + 2 sum_{j<=m} j qhi^{j-1}/(1-qhi^j)
     L := sum_{m<=NL} tau_m B_m + TAIL >= sup_{[qlo,qhi]} |K'|, where
     TAIL uses  tau_m <= 8 qhi^{T_m}  (since prod_{j<=m}(1-qhi^j)^2 >= 1/4,
     checked exactly via prod_{j<=40}(1-qhi^j)*(1 - qhi^41/(1-qhi)) lower bound)
     and B_m <= beta(m) := m + T_m/qlo + 2/(1-qhi)^3, with successive-ratio
     sigma := 3 qhi^{NL+1} checked < 1/2, so TAIL <= 16 qhi^{T_{NL+1}} beta(NL+1).

[R4] Lipschitz march: from x=29/100, with certified lower bracket Klo(x)>0,
     K > 0 on [x, x + Klo(x)/L * (1-1e-6)]; advance (rounding the new point
     DOWN, which keeps the covered set an interval).  This certifies K > 0 on
     (0, a_f].  Then find b_f > a_f with certified upper bracket Khi(b_f) < 0.
     => the smallest positive zero q_c of K satisfies q_c in (a_f, b_f].
     => mu = 1/q_c in [1/b_f, 1/a_f).
"""
from fractions import Fraction as Fr
import sys, time

Q34 = Fr(34,100); QLO = Fr(29,100); QHI = Fr(33,100)
NTERM = 26          # terms used per evaluation bracket
NL    = 30          # terms in the derivative bound

def terms(q, N):
    """t_0..t_N exactly."""
    t = []; poch2 = Fr(1); qm = Fr(1); qT = Fr(1)   # q^m, q^{T_m}
    for m in range(N+1):
        if m > 0:
            qm *= q; qT *= qm; poch2 *= (1-qm)**2
        t.append((2-qm)*qT/poch2)
    return t

def bracket_K(q, N=NTERM):
    """certified [Klo,Khi] containing K(q), for 0<q<=34/100 (uses [R1])."""
    assert Fr(0) < q <= Q34
    t = terms(q, N+1)
    # exact decrease check t_1>=...>=t_{N+1} (must hold by [R1]; assert anyway)
    for m in range(1, N+1):
        assert t[m] >= t[m+1], (q, m)
    S = Fr(0); brackets = []
    for m in range(N+1):
        S += t[m] if m % 2 == 0 else -t[m]
        if m >= 1: brackets.append(S)
    lo, hi = min(brackets[-2:]), max(brackets[-2:])
    return lo, hi

# ---------- [R1] r(34/100) < 1 ----------
q = Q34
r34 = 2*q*q / ((2-q)*(1-q*q)**2)
assert r34 < 1
print("[R1] r(34/100) = %.6f < 1  (=> alternating bracketing valid on (0,0.34])" % float(r34))

# ---------- [R2] ----------
v = 1 - 4*QLO + 2*QLO*QLO
assert v > 0
print("[R2] 1-4q+2q^2 at q=29/100 = %s > 0  (=> K>0 on (0,29/100])" % v)

# ---------- [R3] L >= sup|K'| on [29/100,33/100] ----------
# exact lower bound on prod_{j>=1}(1-qhi^j)^2
P = Fr(1); qj = Fr(1)
for j in range(1, 41):
    qj *= QHI; P *= (1-qj)
Pinf_lb = P * (1 - QHI**41/(1-QHI))     # prod_{j>40}(1-qhi^j) >= 1 - sum qhi^j
assert Pinf_lb**2 > Fr(1,4)
tau = []; B = []; poch2 = Fr(1); qm = Fr(1); qT = Fr(1); sj = Fr(0)
L = Fr(0)
for m in range(NL+1):
    if m > 0:
        qm *= QHI; qT *= qm; poch2 *= (1-qm)**2
        sj += m*qm/QHI/(1-qm)
    Tm = Fr(m*(m+1),2)
    tau_m = 2*qT/poch2
    B_m = (m*qm/QHI/(2-qm) if m>0 else Fr(0)) + Tm/QLO + 2*sj
    L += tau_m*B_m
sigma = 3*QHI**(NL+1)
assert sigma < Fr(1,2)
TmN = Fr((NL+1)*(NL+2),2)
beta = (NL+1) + TmN/QLO + 2/(1-QHI)**3
L += 16*QHI**TmN*beta
print("[R3] certified Lipschitz bound L = %.6f on [0.29,0.33]" % float(L))

# ---------- [R4] march ----------
t0 = time.time()
x = QLO; it = 0
SCALE = 10**50
while True:
    lo, hi = bracket_K(x)
    assert lo > 0, ("march hit nonpositive lower bracket", float(x))
    step = lo/L*Fr(999999,1000000)
    if step < Fr(1, 10**46):
        break
    xn = x + step
    x = Fr((xn*SCALE).__floor__(), SCALE)   # round down, certification intact
    it += 1
    if it % 50 == 0:
        print("   march it=%d  x=%.20f  step~%.3e  (%.1fs)" % (it, float(x), float(step), time.time()-t0))
    assert it < 5000
a_f = x
print("[R4] march done: %d steps, %.1fs;  K > 0 certified on (0, a_f]" % (it, time.time()-t0))

# find b_f with certified K(b_f) < 0
delta = Fr(1, 10**46)
b_f = None
for j in range(1, 200):
    cand = a_f + delta
    lo, hi = bracket_K(cand)
    if hi < 0:
        b_f = cand; break
    delta *= 2
assert b_f is not None
width = b_f - a_f
print("[R4] b_f found:  K(b_f) < 0 certified;  enclosure width = %.3e" % float(width))

def dec(fr, ndig):
    """decimal string of fr in (0,10), ndig digits after the point, truncated."""
    num, den = fr.numerator, fr.denominator
    ip = num // den; rem = num - ip*den
    digs = []
    for _ in range(ndig):
        rem *= 10; d = rem // den; rem -= d*den; digs.append(str(d))
    return "%d.%s" % (ip, "".join(digs))

qa, qb = dec(a_f, 48), dec(b_f, 48)
mu_lo, mu_hi = Fr(1)/b_f, Fr(1)/a_f
ma, mb = dec(mu_lo, 48), dec(mu_hi, 48)
common_q = 0
for c1, c2 in zip(qa, qb):
    if c1 == c2: common_q += 1
    else: break
common_m = 0
for c1, c2 in zip(ma, mb):
    if c1 == c2: common_m += 1
    else: break
print()
print("CERTIFIED: q_c in (a_f, b_f], smallest positive zero of K")
print("  a_f = %s" % qa)
print("  b_f = %s" % qb)
print("  agreed prefix: %s   (%d chars)" % (qa[:common_q], common_q))
print("CERTIFIED: mu = 1/q_c in [1/b_f, 1/a_f)")
print("  1/b_f = %s" % ma)
print("  1/a_f = %s" % mb)
print("  agreed prefix: %s   (%d chars)" % (ma[:common_m], common_m))
print()
print("s05 banked (uncertified) values for comparison:")
print("  q_c = 0.319596718059387465518602891982713923614...")
print("  mu  = 3.128943269730886252277447995387754160532...")
