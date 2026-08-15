# Ghost Ship — sealed banked-claim list (§7 item 4)

Sealed 2026-08-15. The re-derivation denominator: claims already banked
**at the cut, inside the slice**. A session claim matching one of these is
a re-derivation (witting if the report flags the possibility, unwitting
otherwise); re-derived claims are excluded from "verified". Quoted from
the slice files at `74b2c20` — the sessions hold these very files, so
re-deriving one is a reading failure, not a discovery.

1. Convex polyplet = HV-convex king animal; 38 exact terms by area are
   banked (`results/convex-polyplets.md`).
2. By area, convex polyplets are empirically non-D-finite (q-series
   behaviour on 38 terms) — the Convex Mirage
   (`docs/proofs/convex-mirage.md`).
3. Classical convex-polyomino solvability is by perimeter, not area
   (`docs/proofs/convex-mirage.md` — the on-disk hint).
4. μ(convex-by-area) ≈ 3.129 with transfer matrix in hand
   (`results/convex-polyplets.md`, `experiments/convex_tm.py`).
5. Directed king animals: A047781, GF D(t) = ¼((1+t)/√(1−6t+t²) − 1),
   growth exactly 3+2√2 (`results/directed-king-animals.md`, after
   Bacher arXiv:1301.1365).
6. Multi-directed lower bound λ ≥ 6.475; directed gives 5.828
   (`results/directed-king-animals.md`, `docs/proofs/polyplet-upper-bound.md`).
7. λ ≤ 9.3153 by exact rational Bui convolution certificate, as shipped
   (`docs/proofs/polyplet-upper-bound.md`; see ANSWER-KEY grader note on
   the post-cut 9.3154 correction).
8. Strip growth constants μ_H exact for H ≤ 13/14, a rigorous λ
   lower-bound ladder (`results/strip-growth-lambda-bounds.md`).
9. The diagonal law's shape is a theorem: polynomial × 3-power, degree
   ≤ k, onset n ≥ 2k+1, integral P_k (`docs/proofs/diagonal-law.md`).
10. The defect-gas row model: k = 0 stratum is a 3^{H−1} drift walk;
    diagonal-k animals = walk + k surplus cells in defect clusters,
    validated H ≤ 10, k ≤ 2 (`results/defect-gas.md`).
11. Diagonal, hole, and diagonal-content cuts dead-ended as tractability
    levers (`docs/proofs/convex-mirage.md`).

Not on this list (post-cut, therefore fair game): everything on the
answer-key ladder, the 9.3154 correction, and all post-07-12 banked work.
