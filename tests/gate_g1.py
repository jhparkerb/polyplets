#!/usr/bin/env python3
"""Gate G1: the oracle must reproduce the pinned OEIS b-files.

This is the project's first green gate (implementation-plan.md section 3).
Exits nonzero on any mismatch. Depth per lattice is chosen so the whole gate
runs in about a minute; deeper validation belongs to G2.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "oracle"))

from g1_naive import count_fixed  # noqa: E402

# lattice -> (b-file, max n for the quick gate)
CASES = {
    "square4": ("b001168.txt", 10),
    "square8": ("b006770.txt", 8),
    "tri6":    ("b001207.txt", 8),
}


def read_bfile(name):
    terms = {}
    with open(os.path.join(ROOT, "fixtures", name)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            n, a = line.split()
            terms[int(n)] = int(a)
    return terms


def main():
    sums = subprocess.run(
        ["shasum", "-a", "256", "-c", "SHA256SUMS"],
        cwd=os.path.join(ROOT, "fixtures"),
        capture_output=True, text=True)
    if sums.returncode != 0:
        print("FAIL: fixture checksums do not match SHA256SUMS")
        print(sums.stdout, sums.stderr)
        return 1

    failures = 0
    for lattice, (bfile, maxn) in CASES.items():
        expected = read_bfile(bfile)
        got = count_fixed(lattice, maxn)
        for n in range(1, maxn + 1):
            if n not in expected:
                continue  # b-file may start past 1 or be short
            ok = got[n] == expected[n]
            mark = "ok " if ok else "FAIL"
            print(f"{mark} {lattice:8s} n={n:2d}  got {got[n]:>10d}  "
                  f"expect {expected[n]:>10d}  [{bfile}]")
            failures += 0 if ok else 1
    print("GATE G1:", "GREEN" if failures == 0 else f"RED ({failures} mismatches)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
