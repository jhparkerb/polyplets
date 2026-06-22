# Growth constant and algebraic structure of A006770 (fixed polyplets)
(2026-06-22 — three parallel analysis hunts + a series fit. Data: a(n) to n=20, the
fixed-height GF denominators Q_H for H=1..10.)

## Growth constant lambda — bracketed to [7.12, 7.155]
Two independent methods:
- **Series-ratio** (`experiments/lambda_series.py`): r(n)=a(n)/a(n-1) fit vs 1/n is ~10x
  cleaner than vs 1/sqrt(n) (resid 3.4e-4 vs 3.3e-3) -> the sub-exponential correction is
  POWER-LAW, i.e. the **2D lattice-animal universality class** (like polyominoes), NOT a
  stretched-exponential (SAW) class. lambda -> 7.10 (free theta) / 7.12 (theta=1 imposed,
  stable across n=18..20), approached from BELOW. Correction exponent g -> -0.94 -> -1.
- **GF-pole Neville**: lambda_H = Perron root of the atom N_H (= 1/dominant pole of G_H):
  1, 2.4142, 3.4437, 4.1823, 4.7178, 5.1153, 5.4179, 5.6534, 5.8405, 5.9917 (H=1..10).
  Monotone, concave, ~1/H convergence; Neville extrapolation -> **7.155 from ABOVE** (still
  descending ~0.003/pt, so true lambda <= 7.155).

=> **lambda in [7.12, 7.155]**; CONJECTURE: a(n) ~ C * lambda^n * n^{-1} with theta=1 (2D
universality), lambda ~ 7.13-7.15. a(21)/a(22) would tighten lambda and directly test theta=1.
(lambda_2 = 1+sqrt(2), the silver ratio — the one closed-form per-height rate.)

## Structural identity — the lifetime-3 law, in degrees
**deg Q_H = deg N_H + deg N_{H-1} + deg N_{H-2}**, EXACT for all H=1..10 — a clean corollary
of lifetime-3 (each irreducible atom appears in exactly three consecutive denominators).
Atom degrees deg N_H = 1,2,4,9,29,68,181,462,1254,3289 grow geometrically ~ C*2.637^H (no
closed form / no low-order recurrence — it is a transfer-matrix state count).
REFUTES the old `deg Q_H = 2^H-1` guess in gf/fixed_height.py (holds only H<=4; 42 != 31 at H=5).
Atoms are pairwise coprime, squarefree, non-cyclotomic; leading coeffs 1,1,1,1,2,4,384 (a
candidate 2^{H-4} sub-pattern worth checking past H=7).

## Non-holonomic — rigorous negative
a(n) satisfies NO P-recurrence sum_k p_k(n) a(n-k)=0 up to order 8 (degree 7-8 at low order),
by an exact-rational nullspace search with a detector validated to find Catalan (order 1) and
Motzkin (order 2). No clean relation to A001168 (fixed polyominoes); inverse Euler/INVERT/
binomial transforms all leave OEIS-absent, non-simpler sequences. A006770 has no %F line in
OEIS. Confirms the believed non-holonomicity: a closed-form recurrence is NOT the route to reach.

## Reach lever (algorithm hunt)
R1 (vertical-mirror fold) is the ONLY lattice symmetry compatible with the directional column
sweep — 180-deg and transpose are provably incompatible (they map swept->unswept). The real RAM
levers are orthogonal to symmetry: R3 (u32 mod-p + CRT, ~1.7x) and B (blocked drain-and-free,
~1.9x). Practical stack **R1 x R3 x B ~ 6-8x RAM at 2-3x compute -> ~+2.2 terms** (a(22)/a(23)
in budget, a(24)/a(25) plausible); Phase-4 out-of-core removes the ceiling. R2 (ranged row) is a
confirmed compute trap (~100x). Engines built + gated on branches reach-modp-u32 (R3),
reach-blocked-store (B + OOC), reach-symmetry-fold (R1); unmerged. DEPLOY = merge + a production
driver that runs one sweep per CRT prime and combines.

## Literature check (2026-06-22) — novelty caveat
The asymptotic FORM (theta=1, a_n ~ C lambda^n / n, log divergence) is ESTABLISHED 2D
lattice-animal universality (Jensen & Guttmann, cond-mat/0007238; square tau=4.062570(8)) --
so theta=1 here is EXPECTED, not a finding; the g -> -1 fit only re-confirms known universality.
The king/NNN lambda VALUE is published in Mertens 1990 (J. Stat. Phys. 58, 1095) and
Mertens-Lautenbacher 1991 (the source of the A006770 enumeration), but both are paywalled,
Mertens' data page is unreachable, and OEIS carries no estimate -- the published figure could not
be retrieved here. NET: our 7.12-7.155 (n<=20, two methods) is consistent-with-universality but
UNCONFIRMED against the literature value. TO CLOSE: obtain the Mertens 1990 king growth constant
and check ours matches/improves it. (3 of the 4 thread-hunt findings turned out known/expected;
the genuine keeper is the reach lever R1xR3xB -> ~+2.2 terms.)

## Rigorous bounds on lambda (2026-06-22)
- LOWER (NEW, narrowed): Rands-Welsh / concatenation argument on the confirmed n<=19 series --
  the method Jensen used for the square lattice (tau >= 3.903). A*(u)=1/(1-P(u)) with
  p_n=[u^n]P >= 0 (renewal, verified to n=19); the positive root u* of the truncated P_N(u)=1
  gives lambda >= 1/u*. Result: **lambda >= 6.540** (n<=19, rigorous); 6.563 with the a(20)
  candidate. IMPROVES with terms (6.424 @ n<=15, 6.488 @ 17, 6.540 @ 19) -> converges up to
  lambda; a(21)/a(22) push it past ~6.6. Up from strip lambda_10 = 5.99 and Fekete
  a(20)^(1/20) = 5.63. Script: experiments/lambda_lower_bound.py.
- UPPER: lambda <= 15.83 (ancestor-exclusion, branch explore/theorem-lambda-bound, at its method
  floor ~15.56). LOOSE -- 2.2x the estimate; the weak side. A polyomino-style twig/Eden upper
  bound (~14% over truth on the square) would be the way to tighten it (-> ~8 if comparable).
- RIGOROUS INTERVAL: [6.54, 15.83]; series ESTIMATE 7.12-7.155 sits just above the (now ~0.92*lambda)
  lower bound. Narrowing further: more a(n) terms lift the lower bound; a better upper-bound method
  is the open task.

## Literature check RESOLVED (2026-06-22, both papers obtained -> papers/)
Read Mertens 1990 (J.Stat.Phys 58:1095) and Mertens-Lautenbacher 1991 (66:669) in full. NEITHER
estimates a growth constant -- both are enumeration/algorithm papers (counts + perimeter
polynomials). Mertens 1990 Table I gives the king (nnSquare) counts to s=14 == our a(1..14)
exactly (the A006770 source; clean cross-check of our engine vs the primary source).
Mertens-Lautenbacher 1991 does the TRIANGULAR lattice, not the king. They explicitly leave the
"analytic asymptotic theory of lattice animals" as open future work. CONCLUSION: there is NO
published growth constant for the king lattice. Our lambda ~ 7.12-7.155, rigorous interval
[6.54, 15.83], and the Rands-Welsh lower bound 6.540 are -- as far as the OEIS references and an
exhaustive web search show -- the FIRST characterization of it. (The theta=1 universality FORM
remains known/expected per Jensen-Guttmann; the king VALUE and bounds are the novel part.)

## Correction (2026-06-22): "first" overclaim withdrawn
Computing lambda from a(n)/a(n-1) is trivial, so a priority claim is unwarranted -- an informal
lambda ~ 7 very likely exists somewhere not surfaced here. Honest nuance: the communities holding
king-lattice data optimized DIFFERENT quantities. Percolation work targets the threshold p_c
(Mertens 1990 even tabulates the nnSquare mean-cluster-size series S(p)=sum b_r p^r, but its
singularity is p_c, NOT 1/lambda); the enumeration papers report only counts. So the *animal
growth constant* lambda may be genuinely under-attended for the king lattice -- but that is not
"first". Defensible claims only: (1) no lambda VALUE was found in OEIS, the Mertens enumeration
papers, or web/percolation searches; (2) ours uses n<=20, more terms than the best PUBLISHED
enumeration (n<=18), so it is plausibly the sharpest current estimate; (3) I have not seen the
Rands-Welsh / ancestor-exclusion bounds applied to the king lattice specifically. Treat all of the
above as "no published value located," NOT a priority claim.

## Clarification: 7.12-7.155 is an ESTIMATE spread, NOT a bracket containing lambda
The only interval PROVEN to contain lambda is the rigorous [6.54, 15.83]. The 7.12-7.155 is the
spread between two EXTRAPOLATIONS, neither a bound: (a) series-ratio of a(n)/a(n-1) -- the
1/n-corrected fit gives ~7.10-7.12 and is still drifting UP as the window narrows (not converged);
(b) GF-pole Neville on the per-height rates lambda_H (the lambda_H ARE rigorous lower bounds, 5.99
at H=10; their Neville extrapolation gives ~7.155, drifting DOWN). Both assume the theta=1
asymptotic form, neither has converged, and a(20) is a candidate. The ~0.5% agreement +
from-below/from-above drift SUGGEST lambda ~ 7.13, but lambda is NOT proven to lie in [7.12,7.155]
and could be slightly outside. Best point estimate ~7.13, no defensible error bar. Tightening
requires more confirmed terms (lower bound) + a real upper-bound method (15.83 is far too loose).
