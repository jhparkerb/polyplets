"""As slope_slices.py but scanning an onset: drop the first t points before
fitting, since the s=1 diagonal law only holds for n >= 2k+1. Also fits the
growth form T ~ C * mu^H * H^theta on the slope-2 slice."""
import glob, re, math
from fractions import Fraction
import importlib.util
spec = importlib.util.spec_from_file_location("ss", __file__.replace("slope_onset", "slope_slices"))
ss = importlib.util.module_from_spec(spec); spec.loader.exec_module(ss)

T = ss.T

def slice_seq(s, k):
    seq, Hs = [], []
    H = 1
    while s * H + k <= 40:
        v = T.get((s * H + k, H))
        if v is None: break
        if v: seq.append(v); Hs.append(H)
        H += 1
    return Hs, seq

print("=== onset scan: minimal order with the first t points dropped ===")
for s in (1, 2, 3):
    for k in (0, 1, 2):
        Hs, seq = slice_seq(s, k)
        hits = []
        for t in range(0, min(8, len(seq) - 8)):
            sub = seq[t:]
            rmax = max(1, (len(sub) - 2) // 2)
            r, c = ss.minimal_order(sub, maxord=min(8, rmax))
            if r: hits.append((t, Hs[t], r))
        print(f"s={s} k={k}: {len(seq)} pts, fits found: "
              + (", ".join(f"onset H>={h} order={r}" for t, h, r in hits) if hits else "NONE"))

print()
print("=== slope-2 growth form: ratios and local exponent ===")
Hs, seq = slice_seq(2, 0)
print(" H   T(2H,H)/T(2H-2,H-1)   local theta (3-pt)")
for i in range(2, len(seq)):
    r1 = seq[i] / seq[i - 1]
    r0 = seq[i - 1] / seq[i - 2]
    # T = C mu^H H^theta  =>  log(r_i/r_{i-1}) = theta*log(H_i(H_i-2)/(H_i-1)^2)
    H = Hs[i]
    denom = math.log(H * (H - 2) / (H - 1) ** 2)
    theta = math.log(r1 / r0) / denom if denom else float('nan')
    print(f"{H:3d}   {r1:18.5f}   {theta:8.3f}")
