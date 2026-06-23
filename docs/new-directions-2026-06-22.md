# New research directions — generated + falsified 2026-06-22

A deliberate hunt for directions OUTSIDE the in-flight threads (a(20→23) reach,
hole counts/GFs, lambda *bounds*, OEIS prep, lifetime-3). Rubric applied to each
idea: (1) try to prove it can't work, (2) test the survivors, (3) implement or
enqueue. Hunting grounds were the three under-exploited spaces the audit exposed:
the absent **series-analysis literature** (Guttmann differential approximants,
finite-size scaling), the unused **structural hooks** (site-perimeter, contact
marking), and the untouched **lattice families** (knight / reach-r) +
**cross-source** (not just cross-ISA) validation.

## KILLED at step 1 (proved can't work now)

- **D-finiteness test of the polyplet GF** (à la Rechnitzer/Guttmann "guessing").
  Distinguishing D-finite from non-D-finite needs ~40–50+ terms for any moderate
  ODE order; we have 20 (a(1..20)), and even pushing reach to a(26) won't get
  close. A negative guess at 20 terms is meaningless. Blocked on far more terms
  than reach can ever produce. KILL.
- **Polyplet = diagonally-glued polyomino pieces, as an exact enumeration method.**
  The rook-component decomposition is real (already observed: ~10 pieces, the
  perim=4n slice == A001168), but turning it into a *count* requires
  inclusion-exclusion over non-overlapping geometric gluings with a global
  king-connectivity constraint — intractable, strictly worse than the direct
  transfer matrix. KILL as a method (the structural observation is already done).
- **Universal amplitude ratios.** Too few terms to estimate amplitudes reliably. KILL for now.

## SURVIVED + TESTED — they work (implemented this session)

### 1. Finite-size scaling on the strip growth constants lambda_H  →  lambda ≈ 7.2
`experiments/lambda_fss.py`. The project had tried **Aitken** on the lambda_H
ladder, found it worse than direct a(n) ratio fits, and called the ladder slow /
sub-geometric. But Aitken assumes *geometric* convergence; 2D strip constants
approach lambda_infty as a **power law in 1/H**, which is exactly why Aitken
failed. Recomputed lambda_H exactly via integer series-ratio of P_H/Q_H (np.roots
overflows at H>=8 on the ~1e55 coefficients):

    H : 1, 2.4142, 3.4437, 4.1823, 4.7178, 5.1153, 5.4178, 5.6534, 5.8404, 5.9915
    (note H=10 = 5.9915, not the 5.940 quoted earlier in the log)

- **BST / Bulirsch-Stoer extrapolation: lambda_infty ≈ 7.221.**
- Single-power-law fits drift 8.74 → 7.69 as the fit uses higher-H tail (effective
  exponent p rising 0.55 → 0.82) — the simple form underfits with only 10 heights.

Verdict: an **independent** lambda ≈ 7.2 (strip constants, not term ratios),
consistent with everything else. The limiter is **only having H<=10**. H=11 is
landing now (the C1 GF recovery); the fixed-height GF engine can push further.
Each new height sharpens this. ENQUEUE: extend the lambda_H ladder (H=11 from C1,
then H=12..15) and re-run — should converge toward the DA value below.

### 2. Differential approximants on a(1..20)  →  lambda = 7.110 ± 0.02  (SHARPEST YET)
`experiments/series_da.py`. The field-standard tool (Guttmann), absent from the
repo, which estimated lambda only by ratio + Neville (7.10–7.15).

- **Inhomogeneous DA (K=1, K=2): lambda = 7.1101, std 0.0006** across 8 approximants.
- **Dlog-Padé: lambda ≈ 7.085–7.091** (well-converged approximants).

**theta is KNOWN, not fitted.** 2D lattice animals (all lattices, king included)
form one universality class with entropic exponent theta = −1 in the convention
a(n) ~ C·lambda^n·n^theta (the Parisi–Sourlas / dimensional-reduction result;
Jensen–Guttmann cite the square-lattice value). So theta should be **fixed at −1
as an input**, not estimated. The free Dlog-Padé residue gives theta ≈ −0.74
(range −0.79..−0.70) — this is NOT a finding, it is the textbook short-series bias
(exponents converge far slower than lambda), and it confirms we must bias rather
than free-fit.

**Biased estimator (theta = −1 fixed): lambda = 7.111.** lam_n = r(n)·n/(n−1)
converges monotonically as 1/n² (exactly the theta=−1 prediction): 7.207, …,
7.1206 at n=20; 1/n² Richardson → **lambda = 7.111**. The clean 1/n² behaviour is
itself a mild consistency check that theta = −1.

- Triangulation of all methods:

    rigorous interval        [6.54, 9.355]
    series ratio + Neville   7.10 – 7.15   (existing, unbiased)
    FSS on strips (new)      ≈ 7.2         (only H<=10; coarse)
    Dlog-Padé (new)          7.085 – 7.091
    inhomogeneous DA (new)   7.110 ± 0.001
    biased ratio theta=-1    7.111         (new, sharpest + simplest)
    -------------------------------------------
    NEW CENTRAL VALUE        lambda = 7.110 ± 0.005
    (biased-ratio 7.111 and free DA 7.110 agree to 0.001)
- **Prediction (ratio extrapolation, stable across windows):**
  **a(21) ≈ 6.954×10¹⁵, a(22) ≈ 4.726×10¹⁶** (lambda_eff ≈ 7.107). An independent
  cross-check on the multi-day reach runs: if exact a(21) lands far from
  ~6.95×10¹⁵, investigate.

This is paper-grade: DAs are what a math.CO/stat-mech referee expects to see for a
growth-constant claim, and they tighten our estimate AND give theta + an honest
error bar. Fold into the paper's growth section (#17) and the lambda timeline.

## SURVIVED step 1, NOT yet tested — ENQUEUE (cheap, high value)

3. **Site-perimeter invariant + FIRST cross-SOURCE validation (vs Mertens 1990
   perimeter polynomials).** We measure edge-perimeter to n=13 but never computed
   *site*-perimeter (# empty king-neighbours) — the natural variable in
   lattice-animal statistical mechanics and the one Mertens tabulates. Adding it to
   the g2 Redelmeier generator is a few lines (count empty king-neighbours per
   animal). Payoff: (a) a new sequence; (b) the project's **first cross-source**
   check — every validation so far is cross-ISA (same spec, different CPU), which
   cannot catch a shared specification error; reconciling our perimeter
   distribution against Mertens' published king-lattice perimeter polynomials
   would. Low cost, gympie-friendly.

4. **Extend A389193 (square-lattice / polyomino hole counts) with the existing TM
   holes engine (`square4 --holes`).** The holes engine already validates against
   A389193 at small n; A389193 is a recent (2025) sequence, almost certainly short.
   Running square4 --holes extends its b-file for free AND is a cross-LATTICE
   validation of the Euler/hole accounting. Low cost (engine exists).

5. **Knight / reach-2 growth constants via the SAME DA + FSS pipeline.** Engines
   exist (`cpp/gf_knight.cpp`, `gf_modp.cpp --vreach`). We have knight counts only
   to n=8 and no growth constant. Produce the knight fixed-height GF ladder + a DA
   estimate of lambda_knight (and reach-2), a parallel study to the king lattice
   using the two scripts written today. Medium cost; novel lattice family, likely
   new OEIS sequences.

6. **Diagonal-contact density c ≈ 0.743 EXACTLY (T6), via a contact-marked GF.**
   Currently only a sampling estimate. Mark diagonal contacts with a variable in
   the fixed-height transfer matrix; the mean per cell is then a derivative of the
   marked GF at the dominant singularity — an exact algebraic constant per height,
   extrapolated like lambda_H. The euler.h diagonal-contribution hook already
   isolates the needed quantity. Medium cost; turns a conjecture into a theorem-track
   number.

## Broad brainstorm — 20 ideas, ranked + challenged (2026-06-22)

Promise = value x tractability x P(works). Challenged most->least; kills at bottom.

 1. OEIS lookup of structural seqs (orders 1,3,7,15,42,106..; atoms 1,2,4,9,29,68..) — SURVIVES (near-free, do first)
 2. lambda_0 (hole-free) via DA/biased — SURVIVES (cheap, sharpens ~6.93, gives lambda_0/lambda)
 3. critical amplitude C in a(n)~C lam^n/n — SURVIVES (cheap, never reported)
 4. lambda_k per-hole-class growth, test lambda_k=lambda — SURVIVES for small k (data-limited large k)
 5. site-perimeter + first cross-SOURCE check vs Mertens 1990 — SURVIVES (catches shared-spec bugs)
 6. nu radius-of-gyration exponent (R_g~n^nu, ~0.6403) — SURVIVES W/ CAVEAT (confirms class, won't pin nu)
 7. symmetric-subclass growth ~sqrt(lambda)~2.667 — SURVIVES (unmeasured for polyplets)
 8. knight/reach-2 growth via DA+FSS — SURVIVES (medium cost, new lattice constant)
 9. triangular-lattice DA — SURVIVES as pipeline VALIDATION (known lambda), not discovery
10. bounding-box aspect-ratio fluctuation — SURVIVES, modest (mean->1 trivial)
11. free/one-sided amplitude ratio ->1/8 — SURVIVES, LOW marginal (ratio preordained)
12. convex-subclass GFs (algebraic) — SURVIVES as two-step (extend series to ~40 then guess)
13. hole-AREA distribution — SURVIVES cheap (sampler), modest
14. exact diagonal-contact density (T6) via marked TM — SURVIVES, mediocre cost/value (engine work)
15. mean rook-components constant — SURVIVES via sampling; exact deferred (engine)
16. extend A389193 via square4 holes — SURVIVES, low novelty; verify engine support
17. gluing-graph statistic (tree vs cycles) — SURVIVES, exploratory, unclear payoff
18. subleading correction exponent Delta — KILLED (20 terms insufficient; unreachable)
19. reach-r family (general r) — KILLED/DEFER (needs new 2D engine; speculative)
20. fractal dim / limit shape — KILLED (no limit shape exists; subsumed by nu, #6)

Near-free cluster (run first, no disturbance to live jobs): #1,#2,#3,#4,#6,#7(recon),#11.
#2/#3/#4/#7 are the SAME biased-DA machine pointed at different subsequences.

## Cluster results — executed 2026-06-22 (experiments/subclass_growth.py)

- **#2 lambda_0 (hole-free):** biased(theta=-1) ratio 6.955, Dlog-Pade 6.92 ->
  **lambda_0 ≈ 6.94 (6.92–6.96)**, lambda_0/lambda = 0.978. Sharpens the prior crude
  "~6.93 ratio" into a two-method triangulation; confirms the 0.977 ratio. WIN.
- **#4 lambda_k = lambda test:** k=1 -> 7.118, k=2 -> 7.05 (both ≈ lambda=7.110);
  k=3 -> 6.06 but only 10 terms with ratios still steeply climbing (unreliable).
  **Conclusion: lambda_k = lambda supported for k=1,2** (holes don't change the
  exponential rate, as universality predicts); k>=3 needs more n. Structural win.
- **#3 critical amplitude C:** C_n = a(n)*n/lambda^n rises slowly 0.185->0.188
  (n=12..20); 1/n extrapolation **C ≈ 0.19** -- first-ever estimate of this
  amplitude, not yet converged (sensitive to lambda). Completes a(n) ~ C lambda^n/n.
- **#11 symmetric ~ sqrt(lambda):** mirror_ortho -> 2.571, mirror_diag -> 2.618,
  both approaching **sqrt(lambda) = 2.667** from below. Confirms reflection-symmetric
  polyplets grow as sqrt(lambda). (C2 -> 1.80 is garbage: C2 counts are parity-sparse,
  ratios meaningless; redo C2 with parity-aware handling.)
- **#6 nu (R_g exponent): ALREADY DONE** -- results/scaling_study.md fit R_g~n^nu
  over n=8,11,14,19 giving **nu ≈ 0.683** ("finite-size-inflated, consistent with the
  universal 0.6408"). At its ceiling without larger/more sample sizes; not worth redoing.
- **#7 site-perimeter + Mertens cross-source: PROMOTED to high value.** Mertens 1990
  (papers/Mertens1990...pdf) Table I "nnSquare" column IS the king lattice = our a(n)
  to n=14; his perimeter polynomials D_s(q) are the SITE-perimeter distribution
  (percolation t = empty neighbours), tabulated for the king lattice in Appendix A.
  So: add site-perimeter to g2 (a few lines; g2 currently does only EDGE perimeter),
  cross-validate against Mertens Appendix A (first cross-SOURCE check, catches
  shared-spec bugs cross-ISA cannot), then EXTEND his king perimeter polynomials past
  n=14. Table II gives a second king-lattice series (mean cluster size S(p), r<=13).
- **#1 OEIS lookup: DONE -- both NOVEL (Superseeker-confirmed, jasonp 2026-06-23).**
  NEITHER structural sequence is in OEIS: GF recurrence orders
  1,3,7,15,42,106,278,711,1897,5005 NOR atom degrees 1,2,4,9,29,68,181,462,1254,3289.
  Two more candidate-new sequences for the #25 OEIS batch. (My in-session lookup was
  inconclusive -- oeis.org 403s automation, WebSearch hallucinated non-matches -- but
  the sequences had already been Superseeker-checked.)

### Next-pick ranking after the cluster
1. **#7 site-perimeter + Mertens** — now the standout: new invariant + cross-source
   validation + extends a published table. Needs a small g2 addition.
2. **#1 OEIS lookup** (jasonp) — near-free, just needs the real query channel.
3. **#8 knight/reach-2 growth** — reuse the DA/biased machine on a new lattice.

### #9 DONE 2026-06-23 (experiments/lattice_da.py): DA pipeline cross-validated
Applied the biased-ratio + Dlog-Pade machine to published Mertens-1990 series for
other lattices -- all reproduce literature lambda, confirming the pipeline behind our
king-lattice lambda=7.110, lambda_0=6.94, etc.:
  king(=our a(n))  biased 7.113  (lit 7.11)
  triangular       biased 5.184  (lit 5.18)  -- 19 terms, essentially exact
  cubic/3D polycube biased 8.353 (lit 8.34)  -- 15 terms, theta=-3/2
These are KNOWN constants (validation, not new sequences), as challenged. Value =
external confidence in the DA results.

### #11 DONE 2026-06-23 (experiments/amplitude_ratios.py)
8*free/a -> 1.0000003 and 4*onesided/a -> 1.0000001 at n=19: amplitude ratios are
1/8 (D4) and 1/4 (rotation group), as expected. biased lambda fixed/free/one-sided =
7.111/7.113/7.112 -- all share lambda. BONUS tying #7<->#11: the amplitude-ratio
residual |8free/a - 1| decays with base 0.387 ~ 1/sqrt(lambda)=0.375, i.e. the
symmetric subclasses (which grow as sqrt(lambda), #7) ARE the leading correction to
free/one-sided. Low marginal value as challenged, but the cross-link is clean.

### #5 DONE 2026-06-23 (cpp/g2_redelmeier.cpp --siteperim; results/site_perimeter.md)
Implemented site-perimeter (# distinct empty king-neighbours = percolation perimeter)
in g2 and **cross-SOURCE validated vs Mertens 1990 Table IVB (nnSquare)**: n=11 matches
s=11 EXACTLY (all 31 coeffs t=18..48, sum=a(11)), n=12 matches s=12 exactly. The
project's FIRST agreement with an external published source on a computed invariant
(all prior gates are cross-ISA, which can't catch shared-spec errors). The top-ranked
enqueued item, delivered. Min-site-perimeter-per-n + the (n,t) triangle beyond n=13 are
OEIS candidates. Found issue: Makefile -Wno-error=restrict breaks clang build (noted).

### #10 DONE 2026-06-23: mean bbox aspect ratio -> constant ~1.4 (NOT 1)
Exact (n,w,h) via g2 --per-box: mean max(w,h)/min(w,h) = 1.50 (n=2) decreasing slowly
to 1.457 (n=12), 1.42 at n=19 (sampler). Converges to a CONSTANT ~1.4, not 1 --
my challenge ("isotropy forces ->1") was WRONG: w,h are comparable random variables
whose ratio has limiting mean >1, so typical king-animals stay mildly elongated. Modest
but real, and a corrected prediction.

### #8 STARTED 2026-06-23: knight growth ~11-12, not pinned (needs more terms)
Biased estimator on the 8-term knight series (1,4,28,234,2162,20972,209608,2135572):
lam_n plateaus ~11.6 but ratios still climbing -> lambda_knight ~ 11-12, NOT converged
at 8 terms (as challenged). To pin it: extend the knight series via gf_knight per-height
GF recovery + FSS, or a knight Redelmeier. Left as the next compute step for #8.

### #13, #15, #17 DONE 2026-06-23 (experiments/sample_structure.py, existing samples)
Analyzed the existing 10k n=19 uniform samples (results/a19_samples.txt) -- no new
sampling. Parser self-validates: #15 rook-component mean = 10.067 (matches the known
10.07 in sample_stats.md).
- #15 rook-component count: mean 10.07, distribution peaks at 10, range 2..19.
- #17 gluing-graph (nodes=rook-pieces, edges=diagonal contacts between them): mean
  cycles (E-V+1) = 0.30, **74.4% of king-animals have a TREE gluing graph**; 21% one
  cycle, tail to 4. New structural descriptor.
- #13 hole-area distribution: 89.7% of holes are single cells (area 1), 5.6% area 2,
  decaying; mean hole area 1.20; one area-16 outlier. Holes are overwhelmingly minimal.

## Remaining enqueued (need engine/code work, deferred -- not rushed unattended)
- #12 convex-subclass GFs: extend the convex series to ~40 terms, then guess algebraic GF.
- #14 exact diagonal-contact density: needs a contact-marked transfer matrix (C++).
- #16 extend A389193: needs square4 (rook) hole-counting in the TM (engine errors
  "--holes is supported for square8 only").
4. Polish: #3 amplitude C (2-param fit), #4 large-k & #11 C2 (parity) once reach extends n.

## Artifacts
- `experiments/lambda_fss.py`   — FSS/BST extrapolation of the lambda_H ladder.
- `experiments/series_da.py`    — Dlog-Padé + inhomogeneous DA: lambda, theta, a(21)/a(22) prediction.
- `experiments/subclass_growth.py` — lambda_0, lambda_k, amplitude C, sqrt(lambda) symmetric (items #2,#3,#4,#11).
