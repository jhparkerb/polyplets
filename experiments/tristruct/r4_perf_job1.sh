#!/usr/bin/env bash
# PERF-JOB-1 -- does the fast-modp patch pay, and does it change any value?
# Job request: results/r4/r4-perf.md §4. Runs on dalby, single thread, idle box.
#
# The control is `cmp`, not "correct": every lever in the patch claims to
# preserve the value bit for bit, so anything short of byte-identical rows is a
# failure even if the numbers happen to be right.
set -u

PERF="$HOME/src/pm-b1-perf"
BASE="$HOME/src/pm-b1"
BIN="$PERF/build/cutcount_b1"
OUT="$PERF/results/cutcount_b1/modp"
REF="$BASE/results/cutcount_b1/modp"
P=2147483647

mkdir -p "$OUT"
echo "=== PERF-JOB-1 start $(date -u +%FT%TZ)"
echo "patched:   $(sha256sum "$BIN")"
echo "reference: $(sha256sum "$BASE/build/cutcount_b1")"

fail=0
for H in 13 14 15; do
  f="$OUT/C$H.p$P.out"
  echo "--- H=$H start $(date -u +%FT%TZ)"
  /usr/bin/time -v "$BIN" --modp "$H" 40 "$P" "$f" 2>&1
  rc=$?
  echo "--- H=$H rc=$rc end $(date -u +%FT%TZ)"
  if [ "$rc" -ne 0 ]; then echo "ABORT: patched binary exited $rc at H=$H"; exit "$rc"; fi
  if cmp -s "$f" "$REF/C$H.p$P.out"; then
    echo "CMP H=$H: IDENTICAL to the unpatched row"
  else
    echo "CMP H=$H: **DIFFERS** from the unpatched row -- the patch changed a value"
    fail=1
  fi
done

echo "=== PERF-JOB-1 done $(date -u +%FT%TZ) cmp_failures=$fail"
exit "$fail"
