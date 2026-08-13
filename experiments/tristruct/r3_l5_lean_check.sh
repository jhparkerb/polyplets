#!/bin/sh
# r3-l5-JOB-1: compile-check the L5 hardening proofs (r3_l5_normalization.lean)
# and re-run the L5 evaluation file, on a non-gympie box (docs/r3-job-dispatch.md).
#
# Prerequisites on the target: elan with toolchain leanprover/lean4:v4.31.0,
# repo checkout, and the polyplets mathlib .olean cache
# (cd polyplets && ~/.elan/bin/lake exe cache get   -- one-time, ~GBs).
#
# Usage: r3_l5_lean_check.sh /path/to/polyominoes
# GREEN: exits 0 after printing "r3-l5-JOB-1 GREEN".
# Any nonzero exit is a failure; the offending log names the lemma.
set -eu
REPO="${1:?usage: r3_l5_lean_check.sh /path/to/polyominoes}"
TS="$REPO/experiments/tristruct"
LAKE="$HOME/.elan/bin/lake"
cd "$REPO/polyplets"

# 1. GREEN gate A: the hardening proofs must elaborate clean (no output).
"$LAKE" env lean "$TS/r3_l5_normalization.lean" 2>&1 \
  | tee "$TS/r3_l5_normalization.log"
test ! -s "$TS/r3_l5_normalization.log"

# 2. GREEN gate B: re-run the evaluation file (replaces the log truncated on
#    gympie 2026-08-12 19:04); expect the banked-value line and per-cell walls.
"$LAKE" env lean "$TS/r3_l5_king_connected.lean" 2>&1 \
  | tee "$TS/r3_l5_king_connected.rerun.log"
grep -q 'ALL BANKED VALUES REPRODUCED' "$TS/r3_l5_king_connected.rerun.log"

# 3. RED control: a corrupted banked constant must be flagged.
#    (5,3,248) -> (5,3,249): the #eval table must report exactly 1 MISMATCHES.
RED="$TS/r3_l5_red_mutant.lean"
sed 's/(5,3,248)/(5,3,249)/' "$TS/r3_l5_king_connected.lean" > "$RED"
grep -q '(5,3,249)' "$RED"   # fail closed if the mutation did not take
"$LAKE" env lean "$RED" >"$TS/r3_l5_red_mutant.log" 2>&1 || true
grep -q '1 MISMATCHES' "$TS/r3_l5_red_mutant.log" || {
  echo "RED CONTROL FAILED TO FIRE" >&2
  exit 1
}
rm -f "$RED"

echo "r3-l5-JOB-1 GREEN"
