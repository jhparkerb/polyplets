# Arithmetic structure of the height triangle

The height triangle T(n,H) counts fixed king animals of n cells whose
bounding box has height H; its values for n ≤ 40 are in `results/triangle.txt`.
This file holds the triangle's arithmetic: its structure at the prime 3,
where all of its integer content lives; a parity theorem at the prime 2; the
5-adic denominators of the diagonal polynomials; and the rank of the strip
transfer matrix over finite fields, which bounds every linear method for the
mod-2 bit. The Smith normal form being all 3-powers, the parity theorem, the
characteristic-landscape theorems and the 5-adic lower bound are
unconditional; the mod-3 theorems rest on the proved diagonal formula plus
congruences derived from the cluster expansion and checked against data to
k = 17; everything else is measured and marked so. Full proofs of Theorems 1
to 6 are in `paper/L1-diagonal-law.tex`, Part II.

## Definitions

**The diagonal formula** (`docs/proofs/diagonal-law.md`, proved): for each
k ≥ 0 there is an integer-valued polynomial P_k of degree ≤ k with

    T(n, n−k) = P_k(n) · 3^(n−1−3k)   for all n ≥ 2k+1.

The bound n = 2k+1 is the formula's onset; "in range" means n ≥ 2k+1. The
fitted P_k for k ≤ 17 are in `polyplets/pin-data.md` (k ≤ 3 also derived from
cluster weights); P_19 was derived from the enumerated entries T(39,20) and
T(40,21).

**The product form** (`docs/proofs/grand-form.md`, proved): series
G, Λ ∈ ℚ[[y]] with G(0) = Λ(0) = 1 and Σ_k P_k(n) y^k = G(y) Λ(y)^n, valid at
order y^k for n ≥ 2k+1. Λ is the per-row transfer series of the cluster
expansion (`results/diagonal-formula.md`); the paper and the mod-3 scripts
write it H. Its master equation is Λ = 1 + Σ_c Ŵ_c u^{k_c} Λ^{−(k_c+ℓ_c)} over
cluster types c of surplus k_c and length ℓ_c, with k_c ≥ ℓ_c.

**Deficit.** An in-range entry T(n, n−k) has deficit d := 3k+1−n, and
v₃(P_k(n)) = v₃(T(n,n−k)) + d. The **spine** of column H is its entry at
n = ⌊3H/2⌋. The **sleeve** of row n is its set of in-range entries left of
the spine, k from ⌊(n−1)/3⌋+1 to ⌊(n−1)/2⌋.

**Provenance.** "Enumerated" means computed by the transfer-matrix engine
rather than composed from P_k; `results/provenance-table.md` says which.

## The prime 3

### Integrality, and the two series

**Proposition 1 (Pólya).** Each P_k is integer-valued, hence 3-integral. On
the k+1 consecutive integers of [2k+1, 3k+1], P_k(n) = T(n,n−k)·3^(3k+1−n)
is a count times a nonnegative power of 3, and a degree-k polynomial integral
at k+1 consecutive integers is integer-valued everywhere. The leading
coefficient is 25^k/k!. Checked P_k(n) ∈ ℤ for n ∈ [−5, 40], k ≤ 15.

**Proposition 2.** G = Σ_k P_k(0) y^k and Λ = (Σ_k P_k(1) y^k)/G are integer
power series with constant term 1. Λ begins 1, 25, 208, 1483, 20688, 130208;
the 25 is the pair weight, the single-defect species of one row. Λ has not
been looked up in the OEIS.

### Three congruences

Let W ∈ 𝔽₃[[t]] be the unique root with W(0) = 1 of the spine cubic

    W³ = W² + t,

parametrized by t = x/(1−x)³, W = 1/(1−x).

- (⋆a) G ≡ 1 (mod 9): from the boundary-cluster residue formula, a valuation
  lemma on boundary weights, and one identity of the mod-9 cubic
  (`results/diagonal-formula.md`). Checked v₃(G_j) ≥ 2 for j ≤ 17.
- (⋆b) Λ ≡ W (mod 3) at all orders: k_c ≥ ℓ_c for every cluster, so the
  valuation lemma leaves only the bare two-cell row modulo 3, whose chains
  give Λ³ = Λ² + u over 𝔽₃; the same lemma gives Λ³ ≡ Λ² + 7u (mod 9) and a
  finite mod-27 equation. Checked on all 18 known coefficients; the digit
  product reproduces all 342 enumerated in-range entries mod 3.
- (⋆c) S := (Λ³ − Λ(t³))/3 ≡ t² + tW (mod 3): proved 2026-07-13 from the
  mod-9 cubic alone (its fixed point is unique, so
  Λ(t³) ≡ Λ² + 25t − 3t² − 3tW mod 9, then a three-line 𝔽₃ cancellation).
  Checked to order t³⁰⁰ against the mod-27 solution.

All three rest on the cluster expansion (its renewal formalism and finitely
many weights), not on data.

### The digit product and the spines

**Theorem 1 (digit product).** Write n = Σ_i n_i 3^i in base 3. Then

    P_k(n) mod 3 = [y^k] Π_i W(y^{3^i})^{n_i}.

By (⋆a), (⋆b) the product form reduces to W^n mod 3, and Frobenius gives
W(y)^{3^i} = W(y^{3^i}). W is algebraic of degree 3 over 𝔽₃(t), so by
Christol's theorem the array P_k(n) mod 3 is 3-automatic; Theorem 1 is that
automaton written out. The cubic is Artin–Schreier-like.

**Theorem 2 (odd spine).** T(3k+1, 2k+1) ≡ 1 (mod 3) for every k ≥ 0.

**Theorem 3 (even spine).** P_k(3k) ≡ 3 (mod 9) for every k ≥ 1; hence
T(3k,2k) = P_k(3k)/3 ≡ 1 (mod 3). Both spines are Lagrange–Bürmann
computations on the parametrization, whose correction factor is 1 in
characteristic 3; Theorem 3 uses (⋆c) for 3 ∤ k and the self-similarity
P_{3m}(9m) ≡ P_m(3m) (mod 9) for k = 3m. Checked for k ≤ 17, the
self-similarity for m ≤ 5.

**Theorem 4 (activation boundary).** T(n,H) ≡ 0 (mod 3) for every
n < ⌊3H/2⌋, and T(⌊3H/2⌋, H) ≢ 0 (mod 3). With k = n−H,
v₃(T(n,H)) = (3H−2n−1) + v₃(P_k(n)); the zero half needs only the diagonal
formula and Proposition 1, and the boundary is Theorem 2 for H odd, Theorem 3
for H even.

### The Smith normal form

Let T_N := [T(i,j)]_{i,j ≤ N}.

**Theorem 5 (unconditional).** The Smith normal form of T_N over ℤ is
diag(3^{e_1}, …, 3^{e_N}); the cokernel is a finite abelian 3-group. (T_N is
lower triangular with det = 3^{N(N−1)/2}.)

**Theorem 6.** T_N has exactly ⌈(N−1)/3⌉ nontrivial invariant factors: the
count is nullity(T_N mod 3), and by Theorem 4 the nonzero columns are in
echelon position, so the null space is spanned by the columns with
⌊3H/2⌋ > N.

Checked directly on the enumerated matrix for every N ≤ 36 (sympy). The
first computation, 2026-07-10:

| N | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| nontrivial factors | 1 | 2 | 2 | 2 | 3 | 3 | 3 | 4 | 4 | 4 | 5 |

Nontrivial 3-exponents by N: 4: [6]; 5: [1,9]; 6: [5,10]; 7: [6,15];
8: [2,8,18]; 9: [4,13,19]; 10: [7,14,24]; 11: [1,12,16,26];
12: [3,14,22,27]; 13: [6,16,23,33]; 14: [1,9,20,25,36]. They sum to
N(N−1)/2; about 2N/3 of the factors are 1.

### Rows, and the deficit families

The spine of column H is also the last nonzero entry of its row: right of
the spine in row n means n < ⌊3H/2⌋, the region Theorem 4 proves zero. Rows
n ≡ 2 (mod 3) contain no spine; their last nonzero entry has deficit 2.

**Theorem 7 (deficit 2).** T(3m+2, 2m+1) ≡ 2 (mod 3) for every m ≥ 0;
equivalently P_{m+1}(3m+2) ≡ 18 (mod 27). Proved 2026-07-15,
`experiments/deficit2_proof.py`: D(v) := Σ_m P_{m+1}(3m+2) v^m is a diagonal
of GΛ^n, and formal Lagrange–Bürmann over ℤ/27 with v = u/Λ³ turns
D = 5 + 18v/(1−v) into a rational identity on the mod-27 master curve
E(Λ,u) = Λ⁷ − Λ⁶ − 25uΛ⁴ − 9u²Λ³ − 18u²Λ² − 18u³ ≡ 0 (mod 27), monic in Λ,
decided by exact polynomial division; the remainder vanishes.

So the last-nonzero residue of row n cycles 1, 1, 2 with n mod 3.

**Theorem 8 (deficit 3).** For every k ≥ 3,

    P_k(3k−2) ≡ 27·r_k (mod 81),   r_k = 2, 0, 1 for k ≡ 0, 1, 2 (mod 3).

Equivalently, on the family (n,H) = (3k−2, 2k−2) where
T(3k−2, 2k−2) = P_k(3k−2)/27: T ≡ 2 (mod 3) for k ≡ 0, T ≡ 1 (mod 3) for
k ≡ 2, and v₃(P_k(3k−2)) ≥ 4 for k ≡ 1. Since r_k is a unit for k ≢ 1,

    v₃(P_k(3k−2)) > 3  ⟺  k ≡ 1 (mod 3)

for all k ≥ 3, not only the k ≤ 11 the data reached. The finer valuations
at k ≡ 1 (7, 4, 4, 5 at k = 4, 7, 10, 13) are invisible mod 81 and open.
Proved 2026-08-11, `experiments/tristruct/r2_prove_d3.py` (exact arithmetic,
about 1 s), and audited by an independent script in the same round.

*Frame.* (A1) The diagonal formula and P_k(n) = [u^k] G(u) Λ(u)^n for
n ≥ 2k+1, proved and Lean-checked. (A2) Λ ≡ the fixed point of the mod-81
master equation at all orders, derived from the cluster expansion with
completeness from the proved row bound ℓ ≤ k (interior clusters need k ≤ 4,
boundary clusters k ≤ 3, no new weights), checked against the coefficients
of Λ for k ≤ 17 (`experiments/tristruct/r2_tower_mod81.py`). (A3)
G ≡ ε_b ε_t (1 − uΛ'/Λ)/den (mod 81), the boundary residue formula reduced
mod 81, checked against the coefficients of G for k ≤ 17. (A4) Eleven
cluster weights (5 interior, 4 boundary, 5 denominator entries, overlapping)
from `experiments/cluster_weight_dp.py`, each with low-order enumeration
cross-checks. Past (A1)–(A4) everything is unconditional algebra.

*Method.* S(v) := Σ_k P_k(3k−2) v^k; the theorem is the k ≥ 3 part of
S ≡ 1 + 61v + v² + 27(2v³ + v⁵)/(1 − v³) (mod 81) (constants P₀(−2),
P₁(1) = −20, P₂(4) = 649). Lagrange–Bürmann with Φ = GΛ^{−2}, φ = Λ³ and the
substitution v = u/Λ³ give S = GΛ^{−2}/(1 − 3uΛ'/Λ) over ℤ/81[[u]]; (A2)
times Λ⁸ is the monic degree-9 curve

    E81(Λ,u) = Λ⁹ − Λ⁸ − 25uΛ⁶ − 36u²Λ⁵ − 45u²Λ⁴ − 72u³Λ² − 27u⁴ ≡ 0 (mod 81),

differentiated for Λ', and (A3) enters as εp = Λ⁶ + 15uΛ⁴ + 27u²Λ³ + 27u²Λ² + 27u³,
dp = Λ⁸ + 50uΛ⁶ + 72u²Λ⁵ + 54u²Λ⁴ + 45u³Λ² + 54u⁴. Cross-multiplying (every
cleared factor has constant term 1) leaves a polynomial of degree 32 in Λ
whose exact division by E81 has a remainder divisible by 81 in every
coefficient: sufficient, not necessary, since the ideal of relations of Λ
mod 81 exceeds (E81). Each step is also checked as a series to order 122
mod 81, and [v^k]S equals the exact P_k(3k−2) for k = 3..17. Weakest links:
(A3) at orders k ≥ 18, the exposure the mod-27 proofs also carry; then (A2).
Against deficit 2 the object grew mildly (degree in Λ 21 → 32, divisor
7 → 9) and the method changed nowhere; each further deficit costs the next
3-adic level of the master equation. The family k = 3..14 at
(n,H) = (3k−2, 2k−2) has T mod 3 = 2, 0, 1 repeating, as predicted; k ≤ 11
enumerated, k = 12..14 computed from P_k.

### Sleeve zeros

Generically v₃(P_k(n)) = d exactly; a **sleeve zero** is an entry with
v₃(P_k(n)) > d. The census on n ≤ 40 (`experiments/sleeve_zero_census.py`)
reads valuations off the triangle through v₃(P_k(n)) = v₃(T(n,n−k)) + d, so
it needs no fitted P_k and covers the whole proved range. Four record events,
final for this data: first row with two sleeve zeros n = 19 (k = 7: 3 → 4;
k = 9: 9 → 10); first adjacent pair n = 30; first three in total n = 35; first
three in a row n = 36. The last four rows:

| n | sleeve zeros (k: d → v₃(P_k(n))) | count | longest run |
|---|---|---|---|
| 37 | 13: 3 → 5, 16: 12 → 13, 17: 15 → 18 | 3 | 2 |
| 38 | 16: 11 → 13 | 1 | 1 |
| 39 | none | 0 | 0 |
| 40 | 16: 9 → 10, 18: 15 → 18, 19: 18 → 21 | 3 | 2 |

Rows 37 and 40 tie the three-in-total record; nothing reaches four. The
k = 16 diagonal spikes at n = 36, 37, 38 and 40, skipping only n = 39, the one
zero-free sleeve after n = 31. The excess v₃ − d here tops out at 3, against
a ceiling of 5 over all n (k = 8 at n = 17); the k = 18, 19 entries at n = 40
are past the fitted range but inside the proved one. Theorem 8 turns the
deficit-3 slice of the census into a formula; d ≥ 4 is open.

### Higher 3-adic levels (measured, not proved)

- Λ³ − Λ² ≡ 25t (mod 27): the cubic lifts two levels with the pair weight 25
  as its constant (25 ≡ 7 mod 9, ≡ 1 mod 3, which is why none shows mod 3).
- (Λ³ − Λ² − 25t)/27 ≡ t(W(t³) − 1) (mod 3): the level-3 correction is again W.
- (Λ(t³) − Λ² − t)/3 ≡ −(t + t² + tW) (mod 3).

### Checks against rows 37 to 40

Stated before the enumeration reached n = 40 and confirmed entry by entry on
2026-07-31: T(37,25) ≡ 1 (mod 3) (odd spine, k = 12) with T(37,H) for
H = 26..37 and T(n,25) for n < 37 all ≡ 0; T(39,26) ≡ 1 (mod 3), so
P₁₃(39) = 3T(39,26) ≡ 3 (mod 9), with row-39 entries H = 27..39 all ≡ 0;
every other in-range entry mod 3 through Theorem 1.

### Which diagonals the data can check

The formula's reach in row n is k_max(n) = ⌊(n−1)/2⌋, the same at n = 2k+1
and 2k+2: diagonal k is fitted at n = 2k+1, 2k+2 and first checked at
n = 2k+3. So the top in-range entry of an even row n = 2k+2 is on a diagonal
fitted and not yet checked (a(34) with P₁₆, a(36) with P₁₇), while the top
entry of an odd row n = 2k+3 is that diagonal's first check (a(35) checks
P₁₆). Observation, jasonp.

### What is conditional on what

Unconditional: Propositions 1 and 2, the lower half of Theorem 4, Theorem 5,
the echelon and counting steps of Theorem 6, and every Lagrange–Bürmann
identity about W itself. Conditional on the diagonal formula (shape proved,
fitted values to k = 17): everything quantified over all k; further on
(⋆a)–(⋆c) or (A2)–(A3): Theorems 1, 2, 3, 6, 7, 8 and the boundary half of
Theorem 4.

## The prime 2

**Theorem 9.** For every n odd and H even (H ≤ n), T(n,H) ≡ 0 (mod 2).
*Proof.* Let F reflect a translation-class animal about the horizontal
midline of its own bounding box. F preserves cell count and box height, so
it is an involution on the set counted by T(n,H) and T(n,H) ≡ #{F-invariant
animals} (mod 2). Invariance means reflect(A) = A + t for a translation t;
the reflection is about A's own box midline, so box(reflect(A)) = box(A),
forcing t = 0. An F-invariant animal with H even has every column invariant
under i ↦ H+1−i, fixed-point-free for H even, so every column has even size
and n is even; for n odd the fixed set is empty. ∎

The 180° rotation gives the same parity independently (its fixed cell would
sit at the box center, between rows for H even). Proved 2026-08-11
(`experiments/tristruct/candidates/p2_congruence.py`) on a self-written
enumerator before the triangle was consulted; checked on all 190 entries of
the region in n ≤ 39 (`experiments/tristruct/p2_measure.py`), 135 of them
not used in any fit and 81 of those enumerated. Row 40 is even, so the
theorem says nothing about a(40).

**The zero set of the symmetric count.** Let I(n,H) count the animals
invariant under the full height-preserving Klein group
(`results/subgroup_d2ax_byheight.txt`, n ≤ 40). I(n,H) = 0 on all 190
entries with n odd and H even (the theorem) and I(n,H) > 0 on all 630 other
entries at n ≤ 40 (`experiments/tristruct/p2_symtri_probe.py`; verified, not
proved: a 2×(n/2) rectangle is the unique Klein-invariant animal with H = 2,
so I(n,2) = [n even], but no uniform construction for all four parity
classes is written down). T(n,H) ≡ I(n,H) (mod 2) is Burnside's lemma,
checked on all 820 entries at n ≤ 40 in `results/symmetry-classes.md`; what
Theorem 9 adds is that on the region its right side is zero by proof.

**Even columns mod 2.** T(n,4) has period 4; T(n,6) and T(n,8) have period 8
out to n = 40; H = 10 is the first aperiodic even column. The diagonal formula
fixes parity only on the k ≤ 13 diagonal entries, a corner of the region.
The campaign behind Theorem 9 is recorded in `docs/lessons-learned.md`.

## The prime 5: the denominators of P_k

**Status.** Correct and proved, and a fact about a representation, not about
polyplets: P_k is integer-valued, so in the binomial basis it has no
denominator; the 5-adic content appears only because P_k is written in
powers of n. What the engine's coefficient table needs is k!·P_k ∈ ℤ[n],
proved separately; k! is not the minimal denominator (only 5-content ever
drops), so quote the divisibility, never the minimality. The question came
from a fit recorded in `results/closed-doors.md` that guessed
c_k = ⌈v₅(k!)/2⌉ and could not explain k = 11; that fit is wrong at
k ∈ {1, 11} on k ≤ 20, and k = 11 is no exception to anything. Not to be
extended.

**Statement.** Let ĉ_k := min_i v₅([nⁱ] k!·P_k), uncapped. Define the harvest

    H(k) := max { Σ_t v₅(m_t!) − 2m₁ − [j_G = 1] : j_G + Σ_{t≥1} t·m_t = k, j_G, m_t ≥ 0 },

whose closed form (Lemma C) is, for all k ≥ 0,

    H(k) = v₅(⌊k/2⌋!) − [k ≡ 1 (mod 10)].

Since k! = 2^⌊k/2⌋·⌊k/2⌋!·(odd numbers ≤ k), equivalently
ĉ_k = v₅(Π_{j ≤ k, j odd} j) + [k ≡ 1 (mod 10)]: the order-2 Newton slots eat
the even half of k!'s 5-content; the floor is the odd half plus a tax on one
residue class.

**Theorem 10 (lower bound).** ĉ_k ≥ v₅(k!) − H(k) for every k ≥ 1;
equivalently v₅(D_k) ≤ max(H(k), 0) for the minimal denominator D_k of P_k.
Equality holds at k = 1..18 (`polyplets/pin-data.md`) and at k = 19 out of
sample (predicted 2, measured 2); equality in general is a mod-5^{ĉ+1}
non-cancellation statement, checkable per k, not proved.

*Proof.* Inputs: P_k(n) ∈ ℤ for every integer n; the product form with
G = exp(Σ a_j y^j), Λ = exp(Σ b_j y^j) as a polynomial identity in n at each
y-order; P₁(n) = 25n − 45 (`docs/proofs/T-n-nm1.md`). Hence
G, Λ ∈ 1 + yℤ[[y]], and with u := Λ − 1, u₁ = P₁(1) − P₁(0) = 25 and
g₁ = −45, every other coefficient of u and G 5-integral (Lemma A); and
P_k(n) = Σ_{m≤k} C(n,m)·[y^k](G·u^m) (Lemma B, Newton form). Expanding
k!·C(n,m) = (k!/m!)(n)_m by Stirling numbers, u^m multinomially over
configurations (m_t), and G over its slot j_G,

    [nⁱ] k!·P_k = Σ_{j_G + Σ t·m_t = k} (k!/Π_t m_t!) · s(Σm_t, i) · g_{j_G} · Π_t u_t^{m_t},

each summand having v₅ ≥ (v₅(k!) − Σ_t v₅(m_t!)) + 2m₁ + [j_G = 1]
≥ v₅(k!) − H(k). ∎ Lemma C: order-1 slots are dominated by j_G
(v₅(m!) ≤ (m−1)/4), parts t ≥ 2 by parts of size 2 (v₅(m!) monotone and
superadditive); even k takes m₂ = k/2, odd k pays the g₁ tax (payoff −1) or
parks the parity in a free order-≥2 slot (m₂ = (k−3)/2), so the odd-k
optimum is v₅(m!) − [5 | m] with m = ⌊k/2⌋, and 5 | m ⟺ k ≡ 1 (mod 10) for
odd k. Checked against the case split for k ≤ 5000 and the brute-force
partition optimum for k ≤ 45.

**Why k = 11.** Harvesting one 5 against k! needs five identical Λ-slots of
order ≥ 2, cost ≥ 10, first affordable at k = 10. At k = 11 one unit is left
over and every order-1 object is taxed at least what the harvest pays
(g₁ = −45 costs 1, so H(11) = max(v₅(4!), v₅(5!) − 1) = 0; u₁ = 25 costs 2);
from k = 12 the leftover parks in a free order-2 slot. So ĉ₁₁ = 2, and the
dock lands on the whole class k ≡ 1 (mod 10). The old fit diverges from the
law at k ∈ {1, 11, 21, 25, 26, 27, 28, 29, 31, 35, …} (k ≤ 40; the script
prints the set to 120; from 25 on the cause is ⌊k/2⌋!-versus-half drift, not
the bracket). First unmeasured divergence: ĉ₂₁ = 4 − 1 = 3 where the fit says
2; it needs P₂₀, P₂₁, that is rows n ≥ 41 or ab initio cluster weights to
surplus 21.

Measured (`experiments/v5_denominator.py`, exact arithmetic, under 5 s):

| k | 1 | 2–4 | 5–9 | 10 | 11 | 12–14 | 15–18 | 19 |
|---|---|---|---|---|---|---|---|---|
| v₅(k!) | 0 | 0 | 1 | 2 | 2 | 2 | 3 | 3 |
| H(k) | −1 | 0 | 0 | 1 | 0 | 1 | 1 | 1 |
| ĉ_k predicted | 1 | 0 | 1 | 1 | 2 | 1 | 2 | 2 |
| ĉ_k measured | 1 | 0 | 1 | 1 | 2 | 1 | 2 | 2 (out of sample) |

Same script: G and Λ are integer series to order 18; the product-form
constants show v₅(a₁₀) = v₅(b₁₀) = v₅(b₁₅) = −1, the log-of-integral-series
denominators the theorem predicts (v₅(b_j) ≥ −⌊log₅ j⌋, first reachable at
j = 10 because u₁ = 25 blocks j ≤ 9); P₁..P₁₈ re-derived from enumerated
entries agree with `polyplets/pin-data.md` in every coefficient.

**Bookkeeping.** D_k = k!/5^{min(ĉ_k, v₅(k!))}, so the k = 1 row caps to
D₁ = 1 (coefficients 25, −45); the uncapped ĉ obeys the law and H(1) = −1 is
real. For k ≥ 2, v₅(D_k) = H(k) at every measured level.

**Valuation profiles** (k ≤ 19, same script, 2026-07-31):

- Upper-half law, exact at all 115 coefficients with i ≥ ⌈k/2⌉:
  v₅([nⁱ] k!·P_k) = 2(2i−k) + v₅(k!/((2i−k)!(k−i)!)), the unique
  minimal-valuation configuration (2i−k order-1 slots, k−i order-2 slots)
  carrying everything. Lean `upper_half_law`, k ≤ 18. At large k the same
  care as the bracket is needed (25 | m₂(m₂−1) first bites near m₂ ≈ 25).
- The i = 0 column: [n⁰] k!·P_k = k!·g_k, so v₅ = v₅(k!) + v₅(g_k).
- Valuations to t = 19: v₅(u_t) is 2 at t = 1, 3 at t = 17, else 0; v₅(g_t)
  is 1 at t ∈ {1, 3, 4, 7, 12, 17}, else 0. No law for these supports ("t ≡ 2
  mod 5" for {7, 12, 17} fails as a value pattern, g₂ ≡ 2 mod 5).
- 23 mid-band coefficients sit strictly above the configuration bound even
  with the exact u/g tables fed in: cross-configuration cancellations, all +1
  except (k,i) = (18,6) and (19,6) at +2. The floor law survives because
  cancellation only adds 5s.
- Mod-5 spine: negative. G and Λ mod 5 and mod 25 show no period ≤ 9 from any
  start ≤ 9 and no quadratic algebraic relation with polynomial coefficients
  of degree ≤ 5 on the 20-term window. Not to be re-hunted on this window.

**Lean** (`polyplets/Polyplets/V5Denominator.lean`, 2026-07-31): the law at
k = 1..18 (`v5_law_all`), the refutation of the old fit at k = 11
(`ceil_fit_refuted`), the k = 11 obstruction in general (`eleven_no_harvest`),
the seeds tied to P₁ (`u1_seed`, `g1_seed`); `decide`, standard axioms, no
native_decide, numerator lists tied to `Pin.lean` by rfl. The general-k
lower bound is paper-level only (`polyplets/PROOF-STATUS.md`).

## Characteristic 2, and the rank of the strip functional

### The object

At height H the strip automaton has states the king-connectivity partitions
of a column, alphabet the 2^H − 1 nonempty column fills, and
f(w) = [the placed cells form exactly one king-connected component]; it is
deterministic, so its observability matrix M over ℤ (rows the reachable
states, columns the distinct residuals) has 0/1 columns, N of them, with
r = rank_ℚ(M) ≤ N and d_p := r − rank_{𝔽_p}(M). Any weighted automaton over
a ring (one matrix per column, a scalar read at the end) is covered: every
characteristic-2 proposal of the project (Coin Flip, Coin Roll, Biased Coin
Flip, Coin Lift, `results/second-sources.md`), every cut-and-count variant
with any auxiliary group, and the exact transfer-matrix engines.

### Five theorems

**T1 (extension fields buy nothing).** rank_F(M) depends only on char F: M
has entries in the prime field, and rank is the vanishing pattern of minors,
which lie in the prime field. GF(2^k) on this matrix is GF(2); Biased Coin
Flip's GF(2^k) buys a false-pass probability of 40/2^k and not one dimension.

**T2 (multiplicative grading is rank-preserving).** The area-graded Hankel
entry is t^|u| f(uv) t^|v|, so the graded matrix is DMD' with D, D' invertible
diagonal: the same rank over any ring in which t is a unit. Coin Roll (the
area grading that gives every n in one run) costs zero dimensions by theorem,
and no weighting of that shape can help.

**T3 (the landscape is indexed by the characteristic).** A realization of
dimension D factors the Hankel matrix with inner dimension D, so rank ≤ D
over any ring; reducing an R-linear realization (R commutative, 1 ≠ 0)
modulo a maximal ideal gives D ≥ min_p rank_{𝔽_p}(M) by T1, with
rank_{𝔽_p} ≤ rank_ℚ. Cut-and-count with a group G is 𝔽_p-linear whenever p
divides |G|.

**T4 (finitely many characteristics, explicitly).** p^{d_p} divides the r-th
determinantal divisor, hence every nonzero r×r minor, which Hadamard bounds
by r^{r/2} for a 0/1 matrix; with r ≤ N,

    d_p · ln p ≤ (N/2) · ln N =: B   for every prime p,   (*)

and Σ_p d_p ln p ≤ B over all primes at once. A prime matching
characteristic 2 needs ln p ≤ B/d_2, below which every prime can be tested,
and (*) fixes rank_ℚ: a rank one above the observed maximum would have to
drop at every tested prime, costing Σ ln p > B.

**T5 (non-commutative rings, counted in scalars).** If R/m is artinian,
R/m = M_k(D) and a realization of dimension D₀ has
kD₀ ≥ rank_D(M) = rank_{𝔽_p}(M), p = char D; each dimension stores k²
scalars, so D₀k² ≥ rank_{𝔽_p}. Non-artinian simple quotients are not covered.

### Every prime, certified

Run 2026-08-14 (`experiments/tristruct/r3_char_landscape.py`, certificate
`experiments/tristruct/r3_char_landscape_certify.py`): every prime below the
T4 cutoff tested directly, everything above excluded by (*). The certifier
prints no verdict unless consistency (the sum form of (*)), the fixing of
rank_ℚ and completeness all close; it voided its first H = 6 run for an
untested-prime gap.

| H | states | N | B | rank_ℚ | primes tested | T4 cutoff | every drop, all primes |
|---|---|---|---|---|---|---|---|
| 6 | 126 | 45 | 85.6 | 35 | 4,642 | 44,633 | p=2: −8 (22.9%); nothing else |
| 7 | 322 | 103 | 238.7 | 88 | 417 | 2,853 | p=2: −30 (34.1%); p=3: −1 (1.1%) |
| 8 | 834 | 241 | 660.9 | 204 | 217 | 1,318 | p=2: −92 (45.1%); p=3: −3 (1.5%) |
| 9 | 2,187 | 577 | 1,834.2 | 501 | 196 | 849 | p=2: −272 (54.3%); p=3: −13 (2.6%) |

At H = 6, p = 2 is the only prime anywhere that drops the rank: 4,642 primes
measured and the infinitely many above 44,633 excluded. From H = 7 on only
p = 3 also moves, never above 2.6%. Characteristic 2's share grows with H
while the cutoff falls, because d_2 grows faster than B.

Settled: any commutative-ring-linear strip method has dimension at least
min_p rank_{𝔽_p}(M), attained at p = 2; no second collapse exists at any
prime, in any extension field, under any grading, with any auxiliary group.
The characteristic-0 rank at H = 21 is a floor about 17x below the exact
engine that nothing constructs (`results/second-sources.md`, Coin Lift), and
T3 makes it the best any ring-linear method can do in characteristic 0.
Untouched: non-linear methods, any other functional, and H ≥ 10 (T1–T3 are
height-independent; T4 and the search are per height).

### The characteristic-2 rank sequence

The GF(2) rank r(H) of the strip functional, from the partition automaton
(`experiments/tristruct/r3_inv_rank_probe.py`, to H = 12), the minimized
automaton (`experiments/tristruct/exactchange_minauto.py`, to H = 13) and
the closure probes of 2026-08-14 (to H = 10):

| H | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|
| minimized states N(H) | 8 | 19 | 43 | 101 | 239 | 575 | 1,399 | 3,441 | 8,539 | 21,355 |
| rank r(H) | 6 | 15 | 27 | 58 | 112 | 229 | 453 | 912 | 1,818 | 3,643 |

All ten ranks match OEIS A034299 at r(H) = a(H−1):

    r(H) = (2^(H+4) − (−1)^H (6H+7) − 9) / 36
    r(H) = 2 r(H−1) + (−1)^(H−1) ⌊(H+1)/2⌋
    generating function 1 / ((1−x²)(1−x−2x²)), partial sums of the Jacobsthal numbers.

Asymptotically r(H) ~ (4/9)·2^H, a 3² denominator in a characteristic-2
rank; the closed form predicts r(21) = 932,071. Ten terms of a four-term
recurrence is an identification, not a proof, and nothing below leans on it
past the measured range. This table has consumed three pattern matches: an
A001333 (NSW) identification of N(H) died at H = 9, 10 (575 vs 577, 1399 vs
1393), a ⌈H/2⌉-doubling guess died, and the Jacobsthal filtration below is
the third.

Cost. H = 12 on ayr: build 148.5 s, rank 874.7 s, 3.9 GB (2026-08-22). H = 13
on ayr: wall 4 h 42 min (build 886 s, rank 14,829 s), 19.8 GB, revision
95fbb6c (2026-08-23); the run asserts every earlier rank and the brute-force
anchors at H = 2, 3 before printing the new one. H ≤ 12 has two
implementations agreeing; H = 13 has the minimized automaton alone and does
not count as confirmed until a second implementation (a cross-automaton
random-word equality test) reproduces it.

### The Nerode layer

**Theorem 11.** Two strip states are GF(2)-Nerode-equivalent iff they carry
the same multiset of block neighborhoods N(b) = rows(b) expanded ±1, clipped
to [0,H). "If" is a proof over every field: the transition rule reads
nothing about a block except N(b) (a new cell at row r attaches to b iff
r ∈ N(b); b strands iff the new mask misses N(b)). "Only if" (no further
characteristic-2 merging) is measured exact at H = 4..10 with the class
inventories inspected. Every local key (mask), (mask, #blocks mod 2),
(mask, #blocks) splits classes, and φ(s), the coordinate vector of state s
in the closure basis, is injective within every mask class at H = 4..8: all
compression is cross-mask linear algebra. So the minimal automaton is
constructible a priori with N-families as states; the same congruence, shown
characteristic-free and censused to H = 21, is in `results/closed-doors.md`.
φ factors through the Nerode class trivially, and the class count exceeding
the rank (8,539 against 1,818 at H = 12, ratio 1.33 → 4.70 from H = 4) is
N(H) ~ 2.48^H against (4/9)·2^H, not a tension.

### Cell-level rank and sparsity

The column-level automaton needs one r×r matrix per column mask, 2^H − 1 of
them, which cannot be stored; an algorithm reads one cell at a time. The
cell-level functional's GF(2) rank
(`experiments/tristruct/exactchange_cell_rank.py`) is 32, 93, 210, 516 at
H = 4..7 against column rank 6, 15, 27, 58, ratio 5.3, 6.2, 7.8, 8.9: it
looks like Θ(H·2^H) (four points, ratio still rising), about 2×10⁷ at
H = 21, so the compression where an algorithm would live is about 6x, not
10³. In the pivot basis the closure hands over, the two compressed
transition matrices are sparse (average row weight 1.8 → 3.6 for A₀ and
2.7 → 5.0 for A₁ across H = 4..7, against dense ~r/2; at H = 21 about 5×10⁸
nonzeros and 10¹¹ sparse GF(2) operations, conditional on the basis). That
is the Cygan–Kratsch–Nederlof signature, but the basis comes from the
observability closure, which at H = 21 costs more than counting: the
existence is measured, an a-priori construction is open. The bits this
would buy, T(40,20) and T(40,21) mod 2, were computed by the spin runs of
2026-08-13 (`results/second-sources.md`), so the hunt is on no critical path.

### Relations, and the Jacobsthal filtration

Layer 2 is the relations among the N(H) distinct φ values, dimension N − r
(`experiments/tristruct/exactchange_kernel_probe.py`). No weight-3 relations
exist at any measured height (a sum-free-like family; not the matchings
shape). Weight-4 relations exist but do not span (H = 8: 93 of 127; H = 10:
748 of 946; the raw weight-4 counts the probe prints are 3x inflated, span
dimensions unaffected). A "shadowing" reading of the H = 4, 5 quads rests on
two quads and is too thin to call a mechanism.

Cut-and-count linearization, derived and not machine-checked: mod 2 the
connectivity indicator equals the parity of anchored {A,B}-colorings with no
AB king-adjacency (2^{c−1} for c components), and the Hankel matrix factors
through spin patterns (U_A, U_B), so the ℤ[q]/(q²) color algebra of the spin
engine is a rank factorization. A hand re-derivation found no gap; the
numeric check that must first fail on a corrupted input has not been run. A
claimed self-duality (suffix classes are also N-families) is asserted only.

The filtration (`experiments/tristruct/exactchange_doubling_probe.py`,
H = 4..10). With V_low the span of Hankel rows of words avoiding the top row
and V_int of words avoiding both boundary rows:

    dim V_int = 2^(H−2)                     exactly (4, 8, …, 256)
    dim V_low = (2^H − (−1)^H)/3 = J(H)     Jacobsthal, A001045 (5, 11, 21, 43, 85, 171, 341)
    r(H) − dim V_low = r(H−2)               by subtraction

which telescopes to r(H) = Σ_k J(H−2k), Barry's formula on A034299. The
H = 10 values (341, 256) were stated before measurement; the rest are fits
with four or five surplus points each, no more than the A034299 match. The
bottom-row variant equals the top-row variant at every height. The third
line is a subtraction: only dim V_low is a new measurement, and no map
between the top-row quotient and the height-(H−2) system has been exhibited.
Three lemmas, none proved: (L1) dim V_int = 2^(H−2); (L2) dim V_low = J(H);
(L3) an explicit isomorphism V_H/V_low ≅ V_{H−2}. L3 is the item.

**A candidate for L3** (proposal, 2026-08-22, untested). A word touching the
top row commits rows H−1 and, by king adjacency, H−2, leaving a
height-(H−2) system. For such a word w let w' delete rows H−1 and H−2 from
every column mask; conjecture: w ↦ g_{w'} induces a well-defined isomorphism
V_H/V_low → V_{H−2}. Test at H = 6, 8, 10: sample pairs with
g_{w₁} − g_{w₂} ∈ V_low and check g_{w₁'} = g_{w₂'}; one counterexample kills
it, and the dimension count gives bijectivity. If deletion fails, try the
pullback: insert two top rows into a height-(H−2) word and ask whether it
lands in a fixed complement of V_low.

### What it would not give

Even with L1–L3 proved and the basis hunt finished, the object compressed is
the mod-2 bit of T(n,H) and nothing else; the characteristic-0 rank shows no
comparable collapse, so exact and odd-prime counting keep their floor and
Coin Lift's exact-value exclusion stands (the five height-H sizes and how
they bound each other: `results/closed-doors.md`). For the mod-2 bit the spin
engine already runs in the coloring space, about (1+√2)^H = 2.414^H states,
so the ceiling on the whole program is a (2.414/2)^H ≈ 1.21^H factor on one
bit: at H = 21 roughly 55x on a computation already cheap next to the exact
engines.

## Open problems

- The individual Smith exponents e_i(N): Theorem 6 gives their count and the
  determinant their sum; the mod-9 and mod-27 lifts are the natural attack.
- The deficit-d unit formulas for d ≥ 4 (Theorems 2, 3, 7, 8 are d = 0, 1,
  2, 3), each costing the next 3-adic level of the master equation; the finer
  valuations at deficit 3, k ≡ 1 (mod 3); a law for the sleeve zeros.
- The three mod-27 congruences are measured, not proved.
- Equality in Theorem 10 for general k, and its lower bound in Lean.
- "Only if" in Theorem 11 beyond H = 10.
- L1, L2, L3 and the candidate map; the numeric check of the cut-and-count
  factorization at H = 4, 5; a cross-automaton random-word test at H = 8..10;
  a second implementation of r(13) = 3,643.
- Whether Θ(H·2^H) holds for the cell rank past H = 7, and whether sparse
  transitions exist in any a-priori basis.
- I(n,H) > 0 off {n odd, H even}: a uniform construction for all four parity
  classes.
- The prime search at H ≥ 10.

## Reproduce

    python3 -m experiments.ternary_spine            # Theorems 1-6, 15 checks; needs results/ns_a36/perheight/
    python3 experiments/deficit2_proof.py           # Theorem 7
    python3 experiments/tristruct/r2_tower_mod81.py # the mod-81 master equation and G mod 81
    python3 experiments/tristruct/r2_prove_d3.py    # Theorem 8
    python3 experiments/sleeve_zero_census.py       # the sleeve-zero table
    python3 experiments/spine_deeper.py             # the mod-27 lifts
    cd experiments/tristruct && python3 p2_measure.py && python3 p2_symtri_probe.py   # Theorem 9, the zero set
    python3 experiments/v5_denominator.py           # Theorem 10 and the profiles
    cd polyplets && lake build                      # V5Denominator.lean
    python3 experiments/tristruct/r3_char_landscape.py H [SHARD] [NSHARD]
    python3 experiments/tristruct/r3_char_landscape_certify.py <shard logs>
    python3 experiments/tristruct/exactchange_phi_probe.py
    python3 experiments/tristruct/exactchange_cell_rank.py
    python3 experiments/tristruct/exactchange_kernel_probe.py
    python3 experiments/tristruct/exactchange_doubling_probe.py
    python3 experiments/tristruct/exactchange_minauto.py 13   # ayr; H = 12 about 17 min and 3.9 GB, H = 13 4 h 42 min and 19.8 GB

The triangle is `results/triangle.txt`; the symmetric counts are
`results/subgroup_d2ax_byheight.txt`.

## Sources

- `results/ternary-spine.md` (deleted 2026-09-06; its content is above)
- `results/triangle-snf.md` (deleted 2026-09-06; its content is above)
- `results/v5-denominator-law.md` (deleted 2026-09-06; its content is above)
- `results/triangle-hunt-klein-parity.md` (deleted 2026-09-06; its content is above)
- `results/triangle-r2-d3-proof.md` (deleted 2026-09-06; its content is above)
- `results/coin-flip-characteristic-landscape.md` (deleted 2026-09-06; its content is above)
- `results/char2-basis-status.md` (deleted 2026-09-06; its content is above)
- `results/exactchange-probes.md` (deleted 2026-09-06; its content is above)
