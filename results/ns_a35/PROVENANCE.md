# a(35) — provenance

**a(35) = 3561147281381782175236253062**  (new frontier term)

- **Computed:** 2026-07-10, **two-machine disk-split** (dalby + ayr), **KINK
  kernel**, u128 counter. First use of the multi-machine split-by-height =
  split-by-DISK approach (each machine's heights hit only its own disk, so the
  single-disk I/O contention that dominates a solo run is eliminated for free).
  Driver `scripts/run_height_subset.sh N HEIGHTS CORES RAM`.
  - **dalby** (aarch64 / ARM Neoverse-N1, 80 cores), engine rev `b8f13d41`:
    `--heights 1-2,19-35` = the real top height **H19** (the long pole) plus all
    closed forms. orchestrate wall **25112.2s (~7.0h)**, rss_max **372 MB**.
    Run-dir on NVMe (scratch on disk, not tmpfs).
  - **ayr** (x86_64, 32 cores), engine rev `d6e5679` (native build, Go 1.24.13):
    `--heights 3-18` = the other real heights. wall **19831.6s (~5.5h)**,
    rss_max **339 MB**.
  - Both concurrent → **total ~7.0h wall vs ~16h single-machine (~2.3x)**. The
    two engine revs differ only in docs/scripts after `b8f13d41`; the kink
    engine itself is identical.
  - Config: `--kernel kink --counter u128 --overlap-heights 35`, per-worker
    `--ram` 1 GiB (dalby) / 1.5 GiB (ayr), `--checkpoint-every 300`.
- **Height coverage:** P16 is NOT wired in `b8f13d41`, so the real sweep ran
  **H3-H19** (H19 swept as a real height, unlike a34 where P15 held the top real
  at H18). H20-H35 closed-form (P9-P15 diagonals k=2..16-ish + pole H34 + top
  H35), plus low H1,H2. All 35 per-height shards present exactly once (combine
  errors on a missing/truncated shard); `results/ns_a35/perheight/`.
- **Validation:**
  - a(1)-a(20) byte-match `fixtures/b006770.txt`.
  - a(21)-a(34) match banked `results/ns_a{21..34}` exactly (a22-a25 have no
    2-column banked triangle, skipped — all others OK). `A35_VALIDATE_PASS`.
  - growth a35/a34 = **6.9106** (trend .../6.8987/6.9048/6.9106, monotone,
    still climbing toward λ≈7.1).
  - **P16 holdout now available (not yet run):** T(35,19) is a REAL computed
    value (H19 was swept, not taken from P16). P16 was *fit* from T(33,17) and
    T(34,18), so T(35,19) is the first independent point P16 predicts — comparing
    the fitted P16(35,19) against this real T(35,19) is the first genuine holdout
    test of P16. a34's top cell had no such holdout.
- **Method note / tier:** the split ran DIFFERENT heights on ARM (dalby) vs x86
  (ayr) — a partial cross-ISA computation, NOT a full same-heights cross-ISA
  re-verify (as a34 had). The kink kernel is the a29 cell-diff-validated
  independent reimplementation of the column kernel, so the method is
  cross-checked; this specific term is one-algorithm, banked-prefix + growth
  validated. A full cross-ISA re-verify (recompute all heights on one machine)
  is a follow-up if a stronger tier is wanted.
