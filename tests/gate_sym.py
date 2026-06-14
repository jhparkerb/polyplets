#!/usr/bin/env python3
"""Gate: symmetric-polyplet counters + free-count assembly vs external truth.

Validates the symmetric-animal generator for all four symmetry types against
the brute oracle's per-symmetry fixed-point counts, then assembles the free
polyplet count via Burnside and checks it against A030222 (the published
sequence) and the oracle. A mismatch in any symmetry type points at a wrong or
missing centre placement; a free-count mismatch points at the assembly.

  Free(n) = (Fixed + 2*R90 + R180 + 2*H + 2*D) / 8
where R90 = #(90-deg rot symmetric), R180 = #(180-deg), H = #(axis mirror,
one orientation), D = #(diagonal mirror, one orientation).
"""

import os
import subprocess
import sys

from common import ROOT, Gate, read_bfile

sys.path.insert(0, os.path.join(ROOT, "sym"))
sys.path.insert(0, os.path.join(ROOT, "oracle"))

from symcount import SYMMETRY_TYPES, count_symmetry_type  # noqa: E402
from g1_naive import count_symmetry  # noqa: E402

MAXN = 8  # oracle reach; enough to exercise every placement type
FAST_MAXN = 11  # depth for the C++ vs Python cross-check

# which oracle D4 fixed-point index each symmetry type must match
ORACLE_INDEX = {
    "90-degree rotation": 1,
    "180-degree rotation": 2,
    "axis mirror": 4,
    "diagonal mirror": 6,
}
# C++ symcount_fast CLI name for each symmetry type
FAST_NAME = {
    "90-degree rotation": "r90",
    "180-degree rotation": "r180",
    "axis mirror": "hmirror",
    "diagonal mirror": "dmirror",
}
FAST_BIN = os.path.join(ROOT, "build", "symcount_fast")


def main():
    gate = Gate()
    oracle = count_symmetry("square8", MAXN)
    cf = oracle["classfix"]  # D4 indices: 1=r90, 2=r180, 4=h, 6=d1

    # each symmetry type: placement-sum must equal the oracle's Fix(g)
    sym = {}
    for name, (placements, anchor) in SYMMETRY_TYPES.items():
        fix = cf[ORACLE_INDEX[name]]
        got = count_symmetry_type(placements, MAXN, anchor)
        oracle_vals = {n: fix[n] for n in range(1, MAXN + 1)}
        bad = [n for n in range(1, MAXN + 1) if got.get(n, 0) != fix[n]]
        label = f"{name:20s} vs oracle, n<={MAXN}"
        if bad:
            label += f"  MISMATCH {bad}\n   got={got}\n   oracle={oracle_vals}"
        gate.check(not bad, label)
        sym[name] = got

    # assemble free count via Burnside, using the published Fixed counts
    fixed = read_bfile("b006770.txt")          # A006770 fixed polyplets
    free_target = read_bfile("b030222.txt")    # A030222 free polyplets

    def s(name, n):
        return sym[name].get(n, 0)

    free_bad, free_calc = [], {}
    for n in range(1, MAXN + 1):
        total = (fixed[n] + 2 * s("90-degree rotation", n) + s("180-degree rotation", n)
                 + 2 * s("axis mirror", n) + 2 * s("diagonal mirror", n))
        if total % 8 != 0:
            free_bad.append((n, "not divisible by 8"))
            continue
        free_calc[n] = total // 8
        if n in free_target and free_calc[n] != free_target[n]:
            free_bad.append((n, f"{free_calc[n]} != A030222 {free_target[n]}"))
    label = f"free polyplets via Burnside vs A030222, n<={MAXN}"
    if free_bad:
        label += f"  MISMATCH {free_bad}"
    gate.check(not free_bad, label)

    # C++ fast counter must match the Python reference for every type
    if os.path.exists(FAST_BIN):
        for name, (placements, anchor) in SYMMETRY_TYPES.items():
            py = count_symmetry_type(placements, FAST_MAXN, anchor)
            out = subprocess.run([FAST_BIN, FAST_NAME[name], str(FAST_MAXN)],
                                 capture_output=True, text=True, check=True).stdout
            cpp = {}
            for line in out.strip().splitlines():
                a, b = line.split()
                cpp[int(a)] = int(b)
            py = {n: v for n, v in py.items() if v}
            gate.check(cpp == py, f"C++ {name:20s} == Python, n<={FAST_MAXN}")
    else:
        print(f"note: {FAST_BIN} absent, skipping C++ cross-check")

    return gate.verdict("symmetric/free")


if __name__ == "__main__":
    sys.exit(main())
