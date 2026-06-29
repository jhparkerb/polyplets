#!/usr/bin/env bash
# g2_campaign.sh — Redelmeier (Method A) count of A006770 a(1..MAXN) as a split
# campaign of K single-core workers on this box, combined to per-height T(n,H)
# and totals a(n). This is the INDEPENDENT confirmation algorithm — it shares no
# counting logic with the transfer-matrix engine (oeis/submission-a19.md).
#
# Usage:  g2_campaign.sh MAXN K OUTDIR [SPLIT_S]
#   MAXN     target n
#   K        number of split workers (= cores to use)
#   OUTDIR   per-worker outputs + combined triangle.txt / an.txt
#   SPLIT_S  subtree split size (default 7)
#
# Per the job-checklist: run it in a tmux window with `time`, tee'd to a log.
set -euo pipefail
MAXN="${1:?MAXN}"; K="${2:?K}"; OUTDIR="${3:?OUTDIR}"; SPLIT_S="${4:-7}"
root="$(cd "$(dirname "$0")/.." && pwd)"
G2="$root/build/g2"
[ -x "$G2" ] || { echo "g2_campaign: $G2 not built (make build/g2)" >&2; exit 1; }
mkdir -p "$OUTDIR"
rev="$(git -C "$root" rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "event=start tool=g2_campaign a=$MAXN lattice=square8 K=$K split_s=$SPLIT_S rev=$rev t=$(date -u +%FT%TZ)"

pids=()
for ((idx=0; idx<K; idx++)); do
  w=$(printf 'w%04d' "$idx")
  "$G2" square8 "$MAXN" --per-box --split "$SPLIT_S" "$K" "$idx" \
      > "$OUTDIR/$w.out" 2> "$OUTDIR/$w.err" &
  pids+=($!)
done
echo "event=launched workers=$K t=$(date -u +%FT%TZ)"
fail=0
for p in "${pids[@]}"; do wait "$p" || fail=1; done
[ "$fail" -eq 0 ] || { echo "event=error msg=worker_failed" >&2; exit 1; }

# Combine: sum count over workers and over w, grouped by (n,h)->T(n,h); over h->a(n).
python3 - "$OUTDIR" "$MAXN" <<'PY'
import sys, glob, collections
outdir, maxn = sys.argv[1], int(sys.argv[2])
Tnh = collections.Counter(); an = collections.Counter()
for f in glob.glob(f"{outdir}/w*.out"):
    for line in open(f):
        p = line.split()
        if len(p) != 4:
            continue
        n, w, h, c = map(int, p)
        Tnh[(n, h)] += c; an[n] += c
with open(f"{outdir}/triangle.txt", "w") as o:
    for n in range(1, maxn + 1):
        for h in range(1, n + 1):
            if Tnh[(n, h)]:
                o.write(f"tri {h} {n} {Tnh[(n,h)]}\n")
with open(f"{outdir}/an.txt", "w") as o:
    for n in range(1, maxn + 1):
        o.write(f"{n} {an[n]}\n")
print("a(n):")
for n in range(1, maxn + 1):
    print(f"  a({n}) = {an[n]}")
PY
echo "event=done tool=g2_campaign a=$MAXN t=$(date -u +%FT%TZ)"
