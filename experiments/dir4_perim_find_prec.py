#!/usr/bin/env python3
"""Phase 2b: exact-rational P-recurrence for (dir4, HV-convex) by semiperimeter.

docs/middle-kingdom-followups-plan.md Phase 2b asks for
experiments/convex_perimeter.py's find_prec on the Phase 2a series
(results/mk_dir4_perim_terms_s200.txt, 199 terms).  find_prec works over Q
with Fractions, so a solution it returns is exact, not modular -- and it
returns one ONLY if the fit, trained on the first (unknowns + 4) rows,
annihilates every remaining row.  That is the Phase 1b holdout discipline
verbatim (results/convex-polyplets.md).

  usage:  experiments/dir4_perim_find_prec.py <J> <D> [terms_file]
  target: gympie, local, single-threaded
  cost:   measured, box (19,3), 80 unknowns: see results/dir4_perim_find_prec.log
          Nothing to resume; kill and rerun.
"""
import os
import sys
import time

from seriestools import read_terms

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convex_perimeter import find_prec  # noqa: E402
from dir4_perim_find_alg import primitive  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(ROOT, "results", "mk_dir4_perim_terms_s200.txt")


def main():
    J = int(sys.argv[1])
    D = int(sys.argv[2])
    path = sys.argv[3] if len(sys.argv) > 3 else DEFAULT
    seq = read_terms(path)
    unknowns = (J + 1) * (D + 1)
    rows = len(seq) - J
    train = unknowns + 4
    print(f"series={os.path.basename(path)} terms={len(seq)} box=({J},{D}) "
          f"unknowns={unknowns} rows={rows} train={train} holdout={rows-train}")
    t0 = time.time()
    sol = find_prec(seq, J, D)
    dt = time.time() - t0
    if sol is None:
        print(f"NO RECURRENCE in box ({J},{D})   [{dt:.1f}s]")
        return 1
    # Clear denominators and the overall gcd, so the printed operator is the
    # primitive integer one.
    ints = primitive(sol)

    # Independent re-verification over Q on EVERY row, not just the holdout.
    bad = 0
    for n in range(len(seq) - J):
        s = 0
        for j in range(J + 1):
            c = 0
            for d in range(D + 1):
                c += ints[j * (D + 1) + d] * n ** d
            s += c * seq[n + j]
        if s != 0:
            bad += 1
    print(f"FOUND in ({J},{D})  [{dt:.1f}s]  rows failing over Q: {bad} of "
          f"{len(seq)-J}")
    for j in range(J + 1):
        cs = ints[j * (D + 1):(j + 1) * (D + 1)]
        print(f"  p_{j}(n) = " + " + ".join(f"{c}*n^{d}" for d, c in
                                            enumerate(cs) if c))
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
