# Overlap + kink steal fix — scoped sketch, impact estimate, and what else could bite

**Date:** 2026-07-07. Follow-on to `a34-utilization-postmortem.md`. Sketch only —
no code changed, no job launched.

> **SUPERSEDED:** the §2-3 a(34) impact estimates were replaced with MEASURED numbers
> (the three scheduler fixes bought ~0) in `results/utilization-fix-and-ceiling.md`;
> and the reach-ladder day-counts here are obsolete — a(36) is banked (H19 long pole
> 3.28h via the varint engine, far under this sketch's projection).

## 1. The fix, scoped

Two independent pieces, both small, both already have a home in the existing
code:

**(a) `stealEligible`'s record-count floor → a wall-time floor**
(`orchestrator/sweep.go:909-914`). Today:

```go
func stealEligible(r *runningUnit, grainRecs uint64) bool {
    if r.stopped || r.u.noSteal || r.processed.Load() == 0 { return false }
    rem := r.remaining()
    return rem > grainRecs && rem >= 2*indexStride
}
```

`stealScore` (a few lines below) already computes an estimated-seconds-remaining
from the observed rate (`rem/rate`) — the fix is to gate eligibility on *that*
estimate crossing a wall-time grain (e.g. `cfg.StealGrain` fraction of a core's
fair share of the column's wall so far), not on raw `rem`. Concretely: compute
`estSec := rem / max(rate, epsilon)`; require `estSec > grainSeconds` in place of
`rem > grainRecs`. Keep the existing `rem >= 2*indexStride` clause unchanged —
that guard is about whether the `.idx` can physically cut the remnant, which is
still record-shaped and still correct. This is a one-function diff plus a config
field rename/addition; no new machinery.

**(b) Turn on `--overlap-heights` for kink production runs.** This turns out to
be *less work than expected* — checked the current code, not assumed:
`sweepHeightKink` (sweep.go:710) already threads `sem` and `activeHeights`
through `mapPhase` on every stage round, identically to the whole-column
`sweepHeight` (sweep.go:598). The shared-pool semaphore, the dynamic
`stealAllowed(activeHeights)` gate, and the height-boundary checkpoint machinery
are kernel-agnostic already — kink was built on top of them (Design 14 reused the
column DAG/checkpoint/telemetry deliberately), so **no wiring work is needed
here.** This is a config decision + validation, not a code change.
`orchestrator/guard_test.go` already asserts that a column checkpoint written
under one kernel can't silently be resumed under the other — the cross-kernel
correctness boundary was anticipated.

**(c) Validation gate before trusting either for a real term.** Per
`validate-at-scale-before-record`: extend `overlap_resume_test.go`'s kill/resume
matrix to run under `--kernel kink`, add a red-first unit test for the new
`stealEligible` wall-time floor (the record-count case in `steal_test.go` is the
template), then an a(29)/a(30) `--kernel kink --overlap-heights N --compare` full
run (cheap, minutes, not a beg-and-agree job) before trusting the combination for
a(35)+.

**(d) The one thing that has to happen first, and isn't a code change at all:**
the still-open question from `steal-tail-h18.md` — is the H18 tail many
separable heavy states or one pathological state? A cheap instrumented single
H18 column probe answers it. It gates how much (a) is worth; it doesn't gate
(b), which helps regardless.

## 2. Impact estimate for a34 — and why it's bigger than my last estimate, with a caveat

My previous estimate (steal-fix alone, map-phase only) gave ~1.85x realistic /
~5.05x idealized. Re-deriving with overlap in the picture changes the shape of
the argument, not just the number, because overlap and the steal-fix cover
*different* idle mechanisms — overlap fills gaps the steal-fix structurally
cannot (merge-phase idle, and any height's tail once its own map units are
truly exhausted) with *other heights'* genuinely available work, as long as
another height is still alive to supply it.

**The key constraint: overlap only helps while a sibling height is still
running.** a34's non-H18 heights sum to only 3,965s of wall (H3–H17), of which
H17 alone is 2,376s — the rest finish in well under a minute combined. So:

- **The first ~2,376s of H18's timeline** can draw on H17 (and everything
  below) as backfill — genuinely close to full-pool packing is plausible here,
  since total combined demand (H17+H18+lower, ~175k cpu-s cpu across that
  window) comfortably exceeds 80 cores' worth of supply.
- **The remaining ~75% of H18's timeline** runs with no sibling left — this
  portion is bounded purely by whatever the steal-fix (2a above) achieves
  *within* H18 alone, i.e. my previous 1.85x-realistic/5.05x-idealized range.

Rough combination: non-H18 heights' wall (3,965s) becomes close to free
(absorbed into H18's own idle capacity, which structurally has far more idle
core-seconds than 3,965s worth of other-height work to soak up). H18's own
9,335.5s splits into an early overlap-assisted stretch and a longer
alone stretch bounded by the intra-height fix. Combining:

| scenario | total a34 wall | vs 13,300s |
|---|---:|---:|
| conservative (only the diagnosed steal-eligibility bug fixed; overlap not combined, or contributes little beyond the free absorption of cheap heights) | ~6,000–8,000s | 1.7–2.2x |
| optimistic (both fixed, tail turns out splittable, overlap absorption works as hoped) | ~3,000–5,500s | 2.4–4.4x |

Both numbers are still short of the fully idealized 5.05x ceiling from last
time, because that ceiling assumed the alone-stretch of H18 also hits 100%
utilization — which nothing here can deliver (nothing to overlap with, once
alone). **The "H18 running alone at the end" stretch is the real floor** —
`results/scheduling.md` names this explicitly: "even at 100% bulk utilization,
the wall can't drop below the tallest height's serial column chain... at the
very end ... unrecoverable by *any* scheduler." That floor is real and
persists after both fixes.

## 3. Reach-ladder impact (same method as before, updated factor)

Applying 1.7–4.4x (vs the 1.8–5.05x range used last time — genuinely similar,
just re-derived with a clearer mechanism) to the standing HANDOFF ladder:

| term | unfixed | conservative (÷1.7–2.2) | optimistic (÷2.4–4.4) |
|---|---|---|---|
| a(36) | 1.9–3.0 d | ~0.9–1.8 d | ~0.4–1.3 d |
| a(37) | 8.2–13.1 d | ~3.7–7.7 d (crosses into a week) | ~1.9–5.5 d |
| a(38) | ~36–58 d | ~16–34 d (still out) | ~8.2–24 d (borderline at best) |
| a(39) | — | — | still clearly out |

**Conclusion is unchanged from last time, just on firmer footing:** the combined
fix plausibly buys about one more term (a(37) solidly reachable), a(38) stays
borderline-to-out even in the good case, a(39)+ stays out. The 4.4x/term growth
still dominates a one-time constant-factor scheduling win within about two
terms.

## 4. Other ways utilization could still fall behind the 80% goal — not yet measured, worth flagging before trusting any of the above

These are risks specific to the *combination* (kink + overlap, at record scale)
that nothing in the repo has tested, because the combination has never been run:

1. **Disk-bandwidth contention across concurrently-overlapped heights.** The
   engine's core design bet (`docs/engine-design.md` §0) is "NVMe seq out-runs
   random RAM 2–4x" — a claim about *one* height's sequential spill/merge
   stream. Overlap runs several heights' map/merge workers concurrently against
   the same NVMe device; the aggregate I/O pattern becomes several interleaved
   sequential streams, which on real hardware often degrades toward the
   random-access case the design explicitly avoided. Untested for kink+overlap
   at record scale.
2. **Merge's "a few workers" ceiling doesn't multiply for free.**
   `results/scheduling.md`: merge "saturates with a few workers (Amdahl + disk
   bandwidth)" *per height*. Under overlap with many heights alive at once
   (true early in a run, before the cheap heights drain), that's N ×
   "a few workers" of simultaneous merge demand — plausibly enough on its own
   to matter, in a phase the design otherwise treats as free backfill capacity.
3. **Kink's finer barrier granularity multiplies spawn/fork overhead.** The
   process-per-shard-unit design (`engine-design.md` D-1) was costed at
   "spawn cost <0.1%" against the old engine's one map+merge barrier per
   column. Kink's ~20 stage-rounds per column means ~20x more spawn waves per
   column; under overlap, multiple heights doing this simultaneously multiplies
   it again. Never re-costed for kink, let alone kink+overlap.
4. **RAM re-verification needed at a(35)+ scale, not just a(34) solo.** a34's
   measured 6.44 GB peak RSS is for kink running *one* height alone, at maxn=34.
   `results/scheduling.md`'s "RAM is not a constraint" conclusion was for the
   *old* engine at a(24)/(25) scale. Nobody has measured kink's co-resident RAM
   when several of the biggest heights (H16+H17+H18) are alive at once at
   a(35)+ scale, where each height's own frontier is itself ~2.4x bigger than
   the one below it. Plausible it's still fine (kink is RAM-light per state);
   not yet a fact.
5. **The kink+overlap+steal correctness surface is genuinely unexercised.**
   `guard_test.go` shows the team already anticipated cross-kernel checkpoint
   confusion, which is a good sign, but no test in the current suite actually
   runs the three-way combination (kink stage checkpoint × height-boundary
   overlap checkpoint × the fixed wall-time steal) together. This is a
   "haven't looked yet" risk, not a measured one — exactly what item 2c's gate
   is for.
6. **The utilization *metric itself* can hide a memory-bandwidth ceiling.**
   `cpu_s/wall_s/cores` reads as 100% whenever cores are *assigned* work, even
   if they're stalled on memory bandwidth rather than doing useful cycles. The
   PGO investigation (`pgo-no-go-dalby`) found the single-height case cache-fine
   (2.6% L1 miss) — but that was measured with one height's worth of processes
   on the box, not sixteen simultaneously under overlap. A genuinely fixed
   scheduler could report ~80% "utilization" by this metric while real
   throughput scales sublinearly, if aggregate memory bandwidth becomes the
   limiter at high overlap depth. Worth a `perf stat` bandwidth check under the
   validation-gate run in §1c, not just a wall-clock comparison.

None of these are known to be real — they're the honest list of "haven't
measured this yet" risks that sit between "diagnosed the bug" and "trust the
combination for a record run." Item 6 in particular is worth calling out
specifically because it would masquerade as success (a good utilization number)
while not delivering the wall-clock win the ladder in §3 assumes.
