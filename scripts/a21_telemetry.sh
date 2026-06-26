#!/usr/bin/env bash
# a21_telemetry.sh [PERIOD_S] -- passive per-(height,column) RAM/CPU sampler for the
# running a(21) fold. NON-INTRUSIVE: reads `ps` + the proctitle (which already carries
# "tma a(21) H## c=col/ncol ~pct%"); never signals or touches the running tma jobs.
#
# WHY: the heartbeat log (runs/a21fold/h##.log) already records per-column src / rate /
# elapsed -- the WORK and THROUGHPUT that idea 04 needs. The one signal it does NOT carry
# is RAM-over-time tagged by height+column, which oq3 (per-height peak RAM) and 04
# (per-column RAM variance) both need. This captures exactly that. Join offline to the
# heartbeat on (height,col): heartbeat gives src/rate, this gives peak rss_kb.
#   awk-join key = (height,col).  oq3 peak RAM(H) = max(rss_kb) over that height.
#
# PERISHABLE: H20 (the pole) is mid-sweep; its per-column RAM curve is gone once it
# finishes, so this must run for the rest of the fold. It self-exits after the fold ends
# (no `tma a(21)` proc seen for MISS_LIMIT consecutive samples) so it never orphans.
#
# CSV: runs/a21fold/telemetry.csv  ->  iso_ts,pid,height,col,ncol,pct,rss_kb,cpu_pct
# Run on dalby in the existing tmux session (foreground-visible). USAGE:
#   scripts/a21_telemetry.sh 30
set -u
cd "$(dirname "$0")/.."
PERIOD="${1:-30}"
MISS_LIMIT=20                       # ~10 min of no-a(21)-procs (at 30s) => fold done, exit
out="runs/a21fold/telemetry.csv"
mkdir -p runs/a21fold
echo $$ > runs/a21fold/telemetry.pid
[ -f "$out" ] || echo "iso_ts,pid,height,col,ncol,pct,rss_kb,cpu_pct" > "$out"
echo "$(date -Is) telemetry up: period=${PERIOD}s -> $out"

miss=0
while :; do
  ts=$(date -Is); n=0
  while read -r pid rss cpu rest; do
    [ -z "${pid:-}" ] && continue
    h=$(printf '%s' "$rest"   | grep -oE 'H[0-9]+'        | head -1 | tr -d H)
    cf=$(printf '%s' "$rest"  | grep -oE 'c=[0-9]+/[0-9]+' | head -1); cf=${cf#c=}
    cc=${cf%/*}; ncol=${cf#*/}
    pct=$(printf '%s' "$rest" | grep -oE '~[0-9]+%'        | head -1 | tr -dc '0-9')
    printf '%s,%s,%s,%s,%s,%s,%s,%s\n' \
      "$ts" "$pid" "${h:-?}" "${cc:-?}" "${ncol:-?}" "${pct:-?}" "$rss" "$cpu" >> "$out"
    n=$((n+1))
  done < <(ps -eo pid=,rss=,%cpu=,args= | grep 'tma a(21)' | grep -v grep)
  if [ "$n" -eq 0 ]; then miss=$((miss+1)); else miss=0; fi
  if [ "$miss" -ge "$MISS_LIMIT" ]; then
    echo "$(date -Is) no a(21) procs x${MISS_LIMIT} -- fold done, telemetry exit"; break
  fi
  sleep "$PERIOD"
done
