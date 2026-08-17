# Local structure of the area-moment hierarchy at the singular collision
# (delta-Laurent chassis): odd-part multiplicity law + c_r localization

Session 12 result. Builds on the s08 kernel moment recursion
(`docs/proofs/area-moment-kernel.md`), the s09 slice/collision analysis
(`results/convex-area-limit-law.md`), and the s10 B_1 factorization
(`out_s10_verify_B1_div.txt`). Scripts: `experiments/s12_delta_local.py`,
`experiments/s12_bivar_Br.py` (s11's, run to completion),
`experiments/s12_bivar_r2_king.py`, `experiments/s12_bivar_r4.py`,
`experiments/s12_factor_probe.py`.

## 1. The delta-Laurent chassis (new computational method)

On the slice x = 1/4, parametrize the singularity by delta = sqrt(Delta):

    y(delta)  = 5/4 - sqrt(1+delta^2),   s0 = 2(sqrt(1+delta^2) - delta),
    s1 = 2(sqrt(1+delta^2) + delta),     sqrt(Delta) == delta  (RATIONAL).

All seeds are closed-form power series in delta; the s08 Temperley moment
recursion (operators B, D1, D2, closing kernel, evaluations at s0 and
sigma_pm = 1/(1 -+ sqrt(y))) runs verbatim over the Laurent field
F_p((delta)) with per-object precision tracking. The kernel-point
evaluations (PK1(s0) = delta, D00(s0) ~ delta, D00(sigma+) ~ delta^2)
genuinely divide by delta-powers: singular behaviour appears DIRECTLY as
Laurent poles — no P/Q fitting stage, no asymptotic extraction.

Validation (receipts `out_s12_delta_run.log`, `out_s12_delta_run2.log`,
`out_s12_delta_local.txt`, `out_s12_delta_profiles.json`; r <= 6, king
AND polyomino control, both 61-bit primes, ZERO failures):
  V1  level-0 total == the s03 PROVEN closed form expanded at the
      collision (absolute anchor, king);
  V2  every level r = 0..6: tot_r * Kx^(r+1) * delta^(4r+4) equals
      P_r + delta*Q_r of the INDEPENDENT y-adic slice engine receipts
      (out_s09_slice_PQ_run1.json) — 14 level-checks per prime per mode;
  V3  leading Laurent coefficient == c_r = (r!)^2/2^(r+7) at every r
      (the s09 law, re-derived by an expansion at a different point);
      coefficient at delta^(-(4r+3)) == 0.

## 2. Odd-part multiplicity law (new; refines s09 finding 4, refutes the
##    s10/s11 factorization-shape conjecture)

Write M_r * K^(r+1) Delta^(2r+2) = A_r + B_r sqrt(Delta) (s07/s08 forms).

**Law (firm, multi-receipt):** nu_Delta(B_r) = ceil(r/2) for r >= 1 —
the sqrt-part degeneracy DEEPENS with the moment level, in BOTH modes:

  - delta-chassis (r <= 6, both modes, both primes): the odd part of
    tot_r first appears at delta^(2*ceil(r/2)+1-(4r+4)); odd-position
    coefficient pattern (delta^(-(4r+3)), -(4r+1)), -(4r-1)), -(4r-3))) =
    (0,*,*,*) r=1,2; (0,0,*,*) r=3,4; (0,0,0,*) r=5,6
    (`out_s12_delta_profiles.json`).
  - bivariate exact (r <= 3 + r=4, WBOX 30/38, 2 primes, CRT, then
    verified EXACTLY over Z on the full grid, then exact multivariate
    division): nu_Delta(B_1) = nu_Delta(B_2) = 1, nu_Delta(B_3) = 2,
    exactly, both modes (`out_s12_bivar_Br.txt`,
    `out_s12_bivar_r2_king.txt`, `out_s12_factor_probe.txt`); r=4 run
    `out_s12_bivar_r4.txt` (registered prediction nu=2 in its header).
  - slice Q_r vanishing orders (`out_s12_Qord_check.txt`):
    ord Q_r = ceil(r/2) at BOTH roots y = 1/4 and 9/4 (so
    Delta_x^ceil(r/2) | Q_r), r <= 12, both modes, both primes
    (`out_s12_slice_PQ_r12.json`; the r = 9..12 cases were a REGISTERED
    prediction, written down before the slice-r12 receipts existed).
    The same run adjudicates s11's P1: c_r = (r!)^2/2^(r+7) and cQ_r = 0
    now hold at moment level 12 (was 8), both modes
    (`out_s12_slice_r12.txt`).

**Degree corrigendum (king, even r):** the s11 numerator-degree ansatz
deg B_r = 6r+5 is one short at even r: true king degrees are
deg A_r = 6r+8 (all r <= 4) but deg B_1..B_4 = 11, 18, 23, 30, i.e.
6r+6 at even r — this (not the denominator) caused s11's king r=2 fit
inconsistency. Poly degrees 4r+6/4r+4 exact throughout. King r=2 closed
at (TA,TB)=(21,18), exact over Z on the full 31x31 grid
(`out_s12_bivar_r2_king.txt`); king r=4 at (33,30) after (32,29) failed
inconsistent EXACTLY as the even-r bump predicts (registered), exact
over Z on the full 39x39 grid, nu_Delta(B_4) = 2 (`out_s12_bivar_r4.txt`).

**Refutation:** s10's conjectured shape B_r = Delta*x^2y^2*(1+x+y)*C_r
(king) / s11's Delta*4x^2y^2*E_r (control) holds ONLY at r = 1.
At r = 3 (both modes) the correct shape is B_3 = Delta^2*x^2y^2*(core)
with the king core (deg 15, 116 monomials) having NO (1+x+y) factor and
the poly core (deg 8, 45 monomials) no (1-x+y)(1+x-y) factors; poly
integer contents run 4, 2, 2 at r = 1,2,3. The r=1 atoms are accidents;
the Delta-multiplicity is the real structure.

## 3. Localization of the c_r induction (executes the start of s09 OPEN 1)

Receipts: V4 blocks of `out_s12_delta_local.txt`; `out_s12_delta_trace.txt`.

1. **Phase attribution at the collision** (every r <= 6, both modes):
   M00^(r)(1) is REGULAR (delta-valuation 0); M10^(r)(1) has valuation
   EXACTLY -(3r+1) (new law; refines s09's "M10 residues vanish": the
   value sits r+3 orders above the tot pole -(4r+4)); M11^(r)(1) has
   valuation -(4r+4) and its leading coefficient IS c_r.

2. **Dominant-term truncation:** replacing the level-r inhomogeneity
   I^(r) = sum_{k<r} (-1)^(r-1-k) C(r,k) D^(r-k) M^(k) by ONLY its
   k = r-1 term  r*D*M^(r-1)  changes tot_r starting EXACTLY at
   delta^(-(4r+2)) — gap 2 below leading, at every r = 2..6, both modes,
   both primes. The c_r law (and the cQ_r = 0 order below it) is carried
   entirely by r*D*M^(r-1).

3. **Channel split (trace):** of the three terms assembling M11^(r)(1)
   = avg_{sigma_pm}( yD1[M00^(r)] + 2yD2[M10^(r)] + I11^(r) ):
   yD1[M00] enters at val -(4r+2) (negligible); 2yD2[M10] and I11 both
   enter at -(4r+4) and their leading parts SUM to c_r (king; exact
   rationals by CRT + Wang from both primes):
       r=1: 3/1024   + 1/1024     = 1/256    (split 3/4   : 1/4 of c_1)
       r=2: 17/4096  + 15/4096    = 1/128    (split 17/32 : 15/32)
       r=3: 423/32768 + 729/32768 = 9/256    (split 47/128: 81/128)
       r=4: 4617/65536 + 13815/65536 = 9/32  (split 513/2048:1535/2048)
   with the yD1[M00] channel at -(4r+2) worth 1/1024, 3/4096, 45/32768,
   315/65536 there. The I11 share of c_r grows with r. **The identical
   constants hold for the polyomino control, channel by channel**
   (`out_s12_delta_local_trace_poly.txt`): king/poly universality of the
   limit law extends to the individual local-transfer channels at the
   collision — the mode difference (kernel K, weight atoms) is entirely
   regular there. Normalized by c_(r-1) the channels sum to r^2/2
   exactly: 1/2, 2, 9/2, 8. Moreover the
   truncated I11 (dom term only) has the same leading coefficient as the
   full I11 at every r.

**Consequence for the proof:** at leading Laurent order the recursion
closes in the (M10, M11) two-phase subsystem with inhomogeneity
r*D*M^(r-1); the M00/D1 channel decouples. The blow-up induction
c_r/c_(r-1) = r^2/2 (s09 OPEN 1) is now a statement about ONE explicit
local transfer: level-(r-1) leading profiles -> (2yD2[M10] + I11)
evaluated at sigma+ -> c_r, with all objects available as machine-checked
Laurent data in `out_s12_delta_trace.txt`.

## Status

nu-law: firm at the stated ranges (r<=6 delta/slice, r<=3(4) bivariate);
the general-r statement is the natural companion of the denominator law
K^(r+1)Delta^(2r+2) (s08 OPEN 2) and should fall to the same pole-order
induction, with the parity refinement coming from the sigma_pm mirror
average (odd-in-delta parts cancel once per two levels — mechanism
conjectured, not proven).

## Addendum (session 13)

Section 3's local transfer is executed and solved in closed form in
`results/convex-area-local-transfer.md` (c_r law all r, curve law,
channel-split closed forms, d_r = 2c_r value law, universality derived).
The nu-law mechanism remains open one Laurent order below the solved
profiles.
