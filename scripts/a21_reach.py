#!/usr/bin/env python3
# Reach driver for a(N) with a LIVE, self-calibrated ETA -- the a(20) h20 sweep sat
# 35h on a single per-column heartbeat with a meaningless col/maxn ETA; this never
# happens here. a(N) = sum_H B_H(N), recovered exactly by CRT over 3 primes near 2^31.
# The N*3 (H,p) mod-p sweeps are independent, so we run JOBS at once.
#
# ETA model (jasonp's "max of per-sweep ETAs", self-calibrated):
#   every (H,p) sweep at a fixed height costs ~the same regardless of prime, so the
#   FIRST completion at height H calibrates the cost of that height's remaining primes.
#   Heights not yet seen fall back to a measured cost curve. The job ETA is the long
#   pole: max(remaining time of any single in-flight/queued sweep, total remaining
#   work / JOBS). No col/maxn fiction -- it is anchored to measured per-height times.
#
# USAGE: a21_reach.py [N=21] [JOBS=8]
import os
import subprocess
import sys
import time

N = int(sys.argv[1]) if len(sys.argv) > 1 else 21
JOBS = int(sys.argv[2]) if len(sys.argv) > 2 else 8
# 3rd arg = number of primes (default 3 = exact CRT; 1 = fast cost-curve calibration,
# emits a(N) mod p only -- used to measure the real per-height curve before the run).
NPRIMES = int(sys.argv[3]) if len(sys.argv) > 3 else 3
PRIMES = [2147483647, 2147483629, 2147483587][:NPRIMES]
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(HERE, f"runs/anmodp_N{N}")
TMA = os.path.join(HERE, "build/tma")

# Measured N=21 single-prime fallback curve (seconds), only used until a height
# self-calibrates from its own first completion. Heights above the measured range
# extrapolate the observed ~5x/step climb; the model is replaced by reality fast.
FALLBACK = {h: 0.2 for h in range(1, 9)}
FALLBACK.update({9: 1.7, 10: 8.6, 11: 45.0})
for h in range(12, N + 1):
    FALLBACK[h] = FALLBACK[h - 1] * 5.0  # climbs, then the real time corrects it
FALLBACK[N] = 0.05  # top height H==N is the 3^(N-1) closed form -- instant

os.makedirs(DIR, exist_ok=True)
for f in os.listdir(DIR):  # fresh: stale rows_*/hb_* would double-count or mislead
    if f.startswith(("rows_p", "hb_p")):
        os.remove(os.path.join(DIR, f))
with open(os.path.join(DIR, "driver.pid"), "w") as f:
    f.write(str(os.getpid()) + "\n")

# Build the task list. Interleave primes within each height so a height calibrates
# its siblings quickly; ascending height keeps the cheap ones first.
tasks = [(H, p) for H in range(1, N + 1) for p in PRIMES]
TOTAL = len(tasks)


def launch(H, p):
    out = open(os.path.join(DIR, f"rows_p{p}_H{H}.txt"), "w")
    hb = open(os.path.join(DIR, f"hb_p{p}_H{H}.log"), "w")
    proc = subprocess.Popen(
        [TMA, "square8", str(N), "--only-height", str(H), "--modp", str(p),
         "--fold", "--blocked", "8"], stdout=out, stderr=hb)
    return proc, out, hb


t0 = time.time()
print(f">>> a({N}) reach: {TOTAL} sweeps ({N} heights x {len(PRIMES)} primes), "
      f"JOBS={JOBS}, pid={os.getpid()}  {time.strftime('%Y-%m-%dT%H:%M:%S%z')}",
      flush=True)

running = {}          # (H,p) -> (proc, out, hb, start)
done_dur = {}         # H -> list of measured durations (one per finished prime)
started = {}          # (H,p) -> start time (for in-flight remaining calc)
idx, completed = 0, 0
last_print = 0.0


def predict(H):
    if H in done_dur:
        return sum(done_dur[H]) / len(done_dur[H])
    return FALLBACK.get(H, 1.0)


def eta_seconds():
    now = time.time()
    # remaining time of in-flight sweeps (their predicted dur minus elapsed, >=0)
    inflight = [max(0.0, predict(H) - (now - st)) for (H, _p), st in started.items()
                if (H, _p) in running]
    queued = [predict(H) for (H, p) in tasks[idx:]]
    pole = max(inflight + queued + [0.0])
    work_remaining = sum(inflight) + sum(queued)
    return max(pole, work_remaining / JOBS)


while idx < TOTAL or running:
    while idx < TOTAL and len(running) < JOBS:
        H, p = tasks[idx]
        proc, out, hb = launch(H, p)
        running[(H, p)] = (proc, out, hb)
        started[(H, p)] = time.time()
        idx += 1
    # reap finished
    for key in list(running):
        proc, out, hb = running[key]
        if proc.poll() is not None:
            out.close(); hb.close()
            H, p = key
            dur = time.time() - started[key]
            done_dur.setdefault(H, []).append(dur)
            completed += 1
            del running[key]
    now = time.time()
    if now - last_print >= 5.0:
        last_print = now
        el = now - t0
        eta = eta_seconds()
        runlist = ",".join(f"H{H}@{int(now - started[(H, p)])}s"
                           for (H, p) in sorted(running)) or "-"
        fin = time.strftime("%H:%M:%S", time.localtime(now + eta))
        print(f"    [{int(el):5d}s] done {completed:2d}/{TOTAL}  "
              f"running: {runlist}  ETA ~{int(eta)}s (~{fin})", flush=True)
    time.sleep(0.5)

el = time.time() - t0
if NPRIMES == 1:  # calibration mode: report the measured per-height cost curve
    print(f">>> calibration curve (N={N}, single prime, {int(el)}s total):", flush=True)
    for H in sorted(done_dur):
        print(f"    H={H:2d}  {sum(done_dur[H])/len(done_dur[H]):8.2f}s", flush=True)
print(f">>> all {TOTAL} sweeps done in {int(el)}s; CRT-combining  "
      f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')}", flush=True)

# CRT combine -> exact a(1..N) diagonal
cc = subprocess.run(
    [sys.executable, os.path.join(HERE, "scripts/crt_combine.py"), DIR, str(N)]
    + [str(p) for p in PRIMES], capture_output=True, text=True)
sys.stdout.write(cc.stdout)
a = {}
for ln in cc.stdout.splitlines():
    x = ln.split()
    if len(x) == 2:
        a[int(x[0])] = int(x[1])

# built-in correctness gate: the diagonal includes already-confirmed lower terms.
# Only meaningful with the full 3-prime CRT (exact); with fewer primes the values
# are mod-p, so skip the gate (this is a cost-curve / mod-p calibration pass).
KNOWN = {12: 257105146, 20: 1025573519362016}
EXACT = len(PRIMES) >= 3
ok = True
if EXACT:
    for n, v in KNOWN.items():
        if n <= N:
            if a.get(n) == v:
                print(f"    gate ok: a({n}) = {v}", flush=True)
            else:
                print(f"!!! GATE FAIL a({n})={a.get(n)} != {v}", flush=True)
                ok = False
else:
    print(f"    (single/2-prime mode: values are mod p, gate skipped)", flush=True)

tag = ("VALIDATED" if ok else "UNVALIDATED -- gate fail") if EXACT else "mod-p only"
print(f">>> a({N}) = {a.get(N)}   [{tag}]", flush=True)
if N - 1 in a and a.get(N - 1):
    print(f">>> ratio a({N})/a({N-1}) = {a[N] / a[N-1]:.4f}", flush=True)
