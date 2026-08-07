#!/usr/bin/env bash
# Site-perimeter census for the perimeter-defect grading (docs/perimeter-defect-plan.md).
#
#   scripts/siteperim_grade.sh <lattice> <N> <outfile>
#
# lattice is square4 or square8; the output is the raw "n p count" table that
# experiments/perimeter_defect_fit.py grades by k = pmax(n) - p.
set -euo pipefail

lattice=${1:?lattice (square4|square8)}
n=${2:?N}
out=${3:?output file}

cd "$(dirname "$0")/.."
test -x build/g2 || make build/g2

echo "launch lattice=$lattice N=$n out=$out binary=$(./build/g2 "$lattice" 1 --siteperim 2>&1 | sed -n 's/.*git=\([^ ]*\).*/\1/p' | head -1)"
/usr/bin/time -l ./build/g2 "$lattice" "$n" --siteperim > "$out" 2> "$out.obs.log" || {
  echo "FAILED — full stderr:"; cat "$out.obs.log"; exit 1; }
echo "done rows=$(grep -c '^[0-9]' "$out")"
