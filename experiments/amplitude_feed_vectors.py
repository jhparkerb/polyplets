#!/usr/bin/env python3
"""The (dir4, HV-convex) / HV-convex amplitude ratio, from the block structure.

results/subclasses.md (formerly docs/middle-kingdom-followups-plan.md) Table B measured
    r = C_dir4 / C_HV = 0.46210904920994244003566238770030583284116343972998...
and found no integer relation.  results/hv-growth-sandwich.md's block picture
says what r *is* -- "a ratio of residues of the same staircase resolvent
against two different feed vectors".  This script writes those feed vectors
down and evaluates them, so the ratio becomes an explicit convergent
expression rather than an extrapolated decimal.

THE DERIVATION (all of it checked numerically below).  Column heights h, area
marked by x.  From cpp/middle_kingdom_tm.cpp's PROFILE engine, the transfer
weight (h -> h') carries x^(h') and the four phase blocks have kernels

    (0,0) internal       U (h,h')  = h' - h + 1        (h' >= h)
    (0,0) internal, dir4 U4(h,h')  = min(2, h'-h+1)    (h' >= h)
    (1,0) internal       T (h,h')  = min(h,h') + 1     (the staircase block)
    (0,0) -> (1,0)       L (h,h')  = min(h, h'+1)      (unchanged by dir4)
    (0,0) -> (0,1)       L (h,h')  = min(h, h'+1)      (the same matrix)

Only U is touched by the 4-cone floor d >= -1; T, the (1,1) block and every
map out of (1,0) are untouched entry for entry.  So, writing v0(h) = x^h for
the first column and x_c = 1/mu for the dominant singularity,

    feed vector   w  = v0 (I - U )^-1 L        (row vector over heights)
    feed vector   w4 = v0 (I - U4)^-1 L

and, because (I - T(x))^-1 has a rank-one pole at x_c whose residue is
phi psi^T with T phi = phi, the pole part of any path through the staircase
block factors as (feed . phi) x (everything downstream of the block).  Every
factor downstream is shared, so it cancels:

    C(D_asc) / C(A_(1,0))  =  (w4 . phi) / (w . phi).

The vertical mirror h -> reflection swaps phases (pb,pt) -> (pt,pb), fixes U
and maps the two middle blocks onto each other, so A_(0,1)(n) = A_(1,0)(n)
exactly and C_HV = 2 C(A_(1,0)).  D_asc has no (0,1) part at all.  Hence

    r  =  (1/2) (w4 . phi) / (w . phi).                              (*)

phi is not computed by linear algebra.  Summing T phi = phi by parts twice
turns the eigenvector equation into a three-term q-recurrence

    phi(h) = (2 - x^(h-1)) phi(h-1) - phi(h-2),   phi(0) = 1, phi(1) = 2,

whose two solutions are asymptotically constant and linear in h.  The
eigenvalue condition (Perron eigenvalue of T(x) equal to 1, i.e. x = x_c) is
exactly "the linear solution is absent", i.e. phi(h) - phi(h-1) -> 0.  That
gives mu independently of any series extrapolation, by shooting.

RED-first controls, all run by default:
  GREEN  the phi recurrence satisfies the eigen-equation of T(x_c) by direct
         summation at several h
  GREEN  the shot x_c reproduces the banked 199-digit mu
  RED    at x = 1/3.13 (off x_c by 1e-3) the eigen-equation must FAIL
  RED    truncating U at min(3,.) instead of min(2,.) must NOT reproduce r
  RED    dropping the factor 1/2 must NOT reproduce r

Usage: python3 experiments/amplitude_feed_vectors.py [--dps 400] [--hmax 900]
         [--measured results/mk_hvdir4asc_terms_n700.txt,
                     results/convex_area_terms_n700_king.txt]
Target machine: gympie (laptop).  MEASURED: dps 400 / hmax 900 in about 6 s,
under 100 MB.  Nothing to resume; SIGINT is enough.
"""
import argparse
import sys

from mpmath import mp, mpf, nstr, findroot

from seriestools import agree_digits, read_terms

# results/convex-polyplets.md's 199 banked digits of mu, reproduced by three
# further series in results/hv-growth-sandwich.md.  Used only as a cross-check
# on the shooting, never as an input to it.
MU_BANKED = (
    "3.1289432697308862522774479953877541605320912219043941349649746499492443858371"
    "8257615823063288164783234634835221018937039608167576493048146233778414064847543"
    "298805623983850111109827008627878918922549")

# results/subclasses.md (formerly docs/middle-kingdom-followups-plan.md) Table B, MEASURED and never edited: the
# amplitude ratio of the UNSPLIT (dir4, HV-convex) series against HV-convex, to
# its 54 trusted digits.  D_desc contributes nothing at order mu^n, so the
# split ratio must reproduce this to Table B's own precision.
TABLE_B = "0.462109049209942440035662387700305832841163439729980425"


def phi_vector(x, hmax):
    """Right Perron eigenvector of T(x)(h,h') = x^h' (min(h,h')+1).

    phi(h) = (2 - x^(h-1)) phi(h-1) - phi(h-2), phi(0)=1, phi(1)=2.
    Returned indexed 0..hmax.
    """
    phi = [mpf(1), mpf(2)]
    xp = mpf(1)                       # x^(h-1) at h = 1
    for h in range(2, hmax + 1):
        xp *= x                       # now x^(h-1)
        phi.append((2 - xp) * phi[h - 1] - phi[h - 2])
    return phi


def slope(x, hmax):
    """phi(hmax) - phi(hmax-1): zero exactly when x = x_c."""
    phi = phi_vector(x, hmax)
    return phi[hmax] - phi[hmax - 1]


def eigen_residual(x, phi, hmax, hs):
    """max relative failure of sum_h' x^h'(min(h,h')+1) phi(h') = phi(h)."""
    xs = [mpf(0)] * (hmax + 1)
    p = mpf(1)
    for h in range(1, hmax + 1):
        p *= x
        xs[h] = p
    worst = mpf(0)
    for h in hs:
        acc = mpf(0)
        for hp in range(1, hmax + 1):
            acc += xs[hp] * (min(h, hp) + 1) * phi[hp]
        rel = abs(acc - phi[h]) / abs(phi[h])
        worst = max(worst, rel)
    return worst


def feed_vector(x, hmax, cap=None):
    """w = v0 (I - U)^-1 L, indexed 1..hmax.

    cap=None  : U(h,h') = h'-h+1        (unrestricted (0,0) block)
    cap=k     : U(h,h') = min(k, h'-h+1) (4-cone truncation at k=2; k=3 is the
                                          RED control)
    Both recurrences are O(hmax) via prefix sums; the h'=h diagonal entry is 1
    in every case, which is why each step divides by (1 - x^h').
    """
    xs = [mpf(0)] * (hmax + 2)
    p = mpf(1)
    for h in range(1, hmax + 2):
        p *= x
        xs[h] = p

    g = [mpf(0)] * (hmax + 1)
    S0 = [mpf(0)] * (hmax + 1)        # S0[h] = sum_{j<=h} g[j]
    S1 = [mpf(0)] * (hmax + 1)        # S1[h] = sum_{j<=h} j*g[j]
    for hp in range(1, hmax + 1):
        if cap is None:
            # sum_{h<h'} g[h](h'-h+1) = (h'+1) S0(h'-1) - S1(h'-1)
            inner = (hp + 1) * S0[hp - 1] - S1[hp - 1]
        elif cap == 2:
            inner = 2 * S0[hp - 1]
        else:
            # min(cap, h'-h+1): h' - h + 1 < cap  <=>  h > h' + 1 - cap
            split = hp + 1 - cap      # h <= split use cap, h > split use h'-h+1
            lo = min(split, hp - 1)
            inner = cap * S0[max(lo, 0)]
            if hp - 1 > lo:
                inner += ((hp + 1) * (S0[hp - 1] - S0[max(lo, 0)])
                          - (S1[hp - 1] - S1[max(lo, 0)]))
        g[hp] = xs[hp] * (1 + inner) / (1 - xs[hp])
        S0[hp] = S0[hp - 1] + g[hp]
        S1[hp] = S1[hp - 1] + hp * g[hp]

    # w(h') = x^h' * sum_h g(h) min(h, h'+1)
    #       = x^h' * [ S1(m) + (h'+1)(S0(hmax) - S0(m)) ],  m = min(h'+1, hmax)
    w = [mpf(0)] * (hmax + 1)
    for hp in range(1, hmax + 1):
        m = min(hp + 1, hmax)
        w[hp] = xs[hp] * (S1[m] + (hp + 1) * (S0[hmax] - S0[m]))
    return w


def contract(w, phi, hmax):
    acc = mpf(0)
    for h in range(hmax, 0, -1):      # small terms first
        acc += w[h] * phi[h]
    return acc


def evaluate(dps, hmax):
    """(mu, r, r_nohalf, r_cap3, min phi) at working precision dps.

    The one entry point tests/gate_middle_kingdom.py uses, so the gate runs
    the same arithmetic as the write-up rather than a copy of it.
    """
    mp.dps = dps
    xc = findroot(lambda t: slope(t, hmax), 1 / mpf(MU_BANKED),
                  tol=mpf(10) ** (-2 * dps))
    phi = phi_vector(xc, hmax)
    den = contract(feed_vector(xc, hmax, cap=None), phi, hmax)
    num = contract(feed_vector(xc, hmax, cap=2), phi, hmax)
    bad = contract(feed_vector(xc, hmax, cap=3), phi, hmax)
    return 1 / xc, num / den / 2, num / den, bad / den / 2, min(phi[1:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dps', type=int, default=400)
    ap.add_argument('--hmax', type=int, default=900)
    ap.add_argument('--measured', default='results/mk_hvdir4asc_terms_n700.txt,'
                                          'results/convex_area_terms_n700_king.txt')
    ap.add_argument('--show', type=int, default=200)
    ap.add_argument('--emit', default=None,
                    help='write mu and r_struct, one per line, for the PSLQ run')
    args = ap.parse_args()
    mp.dps = args.dps + 30
    hmax = args.hmax

    print(f"# feed-vector evaluation of the amplitude ratio: dps {mp.dps},"
          f" hmax {hmax} (x^hmax ~ 1e-{int(hmax * 0.4954)})")

    # --- mu by shooting on the three-term recurrence ------------------------
    x0 = 1 / mpf(MU_BANKED)
    xc = findroot(lambda t: slope(t, hmax), x0, tol=mpf(10) ** (-2 * mp.dps))
    mu = 1 / xc
    d_mu = agree_digits(mu, mpf(MU_BANKED))
    # what this run can reach: 199 banked digits, capped by the x^hmax
    # truncation and by the working precision
    reach = min(199, int(hmax * 0.4954) - 5, args.dps)
    print(f"\n## mu from the phi recurrence's eigenvalue condition (shooting)")
    print("  " + nstr(mu, min(args.show, 210)))
    print(f"  agreement with the banked 199-digit mu: {d_mu} digits"
          f" (this run reaches {reach})  {'OK' if d_mu >= reach else 'FAIL'}")
    if d_mu < reach:
        return 1

    phi = phi_vector(xc, hmax)

    # --- GREEN: phi really is the eigenvector; RED: it is not, off x_c ------
    hs = [1, 2, 3, 5, 10, 50]
    res_ok = eigen_residual(xc, phi, hmax, hs)
    phi_bad = phi_vector(1 / mpf('3.13'), hmax)
    res_bad = eigen_residual(1 / mpf('3.13'), phi_bad, hmax, hs)
    print(f"\n## eigen-equation sum_h' x^h'(min(h,h')+1)phi(h') = phi(h)")
    print(f"  GREEN at x_c        : worst relative residual 1e{int(mp.log10(res_ok))}")
    print(f"  RED   at x = 1/3.13 : worst relative residual 1e{int(mp.log10(res_bad))}"
          f"  {'(diverges, good)' if res_bad > mpf(10) ** -6 else '(CONTROL FAILED)'}")
    if res_ok > mpf(10) ** (-(args.dps - 20)) or res_bad < mpf(10) ** -6:
        print("  eigenvector controls FAILED")
        return 1

    # --- the two feed vectors and the ratio ---------------------------------
    w = feed_vector(xc, hmax, cap=None)
    w4 = feed_vector(xc, hmax, cap=2)
    w_bad = feed_vector(xc, hmax, cap=3)
    num, den = contract(w4, phi, hmax), contract(w, phi, hmax)
    r_struct = num / den / 2
    r_nohalf = num / den
    r_bad = contract(w_bad, phi, hmax) / den / 2

    # GREEN: phi positive and bounded => by Perron-Frobenius the eigenvalue 1
    # is the spectral radius, so the pole of (I-T)^-1 at x_c really is the
    # leading one and its residue really is rank one.
    pos = min(phi[1:])
    print(f"\n## Perron check: min phi = {nstr(pos, 8)}, phi(1) = {nstr(phi[1], 8)},"
          f" phi(hmax) = {nstr(phi[hmax], 12)}")
    print(f"  positive and bounded {'OK' if pos > 0 else 'FAIL'}"
          f" -- a positive eigenvector of a positive operator has the spectral"
          f" radius for its eigenvalue")
    if pos <= 0:
        return 1

    print(f"\n## (*)  r = (1/2) (w4 . phi) / (w . phi)")
    print("  w  . phi = " + nstr(den, 30))
    print("  w4 . phi = " + nstr(num, 30))
    print("  r_struct = " + nstr(r_struct, args.show))

    # --- against Table B, which measured the UNSPLIT ratio -------------------
    d_tb = agree_digits(r_struct, mpf(TABLE_B))
    print(f"\n## against Table B's 54 measured digits (the unsplit dir4 series)")
    print(f"  agree to {d_tb} digits"
          f"  {'OK' if d_tb >= 53 else 'MISMATCH -- REPORT, DO NOT EDIT TABLE B'}")
    if d_tb < 53:
        return 1

    # --- against the measured ratio -----------------------------------------
    f1, f2 = args.measured.split(',')
    # ratio_series/accelerate live in the probe that derived them; import them
    # by this file's directory, not the cwd, so the script runs from anywhere.
    sys.path.insert(0, __file__.rsplit('/', 1)[0])
    import ratio_amplitude as ra
    a1, a2 = read_terms(f1), read_terms(f2)
    N = min(len(a1), len(a2))
    _, est_full = ra.accelerate(ra.ratio_series(a1, a2, N), 60)
    _, est_drop = ra.accelerate(ra.ratio_series(a1, a2, N - 100), 60)
    trusted = max(0, min(agree_digits(mpf(a1[N - 1]) / mpf(a2[N - 1]),
                                      mpf(a1[N - 101]) / mpf(a2[N - 101])),
                         agree_digits(est_full, est_drop)) - 2)
    d_hit = agree_digits(r_struct, est_full)
    # the comparison can only reach the weaker of the two sides
    want = min(trusted, reach, int(hmax * 0.4954) - 5)
    print(f"\n## against {f1} / {f2}")
    print(f"  measured (Aitken, {N} terms), trusted {trusted} digits")
    print(f"  r_struct vs measured: {d_hit} digits agree, need {want}"
          f"   {'OK' if d_hit >= want else 'MISMATCH'}")
    print(f"  RED  no 1/2      : {agree_digits(r_nohalf, est_full)} digits"
          f"  {'(diverges, good)' if agree_digits(r_nohalf, est_full) < 3 else '(FAILED)'}")
    print(f"  RED  cap 3 not 2 : {agree_digits(r_bad, est_full)} digits"
          f"  {'(diverges, good)' if agree_digits(r_bad, est_full) < 3 else '(FAILED)'}")
    if d_hit < want or agree_digits(r_nohalf, est_full) >= 3 \
            or agree_digits(r_bad, est_full) >= 3:
        return 1

    # --- hmax / dps stability: the honest digit count for r_struct ----------
    hsmall = hmax - 200
    phis = phi_vector(xc, hsmall)
    rs = (contract(feed_vector(xc, hsmall, cap=2), phis, hsmall)
          / contract(feed_vector(xc, hsmall, cap=None), phis, hsmall) / 2)
    d_h = agree_digits(r_struct, rs)
    print(f"\n## r_struct's own precision")
    print(f"  hmax {hmax} vs hmax {hsmall}: {d_h} digits agree"
          f" -- truncation is x^hmax, so this is a FLOOR for hmax {hmax},"
          f" set by the smaller run")
    print(f"  usable digits of r_struct: {min(d_h, args.dps)}"
          f" -- structural, conditional on the rank-one residue reading")
    if args.emit:
        with open(args.emit, 'w') as fh:
            fh.write(nstr(mu, min(d_mu, args.dps)) + "\n")
            fh.write(nstr(r_struct, min(d_h, args.dps)) + "\n")
        print(f"  wrote mu and r_struct to {args.emit}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
