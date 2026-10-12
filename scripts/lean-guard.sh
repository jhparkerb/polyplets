#!/bin/bash
# lean-guard.sh MAX_RSS_GB SECONDS CMD... : run CMD, kill it (and every
# descendant, so `lake env lean` cannot leave an orphaned `lean`) if the
# tree's RSS passes MAX_RSS_GB or it outlives SECONDS. Prints exit status and
# peak RSS.
max_kb=$(( ${1} * 1048576 )); limit=$2; shift 2
"$@" & pid=$!; peak=0; t=0
tree() {  # pid and all descendants
  local all="$1" new="$1"
  while [ -n "$new" ]; do
    new=$(ps -ax -o pid=,ppid= | awk -v ps="$new" 'BEGIN{n=split(ps,a," ");for(i=1;i<=n;i++)p[a[i]]=1} p[$2]{print $1}' | tr '\n' ' ')
    all="$all $new"
  done
  echo $all
}
while kill -0 $pid 2>/dev/null; do
  pids=$(tree $pid)
  rss=$(ps -o rss= -p $(echo $pids | tr ' ' ',') 2>/dev/null | awk '{s+=$1} END{print s+0}')
  [ "$rss" -gt "$peak" ] && peak=$rss
  if [ "$rss" -gt "$max_kb" ]; then kill $pids 2>/dev/null; echo "GUARD: killed, rss ${rss}kB > limit"; fi
  if [ "$t" -ge "$limit" ]; then kill $pids 2>/dev/null; echo "GUARD: killed, ${t}s > limit"; fi
  sleep 2; t=$((t+2))
done
wait $pid; st=$?
echo "GUARD: exit=$st peak_rss=$((peak/1024))MB wall=${t}s"
