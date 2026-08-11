# Structure of the symmetry-refined triangle I(n,H): diagonals and columns

2026-08-11, Proposer 2 (congruence/valuation/symmetry) of the
triangle-structure hunt. Companion to
`results/triangle-hunt-klein-parity.md`. Scripts:
`experiments/tristruct/p2_symdiag.py`, `p2_symcol_rec.py`,
`p2_symtri_probe.py`; self data `experiments/tristruct/data/p2_sym_n14.txt`
(own enumerator `p2_enum --sym`, 3m42s for n ≤ 14).

## The object, and why it was fair game

I(n,H) = I_H(D2ax): fixed king animals of height exactly H invariant under
the full height-preserving Klein group {e, tb, lr, 180}. Banked to n = 40 by
the subgroup census (`results/subgroup_d2ax_byheight.txt`, `symcount_fast`
lineage) as the *input* of the per-cell parity check on the a(40) triangle
(`results/subgroup-mod4.md`). `results/triangle-combinations.md` lists
"symmetry-class-refined triangles" as an untested combination; no structure
hunt on I exists in-tree (grep: parity/Burnside/Klein/subgroup over
results/, docs/proofs/).

Why structure on I matters at all for a(40): the banked row-40 parity bits
consume I(40,H) from a single code path. Any relation that predicts I(40,H)
from smaller n makes that input two-source.

**Cross-validation first** (checker held to a higher standard): my own
recursion (`p2_enum --sym` klein column, independent connectivity rule)
matches the banked I file on **all 105 cells n ≤ 14**, and its tb/r180
totals match the sym34 farm (`runs/sym34/`) on all n ≤ 14. Three code
lineages agree on the object at small n.

## Diagonals: I(n, n−k) is an eventually quasi-polynomial of degree ⌊k/2⌋

Protocol: blind where self data suffices — fit ONLY on self-enumerated
cells n ≤ 14, banked n ≥ 15 pure holdout; where the onset leaves too little
self depth, a declared phase-2 fit on banked n ≤ 22 with banked 23..40 as
strict holdout (derivation touches banked fit cells; independence scored
lower). Exact arithmetic throughout; support rule: a degree-d fit needs
≥ 2d+3 contiguous matching fit points.

| k | class | form (m = ⌈n/2⌉) | onset | protocol | holdout |
|---|---|---|---|---|---|
| 0 | both | 1 | n=1 | blind | 26/26 pass |
| 1 | n even (odd ≡ 0 proved) | 1 | n=2 | blind | 13/13 pass |
| 2 | both | ⌊(n−1)/2⌋ | n=3 | blind | 26/26 pass |
| 3 | n even | n/2 | n=8 | phase 2 | 9/9 pass |
| 4 | both | (m−1)(m−2)/2 + 2, m = ⌈n/2⌉ — i.e. I(n,n−4) depends only on ⌈n/2⌉ | n=7 | phase 2 | 18/18 pass |
| 5 | n even | quadratic in n/2 through (18,40),(20,49),(22,59) | n=12 | phase 2, **MANUAL OVERRIDE of the 2d+3 support rule** (6 fit points for deg 2, one short; the script itself culls this row) | 9/9 pass (n=24..40) |
| ≥6 | — | second differences not settled by n=22 (deg-3 onset too late) | — | — | **negative: not determined** |

**Correction 2026-08-11 (refuter B):** the k=4 form was first printed with
m = ⌊n/2⌋, which fails at every odd n (first at n=11: 8 vs the true 12).
A transcription error in the write-up, not in the fits — the phase-2
per-class fit points ((17,30),(19,38),(21,47) and (18,30),(20,38),(22,47))
were correct, and the ⌈n/2⌉ form matches banked I on all n = 7..40
(re-verified directly). Caught by refuter B's independent recount
(`results/triangle-hunt-refutation-symmetry.md`).

k = 0 and k = 1 are also proved from the definition (H = n forces one cell
per row and the lr-mirror pins each to the central column — the vertical
bar, uniquely; H = n−1 forces the doubled row to the middle row, n even,
and its pair to the two king-adjacent off-center columns, uniquely).
k ≥ 2 forms are fitted-then-held-out, not proved; the degree-⌊k/2⌋ shape
(against degree k for the main triangle's P_k) is what a
symmetric-pairs-of-excess-cells mechanism predicts, and a proof in the
diagonal-law style looks reachable — left for the proof-first lane.
Refuter B (`results/triangle-hunt-refutation-symmetry.md`) supplies the
sketch for every k: a Klein-invariant diagonal animal is a placement of at
most ⌊k/2⌋ heavy-row profiles into ⌊H/2⌋ palindromic slots with O(1) local
connectivity constraints, which gives eventual quasi-polynomiality in n of
period 2 and degree ≤ ⌊k/2⌋ for ALL k — so the k ≥ 6 negative below is
about reachability from n ≤ 22 fit depth, not about existence of the form.

Note the contrast with the main triangle: T(n,n−k) = P_k(n)·3^(n−1−3k)
(diagonal law, proved). I has **no 3-power**: the symmetric triangle's
diagonals are pure quasi-polynomials. Corollary of the two + the parity
identity: P_k(n) ≡ I(n,n−k) (mod 2) for n ≥ both onsets — the diagonal-law
prefactor's parity is a ⌊k/2⌋-degree quasi-polynomial's.

## Columns: I(·,3) and I(·,4) are low-order C-finite, fit low / predict high

`p2_symcol_rec.py`, minimal exact recurrence fitted on n ≤ 22 only,
every banked term n = 23..40 held out:

- **H=3**: I(n,3) = 2·I(n−2,3) − I(n−8,3), order 8, **18/18 holdout pass
  including I(40,3) = 187425**. Refuter B notes the characteristic
  polynomial factors as (x²−1)(x⁶−x⁴−x²−1) — tribonacci in x², exactly
  the palindromic 3-letter column-word mechanism (verified:
  the product expands to x⁸−2x⁶+1).
- **H=4** (even-n subsequence; odd-n ≡ 0 proved): order 5, coefficients
  (1, 2, −2, 1, −1), **9/9 holdout pass including I(40,4) = 8117**.
- **H=1,2**: constant 1 / [n even] (trivially proved: bar; unique 2×(n/2)
  rectangle).
- **H = 5..12: negative.** No recurrence of order ≤ 12 fits n ≤ 22 (or
  fits but fails holdout — orders and first-fail rows in the script
  output). Same mechanism caveat as the sweep's T-column survivors: a
  palindromic-transfer-matrix object is *expected* to be C-finite; the
  finding is that the order is small enough to fit-and-predict for H ≤ 4
  and demonstrably not ≤ 12 for H = 5..12.

## Independence fields

- **Bits of independent check on a(40): ~0 direct.** No relation here
  predicts T(40,H) or a(40). Indirect: the H=3, H=4 recurrences and the
  k ≤ 5 diagonal forms each reproduce banked I(40,H) cells
  (H = 3, 4, 35..40) from strictly smaller n, making the corresponding
  *inputs* of the banked row-40 parity check two-source. The parity check
  itself stays worth 1 bit/cell; nothing here adds to that number, and I
  am not claiming otherwise.
- **Input footprint:** blind rows: self cells n ≤ 14 only. Phase-2 rows
  and column fits: banked I cells n ≤ 22 (largest consumed n = 22);
  holdout is banked I n = 23..40, never touched in fitting.
- **Derivation independence:** k ≤ 2 diagonals and all zero statements:
  blind. k = 3..5 diagonals and column recurrences: fitted on banked I
  (declared; that is why they sit below the blind rows).
- **Rule independence:** self data uses my own connectivity rule; banked I
  comes from `symcount_fast` (quotient-domain DFS), a third lineage vs the
  production column engine. The 105-cell three-way agreement is above.

## Refuter notes

- The support rule (2d+3 contiguous fit matches) was chosen before k=5 was
  examined; k=5 is reported as marginal rather than silently admitted.
- Onset behavior is real and visible (k=5 fails at n = 6, 8, 10 with
  errors −6, −1, +3): these forms are *eventually* quasi-polynomial, and
  every onset row in the table is the measured one, not an assumption.
- The obvious overfit attack — quasi-polynomials have enough parameters to
  fit anything short — is answered by the holdout counts: 26, 13, 26, 9,
  18, 9 exact integer predictions per row, values growing to 10^2 (and for
  columns to 10^5..10^6 at n=40) with zero misses.
