DIRECTION: Certify the amplitude constants (s06 OPEN c, untouched 4 sessions): exact-rational interval enclosures of alpha(q_c), c1(q_c), K'(q_c) => certified A, A_dir for king AND control; control anchors against ~70 published Kotesovec digits.
SHAPE: interval arithmetic certification

Plan: (1) rerun the s06 exact-rational Lipschitz march to re-derive the king
q_c bracket self-containedly, and build the analogous march for the control
(J) family, which s06 never certified. (2) Implement dual-number interval
arithmetic over Fraction (value + d/ds catalytic derivative), with explicit
rational tail bounds for every nested q-series in the s04 Temperley solution
(F00, A1, alpha, beta, F10, A2, P/Q1/Q2, 2x2 solve), evaluated over the q_c
enclosure interval; termwise q-dual for K'. (3) Output certified enclosures
of alpha, c1, det, K', A = -c1*alpha/(K' q_c), A_dir = -alpha/(K' q_c) for
both modes; check control against Kotesovec's published constants in A067675.
(4) Verify an s09 claim as the VERIFY duty.

## CARRY
CLAIM: king amplitude constants CERTIFIED by exact-rational interval arithmetic: A = 0.974452213135004649151329420860243327425384(4) [44 digits], A_dir = 0.3754530202799247317434892438190728207071001 [45], alpha/c1/det/K'(q_c) to 44-46 digits, enclosure widths ~1e-43 | receipt: out_s10_certify_amplitude.txt, experiments/s10_certify_amplitude.py | status: firm
CLAIM: control family CERTIFIED via NEW Lipschitz march (windows .38/.44/.45, left lemma 1-3q+q^2>0 at .38): q_c/mu to 46 digits, A to 42, A_dir to 45; enclosures CONTAIN all published Kotesovec digits (A067675 amplitude + growth = Klarner-Rivest A276994) — pipeline literature-anchored at certified precision | receipt: out_s10_certify_amplitude.txt | status: firm
CLAIM: simple-pole certificate both modes: K'(q_c)!=0, det(q_c)!=0, c1(q_c)*alpha(q_c)!=0 all certified => F(1,1,q) has a simple pole at q_c with certified nonzero residue (0.3114317292236542239905877329508557019044219 king / 1.26436694538227764216337069536623455631280 control) | receipt: out_s10_certify_amplitude.txt | status: firm
CLAIM: B_1/Delta factors over the s02 atoms: control = 4x^2y^2(1-x+y)(1+x-y); king = x^2y^2(1+x+y)*C, C = 4u-4u^2+3v+2uv-u^2v+8v^2 (u=x+y,v=xy) — the king weight (1+x+y) appears | receipt: out_s10_verify_B1_div.txt | status: firm
VERIFY: s09 claim 3 (Delta | B_1) | outcome: confirmed — upgraded from point-vanishing to EXACT multivariate long division, remainder 0 both modes; also Delta does NOT divide A_1 (divisibility special to the sqrt part) | receipt: out_s10_verify_B1_div.txt
VERIFY: s06 claim 3 (q_c bracket, 45 digits) | outcome: confirmed — fresh march with tighter Lipschitz L=11.73 (vs s06's 13.60; exact taucap replaces crude factor 8), 225 steps, overlapping bracket, all digits agree | receipt: out_s10_certify_amplitude.txt
VERIFY: s05 claims 1,2,4,5 (all banked constants: q_c, mu, A, A_dir, alpha, c1, det, K', both modes) | outcome: confirmed — every banked value contained in the certified enclosures; s05's Decimal pipeline is a fully independent implementation | receipt: out_s10_certify_amplitude.txt
OPEN: s06 OPEN (c) is CLOSED. Untouched majors, in rough order of value: non-D-finiteness (i)/(ii) (s05/s06 — oscillation-law rigor is the hard half); tau-blow-up induction for c_r (s09 OPEN 1); global denominator law K^(r+1)Delta^(2r+2) (s08/s09 OPEN 2); figure-eight/quantum-modularity probe (s06); Bousquet-Melou q-Bessel normal form (s04/s05).
OPEN: (small, concrete) meaning of B_1 = Delta*x^2y^2*(weight-atom)*C: conjecture Delta | B_r all r>=1 (s09) suggests B_r = Delta*x^2y^2*(1+x+y)*C_r [king] — extract B_2 from the s08 kernel pipeline and test; is the symmetric quartic C related to the curve-amplitude law (xy)^(3r+5)/2 exponents?
DEAD: none this session; NOTE: certified-digit yield is capped by the q_c bracket width 4e-46 (march threshold), not by series tails (~1e-69) — rerun marches with threshold 1e-96 (~2x steps) if ~90 certified digits ever needed.
## LOG

Session start. Read all CARRY sections s01-s09. Target: s06 OPEN (c)
amplitude certification. Reference values (uncertified, s05 110-digit
Decimal, from out_s05_asymptotics.txt):
  king:    alpha=0.51142523878644464682870309074102686389...
           c1=2.59540384682080043879790022556523721352...
           det=0.58193497759410282803770657742054230958...
           K'=-4.26210596915238160064652438736420553788...
           A=0.974452213135004649151329420860243327425...
           A_dir=0.375453020279924731743489243819072820707...
  control: alpha=1.07524214134071812420327957128980721481...
           c1=4.43064565707653695304181870822435314295...
           det=0.39743677377984225410095346792925690739...
           K'=-3.76790688908475229878173233930304564645...
           A=2.919598509713607055384709515651335685915...
           A_dir=0.658955541852118959920998187900883420849...

### Method (experiments/s10_certify_amplitude.py; full rigor chain in its docstring)

Interval arithmetic: endpoints Fraction, every operation outward-rounded
to the grid Z/10^90 (rounding only widens; ~1e-90/op slop, irrelevant at
the 1e-45 target). Dual intervals (a,b) track (value, d/ds at s=1) of the
catalytic variable; mag(u) = sup|a|+sup|b| is submultiplicative, which is
what makes all product-tail bounds one-liners.

Tail bounds (b = q_hi rounded up to 1e-6 grid, c = 1/(1-b), I1 = c+bc^2
bounds mag((1-w_k)^-1) and mag((w_k-1)^-1) for k>=1, w_k = (q^k, q^k);
V = 1/Pinf_lb^2 from an exact lower bound on (b;b)_inf; CP = V(1+2bc^2)
bounds any product prod(1-w_j)^-2 via the log-derivative trick):
  - F00(m), N terms: tail <= 2*I1*CP*b^(m+N+1)/(1-b); N = max(20, 200-m).
  - alpha/beta (prod of R, mag(R(w_j)) <= 2b^j I1^2): geometric tail
    ratio rho = 2b^(N+1)I1^2 < 1, tail <= mag(prod_N)*C/(1-rho) with
    C = CA1 (uniform mag bound on A1) resp. CT (on T). N=32.
  - F10(t): same with C = CA1+CT (|F101|<=1). N=28.
  - P/Q1/Q2 (prod of V1, mag(V1(w_j)) <= 4b^(2j)I1^2): same pattern,
    C = CA2 (assembled from D1F00/D2F10 formulas, using computed
    mag(alpha)+mag(beta) for F10p1), CV1, CV2. N=26.
  - K' by q-duals (seed (Q,1)), m<=40; tails from s06 [R3] bounds
    (t_m <= taucap*q^(T_m), |t_m'| <= t_m*B_m); T_41=861 => ~1e-300.
The 2x2 Temperley system is solved in intervals (division certified by
det-interval excluding 0). c1 = assemble(F101=1) - assemble(F101=0).
The solver mirrors s05's NSolver structurally but shares no numerics
(Fraction intervals vs adaptive Decimal): agreement to 44+ digits is a
genuinely independent cross-check of both.

March [M]: s06 machinery generalized. King windows .29/.33/.34 (rerun);
control windows .38/.44/.45 all freshly justified: term-ratio validity
q^2/(1-q^2)^2 < 1 at 0.45 exact; left lemma J >= S_1 = (1-3q+q^2)/(1-q)^2
with numerator 44/10000 > 0 at q=0.38 exact, decreasing on [0,1].
One deliberate improvement over s06: taucap = F/Pinf_lb^2 computed exactly
(F=2 king, 1 control) instead of the crude "<=8", giving L = 11.73 (king,
vs s06's 13.60) and L = 16.55 (control; note Pinf_lb(0.44)^2 ~ 0.149 < 1/4,
so s06's hardcoded 8 would have been WRONG for the control window — the
parameterization was necessary, not cosmetic).

### Run (single script run, ~7 min total; out_s10_certify_amplitude.txt)

King march: 225 steps, 113s; bracket width 4e-46,
  a_f = 0.319596718059387465518602891982713923614508377420
  b_f = 0.319596718059387465518602891982713923614508377820
(s06 had [...387387, ...387787]: overlapping, consistent; my a_f slightly
larger because tighter L takes bigger steps. Confirms s06 claim 3.)
Control march (NEW): 394 steps, 92s; bracket width 4e-46,
  a_f = 0.433061923129390664584616965418983708541834677210
  b_f = 0.433061923129390664584616965418983708541834677610
  mu in [2.309138593330494731098720305017212531911814472266,
         2.309138593330494731098720305017212531911814474399]
  — contains A276994 = Klarner-Rivest to full certified width.

Amplitude phases (~10s each after ~2min of interval-power precomputation
included above): all enclosures listed in the addendum to
results/convex-area-asymptotics.md. Key widths: king A 1.07e-43,
king A_dir 9.27e-45, control A 5.26e-42, control A_dir 3.12e-44.
Containment checks vs s05 banked digits: 12/12 OK. Kotesovec containment
(growth + amplitude): OK. Sanity: K-value enclosure over the bracket
contains 0 (width ~4e-45 ~ |K'|*bracket width, as expected).

Certified sign facts at q_c (both modes): K'(q_c) != 0 (so q_c is a
SIMPLE zero), det(q_c) != 0 (Temperley 2x2 solve well-posed at q_c),
c1(q_c)*alpha(q_c) != 0 (residue nonzero). Together with s06's certified
"K>0 on (0,a_f]" this makes "F(1,1,q) has its first (0,1)-pole at q_c,
simple, with residue in a certified interval" fully rigorous; what remains
heuristic-free-but-analytic is only the standard transfer a(n) ~ A mu^n
(meromorphy on |q| <= q_2 - eps established structurally in s05).

Dev notes / bugs found in my own harness during the smoke test (king on
s06's banked bracket): (1) dec() used floor division for the integer part,
mangling NEGATIVE fractions' display (K' printed as -5.737894... meaning
-5 + 0.737894 = -4.262106; arithmetic unaffected); (2) containment checker
assumed banked digits truncated, but s05 printed ROUNDED digits (alpha
...63898|2 vs true ...638981.9) — widened to +-ulp. Neither affects the
certification itself; recorded here so successors don't re-trip.

### VERIFY: s09 claim 3 by exact division (experiments/s10_verify_B1_div.py)

s09 proved Delta | B_1 by vanishing at 29 points of the irreducible conic
Delta=0 with degree bound. I redid it by exact multivariate long division
over Q (Delta monic in x^2, lex division terminates): remainder EXACTLY 0,
both modes, from the banked bivariate JSONs (symmetrizing the i<=j
representatives per s08's DEAD note). Negative control: Delta does NOT
divide A_1 in either mode. Bonus explicit quotients:
  control: B_1/Delta = 4x^2y^2 - 4x^2y^4 + 8x^3y^3 - 4x^4y^2
                     = 4x^2y^2(1-(x-y)^2) = 4x^2y^2(1-x+y)(1+x-y)
  king:    B_1/Delta = 4x^2y^3 - 4x^2y^5 + 4x^3y^2 + 3x^3y^3 - 7x^3y^4
                       + x^3y^5 - x^3y^6 - 7x^4y^3 + 10x^4y^4 + 5x^4y^5
                       - 4x^5y^2 + x^5y^3 + 5x^5y^4 - x^6y^3
The control factorization 4x^2y^2(1-x+y)(1+x-y) is suggestive: the factors
1+-(x-y) also appear in s09's inner-scale analysis (sigma+ = 1/(1-sqrt y)
collides at Delta=0). Follow-up (same session): the king quotient DOES
factor over the s02 atoms — atom-division loop pulled out x^2 y^2 (1+x+y),
leaving a symmetric quartic core C = 4u - 4u^2 + 3v + 2uv - u^2 v + 8v^2
in u=x+y, v=xy (spot-check x=2,y=3: 136 both forms). So
  king:    B_1 = Delta * x^2 y^2 * (1+x+y) * C
  control: B_1 = Delta * 4 x^2 y^2 * (1 - u^2 + 4v)
and the s02 king weight atom (1+x+y) (squared in F itself) reappears in
the first moment's sqrt-coefficient. Appended to out_s10_verify_B1_div.txt;
banked as CARRY claim 4; new OPEN handed forward (test B_2).

### OEIS

No OEIS queries this session (all needed anchors were already banked;
search endpoint known Cloudflare-blocked since s06, b-files not needed).

### Files written

  experiments/s10_certify_amplitude.py   (certification, both modes)
  out_s10_certify_amplitude.txt          (receipt: marches + enclosures)
  experiments/s10_verify_B1_div.py       (exact-division verify)
  out_s10_verify_B1_div.txt              (receipt: quotients, remainder 0)
  results/convex-area-asymptotics.md     (addendum: certified constants)
