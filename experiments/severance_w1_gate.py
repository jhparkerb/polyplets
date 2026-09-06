"""Fail-closed gate for Severance W1 (docs/onset-defect-severance-plan.md (deleted) §3).

Checks the C++ cluster-weight port (build/severance_w1) against:
  A. the banked per-composition KNOWN_WEIGHTS, k <= 5, exactly;
  B. level-6 holdouts against BANKED Python-DP values (LEVEL6 below), the
     same practice TWO_ROW_INTERIOR already uses and for the same reason --
     the DP that produces them is minutes and produces the same numbers every
     time.  Re-derive with --emit-level6; --deep recomputes them live;
  C. structural invariants at EVERY level present (deep files included):
     composition list complete and in reference order, reversal symmetry
     (interior and pure palindromic, boundaries swap), single-row closed
     forms interior((m,)) = (2m+1)^2, boundary = 2m+1, pure = 1;
  D. --selftest: perturbs a value and requires the comparator to fire (RED).

Usage:
  python3 experiments/severance_w1_gate.py               # A+B+C on binary k<=6
  python3 experiments/severance_w1_gate.py FILE [FILE..] # + C on deep files
  python3 experiments/severance_w1_gate.py --selftest
  python3 experiments/severance_w1_gate.py --deep        # recompute B live
  python3 experiments/severance_w1_gate.py --emit-level6 # print LEVEL6 to re-bank

Exit 0 = gate green; any mismatch raises and exits nonzero.
"""

import subprocess
import sys
import os
from functools import lru_cache

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


# Level-6 holdout, DP-derived and BANKED.  Re-running the DP for these on every
# push cost 536 s of a 538 s gate suite (dalby, 2026-08-24) to reprint numbers
# that have not moved since they were derived.  Banking them keeps the holdout
# exactly as strong -- the C++ is still compared against a value the Python DP
# produced independently -- and moves only the recomputation, which --deep and
# gate-severance-w1-deep still do.  Same practice as TWO_ROW_INTERIOR.
#
# (7,)'s interior is not in TWO_ROW_INTERIOR because it is a ONE-row stack; the
# other two take their interior from that table and only their boundary/pure
# were being recomputed here.
# Derived by cluster_weight_dp on dalby, 2026-08-24, at 8e96d1f (the revision
# whose gate ran them live and green).  The two-row interiors agree with
# TWO_ROW_INTERIOR and (7,)'s row agrees with the single-row closed form
# ((2m+1)^2, 2m+1, 2m+1, 1) at m=7 -- both cross-checked below, every run.
LEVEL6 = {   # composition -> (interior, boundary_bottom, boundary_top, pure)
    (7,): (225, 15, 15, 1),
    (4, 4): (28559, 3012, 3012, 321),
    (3, 5): (19671, 2585, 1743, 231),
}


@lru_cache(maxsize=None)
def dp_ref(v):
    """The holdout reference for one composition, straight from the Python DP.

    Cached: --deep recomputes the bank, and with deep files on the command line
    check_level6 runs once per file -- without this the same minutes-long
    derivation runs again for each of them."""
    return (interior(v), boundary(v), boundary(tuple(reversed(v))), pure(v))


def emit_level6():
    """Re-derive the bank. Iterates LEVEL6 rather than a second copy of its
    keys, so a composition added to the bank is re-derived by definition."""
    print("LEVEL6 = {")
    for v in sorted(LEVEL6, key=lambda t: (len(t), t)):
        print(f"    {v}: {dp_ref(v)},")
    print("}")


def check_dp_alive():
    """Banked holdouts are only as good as the DP that produced them, so the DP
    itself runs on every gate -- on a level-3 composition, which is a second and
    exercises exactly the same count_stack/interior/boundary/pure call graph."""
    v = (3, 2)
    ref = dp_ref(v)
    assert ref == KNOWN_WEIGHTS[v], \
        f"[D] the Python DP no longer reproduces KNOWN_WEIGHTS at {v}: {ref}"
    print(f"  [D] Python DP live at {v} -> {ref}, matches KNOWN_WEIGHTS")


def check_level6(table, deep=False):
    bank = {v: dp_ref(v) for v in LEVEL6} if deep else LEVEL6
    assert bank, "[B] LEVEL6 is empty -- re-bank with --emit-level6 (fail-closed)"
    for v, ref in bank.items():
        assert table[v] == ref, \
            f"[B] level-6 holdout fails at {v}: {table[v]} != {ref}"
    # The two-row interiors are ALSO in TWO_ROW_INTERIOR; cross-check the two
    # banks against each other so a typo in either one is caught.
    for v in [v for v in bank if len(v) == 2]:
        assert bank[v][0] == TWO_ROW_INTERIOR[v], \
            f"[B] LEVEL6 and TWO_ROW_INTERIOR disagree at {v}"
    m = 7   # and the one-row entry against the single-row closed form
    assert bank[(m,)] == ((2 * m + 1) ** 2, 2 * m + 1, 2 * m + 1, 1), \
        f"[B] LEVEL6's ({m},) row disagrees with the single-row closed form"
    src = "recomputed live" if deep else "banked DP values"
    print(f"  [B] level-6 holdouts match ({src}): {sorted(bank)}")


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
    if "--emit-level6" in sys.argv:
        emit_level6()
        return
    deep = "--deep" in sys.argv
    out = subprocess.run([BINARY, "6"], capture_output=True, text=True, check=True)
    table, order = parse(out.stdout)
    check_known(table)
    check_structure(table, order, f"{BINARY} 6")
    check_level6(table, deep)
    check_dp_alive()
    for path in [a for a in sys.argv[1:] if not a.startswith("--")]:
        with open(path) as f:
            t, o = parse(f.read())
        check_structure(t, o, path)
        check_known(t)   # deep files contain the shallow levels too
        check_level6(t, deep)
    print("GATE GREEN")


if __name__ == "__main__":
    main()
