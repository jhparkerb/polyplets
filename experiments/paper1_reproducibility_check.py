#!/usr/bin/env python3
"""Regenerate every number the report's Reproducibility section will quote.

`paper/technical-report.tex`'s Reproducibility section is empty, and
`paper/technical-report-gaps.md` item 1 calls it the biggest hole. The material
is spread over HANDOFF.md, results/strip-engine.md and results/ns_a40/. This
script recomputes it from the banked artifacts rather than copying it forward,
so the section can be written against checked numbers.

What it checks, each against a file that was produced by a different part of
the campaign:

  A. the height triangle's rows sum to the banked terms, all n <= 40
     (results/ns_a40/perheight/h*.out  vs  results/b006770_upload.txt)
  B. the three pinned diagonals hold on every banked cell in range
     T(n,n) = 3^(n-1), T(n,n-1) = 5(5n-9)3^(n-4), T(n,n-2) = (625n^2 -
     2459n + 1134)/2 * 3^(n-7)
  C. Redelmeier's independent enumeration agrees on a(1)..a(22)
     (results/redelmeier_row22/combined.txt)
  D. the strip engine's coverage arithmetic: 820 cells, 469 swept, and the
     doc-style / honest figures of results/strip-engine.md
  E. per row n = 29..40, how many CELLS were really swept (H <= 21), how
     many are wired closed forms whose level is pinned by real data alone
     (k <= 10), and how many are wired closed forms above that (k > 10) --
     the decomposition scripts/verify_diagonal_pins.py prints as shares of
     a(n), restated in cells.  Cells, not shares: a wrong cell ruins a(n)
     whatever its size, so a percentage of a(n) carries no decision
     (standing ruling, 2026-08-18).  Until 2026-09-05 this check printed
     "share of each late row's mass" inside the strip engine's reach.
  F. the Motley (colouring) second source: results/cutcount_b1/rows41/
     assembles to the banked triangle at every cell with H <= 19 and n <= 40
     (589 cells) and to the kink sweep's own n = 41 row at H <= 19 (19
     cells); the same two numbers `make gate-cutcount-assembly` pins.

RED controls, all required to fail: each diagonal formula perturbed in its
leading coefficient must break check B, a single altered digit in the
Redelmeier column must break check C, and one altered Motley cell must break
check F.

Usage: python3 experiments/paper1_reproducibility_check.py
"""
import argparse
import glob
import os
import sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERHEIGHT = os.path.join(ROOT, "results", "ns_a40", "perheight")
ROWS41 = os.path.join(ROOT, "results", "cutcount_b1", "rows41")
A41 = os.path.join(ROOT, "results", "a41")
SWEEP_H = 21            # the a(40) run's tallest real sweep
PINNED_K = 10           # levels the diag-pins audit shows pinned by real data alone
TERMS = os.path.join(ROOT, "results", "b006770_upload.txt")
REDELMEIER = os.path.join(ROOT, "results", "redelmeier_row22", "combined.txt")
NMAX = 40

# results/diagonal-closed-forms.md and docs/proofs/T-n-nm1.md,
# T-n-nm2-and-general.md. Each is (k, onset n, callable).
DIAGONALS = [
    (0, 1, lambda n: 3 ** (n - 1)),
    (1, 4, lambda n: 5 * (5 * n - 9) * 3 ** (n - 4)),
    (2, 5, lambda n: Fraction(625 * n * n - 2459 * n + 1134, 2) * 3 ** (n - 7)),
]
BAD_DIAGONALS = [
    (0, 1, lambda n: 2 * 3 ** (n - 1)),
    (1, 4, lambda n: 5 * (5 * n - 8) * 3 ** (n - 4)),
    (2, 5, lambda n: Fraction(624 * n * n - 2459 * n + 1134, 2) * 3 ** (n - 7)),
]


def read_terms(path):
    out = {}
    with open(path) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            n, v = line.split()
            out[int(n)] = int(v)
    return out


def read_triangle(path):
    """T[(n,H)] from the per-height sweep outputs."""
    T = {}
    for f in sorted(glob.glob(os.path.join(path, "h*.out"))):
        H = int(os.path.basename(f)[1:-4])
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    n, v = line.split()
                    if int(v):
                        T[(int(n), H)] = int(v)
    return T


def diagonal_failures(T, table):
    bad = []
    for k, onset, formula in table:
        for n in range(onset, NMAX + 1):
            H = n - k
            if H < 1:
                continue
            got, want = T.get((n, H), 0), formula(n)
            if got != want:
                bad.append((k, n))
    return bad


def coverage():
    cells = {(n, H) for n in range(1, NMAX + 1) for H in range(1, n + 1)}
    R = {c for c in cells if c[1] <= 4}                      # low-height recurrences
    S = {c for c in cells if c[1] <= 14}                     # the strip engine's sweep
    P = {(n, H) for (n, H) in cells                          # pinned diagonals, k <= 18
         if n - H <= 18 and n >= 2 * (n - H) + 1}
    honest = R | S | (P & {c for c in cells if c[1] <= 21})
    return cells, R, S, P, honest


def main():
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter
                            ).parse_args()
    terms = read_terms(TERMS)
    T = read_triangle(PERHEIGHT)

    # A. rows sum to the banked terms
    bad = [n for n in range(1, NMAX + 1)
           if sum(v for (m, _), v in T.items() if m == n) != terms[n]]
    assert not bad, f"row sums disagree with the banked terms at n={bad[:5]}"
    print(f"A. all {NMAX} triangle rows sum to the banked term, "
          f"a({NMAX}) = {terms[NMAX]}  OK")

    # B. the pinned diagonals
    bad = diagonal_failures(T, DIAGONALS)
    assert not bad, f"pinned diagonal fails at (k,n) = {bad[:5]}"
    counts = {k: sum(1 for n in range(onset, NMAX + 1) if n - k >= 1)
              for k, onset, _ in DIAGONALS}
    print(f"B. T(n,n), T(n,n-1), T(n,n-2) hold on every banked cell in range "
          f"({counts[0]}, {counts[1]}, {counts[2]} cells)  OK")
    alive = [k for k, *_ in DIAGONALS
             if not any(b[0] == k for b in diagonal_failures(T, BAD_DIAGONALS))]
    assert not alive, f"RED control alive: perturbed diagonal k={alive} still fits"
    print("   RED perturbing any of the three leading coefficients breaks it  OK")

    # C. Redelmeier, the second algorithm
    red = read_terms(REDELMEIER)
    bad = [n for n in red if red[n] != terms[n]]
    assert not bad, f"Redelmeier disagrees at n={bad[:5]}"
    print(f"C. Redelmeier reproduces a(1)..a({max(red)}) digit for digit  OK")
    red[max(red)] += 1
    assert any(red[n] != terms[n] for n in red), "RED control alive"
    print("   RED one altered digit in the Redelmeier column breaks it  OK")

    # D, E. the strip engine's reach
    cells, R, S, P, honest = coverage()
    doc = R | P | S
    print(f"D. cells in the closed triangle: {len(cells)}; strip-swept (H<=14): "
          f"{len(S)} = {100 * len(S) / len(cells):.1f}%; "
          f"honest {len(honest)} = {100 * len(honest) / len(cells):.1f}%; "
          f"doc-style {len(doc)} = {100 * len(doc) / len(cells):.1f}%")
    assert (len(cells), len(S), len(honest), len(doc)) == (820, 469, 592, 782), \
        "coverage arithmetic no longer reproduces results/strip-engine.md"

    # E. cells per row by how they were produced.  H <= 21 was really swept
    # in the a(40) run; above it every cell is a wired closed form P_k,
    # k = n - H, and verify_diagonal_pins.py shows k <= 10 pinned by real
    # data alone.  Checked against the row length so nothing is dropped.
    print("E. cells per row: really swept (H<=21) / wired P_k, k<=10 / wired P_k, k>10")
    for n in range(29, NMAX + 1):
        swept = sum(1 for H in range(1, n + 1) if H <= SWEEP_H)
        low = sum(1 for H in range(SWEEP_H + 1, n + 1) if n - H <= PINNED_K)
        high = sum(1 for H in range(SWEEP_H + 1, n + 1) if n - H > PINNED_K)
        assert swept + low + high == n
        print(f"   n={n}: {swept} swept, {low} formula k<=10, {high} formula k>10")

    # F. the colouring second source at Nmax 41.
    C = {0: {}, -1: {}}
    for f in glob.glob(os.path.join(ROWS41, "C*.out")):
        H = int(os.path.basename(f)[1:-4])
        C[H] = read_terms(f)
    tri = {}
    for H in range(1, 20):
        for n in range(1, 41):
            if H in C and H - 1 in C and H - 2 in C and n in C[H]:
                tri[(n, H)] = C[H][n] - 2 * C[H - 1].get(n, 0) + C[H - 2].get(n, 0)
    cells = [(n, H) for (n, H) in tri if (n, H) in T]
    bad = [c for c in cells if tri[c] != T[c]]
    assert not bad and len(cells) == 589, \
        f"Motley rows41 vs the triangle: {len(cells)} cells, mismatches {bad[:3]}"
    a41 = read_triangle(A41)
    top = [(41, H) for H in range(1, 20)]
    bad = [c for c in top if a41.get(c) !=
           C[c[1]][41] - 2 * C[c[1] - 1].get(41, 0) + C[c[1] - 2].get(41, 0)]
    assert not bad, f"Motley rows41 vs the kink sweep at n = 41: {bad[:3]}"
    print(f"F. Motley rows41: {len(cells)} cells H<=19, n<=40 equal the triangle; "
          f"{len(top)} cells at n = 41 equal the kink sweep  OK")
    C[19][40] += 1
    assert C[19][40] - 2 * C[18][40] + C[17][40] != T[(40, 19)], "RED control alive"
    print("   RED one altered Motley cell breaks the agreement  OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
