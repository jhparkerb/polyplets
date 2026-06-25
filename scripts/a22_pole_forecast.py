#!/usr/bin/env python3
# a22_pole_forecast.py -- final a(22)-on-dalby wall forecast from the pole ladder.
#
# The wall = the H21 (=N-1) sweep MT'd (the pole; all 63 sweeps run concurrently on dalby's
# ~76 cores, so wall = heaviest single sweep). We fit pole_states(N) and pole_cpu(N) for the
# measured ladder (H=N-1, N=13..20) log-linearly in N and extrapolate to N=22, then convert
# cpu -> wall with the measured MT speedup.
#
# USAGE: a22_pole_forecast.py [speedup]   (speedup default 9.0; pass measured value)
import os, re, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEEDUP = float(sys.argv[1]) if len(sys.argv) > 1 else 9.0

# pole_states for tiny N measured inline (serial), exact:
pts_states = {13: 23778, 14: 57408}
pts_cpu = {}

# parse the ladder log (N, H, wall, cpu, states)
log = os.path.join(ROOT, "runs/a22_forecast/pole_ladder.log")
if os.path.exists(log):
    for ln in open(log):
        m = re.match(r"\s*(\d+)\s+H\d+\s+([0-9.]+)\s+([0-9.]+)\s+(\d+)", ln)
        if m:
            N = int(m.group(1)); wall = float(m.group(2)); cpu = float(m.group(3)); st = int(m.group(4))
            pts_states[N] = st; pts_cpu[N] = (cpu, wall)

def loglin_fit(xy):                       # fit y = A*exp(b*N); return (A,b, predict)
    xs = sorted(xy); n = len(xs)
    X = [float(N) for N in xs]; Y = [math.log(xy[N]) for N in xs]
    mx = sum(X)/n; my = sum(Y)/n
    b = sum((X[i]-mx)*(Y[i]-my) for i in range(n)) / sum((X[i]-mx)**2 for i in range(n))
    a = my - b*mx
    return a, b, (lambda N: math.exp(a + b*N))

print(f"=== pole ladder data (H=N-1) ===")
print(f"{'N':>3} {'states':>12} {'st_ratio':>8} {'cpu_s':>11} {'wall_s':>9} {'eff_par':>7} {'cpu/st_ms':>9}")
prev=None
for N in sorted(pts_states):
    st = pts_states[N]
    r = f"{st/prev:.3f}" if prev else "-"
    if N in pts_cpu:
        cpu, wall = pts_cpu[N]
        ep = f"{cpu/wall:.1f}" if wall>0 else "-"
        cps = f"{cpu/st*1000:.3f}"
        print(f"{N:>3} {st:>12} {r:>8} {cpu:>11.1f} {wall:>9.1f} {ep:>7} {cps:>9}")
    else:
        print(f"{N:>3} {st:>12} {r:>8} {'-':>11} {'-':>9} {'-':>7} {'-':>9}")
    prev=st

if len(pts_states) >= 3:
    aS,bS,fS = loglin_fit(pts_states)
    print(f"\npole_states(N) ~ exp({aS:.3f} + {bS:.3f} N)  => ratio/N = {math.exp(bS):.3f}")
    print(f"  pole_states(22) = {fS(22):.3e}")
if len(pts_cpu) >= 2 and len(pts_states) >= 3:
    # per-state(N) = cpu/states; track its ratio (saturation detector)
    ps = {N: pts_cpu[N][0] / pts_states[N] for N in pts_cpu}
    print("\nper-state(N) ms and ratio:")
    pv = None
    for N in sorted(ps):
        r = f"{ps[N]/pv:.3f}" if pv else "-"
        print(f"  N={N}: {ps[N]*1000:.3f} ms   ratio={r}")
        pv = ps[N]
    Ns = sorted(ps)
    last_ps = ps[Ns[-1]]
    pole_states22 = fS(22)
    # effective parallelism (cap)
    eff = max(pts_cpu[N][0]/pts_cpu[N][1] for N in pts_cpu)  # best observed
    print(f"\neff_par cap observed = {eff:.2f}x")
    print("=== BRACKET on pole sweep (H21) wall ===")
    # OPTIMISTIC: per-state saturates NOW -> pole_cpu = states(22)*last_per_state
    cpu_opt = pole_states22 * last_ps
    # PESSIMISTIC: per-state keeps its current geometric growth to N=22
    aP,bP,fP = loglin_fit(ps)
    cpu_pess = pole_states22 * fP(22)
    for label, cpu in (("optimistic (per-state saturates at N=%d)"%Ns[-1], cpu_opt),
                       ("pessimistic (per-state holds x%.2f/N)"%math.exp(bP), cpu_pess)):
        print(f"  {label}: pole_cpu={cpu:.3e}s = {cpu/3600:.0f} cpu-hr "
              f"-> wall@{eff:.1f}x = {cpu/eff/3600:.1f} h ({cpu/eff/3600/24:.2f} d)")
    print(f"\n=== a(22) dalby wall ~ pole-sweep wall (×1–3 for 3-prime RAM schedule, §sched). "
          f"Need N18/N19 to collapse the bracket. ===")
