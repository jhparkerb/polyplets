#!/usr/bin/env python3
"""Verify the atom-factorization structure of the polyplet triangle.

Claim (from triangle_relations2.py measurements):
  C_H(n) := sum_{h<=H} (H-h+1) T(n,h)   (naive height-H strip TM count)
  satisfies a minimal recurrence with char poly q_H ("atom"),
  orders 1,2,4,9,(29,68,...); and since
  T(n,H) = C_H(n) - 2 C_{H-1}(n) + C_{H-2}(n),
  the column char poly factors as p_H = q_H * q_{H-1} * q_{H-2}
  (orders 3=2+1, 7=4+2+1, 15=9+4+2).

This script computes q_1..q_4 and p_2..p_4 from the data and checks the
products exactly, plus that the q's are pairwise coprime (no shared roots).
"""
import os, sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from triangle_relations import load_triangle, col_seq, find_min_recurrence, NMAX
from triangle_relations2 import charpoly


def polymul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def polygcd(a, b):
    a, b = [F(x) for x in a], [F(x) for x in b]
    while b and any(x != 0 for x in b):
        # a mod b
        r = a[:]
        while len(r) >= len(b) and any(x != 0 for x in r):
            if r[0] == 0:
                r = r[1:]
                continue
            f = r[0] / b[0]
            for j in range(len(b)):
                r[j] -= f * b[j]
            r = r[1:]
        a, b = b, r
    # normalize
    while a and a[0] == 0:
        a = a[1:]
    if a:
        a = [x / a[0] for x in a]
    return a


def main():
    T = load_triangle()
    # atoms from strip cumulative sequences
    q = {0: [F(1)]}  # empty product for H=0
    for H in range(1, 5):
        seq = [sum((H - h + 1) * T.get((n, h), 0) for h in range(1, H + 1))
               for n in range(1, NMAX + 1)]
        d, c, ho = find_min_recurrence(seq)
        q[H] = charpoly(c)
        print(f"q_{H} (order {d}, holdout {ho}): "
              + " ".join(str(x) for x in q[H]))
    # column char polys
    print()
    for H in range(2, 5):
        seq = col_seq(T, H)
        d, c, ho = find_min_recurrence(seq)
        pH = charpoly(c)
        prod = polymul(polymul(q[H], q[H - 1]), q[H - 2] if H >= 2 else [F(1)])
        match = (len(prod) == len(pH)
                 and all(a == b for a, b in zip(prod, pH)))
        print(f"p_{H} == q_{H} * q_{H-1} * q_{H-2}: {'YES' if match else 'NO'}"
              f"  (order {d})")
    # pairwise coprimality of atoms
    print()
    for a in range(1, 5):
        for b in range(a + 1, 5):
            g = polygcd(q[a], q[b])
            co = len(g) == 1
            print(f"gcd(q_{a}, q_{b}) = {'1 (coprime)' if co else g}")


if __name__ == "__main__":
    main()
