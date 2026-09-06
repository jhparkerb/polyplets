# a(37) provenance

a(37) = 170463735577007360431441250424

Computed 2026-07-23 on dalby alone (ARM Ampere Altra, 80 core), engine rev
28e4056c (branch `second-wind`: P_17 wired + Fan-In Tax fixes,
docs/engine-record.md), launched 12:05 EDT via `scripts/term.sh 37`,
foreground in tmux window 0:a37 with tee'd log.

- Real sweeps H3-H19; H20-H37 via wired P_k closed forms (k = 37-H <= 17,
  H20 is P_17's first production use). H1-H2 closed-form trivial heights.
- wall 13048.4s (3.62h), cpu 580223s, rss_max 394.6 MB.
- Disk peak 75.7 GB (measured, runs/ns_a37/dalby.rundir_size.log via
  scripts/dalby_du_monitor.sh — first ladder run with du telemetry; banked
  copy rundir_size.log). Calibrates the a(38) H20 projection at ~160-170 GB.
- Single-box comparison: a(36) needed dalby (H19, 11810s) + ayr (H1-18,
  6988s) in parallel; this run did every height one term higher on one box
  in 13048s — the Fan-In Tax fixes' mid-height win in production shape.

## Validation

- a(1)..a(20) match fixtures/b006770.txt exactly (full b-file extent).
- a(21), a(26)..a(36) match the banked plain-format triangles exactly
  (a(22)-a(25) have no plain-format banked file; skipped, as in prior runs).
- A37_VALIDATE_PASS from the term.sh built-in check.
- T(37,37) = 3^36 exactly (king-chain identity T(n,n) = 3^(n-1)).
- T(37,36) = 880 * 3^33 with 880 = 25*37 - 45 = P_1(37) exactly.
- Growth a(37)/a(36) = 6.9212 vs a(36)/a(35) = 6.9157 — smooth, monotone
  toward lambda.

## Notes

T(37,19) (real, height 19) sits on diagonal k=18: it is the FIRST of the
two P_18 fit points. a(38)'s real H20 sweep supplies the second, T(38,20),
plus T(37,20) real — P_17's first independent holdout. Diagonal k=17 ratio
T(37,20)/T(36,19) = 5.19, continuing the smooth declining trend.
