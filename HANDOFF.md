# HANDOFF — a(19) confirmed; a(20) candidate, height-19 cross-ISA confirmed; ayr reproducing heights 11–18,20

Polyomino project at `/Users/jasonp/src/polyominoes` (read `ROADMAP.md`,
`method-a19.md`, and `RESULTS.md` first). Subject: fixed polyplets / king-move
animals, OEIS A006770.

## State

**a(19) = 151,609,203,011,580 is confirmed** (RESULTS.md R1, done 2026-06-16) by
two independent algorithms: two decorrelated Redelmeier campaigns (clang/ARM on
gympie + GCC/x86 on ayr, byte-identical results.txt) *and* an
algorithm-independent column transfer-matrix recount (`cpp/tma/`) that assembles
to the same value with n≤18 byte-identical to A006770. method-a19.md and the
b-file (`results/b006770_upload.txt`) reflect this. Nothing left to do on a(19).

## In progress — a(20) single-method candidate (#21)

The transfer-matrix engine is now extending to **a(20)** on **gympie** (local;
this is the gympie-side single-method run — the cross-ISA reproduction is the
remaining confirmation step and needs ayr, busy until ~June 27).

- Per-height jobs write `runs/a20/h<H>.out` (format `"n count"` = byHeight[H][n]).
- **Heights 1–18 and 20 are complete.** Height 20 finished 2026-06-20 06:43
  (`h20.out`: byHeight[20][20] = 1,162,261,467).
- **Height 19 DONE (2026-06-21): cross-ISA byte-match confirmed.** Gympie's
  height-19 recount (`build/tma square8 20 --only-height 19`, PID 85504, ~24.5 h)
  finished: `runs/a20/h19.out` byHeight[19][20] = 19,586,258,055 is **byte-identical
  to ayr's** `runs/a20/h19.ayr.out`. `build/tma` is now rebuilt with the
  obs / MT / `--reserve` / intra-height-checkpoint engine.
- Assemble once h19 and h20 are both non-empty: a(20) = Σ over H=1..20 of
  byHeight[H][20], reading h1..h20.out. Verify n≤18 against `fixtures/b006770.txt`
  and a(19) against the confirmed **151,609,203,011,580**; report any mismatch
  loudly (a low value would indicate an inadmissible size-budget prune).
- **ASSEMBLED 2026-06-20: a(20) = 1,025,573,519,362,016** (candidate). Used ayr's
  height-19 (`runs/a20/h19.ayr.out`, byHeight[19][20]=19,586,258,055) so as not to
  wait on gympie's still-running h19. Checks passed: n≤18 == `fixtures/b006770.txt`,
  a(19) == 151,609,203,011,580, bignum-exact. Recorded RESULTS.md R4 + ledger.
- Independent GF cross-check passed (2026-06-20): `results/fixed_height_gfs.txt`
  (fixed-height GFs H=1..10, recovered on ayr) expands to match the `byHeight[H][n]`
  columns exactly for H=1..10, n≤20.
- Result tier: a(20) is a **candidate** (single method) until an ISA-decorrelated
  rerun on ayr reproduces heights 11–18,20 *and* gympie's own h19 byte-matches
  ayr's. Do not submit until confirmed.

## Notes

- gympie (local, 24 GB) is **busy** with the a(20) height-20 job — do not assume
  it is free, and do not kill or disturb that process.
- ayr (78 GB, no OOM) is busy until ~June 27; dalby off-limits.
- Build with `make build/tma` (needs `-pthread`, C++20).
- jasonp is a Unix veteran — bare commands, no operational hand-holding; don't run
  destructive git/rm commands or kill processes without confirming; for
  background work, rely on completion notifications rather than sleep-polling.
- The discarded variable-width memory experiment is preserved as
  `variable-width-rows.patch` (reverted from the tree; not needed for this run).
