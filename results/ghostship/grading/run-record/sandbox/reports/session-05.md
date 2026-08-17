DIRECTION: Take s04's OPEN (a): extract the area growth constant mu=3.12894... exactly from the explicit q-Temperley solution (q->1- singularity of alpha/(1-beta)), with full asymptotic form a(n) ~ A*mu^n, calibrated against the convex-polyomino control's literature values.
SHAPE: singularity analysis of q-series

Plan: (1) put the Temperley denominator 1-beta into q-Pochhammer normal
form and verify symbolically against the s04 solver; (2) extend the exact
area sequences to n=60; (3) build a 110-digit Decimal scalar mirror of the
s04 solver = numeric analytic continuation of F(1,1,q) on (0,1); locate the
dominant pole q_c (smallest zero of the denominator), compute mu=1/q_c and
the residue amplitude; (4) control first: same machinery must hit the known
convex-polyomino-by-area constants; (5) verify the full asymptotic against
exact terms, including the second pole; (6) OEIS lookups; results doc.

## CARRY
CLAIM: mu(convex king by area) = 1/q_c EXACTLY, q_c = smallest positive zero of K(q)=sum_m (-1)^m (2-q^m) q^(m(m+1)/2)/(q;q)_m^2 = 2J(1;q)-J(q;q); mu = 3.128943269730886252277447995387754160532... , q_c = 0.319596718059387465518602891982713923614... (both NOT in OEIS) | receipt: out_s05_asymptotics.txt, results/convex-area-asymptotics.md | status: firm
CLAIM: a(n) ~ A*mu^n with A = -c1(q_c)alpha(q_c)/(K'(q_c)q_c) = 0.974452213135004649151329420860243327425...; rel.err +1.6e-16 at n=60 vs exact terms, decaying at exactly (q_c/q_2)^n | receipt: out_s05_asymptotics.txt, out_s05_terms60.txt | status: firm
CLAIM: 1-beta(1;q) at x=y=1 telescopes to K(q) [king] / J(1;q) [control]; exact series identity to q^40 vs solver beta | receipt: out_s05_beta_forms.txt | status: firm
CLAIM: control anchor is EXACT: J(q)=0 is the defining equation of the Klarner-Rivest constant A276994, and our control mu (2.3091385933304947310987203050172125319118...) and amplitude (2.9195985097136070553847095156513356859151...) match ALL ~70 published digits of Kotesovec's constants in A067675 | receipt: out_s05_asymptotics.txt | status: firm
CLAIM: directed subfamilies share mu (GF = F00 + alpha/K); amplitudes A_dir = -alpha(q_c)/(K'(q_c)q_c): king 0.375453020279924731743489243819072820707... (new), control 0.658955541852118959920998187900883420849... = asymptotics of A067676 (none published — new) | receipt: out_s05_asymptotics.txt | status: firm
CLAIM: F(1,1,q) is meromorphic in |q|<1 with simple poles at zeros of K: residue formula at second zero q_2=0.664430094083357809... predicts the subdominant term of a(n), confirmed vs exact terms (rel.err -1.1e-2 full / -2.8e-3 directed at n=60, shrinking); det(2x2) sign-constant and nonzero through (0,q_2] | receipt: out_s05_secondpole.txt | status: firm
CLAIM: K has >=37 real zeros in (0,0.995) (J: >=34), accumulating at q=1, residues nonzero at first four => F(1,1,q) has infinitely many poles in [0,1) numerically — D-finite functions have finitely many singularities | receipt: out_s05_zeros_scan.txt | status: firm (zero count is a lower bound; "infinitely many" is the open proof)
VERIFY: s04 claims 1-2 (q-FE + Temperley solution): full s04 validation suite rerun, all checks pass | outcome: confirmed | receipt: out_s05_beta_forms.txt
VERIFY: s04 claim 4 (50-term sequences): exact solver rerun at N=60 reproduces all 50 TM terms + banked 30; a(60)=515966960402732546167749372540 | outcome: confirmed | receipt: out_s05_terms60.txt
OPEN: non-D-finiteness is now two statements about explicit q-series: (i) K has infinitely many zeros in (0,1) [theta/q-Airy-type oscillation near q=1 is the likely mechanism], (ii) c1*alpha nonvanishing at infinitely many of them; either proven => the mirage negative becomes a theorem.
OPEN: q-Bessel normal form of alpha and c1 (denominator K is DONE — it IS the q-Bessel combination; the numerators remain unnormalized) — s04 OPEN (b) half-resolved.
OPEN: certified error bounds on the constants (current: 110-digit working precision, truncation 1e-100, bisection-converged; interval-arithmetic certification would make them citable digits).
DEAD: none — the singularity-analysis path worked without a failed branch this session.

## LOG

### Narrative

1. Read s01-s04 CARRYs + docs/proofs/convex-area-q-temperley.md +
   s04_q_temperley.py. Chose s04 OPEN (a) (exact mu), which also half-solves
   OPEN (b) (normal form) via the denominator.

2. Normal form (experiments/s05_beta_forms.py): from the solver's
   solve_F10 loop at x=y=1: beta = sum_n T(q^{n+1}) prod_{j<=n} R(q^j),
   R(z)=-z/(1-z)^2, T(z)=z(2-z)/(1-z)^2 [king] resp. z/(1-z)^2 [control];
   prod telescopes to (-1)^n q^(n(n+1)/2)/(q;q)_n^2. So 1-beta = K(q)
   [king] / J(q) [control], J = the classical q-Bessel-type series.
   Verified as exact Fraction series identity to q^40 against the solver's
   beta (subclass exposing alpha/beta), plus the K = 2J(1;q)-J(q;q)
   presentation. Also reran the whole s04 validation suite (VERIFY line).

3. Exact terms to n=60 (experiments/s05_terms60.py, 6s): king/control x
   full/directed. First 50 king terms match out_s04_tm50.txt (parsed
   separately), first 30 match the banked mirage list in-script.

4. Main analysis (experiments/s05_asymptotics.py): Decimal prec=110 dual
   numbers (a+b*eps) mirroring the s04 Solver method-for-method, loops
   truncated at 1e-100 — this evaluates all the q-series (alpha, beta, c0,
   c1, det) as ANALYTIC functions at numeric q in (0,1), beyond the series'
   radius q_c. Validation ladder: (a) NSolver's 1-beta vs independent
   closed-form K/J evaluation: agree to ~1e-108 at q=0.1, 0.3; (b) full
   F(0.1) = c0 + c1*alpha/K vs 60-term exact partial sums: difference
   EQUALS the estimated tail (2.35e-31 vs 2.3e-31 king; 5.6e-39 both,
   control) — the evaluator is exact to working precision; (c) pole
   residue vs (q_c-q)*F at q_c-1e-12: 11 digits.
   F is affine in the injected F10(1): two assemblies (F101=0,1) give
   c0, c1. Root of K by bisection to 1e-102. Scans: K>0 on (0,q_c) (31
   pts); det sign-constant, |det|>0.58 up to q_c. Amplitudes by residue.
   Asymptotic table: king a(n)/(A mu^n)-1 = 2.4e-10 (n=40) -> 1.6e-16
   (n=60), successive-error ratio 0.2336 per Delta-n=2 vs (q_c/q_2)^2 =
   0.2314 — subdominant rate nailed by the second zero.

5. OEIS: A067675's Kotesovec asymptotics matched digit-for-digit on BOTH
   constants (~70 digits each); A276994 (Klarner-Rivest) turns out to be
   DEFINED by our control equation J(q)=0 — the control anchor could not
   be stronger. Flajolet-Sedgewick p.662 has this constant wrong per the
   OEIS comment; worth citing carefully. King digit-searches: null (new).

6. Two-pole check (experiments/s05_secondpole.py): residue formula
   evaluated AT q_2 (NSolver runs fine there; det nonzero, sign-constant
   scan extended to (q_c,q_2]) predicts A2; empirical
   (a(n)-A*mu^n)/mu2^n from exact terms converges to it in all four
   sequences. F's meromorphic structure is confirmed at two distinct
   poles with one formula.

7. Zero census (inline script -> out_s05_zeros_scan.txt): 0.001-step scan
   finds 37 real zeros of K in (0,0.995) (34 for J), gaps (1-q_k)
   shrinking steadily => accumulation at 1 (count is a lower bound; the
   scan step undercounts near 1). c1*alpha != 0 at the first four zeros
   (values grow like 1/det: 1.3, -1.4e4, 2.4e8, -4.3e12). This is the
   sharpest available launchpad for the non-D-finiteness proof.

8. Wrote results/convex-area-asymptotics.md (summary table, provenance,
   route to impossibility proof).

### Gotchas for successors

- The tm50 receipt file is comma-separated prose, not "n a(n)" lines; my
  first parse silently found 0 terms (the assert against the in-code
  banked list still protected the run). Check parser hit counts.
- Decimal formatting: f-strings with :.2e/:.40f work on Decimal directly.
- The numeric mirror MUST clear the F10 cache between the two assemble()
  calls (F10_at depends on the injected F101) — same-shaped bug as s04's
  "q-deform G(1) too" trap.
- Near q=1 the K/J series need ~100+ terms and have large intermediate
  terms ((q;q)_m^2 ~ 1e-28 at q=0.95): prec 110 absorbs it; don't scan
  past 0.995 without raising prec.
- Bisection at prec 110: 400 iterations is cheap; don't bother with
  secant/Newton bracketing subtleties.

### OEIS queries (verbatim)

UA = 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'
1. curl -s -A "$UA" "https://oeis.org/search?q=id:A067675&fmt=json"
   -> Kotesovec: a(n) ~ c*d^n, d = 2.309138593330494731098720305017212531911814472581628401694402900284456440748..., c = 2.91959850971360705538470951565133568591516894147305658630679268977185945...; both match our computed values on all digits.
2. curl -s -A "$UA" "https://oeis.org/search?q=id:A276994&fmt=json"
   -> "Decimal expansion of the Klarner-Rivest polyomino constant"; defining equation = our J(q)=0; comment: Flajolet-Sedgewick 2009 p.662 value is wrong.
3. curl -s -A "$UA" "https://oeis.org/search?q=3,1,2,8,9,4,3,2,6,9,7,3,0,8,8&fmt=json"
   -> null (king mu NOT in OEIS).
4. curl -s -A "$UA" "https://oeis.org/search?q=3,1,9,5,9,6,7,1,8,0,5,9,3,8,7&fmt=json"
   -> null (king q_c NOT in OEIS).
5. curl -s -A "$UA" "https://oeis.org/search?q=id:A067676&fmt=json" and "...&fmt=text"
   -> entry has NO asymptotic formula (%N only relevant): our control-directed amplitude is new.

### Handoff pointers

Primary writeup: results/convex-area-asymptotics.md. Reusable machinery:
s05_asymptotics.py exports NSolver (numeric analytic continuation of the
whole s04 solution at any real q in (0,1), dual numbers included),
denom_series (K/J), find_root, load_terms. The impossibility-proof OPEN is
concrete: study K(q) near q=1 (Poisson/modular asymptotics of
theta-like sums with (q;q)_m^2 denominators — expect q-Airy oscillation)
to prove infinitely many zeros; then residue nonvanishing. A lighter
session: certify the constants with interval arithmetic and/or push the
zero census with adaptive stepping; also the alpha/c1 normal form
(s04 OPEN (b) second half) is untouched.
