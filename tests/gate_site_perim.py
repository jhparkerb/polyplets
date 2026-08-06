#!/usr/bin/env python3
"""Gate SITE-PERIM: docs/middle-kingdom-followups-plan.md Phase 4a acceptance.

build/directed_cone_anchor's "grid" mode already does one Redelmeier pass over
ALL fixed king animals of every size <= N (Phase 0 of the middle-kingdom
plan). Phase 4a rides that pass with a per-n MIN-REDUCE of the site
perimeter -- the number of distinct EMPTY cells adjacent to the animal -- and
appends it as two trailing columns after the existing 20 directedness x
convexity counts: minSPKing then minSPRook.

Convention (pinned BEFORE the reduce was written, per the plan): KING
(8-)adjacency, transcribed from cpp/g2_redelmeier.cpp's `--siteperim` header
comment -- "the percolation perimeter for the king/nnSquare lattice",
cross-checked there against Mertens 1990 Table IVB. minSPRook uses orthogonal
(4-)adjacency instead: a deliberately WRONG convention, kept as the RED
control this phase's acceptance requires.

This gate is RED-first in the literal sense: it was run against the
unmodified binary (no minSPKing/minSPRook columns at all) before the C++
change landed, and failed by construction (parts[21:] was empty). It also
carries an independent-oracle cross-check: build/g2's square8 lattice grows
KING-connected animals with KING-adjacency growth AND (via --siteperim, which
uses the lattice's own connectivity degree for both) KING-adjacency site
perimeter -- the same population and the same convention, computed by
completely different code (fixed-origin placed/inAnimal array growth, not the
untried-set DFS). The two must agree exactly.

Acceptance, all required:
  - minSPKing reproduces 4k+4 at every perfect square n=k^2 in range (a k*k
    solid block's king site-perimeter: Minkowski sum with the 3x3 king ball
    is a (k+2)x(k+2) square, minus the k^2 occupied cells).
  - minSPKing agrees with the g2 square8 --siteperim independent oracle at
    every n in range.
  - minSPRook diverges from minSPKing at every n in range (the RED control
    must fail to reproduce the real convention).
"""
import os
import subprocess
import sys

from common import ROOT, Gate

BIN = os.path.join(ROOT, "build", "directed_cone_anchor")
G2 = os.path.join(ROOT, "build", "g2")

ACCEPT_N = 9
SQUARES = [1, 4, 9]  # k=1,2,3 within ACCEPT_N


def run_grid(n, threads=4):
    proc = subprocess.run([BIN, "grid", str(n), str(threads)],
                          capture_output=True, text=True, check=True)
    king, rook = {}, {}
    for line in proc.stdout.strip().splitlines():
        parts = [int(x) for x in line.split()]
        n_ = parts[0]
        king[n_] = parts[-2]
        rook[n_] = parts[-1]
    return king, rook


def run_g2_siteperim_min(n):
    proc = subprocess.run([G2, "square8", str(n), "--siteperim"],
                          capture_output=True, text=True, check=True)
    mn = {}
    for line in proc.stdout.strip().splitlines():
        n_, p, c = (int(x) for x in line.split())
        if c > 0:
            mn[n_] = min(mn.get(n_, 1 << 62), p)
    return mn


def main():
    gate = Gate()
    if not os.path.exists(BIN):
        print(f"FAIL missing {BIN} (run: make build/directed_cone_anchor)")
        return 1
    if not os.path.exists(G2):
        print(f"FAIL missing {G2} (run: make build/g2)")
        return 1

    king, rook = run_grid(ACCEPT_N)

    for n in SQUARES:
        k = round(n ** 0.5)
        expect = 4 * k + 4
        gate.check(king.get(n) == expect,
                   f"minSPKing({n}) == 4*{k}+4 = {expect}: got {king.get(n)}")

    oracle = run_g2_siteperim_min(ACCEPT_N)
    bad = [n for n in range(1, ACCEPT_N + 1) if king.get(n) != oracle.get(n)]
    gate.check(not bad,
               f"minSPKing vs g2 square8 --siteperim oracle n<={ACCEPT_N}"
               + (f"  MISMATCH at n={bad}" if bad else ""))

    same = [n for n in range(1, ACCEPT_N + 1) if king.get(n) == rook.get(n)]
    gate.check(not same,
               f"RED control minSPRook MUST diverge from minSPKing at every "
               f"n<={ACCEPT_N}" + (f"  AGREED at n={same}" if same else ""))

    print(f"minSPKing n=1..{ACCEPT_N}: {[king[n] for n in range(1, ACCEPT_N+1)]}")
    print(f"minSPRook n=1..{ACCEPT_N}: {[rook[n] for n in range(1, ACCEPT_N+1)]}")

    return gate.verdict("SITE-PERIM")


if __name__ == "__main__":
    sys.exit(main())
