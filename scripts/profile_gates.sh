#!/usr/bin/env bash
# Profile the pre-push gate suite: what does a `git push` actually pay for?
#
# .githooks/pre-push runs `make ns-gate-fast` (serial -- no -j) and then, for
# any push touching code, the full `make gates` (-j$(JOBS)). This script times
# BOTH as the hook runs them, then re-times every individual target serially so
# the parallel critical path can be named rather than guessed.
#
# Warm-build by design: phase A/B leave every binary built, so the phase-C
# per-target numbers are the steady-state cost of a push whose code was already
# compiled. The build cost itself is reported separately by phase A's own time.
#
# Output: a TSV (target, phase, seconds, exit status) plus a ranked summary.
set -uo pipefail

root="$(git rev-parse --show-toplevel)" || exit 1
cd "$root" || exit 1

out="${1:-build/gate-profile.tsv}"
mkdir -p "$(dirname "$out")" build/gate-profile-logs
: > "$out"
printf 'target\tphase\tseconds\tstatus\n' >> "$out"

# bash 5 gives sub-second wall time with no subprocess; fall back to GNU date.
now() {
  if [ -n "${EPOCHREALTIME:-}" ]; then echo "${EPOCHREALTIME/,/.}"
  else date +%s.%N; fi
}

run() {   # run <phase> <label> <make-args...>
  local phase="$1" label="$2"; shift 2
  local log="build/gate-profile-logs/${phase}-${label}.log"
  local t0 t1 st
  t0="$(now)"
  make -C "$root" "$@" > "$log" 2>&1
  st=$?
  t1="$(now)"
  local secs
  secs="$(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f", b-a}')"
  printf '%s\t%s\t%s\t%s\n' "$label" "$phase" "$secs" "$st" >> "$out"
  printf '%8ss  %-28s %s\n' "$secs" "$label" \
    "$([ "$st" -eq 0 ] && echo ok || echo "RED(exit $st) -- $log")"
}

# Target lists come from make itself, not from sed-ing the Makefile. The sed
# version claimed it "cannot drift from what the hook runs" and drifted within
# the same change: once `ns-gate-fast:` grew a prerequisite, the scrape returned
# the literal string $(NS_FAST_PREREQS) -- non-empty, so the fail-closed check
# passed it straight through to `make`.
#
# So the check is on the SHAPE now, not just on emptiness: every token has to
# look like a gate target, which a stray variable reference or a filename does
# not.
fastlist="$(make -s -C "$root" print-NS_FAST_TARGETS)"
gatelist="$(make -s -C "$root" print-GATE_TARGETS)"
jobs_n="$(make -s -C "$root" print-JOBS)"

check_list() {                  # check_list <name> <tokens...>
  local name="$1"; shift
  [ "$#" -gt 0 ] || { echo "profile_gates: $name is empty" >&2; exit 2; }
  local t
  for t in "$@"; do
    case "$t" in
      gate-*|ns-gate-*) ;;
      *) echo "profile_gates: $name has a token that is not a gate target: $t" >&2
         exit 2 ;;
    esac
  done
}
check_list NS_FAST_TARGETS $fastlist
check_list GATE_TARGETS $gatelist


echo "=== host $(hostname -s)  rev $(git rev-parse --short HEAD)  JOBS=$jobs_n"
echo
echo "=== phase A: the hook's own two commands, in hook order"
run hook ns-gate-fast ns-gate-fast
run hook gates gates
echo
echo "=== phase B: ns-gate-fast targets, serial, warm"
for t in $fastlist; do run fast "$t" "$t"; done
echo
echo "=== phase C: GATE_TARGETS, serial, warm"
for t in $gatelist; do run gates "$t" "$t"; done

echo
echo "=== ranked (serial, warm), slowest first"
awk -F'\t' 'NR>1 && ($2=="fast"||$2=="gates"){printf "%8.2fs  %-10s %s\n",$3,$2,$1}' "$out" | sort -rn
echo
awk -F'\t' '
  NR>1 && $2=="fast"  {f+=$3; if($3>fm){fm=$3}}
  NR>1 && $2=="gates" {g+=$3; if($3>gm){gm=$3; gt=$1}}
  END{printf "ns-gate-fast: serial sum %.1fs (hook runs it SERIAL)\n", f;
      printf "gates:        serial sum %.1fs, slowest single target %.1fs (%s)\n", g, gm, gt}' "$out"
echo "=== TSV: $out"
