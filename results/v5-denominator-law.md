# The v5 denominator law: c_k = v5(k!) − H(k), proved via the 5-adic order of Λ − 1

2026-07-31. Resolves the open question of `results/converse-sweep.md` §2
("prove c_k = ⌈v₅(k!)/2⌉ — or the corrected law — via the 5-adic structure
of G, and explain k = 11"). Outcome: **⌈v₅(k!)/2⌉ was the wrong law** — a
numerological fit that happens to agree with the true law on the window
k ≤ 20 except at k ∈ {1, 11} — and **k = 11 is not an exception to
anything**: the corrected law holds there exceptionlessly. Probe:
`experiments/v5_denominator.py` (<5 s, exact arithmetic on
`polyplets/pin-data.md` + real-swept cells; no enumeration).

## Statement

Write ĉ_k := min_i v₅([nⁱ] k!·P_k) (minimum 5-adic valuation over the
k!-basis numerator coefficients — uncapped; see "bookkeeping" below for the
relation to the minimal denominator D_k). Define the **harvest**

> H(k) := max { Σ_t v₅(m_t!) − 2·m₁ − 𝟙[j_G = 1] :
>               j_G + Σ_{t≥1} t·m_t = k,  j_G, m_t ≥ 0 },

whose closed form (Lemma C) is, for ALL k ≥ 0 in one expression
(2026-07-31, second pass — jasonp asked whether the original even/odd
case-split was a simpler expression in disguise; it is):

> **H(k) = v₅(⌊k/2⌋!) − [k ≡ 1 (mod 10)]**.

(The intermediate case-split form — H even = v₅((k/2)!), H odd =
max(v₅(((k−3)/2)!), v₅(((k−1)/2)!) − 1), H(1) = −1 — collapses via
max(v₅(m!) − v₅(m), v₅(m!) − 1) = v₅(m!) − min(v₅(m), 1) and, for odd k,
5 | ⌊k/2⌋ ⟺ k ≡ 1 (mod 10); k = 0, 1 absorb into the same expression.
Verified ≡ the case-split for k ≤ 5000 and ≡ the brute-force partition
optimum for k ≤ 45.) Since k! = 2^⌊k/2⌋·⌊k/2⌋!·(odd numbers ≤ k), the law
has the equivalent **odd-double-factorial form**

> **ĉ_k = v₅( Π_{j ≤ k, j odd} j ) + [k ≡ 1 (mod 10)]** :

the order-2 Newton slots eat exactly the even half of k!'s 5-content; the
numerator floor is the odd half, plus the g₁ tax on one residue class.

**THEOREM (lower bound, proved below).** ĉ_k ≥ v₅(k!) − H(k) for every
k ≥ 1. Equivalently v₅(D_k) ≤ max(H(k), 0): the 5-part of the minimal
denominator of P_k divides the 5-part of ⌊k/2⌋! (with the odd-k refinement).

**Equality** holds at every measured level: k = 1..18 from the production
polynomials (`polyplets/pin-data.md`), and k = 19 as a genuine
out-of-sample confirmation (P₁₉ derived from the two real-swept cells
T(39,20), T(40,21) after the law was fixed; predicted ĉ₁₉ = 2, measured 2).
Equality in general (non-cancellation of the extremal terms) is not proved;
it is a mod-5^{ĉ+1} statement about the boundary coefficients, exact and
checkable per k.

## The mechanism in one line

5-adically, the boundary series **Λ − 1 vanishes to order 2**: its linear
coefficient is u₁ = 25 ≡ 0 (mod 5²), so in the Newton expansion
P_k(n) = Σ_m C(n,m)·[y^k](G·u^m) the binomial slots with m > ⌊k/2⌋ are
5-adically suppressed, and the denominator's 5-part collapses from v₅(k!)
to v₅(⌊k/2⌋!). The odd-k leftover cell can only be paid by an order-1
coefficient — u₁ = 25 (tax 2) or g₁ = −45 (tax 1) — which is the entire
k = 11 story.

## Proof of the lower bound

Inputs, all previously proved:

- (I1) P_k(n) ∈ ℤ for **every** integer n (`docs/proofs/diagonal-law.md`
  Step 6).
- (I2) Grand form: Σ_k P_k(n) y^k = G(y)·Λ(y)^n with
  G = exp(Σ a_j y^j), Λ = exp(Σ b_j y^j) (`docs/proofs/grand-form.md`),
  valid at order y^k for n ≥ 2k+1 — hence, both sides being polynomials in
  n of degree ≤ k (shape theorem; [y^k] G·exp(n log Λ) is a degree-≤ k
  polynomial in n), valid as a polynomial identity in n per y-order.
- (I3) P₁(n) = 25n − 45 (`docs/proofs/T-n-nm1.md`).

**Lemma A (integrality of the boundary series).** G ∈ 1 + yℤ[[y]] and
Λ ∈ 1 + yℤ[[y]]; writing u := Λ − 1 ∈ yℤ[[y]]:
u₁ = 25, g₁ = −45, and all other coefficients of u and G are (5-adic)
integers.

*Proof.* g_k = P_k(0) ∈ ℤ by I1, g₀ = P₀(0) = 1, so G is a unit of ℤ[[y]].
By I2 at n = 1, G·Λ = Σ_k P_k(1) y^k ∈ ℤ[[y]], so Λ = G^{−1}·Σ P_k(1)y^k
∈ ℤ[[y]] with Λ(0) = 1. Finally u₁ = [y](GΛ) − g₁ = P₁(1) − P₁(0) =
(−20) − (−45) = 25 and g₁ = P₁(0) = −45 by I3. ∎

**Lemma B (Newton form).** P_k(n) = Σ_{m=0}^{k} C(n,m)·A_{k,m} with
A_{k,m} := [y^k](G·u^m) = Δ^m P_k(0) ∈ ℤ.

*Proof.* For integer n ≥ 0, Λ^n = (1+u)^n = Σ_m C(n,m) u^m exactly
(y-adically finite per order; ord_y u^m ≥ m kills m > k at order k), so
[y^k] gives Σ_k-identity at every n ≥ 0; both sides are polynomials in n,
hence identical. A_{k,m} = Δ^m P_k(0) (finite differences of I2 at
n = 0..m), an integer by I1. ∎

**Theorem.** For every k ≥ 1 and 0 ≤ i ≤ k,
v₅([nⁱ] k!·P_k) ≥ v₅(k!) − H(k).

*Proof.* k!·C(n,m) = (k!/m!)·(n)_m and (n)_m = Σ_i s(m,i) nⁱ with integer
Stirling numbers. Expanding u^m by the multinomial theorem over
configurations (m_t)_{t≥1}, Σ m_t = m, and G over its single slot j_G:

> [nⁱ] k!·P_k = Σ_{j_G + Σ t·m_t = k} ( k! / Π_t m_t! ) · s(Σm_t, i)
>               · g_{j_G} · Π_t u_t^{m_t}.

v₅ is a valuation, so each summand has

> v₅ ≥ ( v₅(k!) − Σ_t v₅(m_t!) ) + 2m₁ + 𝟙[j_G = 1]
>    ≥ v₅(k!) − H(k),

using Lemma A: v₅(u₁^{m₁}) = 2m₁, v₅(g₁) = 1, every other u_t, g_{j_G}
5-integral. ∎

**Lemma C (closed form of H).** As stated above.

*Proof.* (i) m₁-elimination: moving the m₁ order-1 cells into
j_G′ = j_G + m₁ changes the payoff by −v₅(m₁!) + 2m₁ − 1 > 0 (as
v₅(m!) ≤ (m−1)/4), so WLOG m₁ = 0. (ii) All-2s optimality: v₅(m!) is
monotone and superadditive (v₅((a+b)!) ≥ v₅(a!) + v₅(b!), binomial
integrality), so any multiset of parts t ≥ 2 with multiplicities m_t is
dominated by parts of size 2 with multiplicity Σ_t ⌊t·m_t/2⌋ ≥ Σ_t m_t.
(iii) The leftover: even k takes j_G = 0, m₂ = k/2; odd k either pays the
g₁ tax (j_G = 1, m₂ = (k−1)/2, payoff −1) or parks the parity in a free
order-≥2 slot (one part 3, or j_G = 3: m₂ = (k−3)/2); larger j_G is
dominated by monotonicity. (iv) Collapse to the single expression: with
m = ⌊k/2⌋, the odd-k optimum is max(v₅((m−1)!), v₅(m!) − 1) =
v₅(m!) − min(v₅(m), 1) = v₅(m!) − [5 | m], and for odd k, 5 | m ⟺
k ≡ 1 (mod 10); even k is never docked (no leftover), and k = 0, 1 read
off directly. ∎

## Why k = 11 (and why "lone")

Harvesting one factor of 5 against k! requires **five identical Λ-slots of
order ≥ 2** — cost ≥ 10 cells. k = 10 is the first k that affords it
(m₂ = 5). At k = 11 exactly one cell is left over, and every order-1
object is taxed at least as much as the harvest pays: g₁ = −45 costs 1
(cancelling the 5 exactly: H(11) = max(v₅(4!), v₅(5!) − 1) = 0), u₁ = 25
costs 2. From k = 12 the leftover parks in a free order-2 slot. So
ĉ₁₁ = v₅(11!) − 0 = 2, exceptionlessly.

k = 11 looked "lone" only because the data window ended at 18: in the
one-line form of H, the "exception" is exactly the Iverson bracket — the
dock lands on the entire residue class k ≡ 1 (mod 10), of which 11 is
just the first member past onset. The fit ⌈v₅(k!)/2⌉ diverges from the
true law at k ∈ {1, 11, 21, 25, 26, 27, 28, 29, 31, 35, ...} (k ≤ 40;
script prints the set to 120 — the 25, 26, ... entries are ⌊k/2⌋!-vs-half
drift, not the bracket). First unmeasured divergence: **ĉ₂₁ = 4 − 1 = 3** where
the old fit says 2 — a sharp falsifiable prediction, but it needs P₂₀/P₂₁,
i.e. triangle rows n ≥ 41 (beyond project close) or an ab initio cluster
weight sweep to surplus 21.

## Measured confirmation (all from `experiments/v5_denominator.py`)

| k | 1 | 2–4 | 5–9 | 10 | 11 | 12–14 | 15–18 | 19 |
|---|---|---|---|---|---|---|---|---|
| v₅(k!) | 0 | 0 | 1 | 2 | 2 | 2 | 3 | 3 |
| H(k) | −1 | 0 | 0 | 1 | **0** | 1 | 1 | 1 |
| ĉ_k = v₅(k!) − H(k), predicted | 1 | 0 | 1 | 1 | **2** | 1 | 2 | 2 |
| ĉ_k measured | 1 | 0 | 1 | 1 | 2 | 1 | 2 | 2 (out-of-sample) |

Consistency outputs, same script: G and Λ are integer series to order 18
(Lemma A verified numerically on top of its proof); the derived
grand-form constants show v₅(a₁₀) = v₅(b₁₀) = v₅(b₁₅) = −1 — the
log-of-integral-series denominators the theorem predicts (v₅(b_j) ≥
−⌊log₅ j⌋ from log(1+u), first reachable at j = 10 because u₁ = 25 blocks
j ≤ 9) — and P₁..P₁₈ re-derived from real-swept cells agree with
`pin-data.md` coefficient-for-coefficient.

## Bookkeeping: ĉ_k vs the minimal denominator

D_k = k!/5^{min(ĉ_k, v₅(k!))} — the denominator cannot drop below 1, so
the k = 1 row (ĉ₁ = 1 > 0 = v₅(1!)) caps to D₁ = 1. The
`results/converse-sweep.md` §2 table "c_k = 0 (k ≤ 4)" is the capped
quantity; the uncapped numerator minimum at k = 1 is 1 (coefficients
25, −45), and it is the uncapped ĉ that obeys the clean law — the k = 1
"tax" H(1) = −1 is real, not an artifact. For k ≥ 2, v₅(D_k) = H(k) at
every measured level: **the 5-part of the true denominator of P_k is that
of ⌊k/2⌋!, docked one 5 exactly when k ≡ 1 (mod 10)**.

## Second pass: profile structure (2026-07-31, same day)

Prompted by the H collapse, a sweep for further simplifications over the
full valuation profiles (all coefficients, not just the floor; probe
extended, k ≤ 19 with P₁₉ from the real-swept two-point pin):

- **Upper-half law, EXACT.** For every i ≥ ⌈k/2⌉ and every k ≤ 19:

  > v₅([nⁱ] k!·P_k) = 2(2i−k) + v₅( k! / ((2i−k)!·(k−i)!) ).

  The "ramp descending ~3–4 per degree" of the first measurement is pure
  multinomial arithmetic: the minimal-slot configuration (m = i slots:
  2i−k order-1 slots at u₁ = 25, k−i order-2 slots, Stirling s(i,i) = 1)
  is unique at minimal valuation and carries everything. Zero mismatches
  at all 115 upper-half coefficients; Lean `upper_half_law` (kernel
  decide, k ≤ 18). Large-k persistence needs the same care as the
  bracket (25 | m₂(m₂−1) swaps first bite around m₂ ≈ 25).
- **i = 0 column, exact and trivial once seen.** [n⁰] k!·P_k = k!·g_k is
  a single term: v₅ = v₅(k!) + v₅(g_k). The primitive is the g-table.
- **The exact u/g valuation tables (t ≤ 19).** v₅(u_t): 2 at t = 1,
  **3 at t = 17**, else 0. v₅(g_t): 1 at t ∈ {1, 3, 4, 7, 12, 17}, else
  0. No law found for these supports (the tempting "t ≡ 2 (mod 5)" for
  {7, 12, 17} is support-only — g₂ ≡ 2 (mod 5) breaks it as a value
  pattern).
- **The residual: 23 genuine cancellation points.** After the i = 0 and
  upper-half laws, 23 mid-band coefficients (k ≤ 19) sit strictly above
  the config bound — and feeding the bound the EXACT u/g tables changes
  nothing (the crude ≥0 bound and the exact-table bound coincide at all
  of them): they are cross-config cancellations in the extremal sum, not
  richer coefficient divisibility. All are +1 except (k,i) = (18,6) and
  (19,6) at +2. The full profile is therefore NOT config-forced; the
  floor law survives because cancellation only ever adds 5s.
- **Mod-5 spine: NEGATIVE.** Unlike the mod-3 ternary spine (W³ = W²+t),
  G and Λ mod 5 show no periodicity (no period ≤ 9 from any start ≤ 9,
  also mod 25) and no quadratic algebraic relation A·S² + B·S + C ≡ 0
  with deg ≤ 5 polynomial coefficients (full rank, nullity 0, at every
  tested degree over the 20-term window). Data-capped at t ≤ 19; recorded
  so nobody re-hunts it on this window.

## Status

- Lower bound (ĉ_k ≥ v₅(k!) − H(k)): **proved**, from I1 + I2 + I3 only.
- **Lean (2026-07-31, `polyplets/Polyplets/V5Denominator.lean`)**: the law
  at every pinned level k = 1..18 (`v5_law_all`), the refutation of the
  old ⌈v₅(k!)/2⌉ fit at k = 11 (`ceil_fit_refuted`), the k = 11 multiset
  obstruction as a general theorem (`eleven_no_harvest`), and the taxed
  seeds u₁ = 25, g₁ = −45 tied to the pinned P₁ (`u1_seed`, `g1_seed`) —
  all kernel `decide`/proof, standard axioms, no native_decide; the
  numerator lists are certified identical to `Pin.lean`'s production data
  by `rfl` tie lemmas. The general-k lower bound remains paper-level
  (open item in `polyplets/PROOF-STATUS.md`).
- Equality: exact at k = 1..19 (k = 19 out-of-sample); open in general —
  needs non-vanishing of the extremal multinomial sum mod 5^{ĉ_k+1}
  (finite check per k, e.g. u₂ mod 5 drives the even-k floor).
- The old open question "which coefficient binds the 5-adic content" is
  answered structurally: the binding coefficients are those reachable by
  the optimal harvest configurations (five-fold order-2 Λ-slots), which is
  why the measured valuation profiles show a flat floor across all low
  degrees.
