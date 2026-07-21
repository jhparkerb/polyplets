# GF-3 — `Polyplets/Grand/MuRec.lean`: the μ-recursion (THE core theorem)

This is the mathematical heart of the whole formalization; everything after
it is bookkeeping. Read first: `polyplets/GRANDFORM-PLAN.md`;
`Polyplets/Grand/Series.lean`, `Polyplets/Grand/Mu.lean` (your inputs);
`Polyplets/Peel.lean` lines 1723–1737 (`d_rec` — the ONLY combinatorial
input); `Polyplets/Weights.lean` (defs of `d`, `V`, and the native_decide
values used in the gate). The statement was verified on banked data at all
170 in-range instances (`experiments/staircase_check.py`).

## Main theorem

```lean
/-- **The μ-recursion**: one transfer step multiplies the walk-top diagonal
family by the fixed series μ, exactly, for H ≥ k+1 (sharp onset). -/
theorem d_mu_rec : ∀ H k : ℕ, k + 1 ≤ H →
    (d k (H + 1) : ℚ) = ∑ i ∈ Finset.range (k + 1), mu i * (d (k - i) H : ℚ)
```

Prove by strong induction on `H` (`Nat.strong_induction_on`, motive
`M H := ∀ k, k + 1 ≤ H → …` exactly as displayed). Two helper lemmas are
proved first, each taking the strong-induction hypothesis as an explicit
argument `hrec` so they can live outside the induction:

## Helper 1 — upward iterate

```lean
lemma d_iter_up (H₀ ℓ : ℕ)
    (hrec : ∀ r, r < ℓ → ∀ k', k' + 1 ≤ H₀ + r →
      (d k' (H₀ + r + 1) : ℚ) =
        ∑ i ∈ Finset.range (k' + 1), mu i * (d (k' - i) (H₀ + r) : ℚ)) :
    ∀ k, k + 1 ≤ H₀ →
      (d k (H₀ + ℓ) : ℚ) =
        ∑ i ∈ Finset.range (k + 1), convPow mu ℓ i * (d (k - i) H₀ : ℚ)
```

Induction on ℓ. Base ℓ = 0: `convPow mu 0 = eps`, sum collapses to the i = 0
term. Step: `d k (H₀ + ℓ + 1)` by `hrec` at `r = ℓ` (valid: `k+1 ≤ H₀ ≤
H₀+ℓ`) gives `Σ_i mu i · d (k−i) (H₀+ℓ)`; rewrite each `d (k−i) (H₀+ℓ)` by
the ℓ-IH at level `k−i` (valid: `k−i+1 ≤ k+1 ≤ H₀`); collapse the double sum
with `sum_conv_collapse` (GF-1) into
`Σ_s conv mu (convPow mu ℓ) s · d (k−s) H₀ = Σ_s convPow mu (ℓ+1) s · …`.
Note `convPow mu (ℓ+1) = conv mu (convPow mu ℓ)` is definitional.

## Helper 2 — downward iterate (inverts with ν)

```lean
lemma d_iter_down (H₀ ℓ : ℕ)
    (hrec : … same signature as in d_iter_up …) :
    ∀ k, k + 1 ≤ H₀ →
      (d k H₀ : ℚ) =
        ∑ i ∈ Finset.range (k + 1), convPow nu ℓ i * (d (k - i) (H₀ + ℓ) : ℚ)
```

Start from the RHS: rewrite each `d (k−i) (H₀+ℓ)` by `d_iter_up` at level
`k−i` (valid `k−i+1 ≤ H₀`), collapse with `sum_conv_collapse` to
`Σ_s conv (convPow nu ℓ) (convPow mu ℓ) s · d (k−s) H₀`, then
`mu_conv_nu_pow` turns the coefficient into `eps s`, and the sum collapses
to the s = 0 term `d k H₀`. (Order of arguments in the conv: use
`conv_comm` as needed.)

## The main induction step

Fix `H`, assume `M H'` for all `H' < H`; fix `k` with `k + 1 ≤ H`.

1. Apply `d_rec k (H+1)` (hypothesis `k + 2 ≤ H + 1` ⟺ `k + 1 ≤ H` ✓) and
   cast to ℚ (`exact_mod_cast` pattern as in `Shape.lean`'s use of
   `c_ident`):
   `(d k (H+1) : ℚ) = 3·d k H + Σ_{j ∈ Icc 1 k} Σ_{ℓ ∈ Icc 1 j} V ℓ j · d (k−j) (H−ℓ)`.
   Note `H + 1 − 1 − ℓ = H − ℓ` (`omega`-managed; rewrite while still in ℕ).
2. For each `(j, ℓ)` in range, rewrite `d (k−j) (H−ℓ)` by
   `d_iter_down (H₀ := H − ℓ) (ℓ := ℓ)` at level `k − j`:
   - validity `(k−j) + 1 ≤ H − ℓ`: from `ℓ ≤ j ≤ k` and `k + 1 ≤ H`, `omega`;
   - `H₀ + ℓ = H` (ℕ-subtraction: `ℓ ≤ H` holds, `omega`);
   - `hrec` instances needed: heights `H − ℓ + r` with `r < ℓ`, i.e.
     `< H` — all covered by the strong IH `M`.
   Result: `d (k−j) (H−ℓ) = Σ_{t ∈ range (k−j+1)} convPow nu ℓ t · d (k−j−t) H`.
3. Regroup the triple sum `Σ_j Σ_ℓ Σ_t V ℓ j · (ν^{∗ℓ})_t · d (k−j−t) H` by
   `s := j + t`:
   `= Σ_{s ∈ Icc 1 k} (Σ_{ℓ ∈ Icc 1 s} conv (v ℓ) (convPow nu ℓ) s) · d (k−s) H`.
   This is `sum_conv_collapse` applied with `a := v ℓ` after swapping the
   j/ℓ order (`Finset.sum_sigma` / `Finset.sum_comm'`): first rewrite
   `Σ_{j ∈ Icc 1 k} Σ_{ℓ ∈ Icc 1 j} = Σ_{ℓ ∈ Icc 1 k} Σ_{j ∈ Icc ℓ k}`, then
   for fixed ℓ the (j, t)-collapse is exactly `sum_conv_collapse` with the
   `v ℓ`-vanishing (`v_vanish_lt`) absorbing the range mismatch between
   `Icc ℓ k` and `range (k+1)`. Take the ℓ-sum back inside afterwards.
   This step is the fiddliest Finset work of the whole plan — budget time
   for it; `omega` closes every index side goal.
4. By `mu_succ_eq` (GF-2), the coefficient `Σ_ℓ conv (v ℓ) (convPow nu ℓ) s`
   IS `mu s` for `s ≥ 1`; and `3·d k H` is the `s = 0` term (`mu_zero`).
   Assemble: `(d k (H+1) : ℚ) = Σ_{s ∈ range (k+1)} mu s · d (k−s) H`. ∎

## Gate (end of file)

```lean
theorem d_mu_rec_check_k1_H2 :
    (d 1 3 : ℚ) = mu 0 * d 1 2 + mu 1 * d 0 2 := by
  have h := d_mu_rec 2 1 (by norm_num)
  simpa [Finset.sum_range_succ] using h
theorem d_mu_rec_value_check : (40 : ℚ) = 3 * 5 + (25/3) * 3 := by norm_num
```
plus the (k, H) = (2, 3) instance against the native_decide values
`d 2 4 = 1019`, `d 2 3 = 136`, `d 1 3 = 40`, `d 0 3 = 9` with
`mu 2 = 833/27`. VERIFIED arithmetic (do not re-derive):
`1019 = 3·136 + (25/3)·40 + (833/27)·9 = 408 + 1000/3 + 833/3 = 408 + 611`.
The (1, 2) gate above is likewise verified: `40 = 15 + 25`.

## Pitfalls

- ℕ-subtraction everywhere: keep subtractions inside `d`'s arguments and
  discharge bounds with `omega` — never rewrite `H − ℓ + ℓ` without the
  `ℓ ≤ H` fact in context.
- Cast once: bring `d_rec` to ℚ at the top (push_cast) and stay in ℚ.
- The strong-induction plumbing: instantiate `hrec` for the helpers as
  `fun r hr k' hk' => M_ih (H − ℓ + r) (by omega) k' hk'` — heights
  `H − ℓ + r < H` need `r < ℓ ≤ H`; `omega`.
- If step 3's reindex resists after two serious attempts, STOP and report
  the exact goal — the orchestrator will restructure it.

## Done criteria

Green build, no `sorry`, standard axioms for `d_mu_rec` itself
(`#print axioms d_mu_rec` — the gates may add `Lean.ofReduceBool`).
Commit `lean-gf: MuRec — the mu-recursion, sharp onset`.
