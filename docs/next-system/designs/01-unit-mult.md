# 01 — unit-mult: decouple work units from core count

## Problem

In `orchestrator/sweep.go` the number of work units equals the core count:

- `mapPhase`: `numUnits := cfg.Cores` (sweep.go:254)
- `mergePhase`: `numRanges := cfg.Cores` (sweep.go:334)
- concurrency semaphores: `make(chan struct{}, cfg.Cores)` (sweep.go:274, 357)

So one unit ≈ one core, and each phase ends at a barrier (`wg.Wait()`, sweep.go:302
and 381). Unit cost is **not** uniform by key — heavy states cluster — so fast
units finish and their cores idle at the barrier while the tail unit runs alone.
There is no work-stealing. On a heavy column this can waste a large fraction of the
box near the column tail.

## Design

Decouple unit count from concurrency:

```
numUnits   = cfg.Cores * cfg.UnitMult   // more, finer units
semaphore  = cfg.Cores                   // unchanged: still ≤cores running
```

Finer units mean a core that finishes early pulls the next queued unit instead of
idling to the barrier. This *approximates* work-stealing without any stealing code:
the tail shrinks to one small unit instead of one core-sized unit. Peak RAM is
unchanged (still ≤cores workers resident). The partitioner already supports it —
`SampleKeysMulti(frontier, H, numUnits-1)` (sweep.go:259) and `cutsToBounds`
(sweep.go:403) take an arbitrary cut count.

## Implementation

Files: `orchestrator/sweep.go`, `orchestrator/cmd/orchestrate/main.go`.

1. `SweepConfig` (sweep.go:21): add `UnitMult int // units per core (default 1)`.
2. mapPhase (sweep.go:254):
   ```go
   mult := cfg.UnitMult; if mult < 1 { mult = 1 }
   numUnits := cfg.Cores * mult
   ```
   Semaphore at 274 stays `cfg.Cores`.
3. mergePhase (sweep.go:334): `numRanges := cfg.Cores * mult` (same guard). The
   existing cap `if numRanges > len(mapOuts)` (sweep.go:338) still applies;
   semaphore at 357 stays `cfg.Cores`.
4. CLI (main.go:32–43): `unitMult := flag.Int("unit-mult", 1, "work units per core")`;
   set `UnitMult: *unitMult` in the cfg literal (main.go:81–93); echo it in the
   launch banner (main.go:95).

No change to workers, sampling, or checkpoint format.

## Cost / risk — the merge fan-in ceiling

`mergePhase` gives every merge worker **all** map outputs (`InPaths: mapOuts`,
sweep.go:369) and a key sub-range. With M = `cores*mult` map files and R =
`cores*mult` merge ranges, total file-opens per column ≈ M·R = (cores·mult)². At
cores=80, mult=8 that is ~410k opens/column, plus mult× more small spill files
(`map_h*_c*_u*.bin`). So unit-mult has a **knee**: past some mult the merge
all-to-all and small-file overhead outweighs the reduced tail-idle. This is exactly
why the probe (doc 03) sweeps mult∈{1,4,8} and measures wall, rather than assuming
"more is better." If the knee is below the granularity needed to kill tail-idle,
that is the signal that real work-stealing (not just finer static units) is needed.

## Gates / acceptance

- `ns-gate-parallel` (`orchestrate --maxn 16 --compare`) must PASS unchanged at
  `--unit-mult 1`, `4`, `8` — result invariance under unit count. Add the mult
  variants to the gate (Makefile `ns-gate-parallel`).
- Acceptance: a(16) byte-identical across mults; probe shows higher tail-time core
  occupancy at mult>1 with wall improving up to the knee.

## Effort

~1–2h including the gate additions.
