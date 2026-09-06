#!/usr/bin/env python3
"""Gate UNDERTOW-PAIRS: every pinned level of the a(41) tower is overdetermined,
and the depth pairs agree.

AUDIT-2026-09-02 M1.  `T(41,20)` sits on level 21 of the tower.  At depths
j <= 4 that level has one below-onset pin pair, `T(40,19)` and `T(39,18)`, and
so no check at its own level.  The guard `results/confidence.md` cited for its
one single-source constant, `D_4(21)`, is the 3-power congruence gate, which
tests integrality only: a shift of Delta in `D_4(21)` moves `T(41,20)` by 9 Delta,
and every single-entry error in the e = 3 row of the family table enters
`D_4(21)` with a coefficient in (1/9) Z, so every realistic table error shifts
a(41) by an INTEGER and the congruence gate stays green.  RED 1 below measures
exactly that, on a shadow copy of the table: +9 on `sig[3][21]` leaves
`gate-undertow-congruence` green and moves the depth-4 assembler's a(41) by 9.

The check that closes it has been in the tree since 2026-08-24 and was never
wired: `results/severance_w3_families_K21_e4.txt` gives depth 5, and at depth 5
level 21 has THREE pin pairs through `T(38,17)`, `T(39,18)`, `T(40,19)`.
`pp[3][21]` enters `D_4(21)` but not `D_5(21)`, and `sig`, `bb` enter the two
with different coefficients, so any single-entry error makes the pairs
disagree and `undertow_a41.build` refuses.  This gate runs that build and pins
its shape:

  * levels 20 and 21 pinned at depths j <= 5 from cells no taller than the
    swept H = 19, with the pin cells and pair counts PINNED here (a table that
    stops loading, or a triangle that loses a cell, shrinks the check and must
    fail rather than pass with less);
  * every depth pair at each level agrees (build() refuses otherwise);
  * a(41) reassembled from the tracked sweep `results/a41/h*.out` plus the
    tower equals the banked value, digit for digit;
  * the HOLDOUT (2026-09-05): the swept `T(41,20)` in `results/a41/h20.out`
    (dalby, 9.6 h on 76 cores, `scripts/dalby_a41_h20.sh`) equals the value
    the tower predicts for it from level 21 at depth 2, WITHOUT that cell
    among its pins.  This is the one enumeration that crosses assumption
    families for the tower's top level; a(41) itself no longer needs P_21.

RED controls (--selftest), each in a shadow copy of the family tables:
  1  sig[3][21] += 9   congruence gate GREEN, depth-4 a(41) shifted by +9
                       (the blind spot, measured), depth-5 build REFUSES;
  2  bb[3][21]  += 1   depth-5 build refuses;
  3  pp[3][21]  += 1   depth-5 build refuses (the column
                       results/depth5-gate-green.md called inert; it is not,
                       above depth 1);
  4  the e = 4, k = 21 row of the K21_e4 table, sig += 1: D_5's own input,
                       depth-5 build refuses;
  5  a banked pin cell T(38,17) += 1 in the triangle: refuses.
  6  the swept T(41,20) += 1 in a shadow copy of results/a41: the holdout
                       comparison reports the disagreement.

Usage:
  python3 experiments/undertow_pairs_gate.py             # the gate
  python3 experiments/undertow_pairs_gate.py --selftest  # RED controls

Exit 0 = GATE GREEN; anything else = red.  ~1 s.
"""

import contextlib
import io
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import severance_w3_depths as swd                                 # noqa: E402
import slope2_law_vs_truth as sl                                  # noqa: E402
from undertow_a41 import build, sweep_rows, tower                 # noqa: E402
import undertow_congruence_gate as ucg                            # noqa: E402
from lane_b_a41_recount import CLAIM as A41                       # noqa: E402

JMAX = 5                                       # one depth past the congruence gate's
KMAX, HMAX_PIN = ucg.KMAX, ucg.HMAX_PIN
SWEEP = os.path.join(ROOT, "results", "a41")
TABLES = os.path.join(ROOT, "results")

# Pinned shape of the two Undertow levels at depths <= 5, cells no taller than
# H = 19.  Level k, depth j is the cell (2k+1-j, k+1-j); every pair of its
# cells is a depth pair, so the pair count follows from the cell count.
EXPECT_CELLS = {
    20: {(36, 16), (37, 17), (38, 18), (39, 19)},          # j = 5, 4, 3, 2
    21: {(38, 17), (39, 18), (40, 19)},                     # j = 5, 4, 3
}


def quiet(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)


def assemble(jmax):
    """(ab, Dj, tri, a41) with the tower pinned at depths <= jmax."""
    ab, Dj, tri, _ = build(jmax, KMAX, forbid_row=41, hmax=HMAX_PIN)
    swept = sweep_rows(SWEEP, 41, HMAX_PIN)
    row = {H: swept[H] if H in swept else tower(ab, Dj, 41, H)
           for H in range(1, 42)}
    if len(swept) != HMAX_PIN:
        raise AssertionError(f"sweep supplies {len(swept)} heights, "
                             f"expected {HMAX_PIN}")
    return ab, Dj, tri, sum(row.values())


HOLDOUT = (41, 20)                             # swept 2026-09-05; level 21, depth 2


def holdout_check(ab, Dj, sweep_dir):
    """The swept T(41,20) against the tower's prediction for it.  The tower is
    built with hmax = HMAX_PIN, so the swept cell is not among its pins."""
    n, H = HOLDOUT
    swept = sweep_rows(sweep_dir, n)
    if H not in swept:
        return [f"holdout: {sweep_dir}/h{H}.out missing; T({n},{H}) was swept "
                f"2026-09-05 and must stay banked"]
    predicted = tower(ab, Dj, n, H)
    if swept[H] != predicted:
        return [f"holdout: swept T({n},{H}) = {swept[H]}, tower predicts "
                f"{predicted}"]
    return []


def run_gate(verbose=True, sweep_dir=SWEEP):
    ab, Dj, tri, total = quiet(assemble, JMAX)
    bad = []
    for k, cells in ucg.pin_cells(tri, JMAX, HMAX_PIN).items():
        if cells != EXPECT_CELLS[k]:
            bad.append(f"level {k} pin cells {sorted(cells)}, pinned at "
                       f"{sorted(EXPECT_CELLS[k])}")
        elif verbose:
            pairs = math.comb(len(cells), 2)
            print(f"  level k={k}: {pairs} depth pairs over {sorted(cells)} "
                  f"agree ({pairs - 1} independent checks)")
    if total != A41:
        bad.append(f"a(41) assembled {total}, banked {A41}")
    elif verbose:
        print(f"  a(41) = {total} from the tracked sweep + the depth-5 tower, "
              f"equal to the banked value")
    hb = holdout_check(ab, Dj, sweep_dir)
    bad += hb
    if not hb and verbose:
        n, H = HOLDOUT
        print(f"  holdout: swept T({n},{H}) equals the tower's level-{n-H} "
              f"depth-{2*(n-H)+1-n} prediction, that cell not among its pins")
    return bad


# ------------------------------------------------------------ RED controls
@contextlib.contextmanager
def shadow_tables(mutate):
    """Copy every family table to a temp dir, mutate one, and point the depth
    machinery at the copy.  _FAM is the module cache; it must be cleared both
    ways or the second run reads the first run's tables."""
    with tempfile.TemporaryDirectory() as d:
        for fn in os.listdir(TABLES):
            if fn.startswith("severance_w3_families_K") and fn.endswith(".txt"):
                shutil.copy(os.path.join(TABLES, fn), d)
        mutate(d)
        swd.TABLE_DIR, saved = d, swd.TABLE_DIR
        swd._FAM.clear()
        try:
            yield
        finally:
            swd.TABLE_DIR = saved
            swd._FAM.clear()


def bump(fname, e, k, col, delta):
    """Add delta to column col (2 = sig, 3 = bb, 4 = pp) of row (e, k)."""
    def m(d):
        p = os.path.join(d, fname)
        lines = open(p).read().splitlines()
        hit = 0
        for i, ln in enumerate(lines):
            q = ln.split()
            if q[:2] == [str(e), str(k)]:
                q[col] = str(int(q[col]) + delta)
                lines[i] = " ".join(q)
                hit += 1
        assert hit == 1, f"{fname}: row e={e} k={k} matched {hit} lines"
        open(p, "w").write("\n".join(lines) + "\n")
    return m


def refuses(jmax):
    try:
        quiet(assemble, jmax)
    except SystemExit as ex:
        return "disagree" in str(ex)
    return False


def selftest():
    problems = []
    if run_gate(verbose=False):
        problems.append("GREEN: the tree as it stands fails the gate")

    # RED 1: the audit's mutation, measured end to end.
    with shadow_tables(bump("severance_w3_families_K22_e3.txt", 3, 21, 2, 9)):
        ab, Dj, tri, total = quiet(assemble, 4)
        try:
            quiet(ucg.run_gate, ab, Dj, tri, quiet=True)
            congruence_green = True
        except AssertionError:
            congruence_green = False
        shift = total - A41
        if not congruence_green:
            problems.append("RED 1: sig[3][21]+9 turned the congruence gate red "
                            "-- the blind spot this gate documents has closed; "
                            "re-read AUDIT-2026-09-02 M1 before trusting this")
        if shift != 9:
            problems.append(f"RED 1: depth-4 a(41) moved by {shift}, "
                            f"expected 9 (the audit's 9*Delta lever)")
        if not refuses(5):
            problems.append("RED 1: sig[3][21]+9 was NOT refused at depth 5")
        else:
            print("RED 1 GREEN: sig[3][21]+9 -- congruence gate green, depth-4 "
                  "a(41) shifted by 9, depth-5 pairs disagree and refuse")

    # RED 2, 3: the other two exposed integers of the e = 3, k = 21 row.
    for col, name in ((3, "bb"), (4, "pp")):
        with shadow_tables(bump("severance_w3_families_K22_e3.txt", 3, 21, col, 1)):
            if refuses(5):
                print(f"RED {col - 1} GREEN: {name}[3][21]+1 refused at depth 5")
            else:
                problems.append(f"RED {col - 1}: {name}[3][21]+1 passed")

    # RED 4: D_5's own table.
    with shadow_tables(bump("severance_w3_families_K21_e4.txt", 4, 21, 2, 1)):
        if refuses(5):
            print("RED 4 GREEN: the K21_e4 table's e=4 k=21 sig+1 refused")
        else:
            problems.append("RED 4: a corrupted D_5 input passed")

    # RED 5: a corrupted pin cell in the triangle.
    real = sl.read_tri

    def tampered():
        t = real()
        t[(38, 17)] += 1
        return t
    import undertow_a41
    sl.read_tri, undertow_a41.read_tri = tampered, tampered
    try:
        if refuses(5):
            print("RED 5 GREEN: T(38,17)+1 in the triangle refused at depth 5")
        else:
            problems.append("RED 5: a corrupted pin cell passed")
    finally:
        sl.read_tri, undertow_a41.read_tri = real, real

    # RED 6: the swept holdout cell, corrupted in a shadow copy of the sweep.
    with tempfile.TemporaryDirectory() as d:
        shutil.copytree(SWEEP, os.path.join(d, "a41"))
        p = os.path.join(d, "a41", "h20.out")
        lines = open(p).read().splitlines()
        hit = 0
        for i, ln in enumerate(lines):
            q = ln.split()
            if q and q[0] == "41":
                q[1] = str(int(q[1]) + 1)
                lines[i] = " ".join(q)
                hit += 1
        assert hit == 1, f"h20.out: n = 41 matched {hit} lines"
        open(p, "w").write("\n".join(lines) + "\n")
        ab, Dj, tri, _ = quiet(assemble, JMAX)
        if holdout_check(ab, Dj, os.path.join(d, "a41")):
            print("RED 6 GREEN: swept T(41,20)+1 disagrees with the tower")
        else:
            problems.append("RED 6: a corrupted swept T(41,20) passed the holdout")

    if problems:
        print("undertow-pairs selftest FAILED:")
        for p in problems:
            print("  " + p)
        return 1
    print("undertow-pairs selftest ok: 1 green control, 6 RED controls, all fired")
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    print("undertow pairs, levels 20 and 21 at depths <= 5, pins at H <= 19, "
          "holdout T(41,20) swept:")
    bad = run_gate()
    if bad:
        print("\nundertow-pairs gate RED:")
        for b in bad:
            print("  " + b)
        return 1
    print("undertow-pairs gate GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
