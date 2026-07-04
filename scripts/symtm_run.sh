#!/bin/bash
# symtm_run.sh TYPE N [THREADS] -- one symmetric-count production run via
# build/symtm (Hall of Mirrors), e.g. `symtm_run.sh hmirror 34 32` on dalby.
#
# Predicted cost for hmirror N=34 (measured gympie ladder n=24..30, slope
# ~x2.09/term): ~6.7h cpu, wall ~1-1.5h at 32 threads (floored by the
# tallest-strip straggler), peak RSS ~15-25 GB. No resume -- a killed run
# restarts from scratch; kill = explicit numeric kill of the symtm PID.
#
# Run FOREGROUND in a tmux window: heartbeats (stderr) stay on screen and are
# teed to runs/symN/TYPE.err; counts go to runs/symN/TYPE.out.
set -u
cd "$(dirname "$0")/.."
TYPE="${1:?usage: symtm_run.sh TYPE N [THREADS]}"
N="${2:?usage: symtm_run.sh TYPE N [THREADS]}"
THREADS="${3:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)}"
OUT="runs/sym${N}"
mkdir -p "$OUT"
echo "=== symtm $TYPE N=$N threads=$THREADS starting: $(date -Iseconds) ==="
./build/symtm "$TYPE" "$N" "$THREADS" > "$OUT/$TYPE.out" 2> >(tee "$OUT/$TYPE.err")
rc=$?
echo "=== symtm $TYPE N=$N done rc=$rc: $(date -Iseconds) ==="
tail -3 "$OUT/$TYPE.out"
echo "SYMTM_${TYPE}_${N}_DONE rc=$rc"
