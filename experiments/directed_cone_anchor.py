#!/usr/bin/env python3
"""Cone anchor -- directed king animals: enumerate+filter vs Bacher's closed form.

Purpose: close the "validation hook (feasible, not yet built)" of
results/directed-king-animals.md. Filter the fixed king-animal (polyplet)
enumeration down to DIRECTED king animals and check the result against the
exact generating function D(t) = 1/4 * ((1+t)/sqrt(1-6t+t^2) - 1) = A047781.
Write-up: results/directed-cone-anchor.md.

Compute lives in build/directed_cone_anchor (C++); this is glue + the exact
closed-form arithmetic + the fail-closed comparisons.

Three INDEPENDENT closed-form routes are computed and required to agree
term-by-term before either is used as a reference:
  legendre  (n+1)P_{n+1}(3) = 3(2n+1)P_n(3) - n P_{n-1}(3);  d(n) = (P_n+P_{n-1})/4
  sqrt      exact Fraction series sqrt of 1/(1-6t+t^2) (naive c_n = 6c_{n-1}-c_{n-2}
            inversion, then the standard series square-root recurrence)
  delannoy  P_n(3) = central Delannoy D(n) = Sum_k C(n,k)*C(n+k,k)  (closed sum)

Exact command:
    make build/directed_cone_anchor
    python3 experiments/directed_cone_anchor.py --dir5 15 --cone5 17 \
        --ctrl 14 --threads 8
Target machine: local laptop, 8 threads. Predicted cost (measured on this box,
2026-07-31): dir5 n=13 11s and ~6.7x/term  => n=15 ~8 min; cone5 n=14 2.5s and
~5.6x/term => n=17 ~7 min; the two controls at n=14 ~75s each. Whole default
run ~19 min wall, RAM nil (O(n^2) bytes/thread). No checkpointing needed --
kill with SIGINT and rerun; each mode is an independent invocation.
"""
from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "build", "directed_cone_anchor")

# Published reference terms, hard-coded with provenance (no b-file exists in
# fixtures/ for either sequence -- see results/directed-cone-anchor.md).
# A047781, first 8 terms as listed in results/directed-king-animals.md line 9
# (that note states they were verified against Bacher arXiv:1301.1365 + OEIS).
A047781_DOC = [1, 4, 19, 96, 501, 2668, 14407, 78592]
# A055834, first 6 terms as listed in results/king-subfamilies.md (addendum
# 2026-07-23), where they were checked against the OEIS entry to n=15.
A055834_DOC = [1, 4, 18, 85, 413, 2044]


# ---------------------------------------------------------------- closed forms
def legendre_terms(nmax: int) -> list[int]:
    """d(n) via the Legendre P_n(3) three-term recurrence."""
    P = [1, 3]
    for n in range(1, nmax):
        nxt, rem = divmod(3 * (2 * n + 1) * P[n] - n * P[n - 1], n + 1)
        assert rem == 0, f"Legendre recurrence left a remainder at n={n}"
        P.append(nxt)
    out = []
    for n in range(1, nmax + 1):
        d, rem = divmod(P[n] + P[n - 1], 4)
        assert rem == 0, f"(P_n+P_(n-1)) not divisible by 4 at n={n}"
        out.append(d)
    return out


def sqrt_series_terms(nmax: int) -> list[int]:
    """d(n) by exact series arithmetic on D(t) itself: invert 1-6t+t^2, take the
    series square root with Fractions, multiply by (1+t), subtract 1, divide 4."""
    m = nmax + 1
    c = [Fraction(0)] * (m + 1)  # c = 1/(1-6t+t^2)
    c[0] = Fraction(1)
    if m >= 1:
        c[1] = Fraction(6)
    for n in range(2, m + 1):
        c[n] = 6 * c[n - 1] - c[n - 2]
    b = [Fraction(0)] * (m + 1)  # b = sqrt(c) = (1-6t+t^2)^(-1/2)
    b[0] = Fraction(1)
    for n in range(1, m + 1):
        s = sum(b[k] * b[n - k] for k in range(1, n))
        b[n] = (c[n] - s) / 2
    out = []
    for n in range(1, nmax + 1):
        d = (b[n] + b[n - 1]) / 4  # coefficient of t^n in ((1+t)*b - 1)/4
        assert d.denominator == 1, f"non-integer coefficient at n={n}: {d}"
        out.append(int(d))
    return out


def delannoy_terms(nmax: int) -> list[int]:
    """d(n) from the closed binomial sum for the central Delannoy numbers."""
    D = [sum(math.comb(n, k) * math.comb(n + k, k) for k in range(n + 1))
         for n in range(nmax + 1)]
    out = []
    for n in range(1, nmax + 1):
        d, rem = divmod(D[n] + D[n - 1], 4)
        assert rem == 0, f"(D_n+D_(n-1)) not divisible by 4 at n={n}"
        out.append(d)
    return out


# ------------------------------------------------- third implementation (brute)
# Deliberately shares NOTHING with the C++ engine: growth by frozenset + explicit
# translation canonicalisation instead of Redelmeier's untried set, dict-of-sets
# reachability instead of a stamped grid. Small n only; it exists to catch a bug
# that both C++ modes could share.
KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
CONE5 = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0)]


def _canon(cells: frozenset) -> frozenset:
    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def brute_terms(nmax: int) -> tuple[list[int], list[int]]:
    """-> (all fixed king animals, directed ones) for n = 1..nmax, from scratch."""
    total, direct = [], []
    layer = {frozenset({(0, 0)})}
    for n in range(1, nmax + 1):
        total.append(len(layer))
        d = 0
        for A in layer:
            ys = min(y for _, y in A)
            src = (min(x for x, y in A if y == ys), ys)
            seen, stack = {src}, [src]
            while stack:
                x, y = stack.pop()
                for dx, dy in CONE5:
                    c = (x + dx, y + dy)
                    if c in A and c not in seen:
                        seen.add(c)
                        stack.append(c)
            if len(seen) == len(A):
                d += 1
        direct.append(d)
        if n < nmax:
            nxt = set()
            for A in layer:
                for x, y in A:
                    for dx, dy in KING:
                        c = (x + dx, y + dy)
                        if c not in A:
                            nxt.add(_canon(A | {c}))
            layer = nxt
    return total, direct


# ------------------------------------------------------------------- reference
def load_a006770(nmax: int) -> list[int]:
    path = os.path.join(ROOT, "fixtures", "b006770.txt")
    terms = {}
    with open(path) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            n, v = line.split()
            terms[int(n)] = int(v)
    return [terms[n] for n in range(1, nmax + 1)]


# ------------------------------------------------------------------- the engine
def run(mode: str, n: int, threads: int) -> tuple[list[int], list[int]]:
    """-> (unfiltered totals, filtered counts) for n = 1..n. cone5 has no totals."""
    cmd = [BIN, mode, str(n), str(threads)]
    print(f"  $ {' '.join(cmd)}", flush=True)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    for line in proc.stderr.splitlines():
        if line.startswith("event=done") or line.startswith("event=start"):
            print(f"    {line}", flush=True)
    total, filt = [], []
    for line in proc.stdout.split("\n"):
        if not line.strip():
            continue
        parts = line.split()
        if mode == "cone5":
            filt.append(int(parts[1]))
        else:
            total.append(int(parts[1]))
            filt.append(int(parts[2]))
    return total, filt


# ------------------------------------------------------------------ comparisons
FAILURES: list[str] = []


def compare(label: str, got: list[int], ref: list[int], *, expect_equal=True) -> None:
    """Fail-closed: an empty overlap is a FAILURE, not a silent pass."""
    k = min(len(got), len(ref))
    if k == 0:
        FAILURES.append(f"{label}: nothing to compare (empty overlap)")
        print(f"  FAIL {label}: empty overlap")
        return
    diffs = [(i + 1, got[i], ref[i]) for i in range(k) if got[i] != ref[i]]
    if expect_equal:
        if diffs:
            FAILURES.append(f"{label}: {len(diffs)} mismatch(es), first {diffs[0]}")
            print(f"  FAIL {label}: n<={k}, first mismatch n={diffs[0][0]} "
                  f"got {diffs[0][1]} want {diffs[0][2]}")
        else:
            print(f"  ok   {label}: agree for all n <= {k}")
    else:
        if not diffs:
            FAILURES.append(f"{label}: expected a DIVERGENCE, got none up to n={k}")
            print(f"  FAIL {label}: expected divergence, none up to n={k}")
        else:
            print(f"  ok   {label}: diverges first at n={diffs[0][0]} "
                  f"({diffs[0][1]} vs {diffs[0][2]}) as required")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir5", type=int, default=13, help="reach of enumerate+filter")
    ap.add_argument("--cone5", type=int, default=15, help="reach of direct cone growth")
    ap.add_argument("--ctrl", type=int, default=12, help="reach of the RED controls")
    ap.add_argument("--brute", type=int, default=0,
                    help="reach of the from-scratch Python brute force (0 = skip)")
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()

    if not os.path.exists(BIN):
        print(f"missing {BIN} -- run: make build/directed_cone_anchor", file=sys.stderr)
        return 2

    nmax = max(args.dir5, args.cone5, args.ctrl)

    print("== closed form, three independent routes ==")
    leg = legendre_terms(max(nmax, 25))
    sq = sqrt_series_terms(max(nmax, 25))
    dela = delannoy_terms(max(nmax, 25))
    compare("closed form: legendre vs sqrt-series", leg, sq)
    compare("closed form: legendre vs delannoy sum", leg, dela)
    compare("closed form vs published A047781 (doc)", leg, A047781_DOC)
    print(f"  D(t) coefficients n=1..12: {leg[:12]}")

    if args.brute:
        print(f"\n== GREEN: from-scratch Python brute force, n <= {args.brute} ==")
        bt, bd = brute_terms(args.brute)
        compare("brute total vs A006770", bt, load_a006770(args.brute))
        compare("brute dir5 vs closed form", bd, leg)
        _, cd = run("dir5", args.brute, args.threads)
        compare("brute dir5 vs C++ dir5 (implementation cross-check)", bd, cd)

    print("\n== GREEN: enumerate all fixed king animals, filter to 5-step cone ==")
    tot5, d5 = run("dir5", args.dir5, args.threads)
    compare("unfiltered total vs A006770 (fixtures/b006770.txt)",
            tot5, load_a006770(args.dir5))
    compare("dir5 filter vs closed form", d5, leg)

    print("\n== GREEN: direct cone growth (second enumeration engine) ==")
    _, c5 = run("cone5", args.cone5, args.threads)
    compare("cone5 vs closed form", c5, leg)
    compare("cone5 vs dir5 filter (engine cross-check)", c5[:len(d5)], d5)

    print("\n== RED control A: wrong cone (4-step {N,NE,E,SE}) ==")
    tot4, d4 = run("dir4", args.ctrl, args.threads)
    compare("dir4 unfiltered total vs A006770", tot4, load_a006770(args.ctrl))
    compare("dir4 vs published A055834 (doc)", d4, A055834_DOC)
    compare("dir4 vs A047781 -- MUST DIVERGE", d4, leg, expect_equal=False)

    print("\n== RED control B: 5-step cone, bottom-row contiguity waived ==")
    totnb, dnb = run("dir5nb", args.ctrl, args.threads)
    compare("dir5nb unfiltered total vs A006770", totnb, load_a006770(args.ctrl))
    compare("dir5nb vs A047781 -- MUST DIVERGE", dnb, leg, expect_equal=False)
    compare("dir5nb vs A006770 -- MUST DIVERGE too (not just 'everything')",
            dnb, load_a006770(args.ctrl), expect_equal=False)

    print("\n== table: n | A006770 total | dir5 filter | closed form | dir4 | dir5nb ==")
    for n in range(1, nmax + 1):
        def at(seq, i=n):
            return str(seq[i - 1]) if i - 1 < len(seq) else "-"
        print(f"{n:3d} {at(tot5):>16} {at(d5):>15} {at(leg):>15} "
              f"{at(d4):>13} {at(dnb):>15}")

    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}):")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
