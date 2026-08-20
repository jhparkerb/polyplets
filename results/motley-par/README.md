# motley_par — the parallel Motley engine, and its receipts

2026-08-20, branch `lastditch`. Source `cpp/motley_par.cpp`, gate
`tests/gate_motley_par.py`. Every number below is in a file in this directory.

`docs/b1-closure-plan.md` §4 named the wall this removes and left it standing:

> The engine is still single-threaded. Everything above is per-process peak
> RSS, which is what the budget constrains; the wall figures ... demand a
> parallel frontier that does not exist yet. RAM is the wall this document
> plans around; cores are the next one.

Confetti (H = 18) spent 399,700 s of wall on **one core of an 80-core box**.

## The rule is not mine to change

`slot`, `canon`, `gather`, `shifted` and `successors` are transcribed
character for character from the frozen spec
`results/cutcount_b1/cutcount_b1.cpp.59e90660` lines 93-173 — what
`docs/proofs/cutcount-identity.md` proves and what every banked `C_H` row was
produced by. Everything else in the file is accounting, and the gate is that
the rows come out byte-identical.

## What is different

- open-addressed flat table + a contiguous payload slab, instead of
  `unordered_map` plus one heap `vector` per state per cell-step;
- the cell-step is an OpenMP loop over source rows, lock-free find-or-insert,
  and a spinlock living in the row it protects;
- payload width chosen from the prime (u8 / u16 / u32);
- **rung G, "chunked release of the consumed buffer"** — the change §3 calls
  the fiddliest and prices at 1.7x. Buckets went 24 B -> 8 B (the key lives
  once, in its payload row, which is also what lets the step iterate rows and
  therefore release them); `IDX_EMPTY` moved to zero so `clear()` is a
  `MADV_DONTNEED` rather than a memset (~7 TB of memset that does not happen
  at H = 20); and each chunk's pages go back the moment it is consumed;
- `--census --sizes-out` writes exact per-cell-step state counts and
  `--modp --sizes` pre-sizes from them. Release is only sound without regrow
  retries — a retry re-reads a source already handed back — so with sizes an
  overflow is **fatal**, not silently retried;
- column-boundary checkpoint / resume.

## Receipts

| file | what |
|---|---|
| `serial-baseline.txt` | `cutcount_b1 --modp` single-thread, H = 10..14 |
| `thread-scaling.txt` | `motley_par` at 1 / 8 / 32 / 80 threads, H = 13, 14 |
| `h18-reproduction.log` | ayr: all five banked Confetti residue rows |
| `h18-release-gate.log` | dalby: the release path vs a banked row |
| `sizes.H19.N40.txt` | the H = 19 census, 779 cell-steps |

### Thread scaling, H = 14 / Nmax 40 / one 31-bit prime, dalby

| threads | 1 | 8 | 32 | 80 | `cutcount_b1` |
|---|---|---|---|---|---|
| wall s | 323.3 | 41.2 | 13.1 | **11.8** | 596.0 |
| RSS MB | 718 | 718 | 693 | 733 | 1048 |

27x on cores, 1.84x before any core is added, **50x end to end**, and
byte-identical at every thread count.

### The five banked H = 18 residue rows, ayr, 32 threads

    p=2147483647 wall=3316.25  IDENTICAL to banked Confetti row
    p=2147483629 wall=3318.71  IDENTICAL
    p=2147483587 wall=3360.64  IDENTICAL
    p=2147483579 wall=3415.48  IDENTICAL
    p=2147483563 wall=3380.87  IDENTICAL
    ALL FIVE BANKED H=18 RESIDUE ROWS REPRODUCED

Frontier `states=72487711` — the count HANDOFF records for Confetti.
**~3350 s per prime against ~79,940 s.**

### The release path, dalby, 80 threads

    census H=18            wall=  573.75  rss= 6.65 GB
    modp H=18 p=2147483647 wall= 1731.68  rss=32.06 GB   RELEASE
    H=18 RELEASE PATH: IDENTICAL to the banked Confetti residue row -- GREEN

Against ayr's 60.2 GB for the same height and payload **without** release:
**0.53x**. Rung G does what it was built to do.

### The H = 19 census

**224,529,648 states**, saturated at column 1 — measured, replacing the
±20% projection band of `docs/b1-closure-plan.md` §2. Per-state cost derived
from the H=18 release measurement is 445 B at stride 352, giving:

| H = 19 payload | B/state | total | passes | wall |
|---|---|---|---|---|
| u16, 9 primes | 243 | **59 GB** | 9 | ~15 h |
| u32, 5 primes | 445 | 101 GB | 5 | ~8 h |

u16 was taken: 101 GB on a 125 GB box is 83%, and the H=18 prediction came in
34% under the measurement, which is the margin that becomes an OOM.

## Gate

`tests/gate_motley_par.py` checks three things and the first is the one that
matters:

1. **rule** — every `C_H(n) mod p` against the banked exact rows
   `results/cutcount_b1/rows/`, at three payload widths. Agreeing with those
   is agreeing with the rule, not with my transcription of it.
2. **implementation** — byte-identical to `cutcount_b1 --modp`.
3. **determinism** — thread count changes no digit.

**GATE GREEN: 1560 cell-comparisons, H = 1..13**, both RED controls firing.
Extended to H = 17 and H = 18 by the release-gate and reproduction runs above.

## Two bugs worth naming

- An 8-bit payload makes the row 90 bytes, and a misaligned `atomic<u32>` is a
  **SIGBUS on aarch64**, not a slow path.
- Moving `IDX_EMPTY` to zero silently made `find_or_insert`'s failure value
  collide with row 0, which zeroed every answer. The gate caught it, which is
  the point of the gate.

The first cut also scaled 4x while burning 76 cores — one global row counter
and spinlock bytes packed 64 to a cache line.
