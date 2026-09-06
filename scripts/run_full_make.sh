#!/bin/bash
# Run the full `make` and tee it to a named log, recording make's own exit code
# (not tee's -- hence pipefail) on the last line of the log.
#
# Purpose: the final gate for any session that touches code. Named on-disk
# script because docs/job-checklist.md item 3 forbids running it from a
# heredoc or a `-c` one-liner.
# Exact command:   scripts/run_full_make.sh results/make_full_<topic>.log
# Target machine:  gympie (laptop), single make job.
# Predicted cost:  ~11 min wall on gympie -- measured 10m47s on the one
#                  2026-08-06 run that recorded a timing. (The sibling
#                  results/make_full_*.log runs this line used to point at
#                  were removed 2026-08-22; see docs/publication.md.
#                  Fifteen of the sixteen never recorded a wall time, and the
#                  "~5-10 min" they were said to support was not in any of
#                  them.) No RAM or disk pressure.
# Kill/resume:     plain SIGINT; make restarts from whatever is already built.
set -u
set -o pipefail
log="${1:?usage: run_full_make.sh LOGFILE}"
cd "$(dirname "$0")/.."
make 2>&1 | tee "$log"
rc=$?
echo "make exit code: $rc" | tee -a "$log"
exit "$rc"
