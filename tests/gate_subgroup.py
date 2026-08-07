#!/usr/bin/env python3
"""Gate: subgroup-invariant polyplet counts, and the a(n) mod 4 congruence.

D4 acts on fixed (translation-class) king animals; orbit sizes divide 8, so
a(n) = n1 + 2 n2 + 4 n4 + 8 n8 with n_k = #orbits of size k.  Writing I(H) for
the number of fixed animals invariant under a subgroup H <= D4:

  n1 = I(D4)
  2 n2 = I(C4) + I(D2ax) + I(D2diag) - 3 I(D4)      (stabiliser order exactly 4)
  ==>  a(n) = I(C4) + I(D2ax) + I(D2diag) - 2 I(D4)   (mod 4)

The three order-4 subgroups are each a quotient-domain family of size
~lambda^(n/4), so the right-hand side is reachable at n = 40 while a(40)
itself took the full engine.  That is what makes this an independent check.

Checks, in printed order:
  1. Python symcount subgroup counts == brute oracle, n <= 8
  2. C++ symcount_fast == Python, n <= 11
  3. the mod-4 congruence vs the published A006770 b-file, n <= 11
  4. CONTROLS that must diverge (a check with no teeth passes vacuously)
"""

import os
import subprocess
import sys

from common import ROOT, Gate, read_bfile

sys.path.insert(0, os.path.join(ROOT, "sym"))
sys.path.insert(0, os.path.join(ROOT, "oracle"))

from symcount import (HMIRROR_PLACEMENTS, SUBGROUP_TYPES,  # noqa: E402
                      SYMMETRY_TYPES, _anchor_xmin0, count_symmetry_type)
from g1_naive import count_by_box, count_symmetry  # noqa: E402

ORACLE_MAXN = 8   # brute force generates every animal, so this is the cheap wall
MAXN = 11         # Python reference depth and the C++ cross-check depth

FAST_BIN = os.path.join(ROOT, "build", "symcount_fast")


def cpp_counts(name, maxn):
    out = subprocess.run([FAST_BIN, name, str(maxn)],
                         capture_output=True, text=True, check=True).stdout
    return {int(a): int(b) for a, b in
            (line.split() for line in out.strip().splitlines())}


def main():
    gate = Gate()

    sym = {name: count_symmetry_type(pl, MAXN, anchor)
           for name, (pl, anchor) in SUBGROUP_TYPES.items()}

    # 1. Python vs the brute oracle.
    sub = count_symmetry("square8", ORACLE_MAXN)["subfix"]
    for name in SUBGROUP_TYPES:
        bad = [n for n in range(1, ORACLE_MAXN + 1)
               if sym[name].get(n, 0) != sub[name][n]]
        label = f"I({name:6s}) vs brute oracle, n<={ORACLE_MAXN}"
        if bad:
            label += (f"  MISMATCH at {bad}\n   got={sym[name]}"
                      f"\n   oracle={sub[name]}")
        gate.check(not bad, label)

    # 2. C++ vs Python.
    if os.path.exists(FAST_BIN):
        for name in SUBGROUP_TYPES:
            ref = {n: v for n, v in sym[name].items() if v}
            gate.check(cpp_counts(name, MAXN) == ref,
                       f"C++ symcount_fast {name:6s} == Python, n<={MAXN}")
    else:
        print(f"note: {FAST_BIN} absent, skipping C++ cross-check")

    # 3. The congruence itself, against the published sequence.
    fixed = read_bfile("b006770.txt")
    def rhs(n):
        return (sym["c4"].get(n, 0) + sym["d2ax"].get(n, 0)
                + sym["d2diag"].get(n, 0) - 2 * sym["d4"].get(n, 0))
    bad = [n for n in range(1, MAXN + 1) if (fixed[n] - rhs(n)) % 4]
    gate.check(not bad,
               f"a(n) = I(C4)+I(D2ax)+I(D2diag)-2I(D4) (mod 4), n<={MAXN}"
               + (f"  MISMATCH at {bad}" if bad else ""))

    # 3b. The mod-8 companion.  Every I(C4) and I(D4) term cancels; the two
    #     order-2 mirror CLASSES each contribute twice ({e,h} with {e,v}, and
    #     {e,d} with {e,ad}), which is where both factors of 2 come from.
    #     Gated because the first version of it shipped with those factors
    #     dropped and was wrong on 21 of 33 rows.
    elem = {name: count_symmetry_type(pl, MAXN, anchor)
            for name, (pl, anchor) in SYMMETRY_TYPES.items()}

    def rhs8(n, k):
        return (elem["180-degree rotation"].get(n, 0)
                + 2 * elem["axis mirror"].get(n, 0)
                + 2 * elem["diagonal mirror"].get(n, 0)
                - k * sym["d2ax"].get(n, 0) - k * sym["d2diag"].get(n, 0))
    bad8 = [n for n in range(1, MAXN + 1) if (fixed[n] - rhs8(n, 2)) % 8]
    gate.check(not bad8,
               f"a(n) = Fix(r180)+2Fix(h)+2Fix(d)-2I(D2ax)-2I(D2diag) (mod 8),"
               f" n<={MAXN}" + (f"  MISMATCH at {bad8}" if bad8 else ""))
    slipped = [n for n in range(1, MAXN + 1) if (fixed[n] - rhs8(n, 1)) % 8]
    gate.check(bool(slipped),
               "control: coefficient 1 instead of 2 breaks it"
               + (f" (first at n={slipped[0]})" if slipped else " -- IT DID NOT"))

    # 4. Controls. Each must FAIL the corresponding true statement somewhere,
    #    or the check above would be passing on a degenerate identity.
    dropped = [n for n in range(1, MAXN + 1)
               if (fixed[n] - (rhs(n) - sym["d2ax"].get(n, 0))) % 4]
    gate.check(bool(dropped),
               "control: dropping I(D2ax) breaks the congruence"
               + (f" (first at n={dropped[0]})" if dropped else " -- IT DID NOT"))

    same = [n for n in range(1, MAXN + 1)
            if sym["d2ax"].get(n, 0) != sym["d2diag"].get(n, 0)]
    gate.check(bool(same),
               "control: D2ax and D2diag are genuinely different families"
               + (f" (first at n={same[0]})" if same else " -- THEY ARE NOT"))

    # The specific error this whole file exists to avoid: using the per-element
    # Fix(h) where the per-subgroup I(D2ax) is meant. It must break the
    # congruence, or the distinction would be cosmetic.
    hmirror = count_symmetry_type(HMIRROR_PLACEMENTS, MAXN, _anchor_xmin0)
    swapped = [n for n in range(1, MAXN + 1)
               if (fixed[n] - (rhs(n) - sym["d2ax"].get(n, 0)
                               + hmirror.get(n, 0))) % 4]
    gate.check(bool(swapped),
               "control: substituting Fix(h) for I(D2ax) breaks the congruence"
               + (f" (first at n={swapped[0]})" if swapped
                  else " -- IT DID NOT"))

    # I(D4) is supported only on n = 0, 1 (mod 4): a D4-invariant animal splits
    # into cell-orbits of size 8, 4 (axis or diagonal) and 1 (the centre only).
    off = [n for n in range(1, MAXN + 1)
           if n % 4 in (2, 3) and sym["d4"].get(n, 0)]
    gate.check(not off,
               "I(D4) vanishes for n = 2, 3 (mod 4)"
               + (f"  VIOLATED at {off}" if off else ""))

    # 5. Height-graded parity.  D2ax = {e,h,v,r180} is EXACTLY the
    #    height-preserving subgroup of D4 (r90, r270 and both diagonal mirrors
    #    swap height with width), so it acts on the animals of each fixed
    #    height H and orbit sizes there divide 4:
    #        T(n,H) = m1 + 2 m2 + 4 m4   ==>   T(n,H) = I_H(D2ax)  (mod 2)
    #    One independent bit per triangle CELL, which is what localises the
    #    check to a height band rather than the row total.
    if os.path.exists(FAST_BIN):
        out = subprocess.run([FAST_BIN, "d2ax", str(MAXN), "--byheight"],
                             capture_output=True, text=True, check=True).stdout
        byh = {}
        for line in out.strip().splitlines():
            n, h, v = (int(x) for x in line.split())
            byh[(n, h)] = v
        flat = {n: sum(v for (m, _), v in byh.items() if m == n)
                for n in range(1, MAXN + 1)}
        gate.check(flat == {n: v for n, v in sym["d2ax"].items() if v},
                   f"--byheight rows sum to the flat d2ax counts, n<={MAXN}")

        box = count_by_box("square8", ORACLE_MAXN)
        tri = {}
        for (n, _w, h), v in box.items():
            tri[(n, h)] = tri.get((n, h), 0) + v
        bad = [(n, h) for (n, h) in tri
               if n <= ORACLE_MAXN and (tri[(n, h)] - byh.get((n, h), 0)) % 2]
        gate.check(not bad,
                   f"T(n,H) = I_H(D2ax) (mod 2) vs brute oracle, n<={ORACLE_MAXN}"
                   + (f"  MISMATCH at {sorted(bad)}" if bad else ""))

        # Control: D2diag does NOT preserve height, so grading it by height
        # must break the same parity statement somewhere.
        out = subprocess.run([FAST_BIN, "d2diag", str(MAXN), "--byheight"],
                             capture_output=True, text=True, check=True).stdout
        dd = {}
        for line in out.strip().splitlines():
            n, h, v = (int(x) for x in line.split())
            dd[(n, h)] = v
        broken = [(n, h) for (n, h) in tri
                  if n <= ORACLE_MAXN and (tri[(n, h)] - dd.get((n, h), 0)) % 2]
        gate.check(bool(broken),
                   "control: D2diag graded by height breaks the parity"
                   + (f" (e.g. n,H={sorted(broken)[0]})" if broken
                      else " -- IT DID NOT"))

    return gate.verdict("subgroup/mod-4")


if __name__ == "__main__":
    sys.exit(main())
