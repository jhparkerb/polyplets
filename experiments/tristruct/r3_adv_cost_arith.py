#!/usr/bin/env python3
"""r3_adv_cost_arith.py -- cost-adversary exact arithmetic checks, round 3.

Re-derives, in exact integers, the decision-bearing figures of
results/triangle-r3-l6-wildcard.md (residue/CRT ladder) and spot-checks
L4's floor and the band shares.  Throwaway; log alongside.
"""
from fractions import Fraction

# Banked row-40 values (results/triangle-r3-harness.md Part 2, loader-quoted).
T40 = {
    15: 6374412577120147022430261962743,
    16: 5908452097354911220916654388822,
    17: 5140790021321717364748374654418,
    18: 4209726451267585301668763319533,
    19: 3247572468599336484342102174163,
    20: 2359769260803281210360136128699,
    21: 1613457978443478071138613405555,
}
a40 = 56749893611764175164545926946127

print("== band shares ==")
s1520 = sum(T40[h] for h in range(15, 21))
s1521 = s1520 + T40[21]
print(f"H=15..20 share: {float(Fraction(s1520, a40))*100:.4f}%  (L6 claims 48.00%)")
print(f"H=15..21 share: {float(Fraction(s1521, a40))*100:.4f}%  (brief: 50.8445%)")

print("\n== CRT modulus count (L6: '13 runs exceed log2 T(40,15) ~ 103 bits') ==")
# 8-bit primes: payload is one byte, so p <= 251.
def primes_desc(lo, hi):
    ps = [p for p in range(hi, lo, -1)
          if p > 1 and all(p % d for d in range(2, int(p**0.5) + 1))]
    return ps
ps = primes_desc(1, 255)
target = T40[15]
prod, k = 1, 0
for p in ps:
    if prod > target:
        break
    prod *= p
    k += 1
print(f"log2 T(40,15) = {target.bit_length()} bits")
print(f"largest 8-bit primes, product first exceeds T(40,15) at k = {k} runs")
print(f"top-13 product bits = {sum([], )or (lambda q: q)(1)}", end="")
p13 = 1
for p in ps[:13]:
    p13 *= p
print(f"\ntop-13 product = {p13.bit_length()-1}..{p13.bit_length()} bits; "
      f"covers T(40,15)? {p13 > target}")

print("\n== L6 ladder projections: growth-base sensitivity ==")
W14 = 891074          # branch-measured window census at H=14
slot_s = Fraction(342, 10) / (W14 * 41)   # 34.2 s/col over 891074*41 slot-cols
print(f"anchor: {float(slot_s)*1e6:.3f} us/slot-col (branch, H=14, exact payload)")
for base_num, base_den, tag in [(29, 10, "x2.9 (L6 model)"), (304, 100, "x3.04 (L6 own probe, upper)")]:
    print(f"-- growth base {tag}")
    for H in (20, 21):
        w = W14 * base_num**(H - 14) // base_den**(H - 14)
        ram_tight = w * (41 * 1 * 2 + 22)          # L6's own per-state model, bytes
        cols = 40 - H + 1
        wall_s = float(slot_s) * w * 41 * cols
        print(f"   H={H}: windows {w/1e6:,.0f}M  RAM(model) {ram_tight/2**30:.0f} GiB"
              f"  (x1.5 container: {ram_tight*1.5/2**30:.0f} GiB)"
              f"  wall(1 thr) {wall_s/86400:.1f} d")

print("\n== L6 ladder total wall, one 8-bit prime, H=15..20 (base 2.9) ==")
tot = 0.0
for H in range(15, 21):
    w = W14 * 29**(H - 14) // 10**(H - 14)
    tot += float(slot_s) * w * 41 * (40 - H + 1)
print(f"sum H=15..20: {tot/86400:.1f} days single-thread; x14 CRT runs = {14*tot/86400:.0f} days")

print("\n== L4 floor spot-check ==")
lam_half = 2.669
fix_h_32 = 2546382907164
fix_r_32 = 7063812264280
g8 = lam_half**8
print(f"lambda^4 = 2.669^8 = {g8:.0f} (L4: ~2574)")
print(f"I(h)(40) ~ {fix_h_32*g8:.2e} (L4: 6.6e15);  I(C2)(40) ~ {fix_r_32*g8:.2e} (L4: 1.8e16)")
print(f"hmirror wall: 7.49 s x 2.669^22 = {7.49*lam_half**22/86400/365.25:.0f} laptop-yr (L4: 570)")
print(f"r180 wall:   53.1 s x 2.669^22 = {53.1*lam_half**22/86400/365.25:.0f} laptop-yr (L4: 4000)")
print(f"floor at 8.5e5/s: {fix_h_32*g8/8.5e5/86400/365.25:.0f} yr (L4: ~240);"
      f" at 3.1e5/s: {fix_r_32*g8/3.1e5/86400/365.25:.0f} yr (L4: ~1900)")

print("\n== L5 model-count floor ==")
print(f"band sum H=15..21 = {s1521:.3e} models (L5: ~2.9e31)")
