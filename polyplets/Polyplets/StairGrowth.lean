/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Fekete
import Polyplets.StairAnimals

/-!
# `µ`: the staircase king animals have a growth constant

`StairAnimals.lean` proves the combinatorial core of
`results/subclasses.md` Lemma 3 — the column-join stays in the class and
is injective once both areas are fixed. This file is the counting layer on top
of it, and the Fekete step:

* `M n` — the number of staircase king animals of area `n`, up to translation;
* `M_supermul` — **Lemma 3**, `M i * M j ≤ M (i + j)`, for all `i` and `j`;
* `M_tendsto` — `µ = lim M(n)^{1/n}` exists;
* `M_le_mu_pow` — `M n ≤ µⁿ` for every `n`, the limit-is-supremum half;
* `mu_gt_of_banked` — `3.1234 < µ`, **conditional** on the banked
  `M 700` of `results/mk_stair_terms_n700.txt`.

The last two are the point. `make gate-middle-kingdom` checks
supermultiplicativity on 700 computed terms; `M_supermul` makes it a theorem for
all `i` and `j`, and Fekete then converts *any* banked term into a rigorous
floor under `µ` rather than an extrapolation towards it.

What is deliberately not here: Lemma 1 (the phase split), Lemma 2 (the stack
bound), the geometric layer, and the squeeze that turns the three into
Proposition 6. Those stay paper proofs; see `docs/lean-staircase-growth-brief.md`
for why this slice and no more.

## Counting without a bijection

`M n` is `Nat.card` of a subtype, so it needs the subtype to be finite before it
means anything. Both finiteness and the exponential ceiling come from one
construction, `cand p n`: an explicit `Finset` of *all* lists that could be a
legal continuation to the right of a column of height `p` with `n` cells left to
spend. It over-counts: it enforces the height and offset ranges but none of the
staircase inequalities. It is finite, it contains every valid list, and its
cardinality obeys

    |cand p n| ≤ (p + 1) · 4ⁿ

by induction. That is the composition-times-offsets count (`2^{n-1}` height
compositions, `∏ (hⱼ + 1) ≤ 2ⁿ` offsets) done as a recursion instead of as a
product formula, which keeps it to one arithmetic lemma (`sum_pow_bound`).
-/

namespace Polyplets.Stair

open Finset

/-! ## The candidate over-count -/

/-- Every list that *could* follow a column of height `p` and use exactly `n`
cells: a first column of height `k + 1 ≤ n` and offset `d ≤ p`, then a legal
continuation of the remaining `n - k - 1` cells. No staircase inequality is
enforced: this is a superset chosen so that its cardinality is easy to bound. -/
def cand : ℕ → ℕ → Finset (List Col)
  | _, 0 => {[]}
  | p, (n + 1) =>
      (range (n + 1)).biUnion fun k =>
        (range (p + 1)).biUnion fun d =>
          (cand (k + 1) (n - k)).image (fun t => ((k + 1, d) : Col) :: t)
termination_by _ n => n
decreasing_by omega

/-- Every legal continuation is a candidate. -/
theorem mem_cand : ∀ (l : List Col) (p : ℕ), ValidFrom p l → l ∈ cand p (area l)
  | [], p, _ => by simp [area, cand]
  | c :: t, p, hv => by
      have h1 : 1 ≤ c.1 := hv.1
      have hd : c.2 ≤ p := hv.2.1
      have ht : t ∈ cand c.1 (area t) := mem_cand t c.1 hv.2.2.2
      obtain ⟨k, hk⟩ : ∃ k, c.1 = k + 1 := ⟨c.1 - 1, by omega⟩
      have harea : area (c :: t) = (k + area t) + 1 := by
        simp only [area_cons, hk]; omega
      rw [harea, cand]
      refine mem_biUnion.mpr ⟨k, mem_range.mpr (by omega), ?_⟩
      refine mem_biUnion.mpr ⟨c.2, mem_range.mpr (by omega), ?_⟩
      refine mem_image.mpr ⟨t, ?_, ?_⟩
      · have hsub : k + area t - k = area t := by omega
        rw [hsub, ← hk]
        exact ht
      · exact congrArg (fun s => s :: t) (Prod.ext hk.symm rfl)

/-- The arithmetic behind the `4ⁿ` ceiling: `∑_{k<n+1} (k+2) 4^{n−k} ≤ 4^{n+1}`,
with the slack `n + 2` that makes the induction go through. -/
theorem sum_pow_bound : ∀ n : ℕ,
    (∑ k ∈ range (n + 1), (k + 2) * 4 ^ (n - k)) + (n + 2) ≤ 4 ^ (n + 1)
  | 0 => by norm_num
  | (n + 1) => by
      have ih := sum_pow_bound n
      have hterm : ∑ k ∈ range (n + 1), (k + 2) * 4 ^ (n + 1 - k)
          = 4 * ∑ k ∈ range (n + 1), (k + 2) * 4 ^ (n - k) := by
        rw [Finset.mul_sum]
        refine Finset.sum_congr rfl fun k hk => ?_
        have hk' : k ≤ n := Nat.lt_succ_iff.mp (mem_range.mp hk)
        have hpow : n + 1 - k = (n - k) + 1 := by omega
        rw [hpow, pow_succ]
        ring
      have h4 : (4 : ℕ) ^ (n + 2) = 4 * 4 ^ (n + 1) := by ring
      rw [Finset.sum_range_succ, hterm]
      simp only [Nat.sub_self, pow_zero, mul_one]
      omega

/-- **The candidate count is exponential.** `(p + 1) · 4ⁿ`: the `p + 1` is the
offset freedom of the first column, and each further column pays for its own
offsets out of its own height. -/
theorem card_cand : ∀ (n p : ℕ), (cand p n).card ≤ (p + 1) * 4 ^ n
  | 0, p => by simp [cand]
  | (n + 1), p => by
      rw [cand]
      calc ((range (n + 1)).biUnion fun k => (range (p + 1)).biUnion fun d =>
              (cand (k + 1) (n - k)).image (fun t => ((k + 1, d) : Col) :: t)).card
          ≤ ∑ k ∈ range (n + 1), ((range (p + 1)).biUnion fun d =>
              (cand (k + 1) (n - k)).image (fun t => ((k + 1, d) : Col) :: t)).card :=
            Finset.card_biUnion_le
        _ ≤ ∑ k ∈ range (n + 1), (p + 1) * ((k + 1 + 1) * 4 ^ (n - k)) := by
            refine Finset.sum_le_sum fun k _ => ?_
            calc ((range (p + 1)).biUnion fun d =>
                    (cand (k + 1) (n - k)).image (fun t => ((k + 1, d) : Col) :: t)).card
                ≤ ∑ _d ∈ range (p + 1),
                    ((cand (k + 1) (n - k)).image
                      (fun t => ((k + 1, _d) : Col) :: t)).card := Finset.card_biUnion_le
              _ ≤ ∑ _d ∈ range (p + 1), (k + 1 + 1) * 4 ^ (n - k) :=
                  Finset.sum_le_sum fun _ _ =>
                    le_trans Finset.card_image_le (card_cand (n - k) (k + 1))
              _ = (p + 1) * ((k + 1 + 1) * 4 ^ (n - k)) := by
                  rw [Finset.sum_const, Finset.card_range, smul_eq_mul]
        _ = (p + 1) * ∑ k ∈ range (n + 1), (k + 2) * 4 ^ (n - k) := by
            rw [Finset.mul_sum]
        _ ≤ (p + 1) * 4 ^ (n + 1) :=
            Nat.mul_le_mul_left _ (by have := sum_pow_bound n; omega)

/-- A staircase animal is in particular a legal continuation of a height-`0`
column: pinning the first offset to `0` is exactly what `ValidFrom 0` asks. -/
theorem validFrom_zero_of_valid : ∀ {l : List Col}, Valid l → ValidFrom 0 l
  | _ :: _, hv => ⟨hv.1, le_of_eq hv.2.1, Nat.zero_le _, hv.2.2⟩

/-- The staircase animals of a fixed area form a finite set. -/
theorem setM_finite (n : ℕ) : {l : List Col | Valid l ∧ area l = n}.Finite := by
  refine Set.Finite.subset (cand 0 n).finite_toSet ?_
  rintro l ⟨hv, ha⟩
  have hm := mem_cand l 0 (validFrom_zero_of_valid hv)
  rw [ha] at hm
  exact Finset.mem_coe.mpr hm

/-! ## `M n` and Lemma 3 -/

/-- **`M n`** — staircase king animals of area `n`, up to translation.
`Nat.card` returns the junk value `0` on an infinite type; `setM_finite` is what
rules that out here. -/
noncomputable def M (n : ℕ) : ℕ := Nat.card {l : List Col // Valid l ∧ area l = n}

/-- `Nat.card` of the subtype is `ncard` of the set, the form the `Finset`
arguments below want. -/
theorem M_eq_ncard (n : ℕ) : M n = {l : List Col | Valid l ∧ area l = n}.ncard :=
  Nat.card_coe_set_eq _

/-- `M n` as a `Finset` cardinality — `a_supermul`'s `key`, one encoding over. -/
theorem M_eq_card (n : ℕ) : M n = (setM_finite n).toFinset.card := by
  rw [M_eq_ncard, Set.ncard_eq_toFinset_card _ (setM_finite n)]

/-- There is at least one staircase animal of every positive area: the single
column. -/
theorem M_pos {n : ℕ} (hn : 1 ≤ n) : 1 ≤ M n := by
  rw [M_eq_card]
  refine Finset.card_pos.mpr ⟨[(n, 0)], ?_⟩
  rw [Set.Finite.mem_toFinset]
  exact ⟨⟨hn, rfl, trivial⟩, by simp [area]⟩

/-- `M 0 = 0`: every column is nonempty, so there is no animal of area zero.
(The paper's `M(0) = 1` convention is a bookkeeping choice for Lemma 1's
convolution; nothing here needs it, and `0` is what the encoding gives.) -/
theorem M_zero : M 0 = 0 := by
  rw [M_eq_card, Finset.card_eq_zero, Finset.eq_empty_iff_forall_notMem]
  rintro l hl
  rw [Set.Finite.mem_toFinset] at hl
  obtain ⟨hv, ha⟩ := hl
  match l, hv with
  | c :: t, hv =>
    have h1 : 1 ≤ c.1 := hv.1
    simp only [area_cons] at ha
    omega

/-- **The `4ⁿ` ceiling.** Every staircase animal of area `n` is a candidate from
a height-`0` predecessor, and there are at most `4ⁿ` of those. -/
theorem M_le_pow (n : ℕ) : M n ≤ 4 ^ n := by
  rw [M_eq_card]
  have hsub : (setM_finite n).toFinset ⊆ cand 0 n := by
    intro l hl
    rw [Set.Finite.mem_toFinset] at hl
    have hm := mem_cand l 0 (validFrom_zero_of_valid hl.1)
    rwa [hl.2] at hm
  calc (setM_finite n).toFinset.card ≤ (cand 0 n).card := Finset.card_le_card hsub
    _ ≤ (0 + 1) * 4 ^ n := card_cand n 0
    _ = 4 ^ n := by ring

/-- **Lemma 3** (`results/subclasses.md`): the staircase count is
supermultiplicative, on the nose and with no factor. `StairAnimals.lean`'s
`join_valid` says the join lands in the class and `join_injOn` says the pair is
recovered from the join alone once both areas are fixed; this is those two read
as a cardinality.

Unconditional: at `i = 0` the left side is `M 0 * M j = 0`, exactly as
`a_supermul` degenerates. -/
theorem M_supermul (i j : ℕ) : M i * M j ≤ M (i + j) := by
  classical
  rw [M_eq_card i, M_eq_card j, M_eq_card (i + j), ← Finset.card_product]
  refine Finset.card_le_card_of_injOn (fun z => join z.1 z.2) ?_ ?_
  · intro z hz
    rw [Finset.mem_coe, Finset.mem_product] at hz
    simp only [Set.Finite.mem_toFinset, Set.mem_setOf_eq] at hz
    rw [Finset.mem_coe, Set.Finite.mem_toFinset, Set.mem_setOf_eq]
    exact ⟨join_valid hz.1.1 hz.2.1, by rw [area_join, hz.1.2, hz.2.2]⟩
  · intro z hz w hw heq
    rw [Finset.mem_coe, Finset.mem_product] at hz hw
    simp only [Set.Finite.mem_toFinset, Set.mem_setOf_eq] at hz hw
    have harea : area z.1 = area w.1 := by rw [hz.1.2, hw.1.2]
    have hj := join_injOn hz.1.1 hz.2.1 hw.1.1 hw.2.1 harea heq
    exact Prod.ext hj.1 hj.2

/-! ## Fekete: the growth constant `µ` -/

/-- The staircase instance of `Fekete.lean`'s ladder. Lemma 3 is the only field
with any content. -/
noncomputable def stairFekete : Fekete where
  f := M
  c := 4
  one_le_c := by norm_num
  supermul := M_supermul
  one_le := M_pos
  ceiling := fun k => by exact_mod_cast M_le_pow k

/-- **The staircase growth constant** `µ = lim M(n)^{1/n}`. The measured value is
`3.128943269730886…` (`results/subclasses.md`); what is proved here is
that the limit exists, plus the two-sided bracket below. -/
noncomputable def mu : ℝ := stairFekete.growth

/-- `µ` is positive. -/
lemma mu_pos : 0 < mu := stairFekete.growth_pos

/-- **`µ` is the limit of `M(n)^{1/n}`.** -/
theorem M_tendsto :
    Filter.Tendsto (fun n => (M n : ℝ) ^ ((n : ℝ)⁻¹)) Filter.atTop (nhds mu) :=
  stairFekete.tendsto

/-- **Fekete's supremum half:** `M n ≤ µⁿ` for *every* `n`, so every computed
term of the staircase sequence is a rigorous lower bound on `µ` rather than an
approximation to it. At `n = 0` the statement reads `0 ≤ 1`. -/
theorem M_le_mu_pow (n : ℕ) : (M n : ℝ) ≤ mu ^ n := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · rw [M_zero]; simp
  · exact stairFekete.le_growth_pow hn

/-- **The upper bound `µ ≤ 4`**, from the candidate ceiling. Crude against the
measured `3.1289…`, and free: it is the ceiling Fekete needed anyway. -/
theorem mu_le : mu ≤ 4 := stairFekete.growth_le

/-! ## The conditional lower bound from the banked term

`M_le_mu_pow` turns any banked term into a floor. The largest one this project
has computed is `M 700`, from `cpp/middle_kingdom_tm.cpp` in `stair` mode
(`results/mk_stair_terms_n700.txt`, log `results/mk_stair_n700.log`). It enters
as an explicit hypothesis, in the `lambda_gt_of_banked` style, so the
computation stays outside the kernel and visible in the statement. -/

set_option linter.style.longLine false in
/-- **The conditional lower bound `3.1234 < µ`, given the banked `M 700`.**
`M 700 ^ (1/700) = 3.1234045…`, so `15617/5000 = 3.1234` is a floor with room to
spare, and `x ↦ x⁷⁰⁰` is strictly monotone on `[0, ∞)`. With `mu_le` this is the
machine-checked bracket `3.1234 < µ ≤ 4`.

The conditionality is real: the hypothesis is a single-source value, produced by
one transfer-matrix run and not independently reproduced, and the bound it buys
is far from the measured `µ = 3.128943269730886…`. It is not an extrapolation:
the inequality direction is `M_le_mu_pow`, a theorem, which is what Lemma 3
buys. The digits appear once, in the statement; the proof carries `M 700` and
rewrites by the hypothesis at the last moment. -/
theorem mu_gt_of_banked (h : M 700 = 17368528651849586692964028326758271833612371383870423413808116889318363599460025100827498779086610136761902989817504169488748816867918876735230734086164154151538989546114696139586414190817304691612024386097843528450235138333808483697230123839488604376917096321409200698726184492443222298900447735379737893097804045322780266978742339265500438636729) : (15617 / 5000 : ℝ) < mu := by
  have hle : (M 700 : ℝ) ≤ mu ^ 700 := M_le_mu_pow 700
  have hnum : (15617 : ℕ) ^ 700 < M 700 * 5000 ^ 700 := by
    rw [h]
    have e1 : (15617 : ℕ) ^ 700 = ((15617 : ℕ) ^ 100) ^ 7 := by rw [← pow_mul]
    have e2 : (5000 : ℕ) ^ 700 = ((5000 : ℕ) ^ 100) ^ 7 := by rw [← pow_mul]
    rw [e1, e2]
    norm_num
  have hnumR : (15617 : ℝ) ^ 700 < (M 700 : ℝ) * (5000 : ℝ) ^ 700 := by
    exact_mod_cast hnum
  have hpow : ((15617 / 5000 : ℝ)) ^ 700 < mu ^ 700 := by
    refine lt_of_lt_of_le ?_ hle
    rw [div_pow, div_lt_iff₀ (by positivity)]
    exact hnumR
  exact lt_of_pow_lt_pow_left₀ 700 (le_of_lt mu_pos) hpow

/-! ## Axiom audit

`AuditOutworks.lean` wraps these in `#guard_msgs`; the plain prints here are the
in-module copies the other growth modules also carry. -/

#print axioms M_supermul
#print axioms M_tendsto
#print axioms M_le_mu_pow
#print axioms mu_le
#print axioms mu_gt_of_banked

end Polyplets.Stair
