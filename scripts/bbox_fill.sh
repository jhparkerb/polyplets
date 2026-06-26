#!/usr/bin/env bash
# bbox_fill.sh N... -- extend the bounding-box (H,W) triangle B_{H,W}(n) for each given N,
# sequentially, via scripts/bbox_crt.py (CRT over 3 primes, exact). Writes
# results/bbox_polyplets_n{N}_exact.txt per N and logs start/done timestamps so a partial
# overnight run is legible. Each N's table is written before the next N starts, so an
# unfinished tail loses only the in-progress N. Observable (run foreground in a tmux window).
set -u
cd "$(dirname "$0")/.."
mkdir -p runs
echo $$ > runs/bbox_fill.pid
for N in "$@"; do
  echo "=== bbox n=$N START $(date -Is) ==="
  python3 scripts/bbox_crt.py "$N" || { echo "!! bbox n=$N FAILED -- stopping"; exit 1; }
  echo "=== bbox n=$N DONE  $(date -Is) ==="
done
echo "ALL bbox fills done $(date -Is)"
