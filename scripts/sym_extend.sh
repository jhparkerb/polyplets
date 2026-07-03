#!/bin/bash
# sym_extend.sh N -- extend the four symmetric fixed-point counts to size N via
# build/symcount_fast (orbit-graph Redelmeier), for the related-sequence
# (A030222/A030233/A030234/A030235/A194596) Burnside derivation. Runs the 4
# types in PARALLEL (4 cores, within gympie's perf-core budget). r180 is the
# pole (~2.6x/term; n=22 ~6h); r90 is trivial.
#
# symcount_fast has NO resume -- a killed run restarts that type from scratch.
# Output: runs/symN/{r90,r180,hmirror,dmirror}.out ("n count" lines, sizes 1..N).
set -u
cd "$(dirname "$0")/.."
N="${1:?usage: sym_extend.sh N}"
OUT="runs/sym${N}"
mkdir -p "$OUT"
echo "=== sym_extend to n=$N starting: $(date -Iseconds) ==="
pids=""
for t in r90 r180 hmirror dmirror; do
  ( t0=$(date +%s); ./build/symcount_fast "$t" "$N" > "$OUT/$t.out" 2> "$OUT/$t.err"; \
    echo "$t done rc=$? $(($(date +%s)-t0))s $(date -Iseconds)" >> "$OUT/timing.log" ) &
  pids="$pids $!"
done
wait $pids
echo "=== sym_extend to n=$N: all types done: $(date -Iseconds) ==="
cat "$OUT/timing.log"
for t in r90 r180 hmirror dmirror; do echo "$t: $(tail -1 "$OUT/$t.out")"; done
echo "SYM_EXTEND_${N}_DONE"
