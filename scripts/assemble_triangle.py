#!/usr/bin/env python3
"""Assemble the canonical T(n,H) triangle from results/ns_a40/perheight/hH.out.

Output: results/triangle.txt, one line per cell "n H T(n,H)", row-major
(n ascending, H ascending), 1 <= H <= n <= 40.

Usage:
    scripts/assemble_triangle.py            # assemble and write
    scripts/assemble_triangle.py --check    # verify only, write nothing
                                            # (exit 1 if the tracked file
                                            #  differs from the assembly)

WHAT THE CHECKS ACTUALLY GUARD (AUDIT-2026-07-30 P12).  Read this before
quoting the row-sum check as evidence:

  * `sum_H T(n,H) = a(n)` is NOT independent corroboration.  a(n) comes from
    results/ns_a40/triangle.txt, which the engine's `combine` produced from
    these same per-height files.  What the check does catch is divergence
    between the two artifacts introduced AFTER banking -- a truncated,
    edited, or partially-copied column file, or an assembler bug.  What it
    cannot catch is an error already present in the per-height files when
    combine ran: both sides would be wrong the same way.
  * `T(n,n) = 3^(n-1)` and `T(n,n-1) = (25n-45)*3^(n-4)` (n >= 4) ARE
    independent: proven closed forms, not derived from this data.  They
    pin the two topmost diagonals of every row.
  * The per-column presence assert makes a missing row a hard error instead
    of a silent zero: read_column used to be consulted with .get(n, 0), so a
    column that simply lacked row n contributed 0 and relied entirely on the
    (non-independent) row sum to notice.
  * Duplicate `n` lines in a column file are refused rather than last-win.

Everything below is fail-closed; nothing is written unless every check
passes, and --check never writes at all.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results" / "ns_a40" / "perheight"
ROWSUMS = ROOT / "results" / "ns_a40" / "triangle.txt"
OUT = ROOT / "results" / "triangle.txt"
NMAX = 40


def read_column(path, height=None):
    """Parse an 'n value' file.  Refuses duplicate n; asserts row presence.

    height=None means "row-sum file": no presence rule.  Otherwise the file
    must carry every row n = height..NMAX, and any row n < height (the
    engine emits explicit zeros there) must be zero.
    """
    col = {}
    for lineno, line in enumerate(path.read_text().split("\n"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, v = line.split()
        n, v = int(n), int(v)
        if n in col:
            sys.exit(f"{path}:{lineno}: duplicate row n={n} "
                     f"({col[n]} then {v}); refusing last-win")
        col[n] = v
    if height is not None:
        missing = [n for n in range(height, NMAX + 1) if n not in col]
        if missing:
            sys.exit(f"{path}: missing rows n={missing} "
                     f"(a missing row would silently assemble as T=0)")
        nonzero = [n for n, v in col.items() if n < height and v != 0]
        if nonzero:
            sys.exit(f"{path}: nonzero T(n,{height}) below the diagonal "
                     f"at n={nonzero}")
    return col


def assemble():
    """-> (list of 'n H T' lines, header lines).  Fail-closed throughout."""
    cols = {}
    for h in range(1, NMAX + 1):
        p = SRC / f"h{h}.out"
        if not p.exists():
            sys.exit(f"missing column file: {p}")
        cols[h] = read_column(p, height=h)

    a = read_column(ROWSUMS)
    missing = [n for n in range(1, NMAX + 1) if n not in a]
    if missing:
        sys.exit(f"{ROWSUMS}: missing rows n={missing}")

    lines = []
    for n in range(1, NMAX + 1):
        row = [cols[h][n] for h in range(1, n + 1)]
        if sum(row) != a[n]:
            sys.exit(f"row-sum mismatch at n={n}: {sum(row)} != a(n)={a[n]}")
        if row[n - 1] != 3 ** (n - 1):
            sys.exit(f"top-diagonal mismatch at n={n}: T(n,n) != 3^(n-1)")
        if n >= 4 and row[n - 2] != (25 * n - 45) * 3 ** (n - 4):
            sys.exit(f"pole-diagonal mismatch at n={n}: T({n},{n - 1}) = "
                     f"{row[n - 2]} != (25n-45)*3^(n-4) = "
                     f"{(25 * n - 45) * 3 ** (n - 4)}")
        for h in range(1, n + 1):
            lines.append(f"{n} {h} {row[h - 1]}")

    header = [
        "# T(n,H): fixed polyplets (king-connected animals) of size n and",
        "# bounding-box height exactly H, 1 <= H <= n <= 40.",
        "# Columns: n H T(n,H).  Row sums give A006770.",
        "# Assembled by scripts/assemble_triangle.py from",
        "# results/ns_a40/perheight/hH.out; provenance in results/ns_a40/PROVENANCE.md.",
        "# Checks enforced at assembly: every column carries rows n=H..40 (no",
        "# defaulted zeros) and no duplicate n; sum_H T(n,H) = a(n) for all n",
        "# (agreement with the combine output, NOT independent corroboration);",
        "# T(n,n) = 3^(n-1) and T(n,n-1) = (25n-45)*3^(n-4) for all n >= 4",
        "# (proven closed forms, independent of this data).",
    ]
    return lines, header


def main():
    check_only = "--check" in sys.argv[1:]
    if [a for a in sys.argv[1:] if a != "--check"]:
        sys.exit("usage: assemble_triangle.py [--check]")

    lines, header = assemble()
    text = "\n".join(header + lines) + "\n"

    if check_only:
        if not OUT.exists():
            sys.exit(f"--check: {OUT} does not exist")
        if OUT.read_text() != text:
            sys.exit(f"--check: {OUT} differs from the assembly "
                     f"(re-run without --check to regenerate)")
        print(f"--check: {OUT} matches the assembly byte for byte "
              f"({len(lines)} cells, n <= {NMAX}, all checks passed)")
        return

    OUT.write_text(text)
    print(f"wrote {OUT}: {len(lines)} cells, n <= {NMAX}, all checks passed")


if __name__ == "__main__":
    main()
