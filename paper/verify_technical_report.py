#!/usr/bin/env python3
"""Verify every number in paper/technical-report.tex against banked results.

Read-only with respect to the .tex: parses its tables and checks them
against results/ns_a40/ (triangle + per-height columns), the staged
companion b-files, and results/holes_n18.txt. Run from anywhere:

    python3 paper/verify_technical_report.py

Exit 0 iff all checks pass. The a(40) abstract/table placeholder shows up
as a plain FAIL until the real value is typed in.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "technical-report.tex"

failures = []
checks = 0


def check(label, got, want):
    global checks
    checks += 1
    if got != want:
        failures.append(f"FAIL {label}: report has {got}, banked is {want}")


def load_pairs(path, cols=2):
    """Parse 'n value' (or 'n k value') integer lines, skipping comments."""
    out = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != cols or not parts[0].isdigit():
            continue
        key = int(parts[0]) if cols == 2 else (int(parts[0]), int(parts[1]))
        out[key] = int(parts[-1])
    return out


# ---------------- banked sources ----------------
banked_an = load_pairs(ROOT / "results/ns_a40/triangle.txt")
oeis_an = load_pairs(ROOT / "fixtures/b006770.txt")
for n in range(1, 19):
    check(f"banked a({n}) vs OEIS b-file", banked_an[n], oeis_an[n])

col = {}  # col[H][n] = T(n,H)
for f in (ROOT / "results/ns_a40/perheight").glob("h*.out"):
    col[int(f.stem[1:])] = load_pairs(f)
for n in range(1, 41):  # per-height columns must recompose the row sums
    check(f"sum_H T({n},H) = a({n})",
          sum(c.get(n, 0) for c in col.values()), banked_an[n])

onesided = load_pairs(ROOT / "results/b030233_upload.txt")
free = load_pairs(ROOT / "results/b030222_upload.txt")
bilateral = load_pairs(ROOT / "results/b030234_upload.txt")
asymmetric = load_pairs(ROOT / "results/b030235_upload.txt")
nonpoly = load_pairs(ROOT / "results/b194596_upload.txt")
holes = load_pairs(ROOT / "results/holes_n18.txt", cols=3)

# ---------------- parse the .tex tables ----------------
tex = TEX.read_text()


def table_body(label):
    m = re.search(r"\\midrule(.*?)\\bottomrule(.*?\\label\{%s\})?" % label,
                  tex, re.S)
    # locate by label instead: find the table env containing the label
    envs = re.findall(r"\\begin\{table\}(.*?)\\end\{table\}", tex, re.S)
    for env in envs:
        if f"\\label{{{label}}}" in env:
            return env
    sys.exit(f"table {label} not found")


def cells(row):
    out = []
    for c in row.split("&"):
        c = re.sub(r"\\(num|textbf|g)\b|[{}\\]|\s", "", c)
        out.append(int(c) if c.isdigit() else None)
    return out


def rows(env):
    body = env
    for chunk in re.findall(r"\\midrule(.*?)\\bottomrule", body, re.S):
        for row in chunk.split(r"\\"):
            row = row.strip().rstrip("\\")
            if row and "&" in row:
                yield cells(row)


# Table 1: a(n), two column-pairs per row
env = table_body("tab:an")
seen = 0
for r in rows(env):
    for i in range(0, len(r) - 1, 2):
        if r[i] is not None and r[i + 1] is not None:
            check(f"tab:an a({r[i]})", r[i + 1], banked_an[r[i]])
            seen += 1
if seen != 40:
    failures.append(f"FAIL tab:an: parsed {seen} of 40 terms")

# Table 2: T(n,H) for n<=12
env = table_body("tab:tnh")
for r in rows(env):
    n = r[0]
    for H, v in enumerate(r[1:], start=1):
        if v is not None:
            check(f"tab:tnh T({n},{H})", v, col[H][n])

# Table 3: one-sided / free
env = table_body("tab:onefree")
for r in rows(env):
    n = r[0]
    check(f"tab:onefree one-sided({n})", r[1], onesided[n])
    if len(r) > 2 and r[2] is not None:
        check(f"tab:onefree free({n})", r[2], free[n])

# Table 4: bilateral / asymmetric / non-polyominoes
env = table_body("tab:bisym")
for r in rows(env):
    n = r[0]
    check(f"tab:bisym bilateral({n})", r[1], bilateral[n])
    check(f"tab:bisym asymmetric({n})", r[2], asymmetric[n])
    check(f"tab:bisym nonpoly({n})", r[3], nonpoly[n])
    check(f"tab:bisym bilateral+asymmetric=free({n})",
          r[1] + r[2], free[n])

# Table 5: holes, two stacked tabulars (k=0..3, then k=4..10)
env = table_body("tab:holes")
blocks = re.findall(r"\$n\$\s*&\s*\$k=(\d+)\$(.*?)\\bottomrule", env, re.S)
for k0, body in blocks:
    k0 = int(k0)
    for row in body.split(r"\\"):
        row = row.strip()
        if not row or "&" not in row or "midrule" in row:
            continue
        r = cells(row)
        n = r[0]
        if n is None:  # remainder of the header row
            continue
        for j, v in enumerate(r[1:]):
            if v is not None:
                check(f"tab:holes ({n},k={k0 + j})", v, holes[(n, k0 + j)])

# Abstract: the inline a(40) display
m = re.search(r"a\(40\) = \\num\{(\d+)\}", tex)
if m:
    check("abstract a(40)", int(m.group(1)), banked_an[40])
else:
    failures.append("FAIL abstract: no 'a(40) = \\num{...}' found")

# ---------------- formula claims ----------------
for n in range(1, 41):
    check(f"T({n},{n}) = 3^(n-1)", col[n][n], 3 ** (n - 1))
for n in range(4, 41):
    check(f"T({n},{n}-1) = (25n-45)*3^(n-4)",
          col[n - 1][n], (25 * n - 45) * 3 ** (n - 4))

print(f"{checks} checks, {len(failures)} failures")
for f in failures:
    print(" ", f)
sys.exit(1 if failures else 0)
