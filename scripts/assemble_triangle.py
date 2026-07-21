#!/usr/bin/env python3
"""Assemble the canonical T(n,H) triangle from results/ns_a36/perheight/hH.out.

Output: results/triangle.txt, one line per cell "n H T(n,H)", row-major
(n ascending, H ascending), 1 <= H <= n <= 36.

Fail-closed checks: row sums must equal a(n) from results/ns_a36/triangle.txt,
and T(n,n) must equal 3^(n-1).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results" / "ns_a36" / "perheight"
ROWSUMS = ROOT / "results" / "ns_a36" / "triangle.txt"
OUT = ROOT / "results" / "triangle.txt"
NMAX = 36


def read_column(path):
    col = {}
    for line in path.read_text().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, v = line.split()
        col[int(n)] = int(v)
    return col


def main():
    cols = {}
    for h in range(1, NMAX + 1):
        p = SRC / f"h{h}.out"
        if not p.exists():
            sys.exit(f"missing column file: {p}")
        cols[h] = read_column(p)

    a = read_column(ROWSUMS)

    lines = []
    for n in range(1, NMAX + 1):
        row = [cols[h].get(n, 0) for h in range(1, n + 1)]
        if sum(row) != a[n]:
            sys.exit(f"row-sum mismatch at n={n}: {sum(row)} != a(n)={a[n]}")
        if row[n - 1] != 3 ** (n - 1):
            sys.exit(f"top-diagonal mismatch at n={n}: T(n,n) != 3^(n-1)")
        for h in range(1, n + 1):
            lines.append(f"{n} {h} {row[h - 1]}")

    header = [
        "# T(n,H): fixed polyplets (king-connected animals) of size n and",
        "# bounding-box height exactly H, 1 <= H <= n <= 36.",
        "# Columns: n H T(n,H).  Row sums give A006770.",
        "# Assembled by scripts/assemble_triangle.py from",
        "# results/ns_a36/perheight/hH.out; provenance in results/ns_a36/PROVENANCE.md.",
        "# Checks enforced at assembly: sum_H T(n,H) = a(n) for all n;",
        "# T(n,n) = 3^(n-1) for all n.",
    ]
    OUT.write_text("\n".join(header + lines) + "\n")
    print(f"wrote {OUT}: {len(lines)} cells, n <= {NMAX}, all checks passed")


if __name__ == "__main__":
    main()
