# The height-anisotropic polyplet GF: quantified non-D-finiteness (H1)

2026-07-14. Haruspicy-style theorem (Rechnitzer's program) mechanized via the
Atom Ledger's root structure. Checker: `experiments/anisotropic_dfinite.py`
(all certificates mod p = 2⁶¹−1; gcd = 1 mod p with preserved degrees is a
rigorous certificate over ℚ).

## Object and ingredients

F(x,y) = Σ_H G_H(x) y^H, with G_H the banked fixed-height generating
functions (validated H ≤ 10; the H=11 entry is excluded — it was refuted on
2026-09-05 as a CRT wraparound, see the closing section). Define the
**new-root content**
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
  (mod p), inconsistent with the atom law. **Resolved 2026-09-05 — see the
  closing section. There was no anomaly to explain: the banked Q₁₁ is a
  failed reconstruction, and the certificates never used it.**


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


## THE UNCONDITIONAL THEOREM (2026-07-15): the attack succeeded

The "one remaining condition" above FALLS: unbounded algebraic degree of
the strip growth constants follows from strict monotonicity plus Northcott
finiteness. Nothing empirical remains.

**Theorem.** F(x,y) = sum_{n,H} T(n,H) x^n y^H is not D-finite.

*Proof, assembled from four classical ingredients:*

1. **(Fatou + rationality.)** Each G_H(x) = sum_n T(n,H) x^n is rational
   (finite transfer matrix) with integer coefficients, so by Fatou's lemma
   its lowest-terms denominator Q_H has Q_H(0) = 1 and integer
   coefficients. The reversal of Q_H is monic integral, and its roots are
   exactly the reciprocals 1/(poles of G_H). Hence mu_H := 1/(radius of
   convergence of G_H) is an algebraic integer: the radius point of a
   rational series is a pole, positive-real by Pringsheim (T >= 0), and its
   minimal polynomial divides the monic reversal.

2. **(House bound.)** Every pole of G_H has modulus >= the radius 1/mu_H,
   by the definition of radius of convergence. So every Galois conjugate of
   mu_H (a root of the reversal) has modulus <= mu_H: house(mu_H) = mu_H,
   and mu_H < lambda <= 9.3154 (the banked rigorous bound; any crude bound
   works).

3. **(Strict monotonicity — Perron-Frobenius.)** Let nu_H be the growth of
   the height-<=H strip counts, computed by the column-signature transfer
   M_H(x) (Method B): states = boundary signatures under the
   nonempty-column invariant; the signature digraph is strongly connected
   (any state reaches the single-cell state by closing components with a
   spanning column, and any state is reachable from it), so M_H(x) is
   irreducible nonnegative for x > 0. M_H sits inside M_{H+1} as a proper
   principal submatrix (signatures not using row H+1), and the extra states
   connect through the explicit cycle single-cell -> full-(H+1)-column ->
   single-cell. Deleting rows/columns of an irreducible nonnegative matrix
   strictly decreases the Perron root, so rho_{H+1}(x) > rho_H(x) at every
   x > 0; at x*_H (where rho_H = 1) this gives rho_{H+1}(x*_H) > 1, hence
   x*_{H+1} < x*_H and nu_{H+1} > nu_H strictly. Exact-height counts are
   second differences of strip counts, so (strictness => no cancellation)
   mu_H = nu_H, the pole 1/mu_H of G_H is genuine, and the mu_H are
   pairwise distinct, converging up to lambda. [Numerically confirmed
   H <= 10; Pringsheim min-modulus confirmed H <= 6.]

4. **(Northcott/Kronecker finiteness.)** For fixed D, an algebraic integer
   of degree <= D with house <= B has minimal-polynomial coefficients
   bounded by binom(D,k) B^k — finitely many integer polynomials, so
   finitely many such numbers. With B = 9.3154: for every D, only finitely
   many of the (infinitely many, distinct) mu_H can have degree <= D.
   Therefore **deg_Q(mu_H) -> infinity**.

5. **(Dichotomy theorem, above.)** A y-ODE of order r with x-degrees <= D
   forces deg_Q(mu_H) <= D at all but at most r heights — contradicted by
   (4) for every (r, D). (Wlog the ODE is over Q(x,y): F has rational
   coefficients, and D-finiteness over C descends to the field of
   definition.) QED

**Scope.** The proof uses only: integer counts, per-height rationality,
and strictly increasing bounded strip growth constants. It therefore
applies verbatim to fixed POLYOMINOES by height (A001168's triangle),
polyhexes, polyiamonds, and generally to any lattice-animal family with a
column transfer matrix — a universal anisotropic non-D-finiteness
criterion. We have not found this Northcott-plus-monotonicity argument in
the literature (Rechnitzer's haruspicy proves the SAP analog by very
different means); flagged in papers/MISSING.md for a literature check
before any external claim of novelty.

**Status ledger for this document:** the quantified psi-boxes and the
irreducibility certificates above remain as concrete effective content;
the conditional statements are all retired.


## Prior art, read and compared (2026-08-01)

The novelty flag above sent us to the literature. Papers now held in
`papers/`: Haruspicy 2 (arXiv math/0406450), Haruspicy 3 (math/0408054),
and — the one that actually matters — **Bousquet-Melou & Rechnitzer,
"Lattice animals and heaps of dimers," Discrete Math. 258 (2002) 235-274**,
free from labri.fr/perso/bousquet.

**First finding: we were chasing the wrong paper.** The D-finiteness test is
not in Haruspicy 1. Haruspicy 2 states it as Theorem 15 "(from [4])" and
Haruspicy 3 as Theorem 5 "(from [6])"; both references resolve to BM-R 2002,
Lemma 9. Haruspicy 1 supplies the combinatorial section/density machinery
(Haruspicy 2's Theorem 1), not the test.

**Their criterion** (BM-R 2002, Lemma 9, verbatim modulo notation):

> Let S(q,u) = sum_n S_n(q) u^n be a formal power series in u with
> coefficients in C(q). Assume S(q,u) is D-finite in u. For n >= 0 let P_n
> be the set of poles of S_n(q), and let P = union P_n. Then P has only a
> finite number of limit points.

Their proof: extract the coefficient of u^n from the ODE to get
a_0(q,n)S_n = a_1(q,n)S_{n-1} + ... + a_k(q,n)S_{n-k} with a_i in C[q,n];
so S_n has denominator I(q)·prod_m a_0(q,m). If l is a limit point there are
(q_i, n_i) with q_i -> l, n_i -> infinity, a_0(q_i,n_i) = 0; dividing
a_0 = sum_k b_k(q)n^k by n_i^d and letting i -> infinity gives b_d(l) = 0.
So every limit point is a root of the fixed polynomial b_d. QED

**Side by side with the dichotomy theorem above:**

| | BM-R 2002, Lemma 9 | ours (dichotomy) |
|---|---|---|
| opening move | extract y-coefficients of the ODE => linear recurrence, polynomial coefficients | **identical** |
| what is tracked | the *whole* pole set of every slice | *one* pole per slice, x = 1/mu_H |
| finiteness input | topological: limit points of a subset of C | arithmetic: Northcott (bounded degree + bounded house) |
| mechanism | asymptotic in n — divide by n^d, take the limit, hit the leading coefficient b_d | at a single level: lower faces regular at 1/mu_{H0} by strict monotonicity, so c_0 vanishes there; a degree-D polynomial over Q cannot kill an algebraic number of degree > D |
| conclusion | qualitative: D-finite or not | **effective**: explicit (r, D) exclusion boxes |
| input needed to apply | an explicit combinatorial description of the denominators (cyclotomic Psi_k from k-sections) | Perron-Frobenius monotonicity + any crude upper bound on lambda |

**Honest reading.** Step 1 is theirs and dates to 2002 — extracting the
coefficient relation is not ours to claim, and we should cite Lemma 9 for it
rather than presenting the derivation as self-contained. Everything after
step 1 diverges: they need all the poles and an accumulation argument in C,
we need one distinguished pole and its degree over Q. The lightness of our
hypotheses is the actual contribution — needing only monotonicity plus a
crude bound is why the proof transports verbatim to polyominoes-by-height,
polyhexes, polyiamonds, and any family with a column transfer matrix, where
theirs needs a bespoke combinatorial denominator analysis per family.
Northcott appears in neither paper.

### Klazar 2003, read (2026-08-01): analytic, not arithmetic

Haruspicy 2's reference [13] — M. Klazar, "Non-P-recursiveness of numbers of
matchings (linear chord diagrams) with many crossings," Adv. in Appl. Math.
30 (2003) 126-136, same issue as Haruspicy 1 — was pulled on the guess that a
one-variable non-P-recursiveness proof might be arithmetic and so a closer
relative of ours than the Haruspicy line. **The guess was wrong: his
obstruction is analytic.** Recording it because the negative is useful.

His Theorem 1: let F satisfy F' = G(x,F) with G a Laurent series; if (i) F is
*not analytic*, (ii) G is analytic, (iii) ord_y(G) < 0, then F is not
D_A-finite, a fortiori not D-finite. Proof: iterate to get F^(k) = G_k(x,F)
with ord_y(G_k) = k(p-1)+1 strictly negative; a D-finite relation collapses to
H(x,F) = 0 with H analytic and nonzero (its y-order is R_0 G_m's, still
negative), so Weierstrass preparation plus Puiseux force F analytic —
contradicting (i). The whole lever is **divergence**: F must have zero radius
of convergence.

That criterion cannot engage with our object at all. Every G_H is rational
with radius 1/mu_H, and mu_H < lambda, so F(x,y) is analytic in a bidisc.
Condition (i) fails at the first hurdle.

**Three distinct obstruction types now mapped in this neighbourhood:**

| | obstruction | lever |
|---|---|---|
| BM-R 2002 | topological | accumulation of the pole set in C |
| Klazar 2003 | analytic | zero radius of convergence vs. forced analyticity |
| ours | arithmetic | degree and house of algebraic numbers (Northcott) |

**The genuinely useful thing Klazar has, and we do not.** He enlarges the
target class from D-finite (polynomial coefficients) to **D_A-finite**
(analytic coefficients), on the explicit ground that "the key lies in the
analytic x nonanalytic dichotomy" — so polynomiality was never doing the
work, and he gets the stronger conclusion for free. Our theorem cannot follow
him there, and it is worth being clear why: the step "a rational polynomial
of degree <= D cannot vanish at an algebraic number of degree > D" is the
entire dichotomy argument, and it dies the instant the coefficients are
analytic rather than polynomial, since an analytic function may vanish at
1/mu_{H0} without vanishing identically. **So our result is
not-D-finite-over-Q(x) and does not extend to D_A-finite.** That is a real
ceiling on the method, not a gap in the write-up, and it should be stated
rather than left for a referee to notice.

**One resonance worth following up separately.** Klazar's Theorem 4: (con_n)
and (cro_n) are P-recursive modulo 2^k for every k — an object with no
P-recursive description whose reductions mod a prime power are algebraic.
That is structurally the same phenomenon as our ternary spine
(`results/ternary-spine.md`): the height triangle admits no C-finite
recurrence, yet mod 3 it is governed by the cubic W^3 = W^2 + t. Different
combinatorics, same shape of answer. Whether the mechanisms are related is
open and nobody has looked.

**What remains unresolved, permanently by this method.** Whether the
Northcott endgame appears somewhere else cannot be settled by search —
absence is not a database result. The claim should therefore be scoped so it
does not rest on absence: assert the *lighter hypotheses* and the *effective
boxes*, cite BM-R 2002 for the shared opening, and do not write "first."
Two levers remain if a stronger statement is ever wanted: MathSciNet's
citation graph on BM-R 2002 (read-only, weekday guest pass at Pitt Hillman or
CMU Hunt), or asking Rechnitzer directly. Both jasonp's call.

### Item CLOSED (2026-08-01)

The remaining leads named in the original todo -- Bell, Gerhold, Mezzarobba,
Guttmann's solvability tests, the Bousquet-Melou anisotropic surveys -- were
swept; detail and verdict in `papers/MISSING.md`. No collision. Every method
located is topological (BM-R) or analytic (Klazar divergence; Bell-Gerhold-
Klazar-Luca zero-counting); the one paper pairing heights with D-finiteness
(Bell-Hu-Satriano, arXiv 2003.01255) is arithmetic dynamics along orbits of
rational maps, a different configuration.

The paper was updated the same day rather than left carrying the unattributed
version: `paper/polyplets-report.tex` now cites BM-R Lemma 9 inside the proof
at the extraction step, carries a "Relation to existing work" paragraph
stating what is shared and what diverges, claims the Northcott endgame with
the absence caveat explicit instead of implied, and records the
D_A-finiteness ceiling. A stale citation was fixed in passing: the
`rechnitzer` bibitem had labelled JCTA 113 (2006) 520-546 as "Haruspicy 3";
that is Haruspicy 2 (Haruspicy 3 is the directed bond-animal paper).

Nothing further is owed here. The two optional levers above are for a
stronger claim than the paper now makes.

### Forward citation crawl (2026-08-01) — still no collision

The one search direction never tried: everything above was found by keyword
or by following references *backwards*. Crawled forward with OpenAlex and
Semantic Scholar (`experiments/citation_crawl.py`) over BM-R 2002 (83/74
citing), Haruspicy 2 (13/17), Haruspicy 3 (4/4), Chan-Rechnitzer 2018 (20/2),
BBEP 2020 (3/20), plus the arithmetic relatives Bell-Hu-Satriano (5) and
Bell-Gerhold-Klazar-Luca (25). Table and per-seed notes in
`papers/MISSING.md`. Every descendant of BM-R that proves non-D-finiteness
uses pole/singularity accumulation; no arithmetic endgame on a family of
slice growth constants appears anywhere in those sets.

The crawl did upgrade the nearest relative. **Bell, Nguyen & Zannier,
"D-finiteness, rationality, and height"** (Trans. AMS 373 (2020) 4889-4906;
II, Adv. Math. 414 (2023); III, multivariate Polya-Carlson, Math. Z. 306
(2024), with S. Chen) is height theory applied directly to D-finite series —
closer to us than Bell-Hu-Satriano's arithmetic dynamics. It is still a
different configuration: they bound the Weil heights of the *coefficients*
and conclude rationality; we bound degree and house of the *slice growth
constants* and conclude a contradiction. Their forward citations (15/3/4)
contain no combinatorial application. Now cited in the paper's "Relation to
existing work" paragraph, so that paragraph names the arithmetic neighbours
instead of resting on absence alone.

Coverage caveat kept honest: OpenAlex and Semantic Scholar disagree on counts
(83 vs 74 on BM-R), so neither is complete; MathSciNet and Google Scholar's
own "Cited by" remain unrun and remain jasonp's call.

### Third database: Google Scholar (jasonp, 2026-08-01) — no collision

The optional belt-and-braces from the crawl above, run. Scholar's *search
within citing articles* is full-text, unlike OpenAlex and S2 which matched
metadata only — a genuinely different instrument, and the one that could catch
a paper using Northcott inside a proof without saying so in its abstract.

Over BM-R 2002's 79 citing articles (a third count: OpenAlex 83, S2 74):
**`Northcott` 0 hits, `Mahler` 0 hits.** `algebraic degree` and `height` return
hits, all false — degree of the algebraic *equation* a generating function
satisfies, and column/path height in bargraphs. Standalone searches
`"growth constant" Northcott D-finite` and `"transfer matrix" "algebraic
degree" "not D-finite"` return nothing at all. Haruspicy 2's 14 citing articles
read in full: surveys, constructions, and the pole-accumulation route; the one
new name, Assis-van Hoeij-Maillard's Fuchsian-ODE paper (J. Phys. A 2016),
runs the opposite direction — exhibiting ODEs for solvable models, not
supplying a non-D-finiteness criterion.

Three independent databases, no collision, and the strongest of the three
searches full text. Table and per-term notes in `papers/MISSING.md`. The
paper's "Relation to existing work" scoping is unchanged and stays correct:
absence cannot be established by search, and we claim the argument with that
qualification. MathSciNet is now recorded as closed rather than pending —
Scholar covers a superset of venues and searches full text, so a fourth
negative would not change the sentence.

### The H=11 anomaly, resolved (2026-09-05)

The banked `Q₁₁` is a failed reconstruction: a CRT lift from 133 primes whose
modulus half (1241 digits) is below the true coefficient size (about 1299 digits
at degree 13381), so every coefficient from degree 8159 up is a residue. Proved
by the pipeline's own soundness gate on the banked entry
(`experiments/gf_h11_validate.py`: `Q₁₁ · B₁₁ ≠ P₁₁` mod a fresh prime, first
mismatch at n = 8170); the full account and the price of a re-recovery (about
48 CPU-hours, not launched) are in [gf-head-check.md](gf-head-check.md).
"`Q₁₁` shares no roots with `Q₉Q₁₀`" was a restatement of the wraparound, not a
fact about height 11. Nothing here used it: the ψ-ladder and irreducibility
certificates, the monotonicity lemma and the theorem read `validated=True`
blocks only and stop at H=10.
