#!/usr/bin/env bash
# Gate for build/perimeter_defect: the pruned search must reproduce build/g2's
# site-perimeter census cell for cell, on both lattices, before any number it
# produces past g2's reach is believed.  docs/perimeter-defect-plan.md, Task B.
#
# Three checks, all fail-closed:
#   A  pruned counts == g2 --siteperim, for every (n, k) with k <= KMAX
#   B  pruned == unpruned on the same range (isolates the prune from the rewrite)
#   C  the (k, c, H) marginals sum back to the (n, k) totals
set -euo pipefail
cd "$(dirname "$0")/.."

WORK=${WORK:-$(mktemp -d)}
NSQ=${NSQ:-13}          # g2 square4 --siteperim is cheap to here
NKI=${NKI:-11}          # square8 costs 7.4x per n; 11 is ~3s
KMAX=${KMAX:-5}
fail=0

make -s build/g2 build/perimeter_defect

for spec in "square4 $NSQ" "square8 $NKI"; do
  set -- $spec
  lat=$1 n=$2
  echo "== $lat, n <= $n, k <= $KMAX =="

  ./build/g2 "$lat" "$n" --siteperim > "$WORK/g2.$lat" 2>/dev/null
  ./build/perimeter_defect "$lat" "$n" "$KMAX" > "$WORK/pd.$lat" 2>"$WORK/pd.$lat.log"
  ./build/perimeter_defect "$lat" "$n" "$KMAX" --no-prune \
      > "$WORK/np.$lat" 2>"$WORK/np.$lat.log"

  python3 - "$lat" "$n" "$KMAX" "$WORK/g2.$lat" "$WORK/pd.$lat" "$WORK/np.$lat" <<'PY' || fail=1
import sys
from collections import defaultdict
lat, n, kmax, g2f, pdf, npf = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), *sys.argv[4:]
half = 2 if lat == "square4" else 4

want = defaultdict(int)
for line in open(g2f):
    p = line.split()
    if len(p) == 3 and p[0].isdigit():
        nn, pp, c = map(int, p)
        k = half * (nn + 1) - pp
        if 0 <= k <= kmax:
            want[(nn, k)] += c

def load(path):
    tot, full = defaultdict(int), defaultdict(int)
    for line in open(path):
        p = line.split()
        if len(p) == 5 and p[0].isdigit():
            nn, k, c, H, v = map(int, p)
            tot[(nn, k)] += v
            full[(nn, k, c, H)] += v
    return tot, full

got, full = load(pdf)
unp, _ = load(npf)

bad = [key for key in set(want) | set(got) if want.get(key, 0) != got.get(key, 0)]
if bad:
    print(f"  A FAIL {lat}: {len(bad)} cells differ from g2, e.g. "
          f"{[(k, want.get(k,0), got.get(k,0)) for k in sorted(bad)[:5]]}")
    sys.exit(1)
print(f"  A ok  {len(want)} (n,k) cells match g2 --siteperim")

bad = [key for key in set(unp) | set(got) if unp.get(key, 0) != got.get(key, 0)]
if bad:
    print(f"  B FAIL {lat}: prune changed {len(bad)} cells, e.g. {sorted(bad)[:5]}")
    sys.exit(1)
print(f"  B ok  pruned == unpruned")

if sum(full.values()) != sum(got.values()):
    print(f"  C FAIL {lat}: (c,H) marginals do not sum back")
    sys.exit(1)
print(f"  C ok  (k,c,H) marginals sum to the (n,k) totals")
PY
done

if [ "$fail" -ne 0 ]; then echo "GATE FAILED"; exit 1; fi
echo "GATE PASSED"
