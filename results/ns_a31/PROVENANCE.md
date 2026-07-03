# a(31) — provenance

**a(31) = 1569631619081324581014300**  (new frontier term)

- **Computed:** 2026-07-03, dalby-solo, **KINK kernel**. rev `2ce164b`, u128
  counter. `scripts/dalby_term.sh 31`. orchestrate wall **10003.1s
  (~166.7 min / ~2.78h)**, 80 cores (dalby = aarch64 / ARM Neoverse-N1).
  - Config = the a29-cell-validated kink config: `--kernel kink --counter
    u128 --cores 80 --ram 1GiB --unit-mult 4 --steal-grain 0.05` (no
    overlap-heights). RAM light (kink rss_max ~5.9 GB peak at the H18 peak
    column).
  - P9-P12 closed-form diagonals cover H19-29 (k=2..12) + pole H30 + top H31
    + low H1,H2; real sweep was **H3-18** (top real height H18, **68% of the
    sweep wall** — 6827s; H17 1838s; see cost_profile_dalby.tsv).
- **Combine:** `combine -in runs/ns_a31/perheight -maxn 31`, all 31 heights
  present exactly once.
- **Validation:**
  - a(1)-a(20) byte-match `fixtures/b006770.txt`.
  - a(21)-a(30) match banked `results/b006770_upload.txt` exactly.
  - growth a31/a30 = **6.8853** (trend .../6.8616/6.8700/6.8779/6.8853,
    monotone, still climbing toward λ≈7.1).
- **Tier:** computed, single-source (high heights not independently
  reconfirmed). The kink kernel itself is the a29 cell-diff-validated
  independent reimplementation of the column kernel, so the method is
  cross-checked; this specific term is one-algorithm.
