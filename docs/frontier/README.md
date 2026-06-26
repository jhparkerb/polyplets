# Frontier ideas — kill-test + improvement playbooks

One file per still-open future direction from `docs/scheduling-design.md` (the
"Unexplored axes" #1–9 and the three "Open empirical questions"). Each file is the
same shape: the idea, **one cheapest-conclusive way to rule it INFEASIBLE**, and a
per-idea ladder of checks that it's a *substantial* improvement on its own. The
already-adjudicated ones (I4/M6 DROP, I5/I6 DEFER, B-BS 45° RETIRED) are not re-litigated
here — see scheduling-design.md.

**For the holistic view — what the whole push is for, the one-bet-plus-supporting-cast
framing, and the gate-ordered program across the a(22)→a(24) staging — read [PLAN.md](PLAN.md).**
This file is the per-idea index; PLAN.md is the strategy the ideas hang on. Shared test
infra: [harness-spec.md](harness-spec.md), [standing-telemetry.md](standing-telemetry.md).

Verdict-lean = where the evidence already points *before* running the kill-test; it is
NOT the answer, just which way to expect.

Each file now opens its checks with a **`## Smoke test`** (the minutes-cheap
dead-on-arrival check) above the fuller kill-test below — the "smoke" column flags it.

| # | idea | attacks | smoke (dead-on-arrival) | kill-test (cost) | lean |
|---|------|---------|-------------------------|------------------|------|
| [01](01-state-compression.md) | state compression + symmetry | RAM/state (~580 B) | `--profile-rows`: mean row width ≈ maxn ⇒ already dense (min) | FLM bend-vs-shift envelope + `--profile-rows` (free) | **BUILD, cap hopes** — constant-factor ~+1.3 terms unless FLM bends the curve |
| [02](02-out-of-core-spill.md) | out-of-core / disk spill | RAM cliff | target term fits box RAM? ⇒ disk moot (subtraction) | random-IOPS back-of-envelope (free) | **NO-GO raw** — collapses into 03; a backend, not a bet |
| [03](03-sort-transition-engine.md) | sort/merge transition engine | RAM + distribution | whiteboard: seam-closure as sort+merge w/o random lookup? (1h) | in-RAM sort-vs-hash prototype @ n=14–16 (S) | **GATE-1 PASS** (S≈1.0, compute-free; [seam-closure](03-seam-closure-analysis.md)) — C2 bandwidth test next decides it |
| [04](04-adaptive-per-column-config.md) | per-column (T,B,K) | wall + RAM headroom | h##.log: rate/src vary >2× across cols? (PASSES, free) | parse existing a(21) per-column logs (free) | **MARGINAL** but near-free test — gated at ~15% |
| [05](05-elastic-cloud-resources.md) | cloud burst / elastic | the cliff, with $ | roadmap target > a(23)? else dead (one look) | access-pattern gate + $ envelope (free) | **NO-GO until 03 lands AND a(24)+** |
| [06](06-continuous-verification.md) | continuous validation | wasted-rerun risk | `--modp` total readable mid-sweep? (yes, by construction) | mod-p shadow power + overhead @ small h (S) | **GO-lean** — de-risks the multi-day pole runs |
| [07](07-gf-recovery-notch-modp.md) | GF-recover notch via mod-p | fills a height-column | one division: 2·order(H) ≫ cells? dead H≥10 (≈kill-test) | recurrence-order arithmetic (free) | **DORMANT H≥10** (order 5005→6e5); H≤9 already banked |
| [08](08-meta-over-computing.md) | are we over-computing? | total work volume | b-file + draft claim cite only a(n)? ⇒ trim candidates (30m) | requirements audit of the submission (free) | **GO to trim, jasonp's call** — spine is load-bearing, rest is enrichment |
| [09](09-u128-counters.md) | u128 CRT-free counters | complexity/footguns | `__uint128_t` add compiles+correct on BOTH ISAs? (10-line) | extend `crt_counter_bench.cpp`, both ISAs (XS) | **SIMPLICITY-ONLY, DEFER to a(26)+** |
| [oq1](oq1-i7-hot-slot.md) | I7 shared lock-free table | RAM (makes a(23) fit) | 2-thread CAS map beats one mutex on a toy column? (min) | CAS-retry/contention on one heavy column (M) | **GO-lean, highest stakes** — but mutex history says measure |
| [oq2](oq2-m4-checkpoint-portability.md) | cross-arch checkpoint | sticky-pole imbalance | `tmaCkptLoad` returns Loaded (not Refuse) cross-arch? (2m) | dalby→ayr resume, byte-identical (S) | **UNCERTAIN, test-first** — gates M4 *and* M5 |
| [oq3](oq3-cost-model-calibration.md) | cost-model calibration | scheduling + honest ETAs | frozen H19 prediction lands within ±30%? (one residual) | predict a(21) heights, compare as they land (free) | **GO-lean, near-free** — but data is PERISHABLE |

## The one bet, restated
02, 05, and M5 are leaves that all reduce to **03**'s access-pattern restructure
(random find-or-insert → sequential/sort/batched). Once that lands, the storage backend
(local disk · cloud KV · network shards) is a swappable deployment choice. **03 is the
only one of the four with a real empirical kill-test** — do it, and 02/05/M5 fall out.

## Gate DAG (don't-start-X-until-Y)
Hard edges — do NOT start the blocked node until the blocker's number is in:
- **03 → 02, 05, M5** — all three are backends of 03's access-pattern restructure; don't
  build them until 03's sort-vs-hash number lands (03 blocks 02/05/M5).
- **oq2 smoke (loads cross-arch) → oq2 kill-test (byte-identical) → M4, M5** — a `Refuse`
  on load kills it cheap; only a byte-identical pass unblocks M4/M5 at their cheap estimate.
- **oq1 → a(23) engine choice** — oq1's contention result *gates* (informs, doesn't block)
  whether a(23) runs single-box via the I7 1-copy table or falls back to 01/02.
- **01 §0.1 FLM bend → compression verdict** — the FLM bend-vs-shift kill-test gates whether
  compression is a game-changer (BEND) or a banked ~+1.3-term constant factor (SHIFT).

## Do-first ordering (cheapest-and-decisive, perishable first)
Each item below leads with its **smoke** (the minutes-cheap dead-on-arrival check, in each
file's new `## Smoke test` section) before the fuller kill-test. Run the smoke first.
1. **oq3 cost-model + 04 per-column config + oq1 heavy-column contention** — all three feed
   on the *running* a(21). oq3 and 04 want predictions/logs recorded **before** heights
   land; once a(21) finishes the cheapest validation is gone. Record now, analyze after.
2. **03 sort-vs-hash prototype** — the load-bearing one-bet trunk; a small in-RAM
   prototype settles it and unlocks (or kills) 02/05/M5 together.
3. **oq2 checkpoint round-trip** — minutes-long dalby↔ayr test; a hard prerequisite that
   re-prices M4/M5 either way.
4. **06 mod-p shadow power+overhead** — cheap, de-risks every multi-day pole run that follows.
5. **01 FLM bend-or-shift** — decides whether compression is a game-changer or a banked
   ~1-term win (still worth shipping per frontier-revision-plan.md).
6. **Decisions, not experiments:** 08 (trim scope — jasonp's call), 09 (revisit at a(26)),
   07 (leave H≥10 dormant), 02/05 (downstream of 03).
