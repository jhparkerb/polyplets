#!/usr/bin/env python3
"""Where does a(n)'s mass sit, and what is the extent exponent nu?
Mean/mode bbox-height vs n from the banked height triangle; fit mean_H ~ c*n^nu.
Expect nu ~ 0.6407 (2D lattice-animal size exponent) -- sublinear, so the mass
sits at growing-but-sublinear height, not at fixed small H nor at n/2.

Default: the FULL exact triangle results/triangle.txt (all H, 1 <= H <= n <= 40).
`python3 experiments/nu_exponent.py 18` reproduces the original 2026-07-10 run,
which used only the H <= 18 slice (captured < 1 for n > 19; the clean range is
then n <= 21, and mean_H/n is truncation-biased downward for larger n).
"""
import os, sys, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HMAX = int(sys.argv[1]) if len(sys.argv) > 1 else None   # None = untruncated

# full exact triangle: "n H T(n,H)" rows (comment lines start with '#')
T = {}
NMAX = 0
with open(os.path.join(ROOT, "results", "triangle.txt")) as fh:
    for line in fh:
        p = line.split()
        if len(p) == 3 and p[0].isdigit():
            n, H, v = int(p[0]), int(p[1]), int(p[2])
            T[(n, H)] = v
            NMAX = max(NMAX, n)

a = {n: sum(T.get((n, H), 0) for H in range(1, n + 1)) for n in range(1, NMAX + 1)}
cap = HMAX if HMAX else NMAX

print(f"data: results/triangle.txt (n <= {NMAX}), "
      f"{'H <= %d slice' % HMAX if HMAX else 'untruncated'}")
print(f" n | captured(H<={cap}) | mean_H | mode_H | mean_H/n")
rows = []
for n in range(4, NMAX + 1):
    col = [(H, T.get((n, H), 0)) for H in range(1, min(cap, n) + 1)]
    tot = sum(c for _, c in col)
    if tot == 0:
        continue
    capt = tot / a[n] if a.get(n) else float('nan')
    meanH = sum(H * c for H, c in col) / tot
    modeH = max(col, key=lambda x: x[1])[0]
    rows.append((n, capt, meanH, modeH))
    print(f"{n:2d} |   {capt:.5f}      | {meanH:5.2f}  |  {modeH:2d}    | {meanH/n:.3f}")

# fit log(mean_H) = log c + nu log n over the clean range (captured ~ 1)
clean = [(n, mh) for (n, capt, mh, _) in rows if capt > 0.9999]
xs = [math.log(n) for n, _ in clean]; ys = [math.log(mh) for _, mh in clean]
k = len(xs); sx = sum(xs); sy = sum(ys)
nu = (k * sum(x*y for x, y in zip(xs, ys)) - sx*sy) / (k * sum(x*x for x in xs) - sx*sx)
print(f"\nclean range n={clean[0][0]}..{clean[-1][0]} (captured>0.9999)")
print(f"nu (mean_H ~ n^nu)  = {nu:.4f}    [2D lattice-animal value ~0.6407]")
# local slopes (finite-size drift)
print("local slopes (consecutive n):",
      [round((math.log(clean[i+1][1])-math.log(clean[i][1])) /
              (math.log(clean[i+1][0])-math.log(clean[i][0])), 3)
       for i in range(len(clean)-1)])
# 4-step local slopes: the smoother drift series quoted in the .md
print("local slopes (4-step, d log<H>/d log n):")
mh = dict((n, m) for n, m in clean)
for n in range(12, clean[-1][0] + 1, 4):
    if n - 4 in mh and n in mh:
        print(f"  n={n:2d}  <H>={mh[n]:6.3f}  nu_eff[{n-4},{n}]="
              f"{(math.log(mh[n]) - math.log(mh[n-4])) / (math.log(n) - math.log(n-4)):.4f}")
