# Spring Clean — deferred items & judgment calls (for review)

A 4-part parallel simplification sweep over the engine after the 12-fix batch. The
**safe set was applied** (commit `1c4498f`, validated by the full Go suite + C++
-Werror + gate_runfile + a(17)/a(19) `--compare`). This file records what I
**deferred** and the **judgment calls** I made under the "safest option when
uncertain" directive — all yours to override.

## Applied (safe, validated) — `1c4498f`
Dead `#include <algorithm>`; dead `RunFileWriter` default ctor (also a latent
uninit-member trap); unified `.idx` header constants; dead `RunRef.KeyLo/KeyHi`;
`SplitRangeByIndex` de-dup → `subsampleEvenly`; dead `WorkerResult.Err`; vestigial
`telemetry.cols`; `topHeightClosedForm` → `pow3`.

## Deferred — safe but too churny to do right before the reach runs
Each is **proven behavior-preserving**; I held them because they touch freshly-
written injection/format code and the value is cosmetic. Good for a non-record window.

1. **Pole/Diagonal merge** (`sweep.go`). `contributePoleHeight` computes a row
   byte-identical to `contributeDiagonalStrip(maxn, 1, …)` (the dispatch guards
   even match: both need `maxn≥4`). Folding `k=1` into the diagonal branch and
   deleting the function removes ~20 lines of duplicated proven-formula code in
   both `Run` and `runOverlap`. Needs `poleheight_test.go` repointed. **Highest-
   value cleanup**, but it's a structural change to the injection dispatch I just
   extended to k≤6 — defer until after the reach runs. (Gate-testable when done.)
2. **`Run` vs `runOverlap` dispatch dedup** — the two closed-form dispatch blocks
   duplicate 5 strip cases each. Factoring means threading the `mu.Lock()`-vs-no-
   lock distinction through a helper; a botched extraction drops a lock → data race
   on `triangle`. Defer; do item 1 first (it deletes one case from both).
3. **`forEachKV` helper** — `parseEventDone`/`parseConfig`/`parseAcct` share a
   `for field := range Fields { Cut("="); switch }` scaffold. A small callback
   helper de-dups the scaffold (switch bodies unchanged). Touches parse code; modest.
4. **`readIdxHeader` helper (C++)** — extract the reader's `.idx` header read+
   validate in `seekToKey`; pairs naturally with the shared constants now in place.
5. **`lowHeightRow` flatten** — `switch n {case 2…3…default}` → two seed assigns +
   a `for n:=4` loop. Pure readability, proven equivalent.
6. **Redundant `n >= 0` bound checks** (`sweep.go` accumulate loops) — `n` is a
   non-negative index/count; the lower guard is dead. Cosmetic; one reads C++
   worker output, so zero-risk only on the pure-Go-index site.

## Judgment calls (chose the safer option; flagging for you)
- **`WorkerResult.SpillBytes` — KEPT.** It's parsed (`spill_bytes`) but read
  nowhere, so removal would be behavior-preserving. I kept it because it reads like
  *half-wired observability* (the worker emits it; the orchestrator just doesn't
  surface it yet) — removing intended-future wiring is the less-safe call. **Your
  call:** delete it, or wire it into the cost profile.
- **`orchestrator.VerifyCRC` — KEPT, flagged.** Genuinely has **no production
  caller** (the only test exercises `verify/verify.go`, a different symbol). But
  it's exported API and a stated B3 corruption backstop, so removing it is a
  deliberate API decision, not a mechanical cleanup. **Your call.**

## Rejected (correctly left alone — byte/offset/count/timing-sensitive)
LE byte-pack helper (would shift on-disk bytes/CRC); `combine()` loop merge (load-
bearing overflow asserts, different sources/offsets); `bytesCompare` → `bytes.Compare`
(unverified equivalence feeds cut selection); `estPer`/`stopped`/`noSteal` (scheduler
internals — change steal decisions); `record_est` (a tuned Budget-Blind calibration).
