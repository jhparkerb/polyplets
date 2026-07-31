/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Sequence

/-!
# A rigorous exponential upper bound: `a n ≤ C(5n, n)`

`Sequence.lean` names the sequence `a n` but says nothing about its size. This
file supplies the paper's crude decision-tree bound (§3): a deterministic
exploration reconstructs any `n`-cell king animal from at most `5n` yes/no
membership decisions, exactly `n` of which are "yes", so

* `a_le_choose` : `a n ≤ Nat.choose (5 * n) n`,

and the elementary ratio estimate

* `choose_le_pow` : `Nat.choose (5 * n) n * 256 ^ n ≤ 3125 ^ n`

turns that into the growth-rate ceiling `λ ≤ 5⁵/4⁴ = 3125/256` once the limit
is available (the limit itself is not built here).

## The exploration

Every canonical animal is first re-anchored: `expShape S` translates `S` so that
its scan-least cell (row-major, `y` before `x`) sits at the origin. Canonicity
pins the translation back, so `expShape` is injective (`expShape_injOn`), and the
the shape is what the exploration reconstructs.

The exploration is a breadth-first flood from the origin, run as a pure
transition function `expStep : ExpState → Bool → ExpState` on a queue of
*candidates*. Each step pops the head candidate and consumes one `Bool` — the
answer to "is this cell in the animal?". Accepted cells push their king
neighbours (those scan-greater than the origin, and not yet seen) onto the
queue. Two runs of that transition are compared:

* `runO D k` drives it with the membership oracle of a fixed shape `D`;
* `runA A k` drives it with a set `A ⊆ ℕ` of *accepting step indices*.

`runA_eq_runO` shows the second reproduces the first when `A` is the first's own
accept-position set, which is what makes `S ↦ accept positions` injective.

Two facts bound the number of steps:

* the origin proposes only `4` candidates (the other four king neighbours are
  scan-smaller, hence never cells of a expShape), and
* every later accepted cell `c` proposes at most `5`: its proposer `p` and all
  of `p`'s neighbours were already seen when `p` was accepted, and `p` shares
  at least two neighbours with `c` (`countP_new_le`).

So at most `5n` cells are ever considered, the run halts inside `5 * n` steps
(`runO_queue_nil`), and the accept positions form an `n`-subset of
`Finset.range (5 * n)`.
-/

namespace Polyplets

open Nat (factorial)

/-! ## Part 2: the ratio estimate `C(5n, n) · 256ⁿ ≤ 3125ⁿ`

Elementary and independent of the exploration, so it comes first. The engine is
the one-step factorial identity `choose_step`, which turns the induction into a
polynomial inequality with nonnegative coefficient differences. -/

/-- Five factorial peels, with the successor expShape supplied by definitional
unfolding of `Nat.add` (`m + 5` is `(m + 4) + 1`). -/
private lemma factorial_add_five (m : ℕ) :
    factorial (m + 5)
      = (m + 5) * ((m + 4) * ((m + 3) * ((m + 2) * ((m + 1) * factorial m)))) := by
  have h1 : factorial (m + 1) = (m + 1) * factorial m := Nat.factorial_succ m
  have h2 : factorial (m + 2) = (m + 2) * factorial (m + 1) := Nat.factorial_succ (m + 1)
  have h3 : factorial (m + 3) = (m + 3) * factorial (m + 2) := Nat.factorial_succ (m + 2)
  have h4 : factorial (m + 4) = (m + 4) * factorial (m + 3) := Nat.factorial_succ (m + 3)
  have h5 : factorial (m + 5) = (m + 5) * factorial (m + 4) := Nat.factorial_succ (m + 4)
  rw [h5, h4, h3, h2, h1]

/-- Four factorial peels; the companion of `factorial_add_five`. -/
private lemma factorial_add_four (m : ℕ) :
    factorial (m + 4) = (m + 4) * ((m + 3) * ((m + 2) * ((m + 1) * factorial m))) := by
  have h1 : factorial (m + 1) = (m + 1) * factorial m := Nat.factorial_succ m
  have h2 : factorial (m + 2) = (m + 2) * factorial (m + 1) := Nat.factorial_succ (m + 1)
  have h3 : factorial (m + 3) = (m + 3) * factorial (m + 2) := Nat.factorial_succ (m + 2)
  have h4 : factorial (m + 4) = (m + 4) * factorial (m + 3) := Nat.factorial_succ (m + 3)
  rw [h4, h3, h2, h1]

/-- **The one-step ratio identity for `C(5n, n)`.** Both binomial coefficients
are expanded by `Nat.choose_mul_factorial_mul_factorial`; the five numerator and
five denominator factors are peeled off the factorials, and the common factor
`n! · (4n)!` is cancelled. -/
private lemma choose_step (n : ℕ) :
    Nat.choose (5 * n + 5) (n + 1) * ((n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4)))))
      = Nat.choose (5 * n) n * ((5*n+1) * ((5*n+2) * ((5*n+3) * ((5*n+4) * (5*n+5))))) := by
  have hn : n ≤ 5 * n := Nat.le_mul_of_pos_left n (by norm_num)
  have h1 : Nat.choose (5 * n) n * factorial n * factorial (4 * n) = factorial (5 * n) := by
    have := Nat.choose_mul_factorial_mul_factorial hn
    rwa [show 5 * n - n = 4 * n by omega] at this
  have hn' : n + 1 ≤ 5 * n + 5 := by omega
  have h2 : Nat.choose (5 * n + 5) (n + 1) * factorial (n + 1) * factorial (4 * n + 4)
      = factorial (5 * n + 5) := by
    have := Nat.choose_mul_factorial_mul_factorial hn'
    rwa [show 5 * n + 5 - (n + 1) = 4 * n + 4 by omega] at this
  rw [Nat.factorial_succ, factorial_add_four, factorial_add_five] at h2
  rw [← h1] at h2
  have hpos : 0 < factorial n * factorial (4 * n) :=
    Nat.mul_pos (Nat.factorial_pos n) (Nat.factorial_pos (4 * n))
  refine Nat.eq_of_mul_eq_mul_right hpos ?_
  calc Nat.choose (5*n+5) (n+1) * ((n+1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4)))))
        * (factorial n * factorial (4 * n))
      = Nat.choose (5*n+5) (n+1) * ((n + 1) * factorial n)
          * ((4*n+4) * ((4*n+3) * ((4*n+2) * ((4*n+1) * factorial (4*n))))) := by ring
    _ = (5*n+5) * ((5*n+4) * ((5*n+3) * ((5*n+2) * ((5*n+1)
          * (Nat.choose (5*n) n * factorial n * factorial (4*n)))))) := h2
    _ = Nat.choose (5*n) n * ((5*n+1) * ((5*n+2) * ((5*n+3) * ((5*n+4) * (5*n+5)))))
          * (factorial n * factorial (4 * n)) := by ring

/-- **The coefficient check.** `3125 · (n+1)(4n+1)(4n+2)(4n+3)(4n+4)` exceeds
`256 · (5n+1)(5n+2)(5n+3)(5n+4)(5n+5)`: the `n⁵` terms cancel exactly and the
difference `400000n⁴ + 1030000n³ + 935000n² + 349280n + 44280` has nonnegative
coefficients throughout. -/
private lemma ratio_ineq (n : ℕ) :
    256 * ((5*n+1) * ((5*n+2) * ((5*n+3) * ((5*n+4) * (5*n+5)))))
      ≤ 3125 * ((n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4))))) := by
  have h : 3125 * ((n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4)))))
      = 256 * ((5*n+1) * ((5*n+2) * ((5*n+3) * ((5*n+4) * (5*n+5)))))
        + (400000 * n^4 + 1030000 * n^3 + 935000 * n^2 + 349280 * n + 44280) := by ring
  omega

/-- **`C(5n, n) · 256ⁿ ≤ 3125ⁿ`.** Induction on `n`: the one-step identity
`choose_step` converts the goal into the polynomial inequality `ratio_ineq`
after multiplying through by the (positive) denominator. -/
theorem choose_le_pow (n : ℕ) : Nat.choose (5 * n) n * 256 ^ n ≤ 3125 ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
    have hM : 0 < (n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4)))) := by positivity
    have key : Nat.choose (5 * n + 5) (n + 1) * 256 ^ (n + 1)
          * ((n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4)))))
        ≤ 3125 ^ (n + 1) * ((n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4))))) := by
      calc Nat.choose (5 * n + 5) (n + 1) * 256 ^ (n + 1)
            * ((n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4)))))
          = Nat.choose (5 * n + 5) (n + 1)
              * ((n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4))))) * 256 ^ (n + 1) := by
            ring
        _ = Nat.choose (5 * n) n
              * ((5*n+1) * ((5*n+2) * ((5*n+3) * ((5*n+4) * (5*n+5))))) * 256 ^ (n + 1) := by
            rw [choose_step]
        _ = (Nat.choose (5 * n) n * 256 ^ n)
              * (256 * ((5*n+1) * ((5*n+2) * ((5*n+3) * ((5*n+4) * (5*n+5)))))) := by ring
        _ ≤ 3125 ^ n * (3125 * ((n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4)))))) :=
            Nat.mul_le_mul ih (ratio_ineq n)
        _ = 3125 ^ (n + 1) * ((n + 1) * ((4*n+1) * ((4*n+2) * ((4*n+3) * (4*n+4))))) := by ring
    have := Nat.le_of_mul_le_mul_right key hM
    rwa [show 5 * (n + 1) = 5 * n + 5 by ring]

/-! ## King neighbourhoods, as ordered lists

The exploration needs neighbours in a *fixed order* (determinism is the whole
point), so they are produced as a `List`, not a `Finset`. Everything about the
proposal budget is a statement about `List.countP` over these eight cells. -/

/-- The eight king offsets, in a fixed order. -/
def nbrOffsets : List (ℤ × ℤ) :=
  [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

/-- The eight king neighbours of `c`, in the fixed order of `nbrOffsets`. -/
def nbrsOf (c : ℤ × ℤ) : List (ℤ × ℤ) :=
  nbrOffsets.map fun o => (c.1 + o.1, c.2 + o.2)

/-- `nbrsOf`, written out. -/
lemma nbrsOf_eq (c : ℤ × ℤ) :
    nbrsOf c = [(c.1 - 1, c.2 - 1), (c.1, c.2 - 1), (c.1 + 1, c.2 - 1),
                (c.1 - 1, c.2), (c.1 + 1, c.2),
                (c.1 - 1, c.2 + 1), (c.1, c.2 + 1), (c.1 + 1, c.2 + 1)] := by
  simp [nbrsOf, nbrOffsets, sub_eq_add_neg]

/-- `nbrsOf c` lists exactly the cells king-adjacent to `c`. -/
lemma mem_nbrsOf {c q : ℤ × ℤ} : q ∈ nbrsOf c ↔ kingAdj c q := by
  obtain ⟨cx, cy⟩ := c
  obtain ⟨qx, qy⟩ := q
  rw [nbrsOf_eq]
  simp only [List.mem_cons, List.not_mem_nil, or_false, kingAdj, ne_eq, Prod.mk.injEq, abs_le]
  omega

/-- The eight neighbours are distinct. -/
lemma nbrsOf_nodup (c : ℤ × ℤ) : (nbrsOf c).Nodup := by
  obtain ⟨cx, cy⟩ := c
  rw [nbrsOf_eq]
  simp only [List.nodup_cons, List.mem_cons, List.not_mem_nil, or_false, List.nodup_nil,
    and_true, true_and, not_or, not_false_eq_true, Prod.mk.injEq]
  omega

/-- Strictly scan-greater than the origin: `(0,0) < q` in the row-major scan
order (`y` first, then `x`). Exactly the cells a shape may contain besides its
own anchor. -/
def scanPos (q : ℤ × ℤ) : Bool :=
  decide (0 < q.2) || (decide (q.2 = 0) && decide (0 < q.1))

/-- **The origin proposes only four candidates.** Of its eight king neighbours,
the four scan-predecessors `(x-1..x+1, y-1)` and `(x-1, y)` are scan-smaller
than the origin, hence never proposed. -/
lemma countP_scanPos_origin : (nbrsOf (0, 0)).countP scanPos = 4 := by decide

/-- The offset form of "far from the proposer": `o` differs from `e` and is not
king-adjacent to it, written with plain integer comparisons so that the
eight-case check below is a kernel `decide`. -/
private def offsetFar (e o : ℤ × ℤ) : Bool :=
  decide (o ≠ e) &&
    decide (¬ (e.1 - o.1 ≤ 1 ∧ o.1 - e.1 ≤ 1 ∧ e.2 - o.2 ≤ 1 ∧ o.2 - e.2 ≤ 1))

/-- **The eight-case neighbour-overlap check.** For each king offset `e`, at
most five of the eight king offsets are neither `e` itself nor king-adjacent to
`e`: an orthogonal `e` leaves three, a diagonal `e` leaves five. This is the
`|N(p) ∩ N(c)| ∈ {2, 4}` fact of the paper's decision-tree count. -/
private lemma offsetFar_count_le : ∀ e ∈ nbrOffsets, nbrOffsets.countP (offsetFar e) ≤ 5 := by
  decide

/-- **The proposal budget for a non-anchor cell.** If `c` has an already-decided
king neighbour `p`, then any predicate that only holds on cells distinct from
`p` and not adjacent to `p` selects at most five of `c`'s eight neighbours.
Applied with `P` = "scan-positive and not yet considered", `p` = the proposer of
`c`: the proposer and the two-to-four cells it shares with `c` were all recorded
when `p` was accepted. -/
lemma countP_new_le {p c : ℤ × ℤ} (h : kingAdj p c) {P : ℤ × ℤ → Bool}
    (hP : ∀ q, P q = true → q ≠ p ∧ ¬ kingAdj p q) :
    (nbrsOf c).countP P ≤ 5 := by
  obtain ⟨px, py⟩ := p
  obtain ⟨cx, cy⟩ := c
  have hmem : ((px - cx : ℤ), (py - cy : ℤ)) ∈ nbrOffsets := by
    obtain ⟨hne, h1, h2⟩ := h
    simp only [ne_eq, Prod.mk.injEq, abs_le] at hne h1 h2
    simp only [nbrOffsets, List.mem_cons, List.not_mem_nil, or_false, Prod.mk.injEq]
    omega
  calc (nbrsOf (cx, cy)).countP P
      = nbrOffsets.countP fun o => P (cx + o.1, cy + o.2) := by
        simp [nbrsOf, List.countP_map, Function.comp_def]
    _ ≤ nbrOffsets.countP (offsetFar ((px - cx : ℤ), (py - cy : ℤ))) := by
        refine List.countP_mono_left fun o _ ho => ?_
        obtain ⟨ox, oy⟩ := o
        obtain ⟨hne, hadj⟩ := hP _ ho
        simp only [kingAdj, ne_eq, Prod.mk.injEq, abs_le, not_and, not_le] at hne hadj
        simp only [offsetFar, Bool.and_eq_true, decide_eq_true_eq, ne_eq, Prod.mk.injEq,
          not_and, not_le]
        omega
    _ ≤ 5 := offsetFar_count_le _ hmem

/-! ## The explorer

A breadth-first flood from the origin, written as a pure transition function so
that the whole run is a function of its decision bits. -/

/-- State of the exploration. -/
structure ExpState where
  /-- Cells decided to belong to the animal. -/
  accepted : Finset (ℤ × ℤ)
  /-- Cells ever proposed; each is decided exactly once. -/
  considered : Finset (ℤ × ℤ)
  /-- Pending candidates, each paired with the accepted cell that proposed it. -/
  queue : List ((ℤ × ℤ) × (ℤ × ℤ))
  /-- Decisions consumed so far. -/
  steps : ℕ
  /-- Indices of the decisions that were "yes". -/
  accPos : Finset ℕ

/-- The candidates a newly accepted cell `c` proposes: its king neighbours that
are scan-greater than the origin (a shape has no others) and have not been
considered yet. -/
def newCells (con : Finset (ℤ × ℤ)) (c : ℤ × ℤ) : List (ℤ × ℤ) :=
  (nbrsOf c).filter fun q => scanPos q && !decide (q ∈ con)

/-- Membership in `newCells`, unfolded. -/
lemma mem_newCells {con : Finset (ℤ × ℤ)} {c q : ℤ × ℤ} :
    q ∈ newCells con c ↔ q ∈ nbrsOf c ∧ scanPos q = true ∧ q ∉ con := by
  simp [newCells, List.mem_filter]

/-- Proposals are distinct: the eight king neighbours are. -/
lemma newCells_nodup (con : Finset (ℤ × ℤ)) (c : ℤ × ℤ) : (newCells con c).Nodup :=
  (nbrsOf_nodup c).filter _

/-- The proposal count as a `countP` over the neighbour list. -/
lemma newCells_length (con : Finset (ℤ × ℤ)) (c : ℤ × ℤ) :
    (newCells con c).length
      = (nbrsOf c).countP fun q => scanPos q && !decide (q ∈ con) :=
  List.countP_eq_length_filter.symm

/-- The transition, taken apart by the queue so that its equations are clean. -/
private def expStepAux (st : ExpState) (b : Bool) :
    List ((ℤ × ℤ) × (ℤ × ℤ)) → ExpState
  | [] => { st with steps := st.steps + 1 }
  | (c, _) :: rest =>
      if b then
        { accepted := insert c st.accepted
          considered := st.considered ∪ (newCells st.considered c).toFinset
          queue := rest ++ (newCells st.considered c).map fun q => (q, c)
          steps := st.steps + 1
          accPos := insert st.steps st.accPos }
      else
        { st with queue := rest, steps := st.steps + 1 }

/-- **One decision step.** Pop the head candidate and consume one `Bool`: the
answer to "does the animal contain this cell?". A "yes" records the cell and
queues its unseen scan-positive neighbours; a "no" simply drops it. With an
empty queue the run has finished and the step is inert apart from the counter.
-/
def expStep (st : ExpState) (b : Bool) : ExpState := expStepAux st b st.queue

/-- The initial state: the origin proposed, nothing decided. -/
def expInit : ExpState :=
  { accepted := ∅, considered := {(0, 0)}, queue := [((0, 0), (0, 0))],
    steps := 0, accPos := ∅ }

/-- The step on a finished run. -/
lemma expStep_nil {st : ExpState} (b : Bool) (h : st.queue = []) :
    expStep st b = { st with steps := st.steps + 1 } := by
  simp [expStep, h, expStepAux]

/-- The rejecting step. -/
lemma expStep_false {st : ExpState} {c p : ℤ × ℤ} {rest : List ((ℤ × ℤ) × (ℤ × ℤ))}
    (h : st.queue = (c, p) :: rest) :
    expStep st false = { st with queue := rest, steps := st.steps + 1 } := by
  simp [expStep, h, expStepAux]

/-- The accepting step. -/
lemma expStep_true {st : ExpState} {c p : ℤ × ℤ} {rest : List ((ℤ × ℤ) × (ℤ × ℤ))}
    (h : st.queue = (c, p) :: rest) :
    expStep st true =
      { accepted := insert c st.accepted
        considered := st.considered ∪ (newCells st.considered c).toFinset
        queue := rest ++ (newCells st.considered c).map fun q => (q, c)
        steps := st.steps + 1
        accPos := insert st.steps st.accPos } := by
  simp [expStep, h, expStepAux]

/-- Every step consumes exactly one decision. -/
lemma expStep_steps (st : ExpState) (b : Bool) : (expStep st b).steps = st.steps + 1 := by
  rcases hq : st.queue with _ | ⟨⟨c, p⟩, rest⟩
  · rw [expStep_nil b hq]
  · cases b
    · rw [expStep_false hq]
    · rw [expStep_true hq]

/-- The membership oracle of a fixed cell set, as a decision driver. It answers
"no" on a finished run, so a "yes" always names a genuine head candidate. -/
def oracleBit (D : Finset (ℤ × ℤ)) (st : ExpState) : Bool :=
  match st.queue with
  | [] => false
  | (c, _) :: _ => decide (c ∈ D)

/-- The oracle-driven run: `k` steps of `expStep`, answered by membership in `D`. -/
def runO (D : Finset (ℤ × ℤ)) : ℕ → ExpState
  | 0 => expInit
  | k + 1 => expStep (runO D k) (oracleBit D (runO D k))

/-- The position-driven run: `k` steps of `expStep`, accepting exactly at the
step indices listed in `A`. -/
def runA (A : Finset ℕ) : ℕ → ExpState
  | 0 => expInit
  | k + 1 => expStep (runA A k) (decide ((runA A k).steps ∈ A))

/-- The oracle run's counter is the iteration index. -/
lemma runO_steps (D : Finset (ℤ × ℤ)) (k : ℕ) : (runO D k).steps = k := by
  induction k with
  | zero => rfl
  | succ k ih => rw [runO, expStep_steps, ih]

/-- The position run's counter is the iteration index. -/
lemma runA_steps (A : Finset ℕ) (k : ℕ) : (runA A k).steps = k := by
  induction k with
  | zero => rfl
  | succ k ih => rw [runA, expStep_steps, ih]

/-- A "yes" answer names a head candidate. -/
lemma oracleBit_true {D : Finset (ℤ × ℤ)} {st : ExpState} (h : oracleBit D st = true) :
    ∃ c p rest, st.queue = (c, p) :: rest ∧ c ∈ D := by
  rcases hq : st.queue with _ | ⟨⟨c, p⟩, rest⟩
  · rw [oracleBit, hq] at h; exact absurd h (by simp)
  · exact ⟨c, p, rest, rfl, by rw [oracleBit, hq] at h; simpa using h⟩

/-- **The accept positions record exactly the accepting steps.** Position `k` is
banked by the run of length `m` iff step `k` happened and answered "yes"; in
particular the record never changes retroactively. -/
lemma mem_accPos (D : Finset (ℤ × ℤ)) (m k : ℕ) :
    k ∈ (runO D m).accPos ↔ k < m ∧ oracleBit D (runO D k) = true := by
  induction m with
  | zero => simp [runO, expInit]
  | succ m ih =>
      have hst : (runO D m).steps = m := runO_steps D m
      by_cases hb : oracleBit D (runO D m) = true
      · obtain ⟨c, p, rest, hq, -⟩ := oracleBit_true hb
        rw [runO, hb, expStep_true hq, hst]
        simp only [Finset.mem_insert, ih]
        constructor
        · rintro (rfl | ⟨h1, h2⟩)
          · exact ⟨Nat.lt_succ_self _, hb⟩
          · exact ⟨Nat.lt_succ_of_lt h1, h2⟩
        · rintro ⟨h1, h2⟩
          rcases Nat.lt_succ_iff_lt_or_eq.mp h1 with h | rfl
          · exact Or.inr ⟨h, h2⟩
          · exact Or.inl rfl
      · rw [Bool.not_eq_true] at hb
        have hacc : (runO D (m + 1)).accPos = (runO D m).accPos := by
          rcases hq : (runO D m).queue with _ | ⟨⟨c, p⟩, rest⟩
          · rw [runO, expStep_nil _ hq]
          · rw [runO, hb, expStep_false hq]
        rw [hacc, ih]
        constructor
        · rintro ⟨h1, h2⟩; exact ⟨Nat.lt_succ_of_lt h1, h2⟩
        · rintro ⟨h1, h2⟩
          refine ⟨?_, h2⟩
          rcases Nat.lt_succ_iff_lt_or_eq.mp h1 with h | rfl
          · exact h
          · rw [hb] at h2; exact absurd h2 (by simp)

/-- **The decision word determines the run.** Replaying the exploration with the
accept positions of an oracle run — a `Finset ℕ`, carrying no information about
`D` beyond those positions — reproduces that run step for step. -/
lemma runA_eq_runO (D : Finset (ℤ × ℤ)) (K : ℕ) :
    ∀ k, k ≤ K → runA (runO D K).accPos k = runO D k := by
  intro k
  induction k with
  | zero => intro _; rfl
  | succ k ih =>
      intro hk
      have hlt : k < K := by omega
      have h1 : (k ∈ (runO D K).accPos) ↔ (oracleBit D (runO D k) = true) := by
        rw [mem_accPos]; exact ⟨fun h => h.2, fun h => ⟨hlt, h⟩⟩
      rw [runA, ih (by omega), runO, runO_steps]
      congr 1
      simp [h1]

/-! ## The exploration invariant

Fourteen clauses carried together: piecemeal invariants do not survive the
accepting step, where the queue, the considered set and the budget all move at
once. `D` is an arbitrary cell set here — nothing in this section needs it to
be a expShape. -/

/-- The exploration invariant relative to a cell set `D`. -/
structure Good (D : Finset (ℤ × ℤ)) (st : ExpState) : Prop where
  /-- Only cells of `D` are ever accepted. -/
  accSub : st.accepted ⊆ D
  /-- Accepted cells have been considered. -/
  accCon : st.accepted ⊆ st.considered
  /-- The origin is considered from the outset. -/
  origCon : (0, 0) ∈ st.considered
  /-- Queued candidates have been considered. -/
  qCon : ∀ e ∈ st.queue, e.1 ∈ st.considered
  /-- No candidate is queued twice. -/
  qNodup : (st.queue.map Prod.fst).Nodup
  /-- Queued candidates are still undecided. -/
  qNotAcc : ∀ e ∈ st.queue, e.1 ∉ st.accepted
  /-- Every candidate but the origin carries an accepted, adjacent proposer. -/
  qParent : ∀ e ∈ st.queue, (e.2 ∈ st.accepted ∧ kingAdj e.2 e.1) ∨ e.1 = (0, 0)
  /-- An accepted cell has proposed all of its scan-positive neighbours. -/
  closure : ∀ q ∈ st.accepted, ∀ r ∈ nbrsOf q, scanPos r = true → r ∈ st.considered
  /-- Before the origin is accepted, nothing has happened at all. -/
  base : (0, 0) ∈ st.accepted ∨ (st.accepted = ∅ ∧ st.considered = {(0, 0)})
  /-- The five-per-cell budget, once the origin has been accepted. -/
  budget : (0, 0) ∈ st.accepted → st.considered.card ≤ 5 * st.accepted.card
  /-- Steps taken plus candidates pending is at most the number considered. -/
  count : st.queue = [] ∨ st.steps + st.queue.length ≤ st.considered.card
  /-- One banked position per accepted cell. -/
  posCard : st.accPos.card = st.accepted.card
  /-- Positions are banked in the past. -/
  posLt : ∀ i ∈ st.accPos, i < st.steps
  /-- A considered cell of `D` is accepted or still pending. -/
  reach : ∀ q ∈ st.considered, q ∈ D → q ∈ st.accepted ∨ ∃ e ∈ st.queue, e.1 = q

/-- The invariant holds at the start: the origin is the sole candidate. -/
lemma good_init (D : Finset (ℤ × ℤ)) : Good D expInit where
  accSub := by simp [expInit]
  accCon := by simp [expInit]
  origCon := by simp [expInit]
  qCon := by simp [expInit]
  qNodup := by simp [expInit]
  qNotAcc := by simp [expInit]
  qParent := by simp [expInit]
  closure := by simp [expInit]
  base := Or.inr ⟨rfl, rfl⟩
  budget := by simp [expInit]
  count := Or.inr (by simp [expInit])
  posCard := by simp [expInit]
  posLt := by simp [expInit]
  reach := by
    intro q hq _
    refine Or.inr ⟨((0, 0), (0, 0)), by simp [expInit], ?_⟩
    have : q ∈ ({(0, 0)} : Finset (ℤ × ℤ)) := by simpa [expInit] using hq
    exact (Finset.mem_singleton.mp this).symm

/-- **The invariant is preserved by an oracle-driven step.** The rejecting and
inert steps only shrink the queue; the accepting step is where the budget
argument lives — the origin proposes four candidates, and any later cell
proposes at most five because its proposer and their shared neighbours are
already recorded (`countP_new_le`). -/
lemma good_step {D : Finset (ℤ × ℤ)} {st : ExpState} (hg : Good D st) :
    Good D (expStep st (oracleBit D st)) := by
  rcases hq : st.queue with _ | ⟨⟨c, p⟩, rest⟩
  · rw [expStep_nil _ hq]
    exact { hg with
      count := Or.inl hq
      posLt := fun i hi => Nat.lt_succ_of_lt (hg.posLt i hi) }
  · have hbit : oracleBit D st = decide (c ∈ D) := by rw [oracleBit, hq]
    have hmemq : ((c, p) : (ℤ × ℤ) × (ℤ × ℤ)) ∈ st.queue := by rw [hq]; exact List.mem_cons_self ..
    have hrest : ∀ e ∈ rest, e ∈ st.queue := fun e he => by rw [hq]; exact List.mem_cons_of_mem _ he
    have hmapq : st.queue.map Prod.fst = c :: rest.map Prod.fst := by rw [hq]; simp
    have hcnot : c ∉ rest.map Prod.fst ∧ (rest.map Prod.fst).Nodup := by
      have := hg.qNodup
      rw [hmapq, List.nodup_cons] at this
      exact this
    have hcCon : c ∈ st.considered := hg.qCon _ hmemq
    have hcNotAcc : c ∉ st.accepted := hg.qNotAcc _ hmemq
    have hcount : st.steps + (rest.length + 1) ≤ st.considered.card := by
      rcases hg.count with h | h
      · rw [hq] at h; exact absurd h (by simp)
      · rw [hq] at h; simpa using h
    by_cases hcD : c ∈ D
    · -- the accepting step
      rw [hbit, decide_eq_true hcD, expStep_true hq]
      set N := newCells st.considered c with hN
      have hNmem : ∀ q ∈ N, q ∈ nbrsOf c ∧ scanPos q = true ∧ q ∉ st.considered :=
        fun q hqN => mem_newCells.mp hqN
      have hNnodup : N.Nodup := newCells_nodup _ _
      have hdisj : Disjoint st.considered N.toFinset := by
        rw [Finset.disjoint_right]
        intro q hqN
        exact (hNmem q (List.mem_toFinset.mp hqN)).2.2
      have hcardU : (st.considered ∪ N.toFinset).card = st.considered.card + N.length := by
        rw [Finset.card_union_of_disjoint hdisj, List.toFinset_card_of_nodup hNnodup]
      have hsubU : st.considered ⊆ st.considered ∪ N.toFinset := Finset.subset_union_left
      have hqmap : (rest ++ N.map fun q => (q, c)).map Prod.fst = rest.map Prod.fst ++ N := by
        simp [List.map_append, List.map_map, Function.comp_def]
      have hqsplit : ∀ e ∈ rest ++ N.map fun q => (q, c),
          e ∈ rest ∨ (e.1 ∈ N ∧ e.2 = c) := by
        intro e he
        rcases List.mem_append.mp he with he | he
        · exact Or.inl he
        · obtain ⟨q, hqN, rfl⟩ := List.mem_map.mp he
          exact Or.inr ⟨hqN, rfl⟩
      refine
        { accSub := ?_, accCon := ?_, origCon := ?_, qCon := ?_, qNodup := ?_, qNotAcc := ?_,
          qParent := ?_, closure := ?_, base := ?_, budget := ?_, count := ?_, posCard := ?_,
          posLt := ?_, reach := ?_ }
      · exact Finset.insert_subset hcD hg.accSub
      · exact Finset.insert_subset (hsubU hcCon) (hg.accCon.trans hsubU)
      · exact hsubU hg.origCon
      · intro e he
        rcases hqsplit e he with he | ⟨he, -⟩
        · exact hsubU (hg.qCon e (hrest e he))
        · exact Finset.mem_union_right _ (List.mem_toFinset.mpr he)
      · rw [hqmap]
        refine List.nodup_append'.mpr ⟨hcnot.2, hNnodup, ?_⟩
        intro q hq1 hq2
        obtain ⟨e, he, rfl⟩ := List.mem_map.mp hq1
        exact (hNmem e.1 hq2).2.2 (hg.qCon e (hrest e he))
      · intro e he hacc
        rcases Finset.mem_insert.mp hacc with h | h
        · rcases hqsplit e he with he | ⟨he, -⟩
          · exact hcnot.1 (h ▸ List.mem_map_of_mem he)
          · exact (hNmem e.1 he).2.2 (h ▸ hcCon)
        · rcases hqsplit e he with he | ⟨he, -⟩
          · exact hg.qNotAcc e (hrest e he) h
          · exact (hNmem e.1 he).2.2 (hg.accCon h)
      · intro e he
        rcases hqsplit e he with he | ⟨he, he2⟩
        · rcases hg.qParent e (hrest e he) with ⟨h1, h2⟩ | h
          · exact Or.inl ⟨Finset.mem_insert_of_mem h1, h2⟩
          · exact Or.inr h
        · refine Or.inl ⟨he2 ▸ Finset.mem_insert_self _ _, ?_⟩
          rw [he2]
          exact mem_nbrsOf.mp (hNmem e.1 he).1
      · intro q hqacc r hr hscan
        rcases Finset.mem_insert.mp hqacc with rfl | h
        · by_cases hrc : r ∈ st.considered
          · exact hsubU hrc
          · exact Finset.mem_union_right _
              (List.mem_toFinset.mpr (mem_newCells.mpr ⟨hr, hscan, hrc⟩))
        · exact hsubU (hg.closure q h r hr hscan)
      · exact Or.inl (by
          by_cases hc0 : c = (0, 0)
          · exact hc0 ▸ Finset.mem_insert_self _ _
          · rcases hg.base with h | h
            · exact Finset.mem_insert_of_mem h
            · exact absurd (Finset.mem_singleton.mp (h.2 ▸ hcCon)) hc0)
      · intro h0
        by_cases hc0 : c = (0, 0)
        · subst hc0
          have hbase : st.accepted = ∅ ∧ st.considered = {((0 : ℤ), (0 : ℤ))} := by
            rcases hg.base with h | h
            · exact absurd h hcNotAcc
            · exact h
          have hlen : N.length ≤ 4 := by
            rw [hN, newCells_length]
            calc (nbrsOf ((0 : ℤ), (0 : ℤ))).countP
                    (fun q => scanPos q && !decide (q ∈ st.considered))
                ≤ (nbrsOf ((0 : ℤ), (0 : ℤ))).countP scanPos :=
                  List.countP_mono_left fun x _ hx => by
                    have hx' : scanPos x = true ∧ x ∉ st.considered := by simpa using hx
                    exact hx'.1
              _ = 4 := countP_scanPos_origin
          have h1 : st.considered.card = 1 := by rw [hbase.2]; simp
          have h2 : (insert ((0 : ℤ), (0 : ℤ)) st.accepted).card = 1 := by
            rw [hbase.1]; simp
          rw [hcardU, h2]
          omega
        · have h0acc : ((0 : ℤ), (0 : ℤ)) ∈ st.accepted := by
            rcases Finset.mem_insert.mp h0 with h | h
            · exact absurd h.symm hc0
            · exact h
          obtain ⟨hpacc, hadj⟩ : p ∈ st.accepted ∧ kingAdj p c := by
            rcases hg.qParent _ hmemq with h | h
            · exact h
            · exact absurd h hc0
          have hlen : N.length ≤ 5 := by
            rw [hN, newCells_length]
            refine countP_new_le hadj fun q hqt => ?_
            have hq' : scanPos q = true ∧ q ∉ st.considered := by simpa using hqt
            obtain ⟨hs, hnc⟩ := hq'
            exact ⟨fun hqp => hnc (hqp ▸ hg.accCon hpacc),
              fun hk => hnc (hg.closure p hpacc q (mem_nbrsOf.mpr hk) hs)⟩
          have hb := hg.budget h0acc
          rw [hcardU, Finset.card_insert_of_notMem hcNotAcc]
          omega
      · refine Or.inr ?_
        change st.steps + 1 + (rest ++ N.map fun q => (q, c)).length
          ≤ (st.considered ∪ N.toFinset).card
        rw [hcardU, List.length_append, List.length_map]
        omega
      · rw [Finset.card_insert_of_notMem hcNotAcc,
          Finset.card_insert_of_notMem (fun h => absurd (hg.posLt _ h) (by omega)), hg.posCard]
      · intro i hi
        rcases Finset.mem_insert.mp hi with rfl | h
        · exact Nat.lt_succ_self _
        · exact Nat.lt_succ_of_lt (hg.posLt i h)
      · intro q hqc hqD
        rcases Finset.mem_union.mp hqc with hqc | hqc
        · rcases hg.reach q hqc hqD with h | ⟨e, he, rfl⟩
          · exact Or.inl (Finset.mem_insert_of_mem h)
          · rw [hq] at he
            rcases List.mem_cons.mp he with rfl | he
            · exact Or.inl (Finset.mem_insert_self _ _)
            · exact Or.inr ⟨e, List.mem_append_left _ he, rfl⟩
        · exact Or.inr ⟨(q, c), List.mem_append_right _
            (List.mem_map_of_mem (List.mem_toFinset.mp hqc)), rfl⟩
    · -- the rejecting step
      rw [hbit, decide_eq_false hcD, expStep_false hq]
      refine
        { accSub := hg.accSub, accCon := hg.accCon, origCon := hg.origCon,
          qCon := fun e he => hg.qCon e (hrest e he),
          qNodup := ?_,
          qNotAcc := fun e he => hg.qNotAcc e (hrest e he),
          qParent := fun e he => hg.qParent e (hrest e he),
          closure := hg.closure, base := hg.base, budget := hg.budget,
          count := Or.inr (by change st.steps + 1 + rest.length ≤ st.considered.card; omega),
          posCard := hg.posCard,
          posLt := fun i hi => Nat.lt_succ_of_lt (hg.posLt i hi),
          reach := ?_ }
      · exact hcnot.2
      · intro q hqc hqD
        rcases hg.reach q hqc hqD with h | ⟨e, he, rfl⟩
        · exact Or.inl h
        · rw [hq] at he
          rcases List.mem_cons.mp he with rfl | he
          · exact absurd hqD hcD
          · exact Or.inr ⟨e, he, rfl⟩

/-- The invariant holds all along the oracle-driven run. -/
lemma good_runO (D : Finset (ℤ × ℤ)) (k : ℕ) : Good D (runO D k) := by
  induction k with
  | zero => exact good_init D
  | succ k ih => exact good_step ih

/-! ## Termination and completeness

What the exploration needs of the animal it is exploring: `n` cells,
king-connected, anchored at the origin with every other cell scan-greater. -/

/-- An origin-anchored `n`-cell shape: the exploration's input format. -/
structure IsShape (n : ℕ) (D : Finset (ℤ × ℤ)) : Prop where
  /-- `n` cells. -/
  card : D.card = n
  /-- King-connected. -/
  conn : KingConnected D
  /-- Anchored at the origin. -/
  origin : (0, 0) ∈ D
  /-- The origin is the scan-least cell. -/
  scan : ∀ q ∈ D, q ≠ (0, 0) → scanPos q = true

/-- **The `5n` budget.** Either the origin has been accepted, and the invariant
charges five considered cells to each accepted one, or nothing has happened yet
and only the origin is considered. -/
lemma considered_card_le {n : ℕ} {D : Finset (ℤ × ℤ)} (hD : IsShape n D) (hn : 1 ≤ n) (k : ℕ) :
    (runO D k).considered.card ≤ 5 * n := by
  have hg := good_runO D k
  rcases hg.base with h0 | ⟨-, hcon⟩
  · have hle : (runO D k).accepted.card ≤ n := by
      have := Finset.card_le_card hg.accSub
      rwa [hD.card] at this
    have := hg.budget h0
    omega
  · rw [hcon, Finset.card_singleton]
    omega

/-- **The run halts inside `5 * n` steps.** Each step either finds the queue
empty or consumes a distinct considered cell, and there are at most `5n` of
those. -/
lemma runO_queue_nil {n : ℕ} {D : Finset (ℤ × ℤ)} (hD : IsShape n D) (hn : 1 ≤ n) :
    (runO D (5 * n)).queue = [] := by
  by_contra hne
  have hg := good_runO D (5 * n)
  rcases hg.count with h | h
  · exact hne h
  · rw [runO_steps] at h
    have hb := considered_card_le hD hn (5 * n)
    rcases hq : (runO D (5 * n)).queue with _ | ⟨e, r⟩
    · exact hne hq
    · rw [hq] at h
      simp only [List.length_cons] at h
      omega

/-- **The exploration reconstructs the expShape.** Only cells of `D` are accepted,
and every cell of `D` is: the origin is decided first, and each further cell is
reached along a king path from it — when its predecessor was accepted the cell
was proposed (it is scan-positive, being a non-origin cell of a expShape), and a
halted run has decided everything it proposed. -/
lemma runO_accepted {n : ℕ} {D : Finset (ℤ × ℤ)} (hD : IsShape n D) (hn : 1 ≤ n) :
    (runO D (5 * n)).accepted = D := by
  have hg := good_runO D (5 * n)
  have hnil := runO_queue_nil hD hn
  have hdec : ∀ q ∈ (runO D (5 * n)).considered, q ∈ D → q ∈ (runO D (5 * n)).accepted := by
    intro q hq hqD
    rcases hg.reach q hq hqD with h | ⟨e, he, -⟩
    · exact h
    · rw [hnil] at he; exact absurd he (by simp)
  have h0 : ((0 : ℤ), (0 : ℤ)) ∈ (runO D (5 * n)).accepted := hdec _ hg.origCon hD.origin
  refine Finset.Subset.antisymm hg.accSub fun q hqD => ?_
  have hpath : Relation.ReflTransGen (fun x y => x ∈ D ∧ y ∈ D ∧ kingAdj x y)
      ((0 : ℤ), (0 : ℤ)) q := hD.conn _ hD.origin q hqD
  clear hqD
  induction hpath with
  | refl => exact h0
  | @tail b c _ hstep ih =>
      by_cases hc0 : c = (0, 0)
      · exact hc0 ▸ h0
      · exact hdec c (hg.closure b ih c (mem_nbrsOf.mpr hstep.2.2)
          (hD.scan c hstep.2.1 hc0)) hstep.2.1

/-- The code of a halted run has one position per cell. -/
lemma accPos_card {n : ℕ} {D : Finset (ℤ × ℤ)} (hD : IsShape n D) (hn : 1 ≤ n) :
    (runO D (5 * n)).accPos.card = n := by
  rw [(good_runO D (5 * n)).posCard, runO_accepted hD hn, hD.card]

/-- Positions are banked before the run ends. -/
lemma accPos_subset (D : Finset (ℤ × ℤ)) (k : ℕ) : (runO D k).accPos ⊆ Finset.range k := by
  intro i hi
  rw [Finset.mem_range]
  have := (good_runO D k).posLt i hi
  rwa [runO_steps] at this

/-! ## Re-anchoring a canonical animal

A canonical animal is anchored by its *bounding box*, which need not put any
cell at the origin. The exploration wants the *scan-least cell* there instead,
so the animal is translated; canonicity pins the translation back, which is why
nothing is lost (`expShape_injOn`). -/

/-- The x-coordinate of the scan-least cell of `S`: the least `k` with
`(k, 0) ∈ S`. Totalised by `Nat.sInf`, whose junk value `0` on the empty set
never arises for a canonical animal (`anchorSet_nonempty`). -/
noncomputable def anchorX (S : Finset (ℤ × ℤ)) : ℕ := sInf {k : ℕ | ((k : ℤ), (0 : ℤ)) ∈ S}

/-- The scan-least cell of a canonical animal: minimum `y` is `0`, so it lies in
row `0`, and `anchorX` picks the leftmost cell of that row. -/
noncomputable def anchor (S : Finset (ℤ × ℤ)) : ℤ × ℤ := ((anchorX S : ℤ), 0)

/-- `S` translated so that its scan-least cell sits at the origin. -/
noncomputable def expShape (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  S.image fun q => (q.1 - (anchor S).1, q.2 - (anchor S).2)

/-- Row `0` of a canonical animal is inhabited, so `anchorX` is a genuine
minimum. -/
private lemma anchorSet_nonempty {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) :
    {k : ℕ | ((k : ℤ), (0 : ℤ)) ∈ S}.Nonempty := by
  obtain ⟨p, hp, hp2⟩ := hS.2.2.2.2.2
  refine ⟨p.1.toNat, ?_⟩
  have hx := hS.2.2.1 p hp
  have hpe : ((p.1.toNat : ℤ), (0 : ℤ)) = p := by
    rw [Int.toNat_of_nonneg hx, ← hp2]
  rw [Set.mem_setOf_eq, hpe]
  exact hp

/-- The anchor is a cell of the animal. -/
lemma anchor_mem {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) : anchor S ∈ S :=
  Nat.sInf_mem (anchorSet_nonempty hS)

/-- The anchor is leftmost in row `0`. -/
lemma anchor_min {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) {q : ℤ × ℤ}
    (hq : q ∈ S) (hq2 : q.2 = 0) : (anchor S).1 ≤ q.1 := by
  have hx := hS.2.2.1 q hq
  have hmem : q.1.toNat ∈ {k : ℕ | ((k : ℤ), (0 : ℤ)) ∈ S} := by
    have hqe : ((q.1.toNat : ℤ), (0 : ℤ)) = q := by
      rw [Int.toNat_of_nonneg hx, ← hq2]
    rw [Set.mem_setOf_eq, hqe]; exact hq
  have hle : anchorX S ≤ q.1.toNat := Nat.sInf_le hmem
  simp only [anchor]
  omega

/-- Translation is injective on cells. -/
private lemma sub_injective (a : ℤ × ℤ) :
    Function.Injective fun q : ℤ × ℤ => (q.1 - a.1, q.2 - a.2) := by
  intro x y h
  simp only [Prod.mk.injEq] at h
  exact Prod.ext (by omega) (by omega)

/-- Translation preserves king adjacency. -/
private lemma kingAdj_sub (a : ℤ × ℤ) {x y : ℤ × ℤ} (h : kingAdj x y) :
    kingAdj (x.1 - a.1, x.2 - a.2) (y.1 - a.1, y.2 - a.2) := by
  obtain ⟨hne, h1, h2⟩ := h
  rw [ne_eq, Prod.ext_iff] at hne
  refine ⟨by simp only [ne_eq, Prod.mk.injEq]; omega, ?_, ?_⟩
  · change |x.1 - a.1 - (y.1 - a.1)| ≤ 1
    rw [show x.1 - a.1 - (y.1 - a.1) = x.1 - y.1 by ring]; exact h1
  · change |x.2 - a.2 - (y.2 - a.2)| ≤ 1
    rw [show x.2 - a.2 - (y.2 - a.2) = x.2 - y.2 by ring]; exact h2

/-- **A canonical animal re-anchors to a expShape.** Size and connectivity survive
the translation; the origin is the image of the anchor; and every other cell is
scan-greater because the anchor is scan-least. -/
lemma isShape_expShape {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) :
    IsShape n (expShape S) where
  card := by rw [expShape, Finset.card_image_of_injective _ (sub_injective _), hS.1]
  conn := by
    intro d hd e he
    rw [expShape, Finset.mem_image] at hd he
    obtain ⟨x, hx, rfl⟩ := hd
    obtain ⟨y, hy, rfl⟩ := he
    refine Relation.ReflTransGen.lift
      (fun q : ℤ × ℤ => (q.1 - (anchor S).1, q.2 - (anchor S).2)) (fun u v huv => ?_)
      (hS.2.1 x hx y hy)
    exact ⟨by rw [expShape]; exact Finset.mem_image_of_mem _ huv.1,
      by rw [expShape]; exact Finset.mem_image_of_mem _ huv.2.1, kingAdj_sub _ huv.2.2⟩
  origin := by
    have := Finset.mem_image_of_mem (fun q : ℤ × ℤ => (q.1 - (anchor S).1, q.2 - (anchor S).2))
      (anchor_mem hS)
    simpa [expShape] using this
  scan := by
    intro d hd hd0
    rw [expShape, Finset.mem_image] at hd
    obtain ⟨q, hq, rfl⟩ := hd
    have hy := hS.2.2.2.2.1 q hq
    have hane : (anchor S).2 = 0 := rfl
    simp only [ne_eq, Prod.mk.injEq, not_and] at hd0
    simp only [scanPos, Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq]
    rcases eq_or_lt_of_le hy with hy0 | hy0
    · have hmin := anchor_min hS hq hy0.symm
      have : ¬ (q.1 - (anchor S).1 = 0) := fun h => hd0 h (by omega)
      right; omega
    · left; omega

/-- Re-anchoring is undone by translating back. -/
lemma expShape_image (S : Finset (ℤ × ℤ)) :
    (expShape S).image (fun d => (d.1 + (anchor S).1, d.2 + (anchor S).2)) = S := by
  rw [expShape, Finset.image_image]
  ext q
  simp [Function.comp_def]

/-- **Re-anchoring loses nothing.** Two canonical animals with the same shape
have the same anchor: the animal's own `min x = 0` clause forces the anchor's
x-coordinate to be the negative of the shape's minimum x-coordinate, so it is
determined by the expShape. Translating back then identifies the animals. -/
lemma expShape_injOn (n : ℕ) :
    Set.InjOn expShape {S : Finset (ℤ × ℤ) | IsCanonicalAnimal n S} := by
  have key : ∀ T₁ T₂ : Finset (ℤ × ℤ), IsCanonicalAnimal n T₁ → IsCanonicalAnimal n T₂ →
      expShape T₁ = expShape T₂ → (anchor T₁).1 ≤ (anchor T₂).1 := by
    intro T₁ T₂ hT₁ hT₂ h
    obtain ⟨q, hq, hq0⟩ := hT₁.2.2.2.1
    have hd : (q.1 - (anchor T₁).1, q.2 - (anchor T₁).2) ∈ expShape T₂ := by
      rw [← h, expShape]; exact Finset.mem_image_of_mem _ hq
    rw [expShape, Finset.mem_image] at hd
    obtain ⟨r, hr, hre⟩ := hd
    have hr0 : 0 ≤ r.1 := hT₂.2.2.1 r hr
    simp only [Prod.mk.injEq] at hre
    omega
  intro S₁ h₁ S₂ h₂ heq
  have ha : anchor S₁ = anchor S₂ := by
    have e1 := key S₁ S₂ h₁ h₂ heq
    have e2 := key S₂ S₁ h₂ h₁ heq.symm
    simp only [anchor] at e1 e2 ⊢
    have : (anchorX S₁ : ℤ) = (anchorX S₂ : ℤ) := by omega
    rw [this]
  calc S₁ = (expShape S₁).image (fun d => (d.1 + (anchor S₁).1, d.2 + (anchor S₁).2)) :=
        (expShape_image S₁).symm
    _ = (expShape S₂).image (fun d => (d.1 + (anchor S₂).1, d.2 + (anchor S₂).2)) := by
        rw [heq, ha]
    _ = S₂ := expShape_image S₂

/-! ## The bound -/

/-- The exploration code of a canonical animal: the accept positions of the
oracle-driven run on its expShape. -/
noncomputable def expCode (n : ℕ) (S : Finset (ℤ × ℤ)) : Finset ℕ :=
  (runO (expShape S) (5 * n)).accPos

/-- **`a n ≤ C(5n, n)`.** The exploration code embeds the canonical animals of
`n` cells into the `n`-element subsets of `Finset.range (5 * n)`: it lands there
because the run halts within `5 * n` steps and accepts exactly `n` times, and it
is injective because replaying the exploration from the code alone recovers the
expShape (`runA_eq_runO`), which recovers the animal (`expShape_injOn`). -/
theorem a_le_choose (n : ℕ) (hn : 1 ≤ n) : a n ≤ Nat.choose (5 * n) n := by
  have hmap : ∀ S ∈ {S : Finset (ℤ × ℤ) | IsCanonicalAnimal n S},
      expCode n S ∈ (↑(Finset.powersetCard n (Finset.range (5 * n))) : Set (Finset ℕ)) := by
    intro S hS
    rw [Finset.mem_coe, Finset.mem_powersetCard]
    exact ⟨accPos_subset _ _, accPos_card (isShape_expShape hS) hn⟩
  have hinj : Set.InjOn (expCode n) {S : Finset (ℤ × ℤ) | IsCanonicalAnimal n S} := by
    intro S₁ h₁ S₂ h₂ h
    refine expShape_injOn n h₁ h₂ ?_
    have k1 : runA (expCode n S₁) (5 * n) = runO (expShape S₁) (5 * n) :=
      runA_eq_runO _ _ _ le_rfl
    have k2 : runA (expCode n S₂) (5 * n) = runO (expShape S₂) (5 * n) :=
      runA_eq_runO _ _ _ le_rfl
    rw [← runO_accepted (isShape_expShape h₁) hn, ← runO_accepted (isShape_expShape h₂) hn,
      ← k1, ← k2, h]
  have hfin := (Finset.powersetCard n (Finset.range (5 * n))).finite_toSet
  have hle := Set.ncard_le_ncard_of_injOn (expCode n) hmap hinj hfin
  rw [Set.ncard_coe_finset, Finset.card_powersetCard, Finset.card_range] at hle
  rw [a]
  exact hle

/-! ## Axiom audit

Plain `#print axioms`; the `#guard_msgs`-wrapped versions are integrated into
the campaign audit point by the orchestrator. Both results must carry the
standard three — no `native_decide` enters this file, the eight-case neighbour
check being a kernel `decide`. -/

#print axioms a_le_choose
#print axioms choose_le_pow

end Polyplets
