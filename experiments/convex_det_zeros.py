#!/usr/bin/env python3
"""Is nu = 2.5145796... the reciprocal of a zero of the second pole family?

experiments/convex_kernel_zeros.py showed that the four exponentials L7
measures on the unrestricted and staircase series are 1/zeros(K), the first
pole family of the Temperley solution.  L7's descending half grows at
nu = 2.51457964387872... and appears in neither list.

The solution has a second denominator: the determinant of the 2x2 linear
system that closes phase (1,1).  Its zeros are the other poles.  This builds
that determinant as a truncated q-series with the s04 solver's own code, then
looks for its smallest positive zero and compares 1/zero to nu.

    python3 experiments/convex_det_zeros.py [--terms 48]

L7 Open Problem "does the second pole family explain nu?".
"""
from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

SANDBOX = (Path(__file__).resolve().parent.parent / "results" / "ghostship"
           / "grading" / "run-record" / "sandbox" / "experiments")

NU = Fraction(25145796438787291885, 10 ** 19)


def build_det(king: bool, terms: int):
    """The 2x2 determinant of the phase-(1,1) system, as a coefficient list.

    This is the loop of Solver.solve_F11 with the determinant kept instead of
    discarded; everything it calls is the solver's own arithmetic.
    """
    sys.path.insert(0, str(SANDBOX))
    import s04_q_temperley as s04

    s04.QS.N = terms
    sol = s04.Solver(1, 1, king=king)
    sol.solve_F10()

    P = s04.D(s04.QS(), s04.QS())
    Q1 = s04.D(s04.QS(), s04.QS())
    Q2 = s04.D(s04.QS(), s04.QS())
    prod = sol.one
    n = 0
    while n <= s04.QS.N and not prod.is_zero():
        zn1 = sol.Z(n + 1)
        iz1 = (zn1 - 1).inv()
        V1 = zn1 * zn1 * iz1 * iz1
        V2 = zn1 * iz1
        P = P + sol.y ** n * prod * sol.A2_at(n)
        Q1 = Q1 + sol.y ** (n + 1) * prod * V1
        Q2 = Q2 + sol.y ** (n + 1) * prod * V2
        prod = prod * V1
        n += 1
    one = s04.QS.const(1)
    a11, a12 = one + Q1.a, Q2.a
    a21, a22 = Q1.b, one + Q2.b
    det = a11 * a22 - a12 * a21
    return list(det.c)


def evaluate(coeffs, q):
    """Horner.  The coefficients are exact rationals with large numerators, so
    the running power this replaces was the expensive part of the scan."""
    out = Fraction(0)
    for c in reversed(coeffs):
        out = out * q + c
    return out


def smallest_positive_zero(coeffs, lo, hi, step, iters=200):
    q = lo
    prev = evaluate(coeffs, q)
    while q < hi:
        q2 = q + step
        cur = evaluate(coeffs, q2)
        if prev * cur < 0:
            a, b = q, q2
            fa = prev
            for _ in range(iters):
                mid = (a + b) / 2
                fm = evaluate(coeffs, mid)
                if fa * fm > 0:
                    a, fa = mid, fm
                else:
                    b = mid
            return (a + b) / 2
        q, prev = q2, cur
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", type=int, default=48)
    args = ap.parse_args()

    for king in (True, False):
        coeffs = build_det(king, args.terms)
        z = smallest_positive_zero(coeffs, Fraction(1, 100), Fraction(9, 10),
                                   Fraction(1, 200))
        name = "king" if king else "control (polyomino)"
        if z is None:
            print("%-22s no sign change of det on (0.01, 0.9)" % name)
            continue
        inv = 1 / z
        print("%-22s smallest positive zero of det: q = %.18f   1/q = %.18f"
              % (name, float(z), float(inv)))
        if king:
            rel = abs(float(inv) - float(NU)) / float(NU)
            print("%-22s nu = %.18f   relative difference %.3e"
                  % ("", float(NU), rel))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
