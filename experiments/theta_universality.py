#!/usr/bin/env python3
"""Are king and square lattice animals in the same universality class?

`results/closed-doors.md` idea 6.2, the half of the Parisi-Sourlas item
that survived 6.1's closure because it does not run through the strip ladder:

> Is the king lattice in the same class as the square lattice?  It must be if
> universality holds.  That is a *prediction*, testable against the two theta
> fits, rather than a count.

`results/growth-constant.md` pins the king exponent at theta = -1.000(1)
from 40 terms by first-order inhomogeneous differential approximants.  The
square-lattice exponent is not measured anywhere in this repo -- it is quoted
from the literature, which is a different kind of statement.

The test this script runs is deliberately narrow, and its narrowness is the
point: **the same code, the same approximant spectrum, the same number of
terms, on both lattices.**  A theta difference then cannot be a method
artifact, because there is only one method.  Running square at its full length
as well says how much of any agreement is the extra terms.

Series:
  king   A006770, n = 1..40   -- results/b006770_upload.txt (banked, gated)
  square A001168, n = 1..70   -- OEIS b-file, fetched read-only; a(57)-a(70)
                                 are Barequet and Ben-Shachar (2024), which is
                                 outside this project entirely and is the
                                 nearest thing to an external oracle available.

RED controls (all must fire):
  - a synthetic series with theta = -0.5 must NOT be reported as -1, on both
    lambda scalings, or the method is just printing the universal value;
  - a synthetic series at the square lambda with theta = -1 must recover it,
    so a null result on real square data is not the scaling being wrong;
  - the square series must be rejected if its first terms do not match the
    known head 1, 2, 6, 19, 63, 216 -- a wrong file must not be analysed.

Usage: python3 experiments/theta_universality.py [--square-bfile PATH]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series_da import spectrum, load_sequence  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The head of A001168 (fixed polyominoes), n = 1..6.  A file that does not
# start this way is not the square-lattice series and must not be analysed.
SQUARE_HEAD = [1, 2, 6, 19, 63, 216]

# Rescaling anchors: the series is divided by lam0^n before the linear solve,
# so lam0 must be in the right ballpark for each lattice or the system is
# badly conditioned.  Neither value is an input to the answer -- the
# robustness sweep below varies them.
LAM0_KING = 7.11
LAM0_SQUARE = 4.06


def load_square(path):
    """A001168 from an OEIS b-file; returns [None, a(1), a(2), ...]."""
    banked = {}
    with open(path) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            p = ln.split()
            if len(p) == 2 and p[0].lstrip("-").isdigit():
                banked[int(p[0])] = int(p[1])
    nmax = max(banked)
    seq = [None] + [banked[n] for n in range(1, nmax + 1)]
    head = seq[1:1 + len(SQUARE_HEAD)]
    if head != SQUARE_HEAD:
        raise ValueError(
            f"not A001168: head is {head}, expected {SQUARE_HEAD}")
    return seq


def median(vs):
    vs = sorted(vs)
    return vs[len(vs) // 2]


def theta_of(seq, N, lam0):
    """Median (lambda, theta) over the approximant spectrum, or None."""
    ests = spectrum(seq, N, lam0)
    if not ests:
        return None
    return median([e[0] for e in ests]), median([e[1] for e in ests]), len(ests)


def red_controls():
    ok = True

    # 1. theta = -0.5 must not come back as -1, at either lattice's scaling.
    for lam_t, lam0 in ((7.11, LAM0_KING), (4.06, LAM0_SQUARE)):
        synth = [None] + [round(n ** -0.5 * lam_t ** n) for n in range(1, 41)]
        r = theta_of(synth, 40, lam0)
        good = r is not None and abs(r[1] - (-1.0)) > 0.2
        print(f"RED  theta=-0.5 at lambda={lam_t} is not reported as -1 "
              f"(got {r[1]:+.4f})  {'OK' if good else 'FAILED'}")
        ok &= good

    # 2. theta = -1 at the SQUARE lambda must be recovered, so that a null
    #    result on real square data cannot be blamed on the scaling.
    synth = [None] + [round(n ** -1.0 * 4.06 ** n) for n in range(1, 41)]
    r = theta_of(synth, 40, LAM0_SQUARE)
    good = r is not None and abs(r[1] + 1.0) < 0.05 and abs(r[0] - 4.06) < 0.01
    print(f"RED  theta=-1 at the square lambda is recovered "
          f"(lambda={r[0]:.4f}, theta={r[1]:+.4f})  {'OK' if good else 'FAILED'}")
    ok &= good

    # 3. A file with the wrong head must be refused.
    bad = os.path.join(ROOT, "results", "b006770_upload.txt")
    try:
        load_square(bad)
        print("RED  a non-A001168 b-file is refused  FAILED (no raise)")
        ok = False
    except ValueError:
        print("RED  a non-A001168 b-file is refused  OK")

    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--square-bfile", default=os.path.join(
        ROOT, "results", "b001168_external.txt"))
    args = ap.parse_args()

    king = load_sequence()
    square = load_square(args.square_bfile)
    n_sq = len(square) - 1

    print("=" * 70)
    print("Universality: the same DA spectrum on king and square")
    print("=" * 70)
    print(f"king   A006770  n = 1..40   (banked)")
    print(f"square A001168  n = 1..{n_sq}   ({args.square_bfile})")
    print()

    print("--- 1. Matched term count: both at N = 40 ---")
    k = theta_of(king, 40, LAM0_KING)
    s = theta_of(square, 40, LAM0_SQUARE)
    print(f"  king   N=40: lambda = {k[0]:.4f}  theta = {k[1]:+.4f}  "
          f"({k[2]} approximants)")
    print(f"  square N=40: lambda = {s[0]:.4f}  theta = {s[1]:+.4f}  "
          f"({s[2]} approximants)")
    print(f"  difference in theta: {abs(k[1] - s[1]):.4f}")
    print()

    print("--- 2. Square at full length ---")
    for N in (40, 50, 60, n_sq):
        if N > n_sq:
            continue
        r = theta_of(square, N, LAM0_SQUARE)
        if r:
            print(f"  square N={N:>2}: lambda = {r[0]:.5f}  "
                  f"theta = {r[1]:+.5f}  ({r[2]} approximants)")
    print()

    print("--- 3. King, for the same convergence-in-N picture ---")
    for N in (28, 32, 36, 40):
        r = theta_of(king, N, LAM0_KING)
        if r:
            print(f"  king   N={N:>2}: lambda = {r[0]:.5f}  "
                  f"theta = {r[1]:+.5f}  ({r[2]} approximants)")
    print()

    print("--- 4. Anchoring: theta must not depend on the rescaling ---")
    for label, seq, N, anchors in (
            ("king  ", king, 40, (6.8, 7.0, 7.11, 7.3, 7.5)),
            ("square", square, n_sq, (3.8, 3.95, 4.06, 4.2, 4.4))):
        out = []
        for lam0 in anchors:
            r = theta_of(seq, N, lam0)
            out.append(f"{lam0}:{r[1]:+.4f}" if r else f"{lam0}:--")
        print(f"  {label} theta vs lambda0: " + "  ".join(out))
    print()

    print("--- RED controls ---")
    if not red_controls():
        print("\nSELFTEST: FAILED")
        return 1
    print("\nSELFTEST: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
