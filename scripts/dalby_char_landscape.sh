#!/bin/bash
# Characteristic-landscape sweep at one height, sharded across cores.
#
# Purpose: certify that characteristic 2 is the only place the strip
# functional's Hankel rank collapses -- every prime below the T4 bound tested
# by direct computation, everything above it excluded by the bound.  See
# experiments/tristruct/r3_char_landscape.py for the theorems.
#
# Target machine: dalby.  Predicted cost at H=9: ~190 primes at ~150 s each
# (dalby is ~2.7x slower per core than gympie on this probe), so ~8 core-hours
# over NSHARD cores; ~250 MB per shard.  H=8 is ~25 min of core time.
#
#   ./dalby_char_landscape.sh <H> <NSHARD>
#
# Each shard writes cl_H<H>_<i>.log; the certifier reads them all together:
#   python3 r3_char_landscape_certify.py cl_H<H>_*.log
# Resume by rerunning any shard whose log is short -- shards are independent.

set -euo pipefail
H="$1"; NSHARD="$2"
cd "$HOME/var/coinlift"

for i in $(seq 0 $((NSHARD - 1))); do
  python3 -u r3_char_landscape.py "$H" "$i" "$NSHARD" > "cl_H${H}_${i}.log" 2>&1 &
done
wait
echo "=== all $NSHARD shards done $(date -Is)"
python3 r3_char_landscape_certify.py cl_H${H}_*.log
