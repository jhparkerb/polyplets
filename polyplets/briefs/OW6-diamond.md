# OW-6 "Moat and Diamond" — Theorem 2: single-hole max area

Read first: `polyplets/OUTWORKS-PLAN.md`; `results/maxhole-proof.md`
END-TO-END (the complete paper-grade proof, including the moat-cycle
argument and its verification history); paper §8 `thm:diamond` (read-only);
`experiments/maxhole_box_construction.py` (the exact extremal family — 60
lines, transcribe, don't re-derive); `Polyplets/Defs.lean`. Banked ground
truth: `results/maxhole.txt` (M(n) = 0,0,0,1,1,2,3,5,6,8,10,13,15,18,21,
25,28 for n = 1..17). Size L, phased: OW-6a is COMMITTED scope, OW-6b is
committed except its final lemma, which is stretch with a STOP-and-report
protocol. A partial theorem landed green beats a full theorem stuck.

Target (paper Theorem 2): over n-cell king animals whose enclosed empty
cells form ONE 4-connected region, the maximum enclosed area is exactly
`⌊(n−2)²/8 + 1/2⌋` for every n ≥ 4.

## Definitions (`Polyplets/Holes.lean`) — none of this exists in Lean

Work translation-invariantly over arbitrary `S : Finset (ℤ × ℤ)` (no
anchoring — the theorem doesn't need it; state connectivity as
`KingConnected S`).

```lean
def rookAdj (p q : ℤ × ℤ) : Prop :=
  p ≠ q ∧ ((p.1 = q.1 ∧ |p.2 − q.2| = 1) ∨ (p.2 = q.2 ∧ |p.1 − q.1| = 1))

/-- The 4-component of `p` in the complement of `S` (as a Set). -/
def compComponent (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) : Set (ℤ × ℤ) :=
  {q | Relation.ReflTransGen (fun x y => x ∉ S ∧ y ∉ S ∧ rookAdj x y) p q}

/-- The enclosed (hole) cells: complement cells whose 4-component is finite. -/
def enclosed (S : Finset (ℤ × ℤ)) : Set (ℤ × ℤ) :=
  {p | p ∉ S ∧ (compComponent S p).Finite}

def SingleHole (S : Finset (ℤ × ℤ)) : Prop :=
  (enclosed S).Nonempty ∧ ∀ p ∈ enclosed S, ∀ q ∈ enclosed S,
    Relation.ReflTransGen (fun x y => x ∈ enclosed S ∧ y ∈ enclosed S ∧ rookAdj x y) p q
```

(Definitional freedom is yours on the exact packaging, but keep: holes are
4-components of the complement, enclosed = finite component, area = ncard.
Prove the basic sanity lemmas: `enclosed` is a union of components; a
finite component's every member has the same component (`ReflTransGen`
symmetry — the step relation is symmetric); `enclosed S` is finite —
enclosed cells lie inside S's bounding box, because any complement cell
outside the box has an unbounded monotone escape path, see 6a-3 below.)

## Phase OW-6a — the construction (lower bound), COMMITTED

Target:

```lean
theorem maxhole_lower (n : ℕ) (hn : 4 ≤ n) :
    ∃ S : Finset (ℤ × ℤ), S.card = n ∧ KingConnected S ∧ SingleHole S ∧
      (enclosed S).ncard = ((n − 2) ^ 2 / 8 : ℚ) + 1/2 |>.floor …
```

(state the RHS as `((n−2)^2 + 4) / 8` in ℕ-division — verify:
`⌊x²/8 + 1/2⌋ = (x² + 4) / 8` in ℕ for x = n−2; `decide` a few values,
`omega`-prove the general identity per residue class mod 4.)

The family (from `maxhole_box_construction.py`, verified n ≤ 60 there):

1. **Box hole**: `boxHole a b := {(x, y) | x + y ∈ [0, a−1] ∧ x − y ∈
   [0, b−1]}` — as a Finset via `Finset.Icc`-product filter on the parity
   sublattice (`(x+y) − (x−y)` even automatically; the populated cells are
   those with `x+y ≡ x−y (mod 2)`, i.e. all integer cells in the diagonal
   box — transcribe the python `box_hole` exactly).
2. **Ring**: `ring a b :=` the 4-neighbour set of `boxHole a b` minus the
   box. Prove `(ring a b).card = a + b + 2` — **only for admissible
   (a, b)**: both ≥ 2, or one = 1 with the other odd (the python
   docstring's non-degeneracy condition; (2,1) is DEGENERATE — see the
   n = 5 case below). Route: explicit parametrization of the four walls as
   arithmetic progressions (derive it once on paper from the python `ring_of`,
   pin the four lists, prove the union/card by `Finset` algebra +
   `omega`-grade parity bookkeeping). Sanity-gate the parametrization
   with `decide`/`native_decide` at (1,1), (2,2), (3,2), (3,3) before
   attempting the general proof.
3. **Enclosure**: `enclosed (ring a b) = boxHole a b` and it is single-hole:
   - ⊇: the box is rook-connected (row/column interval walk inside the
     diagonal box — prove via the u,v coordinates), its 4-boundary is
     ⊆ ring by construction, so its component is itself: finite ✓.
   - ⊆: any complement cell outside `boxHole` connects to infinity: give a
     monotone escape path (from p outside the hull, repeatedly step in a
     coordinate direction chosen by which hull inequality p violates —
     each step keeps it violated; formalize as "there is an infinite
     injective rook-path in the complement", hence the component is
     infinite — package as a reusable lemma
     `component_infinite_of_escape`). Cells in hull∖(box ∪ ring): show
     the hull decomposes exactly as box ∪ ring (the wall parametrization
     gives this).
4. **The split per n** (arithmetic case analysis, pinned):
   - n = 4: (a,b) = (1,1) — the diamond, area 1.
   - n = 5: the (2,1) box is degenerate — use the n = 4 ring PLUS one
     padding cell king-adjacent to it (e.g. adjacent to a wall cell,
     chosen not to touch the hole); area stays 1 = ⌊9/8 + ½⌋ ✓.
   - n ≥ 6: a + b = n − 2 with both ≥ 2, near-equal parity-optimal split:
     n−2 ≡ 0 (mod 4): a = b = (n−2)/2 (even); area = (n−2)²/8 exactly.
     n−2 ≡ 2 (mod 4): a = b = (n−2)/2 (odd); area = ⌈a²/2⌉ = ((n−2)²+4)/8.
     n−2 odd: a = (n−1)/2... i.e. {a,b} = {(n−1)/2 − 0, …} consecutive
     integers; ab even; area = ab/2 = ((n−2)²−1)/8.
     Verify each against `⌊(n−2)²/8 + ½⌋` by `omega` per residue.
   Anchor the assembled theorem numerically: `decide`-instances at
   n = 4..10 must equal M(n) from results/maxhole.txt (1,1,2,3,5,6,8).

## Phase OW-6b — the upper bound

Two lemmas + assembly. (I′) and the maximization are COMMITTED; (II′) is
the stretch.

1. **(I′) parity count, COMMITTED.** For finite nonempty `R` (the hole)
   let `ha := u-extent`, `hm := v-extent` (u = x+y, v = x−y; extent =
   max − min + 1 in ℕ). Then `R.card ≤ (ha * hm + 1) / 2`-style — the
   precise form: R injects into the parity sublattice of an ha×hm diagonal
   box, which has `⌈ha·hm/2⌉` points; mind which parity class is populated
   (corner-aligned dominant class). Elementary lattice count.
2. **Maximization, COMMITTED.** For `ha + hm ≤ n − 2`:
   `⌈ha·hm/2⌉ ≤ ⌊(n−2)²/8 + ½⌋` over positive integers — `omega`-grade
   after the right case split (mirror 6a-4's residue analysis; integer
   AM-GM: `4·ha·hm ≤ (ha+hm)²`).
3. **(II′) the moat bound, STRETCH.** `SingleHole S → n ≥ ha + hm + 2`
   (extents of the hole). This is the discrete-Jordan step
   (`results/maxhole-proof.md` "moat-cycle argument", five steps,
   machine-checked on 3,927 animals). Mathlib has NO digital topology;
   formalizing winding numbers for king-walks is a project in itself.
   Attempt budget: TWO focused attempts at a combinatorial substitute,
   then stop and report. Suggested substitute to try first (from the
   proof doc's step-5 skeleton, avoiding winding entirely): every
   anti-diagonal level u = c with `u_min ≤ c ≤ u_max` must contain ≥ 2
   animal cells... — CAUTION: the proof doc records that span-based
   arguments WITHOUT the enclosing property are provably too weak
   (§"Superseded notes": a diagonal path spans huge ha, hm with few
   cells). Any substitute must use single-hole-ness essentially. If no
   substitute closes, formalize the statement as a named hypothesis:
   ```lean
   def MoatBound : Prop := ∀ S …, SingleHole S → …  -- exact (II′)
   theorem maxhole_upper (hmoat : MoatBound) : …
   theorem maxhole (hmoat : MoatBound) (n : ℕ) (hn : 4 ≤ n) :
       IsGreatest {A | ∃ S, S.card = n ∧ KingConnected S ∧ SingleHole S ∧
         (enclosed S).ncard = A} (((n−2)^2 + 4) / 8)
   ```
   — the two-sided theorem conditional on one named, paper-proved lemma,
   with the unconditional lower bound from 6a. That is an honest,
   publishable state; report it as such.

## STOP-and-report items

- Any divergence between the formal enclosure behaviour and
  `maxhole-proof.md`'s claims (e.g. the ring card or the degenerate-(a,b)
  set differing from the python docstring).
- (II′): report the exact failure point of each attempted route; do not
  burn more than the budget.

## Done criteria

6a: `maxhole_lower` green, no `sorry`, anchors match banked M(n); guard
its footprint (standard + `Lean.ofReduceBool` for the anchors only —
the general theorem itself must be decide-free). 6b: (I′) + maximization
green; `maxhole` lands either unconditional (moat closed) or conditional
on `MoatBound` (reported). Commits:
`lean-ow: Holes — definitions + box-ring lower bound`,
`lean-ow: Holes — (I′) + maximization [+ moat | conditional]`.
