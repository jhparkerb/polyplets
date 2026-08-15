#!/usr/bin/env python3
"""Ridgeline 2: the depth family is a one-parameter law -- a branch point moving at
constant velocity in the excess variable.

Builds on experiments/ridgeline_master.py, which verifies the closed form

    D_j(k) = [Y^k t^(j-1)] ( Phat(Y,t) + Bhat(Y,t)^2 / (t - 3 - Shat(Y,t)) )   (M)

with t marking cluster *excess*.

===========================================================================
1. Normalisation (read this before comparing with onset-defect-law.md)
===========================================================================

Two different quantities are both called an "amplitude" in this campaign.
results/onset-defect-law.md Sec.2 uses A_j := C_j Gamma(j-1/2), where C_j is the
coefficient amplitude of the defect itself:

    D_j(k) ~ C_j 9^k k^(j-3/2).

This script works throughout in C_j, and converts only when quoting the doc.
The conversion is R_j^doc = R_j^coef * Gamma(j-1/2)/Gamma(1/2), with
R_j := (C_j/C_1)(81/25)^(j-1) resp. (A_j/A_1)(81/25)^(j-1).

===========================================================================
2. The ridge and the scaling function
===========================================================================

Every depth has its singularity at the same point Y = 1/9 (the rate is 9 at every
depth: results/onset-defect-law.md Sec.1); only the exponent moves,

    F_j(Y) = sum_k D_j(k) Y^k ~ C_j Gamma(j-1/2) (1-9Y)^(-(j-1/2)).

So the whole tower is one scaling function in tau = t/(1-9Y):

    G(Y,t)/t ~ (1-9Y)^(-1/2) f(tau),   f(tau) = sum_M C_(M+1) Gamma(M+1/2) tau^M,

and f is exactly the amplitude generating function of onset-defect-law.md Sec.2:
f(tau) = sum_j A_j tau^(j-1).  Since sum_L z^L L^(M-1/2) ~ Gamma(M+1/2)(1-z)^(-M-1/2),
the same statement read at fixed chain length L is

    G(Y,t)/t ~ C_1 sum_L (9Y)^L L^(-1/2) Acal(tL),   Acal(xi) = sum_M (C_(M+1)/C_1) xi^M,

i.e. **Acal is the excess enhancement of a cluster, resolved by chain length**.

===========================================================================
3. The conjectured family IS a moving branch point
===========================================================================

Suppose the dominant singularity of G/t is a square-root branch point whose
location moves with the excess marker: singular part h(t)(1-9Y-psi(t))^(-1/2)
with h and psi analytic at t = 0, psi(0) = 0, psi'(0) = alpha, and the exponent
-1/2 fixed.  In the scaling limit (t -> 0, tau fixed) only psi'(0) survives, so

    f(tau) = h(0)(1 - alpha tau)^(-1/2),
    C_(M+1) Gamma(M+1/2) = C_1 Gamma(1/2) alpha^M (1/2)_M / M!,
    and since Gamma(M+1/2) = sqrt(pi) (1/2)_M,

        C_(M+1) = C_1 alpha^M / M!,   i.e.   Acal(xi) = exp(alpha xi).       (*)

Equivalently: depth M+1 is the M-th derivative of depth 1,
F_(M+1) = (-alpha)^M/M! * d^M F_1/d(1-9Y)^M + less singular.

The conjectured family of results/onset-defect-law.md Sec.2,
A_j = (sqrt6/27)(25/81)^(j-1) binom(2j-2,j-1)/2^(j-1), is *exactly* (*) with
alpha = 50/81: using binom(2M,M)/2^M = 2^M (1/2)_M/M!,

    C_(M+1)/C_1 = (A_(M+1)/A_1) sqrt(pi)/Gamma(M+1/2) = (50/81)^M / M!.

So the seven-term family of rationals is not seven numbers: it is ONE constant,
the velocity alpha at which the branch point moves.  This script measures alpha
independently at M = 1, 2, 3 from the exact defects of (M) and asks whether the
three agree -- and what the j = 5 rivals 35/8 and 118/27 demand of alpha.

RED controls: synthetic towers built to obey (*) exactly must be accepted, and a
synthetic tower built to violate it must be rejected.

Run from repo root:  python3 experiments/ridgeline_scaling.py [K] [EMAX]
"""
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ridgeline_master import master_G                              # noqa: E402

mp.mp.dps = 60
ALPHA = mp.mpf(50) / 81


# ------------------------------------------------------------ amplitude tools

def richardson(seq, ks, order):
    """Classical order-n Richardson for a 1/k expansion, evaluated at the top.

    R_n(k) = sum_{i=0..n} (-1)^(n-i) (k+i)^n a_(k+i) / (i! (n-i)!),
    which annihilates the 1/k, ..., 1/k^n terms exactly.  `ks` must be consecutive.
    """
    assert all(ks[i + 1] - ks[i] == 1 for i in range(len(ks) - 1))
    base = len(seq) - 1 - order
    assert base >= 0, "not enough points for that Richardson order"
    tot = mp.mpf(0)
    for i in range(order + 1):
        k = mp.mpf(ks[base + i])
        tot += (-1) ** (order - i) * k ** order * seq[base + i] \
            / (mp.factorial(i) * mp.factorial(order - i))
    return tot


def amplitude(seqfun, j, kmin, kmax, orders=(2, 3, 4, 5)):
    """C_j from D_j(k) ~ C_j 9^k k^(j-3/2): top-order value and order-spread bar."""
    ks = list(range(kmin, kmax + 1))
    seq = [seqfun(k) / mp.mpf(9) ** k / mp.mpf(k) ** (j - mp.mpf(3) / 2) for k in ks]
    vals = [richardson(seq, ks, o) for o in orders]
    return vals[-1], max(abs(v - vals[-1]) for v in vals[:-1])


def alphas_from_C(C):
    """alpha_M := (M! C_(M+1)/C_1)^(1/M) -- one determination of alpha per depth."""
    return {M: (mp.factorial(M) * C[M + 1] / C[1]) ** (mp.mpf(1) / M)
            for M in range(1, len(C))}


def law_holds(al, tol):
    return all(abs(a / ALPHA - 1) < tol for a in al.values())


def alpha_by_derivative(D1, Dj, M, kmin, kmax, orders=(2, 3, 4, 5)):
    """alpha from  D_(M+1)(k) ~ (alpha^M/M!) 9^-M (k+M)!/k! D_1(k+M).

    This is the derivative form of the moving-branch-point claim
    F_(M+1) = (-alpha)^M/M! d^M F_1/dw^M, w = 1-9Y, d/dw = -(1/9) d/dY.
    Dividing by the exact D_1 removes 9^k, k^(M-1/2) and part of the 1/k
    structure, so it is a far sharper estimator than extracting C_j separately.
    Needs D_1 out to k = kmax + M -- cheap, the gap walk gives it to any k.
    """
    ks = list(range(kmin, kmax + 1))
    seq = []
    for k in ks:
        num = mp.mpf(Dj[k].numerator) / mp.mpf(Dj[k].denominator)
        den = mp.mpf(D1[k + M].numerator) / mp.mpf(D1[k + M].denominator)
        ratio = num / den * mp.factorial(M) * mp.mpf(9) ** M \
            * mp.factorial(k) / mp.factorial(k + M)
        seq.append(ratio)
    vals = [richardson(seq, ks, o) ** (mp.mpf(1) / M) for o in orders]
    return vals[-1], max(abs(v - vals[-1]) for v in vals[:-1])


def synth(rule, kmax, jmax, C1, sub=mp.mpf("0.7")):
    """Synthetic tower D_j(k) = C_j 9^k k^(j-3/2)(1+sub/k) with C_j/C_1 by `rule`."""
    return {j: (lambda k, j=j: mp.mpf(9) ** k * mp.mpf(k) ** (j - mp.mpf(3) / 2)
                * C1 * rule(j) * (1 + sub / k)) for j in range(1, jmax + 1)}


# ---------------------------------------------------------------------- main

def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    EMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    t0 = time.time()

    print("== exact depth tower from the master identity (M), k <= %d" % K)
    G = master_G(K, EMAX)
    D = {j: {k: G[j - 1][k] for k in range(K + 1)} for j in range(1, EMAX + 2)}
    print("   D_1..D_%d assembled exactly  [%.1fs]" % (EMAX + 1, time.time() - t0))

    print()
    print("== coefficient amplitudes  D_j(k) ~ C_j 9^k k^(j-3/2)   (Richardson, k <= %d)"
          % K)
    C, bar = {}, {}
    for j in range(1, EMAX + 2):
        C[j], bar[j] = amplitude(lambda k, j=j: mp.mpf(D[j][k].numerator)
                                 / mp.mpf(D[j][k].denominator), j, max(j, 6), K)
        print("   C_%d = %s   (order spread %.2e)" % (j, mp.nstr(C[j], 12), float(bar[j])))
    c1exact = mp.sqrt(6) / (27 * mp.sqrt(mp.pi))
    print("   C_1 vs the DERIVED sqrt6/(27 sqrt pi) = %s : rel diff %.2e"
          % (mp.nstr(c1exact, 12), float(abs(C[1] / c1exact - 1))))

    print()
    print("== the one-parameter law:  C_(M+1)/C_1 = alpha^M/M!,  alpha = 50/81 = %s"
          % mp.nstr(ALPHA, 12))
    print("   %-4s %-20s %-14s %-12s" % ("M", "alpha_M", "alpha_M/(50/81)-1", "spread"))
    al = alphas_from_C(C)
    for M in sorted(al):
        # first-order propagation of the amplitude spreads into alpha_M
        rel = (bar[M + 1] / C[M + 1] + bar[1] / C[1]) / M
        print("   %-4d %-20s %-14.2e %-12.2e"
              % (M, mp.nstr(al[M], 12), float(al[M] / ALPHA - 1), float(rel)))
    tol = mp.mpf("1e-3")
    law_ok = law_holds(al, tol)
    print("   all |alpha_M/alpha - 1| < %s : %s" % (mp.nstr(tol, 2),
                                                    "YES" if law_ok else "NO"))

    print()
    print("== the sharp estimator: depth M+1 as the M-th derivative of depth 1")
    print("   D_(M+1)(k) / [(alpha^M/M!) 9^-M (k+M)!/k! D_1(k+M)] -> 1")
    from depth1_gap_walk import walk_families, series_D1            # noqa: E402
    D1 = series_D1(walk_families(K + EMAX + 2), K + EMAX + 2)
    print("   %-4s %-22s %-16s %-12s" % ("M", "alpha_M (derivative form)",
                                         "alpha_M/(50/81)-1", "spread"))
    ald = {}
    for M in range(1, EMAX + 1):
        ald[M], sp = alpha_by_derivative(D1, D[M + 1], M, max(M + 1, 5), K)
        print("   %-4d %-22s %-16.2e %-12.2e"
              % (M, mp.nstr(ald[M], 14), float(ald[M] / ALPHA - 1), float(sp)))
    print("   (D_1 is exact to any k via the gap walk, so only D_2..D_%d limit this)"
          % (EMAX + 1))

    print()
    print("== calibration: the estimator's own bias on towers that obey the law exactly")
    print("   synthetic D_j(k) = C_j 9^k k^(j-3/2)(1 + c1/k + c2/k^2), C_j = C_1 alpha^j-1/(j-1)!")
    print("   %-18s %s" % ("(c1, c2)", "  ".join("bias at M=%d" % M
                                                 for M in range(1, EMAX + 1))))
    calib = {M: mp.mpf(0) for M in range(1, EMAX + 1)}
    for c1v, c2v in ((mp.mpf("0.7"), mp.mpf(0)), (mp.mpf(2), mp.mpf(0)),
                     (mp.mpf(0), mp.mpf(5)), (mp.mpf(2), mp.mpf(-8))):
        def mk(j, c1v=c1v, c2v=c2v):
            Cj = c1exact * ALPHA ** (j - 1) / mp.factorial(j - 1)
            return {k: mp.mpf(9) ** k * mp.mpf(k) ** (j - mp.mpf(3) / 2) * Cj
                    * (1 + c1v / k + c2v / k ** 2) for k in range(1, K + EMAX + 3)}
        Ssyn = {j: mk(j) for j in range(1, EMAX + 2)}
        row = []
        for M in range(1, EMAX + 1):
            ks = list(range(max(M + 1, 5), K + 1))
            seq = [Ssyn[M + 1][k] / Ssyn[1][k + M] * mp.factorial(M) * mp.mpf(9) ** M
                   * mp.factorial(k) / mp.factorial(k + M) for k in ks]
            a = richardson(seq, ks, 5) ** (mp.mpf(1) / M)
            b = abs(a / ALPHA - 1)
            calib[M] = max(calib[M], b)
            row.append("%.2e" % float(b))
        print("   %-18s %s" % ("(%s, %s)" % (mp.nstr(c1v, 3), mp.nstr(c2v, 3)),
                               "  ".join("%11s" % r for r in row)))
    print("   worst calibrated bias: %s"
          % "  ".join("M=%d: %.2e" % (M, float(calib[M])) for M in sorted(calib)))
    law_d = all(abs(ald[M] / ALPHA - 1) <= max(calib[M], mp.mpf("1e-9")) * 3
                for M in ald)
    print("   observed deviations within 3x the calibrated bias at every M: %s"
          % ("YES" if law_d else "NO"))

    print()
    print("== RED controls")
    print("   the test is: every alpha_M equals the DERIVED 50/81 (ridgeline_vertex.py)")
    print("   within tolerance.  Controls must be rejected.  Note M = 1 is definitional")
    print("   (alpha_1 := C_2/C_1), so the constancy rivals only bite from M = 2.")
    ctl = []
    cases = [("exponential (the law)",
              lambda j: ALPHA ** (j - 1) / mp.factorial(j - 1), True),
             ("law with alpha shifted 1%",
              lambda j: (ALPHA * mp.mpf("1.01")) ** (j - 1) / mp.factorial(j - 1), False)]
    if EMAX >= 2:
        cases += [("geometric (violates)", lambda j: ALPHA ** (j - 1), False),
                  ("binomial-in-C (violates)",
                   lambda j: ALPHA ** (j - 1) * mp.binomial(2 * j - 2, j - 1)
                   / mp.mpf(2) ** (j - 1), False)]
    else:
        print("   (constancy rivals skipped: they are indistinguishable at M = 1)")
    for name, rule, want in cases:
        S = synth(rule, K, EMAX + 1, c1exact)
        Cs = {j: amplitude(S[j], j, max(j, 6), K)[0] for j in range(1, EMAX + 2)}
        got = law_holds(alphas_from_C(Cs), tol)
        ok = (got == want)
        ctl.append(ok)
        print("   %-26s -> law %-8s (expected %-8s) %s"
              % (name, "holds" if got else "fails", "holds" if want else "fails",
                 "OK" if ok else "CONTROL FAILED"))
    controls_ok = all(ctl)

    print()
    print("== the chain-length reduction, checked term by term")
    print("   sum_L z^L L^(M-1/2) = Li_(1/2-M)(z) ~ Gamma(M+1/2)(1-z)^(-M-1/2)")
    chain_ok = True
    for M in range(EMAX + 2):
        errs = []
        for eps in (mp.mpf("1e-3"), mp.mpf("1e-6")):
            z = 1 - eps
            lhs = mp.polylog(mp.mpf(1) / 2 - M, z)
            rhs = mp.gamma(M + mp.mpf(0.5)) * eps ** (-M - mp.mpf(0.5))
            errs.append(abs(lhs / rhs - 1))
        # M = 0 converges only like (1-z)^(1/2) (the zeta(1/2) term); M >= 1 like (1-z)
        ok = errs[1] < errs[0] / 10
        chain_ok = chain_ok and ok
        print("   M=%d: rel %.2e (1-z=1e-3) -> %.2e (1e-6)   %s"
              % (M, float(errs[0]), float(errs[1]), "OK" if ok else "FAIL"))

    print()
    print("== the law reproduces the whole measured family of onset-defect-law.md Sec.2")
    print("   R_j^coef := (C_j/C_1)(81/25)^(j-1) = 2^(j-1)/(j-1)!  [the law]")
    print("   R_j^doc  := (A_j/A_1)(81/25)^(j-1) = R_j^coef Gamma(j-1/2)/Gamma(1/2)")
    print("   %-3s %-14s %-16s %-16s %s" % ("j", "R_j^coef (law)", "-> R_j^doc",
                                            "binom(2j-2,j-1)/2^(j-1)", "match"))
    fam_ok = True
    for j in range(1, 8):
        M = j - 1
        rc = mp.mpf(2) ** M / mp.factorial(M)
        rd = rc * mp.gamma(j - mp.mpf(0.5)) / mp.gamma(mp.mpf(0.5))
        doc = mp.binomial(2 * j - 2, j - 1) / mp.mpf(2) ** M
        same = abs(rd - doc) < mp.mpf("1e-40")
        fam_ok = fam_ok and same
        print("   %-3d %-14s %-16s %-16s %s"
              % (j, mp.nstr(rc, 8), mp.nstr(rd, 8), mp.nstr(doc, 8),
                 "yes" if same else "NO"))
    print("   the law is identically the binomial family: %s"
          % ("OK" if fam_ok else "FAIL"))

    print()
    print("== the j = 5 rivals in the natural (coefficient) normalisation")
    from fractions import Fraction as Fr                           # noqa: E402
    convF = Fr(105, 16)                       # Gamma(9/2)/Gamma(1/2)
    print("   R_5^coef = R_5^doc / (Gamma(9/2)/Gamma(1/2)) = R_5^doc / (105/16)")
    print("   the law:        2^4/4!   = %s" % Fr(2 ** 4, 24))
    for nm, rd in (("binomial 35/8", Fr(35, 8)), ("rival 118/27", Fr(118, 27))):
        print("   %-16s -> R_5^coef = %s%s" % (nm, rd / convF,
                                               "   (= the law)" if rd / convF
                                               == Fr(2 ** 4, 24) else ""))
    print("   so the rival is a simple rational only in the Gamma-weighted A_j;")
    print("   in C_j it is 1888/2835, which is what a recogniser scanning the")
    print("   wrong normalisation will not tell you.")

    print()
    print("== the j = 5 question")
    conv5 = mp.gamma(mp.mpf(9) / 2) / mp.gamma(mp.mpf(1) / 2)      # A_5/C_5 over A_1/C_1
    for name, Rdoc in (("binomial 35/8", mp.mpf(35) / 8),
                       ("rival 118/27", mp.mpf(118) / 27)):
        Rcoef = Rdoc / conv5
        a4 = (mp.factorial(4) * Rcoef * (mp.mpf(25) / 81) ** 4) ** (mp.mpf(1) / 4)
        print("   R_5^doc = %-16s -> C_5/C_1 = %s -> alpha_4 = %s  (%+.2e from 50/81)"
              % (name + " = " + mp.nstr(Rdoc, 8),
                 mp.nstr(Rcoef * (mp.mpf(25) / 81) ** 4, 8), mp.nstr(a4, 10),
                 float(a4 / ALPHA - 1)))
    print("   the law predicts C_5/C_1 = alpha^4/4! = %s, i.e. R_5^doc = %s = 35/8"
          % (mp.nstr(ALPHA ** 4 / 24, 10),
             mp.nstr(ALPHA ** 4 / 24 * conv5 * (mp.mpf(81) / 25) ** 4, 10)))
    worst = max(abs(ald[M] / ALPHA - 1) for M in ald)
    need = abs(((mp.factorial(4) * (mp.mpf(118) / 27) / conv5 * (mp.mpf(25) / 81) ** 4)
                ** (mp.mpf(1) / 4)) / ALPHA - 1)
    print("   largest |alpha_M/alpha-1| seen (derivative form, M=1..%d): %.2e"
          % (EMAX, float(worst)))
    print("   the departure 118/27 would require at M=4:            %.2e" % float(need))
    print("   ratio: %.1fx" % float(need / worst))

    green = law_ok and law_d and controls_ok and chain_ok and fam_ok
    print()
    print("VERDICT: %s   [%.1fs]" % ("GREEN" if green else "RED", time.time() - t0))
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
