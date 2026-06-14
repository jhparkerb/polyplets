#!/usr/bin/env python3
"""Gate: symmetric-polyplet counters + free-count assembly vs external truth.

Chain of checks on one claim ("the symmetric counters + Burnside assembly are
correct"):
  1. each symmetry type's placement-sum == the brute oracle's Fix(g)  (n<=8)
  2. free polyplets via Burnside == A030222 (published sequence)       (n<=11)
  3. the C++ fast counter == the Python reference for every type        (n<=11)

The Python symmetric counts are computed once and reused across all three.
"""

import os
import subprocess
import sys

from common import ROOT, Gate, free_and_one_sided, read_bfile

sys.path.insert(0, os.path.join(ROOT, "sym"))
sys.path.insert(0, os.path.join(ROOT, "oracle"))

from symcount import SYMMETRY_TYPES, count_symmetry_type  # noqa: E402
from g1_naive import count_symmetry  # noqa: E402

ORACLE_MAXN = 8   # how far the brute oracle (generates all animals) reaches
MAXN = 11         # depth for Python counts, the C++ cross-check, and free assembly

# brute oracle D4 fixed-point index per symmetry type.
# D4 order in g1_naive.py: e(0) r90(1) r180(2) r270(3) h(4) v(5) d1(6) d2(7)
ORACLE_INDEX = {
    "90-degree rotation": 1,
    "180-degree rotation": 2,
    "axis mirror": 4,
    "diagonal mirror": 6,
}
FAST_NAME = {
    "90-degree rotation": "r90",
    "180-degree rotation": "r180",
    "axis mirror": "hmirror",
    "diagonal mirror": "dmirror",
}
FAST_BIN = os.path.join(ROOT, "build", "symcount_fast")


def main():
    gate = Gate()

    # Python symmetric counts, computed once, reused by all three checks.
    sym = {name: count_symmetry_type(pl, MAXN, anchor)
           for name, (pl, anchor) in SYMMETRY_TYPES.items()}

    # 1. each type vs the brute oracle
    cf = count_symmetry("square8", ORACLE_MAXN)["classfix"]
    for name in SYMMETRY_TYPES:
        fix = cf[ORACLE_INDEX[name]]
        bad = [n for n in range(1, ORACLE_MAXN + 1) if sym[name].get(n, 0) != fix[n]]
        label = f"{name:20s} vs oracle, n<={ORACLE_MAXN}"
        if bad:
            label += (f"  MISMATCH {bad}\n   got={sym[name]}"
                      f"\n   oracle={{n: fix[n] for n in range(1, ORACLE_MAXN + 1)}}")
        gate.check(not bad, label)

    # 2. free polyplets via Burnside vs A030222
    fixed = read_bfile("b006770.txt")
    free_target = read_bfile("b030222.txt")
    free_bad = []
    for n in range(1, MAXN + 1):
        try:
            free, _ = free_and_one_sided(
                fixed[n], sym["90-degree rotation"].get(n, 0),
                sym["180-degree rotation"].get(n, 0),
                sym["axis mirror"].get(n, 0), sym["diagonal mirror"].get(n, 0))
        except ValueError as ex:
            free_bad.append((n, str(ex)))
            continue
        if n in free_target and free != free_target[n]:
            free_bad.append((n, f"{free} != A030222 {free_target[n]}"))
    gate.check(not free_bad,
               f"free polyplets via Burnside vs A030222, n<={MAXN}"
               + (f"  MISMATCH {free_bad}" if free_bad else ""))

    # 3. C++ fast counter vs the Python reference
    if os.path.exists(FAST_BIN):
        for name in SYMMETRY_TYPES:
            out = subprocess.run([FAST_BIN, FAST_NAME[name], str(MAXN)],
                                 capture_output=True, text=True, check=True).stdout
            cpp = {}
            for line in out.strip().splitlines():
                a, b = line.split()
                cpp[int(a)] = int(b)
            ref = {n: v for n, v in sym[name].items() if v}
            gate.check(cpp == ref, f"C++ {name:20s} == Python, n<={MAXN}")
    else:
        print(f"note: {FAST_BIN} absent, skipping C++ cross-check")

    return gate.verdict("symmetric/free")


if __name__ == "__main__":
    sys.exit(main())
