# The area limit law of convex king animals at moment level r ≤ 8

Session 09 result. Builds on the s08 kernel-derived moment hierarchy
(`docs/proofs/area-moment-kernel.md`) and the banked closed forms of s07/s08
(`results/convex-area-moments.md`, `out_s07_r4_fit.txt`). Scripts:
`experiments/s09_slice_moments.py`, `experiments/s09_anchor_check.py`;
receipts `out_s09_slice_moments.txt`, `out_s09_slice_PQ.json`,
`out_s09_anchor_check.txt`.

## Statement

Let A_r(t) = Σ_s a_r(s) t^s be the r-th area-moment GF of convex king
animals by semiperimeter (a_r(s) = Σ_{animals, w+h=s} area^r), and the same
with "convex polyominoes" for the control. Then for r = 0,1,...,8, in BOTH
modes, the leading singular coefficient at the dominant singularity t = 1/4
is

    A_r(t) ~ c_r / (1-4t)^(2r+2),    c_r = (r!)² / 2^(r+7).

Since a_0(s) ~ (s/128)·4^s (s01, firm; c_0 = 1/128), this is equivalent to

    E[area^r | s] / s^(2r)  →  (r!)² / ((2r+1)!·2^r)   =  E[X^r],
    X = U(1-U)/2,  U ~ Uniform(0,1),

i.e. **area/s² converges to U(1-U)/2 in moments up to order 8** (identical
for king animals and polyominoes). X is supported on [0,1/8], so the moment
problem is determinate: if the c_r law holds for all r (OPEN; mechanism
below), area/s² →d U(1-U)/2 is a theorem. This extends the r ≤ 4 record of
s07/s08 (registered-prediction confirmed) to r ≤ 8 by a new, cheaper route.

## Method: the singular slice x = 1/4 of the moment-kernel recursion

The s08 recursion produces M_r(x,y) ∈ Q(x,y,√Δ), Δ = (1-x-y)²-4xy, with
denominator K^(r+1)Δ^(2r+2), K = x+y+xy. Writing M_r ~ C_r(x,y)/Δ^(2r+2)
near the singular curve Δ=0, the diagonal (t,t) gives Δ = 1-4t and
c_r = C_r(1/4,1/4). The slice x = 1/4 crosses the curve transversally at
y = 1/4 (Δ(1/4,y) = (y-1/4)(y-9/4)), so C_r(1/4,1/4) is computable there:

    S_r(y) := M_r(1/4,y),
    S_r · Kx^(r+1) Δx^(2r+2) = P_r(y) + Q_r(y)·√Δx,
    Kx = (1+5y)/4,  Δx = (y-1/4)(y-9/4),
    c_r = P_r(1/4)/(9/16)^(r+1),   cQ_r = Q_r(1/4)/(9/16)^(r+1).

With x NUMERIC the whole recursion runs in ONE truncated series variable
(y-precision 130), which is what makes r = 8 cheap (~2.5 min/mode/prime)
where the bivariate r = 4 run took ~75 s at box 16×16. The s08 SRat
denominators (which grow like 3^r in degree) were replaced by rational
functions with FACTORED denominators over the atom registry
{1-xs, D00 = (1-xs)²-y, PK1 = PK/(s-s0)}, lcm-based addition, reuse of
D = s·d/ds ladders across levels, and exact factor cancellation after every
step ("FRat"). Everything mod the two s08 primes independently.

## Validation ladder (all machine-checked, see receipts)

  S0  slice series of level 0 == the s03 PROVEN closed form
      -(M + 2x²y²(1+x+y)²√Δ)/(2KΔ²) at x=1/4 — all 131 y-coefficients.
  S1  slice series of level 1 == the s07/s08 bivariate M1 closed form
      (A+B√Δ)/(K²Δ⁴) at x=1/4 — all 130 y-coefficients (king AND control).
  S2  every fit P_r, Q_r is massively overdetermined: surplus 37–119
      equations, zero failures, at the conjectured denominator — i.e. the
      denominator law K^(r+1)Δ^(2r+2) HOLDS on the slice for r ≤ 8.
  S3  (cP_r, cQ_r) for r ≤ 4 == the same constants computed exactly (over
      Q) from the BANKED diagonal closed forms A_r(t) — which themselves
      re-expand to the independent DP57 moment sequences, 48 terms each
      (`out_s09_anchor_check.txt`). Two pipelines, same constants.
  S4  two primes agree; c_r comparisons done per prime, constants
      reconstructed by CRT + Wang.

## The constants (CRT-reconstructed, identical for king and control)

    r   :   0      1      2      3     4     5       6       7        8
    c_r : 1/128  1/256  1/128  9/256  9/32  225/64  2025/32 99225/64 99225/2
    cQ_r: -1/64    0      0      0     0      0       0       0        0

c_r = (r!)²/2^(r+7) at every r (surplus-checked fits, two primes; receipts
`out_s09_slice_moments_run1.txt`, `out_s09_slice_PQ_run1.json`). The
half-power coefficient cQ_r vanishes for every r ≥ 1; more precisely the
fitted Q_r(y) vanish at BOTH roots of Δx (y = 1/4 and 9/4), i.e.
Δx | Q_r on the slice, r = 1..8, both modes, both primes
(`out_s09_Qdiv_check.txt`).

## Structural findings en route

1. **Catalytic denominator law.** After exact factor cancellation, every
   level has (slice, both modes, r ≤ 8, both primes)

       M00^(r): den = D00^(2r+1),               num deg 4r+1
       M10^(r), M11^(r): den = D00^(2r+1)·PK1^(2r+1),  num deg ≤ 6r+3

   and fitted numerator degrees deg P_r = 5r+4, deg Q_r = 5r+3 exactly.

2. **Quadruple collision at the singularity** (exact algebra, whole
   curve): on Δ=0 parametrized by (x,y) = (a², (1-a)²), FOUR
   distinguished points of the catalytic s-plane coalesce at s* = 1/a:
   the two staircase-kernel roots s0, s1 (disc Δ), the D00-root
   (1-√y)/x, and the closing-kernel root σ+ = 1/(1-√y) = 1/(1-(1-a))
   = 1/a (σ- stays far away — hence only the σ+ half of the ± average
   is singular, i.e. the M11 phase). Two scales: off the curve (slice
   x=1/4, δ=√Δ) s0,1 - s* = ∓2δ (outer scale δ), while u₋ - s* = δ²
   and σ+ - s* = -3δ² (inner scale δ²). Exact leading atom values:
   PK1(s0) = δ, D00(s0) = √y·δ·(1+O(δ)), D00(σ+) = δ²·(1+O(δ)),
   PK1(σ+) = δ/2·(1+O(δ)). Evaluating the level-r M10 (pole (D00·PK1)^
   (2r+1)) at σ+ thus amplifies by δ^(-3(2r+1))·N_r(σ+), forcing the
   numerator vanishing order δ^(2r-1) that the M10-residue zeros
   (finding 3) witness. This two-scale blow-up is the frame for the
   induction proof of the c_r law.

3. **The closing phase is the sole singularity carrier.** Per-phase fits
   (phases run, `out_s09_slice_moments.txt`) show: the M00 phase is
   RATIONAL in y with poles only at y = (1-x)² (its subsystem is closed —
   the inhomogeneity I00 involves only the M00 ladder, never a
   kernel-root evaluation), no Δ-singularity at all; the M10 phase value
   M10^(r)(1) has BOTH leading residues (Δ^-(2r+2) and Δ^-(2r+3/2)) equal
   to ZERO for every r ≤ 7; the M11 phase carries the full C_r. The
   assembled c_r is M111's residue alone. M11-phase fitted numerator
   degrees: degP = 7r+5, with extra atom ((1-x)²-y)^(2r+1).

4. **The √Δ-part is doubly degenerate at the singularity.** cQ_r = 0 for
   ALL 1 ≤ r ≤ 8 (both modes; and cQ_0 = -1/64 both modes). For r = 1
   this is PROVEN globally: the banked bivariate B_1(x,y) (degree ≤ 11,
   verified over Z by s08) vanishes at 29 rational points of the
   irreducible conic Δ=0, hence Δ | B_1 exactly — in both modes. On the
   slice the fitted Q_r are divisible by Δx for r = 1..8 (checked at both
   roots y = 1/4, 9/4 mod both primes). Conjecture: Δ | B_r for all
   r ≥ 1 (the odd part of M_r is O(Δ^(-(2r+1/2))), not the generic
   Δ^(-(2r+3/2))).

### Epistemic status of the diagonal statement for r ≥ 5

M_r is a THEOREM-level algebraic function (s08 kernel construction), and
its restrictions to the slices x = 1/4 (r ≤ 8) and x = 1/9 (r ≤ 6) are
proven (surplus-checked, two primes) to equal (P+Q√Δ)/(K^(r+1)Δ^(2r+2))
there, with the diagonal r ≤ 4 forms exact from s07/s08. The r ≥ 5
diagonal claim A_r ~ c_r/(1-4t)^(2r+2) additionally uses that the GLOBAL
denominator is K^(r+1)Δ^(2r+2) (s08 OPEN 2, unproven in general): an
extra global denominator factor would have to avoid producing any pole on
either slice line despite 100+ surplus equations each — no such factor is
visible, and the s08 recursion only ever inverts K- and Δ-type atoms, but
the global statement remains the successor's induction target.

## Curve amplitude: the anisotropic limit law

From the EXACT bivariate forms (r ≤ 1, both modes) the leading singular
amplitude C_r(x,y) = lim Δ^(2r+2)·M_r along the whole singular curve
Δ = 0, parametrized (x,y) = (a², (1-a)²), a ∈ (0,1), is

    C_0 = 8·(a(1-a))^5,   C_1 = 256·(a(1-a))^8      (both modes, exact),

which with C_r(1/2) = c_r = (r!)²/2^(r+7) forces the conjecture

    C_r(x,y) = (r!)² · 2^(5r+3) · (xy)^((3r+5)/2)   on Δ = 0.        (*)

Registered prediction (written before the run, `s09_slice_curve.py`): the
slice x = 1/9 (curve point a = 1/3, crossing y = 4/9, K = 49/81) must give
P_r(4/9)/K^(r+1) = (r!)²·2^(5r+3)·(2/9)^(3r+5). **Verdict: ALL MATCH** —
r = 0..6, both modes, both primes, surplus 38–99 equations per fit, and
Q_r(4/9) = 0 for r ≥ 1 on this slice too (`out_s09_slice_curve.txt`).
So (*) is exact on the whole curve for r ≤ 1, holds at a = 1/2 for
r ≤ 8 and at a = 1/3 for r ≤ 6: status firm.

Interpretation. In 2D singularity analysis the direction (w,h) selects the
saddle a* = w/(w+h) = α, so (*) is the moment-level statement of a
CONDITIONAL limit law: for animals of aspect w/s → α,

    area/s² →d c(α)·U(1-U),   c(α) = 32(α(1-α))³/A(α)²

with A(α) the normal-scale factor of Δ at a* (A(1/2) = 1, matching the
unconditional law and s07's fill-ratio picture 2U(1-U) in near-square
boxes). Per-level transfer factor: C_r/C_(r-1) = r²·32·(xy)^(3/2), which
at a = 1/2 is the r²/2 of the diagonal — this is the quantity the
blow-up induction must produce.

## What this changes

The area statistic itself is non-D-finite (s05/s06 route), but its moment
hierarchy is not just algebraic (s08) — its dominant singular data is
UNIVERSAL and explicit: c_r = (r!)²/2^(r+7), identical for the king
(polyplet) and polyomino families. The limit law area/s² →d U(1-U)/2 is
now pinned at moment level 8 with a mechanism (triple collision + factor-2
per level: c_r/c_(r-1) = r²/2) localized for a proof.

## Open

- Close the induction: from the blow-up frame (finding 2), prove
  c_r/c_(r-1) = r²/2 for all r (the r comes from the dominant
  inhomogeneity term r·D·M^(r-1); the /2 and the r from the local
  transfer at the triple collision).
- Prove the catalytic denominator law (finding 1) — this is the slice
  shadow of s08's OPEN 2 (K^(r+1)Δ^(2r+2)), now with exact exponents in
  the catalytic direction too.
- Prove Δ | B_r for all r ≥ 1 (finding 3).

## Addendum (session 12)

The headline law is now verified at moment level 12: c_r = (r!)²/2^(r+7)
and cQ_r = 0 for r = 0..12, both modes, both primes, surplus 55-179 per
fit (`out_s12_slice_r12.txt`, completing s11's dead run; r = 9..12 were
s11's registered prediction P1). Finding 4's conjecture "Δ | B_r" is
superseded by the exact multiplicity law nu_Δ(B_r) = ceil(r/2)
(`results/convex-area-local-structure.md`). Finding 2's inner-scale
constants are corrected there (u₋ - s* = +2δ², σ+ - s* = -2δ²), and the
open induction is localized: the c_r transfer closes in the (M10, M11)
two-phase subsystem with inhomogeneity r·D·M^(r-1), with channel
constants identical for king and polyomino.

## Addendum (session 13)

The localized c_r induction is EXECUTED AND SOLVED in
`results/convex-area-local-transfer.md`: the inner-chart profile
recursion has closed-form solution (Borel/Euler-series), giving
c_r = (r!)^2/2^(r+7) for ALL r and, by scaling covariance in the curve
parameter v (x = v^2, y_c = (1-v)^2), the curve-amplitude law
C_r = (r!)^2 2^(5r+3)(xy)^((3r+5)/2) — both at leading-order-closure
rigor (single stated gap: uniform-in-r subdominance).
