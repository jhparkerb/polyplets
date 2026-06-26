# Future-directions program — the holistic plan

The level above the 12 per-idea playbooks (`README.md`). It says what the whole push is
*for*, why it's really **one bet plus a supporting cast**, and the sequence — gated, with
the cheap-and-perishable first — that gets us past the wall without wasted effort.
Decision record this derives from: `../scheduling-design.md`.

## 1. The goal and the wall
Extend A006770 (fixed king-polyplets) as far as is honestly reachable. The binding
constraint is **RAM at the pole** (height H=N−1); pole RAM grows **2.41×/N**. From the lean
~580 B/state law:

| term | pole states | lean RAM | single box? |
|------|------------:|---------:|-------------|
| a(22) | 6.9×10⁷ | ~40 GB | fits (current engine) |
| a(23) | 1.7×10⁸ | ~96 GB | fits **only with oq1** (I7 1-copy table); batched → OOM |
| a(24) | 4.0×10⁸ | ~232 GB | **fits no box** — the cliff |

**The program is not "12 ideas." It is: cross the a(24) RAM cliff, ship a(22)/a(23)
cleanly on the way, and generate the by-products (triangle, holes, GFs) only as far as
they're worth.** Everything below hangs on that spine.

## 2. The shape of the bet — three tiers
- **Cliff-movers** — change *where* the wall is. Only **03 (sort/merge engine)** truly
  bends the access pattern; **02 (disk), 05 (cloud), M5 (distribute)** are its *backends*,
  not independent bets. **01 (compression)** is a partial cliff-mover: a 4× RAM cut buys
  ~1.57 terms (log4/log2.42), so it *shifts* the curve ~1 term — only **01-via-FLM** could
  *bend* it.
- **Term-enablers / constant factors** — **oq1 (I7)** is what makes a(23) RAM-resident at
  all; **04 (per-column config)** is a wall/RAM trim; **09 (u128)** is a counting-arithmetic
  swap for a(26)+. None move the cliff; they buy a term or simplify.
- **Process & scope** — **06 (continuous verification)** de-risks every multi-day run;
  **oq2 (portable checkpoint) / M4 / M5** are the only levers on cross-box pole imbalance;
  **oq3 (cost model)** drives scheduling + honest ETAs; **07 (GF notch)** is dormant (order
  explosion); **08 (over-computing)** is a scope decision.

If you remember one thing: **03 is the trunk; 01 and oq1 are the two big branches; the rest
is instrumentation and decisions.**

## 3. The staging spine (the ideas hang on the term ladder)
- **NOW — a(21) finishing (dalby).** Capture its perishable per-height/per-column telemetry
  (done: `results/oq3-04-data-collection.md` + `scripts/a21_telemetry.sh`). This is the only
  free calibration of oq3/04 we'll get until the standing telemetry lands.
- **a(22) — current engine** (~40 GB, fits). Two things to settle *before* launch: (c)
  **standing telemetry** (`standing-telemetry.md`) so a(22) self-instruments instead of
  being scavenged; and **08** — decide whether the triangle/holes/GF by-products are in
  scope for this term, since they're ~85% of per-state RAM and most of the extra compute.
- **a(23) — the TESTBED** (jasonp's call, scheduling-design §staging). It still *fits* (with
  oq1), so prove the a(24)-grade machinery here where failure is cheap: **oq1 (I7)** to make
  it resident, **03 (sort engine)** trialed in anger, **oq2 + M4/M5** if distribution is
  wanted, **01** sliding the row rightward. Do NOT squeeze the current engine over a
  hope-for-the-best a(24).
- **a(24)+ — the cliff.** **03's restructure is mandatory**; the backend (local disk · cloud
  KV · sharded) becomes a deployment choice; **01** compounds. No owned box fits, so this is
  where **05 (cloud)** finally clears its gate.

## 4. The enabling layer — build the cheap multiplier first
Two pieces of shared infra make every engine idea testable apples-to-apples and every
production run self-calibrating. They are cheap and they pay back across the whole program,
so they come **before** sinking effort into any single engine idea:
- **`harness-spec.md`** — a fixed off-frontier **smoke fixture** (`tma square8 14
  --only-height 12`, ~27 s, gate-checkable) + a **single-column micro-bench** with swappable
  hash/sort/concurrent/compressed/u128 backends, each byte-identical to the dense baseline.
  Turns "four bespoke prototypes with non-comparable numbers" into "a backend + a row in one
  table." Serves 03, oq1, 01, 09.
- **`standing-telemetry.md`** — default-on per-column CSV (state count, peak RSS, wall,
  throughput, mod-p checksum) baked into the engine, so a(22)+ produce the oq3/04/06 data for
  free and the perishability problem never recurs.

## 5. The program, sequenced (gate-ordered, cheap+perishable first)
1. **Now / perishable / minutes:** oq3+04 capture off a(21) (**done**); oq2 2-min cross-arch
   *load* smoke; 09 10-min `__uint128_t` compile+correctness on both ISAs; 01 `--profile-rows`.
2. **Infra (the multiplier):** the fixture + `bench_column` harness; standing telemetry —
   **land before a(22) launches.**
3. **The trunk:** 03 whiteboard smoke (seam-closure as sort+merge w/o random lookup?) →
   in-RAM sort-vs-hash micro-bench → the break-even kill-test. **Gates 02/05/M5** — don't
   touch them until 03's number is in.
4. **a(23) enabler:** oq1 I7 contention on one heavy a(21)/a(22) pole column (the highest-
   stakes measurement — it decides whether a(23) is single-box).
5. **Decisions, not experiments:** 08 (scope trim — jasonp); 07 (leave H≥10 dormant); 05
   (deferred to a(24)+).
6. **Continuous:** 06 mod-p shadow on every multi-day pole; oq3 calibrated against a(21)→a(22)
   so the queue has real priorities and ETAs are derived, never guessed.

Hard gates (full DAG in `README.md`): **03 → 02/05/M5**; **oq2-load → oq2-byte → M4/M5**;
**oq1 → a(23) engine choice**; **01-FLM → compression verdict**.

## 6. What success looks like — and what re-plans it
- **Success:** a(24) becomes reachable (03 lands), a(22)/a(23) ship on self-calibrating
  telemetry, and the by-product scope is a deliberate choice, not drift.
- **Re-plan triggers:**
  - **03 smoke fails** (no sort+merge seam-closure) → fall back to compression-only; the
    cliff stays ~a(23) and a(24)+ needs a different idea. *This is the pivotal unknown — test it early.*
  - **oq1 contention high** → a(23) can't go single-box; distribution (M5/oq2) moves up.
  - **01-FLM bends the curve** → compression dominates and reorders everything (scheduling-
    design §reuse already flags FLM as the one scaling-changer).
  - **08 says trim** → drop the triangle/holes from the frontier path, which also shrinks
    per-state RAM (~85% is the all-n counts row) and amplifies 01's ranged-row win at the pole.

## Pointers
- Per-idea playbooks + verdict table + gate DAG + do-first order → `README.md`
- Infra specs → `harness-spec.md`, `standing-telemetry.md`
- Live data capture → `../../results/oq3-04-data-collection.md`, `../../scripts/a21_telemetry.sh`
- Source decision record + staging rationale → `../scheduling-design.md`
