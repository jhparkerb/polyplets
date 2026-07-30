#!/usr/bin/env python3
"""Bank the symmetric fixed-point counts out of the gitignored runs/ tree.

runs/ is in .gitignore, so runs/sym32{,.derive}, runs/sym33{,.derive} and
runs/sym34 -- weeks of symcount/symtm compute, and the only copies of the
n=20..34 symmetric columns anywhere -- exist on exactly one machine.  Every
paper/verify_claims.py check that consumes them therefore silently skips in
any other checkout (AUDIT-2026-07-30 P6).

This extracts them into the tracked results/sym_counts.txt, which
verify_claims.py reads as a fallback whenever runs/ is absent.  Re-run only
if the source columns are extended:

    python3 scripts/bank_sym_counts.py

Banked columns (key -> "col n value" lines):
  r90, r180, hmirror   runs/sym34/{r90,r180,hmirror}.out
  dmirror32            runs/sym32/dmirror.out       (n <= 32, direct)
  dmirror33            runs/sym33/dmirror.out       (n <= 33, T3 hybrid)
  dmirror_strip        runs/sym32/dmirror.S*.out    ("dmirror_strip S n v")
"""

import glob
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "sym_counts.txt")

COLUMNS = [
    ("r90", "runs/sym34/r90.out"),
    ("r180", "runs/sym34/r180.out"),
    ("hmirror", "runs/sym34/hmirror.out"),
    ("dmirror32", "runs/sym32/dmirror.out"),
    ("dmirror33", "runs/sym33/dmirror.out"),
]


def read_nv(path):
    d = {}
    for line in open(path):
        p = line.split()
        if len(p) == 2 and p[0].lstrip("-").isdigit():
            d[int(p[0])] = int(p[1])
    return d


def main():
    rev = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    lines = []
    summary = []
    for key, rel in COLUMNS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            sys.exit(f"missing source column: {rel} "
                     f"(this script only runs on the box holding runs/)")
        d = read_nv(path)
        summary.append(f"#   {key:14s} n={min(d)}..{max(d)} ({len(d)} rows) "
                       f"<- {rel}")
        lines += [f"{key} {n} {d[n]}" for n in sorted(d)]

    strips = sorted(glob.glob(os.path.join(ROOT, "runs/sym32/dmirror.S*.out")),
                    key=lambda f: int(re.search(r"S(\d+)\.out", f).group(1)))
    if not strips:
        sys.exit("missing runs/sym32/dmirror.S*.out strips")
    nstrip = 0
    for f in strips:
        S = int(re.search(r"S(\d+)\.out", f).group(1))
        d = read_nv(f)
        lines += [f"dmirror_strip {S} {n} {d[n]}" for n in sorted(d)]
        nstrip += len(d)
    summary.append(f"#   dmirror_strip  {len(strips)} strips, {nstrip} rows "
                   f"<- runs/sym32/dmirror.S*.out")

    header = [
        "# Symmetric fixed-point counts for the king-move (polyplet) lattice.",
        "# Columns: <key> <n> <value>, except dmirror_strip: "
        "dmirror_strip <S> <n> <value>.",
        "#",
        "# WHY THIS FILE EXISTS: runs/ is gitignored, so the source run",
        "# directories below live on one machine only and every check that",
        "# needs them silently skipped in any other checkout.  This is the",
        "# tracked fallback source (AUDIT-2026-07-30 P6).",
        "#",
        "# Source run directories (weeks of symcount_fast / symtm compute):",
    ] + summary + [
        "#",
        f"# Extracted {time.strftime('%Y-%m-%d')} by scripts/bank_sym_counts.py "
        f"at rev {rev}.",
        "# r90/r180/hmirror are the 90-degree, 180-degree and axis-parallel",
        "# mirror fixed-point counts; dmirror is the diagonal mirror.",
        "# dmirror32 is the direct n<=32 column; dmirror33 is the T3 hybrid",
        "# (direct strips + pinned closed forms) and prefix-matches it.",
        "# r90 legitimately has no rows for n = 2,3 (mod 4): no 90-degree-fixed",
        "# animals exist there, so an absent row means exactly 0.",
    ]
    with open(OUT, "w") as fh:
        fh.write("\n".join(header + lines) + "\n")
    print(f"wrote {OUT}: {len(lines)} rows")


if __name__ == "__main__":
    main()
