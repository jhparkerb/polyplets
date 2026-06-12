#!/usr/bin/env python3
"""Gate TMA: first transfer-matrix engine vs fixtures and the G2 engine.

Validation target is square-4 (polyominoes) per the implementation plan:
no new terms wanted, just the richest external truth available.

  A. totals: TMA counts equal b001168 (deeper than the oracle can reach)
  B. per-height: TMA's by-height counts equal G2's per-box height marginals
     (cross-ENGINE structural check: transfer matrix vs generation)
  C. ASan/UBSan build runs clean and agrees with the optimized build

CLI under test: tma LATTICE MAXN [--per-height]
  totals: "n count" lines; --per-height: "h n count" lines.
"""

import os
import subprocess
import sys

from common import ROOT, read_bfile

TMA = os.path.join(ROOT, "build", "tma")
TMA_ASAN = os.path.join(ROOT, "build", "tma_asan")
G2 = os.path.join(ROOT, "build", "g2")

failures = 0


def check(ok, label):
    global failures
    print(("ok   " if ok else "FAIL ") + label)
    if not ok:
        failures += 1


def run(binary, *args):
    r = subprocess.run([binary] + [str(a) for a in args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{binary} {args}: rc={r.returncode}\n{r.stderr}")
    return r.stdout


def parse_lines(out):
    d = {}
    for line in out.strip().splitlines():
        parts = line.split()
        d[tuple(map(int, parts[:-1]))] = int(parts[-1])
    return d


def main():
    for b in (TMA, TMA_ASAN, G2):
        if not os.path.exists(b):
            print(f"FAIL missing binary {b} (run: make)")
            return 1

    # A. totals vs fixture
    depth_a = 12
    expected = read_bfile("b001168.txt")
    got = parse_lines(run(TMA, "square4", depth_a))
    bad = [n for n in range(1, depth_a + 1) if got.get((n,)) != expected[n]]
    check(not bad, f"A totals      square4 n<={depth_a} vs b001168.txt"
          + (f"  MISMATCH at n={bad}" if bad else ""))

    # B. per-height vs G2 per-box marginals
    depth_b = 10
    tma_h = parse_lines(run(TMA, "square4", depth_b, "--per-height"))
    marg = {}
    for (n, w, h), c in parse_lines(run(G2, "square4", depth_b, "--per-box")).items():
        marg[(h, n)] = marg.get((h, n), 0) + c
    check(tma_h == marg,
          f"B per-height  square4 n<={depth_b} vs G2 per-box marginals "
          f"({len(marg)} (h,n) classes)")

    # C. sanitizer build agrees and runs clean
    depth_c = 9
    opt = parse_lines(run(TMA, "square4", depth_c))
    san = parse_lines(run(TMA_ASAN, "square4", depth_c))
    check(opt == san, f"C asan        square4 n<={depth_c} clean + equal")

    print("GATE TMA:", "GREEN" if failures == 0 else f"RED ({failures} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
