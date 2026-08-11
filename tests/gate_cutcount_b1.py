#!/usr/bin/env python3
"""Gate CUTCOUNT-B1: the rule-independent second count of T(n,H) vs the banked
triangle, plus the controls that make that comparison non-vacuous.

B1 (cpp/cutcount_b1.cpp) is the second-source campaign's winner
(results/second-source-candidates.md §5.1): a colour-symmetrized spin transfer
matrix over Z[q]/(q^2) that never DECIDES connectivity -- no union-find verdict,
no stranded-component death -- and reads the connected count off the linear
coefficient. Its whole value is that it does not share the incumbent's
connectivity rule, so the one thing this gate must never do is pass without
actually comparing values: an unreadable banked directory used to print
"0 match, 0 MISMATCH" and exit 0. Checks D and E are that hazard, red-first.

Checks:
  A  H<=6,  n<=14  vs banked -- 84 cells, exit 0
  B  H<=10, n<=40  vs banked -- 400 cells, exit 0 (~5 s, the campaign's figure)
  C  the in-engine self-checks fire on every height (q0_zero, q1eval_binomial),
     the q=1 binomial identity being a full exercise of the transition weights
     with no connectivity in it anywhere
  D  RED control: one banked cell perturbed by +1 -> exit 2, and the reported
     mismatch is at exactly that (n,H)
  E  RED control: banked directory with no rows -> exit 3, not a silent pass
  F  the --assemble path (what the production run uses) agrees cell-for-cell
     with the full path (what checks A/B validate)
  G  RED control: a missing C_H row file must abort --assemble, not assemble a
     hole -- a resume that lost a height cannot look healthy
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

from common import ROOT, Gate

B1 = os.path.join(ROOT, "build", "cutcount_b1")
BANKED = os.path.join(ROOT, "results", "ns_a40", "perheight")


def run_b1(*args, expect_rc=0):
    r = subprocess.run([B1] + [str(a) for a in args],
                       capture_output=True, text=True)
    if r.returncode != expect_rc:
        raise RuntimeError(f"cutcount_b1 {args}: rc={r.returncode} "
                           f"(expected {expect_rc})\n{r.stdout}\n{r.stderr}")
    return r.stdout


def compare_line(out):
    """('match', 'MISMATCH') counts from the trailing comparison line."""
    m = re.search(r"vs banked triangle: (\d+) match, (\d+) MISMATCH", out)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def copy_banked(dst, hmax):
    os.makedirs(dst, exist_ok=True)
    for h in range(1, hmax + 1):
        shutil.copy(os.path.join(BANKED, f"h{h}.out"), os.path.join(dst, f"h{h}.out"))


def main():
    if not os.path.exists(B1):
        print(f"FAIL missing binary {B1} (run: make build/cutcount_b1)")
        return 1
    gate = Gate()
    tmp = tempfile.mkdtemp(prefix="gate_cutcount_b1_")
    try:
        # A / C -- small and instant, and the self-check evidence comes with it
        out = run_b1(6, 14, BANKED)
        ok, bad = compare_line(out)
        gate.check((ok, bad) == (84, 0), f"A  H<=6 n<=14 vs banked: {ok} match, {bad} mismatch (want 84, 0)")
        selfchecks = re.findall(r"selfcheck H=(\d+): q0_zero=OK q1eval_binomial=OK", out)
        gate.check(sorted(map(int, selfchecks)) == list(range(1, 7)),
                   f"C  in-engine self-checks fired on every height 1..6: {sorted(map(int, selfchecks))}")

        # B -- the campaign's headline validation figure
        out = run_b1(10, 40, BANKED)
        ok, bad = compare_line(out)
        gate.check((ok, bad) == (400, 0), f"B  H<=10 n<=40 vs banked: {ok} match, {bad} mismatch (want 400, 0)")

        # D -- RED control: a perturbed banked cell must be caught and located
        bad_dir = os.path.join(tmp, "banked_perturbed")
        copy_banked(bad_dir, 6)
        h5 = os.path.join(bad_dir, "h5.out")
        lines = open(h5).read().splitlines()
        hit = None
        for i, line in enumerate(lines):
            n, v = line.split()
            if int(n) == 12:
                lines[i] = f"{n} {int(v) + 1}"
                hit = (12, 5)
        open(h5, "w").write("\n".join(lines) + "\n")
        out = run_b1(6, 14, bad_dir, expect_rc=2)
        ok, bad = compare_line(out)
        located = re.search(r"first MISMATCH T\((\d+),(\d+)\)", out)
        gate.check(bad == 1 and ok == 83,
                   f"D  RED control (one banked cell +1): {ok} match, {bad} mismatch (want 83, 1), exit 2")
        gate.check(located is not None and (int(located.group(1)), int(located.group(2))) == hit,
                   f"D' RED control names the perturbed cell: {located.group(0) if located else 'none'} (want T(12,5))")

        # E -- RED control: nothing to compare is a failure, not a pass
        empty = os.path.join(tmp, "banked_empty")
        os.makedirs(empty)
        out = run_b1(4, 10, empty, expect_rc=3)
        ok, bad = compare_line(out)
        gate.check((ok, bad) == (0, 0),
                   f"E  RED control (empty banked dir): compared {ok} cells and exited 3, not 0")

        # F -- the production path (--height rows + --assemble) vs the full path
        rows = os.path.join(tmp, "rows")
        os.makedirs(rows)
        for h in range(1, 7):
            run_b1("--height", h, 14, os.path.join(rows, f"C{h}.out"))
        out = run_b1("--assemble", 6, 14, rows, BANKED)
        ok, bad = compare_line(out)
        gate.check((ok, bad) == (84, 0),
                   f"F  --assemble path vs banked: {ok} match, {bad} mismatch (want 84, 0)")

        # G -- RED control: a lost height must abort, not assemble a hole
        os.remove(os.path.join(rows, "C4.out"))
        r = subprocess.run([B1, "--assemble", "6", "14", rows, BANKED],
                           capture_output=True, text=True)
        gate.check(r.returncode == 1 and "missing" in r.stderr,
                   f"G  RED control (C_4 row deleted): --assemble aborts, rc={r.returncode}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return gate.verdict("CUTCOUNT-B1")


if __name__ == "__main__":
    sys.exit(main())
