# Specializations x = -1 and x -> 1 of the row generating functions
### (session 06; proves s02's tentative halving identities and the A153337 closed form)

Setting: F(x,y) = sum f(w,h) x^w y^h for convex king animals, with the
kernel-proven closed form (docs/proofs/convex-box-kernel.md)

    F = -( M + 2 x^2 y^2 (1+x+y)^2 sqrt(Delta) ) / (2 K Delta^2),
    K = x+y+xy,  Delta = (1-x-y)^2 - 4xy,  M = the explicit degree-8
    polynomial of out_s02_KM.txt.

Row structure (s01/s02, verified h <= 18): [y^h] F = R_h(x) = N_h(x)/(1-x)^{2h-1}
with N_h an integer polynomial of degree 2h-1. All per-h statements below are
exact for h <= 18 by the banked table and hold for all h at the level of the
generating functions; extending the per-h reading to all h needs only the
row-rationality statement (poles of R_h only at x=1), whose mechanism is:
[y^h] of the algebraic part has x-denominators coming solely from the y-roots
y_pm = (1 +- sqrt(x))^2 of Delta (conjugate pairs recombine to powers of
y_+ y_- = (1-x)^2), while the potential pole at the K-root is removable since
M^2 - Delta*(2x^2y^2(1+x+y)^2)^2 = 4*K*A0 vanishes on K = 0 (s03, exact).

## 1. x = -1 (receipt: out_s06_specialize_pm1.txt, part A)

At x = -1: K = -1, Delta = 4 + y^2, (1+x+y)^2 = y^2, and the series branch
of sqrt(Delta) specializes to +sqrt(4+y^2) (both sides square to Delta(-1,y)
and agree at y=0, where sqrt(Delta)(x,0) = 1-x = 2). Exact substitution into
M gives M(-1,y) = -16y + 16y^2 - 20y^3 - 2y^5, so

    F(-1,y) = ( M(-1,y) + 2 y^4 sqrt(4+y^2) ) / ( 2 (4+y^2)^2 ).

Since N_h(-1) = 2^{2h-1} R_h(-1), the halved-argument repack gives, with
s := sqrt(1+4y^2)  (sqrt(4+16y^2) = 2s):

    Phi(y) := sum_{h>=1} N_h(-1) y^h  =  (1/2) F(-1, 4y)
            = (-y + 4y^2 - 20y^3 - 32y^5)/(1+4y^2)^2  +  16 y^4 s/(1+4y^2)^2.

Checked: series coefficients equal the banked N_h(-1) for h = 1..18, and the
closed form equals the series to y^44.

## 2. x -> 1 (receipt: out_s06_specialize_pm1.txt, part B)

Scale y = Y e^2, x = 1-e. Then Delta = e^2 W with W = (1-4Y) + 2Ye + Y^2e^2,
sqrt(Delta) = e sqrt(W), and F(1-e, Ye^2) = e * sum_h N_h(1-e) Y^h + O(e^2)
by the row structure. The single computational fact needed is

    M(1-e, Y e^2)  ==  -2Y e^5   (mod e^6),

an exact 19-term polynomial expansion (orders e^0..e^4 vanish identically in
Y). Substituting into the closed form and letting e -> 0 (exact truncated
bivariate series, coefficients in Q):

    G(Y) := sum_{h>=1} N_h(1) Y^h = lim_{e->0} F(1-e, Ye^2)/e
          = Y/(1-4Y)^2 - 4Y^2 (1-4Y)^{-3/2}.

Coefficient extraction gives N_h(1) = h 4^{h-1} - 2(h-1) C(2h-2,h-1): the
identification N_h(1) = A153337(h) (s02 claim 6, an 18-term observation) is
now PROVEN at generating-function level. Verified against the banked table
(h <= 18) and the binomial form (h < 44).

## 3. The halving identities (s02 claim 7: tentative -> proven)

Compare even/odd parts of Phi with G. The claim
N_{2k}(-1) = (-1)^{k+1} * 4 * N_k(1) is equivalent to
even(Phi)(y) = -4 G(-y^2); this splits into
  * sqrt components: 16 y^4 s/(1+4y^2)^2 = -4 * ( -4Y^2 (1-4Y)^{-3/2} )|_{Y=-y^2}
    -- identical on the nose, since (1+4y^2)^{-3/2} = s/(1+4y^2)^2; note the
    height-halving is literally the substitution Y = -y^2 bridging the two
    quadratic extensions sqrt(1-4Y) and sqrt(1+4y^2);
  * rational components: even(-y+4y^2-20y^3-32y^5) = 4y^2 vs
    -4*(-y^2) = 4y^2 -- identical.
The claim N_{2k+1}(-1) = (-1)^k (2k+1) 4^k (k >= 1) is equivalent to
odd(Phi) = y(1-4y^2)/(1+4y^2)^2 - 2y, i.e. to the polynomial identity
-y - 20y^3 - 32y^5 == y(1-4y^2) - 2y(1+4y^2)^2, which holds. The correction
term -2y is exactly the k = 0 boundary: N_1(-1) = -1 while the formula
would give +1; k = 0 is the sole exception.

Both identities are therefore consequences of the proven closed form,
uniformly in k. QED (modulo the row-rationality reading noted above).
