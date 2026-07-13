# The height-anisotropic polyplet GF: quantified non-D-finiteness (H1)

2026-07-14. Haruspicy-style theorem (Rechnitzer's program) mechanized via the
Atom Ledger's root structure. Checker: `experiments/anisotropic_dfinite.py`
(all certificates mod p = 2⁶¹−1; gcd = 1 mod p with preserved degrees is a
rigorous certificate over ℚ).

## Object and ingredients

F(x,y) = Σ_H G_H(x) y^H, with G_H the banked fixed-height generating
functions (validated H ≤ 10; the H=11 entry is validated=False and behaves
anomalously — excluded). Define the **new-root content**
ψ_H = Q_H / gcd(Q_H, Q_1 Q_2 ⋯ Q_{H−1}): the denominator factors appearing
first at height H. Certified:

- deg ψ_H = 1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289 (H = 1..10);
- every ψ_H squarefree; every P_H/Q_H in lowest terms (all roots active);
- ψ-roots are genuinely new: coprime to every earlier Q by construction.

## Theorem (quantified)

Suppose Σ_{i≤r} p_i(x,y) ∂_y^i F = 0 with p_i ∈ ℚ[x,y], not all zero,
D = max deg_x p_i. Extracting y-coefficients gives, for every H,
Σ_{δ≤σ} c_δ(x,H) G_{H−δ}(x) = 0 with deg_x c_δ ≤ D, deg_H c_δ ≤ r, and
{c_δ} ≡ 0 forces {p_i} ≡ 0 (falling factorials of H are independent).

*Pole argument.* Let α be a root of ψ_{H₀}. Instance the relation at
H = H₀: every term with δ ≥ 1 references a height < H₀, where α is not a
pole; G_{H₀} has a genuine pole at α (lowest terms + squarefree). Hence
c_0(α, H₀) = 0 — for all deg ψ_{H₀} roots — so **deg ψ_{H₀} > D forces
c_0(·, H₀) ≡ 0**. If this holds at r+1 distinct levels, c_0 ≡ 0 (its
H-degree is ≤ r); recurse through the faces δ = 1, 2, … (each reuses the
same levels, anchored at H₀+δ). All faces vanish — contradiction. ∎

**Corollary (from the certified levels).** No annihilating y-ODE exists with
(order r, x-degree D) in any of:
r ≤ 5 & D ≤ 28 · r ≤ 4 & D ≤ 67 · r ≤ 3 & D ≤ 180 ·
r ≤ 2 & D ≤ 461 · r ≤ 1 & D ≤ 1253 · r = 0 & D ≤ 3288.
(Rule: excluded whenever ≥ r+1 certified levels have deg ψ_H > D.)

**Conditional full statement.** If deg ψ_H → ∞ with squarefreeness and lowest
terms persisting (measured growth ×≈2.7 per level, structural in the strip
transfer matrices), then F(x,y) is **not D-finite**. This is the king-animal,
height-anisotropic analog of Rechnitzer's SAP theorem; as there, the isotropic
a(x) remains untouched.

## Notes

- This is the Atom Ledger's root-separation theorem
  (`results/triangle-structure.md` §6) re-run at the generating-function
  level, where a pole-localization argument replaces the Vandermonde; the
  ψ-construction removes any reliance on the triple-product atom law (whose
  no-cancellation part was only verified for H ≤ 7).
- The paper's "not expected to be D-finite" sentence for the by-height
  columns can now cite the corollary.
- H=11 anomaly recorded: the unvalidated Q₁₁ shares no roots with Q₉Q₁₀
  (mod p), inconsistent with the atom law — that banked entry deserves a
  re-recovery before use anywhere.


## Unconditionalization push (2026-07-15): the dominant-pole dichotomy

The ingredient list is now reduced to ONE crisp spectral statement.
Additions certified in `experiments/anisotropic_dfinite.py`:

- **Strict monotonicity (lemma).** The strip growth constants strictly
  increase: mu_H = 1.0, 2.41421 (=1+sqrt2), 3.44372, 4.18232, 4.71780,
  5.11532, 5.41785, 5.65337, 5.84046, 5.99170 (H = 1..10, exact-coefficient
  evaluation; an earlier float artifact at H=9 corrected). Proof route:
  Perron-Frobenius — the height-<=(H+1) signature transfer is irreducible on
  its recurrent class and contains the height-<=H system as a proper
  principal submatrix, so its dominant eigenvalue is strictly larger;
  exact-height counts are second differences of strip counts, so no
  cancellation and 1/mu_H is a genuine pole of G_H, distinct from every
  pole of every G_j, j < H.

- **Atom irreducibility (new hard data).** psi_H is IRREDUCIBLE over Q for
  H = 1..8 (degrees 1, 2, 4, 9, 29, 68, 181, 462) — single-prime
  certificates for H <= 4, multi-prime subset-sum-intersection certificates
  for H = 5..8. Hence deg_Q(mu_H) = deg psi_H at every certified level.
  (H = 9, 10 at degrees 1254, 3289 left uncertified — factoring cost.)
  Side effect: irreducibility + positivity of the dominant root means, by
  Galois conjugation, EVERY root of the atom is active in T(n,H) — the
  Atom Ledger's minimality ingredient is no longer needed at these levels.

**Theorem (dichotomy).** If F(x,y) is annihilated by a y-ODE of order r
with x-degrees <= D, then deg_Q(mu_H) <= D for all but at most r values of
H. Proof: at level H0, instance the coefficient relation at H = H0; every
lower face is finite at x = 1/mu_{H0} (strict monotonicity), G_{H0} has a
pole there, so c_0(1/mu_{H0}, H0) = 0. A rational polynomial of degree
<= D cannot vanish at an algebraic number of degree > D, so
deg_Q(mu_{H0}) > D forces c_0(., H0) == 0; r+1 such levels kill c_0 as a
polynomial in H, and the face recursion reuses the same levels. QED

**Corollary (boxes, self-contained ingredients).** No annihilating y-ODE
with (r <= 4 & D <= 8), (r <= 3 & D <= 28), (r <= 2 & D <= 67),
(r <= 1 & D <= 180), (r = 0 & D <= 461). Weaker than the psi-boxes above
but resting only on monotonicity + irreducibility certificates.

**The one remaining condition.** F is not y-D-finite provided
limsup_H deg_Q(mu_H) = infinity — i.e. the strip growth constants have
unbounded algebraic degree. Every certified level has
deg_Q(mu_H) = deg psi_H, growing at the measured rate ~sqrt(lambda) = 2.67
per level (atom degree tracks frontier size). This conjecture — natural,
spectral, and checked to degree 462 — is the entire distance between the
quantified theorem and full non-D-finiteness.
