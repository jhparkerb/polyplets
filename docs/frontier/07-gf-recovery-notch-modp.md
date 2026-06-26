# Frontier idea 07 — GF-recovery for the mid-heavy notch columns via mod-p
*Source: docs/scheduling-design.md §"Unexplored axes" #7. Related: results/fixed_height_gf.md (the order law + recovery cost), ROADMAP.md #26, gf/modp_recover.py, docs/frontier/01-state-compression.md (u32 mod-p rows it would reuse).*

## Idea
For a fixed bounding-box height H, recover the rational generating function
G_H(x) = P_H(x)/Q_H(x) by mod-p column sweeps + Berlekamp-Massey + CRT, then series-expand
it to fill the ENTIRE height-column B_H(n) for **all n at once** — instead of one
per-cell sweep per (H,n). This is the concrete bridge to the by-height triangle work
(ROADMAP §"WHAT'S IN HAND": H=1..9 columns already come for free this way). It attacks
**WORK VOLUME** by doing a height once for all n. The wall is not RAM — it's the
**recurrence order**, which sets how many terms (hence how far each sweep must reach).

## Why it might matter here
A recovered GF is the maximal form of cross-n reuse: one rational function → every
B_H(n). For small H it is pure profit and **already banked** (H≤9 recovered + validated,
results/fixed_height_gf.md; H=10 order/structure confirmed mod-p). The question is whether
it pays for the **mid-heavy notch** heights (H≈10..19) that the running a(21) sweeps cell
by cell. The lever is real only where the order stays small enough that "2r terms × prime
count" sweeps cost less than sweeping the notch cells directly.

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** at notch height H, does recovering G_H cost LESS than directly
sweeping the ~handful of notch cells B_H(n) that the triangle actually needs?
**Setup:** back-of-envelope on the **recurrence order**, no build — all inputs measured.
The order law (results/fixed_height_gf.md, validated H=1..10):
  order: 1, 3, 7, 15, 42, 106, 278, 711, 1897, **5005** at H=1..10; growth ≈ **2.6×/H**.
**Measure / arithmetic:** recovering an order-r GF needs ≥ **2r terms** (BM is
underdetermined below ~2r — the doc's own debunked-conjecture cautionary tale), each term
a mod-p sweep reaching that n, **× the CRT prime count** for the coefficient magnitude.
  - terms needed: 2r. H=10: 2·5005 ≈ **10,010 terms** ⇒ sweeps must reach n≈10⁴.
  - extrapolate the order: H=11 ≈ 5005·2.6 ≈ 1.3×10⁴; H=15 ≈ 5005·2.6⁵ ≈ **6×10⁵**
    ⇒ 2r ≈ 1.2×10⁶ terms.
  - CRT prime count scales with coeff size: log10|coeff| ≈ 0.078·deg (results/…gf.md), so
    the pool ≈ deg/110 primes — H=10 needs ~57 primes (40 silently failed its ~1e390
    coeffs); H=15's deg-6×10⁵ coeffs are astronomically larger ⇒ **full bignum, hundreds
    of primes.** (u128 does NOT rescue this — only 63-bit CRT primes, half the pool; not a
    single prime. scheduling-design #9 tangential note.)
  - direct sweep cost: the triangle needs B_H(n) only for n up to the frontier N≈21–24 —
    a *handful* of cells per notch height, each a single sweep to n≤N. The a(21) run
    already does exactly this.
**NO-GO for H ≥ 10 if** recovery cost (2r sweeps to n≈order, × prime pool) > direct notch
sweeps (a few sweeps to n≤N). At H=10 that's ~10⁴ deep terms × ~57 primes vs ~3–4 cells
to n≤24 — recovery is **~10⁴–10⁵× more work.** The order explosion makes this near-certain
and it only worsens up-height. **Decisive:** the deliverable needs B_H(n) at n≤N, not the
closed form; paying for the whole rational function to read off a few low-n coefficients is
strictly wasteful once 2r ≫ N.

## Substantial-improvement ladder (must clear ALL)
- **C1 — order(H) keeps 2r ≲ N** at the target height — i.e. recovering the GF reaches no
  deeper in n than the direct sweep already must. Fails for all H≥10 (2r ≥ 10⁴ ≫ 24).
- **C2 — recovery wall ≤ direct-notch-sweep wall** for the cells the triangle needs —
  measured as (2r × prime-pool × per-term sweep) vs (notch-cell-count × per-cell sweep).
- **C3 — CRT prime pool stays bounded** (coeffs fit a fixed pool); fails by H≈10 (~57
  primes, growing ~deg/110).
*Per-idea bar:* "substantial" = fills an entire height-column for all n in **one shot**
cheaper than the cells cost directly. That holds ONLY where the order stays small.

## Composition / foreclosures
- **Boundary is concrete: H≤9 yes, H≥10 no.** H≤9 already recovered+validated (free,
  banked). The honest verdict for the heavy notch (H≈10..19) is **DORMANT** — revive only
  if the order law breaks downward (no evidence) or a sub-order recovery appears.
- **Would reuse** the u32 mod-p ranged rows from docs/frontier/01-state-compression.md
  (Phase 2) and the existing `--modp` machinery (gf/modp_recover.py, sweep8_holes.h) — so
  if ever viable it's driver code, not a new engine.
- **Rules out nothing**; it's an alternative *filling order* for triangle columns, not an
  architecture. Mirrors scheduling-design §Reuse ("GF pays only for H≤9") — this file is
  the arithmetic behind that one-liner.

## If it passes: effort & where it lands
**For H≤9: ZERO (ESTIMATE) — already done**, columns in hand. **For H≥10: does not pass**
the kill-test; effort is moot (DORMANT, do not build). If the order law were ever found to
plateau, recovery would be **S** driver work atop the existing mod-p engine — but absent
that, the notch is filled by direct sweeps (the a(21) run). **No ETA fabricated; the
verdict rests on the validated order sequence, not a projection.**
