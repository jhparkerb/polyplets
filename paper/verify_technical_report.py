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
        # Strip any LaTeX control word.  The old pattern was
        # r"\\(num|textbf|g)\b" -- but \g is used brace-less as \g1234, and
        # \b never matches between "g" and "1", so every shaded cell survived
        # as "g1234", parsed to None, and was silently skipped (42 of the 78
        # tab:tnh cells).  A control word ends at the first non-letter, which
        # is exactly what (?![A-Za-z]) / a greedy [a-zA-Z]+ expresses.
        c = re.sub(r"\\[a-zA-Z]+|[{}\\]|\s", "", c)
        out.append(int(c) if c.isdigit() else None)
    return out


# Per-table expected cell counts.  rows() yields nothing at all if a table
# loses its \midrule or \bottomrule, and cells() yields None for anything it
# cannot parse; without these guards either failure mode is silent and the
# tool still prints a healthy-looking total.  Bump these deliberately when a
# table gains rows.
EXPECTED_CELLS = {
    "tab:an": 40,        # a(1)..a(40), two column-pairs per row
    "tab:tnh": 78,       # lower triangle T(n,H), n=1..12
    "tab:onefree": 32,   # 17 one-sided + 15 free (n=33,34 free not yet known)
    "tab:bisym": 60,     # 15 rows x (bilateral, asymmetric, nonpoly, sum)
    "tab:holes": 93,     # both stacked tabulars, k=0..10
}


def coverage(label, seen):
    want = EXPECTED_CELLS[label]
    if seen != want:
        failures.append(
            f"FAIL {label} coverage: {seen} cells checked, expected {want}")


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
coverage("tab:an", seen)

# Table 2: T(n,H) for n<=12
env = table_body("tab:tnh")
seen = 0
for r in rows(env):
    n = r[0]
    for H, v in enumerate(r[1:], start=1):
        if v is not None:
            check(f"tab:tnh T({n},{H})", v, col[H][n])
            seen += 1
coverage("tab:tnh", seen)

# Table 3: one-sided / free
env = table_body("tab:onefree")
seen = 0
for r in rows(env):
    n = r[0]
    check(f"tab:onefree one-sided({n})", r[1], onesided[n])
    seen += 1
    if len(r) > 2 and r[2] is not None:
        check(f"tab:onefree free({n})", r[2], free[n])
        seen += 1
coverage("tab:onefree", seen)

# Table 4: bilateral / asymmetric / non-polyominoes
env = table_body("tab:bisym")
seen = 0
for r in rows(env):
    n = r[0]
    check(f"tab:bisym bilateral({n})", r[1], bilateral[n])
    check(f"tab:bisym asymmetric({n})", r[2], asymmetric[n])
    check(f"tab:bisym nonpoly({n})", r[3], nonpoly[n])
    check(f"tab:bisym bilateral+asymmetric=free({n})",
          r[1] + r[2], free[n])
    seen += 4
coverage("tab:bisym", seen)

# Table 5: holes, two stacked tabulars (k=0..3, then k=4..10)
env = table_body("tab:holes")
blocks = re.findall(r"\$n\$\s*&\s*\$k=(\d+)\$(.*?)\\bottomrule", env, re.S)
seen = 0
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
                seen += 1
coverage("tab:holes", seen)

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

# ---------------- every in-onset diagonal cell vs the closed forms ----
# The report's "P_k explicitly known for k<=19 ... verified against values
# from later rows" claim, exercised on the WHOLE triangle: refit each P_k
# (k=1..18) from its two EARLIEST in-onset cells via the exponential/cumulant
# law (exact rationals), then demand that every other in-onset cell T(n,n-k)
# of the banked triangle match the closed form.  The two fit cells per k are
# skipped (they define the coefficients and cannot test them).
#
# This splits into two populations, both reported below:
#   * H <= 21 -- real-swept cells; these genuinely test the closed forms.
#   * H >= 22 -- cells the a(40) run *injected* from the wired P_k; matching
#     here is a self-consistency check of the refit-vs-wired coefficients,
#     not independent evidence.
# Before this was widened it only covered H in (20,21), 35 cells.
from fractions import Fraction as Fr

def pcell(n, k):  # P_k(n) = T(n,n-k) * 3^(1+3k-n), exact
    return Fr(col[n - k][n]) * Fr(3) ** (1 + 3 * k - n)

ab = {}  # k -> (a_k, b_k) cumulant constants

def qpart(n, k):  # [y^k] exp(sum_{j<k} (a_j+b_j n) y^j)
    c = [Fr(0)] * (k + 1)
    c[0] = Fr(1)
    for j in range(1, k):
        aj, bj = ab[j]
        cy = [Fr(0)] * (k + 1)
        cy[0] = Fr(1)
        term = Fr(1)
        for m in range(1, k // j + 1):
            term *= (aj + bj * n)
            term /= m
            if m * j <= k:
                cy[m * j] = term
        c = [sum(c[i] * cy[m - i] for i in range(m + 1))
             for m in range(k + 1)]
    return c[k]

for k in range(1, 19):
    n1, n2 = 2 * k + 1, 2 * k + 2
    v1, v2 = pcell(n1, k) - qpart(n1, k), pcell(n2, k) - qpart(n2, k)
    bk = v2 - v1
    ab[k] = (v1 - bk * n1, bk)

n_real, n_injected = 0, 0
for H in range(2, 41):
    for n in range(H + 1, 41):
        k = n - H
        if not (1 <= k <= 18) or n < 2 * k + 1:
            continue          # outside the onset n >= 2k+1: no closed form
        if n in (2 * k + 1, 2 * k + 2):
            continue          # the two fit cells; they define P_k
        ak, bk = ab[k]
        want = qpart(n, k) + ak + bk * n
        check(f"diagonal: T({n},{H}) matches refit P_{k}", pcell(n, k), want)
        if H <= 21:
            n_real += 1
        else:
            n_injected += 1
if (n_real, n_injected) != (171, 171):
    failures.append(f"FAIL diagonal coverage: {n_real} real-swept / "
                    f"{n_injected} injected cells, expected 171 / 171")

print(f"diagonal closed forms: {n_real} real-swept cells (independent) + "
      f"{n_injected} injected cells (self-consistency)")
print(f"{checks} checks, {len(failures)} failures")
for f in failures:
    print(" ", f)
sys.exit(1 if failures else 0)
