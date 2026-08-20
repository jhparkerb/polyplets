#!/bin/bash
# Motley H = 19 with the parallel + chunked-release engine: the rung
# docs/motley-plan.md calls Ticker Tape and priced at 27-40 days.
#
# Purpose: T(n,19) = C_19 - 2 C_18 + C_17 rule-independently.  That retires
# T(40,19) -- the ONE cell of row 40 that Undertow cannot reach from Motley's
# banked H <= 18 rows (results/undertow.md) -- and with it a(40) entirely.
#
# Payload width is chosen by the prime, so the prime list is the knob:
#   31-bit (default): 4 primes reconstruct values < 2^112 (product ~2^124),
#     a 5th held out and PREDICTED from the CRT over the other four -- the
#     same RED-D Confetti used.  u32 payload, ~83 GB.  Five passes.
#   16-bit (MOTLEY_PRIMES=...): 8 + 1 held out, u16 payload, ~48 GB, nine
#     passes.  Slower in total (per-pass cost barely moves with payload
#     width) but it is what fits ayr's 76 GB.
#
# Measured inputs, not guesses: H=19 has 224,529,648 states (census, saturated
# at column 1); H=14/Nmax40 is 11.8 s at 80 threads and the per-height wall
# ratio is ~3.4x, so ~1.2 h per pass on dalby's 80 cores.
#   dalby, 31-bit x5:  ~6 h,  ~83 GB
#   ayr,   16-bit x9: ~29 h,  ~48 GB
#
# The census runs FIRST and is not optional: it writes the exact per-cell-step
# state counts, and only with those can the engine hand the consumed source
# back (a regrow retry would re-read what it just released).
#
# Kill: kill the PID in $OUT/pid.  Resume: re-run -- passes whose output file
# exists are skipped, and each pass checkpoints at every column boundary.
set -euo pipefail
# Repo root from the script's own path, and the binary the Makefile built
# there -- docs/engineering-standards.md 5: code arrives by pull, runs from a
# checkout (or a worktree of one), and the binary carries a real GIT_REV.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN=${MOTLEY_BIN:-$ROOT/build/motley_par}
OUT=${MOTLEY_OUT:-$HOME/var/motley-h19}
H=19
NMAX=${MOTLEY_NMAX:-40}
THREADS=${MOTLEY_THREADS:-$(nproc)}
read -r -a PRIMES <<< "${MOTLEY_PRIMES:-2147483647 2147483629 2147483587 2147483579 2147483563}"
mkdir -p "$OUT"; echo $$ > "$OUT/pid"
SZ="$OUT/sizes.H$H.N$NMAX.txt"
if [ ! -s "$SZ" ]; then
  echo "=== census H=$H Nmax=$NMAX: $(date -Iseconds) ==="
  /usr/bin/time -f "census wall=%e rss_kb=%M" \
    "$BIN" --census "$H" "$NMAX" --threads "$THREADS" --sizes-out "$SZ" \
    >> "$OUT/census.log" 2>> "$OUT/timings.txt"
fi
for P in "${PRIMES[@]}"; do
  f="$OUT/C$H.p$P.out"
  [ -s "$f" ] && { echo "skip p=$P"; continue; }
  mkdir -p "$OUT/ckpt.$P"
  echo "=== pass p=$P: $(date -Iseconds) ==="
  /usr/bin/time -f "p=$P wall=%e rss_kb=%M" \
    "$BIN" --modp "$H" "$NMAX" "$P" "$f" --threads "$THREADS" \
    --sizes "$SZ" --ckpt "$OUT/ckpt.$P" \
    >> "$OUT/console.log" 2>> "$OUT/timings.txt"
  rm -rf "$OUT/ckpt.$P"
done
echo "ALL ${#PRIMES[@]} PASSES DONE" >> "$OUT/timings.txt"
