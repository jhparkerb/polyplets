#!/usr/bin/env python3
# T2: the k-hole generating function G_{H,k}(x) has recurrence order (= deg denominator)
# that is LINEAR in the hole count k. Fit order(H,k) = m_H*k + b_H per height and test
# the clean form order = m_H*(k+1); identify the slope sequence m_H.
import re
import collections

data = collections.defaultdict(dict)   # H -> {k: order}
for line in open("results/hole_gfs.txt"):
    m = re.search(r"H=(\d+) k=(\d+)\s+order=(\d+)", line)
    if m:
        H, k, o = map(int, m.groups())
        data[H][k] = o

ATOM = {1: 1, 2: 2, 3: 4, 4: 9, 5: 29, 6: 68, 7: 181, 8: 462}  # deg N_H (fixed_height_gf.md)
print(" H   m_H(slope)  b_H  order==m_H*(k+1)?  k=0 order  atom_deg(H+1)")
for H in sorted(data):
    ks = sorted(data[H])
    if len(ks) < 2:
        print(f" {H}   (only k=0: order={data[H][0]})")
        continue
    # slope from the last two points (the eventual linear regime)
    m = data[H][ks[-1]] - data[H][ks[-2]]
    b = data[H][ks[-1]] - m * ks[-1]
    exact_linear = all(data[H][k] == m * k + b for k in ks if k >= 1)
    clean = all(data[H][k] == m * (k + 1) for k in ks if k >= 1)
    print(f" {H}    {m:5d}    {b:4d}    {'YES' if clean else ('lin k>=1' if exact_linear else 'NO')}"
          f"        {data[H].get(0,'?'):>4}     {ATOM.get(H+1,'?')}")

print()
print("slope sequence m_H (H=3,4,5,6):", [data[H][sorted(data[H])[-1]] -
      data[H][sorted(data[H])[-2]] for H in sorted(data) if len(data[H]) >= 2])
