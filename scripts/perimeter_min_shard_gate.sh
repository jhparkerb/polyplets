#!/usr/bin/env bash
# Gate for scripts/perimeter_min_sharded.sh + experiments/perimeter_min_merge.py.
#
# The sharded driver exists so that a killed run costs one frame, not the whole
# census. That is only worth anything if two things hold, and both are checked
# here rather than argued:
#
#   1. EQUIVALENCE -- the merged per-frame census equals the monolithic run,
#      byte for byte. This is also the real test of the multiplicity trap:
#      `--only` forces mult=1 (cpp/perimeter_min.cpp:465) while the plan carries
#      mult=2 for every W<H frame, so a merge that forgets to reapply it halves
#      most of the table and this check goes red.
#   2. RESUMPTION IS FAIL-CLOSED -- a frame file that is not provably whole is
#      redone, never skipped and never merged. Checked by damaging frame files
#      in each of the ways a kill can leave them.
#
# Both lattices are exercised: square8 has one parity, square4 has two, and the
# parity is part of the frame filename.
#
#   scripts/perimeter_min_shard_gate.sh      # prints GATE PASSED or exits nonzero
set -euo pipefail
cd "$(dirname "$0")/.."

make -s build/perimeter_min

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
fail=0

# The driver writes under results/; point it at a scratch tree so a gate run
# never touches a banked census.
run_sharded () {                # lattice pmax rmax -> stdout of the driver
  local lat=$1 pmax=$2 rmax=$3
  ( cd "$TMP/repo" && ./scripts/perimeter_min_sharded.sh "$lat" "$pmax" "$rmax" 2 )
}

mkdir -p "$TMP/repo/results" "$TMP/repo/scripts" "$TMP/repo/experiments" "$TMP/repo/build"
cp scripts/perimeter_min_sharded.sh "$TMP/repo/scripts/"
cp experiments/perimeter_min_merge.py "$TMP/repo/experiments/"
cp build/perimeter_min "$TMP/repo/build/"

frames_of () { echo "$TMP/repo/results/pmin_$1_p$2_r$3.frames"; }
out_of ()    { echo "$TMP/repo/results/perimmin_$1_p$2_r$3.txt"; }

# ---------------------------------------------------------------- check A/B
# Equivalence against the monolithic run, on both lattices.
for spec in "square8 20 6" "square4 14 6"; do
  set -- $spec
  lat=$1 pmax=$2 rmax=$3
  echo "== $lat pmax=$pmax rmax=$rmax: sharded+merged == monolithic"
  ./build/perimeter_min "$lat" "$pmax" "$rmax" --threads 2 \
      > "$TMP/mono_$lat.txt" 2> "$TMP/mono_$lat.log"
  run_sharded "$lat" "$pmax" "$rmax" > "$TMP/drv_$lat.log" 2>&1 || {
    echo "  driver FAILED"; sed -n '1,20p' "$TMP/drv_$lat.log"; fail=1; continue; }
  if diff -q "$TMP/mono_$lat.txt" "$(out_of $lat $pmax $rmax)" >/dev/null; then
    echo "  identical ($(grep -vc '^#' "$TMP/mono_$lat.txt" || true) rows)"
  else
    echo "  MISMATCH monolithic vs merged:"
    diff "$TMP/mono_$lat.txt" "$(out_of $lat $pmax $rmax)" | head -10
    fail=1
  fi
done

LAT=square8 PMAX=20 RMAX=6
FR=$(frames_of $LAT $PMAX $RMAX)
GOLD=$(out_of $LAT $PMAX $RMAX)
cp "$GOLD" "$TMP/gold.txt"

# ---------------------------------------------------------------- check C
echo "== resume: a finished census re-runs zero frames and is unchanged"
run_sharded $LAT $PMAX $RMAX > "$TMP/resume.log" 2>&1
if grep -q -- "--- frames: 0 run," "$TMP/resume.log"; then
  echo "  0 frames re-run"
else
  echo "  EXPECTED '0 run', got: $(grep -- '--- frames:' "$TMP/resume.log" || true)"; fail=1
fi
diff -q "$TMP/gold.txt" "$GOLD" >/dev/null && echo "  output unchanged" \
  || { echo "  OUTPUT CHANGED on a no-op resume"; fail=1; }

# ---------------------------------------------------------------- check D
# RED: the shape a kill actually leaves -- output flushed up to the '# box'
# line, no trailer. Skipping such a file would merge a truncated frame.
echo "== RED: a frame with no trailer is redone, not trusted"
victim="$FR/f_3_5_-1.txt"
[ -f "$victim" ] || victim=$(ls "$FR"/f_*.txt | tail -1)
grep '^# box ' "$victim" > "$TMP/truncated.txt"
cp "$TMP/truncated.txt" "$victim"
run_sharded $LAT $PMAX $RMAX > "$TMP/red_d.log" 2>&1
if grep -q -- "--- frames: 1 run," "$TMP/red_d.log"; then
  echo "  redone as required"
else
  echo "  NOT REDONE: $(grep -- '--- frames:' "$TMP/red_d.log" || true)"; fail=1
fi
diff -q "$TMP/gold.txt" "$GOLD" >/dev/null && echo "  census restored identically" \
  || { echo "  CENSUS DIFFERS after redo"; fail=1; }

# ---------------------------------------------------------------- check E
echo "== RED: an empty frame file is redone, not trusted"
: > "$victim"
run_sharded $LAT $PMAX $RMAX > "$TMP/red_e.log" 2>&1
grep -q -- "--- frames: 1 run," "$TMP/red_e.log" && echo "  redone as required" \
  || { echo "  NOT REDONE: $(grep -- '--- frames:' "$TMP/red_e.log" || true)"; fail=1; }
diff -q "$TMP/gold.txt" "$GOLD" >/dev/null && echo "  census restored identically" \
  || { echo "  CENSUS DIFFERS after redo"; fail=1; }

# ---------------------------------------------------------------- check F
echo "== RED: the merge refuses a missing frame instead of undercounting"
mv "$victim" "$TMP/held.txt"
if ( cd "$TMP/repo" && python3 experiments/perimeter_min_merge.py \
        "results/pmin_${LAT}_p${PMAX}_r${RMAX}.frames" $LAT $PMAX $RMAX \
        > /dev/null 2> "$TMP/merge_missing.err" ); then
  echo "  MERGE ACCEPTED A MISSING FRAME"; fail=1
else
  echo "  refused: $(head -1 "$TMP/merge_missing.err")"
fi
mv "$TMP/held.txt" "$victim"

# ---------------------------------------------------------------- check G
echo "== RED: the merge refuses a frame that disagrees with the plan"
sed 's/cells=[0-9]*/cells=999/' "$victim" > "$TMP/doctored.txt"
cp "$victim" "$TMP/victim_good.txt"
cp "$TMP/doctored.txt" "$victim"
if ( cd "$TMP/repo" && python3 experiments/perimeter_min_merge.py \
        "results/pmin_${LAT}_p${PMAX}_r${RMAX}.frames" $LAT $PMAX $RMAX \
        > /dev/null 2> "$TMP/merge_bad.err" ); then
  echo "  MERGE ACCEPTED A FRAME THAT IS NOT THE PLANNED ONE"; fail=1
else
  echo "  refused: $(head -1 "$TMP/merge_bad.err")"
fi
cp "$TMP/victim_good.txt" "$victim"

# ---------------------------------------------------------------- check H
# RED control on the control: if the multiplicity were NOT reapplied, check A
# would have to fail. Prove that check A can fail, so its pass means something.
echo "== RED control: dropping the transpose multiplicity must break equivalence"
sed 's/v \* f\["mult"\]/v/' experiments/perimeter_min_merge.py > "$TMP/repo/experiments/nomult.py"
if ( cd "$TMP/repo" && python3 experiments/nomult.py \
        "results/pmin_${LAT}_p${PMAX}_r${RMAX}.frames" $LAT $PMAX $RMAX \
        2>/dev/null | diff -q - "$TMP/gold.txt" >/dev/null ); then
  echo "  RED CONTROL DID NOT FIRE -- mult=1 gives the same census, so check A"
  echo "  is not testing the multiplicity at all"
  fail=1
else
  echo "  fired as expected (mult matters)"
fi

if [ "$fail" = 0 ]; then echo "GATE PASSED"; else echo "GATE FAILED"; exit 1; fi
