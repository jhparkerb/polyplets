#!/usr/bin/env python3
"""Gate G1: the oracle must reproduce the pinned OEIS b-files.

This is the project's first green gate (implementation-plan.md section 3).
Exits nonzero on any mismatch. Depth per lattice is chosen so the whole gate
runs in about a minute; deeper validation belongs to G2.
"""

import os
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
