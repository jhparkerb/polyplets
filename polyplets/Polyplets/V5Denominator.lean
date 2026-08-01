/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Pin

/-!
# V5Denominator: the 5-adic law of the production-polynomial denominators

`results/v5-denominator-law.md` (2026-07-31): the minimal 5-adic valuation
over the `k!`-basis numerator coefficients of `P_k` obeys

> `chat k = v5(k!) - H k`,   `H k = v5((k/2)!)` for even `k`
> (odd `k`: `max (v5(((k-3)/2)!)) (v5(((k-1)/2)!) - 1)`; `H 1 = -1`),

NOT the previously conjectured `ceil (v5 (k!) / 2)` — which fails at
`k = 11` (and is refuted here). This file machine-checks the corrected law
at every pinned level and formalizes the `k = 11` obstruction:

* `N1 .. N18` — the numerator lists, certified to be EXACTLY the data of
  the pinned production polynomials by the `rfl` tie lemmas
  `Pp<k>_data : Pp<k> = prodPoly N<k> k!` (a transcription typo fails the
  build).
* `v5_law_all` — the corrected law at every level `k = 1 .. 18`, kernel
  `decide` (no native leaves).
* `chat11` / `ceil_fit_refuted` — `chat 11 = 2`, and the old fit's `1` is
  wrong: the value we were "badly wrong" about is now a kernel fact.
* `eleven_no_harvest` — WHY `k = 11`: a multiset of parts `>= 2` summing
  to `11` has every multiplicity `<= 4`, so the five-fold order-2 slot
  harvest that drops the denominator at every other `k >= 10` is
  additively blocked — a general theorem, not a table lookup.
* `u1_seed` / `g1_seed` — the two taxed order-1 boundary coefficients
  `u_1 = P_1(1) - P_1(0) = 25` and `g_1 = P_1(0) = -45`, tied to `Pp1`.

The general-`k` lower bound `chat k >= v5 (k!) - H k` (Newton/multinomial
over the boundary series, from integer-valuedness + grand form + `P_1`)
is paper-level in `results/v5-denominator-law.md`; formalizing it is a
known open item, tracked in `PROOF-STATUS.md`.

Data provenance: `polyplets/pin-data.md` == `Pin.lean` literals
(cross-checked 2026-07-31). Axioms: standard three only.
-/

namespace Polyplets
namespace V5

/-- Fuel-based 5-adic valuation of a natural number (kernel-reducible;
`64` units of fuel cover every integer below `5^64`). Returns `0` at `n = 0`
by convention — never applied to `0` here (no numerator coefficient
vanishes at any pinned level). -/
def v5F : Nat → Nat → Nat
  | 0, _ => 0
  | _, 0 => 0
  | fuel + 1, n => if n % 5 == 0 then v5F fuel (n / 5) + 1 else 0

/-- 5-adic valuation of a rational's numerator (the lists below are
integers embedded in `ℚ`, so this is their 5-adic valuation). -/
def v5q (q : ℚ) : ℤ := (v5F 64 q.num.natAbs : ℤ)

/-- `v₅(k!)`. -/
def v5fact (k : ℕ) : ℤ := (v5F 64 (Nat.factorial k) : ℤ)

/-- The harvest `H k`: how far the 5-adic content of the coefficients of
`k!·P_k` can drop below `v₅(k!)`. The partition optimum (all-2s blocks,
odd leftover paying the `g₁` tax) collapses to a single expression:
`v₅(⌊k/2⌋!)` docked by one exactly on the residue class `k ≡ 1 (mod 10)`
(for odd `k` the leftover cell collides with a fresh multiple-of-5
multiplicity iff `5 ∣ ⌊k/2⌋`; `H 1 = -1` is the same indicator at
`v₅(0!) = 0`). Equivalently `v₅(k!) - H k` is `v₅` of the odd double
factorial `≤ k`, plus the same indicator. -/
def H (k : ℕ) : ℤ :=
  v5fact (k / 2) - if k % 10 == 1 then 1 else 0

/-! ## The pinned numerator data

Descending in `n`, over `k!` — the exact `prodPoly` arguments of
`Pin.lean`; the `Pp<k>_data` lemmas below are `rfl`, so these lists ARE
the production data. -/

section Data
set_option linter.style.longLine false

def N1 : List ℚ := [25, -45]

def N2 : List ℚ := [625, -2459, 1134]

def N3 : List ℚ := [15625, -100050, 122213, -32940]

def N4 : List ℚ := [390625, -3596250, 8099843, -6462882, 1752840]

def N5 : List ℚ := [9765625, -120546875, 425836625, -650171245, 422003550, 76975920]

def N6 : List ℚ := [244140625, -3861328125, 19486496875, -47366857935, 55373728180, 946828380, -32099353920]

def N7 : List ℚ :=
[6103515625, -119765625000, 812310625000, -2839739579250, 5194366339015, -1878923357430, 
  -6841564107480, 7756630081200]

def N8 : List ℚ :=
[152587890625, -3625976562500, 31658675781250, -149222374175000, 391357255277905, 
  -350057694296660, -718224955399380, 2136536485853040, -923712586957440]

def N9 : List ℚ :=
[3814697265625, -107720947265625, 1172546074218750, -7126125723281250, 25246485663128625, 
  -39217219391133945, -44784313962337720, 312218815384892340, -359168984859479760, 
  17928204588927360]

def N10 : List ℚ :=
[95367431640625, -3151702880859375, 41724067382812500, -316409147402343750, 
  1450416433150453125, -3370526923710995055, -1108292379978242050, 31805482385795516100, 
  -69735093253554241800, 32190356082435763680, 25618243319042572800]

def N11 : List ℚ :=
[2384185791015625, -91056823730468750, 1437517181396484375, -13264842209179687500, 
  76160367268876171875, -243501035699144280750, 120586120186765409825, 2497738719648063722600, 
  -9207797682124933481700, 10269478266342644052000, 3325021854753536899200, 
  5868473845727607206400]

def N12 : List ℚ :=
[59604644775390625, -2602958679199218750, 48223920440673828125, -530815263596191406250, 
  3721840065507802734375, -15512118396389744456250, 21149152791035920752695, 
  157168222110058996109130, -936571784113889621399900, 1860945781255305037306200, 
  -561954556767083249661120, 2518353204096205882465920, -12192370946767873838592000]

def N13 : List ℚ :=
[1490116119384765625, -73735713958740234375, 1581930904388427734375, -20438647987884521484375, 
  171498867051782080078125, -897242973195286876640625, 2053473678621559440657125, 
  7845602899216787491993635, -78302966517647904123999050, 242568775590879458927220300, 
  -252892500470648129748781800, 630295671430278785315535840, -4709212944929227143077529600, 
  8516420444581467205615027200]

def N14 : List ℚ :=
[37252902984619140625, -2072393894195556640625, 50912246036529541015625, 
  -761843525055694580078125, 7524678110464896240234375, -48052027303805350998046875, 
  157448856577961057749371875, 276655470142052990154351185, -5583936647603503419750059540, 
  25191124931485376140721243800, -47958023503387714879301084400, 
  118184880567640594471489711440, -979514007904340174674683668160, 
  3638916058760447487430557542400, -4028797193164605150126008371200]

def N15 : List ℚ :=
[931322574615478515625, -57846307754516601562500, 1611761021614074707031250, 
  -27620633003425598144531250, 316736418664104003906250000, -2416046782053819856347656250, 
  10461322884210958342060156250, 1967893236430787060707991250, -346618516939812097631010184825, 
  2203970151840239765899986819750, -6398534829863605593928976949100, 
  17955993014682160383586429971000, -146852693386847802168160405132800, 
  824216279306486381670291956424000, -1935618838774923672066722617670400, 
  1370506748049564268873803929856000]

def N16 : List ℚ :=
[23283064365386962890625, -1604855060577392578125000, 50296202898025512695312500, 
  -977645294998168945312500000, 12866158692583824157714843750, -115227786191848182480468750000, 
  627956075188775884851523437500, -744604346962912741214695500000, 
  -18856370906133182542352742484975, 168083439133981919034904849231800, 
  -683834540674642382762519712038200, 2295047561654327718980302632052800, 
  -17913005887676406640071685928060400, 131791153675357698130550590831267200, 
  -488805850691225808484910594988268800, 759766595538270156033339090440755200, 
  -219118392304691271841806767714304000]

def N17 : List ℚ :=
[582076609134674072265625, -44283457100391387939453125, 1549785345792770385742187500, 
  -33886054842615127563476562500, 506738958957323265075683593750, 
  -5253930386581950765319824218750, 34866787110157325826676367187500, 
  -86528320883080938837347917187500, -889937241002481289280616442864375, 
  11422356391454342173853403279879275, -62157637321860866791915723663376800, 
  253251875227507029291999691317061400, -1898632937628268836106376147065825200, 
  16730852931327365644218857489259687600, -86335313597104845199405280481932515200, 
  218410029105004429734891444381037497600, -171351859928354717515789878977767372800, 
  -114129552065978933164859052982947840000]

def N18 : List ℚ :=
[14551915228366851806640625, -1216004602611064910888671875, 47220123186707496643066406250, 
  -1152996117314100265502929687500, 19425111820647906303405761718750, 
  -230445407070280340071105957031250, 1818181407908782536004023437500000, 
  -6826614118228039757132018320312500, -34818861040188463329071106306984375, 
  701508624630574629016108663795874925, -4974015500069905129885380187424318850, 
  24632585272713265594357624257091138200, -181772288700805914476560807450032440000, 
  1799250000012213308990934660048459646800, -11981768558659998471685945614032297834400, 
  43413108716808863459147673721575806860800, -62928082571267723622620177718733540032000, 
  -37079629775551619904419498589278737305600, 127787800900726736892183047952793411584000]

theorem Pp1_data : Pp1 = prodPoly N1 1 := rfl
theorem Pp2_data : Pp2 = prodPoly N2 2 := rfl
theorem Pp3_data : Pp3 = prodPoly N3 6 := rfl
theorem Pp4_data : Pp4 = prodPoly N4 24 := rfl
theorem Pp5_data : Pp5 = prodPoly N5 120 := rfl
theorem Pp6_data : Pp6 = prodPoly N6 720 := rfl
theorem Pp7_data : Pp7 = prodPoly N7 5040 := rfl
theorem Pp8_data : Pp8 = prodPoly N8 40320 := rfl
theorem Pp9_data : Pp9 = prodPoly N9 362880 := rfl
theorem Pp10_data : Pp10 = prodPoly N10 3628800 := rfl
theorem Pp11_data : Pp11 = prodPoly N11 39916800 := rfl
theorem Pp12_data : Pp12 = prodPoly N12 479001600 := rfl
theorem Pp13_data : Pp13 = prodPoly N13 6227020800 := rfl
theorem Pp14_data : Pp14 = prodPoly N14 87178291200 := rfl
theorem Pp15_data : Pp15 = prodPoly N15 1307674368000 := rfl
theorem Pp16_data : Pp16 = prodPoly N16 20922789888000 := rfl
theorem Pp17_data : Pp17 = prodPoly N17 355687428096000 := rfl
theorem Pp18_data : Pp18 = prodPoly N18 6402373705728000 := rfl

def table : List (ℕ × List ℚ) :=
  [(1, N1), (2, N2), (3, N3), (4, N4), (5, N5), (6, N6), (7, N7), (8, N8), (9, N9),
   (10, N10), (11, N11), (12, N12), (13, N13), (14, N14), (15, N15), (16, N16), (17, N17),
   (18, N18)]


end Data


/-! ## The corrected law, kernel-checked at every pinned level -/

set_option maxRecDepth 20000 in
/-- **The v5 denominator law, `k = 1 .. 18`**: the minimal 5-adic valuation
over the `k!`-basis numerator coefficients equals `v₅(k!) - H k` — at
EVERY level, `k = 11` included, no exception. Kernel `decide`. -/
theorem v5_law_all :
    ∀ p ∈ table, (p.2.map v5q).min? = some (v5fact p.1 - H p.1) := by decide

set_option maxRecDepth 4000 in
/-- `chat 11 = 2`: all twelve numerator coefficients of `11!·P_11` are
divisible by `25`, and one is not divisible by `125`. -/
theorem chat11 : (N11.map v5q).min? = some 2 := by decide

set_option maxRecDepth 4000 in
/-- The old conjectured law `ceil (v5 (k!) / 2)` predicts `1` at `k = 11`;
the pinned data says `2`. The fit is refuted where we were wrong. -/
theorem ceil_fit_refuted :
    (v5fact 11 + 1) / 2 = 1 ∧ (N11.map v5q).min? ≠ some 1 := by decide

/-- At `k = 1` the uncapped numerator minimum is `1`, not `0` (`25, -45`
are both divisible by 5): the `H 1 = -1` tax is real, only masked in the
denominator by the cap `D_1 = 1`. -/
theorem chat1 : (N1.map v5q).min? = some 1 := by decide

/-! ## Why k = 11: the additive obstruction -/

/-- **The `k = 11` obstruction.** Any multiset of parts `≥ 2` summing to
`11` has every multiplicity `≤ 4`: a multiplicity `≥ 5` forces five parts
of size exactly `2` (cost `10`), and the leftover `1` is not a part `≥ 2`.
This is the additive fact that blocks the five-fold harvest at `k = 11`
(and only there among `10 ≤ k ≤ 20`). -/
theorem eleven_no_harvest (s : Multiset ℕ) (h2 : ∀ x ∈ s, 2 ≤ x)
    (hsum : s.sum = 11) (x : ℕ) : s.count x ≤ 4 := by
  by_contra hc
  have hrep : Multiset.replicate 5 x ≤ s :=
    Multiset.le_count_iff_replicate_le.mp (by omega)
  obtain ⟨t, rfl⟩ := Multiset.le_iff_exists_add.mp hrep
  have hx2 : 2 ≤ x := h2 x (Multiset.mem_add.mpr (Or.inl (by simp)))
  have hsums : 5 * x + t.sum = 11 := by
    rw [Multiset.sum_add, Multiset.sum_replicate] at hsum
    simpa [smul_eq_mul] using hsum
  have ht1 : t.sum = 1 := by omega
  have ht0 : t ≠ 0 := by intro h; rw [h] at ht1; simp at ht1
  obtain ⟨y, hy⟩ := Multiset.exists_mem_of_ne_zero ht0
  have hy2 : 2 ≤ y := h2 y (Multiset.mem_add.mpr (Or.inr hy))
  have hyle : y ≤ t.sum := Multiset.single_le_sum (fun _ _ => Nat.zero_le _) y hy
  omega

/-! ## The two taxed order-1 seeds, tied to the pinned `P_1` -/

/-- `g₁ = P₁(0) = -45`, with `v₅ = 1`. -/
theorem g1_seed : Pp1.eval 0 = -45 ∧ v5q (-45) = 1 := by
  constructor
  · rw [Pp1_data, prodPoly_eval]; norm_num [N1]
  · decide

/-- `u₁ = P₁(1) - P₁(0) = 25`, with `v₅ = 2` — the order-2 vanishing of
`Λ - 1` mod 5 that collapses the denominator (`results/v5-denominator-law.md`). -/
theorem u1_seed : Pp1.eval 1 - Pp1.eval 0 = 25 ∧ v5q 25 = 2 := by
  constructor
  · simp only [Pp1_data, prodPoly_eval]; norm_num [N1]
  · decide


set_option maxRecDepth 20000 in
/-- **Upper-half profile law** (second pass, 2026-07-31): for every
`i ≥ ⌈k/2⌉` the coefficient valuation is EXACTLY multinomial arithmetic,
`v₅([nⁱ] k!·P_k) = 2(2i−k) + v₅(k!/((2i−k)!·(k−i)!))` — the unique
minimal-slot configuration (`2i−k` order-1 slots at `u₁ = 25`, `k−i`
order-2 slots, Stirling `s(i,i) = 1`) carries the whole 5-adic content.
Lists are descending in `n`: ascending coefficient `i` is entry `k − i`. -/
theorem upper_half_law :
    ∀ p ∈ table, ∀ i ∈ List.range (p.1 + 1), p.1 ≤ 2 * i →
      v5q (p.2.getD (p.1 - i) 0) =
        2 * (2 * i - p.1 : ℕ) +
        (v5F 64 (Nat.factorial p.1 /
          (Nat.factorial (2 * i - p.1) * Nat.factorial (p.1 - i))) : ℤ) := by
  decide

/-! ## Axiom audit -/

#print axioms v5_law_all
#print axioms ceil_fit_refuted
#print axioms eleven_no_harvest
#print axioms u1_seed
#print axioms upper_half_law

end V5
end Polyplets
