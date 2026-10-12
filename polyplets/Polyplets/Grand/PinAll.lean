/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Polyplets.Grand.Staircase
import Polyplets.EnumData
import Polyplets.Pin

/-!
# The production polynomials `P_0 … P_18`, pinned level by level

`T_staircase` says one transfer step multiplies the diagonal family by the
fixed series `μ`:

`T(H+1+k, H+1) = Σ_{i ≤ k} μ_i · T(H+k-i, H)`.

Two consequences, each a single theorem here rather than one copy per level:

* `grand_step`: if `P_{k-i}` is known for `1 ≤ i ≤ k`, and `μ_0 … μ_k` are
  known, then `P_k` is pinned by its value at one cell `A_k = T(2k+1, k+1)`,
  by induction on `H` through the staircase (`hstair` is the staircase as a
  polynomial identity).
* `mu_step`: `μ_k` itself is solved from the staircase at `H = k+1`, where the
  only unknown is `μ_k · T(k+1, k+1) = μ_k · 3^k`; the one new cell is
  `B_k = T(2k+2, k+2)`.

Level `0` is `T(n,n) = 3^(n-1)`; levels `1 … 18` climb through `level_step`
with `anchorA`/`anchorB` as the only inputs (`BankedAnchors`, 36 cells). The
per-level arithmetic is three lemmas proved by `interval_cases`
(`stair_check`, `anchor_check`, `num_check`).

`μ_i·3^(2i-1)` is an integer (`cTab`); `μ` is carried as `μ_i·3^(2i) = 3·c_i`
so no negative exponent appears.
-/

namespace Polyplets

open Polynomial

/-! ## Grand form and its coordinate changes -/

/-- Grand form at level `i`: `3^(3i+1)·T(H+i, H) = Q(H+i)·3^(H+i)` for all
`H ≥ i+1`. -/
def GrandForm (i : ℕ) (Q : Polynomial ℚ) : Prop :=
  ∀ H : ℕ, i + 1 ≤ H →
    (3 : ℚ) ^ (3 * i + 1) * (T (H + i) H : ℚ) = Q.eval ((H : ℚ) + i) * 3 ^ (H + i)

/-- Grand form to the production `n`-form `T(n, n-k) = P(n)·3^(n-1-3k)`. -/
lemma grand_to_prod {k : ℕ} {P : Polynomial ℚ} (h : GrandForm k P) :
    ∀ n : ℕ, 2 * k + 1 ≤ n →
      (T n (n - k) : ℚ) = P.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k) := by
  intro n hn
  have hg := h (n - k) (by omega)
  rw [show n - k + k = n from by omega,
    show ((n - k : ℕ) : ℚ) + k = (n : ℚ) from by rw [Nat.cast_sub (by omega)]; ring] at hg
  rw [show ((n : ℤ) - 1 - 3 * k) = (n : ℤ) - (3 * k + 1 : ℕ) from by push_cast; ring,
    zpow_sub₀ (by norm_num : (3 : ℚ) ≠ 0), zpow_natCast, zpow_natCast]
  field_simp
  linear_combination hg

/-! ## The two generic steps -/

/-- **`μ_k` from the staircase at `H = k+1`.** With the lower levels and
`μ_0 … μ_{k-1}` known, the staircase reads
`B_k = Σ_{i<k} μ_i·T(2k+1-i, k+1) + μ_k·3^k`, and `hnum` is that equation
with the proposed `μ_k = 3·c_k/3^(2k)` substituted. The `i = 0` term is level
`k` at its onset, `A_k`, hence `hanchor`. -/
theorem mu_step (k : ℕ) (Q : ℕ → Polynomial ℚ) (c : ℕ → ℚ)
    (hlow : ∀ i, 1 ≤ i → i ≤ k → GrandForm (k - i) (Q (k - i)))
    (hmu : ∀ i, i < k → mu i * 3 ^ (2 * i) = 3 * c i)
    (hanchor : (3 : ℚ) ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) =
      (Q k).eval ((2 * k + 1 : ℕ) : ℚ) * 3 ^ (2 * k + 1))
    (hnum : (T (2 * k + 2) (k + 2) : ℚ) * 3 ^ (2 * k) = 3 * c k * 3 ^ k +
      ∑ i ∈ Finset.range k, 3 * c i * 3 ^ (2 * k - 2 * i) *
        ((Q (k - i)).eval ((k + 1 + (k - i) : ℕ) : ℚ) * 3 ^ (k + 1 + (k - i))
          / 3 ^ (3 * (k - i) + 1))) :
    mu k * 3 ^ (2 * k) = 3 * c k := by
  have hst := T_staircase k (k + 1) (by omega)
  rw [Finset.sum_range_succ, Nat.sub_self, Nat.add_zero,
    show k + 1 + 1 + k = 2 * k + 2 from by omega, show k + 1 + 1 = k + 2 from by omega] at hst
  have hdiag : (T (k + 1) (k + 1) : ℚ) = 3 ^ k := by
    rw [T_diag_pow (k + 1) (by omega),
      show ((k + 1 : ℕ) : ℤ) - 1 = (k : ℤ) from by push_cast; ring, zpow_natCast]
  rw [hdiag] at hst
  have hterm : ∀ i ∈ Finset.range k,
      mu i * (T (k + 1 + (k - i)) (k + 1) : ℚ) * 3 ^ (2 * k) =
        3 * c i * 3 ^ (2 * k - 2 * i) *
          ((Q (k - i)).eval ((k + 1 + (k - i) : ℕ) : ℚ) * 3 ^ (k + 1 + (k - i))
            / 3 ^ (3 * (k - i) + 1)) := by
    intro i hi
    rw [Finset.mem_range] at hi
    have e : (3 : ℚ) ^ (3 * (k - i) + 1) * (T (k + 1 + (k - i)) (k + 1) : ℚ) =
        (Q (k - i)).eval (((k + 1 : ℕ) : ℚ) + ((k - i : ℕ) : ℚ)) * 3 ^ (k + 1 + (k - i)) := by
      rcases Nat.eq_zero_or_pos i with rfl | hpos
      · simp only [Nat.sub_zero]
        rw [show k + 1 + k = 2 * k + 1 from by omega,
          show ((k + 1 : ℕ) : ℚ) + (k : ℚ) = ((2 * k + 1 : ℕ) : ℚ) from by push_cast; ring]
        exact hanchor
      · exact hlow i hpos (by omega) (k + 1) (by omega)
    have h3 : (3 : ℚ) ^ (3 * (k - i) + 1) ≠ 0 := pow_ne_zero _ (by norm_num)
    have h3' : (3 : ℚ) ^ (2 * i) ≠ 0 := pow_ne_zero _ (by norm_num)
    have eT : (T (k + 1 + (k - i)) (k + 1) : ℚ) =
        (Q (k - i)).eval ((k + 1 + (k - i) : ℕ) : ℚ) * 3 ^ (k + 1 + (k - i))
          / 3 ^ (3 * (k - i) + 1) := by
      rw [eq_div_iff h3, show ((k + 1 + (k - i) : ℕ) : ℚ) = ((k + 1 : ℕ) : ℚ) + ((k - i : ℕ) : ℚ)
        from by push_cast; ring]
      linear_combination e
    have em : mu i = 3 * c i / 3 ^ (2 * i) := by
      rw [eq_div_iff h3']; exact hmu i hi
    have hp : (3 : ℚ) ^ (2 * k) = 3 ^ (2 * i) * 3 ^ (2 * k - 2 * i) := by
      rw [← pow_add]; congr 1; omega
    rw [eT, em, hp]
    field_simp
  have key : (T (2 * k + 2) (k + 2) : ℚ) * 3 ^ (2 * k) =
      (∑ i ∈ Finset.range k, mu i * (T (k + 1 + (k - i)) (k + 1) : ℚ) * 3 ^ (2 * k)) +
        mu k * 3 ^ k * 3 ^ (2 * k) := by
    rw [hst, add_mul, Finset.sum_mul]
  rw [Finset.sum_congr rfl hterm, hnum] at key
  have h3k : (3 : ℚ) ^ k ≠ 0 := pow_ne_zero _ (by norm_num)
  apply mul_right_cancel₀ h3k
  linear_combination (-1 : ℚ) * key

/-- **`P_k` from one cell.** With the lower levels and `μ_0 … μ_k` known, and
the staircase as a polynomial identity (`hstair`), the grand form at level
`k` follows from its value at `A_k = T(2k+1, k+1)` by induction on `H`. -/
theorem grand_step (k : ℕ) (Q : ℕ → Polynomial ℚ) (c : ℕ → ℚ)
    (hlow : ∀ i, 1 ≤ i → i ≤ k → GrandForm (k - i) (Q (k - i)))
    (hmu : ∀ i, i ≤ k → mu i * 3 ^ (2 * i) = 3 * c i)
    (hstair : ∀ x : ℚ, (Q k).eval (x + 1) =
      ∑ i ∈ Finset.range (k + 1), c i * (Q (k - i)).eval (x - i))
    (hanchor : (3 : ℚ) ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) =
      (Q k).eval ((2 * k + 1 : ℕ) : ℚ) * 3 ^ (2 * k + 1)) :
    GrandForm k (Q k) := by
  intro H hH
  induction H, hH using Nat.le_induction with
  | base =>
    rw [show k + 1 + k = 2 * k + 1 from by omega,
      show ((k + 1 : ℕ) : ℚ) + k = ((2 * k + 1 : ℕ) : ℚ) from by push_cast; ring]
    exact hanchor
  | succ H hH ih =>
    have hall : ∀ i, i ≤ k →
        (3 : ℚ) ^ (3 * (k - i) + 1) * (T (H + (k - i)) H : ℚ) =
          (Q (k - i)).eval ((H : ℚ) + ((k - i : ℕ) : ℚ)) * 3 ^ (H + (k - i)) := by
      intro i hi
      rcases Nat.eq_zero_or_pos i with rfl | hpos
      · simpa using ih
      · exact hlow i hpos hi H (by omega)
    have hst := T_staircase k H hH
    have hs := hstair ((H : ℚ) + k)
    rw [show ((H + 1 : ℕ) : ℚ) + k = (H : ℚ) + k + 1 from by push_cast; ring, hs, hst,
      Finset.mul_sum, Finset.sum_mul]
    refine Finset.sum_congr rfl fun i hi => ?_
    rw [Finset.mem_range] at hi
    have e := hall i (by omega)
    have hm := hmu i (by omega)
    have hc : (H : ℚ) + ((k - i : ℕ) : ℚ) = (H : ℚ) + k - i := by
      rw [Nat.cast_sub (by omega)]; ring
    rw [hc] at e
    have p1 : (3 : ℚ) ^ (3 * k + 1) = 3 ^ (3 * (k - i) + 1) * 3 ^ (3 * i) := by
      rw [← pow_add]; congr 1; omega
    have p3 : (3 : ℚ) ^ (H + 1 + k) * 3 ^ (2 * i) = 3 * (3 ^ (H + (k - i)) * 3 ^ (3 * i)) := by
      rw [← pow_add, ← pow_add, ← pow_succ']; congr 1; omega
    have hC : (3 : ℚ) ^ (2 * i) ≠ 0 := pow_ne_zero _ (by norm_num)
    apply mul_right_cancel₀ hC
    rw [p1]
    linear_combination
      (3 ^ (3 * (k - i) + 1) * 3 ^ (3 * i) * (T (H + (k - i)) H : ℚ)) * hm
        + (3 * c i * 3 ^ (3 * i)) * e
        - (c i * (Q (k - i)).eval ((H : ℚ) + k - i)) * p3

/-- Levels `0 … K` all in grand form. -/
def grandOK (Q : ℕ → Polynomial ℚ) (K : ℕ) : Prop := ∀ i, i ≤ K → GrandForm i (Q i)

/-- `μ_0 … μ_K` all known: `μ_i·3^(2i) = 3·c_i`. -/
def muOK (c : ℕ → ℚ) (K : ℕ) : Prop := ∀ i, i ≤ K → mu i * 3 ^ (2 * i) = 3 * c i

/-- One level up: `mu_step` then `grand_step`. -/
theorem level_step (k : ℕ) (hk : 1 ≤ k) (Q : ℕ → Polynomial ℚ) (c : ℕ → ℚ)
    (hg : grandOK Q (k - 1)) (hm : muOK c (k - 1))
    (hstair : ∀ x : ℚ, (Q k).eval (x + 1) =
      ∑ i ∈ Finset.range (k + 1), c i * (Q (k - i)).eval (x - i))
    (hanchor : (3 : ℚ) ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) =
      (Q k).eval ((2 * k + 1 : ℕ) : ℚ) * 3 ^ (2 * k + 1))
    (hnum : (T (2 * k + 2) (k + 2) : ℚ) * 3 ^ (2 * k) = 3 * c k * 3 ^ k +
      ∑ i ∈ Finset.range k, 3 * c i * 3 ^ (2 * k - 2 * i) *
        ((Q (k - i)).eval ((k + 1 + (k - i) : ℕ) : ℚ) * 3 ^ (k + 1 + (k - i))
          / 3 ^ (3 * (k - i) + 1))) :
    grandOK Q k ∧ muOK c k := by
  have hlow : ∀ i, 1 ≤ i → i ≤ k → GrandForm (k - i) (Q (k - i)) :=
    fun i h1 _ => hg (k - i) (by omega)
  have hmu' : ∀ i, i < k → mu i * 3 ^ (2 * i) = 3 * c i := fun i hi => hm i (by omega)
  have hk' := mu_step k Q c hlow hmu' hanchor hnum
  have hmu : ∀ i, i ≤ k → mu i * 3 ^ (2 * i) = 3 * c i := fun i hi => by
    rcases Nat.lt_or_eq_of_le hi with h | rfl
    · exact hmu' i h
    · exact hk'
  have hG := grand_step k Q c hlow hmu hstair hanchor
  refine ⟨fun i hi => ?_, hmu⟩
  rcases Nat.lt_or_eq_of_le hi with h | rfl
  · exact hg i (by omega)
  · exact hG

/-! ## The data: `c_k` and the anchor cells (`Pk` is `Pin.lean`'s) -/

/-- `c_i = μ_i·3^(2i-1)`, the integer staircase coefficients, `i ≤ 18`. -/
def cTab : ℕ → ℚ
  | 0 => 1
  | 1 => 25
  | 2 => 833
  | 3 => 32708
  | 4 => 1426141
  | 5 => 66608903
  | 6 => 3265287780
  | 7 => 165921882171
  | 8 => 8666832237591
  | 9 => 462665755865681
  | 10 => 25137023928857275
  | 11 => 1385671259198548241
  | 12 => 77319304617990777833
  | 13 => 4359188101895471675368
  | 14 => 247962796972892838442550
  | 15 => 14214323567027194988223213
  | 16 => 820375357941284927401273554
  | 17 => 47632676413158811686709315719
  | 18 => 2780470639303344734283777988650
  | _ => 0

/-- The first anchor cell of level `k`: `A_k = T(2k+1, k+1)`, enumerated. -/
def anchorA : ℕ → ℕ
  | 1 => 10
  | 2 => 248
  | 3 => 7898
  | 4 => 278240
  | 5 => 10311170
  | 6 => 393543824
  | 7 => 15308484950
  | 8 => 603392972436
  | 9 => 24014057424024
  | 10 => 962797249464752
  | 11 => 38826609174639928
  | 12 => 1573134737210737385
  | 13 => 63986427407097237332
  | 14 => 2611110015255604740530
  | 15 => 106848447386284024770292
  | 16 => 4382793740312244017806517
  | 17 => 180152359823857046862682314
  | 18 => 7418664369542642927200487045
  | _ => 0

/-- The second anchor cell of level `k`: `B_k = T(2k+2, k+2)`, enumerated. -/
def anchorB : ℕ → ℕ
  | 1 => 55
  | 2 => 1480
  | 3 => 47066
  | 4 => 1631340
  | 5 => 59434367
  | 6 => 2234817674
  | 7 => 85849256593
  | 8 => 3348606811298
  | 9 => 132107598093637
  | 10 => 5257610926802452
  | 11 => 210692983396251014
  | 12 => 8490578913536448064
  | 13 => 343733831675681363476
  | 14 => 13969442417594351366268
  | 15 => 569579285523233406028051
  | 16 => 23288787870043631158670332
  | 17 => 954543410624801880699125196
  | 18 => 39207474138446972682720171554
  | _ => 0

/-- The enumerated cells the pinning of `P_1 … P_18` takes as input: two per
level, `A_k = T(2k+1, k+1)` and `B_k = T(2k+2, k+2)`, all with `H ≤ 20`. -/
def BankedAnchors : Prop :=
  ∀ k, 1 ≤ k → k ≤ 18 → T (2 * k + 1) (k + 1) = anchorA k ∧ T (2 * k + 2) (k + 2) = anchorB k

/-! ## The per-level arithmetic -/

set_option maxHeartbeats 1600000 in
-- 18 levels of `norm_num` on degree-18 polynomials with 30-digit coefficients
/-- The staircase as a polynomial identity, `P_k(x+1) = Σ c_i·P_{k-i}(x-i)`. -/
lemma stair_check : ∀ k, 1 ≤ k → k ≤ 18 → ∀ x : ℚ,
    (Pk k).eval (x + 1) = ∑ i ∈ Finset.range (k + 1), cTab i * (Pk (k - i)).eval (x - i) := by
  intro k h1 h2 x
  interval_cases k <;>
    norm_num [Finset.sum_range_succ, Pk, cTab, prodPoly_eval] <;>
    ring

set_option maxHeartbeats 1600000 in
-- 18 levels of `norm_num` on up-to-30-digit anchor values
/-- `P_k` agrees with the anchor `A_k`. -/
lemma anchor_check (hA : BankedAnchors) : ∀ k, 1 ≤ k → k ≤ 18 →
    (3 : ℚ) ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) =
      (Pk k).eval ((2 * k + 1 : ℕ) : ℚ) * 3 ^ (2 * k + 1) := by
  intro k h1 h2
  rw [(hA k h1 h2).1]
  interval_cases k <;>
    norm_num [Pk, anchorA, prodPoly_eval]

set_option maxHeartbeats 1600000 in
-- 18 levels of `norm_num` on sums of up to 18 big rationals
/-- The anchor `B_k` solves the staircase at `H = k+1` with `μ_k = 3·c_k/3^(2k)`. -/
lemma num_check (hA : BankedAnchors) : ∀ k, 1 ≤ k → k ≤ 18 →
    (T (2 * k + 2) (k + 2) : ℚ) * 3 ^ (2 * k) = 3 * cTab k * 3 ^ k +
      ∑ i ∈ Finset.range k, 3 * cTab i * 3 ^ (2 * k - 2 * i) *
        ((Pk (k - i)).eval ((k + 1 + (k - i) : ℕ) : ℚ) * 3 ^ (k + 1 + (k - i))
          / 3 ^ (3 * (k - i) + 1)) := by
  intro k h1 h2
  rw [(hA k h1 h2).2]
  interval_cases k <;>
    norm_num [Finset.sum_range_succ, Pk, cTab, anchorB, prodPoly_eval]

/-! ## The climb -/

/-- Level `0`: `3·T(H, H) = 1·3^H`, from `T(n,n) = 3^(n-1)`. -/
lemma grand_zero : GrandForm 0 (Pk 0) := by
  intro H hH
  simp only [Nat.cast_zero, add_zero, Nat.mul_zero, Nat.zero_add, pow_one, Pk, prodPoly_eval]
  rw [T_diag_pow H hH, show (H : ℤ) - 1 = ((H - 1 : ℕ) : ℤ) from by omega, zpow_natCast,
    show (3 : ℚ) ^ H = 3 * 3 ^ (H - 1) from by rw [← pow_succ']; congr 1; omega]
  norm_num

/-- Level `0`: `P_0 = 1` and `μ_0`. -/
theorem grand_base : grandOK Pk 0 ∧ muOK cTab 0 := by
  refine ⟨fun i hi => ?_, fun i hi => ?_⟩
  · interval_cases i; exact grand_zero
  · interval_cases i; rw [mu_zero]; norm_num [cTab]

/-- **`P_0 … P_18` and `μ_0 … μ_18`**, from the anchors: level `0` is
`grand_base`, each later level one `level_step`. -/
theorem grand_all (hA : BankedAnchors) : ∀ k, k ≤ 18 → grandOK Pk k ∧ muOK cTab k := by
  intro k
  induction k with
  | zero => exact fun _ => grand_base
  | succ k ih =>
    intro hk
    obtain ⟨hg, hm⟩ := ih (by omega)
    exact level_step (k + 1) (by omega) Pk cTab (by rwa [Nat.add_sub_cancel])
      (by rwa [Nat.add_sub_cancel]) (stair_check (k + 1) (by omega) hk)
      (anchor_check hA (k + 1) (by omega) hk) (num_check hA (k + 1) (by omega) hk)

/-- **`P_k` is explicitly known for `k ≤ 18`**, production form. -/
theorem Pk_prod (hA : BankedAnchors) (k : ℕ) (hk : k ≤ 18) :
    ∀ n : ℕ, 2 * k + 1 ≤ n →
      (T n (n - k) : ℚ) = (Pk k).eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k) :=
  grand_to_prod ((grand_all hA k hk).1 k le_rfl)

/-! ## Levels `1` and `2` unconditionally

The climb's first two levels need four onset cells, `T(3,2)`, `T(4,3)`,
`T(5,3)` and `T(6,4)`, all of which the kernel decides (`Enum.lean`,
`EnumData.lean`), so `P_1` and `P_2` hold outright. `P1_closed` of
`Pin.lean` is the Lagrange route to the first; this is the staircase route to
both, and `P2_closed` is the `k = 2` law in its human form. -/

/-- The climb to level `2`, from the kernel-decided cells. -/
theorem grand_two : grandOK Pk 2 ∧ muOK cTab 2 := by
  have h1 : grandOK Pk 1 ∧ muOK cTab 1 :=
    level_step 1 (by norm_num) Pk cTab grand_base.1 grand_base.2
      (stair_check 1 (by norm_num) (by norm_num))
      (by norm_num [T_3_2, Pk, prodPoly_eval])
      (by norm_num [Finset.sum_range_succ, T_4_3, Pk, cTab, prodPoly_eval])
  exact level_step 2 (by norm_num) Pk cTab h1.1 h1.2 (stair_check 2 (by norm_num) (by norm_num))
    (by norm_num [Enum.T_5_3, Pk, prodPoly_eval])
    (by norm_num [Finset.sum_range_succ, Enum.T_6_4, Pk, cTab, prodPoly_eval])

/-- **`k = 2` diagonal, unconditional** (production form). -/
theorem P2_pinned : ∀ n : ℕ, 2 * 2 + 1 ≤ n →
    (T n (n - 2) : ℚ) = (Pk 2).eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 2) :=
  grand_to_prod (grand_two.1 2 le_rfl)

/-- **`k = 2` diagonal, human form**:
`T(n, n-2) = ½(625n² - 2459n + 1134)·3^(n-7)` for `n ≥ 5`. -/
theorem P2_closed (n : ℕ) (hn : 5 ≤ n) :
    (T n (n - 2) : ℚ)
      = (1 / 2) * (625 * (n : ℚ) ^ 2 - 2459 * (n : ℚ) + 1134) * (3 : ℚ) ^ ((n : ℤ) - 7) := by
  have h := P2_pinned n hn
  simp only [Pk, prodPoly_eval] at h
  norm_num at h ⊢
  rw [h]; ring_nf

end Polyplets
