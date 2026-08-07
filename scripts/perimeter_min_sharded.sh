#!/usr/bin/env bash
# PURPOSE: run the min-end site-perimeter census ONE FRAME AT A TIME, so that a
#   kill, a crash or a power cut costs one frame instead of the whole run.
#
#   The monolithic `perimeter_min LAT PMAX RMAX` accumulates every frame's tally
#   in memory and prints it only at exit, so it is strictly all-or-nothing: the
#   square8 p=48 run on ayr on 2026-08-07 died at 3.9 h with a 0-byte output
#   file, having dispatched 118 of its 121 frames. Nothing was corrupted; all of
#   it was lost. docs/job-checklist.md item 5 calls that a defect to fix before
#   running the job long, which is what this script is.
#
#   (Dispatched, not completed: the heartbeat's `count` is whichever worker beat
#   last, so it is non-monotonic across 32 threads and is an index into the frame
#   list, never a completion count. 118 is the largest index seen.)
#
#   Frame granularity also fixes the straggler: the frame pool cannot help the
#   single largest frame, but `--only` with --threads shards the removal DFS
#   inside it (cpp/perimeter_min.cpp `shardOneFrame`), so the biggest box gets
#   every core instead of one.
#
# COMMAND:
#   scripts/perimeter_min_sharded.sh LATTICE PMAX RMAX [THREADS]
#   e.g. scripts/perimeter_min_sharded.sh square8 48 6 32
#
# TARGET: any box; sized by THREADS. RAM is a few MB per thread (a <=145-cell
#   box plus a small map), so this is pure CPU -- see the p44 receipt below.
#
# PREDICTED COST (square8 p=48 r=6, from measured runs):
#   p=44 r=6 took 3885 s wall / 16694 cpu-s over 100 frames, 9.3e9 nodes.
#   The dead ayr p=48 run reached 16.6e9 nodes in 14092 s at 32 threads, with
#   frame 118 of 121 dispatched. Node count is super-exponential in PMAX and the
#   last frames are the largest, so budget 5-8 h at 32 threads and treat any
#   figure tighter than that as unmeasured.
#
# RESUME: just re-run the same command. A frame is complete iff its file carries
#   BOTH a '# box' line and the '# perimeter_min lattice=' trailer; complete
#   frames are skipped, anything else is deleted and redone. Output is published
#   by atomic rename from .part, so an interrupted frame can never be mistaken
#   for a finished one. Tested by scripts/perimeter_min_shard_gate.sh.
#
# KILL: read the PID off the `event=start` line in the frame's .log and kill
#   that number; the driver will exit and the frame will be redone on resume.
set -euo pipefail
cd "$(dirname "$0")/.."

LAT=${1:?LATTICE}
PMAX=${2:?PMAX}
RMAX=${3:?RMAX}
T=${4:-${THREADS:-8}}

DIR="results/pmin_${LAT}_p${PMAX}_r${RMAX}.frames"
OUT="results/perimmin_${LAT}_p${PMAX}_r${RMAX}.txt"
mkdir -p "$DIR"

# BSD date has no -Is and BSD sed has no \?; this script has to run on gympie
# (the gate) as well as on the Linux boxes (the census).
stamp () { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
plan_frames () {                # plan.txt -> "W H PARITY" per frame
  awk '/^# box /{ w=h=p="";
                  for (i = 1; i <= NF; i++) { n = index($i, "=");
                    if (n) { k = substr($i, 1, n-1); v = substr($i, n+1);
                             if (k == "W") w = v; else if (k == "H") h = v;
                             else if (k == "parity") p = v } }
                  if (w != "" && h != "" && p != "") print w, h, p }' "$1"
}

complete () {                   # a frame file the merge is allowed to read
  local f=$1
  [ -s "$f" ] \
    && grep -q '^# box ' "$f" \
    && grep -q '^# perimeter_min lattice=' "$f"
}

echo "=== $LAT pmax=$PMAX rmax=$RMAX threads=$T -> $DIR  ($(stamp))"

# 1. The frame plan, MEASURED by the binary rather than derived from a formula:
#    RMAX=0 walks the same box loop and costs one node per frame. Its own
#    `event=plan boxes=N` is the cross-check on the '# box' lines it printed.
./build/perimeter_min "$LAT" "$PMAX" 0 --boxes --threads 1 \
    > "$DIR/plan.txt.part" 2> "$DIR/plan.log"
mv "$DIR/plan.txt.part" "$DIR/plan.txt"
planned=$(sed -n 's/.*event=plan job=perimeter_min boxes=\([0-9]*\).*/\1/p' "$DIR/plan.log" | head -1)
listed=$(grep -c '^# box ' "$DIR/plan.txt")
if [ "$planned" != "$listed" ]; then
  echo "FATAL: plan says boxes=$planned but $listed '# box' lines were printed" >&2
  exit 4
fi
echo "--- plan: $listed frames"

# 2. One --only run per frame. Skip the complete, redo everything else.
done_n=0 skip_n=0 i=0
while read -r W H PAR; do
  i=$((i + 1))
  f="$DIR/f_${W}_${H}_${PAR}.txt"
  if complete "$f"; then
    skip_n=$((skip_n + 1))
    continue
  fi
  # An incomplete frame file is never patched or appended to -- it is removed.
  rm -f "$f" "$f.part"
  echo "--- [$i/$listed] W=$W H=$H parity=$PAR  ($(stamp))"
  ./build/perimeter_min "$LAT" 999 "$RMAX" --only "$W" "$H" "$PAR" --threads "$T" \
      > "$f.part" 2> "${f%.txt}.log"
  # Fail closed: publish only what is provably whole. Without this a binary that
  # exited early on a flushed buffer would leave a short file that looks final.
  if ! { grep -q '^# box ' "$f.part" && grep -q '^# perimeter_min lattice=' "$f.part"; }; then
    echo "FATAL: frame W=$W H=$H parity=$PAR produced an incomplete file; not publishing" >&2
    exit 5
  fi
  mv "$f.part" "$f"
  grep '^# box ' "$f"
  done_n=$((done_n + 1))
done < <(plan_frames "$DIR/plan.txt")

echo "--- frames: $done_n run, $skip_n already complete, $listed total"

# 3. Merge. The merge refuses a missing or mismatched frame, so reaching this
#    line with a written $OUT means the census is whole.
python3 experiments/perimeter_min_merge.py "$DIR" "$LAT" "$PMAX" "$RMAX" > "$OUT.part"
mv "$OUT.part" "$OUT"
echo "--- wrote $OUT ($(grep -vc '^#' "$OUT" || true) rows)"
echo "SHARDED_DONE $LAT pmax=$PMAX rmax=$RMAX $(stamp)"
