#!/bin/bash
# lean-enumdata-measure.sh OUTDIR : elaborate each of EnumData.lean's five
# kernel checks (L5_eq, L6a_eq .. L6d_eq) alone under lean-guard.sh and
# print wall time and peak RSS for each. Writes one-theorem copies of the
# file into OUTDIR. 2026-10-12 on gympie: 4–5 GB and 8–14 s each.
cd "$(dirname "$0")/../polyplets" || exit 1
DIR=${1:?outdir}; mkdir -p "$DIR"
src=Polyplets/EnumData.lean
end=$(grep -n '^def L6 ' "$src" | cut -d: -f1)
for t in L5_eq L6a_eq L6b_eq L6c_eq L6d_eq; do
  { sed -n "1,${end}p" "$src"; echo; grep "^theorem $t " "$src"; echo; echo "end Polyplets.Enum"; } > "$DIR/$t.lean"
  out=$(../scripts/lean-guard.sh 10 1800 env LEAN_NUM_THREADS=1 nice -n 10 ~/.elan/bin/lake env lean "$DIR/$t.lean" 2>&1 | tail -1)
  echo "$t: $out"
done
