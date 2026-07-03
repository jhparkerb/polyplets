# a(30) — provenance

**a(30) = 227969227118066423789154**  (new frontier term)

- **Computed:** 2026-07-03, dalby-solo, **KINK kernel** (first production
  frontier term on the validated kink-carry engine). rev `d1554bd`, u128
  counter. `scripts/dalby_a30.sh`. orchestrate wall **3711s (~61.9 min)**,
  80 cores (dalby = aarch64 / ARM Neoverse-N1).
  - Config = the exact one that passed the a29 kink cell-diff: `--kernel
    kink --counter u128 --cores 80 --ram 1GiB --unit-mult 4 --steal-grain
    0.05` (no overlap-heights). RAM light (kink rss_max ~76 MB).
  - P9-P12 closed-form diagonals cover H18-28 (k=2..12) + pole H29 + top H30
    + low H1,H2; real sweep was **H3-17** (top real height H17, 45% of the
    sweep wall).
- **Combine:** `combine -in runs/ns_a30/perheight -maxn 30`, all 30 heights
  present exactly once.
- **Validation:**
  - a(1)-a(20) byte-match `fixtures/b006770.txt`.
  - a(21)-a(29) match certified `results/ns_a2{1..9}` exactly.
  - growth a30/a29 = **6.8779** (trend .../6.853/6.8526/6.8616/6.8700/6.8779
    — monotone, rising toward λ≈7.1, no anomaly).
  - **Independent cross-check (in progress):** ayr (x86-64 AMD Ryzen) runs
    the COLUMN kernel on H17 — different ISA *and* different kernel than
    dalby's ARM/kink — comparing per-column boundary frontier counts (col0
    matched: 65791==65791). `scripts/ayr_a30_h17_verify.sh`.
- **Diagonals:** T(30,17) = 9142099138689979555656 (top swept height; a new
  data point for the not-yet-derived P13). T(30,18) = 5455070058849476986528
  (P12 closed-form inject).
- **Tier:** computed, single-source. Pending certification.
