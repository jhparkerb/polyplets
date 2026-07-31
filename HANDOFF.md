# HANDOFF — live state (updated 2026-07-30)

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
  `results/ns_a40/PROVENANCE.md` — H11-19 is 81.3% of the term and has
  no independent corroboration. That is what the T2⁻ grade means.
- the strip second source is scoped honestly (same union-find rule as
  `core/transition.h`; the Python "twin" is a port; coverage is 67.6%
  of cells honestly counted, not 90.7%);
- Lean: the Shape/Peel axiom claims are `#guard_msgs`-enforced, the
  four "outside the default build" statements corrected, a build
  receipt banked.

One deviation worth knowing: the "monomial integer coefficients of P_k,
observed k<=17" open item in `docs/proofs/diagonal-law.md` /
`grand-form.md` was measured FALSE (P_k's monomial coefficients have
denominator dividing k! at every wired level; 25^k/k! forces it). It is
replaced by the true statement behind it — **k!·P_k ∈ ℤ[n]**, observed at
all 19 wired levels, load-bearing for `diagCoeffTable`'s representation
and the k!-divide guard, and not proved.

**Holdout-confirmed mass** (new, `results/ns_a40/PROVENANCE.md`): the
share of each term that a closed form predicted first and a later real
sweep then confirmed — a(35) 18.8%, a(36) 13.5%, a(37) 9.1%, a(38) 5.5%,
a(39) 2.5%, **a(40) 0.0%**. Zero at a(40) structurally: its closed-form
cells start at H=22, above every real sweep that will ever exist. Do not
confuse this with strip coverage; they are different quantities.

**IN PROGRESS on dalby: strip N=40 second-source run.** Launched
2026-07-30, tmux window `strip40`, ~8.3 h predicted, log
`results/strip_C14_n40_run.log`. Purpose: the banked strip run stops at
n=36, so it second-sources **0%** of a(37)-a(40) by mass. Extending it
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
- **Two-sided rigorous bracket 5.828 ≤ λ ≤ 9.3153**, numerical λ≈7.111 inside.
  Lower: directed/multi-directed king animals (3+2√2 exact, 6.475 Bacher). Upper
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
  Open: onset sharpness for general k (non-cancellation); monomial integer
  coefficients of P_k (values proved, coefficients observed).
- **Max-hole theorem M(n)=round((n−2)²/8) — STAGED for later examination**
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
  rho = 14.40871398627036583814804007788... (37 digits), localized kappa-mode
  (kappa=0.42109, kernel relation verified), P-plateau confirmed; algebraic
  but no low-degree form (PSLQ excludes deg<=10, coeffs<=1e10; two spurious
  fits exposed); exact elimination documented, not executed (low value).
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
  Open: is w always a unit (or ever 0)? polyiamonds (needs row conventions).
  Paper's not-D-finite theorem landed (thm:notdfinite, verify_claims 407/407).

- **Lessons-learned DRAFTED 2026-07-15** (docs/lessons-learned.md): six failure
  classes, verification war stories, bug bestiary, process/ops/collaboration
  lessons; sections marked [JP] are jasonp's to write.
- **EVERYTHING ELSE BLOCKED OR COMPLETE (2026-07-15).** Blocked on time/boxes:
  a(22) (~07-16; then gather+bank, frontier->22), H=11 GF re-recovery, a(37)
  decision. Blocked on jasonp: viva -> OEIS batch + 3 comment drafts,
  [JP] lessons sections, Northcott literature check (papers/MISSING.md),
  paper scoping sign-off. Blocked on hard math (obstructions documented):
  onset sharpness (king+dm), dm Lemma-5 hardening + multiplicity split,
  max-hole peeling, SNF exponents, K3 exact convex mu, periodic-lattice
  formalization.

## Remaining work ledger
1. **Paper final read-through.**
2. **Viva cold retakes**, then %C authorship pass (jasonp's own words), then jasonp submits.
3. **Lessons-learned document** (jasonp + Claude) — jasonp's explicit ask; after compute
   and paper, BEFORE submitting. The six postmortem failure classes as day-one practices
   are captured in MEMORY.md ([[next-project-practice]]).
4. **Holes n≥20 campaign — measured not-cheap, jasonp's call.** n=19 is now assembled
   from rescued telemetry (`results/holes_n19.txt`, TIER-DEGRADED: dirty binary stamp).
   Cost scales ×4.2/term off a measured n=19 baseline of 61 h summed per-height wall
   (201 CPU-h) with a 21.6 h critical-path height, so n=20 is ~11 days of summed wall
   and n=22 ~190 days. Cost model + fit impact in
   `results/hole-free-growth-constant.md`.

## Starting a fresh session from here
Read this file, then `MEMORY.md`'s index (auto-loaded) for standing practices. No open
thread needs immediate action; pacing is jasonp's (viva retakes, whether to merge the
unmerged engine branches, whether to revisit a(37)+ compute given the reach ceiling).
