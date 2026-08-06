#!/bin/bash
# RED demonstration for gate-dir4-perim-alg's null control.
#
# The gate's null control (199 terms of the HV-convex king animals BY AREA
# series) used to be a derived file sitting untracked in results/. It is now
# re-cut into build/ from results/convex_area_terms_n700_king.txt on every run.
# This script proves the gate STOPS -- loudly, nonzero -- when that real source
# is missing, truncated, or altered, and that it never falls back to a
# previously cut copy sitting in build/.
#
#   target: gympie, local, single-threaded
#   cost:   ~1 s (each RED case exits before any prec_guess call)
#   usage:  scripts/dir4_perim_gate_red_check.sh
set -u
cd "$(dirname "$0")/.."

SRC=results/convex_area_terms_n700_king.txt
SAVE=build/convex_area_terms_n700_king.SAVED
NULL=build/dir4_perim_null199.txt
fail=0

restore() { [ -f "$SAVE" ] && mv -f "$SAVE" "$SRC"; }
trap restore EXIT

[ -f "$SRC" ] || { echo "no $SRC to test with" >&2; exit 1; }
before=$(shasum "$SRC" | cut -d' ' -f1)

# case <label> <expect-in-message>
case_red() {
  local label="$1" want="$2" out rc
  out=$(python3 tests/gate_dir4_perim_alg.py 2>&1); rc=$?
  printf '%-34s rc=%-3s ' "$label" "$rc"
  if [ "$rc" -ne 0 ] && printf '%s' "$out" | grep -q "$want"; then
    echo "RED as required"
  else
    echo "*** NOT RED (or wrong message) ***"; printf '%s\n' "$out" | head -20
    fail=1
  fi
}

mv "$SRC" "$SAVE"

rm -f "$NULL"
case_red "source missing, no cut file" "null control source missing"

# the stale-copy trap: a previously cut control is present, source is not.
head -199 results/mk_dir4_perim_terms_s200.txt > "$NULL"
case_red "source missing, stale cut present" "null control source missing"
rm -f "$NULL"

head -100 "$SAVE" > "$SRC"
case_red "source truncated to 100 terms" "fewer than the 199"

awk 'NR==7{print $1, $2+1; next} {print}' "$SAVE" > "$SRC"
case_red "source term 7 altered by +1" "does not start with the banked"

restore; rm -f "$SAVE"; trap - EXIT
after=$(shasum "$SRC" | cut -d' ' -f1)
[ "$before" = "$after" ] || { echo "*** source not restored ***"; fail=1; }

echo
echo "--- and GREEN with the real source in place:"
python3 tests/gate_dir4_perim_alg.py | tail -3 || fail=1

[ "$fail" -eq 0 ] && echo "RED CHECK DONE" || { echo "RED CHECK FAILED"; exit 1; }
