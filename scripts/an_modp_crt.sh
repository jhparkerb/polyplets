#!/usr/bin/env bash
# R1xR3(xB) reach driver: exact a(n) for n<=N via fold + u32 mod-p height sweeps + CRT.
# For each prime p:  a(n) mod p = sum over heights H of B_H(n) mod p  (one sweep per (H,p)).
# CRT across 3 primes near 2^31 recovers exact a(n). The N*3 (H,p) sweeps are INDEPENDENT,
# so --jobs J runs J of them at once (each writes its own rows_p${p}_H${H}.txt -- no shared
# append, no interleave). --blocked S adds B (the drained/partitioned store): ~2x less RAM
# per worker, composing with --fold (R1) and --modp (R3). RAM budget = J x per-worker-peak.
#
# HARDENED (no silent failures): (1) an atomic mkdir-lock prevents a second run from
# clobbering rows files on the same dir (the race that once corrupted output); (2) each
# sweep's stderr is kept in hb_p{p}_H{H}.log for debugging; (3) every sweep's EXIT CODE is
# checked and a non-zero sweep aborts the run; (4) crt_combine.py then validates every
# output is complete before combining. A crashed/raced sweep can never be summed as a zero.
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
DIR="runs/anmodp_N$N"; mkdir -p "$DIR"
# Atomic lock: a second run on the same N fails fast instead of racing the rows files.
if ! mkdir "$DIR/.lock" 2>/dev/null; then
  echo "ERROR: $DIR/.lock held -- another run on N=$N is active (or stale; rmdir to clear)" >&2
  exit 3
fi
trap 'rmdir "$DIR/.lock" 2>/dev/null' EXIT
echo $$ > "$DIR/driver.pid"
rm -f "$DIR"/rows_p*_H*.txt "$DIR"/hb_p*_H*.log   # fresh -- stale files would mislead

# Run the N*3 independent (H,p) sweeps, at most JOBS concurrent. wait -n frees a slot as a
# worker finishes AND yields its exit status; any non-zero status is recorded.
fail=0; launched=0
for p in $PRIMES; do
  for H in $(seq 1 "$N"); do
    build/tma square8 "$N" --only-height "$H" --modp "$p" $FOLD $BLOCKED \
      > "$DIR/rows_p${p}_H${H}.txt" 2> "$DIR/hb_p${p}_H${H}.log" &
    launched=$((launched + 1))
    if [ "$launched" -ge "$JOBS" ]; then wait -n || fail=1; launched=$((launched - 1)); fi
  done
done
while [ "$launched" -gt 0 ]; do wait -n || fail=1; launched=$((launched - 1)); done
if [ "$fail" -ne 0 ]; then
  echo "ERROR: >=1 sweep exited non-zero (see $DIR/hb_*.log)" >&2
  exit 4
fi

python3 scripts/crt_combine.py "$DIR" "$N" $PRIMES
