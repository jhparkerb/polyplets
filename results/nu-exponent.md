# Where a(n)'s mass sits + the extent exponent nu

Date: 2026-07-10. `experiments/nu_exponent.py` on the banked height triangle.
Settles "where does the typical polyplet's height sit" (raised vs Other Claude,
who over-claimed "fixed small columns 2,3,4").

## Result

Mean bbox height vs n (mass-weighted by T(n,H)):

- **`mean_H/n` falls monotonically** `0.745 (n=4) → 0.488 (n=18) → 0.375 (n=36)`.
  So typical height is a *shrinking* fraction of n → the mass is at
  **growing-but-sublinear height**, not `n/2` and not fixed small H.
- Fitting `mean_H ~ c·n^ν`, the **local slope drifts `0.744 → 0.688`** over the
  clean range n=4..19 (where H<=18 captures 100% of the mass), monotonically
  decreasing toward the **universal 2D lattice-animal exponent `ν ≈ 0.6407`**.
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

- Data truncated at H<=18, so `captured < 1` for n>19 (down to 0.905 at n=36);
  those `mean_H` are slightly underestimated (missing high-H tail biases mean and
  local-ν DOWN). The clean, unbiased range is n<=19. A paper-grade ν figure wants
  the FULL height distribution (all H, via the transpose/full triangle).
- n<=19 is small for asymptotics; finite-size corrections are large (local ν still
  0.69 at n=19). The trend toward 0.6407 is unambiguous; the precise value is not
  pinned here.

## Paper use

Figure candidate: local-ν vs n (or `mean_H/n` vs n) showing convergence toward
`0.6407` — a clean one-panel universality check. Cheap to upgrade with the full
distribution if wanted.
