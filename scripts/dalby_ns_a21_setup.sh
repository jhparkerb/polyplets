#!/bin/bash
# dalby_ns_a21_setup.sh — wait for old-engine a(21) H20 to finish, then
# fetch next-system branch, build new engine, launch a(21) run.
#
# Run in a dalby tmux window; pass the H20 pid as $1.
# Usage: scripts/dalby_ns_a21_setup.sh <H20_pid>

set -euo pipefail

H20_PID=${1:?usage: $0 <H20_pid>}
REPO=$(cd "$(dirname "$0")/.." && pwd)

echo "=== dalby_ns_a21_setup start $(date -Iseconds) ==="
echo "repo: $REPO"
echo "waiting for H20 pid $H20_PID to exit..."

tail --pid="$H20_PID" -f /dev/null

echo "H20 done $(date -Iseconds)"

cd "$REPO"
git log --oneline -1

echo "building new engine..."
make build/ns/orchestrate build/ns/map_worker build/ns/merge_worker

echo "launching a(21)..."
exec scripts/dalby_ns_a21.sh
