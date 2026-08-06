#!/usr/bin/env python3
"""Cheap probe: is a(n) mod p (A006770) C-finite / algebraic-looking?

Berlekamp-Massey over F_p on the 40 banked terms, for p in {2,3,5,7,11,13}.
Also prints the residue strings so patterns are eyeballable, and runs the
same probe on the height-triangle row sums restricted to fixed H (control:
those ARE C-finite, so BM must succeed there -- that validates the probe).
"""

def read_bfile(path):
    a = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        k, v = line.split()
        a[int(k)] = int(v)
    return [a[i] for i in range(1, max(a) + 1)]


def bm(seq, p):
    """Berlekamp-Massey over F_p. Returns minimal LFSR poly C (list)."""
    C = [1]; B = [1]; L = 0; m = 1; b = 1
    for n in range(len(seq)):
        d = seq[n] % p
        for i in range(1, L + 1):
            d = (d + C[i] * seq[n - i]) % p
        if d == 0:
            m += 1
        elif 2 * L <= n:
            T = C[:]
            coef = d * pow(b, p - 2, p) % p
            while len(C) < len(B) + m:
                C.append(0)
            for i in range(len(B)):
                C[i + m] = (C[i + m] - coef * B[i]) % p
            L, B, b, m = n + 1 - L, T, d, 1
        else:
            coef = d * pow(b, p - 2, p) % p
            while len(C) < len(B) + m:
                C.append(0)
            for i in range(len(B)):
                C[i + m] = (C[i + m] - coef * B[i]) % p
            m += 1
    return C, L


def check(seq, p, C, L):
    """How many terms past 2L does the recurrence predict correctly?"""
    ok = 0
    for n in range(L, len(seq)):
        s = 0
        for i in range(1, L + 1):
            s = (s + C[i] * seq[n - i]) % p
        if (-s) % p == seq[n] % p:
            ok += 1
        else:
            break
    return ok


a = read_bfile('results/b006770_upload.txt')
print("terms:", len(a))
for p in (2, 3, 5, 7, 11, 13):
    r = [x % p for x in a]
    C, L = bm(r, p)
    ok = check(r, p, C, L)
    holdout = len(a) - 2 * L
    print(f"p={p:3d}  order L={L:3d}  terms={len(a)}  holdout={holdout:3d}  "
          f"consecutive-correct-from-L={ok}")
    print(f"       a(n) mod {p}: {''.join(str(x) for x in r)}")
