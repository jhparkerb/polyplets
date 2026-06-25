#!/usr/bin/env bash
# a22_pole_ladder.sh -- measure the POLE sweep cost vs N.
#
# The a(22) wall = the heaviest single (H,p) sweep. Small-N curves prove peak_states rises
# monotonically to H=N-1, so the pole is H=N-1 (H=N is the free 3^(N-1) closed form). This
# measures the pole sweep B_{N-1}(N) for a ladder of N, giving peak_states(N) and cpu_s(N)
# at the pole -> extrapolate to N=22 (pole = H21).
#
# MACHINE: dalby aarch64 80c. cpu_s is contention-robust (getrusage); wall is timed too but
#   is only clean when the box is otherwise idle. MT threads=40.
# COST: ramps ~2.4x/N. N<=17 seconds-minutes; N18 ~1-2h, N19 ~4h MT (N20 ~10h: optional).
# USAGE: scripts/a22_pole_ladder.sh "15 16 17 18 19"  2>&1 | tee runs/a22_forecast/pole_ladder.log
set -u
cd "$(dirname "$0")/.."
LIST=${1:-"15 16 17 18 19"}
P=2147483647; T=40; SM=32
echo "=== pole ladder (H=N-1)  $(date -Is)  git=$(git rev-parse --short HEAD) T=$T SM=$SM ==="
echo "  N    H=N-1     wall_s     cpu_s   peak_states   states_ratio   result"
prev=0
for N in $LIST; do
  H=$((N-1))
  t0=$(date +%s.%N)
  out=$(TMA_SHARD_MULT=$SM ./build/tma square8 $N --only-height $H --modp $P --fold --threads $T 2>&1)
  t1=$(date +%s.%N)
  w=$(awk "BEGIN{printf \"%.1f\", $t1-$t0}")
  c=$(echo "$out" | grep -oE "cpu_s=[0-9.]+" | head -1 | cut -d= -f2)
  st=$(echo "$out" | grep -oE "peak_states=[0-9]+" | head -1 | cut -d= -f2)
  r=$(echo "$out" | grep -oE "result=[0-9]+")
  ratio=$(awk "BEGIN{if($prev>0)printf \"%.3f\", $st/$prev; else printf \"-\"}")
  printf "%3s   H%-3s   %8s   %8s   %11s   %10s   %s\n" "$N" "$H" "$w" "$c" "$st" "$ratio" "$r"
  prev=$st
done
echo "=== pole ladder done $(date -Is) ==="
