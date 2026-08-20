#!/bin/bash
# motley_par4 with the census-sizes pass folded in, so the gate exercises the
# release path.  $1.. are the gate_motley_par.py argv for --modp.
H=$2; N=$3
SZ=/tmp/gatesz.$H.$N.txt
[ -s "$SZ" ] || ~/src/pm-lastditch/build/motley_par4 --census "$H" "$N" --threads 16 --sizes-out "$SZ" >/dev/null 2>&1
exec ~/src/pm-lastditch/build/motley_par4 "$@" --sizes "$SZ"
