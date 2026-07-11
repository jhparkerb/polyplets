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

    # I. terminal pure-count path (L1). The aggregate counter takes the terminal
    #    shortcut at size==maxn-1 (bs[maxn] += numUntried + DEG - sum(status));
    #    the per-box counter does NOT (it needs each child's coordinates, so it
    #    keeps the mark/push batch). They must still agree row-by-row -- a bug in
    #    the pure-count arithmetic would diverge here. Then a --split whose
    #    boundary sits AT maxn disables the shortcut (canCount = splitS<maxn is
    #    false) and drives the per-cell split path through the terminal level; it
    #    must still sum to the full run.
    for lattice, depth in (("square8", 13), ("square4", 14), ("tri6", 13)):
        agg = parse_counts(run(G2, lattice, depth))
        pbox = parse_counts(run(G2, lattice, depth, "--per-box"))
        rowsum = {}
        for (n, w, h), c in pbox.items():
            rowsum[(n,)] = rowsum.get((n,), 0) + c
        gate.check(agg == rowsum,
              f"I terminal  {lattice:8s} n<={depth}: aggregate(pure-count)==per-box rowsums")

    mx = 9
    full_m = parse_counts(run(G2, "square8", mx))
    summed_m = {}
    for idx in range(3):
        part = parse_counts(run(G2, "square8", mx, "--split", mx, 3, idx))
        for k, v in part.items():
            summed_m[k] = summed_m.get(k, 0) + v
    gate.check(summed_m == full_m,
          f"I split@max square8 n<={mx} S={mx} K=3: boundary-at-maxn sums to full")

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

    # F. transpose symmetry: reflecting across the diagonal is a king-lattice
    #    symmetry that swaps width and height, so the bounding-box distribution
    #    must satisfy byBox[n][w][h] == byBox[n][h][w]. A free internal invariant
    #    (no external sequence) that catches any width/height-asymmetric miscount.
    F_DEPTH = 11
    box = parse_counts(run(G2, "square8", F_DEPTH, "--per-box"))
    sym_ok = all(c == box.get((n, h, w), 0) for (n, w, h), c in box.items())
    gate.check(sym_ok,
          f"F transpose square8 n<={F_DEPTH}: byBox[n][w][h]==byBox[n][h][w] "
          f"({len(box)} (n,w,h) cells)")

    # H. hole counting (--holes / --holes8). Two independent guarantees:
    #    (1) the by-hole-count partition must sum to the total for BOTH background
    #        conventions (square8 -> A006770); and
    #    (2) the convention itself is validated against KNOWN answers by running
    #        the identical flood on polyominoes (square4): hole-free must equal
    #        A006724 (simply-connected fixed polyominoes) and the with-holes count
    #        must equal A389193 (fixed polyominoes with holes). This pins the flood
    #        logic and the 4-connected-hole definition to OEIS's own convention.
    H_DEPTH = 11

    def hole_table(args):
        tbl = {}
        for line in run(G2, *args).strip().splitlines():
            n, h, c = (int(x) for x in line.split())
            tbl.setdefault(n, {})[h] = c
        return tbl

    sum_ok = True
    for flag in ("--holes", "--holes8"):
        tbl = hole_table(("square8", H_DEPTH, flag))
        for n in range(1, H_DEPTH + 1):
            if sum(tbl.get(n, {}).values()) != a006770[n]:
                sum_ok = False
    gate.check(sum_ok,
          f"H holes-sum square8 n<={H_DEPTH}: 4-bg and 8-bg both sum to A006770")

    # A006724 (fixed simply-connected polyominoes) and A389193 (fixed polyominoes
    # with holes), n=1..12; the 4-connected-hole convention must reproduce both.
    A006724 = {1:1,2:2,3:6,4:19,5:63,6:216,7:756,8:2684,9:9638,10:34930,11:127560}
    A389193 = {n:0 for n in range(1,7)}
    A389193.update({7:4,8:41,9:272,10:1516,11:7708})
    poly = hole_table(("square4", H_DEPTH, "--holes"))
    conv_ok = True
    for n in range(1, H_DEPTH + 1):
        free = poly.get(n, {}).get(0, 0)
        holey = sum(c for h, c in poly.get(n, {}).items() if h > 0)
        if free != A006724[n] or holey != A389193[n]:
            conv_ok = False
    gate.check(conv_ok,
          f"H holes-conv square4 n<={H_DEPTH}: hole-free=A006724, holey=A389193")

    return gate.verdict("G2")


if __name__ == "__main__":
    sys.exit(main())
