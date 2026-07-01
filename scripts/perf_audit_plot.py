#!/usr/bin/env python3
# perf_audit_plot.py -- plot CPU/disk/memory/run-queue metrics vs time for the
# dalby perf-audit probe (results/dalby-perf-audit.md). Reads the raw
# vmstat/iostat/mpstat logs pulled from dalby's /tmp/perfaudit_logs and the
# engine's own orchestrate.log, and produces one PNG with aligned time series.
#
# Usage: python3.13 scripts/perf_audit_plot.py <logdir> <out.png>
import sys
import re
import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SAMPLE_INTERVAL_S = 2


def parse_mpstat(path):
    times, busy = [], []
    with open(path) as f:
        for line in f:
            m = re.match(r"(\d{2}:\d{2}:\d{2}) (AM|PM)\s+all\s+([\d.]+)", line)
            if not m:
                continue
            t = datetime.datetime.strptime(f"{m.group(1)} {m.group(2)}", "%I:%M:%S %p")
            usr = float(m.group(3))
            idle = float(line.split()[-1])
            times.append(t)
            busy.append(100.0 - idle)
    return times, busy


def parse_vmstat(path):
    rows = []
    with open(path) as f:
        lines = f.readlines()
    for line in lines[2:]:
        parts = line.split()
        if len(parts) < 17:
            continue
        try:
            r = int(parts[0])
            free_kb = int(parts[3])
        except ValueError:
            continue
        rows.append((r, free_kb))
    return rows


def parse_iostat(path):
    # blocks separated by blank lines; each block has an avg-cpu header/line
    # pair, then per-device rows. We want md3 (the RAID1 root) %util (last col).
    util = []
    with open(path) as f:
        block_lines = []
        for line in f:
            line = line.rstrip("\n")
            if line.strip() == "":
                # process block
                for bl in block_lines:
                    if bl.startswith("md3"):
                        parts = bl.split()
                        try:
                            util.append(float(parts[-1]))
                        except ValueError:
                            pass
                block_lines = []
                continue
            block_lines.append(line)
    return util


def parse_orchestrate_heights(path):
    # returns list of (line_index_fraction, height) for event=column lines,
    # used only to find where each height's column-sweep starts/ends in file
    # order (proxy for real time, since the log is append-ordered).
    events = []
    with open(path) as f:
        lines = f.readlines()
    total = len(lines)
    for i, line in enumerate(lines):
        m = re.match(r"event=column H=(\d+) col=(\d+)", line)
        if m:
            events.append((i / total, int(m.group(1)), int(m.group(2))))
    return events


def main():
    logdir, outpng = sys.argv[1], sys.argv[2]

    mp_times, mp_busy = parse_mpstat(f"{logdir}/mpstat.log")
    vm_rows = parse_vmstat(f"{logdir}/vmstat.log")
    io_util = parse_iostat(f"{logdir}/iostat.log")

    t0 = mp_times[0]
    mp_secs = [(t - t0).total_seconds() for t in mp_times]
    total_s = mp_secs[-1]

    vm_secs = [i * SAMPLE_INTERVAL_S for i in range(len(vm_rows))]
    vm_r = [r for r, _ in vm_rows]
    vm_free_gb = [f / 1024 / 1024 for _, f in vm_rows]

    io_secs = [i * SAMPLE_INTERVAL_S for i in range(len(io_util))]

    events = parse_orchestrate_heights(f"{logdir}/orchestrate.log")
    # mark the first column of each height as a vertical line, positioned by
    # fractional offset into the run (proxy for real time).
    height_starts = {}
    for frac, h, col in events:
        if h not in height_starts:
            height_starts[h] = frac * total_s

    fig, axes = plt.subplots(4, 1, figsize=(13, 12), sharex=True)

    ax = axes[0]
    ax.plot(mp_secs, mp_busy, color="tab:blue", linewidth=0.8)
    ax.set_ylabel("CPU busy %\n(mpstat, all cores)")
    ax.set_ylim(0, 105)
    ax.axhline(79.3, color="gray", linestyle=":", linewidth=1, label="run mean 79.3%")
    ax.legend(loc="lower left", fontsize=8)

    ax = axes[1]
    ax.plot(vm_secs, vm_r, color="tab:orange", linewidth=0.8)
    ax.set_ylabel("run queue (r)\n(vmstat)")
    ax.axhline(80, color="gray", linestyle=":", linewidth=1, label="80 cores")
    ax.legend(loc="upper left", fontsize=8)

    ax = axes[2]
    ax.plot(io_secs, io_util, color="tab:red", linewidth=0.8)
    ax.set_ylabel("md3 (RAID1) %util\n(iostat)")
    ax.set_ylim(0, 100)

    ax = axes[3]
    ax.plot(vm_secs, vm_free_gb, color="tab:green", linewidth=0.8)
    ax.set_ylabel("free mem (GB)\n(vmstat)")
    ax.set_xlabel("seconds since run start")

    for h, s in height_starts.items():
        for ax in axes:
            ax.axvline(s, color="black", linestyle="--", linewidth=0.5, alpha=0.4)
        axes[0].text(s, 102, f"H{h}", fontsize=7, rotation=0, ha="center")

    fig.suptitle(
        "dalby perf-audit probe: maxn=24 heights 1-15, rev 5fadde3, "
        f"wall={total_s:.0f}s, mean util=79.3%"
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(outpng, dpi=130)
    print(f"wrote {outpng}")


if __name__ == "__main__":
    main()
