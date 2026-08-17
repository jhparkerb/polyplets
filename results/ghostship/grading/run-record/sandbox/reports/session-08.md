DIRECTION: finish s07's unfinished r=3,4 registered-prediction test (DP to s=57 + fits), then PROVE the moment structure via the Temperley moment method (d/dq of the proven q-FE at q=1), upgrading fitted A_r forms to derived ones
SHAPE: verify holdout, then derive

Plan: (1) rerun session 07's validated r<=4 moment DP at SMAX=57 in the
background (it died last session; the registered predictions in
out_s07_limit_law_prediction.txt were never tested) and run the waiting
s07_r4_fit.py harness on the result — this is a VERIFY of s07's limit-law
prediction and closes its first OPEN. (2) While that runs, implement the
moment method sketched in results/convex-area-moments.md: differentiate the
proven q-functional-equation system (s03/s04) with respect to q at q=1 to
get an inhomogeneous linear FE for the area-weighted generating function
with the SAME kernel; solve by kernel roots; compare the derived moments
with s07's fitted closed forms and the ground-truth tables. (3) Push the
derivation to general level r.

## CARRY
CLAIM: Temperley moment method EXECUTED: level-r moment FE = level-0 operators + inhomogeneity I^(r)=sum_{k<r}(-1)^(r-1-k)C(r,k)(s d/ds)^(r-k)M^(k), closed by the SAME kernel roots s0, sigma_pm at every level => M_r(x,y) and A_r(t) are ALGEBRAIC (in Q(x,y,sqrt(Delta))) for EVERY r; machine-executed r<=4, king+control | receipt: docs/proofs/area-moment-kernel.md, experiments/s08_moment_kernel.py, out_s08_moment_kernel_16x16_r4.txt | status: firm
CLAIM: derived M_1..M_4 match the joint truth table (every cell, boxes w,h<=10), the independent r<=4 moment DP diagonal, and s07's fitted bivariate M1*K^2*Delta^4 == A+B*sqrt(Delta), at primes 2^61-1, 10^18+9 AND 2^521-1 (compared coefficients exact) | receipt: out_s08_moment_kernel_16x16_r4.txt, out_s08_moment_kernel_10x10_r4_big.txt | status: firm
CLAIM: A_3, A_4 identified with the s07-predicted denominators (2+t)^4(1-4t)^8, (2+t)^5(1-4t)^10 [king] / (1-4t)^8, (1-4t)^10 [control]; explicit numerators banked; surplus 12-28 equations per fit on SMAX=57 data | receipt: out_s07_r4_fit.txt, out_s07_area_moments_r4_57.txt | status: firm
VERIFY: s07 registered limit-law prediction (its OPEN 1: p_0(A_3)=9/256, p_0(A_4)=9/32, E[area^r]/s^2r=(r!)^2/((2r+1)!2^r), both modes) | outcome: confirmed (all 8 constants exact) | receipt: out_s07_r4_fit.txt
VERIFY: s07 claim 4 (bivariate M1 closed form (A+B sqrt D)/(K^2 D^4)) | outcome: confirmed — now DERIVED from the q-FE by the kernel construction, independent of s07's modular fit | receipt: out_s08_moment_kernel_16x16_r4.txt (check C3)
VERIFY: s07 claim 1 (A_1, A_2 algebraic with denominators (2+t)^(r+1)(1-4t)^(2r+2)) | outcome: confirmed — algebraicity now a theorem for all r; specific fitted forms pinned via C2/C3 + s07 holdouts | receipt: docs/proofs/area-moment-kernel.md
OPEN: close the identification of derived M_r with the specific fitted closed forms on a sufficient degree box (s03-style degree bounds + specializations; s04_exact_close machinery adapts mechanically) — parallel of s03 §7.
OPEN: denominator law K^(r+1)Delta^(2r+2) as a theorem: track pole orders through the level-r recursion (D raises Delta-powers via s0=((1+x-y)-sqrt(Delta))/2x; kernel division adds one K) — induction is set up in the proof doc.
OPEN: extract E[area^r]/s^2r -> (r!)^2/((2r+1)!2^r) for ALL r from the singular expansion of the recursion at t=1/4 => area/s^2 ->d U(1-U)/2 becomes a THEOREM (bounded moment problem is determinate); confirmed r<=4.
DEAD: none this session; NOTE for successors: out_s07_bivar_moment{,_poly}.json store only the i<=j representative of each symmetric (A,B) monomial pair — symmetrize before use (cost me one false C3 failure).
## LOG

Session start. Read all seven CARRY sections. out_s07_r4_fit.txt absent —
s07's SMAX=57 r<=4 DP died before finishing; predictions untested. Timing
calibration of s07_area_moments_r4b.py: 4.4s @ SMAX=22, 17.7s @ SMAX=30
(printed a_r(30) values match the banked out_s07_area_moments_r4_30.txt).
Extrapolated ~14 min @ SMAX=57. Launched in background; finished clean
(validations V1 brute force, V3 truth table, V4 transpose all OK — see
out_s07_area_moments_r4_57.txt).

### Part 1: r=3,4 registered-prediction test (s07's unfinished holdout)

Ran experiments/s07_r4_fit.py (written by s07 BEFORE the data existed)
on the fresh SMAX=57 data. Cross-check first: the r<=2 sequences of the
r4 run match the independent SMAX=52 run on all 51 shared terms. Fits
with the PREDICTED denominators close immediately:
  king A_3: degP=degQ<=18, surplus 20; king A_4: deg<=22, surplus 12
  poly A_3: deg<=14, surplus 28;      poly A_4: deg<=17, surplus 22
All four p_0 values and all four E-constants equal the registered
predictions exactly: p_0(A_3)=9/256, p_0(A_4)=9/32, E[area^3]/s^6=1/1120,
E[area^4]/s^8=1/10080, king AND polyomino. Verdict line in
out_s07_r4_fit.txt: CONFIRMED. The moments of area/s^2 now match
X=U(1-U)/2 for r=1,2,3,4 in both families.

### Part 2: the Temperley moment method, executed (the main result)

Derivation (full statement in docs/proofs/area-moment-kernel.md):
setting q=e^eps in the PROVEN q-FE (s04) and extracting eps^r, each term
c(qs)*X(q) contributes sum_k C(r,k) D^(r-k)[c*X^(k)], D = s d/ds. Using
the lower-level equations to telescope, the level-r system is the SAME
s03 operator system on the M^(r)_ph with explicit inhomogeneity

  I^(r) = sum_{k=0}^{r-1} (-1)^(r-1-k) C(r,k) D^(r-k) M^(k)

(I^1 = DF, I^2 = 2DM^1 - D^2F, I^3 = 3DM^2 - 3D^2M^1 + D^3F, ...).
Phase (0,0) stays non-catalytic; the staircase kernel P_K and closing
kernel (s-1)^2 - ys^2 are LEVEL-INDEPENDENT, so s0 and sigma_pm close
every level. Two structural facts make the back-substitution exact:
the staircase numerator vanishes at s0 by construction, and
P_K/(s-s0) = 1/s0 - xs has unit constant term (synthetic division);
the closing numerator vanishes at both sigma_pm and the closing kernel
has unit leading coefficient 1-y (exact polynomial division). Everything
stays in Q(x,u,sqrt(Delta))(s); assembled moments are even in u
(asserted every level) hence in Q(x,y,sqrt(Delta)). Induction => M_r
algebraic for ALL r. This resolves s07's OPEN 2 and the "Open (proof
path)" of results/convex-area-moments.md (addendum appended there).

Implementation: experiments/s08_moment_kernel.py reuses the s03 exact
series classes (Ser/SPoly/SRat, imported from s03_kernel_solve); new
pieces: srat_Dj (repeated s d/ds keeping denominator as a power, not
squaring), sdiv_root (synthetic division by s-root), polydiv_exact
(division by unit-leading polynomial with zero-remainder assert),
generic solve_level() used for ALL levels (level 0 = inhomogeneity 0,
reproducing s03's solution through the same code path — check C0).

Checks (all pass, king AND polyomino):
  C0 level-0 grid == validated DP table f(w,h);
  C1 [x^w y^h]M_r == sum_n n^r f(w,h;n), joint truth table, r=1..4;
  C2 diagonal == a_r(s) from the independent univariate moment DP;
  C3 M_1*K^2*Delta^4 == A + B*sqrt(Delta) (s07 bivariate fit), checked
     by multiplication (K is not monomial-cornered, so no division).
Runs: 6x6 and 12x12 debug (levels 0-4), final receipts 16x16 r<=4 at
p=2^61-1 and 10^18+9 (out_s08_moment_kernel_16x16_r4.txt) and 10x10
r<=4 at p=2^521-1 (out_s08_moment_kernel_10x10_r4_big.txt; any false
match would need a coefficient divisible by ~10^157). Wall: seconds to
~1 min per mode/prime — far cheaper than feared; the SRat degree growth
per level is tame because SPoly auto-trims and denominators are kept as
powers.

Pitfall logged: first C3 attempt FAILED at every sign/branch combination;
cause was NOT the derivation but the receipt format — the s07 JSON stores
only the i<=j representative of each symmetric monomial (the .txt prints
the full symmetrized polynomial). Symmetrizing poly_of fixed it; kept as
a NOTE in CARRY since the same trap awaits anyone reusing those JSONs.

### What this changes about the problem map

The area statistic's tractability boundary is now: counting sequence
non-D-finite in mechanism (s04-s06, infinitely many poles numerically),
but EVERY moment by semiperimeter algebraic — proven constructively, not
just fitted — in the same field Q(t,sqrt(1-4t)) as the counting GF, with
all moment asymptotics matching the U(1-U)/2 limit law through r=4. The
remaining gaps are mechanical (identification closure, denominator-law
induction) or analytic (all-r constants => limit law theorem), all laid
out in the OPENs.

### OEIS queries

None this session (searches remain Cloudflare-blocked per s06/s07; no
b-file lookups were needed).

### Receipts written this session
  out_s07_area_moments_r4_57.{json,txt}  (SMAX=57 DP, s07's script)
  out_s07_r4_fit.txt                     (registered-prediction verdict)
  out_s08_r4_57_run.log                  (DP run log, empty=clean)
  experiments/s08_moment_kernel.py       (moment-kernel pipeline)
  out_s08_moment_kernel_16x16_r4.txt     (main receipt, 2 primes)
  out_s08_moment_kernel_10x10_r4_big.txt (2^521-1 receipt)
  docs/proofs/area-moment-kernel.md      (proof doc)
  docs/proofs/area-moments-method.md     (status update prepended)
  results/convex-area-moments.md         (addendum appended)
