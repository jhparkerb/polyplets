#!/usr/bin/env bash
# n=19 exact hole-count (#28) on DALBY -- the only host with RAM over ayr's 78 GB.
#
# WHY DALBY: exact18 (n=18) peaked 74.6 GB on ayr; n=19 is ~1.7-2x (peak_states
#   x1.73, wider holes stride) => ~120-150 GB raw -- fits nowhere but dalby (125 GiB).
#
# MACHINE: dalby = 80x Ampere Neoverse-N1 (ARMv8.2-A, NO SMT, 1 NUMA), 125 GiB,
#   gcc 15.2 (no clang), Debian. Our TM sweep is memory-bandwidth-bound, so it
#   saturates ~67 of 80 cores -> use --threads 64, not 80.
#
# PREDICTED COST (REFINE WITH STEP 2 BEFORE THE REAL RUN):
#   RAM  ~100-130 GB at the tallest height with --kmax 13 (BORDERLINE on 125 GiB;
#        the benchmark below measures the real peak incl. the doubling-grow spike).
#   TIME ~3-8 h on 64 cores (exact18 was 44 h single-core; MT + bandwidth limit).
#   DISK ckpt file ~50-90 GB under runs/holes_n19_ckpt on / (~376 GB free).
#
# OBSERVABILITY: the binary emits start/heartbeat/done with a self-computed ETA to
#   stderr (the *.log) -- this run is NOT blind.
# RESUME: re-run the identical command; --checkpoint resumes mid-height (cadence
#   TMA_CKPT_SECS, default 1800 s). KILL: kill the tma_holes PID; the ckpt survives.
#
# Run from the repo root on dalby (a ~/polyominoes checkout at the
# obs/MT/reserve/checkpoint commit; `git log -1` should show the checkpoint work).
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root

# 1. Build (gcc on dalby; c++ -> g++ 15.2). Provenance is baked by the Makefile.
#    Optional tuning: append -mcpu=neoverse-n1 (perf only, not required).
echo ">>> build"
make build/tma_holes 2>&1 | tail -1
build/tma_holes 2>&1 | head -1 || true   # usage banner (confirm it runs on this arch)

# 2. BENCHMARK FIRST (job-checklist item 1): measure the n=18 peak RSS with the
#    intended flags, so we know whether n=19 (~1.7-2x) fits 125 GiB BEFORE committing
#    the multi-hour run. Does NOT alter production counts.
echo ">>> benchmark: n=18 holes, --kmax 13 --hdrop, 64 threads (measuring peak RSS)"
mkdir -p runs
/usr/bin/time -v build/tma_holes square8 18 --holes --kmax 13 --hdrop --threads 64 \
    > /dev/null 2> runs/bench_holes_n18.log
grep -E 'Maximum resident|Elapsed \(wall' runs/bench_holes_n18.log
echo ">>> DECIDE: if n=18 peak is well under ~70 GB, n=19 (~1.7-2x) should fit 125"
echo ">>> GiB with headroom. If it's near 70+, n=19 will NOT fit -- needs the"
echo ">>> ranged-row compression (state-store-compression.md, unbuilt) first."

# 3. THE REAL RUN -- uncomment only after step 2 confirms n=19 fits.
#    All-heights sweep (sums to the (n,#holes) distribution). NOTE: do NOT add
#    --reserve here -- on the all-heights sweep it over-allocates the small early
#    heights. The intra-height --checkpoint makes it resumable instead.
# mkdir -p runs/holes_n19_ckpt
# build/tma_holes square8 19 --holes --kmax 13 --hdrop --threads 64 \
#     --checkpoint runs/holes_n19_ckpt \
#     > results/holes_n19.txt 2> runs/holes_n19.log
# echo ">>> done -> results/holes_n19.txt  (validate: per-n sum == A006770 a(19))"
