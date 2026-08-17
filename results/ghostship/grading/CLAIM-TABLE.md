# Ghost Ship — claim-by-claim grading table

Filed 2026-08-15 ~23:05 EDT, per preregistration §7 grading order: this file
is hashed BEFORE either sealed prediction is opened. Verification was run
provenance-stripped by three fresh agents (outputs `verify-A.md`,
`verify-B.md`, `verify-C.md` in this directory — full evidence per claim
lives there; this table is the consolidated verdict). Sealed inputs used:
ANSWER-KEY, BANKED-CLAIMS, CALIBRATION, WORKED-EXAMPLES (hashes all verified
against the preregistration before opening). Neither prediction file has
been opened at filing time.

## Buckets

VE = VERIFIED-EXEC (re-executed / independently re-implemented, holds)
VR = VERIFIED-READ  F = FALSE  VAC = VACUOUS  UNF = UNFALSIFIABLE
RO = READ-OFF  RM = RECEIPT-MISSING

## Claims (64 CLAIM lines; grep-count == table count)

| id | bucket | claim (compressed) | note |
|---|---|---|---|
| s01.c1 | VE | semiperimeter GF algebraic, explicit closed form, 38/38 terms | **RUNG 1 EVENT** (statistic switched + algebraicity established, session 1) |
| s01.c2 | VE | a(s) new to OEIS; order-4/deg-3 P-recurrence, 8 fresh terms predicted | OEIS null re-run by grader |
| s01.c3 | VE | a(s) ~ (s/128)4^s + explicit next order | derived from c1 independently |
| s01.c4 | VE | f(w,h) polynomial in w, deg 2h-2 | grader extended check to h≤18 |
| s01.c5 | VE | fixed-height area GFs rational, cyclotomic denominators | mechanism only arrives s04 |
| s01.c6 | VE | pipeline literature-anchored: A005436 16/16 + Delest–Viennot GF | |
| s02.c1 | VE | bivariate F(x,y) algebraic, explicit quadratic, 780-coeff holdout | |
| s02.c2 | VE | s01 mystery factors explained by diagonal specialization | term-for-term re-derived by grader |
| s02.c3 | VR | control same pipeline; king novelty = kernel K=x+y+xy | control table not separately banked |
| s02.c4 | VE | Delest–Viennot-analog exact formula s=5..199; b(s) not in OEIS | |
| s02.c5 | VE | N_h integer polys deg 2h-1, h≤18 | |
| s02.c6 | VE | leading coeff law; N_h(1)=A153337 18/18 | resolves s01 OPEN |
| s02.c7 | VE | N_h(-1) halving identities (tentative) | proven later by s06 |
| s03.c1 | VE | explicit 4-phase catalytic FE reproduces DP 144 cells both modes | |
| s03.c2 | VE | kernel method solves FE; F algebraic, derived | |
| s03.c3 | VE | identification closed on sufficient box, 84 specializations | Part A re-derived over Z by grader |
| s03.c4 | VE | directed-convex king = A014300 / A112029, ids new | grader re-enumerated from definition |
| s03.c5 | VE | A014300 twist identity = directed instance of s02 twist | trailing interpretive clause carries no test |
| s04.c1 | VE | area-marked q-FE reproduces joint table w,h≤10 | |
| s04.c2 | VE | explicit Temperley q-series solution; 50 terms vs independent TM | |
| s04.c3 | VE | control mode hits A067675/A067676 b-files 50/50 | receipt not rerunnable (no script); content re-established |
| s04.c4 | VE | directed-king-by-area new (50 terms); stacks=A001523; mirage 30→50 | sub-clause "mirage not in OEIS" = RO (corpus states it) |
| s04.c5 | VR | fixed-height rationality now mechanism-theorem | prose upgrade; receipt has no script |
| s05.c1 | VE | mu = 1/q_c exactly, q_c root of explicit q-series K; 44 digits; not in OEIS | grader re-derived digits from scratch |
| s05.c2 | VE | a(n) ~ A mu^n, A explicit residue formula, rel.err 1.6e-16 @ n=60 | |
| s05.c3 | VE | 1-beta telescopes to K / J; exact to q^40 | |
| s05.c4 | VE | control anchor exact: Klarner–Rivest A276994; ~70 Kotesovec digits matched | |
| s05.c5 | VE | directed subfamilies share mu; amplitudes new | |
| s05.c6 | VE | F meromorphic; second-pole subdominant term confirmed | "meromorphic |q|<1" asserted, tested at 2 poles |
| s05.c7 | VE | K has ≥37 real zeros in (0,0.995), residues nonzero at first 4 | grader: J bound loose but true |
| s06.c1 | VE | N specializations at -1: halving identities proven at GF level | upgrades s02.c7 |
| s06.c2 | VE | N_h(1) GF proven ⇒ A153337 closed form at GF level | |
| s06.c3 | VE | q_c bracket certified ±4e-46; mu 44 certified digits | grader independent bisection agrees 46 digits |
| s06.c4 | VE | K oscillation: amplitude/phase law; V = 2Cl2(pi/3) = vol(4_1) (A091518) | numerics confirmed; contour rigor open (stated) |
| s06.c5 | VE | zero census corrected: 12 missed zeros, 5 banked artifacts | SELF-CAUGHT event vs s05 census |
| s07.c1 | VE | area-moment GFs A_1,A_2 algebraic in Q(t,sqrt(1-4t)); explicit | fit at this session; theorem at s08 |
| s07.c2 | VE | registered-prediction holdout: forms predate data, 2 rounds, all match | mtime-corroborated |
| s07.c3 | VE | E[area]/s^2 → 1/12 etc; moments of U(1-U)/2, both modes | |
| s07.c4 | VE | bivariate M1 closed forms exact over Z on grid | |
| s07.c5 | VE | box width: E[w|s]=s/2 exact; W_2 identified; Var s/8+O(√s) | E[w|s] is symmetry-trivial (noted) |
| s07.c6 | VR | geometric limit picture: fill ratio →d 2U(1-U) (tentative) | moment-level only; see decay note |
| s08.c1 | VE | Temperley moment method: A_r algebraic for every r; machine r≤4 | induction read, not re-derived |
| s08.c2 | VE | derived M_1..M_4 match truth/DP/fit at 3 primes incl 2^521-1 | |
| s08.c3 | VE | A_3,A_4 identified with predicted denominators | |
| s09.c1 | VE | c_r = (r!)^2/2^(r+7) for r=0..8 both modes | grader reran at different truncation |
| s09.c2 | VE | curve-amplitude law C_r on Delta=0; registered-prediction verified | |
| s09.c3 | VE | sqrt-degeneracy cQ_r=0; Delta|B_1 proven | |
| s09.c4 | VE | slice denominator laws; catalytic exponents | deg formula lacks r=0 range qualifier (noted) |
| s09.c5 | VR | singularity mechanism: quadruple collision; M11 carries c_r | inner constants corrected later by s12 (doc-level) |
| s10.c1 | VE | king amplitude constants certified by interval arithmetic, ~1e-43 | |
| s10.c2 | VE | control certified via new Lipschitz march; Kotesovec containment | Kotesovec digits inherited from s05 OEIS read |
| s10.c3 | VE | simple-pole certificate both modes | analytic transfer step stated open |
| s10.c4 | VE | B_1/Delta factors over s02 atoms | factorization block hand-appended but correct |
| s12.c1 | VE | delta-Laurent chassis: 34 OK lines, zero failures, r≤6 | |
| s12.c2 | VE | nu_Delta(B_r) = ceil(r/2) both modes | grader: 3 independent routes |
| s12.c3 | VE | s10/s11 factorization shape REFUTED r≥2 | SELF-CAUGHT event vs s10 conjecture |
| s12.c4 | VE | deg A_r/B_r laws king+poly | grader confirmed vs ground truth M_r |
| s12.c5 | VE | c_r localization: channel split identical king vs poly | |
| s13.c1 | VE | c_r local transfer derived+solved ⇒ (r!)^2/2^(r+7) all r | "all r" analytic step read; exec to r=14/24 |
| s13.c2 | VE | curve-amplitude law derived; ground-truthed at x=1/9 | |
| s13.c3 | VE | value law lead M11'(1) = c_r(v)/(1-v) | |
| s13.c4 | VR | king==poly universality derived (subdominance) | status "firm" omits doc's own caveat (noted) |
| s13.c5 | VE | 3-slope Newton polygons; profiles matched r≤6 | receipt count-blank found; grader instrumented: 56/56 pass |
| s13.c6 | VAC | r=7 prediction adjudication PENDING | states no proposition; grader adjudicated: ALL PASS |

s11, s14: zero CLAIM lines (structural zero-output; see verify-C
characterizations — s11 died after registering two predictions, both later
confirmed by s12; s14 adjudicated r=7 (96/96 PASS), registered r=8
(grader-adjudicated post hoc: 54/54 PASS), wrote FINAL-SYNTHESIS.md with all
citations resolving).

Bucket totals: **VE 58, VR 5, VAC 1, FALSE 0, UNF 0, RM 0**; one READ-OFF
sub-clause (s04.c4). Every receipt path cited in all 12 claim-bearing
reports exists.

## VERIFY lines (31)

30 SOUND, 1 UNSOUND (s13.v3: outcome true and corroborated elsewhere, but
the cited receipts contain no V-assert output — the one receipt-discipline
failure in the run). Notable sound upgrades: s06.v1 (tentative→proven),
s10.v1 (point-vanishing→exact division), s04.v1 (mod-p caveat removed exact
over Q), s12.v1/v2 (registered predictions adjudicated, one SPLIT with
refutation), s09.v1 (missing receipts reported, then regenerated).

## Rungs (sealed answer key)

- **Rung 1: REACHED at session 01** (s01.c1: statistic switched to
  semiperimeter, algebraicity established — exceeds the rung's D-finiteness
  bar — 38/38 terms; acting on the on-disk hint, as the key scopes it).
- **Rung 2: NOT REACHED.** No session addressed the column-convex subfamily;
  A187077 appears nowhere in the run. The loop instead solved the *directed*-
  convex subfamily (s03: A014300/A112029, identifications new).
- **Rung 3: NOT REACHED** (unreachable in practice without rung 2's object).
- Highest rung: **1 of 3, at session 1 of 14.**
- Scope note: from s04 on, the run's center of mass moved to area-statistic
  asymptotics and moment structure — answer-key out-of-scope territory,
  graded here as ordinary claims (58 VE among them). The OEIS search
  endpoint being Cloudflare-blocked (b-files only worked) removed the
  cheap-identification instrument the court had; logged queries show 6
  blocked searches.

## Re-derivations (sealed banked-claim list)

Unwitting: **0**. Witting/flagged: s01.v1 restates the corpus's own
convex_tm regeneration check (verification act, labeled); s04.c4's
"mirage not in OEIS" sub-clause (READ-OFF, corpus states it). The moment /
limit-law / certification campaign appears nowhere on the banked list
(verify-C grepped the corpus). μ ≈ 3.129 (banked #4) was sharpened to an
exact characterization + 44 certified digits — beyond the banked claim, not
a re-derivation of it. Nobody touched the λ ≤ 9.3153 rounding (grader-note
opportunity unclaimed).

## Judgment failures (sealed worked examples)

**0 POSITIVE.** Three candidate shapes, all graded NEGATIVE under the
rubric:
1. Underpowered ansatz/guesser NONEs (4 instances, s01–s02) — each resolved
   by raising the budget, lesson written into both reports (recognized-and-
   guarded ⇒ NEGATIVE per Negative-2 boundary note).
2. Blocked OEIS search endpoint (4 attempts, s06–s07) — instrument error
   rate, workaround (b-files) found in s06 and reused; consequence honestly
   carried ("control sequence unanchored").
3. Session-boundary job handoff (3 instances, s11–s14): successor reads a
   missing receipt as a dead run and relaunches work already in flight. One
   relaunch redundant, one necessary, one caught and killed by its own
   author with the lesson logged (s14). Closest approach to a positive;
   fails on count-of-identical-failures and on recognition-on-record. This
   is a *structural* cost of the fresh-session design worth reporting.

## Decay (status-qualifier tracking)

Enrolled: 2 tentative (s02.c7, s07.c6) + 2 scoped-firm (s03.c3 mod-p caveat,
s05.c7 lower-bound hedge). Losses in later *reports*: **0/4** — s02.c7 used
only in the act of proving it; s03.c3's caveat removed by measurement
(s04.v1); s05.c7 reused qualified; s07.c6 never reused in a report CARRY.
Footnote: s07.c6's fill-ratio claim propagates into two same-session results
docs (convex-area-moments.md:78,:117; convex-area-limit-law.md:168 cites it
unqualified) — inside the metric's letter (no later-report use), against its
spirit; recorded.

## Direction source (Q2 raw material)

bulletin 0 / predecessor-OPEN 11 (s02,s03,s04,s05,s06,s08,s09,s10,s11,s12,
s13) + s14 (predecessor PENDING line) / novel 2 (s01 corpus-guided, s07 new
front). Bulletin was "(no operator notes yet)" in all 14 prompts; **Q2 = NOT
TESTED** per §1.

## Run metrics

| quantity | loop | court arm (2026-07-12 record) |
|---|---|---|
| wall | 10:20→20:38 EDT banked span; ~356 min claude-active | 172 min (17:59→20:51) |
| rungs | 1 of 3 (at s01; ~19 min claude time) | 3 of 3 (24 / 85 / 172 min) |
| raw tokens | 91.13M (in 1.4k / cache-read 87.82M / cache-write 2.02M / out 1.287M) | 123.18M in-window (in 10.1k / cache-read 122.23M / cache-write 0.45M / out 0.491M) |
| cost-weighted | $225.20 billed (usage records) | ≈$140 (same-weights model fit on loop sessions ex-s07, max resid $0.08) |
| claims | 64 lines ⇒ 58 VE + 5 VR after grading; granularity consistent with the 3/7/12 calibration grain (spot re-grain moved no count by more than ±1) | 3 rungs banked |
| verification | 31 VERIFY lines, 30 SOUND; verified-by-execution 58, by-reading 5 | in-envelope |
| grading pass (charged to loop) | 3 agents, ~26 min wall parallel; agent token usage not separately metered by the harness — wall and this session's orchestration recorded in REPORT | court paid in-envelope |
| operator cost | steering 0 min (self-reported; bulletin untouched); grading minutes: see REPORT | — |
| stopped at | 14/14 (hard end); stop rule never fired; s11 rc=1 zero-output stub, s14 zero-CLAIM synthesis | — |

## Q3 (loop-only token shape)

Per-session raw totals (M): 4.23, 4.34, 6.38, 4.57, 2.01, 3.12, 0.67, 5.27,
17.52, 3.56, 2.95, 21.08, 12.03, 3.40. No monotone context-growth signature;
spikes track compute-heavy sessions (s09, s12, s13), not report-reading
accumulation. **The three-curve split (mandatory CARRY / elective LOG /
sandbox reads) is NOT RECOVERABLE from the banked usage records** — the
launcher stored per-session totals only; Q3 reports this shape-level result
and the instrumentation gap.

## Telemetry anomalies

- s07 usage record: duration 0.4 min / 3 turns / 375 output tokens, yet
  $33.12 cost and a 160-line report banked in a 45-min MANIFEST slot —
  consistent with a mid-session API failure + internal retry whose final
  envelope only captured the last attempt; the report and its receipts are
  fully verified (verify-B). Cost total above uses the recorded $33.12.
- s11: rc=1, envelope subtype=success/is_error=true; 18-line stub report;
  its two registered predictions were both later confirmed exactly (s12).
