# Where a(n)'s mass sits + the extent exponent nu

Date: 2026-07-10. `experiments/nu_exponent.py` on the banked height triangle.
Settles "where does the typical polyplet's height sit" (raised vs Other Claude,
who over-claimed "fixed small columns 2,3,4").

## Result

Mean bbox height vs n (mass-weighted by T(n,H)):

- **`mean_H/n` falls monotonically** `0.745 (n=4) → 0.488 (n=18) → 0.375 (n=36)`.
  So typical height is a *shrinking* fraction of n → the mass is at
  **growing-but-sublinear height**, not `n/2` and not fixed small H.
- Fitting `mean_H ~ c·n^ν`, the **local slope drifts down** monotonically toward the
  **universal 2D lattice-animal exponent `ν ≈ 0.6407`** (original H≤18 run: 0.744→0.688
  to n=19; full-triangle redo 2026-07-11: to 0.678 at n=36 — see the caveats update).
- mode_H tracks mean_H (both `~ n^0.64`).

## Reading

1. **Question settled:** the bulk of `a(n)` lives at height `~ n^ν`, ν≈0.64 —
   growing, but sublinearly. The correct statement we gave Other Claude; his
   "columns 2,3,4" was too extreme, his "n/2" worry is wrong the other way.
2. **Universality confirmed:** the extent exponent converges toward `0.6407`, the
   standard 2D lattice-animal (Klarner) value — polyplets share the universality
   class of ordinary polyominoes. (Companion to the paper's `θ = −1` growth-fit
   check, the other universal exponent.)

## Caveats

- **UPDATE 2026-07-11:** the truncation caveat below is RESOLVED — the full
  untruncated triangle T(n,H) (all H, n≤36, row sums verified == a(n)) is banked at
  `results/ns_a36/perheight/`. Redone on the full data, mean-based local-ν drifts
  0.712 (n=12) → 0.678 (n=36), same trend toward 0.6407, now clean to n=36 (no
  high-H bias). The full-distribution analysis + a universal shape data-collapse are
  in [[height-distribution-collapse]]. (The original run below used an H≤18 slice.)
- ~~Data truncated at H<=18, so `captured < 1` for n>19; the clean range is n<=19.~~
  (Superseded — see the update above; full triangle now used.)
- n≤36 is still pre-asymptotic; finite-size corrections are large (effective ν ≈
  0.68 at n=36). The trend toward 0.6407 is unambiguous; the precise value is not
  pinned here.

## Paper use

Figure candidate: local-ν vs n (or `mean_H/n` vs n) showing convergence toward
`0.6407` — a clean one-panel universality check. Cheap to upgrade with the full
distribution if wanted.
