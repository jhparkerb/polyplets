#!/usr/bin/env python3
"""Assemble free / one-sided polyplet counts from fixed + symmetric counts.

Free(n)      = (Fixed + 2*R90 + R180 + 2*H + 2*D) / 8
One-sided(n) = (Fixed + 2*R90 + R180) / 4

Fixed comes from A006770 (b-file, known to 18); the four symmetric counts come
from the validated C++ counter (build/symcount_fast). Verifies Free against
A030222 on the overlap (n<=17) before reporting any new term, so a wrong
symmetric count or a wrong Fixed(19) candidate is caught against external
truth.

Usage: free_polyplets.py MAXN [FIXED_19]
  FIXED_19 optionally supplies the (candidate) a(19) so Free(19) can be formed.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tests"))
from common import read_bfile  # noqa: E402

FAST = os.path.join(ROOT, "build", "symcount_fast")
TYPES = ["r90", "r180", "hmirror", "dmirror"]


def sym_counts(t, maxn):
    out = subprocess.run([FAST, t, str(maxn)], capture_output=True, text=True,
                         check=True).stdout
    d = {}
    for line in out.strip().splitlines():
        n, c = line.split()
        d[int(n)] = int(c)
    return d


def main():
    maxn = int(sys.argv[1])
    fixed = read_bfile("b006770.txt")
    if len(sys.argv) > 2:
        fixed[19] = int(sys.argv[2])
    free_known = read_bfile("b030222.txt")

    print(f"computing symmetric counts to n={maxn} (C++)...", flush=True)
    sym = {t: sym_counts(t, maxn) for t in TYPES}

    def g(t, n):
        return sym[t].get(n, 0)

    print(f"{'n':>3} {'free':>22} {'one-sided':>22}  note")
    for n in range(1, maxn + 1):
        if n not in fixed:
            continue
        ft = (fixed[n] + 2 * g("r90", n) + g("r180", n)
              + 2 * g("hmirror", n) + 2 * g("dmirror", n))
        ot = fixed[n] + 2 * g("r90", n) + g("r180", n)
        assert ft % 8 == 0, f"Free({n}) not divisible by 8"
        assert ot % 4 == 0, f"OneSided({n}) not divisible by 4"
        free, one = ft // 8, ot // 4
        note = ""
        if n in free_known:
            note = "ok vs A030222" if free == free_known[n] else \
                   f"!!! A030222 says {free_known[n]}"
        else:
            note = "NEW TERM"
        print(f"{n:>3} {free:>22} {one:>22}  {note}")


if __name__ == "__main__":
    sys.exit(main())
