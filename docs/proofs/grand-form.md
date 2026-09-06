# The grand form is a theorem (exact one-mode resummation)

2026-07-21. Upgrades the Corollary of `diagonal-law.md` from a sketch to a
standalone theorem, with the sharp onset. Content: the diagonal cumulants are
*exactly* linear — each level k adds exactly two new rational constants
(a_k, b_k) — so the `scripts/derive_pk_fast.py` model
`P_k(n) = [y^k] exp(Σ_j (a_j + b_j n) y^j)` is proved structure, not an
ansatz. Combined with the shape theorem this removes the "defect-gas
structure" conditionality from the wired diagonals k = 10..19 (modulo the
Lean formalization of THIS proof, tracked separately).

Machine check: `experiments/grand_form_check.py` — constructs z*, u, C, μ
below ab initio from the Lean-verified cluster weights (j ≤ 3), reproduces
the banked real triangle at every in-onset point it can reach, and
reproduces the production P_1..P_3 coefficient-exactly.

## Statement

**THEOREM (grand form).** There are rational constants a_j, b_j (j ≥ 1),
with (a_j, b_j) determined by the cluster weights of surplus ≤ j, such that

> P_k(n) = [y^k] exp( Σ_{j≥1} (a_j + b_j n) y^j )  for every k ≥ 0, n ≥ 2k+1,

where P_k is the diagonal polynomial of the law T(n, n−k) = P_k(n)·3^(n−1−3k)
(`diagonal-law.md`). Equivalently, in transfer coordinates: there are
C, μ ∈ ℚ[[y]] with C(0) = 1/3, μ(0) = 3 and

> T(H+k, H) = [y^k]( C(y)·μ(y)^H )  for every k ≥ 0, H ≥ k+1;

i.e. the cumulants c_j(H) = [y^j] log A_H of A_H(y) := Σ_k T(H+k,H) y^k are
EXACTLY linear in H for H ≥ j+1.

Everything happens in ℚ[[y]] (y-adic formal algebra); no analysis, no
convergence, and — the load-bearing feature — **no weight enumeration**: the
proof is uniform in the weights, so it covers all k at once.

## Setup (from the chain identity)

`diagonal-law.md` Step 2 proves the exact identity for
F(y,z) = Σ T(n,H) y^(n−H) z^H:

> F = E_b · (1−S)^(−1) · E_t + P,

with S = 3z + σ, σ = Σ_{j≥1} σ_j(z) y^j, and (Step 3, from ℓ ≤ k on cluster
rows) the three degree facts, per y-order j:

- deg σ_j ≤ j+1  (a surplus-j cluster has ≤ j rows, plus the walk row above);
- deg [y^j] E_b ≤ j+1, with E_b = z·(1 + edge terms);
- deg [y^j] E_t ≤ j, and deg_z [y^j] P ≤ j.

These are the only inputs. All series below live in ℚ[[y]] with coefficients
in ℚ[z] per y-order.

## Step 1 — root and cofactor (Weierstrass preparation by hand)

*There is a unique pair (z*, u) with z* ∈ 1/3 + yℚ[[y]],
u = Σ_j u_j(z) y^j, each u_j a polynomial of degree ≤ j, u_0 = 3, and*

> 1 − S = (z* − z) · u.

Construction by induction on the y-order. Write z* = 1/3 + Σ_{j≥1} ζ_j y^j.
Order 0: u_0·(1/3 − z) = 1 − 3z gives u_0 = 3. Order j ≥ 1, collecting
[y^j] of (z*−z)u = 1−S:

> (1/3 − z)·u_j = N_j − 3ζ_j,  N_j := −σ_j − Σ_{m=1}^{j−1} ζ_m u_{j−m}.

N_j is a known polynomial with deg N_j ≤ j+1 (deg σ_j ≤ j+1; inductively
deg u_{j−m} ≤ j−m < j+1). Choose **ζ_j := N_j(1/3)/3**: then the right side
vanishes at z = 1/3, the division by (1/3 − z) is exact in ℚ[z], and
deg u_j ≤ j. This simultaneously constructs the root and the cofactor.

u is a unit (u(0,0) = 3 ≠ 0). Substituting z = z* (legal: z* − 1/3 ∈ yℚ[[y]])
gives 1 − S(y, z*) = 0: z* is a root, and it is the unique root in
1/3 + yℚ[[y]] (if z' were another, 0 = (z*−z')·u(y,z') with u(y,z') a unit).

## Step 2 — the unit inverse is polynomial per order

u/3 = 1 + Σ_{j≥1} (u_j/3) y^j, so u^(−1) = (1/3)·Σ_{m≥0} (−1)^m
(Σ_{j≥1} (u_j/3) y^j)^m. The y^k-coefficient takes only m ≤ k and
compositions j_1+…+j_m = k, each term of z-degree ≤ Σ deg u_{j_i} ≤ k:

> deg [y^k] u^(−1) ≤ k.

Hence for G := E_b · E_t · u^(−1), splitting k = k_b + k_t + k_u:

> deg [y^k] G ≤ (k_b + 1) + k_t + k_u = k + 1.

Equivalently, writing G = Σ_i g_i(y) z^i: **ord_y(g_i) ≥ i − 1**. (This is
the fact that makes the resummation exact rather than asymptotic.)

## Step 3 — exactly one geometric mode for H ≥ k+1

Let μ := 1/z* (a unit, μ(0) = 3). In ℚ[[y]][[z]],
(z*−z)^(−1) = μ·Σ_{m≥0} (μz)^m, so F − P = G·(z*−z)^(−1) and

> [z^H](F − P) = Σ_{i=0}^{H} g_i·μ^(H+1−i) = μ^(H+1)·( Ĉ − ρ_H ),

with Ĉ := Σ_{i≥0} g_i z*^i (y-adically convergent, since
ord_y(g_i z*^i) ≥ i−1) and tail ρ_H := Σ_{i>H} g_i z*^i, which has
**ord_y(ρ_H) ≥ H**. So for H ≥ k+1 the tail contributes nothing at order y^k,
and [z^H][y^k]P = 0 as well (deg_z [y^k]P ≤ k < H). Setting C := Ĉ·μ:

> T(H+k, H) = [y^k][z^H] F = [y^k]( C·μ^H )  for all H ≥ k+1. ∎

(Constant check: [y^0]G = z/3, so Ĉ(0) = 1/9, C(0) = 1/3, and k = 0 reads
T(H,H) = 3^(H−1) — the king chain.) The onset H ≥ k+1 is exactly the law's
n ≥ 2k+1: no strength is lost at the boundary, which is where the top wired
diagonals live.

## Step 4 — cumulant linearity in H

Fix j and H ≥ j+1. Step 3 gives A_H ≡ C·μ^H mod y^(j+1) (each order k ≤ j
needs only H ≥ k+1). A_H is a unit ([y^0]A_H = 3^(H−1)), so taking log mod
y^(j+1):

> c_j(H) = [y^j] log C + H·[y^j] log μ  for all H ≥ j+1. ∎

## Step 5 — production coordinates (diagonal Lagrange lemma)

The production form reads the triangle along fixed n, not fixed H; the
change of coordinates is the classical diagonal form of Lagrange inversion,
proved here in full since it must be exact per order.

**Lemma.** Let f, φ ∈ ℚ[[w]], φ(0) ≠ 0, and let ŵ ∈ yℚ[[y]] be the unique
solution of ŵ = y·φ(ŵ) (it exists by the Step-1 induction applied to
w − yφ(w)). Then

> Σ_{k≥0} y^k · [w^k]( f·φ^k ) = f(ŵ) / (1 − y·φ′(ŵ)).

*Proof.* [w^k](fφ^k) = res_w( fφ^k w^(−k−1) ), so the sum is
res_w( f/w · Σ_k (yφ/w)^k ) = res_w( f / (w − yφ(w)) ). By Step 1's
construction, w − yφ(w) = (w − ŵ)·v(w,y) with v a unit per y-order;
differentiating at w = ŵ gives v(ŵ) = 1 − yφ′(ŵ). Finally
res_w( (f v^(−1)) · (w−ŵ)^(−1) ) = Σ_m ŵ^m [w^m](f v^(−1)) = (f v^(−1))(ŵ),
y-adically convergent. ∎

Apply with f = C·μ^n, φ = μ^(−1) (so φ(0) = 1/3 ≠ 0), ŵ = y/μ(ŵ):

> L_n(y) := Σ_k y^k [w^k]( C·μ^(n−k) ) = K(y)·M(y)^n,
> K := C(ŵ)/(1 − yφ′(ŵ)),  M := μ(ŵ) —

n enters only through M^n. By Step 3, [y^k]L_n = T(n, n−k) whenever
n − k ≥ k+1, i.e. n ≥ 2k+1. Renormalizing to the law's units,
P_k(n) = T(n,n−k)·3^(1+3k−n) gives, for n ≥ 2k+1:

> [y^k] Σ_k P_k(n) y^k = [y^k]{ 3^(1−n)·L_n(27y) }
>                      = [y^k]{ 3K(27y) · (M(27y)/3)^n }.

Both 3K(27y) and M(27y)/3 have constant term 1 (K(0) = C(0) = 1/3,
M(0) = 3), so with

> a_j := [y^j] log( 3·K(27y) ),  b_j := [y^j] log( M(27y)/3 ),

we get P_k(n) = [y^k] exp( Σ_{j≥1} (a_j + b_j n)·y^j ) for n ≥ 2k+1. Every
object at order j is built from σ_{≤j}, E-terms ≤ j — weights of surplus
≤ j — which gives the locality claim. ∎

## Corollaries

1. **Two new constants per level.** [y^k]exp(Σ c_j y^j) = (polynomial in
   c_1..c_{k−1}) + c_k, so P_k(n) = known_k(n) + a_k + b_k·n with known_k
   determined by levels < k — exactly `scripts/derive_pk_fast.py`. Given the
   shape theorem (deg P_k ≤ k, Lean), any TWO in-onset values pin (a_k, b_k)
   by a nonsingular 2×2 rational solve, and every further in-onset value is a
   theorem, not a test. The 28 extra exact matches recorded by
   `scripts/verify_diagonal_pins.py` are over-determination.
2. **Leading coefficient, now proved.** The only n^k-term at order y^k is
   (b_1·n·y)^k/k!, so [n^k]P_k = b_1^k/k!. From the first-principles
   P_1(n) = 25n − 45 (`T-n-nm1.md`): b_1 = 25, a_1 = −45. Hence
   **[n^k]P_k = 25^k/k! for all k** — the conjecture of
   `results/diagonal-formula.md` (and the deferred stretch goal of `Shape.lean`) —
   and deg P_k = k exactly.
3. **Conditionality ledger.** a(30)..a(40) (wired cells on diagonals
   k = 10..19) now rest on: the real sweeps (H ≤ 21 as of a(40)), the shape theorem
   (Lean, deductive), THIS theorem (paper level, machine-checked), and the
   banked 2-point solve inputs. The former free-standing assumption "the
   defect gas is exactly linear" is discharged. The former Lean PREDICTED
   tier for k = 12..16 is retired: this proof is formalized (§Formalization
   below) and `P<k>_grand_of_banked` pins every level from two real-swept
   cells with H ≤ 20 (`polyplets/PROOF-STATUS.md`).

## Formalization (2026-07-21)

Formalized in Lean 4: `polyplets/Polyplets/Grand/` (plan
`polyplets/GRANDFORM-PLAN.md`, briefs `polyplets/briefs/`). The proof was
restructured for Lean as the **staircase route**: in sequence form, Steps
1–3 collapse to a convolution fixed point (ν = z*, μ = 1/z*) plus one
strong induction (`d_mu_rec`), and Step 5's Lagrange lemma becomes the `W`
fixed point of `ExpForm.lean` — same theorem, no power-series ring.
Audits (`Polyplets/Grand/Audit.lean`): `grand_form` (the exp-form above)
and `T_staircase` depend on **standard axioms only**; `lead_coeff_25`
(Corollary 2) adds the single `V_1_1` native_decide leaf; the production
polynomials are pinned for k ≤ 18 from two real-swept cells per level
(`P<k>_grand_of_banked`) — *conditional on those cells*: they are
hypotheses of the Lean theorems, engine values assumed, not proved in
Lean (`docs/lean-hostile-witness.md`). This retires the Lean PREDICTED
tier. The item
"Lean formalization" below is CLOSED.

## What remains open (unchanged from diagonal-law.md)

- Onset sharpness at n = 2k (failure below onset) — verified on banked data,
  proved ab initio only k ≤ 5.
- **Denominator k! — CLOSED both ways (2026-07-31)**: `k!·P_k ∈ ℤ[n]` is
  proved for all k (Lean `production_factorial_int`); minimality is FALSE —
  the minimal denominator is k!/5^{ĉ_k}, ĉ_k = v₅(k!) − v₅(⌊k/2⌋!) +
  [k ≡ 1 (mod 10)] (`results/arithmetic-structure.md`; lower bound proved,
  exact k ≤ 19). The old "25^k/k! shows k! is necessary" pointed the wrong
  way — it is why the 5-part drops.
  (Corrected 2026-07-30, AUDIT-2026-07-30 P8: this entry previously read
  "monomial integer coefficients of P_k, coefficient integrality observed
  k ≤ 17". Monomial integrality is FALSE at every k ≥ 2 — P_2's leading
  coefficient is 625/2 — measured across all 19 wired levels. Integer
  *values* are proved: Step 6 of `diagonal-law.md`, `production_int_all` in
  Lean; the equivalent Newton-basis integrality checks out k = 1..19.)

(The Lean formalization of this theorem, formerly listed here, is CLOSED —
see §Formalization above.)
