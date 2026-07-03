/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib

/-!
# Diagonal closed forms for fixed polyplets (A006770)

`T n H` is the number of *fixed polyplets* — king-move connected animals,
counted up to translation — with `n` cells whose bounding box has height
exactly `H`.

For heights a fixed distance `k` below the maximum (`H = n - k`, the "k-th
diagonal"), the counts are claimed to be a degree-`k` polynomial in `n` times a
power of three:

  `T n (n - k) = P_k(n) * 3 ^ (n - 1 - 3 * k)`,  valid for `n ≥ 2*k + 1`.

We state it over `ℚ` with an **integer** exponent (`zpow`) so the `3`-power
stays meaningful across the whole `n ≥ 2k+1` range: for `2k+1 ≤ n < 3k+1` the
exponent `n - 1 - 3k` is negative and `P_k(n)` carries the compensating factors
of three (exactly the positive/negative-exponent split the engine's `applyPow3`
handles). Stating it in `ℕ` would truncate that exponent to `0` and be false.

Paper proofs:
* `docs/proofs/T-n-nm1.md` — `k = 1`, near-complete (one informal
  factorization step).
* `docs/proofs/T-n-nm2-and-general.md` — `k = 2` modulo a machine-checked
  gadget lemma; general `k` is a *sketch*, and the factorization lemma it
  leans on is the open prize (see the Fable review, 2026-07-03).

## Roadmap
0. Replace the `opaque T` placeholder with the real definition: the king graph
   on `ℤ × ℤ`, `SimpleGraph.Connected` on the induced subgraph over a `Finset`,
   a canonical translate to pin the up-to-translation quotient, and
   bounding-box height. (This file only *states* the targets.)
1. Prove `T_n_nm1` (`k = 1`).
2. Prove `T_n_nm2` (`k = 2`).
3. State and prove the general-`k` factorization lemma — the real theorem the
   whole diagonal-injection method rests on.
-/

namespace Polyplets

/-- Number of fixed polyplets of `n` cells whose bounding box has height
exactly `H`.

**PLACEHOLDER.** Roadmap step 0 replaces this `opaque` stub with the real
`Finset (ℤ × ℤ)` definition; every theorem below is `sorry` until then. -/
opaque T : ℕ → ℕ → ℕ

/-- **k = 1 diagonal.** `T(n, n-1) = (25n - 45) · 3^(n-4)` for `n ≥ 4`
(the statement is true for `n ≥ 3` via the negative exponent; we take the
clean `n ≥ 4` regime here). Paper proof: `docs/proofs/T-n-nm1.md`. -/
theorem T_n_nm1 (n : ℕ) (hn : 4 ≤ n) :
    (T n (n - 1) : ℚ) = (25 * (n : ℚ) - 45) * (3 : ℚ) ^ ((n : ℤ) - 4) := by
  sorry

/-- **k = 2 diagonal.** `T(n, n-2) = ½(625n² - 2459n + 1134) · 3^(n-7)` for
`n ≥ 5`. Paper proof: `docs/proofs/T-n-nm2-and-general.md` §1 — a proof modulo
a machine-verified gadget lemma. -/
theorem T_n_nm2 (n : ℕ) (hn : 5 ≤ n) :
    (T n (n - 2) : ℚ)
      = (1 / 2) * (625 * (n : ℚ) ^ 2 - 2459 * (n : ℚ) + 1134)
          * (3 : ℚ) ^ ((n : ℤ) - 7) := by
  sorry

end Polyplets
