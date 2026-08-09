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
— one bit per triangle CELL, not two per row. **820 cells, 0 mismatches,
100% of a(40)'s mass**, including the 120 cells of H15-19 (43.84%, previously
"none available" above) and the 190 cells of H22-40 that no later sweep can
hold out. Two bits per row / one per cell, not a proof — a wrong a(40)
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
