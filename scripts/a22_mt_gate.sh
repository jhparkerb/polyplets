#!/usr/bin/env bash
# a22_mt_gate.sh -- MT-vs-serial correctness gate for the reach mod-p engine.
#
# PURPOSE: before trusting the multithreaded (--threads) path for the a(22) forecast /
#   production run, prove it is byte-identical to the single-thread path per (H,p). A
#   mismatch is a STOP: the MT result would be a silently-wrong a(22). The very top
#   heights (serial = hours) are NOT checked here -- they are validated end-to-end by
#   the N=22 run's CRT diagonal reproducing the KNOWN a(12..20).
# MACHINE: dalby (aarch64, 80c).  Engine: build/tma (current commit, rebuilt fresh).
# COST: ~25 min (slowest serial sweep ~H12@N20 ~16 min).  threads=1 vs threads=24.
# RUN:   scripts/a22_mt_gate.sh 2>&1 | tee runs/a22_forecast/mt_gate.log
set -u
cd "$(dirname "$0")/.."
TMA=./build/tma
P=2147483647
SM=32
mismatch=0
echo "=== MT-vs-serial gate  $(date -Is)  git=$(git rev-parse --short HEAD)$(git diff --quiet || echo -dirty) ==="
gate() {
  local N=$1
  for H in $2; do
    s=$($TMA square8 "$N" --only-height "$H" --modp $P --fold --threads 1  2>&1 | grep -oE 'result=[0-9]+')
    m=$(TMA_SHARD_MULT=$SM $TMA square8 "$N" --only-height "$H" --modp $P --fold --threads 24 2>&1 | grep -oE 'result=[0-9]+')
    if [ "$s" = "$m" ]; then tag=ok; else tag="MISMATCH"; mismatch=1; fi
    echo "N=$N H=$H  serial=$s  mt24=$m  [$tag]"
  done
}
gate 16 "8 9 10 11 12 13 14 15"
gate 18 "10 11 12 13 14"
gate 20 "10 11 12"
echo "=== gate done  $(date -Is)  mismatch=$mismatch ==="
exit $mismatch
