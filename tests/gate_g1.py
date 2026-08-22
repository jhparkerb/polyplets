#!/usr/bin/env python3
"""Gate G1: the oracle must reproduce the pinned OEIS b-files.

This is the project's first green gate (implementation-plan.md section 3).
Exits nonzero on any mismatch. Depth per lattice is chosen so the whole gate
runs in about a minute; deeper validation belongs to G2.
"""

import os
import re
import subprocess
import sys

from common import ROOT, Gate, read_bfile

sys.path.insert(0, os.path.join(ROOT, "oracle"))

from g1_naive import count_fixed  # noqa: E402

# lattice -> (b-file, max n for the quick gate)
CASES = {
    "square4": ("b001168.txt", 10),
    "square8": ("b006770.txt", 8),
    "tri6":    ("b001207.txt", 8),
}


# Every fixture must SAY where it came from and when anyone last looked.
#
# results/gate-class-sweep.md finding F5: SHA256SUMS pins the fixtures against
# accident but is itself regenerable, so it is no defence against a deliberate
# edit of both, and nothing in the suite can re-check a fixture against OEIS --
# the gates run with no network.  The control for that is
# scripts/fixture_oeis_recheck.py, run deliberately.  What the suite CAN do is
# refuse a fixture that carries no provenance at all, which is what fourteen of
# the fifteen did until 2026-08-22: bare columns of numbers with nothing saying
# their source or their date.
PROVENANCE_RE = re.compile(r"^#.*A\d{6}\.", re.M)
RECHECK_RE = re.compile(r"^#.*Re-verified against OEIS \d{4}-\d{2}-\d{2}", re.M)


def check_provenance(text):
    """(has an A-number line, has a dated re-verification line)."""
    return bool(PROVENANCE_RE.search(text)), bool(RECHECK_RE.search(text))


def main():
    sums = subprocess.run(
        ["shasum", "-a", "256", "-c", "SHA256SUMS"],
        cwd=os.path.join(ROOT, "fixtures"),
        capture_output=True, text=True)
    if sums.returncode != 0:
        print("FAIL: fixture checksums do not match SHA256SUMS")
        print(sums.stdout, sums.stderr)
        return 1

    gate = Gate()

    # --- fixture provenance, and a RED control that it can fail -------------
    fixdir = os.path.join(ROOT, "fixtures")
    missing = []
    for fn in sorted(os.listdir(fixdir)):
        if not re.fullmatch(r"b\d{6}\.txt", fn):
            continue
        anum, dated = check_provenance(open(os.path.join(fixdir, fn)).read())
        if not (anum and dated):
            missing.append(fn)
    gate.check(not missing,
               "every fixture names its A-number and its last OEIS re-check"
               + (f"  MISSING: {missing}" if missing else ""))
    gate.check(check_provenance("1 1\n2 4\n") == (False, False),
               "RED a fixture with no provenance header is detected")
    gate.check(check_provenance("# A006770.\n1 1\n") == (True, False),
               "RED an A-number alone, with no dated re-check, is not enough")
    for lattice, (bfile, maxn) in CASES.items():
        expected = read_bfile(bfile)
        got = count_fixed(lattice, maxn)
        for n in range(1, maxn + 1):
            if n not in expected:
                continue  # b-file may start past 1 or be short
            gate.check(got[n] == expected[n],
                       f"{lattice:8s} n={n:2d}  got {got[n]:>10d}  "
                       f"expect {expected[n]:>10d}  [{bfile}]")
    return gate.verdict("G1")


if __name__ == "__main__":
    sys.exit(main())
