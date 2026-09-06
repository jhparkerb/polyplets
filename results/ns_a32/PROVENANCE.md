# a(32) — provenance

**a(32) = 10818203977457804418974036**  (new frontier term)

- **Computed:** 2026-07-03, dalby-solo, **KINK kernel**. rev `3ffeed2b`
  (P13 wired), u128 counter. `scripts/term.sh 32`. orchestrate wall
  **10945.3s (~182.4 min / ~3.04h)**, 80 cores (dalby = aarch64 / ARM
  Neoverse-N1).
  - Config = the a29-cell-validated kink config: `--kernel kink --counter
    u128 --cores 80 --ram 1GiB --unit-mult 4 --steal-grain 0.05` (no
    overlap-heights). RAM light (kink rss_max **~5.78 GB** peak at the H18
    peak column).
  - P9-P13 closed-form diagonals cover H19-30 (k=2..13) + pole H31 + top
    H32 + low H1,H2; real sweep was **H3-18**. **P13 held the top real
    height at H18** (without it a32 would have swept H19). H18 = **68.8% of
    the sweep wall** (7516s); H17 18.4% (2010s); H16 5.8% (see
    cost_profile_dalby.tsv). Total sweep wall 10931.7s.
- **Combine:** `combine -in runs/ns_a32/perheight -maxn 32`, all 32 heights
  present exactly once.
- **Validation:**
  - a(1)-a(20) byte-match `fixtures/b006770.txt`.
  - a(21)-a(31) match banked `results/ns_a31/triangle.txt` exactly.
  - growth a32/a31 = **6.8922** (trend .../6.8700/6.8779/6.8853/6.8922,
    monotone, still climbing toward λ≈7.1).
- **Tier:** computed, single-source (high heights not independently
  reconfirmed). The kink kernel is the a29 cell-diff-validated independent
  reimplementation of the column kernel, so the method is cross-checked;
  this specific term is one-algorithm.
