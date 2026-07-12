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

## Open

- Boundary weights → derive G (ladder item (⋆a) G ≡ 1 mod 9) the same way.
- Two-row closed form generalizing (2s+1)² (table above is raw material).
- The convergence + boundary analysis for a full proof of the law.
