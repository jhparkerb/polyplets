# a(23) — fixed polyplets (king-move animals), 2026-06-30

Two new terms of A006770 (fixed polyplets / king-move animals), computed by the
column-sweep transfer-matrix engine, split across two boxes:
- **ayr**: heights H=1..16
- **dalby**: heights H=17..23 (H=18 was the wall; finished 00:45, 19–23 injected by
  the proven k≤4 closed forms)

## The terms
```
a(22) = 47255332844367680      (new)
a(23) = 321749260511448732     (new)
```
Growth: a(23)/a(22) = 6.8087, a(22)/a(21) = 6.7953 (→ λ ≈ 6.77 from above, expected
for finite n). Full assembled sequence in `a_n.txt`; triangle T(n,H) in `triangle.txt`.

## Validation (this run, independent of certification)
- **a(20), a(21) reproduce the prior a(21) run BYTE-EXACT** —
  a(20)=1025573519362016, a(21)=6954084405510437. The new run independently
  re-derives every prior known value, and the full sequence matches A006770
  through a(21).
- **The k=5,6 closed-form diagonals match the swept high-H rows at scale**:
  diagonalCell(n,5)=T(n,n−5) and diagonalCell(n,6)=T(n,n−6) reproduce the
  dalby-swept H=18,17 rows exactly at n=21,22,23 (e.g. T(23,18)=619065902379384,
  T(23,17)=1821918690703296). This is the at-scale gate for the k≤6 injection
  (commit 066f0ba) — passed.
- **k=7 / P₇ is now PINNED** (the a(21) data was one point short). With n=15..23
  swept (9 points), P₇ is fully determined, leading coeff = 25⁷/7! (the defect-gas
  pattern), and reproduces the swept T(22,15)=1035856891052731 and
  T(23,16)=4492550651512074. Numerator (÷5040, ×3^(n−22)), degree 7→0:
  `6103515625, −119765625000, 812310625000, −2839739579250, 5194366339015,
  −1878923357430, −6841564107480, 7756630081200`.
  **NB:** these coefficients overflow int64 at every used n (6103515625·n⁷ > 9.2e18
  for n≥22), so wiring k=7 into `diagonalCell` needs a `big.Int` path — unlike
  k≤6, which stay in int64 through a25.

## Cross-ISA verify — COMPLETE, PASSED (2026-07-01)

ayr independently recomputed H17 and H18 (`ns_a23_verify`, x86-64, different
machine and ISA than the original dalby run) — the two most expensive swept
heights, the ones most likely to expose a transient/ISA-specific bug. Total wall
82,146s (≈22.8h). **Every value matches byte-exact**, n=17..23 on both heights,
e.g. T(23,17)=1821918690703296, T(23,18)=619065902379384 — identical to the
dalby-sourced `triangle.txt`. This is the independent certification a(23)'s
record values were waiting on.

## Pending
- **Certification** of the novel terms (mod-p shadow / independent reimpl) per
  the a23-readiness note — cross-ISA passing raises confidence beyond
  single-source but is not a substitute for an independent reimplementation.
- **OEIS**: extend the A006770 b-file with a(22), a(23) (jasonp's button).
