#!/usr/bin/env bash
# tri6 hull inventory at p<=30, for experiments/perimeter_min_hex_model.py.
#
# --boxes prints the per-frame breakdown but still runs the full enumeration,
# so this redoes the tri30 census that already landed in
# results/perimmin_tri6_p30_r6.txt.  jasonp approved the redo (2026-08-07)
# rather than adding an inventory-only flag.  ~13 min at 6 threads now that the
# connectivity mask uses ctz.
set -euo pipefail
cd "$(dirname "$0")/.."
out=results/perimmin_tri6_p30_boxes.txt
./build/perimeter_min tri6 30 6 --threads 6 --boxes > "$out" 2> "${out%.txt}.log"
echo "boxes emitted: $(grep -c '^# box' "$out")"
echo "TRI6BOXES_DONE"
