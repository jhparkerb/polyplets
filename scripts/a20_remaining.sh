#!/usr/bin/env bash
# a(20) cross-ISA reproduction -- REMAINING heights on the NEW MT/checkpoint engine.
#
# CONTEXT: the old a20cross (pre-MT, no checkpoint, --threads 16) was killed mid
#   height-15 (~17h, unprotected) on 2026-06-21. Heights 11-14 are already done
#   (runs/a20/h11-14.out; the new engine's counts are byte-identical to the old --
#   gate_tma checks serial==MT==reserve==resume -- so reusing them is exact). This
#   recomputes heights 15,16,17,18,20 on the new engine to finish ayr's gcc/x86
#   reproduction, then assemble Sum_H byHeight[H][20] and diff vs the candidate
#   a(20) = 1,025,573,519,362,016 to flip RESULTS R4 candidate -> confirmed.
#
# MACHINE: ayr (x86-64, gcc) -- the cross-ISA partner to gympie (clang/ARM). 32 cores,
#   78 GB. --threads 30 (headroom). Heaviest here is h18; h19 peaked ~60 GB so h18
#   fits 78 GB run one-at-a-time. Sequential = one heavy height at a time.
# COST: per-height minutes (small H) to a few hours (h17/h18) on the MT engine --
#   far faster than the old engine's ~17h/height. Checkpointed: a kill costs one
#   cadence (TMA_CKPT_SECS, default 1800s) and resumes by re-running this script.
# OBSERVABILITY: build/tma emits start/heartbeat/done with a self-computed ETA to the
#   per-height runs/a20/h<H>.log -- this run is NOT blind.
# RESUME/KILL: re-run this script; --checkpoint resumes each height mid-sweep. To stop,
#   kill the build/tma PID; the checkpoint under runs/a20/ckpt_h<H> survives.
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root (~/polyominoes on ayr)
mkdir -p runs/a20
for H in 15 16 17 18 20; do
  echo ">>> height $H start $(date -Is)"
  build/tma square8 20 --only-height "$H" --threads 30 --checkpoint "runs/a20/ckpt_h$H" \
      > "runs/a20/h$H.out" 2> "runs/a20/h$H.log"
  echo ">>> height $H DONE: $(cat "runs/a20/h$H.out")  $(date -Is)"
done
echo ">>> remaining heights done. Assemble Sum_H byHeight[H][20] over H=1..20 and diff"
echo ">>> vs 1,025,573,519,362,016 (RESULTS R4)."
