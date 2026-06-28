#!/usr/bin/env python3
"""Analyze per-unit map costs (event=unit traces) to decide whether LPT-ordering
of map units is feasible -- i.e. whether per-unit cost is (a) imbalanced enough to
be worth reordering and (b) PREDICTABLE a priori (the open question in #32/LPT).

Reads a run log produced with POLY_UNIT_LOG=1. For each height it reports:

  imbalance   -- per-column cost spread (CV, p90/p50, tail = max/mean). Near 0 =>
                 units are equal-cost => LPT cannot help, idea is moot.
  predictY    -- Spearman rank-correlation of per-unit cost between CONSECUTIVE
                 columns at the same unit position. High => the previous column
                 predicts this one => cost is effectively KNOWN a priori => the
                 "cost unknown" catch dissolves.
  makespan    -- list-schedule the column's units onto C cores under three orders
                 and report wall vs the divisible ideal (sum/C):
                   as-emitted   : the current dispatch order (baseline)
                   LPT-prev     : sort by the PREVIOUS column's cost (realizable)
                   LPT-oracle   : sort by THIS column's true cost (upper bound)
                 The gap between as-emitted and LPT-prev is the achievable win;
                 the gap between LPT-prev and LPT-oracle is what prediction leaves
                 on the table (closed by reactive tail-split).

Usage:  unit_cost_analysis.py RUN.log [--cores 8]
"""
import argparse
import re
import statistics as st
import sys
from collections import defaultdict

UNIT_RE = re.compile(r"event=unit\s+(.*)")
KV_RE = re.compile(r"(\w+)=([-\w.]+)")


def parse(path):
    # (H, col) -> list of dicts in emission order
    cols = defaultdict(list)
    for line in open(path):
        m = UNIT_RE.search(line)
        if not m:
            continue
        kv = dict(KV_RE.findall(m.group(1)))
        cols[(int(kv["H"]), int(kv["col"]))].append({
            "u": int(kv["u"]),
            "cpu": float(kv["cpu_s"]),
            "out": int(kv["out_records"]),
        })
    return cols


def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        for rank, i in enumerate(order):
            r[i] = rank
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else float("nan")


def list_schedule(costs, C):
    """Greedy list scheduling: assign each cost (in given order) to the least-loaded
    core. Returns makespan (max core load)."""
    load = [0.0] * C
    for c in costs:
        i = load.index(min(load))
        load[i] += c
    return max(load)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--cores", type=int, default=8)
    args = ap.parse_args()
    C = args.cores

    cols = parse(args.log)
    if not cols:
        print("no event=unit lines (run with POLY_UNIT_LOG=1)", file=sys.stderr)
        return 1

    heights = sorted({H for (H, _) in cols})
    print(f"# unit-cost analysis  cores={C}  heights={heights[0]}..{heights[-1]}")
    print(f"# {'H':>2} {'col':>3} {'units':>5} {'cpu_sum':>9} {'CV':>5} "
          f"{'p90/p50':>7} {'tail':>5} {'predY':>6} {'cpu~out':>7} "
          f"{'as-emit':>8} {'LPTprev':>8} {'LPTora':>8}")

    prev_by_pos = {}   # H -> {u: cpu} from previous column
    agg = defaultdict(list)
    for H in heights:
        hcols = sorted(c for (h, c) in cols if h == H)
        prev_by_pos.pop(H, None)
        for col in hcols:
            units = cols[(H, col)]
            cpu = [u["cpu"] for u in units]
            out = [u["out"] for u in units]
            n = len(cpu)
            if n < 2 or sum(cpu) == 0:
                prev_by_pos[H] = {u["u"]: u["cpu"] for u in units}
                continue
            mean = sum(cpu) / n
            cv = (st.pstdev(cpu) / mean) if mean else 0.0
            srt = sorted(cpu)
            p50 = srt[n // 2]
            p90 = srt[min(n - 1, int(0.9 * n))]
            tail = max(cpu) / mean
            cpu_out = spearman(cpu, out)

            # predictability vs previous column at same unit position u
            prev = prev_by_pos.get(H, {})
            common = [u for u in units if u["u"] in prev]
            predY = float("nan")
            if len(common) >= 3:
                predY = spearman([u["cpu"] for u in common],
                                 [prev[u["u"]] for u in common])

            ideal = sum(cpu) / C
            ms_emit = list_schedule(cpu, C) / ideal
            ms_ora = list_schedule(sorted(cpu, reverse=True), C) / ideal
            # LPT-prev: order this column's units by the previous column's cost
            if prev:
                order = sorted(units, key=lambda u: -prev.get(u["u"], 0.0))
                ms_prev = list_schedule([u["cpu"] for u in order], C) / ideal
            else:
                ms_prev = float("nan")

            print(f"  {H:>2} {col:>3} {n:>5} {sum(cpu):>9.2f} {cv:>5.2f} "
                  f"{p90/p50 if p50 else 0:>7.1f} {tail:>5.1f} {predY:>6.2f} "
                  f"{cpu_out:>7.2f} {ms_emit:>7.2f}x {ms_prev:>7.2f}x {ms_ora:>7.2f}x")
            agg["cv"].append(cv)
            agg["tail"].append(tail)
            if predY == predY:   # not NaN
                agg["predY"].append(predY)
            agg["emit"].append(ms_emit)
            if ms_prev == ms_prev:
                agg["prev"].append(ms_prev)
            agg["ora"].append(ms_ora)
            # wall-weighted bookkeeping: (cpu_sum, emit, prev, ora, floor) per
            # column, weighted by where the wall actually is. floor = heaviest unit
            # / ideal: if >1, one atomic unit outlasts a perfectly packed column,
            # so reordering CANNOT help and only splitting (work-stealing) can.
            straggler_floor = max(cpu) / ideal
            agg["wrows"].append((sum(cpu), ms_emit, ms_prev, ms_ora, straggler_floor))
            prev_by_pos[H] = {u["u"]: u["cpu"] for u in units}

    def med(k):
        return st.median(agg[k]) if agg[k] else float("nan")
    print()
    print("## medians across all columns")
    print(f"  imbalance:   CV={med('cv'):.2f}   tail(max/mean)={med('tail'):.1f}x")
    print(f"  predictY:    prev-column rank-corr={med('predY'):.2f}")
    print(f"  makespan/ideal:  as-emitted={med('emit'):.2f}x  "
          f"LPT-prev={med('prev'):.2f}x  LPT-oracle={med('ora'):.2f}x")
    print()
    print("  read: if predictY high and LPT-prev << as-emitted, cost is predictable")
    print("        and LPT-ordering wins; if LPT-prev ~ as-emitted, prediction fails")
    print("        and the lever is reactive tail-split, not a-priori ordering.")

    # Wall-weighted: weight each column's makespan ratio by its cpu_sum, so the
    # numbers reflect where the wall actually is (not the many cheap columns).
    wrows = agg["wrows"]
    W = sum(w for w, *_ in wrows)
    emit_w = sum(w * e for w, e, _, _, _ in wrows) / W
    ora_w = sum(w * o for w, _, _, o, _ in wrows) / W
    floor_w = sum(w * f for w, _, _, _, f in wrows) / W
    # LPT-prev defined only on a subset; compare it to as-emitted on the SAME cols.
    pv = [(w, e, p) for w, e, p, _, _ in wrows if p == p]
    Wp = sum(w for w, _, _ in pv)
    emit_wp = sum(w * e for w, e, _ in pv) / Wp
    prev_w = sum(w * p for w, _, p in pv) / Wp
    win_ora = 100 * (emit_w - ora_w) / emit_w        # reordering only
    win_prev = 100 * (emit_wp - prev_w) / emit_wp     # realizable a-priori order
    win_split = 100 * (emit_w - 1.0) / emit_w         # splitting reaches ~ideal
    premium = 100 * (ora_w - 1.0) / emit_w            # split's gain BEYOND reorder
    print()
    print(f"## WALL-WEIGHTED (by cpu_sum, n={len(wrows)} cols, total {W:.0f} cpu-s)")
    print(f"  as-emitted (current)        = {emit_w:.3f}x ideal")
    print(f"  straggler floor (max/ideal) = {floor_w:.3f}x   "
          f"(>1 => one unit outlasts a packed column; only splitting helps)")
    print(f"  -- reorder lever (LPT) --")
    print(f"     LPT-oracle (perfect order) = {ora_w:.3f}x  => ceiling {win_ora:.1f}% of map-wall")
    print(f"     LPT-prev (realizable)      = {prev_w:.3f}x  => realized {win_prev:.1f}%")
    print(f"  -- split lever (work-stealing) --")
    print(f"     split to ideal             = 1.000x  => ceiling {win_split:.1f}% of map-wall")
    print(f"     split premium over reorder = {premium:.1f}%  (the work-stealing-only gain)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
