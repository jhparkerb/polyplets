# The d=3 sleeve unit formula, proved on the mod-81 curve

2026-08-11. Round-2 agent 2 (prover), per
`docs/triangle-structure-round2-brief.md` §Team shape. Verifier:
`experiments/tristruct/r2_prove_d3.py` (exact integer/symbolic arithmetic
throughout; all checks pass in ~1 s). Input: agent 1's mod-81 tower
(`results/triangle-r2-tower-mod81.md`, re-derived and re-asserted inside the
verifier, not trusted).

**Bits against enumeration error: 0 new** — no enumerated cell is newly
checked here; the 12-cell family table below re-confirms agreements already
banked in round 1 (`results/triangle-hunt-synthesis.md`, verified through
k = 11). **Bits against formula-chain error: 0 new** — this file is a
derivation, not a measurement; conditional on the proof, the 9 real-sweep
family cells' banked agreement (≈ 9·log₂3 ≈ 14 bits) becomes a check of the
formula chain, but that agreement was round 1's output, not this file's.
The deliverable is the proof.

## Statement

**THEOREM (conditional frame below).** For every k ≥ 3,

> P_k(3k−2) ≡ 27·r_k (mod 81), with r_k = 2, 0, 1 for k ≡ 0, 1, 2 (mod 3).

Equivalently, on the d=3 deficit family (n, H) = (3k−2, 2k−2), where
T(3k−2, 2k−2) = P_k(3k−2)/27:

- T ≡ 2 (mod 3) for k ≡ 0 (mod 3),
- T ≡ 1 (mod 3) for k ≡ 2 (mod 3),
- v₃(P_k(3k−2)) ≥ 4 for k ≡ 1 (mod 3);

and since r_k ∈ {1, 2} is a unit for k ≢ 1, v₃(P_k(3k−2)) = 3 exactly there,
so

> **v₃(P_k(3k−2)) > 3 ⟺ k ≡ 1 (mod 3)** — round 1's sharpest target
> (synthesis, negative 5), now a theorem for ALL k ≥ 3, not an observation
> through k = 11.

The finer valuations at k ≡ 1 (7, 4, 4, 5 at k = 4, 7, 10, 13) are invisible
mod 81 and remain open; they belong to the mod-3⁵⁺ levels of the tower.

## Conditional frame, stated in full

Identical in kind to the proved d = 1 (T3, `results/ternary-spine.md`) and
d = 2 (`experiments/deficit2_proof.py`) cases:

- **(A1)** The diagonal-law shape theorem and the grand form
  P_k(n) = [u^k] G(u)·H(u)^n for n ≥ 2k+1 — both PROVED
  (`docs/proofs/diagonal-law.md`, `docs/proofs/grand-form.md`; Lean-checked,
  standard axioms).
- **(A2)** H ≡ (fixed point of the mod-81 master equation) (mod 81) at all
  orders — derived from the defect-gas renewal formalism
  (`results/defect-gas.md`) with completeness from the row bound ℓ ≤ k
  (proved); machine-verified against banked h_k for k ≤ 17
  (`results/triangle-r2-tower-mod81.md`).
- **(A3)** G ≡ ε_b ε_t (1 − uH′/H)/den (mod 81) at all orders, with the four
  ε-terms and five den-terms of agent 1's file — the boundary residue formula
  of `results/defect-gas.md` reduced mod 81; machine-verified against banked
  g_k for k ≤ 17.
- **(A4)** The eleven surviving cluster weights (5 interior, 4 boundary,
  5 denominator entries, overlapping lists) — finite integers from the
  banked DP table (`experiments/cluster_weight_dp.py`), all with independent
  low-order enumeration cross-checks.

Everything below (A1)–(A4) is unconditional algebra: a proved inversion
lemma, one implicit differentiation, a units inventory, and an exact
polynomial division whose remainder vanishes identically mod 81.

## The proof

Write S(v) = Σ_{k≥0} P_k(3k−2) v^k. The theorem is the k ≥ 3 part of

> S(v) ≡ c₀ + c₁v + c₂v² + 27·(2v³ + v⁵)/(1 − v³) (mod 81),

with c₀ = P₀(−2) = 1, c₁ = P₁(1) = −20 ≡ 61, c₂ = P₂(4) = 649 ≡ 1 (mod 81):
[v^k] of the rational term is 27·2, 0, 27 for k ≡ 0, 1, 2 (mod 3), k ≥ 3.
(The target is periodic, not constant as at d = 1, 2 — hence the (1 − v³)
denominator; it changes nothing structural below because H⁹ − u³ is a
power-series unit.)

**Step 1 — the family GF is a diagonal of G·H^n.** For k ≥ 3, n = 3k−2 ≥
2k+1 is in-onset, so P_k(3k−2) = [u^k] G H^(3k−2) directly by (A1). For
k = 0, 1, 2 both P_k(n) and [u^k]G H^n are polynomials in n of degree ≤ k
([u^k] of G(1+uĤ)^n involves only C(n,j), j ≤ k) agreeing at all n ≥ 2k+1,
hence at every integer n; these three below-onset values only fix the
polynomial part of the target, they carry no family content.

**Step 2 — Lagrange–Bürmann, formal, then reduced.** The inversion lemma
(`docs/proofs/grand-form.md` Step 5): for Φ, φ formal series with φ(0) a
unit, and u₀ the unique solution of u₀ = v·φ(u₀),

> Σ_{k≥0} v^k [u^k](Φ·φ^k) = Φ(u₀) / (1 − v·φ′(u₀)).

Apply over ℤ with the exact integer series Φ = G·H^(−2), φ = H³ (both
well-defined: H(0) = 1): since [u^k](G H^(−2) H^(3k)) = P_k(3k−2),

> S(v) = Φ(u₀)/(1 − v·φ′(u₀)), u₀ = v·H(u₀)³,

an identity in ℤ[[v]]. Reduce coefficientwise mod 81 — every operation on
the right (composition at u₀ ∈ vℤ[[v]], inversion of a unit) commutes with
reduction.

**Step 3 — parametrize by u.** Set v(u) := u/H(u)³ = u·(unit); u ↦ v(u) is
invertible over ℤ/81[[u]] (linear coefficient 1). By uniqueness of the
fixed point, u₀(v(u)) = u. Substituting, with φ′ = 3H²H′ and
v·φ′ = 3uH′/H:

> S(v(u)) = G·H^(−2) / (1 − 3uH′/H),

and since the substitution is invertible, the target identity in v is
EQUIVALENT to its image in u. Everything now lives on the curve.

**Step 4 — the mod-81 curve and implicit differentiation.** By (A2),
multiplying the master equation by the unit power H⁸:

> E81(H, u) = H⁹ − H⁸ − 25uH⁶ − 36u²H⁵ − 45u²H⁴ − 72u³H² − 27u⁴ ≡ 0 (mod 81)

as a series identity at H = H(u) — an algebraic consequence of the master
equation, valid at all orders (max k+ℓ = 8, so no negative exponents).
Differentiating a series that is ≡ 0 mod 81 term by term multiplies each
coefficient by an integer, so the congruence survives d/du:

> A·H′ ≡ B (mod 81), A := ∂E81/∂H, B := −∂E81/∂u.

This is the ONLY place H′ is converted to algebra, and it needs no division:
A is kept as a factor and cleared at the end (A(1,0) = 9−8 = 1, so A is a
series unit — the clearing is reversible).

**Step 5 — substitute G and cross-multiply.** By (A3), with
εp := H⁶·ε = H⁶ + 15uH⁴ + 27u²H³ + 27u²H² + 27u³ and
dp := H⁸·den = H⁸ + 50uH⁶ + 72u²H⁵ + 54u²H⁴ + 45u³H² + 54u⁴:

> G·H^(−2)/(1 − 3uH′/H) ≡ εp²·(AH − uB) / (H⁶·dp·(AH − 3uB)) (mod 81),

using A(1 − uH′/H) ≡ (AH − uB)/H and A(1 − 3uH′/H) ≡ (AH − 3uB)/H from
Step 4. The target side, at v = u/H³, over the common denominator
H⁶(H⁹ − u³):

> Mnum := (c₀H⁶ + c₁uH³ + c₂u²)(H⁹ − u³) + 27(2u³H⁶ + u⁵).

Units inventory (constant terms, each invertible in ℤ/81[[u]]): H → 1,
A → 1, dp → 1, AH − 3uB → 1, H⁹ − u³ → 1. So the identity is equivalent to
the vanishing of

> N(H, u) := εp²·(AH − uB)·(H⁹ − u³) − Mnum·dp·(AH − 3uB)

at H = H(u), mod 81.

**Step 6 — the division certificate.** E81 is MONIC of degree 9 in H, so
exact division in ℚ[u][H] decides membership: N = q·E81 + r with
deg_H r ≤ 8, and the verifier asserts **every coefficient of r is an integer
divisible by 81** (N has deg_H 32; sympy `div` over QQ[u], the
`deficit2_proof.py` route unchanged). Hence

> N(H(u), u) = q(H(u), u)·E81(H(u), u) + r(H(u), u) ≡ 0 + 0 (mod 81),

and dividing back by the listed units gives S(v) ≡ the target, coefficient
by coefficient. Reading off [v^k], k ≥ 3, proves the theorem. ∎

Note the certificate's direction: r ≡ 0 is SUFFICIENT and is what a proof
needs. (Had r not vanished, that alone would not have refuted the identity —
the ideal of relations of H mod 81 is larger than (E81); the fallback
reduction against the tower ladder 3·E27, 9·E9, 27·E3 was mapped out but
never needed. Same first-try outcome as deficit-2.)

## Numerics as guards on derived steps (never as the result)

Each derived step is independently checked to series order 122 mod 81 in the
verifier, so a transcription error in any step would have been caught before
the certificate ran:

- E81(H, u) ≡ 0 and A·H′ ≡ B as series (Step 4);
- the Step 3 identity S(v(u)) ≡ G H^(−2)/(1 − 3uH′/H) by explicit
  composition (this also confirms the LB kernel is Φ = G·H^(−2) — the
  handoff's flagged sign change from deficit-2's G·H², which came from that
  proof's index shift m = k−1, is verified right);
- N(H, u) ≡ 0 as a series, before the symbolic division;
- the target coefficients: [v^k]S equals c₀, c₁, c₂ then the 27·(2,0,1)
  cycle for every k ≤ 122, and equals the exact banked P_k(3k−2) for
  k = 3..17.

## Where the d = 1, 2 structure was assumed to transfer — audited

1. **The G-formula shape (no correction term at mod 81).** Consumed as (A3)
   from agent 1; not re-derived here. This is the transfer point with real
   exposure — see weakest links.
2. **The LB kernel.** NOT assumed: derived for this family in Step 2 and
   numerically confirmed (exponent −2, not +2).
3. **Constant vs periodic target.** The (1 − v³) denominator is new at
   d = 3; it enters the certificate only through the unit H⁹ − u³ and adds
   nothing to the difficulty. No transfer assumption needed.
4. **Monicity of the curve.** Re-checked, not assumed: E81 is monic of
   degree 9 because the maximal surviving k+ℓ is 8 (four-pair stack); the
   division route requires exactly this.

## Weakest links, self-flagged

- **(W1) = (A3) at orders k ≥ 18.** The boundary residue formula mod 81 is
  derived within the gas formalism but machine-verified only against the
  banked g_k, k ≤ 17. If it failed at some higher order, the theorem would
  inherit the failure at exactly those k. This is the same exposure the
  proved d = 1, 2 results carry at mod 27 (deficit-2 consumed G mod 27 the
  same way); nothing in this file enlarges it, but nothing shrinks it
  either. An adversary should press here first.
- **(W2) = (A2) likewise**, with the mitigation that the master equation has
  a completeness proof from the row bound (agent 1's file), so its exposure
  is the renewal formalism itself, not the survivor list.
- **(W3)** The all-integer-n extension of P_k(n) = [u^k]G H^n (Step 1) is
  used only for the three below-onset constants c₀, c₁, c₂, which sit
  outside the theorem's k ≥ 3 range; a reader who rejects the extension can
  simply define the target's polynomial part by those three series
  coefficients and lose nothing.

## The family against the banked triangle (provenance rule)

Provenance quoted from `triangle.py provenance(n,H)` per cell (verifier
section 7); residues are the banked T mod 3 vs the theorem's prediction —
all 12 agree (banked in round 1; re-asserted, not newly claimed):

| k | (n,H) | T mod 3 | predicted | provenance |
|---|---|---|---|---|
| 3 | (7,4) | 2 | 2 | real-sweep |
| 4 | (10,6) | 0 | 0 | real-sweep |
| 5 | (13,8) | 1 | 1 | real-sweep |
| 6 | (16,10) | 2 | 2 | real-sweep |
| 7 | (19,12) | 0 | 0 | real-sweep |
| 8 | (22,14) | 1 | 1 | real-sweep |
| 9 | (25,16) | 2 | 2 | real-sweep |
| 10 | (28,18) | 0 | 0 | real-sweep |
| 11 | (31,20) | 1 | 1 | real-sweep |
| 12 | (34,22) | 2 | 2 | closed-form-Pk |
| 13 | (37,24) | 0 | 0 | closed-form-Pk |
| 14 | (40,26) | 1 | 1 | closed-form-Pk |

## Cost of this step (for the go/no-go ledger)

One desk session; the certificate ran green on the first attempt and the
whole verifier takes ~1 s. Relative to deficit-2 the object grew mildly
(deg_H N: 21 → 32; divisor degree 7 → 9) and the method changed nowhere.
Combined with agent 1's census (mod 243 and 729 need zero new weights),
d = 4 and d = 5 look like the same one-session exercise each; the periodic
target caused no new difficulty, so period-length growth at higher d should
not either. The method's cost so far is dominated entirely by the tower
level, not the proof step.

## Novelty

`git log --all --oneline --name-only -- 'results/*.md' 'docs/**/*.md'`
swept; off-branch hits inspected. Prior art: the deficit-2 proof
(`34e3476`, `experiments/deficit2_proof.py` — the method), the numeric
mod-81 master equation (`c95ebc0`, `experiments/spine_deeper.py` — credited
in agent 1's file), and agent 1's uncommitted tower derivation (this
round). No proof of any d ≥ 3 unit formula exists on any branch; round 1's
synthesis lists d = 3..7 as open and names this statement its sharpest
target.
