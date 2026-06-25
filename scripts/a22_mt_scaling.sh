#!/usr/bin/env bash
# a22_mt_scaling.sh H [N] -- measure MT wall vs thread count / shard mult for ONE heavy
# height, to pick the fastest config for the a(22) pole sweep (the wall is one sweep, so
# its single-sweep speedup is the whole lever). Run on an OTHERWISE-IDLE dalby for clean
# walls (cpu_s is contention-free but wall is not).
#
# PURPOSE: the production wall = the pole sweep's MT wall. The reach docs claim ~10x on
#   x86; dalby (ARM) measured ~5.5x at T=26. This finds dalby's actual knee for a heavy
#   sweep -- more speedup here = proportionally shorter a(22).
# MACHINE: dalby aarch64 80c.  COST: ~ (serial_cpu_s/5) x (#configs); run on a height
#   whose serial cost is minutes, not hours (start with the climb's largest CLEAN height).
# USAGE: scripts/a22_mt_scaling.sh 15 22   2>&1 | tee runs/a22_forecast/mt_scaling_H15.log
set -u
cd "$(dirname "$0")/.."
H=${1:?height}; N=${2:-22}; P=2147483647
echo "=== MT scaling  H=$H N=$N  $(date -Is)  git=$(git rev-parse --short HEAD) ==="
echo "config            wall_s   cpu_s   speedup_vs_serial  result"
# serial baseline (truth)
base=$(./build/tma square8 $N --only-height $H --modp $P --fold --threads 1 2>&1)
bw=$(echo "$base" | grep -oE "wall_s=[0-9.]+" | head -1 | cut -d= -f2)
bc=$(echo "$base" | grep -oE "cpu_s=[0-9.]+"  | head -1 | cut -d= -f2)
br=$(echo "$base" | grep -oE "result=[0-9]+")
# wall_s is buggy(0) on some paths; time the serial with date instead if needed
echo "serial(t1)        cpu=$bc   $br   (baseline)"
for cfg in "26 32" "26 64" "40 32" "40 64" "52 64" "64 64"; do
  set -- $cfg; T=$1; SM=$2
  t0=$(date +%s.%N)
  out=$(TMA_SHARD_MULT=$SM ./build/tma square8 $N --only-height $H --modp $P --fold --threads $T 2>&1)
  t1=$(date +%s.%N)
  w=$(awk "BEGIN{printf \"%.1f\", $t1-$t0}")
  c=$(echo "$out" | grep -oE "cpu_s=[0-9.]+" | head -1 | cut -d= -f2)
  r=$(echo "$out" | grep -oE "result=[0-9]+")
  sp=$(awk "BEGIN{printf \"%.2f\", $bc/$w}")  # serial cpu_s ~= serial wall; vs MT wall
  ok=ok; [ "$r" != "$br" ] && ok="MISMATCH"
  printf "T=%-3s SM=%-3s     %7s   %6s   %5sx              [%s]\n" "$T" "$SM" "$w" "$c" "$sp" "$ok"
done
echo "=== done $(date -Is) ==="
