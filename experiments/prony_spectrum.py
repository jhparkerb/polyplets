#!/usr/bin/env python3
"""Prony/Hankel reading of a series' exponential spectrum, at high precision.

An independent alternative to experiments/convex_growth.py's Aitken-on-ratios
and to experiments/dir4_descent_block.py's "peel two exponentials by hand".
Where those extract one constant at a time and need the model
a(n) ~ C mu^n (1 + c rho^n) assumed in advance, this fits

    a(n) ~ sum_{i=1..k} C_i lambda_i^n

directly: solve the k x k Hankel system for the constant-coefficient linear
recurrence that the tail of the series obeys best, and read ALL k of the
lambda_i off its characteristic polynomial at once.  The dominant, subdominant
and sub-subdominant growth constants come out of the same solve, so the
"subdominant of series X equals the dominant of series Y" question is a
comparison between two numbers each measured directly, with no peeling.

Honesty about what that measures: the true generating function is not a finite
sum of exponentials, so lambda_1..lambda_k are approximations whose error is
governed by the modes the fit drops.  The script therefore reports agreement
between three independent fits -- (N, k), (N - shift, k) and (N, k + 1) -- and
the TRUSTED digit count is the minimum of those agreements, minus a guard.
That is the same discipline convex_growth.py uses, applied to every eigenvalue
rather than only to the leading one.

RED-first self-test (run on every invocation, --no-selftest to skip):
  GREEN  order-k Prony on an exact k-term exponential sum recovers every
         exponent to near the working precision
  RED    order-(k-1) on the same data must NOT recover them

Usage: python3 experiments/prony_spectrum.py TERMS [--order 6] [--dps 1200]
                [--shift 50] [--show 5]
Target machine: gympie (laptop).  MEASURED: a 700-term file at order 8 and
dps 1200 takes about 2 s.  Nothing to resume; SIGINT is enough.
"""
import argparse
import sys

from mpmath import mp, mpf, mpc, nstr, matrix, lu_solve, polyroots


def read_terms(path):
    vals = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith('#'):
                vals.append(int(line.split()[-1]))
    return vals


def prony(a, k, end):
    """Fit a(n) = sum_i C_i lambda_i^n on a[end-2k .. end-1]; return lambdas.

    `end` is an exclusive index into `a` (1-based series values in a[0..]).
    """
    n0 = end - 2 * k
    if n0 < 0:
        raise ValueError('window runs off the front of the series')
    scale = mpf(a[n0])
    w = [mpf(a[n0 + i]) / scale for i in range(2 * k)]
    A = matrix(k, k)
    b = matrix(k, 1)
    for i in range(k):
        for j in range(k):
            A[i, j] = w[i + j]
        b[i] = w[i + k]
    c = lu_solve(A, b)                       # a(n+k) = sum_j c[j] a(n+j)
    # characteristic polynomial x^k - c[k-1] x^(k-1) - ... - c[0]
    coeffs = [mpf(1)] + [-c[k - 1 - j] for j in range(k)]
    roots = polyroots(coeffs, maxsteps=500, extraprec=8 * mp.prec)
    return sorted(roots, key=lambda z: -abs(z))


def agree_digits(x, y):
    if x == y:
        return mp.dps
    d = abs(x - y) / abs(x) if x != 0 else abs(y)
    return int(-mp.log10(d)) if d > 0 else mp.dps


def nearest_agree(z, others):
    """Best agreement between z and any root in `others`.

    Cross-checking eigenvalue i of one fit against eigenvalue i of another is
    wrong: a fit of different order or window can insert a spurious root and
    shift every index below it, which then reads as zero trusted digits for
    eigenvalues that are in fact converged.  Match by proximity instead.
    """
    return max((agree_digits(z, w) for w in others), default=0)


def selftest():
    """RED-first: order k recovers a k-exponential sum, order k-1 does not."""
    saved = mp.dps
    mp.dps = 120
    lam = [mpf('2.5145796'), mpf('1.5050492'), mpf('0.71828')]
    amp = [mpf('3.25'), mpf('-1.125'), mpf('0.5')]
    a = [sum(A * L ** n for A, L in zip(amp, lam)) for n in range(1, 41)]
    a_i = [x for x in a]                       # already mpf; prony only reads
    got = prony(a_i, 3, len(a_i))
    ok = min(agree_digits(g, l) for g, l in zip(got, lam))
    bad = prony(a_i, 2, len(a_i))
    ok_bad = agree_digits(bad[0], lam[0])
    mp.dps = saved
    if ok < 60:
        return False, f"GREEN self-test: order 3 recovered only {ok} digits"
    if ok_bad > 40 or ok_bad > ok // 2:
        return False, (f"RED self-test: order 2 recovered {ok_bad} digits of "
                       "lambda_1 -- the control did not diverge")
    return True, (f"selftest ok: order 3 recovers all three exponents to "
                  f"{ok} digits; order 2 gets lambda_1 to only {ok_bad}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('terms')
    ap.add_argument('--order', type=int, default=6)
    ap.add_argument('--dps', type=int, default=1200)
    ap.add_argument('--shift', type=int, default=50)
    ap.add_argument('--show', type=int, default=4)
    ap.add_argument('--digits', type=int, default=30)
    ap.add_argument('--no-selftest', action='store_true')
    args = ap.parse_args()
    mp.dps = args.dps

    if not args.no_selftest:
        ok, msg = selftest()
        print(('ok   ' if ok else 'FAIL ') + msg)
        if not ok:
            return 1

    a = read_terms(args.terms)
    N = len(a)
    print(f"\n# {args.terms}: {N} terms, order {args.order}, dps {mp.dps}")

    base = prony(a, args.order, N)
    alt_n = prony(a, args.order, N - args.shift)
    alt_k = prony(a, args.order + 1, N)

    print(f"{'i':>2} {'|lambda_i|':>14}  trusted digits (min of N-{args.shift} "
          f"and order+1 agreement, minus 2)")
    out = []
    for i in range(min(args.show, args.order)):
        z = base[i]
        d1 = nearest_agree(z, alt_n)
        d2 = nearest_agree(z, alt_k)
        trust = max(0, min(d1, d2) - 2)
        im = abs(z.imag) / abs(z) if isinstance(z, mpc) else 0
        tag = ' (complex)' if im > mpf(10) ** (-20) else ''
        print(f"{i + 1:>2} {nstr(abs(z), 14):>14}   window {d1:4d}   "
              f"order {d2:4d}   => TRUSTED {trust}{tag}")
        print("     " + nstr(z, max(min(trust, args.digits), 5)))
        out.append((z, trust))
    return 0


if __name__ == '__main__':
    sys.exit(main())
