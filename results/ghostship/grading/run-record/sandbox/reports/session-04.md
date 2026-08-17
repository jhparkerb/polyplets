DIRECTION: Take s03's strategic OPEN: q-deform the proven functional equation by area (q marks cells), solve it Temperley-style into explicit q-series, and validate the resulting area GF against the banked mirage sequence — making "area is q-series, not algebraic" structural. Side thread: exact-Q closure of s03's mod-p caveat.
SHAPE: area q-Temperley solution

Plan: (1) derive the q-FE (every s03 operator formula at z:=qs, G(1), G'(1)
fixed); validate raw q-transitions against a doubly-computed ground-truth
joint table f(w,h;n). (2) Solve by q-iteration: F00 explicit q-product
series; F10(1)=alpha/(1-beta); F11 via a 2x2 unit-determinant system using
dual numbers s=1+eps; all in truncated Q[[q]] with x,y numeric. (3) Validate
jointly at 4 (x,y) points, then x=y=1 vs 50 transfer-matrix terms, control
vs OEIS b-files. (4) Corollary: fixed-height A_H(q) rationality mechanism.
(5) Background: rerun s03 Part B specializations with exact Fractions.
(6) Docs + OEIS.

## CARRY
CLAIM: the area-marked q-FE (s03 operators at z=qs, G(1),G'(1) unchanged) reproduces the joint table f(w,h;n) for ALL w,h<=10, every n, king+polyomino | receipt: out_s04_qfe_check.txt, out_s04_area_truth.txt | status: firm
CLAIM: F(x,y,q) has an explicit Temperley q-series solution (F10(1)=alpha(1)/(1-beta(1)), F11 by 2x2 unit system; docs/proofs/convex-area-q-temperley.md); matches joint truth at 4 (x,y) points and ALL 50 area terms vs fresh independent transfer matrix | receipt: out_s04_q_temperley.txt, out_s04_predict50.txt | status: firm
CLAIM: same solver, control mode, hits OEIS A067675 (convex polyominoes by area) and A067676 (directed convex by area) b-files 50/50 terms each — q-pipeline literature-anchored | receipt: out_s04_oeis_control.txt | status: firm
CLAIM: king directed-convex by area = 1,3,10,33,107,342,1084,... NOT in OEIS (new, 50 exact terms); phase-(0,0) subfamily = stacks A001523 with king constraints vacuous; mirage area sequence NOT in OEIS, extended 30->50 terms, a(50)=5736473632219682585431462 | receipt: out_s04_subfamilies.txt, out_s04_tm50.txt | status: firm
CLAIM: fixed-height rationality is now a mechanism-theorem (finite y-iteration of the explicit q-series => denominators (1-q^j),(1-xq^j) products); slices of F(1,y,q) match s01's banked A_1..A_4 exactly | receipt: out_s04_fixed_height_check.txt | status: firm
VERIFY: s03 claim 3 (identification closed, sole mod-p caveat) | outcome: confirmed — caveat REMOVED, exact over Q, 84/84 specializations, 44s wall | receipt: out_s04_exact_close.txt, addendum in docs/proofs/convex-box-kernel.md
VERIFY: s01 claim 5 (A_H(q) rational, cyclotomic denominators) | outcome: confirmed + mechanism established | receipt: out_s04_fixed_height_check.txt
VERIFY: s01/mirage 30-term area sequence | outcome: confirmed (independent convex_tm 50-term rerun + formula agree) | receipt: out_s04_tm50.txt, out_s04_predict50.txt
OPEN: extract mu=3.12894... exactly from the q-series (q->1- singularity analysis of alpha/(1-beta); the growth constant should be computable from the kernel of 1-beta(1)).
OPEN: normal-form alpha, beta, and the 2x2 system into named q-Bessel-type functions (Bousquet-Melou presentation) for the paper.
OPEN: PROVE non-D-finiteness of the area sequence — the explicit q-form makes this approachable (natural-boundary / infinitely-many-singularities argument).
DEAD: q-kernel-root substitution (no power-series root kills the F10(s)-F10(qs) coupling); q-adic iteration is the correct tool — do not retry kernel roots at q != 1.
## LOG

### Narrative

1. Read s01–s03 CARRY + docs/proofs/convex-box-kernel.md. Chose s03 OPEN (c)
   (area q-deformation, the strategic one) as main thread and OPEN (a)
   (exact-Q Part B) as background engineering. Machine: 80 cores.

2. Ground truth first (experiments/s04_area_truth.py): joint table f(w,h;n)
   computed two independent ways — definitional subset brute force (boxes
   wh<=16, HV-convex + connectivity + 4-side touch, area=popcount) and the
   s01-validated interval DP with rows weighted by length (w,h<=10, ALL
   areas). Cross-checked per-area; q=1 marginal == banked f(w,h); area
   marginal == banked mirage/control sequences. Both modes. 3s runtime.
   Banked as out_s04_area_truth.json.

3. q-FE validation (experiments/s04_qfe_check.py): the raw transition sums
   of s03_funceq_check.py with each new row of length k' also weighted
   q^{k'}. Matches the truth table on all 100 boxes, per-area, both modes.
   KEY DERIVATION FACT: every s03 operator formula is an identity in a free
   variable z evaluated at z=s; area-marking evaluates the SAME identity at
   z=qs (G(1), G'(1) stay — they extract the previous row's coefficients).
   So the q-FE costs nothing new combinatorially.

4. Background thread meanwhile: s04_kernel_solve_exact.py (line-for-line
   Fraction twin of s03_kernel_solve.py; sanity gate = exact bivariate run
   vs DP table, both modes OK) + s04_exact_close.py (Part A reused from
   s03_specialize_close — already exact over Z; Part B per-c worker,
   multiprocessing Pool of 60). Single-c probe at worst case c=85: 24.7s,
   passes exactly over Q. Full run: 84/84 specializations pass, 44s wall.
   s03's ONLY caveat is gone; addendum written into the kernel proof doc.

5. Main solver (experiments/s04_q_temperley.py): truncated Q[[q]] (Fraction
   coefficients) + dual numbers (s=1+eps) for the s-derivative at 1; all
   evaluation points are z=q^m(1+eps) with m>=1 wherever (z-1) is inverted,
   so every inversion is a unit in Q[[q]]. Iteration terms gain q-valuation
   n(n+1)/2 (staircase) / n(n+1) (closing) — q-adic convergence, loops are
   short. F10(1) = alpha(1)/(1-beta(1)); F11(1),F11'(1) from a 2x2 system
   with determinant 1+O(q). Checks all passed on first complete run (one
   trivial __rmul__ operator fix): joint at (1,1),(2,1),(1,3),(3,2) vs
   truth table n<=10 both modes; x=y=1 N=30 == banked mirage 30 terms
   (0.5s); control == known 14 terms + extension.

6. Predict-and-confirm at depth 50: convex_tm.py 50 (independent, validated
   transfer matrix) vs solver N=50 — all 50 terms agree (2s for the
   formula). Control at N=50 vs OEIS b-files: A067675 50/50, A067676
   (directed subfamily F00(1)+F10(1)) 50/50. The q-machinery is thus
   literature-anchored at depth 50, king results doubly confirmed.

7. Subfamilies (experiments/s04_subfamilies.py): phase (0,0) is identical
   king vs polyomino (constraints vacuous) == stacks == A001523 (verified
   also by a tiny independent nested-interval DP); king directed-convex by
   area is NOT in OEIS — new sequence with 50 exact terms and (via s03's
   A014300 semiperimeter hit) a two-statistic profile.

8. Fixed-height tie-back: exact Vandermonde interpolation in y of F(1,y,q)
   (15 solver runs, N=14) recovers s01's banked rational A_H(q), H=1..4,
   all 15 coefficients each. Combined with the finite-iteration structure
   of the solution, fixed-height rationality + cyclotomic denominators is
   now a theorem-with-mechanism rather than an observation.

9. Wrote docs/proofs/convex-area-q-temperley.md (theorem + derivation +
   verification ledger) and results/convex-area-q-series.md (summary +
   sequences + opens). The problem statement's tractability question now
   has a complete answer: box/perimeter statistics algebraic (s03, now
   fully exact), area statistic explicitly q-series-solvable (this
   session), q=1 degeneration singular term-by-term — the "resistance" of
   the area statistic is located precisely in the q->1 limit, not in the
   absence of a closed form.

### Dead ends / gotchas

- QS scalar ops: int*QS needs __rmul__ (one traceback, one-line fix). No
  other failures occurred in the whole session — the layered validation
  ladder (brute -> DP -> raw q-FE -> solver) meant each new artifact was
  tested against an already-trusted one.
- The q-operators must keep G(1), G'(1) UNdeformed (they read the previous
  row); q-deforming them too is the natural transcription error — caught by
  design in step 3 before any solver work.
- Dual-number bookkeeping: build points as Z(m)=q^m+q^m*eps (chain rule
  pre-encoded); never invert (z-1) at m=0 — the solution's structure keeps
  all such inversions at m>=1 automatically.
- Fraction cost is a non-issue at these depths (50 terms, 2s); no need for
  mod-p anywhere in the q-thread.

### OEIS queries (verbatim)

UA = 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'
1. curl -s -A "$UA" "https://oeis.org/search?q=1,2,4,8,15,27,47,79,130,209,330,512,784,1183,1765&fmt=json"
   -> A001523 (stacks / weakly unimodal compositions). Our F00 sequence.
2. curl -s -A "$UA" "https://oeis.org/search?q=1,2,5,13,33,82,200,481,1144,2699,6329,14775,34381&fmt=json"
   -> A067676 (fixed directed convex polyominoes with n cells).
3. curl -s -A "$UA" "https://oeis.org/search?q=1,3,10,33,107,342,1084,3417,10737,33675,105505&fmt=json"
   -> null (king directed-convex by area NOT in OEIS).
4. curl -s -A "$UA" "https://oeis.org/search?q=1,2,6,19,59,176,502,1374,3630,9312,23320,57279,138536,331032&fmt=json"
   -> A067675 (fixed convex polyominoes with n cells).
5. curl -s -A "$UA" "https://oeis.org/A067675/b067675.txt"  (b-file, 1000 terms)
   curl -s -A "$UA" "https://oeis.org/A067676/b067676.txt"  (b-file, 504 terms)
6. curl -s -A "$UA" "https://oeis.org/search?q=1,4,16,61,221,766,2566,8390,26982,85834,271174&fmt=json"
   -> null (convex king animals by area NOT in OEIS).
7. curl -s -A "$UA" "https://oeis.org/search?q=3,10,33,107,342,1084,3417,10737,33675&fmt=json"
   -> null (shift re-check of query 3).

### Handoff pointers

Primary artifacts: docs/proofs/convex-area-q-temperley.md (the theorem),
results/convex-area-q-series.md (summary), experiments/s04_q_temperley.py
(Solver class is importable; QS.N sets depth; Solver(x,y,king).solve()
returns the q-series; .F001/.F101/.F111 expose the phase pieces).
The three OPENs are sized for a session each: (a) the asymptotics OPEN is
the flashiest — beta(1) at q->1- controls mu=3.12894..., and the control
case has literature values to calibrate against (Bousquet-Mélou's convex
polyomino area asymptotics); (b) the q-Bessel normal form is symbolic
manipulation of the alpha/beta products, low-risk; (c) non-D-finiteness
proof is the hardest and would upgrade convex-mirage's empirical negative
to a theorem — the explicit q-form plus a natural-boundary argument is the
standard route. The s01–s03 statistics (box, semiperimeter) are DONE and
now fully exact; this session closes the "what is tractable" question —
what remains is sharpening (asymptotics, normal form, impossibility proof).
