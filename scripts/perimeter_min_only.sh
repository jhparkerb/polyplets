#!/usr/bin/env bash
# Run ONE frame of the min-end enumerator and record it.
#
#   scripts/perimeter_min_only.sh W H PARITY RMAX [LATTICE]
#
# --only runs a single frame and the thread pool is over frames, so this is
# single-threaded by construction; --threads would do nothing.  Cost is
# sum_{r<=RMAX} C(cells,r); at RMAX=7 and 145 cells that is ~2.4e11 nodes.
#
# Output: results/perimmin_free_<W>_<H>_<PARITY>_r<RMAX>.txt (+ .log).
set -euo pipefail
cd "$(dirname "$0")/.."

W=${1:?W} H=${2:?H} PAR=${3:?PARITY} RMAX=${4:?RMAX} LAT=${5:-square4}
out="results/perimmin_free_${W}_${H}_${PAR}_r${RMAX}.txt"

echo "=== $LAT W=$W H=$H parity=$PAR rmax=$RMAX -> $out"
./build/perimeter_min "$LAT" 999 "$RMAX" --only "$W" "$H" "$PAR" \
    > "$out" 2> "${out%.txt}.log"
grep '^# box' "$out"
echo "ONLY_DONE W=$W H=$H parity=$PAR rmax=$RMAX"
