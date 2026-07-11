#!/usr/bin/env bash
# Launch a whole-row g2 fleet run across dalby + ayr + gympie. Each box gets a
# DISJOINT IDX range of the SAME N/S/K split; split-sum invariance (gate-g2 C)
# makes the union exact regardless of which box ran which shard. Shares are
# ~ measured (per-core throughput x cores): dalby 53% / ayr 27% / gympie 20%
# (results/terminal-velocity.md). Each box runs in a FOREGROUND tmux window on
# its existing session 0 (survives ssh disconnect), tee'd to a launch log, and is
# per-shard resumable -- re-running this script relaunches only unfinished shards.
#
# USAGE:  scripts/g2_fleet_launch.sh N S K
# THEN:   wait with the robust poll-waiter (NOT tail --pid; see the plan), then
#         scripts/g2_fleet_gather.sh N K   to gather+combine+report.
#
# Boxes/cores are this fleet's fixed roles; gympie is HARD-capped at 10 perf cores.
set -euo pipefail
N="${1:?N}"; S="${2:?S}"; K="${3:?K}"

D_TO=$(( K * 53 / 100 ))     # dalby [0, D_TO)
A_TO=$(( K * 80 / 100 ))     # ayr   [D_TO, A_TO)   gympie [A_TO, K)

launch() {
  local host="$1" from="$2" to="$3" jobs="$4"
  ssh "$host" "tmux new-window -t '0:' -n g2_a${N} \"cd ~/src/polyominoes && \
    scripts/g2_wholerow.sh $N $S $K $jobs --range $from $to --no-combine \
    2>&1 | tee runs/g2row_N${N}.launch.log; exec bash\""
  echo ">>> launched $host  range [$from,$to)  jobs=$jobs"
}

echo ">>> g2 fleet whole-row N=$N S=$S K=$K  (dalby 53% / ayr 27% / gympie 20%)"
launch dalby.jhpb.org 0        "$D_TO"  80
launch ayr            "$D_TO"  "$A_TO"  32
launch gympie         "$A_TO"  "$K"     10
echo ">>> all windows up. Verify: ssh <box> 'tmux ls; tail runs/g2row_N${N}/driver.log'"
