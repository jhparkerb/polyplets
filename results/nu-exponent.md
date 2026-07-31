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
  to n=19; full-triangle redo 2026-07-11: to 0.678 at n=36 — see the caveats update;
  **final data 2026-07-31: to 0.676 at n=40** — see the refresh at the bottom).
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

## Refreshed at n=40 (2026-07-31)

Recomputed on the final exact triangle `results/triangle.txt` (all H, 1≤H≤n≤40).
`experiments/nu_exponent.py` now reads that file untruncated by default; the old
H≤18 slice is reproduced with `python3 experiments/nu_exponent.py 18` (it returns
the original table above digit-for-digit, including `mean_H/n = 0.375` at n=36 and
the local slopes `0.744 → 0.688`). The untruncated slope sequence reproduces
[[height-distribution-collapse]]'s banked ν_eff values exactly through n=36.

Command: `python3 experiments/nu_exponent.py`.

- **`mean_H/n` still falls monotonically**, untruncated: `0.745 (n=4) → 0.488
  (n=18) → 0.392 (n=36) → 0.379 (n=40)`, with `mean_H = 15.17` at n=40.
  (The banked `0.375 (n=36)` above was the H≤18-slice figure — truncation-biased
  down because 9.5% of the n=36 mass sits above H=18. On the full triangle the
  same n=36 number is 0.392. The monotone-decrease conclusion is unaffected.)
- **The local slope keeps drifting down.** 4-step slopes `d log⟨H⟩ / d log n`:

  | n | 12 | 16 | 20 | 24 | 28 | 32 | 36 | **40** |
  |---|---|---|---|---|---|---|---|---|
  | ν_eff | 0.7124 | 0.7007 | 0.6932 | 0.6879 | 0.6838 | 0.6806 | 0.6779 | **0.6757** |

  Consecutive-n slopes run `0.744 (n=5) → 0.678 (n=36) → 0.675 (n=40)`. The
  full-range log-log fit over n=4..40 gives ν = 0.7009 (dominated by small n; the
  local slope is the honest estimator).
- The drift per 4 terms is still shrinking (0.0027 over 32→36, 0.0022 over
  36→40): a slow approach, consistent with a Δ₁=1/2 confluent correction, and
  nowhere near reaching 0.6407 at n=40. **Reading unchanged: the trend toward
  0.6407 is unambiguous, the value is not pinned by n≤40.** This is the final
  data — no more terms are coming — so 0.676 is the last effective ν this
  project will report.
- mode_H = 14 at n=40 (still tracking mean_H = 15.17).
