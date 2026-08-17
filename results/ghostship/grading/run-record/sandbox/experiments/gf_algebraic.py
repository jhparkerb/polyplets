#!/usr/bin/env python3
"""Guess an algebraic equation P(t, F) = 0 for a GF from its coefficients.

F(t) = sum a_i t^(i+OFFSET). Search c_{jm}: sum_{j<=D, m<=M} c_{jm} t^m F^j = 0
as a power series, fit on the first part, holdout-validate on the tail.
Exact rational arithmetic. Reads sequence from argv or stdin.

Usage: gf_algebraic.py "1,2,9,..." [OFFSET=2] [D=4] [M=14] [HOLDOUT=5]
"""
import sys
from fractions import Fraction


def series_mul(A, B, N):
    C = [0] * N
    for i, x in enumerate(A):
        if x:
            for j, y in enumerate(B):
                if i + j >= N:
                    break
                if y:
                    C[i + j] += x * y
    return C


def nullspace_all(rows, ncols):
    m = [list(map(Fraction, r)) for r in rows]
    nr = len(m)
    piv = []
    r = 0
    for c in range(ncols):
        pr = next((i for i in range(r, nr) if m[i][c] != 0), None)
        if pr is None:
            continue
        m[r], m[pr] = m[pr], m[r]
        inv = m[r][c]
        m[r] = [x / inv for x in m[r]]
        for i in range(nr):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        piv.append(c)
        r += 1
        if r == nr:
            break
    pivset = set(piv)
    basis = []
    for fc in [c for c in range(ncols) if c not in pivset]:
        v = [Fraction(0)] * ncols
        v[fc] = Fraction(1)
        for i, c in enumerate(piv):
            v[c] = -m[i][fc]
        basis.append(v)
    return basis


def main():
    seq = [int(x) for x in sys.argv[1].replace(",", " ").split()]
    OFF = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    D = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    Mmax = int(sys.argv[4]) if len(sys.argv) > 4 else 14
    HOLD = int(sys.argv[5]) if len(sys.argv) > 5 else 5
    N = len(seq) + OFF          # series precision: t^0 .. t^(N-1)
    F = [0] * N
    for i, a in enumerate(seq):
        if OFF + i < N:
            F[OFF + i] = a
    # powers of F
    pows = [[1] + [0] * (N - 1)]
    for j in range(D):
        pows.append(series_mul(pows[-1], F, N))

    for d in range(1, D + 1):
        for M in range(1, Mmax + 1):
            nvars = (d + 1) * (M + 1)
            neq = N - HOLD
            if neq < nvars + 2:
                continue
            # unknown c_{j,m}; equation: coefficient of t^k of sum c_jm t^m F^j = 0
            rows = []
            for k in range(neq):
                row = []
                for j in range(d + 1):
                    for m in range(M + 1):
                        row.append(pows[j][k - m] if 0 <= k - m < N else 0)
                rows.append(row)
            basis = nullspace_all(rows, nvars)
            for v in basis:
                # holdout check on remaining coefficients
                ok = True
                for k in range(neq, N):
                    tot = Fraction(0)
                    idx = 0
                    for j in range(d + 1):
                        for m in range(M + 1):
                            if 0 <= k - m < N:
                                tot += v[idx] * pows[j][k - m]
                            idx += 1
                    if tot != 0:
                        ok = False
                        break
                if not ok:
                    continue
                # require actual F-dependence (some c_jm != 0 with j >= 1)
                if all(v[j * (M + 1) + m] == 0 for j in range(1, d + 1)
                       for m in range(M + 1)):
                    continue
                from math import lcm, gcd
                L = 1
                for x in v:
                    L = lcm(L, x.denominator)
                iv = [int(x * L) for x in v]
                gg = 0
                for x in iv:
                    gg = gcd(gg, x)
                if gg > 1:
                    iv = [x // gg for x in iv]
                print(f"ALGEBRAIC: F-degree {d}, t-degree {M} "
                      f"(fit {neq} coeffs, holdout {N - neq} OK)")
                for j in range(d + 1):
                    terms = []
                    for m in range(M + 1):
                        c = iv[j * (M + 1) + m]
                        if c:
                            terms.append(f"{c:+d}*t^{m}")
                    if terms:
                        print(f"  [F^{j}] {' '.join(terms)}")
                return
    print(f"NONE up to F-degree {D}, t-degree {Mmax} on {len(seq)} terms")


if __name__ == "__main__":
    main()
