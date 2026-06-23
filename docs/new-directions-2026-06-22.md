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

## Artifacts
- `experiments/lambda_fss.py`   — FSS/BST extrapolation of the lambda_H ladder.
- `experiments/series_da.py`    — Dlog-Padé + inhomogeneous DA: lambda, theta, a(21)/a(22) prediction.
