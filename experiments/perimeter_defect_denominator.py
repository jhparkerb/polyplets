#!/usr/bin/env python3
"""Which cyclotomic denominator does a defect class actually have?

A closed-form FIT needs period*(degree+1+holdouts) points above the onset --
54 for a period-6 degree-6 class -- which is why k=6 needs n near 80. The
DENOMINATOR needs far fewer: if

    G_k^tail(x) = sum_{n >= onset} A(n,k) x^n = x^onset * N(x) / D(x)

with deg N < deg D, then multiplying the measured tail series by a candidate D
must kill every coefficient above x^(onset + deg D - 1). With the census to
n = 60 and deg D = 16 that is ~20 consecutive exact zeros the fit never saw --
a decisive test of D from data that cannot yet fit the class.

Two things are scanned rather than assumed:

  * THE ONSET. A closed form valid from `onset` is also valid from anything
    larger, so the division test passes for every onset >= the true one. The
    SMALLEST onset that passes is therefore the real one, and finding it tests
    the onset law k(k+1)/2 + 3 independently of any interpolation.
  * MINIMALITY OF D. Any multiple of the true denominator also passes. So each
    candidate that passes is retested with one factor removed at a time; a
    denominator is only reported as THE answer if every reduction fails.

    python3 experiments/perimeter_defect_denominator.py results/perimdefect_square8_n60_k6.txt --k 6

results/perimeter.md, "What this run did not buy".
"""

from __future__ import annotations

import argparse
import itertools
import sys
from collections import defaultdict

PHI = {1: [1, -1], 2: [1, 1], 3: [1, 1, 1], 4: [1, 0, 1],
       5: [1, 1, 1, 1, 1], 6: [1, -1, 1]}


def read_census(path, k):
    pts = defaultdict(int)
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        if int(f[1]) == k:
            pts[int(f[0])] += int(f[-1])
    return dict(pts)


def polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def build_den(exps):
    d = [1]
    for base, e in sorted(exps.items()):
        for _ in range(e):
            d = polymul(d, PHI[base])
    return d


def passes(pts, onset, nmax, exps):
    """Does multiplying the tail series by D kill everything above deg D - 1?"""
    den = build_den(exps)
    degD = len(den) - 1
    ser = [0] * (nmax + 1)
    for n in range(onset, nmax + 1):
        ser[n] = pts.get(n, 0)
    prod = polymul(ser, den)
    hi = onset + degD
    tail = prod[hi:nmax + 1]
    return (len(tail) >= 6) and all(c == 0 for c in tail), len(tail)


def fmt(exps):
    return " ".join("Phi_%d^%d" % (b, e) for b, e in sorted(exps.items()) if e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("census")
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--onset-scan", type=int, nargs=2, default=None,
                    help="lo hi (default: T_k+3 minus 8 .. plus 8)")
    args = ap.parse_args()

    k = args.k
    pts = read_census(args.census, k)
    if not pts:
        print("no k=%d rows in %s" % (k, args.census))
        return 1
    nmax = max(pts)
    pred_onset = k * (k + 1) // 2 + 3
    lo, hi = args.onset_scan or (max(1, pred_onset - 8), pred_onset + 8)
    print("census %s  k=%d  n<=%d   predicted onset T_k+3 = %d"
          % (args.census, k, nmax, pred_onset))
    print()

    # The predicted denominator, and neighbors of it in every exponent.
    base = {1: k + 1, 2: max(0, k - 1), 3: max(0, k - 4)}
    cands = []
    for d3 in range(0, max(1, k - 4) + 2):
        for d4 in (0, 1, 2):
            for d2 in (max(0, k - 2), max(0, k - 1), k):
                e = {1: k + 1, 2: d2, 3: d3}
                if d4:
                    e[4] = d4
                if e not in cands:
                    cands.append(e)
    # also try a couple of Phi_1 exponents
    for d1 in (k, k + 2):
        e = dict(base)
        e[1] = d1
        if e not in cands:
            cands.append(e)

    print("== smallest (onset, denominator) that passes the division test")
    winners = []
    for onset in range(lo, hi + 1):
        for e in cands:
            ok, spare = passes(pts, onset, nmax, e)
            if ok:
                winners.append((onset, e, spare))
    if not winners:
        print("   NOTHING PASSES -- either the census is too short or the")
        print("   assumed shape (rational with these cyclotomic factors) is wrong.")
        return 1

    best_onset = min(w[0] for w in winners)
    print("   smallest onset that admits ANY denominator: %d  (predicted %d) %s"
          % (best_onset, pred_onset,
             "MATCH" if best_onset == pred_onset else "MISMATCH"))
    print()
    print("   denominators passing at onset=%d:" % best_onset)
    at_best = [w for w in winners if w[0] == best_onset]
    minimal = []
    for onset, e, spare in sorted(at_best, key=lambda w: sum(w[1].values())):
        # minimality: dropping any one factor must break it
        reducible = False
        for b in list(e):
            if e[b] <= 0:
                continue
            e2 = dict(e)
            e2[b] -= 1
            ok, _ = passes(pts, onset, nmax, e2)
            if ok:
                reducible = True
                break
        tag = "REDUCIBLE" if reducible else "MINIMAL"
        print("     %-34s deg=%2d  spare zeros=%2d  %s"
              % (fmt(e), len(build_den(e)) - 1, spare, tag))
        if not reducible:
            minimal.append(e)
    print()
    if len(minimal) == 1:
        e = minimal[0]
        print("   ANSWER: D_%d = %s" % (k, fmt(e)))
        print("   predicted was  Phi_1^%d Phi_2^%d Phi_3^%d"
              % (k + 1, max(0, k - 1), max(0, k - 4)))
        print("   Phi_4 present: %s" % ("YES" if e.get(4) else "no"))
    else:
        print("   %d minimal denominators -- census too short to separate them"
              % len(minimal))
    return 0


if __name__ == "__main__":
    sys.exit(main())
