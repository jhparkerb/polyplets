# The area-moment generating functions of convex king animals are
# algebraic at every moment level: the Temperley moment method, executed

Date: 2026-08-15 (autonomous session 08). Executes the recipe sketched in
`docs/proofs/area-moments-method.md` (s07), building on the proven q-FE of
`docs/proofs/convex-area-q-temperley.md` (s04) and the level-0 kernel
solution of `docs/proofs/convex-box-kernel.md` (s03). Companion script:
`experiments/s08_moment_kernel.py`.

**Theorem (established here).** For r ≥ 0 let

    M_r(x,y) = Σ_{w,h} ( Σ_{A in box w×h} area(A)^r ) x^w y^h

be the bivariate r-th area-moment generating function of convex king
animals with bounding box exactly w×h (and the same with the two king
boundary terms dropped for the convex-polyomino control). Then for EVERY
r, M_r is algebraic over Q(x,y): it is an explicit element of
Q(x,y,√Δ), Δ = (1−x−y)² − 4xy, produced by the recursive kernel
construction below. In particular the univariate area-moment GFs
A_r(t) = M_r(t,t) by semiperimeter are algebraic for all r — the closed
forms fitted in s07 (r = 1,2) and s08 (r = 3,4) are instances. This
resolves s07's OPEN ("PROVE A_r algebraic by the Temperley moment
method").

## 1. The moment hierarchy of the q-functional equation

The s04 q-FE system (proven; validated transitions) is, schematically,

    F_ph(s;q) = Σ_terms c(z)·X(q),    z = qs,

where each term's coefficient c is a rational function of z and each slot
X(q) is one of: the constant 1 (initial term), G(z;q), G(1;q), G'(1;q)
for G a phase series (G' = ∂/∂s). Define the moment functions

    M_ph^{(r)}(s) = (q d/dq)^r F_ph(s;q) |_{q=1},      M^{(0)} = F_ph,

and D = s d/ds. Substituting q = e^ε and expanding, a slot term satisfies

    c(se^ε)·G(se^ε; e^ε) = Σ_{a,b} (ε^{a+b+m}/(a! b! m!)) D^m c · D^a M^{(b)}

(sum over m for the coefficient, a for the argument shift, b for the
q-slot), whence the ε^r coefficient times r! is

    Σ_{k=0}^{r} C(r,k) D^{r−k} [ c · M^{(k)} ] .

Slots G(1;q), G'(1;q) contribute the same with M^{(k)}(1), (M^{(k)})'(1)
(constants under D beyond the coefficient factor), and the initial term
contributes D^r[c_init]. Summing over the terms of each equation: the
level-r moment system is the LEVEL-0 OPERATOR SYSTEM applied to the
M^{(r)} plus a correction Σ_{k<r} C(r,k) D^{r−k}[Op_lin[M^{(k)}]] + D^r[init].
Using the level-k equations Op_lin[M^{(k)}] = M^{(k)} − I^{(k)} to
telescope, the correction collapses to the explicit inhomogeneity

    I^{(r)} = Σ_{k=0}^{r−1} (−1)^{r−1−k} C(r,k) D^{r−k} M^{(k)},           (7)

a finite alternating-binomial combination of D-derivatives of the
already-solved lower levels (I^{(1)} = D F, I^{(2)} = 2 D M^{(1)} − D² F,
I^{(3)} = 3 D M^{(2)} − 3 D² M^{(1)} + D³ F, ...). So:

    M00^{(r)}(s) = y M00^{(r)}(s)/(1−xs)² + I00^{(r)}(s)                    (E0r)
    M10^{(r)}(s) = y B[M00^{(r)}](s) + y C[M10^{(r)}](s) + I10^{(r)}(s)     (E1r)
    M11^{(r)}(s) = y D1[M00^{(r)}] + 2y D2[M10^{(r)}] + y L3[M11^{(r)}]
                   + I11^{(r)}(s)                                           (E2r)

with exactly the s03 operators B, C, D1, D2, L3 (boundary slots receiving
M^{(r)}(1), (M^{(r)})'(1)).

## 2. Kernel closure at every level

(E0r) is non-catalytic: M00^{(r)} = I00^{(r)}·(1−xs)²/((1−xs)²−y).

(E1r): multiplying by W(s) = (s−1)(1−xs) collects the SAME kernel
P_K(s) = (s−1)(1−xs) − ys as level 0. Substituting the power-series root
s0 (s0 −1 has positive valuation; the substitution lemma of
`convex-box-kernel.md` §2 applies verbatim — formal D-derivatives stay in
the substitution-legal space S) kills M10^{(r)}(s) and solves

    M10^{(r)}(1) = −[ y B[M00^{(r)}](s0) + I10^{(r)}(s0) ] · s0 / Q(s0),

Q the level-0 companion (king: xs(s−1)−s; control: −s). Back-substitution
gives M10^{(r)}(s) as an explicit rational function (the numerator
vanishes at s0 BY CONSTRUCTION, so the factor (s−s0) cancels exactly
against P_K = −x(s−s0)(s−s1); the cofactor P_K/(s−s0) = 1/s0 − xs has
unit constant term).

(E2r): same closing kernel (s−1)² − ys² with roots σ± = 1/(1∓u), u = √y:

    M11^{(r)}(1) ± u (M11^{(r)})'(1) = y D1[M00^{(r)}](σ±)
                                       + 2y D2[M10^{(r)}](σ±) + I11^{(r)}(σ±);

averaging gives M11^{(r)}(1) (the u → −u mirror swaps σ±, so the odd part
cancels — machine-asserted at every level), and the difference over 2u
gives (M11^{(r)})'(1). M11^{(r)}(s) follows since its numerator vanishes
at BOTH roots of the quadratic kernel (s−1)² − ys², which has unit
leading coefficient 1−y: exact polynomial division.

Assembly: M_r = M00^{(r)}(1) + 2 M10^{(r)}(1) + M11^{(r)}(1).

Induction over r: every denominator inverted is a product of atoms from
the FIXED level-0 set (all with unit corners at the substitution points),
every substitution point is one of s = 1, s0, σ±, and I^{(r)} is a
rational-D combination of lower levels — so each level stays in
Q(x, u, √Δ)(s), and each assembled M_r, being even in u (mirror
symmetry), lies in Q(x, y, √Δ). ∎

Uniqueness (level r solves the right problem): each operator carries a
factor y, so (E0r)–(E2r) determine the y^h coefficients of the M^{(r)}_ph
from the y^{h−1} coefficients plus lower levels — exactly one
power-series solution, and the ε-Taylor coefficients of the unique q-FE
solution satisfy the system; hence the kernel-derived solution is the
combinatorial moment GF.

## 3. Machine execution (`experiments/s08_moment_kernel.py`)

The construction is executed literally (truncated bivariate series in
(x,u), the s03 exact-series classes) for r = 0,1,2,3,4, king AND
polyomino, independently mod p1 = 2^61 − 1 and p2 = 10^18 + 9, with
checks:

  C0  level-0 output == brute-force-validated DP table f(w,h)
      (re-derivation of s03's solution by the same code path);
  C1  [x^w y^h] M_r == Σ_n n^r f(w,h;n) against the doubly-validated
      joint truth table `out_s04_area_truth.json` (boxes w,h ≤ 10),
      r = 1..4, both modes — every cell exact;
  C2  diagonal Σ_w [x^w y^{s−w}] M_r == a_r(s) against the independent
      r ≤ 4 moment DP (`out_s07_area_moments_r4_30.json`), r = 1..4;
  C3  M_1 · K²Δ⁴ == A + B√Δ for s07's CRT-lifted bivariate first-moment
      closed form (`out_s07_bivar_moment.json`; control: M_1 · Δ⁴) —
      checked by multiplication, exact on the full validity box.

Receipts: `out_s08_moment_kernel_16x16_r4.txt` (boxes to 16×16, both
61-bit primes) and `out_s08_moment_kernel_10x10_r4_big.txt` (prime
2^521 − 1 ≈ 10^157: a false coefficient match would require divisibility
by that prime — the compared integer coefficients are certified exactly).
ALL CHECKS PASS in every configuration.

## 4. Corollaries and status

1. **A_r(t) algebraic for all r** — with it, the s07 asymptotic
   moment-transfer inputs are derivation-backed: the fitted closed forms
   (r ≤ 2: `out_s07_moment_fit.txt`; r = 3,4: `out_s07_r4_fit.txt`) are
   pinned to the derived objects by C2/C3 plus their own
   registered-prediction holdouts on 30–36-digit terms.
2. **Identification caveat** (parallel to s03 §7 before its closure): the
   equality of the derived M_r with the specific small fitted closed
   forms is checked on finite coefficient boxes (exactly, incl. the
   2^521−1 run), not yet closed on a sufficient degree box by the
   s03-style degree-bound + specialization argument. The s04 exact-close
   machinery would mechanize this; nothing conceptual is missing.
3. **Denominator law** K^{r+1} Δ^{2r+2} (king; K = 1 control): confirmed
   by the fits at r ≤ 4; the construction exhibits the mechanism (each
   level applies D — which raises Δ-powers through s0 = ((1+x−y)−√Δ)/2x —
   and divides once more by the kernel companions) but the law is not yet
   extracted as a theorem. OPEN.
4. The limit-law constants E[area^r]/s^{2r} → (r!)²/((2r+1)! 2^r)
   (= moments of U(1−U)/2) are now confirmed at r = 3,4 by registered
   prediction (`out_s07_r4_fit.txt`); proving them for ALL r from this
   construction (singular expansion of the level-r recursion at t = 1/4)
   would prove the limit law. OPEN.
