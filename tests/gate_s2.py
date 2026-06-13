#!/usr/bin/env python3
"""Gate S2: free / one-sided counting via Burnside, brute-force ground truth.

Establishes the D4 Burnside machinery and the symmetry-class definitions
that the (future) efficient symmetric enumerator must reproduce. Checks:

  A. free polyominoes  == A000105   (square4)
  B. free polyplets    == A030222   (square8)   <- the S2 target sequence
  C. Burnside identity: sum(Fix(g))/8 == direct free dedup (both lattices)
  D. one-sided identity: sum_{rotations} Fix(g)/4 == direct one-sided dedup
  E. conjugacy equalities: Fix(r90)==Fix(r270), Fix(h)==Fix(v),
     Fix(d1)==Fix(d2)
"""

import os
import sys

from common import ROOT, read_bfile

sys.path.insert(0, os.path.join(ROOT, "oracle"))

from g1_naive import count_symmetry  # noqa: E402

DEPTH = {"square4": 10, "square8": 9}  # bounded by fixed-count explosion
failures = 0


def check(ok, label):
    global failures
    print(("ok   " if ok else "FAIL ") + label)
    if not ok:
        failures += 1


def main():
    results = {lat: count_symmetry(lat, d) for lat, d in DEPTH.items()}

    # A / B: free counts vs fixtures
    for lat, bfile, seq in [("square4", "b000105.txt", "A000105 free polyominoes"),
                            ("square8", "b030222.txt", "A030222 free polyplets")]:
        expected = read_bfile(bfile)
        free = results[lat]["free"]
        bad = [n for n in range(1, DEPTH[lat] + 1)
               if n in expected and free[n] != expected[n]]
        check(not bad, f"free {lat:8s} n<={DEPTH[lat]} vs {seq}"
              + (f"  MISMATCH {bad}" if bad else ""))

    # C / D: Burnside identities (free = sum/8, one-sided = rot-sum/4)
    for lat in DEPTH:
        r = results[lat]
        cf = r["classfix"]
        free_ok = all(sum(cf[i][n] for i in range(8)) == 8 * r["free"][n]
                      for n in r["free"])
        one_ok = all(sum(cf[i][n] for i in range(4)) == 4 * r["onesided"][n]
                     for n in r["onesided"])
        check(free_ok, f"burnside-free  {lat}: sum(Fix)/8 == direct dedup")
        check(one_ok, f"burnside-1side {lat}: sum_rot(Fix)/4 == direct dedup")

    # E: conjugacy equalities
    for lat in DEPTH:
        cf = results[lat]["classfix"]
        eqs = [(1, 3, "r90==r270"), (4, 5, "h==v"), (6, 7, "d1==d2")]
        ok = all(cf[a][n] == cf[b][n] for a, b, _ in eqs for n in cf[a])
        check(ok, f"conjugacy {lat}: " + ", ".join(e[2] for e in eqs))

    print("GATE S2:", "GREEN" if failures == 0 else f"RED ({failures} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
