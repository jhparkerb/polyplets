#!/usr/bin/env bash
# r3_ladder_bpw_probe.sh — LG-JOB-1: bytes/window and us/slot-col of the
# residue-payload cutcount_b1 variant (results/triangle-r3-ladder-gate.md §2).
#
# NOT RUN by the wave-5 scout (docs/r3-job-dispatch.md: agents do not run
# compute). Dispatch prerequisite: a residue-payload build of
# second-source:cpp/cutcount_b1.cpp (2 x u8 coefficients mod one 8-bit prime
# in place of 3 x u256; stencil/transitions/self-checks/--assemble unchanged),
# passed as $1. Run on ayr or dalby from the repo root, in a tmux window.
#
# Measures: per-height peak RSS and wall at H=12..15 from the engine's own
# obs lines; reports the three pairwise marginal slopes
#   (RSS_H2 - RSS_H1) / (windows_H2 - windows_H1)
# which cancel fixed overhead. Decisive bands (gate for H=20 routing):
#   <= 113 B/window : ayr sole-tenant possible
#   113..175        : dalby only
#   > 175           : H=20 residue out of RAM everywhere
# Slopes disagreeing > 15% across the three pairs = rehash/load-factor
# artifact: rerun once; if it persists, report the max and label it.
#
# Correctness guard (must be green before any RSS number is believed):
# --assemble H<=10 against the banked triangle (400 cells; the committed
# engine exits nonzero on mismatch or zero-cell compare).
set -euo pipefail
BIN=${1:?usage: r3_ladder_bpw_probe.sh <residue-payload cutcount_b1 binary>}
cd "$(dirname "$0")/../.."
OUT=results/tristruct_bpw
ROWS=$OUT/rows
mkdir -p "$ROWS"
LOG=$OUT/bpw_probe.log
exec > >(tee -a "$LOG") 2>&1
echo "=== r3_ladder_bpw_probe $(date -u +%Y-%m-%dT%H:%M:%SZ) host=$(hostname) bin=$BIN"
echo "=== binary sha256: $(sha256sum "$BIN" | cut -c1-16)"

for H in 12 13 14 15; do
  /usr/bin/time -v "$BIN" --height "$H" 40 "$ROWS/C$H.out" 2>&1
done

echo "=== correctness guard: assemble H<=10 vs banked (must exit 0)"
"$BIN" --assemble 10 40 "$ROWS" results/ns_a40/perheight

echo "=== slopes (marginal bytes/window between consecutive heights)"
python3 - "$LOG" <<'EOF'
import re, sys
txt = open(sys.argv[1]).read()
rss = dict(re.findall(r'peak_rss_mb=([\d.]+) mode=height H=(\d+)', txt))
rss = {int(h): float(m) for m, h in
       re.findall(r'peak_rss_mb=([\d.]+) mode=height H=(\d+)', txt)}
win = {int(h): int(s) for h, s in re.findall(r'H=(\d+) states=(\d+)', txt)}
hs = sorted(set(rss) & set(win) & {12, 13, 14, 15})
for a, b in zip(hs, hs[1:]):
    slope = (rss[b] - rss[a]) * 1048576 / (win[b] - win[a])
    print(f"H={a}->{b}: {slope:.1f} B/window")
EOF
echo "=== done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
