# `technical-report.tex` — open items

The report is the author's prose and is not edited by the machine; this is
the list of what it does not yet say, for him to accept, reject or reword.
`paper/verify_technical_report.py` reads every number out of the current
text, and `tests/gate_p_paper_verifier.py` checks that it does.

## Two sentences that reach further than the record

- "Fitted against computed values and verified against values from later
  rows" is true for k ≤ 18. P_19's diagonal has two in-onset enumerated
  cells, T(39,20) and T(40,21), both of which fit it, and no later row
  exists; the re-derivation from below-onset cells is a consistency check
  on those two values, not a holdout.
- "λ ≈ 7.11, checkable from Table 1": the table gives a(40)^(1/40) = 6.2208
  and a(40)/a(39) = 6.9352; 7.11 is an extrapolation of the ratios
  (`results/growth-constant.md`). Cite or drop.

Also: "fixed after computing the 3k-th row" is correct because the previous
sentence supplies the leading coefficient 25^k/k!; separated, it reads off
by one.

## Sections that do not exist

- **Reproducibility.** Material: `results/confidence.md`,
  `results/provenance-table.md`, the README's reproduce section.
- **The engine chapter.** Methods has three paragraphs; `docs/engine-record.md`
  has the components, which kernel produced which term, and the per-term
  costs.
- **Bibliography.** Zero `\cite`; `technical-report.bib` exists. Redelmeier,
  Klarner–Rivest, Jensen, Barequet–Ben-Shachar, Bacher, Madras, the OEIS
  entries.
- **External anchors**, as a subsection of validation: a(1)–a(18) against
  the OEIS, Bender's and Klarner–Rivest's constants, Richard's limit law, the
  Fortuin–Kasteleyn identity behind the coloring recount
  (`docs/external-anchors.md`).
- **a(41)**, in with an asterisk. What the asterisk can carry: heights 1–19
  enumerated by two programs that agree on all 19 cells; height 20
  enumerated once and equal to the formula that predicted it; heights 21–41
  from the closed forms (`results/a41/PROVENANCE.md`,
  `results/confidence.md`).

## Results in the repository and not in the paper

Open, in rough order of how much machinery the statement needs:

- Fekete's lower bound λ ≥ a(40)^(1/40) = 6.2208; one sentence
  (`results/growth-constant.md`).
- The growth-rate paragraph: ratio fits and differential approximants give
  λ ≈ 7.110(1), θ ≈ −1; a(n+1)/a(n) → λ is a theorem for king-lattice site
  animals (Madras 1999, Thm 2.2). Decided: cite or drop.
- Where the 25 in the T(n,n−1) derivation comes from: 16 (domino joiner)
  + 9 (split joiner) (`results/diagonal-formula.md`).
- T(n,n−2) = ½(625n²−2459n+1134)·3^(n−7), n ≥ 5, decided in; the author
  writes it in the T(n,n−1) style from `docs/proofs/T-n-nm2-and-general.md`
  §1. The verifier already checks the closed form on all 36 enumerated cells
  and a census of the cases at n = 5..8.
- Component stratification C(n,c): C(n,1) = C(n,n) = A001168
  (`results/subclasses.md`).
- Directed polyplets (Bacher) as a closed-form check: filtering the
  enumeration reproduces A047781 (`results/subclasses.md`).
- Height of a typical polyplet: mean H/n falls from 0.745 at n = 4 to 0.379
  at n = 40; qualitative only (`results/growth-constant.md`).
- The bracket 6.543 ≤ λ ≤ 9.3154, both ends exact-arithmetic certificates
  (`results/growth-constant.md`, `docs/proofs/polyplet-upper-bound.md`).
- The diagonal formula is proved, not fitted: the paper says "fitted"
  (`docs/proofs/diagonal-law.md`, `docs/proofs/product-form.md`). The author
  will fix the wording by asking questions, not by taking wording.
- The diagonal-mirror triangle: d(S,S+k) quasi-polynomial in S, period 2,
  conjectural (`results/symmetry-classes.md`).
- The same formula on every row-local lattice, b = 1, 2, 3 for square, hex,
  king (`docs/proofs/universal-diagonal-law.md`).
- The triangle mod 3: one algebraic series W³ = W² + t governs the diagonal
  family (`results/arithmetic-structure.md`).

Deferred by the author: the hole-fill bijection, the maximum hole area
M(n) = ⌊((n−2)²+4)/8⌋ (the grid isoperimetric inequality, Wang & Wang 1977;
print as a corollary), hole-free polyplets exponentially rare (a corollary
of Madras 1999's pattern theorem), and the maximum number of holes
n − ⌈2√n⌉ + 1 (A248333). The hole table stays because three staged OEIS
sequences rest on it.

Deliberately out, as beyond "follow the statement unaided": the
non-D-finiteness of the by-height generating function (a statement at most),
the Smith normal form of the triangle, the v₅ denominator pattern, convex
polyplets by area, and the differential-approximant method itself.

## Every result the paper must state or prove, in dependency order

Line numbers are into `technical-report.tex` as of 2026-09-04. "Needs" names
the earlier items each one rests on. Onset sharpness (failure at n = 2k) is
not asserted by the text and is not required.

### Lattice facts

1. **Polyominoes are polyplets.** Rook adjacency implies king adjacency.
   Implicit; used by the A194596 column and by "few polyplets are
   polyominoes" (line 165). Needs nothing.
2. **Row occupancy and the walk-row cut.** A connected animal occupies every
   row of its bounding box; king adjacency changes the row by at most one, so
   a one-cell row separates the animal. Not in the paper. The engine of every
   closed form below. Proved: `docs/proofs/diagonal-law.md` step 1. Needs
   nothing.
3. **Height partition.** Σ_H T(n,H) = a(n). Stated as a definition, line 85.
   Needs nothing.

### Closed forms

4. **T(n,n) = 3^(n−1).** Consecutive one-cell rows connect iff the column
   offset is in {−1,0,1}. In the paper with proof, lines 131 and 293.
   Needs 2.
5. **Doubled-row gap lemma.** Two cells in one row join only as a domino or
   with a gap of exactly one empty cell, bridged by a single cell in the
   middle column of a neighboring row. One clause, line 314. Proved:
   `docs/proofs/T-n-nm1.md` §3. Needs 2.
6. **T(n,n−1) = (25n−45)·3^(n−4)**, n ≥ 3. In the paper with derivation,
   lines 304–345; census n = 4..8 in the verifier. Needs 2, 4, 5.
7. **The diagonal formula.** For n ≥ 2k+1, T(n,n−k) = P_k(n)·3^(n−3k−1), P_k
   of degree ≤ k, integer-valued. Stated lines 133–135 as a fitted fact.
   Proved: `docs/proofs/diagonal-law.md` and Lean; not in the paper.
   Needs 2, 3.
8. **Leading coefficient 25^k/k!**, so deg P_k = k exactly. Stated line 135.
   Proved: `docs/proofs/product-form.md`, taking 25 from item 6. Not in the
   paper. Needs 6, 7.
9. **P_k pinned by rows 2k+1..3k.** With the leading coefficient fixed, k
   unknowns, k in-onset cells, nonsingular Vandermonde. Stated line 136.
   Needs 7, 8; wrong if separated from the sentence before it.
10. **Composition of a(24)–a(40).** Cells with H > n/2 are in onset, so
    enumerated cells plus closed-form evaluations sum to a(n), and the closed
    forms check the enumerated cells. Abstract. Needs 3, 9.
11. **T(n,n−2) = ½(625n²−2459n+1134)·3^(n−7)**, n ≥ 5. Decided in, not yet
    in the tex. Proof: `docs/proofs/T-n-nm2-and-general.md` §1, in the style
    of item 6. Needs 2, 4, 5. Leading coefficient 625/2 is the k = 2
    instance of item 8.

### Growth

12. **Exponential upper bound a(n) ≤ C^n.** Spanning-tree count for connected
    n-sets through a fixed cell in a degree-8 graph, C ≤ 7e or so. Not in the
    paper. Makes λ finite; used by 17. Cite or prove in two lines. Needs
    nothing.
13. **Supermultiplicativity and Fekete.** Diagonal-corner concatenation is
    injective, so a(m+n) ≥ a(m)a(n); hence a(n)^(1/n) → λ = sup a(n)^(1/n),
    λ ≥ a(40)^(1/40) = 6.2208, a(n) ≤ λ^n. Convergence asserted line 289
    without proof; the author's argument is in the tex comment above it.
    Needs 12.
14. **λ ≈ 7.11.** Not a theorem. Cite or drop (Madras ratio theorem,
    differential approximants, the bracket 6.543 ≤ λ ≤ 9.3154). Needs 13 to
    be well defined.

### Symmetry

15. **Burnside on D4.** Free = ⅛ Σ_{D4} Fix(g); one-sided = ¼ Σ_{C4} Fix(g);
    bilateral = free classes with a reflection; bilateral + asymmetric =
    free. Only the last is in the paper, line 220. Cite Burnside. Needs
    definitions only.
16. **The Burnside congruence** a(n) ≡ I(C4) + I(D2ax) + I(D2diag) − 2·I(D4)
    (mod 4), from the orbit-size count with F(H) for stabiliser exactly H.
    Invoked abstract line 53, never stated. Three lines in
    `results/symmetry-classes.md`. Needs 15.
17. **Symmetric polyplets are negligible.** Each nontrivial Fix(g)(n) ≤
    poly(n)·a(⌈n/2⌉ + O(1)) (a symmetric animal is a half plus an axis);
    a(n) ≥ 6.2208^(n−39) from 13; the ratio vanishes exponentially provided
    C^(1/2) < 6.2208. This is "one-sided → a(n)/4, free → a(n)/8", line 166.
    Not in the paper, not in the repo as a proof. Needs 12, 13, 15.
18. **Polyominoes are a vanishing share.** Fixed polyominoes ≤ 4.65^n
    (Klarner–Rivest) against a(n) ≥ 6.2208^(n−39). "Few polyplets are
    polyominoes thanks to the higher growth rate", line 165; A194596 = free
    polyplets − A000105 rests on item 1. Needs 1, 13, 15 for the free
    version, one citation.

### Holes

19. **Hole definition and the Euler count.** A hole is a bounded
    rook-connected component of the complement. With 8-connected foreground
    and 4-connected background, Gray's 2×2-window formula with the −2·Q_D
    branch gives E = components − holes, so holes = 1 − E for a connected
    animal, and E accumulates over column pairs. What "tracking the Euler
    characteristic" (line 226) rests on. Not stated. Cite Gray 1971 or
    Rosenfeld. Needs the definition at line 81.
20. **Minimal enclosures.** A 1-cell hole needs its four rook neighbors,
    pairwise king-adjacent, so 4 is minimal and unique; a domino hole needs
    its six; two 1-cell holes need ≥ 6 (two 4-sets share ≤ 2 cells), achieved
    diagonally. Stated lines 82–83 without proof. Needs 19.

### Methods

21. **Transfer-matrix signature sufficiency.** Equal frozen column,
    connectivity partition, top/bottom flags and remaining budget give equal
    completions, so the count over signatures is T(n,H) exactly. Described
    lines 298–302, correctness never stated. Cite Jensen or Conway; state the
    invariant. Needs 2, 3.
22. **The coloring second source.** C_H(n) = Σ_{h≤H} (H−h+1)·T(n,h), T its
    second difference in H; the connected count is the q¹ coefficient of the
    Fortuin–Kasteleyn polynomial. Abstract line 52. Decided: machine work
    with a pointer, or drop. If kept, state only the second-difference
    identity and cite `docs/proofs/cutcount-identity.md`. Needs 3.
23. **Redelmeier.** Citation only.

Stated and proved in the paper: 4, 6. Stated or invoked without proof: 3, 7,
8, 9, 13, 15, 16, 20. Needed by the text, never stated: 1, 2, 5, 12, 17, 18,
19, 21. Decided in, unwritten: 11. Cite-or-drop: 14, 22.
