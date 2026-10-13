# a(37)

a(37) = 170463735577007360431441250424

Computed 2026-07-23 on dalby (ARM Ampere Altra, 80 cores) at revision
`28e4056c` (P_17 newly wired; engine changes in `docs/engine-record.md`) by
`scripts/term.sh 37`: 13,048.4 s of wall, 580,223 cpu-s, peak RSS 394.6 MB.
Heights 3..19 enumerated; heights 1, 2 and 20..37 from the closed forms
P_k, k = 37 − H ≤ 17, H = 20 being P_17's first use. Disk peak 75.7 GB,
measured by `scripts/dalby_du_monitor.sh` (`rundir_size.log`).

Files: `triangle.txt`, `perheight/h{1..37}.out`, `rundir_size.log`.

Checks:

- a(1)..a(20) match `fixtures/b006770.txt`; a(21) and a(26)..a(36) match the
  earlier triangles (a(22)..a(25) have no plain-format file and are
  skipped, as in the earlier runs).
- T(37,37) = 3^36 and T(37,36) = 880·3^33 with 880 = P_1(37).
- Growth: a(37)/a(36) = 6.9212 (a(36)/a(35) = 6.9157).

T(37,19) is enumerated and is the first of the two cells needed to fit
P_18; the k = 17 ratio T(37,20)/T(36,19) = 5.19 continues the trend.
