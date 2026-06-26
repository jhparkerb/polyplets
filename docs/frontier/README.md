# Frontier ideas — kill-test + improvement playbooks

One file per still-open future direction from `docs/scheduling-design.md` (the
"Unexplored axes" #1–9 and the three "Open empirical questions"). Each file is the
same shape: the idea, **one cheapest-conclusive way to rule it INFEASIBLE**, and a
per-idea ladder of checks that it's a *substantial* improvement on its own. The
already-adjudicated ones (I4/M6 DROP, I5/I6 DEFER, B-BS 45° RETIRED) are not re-litigated
here — see scheduling-design.md.

Verdict-lean = where the evidence already points *before* running the kill-test; it is
NOT the answer, just which way to expect.

| # | idea | attacks | kill-test (cost) | lean |
|---|------|---------|------------------|------|
| [01](01-state-compression.md) | state compression + symmetry | RAM/state (~580 B) | FLM bend-vs-shift envelope + `--profile-rows` (free) | **BUILD, cap hopes** — constant-factor ~+1.3 terms unless FLM bends the curve |
| [02](02-out-of-core-spill.md) | out-of-core / disk spill | RAM cliff | random-IOPS back-of-envelope (free) | **NO-GO raw** — collapses into 03; a backend, not a bet |
| [03](03-sort-transition-engine.md) | sort/merge transition engine | RAM + distribution | in-RAM sort-vs-hash prototype @ n=14–16 (S) | **THE one to test** — load-bearing; genuinely empirical |
| [04](04-adaptive-per-column-config.md) | per-column (T,B,K) | wall + RAM headroom | parse existing a(21) per-column logs (free) | **MARGINAL** but near-free test — gated at ~15% |
| [05](05-elastic-cloud-resources.md) | cloud burst / elastic | the cliff, with $ | access-pattern gate + $ envelope (free) | **NO-GO until 03 lands AND a(24)+** |
| [06](06-continuous-verification.md) | continuous validation | wasted-rerun risk | mod-p shadow power + overhead @ small h (S) | **GO-lean** — de-risks the multi-day pole runs |
| [07](07-gf-recovery-notch-modp.md) | GF-recover notch via mod-p | fills a height-column | recurrence-order arithmetic (free) | **DORMANT H≥10** (order 5005→6e5); H≤9 already banked |
| [08](08-meta-over-computing.md) | are we over-computing? | total work volume | requirements audit of the submission (free) | **GO to trim, jasonp's call** — spine is load-bearing, rest is enrichment |
| [09](09-u128-counters.md) | u128 CRT-free counters | complexity/footguns | extend `crt_counter_bench.cpp`, both ISAs (XS) | **SIMPLICITY-ONLY, DEFER to a(26)+** |
| [oq1](oq1-i7-hot-slot.md) | I7 shared lock-free table | RAM (makes a(23) fit) | CAS-retry/contention on one heavy column (M) | **GO-lean, highest stakes** — but mutex history says measure |
| [oq2](oq2-m4-checkpoint-portability.md) | cross-arch checkpoint | sticky-pole imbalance | dalby→ayr resume, byte-identical (S) | **UNCERTAIN, test-first** — gates M4 *and* M5 |
| [oq3](oq3-cost-model-calibration.md) | cost-model calibration | scheduling + honest ETAs | predict a(21) heights, compare as they land (free) | **GO-lean, near-free** — but data is PERISHABLE |

## The one bet, restated
02, 05, and M5 are leaves that all reduce to **03**'s access-pattern restructure
(random find-or-insert → sequential/sort/batched). Once that lands, the storage backend
(local disk · cloud KV · network shards) is a swappable deployment choice. **03 is the
only one of the four with a real empirical kill-test** — do it, and 02/05/M5 fall out.

## Do-first ordering (cheapest-and-decisive, perishable first)
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
