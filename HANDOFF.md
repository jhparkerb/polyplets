# HANDOFF — 2026-06-27 ~08:30 EDT

## What's running

### Old engine a(21) — split ayr + dalby, finishing

- **dalby** (80c Neoverse N1): **H20** pid 30478, `tma-a21-H20`, 4 threads / ~6.4 eff cores.
  At ~99.3% col 2 with eta ~14 min reported, but long-window actual rate is ~102 states/s
  (half the instantaneous reading) → true eta likely 30-45 min. H19 already done.
  `runs/a21fold/h20.log` for heartbeat.

- **ayr** (32c x86): **H17** pid 1214013, col 4, ~55%, eta_col ~2h.
  **H18** pid 1213956, col 2, ~92%, eta_col ~1.9h. Both run concurrently (MAXJOBS=2).
  H1–H16 done. `runs/a21fold/h17.log`, `h18.log` for heartbeats.
  Driver: pid 1213926, `scripts/an_fold_parallel.sh 21 2 14`, window `0:a21`.

- **H21 = 3^20 = 3,486,784,401** (closed form, add by hand when combining).
- **ayr partial** (H1–H16): 6,937,832,928,078,101 in `runs/a21fold/a21.partial`.
- **Combine** when all heights done: rsync dalby `runs/a21fold/h*.out` to ayr, sum all h*.out
  cols at n=21 across both, add H21. Gate ratio vs a(20)=1,025,573,519,362,016.

- **Do not restart ayr** — let it finish. True bottleneck is ayr H17 (~2h) not dalby H20.

### dalby telemetry
- Script `scripts/a21_telemetry.sh 30` in tmux `0:telem`, pid 157284.
- CSV: `runs/a21fold/telemetry.csv`. Console: `runs/a21fold/telemetry_console.log`.
- Self-exits after fold ends (MISS_LIMIT=20 consecutive 30s samples with no tma a(21) proc).

### New engine a(21) — armed on dalby, waiting to fire

- Waiter in dalby tmux `0:ns-a21`:
  `tail --pid 30478 -f /dev/null && ... && scripts/dalby_ns_a21.sh`
- When H20 exits: builds from worktree `~/src/polyominoes-ns` (next-system branch at 631636b),
  launches `scripts/dalby_ns_a21.sh` (80 cores, 1 GB RAM/worker, checkpoint every 15 min).
- Run dir: `~/src/polyominoes-ns/runs/ns_a21/`, log: `runs/ns_a21/run.log`.
- **Prediction to verify**: ~8h wall, ~80 GB peak RAM. Basis: a(17)=2274s wall on gympie M1
  @ --cores 4; ×4.4^4 scaling; N1 ≈ 0.75× M1/core; 80 cores. Binding uncertainty: N1/M1 ratio.

## Code state

- **Branch**: `next-system` at `631636b` (pushed to origin).
- **Tag**: `simplified` at `631636b`.
- **All ns-gates green**: arch, math, regression, fold, spill, parallel, resume-boundaries, u128.
- **a(15), a(16), a(17)** cross-checked PASS this session (wall 2m/8.7m/37.9m, scaling ~4.4×).
- **Worktree on dalby**: `~/src/polyominoes-ns` at `cc7268d` (slightly behind; scripts patched
  in-place on dalby — `scripts/dalby_ns_a21.sh` REPO line patched; `dalby_ns_a21_setup.sh`
  not used for the actual launch).
- **gympie** master branch at `8b869c9` (not relevant to next-system work).

## When the new engine a(21) finishes

1. Compare `runs/ns_a21/run.log` triangle output to old engine's combined T(n,H) table.
   The old engine per-height output is in `runs/a21fold/h*.out` on ayr (after combining).
   `--compare` validates n≤18; n=19/20/21 need manual row-by-row check vs old engine.
2. If PASS → **T3.2 closed**. Update fixture `fixtures/b006770.txt` with a(19), a(20), a(21).
3. **T3.3** (a(22) cross-check) requires a(22) from the old engine — that hasn't been run.
   Plan a(22) run per M3.5 sizing in `docs/next-system/IMPLEMENTATION-PLAN.md` (GO on dalby,
   ~5-6 days old engine or new engine at ~2 days once T3.2 is green).

## Prediction record

| run | predicted wall | predicted peak RAM | basis |
|-----|---------------|-------------------|-------|
| new engine a(21) on dalby | ~8h (range 6-12h) | ~80 GB | a(17) measured 2274s @ 4 cores M1; ×375 (4.4^4); N1≈0.75×M1; 80 cores |

Compare actual `wall=` and `rss_max_mb=` from `runs/ns_a21/run.log` event=done line.

## Pending work (ready to start, no compute needed)

- **M5 prep**: `formats.md`, `runcat` tool, `manifest.go` skeleton.
- **T5.4 holes classifier**: `Classifier<holes>` template — same engine, new classifier.
- **HANDOFF update**: this file — done.
