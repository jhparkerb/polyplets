#!/usr/bin/env bash
# PURPOSE: price the k=7 site-perimeter defect census before anyone commits to
#   running it. The k=6 run's own header predicted ~1.8 h wall and the real
#   cost was 42 h (king) / 23 h (square) at 76-way -- a factor of ~23 -- so the
#   n^7.9 single-core model in scripts/dalby_perimeter_defect_pool.sh is
#   REFUTED and must not be reused. This job re-measures it: single-core wall
#   at n = 30, 34, 38, for k = 6 AND k = 7, on both lattices. k=6 is the
#   control -- its three points are on record (254 s, 692 s, 1666 s, king,
#   git=6473890c), so a disagreement means the machine or the binary moved and
#   the k=7 numbers are not comparable to the k=6 run.
#
#   Two things come out: the exponent in n at fixed k, and the cost ratio
#   k=7 : k=6 at fixed n. The census n for k=7 is set by the fit, not by this
#   script: deg D_7 = 22 if Phi_4 enters at k=7 as the exponent rule predicts,
#   so ~44 series coefficients are needed against ~32 for k=6, on an onset of
#   31 against 24.
#
# COMMAND:
#   scripts/dalby_perimeter_defect_k7_calib.sh
#
# TARGET: dalby (80 cores, 125 GB), alongside Confetti (cutcount_b1, 1 core,
#   ~62 GB). This job takes 12 cores and a few MB each, so it fits with room to
#   spare on both counts. NOT ayr -- ayr was unreachable 2026-08-18.
#
# PREDICTED COST: 12 single-core runs in parallel, wall = the slowest one.
#   k=6 n=38 is 1666 s measured. If k=7 costs 3-5x k=6 at fixed n, the slowest
#   run is ~1.5-2.5 h and that is the wall. If it is much worse than that, the
#   answer to "can we afford k=7" is already no.
#
# RESUME/KILL: each cell writes its own result line to a separate file and is
#   skipped if that file already exists, so a re-run resumes. Kill by killing
#   this script's PID; unfinished cells simply have no file.
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=results/perimdefect_k7_calib
mkdir -p "$OUT"

make -s build/perimeter_defect
STAMP=$(./build/perimeter_defect square8 6 2 2>&1 >/dev/null | grep -o 'git=[^ ]*' || true)
case "$STAMP" in
  *dirty*) echo "REFUSING: binary is stamped dirty; commit first"; exit 1;;
esac
echo "=== k=7 calibration  $STAMP  $(date -u +%Y-%m-%dT%H:%M:%SZ)"

run_cell() {
  local lat=$1 n=$2 k=$3
  local f="$OUT/${lat}_n${n}_k${k}.txt"
  [ -s "$f" ] && { echo "skip $lat n=$n k=$k (have it)"; return; }
  local t0 t1
  t0=$(date +%s)
  ./build/perimeter_defect "$lat" "$n" "$k" > "$f.raw" 2> "$f.log"
  t1=$(date +%s)
  printf '%s n=%s k=%s wall_s=%s stamp=%s\n' "$lat" "$n" "$k" "$((t1 - t0))" "$STAMP" > "$f"
  cat "$f"
}
export -f run_cell
export OUT STAMP

for lat in square4 square8; do
  for k in 6 7; do
    for n in 30 34 38; do
      echo "$lat $n $k"
    done
  done
done | xargs -P 12 -n 3 bash -c 'run_cell "$0" "$1" "$2"'

echo "=== done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
grep -h wall_s "$OUT"/*.txt | sort
