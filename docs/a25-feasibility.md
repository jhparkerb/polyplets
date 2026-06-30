# a(25) feasibility first-cut (post-a(23), with k≤7 injection)

Answering "is a(25)-at-home feasible?" with real a(23) data and the k≤7 diagonal
injection now wired. **Tentative verdict: YES — the injection turns a(25) from a
~month-scale cloud job into a ~1–2 day home-cluster run.** Caveats below; this is a
first-cut, not a launch authorization.

## The lever: injection cuts compute ~15×, not just RAM

Measured a(23) per-height compute (core-hours): **H18=257, H17=113, H16=45,
H15≈16, H14≈5.5, H1–13≈5; total ≈ 441.** The cost is concentrated in the few tall
swept heights. k≤7 injection replaces the tall heights with closed forms (zero
sweep). Applied at a(23): it removes H16+H17+H18 = 415 of 441 core-h, leaving
**~26 core-h**. So injection is a ~15× *compute* reduction, not merely the RAM win.

## a(25) estimate

With k≤7 injected, a(25) injects H18–25 (the 8 tallest) and **sweeps only H1–17**;
the peak swept height is **H17**. Extrapolate each swept height's a(23) cost by the
per-term per-height compute growth g (g ≈ 1.8: total scales ~4.4×/term ÷ the ~2.4×
height-ladder ratio). Over 2 terms (g²≈3.24):

| Height | a(23) core-h | a(25) est (×g²) |
|---|---|---|
| H17 | 113 | 366 |
| H16 | 45 | 146 |
| H15 | 16 | 52 |
| H14–1 | ~11 | ~36 |
| **total swept** | | **≈ 600 core-h** |

Sensitivity: g∈[1.5, 2.4] → **~400–1000 core-h**. Either end is days, not weeks.

**Wall on the home cluster** (≈50% parallel efficiency):
- gympie+ayr (~40 cores, ~20 eff): 600/20 ≈ **30 h (~1.25 days)**
- + dalby (~120 cores, ~60 eff): ≈ **10 h**

## RAM / disk

Peak swept height is **H17**, whose a(23) frontier was **4.7 M states** (vs H18's
11.1 M). The frontier is ~weakly maxn-dependent (a(23) H16=1.9M sits right on the
height-ladder), so a(25) H17 ≈ low-tens-of-millions of states ≈ a few GB of frontier
— **spillable on any home box**; no 122 GB wall. Disk = spill volume, manageable.
This is why a(25)-at-home is RAM-feasible *only with* the injection: without it the
peak swept height is H20+ (≫ RAM).

## Caveats (why this is first-cut, not go)

1. **g is estimated**, not measured — I lack an a(21) cost profile to pin the
   per-term per-height growth. The table assumes g≈1.8.
2. **k≤7 at n=24,25 is EXTRAPOLATION.** The diagonals are validated through a(23)
   (swept H16/17/18); at a(25) the k≤7 cells (T(25,18..24)) are injected, not swept,
   so there's no in-run check — it rides on the polynomial form holding. Acceptable
   for an explicitly-unverified push; not for a certified record.
3. Efficiency assumed 50%; the merge/steal fixes could improve it, or a tall
   height could straggle worse.

## Bottom line

The k≤7 injection (wired, validated to a(23)) is the difference between "a(25) needs
cloud" and "a(25) is a 1–2 day home-cluster run." Static height-balancing across
gympie+ayr(+dalby) handles the parallelism; no cross-machine stealing needed (see
border-raid.md). Next refinement: an a(21) cost profile to pin g, and a decision on
whether the unverified-extrapolation risk (caveat 2) is acceptable for the push.
