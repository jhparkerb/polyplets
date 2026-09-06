# Brief: machine-check the staircase growth constant (Lemma 3 + Fekete)

Written 2026-08-06, decided after a sceptical pass over four routes to
Proposition 6 in Lean. **This is the whole job.** Everything else about
Proposition 6 stays a paper proof.

## Goal

Two theorems in Lean, sorry-free:

1. `M i * M j ≤ M (i + j)` — `results/subclasses.md` Lemma 3, where `M n`
   counts staircase king animals of area `n` up to translation.
2. `µ = lim M(n)^(1/n)` exists, with the limit-is-supremum half, so
   `M n ≤ µ ^ n` for every `n`.

Plus the conditional numeric floor in the style of `Growth.lean:779`'s
`lambda_gt_of_banked`: given `M 700` as a hypothesis, `µ ≥ 3.1234045…`.

## Why only this slice

Proposition 6's paper proof is three elementary steps a referee can check
unaided, and `make gate-middle-kingdom` already backs both lemmas
computationally with RED controls that make the check non-vacuous (zero
supermultiplicativity violations over all `i+j ≤ 700`; the `d=0` join provably
leaves the class; the area-`(i+1)` cut provably fails to invert; `P(n)` provably
is *not* supermultiplicative). Formalizing the rest competes against that and
loses on cost — the full statement is 2000–3000 lines for a result that is not
central to the project.

What this slice buys that neither the paper proof nor the gate does: the gate
checks supermultiplicativity on 700 terms; Lean makes it a theorem for all `n`.
That is the one place the existing evidence is genuinely finite.

## What already exists

- `polyplets/Polyplets/StairAnimals.lean` (190 lines, sorry-free, footprint
  `[propext, Quot.sound]`) — the `List Col` encoding, `Valid`, `join`, `cut`, and
  `join_valid` / `area_join` / `cut_join` / `join_injOn`. **The combinatorial core
  is done.** What is missing is the counting layer on top of it.
- `polyplets/Polyplets/Growth.lean:648–730` — the Fekete chain for `λ`. 83 lines
  that use exactly three facts about `a`: supermultiplicativity, `1 ≤ a k`, and an
  exponential ceiling.
- `polyplets/Draft/Prop6Skeleton.lean` — typechecking skeleton with the target
  statements and the `Fekete` structure. Start here; it compiles in ~3s via
  `lake env lean Draft/Prop6Skeleton.lean`.

## Deliverables

1. **`M n` and its finiteness.** `Nat.card` over `{l : List Stair.Col // Stair.Valid l ∧ Stair.area l = n}`.
   Finiteness comes from mathlib's `Set.finite_length_lt` plus a bounding
   injection (heights, offsets and length are all `≤ n`) — do **not** copy
   `Sequence.lean`'s `canonicalAnimal_finite`, which is a geometric argument
   about `Finset (ℤ × ℤ)` and a different, longer proof.
2. **Lemma 3.** Turn `join_injOn` into `M i * M j ≤ M (i + j)` by the card-of-
   product injection. `Growth.lean:608 a_supermul` is the same 26-line move one
   encoding over; follow it.
3. **The ceiling `M n ≤ 4 ^ n`.** Heights form a composition of `n` (`2^(n-1)`)
   and the offsets contribute `Π (h_j + 1) ≤ 2^n` because `Σ h_j = n` and
   `h + 1 ≤ 2^h`. This is a real induction, ~100–150 lines. Do not try to inherit
   `a_le_ratio_pow` via `M n ≤ a n`; that needs the geometric bridge this brief
   exists to avoid.
4. **Generalize Fekete — do not transcribe it.** Extract `Growth.lean:648–730`
   into a `Fekete` structure (`f`, `c`, `one_le_c`, `supermul`, `one_le`,
   `ceiling`) carrying `negLog`, `subadditive`, `bddBelow`, `growth`, `tendsto`,
   `le_growth_pow`. Then `lambda := polypletFekete.growth` and
   `mu := stairFekete.growth`. `Growth.lean` gets shorter; `mu` costs ~10 lines.

Budget: **~300 lines**, of which the ceiling is the largest single piece.

## Pitfalls, all measured

- **The numeric floor is conditional.** Fekete gives `M n ≤ µ^n` abstractly; the
  value `M 700` can only enter as a hypothesis or a named native leaf. State it
  as `mu_ge_of_banked`, mirroring `lambda_gt_of_banked`. Do not claim an
  unconditional `µ ≥ 3.1234…`.
- **`lambda`'s public names must survive the refactor.** `lambda`,
  `lambda_tendsto`, `a_le_lambda_pow`, `lambda_le`, `lambda_gt` are cited by
  `PROOF-STATUS.md`, `docs/lean-artifact.md` and the papers. Keep them as thin
  wrappers over the instance. `AuditOutworks.lean:120–126` pins
  `#print axioms lambda_tendsto` and `a_le_lambda_pow` to
  `[propext, Classical.choice, Quot.sound]` as `/-- info: -/` guards, so a
  footprint regression fails the build rather than passing quietly — that is the
  safety net, use it.
- **Naming.** Phase labels like `(1,1)` mean nothing outside
  `results/subclasses.md`'s table. If any appear, name the bits
  (`bottomRising`, `topFalling`).

## Acceptance

- `lake build` green, no `sorry` in the new material.
- `#print axioms` on both new theorems: standard axioms only, no native leaves
  (the conditional floor may carry the banked hypothesis, not a leaf).
- `AuditOutworks.lean`'s pinned footprints unchanged.
- Full `make` green (16 gates).
- `PROOF-STATUS.md` updated with the two new theorems and their tier.

## Explicitly out of scope

Lemma 2 (the stack bound and its transpose), Lemma 1 (the phase split), the
geometric layer `IsHVCanonical`, Corollary 4, and the squeeze `A_tendsto`. Those
are 1700–2700 further lines and are **not** authorized by this brief. If the
answer to "should we do those too" is ever revisited, the flip conditions are:
Paper 3 leads with Proposition 6 rather than the λ bracket, or jasonp would
rather not personally vouch for the lemmas in print.
