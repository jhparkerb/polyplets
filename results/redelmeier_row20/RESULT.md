# Whole-row Redelmeier confirmation, n ≤ 20

**a(20) = 1025573519362016 — two-algorithm confirmed.** All rows n=1..20 of the
independent Redelmeier enumeration (`build/g2`, rev `7eab237`) match the banked
transfer-matrix values (`results/b006770_upload.txt`) exactly, 0 mismatches.
The two-algorithm frontier for A006770 moves 19 → **20**; A030233/A030222/A194596
inherit confirmation at n=20 (symmetric parts already Redelmeier-enumerated to 24).

- **Run:** dalby, tmux `0:g2_a20`, `scripts/g2_wholerow.sh 20 10 800 80`
  (S=10, K=800 shards, 80 jobs), launched 2026-07-10T18:03:39-0400.
- **Cost:** 28,684 s wall (7.97 h), 2,204,116 core-s total, **96.1% utilization**
  (2.204e6 / (28684×80)). Shard wall_s: mean 2755, p50 2752, p99 3092, max 3188.
- **Throughput:** full-cost nodes (size ≤ 19) = Σa(1..19) ≈ 1.777e14 →
  **12.4 ns/node ≈ 37 cycles** per full-cost node on Neoverse-N1 @3.0 GHz.
- **Artifacts:** `combined.txt` (this dir, verified vs b-file by exact diff),
  `driver.log`; per-shard w*.out/w*.log on dalby `runs/g2row_N20/`.
- Plan context: docs/redelmeier-tall-plan.md §5 (row 20 = the efficient buy).
  Row 21 follow-on: docs/terminal-velocity-plan.md.
