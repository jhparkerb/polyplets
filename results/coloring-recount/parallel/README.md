# coloring_recount: the parallel coloring recount

Source `cpp/coloring_recount.cpp`, gate `tests/gate_coloring_recount.py`, 2026-08-20.
Every number below is in a file in this directory.

The original coloring program (`results/coloring-recount/`) is single-threaded;
its H = 18 run took 399,700 s of wall on one core of an 80-core machine.
`coloring_recount` is the same counting rule on many cores.

## The rule is unchanged

`slot`, `canon`, `gather`, `shifted` and `successors` are transcribed
character for character from `results/coloring-recount/cutcount_b1.cpp.59e90660`
lines 93-173, the rule that `docs/proofs/cutcount-identity.md` proves and
that every stored `C_H` row was produced by. Everything else in the file is
bookkeeping, and the gate is that the rows come out byte-identical.

## What is different

- an open-addressed flat table with a contiguous payload slab, instead of
  `unordered_map` plus one heap `vector` per state per cell-step;
- the cell-step is an OpenMP loop over source rows, lock-free find-or-insert,
  with a spinlock living in the row it protects;
- payload width chosen from the prime (u8 / u16 / u32);
- chunked release of the consumed buffer: buckets went from 24 B to 8 B (the
  key lives once, in its payload row, which is also what lets the step
  iterate rows and release them); `IDX_EMPTY` is zero so `clear()` is a
  `MADV_DONTNEED` rather than a memset; each chunk's pages go back the
  moment it is consumed;
- `--census --sizes-out` writes exact per-cell-step state counts and
  `--modp --sizes` pre-sizes from them. Release is only sound without
  regrow retries (a retry re-reads a source already handed back), so with
  sizes an overflow is fatal rather than retried;
- column-boundary checkpoint and resume.

## Files

| file | what |
|---|---|
| `serial-baseline.txt` | `cutcount_b1 --modp` single-thread, H = 10..14 |
| `thread-scaling.txt` | `coloring_recount` at 1 / 8 / 32 / 80 threads, H = 13, 14 |
| `h18-reproduction.log` | ayr: all five stored H = 18 residue rows |
| `h18-release-gate.log` | dalby: the release path against a stored row |
| `sizes.H19.N40.txt` | the H = 19 census, 779 cell-steps |

### Thread scaling, H = 14, Nmax 40, one 31-bit prime, dalby

| threads | 1 | 8 | 32 | 80 | `cutcount_b1` |
|---|---|---|---|---|---|
| wall s | 323.3 | 41.2 | 13.1 | 11.8 | 596.0 |
| RSS MB | 718 | 718 | 693 | 733 | 1048 |

27x from cores, 1.84x single-threaded, 50x end to end, byte-identical at
every thread count.

### The five stored H = 18 residue rows, ayr, 32 threads

    p=2147483647 wall=3316.25  IDENTICAL
    p=2147483629 wall=3318.71  IDENTICAL
    p=2147483587 wall=3360.64  IDENTICAL
    p=2147483579 wall=3415.48  IDENTICAL
    p=2147483563 wall=3380.87  IDENTICAL

Frontier `states=72487711`, as in the original run. About 3350 s per prime
against about 79,940 s.

### The release path, dalby, 80 threads

    census H=18            wall=  573.75  rss= 6.65 GB
    modp H=18 p=2147483647 wall= 1731.68  rss=32.06 GB   RELEASE
    H=18 RELEASE PATH: IDENTICAL to the stored residue row

Against ayr's 60.2 GB for the same height and payload without release:
0.53x.

### The H = 19 census

224,529,648 states, saturated at column 1. Per-state cost derived from the
H = 18 release measurement is 445 B at stride 352, giving:

| H = 19 payload | B/state | total | passes | wall |
|---|---|---|---|---|
| u16, 9 primes | 243 | 59 GB | 9 | ~15 h |
| u32, 5 primes | 445 | 101 GB | 5 | ~8 h |

u16 was used: 101 GB on a 125 GB machine is 83%, and the H = 18 prediction
had come in 34% under the measurement.

## Gate

`tests/gate_coloring_recount.py` checks three things:

1. rule: every `C_H(n) mod p` against the stored exact rows
   `results/coloring-recount/rows/`, at three payload widths;
2. implementation: byte-identical to `cutcount_b1 --modp`;
3. determinism: thread count changes no digit.

Green at 1560 cell-comparisons, H = 1..13, with both controls firing.
Extended to H = 17 and H = 18 by the release-gate and reproduction runs
above.

## Two bugs found on the way

- An 8-bit payload makes the row 90 bytes, and a misaligned `atomic<u32>`
  is a SIGBUS on aarch64, not a slow path.
- Moving `IDX_EMPTY` to zero made `find_or_insert`'s failure value collide
  with row 0, which zeroed every answer; the gate caught it.

The first version scaled only 4x on 76 cores: one global row counter, and
spinlock bytes packed 64 to a cache line.
