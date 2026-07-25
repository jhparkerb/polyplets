# a(39) provenance

a(39) = 8182864667276277865830132493466

Computed 2026-07-24/25 on dalby alone (ARM Ampere Altra, 80 core), engine
rev 0057f2c5 (branch `second-wind`), launched 2026-07-24 ~13:50 EDT via
`FRONTIER_LEVERS=1 scripts/dalby_term.sh 39` — the FIRST production run
with the Mirror Toll disk-IO levers on (block-framed frontier zstd at
64-record frames = 1.45x, plus /dev/shm map-output routing with
per-round headroom fallback; results/fanin-tax.md).

- Real sweeps H3-H20; H21-H39 via wired P_k closed forms (k = 39-H <= 18,
  H21 is P_18's first production use). wall 39957s (11.1h), cpu
  2,070,672s, rss_max 1516 MB.
- Disk peak 174.5 GB (du telemetry; banked rundir_size.log), hit at hour
  ~3 during maximum height co-residency — vs a(38)'s 221.5GB one term
  LOWER. /dev/shm held up to ~42GB of transient map outputs; 189
  fastmap fallbacks routed oversized rounds to disk (the guard working).
- **Lever win at the pole: H20 columns ~3,500s vs a(38)'s ~5,500s at the
  same 127-128M-record frontier (1.5x); whole run 11.1h vs 15.8h one
  term lower (1.42x).**

## Validation

- a(1)..a(20) match fixtures/b006770.txt exactly; a(21), a(26)..a(38)
  match the banked plain-format triangles exactly. A39_VALIDATE_PASS.
- T(39,39) = 3^38 exactly; T(39,38) = 930 * 3^35 with 930 = P_1(39).
- Growth a(39)/a(38) = 6.9308 (6.9212, 6.9261, 6.9308 — smooth).
- **Format-change cross-check: this run's independent H20 re-sweep
  reproduces a(38)'s real T(38,20) = 39207474138446972682720171554
  exactly** — the compressed+tmpfs engine re-derives the plain engine's
  row at 128M-record scale.

## Notes

- Real T(39,20) = 305997488346556404027895440838 sits on diagonal k=19:
  the FIRST of the two P_19 fit points. The second, T(40,21), needs a
  real H21 sweep (a(40)).
- H21 disk gate (a(40)/a(41) authorization: effective peak <= 234GB for
  20% headroom of 281GB free): same-shape projection 174.5GB x 2.2-2.8
  x (1.45/1.72 for the now-default 256-record frames) = ~320-410GB —
  FAILS. H21-solo-first reshaping lands ~200-380GB depending on how much
  map traffic /dev/shm can absorb (62GB cap vs ~90GB+ H21 rounds) — not
  provably under the gate. Ladder STOPS at a(39) pending jasonp.
