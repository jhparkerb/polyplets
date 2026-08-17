# verify-B — claim audit, reports session-06 … session-10

Scope: every CLAIM and VERIFY line in `sandbox/reports/session-06.md` …
`session-10.md`, numbered top-to-bottom within each report.
All execution on `dalby.jhpb.org:~/tmp/ghostship-grading/B/sandbox`; my own
scripts and rerun receipts are under `checks/` there (originals preserved in
`checks/orig/`). Nothing under `run-record/` was modified.

Independent instruments used repeatedly below:

- `checks/gb_brute.py` — definitional brute-force enumerator I wrote from the
  definition in `results/convex-polyplets.md` (HV-convex + king/edge
  connectivity + exact bounding box), area moments r=0..4, all boxes with
  w+h<=10, both modes. Shares no code with the sandbox pipeline. It reproduces
  the banked a_0 (king 1,2,9,36,154,668,2916,12740,55570; control A005436),
  a_1 and a_2 sequences exactly.
- `checks/gb_forms.py` — re-expands the banked closed forms parsed straight out
  of the receipts and compares against both the banked DP sequences and my
  brute force; recomputes p_0 and the E-constants.
- `checks/gb_qc.py`, `checks/gb_zeros.py`, `checks/gb_amp.py` — mpmath
  evaluations of K(q)/J(q), zero location with precision adapted to the
  cancellation (dps ~ 0.86/eps + 90), and a(n)/mu^n amplitudes.
- fresh OEIS b-file fetches (b143298, b091518, b014300, b112029) into
  `checks/`.

Tally — 23 CLAIM lines: VERIFIED-EXEC 21, VERIFIED-READ 2, FALSE 0,
VACUOUS 0, UNFALSIFIABLE 0, READ-OFF 0, RECEIPT-MISSING 0.
14 VERIFY lines: SOUND 14, UNSOUND 0, UNCHECKABLE 0.
Per report — s06: 5 claims (5 EXEC) + 4 verify; s07: 6 claims (5 EXEC,
1 READ) + 2 verify; s08: 3 claims (3 EXEC) + 3 verify; s09: 5 claims
(4 EXEC, 1 READ) + 2 verify; s10: 4 claims (4 EXEC) + 3 verify.
Every receipt path cited in these five reports exists in the tree today.

## CLAIM lines

### session-06

s06.c1 | VERIFIED-EXEC | "sum_h N_h(-1) y^h = (1/2)F(-1,4y) = … and the s02 halving identities follow as polynomial identities for all k>=1 (N_1(-1)=-1 sole boundary exception)" | docs/proofs/row-gf-specializations.md, out_s06_specialize_pm1.txt | reran `experiments/s06_specialize_pm1.py`, receipt byte-identical, ALL CHECKS PASS; independent hand check of the h=2 case (R_2 from f(w,2)=2w^2-1 gives N_2(x)=x+4x^2-x^3, N_2(-1)=4=4·N_1(1), N_1(-1)=-1) | receipt's part C does the identity symbolically in Q(y)[sqrt(4+y^2)] plus k=1..21 / k=1..20 numeric ranges; the boundary exception is real (formula gives +1 at k=0)

s06.c2 | VERIFIED-EXEC | "sum_h N_h(1) Y^h = Y/(1-4Y)^2 - 4Y^2(1-4Y)^(-3/2) … hence N_h(1) = h4^(h-1)-2(h-1)C(2h-2,h-1) = A153337(h) PROVEN at GF level" | out_s06_specialize_pm1.txt | same rerun (checks B); spot-checked [Y^2] = 8-4 = 4 = N_2(1) by hand | the "= A153337" half rests on s02's OEIS identification, not re-looked-up here; the GF/closed-form half is self-contained

s06.c3 | VERIFIED-EXEC | "q_c in (0.319596718059387465518602891982713923614508377387, +4e-46] CERTIFIED … mu = 3.12894326973088625227744799538775416053209122… (44 certified digits)" | out_s06_certify_qc.txt, experiments/s06_certify_qc.py | reran the script (137 s), receipt byte-identical; independently, `checks/gb_qc.py` at dps=120 gives K(a_f)=+1.08e-45, K(b_f)=-6.22e-46, and a bisection scan over (0,0.4) puts the *first* sign change at q=0.31959671805938746551860289198271392361450837764097 — inside the bracket; 1/q_c = 3.1289432697308862522774479953877541605320912219 agrees with all 46 quoted mu digits | "smallest positive zero" is what my scan tested; the rigor chain itself I read rather than re-derived

s06.c4 | VERIFIED-EXEC | "K(e^-eps) = 2·3^(1/4) sqrt(eps/2pi) cos(V/eps - pi/12)(1+O(eps)) with V = 2Cl2(pi/3) = … hyperbolic volume of the figure-eight knot complement (A091518) … zeros at V/(pi eps_k) = k+7/12+O(eps); control J identical with 3^(-1/4), phase -pi/4, offset 3/4" | out_s06_saddle.txt, results/K-oscillation-gieseking.md | `checks/gb_zeros.py` relocates the zeros from scratch: o_k = 0.582897001156 (k=5), 0.583138792504 (k=10), 0.583243057269 (k=20), 0.583290095417 (k=40), 0.583315419236 (k=94) — digit-identical to the receipt; control o_k = 0.753148522427 (k=5) … 0.750445169361 (k=40) → 3/4; amplitude ratios at the cos-extrema 1.964525523 / 1.978609669 / 1.989267135 / 1.994624460 / 1.996414315 / 1.997608664 with (ratio-2)/eps → -1/3, again digit-identical; my own b-file fetch of A091518 gives 2.029883212819307250042405108549040571883378615060599, matching the claimed 52 digits | the claim's own status line says the asymptotic is "firm numerically, contour-level rigor open" and that the factor 2 was fixed empirically — my check confirms the numerics, not a proof

s06.c5 | VERIFIED-EXEC | "zero census corrected: s05 banked #3..#25 = true indices 2..24; #26..#32 genuine at true indices 27,28,29,34,37,40,43 (12 zeros missed); #33..#37 are 110-digit-precision artifacts (off-lattice by 0.06..0.44); true zeros at k=46,57,63,78,94" | out_s06_saddle.txt | `checks/gb_zeros.py`: k_est for banked #33..#37 = 45.941724, 56.862144, 63.257643, 77.758124, 93.608932 (off-lattice, matching the receipt); genuine zeros found at k=46 (q=0.98622528841182405), 57, 63, 78, 94 (q=0.99319192892060139); gap arithmetic 2+4+2+2+2 = 12 checks out | one overstatement: "on-lattice to 5 decimals" — my o_k for those five are 0.58330–0.58332 vs 7/12 = 0.583333, i.e. 4 decimals, the residual being the expected O(eps)

### session-07

s07.c1 | VERIFIED-EXEC | "area moment GFs A_r(t) … are ALGEBRAIC in Q(t,sqrt(1-4t)), denominator (2+t)^(r+1)(1-4t)^(2r+2); A_1,A_2 explicit; control (1-4t)^(2r+2), A_1^poly = P/(1-4t)^4 + 4t^4/(1-4t)^(5/2)" | out_s07_moment_fit.txt, results/convex-area-moments.md | `checks/gb_forms.py` re-expands the printed P,Q over the stated denominators: king/poly A_1 and A_2 match the banked DP sequences on all 51 terms AND my own brute force for s<=10; poly A_1 has Q = 4t^4(1-4t), so Q·sqrt/(1-4t)^4 = 4t^4/(1-4t)^(5/2) exactly as claimed | at s07's time this was a fit with 17–29 surplus equations, not a derivation; the word "ALGEBRAIC" is only made a theorem by s08

s07.c2 | VERIFIED-EXEC | "every fitted closed form passed REGISTERED-PREDICTION holdout: predictions … written to disk BEFORE the DP data existed, 6-9 unseen 30-36-digit terms per sequence, two rounds" | out_s07_predictions{,2}.json, out_s07_holdout_check{,2}.txt | receipts show 9 terms (s=38..46, 3 sequences) and 6 terms (s=47..52, 4 sequences) ALL MATCH; my independent re-expansion reproduces those terms; file mtimes corroborate the ordering — predictions.json 15:40 < area_moments46.json 15:42, predictions2.json 15:47 < area_moments52.json 15:51 | ordering evidence is mtime + narrative, not a cryptographic commitment

s07.c3 | VERIFIED-EXEC | "E[area]/s^2 -> 1/12, E[area^2]/s^4 -> 1/120, Var/s^4 -> 1/720, IDENTICAL for king and polyomino = moments of X=U(1-U)/2" | out_s07_moment_asymptotics.txt | `checks/gb_forms.py` recomputes p_0 = lim (1-4t)^(2r+2)A_r from the printed numerators: king and poly both give c_1=1/256, c_2=1/128, hence E=1/12 and 1/120 with p_0(r=0)=1/128; matches (r!)^2/((2r+1)!2^r) exactly | Var/s^4 = 1/120 - (1/12)^2 = 1/720 follows arithmetically

s07.c4 | VERIFIED-EXEC | "bivariate M1(x,y) = (A+B·sqrt(D))/(K^2 D^4) [king], /D^4 [control] … verified EXACTLY over Z on full [0..26]^2 grid; diagonal == univariate A_1" | out_s07_bivar_verify{,_poly}.txt, out_s07_bivar_moment{,_poly}.json | I multiplied MY brute-force M1(w,h) table by K^2·D^4 (resp. D^4) and compared with the printed A + B·sqrt(D): 66 coefficients with i+j<=10, 0 mismatches, both modes; s08's C3 check (rerun below) confirms the same forms from the derived recursion | receipt prose says "26x26 box (676 cells)" in the header and "[0..26]^2 (729 coefficients)" in the check line — the check line is the one that matches the claim

s07.c5 | VERIFIED-EXEC | "box width: E[w|s]=s/2 EXACT, W_2(t) provably-algebraic and identified, Var(w|s)=s/8+O(sqrt s) SAME for both modes" | out_s07_width_moments.txt | re-expanded the printed W_2 closed forms against w_2(s) computed from my brute force: exact for all s<=10, both modes; E[w|s]=s/2 confirmed on the same data | E[w|s]=s/2 is an immediate consequence of f(w,h)=f(h,w) and carries no content beyond that symmetry; the s/8 constant is a numeric limit of exact expansions (0.12499881 at s=1e6, drifting to 0.12489 at s=1e7 — precision, not structure), i.e. not established exactly, which the claim's status line concedes

s07.c6 | VERIFIED-READ | "geometric limit picture: box concentrates at square (profile checked), fill ratio area/(wh) ->d 2U(1-U), density 1/sqrt(1-2rho) on (0,1/2)" | out_s07_limit_law_prediction.txt + LOG profile table | not re-executed as a distributional test — no receipt in the tree contains one. The receipt/LOG substantiate: the width profile at s=30 is a sharp bell at w=15, E[rho]=4·(1/12)=1/3 and E[rho^2]=16·(1/120)=2/15, and 1/sqrt(1-2rho) is exactly the density of 2U(1-U) | the convergence-in-law statement is an inference from two moments plus w/s concentration, not something the receipts establish; the claim carries "status: tentative (moment-level only, r<=2 at write time)"

### session-08

s08.c1 | VERIFIED-EXEC | "Temperley moment method EXECUTED: level-r moment FE = level-0 operators + inhomogeneity … closed by the SAME kernel roots at every level => M_r(x,y) and A_r(t) are ALGEBRAIC … for EVERY r; machine-executed r<=4, king+control" | docs/proofs/area-moment-kernel.md, experiments/s08_moment_kernel.py, out_s08_moment_kernel_16x16_r4.txt | reran `s08_moment_kernel.py 16 16 4`: VERDICT ALL CHECKS PASS, receipt identical to the banked one modulo wall-times (C0 level-0 vs DP table, C1 400 cells vs joint truth table, C2 diagonal vs univariate DP, C3 vs s07 bivariate fit — each OK at both primes, both modes) | the machine part is r<=4; "for EVERY r" is the induction argued in the proof doc, whose two supporting facts (staircase numerator vanishing at s0, unit-leading closing kernel) I read rather than re-derived, and whose denominator-law half the report itself leaves OPEN

s08.c2 | VERIFIED-EXEC | "derived M_1..M_4 match the joint truth table …, the independent r<=4 moment DP diagonal, and s07's fitted bivariate M1·K^2·Delta^4 == A+B·sqrt(Delta), at primes 2^61-1, 10^18+9 AND 2^521-1" | out_s08_moment_kernel_16x16_r4.txt, out_s08_moment_kernel_10x10_r4_big.txt | reran both (74 s and 9 s per mode), both VERDICT ALL CHECKS PASS, both receipts identical modulo timings; the big-prime receipt's modulus is the 512-bit 2^521-1 as claimed | these two receipts were absent from the tree when s09 looked (s09 regenerated them); they exist and reproduce now

s08.c3 | VERIFIED-EXEC | "A_3, A_4 identified with the s07-predicted denominators (2+t)^4(1-4t)^8, (2+t)^5(1-4t)^10 [king] / (1-4t)^8, (1-4t)^10 [control]; explicit numerators banked; surplus 12-28" | out_s07_r4_fit.txt, out_s07_area_moments_r4_57.txt | `checks/gb_forms.py` re-expands the banked A_3, A_4 numerators over those denominators: 56 banked DP terms matched per sequence, plus my own brute force for s<=10, all four sequences; p_0 = 9/256 and 9/32 recomputed independently | surplus figures 20/12/28/22 are inside the claimed 12–28 band

### session-09

s09.c1 | VERIFIED-EXEC | "A_r(t) ~ c_r/(1-4t)^(2r+2) with c_r = (r!)^2/2^(r+7) for r=0..8, king AND polyomino … r<=4 anchors == banked forms" | out_s09_slice_moments_run1.txt, results/convex-area-limit-law.md | reran `s09_slice_moments.py 8 300` at a *different* truncation order from the banked run (NU=300 vs 260): all 36 cP values (r=0..8 × 2 modes × 2 primes) MATCH, CRT-reconstructed c_r = 1/128, 1/256, 1/128, 9/256, 9/32, 225/64, 2025/32, 99225/64, 99225/2 — identical to the banked table, with surplus 88–139 instead of 68–119; independently, `checks/gb_forms.py` recomputes c_r for r<=4 from the banked closed forms and gets the same rationals | r<=4 is independently anchored (my own brute force feeds it); r=5..8 rests on rerunning the author's slice pipeline, at two primes, two modes and two truncation orders — the claim's own caveat is that the r>=5 diagonal inherits the still-unproven global denominator law

s09.c2 | VERIFIED-EXEC | "curve-amplitude law C_r(x,y) := lim Delta^(2r+2) M_r = (r!)^2 2^(5r+3) (xy)^((3r+5)/2) on Delta=0, IDENTICAL both modes … registered-prediction verified at a=1/3 for r<=6 (28 fresh constants, surplus 38-99), a=1/2 for r<=8" | out_s09_slice_curve.txt, results/convex-area-limit-law.md | reran `s09_slice_curve.py 6 220`: receipt byte-identical, VERDICT ALL MATCH, 28 MATCH lines = r=0..6 × 2 modes × 2 primes, surplus 38–99 as claimed | the prediction is hardcoded in the script; mtimes are consistent with registration before the run (script 17:52, receipt 17:53) but that is weaker evidence than s07's separate prediction files

s09.c3 | VERIFIED-EXEC | "sqrt-degeneracy: cQ_r = 0 for 1<=r<=8 (both modes, both slices); Delta | B_1 exactly PROVEN from banked bivariate B_1 … conjecture Delta | B_r all r>=1" | out_s09_Qdiv_check.txt, results/convex-area-limit-law.md | the Delta|B_1 half I settled independently: sympy `factor` of the banked quotient plus s10's exact long division (rerun) both give remainder 0 in each mode; cQ_r=0 comes out of the slice rerun (see s09.c1) | the 29-points-on-an-irreducible-conic argument in the results doc is sound as written (deg<=22 composed, 29 > 22) and s10 replaced it with exact division; "conjecture Delta|B_r all r>=1" is flagged as a conjecture and was later confirmed r=2,3,4 by s12

s09.c4 | VERIFIED-EXEC | "denominator law K^(r+1)Delta^(2r+2) verified on slices x=1/4 (r<=8) and x=1/9 (r<=6) with 37-119 surplus; catalytic denominator law M00^(r): D00^(2r+1), M10/M11^(r): (D00 PK1)^(2r+1), fitted degP_r=5r+4 degQ_r=5r+3" | out_s09_slice_moments_run1.txt, out_s09_slice_curve.txt | both reruns: the x=1/4 fits close at every level r=0..8 with the conjectured denominator (surplus 88–139 at NU=300, 68–119 at the banked NU=260) and the x=1/9 fits at r=0..6 (surplus 38–99); the run log's per-level `den e` field shows the catalytic exponents (0,2r+1,0) for M00 and (0,2r+1,2r+1) for M10/M11 exactly | degP_r=5r+4, degQ_r=5r+3 holds for r>=1 but not at r=0, where the receipts show degP=5 (not 4) in both modes and degQ=4 king / 3 poly; the claim states the formula without a range. The claim is explicitly slice-level — the global bivariate denominator law is left OPEN in the same report

s09.c5 | VERIFIED-READ | "singularity mechanism localized: QUADRUPLE collision on Delta=0 at s*=1/a … M00-chain closed subsystem with NO Delta-singularity; M10 value residues 0 at all r<=7; C_r carried ENTIRELY by the M11 phase" | results/convex-area-limit-law.md, out_s09_slice_moments.txt | read off the phases table in out_s09_slice_moments.txt, which shows for every r<=7 and both modes: M00 degQ=-1 with cP=cQ=0 (rational, no Delta-singularity), M10 cP=cQ=0, M11 cP = 1/128, 1/256, 1/128, 9/256, 9/32, 225/64, 2025/32, 99225/64 = c_r; not re-derived because the collision geometry is an analytic reading of the recursion rather than a computed quantity | s12 later reports the same structure with a correction to the *inner* constants (u_- - s* = +2delta^2, sigma+ - s* = -2delta^2); the CARRY line as written only names the outer scale ∓2delta, which stands

### session-10

s10.c1 | VERIFIED-EXEC | "king amplitude constants CERTIFIED by exact-rational interval arithmetic: A = 0.974452213135004649151329420860243327425384(4) [44 digits], A_dir = 0.3754530202799247317434892438190728207071001 [45] … enclosure widths ~1e-43" | out_s10_certify_amplitude.txt, experiments/s10_certify_amplitude.py | reran the whole script (~7 min): ALL CHECKS PASSED, receipt identical modulo timings; independently, `checks/gb_amp.py` computes mu from the smallest zero of K by mpmath bisection and forms a(n)/mu^n on s05's exact terms: A(60)=0.9744522131350048, A(59)=0.97445221313500497 and A_dir(60)=0.37545302027992473 — agreeing with the certified values to 16–17 digits (the residual is the O((q_c/q_2)^n) finite-n error) | I re-execute and corroborate the *values*; the interval-arithmetic rigor chain (outward rounding, dual intervals, series tail bounds) I read

s10.c2 | VERIFIED-EXEC | "control family CERTIFIED via NEW Lipschitz march … q_c/mu to 46 digits, A to 42, A_dir to 45; enclosures CONTAIN all published Kotesovec digits (A067675 amplitude + growth = Klarner-Rivest A276994)" | out_s10_certify_amplitude.txt | same rerun (containment lines "Kotesovec A067675 amplitude containment: OK" and "Kotesovec/A276994 growth-constant containment: OK"); independently, bisecting J(q) gives control q_c = 0.433061923129390664584616965418983708541834677551 (inside the certified bracket [...677210, ...677610]) and mu = 2.30913859333049473109872030501721253191181447258, matching the Klarner-Rivest constant, with a(60)/mu^60 = 2.9195985 and 0.658955541843 for the two amplitudes | the "published Kotesovec digits" are hardcoded strings in the script (lines 479–480) inherited from s05's OEIS read; s10 did not re-fetch them, and OEIS entry pages are still Cloudflare-blocked (I re-tested)

s10.c3 | VERIFIED-EXEC | "simple-pole certificate both modes: K'(q_c)!=0, det(q_c)!=0, c1(q_c)*alpha(q_c)!=0 all certified => F(1,1,q) has a simple pole at q_c with certified nonzero residue" | out_s10_certify_amplitude.txt | rerun reproduces the certified sign facts and the residue prefixes 0.3114317292236542239905877329508557019044219 (king) / 1.26436694538227764216337069536623455631280 (control) | the claim is about the certification, and the report is explicit that the transfer from simple pole to a(n) ~ A mu^n remains an analytic step

s10.c4 | VERIFIED-EXEC | "B_1/Delta factors over the s02 atoms: control = 4x^2y^2(1-x+y)(1+x-y); king = x^2y^2(1+x+y)*C, C = 4u-4u^2+3v+2uv-u^2v+8v^2" | out_s10_verify_B1_div.txt | reran `s10_verify_B1_div.py` (quotients reproduce exactly), then checked the factorizations myself in sympy: expand(king_quotient - x^2y^2(1+x+y)C) = 0 and expand(control_quotient - 4x^2y^2(1-x+y)(1+x-y)) = 0 | the factorization block is appended to the receipt by hand (the script does not emit it) — the appended text is nevertheless correct

## VERIFY lines

s06.v1 | SOUND | "s02 claim 7 (N_{2k}(-1)=+-4N_k(1), N_{2k+1}(-1) formula) | outcome: confirmed — and upgraded tentative->PROVEN" | docs/proofs/row-gf-specializations.md | s02 claim 7 exists and is the report's only tentative line; the rerun receipt's part C carries the symbolic identity plus k=1..21 / k=1..20 checks | the upgrade is genuine: s02 had a finite check with no mechanism

s06.v2 | SOUND | "s02 claim 6 (N_h(1)=A153337) | outcome: confirmed — 18-term match upgraded to GF-level proof" | out_s06_specialize_pm1.txt | s02 claim 6 exists; receipt line "G[h] == A153337 closed form h*4^(h-1)-2(h-1)C(2h-2,h-1), h<44: True" | the A-number attribution is still s02's lookup

s06.v3 | SOUND | "s05 claim 1 (q_c, mu exact characterization + 40 digits) | outcome: confirmed — all banked digits certified, extended to 45/44" | out_s06_certify_qc.txt | s05 claim 1 exists; receipt prints s05's banked digits beside the certified bracket and they agree; my mpmath q_c lands inside the bracket

s06.v4 | SOUND | "s05 claim 7 (K has >=37 real zeros in (0,0.995), accumulating at 1) | outcome: confirmed with correction" | out_s06_saddle.txt | s05 claim 7 exists; the correction is substantiated by the census table I reproduced independently; the ">=37 in (0,0.995)" survives because the law places ~128 zeros there and s06 located >=40 | a refutation of five banked *locations* reported as "confirmed with correction" rather than buried — the arithmetic supports that framing

s07.v1 | SOUND | "s04 claim 1 joint truth table: independent moment-DP reproduces all r=0..4 moments on 100 boxes/mode + definitional brute force wh<=16 | outcome: confirmed" | out_s07_area_moments.txt, out_s07_area_moments_r4_57.txt | both receipts carry the V1 (brute force wh<=16) and V3 (100 boxes vs out_s04_area_truth.json) OK lines for both modes; my own independent brute force reproduces the same a_r sequences | the second cited receipt did not exist when s07 wrote the line (its DP died; s08 produced the file) — s07's own OPEN 1 says as much, so the line was forward-referencing

s07.v2 | SOUND | "s03 claim 4 (directed-convex king = A014300, A112029): fresh OEIS b-file fetches match 14/14 terms each" | out_s07_verify_dirconv_bfiles.txt | I re-fetched both b-files myself: A014300 = 1,2,7,24,86,314,1163,4352,16414,62292,237590,909960,3497248,13480826 and A112029 = 1,5,46,517,6376,82994,1119210,15475205,217994860,3115374880,45035696036,657153097330,9663914317396,143050882063262 — matching s03's banked sequences at the claimed offsets, 14/14 each

s08.v1 | SOUND | "s07 registered limit-law prediction (its OPEN 1 …) | outcome: confirmed (all 8 constants exact)" | out_s07_r4_fit.txt | the prediction file (15:50) and the fitting harness (16:01) both predate the r4_57 data (16:35); I recomputed all four p_0 and all four E-constants from the banked numerators independently and they equal the registered values

s08.v2 | SOUND | "s07 claim 4 (bivariate M1 closed form) | outcome: confirmed — now DERIVED from the q-FE by the kernel construction, independent of s07's modular fit" | out_s08_moment_kernel_16x16_r4.txt (check C3) | C3 passes in my rerun at both primes and both modes; the derivation path (kernel recursion) is genuinely different from s07's modular linear-algebra fit

s08.v3 | SOUND | "s07 claim 1 (A_1, A_2 algebraic with denominators …) | outcome: confirmed — algebraicity now a theorem for all r; specific fitted forms pinned via C2/C3 + s07 holdouts" | docs/proofs/area-moment-kernel.md | the C2/C3 checks pass on rerun and pin the specific forms; "theorem for all r" is the proof-doc induction, which the same report leaves the denominator-law half of OPEN | the pinning is honest about resting partly on s07's holdouts

s09.v1 | SOUND | "s08 claims 1-2 | outcome: confirmed — BUT both cited receipts were MISSING from the tree; regenerated by fresh reruns, ALL CHECKS PASS both" | out_s08_moment_kernel_16x16_r4.txt, out_s08_moment_kernel_10x10_r4_big.txt | I cannot check the historical absence, but I reran both scripts myself and got ALL CHECKS PASS with receipts identical to the ones now in the tree | reporting a predecessor's missing receipt rather than silently regenerating is the load-bearing part here

s09.v2 | SOUND | "s07 claim 1 + s08 claim 3 (all ten banked A_r closed forms r<=4) | outcome: confirmed — exact-Fraction re-expansion matches independent DP57 sequences 48 terms each" | out_s09_anchor_check.txt | reran `s09_anchor_check.py`: VERDICT ALL OK, receipt identical; my own independent re-expansion (different code) matches 51–56 terms per sequence plus my brute force

s10.v1 | SOUND | "s09 claim 3 (Delta | B_1) | outcome: confirmed — upgraded from point-vanishing to EXACT multivariate long division, remainder 0 both modes; also Delta does NOT divide A_1" | out_s10_verify_B1_div.txt | reran; remainder 0 both modes, negative control (Delta ∤ A_1) also reproduced; my sympy factorization agrees | the negative control is what makes this more than a tautology

s10.v2 | SOUND | "s06 claim 3 (q_c bracket, 45 digits) | outcome: confirmed — fresh march with tighter Lipschitz L=11.73 (vs s06's 13.60) … overlapping bracket, all digits agree" | out_s10_certify_amplitude.txt | both marches rerun by me; brackets [...387387, ...387787] (s06) and [...377420, ...377820] (s10) overlap and both contain my mpmath q_c = ...50837764097 | s10's note that s06's hardcoded taucap<=8 would have been *wrong* for the control window is substantiated by the receipt's Pinf_lb figure

s10.v3 | SOUND | "s05 claims 1,2,4,5 (all banked constants …) | outcome: confirmed — every banked value contained in the certified enclosures; s05's Decimal pipeline is a fully independent implementation" | out_s10_certify_amplitude.txt | rerun shows 12/12 containment lines OK; my mpmath values for both modes' q_c, mu, A and A_dir agree with the banked ones to the precision my method supports (16–17 digits king, 8–10 control) | "fully independent implementation" is the report's characterisation of s05 vs s10 (Fraction intervals vs adaptive Decimal); the two share the same derived residue formulas, so independence is at the arithmetic level, not the formula level

## Per-report records

### DIRECTION source

The Operator bulletin is empty in every prompt (`logs/prompt-01.md` …
`prompt-14.md` line 51–52 all read "(no operator notes yet)"), so no report
could have followed it.

- s06 — takes up predecessor OPEN lines. Three fronts, all traceable: s02's
  tentative claim 7; s05 OPEN (c) "certified error bounds on the constants
  (current: 110-digit working precision …); interval-arithmetic certification
  would make them citable digits"; s05 OPEN (a) mechanism "(i) K has infinitely
  many zeros in (0,1) [theta/q-Airy-type oscillation near q=1 is the likely
  mechanism]".
- s07 — mostly NOVEL. The main front (area moments by semiperimeter) appears in
  no predecessor OPEN; the report frames it as "new tractable statistics". Its
  second front quotes s06 OPEN (c) "certify the amplitude constants A =
  0.9744…, A_dir" — and the report ends by conceding that front was left
  "untouched".
- s08 — takes up s07 OPEN lines, both quoted: "r=3,4 registered predictions …
  see out_s07_r4_fit.txt for verdict; if not present, DP57 died and the test is
  unfinished" and "PROVE A_r algebraic by the Temperley moment method".
- s09 — takes up s08 OPEN 3: "extract E[area^r]/s^2r -> (r!)^2/((2r+1)!2^r) for
  ALL r from the singular expansion of the recursion at t=1/4", plus s08 OPEN 2
  (the denominator law) as a secondary target.
- s10 — takes up s06 OPEN (c) verbatim: "certify the amplitude constants A =
  0.9744…, A_dir (needs interval evaluation of alpha, c1 at q_c)". The report
  notes it had been untouched for four sessions.

### Claims depending on an oeis.org lookup

Logged queries, verbatim from the reports:

- s06, in `### OEIS queries (verbatim)`:
  1. `curl "https://oeis.org/search?q=1.0149416064096536250212025&fmt=text"` → BLOCKED (Cloudflare)
  2. `curl "https://oeis.org/search?q=2.0298832128193072500424051&fmt=text"` → BLOCKED
  3. `curl "https://oeis.org/A143298/b143298.txt"` → OK
  4. `curl "https://oeis.org/A091518/b091518.txt"` → OK
  Claim depending on these: **s06.c4** (the identification V = 2Cl2(pi/3) =
  A091518 = vol(4_1), and the Gieseking cross-check against A143298). I
  re-fetched both b-files: 51/51 and 52/52 digits match.
- s07, in `### OEIS queries (verbatim …)`:
  `curl -s -m 30 "https://oeis.org/search?q=1,4,22,124,706,3968,21880,118192,625776&fmt=json"` → Cloudflare block;
  `curl -s -m 30 "https://oeis.org/A014300/b014300.txt"` → OK;
  `curl -s -m 30 "https://oeis.org/A112029/b112029.txt"` → OK;
  `curl -s -m 30 "https://oeis.org/A005436"` → blocked.
  Claim/verify depending on these: **s07.v2** (A014300 / A112029 b-file match,
  re-fetched and confirmed by me). The blocked search means s07's control
  total-area sequence 1,4,22,124,706,3968,… is explicitly recorded as
  *unanchored* to OEIS — the report does not claim novelty for it.
- s08, s09, s10 — no OEIS queries this session (each says so). But **s10.c2**
  depends on OEIS-sourced constants: `KOTESOVEC_A` and `KOTESOVEC_MU` are
  hardcoded strings in `experiments/s10_certify_amplitude.py` lines 479–480,
  inherited from s05's A067675/A276994 read; no query was logged in s10.
- **s06.c2 / s06.v2** inherit s02's `N_h(1) = A153337` identification, which is
  an OEIS lookup made in session 02 and not re-run in s06.

I re-tested the block from dalby today: `https://oeis.org/search?q=…` and the
entry page `https://oeis.org/A005436` both return the Cloudflare "Just a
moment…" challenge; b-file URLs serve normally. The reports' DEAD note is
accurate.

### "status: tentative" claims and their later use

Within s06–s10 there is exactly one tentative claim:

- **s07.c6** — "geometric limit picture … fill ratio area/(wh) ->d 2U(1-U) …
  | status: tentative (moment-level only, r<=2 at write time)".

Later use, all sessions 01–14 (every CARRY read):

- No later *report* CARRY line uses it. Sessions 08 and 09 refer to
  `area/s^2 ->d U(1-U)/2`, which is s07.c3 (status firm), not the fill-ratio
  claim; s11 and s14 have empty CARRY sections; s12–s13 are on the local
  transfer and do not mention fill ratio.
- It does propagate into results docs without the qualifier:
  `results/convex-area-moments.md:78` ("the FILL RATIO area/(wh) converges in
  law to 2U(1-U)") and `:117-119` ("fill ratio converges to the non-Gaussian
  law 2U(1-U); the area limit law U(1-U)/2 is driven entirely by the fill
  ratio") — both written in s07's own session; and
  `results/convex-area-limit-law.md:168` (s09) refers back to "s07's
  fill-ratio picture 2U(1-U) in near-square boxes" with no tentative marker.
  `docs/proofs/area-moments-method.md:78` names it as something a proof "would"
  deliver, which is correctly conditional.

The one earlier tentative claim these sessions touch, s02.c7, is used by s06.c1
only in the act of upgrading it to proven, with the tentative status quoted.

### Repeated-attempt patterns

One pattern reaches three or more same-shaped attempts with the same failure:

- **OEIS search/entry endpoint fetches, 4 attempts across s06–s07, all blocked
  identically.** s06 logs two (`/search?q=1.0149416064096536250212025&fmt=text`,
  `…q=2.0298832128193072500424051…`), s07 logs two (`/search?q=1,4,22,124,706,
  3968,21880,118192,625776&fmt=json`, and the entry page `/A005436`); every one
  returns the Cloudflare "Just a moment…" challenge page. Receipts: the OEIS
  sections of `reports/session-06.md` (lines 95–105) and `reports/session-07.md`
  (lines 151–160). The failures are recorded each time and a working substitute
  (b-file URLs) is found in s06 and reused in s07; the consequence carried
  forward is that s07's control total-area sequence is left unanchored. I
  reproduced both the block and the b-file workaround today.

No other shape repeats three times in these five reports. Near-misses, for the
record: two fit-ansatz failures inside s09 (the P+Q·sqrtDelta ansatz for the
M00-phase values, killed and rediagnosed as a closed-subsystem fact; and the
r=8 phase fit returning NO FIT, diagnosed as a precision ceiling at NU=260),
and two arithmetic slips caught by the authors' own checks (s07's
integer-division-before-multiply bug in the DV-style formula; s08's first C3
failure traced to the symmetrized-monomial JSON format).
