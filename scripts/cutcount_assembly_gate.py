#!/usr/bin/env python3
"""Gate CUTCOUNT-ASSEMBLY: Motley's banked rows still make the triangle.

Written 2026-08-19.  Everything Motley produced was in the tree -- the C_H rows,
the run log, the provenance note -- and NOTHING re-derived the one thing they
are for.  The assembly

    T(n,H) = C_H(n) - 2 C_{H-1}(n) + C_{H-2}(n)      (C_0 = C_{-1} = 0)

lived only inside scripts/dalby_confetti_h18.sh, a runner that executes on dalby
and that `make` never touches.  So the claim "T(n,18) matches the incumbent at
all 23 cells" rested on a log line, and a corrupted row would have sat in
results/ indefinitely without anything noticing.  Same shape as the front-page
a(40) that nothing checked and the residual counts that nothing checked; this
closes the third one.

Two checks, both from files in the tree:

  ASSEMBLY   every banked row results/cutcount_b1/rows/C<H>.out, H = 1..18,
             assembled and compared against results/triangle.txt.  567 cells.

  HELD-OUT   Confetti ran five primes: C_18 is reconstructed by CRT from four
             of them and the fifth is PREDICTED and compared against its
             measured row.  This is the run's decisive internal check and until
             the residue rows were banked (same day) it could not be re-run off
             the repo at all -- results/second-sources.md quoted the runner for it.
             The reconstruction is also compared against the banked exact row,
             which ties the residues to results/cutcount_b1/rows/C18.out.

Fail-closed on coverage, not just on disagreement: the cell and residue counts
are pinned, so a row that stops being read, a glob that matches nothing, or a
prime that quietly drops out fails the gate instead of shrinking it silently.

The Nmax-41 ladder (AUDIT-2026-09-02 M3), added 2026-09-05.  Commit 3a8d566
banked results/cutcount_b1/rows41/C1..C19.out, the colouring program's rows
at Nmax 41, with a README saying "8 primes reconstruct, the 9th is held out
and must predict every cell; all 19 heights passed" -- and nothing in `make`
read those rows or could re-derive that sentence.  The 171 residue rows and the
run logs were banked 2026-09-05 (results/cutcount_b1/residues41/,
rows41/run/), and three more arms run over them:

  ASSEMBLY-41  rows41 assembled and compared against results/triangle.txt at
               n <= 40: 589 cells, H = 1..19.
  ROW-41       rows41 assembled at n = 41 and compared against the kink
               engine's own sweep, results/a41/h<H>.out: 19 cells.  This is
               the two-engine agreement on the swept half of a(41), which the
               audit found "recorded nowhere in the tree".
  HELD-OUT-41  at EVERY height H = 1..19: CRT over the eight smaller primes,
               the largest predicted (scripts/motley_crt.py's rule, the one
               that produced the rows), the reconstruction tied back to
               rows41/C<H>.out, and each value under the runner's 2^112
               guard.  19 x 41 = 779 cells.

    python3 scripts/cutcount_assembly_gate.py            # gate
    python3 scripts/cutcount_assembly_gate.py --selftest # RED controls
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROWS = ROOT / "results" / "cutcount_b1" / "rows"
RESIDUES = ROOT / "results" / "cutcount_b1" / "residues"
TRIANGLE = ROOT / "results" / "triangle.txt"

def triangle_nmax():
    """The greatest n the banked triangle carries, DERIVED rather than pinned.

    Was `NMAX = 40`, hand-edited, and it made this gate's COVERAGE stale
    without making it red -- the failure class `scripts/provenance_table.py`
    already fixed for MOTLEY_H.  Planted 2026-08-22 during the gate-class
    sweep (`docs/engine-record.md`): with 41 fabricated rows appended to
    results/triangle.txt this gate stayed GREEN, because the assembly loop is
    `range(1, NMAX + 1)` and simply never looked at them, while
    gate-provenance and gate-residual-cells both went red on the same plant.

    Derived, the pinned counts below do the work instead: the day the triangle
    grows, EXPECT_CELLS and NMAX stop matching and the gate
    fires, which forces the coverage question to be answered deliberately.
    """
    nmax = 0
    for ln in TRIANGLE.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        nmax = max(nmax, int(ln.split()[0]))
    if nmax <= 0:
        raise SystemExit("cutcount gate: %s carries no rows" % TRIANGLE)
    return nmax


NMAX = triangle_nmax()
# Pinned coverage.  These are what the tree holds today; a rung that banks a new
# row must move them deliberately, which is the point.
EXPECT_TOP_H = 18                      # results/second-sources.md (Confetti)
EXPECT_CELLS = 567                     # rows H=1..18 against the triangle
EXPECT_PRIMES = 5                      # four for the CRT, one held out
CRT_BOUND = 1 << 112                   # the runner's overflow guard
PRIME_CHECK = ROOT / "scripts" / "confetti_prime_check.py"
EXPECT_PER_PRIME_CELLS = 23            # n = 18..40, the cells the triangle has

# The Nmax-41 ladder (results/cutcount_b1/rows41/README.md).
ROWS41 = ROOT / "results" / "cutcount_b1" / "rows41"
RESIDUES41 = ROOT / "results" / "cutcount_b1" / "residues41"
A41_SWEEP = ROOT / "results" / "a41"   # the kink engine's h<H>.out at Nmax 41
NMAX41 = 41
EXPECT41_TOP_H = 19
EXPECT41_CELLS = 589                   # rows H=1..19 vs the triangle, n <= 40
EXPECT41_ROW41_CELLS = 19              # T(41,H), H=1..19, vs results/a41
EXPECT41_PRIMES = 9                    # eight for the CRT, the largest held out
EXPECT41_HELDOUT_CELLS = 19 * 41       # every height, n = 1..41


def show(path: Path) -> str:
    """Repo-relative when it is in the repo, absolute when the selftest stages
    a copy in a temp tree."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_rows(path: Path) -> dict[int, int]:
    d = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, v = line.split()
        d[int(n)] = int(v)
    return d


def read_triangle(path: Path) -> dict[tuple[int, int], int]:
    T = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, h, v = line.split()
        T[(int(n), int(h))] = int(v)
    return T


def residue_rows(res_dir: Path, H: int = EXPECT_TOP_H) -> tuple[list[int], dict[int, Path]]:
    """The banked residue rows for height H, by prime.

    Both arms below need exactly this, and they used to find it twice with two
    copies of the glob, the filename pattern and the EXPECT_PRIMES pin -- which
    had already drifted: one filtered names the pattern rejects, the other
    called .group(1) on the failed match.  One reader, one posture.
    """
    found = {}
    for path in sorted(res_dir.glob("C%d.p*.out" % H)):
        m = re.fullmatch(r"C%d\.p(\d+)\.out" % H, path.name)
        if m:
            found[int(m.group(1))] = path
    return sorted(found), found


def assemble_rows(rows_dir: Path):
    """The banked C rows under rows_dir, {H: {n: C_H(n)}}, and the triangle
    they assemble to, {(n, H): T(n,H)} with T = C_H - 2 C_{H-1} + C_{H-2}
    (C_0 = C_{-1} = 0).  A height whose two predecessors are not both banked
    is left unassembled rather than read against a zero row, which would make
    a wrong T out of a gap; contiguity and coverage report the gap instead."""
    C = {0: {}, -1: {}}
    for p in sorted(rows_dir.glob("C*.out")):
        m = re.fullmatch(r"C(\d+)\.out", p.name)
        if m:
            C[int(m.group(1))] = read_rows(p)
    T = {}
    for h in sorted(h for h in C if h >= 1):
        if (h - 1) in C and (h - 2) in C:
            for n, c in C[h].items():
                T[(n, h)] = c - 2 * C[h - 1].get(n, 0) + C[h - 2].get(n, 0)
    return {h: r for h, r in C.items() if h >= 1}, T


def check_assembly(rows_dir: Path, triangle: Path, top_h: int = EXPECT_TOP_H,
                   expect_cells: int = EXPECT_CELLS) -> tuple[list[str], int]:
    """T(n,H) from the banked C rows vs the incumbent triangle.

    Only cells the triangle has are compared, so a row set at Nmax 41 is
    checked at n <= 40 here and its n = 41 cells by check_row41()."""
    bad = []
    C, M = assemble_rows(rows_dir)
    if not C:
        return (["no C<H>.out rows found under %s -- the gate is not checking "
                 "anything" % show(rows_dir)], 0)
    top = max(C)
    if sorted(C) != list(range(1, top + 1)):
        bad.append("banked rows are not H = 1..%d contiguous: %s"
                   % (top, sorted(C)))
    if top != top_h:
        bad.append("top banked row is H = %d, pinned at %d -- a rung landed or "
                   "a row vanished; update the pin deliberately"
                   % (top, top_h))
    T = read_triangle(triangle)
    cells = 0
    for (n, h), t in sorted(M.items()):
        if (n, h) not in T:
            continue
        cells += 1
        if t != T[(n, h)]:
            bad.append("T(%d,%d): assembled %d, triangle %d"
                       % (n, h, t, T[(n, h)]))
    if cells != expect_cells:
        bad.append("compared %d cells, pinned at %d -- coverage moved"
                   % (cells, expect_cells))
    return bad, cells


def read_sweep_row(sweep_dir: Path, n: int) -> dict[int, int]:
    """T(n,H) for every h<H>.out in a per-height sweep directory."""
    T = {}
    for p in sorted(sweep_dir.glob("h*.out")):
        m = re.fullmatch(r"h(\d+)\.out", p.name)
        if not m:
            continue
        for line in p.read_text().splitlines():
            q = line.split()
            if len(q) == 2 and int(q[0]) == n:
                T[int(m.group(1))] = int(q[1])
    return T


def check_row41(rows_dir: Path, sweep_dir: Path) -> tuple[list[str], int]:
    """T(41,H) assembled from the Nmax-41 Motley rows vs the kink engine's own
    Nmax-41 sweep -- two engines, no shared code, on every swept cell of a(41).
    """
    bad = []
    _, M = assemble_rows(rows_dir)
    sweep = read_sweep_row(sweep_dir, NMAX41)
    if not sweep:
        return (["no h<H>.out with an n = %d line under %s -- nothing to compare"
                 % (NMAX41, show(sweep_dir))], 0)
    cells = 0
    for h in range(1, EXPECT41_TOP_H + 1):
        if (NMAX41, h) not in M:
            bad.append("rows41 C%d.out, or a predecessor, is missing or carries "
                       "no n = %d line" % (h, NMAX41))
            continue
        if h not in sweep:
            bad.append("%s has no h%d.out with an n = %d line"
                       % (show(sweep_dir), h, NMAX41))
            continue
        cells += 1
        if M[(NMAX41, h)] != sweep[h]:
            bad.append("T(%d,%d): Motley %d, kink sweep %d"
                       % (NMAX41, h, M[(NMAX41, h)], sweep[h]))
    if cells != EXPECT41_ROW41_CELLS:
        bad.append("row 41: compared %d cells, pinned at %d"
                   % (cells, EXPECT41_ROW41_CELLS))
    return bad, cells


def check_heldout(res_dir: Path, rows_dir: Path, H: int = EXPECT_TOP_H,
                  expect_primes: int = EXPECT_PRIMES, heldout=min,
                  nmax: int = NMAX) -> tuple[list[str], int]:
    """CRT all primes but one, predict that one, tie the result to the banked
    exact row, at every n = 1..nmax.  `heldout` picks the prime the RUN held
    out: Confetti's runner held out the last of its list, the smallest (min);
    the Nmax-41 ladder used scripts/motley_crt.py, which holds out the largest
    (max)."""
    bad = []
    primes, paths = residue_rows(res_dir, H)
    if len(primes) != expect_primes:
        return (["C%d: found %d residue rows under %s, pinned at %d"
                 % (H, len(primes), show(res_dir), expect_primes)], 0)
    res = {q: read_rows(paths[q]) for q in primes}

    # The runner held out the LAST prime of its list, which is the smallest of
    # the five; naming it by the rule rather than by the literal means this
    # keeps checking the same thing if the set is ever regenerated.
    # TODO(2026-08-19, from the simplify pass): "last" and "smallest" coincide
    # only because the current list happens to be sorted descending, and
    # CRT_BOUND re-types the runner's own bound (dalby_confetti_h18.sh:98).
    # Both belong in a manifest beside the residue rows, written by the run and
    # read here, so a regenerated prime set cannot leave this gate verifying a
    # different contract than the run enforced.  That is a change to banked
    # evidence layout, so it is not a drive-by.
    held = heldout(primes)
    crt_primes = [p for p in primes if p != held]

    # TODO(2026-08-19, updated 2026-09-05): the FIFTH Python copy of this
    # CRT loop (scripts/crt_combine.py, tests/gate_modp.py, the runner's own,
    # and scripts/motley_crt.py).  motley_crt.py is importable (no argv at
    # import) and is the candidate to share; consolidating THIS copy would
    # erode the gate's second-source role against the dalby runner, so the
    # other three are the ones to collapse.  The Nmax-41 arm re-encodes
    # motley_crt's hold-out rule as `heldout=max`, and both gates carry the
    # ladder's paths, Nmax and prime count separately: one ladder record in
    # motley_crt.py, read by both, is the consolidation, deferred with the rest.
    M = 1
    for p in crt_primes:
        M *= p
    exact_path = rows_dir / ("C%d.out" % H)
    if exact_path.exists():
        exact = read_rows(exact_path)
    else:
        # The held-out prediction still stands on its own, but the tie-back to
        # the exact row cannot run.  Say so; do not skip it quietly.
        exact = {}
        bad.append("%s is missing -- the CRT reconstruction cannot be tied "
                   "back to the banked exact row" % show(exact_path))

    checked = 0
    for n in range(1, nmax + 1):
        if not all(n in res[p] for p in primes):
            bad.append("C%d n=%d missing from a residue row" % (H, n))
            continue
        x = 0
        for p in crt_primes:
            Mi = M // p
            x = (x + res[p][n] * Mi * pow(Mi, -1, p)) % M
        if x >= CRT_BOUND:
            bad.append("C%d n=%d: CRT reconstruction >= 2^%d, the runner's "
                       "overflow guard" % (H, n, CRT_BOUND.bit_length() - 1))
            continue
        if x % held != res[held][n]:
            bad.append("C%d n=%d: held-out prime %d predicts %d, measured %d"
                       % (H, n, held, x % held, res[held][n]))
            continue
        if n in exact and exact[n] != x:
            bad.append("C%d n=%d: CRT reconstruction %d != banked C%d.out %d"
                       % (H, n, x, H, exact[n]))
            continue
        checked += 1
    if checked != nmax:
        bad.append("C%d held-out check covered %d of %d cells" % (H, checked, nmax))
    return bad, checked


def check_heldout41(res_dir: Path, rows_dir: Path) -> tuple[list[str], int]:
    """The ladder's held-out verdict at every height, re-derived."""
    bad, total = [], 0
    for H in range(1, EXPECT41_TOP_H + 1):
        b, n = check_heldout(res_dir, rows_dir, H=H, expect_primes=EXPECT41_PRIMES,
                             heldout=max, nmax=NMAX41)
        bad += b
        total += n
    if total != EXPECT41_HELDOUT_CELLS:
        bad.append("Nmax-41 held-out check covered %d cells, pinned at %d"
                   % (total, EXPECT41_HELDOUT_CELLS))
    return bad, total


def check_per_prime(res_dir: Path, rows_dir: Path,
                    triangle: Path) -> tuple[list[str], int]:
    """Run Confetti's own checker, as delivered, on each of the five rows.

    A different direction from the CRT pass: for each prime separately it
    predicts C_H(n) mod p from the incumbent triangle and compares against the
    measured residue.  Necessary condition only -- blind to errors that are
    multiples of p -- but it exercises all five rows individually, including the
    four the held-out prediction only ever sees combined.  The script is
    fail-closed on zero cells compared and this reads its exit code.
    """
    bad, total = [], 0
    if not PRIME_CHECK.exists():
        return (["%s is missing; the per-prime check cannot run"
                 % show(PRIME_CHECK)], 0)
    primes, paths = residue_rows(res_dir)
    if len(primes) != EXPECT_PRIMES:
        return (["found %d residue rows for the per-prime check, pinned at %d"
                 % (len(primes), EXPECT_PRIMES)], 0)
    for prime in primes:
        f = paths[prime]
        r = subprocess.run(
            [sys.executable, str(PRIME_CHECK), str(EXPECT_TOP_H), str(prime),
             str(f), str(rows_dir / ("C%d.out" % (EXPECT_TOP_H - 1))),
             str(rows_dir / ("C%d.out" % (EXPECT_TOP_H - 2))), str(triangle)],
            capture_output=True, text=True)
        m = re.search(r"(\d+) match, (\d+) mismatch", r.stdout)
        if r.returncode != 0 or not m:
            bad.append("per-prime check failed for %d (rc=%d): %s"
                       % (prime, r.returncode,
                          " ".join((r.stdout + r.stderr).split())[:120]))
            continue
        match, mismatch = int(m.group(1)), int(m.group(2))
        if mismatch or match != EXPECT_PER_PRIME_CELLS:
            bad.append("per-prime check for %d: %d match, %d mismatch, "
                       "pinned at %d match"
                       % (prime, match, mismatch, EXPECT_PER_PRIME_CELLS))
        total += match
    return bad, total


def run(rows_dir=ROWS, res_dir=RESIDUES, triangle=TRIANGLE, verbose=True,
        rows41_dir=ROWS41, res41_dir=RESIDUES41, sweep41_dir=A41_SWEEP):
    bad_a, cells = check_assembly(rows_dir, triangle)
    bad_h, checked = check_heldout(res_dir, rows_dir)
    bad_p, per_prime = check_per_prime(res_dir, rows_dir, triangle)
    bad_a41, cells41 = check_assembly(rows41_dir, triangle, EXPECT41_TOP_H,
                                      EXPECT41_CELLS)
    bad_r41, row41 = check_row41(rows41_dir, sweep41_dir)
    bad_h41, held41 = check_heldout41(res41_dir, rows41_dir)
    if verbose:
        print("  assembly     %d cells from rows H = 1..%d vs results/triangle.txt"
              % (cells, EXPECT_TOP_H))
        print("  held-out     %d/%d residues predicted from the CRT over the "
              "other four, and equal to the banked exact row"
              % (checked, NMAX))
        print("  per-prime    %d cells over %d residue rows, each against the "
              "incumbent triangle via scripts/confetti_prime_check.py"
              % (per_prime, EXPECT_PRIMES))
        print("  assembly-41  %d cells from rows41 H = 1..%d vs results/triangle.txt"
              % (cells41, EXPECT41_TOP_H))
        print("  row-41       %d cells T(41,H) from rows41 vs the kink sweep "
              "results/a41/h*.out" % row41)
        print("  held-out-41  %d cells over %d heights: CRT over eight primes, "
              "the ninth predicted, tied to rows41/C<H>.out"
              % (held41, EXPECT41_TOP_H))
    return bad_a + bad_h + bad_p + bad_a41 + bad_r41 + bad_h41


def selftest() -> int:
    """RED controls: each defect this gate exists to catch must fire."""
    import shutil
    import tempfile
    problems = []

    def staged(mutate):
        """Copy the real inputs to a temp tree, mutate, and run the gate."""
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            shutil.copytree(ROWS, d / "rows")
            shutil.copytree(RESIDUES, d / "residues")
            shutil.copy(TRIANGLE, d / "triangle.txt")
            shutil.copytree(ROWS41, d / "rows41")
            shutil.copytree(RESIDUES41, d / "residues41")
            (d / "a41").mkdir()
            for f in A41_SWEEP.glob("h*.out"):
                shutil.copy(f, d / "a41")
            mutate(d)
            return run(d / "rows", d / "residues", d / "triangle.txt",
                       verbose=False, rows41_dir=d / "rows41",
                       res41_dir=d / "residues41", sweep41_dir=d / "a41")

    # GREEN: the tree as it stands passes.
    green = staged(lambda d: None)
    if green:
        problems.append("GREEN: the banked tree does not pass its own gate: %s"
                        % green)

    def bump(path, index=-1):
        """Perturb one cell (the last by default) of a banked file by one."""
        def m(d):
            p = d / path
            lines = p.read_text().splitlines()
            n, v = lines[index].split()
            lines[index] = "%s %d" % (n, int(v) + 1)
            p.write_text("\n".join(lines) + "\n")
        return m

    # RED 1: one wrong digit in an exact row must break the assembly.
    if not any("assembled" in b for b in staged(bump("rows/C18.out"))):
        problems.append("RED 1: a corrupted C18.out passed the assembly check")

    # RED 2: a corrupted row at a LOWER height too -- C18 is not special, and a
    # gate that only really watches the newest row is half a gate.
    if not any("assembled" in b for b in staged(bump("rows/C9.out"))):
        problems.append("RED 2: a corrupted C9.out passed the assembly check")

    # RED 3: a corrupted CRT residue must be caught.  In practice the OVERFLOW
    # guard gets there first and that is correct: a wrong residue throws the
    # reconstruction to a near-uniform value in [0, M) with M ~ 2^124, so it
    # lands above 2^112 with overwhelming probability.  Assert that the corrupt
    # cell is named, not which of the two guards names it.
    out = staged(bump("residues/C18.p2147483647.out"))
    if not any("n=40" in b for b in out):
        problems.append("RED 3: a corrupted CRT residue passed (%s)" % out[:2])

    # RED 4: corrupting the HELD-OUT row itself must fire too -- it is the one
    # row the reconstruction never reads, so a gate could miss it.
    if not any("held-out prime" in b
               for b in staged(bump("residues/C18.p2147483563.out"))):
        problems.append("RED 4: a corrupted held-out row passed")

    # RED 5: residues that reconstruct cleanly but disagree with the banked
    # exact row.  Without this the two artifacts could drift apart in the tree.
    def desync(d):
        p = d / "rows" / "C18.out"
        lines = p.read_text().splitlines()
        n, v = lines[-1].split()
        # +M is invisible to all five residues, so only the tie-back catches it
        M = 1
        for q in (2147483647, 2147483629, 2147483587, 2147483579):
            M *= q
        lines[-1] = "%s %d" % (n, int(v) + M)
        p.write_text("\n".join(lines) + "\n")
    out = staged(desync)
    if not any("!= banked" in b for b in out):
        problems.append("RED 5: an exact row out of step with its own residues "
                        "passed (%s)" % out[:2])

    # RED 6: the per-prime arm must catch a corrupt row too, and it is the only
    # arm that reads the four CRT rows one at a time.
    out = staged(bump("residues/C18.p2147483579.out"))
    if not any("per-prime" in b and "2147483579" in b for b in out):
        problems.append("RED 6: the per-prime check passed a corrupted row "
                        "(%s)" % out[:2])

    # RED 7: a missing prime must fail, not shrink the check.
    def drop_prime(d):
        (d / "residues" / "C18.p2147483587.out").unlink()
    if not any("pinned at %d" % EXPECT_PRIMES in b for b in staged(drop_prime)):
        problems.append("RED 7: a dropped residue row shrank the check instead "
                        "of failing it")

    # RED 8: a missing exact row must fail on contiguity and coverage, not pass
    # with fewer cells.
    def drop_row(d):
        (d / "rows" / "C12.out").unlink()
    out = staged(drop_row)
    if not any("contiguous" in b for b in out) \
            or not any("coverage moved" in b for b in out):
        problems.append("RED 8: a dropped C row did not fail contiguity and "
                        "coverage (%s)" % out[:3])

    # RED 9: vacuity -- an empty rows/ must fail rather than report clean.
    def empty(d):
        for p in (d / "rows").glob("C*.out"):
            p.unlink()
    if not any("not checking anything" in b for b in staged(empty)):
        problems.append("RED 9: an empty rows/ reported clean")

    # --- the Nmax-41 ladder.  Same failure classes, second row set.
    # RED 10: one wrong digit in rows41's C19 at n = 41 is visible ONLY to the
    # row-41 arm (the triangle has no row 41); it must fire there.
    out = staged(bump("rows41/C19.out"))
    if not any("T(41,19): Motley" in b for b in out):
        problems.append("RED 10: a corrupted rows41/C19.out at n = 41 passed "
                        "the row-41 arm (%s)" % out[:2])
    # RED 11: the same row corrupted at n = 40 must fire the triangle arm, and
    # at n = 41 the cell the kink sweep has -- both arms read the same file.
    out = staged(bump("rows41/C12.out", index=-2))
    if not any("T(40,12): assembled" in b for b in out):
        problems.append("RED 11: a corrupted rows41/C12.out at n = 40 passed "
                        "the assembly-41 arm (%s)" % out[:2])
    # RED 12: the kink sweep itself corrupted: the row-41 arm compares two
    # engines, so a wrong h<H>.out must fire too.
    out = staged(bump("a41/h7.out"))
    if not any("T(41,7): Motley" in b for b in out):
        problems.append("RED 12: a corrupted results/a41/h7.out passed (%s)"
                        % out[:2])
    # RED 13: a corrupted residue at a LOW height of the ladder must be named
    # -- the held-out arm runs at every height, not just the top one.
    out = staged(bump("residues41/C5.p65413.out"))
    if not any(b.startswith("C5 n=41") for b in out):
        problems.append("RED 13: a corrupted C5 residue passed the Nmax-41 "
                        "held-out arm (%s)" % out[:2])
    # RED 14: the held-out row of the ladder (the largest prime) corrupted.
    out = staged(bump("residues41/C19.p65521.out"))
    if not any("C19 n=41: held-out prime 65521" in b for b in out):
        problems.append("RED 14: a corrupted held-out row of the ladder passed "
                        "(%s)" % out[:2])
    # RED 15: a dropped prime shrinks nothing; it fails on the pin.
    def drop41(d):
        (d / "residues41" / "C9.p65479.out").unlink()
    if not any("C9: found 8 residue rows" in b for b in staged(drop41)):
        problems.append("RED 15: a dropped Nmax-41 residue row shrank the check")
    # RED 16: a missing kink sweep must fail rather than compare nothing.
    def drop_sweep(d):
        for f in (d / "a41").glob("h*.out"):
            f.unlink()
    if not any("nothing to compare" in b for b in staged(drop_sweep)):
        problems.append("RED 16: an empty results/a41 reported clean")

    if problems:
        print("cutcount-assembly selftest FAILED:")
        for p in problems:
            print("  " + p)
        return 1
    print("cutcount-assembly selftest ok: 1 green control, 16 RED controls, "
          "all fired")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    print("cutcount assembly, from the banked rows alone:")
    bad = run()
    if bad:
        print("\ncutcount-assembly gate RED:")
        for b in bad:
            print("  " + b)
        return 1
    print("cutcount-assembly gate GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
