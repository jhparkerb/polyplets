# External definition anchors: Mertens 1990 perimeter polynomials and OEIS A286139

2026-08-11, Teammate C of the second-source team (probes C1 and C2 of
`results/second-source-candidates-C.md`, banked as a standalone note per
team-lead request). Both probes compare banked king-lattice data against
numbers computed entirely outside this project's lineage. Both agree, and the
one disagreement found is provably the literature's misprint, not ours.

## Probe C2 — Mertens 1990 Table IVB vs banked site-perimeter polynomials

### What was compared, with provenance

**External side.** S. Mertens, "Lattice animals: a fast enumeration algorithm
and new perimeter polynomials", J. Stat. Phys. 58(5–6) (1990) 1095–1108, DOI
10.1007/BF01026565 — local copy `papers/mertens_1990_lattice_animals.pdf`.
Table IVB (journal p. 1104, PDF page 10): perimeter polynomials for "the
square lattice with next nearest neighbors" — the king lattice — at
s = 11, 12, 13, computed in 1990 by an independent Fortran implementation
(~30 h on an Apollo DN3500/4500). Extraction: `pdftotext -layout`, and the
disputed cell re-read visually from a 200-dpi render of the page. Earlier
terms (s ≤ 10) are attributed by Mertens to Peters, Stauffer, Hölters &
Loewenich, Z. Phys. B 34 (1979) 399, DOI 10.1007/BF01325205 (not held).

**Banked side.** `results/siteperim_square8_n14.txt` — rows (n, t, count):
fixed king animals of size n with king-(8-)adjacent site perimeter t,
n ≤ 14. Produced by `build/g2` (`cpp/g2_redelmeier.cpp`) in `square8
--siteperim` mode, job `g2-square8-N14`, gympie 2026-08-06, rev 69c4ccd-dirty,
1121.9 s wall (`results/siteperim_square8_n14.txt.obs.log`). The g2 header
(`cpp/g2_redelmeier.cpp:124`) pins the perimeter convention (distinct EMPTY
king-adjacent cells) and names Mertens Table IVB as the intended cross-source
— but no coefficient-level comparison had ever been recorded before this
probe; the reference existed as a convention note only.

### Result

Coefficient-by-coefficient over the three columns (31 + 34 + 37 = 102
nonzero coefficients):

- **s = 11**: all 31 coefficients (t = 18..48) identical.
- **s = 13**: all 37 coefficients (t = 20..56) identical.
- **s = 12**: 33 of 34 identical; **one disagreement at t = 39** —
  Mertens prints **26269734**, the banked value is **26169734**.

### Why the misprint is Mertens', shown rather than asserted

Summing each printed column and comparing with a(s) = A006770(s), which for
these s is multi-source (Redelmeier `build/g2`, the strip transfer matrix,
Tremblay–Vernay 2024, and the OEIS entry itself — see
`results/b006770_upload.txt` provenance):

| s | printed column sum | banked a(s) | difference |
|---|---|---|---|
| 11 | 39299408 | 39299408 | 0 |
| 12 | **257205146** | 257105146 | **+100000** |
| 13 | 1692931066 | 1692931066 | 0 |

The s = 12 column with the printed cell overshoots a(12) by exactly 100000 —
and 26269734 − 26169734 = 100000, so replacing that single cell with the
banked value restores Mertens' own row-sum identity (Σ_t g_{s,t} = a(s)),
which his other two columns satisfy exactly. A single misread hundred-
thousands digit ("2" for "1") in typesetting explains it; a counting error in
his program would have no reason to break exactly one cell by a round power
of ten while leaving the neighbouring 101 coefficients perfect. The printed
digit was confirmed by eye on the rendered page (not a text-extraction
artifact).

For the misprint to be ours instead, a(12) = 257105146 would have to be
wrong — against four independent sources, including the 2024 published
record and the OEIS b-file.

### What this buys, scoped honestly (style of `results/strip-engine.md` §Independence)

- **It is a definition-level anchor, not a T(n,H) cell check.** Mertens'
  table is graded by (size, site-perimeter); the banked triangle is graded by
  (size, height). Nothing here confirms any individual T(n,H) entry.
- **What it does confirm**: an enumeration written in 1990, by an independent
  author, in an independent implementation, under the percolation community's
  own definition of NNN-square (= king) connectivity and site perimeter,
  agrees with this repo's counts at the finest refinement available, for
  every n ≤ 13 (s ≤ 10 via the row sums a(n) matching the b-file lineage;
  s = 11..13 coefficient-level here). A shared in-house misconception about
  what king-connectivity means would have had to infect a 1990 Fortran
  program written for percolation series to survive this comparison.
- **The ceiling**: s = 13 is where the external perimeter-refined literature
  stops (the community moved to Monte Carlo). This anchor cannot be extended
  by citation; extending it means object-materialising enumeration, which the
  brief's a(22) fleet arithmetic prices out past n ≈ 22.

### Addendum 2026-08-11 (cross-critique wave): confirmed and strengthened by lane A

Lane A re-checked independently (`results/second-source-candidates-A.md`,
"Cross-critique of C" §3): (i) its own `pdftotext -layout` re-extraction
reproduces the column sums and the exact-100000 overshoot; (ii) **the
inconsistency is internal to Mertens's own paper** — Table I of the same
publication prints g₁₂ = 257105146, so the printed IVB cell is refuted
without appeal to any post-1990 source, closing the "all later sources are
one lineage" objection; (iii) a third-lineage recount (A's own C++
enumerator, `build/probe_king_perim12` — not g2, not Mertens) gives
(s=12, t=39) = 26169734 and reproduces all other 33 printed s = 12
coefficients and all totals n ≤ 12. The banked value now stands on three
independent computations against one printed digit. Whether to send Mertens
a two-line erratum note is jasonp's call.

## Probe C1 — OEIS A286139: connected induced subgraphs of the n×n king graph

**External side.** OEIS A286139, "Number of connected induced (non-null)
subgraphs of the n X n king graph": terms n ≤ 4 by Giovanni Resta (2017),
brute force — Mathematica `ConnectedGraphQ` over all 2^{n²} subsets of an
explicitly built king graph: no frontier, no union-find over a boundary, no
stranded-component logic anywhere in the mechanism. b-file to n = 16 by
Andrew Howroyd (method not stated; independent implementor outside this
problem's lineage). Companion A290764 (2×n king graph) has the closed form
a(n) = (3/4)(3^{n+1} − 2n − 3).

**Repo side.** `experiments/king_cis_probe.py` (throwaway probe, kept):
column DP over the n×n board carrying a king-connectivity partition of the
previous column — this repo's connectivity notion — tallying each connected
subset once at its rightmost occupied column.

**Result**: all nine terms computable inside the 15-minute probe box MATCH
exactly, n = 1..9; the n = 9 term is the 24-digit 463376724731585422732393,
aggregating clusters up to 81 cells in a 9×9 box (40.9 s, Python, gympie).

**Scope, honestly**: the probe itself carries a partition frontier, so the
probe is not rule-independent — the independence lives in the external
reference values, especially Resta's mechanism-free brute force at n ≤ 4 and
Howroyd's independent extension. Like C2 this anchors the *definition*, not
any banked T(n,H) cell: the aggregate would need joint (height, width)
bounding-box refinement at unbounded cluster size to be derived from the
triangle. Candidate C-2 of `results/second-source-candidates-C.md` is the
cheap extension of this comparison to Howroyd's full n = 16.

## Reproduce

    # C1: nine-term A286139 comparison (~50 s total)
    python3 experiments/king_cis_probe.py 9

    # C2: extract Table IVB and compare against banked siteperim data
    pdftotext -layout papers/mertens_1990_lattice_animals.pdf - \
      | sed -n '/Table IVB/,/Lattice Animals: A Fast Enum/p'
    # banked side: results/siteperim_square8_n14.txt (rows "n t count")
    # column sums: awk 'NF==4 && $1 ~ /^[0-9]+$/ {s11+=$2; s12+=$3; s13+=$4} END {print s11, s12, s13}'
    # visual check of the (s=12, t=39) cell: render PDF page 10 at 200 dpi
