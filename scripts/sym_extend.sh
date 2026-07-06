#!/bin/bash
# sym_extend.sh N [THREADS] -- extend the four symmetric fixed-point counts to
# size N via build/symcount_fast (parallel orbit-graph Redelmeier), for the
# related-sequence (A030222/A030233/A030234/A030235/A194596) Burnside
# derivation. All four types parallelize over ROOTS (plentiful at large n), so
# each runs with the full THREADS budget, one at a time (sequential). At the
# frontier (n>=23) hmirror/dmirror are the pole, not r180 — and single-threading
# them (the old behaviour) wasted the box for hours; threaded they scale.
# Sequential-threaded also keeps at most THREADS cores busy at once, which
# respects a per-box perf-core budget (e.g. gympie=10) exactly.
#
# THREADS (arg $2) = threads per type. Default: online CPU count. On gympie pass
# the perf-core budget explicitly (10) — the default counts efficiency cores too.
#
# symcount_fast has NO resume -- a killed run restarts that type from scratch.
# Output: runs/symN/{r90,r180,hmirror,dmirror}.out ("n count" lines, sizes 1..N).
set -u
cd "$(dirname "$0")/.."
N="${1:?usage: sym_extend.sh N [THREADS]}"
THREADS="${2:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)}"
OUT="runs/sym${N}"
mkdir -p "$OUT"
echo "=== sym_extend to n=$N (threads=$THREADS, sequential) starting: $(date -Iseconds) ==="
for t in r90 r180 hmirror dmirror; do
  t0=$(date +%s); ./build/symcount_fast "$t" "$N" "$THREADS" > "$OUT/$t.out" 2> "$OUT/$t.err"
  echo "$t done rc=$? $(($(date +%s)-t0))s $(date -Iseconds)" | tee -a "$OUT/timing.log"
done
echo "=== sym_extend to n=$N: all types done: $(date -Iseconds) ==="
cat "$OUT/timing.log"
for t in r90 r180 hmirror dmirror; do echo "$t: $(tail -1 "$OUT/$t.out")"; done
echo "SYM_EXTEND_${N}_DONE"
