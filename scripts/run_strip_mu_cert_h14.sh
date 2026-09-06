#!/bin/bash
# run_strip_mu_cert_h14.sh — exact Collatz-Wielandt certificate for mu_14.
#
# Purpose: promote mu_14 = 6.3800344 from a floating-point power-iteration value
#   to a machine-checkable rational, so the project's rigorous lambda bracket can
#   quote the lower end at certificate grade (mu_14 <= lambda by subfamily
#   containment, results/growth-constant.md). Method and the H<=11
#   receipts: results/growth-constant.md.
# Machine: any; single-threaded, ~350 MB peak (17 MB measured at H=11, states
#   grow 15510 -> 310571). No spill, no checkpoint.
# Predicted cost: ~1.2-1.5 h wall. Basis: MEASURED on gympie H=9 11.2s,
#   H=10 36.2s, H=11 120.9s (3.3x/height => H=14 ~70 min), and the banked
#   strip_mu_kink H=14 float solve at 4851s (results/strip_mu_H14.log) on the
#   same class of box. The exact phase adds at most a few tens of sweeps, ~1
#   matvec each (20 sweeps cost no measurable extra wall in the H=10 --vbits 55
#   stress case), i.e. minutes, not hours.
# Kill/resume: plain kill of the strip_mu_cert PID; single-unit job with no
#   checkpoint — a kill costs the whole run. Nothing is appended to the receipt
#   log until the H completes, so a kill leaves no partial receipt.
# Output: one logfmt receipt line appended to results/strip_mu_certificates.log
#   (H, num/den, states, SHA-256 of the certificate vector, PASS/FAIL, wall);
#   full stdout+stderr teed to results/strip_mu_cert_H14.log.
# Usage: run_strip_mu_cert_h14.sh [H_LO [H_HI]]   (default 14 14)
set -e
H_LO=${1:-14}
H_HI=${2:-14}
# Repo root from the script's own path, not a hardcoded ~/src/polyominoes:
# a clone lands wherever the reader put it (acceptance-queue item 2).
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
make build/strip_mu_cert
./build/strip_mu_cert --selftest          # RED-first gate before the long run
echo "=== strip_mu_cert H=$H_LO..$H_HI host=$(hostname -s) rev=$(git rev-parse --short HEAD) $(date -u +%FT%TZ) ==="
echo "=== cpp/strip_mu_cert.cpp blob $(git hash-object cpp/strip_mu_cert.cpp) ==="
exec ./build/strip_mu_cert "$H_LO" "$H_HI" --digits 7 --log results/strip_mu_certificates.log
