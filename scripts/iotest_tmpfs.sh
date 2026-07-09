#!/bin/bash
# One-off measurement: same real height sweep with run/spill on DISK vs TMPFS.
# Decides whether file-I/O is a real share of fat-column wall (gates the
# clean-slate in-process-substrate design in docs/full-utilization-redesign.md).
# Same work both ways; only the run/spill directory location differs.
set -u
cd ~/src/polyominoes
export GOGC=1000
H=${1:-16}; MAXN=${2:-30}

run_one(){
  local label=$1 base=$2
  rm -rf "$base"; mkdir -p "$base/spill"
  local T0 T1 RC
  T0=$(date +%s)
  ./build/ns/orchestrate --maxn "$MAXN" --kernel kink --counter u128 --cores 80 \
    --ram 1073741824 --unit-mult 8 --merge-mult 1 --steal-grain 0.05 \
    --overlap-heights 1 --persistent-workers --heights "$H" \
    --run-dir "$base" --spill-dir "$base/spill" \
    --checkpoint "$base/CK" --checkpoint-every 3000 \
    --cost-profile-out "$base/cp.tsv" > "$base/log" 2>&1
  RC=$?
  T1=$(date +%s)
  if [ "$RC" != 0 ]; then echo "$label FAILED rc=$RC"; tail -5 "$base/log"; return; fi
  awk -v L="$label" -v W=$((T1-T0)) 'NR>2{w+=$5;c+=$6;mx=($3>mx?$3:mx)} END{printf "%-6s realwall=%ds cols_wall=%.1fs cpu=%.1f util=%.1f%% maxfrontier=%d\n", L, W, w, c, 100*c/w/80, mx}' "$base/cp.tsv"
}

echo "=== iotest H$H maxn$MAXN rev=$(git rev-parse --short HEAD) : $(date -Iseconds) ==="
run_one DISK  runs/iotest_disk
run_one TMPFS /dev/shm/iotest_tmpfs
run_one DISK2 runs/iotest_disk2
run_one TMPFS2 /dev/shm/iotest_tmpfs2
rm -rf /dev/shm/iotest_tmpfs /dev/shm/iotest_tmpfs2
echo "=== IOTEST_DONE ==="
