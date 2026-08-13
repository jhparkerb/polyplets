#!/bin/sh
# r4 increment 1 — fail-closed check of r4_lean_funnel_probe.lean.
#
#   sh experiments/tristruct/r4_lean_funnel_probe.sh <repo-root>
#
# Gate A (GREEN): the probe elaborates with EXIT 0 AND NO OUTPUT. Any stdout or
#   stderr at all is a failure — warnings included. `#guard_msgs` prints nothing
#   when the axiom footprint matches, so silence is the whole success signal.
# Gate B (RED control 1, the stencil): one token is flipped in `cut_edge_cols`
#   so that the column conclusion is drawn from the row bound. `omega` must then
#   fail. A RED that passes means the probe is not testing what it claims.
#
# Fail-closed: unset/absent inputs, a missing toolchain, and an empty log are
# all failures. Nothing is written outside the repo; no /tmp.
#
# Written 2026-08-12 by scout r4-lean, which ran none of it.

ROOT="$1"
if [ -z "$ROOT" ] || [ ! -d "$ROOT/polyplets" ]; then
  echo "FAIL: usage: $0 <repo-root>  (must contain polyplets/)" >&2
  exit 2
fi

LAKE="$HOME/.elan/bin/lake"
if [ ! -x "$LAKE" ]; then
  echo "FAIL: no lake at $LAKE" >&2
  exit 2
fi

SRC="$ROOT/experiments/tristruct/r4_lean_funnel_probe.lean"
RED="$ROOT/experiments/tristruct/r4_lean_funnel_probe.red.lean"
LOG="$ROOT/experiments/tristruct/r4_lean_funnel_probe.log"
if [ ! -f "$SRC" ]; then
  echo "FAIL: no source at $SRC" >&2
  exit 2
fi

: > "$LOG"
echo "host=$(hostname) date=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
echo "lake=$LAKE toolchain=$(cat "$ROOT/polyplets/lean-toolchain")" >> "$LOG"

# ---- Gate A: the probe must elaborate silently ----
echo "=== GATE A: $SRC ===" >> "$LOG"
A_OUT="$ROOT/experiments/tristruct/r4_lean_funnel_probe.gateA.out"
A_TIME="$ROOT/experiments/tristruct/r4_lean_funnel_probe.gateA.time"
cd "$ROOT/polyplets" || exit 2

# `time -l` reports on ITS stderr; the elaborator's own output goes to A_OUT via
# the inner shell, so the two streams never mix and the emptiness test is exact.
/usr/bin/time -l sh -c '"$0" env lean "$1" > "$2" 2>&1' \
  "$LAKE" "$SRC" "$A_OUT" 2> "$A_TIME"
A_RC=$?
echo "--- elaborator output (must be empty) ---" >> "$LOG"
cat "$A_OUT" >> "$LOG"
echo "--- wall / peak RSS (MEASURED, this run) ---" >> "$LOG"
cat "$A_TIME" >> "$LOG"
echo "gateA_exit=$A_RC" >> "$LOG"

A_NOISE=$(grep -c '[^[:space:]]' "$A_OUT")
echo "gateA_elaborator_output_lines=$A_NOISE" >> "$LOG"

if [ "$A_RC" -ne 0 ] || [ "$A_NOISE" -ne 0 ]; then
  echo "GATE A: FAIL (exit=$A_RC, elaborator output lines=$A_NOISE)" >> "$LOG"
  echo "GATE A: FAIL — see $LOG" >&2
  rm -f "$A_OUT" "$A_TIME"
  exit 1
fi
echo "GATE A: PASS" >> "$LOG"
rm -f "$A_OUT" "$A_TIME"

# ---- Gate B: RED control 1 must fail loudly ----
# Mutation: draw the column conclusion of `cut_edge_cols` from the ROW bound.
echo "=== GATE B (RED control 1) ===" >> "$LOG"
echo "mutation: sed 's/have h := hadj.2.1/have h := hadj.2.2/'" >> "$LOG"
sed 's/have h := hadj\.2\.1/have h := hadj.2.2/' "$SRC" > "$RED"
if cmp -s "$SRC" "$RED"; then
  echo "GATE B: FAIL — mutation was a no-op; the probe changed under the script" >> "$LOG"
  echo "GATE B: FAIL — mutation no-op" >&2
  rm -f "$RED"
  exit 1
fi

"$LAKE" env lean "$RED" >> "$LOG" 2>&1
B_RC=$?
echo "gateB_exit=$B_RC" >> "$LOG"
rm -f "$RED"

if [ "$B_RC" -eq 0 ]; then
  echo "GATE B: FAIL — the RED mutant compiled; the probe proves less than claimed" >> "$LOG"
  echo "GATE B: FAIL — RED mutant compiled" >&2
  exit 1
fi
echo "GATE B: PASS (mutant rejected, exit=$B_RC)" >> "$LOG"

if [ ! -s "$LOG" ]; then
  echo "FAIL: empty log" >&2
  exit 1
fi
echo "ALL GATES PASS" >> "$LOG"
echo "ALL GATES PASS — $LOG"
exit 0
