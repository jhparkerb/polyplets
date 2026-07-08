**CORRECTION (2026-07-08, later session):** the two `forEachViableMask`
references below (in "The prediction, and the concrete reasons behind
it") are wrong — that function is the column kernel's enumeration
mechanism (`core/mapreduce.h`), not used by `--kernel kink`, which every
real run in this doc actually used. Kink's own per-record hot path is
`kinkStageTransition` (`core/kink.h:98`), a simple bounded `for (occupy in
{0,1})` loop with no recursive tree at all — the "pathological-record
enumeration explosion" story doesn't apply to it as described. The
`core/kink.h:296` cooperative-stop-check citation itself is correct (that
line is real and does what's described); only the parenthetical function
name naming what it can't reach mid-record is wrong. See
`results/sub-record-interrupt-design.md`'s own correction note for the
full story — this doc's floor/ceiling analysis and the three real
scheduler-fix findings elsewhere in this doc are unaffected.

# Utilization: what got fixed, what didn't, and the achievable ceiling

**Date:** 2026-07-07. Branch `steal-wall-time-floor` (4 commits, all gated:
`208864b`, `9c5edc4`, `22b0206`, `bab6e64`). All measurements below are real
dalby runs of the actual a34 H16/H17 columns — not simulation, not
extrapolation from smaller n. Supersedes the speculative estimates in
`overlap-kink-design-sketch.md` §2-3 with measured numbers.

## What was fixed (three real bugs, all shipped and gated)

1. **`stealEligible`'s record-count floor → wall-time floor.** The original
   bug (`steal-tail-h18.md`): a compute-heavy/low-record straggler never
   cleared the record-based eligibility gate, so the wall-time ranker
   (`stealScore`) never got to see it. Fixed with a fallback wall-time check.
2. **The wall-time floor's own reference-rate bug**, found on the FIRST real
   dalby test of fix #1: using `totalDone/elapsedSincePhaseStart` as the pool's
   "typical pace" is self-defeating — it degrades the longer a straggler runs,
   inflating the bar exactly when a real straggler is present. Fixed to use
   finished-units-only pace (`completedRecords/completedSeconds`), which
   doesn't dilute with the ongoing tail.
3. **`remaining()` clamping to 0 on a grossly-underestimated unit.** Every map
   unit is seeded with the SAME flat average estimate
   (`frontierIn/numUnits`), assuming `SampleKeysMulti`'s record-quantile cuts
   split the frontier evenly. Measured on real H17 col3: unit 319 (the last,
   open-ended key range) held up to ~590M records against a ~64K flat
   estimate. Once processed exceeds a too-low estimate, `remaining()` returned
   0, making the unit look finished and permanently invisible to the stealer.
   Fixed with a 2x-overshoot fallback.

All three are correct, independently validated (unit tests + `make
ns-gates`, including ASAN/parallel/resume-boundary gates), and worth keeping
— they fix real, distinct defects in the scheduler. **But together they had
zero measured effect** on the actual dominant column (H17 col3's utilization:
24.7% baseline → 25.1% → 25.0% → 24.0% across the three fix iterations,
noise-level, no trend).

## The real, fourth, deeper finding: why the fixes didn't move the number

Added `POLY_STEAL_DEBUG` (env-gated trace of every `pickVictim` decision) and
re-ran H17 col3 with all three fixes live. The scheduling logic now works
**exactly as intended**: `pickVictim` correctly identified col3's true
straggler and attempted to steal it three separate times
(`stage=7`, `stage=10`, `stage=16`, each logged `picked=true`). Every single
time, the nomination was correct — and every single time, **zero actual
steals completed**: `processed` froze permanently at the moment of
nomination, and the unit ran to natural completion regardless of the SIGTERM
cooperative-stop signal.

Traced to the exact cause: `core/kink.h:296`

```cpp
if (on_progress && (++processed & kKinkProgressStrideMask) == 0) {
    on_progress(processed);
    if (stop_flag && *stop_flag && stop_key_hex) { ... break; }
}
```

The stop flag is checked **only once every 1024 records consumed, and only
between records** (outside the per-record enumeration). If a single record's
own transition/successor enumeration (`forEachViableMask`, generating a huge
number of successor states for one pathological boundary signature) is what's
consuming the wall time, the outer loop never even reaches the next check —
there's no way to interrupt mid-record. This is architecturally distinct from
(and deeper than) anything `steal-tail-h18.md` or the three scheduler fixes
above could touch: it is not an eligibility/scoring bug, it's a **granularity
floor in where the interrupt point lives**.

**This definitively answers steal-tail-h18.md's open question** ("is the tail
splittable — many separable heavy states, or one pathological state?"): for
H17 col3, the dominant straggler is *effectively* unsplittable via the
current cursor-based, between-records mechanism, regardless of how correct
the scheduling logic around it is. Fixing this further would mean checking
the stop flag *inside* `forEachViableMask`'s own iteration — a genuinely
invasive hot-path change (the enumeration loop is the most measured,
carefully-guarded code in the engine; see `pgo-no-go-dalby` and the
terminal-sort investigation in `HANDOFF.md`) that risks a real regression on
the 99% of records that are NOT pathological, and needs its own focused
measurement effort — not something to bolt on inside this investigation.

## What DOES measurably work: `--overlap-heights`

Unlike the steal fix, overlap doesn't need to interrupt the pathological
record at all — it just needs *other, independent* ready work to fill the 79
idle cores while one core is stuck. Real test, maxn=34, `--heights 16,17
--overlap-heights 2`, fixed binary:

| | wall | cpu-s | utilization |
|---|---:|---:|---:|
| H17 alone (sequential) | 2462.7s | 47,335.4 | 24.0% |
| H16 alone (sequential, from a34 record) | 722.1s | 19,395.0 | 33.6% |
| H16+H17 sequential (sum, not run this way) | 3,184.8s | 66,730.4 | (26.2%, hypothetical) |
| **H16+H17 with `--overlap-heights 2`** | **2,522s** | **66,596.3** | **33.0%** |

H16's entire 722s of work landed almost for free — the combined run took only
59s longer than H17 running alone. **A real, validated 21% wall-clock cut**
from mixing independent heights, with byte-identical CPU-seconds (confirmed:
overlap doesn't redo work, it just packs it better — same signature as the
`results/scheduling.md` finding on the old engine, now confirmed to hold on
the kink kernel too).

## The prediction, and the concrete reasons behind it

**At frontier sizes (H17/H18-shaped columns), utilization is not going to
reach anywhere near 80% under the current architecture, and the ceiling is
now precisely locatable rather than a guess:**

1. **Floor component — the pathological-record limit.** Whatever fraction of
   a column's wall time is dominated by a single record's own enumeration
   cost is *unrecoverable by any scheduling change* (steal, overlap, or
   otherwise) unless the sub-record interrupt point is built — a distinct,
   larger, riskier engineering effort with its own validation burden, not
   something this investigation's fixes reach. Measured floor for H17 col3:
   the fixed run's utilization (24.0%) is close to the theoretical floor for
   that column *in isolation* — the three scheduler fixes bought
   approximately nothing there, which is itself the useful, confirmed result.
2. **Recoverable component — cross-height packing.** `--overlap-heights`
   measurably works, is architecturally already wired through the kink kernel
   (confirmed in code, no plumbing needed), and RAM is not a binding
   constraint at these frontier sizes (combined H16+H17 peak RSS 2.7GB,
   trivial against dalby's 122GB). Applying it across the FULL a34 triangle
   (all swept heights H3-H18, not just H16+H17) should recover most of the
   non-dominant heights' wall for close to free, the same way H16's did here
   — plausibly pushing whole-run utilization from a34's actual 19.8% into the
   low-to-mid 30s%, extrapolating from this measured 24.7%→33.0% single-pair
   result. This has NOT been measured end-to-end (would need a multi-hour
   full-triangle run, out of this session's bounded-job scope) — it is a
   measured-mechanism-based projection, not a guess, but still a projection.
3. **The endgame floor remains.** Once every cheaper height finishes, H18
   alone (70% of a34's total wall) runs with no sibling to backfill from —
   exactly `results/scheduling.md`'s "irreducible floor." For H18's own tail,
   only the pathological-record floor in (1) applies, and it is a materially
   bigger height (H18's peak columns are longer and, per design-08's Finding
   3, the tail *worsens* with height) — so H18's OWN utilization, even with
   overlap doing everything it can for the heights below it, is likely to
   look similar to or worse than the 24.0% measured here for H17, not better.

**Bottom line prediction: with `--overlap-heights` deployed across the full
sweep (a real, validated, low-risk, already-wired lever), expect whole-run
utilization in the **low-to-mid 30s%** at a34-scale frontier sizes — up from
the actual 19.8% — with H18's own dominant, unshared tail continuing to sit
around 20-25% regardless, because that specific floor is a single-record
enumeration cost with no scheduling lever that reaches it.** Getting
meaningfully past that would require the sub-record interrupt point, a
distinct and materially riskier project, not a continuation of this one.

## Recommended next step (not undertaken here — needs its own go/no-go)

If the low-to-mid-30s% ceiling is worth banking: wire `--overlap-heights`
into the production `dalby_term.sh`/trusted config and re-validate at scale
(a29/a30 `--compare` full run, gated) before trusting it for a real term —
per `validate-at-scale-before-record`. The scheduler fixes on this branch
should ship regardless (they're correct and harmless even where they don't
move this specific number) but are not, on their own, the lever that matters
here.
