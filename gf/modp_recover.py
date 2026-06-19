#!/usr/bin/env python3
"""Recover the exact integer recurrence / generating function of the fixed-height
polyplet rows B_H(n), via the mod-p transfer matrix (build/gf_modp).

For each of several primes p: generate B_H(n) mod p, run Berlekamp-Massey mod p to
get the minimal recurrence mod p. The order agrees across primes (= the true
order, barring an unlucky prime). CRT the coefficients to lift to the exact
integer recurrence, then validate it against a fresh prime's sequence.

Usage:  python3 gf/modp_recover.py [Hmax]
"""
import sys, subprocess, os
from functools import reduce

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GF = os.path.join(ROOT, "build", "gf_modp")

def _isprime(n):
    if n < 2: return False
    d = n - 1; r = 0
    while d % 2 == 0: d //= 2; r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def _primes_below(below, count):
    out = []; n = below - 1
    while len(out) < count:
        if _isprime(n): out.append(n)
        n -= 2
    return out

# Verified prime moduli just under 2^31. The fixed-height GF coefficients grow
# fast (max|coeff| roughly squares per height: ~1e11 at H=6, ~5e55 at H=8), so the
# CRT modulus must outrun them -- use a large pool. (A composite modulus, e.g. the
# tempting 2147483479, silently breaks the modular inverse, so all are MR-checked.)
PRIMES = _primes_below(1 << 31, 40)
VAL_PRIME = _primes_below(1 << 30, 1)[0]   # fresh prime for validation, disjoint

def seq_modp(H, N, p):
    out = subprocess.run([GF, str(H), str(N), str(p)], capture_output=True, text=True).stdout
    d = {0: 0}
    for line in out.split("\n"):
        q = line.split()
        if len(q) == 2: d[int(q[0])] = int(q[1])
    return [d[n] for n in range(N + 1)]

def bm_modp(s, p):
    C = [1]; B = [1]; L = 0; m = 1; b = 1
    for n in range(len(s)):
        d = s[n]
        for i in range(1, L + 1): d = (d + C[i] * s[n - i]) % p
        if d == 0:
            m += 1
        elif 2 * L <= n:
            T = C[:]; coef = d * pow(b, p - 2, p) % p
            while len(C) < len(B) + m: C.append(0)
            for i in range(len(B)): C[i + m] = (C[i + m] - coef * B[i]) % p
            L = n + 1 - L; B = T; b = d; m = 1
        else:
            coef = d * pow(b, p - 2, p) % p
            while len(C) < len(B) + m: C.append(0)
            for i in range(len(B)): C[i + m] = (C[i + m] - coef * B[i]) % p
            m += 1
    return C, L

def order_of(C):
    return max((i for i, c in enumerate(C) if c != 0), default=0)

def find_order(H):
    """Grow N until Berlekamp-Massey's order is comfortably below N/2."""
    N = 64
    while True:
        s = seq_modp(H, N, PRIMES[0])
        _, L = bm_modp(s, PRIMES[0])
        if L < N // 2 - 8 or N > 60000:
            return order_of(bm_modp(s, PRIMES[0])[0]), N
        N *= 2

def crt(rems, mods):
    x, M = 0, 1
    for r, p in zip(rems, mods):
        # solve x' = x (mod M), x' = r (mod p)
        g = pow(M % p, p - 2, p)
        t = (r - x) % p * g % p
        x += M * t; M *= p
        x %= M
    return x, M

def sym(x, M):
    return x - M if x > M // 2 else x

def main():
    # usage: modp_recover.py [Hmax] [Hmin] [nprimes]
    #   Hmin>1 appends to the existing file; nprimes enlarges the CRT pool for high
    #   H (coeffs ~square per height: H=11 ~1e445 needs ~48 primes, H=12 ~96).
    global PRIMES
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    Hmin = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    if len(sys.argv) > 3:
        PRIMES = _primes_below(1 << 31, int(sys.argv[3]))
    path = sys.argv[4] if len(sys.argv) > 4 else \
        os.path.join(ROOT, "results", "fixed_height_gfs.txt")
    out = open(path, "a" if Hmin > 1 else "w")
    if Hmin == 1:
        out.write("# Fixed-height polyplet generating functions G_H(x) = P_H(x)/Q_H(x)\n")
        out.write("# B_H(n) = fixed polyplets of n cells, bounding-box height exactly H.\n")
        out.write("# Recovered by mod-p transfer matrix + Berlekamp-Massey + CRT; validated.\n")
        out.write("# Format per height:  P: <numerator coeffs, low->high>\n")
        out.write("#                     Q: <denominator coeffs, low->high, Q[0]=1>\n\n")
    for H in range(Hmin, Hmax + 1):
        order, _ = find_order(H)
        N = 2 * order + 30
        # CRT pool must outrun the coefficients: log10|coeff| ~ 0.078 * deg (roots
        # ~ lambda^deg), so primes needed ~ deg/110. Auto-grow if under-provisioned
        # (40 primes silently failed H=10, deg 5005 ~ 1e390 > 40-prime ceiling).
        need = order // 110 + 12
        if len(PRIMES) < need:
            PRIMES = _primes_below(1 << 31, need)
        seqs = [seq_modp(H, N, p) for p in PRIMES]
        Cs = [bm_modp(seqs[k], PRIMES[k]) for k in range(len(PRIMES))]
        Ls = [order_of(C) for C, _ in Cs]
        if len(set(Ls)) != 1:
            print(f"H={H}: order disagreement across primes {Ls} -- rerun", flush=True)
            continue
        d = Ls[0]
        # denominator Q[0..d] by CRT (Q[0]=1), symmetric lift
        Q = [1] + [sym(*crt([Cs[k][0][i] for k in range(len(PRIMES))], PRIMES))
                   for i in range(1, d + 1)]
        # numerator P[k] = sum_{i<=min(k,d)} Q[i] B_H(k-i), deg P <= d, also by CRT
        P = []
        for k in range(d + 1):
            rems = [sum(Q[i] % p * seqs[ki][k - i] for i in range(min(k, d) + 1)) % p
                    for ki, p in enumerate(PRIMES)]
            P.append(sym(*crt(rems, PRIMES)))
        while len(P) > 1 and P[-1] == 0: P.pop()       # trim leading-zero high terms
        # validate the FULL GF against a fresh prime: expand P/Q as a power series
        # and compare to the engine's sequence.
        vp = VAL_PRIME
        sv = seq_modp(H, N, vp)
        b = [0] * (N + 1)
        for n in range(N + 1):
            v = (P[n] if n < len(P) else 0)
            for i in range(1, d + 1):
                if n - i >= 0: v -= Q[i] * b[n - i]
            b[n] = v % vp
        ok = all(b[n] == sv[n] % vp for n in range(N + 1))
        print(f"H={H}: order {d}  full-GF-validated:{ok}  "
              f"deg P={len(P)-1}  P[:4]={P[:4]}", flush=True)
        out.write(f"H={H}  order={d}  validated={ok}\n")
        out.write(f"P: {P}\n")
        out.write(f"Q: {Q}\n\n")
        out.flush()
    out.close()

if __name__ == "__main__":
    main()
