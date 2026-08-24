#!/usr/bin/env python3
"""Gate: symmetric transfer-matrix counter (symtm) vs the explicit
orbit-graph Redelmeier (symcount_fast) -- a cross-ALGORITHM check per
symmetry type (Hall of Mirrors thread).

symtm builds symmetric animals from ~n/2 free cells via the production
column transition, so it reaches n~34; symcount_fast is the independently
validated explicit counter (gate_sym: brute oracle + Burnside/A030222).
Identical 'n count' output to GATE_MAXN, live-run, is the bar, for all
three symtm modes.
"""

import os
import subprocess
import sys

from common import ROOT, Gate

# Six sequential runs (three types x two binaries) and, by this file's own
# note, ~2.9x per further n: hmirror@18 ~4 s, @20 33 s. Measured 68 s on gympie
# under `make gates -j10`, the largest single contributor to the push -- and
# only 18.9 s serial on dalby, which is why the dalby ranking never showed it.
# What the gate asserts is that two independent algorithms agree at every n;
# a cross-algorithm divergence does not wait until n=16 to appear. --deep
# restores n=18.
GATE_MAXN = 18 if "--deep" in sys.argv else 15
TYPES = ["hmirror", "r180", "dmirror"]

SYMTM = os.path.join(ROOT, "build", "symtm")
FAST = os.path.join(ROOT, "build", "symcount_fast")


def counts(binary, typ, maxn):
    out = subprocess.run([binary, typ, str(maxn)], capture_output=True,
                         text=True, check=True).stdout
    return {int(a): int(b) for a, b in
            (ln.split()[:2] for ln in out.splitlines() if ln.strip())}


def main():
    gate = Gate()
    for typ in TYPES:
        tm = counts(SYMTM, typ, GATE_MAXN)
        fast = counts(FAST, typ, GATE_MAXN)
        bad = [n for n in range(1, GATE_MAXN + 1)
               if tm.get(n, 0) != fast.get(n, 0)]
        label = f"symtm {typ} == symcount_fast, n<={GATE_MAXN}"
        if bad:
            label += (f"  MISMATCH at n={bad}"
                      f"\n   symtm={tm}\n   fast={fast}")
        gate.check(not bad, label)
    raise SystemExit(gate.verdict("SYMTM"))


if __name__ == "__main__":
    main()
