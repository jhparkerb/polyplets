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

## Open

- Multi-row cluster weights: adjacent pair-pair = 339 = 3·113 in natural units —
  closed form / two-row generalization of (2s+1)²?
- The weight-3 ledger (classification at K=3) and h₃'s anatomy.
- The convergence + boundary analysis for a full proof of the law.
