DIRECTION: Take session 01's handoff: independently verify its semiperimeter results with fresh brute force, then establish the bivariate box GF F(x,y) (algebraic?) and hunt the exact binomial closed form for a(s) and the N_h(x) row-numerator structure.
SHAPE: verify + bivariate structure

Plan: (1) from-scratch brute-force enumerator (independent of convex_box.py)
for convex king animals in a w-by-h box; verify f(w,h) for wh<=16 and a(s)
for s<=10. (2) Extract row GFs R_h(x)=N_h(x)/(1-x)^(2h-1) from the 38x38
table; pattern-hunt N_h; OEIS the families. (3) Fit an algebraic equation for
F(x,y)=sum f(w,h)x^w y^h by modular linear algebra + rational reconstruction,
with the convex-POLYOMINO table as literature-anchored control; verify on
held-out coefficients; extract discriminant/radical closed form. (4) Exact
Delest-Viennot-style coefficient formula. (5) Bank receipts + writeup
(results/convex-box-bivariate.md).

## CARRY
CLAIM: F(x,y)=sum f(w,h)x^w y^h is ALGEBRAIC: F = -[M + 2x^2y^2(1+x+y)^2 sqrt(D)]/(2KD^2), D=(1-x-y)^2-4xy, K=x+y+xy, M explicit deg-8 (out_s02_KM.txt); unique quadratic (degs 10/14/18), exact holdout ALL 780 coeffs i+j<=38 | receipt: results/convex-box-bivariate.md, out_s02_bivar_king.txt | status: firm
CLAIM: s01's univariate mystery factors explained: (2+t)=K(t,t)/t, (1+2t)^2=(1+x+y)^2 at x=y=t; specialization reproduces s01 closed form exactly and annihilates all 200 terms | receipt: out_s02_bivar_analysis.txt, out_s02_closed_form.txt | status: firm
CLAIM: control (convex polyominoes) same pipeline: A2=Delta^4 i.e. K=1, disc=64x^4y^4 Delta^5 -> king novelty is EXACTLY kernel K=x+y+xy + weight (1+x+y)^2 vs 4 | receipt: out_s02_bivar_control.txt, out_s02_control_structure.txt | status: firm
CLAIM: Delest-Viennot analog: 2a(s)+a(s-1) = (18s+49)4^(s-5) - (9n^2-3n-1)/(2n-1)*C(2n,n), n=s-3, verified s=5..199; b(s)=2,5,20,81,344,... NOT in OEIS | receipt: out_s02_exact_formula.txt | status: firm
CLAIM: N_h(x)=(1-x)^(2h-1)R_h(x) is an integer polynomial of degree 2h-1 for h<=18 (extends s01 h<=5); table banked | receipt: out_s02_rowgf.txt | status: firm
CLAIM: leading coeff of f(w,h) in w = [h*4^(h-1)-2(h-1)C(2h-2,h-1)]/(2h-2)!; N_h(1) IS OEIS A153337 (zig-zag=king paths in square), 18/18 terms — resolves s01 OPEN | receipt: out_s02_fingerprints.txt | status: firm
CLAIM: N_{2k}(-1)=(-1)^(k+1)*4*N_k(1) (k<=9) and N_{2k+1}(-1)=(-1)^k(2k+1)4^k (k<=8) | receipt: out_s02_fingerprints.txt | status: tentative (finite check, no mechanism)
VERIFY: s01 claim 1+2 (a(s) sequence & closed form path): independent definitional brute force (raw subsets + interval-DFS w/ BFS, no DP machinery) matches all f(w,h) wh<=16 and a(s) s=2..10 | outcome: confirmed | receipt: out_s02_brute_verify.txt, out_s02_brute_s10.txt
VERIFY: s01 claim 4 (row polynomiality): confirmed and extended to h<=18 via zero-checks on N_h coefficients | outcome: confirmed | receipt: out_s02_rowgf.txt
OPEN: PROVE the bivariate closed form via kernel method (K=x+y+xy is surely the kernel root of the column-adding functional equation; this subsumes s01's univariate proof OPEN).
OPEN: bijective proof lead_h*(2h-2)! = A153337 (top/bottom king-path-pair dominance at w->infty); explain N_{2k}(-1)=+-4N_k(1) (height-halving at x=-1).
OPEN: is F(x,y) with an area catalytic variable q Temperley-solvable? (A_H(q) numerator pattern from s01 still unmined.)
DEAD: Ehrhart-style reciprocity probe: f(-w,h) matches neither king nor polyomino tables under simple shifts (f(-4,7)=0 hints at sign/zero structure); inconclusive, low priority | receipt: out_s02_reciprocity_probe.txt
## LOG

### Narrative

1. Independent verification first (s02_brute.py): raw 2^(wh) subset
   enumeration with definitional predicates (row/col contiguity, BFS king
   connectivity, 4-side touching) — deliberately none of convex_box.py's
   interval/phase/reach machinery. All wh<=16 boxes match banked; interval-DFS
   variant (col-convexity pruning + BFS at leaves) extends to a(s)=banked for
   s<=10 (a(10)=55570, boxes up to 5x5). s01's DP is definitionally correct.

2. Row GFs (s02_rowgf.py): N_h(x) integer polys deg 2h-1, h<=18, with 3-37
   verified zero coefficients each beyond the degree (polynomiality of
   f(w,h) in w now firm through h=18). Fingerprints: N_h(1)=1,4,24,136,720,...
   -> OEIS A153337 EXACT HIT (18/18 vs their b-file terms, closed form
   h*4^(h-1)-2(h-1)C(2h-2,h-1)); note the OEIS object is zig-zag paths =
   KING paths — structurally right (w->infty box dominated by top/bottom
   profile pairs). Resolves s01's "1, 2, 1, 17/90, 1/56 unidentified".
   Bonus fingerprints at x=-1 (see CARRY claim 7), spotted by eye from the
   printed table, machine-verified in out_s02_fingerprints.txt.

3. Bivariate fit (s02_bivar_fit.py -> generalized s02_bivar_fit2.py):
   linear system on series coefficients mod p=2^61-1, nullspace, rational
   reconstruction, then EXACT bigint holdout on all table coefficients.
   Gotcha #1: excluding i+j<2 equations left A0's constant unconstrained ->
   spurious "solution" A0=1. Include ALL coefficients from (0,0).
   Gotcha #2: underpowered budgets give nullspace dim >> 1 and garbage
   (control at TFIT=24 gave dim 24); raise TFIT until dim=1 before believing
   anything. King NONE at degs (6,9,12) and (9,13,17) was a power issue
   resolved at (10,14,18) — s01's "check the var/equation budget" lesson
   re-learned bivariately.
   Control (polyomino mode of the validated DP) fitted FIRST at (8,12,16):
   unique, holdout-exact i+j<=34 — pipeline is literature-anchored.
   King: unique at (10,14,18), holdout-exact i+j<=38 (780 coefficients,
   ~200 of them pure holdout beyond the fitted diagonals).

4. Analysis (s02_bivar_analyze.py, s02_closed_form.py): disc = Delta^5 * S^2,
   S=2x^2y^2(1+x+y)^2, exact bivariate square-root extraction; radical form
   verified as series identity 2*A2*F+A1 = -S*Delta^2*sqrt(Delta) to total
   degree 30 (sqrt by Newton on series, exact Fractions); A2=Delta^4*K with
   K=x+y+xy; A1=Delta^2*M, M deg 8; consistency identity 4KA0=M^2-Delta*S^2
   exact. Specialization x=y=t: matches s01's F(t) term-for-term
   (-M(t,t)=2t^3*(2-10t+14t^2-5t^3-4t^4), K(t,t)=t(2+t)).

5. Exact coefficient formula: (2+t)F(t,t) has pure (1-4t)^k denominators, so
   b(s)=2a(s)+a(s-1) is clean. Hand partial-fractions had an LCD slip
   (first formula failed at s=6 — caught by the 200-term check); corrected
   b(s)=(18s+49)4^(s-5) - (9n^2-3n-1)/(2n-1) C(2n,n), n=s-3: matches ALL
   s=5..199. This is the king analog of Delest-Viennot
   p(n+2)=(2n+11)4^n-4(2n+1)C(2n,n); the twist 2a(s)+a(s-1) is forced by
   the K kernel.

### Dead ends / gotchas
- The two fitting gotchas above (equation range; nullspace-dim discipline).
- Reciprocity probe f(-w,h): extrapolated values 4,15,67,216 (h=3) sit
  close to but NOT equal to polyomino row 13,68,222 — tempting near-miss,
  do not chase without a mechanism. f(-4,7)=0 is the one intriguing datum.
- Hand partial fractions: trust nothing unverified against 200 terms.

### OEIS queries (verbatim)
1. curl -s -A "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0" "https://oeis.org/search?q=1,4,24,136,720,3624,17584,83024,383904,1746280&fmt=json"
   -> A153337 (zig-zag paths, formula n*2^(2n-2)-2(n-1)*binomial(2n-2,n-1)); our 18 terms all match.
2. curl -s -A "(same UA)" "https://oeis.org/search?q=20,81,344,1490,6500,28396,123880&fmt=json"
   -> null (b(s)=2a(s)+a(s-1) NOT in OEIS).

### Handoff pointers
Primary writeup: results/convex-box-bivariate.md (equation JSON:
out_s02_bivar_eq_king_D2.json; control JSON alongside). The kernel-method
proof is now THE open item and it is well-posed: reproduce the column-adding
functional equation for interval-pairs with king reach + unimodality phases,
two catalytic variables; the kernel should be K=x+y+xy up to units, the
algebraic solution -(M+S*sqrt(Delta))/(2K*Delta^2) is the target. A
session-03-sized first move: derive the functional equation and CHECK it
numerically against the banked table before attempting the kernel algebra.
Everything fitted here is exact-holdout-validated but unproven.
