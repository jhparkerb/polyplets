#!/usr/bin/env python3
"""One per-cell provenance table for the a(40) triangle, and a gate over it.

Until now "what is confirmed, by which independent source, covering what share"
was spread over results/ns_a40/PROVENANCE.md, results/second-sources.md,
results/symmetry-classes.md, results/second-sources.md and docs/handoff.md.  Five places
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
  M  Motley/cutcount, rule-independent H <= MOTLEY_H    motley-h18.md
  F  P_k formula-derived cell, the formula itself holdout-validated elsewhere
                                       k <= 18, n >= 2k+1, H > 21
                                                        ns_a40/PROVENANCE.md
  U  Undertow tower pinned from Motley's own cells, agreeing with the incumbent
                                       H > MOTLEY_H, measured per cell
                                                        undertow.md,
                                                        experiments/undertow_ri.py
  C  subgroup mod-2/mod-4 congruence   every cell       subgroup-mod4.md
                                                        (congruence level only:
                                                        an error survives iff
                                                        it is 0 mod 4)

Four tiers, and the difference between them is the whole point of the table:
an EXACT source recomputed the cell by other means; F means the cell's value
came from a closed form whose other cells were checked against real sweeps, so
the formula is corroborated and this cell is not; U means the cell is
reproduced by the diagonal tower refitted to Motley's cells -- a formula-level
check that shares the depth tables D_j and the grand form with the wired route,
so it is not an exact recount either (AUDIT-2026-09-02 M2: "one tower strategy
pinned from Motley's data"); C is a congruence, which catches an error only if
it is nonzero mod 4.  U is derived by running the tower, not by a rule, and is
claimed only at the measured Motley reach.
"""
from __future__ import annotations

import argparse
import functools
import sys
from pathlib import Path

from cutcount_assembly_gate import assemble_rows

ROOT = Path(__file__).resolve().parent.parent
TRIANGLE = ROOT / "results" / "triangle.txt"
OUT = ROOT / "results" / "provenance-table.md"

NMAX = 40


def read_triangle(path=TRIANGLE):
    T = {}
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        n, h, v = line.split()
        T[(int(n), int(h))] = int(v)
    return T


def _reach_by_rowdir(nmax, root):
    """Motley's verified reach per banked row set: {dir: H}.

    `T(n,H) = C_H - 2C_{H-1} + C_{H-2}` needs all three cut-count rows at the
    SAME Nmax, so a height counts only when C_H, C_{H-1}, C_{H-2} all live in
    one directory, all reach n >= nmax, AND the assembled T(n,H) equals the
    banked triangle at every cell n <= nmax the triangle has.  Reach is
    contiguous from H = 1: the first height that fails caps it, so a corrupt
    banked row shrinks the reach and the pinned count below fires
    (AUDIT-2026-09-02 M3).
    """
    T = read_triangle(root / "results" / "triangle.txt")
    out = {}
    for d in sorted((root / "results" / "cutcount_b1").glob("rows*")):
        if not d.is_dir():
            continue
        C, M = assemble_rows(d)
        reach = 0
        for h in sorted(C):
            if any(max(C.get(h - i, {}), default=0) < nmax
                   for i in (0, 1, 2) if h - i >= 1):
                break
            if any(M.get((n, h)) != T[(n, h)]
                   for n in range(h, nmax + 1) if (n, h) in T):
                break
            reach = h
        out[d] = reach
    return out


def motley_reach(nmax=None, root=None):
    """The greatest height Motley covers, DERIVED from the banked row sets and
    VERIFIED against the triangle (see _reach_by_rowdir).  A hand-edited
    constant here went stale the day the Nmax-41 ladder landed, and the gate,
    which compares the published note against this generator, stayed green."""
    root = Path(root) if root else ROOT
    nmax = NMAX if nmax is None else nmax
    return max(_reach_by_rowdir(nmax, root).values(), default=0)


def motley_rowdir(nmax=None, root=None):
    """The banked row set that achieves motley_reach()."""
    root = Path(root) if root else ROOT
    nmax = NMAX if nmax is None else nmax
    by = _reach_by_rowdir(nmax, root)
    return max(by, key=by.get) if by else None


MOTLEY_H = motley_reach()
MOTLEY_DIR = motley_rowdir()


@functools.lru_cache(maxsize=None)
def tower_cells(motley_h=None, rowdir=None, jmax=4):
    """The cells above Motley's reach that the Motley-pinned Undertow tower
    reproduces EXACTLY -- experiments/undertow_ri.py, one tower per row with
    the row excluded from its own pinning set, levels 1..9 ab initio and the
    rest pinned from Motley cells at H <= motley_h.  Only cells that agree
    with the incumbent come back; a cell that disagrees makes undertow_ri red
    on its own, and this refuses too rather than tag around it."""
    motley_h = MOTLEY_H if motley_h is None else motley_h
    rowdir = MOTLEY_DIR if rowdir is None else rowdir
    if not motley_h or rowdir is None:
        return set()
    sys.path.insert(0, str(ROOT / "experiments"))
    from undertow_ri import cover
    cells = set()
    for r in cover(hmax=motley_h, jmax=jmax, rows=range(motley_h + 1, NMAX + 1),
                   rowdir=str(rowdir)):
        if r["wrong"]:
            raise SystemExit("provenance: the Motley-pinned tower disagrees with "
                             "the incumbent at %s" % r["wrong"])
        cells.update(r["agree"])
    return cells

# The closed-form band, in one place.  The production engine wires P_k for
# k <= PK_KMAX, the diagonal law's onset is sharp at n >= 2k+1
# (docs/proofs/diagonal-law.md), and a real sweep reached H <= SWEEP_H, which is
# what separates source P from source F above.  scripts/residual_cells.py
# derives its Q2 band and its closure figure from these same three, so a rung
# that moves one of them cannot leave the two generators disagreeing.
PK_KMAX = 18
SWEEP_H = 21

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
    # something regressed, and a rung that widens Motley's reach must shrink it,
    # which fires the gate and forces this number to be updated deliberately.
    # It did, twice.  Confetti landed 2026-08-19 and took it from 11 to 6,
    # retiring (36,18), (37,18), (38,18), (39,18) and (40,18).  Then Motley's
    # reach went to H<=19 -- MOTLEY_H above is derived from the banked row sets
    # now, not hand-set -- which retired the three H=19 cells (38,19), (39,19)
    # and (40,19).  What is left is (39,20), (40,20), (40,21): the three below.
    # This narration said "six" for a while after the pin already said 3; the
    # pin is the thing the gate checks, so the story was the half that drifted.
    "congruence_only_cells": (3, "results/cutcount_b1/rows41/README.md; "
                                 "Motley at H<=%d, derived from the banked "
                                 "row sets" % MOTLEY_H),
    # Every cell with no exact recount -- the formula-only ones and the three
    # above -- is reproduced by the Motley-pinned tower (tag U).  Pinned so that
    # a tower that stops reaching one of them, or a cell that stops agreeing,
    # fails here rather than dropping out of the table quietly.
    "tower_reproduced_unsourced": (192, "results/undertow.md; "
                                       "experiments/undertow_ri.py at H<=%d"
                                       % MOTLEY_H),
}


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
    if k <= PK_KMAX and n >= 2 * k + 1:
        out.add("P" if h <= SWEEP_H else "F")
    if h <= motley_h:
        out.add("M")
    if motley_h == MOTLEY_H and (n, h) in tower_cells():
        out.add("U")                 # measured at this reach only, not a rule
    out.add("C")
    return out


def analyse(T, motley_h=MOTLEY_H):
    cells = sorted(T)
    a = {}
    for (n, h), v in T.items():
        a[n] = a.get(n, 0) + v
    src = {c: sources(*c, motley_h=motley_h) for c in cells}
    # C is congruence-level, F and U are formula-level; none is an exact recount.
    exact = {c: (s - {"C", "F", "U"}) for c, s in src.items()}
    stats = {
        "cells_total": len(cells),
        "strip_cells": sum(1 for c in cells if "S" in src[c]),
        "gf_cells": sum(1 for c in cells if "G" in src[c]),
        "no_exact_source": [c for c in cells if not exact[c]],
        "formula_only": [c for c in cells if not exact[c] and "F" in src[c]],
        "congruence_only": [c for c in cells
                            if not exact[c] and "F" not in src[c]],
        "tower_reproduced_unsourced": [c for c in cells
                                       if not exact[c] and "U" in src[c]],
    }
    # The published figure uses exactly R u S u (P n {H<=21}) -- it predates
    # both Motley and the fixed-height GF arm, so reproducing it means using
    # its own three sources and no more.
    honest_doc = [c for c in cells if exact[c] & {"R", "S", "P"}]
    stats["honest_pct"] = round(100 * len(honest_doc) / len(cells), 1)
    # What the table itself can now say, with every exact source counted.
    stats["exact_any_pct"] = round(
        100 * sum(1 for c in cells if exact[c]) / len(cells), 1)
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
        if isinstance(got, list):
            got = len(got)
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
    L.append("| M | Motley/cutcount, the second enumerator: it counts by "
             "colouring and never decides connectivity, so it is what "
             "`results/confidence.md` calls the second program | H <= %d | "
             "rule-independent |" % MOTLEY_H)
    L.append("| U | Undertow tower refitted to Motley's cells -- the closed "
             "forms of `docs/proofs/diagonal-law.md` with their constants "
             "pinned from Motley's own cells, which `results/confidence.md` "
             "calls the formula tower | H > %d, rows %d-%d, "
             "measured per cell | formula-level: shares D_j and the grand form "
             "with P/F; agrees with the incumbent at every tagged cell |"
             % (MOTLEY_H, MOTLEY_H + 1, NMAX))
    L.append("| C | subgroup mod-2/mod-4 | every cell | congruence only |")
    L.append("\n## Coverage\n")
    L.append("- cells: **%d**; strip covers **%d**; fixed-height GFs **%d**"
             % (stats["cells_total"], stats["strip_cells"], stats["gf_cells"]))
    L.append("- entries with at least one exact second source: **%d of %d "
             "(%.1f%%)** -- counting every exact source now available"
             % (round(stats["exact_any_pct"] * stats["cells_total"] / 100.0),
                stats["cells_total"], stats["exact_any_pct"]))
    L.append("- the figures published before Motley and the GF arm, kept for "
             "comparison: **%.1f%%** with the sources of the day, **%.1f%%** "
             "from the strip engine alone"
             % (stats["honest_pct"], stats["strip_alone_pct"]))
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
        L.append("  Each is a cell whose value has one enumeration. That is the "
                 "statement; a(n) is no better than its worst cell, so how "
                 "large these cells are is not a fact about how much of a(n) "
                 "is trustworthy and is deliberately not reported.")
    tu = stats["tower_reproduced_unsourced"]
    L.append("- cells with no exact recount that the Undertow tower refitted to "
             "Motley's cells reproduces (tag U): **%d** of the %d, the %d "
             "formula-derived cells and the %d above included. A formula-level "
             "check sharing the depth tables with the wired route, not a second "
             "enumeration (AUDIT-2026-09-02 M2)."
             % (len(tu), len(stats["no_exact_source"]),
                len(stats["formula_only"]), len(co)))
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
    # RED 2: a corrupt banked row must SHRINK the derived reach, not be
    # credited for existing.  Stage a copy of results/ with one digit of
    # rows41/C19.out changed at n = 40 and re-derive.
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "results").mkdir()
        shutil.copy(TRIANGLE, root / "results" / "triangle.txt")
        shutil.copytree(ROOT / "results" / "cutcount_b1" / "rows",
                        root / "results" / "cutcount_b1" / "rows")
        shutil.copytree(ROOT / "results" / "cutcount_b1" / "rows41",
                        root / "results" / "cutcount_b1" / "rows41")
        p = root / "results" / "cutcount_b1" / "rows41" / "C19.out"
        lines = p.read_text().splitlines()
        n, v = lines[-2].split()                 # n = 40: a cell the triangle has
        lines[-2] = "%s %d" % (n, int(v) + 1)
        p.write_text("\n".join(lines) + "\n")
        got = motley_reach(root=root)
        if got >= MOTLEY_H:
            print("SELFTEST FAILED: a corrupted rows41/C19.out still credits "
                  "Motley with H=%d" % got)
            return 1
    # RED 3: a tower cell that stops agreeing must refuse, not drop out of U.
    # A canned record stands in for the 21 towers; the refusal path is the same.
    import undertow_ri
    real = undertow_ri.cover
    undertow_ri.cover = lambda **kw: [{"agree": [(40, 20)], "wrong": [(40, 21)]}]
    tower_cells.cache_clear()
    try:
        try:
            tower_cells()
        except SystemExit:
            pass
        else:
            print("SELFTEST FAILED: a disagreeing tower cell did not refuse")
            return 1
    finally:
        undertow_ri.cover = real
        tower_cells.cache_clear()
    print("selftest ok: a one-height change in Motley's reach moves the "
          "pinned count; a corrupt banked row shrinks the derived reach "
          "(%d -> %d); a disagreeing tower cell refuses" % (MOTLEY_H, got))
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
