#!/bin/bash
# motley_par4 with the census-sizes pass folded in, so the gate exercises the
# release path.  $1.. are the gate_motley_par.py argv for --modp.
#
# Two things this used to get wrong.  The sizes cache lived under /tmp, against
# the rule that no run record does; it lives under ~/var now.  And the binary
# was hardcoded to a side worktree (~/src/pm-lastditch) that the engine has
# since landed out of -- pointing there would certify a stale build against the
# in-tree gate.  MOTLEY_BIN still overrides, for the campaign's own binary.
H=$2; N=$3
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BIN=${MOTLEY_BIN:-$ROOT/build/motley_par}
SZDIR=${SZDIR:-$HOME/var/motley_sizes}
mkdir -p "$SZDIR"
SZ=$SZDIR/gatesz.$H.$N.txt
[ -s "$SZ" ] || "$BIN" --census "$H" "$N" --threads 16 --sizes-out "$SZ" >/dev/null 2>&1
exec "$BIN" "$@" --sizes "$SZ"
