#!/usr/bin/env python3
"""Fit F(t) = (sum_j P_j(t) * R_j(t)) / D(t) with polynomial P_j, known
denominator D and known radical series R_j. Exact rationals + holdout.

Radical basis is configured in MODES below. Sequence offset: F = sum a_i t^(i+2)
(semiperimeter GFs here start at t^2).
"""
import sys
from fractions import Fraction


def binom_series(alpha, c, N):
    """(1 + c t)^alpha as Fraction series, length N."""
    out = [Fraction(1)]
    for k in range(1, N):
        out.append(out[-1] * (Fraction(alpha) - (k - 1)) * c / k)
    return out


def mul(A, B, N):
    C = [Fraction(0)] * N
    for i, x in enumerate(A[:N]):
        if x:
            for j, y in enumerate(B[: N - i]):
                if y:
                    C[i + j] += x * y
    return C


def poly_mul_series(p, S, N):
    C = [Fraction(0)] * N
    for m, c in enumerate(p):
        if c:
            for i, s in enumerate(S[: N - m]):
                C[m + i] += c * s
    return C


def solve_fit(target, basis_series, dmax, N, hold):
    """target = sum_j sum_m c_{jm} t^m basis_j  (deg m <= dmax).
    Fit on coefficients 0..N-hold-1, validate on the rest. Returns c or None."""
    nvars = len(basis_series) * (dmax + 1)
    neq = N - hold
    if neq < nvars:
        print(f"  underpowered: {neq} eqs < {nvars} vars")
        return None
    rows, rhs = [], []
    for k in range(neq):
        row = []
        for S in basis_series:
            for m in range(dmax + 1):
                row.append(S[k - m] if 0 <= k - m else Fraction(0))
        rows.append(row)
        rhs.append(target[k])
    # least-norm exact solve via Gaussian elimination on [rows | rhs]
    m_ = [r[:] + [b] for r, b in zip(rows, rhs)]
    nr, nc = len(m_), nvars
    piv = []
    r = 0
    for c in range(nc):
        pr = next((i for i in range(r, nr) if m_[i][c] != 0), None)
        if pr is None:
            continue
        m_[r], m_[pr] = m_[pr], m_[r]
        inv = m_[r][c]
        m_[r] = [x / inv for x in m_[r]]
        for i in range(nr):
            if i != r and m_[i][c] != 0:
                f = m_[i][c]
                m_[i] = [a - f * b for a, b in zip(m_[i], m_[r])]
        piv.append(c)
        r += 1
        if r == nr:
            break
    # consistency: any zero row with nonzero rhs -> no solution
    for i in range(r, nr):
        if all(x == 0 for x in m_[i][:nc]) and m_[i][nc] != 0:
            return None
    sol = [Fraction(0)] * nvars
    for i, c in enumerate(piv):
        sol[c] = m_[i][nc]
    # validate on ALL N coefficients (including holdout)
    for k in range(N):
        tot = Fraction(0)
        idx = 0
        for S in basis_series:
            for m in range(dmax + 1):
                if 0 <= k - m:
                    tot += sol[idx] * S[k - m]
                idx += 1
        if tot != target[k]:
            return None
    return sol


def run(seq, den_roots, radicands, dmax, hold, label):
    """den_roots: list of (c, mult) meaning (1 + c t)^mult in denominator D.
    radicands: list of lists of c's -> radical prod_j sqrt(1 + c_j t)."""
    OFF = 2
    N = len(seq) + OFF
    F = [Fraction(0)] * N
    for i, a in enumerate(seq):
        F[OFF + i] = Fraction(a)
    # D(t) as series-free polynomial
    D = [Fraction(1)]
    for c, mult in den_roots:
        for _ in range(mult):
            D = [a + (Fraction(c) * b if b is not None else 0)
                 for a, b in zip(D + [Fraction(0)], [None] + D)]
    target = poly_mul_series(D, F, N)
    basis = []
    names = []
    for rad in radicands:
        S = [Fraction(1)] + [Fraction(0)] * (N - 1)
        nm = []
        for c in rad:
            S = mul(S, binom_series(Fraction(1, 2), c, N), N)
            nm.append(f"sqrt(1{'+' if c > 0 else ''}{c}t)")
        basis.append(S)
        names.append("*".join(nm) if nm else "1")
    sol = solve_fit(target, basis, dmax, N, hold)
    print(f"== {label}: D = " + " * ".join(f"(1{'+' if c>0 else ''}{c}t)^{m}" for c, m in den_roots))
    if sol is None:
        print("  NO FIT")
        return None
    print(f"  FIT OK (all {N} coeffs incl. {hold} holdout)")
    idx = 0
    for nm in names:
        terms = []
        for m in range(dmax + 1):
            c = sol[idx]
            idx += 1
            if c:
                terms.append(f"({c})t^{m}")
        print(f"  [{nm}] " + (" + ".join(terms) if terms else "0"))
    return sol


if __name__ == "__main__":
    seq = [int(x) for x in open(sys.argv[1]).read().replace(",", " ").split()]
    mode = sys.argv[2] if len(sys.argv) > 2 else "king"
    if mode == "control":
        run(seq, [(-4, 2)], [[], [-4]], 8, 6, "control: (1-4t)^2 F = A + B sqrt(1-4t)")
    else:
        # king: singularities 1/4 (double), -1/2
        for den in ([(-4, 2), (2, 1)], [(-4, 2), (2, 2)], [(-4, 3), (2, 2)]):
            for rads in ([[], [-4]],
                         [[], [-4], [2], [-4, 2]],
                         [[], [-4, 2]]):
                lbl = f"king rads={rads}"
                if run(seq, den, rads, 10, 6, lbl) is not None:
                    sys.exit(0)
        print("king: no ansatz fit")
