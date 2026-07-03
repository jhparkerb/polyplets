#!/bin/bash
# Controlled A/B: is ns-gate-spill (test/driver1.cpp, column-kernel M1 spill
# path) actually broken by the kink-carry branch, or is the failure
# branch-independent (compiler/UB/stale-tree)? Diagnostic for Design 14
# Phase 3 kink validation. Runs both branches on ONE box/one compiler,
# hashes the driver1 translation-unit project sources under each so we know
# whether the source even differs, and records PASS/FAIL + spill bytes with
# real exit codes (no tail-masking).
set -u
cd ~/src/polyominoes-ns
OUT=/tmp/gate_spill_ab.log
: > "$OUT"

HDRS="test/driver1.cpp core/classifier.h core/counter.h core/euler.h core/libenum.h core/mapreduce.h core/profile.h core/run.h core/runfile.h core/signature.h core/transition.h worker/worker_util.h"

run_branch() {
  local br="$1"
  git checkout "$br" >>"$OUT" 2>&1
  echo "=== branch=$br rev=$(git rev-parse --short HEAD) ===" | tee -a "$OUT"
  echo "driver1-TU-md5=$(cat $HDRS | md5sum | cut -d' ' -f1)" | tee -a "$OUT"
  rm -f build/ns/driver1
  make build/ns/driver1 >>"$OUT" 2>&1
  local bd="/tmp/gate_spill_ab_${br//\//_}"
  rm -rf "$bd" && mkdir -p "$bd"
  ./build/ns/driver1 --maxn 14 --ram 1048576 --spill "$bd" --compare > "/tmp/gsab_${br//\//_}.out" 2>&1
  local rc=$?
  echo "driver1-exit=$rc" | tee -a "$OUT"
  grep -E "n=11|n=14|gate_spill|total_spill_bytes" "/tmp/gsab_${br//\//_}.out" | tee -a "$OUT"
  echo "" | tee -a "$OUT"
}

CUR=$(git rev-parse --abbrev-ref HEAD)
run_branch next-system
run_branch kink-carry
git checkout "$CUR" >>"$OUT" 2>&1
echo "GATE_SPILL_AB_DONE"
