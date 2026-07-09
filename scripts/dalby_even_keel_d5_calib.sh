#!/bin/bash
# D5 (Even Keel) calibration run: small real-swept height to size the timing
# before committing to the fat-height A/B comparison. Not a permanent gate --
# scratch script for the even-keel D5 confirmation session.
set -u
cd ~/src/polyominoes
export GOGC=1000
H=${1:-15}; MAXN=${2:-30}; BASE=${3:-runs/even_keel_d5/new/calib}
rm -rf "$BASE"; mkdir -p "$BASE/spill"
T0=$(date +%s)
./build/ns/orchestrate --maxn "$MAXN" --kernel kink --counter u128 --cores 80 \
  --ram 1073741824 --unit-mult 8 --merge-mult 1 --steal-grain 0.05 \
  --overlap-heights 1 --persistent-workers --heights "$H" \
  --run-dir "$BASE" --spill-dir "$BASE/spill" \
  --checkpoint "$BASE/CK" --checkpoint-every 0 \
  --cost-profile-out "$BASE/cost_profile.tsv" \
  --per-height-out "$BASE/out" 2>&1 | tee "$BASE/log.txt"
RC=${PIPESTATUS[0]}
T1=$(date +%s)
echo "CALIB_DONE rc=$RC wall=$((T1-T0))s"
