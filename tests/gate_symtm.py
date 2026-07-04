#!/usr/bin/env python3
"""Gate: symmetric transfer-matrix counter (symtm) vs the explicit
orbit-graph Redelmeier (symcount_fast) -- a cross-ALGORITHM check per
symmetry type (Hall of Mirrors thread).

symtm builds symmetric animals from ~n/2 free cells via the production
column transition, so it reaches n~34; symcount_fast is the independently
validated explicit counter (gate_sym: brute oracle + Burnside/A030222).
Identical 'n count' output to GATE_MAXN, live-run, is the bar. Types are
gated as their symtm mode lands: hmirror now; r180, dmirror to follow.
"""

import os
import subprocess

from common import ROOT, Gate

GATE_MAXN = 18  # symcount_fast hmirror@18 ~4s on gympie; @20 is 33s, too slow
TYPES = ["hmirror"]

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
