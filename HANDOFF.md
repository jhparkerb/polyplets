# HANDOFF — for the next session

_Written 2026-06-22 evening, end of a long autonomous-push session. (The previous HANDOFF.md was
deleted in an earlier cleanup commit 8ed3137; this is a fresh one.)_

## Machines RIGHT NOW — 3 jobs running
- **gympie** (local, `~/src/polyominoes`): **C1 — H=11 fixed-height GF recovery**. 8 `gf_modp`
  workers, ~5h in, 10/11 heights done (H=11 still computing). Appends H=11 to
  `results/fixed_height_gfs.txt` on completion. Load ~8.5 (within the 10 perf-core cap). Payoff:
  extends lifetime-3 + the GF-pole data, adds lambda_11 (sharpens the lambda bracket a touch).
- **dalby** (`~/src/polyominoes`): **D1-at-scale — `scripts/g2_split.sh 16 --maxhole-strat max`**.
  80 g2 workers (full machine), tmux session 0 window `d1strat`. Result -> 
  `runs/gsplit_maxholestrat_N16/combined.txt` (M(n), M_asym(n), M_k(n) to n=16). Heavy n=16 flood.
- **ayr** (`~/polyominoes`): **a(20) CONFIRMATION recount** — `build/tma square8 20 --only-height
  {18,20} --checkpoint runs/a20/ckpt_h{18,20}` (PIDs 995469/996158). Confirms/refutes the candidate
  **a(20) = 1,025,573,519,362,016**. THE gating item for any new reach term.

## Session deliverables (all committed)
### lambda (king-lattice growth constant) — characterized
- Estimate **lambda ~ 7.13** — two NON-converged extrapolations; **[7.12,7.155] is an estimate
  spread, NOT a proven bracket** (see clarification in `results/growth-and-structure.md`).
- **Rigorous interval [6.54, 10.354]** — both ends improved this session:
  - lower 5.99 -> **6.540** (Rands-Welsh concatenation on confirmed n<=19; `experiments/lambda_lower_bound.py`)
  - upper 15.83 -> **10.354** (Eden/twig encoding, independently verified; `experiments/lambda_upper_bound.py`)
- Lit check: **no published king growth constant** (Mertens papers in `papers/` are enumeration-only;
  M-L 1991 only a qualitative "lambda below coordination z=8"). NOT a priority claim — treat as
  "no published value located." Records: `results/growth-and-structure.md`, `lambda-bounds-timeline.md`.
### Reach engine — R1xR3 DEPLOYED + gated (branch `deploy/reach-modp`)
- `cpp/tma_main.cpp`: `--only-height H --modp P --fold` -> `sweepSquare8HeightModP` (~4x less RAM).
- `scripts/an_modp_crt.sh`: per-height fold+modp sweeps over 3 primes -> CRT -> exact a(n).
  **GATED: `an_modp_crt.sh 12 --fold` == A006770 (n<=12).**
- REMAINING: compose **B** (blocked store, `sweep8_blocked.h` on `explore/reach-blocked-store` -> ~8x)
  + parallelize the (H,p) sweeps. The actual reach RUN waits on a(20) confirming (ayr).
### Fresh hunts (research log 2026-06-22)
- **Hole-stratified growth (VERIFY before using)**: hole-free A_0 grows STRICTLY slower — A_0/a
  decays exponentially ~0.978^n -> lambda_0 ~ 6.95 < lambda ~ 7.11. Opposite the square lattice;
  the decay fit is solid but the square-contrast premise needs a double-check.
- **Novel OEIS sequences (submission candidates)**: hole-free count (1,4,20,109,622,3664,...),
  one-hole, square-bounding-box, max-distinct-holes. Confirmed identities: maxhole-area =
  A001971-shifted, max-perim = A001168, min-perim = A027709.
- King site-percolation threshold p_c ~ 0.406 (validation; matches published 0.4071, Malarz-Galam).
### C++ stats engine D1 (branch `explore/cpp-stats-engine`)
- `g2 --maxhole-strat` (M_asym, M_k) + `--contacts`. Settled b2 (M_asym=M(n-1) REFUTED); c=3/4
  refuted (contact density ~0.742). `results/maxhole-stratified.txt`, `contact-density.txt`.

## Branches (unmerged)
- `deploy/reach-modp` — R1xR3 reach engine (gated). **The keeper for reach.**
- `explore/cpp-stats-engine` — g2 stats (b2, c, contacts).
- `explore/reach-blocked-store` — B (blocked store) + Phase-4 OOC, to compose with R1xR3.
- `explore/theorem-lambda-bound` — the old 15.83 upper bound (now superseded by 10.354).

## NEXT SESSION — pick up here
1. **Fold in the 3 jobs** when they land: C1 (H=11 -> lifetime-3 + lambda_11), dalby (M_k to n=16),
   **ayr (a(20) CONFIRMATION — the big one; unblocks new reach terms)**.
2. **Reach engine**: compose B (-> ~8x RAM) + parallelize; then, once a(20) is confirmed, run a(21)
   with the R1xR3(xB) engine.
3. **OEIS**: prep the 4 novel sequences for submission (jasonp pushes the button).
4. **Verify** the hole-free lambda_0 < lambda gap (contradicts the square lattice).
5. (Optional) push the lambda upper bound toward ~8 via the heavy iterated-twig method.

## Standing constraints
- gympie 10 perf-core HARD cap; never pkill/killall (explicit PIDs); long jobs in tmux foreground;
  no orphaned background jobs (left an R2 `tma_rangestat` running 7h this session — killed).
- Claude preps OEIS/paper; jasonp pushes submit. Publishing is jasonp's call.
