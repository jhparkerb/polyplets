#!/usr/bin/env bash
# R1xR3 reach driver: exact a(n) for n<=N via fold + u32 mod-p height sweeps + CRT.
# For each prime p:  a(n) mod p = sum over heights H of B_H(n) mod p  (one sweep per (H,p),
# ~4x less RAM than the exact u64 sweep). CRT across 3 primes near 2^31 recovers exact a(n).
# Heights are independent -- this serial version is for the gate; the production version
# parallelizes the (H,p) sweeps (see scripts/an_fold_parallel.sh for the per-height pattern).
#
# USAGE: scripts/an_modp_crt.sh N [--fold|--nofold]   (default --fold)
set -uo pipefail
cd "$(dirname "$0")/.."
N="${1:?N}"; FOLD="${2:---fold}"; [ "$FOLD" = "--nofold" ] && FOLD=""
PRIMES="2147483647 2147483629 2147483587"
DIR="runs/anmodp_N$N"; mkdir -p "$DIR"; echo $$ > "$DIR/driver.pid"

for p in $PRIMES; do
  : > "$DIR/rows_$p.txt"
  for H in $(seq 1 "$N"); do
    build/tma square8 "$N" --only-height "$H" --modp "$p" $FOLD 2>/dev/null >> "$DIR/rows_$p.txt"
  done
done

python3 - "$DIR" "$N" $PRIMES <<'PYEOF'
import sys
from functools import reduce
d, N = sys.argv[1], int(sys.argv[2])
primes = [int(x) for x in sys.argv[3:]]
def crt(rs, ms):
    M = reduce(lambda a, b: a * b, ms); x = 0
    for r, m in zip(rs, ms):
        Mi = M // m; x += r * Mi * pow(Mi, -1, m)
    return x % M
amod = {p: [0] * (N + 1) for p in primes}
for p in primes:
    for ln in open(f"{d}/rows_{p}.txt"):
        x = ln.split()
        if len(x) == 2:
            n = int(x[0]); amod[p][n] = (amod[p][n] + int(x[1])) % p
for n in range(1, N + 1):
    print(n, crt([amod[p][n] for p in primes], primes))
PYEOF
