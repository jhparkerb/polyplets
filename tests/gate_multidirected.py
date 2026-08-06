#!/usr/bin/env python3
"""Gate MULTIDIRECTED: docs/middle-kingdom-plan.md Phase 1c acceptance.

Two independent routes to the number m(n) of MULTI-DIRECTED king animals of
area n, in Bacher's sense (arXiv:1301.1365, Definition 2):

  series  experiments/multidirected_king.py -- the Nordic-decomposition
          generating function M = D/(1-B) of Theorem 8, exact integer series,
          reaches n=200 in seconds
  brute   build/directed_cone_anchor mdir -- Redelmeier DFS over ALL fixed king
          animals with Definition 2 evaluated directly on every animal
          generated (local-minimum sources, keystone two-sided condition)

They share no code and no idea: one is a functional equation on heaps of
segments, the other is reachability bookkeeping on cell sets. They must agree
on every n where both are available.

RED controls, all fail-closed (an agreement here FAILS the gate):

  mdirbad  Definition 2 with condition (2) -- the keystone two-sided
           requirement -- dropped. A strict superset predicate; must NOT
           reproduce m(n).
  dir5nb   "control B" of results/directed-cone-anchor.md: forward flood from
           every GLOBAL-bottom-row cell. results/directed-king-animals.md used
           to call this predicate "multi-directed"; it is not, and this check
           pins that (it diverges at n=4, 106 vs 110). See
           results/multi-directed.md.
  dir5     Bacher's DIRECTED animals, A047781. Must be a strict subset:
           d(n) <= m(n) with strict inequality somewhere.

Plus the trap the phase exists to avoid: the ratio m(n)/m(n-1) must approach
mu = 1/rho_M = 6.4752 and NOT 1/rho_B = 6.1175, the pole of the intermediate
series B (Lemma 11). A series trending to 6.118 is a wrong definition or a
bug, never a finding.
"""
import os
import subprocess
import sys
import time

from common import ROOT, Gate

sys.path.insert(0, os.path.join(ROOT, "experiments"))
import multidirected_king as mdk  # noqa: E402

BIN = os.path.join(ROOT, "build", "directed_cone_anchor")

A047781 = [1, 4, 19, 96, 501, 2668, 14407, 78592, 432073, 2390004]
# results/middle-kingdom-grid.md, ctrlB column (bottom-row-waived flood).
CTRL_B = [1, 4, 20, 106, 576, 3179, 17736, 99748, 564430, 3209194,
          18316729, 104872413]
MU = 6.4752      # Bacher Corollary 12, 1/rho_M
MU_B = 6.1175    # Lemma 11, 1/rho_B -- the decoy


def run_filter(mode, n, threads=8):
    """Run a filter mode; return {n: filtered_count} and the wall time."""
    t0 = time.time()
    proc = subprocess.run([BIN, mode, str(n), str(threads)],
                          capture_output=True, text=True, check=True)
    wall = time.time() - t0
    out = {}
    for line in proc.stdout.strip().splitlines():
        p = [int(x) for x in line.split()]
        out[p[0]] = p[2]
    return out, wall


def main():
    gate = Gate()
    if not os.path.exists(BIN):
        print(f"FAIL missing {BIN} (run: make build/directed_cone_anchor)")
        return 1

    nseries = 200
    t0 = time.time()
    _, _, _, d, b, m = mdk.multidirected(nseries)
    print(f"series to n={nseries}: {time.time() - t0:.1f}s")

    # --- the series is anchored on its own before it anchors anything -------
    s = mdk.half_animals(nseries)
    gate.check(s[1:12] == mdk.A001003[1:12],
               "series S = A001003 (little Schroeder half-animals)")
    gate.check(d == mdk.directed_closed_form(nseries),
               "series D from (1)-(3) = closed form (1/4)((1+t)/sqrt(1-6t+t^2)-1)")
    gate.check(d[1:11] == A047781, "series D = A047781 (directed king animals)")

    # --- brute force vs series ---------------------------------------------
    accept_n = 12
    brute, wall = run_filter("mdir", accept_n)
    print(f"brute mdir n={accept_n}: wall={wall:.1f}s (budget 600s)")
    gate.check(wall < 600, f"mdir n={accept_n} runs under 10 minutes")
    bad = [n for n in range(1, accept_n + 1) if brute.get(n) != m[n]]
    gate.check(not bad,
               f"brute-force Definition 2 == GF series, n<={accept_n}"
               + (f"  MISMATCH at n={bad}: brute "
                  f"{[brute.get(n) for n in bad]} vs series {[m[n] for n in bad]}"
                  if bad else ""))

    # --- RED control: condition (2) dropped --------------------------------
    bad_brute, _ = run_filter("mdirbad", 8, threads=4)
    got = [bad_brute[n] for n in range(1, 9)]
    want = [m[n] for n in range(1, 9)]
    gate.check(got != want,
               f"RED control mdirbad (keystone condition dropped) MUST diverge "
               f"from m(n): got {got}")
    gate.check(all(got[i] >= want[i] for i in range(8)),
               f"mdirbad is a superset predicate (>= m(n) termwise): {got}")

    # --- RED control: control B is NOT multi-directed -----------------------
    k = min(len(CTRL_B), accept_n)
    ctrl = CTRL_B[:k]
    gate.check(ctrl != [m[n] for n in range(1, k + 1)],
               "RED control dir5nb ('control B') MUST diverge from m(n)")
    gate.check(CTRL_B[3] == 106 and m[4] == 110,
               f"control B diverges from multi-directed first at n=4: "
               f"{CTRL_B[3]} vs {m[4]}")
    ctrlb_live, _ = run_filter("dir5nb", 8, threads=4)
    gate.check([ctrlb_live[n] for n in range(1, 9)] == CTRL_B[:8],
               "dir5nb still reproduces the recorded control B column")

    # --- directed is a strict subset ---------------------------------------
    gate.check(all(d[n] <= m[n] for n in range(1, nseries + 1))
               and d[5] < m[5],
               "directed A047781 is a strict subset of multi-directed")

    # --- the growth-constant trap ------------------------------------------
    ratio = m[nseries] / m[nseries - 1]
    gate.check(abs(ratio - MU) < 5e-4,
               f"m({nseries})/m({nseries-1}) = {ratio:.6f} -> mu = {MU}")
    gate.check(abs(ratio - MU_B) > 0.3,
               f"ratio is NOT drifting to 1/rho_B = {MU_B} (the Lemma 11 decoy)")
    # B's pole really is the root of 1 - 5x - 7x^2 + x^3, so the decoy value
    # used above is the paper's, not a number invented here.
    gate.check(abs(1.0 / mdk.rho_b() - MU_B) < 5e-4,
               f"1/rho_B from 1-5x-7x^2+x^3 = {1.0 / mdk.rho_b():.4f}")
    # B(rho_M) = 1 (Theorem 10): the series B evaluated at 1/mu must sit at 1.
    bval = sum(b[i] * MU ** -i for i in range(len(b)))
    gate.check(abs(bval - 1.0) < 1e-3,
               f"B(1/mu) = {bval:.6f} = 1 (Theorem 10, B(rho_M)=1)")

    return gate.verdict("MULTIDIRECTED")


if __name__ == "__main__":
    sys.exit(main())
