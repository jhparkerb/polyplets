#!/usr/bin/env bash
# Gather a fleet whole-row g2 run's shards from dalby + ayr + gympie, combine, and
# report a(N). Tars each box's w*.out/w*.done into ONE file per box (per-file scp
# over thousands of shards is minutes-slow), pulls them to a local dir, extracts,
# and runs scripts/g2_combine.sh (which fails loudly if any of the K shards is
# missing). Run only after the robust poll-waiter says all three boxes are cleanly
# complete.
#
# USAGE:  scripts/g2_fleet_gather.sh N K [--per-box]
# RESULT: <local dir>/combined.txt  (+ prints a(N)); dir echoed at the end.
set -euo pipefail
N="${1:?N}"; K="${2:?K}"; PERBOX="${3:-}"
RUN="g2row_N${N}"; [ "$PERBOX" = "--per-box" ] && RUN="g2row_N${N}_perbox"
DIR="$(cd "$(dirname "$0")/.." && pwd)/runs/fleet_${RUN}"
rm -rf "$DIR"; mkdir -p "$DIR"

for host in dalby.jhpb.org ayr gympie; do
  echo ">>> gathering $host"
  ssh "$host" "# Repo root from the script's own path, not a hardcoded ~/src/polyominoes:
# a clone lands wherever the reader put it (acceptance-queue item 2).
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"/runs/$RUN && tar czf /tmp/${RUN}_gather.tgz w*.out w*.done"
  scp -q "$host:/tmp/${RUN}_gather.tgz" "$DIR/$host.tgz"
  tar xzf "$DIR/$host.tgz" -C "$DIR"
  ssh "$host" "rm -f /tmp/${RUN}_gather.tgz"
done
echo ">>> gathered: out=$(find "$DIR" -name 'w*.out' | wc -l | tr -d ' ') done=$(find "$DIR" -name 'w*.done' | wc -l | tr -d ' ')  (expect $K)"

scripts/g2_combine.sh "$DIR" "$N" "$K" $PERBOX
echo ">>> combined dir: $DIR"
