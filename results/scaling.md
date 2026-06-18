# Transfer-matrix scaling & reach projection (PRELIMINARY — task #19)

Goal: turn "as many terms as we can reasonably do" into per-term memory numbers,
so we know which terms fit gympie (24 GB, now), which wait for ayr (78 GB,
~2026-06-27), and which need the out-of-core backend.

Status: **preliminary.** Low/mid heights measured directly; tall heights are the
open question and are *not* safely extrapolatable (see the deceleration note).

## Measured: a(20) forward sweep, peak boundary-state count by height

From the gympie partial run (`build/tma square8 20 --only-height H`), peak number
of distinct boundary signatures held at once:

| H | peak_states | ratio | | H | peak_states | ratio |
|---:|---:|---:|---|---:|---:|---:|
| 1 | 1 | — | | 8 | 1604 | 2.57 |
| 2 | 5 | 5.00 | | 9 | 4176 | 2.60 |
| 3 | 15 | 3.00 | | 10 | 10992 | 2.63 |
| 4 | 39 | 2.60 | | 11 | 29192 | 2.66 |
| 5 | 98 | 2.51 | | 12 | 77752 | 2.66 |
| 6 | 246 | 2.51 | | 13 | 204843 | 2.63 |
| 7 | 624 | 2.54 | | … | (running) | |

Low/mid growth is ~**2.6×/height**.

## The deceleration (why we must NOT extrapolate 2.6× to the top)

The a(19) production run on ayr peaked at these RSS values for its tallest heights:

| height | RSS | ratio vs previous |
|---:|---:|---:|
| H17 | 4.0 GB | — |
| H18 | 8.0 GB | 2.0× |
| H19 | 12.5 GB | 1.56× |

So as H→n the per-height cost **tapers** (2.0×, then 1.56×), well below the 2.6×
seen low down. A constant-ratio extrapolation overestimates the tall heights —
the exact error mode to avoid. The real tall-height numbers must be *measured*,
which for a(20) needs >24 GB → ayr (June 27) or out-of-core.

## Important: at these sizes the gympie limit is TIME, not memory

Measured on the a(20) partial: height 14 ran **>68 min** while holding only
~450 MB (peak ≈ 0.5 M states). So the mid heights are cheap on RAM but expensive
in time, and the per-height *time* grows steeply (H1–13 finished in ~35 min
total; H14 alone exceeded that). Implication: gympie's reach for a(20) is gated by
**wall-clock**, not the 24 GB — the memory cliff is further out than the time
cliff. This reinforces that extending a(20)+ wants ayr's cores (June 27) or
engine optimization, not just more RAM. (The memory model below still governs the
tall heights, which is where RAM eventually binds.)

## Memory model

Per state ≈ Sig (32 B) + counts row ((maxn+1)·8 B) ≈ 200 B at n=20; the sweep
holds two maps (db + next) at load factor ≤0.7, so effective ≈ **~570 B/state**.
(Anchor check: a(19) H19 at 12.5 GB ⇒ ≈ 22 M states, consistent.)

Implied capacity: gympie 24 GB ≈ **42 M states**; ayr 78 GB ≈ **137 M states**.

## Provisional reach (to be replaced by measured tall-height numbers)

- **gympie (now):** comfortably does a(20) up to ~H16–17; H18 is borderline, H19–H20
  exceed 24 GB. So the gympie partial (currently capped at H15) can likely be
  pushed to ~H17 safely. Heights 18–20 are the gap.
- **ayr (June 27):** completing a(20) depends on whether its tallest height (H20)
  fits 78 GB. With deceleration it plausibly does; a 2.6× extrapolation says it
  doesn't — genuinely unresolved until measured. **a(20) is therefore NOT a sure
  "just wait for ayr"** (revises the earlier assumption); it may need out-of-core.
- **out-of-core (#20):** required for whatever exceeds 78 GB — possibly a(20)'s top
  height, more likely the a(21)+ frontier.

## Update — a(20) heights 1–15 measured (gympie)

peak_states (continuing the table): H14 = 524,653; H15 = 1,287,218. Ratios
H13→H14→H15 = 2.56, 2.45 — still ~2.5× and *very slightly* decelerating, as
expected. Memory per height (≈570 B/state): H15 ≈ 0.7 GB, H16 ≈ 1.8 GB,
H17 ≈ 4.5 GB, H18 ≈ 14 GB — so after freeing Chrome (~20 GB available) the tall
heights through ~H18 **fit gympie's RAM**. The binding constraint here is
**time**, not memory: the loop took ~4 h for H1–15, and per-height time grows
~2.5×, so H16 ≈ hours, H17 ≈ ~½ day, H18 ≈ a day+.

Partial a(20): Σ_{H=1}^{15} byHeight[H][20] = **1,021,174,452,560,693**. The
byHeight distribution peaks at H9 (1.83×10¹⁴) and tails ~0.4–0.5× per height past
the peak, so the missing H16–20 add ≈6–7×10¹² → full **a(20) ≈ 1.028×10¹⁵**
(estimate, to be confirmed by completing the tall heights).

## Revised reach conclusion
- **gympie:** can bank a(20) through ~H17–18 given enough *wall-clock* (heights
  16–18 launched; memory is fine post-Chrome). H19–H20 are time-prohibitive here.
- **ayr (June 27):** completes a(20) comfortably (its tallest height ≈ tens of
  GB ≪ 78 GB) and is the natural host for a(21).
- **out-of-core (#20):** now looks like the **a(22)+** frontier, not a(20) — the
  earlier worry that a(20) itself might exceed 78 GB is not borne out by the
  measured, decelerating state growth.

## Still to fill in
- a(20) H16–H18 (gympie, running) and H19–H20 (ayr) → confirm full a(20).
- One clean tall-height anchor to lock the memory model at large H.
