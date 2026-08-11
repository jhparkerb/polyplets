#!/usr/bin/env bash
# run_cutcount_b1_calib.sh — B1 colour-symmetrized spin TM (clash-zeroing) calibration.
#
# Purpose: second-source team candidate B1 (results/second-source-candidates-B.md):
#   recompute the triangle's C_H rows by the colour-symmetrized spin TM
#   ([q^1] in Z[q]/(q^2), clash-zeroing, no partition joins) — connectivity
#   never decided, only extracted — and compare
#   T(n,H) against the banked triangle for every banked cell, H<=15 then H<=16.
#   H=15/16 include the kink-only Grand anchors T(28,15) T(29,15) T(30,16) T(31,16).
#
# Command:  bash scripts/run_cutcount_b1_calib.sh     (from repo root, dalby)
# Machine:  dalby (125 GB, idle but for a 1-thread g2 siteperim run — leave it alone).
# Predicted cost (from gympie measurements 2026-08-11: C_10 full = 2.9 s, 91 MB,
#   per-height wall ratio ~3.8x, states 891,074 at H=14 growing ~2.9x/height;
#   dalby ~5.4x slower per thread per results/strip-engine.md):
#   1 core (single-threaded). With the third self-check coefficient (+~40%):
#   wall H<=15 phase ~7 h, H=16 phase ~18 h. Peak RAM: ~9 GB at H=14, ~27 GB
#   at H=15, ~80 GB at H=16 — fits 121 GB free. Measured on this run so far:
#   H=12 was 117.5 s / 567 MB with 2 coefficients (2026-08-11 first launch).
#   Per-height selfchecks logged: q0_zero, q1eval_binomial.
# Resume:   per-height rows land in results/cutcount_b1/rows/C<H>.out; rerun the
#   script and completed heights are skipped. A kill costs one height at most.
# Kill:     kill the cutcount_b1 PID shown in the tmux window; rows already
#   written are kept.
# Provenance: the run in flight 2026-08-11 was launched from a dalby tree
#   clean-at-3b7359de that stamps -dirty (22 untracked result files), with
#   cpp/cutcount_b1.cpp still uncommitted. It is committed now, on branch
#   second-source, together with gate-cutcount-b1; the source sha256 echoed
#   into the log below is what identifies which revision produced a row.
#   NOTE: the committed engine exits nonzero on a mismatch AND on a
#   zero-cell comparison; the running binary predates that and exits 0.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=results/cutcount_b1
ROWS=$OUT/rows
mkdir -p "$ROWS"
LOG=$OUT/calib_run.log
exec > >(tee -a "$LOG") 2>&1
echo "=== run_cutcount_b1_calib $(date -u +%Y-%m-%dT%H:%M:%SZ) host=$(hostname)"
echo "=== source sha256: $(sha256sum cpp/cutcount_b1.cpp | cut -c1-16)  tree: $(git rev-parse --short HEAD)$(git diff --quiet 2>/dev/null || echo -dirty)"
for H in $(seq 1 16); do
  f=$ROWS/C$H.out
  if [ -s "$f" ]; then echo "skip H=$H (row exists)"; continue; fi
  ./build/cutcount_b1 --height "$H" 40 "$f.tmp"
  mv "$f.tmp" "$f"
  if [ "$H" = 15 ]; then
    echo "=== H<=15 assemble/compare:"
    ./build/cutcount_b1 --assemble 15 40 "$ROWS" results/ns_a40/perheight || true
  fi
done
echo "=== H<=16 assemble/compare:"
./build/cutcount_b1 --assemble 16 40 "$ROWS" results/ns_a40/perheight
echo "=== done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
