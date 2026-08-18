#!/usr/bin/env python3
"""One per-cell provenance table for the a(40) triangle, and a gate over it.

Until now "what is confirmed, by which independent source, covering what share"
was spread over results/ns_a40/PROVENANCE.md, results/strip-engine.md,
results/subgroup-mod4.md, results/motley-h17.md and HANDOFF.md.  Five places
drift, and one of them already did: the strip-coverage-vs-holdout-mass
confusion recorded in strip-engine.md.

This script is the single source.  It assigns every one of the 820 cells its
set of corroborating sources from the rules the source notes state, and it
recomputes from the banked triangle every headline share those notes quote.

    python3 scripts/provenance_table.py            # write results/provenance-table.md
    python3 scripts/provenance_table.py --check    # gate: recompute and compare

The gate is fail-closed in both directions: a share that drifts fails, and so
does a cell with no source at all.  RED control included (--selftest).

Source rules, each traceable to the note that establishes it:

  B  brute force / Redelmeier          n <= 22          results/ns_a2*/,
                                                        b-file to n <= 20
  G  decorrelated fixed-height GFs     H <= 10          ns_a40/PROVENANCE.md
  R  small-height recurrences          H <= 4           strip-engine.md
  S  strip transfer matrix             H <= 14          strip-engine.md (469
                                                        cells, 0 mismatch)
  P  closed forms P_k, credited only where a real sweep also reached the cell
                                       k = n-H <= 18, n >= 2k+1, H <= 21
                                                        strip-engine.md
                                                        ("honest" rule)
  M  Motley/cutcount, rule-independent H <= MOTLEY_H    motley-h17.md
  F  P_k formula-derived cell, the formula itself holdout-validated elsewhere
                                       k <= 18, n >= 2k+1, H > 21
                                                        ns_a40/PROVENANCE.md
  C  subgroup mod-2/mod-4 congruence   every cell       subgroup-mod4.md
                                                        (congruence level only:
                                                        an error survives iff
                                                        it is 0 mod 4)

Three tiers, and the difference between them is the whole point of the table:
an EXACT source recomputed the cell by other means; F means the cell's value
came from a closed form whose other cells were checked against real sweeps, so
the formula is corroborated and this cell is not; C is a congruence, which
catches an error only if it is nonzero mod 4.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRIANGLE = ROOT / "results" / "triangle.txt"
OUT = ROOT / "results" / "provenance-table.md"

NMAX = 40
MOTLEY_H = 17          # Half Measure banked; Confetti (H=18) not yet landed

# Published figures this gate holds the table to.  Each is quoted in the note
# named beside it; if the table stops reproducing one, either the table or the
# note is wrong and the gate says so rather than letting them drift apart.
EXPECTED = {
    "cells_total": (820, "strip-engine.md"),
    "strip_cells": (469, "strip-engine.md"),
    "gf_cells": (355, "ns_a40/PROVENANCE.md"),
    "honest_pct": (72.2, "strip-engine.md"),
    "strip_alone_pct": (57.2, "strip-engine.md"),
    # No share-of-a(n) figures are computed or pinned here.  A cell is
    # corroborated or it is not; a wrong cell ruins a(n) whatever its size, so a
    # percentage of a(n) carries no decision and is not tracked.  Standing
    # ruling, restated 2026-08-18.
    # The cells that carry ONLY the mod-4 congruence -- no exact recount and no
    # closed form.  This is the project's real gap, so it is pinned: if it grows
    # something regressed, and when Confetti lands (Motley H=18) it must shrink,
    # which fires the gate and forces this number to be updated deliberately.
    "congruence_only_cells": (11, "this table; Motley at H<=%d" % 17),
}


def read_triangle():
    T = {}
    for line in TRIANGLE.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        n, h, v = line.split()
        T[(int(n), int(h))] = int(v)
    return T


def sources(n, h, motley_h=MOTLEY_H):
    """The corroborating sources for one cell, by the rules in the docstring."""
    out = set()
    if n <= 22:
        out.add("B")
    if h <= 10:
        out.add("G")
    if h <= 4:
        out.add("R")
    if h <= 14:
        out.add("S")
    k = n - h
    if k <= 18 and n >= 2 * k + 1:
        out.add("P" if h <= 21 else "F")
    if h <= motley_h:
        out.add("M")
    out.add("C")
    return out


def analyse(T, motley_h=MOTLEY_H):
    cells = sorted(T)
    a = {}
    for (n, h), v in T.items():
        a[n] = a.get(n, 0) + v
    src = {c: sources(*c, motley_h=motley_h) for c in cells}
    # C is congruence-level and F is formula-level; neither is an exact recount.
    exact = {c: (s - {"C", "F"}) for c, s in src.items()}
    stats = {
        "cells_total": len(cells),
        "strip_cells": sum(1 for c in cells if "S" in src[c]),
        "gf_cells": sum(1 for c in cells if "G" in src[c]),
        "no_exact_source": [c for c in cells if not exact[c]],
        "formula_only": [c for c in cells if not exact[c] and "F" in src[c]],
        "congruence_only": [c for c in cells
                            if not exact[c] and "F" not in src[c]],
    }
    # The published figure uses exactly R u S u (P n {H<=21}) -- it predates
    # both Motley and the fixed-height GF arm, so reproducing it means using
    # its own three sources and no more.
    honest_doc = [c for c in cells if exact[c] & {"R", "S", "P"}]
    stats["honest_pct"] = round(100 * len(honest_doc) / len(cells), 1)
    # What the table itself can now say, with every exact source counted.
    stats["exact_any_pct"] = round(
        100 * sum(1 for c in cells if exact[c]) / len(cells), 1)
    stats["congruence_only_mass"] = {}
    stats["strip_alone_pct"] = round(100 * stats["strip_cells"] / len(cells), 1)
    # Cells, not shares: per row, which cells have no exact recount.
    stats["unsourced_cells"] = {
        n: [h for h in range(1, n + 1) if not exact[(n, h)]]
        for n in range(1, NMAX + 1)
    }
    return a, src, exact, stats


def check(stats, verbose=True):
    bad = []
    for key, (want, note) in EXPECTED.items():
        if key == "congruence_only_cells":
            continue
        got = stats[key]
        if abs(got - want) > (0.05 if isinstance(want, float) else 0):
            bad.append("%s: table says %s, %s says %s" % (key, got, note, want))
        elif verbose:
            print("  ok  %-24s %-8s (%s)" % (key, got, note))
    got = len(stats["congruence_only"])
    want, note = EXPECTED["congruence_only_cells"]
    if got != want:
        bad.append("congruence_only_cells: table says %d, pinned at %d (%s) -- "
                   "cells %s" % (got, want, note, stats["congruence_only"]))
    elif verbose:
        print("  ok  %-24s %-8s (%s)" % ("congruence_only_cells", got, note))
    return bad


def write_table(T, a, src, exact, stats):
    L = []
    L.append("# Provenance, per cell — the single table\n")
    L.append("Generated by `scripts/provenance_table.py`; do not hand-edit. The\n"
             "gate `make gate-provenance` regenerates it and fails if any share\n"
             "drifts from the note that publishes it.\n")
    L.append("\n## Sources\n")
    L.append("| tag | source | rule | independence |\n|---|---|---|---|")
    L.append("| B | Redelmeier / brute force | n <= 22 | full |")
    L.append("| G | decorrelated fixed-height GFs | H <= 10 | full |")
    L.append("| R | small-height recurrences | H <= 4 | full |")
    L.append("| S | strip transfer matrix | H <= 14 | shares the union-find rule |")
    L.append("| P | closed forms P_k on really-swept cells | k <= 18, n >= 2k+1, H <= 21 | full where credited |")
    L.append("| M | Motley/cutcount | H <= %d | rule-independent |" % MOTLEY_H)
    L.append("| C | subgroup mod-2/mod-4 | every cell | congruence only |")
    L.append("\n## Coverage\n")
    L.append("- cells: **%d**; strip covers **%d**; fixed-height GFs **%d**"
             % (stats["cells_total"], stats["strip_cells"], stats["gf_cells"]))
    L.append("- honest cell coverage: **%.1f%%**; strip alone **%.1f%%**"
             % (stats["honest_pct"], stats["strip_alone_pct"]))
    L.append("- honest coverage counting **every** exact source now available "
             "(the published 72.2 percent predates Motley and the GF arm): "
             "**%.1f%%**" % stats["exact_any_pct"])
    L.append("- cells with no exact recount, whose value came from a closed "
             "form that is itself holdout-validated elsewhere: **%d**"
             % len(stats["formula_only"]))
    co = stats["congruence_only"]
    L.append("- cells carrying **only** the mod-4 congruence — no exact "
             "recount, no closed form: **%d**" % len(co))
    if co:
        L.append("")
        L.append("  " + ", ".join("T(%d,%d)" % c for c in sorted(co)))
        L.append("")
        L.append("  Each is a cell whose value has one source. That is the "
                 "statement; a(n) is no better than its worst cell, so how "
                 "large these cells are is not a fact about how much of a(n) "
                 "is trustworthy and is deliberately not reported.")
    L.append("\n## Row 40, cell by cell\n")
    L.append("| H | sources |\n|---|---|")
    for h in range(1, NMAX + 1):
        L.append("| %d | %s |" % (h, "".join(sorted(src[(NMAX, h)]))))
    L.append("\n## Cells with no exact second source, by row\n")
    L.append("| n | heights |\n|---|---|")
    for n in range(30, NMAX + 1):
        hs = stats["unsourced_cells"][n]
        L.append("| %d | %s |" % (n, ", ".join(map(str, hs)) if hs else "none"))
    L.append("")
    OUT.write_text("\n".join(L))


def selftest(T):
    """RED control: a corrupted rule must be caught."""
    a, src, exact, stats = analyse(T, motley_h=MOTLEY_H)
    bad = check(stats, verbose=False)
    if bad:
        print("SELFTEST FAILED: clean run should pass:", bad)
        return 1
    # RED: widening Motley's reach by one height must change the pinned count
    # of congruence-only cells.  (The old control doubled a cell's value and
    # watched a share move; shares are gone, and a cell count is the right
    # thing to guard anyway -- it is what the table asserts.)
    _, _, _, stats2 = analyse(T, motley_h=MOTLEY_H + 1)
    if not check(stats2, verbose=False):
        print("SELFTEST FAILED: Motley at H=%d left the pinned cell count "
              "unchanged" % (MOTLEY_H + 1))
        return 1
    print("selftest ok: a one-height change in Motley's reach moves the "
          "pinned count")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    T = read_triangle()
    if args.selftest:
        return selftest(T)
    a, src, exact, stats = analyse(T)
    if args.check:
        print("provenance table vs the notes that publish its figures:")
        bad = check(stats)
        if bad:
            print("\nprovenance gate RED:")
            for b in bad:
                print("  " + b)
            return 1
        print("provenance gate GREEN")
        return 0
    write_table(T, a, src, exact, stats)
    print("wrote %s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
