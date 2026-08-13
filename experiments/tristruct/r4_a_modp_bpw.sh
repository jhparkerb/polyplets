#!/usr/bin/env bash
# LG-JOB-1R -- bytes/window and us/slot-col of the committed --modp payload.
# Job request: results/r4/r4-a.md §3. Runs in the worktree ~/src/pm-b1 (48ac108),
# single-threaded, on dalby. Per-(H,prime) resume: a completed row file is skipped.
set -u

WT="${WT:-$HOME/src/pm-b1}"
BIN="$WT/build/cutcount_b1"
OUT="$WT/results/cutcount_b1/modp"
ORACLE="$HOME/src/polyominoes/results/cutcount_b1/rows"   # the recovered exact rows
CHECK="$WT/experiments/tristruct/r4_a_modp_rowcheck.py"

P1=2147483647
PRIMES=(2147483647 2147483629 2147483587 2147483579 2147483563)

mkdir -p "$OUT"
echo "=== LG-JOB-1R start $(date -u +%FT%TZ)"
echo "binary sha256: $(sha256sum "$BIN")"
echo "oracle: $ORACLE"

run_one() {   # H prime
  local H="$1" p="$2"
  local f="$OUT/C$H.p$p.out"
  if [ -s "$f" ]; then echo "skip H=$H p=$p (row exists)"; return 0; fi
  echo "--- H=$H p=$p start $(date -u +%FT%TZ)"
  /usr/bin/time -v "$BIN" --modp "$H" 40 "$p" "$f" 2>&1
  local rc=$?
  echo "--- H=$H p=$p rc=$rc end $(date -u +%FT%TZ)"
  if [ "$rc" -ne 0 ]; then echo "ABORT: --modp exited $rc at H=$H p=$p"; rm -f "$f"; exit "$rc"; fi
}

# (a)+(b): the slope ladder -- four consecutive marginal slopes at one prime.
for H in 12 13 14 15 16; do run_one "$H" "$P1"; done

# CRT / RED-D rehearsal at a cheap height.
for p in "${PRIMES[@]:1}"; do run_one 13 "$p"; done

# (c) RED-modp: every residue against the exact recovered oracle, at production scale.
echo "=== rowcheck $(date -u +%FT%TZ)"
python3 "$CHECK" "$ORACLE" "$OUT"
echo "rowcheck rc=$?"
echo "=== LG-JOB-1R done $(date -u +%FT%TZ)"
