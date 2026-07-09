#!/bin/bash
# Design 14 Phase 3: validate the kink sweep kernel at production scale by
# cell-diffing its per-height T(n,H) output against an EXISTING column-kernel
# reference (banked production per-height — no column re-run), plus a total
# check against the certified a(n). The kink kernel is an INDEPENDENT
# transition implementation (per-cell union-find + NW carry vs the column
# kernel's per-column union-find), so a full cell match is the
# independent-reimplementation closure the a(23) validation plan names
# ([[a23-readiness-and-validation]]).
#
# Usage: kink_validate.sh MAXN COUNTER REFDIR [CERTFILE]
#   REFDIR   : dir of existing column-kernel h<H>.out files (H=1..MAXN)
#   CERTFILE : optional 'n value' file to check the kink total against
#
# dalby: 80 cores, 1 GiB/worker (ram-budget-per-worker: 125GiB*0.6/80 ~ 0.94).
#
# Utilization flags brought up to the dalby_term.sh-validated production
# config (docs/utilization-bottleneck-log.md, results/scheduling.md,
# results/utilization-fix-and-ceiling.md) -- this is a real production-scale
# sweep, not a small gate, so it pays the same fork/GC/merge-fanin/idle-pool
# costs dalby_term.sh was fixed for: unit-mult 4->8, +merge-mult 1,
# +overlap-heights (deliberate overshoot at MAXN, harmless per dalby_term.sh's
# own overlap validation), +persistent-workers, +GOGC=1000.
export GOGC=1000
set -u
cd ~/src/polyominoes

MAXN=$1; COUNTER=$2; REFDIR=$3; CERTFILE=${4:-}
CORES=80; RAM=1073741824

RUN=runs/ns_a${MAXN}_kinkval
KINK=$RUN/kink_ph
rm -rf "$RUN"
mkdir -p "$KINK" "$RUN/kink_run/spill"

echo "=== kink_validate maxn=$MAXN counter=$COUNTER : $(date -Iseconds) ==="
echo "rev: $(git rev-parse --short HEAD)  ref: $REFDIR"

# ── kink kernel run ────────────────────────────────────────────────────────
./build/ns/orchestrate --maxn "$MAXN" --kernel kink --counter "$COUNTER" \
  --cores "$CORES" --ram "$RAM" --unit-mult 8 --merge-mult 1 --steal-grain 0.05 \
  --overlap-heights "$MAXN" --persistent-workers \
  --run-dir "$RUN/kink_run" --spill-dir "$RUN/kink_run/spill" \
  --checkpoint "$RUN/kink_run/POLYCKPT" --checkpoint-every 300 \
  --per-height-out "$KINK" \
  --cost-profile-out "$RUN/kink_run/cost_profile.tsv" \
  2>&1 | tee "$RUN/kink.log"
KRC=${PIPESTATUS[0]}; [ "$KRC" = 0 ] || { echo "KINK_RUN_FAILED rc=$KRC"; exit 3; }

# ── per-cell diff: every T(n,H), kink vs the existing column reference ──────
echo "--- combine --diff-b (every T(n,H) cell) vs $REFDIR ---"
./build/ns/combine --in "$KINK" --diff-b "$REFDIR" --maxn "$MAXN" 2>&1 | tee "$RUN/diff.log"
DRC=${PIPESTATUS[0]}

# ── total-value check against the certified a(n) ───────────────────────────
./build/ns/combine --in "$KINK" --maxn "$MAXN" --out "$RUN/kink_a_n.txt" >/dev/null 2>&1
if [ -n "$CERTFILE" ] && [ -f "$CERTFILE" ]; then
  echo "--- total vs $CERTFILE ---"
  if diff "$RUN/kink_a_n.txt" "$CERTFILE" >/dev/null; then
    echo "TOTAL_MATCH"
  else
    echo "TOTAL_MISMATCH"; diff "$RUN/kink_a_n.txt" "$CERTFILE" | head; DRC=1
  fi
fi

if [ "$DRC" = 0 ]; then
  echo "KINK_VALIDATE_a${MAXN}_PASS"
else
  echo "KINK_VALIDATE_a${MAXN}_FAIL rc=$DRC"
fi
