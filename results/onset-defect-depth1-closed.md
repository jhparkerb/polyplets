# Depth one closes: the defect on n = 2H is an algebraic function, all constants derived

2026-08-09. Continues `results/onset-defect-law.md` and `results/discarded-term.md`;
supersedes their depth-1 content. Scripts, run from repo root, each seconds to
~45 s: `experiments/depth1_gap_walk.py`, `depth1_asymptotics.py`,
`depth1_minpoly.py`, `depth1_recurrence.py`, `depth1_sharpness.py`.

Summary of what changed today:

- The depth-1 defect `D_1(k) = T(2k,k) − law` is **exactly** the top coefficient
  of the column numerator `R_k` of the chain identity, and that top coefficient
  assembles from the **all-pairs cluster families alone** — the gap walk of
  `results/allpairs-kernel.md`. This removes the `P_k ≤ 19` wall entirely:
  `D_1(k)` is now computed exactly to `k = 200` in 42 s.
- The generating function is **algebraic**: an irreducible quartic
  `Φ(x, W) = 0` pins it, **derived** by the kernel method (§3), the earlier fit
  and its 144 holdout orders now confirmation. Its mod-3 reduction proves the
  onset is sharp: `D_1(k) ≠ 0` for every `k ≥ 1` (§3, 2026-09-05).
- From `Φ`, every measured constant of the depth-1 campaign is **derived
  exactly**: rate `9`, exponent `−1/2`, amplitude `C_1 = √6/(27√π)`, and the
  1/k coefficient
  **`a = 3293/92928 − 3251√3/185856 = 0.005138939956706…`** — an element of
  `Q(√3)`, which is why every recognition attempt at `k ≤ 19` (rationals,
  `√6`/`π` products) had to fail. The Second Term plan's kill criterion is
  hereby retired by derivation, not by more fitting.
- `D_1` **is** P-finite — at `(r,d) = (35,4)`, exhibited and verified. The old
  "not P-finite" verdicts were correct as scoped (envelopes `(4,4)`, `(6,8)`)
  and are now explained.

## 1. The exact frame: below-onset columns are finite data

`docs/proofs/diagonal-law.md` Step 4 gives, per column `k = n − H`:

```
[y^k] F = R_k(z) / (1−3z)^(k+1),   R_k ∈ ℤ[z],  deg R_k ≤ 2k+1,
```

and Step 5 splits off a correction polynomial `D(z)` of degree ≤ k. So **the
entire below-onset part of column k is k+1 integers** — the coefficients of
`D(z)` — and the campaign's depth-j defect is literally a coefficient:
`D_j(k) = [z^(k+1−j)] D(z)`. In particular the top one:

```
D_1(k) = lead(R_k) / (−3)^(k+1).                                   (I)
```

`experiments/depth1_gap_walk.py` verifies this **law-free**: `R_k` fitted from
the banked triangle column alone (no `P_k`) is uniquely determined for
`k ≤ 13`, with 39 down to 0 surplus equations all consistent, integer
coefficients, `lead(R_k)` matching `spine_deeper.py`'s ab-initio values
`1, 4, −80, 1753, −40928, 987355` at `k ≤ 5`, and (I) holding at every fitted
level. The premise question — is the rest of the triangle countable? — has this
precise answer: **per column, yes, at k+1 new integers per column**; depth j
touches only the top j of them.

## 2. The gap-walk identity: the P_k ≤ 19 wall falls

In Step 4's degree count, total z-degree `2k+1` is attained only when every
inequality is tight, and every tightness condition says the same thing: **every
cluster row carries exactly one surplus, i.e. has exactly 2 cells.** The top
coefficient therefore assembles from the all-pairs weight families
(`experiments/cluster_weight_dp.py` notation):

```
S(y) = Σ W(2^ℓ) y^ℓ,   B(y) = 1 + Σ W^b(2^ℓ) y^ℓ,   P̂(y) = Σ W^p(2^ℓ) y^ℓ
```

(interior, bottom-edge = top-edge by palindromy, pure), via the chain
`Σ_m E_b σ^m E_t (1−3z)^(k−m) + P (1−3z)^(k+1)` at top degree:

```
D_1(k) = [y^k]( P̂(y) − B(y)² / (3 + S(y)) ).                       (II)
```

`depth1_gap_walk.py` computes all three families exactly by the two-class gap
walk of `experiments/allpairs_kernel.py` (transitions verbatim; new start/end
vectors for the boundary and pure variants), validates against every
enumerated weight (interior ℓ ≤ 8; boundary/pure ℓ ≤ 5 from `KNOWN_WEIGHTS`,
plus a fresh ℓ = 6 DP holdout `W^b(2⁶) = 2703074`, `W^p(2⁶) = 517701`), and
then checks (II) against the **exact banked defect at all 19 cells k ≤ 19**.
Everything matches. The identity needs no `P_k`, so the series extends at will:
`k = 200` in 42 s, positive throughout, denominators exactly `3^(k+1)`.

The numerators `4, 80, 1753, 40928, 987355, …` are not in OEIS (2026-08-09).

## 3. The generating function is algebraic

Write `N(x) = Σ N_k x^k`, `N_0 = 0`, `N_k = 3^(k+1) D_1(k)` (so `N = 3F_1(3x)`).
The coefficients are integers: `N_k = 3^(k+1)T(2k,k) − P_k(2k)`, and `P_k`, of
degree `k`, takes the integer values `T(n,n−k)·3^(3k+1−n)` at the `k+1`
consecutive integers `n = 2k+1..3k+1`, hence integer values on all of ℤ. `experiments/depth1_minpoly.py` finds the minimal box by
a mod-p dimension scan (nothing below `deg_W = 4`, `deg_x = 8`) and solves it
exactly over `Q` — an irreducible quartic with coprime integer coefficients:

```
Φ(x,W) =   (27x−1)²(2187x⁶−5751x⁵+5502x⁴+3486x³−4329x²+449x+392)·W⁴
         + (27x−1)²(2916x⁶−7155x⁵+9636x⁴+54x³−4284x²+877x+420)·W³
         + 3(27x−1)(13122x⁷−29403x⁶+50193x⁵−14487x⁴−15039x³+5790x²+1640x−48)·W²
         + (27x−1)(8748x⁷−16767x⁶+36045x⁵−18573x⁴−7197x³+5076x²+1148x−16)·W
         + x(19683x⁷−30618x⁶+89667x⁵−63720x⁴−4920x³+16560x²+2736x−64)
```

`Φ(x, N(x)) = 0` through `x^200` exactly; the fit used orders 0..56, so 144
orders are holdout.

Status — **DERIVED, 2026-08-09 (Severance W2,
`experiments/severance_w2_kernel.py`).** The kernel method executed exactly
as sketched: kernel `D(u) = u² − y(1+u+u²)²` factors into two quadratic
branches in `s = √y` (small roots in `Q(s)[A,B]`,
`A² = (1−3s)(1+s)`, `B² = (1+3s)(1−s)` — the `1−3s` branch point is Φ's
`27x−1`); a 6×6 closure over the two analyticity conditions per small root,
the `[u³]` self-consistency, and `J(1)` pins the boundary unknowns; (II)
assembles `F_1 = c₀+c₁A+c₂B+c₃AB` and the degree-4 norm is `Φ` **coefficient-
for-coefficient (scale 1)** after `y = 3x`, `W = 3F₁+1`. No series data enters
the derivation; gate `experiments/severance_w2_gate.py` (RED selftest
fires) confirms exact equality and independent annihilation to `x^80`.

**Onset sharpness, proved (2026-09-05).** Reduce `Φ` mod 3. It factors:

```
Φ(x, W) ≡ 2 (W−1)³ ((1+x)W − x)          in F_3[x, W].              (III)
```

`F_3[[x]]` is an integral domain, so the reduction `N̄` of `N` must kill one
factor. `N̄ = 1` would need `N_1 ≡ 0`, and `N_1 = 4`; so `(1+x)N̄ = x`, i.e.
`N̄ = Σ_{k≥1} (−1)^(k+1) x^k`. Hence `N_k ≡ (−1)^(k+1) (mod 3)` for every
`k ≥ 1`, so `3 ∤ N_k`, so `N_k ≠ 0`, so

```
D_1(k) = N_k / 3^(k+1) ≠ 0        for every k ≥ 1.
```

The diagonal formula therefore fails at `n = 2k` for every `k ≥ 1`: **the onset
`n ≥ 2k+1` is sharp.** No tail bound, no `K_0`, no asymptotics — the whole
argument is (III) plus one integer. It also upgrades §2's observation that the
denominator of `D_1(k)` is exactly `3^(k+1)` from a check to a consequence.
Gate `experiments/depth1_sharpness.py` (45 s): rebuilds `D_1` to `k = 200` from
the gap walk alone, then checks integrality, annihilation through `x^200`,
(III) coefficient-by-coefficient in `F_3[x,W]`, the branch selection, and the
congruence — RED selftest fires on a perturbed `Φ` and on a perturbed series.
The proof inherits the standing of (II) (see Limits): derived from the proved
chain identity, machine-verified at 19 exact cells, not yet written up as a
standalone document.

## 4. Every constant of the campaign, derived

At `x = 1/27` (i.e. `y = 1/9`) the leading coefficient of `Φ` vanishes to
order 2 and nowhere else (`sympy.roots`: `{1/27: 2}`). Substituting
`W = V/v`, `v = √(1−27x)` collapses `Φ` to a polynomial in `(v, V)` whose
order-0 part factors as `(27V²−2)²` — two sheets crossing at
`V₀ = √6/9`, the first Taylor step a quadratic with roots
`−439/1584 ∓ 23√3/792`, every later step linear (`depth1_minpoly.py` walks
both branches; the physical one is selected by the independent 11-digit
Richardson measurement of `a`).

Consequences, all exact:

| quantity | derived value | independent measurement (`depth1_asymptotics.py`, K = 200) |
|---|---|---|
| growth rate | `27` in x, i.e. **9** per k | Richardson: `9` to the θ-table's resolution |
| exponent | branch `V/v` ⟹ `(1−27x)^(−1/2)` ⟹ **k^(−1/2)** | `θ = −1/2 ± 1.5e−10` |
| amplitude | `C_1 = V₀/(3√π)` = **√6/(27√π)** | matches to `1.6e−17` relative (order spread `1.2e−13`) |
| amplitude², θ-free | `A² = 2/243` | half-power ladder on `[y^k]F_1²`: matches to `3.4e−15` |
| 1/k coefficient | **`a = −1/8 − V₂/(2V₀) = 3293/92928 − 3251√3/185856`** | `0.00513893995671`, measured − exact = `4.7e−17` |

The recognition history is now fully explained: `a ∈ Q(√3)` with denominator
185856, while the `k ≤ 19` campaign scanned rationals and `√6`/`π`
combinations — the kill criterion ("526 rationals inside the bar") fired on a
constant outside its search field.

**The old θ_j-retrodiction concern is bypassed at j = 1**: rate, exponent and
amplitude no longer rest on Richardson calibration at all; they are branch
data of `Φ`.

**Why the weights' own growth (ρ ≈ 14.41) does not appear.** `P̂`, `B`, `S`
each diverge at `y = 1/ρ` (the localized boundary eigenvalue of the gap walk),
inside `|y| < 1/9`. In `P̂ − B²/(3+S)` the pole cancels: the spectral
projection of an isolated eigenvalue is rank one, so the residues factorize
(`π_res · σ_res = β²`) and the leading singularity subtracts out exactly —
numerically visible as the series growing at 9, not 14.41
(`depth1_gap_walk.py`: ratio·√(k/(k−1)) = 8.999978 at k = 50). The curve
confirms this as a closed door: every factor of `disc_W Φ` has degree ≤ 10,
while ρ has no minimal polynomial of degree ≤ 10 (PSLQ,
`results/allpairs-kernel.md`) — **ρ is provably not on the curve.** What
survives the cancellation is the walk's bulk edge: mass 9 = 3² per pair-row
(the convolution of two king steps; the (1,2,3,2,1) kernel), which is where
the per-cell rate 3 of `onset-defect-law.md` §4 comes from mechanically.

**P-finiteness, resolved.** `experiments/depth1_recurrence.py` derives from
`Φ` the order-4 ODE (coefficient degrees 29..36) and the recurrence
`Σ_{s=−32..3} q_s(n) N_{n+s} = 0`, `deg q_s ≤ 4` — **order 35, degree 4** —
verified in exact integers at 56 positions. `defect_pfinite_full.py`'s null at
`(4,4)` and the fresh null at `(6,8)` were both correct and both hopeless:
the true recurrence was an order of magnitude away.

## 5. What this supersedes or repairs

- `onset-defect-law.md` §2b: `a` is no longer "not recognisable, anomalously
  small" — it is exact, and small because `3293/92928 ≈ 0.03543` and
  `3251√3/185856 ≈ 0.03029` nearly cancel. The section's C_1 confirmation
  stands, now 10 orders sharper.
- `discarded-term.md`: the two discarded terms are exactly the two terms of
  (II) (`P̂` ↔ the P-term, `B²/(3+S)` ↔ the ρ-term); "the answer is in the
  cancellation" is now literal — it is the rank-one residue cancellation, and
  the remaining constants were computed without any high-order cluster
  weights, closing the obstacle that section named (the cumulant-inversion
  route around it was never needed).
- `diagonal-law.md` open item "onset sharpness in general": **closed at
  depth 1** by (III) above — `D_1(k) ≠ 0` for every `k ≥ 1`.
- The below-onset smoke test (`defect_holdout.py`) can now use exact `D_1` at
  any k — the depth-1 line needs no fitted amplitude at all.

## 6. Depth j ≥ 2: the shape of the rest, priced

`D_j(k)` is the `(j−1)`-th-from-top coefficient of `R_k`; each step down in
degree admits exactly one more unit of slack in Step 4's count, i.e. finitely
many new weight families. **Correction (Severance W3, 2026-08-09):** the
family class at depth j is total excess `Σ(s_i−2) ≤ j−1`, NOT "up to j−1
rows of size 3" — depth 3 needs the one-4-row family as well as two-3-rows,
and this note's original sub-claim undercounts. The identity (C)/(D) and
the excess-graded assembly live in `experiments/severance_w3_depths.py`;
depths 2 and 3 are CLOSED against all banked cells
(gate `experiments/severance_w3_gate.py`). The
conjecture this note's result makes natural: **every fixed depth is algebraic,
on curves sharing the branch point at 1/27**, with the measured depth family
`A_j = (√6/27)(25/81)^(j−1) binom(2j−2,j−1)/2^(j−1)` (verified j ≤ 4) as
branch data. Cost: the one-3 families are a modest extension of
`depth1_gap_walk.py` (state gains one marker); the assembly bookkeeping is
the real work. Desk work, no machine time.

## Limits

- (II) is derived from the proved chain identity plus the tightness
  observation (top degree ⟺ all rows of size 2); the bookkeeping is spelled
  out in §2 of this note and machine-verified at 19 exact cells plus the
  ℓ ≤ 8 / ℓ ≤ 6 weight validations. It is not yet written as a standalone
  proof document — the one thing the §3 sharpness proof still rests on.
- The Puiseux branch through `V₀` is selected by the measured `a` (the other
  sheet gives 0.0657…); `C_1` is branch-independent.
- Everything here is depth 1. The depth-j family and the boundary-layer /
  `g(x)` questions of `onset-defect-crossover.md` are untouched.
- The gap-walk transition table is trusted from `allpairs_kernel.py`
  (validated ℓ ≤ 8 against enumeration); its boundary/pure end-vectors are
  new here, validated ℓ ≤ 6.
