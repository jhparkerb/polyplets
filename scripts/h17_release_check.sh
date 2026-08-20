#!/bin/bash
# Does the CHUNKED-RELEASE path still give the banked row at production scale?
#
# tests/gate_motley_par.py covers H <= 13 with release on; H = 19 production
# would be the first time the release path ran anywhere near its own size.
# H = 17 has a banked exact row (results/cutcount_b1/rows/C17.out) and ~24M
# states, so it is the cheapest height that is not a toy.
# Target: dalby, 8 threads on purpose -- the box has a sweep and a census on
# it and this is a correctness check, not a benchmark.
# Predicted: census ~3 min, pass ~30 min, RSS ~9 GB.
set -euo pipefail
B=$HOME/src/pm-lastditch/build/motley_par4
O=$HOME/var/motley-h17-rel
mkdir -p "$O"; echo $$ > "$O/pid"
[ -s "$O/sizes.txt" ] || /usr/bin/time -f "census H=17 wall=%e rss_kb=%M" \
  "$B" --census 17 40 --threads 8 --sizes-out "$O/sizes.txt" >/dev/null 2>>"$O/log"
/usr/bin/time -f "modp H=17 p=65521 wall=%e rss_kb=%M" \
  "$B" --modp 17 40 65521 "$O/C17.p65521.out" --threads 8 --sizes "$O/sizes.txt" \
  >/dev/null 2>>"$O/log"
python3 - "$O/C17.p65521.out" <<"PY" >>"$O/log" 2>&1
import sys
p = 65521
got = {}
for line in open(sys.argv[1]):
    a,b = line.split(); got[int(a)] = int(b)
ok = bad = 0
for line in open("/home/jasonp/src/polyominoes/results/cutcount_b1/rows/C17.out"):
    a,b = line.split(); n, v = int(a), int(b)
    if n in got:
        if got[n] == v % p: ok += 1
        else: bad += 1; print(f"MISMATCH n={n}")
print(f"H=17 RELEASE PATH vs banked C17 mod {p}: {ok} cells agree, {bad} wrong")
print("VERDICT:", "GREEN" if (bad==0 and ok>=30) else "RED")
PY
