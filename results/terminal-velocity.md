# Terminal Velocity — g2 kernel shakeout ledger

Running record for `docs/terminal-velocity-plan.md`. Baseline
`results/redelmeier_row20/RESULT.md`. dalby = 80× Neoverse-N1, gcc 15.2,
clang++-19, aarch64, no SMT, 3.0 GHz sustained.

## P0 — profile (rev 7eab237, `build/g2 square8 15`, single core, 167.1 s)

| counter | value | derived |
|---|---|---|
| cycles | 501.02e9 | — |
| instructions | 1187.39e9 | **IPC 2.37** |
| branches | 210.81e9 | — |
| branch-misses | 4.14e9 | **1.96% miss rate; ≈9% of cycles** |
| L1-dcache-loads | 513.10e9 | — |
| L1-dcache-load-misses | 1.49e6 | **0.0003% — cache is perfect** |

Full-cost nodes N=15 = Σa(1..14) = 1.3157e10 → **90 instructions/node, 38 cy/node**.

**Conclusion — hypothesis revised.** NOT branch-miss-bound (miss rate 1.96%,
mispredicts ≈9% of cycles; IPC a healthy 2.37; cache essentially perfect). The
kernel is **instruction-throughput bound**. So the winning levers are the ones
that *delete instructions*, not the ones that fix stalls.

`perf annotate` (searchT, the only hot function — fully recursive/inlined):
- **~30%+ of samples** in the unrolled 8× neighbour probe: `ldr w,[x20,#132..#156]`
  (the `dj[]` offsets, reloaded from the struct every node), `ldrb w,[x19,w]`
  (status byte), `cbnz` (the `if(!st[j2])`), conditional push.
- Significant `memcpy` PLT weight (the per-call `std::memcpy` of the untried list).
- `str w,[x20,#776]` (numUntried/spill) ~7%.

**Revised lever ranking:** L1 (eliminate probe+push+unmark at the terminal-parent
level = 85.2% of N=21 nodes) #1 unchanged. **L3 up** (constexpr `dj[]` offsets
kill the 8 per-node struct loads — pure throughput). **L4 up** (u16 halves the
memcpy). **L2 down** (branch mispredicts aren't the bottleneck; the branchless
form still removes the branch *instruction*, so try it cheaply). L6 compiler
sweep last on the final kernel.

### Node structure (confirms the plan's premise)
For target N: terminal-parent level (size N-1) holds a(N-1)/Σa(1..N-1) of all
full-cost nodes. N=15: a(14)/Σa(1..14) = 1.116e10/1.316e10 = **84.8%**.
N=21: a(20)/Σa(1..20) = 1.0256e15/1.2036e15 = **85.2%**.

## Lever A/B log
(build on dalby, best-of-3 `time build/g2 square8 15`; confirm kept levers at N=16)

| lever | N=15 s | vs base | N=16 s | kept? | notes |
|---|---|---|---|---|---|
| baseline 7eab237 | 167.1 | 1.00× | — | — | perf stat above |
| L1 terminal pure-count | 95.0 | **1.76×** | — | ✅ | gate green; 85% of nodes → 8 loads+sum |
| L1 + `-mcpu=neoverse-n1` | 95.2 | 1.76× | — | ❌ | no gain; gcc generic aarch64 already tuned |
| + L3 constexpr offsets | 89.1 | **1.88×** | — | ✅ | +6.6%; folds dj[] into immediate offsets |
| + L2 branchless probe | 89.4 | 1.87× | — | ❌ | neutral (P0 was right: not branch-bound); reverted |
| + L4 u16 untried | 88.7 | 1.88× | — | ➖ | neutral on speed; kept (halves buffer footprint) |
| + gcc PGO | 91.0 | 1.84× | — | ❌ | worse than gcc -O3; dead end (known pattern) |
| + gcc `-mcpu=neoverse-n1` | 95.2 | — | — | ❌ | no gain |
| + **clang++-19 -O3** | **81.3** | **2.06×** | — | ✅ | **+9.2% over gcc**; wired into Makefile (G2CXX) |
| + clang PGO | ? | ? | — | ⏸ | blocked: needs libclang-rt-19-dev + llvm-19 on dalby |

**Kernel levers settled at 2.06× (L1 + L3 + L4 + clang).** L2/L4/gcc-PGO/-mcpu
measured neutral-or-worse. L5 (size-(maxn-2) fusion) estimated ~3% for real
structural risk — skipped unless margin needed. clang PGO skipped (blocked on a
dalby package, speculative ~5%, and would add per-box build complexity; the
fleet already reaches ~14h).

## Fleet per-core throughput (N=15 single-core wall, clang builds)

| box | ISA | cores | N=15 wall | per-core vs dalby | dalby-core-equiv |
|---|---|---|---|---|---|
| dalby | Neoverse-N1 aarch64 | 80 | 81.3 s | 1.00x | 80 |
| ayr | x86-64 | 32 | 63.5 s | 1.28x | 41 |
| gympie | Apple Silicon (perf) | 10 | 27.1 s | 3.00x | 30 |
| **fleet** | | 122 | | | **151** |

Shard allocation proportional to dalby-core-equiv: **dalby 53% / ayr 27% / gympie 20%**.

## ETA (optimized kernel 2.06x, a(21) = 6.7614x the row-20 work)

- a(21) work = 7.23e6 dalby-core-s. **dalby-alone 26.1 h; fleet ~14 h** (<24h ok).
- **Reach frontier:** a(22) = 6.78x a(21) -> **fleet ~3.9 days** (was ~15 days
  dalby-alone pre-optimization) — now a feasible long run. a(23) ~27 days (no).
  Optimization+fleet moves the whole-row two-algorithm confirmation frontier to
  **21 (this run) and puts 22 in reach**. Re-confirm from the real a(21) run.

## P3 — validation ladder

- **gate-g2 GREEN** after every kept lever (fixtures/per-box/split/ASan/holes)
  plus new **check I** (aggregate pure-count path == per-box row-sums for
  square8/4/tri6; split-boundary-at-maxn sums to full).
- **Row-18 fleet: PASS.** dalby[0,96) aarch64 + ayr[96,145) x86 + gympie[145,180)
  Apple, K=180/S=10, gathered + centrally combined → all 18 rows match banked
  (a(18)=22471158811164, 0 mismatch). Validates the L1 pure-count path at scale,
  **cross-ISA agreement across 3 compilers/architectures**, and the fleet
  gather/combine plumbing in one run.
- **Key coverage note:** in a row-N run the pure-count path (L1) produces *only*
  row N (it fires at size==N-1). So row-18 validated the pure-count producing
  a(18); row-19 validates it producing a(19). The arithmetic (`numUntried + DEG -
  stale`, u64, no overflow until 9.2e18 ≫ a(21)=7e15) is n-independent, so these
  two scale points fully cover the identical path at n=21. A dedicated row-20
  re-run is therefore optional (a third point, no new coverage).
- **Row-19 fleet: PASS.** All 19 rows match banked (a(19)=151609203011580), gathered
  via `g2_fleet_gather.sh` (tar-per-box), 360/360 shards. Second scale point green.

## a(22) LAUNCHED 2026-07-11 13:41 (jasonp's go; supersedes a(21) — a(22) subsumes it)
`scripts/g2_fleet_launch.sh 22 12 24000`: dalby [0,12720)/80w, ayr [12720,19200)/32w,
gympie [19200,24000)/10w, tmux `0:g2_a22`, resumable, `runs/g2row_N22/`. K=24000 (finer
than a(21)'s 2400 for a multi-day run: shard ~34min/dalby-core, tail straggle ~0.6%,
redundant top-tree walk ~0.09%). Acceptance: rows 1..22 vs banked, **a(21)=6954084405510437,
a(22)=47255332844367680**. Both already TM-known; this is the independent Redelmeier
two-algorithm confirmation, moving that frontier 20 → **22**.

### Rebalanced 2026-07-11 16:40 (~2.9h in)
**The 3.9-day estimate was wrong** — it extrapolated single-core N=15 benchmarks to
all-core, which over-predicts throughput (shared memory bandwidth under all-core load).
Measured all-core per-core rates: dalby 1.386 shards/h/core (holds — server Neoverse),
**ayr 1.275 → all-core 0.92× dalby** (AMD Threadripper 2990WX: split-NUMA, half its
cores reach memory over Infinity Fabric; single-core bench said 1.28×), gympie 2.62×
(was 3.0×). Aggregate 188 shards/h → balanced floor ~5.3d, not 3.9d. Original
53/27/20 split made ayr the long pole (~6.6d) with dalby idle ~1.8d at the end.
**Fix:** re-partitioned into balanced contiguous ranges equalizing finish time
(accounting for the ~242 shards ayr/gympie lose from their current position, redone
by the box that now owns them — ~1% waste): **dalby [0,14300), ayr [14300,19460),
gympie [19460,24000)**. All finish ~129h ≈ **5.4 days** (~2026-07-17). No progress
lost (resumed from .done; ~120 in-flight shards redone). No contention on any box
(each cleanly at full load). **Lesson:** benchmark fleet boxes under *all-core* load,
not single-core, before allocating shares.

## a(22) COMPLETE 2026-07-16 — PASS (two-algorithm frontier now 22)
All 24000 shards ran to `.done`; ranges tile [0,24000) exactly (dalby [0,14300)
427974s wall, ayr [14300,19460) 418525s, gympie [19460,24000) 440745s — long pole
gympie ~5.1d). Gathered all boxes' `w*.out`/`w*.done` to gympie via tar-over-`ssh -T`
(rsync blocked by unclean remote shell banner), `scripts/g2_combine.sh runs/g2row_N22
22 24000` → `combined.txt`. Full column rows 1..20 match published **A006769**
(fixed polyplets) to the last digit; rows 21,22 match the banked TM values digit-for-
digit: **a(21)=6954084405510437, a(22)=47255332844367680**. Growth smooth/monotone
(a22/a21=6.7953, λ→~6.8). This closes the independent-reimplementation gap for a(21)
and a(22): the Redelmeier oracle and the varint TM engine now agree at the frontier.

## a(21) launch runbook (fleet, tmux — for P4, on jasonp's go)

Launch pattern (worked out on row-18/19; `-t 0:` = session 0 next free window):
```
# per box, in its existing tmux session 0, foreground + tee, resumable:
ssh <box> 'tmux new-window -t "0:" -n g2_a21 "cd ~/src/polyominoes && \
  scripts/g2_wholerow.sh 21 12 2400 <JOBS> --range <FROM> <TO> --no-combine \
  2>&1 | tee runs/g2row_N21.launch.log; exec bash"'
```
Ranges (K=2400, shares 53/27/20): **dalby [0,1272) JOBS=80**, **ayr [1272,1923)
JOBS=32**, **gympie [1923,2400) JOBS=10**. Expected wall ~14h.

**Waiting — robust, NOT `tail --pid`.** A single `tail --pid` over ssh can drop on
a network blip and falsely report completion (seen on row-19). Use a poll-waiter
(`/tmp/fleet_wait.sh` pattern) that per box checks: driver process dead AND the
driver.log "range [..) complete" success line present AND all range `.done` there;
declare done only when all three boxes satisfy all three. Poll ~5 min for a 14h run.

**Gather — tar per box, NOT per-file scp.** 2400 shards × 2 files = 4800 tiny files;
per-file scp is minutes-slow. On each box `tar czf /tmp/n21.tgz w*.out w*.done`,
scp the one tarball, extract into a single local dir. Then
`scripts/g2_combine.sh <dir> 21 2400` (verifies all 2400 shards present), and check
rows 1..20 vs banked + row 21 == **6954084405510437**.
