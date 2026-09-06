#!/usr/bin/env python3
"""Kurkov's conjectured continued fraction for A225114, and where its poles are.

results/subclasses.md identifies the staircase king animals (A225114)
as the block that carries mu, and the spectrum measured by
experiments/prony_spectrum.py says the staircase series behaves like a sum of
exponentials 3.12894..., 1.50504..., 1.28433..., -1.25776..., i.e. like a
function meromorphic in a disc, with poles at the reciprocals of those.

The OEIS entry (verified 2026-08-06, experiments/oeis_lookup.py --full
id:A225114) carries exactly one formula, a CONJECTURE by Mikhail Kurkov
(Sep 2024):

    g.f. = 1/(2 - 1/(1 - x/(1 - x/(1 - x^2/(1 - x^2/(1 - x^3/(1 - x^3/...)))))))

i.e. partial numerators x, x, x^2, x^2, x^3, x^3, ... .  Truncating it at depth
D gives a RATIONAL function; this script computes that convergent exactly in
Z[x], checks it against the banked series, and asks whether its poles settle on
the reciprocals of the measured spectrum.  They do, which is why the write-up
names this conjecture as the concrete route to a proof of the subdominant
identification: a proved continued fraction of this shape would supply the
meromorphic continuation and the spectral gap that the coefficient-level
argument cannot reach.

GREEN test: the depth-D convergent must reproduce the banked A225114 terms up
to the order the truncation is faithful to.
RED control: change one partial numerator (x^2 -> x^3 at one level) and the
convergent must STOP reproducing them.

Usage: python3 experiments/staircase_cf_poles.py [--depth 40] [--terms 40]
Target machine: gympie (laptop).  MEASURED: depth 60 in about 20 s.
"""
import argparse
import sys

from mpmath import mp, mpf, nstr, polyroots

from seriestools import read_terms

STAIR = 'results/mk_stair_terms_n700.txt'
# measured by experiments/prony_spectrum.py on the 700-term staircase series
# (order 10, dps 1500); trusted digit counts are in
# results/subdominant_identification.log.
MEASURED = ['3.12894326973088625227744799539',
            '1.50504922775900393466569424779',
            '1.28433727098118142855105776084',
            '-1.25776216033063548324174210622']


def padd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
            for i in range(n)]


def pshift(a, k):
    return [0] * k + list(a)


def psub(a, b):
    return padd(a, [-c for c in b])


def convergent(depth, red=False):
    """Numerator, denominator of the depth-D truncation, as int coeff lists."""
    # T_k = 1 - a_k / T_(k+1); with T_(k+1) = N/Dn:  T_k = (N - a_k*Dn) / N
    N, Dn = [1], [1]
    for k in range(depth, 0, -1):
        e = (k + 1) // 2                       # a_k = x^e, e = ceil(k/2)
        if red and k == 4:
            e += 1                             # RED: one wrong partial numerator
        N, Dn = psub(N, pshift(Dn, e)), N
    # G = Dn / N,  F = 1 / (2 - G) = N / (2N - Dn)
    return N, psub([2 * c for c in N], Dn)


def series(num, den, terms):
    """Power-series coefficients of num/den to `terms` terms (den[0] != 0)."""
    out = []
    for n in range(terms):
        s = num[n] if n < len(num) else 0
        for j in range(1, min(n, len(den) - 1) + 1):
            s -= den[j] * out[n - j]
        q, r = divmod(s, den[0])
        if r:
            raise ValueError('non-integer coefficient: CF is not what we think')
        out.append(q)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--depth', type=int, default=40)
    ap.add_argument('--terms', type=int, default=40)
    ap.add_argument('--dps', type=int, default=60)
    args = ap.parse_args()
    mp.dps = args.dps

    # A225114 has offset 0 with a(0) = 1; the repo's staircase file starts at
    # n = 1, so the g.f.'s coefficients are 1 followed by the file's terms.
    want = [1] + read_terms(STAIR)[:args.terms]

    num, den = convergent(args.depth)
    got = series(num, den, len(want))
    agree = next((i for i in range(len(want)) if got[i] != want[i]), len(want))
    print(f"depth {args.depth}: convergent reproduces A225114 for n = 0..{agree - 1}"
          f" ({agree} terms)")
    if agree < min(args.terms, args.depth) // 2:
        print("FAIL: the conjectured CF does not reproduce the banked series")
        return 1
    print(f"  first terms: {got[:10]}")

    rn, rd = convergent(args.depth, red=True)
    rgot = series(rn, rd, len(want))
    ragree = next((i for i in range(len(want)) if rgot[i] != want[i]), len(want))
    if ragree >= agree:
        print("FAIL: RED control (one partial numerator changed) did not diverge")
        return 1
    print(f"ok   RED control diverges at n = {ragree} (true CF: n = {agree})")

    print("\n## poles of the convergent, as 1/x, against the measured spectrum")
    for d in (args.depth // 2, args.depth * 3 // 4, args.depth):
        n2, d2 = convergent(d)
        roots = polyroots([mpf(c) for c in reversed(d2)], maxsteps=800,
                          extraprec=40 * mp.prec)
        lam = sorted((1 / r for r in roots if abs(r) > mpf(10) ** -40),
                     key=lambda z: -abs(z))
        line = []
        for want_s in MEASURED:
            w = mpf(want_s)
            best = min(lam, key=lambda z: abs(z - w))
            rel = abs(best - w) / abs(w)
            line.append(int(-mp.log10(rel)) if rel > 0 else mp.dps)
        print(f"  depth {d:3d}: agreement with the four measured lambda, in "
              f"digits: {line}")
        if d == args.depth:
            for want_s in MEASURED:
                w = mpf(want_s)
                best = min(lam, key=lambda z: abs(z - w))
                print(f"     measured {want_s:<32} CF pole 1/x = "
                      f"{nstr(best, 20)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
