#!/bin/sh
# r4 increment 3 — fail-closed check of the encoding layer.
#
#   sh experiments/tristruct/r4_lean2_gate.sh <repo-root>
#
# Six gates, in increasing cost. Every one of them fails closed: a missing
# input, a missing toolchain, a mutation that turned out to be a no-op, and an
# empty log are all failures, not skips.
#
#   D  (free)  the SHARED DEFS block is byte-identical in the two .lean files.
#              They cannot import each other (neither is a module), so the two
#              copies are kept honest by diff rather than by hope.
#   A  GREEN   r4_lean2_encode.lean elaborates with EXIT 0 AND NO OUTPUT.
#              Any stdout or stderr at all is a failure, warnings included.
#              One refinement over the funnel probe's gate A: if every error
#              line is the `#guard_msgs` axiom-pin mismatch, the failure is
#              reported as AXIOM-PIN-ONLY. It is still a failure and still
#              exits nonzero — but a pin mismatch is a fact about the axiom
#              footprint, not a hole in an argument, and the lead should not
#              have to read the log to tell the two apart.
#   B  RED 1   over-merging: `rowCls` is taken over all of `P` instead of over
#              the reachable closure, so every cut-column cell falls in every
#              class. This is the mutation that matters — it is exactly the
#              failure "the state cannot tell two components from one", which
#              is what the whole encoding is for. Must be REJECTED.
#   C  RED 2   the occupancy guard is removed from `lbl`, so an unoccupied row
#              gets a real label and `lbl_eq_top_iff` becomes false. Must be
#              REJECTED.
#   E  SKEL    r4_lean2_state.lean: exit 0, ZERO error lines, EXACTLY THREE
#              `declaration uses 'sorry'` warnings, and no other output. Both
#              directions bind: four sorries is a failure and two is a failure.
#   F  RED 3   `rowFin`'s range test is weakened so `omega` cannot discharge
#              the `Fin` bound. An error line must appear and gate E's criteria
#              must be violated — this exercises the half of gate E that a
#              sorry-count check alone would not.
#
# Nothing is written outside the repo; no /tmp. Mutant copies are created and
# removed beside the sources.
#
# Written 2026-08-13 by scout/builder r4-lean2, which ran none of it.

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

D="$ROOT/experiments/tristruct"
ENC="$D/r4_lean2_encode.lean"
SKEL="$D/r4_lean2_state.lean"
LOG="$D/r4_lean2_gate.log"
MUT="$D/r4_lean2_mutant.lean"
OUT="$D/r4_lean2_gate.out"
TM="$D/r4_lean2_gate.time"

for f in "$ENC" "$SKEL"; do
  if [ ! -f "$f" ]; then
    echo "FAIL: no source at $f" >&2
    exit 2
  fi
done

: > "$LOG"
echo "host=$(hostname) date=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
echo "lake=$LAKE toolchain=$(cat "$ROOT/polyplets/lean-toolchain")" >> "$LOG"

cd "$ROOT/polyplets" || exit 2

fail() {
  echo "$1" >> "$LOG"
  echo "$1 — see $LOG" >&2
  rm -f "$MUT" "$OUT" "$TM"
  exit 1
}

# `time -l` writes to ITS stderr; the elaborator's own output is redirected by
# the inner shell, so the two streams never mix and the emptiness test is exact.
elaborate() {
  /usr/bin/time -l sh -c '"$0" env lean "$1" > "$2" 2>&1' \
    "$LAKE" "$1" "$OUT" 2> "$TM"
  return $?
}

# ---- Gate D: the duplicated definition block has not drifted ----
echo "=== GATE D: SHARED DEFS byte-identity ===" >> "$LOG"
awk '/^-- BEGIN SHARED DEFS/,/^-- END SHARED DEFS/' "$ENC" > "$OUT"
awk '/^-- BEGIN SHARED DEFS/,/^-- END SHARED DEFS/' "$SKEL" > "$TM"
if [ ! -s "$OUT" ] || [ ! -s "$TM" ]; then
  fail "GATE D: FAIL — a SHARED DEFS block is missing or empty"
fi
if ! diff -u "$OUT" "$TM" >> "$LOG" 2>&1; then
  fail "GATE D: FAIL — the two SHARED DEFS blocks have drifted (diff above)"
fi
echo "gateD_shared_def_lines=$(wc -l < "$OUT" | tr -d ' ')" >> "$LOG"
echo "GATE D: PASS" >> "$LOG"
rm -f "$OUT" "$TM"

# ---- Gate A: the encode file must elaborate silently ----
echo "=== GATE A (GREEN): $ENC ===" >> "$LOG"
elaborate "$ENC"
A_RC=$?
echo "--- elaborator output (must be empty) ---" >> "$LOG"
cat "$OUT" >> "$LOG"
echo "--- wall / peak RSS (MEASURED, this run) ---" >> "$LOG"
cat "$TM" >> "$LOG"
A_NOISE=$(grep -c '[^[:space:]]' "$OUT")
A_ERR=$(grep -c 'error:' "$OUT")
A_PIN=$(grep 'error:' "$OUT" | grep -c 'Docstring on')
echo "gateA_exit=$A_RC" >> "$LOG"
echo "gateA_output_lines=$A_NOISE gateA_error_lines=$A_ERR gateA_pin_errors=$A_PIN" >> "$LOG"

if [ "$A_RC" -ne 0 ] || [ "$A_NOISE" -ne 0 ]; then
  if [ "$A_ERR" -gt 0 ] && [ "$A_ERR" -eq "$A_PIN" ]; then
    fail "GATE A: FAIL (AXIOM-PIN-ONLY) — every error is the #guard_msgs pin; the proofs elaborated"
  fi
  fail "GATE A: FAIL (exit=$A_RC, output lines=$A_NOISE, errors=$A_ERR)"
fi
echo "GATE A: PASS" >> "$LOG"
rm -f "$OUT" "$TM"

# ---- Gate B: RED 1, over-merging ----
echo "=== GATE B (RED 1: rowCls over-merges) ===" >> "$LOG"
echo "mutation: ((reachSet P (c, y)).filter -> ((P).filter" >> "$LOG"
sed 's/((reachSet P (c, y))\.filter/((P).filter/' "$ENC" > "$MUT"
if cmp -s "$ENC" "$MUT"; then
  fail "GATE B: FAIL — mutation was a no-op; the source changed under the script"
fi
"$LAKE" env lean "$MUT" >> "$LOG" 2>&1
B_RC=$?
echo "gateB_exit=$B_RC" >> "$LOG"
rm -f "$MUT"
if [ "$B_RC" -eq 0 ]; then
  fail "GATE B: FAIL — the over-merging mutant compiled; the encoding proves less than claimed"
fi
echo "GATE B: PASS (mutant rejected, exit=$B_RC)" >> "$LOG"

# ---- Gate C: RED 2, occupancy guard removed ----
echo "=== GATE C (RED 2: lbl loses its occupancy guard) ===" >> "$LOG"
echo "mutation: ' else ⊤' -> ' else (rowCls P c y).min' in lbl" >> "$LOG"
sed 's/ else ⊤$/ else (rowCls P c y).min/' "$ENC" > "$MUT"
if cmp -s "$ENC" "$MUT"; then
  fail "GATE C: FAIL — mutation was a no-op; the source changed under the script"
fi
"$LAKE" env lean "$MUT" >> "$LOG" 2>&1
C_RC=$?
echo "gateC_exit=$C_RC" >> "$LOG"
rm -f "$MUT"
if [ "$C_RC" -eq 0 ]; then
  fail "GATE C: FAIL — the unguarded-label mutant compiled; lbl_eq_top_iff is not being tested"
fi
echo "GATE C: PASS (mutant rejected, exit=$C_RC)" >> "$LOG"

# ---- Gate E: the skeleton, exactly three named holes ----
echo "=== GATE E (SKELETON): $SKEL ===" >> "$LOG"
elaborate "$SKEL"
E_RC=$?
echo "--- elaborator output (expected: exactly 3 sorry warnings) ---" >> "$LOG"
cat "$OUT" >> "$LOG"
echo "--- wall / peak RSS (MEASURED, this run) ---" >> "$LOG"
cat "$TM" >> "$LOG"
E_LINES=$(grep -c '[^[:space:]]' "$OUT")
E_ERR=$(grep -c 'error:' "$OUT")
E_SORRY=$(grep -c "declaration uses 'sorry'" "$OUT")
echo "gateE_exit=$E_RC gateE_output_lines=$E_LINES gateE_errors=$E_ERR gateE_sorries=$E_SORRY" >> "$LOG"
if [ "$E_RC" -ne 0 ]; then
  fail "GATE E: FAIL — the skeleton did not elaborate (exit=$E_RC)"
fi
if [ "$E_ERR" -ne 0 ]; then
  fail "GATE E: FAIL — $E_ERR error line(s); a statement does not type-check"
fi
if [ "$E_SORRY" -ne 3 ]; then
  fail "GATE E: FAIL — $E_SORRY sorry warnings, expected exactly 3 (see the hole ledger)"
fi
if [ "$E_LINES" -ne 3 ]; then
  fail "GATE E: FAIL — $E_LINES output lines, expected exactly the 3 sorry warnings"
fi
echo "GATE E: PASS (3 named holes, nothing else)" >> "$LOG"
rm -f "$OUT" "$TM"

# ---- Gate F: RED 3, the skeleton's error check must really bite ----
echo "=== GATE F (RED 3: rowFin's Fin bound cannot be discharged) ===" >> "$LOG"
echo "mutation: 'if h : 0 ≤ y ∧ y < (H : ℤ)' -> '... y ≤ (H : ℤ)'" >> "$LOG"
sed 's/if h : 0 ≤ y ∧ y < (H : ℤ)/if h : 0 ≤ y ∧ y ≤ (H : ℤ)/' "$SKEL" > "$MUT"
if cmp -s "$SKEL" "$MUT"; then
  fail "GATE F: FAIL — mutation was a no-op; the source changed under the script"
fi
"$LAKE" env lean "$MUT" > "$OUT" 2>&1
F_RC=$?
cat "$OUT" >> "$LOG"
F_ERR=$(grep -c 'error:' "$OUT")
echo "gateF_exit=$F_RC gateF_errors=$F_ERR" >> "$LOG"
rm -f "$MUT" "$OUT"
if [ "$F_RC" -eq 0 ] || [ "$F_ERR" -eq 0 ]; then
  fail "GATE F: FAIL — the broken-bound mutant produced no error; gate E's error check is inert"
fi
echo "GATE F: PASS (mutant rejected, exit=$F_RC, errors=$F_ERR)" >> "$LOG"

rm -f "$MUT" "$OUT" "$TM"
if [ ! -s "$LOG" ]; then
  echo "FAIL: empty log" >&2
  exit 1
fi
echo "ALL GATES PASS" >> "$LOG"
echo "ALL GATES PASS — $LOG"
exit 0
