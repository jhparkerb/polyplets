#!/bin/bash
# The coverage audit of polyplets-report.tex, sharded across cores.
#
# WHY.  tests/gate_p_paper_verifier.py established that 199 of the 200 numeric
# literals in technical-report.tex are read by a check -- the first evidence
# that its verifier's 781 green checks mean anything.  paper/verify_claims.py
# guards the other human-authored paper with 428 checks and has had the same
# absence of a RED control.  It cannot be gated the same way because one run is
# 431 s, so the same measurement is made once, offline, and recorded.
#
# WHAT IT COSTS.  264 literals x 431 s = ~32 core-hours; at 16 shards, ~2 h
# wall.  Memory is one verify_claims process per shard, measured by the first
# shard's /usr/bin/time line before the rest are trusted.
#
# Target: dalby ONLY.  ayr has neither build/g2 nor the runs/sym3x directories
# verify_claims reads, and every shard there would fail its green control.
# Each shard re-runs that control first, so a box missing the inputs exits 2
# rather than reporting a wall of false "guarded".
#
# Kill: kill the PIDs in $OUT/pids.  Shards are independent; a kill costs only
# the shards in flight, and re-running one shard re-does only its literals.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT=${PCOV_OUT:-$HOME/var/p-coverage}
N=${1:-16}
mkdir -p "$OUT"; : > "$OUT/pids"
echo "=== polyplets coverage audit, $N shards: $(date -Is)" >> "$OUT/log.txt"
echo "=== rev $(cd "$ROOT" && git rev-parse --short HEAD)" >> "$OUT/log.txt"
for i in $(seq 0 $((N-1))); do
  /usr/bin/time -f "shard=$i wall=%e rss_kb=%M" \
    python3 "$ROOT/tests/p_paper_coverage_audit.py" --paper polyplets \
      --shard "$i" --of "$N" --out "$OUT/shard$i.json" \
      >> "$OUT/log.txt" 2>> "$OUT/events.txt" &
  echo $! >> "$OUT/pids"
done
wait
{
  echo "-- all shards done $(date -Is)"
  python3 "$ROOT/tests/p_paper_coverage_audit.py" --paper polyplets \
    --merge "$OUT"/shard*.json
} >> "$OUT/log.txt" 2>&1
