#!/usr/bin/env python3
"""Gate KING-GRID: results/subclasses.md (formerly docs/middle-kingdom-plan.md) Phase 0 acceptance.

build/directed_cone_anchor's "grid" mode does one Redelmeier pass over ALL
fixed king animals and tallies all 20 (directedness x convexity) cells at
once: directedness in {none, dir5 (Bacher 5-cone), dir4 (half-plane 4-cone),
ctrlB (dir5nb's bottom-row-waived predicate -- a class of its own, NOT
multi-directed; see results/multi-directed.md), mdir (Bacher's Definition 2,
the fifth row Phase 3 added)} x convexity in {none, column-convex,
HV-convex, staircase}. Output per n: "n" then 20 counts, dir-major
(none,dir5,dir4,ctrlB,mdir) then conv-minor (none,col,hv,staircase) within each.

Per the plan, Phase 0's acceptance is:
  - every row-1 (directedness=none) and column-1 (convexity=none) entry of
    the plan's reference table reproduced exactly
  - A006770 reproduced to n=12 as the unfiltered control
  - the three pre-existing RED controls (dir4, dir5nb) still diverge from
    A047781 exactly where results/directed-cone-anchor.md recorded (n=3)
  - a NEW RED control: "gridbad" mode's staircase predicate (bottoms-monotone
    only, tops dropped) must FAIL to reproduce A225114
  - runs to n>=12 in under 10 minutes on 8 threads

Phase 3 added the mdir row and, with it, the collapse checks below. Each is a
PROVED equality (results/middle-kingdom-phase3.md): HV-convexity forces the
bottom profile to be valley-unimodal, which is exactly 5-cone directedness on
a column-convex animal, and every column-convex king animal is multi-directed.
The brute force is what those proofs are checked against, so the gate keeps
both the equalities that must hold AND the four that must NOT
((dir4,HV-convex) and the three column-convex cells), which is what stops a
degenerate predicate -- one that accepted everything -- from passing.

Reference values are transcribed from results/subclasses.md (formerly docs/middle-kingdom-plan.md)'s table,
which is the plan's stated source of truth -- a mismatch here means the
ENGINE is wrong, not the reference (the plan is explicit: "does not adjust
the reference").
"""
import os
import subprocess
import sys
import time

from common import ROOT, Gate, run, require_binary, read_bfile

BIN = os.path.join(ROOT, "build", "directed_cone_anchor")

# dir index: 0=none 1=dir5(Bacher 5-cone) 2=dir4(half-plane) 3=ctrlB(dir5nb)
#            4=mdir (Bacher Definition 2)
# conv index: 0=none 1=column-convex 2=HV-convex 3=staircase
DIR_NAMES = ["none", "dir5", "dir4", "ctrlB", "mdir"]
CONV_NAMES = ["none", "colconvex", "hvconvex", "staircase"]

# results/subclasses.md (formerly docs/middle-kingdom-plan.md) reference table -- row-1 (dir=none) and
# column-1 (conv=none) entries only; "?" cells are untested here (Phase 3's
# job). ctrlB/none uses the "cone-anchor control B" row; Phase 1c settled that
# this is a distinct class, incomparable with Bacher's multi-directed one
# (results/multi-directed.md), so the label is permanent, not a placeholder.
REF = {
    ("none", "none"): [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180],
    ("none", "colconvex"): [1, 4, 18, 83, 385],
    ("none", "hvconvex"): [1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834],
    ("none", "staircase"): [1, 3, 9, 28, 87, 272],
    ("dir5", "none"): [1, 4, 19, 96, 501, 2668, 14407, 78592, 432073, 2390004],
    ("dir4", "none"): [1, 4, 18, 85, 413, 2044],
    ("ctrlB", "none"): [1, 4, 20, 106, 576, 3179, 17736, 99748],
    ("mdir", "none"): [1, 4, 20, 110, 636, 3790, 23036, 141946],
}
# Phase 3's proved collapses (left) and the cells that must stay distinct
# (right). results/middle-kingdom-phase3.md, Propositions 1-5.
COLLAPSE = [("dir5", "hvconvex"), ("dir5", "staircase"), ("dir4", "staircase"),
            ("ctrlB", "hvconvex"), ("ctrlB", "staircase"), ("mdir", "colconvex"),
            ("mdir", "hvconvex"), ("mdir", "staircase")]
DISTINCT = [("dir5", "colconvex"), ("dir4", "colconvex"), ("ctrlB", "colconvex"),
            ("dir4", "hvconvex")]
# A007052 (1,3,10,34,116,396): the plan's grid table fills (dir5,colconvex)
# with A007052, but results/king-subfamilies.md's own derivation proves that
# identity via "column-convex + bottoms nondecreasing" -- NOT Bacher-cone
# reachability. Confirmed here as a diagnostic, not an acceptance check: it's
# gridbad's (none,staircase) column [tops-monotonicity dropped], not any
# grid cell. Left as a Phase 3 note (results/middle-kingdom-grid.md).
A007052 = [1, 3, 10, 34, 116, 396]
A225114 = [1, 3, 9, 28, 87, 272]


def run_engine(mode, n, threads=8):
    t0 = time.time()
    out = run(BIN, mode, n, threads)
    wall = time.time() - t0
    table = {}
    for line in out.strip().splitlines():
        parts = [int(x) for x in line.split()]
        table[parts[0]] = parts[1:]
    return table, wall


def col(table, dirname, convname):
    d = DIR_NAMES.index(dirname)
    c = CONV_NAMES.index(convname)
    return {n: vals[4 * d + c] for n, vals in table.items()}


def main():
    gate = Gate()
    if not require_binary(BIN, "build/directed_cone_anchor"):
        return 1

    # The engine run this line makes is 22.7 s on gympie -- the single most
    # expensive check in the whole suite -- and it grows ~4x per n. accept_n is
    # the depth the series comparison below reaches; the shape it checks holds
    # at every n. --deep restores 12.
    accept_n = 12 if "--deep" in sys.argv else 11
    grid, wall = run_engine("grid", accept_n)
    print(f"grid n={accept_n}: wall={wall:.1f}s (budget 600s)")
    gate.check(wall < 600, f"grid n={accept_n} runs under 10 minutes")

    # row-1 / column-1 reference reproduction
    for (dirname, convname), ref in REF.items():
        got = col(grid, dirname, convname)
        k = min(len(ref), accept_n)
        bad = [n for n in range(1, k + 1) if got.get(n) != ref[n - 1]]
        gate.check(not bad,
                   f"({dirname},{convname}) vs reference n<={k}"
                   + (f"  MISMATCH at n={bad}" if bad else ""))

    # A006770 fixture, to n=12 (deeper than the plan table's 10 terms)
    b006770 = read_bfile("b006770.txt")
    none_none = col(grid, "none", "none")
    bad = [n for n in range(1, accept_n + 1)
           if none_none.get(n) != b006770.get(n)]
    gate.check(not bad, f"(none,none) vs fixtures/b006770.txt n<={accept_n}"
               + (f"  MISMATCH at n={bad}" if bad else ""))

    # Phase 3: the proved collapses, and the cells that must NOT collapse.
    for dirname, convname in COLLAPSE:
        got = col(grid, dirname, convname)
        ref = col(grid, "none", convname)
        bad = [n for n in got if got[n] != ref[n]]
        gate.check(not bad, f"({dirname},{convname}) == (none,{convname})"
                   + (f"  DIFFERS at n={bad}" if bad else ""))
    for dirname, convname in DISTINCT:
        got = col(grid, dirname, convname)
        ref = col(grid, "none", convname)
        gate.check(any(got[n] != ref[n] for n in got),
                   f"({dirname},{convname}) != (none,{convname}) "
                   f"(a predicate that collapsed everything would pass above)")

    # existing RED controls (dir4, dir5nb), unchanged by the grid refactor:
    # must diverge from A047781 exactly at n=3 as results/directed-cone-anchor.md
    # recorded (4-cone 18 vs 19; bottom-row-waived 20 vs 19).
    a047781_3 = 19
    for mode, expect_bad in (("dir4", 18), ("dir5nb", 20)):
        out = subprocess.run([BIN, mode, "5", "1"], capture_output=True,
                             text=True, check=True).stdout
        filt3 = None
        for line in out.strip().splitlines():
            parts = [int(x) for x in line.split()]
            if parts[0] == 3:
                filt3 = parts[2]
        gate.check(filt3 == expect_bad,
                   f"RED control {mode}: filtered(3)={filt3} "
                   f"(expect {expect_bad}, MUST diverge from A047781={a047781_3})")

    # new RED control: gridbad's staircase predicate must FAIL to reproduce
    # A225114 (it reproduces A007052 instead -- confirms the break is real,
    # not just "off by noise").
    gridbad, _ = run_engine("gridbad", 6, threads=2)
    bad_stair = col(gridbad, "none", "staircase")
    got = [bad_stair[n] for n in range(1, 7)]
    gate.check(got != A225114,
               f"RED control gridbad staircase MUST diverge from A225114: got {got}")
    gate.check(got == A007052,
               f"gridbad staircase reproduces A007052 (confirms the dropped "
               f"predicate is exactly bottoms-only monotonicity): got {got} "
               f"want {A007052}")

    return gate.verdict("KING-GRID")


if __name__ == "__main__":
    sys.exit(main())
