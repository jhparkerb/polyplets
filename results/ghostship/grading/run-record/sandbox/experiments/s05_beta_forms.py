#!/usr/bin/env python3
"""Session 05, step 1: q-Pochhammer NORMAL FORM for the Temperley
denominator 1 - beta(1) at x=y=1, both modes, verified symbolically
against the s04 solver's own beta series.

Claim being established (then used for the asymptotics):

  king:    1 - beta(q) = K(q) := sum_{m>=0} (-1)^m (2-q^m) q^{m(m+1)/2} / (q;q)_m^2
  control: 1 - beta(q) = J(q) := sum_{m>=0} (-1)^m         q^{m(m+1)/2} / (q;q)_m^2

where (q;q)_m = prod_{j=1}^m (1-q^j).  Both are entire-in-the-disk
q-series; J is the classical q-Bessel-type function of Bousquet-Melou's
convex-polyomino area solutions, and K(q) = 2*J(1;q) - J(q;q) for
J(x;q) = sum (-1)^m x^m q^{m(m+1)/2}/(q;q)_m^2.

Derivation (from s04_q_temperley.py's solve_F10 loop, x=y=1):
  beta = sum_{n>=0} T(q^{n+1}) prod_{j=1}^n R(q^j),
  R(z) = z/((z-1)(1-z)) = -z/(1-z)^2,
  T(z) = (z(z-1)-z)/((z-1)(1-z)) = z(2-z)/(1-z)^2   [king]
       = -z/((z-1)(1-z))         = z/(1-z)^2         [control]
  => prod_{j=1}^n R(q^j) = (-1)^n q^{n(n+1)/2}/(q;q)_n^2
  => beta = sum_{m>=1} (-1)^{m-1} q^{m(m+1)/2} (2-q^m)/(q;q)_m^2   [king]
     beta = sum_{m>=1} (-1)^{m-1} q^{m(m+1)/2}        /(q;q)_m^2   [control]
  and 1-beta absorbs the m=0 term (=1 resp. 2-1=1) into the sum.

This script verifies the normal form as an exact series identity in q to
order N=40 against the solver's beta (obtained by re-running the s04
solve_F10 loop verbatim with alpha/beta exposed), and re-runs the full s04
validation suite (VERIFY of s04 claims 1-2).
"""
import sys, os, time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from s04_q_temperley import QS, D, Solver, series_ints, MIRAGE_KING  # noqa


class XSolver(Solver):
    """s04 Solver with alpha/beta exposed (loop copied verbatim)."""

    def solve_F10(self):
        f0 = self.F00_at(0)
        self.F001, self.F00p1 = f0.a, f0.b
        alpha = D(QS(), QS())
        beta = D(QS(), QS())
        prod = self.one
        n = 0
        while n <= QS.N and not prod.is_zero():
            alpha = alpha + self.y ** n * prod * self.A1_at(n)
            beta = beta + self.y ** (n + 1) * prod * self.T_at(n + 1)
            prod = prod * self.R_at(n + 1)
            n += 1
        self.alpha, self.beta = alpha, beta
        self.F101 = alpha.a * (QS.const(1) - beta.a).inv()
        self.F10p1 = alpha.b + beta.b * self.F101


def qpoch_sq_inv(m, N):
    """1/(q;q)_m^2 as a QS."""
    p = QS.const(1)
    for j in range(1, m + 1):
        p = p * (QS.const(1) - QS.mono(j))
    return (p * p).inv()


def normal_form(N, king):
    """1 - beta as the claimed sum, truncated at q^N (m up to triangular)."""
    out = QS()
    m = 0
    while m * (m + 1) // 2 <= N:
        w = qpoch_sq_inv(m, N)
        coef = QS.mono(m * (m + 1) // 2)
        if king:
            two_minus = QS.const(2) - QS.mono(m)
            term = coef * two_minus * w
        else:
            term = coef * w
        out = out + term.scal((-1) ** m)
        m += 1
    return out


def main():
    N = 40
    QS.N = N
    print(f"== normal form check, series to q^{N}, x=y=1 ==")
    for king in (True, False):
        tag = "king" if king else "control"
        s = XSolver(1, 1, king=king)
        s.solve_F10()
        one_minus_beta = QS.const(1) - s.beta.a
        nf = normal_form(N, king)
        diff = one_minus_beta - nf
        ok = diff.is_zero()
        print(f"  {tag}: (1-beta) == {'K' if king else 'J'}(q) "
              f"to q^{N}: {'OK' if ok else 'FAIL'}")
        if not ok:
            print("    1-beta:", one_minus_beta.c[:12])
            print("    normal:", nf.c[:12])
            sys.exit(1)

    # cross-check the K = 2*J(1;q) - J(q;q) presentation (king)
    QS.N = N
    Jq = QS()   # J(q;q) = sum (-1)^m q^{m(m+1)/2} q^m /(q;q)_m^2
    J1 = QS()
    m = 0
    while m * (m + 1) // 2 <= N:
        w = qpoch_sq_inv(m, N)
        J1 = J1 + (QS.mono(m * (m + 1) // 2) * w).scal((-1) ** m)
        Jq = Jq + (QS.mono(m * (m + 1) // 2 + m) * w).scal((-1) ** m)
        m += 1
    s = XSolver(1, 1, king=True)
    s.solve_F10()
    diff = (QS.const(1) - s.beta.a) - (J1.scal(2) - Jq)
    print(f"  king: 1-beta == 2*J(1;q) - J(q;q) to q^{N}: "
          f"{'OK' if diff.is_zero() else 'FAIL'}")
    if not diff.is_zero():
        sys.exit(1)

    # VERIFY s04: rerun the full s04 validation suite
    print("\n== VERIFY s04 (full rerun of s04_q_temperley checks) ==")
    t0 = time.time()
    import s04_q_temperley
    s04_q_temperley.main()
    print(f"(rerun wall time {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
