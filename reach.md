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
