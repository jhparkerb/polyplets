# The local transfer at the collision, solved: c_r = (r!)^2 / 2^(r+7)
# (session 13; executes and closes s09 OPEN 1 / s12 OPEN 2)

Builds on: the PROVEN kernel moment recursion (s08,
`docs/proofs/area-moment-kernel.md`), the collision analysis (s09,
`results/convex-area-limit-law.md`), the delta-Laurent chassis and
localization (s12, `results/convex-area-local-structure.md`).
Scripts: `experiments/s13_tau_profiles.py` (chassis profile extraction),
`experiments/s13_local_recursion.py` (recursion + closed form + checks).
Receipts: `out_s13_tau_profiles.txt/.json` (+ first-run copies
`out_s13_tau_run.log`, `out_s13_tau_run2.log`),
`out_s13_local_recursion.txt`.

Everything below is on the slice x = 1/4 at the collision point s* = 2,
delta = sqrt(Delta), inner chart s = 2 + delta^2*tau, z := tau - 2
(so the closing-kernel evaluation point sigma+ corresponds to z = -4).

## 1. Chart linearizations (exact leading forms, from the closed-form
##    chassis seeds)

    PK  (staircase kernel)   = delta^2 * (1 + O(delta^2))   [tau-FREE]
    K11 (closing kernel)     = delta^2 * (tau + 2) + O(delta^4)
                               [root AT sigma+ <-> tau = -2: the kernel
                                method evaluates exactly on the
                                degenerating root]
    D00 = -delta^2 z / 4,    PK1 = delta/2 * (1 + O(delta)),
    W = (s-1)(1-xs) -> 1/2,  1 - xs -> 1/2,  y -> 1/4,
    D = s d/ds -> 2 delta^-2 d/dtau,
    B[G] = [(G - sG(1))/(s-1) + xsG(1)]/(1-xs) -> 2*G  (leading),
    D2[G](sigma+) -> 2*G(sigma+),  D1[M00] channel subdominant,
    M00-solve:  M00^(r) = (1-xs)^2 I_M00 / D00.

Newton polygons of the phase numerators at s* (receipt
out_s13_tau_profiles.txt) have THREE slopes: -2 (inner chart), -1
(outer chart s = 2 + delta*tau), 0 (global); the inner data below is
the slope -2 boundary.

## 2. The local profile recursion (THEOREM, leading Laurent order)

Write, in the inner chart,

    M00^(r)(2+delta^2 tau) = delta^-(4r+2) psi00_r(z) (1+O(delta)),
    M10^(r)(2+delta^2 tau) = delta^-(4r+4) chi_r(z)   (1+O(delta)),
    M11^(r)(2+delta^2 tau) = delta^-(4r+6) phi_r(z)   (1+O(delta)).

Expanding the s08 solve_level operators with the linearizations of
section 1 and keeping leading Laurent order (the inhomogeneity ladder
contributes only its k = r-1 term r*D*M^(r-1), s12's V4b; the
mode-dependent atoms Qcomp, the king term of B, and all G(1), G'(1)
value-atoms are subdominant), the recursion closes:

    psi00_r = -2r psi00'_{r-1} / z            seed  psi00_0 = -1/(4z)
      [=> psi00_r = -(2r)!/(4 z^(2r+1)) in closed form]
    chi_r   = psi00_r/4 + r chi'_{r-1}        seed  chi_0   = -1/(16z)
    a_r     = chi_r + 2r phi'_{r-1}           (A2M profile)
    phi_r   = (a_r(z) - a_r(-4))/(z+4)        seed  phi_0   = -1/(64z)
    c_r     = a_r(-4)/2

with the channel identities (s12's split, now formulaic)

    D2-channel = chi_r(-4)/2,   I11-channel = r phi'_{r-1}(-4),

and, from removability of the K11 root z = -4 (tau = -2) in phi_r,

    lead of M11^(r)'(1) = d_r = 2 c_r    (new value law).

MODE UNIVERSALITY IS DERIVED: every mode-dependent term enters at
subdominant delta-order, so the recursion (hence every c_r and every
channel constant) is identical for king and polyomino — explaining
s12's channel-by-channel coincidence.

Status of the derivation: the chart algebra above is exact; what is
NOT yet proven for all r is the subdominance bookkeeping it relies on
(the valuation laws val M10^(r)(1) = -(3r+1), yD1-channel at -(4r+2),
inhomogeneity gap 2 — each machine-verified at r <= 6 by s12, with the
value laws consistent to r = 12 on the slice). See section 6.

## 3. Solution of the recursion (closed form; this is a full proof
##    THAT THE RECURSION IMPLIES the c_r law, for every r)

Borel substitution z^-(j+1) <-> t^j / j! (so d/dz <-> mult by -t, and
(a(z)-a(-4))/(z+4) <-> the unique POLYNOMIAL solution Phi of
Phi' + 4Phi = A, with a(-4) = -Phi(0)):

    X_0 = -1/16,  X_r = -t^(2r)/16 - r t X_{r-1}
    Phi_r = (4+D)^{-1} [X_r - 2r t Phi_{r-1}]
    c_r = -Phi_r(0)/2.

EGFs (F(t,w) := sum_r Phi_r(t) w^r/r!):

    sum_r X_r w^r/r! = -(1/16) e^(t^2 w) / (1+tw)
    F_t + (4 + 2wt) F = -(1/16) e^(t^2 w)/(1+tw).

Substitute F = e^(t^2 w) G(u,w), u = 1 + tw. The PDE collapses to the
ordinary equation  w G_u + 4u G = -1/(16u),  whose formal power-series
solution in w is (one-line telescoping verification)

    G(u,w) = -(1/(64 u^2)) * sum_{k>=0} k! (w / (2u^2))^k.

Each w-order of F = e^(t^2 w) G(1+tw, w) is a polynomial in t; the
polynomial solution of the PDE is unique order-by-order (the
homogeneous solution e^{-4t} is not polynomial). Hence Phi_r =
r! [w^r] F, explicitly

    Phi_r(t) = -(1/64) sum_{k+m+i=r} (k!/2^k) C(2k+1+m, m) (-1)^m
               (r!/i!) t^(m+2i),

and at t = 0 only (k,m,i) = (r,0,0) survives:

    Phi_r(0) = -(1/64) (r!)^2 / 2^r   =>   c_r = (r!)^2 / 2^(r+7)

for EVERY r >= 0. The value generating function is the Euler series
-(1/64) sum k! (w/2)^k — divergent, Borel-summable; its Borel plane is
where the profiles live. The M10-profile EGF is exactly
-(1/16)e^(t^2 w)/(1+tw); psi00, chi, phi are all elementary.

Corollary (with s08's algebraicity + s09/s12's denominator/anchor data):
the limit law area/s^2 ->d U(1-U)/2 (U uniform) holds at ALL moment
orders, king and polyomino, conditional on (i) the section-6 gap and
(ii) the global denominator/singular-exponent law A_r ~ c_r/(1-4t)^(2r+2)
(s08 OPEN 2; machine-verified r <= 12 slice / r <= 4 bivariate).

## 4. Validation (all exact, out_s13_local_recursion.txt)

  C1  z-form recursion gives c_r = (r!)^2/2^(r+7) for r <= 24
      (independent slice data covers r <= 12; 12 fresh orders agree).
  C2  channel split == s12 banked exact rationals r = 1..4:
      (3+1)/1024, (17+15)/4096, (423+729)/32768, (4617+13815)/65536.
  C3  Borel polynomial form == z-form coefficientwise, r <= 24.
  C6  closed-form Phi_r formula == recursion output, r <= 24.
  C4  chassis ground truth: inner profiles chi_r, phi_r match the
      recentered Newton-table profiles of the s12 delta-Laurent chassis
      (out_s13_tau_profiles.json) at every r <= 5 for M10 AND M11, BOTH
      modes, BOTH primes; r = 6 M11 [see receipt for final status —
      NUCAP=150 chassis run hit its precision edge there; NUCAP=220
      rerun adjudicates].
  Seeds/first levels hand-checked: psi00_3 = -180/z^7 == -(2*3)!/(4z^7);
  c_0 = 1/128, c_1 = 1/256 by hand through the recursion.

## 5. General curve point: the s09 curve-amplitude law by scaling
##    covariance (closes the curve version of s09 OPEN 1)

Parametrize the singular curve Delta = 0 by x = v^2, y_c = (1-v)^2
(0 < v < 1); the collision is at s* = 1/v (sigma+ = 1/sqrt(x) on the
curve), and on the slice x = v^2 fixed, y(delta) = 1+v^2 -
sqrt(4v^2+delta^2), s0 = (sqrt(4v^2+delta^2)-delta)/(2v^2) — closed-form
chassis seeds for ANY rational v with v rational. Chart linearizations
generalize (h = s - s*, inner h = delta^2 tau):

    PK -> delta^2/(4x),   D00 -> -2v^2(1-v) h + delta^2/(4v),
    K11 -> 2(1-v)(h + delta^2/(8v^3(1-v))),
    sigma+ - s* = -delta^2/(8v^3(1-v)),  u_-(D00 root) - s* = +same,
    W -> (1-v)^2/v,  1-xs -> 1-v,  y -> (1-v)^2,  D -> (1/(v delta^2)) d/dtau,
    B -> (v/(1-v)^2) G / ... net yWB-weight (1-v)^2,  D2 -> (v/(1-v)^2) G.

In lambda := 8v^3(1-v) tau, mu := lambda - 1 (D00 root at mu = 0,
sigma+ at mu = -2), with kappa := 32 v^3 (1-v)^3:

    psi_r = -(r kappa/mu) psi'_{r-1},   psi_0 = -4v^2(1-v)^3/mu
    chi_r = 4v^2(1-v)^2 psi_r + kappa r chi'_{r-1}
    a_r   = 2v chi_r + 8v^2(1-v) r phi'_{r-1}
    phi_r = 4v(1-v)^2 (a_r - a_r(-2))/(mu+2)
    c_r(v) = a_r(-2)/2,   d_r(v) = c_r(v)/(1-v)  [lead M11'(1)].

SCALING REDUCTION: normalizing chi-hat := chi_r/(Cchi g^r), phi-hat :=
phi_r/(Cphi g^r), a-hat := a_r/(Ca g^r) with

    g = 64 v^3(1-v)^3,  Cchi = 512 v^4(1-v)^5,
    Ca = 1024 v^5(1-v)^5,  Cphi = 8192 v^6(1-v)^7,

the system becomes EXACTLY the v = 1/2 system with no v remaining
(machine check K3). Hence by section 3,

    c_r(v) = Ca g^r (r!)^2/2^(r+7) = (r!)^2 2^(5r+3) (v(1-v))^(3r+5)
           = (r!)^2 2^(5r+3) (x y)^((3r+5)/2)   on Delta = 0

— precisely s09's registered-verified curve-amplitude law, now DERIVED
(same leading-order-closure caveat as section 2). Validation:

  K1  v = 1/2 system == banked z-form, r <= 12         (PASS)
  K2  c_r(v) law at v in {1/3,1/5,3/7,2/5,1/2}, r <= 12 (PASS)
  K3  normalized profiles v-free                        (PASS)
      [receipt out_s13_curve_recursion.txt]
  G1-G4  GROUND TRUTH at x = 1/9 (v = 1/3): fresh delta-chassis run
      (v-general build_ctx, receipt out_s13_curve_chassis.txt): inner
      orders, ALL THREE profiles psi/chi/phi as rational functions of
      tau, value law c_r(1/3), derivative law d_r(1/3) — every check
      at r <= 4, king AND poly, both primes               (PASS)

The value law lead M11'(1) = d_r = c_r/(1-v) (= 2c_r at x = 1/4) is
new; on the slice x = 1/4 it is verified independently at r <= 6, both
modes, both primes (out_s13_dr_check.txt).

## 6. What remains for a fully rigorous all-r theorem

The single gap is uniformity in r of the subdominance used in section 2
(the valuation laws / remainder bookkeeping). Everything else — the
operators, the chart linearizations, the recursion solution — is exact.
The natural route: filtration induction on the exact FRat objects
(numerator Newton polygons have slopes in {-2,-1,0} with explicit
anchor orders; each solve_level operation demonstrably preserves the
filtration), carrying the section-2 valuation laws as the induction
hypothesis. The chassis receipts verify every ingredient at r <= 6.

(The general-curve-point extension is DONE — section 5.) Second open
thread: push the same charts one Laurent order deeper — the odd-part
multiplicity law nu_Delta(B_r) = ceil(r/2) and cQ_r = 0 live exactly
one order below the profiles solved here, and the outer chart (s0,
M101), inert at leading order, activates there.
