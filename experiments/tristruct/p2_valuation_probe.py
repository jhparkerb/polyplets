#!/usr/bin/env python3
"""p2_valuation_probe.py -- valuation probes on the banked triangle, beyond
the sweep's residue-pattern space (Proposer 2).

Exact integer arithmetic. Probes:
  V1. v_p(a(n)) for p = 2,3,5,7, n = 1..40 -- printed for the record.
  V2. v_3(T(n,H)) OFF the diagonal-law region (k = n-H > 13): distribution
      by value; cells with v_3 >= 3 listed (structured or scattered?).
  V3. v_2(T(n,H)) distribution over the whole triangle; cells with
      v_2 >= 6 listed.
  V4. alternating row sum F_n(-1) = sum_H (-1)^H T(n,H): residues mod 4, 8
      (triangle-combinations.md covered its size/sign/recurrences, not its
      2-adic residues).
  V5. geometric-mod probe: T(n,H) mod (n) and mod (H): any forced classes?
      (congruences whose modulus depends on the coordinates -- outside the
      sweep's fixed-modulus space). Reported as pass-rate tables only.

Run from experiments/tristruct/:  python3 p2_valuation_probe.py
"""
import os
from collections import Counter
from triangle import Triangle

def vp(x, p):
    if x == 0:
        return -1   # sentinel for zero
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v

def main():
    tri = Triangle.load()

    # V1
    for p in (2, 3, 5, 7):
        print("V1 v_%d(a(n)) n=1..40: %s"
              % (p, [vp(tri.rowsum(n), p) for n in range(1, 41)]))

    # V2
    c = Counter()
    big = []
    for n in range(1, 41):
        for H in range(1, n + 1):
            if n - H > 13:
                v = vp(tri.cell(n, H), 3)
                c[v] += 1
                if v >= 3:
                    big.append((n, H, v))
    print("V2 v_3(T) off diagonal-law region (k>13): %s" % dict(sorted(c.items())))
    print("V2 cells v_3>=3: %s" % big)

    # V3
    c = Counter()
    big = []
    for n in range(1, 41):
        for H in range(1, n + 1):
            v = vp(tri.cell(n, H), 2)
            c[v] += 1
            if v >= 6:
                big.append((n, H, v))
    print("V3 v_2(T) whole triangle: %s" % dict(sorted(c.items())))
    print("V3 cells v_2>=6: %s" % big)

    # V4
    for m in (4, 8):
        res = [sum((-1) ** H * tri.cell(n, H) for H in range(1, n + 1)) % m
               for n in range(1, 41)]
        print("V4 F_n(-1) mod %d, n=1..40: %s" % (m, res))

    # V5
    for label, mod in (("n", lambda n, H: n), ("H", lambda n, H: H)):
        c = Counter()
        for n in range(2, 41):
            for H in range(1, n + 1):
                m = mod(n, H)
                if m >= 2:
                    c[tri.cell(n, H) % m == 0] += 1
        print("V5 T(n,H) == 0 mod %s: %s of %d cells"
              % (label, c[True], c[True] + c[False]))

if __name__ == '__main__':
    main()
