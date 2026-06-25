#!/usr/bin/env python3
# a22_forecast2.py -- pole-based a(22) runtime forecast.
#
# IDEA (their own perf docs): the production wall on dalby = the single heaviest (H,p)
# sweep ("the pole"), because 21 heights x 3 primes = 63 independent sweeps all run
# concurrently on dalby's ~76 effective cores. So forecast = MT wall of the pole sweep.
#
# STEP 1 locate the pole: peak_states(H,N) is the clean, build/thread-independent signal.
#   Build it for every N we measured; the state-growth ratio r depends on SPARE CELLS
#   s = N-H (the cell-budget prune is what rolls the cost over). r(s) is ~N-invariant, so
#   we read r(s) off the small-N curves and replay it at N=22.
# STEP 2 project states(H,22) from a measured low-H anchor up through the pole.
# STEP 3 size the pole: fit wall ~ k * states (clean MT walls from the climb), or fall
#   back to cpu_s/speedup. Print pole wall = the production wall, + total CPU.
import os, re, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(N):
    d = os.path.join(ROOT, f"runs/anmodp_N{N}")
    out = {}
    for f in glob.glob(os.path.join(d, "hb_p*_H*.log")):
        H = int(re.search(r"_H(\d+)\.log$", f).group(1))
        t = open(f).read()
        dn = [l for l in t.splitlines() if "event=done" in l]
        if not dn: continue
        st = re.search(r"peak_states=(\d+)", dn[-1])
        cp = re.search(r"cpu_s=([0-9.]+)", dn[-1])
        if st: out[H] = {"states": int(st.group(1)),
                         "cpu": float(cp.group(1)) if cp else None}
    return out

NS = [15, 16, 17, 18, 20, 21, 22]
data = {N: load(N) for N in NS}
data = {N: d for N, d in data.items() if d}

print("=== peak_states(H,N) ===")
print("  H " + "".join(f"{N:>10}" for N in sorted(data)))
allH = sorted({H for d in data.values() for H in d})
for H in allH:
    row = f"{H:>3} "
    for N in sorted(data):
        v = data[N].get(H, {}).get("states")
        row += f"{v:>10}" if v else f"{'-':>10}"
    print(row)

# pole per N = argmax states (only if we have the turnover, i.e. measured up to N-1)
print("\n=== pole per N (where states peaks) ===")
for N in sorted(data):
    ds = {H: data[N][H]["states"] for H in data[N]}
    top = max(ds) if ds else 0
    if top >= N - 1:                      # we reached the top -> real pole
        pole = max(ds, key=ds.get)
        print(f"N={N}: pole H={pole} states={ds[pole]} frac={pole/N:.3f} "
              f"(measured to H={top})")
    else:
        print(f"N={N}: still rising at H={top} (states {ds[top]}); pole>frac {top/N:.2f}")

# r(s): state ratio as a function of spare cells s = N-H, pooled across N
print("\n=== state ratio r(s), s = spare cells = N-H (pooled) ===")
import collections
rs = collections.defaultdict(list)
for N in data:
    for H in data[N]:
        if H - 1 in data[N]:
            s = N - H
            rs[s].append(data[N][H]["states"] / data[N][H - 1]["states"])
def med(x): x = sorted(x); return x[len(x)//2]
rbar = {}
for s in sorted(rs, reverse=True):
    rbar[s] = med(rs[s])
    print(f"  s={s:>2} (H=N-{s})  r={rbar[s]:.3f}   n={len(rs[s])}  {['%.2f'%v for v in rs[s]]}")

# STEP 2: project states(H,22)
print("\n=== N=22 projection ===")
d22 = data.get(22, {})
if d22:
    anchor = max(d22)                      # highest cleanly measured climb height
    st = d22[anchor]["states"]
    proj = {anchor: st}
    print(f"anchor: H={anchor} states={st}")
    for H in range(anchor + 1, 22):        # up to H=21 (H=22 is closed form)
        s = 22 - H
        r = rbar.get(s)
        if r is None:                      # no measured r at this spare -> hold last/decay
            r = max(1.0, min(rbar.values()))
        st *= r
        proj[H] = st
    pole = max(proj, key=proj.get)
    print(f"projected pole: H={pole}  states={proj[pole]:.3e}  frac={pole/22:.3f}")
    print("  H   proj_states")
    for H in sorted(proj):
        print(f"  {H:>3} {proj[H]:.4e}")
    # STEP 3 sizing handled in the doc once clean pole wall measured.
