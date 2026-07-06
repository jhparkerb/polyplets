# a(28) — provenance

**a(28) = 4824589228356722264087**  (new frontier term, first sextillion)

- **Computed:** 2026-07-02, ayr-solo, rev `7e28071` (next-system branch),
  u128 counter. `scripts/ayr_a28.sh`. orchestrate wall **11723.8s (~3.26h)**,
  32 cores, cpu **353201.8s**, rss_max **786.9 MB**.
  - P9-P12 closed-form diagonal strips cover H=16-26 (k=2..12) plus pole H27
    and top H28; only H1,2 and the real sweep H3-15 run the engine (top real
    height H=15 — the same height a26 swept dalby-solo, proven-feasible on
    ayr's 78GiB).
  - Ran **concurrently** with `dalby_a29.sh` (one term per box, no
    cross-machine combine needed for either).
- **Combine:** `combine -in runs/ns_a28/perheight -maxn 28`, all 28 heights
  present exactly once (`--require-cover`).
- **Validation:**
  - a(1)-a(20) byte-match `fixtures/b006770.txt`.
  - a(21)-a(27) match certified `results/ns_a2{1..7}` values exactly.
  - growth a28/a27 = **6.8616** (trend .../6.821/6.833/6.843/6.853/6.8526 →
    6.8616 — monotone, no anomaly).
- **Tier:** computed, single-source. Pending certification.
