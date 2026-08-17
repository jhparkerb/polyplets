DIRECTION: Take s02's handoff: derive the row-adding functional equation for convex king animals, validate it exactly, then PROVE the fitted bivariate closed form F(x,y) by the kernel method — and close the identification on a provably sufficient degree box.
SHAPE: functional equation + kernel proof

Plan: (1) re-derive the phase-transfer structure (unimodality parse) as an
explicit transition system with catalytic variable s = last-row length and
incremental box-width x-weights; validate cell-by-cell against the
brute-force-validated DP, king and polyomino modes. (2) Sum the transitions
into a functional-equation system; solve by the kernel method (kernel roots
s0 for the staircase phase, sigma_pm for the closing phase); execute the
elimination in exact truncated-series arithmetic mod two primes; check
against the DP table and s02's fitted equation. (3) Bound the degrees of the
final identification identity via a degree-bound semiring mirror of the
pipeline; close the identity on the full sufficient box by per-x
specializations. (4) Write docs/proofs/convex-box-kernel.md; mine the phase
decomposition for subfamily results (directed-convex king) + OEIS.

## CARRY
CLAIM: convex king animals satisfy the explicit 4-phase catalytic functional equation of docs/proofs/convex-box-kernel.md section 1; transitions reproduce the DP table f(w,h) for ALL w,h<=12, king AND polyomino modes, exact integers | receipt: out_s03_funceq_check.txt | status: firm
CLAIM: kernel method solves the FE: F(x,y) is ALGEBRAIC with explicit expression in Q(x,y,sqrt(Delta)) (eqs (1)-(6) of proof doc; kernels xs^2-(1+x-y)s+1 with disc=Delta, and (s-1)^2=ys^2); solution matches DP table (144 cells) + s02 equation at both primes, control included | receipt: docs/proofs/convex-box-kernel.md, out_s03_kernel_solve.txt | status: firm
CLAIM: identification F = -(M+2x^2y^2(1+x+y)^2 sqrt(Delta))/(2K Delta^2) CLOSED on full sufficient box: components deg<=(79,119) proven by degree-bound mirror; 84 specializations x=2..85 to u-deg 242, both primes, zero failures; s02 structural identities re-proved exactly over Z | receipt: out_s03_specialize_close.txt, out_s03_degree_bounds.txt | status: firm modulo stated mod-p caveat (proof doc section 7)
CLAIM: directed-convex king animals (phases (0,0)+(1,0), r non-decreasing) by semiperimeter = A014300(s-1); exact nxn box count = A112029(n-1) = Sum_k C(n-1+k,k)^2; verified exactly to 17x17; neither OEIS entry mentions animals — identifications new | receipt: out_s03_dirconv_verify.txt, results/directed-convex-king.md | status: firm
CLAIM: A014300's identity 2a(n)+a(n-1)=(3n-1)Cat(n-1) is the directed-subfamily instance of s02's 2a(s)+a(s-1) twist — independent confirmation that K=x+y+xy is the right kernel (K(t,t)/t=2+t forces the twist) | receipt: results/directed-convex-king.md | status: firm
VERIFY: s02 claim 1 (bivariate closed form algebraic, explicit) | outcome: confirmed — now DERIVED from combinatorics via kernel method, no fitting anywhere in the chain | receipt: docs/proofs/convex-box-kernel.md
VERIFY: s02 exact identities A2=Delta^4*K, A1=Delta^2*M, 4K*A0=M^2-Delta*S^2, disc=Delta^5*S^2 | outcome: confirmed over Z (no truncation) + closed form satisfies the quadratic by direct expansion | receipt: out_s03_specialize_close.txt (Part A)
OPEN: remove the mod-p caveat: rerun Part B of s03_specialize_close.py with Fraction arithmetic (est. hours in pure Python; or find a height bound). Everything else in the chain is exact.
OPEN: bijections behind the new identifications: A014300's "unimodal f:[n]->[n], f(i)!=f(i+1)" objects <-> king top boundaries; A112029 square-sum <-> king-path pairs (likely same mechanism as s02's N_h(1)=A153337 hit).
OPEN: AREA q-analog of the functional equation (mark each row q^k): the FE system is the natural Temperley vehicle to make convex-mirage's q-series nature a theorem — F00 stays solvable, kernels become q-deformed.
DEAD: closing the identification by one bivariate exact run at box (160,242): ~4h+ in pure Python (cost ~(box area)^2); per-x specializations achieve the same box in ~4 min.
## LOG

### Narrative

1. Read s01/s02 CARRY + results docs. s02's handoff: derive the column/row
   functional equation, check numerically, then kernel method with expected
   kernel K=x+y+xy. Corpus survey: no pre-banked staircase-subfamily pieces
   (directed-king-animals.md is the non-convex Bacher family).

2. Derived the transition system on paper from the validated row-interval
   model (l valley-unimodal, r mountain-unimodal, king reach l'<=r+1,
   r'>=l-1). Key structural facts: in phase (0,0) the last row spans the
   whole current box; king reach is AUTOMATIC inside phases and binds only
   at the strict-jump boundary cases i=k (l'=r+1, e>=1) — precisely the
   cases absent in polyomino mode. State = (phase, last-row length k);
   width tracked incrementally (x^ext). s03_funceq_check.py implements the
   raw sums independently of the DP: ALL 144 cells match in both modes.

3. Functional equations by geometric summation: divided-difference operators
   B, C (staircase, with king boundary terms xs*G1/(1-xs)) and D1, D2, L3
   (closing). F00 solves rationally: xys(1-xs)/((1-xs)^2-y). Staircase
   kernel (s-1)(1-xs)-ys: quadratic with discriminant (1+x-y)^2-4x = Delta
   EXACTLY (the classical staircase radicand appears for free). Closing
   kernel (s-1)^2=ys^2, roots 1/(1-+u), u=sqrt(y): Temperley-style; the
   two root-equations average to F11(1), odd u-powers cancel (checked).

4. s03_kernel_solve.py: the whole elimination in truncated bivariate series
   (x,u) mod p (box truncation is exact for retained coefficients; validity
   boxes shrink only at monomial-corner divisions). Checks: operator unit
   tests vs raw sums; kernel-root residual = 0; val1(F10 SRat) == kernel
   formula; F table 144/144 both modes; s02 equation identity in box; two
   primes (2^61-1, 10^18+9). Runtime ~1.5 s. Control (polyomino) passes
   with the boundary terms dropped and companion Q(s)=-s instead of
   xs(s-1)-s (my first run failed exactly there — the king/polyomino
   difference is ONLY those boundary terms, a clean structural statement).

5. Rigor closing: s03_degree_bounds.py mirrors every field op in a
   degree-bound semiring over Q(x,u)[sqrt(Delta)] (denominators = formal
   products of actually-inverted atoms, LCM-style bounds on addition) =>
   final identity components deg <= (79,119); lex-min/Newton-polytope
   argument => sufficient verification box (160,242). Direct bivariate run
   at that box infeasible in Python, BUT per-x specializations are cheap:
   s03_specialize_close.py reruns the ENTIRE pipeline at x=c univariately
   (NX=0 reuse of the same code) for c=2..85 to u-deg 250. Delta(c,y) is
   never a square (disc_y=16c), so per-c vanishing to u-deg 242 kills both
   components; 84 > 79+1 values kill the x-dependence. Both primes, zero
   failures, ~4 min. Part A re-proves s02's structural identities exactly
   over Z (including exact division M=A1/Delta^2) and shows by direct
   expansion that the closed form satisfies the s02 quadratic.

6. Cherry from the phase decomposition: the (0,0)+(1,0) subfamily =
   directed-convex king animals. Control reproduces the classical central
   binomials C(2s-4,s-2) and C(2n-2,n-1)^2 (definition is the right
   analog); king versions hit A014300 (semiperimeter) and A112029 (square
   box) — both entries tree/binomial-theoretic, no animal interpretation:
   new combinatorial identifications, verified exactly to 17x17 boxes
   (s03_dirconv_verify.py). A014300's 2a(n)+a(n-1)=(3n-1)Cat(n-1) mirrors
   s02's twist — the kernel K's diagonal (2+t) seen in a 1990s OEIS entry.

### Dead ends / gotchas

- Validity-box bookkeeping: additions keep dict terms beyond the min
  validity box; is_zero/divexact must ignore out-of-box terms or you get
  phantom failures (first F10(1) consistency "FAIL" was exactly this).
- Control mode differs from king in TWO places (B operator boundary term
  AND the companion polynomial Q(s) in the F10 elimination); forgetting the
  second gives a control that fails while king passes.
- Degree-bound semirings need LCM-style denominator handling (formal atom
  products), else repeated additions inflate bounds exponentially.
- pdivexact over Z[x,y]: for EXACT division, lex-leading-term long division
  terminates with componentwise-divisible leads at every step; assert it.
- M's diagonal cross-check: drop zero-sum entries before comparing dicts
  (degree-8 diagonal terms of M cancel).
- Fraction-exact closure of Part B estimated hours (Fraction ~100x mod-p);
  left as the single OPEN caveat rather than blowing the compute budget.

### OEIS queries (verbatim)

1. curl -s -A "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0" "https://oeis.org/search?q=1,2,7,24,86,314,1163,4352,16414,62292,237590&fmt=json"
   -> A014300 (nodes of odd outdegree in ordered rooted trees; GF 2z/(1-4z+(1+2z)sqrt(1-4z))). All 14 computed terms match.
2. curl -s -A "(same UA)" "https://oeis.org/search?q=1,5,46,517,6376,82994,1119210,15475205&fmt=json"
   -> A112029 (Sum_{k=0..n} C(n+k,k)^2). All 14 computed terms match.
3. curl -s -A "(same UA)" "https://oeis.org/search?q=2,7,24,86,314,1163,4352,16414,62292&fmt=json"
   -> A014300 again (shift check).
4. curl -s -A "(same UA)" "https://oeis.org/search?q=id:A014300&fmt=json"
   -> formulas/comments fetched (binomial formula, twist identity, unimodal-function comment).
5. curl -s -A "(same UA)" "https://oeis.org/search?q=id:A112029&fmt=json"
   -> formulas fetched (asymptotics 2^(4n+2)/(3 pi n), P-recurrence).

### Handoff pointers

Primary artifact: docs/proofs/convex-box-kernel.md — the complete derivation
with per-step verification status; scripts s03_funceq_check.py,
s03_kernel_solve.py (importable; solve(king, xval) supports specialization),
s03_degree_bounds.py, s03_specialize_close.py, s03_directed_convex.py,
s03_dirconv_verify.py. The three OPENs above are sized for a session each:
(a) exact-Q Part B is pure engineering (background-friendly, chunk by c);
(b) the two bijections are self-contained combinatorics with strong hints;
(c) the AREA q-deformation of the FE is the strategic one — the FE was
built for it: q-mark row lengths, F00 stays explicit (q-geometric), the
kernels become q-kernels; even partial q-structure (e.g. a q-functional
equation with numerically-checked solution) would convert the mirage's
"area is q-series-hard" from empirical to structural. The semiperimeter /
box statistics on this family are now DONE (s01 fit -> s02 bivariate fit ->
s03 proof); tractability boundary precisely located at the area statistic.
