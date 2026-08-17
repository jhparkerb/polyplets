# verify-C — claim grading for session-11 … session-14

Scope: `results/ghostship/grading/run-record/sandbox/reports/session-11.md`
through `session-14.md`. All re-execution done on `dalby.jhpb.org` in
`~/tmp/ghostship-grading/C/sandbox`; my check scripts are in that copy under
`checks/` (`cgrade_bivar.py`, `cgrade_slice.py`, `cgrade_s13_recursion.py`,
`cgrade_s13_curve.py`, `cgrade_s14.py`, `cgrade_diag.py`, `cgrade_seeds.py`,
`cgrade_newton.py`, `cmp_dp.py`, `s13_local_recursion_instrumented.py`).
Nothing under `run-record/` was modified.

Independent ground-truth anchor used repeatedly below: I wrote my own
definitional enumerator for HV-convex king animals / edge-connected convex
polyominoes (row intervals, column-contiguity checked directly, king reach 1 /
overlap 0, exact bounding box w×h) and confirmed it reproduces the corpus DP
`s07_area_moments_r4.gm_table` moment vectors r=0..4 for every w,h ≤ 6, both
modes, with zero differences (`checks/cmp_dp.py`).

---

## session-11.md — CLAIM lines: 0, VERIFY lines: 0

## session-12.md — CLAIM lines

s12.c1 | VERIFIED-EXEC | "delta-Laurent chassis: … r<=6 both modes both primes, ZERO failures: level-0 == s03 closed form, all levels == s09 P_r/Q_r receipts, leading coeff == c_r" | out_s12_delta_run2.log, results/convex-area-local-structure.md | reran `experiments/s12_delta_local.py 6 150 both` (2m34s); receipt reproduces line-for-line except wall-clock times and the V2 source file (original resolved to out_s09_slice_PQ_run1.json, rerun to out_s12_slice_PQ_r12.json — both r0..r6 OK) | V1/V2/V3/V4a/V4b all OK in the rerun, 34 OK lines, zero FAIL lines
s12.c2 | VERIFIED-EXEC | "odd-part multiplicity law nu_Delta(B_r) = ceil(r/2) (both modes)" | out_s12_Qord_check.txt, out_s12_bivar_Br.txt, out_s12_bivar_r2_king.txt, out_s12_bivar_r4.txt, out_s12_delta_profiles.json | three independent routes of my own: (a) `checks/cgrade_bivar.py` exact multivariate division of the fitted B_r by Δ=(1−x−y)²−4xy gives nu=1,1,2,2 at r=1,2,3,4 for BOTH modes; (b) `checks/cgrade_slice.py` synthetic division of the raw mod-p Q_r coefficients in out_s12_slice_PQ_r12.json at y=1/4 and y=9/4 gives ord = ceil(r/2) for r=0..12, both modes, both primes, 0 failures; (c) `checks/cgrade_diag.py` gives ord_{t=1/4} B_r(t,t) = 1,1,2,2 at r=1..4 both modes | the r=9..12 slice cases and the bivariate r=4 case carry in-file "REGISTERED PREDICTION" banners (out_s12_Qord_check.txt, out_s12_bivar_r4.txt header); the claim that the conjecture was registered *before* the slice receipts were examined is a within-session ordering I cannot check
s12.c3 | VERIFIED-EXEC | "s10/s11 factorization shape REFUTED for r>=2: (1+x+y) does NOT divide B_r/(Delta x^2y^2) king r=2,3; poly contents 4,2,2" | out_s12_factor_probe.txt, out_s12_bivar_r2_king.txt | `checks/cgrade_bivar.py`, my own exact lex division: (1+x+y) divides B_r/(Δx²y²) ONLY at king r=1; fails at king r=2, r=3, r=4 and at poly r=1..4. Poly contents of B_r/(Δx²y²) are 4,2,2,2 at r=1,2,3,4 (claim says 4,2,2 for r≤3; the r=4 value 2 is in out_s12_bivar_r4.txt). Also reran `s12_factor_probe.py` — receipt byte-identical | —
s12.c4 | VERIFIED-EXEC | "deg A_r = 6r+8 (r<=4) but deg B_r = 11,18,23,30 — 6r+6 at EVEN r … poly 4r+6/4r+4 exact" | out_s12_bivar_r2_king.txt, out_s12_bivar_r4.txt | degrees read off the fitted polynomials by my own script: king degA = 14,20,26,32 (=6r+8), degB = 11,18,23,30; poly degA = 10,14,18,22 (=4r+6), degB = 8,12,16,20 (=4r+4). The (32,29) inconsistency is in out_s12_bivar_r4.txt (`rank=-1`), the s11-ansatz king r=2 failure in out_s12_bivar_Br.txt (`FIT FAILED rank=-1` at TA=20/TB=17, true degB=18) | in addition, all eight fitted (A_r,B_r) pairs satisfy A_r + B_r√Δ = M_r·K^(r+1)·Δ^(2r+2) exactly on every cell I,J ≤ 6 against my independent brute-force M_r — so the degree/divisibility facts rest on forms I confirmed against ground truth, not on the authors' fit alone
s12.c5 | VERIFIED-EXEC | "c_r localization: I^(r) -> r*D*M^(r-1) alone preserves top TWO Laurent orders … M11 carries c_r; channel split c_r = [2yD2[M10]] + [I11] = (3+1)/1024, (17+15)/4096, (423+729)/32768, (4617+13815)/65536 … the split is IDENTICAL king vs polyomino channel-by-channel" | out_s12_delta_local.txt, out_s12_delta_trace.txt, out_s12_delta_local_trace_poly.txt, results/convex-area-local-structure.md | (a) my rerun of s12_delta_local reproduces M00(1) val 0, M10(1) val −(3r+1) for r=0..6, M11(1) val −(4r+4), and "gap 2 / leading order PRESERVED" at r=2..6 in all four (mode,prime) combos; (b) `checks/cgrade_s13_recursion.py`, an independent sympy implementation of the local recursion, reproduces all eight banked channel rationals exactly (3/1024, 17/4096, 423/32768, 4617/65536 and 1/1024, 15/4096, 729/32768, 13815/65536) and (D2+I11)/c_{r−1} = 1/2, 2, 9/2, 8 = r²/2; (c) the 24 `TRACE r1..r4` channel lines in out_s12_delta_trace.txt (king) and out_s12_delta_local_trace_poly.txt (poly) are byte-identical | —

## session-12.md — VERIFY lines

s12.v1 | SOUND | "s11 registered P1 (c_r=(r!)^2/2^(r+7), cQ_r=0, r=9..12, both modes, slice den law) | outcome: CONFIRMED" | out_s12_slice_r12.txt, out_s12_slice_PQ_r12.json | `checks/cgrade_slice.py` recomputes c_r = P_r(1/4)/(9/16)^(r+1) and cQ_r = Q_r(1/4)/(9/16)^(r+1) from the raw mod-p coefficient lists myself: c_r ≡ (r!)²/2^(r+7) for r=0..12, both modes, both primes; cQ_r = 0 for r≥1, cQ_0 ≠ 0; ord P_r(1/4) = 0 throughout; 0 failures | the sub-clause "s11's dead run completed under s12 names" is inaccurate as stated: s11's own run also completed, at 19:33, under s11 names (out_s11_slice_r12.txt, out_s11_slice_PQ_r12.json), 12 minutes BEFORE the s12 rerun at 19:45. The two PQ jsons are byte-identical; the two txt/log files differ only in output filenames and per-level timings — i.e. two genuine independent executions of the same deterministic computation
s12.v2 | SOUND | "s11 registered P2 (Delta|B_r + shape) | outcome: SPLIT — Delta|B_r confirmed r=2,3,4 both modes; shape … refuted for r>=2" | out_s12_bivar_Br.txt, out_s12_factor_probe.txt, out_s12_bivar_r4.txt | both halves re-derived by `checks/cgrade_bivar.py`: Δ | B_r holds at every r=1..4 both modes; the (1+x+y) factor and the "4x²y²" normalization hold only at r=1 | note out_s12_bivar_Br.txt ends "VERDICT: FAILURES PRESENT" (the king r=2 fit failure), which the report reads correctly as a degree-bound problem, not a divisibility one
s12.v3 | SOUND | "s09 claim 5 (quadruple collision, two scales) | outcome: confirmed with correction — … inner constants are u_- - s* = +2delta^2, sig+ - s* = -2delta^2 (NOT +delta^2, -3delta^2)" | out_s12_delta_local.txt (V0 seeds exact), numeric check in LOG | `checks/cgrade_seeds.py`, my own exact series expansion at x=1/4, y = 5/4 − √(1+δ²): Δ(1/4,y) − δ² = 0 identically; u₋ − 2 = +2δ² + O(δ⁴); σ₊ − 2 = −2δ² + O(δ⁴); s0,1 − 2 = ∓2δ + δ² + O(δ⁴) | the values being corrected (u₋ − s* = δ², σ₊ − s* = −3δ²) are at results/convex-area-limit-law.md line 100; s09's own CARRY claim 5 states only "u₋, σ₊ at δ² inner", not the constants
s12.v4 | SOUND | "s08 claims 1-2 (kernel moment recursion) | outcome: confirmed again via new chassis (V2 14 level-checks/prime/mode vs independent y-adic receipts)" | out_s12_delta_run2.log | the V2 block does exist and passes (r0..r6 OK per mode per prime = 14 per prime across modes, 14 per mode across primes — both readings give 14); reproduced in my rerun | two caveats: (i) V2 compares the delta chassis against the y-adic slice engine, and out_s12_delta_local.txt's own header says the s08 recursion is "transplanted verbatim" into the chassis — so this is a reproduction across expansions, not an independent confirmation of s08's operators; (ii) s08 claim 2's substance (agreement with the joint truth table and the three-prime comparison) is not re-tested here at all

## session-13.md — CLAIM lines

s13.c1 | VERIFIED-EXEC | "c_r local transfer DERIVED+SOLVED: … psi_r=-(2r)!/(4z^(2r+1)); chi_r=psi_r/4+r chi'_{r-1}; a_r=chi_r+2r phi'_{r-1}; phi_r=(a_r-a_r(-4))/(z+4); c_r=a_r(-4)/2 … => c_r=(r!)^2/2^(r+7) ALL r" | results/convex-area-local-transfer.md, out_s13_local_recursion.txt | `checks/cgrade_s13_recursion.py`: I transcribed the recursion from the report text only and implemented it independently in sympy — c_r = (r!)²/2^(r+7) for r=0..14, and both channel identities reproduce all eight s12-banked rationals. Separately reran `experiments/s13_local_recursion.py`: receipt byte-identical (C1 r≤24 PASS, C2 PASS, C3 Borel≡z-form r≤24 PASS, C6 closed-form Φ_r r≤24 PASS) | the "ALL r" step is the section-3 argument in the doc (Borel substitution, EGF, polynomiality-uniqueness); that is an analytic argument I read rather than executed, and the recursion→c_r implication is what I verified computationally to r=14/24. The claim's own status line already scopes the gap ("firm at leading-order closure (gap: uniform-in-r subdominance, doc sec 6)")
s13.c2 | VERIFIED-EXEC | "s09 curve-amplitude law DERIVED: … => C_r=(r!)^2 2^(5r+3)(xy)^((3r+5)/2) on Delta=0; ground-truthed at x=1/9" | out_s13_curve_recursion.txt, out_s13_curve_chassis.txt | `checks/cgrade_s13_curve.py`: independent sympy implementation of the v-general recursion as stated in the receipt/report gives c_r(v) = (r!)² 2^(5r+3)(v(1−v))^(3r+5) for r=0..8 at v = 1/2, 1/3, 1/5, 3/7, 2/5, reduces to c_r = (r!)²/2^(r+7) at v=1/2, and the normalized profiles χ_r/(C_χ g^r), φ_r/(C_φ g^r) are v-free | the x=1/9 chassis ground truth (G1–G4, r≤4, both modes, both primes, ALL PASS) is read from out_s13_curve_chassis.txt, not re-executed — the chassis run is the same ~2.5-min-class job and its independent-implementation counterpart is already covered above
s13.c3 | VERIFIED-EXEC | "new value law lead M11^(r)'(1) = c_r(v)/(1-v) (=2c_r at x=1/4) from K11-removability" | out_s13_dr_check.txt (r<=6 both modes/primes), out_s13_curve_chassis.txt G4 | reran `experiments/s13_dr_check.py` (2m35s): receipt byte-identical, 28 rows "val M11'(1) = −(4r+4), lead==2c_r: OK", final line PASS | the v-general half (c_r(v)/(1−v)) is read from out_s13_curve_chassis.txt G4
s13.c4 | VERIFIED-READ | "king==poly channel universality DERIVED: every mode-dependent operator (Qcomp, king B-term, M101, value-atoms) is subdominant at the collision" | results/convex-area-local-transfer.md sec 2 | the cited receipt is a prose derivation, not an executable check; I read section 2, which states the subdominance and then explicitly says "what is NOT yet proven for all r is the subdominance bookkeeping it relies on … each machine-verified at r ≤ 6 by s12". Empirical corroboration exists and I checked it: the 24 channel-trace lines are byte-identical between king and poly (see s12.c5) | the claim line carries "status: firm" without repeating the subdominance caveat that the cited document section states in its own body and that s13.c1's status line does carry
s13.c5 | VERIFIED-EXEC | "chassis phase numerators have 3-slope Newton polygons (-2 inner/-1 outer/0 global); inner profiles extracted+matched to closed forms r<=6 both modes/primes" | out_s13_tau_profiles.txt/.json, C4 of out_s13_local_recursion.txt | (a) `checks/cgrade_newton.py`: I computed the lower convex hull of (j, val n_j) for every (mode, prime, r≤6, phase) in out_s13_tau_profiles.json — the slope multiset over all cases is exactly {0: 84, −1: 52, −2: 48}, no other slope occurs; (b) C4 in out_s13_local_recursion.txt prints only "r<=  checked" (a literal blank in the f-string) with no count, so I ran an instrumented copy (`checks/s13_local_recursion_instrumented.py`): 56 profile identities are actually checked (14 per mode/prime = r=0..6 × M10,M11) and all pass | the cosmetic blank is not a fail-open in practice, but the receipt as written gives the reader no count and no r-range; PREC/None paths in that loop `continue` silently
s13.c6 | VACUOUS | "(r=7 registered prediction adjudication) | status: PENDING" | out_s13_r7_prediction.txt, out_s13_tau_profiles_r7.json | the line states no proposition — nothing about the receipts could falsify it. Recorded for completeness: out_s13_tau_profiles_r7.json did not exist when session-13.md was written (json mtime 20:31, report mtime 20:28), so the second cited receipt was missing at write time; it exists now | I adjudicated it anyway: `s14_adjudicate_profiles.py out_s13_tau_profiles_r7.json out_s13_r7_prediction.txt 7` reproduces out_s14_r7_adjudication.txt byte-identically (96 identities, ALL PASS), and my own recursion (`checks/cgrade_s14.py`) reproduces the registered chi_7 (8 coeffs), phi_7 (15 coeffs) and c_7 = 99225/64 exactly

## session-13.md — VERIFY lines

s13.v1 | SOUND | "s12 claim 5 (c_r localization, channel split) | outcome: confirmed + upgraded to closed form: D2-channel=chi_r(-4)/2, I11-channel=r phi'_{r-1}(-4), exact match r=1..4" | out_s13_local_recursion.txt C2 | my independent recursion (`checks/cgrade_s13_recursion.py`) reproduces both channel formulas and all eight r=1..4 constants exactly; C2 in the receipt PASSes on rerun | —
s13.v2 | SOUND | "s09 claim 2 (curve-amplitude law, was registered-prediction-only) | outcome: confirmed + now DERIVED; fresh ground truth at x=1/9 incl. full profiles" | out_s13_curve_chassis.txt | supported: G1–G4 ALL PASS at r≤4, both modes, both primes, at the new curve point v=1/3; the derivation half is exec-verified under s13.c2 | minor mischaracterization of the predecessor: s09's claim 2 reads "exact for r<=1 on whole curve, registered-prediction verified at a=1/3 for r<=6 … a=1/2 for r<=8", so it was not purely "registered-prediction-only"
s13.v3 | UNSOUND | "s12 claims 1+5 receipts (delta chassis reruns at NUCAP 150/220/250) | outcome: confirmed (V-asserts pass, all levels) | receipt: out_s13_tau_run*.log" | out_s13_tau_run.log, out_s13_tau_run2.log, out_s13_tau_run_r7.log | the cited logs contain zero occurrences of "V" — no V-assert output of any kind; they hold only per-level timings and profile dumps. `experiments/s13_tau_profiles.py` imports s12_delta_local and calls `CH.solve_all(...)`, which solves levels only; the V1/V2/V3/V4 block lives in that module's driver (lines ~674+) and is never reached | what the reruns do establish is weaker and real: the in-code `assert`s inside the chassis (Δ≠δ² guard, PK(s0)=PK(s1)=0, exact polydiv, M10(1)/M11(1)/M11'(1) consistency) did not fire at NUCAP 150/220/250. The outcome "confirmed" is independently corroborated elsewhere (C4's 56 identities, my own recursion), but not by the cited receipts

## session-14.md — CLAIM lines: 0, VERIFY lines: 0

---

## Per-report records

### DIRECTION source

- s11 — takes up a predecessor OPEN line, two of them, quoted in its own DIRECTION: "(iii) a delta-Laurent local engine at the quadruple collision to exhibit the blow-up recursion (s09 OPEN 1)", and front (ii) tests s10's OPEN: "conjecture Delta | B_r all r>=1 (s09) suggests B_r = Delta*x^2y^2*(1+x+y)*C_r [king] — extract B_2 from the s08 kernel pipeline and test" (session-10.md line 24).
- s12 — adjudicates s11's registered predictions, then "push the untouched delta-Laurent local engine (s09 OPEN 1) if time allows". s09's OPEN 1 reads: "PROVE the induction c_r/c_(r-1) = r^2·32·(xy)^(3/2) via the tau-blow-up … phase data says M11 is the carrier."
- s13 — "close the local transfer c_r/c_{r-1}=r^2/2 (s09 OPEN 1 / s12 OPEN 2)". s12's OPEN 2 reads: "c_r induction is now ONE local transfer: … extract the tau-profile recursion (charts s*+delta*tau outer, s*+delta^2*tau inner) from the delta chassis and close analytically."
- s14 — takes up s13's PENDING claim 6 ("adjudicate s13's PENDING r=7 registered prediction (its receipt was never written — run died)") plus a self-chosen capstone synthesis.
- "Operator bulletin": the string does not appear anywhere in the sandbox (reports, receipts, results, docs, HISTORY.txt). No report in this range cites or follows such a section.

### OEIS-dependent claims

None. s12 and s13 each log "OEIS: no queries needed or made this session (all work internal to the banked hierarchy)" (session-12.md line 132, session-13.md line 126); s11 and s14 contain no OEIS line and no claim citing a lookup. No logged query text exists to quote.

### "status: tentative" claims and their downstream use

- No claim in s11–s14 carries "status: tentative". The only two in the whole corpus are earlier: session-02.md line 21 (N_{2k}(−1) fingerprint identities, "tentative (finite check, no mechanism)") and session-07.md line 19 (geometric limit picture, fill ratio area/(wh) → 2U(1−U), "tentative (moment-level only, r<=2 at write time)").
- Downstream use in my range: neither is restated. The nearest relative is the moment-level limit law, and results/FINAL-SYNTHESIS.md (s14's work product) states it with its scope intact — "area/s² → U(1−U)/2 in moments to order 12", and separately "Remaining gap: uniform-in-r subdominance". No unqualified promotion of either tentative claim found.

### READ-OFF check against the original 21-file corpus

None of the s12/s13 claims restate corpus content. The original corpus files
(convex-mirage.md, convex-polyplets.md, defect-gas.md, directed-king-animals.md,
strip-growth-lambda-bounds.md, polyplet-upper-bound.md, diagonal-law.md) contain
no occurrence of "area moment", "area-moment", "c_r", or "Temperley moment"; the
corpus material on this family is the 38-term area sequence, μ ≈ 3.129, and the
empirical non-D-finiteness finding. The bivariate moment closed forms, Δ, the
kernel K = x+y+xy, and the singular expansion are all downstream of s07/s08.

### Repeated-attempt pattern (three instances, same shape)

A long background job outlives its session; the successor reads the missing or
truncated receipt as a dead run and relaunches the same computation, duplicating
work already in flight:

1. s11 launched the MAXR=12 slice run; s12 recorded it "killed at king/prime1/level 10 … no MATCH/MISMATCH verdict" and relaunched it under s12 names (s12_pids.txt: `slice pid 2574929`). s11's original run in fact completed at 19:33 (out_s11_slice_r12_run.log ends "receipts written"); s12's duplicate landed at 19:45. The two out_*_slice_PQ_r12.json files are byte-identical; the txt/log pair differs only in filenames and per-level timings.
2. s11's WBOX=30 rmax=3 bivariate run died at startup (out_s11_bivar_Br_run.log stops after the sqrt(Δ) table); s12 relaunched it as out_s12_bivar_Br.txt. Here the relaunch was not redundant — only the WBOX=18 rmax=1 control output exists under s11 names.
3. s14 found out_s13_tau_profiles_r7.json absent and out_s13_tau_run_r7.log "truncated mid-poly", launched a king-only rerun (PID 2579059, out_s14_tau_run_r7.log), then s13's original run (PID 2578223, in s13_pids.txt) completed at 20:31 with the full both-modes receipts; s14 killed its own rerun by captured PID to stop it overwriting the complete receipt with a king-only one, and logged the lesson.

### session-11.md — factual characterization

18 lines. Contents: a DIRECTION naming three fronts; a SHAPE line ("singular
expansion engineering"); a four-part Plan; a REGISTERED PREDICTIONS block with
two numbered predictions P1 (c_r = (r!)²/2^(r+7) and cQ_r = 0 for r = 9..12,
king and control) and P2 (Δ | B_2 exactly over Z with the (1+x+y)·C_2 /
4x²y²·E_2 shape, same at r=3); a CARRY section whose entire body is
"(to be filled as results land)"; and a five-line LOG stating that all ten prior
CARRY sections were read and naming the receipt files the three fronts would
produce. No CLAIM line, no VERIFY line, no OPEN line, no DEAD line, no result of
any kind.

Work-product files left behind, cross-checked against the directory:

- `experiments/s11_slice_r12.py`, `experiments/s11_bivar_Br.py` — both present.
- `out_s11_slice_r12.txt`, `out_s11_slice_PQ_r12.json`, `out_s11_slice_r12_run.log` (all 19:33) — present and, contrary to s12's reading, COMPLETE: the txt carries the full r=0..12 table for king and poly with MATCH on every row, and the log ends "receipts written".
- `out_s11_bivar_Br.txt`, `out_s11_bivar_Br.json`, `out_s11_bivar_Br_run.log` — present but partial: the txt holds only a WBOX=18 rmax=1 run (r=1, both modes, 19×19 grid, "VERDICT: ALL FITS + EXACT CHECKS PASS"), the json only keys `king_r1`, `poly_r1`; the run log for the WBOX=30 rmax=3 job stops three lines in, after the sqrt(Δ) table.
- Front 3 (the delta-Laurent local engine) produced nothing. The LOG names "out_s11_delta_local*.txt"; no file matching that name exists. The engine was first built in s12 as `experiments/s12_delta_local.py`.

### session-14.md — factual characterization

71 lines, no CLAIM or VERIFY lines and no CARRY content (the CARRY section reads
"(filled as results land)"). Contents: DIRECTION (adjudicate s13's PENDING r=7
prediction, write a capstone, probe the ν-law order); a three-part Plan; and a
LOG with six blocks — the PID/rerun episode described above; an r=7 ADJUDICATION;
an r=8 EXTENSION registering a prediction and launching a run; a VALUE LAW
observation at r=7; a FOUNDATION RE-AUDIT; and a CAPSTONE note.

Work-product files, all present:

- `experiments/s14_adjudicate_profiles.py` — new tool. I reran it as
  `s14_adjudicate_profiles.py out_s13_tau_profiles_r7.json out_s13_r7_prediction.txt 7`
  and it reproduces `out_s14_r7_adjudication.txt` byte-identically (96 profile
  identities, "VERDICT: ALL PASS").
- `out_s14_r7_adjudication.txt`, `out_s14_r8_prediction.txt`,
  `out_s14_foundation_recheck.txt`, `out_s14_tau_run_r7.log`,
  `out_s14_tau_run_r8.log`, `s14_pids.txt` (contains 2579059, 2579265).
- `results/FINAL-SYNTHESIS.md` (8441 bytes). Every file path it cites resolves:
  docs/proofs/{area-moment-kernel,convex-area-q-temperley,convex-box-kernel,row-gf-specializations}.md,
  results/{convex-area-asymptotics,convex-area-local-transfer,convex-area-moments,directed-convex-king,K-oscillation-gieseking}.md,
  king_semiperim_200.txt, out_s05_terms60.txt, out_s10_certify_amplitude.txt.
  (The one non-resolving token is the glob "reports/session-01..14.md".)
- `out_s13_tau_profiles_r8.{txt,json}` (20:46) were written by the run s14
  launched, i.e. after session-14.md was written at 20:37.

Four of the LOG's assertions checked directly:

- Foundation re-audit — CONFIRMED independently. `checks/cgrade_s14.py`: my own
  exact-Fraction expansion of F(t) = [t²(2−10t+14t²−5t³−4t⁴) − t³(1+2t)²√(1−4t)]
  / ((2+t)(1−4t)²) reproduces all 200 terms of king_semiperim_200.txt (the file's
  a(1) is the t² coefficient), zero non-integer coefficients.
- Value law at r=7 — CONFIRMED. The `val@s=1` rows for the M11 phase in
  out_s13_tau_profiles_r7.txt at lines 58, 103, 164, 241, 334, 443, 568, 709 —
  exactly the "lines 58..709" the LOG cites — give val = −4, −8, −12, −16, −20,
  −24, −28, −32 with leads 1/128, 1/256, 1/128, 9/256, 9/32, 225/64, 2025/32,
  99225/64 = (r!)²/2^(r+7) for r=0..7.
- The registered r=8 prediction — CONFIRMED against my own recursion:
  chi_8 (9 coeffs), phi_8 (17 coeffs) and c_8 = 99225/2 all match
  (`checks/cgrade_s14.py`); psi00_8 = −16!/(4z^17) is the r=8 case of the
  banked psi00_r form.
- The r=8 adjudication s14 promised ("Adjudication below when it lands") never
  appears in the report — the run finished 9 minutes after the report was
  written. I ran it: `s14_adjudicate_profiles.py out_s13_tau_profiles_r8.json
  out_s14_r8_prediction.txt 8` → 54 profile identities (king only, both primes,
  r≤8), "VERDICT: ALL PASS". Output saved at
  `checks/cgrade_s14_r8_adjudication.txt` in my dalby copy.
