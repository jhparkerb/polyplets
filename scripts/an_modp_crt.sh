#!/usr/bin/env bash
# R1xR3(xB) reach driver: exact a(n) for n<=N via fold + u32 mod-p height sweeps + CRT.
# For each prime p:  a(n) mod p = sum over heights H of B_H(n) mod p  (one sweep per (H,p)).
# CRT across 3 primes near 2^31 recovers exact a(n). The N*3 (H,p) sweeps are INDEPENDENT,
# so --jobs J runs J of them at once (each writes its own rows_p${p}_H${H}.txt -- no shared
# append, no interleave). --blocked S adds B (the drained/partitioned store): ~2x less RAM
# per worker, composing with --fold (R1) and --modp (R3). RAM budget = J x per-worker-peak,
# so pick J for the machine (gympie<=10 cores, ayr 32, dalby ~25-35 bandwidth-bound).
#
# USAGE: scripts/an_modp_crt.sh N [--fold|--nofold] [--jobs J] [--blocked S]
#   defaults: --fold, --jobs 1 (serial -- this is the gate default), --blocked off
set -uo pipefail
cd "$(dirname "$0")/.."

N="${1:?N}"; shift || true
FOLD="--fold"; JOBS=1; BLOCKED=""
while [ $# -gt 0 ]; do
  case "$1" in
    --fold)    FOLD="--fold" ;;
    --nofold)  FOLD="" ;;
    --jobs)    JOBS="$2"; shift ;;
    --blocked) BLOCKED="--blocked $2"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

PRIMES="2147483647 2147483629 2147483587"
DIR="runs/anmodp_N$N"; mkdir -p "$DIR"; echo $$ > "$DIR/driver.pid"
rm -f "$DIR"/rows_p*_H*.txt   # fresh -- stale per-(H,p) files would double-count

# Run the N*3 independent (H,p) sweeps with at most JOBS concurrent. wait -n frees a
# slot as soon as ANY worker finishes (no fixed-batch barrier); no pkill anywhere.
running=0
for p in $PRIMES; do
  for H in $(seq 1 "$N"); do
    build/tma square8 "$N" --only-height "$H" --modp "$p" $FOLD $BLOCKED \
      2>/dev/null > "$DIR/rows_p${p}_H${H}.txt" &
    running=$((running + 1))
    if [ "$running" -ge "$JOBS" ]; then wait -n; running=$((running - 1)); fi
  done
done
wait

python3 scripts/crt_combine.py "$DIR" "$N" $PRIMES
