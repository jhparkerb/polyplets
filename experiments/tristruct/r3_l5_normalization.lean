/- R3 L5 hardening: the two hand-checked claims of r3_l5_king_connected.lean,
   written as Lean theorems.

   STATUS: WRITTEN BUT NOT COMPILED (2026-08-12, restart agent). Lean and lake
   are banned on gympie for this round (docs/r3-job-dispatch.md); this file has
   never been elaborated. The proofs were written and checked by eye only.

   Check command (ayr or dalby, or any machine with the project toolchain
   leanprover/lean4:v4.31.0 and the polyplets mathlib cache — NOT gympie):

     cd <repo>/polyplets && ~/.elan/bin/lake env lean \
       ../experiments/tristruct/r3_l5_normalization.lean

   Expected on success: no output, exit 0 (the file is proofs only — no #eval,
   no pins). Any output is a failure and names the lemma that needs repair.

   WHAT IS PROVED (statement inventory):

   Claim 1 — the width <= n normalization ("the domain box loses nothing"):
     * `walk_hits_column`      — discrete IVT along a king walk (the argument
                                 the original file's header states in prose)
     * `width_lt_of_normalized`— a normalized plane animal has every x < n
     * `rows_of_normalized`    — and every y in [0, H-1], with row H-1 attained
     * `normalized_in_box`     — packaged: normalized plane animals live in
                                 [0,n) x [0,H)
     * `mem_counted_iff_normalized_animal`
                               — the sets counted by `T n H` are EXACTLY the
                                 (casts of) normalized plane animals

   Claim 2 — the translation-class bijection:
     * `existsUnique_normalizing_translate`
                               — every plane animal has exactly one
                                 normalizing translate (transversal property)
     * `T_eq_card_normalized`  — T(n,H) = #(normalized plane animals)
     * `T_eq_card_translationClasses`
                               — T(n,H) = #(translation classes of
                                 king-connected n-cell sets of height
                                 exactly H)   [the headline]

   Plane objects are over ℤ x ℤ with no box; "up to translation" is the
   genuine Setoid quotient, so nothing about the box is smuggled into the
   definition being counted against.

   FRAGILE POINTS, listed honestly (mechanical, not mathematical — each has a
   local repair if the compile trips on it):
     1. `SimpleGraph.connected_iff` — used to assemble Connected from
        Preconnected + Nonempty in `connected_map_surj`. If renamed, replace
        with the structure's anonymous constructor.
     2. `add_neg_cancel` — older Mathlib called it `add_right_neg`.
     3. `Int.toNat_natCast` (in `toN_toZ`'s simp set) — older name
        `Int.toNat_coe_nat`.
     4. `obtain ⟨a⟩ := c` on a `Quotient` in the surjectivity branch — if
        rcases balks, use `induction c using Quotient.ind`.
     5. `omega` is asked to read `Int.toNat`, ℕ→ℤ casts, and ℕ subtraction
        (all documented omega features), but never a bare `Prod` projection:
        every projection-of-mk goal is first reduced by an explicit `show`.
     6. `animalSetoid` is declared as an `instance` so that `Quotient.exact`
        / `Quotient.sound` resolve `≈` without plumbing.
   No step of either claim RESISTED: both are complete written proofs.

   The Part-0 block below must be a verbatim copy of
   r3_l5_king_connected.lean lines 30-62 (the definitions whose meaning these
   theorems pin down). Referee check:

     diff <(sed -n '30,62p' r3_l5_king_connected.lean) \
          <(awk '/^-- BEGIN COPY/{f=1;next}/^-- END COPY/{f=0}f' \
              r3_l5_normalization.lean)

   Both files use namespace R3L5; they are elaborated separately (one
   `lake env lean` each), never together, so the duplicate names never meet.
-/
import Mathlib

namespace R3L5

/- ===================================================================
   PART 0 — verbatim copy of the definitions under scrutiny
   =================================================================== -/
-- BEGIN COPY
abbrev Cell := ℕ × ℕ

/-- King (Chebyshev-distance-1) adjacency on cells. -/
def kingAdj (p q : Cell) : Prop :=
  p ≠ q ∧ p.1 ≤ q.1 + 1 ∧ q.1 ≤ p.1 + 1 ∧ p.2 ≤ q.2 + 1 ∧ q.2 ≤ p.2 + 1

instance (p q : Cell) : Decidable (kingAdj p q) := by
  unfold kingAdj; infer_instance

/-- The king graph induced on a finite cell set `s`. -/
def kingGraph (s : Finset Cell) : SimpleGraph {x // x ∈ s} where
  Adj a b := kingAdj a.1 b.1
  symm := ⟨fun _ _ h => ⟨h.1.symm, h.2.2.1, h.2.1, h.2.2.2.2, h.2.2.2.1⟩⟩
  loopless := ⟨fun _ h => h.1 rfl⟩

instance (s : Finset Cell) : DecidableRel (kingGraph s).Adj :=
  fun a b => inferInstanceAs (Decidable (kingAdj a.1 b.1))

/-- Normalized king animal of height exactly H inside its domain box:
    touches column 0 (min-x = 0), row 0 (min-y = 0), row H-1 (height H),
    and is king-connected. Cardinality and the box bounds are enforced by
    the domain in `T` below. -/
def isAnimal (H : ℕ) (s : Finset Cell) : Prop :=
  (∃ p ∈ s, p.1 = 0) ∧ (∃ p ∈ s, p.2 = 0) ∧ (∃ p ∈ s, p.2 = H - 1) ∧
  (kingGraph s).Connected

instance (H : ℕ) : DecidablePred (isAnimal H) := fun s => by
  unfold isAnimal; infer_instance

/-- The triangle cell T(n,H), by definition. -/
def T (n H : ℕ) : ℕ :=
  ((((Finset.range n) ×ˢ (Finset.range H)).powersetCard n).filter
    (isAnimal H)).card
-- END COPY

/-- The Finset whose card is `T n H`, named so `T_eq_card_counted` is `rfl`. -/
def counted (n H : ℕ) : Finset (Finset Cell) :=
  (((Finset.range n) ×ˢ (Finset.range H)).powersetCard n).filter (isAnimal H)

theorem T_eq_card_counted (n H : ℕ) : T n H = (counted n H).card := rfl

/- ===================================================================
   PART 1 — the plane (ℤ x ℤ) objects: no box, honest translations
   =================================================================== -/

abbrev ZCell := ℤ × ℤ

/-- King adjacency on the plane. -/
def kingAdjZ (p q : ZCell) : Prop :=
  p ≠ q ∧ |p.1 - q.1| ≤ 1 ∧ |p.2 - q.2| ≤ 1

/-- The king graph induced on a finite plane cell set. -/
def kingGraphZ (s : Finset ZCell) : SimpleGraph {x // x ∈ s} where
  Adj a b := kingAdjZ a.1 b.1
  symm := by
    rintro a b ⟨hne, hx, hy⟩
    exact ⟨hne.symm, by rwa [abs_sub_comm], by rwa [abs_sub_comm]⟩
  loopless := by rintro a ⟨hne, -, -⟩; exact hne rfl

/-- Translate every cell of `s` by `v`. -/
def translate (v : ℤ × ℤ) (s : Finset ZCell) : Finset ZCell :=
  s.image fun p => (p.1 + v.1, p.2 + v.2)

/-- A plane king animal: n cells, king-connected, bounding-box height
    exactly H (y0 = the min row, y0 + H - 1 = the max row, both attained). -/
def IsAnimalZ (n H : ℕ) (s : Finset ZCell) : Prop :=
  s.card = n ∧ (kingGraphZ s).Connected ∧
  ∃ y0 : ℤ, (∀ p ∈ s, y0 ≤ p.2 ∧ p.2 ≤ y0 + (H : ℤ) - 1) ∧
    (∃ p ∈ s, p.2 = y0) ∧ (∃ p ∈ s, p.2 = y0 + (H : ℤ) - 1)

/-- Translation-normalized: all coordinates nonnegative, min-x = 0 and
    min-y = 0 both attained. -/
def IsNormalized (s : Finset ZCell) : Prop :=
  (∀ p ∈ s, 0 ≤ p.1 ∧ 0 ≤ p.2) ∧ (∃ p ∈ s, p.1 = 0) ∧ (∃ p ∈ s, p.2 = 0)

/- ------------------------------------------------------------------
   Small translation toolkit
   ------------------------------------------------------------------ -/

lemma translate_injective (v : ℤ × ℤ) :
    Function.Injective (fun p : ZCell => (p.1 + v.1, p.2 + v.2)) := by
  rintro ⟨a1, a2⟩ ⟨b1, b2⟩ h
  simp only [Prod.mk.injEq] at h ⊢
  omega

lemma mem_translate {v : ℤ × ℤ} {s : Finset ZCell} {p : ZCell} :
    p ∈ translate v s ↔ (p.1 - v.1, p.2 - v.2) ∈ s := by
  unfold translate
  rw [Finset.mem_image]
  constructor
  · rintro ⟨q, hq, rfl⟩
    have hq' : ((q.1 + v.1 - v.1 : ℤ), (q.2 + v.2 - v.2 : ℤ)) = q := by
      rw [Prod.ext_iff]
      constructor
      · show q.1 + v.1 - v.1 = q.1; ring
      · show q.2 + v.2 - v.2 = q.2; ring
    show ((q.1 + v.1 - v.1 : ℤ), (q.2 + v.2 - v.2 : ℤ)) ∈ s
    rwa [hq']
  · intro h
    refine ⟨(p.1 - v.1, p.2 - v.2), h, ?_⟩
    show (p.1 - v.1 + v.1, p.2 - v.2 + v.2) = p
    rw [Prod.ext_iff]
    constructor
    · show p.1 - v.1 + v.1 = p.1; ring
    · show p.2 - v.2 + v.2 = p.2; ring

lemma translate_zero (s : Finset ZCell) : translate (0 : ℤ × ℤ) s = s := by
  ext p
  unfold translate
  rw [Finset.mem_image]
  constructor
  · rintro ⟨q, hq, rfl⟩
    have hq' : ((q.1 + (0 : ℤ × ℤ).1, q.2 + (0 : ℤ × ℤ).2) : ZCell) = q := by
      rw [Prod.ext_iff]
      constructor
      · show q.1 + 0 = q.1; ring
      · show q.2 + 0 = q.2; ring
    show ((q.1 + (0 : ℤ × ℤ).1, q.2 + (0 : ℤ × ℤ).2) : ZCell) ∈ s
    rwa [hq']
  · intro hp
    refine ⟨p, hp, ?_⟩
    show (p.1 + 0, p.2 + 0) = p
    rw [Prod.ext_iff]
    constructor
    · show p.1 + 0 = p.1; ring
    · show p.2 + 0 = p.2; ring

lemma translate_translate (v w : ℤ × ℤ) (s : Finset ZCell) :
    translate w (translate v s) = translate (v + w) s := by
  unfold translate
  rw [Finset.image_image]
  apply Finset.image_congr
  intro p _
  simp only [Function.comp_apply, Prod.mk.injEq, Prod.fst_add, Prod.snd_add]
  constructor <;> ring

/- ------------------------------------------------------------------
   Connectivity transport (surjective graph homs)
   ------------------------------------------------------------------ -/

/-- Connectivity transports along any surjective graph homomorphism.
    (Mathlib's `SimpleGraph.Connected.map` states the same; hand-proved here
    to keep the identifier surface small.) -/
private lemma connected_map_surj {V W : Type*} {G : SimpleGraph V}
    {G' : SimpleGraph W} (f : G →g G') (hsurj : Function.Surjective f)
    (h : G.Connected) : G'.Connected := by
  rw [SimpleGraph.connected_iff]
  constructor
  · intro a b
    obtain ⟨a', rfl⟩ := hsurj a
    obtain ⟨b', rfl⟩ := hsurj b
    obtain ⟨w⟩ := h.preconnected a' b'
    exact ⟨w.map f⟩
  · obtain ⟨v⟩ := h.nonempty
    exact ⟨f v⟩

/-- Translation is a (surjective) isomorphism of induced king graphs. -/
lemma connected_translate (v : ℤ × ℤ) {s : Finset ZCell}
    (h : (kingGraphZ s).Connected) : (kingGraphZ (translate v s)).Connected := by
  let f : kingGraphZ s →g kingGraphZ (translate v s) :=
    { toFun := fun p =>
        ⟨(p.1.1 + v.1, p.1.2 + v.2), Finset.mem_image_of_mem _ p.2⟩
      map_rel' := by
        rintro ⟨p, hp⟩ ⟨q, hq⟩ hpq
        obtain ⟨hne, hx, hy⟩ := (show kingAdjZ p q from hpq)
        rw [abs_le] at hx hy
        show (p.1 + v.1, p.2 + v.2) ≠ (q.1 + v.1, q.2 + v.2) ∧
          |(p.1 + v.1) - (q.1 + v.1)| ≤ 1 ∧ |(p.2 + v.2) - (q.2 + v.2)| ≤ 1
        refine ⟨?_, by rw [abs_le]; omega, by rw [abs_le]; omega⟩
        intro hEq
        rw [Prod.mk.injEq] at hEq
        exact hne (Prod.ext_iff.mpr ⟨by omega, by omega⟩) }
  refine connected_map_surj f ?_ h
  rintro ⟨p, hp⟩
  rw [mem_translate] at hp
  refine ⟨⟨(p.1 - v.1, p.2 - v.2), hp⟩, Subtype.ext ?_⟩
  show (p.1 - v.1 + v.1, p.2 - v.2 + v.2) = p
  rw [Prod.ext_iff]
  constructor
  · show p.1 - v.1 + v.1 = p.1; ring
  · show p.2 - v.2 + v.2 = p.2; ring

/-- Being a plane animal is translation-invariant. -/
lemma isAnimalZ_translate {n H : ℕ} (v : ℤ × ℤ) {s : Finset ZCell}
    (h : IsAnimalZ n H s) : IsAnimalZ n H (translate v s) := by
  obtain ⟨hcard, hconn, y0, hbd, ⟨plo, hplo, hploy⟩, ⟨phi, hphi, hphiy⟩⟩ := h
  refine ⟨?_, connected_translate v hconn, y0 + v.2, ?_, ?_, ?_⟩
  · unfold translate
    rw [Finset.card_image_of_injective _ (translate_injective v)]
    exact hcard
  · intro p hp
    rw [mem_translate] at hp
    have hb : y0 ≤ p.2 - v.2 ∧ p.2 - v.2 ≤ y0 + (H : ℤ) - 1 := hbd _ hp
    omega
  · refine ⟨(plo.1 + v.1, plo.2 + v.2), Finset.mem_image_of_mem _ hplo, ?_⟩
    show plo.2 + v.2 = y0 + v.2
    omega
  · refine ⟨(phi.1 + v.1, phi.2 + v.2), Finset.mem_image_of_mem _ hphi, ?_⟩
    show phi.2 + v.2 = y0 + v.2 + (H : ℤ) - 1
    omega

/- ===================================================================
   PART 2 — CLAIM 1: width <= n (the domain box loses nothing)
   =================================================================== -/

/-- Discrete intermediate-value theorem along a king walk: the x-coordinate
    changes by at most 1 per step, so every column between the endpoints'
    columns is visited. This is the prose argument in the original file's
    header, as a theorem. -/
lemma walk_hits_column {s : Finset ZCell} {a b : {x // x ∈ s}}
    (w : (kingGraphZ s).Walk a b) :
    ∀ x : ℤ, ((a.1.1 ≤ x ∧ x ≤ b.1.1) ∨ (b.1.1 ≤ x ∧ x ≤ a.1.1)) →
      ∃ p ∈ w.support, p.1.1 = x := by
  induction w with
  | nil =>
      intro x hx
      refine ⟨a, by simp [SimpleGraph.Walk.support_nil], by omega⟩
  | @cons u v c hadj w ih =>
      intro x hx
      have hadj' : u.1 ≠ v.1 ∧ |u.1.1 - v.1.1| ≤ 1 ∧ |u.1.2 - v.1.2| ≤ 1 := hadj
      obtain ⟨-, hxd, -⟩ := hadj'
      rw [abs_le] at hxd
      by_cases hmid : (v.1.1 ≤ x ∧ x ≤ c.1.1) ∨ (c.1.1 ≤ x ∧ x ≤ v.1.1)
      · obtain ⟨p, hp, hpx⟩ := ih x hmid
        refine ⟨p, ?_, hpx⟩
        rw [SimpleGraph.Walk.support_cons]
        exact List.mem_cons_of_mem _ hp
      · refine ⟨u, ?_, by omega⟩
        rw [SimpleGraph.Walk.support_cons]
        simp

/-- Column-interval property of a connected plane set. -/
lemma connected_hits_column {s : Finset ZCell}
    (hc : (kingGraphZ s).Connected) {p q : ZCell} (hp : p ∈ s) (hq : q ∈ s)
    {x : ℤ} (hx : p.1 ≤ x ∧ x ≤ q.1) : ∃ r ∈ s, r.1 = x := by
  obtain ⟨w⟩ := hc.preconnected ⟨p, hp⟩ ⟨q, hq⟩
  obtain ⟨r, -, hrx⟩ := walk_hits_column w x (Or.inl hx)
  exact ⟨r.1, r.2, hrx⟩

/-- CLAIM 1, core: a normalized plane animal with n cells has every
    x-coordinate < n. (If some cell had x >= n, columns 0..n would all be
    occupied — n+1 distinct columns — but n cells occupy at most n.) -/
theorem width_lt_of_normalized {n H : ℕ} {s : Finset ZCell}
    (ha : IsAnimalZ n H s) (hn : IsNormalized s) :
    ∀ p ∈ s, p.1 < (n : ℤ) := by
  obtain ⟨hcard, hconn, -⟩ := ha
  obtain ⟨-, ⟨p0, hp0, hp0x⟩, -⟩ := hn
  intro p hp
  by_contra hbig
  push_neg at hbig
  have hcols : Finset.Icc (0 : ℤ) (n : ℤ) ⊆ s.image Prod.fst := by
    intro x hx
    rw [Finset.mem_Icc] at hx
    obtain ⟨r, hr, hrx⟩ :=
      connected_hits_column hconn hp0 hp ⟨by omega, by omega⟩
    exact Finset.mem_image.mpr ⟨r, hr, hrx⟩
  have hle := Finset.card_le_card hcols
  rw [Int.card_Icc] at hle
  have himg := Finset.card_image_le (s := s) (f := Prod.fst)
  omega

/-- Height exactly H forces H >= 1 (the top row exists). -/
lemma one_le_H {n H : ℕ} {s : Finset ZCell} (ha : IsAnimalZ n H s) : 1 ≤ H := by
  obtain ⟨-, -, y0, hbd, -, ⟨phi, hphi, hphiy⟩⟩ := ha
  have h1 := (hbd phi hphi).1
  omega

/-- Rows of a normalized plane animal: all in [0, H-1], top row attained. -/
theorem rows_of_normalized {n H : ℕ} {s : Finset ZCell}
    (ha : IsAnimalZ n H s) (hn : IsNormalized s) :
    (∀ p ∈ s, 0 ≤ p.2 ∧ p.2 ≤ (H : ℤ) - 1) ∧
      (∃ p ∈ s, p.2 = (H : ℤ) - 1) := by
  obtain ⟨-, -, y0, hbd, ⟨plo, hplo, hploy⟩, ⟨phi, hphi, hphiy⟩⟩ := ha
  obtain ⟨hnn, -, ⟨p0, hp0, hp0y⟩⟩ := hn
  have hy0 : y0 = 0 := by
    have h1 := (hbd p0 hp0).1
    have h2 := (hnn plo hplo).2
    omega
  constructor
  · intro p hp
    have h1 := (hnn p hp).2
    have h2 := (hbd p hp).2
    omega
  · exact ⟨phi, hphi, by omega⟩

/-- CLAIM 1, packaged: a normalized plane (n,H)-animal lives in the domain
    box [0,n) x [0,H). Nothing is lost by enumerating inside it. -/
theorem normalized_in_box {n H : ℕ} {s : Finset ZCell}
    (ha : IsAnimalZ n H s) (hn : IsNormalized s) :
    ∀ p ∈ s, 0 ≤ p.1 ∧ p.1 < (n : ℤ) ∧ 0 ≤ p.2 ∧ p.2 < (H : ℤ) := by
  intro p hp
  have h1 := hn.1 p hp
  have h2 := width_lt_of_normalized ha hn p hp
  have h3 := (rows_of_normalized ha hn).1 p hp
  exact ⟨h1.1, h2, h1.2, by omega⟩

/- ===================================================================
   PART 3 — the transversal: exactly one normalizing translate
   =================================================================== -/

/-- CLAIM 2, half 1: every plane animal has exactly one translate that is
    normalized. Existence translates by (-min x, -min y); uniqueness because
    normalization pins both minima and translation shifts them faithfully. -/
theorem existsUnique_normalizing_translate {n H : ℕ} {s : Finset ZCell}
    (ha : IsAnimalZ n H s) :
    ∃! v : ℤ × ℤ, IsNormalized (translate v s) := by
  have hne : s.Nonempty := by
    obtain ⟨-, hconn, -⟩ := ha
    obtain ⟨⟨p, hp⟩⟩ := hconn.nonempty
    exact ⟨p, hp⟩
  -- a least-x cell and a least-y cell (no `min'`, so no proof-term mismatch)
  obtain ⟨qx, hqx, hxmin⟩ := s.exists_min_image Prod.fst hne
  obtain ⟨qy, hqy, hymin⟩ := s.exists_min_image Prod.snd hne
  refine ⟨(-qx.1, -qy.2), ⟨?_, ?_, ?_⟩, ?_⟩
  -- all coordinates nonnegative after the shift
  · intro p hp
    rw [mem_translate] at hp
    have h1 : qx.1 ≤ p.1 - -qx.1 := hxmin _ hp
    have h2 : qy.2 ≤ p.2 - -qy.2 := hymin _ hp
    omega
  -- x = 0 attained (image of the least-x cell)
  · refine ⟨(qx.1 + -qx.1, qx.2 + -qy.2), Finset.mem_image_of_mem _ hqx, ?_⟩
    show qx.1 + -qx.1 = 0
    omega
  -- y = 0 attained (image of the least-y cell)
  · refine ⟨(qy.1 + -qx.1, qy.2 + -qy.2), Finset.mem_image_of_mem _ hqy, ?_⟩
    show qy.2 + -qy.2 = 0
    omega
  -- uniqueness
  · rintro w ⟨hwnn, ⟨pw, hpwm, hpwx⟩, ⟨pv, hpvm, hpvy⟩⟩
    -- every cell of s lands at nonnegative coordinates under w
    have hub : ∀ q ∈ s, -w.1 ≤ q.1 ∧ -w.2 ≤ q.2 := by
      intro q hq
      have hmem : (q.1 + w.1, q.2 + w.2) ∈ translate w s :=
        Finset.mem_image_of_mem _ hq
      have h' : 0 ≤ q.1 + w.1 ∧ 0 ≤ q.2 + w.2 := hwnn _ hmem
      omega
    -- and some cell of s sits at x = -w.1, some at y = -w.2
    rw [mem_translate] at hpwm hpvm
    have hxle : qx.1 ≤ pw.1 - w.1 := hxmin _ hpwm
    have hyle : qy.2 ≤ pv.2 - w.2 := hymin _ hpvm
    have hxge := (hub qx hqx).1
    have hyge := (hub qy hqy).2
    -- qx.1 = -w.1 and qy.2 = -w.2, hence w = (-qx.1, -qy.2)
    rw [Prod.ext_iff]
    constructor
    · show w.1 = -qx.1; omega
    · show w.2 = -qy.2; omega

/- ===================================================================
   PART 4 — the bridge between the plane picture and the ℕ box
   =================================================================== -/

/-- Forget signs (valid on normalized sets). -/
def toN (s : Finset ZCell) : Finset Cell :=
  s.image fun p => (p.1.toNat, p.2.toNat)

/-- Embed the box into the plane. -/
def toZ (t : Finset Cell) : Finset ZCell :=
  t.image fun p => ((p.1 : ℤ), (p.2 : ℤ))

lemma castPair_injective :
    Function.Injective (fun p : Cell => ((p.1 : ℤ), (p.2 : ℤ))) := by
  rintro ⟨a1, a2⟩ ⟨b1, b2⟩ h
  simp only [Prod.mk.injEq] at h ⊢
  omega

lemma toN_toZ (t : Finset Cell) : toN (toZ t) = t := by
  unfold toN toZ
  rw [Finset.image_image]
  have h : ∀ p ∈ t,
      ((fun q : ZCell => (q.1.toNat, q.2.toNat)) ∘
        fun q : Cell => ((q.1 : ℤ), (q.2 : ℤ))) p = id p := by
    intro p _
    simp only [Function.comp_apply, id_eq]
    show (((p.1 : ℤ)).toNat, ((p.2 : ℤ)).toNat) = p
    rw [Prod.ext_iff]
    constructor
    · show ((p.1 : ℤ)).toNat = p.1; omega
    · show ((p.2 : ℤ)).toNat = p.2; omega
  rw [Finset.image_congr h, Finset.image_id]

lemma toZ_toN {s : Finset ZCell} (hpos : ∀ p ∈ s, 0 ≤ p.1 ∧ 0 ≤ p.2) :
    toZ (toN s) = s := by
  unfold toN toZ
  rw [Finset.image_image]
  ext p
  rw [Finset.mem_image]
  constructor
  · rintro ⟨q, hq, rfl⟩
    obtain ⟨h1, h2⟩ := hpos q hq
    have hq' : ((fun r : Cell => ((r.1 : ℤ), (r.2 : ℤ))) ∘
        fun r : ZCell => (r.1.toNat, r.2.toNat)) q = q := by
      simp only [Function.comp_apply]
      show (((q.1.toNat : ℕ) : ℤ), ((q.2.toNat : ℕ) : ℤ)) = q
      rw [Prod.ext_iff]
      constructor
      · show ((q.1.toNat : ℕ) : ℤ) = q.1; omega
      · show ((q.2.toNat : ℕ) : ℤ) = q.2; omega
    rwa [hq']
  · intro hp
    refine ⟨p, hp, ?_⟩
    obtain ⟨h1, h2⟩ := hpos p hp
    simp only [Function.comp_apply]
    show (((p.1.toNat : ℕ) : ℤ), ((p.2.toNat : ℕ) : ℤ)) = p
    rw [Prod.ext_iff]
    constructor
    · show ((p.1.toNat : ℕ) : ℤ) = p.1; omega
    · show ((p.2.toNat : ℕ) : ℤ) = p.2; omega

/-- Connectivity descends from the plane graph to the box graph. -/
lemma connected_toN {s : Finset ZCell}
    (hpos : ∀ p ∈ s, 0 ≤ p.1 ∧ 0 ≤ p.2)
    (h : (kingGraphZ s).Connected) : (kingGraph (toN s)).Connected := by
  let f : kingGraphZ s →g kingGraph (toN s) :=
    { toFun := fun p =>
        ⟨(p.1.1.toNat, p.1.2.toNat), Finset.mem_image_of_mem _ p.2⟩
      map_rel' := by
        rintro ⟨p, hp⟩ ⟨q, hq⟩ hpq
        obtain ⟨hp1, hp2⟩ := hpos p hp
        obtain ⟨hq1, hq2⟩ := hpos q hq
        obtain ⟨hne, hx, hy⟩ := (show kingAdjZ p q from hpq)
        rw [abs_le] at hx hy
        show (p.1.toNat, p.2.toNat) ≠ (q.1.toNat, q.2.toNat) ∧
          p.1.toNat ≤ q.1.toNat + 1 ∧ q.1.toNat ≤ p.1.toNat + 1 ∧
          p.2.toNat ≤ q.2.toNat + 1 ∧ q.2.toNat ≤ p.2.toNat + 1
        refine ⟨?_, by omega, by omega, by omega, by omega⟩
        intro hEq
        rw [Prod.mk.injEq] at hEq
        exact hne (Prod.ext_iff.mpr ⟨by omega, by omega⟩) }
  refine connected_map_surj f ?_ h
  rintro ⟨p, hp⟩
  obtain ⟨q, hq, hqp⟩ := Finset.mem_image.mp hp
  exact ⟨⟨q, hq⟩, Subtype.ext hqp⟩

/-- Connectivity lifts from the box graph to the plane graph. -/
lemma connected_toZ {t : Finset Cell}
    (h : (kingGraph t).Connected) : (kingGraphZ (toZ t)).Connected := by
  let f : kingGraph t →g kingGraphZ (toZ t) :=
    { toFun := fun p =>
        ⟨((p.1.1 : ℤ), (p.1.2 : ℤ)), Finset.mem_image_of_mem _ p.2⟩
      map_rel' := by
        rintro ⟨p, hp⟩ ⟨q, hq⟩ hpq
        obtain ⟨hne, h1, h2, h3, h4⟩ := (show kingAdj p q from hpq)
        show ((p.1 : ℤ), (p.2 : ℤ)) ≠ ((q.1 : ℤ), (q.2 : ℤ)) ∧
          |(p.1 : ℤ) - (q.1 : ℤ)| ≤ 1 ∧ |(p.2 : ℤ) - (q.2 : ℤ)| ≤ 1
        refine ⟨?_, by rw [abs_le]; omega, by rw [abs_le]; omega⟩
        intro hEq
        rw [Prod.mk.injEq] at hEq
        exact hne (Prod.ext_iff.mpr ⟨by omega, by omega⟩) }
  refine connected_map_surj f ?_ h
  rintro ⟨p, hp⟩
  obtain ⟨q, hq, hqp⟩ := Finset.mem_image.mp hp
  exact ⟨⟨q, hq⟩, Subtype.ext hqp⟩

/-- The membership characterization: the sets `T n H` counts are exactly the
    box shadows of normalized plane (n,H)-animals. This is the precise
    statement of "the domain box loses nothing". -/
theorem mem_counted_iff_normalized_animal {n H : ℕ} (t : Finset Cell) :
    t ∈ counted n H ↔ IsAnimalZ n H (toZ t) ∧ IsNormalized (toZ t) := by
  unfold counted
  rw [Finset.mem_filter, Finset.mem_powersetCard]
  constructor
  · rintro ⟨⟨hsub, hcard⟩, hx0, hy0, hyH, hconn⟩
    have hbox : ∀ q ∈ t, q.1 < n ∧ q.2 < H := by
      intro q hq
      have h := hsub hq
      simp only [Finset.mem_product, Finset.mem_range] at h
      exact h
    refine ⟨⟨?_, connected_toZ hconn, 0, ?_, ?_, ?_⟩, ?_, ?_, ?_⟩
    -- card
    · unfold toZ
      rw [Finset.card_image_of_injective _ castPair_injective]
      exact hcard
    -- row bounds around y0 = 0
    · intro p hp
      simp only [toZ, Finset.mem_image] at hp
      obtain ⟨q, hq, rfl⟩ := hp
      have hb := hbox q hq
      refine ⟨?_, ?_⟩
      · show (0 : ℤ) ≤ (q.2 : ℤ); omega
      · show (q.2 : ℤ) ≤ 0 + (H : ℤ) - 1; omega
    -- bottom row attained
    · obtain ⟨q, hq, hq2⟩ := hy0
      refine ⟨((q.1 : ℤ), (q.2 : ℤ)), ?_, ?_⟩
      · simp only [toZ, Finset.mem_image]; exact ⟨q, hq, rfl⟩
      · show (q.2 : ℤ) = 0; omega
    -- top row attained (needs H >= 1, which the box membership supplies)
    · obtain ⟨q, hq, hq2⟩ := hyH
      have hb := hbox q hq
      refine ⟨((q.1 : ℤ), (q.2 : ℤ)), ?_, ?_⟩
      · simp only [toZ, Finset.mem_image]; exact ⟨q, hq, rfl⟩
      · show (q.2 : ℤ) = 0 + (H : ℤ) - 1; omega
    -- all coordinates nonnegative
    · intro p hp
      simp only [toZ, Finset.mem_image] at hp
      obtain ⟨q, hq, rfl⟩ := hp
      refine ⟨?_, ?_⟩
      · show (0 : ℤ) ≤ (q.1 : ℤ); omega
      · show (0 : ℤ) ≤ (q.2 : ℤ); omega
    -- column 0 attained
    · obtain ⟨q, hq, hq1⟩ := hx0
      refine ⟨((q.1 : ℤ), (q.2 : ℤ)), ?_, ?_⟩
      · simp only [toZ, Finset.mem_image]; exact ⟨q, hq, rfl⟩
      · show (q.1 : ℤ) = 0; omega
    -- row 0 attained
    · obtain ⟨q, hq, hq2⟩ := hy0
      refine ⟨((q.1 : ℤ), (q.2 : ℤ)), ?_, ?_⟩
      · simp only [toZ, Finset.mem_image]; exact ⟨q, hq, rfl⟩
      · show (q.2 : ℤ) = 0; omega
  · rintro ⟨ha, hn⟩
    have hbox := normalized_in_box ha hn
    have hrows := rows_of_normalized ha hn
    have hposz : ∀ p ∈ toZ t, 0 ≤ p.1 ∧ 0 ≤ p.2 := fun p hp => by
      have h := hbox p hp
      exact ⟨h.1, h.2.2.1⟩
    refine ⟨⟨?_, ?_⟩, ?_, ?_, ?_, ?_⟩
    -- t sits inside the box
    · intro q hq
      have hqz : ((q.1 : ℤ), (q.2 : ℤ)) ∈ toZ t := by
        simp only [toZ, Finset.mem_image]; exact ⟨q, hq, rfl⟩
      have hb : (0 : ℤ) ≤ (q.1 : ℤ) ∧ (q.1 : ℤ) < (n : ℤ) ∧
          (0 : ℤ) ≤ (q.2 : ℤ) ∧ (q.2 : ℤ) < (H : ℤ) := hbox _ hqz
      simp only [Finset.mem_product, Finset.mem_range]
      omega
    -- card
    · have hc : (toZ t).card = n := ha.1
      have hct : (toZ t).card = t.card := by
        unfold toZ
        rw [Finset.card_image_of_injective _ castPair_injective]
      omega
    -- touches column 0
    · obtain ⟨p, hp, hp1⟩ := hn.2.1
      simp only [toZ, Finset.mem_image] at hp
      obtain ⟨q, hq, rfl⟩ := hp
      have hp1' : (q.1 : ℤ) = 0 := hp1
      exact ⟨q, hq, by omega⟩
    -- touches row 0
    · obtain ⟨p, hp, hp2⟩ := hn.2.2
      simp only [toZ, Finset.mem_image] at hp
      obtain ⟨q, hq, rfl⟩ := hp
      have hp2' : (q.2 : ℤ) = 0 := hp2
      exact ⟨q, hq, by omega⟩
    -- touches row H-1
    · obtain ⟨p, hp, hp2⟩ := hrows.2
      simp only [toZ, Finset.mem_image] at hp
      obtain ⟨q, hq, rfl⟩ := hp
      have hp2' : (q.2 : ℤ) = (H : ℤ) - 1 := hp2
      have h1H := one_le_H ha
      exact ⟨q, hq, by omega⟩
    -- connected
    · have hcN := connected_toN hposz ha.2.1
      rwa [toN_toZ] at hcN

/- ===================================================================
   PART 5 — the headline counts
   =================================================================== -/

/-- `counted n H` and the normalized plane animals are in bijection via
    `toZ` / `toN`. -/
def countedEquivNormalized (n H : ℕ) :
    {t // t ∈ counted n H} ≃
      {s : Finset ZCell // IsAnimalZ n H s ∧ IsNormalized s} where
  toFun t := ⟨toZ t.1, (mem_counted_iff_normalized_animal t.1).mp t.2⟩
  invFun s := ⟨toN s.1, by
    have hz : toZ (toN s.1) = s.1 := toZ_toN s.2.2.1
    rw [mem_counted_iff_normalized_animal, hz]
    exact s.2⟩
  left_inv t := Subtype.ext (toN_toZ t.1)
  right_inv s := Subtype.ext (toZ_toN s.2.2.1)

/-- T(n,H) counts the normalized plane animals. -/
theorem T_eq_card_normalized (n H : ℕ) :
    T n H =
      Nat.card {s : Finset ZCell // IsAnimalZ n H s ∧ IsNormalized s} := by
  rw [← Nat.card_congr (countedEquivNormalized n H),
    Nat.card_eq_fintypeCard, Fintype.card_coe]
  rfl

/-- Translation equivalence on plane animals. Declared as an instance so the
    Quotient API (`Quotient.exact`/`Quotient.sound`) resolves without
    plumbing. -/
instance animalSetoid (n H : ℕ) :
    Setoid {s : Finset ZCell // IsAnimalZ n H s} where
  r a b := ∃ v : ℤ × ℤ, translate v a.1 = b.1
  iseqv := by
    refine ⟨fun a => ⟨0, translate_zero a.1⟩, ?_, ?_⟩
    · rintro a b ⟨v, hv⟩
      refine ⟨-v, ?_⟩
      rw [← hv, translate_translate, add_neg_cancel, translate_zero]
    · rintro a b c ⟨v, hv⟩ ⟨w, hw⟩
      refine ⟨v + w, ?_⟩
      rw [← hw, ← hv, translate_translate]

/-- CLAIM 2, headline: T(n,H) is the number of translation classes of
    king-connected n-cell subsets of the plane with bounding-box height
    exactly H. The quotient is the honest one — plane sets, genuine
    translations — and the bijection routes through the unique normalized
    representative of each class. -/
theorem T_eq_card_translationClasses (n H : ℕ) :
    T n H = Nat.card (Quotient (animalSetoid n H)) := by
  rw [T_eq_card_normalized]
  refine Nat.card_congr (Equiv.ofBijective
    (fun s => Quotient.mk (animalSetoid n H) ⟨s.1, s.2.1⟩) ⟨?_, ?_⟩)
  -- injective: two equivalent normalized animals are equal, because the
  -- normalizing translate is unique and both 0 and v normalize the first
  · rintro ⟨s, hsa, hsn⟩ ⟨t, hta, htn⟩ hEq
    obtain ⟨v, hv⟩ := Quotient.exact hEq
    obtain ⟨w, -, huniq⟩ := existsUnique_normalizing_translate hsa
    have h0 : (0 : ℤ × ℤ) = w := huniq 0 (by rwa [translate_zero])
    have hvw : v = w := huniq v (by rwa [hv])
    have hv0 : v = 0 := hvw.trans h0.symm
    rw [hv0, translate_zero] at hv
    exact Subtype.ext hv
  -- surjective: every class contains its normalized representative
  · intro c
    obtain ⟨a⟩ := c
    obtain ⟨v, hnorm, -⟩ := existsUnique_normalizing_translate a.2
    refine ⟨⟨translate v a.1, isAnimalZ_translate v a.2, hnorm⟩, ?_⟩
    apply Quotient.sound
    refine ⟨-v, ?_⟩
    rw [translate_translate, add_neg_cancel, translate_zero]

end R3L5
