#!/usr/bin/env python3
# a22_forecast_analyze.py -- build the a(22)-on-dalby runtime forecast from measured
# per-height reach sweeps.
#
# DATA SOURCES (per N, dir runs/anmodp_N{N}/):
#   hb_p{p}_H{H}.log  -> peak_states, cpu_s (getrusage; reliable for serial AND MT)
#   rows_p{p}_H{H}.txt mtime -> per-height WALL for a SEQUENTIAL (--jobs 1) run
#       (the obs wall_s field is a known 0.0 bug on the MT path; mtime deltas are truth).
#
# MODEL: the production a(22) wall on dalby = the single heaviest height-sweep run at the
#   MT knee, because 21x3=63 independent sweeps < dalby's ~76 effective cores -> they all
#   run concurrently and the wall is the long pole, not the sum (their own perf docs).
#   So the forecast = max_H wall_MT(H, N=22). We measure wall_MT for the heights the climb
#   reaches and extrapolate the rest with the measured state-growth + per-state-cost laws,
#   cross-checked against the pole SHAPE seen at smaller N (18, 20, 21).
#
# USAGE: scripts/a22_forecast_analyze.py [climb_N=22] [climb_threads=26]
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIMB_N = int(sys.argv[1]) if len(sys.argv) > 1 else 22

def load_N(N):
    """Return {H: {'states':int,'cpu':float,'mtime':float,'result':str}} for run dir N."""
    d = os.path.join(ROOT, f"runs/anmodp_N{N}")
    out = {}
    for f in glob.glob(os.path.join(d, "hb_p*_H*.log")):
        m = re.search(r"_H(\d+)\.log$", f)
        if not m: continue
        H = int(m.group(1))
        txt = open(f).read()
        dn = [l for l in txt.splitlines() if "event=done" in l]
        if not dn: continue
        rec = out.setdefault(H, {})
        cs = re.search(r"cpu_s=([0-9.]+)", dn[-1]);  rec['cpu'] = float(cs.group(1)) if cs else None
        ps = re.search(r"peak_states=(\d+)", dn[-1]); rec['states'] = int(ps.group(1)) if ps else None
        rr = re.search(r"result=(\d+)", dn[-1]);      rec['result'] = rr.group(1) if rr else None
    # wall via rows mtime (sequential runs only)
    for f in glob.glob(os.path.join(d, "rows_p*_H*.txt")):
        m = re.search(r"_H(\d+)\.txt$", f)
        if not m: continue
        H = int(m.group(1))
        if os.path.getsize(f) > 0 and H in out:
            out[H]['mtime'] = os.path.getmtime(f)
    return out

def seq_walls(data):
    """Per-height wall = mtime[H] - mtime[H-1] for a sequential climb (low->high)."""
    Hs = sorted(h for h in data if 'mtime' in data[h])
    walls = {}
    for i, H in enumerate(Hs):
        if i == 0: continue
        walls[H] = data[H]['mtime'] - data[Hs[i-1]]['mtime']
    return walls

def fmt_hms(s):
    s = int(s); return f"{s//3600}h{(s%3600)//60:02d}m{s%60:02d}s"

print(f"=== a({CLIMB_N}) forecast analysis  (root {ROOT}) ===\n")
allN = {}
for N in (16, 18, 20, 21, CLIMB_N):
    data = load_N(N)
    if not data: continue
    allN[N] = data
    walls = seq_walls(data)
    print(f"--- N={N}: {len(data)} heights measured ---")
    print(f"{'H':>3} {'states':>12} {'st_ratio':>8} {'cpu_s':>10} {'wall_s':>10} {'cpu/st_us':>10}")
    prev = None
    for H in sorted(data):
        st = data[H].get('states'); cpu = data[H].get('cpu'); w = walls.get(H)
        r = (st/prev) if (st and prev) else None
        cps = (cpu/st*1e6) if (cpu and st) else None
        print(f"{H:>3} {st if st else '-':>12} "
              f"{(f'{r:.3f}' if r else '-'):>8} "
              f"{(f'{cpu:.1f}' if cpu is not None else '-'):>10} "
              f"{(fmt_hms(w) if w else '-'):>10} "
              f"{(f'{cps:.1f}' if cps else '-'):>10}")
        if st: prev = st
    # pole location at this N (max states height measured)
    pole = max((H for H in data if data[H].get('states')),
               key=lambda h: data[h]['states'], default=None)
    if pole:
        print(f"    heaviest measured height: H={pole} "
              f"(states={data[pole]['states']}, frac={pole/N:.2f})")
    print()

# --- forecast: extrapolate N=22 wall curve to the pole ---
if CLIMB_N in allN:
    d = allN[CLIMB_N]; walls = seq_walls(d)
    meas = sorted(h for h in walls if walls[h] > 0.5)
    if len(meas) >= 3:
        print("=== N=22 wall extrapolation ===")
        # geometric wall ratio from the last 3 clean measured heights
        last = meas[-3:]
        ratios = [walls[last[i+1]]/walls[last[i]] for i in range(len(last)-1)]
        rbar = sum(ratios)/len(ratios)
        topH = meas[-1]
        print(f"measured to H={topH}; recent wall ratios {['%.2f'%x for x in ratios]} "
              f"mean={rbar:.2f}")
        # NOTE: rbar likely OVERSTATES the top because states roll off near H->N
        # (cell-budget prune). The smaller-N maps give the rolloff; applied by hand in
        # the doc. Here print a naive geometric projection as an UPPER bound.
        proj = dict(walls); w = walls[topH]
        for H in range(topH+1, CLIMB_N):  # up to N-1; H=N is the 3^(N-1) closed form
            w *= rbar; proj[H] = w
        pole_w = max(proj.values())
        pole_H = max(proj, key=proj.get)
        total = sum(proj.values())
        print(f"naive-geometric pole: H={pole_H} wall={fmt_hms(pole_w)} (UPPER bound)")
        print(f"  full-MT schedule wall ~ pole = {fmt_hms(pole_w)}")
        print(f"  serial-concurrent-ish total (sum) = {fmt_hms(total)}")
