# a(36)

a(36) = 24629107617723857143962968288

Computed 2026-07-10 on two machines at revision `f4edb3b` (run files now
written with LEB128 varints): ayr (x86, 32 cores) enumerated heights 1..18
and filled 20..36 from the closed forms P_k, k = 36 − H ≤ 16, in 6988.2 s
of wall (187,437.7 cpu-s, peak RSS 351.6 MB); dalby (ARM, 80 cores)
enumerated height 19 in 11,810.4 s (397,861 cpu-s, peak RSS 380.2 MB).

Files: `triangle.txt`, `perheight/h{1..36}.out`.

Checks:

- a(1)..a(35) from the combined triangle match `results/ns_a35/triangle.txt`.
- a(1)..a(20) match `fixtures/b006770.txt`.
- T(36,36) = 3^35 and T(36,35) = 855·3^32 with 855 = 25·36 − 45 = P_1(36).
- The ratio along the k = 16 diagonal across the P_16 cell T(36,20) and the
  enumerated T(35,19) continues smoothly: 5.31, 5.20, 5.10.

T(36,19) is enumerated and lies on the k = 17 diagonal; with the enumerated
T(34,17) and T(35,18) it gives two points to fit P_17 and one to check it.
