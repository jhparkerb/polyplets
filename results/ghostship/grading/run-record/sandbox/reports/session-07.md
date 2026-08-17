DIRECTION: The full area distribution is (mechanism-)intractable, but its MOMENTS by semiperimeter should be algebraic — establish the total-area and higher-moment GFs on convex king animals as explicit closed forms in Q(t,sqrt(1-4t)) with registered-prediction holdouts + control, extract the area limit law; second front: certify the amplitude constant A (s06 OPEN c).
SHAPE: area moments are algebraic

Plan: (1) extend the validated box DP to carry area moments M_r(w,h)
alongside counts; validate against definitional brute force AND the s04
joint truth table, king and polyomino. (2) compute a_r(s) by
semiperimeter; fit radical ansatz (P+Q*sqrt(1-4t))/((2+t)^a (1-4t)^b) by
exact linear algebra; REGISTER predictions, then verify on freshly
computed held-out terms. (3) exact singularity analysis -> mean area,
variance, limit law of area/s^2. (4) interval-certify A =
-c1(q_c)alpha(q_c)/(K'(q_c)q_c). Report as I go.

## CARRY
CLAIM: area moment GFs A_r(t) of convex king animals by semiperimeter are ALGEBRAIC in Q(t,sqrt(1-4t)), denominator (2+t)^(r+1)(1-4t)^(2r+2); A_1,A_2 explicit; control (1-4t)^(2r+2), A_1^poly = P/(1-4t)^4 + 4t^4/(1-4t)^(5/2) | receipt: out_s07_moment_fit.txt, results/convex-area-moments.md | status: firm
CLAIM: every fitted closed form passed REGISTERED-PREDICTION holdout: predictions for a_r(s) written to disk BEFORE the DP data existed, 6-9 unseen 30-36-digit terms per sequence, two rounds (38..46, 47..52), zero failures | receipt: out_s07_predictions{,2}.json, out_s07_holdout_check{,2}.txt | status: firm
CLAIM: E[area]/s^2 -> 1/12, E[area^2]/s^4 -> 1/120, Var/s^4 -> 1/720, IDENTICAL for king and polyomino = moments of X=U(1-U)/2, U~Uniform(0,1) | receipt: out_s07_moment_asymptotics.txt | status: firm
CLAIM: bivariate M1(x,y) = (A+B*sqrt(D))/(K^2 D^4) [king], /D^4 [control], D,K the s02/s03 kernel objects; A,B small-integer polys banked; verified EXACTLY over Z on full [0..26]^2 grid; diagonal == univariate A_1 | receipt: out_s07_bivar_verify{,_poly}.txt, out_s07_bivar_moment{,_poly}.json | status: firm
CLAIM: box width: E[w|s]=s/2 EXACT, W_2(t) provably-algebraic and identified, Var(w|s)=s/8+O(sqrt s) SAME for both modes | receipt: out_s07_width_moments.txt | status: firm (s/8 numeric-limit from exact forms)
CLAIM: geometric limit picture: box concentrates at square (profile checked), fill ratio area/(wh) ->d 2U(1-U), density 1/sqrt(1-2rho) on (0,1/2) | receipt: out_s07_limit_law_prediction.txt + LOG profile table | status: tentative (moment-level only, r<=2 at write time)
VERIFY: s04 claim 1 joint truth table: independent moment-DP reproduces all r=0..4 moments on 100 boxes/mode + definitional brute force wh<=16 | outcome: confirmed | receipt: out_s07_area_moments.txt, out_s07_area_moments_r4_57.txt
VERIFY: s03 claim 4 (directed-convex king = A014300, A112029): fresh OEIS b-file fetches match 14/14 terms each at claimed offsets | outcome: confirmed | receipt: out_s07_verify_dirconv_bfiles.txt
OPEN: r=3,4 registered predictions (p_0(A_3)=9/256, p_0(A_4)=9/32, E[area^r]/s^2r=(r!)^2/((2r+1)!2^r)) — see out_s07_r4_fit.txt for verdict; if not present, DP57 died and the test is unfinished.
OPEN: PROVE A_r algebraic by the Temperley moment method: d/dq at q=1 of the proven q-FE gives linear FEs with the SAME kernel, inhomogeneities from lower moments — kernel roots close each level; would also prove the denominator law by induction (recipe in results/convex-area-moments.md).
OPEN: prove the fill-ratio limit law 2U(1-U) (all moments via the moment method above; or corner-cut bijection: U is plausibly a corner touch-position); amplitude certification s06 OPEN c still open (untouched).
DEAD: OEIS anchoring of control total-area seq 1,4,22,124,706,3968,...: /search AND entry pages Cloudflare-blocked (b-files still work); queries logged verbatim in LOG.
DEAD: naive integer-pole-only extraction of Var(w|s) coefficient (gives 7/12, 1/4 — WRONG; half-integer terms feed the s-coefficient through the ratio; must use full singular expansions).

## LOG

Session start. Read all six CARRY sections. Direction: area moments by
semiperimeter (new tractable statistics) + amplitude certification.

### Moment DP (experiments/s07_area_moments.py)
Extended the s01-validated row-interval DP (convex_box.g_table model) to
carry (count, sum area, sum area^2) per state; exact-width extraction by
the same second difference in w (valid: translation-invariant weights,
linear operator). Validations, all hard asserts, king AND polyomino:
  V1 definitional subset brute force (raw subsets, area=popcount), all
     boxes wh<=16, r=0,1,2;
  V2 r=0 == banked convex_box f(w,h) (w,h<=12);
  V3 == s04 joint truth table out_s04_area_truth.json (100 boxes/mode);
  V4 transpose symmetry.
Runs: SMAX=37 (out_s07_area_moments.{json,txt}), SMAX=46 (...46.*),
SMAX=52 (...52.*). a0 reproduces the banked semiperimeter sequences
(king s01, control A005436) — consistency with the proven r=0 forms.

king a1(s), s=2..13: 1,4,26,148,844,4704,25644,136856,716162,3681280,18619948,92820864
poly a1(s), s=2..13: 1,4,22,124,706,3968,21880,118192,625776,3251744,16610072,83537520
king a2(s), s=2..13: 1,8,78,632,4824,34616,236016,1540112,9675818,58812752,347275736,1998867408
poly a2(s), s=2..13: 1,8,70,560,4258,30680,210668,1385928,8778792,53778352,319849916,1853161480

### Fits (experiments/s07_moment_fit.py)
Ansatz (P+Q*sqrt(1-4t))/((2+t)^a(1-4t)^b) [control: a=0], exact Fraction
Gaussian elimination, ALL available coefficients used as equations
(consistency of the overdetermined system = internal holdout), smallest
(a+b+deg) accepted. Results (out_s07_moment_fit.txt):
  king A_1: (2+t)^2(1-4t)^4, degP=10, degQ=8, 25 surplus equations
  king A_2: (2+t)^3(1-4t)^6, degP=14, degQ=12, 17 surplus
  poly A_1: (1-4t)^4, degP=8 (Q=4t^4(1-4t) — so poly A_1 = P/(1-4t)^4
            + 4t^4/(1-4t)^{5/2}), 29 surplus
  poly A_2: (1-4t)^6, degP=11, degQ=9, 23 surplus
Denominator pattern (2+t)^(r+1)(1-4t)^(2r+2) extends the PROVEN r=0 forms
(s01 king: (2+t)(1-4t)^2; Delest-Viennot control: (1-4t)^2) — exactly the
Temperley-moment structure (each d/dq at q=1 raises kernel factor
multiplicities by (1,2)).

### Registered-prediction holdouts (experiments/s07_predict_holdout.py)
Phase 1: fits on s<=37 predicted a_1(38..46) king+poly and a_2(38..46)
poly — predictions written to out_s07_predictions.json BEFORE the SMAX=46
DP ran. Result: ALL MATCH (out_s07_holdout_check.txt).
Phase 2: fits on s<=46 (incl. king A_2, fitted on all 45 terms) predicted
all four a_r(47..52) — registered in out_s07_predictions2.json before the
SMAX=52 DP ran. Result: ALL MATCH (out_s07_holdout_check2.txt).
Every closed form has now correctly predicted >= 6 never-before-computed
~30-36-digit integers exactly.

### Asymptotics (experiments/s07_moment_asymptotics.py)
Exact u=1-4t singular expansions (Fraction arithmetic; r=0 forms are the
kernel-PROVEN s01/DV expressions). Leading constants:
  king: c0=1/128, c1=1/256, c2=1/128; poly: identical c0,c1,c2 (!).
  E[area]/s^2 -> (c1/c0)/3! = 1/12
  E[area^2]/s^4 -> (c2/c0)/5! = 1/120
  Var[area]/s^4 -> 1/720
Same constants for both families. These are the r=1,2 moments of
X = U(1-U)/2, U uniform on (0,1): E[U^r(1-U)^r]/2^r = (r!)^2/((2r+1)! 2^r).
Numeric sanity: multi-term singular expansion vs exact a_r(46): rel.err
1.5e-6 (r=2), 1.7e-3 (r=1); a0 poly exact to machine (the (1-4t)-part of
DV is a polynomial numerator — expansion truncates exactly).

### Width profile check (inline python, logged here)
f(w, s-w) at s=30 from the validated DP: concentrated bell at w=15
(128*f/4^s: 4.56 at t=1/2, 0.43 at t=0.37/0.63, ~0 beyond) — width/s is
NOT uniform; box concentrates at square. Hence the limit law reading:
area/s^2 = (wh/s^2)*fill -> (1/4)*rho with fill ratio rho ->d 2U(1-U)
(moments E rho=1/3, E rho^2=2/15 match exactly; density 1/sqrt(1-2rho)).

### Registered prediction for r=3,4 (out_s07_limit_law_prediction.txt)
Written BEFORE any r>=3 data existed: E[area^r]/s^(2r) = (r!)^2/((2r+1)!2^r)
=> p_0(A_3)=9/256, p_0(A_4)=9/32, both modes; A_3 denominator
(2+t)^4(1-4t)^8 [king]. Generalized DP r<=4 (s07_area_moments_r4.py,
validated V1/V3/V4 for r<=4 at SMAX=12) running at SMAX=57.

### Bivariate first-moment closed forms (s07_bivar_moment.py / _verify.py)
M1(x,y) = sum M1(w,h) x^w y^h over exact bounding boxes:
  king: M1 = (A + B*sqrt(D)) / (K^2 D^4), D=(1-x-y)^2-4xy, K=x+y+xy
  poly: M1 = (A' + B'*sqrt(D)) / D^4
Found by modular linear algebra at two primes (2^61-1 and
9223372036854775783), 306 unknowns vs 729 grid equations, UNIQUE +
consistent at both primes, CRT-lift gives small integers (max |coeff| 86).
Verified EXACTLY over Z on the full [0..26]^2 coefficient grid (729
coefficients, Fractions, no mod-p), and the diagonal x=y=t reproduces the
univariate A_1 fits exactly (A(t,t)=t^2 P_univ, B(t,t)=t^2 Q_univ king;
shift 0 for poly). Full polynomials in out_s07_bivar_verify{,_poly}.txt
and out_s07_bivar_moment{,_poly}.json. Bivariate denominator law:
K^(r+1) D^(2r+2) (king) / D^(2r+2) (control) — the proof target for the
kernel moment method.

### Width fluctuations (s07_width_moments.py)
w_1(s) = s*a0(s)/2 EXACTLY (x<->y symmetry; checked all s<=44, both
modes). W_2(t) = sum_s sum_w w^2 f(w,s-w) t^s is PROVABLY algebraic
(= (x d/dx)^2 F at x=y=t, F proven): identified exactly:
  king: [P+Q*sqrt(1-4t)]/((2+t)^3(1-4t)^4), degP=11 (surplus 21)
  poly: [P+Q*sqrt(1-4t)]/(1-4t)^4, degP=8 (surplus 27)
Var(w|s) = W_2-part/a0 - s^2/4 evaluated via exact singular expansions at
s=10^3..10^6: Var/s -> 0.12499881 (s=1e6), both modes: Var(w|s) = s/8 +
O(sqrt s), SAME constant for king and polyomino. CAUTION: a naive
integer-pole-only extraction gives wrong s-coefficients (7/12, 1/4) —
the half-integer (sqrt) terms of BOTH numerator and a0 contribute at
order s through the ratio; earlier printed values superseded by the
receipt's large-s table. Direct DP check at s=44: Var=5.1123 (king),
5.1132 (poly) — consistent with s/8 + O(sqrt s).

### Exact DV-style formula, control total area (out_s07_poly_exact_formula.txt)
From A_1^poly = P/(1-4t)^4 + 4t^4(1-4t)^(-5/2):
  a1(s) = sum_k P_k C(s-k+3,3) 4^(s-k) + (4/3)(2m+1)(2m+3)C(2m,m), m=s-4
verified exactly for all s=2..52 (inline python; first attempt FAILED due
to integer-division-before-multiply bug 4*(2m+1)*(2m+3)//3*C — the //3
must come after multiplying by C(2m,m); corrected and all-match).

### finite-s convergence sanity (inline)
(E[area]/s^2 - 1/12)*sqrt(s) at s=12..52: 0.139, 0.133, 0.136, 0.139,
0.142 — flat, confirming E/s^2 = 1/12 + c/sqrt(s) + o(1/sqrt s), c~0.14.

### VERIFY of s03 claim 4 via fresh b-files (s07_verify receipt)
Fetched https://oeis.org/A014300/b014300.txt and
https://oeis.org/A112029/b112029.txt (b-files bypass the Cloudflare
block). s03's banked directed-convex king sequences match both, at the
claimed offsets, 14/14 terms each. Receipt:
out_s07_verify_dirconv_bfiles.txt.

### OEIS queries (verbatim; searches Cloudflare-blocked, b-files OK)
  curl -s -m 30 "https://oeis.org/search?q=1,4,22,124,706,3968,21880,118192,625776&fmt=json"
    -> "Just a moment..." Cloudflare challenge page (blocked)
  curl -s -m 30 "https://oeis.org/A014300/b014300.txt"   -> OK (b-file served)
  curl -s -m 30 "https://oeis.org/A112029/b112029.txt"   -> OK (b-file served)
  curl -s -m 30 "https://oeis.org/A005436"
    -> same block (entry pages also blocked; s06's note said b-files work)
Control total-area sequence 1,4,22,124,706,3968,... therefore unanchored
to OEIS this session; its anchor is the definitional brute force V1 +
truth-table V3.
