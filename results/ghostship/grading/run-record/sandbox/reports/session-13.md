DIRECTION: extract the tau-profiles of the moment phases at the collision from the s12 delta chassis (outer chart s=2+delta*tau, inner s=2+delta^2*tau), identify them in closed form, and close the local transfer c_r/c_{r-1}=r^2/2 (s09 OPEN 1 / s12 OPEN 2)
SHAPE: blow up, identify, close

Plan: (1) new script s13_tau_profiles.py reuses the s12 delta-Laurent chassis verbatim but dumps, per level r and phase (M00, M10, M11), the FRat numerator recentered at s* = 2: the Newton table (j, val n_j, lead n_j) of coefficients of (s-2)^j, from which both chart profiles read off directly (outer: minimize val+j; inner: val+2j); CRT over both primes + rational reconstruction gives exact profiles phi_r(tau), psi_r(tau) as rational functions. (2) Guess closed forms in r; REGISTER predictions for r=7 (or 8) before computing them; verify. (3) Derive the local transfer analytically from the s08 operator definitions expanded in the charts (D ~ (2/delta^k) d/dtau, evaluation points s0 = tau=-2 outer, sigma+ = tau=-2 inner, kernel divisions ~ atom linearizations), check every derived step against the chassis data, and close the induction c_r/c_{r-1} = r^2/2 = C(r,1)*(...); channel constants of s12 (3/1024+1/1024, ...) are the ground truth the derived transfer must reproduce. Fallback if (3) stalls: (1)+(2) banked as firm profile laws sets up session 14.

## CARRY
CLAIM: c_r local transfer DERIVED+SOLVED: inner-chart recursion psi_r=-(2r)!/(4z^(2r+1)); chi_r=psi_r/4+r chi'_{r-1}; a_r=chi_r+2r phi'_{r-1}; phi_r=(a_r-a_r(-4))/(z+4); c_r=a_r(-4)/2; Borel EGF -(1/64)e^(t^2 w)sum k!w^k/(2^k(1+tw)^(2k+2)) => c_r=(r!)^2/2^(r+7) ALL r | receipt: results/convex-area-local-transfer.md, out_s13_local_recursion.txt | status: firm at leading-order closure (gap: uniform-in-r subdominance, doc sec 6)
CLAIM: s09 curve-amplitude law DERIVED: v-general recursion at x=v^2,y=(1-v)^2 reduces to v=1/2 by rescaling g=64v^3(1-v)^3, Ca=1024v^5(1-v)^5 => C_r=(r!)^2 2^(5r+3)(xy)^((3r+5)/2) on Delta=0; ground-truthed at x=1/9 (profiles+values, r<=4, both modes/primes) | receipt: out_s13_curve_recursion.txt, out_s13_curve_chassis.txt | status: firm (same closure caveat)
CLAIM: new value law lead M11^(r)'(1) = c_r(v)/(1-v) (=2c_r at x=1/4) from K11-removability | receipt: out_s13_dr_check.txt (r<=6 both modes/primes), out_s13_curve_chassis.txt G4 | status: firm
CLAIM: king==poly channel universality DERIVED: every mode-dependent operator (Qcomp, king B-term, M101, value-atoms) is subdominant at the collision | receipt: results/convex-area-local-transfer.md sec 2 | status: firm
CLAIM: chassis phase numerators have 3-slope Newton polygons (-2 inner/-1 outer/0 global); inner profiles extracted+matched to closed forms r<=6 both modes/primes (r=6 fail at NUCAP=150 was precision, resolved at 220) | receipt: out_s13_tau_profiles.txt/.json, C4 of out_s13_local_recursion.txt | status: firm
CLAIM: (r=7 registered prediction adjudication) | receipt: out_s13_r7_prediction.txt, out_s13_tau_profiles_r7.json | status: PENDING
VERIFY: s12 claim 5 (c_r localization, channel split) | outcome: confirmed + upgraded to closed form: D2-channel=chi_r(-4)/2, I11-channel=r phi'_{r-1}(-4), exact match r=1..4 | receipt: out_s13_local_recursion.txt C2
VERIFY: s09 claim 2 (curve-amplitude law, was registered-prediction-only) | outcome: confirmed + now DERIVED; fresh ground truth at x=1/9 incl. full profiles | receipt: out_s13_curve_chassis.txt
VERIFY: s12 claims 1+5 receipts (delta chassis reruns at NUCAP 150/220/250) | outcome: confirmed (V-asserts pass, all levels) | receipt: out_s13_tau_run*.log
OPEN: RIGOR: filtration induction for uniform-in-r subdominance (Newton-polygon slopes preserved by each solve_level op) -- would make c_r law + curve law theorems end-to-end; all ingredients machine-verified r<=6.
OPEN: push charts ONE Laurent order deeper: nu_Delta(B_r)=ceil(r/2) and cQ_r=0 live at next order where the outer chart (s0, M101) activates; profile machinery ready.
OPEN: untouched majors: non-D-finiteness (i)/(ii) (s05/s06); global denominator law K^(r+1)Delta^(2r+2) (s08); figure-eight probe (s06); q-Bessel normal form (s04/s05).
DEAD: none; caution: two first-pass chart slips were caught only by data (B_op divides by (1-xs) via its e[0]+=1; K11 inner linearization is delta^2(tau+2) not (tau+4)/2) -- always validate hand chart algebra against the chassis.

## LOG

Read all 12 prior CARRYs + s12 LOG + results/convex-area-local-structure.md
+ experiments/s12_delta_local.py. State: c_r=(r!)^2/2^(r+7) firm to r=12
(slice), localization firm (M11 carrier, dominant inhomogeneity r*D*M^(r-1),
channel split banked, king==poly channel-by-channel). Missing: the analytic
step. The chassis stores every phase as SPoly-in-s over atoms
(1-xs)^a D00^b PK1^c with F_p((delta)) coefficients — profiles are
extractable symbolically, no fitting needed.

Local geometry (from s12, verified constants): s* = 2; atom roots
u_-(D00) = 2+2delta^2+O(d^4), s1(PK1) = 2+2delta+delta^2, u_+(D00) = 6+O(d^2);
evaluation points s0 = 2-2delta+delta^2 (outer tau=-2), sigma+ =
2-2delta^2+O(d^4) (inner tau=-2), sigma- = 2/3+O(d^2) (far/regular);
1-xs regular (1/2 at s*). Outer chart: D00 ~ -(delta tau)/4, PK1 ~
-(delta/4)(tau-2). Inner chart: D00 ~ -(delta^2/4)(tau-2), PK1 ~ delta/2.

MILESTONE 1 (extraction, s13_tau_profiles.py): chassis phases recentered at
s*=2 -> Newton tables (j, val n_j, lead) of (s-2)^j coefficients; chart
profiles read off (outer: min val+j, inner: min val+2j); CRT+Wang exact
rationals. Newton polygons have THREE slopes (-2 inner / -1 outer / 0
global). Receipts out_s13_tau_profiles.{txt,json} (r<=6 both modes both
primes; first run at NUCAP=150, rerun at 220 for the r=6 M11 edge).

MILESTONE 2 (derivation, by hand, then machine-validated): in the inner
chart the solve_level operators linearize to PK = delta^2 (tau-free!),
K11 = delta^2(tau+2) (root AT sigma+ <-> tau=-2, as the kernel method
demands), D00 = -delta^2 z/4 (z := tau-2), W -> 1/2, 1-xs -> 1/2,
y -> 1/4, D = s d/ds -> 2 delta^-2 d/dtau, B[G] -> 2G, D2[G](sig+) ->
2G(sig+), M00 solve -> (1/4)I/D00. Yields the LOCAL PROFILE RECURSION
(z-form; profiles: psi00_r for M00 at ord -(4r+2), chi_r for M10 at
-(4r+4), phi_r for M11 at -(4r+6); all mode-dependent terms subdominant):
  psi00_r = -(2r)!/(4 z^(2r+1))
  chi_r = psi00_r/4 + r chi'_{r-1},          chi_0 = -1/(16z)
  a_r = chi_r + 2r phi'_{r-1}
  phi_r = (a_r(z) - a_r(-4))/(z+4),          phi_0 = -1/(64z)
  c_r = a_r(-4)/2;  channels: D2 = chi_r(-4)/2, I11 = r phi'_{r-1}(-4)
K11-removability at z=-4 gives d_r := lead M11'(1) = 2c_r (new law).
First derivation had two slips caught by data (B_op's e[0]+=1 means B
divides by (1-xs); K11 linearization is (tau+2) not (tau+4)/2); corrected
version reproduces c_0, c_1 and s12 channel split by hand.

MILESTONE 3 (solution): Borel substitution z^-(j+1) <-> t^j/j! turns the
recursion into polynomial algebra: X_r = -t^(2r)/16 - r t X_{r-1},
Phi_r = (4+D)^{-1}[X_r - 2rt Phi_{r-1}], c_r = -Phi_r(0)/2. EGFs:
sum X_r w^r/r! = -(1/16)e^(t^2 w)/(1+tw); for F = sum Phi_r w^r/r! the
PDE F_t + (4+2wt)F = Xgf under u = 1+tw becomes wG_u + 4uG = -1/(16u),
G = F e^{-t^2 w}, with FORMAL solution G = -(1/64u^2) sum_k k!(w/2u^2)^k
(one-line telescoping check); each w-order of F = e^(t^2 w)G(1+tw,w) is
polynomial in t, and polynomiality forces uniqueness (homogeneous
solution e^{-4t} is not polynomial) => Phi_r == r![w^r]F, so
  Phi_r(0) = -(1/64) r!^2/2^r  =>  c_r = (r!)^2/2^(r+7)  FOR ALL r.
The value EGF is the Euler series -(1/64) sum k! (w/2)^k.

VALIDATION (s13_local_recursion.py, out_s13_local_recursion.txt):
C1 c_r law r<=24 PASS (vs independent slice data r<=12 + 12 beyond);
C2 s12 banked channel splits r=1..4 PASS; C3 Borel==z-form r<=24 PASS;
C6 closed-form Phi_r identity r<=24 PASS; C4 chassis profile match:
PASS for all r<=5 (M10+M11, both modes, both primes); r=6 M11 mismatch
in all 4 combos at NUCAP=150 -- precision-suspected (r=6 was s12's edge),
higher-NUCAP rerun in flight.

Results doc written: results/convex-area-local-transfer.md (full
derivation, theorem, closed-form solution, validation table, rigor gap).

REGISTERED PREDICTION (out_s13_r7_prediction.txt, written before any
r=7 chassis data existed): full inner profiles chi_7 (8 rationals),
phi_7 (15 rationals), orders delta^-32/-34, c_7 = 99225/64, psi00_7 =
-14!/(4z^15). Adjudication: r=7 chassis run (king) after the NUCAP=220
r<=6 rerun lands.

NEW LAW CHECK launched (s13_dr_check.py): lead M11^(r)'(1) = 2c_r at
val -(4r+4) (predicted by K11-removability), r<=6 both modes both
primes -> out_s13_dr_check.txt.

Side observation: the c_r derivation never needs the OUTER chart (s0,
M101 all subdominant) -- the leading-order transfer is carried entirely
by the inner chart; outer data only feeds subleading orders (where the
nu-law lives).

d_r LAW CONFIRMED (out_s13_dr_check.txt): lead M11^(r)'(1) = 2c_r at
val -(4r+4), r<=6, both modes, both primes -- PASS.

MILESTONE 4 (curve law by scaling covariance): redid the chart
linearizations at a GENERAL curve point x = v^2, y_c = (1-v)^2,
s* = 1/v (closed-form seeds y = 1+v^2 - sqrt(4v^2+delta^2), s0 =
(sqrt(4v^2+delta^2)-delta)/(2v^2) work for any rational v). v-general
recursion in mu = 8v^3(1-v)tau - 1 with kappa = 32v^3(1-v)^3 (see
results doc section 5). Normalizing by g = 64v^3(1-v)^3, Cchi =
512v^4(1-v)^5, Ca = 1024v^5(1-v)^5, Cphi = 8192v^6(1-v)^7 the system
becomes EXACTLY the v=1/2 system -- no v left. Hence c_r(v) = Ca g^r
(r!)^2/2^(r+7) = (r!)^2 2^(5r+3) (xy)^((3r+5)/2): the s09
curve-amplitude law DERIVED, not just the diagonal value. Also
d_r(v) = c_r(v)/(1-v). Checks (out_s13_curve_recursion.txt): K1 v=1/2
== banked z-form r<=12 PASS; K2 curve law at 5 rational v, r<=12 PASS;
K3 normalized profiles v-free PASS.

MILESTONE 5 (ground truth at a second curve point): generalized
build_ctx to v-parametric seeds and ran the ACTUAL moment recursion
chassis at x = 1/9 (v = 1/3, s* = 3): out_s13_curve_chassis.txt -- G1
inner orders, G2 all three profiles psi/chi/phi as rational functions
of tau, G3 value law c_r(1/3) (curve amplitude), G4 derivative law
d_r(1/3): ALL PASS at r<=4, king AND poly, both primes. The v-general
derivation is validated against ground truth away from x = 1/4.

OEIS: no queries needed or made this session (all work internal to the
banked hierarchy; constants are explicit rationals).
