#!/usr/bin/env python3
"""job_stats.py — post-run statistics harvest for a fold-engine sweep.

Parses the `event=column` telemetry stream from a run log and reports, per
COLUMN / per HEIGHT / per JOB: wall time, cpu-seconds, cpu utilization
(effective cores = cpu_s/wall_s), peak RSS, the map-vs-merge phase split, and
the map-unit / merge-range fan counts (the per-column worker-invocation totals,
emitted by runs built at >= the telemetry map_units/merge_ranges change; shown
as "-" for older logs).

The point is to bank actuals over many runs and build intuition for what these
values SHOULD be. Remember the cost model: a column's expense tracks its
FRONTIER size (~2^H, peaks mid-sweep), NOT the polyplet count it yields — the
tallest strip is the most expensive though it adds the fewest polyplets.

Usage:
    job_stats.py RUN.log [--cores N] [--tsv OUT.tsv] [--label NAME]

Reads a saved log (run from the repo so the file is on disk; scp remote logs in
first). --cores overrides the cores= parsed from the log header (for util%).
"""
import argparse
import re
import sys

COL_RE = re.compile(r"event=column\s+(.*)")
KV_RE = re.compile(r"(\w+)=(-?[\d.]+)")


def parse_log(path):
    cores = None
    cols = []
    with open(path) as f:
        for line in f:
            if cores is None:
                m = re.search(r"\bcores=(\d+)", line)
                if m:
                    cores = int(m.group(1))
            cm = COL_RE.search(line)
            if not cm:
                continue
            kv = {k: float(v) for k, v in KV_RE.findall(cm.group(1))}
            cols.append(kv)
    return cores, cols


def eff(cpu, wall):
    return cpu / wall if wall > 0 else 0.0


def fmt_int(kv, key):
    return str(int(kv[key])) if key in kv else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--cores", type=int, default=0)
    ap.add_argument("--tsv", default="")
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    cores, cols = parse_log(args.log)
    if args.cores:
        cores = args.cores
    if not cols:
        print(f"job_stats: no event=column lines in {args.log}", file=sys.stderr)
        return 1
    label = args.label or args.log

    # Per-column TSV (full fidelity for later analysis).
    tsv_cols = ["H", "col", "frontier_in", "frontier_out", "wall_s", "cpu_s",
                "eff_cores", "util_pct", "rss_max_mb", "map_wall_s", "merge_wall_s",
                "merge_frac", "map_units", "merge_ranges"]
    if args.tsv:
        with open(args.tsv, "w") as t:
            t.write("\t".join(tsv_cols) + "\n")
            for c in cols:
                ec = eff(c["cpu_s"], c["wall_s"])
                row = [fmt_int(c, "H"), fmt_int(c, "col"), fmt_int(c, "frontier_in"),
                       fmt_int(c, "frontier_out"), f"{c['wall_s']:.2f}", f"{c['cpu_s']:.1f}",
                       f"{ec:.2f}", f"{100*ec/cores:.1f}" if cores else "-",
                       f"{c['rss_max_mb']:.1f}", f"{c.get('map_wall_s',0):.2f}",
                       f"{c.get('merge_wall_s',0):.2f}",
                       f"{eff(c.get('merge_wall_s',0),c['wall_s']):.3f}" if c["wall_s"] > 0 else "-",
                       fmt_int(c, "map_units"), fmt_int(c, "merge_ranges")]
                t.write("\t".join(row) + "\n")

    # Per-height rollup.
    heights = {}
    for c in cols:
        h = int(c["H"])
        d = heights.setdefault(h, dict(wall=0.0, cpu=0.0, mapw=0.0, mergew=0.0,
                                       rss=0.0, n=0, munits=0, mranges=0))
        d["wall"] += c["wall_s"]; d["cpu"] += c["cpu_s"]
        d["mapw"] += c.get("map_wall_s", 0); d["mergew"] += c.get("merge_wall_s", 0)
        d["rss"] = max(d["rss"], c["rss_max_mb"]); d["n"] += 1
        d["munits"] += int(c.get("map_units", 0)); d["mranges"] += int(c.get("merge_ranges", 0))

    print(f"# job_stats: {label}    cores={cores or '?'}")
    print(f"# {len(cols)} columns over {len(heights)} heights")
    print()
    hdr = ("H", "cols", "wall_s", "wall_h", "cpu_s", "eff_cores", "util%",
           "peak_rss_mb", "merge%", "map_units", "merge_rng")
    print("{:>3} {:>5} {:>11} {:>7} {:>13} {:>9} {:>6} {:>11} {:>7} {:>9} {:>9}".format(*hdr))
    for h in sorted(heights):
        d = heights[h]
        ec = eff(d["cpu"], d["wall"])
        mf = d["mergew"] / d["wall"] * 100 if d["wall"] else 0
        print("{:>3} {:>5} {:>11.1f} {:>7.2f} {:>13.1f} {:>9.2f} {:>6.0f} {:>11.1f} {:>7.1f} {:>9} {:>9}".format(
            h, d["n"], d["wall"], d["wall"] / 3600, d["cpu"], ec,
            100 * ec / cores if cores else 0, d["rss"], mf,
            d["munits"] or "-", d["mranges"] or "-"))

    # Per-job totals.
    tot_wall = sum(c["wall_s"] for c in cols)
    tot_cpu = sum(c["cpu_s"] for c in cols)
    tot_mapw = sum(c.get("map_wall_s", 0) for c in cols)
    tot_mergew = sum(c.get("merge_wall_s", 0) for c in cols)
    peak_rss = max(c["rss_max_mb"] for c in cols)
    ec = eff(tot_cpu, tot_wall)
    munits = sum(int(c.get("map_units", 0)) for c in cols)
    mranges = sum(int(c.get("merge_ranges", 0)) for c in cols)
    # Costliest columns — where the wall actually goes.
    top = sorted(cols, key=lambda c: c["wall_s"], reverse=True)[:5]
    print()
    print("## job totals")
    print(f"wall            {tot_wall:.0f}s ({tot_wall/3600:.2f}h)")
    print(f"cpu             {tot_cpu:.0f}s ({tot_cpu/3600:.1f} cpu-h)")
    print(f"eff_cores       {ec:.2f}" + (f"  ({100*ec/cores:.0f}% of {cores})" if cores else ""))
    print(f"peak_rss        {peak_rss:.1f} MB")
    print(f"map / merge     {tot_mapw:.0f}s / {tot_mergew:.0f}s  (merge {100*tot_mergew/tot_wall:.1f}% of wall)")
    print(f"columns         {len(cols)}  (1 map + 1 merge phase each)")
    if munits or mranges:
        print(f"worker calls    {munits} map-unit + {mranges} merge-range invocations")
    print(f"costliest cols  " + ", ".join(
        f"H{int(c['H'])}c{int(c['col'])}={c['wall_s']:.0f}s" for c in top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
