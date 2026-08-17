# Proof plan: area-moment GFs via the Temperley moment method (s07, SKETCH)

STATUS: recipe only — nothing below is derived/validated yet. The target
closed forms it should produce ARE established numerically at high
confidence (registered-prediction holdouts; results/convex-area-moments.md).

STATUS UPDATE (session 08): EXECUTED. The recipe works at every moment
level; see docs/proofs/area-moment-kernel.md (general level-r
inhomogeneity formula, kernel closure, machine execution r <= 4 with all
checks passing, receipts out_s08_moment_kernel_*.txt). The r=3,4
registered predictions referenced below were tested and CONFIRMED
(out_s07_r4_fit.txt).

## Setup

s04 proved (validated transitions + unique power-series solution) the
q-deformed functional-equation system: every s03 operator formula with
z := q s, G(1), G'(1) fixed, i.e. schematically

  F00(s;q) = O_00[F00](s;q) + init(s;q)
  F10(s;q) = y B_q[F00](s;q) + y C_q[F10](s;q)
  F11(s;q) = y D1_q[F00](s;q) + 2y D2_q[F10](s;q) + y L3_q[F11](s;q)

where each operator evaluates its argument at qs and at 1 (boundary
terms G(1), G'(1) are NOT q-shifted).

## Moment functions

Define G_ph^{(r)}(s) = (q d/dq)^r F_ph(s;q) |_{q=1}.  Then
A_r(t)|_{x=y=t} = G^{(r)}(1) assembled as usual (F00+2F10+F11 parts).

Apply (q d/dq)^r to each equation and set q=1.  Key structural facts:

1. (q d/dq) hits an operator term Op[G](qs) as
   [Op[G^{(1)}]](s) + [s d/ds Op[G]](s) at q=1 — i.e. the SAME operator
   applied to the next moment, plus s-derivative terms of LOWER moments.
   The s-derivatives of the r'<r solutions are explicitly known algebraic
   functions once the induction has reached level r.
2. The homogeneous part of the level-r equation for G^{(r)} is IDENTICAL
   to the level-0 one (same kernel: xs^2-(1+x-y)s+1 for the staircase
   phase, (s-1)^2=ys^2 for the closing phase).
3. Hence the kernel method closes level r with the SAME kernel roots
   s0(x,y), sigma_pm(x,y) in Q(x,y,sqrt(D)): substitute the roots, kill
   the unknown-function term, solve the linear system for the unknowns
   G^{(r)}(1), (d/ds G^{(r)})(1).

## Predicted outcome (to be matched against banked forms)

Each substitution of a kernel root into an inhomogeneous term containing
d/ds of a level-(r-1) solution raises the multiplicity of the kernel
factors: D gains 2, K gains 1 per moment level. This is exactly the
observed law

  denominator(A_r) = K^{r+1} D^{2r+2}   (king; control: K = 1)

with banked numerators (r=1 bivariate: out_s07_bivar_moment.json — use it
as the ground truth for the derivation; specialization checks are in
out_s07_bivar_verify.txt).

## Suggested execution (one session)

- Implement level r=1 only, x,y symbolic via the s03/s04 exact-series
  framework (two primes + exact-Q close, as in s04_exact_close.py).
- Derive d/ds F_ph(s)|_{s-series} from the proven level-0 closed forms
  (rational operations + sqrt(D) only).
- Kernel-substitute, solve the 2x2 linear systems, assemble, and compare
  against out_s07_bivar_moment.json — coefficient-exact match = THEOREM
  for A_1 (and the s07 asymptotic constants E[area]/s^2 = 1/12 etc.
  become theorems for r<=1 automatically).
- Induct r=2 if time permits.

## Limit-law endgame

All moments E[area^r]/s^{2r} -> (r!)^2/((2r+1)! 2^r) (registered, r<=4
tested — see out_s07_r4_fit.txt) identify the law of area/s^2 as
U(1-U)/2, U~Uniform(0,1) (moment problem on a bounded variable =>
determinate). Proving the constants for ALL r via the induction above
would prove the limit law, and with it the fill-ratio law 2U(1-U).
