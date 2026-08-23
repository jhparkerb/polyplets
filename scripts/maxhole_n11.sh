#!/bin/bash
# The first real test of the maximum-hole-count closed form, at n = 11.
#
# WHY.  `results/maxhole-closed-form.md` identifies the maximum number of holes
# an n-cell king animal can enclose as `n - ceil(2*sqrt(n)) + 1` = A248333,
# matching all ten measured terms, with the lower bound proved by construction
# and the reverse inequality open.  Ten terms found the formula; n = 11 is the
# first term it did not see, and the file names it as the first n where the
# increment pattern is not forced by n = 10.  PREDICTION: 5.
#
# Target: ayr, single core.  Predicted from the measured ladder in that file --
# n = 8 is 31 s, n = 10 is 16 min at 8.8 GB, ratio ~6.4x per term:
#
#     n = 11   ~2 h   ~55 GB
#
# against ayr's 78 GB with nothing else resident.  The peak is the level-11
# animal list held in memory; if it exceeds ~70 GB the box will swap and the
# right response is to kill it, not to wait.
#
# NOT CHECKPOINTED, and that is a defect rather than a property: a kill costs
# the whole run.  Accepted here because the run is one pass and two hours; a
# resumable version would have to shard the level.
#
# Kill: kill the PID in ~/var/maxhole-n11/pid.
# Resume: none -- rerun.
#
# Rows print as each n completes, so progress is visible in the log without a
# heartbeat: n = 10 lands ~16 min in and n = 11 about two hours after that.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT=${MAXHOLE_OUT:-$HOME/var/maxhole-n11}
mkdir -p "$OUT"; echo $$ > "$OUT/pid"
{
  echo "=== king_extremal --nmax 11: $(date -Is)"
  echo "=== rev $(cd "$ROOT" && git rev-parse --short HEAD)"
} > "$OUT/run.log"
/usr/bin/time -f "king_extremal nmax=11 wall=%e rss_kb=%M" \
  python3 -u "$ROOT/experiments/king_extremal.py" --nmax 11 \
  >> "$OUT/run.log" 2>&1
echo "=== done $(date -Is)" >> "$OUT/run.log"
