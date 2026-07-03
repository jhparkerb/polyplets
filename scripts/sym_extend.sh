#!/bin/bash
# sym_extend.sh N [THREADS] -- extend the four symmetric fixed-point counts to
# size N via build/symcount_fast (parallel orbit-graph Redelmeier), for the
# related-sequence (A030222/A030233/A030234/A030235/A194596) Burnside
# derivation. r180 is ~100% of the wall (the pole); r90/hmirror/dmirror are
# ~instant. So the three cheap types run single-threaded first (sub-second),
# then r180 takes the full THREADS core budget on its own.
#
# THREADS (arg $2) = threads for the r180 sweep. Default: online CPU count.
# On gympie pass the perf-core budget explicitly (10) — the default counts
# efficiency cores too.
#
# symcount_fast has NO resume -- a killed run restarts that type from scratch.
# Output: runs/symN/{r90,r180,hmirror,dmirror}.out ("n count" lines, sizes 1..N).
set -u
cd "$(dirname "$0")/.."
N="${1:?usage: sym_extend.sh N [THREADS]}"
THREADS="${2:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)}"
OUT="runs/sym${N}"
mkdir -p "$OUT"
echo "=== sym_extend to n=$N (r180 threads=$THREADS) starting: $(date -Iseconds) ==="
pids=""
for t in r90 hmirror dmirror; do
  ( t0=$(date +%s); ./build/symcount_fast "$t" "$N" 1 > "$OUT/$t.out" 2> "$OUT/$t.err"; \
    echo "$t done rc=$? $(($(date +%s)-t0))s $(date -Iseconds)" >> "$OUT/timing.log" ) &
  pids="$pids $!"
done
wait $pids
( t0=$(date +%s); ./build/symcount_fast r180 "$N" "$THREADS" > "$OUT/r180.out" 2> "$OUT/r180.err"; \
  echo "r180 done rc=$? $(($(date +%s)-t0))s $(date -Iseconds)" >> "$OUT/timing.log" )
echo "=== sym_extend to n=$N: all types done: $(date -Iseconds) ==="
cat "$OUT/timing.log"
for t in r90 r180 hmirror dmirror; do echo "$t: $(tail -1 "$OUT/$t.out")"; done
echo "SYM_EXTEND_${N}_DONE"
