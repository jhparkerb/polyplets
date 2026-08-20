#!/bin/bash
# Motley heights HMIN..HMAX at one Nmax, with the parallel engine.
#
# PURPOSE.  T(n,H) = C_H - 2 C_{H-1} + C_{H-2} needs EVERY C_H up to the top
# height, so a row is only rule-independent once the whole ladder has been run
# at that Nmax.  Motley's banked rows (results/cutcount_b1/rows/) all stop at
# n = 40, which is why a(41) has no second rule under it: heights 1..19 come
# from the kink engine alone and the tower supplies the rest.
#
# At HMAX = 19 and depths j <= 4 the Undertow reach rule n <= 2*hmax + J - 1
# gives n <= 41 exactly, so this ladder at Nmax 41 is what makes BOTH
#   * a(40) complete -- T(40,19) is the single cell the tower cannot reach
#     from banked H <= 18 data (results/undertow.md), and
#   * a(41) rule-independent in every cell,
# out of one pass.  Run at Nmax 40 it buys only the first.
#
# TARGET: dalby, 80 cores, 125 GB.  Predicted, from measurements not models:
#   H=19 has 224,529,648 states (census, saturated at column 1).  The measured
#   H=18 release point is 445 B/state at stride 352 (32.06 GB, 1731.7 s at 80
#   threads), so u16 at H=19 is ~59 GB and ~1.64 h per prime at Nmax 40; the
#   measured fixed-height Nmax factor is ~1.08x for 40->41.  Per-height wall
#   ratio ~3.4x.  Nine 16-bit primes (eight reconstruct values < 2^112, the
#   ninth is held out and PREDICTED from the CRT over the others).
#
#     H=19  ~1.8 h/prime  ~16 h   ~59 GB
#     H=18  ~0.5 h/prime  ~4.7 h  ~19 GB
#     H=17  ~0.15 h/prime ~1.4 h
#     H<=16                ~0.6 h
#     censuses                       ~2.5 h
#     TOTAL                        ~25 h
#
#   u16 rather than u32-and-five-primes: 101 GB on a 125 GB box is 83%, and the
#   H=18 RAM prediction came in 34% under the measurement.  That is the margin
#   that becomes an OOM.
#
# The census per height is NOT optional: it writes the exact per-cell-step
# state counts, and only with those can the engine hand the consumed source
# back (a regrow retry would re-read what it just released).
#
# KILL: kill the PID in $OUT/pid, then the engine PID from ps.
# RESUME: re-run.  Censuses and prime passes whose output exists are skipped,
# and each pass checkpoints at every column boundary.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN=${MOTLEY_BIN:-$ROOT/build/motley_par}
OUT=${MOTLEY_OUT:-$HOME/var/motley-ladder}
NMAX=${MOTLEY_NMAX:-41}
HMIN=${MOTLEY_HMIN:-1}
HMAX=${MOTLEY_HMAX:-19}
THREADS=${MOTLEY_THREADS:-$(nproc)}
read -r -a PRIMES <<< "${MOTLEY_PRIMES:-65521 65519 65497 65479 65449 65447 65437 65423 65413}"

[ -x "$BIN" ] || { echo "no engine at $BIN -- make build/motley_par" >&2; exit 1; }
mkdir -p "$OUT"; echo $$ > "$OUT/pid"
echo "=== motley ladder H=$HMIN..$HMAX Nmax=$NMAX threads=$THREADS: $(date -Iseconds) ==="
echo "=== engine $($BIN 2>&1 | head -1) ==="

# Tallest first: it is the one that can fail on RAM, and finding that out after
# eighteen cheap heights have run is the wrong order.
for H in $(seq "$HMAX" -1 "$HMIN"); do
  SZ="$OUT/sizes.H$H.N$NMAX.txt"
  if [ ! -s "$SZ" ]; then
    echo "=== census H=$H: $(date -Iseconds) ==="
    /usr/bin/time -f "census H=$H N=$NMAX wall=%e rss_kb=%M" \
      "$BIN" --census "$H" "$NMAX" --threads "$THREADS" --sizes-out "$SZ" \
      >> "$OUT/census.H$H.log" 2>> "$OUT/timings.txt"
  fi
  for P in "${PRIMES[@]}"; do
    f="$OUT/C$H.p$P.out"
    [ -s "$f" ] && continue
    mkdir -p "$OUT/ckpt.$H.$P"
    echo "=== H=$H p=$P: $(date -Iseconds) ==="
    /usr/bin/time -f "H=$H p=$P wall=%e rss_kb=%M" \
      "$BIN" --modp "$H" "$NMAX" "$P" "$f" --threads "$THREADS" \
      --sizes "$SZ" --ckpt "$OUT/ckpt.$H.$P" \
      >> "$OUT/console.H$H.log" 2>> "$OUT/timings.txt"
    rm -rf "$OUT/ckpt.$H.$P"
  done
  echo "H=$H COMPLETE (${#PRIMES[@]} primes)" >> "$OUT/timings.txt"
done
echo "LADDER COMPLETE H=$HMIN..$HMAX Nmax=$NMAX" >> "$OUT/timings.txt"
