#!/usr/bin/env python3
# Lifetime-3 byproduct sequences (results/lifetime3-proof.md), from the recovered
# fixed-height GF orders in results/fixed_height_gfs.txt:
#   orders     deg Q_H  -- read directly (H=1..10)
#   atom degs  deg N_H  -- via the lifetime-3 degree law deg Q_H = deg N_{H-2} +
#              deg N_{H-1} + deg N_H, with N_{-1}=N_0=0. (Computing deg N_H directly as
#              deg gcd(Q_H,Q_{H+1},Q_{H+2}) is exact but impractical at these degrees --
#              rational poly-gcd coefficient blowup -- so we use the law, which is
#              verified directly to deg N_7=181 in the proof; H>=8 terms are extrapolated.)
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

orders = []
for line in open(os.path.join(ROOT, "results", "fixed_height_gfs.txt")):
    if line.startswith("H=") and "order=" in line:
        orders.append(int(line.split("order=")[1].split()[0]))

N = [0, 0]                       # sentinels N[-1], N[0]
for q in orders:                 # q = deg Q_H for H = 1, 2, ...
    N.append(q - N[-1] - N[-2])
atoms = N[2:]

print("orders     deg Q_H:", " ".join(map(str, orders)))
print("atom degs  deg N_H:", " ".join(map(str, atoms)))
assert atoms[:7] == [1, 2, 4, 9, 29, 68, 181], "atom degrees disagree with lifetime3-proof.md"
print("(deg N_H verified directly to 181 (H=7) in the proof; H>=8 via the degree law)")
