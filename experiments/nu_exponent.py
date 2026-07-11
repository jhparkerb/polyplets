#!/usr/bin/env python3
"""Where does a(n)'s mass sit, and what is the extent exponent nu?
Mean/mode bbox-height vs n from the banked height triangle; fit mean_H ~ c*n^nu.
Expect nu ~ 0.6407 (2D lattice-animal size exponent) -- sublinear, so the mass
sits at growing-but-sublinear height, not at fixed small H nor at n/2."""
import os, math
from statistics import median

PER = "results/ns_a36/perheight"
T = {}
for H in range(1, 19):
    for line in open(os.path.join(PER, f"h{H}.out")):
        n, v = line.split(); T[(int(n), int(H))] = int(v)

a = {}
for line in open("results/ns_a36/triangle.txt"):
    p = line.split()
    if len(p) == 2: a[int(p[0])] = int(p[1])

print(" n | captured(H<=18) | mean_H | mode_H | mean_H/n")
rows = []
for n in range(4, 37):
    col = [(H, T.get((n, H), 0)) for H in range(1, 19)]
    tot = sum(c for _, c in col)
    if tot == 0: continue
    capt = tot / a[n] if n in a else float('nan')
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
