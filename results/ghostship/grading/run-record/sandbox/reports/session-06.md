DIRECTION: Three-front consolidation toward the non-D-finiteness prize: (1) upgrade s02's tentative N_h(-1) halving identities to proven via the x=-1 specialization of the kernel-proven closed form; (2) certified rational-interval enclosures of q_c and mu (s05 OPEN c); (3) q->1- saddle-point asymptotics of K(q) — explicit oscillation phase predicting the zero accumulation law (s05 OPEN a mechanism).
SHAPE: specialize, certify, oscillate

Plan: (A) Substitute x=-1 into the proven F(x,y) closed form: everything
lands in Q(y)[sqrt(1+4y^2)]; extract even/odd parts as exact rational
functions and prove/refute s02 claim 7, plus derive the N_h(1) GF from the
x->1 limit. (B) Certify q_c: exact Fraction evaluation of K(q) with proven
tail bounds, analytic positivity lemma on (0,0.29], Lipschitz march to a
sign-change bracket; interval inversion for mu. (C) Set q=e^-eps, find the
complex saddle of the alternating theta-Pochhammer sum, get the oscillation
law and validate its phase/amplitude/zero predictions against adaptive-
precision evaluations; audit s05's banked zeros against the law.

## CARRY
CLAIM: sum_h N_h(-1) y^h = (1/2)F(-1,4y) = (-y+4y^2-20y^3-32y^5)/(1+4y^2)^2 + 16y^4 sqrt(1+4y^2)/(1+4y^2)^2 exactly, and the s02 halving identities follow as polynomial identities for all k>=1 (N_1(-1)=-1 sole boundary exception) | receipt: docs/proofs/row-gf-specializations.md, out_s06_specialize_pm1.txt | status: firm
CLAIM: sum_h N_h(1) Y^h = Y/(1-4Y)^2 - 4Y^2(1-4Y)^(-3/2), forced by the exact expansion M(1-e,Ye^2) == -2Y e^5 (mod e^6); hence N_h(1) = h4^(h-1)-2(h-1)C(2h-2,h-1) = A153337(h) PROVEN at GF level | receipt: out_s06_specialize_pm1.txt | status: firm
CLAIM: q_c in (0.319596718059387465518602891982713923614508377387, +4e-46] CERTIFIED (exact-rational bracketing + Lipschitz march; smallest positive zero of K); mu = 1/q_c = 3.12894326973088625227744799538775416053209122... (44 certified digits) | receipt: out_s06_certify_qc.txt, experiments/s06_certify_qc.py | status: firm
CLAIM: K(e^-eps) = 2*3^(1/4) sqrt(eps/2pi) cos(V/eps - pi/12)(1+O(eps)) with V = 2Cl2(pi/3) = 2.029883212819307250... = hyperbolic volume of the figure-eight knot complement (A091518); saddle w=e^(-u*) is the 6th root of unity e^(-i pi/3), G=2iCl2(pi/3) pure imaginary; zeros at V/(pi eps_k) = k+7/12+O(eps); control J identical with 3^(-1/4), phase -pi/4, offset 3/4 | receipt: out_s06_saddle.txt, results/K-oscillation-gieseking.md | status: firm numerically (phase offsets to 1e-6/4e-8 by Richardson; zeros k=5..94; amplitude ratio -> 2 with slope -1/3); contour-level rigor open
CLAIM: zero census corrected: s05 banked #3..#25 = true indices 2..24; #26..#32 genuine at true indices 27,28,29,34,37,40,43 (12 zeros missed); #33..#37 are 110-digit-precision artifacts (off-lattice by 0.06..0.44); true zeros at k=46,57,63,78,94 located on-lattice to 5 decimals | receipt: out_s06_saddle.txt | status: firm
VERIFY: s02 claim 7 (N_{2k}(-1)=+-4N_k(1), N_{2k+1}(-1) formula) | outcome: confirmed — and upgraded tentative->PROVEN from the closed form | receipt: docs/proofs/row-gf-specializations.md
VERIFY: s02 claim 6 (N_h(1)=A153337) | outcome: confirmed — 18-term match upgraded to GF-level proof | receipt: out_s06_specialize_pm1.txt
VERIFY: s05 claim 1 (q_c, mu exact characterization + 40 digits) | outcome: confirmed — all banked digits certified, extended to 45/44 | receipt: out_s06_certify_qc.txt
VERIFY: s05 claim 7 (K has >=37 real zeros in (0,0.995), accumulating at 1) | outcome: confirmed with correction — count and accumulation stand (law predicts ~128 there; >=40 zeros now explicitly located), but banked #33..#37 locations are numerical artifacts and #26..#32 indices shift | receipt: out_s06_saddle.txt
OPEN: rigorize the oscillation law (steepest-descent contour + Stokes for the alternating theta-Pochhammer sum; the only empirically-fixed piece is the overall factor 2) — combined with c1*alpha nonvanishing at the zeros this makes non-D-finiteness of the area sequence a THEOREM; the target statement is now fully explicit with closed-form constants.
OPEN: WHY the figure-eight knot volume? The saddle at e^(i pi/3) is the same Li2 evaluation as V(4_1) — probe quantum modularity (Kashaev-type asymptotics of K,J on other roots-of-unity rays q -> zeta e^-eps).
OPEN: certify the amplitude constants A = 0.9744..., A_dir (needs interval evaluation of alpha, c1 at q_c) — remainder of s05 OPEN (c); and derive the O(eps) correction terms (measured: o_k drift coeff ~ -0.0026 king; amplitude slope -1/3 king, O(eps^2) control).
DEAD: none this session (all three fronts closed); note OEIS SEARCH is Cloudflare-blocked for curl — use b-file URLs (oeis.org/Axxxxxx/bxxxxxx.txt), which work.
## LOG

### Narrative

1. Read s01-s05 CARRYs. Chose: verify s02 claim 7 (only unverified
   tentative in the corpus), s05 OPEN (c) certification, s05 OPEN (a)
   mechanism. Report initialized before work.

2. Task A (experiments/s06_specialize_pm1.py -> out_s06_specialize_pm1.txt,
   all exact Fractions, ALL CHECKS PASS):
   - x=-1: K=-1, Delta=4+y^2, (1+x+y)^2=y^2; M(-1,y) = -16y+16y^2-20y^3-2y^5;
     branch check sqrt(Delta)|_{x=-1} = +sqrt(4+y^2) (agree at y=0).
     Phi(y)=(1/2)F(-1,4y) matches banked N_h(-1) h=1..18, closed form to y^44.
   - x->1: with x=1-e, y=Ye^2: Delta=e^2[(1-4Y)+2Ye+Y^2e^2]; the 19-term M
     expansion has e^0..e^4 ORDERS VANISHING IDENTICALLY and e^5 coeff -2Y;
     exact bivariate truncated series gives the limit G(Y) (no analysis
     needed: per-Y-coefficient rational function limits).
   - Halving identities reduce to: sqrt components identical on the nose
     ((1+4y^2)^(-3/2) = s/(1+4y^2)^2, height-halving = substitution Y=-y^2),
     rational components two tiny polynomial identities. The -2y odd
     correction is exactly the k=0 boundary (N_1(-1)=-1 vs formula +1),
     matching s02's observed k>=1 range.
   - Bugs caught en route: banked M(t,t) includes a cancelling degree-8
     diagonal (filter zeros); my first target GF had (1-4Y)^(-5/2) typo.

3. Task B (experiments/s06_certify_qc.py -> out_s06_certify_qc.txt, ~140s):
   rigor chain [R1] term-ratio bound 2q^2/((2-q)(1-q^2)^2) < 1 at q=0.34 =>
   alternating bracketing (terms decrease from m=1); [R2] K >= S_1 =
   (1-4q+2q^2)/(1-q)^2 > 0 on (0,29/100]; [R3] certified L=13.60 >= sup|K'|
   on [0.29,0.33] via termwise sup bounds tau_m*B_m + majorized tail (needs
   prod(1-q^j)^2 >= 1/4, checked exactly); [R4] 270-step Lipschitz march
   (step = Klo/L*(1-1e-6), points rounded down to 50 digits) certifies
   K > 0 on (0, a_f]; then K(a_f + 4e-46) < 0 certified. Enclosure width
   4e-46; q_c 45 digits, mu 44 digits, s05's 40 banked digits all confirmed.

4. Task C (experiments/s06_saddle.py -> out_s06_saddle.txt, ~5s): the
   summand exponent g(u) = -u^2/2 - 2Li2(e^-u) + pi^2/3 (u = m*eps) via
   (q;q)_m = (q;q)_inf/(q^{m+1};q)_inf + modular asymptotics of (q;q)_inf +
   EM half-term. Saddle equation u+2log(1-e^-u) = i pi exponentiates to
   w^2-w+1=0, w=e^-u: SIXTH ROOTS OF UNITY. G = g(u*)+i pi u* = 2i Cl2(pi/3)
   pure imaginary (the conjugate pairing with ReG=2pi^2/3 is not crossed --
   would exceed the termwise bound e^{1.97/eps}); g''(u*) = i sqrt(3);
   h~(u*) = sqrt(3)e^{-i pi/3} (king), e^{-i pi/2} (control). Predicted
   K ~ 2*3^(1/4)sqrt(eps/2pi)cos(2Cl2/eps - pi/12): phase and amplitude
   confirmed against Decimal evaluations at adaptive precision
   0.86/eps + 60 digits (the sum cancels from e^{1.97/eps} to O(sqrt(eps));
   this is also exactly why s05's fixed 110 digits corrupted zeros past
   q ~ 0.986). Factor 2 (both conjugate saddles per Poisson mode) was fixed
   empirically after extremum ratios converged to 2 (not 1) with clean
   (r-2)/eps -> -1/3; my single-saddle Gaussian bookkeeping is off by
   exactly that 2. Zero offsets: o_k -> 7/12 (Richardson diff 1.3e-6,
   drift -0.0026*eps), control -> 3/4 (diff 4e-8, drift O(eps^2)?).
   Pi via Machin; Cl2(pi/3) via the Bernoulli/zeta series
   Cl2(th) = th - th ln th + sum (-1)^(n+1) B_{2n}/(2(2n)!) th^{2n+1}/(n(2n+1)),
   cross-checked against A143298's b-file (51/51 digits).

5. Census: banked zeros mapped through the law; #3..#25 on-lattice
   consecutive (residual < 0.001), #26..#32 on-lattice with gaps totalling
   12 missed zeros, #33..#37 off-lattice (0.06..0.44) = artifacts. Fresh
   zeros at true k = 46,57,63,78,94 (q up to 0.993192) on-lattice to 5
   decimals. Note q(banked #37) = 0.9931637 vs true k=94 zero at 0.9931919:
   s05's last "zero" is 3e-5 from a genuine one — mislocated, not invented.

6. Docs: docs/proofs/row-gf-specializations.md (Task A) and
   results/K-oscillation-gieseking.md (Tasks B+C). Identification
   V = 2*Cl2(pi/3) = vol(S^3 \ 4_1) verified digit-for-digit vs A091518.

### OEIS queries (verbatim)

1. curl "https://oeis.org/search?q=1.0149416064096536250212025&fmt=text"
   -> BLOCKED (Cloudflare "Just a moment..." challenge page)
2. curl "https://oeis.org/search?q=2.0298832128193072500424051&fmt=text"
   -> BLOCKED (same)
3. curl "https://oeis.org/A143298/b143298.txt" -> OK; digits match my
   Cl2(pi/3) = 1.01494160640965362502120255427452028594168930753029 (51/51)
4. curl "https://oeis.org/A091518/b091518.txt" -> OK; digits match my
   2*Cl2(pi/3) = 2.02988321281930725004240510854904057188337861506059 (52/52)
   (A091518 = hyperbolic volume of the figure-eight knot complement)

### Handoff guidance

The non-D-finiteness theorem is now one rigorous-asymptotics paper section
away: prove K(e^-eps)*eps^(-1/2) = sqrt(2/pi)*3^(1/4) cos(V/eps - pi/12) + O(eps^(1/2))
by steepest descent on the Poisson-resummed integral (all constants are
closed-form; the empirical factor 2 will fall out of the correct contour
bookkeeping — check whether each mode's contour crosses BOTH saddles
e^{+-i pi/3}, or whether modes +-pi each contribute one saddle at full
weight). Then show c1*alpha != 0 at infinitely many zeros (s05 verified the
first four; the law gives you their locations to arbitrary precision).
Separately: the fig-8/quantum-modularity OPEN could reframe the whole area
statistic as a quantum invariant story — high risk, high reward.
