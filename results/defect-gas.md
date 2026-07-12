# The defect gas: mechanism of the diagonal cumulant law, and 25 = 16 + 9

2026-07-12 (nibble #3: combinatorial meaning of H = 1, 25, 208, 1483, …).
Verifier: `experiments/defect_gas.py` — row model validated against the banked
triangle (exact, H ≤ 10, k ≤ 2), ledger reconstructs P₂ symbolically.

## The row model (an independent third enumeration algorithm)

Read a height-H king animal row by row. The k = 0 stratum is a drift walk
(one cell per row, offsets {−1,0,+1}: 3^{H−1} = T(H,H)). A diagonal-k animal is
the walk plus k surplus cells, organized into **defect clusters** (maximal runs
of multi-cell rows). Implemented as a transfer DP — states = row contents +
connectivity partitions, surplus-budgeted — it reproduces T(H+k, H) exactly
(banked values, H ≤ 10, k ≤ 2) *by an algorithm sharing nothing with either the
production TM (column sweeps) or Redelmeier*.

## h₁ = 25, PROVED by hand: 25 = 16 + 9

A weight-1 cluster is one row with a pair {a,b}, and 25 is its interior weight
(entry × exit contact counts, relative to the 9 = 3² walk choices it displaces):

- **adjacent pair** (b = a+1, internally connected): 4 contact positions below
  × 4 above = **16**;
- **gap pair** (b = a+2, joinable only through the middle): the below/above
  contacts must cover both cells and not be disjoint singletons — middle-below
  with any of 5 aboves, or middle-above with the 4 remaining belows = **9**.

Sanity anchor: T(4,3) = 15 + 25 + 15 = 55 (boundary pair, interior pair,
boundary pair) ✓. The paper's "25 single-defect species per walk site" is
literally 4² + 3².

## The k = 2 ledger (exact interior weights, fitted with holdouts)

Counts by defect geometry, normalized by 3^{H−5}, fitted exactly:

| cluster type | interior weight (coeff of H) | note |
|---|---|---|
| triple row | **441 = 21²** | the square pattern again |
| adjacent pair-pair (sep 0) | **1017 = 9·113** | the genuine interaction |
| pairs at separation 1 | **625 = 25²** | **exact factorization** — the single row between two pairs is unconstrained beyond its two independent 25-contacts; interaction lives only in the constant term |
| pairs at separation ≥ 2 | ideal gas, leading 625/2·H² | two independent 25s, unordered |

**The ledger sums to P₂(H+2) exactly** (symbolic identity, holdout-verified):
625/2·H² + 41/2·H − 642 on both sides. So the k ≤ 2 content of the cumulant law
is *fully explained*: b₁ = 25 is the one-cluster density, b₁²/2 the pair gas,
b₂ = −209/2 the net short-range correction assembled from 441, 1017, 625.

## What this means

- **The cumulant law is a 1D lattice-gas law.** Cumulants linear in n ⟺
  extensivity of cluster weights along the row direction; the exponential form
  ⟺ independence of well-separated clusters; the aⱼ boundary constants ⟺ the
  two chain ends. H(y) is the per-row grand-partition factor of the defect gas.
- **Road to proving the law** (deconditionalizing the Ternary Spine, the P_k
  injection machinery, the paper's diagonal forms): (i) each h_k is a FINITE
  computation in this model (cluster weights with bounded spread — the DP is
  exact order by order); (ii) validity for n ≥ 2k+1 with the exact 3-power
  normalization needs the transfer/cluster-expansion convergence + boundary
  analysis — standard-shaped statistical-mechanics work, now with the correct
  formalization in hand.
- **3-adic hook (Ternary Spine connection):** the measured weights are
  25 ≡ 1, 441 ≡ 1 (mod 3) with 441 = 21², and 1017 = 9·113 ≡ 0 (mod 9) —
  the ladder congruences (G ≡ 1 mod 9, H ≡ W mod 3) should ultimately be
  arithmetic facts about these cluster weights. The squares (5², 21²) suggest
  a left/right contact-factor structure worth pinning (entry and exit factors
  agreeing by up-down symmetry).

## THEOREM: single-row cluster weight = (2s+1)² (2026-07-12, proved)

In natural units (a single-row cluster displaces 3² of walk freedom regardless
of s — the ledger's 441 is 49·9, a normalization artifact), the interior weight
of an s-cell row cluster is exactly $(2s+1)^2$:
$$25 = 5^2\ (s{=}2),\quad 49 = 7^2\ (s{=}3),\quad 81 = 9^2\ (s{=}4),\quad
121 = 11^2\ (s{=}5),\ \dots$$
*Proof.* A width-2 gap in the row must be bridged by the below-contact $p$ or
the above-contact $q$ standing at its middle (wider gaps need surplus cells,
excluded at this weight); one cell bridges at most one gap. A row with $j$ wide
gaps therefore contributes $(s{+}2)^2$ for $j{=}0$, $\;2(s{+}3){-}1$ for
$j{=}1$, $\;2$ for $j{=}2$, nothing for $j\ge3$, and
$$(s{+}2)^2 + (s{-}1)(2s{+}5) + \binom{s-1}{2}\cdot 2 = 4s^2+4s+1 = (2s+1)^2.\ \square$$
(25 = 16+9 is the $s{=}2$ case; 49 = 25+11+11+2 the $s{=}3$ case. Verified
numerically s ≤ 6.)

**625 = 25² demystified.** Clusters at row-separation ≥ 1 compose as a Markov
chain: each cluster's weight already includes its own entry/exit contacts, and
the intervening walk chains them independently — so separation-≥1 weights
factorize EXACTLY, and interaction is strictly a contact (separation-0)
phenomenon. This is why the dilute-gas exponential form is the right ansatz.

**K = 3 validated.** With corrected transfer windows, the row model reproduces
the banked T(H+k, H) for k ≤ 3, H ≤ 8 exactly — the k=3 content of the law
(h₃ = 1483) confirmed by the independent algorithm. Two window bugs found and
fixed en route (recorded so nobody rediscovers them): naive spread caps and
budget-based gap caps are both WRONG — gaps may be bridged by cells already
placed below, and the only sound reach bound is the pending-block cost
(carrying a disconnected block costs ≥ 1 surplus per row while it converges
at ≤ 2 columns per row).

## THE MASTER EQUATION (2026-07-12) — the spine cubic DERIVED from the gas

**General cluster weight.** An ℓ-row cluster with row sizes (s₁,…,s_ℓ), all
sᵢ ≥ 2, surplus k = Σsᵢ − ℓ, is counted with a fixed single-cell contact row p
below and a free single-cell contact row q above (`cluster_weight()` in the
verifier). Enumerated:

| cluster | W | k | ℓ |
|---|---|---|---|
| (2) | 25 | 1 | 1 |
| (3) | 49 | 2 | 1 |
| (4) | 81 | 3 | 1 |
| (2,2) | **339** = 3·113 | 2 | 2 |
| (2,3) = (3,2) | **930** = 3·310 | 3 | 2 |
| (3,3) | 3325 | 4 | 2 |
| (2,4) | 1993 | 4 | 2 |
| (2,2,2) | **4778** = 2·2389 | 3 | 3 |

(W(2,2) = 339 matches the k=2 ledger's 1017/3 exactly. **Third window bug of
the thread:** W=6 clipped W(2,2,2) to 4776; caught because the master equation
then gave h₃ = 1465 ≠ 1483. Weights above confirmed stable under window widening.)

**Renewal chain ⇒ master equation.** Macro-steps: drift (weight 3z) or cluster
(weight W_c y^{k_c} z^{ℓ_c+1}); per-row growth μ(y) solves
1 = 3z + Σ W_c y^{k_c} z^{ℓ_c+1} at z = 1/μ, i.e. **μ = 3 + Σ W_c y^{k_c} μ^{−ℓ_c}**
(verified exactly at order y²: per-row [y²] of ln A_H = 347/54 both ways).
Substituting the diagonal-Lagrange parametrization μ = 3H(u), u = yμ/27:

$$\boxed{\;H(u) \;=\; 1 \;+\; \sum_c \hat W_c\, u^{k_c}\, H^{-(k_c+\ell_c)},
\qquad \hat W_c = W_c\cdot 3^{\,2k_c-\ell_c-1}.\;}$$

So the ledger's 441 = 49·9 and 1017 = 339·3 are not normalization artifacts —
they ARE the natural weights Ŵ. Verified **exactly through order u³**:
h₂ = −2·25² + 441 + 1017 = 208; h₃ = 1483 from
(Ŵ = 6561, 25110, 25110, 43002 at k=3) — `check_master()`.

**VALUATION LEMMA.** Every cluster row carries ≥ 1 surplus, so k ≥ ℓ and
v₃(Ŵ) = 2k − ℓ − 1 + v₃(W) ≥ k − 1 ≥ 1 for every cluster **except the bare
pair-row** (k = ℓ = 1, Ŵ = 25 ≡ 1 mod 3). Combinatorially trivial; arithmetically
decisive. Consequences, each verified against ALL 18 known coefficients of H:

- **mod 3:** H = 1 + uH⁻² ⟹ **H³ = H² + u — the Ternary Spine cubic, DERIVED.**
  The spine cubic says: *mod 3 the defect gas is a gas of bare pair-rows.*
- **mod 9:** 441 + 1017 = 1458 ≡ 0 ⟹ H³ = H² + 25u ≡ H² + 7u — the measured
  mod-9 lift, derived.
- **mod 27:** all k ≥ 4 clusters die (v₃ ≥ 3), leaving the FINITE equation
  H = 1 + 25uH⁻² + 441u²H⁻³ + 1017u²H⁻⁴ + 43002u³H⁻⁶ — matches all 18
  coefficients. An explicit algebraic characterization of H mod 27 from five
  integers, subsuming the measured H³−H² ≡ 25t lift.

Status: conditional on the diagonal law + the renewal formalism (chain
decomposition is exact combinatorics per order; the law extraction is the same
Lagrange step used throughout the Ternary Spine work). Within that frame the
ladder item (⋆b) H ≡ W mod 3 is no longer a finitely-verified input but a
**theorem of the gas** — and the proof-of-the-law program (i)-(ii) above now
has its Chapter 1 written: h_k = finite cluster computation, demonstrated
through k = 3.

## BOUNDARY WEIGHTS: G derived, the whole ladder falls (2026-07-12)

**Boundary weights.** A bottom-boundary cluster (no p row, counted relative to
the renewal q above) has weight W^b; enumerated: single rows **5, 7, 9 = 2s+1**
— the interior (2s+1)² literally factors as entry × exit — and (2,2) = 66,
(2,3) = 177, (3,2) = 130, (2,2,2) = 919.

**The chain identity with boundaries is EXACT**: with E_b = z(1 + ΣW^b yᵏzˡ),
E_t its reversal, D = 1 − 3z − ΣW yᵏz^{ℓ+1}, and a pure-cluster polynomial,
F(y,z) = E_b E_t/D + pure reproduces the banked triangle **40/40** (k ≤ 3,
H ≤ 10, every boundary correction included). This is the complete combinatorial
decomposition underlying the diagonal law: single-cell rows are renewal points;
everything else is a finite catalogue of clusters.

**G from the residue at z\* = 1/μ** (verified exactly against known G to u³):
$$G \;=\; \frac{\varepsilon_b\,\varepsilon_t\,(1-wH')}{1+\sum_c(\ell_c{+}1)\hat W_c u^{k_c}H^{-(k_c+\ell_c)}},
\qquad \varepsilon = 1+\sum_c \hat B_c u^{k_c}H^{-(k_c+\ell_c)},\ \ \hat B_c = W^b_c 3^{2k_c-\ell_c}.$$

**(⋆a) G ≡ 1 (mod 9), DERIVED.** Boundary valuation v₃(B̂) ≥ 2k−ℓ ≥ k kills
every boundary cluster mod 9 except the pair-row (B̂ = 15); the denominator
reduces structurally to 1 + 50uH⁻² (the ℓ=k=2 case saved by its ℓ+1 = 3).
What remains, (1+15uH⁻²)²(1−uH′/H) ≡ 1+50uH⁻² (mod 9), collapses to
**H²H′ + 3uH′ + 2H ≡ 0 (mod 9)** — and substituting u = 4(H³−H²) (from the
derived mod-9 cubic) plus its derivative identity (3H²−2H)H′ ≡ 25 gives
H′(3H³−2H²) + 2H = 25H + 2H = 27H ≡ 0. ∎

**(⋆c) CLOSED — symbolic proof (2026-07-13).** Let X ∈ (ℤ/9)[[u]] be the
unique solution of X³ = X² + 25u with X(0) = 1 (the master equation mod 9;
uniqueness via the fixed-point form X = 1 + 25uX⁻²), and W = X mod 3. Then

$$H(u^3) \;\equiv\; X^2 + 25u - 3u^2 - 3uW \pmod 9,
\qquad\text{hence}\qquad S = \tfrac{H^3 - H(u^3)}{3} \equiv u^2 + uW \pmod 3.$$

*Proof.* (i) Y := H(u³) mod 9 satisfies Y³ = Y² + 25u³ with Y(0) = 1;
dividing by the unit Y² gives the fixed-point form Y = 1 + 25u³Y⁻², whose
coefficients are forced recursively — so that cubic + constant term pins Y
uniquely. (ii) The candidate Y\* = X² + 25u + 3E with E = −u² − uW satisfies
the same cubic: mod 9, (A+3E)³ ≡ A³ and (A+3E)² ≡ A² + 6AE, so with
A = X² + 25u = X³ we get Y\*³ ≡ X⁹ and Y\*² ≡ X⁶ + 6EX³. Expanding
X⁹ = (X²+25u)³ termwise mod 9 (3·25 ≡ 3, 3·625 ≡ 3, 25³ ≡ 1):
X⁹ ≡ X⁶ + 3uX⁴ + 3u²X² + u³. Hence
Y\*³ − Y\*² − 25u³ ≡ 3(uX⁴ + u²X² + u³ + EX³) (mod 9), and the bracket
vanishes mod 3: with X ≡ W, X³ ≡ W² + u, X⁴ ≡ W² + u + uW,
it collapses to uW² + u² − uW³ = uW² + u² − u(W²+u) = 0. (iii) By
uniqueness Y = Y\*, and H³ − H(u³) ≡ X³ − Y\* = 3u² + 3uW. ∎

Machine checks (`check_ladder()`): the closed-form identity holds on the
pure-algebra fixed point to u³⁰⁰ and against the banked 18 coefficients;
the bracket cancellation re-verified as an 𝔽₃ series identity.

**Net effect on the Ternary Spine:** all three ladder items (⋆a,b,c) now stand
on the defect gas **symbolically** — the ladder is retired as an empirical
input in full. The Spine's conditionality collapses from "law +
finitely-verified ladder" to "law + renewal chain formalism", the chain
identity is exact combinatorics (40/40 with boundaries), and the law's shape
is a theorem (`docs/proofs/diagonal-law.md`).

## The weight DP, k ≤ 5 ab initio, and the P₁₇ reach verdict (2026-07-13)

**Row-transfer DP for weights** (`experiments/cluster_weight_dp.py`): counts a
cluster's configurations without listing them (state = current row's cells +
connectivity partition; stranded pending blocks pruned). Validated against all
21 enumerated weights. Direct enumeration is Ω(W) = Ω(14^ℓ) for stacked pairs
— hopeless past k ≈ 6 — and the DP smashes that floor: W(2,2,2,2) = 68,314 in
milliseconds where enumeration needed hours, all-pairs k=6 (14,115,141) in 0.1s.

**Grand form ab initio through u⁵.** With the full k ≤ 5 weight table (31
types, `KNOWN_WEIGHTS`), the master equation gives
H = [1, 25, 208, 1483, **20688, 130208**] and the boundary residue gives
G = [1, −5, −62/9, −1625/81, **−56842/729, −2170913/6561**] — every
coefficient matching the banked series exactly (`check_grand_form()`, runs in
ms). Both halves of G·Hⁿ now derive from finite local enumerations through
order 5. Boundary single-row pattern continues: (6,) has interior 169 = 13²,
boundary 13 = 2s+1.

**Reach measurement — P₁₇ from the gas is DEAD.** Full-tier DP cost:
k=4: 3.1s, k=5: 65s, k=6: >530s (killed incomplete) — ≈20× per k in Python.
Extrapolated to k=17: ~10¹⁷ s; a C++ rewrite (~100×) plus a thousand cores
buys five orders and leaves centuries. Realistic reach: k ≈ 7 (Python,
hours), k ≈ 9–10 (C++ effort). The strict H20 sweep (~10h) therefore remains
the ONLY route to certifying P₁₇ for a(37); the gas route is priced out.
(Two pathologies recorded: naive fixed-point iteration of μ in exact rationals
blows up big-int sizes on pre-convergence garbage — solve order-by-order; and
the u-series master-equation H is NOT the y-series chain μ — mixing them
breaks the residue formula silently at order 1.)

## Cross-pollination round (2026-07-13) — `experiments/spine_deeper.py`

Applying the gas machinery to the open-problem list; all checks green:

- **Onset sharpness ab initio, k ≤ 5.** deg R_k = 2k+1 exactly (leading
  coefficients 1, 4, −80, 1753, −40928, 987355 — sign-alternating from k=2,
  ratio drifting toward ~24). Two levels past what banked data could verify.
  General-k proof still open, and now known to be harder than hoped: the
  route via a rational top-coefficient GF dies because…
- **The all-pairs weight family is NOT C-finite.** An order-7 recurrence fit
  on ℓ ≤ 14 is refuted at ℓ = 16 (non-integer prediction). Structural
  reason: the gap between pending blocks is an unbounded ±2 walk, so the
  state space is infinite and the GF is at best algebraic. Growth ≈ 14.41
  (ratios 14.398, 14.404, 14.405, 14.407 at ℓ = 7..10; W(2¹⁰) =
  607,573,757,457). Kernel method = the open route to an exact constant.
- **Mod-81 master equation, finite (six terms).** The four-pair stack enters
  at Ŵ ≡ 27; everything else k ≥ 4 dies. Matches all banked coefficients;
  unique fixed point.
- **G mod 27 derived.** Only the pair-row boundary survives (v₃(B̂) ≥ k kills
  k ≥ 2), the denominator keeps 50uH⁻² + 18u²H⁻³ + 18u³H⁻⁶; the residue
  formula reproduces every banked g_j mod 27.
- **The deficit-2 spine law T(3m+2, 2m+1) ≡ 2 (mod 3) — previously an
  unproved observation — now holds on the fully-derived series for
  m = 1..94** (P_{m+1}(3m+2) ≡ 18 mod 27 via the mod-27/81 fixed points +
  derived G mod 27). Banked data could only reach m ≈ 11. Symbolic closure
  is finite algebra of the same kind that closed (⋆c), left open.

## The hole-free gas (2026-07-13) — `experiments/holefree_gas.py`

The hole-free height triangle has its own diagonal law, derived ab initio:
weights are the hole-free configuration counts (pair 25→**24** — the one
holed config is the minimal diamond, gap pair bridged middle-below AND
middle-above; triple 49→47; stacked pairs 339→304; boundary 5, 7 unchanged,
62 for stacked pairs), and the master equation + boundary residue give

$$P^0_1(n) = 24n - 42, \qquad P^0_2(n) = 288n^2 - 1113n + 507,$$

exact against every banked hole-free fixed-height GF value (H ≤ 8, 5+3
holdouts). Note 288 = 24²/2 — the ideal-gas square of the new density.

**Structural corollary: the spine cubic is carried by the hole-makers.**
24 ≡ 0 (mod 3): every hole-free surviving weight has positive 3-valuation,
so the hole-free triangle is mod-3 trivial in-band, and the full triangle's
entire mod-3 structure (W³ = W² + t and everything downstream) lives in the
hole-making configurations. Feeds the OEIS-staged A₀ column.

## Open
- Two-row closed form generalizing (2s+1)² (weight table is raw material).
- ~~The convergence + boundary analysis for a full proof of the law~~
  **DONE 2026-07-12**: `docs/proofs/diagonal-law.md` — separation lemma +
  chain identity + row bound (ℓ ≤ k) + partial fractions prove the law's
  shape with sharp-shaped onset n ≥ 2k+1 and integer-valued P_k;
  checker `experiments/diagonal_law_proof_check.py`.
