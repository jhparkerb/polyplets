#!/usr/bin/env python3
# profile_concurrency.py PPID LOGFILE OUTFILE
# Samples (every 1s) how many map_worker/merge_worker children an orchestrate
# PID has alive, tagging each sample with the last H/col/round seen in LOGFILE.
# Real-time concurrency timeline -- answers WHEN cores go idle within a
# column, not just the aggregate wall/cpu cost_profile.tsv already has.
import subprocess, sys, time, re, os

ppid, logfile, outfile = sys.argv[1], sys.argv[2], sys.argv[3]

tag_re = re.compile(r'H=(\d+) col=(\d+) round=(\S+)')

last_h, last_col, last_round = "-", "-", "-"
logpos = 0

with open(outfile, "w") as out:
    out.write("epoch\tmap_workers\tmerge_workers\tH\tcol\tround\n")
    while True:
        r = subprocess.run(["ps", "--ppid", ppid, "-o", "comm="],
                            capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            if not os.path.exists(f"/proc/{ppid}"):
                break
        lines = r.stdout.split()
        nmap = sum(1 for c in lines if "map_worker" in c)
        nmerge = sum(1 for c in lines if "merge_worker" in c)

        if os.path.exists(logfile):
            with open(logfile) as f:
                f.seek(logpos)
                chunk = f.read()
                logpos = f.tell()
            for m in tag_re.finditer(chunk):
                last_h, last_col, last_round = m.group(1), m.group(2), m.group(3)

        out.write(f"{time.time():.1f}\t{nmap}\t{nmerge}\t{last_h}\t{last_col}\t{last_round}\n")
        out.flush()
        time.sleep(1)
