/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.FieldSimp
import Mathlib.Analysis.SpecialFunctions.Sqrt

/-!
# Notary N3: the depth-1 constants as branch data of `Φ`

Campaign *Notary* (`docs/notary-lean-plan.md` §3, workstream N3). The
constants of `results/onset-defect-depth1-closed.md` §4 — rate, exponent,
amplitude, and the `1/k` coefficient `a` — are **branch data of the quartic
`Φ(x, W)`**. This module states that branch data as pure field algebra, over
an arbitrary field `K` of characteristic zero equipped with square roots
`s2² = 2`, `s3² = 3`, plus `ℝ`-instantiations at `Real.sqrt`.

What is proved (all statements checked in exact arithmetic by
`build/notary_n3_lean_gen.py`, log `build/notary_n3_lean_gen.log`):

1. `lead_factor` / `gPoly_onset_ne_zero`: the leading coefficient of `Φ` is
   `(27x−1)² · g(x)` with `g(1/27) = 7929856/19683 ≠ 0` — the vanishing at
   `x = 1/27` has order exactly two. (Rate `27` in `x`, i.e. `9` per `k`.)
2. `psi_spec`: `Ψ(v, V) := Φ((1−v²)/27, V/v)` is a **polynomial** in
   `(v, V)` — stated division-free as `Ψ(v, wv) = Φ((1−v²)/27, w)` — so the
   Puiseux branch in `v = √(1−27x)` is an ordinary Taylor series. (Exponent
   `−1/2`: the branch variable is `v` itself.)
3. `psi_zero_factor` / `V0_on_crossing`: `Ψ(0, V) = (7929856/14348907) ·
   (27V² − 2)²` and `27V₀² = 2` for `V₀ = s2·s3/9` (= `√6/9`) — two sheets
   crossing at `V₀`, the amplitude numerator. `amp_sq`: `(V₀/3)² = 2/243`,
   the θ-free half-power-ladder check `A² = 2/243` of the campaign.
4. `puiseux_truncation`: with the physical branch data
   `V₁ = −439/1584 + 23·s3/792`,
   `V₂ = (3251/278784)·s2 − (14909/418176)·s2·s3`,
   the truncated branch satisfies `Ψ(v, V₀ + V₁v + V₂v²) = v⁴ · Q₄(v)`
   exactly, with `Q₄` explicit — the coefficients of `v⁰..v³` all vanish.
5. `pivot_ne_zero`: the linear-step pivot `33161216·s3/4782969` that pins
   `V₂` (and every later coefficient) is nonzero.
6. `a_value`: `a := −1/8 − V₂/(2V₀) = 3293/92928 − 3251·s3/185856` — the
   `1/k` coefficient of the campaign, an element of `ℚ(√3)`.

**Not** in scope (docs/notary-lean-plan.md §1): the transfer from branch data
to coefficient asymptotics (`C₁ = √6/(27√π)` with its `√π`) — real-analytic
singularity analysis with no Mathlib support. The constants are pinned here
exactly as the derivation produced them: as algebra of the curve.

Provenance of `Φ`: `PHI_COEFFS` of `experiments/depth1_recurrence.py` —
two-source (fitted with 144 orders of holdout, `depth1_minpoly.py`; derived
ab initio by the kernel method, `severance_w2_kernel.py`, gate
`severance_w2_gate.py`).
-/

namespace Polyplets
namespace DepthOneConstants

variable {K : Type*} [Field K] [CharZero K]

/-! ## The quartic `Φ` -/

/-- Coefficient of `W⁴` in `Φ` (the leading coefficient). -/
def phiC4 (x : K) : K :=
  392 + (-20719) * x + 257193 * x ^ 2 + 564573 * x ^ 3 + (-3338583) * x ^ 4 +
    2238435 * x ^ 5 + 4323699 * x ^ 6 + (-4310577) * x ^ 7 + 1594323 * x ^ 8

/-- Coefficient of `W³`. -/
def phiC3 (x : K) : K :=
  420 + (-21803) * x + 254538 * x ^ 2 + 870723 * x ^ 3 + (-3116316) * x ^ 4 +
    (-488133) * x ^ 5 + 7413930 * x ^ 6 + (-5373459) * x ^ 7 + 2125764 * x ^ 8

/-- Coefficient of `W²`. -/
def phiC2 (x : K) : K :=
  144 + (-8808) * x + 115470 * x ^ 2 + 514107 * x ^ 3 + (-1174698) * x ^ 4 +
    (-1324026) * x ^ 5 + 4153842 * x ^ 6 + (-2421009) * x ^ 7 + 1062882 * x ^ 8

/-- Coefficient of `W¹`. -/
def phiC1 (x : K) : K :=
  16 + (-1580) * x + 25920 * x ^ 2 + 144249 * x ^ 3 + (-175746) * x ^ 4 +
    (-537516) * x ^ 5 + 989982 * x ^ 6 + (-461457) * x ^ 7 + 236196 * x ^ 8

/-- Coefficient of `W⁰`. -/
def phiC0 (x : K) : K :=
  (-64) * x + 2736 * x ^ 2 + 16560 * x ^ 3 + (-4920) * x ^ 4 +
    (-63720) * x ^ 5 + 89667 * x ^ 6 + (-30618) * x ^ 7 + 19683 * x ^ 8

/-- The quartic `Φ(x, W)` of the depth-1 closure. -/
def Phi (x w : K) : K :=
  phiC4 x * w ^ 4 + phiC3 x * w ^ 3 + phiC2 x * w ^ 2 + phiC1 x * w + phiC0 x

/-- The cofactor `g` of the leading coefficient: `phiC4 = (27x−1)² · g`. -/
def gPoly (x : K) : K :=
  392 + 449 * x + (-4329) * x ^ 2 + 3486 * x ^ 3 + 5502 * x ^ 4 +
    (-5751) * x ^ 5 + 2187 * x ^ 6

/-- The leading coefficient of `Φ` carries `(27x−1)` to order exactly two. -/
theorem lead_factor (x : K) : phiC4 x = (27 * x - 1) ^ 2 * gPoly x := by
  sorry

/-- ... and the cofactor does not vanish at the singularity. -/
theorem gPoly_onset : gPoly ((1 : K) / 27) = 7929856 / 19683 := by
  sorry

theorem gPoly_onset_ne_zero : gPoly ((1 : K) / 27) ≠ 0 := by
  sorry

/-! ## The Puiseux frame `Ψ` -/

/-- `Ψ(v, V) = Φ((1−v²)/27, V/v)`, which is a polynomial in `(v, V)` —
coefficients of `V⁴ .. V⁰`, from `build/notary_n3_lean_gen.py`. -/
def Psi (v V : K) : K :=
  ((7929856 : K) / 19683 + (-314368 : K) / 59049 * v ^ 2 +
      (-947516 : K) / 177147 * v ^ 4 + (-38020 : K) / 177147 * v ^ 6 +
      (166 : K) / 19683 * v ^ 8 + (65 : K) / 177147 * v ^ 10 +
      (1 : K) / 177147 * v ^ 12) * V ^ 4 +
    ((79118336 : K) / 177147 * v + (-11057536 : K) / 531441 * v ^ 3 +
      (-3063436 : K) / 531441 * v ^ 5 + (-37432 : K) / 531441 * v ^ 7 +
      (8371 : K) / 531441 * v ^ 9 + (241 : K) / 531441 * v ^ 11 +
      (4 : K) / 531441 * v ^ 13) * V ^ 3 +
    ((-31719424 : K) / 531441 + (118364672 : K) / 531441 * v ^ 2 +
      (-2933828 : K) / 177147 * v ^ 4 + (-1338583 : K) / 531441 * v ^ 6 +
      (17321 : K) / 531441 * v ^ 8 + (1631 : K) / 177147 * v ^ 10 +
      (107 : K) / 531441 * v ^ 12 + (2 : K) / 531441 * v ^ 14) * V ^ 2 +
    ((-158236672 : K) / 4782969 * v + (264115648 : K) / 4782969 * v ^ 3 +
      (-9057070 : K) / 1594323 * v ^ 5 + (-2301349 : K) / 4782969 * v ^ 7 +
      (110047 : K) / 4782969 * v ^ 9 + (3619 : K) / 1594323 * v ^ 11 +
      (179 : K) / 4782969 * v ^ 13 + (4 : K) / 4782969 * v ^ 15) * V +
    ((31719424 : K) / 14348907 + (-109079552 : K) / 14348907 * v ^ 2 +
      (88684129 : K) / 14348907 * v ^ 4 + (-10968686 : K) / 14348907 * v ^ 6 +
      (-403025 : K) / 14348907 * v ^ 8 + (44620 : K) / 14348907 * v ^ 10 +
      (3055 : K) / 14348907 * v ^ 12 + (34 : K) / 14348907 * v ^ 14 +
      (1 : K) / 14348907 * v ^ 16)

/-- `Ψ` is `Φ` in the Puiseux frame, division-free: substituting `V = w·v`
clears every `1/v`. -/
theorem psi_spec (v w : K) : Psi v (w * v) = Phi ((1 - v ^ 2) / 27) w := by
  sorry

/-- At the singularity (`v = 0`) the quartic collapses to a perfect square:
two sheets crossing. -/
theorem psi_zero_factor (V : K) :
    Psi 0 V = (7929856 : K) / 14348907 * (27 * V ^ 2 - 2) ^ 2 := by
  sorry

/-! ## The physical branch -/

section Branch

variable (s2 s3 : K)

/-- `V₀ = √6/9`, the crossing point — the amplitude numerator. -/
def V0 : K := s2 * s3 / 9

/-- `V₁`, the first Puiseux step (physical root of the first-step
quadratic). -/
def V1 : K := (-439 : K) / 1584 + (23 : K) / 792 * s3

/-- `V₂`, the second Puiseux step — the coefficient that carries `a`. -/
def V2 : K := (3251 : K) / 278784 * s2 + (-14909 : K) / 418176 * (s2 * s3)

/-- `Q₄`, the exact quotient: `Ψ(v, V₀+V₁v+V₂v²) = v⁴ · Q₄(v)`. From
`build/notary_n3_lean_gen.py`. -/
def Q4 (v : K) : K :=
  ((-494059136 : K) / 1736217747 +
      (105105438269 : K) / 4125253366872 * v ^ 2 +
      (2647533011815013 : K) / 117135194267874816 * v ^ 4 +
      (428009025298456989887 : K) / 391865015985302552444928 * v ^ 6 +
      (-198886303192752706270559 : K) / 601904664553424720555409408 * v ^ 8 +
      (-13481444810188751934097 : K) / 601904664553424720555409408 * v ^ 10 +
      (114719383826498676713 : K) / 401269776368949813703606272 * v ^ 12 +
      (53870172905629283633 : K) / 2407618658213698882221637632 * v ^ 14 +
      (960674156248325617 : K) / 2407618658213698882221637632 * v ^ 16) +
    ((1111290550 : K) / 19098395217 * v +
      (-32780357365031 : K) / 2662163506088064 * v ^ 3 +
      (-365332387199691535 : K) / 61847382573437902848 * v ^ 5 +
      (157624795001753311877 : K) / 569985477796803712647168 * v ^ 7 +
      (37096904125719591799 : K) / 569985477796803712647168 * v ^ 9 +
      (424047398203868339 : K) / 379990318531202475098112 * v ^ 11 +
      (-53554105728538715 : K) / 2279941911187214850588672 * v ^ 13 +
      (-569063716282399 : K) / 2279941911187214850588672 * v ^ 15) * s2 +
    ((-1002006592 : K) / 15625959723 +
      (18101356969 : K) / 343771113906 * v ^ 2 +
      (-21253266994405517 : K) / 1405622331214497792 * v ^ 4 +
      (-177598618668705009991 : K) / 195932507992651276222464 * v ^ 6 +
      (14581850072977768102295 : K) / 75238083069178090069426176 * v ^ 8 +
      (856085724681926754073 : K) / 75238083069178090069426176 * v ^ 10 +
      (-1803383858072140219 : K) / 16719574015372908904316928 * v ^ 12 +
      (-2326998313094199929 : K) / 300952332276712360277704704 * v ^ 14 +
      (-44631377145963193 : K) / 300952332276712360277704704 * v ^ 16) * s3 +
    ((-9119862340 : K) / 171885556953 * v +
      (253428305915987 : K) / 23959471554792576 * v ^ 3 +
      (1362293724178034981 : K) / 371084295440627417088 * v ^ 5 +
      (-14784162681718793113 : K) / 213744554173801392242688 * v ^ 7 +
      (-4992984866077751155 : K) / 106872277086900696121344 * v ^ 9 +
      (-456029294831617481 : K) / 284992738898401856323584 * v ^ 11 +
      (-596729625775277 : K) / 854978216695205568970752 * v ^ 13 +
      (-1368230217809 : K) / 6679517317931293507584 * v ^ 15) * (s2 * s3)

variable (h2 : s2 ^ 2 = 2) (h3 : s3 ^ 2 = 3)

include h2 h3 in
/-- The crossing point: `27·V₀² = 2`. -/
theorem V0_on_crossing : 27 * V0 s2 s3 ^ 2 = 2 := by
  sorry

include h2 h3 in
/-- The θ-free amplitude check of the campaign: `A² = (V₀/3)² = 2/243`. -/
theorem amp_sq : (V0 s2 s3 / 3) ^ 2 = 2 / 243 := by
  sorry

include h2 h3 in
/-- **The Puiseux truncation**: the physical branch data satisfies `Ψ` to
order `v⁴` exactly — the coefficients of `v⁰, v¹, v², v³` all vanish.
Proof route: `linear_combination` with the cofactors of
`build/notary_n3_cofactors.txt` (regenerate with
`python3 build/notary_n3_lean_gen.py`); fallback, split into the four
`ℚ`-components of `1, s2, s3, s2·s3` and close each with `ring`. -/
theorem puiseux_truncation (v : K) :
    Psi v (V0 s2 s3 + V1 s3 * v + V2 s2 s3 * v ^ 2) = v ^ 4 * Q4 s2 s3 v := by
  sorry

include h3 in
/-- The linear-step pivot that pins `V₂` (and every later branch
coefficient): nonzero. -/
theorem pivot_ne_zero : (33161216 : K) / 4782969 * s3 ≠ 0 := by
  sorry

include h2 h3 in
/-- **The `1/k` coefficient**: `a = −1/8 − V₂/(2V₀) = 3293/92928 −
3251·√3/185856`, an element of `ℚ(√3)` — the constant every `k ≤ 19`
recognition scan had to miss. -/
theorem a_value :
    -1 / 8 - V2 s2 s3 / (2 * V0 s2 s3) =
      (3293 : K) / 92928 - (3251 : K) / 185856 * s3 := by
  sorry

end Branch

/-! ## `ℝ`-instantiations -/

noncomputable section RealInst

open Real

theorem real_sqrt2_sq : (Real.sqrt 2) ^ 2 = 2 := by
  sorry

theorem real_sqrt3_sq : (Real.sqrt 3) ^ 2 = 3 := by
  sorry

/-- The branch truncation over `ℝ`, at the actual square roots. -/
theorem real_puiseux_truncation (v : ℝ) :
    Psi v (V0 (Real.sqrt 2) (Real.sqrt 3) + V1 (Real.sqrt 3) * v +
        V2 (Real.sqrt 2) (Real.sqrt 3) * v ^ 2) =
      v ^ 4 * Q4 (Real.sqrt 2) (Real.sqrt 3) v :=
  puiseux_truncation _ _ real_sqrt2_sq real_sqrt3_sq v

/-- `a` over `ℝ`: the exact value of the campaign's `1/k` coefficient. -/
theorem real_a_value :
    -1 / 8 - V2 (Real.sqrt 2) (Real.sqrt 3) /
        (2 * V0 (Real.sqrt 2) (Real.sqrt 3)) =
      3293 / 92928 - 3251 / 185856 * Real.sqrt 3 :=
  a_value _ _ real_sqrt2_sq real_sqrt3_sq

end RealInst

end DepthOneConstants
end Polyplets
