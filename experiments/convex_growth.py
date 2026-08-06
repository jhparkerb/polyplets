#!/usr/bin/env python3
"""Growth constant, subexponential exponent, and algebraicity test for a series.

docs/middle-kingdom-plan.md Phase 2b. Given an exact integer series file
("n value" per line), assume a(n) ~ C mu^n n^theta and pin mu and theta.

Diagnostics, in the order they are meant to be read:

1. Ratio sequence r_n = a(n+1)/a(n) at high precision, and the ratio of its
   successive differences. That second number is the model discriminator: it
   settles on a constant < 1 when the correction is *geometric* (isolated
   subdominant singularity, theta = 0) and drifts to 1 when the correction is
   a power law (theta != 0, branch point).
2. Aitken/Shanks (the right accelerator for the geometric case) and
   Richardson-in-1/n (the right one for the power-law case) on the ratio tail.
3. Trusted digits, measured not asserted: rerun the whole pipeline on the
   series truncated by --drop terms and report how many digits the two
   estimates share. Extrapolation error falls with N, so the shorter series is
   strictly worse and the agreement is a conservative floor.
4. theta from n*(r_n/mu - 1) -- tends to theta under the power-law model, to 0
   under the geometric one.
5. PSLQ on (1, mu, ..., mu^d) for d <= --algdeg, coefficient height <=
   --maxcoeff, run at the *trusted* precision only. A relation is reported as
   REJECTED-ARTIFACT unless (d+1)*log10(height) is comfortably below the
   trusted digit count -- PSLQ always finds a relation once the unknowns can
   absorb the input precision, and that hit means nothing.

Usage: python3 experiments/convex_growth.py <terms_file> [--prec 400]
         [--algdeg 10] [--maxcoeff 10^15] [--window 40] [--drop 30]
"""
import argparse
import sys

from mpmath import mp, mpf, nstr, pslq, polyroots

from seriestools import read_terms, aitken, agree_digits


def richardson(seq, n0):
    """One Richardson step in 1/n (seq[i] belongs to n = n0 + i)."""
    return [(n0 + i + 1) * seq[i + 1] - (n0 + i) * seq[i]
            for i in range(len(seq) - 1)]


def accelerate(a, window, levels=6):
    """Return (raw_tail_ratio, aitken_estimate, richardson_estimate)."""
    N = len(a)
    ratios = [mpf(a[i + 1]) / mpf(a[i]) for i in range(N - 1)]
    w = min(window, len(ratios) - 4)
    tail = ratios[-w:]
    n0 = N - w

    seq, est_a = tail, None
    for _ in range(levels):
        if len(seq) < 3:
            break
        seq = aitken(seq)
        est_a = seq[-1]

    seq, k, est_r = tail, n0, None
    for _ in range(levels):
        if len(seq) < 2:
            break
        seq = richardson(seq, k)
        est_r = seq[-1]

    return ratios, ratios[-1], est_a, est_r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('terms')
    ap.add_argument('--prec', type=int, default=400)
    ap.add_argument('--algdeg', type=int, default=10)
    ap.add_argument('--maxcoeff', type=int, default=10 ** 15)
    ap.add_argument('--window', type=int, default=40)
    ap.add_argument('--drop', type=int, default=30,
                    help='terms dropped for the trusted-digit cross-check')
    ap.add_argument('--trust', type=int, default=0,
                    help='override the trusted-digit count. ONLY defensible '
                         'when the discriminator says the correction is '
                         'geometric: Richardson-in-1/n is then the wrong '
                         'accelerator and its disagreement with Aitken is '
                         'not evidence about mu. The two cross-checks that '
                         'stay valid (raw and Aitken, N vs N-drop) are still '
                         'printed -- keep the override under the smaller.')
    args = ap.parse_args()
    mp.dps = args.prec

    a = read_terms(args.terms)
    N = len(a)
    print(f"# {args.terms}: {N} terms, working precision {mp.dps} digits")

    ratios, raw, est_a, est_r = accelerate(a, args.window)

    print("\n## model discriminator: d_n = r_n - r_(n-1), and d_n / d_(n-1)")
    print("   constant < 1 => geometric correction (theta = 0);"
          " -> 1 => power law (theta != 0)")
    for i in range(N - 6, N - 1):
        d1 = ratios[i] - ratios[i - 1]
        d0 = ratios[i - 1] - ratios[i - 2]
        rr = d1 / d0 if d0 != 0 else mpf(0)
        print(f"  n={i+1:5d}  d={nstr(d1, 8):>16}  d_n/d_(n-1)={nstr(rr, 12)}")

    print("\n## theta probe: n*(r_n/mu - 1) with mu = raw tail ratio")
    for i in range(N - 6, N - 1):
        n = i + 1
        print(f"  n={n:5d}  {nstr(n * (ratios[i] / raw - 1), 12)}")

    # Trusted digits: same pipeline on a strictly shorter series.
    _, raw_s, est_a_s, est_r_s = accelerate(a[:N - args.drop], args.window)
    d_raw = agree_digits(raw, raw_s)
    d_ait = agree_digits(est_a, est_a_s) if est_a and est_a_s else 0
    d_cross = agree_digits(est_a, est_r) if est_a and est_r else 0
    print(f"\n## trusted digits (cross-checks, --drop {args.drop})")
    print(f"  raw tail ratio, N vs N-{args.drop}:      ~{d_raw} digits")
    print(f"  Aitken,         N vs N-{args.drop}:      ~{d_ait} digits")
    print(f"  Aitken vs Richardson, full N:      ~{d_cross} digits")
    trusted = max(0, min(d_raw, d_ait, d_cross) - 2)
    print(f"  => TRUSTED (min of the three, minus 2 guard): {trusted} digits")
    if args.trust:
        trusted = args.trust
        print(f"  => OVERRIDDEN by --trust: {trusted} digits")

    mu = est_a if est_a is not None else raw
    print(f"\n## mu to {trusted} digits")
    print("  " + nstr(mu, max(trusted, 5)))

    # Amplitude C = lim a(n)/mu^n. Under the geometric model this converges as
    # fast as the ratio does, so it inherits the same trusted-digit count; the
    # printed pair of successive values is the check.
    for n in (N - 1, N):
        print(f"  C = a({n})/mu^{n} = "
              + nstr(mpf(a[n - 1]) / mu ** n, max(min(trusted, 40), 5)))

    if trusted < 20:
        print("\n(too few trusted digits for a meaningful PSLQ search)")
        return 0

    print(f"\n## PSLQ: integer polynomial with mu as a root."
          f" degree <= {args.algdeg}, |coeff| <= {args.maxcoeff},"
          f" precision fed = {trusted} digits")
    saved = mp.dps
    mp.dps = trusted
    mu_t = +mu
    found = []
    for d in range(2, args.algdeg + 1):
        vec = [mu_t ** k for k in range(d + 1)]
        rel = pslq(vec, maxcoeff=args.maxcoeff, maxsteps=200000,
                   tol=mpf(10) ** (-(trusted - 5)))
        if not rel:
            print(f"  degree {d:2d}: none")
            continue
        height = max(abs(c) for c in rel)
        capacity = (d + 1) * mp.log10(max(height, 2))
        verdict = ("REJECTED-ARTIFACT" if capacity > 0.5 * trusted
                   else "SURVIVES-CAPACITY-TEST")
        print(f"  degree {d:2d}: relation height {height},"
              f" capacity {float(capacity):.0f} of {trusted} digits"
              f" -> {verdict}")
        if verdict.startswith('SURVIVES'):
            mp.dps = saved
            # Once a relation of degree d is found, every larger degree admits
            # it padded with leading zeros (x^k * P(x)); strip them, or
            # polyroots divides by a zero leading coefficient.
            coeffs = list(reversed(rel))
            while len(coeffs) > 1 and coeffs[0] == 0:
                coeffs.pop(0)
            roots = polyroots([mpf(c) for c in coeffs], maxsteps=400,
                              extraprec=500)
            best = min(roots, key=lambda r: abs(r - mu))
            print(f"      nearest root agrees with mu to"
                  f" ~{agree_digits(mu, best)} digits (trusted {trusted})")
            # coefficients low-order first, i.e. sum_k rel[k] * mu^k = 0
            print(f"      relation: {list(rel)}")
            found.append((d, rel))
            mp.dps = trusted
    mp.dps = saved
    if not found:
        print(f"  => NO integer relation survives in the searched box"
              f" (degree <= {args.algdeg}, height <= {args.maxcoeff}):"
              f" mu is not algebraic of that size.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
