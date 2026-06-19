# HANDOFF — a(19) confirmed; a(20) candidate assembling on gympie

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
- **Heights 1–18 are complete.** Height 20 is **running now**
  (`build/tma square8 20 --only-height 20 --threads 6`, PID 79582).
- **Height 19 is not yet started** — no `h19.out`, no process. It still needs
  to be launched before a(20) can be assembled.
- Assemble once h19 and h20 are both non-empty: a(20) = Σ over H=1..20 of
  byHeight[H][20], reading h1..h20.out. Verify n≤18 against `fixtures/b006770.txt`
  and a(19) against the confirmed **151,609,203,011,580**; report any mismatch
  loudly (a low value would indicate an inadmissible size-budget prune).
- Result tier: a(20) is a **candidate** (single method) until an ISA-decorrelated
  rerun on ayr reproduces it. Do not submit; record in the ledger as candidate.

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
