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

# Target lists come from the Makefile itself so this cannot drift from what the
# hook runs. Fail closed: an empty list means the parse broke, not that there
# is nothing to profile.
fastlist="$(sed -n 's/^ns-gate-fast: *//p' Makefile)"
gatelist="$(sed -n 's/^GATE_TARGETS = *//p' Makefile)"
[ -n "$fastlist" ] || { echo "profile_gates: cannot parse ns-gate-fast from Makefile" >&2; exit 2; }
[ -n "$gatelist" ] || { echo "profile_gates: cannot parse GATE_TARGETS from Makefile" >&2; exit 2; }

# What -j did `gates` actually use? Same expression the Makefile uses.
if [ "$(uname -s)" = Darwin ]; then
  jobs_n="$(sysctl -n hw.perflevel0.logicalcpu 2>/dev/null || sysctl -n hw.ncpu)"
else
  jobs_n="$(nproc 2>/dev/null || echo 4)"
fi

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
