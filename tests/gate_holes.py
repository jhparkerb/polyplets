#!/usr/bin/env python3
"""gate_holes.py — T5.4 gate: new-system holes distribution vs tma_holes oracle.

Runs build/ns/gate_holes --maxn N and build/tma_holes square8 N --holes
--per-height, then checks byte-identical (H, n, k, count) tuples.
"""

import subprocess
import sys

MAXN = int(sys.argv[1]) if len(sys.argv) > 1 else 12


def run_oracle(maxn):
    """Run tma_holes and return sorted list of (H, n, k, count) tuples."""
    cmd = ["./build/tma_holes", "square8", str(maxn), "--holes", "--per-height"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    rows = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) == 4:
            H, n, k, count = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            rows.append((H, n, k, count))
    return sorted(rows)


def run_new(maxn):
    """Run gate_holes binary and return sorted list of (H, n, k, count) tuples."""
    cmd = ["./build/ns/gate_holes", "--maxn", str(maxn)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    rows = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) == 4:
            H, n, k, count = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            rows.append((H, n, k, count))
    return sorted(rows)


oracle = run_oracle(MAXN)
new    = run_new(MAXN)

if oracle == new:
    print(f"gate_holes PASS  (maxn={MAXN}, {len(oracle)} (H,n,k) tuples matched)")
    sys.exit(0)

# Report mismatches.
oracle_set = set(oracle)
new_set    = set(new)
only_oracle = sorted(oracle_set - new_set)
only_new    = sorted(new_set    - oracle_set)

print(f"gate_holes FAIL  (maxn={MAXN})")
for tup in only_oracle[:20]:
    print(f"  MISSING in new   H={tup[0]} n={tup[1]} k={tup[2]} count={tup[3]}")
for tup in only_new[:20]:
    print(f"  EXTRA   in new   H={tup[0]} n={tup[1]} k={tup[2]} count={tup[3]}")
if len(only_oracle) > 20 or len(only_new) > 20:
    print(f"  ... ({len(only_oracle)} missing, {len(only_new)} extra total)")
sys.exit(1)
