# Area moments of convex king animals are algebraic (session 07)

The full area generating function F(1,1,q) is a q-series with (numerically)
infinitely many poles in [0,1) — non-D-finite in mechanism (s04–s06). This
note establishes what IS tractable about area: **all its moments by
semiperimeter are algebraic over Q(t)**, in the same quadratic field
Q(t, sqrt(1-4t)) as the counting GF, with an explicit denominator law.

Statistic: a_r(s) = sum of area^r over convex king animals whose bounding
box (w,h) has w+h = s.  (a_0 = the s01/s03 kernel-proven counting
sequence.)  A_r(t) = sum_s a_r(s) t^s.

## Closed forms (fit + registered-prediction holdouts; see receipts)

King (S = sqrt(1-4t)):

  A_1 = [4t^2-52t^3+230t^4-348t^5+120t^6-84t^7-54t^8+80t^9+32t^10
         + (8t^3-29t^4-34t^5+100t^6-40t^7-32t^8) S] / [(2+t)^2 (1-4t)^4]

  A_2 = [8t^2+12t^3-444t^4+474t^5+7140t^6-23614t^7+25140t^8+766t^9
         -17936t^10+5936t^11+4928t^12-2304t^13-1024t^14
         + (-128t^3+1010t^4-2093t^5-470t^6+3534t^7+1428t^8-6548t^9
            +16t^10+3344t^11+960t^12) S] / [(2+t)^3 (1-4t)^6]

Control (convex polyominoes; perimeter statistic 2s):

  A_1 = [t^2-12t^3+50t^4-76t^5+42t^6-48t^7+32t^8] / (1-4t)^4
        + 4t^4 / (1-4t)^{5/2}

  A_2 = [t^2-16t^3+172t^4-1116t^5+4062t^6-8304t^7+10160t^8-7872t^9
         +3840t^10-1024t^11
         + (-54t^4+528t^5-1896t^6+3216t^7-2736t^8+960t^9) S] / (1-4t)^6

**Denominator law: A_r has denominator (2+t)^(r+1) (1-4t)^(2r+2) [king],
(1-4t)^(2r+2) [control]** — extending the r=0 proven forms ((2+t)(1-4t)^2
by s01/s03; (1-4t)^2 Delest–Viennot). This is the Temperley-moment
signature: each d/dq at q=1 raises the kernel-factor multiplicities by
(1,2).

Evidence class: exact overdetermined fits (17–29 surplus equations) PLUS
two rounds of registered predictions — closed forms fitted on s<=37
(resp. s<=46) predicted all freshly-computed DP terms s=38..46 (resp.
47..52), 6–9 unseen 30–36-digit integers per sequence, zero failures.
Data from a moment-extended row-interval DP validated against (i)
definitional subset brute force (wh<=16, r<=4), (ii) the s04 joint truth
table f(w,h;n) on 100 boxes per mode, (iii) transpose symmetry, (iv) a0 ==
banked proven sequences.

## Bivariate closed forms (by exact bounding box)

With D = (1-x-y)^2-4xy, K = x+y+xy (the s02/s03 kernel objects):

  M1_king(x,y) = (A + B sqrt(D)) / (K^2 D^4)
  M1_poly(x,y) = (A' + B' sqrt(D)) / D^4

A (deg 9,9; 68 monomials, coeffs <=86), B (27 monomials) — full
polynomials in out_s07_bivar_verify.txt / out_s07_bivar_moment.json;
control A' (22 stored terms), B' (7) in ..._poly variants. Fit by modular
linear algebra at two independent 61/63-bit primes (unique solution,
overdetermined 729-equation grid, both consistent), CRT-lifted to small
integers, then verified EXACTLY over Z on the full [0..26]^2 coefficient
grid, and the diagonal x=y=t reproduces the univariate A_1 exactly.
Denominator law bivariate: K^(r+1) D^(2r+2) (king), D^(2r+2) (control);
K(t,t)=t(2+t), D(t,t)=1-4t recover the univariate law.

## Asymptotics and the limit law

Exact singularity analysis (u = 1-4t) of the closed forms gives, for BOTH
families (identical constants!):

  E[area]/s^2   -> 1/12
  E[area^2]/s^4 -> 1/120     Var[area]/s^4 -> 1/720

These are the first two moments of X = U(1-U)/2 with U ~ Uniform(0,1):
E[X^r] = (r!)^2/((2r+1)! 2^r).  The width profile f(w,s-w) is
CONCENTRATED at w=s/2 (checked numerically at s=30: sharp bell), so the
correct geometric decomposition is: bounding box -> square (s/2 x s/2),
and the FILL RATIO area/(wh) converges in law to 2U(1-U) — density
1/sqrt(1-2*rho) on (0,1/2) — with area/s^2 = rho/4 =d U(1-U)/2.

Registered prediction (out_s07_limit_law_prediction.txt, written before
any r>=3 data existed): E[area^3]/s^6 -> 1/1120, E[area^4]/s^8 -> 1/10080,
p_0(A_3)=9/256, p_0(A_4)=9/32, both modes.  [Test outcome: see session-07
report / out_s07_r4_fit.txt.]

## Receipts

- experiments/s07_area_moments.py, out_s07_area_moments{,46,52}.{txt,json}
- experiments/s07_moment_fit.py, out_s07_moment_fit.txt
- experiments/s07_predict_holdout.py, out_s07_predictions{,2}.json,
  out_s07_holdout_check{,2}.txt
- experiments/s07_moment_asymptotics.py, out_s07_moment_asymptotics.txt
- experiments/s07_bivar_moment.py / s07_bivar_verify.py,
  out_s07_bivar_moment{,_poly}.{txt,json}, out_s07_bivar_verify{,_poly}.txt
- experiments/s07_area_moments_r4.py (r<=4 generalization)

## Open (proof path)

Differentiate the s03 kernel-proven functional equation (s04's q-FE at
z=qs) w.r.t. q at q=1: the moment FEs are linear with the SAME kernel and
inhomogeneous terms built from the (proven) r'<r solutions; the kernel
roots are q-independent, so the kernel method closes each level. This
would upgrade every claim above to theorem, r by r, and prove the
denominator law by induction.

## Width fluctuations (companion tractable statistic)

E[w|s] = s/2 exactly (w_1(s) = s a_0(s)/2, x<->y symmetry, verified).
W_2(t) = (x d/dx)^2 F|_{x=y=t} is PROVABLY algebraic (F is proven);
identified exactly: king [P+Q sqrt(1-4t)]/((2+t)^3(1-4t)^4) with
P = 8t^2-68t^3+343t^4-840t^5+512t^6+1028t^7-386t^8-1254t^9-624t^10-96t^11,
Q = -8t^3-53t^4+133t^5+353t^6-610t^7-808t^8-336t^9-48t^10; control
[t^2-11t^3+62t^4-170t^5+186t^6+16t^7-96t^8 + (-16t^4+68t^5-64t^6-48t^7)S]
/(1-4t)^4.  Consequence (exact singular expansions, receipt
out_s07_width_moments.txt): Var(w|s) = s/8 + O(sqrt s) — the SAME
constant for king and control.  So the full picture by semiperimeter:
box width = s/2 + Gaussian-scale sqrt(s/8) fluctuations, fill ratio
converges to the non-Gaussian law 2U(1-U); the area limit law
U(1-U)/2 is driven entirely by the fill ratio.

## Addendum (session 08): proof path EXECUTED; r=3,4 predictions CONFIRMED

The "Open (proof path)" above is now done: the level-r moment system has
inhomogeneity I^(r) = sum_{k<r} (-1)^(r-1-k) C(r,k) D^(r-k) M^(k)
(D = s d/ds) and is closed by the SAME kernel roots at every level —
executed for r <= 4, king and control, in exact truncated series
arithmetic at primes 2^61-1, 10^18+9 and 2^521-1, matching the joint
truth table, the independent moment DP, and the fitted bivariate M1
closed form on every compared coefficient. THE MOMENT GFs M_r(x,y) AND
A_r(t) ARE ALGEBRAIC (elements of Q(x,y,sqrt(Delta)) resp.
Q(t,sqrt(1-4t))) FOR EVERY r, constructively. Proof + receipts:
docs/proofs/area-moment-kernel.md, experiments/s08_moment_kernel.py,
out_s08_moment_kernel_16x16_r4.txt, out_s08_moment_kernel_10x10_r4_big.txt.

The registered r=3,4 predictions (out_s07_limit_law_prediction.txt) were
tested against fresh SMAX=57 DP data (out_s07_area_moments_r4_57.json,
the run that died in s07): CONFIRMED — denominators (2+t)^4(1-4t)^8 and
(2+t)^5(1-4t)^10 [king] / (1-4t)^8, (1-4t)^10 [control], p_0(A_3)=9/256,
p_0(A_4)=9/32, E[area^3]/s^6 -> 1/1120, E[area^4]/s^8 -> 1/10080, both
modes, surplus 12-28 equations per fit. Receipt: out_s07_r4_fit.txt.
Explicit A_3, A_4 numerators are banked there.
