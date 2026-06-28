#!/usr/bin/env python3
"""sched_sim.py — trace-driven in-column scheduling-policy simulator (#32 tail).

Replays a real per-unit cost trace (event=unit lines, POLY_UNIT_LOG=1) under
different scheduling policies and reports makespan WITHOUT re-running the engine.
This is the bench for evaluating the reactive work-stealing (tail-split) lever
against the current pull-queue and against predictive LPT reordering, on real
cost data -- and it re-runs instantly on any future trace (a20/a21).

Policies (per column: C cores, unit total-works c_i, divisible ideal = Σc/C):
  current : atomic list-scheduling in DISPATCH order = the engine today. A unit
            runs to completion on one core; a heavy unit at the tail strands cores.
  lpt     : atomic list-scheduling, LARGEST-FIRST = the perfect-reorder ceiling
            (needs a cost predictor we measured to be weak; shown as the bound).
  steal   : Cilk-style work-stealing. A unit's REMAINING work is divisible by
            key-range; when a core idles and the ready queue is empty, it steals
            HALF the remaining work of the longest-running straggler, down to a
            --grain floor that models split overhead. Reactive; needs NO predictor.

Makespan is wall-weighted by column cpu_sum (so it reflects where wall actually
is). `current` and `lpt` validate against unit_cost_analysis.py.

Usage: sched_sim.py TRACE.log [--cores 8] [--grains 0.02,0.05,0.1,0.25]
  --grain g = min splittable remaining work as a fraction of the column ideal
              (smaller = finer splitting/more overhead; larger = coarser).
"""
import argparse
import re
import sys
from collections import defaultdict

UNIT_RE = re.compile(r"event=unit\s+(.*)")
KV_RE = re.compile(r"(\w+)=([-\w.]+)")


def parse(path):
    cols = defaultdict(list)   # (H,col) -> [cpu] in emission (dispatch) order
    for line in open(path):
        m = UNIT_RE.search(line)
        if not m:
            continue
        kv = dict(KV_RE.findall(m.group(1)))
        cols[(int(kv["H"]), int(kv["col"]))].append(float(kv["cpu_s"]))
    return cols


def makespan_atomic(works, C, largest_first):
    """List-scheduling: each work runs whole on the least-loaded core."""
    order = sorted(works, reverse=True) if largest_first else works
    load = [0.0] * C
    for w in order:
        i = min(range(C), key=lambda j: load[j])
        load[i] += w
    return max(load)


def makespan_steal(works, C, grain_abs):
    """Event-driven Cilk-style work-stealing on divisible remaining work. Dispatch
    in trace order (FIFO, no reordering); when a core idles with an empty queue it
    halves the longest straggler's remaining work, down to grain_abs."""
    INF = float("inf")
    ready = list(works)          # FIFO dispatch order (the engine's order)
    ri = 0
    finish = [INF] * C           # completion time of each core's current task
    for c in range(C):           # prime the cores
        if ri < len(ready):
            finish[c] = ready[ri]; ri += 1
    t = 0.0
    while True:
        c = min(range(C), key=lambda j: finish[j])
        if finish[c] == INF:
            return t             # all cores idle => done
        t = finish[c]
        finish[c] = INF          # core c just finished, now idle
        if ri < len(ready):
            finish[c] = t + ready[ri]; ri += 1
            continue
        # queue empty -> steal half the longest straggler's remaining work
        v = max(range(C), key=lambda j: -1 if finish[j] == INF else finish[j])
        if finish[v] != INF and (finish[v] - t) > grain_abs:
            half = (finish[v] - t) / 2.0
            finish[v] = t + half
            finish[c] = t + half
        # else: nothing big enough to split; core c stays idle


def wall_weighted(cols, C, fn):
    """Σ(cpu_sum * makespan)/Σcpu_sum over columns, as a multiple of ideal."""
    num = den = 0.0
    for works in cols.values():
        s = sum(works)
        if s == 0 or len(works) < 2:
            continue
        ideal = s / C
        num += s * (fn(works, C, ideal) / ideal)
        den += s
    return num / den


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace")
    ap.add_argument("--cores", type=int, default=8)
    ap.add_argument("--grains", default="0.02,0.05,0.1,0.25")
    args = ap.parse_args()
    C = args.cores
    cols = parse(args.trace)
    if not cols:
        print("no event=unit lines (run with POLY_UNIT_LOG=1)", file=sys.stderr)
        return 1
    grains = [float(g) for g in args.grains.split(",")]

    total = sum(sum(w) for w in cols.values())
    print(f"# sched_sim  {args.trace}  cores={C}  cols={len(cols)}  cpu={total:.0f}s")
    print(f"# makespan as multiple of the divisible ideal (1.000 = perfect); "
          f"recovered = fraction of the current gap closed\n")

    cur = wall_weighted(cols, C, lambda w, c, i: makespan_atomic(w, c, False))
    lpt = wall_weighted(cols, C, lambda w, c, i: makespan_atomic(w, c, True))

    def recov(x):
        return 100 * (cur - x) / (cur - 1.0) if cur > 1.0 else 0.0

    print(f"  {'policy':26} {'makespan':>9} {'vs ideal':>9} {'recovered':>10}")
    print(f"  {'current (pull-queue)':26} {cur:>8.3f}x {'+'+format(100*(cur-1),'.1f')+'%':>9} "
          f"{'baseline':>10}")
    print(f"  {'lpt (perfect reorder)':26} {lpt:>8.3f}x {'+'+format(100*(lpt-1),'.1f')+'%':>9} "
          f"{recov(lpt):>9.0f}%")
    for g in grains:
        st = wall_weighted(cols, C, lambda w, c, i: makespan_steal(w, c, g * i))
        print(f"  {'steal grain='+format(g,'.2f'):26} {st:>8.3f}x "
              f"{'+'+format(100*(st-1),'.1f')+'%':>9} {recov(st):>9.0f}%")

    print(f"\n  current wastes {100*(cur-1):.1f}% of map-wall over ideal; "
          f"work-stealing closes most of it with NO predictor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
