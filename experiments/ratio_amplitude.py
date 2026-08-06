#!/usr/bin/env python3
"""Amplitude ratio of two series sharing a dominant growth constant.

docs/middle-kingdom-followups-plan.md Phase 0, Table B: (dir4, HV-convex)
against unrestricted HV-convex, both by area. a_dir4(n) and a_HV(n) share
the same dominant singularity (mu = 3.1289..., checked to 49+ digits in
results/middle-kingdom-phase3.md and results/convex-polyplets.md), so the
ratio r(n) = a_dir4(n)/a_HV(n) converges to a constant, the amplitude ratio
C_dir4/C_HV -- unlike experiments/convex_growth.py, which extrapolates a
sequence of *term ratios* a(n+1)/a(n) to a growth constant, this script
extrapolates the *already-converging* sequence r(n) itself.

Method, same discipline as convex_growth.py:
  1. Aitken delta-squared, applied directly to the tail of r(n) (r(n) plays
     the role convex_growth.py's r_n = a(n+1)/a(n) plays there: a sequence
     converging geometrically to the quantity of interest).
  2. Trusted digits, measured not asserted: rerun on both series truncated
     by --drop terms and report how many digits the two Aitken estimates
     agree to, minus a 2-digit guard.
  3. PSLQ on (1, r, ..., r^d) at the trusted precision, in a handful of
     explicit (max degree, max coefficient height) boxes -- unlike
     convex_growth.py's single swept box, Table B's boxes shrink in degree
     as they grow in height (the capacity test bites at different sizes),
     so each box is passed explicitly.

Usage: python3 experiments/ratio_amplitude.py <series1> <series2>
         [--prec 500] [--window 60] [--drop 100]
         [--boxes "12:100,5:10000,3:1000000,2:100000000"]
"""
import argparse
import sys

from mpmath import mp, mpf, nstr, pslq


def read_terms(path):
    vals = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            vals.append(int(line.split()[-1]))
    return vals


def aitken(seq):
    out = []
    for i in range(len(seq) - 2):
        d1 = seq[i + 1] - seq[i]
        d2 = seq[i + 2] - 2 * seq[i + 1] + seq[i]
        out.append(seq[i] - d1 * d1 / d2 if d2 != 0 else seq[i])
    return out


def accelerate(vals, window, levels=8):
    """Aitken-accelerate a sequence that already converges to a constant."""
    w = min(window, len(vals))
    tail = vals[-w:]
    seq, est = tail, None
    for _ in range(levels):
        if len(seq) < 3:
            break
        seq = aitken(seq)
        est = seq[-1]
    return tail[-1], est


def agree_digits(x, y):
    if x == y:
        return mp.dps
    d = abs(x - y) / abs(x)
    return int(-mp.log10(d)) if d > 0 else mp.dps


def ratio_series(a1, a2, n_to):
    N = min(n_to, len(a1), len(a2))
    return [mpf(a1[n - 1]) / mpf(a2[n - 1]) for n in range(1, N + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('series1', help='numerator series (e.g. dir4)')
    ap.add_argument('series2', help='denominator series (e.g. unrestricted)')
    ap.add_argument('--prec', type=int, default=500)
    ap.add_argument('--window', type=int, default=60)
    ap.add_argument('--drop', type=int, default=100,
                     help='terms dropped for the trusted-digit cross-check')
    ap.add_argument('--boxes', default='12:100,5:10000,3:1000000,2:100000000',
                     help='comma-separated maxdegree:maxcoeff PSLQ boxes')
    args = ap.parse_args()
    mp.dps = args.prec

    a1 = read_terms(args.series1)
    a2 = read_terms(args.series2)
    N = min(len(a1), len(a2))
    print(f"# {args.series1} / {args.series2}: N={N} shared terms,"
          f" working precision {mp.dps} digits")

    r_full = ratio_series(a1, a2, N)
    raw_full, est_full = accelerate(r_full, args.window)
    r_drop = ratio_series(a1, a2, N - args.drop)
    raw_drop, est_drop = accelerate(r_drop, args.window)

    d_raw = agree_digits(raw_full, raw_drop)
    d_ait = agree_digits(est_full, est_drop)
    trusted = max(0, min(d_raw, d_ait) - 2)
    print(f"\n## trusted digits (cross-check n={N - args.drop} vs n={N})")
    print(f"  raw r(N) vs r(N-{args.drop}):        ~{d_raw} digits")
    print(f"  Aitken estimate, N vs N-{args.drop}:  ~{d_ait} digits")
    print(f"  => TRUSTED (min of the two, minus 2 guard): {trusted} digits")

    r = est_full if est_full is not None else raw_full
    print(f"\n## amplitude ratio a1(n)/a2(n) -> {trusted} trusted digits"
          f" (n={N - args.drop} vs n={N}):")
    print("  " + nstr(r, max(trusted, 5)))

    if trusted < 10:
        print("\n(too few trusted digits for a meaningful PSLQ search)")
        return 0

    print(f"\n## PSLQ: integer polynomial with the amplitude ratio as a root,"
          f" precision fed = {trusted} digits")
    saved = mp.dps
    mp.dps = trusted
    r_t = +r
    any_hit = False
    for box in args.boxes.split(','):
        deg_s, height_s = box.split(':')
        max_deg, max_height = int(deg_s), int(height_s)
        found_here = False
        for d in range(2, max_deg + 1):
            vec = [r_t ** k for k in range(d + 1)]
            rel = pslq(vec, maxcoeff=max_height, maxsteps=200000,
                       tol=mpf(10) ** (-(trusted - 5)))
            if not rel:
                continue
            height = max(abs(c) for c in rel)
            capacity = (d + 1) * mp.log10(max(height, 2))
            verdict = ("REJECTED-ARTIFACT" if capacity > 0.5 * trusted
                       else "SURVIVES-CAPACITY-TEST")
            print(f"  degree <= {max_deg:2d} height <= {max_height:g}:"
                  f" hit at degree {d}, height {height},"
                  f" capacity {float(capacity):.0f} of {trusted} -> {verdict}")
            found_here = True
            any_hit = True
            if verdict.startswith('SURVIVES'):
                any_hit = 'survives'
        if not found_here:
            print(f"  degree <= {max_deg:2d} height <= {max_height:g}: none")
    mp.dps = saved
    if any_hit != 'survives':
        print(f"\n  => NO relation in any in-capacity box: "
              + ", ".join(f"degree <= {b.split(':')[0]} at height <= "
                           f"{int(b.split(':')[1]):g}" for b in args.boxes.split(',')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
