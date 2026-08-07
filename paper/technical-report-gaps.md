# Results in the repo but not in `technical-report.tex`

2026-08-05. A review checklist for jasonp, written at his request. Ordered by
how much machinery is needed to follow the **statement** — not by importance.

**Comparison base:** `paper/technical-report.tex` as of 2026-08-05 — a(n) table,
T(n,H) table with the T(n,n) / T(n,n−1) / grand-form paragraphs, one-sided /
free / bilateral / asymmetric / A194596 tables, the hole table, a one-line
growth-rate remark, three Methods paragraphs, and an empty Reproducibility
section.

> This file proposes; it does not edit. `technical-report.tex` is jasonp's,
> read-only to Claude (memory: `paper-is-jasonps-words`).

---

## 1. Validation architecture (§Reproducibility is empty)

`HANDOFF.md`, `results/strip-engine.md`, `paper/polyplets-report.tex:485`.
Every production run re-derives all smaller terms; Redelmeier confirms to
n=22; an independent strip transfer-matrix engine sharing no enumeration code
confirms T(n,H) for H≤14 across all n≤40 (469 cells, 0 mismatches). Also the
tier system (computed twice / computed once / composed with pinned formulas).
Prose only, no math. Biggest hole in the report right now.

## 2. Fekete's lower bound: λ ≥ a(40)^(1/40) = 6.2208

`results/concatenation-upper-bound.md`. Supermultiplicativity, one sentence,
and it puts a floor under the "λ≈7.11" remark.

## 3. The growth-rate paragraph is a stub

`paper/polyplets-report.tex:200`, `results/series-analysis-da.md`. Ratio fit
with a confluent term Δ₁=½ gives λ≈7.111, θ≈−1.02, matching the universal 2-D
lattice-animal θ=−1; differential approximants independently give λ=7.110(1),
θ=−1.000(1). The report currently says "λ≈7.11, checkable from Table 1."

**Added 2026-08-06:** the ratio limit is not just an assumption — `a(n+1)/a(n)
→ λ` is a **theorem** for site animals on the king lattice (Madras 1999,
Thm 2.2 / Cor 3.6; his §3.1(f) spread-out lattice at M=1 with the sup norm
*is* the king lattice). One sentence, and it licenses the whole ratio-fit
paragraph instead of leaving it as a numerical hope.

## 4. Where the 25 in the T(n,n−1) derivation comes from: 25 = 16 + 9

`results/defect-gas.md`. The derivation in the report already computes 16
(domino joiner) + 9 (split joiner). The defect-gas note shows that "split" is
exactly the two-cell cluster weight and that the same bookkeeping generates
every P_k. One paragraph, and it makes the hand derivation the k=1 case of a
machine.

## 5. T(n,n−2) in closed form

`docs/proofs/T-n-nm2-and-general.md`. T(n,n−2) = ½(625n²−2459n+1134)·3^{n−7}
for n≥5, proved in the same style as the n−1 case (one row of 3, or two rows
of 2), brute-verified n=4..8 and against the triangle to n=20. Natural next
paragraph after the one already written.

## 6. The hole-fill bijection

`results/hole-fill-interior-cell-identity.md`. An n-cell polyplet with one
area-1 hole ↔ (hole-free (n+1)-cell polyplet, choice of interior cell). Exact,
provable, three sentences, and it sits directly under the existing hole table.

## 7. Maximum enclosed hole area: M(n) = ⌊((n−2)²+4)/8⌋

`results/maxhole-proof.md`, `results/maxhole.txt`. Exact by enumeration to
n=17 (M(17)=28 predicted and confirmed). The hole section counts holes but
never asks how big they get. **Revised again 2026-08-06, both sources read:**
it is the grid isoperimetric inequality, entire, and nothing here is a new
theorem. Sieben 2008 Thm 4.1 is the single-hole half verbatim (σ(e) =
⌊e²/8 − e/2 + 1⌋, no inversion); the same minimum for an *arbitrary finite
subset* of ℤ² — **Wang & Wang 1977**, ℤ² count explicit in Altshuler et al.
2006 — applied to the union of all the holes gives the all-holes half in three
lines. **Nothing is conditional any more** — but the statement must be printed
as a corollary, citing Wang–Wang first.
What is ours: the question (the hole literature counts holes, it doesn't
measure them) and the n ≤ 17 enumeration.

## 8. Component stratification C(n,c)

`results/component-stratification.md`. Polyplets split by number of
rook-connected components. C(n,1)=A001168 (fixed polyominoes) and C(n,n)=A001168
*also*, via a clean bijection — edge-isolated king animals are polyominoes on
the 45°-rotated sublattice. The distribution peaks near c≈n/2: the typical
polyplet is ~n/2 tiny pieces joined at corners, which is the mechanism behind
λ≈7.11 ≫ 4.06. Triangle not in OEIS.

## 9. Directed king animals as a closed-form anchor

`results/directed-king-animals.md`, `results/directed-cone-anchor.md`.
Bacher's directed king animals have GF ¼((1+t)/√(1−6t+t²)−1) and growth
exactly 3+2√2 ≈ 5.8284. Filtering the enumeration down to them reproduces
A047781 exactly — validation against a *formula* rather than a second
enumeration, available at any n.

## 10. Where a(n)'s mass sits

`results/nu-exponent.md`, `results/height-distribution-collapse.md`. mean_H/n
falls monotonically 0.745 (n=4) → 0.379 (n=40): growing but sublinear height,
neither fixed-small-H nor n/2. Plus a universal limit shape under rescaling.
State qualitatively — both notes were explicitly narrowed to drop the ν
exponent claim.

## 11. Hole-free polyplets grow strictly slower, exponentially so

`results/hole-free-growth-constant.md`. The hole-free fraction decays
exponentially, not polynomially: a hole is an entropic gain, not a rare
accident. Qualitative only — the note forbids quoting λ₀≈6.94.
**Revised 2026-08-06: this is a corollary of Madras 1999's pattern theorem**
(take the pattern "eight neighbours present, centre absent"; hole-free animals
contain zero translates, hence are exponentially rare), so print it as a cited
consequence, not a measurement. The measured ratio λ₀/λ ≈ 0.978 is the part
that is ours, and it is n ≤ 18 data.

## 12. A rigorous two-sided bracket: 6.543 ≤ λ ≤ 9.3153

`results/strip-mu-certificates.md`, `docs/proofs/polyplet-upper-bound.md`,
`paper/polyplets-report.tex:218`. Lower: certified strip ladder to H=17
(6,536,381 states), each rung a Collatz–Wielandt witness checkable in exact
integer arithmetic, anchored at μ₂=1+√2. Upper: a Bui-style finite-type
convolution certificate, x=2147/20000. No upper bound on λ appears in the
literature.

## 13. The diagonal law is a theorem, not a fit

`docs/proofs/diagonal-law.md`, `docs/proofs/grand-form.md`. §Results currently
says P_k was "fitted against computed values of T(n,H) and verified against
values from later rows." The shape is proved: degree ≤ k, the 3-power,
integrality of P_k, and the sharp onset n ≥ 2k+1 (failure at n=2k verified on
all banked data). Also worth checking: the report says P_k known for k≤19; the
pinned range on record is k≤18.

## 14. The diagonal-mirror triangle

`results/dmirror-diagonals.md`, `paper/polyplets-report.tex:648`. d(S,S+k) is
quasi-polynomial in S with period 2 and degree k per parity class. Still
conjectural — the last unproved law — which is itself worth saying in print.

## 15. The same law holds on every row-local lattice

`docs/proofs/universal-diagonal-law.md`, `results/hex-diagonal-law.md`.
T(H+k,H) = q_k(H)·b^H where b is the number of up-neighbours: b=1 square, b=2
hex, b=3 king. The report's 3^{n−1} is the b=3 instance of a theorem. Proved,
all three instances machine-checked.

## 16. The triangle mod 3

`results/ternary-spine.md`. The whole diagonal family's mod-3 behaviour is
governed by one algebraic series: the unique W ∈ 𝔽₃[[t]] with W(0)=1 solving
W³ = W² + t. 15/15 checks including a 342-cell mass check against the banked
triangle. Compact statement; the derivation is where it starts costing.

---

## Above the line

Deliberately cut as beyond the "follow the statement unaided" bar, in rough
order of remove:

- **Non-D-finiteness of the by-height GF** (`results/anisotropic-not-dfinite.md`,
  `paper/polyplets-report.tex:878`). Unconditional, and the strongest pure-math
  result in the repo. Worth putting in the paper as a *statement* if desired;
  the Rechnitzer haruspicy machinery behind it is not.
- **Smith normal form of the triangle is an all-3-powers group**
  (`results/triangle-snf.md`, `results/open-conjectures.md` C1).
- **The v₅ denominator law** (`results/v5-denominator-law.md`) — already demoted
  to a closed door on its own merits.
- **Convex polyplets by area** (`docs/proofs/convex-mirage.md`,
  `results/convex-anisotropic.md`) — q-series, empirically non-D-finite.
- **The differential-approximant methodology** behind item 3 (the numbers it
  produces are in scope; the method is not).
