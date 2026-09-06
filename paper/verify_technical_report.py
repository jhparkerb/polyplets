#!/usr/bin/env python3
"""Verify every number in paper/technical-report.tex against banked results.

Read-only with respect to the .tex: parses its tables and checks them
against results/ns_a40/ (triangle + per-height columns), the staged
companion b-files, and results/holes_n18.txt; then reads the scope numbers
out of the paper's prose sentences (Redelmeier to 22, Motley to H = 19,
P_k to 19, holes to 18 and 14, the 3k-th row, 25^k/k!, a(n)/4, a(n)/8,
the enclosure sizes) and checks each against the record it rests on, and
re-derives the T(n,n-1) derivation's intermediate counts by enumeration.
The sentence is the anchor: a sentence that goes missing is a failure.
Run from anywhere:

    python3 paper/verify_technical_report.py

Exit 0 iff all checks pass. The a(40) abstract/table placeholder shows up
as a plain FAIL until the real value is typed in.
"""
import os
import re
import sys
from fractions import Fraction as Fr
from functools import cache
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The .tex under test.  Overridable ONLY so tests/gate_p_paper_verifier.py can
# point this at a mutated COPY and prove the checks go red; the real file is
# jasonp's prose and is never written by anything in this tree.
TEX = Path(os.environ.get("VERIFY_TEX") or (ROOT / "paper" / "technical-report.tex"))

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

def pcell(n, k):  # P_k(n) = T(n,n-k) * 3^(1+3k-n), exact
    return Fr(col[n - k][n]) * Fr(3) ** (1 + 3 * k - n)

ab = {}  # k -> (a_k, b_k) cumulant constants

@cache
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

# ---------------- the prose: scope claims, anchored to their sentences --------
# Each check reads a number out of one sentence of the paper (the regex is the
# sentence) and compares it with the record that sentence rests on.  The
# RED-first gate perturbs every literal of two or more digits, so a scope
# number that drifts from its record goes red, and so does a sentence that
# disappears.

# Prose checks match against the text with every run of whitespace collapsed
# to one space, so re-wrapping a sentence in the .tex (which happens every
# edit) cannot turn a check red; the table parsers above keep the raw text.
prose = re.sub(r"\s+", " ", tex)


def said(label, pattern):
    m = re.search(pattern, prose, re.S)
    if not m:
        failures.append(f"FAIL {label}: sentence not found: /{pattern}/")
        return None
    return int(m.group(1))


# Abstract 51-52 and Methods 294-296: Redelmeier agrees with the transfer
# matrix through n = 22.  Record: the 2026-07-16 fleet run.
red = load_pairs(ROOT / "results/redelmeier_row22/combined.txt")
for n in sorted(red):
    check(f"Redelmeier row {n} == banked a({n})", red[n], banked_an[n])
check("abstract: Redelmeier agreement reach",
      said("abstract Redelmeier", r"for \$n\\le\{\}(\d+)\$, transfer matrix and Redelmeier"),
      max(red))
check("methods: Redelmeier reach",
      said("methods Redelmeier", r"only terms through \$n=(\d+)\$ could be confirmed"),
      max(red))

# Abstract 52-53: the colouring transfer matrix (Motley) confirms T(n,H) for
# H <= 19 at every n <= 40.  Record: results/cutcount_b1/rows41/C<H>.out holds
# C_H(n) = sum_{h<=H} (H-h+1) T(n,h); the triangle is its second difference.
rowdir = ROOT / "results/cutcount_b1/rows41"
motley_top = max(int(f.stem[1:]) for f in rowdir.glob("C*.out"))
C = {H: load_pairs(rowdir / f"C{H}.out") for H in range(1, motley_top + 1)}
C[0] = C[-1] = {}
nmax_said = said("abstract Motley n", r"for \$n\\le\{\}(\d+)\$, a transfer-matrix method that uses coloring")
check("abstract: Motley reach in n", nmax_said, 40)
motley_cells = 0
for H in range(1, motley_top + 1):
    for n in range(H, 41):
        t = C[H][n] - 2 * C[H - 1].get(n, 0) + C[H - 2].get(n, 0)
        check(f"Motley T({n},{H}) == banked", t, col[H][n])
        motley_cells += 1
check("abstract: Motley reach in H",
      said("abstract Motley H", r"confirms the \$T\(n,H\\le\{\}(\d+)\)\$ cells"), motley_top)
if motley_cells != 589:
    failures.append(f"FAIL Motley coverage: {motley_cells} cells, expected 589")

# Abstract 53-54: every a(n) passes the Burnside congruence.  Record: the
# subgroup-invariant counts I(H), n <= 40 (results/subgroup-mod4.md):
#   a(n) = I(C4) + I(D2ax) + I(D2diag) - 2 I(D4)   (mod 4)
I = {}
for line in (ROOT / "results/subgroup_counts.txt").read_text().splitlines():
    p = line.split()
    if len(p) == 3 and p[1].isdigit():
        I[(p[0], int(p[1]))] = int(p[2])
if not re.search(r"pass checks based on Burnsides? congruences", prose):
    failures.append("FAIL abstract: the Burnside-congruence sentence not found")
for n in range(1, 41):
    rhs = (I.get(("c4", n), 0) + I.get(("d2ax", n), 0)
           + I.get(("d2diag", n), 0) - 2 * I.get(("d4", n), 0))
    check(f"a({n}) mod 4 == subgroup census", banked_an[n] % 4, rhs % 4)

# Definitions 70-79 and Results 166: each symmetry class names its OEIS entry.
# The A-number in the sentence must be the one whose b-file that column was
# checked against above.
for label, pattern, fname in (
        ("fixed", r"\\item\[Fixed\].*?oeis\.org/A(\d+)", "b006770_upload.txt"),
        ("one-sided", r"\\item\[One-sided\].*?oeis\.org/A(\d+)", "b030233_upload.txt"),
        ("free", r"\\item\[Free\].*?oeis\.org/A(\d+)", "b030222_upload.txt"),
        ("bilateral", r"bilateral\}.*?oeis\.org/A(\d+)", "b030234_upload.txt"),
        ("asymmetric", r"asymmetric\}.*?oeis\.org/A(\d+)", "b030235_upload.txt"),
        ("non-polyomino", r"not polyominoes \(\\href\{https://oeis\.org/A(\d+)", "b194596_upload.txt")):
    check(f"OEIS id for {label}", said(f"OEIS id {label}", pattern), int(fname[1:7]))

# Every OEIS link shows the number it points at.
for url, shown in re.findall(r"\\href\{https://oeis\.org/(A\d+)\}\{(A\d+)\}", tex):
    check(f"href {url} shows its own number", shown, url)

# Definitions 82-83: a 1-cell hole needs a 4-cell polyplet; a domino hole or
# two 1-cell holes need 6.  Record: the hole table and the max-hole-area table.
maxhole = load_pairs(ROOT / "results/maxhole.txt")
n_one = said("enclosure 1", r"hole of size \$1\$ may be enclosed by a polyplet of size \$(\d+)\$")
n_two = said("enclosure 2", r"two size-\$1\$ holes may be enclosed by a polyplet of size \$(\d+)\$")
check("smallest polyplet with a hole", min(n for (n, k) in holes if k >= 1), n_one)
check("smallest polyplet with two holes", min(n for (n, k) in holes if k >= 2), n_two)
check("smallest polyplet enclosing a domino (max hole area 2)",
      min(n for n in maxhole if maxhole[n] >= 2), n_two)

# Table 1 caption: terms 1-18 match A006770.  The OEIS overlap is the 18 the
# loop at the top used; fixtures/b006770.txt lines 19-20 are ours.
check("caption: terms matching A006770",
      said("caption OEIS", r"Terms \$1\$--\$(\d+)\$ match A006770"), 18)

# Results 133-135: T(n,H) = P_k(n) 3^(3H-2n-1) with P_k integer-valued of
# degree k and leading coefficient 25^k/k!  (3H-2n-1 = n-3k-1 at H = n-k, the
# convention pcell() uses).  Integrality on every banked in-onset cell, and
# the leading coefficient of every refit P_k.
lead = said("leading coefficient", r"leading coefficient is exactly \$(\d+)\^k/k!\$")
for k in range(1, 20):
    for n in range(2 * k + 1, 41):
        if pcell(n, k).denominator != 1:
            failures.append(f"FAIL P_{k}({n}) is not an integer")
        checks += 1
for k in range(1, 19):
    ak, bk = ab[k]
    vals = [qpart(n, k) + ak + bk * n for n in range(2 * k + 1, 3 * k + 2)]
    for _ in range(k):                       # k-th finite difference
        vals = [b - a for a, b in zip(vals, vals[1:])]
    check(f"leading coefficient of P_{k} == {lead}^k/k!",
          vals[0] / factorial(k), Fr(lead ** k, factorial(k)))

# Results 135: P_k explicitly known for k <= 19.  Record: the wired table.
sweep_go = (ROOT / "orchestrator/sweep.go").read_text()
wired = int(re.search(r"const maxDiagKMax = (\d+)", sweep_go).group(1))
check("P_k wired to k <=", said("P_k known", r"explicitly known for \$k\\le(\d+)\$"), wired)

# Results 136-137: P_k can be fixed after the 3k-th row -- because the
# previous sentence supplies the leading coefficient, so the k in-onset rows
# 2k+1..3k pin the remaining degree-(k-1) part.  Check: interpolate from
# exactly those rows and demand every later banked in-onset cell.
m3k = said("3k-th row", r"after computing the \$(\d)k\$-th row")
for k in range(1, 14):                       # 3k <= 40 with a row to spare
    xs = list(range(2 * k + 1, m3k * k + 1))
    ys = [pcell(n, k) - Fr(lead ** k, factorial(k)) * n ** k for n in xs]

    def lagrange(x):
        tot = Fr(0)
        for i, xi in enumerate(xs):
            term = ys[i]
            for j, xj in enumerate(xs):
                if j != i:
                    term *= Fr(x - xj, xi - xj)
            tot += term
        return tot
    for n in range(m3k * k + 1, 41):
        check(f"P_{k} from rows 2k+1..{m3k}k predicts T({n},{n - k})",
              pcell(n, k), lagrange(n) + Fr(lead ** k, factorial(k)) * n ** k)

# Table 2 caption / Results 133: the shaded cells are exactly H > n/2.
env = table_body("tab:tnh")
for chunk in re.findall(r"\\midrule(.*?)\\bottomrule", env, re.S):
    for row in chunk.split(r"\\"):
        if "&" not in row:
            continue
        raw = row.split("&")
        n = int(re.sub(r"\D", "", raw[0]))
        for H, c in enumerate(raw[1:], start=1):
            if re.sub(r"\D", "", c):
                check(f"tab:tnh shading T({n},{H}) <=> H > n/2",
                      "\\g" in c, 2 * H > n)

# Results 164-168: non-polyominoes, and the a(n)/4 and a(n)/8 limits.
# Record: A000105 (free polyominoes) for the difference; the ratios from the
# tables themselves.
a000105 = load_pairs(ROOT / "fixtures/b000105.txt")
for n in sorted(nonpoly):
    if n in free and n >= 18:                 # the rows the table prints
        check(f"non-polyomino({n}) == free - A000105", nonpoly[n], free[n] - a000105[n])
        if a000105[n] * 1000 >= free[n]:
            failures.append(f"FAIL 'few polyplets are polyominoes' at n={n}")
        checks += 1
d1 = said("one-sided limit", r"one-sided count approaches\s+\$a\(n\)/(\d)\$")
d8 = said("free limit", r"free count approaches \$a\(n\)/(\d)\$")
for name, table, d in (("one-sided", onesided, d1), ("free", free, d8)):
    ns = sorted(n for n in table if 18 <= n <= 40)
    exc = [Fr(d * table[n], banked_an[n]) - 1 for n in ns]
    # The excess alternates by parity (the rotation-invariant terms do), so
    # "approaches as n grows" is tested two steps apart, not one.
    ok = all(e > 0 for e in exc) and all(a > b for a, b in zip(exc, exc[2:]))
    check(f"{name} count approaches a(n)/{d} from above (decreasing in n+2)", ok, True)
    check(f"{name}: {d} x count / a(n) - 1 < 1e-6 at n={ns[-1]}", exc[-1] < Fr(1, 10 ** 6), True)

# Holes 226-229: Euler-characteristic tracking in the transfer matrix to
# n = 18; Redelmeier flood-fill to n = 14 checked it.  Record: the two files,
# and their agreement on the overlap.
holes14 = load_pairs(ROOT / "results/holes_n14.txt", cols=3)
check("holes: transfer-matrix reach",
      said("holes TM reach", r"Euler characteristic through \$n=(\d+)\$"), max(n for n, k in holes))
check("holes: flood-fill reach",
      said("holes flood reach", r"flood-fill to verify counts\s+for \$n\\le(\d+)\$"), max(n for n, k in holes14))
for key in sorted(holes14):
    check(f"holes {key}: flood-fill == Euler tracking", holes14[key], holes.get(key))
for n in range(1, 19):
    check(f"hole row {n} sums to a({n})", sum(v for (m, k), v in holes.items() if m == n), banked_an[n])

# Table 1 as a whole: a(m+n) >= a(m) a(n), the supermultiplicativity behind any
# growth-rate statement read off the table (results/concatenation-upper-bound.md).
for m in range(1, 21):
    for n in range(m, 41 - m):
        if banked_an[m + n] < banked_an[m] * banked_an[n]:
            failures.append(f"FAIL supermultiplicativity at ({m},{n})")
        checks += 1

# Methods 307-345: the T(n,n-1) derivation, count by count.  Every fixed
# polyplet of size n <= 8 is generated (Redelmeier 1981) and tallied as it
# appears: those of height exactly n-1 have one doubled row, and the row's
# two cells are a domino (gap 1) or a split (gap 2), in an interior row or an
# end row.  The paper's coefficients are read from its own formulas.
NB8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
CENSUS_N = 8
census = {n: 0 for n in range(1, CENSUS_N + 1)}
tally = {n: {} for n in range(1, CENSUS_N + 1)}


def visit(animal):
    n = len(animal)
    census[n] += 1
    rows = {}
    for x, y in animal:
        rows.setdefault(y, []).append(x)
    if len(rows) == n - 2 and n >= 5:
        visit_nm2(n, rows)
    if len(rows) != n - 1:
        return
    (y2, xs), = [(y, xs) for y, xs in rows.items() if len(xs) == 2]
    kind = {1: "domino", 2: "split"}.get(abs(xs[0] - xs[1]), "gap>=3")
    pos = "end" if y2 in (min(rows), max(rows)) else "interior"
    tally[n][(kind, pos)] = tally[n].get((kind, pos), 0) + 1


# Height n-2 (docs/proofs/T-n-nm2-and-general.md): one row of three cells, or
# two rows of two.  A triple is classified by position (end / interior) and
# by its two internal gaps (each must be 1 or 2); two doubles by whether
# their rows are adjacent and how many of them sit at an end.  Two ADJACENT
# doubles bridge each other, so their gaps are unconstrained (0 and 3 with 1
# and 2 above it is connected); a separated double is bridged by a single
# cell and its gap is 1 or 2, like the n-1 case.
tally2 = {n: {} for n in range(1, CENSUS_N + 1)}


def visit_nm2(n, rows):
    lo, hi = min(rows), max(rows)
    fat = sorted((y, sorted(xs)) for y, xs in rows.items() if len(xs) >= 2)
    if len(fat) == 1:
        y, xs = fat[0]
        assert len(xs) == 3
        g = (xs[1] - xs[0], xs[2] - xs[1])
        kind = "triple" if max(g) <= 2 else "triple gap>=3"
        pos = "end" if y in (lo, hi) else "interior"
        key = (kind, pos)
    else:
        (ya, xa), (yb, xb) = fat
        assert len(xa) == len(xb) == 2
        ends = (ya in (lo, hi)) + (yb in (lo, hi))
        where = {0: "interior", 1: "one end", 2: "both ends"}[ends]
        if yb - ya == 1:
            key = ("adjacent", where)       # the pair bridges itself: any gaps
        elif max(xa[1] - xa[0], xb[1] - xb[0]) >= 3:
            key = ("separated gap>=3", "")  # a lone double is bridged by one cell
        else:
            key = ("separated", where)
    tally2[n][key] = tally2[n].get(key, 0) + 1


def redelmeier(animal, untried, tried):
    while untried:
        c = untried.pop()
        new = animal | {c}
        visit(new)
        if len(new) < CENSUS_N:
            fresh = [(c[0] + dx, c[1] + dy) for dx, dy in NB8
                     if (c[1] + dy > 0 or (c[1] + dy == 0 and c[0] + dx >= 0))
                     and (c[0] + dx, c[1] + dy) not in new
                     and (c[0] + dx, c[1] + dy) not in tried]
            redelmeier(new, untried + fresh, tried | set(fresh))
        tried = tried | {c}


redelmeier(frozenset(), [(0, 0)], set())
for n in range(1, CENSUS_N + 1):
    check(f"census: fixed polyplets of size {n}", census[n], banked_an[n])
c_dom = said("domino joiner", r"we have \$(\d+)\(n-3\)\\cdot\{\}3\^\{n-4\}\$ junction")
sp = re.search(r"giving \$\((\d)\\cdot\{\}(\d) \+ (\d)\\cdot\{\}(\d)\)\(n-3\)\\cdot\{\}3\^\{n-4\}\$",prose)
if not sp:
    failures.append("FAIL split-joiner sentence not found")
c_split = int(sp.group(1)) * int(sp.group(2)) + int(sp.group(3)) * int(sp.group(4)) if sp else None
c_int = said("interior joiner", r"give us \$(\d+)\(n-3\)\\cdot\{\}3\^\{n-4\}\$ options")
ends = re.search(r"giving \$(\d)\\cdot\{\}(\d)\\cdot\{\}3\^\{n-3\} = (\d+)\\cdot\{\}3\^\{n-4\}\$",prose)
if not ends:
    failures.append("FAIL end-joiner sentence not found")
tot = re.search(r"T\(n, n-1\) = (\d+)\(n-3\)\\cdot\{\}3\^\{n-4\} \+ (\d+)\\cdot\{\}3\^\{n-4\} = \((\d+)n - (\d+)\)\\cdot\{\}3\^\{n-4\}",prose)
if not tot:
    failures.append("FAIL T(n,n-1) display not found")
if sp and ends and tot:
    check("25 = 16 + 9 (interior joiner)", c_int, c_dom + c_split)
    check("end joiners: 2 x 5 x 3 = 30", int(ends.group(3)), int(ends.group(1)) * int(ends.group(2)) * 3)
    check("display: interior term", int(tot.group(1)), c_int)
    check("display: end term", int(tot.group(2)), int(ends.group(3)))
    check("display: 25n - 45", (int(tot.group(3)), int(tot.group(4))), (c_int, 3 * c_int - int(ends.group(3))))
    for n in range(4, CENSUS_N + 1):
        t, p3 = tally[n], 3 ** (n - 4)
        check(f"census n={n}: interior domino joiners", t.get(("domino", "interior"), 0), c_dom * (n - 3) * p3)
        check(f"census n={n}: interior split joiners", t.get(("split", "interior"), 0), c_split * (n - 3) * p3)
        check(f"census n={n}: end domino joiners (4 placements each end)", t.get(("domino", "end"), 0), 2 * 4 * 3 * p3)
        check(f"census n={n}: end split joiners (1 placement each end)", t.get(("split", "end"), 0), 2 * 1 * 3 * p3)
        check(f"census n={n}: a gap of three or more cannot be spanned", sum(v for (kind, _), v in t.items() if kind == "gap>=3"), 0)
        check(f"census n={n}: T({n},{n - 1}) by enumeration", sum(t.values()), col[n - 1][n])


# T(n,n-2) = (625n^2 - 2459n + 1134)/2 * 3^(n-7), n >= 5 (jasonp's 2026-09-05
# decision C5 in paper/technical-report-gaps.md; docs/proofs/T-n-nm2-and-general.md).
# The closed form on every banked cell, and each of its seven pieces against
# the enumeration for n = 5..8.  A triple has interior weight 49 (tromino 25,
# split-and-domino 11 each way, double split 2) and end weight 7; a doubled
# row keeps its 25 / 5 from the n-1 case; two adjacent doubled rows form one
# compound gadget of weight 339 interior, 66 at an end.
def t_nm2(n):
    num = 625 * n * n - 2459 * n + 1134
    assert num % 2 == 0
    return num // 2 * 3 ** (n - 7) if n >= 7 else Fr(num, 2) / 3 ** (7 - n)

for n in range(5, 41):
    check(f"T({n},{n - 2}) == (625n^2-2459n+1134)/2 * 3^(n-7)", Fr(col[n - 2][n]), Fr(t_nm2(n)))
for n in range(3, 41):
    check(f"T({n},{n - 1}) == (25n-45) 3^(n-4)", Fr(col[n - 1][n]), Fr(25 * n - 45) * Fr(3) ** (n - 4))
for n in range(5, CENSUS_N + 1):
    t = tally2[n]
    p = lambda e: Fr(3) ** e
    check(f"census n={n}: interior triples, 49 per position", t.get(("triple", "interior"), 0), 49 * (n - 4) * p(n - 5))
    check(f"census n={n}: end triples, 7 per end", t.get(("triple", "end"), 0), 14 * p(n - 4))
    check(f"census n={n}: two separated doubles, both interior (25*25)", t.get(("separated", "interior"), 0), Fr(625 * (n - 5) * (n - 6), 2) * p(n - 7))
    check(f"census n={n}: two separated doubles, one at an end (25*5)", t.get(("separated", "one end"), 0), 250 * (n - 5) * p(n - 6))
    check(f"census n={n}: two separated doubles, both ends (5*5)", t.get(("separated", "both ends"), 0), 25 * p(n - 5))
    check(f"census n={n}: adjacent doubles interior (339)", t.get(("adjacent", "interior"), 0), 339 * (n - 5) * p(n - 6))
    check(f"census n={n}: adjacent doubles at an end (66)", t.get(("adjacent", "one end"), 0), 132 * p(n - 5))
    check(f"census n={n}: no gap of three in a triple or a separated double", sum(v for (k, _), v in t.items() if "gap" in k), 0)
    check(f"census n={n}: T({n},{n - 2}) by enumeration", sum(t.values()), col[n - 2][n])

# ---------------- the L draft's scope numbers ----------------------------
# paper/technical-report-draft.tex (category L, 2026-09-05) states the same
# record in its own sentences.  Every number it puts in prose is read here and
# compared with the record, so that when jasonp strikes paragraphs from it
# what remains stays right.  Skipped silently if the draft is gone.
DRAFT = ROOT / "paper" / "technical-report-draft.tex"
if DRAFT.exists():
    dprose = re.sub(r"\s+", " ", DRAFT.read_text())

    def dsaid(label, pattern, conv=int):
        m = re.search(pattern, dprose)
        if not m:
            failures.append(f"FAIL draft {label}: sentence not found: /{pattern}/")
            return None
        return tuple(conv(g) for g in m.groups()) if len(m.groups()) > 1 else conv(m.group(1))

    a41_dir = ROOT / "results" / "a41"
    a41h = {int(f.stem[1:]): load_pairs(f) for f in a41_dir.glob("h*.out")}
    check("draft: a(41) value", dsaid("a(41)", r"a\(41\) = \\num\{(\d+)\}"),
          393811462683918679824582849262105)
    check("draft abstract: A006770 reach", dsaid("A006770 reach", r"\\oeis\{A006770\} to \$n = (\d+)\$"), max(banked_an))
    check("draft abstract: A030233 reach", dsaid("A030233 reach", r"\\oeis\{A030233\} to \$n = (\d+)\$"), max(onesided))
    r = dsaid("free-class reach", r"\\oeis\{A194596\} to \$n = (\d+)\$")
    check("draft abstract: A030222/A030234/A030235/A194596 reach", (r, r, r, r),
          (max(free), max(bilateral), max(asymmetric), max(nonpoly)))
    check("draft: swept heights of a(41) are 1..20", sorted(a41h), list(range(1, 21)))
    check("draft: a(41) assembled from heights 1..20",
          dsaid("a(41) heights", r"assembled from an enumeration of heights \$1\$--\$(\d+)\$"), max(a41h))
    for H, rows_ in sorted(a41h.items()):
        for n in range(H, 41):
            check(f"draft: a(41) sweep T({n},{H}) == banked", rows_.get(n, 0), col[H][n])
    check("draft: regression cells of the a(41) sweep",
          dsaid("regression", r"reproduces the stored triangle at every one of the \$(\d+)\$ entries"),
          sum(41 - H for H in a41h))
    check("draft: T(41,20) swept equals what the text quotes",
          dsaid("T(41,20)", r"T\(41,20\) = \\num\{(\d+)\}"), a41h[20][41])
    for H in range(1, motley_top + 1):
        t = C[H][41] - 2 * C[H - 1].get(41, 0) + C[H - 2].get(41, 0)
        check(f"draft: Motley T(41,{H}) == a(41) sweep", t, a41h[H][41])
    check("draft: Motley cells at n<=40 and the 19 at n=41",
          dsaid("Motley", r"on all \$(\d+)\$ entries with \$n \\le 40\$ and \$H \\le 19\$ and on the \$(\d+)\$ entries of row \$41\$ it reaches"),
          (motley_cells, motley_top))
    check("draft: Motley reach in H", dsaid("Motley H", r"run to height \$(\d+)\$ at the size row \$41\$ needs"), motley_top)
    check("draft: strip cells H<=14", dsaid("strip", r"agrees on all \$(\d+)\$ entries with \$H \\le 14\$"), sum(41 - H for H in range(1, 15)))
    check("draft: refit reproduces the other real-swept cells",
          dsaid("171", r"reproduces all \$(\d+)\$ other enumerated entries with \$H > n/2\$"), n_real)
    check("draft: 171 in the results paragraph",
          dsaid("171b", r"later enumerated entry on that diagonal, \$(\d+)\$ entries in all"), n_real)
    check("draft: P_k wired to", dsaid("wired", r"computes the triangle carries \$P_k\$ for \$k \\le (\d+)\$"), wired)
    for k, n, H in re.findall(r"\$P_\{(\d+)\}\$ at \$T\((\d+),(\d+)\)\$", dprose):
        k, n, H = int(k), int(n), int(H)
        check(f"draft: holdout P_{k} at T({n},{H}) is on its diagonal, in onset, not a fit cell",
              (n - H == k, n >= 2 * k + 1, n not in (2 * k + 1, 2 * k + 2), H <= 21), (True, True, True, True))
    cov = dsaid("coverage", r"Over the \$(\d+)\$ entries of the \$n \\le 40\$ triangle, \$(\d+)\$ are enumerated by at least one second program, \$(\d+)\$ are formula entries above height \$21\$, and three")
    ptab = (ROOT / "results" / "provenance-table.md").read_text()
    if cov:
        check("draft: 820 cells", cov[0], 40 * 41 // 2)
        check("draft: 189 formula-only cells (provenance table)", cov[2],
              int(re.search(r"holdout-validated elsewhere: \*\*(\d+)\*\*", ptab).group(1)))
        check("draft: 628 + 189 + 3 = 820", cov[1] + cov[2] + 3, cov[0])
        check("draft: 192 = 189 + 3 (provenance table)",
              int(re.search(r"tag U\): \*\*(\d+)\*\* of the", ptab).group(1)), cov[2] + 3)
    check("draft: Redelmeier reach", dsaid("Redelmeier", r"confirm the transfer matrix's counts up to \$n = (\d+)\$"), max(red))
    check("draft: Redelmeier cells agree everywhere", dsaid("Redelmeier rows", r"Every entry of every row \$n \\le (\d+)\$ agrees between Redelmeier"), max(red))
    check("draft: a(40)^(1/40)", dsaid("fekete", r"\\lambda \\ge a\(40\)\^\{1/40\} = (\d+\.\d+)", float),
          round(banked_an[40] ** (1 / 40), 4))
    check("draft: a(40)/a(39)", dsaid("ratio", r"a\(40\)/a\(39\) = (\d+\.\d+)", float),
          round(banked_an[40] / banked_an[39], 4))
    n32 = dsaid("limits", r"At \$n = (\d+)\$ the one-sided count exceeds \$a\(n\)/4\$ and the free count \$a\(n\)/8\$ by less than one part in a million")
    if n32:
        e4 = Fr(4 * onesided[n32], banked_an[n32]) - 1
        e8 = Fr(8 * free[n32], banked_an[n32]) - 1
        check(f"draft: one-sided excess at n={n32} in (0, 1e-6)", 0 < e4 < Fr(1, 10 ** 6), True)
        check(f"draft: free excess at n={n32} in (0, 1e-6)", 0 < e8 < Fr(1, 10 ** 6), True)
    check("draft: T(n,n-1) display", dsaid("nm1", r"T\(n,n-1\) = (\d+)\(n-3\)\\,3\^\{\\,n-4\} \+ (\d+) \\cdot 3\^\{\\,n-4\} = \((\d+)n - (\d+)\)\\,3\^\{\\,n-4\}"), (25, 30, 25, 45))
    check("draft: T(n,n-1) cells checked", dsaid("nm1 cells", r"the formula holds on all \$(\d+)\$ computed entries \$3 \\le n \\le 40\$"), 38)

print(f"{checks} checks, {len(failures)} failures")
for f in failures:
    print(" ", f)
sys.exit(1 if failures else 0)
