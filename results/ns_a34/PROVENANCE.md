# a(34) — provenance

**a(34) = 515316838423862758858377704**  (new frontier term)

- **Computed:** 2026-07-04, dalby-solo, **KINK kernel**. rev `d1b6bcb`
  (P15 wired), u128 counter. `scripts/dalby_term.sh 34`. orchestrate wall
  **13316.7s (~222.0 min / ~3.70h)**, 80 cores (dalby = aarch64 / ARM
  Neoverse-N1).
  - Config = the a29-cell-validated kink config: `--kernel kink --counter
    u128 --cores 80 --ram 1GiB --unit-mult 4 --steal-grain 0.05` (no
    overlap-heights). RAM light (kink rss_max **~6.44 GB** peak at the H18
    peak column).
  - P9-P15 closed-form diagonals cover H19-32 (k=2..15) + pole H33 + top
    H34 + low H1,H2; real sweep was **H3-18**. **P15 held the top real
    height at H18** (without it a34 would have swept H19, ~11h). H18 =
    **9336s (~70% of the sweep wall)**; H17 2376s (18%); H16 722s (see
    cost_profile_dalby.tsv).
- **Combine:** `combine -in runs/ns_a34/perheight -maxn 34`, all 34 heights
  present exactly once.
- **Validation:**
  - a(1)-a(20) byte-match `fixtures/b006770.txt`.
  - a(21)-a(33) match banked `results/ns_a{21..33}` exactly.
  - growth a34/a33 = **6.9048** (trend .../6.8853/6.8922/6.8987/6.9048,
    monotone, still climbing toward λ≈7.1).
  - **No closed-form holdout for the top cell**: T(34,18) =
    23288787870043631158670332 is a diagonal-16 point, and P_16 is not yet
    derivable independently of it (P_16 fits from T(33,17) and T(34,18), so
    T(34,18) is a *fit* input, not a prediction). Unlike a(33) (whose
    T(33,18) matched the held-out P_15), a(34)'s top cell is validated only
    by the banked-prefix + growth checks. T(34,18) now enables P_16.
- **Tier:** computed, single-source (high heights not independently
  reconfirmed). The kink kernel is the a29 cell-diff-validated independent
  reimplementation of the column kernel, so the method is cross-checked;
  this specific term is one-algorithm. Term chase parked here (2026-07-04)
  per the close plan.
