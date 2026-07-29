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

## Incident: Zero Harvest (and recovery)

The first phase C launch died at t=0: `--resume` was passed for a phase
that had no checkpoint yet (fixed in the driver, commit `dd748c4`, so
resume is per-phase). On the relaunch (07-26 21:16 EDT), the driver
re-entered completed phases A and B in resume mode before starting C.
Phase B resumed from its final checkpoint state (H=20 col=40), found no
work, and on exit RE-HARVESTED `perheight/h20.out` from an empty
in-memory count table — overwriting phase B's correct output with
all-zero rows (engine bug, open: resuming an already-completed height
harvests zeros instead of refusing or carrying the checkpointed
counts). Phase A's resume path (fully-complete sentinel H=-1) skips
harvest and was unaffected; phase C ran fresh and was unaffected.

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

- a(1)..a(20) match `fixtures/b006770.txt` exactly; a(21), a(26)..a(39)
  match the banked plain-format triangles exactly (a(22)-a(25) banked in
  triangle form only; their combine values match the recorded terms).
  A40_VALIDATE_PASS.
- T(40,40) = 3^39 exactly; T(40,39) = 955 * 3^36 with 955 = P_1(40).
- **Mass P_k holdout certification: the real H21 sweep reproduces
  a(39)'s closed-form-injected H21 shard exactly on every row n=21..39
  — independent real-data holdouts for P_0..P_18 in one shot,**
  including P_18's first holdout T(39,21) (previously fit-only).
- H20 cross-run check: T(20..39,20) identical to a(39)'s real sweep
  (also the recovery certification above).
- Growth a(40)/a(39) = 6.9352 (6.9212, 6.9261, 6.9308, 6.9352 — smooth
  approach to lambda ~= 7.11).

## Notes

- Real T(40,21) = 1613457978443478071138613405555 is diagonal k=19's
  second fit point; with a(39)'s T(39,20) both P_19 fit points are now
  real. P_19 can be wired but has NO independent holdout (that would
  need T(41,22) from an a(42)-scale run).
- **Project closes at a(40)** (jasonp, 2026-07-27): a(41) would add
  only the term plus one orphan P_20 fit point; a(42) is the next
  validation seam and out of scope.
