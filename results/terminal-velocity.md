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
