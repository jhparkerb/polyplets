#!/bin/bash
# dalby_a35_two_media.sh -- compute a(35) via the two-media plan
# (docs/a35-two-media-plan.md), then combine + validate.
#
# Two concurrent orchestrate processes, split by height AND by medium:
#   Job A: the tallest real height H19 (~70% of the wall) -> run-dir on tmpfs
#          (/mnt/polytmp, RAM). Disk-free -> ~4x faster (measured a34: 4.13x).
#   Job B: all other heights (real H3-H18 + closed-form H1,H2,H20-H35) -> NVMe.
# Different media => no disk contention; CPU-bound A co-schedules with I/O-bound
# B (measured a34 two-media: 4.6x overall, box 75% busy, all heights
# byte-identical). Both --cores 80 (oversubscribed; the a34 cal showed the OS
# balances them to finish together, no split tuning). combine reads every
# per-height shard and errors if one is missing, so a dropped height fails loud.
#
# PRECONDITION: /mnt/polytmp mounted (root tmpfs, >=90G) and writable. a(35)'s
# H19 run-dir peaks ~76-80G; the 100G mount holds it. Watch it the first hour
# (H19's mid-sweep peak) -- with swap removed, an overflow OOMs rather than
# swaps, so it must stay under available RAM.
#
# PREDICTED: ~3.5h wall (a34 two-media 2883s x ~4.4/term-ish, tall-height
# dominated). Peak RAM ~80G tmpfs + ~15G heaps; Job B cache evictable.
# Recoverable: each job checkpoints to NVMe every 300s (mid-column over-count
# bug fixed, dd91550); a crash costs one job. Job A's RAM scratch is lost on a
# REBOOT (not a process crash) -- fine for a same-day run.
#
# RUN:  scripts/dalby_a35_two_media.sh
# KILL: kill the two orchestrate PIDs (jobA.log/jobB.log name them).
set -e
cd ~/src/polyominoes
N=35
TMPFS=/mnt/polytmp
BASE=runs/ns_a35_2m
PH=runs/ns_a35/perheight

[ -d "$TMPFS" ] && touch "$TMPFS/.w" 2>/dev/null && rm -f "$TMPFS/.w" || { echo "FATAL: $TMPFS not mounted/writable"; exit 2; }
rm -rf "$TMPFS"/* "$BASE"
mkdir -p "$TMPFS/spill" "$BASE/nvme/spill" "$PH"
rm -f "$PH"/*.out

echo "=== a35 TWO-MEDIA run: $(date -Iseconds), rev $(git rev-parse --short HEAD) ==="
echo "Job A = H19 on tmpfs ($TMPFS) ; Job B = H1-18,20-35 on NVMe"
T0=$(date +%s)

# Job A: tallest real height on tmpfs.
./build/ns/orchestrate --maxn $N --heights 19 --kernel kink --counter u128 \
  --cores 80 --ram 1073741824 --run-dir "$TMPFS" --spill-dir "$TMPFS/spill" \
  --per-height-out "$PH" --cost-profile-out "$BASE/costA.tsv" \
  --checkpoint "$BASE/CKPT_A" --checkpoint-every 300 \
  > "$BASE/jobA.log" 2>&1 &
PA=$!

# Job B: everything else (real H3-18 + closed-form H1,H2,H20-35) on NVMe.
./build/ns/orchestrate --maxn $N --heights 1-18,20-35 --kernel kink --counter u128 \
  --cores 80 --ram 1073741824 --overlap-heights 35 --run-dir "$BASE/nvme" --spill-dir "$BASE/nvme/spill" \
  --per-height-out "$PH" --cost-profile-out "$BASE/costB.tsv" \
  --checkpoint "$BASE/CKPT_B" --checkpoint-every 300 \
  > "$BASE/jobB.log" 2>&1 &
PB=$!
echo "Job A pid=$PA (tmpfs H19) ; Job B pid=$PB (NVMe rest)"

wait "$PA"; RA=$?; echo "Job A (H19 tmpfs) done at $(( $(date +%s)-T0 ))s rc=$RA"
wait "$PB"; RB=$?; echo "Job B (NVMe rest) done at $(( $(date +%s)-T0 ))s rc=$RB"
T1=$(date +%s)
echo "=== a35 two-media compute wall=$((T1-T0))s (A rc=$RA, B rc=$RB) ==="
rm -rf "$TMPFS"/*
[ "$RA" = 0 ] && [ "$RB" = 0 ] || { echo "A JOB FAILED -- not combining"; exit 1; }

echo "=== combine ==="
./build/ns/combine -in "$PH" -maxn $N -out "$BASE/a_n.txt" 2>&1 | tee "$BASE/combine.log"

MISMATCH=0
echo "=== validate a(1)-a(20) vs b-file ==="
for n in $(seq 1 20); do
  got=$(awk -v n=$n '$1==n{print $2}' "$BASE/a_n.txt")
  known=$(awk -v n=$n '$1==n{print $2}' fixtures/b006770.txt)
  if [ "$got" = "$known" ]; then echo "a($n)=$got OK"; else echo "a($n)=$got MISMATCH (b=$known)"; MISMATCH=1; fi
done
echo "=== validate a(21)-a(34) vs banked ==="
for n in $(seq 21 34); do
  got=$(awk -v n=$n '$1==n{print $2}' "$BASE/a_n.txt")
  bank=""
  if [ -f "results/ns_a${n}/triangle.txt" ] && [ "$(awk 'NR==1{print NF; exit}' "results/ns_a${n}/triangle.txt")" = "2" ]; then
    bank=$(awk -v n=$n '$1==n{print $2}' "results/ns_a${n}/triangle.txt")
  fi
  [ -z "$bank" ] && { echo "a($n): no banked value"; continue; }
  if [ "$got" = "$bank" ]; then echo "a($n)=$got OK"; else echo "a($n)=$got MISMATCH (banked=$bank)"; MISMATCH=1; fi
done

aN=$(awk -v n=$N '$1==n{print $2}' "$BASE/a_n.txt")
aP=$(awk -v n=34 '$1==34{print $2}' "$BASE/a_n.txt")
echo "a($N) = $aN"
[ -n "$aP" ] && [ -n "$aN" ] && python3 -c "print('growth a35/a34 =', $aN/$aP)" 2>/dev/null
if [ "$MISMATCH" = 0 ]; then echo "A35_VALIDATE_PASS"; else echo "A35_VALIDATE_FAIL"; fi
echo "A35_TWO_MEDIA_DONE"
