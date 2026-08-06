#!/usr/bin/env python3
"""Strip growth constants mu_H = 1/(smallest positive root of Q_H), from the
banked fixed-height GF denominators (results/fixed_height_gfs.txt), then
extrapolate mu_H -> lambda. mu_H is an exact algebraic number (the dominant
singularity of the height-H GF), so there is no count-ratio convergence issue
-- but computing it in floating point is not free of numerical caveat:

  Q_H has large integer coefficients of alternating sign and its smallest
  positive root sits near 0.16, so Horner cancels catastrophically. At the
  mp.dps=50 this script used to run at, the H=11 root carried only ~8 correct
  digits, not 50 (measured: experiments/mu_H_precision_audit.py). The loss
  grows with H, so a fixed working precision silently degrades as the ladder
  is extended.

So every root is now computed twice, at dps and at 2*dps, and is reported only
if the two agree to DIGITS_WANTED significant digits; otherwise the working
precision doubles and it is recomputed. Fail-closed: a root that cannot be
confirmed at higher precision raises instead of being printed.

The cross-check against cpp/strip_mu's power iteration is a separate matter and
is capped on the other side: that engine converges rho to 1e-11 in double and
prints %.7f, so the comparison establishes agreement to those 7 decimals (7.8
to 8.9 significant digits, measured) and nothing beyond them. The same
iteration recorded at 10 digits in results/strip_mu_certificates.log agrees to
9-10 significant digits, which is the sharpest form of the cross-check. See
experiments/mu_H_precision_audit.py and results/strip-growth-lambda-bounds.md.

Cost: 5m16s for H<=11, measured (the confirmation run at 2*dps dominates, and
H=11 escalates once). Left in mpmath rather than ported: it is a one-shot
analysis over ten polynomials, not a compute job.
"""
import ast, re
from mpmath import mp, mpf, fabs, log10

DPS0 = 60            # starting working precision
DIGITS_WANTED = 25   # confirmed significant digits required of every root
DPS_CAP = 480

Q = {}
with open("results/fixed_height_gfs.txt") as f:
    H = None
    for line in f:
        m = re.match(r"H=(\d+)", line)
        if m: H = int(m.group(1))
        if line.startswith("Q:") and H is not None:
            Q[H] = ast.literal_eval(line[2:].strip())

def polyval(q, x):
    s = mpf(0)
    for c in reversed(q):          # Horner, q low->high
        s = s * x + c
    return s

def mu_at(q, dps):
    # smallest positive real root of Q (radius of convergence); Q(0)=1>0.
    # scan for first sign change, then bisect. The bisection depth follows dps:
    # at a fixed 200 halvings the bracket bottoms out near 1e-64 however many
    # digits mpmath is carrying.
    mp.dps = dps
    iters = int(3.4 * dps) + 50
    step = mpf("0.0002"); x = step; prev = polyval(q, mpf(0))
    while x < mpf("0.6"):
        cur = polyval(q, x)
        if cur == 0: return 1 / x
        if (prev > 0) != (cur > 0):
            lo, hi = x - step, x
            for _ in range(iters):
                mid = (lo + hi) / 2
                if (polyval(q, lo) > 0) == (polyval(q, mid) > 0): lo = mid
                else: hi = mid
            return 1 / ((lo + hi) / 2)
        prev = cur; x += step
    raise ValueError("no root found in (0,0.6)")

def agreeing_digits(a, b):
    mp.dps = 2 * DPS_CAP
    d = fabs(mpf(a) - mpf(b))
    return 10**9 if d == 0 else int(-log10(d / fabs(mpf(b))))

def mu_of(q, label=""):
    """The root, confirmed at twice the precision it was computed at."""
    dps = DPS0
    while dps <= DPS_CAP:
        lo_prec, hi_prec = mu_at(q, dps), mu_at(q, 2 * dps)
        got = agreeing_digits(lo_prec, hi_prec)
        if got >= DIGITS_WANTED:
            return hi_prec, min(got, 2 * dps)
        dps *= 2
    raise ValueError(f"{label}: no root confirmed to {DIGITS_WANTED} digits "
                     f"by dps={DPS_CAP} (best {got})")

mu, conf = {}, {}
for H in sorted(Q):
    if H >= 2:
        mu[H], conf[H] = mu_of(Q[H], f"H={H}")
mp.dps = 40
print(" H   mu_H (exact strip growth constant)   confirmed digits")
for H in sorted(mu):
    print(f"{H:2d}   {mu[H]:.12f}                     {conf[H]:>3d}")

xs = sorted(mu); seq = [mu[H] for H in xs]

# Repeated Richardson assuming mu_H = lambda - c/H^p (+ higher), for p=1,2.
def richardson(xs, seq, p):
    cur = list(seq); H = list(xs)
    while len(cur) > 1:
        nxt = []
        for i in range(len(cur) - 1):
            h1, h2 = H[i], H[i + 1]
            nxt.append((cur[i + 1] * h2**p - cur[i] * h1**p) / (h2**p - h1**p))
        cur = nxt; H = H[1:]
    return cur[0]

print("\nExtrapolations mu_H -> lambda:")
for p in (1, 2):
    print(f"  full Richardson, 1/H^{p}:  lambda ~ {richardson(xs, seq, p):.4f}")

# Neville/Aitken on last few points, and a simple 1/H^2 two-point on top pairs
for i in range(len(xs) - 3, len(xs) - 1):
    h1, h2 = xs[i], xs[i + 1]; f1, f2 = seq[i], seq[i + 1]
    lam2 = (f2 * h2**2 - f1 * h1**2) / (h2**2 - h1**2)
    print(f"  two-point 1/H^2 on H={h1},{h2}:  lambda ~ {lam2:.4f}")

print("\n a(n)-ratio fit (paper): lambda ~ 7.111")
