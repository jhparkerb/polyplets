# OW-1 "Name the Sequence" — `Polyplets/Sequence.lean`: define `a n`

Read first: `polyplets/OUTWORKS-PLAN.md` (conventions, gates), then
`Polyplets/Defs.lean` (30 lines — `kingAdj`, `KingConnected`, `IsCanonical`,
`T`), `Polyplets/Finite.lean` (crossing lemmas `exists_y_eq_of_cross` /
`exists_x_eq_of_cross`, `canonical_finite`, `T_eq_toFinset_card`), and skim
`Polyplets/Compute.lean` (`Tc`, `Tc_eq_T`, the native_decide anchor pattern at
lines 256–277). Size S. No mathematical risk.

The paper's headline object — the sequence a(n) itself, A006770 — does not
exist in the Lean tree; only the height-resolved `T n H` does. This brief
creates it and ties it to `T`.

## Deliverables

```lean
/-- `S` is the origin-anchored representative of a fixed polyplet of `n`
cells, any height: `n` cells, king-connected, min x = min y = 0. -/
def IsCanonicalAnimal (n : ℕ) (S : Finset (ℤ × ℤ)) : Prop :=
  S.card = n ∧ KingConnected S ∧
  (∀ p ∈ S, 0 ≤ p.1) ∧ (∃ p ∈ S, p.1 = 0) ∧
  (∀ p ∈ S, 0 ≤ p.2) ∧ (∃ p ∈ S, p.2 = 0)

/-- `a n`: the number of fixed polyplets of `n` cells (A006770). -/
noncomputable def a (n : ℕ) : ℕ := {S | IsCanonicalAnimal n S}.ncard
```

Definition is by ncard (mirroring `T`), and the sum identity is the theorem —
this keeps `a` definitionally parallel to `T` so OW-2/OW-7 can work with the
set directly.

1. **Height bridge.** For `S` with `IsCanonicalAnimal n S` and `n ≥ 1`, define
   its height `heightOf S := (S.sup' _ Prod.snd).toNat + 1` (or via `Finset.max'`
   on the y-image — pick the formulation that composes with `IsCanonical`) and
   prove
   `isCanonical_iff : IsCanonical n H S ↔ IsCanonicalAnimal n S ∧ heightOf S = H`
   (unfold both; the `∀ y ≤ H−1 / ∃ y = H−1` clauses are exactly `max = H−1`).
2. **Height range.** `height_le_card : IsCanonicalAnimal n S → 1 ≤ n →
   1 ≤ heightOf S ∧ heightOf S ≤ n`. Upper bound: every row
   `0 ≤ y ≤ heightOf S − 1` is nonempty — take a cell at y = 0 and one at the
   max, apply `exists_y_eq_of_cross` (Finite.lean:51) for each intermediate
   row; distinct rows give distinct cells, so `n = S.card ≥ heightOf S`
   (inject `Fin (heightOf S)` into `S` choosing one cell per row —
   `Finset.card_le_card_of_injOn` on a choice function).
3. **Finiteness.** `canonicalAnimal_finite : {S | IsCanonicalAnimal n S}.Finite`
   — either directly (width bound as in `canonical_finite`, Finite.lean:108)
   or as the finite union over `H ∈ Icc 1 n` of the `canonical_finite` sets
   via step 1. Prefer the union route: zero new geometry.
4. **The sum identity** (the headline; goes in the audit):
   ```lean
   theorem a_eq_sum (n : ℕ) (hn : 1 ≤ n) :
       a n = ∑ H ∈ Finset.Icc 1 n, T n H
   ```
   Partition `{S | IsCanonicalAnimal n S}` by `heightOf` using steps 1–2;
   `Set.ncard_eq_toFinset_card'`-style bookkeeping plus disjointness of the
   height classes (`heightOf` is a function — classes are trivially disjoint).
   Convert each class's ncard to `T n H` by `isCanonical_iff`.
5. **Computable twin + anchors.**
   ```lean
   def ac (n : ℕ) : ℕ := ∑ H ∈ Finset.Icc 1 n, Tc n H
   theorem ac_eq_a (n : ℕ) (hn : 1 ≤ n) : ac n = a n   -- Tc_eq_T + a_eq_sum
   theorem a_1 : a 1 = 1    := by rw [← ac_eq_a] <;> first | native_decide | omega
   theorem a_2 : a 2 = 4    := ...
   theorem a_3 : a 3 = 20   := ...
   theorem a_4 : a 4 = 110  := ...
   theorem a_5 : a 5 = 638  := ...
   theorem a_6 : a 6 = 3832 := ...
   ```
   Values verified against `results/triangle.txt` row sums (a = 1, 4, 20, 110,
   638, 3832, 23592, 147941 for n = 1..8). `a 6` costs about what the existing
   `T 6 4 = 1480` anchor costs (ComputeBridge.lean); if `a 7 = 23592` compiles
   in reasonable time add it, else stop at 6.
6. **The §9 GF lower bound** (paper claim: `a(n) ≥ Σ_{H≤10} T(n,H)` exactly,
   the rigorous strip-capture bound):
   ```lean
   theorem strip_sum_le_a (n : ℕ) (hn : 10 ≤ n) :
       ∑ H ∈ Finset.Icc 1 10, T n H ≤ a n
   ```
   `a_eq_sum` + `Finset.sum_le_sum_of_subset` (`Icc 1 10 ⊆ Icc 1 n`).

## Interface consumed by later briefs (do not rename)

- `IsCanonicalAnimal`, `a`, `a_eq_sum`, `canonicalAnimal_finite` (OW-2, OW-7)
- `ac`, `ac_eq_a`, the `a_<n>` anchors (OW-2's numeric λ lower bound)

## Notes

- `a 0 = 0` (the `∃ p ∈ S` clauses fail for `∅`); don't fight it — every
  downstream statement carries `1 ≤ n`.
- Mind `Int.toNat` at the height: cells have `0 ≤ p.2`, so `sup'` is ≥ 0;
  state helper lemmas in ℤ and convert once.
- House style: `omega` for the index arithmetic, no `Nat` subtraction
  gymnastics — mirror how `RowProfile.lean` handles the occupied-rows interval
  (read its fiber lemmas before writing `heightOf`; reuse if they fit).

## Done criteria

`lake build` green, no `sorry`; `#print axioms a_eq_sum` = standard three,
guarded in the audit (extend `Grand/Audit.lean` or open a new
`Polyplets/AuditOutworks.lean` — orchestrator's pick at integration);
anchors carry exactly `Lean.ofReduceBool` extra. Commit
`lean-ow: Sequence — a(n) defined, a = ΣT, anchors 1..6`.
