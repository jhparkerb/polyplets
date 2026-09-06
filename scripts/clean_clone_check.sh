#!/bin/bash
# clean_clone_check.sh --- acceptance-queue item 2: does a fresh clone build?
#
# PURPOSE   A referee's first act is `git clone && make`. Nothing in this project
#           has ever verified that on a box with no working tree, so this runs the
#           sequence end to end on a genuinely clean machine and records every
#           exit code instead of stopping at the first failure. Known going in:
#           the Makefile has no `all` target (bare `make` runs `gates`), and
#           `build/ns/*_worker` is not reachable from GATE_TARGETS.
#
# TARGET    ayr (32 cores, 78 GB). Needs ~/go/bin first in PATH for a modern Go;
#           the Debian go1.19 in the default PATH will not build core/.
#
# COMMAND   [REPRO_N=24] ~/var/clean-clone/clean_clone_check.sh /path/to/repo.bundle
#
#           Bundle it with --all, not just master: the citations gate verifies
#           branch declarations against the refs the clone actually has, and a
#           master-only bundle cannot exercise that path.
#
# COST      make gates measured 624 s serial / 467 s at -j10 on gympie
#           (Makefile:53). Predict under 15 min at -j32 here; ns-gates adds an
#           unmeasured tail. No large RAM: the gates run over fixtures, not the
#           production frontier. Peak expected well under 8 GB.
#
# RESUME    None needed and none offered: it is minutes, and re-running is free.
#           To kill, kill the pid in $OUT/run.pid.
#
# OUTPUT    $OUT/report.txt --- one STEP line per phase with rc and seconds ---
#           plus per-step logs. Read report.txt first.

set -u
BUNDLE=${1:?usage: clean_clone_check.sh <bundle>}
OUT=${OUT:-$HOME/var/clean-clone/run}
CLONE=$OUT/polyplets
export PATH="$HOME/go/bin:$PATH"

rm -rf "$OUT"
mkdir -p "$OUT"
echo $$ > "$OUT/run.pid"
REPORT=$OUT/report.txt

say() { echo "$*" | tee -a "$REPORT"; }

# step <name> <logfile> <command...>: run it, time it, record rc, never abort.
step() {
    local name=$1 log=$2; shift 2
    local t0 t1 rc
    t0=$(date +%s)
    "$@" > "$OUT/$log" 2>&1
    rc=$?
    t1=$(date +%s)
    say "STEP $name rc=$rc secs=$((t1 - t0)) log=$log"
    return $rc
}

say "clean-clone check  host=$(hostname)  start=$(date -Is)"
say "bundle=$BUNDLE"

step clone clone.log git clone -q --branch master "$BUNDLE" "$CLONE" || {
    say "FATAL: clone failed"; exit 1
}
cd "$CLONE" || exit 1
say "rev=$(git rev-parse --short HEAD)  tracked_files=$(git ls-files | wc -l)"
# literature/ exists in a clone -- five text files there are tracked.  Whether a
# copyrighted PDF got in is NOT decided here: `step make` below runs the gate
# suite, which includes gate-no-copyright-pdfs, and that one sets an exit code.
# A second "(must be 0)" line that only prints is the fail-open shape the gate
# was written to replace, so this reports the clone's shape and nothing more.
say "literature/ in the clone: $(ls literature/ 2>/dev/null | wc -l) files (gate-no-copyright-pdfs rules on PDFs, under \`step make\`)"

# The four phases a stranger would run, in the order the README implies.
# `make` and `make gates` are the same target -- the Makefile has no `all` and
# no .DEFAULT_GOAL, so the first rule in the file wins. Run it once, under the
# name a reader types.
step make            make.log            make
step make-ns-gates   make-ns-gates.log   make ns-gates
step verify-lpapers  verify-lpapers.log  python3 paper/verify_l_papers.py
step verify-report   verify-report.log   python3 paper/verify_technical_report.py
# The PDFs are gitignored, so a reader has the .tex and builds them himself.
step build-papers    build-papers.log    make -C paper

# The item's real deliverable: one command that reproduces a banked term from
# nothing but the clone. a(24) is the size that fits an hour on 32 cores; set
# REPRO_N to something else to price a different one.
if [ -n "${REPRO_N:-}" ]; then
    step "reproduce-a$REPRO_N" "reproduce.log" ./scripts/term.sh "$REPRO_N"
fi

say "binaries built: $(ls build 2>/dev/null | wc -l) in build/, $(ls build/ns 2>/dev/null | wc -l) in build/ns/"
say "done=$(date -Is)"
