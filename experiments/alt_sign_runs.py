"""The alternating row sum F_n(-1) = sum_H (-1)^H T(n,H): its sign oscillates
with slowly growing period. Mechanism: F_n(-1) = a(n) * E[(-1)^H], and for a
smooth unimodal height distribution the sign tracks cos(pi * mean_H(n)). Sign
runs therefore have length ~ 1/(d mean_H/dn). With mean_H ~ c n^nu that is
~ n^(1-nu) -- so the run lengths are a readout of the extent exponent.
Test: measure run lengths, measure mean_H directly, check they agree.
"""
import glob, re, math
import numpy as np
T, A = {}, {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2:
            n, v = int(p[0]), int(p[1]); T[(n, H)] = v
            if v: A[n] = A.get(n, 0) + v

alt = {n: sum((-1) ** H * T.get((n, H), 0) for H in range(1, n + 1)) for n in range(1, 41)}
mean = {n: sum(H * T.get((n, H), 0) for H in range(1, n + 1)) / A[n] for n in A}

print("n   sign  mean_H   frac(mean_H)   |F|/a(n)")
for n in range(4, 41):
    s = '+' if alt[n] > 0 else ('0' if alt[n] == 0 else '-')
    print(f"{n:2d}   {s}    {mean[n]:6.3f}   {mean[n]%1:6.3f}      {abs(alt[n])/A[n]:.3e}")

# sign runs and their midpoints
runs, cur, start = [], None, 4
for n in range(4, 41):
    s = 1 if alt[n] > 0 else -1
    if cur is None: cur = s
    elif s != cur:
        runs.append((start, n - 1)); cur = s; start = n
runs.append((start, 40))
print(f"\nsign runs: {runs}")
print(f"run lengths: {[b - a + 1 for a, b in runs]}")

# does a sign flip coincide with mean_H crossing a half-integer?
print("\nflip locations vs half-integer crossings of mean_H:")
for a, b in runs[1:]:
    print(f"  flip between n={a-1} and n={a}: mean_H {mean[a-1]:.3f} -> {mean[a]:.3f}"
          f"   (crosses .5? {math.floor(mean[a-1]*2)!=math.floor(mean[a]*2)})")

# exponent from run lengths vs from mean_H directly
mids = np.array([(a + b) / 2 for a, b in runs[2:]])
lens = np.array([b - a + 1 for a, b in runs[2:]], float)
if len(mids) >= 3:
    c = np.polyfit(np.log(mids), np.log(lens), 1)
    print(f"\nrun length ~ n^{c[0]:.3f}  =>  nu = {1 - c[0]:.3f}")
ns = np.array(sorted(mean)); ms = np.array([mean[n] for n in ns])
sel = ns >= 12
c2 = np.polyfit(np.log(ns[sel]), np.log(ms[sel]), 1)
print(f"mean_H ~ n^{c2[0]:.3f} measured directly over n>=12  "
      f"(banked nu_eff at n=40 is 0.676, results/growth-constant.md)")
