#!/bin/bash
# H = 17 of the frontier census, re-run under the CORRECTED retirement rule.
#
# WHY.  The H = 17 run started on dalby 2026-08-22T23:45 is stamped rev
# a825ad114, which predates 384bd2e -- the fix for the retirement rule that
# could file one component as two when a closed group and the open run share
# an old block whose last row has just passed.  results/closed-doors.md says
# H = 16 "was produced by the pre-fix binary and is being re-run under the
# corrected rule; H = 17 likewise", and this is that re-run.  The fix is known
# to change nothing at H = 14 and H = 15 and is being confirmed at H = 16 on
# ayr; whether it changes anything at 17 is unmeasured, and the census is
# single-threaded on an 80-core box, so measuring it costs one core.
#
# WHAT IT COSTS.  H = 16 was 10,454 s; the cost ratio decelerates (6.7 then
# 5.3 per height), so H = 17 is ~15 h and well under a GB -- H = 16 peaked at
# 80 MB and the class count grows ~2.55x.  One core, no disk.
#
# WHAT IT SETTLES.  Agreement with the in-flight pre-fix run banks H = 17 from
# two binaries.  Disagreement means the pre-fix number is wrong and the fix is
# reachable at 17, which would also put the pre-fix H = 16 in question no
# matter what ayr returns.
#
# Target: dalby, alongside the pre-fix H = 17 run and whatever else is up.
# Kill: kill the PID in ~/var/nkey-census-postfix/pid.  Costs the whole height.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export NKEY_OUT=${NKEY_OUT:-$HOME/var/nkey-census-postfix}
exec "$ROOT/scripts/nkey_census_ladder.sh" 17 17
