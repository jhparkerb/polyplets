# The mod-81 master equation: one tower level, measured

2026-08-11. Round-2 agent 1 (tower builder), per
`docs/triangle-structure-round2-brief.md` §Team shape.
Verifier: `experiments/tristruct/r2_tower_mod81.py` (exact integer
arithmetic throughout; all checks pass in ~1.4 s).

**Bits against enumeration error: 0.** No enumerated triangle cell is newly
checked by anything in this file — every check below is against the
P_k formula chain or internal to the derived series.
**Bits against formula-chain error: ~54 new** (conditional on the diagonal
law + renewal-chain formalism): 34 banked series coefficients (h_k and g_k,
k ≤ 17, from `scripts/derive_pk_fast.py`, whose fit anchors are real-sweep
cells per its audited REAL_H table) match the derived series mod 81 where
only mod-27 agreement was previously banked — one fresh 3-adic digit per
coefficient, 34 · log₂3 ≈ 54 bits, correlated with (not additive to) the
banked mod-27 checks.

Prior art, credited: `experiments/spine_deeper.py` check 1 (2026-07-13)
already held the mod-81 H-equation numerically; `results/defect-gas.md`
records it in one line. New here: the mechanical survivor derivation with a
completeness proof, the explicit monic curve, **G mod 81** (previously only
mod 27), the d=3 target verified on the fully derived series, and the
per-level cost measurement the round-2 brief names as load-bearing.

## The derivation

Everything is the valuation filter of `results/defect-gas.md` applied one
level up, over the full banked weight table (`cluster_weight_dp.KNOWN_WEIGHTS`,
all 31 cluster types with surplus k ≤ 5). Natural weights
Ŵ_c = W_c·3^(2k−ℓ−1) (interior), B̂_c = W^b_c·3^(2k−ℓ) (boundary).

**Completeness is free.** The row bound ℓ ≤ k (proved,
`docs/proofs/diagonal-law.md` Step 3) gives v₃(Ŵ) ≥ k−1 and v₃(B̂) ≥ k, so
mod 81 only interior clusters with k ≤ 4 and boundary clusters with k ≤ 3
can survive — all inside the banked table. **The level needed zero new
weight computations and no new ideas.**

Interior survivors (bar v₃(Ŵ) ≤ 3), coefficients reduced mod 81:

| cluster | k | ℓ | Ŵ | mod 81 |
|---|---|---|---|---|
| (2) | 1 | 1 | 25 | 25 |
| (3) | 2 | 1 | 441 | 36 |
| (2,2) | 2 | 2 | 1017 | 45 |
| (2,2,2) | 3 | 3 | 43002 | 72 |
| (2,2,2,2) | 4 | 4 | 68314·27 | 27 |

The one term new relative to mod 27 is the four-pair stack, whose weight
W(2,2,2,2) = 68314 was already banked (DP, milliseconds).

**Master equation mod 81** (fixed point matches all banked h_k, k ≤ 17):

    H ≡ 1 + 25uH⁻² + 36u²H⁻³ + 45u²H⁻⁴ + 72u³H⁻⁶ + 27u⁴H⁻⁸  (mod 81)

**Explicit monic curve** (degree 9 in H; verified as a series identity —
this is the object the deficit-proof division argument consumes, the mod-81
analogue of `experiments/deficit2_proof.py`'s E):

    E81(H,u) = H⁹ − H⁸ − 25uH⁶ − 36u²H⁵ − 45u²H⁴ − 72u³H² − 27u⁴ ≡ 0  (mod 81)

**Boundary: G mod 81, derived.** The bar v₃(B̂) ≤ 3 keeps four boundary
clusters per end — (2) with B̂ = 15, and (3), (2,2), (2,2,2) each entering
at 27 (B̂ = 189, 594, 24813 ≡ 27) — so

    ε ≡ 1 + 15uH⁻² + 27u²H⁻³ + 27u²H⁻⁴ + 27u³H⁻⁶  (mod 81),

identical for bottom and top (the one chirality pair in range, (2,3)/(3,2),
dies: v₃ = 4). The residue-formula denominator keeps five terms:

    den ≡ 1 + 50uH⁻² + 72u²H⁻³ + 54u²H⁻⁴ + 45u³H⁻⁶ + 54u⁴H⁻⁸  (mod 81),

and G = ε_b ε_t (1 − uH′/H)/den **reproduces every banked g_k mod 81,
k ≤ 17** — the same formula shape as G mod 27; no correction term appeared
at this level.

## The d=3 target, verified on the fully derived series

The family is (n,H) = (3k−2, 2k−2), T = P_k(3k−2)/27, onset k ≥ 3. With
H mod 81 and G mod 81 both derived, P_k(3k−2) mod 81 = Σ_j g_j·[u^(k−j)]H^(3k−2)
is pure algebra. Cross-checked against the exact banked P_k for k = 3..17,
then extended:

> **For k = 3..118: P_k(3k−2) ≡ 27·r_k (mod 81) with r_k cycling (2,0,1)
> from k = 3, i.e. r_k = 0 exactly at k ≡ 1 (mod 3).**

That is precisely round 1's sharpest target
(`results/triangle-hunt-synthesis.md`: v₃(P_k(3k−2)) > 3 ⟺ k ≡ 1 (mod 3),
exceptionless on real-sweep data through k = 11) and the measured d=3 cycle
(2,0,1) — now holding on the derived series ten times past the banked
range. This is verification of the known target on the derived object, not
a new pattern claim; the finer valuations at k ≡ 1 (7, 4, 4, 5 at
k = 4, 7, 10, 13) are invisible mod 81 and stay out of scope. Bits against
enumeration error from the k = 18..118 extension: 0 (nothing there was ever
counted; the derived series is the formula chain talking to itself).

## Per-level cost — the load-bearing measurement

What this level (27 → 81) cost, honestly:

- **New weights: zero.** The one new interior cluster and three new
  boundary clusters were all in the banked k ≤ 5 table.
- **New ideas: zero.** Valuation filter, fixed point, residue formula —
  all carried over unchanged; G's formula needed no correction term.
- **Object growth: mild.** Interior terms 4 → 5, ε terms 1 → 4, denominator
  terms 3 → 5, curve degree 7 → 9.
- **Wall time: ~1 s** compute, one desk session total.

But the census over future levels (mod 3^m, interior candidates =
compositions with 2k−ℓ−1 ≤ m−1; script section 5) shows where the tower
steepens. "newDP" = candidate types whose weight is in no banked table and
has no closed form; live DP settled the pair stacks
(W(2⁶) = 14115141, v₃ = 5 — it dies even mod 3⁶; W(2⁷) v₃ = 3;
W(2⁸) = 2927318947, v₃ = 0):

| m | modulus | serves d | candidates | weights in hand | survivors | needs new DP |
|---|---|---|---|---|---|---|
| 3 | 27 | 2 | 4 | 4 | 4 | 0 |
| 4 | 81 | 3 | 7 | 7 | 5 | 0 |
| 5 | 243 | 4 | 12 | 12 | 11 | 0 |
| 6 | 729 | 5 | 20 | 20 | 16 | 0 |
| 7 | 3⁷ | 6 | 33 | 28 | ≥21 | 5 |
| 8 | 3⁸ | 7 | 54 | 33 | ≥26 | 21 |
| 9 | 3⁹ | 8 | 88 | 34 | ≥30 | 54 |
| 10 | 3¹⁰ | 9 | 143 | 34 | ≥31 | 109 |

(deficit d needs mod 3^(d+1): T = P_k/3^d, unit residue mod 3 ⟺ P_k mod
3^(d+1). The brief's "mod-3^(d+2)" overstates by one level; d = 2 was proved
on the mod-27 curve, and mod-81 is exactly d = 3's level.)

**Verdict: the per-level cost grows — but with a free plateau first.**

- **d = 3, 4, 5 (mod 81, 243, 729): free.** Zero new weights; each level is
  a one-session mechanical extension of this file's derivation.
- **d = 6, 7 (mod 3⁷, 3⁸): cheap.** 5 and 21 new weights respectively, all
  pair-heavy stacks (ℓ ≥ 2k−m), the DP's easy regime — W(2⁸) took 0.2 s;
  hours of Python at worst, plus the matching boundary weights.
- **d = 8..19 (mod 3⁹..3²⁰): a compute campaign, growing exponentially.**
  Candidate count grows ×1.6–1.65 per level (measured m = 3..10, i.e.
  ~thousands of types by m = 20), and the wide low-ℓ clusters that enter —
  two-row weights up to k ≤ (m+2)/2, three-row up to (m+3)/2 — are the DP's
  measured hard regime (`results/defect-gas.md`: W(5,5) alone was 8.4 h;
  two-row cost ≈ ×16 per unit surplus). Extrapolated, the m = 20 table is
  months of Python / weeks of C++ on the widest entries. Not centuries (the
  valuation filter spares the full-tier catastrophe that killed
  P₁₇-from-the-gas), but firmly out of desk-work range. The one named lever
  that would collapse it: closed forms for the two-row family W(a,b)
  (a = 2 cubic and a = 3 quartic already banked in `defect-gas.md`) — if
  the pattern deg_b = a+1 were proved with a general formula, the expensive
  entries become free.

So: **cost is not constant; it is flat through d = 5, shallow through
d = 7, exponential after.** Per the brief this is a complete answer, and it
is a **go** for agent 2 at d = 3 — the mod-81 equation is in hand and the
next two levels are also effectively in hand.

## Handoff to agent 2 (Lagrange–Bürmann at d = 3)

- Curve: E81 above, monic in H, degree 9 — `deficit2_proof.py`'s sp.div
  route applies unchanged mod 81.
- G mod 81: ε and den as above, G = ε²(1 − uH′/H)/den with H′ from implicit
  differentiation of E81.
- Family GF: P_k(3k−2) = [u^k] G·H^(3k−2), so with u₀ = vH(u₀)³ the LB
  kernel is Φ = G·H⁻² (deficit-2 used Φ = G·H²; the sign of the H-shift is
  the only change).
- Target identity, read off the verified residues:
  Σ_{k≥3} P_k(3k−2) v^k ≡ 27·(2v³ + v⁵)/(1 − v³) (mod 81) on the family
  range k ≥ 3 — equivalently r-cycle (2,0,1) from k = 3, zeros at
  k ≡ 1 (mod 3). Unlike d = 1, 2 the target is periodic, not constant, so
  the rational identity to divide out carries the (1 − v³) denominator.
- Everything is conditional on the same frame as d = 1, 2: diagonal law +
  renewal-chain formalism (chain identity exact, 40/40 with boundaries).
