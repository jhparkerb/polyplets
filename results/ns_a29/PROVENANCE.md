# a(29) — provenance

**a(29) = 33145129805782422061325**  (new frontier term)

- **Computed:** 2026-07-02, dalby-solo, rev `7e28071` (next-system branch),
  u128 counter. `scripts/dalby_a29.sh`. orchestrate PID 2243059, wall
  **26202.2s (~7.28h)**, 80 cores, cpu **1960646.8s**, rss_max **1647.1 MB**.
  - P9-P12 closed-form diagonal strips cover H=17-27 (k=2..12) plus pole H28
    and top H29; only H1,2 and the real sweep H3-16 run the engine (top
    real height H=16 — the same height a27 swept dalby-solo).
  - Ran **concurrently** with `ayr_a28.sh` (one term per box, no
    cross-machine combine needed for either).
- **Combine:** `combine -in runs/ns_a29/perheight -maxn 29`, all 29 heights
  present exactly once (`--require-cover`).
- **Validation:**
  - a(1)-a(20) byte-match `fixtures/b006770.txt`.
  - a(21)-a(28) match certified `results/ns_a2{1..8}` values exactly
    (including a(28), landed the same session on ayr).
  - growth a29/a28 = **6.8700** (trend .../6.843/6.853/6.8526/6.8616/6.8700
    — monotone, no anomaly).
- **Tier:** computed, single-source. Pending certification.
