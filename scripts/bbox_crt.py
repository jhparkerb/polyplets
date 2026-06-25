#!/usr/bin/env python3
# bbox_crt.py N [hmax] -- EXACT bounding-box-stratified king-polyplet counts B_{H,W}(n)
# via CRT over 3 primes near 2^31 (product ~9.9e27 > a(n) for n<=~32, so each entry is
# recovered exactly). Runs build/tma_bbox --only-height h --bbox for h=1..hmax (default N)
# at each prime and CRTs each (H,W,n) cell.
#
# NOTE (measured): for polyplets this is NOT a speedup for a(n) -- king diagonals span
# H x W with only max(H,W) cells, so min(H,W) is unbounded and the tall sweeps can't be
# skipped (verified: half-height reconstruction of a(12) misses the both-large block).
# This just produces the exact 2-D refinement table. Cost ~ a(N) itself, so keep N modest.
#
# MACHINE: gympie (local), serial, <=10 cores idle. USAGE: scripts/bbox_crt.py 14
import subprocess, sys, os
from functools import reduce

N = int(sys.argv[1])
HMAX = int(sys.argv[2]) if len(sys.argv) > 2 else N
PRIMES = [2147483647, 2147483629, 2147483587]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMA = os.path.join(ROOT, "build/tma_bbox")

def run(p, h):
    out = subprocess.run([TMA, "square8", str(N), "--only-height", str(h),
                          "--modp", str(p), "--bbox"],
                         capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:  # never sum a crashed sweep as zero (the wrong-a(n) bug class)
        sys.exit(f"tma_bbox failed (rc={out.returncode}) h={h} p={p}: {out.stderr[:200]}")
    d = {}
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        H, W, n, v = map(int, parts)
        d[(H, W, n)] = v
    return d

tabs = []
for p in PRIMES:
    t = {}
    for h in range(1, HMAX + 1):
        t.update(run(p, h))
        print(f"  prime {p} height {h} done ({len(t)} cells)", file=sys.stderr, flush=True)
    tabs.append(t)

M = reduce(lambda a, b: a * b, PRIMES)
def crt(rs):
    x = 0
    for r, m in zip(rs, PRIMES):
        Mi = M // m
        x += r * Mi * pow(Mi, -1, m)
    return x % M

keys = sorted(set().union(*[set(t) for t in tabs]))
exact = {k: crt([t.get(k, 0) for t in tabs]) for k in keys}

out = os.path.join(ROOT, f"results/bbox_polyplets_n{N}_exact.txt")
total_by_n = {}
with open(out, "w") as f:
    f.write(f"# Exact bounding-box-stratified king-polyplets (refines A006770).\n")
    f.write(f"# B_{{H,W}}(n) = # polyplets, n cells, height EXACTLY H, width EXACTLY W.\n")
    f.write(f"# CRT over 3 primes near 2^31 (exact for n<=~32). H<={HMAX} swept; H>{HMAX} via\n")
    f.write(f"# transpose symmetry B_{{H,W}}=B_{{W,H}}. columns: H W n count\n")
    for k in keys:
        H, W, n = k
        f.write(f"{H} {W} {n} {exact[k]}\n")
        total_by_n[n] = total_by_n.get(n, 0) + exact[k]
print(f"wrote {out} ({len(keys)} cells)")
# self-check: sum over the full (symmetric) table at each n == a(n)
for n in sorted(total_by_n):
    # if HMAX<N we only have H<=HMAX rows; full a(n) needs the transpose too -- report raw
    print(f"  n={n}: sum of emitted cells = {total_by_n[n]}")
