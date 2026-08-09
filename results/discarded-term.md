# The discarded term, identified: there are two, and they cancel

> **SUPERSEDED at depth 1, 2026-08-09:**
> `results/onset-defect-depth1-closed.md` computes both terms exactly at the
> top z-degree via the all-pairs gap walk, identifies the cancellation as the
> rank-one residue cancellation of the localized eigenvalue, and derives the
> rate, `θ_1 = −1/2`, `√6/27`, and the 1/k coefficient from the (fitted,
> 144-order-holdout) algebraic minimal polynomial. The obstacle and
> workaround discussed below were not needed at depth 1; depths j ≥ 2 remain
> open.

2026-08-09, revised the same day after adversarial review. Plan **Discarded
Term** of `docs/onset-defect-plans.md`, first pass. Not a derivation of the
constants — an identification of the objects that have to be computed, and a
correction to the first version's claim that only one of them matters.

## What the proof actually discards

`docs/proofs/grand-form.md` Step 3. With `μ := 1/z*` and
`G := E_b·E_t·u^(−1) = Σ_i g_i(y) z^i`:

```
[z^H](F − P) = μ^(H+1)·( Ĉ − ρ_H ),     ρ_H := Σ_{i>H} g_i z*^i
```

so, exactly and with nothing thrown away,

```
T(H+k,H)  =  [y^k](C·μ^H)  −  [y^k]( μ^(H+1)·ρ_H )  +  [y^k][z^H]P
                 └ the law ┘     └──── discarded ────┘   └ discarded ┘
```

**There are two discarded terms, not one.** They are switched off above onset by
two *different* facts:

- `ord_y(ρ_H) ≥ H` (from `ord_y(g_i) ≥ i−1`, Step 2), so `[y^k]ρ_H = 0` while
  `k < H`;
- `deg_z [y^k]P ≤ k`, so `[z^H][y^k]P = 0` while `H > k`.

Both cut in at exactly `H ≤ k`, which is why the onset is sharp and why it is the
*same* onset for both. Below onset both are live, and at depth 1 (`H = k`) neither
is negligible a priori. A derivation that keeps only the `ρ_H` term is incomplete.

## The structural statement — consistent, but a retrodiction

At depth `j`, `H = k+1−j` and `k = H+j−1`, so extracting `[y^k]` from `ρ_H` —
whose y-valuation is `H` — reaches exactly **`j−1` orders past the valuation**.
Depth is the number of extra y-orders taken.

Each extra order in `y` against a series whose coefficients grow polynomially
contributes one factor of `k`. So the construction predicts

```
θ_j − θ_1 = j − 1
```

with the absolute offset `θ_1` set by the leading coefficient's own asymptotics.
Measured (`results/onset-defect-law.md` §1, bias-calibrated): `θ_j = j − 3/2`,
hence `θ_j − θ_1 = j − 1` exactly, at every depth j = 1..7.

**Scope this honestly (review finding).** `θ_j = j − 3/2` was measured first, the
same day, so this is a retrodiction: the argument produces no new number and the
data cannot distinguish it from coincidence. Worse, the step "each extra y-order
contributes one factor of k" is *asserted*, not derived — it holds only if the
near-valuation y-coefficients of `g_i` grow polynomially with degree stepping by
about one per order, which is close to assuming the singularity type one is
trying to derive. Read this as *consistent with*, not *explained by*. The
half-integer part `θ_1 = −1/2` is not addressed at all.

## What has to be computed next — and it is NOT one asymptotic

**Correction (review, 2026-08-09).** The two discarded terms **largely cancel**,
verified exactly ab initio from the Lean weights at all six below-onset cells with
k ≤ 3:

| (k, H) | law | ρ-term | P-term | defect |
|---|---|---|---|---|
| (2, 2) | | −10.04 | 13 | 2.96 |
| (3, 3) | 78923/81 ≈ 974.4 | 155.4 | 177 | 21.6 |

At (3,3) the ρ-term alone is **7× the defect**. So the rate and amplitude live in
the *cancellation between the two terms*, not in either alone, and an asymptotic
for `g_i` by itself will overshoot. An earlier version of this section said the
question "reduces to one asymptotic" immediately after warning that keeping only
the ρ term is incomplete — it then did exactly that.

At depth 1 the ρ contribution is exactly `[y^k] g_{k+1}` (its leading
y-coefficient, since `ord_y(g_{k+1}) ≥ k`). The P contribution at the same cell is
`[z^k][y^k]P`. **Both** are needed, and so is their difference, which is where the
cancellation lives. The open question is therefore:

> how do the leading y-coefficient of `g_i` and the top z-coefficient of
> `[y^k]P` behave as `i, k → ∞`, and what is left after they cancel?

`g_i` comes from `E_b·E_t·u^(−1)`, so this is an asymptotic about the cofactor `u`
of the Weierstrass preparation and the edge series; `P` is the polynomial part of
the chain identity. Getting `3` per cell, `√6/27`, and `25/81` means getting both
asymptotics to enough accuracy that their difference survives.

**The obstacle, stated plainly.** `σ_j` — hence `u_j`, `ζ_j`, `z*` — is built from
the aggregated cluster weights `V(l,j)`, `Vt(l,j)`, and those are Lean-verified
only to `j ≤ 3` (`Weights.lean`, `Weights3.lean`, `Weights3Heavy.lean`). Three
orders will not give an asymptotic in `i`.

**The route around it, untested.** The wired `P_1..P_19` already determine
`a_j, b_j` to j = 19 (`experiments/grand_form_saddle.py`). Step 4–5 of the proof
map the cumulants of `μ` to those constants through the diagonal Lagrange
substitution. If that map inverts, `μ(y)` and `z*(y)` are recoverable to order 19
from data already in hand, without computing a single new cluster weight. That
would still leave `E_b`, `E_t` — the edge series — unrecovered, so it is a partial
route at best. Worth trying before any new weight computation.

## Status

- Discarded terms: **identified**, and there are two — decomposition and signs
  verified exactly at k ≤ 3.
- The two terms **largely cancel**; the answer is in the difference.
- `θ_j − θ_1 = j − 1`: **consistent**, but a retrodiction resting on an
  underived step.
- `θ_1 = −1/2`, the rate, `√6/27`, `25/81`: **not derived**. They reduce to the
  asymptotics of the ρ and P contributions *and their cancellation*.
- The plan's method line ("locate that term and keep it") is correct but
  under-specified: it must keep both, and the hard part is not locating the term
  but computing its asymptotics without high-order cluster weights.
