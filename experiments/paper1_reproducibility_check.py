#!/usr/bin/env python3
"""Regenerate every number the report's Reproducibility section will quote.

`paper/technical-report.tex`'s Reproducibility section is empty, and
`paper/technical-report-gaps.md` item 1 calls it the biggest hole. The material
is spread over the project handoff file (removed), results/second-sources.md and results/ns_a40/. This
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
     doc-style / honest figures of results/second-sources.md
  E. per row n = 29..40, how many CELLS were really swept (H <= 21), how
     many are wired closed forms whose level is pinned by real data alone
     (k <= 10: a level k has the k+1 real in-onset points it needs iff
     k <= (21-1)/2), and how many are wired closed forms above that.  Cells,
     not shares: a wrong cell ruins a(n) whatever its size, so a percentage
     of a(n) carries no decision (standing ruling, 2026-08-18).
  F. the Motley (coloring) second source: results/cutcount_b1/rows41/
     assembles to the banked triangle at every cell with H <= 19 and n <= 40
     (589 cells) and to the kink sweep's own n = 41 row at H <= 19 (19
     cells) -- the two arms of `make gate-cutcount-assembly`, called here.

RED controls, all required to fail: each diagonal formula perturbed in its
leading coefficient must break check B, a single altered digit in the
Redelmeier column must break check C, and one altered Motley cell must break
check F.

Usage: python3 experiments/paper1_reproducibility_check.py
"""
import argparse
import glob
import os
import shutil
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import cutcount_assembly_gate as CAG        # noqa: E402
import provenance_table as PT               # noqa: E402

PERHEIGHT = os.path.join(ROOT, "results", "ns_a40", "perheight")
TRIANGLE = Path(ROOT, "results", "triangle.txt")
ROWS41 = Path(ROOT, "results", "cutcount_b1", "rows41")
A41 = Path(ROOT, "results", "a41")
SWEEP_H = PT.SWEEP_H                        # the a(40) run's tallest real sweep
PINNED_K = (SWEEP_H - 1) // 2               # levels with k+1 real in-onset points
TERMS = os.path.join(ROOT, "results", "b006770_upload.txt")
REDELMEIER = os.path.join(ROOT, "results", "redelmeier_row22", "combined.txt")
NMAX = 40

# results/diagonal-formula.md and docs/proofs/T-n-nm1.md,
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
        "coverage arithmetic no longer reproduces results/second-sources.md"

    # E. cells per row by how they were produced.  H <= SWEEP_H was really
    # swept in the a(40) run; above it every cell is a wired closed form P_k,
    # k = n - H, and a level is pinned by real data alone iff k <= PINNED_K.
    print(f"E. cells per row: really swept (H<={SWEEP_H}) / wired P_k, "
          f"k<={PINNED_K} / wired P_k, k>{PINNED_K}")
    for n in range(29, NMAX + 1):
        low = sum(1 for H in range(SWEEP_H + 1, n + 1) if n - H <= PINNED_K)
        print(f"   n={n}: {SWEEP_H} swept, {low} formula k<={PINNED_K}, "
              f"{n - SWEEP_H - low} formula k>{PINNED_K}")

    # F. the coloring second source at Nmax 41: the gate's two arms, against
    # results/triangle.txt, which is this script's own T.
    tri = CAG.read_triangle(TRIANGLE)
    assert all(tri[c] == T.get(c) for c in tri), "results/triangle.txt != the per-height sweep"
    bad, cells = CAG.check_assembly(ROWS41, TRIANGLE, CAG.EXPECT41_TOP_H, CAG.EXPECT41_CELLS)
    assert not bad, f"Motley rows41 vs the triangle: {bad[:3]}"
    bad, top = CAG.check_row41(ROWS41, A41)
    assert not bad, f"Motley rows41 vs the kink sweep at n = 41: {bad[:3]}"
    print(f"F. Motley rows41: {cells} cells H<=19, n<=40 equal the triangle; "
          f"{top} cells at n = 41 equal the kink sweep  OK")
    with tempfile.TemporaryDirectory() as d:
        shutil.copytree(ROWS41, os.path.join(d, "rows41"))
        p = os.path.join(d, "rows41", "C19.out")
        lines = open(p).read().splitlines()
        n, v = lines[-2].split()                     # n = 40, a cell the triangle has
        lines[-2] = f"{n} {int(v) + 1}"
        open(p, "w").write("\n".join(lines) + "\n")
        bad, _ = CAG.check_assembly(Path(d, "rows41"), TRIANGLE,
                                    CAG.EXPECT41_TOP_H, CAG.EXPECT41_CELLS)
    assert bad, "RED control alive"
    print("   RED one altered Motley cell breaks the agreement  OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
