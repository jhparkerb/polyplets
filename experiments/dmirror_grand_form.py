#!/usr/bin/env python3
"""Does a grand form hold for the dmirror family? -- docs/time-at-the-bar.md A1.3
step 1, which the item says is the step that decides it.

THE KING STATEMENT (docs/proofs/grand-form.md, a theorem, Lean-complete):

    T(H+k, H) = [y^k]( C(y) * mu(y)^H )

equivalently the cumulants c_j(H) = [y^j] log A_H(y), for
A_H(y) = sum_k T(H+k,H) y^k, are EXACTLY LINEAR in H once H >= j+1.  "Level k
carries exactly two new constants" is that linearity: each c_j contributes
(a_j, b_j) and nothing else.

WHY IT CANNOT TRANSFER AS STATED.  The dmirror diagonal has TWO ground states,
not one: d(S, S) = 2 for every S >= 2 (measured, results/sym_counts.txt) --
the main diagonal and the anti-diagonal, both king-connected and both fixed as
SETS by reflection in the main diagonal.  For fixed k and large S an animal
cannot be within k defects of both spines, since the two spines disagree in
~2S cells, so

    d(S, S+k) = d_main(S, S+k) + d_anti(S, S+k)     (disjoint, S large)

and the grand form is a statement about a SINGLE exponential.  log of a sum of
two exponentials is not linear in S unless the two are proportional.  This is
not speculation: results/dmirror-diagonals.md already measured it -- "The
cumulants u_j, v_j of the exp fit are messy -- expected, since they are the log
of a SUM of families."

So the honest step-1 verdict is that the obstruction is NOT row-locality, which
is what A1.3 expected to write a paragraph about.  It is the two-spine sum, and
that is a much more tractable obstruction because it suggests its own repair.

WHERE THE PARITY COMES FROM, and why it is the same effect as A3.2's.
Reflection in the main diagonal fixes every cell of the main diagonal
pointwise, but reverses the anti-diagonal: (i, S-1-i) -> (S-1-i, i), which is
fixed only when S is odd.  So the anti-spine has a centre cell exactly when S
is odd and none when S is even.  That is the period-2 quasi-polynomiality, and
it is the same mechanism as the through-cell / between-cell axis split that
results/bilateral-parity.md found in A030234.

THE REPAIR THIS TESTS.  If the parity split already separates the two families'
contributions cleanly, then EACH PARITY CLASS ON ITS OWN may satisfy a grand
form with two new constants per level.  That is directly checkable from the
quasi-polynomials: form A^p_S(y) = sum_k P^p_k(S) y^k per parity p, take
log in Q[[y]] with coefficients polynomial in S, and ask whether every cumulant
is linear in S.

THE PAYOFF IF IT HOLDS.  results/dmirror-onset-sharp.md showed T4 cannot be
tested at k = 6 because pinning a degree-6 polynomial needs 7 points and the
odd class has 6.  Under a per-parity grand form, level 6 carries only TWO new
constants given levels below, so it needs 2 points, not 7 -- and there are 7
even and 6 odd.  k = 6 becomes reachable with 5 and 4 holdouts, and T4 gets its
first new test since 2026-07-31.

CONTROLS.
  (a) Planted single-family data -- coefficients read off an exact
      C(y)*mu(y)^S -- must be reported LINEAR.  Otherwise "linear" is not being
      measured.
  (b) Planted two-family data C_A mu_A^S + C_B mu_B^S with mu_A != mu_B must be
      reported NONLINEAR.  Otherwise the test cannot fail and proves nothing.
  (c) The P^p_k used must reproduce the banked leading coefficients 1/k!, the
      same anchor results/dmirror-onset-sharp.md uses.

Usage: python3 experiments/dmirror_grand_form.py

Target machine: ayr or dalby.  Cost: instant, exact rational arithmetic.
"""

import math
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from dmirror_onset_probe import load, analyse  # noqa: E402

KMAX = 5           # levels pinnable with a holdout on banked data


# ---- polynomials in S, as coefficient lists (lowest degree first) ----

def padd(a, b):
    n = max(len(a), len(b))
    return [ (a[i] if i < len(a) else F(0)) + (b[i] if i < len(b) else F(0))
             for i in range(n) ]


def pscale(a, c):
    return [x * c for x in a]


def pmul(a, b):
    if not a or not b:
        return [F(0)]
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def pdeg(a):
    d = -1
    for i, x in enumerate(a):
        if x:
            d = i
    return d


# ---- power series in y, coefficients are polynomials in S ----

def series_log(A, n):
    """log(A) for A[0] a nonzero CONSTANT polynomial, to order y^n.

    Uses L = log(A0) + log(1 + u) with u = A/A0 - 1, expanded as the
    alternating series; every coefficient stays a polynomial in S.
    """
    a0 = A[0]
    assert pdeg(a0) <= 0 and a0[0] != 0, "leading term must be a nonzero constant"
    c = a0[0]
    u = [pscale(t, F(1) / c) for t in A]
    u[0] = [F(0)]                                  # u = A/A0 - 1
    out = [[F(0)] for _ in range(n + 1)]
    term = [[F(1)]] + [[F(0)]] * n                 # u^0
    for m in range(1, n + 1):
        # term <- term * u, truncated
        new = [[F(0)] for _ in range(n + 1)]
        for i in range(n + 1):
            if pdeg(term[i]) < 0:
                continue
            for j in range(1, n + 1 - i):
                if pdeg(u[j]) >= 0:
                    new[i + j] = padd(new[i + j], pmul(term[i], u[j]))
        term = new
        sign = F((-1) ** (m + 1), m)
        for i in range(n + 1):
            if pdeg(term[i]) >= 0:
                out[i] = padd(out[i], pscale(term[i], sign))
    return out


def cumulants(polys, kmax):
    """polys[k] = P_k(S) as a polynomial in S; returns c_j(S), j = 1..kmax."""
    A = [polys[k] for k in range(kmax + 1)]
    L = series_log(A, kmax)
    return {j: L[j] for j in range(1, kmax + 1)}


def report(name, polys, kmax):
    c = cumulants(polys, kmax)
    linear = True
    print("  %s:" % name)
    for j in sorted(c):
        d = pdeg(c[j])
        if d > 1:
            linear = False
        print("     c_%d(S) degree %d   %s" % (j, d, "linear" if d <= 1 else "NOT linear"))
    print("     => %s" % ("GRAND FORM SHAPE" if linear
                          else "no grand form: a cumulant is nonlinear in S"))
    return linear


def synth_single(kmax, mu, C):
    """[y^k](C(y) mu(y)^S) as polynomials in S, for planted series mu, C."""
    # log(C mu^S) = log C + S log mu ; exponentiate to order kmax
    n = kmax
    lmu = series_log([[F(x)] for x in mu] + [[F(0)]] * (n + 1 - len(mu)), n)
    lC = series_log([[F(x)] for x in C] + [[F(0)]] * (n + 1 - len(C)), n)
    L = [padd(lC[j], pmul([F(0), F(1)], lmu[j])) for j in range(n + 1)]
    L[0] = lC[0]                                    # S*log(mu(0)) = 0 since mu0=1
    # exp
    out = [[F(0)] for _ in range(n + 1)]
    out[0] = [F(1)]
    term = [[F(1)]] + [[F(0)]] * n
    fact = F(1)
    for m in range(1, n + 1):
        new = [[F(0)] for _ in range(n + 1)]
        for i in range(n + 1):
            if pdeg(term[i]) < 0:
                continue
            for j in range(1, n + 1 - i):
                if pdeg(L[j]) >= 0:
                    new[i + j] = padd(new[i + j], pmul(term[i], L[j]))
        term = new
        fact *= m
        for i in range(n + 1):
            if pdeg(term[i]) >= 0:
                out[i] = padd(out[i], pscale(term[i], F(1) / fact))
    c0 = F(C[0])
    return [pscale(t, c0) for t in out]


def controls(kmax):
    ok = True
    mu = [1, F(3), F(1, 2), F(-1, 5), F(2, 7), F(1, 3)][:kmax + 1]
    C = [1, F(2), F(-1, 3), F(1, 4), F(5, 6), F(1, 9)][:kmax + 1]
    single = synth_single(kmax, mu, C)
    lin = all(pdeg(v) <= 1 for v in cumulants(single, kmax).values())
    print("RED  (a) planted single family reports LINEAR   %s"
          % ("OK" if lin else "FAILED"))
    ok &= lin

    mu2 = [1, F(1), F(-1, 3), F(2, 5), F(1, 8), F(-1, 4)][:kmax + 1]
    C2 = [1, F(-1), F(1, 2), F(1, 7), F(-2, 3), F(1, 5)][:kmax + 1]
    two = [padd(a, b) for a, b in
           zip(single, synth_single(kmax, mu2, C2))]
    nonlin = any(pdeg(v) > 1 for v in cumulants(two, kmax).values())
    print("RED  (b) planted TWO families report NONLINEAR   %s"
          % ("OK" if nonlin else "FAILED"))
    ok &= nonlin
    return ok


def main():
    kmax = KMAX
    print("Does a grand form hold for the dmirror family?  Controls first.\n")
    if not controls(kmax):
        print("\nCONTROLS FAILED -- nothing below is worth reading")
        return 1

    d = load()
    polys = {0: {}, 1: {}}
    print("\nControl (c): pinned leading coefficients must be 1/k!.")
    okc = True
    for k in range(0, kmax + 1):
        for parity in (0, 1):
            res, err = analyse(d, k, parity)
            if res is None:
                print("  k=%d parity=%d NOT PINNED (%s)" % (k, parity, err))
                okc = False
                continue
            polys[parity][k] = list(res[0])
            if k >= 1:
                want = F(1, math.factorial(k))
                got = res[0][k]
                if got != want:
                    print("  k=%d parity=%d lead %s != %s" % (k, parity, got, want))
                    okc = False
    print("  control (c): %s" % ("OK" if okc else "FAILED"))
    if not okc:
        return 1

    print("\nCumulants of each parity class, c_j(S) = [y^j] log sum_k P_k(S) y^k:")
    lin_even = report("even S", polys[0], kmax)
    lin_odd = report("odd S", polys[1], kmax)

    print("\nVERDICT")
    if lin_even and lin_odd:
        print("  Each parity class has the grand-form shape: every cumulant is")
        print("  linear in S, so level k carries TWO new constants per class.")
        print("  Consequence: P_6 needs 2 points per class, not 7. The banked")
        print("  data has 7 even and 6 odd above the onset, so T4 at k = 6")
        print("  becomes testable with 5 and 4 holdouts.")
    else:
        print("  At least one cumulant is nonlinear in S, so the parity split")
        print("  alone does NOT separate the two spine families. A1.3 step 1")
        print("  does not go in this form; the two-spine sum survives the split.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
