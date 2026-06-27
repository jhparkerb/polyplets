#!/usr/bin/env bash
# ns_heightsplit.sh — run one height-subset of an a(n) sweep on this host.
#
# Multi-machine height-split (a(n) = Σ_H T(n,H)): invoke this on each host with a
# DISJOINT --heights subset, then rsync the per-height output dirs to one host and
# combine:
#
#   host1$  scripts/ns_heightsplit.sh 22 1-11   60 64 ~/runs/ns_a22
#   host2$  scripts/ns_heightsplit.sh 22 12-22  60 64 ~/runs/ns_a22
#   combine$ rsync -a host1:~/runs/ns_a22/perheight/ ~/runs/ns_a22/all/
#   combine$ rsync -a host2:~/runs/ns_a22/perheight/ ~/runs/ns_a22/all/
#   combine$ build/ns/combine --in ~/runs/ns_a22/all --maxn 22 --require-cover --compare
#
# Run this as the body of a tmux window (foreground, tee'd) per the project's
# long-job convention; pair with a `tail --pid <orchestrate-pid>` waiter.
set -euo pipefail

MAXN="${1:?usage: ns_heightsplit.sh MAXN HEIGHTS CORES RAM_GB RUNROOT [UNIT_MULT] [REF_PROFILE]}"
HEIGHTS="${2:?heights subset, e.g. 1-11 or 12,14,16}"
CORES="${3:?cores}"
RAM_GB="${4:?ram budget per worker, GB}"
RUNROOT="${5:?run root dir}"
UNIT_MULT="${6:-1}"
REF_PROFILE="${7:-}"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="$(hostname -s)"
RUNDIR="$RUNROOT/$HOST"
SPILL="$RUNDIR/spill"
PERHEIGHT="$RUNROOT/perheight"   # rsync this dir to the combine host
RAM_BYTES=$(( RAM_GB * 1024 * 1024 * 1024 ))

mkdir -p "$SPILL" "$PERHEIGHT"

REFARG=()
[ -n "$REF_PROFILE" ] && REFARG=(--cost-profile-ref "$REF_PROFILE")

echo "ns_heightsplit host=$HOST maxn=$MAXN heights=$HEIGHTS cores=$CORES unit_mult=$UNIT_MULT ram_gb=$RAM_GB"
echo "rundir=$RUNDIR perheight=$PERHEIGHT"

exec "$REPO/build/ns/orchestrate" \
    --maxn "$MAXN" --cores "$CORES" --unit-mult "$UNIT_MULT" \
    --heights "$HEIGHTS" --ram "$RAM_BYTES" \
    --run-dir "$RUNDIR" --spill-dir "$SPILL" \
    --per-height-out "$PERHEIGHT" \
    --checkpoint "$RUNDIR/POLYCKPT" --checkpoint-every 900 \
    --cost-profile-out "$RUNDIR/cost_profile.tsv" \
    "${REFARG[@]}"
