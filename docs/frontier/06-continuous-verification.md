---
# Frontier idea 06 — Verification as a continuous parallel pipeline
*Source: docs/scheduling-design.md §"Unexplored axes" #6. Related: docs/scheduling-design.md §"Open empirical questions" #3 (cost model — supplies the "where on the curve are we" axis), tests/gate_tma.py (the end-of-run A–L byte-identical gate this would FRONT-RUN), cpp/tma/sweep8_modp.h + tma_main.cpp `--modp` (the shadow engine), docs/frontier/oq3-cost-model-calibration.md.*

## Idea
A days-long pole sweep is validated only at the END (gate_tma.py: byte-identical A–L). A single corrupted state discovered then wastes the whole run. Instead, run cheap independent invariants AS COLUMNS LAND — a mod-second-prime running total, the partial triangle row-sum Sum_H B_H(n), GF columns for H≤9 — turning the multi-day end-gate into an early tripwire. Attacks the **wasted-rerun risk**, not RAM or wall.

## Why it might matter here
The pole sweep for a(21) runs **days** (a22-forecast: ~2 days/pole, ~5–6 d for 3 primes). A corruption found at the gate costs that entire wall. If a continuous invariant fires at, say, column c of ~N columns, it saves the remaining (N−c)/N of the run — for a mid-run hit, ~half the wall. The lever is only worth building if (a) the cheap invariant actually catches a single-state corruption and (b) it costs <~10% so it's a monitor, not a re-run.

## Smoke test (dead-on-arrival)
Confirm the `--modp` shadow exposes a running total readable mid-sweep at all — it does:
it's the accumulating count carried through the validated transition. So a per-column
observable to cross-check against **exists by construction**; dead-on-arrival only if
there were no mid-sweep observable. (There is — proceed to the power half of the kill-test,
which is the real risk.) One look at the shadow engine, no run.

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** does a continuously-runnable invariant exist that is BOTH discriminating (catches a single-state count error, not just an OOM/crash) AND cheap (<~10–15% overhead)? Test the cheaper requirement's *power* first — power is the thing that can fail silently.
**Setup:** two free, no-build measurements on gympie at a small height (e.g. `tma square8 14 --only-height 13`):
  - **Power (do first):** the engine already exposes `--modp P` (tma_main.cpp L245) carrying the *validated* transition. Run the exact sweep AND a mod-p shadow at a fresh prime; perturb ONE state's count by +1 mid-run (the same hook style as `TMA_CKPT_KILL_AT_COL`, checkpoint.h L206) and check whether the shadow's running total diverges. Reason out the triangle row-sum's power on paper: Sum_H B_H(n)==a(n) catches any per-HEIGHT error but is blind to errors that cancel within a height.
  - **Cost:** time the exact sweep, then exact + the live shadow total; take the delta as a % of the exact wall.
**Measure:** (1) does the mod-p shadow flag the single +1 perturbation (any error not ≡0 mod p ⇒ caught, p>maxn count step ⇒ all realistic single-state errors caught); (2) shadow overhead as % of sweep wall.
**NO-GO if:** the only <~10%-cost invariant is the triangle row-sum AND it provably misses within-height single-state corruption (weak power), OR the mod-p shadow that DOES catch it costs >~10–15% on top of the sweep — then it's a second enumeration (a re-run), not a monitor, and the cost is the same epic it was meant to de-risk.

## Substantial-improvement ladder (must clear ALL)
- **C1 — catches a realistic single-state corruption** — the injected +1 perturbation is detected by the running invariant before the sweep ends (mod-p shadow: caught iff error ≢0 mod p, which a single 64-bit prime makes overwhelmingly certain).
- **C2 — overhead <~10% of sweep wall** — measured exact-vs-exact+shadow delta at the test height; extrapolate by the same 2.4×/height law to the pole (shadow and exact share enumeration shape, so the % is roughly height-invariant).
- **C3 — fires ≥ days before the end-gate** — quantify the trip column: a mod-p running total checkpointed every K columns fires within K columns of the corruption; at the pole (~days) that is hours-to-a-day of saved wall, vs the full run lost at the gate.
*Per-idea bar:* turns a multi-day end-of-run byte-gate into an early tripwire at <~10% cost — i.e. converts "rerun the whole sweep" into "lose at most the columns since the last invariant check."

## Composition / foreclosures
- **Shares with oq3 (cost model):** the cost model says WHERE on the column curve we are, which converts a fired tripwire into "X days saved" — pairs directly.
- **Reuses, doesn't rebuild:** the `--modp` shadow engine (sweep8_modp.h), the GF-H≤9 oracle (results/fixed_height_gf.md), the triangle identity (#31). No new enumeration architecture.
- **Orthogonal** to compression (01), out-of-core (02), sort-engine (03), M4/M5 — it observes any engine's column stream; it does not change the engine.
- **Ordering:** do the power half of the kill-test before ANY shadow plumbing — a weak-power invariant is dead on arrival regardless of cost.

## If it passes: effort & where it lands
**S–M (ESTIMATE)** — the shadow engine and the GF/triangle oracles already exist; the work is a thin live comparator (running mod-p total + row-sum partials checked at each checkpoint cadence, checkpoint.h `ckptDue`) and a "tripwire fired" abort/alert. Lands as a verification mode in the driver alongside the sweep, reporting via the heartbeat. ROADMAP: a de-risking adjunct to #21/#32 pole runs (not a new term). Engine: tma_main.cpp driver, cpp/tma/sweep8_modp.h, tests/gate_tma.py (the gate it front-runs). **Effort is a t-shirt size, not a wall-clock — no ETA fabricated.**
---
