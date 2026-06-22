#!/usr/bin/env python3
# T1 general case: the open lemma (3a) "N_H irreducible over Q for ALL H" is implied by the
# sharper, cleaner conjecture Gal(N_H) = S_{deg N_H} (the strip Perron eigenvalue is a
# primitive element with the largest possible Galois group). We can't prove it, but the
# mod-p factorization of N_H IS the Frobenius cycle type at p (Dedekind), so Chebotarev lets
# us TEST Gal = S_d statistically -- all mod p, no rational blowup. Under S_d:
#   - irreducible reductions (a d-cycle Frobenius) at density 1/d,
#   - >=1 linear factor (a fixed point) at density 1 - 1/e ~ 0.632,
#   - both permutation parities appear  <=>  disc(N_H) is not a square  <=>  Gal not in A_d.
import re
import sys
from collections import Counter

from sympy import Poly, symbols, nextprime

x = symbols('x')

Q = {}
H = None
for line in open('results/fixed_height_gfs.txt'):
    m = re.match(r'H=(\d+)', line)
    if m:
        H = int(m.group(1))
    if line.strip().startswith('Q:'):
        body = line.split('Q:')[1].strip().strip('[]')
        Q[H] = [int(c.strip()) for c in body.split(',')]

DEG = {3: 4, 4: 9, 5: 29, 6: 68, 7: 181}


def Pmod(coeffs, p):
    return Poly(list(reversed(coeffs)), x, modulus=p)


def atom_mod_p(H, p):
    g = Pmod(Q[H], p)
    for k in (H + 1, H + 2):
        g = g.gcd(Pmod(Q[k], p))
    return g


# (H, #primes) -- fewer primes for the big (slow-to-factor) atoms
PLAN = [(3, 600), (4, 600), (5, 300), (6, 80), (7, 40)]
if len(sys.argv) > 1:
    PLAN = [(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 200)]

print(" H   deg   #p   irreducible (1/d)    fixed-pt (.632)   odd-perms (.5)   verdict")
for H, NP in PLAN:
    d = DEG[H]
    p = 50000
    irr = fix = odd = used = 0
    ctypes = Counter()
    while used < NP:
        p = nextprime(p)
        g = atom_mod_p(H, p)
        if g.degree() != d:
            continue
        degs = tuple(sorted(f.degree() for f, m in g.factor_list()[1] for _ in range(m)))
        used += 1
        ctypes[degs] += 1
        if degs == (d,):
            irr += 1
        if 1 in degs:
            fix += 1
        if (d - len(degs)) % 2 == 1:
            odd += 1
    pi, pf, po = irr / used, fix / used, odd / used
    # S_d predictions
    from math import e
    ok_irr = abs(pi - 1 / d) < 1.5 / d ** 0.5 / used ** 0.5 + 0.6 / d
    ok_fix = abs(pf - (1 - 1 / e)) < 0.12
    ok_odd = po > 0.15  # both parities present => disc non-square => Gal not subset A_d
    verdict = "consistent with S_%d" % d if (ok_fix and ok_odd and pi > 0) else "review"
    print(f" {H}  {d:4d}  {used:4d}   {pi:.4f} ({1/d:.4f})    "
          f"{pf:.3f} (.632)     {po:.3f}          {verdict}")
