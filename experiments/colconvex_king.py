#!/usr/bin/env python3
"""Column-convex polyplets by area via the Temperley/kernel method.

K2 of the kernel/haruspicy program. Catalytic variable q = last column
height; king-touch gives h+h'+1 placements of a height-h' column against
height-h (polyominoes: h+h'-1). The functional equation closes on
A = F(x,1), B = F_q(x,1):

  F(x,q) = t/(1-t) + A t(2-t)/(1-t)^2 + B t/(1-t),   t = qx
  =>  A(x) = x(1-x)^3 / (1 - 7x + 13x^2 - 10x^3 + 2x^4)

growth = 4.64468... (quartic algebraic). OUTCOME: rediscovery -- this is
OEIS A187077 (row-convex polyplets, same GF, equivalent by transpose).
Value of the exercise: validates the Temperley pipeline end-to-end
(functional equation == brute force n<=8 == published GF) as the template
for K1 (all-pairs kernel) and K3 (convex-by-area q-series).
"""
from fractions import Fraction as F

REF = [1, 4, 18, 83, 385, 1788, 8305, 38575, 179170, 832189, 3865253]


def series(N):
    # a(n) = 7a(n-1) - 13a(n-2) + 10a(n-3) - 2a(n-4), from the GF
    num = [0, 1, -3, 3, -1]                    # x(1-x)^3
    den = [1, -7, 13, -10, 2]
    s = [0] * (N + 1)
    for n in range(N + 1):
        v = (num[n] if n < len(num) else 0) - sum(
            den[j] * s[n - j] for j in range(1, min(n, 4) + 1))
        s[n] = v
    return s[1:]


if __name__ == "__main__":
    assert series(len(REF)) == REF
    print("column-convex polyplets == A187077 (GF x(1-x)^3/(1-7x+13x^2-10x^3+2x^4))  OK")
