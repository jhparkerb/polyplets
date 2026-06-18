#!/usr/bin/env python3
"""Gate G2: the C++ Redelmeier engine vs oracle and fixtures.

Four checks, per implementation-plan.md:
  A. aggregate counts equal pinned b-files (deeper than G1 can reach)
  B. per-bounding-box histograms equal the G1 oracle exactly
  C. split-mode invariance: the K split workers' outputs sum to the full run
  D. the ASan/UBSan build runs clean and agrees with the optimized build

Written before the engine exists (TDD); expects binaries at build/g2 and
build/g2_asan with the CLI:
    g2 LATTICE MAXN [--per-box] [--split S K IDX]
emitting "n count" lines (or "n w h count" with --per-box).
"""

import os
import sys

from common import ROOT, Gate, parse_counts, read_bfile, run

sys.path.insert(0, os.path.join(ROOT, "oracle"))

from g1_naive import count_by_box  # noqa: E402

G2 = os.path.join(ROOT, "build", "g2")
G2_ASAN = os.path.join(ROOT, "build", "g2_asan")

# check A: lattice -> (b-file, depth) -- a few seconds each, optimized build
FIXTURE_CASES = {
    "square4": ("b001168.txt", 14),
    "square8": ("b006770.txt", 11),
    "tri6":    ("b001207.txt", 12),
}
# check B: per-box equality vs G1 (G1 runtime bounds the depth)
PERBOX_CASES = {"square4": 9, "square8": 7, "tri6": 7}
# check C: split invariance
SPLIT_CASE = ("square8", 9, 4, 3)  # lattice, maxn, split size S, K workers
# check D: sanitizer build depths
ASAN_CASES = {"square4": 11, "square8": 8, "tri6": 9}


def main():
    gate = Gate()
    for b in (G2, G2_ASAN):
        if not os.path.exists(b):
            print(f"FAIL missing binary {b} (run: make build/g2 build/g2_asan)")
            return 1

    # A. fixtures
    for lattice, (bfile, depth) in FIXTURE_CASES.items():
        expected = read_bfile(bfile)
        got = parse_counts(run(G2, lattice, depth))
        bad = [n for n in range(1, depth + 1)
               if n in expected and got.get((n,)) != expected[n]]
        gate.check(not bad, f"A fixtures  {lattice:8s} n<={depth}  vs {bfile}"
              + (f"  MISMATCH at n={bad}" if bad else ""))

    # B. per-box vs oracle
    for lattice, depth in PERBOX_CASES.items():
        oracle = count_by_box(lattice, depth)
        engine = {k: v for k, v in
                  parse_counts(run(G2, lattice, depth, "--per-box")).items()}
        gate.check(engine == oracle,
              f"B per-box   {lattice:8s} n<={depth}  vs G1 oracle "
              f"({len(oracle)} box classes)")

    # C. split invariance
    lattice, maxn, S, K = SPLIT_CASE
    full = parse_counts(run(G2, lattice, maxn))
    summed = {}
    for idx in range(K):
        part = parse_counts(run(G2, lattice, maxn, "--split", S, K, idx))
        for k, v in part.items():
            summed[k] = summed.get(k, 0) + v
    gate.check(summed == full,
          f"C split     {lattice} n<={maxn} S={S} K={K}: workers sum to full run")

    # D. sanitizer build agrees and runs clean
    for lattice, depth in ASAN_CASES.items():
        opt = parse_counts(run(G2, lattice, depth))
        san = parse_counts(run(G2_ASAN, lattice, depth))
        gate.check(opt == san, f"D asan      {lattice:8s} n<={depth}  clean + equal")

    # E. rook/bishop + perimeter cross-checks (independent structural checks on
    #    the king-animal generator). Of the generated polyplets, those connected
    #    under edge (rook) or corner (bishop) adjacency must each equal A001168
    #    (fixed polyominoes); rook==bishop is the 45-degree colour-class
    #    invariant. The (size,perimeter) distribution must sum to A006770, and
    #    its perimeter=4n slice (no rook edges) must again equal A001168.
    a001168 = read_bfile("b001168.txt")
    a006770 = read_bfile("b006770.txt")
    E_DEPTH = 11

    rb_ok = True
    for line in run(G2, "square8", E_DEPTH, "--rook-bishop").strip().splitlines():
        n, tot, rook, bish = (int(x) for x in line.split())
        if not (tot == a006770[n] and rook == bish == a001168[n]):
            rb_ok = False
    gate.check(rb_ok,
          f"E rook/bish square8 n<={E_DEPTH}: total=A006770, rook==bishop==A001168")

    psum, p4n = {}, {}
    for line in run(G2, "square8", E_DEPTH, "--perimeter").strip().splitlines():
        n, p, c = (int(x) for x in line.split())
        psum[n] = psum.get(n, 0) + c
        if p == 4 * n:
            p4n[n] = c
    per_ok = all(psum.get(n) == a006770[n] for n in range(1, E_DEPTH + 1)) and \
             all(p4n.get(n, 0) == a001168[n] for n in range(1, E_DEPTH + 1))
    gate.check(per_ok,
          f"E perimeter square8 n<={E_DEPTH}: sum=A006770, perim=4n slice=A001168")

    return gate.verdict("G2")


if __name__ == "__main__":
    sys.exit(main())
