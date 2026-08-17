DIRECTION: adjudicate session-11's orphaned registered predictions (P1: c_r=(r!)^2/2^(r+7), cQ_r=0 for r=9..12 both modes; P2: B_r = Delta*x^2y^2*(1+x+y)*C_r king / Delta*4x^2y^2*E_r control at r=2,3) by completing its two dead runs, then push the untouched delta-Laurent local engine (s09 OPEN 1) if time allows
SHAPE: salvage, adjudicate, then blow up

Plan: (1) s11's slice_r12 run died at king/prime1/level 10 and its bivar_Br WBOX=30 rmax=3 run died at startup; neither prediction was judged. Rerun both with budgets sized to actually finish (inspect scripts first; cut NU / WBOX / primes only as far as surplus stays honest), in background, receipts under out_s12_*. (2) Adjudicate P1 and P2 as VERIFY lines — s11's predictions were registered on disk before any data existed, so a clean pass is a strong result and a failure is a real refutation. (3) With the salvage running, build the delta-Laurent engine sketched in s11's plan: slice x=1/4, y on the curve so sqrt(Delta)=delta is rational, run the moment recursion in a single power-series ring, and try to exhibit the local transfer producing c_r/c_{r-1} = 32 r^2 (xy)^{3/2}.

## CARRY
CLAIM: delta-Laurent chassis: s08 moment recursion runs in F_p((delta)) at the collision (slice x=1/4, y=5/4-sqrt(1+delta^2), s0=2(sqrt(1+delta^2)-delta), sqrt(Delta)=delta rational); r<=6 both modes both primes, ZERO failures: level-0 == s03 closed form, all levels == s09 P_r/Q_r receipts, leading coeff == c_r | receipt: out_s12_delta_run2.log, results/convex-area-local-structure.md | status: firm
CLAIM: odd-part multiplicity law nu_Delta(B_r) = ceil(r/2) (both modes): slice ord Q_r = ceil(r/2) at BOTH Delta_x-roots for r<=12 (r=9..12 REGISTERED prediction, fresh data); bivariate EXACT r<=4 (nu=1,1,2,2 full-grid Z-verified, WBOX 30/38; king r=4 registered); delta-chassis r<=6; diagonal ord_{t=1/4} B_r(t,t) = ceil(r/2) | receipt: out_s12_Qord_check.txt, out_s12_bivar_Br.txt, out_s12_bivar_r2_king.txt, out_s12_bivar_r4.txt, out_s12_delta_profiles.json | status: firm
CLAIM: s10/s11 factorization shape REFUTED for r>=2: (1+x+y) does NOT divide B_r/(Delta x^2y^2) king r=2,3; poly contents 4,2,2; the r=1 atoms are accidents, Delta-multiplicity is the real structure | receipt: out_s12_factor_probe.txt, out_s12_bivar_r2_king.txt | status: firm
CLAIM: king numerator degree corrigendum: deg A_r = 6r+8 (r<=4) but deg B_r = 11,18,23,30 — 6r+6 at EVEN r (bump REGISTERED-predicted at r=4, incl. the (32,29) inconsistency) — this, not the denominator, made s11's king r=2 fit fail; poly 4r+6/4r+4 exact | receipt: out_s12_bivar_r2_king.txt, out_s12_bivar_r4.txt | status: firm
CLAIM: c_r localization: I^(r) -> r*D*M^(r-1) alone preserves top TWO Laurent orders of tot_r (gap exactly 2, r=2..6, both modes/primes); M00(1) regular, M10(1) val = -(3r+1) exactly, M11 carries c_r; channel split c_r = [2yD2[M10]] + [I11] = (3+1)/1024, (17+15)/4096, (423+729)/32768, (4617+13815)/65536 (r=1..4) — and the split is IDENTICAL king vs polyomino channel-by-channel: local-transfer universality, leading order closes in the (M10,M11) 2-phase subsystem | receipt: out_s12_delta_local.txt, out_s12_delta_trace.txt, out_s12_delta_local_trace_poly.txt, results/convex-area-local-structure.md | status: firm
VERIFY: s11 registered P1 (c_r=(r!)^2/2^(r+7), cQ_r=0, r=9..12, both modes, slice den law) | outcome: CONFIRMED — c_r MATCH r=0..12 both modes both primes, cQ_r=0 r>=1, surplus 55-179/fit; s11's dead run completed under s12 names | receipt: out_s12_slice_r12.txt, out_s12_slice_PQ_r12.json
VERIFY: s11 registered P2 (Delta|B_r + shape) | outcome: SPLIT — Delta|B_r confirmed r=2,3,4 both modes; shape (1+x+y)*C_r / 4x^2y^2*E_r refuted for r>=2 | receipt: out_s12_bivar_Br.txt, out_s12_factor_probe.txt, out_s12_bivar_r4.txt
VERIFY: s09 claim 5 (quadruple collision, two scales) | outcome: confirmed with correction — scales delta/delta^2 and s0,1-s*=∓2delta right, but inner constants are u_- - s* = +2delta^2, sig+ - s* = -2delta^2 (NOT +delta^2, -3delta^2) | receipt: out_s12_delta_local.txt (V0 seeds exact), numeric check in LOG
VERIFY: s08 claims 1-2 (kernel moment recursion) | outcome: confirmed again via new chassis (V2 14 level-checks/prime/mode vs independent y-adic receipts) | receipt: out_s12_delta_run2.log
OPEN: prove nu_Delta(B_r)=ceil(r/2) (mechanism: sigma_pm mirror average kills odd-delta parts once per two levels) and the even-r king degree bump — both should ride the same pole-order induction as the denominator law (s08 OPEN 2).
OPEN: c_r induction is now ONE local transfer: level-(r-1) leading data -> avg_sigma(2yD2[M10^(r)] + r*D M11^(r-1)) -> c_r; extract the tau-profile recursion (charts s*+delta*tau outer, s*+delta^2*tau inner) from the delta chassis and close analytically. Channel constants banked.
OPEN: untouched majors (in value order): non-D-finiteness (i)/(ii) (s05/s06); global denominator law (s08); figure-eight probe (s06); q-Bessel normal form (s04/s05).
DEAD: pattern-matching B_r factors by fixed atom shapes (probe shows cores are new irreducibles growing in degree; only Delta-powers persist).
## LOG

Session start. Read all eleven reports. s11 (reports/session-11.md) has an
EMPTY CARRY: it registered predictions P1/P2 in its header, launched two
background runs, and died before either finished:
  - out_s11_slice_r12_run.log: s09_slice engine MAXR=12 NU=380, killed at
    king/prime1/level 10 (~130s into that level); no MATCH/MISMATCH verdict.
  - out_s11_bivar_Br_run.log: WBOX=30 rmax=3, killed right after sqrt(Delta)
    table build; only the WBOX=18 rmax=1 CONTROL run (in out_s11_bivar_Br.txt)
    completed, which validated the pipeline against banked s07 r=1 forms.

Relaunched both runs under s12 names (scripts copied, outputs renamed, s11
receipts untouched): experiments/s12_slice_r12.py (MAXR=12 NU=380) and
experiments/s12_bivar_Br.py (WBOX=30 rmax=3). PIDs in s12_pids.txt.

BIVAR RUN RESULT (out_s12_bivar_Br.txt): P2 adjudication is SPLIT.
  - Delta | B_r: CONFIRMED at r=2 (poly), r=3 (king AND poly), exact
    integer division, with the fitted forms verified EXACTLY over Z on the
    full 31x31 grid (fits: 2 primes, 144-390 consistent surplus rows, CRT
    coeffs small). r=1 reproduces banked s07 forms (control passed).
  - king factorization SHAPE REFUTED at r=3: (1+x+y) does NOT divide
    B_3/(Delta x^2y^2). s10's conjectured pattern B_r =
    Delta*x^2y^2*(1+x+y)*C_r holds at r=1 only.
  - poly content pattern: B_r/(Delta x^2y^2) has integer content 4, 2, 2
    at r=1,2,3 — s11's literal "4x^2y^2" normalization is r=1-specific.
  - king r=2 fit INCONSISTENT at s11's ansatz degrees TA=20/TB=17 (rank
    -1 at p1) while poly r=2 and king r=1,3 close — the degree law
    6r+8/6r+5 is wrong at king r=2 (denominator law not suspect: slice
    r<=8 verified by s09 + s12 rerun). Degree-ladder retry running
    (experiments/s12_bivar_r2_king.py).

DELTA-LAURENT LOCAL ENGINE (new, front 3 = s09 OPEN 1 first executable
step): experiments/s12_delta_local.py. Chassis: Laurent series in delta =
sqrt(Delta) mod p (precision-tracked), slice x=1/4, closed-form seeds
y = 5/4 - sqrt(1+delta^2), s0 = 2(sqrt(1+delta^2) - delta), sqrt(Delta) =
delta EXACTLY rational; the s08 Temperley moment recursion transplanted
verbatim (operators B, D1, D2, kernel evaluations at s0, sig+-) now runs
AT the singular collision point, poles appearing directly as Laurent
orders. Smoke run (r<=2, king, both primes) passes:
  V1 level-0 == s03 PROVEN closed form at the collision (absolute anchor);
  V2 == independent y-adic slice receipts (P_r,Q_r of s09) at r=0,1,2;
  V3 leading coeff = c_r=(r!)^2/2^(r+7), next coeff = 0 (cQ law);
  V4a phase attribution: M00(1) REGULAR (val 0), M10(1) val -(3r+1)
      (new clean law), M11(1) val -(4r+4) sole carrier — s09 finding 3
      reproduced in an entirely different expansion;
  V4b LOCALIZATION: replacing I^(r) by only its dominant term
      r*D*M^(r-1) preserves the TOP TWO Laurent orders of tot_r at r=2
      (difference starts at gap 2). This is the reduction the c_r
      induction needs. Full run r<=6 both modes both primes in flight.

DELTA RUN COMPLETE (out_s12_delta_run.log, out_s12_delta_local.txt,
out_s12_delta_profiles.json): ZERO failures. r<=6, both modes, both primes:
V1 OK, V2 OK vs s09 receipts (14 level-checks per prime), V3 c_r law OK at
every level, V4a M00 regular / M10(1) val exactly -(3r+1) / M11 carrier,
V4b gap EXACTLY 2 at every r=2..6 in all four (mode,prime) combos: the
dominant term r*D*M^(r-1) alone reproduces the top TWO Laurent orders;
neglected terms enter at delta^(-(4r+2)).

DELTA-MULTIPLICITY LAW (new, refines s09 finding 4 + refutes s10 shape):
from the profile coefficient tables, the odd(sqrt)-part of tot_r first
appears at delta^(1+2m-(4r+4)) with m = ceil(r/2) EXACTLY for r=1..6
(king AND poly, both primes): odd-position coefficient pattern
(k=1,3,5,7) = (0,*,*,*) r=1,2; (0,0,*,*) r=3,4; (0,0,0,*) r=5,6.
Combined with the bivariate factor probe (out_s12_factor_probe.txt):
  nu_Delta(B_1)=1 (+atoms (1+x+y)C_1 king / (1-x+y)(1+x-y) poly),
  nu_Delta(B_2)=1 (poly; no further atom factors, core deg 6),
  nu_Delta(B_3)=2 (BOTH modes; king core deg 15 has NO (1+x+y) factor).
Conjecture (registered before slice-r12 receipts examined):
  ord_{y=1/4} Q_r = ceil(r/2) for all r, i.e. nu_Delta(B_r) = ceil(r/2);
to be tested at r<=12 from the slice run's fitted Q_r when it lands.
Follow-up runs: king r=2 degree-ladder retry (s12_bivar_r2_king.py, fixed
divide-leadkey bug caught pre-result: BR.divide requires leadkey = lex-lead
monomial of divisor with coeff 1) and r=4 both-mode extraction at WBOX=38
(s12_bivar_r4.py, registered prediction nu_Delta(B_4)=2 in its header).

KING r=2 RESOLVED (out_s12_bivar_r2_king.txt): fits at (TA,TB)=(21,18),
true degrees deg A_2 = 20 = 6r+8, deg B_2 = 18 = 6r+6 — the s11 degree
law 6r+5 for B is one short at EVEN r (king B-degrees 11, 18, 23 at
r=1,2,3; poly 4r+4 exact throughout). Denominator law untouched. Exact
over Z on full grid; nu_Delta(B_2 king) = 1 exactly (core deg 12, 74
monomials, no atom factors, nonvanishing on curve); (1+x+y) fails
already at r=2. REGISTERED (r4 run still in DP stage at write time):
king r=4 will fit at deg A_4 = 32, deg B_4 = 30 (even-r bump), with
nu_Delta(B_4) = 2 both modes.

TRANSFER TRACE (S12_TRACE=1 rerun, r<=4 king both primes,
out_s12_delta_trace.txt): inside solve_level, the three contributions to
M11^(r)(1) = avg over sigma+- split as
  yD1[M00]: val -(4r+2) — NEGLIGIBLE (two orders above leading);
  2yD2[M10] and I11: BOTH at val -(4r+4), summing to c_r exactly:
    r=1: 3/1024 + 1/1024 = 1/256;  r=2: 17/4096 + 15/4096 = 1/128;
    r=3: (423+729)/32768 = 9/256   (rationals decoded from mod 2^61-1).
Also the DOM-truncated I11 has the SAME leading coefficient as the full
I11 at every r. So at leading Laurent order the c_r recursion closes in
the (M10, M11) two-phase subsystem with inhomogeneity r*D*M^(r-1): the
M00/D1 channel drops out. This is the concrete local recursion the s09
OPEN 1 induction must solve; profiles + channel constants banked.
Exact channel rationals (CRT+Wang over both primes, king):
  2yD2-channel: 3/1024, 17/4096, 423/32768, 4617/65536   (r=1..4)
  I11-channel:  1/1024, 15/4096, 729/32768, 13815/65536
  yD1-channel (at -(4r+2)): 1/1024, 3/4096, 45/32768, 315/65536
Normalized by c_(r-1), the two channels sum to r^2/2 exactly (1/2, 2,
9/2, 8 at r=1..4): D2-share 3/8, 17/16, 423/256, 4617/2304 and
I11-share 1/8, 15/16, 729/256, 13815/2304 — no simple closed pattern
per channel yet; the split is the quantity the tau-profile recursion
must reproduce.

POLY TRACE (S12_OUT_SUFFIX mechanism added to s12_delta_local.py so trace
runs cannot clobber canonical receipts): the control's channel constants
are IDENTICAL to the king's at every r=1..4, channel by channel
(out_s12_delta_local_trace_poly.txt) — local-transfer universality.

OEIS: no queries needed or made this session (all work internal to the
banked hierarchy).

DIAGONAL COROLLARY: ord_{t=1/4} B_r(t,t) = 1,1,2 exactly at r=1,2,3
(both modes; symmetrize the half-stored json B first — s08's pitfall
bites again): the odd singular exponent of A_r(t) at t=1/4 is exactly
-(2r+3/2)+ceil(r/2); no accidental extra diagonal vanishing.

COLLISION-CONSTANT CORRECTION (VERIFY of s09 claim 5): from the exact
closed-form seeds, u = sqrt(y) = 1/2 - delta^2/2 + O(delta^4), so
  D00-root u_- = (1-u)/x = 2 + 2*delta^2 + O(delta^4)
  closing root sigma+ = 1/(1-u) = 2 - 2*delta^2 + O(delta^4)
i.e. inner-scale constants (+2, -2), not s09's banked (+1, -3); numeric
bracket at delta=1e-2, 1e-3 confirms ((u_- - 2)/delta^2 -> 2.000001,
(sig+ - 2)/delta^2 -> -1.999999). Outer scale s0,1 - s* = ∓2delta +
delta^2 confirmed. The qualitative two-scale picture of s09 stands.

SLICE RUN LANDED (805s solve wall per mode/prime, out_s12_slice_r12.txt):
P1 CONFIRMED — c_r = (r!)^2/2^(r+7) MATCH at r=0..12, king and poly, both
primes, surplus 55-179 per fit; cQ_r = 0 for all r>=1 (cQ_0 = -1/64);
degP_r = 5r+4, degQ_r = 5r+3 continue to r=12; S0/S1/S3 anchors all OK.
Qord check rerun on the fresh receipts (out_s12_Qord_check.txt):
ord Q_r = ceil(r/2) at BOTH Delta_x-roots through r=12, both modes, both
primes — the registered r=9..12 cases pass. CRT constants listed in
out_s12_slice_r12.txt (c_12 = 437626901250).

R4 RUN LANDED (out_s12_bivar_r4.txt, 2656s): king (32,29) INCONSISTENT
then (33,30) unique fit — even-r bump registered-prediction PASSES; poly
fits first-try with deg A_4 = 22 = 4r+6, deg B_4 = 20 = 4r+4; both modes
exact over Z on the full 39x39 grid; nu_Delta(B_4) = 2 = ceil(4/2) BOTH
modes (registered) — multiplicity law now bivariate-exact r<=4, slice
r<=12. Poly core contents now 4,2,2,2 (r=1..4).

All three s11-orphaned adjudications closed; all s12 registered
predictions passed. Scripts: s12_slice_r12.py, s12_bivar_Br.py (s11
copies), s12_bivar_r2_king.py, s12_bivar_r4.py, s12_delta_local.py,
s12_factor_probe.py, s12_Qord_check.py. Results doc:
results/convex-area-local-structure.md (+ addendum in
results/convex-area-limit-law.md).
