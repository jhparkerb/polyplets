/-
Proposition 6 (`results/subclasses.md`) as a Lean *architecture*: every
statement is real and typechecks; every `sorry` is a contract with a line
estimate. The final theorem is genuinely proved from the contracts above it.

**2026-08-06: the bottom third of this file landed for real** and has been
deleted from it. `Polyplets/StairGrowth.lean` has `M`, its finiteness, the
`4 ^ n` ceiling, Lemma 3 (`Stair.M_supermul`) and `Stair.mu`; the Fekete ladder
they use is `Polyplets/Fekete.lean`, a structure with `Growth.lean`'s `lambda`
and `Stair.mu` as its two instances. Those are `lake build` material now, not
drafts, and this file imports them.

What is left below is what `docs/lean-staircase-growth-brief.md` puts
explicitly OUT of scope: Lemma 2's stack bound, Lemma 1's phase split, the
geometric layer, and the squeeze. Their estimates stand; nobody is authorized
to spend them.

# The five contracts, and how to check each one without Lean

This file is NOT in the build (`lakefile.toml` has `defaultTargets =
["Polyplets"]`, and `Draft/` is not a library), so `lake build` never sees
these `sorry`s and the built development stays at zero. What they cost is
visible where it should be: `#print axioms Polyplets.Prop6.prop6` at the foot
of the file prints `sorryAx`, and will keep printing it until the list below
is empty.

Every contract is proved on paper and pinned numerically. Neither warrant is
in Lean, and neither is weaker for that; what a reader should not do is treat
`prop6` as machine-checked. In reading order:

1. `Stack.Valid` — the stack class: bottoms rise and tops fall, so the column
   intervals nest.
   * **Paper**: `results/subclasses.md` Lemma 1 (the two outer blocks
     are stacks) and Lemma 2 part 1 (a stack is a weakly unimodal
     composition, `P(n) = A001523`).
   * **Checked**: `make gate-middle-kingdom`, via
     `experiments/staircase_supermul.py`'s `stacks()` — `P` is the RED control
     that makes Lemma 3's inequality non-vacuous, so a wrong stack class would
     fail the gate rather than pass it quietly.
   * ~20 lines. `P n`'s finiteness is nearly free now: stack offsets also obey
     `d ≤ p`, so `Stair.cand` already contains them.

2. `lemma2` — `P n ≤ (n+1)^(4√n+6)`, hence `P(n)^(1/n) → 1`.
   * **Paper**: `results/subclasses.md` Lemma 2 part 2, the `√n` split
     of a partition. Hardy–Ramanujan is not used and not needed.
   * **Checked**: `make gate-middle-kingdom`, via
     `experiments/monotone_block_growth.py`: `p(n) ≤ (n+1)^(s+L+1) ≤
     (n+1)^(2√n+2)` and `P(n) ≤ (n+1)² p(n)²` for `n ≤ 120` — which compose to
     exactly this bound — plus an injectivity check on the small/large
     encoding and a RED control showing the large-part cap is attained, so one
     less would make the bound false.
   * 600–900 lines, and the one contract here that needs no geometry.

3. `IsHVCanonical` — HV-convex king animals as a geometric predicate on
   `Finset (ℤ × ℤ)`.
   * **Paper**: Corollary 4 of `results/subclasses.md` (line 86):
     HV-convex = column-convex + `b` valley-unimodal + `t` peak-unimodal, a
     four-line gap argument in both directions.
   * **Checked**: `make gate-middle-kingdom` brute-forces HV-convex animals
     against the 16-cell grid table, and
     `experiments/descent_block_oracle.py`'s `brute_hv_mirror(11)` reproduces
     the grid totals `n ≤ 11` from the phase split itself.
   * The cost centre. Not the definition — the bridge from this predicate to
     the column-list encoding `StairAnimals.lean` uses.

4. `lemma1` — the convolution inequality `A(n) ≤ 2(n+1)² Σ P·M·P`.
   * **Paper**: `results/subclasses.md` Lemma 1. The decomposition is
     not new in kind: Gouyou-Beauchamps & Leroux, FPSAC 2004
     (arXiv:math/0403168) §2.3, for convex polyominoes on the honeycomb
     lattice; the attribution note in that file says what is and is not
     theirs.
   * **Checked**: the phase split's totals, `n ≤ 11`, in the gate above. The
     inequality itself is not checked directly anywhere — it is slack by
     miles, and the split it rests on is what the gate pins.
   * ~1500 lines, and it needs contract 3 first.

5. `A_tendsto` — the squeeze: contracts 2 and 4 kill the outer factors,
   `Stair.M_tendsto` supplies `µ` for the middle.
   * **Paper**: `results/subclasses.md`, Proposition 6.
   * **Checked**: `µ` itself is measured to 204 digits there, and the 49-digit
     agreement between `(dir4, HV-convex)` and the unrestricted HV-convex
     series is the observation Proposition 6 explains.
   * ~250 lines of ε-management in `ℝ`, cheap once the rest exists.
-/
import Mathlib
import Polyplets.StairGrowth

open Filter Topology

namespace Polyplets.Prop6

/-! ## 1. The families that do not exist yet (B3, ~250 lines) -/

/-- Stacks: the column intervals nest, because the two boundaries move
oppositely. This is a different class from `Stair.Valid`, not a reflection of it
— reflecting a staircase gives another staircase. Same `List Col` encoding.

Two reflections do save work, and neither relates stacks to staircases:
reversing the column order swaps the fattening block with the thinning block
(both stacks), and flipping top-to-bottom swaps the two staircase orientations.
Each is an area-preserving involution, so each halves a development.

**Contract 1** — paper: `results/subclasses.md` Lemmas 1 and 2 part 1.
Checked: `make gate-middle-kingdom` (`experiments/staircase_supermul.py`,
`P(n) = A001523` as the RED control). -/
def Stack.Valid : List Stair.Col → Prop := sorry

/-- `P n` — stacks of area `n`. -/
noncomputable def P (n : ℕ) : ℕ :=
  Nat.card {l : List Stair.Col // Stack.Valid l ∧ Stair.area l = n}

/-- HV-convex king animals, origin-anchored, stated geometrically in the
`Defs.lean` idiom: king-connected, every row and every column an unbroken run.
This is the layer that does not exist yet, and Corollary 4 — that it forces
valley-unimodal bottoms and peak-unimodal tops — is proved against it.

**Contract 3** — paper: Corollary 4 of `results/subclasses.md:86`.
Checked: `make gate-middle-kingdom`, brute force against the 16-cell grid table
and `experiments/descent_block_oracle.py`'s `brute_hv_mirror(11)`. -/
def IsHVCanonical (n : ℕ) (S : Finset (ℤ × ℤ)) : Prop := sorry

/-- `A n` — HV-convex king animals of area `n`. -/
noncomputable def A (n : ℕ) : ℕ := {S : Finset (ℤ × ℤ) | IsHVCanonical n S}.ncard

/-! ## 2. The two lemmas that are still paper proofs

Lemma 3 is no longer here: it is `Stair.M_supermul`, proved. -/

/-- **Lemma 2.** Stacks are sub-exponential. The row-width transpose (a bijection
onto weakly unimodal compositions) plus the `√n` split. Mathlib has `Nat.Partition`
and its `Fintype` but nothing on unimodality and no cardinality bound, so both
halves are built from scratch. ~600–900 lines.

**Contract 2** — paper: `results/subclasses.md` Lemma 2 part 2.
Checked: `make gate-middle-kingdom` (`experiments/monotone_block_growth.py`)
verifies both factors of this bound to `n ≤ 120`, with a RED control on the
large-part cap. -/
theorem lemma2 (n : ℕ) : P n ≤ (n + 1) ^ (4 * Nat.sqrt n + 6) := sorry

/-- **Lemma 1.** The three-block factorisation, as a counting inequality: phase
bits are monotone, so the columns split `C1 C2 C3`, and the animal is recovered
from the three blocks, two junction offsets and one phase bit. Needs Corollary 4
first, then a `Finset` injection. The cost centre, ~1500 lines.

**Contract 4** — paper: `results/subclasses.md` Lemma 1, with the
FPSAC 2004 attribution note. Checked: the phase split's totals `n ≤ 11` in the
gate; the inequality itself is nowhere checked directly. -/
theorem lemma1 (n : ℕ) :
    A n ≤ 2 * (n + 1) ^ 2 *
      ∑ i ∈ Finset.range (n + 1), ∑ j ∈ Finset.range (n + 1),
        P i * Stair.M j * P (n - i - j) :=
  sorry

/-! ## 3. The squeeze -/

/-- Lemma 1 bounds `A` by a convolution; Lemma 2 kills the two outer factors
because `(n+1) ^ (4√n+6)` has `n`-th root `→ 1`; `Stair.M_tendsto` supplies `µ`
for the middle. ε-management in `ℝ`, ~250 lines.

**Contract 5** — paper: `results/subclasses.md`, Proposition 6.
Checked: `µ` measured there to 204 digits. -/
theorem A_tendsto :
    Tendsto (fun n : ℕ => (A n : ℝ) ^ ((n : ℝ)⁻¹)) atTop (𝓝 Stair.mu) := sorry

/-- **Proposition 6.** Any family trapped between the staircase animals and the
HV-convex ones has growth constant `µ`. Proved here from contracts 2–5, so its
axiom footprint carries `sorryAx` — the `#print axioms` at the foot of this
file is the honest statement of what this file does and does not establish. -/
theorem prop6 (C : ℕ → ℕ) (hlo : ∀ n, Stair.M n ≤ C n) (hhi : ∀ n, C n ≤ A n) :
    Tendsto (fun n : ℕ => (C n : ℝ) ^ ((n : ℝ)⁻¹)) atTop (𝓝 Stair.mu) := by
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le Stair.M_tendsto A_tendsto
    (fun n => ?_) (fun n => ?_)
  · exact Real.rpow_le_rpow (Nat.cast_nonneg _) (by exact_mod_cast hlo n) (by positivity)
  · exact Real.rpow_le_rpow (Nat.cast_nonneg _) (by exact_mod_cast hhi n) (by positivity)

end Polyplets.Prop6

#print axioms Polyplets.Prop6.prop6
