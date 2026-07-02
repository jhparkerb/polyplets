# a(27) — provenance

**a(27) = 703126792093436034256**  (new frontier term)

- **Computed:** 2026-07-02, dalby+ayr split, rev `b390518`, u128 counter.
  - **dalby**: H16 (the monster) + closed-form H1,2,17-27. orchestrate PID 2215524,
    wall **13553.9s (~3.76h)**, 80 cores. H16 frontier peaked ~2.10M states, spill
    peaked ~126 GB (drained per column; disk fine).
  - **ayr**: swept tail H3-15. PID 1523246, wall **9697.2s (~2.7h)**, 32 cores.
  - Split wall ≈ max(halves) ≈ 3.76h (dalby H16 the critical path), vs ~4.2h+
    dalby-solo. `scripts/{dalby,ayr,combine}_a27.sh`.
- **Combine:** local guarded combine (rev `b14e0b1`, monotone-growth check PASS),
  `--require-cover` H1..27 all present exactly once.
- **Validation:**
  - a(1)-a(20) byte-match `fixtures/b006770.txt`.
  - a(21)-a(26) match certified `results/ns_a2{1..6}` values.
  - growth a27/a26 = **6.8526** (trend 6.821/6.833/6.843/6.853 — monotone, no anomaly).
- **Byproduct:** T(27,16) = 27798973373501478242 → with a26's T(26,15) this CLOSES
  P_11 (docs/a26-a30-diagonal-plan.md). Note T(27,16) > 2^64: the row total needs
  u128; per-state counts stay ~40-bit (the #12 decouple lever).
- **Tier:** computed, single-source. Pending certification.
