"""Fail-closed gate for Severance W1 (docs/onset-defect-severance-plan.md §3).

Checks the C++ cluster-weight port (build/severance_w1) against:
  A. the banked per-composition KNOWN_WEIGHTS, k <= 5, exactly;
  B. level-6 holdouts: (7,) fully via the Python DP, (4,4)/(3,5) interior
     against banked TWO_ROW_INTERIOR, their boundary/pure via the Python DP;
  C. structural invariants at EVERY level present (deep files included):
     composition list complete and in reference order, reversal symmetry
     (interior and pure palindromic, boundaries swap), single-row closed
     forms interior((m,)) = (2m+1)^2, boundary = 2m+1, pure = 1;
  D. --selftest: perturbs a value and requires the comparator to fire (RED).

Usage:
  python3 experiments/severance_w1_gate.py               # A+B+C on binary k<=6
  python3 experiments/severance_w1_gate.py FILE [FILE..] # + C on deep files
  python3 experiments/severance_w1_gate.py --selftest

Exit 0 = gate green; any mismatch raises and exits nonzero.
"""

import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cluster_weight_dp import (compositions, interior, boundary, pure,
                               KNOWN_WEIGHTS, TWO_ROW_INTERIOR)

BINARY = os.path.join("build", "severance_w1")


def parse(text):
    """-> dict composition -> (wi, wb, wt, wp), plus the order seen."""
    table, order = {}, []
    for line in text.strip().splitlines():
        vs, wi, wb, wt, wp = line.split("\t")
        v = tuple(int(x) for x in vs.split(","))
        if v in table:
            raise AssertionError(f"duplicate composition {v}")
        table[v] = tuple(int(x) for x in (wi, wb, wt, wp))
        order.append(v)
    return table, order


def levels_present(table):
    return sorted({sum(s - 1 for s in v) for v in table})


def check_structure(table, order, where):
    ks = levels_present(table)
    # completeness and reference enumeration order, per level
    want = [v for k in range(1, max(ks) + 1) for v in compositions(k)]
    assert order == want, f"{where}: composition order/completeness mismatch"
    for v, (wi, wb, wt, wp) in table.items():
        r = tuple(reversed(v))
        rwi, rwb, rwt, rwp = table[r]
        assert wi == rwi and wp == rwp and wb == rwt and wt == rwb, \
            f"{where}: reversal symmetry fails at {v}"
    for k in ks:
        m = k + 1
        assert table[(m,)] == ((2 * m + 1) ** 2, 2 * m + 1, 2 * m + 1, 1), \
            f"{where}: single-row closed form fails at ({m},)"
    print(f"  [C] {where}: structure OK, levels {ks}, {len(table)} compositions")


def check_known(table):
    for v, ref in KNOWN_WEIGHTS.items():
        assert table[v] == ref, f"[A] KNOWN_WEIGHTS mismatch at {v}: {table[v]} != {ref}"
    print(f"  [A] all {len(KNOWN_WEIGHTS)} banked compositions k<=5 match exactly")


def check_level6(table):
    v = (7,)
    ref = (interior(v), boundary(v), boundary(tuple(reversed(v))), pure(v))
    assert table[v] == ref, f"[B] level-6 DP holdout fails at {v}: {table[v]} != {ref}"
    for v in [(4, 4), (3, 5)]:
        wi, wb, wt, wp = table[v]
        assert wi == TWO_ROW_INTERIOR[v], \
            f"[B] banked interior mismatch at {v}: {wi} != {TWO_ROW_INTERIOR[v]}"
        ref = (boundary(v), boundary(tuple(reversed(v))), pure(v))
        assert (wb, wt, wp) == ref, f"[B] boundary/pure DP holdout fails at {v}"
    print("  [B] level-6 holdouts match: (7,) full DP; (4,4),(3,5) banked+DP")


def selftest():
    out = subprocess.run([BINARY, "5"], capture_output=True, text=True, check=True)
    table, order = parse(out.stdout)
    check_known(table)
    check_structure(table, order, "selftest-clean")
    v = (2, 3)
    table[v] = (table[v][0] + 1,) + table[v][1:]
    fired = 0
    for chk in (check_known, lambda t: check_structure(t, order, "selftest-dirty")):
        try:
            chk(table)
        except AssertionError:
            fired += 1
    assert fired == 2, "selftest: perturbation NOT caught — gate is broken"
    print("GATE SELFTEST GREEN: perturbed value caught by [A] and [C]")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    out = subprocess.run([BINARY, "6"], capture_output=True, text=True, check=True)
    table, order = parse(out.stdout)
    check_known(table)
    check_structure(table, order, f"{BINARY} 6")
    check_level6(table)
    for path in sys.argv[1:]:
        with open(path) as f:
            t, o = parse(f.read())
        check_structure(t, o, path)
        check_known(t)   # deep files contain the shallow levels too
        check_level6(t)
    print("GATE GREEN")


if __name__ == "__main__":
    main()
