# GF-2 — `Polyplets/Grand/Mu.lean`: the root series ν and the multiplier μ

Read first: `polyplets/GRANDFORM-PLAN.md`; `briefs/GF1-series.md` (you import
its results); `Polyplets/Weights.lean` lines 180–420 (defs of `V`, `Vt` and
the native_decide values); `Polyplets/Weights3.lean`. The paper object being
built: μ = 1/z* of `docs/proofs/grand-form.md` Step 1, in coefficient form.
Numeric ground truth: `experiments/staircase_check.py` section 3.

## Deliverables

```lean
/-- Aggregated interior weights as a y-sequence per row count ℓ:
`v ℓ` vanishes below index ℓ (each cluster row carries ≥ 1 surplus —
encoded here by the guard, no combinatorial input needed). -/
def v (ℓ : ℕ) : ℕ → ℚ := fun j => if ℓ ≤ j ∧ 1 ≤ ℓ then (V ℓ j : ℚ) else 0

/-- The root series ν (= z* of docs/proofs/grand-form.md): ν₀ = 1/3, and for
m ≥ 1 the unique solution of the root equation
`eps = 3·ν + Σ_ℓ v_ℓ ∗ ν^{∗(ℓ+1)}` coefficient-by-coefficient. -/
noncomputable def nu : ℕ → ℚ
  | 0     => 1/3
  | m + 1 => -(1/3) * ∑ ℓ ∈ Finset.Icc 1 (m + 1),
      conv (v ℓ) (convPow (fun s => if s ≤ m then nu s else 0) (ℓ + 1)) (m + 1)
```

Termination: the guarded function only calls `nu s` for `s ≤ m < m + 1`;
use the `if h : s ≤ m` dependent form or `decreasing_by` as needed. Then:

1. **De-guarding.** `nu_unfold (m : ℕ) (hm : 1 ≤ m) :
   nu m = -(1/3) * ∑ ℓ ∈ Finset.Icc 1 m, conv (v ℓ) (convPow nu (ℓ+1)) m`.
   Key fact: at coefficient `m`, `conv (v ℓ) (convPow x (ℓ+1)) m` reads `x`
   only at indices `≤ m − 1`: `v ℓ` vanishes below ℓ ≥ 1
   (`conv_left_vanish_lt`), so the inner `convPow … (ℓ+1)` is evaluated at
   indices `≤ m − ℓ ≤ m − 1`; apply `convPow_congr_le` + `conv_congr_le` to
   replace the guarded prefix by `nu`.
2. **Root identity.** `root (m : ℕ) :
   eps m = 3 * nu m + ∑ ℓ ∈ Finset.Icc 1 m, conv (v ℓ) (convPow nu (ℓ+1)) m`
   (m = 0: `1 = 3·(1/3)`, ℓ-sum empty; m ≥ 1: rearrange `nu_unfold`).
3. **μ, non-recursively.**
   ```lean
   noncomputable def mu : ℕ → ℚ :=
     fun m => 3 * eps m + ∑ ℓ ∈ Finset.Icc 1 m, conv (v ℓ) (convPow nu ℓ) m
   ```
   with `mu_zero : mu 0 = 3` and `mu_succ_eq (hm : 1 ≤ m) :
   mu m = ∑ ℓ ∈ Finset.Icc 1 m, conv (v ℓ) (convPow nu ℓ) m`.
4. **The inverse law** `mu_conv_nu : conv mu nu = eps`. Compute
   `(conv mu nu) m = 3·nu m + Σ_ℓ (v_ℓ ∗ ν^{∗ℓ} ∗ ν) m
   = 3·nu m + Σ_ℓ (v_ℓ ∗ ν^{∗(ℓ+1)}) m = eps m` by `root`. The middle step
   is `conv_assoc` + `convPow` unfolding (`ν^{∗ℓ} ∗ ν = ν^{∗(ℓ+1)}` — mind
   the argument order in `convPow`'s definition; use `conv_comm` freely).
   Distributing `conv … nu` through the finite ℓ-sum: sums and `conv` in the
   first argument commute (`conv` is linear — add a tiny
   `conv_sum_left` lemma here or in GF-1 if missing).
   Also export `nu_conv_mu` via `conv_comm`, and
   `nu_zero : nu 0 = 1/3`, `mu_conv_nu_pow :
   conv (convPow mu ℓ) (convPow nu ℓ) = eps` (GF-1's `conv_convPow_inv`).
5. **Numeric gates (unconditional).**
   ```lean
   theorem mu_one : mu 1 = 25/3       -- via V_1_1 (native_decide, exists)
   theorem mu_two : mu 2 = 833/27     -- via V_1_1, V_1_2, V_2_2
   ```
   Proof pattern: `simp only [mu, nu, conv, convPow, v, eps, …]` to expose
   the finite arithmetic, rewrite the `V`-values by the existing theorems
   (`V_1_1`, `V_1_2`, `V_2_2` — NOT new native_decides), then `norm_num`.
   Work out the finite sums by hand first if simp normal forms fight you:
   mu 1 = V 1 1·ν₀ = 25/3; mu 2 = V 1 2·ν₀ + V 1 1·ν₁ + V 2 2·(ν∗ν)₀ with
   ν₁ = −25/27, giving 49/3 − 625/27 + 339/9 = 833/27.
6. **Conditional j=3 gate** (mirrors the house heavy-tier pattern):
   `theorem mu_three_of (hV33 : V 3 3 = 4778) : mu 3 = 32708/243`
   using `V_1_3`, `V_2_3` from `Weights3.lean` (check their exact names) and
   the hypothesis for the heavy leaf. Do NOT import `Weights3Heavy` here.

## Pitfalls

- `v` carries `1 ≤ ℓ` in its guard so `v 0 = 0` identically — keeps every
  ℓ-sum honest when ranges are extended; state
  `v_vanish_lt : ∀ j < ℓ, v ℓ j = 0` and `v_zero : v 0 = fun _ => 0`.
- Keep ℓ-sum ranges as `Finset.Icc 1 m`; extension beyond m is all zeros
  (via `v`-vanishing + `convPow_vanish_lt`) but you should never need it.
- The imports: `Polyplets.Grand.Series`, `Polyplets.Weights`,
  `Polyplets.Weights3`. Nothing from `Peel`/`Shape`.

## Done criteria

Green build, no `sorry`; `#print axioms mu_one` = standard +
`Lean.ofReduceBool` only (inherited from `V_1_1`); gates G1 of the master
plan pass. Commit `lean-gf: Mu — root series, multiplier, inverse law`.
