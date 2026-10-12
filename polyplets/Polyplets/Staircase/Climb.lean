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
import Polyplets.Staircase.Diagonal
import Polyplets.EnumData
import Polyplets.DiagonalPolys

/-!
# The diagonal polynomials `P_0 … P_18`, determined level by level

`T_staircase` says one transfer step multiplies the diagonal family by the
fixed series `μ`:

`T(H+1+k, H+1) = Σ_{i ≤ k} μ_i · T(H+k-i, H)`.

Two consequences, each a single theorem here rather than one copy per level:

* `isDiagonalPolyH_of_below`: if `P_{k-i}` is known for `1 ≤ i ≤ k`, and
  `μ_0 … μ_k` are known, then `P_k` is determined by its value at one cell
  `T(2k+1, k+1)`, by induction on `H` through the staircase (`hstair` is the
  staircase as a polynomial identity).
* `mu_eq_of_below`: `μ_k` itself is solved from the staircase at `H = k+1`,
  where the only unknown is `μ_k · T(k+1, k+1) = μ_k · 3^k`; the one new cell
  is `T(2k+2, k+2)`.

Level `0` is `T(n,n) = 3^(n-1)`; every later level is one `climb_step` on
the two onset cells of `enumerated`. The kernel decides the four cells of
levels `1` and `2` (`enumeratedCellsAt_of_le_two`), so `climb k` needs the
cells of levels `3 … k` only, and `P_1`, `P_2` hold outright
(`isDiagonalPoly_P1`, `T_sub_one`, `isDiagonalPoly_P2`, `T_sub_two`); the
other 32 cells are the hypothesis `EnumeratedCells`. The per-level arithmetic
is three lemmas proved by `interval_cases` (`Pk_staircase`, `Pk_eval_cell`,
`mu_eval_cell`).

The climb works in `H`-coordinates with denominators cleared
(`IsDiagonalPolyH`; `isDiagonalPoly_of_H` returns to `IsDiagonalPoly`), and
`μ_i·3^(2i-1)` is an integer (`cInt`): `μ` is carried as `μ_i·3^(2i) = 3·c_i`
so no negative exponent appears.
-/

namespace Polyplets

open Polynomial

/-! ## The law in the climb's coordinates -/

/-- The diagonal law at level `i` in the `H`-coordinates the climb uses,
denominators cleared: `3^(3i+1)·T(H+i, H) = Q(H+i)·3^(H+i)` for all `H ≥ i+1`.
It implies `IsDiagonalPoly i Q` (`isDiagonalPoly_of_H`). -/
def IsDiagonalPolyH (i : ℕ) (Q : Polynomial ℚ) : Prop :=
  ∀ H : ℕ, i + 1 ≤ H →
    (3 : ℚ) ^ (3 * i + 1) * (T (H + i) H : ℚ) = Q.eval ((H : ℚ) + i) * 3 ^ (H + i)

/-- Back to the report's coordinates, `T(n, n-k) = P(n)·3^(n-1-3k)`. -/
lemma isDiagonalPoly_of_H {k : ℕ} {P : Polynomial ℚ} (h : IsDiagonalPolyH k P) :
    IsDiagonalPoly k P := by
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
`k` at its onset, `A_k`, hence `hcell`, the first enumerated cell. -/
theorem mu_eq_of_below (k : ℕ) (Q : ℕ → Polynomial ℚ) (c : ℕ → ℚ)
    (hlow : ∀ i, 1 ≤ i → i ≤ k → IsDiagonalPolyH (k - i) (Q (k - i)))
    (hmu : ∀ i, i < k → mu i * 3 ^ (2 * i) = 3 * c i)
    (hcell : (3 : ℚ) ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) =
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
    rw [T_self (k + 1) (by omega),
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
        exact hcell
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
the staircase as a polynomial identity (`hstair`), the law at level
`k` follows from its value at `A_k = T(2k+1, k+1)` by induction on `H`. -/
theorem isDiagonalPolyH_of_below (k : ℕ) (Q : ℕ → Polynomial ℚ) (c : ℕ → ℚ)
    (hlow : ∀ i, 1 ≤ i → i ≤ k → IsDiagonalPolyH (k - i) (Q (k - i)))
    (hmu : ∀ i, i ≤ k → mu i * 3 ^ (2 * i) = 3 * c i)
    (hstair : ∀ x : ℚ, (Q k).eval (x + 1) =
      ∑ i ∈ Finset.range (k + 1), c i * (Q (k - i)).eval (x - i))
    (hcell : (3 : ℚ) ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) =
      (Q k).eval ((2 * k + 1 : ℕ) : ℚ) * 3 ^ (2 * k + 1)) :
    IsDiagonalPolyH k (Q k) := by
  intro H hH
  induction H, hH using Nat.le_induction with
  | base =>
    rw [show k + 1 + k = 2 * k + 1 from by omega,
      show ((k + 1 : ℕ) : ℚ) + k = ((2 * k + 1 : ℕ) : ℚ) from by push_cast; ring]
    exact hcell
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

/-- Levels `0 … K` all determined (in the climb's coordinates). -/
def IsDiagonalPolyHUpTo (Q : ℕ → Polynomial ℚ) (K : ℕ) : Prop :=
  ∀ i, i ≤ K → IsDiagonalPolyH i (Q i)

/-- `μ_0 … μ_K` all known: `μ_i·3^(2i) = 3·c_i`. -/
def MuEqUpTo (c : ℕ → ℚ) (K : ℕ) : Prop := ∀ i, i ≤ K → mu i * 3 ^ (2 * i) = 3 * c i

/-- One level up: `mu_eq_of_below` then `isDiagonalPolyH_of_below`. -/
theorem climb_step (k : ℕ) (hk : 1 ≤ k) (Q : ℕ → Polynomial ℚ) (c : ℕ → ℚ)
    (hg : IsDiagonalPolyHUpTo Q (k - 1)) (hm : MuEqUpTo c (k - 1))
    (hstair : ∀ x : ℚ, (Q k).eval (x + 1) =
      ∑ i ∈ Finset.range (k + 1), c i * (Q (k - i)).eval (x - i))
    (hcell : (3 : ℚ) ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) =
      (Q k).eval ((2 * k + 1 : ℕ) : ℚ) * 3 ^ (2 * k + 1))
    (hnum : (T (2 * k + 2) (k + 2) : ℚ) * 3 ^ (2 * k) = 3 * c k * 3 ^ k +
      ∑ i ∈ Finset.range k, 3 * c i * 3 ^ (2 * k - 2 * i) *
        ((Q (k - i)).eval ((k + 1 + (k - i) : ℕ) : ℚ) * 3 ^ (k + 1 + (k - i))
          / 3 ^ (3 * (k - i) + 1))) :
    IsDiagonalPolyHUpTo Q k ∧ MuEqUpTo c k := by
  have hlow : ∀ i, 1 ≤ i → i ≤ k → IsDiagonalPolyH (k - i) (Q (k - i)) :=
    fun i h1 _ => hg (k - i) (by omega)
  have hmu' : ∀ i, i < k → mu i * 3 ^ (2 * i) = 3 * c i := fun i hi => hm i (by omega)
  have hk' := mu_eq_of_below k Q c hlow hmu' hcell hnum
  have hmu : ∀ i, i ≤ k → mu i * 3 ^ (2 * i) = 3 * c i := fun i hi => by
    rcases Nat.lt_or_eq_of_le hi with h | rfl
    · exact hmu' i h
    · exact hk'
  have hG := isDiagonalPolyH_of_below k Q c hlow hmu hstair hcell
  refine ⟨fun i hi => ?_, hmu⟩
  rcases Nat.lt_or_eq_of_le hi with h | rfl
  · exact hg i (by omega)
  · exact hG

/-! ## The data: `c_k` and the enumerated cells (`Pk` is `DiagonalPolys.lean`'s) -/

/-- `c_i = μ_i·3^(2i-1)`, the integer staircase coefficients, `i ≤ 18`. -/
def cInt : ℕ → ℚ
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

/-- **The 36 onset cells** the climb runs on: for each level `k = 1 … 18`
the first two cells of diagonal `k`, `T(2k+1, k+1)` and `T(2k+2, k+2)`, with
the values the engine enumerated (`results/triangle.txt`; every one has
`H ≤ 20`). `0` elsewhere. The kernel decides the four of levels `1` and `2`;
the other 32 are the hypothesis `EnumeratedCells`. -/
def enumerated : ℕ → ℕ → ℕ
  | 3, 2 => 10
  | 4, 3 => 55
  | 5, 3 => 248
  | 6, 4 => 1480
  | 7, 4 => 7898
  | 8, 5 => 47066
  | 9, 5 => 278240
  | 10, 6 => 1631340
  | 11, 6 => 10311170
  | 12, 7 => 59434367
  | 13, 7 => 393543824
  | 14, 8 => 2234817674
  | 15, 8 => 15308484950
  | 16, 9 => 85849256593
  | 17, 9 => 603392972436
  | 18, 10 => 3348606811298
  | 19, 10 => 24014057424024
  | 20, 11 => 132107598093637
  | 21, 11 => 962797249464752
  | 22, 12 => 5257610926802452
  | 23, 12 => 38826609174639928
  | 24, 13 => 210692983396251014
  | 25, 13 => 1573134737210737385
  | 26, 14 => 8490578913536448064
  | 27, 14 => 63986427407097237332
  | 28, 15 => 343733831675681363476
  | 29, 15 => 2611110015255604740530
  | 30, 16 => 13969442417594351366268
  | 31, 16 => 106848447386284024770292
  | 32, 17 => 569579285523233406028051
  | 33, 17 => 4382793740312244017806517
  | 34, 18 => 23288787870043631158670332
  | 35, 18 => 180152359823857046862682314
  | 36, 19 => 954543410624801880699125196
  | 37, 19 => 7418664369542642927200487045
  | 38, 20 => 39207474138446972682720171554
  | _, _ => 0

/-- `T` agrees with the enumerated table at the two cells of level `k`. -/
def EnumeratedCellsAt (k : ℕ) : Prop :=
  T (2 * k + 1) (k + 1) = enumerated (2 * k + 1) (k + 1) ∧
    T (2 * k + 2) (k + 2) = enumerated (2 * k + 2) (k + 2)

/-- **The hypothesis of the climb**: `T` agrees with the enumerated table at the
32 cells of levels `3 … 18`. Nothing in Lean certifies these values; they are
the engine's. -/
def EnumeratedCells : Prop := ∀ k, 3 ≤ k → k ≤ 18 → EnumeratedCellsAt k

/-- The cells of levels `1` and `2`, `T(3,2)`, `T(4,3)`, `T(5,3)`, `T(6,4)`,
the kernel decides (`Enum.lean`, `EnumData.lean`). -/
lemma enumeratedCellsAt_of_le_two : ∀ k, 1 ≤ k → k ≤ 2 → EnumeratedCellsAt k := by
  intro k h1 h2
  interval_cases k
  · exact ⟨T_3_2, T_4_3⟩
  · exact ⟨Enum.T_5_3, Enum.T_6_4⟩

/-! ## The per-level arithmetic -/

set_option maxHeartbeats 1600000 in
-- 18 levels of `norm_num` on degree-18 polynomials with 30-digit coefficients
/-- The staircase as a polynomial identity, `P_k(x+1) = Σ c_i·P_{k-i}(x-i)`. -/
lemma Pk_staircase : ∀ k, 1 ≤ k → k ≤ 18 → ∀ x : ℚ,
    (Pk k).eval (x + 1) = ∑ i ∈ Finset.range (k + 1), cInt i * (Pk (k - i)).eval (x - i) := by
  intro k h1 h2 x
  interval_cases k <;>
    norm_num [Finset.sum_range_succ, Pk, cInt, ofNumerators_eval] <;>
    ring

set_option maxHeartbeats 1600000 in
-- 18 levels of `norm_num` on up-to-30-digit cell values
/-- `P_k` agrees with the cell `T(2k+1, k+1)`. -/
lemma Pk_eval_cell : ∀ k, 1 ≤ k → k ≤ 18 → EnumeratedCellsAt k →
    (3 : ℚ) ^ (3 * k + 1) * (T (2 * k + 1) (k + 1) : ℚ) =
      (Pk k).eval ((2 * k + 1 : ℕ) : ℚ) * 3 ^ (2 * k + 1) := by
  intro k h1 h2 hc
  rw [hc.1]
  interval_cases k <;>
    norm_num [Pk, enumerated, ofNumerators_eval]

set_option maxHeartbeats 1600000 in
-- 18 levels of `norm_num` on sums of up to 18 big rationals
/-- The cell `T(2k+2, k+2)` solves the staircase at `H = k+1` with
`μ_k = 3·c_k/3^(2k)`. -/
lemma mu_eval_cell : ∀ k, 1 ≤ k → k ≤ 18 → EnumeratedCellsAt k →
    (T (2 * k + 2) (k + 2) : ℚ) * 3 ^ (2 * k) = 3 * cInt k * 3 ^ k +
      ∑ i ∈ Finset.range k, 3 * cInt i * 3 ^ (2 * k - 2 * i) *
        ((Pk (k - i)).eval ((k + 1 + (k - i) : ℕ) : ℚ) * 3 ^ (k + 1 + (k - i))
          / 3 ^ (3 * (k - i) + 1)) := by
  intro k h1 h2 hc
  rw [hc.2]
  interval_cases k <;>
    norm_num [Finset.sum_range_succ, Pk, cInt, enumerated, ofNumerators_eval]

/-! ## The climb -/

/-- Level `0`: `3·T(H, H) = 1·3^H`, from `T(n,n) = 3^(n-1)`. -/
lemma isDiagonalPolyH_zero : IsDiagonalPolyH 0 (Pk 0) := by
  intro H hH
  simp only [Nat.cast_zero, add_zero, Nat.mul_zero, Nat.zero_add, pow_one, Pk, ofNumerators_eval]
  rw [T_self H hH, show (H : ℤ) - 1 = ((H - 1 : ℕ) : ℤ) from by omega, zpow_natCast,
    show (3 : ℚ) ^ H = 3 * 3 ^ (H - 1) from by rw [← pow_succ']; congr 1; omega]
  norm_num

/-- Level `0`: `P_0 = 1` and `μ_0`. -/
theorem climb_zero : IsDiagonalPolyHUpTo Pk 0 ∧ MuEqUpTo cInt 0 := by
  refine ⟨fun i hi => ?_, fun i hi => ?_⟩
  · interval_cases i; exact isDiagonalPolyH_zero
  · interval_cases i; rw [mu_zero]; norm_num [cInt]

/-- **The climb: `P_0 … P_k` and `μ_0 … μ_k`**, for `k ≤ 18`, given the
enumerated cells of levels `3 … k`: level `0` is `climb_zero`, each later level
one `climb_step` on its two cells, the kernel's for levels `1` and `2`. -/
theorem climb (k : ℕ) (hk : k ≤ 18) (hcells : ∀ i, 3 ≤ i → i ≤ k → EnumeratedCellsAt i) :
    IsDiagonalPolyHUpTo Pk k ∧ MuEqUpTo cInt k := by
  induction k with
  | zero => exact climb_zero
  | succ k ih =>
    have hc : EnumeratedCellsAt (k + 1) := by
      rcases Nat.lt_or_ge (k + 1) 3 with h | h
      · exact enumeratedCellsAt_of_le_two (k + 1) (by omega) (by omega)
      · exact hcells (k + 1) h le_rfl
    obtain ⟨hg, hm⟩ := ih (by omega) fun i h3 hi => hcells i h3 (by omega)
    exact climb_step (k + 1) (by omega) Pk cInt (by rwa [Nat.add_sub_cancel])
      (by rwa [Nat.add_sub_cancel]) (Pk_staircase (k + 1) (by omega) hk)
      (Pk_eval_cell (k + 1) (by omega) hk hc) (mu_eval_cell (k + 1) (by omega) hk hc)

/-- **`P_k` is explicitly known for `k ≤ 18`**: `Pk k` satisfies the law, given
the 32 enumerated cells. -/
theorem isDiagonalPoly_Pk (hcells : EnumeratedCells) (k : ℕ) (hk : k ≤ 18) :
    IsDiagonalPoly k (Pk k) :=
  isDiagonalPoly_of_H ((climb k hk fun i h3 hi => hcells i h3 (by omega)).1 k le_rfl)

/-! ## The `k = 1` and `k = 2` diagonals in closed form -/

/-- **`P₁ = Pk 1`, unconditionally**: the climb to level `1` needs no
enumerated cell. -/
theorem isDiagonalPoly_P1 : IsDiagonalPoly 1 (Pk 1) :=
  isDiagonalPoly_of_H ((climb 1 (by norm_num) fun _ h3 hi => absurd (h3.trans hi) (by norm_num)).1
    1 le_rfl)

/-- **`T(n, n-1) = (25n - 45)·3^(n-4)`** for `n ≥ 3`: the `k = 1` diagonal, the
report's worked example. -/
theorem T_sub_one (n : ℕ) (hn : 3 ≤ n) :
    (T n (n - 1) : ℚ) = (25 * (n : ℚ) - 45) * (3 : ℚ) ^ ((n : ℤ) - 4) := by
  have h := isDiagonalPoly_P1 n hn
  simp only [Pk, ofNumerators_eval] at h
  norm_num at h ⊢
  rw [h]; ring_nf

/-- **`P₂ = Pk 2`, unconditionally**: the climb to level `2` needs no
enumerated cell. -/
theorem isDiagonalPoly_P2 : IsDiagonalPoly 2 (Pk 2) :=
  isDiagonalPoly_of_H ((climb 2 (by norm_num) fun _ h3 hi => absurd (h3.trans hi) (by norm_num)).1
    2 le_rfl)

/-- **`T(n, n-2) = ½(625n² - 2459n + 1134)·3^(n-7)`** for `n ≥ 5`: the `k = 2`
diagonal. -/
theorem T_sub_two (n : ℕ) (hn : 5 ≤ n) :
    (T n (n - 2) : ℚ)
      = (1 / 2) * (625 * (n : ℚ) ^ 2 - 2459 * (n : ℚ) + 1134) * (3 : ℚ) ^ ((n : ℤ) - 7) := by
  have h := isDiagonalPoly_P2 n hn
  simp only [Pk, ofNumerators_eval] at h
  norm_num at h ⊢
  rw [h]; ring_nf

end Polyplets
