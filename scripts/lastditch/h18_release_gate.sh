#!/bin/bash
# Gate the CHUNKED-RELEASE path at production scale, before a 15-hour run uses it.
#
# tests/gate_motley_par.py covers H <= 13 with release on (1560 cell
# comparisons).  ayr's five-prime H=18 reproduction used the OLD binary, with
# release OFF.  So the release path has never run near its own size, and
# Motley C_19 would be the first time -- which is the wrong place to find out.
# H = 18 has a banked Confetti residue row to compare against byte for byte.
#
# Target: dalby, 80 cores, idle.  Predicted: census ~8 min (H=18 has
# 72,487,711 states MEASURED), pass ~26 min EXTRAPOLATED from H=14/80t = 11.8 s
# at ~3.4x per height, RSS ~25 GB (u32, release, 8-byte buckets: 72.5M x 352 B
# x 1.15 + buckets).  Decision it changes: if RED, Motley C_19 runs with
# release OFF and needs ~2x the RAM, which changes the payload width.
# Kill: kill the PID in ~/var/motley-h18-rel/pid.
set -euo pipefail
B=$HOME/src/pm-lastditch/build/motley_par4
O=$HOME/var/motley-h18-rel
P=2147483647
mkdir -p "$O"; echo $$ > "$O/pid"
[ -s "$O/sizes.txt" ] || /usr/bin/time -f "census H=18 wall=%e rss_kb=%M" \
  "$B" --census 18 40 --threads 80 --sizes-out "$O/sizes.txt" >/dev/null 2>>"$O/log"
/usr/bin/time -f "modp H=18 p=$P RELEASE wall=%e rss_kb=%M" \
  "$B" --modp 18 40 "$P" "$O/C18.p$P.out" --threads 80 --sizes "$O/sizes.txt" \
  >/dev/null 2>>"$O/log"
if cmp -s "$O/C18.p$P.out" "$HOME/var/C18.p$P.out"; then
  echo "H=18 RELEASE PATH: IDENTICAL to the banked Confetti residue row -- GREEN" >>"$O/log"
else
  echo "H=18 RELEASE PATH: DIFFERS from banked -- RED" >>"$O/log"; exit 2
fi
