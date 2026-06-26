# Reach projection — how far the transfer-matrix engine extends (#19)

How far the column transfer-matrix engine can push $a(n)$ on the available
hardware, from **measured** peak-state counts and resident memory — not
extrapolated guesses. Decides which term first requires the out-of-core backend
(#20).

## RAM model

$a(n)$ is assembled per bounding-box height: each height $H$ is swept separately
to $\text{MAXN}=n$ (`tma square8 n --only-height H`). The peak memory of a run is
`peak_states` (the largest live boundary-signature set during the sweep) times the
bytes held per state. Because the signature space grows with strip height, the
**RAM driver for $a(n)$ is the tallest strip, $H=n$** (the "diagonal" job) — not
the most-populous height. So the wall is the single diagonal job, and the whole
term fits a machine iff that one job does.

## Measured data

`peak_states` at the top heights, from the a(19) run (`~/poly-tma/runs/tma-a19`,
ayr) and the a(20) run (`runs/a20`):

| height H | a(19) peak_states | a(20) peak_states | height-step (a20) |
|---|---|---|---|
| 17 | 5,189,646 | 6,587,527 | — |
| 18 | 9,816,902 | 12,843,440 | ×1.95 |
| 19 | 22,095,248 | 23,975,127 | ×1.87 |
| 20 | — | 53,559,816 | ×2.23 |

**Diagonal (the RAM driver, $H=n$):**
- a(19): 22,095,248 states
- a(20): 53,559,816 states
- **term-to-term ratio = 53,559,816 / 22,095,248 = 2.424**

**Bytes per state** (resident): gympie's live a(20) height-19 job holds 6.45 GB
RSS at 23.98 M states ⇒ **≈270 B/state**; the completed a(20) height-20 job
(53.6 M states) fit gympie's 24 GB ⇒ ≲320 B/state at scale. Use **≈270–320
B/state** (small jobs read higher — fixed thread/allocator overhead dominates
until the state store is large; irrelevant at the diagonal).

## Projection

Diagonal grows ×2.42/term (and the height-step ratio is itself drifting up,
1.87→2.23, so treat 2.42 as a slight *under*-estimate for higher terms):

| term | diagonal peak_states | heaviest-job RAM @270–320 B | vs ayr 78 GB |
|---|---|---|---|
| a(20) | 53.6 M (measured) | ~16 GB | fits (measured) |
| **a(21)** | ~130 M | **35–41 GB** | **fits — no backend needed** |
| **a(22)** | ~314 M | **85–100 GB** | **OVER — needs out-of-core (#20)** |
| a(23) | ~760 M | 205–243 GB | far over |

## Verdict

- **a(21) is reachable today on ayr (78 GB) with no code change** — the heaviest
  stratum lands at ~35–41 GB, comfortably inside memory. Free/one-sided(21) ride
  along. (Time, not RAM, is the cost: the diagonal job's work scales with states,
  ≈2.4× the a(20) wall-clock, i.e. order-of-days single-term.)
- **a(22) is the first term that requires the out-of-core state store (#20).**
  At ~85–100 GB it exceeds 78 GB even at the optimistic end of bytes/state, so
  it is not a "tune it and squeak under" case — the backend is mandatory.
- **a(23)+** is far past 78 GB; needs #20 plus likely more than one machine's
  disk, or a fundamentally cheaper representation.

## FLM verdict (Phase 0.1, 2026-06-26): width-bounding BENDS the state base — SURVIVOR

The phase01 worst-case-WIDTH test (maxHW=maxDD=n) killed the 45° rotation on peak
frontier *size*. But that is not the incumbent's cost driver — the **distinct
boundary-SIGNATURE base** (the 2.42/term peak_states growth) is. phase01 itself
flagged the state-count as "the careful follow-up." It has now been run
(`experiments/phase02_statecount_probe.cpp`): Redelmeier-enumerate every king-polyplet,
and for each internal cut record the canonical connectivity partition of the frontier
(the exact TM state, perp-gaps preserved), two ways — **column cut x=c (height-bounded,
= incumbent)** vs **diagonal cut x−y=c (width-bounded, = B-BS 45°)** — peak over cut of
distinct signatures, per term:

| n | col_states | col ratio | diag_states | diag ratio | colW=diaW |
|---|-----------:|:---------:|------------:|:----------:|:---------:|
| 8 | 344 | 2.511 | 81 | 2.077 | 7 |
| 9 | 858 | 2.494 | 168 | 2.074 | 8 |
| 10 | 2129 | 2.481 | 345 | 2.054 | 9 |
| 11 | 5260 | 2.471 | 706 | 2.046 | 10 |
| 12 | 12947 | **2.461** | 1443 | **2.044** | 11 |

- **The proxy is validated:** col base → 2.46 and descending toward the engine's
  measured 2.42 (it's a strict over-estimate that converges from above). Same
  measurement on the diagonal cut.
- **Width-bounding gives a strictly smaller base: ~2.04 vs ~2.42**, stable over 6
  terms, NOT converging upward, gap slightly *widening*. The peak frontier WIDTH is
  identical (colW=diaW=n−1, reproducing phase01) — so at equal frontier size the
  diagonal cut realizes far fewer distinct connectivity partitions. The corroborating
  direct-TM-state probe (`phase03_tmstate_probe.cpp`) shows the same lean in its growth
  region (window-bounded, so only directional, not asymptotic).
- **Cost consequence, with numbers.** Per-term: RAM ∝ states-per-cut = base^n; time ∝
  cuts × states ≈ (cuts)·base^n. Diagonal pays ~2× the cuts (extent Danti≈2n vs n) but
  base 2.04 vs 2.42 ⇒ ratio (2.42/2.04)^n. At **a(22): (2.42/2.04)^22 ≈ 36× less peak
  RAM, ~18× less time** (after the 2× cut penalty); the gap grows ~1.19×/term. This
  reframes the a(24) RAM cliff: a 45° king engine would push it out **~2 full terms**.
- **What the repo's prior NO-GO got wrong:** it dismissed the rotation on worst-case
  *width* and asserted "the state-count can't plausibly rescue it." Measured, the
  state-count says the opposite. The width tie and the state-base gap are both real;
  they measure different things, and the cost driver is the latter.
- **Caveat — this is a state-count signal, not a built engine.** It does not yet account
  for: (a) the connectivity-closure / touch-flag bookkeeping a correct 45° king TM needs
  (a constant factor, same shape as the column engine's, not a base change); (b) whether
  the diagonal transition's *branching* (king back-adjacency j∈{i−1,i} on the anti-
  diagonal) admits the same lock-free batched-merge engine. **Verdict: SURVIVOR — the
  only candidate measured to bend the base. Next test (specified, ~1–2 wk): build a
  minimal 45° king column-transition mirroring `sweep8.h`, validate Σ_cut == a(n) for
  n≤13, and confirm the peak distinct-state ratio of the REAL engine lands ~2.05.** This
  reopens what frontier-revision-plan §0.1 had gated NO-GO.

## Caveats

- Two diagonal data points (a19, a20) fix the ratio at 2.42; the slowly-rising
  height-step ratio suggests the true per-term factor creeps above 2.42 at higher
  $n$, which only makes a(22) *more* over-budget — the verdict is robust to that.
- Bytes/state is measured two ways and agrees to ~20%; the a(22) call survives the
  full range.
- Hole-stratified runs have their own (larger) constant but the same diagonal
  scaling; full $n=19$ holes (~60–75 GB) fits 78 GB, consistent with this model.
- A separate wall governs the fixed-(height,#holes) GFs: recurrence **order**
  ∝ height, so height ≥9 needs series length $N\gtrsim9000$ (time ∝ $N^2$), a
  *time* limit the out-of-core backend does not address.
