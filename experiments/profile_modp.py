"""Profile the per-phase cost of modp_recover at several heights, to find the REAL
bottleneck and extrapolate to H=11 (order 13381, N=26792). Phases per prime:
  seq_modp  -- the C++ transfer-matrix sweep (build/gf_modp), 8-way PARALLEL in prod
  bm_modp   -- Berlekamp-Massey, O(N^2), Python, SERIAL in prod (line 161)
plus the one-shot CRT (Q) and validation. Reports per-prime times + the prod totals
(sweep wall = t_sweep*P/8 ; bm wall = t_bm*P serial) so we can see which wall-dominates.
"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "gf"))
import modp_recover as m

rows=[]
for H in (8, 9, 10):
    order, _ = m.find_order(H)
    N = 2 * order + 30
    P = order // 110 + 12          # prod prime count (old estimate / adaptive start)
    p = m.PRIMES[0]
    t0 = time.time(); s = m.seq_modp(H, N, p); t_sweep = time.time() - t0
    t0 = time.time(); C = m.bm_modp(s, p);     t_bm = time.time() - t0
    rows.append((H, order, N, P, t_sweep, t_bm))
    sweep_wall = t_sweep * P / 8       # 8-way parallel
    bm_wall    = t_bm * P              # SERIAL
    print(f"H={H:2d} order={order:5d} N={N:5d} P={P:3d}: "
          f"sweep={t_sweep:7.2f}s  bm={t_bm:7.2f}s  bm/sweep={t_bm/t_sweep:5.2f}  ||  "
          f"prod-wall: sweep(8x)={sweep_wall/60:6.1f}m  bm(serial)={bm_wall/60:6.1f}m")

# extrapolate to H=11 from the H=9->10 scaling (per-phase power law in N)
(H1,o1,N1,P1,sw1,bm1)=rows[-2]; (H2,o2,N2,P2,sw2,bm2)=rows[-1]
import math
a_sw = math.log(sw2/sw1)/math.log(N2/N1)   # t_sweep ~ N^a_sw
a_bm = math.log(bm2/bm1)/math.log(N2/N1)    # t_bm   ~ N^a_bm (expect ~2)
N11, P11 = 26792, 13381//110+12
sw11 = sw2*(N11/N2)**a_sw; bm11 = bm2*(N11/N2)**a_bm
print()
print(f"scaling exponents in N: sweep~N^{a_sw:.2f}  bm~N^{a_bm:.2f}")
print(f"H=11 EXTRAPOLATION (N={N11}, P~{P11}):")
print(f"  per-prime: sweep~{sw11:.0f}s  bm~{bm11:.0f}s")
print(f"  prod wall: sweep(8x)={sw11*P11/8/3600:.1f}h   bm(SERIAL)={bm11*P11/3600:.1f}h"
      f"   bm(if 8x)={bm11*P11/8/3600:.1f}h")
