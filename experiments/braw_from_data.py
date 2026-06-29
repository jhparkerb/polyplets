#!/usr/bin/env python3
"""Extract the per-row growth series B(y) of the height-diagonal defect gas
directly from the a(21) triangle -- no enumeration needed.

lambda_raw(y) = Z_N(y)/Z_{N-1}(y),  Z_N(y) = sum_e T(N+e,N) y^e   (fixed height N).
This is the *wide* slice of the triangle (T(20,8) exists where the constant-excess
diagonal T(n,n-8) would need n=25), and lambda_raw converges in N, so a fixed n=21
triangle yields 9 converged terms -- two past the diagonal fit. See
docs/proofs/T-n-nm2-and-general.md sec.5. Result: no low-complexity closed form
(B(y) parked as a pure-math open question).

Run:  python3 experiments/braw_from_data.py
"""
from fractions import Fraction

DATA = "results/ns_a21/perheight"   # h{N}.out: lines "n' T(n',N)"
NMAX = 21

def Trow(N):
    d = {}
    for line in open(f"{DATA}/h{N}.out"):
        p = line.split()
        if len(p) == 2:
            d[int(p[0])] = int(p[1])
    return d

ROWS = {N: Trow(N) for N in range(1, NMAX + 1)}

def ZN(N, K):
    return [Fraction(ROWS[N].get(N + e, 0)) for e in range(K + 1)]

def divseries(num, den, K):
    q = [Fraction(0)] * (K + 1)
    for i in range(K + 1):
        q[i] = (num[i] - sum(den[j] * q[i - j] for j in range(1, i + 1))) / den[0]
    return q

def logseries(f, K):
    g = [Fraction(0)] * (K + 1)
    for i in range(1, K + 1):
        s = Fraction(i) * f[i]
        for j in range(1, i):
            s -= Fraction(j) * g[j] * f[i - j]
        g[i] = s / (Fraction(i) * f[0])
    return g

def converged(coeff_at_N):
    """Given {N: value}, return the value once it stabilises in N, else None."""
    Ns = sorted(coeff_at_N)
    for i in range(1, len(Ns)):
        if coeff_at_N[Ns[i]] == coeff_at_N[Ns[i - 1]]:
            return coeff_at_N[Ns[i]], Ns[i] - 1
    return None

if __name__ == "__main__":
    K = 13
    lam, braw = [], []
    print("k :  b_raw_k (converged)                       lambda_raw_k        N>=")
    for k in range(1, K + 1):
        bvals, lvals = {}, {}
        for N in range(max(2, k), NMAX - k + 1):   # Z_N known to order 21-N
            lam_s = divseries(ZN(N, k), ZN(N - 1, k), k)
            lvals[N] = lam_s[k]
            bvals[N] = logseries(lam_s, k)[k]
        cb, cl = converged(bvals), converged(lvals)
        if cb is None:
            print(f"{k:2d}:  NOT converged within a(21)")
            break
        braw.append(cb[0]); lam.append(cl[0])
        print(f"{k:2d}:  {str(cb[0]):40s}  {str(cl[0]):18s}  {cb[1]}")
    print()
    print("lambda_raw =", ['3'] + [str(c) for c in lam])
    print("b_raw      =", [str(c) for c in braw])
