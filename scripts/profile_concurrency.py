#!/usr/bin/env python3
# profile_concurrency.py PPID LOGFILE OUTFILE [INTERVAL_S]
# Samples (default every 0.1s) how many map_worker/merge_worker children an
# orchestrate PID has alive, tagging each sample with the last H/col/round
# seen in LOGFILE. Real-time concurrency timeline -- answers WHEN cores go
# idle within a column, not just the aggregate wall/cpu cost_profile.tsv
# already has. Reads /proc directly (no per-sample ps fork) so it stays
# accurate at sub-second intervals on fast small-maxn diagnostic runs.
import sys, time, re, os

ppid, logfile, outfile = sys.argv[1], sys.argv[2], sys.argv[3]
interval = float(sys.argv[4]) if len(sys.argv) > 4 else 0.1

tag_re = re.compile(r'H=(\d+) col=(\d+) round=(\S+)')


def children_comms(target_ppid):
    comms = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/stat") as f:
                stat = f.read()
            # comm is the ()-wrapped 2nd field, may contain spaces/parens itself
            rp = stat.rindex(")")
            comm = stat[stat.index("(") + 1:rp]
            rest = stat[rp + 2:].split()
            ppid_field = rest[1]  # state is rest[0], ppid is rest[1]
        except (FileNotFoundError, ProcessLookupError, ValueError, IndexError):
            continue
        if ppid_field == target_ppid:
            comms.append(comm)
    return comms


last_h, last_col, last_round = "-", "-", "-"
logpos = 0

with open(outfile, "w") as out:
    out.write("epoch\tmap_workers\tmerge_workers\tH\tcol\tround\n")
    while os.path.exists(f"/proc/{ppid}"):
        comms = children_comms(ppid)
        nmap = sum(1 for c in comms if "map_worker" in c)
        nmerge = sum(1 for c in comms if "merge_worker" in c)

        if os.path.exists(logfile):
            with open(logfile) as f:
                f.seek(logpos)
                chunk = f.read()
                logpos = f.tell()
            for m in tag_re.finditer(chunk):
                last_h, last_col, last_round = m.group(1), m.group(2), m.group(3)

        out.write(f"{time.time():.3f}\t{nmap}\t{nmerge}\t{last_h}\t{last_col}\t{last_round}\n")
        out.flush()
        time.sleep(interval)
