/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.LinearAlgebra.Lagrange
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Set
import Polyplets.Shape

/-!
# Pin: the explicit production polynomials `P_k`

`Shape.lean` proves that for every surplus `k` there is *some* `P_k ∈ ℚ[X]` of
degree `≤ k` with `T(n, n-k) = P_k(n)·3^(n-1-3k)` for `n ≥ 2k+1`
(`shape_production`), but does not identify it. This file holds the concrete
production polynomials `Pp0 … Pp18` of `orchestrator/sweep.go` (numerator
coefficients descending in `n`, over `k!`), the Lagrange pin lemma `pin`
(a degree-`≤ k` polynomial matching the shape witness at the `k+1` onset
points `2k+1 … 3k+1` *is* the witness), and the unconditional `k = 1` law
`P1_closed`, pinned from the kernel-decided cells `T 3 2` and `T 4 3`.

`Grand/PinAll.lean` pins every `Pp<k>`, `k ≤ 18`, from two enumerated anchor
cells per level; `LeadingCoeff.lean` pins from `k` rows given the leading
coefficient. A mistyped coefficient fails there, at the anchor evaluations.
-/

namespace Polyplets

open Polynomial

/-! ## Horner polynomials from coefficient lists -/

/-- Ascending-coefficient Horner polynomial:
`horner [a₀, a₁, …, a_d] = a₀ + a₁·X + … + a_d·X^d`. -/
noncomputable def horner : List ℚ → Polynomial ℚ
  | [] => 0
  | c :: cs => C c + X * horner cs

/-- The Horner polynomial of an `(d+1)`-coefficient list has degree `≤ d`. -/
lemma horner_natDegree_le : ∀ l : List ℚ, (horner l).natDegree ≤ l.length - 1
  | [] => by simp [horner]
  | [c] => by simp [horner]
  | c :: d :: cs => by
      have ih := horner_natDegree_le (d :: cs)
      change (C c + X * horner (d :: cs)).natDegree ≤ _
      refine le_trans (natDegree_add_le _ _) ?_
      rw [natDegree_C]
      refine max_le (Nat.zero_le _) ?_
      refine le_trans natDegree_mul_le ?_
      rw [natDegree_X]
      simp only [List.length_cons] at ih ⊢
      omega

/-- Evaluation of a Horner polynomial is the Horner fold of its coefficients. -/
lemma horner_eval (l : List ℚ) (x : ℚ) :
    (horner l).eval x = l.foldr (fun c acc => c + x * acc) 0 := by
  induction l with
  | nil => simp [horner]
  | cons c cs ih => simp only [horner, eval_add, eval_mul, eval_C, eval_X, ih, List.foldr_cons]

/-- The production polynomial: a descending numerator coefficient list over the
scalar `kf` (the `k!` of `pin-data.md`). -/
noncomputable def prodPoly (num : List ℚ) (kf : ℚ) : Polynomial ℚ :=
  C (1 / kf) * horner num.reverse

/-- `prodPoly` of a `(k+1)`-coefficient numerator has degree `≤ k`. -/
lemma prodPoly_natDegree_le (num : List ℚ) (kf : ℚ) :
    (prodPoly num kf).natDegree ≤ num.length - 1 := by
  refine le_trans (natDegree_C_mul_le _ _) (le_trans (horner_natDegree_le num.reverse) ?_)
  simp [List.length_reverse]

/-- Evaluation of `prodPoly`, ready for `norm_num` at a pin point. -/
lemma prodPoly_eval (num : List ℚ) (kf x : ℚ) :
    (prodPoly num kf).eval x = (1 / kf) * num.reverse.foldr (fun c acc => c + x * acc) 0 := by
  rw [prodPoly, eval_mul, eval_C, horner_eval]

/-! ## The generic pin lemma (Lagrange uniqueness) -/

/-- **Pin lemma.** A polynomial `p` of degree `≤ k` that matches the shape
witness (`shape_production`) at the `k+1` onset points `[2k+1, 3k+1]`
*is* the shape witness, hence carries the full diagonal-law production form.

The hypothesis `hpts` states, at each of the `k+1` onset points
`n ∈ [2k+1, 3k+1]`, that `p(n)` equals the integer `T(n,n-k)·3^(3k+1-n)`
that `production_int_onset` also forces on the witness; Lagrange
(`eq_of_degrees_lt_of_eval_finset_eq`) over `ℚ`, on the interval cast into
`ℚ`, then identifies the two polynomials. (2026-07-31: specialized to
`s = Finset.Icc (2k+1) (3k+1)` — every caller passed exactly that set, so
the former `s`/`hcard`/`hin` parameters were noise.) -/
theorem pin (k : ℕ) (p : Polynomial ℚ) (hp : p.natDegree ≤ k)
    (hpts : ∀ n ∈ Finset.Icc (2 * k + 1) (3 * k + 1),
      p.eval (n : ℚ) = ((T n (n - k) * 3 ^ (3 * k + 1 - n) : ℕ) : ℚ)) :
    ∀ n : ℕ, 2 * k + 1 ≤ n →
      (T n (n - k) : ℚ) = p.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k) := by
  set s : Finset ℕ := Finset.Icc (2 * k + 1) (3 * k + 1) with hs
  have hcard : k + 1 ≤ s.card := by rw [hs, Nat.card_Icc]; omega
  have hin : ∀ n ∈ s, 2 * k + 1 ≤ n ∧ n ≤ 3 * k + 1 := fun n hn =>
    Finset.mem_Icc.mp (hs ▸ hn)
  obtain ⟨P, hPdeg, hPzpow, hPcomp⟩ := shape_production k
  have hpP : p = P := by
    have hinj : Set.InjOn (Nat.cast : ℕ → ℚ) s := fun a _ b _ h => by exact_mod_cast h
    have hcard' : (s.image (Nat.cast : ℕ → ℚ)).card = s.card :=
      Finset.card_image_of_injOn hinj
    apply Polynomial.eq_of_degrees_lt_of_eval_finset_eq (s.image (Nat.cast : ℕ → ℚ))
    · calc p.degree ≤ (p.natDegree : WithBot ℕ) := Polynomial.degree_le_natDegree
        _ ≤ (k : WithBot ℕ) := by exact_mod_cast hp
        _ < ((s.image (Nat.cast : ℕ → ℚ)).card : WithBot ℕ) := by
            rw [hcard']; exact_mod_cast (by omega : k < s.card)
    · calc P.degree ≤ (P.natDegree : WithBot ℕ) := Polynomial.degree_le_natDegree
        _ ≤ (k : WithBot ℕ) := by exact_mod_cast hPdeg
        _ < ((s.image (Nat.cast : ℕ → ℚ)).card : WithBot ℕ) := by
            rw [hcard']; exact_mod_cast (by omega : k < s.card)
    · intro x hx
      rw [Finset.mem_image] at hx
      obtain ⟨n, hn, rfl⟩ := hx
      rw [hpts n hn]
      obtain ⟨hn1, hn2⟩ := hin n hn
      rw [production_int_onset hPcomp hn1 hn2]
  rw [hpP]
  exact hPzpow

/-! ## The production polynomials, and the unconditional `k = 1` law -/

/-- k=0 production polynomial `P_0 = 1`. -/
noncomputable def Pp0 : Polynomial ℚ := prodPoly [1] 1

/-- k=1 production polynomial `P_1 = 25X - 45`. -/
noncomputable def Pp1 : Polynomial ℚ := prodPoly [25, -45] 1
lemma Pp1_deg : Pp1.natDegree ≤ 1 := by
  rw [Pp1]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)
lemma guard_1_3 : Pp1.eval (3 : ℚ) = ((T 3 2 * 3 ^ 1 : ℕ) : ℚ) := by
  rw [Pp1, prodPoly_eval]; norm_num [T_3_2]
lemma guard_1_4 : Pp1.eval (4 : ℚ) = ((T 4 3 * 3 ^ 0 : ℕ) : ℚ) := by
  rw [Pp1, prodPoly_eval]; norm_num [T_4_3]

/-- **k=1 diagonal, unconditional** (production form). -/
theorem P1_pinned : ∀ n : ℕ, 2 * 1 + 1 ≤ n →
    (T n (n - 1) : ℚ) = Pp1.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 1) := by
  refine pin 1 Pp1 Pp1_deg ?_
  intro n hn
  fin_cases hn
  · simp only [show (3 - 1 : ℕ) = 2 from rfl, show (3 * 1 + 1 - 3 : ℕ) = 1 from rfl]
    exact guard_1_3
  · simp only [show (4 - 1 : ℕ) = 3 from rfl, show (3 * 1 + 1 - 4 : ℕ) = 0 from rfl]
    exact guard_1_4

/-- **k=1 diagonal, human form**: `T(n, n-1) = (25n - 45)·3^(n-4)` for `n ≥ 3`. -/
theorem P1_closed (n : ℕ) (hn : 3 ≤ n) :
    (T n (n - 1) : ℚ) = (25 * (n : ℚ) - 45) * (3 : ℚ) ^ ((n : ℤ) - 4) := by
  have h := P1_pinned n hn
  rw [Pp1, prodPoly_eval] at h
  norm_num at h ⊢
  rw [h]; ring_nf

/-! ## `k = 2 … 18`, pinned in `Grand/PinAll.lean` -/

section ProductionPolynomials
set_option linter.style.longLine false

/-- k=2 production polynomial (numerator / 2!). -/
noncomputable def Pp2 : Polynomial ℚ := prodPoly [625, -2459, 1134] 2

/-- k=3 production polynomial (numerator / 3!). -/
noncomputable def Pp3 : Polynomial ℚ := prodPoly [15625, -100050, 122213, -32940] 6

/-- k=4 production polynomial (numerator / 4!). -/
noncomputable def Pp4 : Polynomial ℚ := prodPoly
  [390625, -3596250, 8099843, -6462882, 1752840] 24

/-- k=5 production polynomial (numerator / 5!). -/
noncomputable def Pp5 : Polynomial ℚ := prodPoly
  [9765625, -120546875, 425836625, -650171245, 422003550, 76975920] 120

/-- k=6 production polynomial (numerator / 6!). -/
noncomputable def Pp6 : Polynomial ℚ := prodPoly
  [244140625, -3861328125, 19486496875, -47366857935, 55373728180, 946828380, -32099353920] 720

/-- k=7 production polynomial (numerator / 7!). -/
noncomputable def Pp7 : Polynomial ℚ := prodPoly
  [6103515625, -119765625000, 812310625000, -2839739579250, 5194366339015, -1878923357430, -6841564107480, 7756630081200] 5040

/-- k=8 production polynomial (numerator / 8!). -/
noncomputable def Pp8 : Polynomial ℚ := prodPoly
  [152587890625, -3625976562500, 31658675781250, -149222374175000, 391357255277905, -350057694296660, -718224955399380, 2136536485853040, -923712586957440] 40320

/-- k=9 production polynomial (numerator / 9!). -/
noncomputable def Pp9 : Polynomial ℚ := prodPoly
  [3814697265625, -107720947265625, 1172546074218750, -7126125723281250, 25246485663128625, -39217219391133945, -44784313962337720, 312218815384892340, -359168984859479760, 17928204588927360] 362880

/-- k=10 production polynomial (numerator / 10!). -/
noncomputable def Pp10 : Polynomial ℚ := prodPoly
  [95367431640625, -3151702880859375, 41724067382812500, -316409147402343750, 1450416433150453125, -3370526923710995055, -1108292379978242050, 31805482385795516100, -69735093253554241800, 32190356082435763680, 25618243319042572800] 3628800

/-- k=11 production polynomial (numerator / 11!). -/
noncomputable def Pp11 : Polynomial ℚ := prodPoly
  [2384185791015625, -91056823730468750, 1437517181396484375, -13264842209179687500, 76160367268876171875, -243501035699144280750, 120586120186765409825, 2497738719648063722600, -9207797682124933481700, 10269478266342644052000, 3325021854753536899200, 5868473845727607206400] 39916800

/-- k=12 production polynomial (numerator / 12!). -/
noncomputable def Pp12 : Polynomial ℚ := prodPoly
  [59604644775390625, -2602958679199218750, 48223920440673828125, -530815263596191406250, 3721840065507802734375, -15512118396389744456250, 21149152791035920752695, 157168222110058996109130, -936571784113889621399900, 1860945781255305037306200, -561954556767083249661120, 2518353204096205882465920, -12192370946767873838592000] 479001600

/-- k=13 production polynomial (numerator / 13!). -/
noncomputable def Pp13 : Polynomial ℚ := prodPoly
  [1490116119384765625, -73735713958740234375, 1581930904388427734375, -20438647987884521484375, 171498867051782080078125, -897242973195286876640625, 2053473678621559440657125, 7845602899216787491993635, -78302966517647904123999050, 242568775590879458927220300, -252892500470648129748781800, 630295671430278785315535840, -4709212944929227143077529600, 8516420444581467205615027200] 6227020800

/-- k=14 production polynomial (numerator / 14!). -/
noncomputable def Pp14 : Polynomial ℚ := prodPoly
  [37252902984619140625, -2072393894195556640625, 50912246036529541015625, -761843525055694580078125, 7524678110464896240234375, -48052027303805350998046875, 157448856577961057749371875, 276655470142052990154351185, -5583936647603503419750059540, 25191124931485376140721243800, -47958023503387714879301084400, 118184880567640594471489711440, -979514007904340174674683668160, 3638916058760447487430557542400, -4028797193164605150126008371200] 87178291200

/-- k=15 production polynomial (numerator / 15!). -/
noncomputable def Pp15 : Polynomial ℚ := prodPoly
  [931322574615478515625, -57846307754516601562500, 1611761021614074707031250, -27620633003425598144531250, 316736418664104003906250000, -2416046782053819856347656250, 10461322884210958342060156250, 1967893236430787060707991250, -346618516939812097631010184825, 2203970151840239765899986819750, -6398534829863605593928976949100, 17955993014682160383586429971000, -146852693386847802168160405132800, 824216279306486381670291956424000, -1935618838774923672066722617670400, 1370506748049564268873803929856000] 1307674368000

/-- k=16 production polynomial (numerator / 16!). -/
noncomputable def Pp16 : Polynomial ℚ := prodPoly
  [23283064365386962890625, -1604855060577392578125000, 50296202898025512695312500, -977645294998168945312500000, 12866158692583824157714843750, -115227786191848182480468750000, 627956075188775884851523437500, -744604346962912741214695500000, -18856370906133182542352742484975, 168083439133981919034904849231800, -683834540674642382762519712038200, 2295047561654327718980302632052800, -17913005887676406640071685928060400, 131791153675357698130550590831267200, -488805850691225808484910594988268800, 759766595538270156033339090440755200, -219118392304691271841806767714304000] 20922789888000

/-- k=17 production polynomial (numerator / 17!). -/
noncomputable def Pp17 : Polynomial ℚ := prodPoly
  [582076609134674072265625, -44283457100391387939453125, 1549785345792770385742187500, -33886054842615127563476562500, 506738958957323265075683593750, -5253930386581950765319824218750, 34866787110157325826676367187500, -86528320883080938837347917187500, -889937241002481289280616442864375, 11422356391454342173853403279879275, -62157637321860866791915723663376800, 253251875227507029291999691317061400, -1898632937628268836106376147065825200, 16730852931327365644218857489259687600, -86335313597104845199405280481932515200, 218410029105004429734891444381037497600, -171351859928354717515789878977767372800, -114129552065978933164859052982947840000] 355687428096000

/-- k=18 production polynomial (numerator / 18!). -/
noncomputable def Pp18 : Polynomial ℚ := prodPoly
  [14551915228366851806640625, -1216004602611064910888671875, 47220123186707496643066406250, -1152996117314100265502929687500, 19425111820647906303405761718750, -230445407070280340071105957031250, 1818181407908782536004023437500000, -6826614118228039757132018320312500, -34818861040188463329071106306984375, 701508624630574629016108663795874925, -4974015500069905129885380187424318850, 24632585272713265594357624257091138200, -181772288700805914476560807450032440000, 1799250000012213308990934660048459646800, -11981768558659998471685945614032297834400, 43413108716808863459147673721575806860800, -62928082571267723622620177718733540032000, -37079629775551619904419498589278737305600, 127787800900726736892183047952793411584000] 6402373705728000

end ProductionPolynomials

end Polyplets
