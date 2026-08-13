# Proved forced parity: T(n,H) is even for n odd, H even

2026-08-11, Proposer 2 (congruence/valuation/symmetry) of the
triangle-structure hunt (`docs/triangle-structure-team-brief.md`).
Candidate `experiments/tristruct/candidates/p2_congruence.py` (C1),
verifier verdict **SURVIVES, 135/135 holdout cells exact** (81 of them
real-sweep), 190 cells in-region over the full n ≤ 39 triangle
(`experiments/tristruct/p2_measure.py` M4: 190/190).

## Statement and proof

**Theorem.** For every n odd and H even (H ≤ n), T(n,H) ≡ 0 (mod 2).

*Proof.* Let F be reflection of a fixed (translation-class) animal about the
horizontal midline of its own bounding box. F preserves cell count and box
height, so it is an involution on the set counted by T(n,H); non-fixed
animals pair up, giving T(n,H) ≡ #{F-invariant animals} (mod 2).
F-invariance on translation classes a priori means reflect(A) = A + t for
some translation t; but the reflection is about A's own bounding-box
midline, so box(reflect(A)) = box(A), and equality with A + t forces
box(A) + t = box(A), hence t = 0 and genuine set equality (this lemma
made explicit at refuter B's request). An
F-invariant animal with H even has every column invariant under the row
reflection i ↦ H+1−i, which is fixed-point-free when H is even; so every
column has even size and n is even. For n odd the fixed set is empty. ∎

The same argument through the 180°-rotation involution (whose fixed cell
would have to sit at the box center, which for H even lies between rows)
independently forces the same parity; and Klein-invariant counts vanish
there too (they are a subset of the F-invariant ones).

## Sharper empirical form: the zero set is exactly this region

With I(n,H) = I_H(D2ax), the count of animals invariant under the full
height-preserving Klein group (banked to n = 40 in
`results/subgroup_d2ax_byheight.txt`):

- I(n,H) = 0 for **all 190** cells with n odd, H even (the theorem proves
  this direction), and
- I(n,H) > 0 for **all 630** other cells n ≤ 40
  (`experiments/tristruct/p2_symtri_probe.py` P2).

So on n ≤ 40 the zero set of the symmetric triangle is *exactly*
{n odd, H even}. The nonzero direction is verified, not proved (easy
constructions cover most cases — e.g. a full 2×(n/2) rectangle is the unique
Klein-invariant animal with H = 2, giving I(n,2) = [n even] — but no uniform
construction for all four parity classes is written down here).

## Independence fields (per the brief)

- **Bits of independent check on a(40): 0.** Row 40 has n even; the region
  contains no row-40 cell. Stated plainly: this candidate contributes
  nothing to a(40). Its value is 190 theorem-grade parity bits on the
  n ≤ 39 triangle — those cells' parity now rests on a proof, not on any
  engine or checker agreeing with another.
- **Input footprint:** derivation consumed no banked cells (proof from the
  definition; sanity data from my own enumerator `p2_enum --sym`, n ≤ 13).
  Prediction consumes no banked cells (constant residue 0).
- **Derivation independence:** blind. The theorem was derived and checked
  on self-enumerated cells before the banked triangle was consulted.
- **Rule independence:** the proof is about the definition itself; the
  sanity enumerator uses my own connectivity rule (crosschecked in
  `results/triangle-hunt-enumerator-crosscheck.md`), not the engines'.

## Novelty grep, and the exact relation to prior work

The repo-wide grep (parity / mod 2 / Burnside / Klein over `results/*.md`,
`docs/proofs/*.md`) turns up the subgroup census line of work, which must be
distinguished carefully:

- `results/subgroup-mod4.md` banks **T(n,H) ≡ I_H(D2ax) (mod 2)** and
  checks it on all 820 cells at n ≤ 40 by *computing both sides*. That is an
  identity between two computed quantities (Burnside read backwards; that
  file itself claims no novelty for it).
- `results/percell-mod4.md` (mod-4 refinement, n ≤ 32) notes some (n,H)
  rows of the symmetric inputs are "genuine zeros", as an empirical
  coverage footnote. No parity theorem is stated in either file, and the
  n-odd/H-even characterization appears nowhere in-tree.
- What is new here: the **closed-form zero** — on this region the identity's
  right side is 0 by proof, so the parity of T needs no symmetric count to
  be computed at all; plus the exact-zero-set observation on I.
- The mechanical sweep (`experiments/tristruct/sweep_report.md`) could not
  have found this, but for a structural reason, not a data one (my first
  printed justification here was measurably wrong and was corrected after
  refuter B's measurement, `results/triangle-hunt-refutation-symmetry.md`
  §4): the sweep tests whole-column residue patterns and has no hypothesis
  class for a region or parity-class statement, so C1 — a claim over
  {n odd, H even} across all columns at once — is out of its reach by
  construction. On the data side, the even-H columns are NOT all irregular
  mod 2: T(n,4) is period 4 (the sweep found and culled it
  KNOWN-COINCIDENT, sweep_report.md line 485), T(n,6) and T(n,8) are
  period 8 out to n = 40 (missed only by the sweep's 2p+4 support rule),
  and H = 10 is the first genuinely aperiodic even column.

## Refuter notes (attacks I ran myself)

- Region edges: H = 2 column (engine closed form) and near-diagonal cells
  (H = n−1 even, i.e. the k = 1 diagonal at odd n, inside the diagonal law's
  solved corner) — all 190 cells pass, none excluded, no exceptions at the
  onset boundary.
- The claim's failure surface: a corruption of even delta on a covered cell
  is invisible — inherent to any single congruence mod 2, stated up front.
- Restatement check: against `known.py` families (diagonal law, ternary
  spine, low strips) — verifier did not cull; the diagonal law determines
  parity only on k ≤ 13 diagonal cells, which are a measure-zero corner of
  the region; the theorem covers the whole bulk band as well.
