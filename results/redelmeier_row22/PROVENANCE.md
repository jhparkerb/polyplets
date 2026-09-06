# a(22) whole-row Redelmeier confirmation — provenance

**Two-algorithm confirmation frontier: 20 -> 22** (subsumes 21).

Fleet run launched 2026-07-11 13:41 EDT (Terminal Velocity kernel, 2.06x:
L1 terminal pure-count, L3 compile-time neighbour offsets, L4 u16 untried,
clang++; ledger docs/engine-record.md). 24,000 shards split by
all-core throughput, REBALANCED 2026-07-11 16:40 after measured all-core
rates ([[fleet-benchmark-allcore]]):

- dalby (ARM, 80w): shards [0,14300), wall 427,936s = 118.9h,
  complete 2026-07-16 15:44 EDT
- ayr (x86, 32w): shards [14300,19460), wall 418,454s = 116.2h,
  complete 2026-07-16 13:07 EDT
- gympie (Apple, 10w): shards [19460,24000), wall 440,628s = 122.4h,
  complete 2026-07-16 19:17 EDT
  (balance spread ~5% across three ISAs — the rebalance held to the end)

Gather: scripts/g2_fleet_gather.sh 22 24000 (one tar per box); combine
verified ALL 24,000 shards present and summed (scripts/g2_combine.sh,
fail-loud on missing shards).

## Verification

- **Every row n = 1..22 matches the banked values exactly**, including
  row 21 = 6954084405510437 and row 22 = 47255332844367680 (both
  previously computed by the transfer-matrix engine; this run is the
  independent Redelmeier confirmation, not a first computation).
- Pre-run validation: gate-g2 green incl. pure-count check; row-18 and
  row-19 fleet runs matched banked across all three ISAs.

Result: a(1)..a(22) now rest on two algorithms sharing no counting logic
(paper tier T1), as the paper asserts.
