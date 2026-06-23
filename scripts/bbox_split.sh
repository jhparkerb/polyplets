#!/usr/bin/env bash
# Parallel square-bounding-box polyplet count via g2 Redelmeier --split. Runs K workers
# (worker IDX owns 1/K of the size-S subtrees; sub-S animals counted by worker 0 only), each
# to its own file, then sums per-box counts -> the w==h diagonal + the full-marginal==A006770
# check. Redelmeier is cache-resident, so K workers are compute-bound (safe to co-run with a
# memory-heavy job on the same box). USAGE: bbox_split.sh N K [splitlevel S=7]
set -uo pipefail
cd "$(dirname "$0")/.."
N="${1:?N}"; K="${2:?K}"; S="${3:-7}"
DIR="runs/bbox_N${N}"; mkdir -p "$DIR"; echo $$ > "$DIR/driver.pid"
rm -f "$DIR"/w*.txt
echo "bbox split: N=$N K=$K splitlevel=$S start=$(date -Is)"
for IDX in $(seq 0 $((K - 1))); do
  build/g2 square8 "$N" --per-box --split "$S" "$K" "$IDX" 2>/dev/null > "$DIR/w${IDX}.txt" &
done
wait
echo "all $K workers done $(date -Is); combining"
python3 scripts/bbox_combine.py "$DIR" "$N" | tee "$DIR/result.txt"
echo "bbox split DONE $(date -Is)"
