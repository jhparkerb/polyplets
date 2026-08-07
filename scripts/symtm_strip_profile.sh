#!/bin/bash
# Per-strip cost profile for symtm at N=40, to decide what the per-cell mod-4
# congruence can actually reach.
#
# PURPOSE: `T(n,H) = I_H(<h>) + I_H(<v>) + I_H(C2) - 2 I_H(D2ax) (mod 4)` needs
# three symtm-scale inputs. Two are bounded-height sweeps (strip H only). The
# third, I_H(<v>), goes via transposition to h-symmetric animals of WIDTH H and
# UNBOUNDED height -- i.e. every strip -- so its cost is set by the tall
# strips. This measures one strip at a time to say where the wall is instead of
# guessing at it.
#
# COMMAND:  bash scripts/symtm_strip_profile.sh [N] [THREADS]   (default 40, 8)
# MACHINE:  gympie, laptop-scale by construction (one strip at a time).
# COST:     unknown -- that is the point. Each strip is timed with a hard
#           `timeout`, so a strip that blows past the cap is recorded as ">cap"
#           and the profile continues instead of hanging.
# KILL:     kill the numeric PID of the symtm child; rerun to redo all of it.
set -uo pipefail
cd "$(dirname "$0")/.."

N=${1:-40}
THREADS=${2:-8}
CAP=${3:-120}          # seconds per strip before it is called too expensive
BIN=build/symtm
OUT=results/symtm_strip_profile_n$N.txt

[ -x "$BIN" ] || { echo "missing $BIN (run: make build/symtm)" >&2; exit 1; }

{
  echo "# symtm per-strip wall seconds at N=$N, $THREADS threads, cap ${CAP}s"
  echo "# git=$(git rev-parse --short HEAD) host=$(hostname) date=$(date -Iseconds)"
  echo "# mode H seconds"
} > "$OUT"

for mode in hmirror r180; do
  for H in 5 10 15 19 20 25 30 34 38 40; do
    [ "$H" -gt "$N" ] && continue
    s=$(date +%s)
    if timeout "$CAP" "$BIN" "$mode" "$N" "$THREADS" --strips "$H" "$H" \
        > /dev/null 2>&1; then
      e=$(date +%s)
      printf "%s %d %d\n" "$mode" "$H" "$((e - s))" | tee -a "$OUT"
    else
      printf "%s %d >%s\n" "$mode" "$H" "$CAP" | tee -a "$OUT"
    fi
  done
done
echo "wrote $OUT"
