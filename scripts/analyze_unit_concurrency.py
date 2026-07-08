#!/usr/bin/env python3
# analyze_unit_concurrency.py LOGFILE [H]
# Parses event=unit lines (POLY_UNIT_LOG=1) with start_unix+wall_s and
# reconstructs EXACT concurrency-over-time by interval overlap -- no
# sampling, so it's accurate at any scale including sub-second small-maxn
# diagnostic runs where external ps-sampling aliases or is dominated by
# fork/exec overhead noise.
import sys, re
from collections import defaultdict

logfile = sys.argv[1]
only_h = sys.argv[2] if len(sys.argv) > 2 else None

unit_re = re.compile(
    r'event=unit H=(\d+) col=(\d+) u=(\d+) .*? wall_s=([\d.]+) start_unix=([\d.]+)')

by_hcol = defaultdict(list)
with open(logfile) as f:
    for line in f:
        m = unit_re.search(line)
        if not m:
            continue
        H, col, u, wall_s, start = m.groups()
        if only_h and H != only_h:
            continue
        by_hcol[(H, col)].append((float(start), float(wall_s)))

for (H, col), units in sorted(by_hcol.items(), key=lambda kv: -sum(w for _, w in kv[1])):
    if not units:
        continue
    events = []
    for start, wall in units:
        events.append((start, 1))
        events.append((start + wall, -1))
    events.sort()
    t0 = events[0][0]
    t1 = events[-1][0]
    span = t1 - t0
    cur = 0
    area = 0.0
    last_t = t0
    peak = 0
    for t, delta in events:
        area += cur * (t - last_t)
        cur += delta
        peak = max(peak, cur)
        last_t = t
    mean_conc = area / span if span > 0 else 0
    print(f"H={H} col={col} units={len(units)} span_s={span:.3f} "
          f"mean_concurrency={mean_conc:.2f} peak_concurrency={peak}")
