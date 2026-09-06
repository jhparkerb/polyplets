#!/usr/bin/env python3
"""Ridgeline 3: alpha = 50/81 derived from the excess vertex of the gap walk.

experiments/ridgeline_scaling.py reduces the whole depth-amplitude family to ONE
constant.  If the dominant singularity of G(Y,t) is a square-root branch point
whose location moves analytically with the excess marker t, then

    1 - 9 Y_c(t) = alpha t + O(t^2)   and   C_(M+1) = C_1 alpha^M / M!,

C_j being the coefficient amplitude of D_j(k) ~ C_j 9^k k^(j-3/2).  The measured
family of results/below-onset.md Sec.2 is exactly this with alpha = 50/81.

This script *derives* alpha = 50/81 by a finite local enumeration.

------------------------------------------------------------------ the argument

Y_c(t) is where the cluster's row transfer becomes critical, so alpha is local:
alpha = d(lambda)/dt at (1/9, 0), lambda the zero-momentum eigenvalue of the
deformed transfer.  Rows of size s carry Y^(s-1) t^(s-2), so at t = 0 only 2-cell
rows survive and the bulk (delocalized) mode is two pending components far apart,
each taking one king step: mass 3 x 3 = 9, critical at 9Y = 1.

At first order in t exactly one row is a 3-cell row.  That row costs Y^2 t and
leaves an intermediate configuration which the NEXT row -- an ordinary 2-cell row,
cost Y -- must resolve.  Writing Sigma for the two-row vertex sum

    Sigma = sum over 3-cell rows R over the bulk state
              of (number of 2-cell rows that follow R),

the eigenvalue equation for a two-row excursion is lambda = 9Y + Y^3 t Sigma/lambda,
so lambda = 9Y + Y^2 t Sigma/9 and, at Y = 1/9,

    1 - 9 Y_c = t Sigma / 729,      alpha = Sigma / 729.

Both counts come from experiments/severance_w3_depths.transitions, the vetted
row-transfer enumeration (a new row is legal iff every pending block of the old
row has a cell adjacent to it).  Nothing is counted by hand.

Note the trap that made a first pass give 378 instead of 450: a 3-cell row may
leave THREE pending blocks, and such a configuration is NOT dead -- a single cell
of the next row can be adjacent to two blocks at once when they are close, so a
2-cell row can still close it.  Filtering the intermediate states down to two
blocks loses 72 of the 450 and gives 14/27, not 50/81.  The unfiltered count is
the one the transfer demands, and it is what the enumeration reports.

Run from repo root:  python3 experiments/ridgeline_vertex.py [G]
"""
import os
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import severance_w3_depths as W                                    # noqa: E402

ALPHA = F(50, 81)


def pair_state(G, joined=False):
    """Two cells at 0 and G; two pending blocks (class P) or one (class J)."""
    return ((0, G), (0, 0) if joined else (0, 1))


def row_total(st, t, span):
    return sum(W.transitions(st, t, span).values())


def sigma(G, span, two_block_only=False):
    """The two-row excess vertex sum over the bulk state at gap G."""
    tot = 0
    for st2, mult in W.transitions(pair_state(G), 3, span).items():
        if two_block_only and max(st2[1]) + 1 != 2:
            continue
        tot += mult * row_total(st2, 2, span)
    return tot


def sigma_by_outclass(G, span):
    """Split Sigma by the class of the 2-cell state the excursion lands in.

    Class = number of pending blocks: 2 is P (the delocalised/bulk sector, the
    critical right eigenvector), 1 is J (the sector carrying the localised rho).
    If nothing lands in J, the excess excursion never leaves P and the flat
    zero-momentum projection used for alpha is unambiguous.
    """
    out = {1: 0, 2: 0}
    for st2, mult in W.transitions(pair_state(G), 3, span).items():
        for st3, m2 in W.transitions(st2, 2, span).items():
            out[max(st3[1]) + 1] += mult * m2
    return out


def main():
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    t0 = time.time()
    ok = True

    print("== the unperturbed bulk mode (t = 0): two 2-cell rows, mass 9")
    base = {g: row_total(pair_state(g), 2, g + 6) for g in range(8, G + 1)}
    print("   2-cell rows out of the bulk state, G = %d..%d: %s"
          % (8, G, sorted(set(base.values()))))
    good = set(base.values()) == {9}
    ok = ok and good
    print("   mass 9 = 3 x 3 (one king step per pending component): %s"
          % ("OK" if good else "FAIL"))

    print()
    print("== the first-order excess vertex Sigma, and alpha = Sigma/729")
    print("   %-5s %-8s %-10s %-16s %-14s" % ("G", "span", "Sigma", "alpha = S/729",
                                              "alpha - 50/81"))
    vals = []
    for g in range(10, G + 1):
        for sp in (g + 6, g + 12):
            s = sigma(g, sp)
            a = F(s, 729)
            vals.append(s)
            print("   %-5d %-8d %-10d %-16s %-14s" % (g, sp, s, a, a - ALPHA))
    stable = len(set(vals)) == 1
    ok = ok and stable
    print("   Sigma independent of both the gap G and the span cap: %s"
          % ("OK -- a genuine bulk quantity" if stable else "FAIL"))
    S = vals[0]
    print()
    print("   Sigma = %d,  alpha = %d/729 = %s = %.12f"
          % (S, S, F(S, 729), float(F(S, 729))))
    exact = (F(S, 729) == ALPHA)
    ok = ok and exact
    print("   alpha == 50/81 exactly: %s" % ("YES" if exact else "NO"))

    print()
    print("== controls")
    s2 = sigma(G, G + 6, two_block_only=True)
    c1 = (s2 != S)
    print("   (a) filtering intermediates to 2 blocks gives Sigma = %d -> %s;"
          % (s2, F(s2, 729)))
    print("       the 3-block intermediates carry %d of %d, so the count is NOT"
          % (S - s2, S))
    print("       insensitive to how the vertex is defined: %s" % ("OK" if c1 else "FAIL"))

    saved = dict(W._TRANS)
    key = ((0, G), (0, 1))
    tr = dict(W.transitions(pair_state(G), 3, G + 6))
    victim = sorted(tr)[0]
    tr[victim] -= 1
    W._TRANS[(G + 6, 3, key)] = tr
    s3 = sigma(G, G + 6)
    W._TRANS.clear()
    W._TRANS.update(saved)
    c2 = (s3 != S)
    print("   (b) RED: dropping ONE transition from the 3-cell row table gives"
          " Sigma = %d (%s)" % (s3, "control fires" if c2 else "CONTROL FAILED"))
    ok = ok and c1 and c2
    print("   (c) restored table reproduces Sigma = %d: %s"
          % (sigma(G, G + 6), "OK" if sigma(G, G + 6) == S else "FAIL"))

    print()
    print("== why the exponent is -1/2, and why t moves the point but not the exponent")
    import sympy as sp                                             # noqa: E402
    u = sp.symbols('u', positive=True)
    Kd = (1 + u + u ** 2) ** 2 / u ** 2       # the bulk dispersion: two king steps
    K1 = sp.simplify(Kd.subs(u, 1))
    dK = sp.simplify(sp.diff(Kd, u).subs(u, 1))
    d2lnK = sp.simplify(sp.diff(sp.log(Kd), u, 2).subs(u, 1))
    print("   dispersion K(u) = (1+u+u^2)^2/u^2 (the gap-walk kernel, u marks the gap)")
    print("   K(1) = %s        -> criticality at 9Y = 1, i.e. Y = 1/9" % K1)
    print("   K'(1) = %s        -> u = 1 is stationary (K(u) = K(1/u) by symmetry)" % dK)
    print("   (log K)''(1) = %s -> the stationary point is NONDEGENERATE" % d2lnK)
    disp = (K1 == 9 and dK == 0 and d2lnK != 0)
    ok = ok and disp
    print("   %s: a nondegenerate quadratic minimum of the dispersion gives the"
          % ("OK" if disp else "FAIL"))
    print("   Gaussian transverse integral, hence (1-9Y)^(-1/2) -- the measured")
    print("   theta_1 = -1/2.  An analytic perturbation of a nondegenerate minimum")
    print("   stays a nondegenerate minimum, so switching on t moves the HEIGHT of")
    print("   the minimum (that is alpha) and its location, but not the exponent.")
    print("   That is the argument behind assumption 1 of the ledger.")

    print()
    print("== does the excess excursion leave the P sector?")
    print("   %-5s %-16s %-16s" % ("G", "lands in P (2 blocks)", "lands in J (1 block)"))
    stays = True
    for g in range(10, G + 1):
        sp = sigma_by_outclass(g, g + 6)
        stays = stays and sp[1] == 0 and sp[2] == S
        print("   %-5d %-16d %-16d" % (g, sp[2], sp[1]))
    ok = ok and stays
    print("   the excursion returns to P every time: %s" % ("OK" if stays else "NO"))
    print("   -> the vertex acts inside the delocalised sector, where the critical")
    print("      mode is the flat one; the J class (which carries rho and whose")
    print("      zero-momentum row sum diverges) is never entered at first order.")

    print()
    print("== independent check: the derived alpha against the exact defect series")
    import mpmath as mp                                            # noqa: E402
    from ridgeline_master import master_G                          # noqa: E402
    from ridgeline_scaling import alpha_by_derivative              # noqa: E402
    from depth1_gap_walk import walk_families, series_D1           # noqa: E402
    KM = int(os.environ.get("RIDGELINE_K", "19"))
    Gm = master_G(KM, 1)
    D2 = {k: Gm[1][k] for k in range(KM + 1)}
    D1 = series_D1(walk_families(KM + 3), KM + 3)
    am, spread = alpha_by_derivative(D1, D2, 1, 5, KM)
    rel = abs(am / mp.mpf(50) * 81 - 1)
    print("   measured from D_2 vs D_1 (Richardson, k <= %d): alpha_1 = %s"
          % (KM, mp.nstr(am, 12)))
    print("   derived 50/81 = %.12f   relative difference %.2e (order spread %.1e)"
          % (float(ALPHA), float(rel), float(spread)))
    agree = rel < mp.mpf("1e-4")
    ok = ok and agree
    print("   derived value inside the extraction's reach: %s"
          % ("OK" if agree else "FAIL"))

    print()
    print("VERDICT: %s   [%.1fs]" % ("GREEN" if ok else "RED", time.time() - t0))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
