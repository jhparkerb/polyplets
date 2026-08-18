# HANDOFF — live state (updated 2026-08-18)

## RUNNING — k=7 defect calibration (dalby, window `k7-calib`, since 2026-08-18 17:40Z)

`scripts/dalby_perimeter_defect_k7_calib.sh`, 12 single cores alongside
Confetti, binary `git=6473890c` (the k=6 census stamp). Single-core wall at
`n = 30, 34, 38` for `k = 6` and `k = 7`, both lattices; the `k = 6` cells are
controls against the recorded 254/692/1666 s. **Purpose: price k=7 before
anyone commits to it** --- the pool script's `n^7.9` model predicted 1.8 h for
the k=6 census and the truth was 42 h king / 23 h square at 76-way, so that
model is refuted and a fresh exponent plus a k=7:k=6 ratio are needed. Result
tier: planning input, not a paper number. Resumable per cell; kill by PID.

**The k=7 census is NOT approved and NOT launched.** If Phi_4 enters at k=7 as
the exponent rule predicts, the fit needs ~44 series coefficients against 32,
on an onset of 31 against 24 --- a materially larger n than the k=6 run's 78,
against a cost that already came in 23x over its estimate.

## 2026-08-18 (latest) — THE ABZ PAPER WAS FREE; L6 EDITS PENDING

The paywalled Asinowski--Barequet--Zheng paper the L6 pass wanted is obtained:
the ANALCO 2018 polycube companion, "Polycubes with small perimeter defect,"
93--100, free from Simon Plouffe's OEIS citation mirror. Filed in `papers/`,
read; full verdict in `docs/priority-passes-2026-08-18.md` §ABZ full text.

- **The king column is a separate derivation, not a corollary of their
  framework.** Their proof is cut-shrinking to unique reduced representatives,
  and every mechanical step is stated in face-adjacency terms -- the
  `6n - e - 2|E|` accounting, the L-cell definition, the non-adjacency
  condition defining a cut, the handshake bound at max degree 6. The shape of
  the argument transports to king; the theorem does not.
- **They conjecture what we measured.** Their §4 conjectures highest-degree
  factor `(x-1)^(k+1)` and asymptotics `gamma n^k`. Our table has `Phi_1^(k+1)`
  and degree `k` for every `k <= 6` on both lattices.
- **Pending, his call: the L6 edits.** Cite the ANALCO paper rather than the
  slides, and restate the degree row as confirming a published conjecture
  rather than as our own observation.

Re-confirmed unobtainable in the same pass: **Barequet--Magal 2023** (no
preprint, no conference version; the author's page now offers only a
reprint-request mailto -- this is the remaining high-priority want),
**Andrews Memoirs 301**, **Rands & Welsh 1981**. Ben-Shachar's minimal-perimeter
paper is pinned as Algorithmica 85(1) (2023) 75--99, no arXiv. The Plouffe
mirror is recorded as exhausted for us in `papers/MISSING.md`.

## 2026-08-18 (later) — PRIORITY PASSES AND PROOF AUDIT OVER ALL NINE L PAPERS

**Three literature collisions, two of them load-bearing.** Record:
`docs/priority-passes-2026-08-18.md`.

- **L9 collides at the level of its whole statement.** The cut-count identity
  is the Fortuin-Kasteleyn/Potts correspondence -- evaluating `q^c` by colouring
  components instead of tracking them -- specialised to site clusters in scan
  order. Hoshen-Kopelman (1976) is the unsigned ancestor of the labelling;
  Jensen's signature algorithm is the method it is an alternative to. Abstract,
  introduction and novelty section rewritten; no theorem claimed. What survives
  is the specific rule and the proof that its window suffices.
- **L6 collides twice.** The Asinowski slides turned out to be **free** (the
  repo had them recorded as unobtainable): they carry the defect identity
  `k = e + 2f`, which is our `k = 2c + t` and licenses the enumeration prune,
  and the theorem that each fixed-defect GF is rational with cyclotomic
  denominator, for polyominoes and d-polycubes. Both attributed in place. The
  king column, the onset formula, the two-lattice universality, the coefficient
  triangle and the whole minimum end survive.
- **L5** gains Bousquet-Melou-Fedou as the square antecedent of the kernel.
  **L2** gains a related-work section on Rowland-Yassawi and the mod-3^k
  machinery with why neither applies (L4's non-D-finiteness kills the
  hypothesis). **L8**'s pass found nothing and the paper says why that is weak.

**Lesson recorded in `papers/MISSING.md`: two of the three collisions came from
pulling full text of sources already listed there, not from new searches.
Re-try that file before searching.**

**Proof audit** (`results/l-paper-proof-audit.md`) found **one real defect**:
L9 printed its final step as a product over component minima, but `b` depends
on the history of earlier choices -- the source proof uses downward induction
for exactly that reason. Fixed. Same family as L3's broken proof: a step that
reads as bookkeeping and is not. Both defects were invisible to prose review
and to numerical agreement, because the numbers were right.

Also audited: L7's Lemma T, all six steps, against two independent oracles
through n=16, **with the slack measured** -- steps (i) and (iv) run a factor ~2
from failing, (vi) a factor of 34, so the check confirms shapes and not
constants; two of five RED controls do not fire and the script says so. L5/L7's
phase decomposition to n=13: no animal visits both middle phases (implicit
until now), the mirror equality holds termwise, the remainder is 0.39% of the
class with falling growth ratio. L3's repaired proof re-derived from scratch:
shared sets are 4 cells orthogonal, 2 diagonal, frames 3 or 5 slots as claimed.

Still open, his: every L ledger reads "human verification: none"; whether
`docs/` and the Ghost Ship tree go public; the paywalled ABZ paper is still
wanted (the slides state theorems without proofs).

## 2026-08-18 — L PAPERS BROUGHT CURRENT; TWO NEW ONES; k=6 HARVESTED


**The k=6 censuses were already done.** Both n=78 runs finished on dalby
2026-08-09 and 08-10 (456/456 shards ok, `git=6473890c`) and the output was
never brought back into the repo; harvested 08-18, checksums matched against
dalby, committed. Real cost: king 42 h wall at 76-way, square 23 h --- the
pool script's own header predicted ~1.8 h, so that estimate is refuted and
should not be used as calibration for anything else.

**The k=6 verdict** (`results/perimeter-defect-diagonals.md`, appended):
onset 24 CONFIRMED by scan rather than fit; the Phi_3 exponent k-4 CONFIRMED;
Phi_4 absent CONFIRMED with D minimal and 39 spare zeros; **the Phi_2 leading
diagonal's closed form REFUTED** --- 5/2 measured against 15/4 predicted, on
both lattices. A second k=5 identity (the whole Phi_3 block agreeing across
lattices) also fails to extend. Universality survives and now runs through
k = 6: same period, degree, onset and leading coefficient on both lattices.

**All L papers updated, and there are nine.**

- **L6** --- compute gate cleared, placeholder section replaced by the verdict,
  two claims withdrawn, do-not-submit banner gone.
- **L5** --- the 08-17 salvage folded in: the q-Bessel kernel K, mu/q_c/A
  certified to 44-45 digits by exact interval arithmetic (agreeing with all 44
  corresponding extrapolated digits), area moments algebraic at every level.
  The limit law those give is **Richard arXiv:0704.0716** and is cited as a
  collision in three places, with Enting-Guttmann for the control.
- **L7** --- new: all four Prony exponentials, the negative one included, are
  reciprocals of zeros of K (`experiments/convex_kernel_zeros.py`). rho is
  q_1/q_2, not a measured decimal. The follow-up test (is nu 1/(smallest zero
  of det)?) does **not** converge under truncation and is recorded as a
  negative attempt, in the paper and in `results/convex-polyplets.md`.
- **L3** --- Proposition 6's proof was **false**: the Redelmeier decision
  string is undefined on re-entrant animals (96,065 of 147,941 missed at n=8).
  Replaced by the sound BFS-frame derivation of the same constant; the broken
  argument kept as a labelled warning. Twig route recorded as closed at exactly
  5^5/4^4.
- **L2** --- deficit 3 folded in: `v_3(P_k(3k-2)) > 3 <=> k = 1 mod 3` for all
  k, which predicts the deficit-3 sleeve zeros the census could only tabulate.
  Frame (A1)-(A4) stated, with the weight on the two derivations.
- **L1** --- the P_k denominator remark no longer calls minimality a fact about
  the lattice (it is basis-dependent, and was demoted in-tree on 2026-07-31);
  onset sharpness now points at L8's quartic, which gives it for large k
  conditional on two named gaps.
- **L8 (new)** --- below the onset: the diagonal law's error term. Exact frame,
  depth 1 closed by an algebraic quartic with every constant derived from it,
  depths 2-4 closed, theta_j = j-3/2 to j=7 with the estimator bias named, and
  alpha = 50/81 with its four analytic assumptions stated rather than softened.
- **L9 (new)** --- the cut-count identity: sum over scan-order colourings of
  prod (q-b) = q^c(S), proved in five lemmas, verified on 223,296 subsets with
  five RED controls, and explicit that the identity-to-program bridge is not
  crossed.

`paper/verify_l_papers.py` grows a k=6 check group (336 checks, 23 RED, all
fire). `paper/README.md` and `docs/publication-strategy-2026-08-18.md` are
current.

**Open, his:** the priority passes (L2, L6, L8, L9 have had none; L9's base
rate is unfavourable); every L ledger still reads "human verification: none";
and whether `docs/` and the Ghost Ship tree go public at all.

## 2026-08-17 — GHOST SHIP FILED + TRIAGED; salvage pending, run 2 undecided


Record committed (8336e02, 355 files incl. the loop's own sandbox tree).
Value triage run (e35c549) — the axis grading never covered.
**`results/ghostship/DISPOSITION.md` is the decision layer**; REPORT.md is
the graded record, VALUE-TRIAGE.md the novelty evidence.

Triage findings: all four king sequences absent from OEIS at full and
shifted prefixes (control hits A005436 exactly, so the pipeline finds real
hits) — an independent second search, since the loop had a working one all
along (see below); A014300/A112029/A153337
carry no polyomino interpretation, three comment-grade identifications.
Layer 1 (king-adjacency box/semiperimeter algebraic GF) and Layer 2
(q-series + 44-digit certified constants) find no literature collision —
the two real results. **Layer 3 SUPERSEDED**: Richard arXiv:0704.0716 gives
convex polygons the rectangles area law beta_{1,1/2}; the loop's
c_r = (r!)^2/2^(r+7) is exactly the moment sequence of U(1−U)/2. Sessions
09–14, the run's three most expensive among them, largely re-derive it.

Design consequence: "0 unwitting re-derivations" is scoped to the repo. A
sealed sandbox cannot check priority and the rubric never asks, so
cost-per-new-result is unmeasurable. Larger defect than the untested
bulletin.

Second rubric hole (VALUE-TRIAGE §F, 7ababfc): s01 solved the OEIS
Cloudflare challenge with a browser User-Agent and the loop searched
normally through s05; s06 ran bare curl, re-derived "OEIS SEARCH is
blocked", and banked it as a DEAD line that s07 repeated and
FINAL-SYNTHESIS carries under "do not retry". Fourth instance of the
session-boundary handoff family, and invisible to grading — the claim
table grades CARRY claims, DEAD lines are not claims. A false DEAD line
removes a capability from every successor.

Post-action review CLOSED (b468ee2, `results/ghostship/POST-ACTION.md`):
DEAD-line audit — 4 of 10 substantive DEAD lines defective (2 false, 1
mislabelled lead, 1 unmeasured cost) against 0 FALSE in 64 graded claims;
s01's closed form independently re-implemented, 200/200 terms. Panel
scored — ~30 of 34 recommendations adopted, R3 #1 became the design, R3 #3
caught the memory leak that would have voided the run; all three lanes
shared one blind spot (they audited what the loop asserts, never what it
forecloses).

SALVAGE DONE (a4c8085): Layer 1 + Layer 2 imported as a dated section at
the end of `results/convex-polyplets.md`. The import found that half of
Layer 1 was already banked here — the s≤200 series and degree-2
algebraicity, 2026-08-05, matching the loop's 200 terms exactly — so the
loop re-derived repo work as well as literature, and the sealed denominator
saw neither (it is scoped to the 21 slice files). Three rings, metric
covers the innermost, reports 0.

Decided 2026-08-17: **no run 2, and no further unattended-loop
machinery.** The panel pattern (adversarial desk lanes before spending) and
the court are what earned their cost; the loop did not. Literature-priority
pass adopted as standing practice on any result called new.

Open, his: OEIS sequences + 3 comments staged behind the viva; dalby
`~/var/ghostship/` + `~/tmp/ghostship-grading/` still retained.

## 2026-08-15 (late) — GHOST SHIP RUN + GRADING COMPLETE [SUPERSEDED]

Superseded section below kept for the record. The run compressed to one
day at jasonp's direction (all 14 sessions banked 10:20–20:38 EDT
08-15; deviations with receipts in `results/ghostship/DIVERGENCES.md`),
then graded the same evening per §7 with all blinds enforced.
**`results/ghostship/REPORT.md` is the record**; claim table (hashed
before predictions opened), three provenance-stripped verify files, and
blind prediction scores under `results/ghostship/grading/`.

Verdict (sealed rule): **DID POORLY on the rung criterion alone** —
rung 1/3, banked at s01 in ~19 model-minutes; column-convex/A187077
never visited — with claim hygiene clean beyond both predictions: 64
claims → 58 verified-by-execution, 0 FALSE, 0 unwitting re-derivations,
0 judgment failures; 30/31 VERIFY sound. Cost $225.20 vs court ≈$140
(1.6×); raw tokens below the court evening. Predictions: jasonp 1H/1P/7M,
Fable 4H/6P/5M/1U. Q2 NOT TESTED (bulletin untouched). Real failure
shape: session-boundary job handoff (3×, s11–s14) — fix before any
second run. Contamination log clean (`CONTAMINATION.md`, one
non-contaminating entry). Everything uncommitted; dalby
`~/var/ghostship/` + `~/tmp/ghostship-grading/` retained pending his
cleanup. Open decisions, his: commit the ghostship results tree; whether
a responsive-steering arm (DIVERGENCES.md D1) ever runs.

## 2026-08-15 — GHOST SHIP LAUNCHED; s01 fires 20:00 EDT tonight [SUPERSEDED]

The unattended-loop experiment is live. Protocol:
`docs/ghostship-preregistration.md` (v2 + §4 calendar + OEIS parity ruling);
sandbox spec `results/ghostship/SANDBOX.md`; all seven §7 artifacts sealed
with sha256s recorded in the pre-registration (both predictions, answer
key, banked-claim list, calibration, worked examples, verdict rule).
Predictions split: **jasonp rung 3 at s10, 7 re-derivations, 33% bad
claims, >3× cost; Fable rung 2 at ~s9, rung 3 never, 2 re-derivations,
≥15× cost.**

Mechanics: dalby `~/var/ghostship/` — 21-file sandbox at `74b2c20` +
HISTORY.txt, launcher `run_session.sh` (repo copy
`scripts/ghostship/`), cron `0 4,12,20 * * *` (dalby clock = EDT),
NOT_BEFORE gates until 19:00 08-15. s01 tonight 20:00, s02–s04 Sun,
s05–s13 Mon–Wed, s14 Thu 04:00. Auth: long-lived token in
`~/var/ghostship/token` + isolated `claude-config/` (no CLAUDE.md, no
memory — C6). Smoke tests green (haiku + fable). Stop rule arms at s6;
missing report retried once; timeout 2 h/session.

**Standing rules while it runs**: nobody reads `sandbox/reports/`
content until grading (MANIFEST, session count, machine health are
fine); jasonp steers only via `~/var/ghostship/BULLETIN.md`; any
deviation → `results/ghostship/CONTAMINATION.md`. Between slots dalby
shows NO claude process — that is correct, not a failure. Token-limit
risk acknowledged: usage JSONs land per session in `usage/`; check s01's
burn before Sunday; stretching to 2/day is a loggable schedule change,
not a C3 break.

**After the run (or a HALT)**: grading order per §7 — claim table filed
and hashed BEFORE either prediction file is opened; claim verification
provenance-stripped; prediction scoring authorship-stripped by a fresh
instance. Court baseline = the real 2026-07-12 ladder
`60b6ac5`→`3afca73`→`37ce404`, tokens/wall from that session record.

Also this morning: state system banked (`docs/state-minimal.md`, his
adopt/bank call open); `CLAUDE_CODE_DISABLE_MOUSE=1` added to his global
settings (mouse capture was hijacking Terminal.app selection; ctrl-c
had collaterally stopped three idle agents — no loss).

## 2026-08-14 (evening) — backlog set 5/6/2/4/3 executed; one lane still out

jasonp queued five open threads (his numbering: 5 anisotropic novelty check,
6 onset-defect depth ≥ 2, 2 king twigs, 4 cancellation identity, 3 Middle
Kingdom) with Exact Change (1) deferred on a running job. State:

- **5 and 3 were already done** — the anisotropic novelty check closed
  2026-08-01 (three databases, no collision; paper already scoped) and
  Middle Kingdom is complete through Phase 4 and committed. Both memory
  entries were stale and are fixed; nothing was re-run.
- **2 — King twigs CLOSED, closed door** (`results/king-twigs-l1.md`,
  harness `experiments/kingtwigs/l1_schemes.py`, GREEN on dalby). Level-1
  king twig bound = 5⁵/4⁴ = 12.207 **exactly**; the KR/BS deferral gain is
  structurally blocked on king adjacency (a deferred cell always lands in
  the child's shared set — machine witness `{(0,0),(0,−1),(−1,−1)}`);
  12.207 ≥ the plan's pre-registered 10.5 kill line; C_i ladder dead by
  budget (~24% needed vs BS's 6.3% precedent). λ ≤ 9.3154 untouched.
  Collateral: **the crude-bound proof in
  `docs/proofs/polyplet-upper-bound.md` was broken** (its frontier misses
  re-entrant animals — 65% of n=8; witnessed, measured) and is repaired in
  place with a sound BFS-frame derivation of the same constant.
- **4 — the cancellation identity is written and proved**
  (`docs/proofs/cutcount-identity.md`, Birthright agent off
  `docs/birthright-brief.md`): Σ_configs Π_births (q − b) = q^{c(S)},
  **exactly in ℤ[q]**, unconditional; five lemmas; check
  `experiments/birthright_identity_check.py` (223k subsets, 0 mismatches,
  5 RED controls fire) independently re-run, sha-matched. Its §6 lists four
  corrections to `docs/b1-closure-plan.md` §7's paraphrase (updated) and
  records that the engine header's cited `probe_cutcount_dp.py` was deleted
  from the tree. Tier 2 delimited, not done; Lean formalization open.
  **Gate wiring undecided**: the check is a natural `gate-cutcount-identity`
  but the gympie ban means `make` must run on ayr/dalby — jasonp's call.
- **1 unblocked**: the running job was `exactchange_minauto.py` fast-closure
  on dalby; it landed clean — N-family automaton ranks H=10/11/12 =
  453/912/1818, all A034299, brute anchors OK. Banked in
  `results/exactchange-probes.md`; H=13 test now priced ~5–6 h single-core
  off the measured H=12 wall (1696 s); still needs sign-off + second source.

**Ridgeline (item 6) LANDED and VERIFIED** —
`results/ridgeline-depth-amplitudes.md`, scripts `experiments/ridgeline_*.py`
(hash-matched repo↔dalby, master + vertex independently re-run GREEN, RED
controls fire). **The depth-amplitude family is derived: j = 5 is 35/8**,
and the whole family is one constant — the onset branch-point velocity
α = 50/81 = 450/729, computed by finite enumeration over the vetted row
transfer; the central binomials are Γ(j−1/2) in disguise, and 118/27 was an
artefact of the Γ-weighted normalisation. The scaling function is a square
root, not Airy (dispersion nondegenerate). Depth-1 constants reproduced
(C₁ to 2.5e−12). **Read §5 (limits ledger) before citing** — the
singularity-form assumptions are named, argued and measured but not proved;
proving assumption 4 (the (J,P) perturbation with correct critical vectors)
is the recorded self-contained follow-up. Memories updated
(severance-w4-depth-tower). The whole 5/6/2/4/3 set is now CLOSED.

Machines: **ayr unreachable** since ~23:00 UTC (no route to host — power
cut until proven otherwise; nothing from this set is owed it). Confetti
H=18 still running on dalby per the entry below; today's desk-scale runs
went to dalby scratch (`~/tmp/kingtwigs`, `~/tmp/birthright`,
`~/tmp/ridgeline` — disposable). **Everything from this set is
uncommitted** for review: modified `docs/king-twigs-plan.md` (closed
header), `docs/proofs/polyplet-upper-bound.md`, `docs/b1-closure-plan.md`,
`results/exactchange-probes.md`; new `results/king-twigs-l1.md`,
`docs/proofs/cutcount-identity.md`, `experiments/kingtwigs/`,
`experiments/birthright_identity_check.py`, the two brief files. jasonp's
own pending edits (`docs/rook-parity.md` deletion, `results/coin-lift-g2.md`)
untouched.

## 2026-08-14 — both plans reviewed, reconciled, and executed as far as they go

Two Fable reviews (one per plan) against the tree, reconciled, then executed.
Commits `76f71c5` (Coin Lift), `1e430fb` (Motley), `b9d725b` on branch
`half-measure`. Neither review found a plan blocked; both found a load-bearing
statement that did not survive contact.

- **Coin Lift is CLOSED at G2. It is dead.** The char-2 collapse does not
  survive one lift: at H = 9, mu_1 = 229, mu_2 = 459, mu_3 = 500, mu_4 = 501 =
  the generic rank exactly, and mu_2/mu_1 grows every height (1.00 → 2.00 over
  H = 4..9). **Coin Flip, Coin Roll and Biased Coin Flip are untouched** — one
  deterministic bit, or a probabilistic fingerprint. G3 and G4 never run.
  `results/coin-lift-g2.md`, probe `experiments/tristruct/r3_lift_snf_probe.py`.
- **G2 as written could never have fired**, and the shape of the error is worth
  carrying: "the Z/4 free rank" counts the invariant factors that are units mod
  4, which is identically the GF(2) rank. The well-posed object is
  `mu_k = #{invariant factors with v_2 < k}`, the minimal generator count of
  the Hankel column module over Z/2^k.
- **Other characteristics are also dead, and now it is a theorem plus an
  exhaustive sweep** — `results/coin-flip-characteristic-landscape.md`,
  commit `8861523`. Every weighted automaton over every commutative ring has
  dimension >= min_p rank_{F_p} (reduce mod a maximal ideal), field extensions
  of char 2 are rank-identical, and multiplicative grading is exactly
  rank-preserving — so **Coin Roll's freeness is upgraded from measurement to
  theorem**, and there is nothing to search for in weightings. A
  determinantal-divisor budget `sum_p d_p ln p <= (N/2) ln N` then makes the
  remaining sweep finite; certified at H = 6..9 with rank_Q pinned rather than
  assumed. **At H = 6, p = 2 is the only prime in the universe that drops the
  rank at all**; from H = 7 on only p = 3 moves it, by 1.1-2.6% against
  characteristic 2's 34-54%. Characteristic 2's share grows with height and
  the competitor cutoff falls (44,633 -> 849 across H = 6..9). One
  deterministic bit is the unique optimum of the class.
  Round 1 found rook has no char-2 crack; the collapse is specific to the
  characteristic *and* the stencil.
- **Motley Step 0 is DONE and GREEN** — `results/motley-step0.md`. 16 of 16
  rows byte-identical to the banked rows, 640 of 640 cells against the banked
  triangle, from a clean worktree (`~/src/pm-b1-step0`, stamp `48ac1089`, no
  `-dirty`) with `gate-cutcount-b1` GREEN on that build and the binary's
  sha256 recorded. 4.7 h of wall across three streams against 6.7 core-hours
  serial; H = 16's wall landed 3.5% above the 2026-08-11 calibration despite
  co-residency. **a(n) is citable for n <= 31**, by a rule that never decides
  connectivity.
- **Half Measure is written, gated and measured** (`b9d725b`): rows
  byte-identical to both the reference binary and the banked rows at H = 12,
  13, 14, 15 **and 16** — every height the reference can also reach; payload factor **0.514 measured** — the x1.9 the ladder budgets — and
  a **x1.46-1.57 wall bonus** nobody had counted on. That moves H = 17 from
  100 GB / ~15 h to **91 GB / ~7-10 h**, and the +-20% census band's bad end
  (109 GB) now fits dalby with 13 GB to spare. The check-split does not need to
  be pulled forward.
- **H = 17 is DONE, GREEN** (receipt `results/motley-h17.md`; row banked as
  `results/cutcount_b1/rows/C17.out`): T(n,17) matches the incumbent triangle
  at all 24 cells, 0 mismatch — **a(n) closed rule-independently for
  n <= 33**. Measured: wall 39,117 s (10.9 h), peak RSS 95.0 GB (91
  predicted), census 23,681,423 windows. Per-height ratios above H = 16 —
  census x3.023, RSS x2.963, wall x3.198 same-payload — match the ladder
  constants; **the pre-registered kill condition does not fire**, so
  Confetti's and Ticker Tape's projections stand on a measured point.
  Measured Half Measure factors at H = 16: RSS x0.5147, wall x1.394.
- **Confetti (H = 18) is RUNNING** — launched 2026-08-14 17:56 EDT, tmux
  `motley-h18` on dalby, driver PID in `~/var/motley-h18/driver.pid`. Five
  sequential 31-bit-prime passes, CRT from four + held-out fifth (RED-D),
  T(n,18) vs the incumbent triangle at the end; **~16 h/pass, ~82 h total,
  ~83 GB peak** (measured: modp wall ~0.47x u128 at H = 12, 13). Gate
  battery GREEN on dalby (`tests/gate_confetti.py`, half-measure `3002104`;
  brute A030232-anchored oracle, 4 planted REDs all caught) and **receipt
  enforcement now exists and is red-tested** — the runner
  (`scripts/dalby_confetti_h18.sh`, master `443ed36`) refuses to run a
  binary whose sha256 lacks a green receipt. Product on GREEN: a(n)
  rule-independent for n <= 35.
- **Exact Change** (char-2 basis hunt, `results/exactchange-probes.md`,
  `afec943`): rank = A034299 exactly (nine points, r(21) = 932,071
  predicted); quotient is cross-mask linear algebra; cell-level rank
  ~Theta(H 2^H) shrinks the compression to ~6x vs the spin engine; sparse
  transitions exist in the closure basis, no a-priori construction. Parked
  OPEN — jasonp flags the OEIS hit as very interesting, come back to it.
- **The engine had an uncosted `H <= 16` ceiling** and refused to start. Three
  argument checks, not a property of the algorithm; no plan or review caught
  it. Raised to the structural limit (key packing, H <= 24) with the other two
  bounds now asserted rather than assumed. **H = 18 would have overflowed a
  12-entry stack buffer by one, silently** — found two rungs before the one
  that needed it. Core untouched; commit `4df3fec`.
- **H = 17 has an external oracle**: `results/triangle.txt` carries the
  incumbent's T(n,17) for every n <= 40, so the product and its check land
  together. `scripts/dalby_motley_h17.sh`, fail-closed.
- Plan corrections from the reviews: the banked ladder already closes
  **n <= 31**, not 30; Motley's `--modp` mode is **already committed** on
  `second-source` and carries two streams, not three, so Confetti's A(1) check
  rests on the held-out prime and the banked rows alone; and the receipt
  enforcement Confetti's gate battery names **does not exist yet**.
- **Open for jasonp**: `docs/b1-closure-plan.md` §7 argues the Tier-1
  cancellation-identity write-up should come *before* the engineering ladder;
  neither Motley doc mentions it. Nothing was decided here.

## 2026-08-14 — Motley and Coin Lift: two plans, and one exclusion

Plans: `docs/motley-plan.md`, `docs/coin-lift-plan.md`. Goal docs:
`docs/motley-goal.md`, `docs/coin-lift-goal.md`.

- **B1 is now Motley** — the colour-symmetrized spin TM that paints every
  subset and never decides connectivity. Its three planned rungs: **Half
  Measure** (`I256` -> `u128`, x1.9), **Confetti** (4 x 31-bit residues + CRT,
  x4), **Ticker Tape** (8 x 16-bit residues, x2, and it carries the check-split
  and the flat arena because H = 19 does not fit without them).
- Motley's reach: Half Measure -> H = 17, closes a(n) for n <= 33; Confetti ->
  H = 18, n <= 35; Ticker Tape -> H = 19, n <= 37. Row 40's residual band goes
  9 -> 7 -> 5 -> 3 cells. **Step 0 is a 6.7 core-hour clean re-run of H <= 16**,
  which makes the already-closed a(30) citable.
- **Coin Lift is capped, and the argument is from the repo's own numbers.** A
  Z/2^k realization of bounded dimension for all k gives a Z_2- hence
  Q-realization, and rank_Q >= rank_{F_p}; the measured mod-p Hankel rank
  extrapolates to ~2.3e7 at H = 21 against the char-2 dimension of 9.2e5. So
  **exact values at char-2 dimension are excluded** — the floor is 25x. What
  survives is 2-3 deterministic bits per cell (Z/4, Z/8), untouched by the
  limit argument.
- **Second Coin Lift hazard, easy to miss**: the collapse was measured on the
  *incumbent-rule* automaton, so a compressed realization obtained by
  projecting it inherits the incumbent's rule and certifies nothing. Rule
  independence requires a basis described from the definition of
  king-connectivity, not from the projection. That is gate G3 and it has veto
  power.
- Gates G1 (rank ladder past H = 9, hours) and G2 (Z/4 module structure,
  minutes) together price the whole Coin Lift program. Nothing downstream
  starts before both land.
- **No ensemble recommended for either plan right now.** Motley is a specified
  engineering sequence with mechanical oracles; Coin Lift's first two gates are
  a day of solo work. An ensemble earns its keep only at Coin Lift G3, and only
  if G1 and G2 pass.

## 2026-08-13 — Closure: the P_k lock, and B1's RAM ceiling

Full record and arithmetic: `docs/b1-closure-plan.md`.

- **Every P_k needed for row 40 is anchored at H <= 20**, so a B1 sweep to
  H = 20 pins the whole H >= 22 band ab initio at **zero additional compute**
  (level k = 40-H; band H >= 22 is k <= 18; P_18's anchors are T(37,19) and
  T(38,20)). H <= 20 in RAM plus that lock leaves **one cell** of row 40 not
  rule-independent, **T(40,21)** — P_19's second anchor is T(40,21) itself, so it cannot be reached
  by formula. The tower does not cut the sweep: break-even lands exactly on
  H = 21.
- **RAM ladder against dalby's 121 GB available**, off the measured
  8,142 B/window and the census-anchored window projection. Each height demands
  a factor off baseline — H17 1.6x, H18 4.9x, H19 15.2x, H20 47.7x, H21 151x —
  and the rungs are ordered biggest-and-simplest-first in the plan's §3:
  `I256 -> u128` (x1.9) buys **H = 17** on its own (100 GB); the residue ladder
  with CRT (x4/x8/x16 at u32/u16/u8) buys **H = 18** (52 GB) and **H = 19**
  (87 GB); **H = 20** (92 GB) needs the last width plus a flat arena and
  chunked release of the consumed buffer, and sits at the wall with ~24% margin.
- **H = 21 cannot fit at any payload width** — 2.25B windows means 135 GB of
  keys before a single coefficient is stored. Out-of-core (504 GB working set
  vs 563 GB free NVMe) or nothing.
- Dead levers, recorded so they are not re-derived: area-variable
  evaluation/interpolation (true degree is H*W = 861), and the ranged-area
  payload that gave the incumbent 1.89x (the payload is dense here).
- Next measurement, and it carries the rest: **H = 17 exact-u128**, one core,
  ~15 h — it puts a real wall, RSS, and census ratio under every projection
  above.

## 2026-08-14 — rook parity round 1 run and closed; the goal did not survive it

One desk-only round, six Fable agents, no compute dispatched. Brief
`docs/rook1-brief.md`, product `docs/rook-parity-bar.md`, lane files and the
ledger/queue/INSTRUMENTS under `results/rook1/`. Commits `e72e5ac`..`4a90412`.

**The goal in `docs/rook-parity.md` is not well-formed, and the round is what
established that.** jasonp's verdict, and the evidence agrees: the pin sits
0.31% above what the incumbent already measures, the test is passable by the
incumbent, and the bar contradicts the pin. Do not restart it as written; do not
re-run the round. The goal file itself is UNCHANGED by instruction — every
correction below lives in the brief, the bar file, or the lane files.

- **The incumbent's base is b = 1.7266 = √2.9813** (R1-A), from the measured
  frontier per-height cpu ratio, phase C / phase B = 3,329,644 / 1,116,858, on
  the dH/dn = ½ treadmill. Below the √3 = 1.7321 pin. **`kink-carry.md:46`'s
  2.42–2.5 is WRONG as a kink cost claim** — a pre-kink state-growth number from
  another engine on another trajectory. `kink-carry.md:69`'s 1.61 is the
  states/RAM base, a lower bound on cost. The goal file's whole quantitative
  spine inherited the wrong number.
- **Conditional, and this is the live question**: 1.7266 holds on a *fitted*-P_k
  treadmill; frozen fence gives 2.98. And the per-height ratio is still rising
  (2.60 → 2.73 → 2.98 across H18..H21) — if it crosses 3, b crosses the pin from
  below. That is queue row A2, the only open question that can still move the
  base.
- **Gate 0 fired its kill: the ab-initio P_k tower is DEAD** (R1-B). g ≈ 20 per
  level (ratio 21.0 at k=4→5, MEASURED lower bound 8.15 at k=5→6,
  `results/defect-gas.md:242`). At even g = 3, k=9 → k=19 is 7.4 years of
  16-thread dalby.
- **But gate 0 measured the wrong object** (R1-E): the a(40) assembly consumes
  two rational constants per level, not the weight DP, and depth ≤ 4 below-onset
  cells are closed ab initio — so every level is pinnable from the route's own
  H ≤ 19 sweep, and depth ≥ 5 is consumed nowhere. Not a rescue: both routes
  sweep to half height, so the re-anchored route's base **is** b, and deleting
  phases B+C cpu) is a constant factor, out of scope by the goal's
  own terms. Corrected gate-0 measurement (e ≤ 3 family DP growth over
  K = 19..25, minutes-scale) is queue row E2, UNRUN.
- **King→rook transport is DEAD unconditionally**, not merely out of scope
  (R1-D). Counting floor on all injective reductions β ≥ ln λ_k / ln λ_r = 1.244
  rigorous, 1.400 at best estimates; budget at b = 1.7266 is β < 0.994. The
  goal's asserted β ≥ 2 for the diagonal-splice family is now derived and tight
  (lattice parity ⇒ ≥ 2 expensive axes ⇒ ≥ 2n−1 cells; identity+bridges attains
  it).
- **Rook shows NO char-2 crack** (R1-C): GF(2) Hankel rank 20/49/119/288/696/1681
  at H = 4..9 on a state space identical to king's, growth ~2.42×/height, mod-p
  exactly full. King's 0.44·2^H collapse is stencil-specific, so **the INV-4
  explicit-basis hunt loses its CKN precedent** — reset its prior.
- **Collateral, and it belongs to any future gate**: a bottom-anchored transition
  kill cancels exactly in the exact-height second-difference telescope — the
  corrupted engine still reproduces A001168 for all n ≤ 8. End-to-end value ties
  pass that whole defect class; plant an anchored defect, not just the NW-stencil
  drop (queue row C4).
- **Held for jasonp, undecided**: A1-JOB-1 (incumbent's on-window n=24..30 curve,
  ~2 h dalby) — my recommendation is to run it as the incumbent arm of gate 1
  alongside a challenger, never alone, for commensurability. A4 (gate 1's strict
  clause is now stronger than the √3 pin). E3 (the a(40) test may separate
  nothing, since the treadmill self-anchors).
- **New mechanical control, kept**: `scripts/check_receipts.sh` +
  `make gate-receipts`, red-first with three planted-claim fixtures. A status
  token in a table cell or `status:` line under `results/rook*/`,
  `docs/rook*-brief.md` or `docs/rook-parity-bar.md` needs an in-tree non-empty
  path on the same line.
- **Process lesson, jasonp's**: the round's mechanical controls were aimed at
  transmission failures while the actual failure was target selection again. The
  brief-adversary audited the round's premises but not the *goal's*, and passed
  all four lanes. The base anatomy audit was the goal file's own first question
  and it ran in parallel with three lanes that depended on its answer; it should
  have run before the brief existed.

## 2026-08-13 — triangle salvage merged; reading pass; king twigs opened

- **Triangle-structure agent campaign closed as a FAILURE** (four rounds;
  `docs/triangle-postmortem.md`). Salvage merged to master (`bb897b1`);
  the index of what survived, with verification labels and remaining work
  per item, is `results/triangle-salvage.md`. Per-agent round records stay
  on the `triangle-structure` branch. New banked numbers from the salvage:
  **T(40,20) ≡ 1 and T(40,21) ≡ 1 (mod 2)** — spin/involution route, twin
  runs byte-identical across ayr/dalby, oracle-checked vs the B1 recount
  (caveat pre-registered: not independent of B1).
- **Decade bibliography built**: `papers/polyplets-2024-2026.bib`,
  2016–2026 year-by-year arXiv sweep, search provenance in comments;
  15 PDFs fetched and indexed, 5 unobtainable filed in MISSING.md.
  Across all eleven years: zero papers use "polyplet"/"polyking"; the
  published enumeration frontier is still n=18 (Tremblay–Vernay 2024).
- **Reading-pass verdicts** (four readers over the 11 PDFs, load-bearing
  claims cross-checked): the percolation→growth route (Georgakopoulos–
  Panagiotis) is a **closed door** — capped at λ ≥ 5.256 by the true king
  p_c, permanently under our 6.543; the two-term inequality's form appears
  nowhere in the Bui corpus (last novelty check standing: Jensen-style
  transfer-matrix literature); authoritative king threshold is
  0.40725395… = 1 − p_c(square site), Jacobsen 2015 via Sykes–Essam.
- **King twigs thread OPEN** (`docs/king-twigs-plan.md`): the KR/BS twig
  ladder is untried on king adjacency and level-1 arithmetic suggests it
  could undercut the standing λ ≤ 20000/2147 ≈ 9.3154. Next action = the
  Phase-2 afternoon in the plan. Do not cite KR's 4.6496 (unreproduced).
- **Measured side-result**: the king lattice is an in-scope 2D
  counterexample to the necessity of Barequet–Ben-Shachar's constant-isomer
  conditions — Premise 2 fails at every inflation-chain root, conclusion
  holds 9/9 (`cpp/kingperim.cpp`, `cpp/kinginflate.cpp`, wired into make);
  the |M_n| census 1,2,6,1,8,2,22,6,1,30,… has no OEIS match.
- Full `make` gate battery GREEN on this state (gate-citations fixed:
  three planned-file citations marked per the gate's remedy).

## PROJECT CLOSES AT a(40) — FINAL TERM LANDED
**a(40) = 56749893611764175164545926946127 BANKED 2026-07-28**
(`results/ns_a40/` + PROVENANCE.md). jasonp 2026-07-27: the project
closes at a(40); the a(41)-a(43) ladder is CANCELLED (a(41) would add
only the term + an orphan P_20 fit point; the next validation seam,
a(42), is out of scope). Growth 6.9352 — series 6.9212, 6.9261,
6.9308, 6.9352, smooth toward λ≈7.11.

Landed with the run:
- A40_VALIDATE_PASS (b-file n≤20 + banked chain a(21)-a(39)).
- **Mass P_k holdout certification: P_0..P_18 ALL confirmed** — the
  real H21 sweep reproduces a(39)'s closed-form H21 shard exactly on
  every row n=21..39, including P_18's first holdout T(39,21).
- T(40,40)=3^39 and T(40,39)=955·3^36=P_1(40)·3^36 exact.

Remaining close-out:
0. ~~H20 recheck~~ **DONE 2026-07-29: A40_H20_RECHECK_MATCH** — clean
   H20-only re-sweep (`scripts/a40_h20_recheck.sh`, 48c, 12.2h wall)
   reproduced the Zero-Harvest-recovered h20.out byte-for-byte;
   T(40,20) independently confirmed, recovery asterisk removed
   (PROVENANCE.md updated).
1. ~~Wire P_19~~ **DONE 2026-07-29** (commit 9671e94): derived via
   scripts/derive_pk_fast.py from real T(39,20) + T(40,21), leading
   coeff 25^19/19! + k!-integrality confirmed, red-first
   diag_p19_test.go, k-range fence moved to k=20. Permanently
   fitted-no-holdout (a holdout would need a(42)'s real H22).
2. ~~Fix the Zero Harvest engine bug~~ **DONE 2026-07-29** (red-first
   orchestrator/zero_harvest_test.go): checkpoint now carries the
   current height's partial per-height row (`htri` lines), resume
   seeds it, and writePerHeight refuses all-zero rows. The red test
   also exposed the silent variant — after ANY mid-height resume the
   old code's h<H>.out under-counted (phase B's own pre-clobber
   h20.out was already wrong; the checkpoint was always the sole
   correct copy — PROVENANCE.md corrected accordingly).
3. **jasonp: technical-report placeholders** — real a(40) above;
   revision list delivered in-session 2026-07-27 (line-110 brace, P_k
   k≤16→18/19, λ para, Split truncation, Reproducibility section).
4. Publish prep continues (Leiden easy-fixes committed cca0c30;
   repo/blog/OEIS sequencing is jasonp's).

## AUDIT-2026-07-30 close-out campaign — LANDED (2026-07-30)
Third adversarial campaign (after 2026-06-28 and 2026-07-13), run at
publish: five parallel read-only audits (Second Wind C++ data path,
orchestrator resume/phasing/fastmap, diagonal injection, publish
artifacts/checkers, Lean + strip second source), ~35 findings.
Dispositions and the headline write-ups: **`AUDIT-2026-07-30.md`**.
Fix batches A/B/C/D all landed on master (`git log --grep
AUDIT-2026-07-30`). Bottom line unchanged by any of it: **no banked
value is wrong.**

What the campaign actually bought, in one line each:
- fail-closed reader/finalize (the one HIGH engine fix, E1);
- `verify_technical_report.py` no longer silently skips 42 of 78 Table 2
  cells (P1), and its pole check now covers 342 in-onset cells;
- the recorded a(40) recipe pins `--max-diag-k 18`, so a re-run still
  performs the real H21 sweep instead of injecting it from P_19 (D1);
- holdout reporting stopped grading formulas against their own output
  (D2/D3);
- **a(40) corroboration by mass is now stated** in
  `results/ns_a40/PROVENANCE.md` — post-N=40-strip-run, the band with no
  second source is H15-19, 43.8% of the term (H11-14, 37.5%, is
  strip-second-sourced; 2026-07-31 hygiene sweep). That is what the T2⁻
  grade means.
- the strip second source is scoped honestly (same union-find rule as
  `core/transition.h`; the Python "twin" is a port; coverage is 72.2%
  of cells honestly counted post-N=40 (95.4% doc-style), the k=19
  diagonal deliberately excluded);
- Lean: the Shape/Peel axiom claims are `#guard_msgs`-enforced, the
  four "outside the default build" statements corrected, a build
  receipt banked.

## FLEET STATE at 2026-08-07 18:09 EDT (written for a fresh session)

Three jobs live, all feeding the perimeter-grading paper (L6 in
`docs/publication-split.md`) and nothing else. **Re-arm the watchers first
thing** — they are `tail --pid` over ssh and do not survive a session change.

| box | job | PID to watch | state at 18:09 |
|---|---|---|---|
| ayr | `scripts/ayr_pmin48.sh` → square8 min-end p=48, tmux `0:pmin48`, log `results/ayr_pmin48.runlog` | 2261 | **DONE 2026-08-07 22:12 UTC** — `AYR_PMIN48_DONE`, 121/121 frames, census `results/perimmin_square8_p48_r6.txt` (1526 rows) identical on ayr and here by sha256; script and runlog committed 2026-08-08 |
| dalby | `scripts/dalby_square4_deep.sh` → square4 min-end deep boxes, tmux `0:j7w17` | 2423184 | **DONE 2026-08-08 08:51 EDT** — `DEEP_DONE`, both boxes `result=ok`. `W=15` `1 4 18 60 187 524 1388 3452 8193`, `W=17` `... 3452 8229`. Censuses and logs committed here 2026-08-09; the `j=7,8` predictions are confirmed and the `8193`/`8229` split is explained and measured (`results/perimeter-both-ends.md`) |
| dalby | `dalby_perimeter_defect_pool.sh square8 78 6`, tmux `0:pdk6big` | 2420612 (stage 1) | all 456 shards dispatched, a couple still running. **Stage 2 (`square4 78 6`) starts automatically after**, then `STAGE2_ALLDONE` and a `sleep 86400` — so watch 2420612, not the outer 2420610, and re-arm on stage 2 |

gympie is idle; its three finished windows (percell mod-4, symtm strip profile,
subgroup mod-4) were inspected, confirmed banked and closed 2026-08-07.

**Git divergence, reconciled content-wise 2026-08-08.** `origin/master` is at
3b7359d. gympie's f333ec1/840885c are in local master; ayr's 78ec1cd/6fb3f39
(power-cut receipt, pmin48 script) are now in local master as byte-identical
content, sha256-verified against ayr's commits. Local master is canonical.
Remaining, after jasonp pushes: ayr resets to the pushed master (its two local
commits are content-redundant); dalby reconciles only after its runs land —
do not touch dalby's clone while the drivers hold it.

## LANDED — ayr, king min-end census at p=48 (started 2026-08-07 18:01 EDT, done 22:12 UTC)
`scripts/ayr_pmin48.sh`, tmux `0:pmin48`, driver PID 2261, log
`results/ayr_pmin48.runlog`. Feeds the minimum end of
`results/perimeter-both-ends.md` — the king partner to the square4 deep boxes
on dalby — and through it the perimeter-grading paper (L6 in
`docs/publication-split.md`). Tier: reproducible measurement. Budget 5-8 h at
32 threads; p=48 has never finished, so anything tighter is unmeasured.

The first attempt died at 3.9 h in the afternoon's power cut with a **0-byte**
output file: `perimeter_min` accumulated all 121 frames in memory and printed
only at exit, so it was strictly all-or-nothing. Nothing was corrupted; all of
it was lost. Receipt kept in `results/dead-2026-08-07-powercut/`.

Fixed rather than retried. `scripts/perimeter_min_sharded.sh` runs one `--only`
frame per invocation, skips frames that are provably whole (a `# box` line AND
the trailer), and publishes each by atomic rename, so resuming is re-running
the same command and an interrupted frame can never pass for a finished one.
The trap it had to clear: `--only` forces `mult=1` while the plan carries
`mult=2` for every W<H frame, so `experiments/perimeter_min_merge.py` reapplies
the multiplicity from the plan the binary itself emitted.
`make gate-perimeter-min-shard` checks the merge byte-for-byte against the
monolithic run on both lattices, damages frame files the four ways a kill can,
and RED-controls the multiplicity by dropping it.

Before starting p=48 the job re-ran both gates on ayr's own build and made the
sharded driver **re-derive the banked p=40 census**, with git as the diff: the
tracked file moved in its `git=` stamp line and nowhere else. All three green.

**Two commits sit unpushed on ayr** (78ec1cd the dead-run receipt, 6fb3f39 the
restart script); pushing runs the full gate suite and would steal cores from
the census, so it waits for the run to finish.

## Subgroup census — H15-19 now HAS a second source (2026-08-07)
`results/subgroup-mod4.md`. The orbit-SIZE distribution needs per-SUBGROUP
invariant counts `I(H)` — a different object from the banked per-element
`Fix(g)`, and none were banked. They are lambda^(n/4) families, so 31 min on
gympie buys `a(n) mod 4` at every n <= 40 (a(40) = 3 both ways) by an
algorithm sharing no code path with the column engine.

**The load-bearing result is the height-graded form.** D2ax = {e,h,v,r180} is
exactly the height-preserving subgroup of D4, so `T(n,H) = I_H(D2ax) (mod 2)`
— one bit per triangle CELL, not two per row. **820 cells, 0 mismatches, every cell of the
triangle**, including the 120 cells of H15-19 (previously "none available"
above) and the 190 cells of H22-40 that no later sweep can hold out. Two bits per row / one per cell, not a proof — a wrong a(40)
survives iff its error is 0 mod 4.

A free mod-8 by-product over the banked `Fix(g)` corpus (n <= 32, 0
mismatches) caught its own first version's algebra error, 21 of 33 rows;
both congruences are now in `gate-subgroup` (13 checks, 5 controls).

Idea 1 of `results/unexplored-avenues.md` is marked EXECUTED there, with its
A030222-unstranding payoff STRUCK: Burnside needs per-element `Fix(d)`, the
24h/126GB blocker, which subgroup counts do not supply.

### Per-cell mod 4: BUILT, GATED, DELIBERATELY NOT PUSHED TO n=40
`symtm` grew `--byheight` (hmirror emits "n H W"; r180 emits true height, its
transpose weight split one-at-H one-at-W because the strip label is NOT the
height), plus `--strips` and `--maxwidth`. The refinement
`T(n,H) = I_H(<h>) + I_H(<v>) + I_H(C2) - 2 I_H(D2ax) (mod 4)` is gated at
n<=8 with a control that fails if the height grouping is reused for both
mirrors instead of transposed. **Do not resume the n=40 push** without reading
`results/subgroup-mod4.md` §"why it is NOT being bought": r180's cost peaks on
exactly the H=15..19 band (H=15,19,20,25,30 all past a 120s cap at N=40, while
H=34,38,40 collapse to seconds), `I_H(<v>)` has no bounded-height route short
of a new vmirror sweep mode, and the bit it buys hardens single-cell errors —
the one failure mode this project has never had.

**IN FLIGHT at handoff:** `scripts/percell_mod4.sh 32 8`, tmux window
`percell32` on gympie, driver PID 51511, log
`results/percell_mod4_20260807.log`. Purpose is to check the ALGEBRA at scale
(~500 cells instead of 78), not to reach n=40 — the mod-8 companion shipped
with a wrong coefficient and only banked data caught it. Heartbeat ETA was
drifting 17:27 -> 16:25 as the tall strips cleared; budget ~1h from its 15:39
start. On completion: `results/percell-mod4.md` **does not exist yet and is
already referenced from `results/subgroup-mod4.md`** — write it.

**`make` NOT re-run since the symtm edit.** `gate-subgroup` is GREEN on its
own (17 checks, 7 controls); the full suite was last green at `16236db`. Run a
bare `make` once `percell32` frees the cores.

## Claim-pruning pass 2026-07-31 (cold-eyed bottom-decile review)
jasonp asked for the least novel/interesting/supported claims and an argument
to drop them. Ten items ranked; **1-5 cut, 6-9 rescoped, 10 is jasonp's**.
Each target doc now carries its own scope note; nothing correct was deleted,
because re-deriving a closed door costs an evening and holding it costs a line.
- **Cut:** the 37 digits of the all-pairs constant rho (keep the mechanism:
  boundary-localized eigenvalue => clean constant but no C-finite recurrence);
  the **v5 denominator law** (a fact about the monomial-basis representation of
  an integer-valued polynomial, load-bearing for nothing — retain only
  `k!·P_k ∈ ℤ[n]` + "minimality false"); **nu -> 0.6407** as evidence (0.6757 at
  n=40, 5% off and drifting; theta = -1.000(1) carries universality alone);
  the degree-sequence pattern commentary (`c_H(k+1)` fit, atom-degree "ratio
  2.65"); the W_pair(b) cubic + "degenerate iff 4|b" as results (the numeral
  *correction* 45/69/48 -> 58/114/57 stays, it was load-bearing).
- **Rescoped:** lambda_0 qualitative only (drop "6.94"); component
  stratification keeps the fragmentation statistic, drops "mean = (n+1)/2";
  rook/bishop edge distribution RETIRED (its lever was measured dead);
  **the paper's lambda bracket updated to the certified ladder** (below).
- **Held deliberately, do not cut later:** validation artifacts (gf head-check,
  cone anchor, strip second source) are evidence, not claims; negative results
  are closed doors; well-hedged empirics are already doing their work.
- Filter for future work: before chasing, name the sentence that gets *shorter*
  in the paper if it works. If there isn't one, it is a curiosity.

**paper/polyplets-report.tex lambda bracket UPDATED 2026-07-31**: the stated
rigorous lower bound was 3+2sqrt2 ~ 5.828 (Bacher's directed animals), stale
since the certified strip ladder landed the same day. Now
**6.543 <= lambda <= 9.3154**, both ends machine-checkable in exact arithmetic;
the directed/multi-directed bounds are demoted to a closed-form comparison
remark. sec:gf's "Rigorous lower bounds" paragraph (the GF bound on a(n)) is a
different claim and is unchanged. `paper/technical-report.tex` is jasonp's and
was NOT touched — item 10 (the a(n)/4, a(n)/8 asymptotics reading as a result
rather than as the Burnside triviality they are) is his to reword.

One deviation worth knowing: the "monomial integer coefficients of P_k,
observed k<=17" open item in `docs/proofs/diagonal-law.md` /
`grand-form.md` was measured FALSE (P_k's monomial coefficients have
denominator dividing k! at every wired level; 25^k/k! forces it). It is
replaced by the true statement behind it — **k!·P_k ∈ ℤ[n]**, observed at
all 19 wired levels, load-bearing for `diagCoeffTable`'s representation
and the k!-divide guard — and since proved (Lean `IntCoeff.lean`,
`production_factorial_int`, via integer-valuedness). 2026-07-31 sharpening
(`results/converse-sweep.md`): k! is NOT the minimal denominator — from
k = 5 the true minimum is k!/5 (k!/25 at k = 11 and k = 15..18); only
5-adic content drops. **So quote the divisibility, never the minimality — and
stop there.** The law behind the drop was proved the same day
(`results/v5-denominator-law.md`: the 5-part collapses from v₅(k!) to
v₅(⌊k/2⌋!) because Λ − 1 vanishes to order 2 mod 5) and then **DEMOTED to a
closed door** in the claim-pruning pass above: the minimal denominator is a
property of the *monomial-basis representation* of an integer-valued
polynomial — whose natural (binomial) basis has no denominators at all — and
it is load-bearing nowhere. Proof and Lean statements kept, not extended, not
paper material.

**Holdout-confirmed mass** (new, `results/ns_a40/PROVENANCE.md`): the
share of each term that a closed form predicted first and a later real
sweep then confirmed — a(35) 18.8%, a(36) 13.5%, a(37) 9.1%, a(38) 5.5%,
a(39) 2.5%, **a(40) 0.0%**. Zero at a(40) structurally: its closed-form
cells start at H=22, above every real sweep that will ever exist. Do not
confuse this with strip coverage; they are different quantities.

**COMPLETED on dalby: strip N=40 second-source run.** Launched
2026-07-30, finished same day (~8.6 h, 469 cells, 0 mismatch), log
`results/strip_C14_n40_run.log`. Purpose: the banked strip run stopped at
n=36, so it second-sourced **0%** of a(37)-a(40) by mass. Extending it
to N=40 covers heights H<=14 on those rows — **53.8% / 50.8% / 47.9% /
45.0%** of a(37)/a(38)/a(39)/a(40) respectively. This is the single
highest-value remaining validation action the campaign found, and it is
one command with no new code. When it lands, update
`results/strip-engine.md`'s mass table and
`results/ns_a40/PROVENANCE.md`'s corroboration section.

Still jasonp's, unchanged: the two `paper/technical-report.tex`
placeholders (a(40) appears as 5.7e31 in the abstract and Table `tab:an`
— `verify_technical_report.py` reports exactly those 2 failures out of
781 checks, and nothing else).

## Recently banked
- **a(40) run mechanics (2026-07-25..28, dalby)**: first production
  phased run (Overcommit Hydra design) — phase A H1-19+H22-40
  80c/6.3h, phase B H20-solo 48c/9.6h, phase C H21-solo 32c/36.4h
  (H21 frontier peak 355.4M records, stable ~2.7x per-column over
  H20). Disk peak 363.4GB. One driver incident (missing-checkpoint
  resume at phase C, fixed dd748c4) whose relaunch triggered Zero
  Harvest (above).
- **Fan-In Tax FIXED + branch deployed/validated on dalby (2026-07-23,
  `results/fanin-tax.md`):** the dalby bench A/B exposed ~75% of worker CPU
  going to (units x input-files) open/seek overhead + 256KB-peek reads +
  mmap-threshold buffer churn + byte-at-a-time request getline — none of it
  visible on gympie. Four fixes (orchestrator input pruning [red-first
  test], merge-range record cap, adaptive peek reads, arena-sized buffers +
  POSIX getline): dalby H15/maxn30 bench **336s/20.1k cpu-s → 104.5s/3.9k**
  (3.2x wall, 5.2x cpu), now 1.35x FASTER than the pre-varint D5 baseline.
  Validated: full ns-gates (55) per step + `dalby_term.sh 26` full
  production-shape run on dalby (b-file n≤20 exact, chain exact,
  A26_VALIDATE_PASS). gympie gains ~5% (its pair count was always small).
  **Ladder insight:** a(38)'s intrinsic real H20 sweep yields T(37,20) =
  P_17's first independent holdout AND both P_18 fit points — a(37)-strict
  is subsumed; route = a(37) trusted → a(38) → wire P_18 → a(39) (~a(38)
  cost) → a(40) only if H21's ~280-350GB fits (measure H20 footprint
  during a(38); dalby has 214G free + 68G of banked runs/ clutter).
  **LADDER RUNNING (launched 2026-07-23, jasonp-authorized through a(41)
  contingent on measured disk fit ≥20% headroom):**
  **a(37) BANKED 2026-07-23** = 170463735577007360431441250424
  (results/ns_a37/ + PROVENANCE.md): dalby solo, rev 28e4056c, wall 13048s
  (3.62h), cpu 580k s, rss 395MB, **disk peak 75.7GB measured** (du
  telemetry) → a(38) H20 projection ~160-170GB, fits 281GB free with
  headroom. A37_VALIDATE_PASS (b-file + banked chain), T(37,37)=3^36,
  T(37,36)=P_1(37)·3^33, growth 6.9212 smooth. Real T(37,19) = first P_18
  fit point in hand. One box did all heights one term higher in ~the time
  a(36) needed two boxes in parallel.
  **a(38) BANKED 2026-07-24** = 1180654489101178485738417779914
  (results/ns_a38/ + PROVENANCE.md, commit 0057f2c): dalby solo, 15.8h
  wall / 1.78M cpu-s / 221.5GB disk peak. A38_VALIDATE_PASS; growth
  6.9261. **P_17 INDEPENDENT HOLDOUT PASS** (real T(37,20) == closed
  form). **P_18 WIRED** (fit real T(37,19)+T(38,20), red-first
  diag_p18_test.go). H20 pole reality: frontier 127M (2.8x H19, above
  the x2.15 model), eff_cores ~14 (disk-stall). **H21 raw disk
  projection ~490-620GB FAILS the 281GB gate — the Mirror Toll levers
  are the candidate unlock, calibrated by a(39).**
  **a(39) BANKED 2026-07-25** = 8182864667276277865830132493466
  (results/ns_a39/ + PROVENANCE.md, commit c447f94): FIRST levers-on
  production run — 11.1h wall (vs a(38) 15.8h one term LOWER, 1.42x),
  pole columns 1.5x, disk peak 174.5GB (vs 221.5). A39_VALIDATE_PASS +
  format-change cross-check (re-swept T(38,20) exact). Real T(39,20) =
  first P_19 fit point (second needs a(40)'s H21). 256-frame default
  deployed to dalby post-run (1.72x class ratio).
  **GATE RESOLVED 2026-07-25: jasonp cleaned ~/var+~/tmp** (284GB freed;
  survey + harvest by Claude, deletions authorized explicitly: rf_30008
  fraction-sweep scratch 166GB, tmp/cadoeval 22GB, var/cado/12229_226
  66GB after README-directed harvest to ~/var/cadoeval/groundtruth/,
  30008_259 upload+dup1 36GB; avoid-re-sieve archives kept). dalby now
  565GB free → ceiling 470GB vs a(40) projection 324-412GB — PASSES.
  **a(40) INCIDENT + RELAUNCH 2026-07-25:** the first launch (PID
  2067950) died ~1h in — OOM killer took the ENTIRE tmux server (a(35)
  failure class, 2nd occurrence): the per-round statfs check for
  --fast-map-dir was a TOCTOU race under overlap; N concurrent rounds
  overfilled /dev/shm (tmpfs = RAM). FIXED (commit f9d485f): rounds now
  RESERVE projections under a lock vs a 24GB RAM floor
  (POLY_FASTMAP_FLOOR_GB), red-first TestFastMapReservationRace.
  Collateral: dalby's user ssh-agent died too — github pulls BLOCKED on
  dalby until jasonp re-enters his key passphrase (branch shipped via
  git bundle meanwhile; ref sw-incoming). **a(40) RESUMED (PID 2070278,
  rev f9d485fb, tmux 0:a40 on a fresh tmux server, du monitor 0:a40du);
  effectively a fresh start (~1h lost — overlap checkpoints are
  height-boundary and none had completed).** Top real height H21; real
  T(40,21) = P_19 fit point #2 + P_18's first holdout. Expected ~24-30h
  from resume. On landing: validate → bank → certify P_18 → wire P_19 →
  a(41) per standing authorization.
  Sequence: ~~a(37)~~ → a(38) [real H20 certifies P17 holdout
  T(37,20) + gives both P18 fit points] → wire P18 (derive_pk_fast.py 18,
  dry-run verified, red-first gate like P17) → a(39) → a(40)/a(41) iff
  H21 disk projection fits 281GB free with ≥20% headroom (else stop +
  report). Fallback if a(38) projection >200GB: sweep H20 solo first.
  dalby runs/ cleaned 2026-07-23 (68GB dead checkpoints/torn state;
  telemetry rescued to results/dalby-run-telemetry-202606/, commit
  4faa81a7) → 281GB free.
- **Second Wind (branch `second-wind`, 2026-07-22): a(37) engine-ready.**
  (a) **P_17 WIRED** (diagCoeffTable[17], gated red-first) → a(37) top real
  height H19; fit = T(35,18)+T(36,19), the only two in-onset points;
  **correction**: T(34,17) is n=2k out-of-onset and does NOT lie on P_17
  (sharp onset) — no independent P_17 holdout exists until a real H20 sweep.
  (b) **Block-buffered run-file I/O**: stdio per-FIELD (worst per-varint-BYTE)
  calls were ~90% of worker busy time; fix is format-identical, measured
  **3.36x wall / 3.8x cpu** on the gympie H15/maxn30 bench; full ns-gates +
  fresh a(20) --compare PASS. (c) **--max-diag-k** (gated): forces a wired
  diagonal back to a real sweep — the strict route is `--max-diag-k 16` at
  maxn=37 (real H20 = P_17's first independent holdout). (d) a(37) plan +
  dalby checklist: `results/second-wind.md`. Pending: dalby rebuild + bench A/B (needs
  ssh-agent; jasonp travelling, ayr out of reach — dalby_term.sh is
  dalby-solo anyway). Predicted a(37): trusted ~1.2-2.5h, strict ~2.5-5h.
  **Resume state 2026-07-22:** branch `second-wind` (7 commits off master
  316b5ca) is LOCAL-ONLY on gympie — `git push -u origin second-wind` first
  (needs agent), then the dalby checklist: fetch + checkout +
  `make ns-gates && make install` on dalby, `bench_util.sh` A/B vs the
  140.9s H15/maxn30 baseline to pin the real I/O-win factor, then
  `dalby_term.sh 37` (trusted) or add `--max-diag-k 16` in the script's
  orchestrate line (strict, real H20). Validation already banked on-branch:
  full ns-gates, a(20) --compare, a(26) production-shape chain-match
  (runs/second_wind_a26). The old dalby strip_tm tail-waiter died with the
  network change — expected, its run was already banked.
- **strip C_14 COMPLETE 2026-07-22** (dalby, 7.5h): 413 cells, **0 mismatch —
  columns H≤14 independently confirmed to n=36** (`results/strip_C14_run.log`,
  `results/strip-engine.md`). PinGrand anchors T(26,14)/T(27,14) now
  multi-source; single-algorithm anchor set down to 7 cells (levels 13B–16).
  Hostile-witness audit + full fix list applied same day
  (`docs/lean-hostile-witness.md`): Audit.lean now #guard_msgs-enforced,
  ComputeBridge.lean completes the n≤6 definitional bridge. C_14 footprint
  MEASURED ~38 GB (gympie attempt thrashed, killed) — C_15 ~200+ GB, off table.

Live state only. Completed compute sessions (a(35), Even Keel, the utilization
redesign/deployment passes, the 2026-07-07 M(17)/dmirror/related-seqs jobs, the
terminal-sort investigation) are banked in `results/*.md`, `MEMORY.md`, and git
history — not repeated here. Read this file, then `MEMORY.md`'s index.

## Frontier
- **a(36) = 24629107617723857143962968288** banked+validated, `results/ns_a36/`
  (varint engine, dalby H19 long pole 3.28h). a(1)…a(36) all banked under
  `results/ns_a{n}/`; a(1)-a(20) match the b-file, a(21)+ chain-match each prior term.
- **P17 derivable+validatable** (fit real T(34,17)+T(35,18), holdout real T(36,19));
  wiring it makes a(37)'s top real height H19. **Atom Ledger** banked
  (`results/triangle-structure.md`): triangle dependency structure fully mapped,
  root-separation theorem proves no bounded-depth cross-column relation.
- **a(20) two-algorithm CONFIRMED 2026-07-11** (Redelmeier `build/g2` rev 7eab237 vs
  the TM engine): whole row n≤20 matches banked exactly, 0 mismatches. Banked
  `results/redelmeier_row20/`. Two-algorithm frontier now **20**.
- **a(22) REDELMEIER CONFIRMATION COMPLETE 2026-07-16**
  (results/redelmeier_row22/): fleet run finished cleanly on all three
  boxes (~119h dalby / 116h ayr / 122h gympie, 5% spread — rebalance held);
  all 24,000 shards gathered+combined; **every row n=1..22 matches banked
  exactly** (row 21 = 6954084405510437, row 22 = 47255332844367680).
  **Two-algorithm frontier now 22.** Boxes ALL FREE. Unblocked, jasonp's
  call: a(37) (~3.5h trusted-P17 / ~10h strict) and the H=11 GF
  re-recovery. Run history in results/terminal-velocity.md + provenance.

## Rigorous λ bounds (NEW 2026-07-11)
- **Two-sided rigorous bracket 6.543 ≤ λ ≤ 9.3154**, numerical λ≈7.111 inside.
  Lower (2026-07-31): certified strip ladder — exact Collatz–Wielandt certificates
  μ₂..μ₁₇, μ₁₇ ≥ 6543/1000 (`results/strip-mu-certificates.md`, receipts in
  `results/strip_mu_certificates.log`); supersedes directed/multi-directed
  (3+2√2 exact, 6.475 numerical), which remain the best closed-form/lightweight
  bounds. Upper
  (first ever, ours): Bui-style finite-type convolution certificate, `x=2147/20000`,
  machine-verified in exact rational arithmetic.
- Derivation `docs/proofs/polyplet-upper-bound.md`; certificate `experiments/king_certificate.py`.
  **Certificate Squeeze** (docs/certificate-squeeze-plan.md): P1 (exact cert) + P2 (slack
  audit) done; **P3 not pursued** — the over-count is the connectivity wall (diffuse,
  compounding, non-local), floors this method class above λ. Paper paragraph + `bui2025`
  bib entry landed in `paper/polyplets-report.tex`.

## OEIS submission — gated on jasonp's viva
**Master index + case file: `oeis/SUBMISSION.md`** (2026-07-16; wave structure,
editor-facing argument facts, mechanical checklist, audit trail). Batch staged and
audit-clean (b-files `results/b*_upload.txt` — A006770 to a(40) [promoted
2026-07-29, re-audit owed, see SUBMISSION.md], A030233 to a(34)
[both promoted post-a(22)-confirmation + P_16 holdouts], the four D-dependent to
n=32; a(36)/a(33) staged as conjectured comments). Full pre-submission audit
2026-07-16: every staged term verified against live OEIS + banked data; one
confabulated cross-ref (A337601) caught and fixed. **Submission is jasonp's,
gated on his own readiness process** (OEIS AI policy makes the author personally
responsible; `docs/oeis-ai-policy.md`).
- **Viva** (local-only, git-excluded: docs/viva-exam.md, viva-reserve.md [chmod 000],
  viva-state.md, drill{1,2}-*.md): first exam 56.5/100 vs bar ≥80. Drills 1 & 2 graded;
  cold retake variants (V8/V12/V13, V18/V19/V20) still pending after a spacing gap.
  Full state: docs/viva-state.md.
- Before submit: jasonp rewrites all staged %C in his own words (Claude meaning-checks
  only); signature dates → actual submission day; pink-box replies jasonp's alone.

## Paper (`paper/polyplets-report.tex`)
**UPDATED to the a(40) close 2026-07-29**: title/abstract/tables through
a(40) (twenty-two new terms), tier system reworked (T2 = a(23)-a(38);
T2⁻ = a(39)+a(40), top cells on the never-holdable k=19 diagonal),
by-height table now T(40,H) (peak H=14, injected share 4.1%), growth
fits redone on 40 terms (confluent λ≈7.111 unchanged; series_da.py
re-run on 40 terms: λ=7.1102, θ=-0.9997), validation section carries the
full holdout chain P_15→T(33,18) ... P_18→T(39,21) + the a(40) H21
mass certification + the H20 standalone recheck, cost appendix gains the
a(37)-a(40) ladder table. verify_claims.py retargeted + extended (new
exact 2-point P_k refit/holdout checker): **448/448 GREEN**, compiles
clean. Earlier state below.
Computational-report form, five external review rounds + self-check. Growth §3 confluent
3-param fit (Δ₁=1/2, λ≈7.111). Now includes the rigorous **upper-bound** paragraph
(above). `paper/verify_claims.py` — 397+ checks GREEN (parses tables from the .tex).
Compiles clean (no undefined refs/citations). **FULLY CURRENT as of 2026-07-15**:
second wave landed (sec:universal — lattice-universality of law+spine incl.
w-counterexamples and polyiamond extension; hole-graded diagonal-law paragraph
in sec:holes; deficit-2 proof note in sec:spine; abstract/contributions
updated); verify_claims **412/412** (now runs hex/universal/holefree/
hole-strata/deficit2 checkers). Earlier: **final read-through DONE 2026-07-13**;
now includes the diagonal-law THEOREM (thm:diaglaw), the spine-cubic subsection
(sec:spine), the single-hole max-hole THEOREM (thm:diamond, multi-hole reduced to
peeling as conjecture+open problem), k<=16 corrections, a(36) cost profile.
verify_claims 406/406 (adds: proof checker, ab-initio grand form, (2s+1)^2,
spine digit-product on all in-band cells).

## Open threads
- **Lean proof** (now on master, `polyplets/PROOF-STATUS.md` is authoritative):
  shape theorem + grand form standard-axioms-only; **Grand pin tier extended
  to k ≤ 18 at the a(40) close (2026-07-29)** — triangle.txt reassembled
  n ≤ 40, Pp17/Pp18 + real-swept guards, PinGrand `--kmax 18` (staircase
  oracle 209/209), Audit guards extended; P_19 deliberately NOT formalized
  (fitted-only, no possible holdout, unused in production).
- **Unmerged engine branches — jasonp's call whether/when** (engine work deprioritized
  per the close target): `tm-hotpath-optim` (RunRecord shrink + pmr allocator, real
  4.47% dalby win, gates+ASan clean); `redesign` / kink-sharded (K-shard private-sweep
  kernel, opt-in `--kernel kink-sharded`, real 4.93x at H14/maxn26, still not the default
  and not head-to-head'd at dominant-height scale).
- **steal-tail diagnostic** (`results/steal-tail-h18.md`): banked, not deployed.
- **a(37) READY on branch `second-wind` (2026-07-22, supersedes the 07-12
  shelf costing):** P_17 wired (see Second Wind above; the 07-12 note's "fit
  uses the out-of-onset n=34 point" was wrong — n=34 is off the polynomial,
  sharp onset; fit is T(35,18)+T(36,19), no holdout until H20). Trusted
  route = `dalby_term.sh 37` (~1.2-2.5h predicted post-I/O-fix); strict
  route adds the real H20 sweep (~2.5-5h), which certifies P17, retires
  a(36)'s T2-, and ends the banked range at an odd frontier
  (frontier-parity law). jasonp's call which route; dalby deploy checklist
  in results/second-wind.md.
  **P17-from-the-gas MEASURED DEAD 2026-07-13** (results/defect-gas.md): weight-DP
  cost ~20x/k, k=17 ~10^17s; the strict H20 sweep is the only certification route.
- **Ternary Spine (2026-07-12, BANKED):** the height triangle mod 3 is governed by
  the spine cubic **W³ = W² + t** over 𝔽₃ — digit-product law, first-nonzero-per-
  column ≡ 1, and the **SNF count ⌈(N−1)/3⌉ PROVED** modulo the diagonal law + a
  3-item ladder. `results/ternary-spine.md`, `experiments/ternary_spine.py` (15/15).
  **Ladder RETIRED as empirical input 2026-07-12** by the defect gas (below).
  Open: individual SNF exponents. Candidate paper paragraph — jasonp's call.
- **Defect gas / MASTER EQUATION (2026-07-12, BANKED):** `results/defect-gas.md`,
  `experiments/defect_gas.py` (row model + `master`/`ladder` checks). The diagonal
  law's H is the grand-partition factor of a 1D cluster gas; exact chain identity
  (40/40 vs banked triangle incl. boundaries); master equation
  H = 1 + Σ Ŵ_c u^k H^-(k+ℓ) exact through u³; valuation lemma (k ≥ ℓ) ⟹
  **spine cubic H³=H²+u DERIVED mod 3**, mod-9 lift derived, finite mod-27
  equation matches all 18 coefficients; (⋆a) G≡1 mod 9 derived via boundary
  weights (single-row boundary weight 2s+1 — entry×exit factorization of
  (2s+1)²); **(⋆c) PROVED 2026-07-13** (H(u³) ≡ H²+25u−3u²−3uW mod 9, from the
  mod-9 cubic alone) — the whole ladder is now symbolic, zero empirical input.
  Open: two-row closed form.
  **Deficit-2 law PROVED 2026-07-15** (experiments/deficit2_proof.py):
  T(3m+2,2m+1) == 2 mod 3 for all m, via Lagrange-Buermann diagonal ->
  rational identity on the mod-27 master curve -> exact polynomial division
  (E monic in H, remainder 0). Row-reading picture fully theorem-grade; the
  LB-to-curve-division method is reusable for any linear-family congruence.
  Onset sharpness (general k) attempted, remains OPEN: leading coefficient
  = signed composition of the (non-C-finite) all-pairs family — sign-definite
  after (-1)^k twist on data, no proof.
- **DIAGONAL LAW SHAPE PROVED (2026-07-12):** `docs/proofs/diagonal-law.md`,
  checker `experiments/diagonal_law_proof_check.py` (all green, k ≤ 3 exact).
  Separation lemma (walk rows are cuts) + exact chain identity + row bound
  (ℓ ≤ k) + partial fractions ⟹ T(n,n−k) = P_k(n)·3^{n−1−3k} for n ≥ 2k+1
  with deg P_k ≤ k and **P_k integer-valued** (new, was only observed). Onset
  matches observation exactly. Downstream: Ternary Spine / SNF / P_k machinery
  conditionality collapses to the finitely many enumerated cluster weights.
  Open: onset sharpness for general k (non-cancellation). (Monomial
  integer coefficients: retracted, false at every k ≥ 2 —
  AUDIT-2026-07-30 P8; the true statement is k!·P_k ∈ ℤ[n], proved.)
- **Max-hole theorem M(n)=round((n−2)²/8) — CLOSED 2026-08-06, AND NOT OURS.**
  Both halves are the grid isoperimetric inequality: Sieben 2008 Thm 4.1 is the
  single-hole statement verbatim, and the same minimum for an *arbitrary finite
  subset* of ℤ² — **Wang & Wang 1977**, the primary, with the ℤ² count explicit
  in Altshuler et al. 2006 — applied to the union of all the holes closes the
  multi-hole case in three lines
  (`results/maxhole-proof.md` §The union argument; both PDFs now in `papers/`).
  It ships as a cited corollary plus our n ≤ 17 enumeration; the repo's own
  chain is an independent reproof, kept as a check.
  *Superseded account of the same item, from 2026-07:*
  (`results/maxhole-proof.md`, figs `results/figs/maxhole_{ring,seal}.svg`, checker
  `experiments/maxhole_proof_check.py`). Near-complete proof: construction = diagonal
  diamond ring (done for n≡0 mod 4); upper bound reduced to **one open lemma (II')
  n≥ha+hm+2** (a closed king-curve enclosing an ha×hm diagonal region needs ≥ha+hm+2
  cells). (I') + single-hole reduction + arithmetic in hand; both lemmas verified on
  ~2400 single-hole polyplets (0 violations, tight on diamonds). Partial (II'):
  foreground provably extends 1 step beyond the hole on all 4 sides; the sum (vs max)
  needs a winding/Jordan-curve argument. Also open: clean elongated-diamond family for
  n≢0 mod 4. Jasonp to examine the (II') winding argument. Session-research thread;
  companions this session: [[hole-free-growth-constant]], [[height-distribution-collapse]],
  results/series-analysis-da.md (θ=−1).

- **dm-mirror law PROVED (shape) 2026-07-15** (docs/proofs/dm-diagonal-law.md):
  segment grammar (<=2k+1 perfect diag/anti segments, reversal lemma tight) +
  turn-orbit cost + type finiteness + one-parameter Ehrhart (period 2, coeffs
  {1,2}) + telescoping rank bound => d(S,S+k) per-parity polynomial deg <= k
  past an effective onset; poles only at +-1. NOT proved: sharp onset
  2k+2/2k+3, multiplicity split (k+1,k) — data-grade, like king sharpness.
  Referee pressure point: Lemma 5 (rank/telescoping). Paper updated in 5
  places (abstract/intro/contributions/T3 tier/dmdiag section; T3
  degree-transition failure mode eliminated, onset-shift mode remains,
  bounded); verify_claims 407/407, compiles clean. Program history: `results/dm-diagonal-recon.md`,
  `experiments/dm_sym_enum.py` (validated vs banked law). d(S,S)=2 PROVED
  (permutation skeleton: monotone king permutations). Two-family dichotomy
  refuted (anti-excursion family = the known parity anomaly); proof frame =
  monotone phases + reversal clusters, program steps 1-4 in the recon doc.
  Prize: retires the paper's last conjectural law + the T3 caveat.

- **Kernel/haruspicy/ACSV program (2026-07-14, in flight):** order K2 -> H1 ->
  ACSV -> K1 -> H2 -> K3. K2 DONE (Temperley on column-convex polyplets =
  rediscovery of A187077, pipeline validated; results/convex-polyplets.md).
  H1 DONE + UNCONDITIONALIZATION PUSH 2026-07-15 (results/anisotropic-not-dfinite.md):
  dominant-pole dichotomy theorem (y-D-finite => deg_Q(mu_H) <= D for all but
  r heights); strip growth constants proven strictly monotone (PF route,
  verified exactly H<=10); atoms psi_1..psi_8 CERTIFIED IRREDUCIBLE (degrees
  1..462, multi-prime subset-sum certificates) => deg_Q(mu_H) = atom degree;
  residual conjecture PROVED 2026-07-15 via Northcott finiteness (bounded
  degree + bounded house + infinitude of distinct mu_H = contradiction):
  **THEOREM: the height-anisotropic polyplet GF is NOT D-finite,
  unconditional** — proof template lattice-universal (polyominoes by height
  etc.); literature check flagged in papers/MISSING.md before claiming
  novelty externally. Candidate paper paragraph — jasonp's call. Also: pole-argument theorem
  excludes y-ODEs for the height-anisotropic GF in quantified (order,
  x-degree) boxes (up to r<=5 & D<=28 ... r=0 & D<=3288), from mod-p-certified
  new-root contents psi_H (deg 1..3289, squarefree, lowest terms, H<=10);
  full non-D-finiteness conditional on deg psi -> infinity. H=11 banked GF
  found anomalous (validated=False, shares no roots with Q9Q10) — needs
  re-recovery before any use. ACSV DONE
  (appendix of results/height-distribution-collapse.md): tall-flank rate
  function psi(alpha) = (1-3a)ln3 + Legendre(ln H); saddle reproduces exact
  T(36,36-k) to ~1-3% for k=3..14, breaks at the alpha->1/2 band edge as
  expected; experiments/flank_saddle.py. K1 DONE
  (results/allpairs-kernel.md): gap-walk reformulation exact (l<=8); constant
  **rho ~= 14.41** (37 digits CUT 2026-07-31, claim-pruning pass: the constant
  is ours alone, appears nowhere else, and has no known minimal polynomial, so
  the precision only sharpened an unanswerable question — the CLAIM is the
  mechanism, that growth is a boundary-localized eigenvalue rather than bulk
  spectrum, which is why the family has a clean constant and no C-finite
  recurrence), localized kappa-mode (kappa ~= 0.421, kernel relation verified),
  P-plateau confirmed; algebraic but no low-degree form (PSLQ excludes
  deg<=10, coeffs<=1e10; two spurious fits exposed -- the cautionary half);
  exact elimination documented, NOT to be executed.
  H2 DONE (results/convex-anisotropic.md): convex strip GFs recovered
  exactly H<=7 (orders 1,3,7,14,25,36,53); finding = root RECYCLING (psi
  degrees 1,2,3,5,7,6,8), opposite of the full family's separation -- weak
  exclusion boxes only, Mirage unstrengthened, but sharpens that the H1
  mechanism is special to the unrestricted family. K3 (exact convex mu,
  q-series week-class) PARKED -- last open item of the program. Garnish when idle: Sheffer/Riordan convolution identities for
  P_k as new cross-checks; p=2 spine considered-and-declined (3-powers are
  units mod 2, no collapse).

- **UNIVERSALITY (2026-07-15): the diagonal law holds on the hex lattice**
  (results/hex-diagonal-law.md, experiments/hex_gas.py): T_hex(n,n-k) =
  P_k(n)*2^(n-1-3k), P_1 = 9n-15 (11 holdouts), same onset; single-row
  weights (s+1)^2, gap pairs impossible; **dyadic spine = the SAME cubic
  H^3 = H^2 + u over F_2** with G = 1 + uH^-3. Lattice picks the prime
  (drift count) and density (contacts^2); the curve is invariant. **UNIVERSAL THEOREM
  PROVED 2026-07-15** (docs/proofs/universal-diagonal-law.md): for every
  row-local lattice (|dy|<=1 adjacency, drift count b = |D|), T(H+k,H) =
  q_k(H) b^H from H >= k+1 with integer-valued P_k (Theorem A), and mod any
  prime p | b the spine is H^3 = H^2 + wu with w = W_pair mod p (Theorem B:
  the curve is lattice-invariant; the lattice picks the prime and scaling).
  Instances machine-checked: square b=1 (poly diagonals, density 4,
  experiments/universal_law_check.py), hex b=2, king b=3 -- all with w=1.
  The w question is CLOSED. **Load-bearing half (keep):** the 2026-07-15
  numerals 45, 69, 48 were gap-capped undercounts -- truly **58, 114, 57**
  (`experiments/universal_pair_weights.py`, two independent methods); one of
  them had reached the paper, and the correction also killed the "densities
  are squares" reading (a b<=3 artifact). Theorem B is sharp on two witnesses
  we hold outright: D={-2,0,2} gives w=0 (degenerate branch nonempty), interval
  b=5 gives w=4!=1 (scaling nontrivial). **Demoted 2026-07-31 (claim-pruning
  pass):** the closed form W_pair(b) = b^3 - b(b+1)/2 + 4 and the "degenerate
  iff 4|b" classification are supporting detail, not results -- they describe
  hypothetical interval lattices at b>=4 that nobody enumerates, while the
  three real members (square b=1, hex b=2, king b=3) are all machine-checked.
  Use the cubic to generate witnesses; do not extend the b-family. Open:
  polyiamonds (needs row conventions).
  Paper's not-D-finite theorem landed (thm:notdfinite, verify_claims 407/407).

- **Lessons-learned DRAFTED 2026-07-15** (docs/lessons-learned.md): six failure
  classes, verification war stories, bug bestiary, process/ops/collaboration
  lessons; sections marked [JP] are jasonp's to write.
- **EVERYTHING ELSE BLOCKED OR COMPLETE (2026-07-15).** Blocked on time/boxes:
  a(22) (~07-16; then gather+bank, frontier->22), H=11 GF re-recovery, a(37)
  decision. Blocked on jasonp: viva -> OEIS batch + 3 comment drafts,
  [JP] lessons sections, ~~Northcott literature check~~ **CLOSED
  2026-08-01** (papers/MISSING.md + results/anisotropic-not-dfinite.md:
  criterion traced to BM-R 2002 Lemma 9, not Haruspicy 1; shared opening
  step now cited in the paper; remaining leads swept, no collision;
  D_A-finiteness ceiling recorded; **forward citation crawl DONE 2026-08-01**
  — OpenAlex + Semantic Scholar over BM-R 2002, Haruspicy 2/3,
  Chan-Rechnitzer, BBEP, Bell-Hu-Satriano, BGKL: still no collision, and the
  nearest arithmetic relative found (Bell-Nguyen-Zannier's height/D-finiteness
  series) is now cited in the paper; MathSciNet + Scholar Cited-by remain
  jasonp's optional belt-and-braces), paper scoping sign-off. Blocked on hard math (obstructions documented):
  onset sharpness (king+dm), dm Lemma-5 hardening + multiplicity split,
  max-hole peeling, SNF exponents, K3 exact convex mu, periodic-lattice
  formalization.

## Session 2026-08-01 (pre-publication sweep) — 3 commits, NOT pushed
Master is 56 commits ahead of origin; pushing stays jasonp's call. Today's,
newest first:

- **`5b9e569` two-row weights filed.** The long DP run from the prior session
  landed: eight interior weights W(a,b) — (2,7) (2,8) (3,5) (3,6) (3,7) (4,4)
  (4,5) (5,5), W(5,5) alone 8.4 h — banked in `results/defect-gas.md` with
  costs and in `cluster_weight_dp.py` as `TWO_ROW_INTERIOR`; new CLI
  `cluster_weight_dp.py pair A B` reproduces a cell and self-checks.
  Consequences: the a=2 cubic now has three holdouts; **the a=3 row is the
  quartic 24b⁴+16b³+110b²−19b+16** (holdout W(3,7) exact); and the
  **symmetric-bicubic target is REFUTED** — deg_b W(a,·) = a+1, so no
  fixed-degree bivariate polynomial can be the closed form. Corrected target,
  not a lead. Next cell if ever revived: W(4,6), wants the C++ path.
- **`a5e778e` citation graph crawled** (the standing next action in
  `papers/MISSING.md`, now spent). OpenAlex + Semantic Scholar over BM-R 2002,
  Haruspicy 2/3, Chan-Rechnitzer, BBEP, Bell-Hu-Satriano, BGKL. **No
  collision**; every BM-R descendant proving non-D-finiteness runs on pole
  accumulation. Find: **Bell-Nguyen-Zannier, "D-finiteness, rationality, and
  height"** (Trans. AMS 373 (2020) + parts II/III) — height theory applied to
  D-finite series, nearest arithmetic relative, different configuration
  (coefficient heights ⇒ rationality vs our slice growth constants ⇒
  contradiction). Now cited in the paper's "Relation to existing work"
  alongside Bell-Hu-Satriano, so that paragraph no longer rests on absence
  alone. verify_claims **448/448**, pdflatex clean. Unrun and optional:
  MathSciNet, Google Scholar's own Cited-by.
- **`a621ee2` comb shatter** — the concatenation route to a better λ upper
  bound, priced then closed (`results/concatenation-upper-bound.md`,
  `experiments/concatenation_bound_check.py`). A degree-2 P would have given
  λ ≤ 7.745 (deg 3 → 8.642, deg 4 → nothing), and 40 terms refute no such
  relation; but the lexicographic split shatters a king comb into ~n/4
  components, and the connected (centroid) split can't prescribe halves to
  O(1). The same lemma would beat the polyomino record 4.5252 → 4.3828, so it
  is known-hard. **Bracket unchanged: 6.543 ≤ λ ≤ 9.3154.**

Untracked in the tree and NOT ours to touch: `paper/technical-report.tex`
(+ live `.swp` — jasonp editing).

## Sessions 2026-08-01 (cont.) + 2026-08-02 — paper trim, release flags closed
The section above was saved mid-day (79ac9c7); ~28 commits followed, all
local, NOT pushed. Newest first:

- **2026-08-02: both cuts-log release-integrity flags CLOSED (2cad8f2).**
  (1) `paper/verify_claims.py`'s docstring now names the 18 repo-invariant
  checks it guards beyond the paper and why they stay; (2) new fail-closed
  "sym32 farm manifest" coverage group — S1..S32 all present, every strip
  starts at n=S with contiguous rows, column sums reproduce `dmirror.out`
  on every n. Red-tested on a farm copy with S31 deleted: trips exactly at
  n=31,32, the band the n≤24/28 prefix-matches cannot see. verify_claims
  now **428/428, 0 skipped**.
- **2026-08-02: strip-mu note's false vbits rationale corrected (802277d).**
  The H=17 receipt (vbits=110, vrange_bits=134.8) refutes the note's
  "every rung ran with vbits ≥ vrange" — unattainable at any `--digits`
  (cap = 126 − 6 − log2(10^d), max ~116); the clamped eigenvector tail
  concedes ~0.0035 (6.543 certified vs 6.5464870 float). Bound valid;
  harvest would need ≥192-bit accumulators, not pursued. This was the
  first live finding from the (deleted-at-jasonp's-request) results
  dependency map. The second — λ ≤ 9.3154 is Lean-conditional on the
  named RD=3 hypotheses, unconditional Lean upper bound only 3125/256 —
  needs no fix: PROOF-STATUS.md states it plainly and the paper claims
  only exact-arithmetic checkability (true via the Python certificate).
- **polyplets-report.tex trimmed, two campaigns (2026-08-01).** First wave
  (3d4d6be..d9901d0, 14 commits): abstract rebalanced, one canonical
  telling of the holdout discipline, benchmark appendix / reach section /
  dm apparatus cut, λ bounds state the bound not the rungs, em-dash
  density 76→6, rhetorical closers stripped. Then the remover/defender
  adversarial trim (d1bd54c..218a1ed, 11 commits, six phases):
  1437→1122 lines (−21.9%), verify_claims 448→425 with each check pruned
  in the same commit as its claim, pdflatex + verifier green at every
  stage. **Audit trail: `paper/polyplets-report-cuts.md`** — every cut
  with the winning argument, twelve contested-retained items, standing
  erosion floors (fitted-vs-derived sentence, T2⁻-marking family, T14
  departure marker).
- **Papers sweep closed (d161f3f..967138a, 040815c).** Northcott
  criterion traced to BM-R 2002 Lemma 9; forward citation crawl plus the
  two discriminating Scholar searches return zero collision; six
  lattice-animal papers filed; oh-cluster and implicit-vector threads
  ruled out; **strip frontier is non-crossing** banked as a new fact
  (cdab5fb); holes n≥20 NO-GO recorded (1c30be9).

## Session 2026-08-06 — citations gate, and Proposition 6 made readable
- **Gate CITATIONS added** (`tests/gate_citations.py`, wired first in
  `make gates`). Every repo path cited in a tracked markdown file must exist;
  templates, lines marked deleted/planned, and paths in git history are
  allowed. Written because `results/beyond-polyplets.md` cited a
  `results/cloud-investigation-2026-07-07.md` that has never existed — the name
  belongs to a *memory* entry, not the repo. Six citation fixes landed with it
  (beyond-polyplets, certificate-squeeze-plan Phase 3 deliverables never
  written, sortie-publication-plan's PGO sources, ns_a25 launch script since
  removed, related-seqs-n24's brace-glob path). Full `make`: 16 gates GREEN,
  10m17s.
- **Proposition 6 rewritten for a reader, not a checker.**
  `results/hv-growth-sandwich.md` gains a 215-word notation-free orientation at
  the head of §The proof (fatten / shear / thin; the ends are free, the middle
  has the entropy), and Lemmas 2 and 3 are re-proved in the same register —
  Lemma 2 split explicitly into its bijection half and its counting half with a
  worked transpose (columns `[0,4],[1,3],[2,2]` → row widths `1,2,3,2,1`),
  Lemma 3 gaining the "why that `d` and no other" step and a plainer statement
  of why the seam is recoverable. No claim, bound or measurement changed;
  `make gate-middle-kingdom` GREEN after.
- **Status of the tier-1 gate: still open.** jasonp follows the *sketch* as of
  this session; he has not vetted Lemmas 2 and 3, which is what
  `docs/sortie-publication-plan.md` §3 actually asks for. So the Lean route (P1)
  is not yet demoted to nice-to-have in practice.
- **Lean cost, estimated against the tree (2026-08-06).** Lemma 3 alone ≈400
  lines and no new mathematics — `Polyplets/StairAnimals.lean` already has
  `join_valid`/`cut_join`/`join_injOn`; what is missing is the counting layer
  (`M n` as a cardinality + finiteness, the pattern of `canonicalAnimal_finite`),
  the ceiling `M n ≤ 4^n` for `BddBelow`, and a copy of `Growth.lean`'s
  `a_supermul` → `negLogA_subadditive` → `lambda_tendsto` chain. Lemma 2 ≈600–900
  lines and is real work: mathlib has **nothing** on unimodal compositions
  (`Nat.Partition` and its `Fintype` exist, no cardinality bound), so the
  row-width transpose is built from scratch. All of Proposition 6 ≈3000–4500
  lines, ~60% of it the geometric layer that does not exist yet — HV-convexity
  on `Finset (ℤ × ℤ)` in the `Defs.lean` idiom, Corollary 4, and Lemma 1's phase
  split as a `Finset` injection. For scale: the whole development is 21k lines.
- **Lean route decided: `docs/lean-staircase-growth-brief.md`.** After a
  sceptical pass over four routes, the authorized slice is Lemma 3 + Fekete
  only, ~300 lines — the counting layer on `StairAnimals.lean`, the `4^n`
  ceiling, and Fekete *generalized* out of `Growth.lean:648-730` into a `Fekete`
  structure so `lambda` and `mu` are two instances. Everything else about
  Proposition 6 stays a paper proof: it is elementary, `make
  gate-middle-kingdom` backs it with RED controls, and the full statement is
  2000-3000 lines for a non-central result. Skeleton to start from:
  `polyplets/Draft/Prop6Skeleton.lean` (typechecks, all contracts stubbed).
  Two things the pass corrected: the numeric floor `µ ≥ 3.1234…` is
  *conditional* on the banked `M 700` in any Lean version (the
  `lambda_gt_of_banked` shape), and Corollary 4 is a four-line elementary gap
  argument (`results/middle-kingdom-phase3.md:86`), not the `maxhole`-style
  theory gap first feared.
- **Lean route EXECUTED — Lemma 3 and `µ` are theorems.**
  `polyplets/Polyplets/Fekete.lean` (the ladder, once: supermultiplicative +
  positive + exponential ceiling ⇒ growth, tendsto, `f n ≤ growth^n`) and
  `polyplets/Polyplets/StairGrowth.lean` (`M n` as `Nat.card`, finiteness and
  the `4^n` ceiling from one candidate `Finset`, `M_supermul`, `mu`). 471 new
  lines against the brief's ~300 estimate, and `Growth.lean` gave back 53:
  `lambda` is now `polypletFekete.growth` and its four public names are
  wrappers, with `AuditOutworks.lean`'s pinned footprints unchanged, which is
  what the brief nominated as the refactor's safety net. Guarded and
  standard-three:
  `Stair.M_supermul`, `M_tendsto`, `M_le_mu_pow`, `mu_le`, and the conditional
  `mu_gt_of_banked` — bracket **`3.1234 < µ ≤ 4`**, the floor from the banked
  `M 700`, no native leaf. Out-of-scope per the brief and NOT attempted:
  Lemmas 1 and 2, the geometric layer, the squeeze. `lake build` green, full
  `make` 16 gates green, `PROOF-STATUS.md` + `docs/lean-artifact.md` +
  the build receipt updated (the receipt's old `a(6) = 524` and its
  19/66 guarded split were both wrong; measured 18/70, total 88).
- **Not committed, deliberately:** `paper/technical-report.tex` (jasonp's,
  read-only to Claude) and `paper/technical-report-gaps.md` remain untracked.

## Remaining work ledger
1. **Paper final read-through.**
2. **Viva cold retakes**, then %C authorship pass (jasonp's own words), then jasonp submits.
3. **Lessons-learned document** (jasonp + Claude) — jasonp's explicit ask; after compute
   and paper, BEFORE submitting. The six postmortem failure classes as day-one practices
   are captured in MEMORY.md ([[next-project-practice]]).
4. ~~**Holes n≥20 campaign**~~ **NO-GO, jasonp 2026-08-01.** Closed, not deferred: the
   series ends at n=19 and the hole-free fit uses what is banked. Cost that decided it:
   n=19 is now assembled
   from rescued telemetry (`results/holes_n19.txt`, TIER-DEGRADED: dirty binary stamp).
   Cost scales ×4.2/term off a measured n=19 baseline of 61 h summed per-height wall
   (201 CPU-h) with a 21.6 h critical-path height, so n=20 is ~11 days of summed wall
   and n=22 ~190 days. Cost model + fit impact in
   `results/hole-free-growth-constant.md`.

## Starting a fresh session from here
Read this file, then `MEMORY.md`'s index (auto-loaded) for standing practices. No open
thread needs immediate action; pacing is jasonp's (viva retakes, whether to merge the
unmerged engine branches, whether to revisit a(37)+ compute given the reach ceiling).

**Pre-publication list as of 2026-08-02** — Claude-side items ALL done:
Northcott/citation crawl, concatenation upper bound, the polyplets-report
trim (cuts log = audit trail), both cuts-log release-integrity flags
(sym32 farm manifest + verify_claims docstring, 2cad8f2), and the
strip-mu vbits rationale correction (802277d). verify_claims 428/428.
What is left is the ledger above, and the live items are jasonp's: paper
final read-through (the two `technical-report.tex` placeholders are now
filled — a(40) is literal in both the abstract and `tab:an`, and
`verify_technical_report.py` reports 781 checks, 0 failures), viva cold
retakes → %C authorship pass → OEIS submit, and [JP] lessons-learned
sections. Holes n≥20 is CLOSED no-go. Optional literature
belt-and-braces, also his: MathSciNet Cited-by on BM-R 2002 (the two
discriminating Scholar searches came back zero, 040815c).
