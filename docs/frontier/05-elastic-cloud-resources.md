# Frontier idea 05 — Elastic / opportunistic cloud resources
*Source: docs/scheduling-design.md §"Unexplored axes" #5. Related: docs/frontier/03-sort-transition-engine.md, docs/frontier/02-out-of-core-spill.md, scheduling-design §"One bet, not four", §"Strategic staging".*

## Idea
Burst a big-RAM cloud VM (or a cloud KV store: Redis/Bigtable) for the **pole**
column when no owned box can hold it, scaling availability-aware beyond our three
fixed boxes (gympie/ayr/dalby). Attacks the **RAM cliff** at a(24)+ (~232 GB, fits
no owned box) by renting capacity for the few heavy heights instead of buying it.

## Why it might matter here
We've assumed three fixed boxes; the cliff is a(24) (scheduling-design §"Strategic
staging"). A 256 GB+ cloud VM holds the a(24) pole that dalby (122 GB) cannot.
But cloud capacity is only *capacity* if the access pattern survives the network —
which is exactly the "one bet," so this idea is **gated on #3**, not independent.

## Kill-test — quickest path to INFEASIBLE (two prongs, fail-either)
**Question it answers:** does cloud add *capacity* (GO) or merely *latency* (dead),
and if capacity, is it cheaper than the owned box it replaces?

**Prong (a) — access-pattern gate (back-of-envelope, no spend).** If the engine
still does per-state random find-or-insert, a cloud KV / remote-RAM round-trip is
~10–100 µs vs ~100 ns local — a ~100–1000× per-op latency tax. At the a(24) pole
(4.0×10⁸ states × ~24 cols ≈ 9.6×10⁹ ops), even 10 µs/op serial = 9.6×10⁴ s ≈
**27 h of pure network stall**, on top of compute, per pole. **NO-GO (a):** the
engine still issues random ops (i.e. #3 has not landed) → cloud adds latency, not
capacity. This prong is **identical in shape to #2's IOPS wall** — random op over
network is as fatal as random op over disk (scheduling-design §"One bet, not
four"). So: **dead until docs/frontier/03-sort-transition-engine.md passes.**

**Prong (b) — dollar gate (back-of-envelope, ESTIMATE pricing).** a(24) pole needs
~232 GB; a ~256–384 GB cloud VM lists at roughly **$3–6/hr** on-demand (ESTIMATE,
order-of-magnitude — exact instance/region TBD, no fake precision). Multiply by an
order-of-magnitude pole-wall estimate: if the a(24) pole runs ~10²–10³ machine-hours
(ESTIMATE, anchored on the 2.41×/N pole law off a(22)'s hours-to-days, NOT a
committed ETA), that is ~$300–$6000 per attempt — plus re-runs for cross-ISA
validation. Compare to **dalby-time ≈ $0** (already owned) the moment an owned box
*can* hold the term. **NO-GO (b):** any owned box fits the term in RAM (a(23) and
below, with the lean I7 engine) → renting is pure waste.

**NO-GO if either prong fails.** Combined verdict: worth it **only** when
(a) #3 has landed AND (b) no owned box fits — i.e. **a(24)+ exclusively**.

## Substantial-improvement ladder (must clear ALL to be worth building)
- **C1 — #3 has landed** (sort/stream engine, contention-free, distributable) —
  precondition; without it prong-(a) kills this outright.
- **C2 — streamed remote backend within ~2× of local sorted-stream wall** —
  measured by pointing the #3 engine's spill at cloud object storage / a remote
  sorted-run store at the a(23) testbed scale.
- **C3 — $/term ≤ what the project will actually pay** for a term **no owned box
  can reach** — i.e. a(24)+ where the alternative is *not computing it at all*.
*Per-idea bar:* substantial = unlocks a term (a(24)+) that **no owned box can
reach by any means**, at a dollar cost the project agrees to spend. Anything an
owned box can do = automatic NO-GO (prong b).

## Composition / foreclosures
Strictly **downstream of #3** (shares the "one bet"; cannot precede it). It is the
**a(24)+-only** backend choice, parallel to #2's local-NVMe spill and M5's
sharded-owned-RAM — same restructured engine, different storage deployment. It
forecloses nothing; it is itself foreclosed until #3 passes AND owned boxes are
exhausted. Ordering: last of the three (#3 → then #2/M5 on owned hardware → cloud
only when owned RAM truly runs out).

## If it passes: effort & where it lands
**M (ESTIMATE)** *given #3 exists* — a remote/object-store backend behind the
sort/stream engine's spill interface, plus burst orchestration; the algorithm is
already done by #3. **Not worth any effort before a(24)** (prong b). Lands at
ROADMAP #20 as a deployment backend; engine = the sort/stream successor to
cpp/tma_main.cpp.
