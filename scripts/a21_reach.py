#!/usr/bin/env python3
# Reach driver for a(N): runs a SUBSET of the N*3 independent (H,p) mod-p sweeps on ONE
# machine, idempotently, with the production scaling config. a(N) = sum_H B_H(N),
# recovered exactly by CRT over 3 primes near 2^31.
#
# MULTI-MACHINE: run this on each box over DISJOINT --heights (each writes its own
# rows_p{p}_H{H}.txt), collect all rows into one DIR, then run once more with no
# --no-crt (all sweeps already done -> it skips them and just CRT-combines + gates).
#
# PRODUCTION CONFIG (measured, see HANDOFF): --threads 20 + --shardmult 32 + (ayr only)
# --numa "numactl --interleave=all" -> ~10x per heavy sweep. Power-of-two thread counts
# are ~2x SLOWER (architecture-independent) -- use 20. Light heights (small H) are
# sub-second: run them --threads 1-4 --jobs (many) to fill cores; heavy heights -->
# --threads 20 --jobs 1 (ayr, 32c) or 4 (dalby, 80c).
#
# ETA: self-calibrated -- each height's first finished prime sets the cost of its
# remaining primes; the job ETA is the long pole. Rough until the first heavy height
# of the run completes (no prior N=22 timings exist), then accurate.
#
# USAGE: a21_reach.py N [--heights LO-HI] [--jobs J] [--threads T] [--shardmult M]
#                       [--numa "PREFIX"] [--primes K] [--no-crt] [--fresh]
import argparse
import os
import subprocess
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("N", type=int)
ap.add_argument("--heights", default=None, help="LO-HI height window (default 1..N)")
ap.add_argument("--jobs", type=int, default=1, help="concurrent sweeps on this box")
ap.add_argument("--threads", type=int, default=20, help="threads per sweep (avoid pow2)")
ap.add_argument("--shardmult", type=int, default=32, help="TMA_SHARD_MULT")
ap.add_argument("--numa", default="", help="prefix, e.g. 'numactl --interleave=all'")
ap.add_argument("--primes", type=int, default=3, help="3=exact CRT; 1=mod-p calibration")
ap.add_argument("--no-crt", action="store_true", help="produce rows only (multi-machine)")
ap.add_argument("--fresh", action="store_true", help="wipe rows first (default: resume)")
args = ap.parse_args()

N = args.N
PRIMES = [2147483647, 2147483629, 2147483587][:args.primes]
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(HERE, f"runs/anmodp_N{N}")
TMA = os.path.join(HERE, "build/tma")
LO, HI = (int(x) for x in args.heights.split("-")) if args.heights else (1, N)
NUMA = args.numa.split()

os.makedirs(DIR, exist_ok=True)
if args.fresh:
    for f in os.listdir(DIR):
        if f.startswith(("rows_p", "hb_p")):
            os.remove(os.path.join(DIR, f))
with open(os.path.join(DIR, "driver.pid"), "w") as f:
    f.write(str(os.getpid()) + "\n")


def rows_path(H, p):
    return os.path.join(DIR, f"rows_p{p}_H{H}.txt")


def done_already(H, p):  # idempotent skip: non-empty rows file == that sweep is done
    fp = rows_path(H, p)
    return os.path.exists(fp) and os.path.getsize(fp) > 0


# this box's task list: (H,p) in the height window, minus any already complete
tasks = [(H, p) for H in range(LO, HI + 1) for p in PRIMES if not done_already(H, p)]
TOTAL = len(tasks)


def launch(H, p):
    out = open(rows_path(H, p), "w")
    hb = open(os.path.join(DIR, f"hb_p{p}_H{H}.log"), "w")
    cmd = NUMA + [TMA, "square8", str(N), "--only-height", str(H), "--modp", str(p),
                  "--fold", "--threads", str(args.threads)]
    env = dict(os.environ, TMA_SHARD_MULT=str(args.shardmult))
    return subprocess.Popen(cmd, stdout=out, stderr=hb, env=env), out, hb


t0 = time.time()
print(f">>> a({N}) reach: heights {LO}-{HI} x {len(PRIMES)} primes = {TOTAL} sweeps to "
      f"run, jobs={args.jobs} threads={args.threads} shardmult={args.shardmult} "
      f"numa='{args.numa}' pid={os.getpid()}  {time.strftime('%Y-%m-%dT%H:%M:%S%z')}",
      flush=True)

running, done_dur, started = {}, {}, {}
idx, completed = 0, 0
last_print = 0.0
FALLBACK = 60.0  # flat seed for unstarted heights; self-calibration overrides per height


def predict(H):
    if H == N:
        return 0.05  # H==N is the 3^(N-1) closed form -- instant
    if H in done_dur:
        return sum(done_dur[H]) / len(done_dur[H])
    return FALLBACK


def eta_seconds():
    now = time.time()
    inflight = [max(0.0, predict(H) - (now - st)) for (H, _p), st in started.items()
                if (H, _p) in running]
    queued = [predict(H) for (H, _p) in tasks[idx:]]
    pole = max(inflight + queued + [0.0])
    return max(pole, (sum(inflight) + sum(queued)) / args.jobs)


while idx < TOTAL or running:
    while idx < TOTAL and len(running) < args.jobs:
        H, p = tasks[idx]
        running[(H, p)] = launch(H, p)
        started[(H, p)] = time.time()
        idx += 1
    for key in list(running):
        proc, out, hb = running[key]
        if proc.poll() is not None:
            out.close(); hb.close()
            done_dur.setdefault(key[0], []).append(time.time() - started[key])
            completed += 1
            del running[key]
    now = time.time()
    if now - last_print >= 5.0 and TOTAL:
        last_print = now
        runlist = ",".join(f"H{H}@{int(now - started[(H, p)])}s"
                           for (H, p) in sorted(running)) or "-"
        eta = eta_seconds()
        print(f"    [{int(now - t0):5d}s] done {completed:2d}/{TOTAL}  running: "
              f"{runlist}  ETA ~{int(eta)}s (~{time.strftime('%H:%M:%S', time.localtime(now + eta))})",
              flush=True)
    time.sleep(0.5)

print(f">>> this box done: {completed} sweeps in {int(time.time() - t0)}s  "
      f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')}", flush=True)

if args.no_crt:
    sys.exit(0)

# CRT-combine over ALL rows present in DIR -> exact a(1..N) diagonal, then gate.
cc = subprocess.run(
    [sys.executable, os.path.join(HERE, "scripts/crt_combine.py"), DIR, str(N)]
    + [str(p) for p in PRIMES], capture_output=True, text=True)
sys.stdout.write(cc.stdout)
a = {int(x[0]): int(x[1]) for x in (ln.split() for ln in cc.stdout.splitlines())
     if len(x) == 2}

KNOWN = {12: 257105146, 14: 11208974860, 20: 1025573519362016}
EXACT = len(PRIMES) >= 3
ok = True
if EXACT:
    for n, v in KNOWN.items():
        if n <= N:
            print(f"    gate ok: a({n}) = {v}" if a.get(n) == v
                  else f"!!! GATE FAIL a({n})={a.get(n)} != {v}", flush=True)
            ok = ok and a.get(n) == v
else:
    print("    (<3 primes: values are mod p, gate skipped)", flush=True)
print(f">>> a({N}) = {a.get(N)}   "
      f"[{('VALIDATED' if ok else 'GATE FAIL') if EXACT else 'mod-p only'}]", flush=True)
if a.get(N - 1):
    print(f">>> ratio a({N})/a({N-1}) = {a[N] / a[N - 1]:.4f}", flush=True)
