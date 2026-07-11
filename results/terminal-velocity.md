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
