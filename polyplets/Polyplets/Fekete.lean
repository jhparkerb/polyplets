/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Analysis.Subadditive
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# Fekete's ladder, once, for any supermultiplicative counting sequence

`Growth.lean` built `λ = lim a(n)^{1/n}` from three facts about the polyplet
sequence `a`: it is supermultiplicative, it is positive from `n = 1` on, and it
sits under some exponential. Nothing else about `a` entered. This file isolates
those three facts as a structure and runs the ladder once:

    negLog → subadditive → bddBelow → growth → tendsto → le_growth_pow

so that a second sequence costs an instance, not a transcription. `Growth.lean`'s
`lambda` and `StairGrowth.lean`'s `mu` are the two instances.

The public names of the polyplet development (`lambda`, `lambda_tendsto`,
`a_le_lambda_pow`, `lambda_le`) survive as thin wrappers over
`polypletFekete`; `AuditOutworks.lean` pins their axiom footprints, so a
regression here is a build error there.

## Why `f 0` needs no hypothesis

`ceiling 0` reads `f 0 ≤ c ^ 0 = 1`, so `f 0` is `0` or `1` and `negLog 0 = 0`
either way — `Real.log 0 = 0` is Mathlib's junk value and it is the one the
degenerate case of subadditivity wants. Counting sequences that start at `0`
(no animals of area zero) and ones that start at `1` (the empty object) are
both admissible, with no case split at the point of use.
-/

namespace Polyplets

/-- The three facts Fekete's lemma needs about a counting sequence: it is
supermultiplicative, positive from `1` on, and under an exponential ceiling
`c ^ k` with `1 ≤ c`. -/
structure Fekete where
  /-- The counting sequence. -/
  f : ℕ → ℕ
  /-- The base of the exponential ceiling. -/
  c : ℝ
  /-- The ceiling's base is at least `1` — it dominates `f 0 ≤ 1`. -/
  one_le_c : 1 ≤ c
  /-- Supermultiplicativity: the objects glue without waste. -/
  supermul : ∀ m n, f m * f n ≤ f (m + n)
  /-- There is at least one object of every positive size. -/
  one_le : ∀ {k : ℕ}, 1 ≤ k → 1 ≤ f k
  /-- The exponential ceiling. -/
  ceiling : ∀ k : ℕ, (f k : ℝ) ≤ c ^ k

namespace Fekete

variable (F : Fekete)

/-- The sequence Fekete is applied to: `-log (f n)`. -/
noncomputable def negLog (k : ℕ) : ℝ := -Real.log (F.f k)

/-- Positivity of `f k` in `ℝ`, the form the `log` steps want. -/
theorem f_pos {k : ℕ} (hk : 1 ≤ k) : (0 : ℝ) < F.f k := by
  exact_mod_cast F.one_le hk

/-- `negLog 0 = 0`, whether `f 0` is `0` (Mathlib's `log 0 = 0`) or `1`. -/
@[simp] theorem negLog_zero : F.negLog 0 = 0 := by
  have h : F.f 0 ≤ 1 := by
    have := F.ceiling 0
    rw [pow_zero] at this
    exact_mod_cast this
  have h0 : F.f 0 = 0 ∨ F.f 0 = 1 := by omega
  rcases h0 with h0 | h0 <;> simp [negLog, h0]

/-- **Supermultiplicativity, read through `log`.** The degenerate cases `m = 0`
and `n = 0` are equalities, by `negLog_zero`. -/
theorem subadditive : Subadditive F.negLog := by
  intro p q
  rcases Nat.eq_zero_or_pos p with rfl | hp
  · simp
  rcases Nat.eq_zero_or_pos q with rfl | hq
  · simp
  have h1 : (0 : ℝ) < F.f p := F.f_pos hp
  have h2 : (0 : ℝ) < F.f q := F.f_pos hq
  have hsm : ((F.f p : ℝ) * (F.f q : ℝ)) ≤ (F.f (p + q) : ℝ) := by
    exact_mod_cast F.supermul p q
  have hlog : Real.log ((F.f p : ℝ) * (F.f q : ℝ)) ≤ Real.log (F.f (p + q) : ℝ) :=
    Real.log_le_log (by positivity) hsm
  rw [Real.log_mul (ne_of_gt h1) (ne_of_gt h2)] at hlog
  simp only [negLog]
  linarith

/-- The lower bound on `negLog k / k` supplied by the exponential ceiling. -/
theorem div_ge {k : ℕ} (hk : 1 ≤ k) : -Real.log F.c ≤ F.negLog k / k := by
  have hkR : (0 : ℝ) < k := by exact_mod_cast hk
  have hpos : (0 : ℝ) < F.f k := F.f_pos hk
  have hlog : Real.log (F.f k) ≤ k * Real.log F.c := by
    calc Real.log (F.f k) ≤ Real.log (F.c ^ k) := Real.log_le_log hpos (F.ceiling k)
      _ = k * Real.log F.c := by rw [Real.log_pow]
  rw [le_div_iff₀ hkR]
  simp only [negLog]
  linarith

/-- `negLog k / k` is bounded below, the hypothesis Fekete's lemma needs. -/
theorem bddBelow : BddBelow (Set.range fun k : ℕ => F.negLog k / k) := by
  refine ⟨-Real.log F.c, ?_⟩
  rintro x ⟨k, rfl⟩
  rcases Nat.eq_zero_or_pos k with rfl | hk
  · simp only [negLog_zero, Nat.cast_zero, zero_div]
    have := Real.log_nonneg F.one_le_c
    linarith
  · exact F.div_ge hk

/-- **The growth constant** `lim f(n)^{1/n}`, built as `exp` of the negated
Fekete limit of `negLog`. -/
noncomputable def growth : ℝ := Real.exp (-F.subadditive.lim)

/-- The growth constant is positive. -/
lemma growth_pos : 0 < F.growth := Real.exp_pos _

/-- **The growth constant is the limit of `f(n)^{1/n}`.** -/
theorem tendsto :
    Filter.Tendsto (fun n => (F.f n : ℝ) ^ ((n : ℝ)⁻¹)) Filter.atTop (nhds F.growth) := by
  have h0 : Filter.Tendsto (fun k : ℕ => F.negLog k / k) Filter.atTop
      (nhds F.subadditive.lim) :=
    F.subadditive.tendsto_lim F.bddBelow
  have h2 : Filter.Tendsto (fun k : ℕ => Real.exp (-(F.negLog k / k))) Filter.atTop
      (nhds F.growth) :=
    (Real.continuous_exp.tendsto _).comp h0.neg
  refine h2.congr' ?_
  filter_upwards [Filter.eventually_ge_atTop 1] with k hk
  rw [Real.rpow_def_of_pos (F.f_pos hk)]
  congr 1
  simp only [negLog]
  ring

/-- **Fekete's supremum half:** `f n ≤ growth ^ n` for every `n ≥ 1`. The Fekete
limit of a subadditive sequence is the infimum of `u n / n`, so `-lim` dominates
`log (f n) / n` at every `n` — which is what makes every computed term a
rigorous *lower* bound on the growth constant. -/
theorem le_growth_pow {n : ℕ} (hn : 1 ≤ n) : (F.f n : ℝ) ≤ F.growth ^ n := by
  have hpos : (0 : ℝ) < F.f n := F.f_pos hn
  have hnR : (0 : ℝ) < n := by exact_mod_cast hn
  have hle : F.subadditive.lim ≤ F.negLog n / n :=
    F.subadditive.lim_le_div F.bddBelow (by omega)
  rw [le_div_iff₀ hnR] at hle
  simp only [negLog] at hle
  calc (F.f n : ℝ) = Real.exp (Real.log (F.f n)) := (Real.exp_log hpos).symm
    _ ≤ Real.exp ((n : ℝ) * (-F.subadditive.lim)) := Real.exp_le_exp.mpr (by linarith)
    _ = F.growth ^ n := by rw [growth]; exact Real.exp_nat_mul _ n

/-- The ceiling passes to the limit: `growth ≤ c`. -/
theorem growth_le : F.growth ≤ F.c := by
  have hbd : -Real.log F.c ≤ F.subadditive.lim := by
    refine ge_of_tendsto (F.subadditive.tendsto_lim F.bddBelow) ?_
    filter_upwards [Filter.eventually_ge_atTop 1] with k hk using F.div_ge hk
  rw [growth]
  calc Real.exp (-F.subadditive.lim) ≤ Real.exp (Real.log F.c) :=
        Real.exp_le_exp.mpr (by linarith)
    _ = F.c := Real.exp_log (lt_of_lt_of_le zero_lt_one F.one_le_c)

end Fekete

end Polyplets
