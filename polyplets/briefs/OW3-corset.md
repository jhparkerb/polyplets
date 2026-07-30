# OW-3 "Corset" — `Polyplets/UpperBound.lean`: a(n) ≤ C(5n, n)

Read first: `polyplets/OUTWORKS-PLAN.md`, `Polyplets/Defs.lean`,
`Polyplets/Sequence.lean` (OW-1, prerequisite), `Polyplets/Compute.lean`
(`stepExpand`/`reachSet` — the bounded-closure machinery you will imitate,
not import). Size M–L: the explorer correctness proof is the one real piece
of work in the OW-1/2/3 chain.

Target: the paper's "crude decision-tree bound" (§3): every n-cell king
animal is reproduced by a deterministic exploration that considers at most
5n cells, so `a n ≤ C(5n, n)`, whence λ ≤ 5⁵/4⁴ = 3125/256 ≈ 12.207 (the λ
step itself lives in OW-2; this file delivers the two ℕ-inequalities).

## Deliverables

```lean
theorem a_le_choose (n : ℕ) (hn : 1 ≤ n) : a n ≤ Nat.choose (5 * n) n

theorem choose_le_pow (n : ℕ) : Nat.choose (5 * n) n * 256 ^ n ≤ 3125 ^ n
```

## Part 1 — the exploration injection (`a_le_choose`)

**The mathematical design (fixed; do not weaken the constant).**
Fix a canonical animal `S` (`IsCanonicalAnimal n S`). Let `anchor S` be its
scan-least cell (lexicographic on `(y, x)`; exists, and every other cell of
`S` is scan-greater since min y = 0 pins the anchor into row 0). Run the
following deterministic process:

- State: `accepted : Finset (ℤ×ℤ)`, `considered : Finset (ℤ×ℤ)`,
  `queue : List (ℤ×ℤ)` (pending candidates, kept sorted in scan order —
  determinism is what matters, scan order is the convenient choice).
- Init: `accepted = ∅`, `considered = {anchor}`, `queue = [anchor]`.
- Step: pop the scan-least pending candidate `c`; query `c ∈ S`
  (this membership bit is the *decision*). If accepted, push onto the queue
  every king-neighbour of `c` that is scan-greater than `anchor` and not yet
  in `considered`, adding them to `considered`.
- Stop when `queue = []`.

Facts to prove:

1. **Completeness**: the process accepts exactly `S`. (⊇: induct along a
   king-path from the anchor — `KingConnected` gives one inside `S`; every
   cell of `S` is scan-≥ anchor, so no cell of `S` is ever barred from
   proposal. ⊆: only queried cells with `c ∈ S` are accepted.) This is the
   same closure argument as `Compute.lean`'s `reachSet` correctness — read
   that proof and mirror its structure.
2. **The 5n budget**: `considered.card ≤ 5 * n` at termination. Charge
   considered cells to their proposer:
   - The anchor proposes ≤ 4 new candidates (of its 8 neighbours, the 4
     scan-predecessors `(y−1, x−1..x+1)`, `(y, x−1)` are excluded by the
     scan-greater filter), and contributes itself: 1 + 4 = 5.
   - Every later accepted cell `c` proposes ≤ 5: `c` entered the queue as a
     neighbour of some earlier-accepted `p`; when `p` was accepted, ALL
     unconsidered neighbours of `p` were added to `considered` — so at the
     moment `c` is decided, `p` and every common king-neighbour of `p` and
     `c` are already in `considered`. `|N(p) ∩ N(c)| = 4` when `p, c` are
     orthogonal neighbours, `= 2` when diagonal (finite check — prove as a
     standalone lemma `card_common_neighbours` by `decide` on the offset,
     after translating so `p = (0,0)`; 8 cases for the offset of `c`).
     So ≥ 3 of `c`'s 8 neighbours are pre-considered: ≤ 5 new.
   - Rejected cells propose nothing.
   Total: `considered ≤ 5 + 5·(n−1) = 5n`.
3. **Injectivity**: the decision word reconstructs `S`. Formalize the
   process as a function of the *word*, not of `S`:
   `explore : List Bool → State` (structural recursion on the word;
   each `Bool` decides the current head candidate). Define
   `word S : List Bool` by replaying with the membership oracle
   (`decide (c ∈ S)`), prove `explore (word S) |>.accepted = S`
   (that IS completeness), and conclude `S₁ ≠ S₂ → word S₁ ≠ word S₂`.
   Then map `S ↦ the accept-position set of word S`, an `n`-subset of
   positions `< 5n` (pad conceptually; positions beyond the word length are
   never accepts), landing in `Finset.powersetCard n (Finset.range (5*n))`,
   whose card is `C(5n, n)` (`Finset.card_powersetCard`). Cardinality
   transfer: `Set.ncard_le_of_injOn`-style, via `canonicalAnimal_finite`.

**Engineering notes.**
- Termination of the process on arbitrary words: make `explore` recurse on
  the word (consume one `Bool` per step) — structurally decreasing, no
  well-founded recursion needed. The `S`-replay then terminates because the
  word is finite by construction: define `word S` by fuel = `5*n+1` steps or
  by strong recursion on `(S \ accepted).card` + queue length; pick one and
  don't mix. The fuel formulation (`exploreFuel : ℕ → ...`) with fuel `5*n`
  and a lemma "fuel ≥ considered budget suffices" is the least painful.
- Keep the whole development inside a `section Explore` with `S` fixed;
  state invariants as one `Invariant` structure (accepted ⊆ S ⊆ accepted ∪
  pending-reachable, considered superset relations, card accounting) and
  prove a single preservation lemma — piecemeal invariants will drown you.
- The scan order: `(y, x)` lexicographic as a `LinearOrder` instance via
  `Prod.Lex` on `ℤ ×ₗ ℤ` or a hand-rolled `le`; hand-rolled + `omega` is
  fine and avoids instance friction.

**Fallback (use ONLY if genuinely stuck after real effort, and say so
loudly in the report):** drop the common-neighbour refinement; each
accepted cell proposes ≤ 7 (proposer pre-considered), giving
`a n ≤ C(8n, n)`-grade. The λ corollary then degrades and OW-2's
`lambda_le` constant must change — this is a REPORTED deviation, not a
silent one. The primary target is the paper's constant; the machinery is
identical, so the fallback saves only the `card_common_neighbours` step —
which is a `decide`. Expect to land the primary.

## Part 2 — `choose_le_pow` (pure arithmetic)

Induction on `n`. Base `n = 0`: `1 ≤ 1`. Step: from
`C(5n+5, n+1) · (n+1) · (4n+1)(4n+2)(4n+3)(4n+4) =
 C(5n, n) · (5n+1)(5n+2)(5n+3)(5n+4)(5n+5)`
(five applications of `Nat.succ_mul_choose_eq` / `Nat.choose_symm_diff`
plumbing — or prove the ratio identity once over ℚ and cast), it suffices
that `256 · (5n+1)(5n+2)(5n+3)(5n+4)(5n+5) ≤
      3125 · (n+1)(4n+1)(4n+2)(4n+3)(4n+4)`.
**Verified**: the difference expands to
`400000·n⁴ + 1030000·n³ + 935000·n² + 349280·n + 44280` (n⁵ coefficients
cancel exactly) — all coefficients nonnegative, so after `ring_nf` this is
`positivity`/`nlinarith`-trivial. If the ℕ-side factorial juggling fights
you, prove the whole induction over ℚ with `Nat.cast_choose` and one
`div`-free formulation, then cast back.

## Done criteria

`lake build` green, no `sorry`, **no native_decide anywhere in this file**
(the injection is a proof, not a computation — the only `decide` is the
8-case `card_common_neighbours`, which is kernel `decide`, allowed).
`#print axioms a_le_choose` = standard three, guarded. Commit
`lean-ow: Corset — a(n) ≤ C(5n,n), C(5n,n)·256^n ≤ 3125^n`.
