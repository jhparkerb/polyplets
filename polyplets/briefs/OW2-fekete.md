# OW-2 "Fekete's Ladder" — `Polyplets/Growth.lean`: λ exists, two-sided

Read first: `polyplets/OUTWORKS-PLAN.md`, `Polyplets/Sequence.lean` (OW-1)
and `Polyplets/UpperBound.lean` (OW-3) — both are PREREQUISITES; consume
`IsCanonicalAnimal`, `a`, `a_eq_sum`, `canonicalAnimal_finite`, the `a_<n>`
anchors, `a_le_choose`, `choose_le_pow`. Mathlib ingredient (verified in the
pinned tree): `Mathlib/Analysis/Subadditive.lean` — `Subadditive u`
(`∀ m n, u (m+n) ≤ u m + u n`), `Subadditive.lim`, and
`Subadditive.tendsto_lim (hbdd : BddBelow (Set.range fun n => u n / n)) :
Tendsto (fun n => u n / n) atTop (𝓝 h.lim)`. Size M. The orchestrator
reviews the concatenation injection below before you start proving — flag
any hole you find in it rather than patching silently.

The growth constant λ is quoted throughout the paper but its existence
(Klarner supermultiplicativity + Fekete) is nowhere formalized; both λ
bounds in §3 are statements about an object never shown to exist. This
brief closes that.

## Deliverables

```lean
theorem one_le_a {n : ℕ} (hn : 1 ≤ n) : 1 ≤ a n

theorem a_supermul {m n : ℕ} (hm : 1 ≤ m) (hn : 1 ≤ n) :
    a m * a n ≤ a (m + n)

noncomputable def lambda : ℝ := ...   -- see route

theorem lambda_tendsto :
    Filter.Tendsto (fun n => (a n : ℝ) ^ ((n : ℝ)⁻¹)) Filter.atTop (𝓝 lambda)

theorem a_le_lambda_pow {n : ℕ} (hn : 1 ≤ n) : (a n : ℝ) ≤ lambda ^ n

theorem lambda_le : lambda ≤ 3125 / 256

theorem lambda_lb : (3832 : ℝ) ≤ lambda ^ 6   -- λ ≥ 3832^(1/6) > 3.95
```

## Step 1 — the bar witness (`one_le_a`)

`bar n := (Finset.range n).image (fun i => ((i : ℤ), (0 : ℤ)))` satisfies
`IsCanonicalAnimal n (bar n)`: card by `Finset.card_image_of_injective`,
connectivity by chaining `Relation.ReflTransGen` along `i → i+1`
(adjacent bar cells are king-adjacent; induct on the x-distance), anchoring
trivial. Then `1 ≤ ncard` from membership + `canonicalAnimal_finite`
(`Set.one_le_ncard_iff_nonempty` or `Set.ncard_pos` with the finiteness).

## Step 2 — the concatenation injection (`a_supermul`)

Reviewed design — implement exactly this:

Given canonical `A` (m cells) and `B` (n cells), let
- `wA := A.sup' _ Prod.fst` (rightmost column of A; ≥ 0),
- `aY := max y among A's cells in column wA` (the column is nonempty by
  definition of sup on a finite set — take a witness),
- `bY := min y among B's cells in column 0` (nonempty: canonical B has a
  cell with x = 0).

Define `Φ(A, B) := reanchorY (A ∪ (B + (wA + 1, aY − bY)))` where `+ v` is
`Finset.image (· + v)` and `reanchorY` translates so min y = 0 (min x is
already 0: A keeps x-min 0, B's shift keeps all its x ≥ wA + 1 > 0).

Facts, in order:

1. **Disjointness & card**: A lives in x ≤ wA, shifted-B in x ≥ wA + 1;
   card = m + n via `Finset.card_union_of_disjoint` +
   `Finset.card_image_of_injective` (translation injective).
2. **Connectivity**: `(wA, aY) ∈ A` and `(wA + 1, aY) ∈ shifted-B` (it is
   B's column-0 min-y cell after the shift) are king-adjacent
   (`kingAdj`: Δ = (1,0)). Glue: `KingConnected` of a union of two
   connected sets joined by one cross edge — prove a reusable lemma
   `kingConnected_union_of_adj` (both inclusions `ReflTransGen`-lift into
   the union — `Relation.ReflTransGen.mono` on the step predicate — then
   route p → bridge-left → bridge-right → q).
3. **Translation invariance**: `IsCanonicalAnimal` after `reanchorY`;
   `KingConnected` and card are translation-invariant (image lemmas —
   prove once, generally, for any `v : ℤ × ℤ`).
4. **Injectivity via cut recovery.** Define, for a canonical (m+n)-cell C,
   the cut `x* := the unique boundary with |{p ∈ C : p.1 < x*}| = m`.
   Uniqueness: every column `0 ≤ x ≤ width` of a canonical animal is
   nonempty (`exists_x_eq_of_cross`, Finite.lean:45, between a column-0
   cell and a rightmost cell), so the left-count is strictly increasing in
   x* over the occupied range. Recovery: from `C = Φ(A,B)`, the left part
   re-anchored in y equals A (its x-anchoring never moved; its y-shift is
   undone by re-anchoring — A's min y in the union may be > 0 only if
   reanchorY shifted, track this with care: state recovery as "left part
   ≃ A up to y-translation, hence equal after y-re-anchoring") and
   likewise the right part re-anchored equals B. Conclude
   `Set.InjOn` of Φ on the product, then
   `a m * a n = ncard (product) ≤ ncard (target)` via
   `Set.ncard_le_of_injOn` (finiteness from `canonicalAnimal_finite`).
   NOTE the injection is into (m+n)-cell canonical animals — Φ's image
   must land there; that is steps 1–3.

## Step 3 — Fekete

`u : ℕ → ℝ := fun n => −Real.log (a n)`.
- `Subadditive u`: cases. `m, n ≥ 1`: from `a_supermul`, `Real.log`
  monotone on the cast (`one_le_a` gives positivity), `Real.log_mul`.
  `m = 0` or `n = 0`: `a 0 = 0` and `Real.log 0 = 0` in Mathlib, so
  `u 0 = 0` and the inequality is an equality — handle by `simp`.
- `BddBelow (range fun n => u n / n)`: from OW-3,
  `(a n : ℝ) ≤ (3125/256)^n` (cast `a_le_choose` + `choose_le_pow`;
  derive this cast lemma first), so `u n / n ≥ −Real.log (3125/256)`;
  `n = 0` gives `0`. Witness the bound `−Real.log (3125/256)` (negative,
  fine).
- `lambda := Real.exp (−hsub.lim)` where `hsub : Subadditive u` is the
  lemma above (`Subadditive.lim` takes the proof term; that's fine — it's
  defined from the range, `_h` unused).
- `lambda_tendsto`: `(a n)^(n⁻¹) = Real.exp (−(u n / n))` for `n ≥ 1`
  (via `Real.rpow_natCast`/`Real.rpow_def_of_pos`, positivity from
  `one_le_a`); compose `tendsto_lim` with `Real.exp` continuity
  (`Real.continuous_exp.continuousAt.tendsto.comp`), and patch the n = 0
  term with `Filter.Tendsto.congr'` + `Filter.eventually_atTop` (agree for
  n ≥ 1).
- `a_le_lambda_pow`: Fekete for SUPERmultiplicative sequences gives
  lim = sup: concretely `hsub.lim ≤ u n / n` for every `n ≥ 1` — that is
  `Subadditive.lim_le_div` (Subadditive.lean:47, takes the same BddBelow
  and `n ≠ 0`). Unfold: `−lim ≥ log (a n) / n` ⇒
  `lambda ^ n = exp (−lim · n) ≥ exp (log (a n)) = a n`. Mind
  `Real.exp_log` needs `0 < a n`.
- `lambda_le`: `hsub.lim ≥ −Real.log (3125/256)` because lim is the
  limit of `u n / n`, each `≥` the bound — use
  `le_of_tendsto_of_eventually` (`ge_of_tendsto`) on `lambda_tendsto`'s
  underlying limit, or directly: lim of a sequence bounded below.
  Then `lambda = exp(−lim) ≤ exp (log (3125/256)) = 3125/256`
  (`Real.exp_log` with positivity `3125/256 > 0`, `norm_num`).
- `lambda_lb`: instantiate `a_le_lambda_pow` at `n = 6` with the OW-1
  anchor `a_6 : a 6 = 3832`. (Docstring: λ ≥ 3832^{1/6} ≈ 3.9553 — the
  first machine-checked lower bound on the polyplet growth constant.)

## Notes

- Everything real-analytic here is plumbing; the risk concentrates in
  Step 2.4 (recovery). Budget accordingly: prove Steps 1–3 and Step 3
  first (Step 3 only needs the STATEMENT of `a_supermul`— you may
  temporarily develop against it as a hypothesis in a section, but the
  landed file has no sorry and no hypothesis).
- Do not strengthen to `m, n ≥ 0`: `a 0 = 0` breaks supermultiplicativity
  trivially and nothing needs it.
- Keep `lambda` and every theorem in namespace `Polyplets`.

## Done criteria

`lake build` green, no `sorry`; `#print axioms lambda_tendsto` and
`lambda_le` = standard three; `lambda_lb` additionally `Lean.ofReduceBool`
(inherits the `a_6` anchor) — all guarded. Commit
`lean-ow: Growth — λ exists, 3.95 < λ ≤ 3125/256`.
