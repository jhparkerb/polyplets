# Adversary audit of the d=3 proof: no gap found

> Some files cited below were filed on the unmerged branch `triangle-structure` and never reached this one: `git show triangle-structure:<path>`.

**Bits against enumeration error: 0 new. Bits against formula-chain error:
0 new** — this file re-verifies and probes; every cell it touches (the nine
real-sweep d=3 family cells, k = 3..11) was banked in round 1.

2026-08-11. Round-2 agent 3 (adversary), per
`docs/triangle-structure-round2-brief.md` §Team shape. Default verdict was
"the proof has a gap"; the audit did not find one. Verifier:
`experiments/tristruct/r2_adversary_d3.py` — independent code paths
throughout (own series toolkit, own valuation filter, own monic-reduction
certificate over (ℤ/81)[u][H] with no sympy, exact-integer valuation checks,
and a 9-corruption sensitivity battery). All checks pass in ~1 s. Both
agents' scripts also re-run clean.

**VERDICT: the theorem stands.** For all k ≥ 3, P_k(3k−2) ≡ 27·r_k (mod 81)
with r_k cycling (2,0,1) from k = 3; hence v₃(P_k(3k−2)) > 3 ⟺ k ≡ 1 (mod 3),
with exact valuation 3 and unit residues 2/1 elsewhere. The conditional frame
is exactly (A1)–(A4) as agent 2 states it — and finding 1 below argues the
frame is REDUCIBLE: (A2)/(A3) follow at all orders from already-proved
theorems plus (A4), so the true exposure is smaller than the proof file
claims, not larger.

## Step-by-step verdicts

| step | claim | verdict |
|---|---|---|
| A1 | diagonal law + grand form, P_k(n) = [u^k]G·H^n for n ≥ 2k+1 | CONFIRMED (proved elsewhere, Lean-checked; not re-opened) |
| A2 | H mod 81 satisfies the master equation at all orders | CONFIRMED, and upgradable — see finding 1 |
| A3 | G ≡ ε_bε_t(1−uH′/H)/den (mod 81) at all orders | CONFIRMED, and upgradable — see finding 1 |
| A4 | the 11 surviving weight entries | CONFIRMED with one caveat — see finding 2 |
| tower completeness | interior k ≤ 4 / boundary k ≤ 3 exhaust the survivors | CONFIRMED — re-proved weight-independently: per composition through k = 8, v₃(Ŵ) ≥ 2k−ℓ−1 ≥ 4 for every interior type with k ≥ 5 and v₃(B̂) ≥ 2k−ℓ ≥ 4 for every boundary type with k ≥ 4 (then monotone in k); `KNOWN_WEIGHTS` verified to contain all 31 compositions k ≤ 5. No cluster class can have been wrongly excluded regardless of its (integer ≥ 0) weight value. Survivor coefficients re-filtered independently; match both md files exactly |
| Step 1 | family GF = diagonal of G·H^n; k = 0,1,2 by polynomial extension | CONFIRMED — [u^k]G(1+uĤ)^n involves only C(n,j), j ≤ k, so both sides are degree-≤k polynomials in n agreeing at infinitely many in-onset points; equality at all integers follows unconditionally. c₀,c₁,c₂ = 1, 61, 1 re-derived exactly (P₁(1) = −20, P₂(4) = 649). W3's fallback framing is correct but not needed |
| Step 2 | Lagrange–Bürmann over ℤ, reduced mod 81 | CONFIRMED — Φ = G·H⁻² and φ = H³ are genuinely integer series (P_k(0), P_k(1) ∈ ℤ pin G, GH, hence H, integral); the lemma's ℚ[[v]] identity between elements of ℤ[[v]] reduces coefficientwise; 1−vφ′(u₀) has constant term 1 |
| Step 3 | parametrize by u; equivalence of the v- and u-identities | CONFIRMED — v(u) = u·(unit) has linear coefficient 1, composition is injective on (ℤ/81)[[v]]; identity re-verified with own composition code to order 140 |
| Step 4 | E81 vanishes; A·H′ ≡ B by implicit differentiation | CONFIRMED — d/du of a series in 81ℤ[[u]] stays in 81ℤ[[u]] (coefficientwise integer multiplication); no division by A occurs; A(1,0) = 1 verified. The top-coefficient caveat on H′ is handled correctly in BOTH scripts: Hd[KX] enters every identity u-shifted except the impl-diff guard, which is range-limited to KX−1. No step silently uses the inexact coefficient |
| Step 5 | cross-multiplied form; units inventory | CONFIRMED — the manipulation X/Y ≡ (AH−uB)/(AH−3uB) follows by multiplying the two congruences A·X·H ≡ AH−uB and A·Y·H ≡ AH−3uB and dividing by units; all seven claimed units (H, A, dp, den, AH−3uB, H⁹−u³, fac3) have constant term 1 mod 81, checked. The (1−v³) denominator enters only as H⁹−u³ = 1 + O(u) at series level — a unit in (ℤ/81)[[u]]; the polynomial ring never divides by it. Mnum re-derived from the target independently, matches |
| Step 6 | division certificate | CONFIRMED — reproved with an independent monic-reduction routine over (ℤ/81)[u][H] (legitimate: E81 monic ⇒ ℤ[u][H] division exact and commuting with mod-81 reduction): remainder identically zero. Sufficiency direction is sound: r ≡ 0 ⇒ N ≡ 0 on the curve ⇒ identity after dividing back the listed units. The certificate proving nothing on failure is a completeness worry, not a soundness one — the logic closes |
| exactness of v₃ | v₃ = 3 exactly at k ≢ 1 | CONFIRMED exactly (not mod 81): banked P_k(3k−2) computed as integers, k = 3..17: v₃ = 3 with residues (2,·,1) at k ≢ 1 (mod 3), v₃ = 7, 4, 4, 5, 4 at k = 4, 7, 10, 13, 16. Also 27·T(3k−2, 2k−2) = P_k(3k−2) as INTEGERS on all nine real-sweep cells, provenance quoted from `triangle.py` |
| LB kernel sign | Φ = G·H⁻² vs deficit-2's G·H² | CONFIRMED for THIS proof directly (composition identity S(v(u)) = GH⁻²/(1−3uH′/H) holds to order 140 with own code). The deficit-2 comparison is expository — that proof used the shifted index m = k−1 and a different LB variant; nothing here depends on it |

## Findings, ranked

**1. (UPGRADE, contradicts the proof file's self-assessment in the good
direction.) The (A2)/(A3) "machine-verified only k ≤ 17" exposure is
closable: both are all-orders consequences of already-proved theorems.**
Agent 2 claims (W1) "the same exposure d = 1,2 carry, neither enlarged nor
shrunk". Tested; the exposure is in fact shrinkable to (A4). Derivation
(checked by hand in this audit, consistent with every finite-order machine
check to order 140):

- *Master equation.* `grand-form.md` Step 1 constructs z*(y) with
  1 − S(y, z*) = 0 identically; Step 2 of `diagonal-law.md` (proved
  combinatorics) identifies S's coefficients as the cluster weights. With
  μ = 1/z* this is μ = 3 + Σ_c W_c y^{k_c} μ^{−ℓ_c} at all orders.
  `grand-form.md` Step 5 defines H(u) = M(27u)/3, M = μ∘ŵ, with
  27u = w·μ(w) at w = ŵ(27u); substituting converts each term
  W y^k μ^{−ℓ} into Ŵ u^k H^{−(k+ℓ)} with Ŵ = W·3^{2k−ℓ−1} exactly. So
  H = 1 + Σ_c Ŵ_c u^{k_c} H^{−(k_c+ℓ_c)} is an identity in ℤ[[u]] at ALL
  orders, and the mod-81 finite equation follows from the (weight-value-free,
  k ≥ 5) valuation kill — E81(H(u), u) ∈ 81ℤ[[u]] is a theorem given (A4).
- *Boundary residue formula.* G(u) = 3K(27u) with
  K = C(ŵ)/(1 − yφ′(ŵ)), φ = μ⁻¹ (proved, Step 5). Two exact conversions:
  (i) 1 − yφ′(ŵ) = (μ + wμ′)/μ and 1 − uH′/H = μ/(μ + wμ′) — reciprocals;
  (ii) C = μ·E_b(z*)E_t(z*)/S_z(y, z*) (from u_cofactor(y, z*) = S_z(y, z*),
  got by differentiating 1 − S = (z*−z)·u_cof at z = z*), and at z* = 1/μ
  the E-terms and S_z/3 convert termwise into ε_b/μ, ε_t, den with the
  exact B̂ = W^b·3^{2k−ℓ} and (ℓ+1)Ŵ normalizations. Hence
  G = ε_bε_t(1−uH′/H)/den in ℤ[[u]] at ALL orders — the "no correction term"
  shape is forced, not observed.

Consequence: the theorem's frame reduces to (A1) + chain identity (both
proved, Lean/machine-checked) + (A4). Recommend banking this derivation as
its own note (it retro-upgrades d = 1, 2 as well). Until it is written up
and reviewed, the proof file's more conservative framing stays technically
correct; nothing in the theorem waits on it.

**2. (CAVEAT, low severity, named single point.) W(2,2,2,2) = 68314 is the
one surviving weight with no direct-enumeration cross-check.** It is the
only object new at the mod-81 level; only its mod-3 digit (= 1) enters
(as 27u⁴ in E81 and 54u⁴ in den). `cluster_weight_dp.py`'s `validate()`
covers k ≤ 3 against direct enumeration; `defect-gas.md`'s "enumeration
needed hours" for this cell does not record a completed enumeration. The
certificate provably consumes the digit: forcing it to 0 or 2 breaks the
division (sensitivity battery, both directions). A one-off direct
enumeration of the (2,2,2,2) stack (hours) would close the last
non-enumerative link in (A4). The other eight distinct surviving weights
(25, 49, 339, 4778; 5, 7, 66, 919) all have independent enumeration checks.

**3. (SENSITIVITY, positive.) The certificate is not vacuous.** Nine
deliberate corruptions each produce a nonzero remainder: permuted and
rotated target cycles, a wrong below-onset constant, one corrupted weight
in each of dp / εp / E81, the mod-27 curve promoted verbatim, and both
wrong mod-3 digits of W(2,2,2,2). Per brief rule 4 this is the right
instrument here — the certificate is a polynomial identity, not a
cell congruence, so perturbation measures real teeth.

**4. (BOOKKEEPING, minor.)** (i) Both files carry the two bit-counts and
name their conditionality; agent 2's sit in the second paragraph rather
than literally the first line — content complete, placement slightly off
the brief's letter. (ii) Provenance is quoted from `triangle.py
provenance(n,H)` per cell, and the 12-row table obeys the H-rule (k ≤ 11
real-sweep at H ≤ 20; k = 12..14 closed-form-Pk at H = 22..26); re-verified
here including integer-level 27·T = P_k(3k−2) on the real-sweep cells.
(iii) Novelty: re-swept `git log --all --oneline --name-only` over
results/docs md independently; prior art is exactly what the files credit
(`34e3476` deficit-2 proof, `c95ebc0` numeric mod-81 equation in
`spine_deeper.py`); no d ≥ 3 proof exists on any branch. (iv) Agent 1's
"~54 new formula-chain bits" is fairly stated as correlated-not-additive
with the banked mod-27 checks.

## What the theorem is conditional on, precisely

- (A1): diagonal-law shape theorem + grand form — proved, Lean-checked,
  standard axioms.
- The chain identity F = E_b(1−S)⁻¹E_t + P with weight identification —
  proved (`diagonal-law.md` Steps 1–2), machine-verified 40/40.
- (A4): the 11 surviving weight entries (9 distinct integers) from the
  banked DP; all but W(2,2,2,2) also enumeration-checked (finding 2).
- (A2)/(A3) as stated add no exposure beyond the above once finding 1 is
  banked; as the files stand, they carry the "derived in the gas formalism,
  machine-verified k ≤ 17" framing.

Enumeration-error teeth of the theorem itself: unchanged from round 1 —
the nine real-sweep family cells (≈ 9·log₂3 ≈ 14 bits, conditional on the
formula chain), plus zero on any cell with k ≥ 12. The proof adds no new
enumeration coverage and claims none.

## Extension-scout recommendation

Go. The method survived a hostile audit at d = 3 with margin; agent 1's
census (free through d = 5, cheap through d = 7, exponential after) was not
part of the theorem and was only spot-checked here, but nothing in it is
contradicted by anything found. The scout should carry finding 2's shape
with it: at each new level, the newly-entering weights' mod-3^j digits are
the entire exposure, and DP-only digits should be flagged per level.
