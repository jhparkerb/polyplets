# a(20)

a(20) = 1025573519362016

Computed on ayr with the earlier column engine (`cpp/tma`, seek-index
variant), 30 cores, 420 columns over 20 heights; harvested 2026-06-28 at
commit `f7f6366`. Every height was enumerated.

Files: `summary.txt` (per-height job statistics), `a20.log` (the run log),
`Tnh_triangle.txt` and `triangle_Tnh.txt` (the triangle T(n,H)),
`columns.tsv`, and `perheight/` (one file per height).

Check: a(1)..a(22) agree between this family of transfer-matrix programs and
the Redelmeier enumerator `build/g2` (`results/redelmeier_row22/`).
