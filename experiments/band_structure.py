"""Three structural probes of the uncovered middle band, each with a control:

  1. p-adic valuations of the slope-2 slice   (exact integers)
  2. Hankel determinants / J-fraction of the slice (exact integers)
  3. finite-size scaling of the certified mu_H ladder toward lambda

Controls throughout: a sequence whose structure is KNOWN must be recognized,
and a deliberately structureless sequence must be rejected.
"""
import glob, re, math
from fractions import Fraction
import numpy as np

T = {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2:
            T[(int(p[0]), H)] = int(p[1])

Hs = [H for H in range(1, 21) if T.get((2 * H, H))]
S  = [T[(2 * H, H)] for H in Hs]
Sk = [T[(H + 2, H)] for H in range(1, 21) if T.get((H + 2, H))]      # known: quadratic*3^H

def catalan(n):
    c = 1
    out = []
    for i in range(n):
        out.append(c); c = c * 2 * (2 * i + 1) // (i + 2)
    return out
CAT = catalan(20)
GENERIC = [round(41.85 ** H * H ** -0.25 * 0.7) for H in range(1, 21)]   # no structure

def vp(n, p):
    v = 0
    while n % p == 0:
        n //= p; v += 1
    return v

print("=" * 78)
print("1. p-ADIC VALUATIONS   (generic sequence: v_p iid geometric, mean 1/(p-1))")
print("=" * 78)
for label, seq in (("slope-2 T(2H,H)", S), ("CONTROL Catalan", CAT),
                   ("CONTROL s=1 k=2", Sk), ("CONTROL generic", GENERIC)):
    print(f"\n{label}")
    for p in (2, 3, 5, 7):
        vs = [vp(x, p) for x in seq]
        exp_mean = 1 / (p - 1)
        print(f"  p={p}: {vs}   mean={np.mean(vs):.2f} (generic {exp_mean:.2f})")

print()
print("=" * 78)
print("2. HANKEL DETERMINANTS   det[S(i+j)]_{0..m-1}; smooth dets => J-fraction")
print("=" * 78)
def hankel_dets(seq, maxm):
    out = []
    for m in range(1, maxm + 1):
        if 2 * m - 1 > len(seq): break
        M = [[Fraction(seq[i + j]) for j in range(m)] for i in range(m)]
        # exact fraction-free determinant
        det = Fraction(1); A = [r[:] for r in M]; sign = 1
        for c in range(m):
            piv = next((i for i in range(c, m) if A[i][c] != 0), None)
            if piv is None: det = Fraction(0); break
            if piv != c: A[c], A[piv] = A[piv], A[c]; sign = -sign
            det *= A[c][c]
            inv = A[c][c]
            for i in range(c + 1, m):
                f = A[i][c] / inv
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
        out.append(sign * det)
    return out

SMALL = [p for p in range(2, 10000) if all(p % q for q in range(2, int(p ** .5) + 1))]
def smooth_part(n):
    """(smooth factor removed, remaining cofactor) using primes < 10^4"""
    n = abs(int(n))
    if n == 0: return 0, 0
    rem = n
    for p in SMALL:
        while rem % p == 0: rem //= p
    return n, rem

for label, seq in (("slope-2", S), ("CONTROL Catalan (dets are all 1)", CAT),
                   ("CONTROL s=1 k=2", Sk), ("CONTROL generic", GENERIC)):
    print(f"\n{label}")
    for m, d in enumerate(hankel_dets(seq, 9), start=1):
        n, rem = smooth_part(d)
        digits = len(str(abs(int(d)))) if d else 1
        print(f"  m={m}: {digits:4d} digits, cofactor after removing primes<10^4: "
              f"{len(str(rem)) if rem else 0:4d} digits {'(SMOOTH)' if rem == 1 else ''}")

print()
print("=" * 78)
print("3. FINITE-SIZE SCALING OF mu_H  ->  lambda = 7.110(1)")
print("=" * 78)
MU = {2: 2.414213562, 3: 3.443718375, 4: 4.182321413, 5: 4.717801291,
      6: 5.115324460, 7: 5.417847610, 8: 5.653372762, 9: 5.840457941,
      10: 5.991695792, 11: 6.115841628, 12: 6.219124621, 13: 6.306071285,
      14: 6.380034445, 15: 6.4435408, 16: 6.4985245, 17: 6.5464870}
LAM = 7.110

def fit_scaling(lam, fitH, allH):
    """ln(lam - mu_H) = ln c - x ln H"""
    X = np.column_stack([np.ones(len(fitH)), np.log(fitH)])
    y = np.log([lam - MU[h] for h in fitH])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = {h: lam - math.exp(coef[0] + coef[1] * math.log(h)) for h in allH}
    return coef, pred

for lam in (7.108, 7.110, 7.112):
    fitH = [h for h in range(6, 16)]
    coef, pred = fit_scaling(lam, fitH, [16, 17])
    err = max(abs(pred[h] - MU[h]) / MU[h] for h in (16, 17))
    print(f"  lambda={lam}: x = {-coef[1]:.4f}, c = {math.exp(coef[0]):.4f}, "
          f"holdout H=16,17 max rel err {err:.3%}")

print("\n  CONTROL: same fit on synthetic mu_H = lam - c H^-x with x = 1.00, c = 9")
SYN = {h: 7.110 - 9.0 * h ** -1.0 for h in range(2, 18)}
save = dict(MU); MU.update(SYN)
coef, pred = fit_scaling(7.110, list(range(6, 16)), [16, 17])
print(f"  recovered x = {-coef[1]:.4f} (true 1.0000), "
      f"holdout {max(abs(pred[h]-MU[h])/MU[h] for h in (16,17)):.3%}")
MU.clear(); MU.update(save)

print("\n  lambda free (3-param), fit H=6..15, holdout 16,17:")
best = None
for lam in np.arange(6.90, 7.60, 0.002):
    coef, pred = fit_scaling(lam, list(range(6, 16)), [16, 17])
    err = max(abs(pred[h] - MU[h]) / MU[h] for h in (16, 17))
    if best is None or err < best[0]: best = (err, lam, -coef[1], math.exp(coef[0]))
print(f"  best-holdout lambda = {best[1]:.3f}, x = {best[2]:.4f}, c = {best[3]:.4f}, "
      f"err {best[0]:.4%}   (independent truth: lambda = 7.110(1))")
