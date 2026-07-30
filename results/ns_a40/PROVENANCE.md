# a(40) provenance

a(40) = 56749893611764175164545926946127

Computed 2026-07-25..28 on dalby alone (ARM Ampere Altra, 80 core),
branch `second-wind`, launched 2026-07-25 20:42 EDT via
`FRONTIER_LEVERS=1 scripts/dalby_term.sh 40` — the first production run
of the PHASED driver (Overcommit Hydra, results/overcommit-hydra.md):
maxn=40 with full overlap does not fit 125GB RAM, so the two tall poles
run as solo phases with bounded working sets.

- **Phase A** (H1-19 + H22-40, 80 cores, rev `38956525`): 2026-07-25
  20:42 → 07-26 02:59 EDT, ~6.3h, rss_max 827 MB, cpu 871,963s.
- **Phase B** (H20 solo, 48 cores): 07-26 ~03:00 → ~16:30 EDT, sweep
  cum_wall 34,463.8s (9.6h) across one mid-run interruption + resume,
  rss_max 1023 MB, cpu 1,116,858s.
- **Phase C** (H21 solo, 32 cores, rev `801afd59`): 07-26 21:19 →
  07-28 09:44 EDT, cum_wall 131,071s (36.4h), rss_max 4045 MB, cpu
  3,329,644s. H21 frontier peak 355,390,806 records (cols 6-7), a
  stable ~2.7x per-column cost over H20's profile.
- Disk peak 363.4 GB (du telemetry, banked `rundir_size.log`), hit
  mid-H21 — well above the ~234GB projection gate that had paused the
  ladder at a(39); the H21-solo phasing plus post-a(39) cleanup made it
  fit regardless.
- Real sweeps H3-H21; H22-H40 via wired P_k closed forms (k = 40-H <=
  18). H21 is the tallest real sweep of the whole project.

## Reproduction note (read before re-running)

The original run predates P_19. Since P_19 was wired (`9671e94`, after
a(40) was banked) the k-fence reaches 19, so an unrestricted re-run of
phase C would **inject** H21 from P_19 instead of sweeping it — P_19
being the formula fitted to that very cell. The value is provably
unchanged (the closed-form H21 strip was checked against the real sweep
and matches on all 20 rows), but the run's strongest validation
artifact, the P_0..P_18 mass holdout below, would silently fail to
regenerate.

`scripts/dalby_term.sh` therefore pins `--max-diag-k 18` on all three
phases for N >= 40 (`b2fde69`, AUDIT-2026-07-30 D1). Reproducing this
run at HEAD keeps H21 a real 36.4-hour sweep. Anyone re-running by hand
must pass the same cap; anyone deliberately re-running *without* it gets
the same a(40) but must not describe the result as a holdout.

## Incident: Zero Harvest (and recovery)

The first phase C launch died at t=0: `--resume` was passed for a phase
that had no checkpoint yet (fixed in the driver, commit `dd748c4`, so
resume is per-phase). On the relaunch (07-26 21:16 EDT), the driver
re-entered completed phases A and B in resume mode before starting C.
Phase B resumed from its final checkpoint state (H=20 col=40), found no
work, and on exit RE-HARVESTED `perheight/h20.out` from an empty
in-memory count table — overwriting phase B's output with all-zero rows.
Phase A's resume path (fully-complete sentinel H=-1) skips harvest and
was unaffected; phase C ran fresh and was unaffected.

The engine bug (FIXED post-run, red-first
`orchestrator/zero_harvest_test.go`): the completion-time per-height
write used only the contributions swept by THIS process, while pre-
resume columns' counts live only in the checkpoint's combined triangle.
Resuming a COMPLETED height is the extreme case (no columns left →
all zeros); the red test also proved the silent variant — after ANY
mid-height resume the rewritten h<H>.out under-counts. Phase B itself
had a mid-run interruption + resume, so the h20.out it wrote at
completion was already under-counted BEFORE the zero overwrite; the
checkpoint's count table was always the sole correct copy (its
correctness is what the recovery below and the independent re-sweep
both confirm). Fix: the checkpoint now carries the current height's
partial per-height row (`htri` lines) and resume seeds it; plus
writePerHeight refuses an all-zero row outright (T(H,H)=3^(H-1)>0
makes one impossible for a completed height).

36h later the driver's combine step refused the zeroed shard (fail-
closed: "all counts zero (empty/corrupt shard)") and `set -e` ended the
driver before validation — the guard doing exactly its job.

Recovery: the plain-text checkpoint `POLYCKPT.B` carries the full count
table (`tri n value` lines). All 20 overlapping rows T(20..39,20) match
the independent a(39) run's real H20 sweep digit-for-digit, certifying
the table; T(40,20) = 2359769260803281210360136128699 is the one new
row. `h20.out` was reconstructed from the checkpoint and combine +
validation re-run manually (the driver's exact logic). The zeroed file
is preserved as evidence at `runs/ns_a40/dalby/h20.out.zero-harvest-bug`
on dalby.

**Recheck (2026-07-28..29): a clean H20-only re-sweep
(`scripts/a40_h20_recheck.sh`, fresh run dir + checkpoint, phase B's
exact config, 48 cores, 43,747s sweep wall) reproduced the recovered
`h20.out` byte-for-byte — A40_H20_RECHECK_MATCH. T(40,20) =
2359769260803281210360136128699 is thereby independently re-derived,
and the recovery carries no remaining caveat.**

## Validation

- a(1)..a(20) match `fixtures/b006770.txt` exactly; a(21)..a(39) match
  the banked artifacts (`results/ns_a$n/a_n.txt` where one exists —
  a(23), a(24) — otherwise the banked triangle for that run; n=22's
  independent Redelmeier row lives at
  `results/redelmeier_row22/combined.txt`, and a(25) is carried by
  `results/ns_a25/RESULT.md` + `swept_rows.txt`). A40_VALIDATE_PASS. The
  chain check is now counted rather than asserted: the validate block
  reports its own coverage and fails on a gap (`dbb421a`,
  AUDIT-2026-07-30 P4), and a labeled post-hoc re-run of it over the
  banked artifacts is at `results/ns_a40/validate-2026-07-30.log`
  (`7019ecb`, P5) — **chain coverage: 19/19**, no skips.
- T(40,40) = 3^39 exactly; T(40,39) = 955 * 3^36 with 955 = P_1(40).
- **Mass P_k holdout certification: the real H21 sweep reproduces
  a(39)'s closed-form-injected H21 shard exactly on every row n=21..39
  — independent real-data holdouts for P_0..P_18 in one shot,**
  including P_18's first holdout T(39,21) (previously fit-only).
- H20 cross-run check: T(20..39,20) identical to a(39)'s real sweep
  (also the recovery certification above).
- Growth a(40)/a(39) = 6.9352 (6.9212, 6.9261, 6.9308, 6.9352 — smooth
  approach to lambda ~= 7.11).

## Corroboration by mass

Confidence tiers are usually quoted per *term*; for a(40) the useful
question is what fraction of the 5.67e31 polyplets is corroborated by
something other than the one production sweep that produced it. Shares
are of a(40) itself (recomputed from `perheight/h*.out`, row n=40):

| height band | share of a(40) | independent corroboration |
|---|---|---|
| H1-10 | 7.52% | yes — matches the decorrelated fixed-height GFs expanded to n=40 (355 cells) |
| H11-19 | **81.34%** | **none available** |
| H20 | 4.16% | yes — byte-identical standalone re-sweep (`recheck/h20.out`) |
| H21 | 2.84% | real sweep, but this is P_19's second fit point; no holdout is possible at any n |
| H22-40 | 4.14% | closed forms P_0..P_18, every one with a passed real-swept holdout |

So a(40)'s bulk — four fifths of it — rests on the single kink-carry
production sweep of heights 11-19. That is what the README's T2- grade
means, quantified. Nothing here suggests a wrong value (see Validation
above); it states the denominator honestly.

### Holdout-confirmed mass, a(35)..a(40)

The same accounting applied to the closing terms answers a sharper
question: how much of each term did a *closed form predict first and a
later real sweep then confirm*? Those are the cells in closed-form
territory (k = n-H <= 18, the shipped fence) that the a(40) run's real
sweeps (H <= 21) actually reach:

| term | holdout-confirmed mass |
|---|---|
| a(35) | 18.8% |
| a(36) | 13.5% |
| a(37) | 9.1% |
| a(38) | 5.5% |
| a(39) | 2.5% |
| a(40) | **0.0%** |

It decays to exactly zero at a(40) for a structural reason, not a
sloppy one: a(40)'s closed-form cells start at H=22, above every real
sweep that will ever exist, because the sequence closes here. No later
run can confirm them. This is the T2- grade from the other side — the
same fact as "H21 is P_19's fit point" in the table above.

### Strip second source

The independent strip transfer-matrix engine
(`results/strip-engine.md`) is bounded by its reach. As banked, that run
is H<=14 and **n<=36**, so it touches no cell of rows 37-40: the strip
second-sources **0%** of a(37), a(38), a(39) and a(40). The strip run
extended to N=40 launched 2026-07-30 covers H<=14 at those rows, which
is (recomputed from `perheight/h*.out`) **53.8%** of a(37), **50.8%** of
a(38), **47.9%** of a(39) and **45.0%** of a(40).

## Notes

- Real T(40,21) = 1613457978443478071138613405555 is diagonal k=19's
  second fit point; with a(39)'s T(39,20) both P_19 fit points are now
  real. P_19 can be wired but has NO independent holdout (that would
  need T(41,22) from an a(42)-scale run).
- **Project closes at a(40)** (jasonp, 2026-07-27): a(41) would add
  only the term plus one orphan P_20 fit point; a(42) is the next
  validation seam and out of scope.
