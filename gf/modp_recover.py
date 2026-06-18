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

# verified-prime moduli near 2^31 (Miller-Rabin checked; 2147483479 is COMPOSITE
# and was removed -- a non-prime modulus breaks the modular inverse in CRT/BM)
PRIMES = [2147483647, 2147483629, 2147483587, 2147483563, 2147483549, 2147483477]

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

def main():
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    for H in range(1, Hmax + 1):
        order, _ = find_order(H)
        N = 2 * order + 30
        # recover the recurrence mod each prime (pad to a common length)
        Cs, Ls = [], []
        for p in PRIMES:
            C, L = bm_modp(seq_modp(H, N, p), p)
            Cs.append(C); Ls.append(order_of(C))
        if len(set(Ls)) != 1:
            print(f"H={H}: order disagreement across primes {Ls} -- rerun", flush=True)
            continue
        d = Ls[0]
        # CRT each coefficient C[1..d] (C[0]=1); symmetric lift
        coeffs = [1]
        Mtot = reduce(lambda a, b: a * b, PRIMES)
        for i in range(1, d + 1):
            x, M = crt([Cs[k][i] for k in range(len(PRIMES))], PRIMES)
            coeffs.append(x - M if x > M // 2 else x)
        # validate against a fresh prime not used in the CRT. The recurrence holds
        # for n > deg(numerator); deg P <= deg Q = d for these proper rational GFs,
        # so check from n = d+1 onward.
        vp = 2147483423
        sv = seq_modp(H, N, vp)
        ok = all((sum(coeffs[i] * sv[n - i] for i in range(d + 1))) % vp == 0
                 for n in range(d + 1, len(sv)))
        print(f"H={H}: order {d}  validated:{ok}  denom Q_H = {coeffs}", flush=True)

if __name__ == "__main__":
    main()
