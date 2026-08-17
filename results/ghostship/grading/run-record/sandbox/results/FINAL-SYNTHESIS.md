# Convex king animals: the complete tractability map (sessions 01–14)

Session 14 capstone. This document is the entry point to the 14-session
research loop on the problem statement:

> The area statistic on convex king animals resists a closed form. Find
> what is tractable in this family and establish it.

Object: convex king animal = HV-convex polyplet = sequence of row
intervals [l_i, r_i] with l valley-unimodal, r mountain-unimodal,
consecutive rows within king reach (l' ≤ r+1, r' ≥ l−1). Control family
throughout: classical convex polyominoes (same pipeline, column-overlap
adjacency), used to anchor every method against literature values.
Session reports: `reports/session-01..14.md`. Receipts: `out_*` files;
proofs in `docs/proofs/`; per-topic notes in `results/`.

## The answer, in one paragraph

The area statistic genuinely has no classical closed form — the area GF is
(empirically, at theorem-shape precision) non-D-finite — but everything
around it is tractable, and the boundary is now exactly located. By
semiperimeter the family is ALGEBRAIC with an explicit proven GF; the full
area GF has an explicit Temperley q-series closed form from which exact
terms, exact asymptotics (growth constant and amplitude, certified to 44+
digits), and the singularity structure all follow; and every area MOMENT
GF is algebraic (a theorem, with explicit closed forms at low order),
giving the scaling limit law area/s² → U(1−U)/2. The area statistic
resists a closed form exactly as the classical convex-polyomino area does
(Bousquet-Mélou q-Bessel status) — no worse, no better — and the king
modification is fully absorbed by one kernel object K = x+y+xy and one
weight (1+x+y)².

## Layer 1 — semiperimeter/box statistics: algebraic, PROVEN

- Bivariate box GF F(x,y) = Σ f(w,h) x^w y^h is algebraic, with explicit
  closed form F = −(M + 2x²y²(1+x+y)²√Δ)/(2KΔ²), Δ = (1−x−y)²−4xy,
  K = x+y+xy; DERIVED by kernel method from an explicit 4-phase catalytic
  functional equation, identification closed exactly over Q — no fitting
  anywhere in the final chain. (s01 fit → s02 bivariate fit → s03 proof →
  s04 exact closure; `docs/proofs/convex-box-kernel.md`.)
- Univariate a(s): 1, 2, 9, 36, 154, 668, ... (new to OEIS), algebraic GF,
  P-recursive, a(s) ~ (s/128)·4^s; Delest–Viennot-type twist
  2a(s)+a(s−1) = explicit binomial form (s01, s02).
- Fixed height h: counts polynomial in w of degree 2h−2; row GF
  numerators N_h with N_h(1) = A153337 (proven at GF level) and halving
  identities at x = −1 (proven). (s01, s02, s06;
  `docs/proofs/row-gf-specializations.md`.)
- Directed-convex king subfamily: semiperimeter GF = A014300 (shifted),
  n×n box count = A112029 = Σ C(n−1+k,k)²; identifications new to both
  entries. (s03; `results/directed-convex-king.md`.)

## Layer 2 — the area statistic itself: q-series closed form + exact
## asymptotics; non-D-finite

- Explicit Temperley solution: F(x,y,q) is a finite combination of four
  q-adically convergent q-series, derived from the q-deformed functional
  equation (proven mechanism; 50-term predictions verified against an
  independent transfer matrix; control mode hits A067675/A067676 b-files
  50/50). Fixed-height area GFs rational with cyclotomic denominators —
  now a mechanism theorem. (s04; `docs/proofs/convex-area-q-temperley.md`.)
- Exact asymptotics: a(n) ~ A·mu^n with mu = 1/q_c, q_c the smallest
  positive zero of K(q) = Σ (−1)^m (2−q^m) q^{m(m+1)/2}/(q;q)_m²;
  mu = 3.128943269730886252277447995387754160532... and
  A = 0.974452213135004649151329420860243327425... both CERTIFIED by
  exact-rational interval arithmetic (44+ digits), simple-pole certificate
  included; control values match all published Kotesovec/Klarner–Rivest
  digits at certified precision. (s05, s06, s10;
  `results/convex-area-asymptotics.md`, `out_s10_certify_amplitude.txt`.)
- Non-D-finiteness (the "resists a closed form" half): K(q) has ≥40
  located real zeros in (0,1) accumulating at q=1 following the
  oscillation law K(e^−ε) ≈ 2·3^{1/4}√(ε/2π) cos(V/ε − π/12), where
  V = 2Cl₂(π/3) is the figure-eight knot complement volume; F(1,1,q)
  has poles at these zeros (residues nonzero at the first four) — a
  D-finite GF would have finitely many singularities. Status: firm
  numerically, with the steepest-descent rigor gap explicitly scoped.
  (s05, s06; `results/K-oscillation-gieseking.md`.)

## Layer 3 — area moments: ALGEBRAIC for every r (theorem), with the
## limit law

- Temperley moment method: differentiating the proven q-FE at q=1 gives
  level-r linear functional equations with the SAME kernel; kernel roots
  close every level ⇒ M_r(x,y) ∈ Q(x,y,√Δ) for EVERY r. Machine-executed
  r ≤ 4 with three-prime verification. (s08;
  `docs/proofs/area-moment-kernel.md`.)
- Explicit closed forms A_r(t), r ≤ 4, denominators (2+t)^{r+1}(1−4t)^{2r+2}
  [king] / (1−4t)^{2r+2} [control]; every fit passed registered-prediction
  holdouts on unseen 30–36-digit terms. (s07, s08;
  `results/convex-area-moments.md`.)
- Limit law: A_r(t) ~ c_r/(1−4t)^{2r+2} with c_r = (r!)²/2^{r+7},
  confirmed r ≤ 12 (registered predictions, both modes) ⇒
  E[area^r]/s^{2r} → (r!)²/((2r+1)!·2^r), i.e. area/s² → U(1−U)/2 in
  moments to order 12, IDENTICAL for king and polyomino. (s09, s11/s12.)
- The c_r law DERIVED: at the quadruple collision on Δ=0 the moment
  recursion localizes to a 1-variable inner-chart profile recursion
  (psi/chi/phi chains), solved in closed form (Borel EGF), giving
  c_r = (r!)²/2^{r+7} for ALL r at leading order; curve-amplitude law
  C_r = (r!)² 2^{5r+3} (xy)^{(3r+5)/2} on Δ=0 derived by scaling
  covariance; king ≡ polyomino universality derived (all mode-dependent
  operators subdominant). Remaining gap: uniform-in-r subdominance
  (filtration induction). (s09, s12, s13;
  `results/convex-area-local-transfer.md`.)
- Session 14: the inner-profile machinery adjudicated at r = 7 and r = 8
  against registered predictions (chi_r, phi_r, psi00_r, orders
  −(4r+2)/−(4r+4)/−(4r+6), c_r) — see `reports/session-14.md` CARRY for
  the verdicts and receipts.
- Fine structure (firm empirical): ν_Δ(B_r) = ceil(r/2) multiplicity law
  for the √Δ-part numerators (r ≤ 12 slice, r ≤ 4 bivariate exact); king
  numerator degree law deg A_r = 6r+8 with even-r bump in deg B_r;
  B_1/Δ factors over s02 atoms but the shape does NOT persist for r ≥ 2
  (refuted s12 — Δ-multiplicity is the real structure). (s10, s12.)

## New sequences and constants (not in OEIS as of the loop)

- a(s) king semiperimeter: 1, 2, 9, 36, 154, 668, 2916, ...
  (`king_semiperim_200.txt`)
- twist b(s) = 2, 5, 20, 81, 344, ... (s02)
- king area sequence (convex-mirage) extended to 60 exact terms
  (`out_s05_terms60.txt`)
- directed-convex king by area: 1, 3, 10, 33, 107, 342, ... 50 terms (s04)
- q_c, mu, A, A_dir (king): certified digit strings in
  `out_s10_certify_amplitude.txt`; control asymptotics for A067676
  (amplitude 0.658955541852118959920998187900883420849...) also new.

## Rigor ledger (what would still need work for paper-grade claims)

1. THEOREM-GRADE now: Layer 1 entirely; q-FE + Temperley mechanism (s04);
   moment algebraicity for all r (s08); A153337 and halving identities
   (s06); certified constants (s06/s10, interval arithmetic).
2. FIRM with explicit registered-prediction evidence, mechanism derived
   at leading order: c_r law all r (gap: uniform-in-r subdominance
   filtration induction — s13 OPEN 1); curve law; universality.
3. FIRM empirical, mechanism scoped but unproven: non-D-finiteness
   (needs: (i) rigorous oscillation law for K near q=1 — steepest
   descent/Stokes; (ii) c1·alpha nonvanishing at infinitely many zeros);
   global denominator law K^{r+1}Δ^{2r+2}; ν-law ceil(r/2); even-r degree
   bump; figure-eight/quantum-modularity explanation of V = 2Cl₂(π/3).
4. Untouched: Bousquet-Mélou q-Bessel normal form of alpha, c1 (naming,
   not substance); bijective explanations (A014300/A112029/A153337 hits).

## Dead ends (do not retry)

Area P-recurrence (refuted repeatedly); sqrt(1+2t) radical ansatz (s01);
q-kernel-root substitution at q ≠ 1 (s04); Ehrhart reciprocity probe
(s02); fixed-atom factorization shapes for B_r, r ≥ 2 (s12); OEIS /search
endpoint via curl (Cloudflare-blocked — b-file URLs work).
