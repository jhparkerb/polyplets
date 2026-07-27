# Provenance — a(20) run (predates the PROVENANCE.md convention)

This directory predates the per-term `PROVENANCE.md` convention used from
`results/ns_a26/` onward; its provenance lives in the original artifacts:

- `summary.txt` — per-height job stats (ayr, seek-index engine, 30 cores,
  420 columns over 20 heights; harvested 2026-06-28, commit `f7f6366`).
- `a20.log` — the run log.
- `Tnh_triangle.txt` / `triangle_Tnh.txt`, `columns.tsv`, `perheight/` —
  the swept triangle and per-height outputs.

Validation status: a(20) is inside the two-algorithm confirmed range —
a(1)–a(22) match digit-for-digit between the Redelmeier enumerator
(`build/g2`) and the transfer-matrix engine (fleet run completed
2026-07-16, `results/redelmeier_row22/`).
