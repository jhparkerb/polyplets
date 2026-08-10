# Bivariate depth GF G(y,t): no closed form (dead end)

Recorded 2026-08-10. Closes the "stack the depths into one bivariate algebraic
G(x,t)" idea from the Severance W4 plan. The fixed-depth slices F_j(y) remain
individually algebraic (depth 1 proved, depths 2–4 exact); it is the *bivariate*
object that has no closed form, for a reason already banked.

## The object

Mark below-onset depth with t: G(y,t) = Σ_j t^j F_j(y), F_j(y) = Σ_k D_j(k) y^k.
Writing i = k+1−j for the z-power,

    G(y,t) = Σ_k y^k Σ_j t^j [z^{k+1-j}] D_k(z)
           = Σ_k y^k · t^{k+1} Σ_i t^{-i}[z^i]D_k(z)
           = t · Σ_k (yt)^k D_k(1/t)  =  t · F(yt, 1/t),

where F(y,z) = Σ_k y^k D_k(z) is the below-onset column generating function
(D_k(z) the correction polynomial at surplus k). So G is not a new object: it is
the below-onset master GF under the birational substitution (y,z) → (yt, 1/t).
Depth-slicing was reading its anti-diagonals.

## Why there is no closed form

Fix a height H. The strip GF G_H(x) = Σ_n T(n,H) x^n has onset (diagonal
k = n−H at n = 2k+1) at n = 2H−1, so all but finitely many of its terms are
below onset: G_H equals a fixed-height section of F(y,z) plus a polynomial.

The banked theorem `results/anisotropic-not-dfinite.md` (unconditional,
2026-07-15) gives deg_ℚ(μ_H) → ∞ for the strip growth constants
μ_H = 1, 1+√2, 3.44372, … (atom degrees 1,2,4,9,29,68,181,462,…), via
Northcott finiteness plus strict monotonicity. Adding a polynomial does not move
a radius of convergence, so those same μ_H are the growth constants of F(y,z)'s
fixed-height sections. A D-finite bivariate function has fixed-height sections
whose singularities have bounded algebraic degree; F(y,z) does not. Hence

    G(y,t) is not D-finite — a fortiori not algebraic. No global closed form,
    and no holonomic ODE either.

## The empirical shadow (independent of the theorem)

If G(y,t) were algebraic over ℚ(y,t), every t-coefficient F_j(y) would be
algebraic over ℚ(y) of *uniformly bounded* degree (each lies in the field of
G's branches). The field tester `experiments/severance_w4_field.py` measures the
opposite:

  * depth 1: minimal box (deg_y = 8, deg_W = 4)  [= kernel-derived Φ_1];
  * depth 2: NO relation with deg_W ≤ 4 up to deg_y = 18, none with deg_W ≤ 6
    up to deg_y = 12 (mod-p scan at K = 110, 16-row holdout).

Slice degree 4 → ≥ 7 and climbing is exactly what an inalgebraic G forces. This
also settles the narrower W4 hypothesis (all depths in depth-1's biquadratic
field K = ℚ(s)[A,B]) in the negative: depth 2 is not even degree ≤ 6.

## What survives

The theorem kills the full function, not its dominant-singularity data. The
near-onset amplitudes do have a closed form: with t marking depth,

    Σ_j A_j t^j = (√6/27) · t / √(1 − 50t/81)   (branch t = 81/50),

algebraic in t — the double-scaling function at the onset ridge. That is the
tractable target for the depth direction (see the amplitude/subleading work in
`results/onset-defect-depth1-closed.md`), not the full G.

**But this GF is a four-point fit (j ≤ 4), and it cannot be settled by more
data.** `onset-defect-law.md` §2: at j = 5 the conjectured 35/8 sits *outside*
the measured bar while 118/27 sits inside. Sharpening R_5 needs D_5(k) to
k ≈ 28–30; the triangle−law extraction is capped at k ≤ 18 by P_k (the a40
frontier), and the only independent route (ab-initio D_5 via excess-4 families)
is the W4 wall — measured 2026-08-10: Python `families(12,emax=4)` > 130 s,
C++/10-thread `families(16,emax=4)` > 200 s, and k ≈ 30 is a many-hour-to-days
job for one point. So a fit is structurally dead: the data runs out at exactly
the depth where the family goes ambiguous.

The only path that settles the amplitude family is a **derivation** — the onset
double-scaling limit (local expansion of the depth-1 kernel D(u)=u²−y(1+u+u²)²
near its branch point y=1/9, with depth as the slow coordinate), a W2-sized
piece of analysis. Not pursued: algebraicity of the scaling function is genuinely
uncertain (the measured layer exponent p≈0.39 is consistent with 1/2 → algebraic
√, but does not exclude 1/3 → Airy/transcendental), and the project is in
close-out. Recorded here as the pickup point if the depth direction is revived.

Tooling: `experiments/severance_w3_modp.py` (mod-p D_j(k), 7.4× over the exact
bignum path) and `experiments/severance_w4_field.py` (the field tester).
