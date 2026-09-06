/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum

/-!
# The depth-`j` below-onset defect: the assembly arithmetic of `(C)` / `(D)`

Campaign *Severance* W4, slice 2 (`docs/severance-w4-scoping.md (deleted)` §4(a), §5).
The below-onset correction to the diagonal law at depth `j`,

    `D_j(k) = [z^(k+1-j)] D(z)`,

is a **finite exact-rational assembly** of the excess-graded cluster weight
families — no enumeration at all. This module formalizes that assembly as
stated in `experiments/severance_w3_depths.py`, identities `(C)` and `(D)`:

    `A(k,E,m) = [y^k q^E] (Bb · Sig^m · Bb)`,
    `r_{2k+1-s} = Σ_{E+v=s} Σ_m A(k,E,m) C(k-m,v) (-3)^(k-m-v)`
                `+ Σ_{e+v=s} [y^k q^e]Pp · C(k+1,v) (-3)^(k+1-v)`,      (C)
    `a_{2k+1-t} = (-1)^(t+1) Σ_{s≤t} r_{2k+1-s} C(2k+1-s, 2k+1-t) 3^-(2k+1-s)`,
    `D_j(k) = (-3)^(k+1-j) Σ_{t<j} C(k-t, k+1-j) a_{2k+1-t}`.            (D)

The weight families enter as **hypotheses**: the theorems below quantify over
arbitrary tables `sig`, `bb`, `pp` and assume they are the banked ones, so the
arithmetic is severed from the enumeration that produced the weights.

## Arithmetic layout

Everything except the final division is integer. Writing `T̂` for the bracket of
`(D)` scaled by `3^(2k+1)` (legitimate: the only denominators in `(D)` are the
`3^-(2k+1-s)`, and `s ≥ 0`), `Dnum` computes

    `T̂ · (-3)^(k+1-j) = D_j(k) · 3^(2k+1)`   in `ℤ`,

which the kernel evaluates by `decide`; `Dval` divides by `3^(2k+1)` in `ℚ` and
`norm_num` finishes. (`decide` on `ℚ` is not an option: `Rat` arithmetic does
not reduce in the kernel.)

## Provenance of every literal

* `sigTable`, `bbTable`, `ppTable` — rows `e = 0..3`, columns `k = 0..8` of
  `results/severance_w3_families_K19_e3.txt`, the table written by
  `build/severance_w3_families` (`cpp/severance_w3_families.cpp`) and checked
  by `experiments/severance_w3_depths.py::validate` against
  `cluster_weight_dp.KNOWN_WEIGHTS`, against
  `results/severance_w1_weights_k9.txt`, and (row `e = 0`) against the gap walk
  of `GapWalk.lean`'s spec `experiments/depth1_gap_walk.py`.
* the `D_j(k)` values — printed by `python3 experiments/severance_w3_depths.py 8 4`
  (log `build/w4_depths_8_4.log`) and by the generator
  `build/w4_depth_lean_gen.py`, which emitted the table and theorem blocks
  below verbatim. At `j = 1` they agree with the banked leading coefficients,
  `D_1(k) = lead(R_k)/(-3)^(k+1)`: `lead(R_k) = 1, 4, -80, 1753, -40928,
  987355` for `k = 0..5` (`depth1_gap_walk.py::spine_lead`, fitted law-free
  from the banked triangle column).

The proof-side integer in each `decide` is written `num * 3^e` with the same
`num` as the statement's rational, so a wrong literal fails either the `decide`
(if the integer is wrong) or the `norm_num` (if it does not match the stated
rational).
-/

namespace Polyplets
namespace DepthAssembly

/-! ## Bigraded series -/

/-- A series graded by excess `e` (outer) and surplus `k` (inner), truncated
in both gradings: `a[e][k]`. -/
abbrev BivZ : Type := List (List ℤ)

/-- Coefficient of `q^e y^k`, zero outside the stored range. -/
def bget (a : BivZ) (e k : Nat) : ℤ := (a.getD e []).getD k 0

/-- Product of two bigraded series, truncated at excess `emax` and surplus `K`
(`_bimul`). -/
def bimul (K emax : Nat) (a b : BivZ) : BivZ :=
  (List.range (emax + 1)).map fun E =>
    (List.range (K + 1)).map fun k =>
      ((List.range (E + 1)).map fun e1 =>
        ((List.range (k + 1)).map fun k1 =>
          bget a e1 k1 * bget b (E - e1) (k - k1)).sum).sum

/-- Add the empty-edge term `1` to `Bb` (`Bb[0][0] += 1`). -/
def plusOne : BivZ → BivZ
  | [] => []
  | [] :: rs => [] :: rs
  | (x :: xs) :: rs => ((x + 1) :: xs) :: rs

/-- `Bb · Sig^m · Bb` for `m = 0, 1, ...` (the `A[m]` of `D_series`). -/
def AseriesAux (K emax : Nat) (sig bbp : BivZ) : Nat → BivZ → List BivZ
  | 0, cur => [bimul K emax cur bbp]
  | n + 1, cur => bimul K emax cur bbp :: AseriesAux K emax sig bbp n (bimul K emax cur sig)

/-- `A(k,E,m)` for `m = 0..K`, as a list of bigraded series. -/
def Aseries (K emax : Nat) (sig bbp : BivZ) : List BivZ :=
  AseriesAux K emax sig bbp K bbp

/-! ## Identities (C) and (D) -/

/-- The coefficient `r_{2k+1-s}` of identity `(C)`. -/
def rcoef (emax : Nat) (A : List BivZ) (pp : BivZ) (k s : Nat) : ℤ :=
  ((List.range (s + 1)).map fun E =>
    ((List.range (k + 1)).map fun m =>
      bget (A.getD m []) E k * (Nat.choose (k - m) (s - E) : ℤ) *
        (-3 : ℤ) ^ (k - m - (s - E))).sum).sum
  + ((List.range (min s emax + 1)).map fun e =>
      bget pp e k * (Nat.choose (k + 1) (s - e) : ℤ) *
        (-3 : ℤ) ^ (k + 1 - (s - e))).sum

/-- `D_j(k) · 3^(2k+1)`, an integer: identity `(D)` with the `3^-(2k+1-s)`
cleared. `emax = j - 1` is the excess budget of depth `j`. -/
def Dnum (j K : Nat) (sig bb pp : BivZ) (k : Nat) : ℤ :=
  if k + 1 < j then 0 else
    let emax := j - 1
    let A := Aseries K emax sig (plusOne bb)
    ((List.range j).map fun t =>
      (Nat.choose (k - t) (k + 1 - j) : ℤ) * (-1 : ℤ) ^ (t + 1) *
        ((List.range (t + 1)).map fun s =>
          rcoef emax A pp k s * (Nat.choose (2 * k + 1 - s) (2 * k + 1 - t) : ℤ) *
            (3 : ℤ) ^ s).sum).sum
      * (-3 : ℤ) ^ (k + 1 - j)

/-- The below-onset defect `D_j(k)` at depth `j`, an exact rational. -/
def Dval (j K : Nat) (sig bb pp : BivZ) (k : Nat) : ℚ :=
  (Dnum j K sig bb pp k : ℚ) / (3 : ℚ) ^ (2 * k + 1)

/-- Bridge from the integer kernel computation to the rational statement. -/
theorem Dval_eq_of_num {j K k : Nat} {sig bb pp : BivZ} {n : ℤ}
    (h : Dnum j K sig bb pp k = n) :
    Dval j K sig bb pp k = (n : ℚ) / (3 : ℚ) ^ (2 * k + 1) := by
  rw [Dval, h]

/-! ## The banked weight families

Rows `e = 0..3`, columns `k = 0..8` of
`results/severance_w3_families_K19_e3.txt` (`sig`, `bb`, `pp` columns), emitted
by `build/w4_depth_lean_gen.py`. -/

def sigTable : BivZ :=
  [[0, 25, 339, 4778, 68314, 981085, 14115141, 203235615, 2927318947],
   [0, 0, 49, 1860, 45226, 926236, 17359441, 308397220, 5286665538],
   [0, 0, 0, 81, 7311, 282683, 7866819, 185443644, 3960165215],
   [0, 0, 0, 0, 121, 25080, 1477849, 54033606, 1559809310]]

def bbTable : BivZ :=
  [[0, 5, 66, 919, 13103, 187965, 2703074, 38911979, 560417094],
   [0, 0, 7, 307, 7871, 165553, 3150481, 56524024, 975623392],
   [0, 0, 0, 9, 1045, 45055, 1321553, 32079519, 697938231],
   [0, 0, 0, 0, 11, 3146, 217306, 8582979, 258437191]]

def ppTable : BivZ :=
  [[0, 1, 13, 177, 2515, 36021, 517701, 7450561, 107291033],
   [0, 0, 1, 50, 1359, 29464, 570217, 10340774, 179805890],
   [0, 0, 0, 1, 145, 7062, 220066, 5519815, 122566105],
   [0, 0, 0, 0, 1, 380, 31164, 1345628, 42487955]]

/-! ## The depth identities at `k ≤ 8`

One theorem per `(j, k)`, the value a rational literal; weights supplied as
hypotheses. Emitted by `build/w4_depth_lean_gen.py`. -/

/-- `D_1(0)` = `-1/3`. -/
theorem depth1_k0 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 1 8 sig bb pp 0 = -1 / 3 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := -1 * 3^0) (by decide)]
  norm_num

/-- `D_1(1)` = `4/9`. -/
theorem depth1_k1 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 1 8 sig bb pp 1 = 4 / 9 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 4 * 3^1) (by decide)]
  norm_num

/-- `D_1(2)` = `80/27`. -/
theorem depth1_k2 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 1 8 sig bb pp 2 = 80 / 27 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 80 * 3^2) (by decide)]
  norm_num

/-- `D_1(3)` = `1753/81`. -/
theorem depth1_k3 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 1 8 sig bb pp 3 = 1753 / 81 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 1753 * 3^3) (by decide)]
  norm_num

/-- `D_1(4)` = `40928/243`. -/
theorem depth1_k4 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 1 8 sig bb pp 4 = 40928 / 243 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 40928 * 3^4) (by decide)]
  norm_num

/-- `D_1(5)` = `987355/729`. -/
theorem depth1_k5 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 1 8 sig bb pp 5 = 987355 / 729 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 987355 * 3^5) (by decide)]
  norm_num

/-- `D_1(6)` = `24323825/2187`. -/
theorem depth1_k6 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 1 8 sig bb pp 6 = 24323825 / 2187 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 24323825 * 3^6) (by decide)]
  norm_num

/-- `D_1(7)` = `607833256/6561`. -/
theorem depth1_k7 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 1 8 sig bb pp 7 = 607833256 / 6561 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 607833256 * 3^7) (by decide)]
  norm_num

/-- `D_1(8)` = `15348306104/19683`. -/
theorem depth1_k8 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 1 8 sig bb pp 8 = 15348306104 / 19683 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 15348306104 * 3^8) (by decide)]
  norm_num

/-- `D_2(0)` = `0`. -/
theorem depth2_k0 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 2 8 sig bb pp 0 = 0 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 0) (by decide)]
  norm_num

/-- `D_2(1)` = `20/27`. -/
theorem depth2_k1 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 2 8 sig bb pp 1 = 20 / 27 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 20 * 3^0) (by decide)]
  norm_num

/-- `D_2(2)` = `130/27`. -/
theorem depth2_k2 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 2 8 sig bb pp 2 = 130 / 27 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 130 * 3^2) (by decide)]
  norm_num

/-- `D_2(3)` = `11524/243`. -/
theorem depth2_k3 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 2 8 sig bb pp 3 = 11524 / 243 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 11524 * 3^2) (by decide)]
  norm_num

/-- `D_2(4)` = `344398/729`. -/
theorem depth2_k4 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 2 8 sig bb pp 4 = 344398 / 729 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 344398 * 3^3) (by decide)]
  norm_num

/-- `D_2(5)` = `1124984/243`. -/
theorem depth2_k5 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 2 8 sig bb pp 5 = 1124984 / 243 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 1124984 * 3^6) (by decide)]
  norm_num

/-- `D_2(6)` = `294307877/6561`. -/
theorem depth2_k6 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 2 8 sig bb pp 6 = 294307877 / 6561 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 294307877 * 3^5) (by decide)]
  norm_num

/-- `D_2(7)` = `8480809952/19683`. -/
theorem depth2_k7 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 2 8 sig bb pp 7 = 8480809952 / 19683 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 8480809952 * 3^6) (by decide)]
  norm_num

/-- `D_2(8)` = `80887423214/19683`. -/
theorem depth2_k8 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 2 8 sig bb pp 8 = 80887423214 / 19683 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 80887423214 * 3^8) (by decide)]
  norm_num

/-- `D_3(0)` = `0`. -/
theorem depth3_k0 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 3 8 sig bb pp 0 = 0 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 0) (by decide)]
  norm_num

/-- `D_3(1)` = `0`. -/
theorem depth3_k1 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 3 8 sig bb pp 1 = 0 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 0) (by decide)]
  norm_num

/-- `D_3(2)` = `214/81`. -/
theorem depth3_k2 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 3 8 sig bb pp 2 = 214 / 81 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 214 * 3^1) (by decide)]
  norm_num

/-- `D_3(3)` = `24877/729`. -/
theorem depth3_k3 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 3 8 sig bb pp 3 = 24877 / 729 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 24877 * 3^1) (by decide)]
  norm_num

/-- `D_3(4)` = `343550/729`. -/
theorem depth3_k4 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 3 8 sig bb pp 4 = 343550 / 729 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 343550 * 3^3) (by decide)]
  norm_num

/-- `D_3(5)` = `13288195/2187`. -/
theorem depth3_k5 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 3 8 sig bb pp 5 = 13288195 / 2187 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 13288195 * 3^4) (by decide)]
  norm_num

/-- `D_3(6)` = `1436864696/19683`. -/
theorem depth3_k6 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 3 8 sig bb pp 6 = 1436864696 / 19683 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 1436864696 * 3^4) (by decide)]
  norm_num

/-- `D_3(7)` = `16454701829/19683`. -/
theorem depth3_k7 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 3 8 sig bb pp 7 = 16454701829 / 19683 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 16454701829 * 3^6) (by decide)]
  norm_num

/-- `D_3(8)` = `182195974328/19683`. -/
theorem depth3_k8 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 3 8 sig bb pp 8 = 182195974328 / 19683 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 182195974328 * 3^8) (by decide)]
  norm_num

/-- `D_4(0)` = `0`. -/
theorem depth4_k0 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 4 8 sig bb pp 0 = 0 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 0) (by decide)]
  norm_num

/-- `D_4(1)` = `0`. -/
theorem depth4_k1 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 4 8 sig bb pp 1 = 0 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 0) (by decide)]
  norm_num

/-- `D_4(2)` = `0`. -/
theorem depth4_k2 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 4 8 sig bb pp 2 = 0 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 0) (by decide)]
  norm_num

/-- `D_4(3)` = `24146/2187`. -/
theorem depth4_k3 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 4 8 sig bb pp 3 = 24146 / 2187 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 24146 * 3^0) (by decide)]
  norm_num

/-- `D_4(4)` = `1400566/6561`. -/
theorem depth4_k4 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 4 8 sig bb pp 4 = 1400566 / 6561 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 1400566 * 3^1) (by decide)]
  norm_num

/-- `D_4(5)` = `75221426/19683`. -/
theorem depth4_k5 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 4 8 sig bb pp 5 = 75221426 / 19683 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 75221426 * 3^2) (by decide)]
  norm_num

/-- `D_4(6)` = `1199562484/19683`. -/
theorem depth4_k6 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 4 8 sig bb pp 6 = 1199562484 / 19683 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 1199562484 * 3^4) (by decide)]
  norm_num

/-- `D_4(7)` = `51621741496/59049`. -/
theorem depth4_k7 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 4 8 sig bb pp 7 = 51621741496 / 59049 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 51621741496 * 3^5) (by decide)]
  norm_num

/-- `D_4(8)` = `2058403227110/177147`. -/
theorem depth4_k8 (sig bb pp : BivZ)
    (hs : sig = sigTable) (hb : bb = bbTable) (hp : pp = ppTable) :
    Dval 4 8 sig bb pp 8 = 2058403227110 / 177147 := by
  subst hs; subst hb; subst hp
  rw [Dval_eq_of_num (n := 2058403227110 * 3^6) (by decide)]
  norm_num


end DepthAssembly
end Polyplets
