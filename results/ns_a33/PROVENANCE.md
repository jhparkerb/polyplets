# a(33) — provenance

**a(33) = 74631481980411777590683952**  (new frontier term)

- **Computed:** 2026-07-04, dalby-solo, **KINK kernel**. rev `dcd7da4`
  (P14 wired), u128 counter. `scripts/term.sh 33`. orchestrate wall
  **12200.3s (~203.3 min / ~3.39h)**, 80 cores (dalby = aarch64 / ARM
  Neoverse-N1).
  - Config = the a29-cell-validated kink config: `--kernel kink --counter
    u128 --cores 80 --ram 1GiB --unit-mult 4 --steal-grain 0.05` (no
    overlap-heights). RAM light (kink rss_max **~6.02 GB** peak at the H18
    peak column).
  - P9-P14 closed-form diagonals cover H19-31 (k=2..14) + pole H32 + top
    H33 + low H1,H2; real sweep was **H3-18**. **P14 held the top real
    height at H18** (without it a33 would have swept H19, ~11h). H18 =
    **8478s (~69.5% of the sweep wall)**; H17 2214s (18%); H16 676s (see
    cost_profile_dalby.tsv). Total sweep wall ~12185s.
- **Combine:** `combine -in runs/ns_a33/perheight -maxn 33`, all 33 heights
  present exactly once.
- **Validation:**
  - a(1)-a(20) byte-match `fixtures/b006770.txt`.
  - a(21)-a(32) match banked `results/ns_a{21..32}` exactly.
  - **T(33,18) = 2965403643769893816836542** (swept H18 top cell) equals the
    **independent P_15 prediction** P_15(33)/3^13 — the first holdout for
    P_15, which was deliberately NOT wired so a33 would sweep H18 and yield
    this point. P_15 is thereby validated (see results/ns_a33 and the P_15
    wiring commit).
  - growth a33/a32 = **6.8987** (trend .../6.8779/6.8853/6.8922/6.8987,
    monotone, still climbing toward λ≈7.1).
- **Tier:** computed, single-source (high heights not independently
  reconfirmed). The kink kernel is the a29 cell-diff-validated independent
  reimplementation of the column kernel, so the method is cross-checked;
  this specific term is one-algorithm. (Optional ayr cross-ISA verify of the
  H18 top height may follow, in parallel with a34.)
