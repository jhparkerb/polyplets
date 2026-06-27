# 03 — probe & calibration (the measurement that gates the a(21) launch)

This is methodology, not a code feature. It turns "the new engine does a(21) in ~8h"
from a back-solved claim into a measured projection, and decides whether
work-stealing is worth building.

## What the probe must answer

1. **Core utilization** — does the new engine actually saturate the cores, or does it
   idle like the old one? (The orchestrator barriers at sweep.go:302/381; unit-mult
   is the mitigation — does it work?)
2. **Work-stealing decision** — is static unit-mult enough, or do cores still drain at
   the column tail?
3. **Per-term scaling** — the real work ratio R between consecutive terms on *this*
   engine and box (do not assume 4.4).
4. **Predictor validation** — does the doc-02 a-priori predictor predict a(20) from
   a(19) within tolerance?
5. **Correctness bonus** — a(19) and a(20) are known; `--compare` checks them (higher
   than any current gate, which stops at n≤18).

## Preconditions

- dalby idle (done 2026-06-27).
- Build current `next-system` HEAD on dalby with unit-mult (doc 01) and progress A+B
  (doc 02) compiled in.
- Add a(19), a(20)=1,025,573,519,362,016 to `fixtures/b006770.txt` so `--compare`
  validates them (known.go / main.go:141–167 read this file; values fit u64).

## Runs

All on dalby, idle box, `--cores 80`, `--counter u64`, spill on NVMe.

| Run | Command (sketch) | Purpose |
|-----|------------------|---------|
| P1 | `orchestrate --maxn 19 --compare --unit-mult 1` | baseline util + correctness |
| P2 | `orchestrate --maxn 19 --compare --unit-mult 4` | util vs granularity |
| P3 | `orchestrate --maxn 19 --compare --unit-mult 8` | find the merge-fan-in knee (doc 01) |
| P4 | `orchestrate --maxn 20 --compare --unit-mult <bestK>` | n=20 correctness + predictor validation |

a(19) is small (minutes), so sweeping K is cheap. Capture per run: wall, the
`event=column` trace (doc 02-A), peak RSS, spill bytes, and core occupancy over time
(from the heartbeat if doc 02-C is in, else an external 1 Hz `ps`/`mpstat` sampler —
named on-disk sampler, not a one-liner).

## Decision rules (stated up front so they can't move)

- **unit-mult knee**: pick the K maximizing a(19) throughput. If wall worsens
  4→8, the knee is 4 (merge fan-in dominating).
- **Work-stealing**: at best K, plot core occupancy vs time per column. If occupancy
  holds ≳85% to each column's end → static unit-mult suffices, **do not** build
  work-stealing. If cores still drain at the tail at K=8 → a single unit is too coarse
  to subdivide statically; schedule a work-stealing design.
- **Predictor**: `|predicted_wall(a20) − actual| / actual < 25%` → trust the a(21)
  prediction. Otherwise recalibrate R and re-derive before launching a(21).
- **Launch gate for a(21)**: P1–P4 `--compare` all PASS *and* predictor within
  tolerance. Then record the **earned** a-priori a(21) wall/RAM/disk band and launch.

## Outputs

A results doc `results/ns-probe-<date>.md` with the measured table (wall, RSS, spill,
occupancy, R, predictor error per run) and the three decisions (best K, work-stealing
yes/no, a(21) projection). This is the artifact that replaces the rabbit-out-of-hat.

## Effort

~1–3h wall (mostly a(20) compute), negligible engineering beyond the external
sampler if heartbeat (doc 02-C) is deferred.
