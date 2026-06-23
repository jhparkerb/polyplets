"""Fast per-height growth constant lambda_H WITHOUT the full GF recovery.
B_H(n) is C-finite (rational GF) with dominant eigenvalue lambda_H, so we only need
its MAGNITUDE at modest n: a small-N mod-p sweep (build/gf_modp) over a few primes +
CRT gives exact B_H(n) in seconds-minutes (vs hours for the order-~10^4 GF). lambda_H
= dominant growth rate, recovered by log-linear tail slope + Aitken (geometric conv.).

USAGE: lambda_ladder_fast.py H N [nprimes]
"""
import subprocess, sys, math, os
from multiprocessing import Pool
import numpy as np
ROOT = __import__("os").path.dirname(__import__("os").path.dirname(__file__))
GF = os.environ.get("POLY_GF_ENGINE", ROOT + "/build/gf_modp")  # e.g. build/gf_knight
# primes just below 2^31 (disjoint, ~9.33 digits each)
def primes_below(bound, k):
    out=[]; n=bound|1
    while len(out)<k:
        n-=2
        if n<3: break
        if all(n%d for d in range(3,int(n**0.5)+1,2)) and n%2: out.append(n)
    return out

def sweep(H, N, p):
    out = subprocess.run([GF, str(H), str(N), str(p)], capture_output=True, text=True).stdout
    d = {}
    for line in out.splitlines():
        a = line.split()
        if len(a) == 2: d[int(a[0])] = int(a[1])
    return d

def crt(rs, ms):
    x, M = 0, 1
    for r, p in zip(rs, ms):
        g = pow(M % p, p - 2, p); t = (r - x) % p * g % p; x += M * t; M *= p; x %= M
    return x, M

def lambda_H(H, N, nprimes):
    PR = primes_below(1 << 31, nprimes)
    # each gf_modp builds the full height-H transfer matrix (D_H states ~ order), so
    # concurrency is RAM-bound at large H: 8-way H=13 OOM'd gympie (24GB). Cap via
    # POLY_MAX_WORKERS for the big heights.
    nproc = min(len(PR), os.cpu_count() or 4,
                int(os.environ.get("POLY_MAX_WORKERS", 8)))
    with Pool(nproc) as pool:
        res = pool.starmap(sweep, [(H, N, p) for p in PR])
    M = 1
    for p in PR: M *= p
    B = {}
    for n in res[0]:
        B[n], _ = crt([res[k][n] for k in range(len(PR))], PR)
    ns = [n for n in sorted(B) if B[n] > 0]
    # wrap guard: exact B_H(n) must be positive and below M/2
    maxB = max(B[n] for n in ns)
    wrapped = maxB > M // 2 or any(B[n] < 0 for n in B)
    # log-linear slope on the tail (primary): log B(n) ~ n log(lambda) + const
    tail = [n for n in ns if n >= ns[0] + 2 and n >= N * 0.55]
    x = np.array(tail, float); y = np.array([math.log(B[n]) for n in tail])
    slope = np.polyfit(x, y, 1)[0]; lam_slope = math.exp(slope)
    # Aitken Delta^2 on raw ratios (geometric acceleration), last few
    r = [B[n] / B[n - 1] for n in ns if n - 1 in B and B[n - 1] > 0]
    def aitken(s):
        return [s[i] - (s[i+1]-s[i])**2 / (s[i+2]-2*s[i+1]+s[i])
                for i in range(len(s)-2) if abs(s[i+2]-2*s[i+1]+s[i]) > 1e-12]
    a1 = aitken(r); a2 = aitken(a1) if len(a1) >= 3 else a1
    lam_ait = a2[-1] if a2 else (a1[-1] if a1 else r[-1])
    return dict(lam_slope=lam_slope, lam_aitken=lam_ait, r_last=r[-1],
                nterms=len(ns), maxB_digits=len(str(maxB)), M_digits=len(str(M//2)),
                wrapped=wrapped)

if __name__ == "__main__":
    H = int(sys.argv[1]); N = int(sys.argv[2])
    nprimes = int(sys.argv[3]) if len(sys.argv) > 3 else max(6, int(N * 0.09) + 4)
    d = lambda_H(H, N, nprimes)
    print(f"H={H} N={N} primes={nprimes} terms={d['nterms']} "
          f"coeff_digits={d['maxB_digits']}/{d['M_digits']} wrapped={d['wrapped']}")
    print(f"  lambda_H: slope={d['lam_slope']:.5f}  aitken={d['lam_aitken']:.5f}  "
          f"raw_r_last={d['r_last']:.5f}")
