#!/usr/bin/env python3
"""Phase 1 of Certificate Squeeze: turn the numerical king upper bound (king_bui.py)
into an EXACT rational certificate.

Method (Bui arXiv:2511.00461, Lemma 2): the system map is
    F_x(u)_T = x                              if T is a base type
    F_x(u)_T = u_{T'} + u_{T'} * u_D          otherwise   (T' = T+{d forbidden})
The monotone iteration from 0 is bounded at x  <=>  lambda <= 1/x. A super-solution
u > 0 with  u_T >= F_x(u)_T  for every T  PROVES boundedness at x (F_x is monotone,
so u dominates every iterate). Hence a rational u satisfying that system, checked in
exact Fraction arithmetic, is a machine-checkable proof of lambda <= 1/x.

We pick a rational x just below x* = 1/9.306, float-iterate to the fixpoint, rationalize,
and repair any violated components upward until the exact check passes.

Usage: python3 -m experiments.king_certificate [RD]     (default RD=3, the banked 9.31)
"""
import sys
from fractions import Fraction as F
from experiments.king_types import OFF

KING8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
def free_cells(f): return [d for d in KING8 if d not in f]

RD = int(sys.argv[1]) if len(sys.argv) > 1 else 3
WD = [(dx,dy) for dx in range(-RD,RD+1) for dy in range(-RD,RD+1) if (dx,dy)!=(0,0)]
def d_type(f, d):
    ke = {(0,0)} | (set(KING8) - {d}) | set(f)
    return frozenset(o for o in WD if (d[0]+o[0], d[1]+o[1]) in ke)
def canonical(free): return min(free, key=lambda p:(p[1], p[0]))

# ---- build closure (same system as king_bui.py) ----
recur = {}
G8 = frozenset({OFF[o] for o in ('W','SW','S','SE')})
seen = {G8}; q = [G8]
while q:
    T = q.pop(); fr = free_cells(T)
    if not fr:
        recur[T] = None; continue
    d = canonical(fr); Tp = frozenset(set(T) | {d}); D = d_type(T, d)
    recur[T] = (Tp, D)
    for X in (Tp, D):
        if X not in seen: seen.add(X); q.append(X)

tl = list(recur); ix = {T:i for i,T in enumerate(tl)}; G8i = ix[G8]; NT = len(tl)
rule = [None if recur[T] is None else (ix[recur[T][0]], ix[recur[T][1]]) for T in tl]
print(f"king system: {NT} types (RD={RD})")

# ---- float map + bisection for x* ----
def fstep(v, x):
    nv = [0.0]*NT
    for i in range(NT):
        r = rule[i]
        if r is None: nv[i] = x
        else: a = v[r[0]]; nv[i] = a + a*v[r[1]]
    return nv
def bounded(x, iters=6000, cap=1e12):
    v = [x]*NT
    for _ in range(iters):
        nv = fstep(v, x)
        if nv[G8i] > cap: return None
        if abs(nv[G8i]-v[G8i]) < 1e-14*nv[G8i]: return v
        v = nv
    return v
lo, hi = 1/13.0, 1/4.0
for _ in range(60):
    m = 0.5*(lo+hi)
    if bounded(m) is not None: lo = m
    else: hi = m
xstar = lo
print(f"  x* ~ {xstar:.12f}   =>  lambda ~ {1/xstar:.6f}")

# ---- choose a rational x below x* with a small margin, get the float fixpoint ----
# eps sets the safety margin: fixpoint values scale ~1/eps, so eps=1e-3 keeps values
# ~1e3 (easy to rationalize) at the cost of loosening 1/x by only ~0.1%.
eps = 1e-3
DENOM = 10**6
x = F(round(xstar*(1-eps)*DENOM), DENOM)    # rational x < x*, clean denominator
lam_bound = 1/x
vfix = bounded(float(x), iters=200000, cap=1e300)
assert vfix is not None, "system diverges at chosen x; increase eps"

# ---- rationalize the fixpoint, then repair upward to a valid super-solution ----
# CRITICAL: round every value UP to a FIXED denominator CD. Rounding up preserves the
# super-solution inequality (u_i >= need still holds), and pinning the denominator stops
# the product a+a*u from exploding denominators sweep over sweep.
import math
CD = 10**6
def ceilD(fr): return F(math.ceil(fr * CD), CD)     # smallest k/CD >= fr

u = [ceilD(F(val).limit_denominator(CD)) for val in vfix]

def Fx_exact(u, i):
    r = rule[i]
    if r is None: return x
    a = u[r[0]]; return a + a*u[r[1]]

# Iterate repair: wherever u_i < F_x(u)_i, raise u_i (rounded up to 1/CD). F_x is monotone
# and the true fixpoint at x is finite, so this converges to a super-solution.
for sweep in range(5000):
    viol = 0
    for i in range(NT):
        need = Fx_exact(u, i)
        if u[i] < need:
            u[i] = ceilD(need)               # raise, pinned to denominator CD
            viol += 1
    if viol == 0:
        print(f"  super-solution reached after {sweep} repair sweeps")
        break
else:
    print("  WARNING: repair did not converge; increase eps (x too close to x*)")

# ---- final EXACT verification ----
ok = all(u[i] >= Fx_exact(u, i) for i in range(NT))
maxden = max(v.denominator for v in u)
print(f"\n  EXACT certificate check: {'PASS' if ok else 'FAIL'}")
print(f"  x = {x} = {float(x):.12f}   (rational, denominator {x.denominator})")
print(f"  lambda <= 1/x = {lam_bound} = {float(lam_bound):.6f}")
print(f"  certificate: {NT} rationals, max denominator {maxden}")
assert ok, "CERTIFICATE FAILED"
print("\n  RIGOROUS: lambda(polyplets) <= {:.6f}, proved by exact rational certificate.".format(float(lam_bound)))
