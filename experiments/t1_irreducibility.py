#!/usr/bin/env python3
# T1 (lifetime-3): push the verification of the one open lemma -- (3a) "the unanchored
# strip atom N_H is irreducible over Q" -- past the proof's H<=6 ceiling, via mod-p.
# N_H = gcd(Q_H, Q_{H+1}, Q_{H+2}); the rational gcd blows up (why the proof stopped at 6),
# but mod p it is cheap. Two things mod p: (a) deg N_H mod p directly confirms the atom
# degree (atom_degrees.py EXTRAPOLATES H>=8; this DE-extrapolates deg N_8=462); (b) if
# N_H mod p is irreducible for some p, then N_H is irreducible over Q -> (3a) for that H.
import re
import sys
import time

from sympy import Poly, symbols
from sympy import nextprime

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

EXPECT = {7: 181, 8: 462}    # deg N_H (7 verified in the proof; 8 was extrapolated)


def Pmod(coeffs, p):         # low->high integer coeffs -> monic-capable Poly over GF(p)
    return Poly(list(reversed(coeffs)), x, modulus=p)


def atom_mod_p(H, p):
    g = Pmod(Q[H], p)
    for k in (H + 1, H + 2):
        g = g.gcd(Pmod(Q[k], p))
    return g


def subset_sums(degs):
    reach = {0}
    for d in degs:
        reach |= {r + d for r in reach}
    return reach


# Q_H squarefree (the proof's other H<=6 claim): gcd(Q_H, Q_H') is constant. Squarefree
# mod p => squarefree over Q (a square factor over Q would survive reduction at a good p).
# Blowup-free, so it runs for every available H (here H<=10).
def squarefree_check(p=100003):
    print(f"Q_H squarefree mod p={p} (extends the proof's H<=6):")
    for H in sorted(Q):
        f = Pmod(Q[H], p)
        sf = f.gcd(f.diff(x)).degree() == 0
        print(f"  H={H:2d}: deg Q={len(Q[H]) - 1:4d}  squarefree: {sf}")


# Rigorous mod-p irreducibility certificate: any rational factor of N_H of degree k
# (0<k<deg) reduces, mod EVERY prime, to a set of mod-p factors whose degrees sum to k.
# So k must be a subset-sum of the mod-p factor degrees for every prime. Intersect those
# subset-sum sets over several primes; if only {0, deg} survive, N_H has no proper rational
# factor -> IRREDUCIBLE over Q. (No need for the rare prime that is irreducible outright.)
squarefree_check()
print()
targets = [int(a) for a in sys.argv[1:]] or [7]
NPRIMES = 8
for H in targets:
    exp = EXPECT[H]
    print(f"=== H={H}: atom N_H, expected degree {exp} ===")
    p = 100003
    common = None
    used = 0
    for _ in range(NPRIMES):
        p = nextprime(p)
        t0 = time.time()
        g = atom_mod_p(H, p)
        d = g.degree()
        if d != exp:
            print(f"  p={p}: deg = {d} != {exp} (unfaithful prime; skip)")
            continue
        degs = [f.degree() for f, m in g.factor_list()[1] for _ in range(m)]
        ss = subset_sums(degs)
        common = ss if common is None else (common & ss)
        used += 1
        proper = sorted(common - {0, exp})
        print(f"  p={p}: deg={d} OK, factor degrees={sorted(degs)}  "
              f"[surviving proper subset-sums: {len(proper)}]  [{time.time()-t0:.1f}s]")
        if not proper:
            print(f"  >>> N_{H} IRREDUCIBLE over Q (rigorous, {used} primes): no proper "
                  f"rational-factor degree survives. Lemma (3a) PROVED for H={H}.")
            break
    else:
        rem = sorted((common or set()) - {0, exp})
        print(f"  H={H}: not yet certified; surviving candidate factor degrees {rem[:20]}"
              f"{'...' if len(rem) > 20 else ''} ({len(rem)}). More/diverse primes needed.")
