# Fan-In Tax — dalby was paying ~75% of worker CPU to open files (2026-07-23)

Thread: **Fan-In Tax** (branch `second-wind`, commits 4cb8a95 / 3d168e1 /
58033a2). Found while running the second-wind dalby deploy checklist: the
H15/maxn30 bench A/B meant to pin the buffered-IO win instead exposed a
dalby-shaped pathology the gympie profiling never saw.

## The symptom

`bench_util.sh` H15/maxn30 on dalby: **336s wall / 20,106 cpu-s** on both
`master` and pre-fix `second-wind` (verified fresh per-rev builds) vs the
recorded post-Even-Keel baseline **140.9s / 4,554 cpu-s** (docs/
full-utilization-redesign.md D5). The branch's gympie-measured 3.36x
buffered-IO win did not reproduce at all on dalby. Not frequency (cores
verified ramping to 3.0GHz under load), not a stale binary (rev stamps
checked both runs).

## The mechanism (measured, not theorized)

- `perf` (system-wide): ~33% of ALL box cycles in `__arch_copy_to_user`
  under `filemap_read` (page-cache reads), mostly merge_worker; map-side
  `__pi_clear_page` (anonymous-page zeroing) ~10%.
- `/proc/PID/io`: **342 GB of logical reads in 20s (~17 GB/s)** against a
  ~350MB live run dir — read amplification ~10^3-10^4.
- `strace` on a live map_worker: per work unit, EVERY input range file of
  the previous round is opened — header read + on-disk `.idx` binary
  search + buffer setup — even though a unit's [lo,hi) overlaps ~1-2 of
  the ~74-80 files. ~640 units x ~80 files ≈ **51k open/seek sequences
  per round**, ~25M per run, ~0.45ms each.
- gdb stack samples on merge_workers pinned the remainder: request lines
  (~25KB, listing every map output) read one BYTE per
  `stdio_sync_filebuf::underflow` via `std::getline(std::cin)`; and every
  reader's fixed 256KB buffer crossing glibc's mmap threshold, so each of
  ~18M reader instances paid an mmap+page-zero+munmap cycle.

Why gympie never showed it: 10 cores x mult 8 = 80 units vs dalby's 640,
and ~10 merge ranges vs 74 — the (units x inputs) pair count is ~59x
smaller, and macOS's per-byte stdio cost drowned everything else anyway.
The buffered-IO fix was real but attacked the per-byte term, which was
never dalby's problem.

## The fixes (all format-neutral; full ns-gates + dalby a(26)
## production-shape validation green after each)

1. **Per-unit input pruning** (orchestrator): map units receive only the
   input files whose stamped `[keylo,keyhi)` overlaps their `[lo,hi)`;
   bounds parsed once per round. Unstamped files never pruned; an empty
   prune falls back to the full list. Red-first
   `orchestrator/prune_inputs_test.go`.
2. **Merge-range record cap**: `mergeRangeCount` caps fan-out so each
   range carries ≥2048 records (mirrors mapPhase's `minPerUnit`) — a tiny
   stage table no longer gets cut into cores x mult ranges.
3. **Peek-sized reads**: adaptive body fill (8KB doubling to 256KB, reset
   on seek) + 512B stdio buffers on the header and `.idx` handles — a
   heap-init peek costs ~16KB, not ~285KB.
4. **Arena-sized buffers + bulk request reads**: reader buffers grow with
   the adaptive fill (8KB peeks stay malloc-arena-served, reused across
   readers); persistent workers read request lines with POSIX
   `getline(3)`.

## Measured (dalby, bench_util.sh H15/maxn30, identical flags)

| build                    | wall (s) | cpu-s  |
|--------------------------|---------|--------|
| master / pre-fix branch  | 336-344 | 20-21k |
| + pruning & merge cap    | 204.6   | 10.3k  |
| + peek reads             | 184.9   | 9.3k   |
| + arena bufs & getline   | **104.5** | **3.9k** |
| (old D5 baseline)        | 140.9   | 4.6k   |

**3.2x wall / 5.2x cpu vs the same code's own dalby A/B; 1.35x faster
than the pre-varint D5 baseline with fewer total cpu-s.** Validation:
full ns-gates (55) each step; `dalby_term.sh 26` full production-shape
run on dalby — b-file a(1)-a(20) exact, chain a(21)/a(26) exact
(A26_VALIDATE_PASS).

## Consequences for the ladder

- The buffered-IO "1.5-3x on the dalby pole" prediction in
  results/second-wind.md was gympie-reasoning; dalby's real tax was
  fan-in, now fixed. Pole-scale factor still to be measured on a real
  frontier run.
- Mid-height full sweeps (many columns x H+2 rounds each) were the
  fan-in tax's biggest real-run victims — this is a whole-run wall win,
  not just a bench win.
- a(38)'s real H20 sweep produces T(37,20) — P_17's first independent
  holdout — so the a(37)-strict route is subsumed by running a(38): do
  a(37) trusted, then a(38), and P17 gets certified for free. a(38) also
  yields both P_18 fit points (T(37,19), T(38,20)); wiring P_18 makes
  a(39)'s top real height H20 again (≈ a(38) cost). P_19 then needs
  T(40,21): a(40) is the first term needing a real H21 sweep
  (~2.1x H20, and ~280-350GB disk vs dalby's 214G free — measure H20's
  actual footprint during a(38) before deciding).
