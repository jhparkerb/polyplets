---
# Frontier idea oq3 — Cost-model calibration
*Source: docs/scheduling-design.md §"Open empirical questions" #3 (and §Survivors: "Cost model — the foundation for the queue's priorities and for honest ETAs"). Related: docs/a22-forecast.md (the current hand-fitted forecast this would systematize), ROADMAP.md #19 reach.md (2.42×/term, ~270–320 B/state — the empirical laws), docs/frontier/06-continuous-verification.md (consumes "where on the curve are we"), MEMORY: no-fabricated-progress-or-etas / surface-job-etas.*

## Idea
A closed-form model predicting **cost(H,N)** (wall) and **RAM(H,N,config)** (peak) from the measured laws — 2.4×/height, 4.3×/N, ~580 B/state lean (scheduling-design §"Strategic staging"), 2.42×/term pole (reach.md). It lets the work-unit queue prioritize correctly and replaces guessed ETAs with derived ones (the project's hard rule: ETAs are MEASURED/derived, never fabricated). Attacks **scheduling blindness and fabricated ETAs**.

## Why it might matter here
The cliff decisions are RAM-driven and made BEFORE launch: a(22) ~40 GB (current engine), a(23) ~96 GB (fits dalby ONLY with the lean I7), a(24) ~232 GB (no single box) — scheduling-design's own table. Pick the wrong box/engine and you OOM-kill days in (as happened 2026-06-25). The model is what turns "probably fits dalby" into a pre-launch number, and what makes the heartbeat's `eta=` a derived quantity instead of a guess. a22-forecast already does this BY HAND ("~5–6 days, range 4–7"); the question is whether a closed form is accurate enough to trust as machinery.

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** after fitting to the early/light a(21) heights, does the model predict each remaining a(21) height's wall AND peak RAM within ±30%?
**Setup:** NEARLY FREE — uses the RUNNING a(21) job, no new compute. Before each height lands, record the model's predicted wall + predicted peak RAM (closed form from H, N=21, config: the per-height 2.4× wall law, the ~580 B/state × predicted-states RAM law). As heights complete, log actual wall (heartbeat) and actual peak RSS (`/usr/bin/time -l` / ram_guard.sh sampling). Fit the constants on the first few completed heights; predict the rest forward.
**Measure:** per-height |predicted − actual| / actual for BOTH wall and peak RAM, across the a(21) heights as they land.
**NO-GO (untrustworthy) if:** error exceeds ~±30–50% on wall OR peak RAM after fitting to the early heights — then it can't drive box/engine selection (a 50% RAM miss is the difference between "fits dalby" and OOM) and it stays a rough heuristic (keep hand-forecasting per a22-forecast), not scheduling machinery.

## Substantial-improvement ladder (must clear ALL)
- **C1 — within ±30% on wall AND peak RAM across the a(21) heights** — measured per-height residual after fitting to the early/light heights; ±30% is the band that still lets you pick a box with margin.
- **C2 — predicts the a(22)/a(23) POLE RAM well enough to choose box+engine before launch** — the model, fit on a(21), forecasts the a(22) pole (~40 GB) and a(23) pole (~96 GB, lean) within the band that distinguishes "fits ayr 78 GB" / "fits dalby 122 GB only with I7" / "needs out-of-core." The cliff decisions (scheduling-design §"Strategic staging") depend on exactly this call.
- **C3 — cheap to evaluate: closed form from (H, N, config), not a simulation** — a few arithmetic ops per work unit, so the queue can score every candidate height instantly and the heartbeat can emit a derived `eta=` continuously.
*Per-idea bar:* accurate enough (±30%) to drive box/engine selection AND to replace guessed ETAs with derived ones. Below that band it's a heuristic; at/above it, it's the queue's priority function and the source of every honest ETA.

## Composition / foreclosures
- **Foundation, not a peer** — it is a SURVIVOR (scheduling-design §Survivors): the work-unit queue's priority order and every derived ETA are downstream of it. It composes with everything; it competes with nothing.
- **Feeds #32** (meet-in-the-middle scheduling) — the self-balancing split is robust without it, but the model sharpens the static-split fallback and the per-box height assignment.
- **Feeds 06 (continuous verification)** — converts a fired tripwire's column index into "days saved," because the model knows the remaining cost on the curve.
- **Re-fit, don't rebuild, after compression (01)** — compression slides the RAM law's constant (B/state) rightward; the model's *form* (2.4×/height, 2.42×/term) is unchanged, only the fitted constants move. M4/M5 don't change the per-height form either.
- **Ordering:** kill-test runs NOW against the live a(21) job — record predictions before each height lands; it costs no compute and the data is perishable (gone once a(21) finishes).

## If it passes: effort & where it lands
**S–M (ESTIMATE)** — the laws and constants already exist scattered across reach.md / a22-forecast / scheduling-design; the work is consolidating them into one closed-form `cost(H,N)` + `ram(H,N,config)` evaluator and wiring its output into the heartbeat `eta=` and (later) the queue's priority key. Kill-test itself is **S** — bookkeeping against the running job, no build. Lands as a small predictor module + a derived-ETA field in the heartbeat. ROADMAP: §Survivors "Cost model"; underpins the work-unit queue and #32. Engine: a new `cost_model.py` glue (Python is fine — it's thin scheduling glue, not compute) consumed by the drivers/heartbeat. **Effort is a t-shirt size, not a wall-clock — and the whole point is to STOP fabricating ETAs, so none is invented here.**
---
