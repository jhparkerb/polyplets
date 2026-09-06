# a(38) provenance

a(38) = 1180654489101178485738417779914

Computed 2026-07-23/24 on dalby alone (ARM Ampere Altra, 80 core), engine
rev 8ce1bc5c (branch `second-wind`), launched 2026-07-23 ~16:20 EDT via
`scripts/term.sh 38`, foreground in tmux window 0:a38 with tee'd log.

- Real sweeps H3-H20 (first production H20 sweep); H21-H38 via wired P_k
  closed forms (k = 38-H <= 17). wall 56994s (15.8h), cpu 1,783,598s,
  rss_max 971 MB.
- Disk peak 221.5 GB (measured, du telemetry; banked rundir_size.log) —
  above the 160-170GB projection from a(37)'s 75.7GB x2.15/height model.
- H20 pole reality: peak frontier 127.3M records (2.8x H19's 45.3M peak,
  above the x2.15 model), peak columns ~5,500s each, eff_cores ~14 during
  the pole (disk-stall on the saturated NVMe mirror — the Mirror Toll
  measurement, docs/engine-record.md). Work-stealing active in the tail
  (steals ~200+/column). The pre-run 4-8h wall prediction was wrong on
  both frontier growth and per-record cost (x1.6 vs H19).

## Validation

- a(1)..a(20) match fixtures/b006770.txt exactly (full b-file extent).
- a(21), a(26)..a(37) match the banked plain-format triangles exactly.
- A38_VALIDATE_PASS.
- T(38,38) = 3^37 exactly; T(38,37) = 905 * 3^34 with 905 = P_1(38).
- Growth a(38)/a(37) = 6.9261 vs 6.9212 — smooth, monotone toward lambda.
- **P_17 INDEPENDENT HOLDOUT PASS**: this run's real swept T(37,20) =
  4956437442714322066925263218 equals the P_17 closed-form value used by
  the a(37) run exactly. P_17 is now certified by an independent real
  sweep, closing the "no holdout until a real H20" caveat from its wiring.

## Consequences

- P_18 fit points both real: T(37,19) (a(37) run) + T(38,20) (this run)
  → P_18 derived (scripts/derive_pk_fast.py 18: lead 25^18/18!,
  integer-valued) and wired (diagCoeffTable[18], red-first
  diag_p18_test.go). a(39)'s top real height stays H20.
- H21 disk raw projection from the measured 221.5GB x 2.2-2.8 =
  ~490-620GB — FAILS the 281GB-free a(40) gate on the plain format; the
  Mirror Toll levers (frontier zstd + tmpfs map outputs) are the
  candidate unlock, calibrated by a(39)'s telemetry.
