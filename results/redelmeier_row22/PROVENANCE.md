# Rows 1..22 by the Redelmeier enumerator

Rows n = 1..22 of the triangle, counted by the Redelmeier program
(`build/redelmeier`; kernel changes in `docs/engine-record.md`), which shares no
counting logic with the transfer-matrix engine. The work was split into
24,000 shards by measured all-core throughput and run on three machines
from 2026-07-11 13:41 EDT:

- dalby (ARM, 80 workers): shards [0, 14300), 427,936 s, done 2026-07-16 15:44
  EDT
- ayr (x86, 32 workers): shards [14300, 19460), 418,454 s, done 2026-07-16 13:07
  EDT
- gympie (Apple, 10 workers): shards [19460, 24000), 440,628 s, done 2026-07-16
  19:17 EDT

Gathered by `scripts/redelmeier_fleet_gather.sh 22 24000` and summed by
`scripts/redelmeier_combine.sh`, which fails if any shard is missing; all 24,000
were present. Output: `combined.txt`.

Every row n = 1..22 matches the transfer-matrix values, including row 21 =
6954084405510437 and row 22 = 47255332844367680. Before the run, the
program's own tests were green and its row-18 and row-19 runs had matched
on all three machines. So a(1)..a(22) rest on two algorithms sharing no
counting logic.
