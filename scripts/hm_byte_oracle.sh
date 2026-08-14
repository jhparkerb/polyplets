#!/bin/bash
# Half Measure byte-for-byte oracle (docs/motley-plan.md: "Each rung must
# reproduce the reference byte for byte at every height both can reach").
#
# Runs the u128 engine at the given heights and compares each row to the
# banked I256 row.  Any difference is a rung defect, not a discovery.
#
# Target machine: gympie for H <= 15 (10.5 GB at H=15), dalby for H=16
# (31 GB).  Measured cost, u128, gympie: H=14 ~5 min / 3.6 GB,
# H=15 ~18 min / 10.5 GB.  Single core each.
#
#   ./hm_byte_oracle.sh <bindir> <bankeddir> <outdir> <H>...
#
# Exits nonzero on the first mismatch; the engine's own self-checks
# (q0_zero, q1eval_binomial, the fits_pay bound) exit 2 before that.

set -euo pipefail
BIN="$1/cutcount_b1"; BANKED="$2"; OUT="$3"; shift 3
mkdir -p "$OUT"

for H in "$@"; do
  "$BIN" --height "$H" 40 "$OUT/C$H.out" 2>&1 | tee "$OUT/H$H.log"
  if cmp "$OUT/C$H.out" "$BANKED/C$H.out"; then
    echo "ORACLE H=$H BYTE_IDENTICAL to banked"
  else
    echo "ORACLE H=$H MISMATCH vs banked" >&2
    exit 2
  fi
done
echo "ORACLE ALL GREEN: $*"
