#!/usr/bin/env python3
"""R1-A base anatomy audit: fit the incumbent's per-n cost from banked records.

Data below is transcribed from in-tree banked records only; every number's
source path is in the comment on its line. Re-run: python3 experiments/rook1/rook1_R1-A_basefit.py
(pure stdlib; the cpu sums for a26..a34 are awk sums of the cpu_s column of the
named cost_profile TSVs, reproduced here as constants with a re-derivation
command in the log header).
"""
import math

# --- Series 1: the shipped KINK engine's production ladder, dalby, total cpu-seconds
# per maxn=N end-to-end run (real sweeps + closed-form injection + combine), as banked.
# a35 (two-machine disk-split) and a36 (ayr+dalby split) excluded: cross-ISA cpu-seconds
# are not commensurable with the dalby series.
kink = {
    # n: (cpu_s, top_real_H, source)
    30: (79445,  17, "results/ns_a30/cost_profile_dalby.tsv (awk sum cpu_s)"),
    31: (161215, 18, "results/ns_a31/cost_profile_dalby.tsv (awk sum cpu_s)"),
    32: (176298, 18, "results/ns_a32/cost_profile_dalby.tsv (awk sum cpu_s)"),
    33: (192745, 18, "results/ns_a33/cost_profile_dalby.tsv (awk sum cpu_s)"),
    34: (210666, 18, "results/ns_a34/cost_profile_dalby.tsv (awk sum cpu_s)"),
    37: (580223, 19, "results/ns_a37/PROVENANCE.md (cpu 580223s)"),
    38: (1783598, 20, "results/ns_a38/PROVENANCE.md (cpu 1,783,598s)"),
    39: (2070672, 20, "results/ns_a39/PROVENANCE.md (cpu 2,070,672s)"),
    40: (5318465, 21, "results/ns_a40/PROVENANCE.md (871963+1116858+3329644)"),
}

# --- Series 2: what exists on the chartered window n=24..30 (mixed engines/machines)
window = {
    24: (None, 16, "column", "dalby", "results/ns_a24/RESULT.md: wall 4870.3s x 80c, H16 only; H1-15 reused; TOTAL CPU NOT RECORDED"),
    25: (None, 16, "column", "ayr30", "results/ns_a25/RESULT.md: wall 45841.5s x 30c; cpu not recorded"),
    26: (259913, 15, "column", "dalby", "results/ns_a26/cost_profile.tsv (awk sum cpu_s)"),
    27: (848671, 16, "column", "dalby(H16 only)+ayr(H3-15, cpu not recorded)", "results/ns_a27/cost_profile_dalby.tsv"),
    28: (353202, 15, "column", "ayr32", "results/ns_a28/PROVENANCE.md cpu 353201.8s"),
    29: (1960647, 16, "column", "dalby", "results/ns_a29/PROVENANCE.md cpu 1960646.8s"),
    30: (79445, 17, "kink", "dalby", "results/ns_a30/cost_profile_dalby.tsv"),
}

# --- Per-height cpu sums (kink, dalby; awk sums by H of cpu_s), for the per-height ratio
perH = {
    30: {15: 7772, 16: 15191, 17: 34363},
    31: {15: 7455, 16: 15613, 17: 36831, 18: 95722},
    32: {15: 7905, 16: 16739, 17: 39929, 18: 105768},
    33: {15: 8484, 16: 18032, 17: 43444, 18: 116418},
    34: {15: 9090, 16: 19395, 17: 47028, 18: 128350},
}
a40_BC = (1116858, 3329644)  # phase B (H20 solo), phase C (H21 solo), ns_a40/PROVENANCE.md:14-19


def lsq(pairs):
    n = len(pairs)
    sx = sum(x for x, _ in pairs); sy = sum(y for _, y in pairs)
    sxx = sum(x * x for x, _ in pairs); sxy = sum(x * y for x, y in pairs)
    m = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    b = (sy - m * sx) / n
    return m, b


print("== Series 1: kink dalby ladder, ln(cpu_s) vs n, least squares ==")
pairs = [(n, math.log(c)) for n, (c, _, _) in sorted(kink.items())]
m, b0 = lsq(pairs)
print(f"n window: {min(kink)}..{max(kink)} ({len(kink)} points; 35,36 excluded, cross-machine)")
print(f"slope = {m:.5f}  =>  per-n cost ratio e^slope = {math.exp(m):.4f}")
print("residuals (ln cpu - fit), and implied cpu/fit factor:")
for n, y in pairs:
    r = y - (m * n + b0)
    print(f"  n={n}  resid={r:+.3f}  x{math.exp(r):.2f}   topH={kink[n][1]}  [{kink[n][2]}]")
print("adjacent measured per-n ratios (MEASURED, same machine):")
ks = sorted(kink)
for a, bn in zip(ks, ks[1:]):
    dn = bn - a
    r = kink[bn][0] / kink[a][0]
    print(f"  a{bn}/a{a} = {r:.3f} over dn={dn} => {r ** (1/dn):.3f}/n  (topH {kink[a][1]}->{kink[bn][1]})")

print("\n== Series 2: chartered window n=24..30, what exists ==")
for n in sorted(window):
    c, h, eng, mach, src = window[n]
    print(f"  n={n}  cpu={c}  topH={h}  engine={eng}  machine={mach}  [{src}]")
p = [(n, math.log(window[n][0])) for n in (26, 29)]
m2, _ = lsq(p)
print(f"column-engine dalby pair a26->a29: ratio {window[29][0]/window[26][0]:.3f} over 3n => {math.exp(m2):.3f}/n (2 points, no residuals possible)")

print("\n== Per-height cpu ratios, kink dalby (cost per unit height) ==")
for n in sorted(perH):
    hs = sorted(perH[n])
    rs = ", ".join(f"H{h2}/H{h1}={perH[n][h2]/perH[n][h1]:.3f}" for h1, h2 in zip(hs, hs[1:]))
    print(f"  a{n}: {rs}")
R = a40_BC[1] / a40_BC[0]
print(f"  a40 phases: C/B = H21/H20 = {R:.4f}  (ns_a40/PROVENANCE.md)")
print(f"  sqrt of frontier per-height ratio: sqrt({R:.4f}) = {math.sqrt(R):.5f}")

print("\n== Fixed-H per-n growth (polynomial factor), kink dalby ==")
for h in (16, 17, 18):
    ns = [n for n in sorted(perH) if h in perH[n]]
    rr = [(perH[b][h] / perH[a][h]) ** (1 / (b - a)) for a, b in zip(ns, ns[1:])]
    print(f"  H={h}: per-n factors {['%.3f' % x for x in rr]}")
